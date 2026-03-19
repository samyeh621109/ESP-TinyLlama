import math
import torch
import torch.nn as nn
import torch.nn.functional as F

from ternary_linear import TernaryLinear

# 嘗試載入官方 Cuda 加速的 Mamba (通常在 Linux GPU 機器上安裝了 mamba-ssm 才會有)
try:
    from mamba_ssm.ops.selective_scan_interface import selective_scan_fn
    HAS_MAMBA_CUDA = True
except ImportError:
    HAS_MAMBA_CUDA = False

class MambaBlock(nn.Module):
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2, dt_rank="auto"):
        """
        核心的 Mamba Block 實作，但將主要的線性投影轉換為 Ternary (BitNet b1.58) 型態。
        這能將 Mamba 的權重壓縮至原本 FP16 的 10~20% 大小，適合 MCU 部署。
        """
        super().__init__()
        self.d_inner = int(expand * d_model)
        self.d_state = d_state
        self.dt_rank = math.ceil(d_model / 16) if dt_rank == "auto" else dt_rank

        # 原本的 Mamba 是用 in_proj 把維度放大 2 倍
        # 我們將佔參數最多的 in_proj 替換為 TernaryLinear
        self.in_proj = TernaryLinear(d_model, self.d_inner * 2, bias=False)

        # 1D Convolution 保持原樣 (參數極少，且擷取局部特徵很有效)
        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            bias=True,
            kernel_size=d_conv,
            groups=self.d_inner,
            padding=d_conv - 1,
        )

        # 投影出 dt, B, C，這也是 O(D^2) 級別的參數，我們也替換成 Ternary
        self.x_proj = TernaryLinear(self.d_inner, self.dt_rank + self.d_state * 2, bias=False)
        
        # dt_proj (步長投影)，因為要參與指數計算，這裡保持 FP32 來確保訓練穩定度
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)

        # Mamba 的狀態轉換矩陣 A 與 D
        A = torch.arange(1, self.d_state + 1, dtype=torch.float32).repeat(self.d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.D = nn.Parameter(torch.ones(self.d_inner))

        # 最後輸出的 out_proj 同樣佔據大量參數，替換為 Ternary
        self.out_proj = TernaryLinear(self.d_inner, d_model, bias=False)

    def forward(self, x):
        (b, l, d) = x.shape
        # x_and_res: (b, l, 2 * d_inner)
        x_and_res = self.in_proj(x)  
        x_mamba, res = torch.split(x_and_res, [self.d_inner, self.d_inner], dim=-1)

        # Conv1D 需要 (b, c, l) 的維度
        x_mamba = x_mamba.transpose(1, 2)
        x_mamba = self.conv1d(x_mamba)[:, :, :l]
        x_mamba = x_mamba.transpose(1, 2)
        x_mamba = F.silu(x_mamba)

        # 進入 SSM 核心序列掃描
        y = self.ssm(x_mamba)
        
        # Gating 機制
        y = y * F.silu(res)
        
        # 最終 Ternary 投影回原本維度
        out = self.out_proj(y)
        return out

    def ssm(self, x):
        (b, l, d_in) = x.shape
        A = -torch.exp(self.A_log.float())  # (d_inner, d_state)
        D = self.D.float()

        x_dbl = self.x_proj(x)  # (b, l, dt_rank + 2*d_state)
        delta, B, C = torch.split(x_dbl, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        delta = F.softplus(self.dt_proj(delta))  # (b, l, d_inner)

        if HAS_MAMBA_CUDA and x.is_cuda:
            # 如果有 CUDA，使用官方的超高速 kernel
            y = selective_scan_fn(
                x.transpose(1, 2), # (b, d_inner, l)
                delta.transpose(1, 2),
                A,
                B.transpose(1, 2),
                C.transpose(1, 2),
                D,
                z=None,
                delta_bias=None,
                delta_softplus=False, # 已經在外層做過 softplus
                return_last_state=False
            )
            return y.transpose(1, 2)
        else:
            # Pytorch 迴圈 (Fallback，比較慢，但 PoC 與 CPU 開發可以用)
            y = torch.zeros(b, l, self.d_inner, device=x.device)
            h = torch.zeros(b, self.d_inner, self.d_state, device=x.device)
            
            # (1, 1, d_inner, d_state)
            A = A.unsqueeze(0).unsqueeze(0) 
            
            for i in range(l):
                # Discretization
                delta_i = delta[:, i, :].unsqueeze(-1) # (b, d_inner, 1)
                deltaA = torch.exp(delta_i * A) # (1, d_inner, d_state)
                deltaB = delta_i * B[:, i, :].unsqueeze(1) # (b, d_inner, d_state)
                x_i = x[:, i, :].unsqueeze(-1) # (b, d_inner, 1)
                
                # State Update
                h = deltaA.squeeze(1) * h + deltaB * x_i
                
                # Output
                C_i = C[:, i, :].unsqueeze(1) # (b, 1, d_state)
                y[:, i, :] = (h * C_i).sum(dim=-1) + D * x[:, i, :]

            return y

class TernaryMambaLMHeadModel(nn.Module):
    def __init__(self, vocab_size, d_model=384, n_layer=8):
        """
        組合完整的 Ternary-Mamba Language Model。
        預設 d_model=384, n_layer=8 (與之前 8M 的型號規模相當，方便互相比較 Coherence Threshold)
        """
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([MambaBlock(d_model=d_model) for _ in range(n_layer)])
        self.norm_f = nn.RMSNorm(d_model, elementwise_affine=False)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        
        # 綁定 Embedding 與 LM Head 的權重以節省參數
        self.lm_head.weight = self.embedding.weight

    def forward(self, input_ids):
        x = self.embedding(input_ids)
        for layer in self.layers:
            x = layer(x)
        x = self.norm_f(x)
        logits = self.lm_head(x)
        return logits

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        """
        簡單的自回歸生成邏輯。
        """
        for _ in range(max_new_tokens):
            # 如果輸入序列太長，截斷它
            idx_cond = idx if idx.size(1) <= 512 else idx[:, -512:]
            # forward 得到 logits
            logits = self(idx_cond)
            # 取最後一個 time step 的 logits 並套用 temperature
            logits = logits[:, -1, :] / temperature
            # 可選的 top-k 採樣
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
            # 套用 softmax 得到機率
            probs = F.softmax(logits, dim=-1)
            # 採樣下一個 token
            idx_next = torch.multinomial(probs, num_samples=1)
            # 拼接回輸入序列
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

def test_model():
    model = TernaryMambaLMHeadModel(vocab_size=10000, d_model=128, n_layer=2)
    x = torch.randint(0, 10000, (2, 64))
    out = model(x)
    print(f"[{'CUDA' if HAS_MAMBA_CUDA else 'PyTorch'} Mode] Model Output shape: {out.shape}")
    
    # 統計參數量
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total Parameters: {total_params:,}")

if __name__ == "__main__":
    test_model()

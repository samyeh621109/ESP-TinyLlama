import torch
import torch.nn as nn
import torch.nn.functional as F

class RoundWithSTE(torch.autograd.Function):
    """
    Straight-Through Estimator (STE) for rounding operation.
    Forward: returns rounded tensor.
    Backward: passes the gradient straight through, unchanged.
    """
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output

def bitnet_b1_58_quantization(weight, eps=1e-5):
    """
    Quantizes weights to {-1, 0, 1} based on the BitNet b1.58 paper.
    Formula: W_quant = Round(W / (Mean(|W|) + eps))
             W_quant = Clip(W_quant, -1, 1)
    """
    # 1. 取得絕對值平均作為 scale (gamma)
    gamma = weight.abs().mean().clamp(min=eps)
    
    # 2. 將權重除以 scale
    w_scaled = weight / gamma
    
    # 3. 透過 STE 四捨五入並限制在 [-1, 1] 之間
    w_quant = torch.clamp(RoundWithSTE.apply(w_scaled), min=-1.0, max=1.0)
    
    return w_quant, gamma

class TernaryLinear(nn.Linear):
    def __init__(self, in_features, out_features, bias=False, use_activation_quantization=False):
        """
        BitNet b1.58 的線性層實作。
        為了在 MCU 上極大化硬體效率，預設 bias=False (如同標準的 Mamba 或 GPT 架構)。
        """
        super().__init__(in_features, out_features, bias=bias)
        self.use_activation_quantization = use_activation_quantization
        
        # 使用 RMSNorm 對輸入進行正規化，這在 BitNet 架構中通常是必須的
        self.rmsnorm = nn.RMSNorm(in_features, elementwise_affine=False)

    def forward(self, x):
        # 1. 對輸入進行 RMSNorm (保持穩定性)
        x_norm = self.rmsnorm(x)

        # 2. 啟動值量化 (Activation Quantization) 到 8-bit [-128, 127]
        if self.use_activation_quantization:
            # 這是標準 BitNet 流程：x_quant = Round(x * (127 / max(|x|)))
            x_scale = 127.0 / x_norm.abs().max(dim=-1, keepdim=True)[0].clamp(min=1e-5)
            x_quant = torch.clamp(RoundWithSTE.apply(x_norm * x_scale), -128.0, 127.0)
            
            # 使用 Ternary Weight
            w_quant, w_gamma = bitnet_b1_58_quantization(self.weight)
            
            # 矩陣相乘：Int8(x) * Int2(w) -> 這裡在真實硬體上就是純加法！
            out = F.linear(x_quant, w_quant, self.bias)
            
            # 乘回原本的 Scale 以恢復數值範圍
            out = out / x_scale * w_gamma
        else:
            # PoC 初期，為了更容易收斂，我們只把 Weight 變成 Ternary，Activation 保持 FP32/BF16
            w_quant, w_gamma = bitnet_b1_58_quantization(self.weight)
            out = F.linear(x_norm, w_quant, self.bias)
            out = out * w_gamma

        return out

if __name__ == "__main__":
    # Test TernaryLinear
    torch.manual_seed(42)
    layer = TernaryLinear(in_features=128, out_features=256, bias=False, use_activation_quantization=False)
    x = torch.randn(2, 64, 128) # Batch=2, Seq=64, Dim=128
    
    out = layer(x)
    print("Input shape:", x.shape)
    print("Output shape:", out.shape)
    
    w_quant, gamma = bitnet_b1_58_quantization(layer.weight)
    print(f"\nOriginal weight min={layer.weight.min().item():.4f}, max={layer.weight.max().item():.4f}, mean={layer.weight.mean().item():.4f}")
    print(f"Quantized weight unique values (should be exactly -1, 0, 1): {torch.unique(w_quant).tolist()}")
    
    # 統計 -1, 0, 1 的比例
    total = w_quant.numel()
    print(f"Ratio of -1: {(w_quant == -1).sum().item() / total:.2%}")
    print(f"Ratio of  0: {(w_quant ==  0).sum().item() / total:.2%}")
    print(f"Ratio of  1: {(w_quant ==  1).sum().item() / total:.2%}")

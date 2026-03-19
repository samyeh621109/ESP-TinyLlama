import os
import time
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn.functional as F
import math

from ternary_mamba import TernaryMambaLMHeadModel

configs = {
    # Mamba 參數規模設計，對齊 GPT 的 1M, 3M, 8M, 15M
    "1M": {"d_model": 64,  "n_layer": 4},
    "3M": {"d_model": 128, "n_layer": 4},
    "8M": {"d_model": 192, "n_layer": 6},
    "15M": {"d_model": 256, "n_layer": 6},
}

def get_batch(data, batch_size, block_size, device):
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy((data[i+1:i+1+block_size]).astype(np.int64)) for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y

def train(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用設備: {device}")

    train_data = np.fromfile("training/data/train.bin", dtype=np.uint16)
    val_data = np.fromfile("training/data/validation.bin", dtype=np.uint16)

    conf_params = configs[args.config]
    
    # 建立 Ternary Mamba 模型
    model = TernaryMambaLMHeadModel(vocab_size=50257, **conf_params).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"初始化 {args.config} Ternary-Mamba，總參數量: {total_params:,}")

    # 優化器設定
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    ckpt_path = f"out/mamba_{args.config}/ckpt.pt"
    latest_ckpt_path = f"out/mamba_{args.config}/latest_ckpt.pt"
    
    start_iter = 0
    # 先嘗試讀取最近一次中斷的紀錄
    load_path = latest_ckpt_path if os.path.exists(latest_ckpt_path) else ckpt_path
    if os.path.exists(load_path):
        try:
            ckpt = torch.load(load_path, map_location=device, weights_only=False)
            model.load_state_dict(ckpt['model'])
            # 必須把 optimizer 狀態也讀回來，否則 Adam 的 momentums 歸零會導致訓練曲線震盪
            if 'optimizer' in ckpt:
                optimizer.load_state_dict(ckpt['optimizer'])
            start_iter = ckpt.get('iter', 0)
            print(f"✅ 成功從 {load_path} 繼續訓練！目前 iter = {start_iter}")
        except Exception as e:
            print(f"⚠️ 無法載入舊 ckpt ({e})，準備從頭開始訓練")

    os.makedirs(f"out/mamba_{args.config}", exist_ok=True)

    best_val_loss = float('inf')
    results_file = f"training/data/mamba_results_{args.config}.csv"
    accum_steps = 4
    block_size = 512

    if not os.path.exists(results_file):
        pd.DataFrame(columns=["config", "iter", "train_loss", "val_loss", "perplexity"]).to_csv(results_file, index=False)

    model.train()
    t0 = time.time()
    
    for iter in range(start_iter, args.max_iters):
        if iter % accum_steps == 0:
            optimizer.zero_grad(set_to_none=True)

        xb, yb = get_batch(train_data, args.batch_size, block_size, device)

        # 這裡不使用 autocast，因為量化的 STE 與 Mamba 內部狀態在低精度下可能會不穩定
        # PoC 階段先以 FP32 確保正常收斂
        logits = model(xb)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), yb.view(-1), ignore_index=-1)

        loss = loss / accum_steps
        loss.backward()

        if (iter + 1) % accum_steps == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        logged_loss = loss.item() * accum_steps

        if iter % args.log_interval == 0:
            t1 = time.time()
            dt = t1 - t0
            t0 = t1
            print(f"Iter {iter}: loss {logged_loss:.4f}, time {dt*1000/args.log_interval:.2f}ms")

        # 定期儲存最新進度 (不管 Loss 有沒有變好，至少保底)
        if iter > 0 and iter % 100 == 0:
            torch.save({
                'model': model.state_dict(), 
                'optimizer': optimizer.state_dict(),
                'iter': iter, 
            }, latest_ckpt_path)

        # 驗證循環
        if iter > 0 and iter % args.eval_interval == 0:
            model.eval()
            with torch.no_grad():
                val_loss = 0
                for _ in range(10):
                    vx, vy = get_batch(val_data, args.batch_size, block_size, device)
                    v_logits = model(vx)
                    l = F.cross_entropy(v_logits.view(-1, v_logits.size(-1)), vy.view(-1), ignore_index=-1)
                    val_loss += l.item()
                val_loss /= 10
            
            # 安全防護，避免 loss 爆炸導致 math domain error
            if val_loss < 20: 
                perplexity = math.exp(val_loss)
            else:
                perplexity = float('inf')
                
            print(f"Validation loss: {val_loss:.4f}, Perplexity: {perplexity:.2f}")

            new_report = pd.DataFrame([{"config": args.config, "iter": iter, "train_loss": logged_loss, "val_loss": val_loss, "perplexity": perplexity}])
            new_report.to_csv(results_file, mode='a', header=False, index=False)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save({
                    'model': model.state_dict(), 
                    'optimizer': optimizer.state_dict(),
                    'iter': iter, 
                    'val_loss': val_loss
                }, ckpt_path)
                print(f"儲存最佳模型至 {ckpt_path}")

            model.train()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="8M", choices=["1M", "3M", "8M", "15M"])
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--max_iters", type=int, default=25000)
    parser.add_argument("--lr", type=float, default=6e-4) # Mamba 通常需要比 Transformer 小一點點的 LR，這裡先沿用 6e-4
    parser.add_argument("--eval_interval", type=int, default=500)
    parser.add_argument("--log_interval", type=int, default=10)
    args = parser.parse_args()
    train(args)

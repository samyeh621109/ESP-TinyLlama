import os
import time
import argparse
import pandas as pd
import numpy as np
import torch
import math
from model import GPT, GPTConfig

# 參數配置
configs = {
    "1M":  {"n_layer": 2, "n_head": 4, "n_embd": 64},
    "3M":  {"n_layer": 4, "n_head": 4, "n_embd": 128},
    "8M":  {"n_layer": 6, "n_head": 6, "n_embd": 192},
    "15M": {"n_layer": 8, "n_head": 8, "n_embd": 256},
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
    
    # 載入數據
    train_data = np.fromfile("training/data/train.bin", dtype=np.uint16)
    val_data = np.fromfile("training/data/validation.bin", dtype=np.uint16)
    
    # 模型配置
    conf_params = configs[args.config]
    config = GPTConfig(
        vocab_size=50257, 
        block_size=512, 
        **conf_params
    )
    model = GPT(config).to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    
    os.makedirs(f"out/{args.config}", exist_ok=True)
    
    iter_num = 0
    best_val_loss = float('inf')
    results_file = "training/data/results.csv"
    
    # 初始化實驗記錄檔
    if not os.path.exists(results_file):
        df = pd.DataFrame(columns=["config", "iter", "train_loss", "val_loss", "perplexity"])
        df.to_csv(results_file, index=False)
    
    t0 = time.time()
    for iter in range(args.max_iters):
        # 訓練步
        xb, yb = get_batch(train_data, args.batch_size, config.block_size, device)
        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        
        # Log
        if iter % args.log_interval == 0:
            t1 = time.time()
            dt = t1 - t0
            t0 = t1
            print(f"Iter {iter}: loss {loss.item():.4f}, time {dt*1000/args.log_interval:.2f}ms")
            
        # 驗證 & 存檔
        if iter % args.eval_interval == 0:
            model.eval()
            with torch.no_grad():
                val_loss = 0
                for _ in range(10):
                    vx, vy = get_batch(val_data, args.batch_size, config.block_size, device)
                    _, l = model(vx, vy)
                    val_loss += l.item()
                val_loss /= 10
            perplexity = math.exp(val_loss)
            print(f"Validation loss: {val_loss:.4f}, Perplexity: {perplexity:.2f}")
            
            # 寫入實驗數據
            new_report = pd.DataFrame([{
                "config": args.config,
                "iter": iter,
                "train_loss": loss.item(),
                "val_loss": val_loss,
                "perplexity": perplexity
            }])
            new_report.to_csv(results_file, mode='a', header=False, index=False)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                checkpoint = {
                    'model': model.state_dict(),
                    'config': config,
                    'iter': iter,
                    'val_loss': val_loss,
                }
                torch.save(checkpoint, f"out/{args.config}/ckpt.pt")
                print(f"儲存最佳模型至 out/{args.config}/ckpt.pt")
            
            model.train()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="1M", choices=["1M", "3M", "8M", "15M"])
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--max_iters", type=int, default=50000)
    parser.add_argument("--lr", type=float, default=6e-4)
    parser.add_argument("--eval_interval", type=int, default=500)
    parser.add_argument("--log_interval", type=int, default=10)
    args = parser.parse_args()
    train(args)

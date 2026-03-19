import os
import time
import argparse
import pandas as pd
import numpy as np
import torch
import math
from torch.cuda.amp import autocast
from model import GPT, GPTConfig

configs = {
    "1M": {"n_layer": 2, "n_head": 4, "n_embd": 64},
    "3M": {"n_layer": 4, "n_head": 4, "n_embd": 128},
    "8M": {"n_layer": 6, "n_head": 6, "n_embd": 192},
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

    train_data = np.fromfile("training/data/train.bin", dtype=np.uint16)
    val_data = np.fromfile("training/data/validation.bin", dtype=np.uint16)

    conf_params = configs[args.config]
    config = GPTConfig(vocab_size=50257, block_size=512, **conf_params)
    model = GPT(config).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    # Resume training from checkpoint
    ckpt_path = f"out/{args.config}/ckpt.pt"
    start_iter = 0
    if os.path.exists(ckpt_path):
        try:
            ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
            model.load_state_dict(ckpt['model'])
            start_iter = ckpt.get('iter', ckpt.get('iter_num', 0))
            print(f"Successfully resumed from checkpoint at iteration {start_iter}")
        except Exception as e:
            print(f"Warning: Could not load checkpoint ({e}). Starting from scratch.")

    os.makedirs(f"out/{args.config}", exist_ok=True)

    best_val_loss = float('inf')
    results_file = "training/data/results.csv"
    accum_steps = 4

    if not os.path.exists(results_file):
        pd.DataFrame(columns=["config", "iter", "train_loss", "val_loss", "perplexity"]).to_csv(results_file, index=False)

    t0 = time.time()
    for iter in range(start_iter, args.max_iters):
        if iter % accum_steps == 0:
            optimizer.zero_grad(set_to_none=True)

        xb, yb = get_batch(train_data, args.batch_size, config.block_size, device)

        with torch.amp.autocast('cuda', dtype=torch.bfloat16):
            logits, loss = model(xb, yb)

        loss = loss / accum_steps
        loss.backward()

        if (iter + 1) % accum_steps == 0:
            optimizer.step()

        logged_loss = loss.item() * accum_steps

        if iter % args.log_interval == 0:
            t1 = time.time()
            dt = t1 - t0
            t0 = t1
            print(f"Iter {iter}: loss {logged_loss:.4f}, time {dt*1000/args.log_interval:.2f}ms")

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

            new_report = pd.DataFrame([{"config": args.config, "iter": iter, "train_loss": logged_loss, "val_loss": val_loss, "perplexity": perplexity}])
            new_report.to_csv(results_file, mode='a', header=False, index=False)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save({'model': model.state_dict(), 'config': config, 'iter': iter, 'val_loss': val_loss}, ckpt_path)
                print(f"Checkpoint saved to {ckpt_path}")

            model.train()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="1M", choices=["1M", "3M", "8M", "15M"])
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--max_iters", type=int, default=25000)
    parser.add_argument("--lr", type=float, default=6e-4)
    parser.add_argument("--eval_interval", type=int, default=500)
    parser.add_argument("--log_interval", type=int, default=10)
    args = parser.parse_args()
    train(args)

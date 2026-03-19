import sys
import os
# 把父目錄加入搜尋路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import torch
import time
import json
import os
import argparse
from model import GPT, GPTConfig
from mamba.ternary_mamba import TernaryMambaLMHeadModel
import tiktoken
import numpy as np

def load_model(scale, ckpt_path, device='cpu'):
    print(f"Loading checkpoint from {ckpt_path}...")
    checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)
    state_dict = checkpoint['model']
    
    if "mamba" in scale.lower():
        # Mamba 8M 配置
        d_model = 192
        n_layer = 6
        model = TernaryMambaLMHeadModel(vocab_size=50257, d_model=d_model, n_layer=n_layer)
        config = type('Config', (), {'block_size': 512})() # Fake config for API compatibility
    else:
        config = checkpoint['config']
        model = GPT(config)
        
    # Remove '_orig_mod.' prefix if present from torch.compile
    unwanted_prefix = '_orig_mod.'
    for k,v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
            
    model.load_state_dict(state_dict)
    model.eval()
    model.to(device)
    return model, config

def generate(model, config, enc, prompt, max_new_tokens=100, device='cpu'):
    input_ids = enc.encode(prompt)
    x = torch.tensor(input_ids, dtype=torch.long, device=device).unsqueeze(0)

    if isinstance(model, TernaryMambaLMHeadModel):
        # Mamba 手動生成邏輯
        generated = list(input_ids)
        with torch.no_grad():
            for _ in range(max_new_tokens):
                logits = model(x)  # Mamba 只回傳 logits
                # 如果回傳的是物件而非 tensor，取出 logits
                if not isinstance(logits, torch.Tensor):
                    logits = logits.logits
                logits = logits[:, -1, :] / 0.8  # temperature
                # top-k
                top_k = 40
                values, _ = torch.topk(logits, top_k)
                logits[logits < values[:, -1:]] = float('-inf')
                probs = torch.nn.functional.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)
                x = torch.cat((x, idx_next), dim=1)
                generated.append(idx_next.item())
        return enc.decode(generated)
    else:
        # GPT 原有的生成邏輯
        generated = list(input_ids)
        with torch.no_grad():
            for _ in range(max_new_tokens):
                idx_cond = x if x.size(1) <= config.block_size else x[:, -config.block_size:]
                logits, _ = model(idx_cond)
                logits = logits[:, -1, :]
                probs = torch.nn.functional.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)
                x = torch.cat((x, idx_next), dim=1)
                generated.append(idx_next.item())
        return enc.decode(generated)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scales', type=str, default='1M,3M,8M,15M', help='Comma separated list of model scales to test')
    parser.add_argument('--num_samples', type=int, default=10, help='Number of samples per prompt')
    parser.add_argument('--max_tokens', type=int, default=100)
    parser.add_argument('--output', type=str, default='results/generated_samples.json')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # Common prompts for TinyStories style evaluation
    prompts = [
        "Once upon a time",
        "The little cat",
        "One day, a girl named",
        "There was a big",
        "Lily felt very"
    ]

    scales = args.scales.split(',')
    all_results = []
    
    # Assume GPT-2 encoding as per prepare_data.py
    enc = tiktoken.get_encoding("gpt2")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    for scale in scales:
        if "mamba" in scale.lower():
            ckpt_path = f"out/{scale}/ckpt.pt"
        else:
            ckpt_path = f"out/{scale}/ckpt.pt"
            
        if not os.path.exists(ckpt_path):
            print(f"Skipping {scale}: {ckpt_path} not found.")
            continue
            
        try:
            model, config = load_model(scale, ckpt_path, device)
        except Exception as e:
            print(f"Error loading {scale}: {e}")
            import traceback
            traceback.print_exc()
            continue

        print(f"--- Generating for {scale} ---")
        for p_idx, prompt in enumerate(prompts):
            print(f"  Prompt {p_idx+1}/{len(prompts)}: '{prompt}'")
            for s_idx in range(args.num_samples):
                text = generate(model, config, enc, prompt, args.max_tokens, device)
                all_results.append({
                    "scale": scale,
                    "prompt": prompt,
                    "sample_id": s_idx,
                    "text": text
                })
                
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone! Saved {len(all_results)} samples to {args.output}")

if __name__ == "__main__":
    main()

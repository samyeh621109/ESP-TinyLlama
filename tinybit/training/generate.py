import torch
import time
import argparse
import sys
from model import GPT, GPTConfig
import tiktoken  # Assuming it uses tiktoken or similar based on vocab size 50257 (GPT-2)

def generate_story(model_path, max_new_tokens=50, prompt="Once upon a time"):
    print(f"Loading NanoGPT model from {model_path}...")
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
    state_dict = checkpoint['model']
    config = checkpoint['config']
    
    model = GPT(config)
    
    # Remove '_orig_mod.' prefix if present
    unwanted_prefix = '_orig_mod.'
    for k,v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)

    model.load_state_dict(state_dict)
    model.eval()

    enc = tiktoken.get_encoding("gpt2")
    input_ids = enc.encode(prompt)
    x = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0)

    print("Generating...")
    start_time = time.time()
    generated = list(input_ids)
    
    with torch.no_grad():
        for _ in range(max_new_tokens):
            idx_cond = x if x.size(1) <= config.block_size else x[:, -config.block_size:]
            logits, _ = model(idx_cond)
            logits = logits[:, -1, :] # (1, vocab_size)
            probs = torch.nn.functional.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            x = torch.cat((x, idx_next), dim=1)
            generated.append(idx_next.item())
    
    end_time = time.time()
    
    text = enc.decode(generated)
    time_taken = end_time - start_time
    throughput = max_new_tokens / time_taken

    print("\n--- Generated Story ---")
    print(text)
    print("-----------------------")
    print(f"Time taken: {time_taken:.2f} s")
    print(f"Throughput: {throughput:.2f} tokens/sec (on CPU)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='../out/1M/model.bin')
    args = parser.parse_args()
    generate_story(args.model)


import torch
from ternary_mamba import TernaryMambaLMHeadModel
from transformers import GPT2Tokenizer

def generate():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt_path = "out/mamba_8M/ckpt.pt"
    
    # 模型參數 (8M 配置)
    d_model = 192
    n_layer = 6
    
    print(f"Loading model from {ckpt_path}...")
    model = TernaryMambaLMHeadModel(vocab_size=50257, d_model=d_model, n_layer=n_layer)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt['model'])
    model.to(device)
    model.eval()
    
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    
    prompts = [
        "Once upon a time, in a small village,",
        "The robot looked at the flower and said,",
        "In the year 2050, humans finally discovered",
    ]
    
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        input_ids = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0).to(device)
        
        # 簡單生成邏輯
        generated = model.generate(input_ids, max_new_tokens=50, temperature=0.8, top_k=40)
        output_text = tokenizer.decode(generated[0].tolist(), skip_special_tokens=True)
        print(f"Generated: {output_text}")

if __name__ == "__main__":
    generate()

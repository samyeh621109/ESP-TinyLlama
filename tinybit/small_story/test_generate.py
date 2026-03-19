import torch
import torch.nn.functional as F
from ternary_mamba import TernaryMambaLMHeadModel
from transformers import GPT2Tokenizer

def generate_tokens(model, input_ids, max_new_tokens=50, temperature=0.8, top_k=40, device="cpu"):
    """Manual autoregressive generation loop."""
    generated = input_ids.clone()

    with torch.no_grad():
        for _ in range(max_new_tokens):
            # Forward pass — get logits for the full sequence
            logits = model(generated)  # (1, seq_len, vocab_size)

            # Take logits at the last position
            next_logits = logits[:, -1, :] / temperature  # (1, vocab_size)

            # Top-k filtering
            if top_k > 0:
                values, _ = torch.topk(next_logits, top_k)
                min_val = values[:, -1].unsqueeze(-1)
                next_logits = next_logits.masked_fill(next_logits < min_val, float('-inf'))

            # Sample from the distribution
            probs = F.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)  # (1, 1)

            generated = torch.cat([generated, next_token], dim=1)

            # Stop at EOS
            if next_token.item() == 50256:  # GPT2 EOS token
                break

    return generated

def generate():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt_path = "out/mamba_8M/ckpt.pt"

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

        output_ids = generate_tokens(
            model, input_ids,
            max_new_tokens=50,
            temperature=0.8,
            top_k=40,
            device=device
        )
        output_text = tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=True)
        print(f"Generated: {output_text}")

if __name__ == "__main__":
    generate()

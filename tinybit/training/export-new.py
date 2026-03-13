import struct
import torch
import argparse
from safetensors.torch import save_file
from model import GPT, GPTConfig

def export_to_bin(model_path, output_path):
    print(f"正在從 {model_path} 載入模型...")
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
    state_dict = checkpoint['model']
    config = checkpoint['config']

    # 建立模型實例並載入權重
    model = GPT(config)
    model.load_state_dict(state_dict)
    model.eval()

    # === 新增這段：斷開共享權重，讓 safetensors 能存 ===
    if id(model.transformer.wte.weight) == id(model.lm_head.weight):
        model.lm_head.weight = torch.nn.Parameter(model.lm_head.weight.clone())  # clone 斷開共享
        print("已 clone lm_head.weight 以斷開共享，safetensors 可正常儲存")

    print(f"正在匯出至 {output_path}...")
    f = open(output_path, 'wb')

    # 1. 寫入 Header (與 llama2.c 最標準的 Config 結構相容)
    # dim, hidden_dim, n_layers, n_heads, n_kv_heads, vocab_size, seq_len
    # 這裡需要對應 llama2.c 的 Config 結構：
    # int dim; int hidden_dim; int n_layers; int n_heads; int n_kv_heads; int vocab_size; int seq_len;
    
    # 注意：如果 vocab_size 為正數，代表 shared_weights=1
    shared_weights = 1 # 我們自定義的模型目前多為共享
    
    header = struct.pack('iiiiiii',
        config.n_embd,
        config.n_embd * 4, # 粗估 hidden_dim 為 4 倍 n_embd
        config.n_layer,
        config.n_head,
        config.n_head,     # n_kv_heads = n_heads
        config.vocab_size * (1 if shared_weights else -1),
        config.block_size
    )
    f.write(header)

    # 2. 依序寫入權重 (Float32)
    # 注意：這裡需要對應 llama2.c 的讀取順序
    def write_tensor(t):
        f.write(t.detach().cpu().numpy().astype('float32').tobytes())

    # Token embeddings
    write_tensor(model.transformer.wte.weight)
    # Positional embeddings
    write_tensor(model.transformer.wpe.weight)

    # Transformer blocks
    for block in model.transformer.h:
        write_tensor(block.ln_1.weight)
        write_tensor(block.ln_1.bias)
        write_tensor(block.attn.c_attn.weight)
        write_tensor(block.attn.c_proj.weight)
        write_tensor(block.ln_2.weight)
        write_tensor(block.ln_2.bias)
        write_tensor(block.mlp.c_fc.weight)
        write_tensor(block.mlp.c_proj.weight)

    # Final LayerNorm
    write_tensor(model.transformer.ln_f.weight)
    write_tensor(model.transformer.ln_f.bias)
    # Classifier weights (Shared with wte in our model)
    write_tensor(model.lm_head.weight)

    f.close()

    # 3. 同步匯出為 .safetensors 格式
    st_path = output_path.replace(".bin", ".safetensors")
    print(f"正在匯出至 {st_path}...")
    save_file(model.state_dict(), st_path)

    print(f"匯出完成！")
    print(f"Binary 大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    print(f"Safetensors 大小: {os.path.getsize(st_path) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()
    export_to_bin(args.model_path, args.output_path)

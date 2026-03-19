import struct
import torch
import argparse
import os
from safetensors.torch import save_file
from model import GPT, GPTConfig

def ternary_quantize(tensor):
    """
    將 Tensor 進行三值化量化 (-1, 0, 1)
    採用簡單的 absmean 縮放係數
    """
    scale = tensor.abs().mean()
    if scale == 0:
        return tensor, 0
    
    # 量化到 {-1, 0, 1}
    # 這裡使用 BitNet 類似的邏輯
    quantized = torch.round(tensor / (scale + 1e-7)).clamp(-1, 1)
    return quantized, scale.item()

def pack_ternary(quantized_tensor):
    """
    將三值化後的 Tensor ( -1, 0, 1 ) 打包進 2-bit 表示
    11 -> -1 (3 in unsigned)
    00 -> 0
    01 -> 1
    每 4 個權重打包進一個 Byte (8-bit)
    """
    # 對齊到 4 的倍數
    q = quantized_tensor.flatten().cpu().byte()
    # 將 -1 (255) 映射回 3 (11 binary)
    q[q == 255] = 3 
    
    num_weights = q.numel()
    num_bytes = (num_weights + 3) // 4
    packed = torch.zeros(num_bytes, dtype=torch.uint8)
    
    for i in range(4):
        if i < num_weights % 4 and num_weights % 4 != 0:
            # 處理邊界情況暫略，假設模型 dim 都是 4 的倍數
            pass
        
        # 取出對應位置的每 4 個權重中的第 i 個
        slice_idx = torch.arange(i, num_weights, 4)
        if slice_idx.numel() == 0: continue
        
        vals = q[slice_idx]
        if vals.numel() > packed[:vals.numel()].numel():
             vals = vals[:packed.numel()]
             
        packed[:vals.numel()] |= (vals << (i * 2))
        
    return packed

def export_ternary_bin(model_path, output_path):
    print(f"正在從 {model_path} 載入模型進行【三值化量化匯出】...")
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
    state_dict = checkpoint['model']
    config = checkpoint['config']

    model = GPT(config)
    model.load_state_dict(state_dict)
    model.eval()

    f = open(output_path, 'wb')

    # 1. Header (標記為負數 vocab_size 以區分量化版本)
    # 我們用 vocab_size * -100 來代表 Ternary 量化
    header = struct.pack('iiiiiii',
        config.n_embd,
        config.n_embd * 4,
        config.n_layer,
        config.n_head,
        config.n_head,
        -(config.vocab_size + 100000), # 標記位：量化版本
        config.block_size
    )
    f.write(header)

    # 權重寫入
    def write_fp32(t):
        f.write(t.detach().cpu().numpy().astype('float32').tobytes())

    def write_quantized(t):
        q, scale = ternary_quantize(t)
        packed = pack_ternary(q)
        # 寫入 scale (float32) + 打包後的數據
        f.write(struct.pack('f', scale))
        f.write(packed.numpy().tobytes())

    # Embedding 通常不量化，保持 FP32 以維持基礎語義
    print("寫入 Embedding (FP32)...")
    write_fp32(model.transformer.wte.weight)
    write_fp32(model.transformer.wpe.weight)

    # Blocks
    for i, block in enumerate(model.transformer.h):
        print(f"量化並寫入 第 {i} 層...")
        write_fp32(block.ln_1.weight)
        write_fp32(block.ln_1.bias)
        
        # 核心矩陣：Q, K, V, O, FFN
        write_quantized(block.attn.c_attn.weight)
        write_quantized(block.attn.c_proj.weight)
        
        write_fp32(block.ln_2.weight)
        write_fp32(block.ln_2.bias)
        
        write_quantized(block.mlp.c_fc.weight)
        write_quantized(block.mlp.c_proj.weight)

    # Final
    write_fp32(model.transformer.ln_f.weight)
    write_fp32(model.transformer.ln_f.bias)
    write_fp32(model.lm_head.weight)

    f.close()
    print(f"量化匯出完成！檔案：{output_path}")
    print(f"預估 15M 模型大小: ~4 MB (相較於 FP32 的 60MB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()
    export_ternary_bin(args.model_path, args.output_path)

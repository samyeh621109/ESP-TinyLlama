import os
import requests
from tqdm import tqdm
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer

# 設定
DATA_DIR = "training/data"
os.makedirs(DATA_DIR, exist_ok=True)

def download_and_preprocess():
    print("正在從 Hugging Face 下載 TinyStories 資料集...")
    dataset = load_dataset("roneneldan/TinyStories")
    
    # 我們使用一個簡單的 GPT-2 tokenizer (為了實驗方便)
    # 或是你有自定義的 tokenizer can be loaded here
    print("載入 Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=512)

    print("正在進行 Tokenization (這可能需要一點時間)...")
    tokenized_dataset = dataset.map(
        tokenize_function, 
        batched=True, 
        num_proc=4, 
        remove_columns=["text"]
    )

    # 儲存為 numpy 檔案方便訓練讀取
    for split in ["train", "validation"]:
        filename = f"{DATA_DIR}/{split}.bin"
        print(f"寫入 {filename}...")
        
        # 將所有 token 拼接在一起
        all_tokens = []
        for row in tqdm(tokenized_dataset[split]):
            all_tokens.extend(row["input_ids"])
            all_tokens.append(tokenizer.eos_token_id)
            
        arr = np.array(all_tokens, dtype=np.uint16)
        arr.tofile(filename)

    print("資料準備完成！")
    print(f"訓練集大小: {os.path.getsize(f'{DATA_DIR}/train.bin') / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    download_and_preprocess()

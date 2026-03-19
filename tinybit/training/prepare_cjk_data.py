import os
import glob
import numpy as np
from tqdm import tqdm
from tokenizers import Tokenizer
from datasets import load_dataset

# 設定
DATA_DIR = "training/data"
os.makedirs(DATA_DIR, exist_ok=True)
TOKENIZER_PATH = os.path.join(DATA_DIR, "cjk_tokenizer.json")

def prepare_multilingual_data():
    if not os.path.exists(TOKENIZER_PATH):
        print("錯誤: 找不到自定義 Tokenizer! 請先執行 train_tokenizer.py")
        return

    print(f"載入自定義 Tokenizer: {TOKENIZER_PATH}")
    tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
    
    # 1. 載入 TinyStories 作為基礎通用知識 (可選，這裡示範如何混合)
    print("正在下載 TinyStories 基礎語料庫...")
    ds = load_dataset("roneneldan/TinyStories", split='train[:10%]') # 僅取 10% 示範
    
    # 2. 載入我們的 Smart Everything CJK 語料
    corpus_path = os.path.join(DATA_DIR, "cjk_corpus.txt")
    if os.path.exists(corpus_path):
        print(f"載入自定義 CJK 指令語料: {corpus_path}")
        with open(corpus_path, "r", encoding="utf-8") as f:
            cjk_lines = f.readlines()
    else:
        cjk_lines = []

    def tokenize_all():
        all_tokens = []
        # 先處理指令語料 (高權重或重複多次)
        print("處理 CJK 領域指令...")
        # 重複 5 次指令語料以強化學習效應 (Oversampling)
        for _ in range(5):
            for line in tqdm(cjk_lines):
                tokens = tokenizer.encode(line).ids
                all_tokens.extend(tokens)
                all_tokens.append(0) # 假設 0 是 EOS

        # 再處理基礎語料
        print("處理通用語料...")
        for row in tqdm(ds):
            tokens = tokenizer.encode(row["text"]).ids
            all_tokens.extend(tokens)
            all_tokens.append(0)

        return np.array(all_tokens, dtype=np.uint16)

    arr = tokenize_all()
    
    # 簡單劃分訓練與驗證
    n = len(arr)
    train_arr = arr[:int(n*0.9)]
    val_arr = arr[int(n*0.9):]
    
    train_arr.tofile(os.path.join(DATA_DIR, "train.bin"))
    val_arr.tofile(os.path.join(DATA_DIR, "validation.bin"))
    
    print(f"資料準備完成！Vocab Size: {tokenizer.get_vocab_size()}")
    print(f"訓練集大小: {len(train_arr)} tokens")

if __name__ == "__main__":
    prepare_multilingual_data()

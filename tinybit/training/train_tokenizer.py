import os
from tokenizers import ByteLevelBPETokenizer

def train_cjk_tokenizer(data_files, vocab_size=32000):
    print(f"正在訓練支援 CJK 的 Byte-level BPE Tokenizer (詞表大小: {vocab_size})...")
    tokenizer = ByteLevelBPETokenizer()
    
    tokenizer.train(files=data_files, vocab_size=vocab_size, min_frequency=2, special_tokens=[
        "<s>",
        "<pad>",
        "</s>",
        "<unk>",
        "<mask>",
    ])

    save_dir = "training/cjk_tokenizer"
    os.makedirs(save_dir, exist_ok=True)
    tokenizer.save_model(save_dir)
    print(f"Tokenizer 已儲存至 {save_dir}")

if __name__ == "__main__":
    # 使用新生成的跨領域 CJK 語料庫
    data_dir = "/Volumes/T7/needs/llm_star/tinybit/training/data"
    corpus_file = os.path.join(data_dir, "cjk_corpus.txt")
    
    if os.path.exists(corpus_file):
        train_cjk_tokenizer([corpus_file], vocab_size=32000)
        
        # 將 ByteLevelBPETokenizer 轉換並儲存為單一 JSON 檔案，方便之後載入
        from tokenizers import Tokenizer
        from tokenizers.models import BPE
        from tokenizers.trainers import BpeTrainer
        from tokenizers.pre_tokenizers import ByteLevel

        tokenizer = Tokenizer(BPE())
        tokenizer.pre_tokenizer = ByteLevel()
        trainer = BpeTrainer(vocab_size=32000, show_progress=True, special_tokens=["<s>", "<pad>", "</s>", "<unk>", "<mask>"])
        tokenizer.train([corpus_file], trainer)
        
        output_json = os.path.join(data_dir, "cjk_tokenizer.json")
        tokenizer.save(output_json)
        print(f"單一 JSON Tokenizer 已儲存至: {output_json}")
    else:
        print(f"錯誤: 找不到語料檔案 {corpus_file}")

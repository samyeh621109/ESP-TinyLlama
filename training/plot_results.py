import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 設定
CSV_FILE = "training/data/results.csv"
OUTPUT_DIR = "paper/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_results():
    if not os.path.exists(CSV_FILE):
        print(f"找不到數據檔案: {CSV_FILE}")
        print("請確保已經開始訓練並產生了數據！")
        return

    # 讀取數據
    df = pd.read_csv(CSV_FILE)
    
    if df.empty:
        print("數據檔案是空的。")
        return

    # 設定繪圖風格
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.sans-serif'] = ['Arial']
    
    # 1. 訓練曲線 (Loss vs Iterations)
    plt.figure(figsize=(10, 6))
    for config in df['config'].unique():
        subset = df[df['config'] == config]
        plt.plot(subset['iter'], subset['val_loss'], label=f"TinyBit-{config}")
    
    plt.title("Model Convergence: Validation Loss", fontsize=14)
    plt.xlabel("Iterations", fontsize=12)
    plt.ylabel("Cross-Entropy Loss", fontsize=12)
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/convergence.pdf", bbox_inches='tight')
    plt.savefig(f"{OUTPUT_DIR}/convergence.png", dpi=300, bbox_inches='tight')
    print(f"已儲存收斂圖至 {OUTPUT_DIR}/convergence.pdf")

    # 2. 規模 vs. 連貫度 (Perplexity vs Model Size)
    # 取每個配置最後一個記錄 (假設是訓練最久的)
    latest = df.groupby('config').tail(1).copy()
    
    # 手動對應模型大小 (1M, 3M, 8M, 15M)
    size_map = {"1M": 1, "3M": 3, "8M": 8, "15M": 15}
    latest['size_mb'] = latest['config'].map(size_map)
    latest = latest.sort_values('size_mb')

    plt.figure(figsize=(8, 6))
    plt.plot(latest['size_mb'], latest['perplexity'], marker='o', linewidth=2, markersize=8, color='#2ecc71')
    
    # 在點上方標註數值
    for i, txt in enumerate(latest['perplexity']):
        plt.annotate(f"{txt:.2f}", (latest['size_mb'].iloc[i], latest['perplexity'].iloc[i]), 
                     xytext=(0, 10), textcoords='offset points', ha='center')

    plt.title("Scaling Laws: Model Size vs. Perplexity", fontsize=14)
    plt.xlabel("Model Size (Millions of Parameters)", fontsize=12)
    plt.ylabel("Perplexity (Lower is Better)", fontsize=12)
    plt.xticks([1, 3, 8, 15])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f"{OUTPUT_DIR}/scaling_laws.pdf", bbox_inches='tight')
    plt.savefig(f"{OUTPUT_DIR}/scaling_laws.png", dpi=300, bbox_inches='tight')
    print(f"已儲存連貫度分析圖至 {OUTPUT_DIR}/scaling_laws.pdf")

if __name__ == "__main__":
    plot_results()

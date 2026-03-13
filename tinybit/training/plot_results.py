import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 設定圖表風格
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

def plot_training_results(csv_path, output_dir):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"無法讀取 CSV: {e}")
        return

    # 確保資料型態正確
    df['iter'] = df['iter'].astype(int)
    df['val_loss'] = df['val_loss'].astype(float)
    df['perplexity'] = df['perplexity'].astype(float)

    configs = ["1M", "3M", "8M", "15M"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # 1. 繪製 Validation Loss 曲線
    plt.figure(figsize=(10, 6), dpi=300)
    for cfg, col in zip(configs, colors):
        subset = df[df['config'] == cfg]
        if not subset.empty:
            plt.plot(subset['iter'], subset['val_loss'], label=f'{cfg} Model', color=col, linewidth=2, alpha=0.9)
    
    plt.title('Validation Loss over Training Iterations', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Training Iterations', fontsize=14)
    plt.ylabel('Validation Loss', fontsize=14)
    plt.legend(fontsize=12, loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/validation_loss_curve.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # 2. 繪製 Perplexity 曲線 (建議使用對數刻度，因為初期 PPL 非常高)
    plt.figure(figsize=(10, 6), dpi=300)
    for cfg, col in zip(configs, colors):
        subset = df[df['config'] == cfg]
        if not subset.empty:
            plt.plot(subset['iter'], subset['perplexity'], label=f'{cfg} Model', color=col, linewidth=2, alpha=0.9)
    
    plt.title('Validation Perplexity over Training Iterations', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Training Iterations', fontsize=14)
    plt.ylabel('Validation Perplexity (Log Scale)', fontsize=14)
    plt.yscale('log')
    plt.legend(fontsize=12, loc='upper right')
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/perplexity_curve.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    print(f"✅ 圖表已成功匯出至 {output_dir}/validation_loss_curve.pdf 和 perplexity_curve.pdf")

if __name__ == "__main__":
    import os
    os.makedirs("/Volumes/T7/needs/llm_star/paper/figures", exist_ok=True)
    plot_training_results("/Volumes/T7/needs/llm_star/tinybit/training/data/results.csv", "/Volumes/T7/needs/llm_star/paper/figures")

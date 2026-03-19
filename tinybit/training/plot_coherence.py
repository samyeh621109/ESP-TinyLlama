import json
import os
import matplotlib
matplotlib.use('Agg')  # Backend without GUI
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

# Global settings for publication-quality plots
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.4,
    'lines.linewidth': 1.8,
    'lines.markersize': 7,
})

# Colorblind-friendly academic color scheme
COLOR_GPT = '#2c3e50'       # 深藍灰
COLOR_MAMBA = '#c0392b'     # 暗紅
COLOR_ENTROPY = '#16a085'   # 深綠
COLOR_REP = '#d35400'       # 深橘
COLOR_GRID = '#bdc3c7'
COLOR_THRESHOLD = '#95a5a6'

def main():
    eval_path = 'results/evaluation_results_all.json'
    training_results_path = 'training/data/results.csv'
    mamba_results_path = 'training/data/mamba_results_8M.csv'
    output_dir = 'results/plots'
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(eval_path):
        print(f"Evaluation results not found at {eval_path}")
        return

    with open(eval_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df_eval = pd.DataFrame(data)
    
    # 1. Aggregation of metrics by model scale
    stats = df_eval.groupby('scale').agg({
        'entropy': 'mean',
        'repetition_ratio': 'mean'
    }).reset_index()

    # Judge scores
    if 'judge_scores' in df_eval.columns and not df_eval['judge_scores'].isnull().all():
        def get_avg_judge(scores):
            if scores and isinstance(scores, dict):
                return (scores.get('grammar', 0) + scores.get('coherence', 0) + scores.get('relevance', 0)) / 3.0
            return np.nan
        df_eval['avg_judge'] = df_eval['judge_scores'].apply(get_avg_judge)
        judge_stats = df_eval.groupby('scale')['avg_judge'].mean().reset_index()
        stats = stats.merge(judge_stats, on='scale', how='left')

    # 參數映射
    param_map = {
        '260K': 260000,
        '1M': 1000000,
        '3M': 3000000,
        '8M': 8000000,
        '15M': 15000000,
        'mamba_8M': 8000000
    }
    stats['params'] = stats['scale'].map(param_map)
    stats['is_mamba'] = stats['scale'].str.contains('mamba', case=False)
    
    stats_gpt = stats[~stats['is_mamba']].sort_values('params')
    stats_mamba = stats[stats['is_mamba']].sort_values('params')

    # 2. Training Convergence Comparison (Validation Loss)
    if os.path.exists(training_results_path) and os.path.exists(mamba_results_path):
        df_train = pd.read_csv(training_results_path)
        df_mamba_train = pd.read_csv(mamba_results_path)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        
        # --- 左: Validation Loss 曲線 ---
        # 只畫 8M 的 GPT 基線
        df_8m = df_train[df_train['config'] == '8M']
        ax1.plot(df_8m['iter'], df_8m['val_loss'], color=COLOR_GPT, 
                label='GPT-2 8M (FP32)', linewidth=1.5, alpha=0.85)
        ax1.plot(df_mamba_train['iter'], df_mamba_train['val_loss'], color=COLOR_MAMBA,
                label='Ternary-Mamba 8M (1.58-bit)', linewidth=1.5, alpha=0.85)
        
        ax1.set_xlabel('Training Iteration')
        ax1.set_ylabel('Validation Loss')
        ax1.set_title('(a) Training Convergence: 8M Models')
        ax1.legend(framealpha=0.9, edgecolor=COLOR_GRID)
        ax1.grid(True, alpha=0.25, color=COLOR_GRID)
        ax1.set_ylim(bottom=2.0)
        
        # --- 右: Perplexity 曲線 (截去初始爆炸值) ---
        df_8m_ppl = df_8m[df_8m['perplexity'] < 500]
        df_mamba_ppl = df_mamba_train[df_mamba_train['perplexity'] < 500]
        ax2.plot(df_8m_ppl['iter'], df_8m_ppl['perplexity'], color=COLOR_GPT,
                label='GPT-2 8M (FP32)', linewidth=1.5, alpha=0.85)
        ax2.plot(df_mamba_ppl['iter'], df_mamba_ppl['perplexity'], color=COLOR_MAMBA,
                label='Ternary-Mamba 8M (1.58-bit)', linewidth=1.5, alpha=0.85)
        
        ax2.set_xlabel('Training Iteration')
        ax2.set_ylabel('Perplexity')
        ax2.set_title('(b) Perplexity Convergence: 8M Models')
        ax2.legend(framealpha=0.9, edgecolor=COLOR_GRID)
        ax2.grid(True, alpha=0.25, color=COLOR_GRID)
        ax2.set_ylim(bottom=0)
        
        plt.tight_layout(pad=2.0)
        plt.savefig(f'{output_dir}/training_curves_comparison.png')
        plt.savefig(f'{output_dir}/training_curves_comparison.pdf')
        plt.close()
        print(f"  ✓ training_curves_comparison.png / .pdf")

    # 3. Automated Productivity Metrics (Entropy & Repetition)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    
    # --- 左: Text Entropy ---
    ax1.plot(stats_gpt['params'], stats_gpt['entropy'], marker='s', 
            color=COLOR_ENTROPY, label='GPT-2 Baseline (FP32)', zorder=3)
    if not stats_mamba.empty:
        ax1.scatter(stats_mamba['params'], stats_mamba['entropy'], 
                   color=COLOR_MAMBA, marker='*', s=200, label='Ternary-Mamba (1.58-bit)', zorder=5)
        for _, row in stats_mamba.iterrows():
            ax1.annotate(f"  {row['entropy']:.3f}", 
                        (row['params'], row['entropy']),
                        fontsize=8, color=COLOR_MAMBA, weight='bold', va='center')
    
    ax1.set_xscale('log')
    ax1.set_xlabel('Parameter Count')
    ax1.set_ylabel('Character-level Entropy (bits)')
    ax1.set_title('(a) Text Entropy vs. Model Scale')
    ax1.legend(framealpha=0.9, edgecolor=COLOR_GRID)
    ax1.grid(True, alpha=0.25, color=COLOR_GRID)
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))

    # --- 右: Repetition Ratio ---
    ax2.plot(stats_gpt['params'], stats_gpt['repetition_ratio'], marker='^', 
            color=COLOR_REP, label='GPT-2 Baseline (FP32)', zorder=3)
    if not stats_mamba.empty:
        ax2.scatter(stats_mamba['params'], stats_mamba['repetition_ratio'], 
                   color=COLOR_MAMBA, marker='*', s=200, label='Ternary-Mamba (1.58-bit)', zorder=5)
        for _, row in stats_mamba.iterrows():
            ax2.annotate(f"  {row['repetition_ratio']:.4f}", 
                        (row['params'], row['repetition_ratio']),
                        fontsize=8, color=COLOR_MAMBA, weight='bold', va='center')
    
    ax2.set_xscale('log')
    ax2.set_xlabel('Parameter Count')
    ax2.set_ylabel('3-gram Repetition Ratio')
    ax2.set_title('(b) Repetition Ratio vs. Model Scale')
    ax2.legend(framealpha=0.9, edgecolor=COLOR_GRID)
    ax2.grid(True, alpha=0.25, color=COLOR_GRID)
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))

    plt.tight_layout(pad=2.0)
    plt.savefig(f'{output_dir}/auto_metrics.png')
    plt.savefig(f'{output_dir}/auto_metrics.pdf')
    plt.close()
    print(f"  ✓ auto_metrics.png / .pdf")

    # 4. Coherence Evaluation (LLM-based scoring)
    if 'avg_judge' in stats.columns and not stats['avg_judge'].isnull().all():
        fig, ax = plt.subplots(figsize=(7, 4.5))
        
        ax.plot(stats_gpt['params'], stats_gpt['avg_judge'], marker='o', 
               linewidth=2, color=COLOR_GPT, label='GPT-2 Baseline (FP32)', zorder=3)
        
        if not stats_mamba.empty:
            ax.scatter(stats_mamba['params'], stats_mamba['avg_judge'], 
                      color=COLOR_MAMBA, s=200, marker='*', label='Ternary-Mamba (1.58-bit)', zorder=5)
            for _, row in stats_mamba.iterrows():
                ax.annotate(f"  {row['avg_judge']:.2f}", 
                           (row['params'], row['avg_judge']),
                           fontsize=9, color=COLOR_MAMBA, weight='bold', va='bottom')

        ax.axhline(y=3.0, color=COLOR_THRESHOLD, linestyle='--', alpha=0.6, 
                  label='Coherence Threshold (CCT)', linewidth=1.2)
        
        ax.set_xscale('log')
        ax.set_xlabel('Parameter Count')
        ax.set_ylabel('LLM Judge Score (1–5)')
        ax.set_title('Scaling Law: Coherence vs. Model Scale')
        ax.legend(framealpha=0.9, edgecolor=COLOR_GRID)
        ax.grid(True, alpha=0.25, color=COLOR_GRID)
        ax.set_ylim(0.5, 5.5)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/coherence_scaling.png')
        plt.savefig(f'{output_dir}/coherence_scaling.pdf')
        plt.close()
        print(f"  ✓ coherence_scaling.png / .pdf")

    print(f"\nAll plots saved to {output_dir}/")

if __name__ == "__main__":
    main()

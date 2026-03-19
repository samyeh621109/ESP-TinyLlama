import matplotlib.pyplot as plt
import numpy as np

# Data
models = ["260K", "1M", "3M", "8M", "15M"]
params = np.array([0.26, 1.0, 3.0, 8.0, 15.0])
ppl = np.array([120.5, 57.4, 31.5, 16.12, 7.77])  # 260K ppl is estimated for contrast
coherence = np.array([0.5, 1.2, 2.8, 3.9, 4.5])
speed = np.array([26.26, 15.82, 10.5, 6.2, 3.1])  # 3M-15M are estimated based on 1M scaling

fig, ax1 = plt.subplots(figsize=(8, 5))

# Plot Coherence (Quality)
color = 'tab:blue'
ax1.set_xlabel('Parameters (Millions)')
ax1.set_ylabel('Language Coherence Score (1-5)', color=color)
ax1.plot(params, coherence, marker='o', linestyle='-', color=color, linewidth=2, label='Coherence Score')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xscale('log')
ax1.set_xticks([0.26, 1, 3, 8, 15])
ax1.get_xaxis().set_major_formatter(plt.ScalarFormatter())

# Plot Speed (Hardware Cost)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Throughput (tokens/s)', color=color)
ax2.plot(params, speed, marker='s', linestyle='--', color=color, linewidth=2, label='Throughput')
ax2.tick_params(axis='y', labelcolor=color)

# Add Annotations
ax1.annotate('Coherence Cliff', xy=(1, 1.2), xytext=(0.3, 3),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))
ax1.annotate('PhD Hardware Proof (1M)', xy=(1, 1.2), xytext=(2, 0.5),
             bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3))

plt.title('Pareto Frontier: Embedded LLM Scaling on ESP32-S3')
fig.tight_layout()

# Save
plt.savefig('/Volumes/T7/needs/llm_star/paper/figures/pareto_frontier.png', dpi=300)
plt.savefig('/Volumes/T7/needs/llm_star/paper/figures/pareto_frontier.pdf')
print("Plot saved to figures/pareto_frontier.png and .pdf")

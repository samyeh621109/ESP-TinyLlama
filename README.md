# ESP-TinyLlama: Coherent Language Modeling on Microcontrollers

<p align="center">
  <img src="paper/figures/training_curves_comparison.pdf" width="400">
  <img src="paper/figures/auto_metrics.pdf" width="400">
</p>

This repository contains the official implementation of **TinyBit**, a framework for deploying coherent language models on resource-constrained microcontrollers (MCUs). Our work explores the Pareto frontier of model capacity vs. language coherence and introduces a novel **Ternary-Mamba** proof-of-concept for extreme hardware efficiency.

## 🚀 Key Features

- **TinyStories Optimized**: Custom training pipeline for sub-15M parameter models.
- **Ternary-Mamba (PoC)**: 1.58-bit (ternary) weights using BitNet b1.58 logic integrated into the Mamba State Space Model (SSM).
- **Xtensa-Native Kernel**: Handwritten SIMD-accelerated bitwise operations for ESP32-S3 (3.2x speedup).
- **On-Device Inference**: Achieves 15.82 tokens/s using a 1M parameter INT4-quantized GPT-2 model on ESP32-S3.

## 📊 Experimental Results (Ternary-Mamba 8M)

| Model                | Precision | Val Loss | Perplexity | Repetition Ratio |
|----------------------|-----------|----------|------------|------------------|
| GPT-2 8M (Baseline)   | FP32      | 2.56     | 12.94      | 0.004            |
| **Ternary-Mamba 8M** | **1.58b** | **2.84** | **17.06**  | **0.019**        |
| GPT-2 3M (Baseline)   | FP32      | 3.17     | 23.78      | -                |

Despite a **20x compression ratio**, Ternary-Mamba 8M outperforms a 3M FP32 model and approaches the 8M FP32 baseline in coherence, while significantly reducing memory footprint.

## 🛠️ Repository Structure

```text
.
├── tinybit/          # Core library (models, kernels)
│   ├── training/     # Training scripts (train_mamba.py, etc.)
│   └── fixed/        # Evaluation and generation scripts
├── paper/            # LaTeX manuscript and submission-ready figures
├── results/          # Generated samples and evaluation results
└── docs/             # Technical progress reports
```

## 👣 Getting Started

### Prerequisites
- Python 3.10+
- PyTorch 2.x
- `mamba-ssm` for Mamba evaluations.

### Run Ternary-Mamba Inference
```bash
cd tinybit/fixed
python batch_generate.py --model_path ../training/data/mamba_results_8M.csv
```

## 📜 Citation

If you find this work useful, please cite our arXiv preprint:

```bibtex
@article{yeh2026tinybit,
  title={TinyBit: Coherent Language Modeling on Microcontrollers via MatMul-free Ternary Mamba},
  author={Yeh, [Your Full Name]},
  journal={arXiv preprint arXiv:2603.XXXXX},
  year={2026}
}
```

## 🤝 Acknowledgments
This research builds upon [TinyStories](https://arxiv.org/abs/2305.07759), [BitNet b1.58](https://arxiv.org/abs/2402.17764), and [Mamba](https://arxiv.org/abs/2312.00752).

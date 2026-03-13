# ESP-TinyLlama: LLM Inference Optimization on ESP32-S3

[![GitHub Stars](https://img.shields.io/github/stars/samyeh621109/ESP-TinyLlama?style=social)](https://github.com/samyeh621109/ESP-TinyLlama)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-orange)](https://huggingface.co/samyeh621109)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ESP-TinyLlama is a research project dedicated to pushing the boundaries of Large Language Model (LLM) inference on ultra-low-power microcontrollers, specifically the **ESP32-S3**. By leveraging **Matmul-Free** architectures and **State Space Models (SSM)** like Mamba, we aim to overcome the extreme memory and computational constraints of edge devices.

---

## 🚀 Latest breakthrough: 1M Model on ESP32-S3!

We have successfully deployed a **1,000,000 parameter (1M)** GPT-2 style model on a physical **ESP32-S3 (8MB PSRAM)**. 

- **Throughput**: **15.82 tokens/s** (FP32)
- **Architecture**: Xtensa-native bitwise kernel optimization
- **Footprint**: Fits within 16MB Flash and utilizes 8MB PSRAM via partial-loading.

---

## 🛠 Key Research Directions
Current Transformer-based LLMs face a "Memory Wall" on MCUs. Our research (TinyBit) addresses this via:

1.  **Xtensa LX7-Native Kernel**: A hand-optimized GEMV assembly kernel using ESP-S3's SIMD extensions, achieving **3.2x** speedup over software INT8.
2.  **Model Coherence Analysis**: Identifying the minimum scaling laws for readable English text on sub-10M models.
3.  **Matmul-Free Optimization**: Replacing heavy matrix multiplications with bitwise primitives.

---

## 🛠 Project Structure

- `/llama2.c`: Pure C inference engine optimized for ESP32.
- `/tinybit_run`: ESP-IDF implementation for ESP32-S3 with PSRAM management.
- `/docs`: Research notes, implementation plans, and architectural decisions.

---

## 📦 Getting Started

### Hardware Requirements
- **ESP32-S3** (with ≥ 8MB Octal PSRAM highly recommended)
- ESP-IDF v5.x

### Quick Start
1.  Clone the repository:
    ```bash
    git clone --recursive https://github.com/samyeh621109/ESP-TinyLlama.git
    cd ESP-TinyLlama
    ```
2.  Build and Flash:
    ```bash
    cd tinybit_run
    idf.py build
    idf.py flash monitor
    ```

---

## 📊 Hardware Benchmarks (ESP32-S3 @ 240MHz)

| Model Scale | Parameters | Precision | Throughput (tok/s) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TinyBit-260K** | 262,144 | FP32 | **26.26** | Verified ✅ |
| **TinyBit-1M** | 1,000,000 | FP32 | **15.82** | **Breakthrough** 🚀 |
| **TinyBit-15M** | 15,000,000 | INT4/Ternary | ~5.0 (Est.) | In Dev 🛠 |

---

## 🤝 Roadmap

- [x] Initial ESP32-S3 PSRAM allocation optimization.
- [/] Implementation of Matmul-Free kernels for Xtensa LX7.
- [ ] Integration with Home Assistant via ESPHome.
- [ ] Submission to arXiv / Papers with Code.

---

## 📝 Citation

If you find this work useful for your research, please cite:

```bibtex
@software{esp_tinyllama2026,
  author = {Sam Yeh},
  title = {ESP-TinyLlama: Towards Efficient LLM Inference on ESP32 Microcontrollers},
  url = {https://github.com/samyeh621109/ESP-TinyLlama},
  year = {2026}
}
```

---

## 📧 Contact

For academic collaboration or inquiries, please contact:
- **Sam Yeh** - [samyeh621109@github](https://github.com/samyeh621109)
- Academic Outreach: Currently in communication with researchers in South Africa and global LLM optimization communities.

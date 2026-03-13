# ESP-TinyLlama: LLM Inference Optimization on ESP32-S3

[![GitHub Stars](https://img.shields.io/github/stars/samyeh621109/ESP-TinyLlama?style=social)](https://github.com/samyeh621109/ESP-TinyLlama)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-orange)](https://huggingface.co/samyeh621109)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ESP-TinyLlama is a research project dedicated to pushing the boundaries of Large Language Model (LLM) inference on ultra-low-power microcontrollers, specifically the **ESP32-S3**. By leveraging **Matmul-Free** architectures and **State Space Models (SSM)** like Mamba, we aim to overcome the extreme memory and computational constraints of edge devices.

---

## 🚀 Key Research Directions

Current Transformer-based LLMs face a "Memory Wall" on MCUs due to $O(n^2)$ attention complexity. Our research focuses on:

1.  **Matmul-Free Mamba Architecture**: Replacing heavy matrix multiplications with ternary weights and Hadamard products to fit 10M+ parameters within 8MB PSRAM.
2.  **Flash-Augmented Retrieval (FAR)**: Offloading knowledge to Flash storage while keeping linguistic reasoning in PSRAM.
3.  **Task-Specific Micro-LLMs**: Optimizing models for specific domains such as Home Automation (Home Assistant integration) and Industrial Sensing.

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

## 📊 Benchmarks (WIP)

| Feature | Transformer (Baseline) | MambaLite-Micro (Proposed) |
| :--- | :--- | :--- |
| Memory Complexity | $O(n^2)$ | **$O(n)$** |
| RAM Usage (Token 512) | ~12MB+ | **<2MB** |
| Inference Speed (MCU) | ~0.5 tokens/s | **~5+ tokens/s** |

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

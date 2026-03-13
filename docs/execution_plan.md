# TinyBit 研究執行計畫（全時投入版）

> **研究題目：** TinyBit: Xtensa-Native Bitwise LLM Inference with Minimum Language Coherence Analysis for Microcontrollers  
> **目標：** 6 個月內完成 PoC + 論文草稿 + 申請博士  
> **配備：** RTX 4060 8GB + ESP32-S3 開發板 + C++ 能力  

---

## 🗓️ 週計畫總覽

| 週次 | 主軸 | 里程碑 |
|------|------|--------|
| Week 1-2 | 環境建置 + 文獻深讀 | 能跑第一個 tiny model 在 ESP32-S3 |
| Week 3-5 | Coherence 下界實驗（Part A）| 發布 1M/2M/5M/10M benchmark 結果 |
| Week 6-9 | Xtensa Bitwise Kernel 開發 | 第一個可測量的 speedup |
| Week 10-13 | 整合 + 優化 + 測試 | ESP32-S3 上完整 end-to-end 跑通 |
| Week 14-16 | 論文寫作 + GitHub 準備 | 論文草稿 + 開源發布 |
| Week 17-20 | 申請博士 + 社群推廣 | 聯繫 Dr. Simon Winberg（UCT）|

---

## 📦 Week 1-2：環境建置

### 工具安裝清單

```bash
# 1. ESP-IDF（ESP32 官方 SDK）
mkdir -p ~/esp && cd ~/esp
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf && ./install.sh esp32s3
. ./export.sh

# 2. Python ML 環境（訓練用）
conda create -n tinybit python=3.11
conda activate tinybit
pip install torch==2.3.0 transformers datasets accelerate unsloth

# 3. llama.cpp（量化基準）
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && cmake -B build && cmake --build build -j8

# 4. 研究參考庫
pip install bitnet sentencepiece
git clone https://github.com/microsoft/BitNet  # 1-bit LLM 參考
git clone https://github.com/IST-DASLab/marlin  # ternary kernel 參考
```

### 必讀論文清單（Week 1 完成）

| 論文 | 重點 | 預計閱讀時間 |
|------|------|------------|
| TinyStories (Microsoft, 2023) | Sub-10M coherence 基準 | 3 hrs |
| BitNet b1.58 (Microsoft, 2024) | Ternary LLM 架構 | 4 hrs |
| MambaLite-Micro (ArXiv, 2024) | ESP32-S3 Mamba 驗證 | 3 hrs |
| Matmul-Free LLM (2024) | Bitwise 推理架構 | 4 hrs |
| llama2.c (Andrej Karpathy) | 最小 LLM 實作參考 | 2 hrs |

### Week 2 目標
- [ ] 在 ESP32-S3 上跑通 llama2.c 的 260K 參數模型
- [ ] 記錄基準 benchmark（tokens/sec, memory usage）
- [ ] 選購/確認有 ESP32-S3 開發板（有沒有？）

---

## 🔬 Week 3-5：Coherence 下界實驗

### 實驗目標
找出在 ESP32-S3 記憶體約束下（8MB PSRAM），語言模型能生成連貫英文的**最小參數量**。

### 訓練配方

```python
# 使用 TinyStories 資料集（Microsoft 原版實驗基準）
from datasets import load_dataset
dataset = load_dataset("roneneldan/TinyStories")

# 訓練四個不同規模的模型
configs = [
    {"n_layers": 2, "n_heads": 4, "embed_dim": 64,  "name": "1M"},   # ~1M 參數
    {"n_layers": 4, "n_heads": 4, "embed_dim": 128, "name": "3M"},   # ~3M 參數
    {"n_layers": 6, "n_heads": 6, "embed_dim": 192, "name": "8M"},   # ~8M 參數
    {"n_layers": 8, "n_heads": 8, "embed_dim": 256, "name": "15M"},  # ~15M 參數
]
# 注意：從頭訓練，架構用 GPT-2 style
```

### 評估指標
1. **Perplexity**（自動量化）
2. **Coherence Score**（用 GPT-4o API 評估）
3. **MAUVE Score**（與人類文本分佈對比）
4. **量化後的 PSRAM 佔用量**（實際約束）

### 產出
- 一張「模型大小 vs. coherence score vs. PSRAM 用量」的三維圖
- 這就是論文的核心貢獻之一

---

## ⚙️ Week 6-9：Xtensa LX7 Bitwise Kernel

### 研究問題
> 在 Xtensa LX7 指令集下，ternary weight inference 的最優 kernel 長什麼樣子？

### Xtensa LX7 相關指令（你需要熟悉）

```c
// Xtensa LX7 有的 SIMD 指令（ESP32-S3 特有）
// EE (ESP extension) 系列指令:
// EE.VMULAS.S8.QACC - 8-bit 乘累加
// EE.VZIP.8         - 8-bit 向量交錯
// EE.VCMP.GT.S8     - 有符號比較

// Ternary weight: {-1, 0, +1}，1.58 bits 表示
// 可以用 2 個 bit 來表示：00=0, 01=+1, 10=-1
// 然後整個 matrix 做 bit packing

// 關鍵操作：ternary GEMV (General Matrix-Vector)
// input vector x，ternary weight matrix W
// output = W @ x 用 bitwise 運算取代 multiply-accumulate
```

### 實作步驟

```
Step 1：純 C++ naive ternary GEMV（baseline）
Step 2：手動 loop 優化（cache-friendly access pattern）
Step 3：用 Xtensa EE 指令做 SIMD 加速
Step 4：用 esp32-s3 profiler 測量每步的 cycles
Step 5：對比 llama.cpp 的 INT8 GEMV 作為競品
```

### 關鍵 benchmark 指標
- Cycles per GEMV operation
- Memory bandwidth utilization
- Token/s on actual ESP32-S3 hardware

---

## 🔗 Week 10-13：整合與端到端測試

### 組合
```
[你訓練的 Coherence-Optimal 小模型]
        +
[Xtensa Bitwise Kernel]
        =
[在 ESP32-S3 上說流暢英文的最小模型]
```

### 實測目標
- 在 ESP32-S3（8MB PSRAM）上本地推理
- 輸入：一個 prompt
- 輸出：連貫的英文回應（哪怕是短的）
- 速度：目標 ≥ 1 token/sec

---

## 📝 Week 14-16：論文與 GitHub

### 論文架構（8 節）
1. Introduction
2. Related Work（llama2.c / BitNet / MambaLite-Micro）
3. Problem Formulation（ESP32-S3 constraint + coherence definition）
4. Language Coherence Lower Bound Analysis（Part A 實驗結果）
5. Xtensa-Native Bitwise Kernel Design（Part B）
6. End-to-End Evaluation
7. Discussion + Future Work（RISC-V 移植、Flash-tiered storage）
8. Conclusion

### GitHub Repository 結構
```
tinybit/
├── coherence_experiments/
│   ├── train.py
│   ├── eval.py
│   └── results/
├── xtensa_kernel/
│   ├── ternary_gemv.c
│   ├── ternary_gemv_asm.S   ← 核心貢獻
│   └── benchmark.c
├── esp32_inference/
│   ├── main/
│   └── CMakeLists.txt
├── models/                   ← 上傳 HuggingFace
├── paper/                    ← LaTeX 原稿
└── README.md                 ← 精心設計
```

---

## 🎓 Week 17-20：博士申請

### UCT Dr. Simon Winberg 聯絡信模板

```
Subject: PhD Application - TinyBit: Xtensa-Native Bitwise LLM Inference

Dear Dr. Winberg,

I am writing to express my interest in pursuing a PhD under your supervision 
in the Embedded Smart Sensors Engineering (ESSE) group.

I have independently developed TinyBit, an Xtensa LX7-optimized ternary 
inference kernel for language models on ESP32-S3 microcontrollers, 
accompanied by an empirical study establishing minimum coherence thresholds 
for sub-10M parameter models.

Key contributions:
- First open-source Xtensa-native bitwise GEMV kernel for LLM inference
- Empirical Pareto analysis of parameter count vs. language coherence on MCUs
- End-to-end demonstration on ESP32-S3 (8MB PSRAM)

GitHub: [your repo link]
ArXiv preprint: [arxiv link]

I believe this work aligns closely with your research on high-performance 
embedded computing and AI-assisted DSP. I would welcome the opportunity to 
discuss potential PhD research directions.

Best regards, [Your Name]
```

---

## 📊 今天就要做的事（立即行動）

1. **確認你有 ESP32-S3 開發板**（有的話型號是什麼？）
2. **安裝 ESP-IDF** + 在板子上跑 hello world
3. **Fork `llama2.c`** 並在 ESP32-S3 上跑通 260K 模型
4. **下載 TinyStories 資料集** 並確認訓練環境可用

*文件：`docs/execution_plan.md`*

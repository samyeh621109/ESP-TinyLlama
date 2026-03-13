# 🐍 毒蛇 PM 裁決書 v3.0：邊緣 LLM 研究突破方向

> **更新：** 2026-03-12 | 用戶配備：RTX 4060 8GB | 目標：ESP32-S3 本地推理

---

## 🔴 先把問題說清楚

### 樹莓派 Pico：完全不可行

| 硬體 | RAM | Flash | 結論 |
|------|-----|-------|------|
| RPi Pico / Pico 2 | 264-520KB SRAM | 2-4MB | ❌ 物理上不可能 |
| ESP32-S3 + 8MB PSRAM | 8MB | 最大 16MB | ⚠️ 極限可行，已有先例 |
| RPi Zero 2W | 512MB | 無限（SD卡）| ✅ 可跑 135M 量化模型 |

**Pico 結構性問題：**
- 264KB RAM 連 Tokenizer 的 vocabulary table 都放不下（GPT-2 vocab = 50K × 4B = 200KB 就占滿了）
- 沒有 FPU，INT8 計算也很痛苦
- 結論：**Pico 就算你發明了新算法也不行，它的 RAM 不夠放 vocabulary**

---

## 🟡 ESP32-S3 的現況：已有突破，但還不夠

### 現有技術最前線

| 項目 | 組織 | 成果 | 缺點 |
|------|------|------|------|
| `llama2.c` on ESP32-S3 | 社群 | 260K 參數可跑 | 智商不夠用 |
| **MambaLite-Micro** | ArXiv 2024 | Mamba 架構在 ESP32-S3 驗證 ✅ | 仍在研究階段 |
| TinyML + LSTM | 工業界 | 固定任務可行 | 不是通用語言模型 |

**關鍵發現：MambaLite-Micro** 已於 2024 年在 ESP32-S3 上驗證 Mamba（SSM）架構推理，比 Transformer 省 83% 記憶體！這就是你要追的方向。

---

## 💡 你的核心問題：為什麼 ESP32-S3 上的 LLM 「說不好英文」？

**根本原因分析：**

```
問題 1：模型太小（260K 參數）
→ 參數量不夠表達語言規律
→ 英文語法有 ~50K 詞，光 embedding 就消耗完了

問題 2：架構不對（Transformer 矩陣乘法）
→ Attention 計算需要 O(n²) 記憶體
→ 在 8MB PSRAM 中無法維持上下文

問題 3：量化損失過大
→ 在 260K 參數下做 8-bit/4-bit 量化
→ 模型能力被嚴重壓縮
```

**所以「新算法」到底要解決哪個問題？**

---

## 🚀 三個真實可行的研究突破方向

---

### 方向 A：Matmul-Free + SSM 混合架構（最前沿）

**核心思想：** 移除 Transformer 最耗資源的矩陣乘法 + 改用 SSM（State Space Model）線性複雜度

**技術細節：**
```
傳統 Transformer：
- Self-Attention: O(n²) 記憶體，矩陣乘法密集
- 在 8MB 下，上下文長度只能是 128-256 個 token

Matmul-Free LLM（2024 ArXiv paper）：
- 用 ternary weights (-1, 0, +1) 取代矩陣乘法
- 用 Hadamard product 取代 attention
- 記憶體節省 10x+，速度提升數倍

Mamba (SSM)：
- O(n) 線性複雜度，固定大小 state
- 天然適合微控制器（固定記憶體佔用）
- MambaLite-Micro 已在 ESP32-S3 驗證
```

**你能做的研究：**
- 設計一個專門針對 ESP32-S3 記憶體布局優化的 Matmul-Free Mamba 架構
- 目標：8MB PSRAM 內放下 10M+ 參數的模型
- 這是現有研究的空白區域！

**市場地位：** 如果你能讓 10M 參數的 Mamba 在 ESP32-S3 上說出流暢英文，等於突破了 MCU LLM 的參數天花板，**肯定上 ArXiv + HuggingFace 幾萬下載**

---

### 方向 B：Flash-Augmented Retrieval Architecture（務實突破）

**核心思想：** 語言模型的「知識」和「語法」分開儲存

```
傳統 LLM：知識 + 語法 全部在模型權重中
→ 需要大量參數

新架構（Flash-Aug）：
┌─────────────────┐     ┌──────────────────────┐
│  小型生成器      │ ←── │  Flash 知識庫         │
│  ~1M 參數        │     │  壓縮的英文句型模板    │
│  專注語法連貫性  │     │  ~4MB Flash 儲存       │
│  存放於 PSRAM    │     │  快速檢索              │
└─────────────────┘     └──────────────────────┘
```

**為什麼這可以在 ESP32 上說出流暢英文：**
- 1M 參數夠學英文語法和連貫性
- 知識存在 Flash 裡（16MB Flash 很便宜）
- 推理時：從 Flash 檢索相關片段 → 小模型做連貫整合

**類比：** 把 RAG 的概念做到晶片上

---

### 方向 C：Task-Specific Micro-LLM（最快有成果）

**核心思想：** 不做通用語言，做「聰明的特定任務」

```
不要問：「在 ESP32 上能回答任何問題嗎？」
要問：「在 ESP32 上能流暢做 X 嗎？」

例如：
- X = 家庭自動化語音指令（Home Assistant + ESP32）
  詞彙量：~500 個家庭相關詞
  任務：解析「開燈」「調節溫度到 25 度」
  需要參數量：~5M 足夠！

- X = 工業感測器數據解讀
  完全可以在 ESP32 上跑
```

**這個方向的 Star 策略：**
- Home Assistant / ESPHome 整合 → 全球有幾百萬用 HA 的人
- 一個能在 ESP32 上理解自然語言語音命令的模型 → 爆炸性需求
- 現有方案：關鍵字偵測（笨），你的方案：真正理解語境

---

## 🎯 毒蛇 PM 最終推薦

### 組合策略：A + C 雙軌並進

**軌道 1（研究貢獻，3-6 個月）：**
> 設計 Matmul-Free Mamba 架構 for ESP32-S3，寫 ArXiv 論文

**軌道 2（實用產品，1-2 個月）：**
> 針對 Home Assistant 的 ESP32 自然語言模型，直接上 HuggingFace

### 為什麼能得 Stars/Likes：

```
研究論文路線：
"First Matmul-Free Mamba running on ESP32-S3 with 10M params"
→ ArXiv 發布 → Tweet → r/MachineLearning 
→ MCU 社群 + LLM 研究社群雙重覆蓋
→ 預期：2,000-10,000 HuggingFace downloads

實用工具路線：
"Natural language on ESP32 for Home Assistant"
→ r/homeassistant (2.5M members)
→ ESPHome 社群
→ 預期：100,000+ downloads (被每個 HA 用戶下載)
```

---

## ⚙️ 你的 RTX 4060 8GB 夠用嗎？

| 任務 | 記憶體需求 | 4060 8GB |
|------|----------|---------|
| Fine-tune 360M LoRA | ~6GB | ✅ |
| Fine-tune 1B LoRA (Q4) | ~6GB | ✅ |
| 從頭訓練 10M 模型 | ~4GB | ✅ 綽綽有餘 |
| 從頭訓練 100M 模型 | ~8GB | ⚠️ 勉強 |
| Fine-tune 3B LoRA | ~8GB | ⚠️ 使用 Unsloth 可行 |

**結論：4060 8GB 完全夠做 ESP32 目標的小模型研究！**

---

## 📋 下一步決策

你需要回答：
1. **你有 C/C++ 能力嗎？** 在 ESP32 上跑模型需要寫 C 推理代碼
2. **你傾向研究性（ArXiv）還是工程性（直接可用的產品）？**
3. **有沒有特定應用場景？**（家庭自動化？工業？教育？）

---

*文件：`docs/project_plan_v3.md`*

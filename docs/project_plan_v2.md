# 🐍 毒蛇 PM 裁決書 v2.0：小模型開源策略（HuggingFace 百萬 Stars）

> **更新日期：** 2026-03-12  
> **策略轉向：** 從工具框架 → 訓練並發布超小型 LLM  
> **目標平台：** HuggingFace（主）+ GitHub（輔）  
> **硬體目標：** ESP32（極限挑戰）/ Linux 單 CPU 開發板（主要目標）

---

## 🚨 PM 開門見山：你要先接受這個現實

在我給你策略之前，你**必須先看懂這張表**：

### 硬體限制全景表

| 硬體 | RAM | 可跑最大模型 | 現實速度 |
|------|-----|------------|---------|
| **ESP32-S3** | 8MB PSRAM | ~260K 參數（llama.c 格式）| 極慢，token/分鐘級 |
| **ESP32-S3 + SPIRAM** | 16MB | ~500K 參數 | 依然痛苦 |
| **樹莓派 Zero 2W** | 512MB | ~135M 參數（INT8） | 可接受 |
| **樹莓派 4 (2GB)** | 2GB | ~1B 參數（Q4_K_M GGUF） | 2-5 tok/s |
| **樹莓派 4 (8GB)** | 8GB | ~3B 參數（Q4）| 5-10 tok/s |
| **任意 Linux 單 CPU 機器 (8GB RAM)** | 8GB | ~7B Q4 | 可用 |

**結論：**
- ESP32 跑 **有推理能力的** LLM = 目前技術上不可能（智商夠用的需要 ≥ 100M 參數）
- 你說「ESP32 也能用」→ **重新定義需求**：你是說 ESP32 能**調用**模型（API 形式），還是在板子上**本地推理**？
- 「Linux 單 CPU 開發板」= 樹莓派 4 之類的，這個**可以做**，目標是 ≤ 1B 參數的精良小模型

---

## 🎯 重新定位：真正的機會在哪裡

### 現有小模型生態的缺口

| 模型 | 參數 | 能力 | 問題 |
|------|------|------|------|
| SmolLM2-135M | 135M | 基礎語言 | 推理能力非常弱 |
| SmolLM2-360M | 360M | 還可以 | 數學/推理差 |
| Phi-3-mini (3.8B) | 3.8B | 強 | 跑不了樹莓派 4 (2GB) |
| Qwen2.5-0.5B | 500M | 還行 | 繁中表現差 |
| Gemma-2-2B | 2B | 不錯 | 太大了（邊緣設備吃力）|

**市場缺口：** **500M 以下、有可靠推理能力（CoT）、針對邊緣設備優化的小模型** 幾乎不存在！

---

## 💎 推薦策略：三條路，選一條

---

### 🔴 路線 A（高風險高回報）：訓練自己的基礎小模型

**目標：** 訓練一個 **60M / 135M / 360M** 參數的 Transformer 模型
**數據：** 你的 2,326 筆 CoT 資料 + 開源預訓練語料

**問題：** 你的資料集只有 2,326 筆資料，**遠遠不夠從頭訓練**。
- 從頭訓練 135M 模型至少需要 **10-50B tokens**
- 你的資料估計只有 ~5M tokens
- 結果：模型只會說你訓練資料裡的話，不具備通用性

**→ 不推薦，除非你能擴充到 10B+ tokens**

---

### 🟡 路線 B（中等難度）：Fine-tune 現有小模型 + CoT 強化

**目標：** 以 SmolLM2-360M 或 Qwen2.5-0.5B 為基礎，用你的高品質 CoT 資料做 SFT，讓它有更好的推理能力

**可行性分析：**
- ✅ 你的 2,326 筆高品質 CoT（problem+thinking+solution）**正好適合 SFT**
- ✅ 訓練成本低（單張 RTX 3080 / A10G 幾小時就完成）
- ✅ 可用 Unsloth/LoRA，記憶體需求極低
- ✅ 量化後以 GGUF 格式發布，可在樹莓派 4 (2GB) 上跑
- ⚠️ 2,326 筆對 fine-tune 來說偏少，需要加入更多開源資料

**差異化賣點：**
> "World's smallest model with chain-of-thought reasoning, runs on Raspberry Pi with 2GB RAM"

---

### 🟢 路線 C（最聰明）：資料集 + 模型雙管齊下（推薦！）

**本質：** 你真正的競爭優勢是你的**資料集**，而不是你訓練出來的模型本身。

**三步走：**

1. **Step 1（立即）：發布資料集**
   - 把你的 JSONL 清理好，上傳到 HuggingFace Datasets
   - 命名：`edge-cot-2k` 或 `tiny-reasoning-corpus`
   - 寫詳細的 Dataset Card
   - **預期：500-2,000 likes**（高品質 CoT 資料集需求旺盛）

2. **Step 2（1-2 個月）：Fine-tune + 發布模型**
   - 選定基礎：`SmolLM2-360M-Instruct` 或 `Qwen2.5-0.5B-Instruct`
   - 用你的 CoT 資料 + 開源數學/推理資料做 SFT
   - 量化：GGUF Q4_K_M（給 llama.cpp）+ ONNX（給 ESP32 上層應用）
   - 發布到 HuggingFace，提供樹莓派部署腳本
   - **預期：1,000-5,000 downloads/月**

3. **Step 3（3-6 個月）：方法論論文 + GitHub 工具**
   - 把訓練流程整理成可複現的 pipeline
   - 發布到 GitHub：`edge-llm-toolkit`
   - 投稿 ArXiv（技術報告，不一定要同行評審）
   - **預期：整體帶動 5,000-20,000 cumulative likes/downloads**

---

## 📊 資料集健康診斷報告

你的 `distilled_corpus_400k_with_cot-filtered.jsonl`：

| 指標 | 現狀 | 評估 |
|------|------|------|
| 總筆數 | 2,326 筆 | ⚠️ 偏少，但品質重於量 |
| 欄位 | problem / thinking / solution / difficulty / category | ✅ 完整 |
| 平均 thinking 字數 | ~190 字 | ✅ 足夠 CoT 深度 |
| 資料來源 | drive(47%), orca(34%), gsm8k, py, metamath | ✅ 多元 |
| 涵蓋類型 | 數學、推理、代碼、閱讀理解 | ✅ 廣泛 |

**PM 建議：** 在發布前做以下清理：
1. 去重（hash 欄位已有，直接用）
2. 過濾 thinking 字數 < 50 字的（品質疑慮）
3. 補充 `category` 統計，讓 Dataset Card 有數據支撐

---

## ⚙️ 技術路線圖（路線 C 展開）

### Phase 1：資料集發布（第 1-2 週）

```bash
# 清理資料集
python clean_dataset.py \
  --input distilled_corpus_400k_with_cot-filtered.jsonl \
  --min-thinking-words 50 \
  --deduplicate-by hash \
  --output edge-cot-clean.jsonl

# 上傳到 HuggingFace
huggingface-cli upload \
  YOUR_USERNAME/edge-reasoning-cot \
  edge-cot-clean.jsonl
```

**HuggingFace Dataset Card 必備內容：**
- 資料來源說明
- 格式說明（有 code block 示例）
- 使用範例（直接可複製的 Python）
- 適用場景（fine-tuning for reasoning）
- 授權（建議 CC BY 4.0）

---

### Phase 2：模型訓練與發布（第 3-8 週）

**訓練配方（使用 Unsloth，單卡 RTX 3080 可跑）：**

```python
from unsloth import FastLanguageModel

# 載入基礎模型（選其一）
# 選項 A：SmolLM2-360M-Instruct（最輕量）
# 選項 B：Qwen2.5-0.5B-Instruct（中文能力佳）

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "HuggingFaceTB/SmolLM2-360M-Instruct",
    max_seq_length = 2048,
    load_in_4bit = True,  # 省記憶體
)

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,              # LoRA rank
    target_modules = ["q_proj", "v_proj"],
    lora_alpha = 16,
)

# SFT 訓練格式
def format_example(example):
    return f"""<|im_start|>user
{example['problem']}<|im_end|>
<|im_start|>assistant
<thinking>
{example['thinking']}
</thinking>

{example['solution']}<|im_end|>"""
```

**訓練資料擴充策略（你只有 2,326 筆，需要補充）：**
- `open-orca/OpenOrca`（開源，MIT）取 5,000 筆
- `gsm8k`（數學，開源）全部 ~8,000 筆
- `meta-math/MetaMathQA`（數學變體）取 5,000 筆
- 最終混合：~20,000 筆

---

### Phase 3：量化與部署包（第 9-12 週）

**GGUF 量化（給 llama.cpp / LM Studio / Ollama）：**
```bash
python llama.cpp/convert_hf_to_gguf.py \
  ./your-model-hf \
  --outtype q4_k_m \
  --outfile edge-reasoning-360M-Q4_K_M.gguf
```

**提供的部署腳本（這是爆 Star 的關鍵！）：**
```bash
# 一行在樹莓派 4 上部署
curl -sSL https://raw.githubusercontent.com/YOUR/REPO/main/install.sh | bash

# 然後直接問問題
./edge-llm "請解釋什麼是量子糾纏，用國中生能懂的語言"
```

---

## 📈 HuggingFace 百萬下載量路線圖

### 現實校準（毒蛇版）

HuggingFace 的「likes」頂尖模型：
- Llama 3（Meta）：~10,000 likes
- Phi-3 Mini：~2,000 likes
- SmolLM2：~800 likes
- 個人開發者好模型：100-500 likes

**百萬下載量（Downloads）vs 百萬 Likes 是不同的事！**
- Likes = 主動按讚，難的要死
- Downloads = 被動下載，容易多了
- BERT-base 有 60M+ 下載 / 月，是因為它是管道中間件

**現實的百萬下載量策略：**
做出一個「必要組件」，讓人不得不下載。
例如：如果你的模型被整合進 Home Assistant / ESPHome 的 AI 擴充，每次安裝就是一次下載。

---

## 🚀 爆 Star/Like 的關鍵動作

### HuggingFace 上的成功模式

1. **Demo Space（必做）**：在 HuggingFace Spaces 做一個互動 Demo，讓人不用安裝就能玩
2. **Benchmark 說話**：在 Model Card 列出你的模型 vs 同量級模型的性能比較
3. **一張圖說清楚**：做一張漂亮的比較圖，效果/大小/速度三角形
4. **部署腳本完整**：樹莓派、Docker、Ollama 一鍵安裝

### 推廣（你說只放 Reddit）

```
投稿目標：
- r/LocalLLaMA（主戰場，50萬訂閱者）
- r/MachineLearning
- r/raspberry_pi（如果你有樹莓派 Demo）
- r/esp32（如果你有 ESP32 整合）

標題公式：
"I fine-tuned a 360M model with chain-of-thought reasoning 
that runs on Raspberry Pi 4 with 2GB RAM - here's my approach"

關鍵：要有 Demo GIF / 截圖，光說不練是零效果
```

---

## ⚠️ 已知風險與限制

| 風險 | 評估 | 應對 |
|------|------|------|
| 資料集太小（2,326 筆）| 高 | 必須混合開源資料 |
| 無 GPU 訓練成本 | 中 | 用 Google Colab Pro ($10/月) 或 Lambda Labs |
| ESP32 上真正推理不可能 | 高 | 重新定義：API 調用 or 樹莓派主要目標 |
| 百萬 Likes 目標 | 非常高 | 現實期望：1,000-5,000 likes，百萬 downloads 是可能的 |
| 競爭激烈（SmolLM2、Phi） | 中 | 差異化：CoT 推理能力 + 邊緣設備支援 + 部署工具 |

---

## 📋 立即行動清單

### 本週必做（不做白玩）：
- [ ] 確認你有沒有 GPU（或打算用哪個雲端 GPU）
- [ ] 決定：ESP32 要做本地推理 還是 API 調用？這影響整個技術路線
- [ ] 清理資料集並準備發布 HuggingFace

### 未來 2 週：
- [ ] HuggingFace 帳號建立、Dataset 發布
- [ ] 選定基礎模型（SmolLM2-360M vs Qwen2.5-0.5B）
- [ ] 在 Colab 跑通訓練流程

### 未來 1-2 個月：
- [ ] 模型訓練完成，量化成 GGUF
- [ ] 在樹莓派 4 上實測，拍 Demo 影片
- [ ] 發布 Reddit 帖文

---

*文件位置：`docs/project_plan_v2.md`*  
*毒蛇 PM 要說的話：資料集是你真正的資產，先發出去，讓社群幫你驗證。*

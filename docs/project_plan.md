# 🐍 毒蛇 PM 裁決書：LLM 開源項目完整策略規劃

> **製作日期：** 2026-03-12  
> **版本：** v1.0  
> **負責人：** 毒蛇 PM（本 AI 助手）  
> **目標：** GitHub 3,000+ Stars，造福 LLM 開發者社群

---

## 📋 PM 前言（不聽者自負）

我在 LLM 生態系做了完整的盡職調查。現有工具要麼肥得像豬（LangChain），要麼貴得要命（閉源評估平台），要麼根本沒有人用（那些學術論文附帶的破工具）。

**你的機會窗口是現在。** 2025 年中以後這個賽道會更擁擠。

我給你三條路，按策略層次排列。你可以選，但別選錯。

---

## 🎯 市場缺口分析

### 現有工具的致命弱點

| 工具 | Stars | 致命問題 |
|------|-------|---------|
| LangChain | 95k+ | 過度抽象、breaking changes 頻繁、上手曲線陡 |
| DeepEval | 7k+ | UI 複雜、部分功能需付費、文件混亂 |
| PromptFoo | 5k+ | 配置繁瑣、專注 prompt testing 不夠全面 |
| LiteLLM | 15k+ | 只是個 proxy，沒有智能路由邏輯 |
| Guardrails AI | 4k+ | 太笨重、runtime overhead 大 |
| Instructor | 8k+ | 只解決結構化輸出，範圍太窄 |

### 開發者真實痛點（2025）

1. **評估地獄**：做完 LLM 應用不知道它「夠不夠好」，線上用戶才是第一個 QA
2. **成本盲點**：每個月看到 API 帳單才知道哪條 prompt 在燒錢
3. **幻覺無法量化**：知道模型會幻覺，但搞不清楚發生率有多高
4. **多模型混用複雜**：要換個 provider 就要改一堆代碼
5. **缺乏可重複的測試**：每次改 prompt 都靠「感覺」，工程師最恨這個

---

## 🏗️ 三層次項目策略

### 第一層（立即啟動，4-6 週，目標 1,000 Stars）

#### 項目 A：`llm-unittest` — 給 LLM 應用寫單元測試

**核心概念：** 你已經懂得寫 pytest，現在只是在測試 LLM 的輸出。

```python
# 就是這麼簡單
from llm_unittest import assert_llm

def test_my_chatbot():
    response = my_chatbot("什麼是量子糾纏？")
    
    assert_llm(response).should(
        be_factual=True,          # 自動幻覺檢測
        contain_keywords=["量子", "糾纏", "粒子"],
        not_contain=["我不知道"],
        max_tokens=500,
        language="zh-TW"          # 語言一致性檢查
    )
```

**技術棧：**
- Python（核心庫）
- 可選 OpenAI / Anthropic / 本地 Ollama 作為評估器
- JSON 報告 + HTML 視覺化
- `pip install llm-unittest`

**MVP 範疇（3 週）：**
- [ ] 核心 `assert_llm()` API
- [ ] 5 種基本評估器（factual/relevance/toxicity/format/language）
- [ ] pytest 插件整合
- [ ] 好看的 HTML 報告
- [ ] README 要有 GIF 演示

---

### 第二層（主力項目，3-6 個月，目標 5,000 Stars）

#### 項目 B：`llm-eval` — 完整 LLM 應用評估框架

**一句話定位：** "The pytest for LLM applications"

**核心功能架構：**

```
llm-eval/
├── evaluators/
│   ├── hallucination/     # 幻覺檢測（基於 RAGAS）
│   ├── relevance/         # 相關性評分
│   ├── coherence/         # 邏輯連貫性
│   ├── toxicity/          # 毒性內容過濾
│   ├── cost/              # Token 成本追蹤
│   └── latency/           # 延遲監控
├── suites/
│   ├── rag/               # RAG pipeline 評估套件
│   ├── agent/             # Agent 行為評估
│   └── chatbot/           # 對話品質評估
├── reports/
│   ├── html/              # 漂亮的 HTML 報告
│   ├── json/              # CI/CD 友好的 JSON
│   └── slack/             # Slack 通知
└── cli/                   # llm-eval run --suite rag
```

**殺手級功能：**

1. **自動黃金集生成**
   ```bash
   llm-eval generate-testset --input docs/ --size 50
   # 自動從你的文件生成 50 個測試案例
   ```

2. **回歸測試**
   ```bash
   llm-eval run --compare baseline.json
   # 自動標出哪些指標變差了
   ```

3. **成本計算器**
   ```python
   with llm_eval.cost_tracker(budget=10.0) as tracker:
       pipeline.run(test_cases)
   # 超出預算自動停止並報告
   ```

4. **多模型比較**
   ```bash
   llm-eval compare --models gpt-4o,claude-3-5,llama3.1
   # 一鍵比較三個模型在你的用例上的表現
   ```

**差異化核心：**
- 不依賴任何特定 LLM 框架（不像 LangChain 的 evaluation）
- 本地運行，不上傳你的數據（隱私優先）
- 5 分鐘能跑出第一份報告
- 報告可以一鍵分享（開發者最愛炫耀數字）

**技術棧：**
- Python 3.10+（核心）
- Rich / Textual（CLI 美化）
- Jinja2（報告模板）
- 可選 Web UI（Next.js / Vue）

---

### 第三層（生態擴展，6-12 個月，目標 10,000+ Stars）

#### 項目 C：`llm-hub` — 社群 LLM 評估基準平台

**概念：** 每個人都可以上傳自己的評估結果，形成社群排行榜。

```
llm-eval submit --suite rag --model gpt-4o
# 上傳到 llm-hub.io，貢獻社群基準
```

- 公開的 LLM 應用評估排行榜
- 按任務類型（RAG/chatbot/code/math）分類
- 成為 LLM 界的 MLPerf（但更接地氣）

---

## 🗓️ 執行 Roadmap

### Phase 0：準備期（第 1-2 週）

```
Week 1:
├── 確定你要做的是 A（llm-unittest）還是 B（llm-eval）
├── 建立 GitHub repo 並寫好 README（甚至 README first）
├── 在 Twitter/X、Reddit、HN 預告
└── 找 5 個 beta 測試者（LLM 開發者朋友）

Week 2:
├── 核心 API 設計定稿（改 API 是最貴的成本）
├── 寫 CONTRIBUTING.md 和 CODE_OF_CONDUCT.md
└── 設定 CI/CD（GitHub Actions）
```

### Phase 1：MVP（第 3-8 週）

```
Week 3-5: 核心功能實作
- 核心評估 API
- 至少 3 種評估器
- CLI 基礎功能
- 完整測試覆蓋（80%+）

Week 6-7: 文件與 DX
- 清楚的 QuickStart（< 5 分鐘有結果）
- 3 個 end-to-end 教學
- API 文件（自動生成）
- GIF 演示

Week 8: 第一次公開發布
- 發 0.1.0 release
- 寫 Blog Post（英文）
- 投稿 Reddit r/MachineLearning + r/LocalLLaMA
- 投稿 Hacker News Show HN
```

### Phase 2：成長期（第 9-16 週）

```
每兩週一次 release：
- 根據社群反饋排優先級
- v0.2: 更多評估器
- v0.3: Web UI（若有人要求）
- v0.4: CI/CD 整合（GitHub Actions plugin）
- v0.5: 自動測試集生成
```

### Phase 3：生態期（第 17-24 週）

```
- 支援 LangChain / LlamaIndex / Haystack
- 支援 TypeScript SDK
- 辦 Discord 社群
- 找合作夥伴（Langfuse / vLLM 社群）
- 申請 OSS GCP/AWS Credits
```

---

## 📈 獲取 Star 的增長引擎

### 初期引爆（0 → 500 Stars）

1. **Show HN 帖文** — 標題要有數字："I built a pytest-style testing framework for LLM apps (demo inside)"
2. **Reddit 策略** — 在 r/MachineLearning、r/LocalLLaMA、r/LangChain 發帖
3. **YouTube Demo** — 3 分鐘演示影片，展示"從 0 到看到評估報告"
4. **Twitter 連載** — 用 Thread 分享"為什麼我要做這個工具"的故事

### 成長期（500 → 3000 Stars）

5. **寫教學文章** — Dev.to / Medium / 個人 Blog（中英雙語）
6. **整合其他工具** — 在 LangChain issue 回覆中提到，在 Discord 中分享
7. **Conference Talk** — 投稿 AI conference（PyCon、AI Summit）
8. **Influencer 合作** — 聯繫 YouTube 上做 LLM 教學的人

### 爆發期（3000+ Stars）

9. **案例研究** — 找真實用戶，發表"我用 llm-eval 發現 X Bug 的故事"
10. **Newsletter** — 投稿 TLDR AI、The Batch、AI Breakfast 等

---

## ⚙️ 技術架構建議

### 核心原則

1. **零依賴核心**：核心功能只依賴 Python 標準庫 + 一兩個穩定的包
2. **插件架構**：LLM 提供商、評估器、報告格式都是可插拔的
3. **非同步優先**：現代 LLM 應用都是 async，評估框架也要支援

### 推薦技術選型

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.10"
httpx = "^0.27"           # HTTP 客戶端
pydantic = "^2.0"         # 資料驗證
rich = "^13.0"            # 終端美化
jinja2 = "^3.0"           # 報告模板
typer = "^0.12"           # CLI 框架

[tool.poetry.extras]
openai = ["openai"]
anthropic = ["anthropic"]
langchain = ["langchain"]
```

### 代碼品質標準（非談判項目）

- **測試覆蓋率 ≥ 80%**（強制）
- **型別提示 100%**（mypy strict）
- **文件字串 100%**（所有 public API）
- **Ruff linting + Black formatting**
- **每個 PR 必須有測試**

---

## 💰 資源估計與風險

### 時間投入估計

| 階段 | 每週投入時間 | 持續時間 |
|------|------------|---------|
| Phase 0（準備） | 5-10 hrs/週 | 2 週 |
| Phase 1（MVP） | 15-20 hrs/週 | 6 週 |
| Phase 2（成長） | 10-15 hrs/週 | 8 週 |
| Phase 3（生態） | 按狀況調整 | 持續 |

### API 成本估計（評估本身需要 LLM）

- 測試期：$20-50/月（使用 Ollama 本地模型可以降到 $0）
- 文件生成評估：可免費使用 OpenRouter 的免費模型

### 主要風險與應對

| 風險 | 可能性 | 應對策略 |
|------|--------|---------|
| 大公司做同樣的事 | 中 | 先發優勢 + 社群護城河 |
| API 費用過高 | 低 | 支援本地模型（Ollama）作為評估器 |
| 沒時間維護 | 高 | 從第一天開始建立貢獻者文化 |
| Star 增長停滯 | 中 | 持續輸出內容 + 找合作 |

---

## ✅ 里程碑與驗收標準

### 3 個月目標
- [ ] 0.5.0 版本穩定發布
- [ ] GitHub Stars ≥ 1,000
- [ ] README 有 ≥ 5 個社群貢獻的評估器
- [ ] ≥ 3 篇外部媒體/Blog 引用

### 6 個月目標
- [ ] 1.0.0 穩定版本
- [ ] GitHub Stars ≥ 3,000
- [ ] ≥ 10 個企業/個人在生產環境使用
- [ ] PyPI 月下載量 ≥ 5,000

### 12 個月目標
- [ ] GitHub Stars ≥ 10,000
- [ ] 活躍維護者 ≥ 3 人
- [ ] 社群 Discord ≥ 500 成員
- [ ] 申請到 OSS 贊助或 cloud credits

---

## 🔑 毒蛇 PM 最後忠告

1. **README 是你最重要的代碼**。第一印象決定 80% 的 Star。花 20% 的時間在 README 上。

2. **先做 Demo，再做功能**。你的 GitHub 首頁要有一個讓人看了就想 Star 的 GIF。沒有 GIF 等於沒有臉。

3. **發布第一個 0.1.0 後立刻找 5 個人用**，不要等到"完美"。沒有人用的完美工具是廢物。

4. **英文文件是必須的**。想要幾千 Star 就必須走向全球開發者社群。中文文件可以有，但英文必須是主力。

5. **Response time ≤ 24 小時**。Issue 收到要在 24 小時內回覆，哪怕只是說"Thanks, I'll look into this."。社群冷掉了就很難再暖。

6. **版本要穩定**。寧願慢一點發布，也不要因為 breaking changes 讓早期採用者離開。

7. **度量一切**。從第一天就加 `star-history`、`pypi-stats`、`packagephobia`。沒有數據你不知道哪個發帖帶來最多 Star。

---

## 📁 文件索引

本文件存於：`docs/project_plan.md`

後續文件將包含：
- `docs/architecture.md` — 詳細技術架構設計
- `docs/api_design.md` — 核心 API 設計稿（改 API 比改代碼貴）
- `docs/marketing.md` — 社群推廣詳細計畫
- `docs/weekly_log.md` — 週記錄（PM 要求）

---

*「好工具不需要說服，用過的人自會傳播。你的任務是讓第一個用的人立刻感受到價值。」*  
*— 毒蛇 PM*

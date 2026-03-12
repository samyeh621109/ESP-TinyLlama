# MCU LLM 未解難題快速參考

## 六大研究問題（2025 現況）

| # | 問題 | 類型 | 難度 | 適合度 |
|---|------|------|------|--------|
| 1 | 詞彙表瓶頸（Vocabulary Bottleneck） | 研究 | 中 | ★★★ |
| 2 | **Xtensa LX7 Bitwise 推理 Kernel** | 工程 | 中高 | ★★★★★ |
| 3 | Flash 分層權重儲存架構 | 研究+工程 | 高 | ★★★★ |
| 4 | Minimum Viable Coherence 下界 | 實驗研究 | 低 | ★★★★ |
| 5 | 極小 SSM 的 Long-Range Coherence | 研究 | 高 | ★★★ |
| 6 | On-Device Continual Learning | 研究 | 極高 | ★★ |

## 推薦組合（C++ 背景 + 工程導向）

**問題二（Bitwise Kernel）+ 問題四（Coherence 下界實驗）**

路徑：
1. 實驗確認 1M/2M/5M/10M 模型的 coherence 邊界
2. 設計針對 Xtensa LX7 的 ternary/bitwise inference kernel
3. 在 ESP32-S3 上 benchmark
4. 發布 GitHub + ArXiv

*文件：`docs/research_problems.md`*

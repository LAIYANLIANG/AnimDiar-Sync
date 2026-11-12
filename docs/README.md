# 📚 專案完整技術文檔索引 (Documentation Index)

本目錄包含「Instagram 短影音多人對話轉文字、說話者分離與繁中情緒分析引擎」的完整工程記錄與部署指南：

- 📖 [01_DEPLOYMENT_GUIDE.md](01_DEPLOYMENT_GUIDE.md)：**系統部署與環境安裝指南**（含 Homebrew、Python 3.11 虛擬環境、各套件精準版本、Ollama 模型配置與 Token 申請指引）。
- 🏗️ [02_ARCHITECTURE_AND_MODELS.md](02_ARCHITECTURE_AND_MODELS.md)：**系統架構與模型技術規格**（含端到端處理流程圖、Pyannote 3.1、Faster-Whisper、Taiwan-LLM TAIDE 8B 選型分析與記憶體配置）。
- 🔍 [03_TROUBLESHOOTING_AND_SOLUTIONS.md](03_TROUBLESHOOTING_AND_SOLUTIONS.md)：**實戰問題記錄與排除手冊**（記錄今日遭遇之 Hugging Face 棄用密碼、Pyannote 4.0 403 錯誤、PyTorch 2.13 介面變更、Hub 參數相容性等問題之根本原因與對應解法）。
- 🚀 [04_EXECUTION_AND_CLI_MANUAL.md](04_EXECUTION_AND_CLI_MANUAL.md)：**日常執行與指令使用手冊**（含一鍵 URL 下載分析、本地檔案轉錄、參數說明與產出格式對照）。

---

### 📌 快速執行備忘錄
```bash
cd .
source .venv/bin/activate
export HF_TOKEN="your_huggingface_token_here"

# 執行分析
python main.py --url "https://www.instagram.com/reel/DcDSDo1P14j/" --output-dir ./output
```

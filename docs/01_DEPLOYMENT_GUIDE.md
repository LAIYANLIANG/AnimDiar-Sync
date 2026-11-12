# 🛠️ 系統部署與環境安裝指南 (Deployment & Setup Guide)

- **建置記錄時間**: 2026 年 08 月 16 日 17:53
- **驗證硬體環境**: Apple MacBook Pro (Apple M5 晶片, 24GB Unified Memory, 1TB SSD, macOS arm64)
- **專案路徑**: `.`

本文件旨在提供給任何開發者或團隊成員，按照本步驟即可在全新的 macOS 環境中建立 100% 相同功能之「短影音多人語音分離、逐字轉錄與繁中情緒分析系統」。

---

## 1. 系統底層依賴安裝 (System Dependencies)

透過 Homebrew 安裝音訊處理核心工具與 Python 3.11 執行環境：

```bash
# 1. 安裝 Homebrew (若尚未安裝)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝音訊核心轉換工具 FFmpeg (9.0.1+)
brew install ffmpeg

# 3. 安裝 Python 3.11 (避免使用過新 3.13 導致 PyTorch/Torchaudio 編譯相容問題)
brew install python@3.11

# 4. 安裝本地 LLM 運行器 Ollama
brew install ollama
```

---

## 2. 專案目錄與 Python 虛擬環境建立

為隔離套件依賴，建立專屬 Python 3.11 虛擬環境：

```bash
# 建立工作目錄
mkdir -p ~/ig_transcriber && cd ~/ig_transcriber

# 建立 Python 3.11 虛擬環境
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv .venv

# 啟用虛擬環境
source .venv/bin/activate

# 升級 pip
pip install --upgrade pip setuptools wheel
```

---

## 3. Python 核心 AI 套件清單與精準版本

經過實機相容性驗證，請務必按照以下相容版本安裝（避免使用 PyTorch 2.13 或 Pyannote 4.0 造成套件衝突）：

```bash
# 啟用虛擬環境
source .venv/bin/activate

# 1. 安裝 PyTorch 穩定版 (支援 Apple Silicon MPS 加速)
pip install "torch==2.5.1" "torchaudio==2.5.1" "sympy==1.13.1"

# 2. 安裝相容版 Hugging Face Hub (相容 pyannote 3.3 認證介面)
pip install "huggingface_hub<0.24.0"

# 3. 安裝語音轉文字核心 (Faster-Whisper)
pip install "faster-whisper==1.2.1"

# 4. 安裝說話者分離核心 (Pyannote.audio 3.3.2)
pip install "pyannote.audio==3.3.2"

# 5. 安裝影片下載、LLM 客戶端與輔助函式庫
pip install "yt-dlp>=2026.0.0" "ollama>=0.6.0" "soundfile" "pydantic"
```

---

## 4. 本地端大型語言模型 (Taiwan-LLM) 安裝

本系統採用台灣正體中文微調模型 **Llama3-TAIDE-8B**，記憶體佔用約 5.7GB，能在 24GB RAM 的 M5 晶片上高速運算且留有充足記憶體供多模態處理：

```bash
# 1. 啟動 Ollama 背景服務 (若尚未啟動)
ollama serve &

# 2. 拉取台灣繁體中文 TAIDE 8B 模型
ollama pull cwchang/llama3-taide-lx-8b-chat-alpha1
```

---

## 5. 授權與權限配置清單

| 項目 | 來源 | 是否需要 Token / 登入 | 權限需求 | 申請/取得方式 |
| :--- | :--- | :--- | :--- | :--- |
| **FFmpeg** | Homebrew | ❌ 否 | 本機檔案讀寫 | 直接安裝 |
| **yt-dlp** | PyPI | ❌ 否 | 公開網路讀取 | 直接安裝 |
| **Faster-Whisper** | Systran | ❌ 否 (公開模型) | 本機檔案讀寫 | 自動下載模型快取 |
| **Taiwan-LLM (TAIDE)** | Ollama | ❌ 否 (開源權重) | 本機連接埠 `11434` | `ollama pull` 直接拉取 |
| **Pyannote.audio** | Hugging Face | ✅ **是** (需要 HF Token) | `Read` 權限 | 需至 Hugging Face 接受條款 |

### 🔑 Hugging Face Token 配置步驟：
1. 註冊並登入 [Hugging Face](https://huggingface.co/)。
2. 前往 [Hugging Face Access Tokens](https://huggingface.co/settings/tokens)，建立一把 **Read** 權限的 Token（格式為 `hf_...`）。
3. 在瀏覽器點選以下兩個模型頁面，點擊 **「Agree and access repository」** 接受授權條款：
   - 👉 [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - 👉 [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
4. 將 Token 設定為環境變數或於執行時帶入參數：
   ```bash
   export HF_TOKEN="hf_你的Token字串"
   ```

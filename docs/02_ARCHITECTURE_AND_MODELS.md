# 🏗️ 系統架構與模型技術規格 (Architecture & Models)

- **文件建立時間**: 2026 年 08 月 16 日 17:53
- **系統定位**: 離線優先 (Offline-first)、高隱私、高準確度之短影音多人聲對話轉錄與繁中情緒分析引擎

---

## 1. 端到端處理架構 (Pipeline Flowchart)

```mermaid
flowchart TD
    A[Instagram 短影音 URL / 本地 MP4 影片] -->|yt-dlp 下載| B(原始 MP4 視訊檔案)
    B -->|FFmpeg 轉換 (16kHz 16-bit Mono)| C(標準 WAV 音訊檔)
    
    subgraph 音訊核心處理層 (Audio AI Layer)
        C -->|Pyannote.audio 3.1| D[說話者特徵提取與分群 Diarization]
        C -->|Faster-Whisper medium| E[語音逐字轉錄 Transcription]
        D -->|時間戳交集率 Overlap Match| F[說話者 - 台詞精準對齊]
        E --> F
    end

    subgraph 繁中語意與情緒分析層 (LLM Intelligence Layer)
        F -->|Ollama 本地 API| G[Llama3-TAIDE-8B 台灣繁中模型]
        G -->|情境與心理建模| H[角色畫像、語氣標籤、繁中潤飾]
    end

    subgraph 成果匯出 (Output Formats)
        H --> I[Markdown 完整排版報表]
        H --> J[標準 JSON 結構化資料]
    end
```

---

## 2. 核心 AI 模型選型與技術參數

### ① 說話者分離 (Speaker Diarization)：`pyannote/speaker-diarization-3.1`
- **模型來源**: Hugging Face (需 Read Token 認證)
- **子模型架構**:
  - `pyannote/segmentation-3.0`: 進行多說話者語音端點偵測與重疊發話切分。
  - `pyannote/wespeaker-voxceleb-resnet34-LM`: 聲紋特徵嵌入向量提取 (Embedding)。
- **運算方式**: PyTorch (CPU 全核心平行運算 / MPS 加速)。
- **切分精度**: 毫秒級時間戳標註。

### ② 語音轉文字 (Speech-to-Text)：`faster-whisper (medium)`
- **底層引擎**: CTranslate2 (int8 量化加速)。
- **記憶體佔用**: 約 1.5GB RAM。
- **處理速度**: 在 Apple M5 晶片上，1 分 52 秒音訊轉錄僅需 **約 4.9 秒**（約 23 倍速即時處理）。
- **特色功能**: 內建 VAD (Voice Activity Detection) 靜音過濾，支援繁體中文初始提示詞 (`initial_prompt`) 引導輸出台灣慣用語。

### ③ 語意潤飾與情緒分析 (Local LLM)：`Llama3-TAIDE-8B`
- **模型標籤**: `cwchang/llama3-taide-lx-8b-chat-alpha1`
- **模型架構**: Meta Llama 3 8B 經台灣國科會 TAIDE 繁體中文語料深度微調。
- **記憶體佔用**: 約 5.7GB RAM。
- **優勢**:
  - 徹底避免簡體中文詞彙（如「視頻」、「膠水」）。
  - 對台灣口語、隱喻情話（如「少放油」、「金句都記下來」）具備極高的文化語境同理能力。
  - 24GB RAM 運算環境下，運行 8B 模型時仍可保留 16GB+ 充足記憶體供後續影片渲染或多模態擴充。

---

## 3. 模組程式碼結構說明

```
ig_transcriber/
├── downloader.py                  # 模組 1: 負責 IG 影片下載與 FFmpeg 轉音訊
├── diarization_transcription.py   # 模組 2: Pyannote + Faster-Whisper + 時間戳對齊
├── emotion_analyzer.py            # 模組 3: Ollama TAIDE 8B 繁中情緒語氣分析
├── main.py                        # 主控制台: CLI 命令列端到端排程執行器
├── render_report.py               # 報表產生器: 輸出豐富 Markdown 與 JSON
├── docs/                          # 完整系統部署、排錯與架構文件庫
│   ├── 01_DEPLOYMENT_GUIDE.md
│   ├── 02_ARCHITECTURE_AND_MODELS.md
│   ├── 03_TROUBLESHOOTING_AND_SOLUTIONS.md
│   ├── 04_EXECUTION_AND_CLI_MANUAL.md
│   └── README.md
└── output/                        # 成果輸出目錄 (JSON, MD, WAV, MP4)
```

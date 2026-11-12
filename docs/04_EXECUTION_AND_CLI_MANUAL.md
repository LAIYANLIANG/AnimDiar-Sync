# 🚀 日常執行與指令使用手冊 (Execution & CLI Manual)

- **記錄時間**: 2026 年 08 月 16 日 17:53
- **主程式路徑**: `./main.py`

---

## 1. 快速開始 (Quick Start)

### 步驟 1：進入專案目錄並啟用虛擬環境
```bash
cd .
source .venv/bin/activate
```

### 步驟 2：設定 Hugging Face Token（可加至 `~/.zshrc` 長期生效）
```bash
export HF_TOKEN="your_huggingface_token_here"
```

### 步驟 3：確保本地 Ollama 服務執行中
```bash
# 檢查 Ollama 是否正在運作
ollama list
```

---

## 2. 核心指令範例 (Usage Examples)

### ① 從 Instagram 網址直接全自動處理
```bash
python main.py \
  --url "https://www.instagram.com/reel/DcDSDo1P14j/" \
  --output-dir ./output
```

### ② 針對已下載之本地影片 (.mp4) 或音訊 (.wav)
```bash
python main.py \
  --input "./downloads/DcDSDo1P14j.mp4" \
  --output-dir ./output
```

### ③ 指定更高階的 Whisper 模型 (如 `large-v3`)
```bash
python main.py \
  --input "./downloads/DcDSDo1P14j.mp4" \
  --whisper-model "large-v3" \
  --output-dir ./output
```

---

## 3. 命令列參數完整說明表 (CLI Arguments)

| 參數選項 | 類型 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `--url` | 字串 | `None` | Instagram 短影音 Reel 網址 |
| `--input` | 字串 | `None` | 本地影音檔案路徑 (`.mp4`, `.mov`, `.wav`, `.mp3`) |
| `--hf-token` | 字串 | `$HF_TOKEN` | Hugging Face Access Token |
| `--whisper-model` | 字串 | `medium` | Whisper 辨識模型大小 (`base`, `small`, `medium`, `large-v3`) |
| `--llm-model` | 字串 | `cwchang/llama3-taide-lx-8b-chat-alpha1` | 本地 Ollama 繁中模型名稱 |
| `--output-dir` | 字串 | `./output` | 報表與音訊產出資料夾 |

---

## 4. 輸出檔案清單與用途

每次執行後，指定的輸出資料夾（如 `./output/`）將自動產生以下成果：

1. **`dialogue_analysis_report.md`**：
   - 適合人類閱讀的 Markdown 格式報告。
   - 包含對話情境脈絡、角色性格分析、以及逐句附帶時間戳、說話者、正體中文台詞、情緒標籤與語氣描述之完整表格。
2. **`dialogue_analysis.json`**：
   - 適合後續程式介接、資料庫儲存或前端播放器串接之標準 JSON 格式。
3. **`extracted_audio_16k.wav`**：
   - 由原片提取出之 16kHz 16-bit 單聲道高音質標準音訊檔。

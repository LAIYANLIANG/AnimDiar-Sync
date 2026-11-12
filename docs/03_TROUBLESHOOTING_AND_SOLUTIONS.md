# 🔍 實戰問題記錄與排除手冊 (Troubleshooting & Solutions)

- **記錄時間**: 2026 年 08 月 16 日 17:53
- **紀錄目的**: 彙整系統從 0 建置到完整上線過程中，遇到的所有依賴衝突、授權問題、API 變更與對應解法。

---

## ⚠️ 問題 1：Hugging Face CLI 終端機密碼登入被棄用

### 🔴 狀況描述
嘗試在終端機執行 `huggingface-cli login` 輸入帳號與密碼時，出現以下警告或錯誤：
```text
Warning: `huggingface-cli` is deprecated and no longer works. Use `hf` instead.
```
且 Hugging Face 自 2023 年底起全面停止支援密碼驗證（Password authentication is deprecated）。

### 🟢 解決方法
1. 前往 Hugging Face 官方後台建立專屬 Access Token：
   👉 [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. 權限選擇 **Read** 即可。
3. 在 Python 程式中透過 `huggingface_hub.login(token=...)` 或直接於呼叫模型時傳遞 `use_auth_token=token` 參數。

---

## ⚠️ 問題 2：Pyannote 4.0 強制依賴 Gated PLDA 社群模型 (403 Forbidden)

### 🔴 狀況描述
使用最新版 `pyannote.audio 4.0.7` 時，即使已接受 `speaker-diarization-3.1` 授權，仍報錯：
```text
Cannot access gated repo for url https://huggingface.co/pyannote/speaker-diarization-community-1/resolve/main/plda/xvec_transform.npz.
Access to model pyannote/speaker-diarization-community-1 is restricted and you are not in the authorized list.
```

### 🔍 原因分析
Pyannote 4.0 新增了 PLDA 模組並拆分至獨立的 `speaker-diarization-community-1` 倉庫，需要額外進行二次申請授權。

### 🟢 解決方法
鎖定安裝成熟穩定的 **`pyannote.audio==3.3.2`**：
```bash
pip install "pyannote.audio==3.3.2"
```
此版本直接使用 `pyannote/speaker-diarization-3.1` + `pyannote/segmentation-3.0` + `pyannote/wespeaker-voxceleb-resnet34-LM`，無需額外的 PLDA gated 存取。

---

## ⚠️ 問題 3：PyTorch 2.13 (Pre-release) 與 Torchaudio 函式庫衝突

### 🔴 狀況描述
在安裝預設最新版 PyTorch 時，執行 Pyannote 出現：
```text
AttributeError: module 'torchaudio' has no attribute 'AudioMetaData'
AttributeError: module 'torchaudio' has no attribute 'list_audio_backends'
```

### 🔍 原因分析
Python 3.11 環境若拉取到 PyTorch 2.13 / Torchaudio 2.11 的 Nightly/未來預發行版，該版本重構了音訊後端介面，移除了舊有的 `list_audio_backends`。

### 🟢 解決方法
降版並鎖定為官方正式發佈的穩定版 **PyTorch 2.5.1 + Torchaudio 2.5.1**：
```bash
pip install "torch==2.5.1" "torchaudio==2.5.1" "sympy==1.13.1"
```

---

## ⚠️ 問題 4：Huggingface_hub 1.x 參數更名 (`use_auth_token` vs `token`)

### 🔴 狀況描述
執行 `Pipeline.from_pretrained(..., use_auth_token=token)` 時出現：
```text
TypeError: hf_hub_download() got an unexpected keyword argument 'use_auth_token'
```

### 🔍 原因分析
`huggingface_hub >= 0.24.0` 廢棄了舊版 `use_auth_token` 參數改名為 `token`，導致依賴舊版呼叫方式的 pyannote 3.3 出現引數不匹配。

### 🟢 解決方法
鎖定 `huggingface_hub<0.24.0`（如 `0.23.5`），並在程式碼中加入兼顧 `use_auth_token` 與 `token` 的 try-except 容錯機制：
```python
try:
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
except TypeError:
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=token)
```

---

## ⚠️ 問題 5：LLM 輸出非純 JSON 導致解析中斷

### 🔴 狀況描述
呼叫本地 LLM (TAIDE 8B) 時，模型偶爾會在 JSON 前後附帶禮貌性解說（如「由於你提供的對話內容...」），造成 `json.loads()` 直接報錯。

### 🟢 解決方法
在 `emotion_analyzer.py` 中導入正則表達式自動擷取最大外層括號：
```python
import re
json_match = re.search(r'(\{[\s\S]*\})', content)
if json_match:
    parsed_result = json.loads(json_match.group(1))
```
同時內建**語意備用結構化對齊器**，即便 LLM 輸出不完整，也能 100% 確保 28 句台詞與時間戳完整輸出至最終報表。

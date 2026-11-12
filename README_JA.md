# 🎙️ AnimDiar-Sync: ショート動画複数話者分離・文字起こし＆感情分析エンジン

<p align="center">
  <a href="README.md">繁體中文</a> |
  <a href="README_EN.md">English</a> |
  <b><a href="README_JA.md">日本語</a></b> |
  <a href="README_KO.md">한국어</a>
</p>

<p align="center">
  <a href="https://github.com/LAIYANLIANG/AnimDiar-Sync"><img src="https://img.shields.io/badge/GitHub-AnimDiar--Sync-181717?style=flat&logo=github" alt="GitHub Repo"></a>
  <img src="https://img.shields.io/badge/Platform-macOS%20Apple%20Silicon%20%7C%20Linux%20%7C%20CUDA-blue.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg" alt="Python">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
</p>

プライバシー完全保護型のローカル完結型動画・音声インテリジェンス処理パイプライン。Instagram リールやローカル動画から複数の話者の声紋を自動分離し、高精度な音声認識（**Faster-Whisper**）を実行、さらにローカル LLM（Ollama 上の **TAIDE 8B** 等）を用いて発話者ごとの心理プロファイル構築および文単位の感情・語気アノテーションを自動生成します。

---

## ⚡ 主な特徴と機能

1. **🛡️ 100% ローカル完結のプライバシー保護**：音声認識（Faster-Whisper）および感情分析（Ollama Local LLM）はすべてローカルハードウェア上で推論され、外部クラウド API へデータが送信されることは一切ありません。
2. **👥 高精度な話者分離（Diarization）**：`Pyannote.audio 3.1` を統合し、各話者の発話時間帯をミリ秒単位で正確にセグメンテーション。
3. **🇹🇼 ニュアンス・感情表現の精密解析**：台湾華語・繁体字に特化した `Llama3-TAIDE-8B` を活用し、文脈に潜む感情の機微やユーモア、口語的ニュアンスを深く理解。
4. **📊 2種類の構造化レポート出力**：見やすい Markdown 形式の分析レポート (`dialogue_analysis_report.md`) とプログラム連携に適した JSON データ (`dialogue_analysis.json`) を、二重 Git 保護された集中出力ディレクトリ (`output/`) へ自動出力。

---

## 🧩 システム設計とワークフロー (Architecture & Pipeline)

### 1. エンドツーエンド処理フロー (Pipeline Workflow)

本パイプラインは4つの処理フェーズで構成され、それぞれ独立した Python モジュールによって実行されます：

```mermaid
flowchart TD
    subgraph Stage1["1. 入力および前処理 (Input & Preprocessing)"]
        A1["Instagram リール URL"] --> B1["downloader.py<br/>(yt-dlp ストリーム抽出)"]
        A2["ローカル動画ファイル (*.mp4/*.wav)"] --> B2["FFmpeg 変換モジュール<br/>(16kHz モノラル PCM WAV 変換)"]
        B1 --> B2
    end

    subgraph Stage2["2. 音声推論コア (diarization_transcription.py)"]
        B2 --> C1["Pyannote.audio 3.1<br/>話者声紋クラスタリング＆区間分割<br/>(Speaker Diarization)"]
        B2 --> C2["Faster-Whisper<br/>高速多言語音声認識＆文字起こし<br/>(ASR Transcription)"]
        C1 --> D["時系列重複アライメントアルゴリズム<br/>(Temporal Overlap Mapping)"]
        C2 --> D
    end

    subgraph Stage3["3. 文脈理解＆感情分析 (emotion_analyzer.py)"]
        D --> E["Ollama ローカル LLM エンジン<br/>cwchang/llama3-taide-lx-8b"]
        E --> F1["登場人物の心理プロファイル生成 (Profiles)"]
        E --> F2["文単位のセリフ推敲＆感情・語気タグ (Emotions)"]
        E --> F3["会話コンテキスト全体の要約 (Summary)"]
    end

    subgraph Stage4["4. 集中出力管理 (main.py / render_report.py)"]
        F1 --> G["データ構造のパッケージング"]
        F2 --> G
        F3 --> G
        G --> H1["📄 dialogue_analysis_report.md<br/>(可視化 Markdown レポート)"]
        G --> H2["📦 dialogue_analysis.json<br/>(構造化 JSON データセット)"]
        H1 --> I["📁 output/ 出力ディレクトリ<br/>(二重 .gitignore セキュリティ保護)"]
        H2 --> I
    end
```

### 2. プログラム構造とモジュール構成 (Codebase Architecture)

```mermaid
graph LR
    subgraph UI_CLI["制御＆実行レイヤー"]
        SHELL["start_project.sh<br/>環境自己診断＆ワンクリック起動"]
        MAIN["main.py<br/>中央パイプライン制御 CLI"]
    end

    subgraph CoreServices["推論＆処理コアレイヤー"]
        DL["downloader.py<br/>動画取得＆ストリーミング解析"]
        DT["diarization_transcription.py<br/>話者分離＆音声認識アライメント"]
        EA["emotion_analyzer.py<br/>TAIDE-8B 感情・語気分析"]
        RR["render_report.py<br/>Markdown & JSON レポート出力"]
    end

    subgraph Security["環境＆セキュリティ設定レイヤー"]
        ENV[".env / .env.example<br/>認証トークン＆エンドポイント設定"]
        GIT[".gitignore & output/.gitignore<br/>二重情報漏洩防止ルール"]
        REQ["requirements.txt<br/>厳密バージョン管理された依存関係"]
    end

    SHELL --> MAIN
    MAIN --> DL
    MAIN --> DT
    MAIN --> EA
    MAIN --> RR
    ENV -.-> MAIN
    GIT -.-> CoreServices
```

### 3. モジュール機能対応表

| モジュール名 | コア技術 / モデル | 役割と主な機能 | 主な出力 |
| :--- | :--- | :--- | :--- |
| **`main.py`** | `argparse` / Pipeline Controller | CLI コントローラー。ダウンロード、話者分離、文字起こし、感情分析、レポート生成の全工程を統括。 | コンソール進捗ログ、処理の実行トリガー |
| **`downloader.py`** | `yt-dlp` | Instagram リール等の SNS から高画質な動画・音声を自動抽出・ダウンロード。 | `output/downloads/*.mp4` |
| **`diarization_transcription.py`** | `Pyannote.audio 3.1`<br>`Faster-Whisper` | 16kHz リサンプリング、話者声紋クラスタリング、高速文字起こし、タイムスタンプのアライメント。 | 話者タグ付きセリフリスト |
| **`emotion_analyzer.py`** | `Ollama`<br>`Llama3-TAIDE-8B` | 会話全体の文脈把握、話者心理プロファイル作成、各セリフの感情・語気アノテーション。 | 感情分析 JSON データ構造 |
| **`render_report.py`** | Python IO / Markdown Engine | 分析データを整形し、見やすい Markdown 文書およびシステム連携用 JSON へ出力。 | `dialogue_analysis_report.md`<br>`dialogue_analysis.json` |
| **`start_project.sh`** | Bash Script | ワンクリック起動スクリプト。`.env` 読み込み、Ollama サービス状態確認、`.venv` 有効化を自動実行。 | 対話型作業シェル環境 |

---

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/LAIYANLIANG/AnimDiar-Sync.git
cd AnimDiar-Sync
```

### 2. 環境設定

```bash
# 環境設定テンプレートをコピー
cp .env.example .env

# Python 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. Hugging Face トークンの設定

`Pyannote.audio 3.1` は利用許諾が必要なコミュニティモデルです：
1. [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) および [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) にアクセスし利用規約に同意してください。
2. [Hugging Face Access Tokens](https://huggingface.co/settings/tokens) で `Read` 権限のトークンを作成します。
3. `.env` ファイルに設定します：
   ```env
   HF_TOKEN=your_huggingface_token_here
   ```
   または環境変数で指定：
   ```bash
   export HF_TOKEN="your_huggingface_token_here"
   ```

### 4. 分析の実行

```bash
# 方法 A: Instagram リールの URL を直接指定
python main.py --url "https://www.instagram.com/reel/YOUR_REEL_ID/" --output-dir ./output

# 方法 B: ローカルの動画ファイルを指定
python main.py --video-path "./path/to/video.mp4" --output-dir ./output
```

すべての解析結果（抽出音声 WAV、タイムスタンプ付き対話 JSON、Markdown レポート）は `./output/` に出力されます。

---

## 📚 ドキュメント

詳細な技術解説・トラブルシューティングは [`docs/`](docs/) に保管されています：

- 📖 [01_DEPLOYMENT_GUIDE.md](docs/01_DEPLOYMENT_GUIDE.md)：**システム構築と環境セットアップ手順**
- 🏗️ [02_ARCHITECTURE_AND_MODELS.md](docs/02_ARCHITECTURE_AND_MODELS.md)：**アーキテクチャ設計とモデル技術仕様**
- 🔍 [03_TROUBLESHOOTING_AND_SOLUTIONS.md](docs/03_TROUBLESHOOTING_AND_SOLUTIONS.md)：**障害対応とトラブルシューティング事例**
- 🚀 [04_EXECUTION_AND_CLI_MANUAL.md](docs/04_EXECUTION_AND_CLI_MANUAL.md)：**CLI 操作マニュアルとコマンドリファレンス**

---

## ⚖️ 免責事項と AI 倫理声明

本プロジェクトは AI 倫理およびオープンソースコンプライアンスを厳格に遵守します。詳細は [DISCLAIMER.md](DISCLAIMER.md) をご確認ください。
- 本ツールは学術研究および正規許諾を得たメディア分析のみを目的としています。
- プラットフォーム利用規約を遵守し、本人の同意のない不法な盗聴や音響監視用途への利用を固く禁止します。

---

## 📄 ライセンス

本プロジェクトは [MIT License](LICENSE) のもとで公開されています。
Copyright (c) 2026 [LAIYANLIANG](https://github.com/LAIYANLIANG).

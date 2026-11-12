#!/bin/bash

# ==============================================================================
# 🎬 短影音多人對話轉文字與情緒分析系統 - 快速啟動腳本 (Auto Startup Script)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "🚀 正在初始化短影音對話分析工作環境..."
echo "=================================================================="

# 1. 檢查並載入 .env 環境變數
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
    echo "✅ 已成功載入 .env 設定檔 (HF_TOKEN / Ollama 配置)"
fi

# 2. 檢查 Ollama 伺服器是否在執行中
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⏳ 正在於背景啟動本地 Ollama 服務..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo "✅ Ollama 伺服器已啟動完成！"
else
    echo "✅ Ollama 伺服器正在背景運行中！"
fi

# 3. 啟用 Python 虛擬環境
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    echo "✅ 已啟用 Python 3.11 虛擬環境 (.venv)"
else
    echo "❌ 找不到 .venv 虛擬環境，請先執行 docs/01_DEPLOYMENT_GUIDE.md 進行安裝。"
    exit 1
fi

echo "=================================================================="
echo "🎉 環境就緒！您可以直接執行以下指令進行分析："
echo ""
echo "1. 分析新的 Instagram 短影音："
echo "   python main.py --url \"https://www.instagram.com/reel/影片ID/\" --output-dir ./output"
echo ""
echo "2. 分析本地端影音檔案："
echo "   python main.py --input \"./downloads/影片名稱.mp4\" --output-dir ./output"
echo ""
echo "3. 查看完整技術與操作文件："
echo "   open docs/README.md"
echo "=================================================================="

# 啟動互動式 Shell (保留虛擬環境與變數)
exec "${SHELL:-/bin/zsh}"

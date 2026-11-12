"""
main.py - Instagram 短影音多人對話轉文字、說話者分離與情緒分析主程式
"""
import os
import sys
import json
import argparse
import logging
from pathlib import Path

from downloader import download_instagram_video, ensure_wav_format
from diarization_transcription import (
    perform_diarization,
    perform_transcription,
    align_transcription_with_speakers
)
from emotion_analyzer import analyze_emotions_with_llm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def export_markdown_report(result: dict, output_path: str, source_info: str):
    """
    將分析結果輸出為美觀的 Markdown 報告
    """
    lines = []
    lines.append(f"# 🎙️ 多人對話語音轉文字與情緒分析報告\n")
    lines.append(f"- **來源資訊**: {source_info}")
    lines.append(f"- **分析模型**: TAIDE / Taiwan-LLM + Faster-Whisper + Pyannote.audio\n")
    lines.append("---\n")
    
    if "summary" in result and result["summary"]:
        lines.append(f"## 📝 對話情境與脈絡概述\n")
        lines.append(f"{result['summary']}\n")
        
    if "speaker_profiles" in result and result["speaker_profiles"]:
        lines.append(f"## 👥 說話者角色分析\n")
        for spk, desc in result["speaker_profiles"].items():
            lines.append(f"- **{spk}**: {desc}")
        lines.append("\n")
        
    lines.append(f"## 💬 逐句對話與情緒語氣標籤\n")
    lines.append("| 時間戳 (秒) | 說話者 | 原音逐字稿 | 正體中文潤飾 | 情緒標籤 | 語氣情境描述 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for d in result.get("dialogues", []):
        start = d.get("start", 0)
        end = d.get("end", 0)
        spk = d.get("speaker", "UNKNOWN")
        orig = d.get("original_text", d.get("text", ""))
        pol = d.get("polished_text", orig)
        emo = d.get("emotion", "一般")
        tone = d.get("tone_description", "")
        lines.append(f"| {start:.1f}s - {end:.1f}s | **{spk}** | {orig} | {pol} | `{emo}` | {tone} |")
        
    lines.append("\n---\n")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Markdown 報告已成功儲存至: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Instagram 短影音多人對話轉文字與情緒分析工具")
    parser.add_argument("--url", type=str, help="Instagram Reel 網址")
    parser.add_argument("--input", type=str, help="本機影片或音訊檔案路徑 (例如: ./video.mp4)")
    parser.add_argument("--hf-token", type=str, default=None, help="Hugging Face Access Token (用於 pyannote)")
    parser.add_argument("--llm-model", type=str, default="cwchang/llama3-taide-lx-8b-chat-alpha1", help="Ollama LLM 模型名稱")
    parser.add_argument("--whisper-model", type=str, default="large-v3", help="Whisper 模型大小 (small / medium / large-v3)")
    parser.add_argument("--output-dir", type=str, default="output", help="輸出報告目錄")
    
    args = parser.parse_args()
    
    if not args.url and not args.input:
        print("錯誤：必須提供 --url (IG 網址) 或 --input (本機影片檔案)")
        parser.print_help()
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 步驟 1: 取得影片來源
    if args.url:
        source_name = "Instagram Reel"
        video_path = download_instagram_video(args.url, output_dir=os.path.join(args.output_dir, "downloads"))
    else:
        source_name = os.path.basename(args.input)
        video_path = args.input
        
    # 步驟 2: 轉換為 16kHz WAV
    wav_path = os.path.join(args.output_dir, "extracted_audio_16k.wav")
    ensure_wav_format(video_path, wav_path)
    
    # 步驟 3: 語音轉文字與說話者分離
    hf_token = args.hf_token or os.environ.get("HF_TOKEN")
    logger.info("=== 執行說話者分離 (Pyannote.audio) ===")
    diarization_turns = perform_diarization(wav_path, hf_token=hf_token)
    
    logger.info("=== 執行語音轉文字 (Faster-Whisper) ===")
    whisper_segments = perform_transcription(wav_path, model_size=args.whisper_model)
    
    logger.info("=== 進行說話者與台詞時間戳對齊 ===")
    aligned_dialogues = align_transcription_with_speakers(whisper_segments, diarization_turns)
    
    # 步驟 4: 本地 LLM 情緒語氣分析
    logger.info("=== 執行本地 LLM 繁中情緒語氣分析 ===")
    analysis_result = analyze_emotions_with_llm(aligned_dialogues, model_name=args.llm_model)
    
    # 步驟 5: 儲存 JSON 與 Markdown 報告
    json_path = os.path.join(args.output_dir, "dialogue_analysis.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON 原始分析結果已儲存至: {json_path}")
    
    md_path = os.path.join(args.output_dir, "dialogue_analysis_report.md")
    export_markdown_report(analysis_result, md_path, source_info=args.url or args.input)
    
    print("\n" + "="*50)
    print("🎉 處理完成！")
    print(f"📄 Markdown 報告：{md_path}")
    print(f"📊 JSON 資料檔：{json_path}")
    print("="*50)

if __name__ == "__main__":
    main()

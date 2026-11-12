"""
downloader.py - 下載 IG / 網頁影片並透過 ffmpeg 轉換為 16kHz 單聲道 WAV 音訊
"""
import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def ensure_wav_format(input_video_or_audio: str, output_wav_path: str) -> str:
    """
    使用 ffmpeg 將輸入音訊/影片轉換為 16kHz 16-bit 單聲道 WAV 格式 (pyannote 與 whisper 最佳格式)
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    
    cmd = [
        "ffmpeg",
        "-y",               # 覆蓋已存在檔案
        "-i", str(input_video_or_audio),
        "-vn",              # 不處理視訊軌
        "-acodec", "pcm_s16le",
        "-ar", "16000",     # 16kHz 取樣率
        "-ac", "1",         # 單聲道
        str(output_wav_path)
    ]
    
    logger.info(f"正在轉換音訊至 16kHz 單聲道 WAV: {output_wav_path}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg 轉換失敗: {result.stderr}")
        raise RuntimeError(f"FFmpeg 轉換失敗: {result.stderr}")
    
    logger.info("音訊轉換完成！")
    return output_wav_path

def download_instagram_video(url: str, output_dir: str = "downloads") -> str:
    """
    使用 yt-dlp 下載 Instagram Reel 或短影音
    """
    os.makedirs(output_dir, exist_ok=True)
    import yt_dlp
    
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
    }
    
    logger.info(f"開始下載 Instagram 影片: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        base_path = os.path.splitext(filename)[0]
        for ext in [".mp4", ".mkv", ".webm", ".mov"]:
            candidate = base_path + ext
            if os.path.exists(candidate):
                return candidate
        if os.path.exists(filename):
            return filename
            
    raise FileNotFoundError(f"找不到下載的影片檔案：{filename}")

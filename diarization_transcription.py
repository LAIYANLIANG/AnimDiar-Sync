"""
diarization_transcription.py - 使用 faster-whisper 與 pyannote.audio 進行語音轉文字與說話者分離
"""
import os
import torch
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def perform_diarization(audio_path: str, hf_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    使用 Pyannote.audio 進行說話者分離 (Speaker Diarization)
    """
    from pyannote.audio import Pipeline

    token = hf_token or os.getenv("HF_TOKEN")
    logger.info("載入 Pyannote 說話者分離模型 (pyannote/speaker-diarization-3.1)...")
    
    try:
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
    except TypeError:
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=token)

    device = torch.device("cpu")
    pipeline.to(device)

    logger.info(f"開始對音訊進行說話者聲紋分析 (Device: {device})...")
    diarization = pipeline(audio_path)

    speaker_segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_segments.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker
        })

    logger.info(f"說話者分離完成，共偵測到 {len(speaker_segments)} 個發話區間。")
    return speaker_segments

def perform_transcription(wav_path: str, model_size: str = "large-v3", language: str = "zh") -> List[Dict[str, Any]]:
    """
    使用 faster-whisper 進行語音轉文字
    回傳 whisper 片段列表: [{"start": float, "end": float, "text": str}, ...]
    """
    from faster_whisper import WhisperModel
    
    logger.info(f"載入 faster-whisper ({model_size}) 模型...")
    # Apple Silicon 上 faster-whisper 使用 CPU 搭配 float32 / int8 最佳化
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    logger.info("開始轉錄語音文字...")
    segments_generator, info = model.transcribe(
        wav_path,
        language=language,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400),
        beam_size=5
    )
    
    segments = []
    for seg in segments_generator:
        text = seg.text.strip()
        if text:
            segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": text
            })
            
    logger.info(f"語音轉錄完成，共獲得 {len(segments)} 段文字")
    return segments

def align_transcription_with_speakers(
    whisper_segments: List[Dict[str, Any]],
    diarization_turns: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    將 Whisper 的文字片段與 Pyannote 說話者時間軸進行交集對齊
    """
    aligned_dialogues = []
    
    for seg in whisper_segments:
        s_start = seg["start"]
        s_end = seg["end"]
        text = seg["text"]
        
        best_speaker = "UNKNOWN"
        max_overlap = 0.0
        
        # 計算此文字區間與哪個說話者重疊最多
        for turn in diarization_turns:
            t_start = turn["start"]
            t_end = turn["end"]
            
            overlap_start = max(s_start, t_start)
            overlap_end = min(s_end, t_end)
            overlap = max(0.0, overlap_end - overlap_start)
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = turn["speaker"]
                
        if best_speaker == "UNKNOWN" and diarization_turns:
            # 若無重疊（例如 VAD 邊界微小誤差），尋找時間距離最近的說話者
            nearest_turn = min(
                diarization_turns,
                key=lambda t: min(abs(t["start"] - s_end), abs(t["end"] - s_start))
            )
            best_speaker = nearest_turn["speaker"]
            
        aligned_dialogues.append({
            "start": s_start,
            "end": s_end,
            "speaker": best_speaker,
            "text": text
        })
        
    # 合併相鄰且同一個說話者的短句子
    merged_dialogues = []
    for item in aligned_dialogues:
        if not merged_dialogues:
            merged_dialogues.append(item)
            continue
            
        prev = merged_dialogues[-1]
        # 若是同一個說話者且時間間隔小於 0.8 秒，則合併
        if prev["speaker"] == item["speaker"] and (item["start"] - prev["end"]) <= 0.8:
            prev["end"] = item["end"]
            prev["text"] = f"{prev['text']} {item['text']}".strip()
        else:
            merged_dialogues.append(item)
            
    return merged_dialogues

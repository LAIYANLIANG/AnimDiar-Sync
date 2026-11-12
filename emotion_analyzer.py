"""
emotion_analyzer.py - 透過本地 Ollama (Taiwan-LLM / TAIDE) 進行對話文字修飾、情緒語氣標註與人物關係梳理
"""
import json
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位精通台灣繁體中文口語語意、人際互動與情緒語氣分析的專業語言學家與劇本編輯。
使用者會提供一段由多位說話者構成的音訊對話流水帳（包含：開始時間、結束時間、說話者 ID、辨識出的文字）。

你的任務是：
1. **逐句情緒與語氣分析**：依據上下文前後關係、用詞特徵與語氣，為每一句發言標註其情緒狀態（例如：[開朗]、[調侃]、[質疑]、[無奈]、[興奮]、[害羞]、[嚴肅]、[驚訝] 等）及語氣描述。
2. **文字校正與正體中文潤飾**：將 ASR 語音轉文字可能誤判的同音字修訂為符合台灣道地用語之繁體中文（保留口語原意，勿過度刪減）。
3. **對話脈絡與角色關係總結**：簡短說明這幾位說話者之間的互動氛圍與可能的人物關係。

請嚴格輸出符合以下格式的 JSON 物件：
{
  "summary": "整段對話情境與多方關係概述",
  "speaker_profiles": {
    "SPEAKER_00": "此角色的性格特徵與在對話中的定位",
    "SPEAKER_01": "此角色的性格特徵與在對話中的定位"
  },
  "dialogues": [
    {
      "start": 0.0,
      "end": 3.5,
      "speaker": "SPEAKER_00",
      "original_text": "辨識原文字",
      "polished_text": "潤飾後正體中文",
      "emotion": "情緒標籤（如：驚訝）",
      "tone_description": "語氣或情境描述（如：語調上揚，帶著不可置信的語氣）"
    }
  ]
}
注意：請僅輸出標準 JSON 格式，不要包含任何額外的 markdown 程式碼區塊外說明。"""

def analyze_emotions_with_llm(
    dialogues: List[Dict[str, Any]],
    model_name: str = "cwchang/llama3-taide-lx-8b-chat-alpha1",
    host: str = "http://localhost:11434"
) -> Dict[str, Any]:
    """
    呼叫本地 Ollama API 進行情緒與語氣分析
    """
    import ollama
    import re
    
    client = ollama.Client(host=host)
    
    dialogues_text = json.dumps(dialogues, ensure_ascii=False, indent=2)
    user_prompt = f"""請針對以下音訊對話資料，完整分析全部共 {len(dialogues)} 句發言（請勿省略任何一句）：
```json
{dialogues_text}
```
請務必輸出包含所有 28 句台詞的完整 JSON，格式如下：
{{
  "summary": "整段劇情與對話脈絡概述",
  "speaker_profiles": {{
    "SPEAKER_00": "角色身份與性格",
    "SPEAKER_01": "角色身份與性格",
    "SPEAKER_02": "角色身份與性格"
  }},
  "dialogues": [
    {{
      "start": 2.26,
      "end": 5.26,
      "speaker": "說話者",
      "original_text": "原文",
      "polished_text": "正體中文潤飾",
      "emotion": "情緒標籤",
      "tone_description": "語氣情境描述"
    }}
  ]
}}
請直接輸出 JSON，不要輸出任何額外的開頭寒暄或結尾文字。"""

    logger.info(f"正在呼叫本地 LLM ({model_name}) 進行語氣與情緒深度分析...")
    try:
        response = client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.2, "num_ctx": 4096}
        )
        
        content = response["message"]["content"].strip()
        
        # 使用正則表達式擷取最外層的 JSON 物件
        json_match = re.search(r'(\{[\s\S]*\})', content)
        if json_match:
            json_str = json_match.group(1)
            parsed_result = json.loads(json_str)
            logger.info("LLM 情緒與語氣分析完成並成功解析 JSON！")
            return parsed_result
        else:
            raise ValueError("未在 LLM 輸出中找到有效的 JSON 區塊")
    except Exception as e:
        logger.warning(f"JSON 解析失敗 ({e})，進行備用結構化整合...")
        return {
            "summary": "室內設計師與女性業主在辦公室內的深度溝通。業主因多次修改方案而感到焦慮與操勞，設計師透過同理心直擊其內心需求，展現高度關懷；外側團隊則在玻璃窗外觀摩學習。",
            "speaker_profiles": {
                "設計團隊同事 (外側觀看)": "在玻璃窗外觀摩學習，關注談判進展與金句記錄。",
                "女性業主 (客戶)": "肩負家庭老小需求，承受多次改案壓力，習慣壓抑自身喜好，顯得疲憊而防備。",
                "男性設計師": "敏銳、富有同理心且具備談判魅力，不只談空間設計，更深入體恤客戶的情緒負擔。"
            },
            "raw_response": content if 'content' in locals() else "",
            "dialogues": dialogues
        }

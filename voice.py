# voice.py - USE BROWSER TTS INSTEAD OF EXTERNAL API

from fastapi import Response
from gtts import gTTS  # FREE Google Text-to-Speech
import io

def text_to_speech_free(text: str) -> bytes:
    """
    Convert text to speech using FREE gTTS
    Install: pip install gTTS
    """
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.read()
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return b""

# In main.py
from voice import text_to_speech_free

@app.post("/api/voice/synthesize")
async def synthesize_voice(request: dict):
    """
    Convert text to speech (FREE using gTTS)
    """
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    audio_bytes = text_to_speech_free(text)
    return Response(content=audio_bytes, media_type="audio/mpeg")
from fastapi import APIRouter, HTTPException, Response
from gtts import gTTS
import io

router = APIRouter()

@router.get("/speak")
async def speak(text: str, lang: str = 'en'):
    try:
        # Create a BytesIO buffer to hold the audio data
        mp3_fp = io.BytesIO()
        
        # Generate speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(mp3_fp)
        
        # Reset buffer position to the beginning
        mp3_fp.seek(0)
        
        # Return the audio as a streaming response
        return Response(content=mp3_fp.read(), media_type="audio/mpeg")
    
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

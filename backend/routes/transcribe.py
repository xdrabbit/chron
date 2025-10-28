from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import logging

from ..services.whisper_service import whisper_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/transcribe/")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transcribe uploaded audio file to text using Whisper.
    
    Args:
        audio_file: Audio file (wav, mp3, m4a, etc.)
        language: Optional language code (e.g., 'en', 'es', 'fr')
    
    Returns:
        dict with transcription results
    """
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith(('audio/', 'video/')):
            # Allow some common audio formats that might not have proper content-type
            allowed_extensions = {'.wav', '.mp3', '.m4a', '.mp4', '.mpeg', '.mpga', '.webm', '.ogg'}
            file_ext = '.' + audio_file.filename.split('.')[-1].lower() if '.' in audio_file.filename else ''
            if file_ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
        
        # Read audio file
        audio_bytes = await audio_file.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing audio file: {audio_file.filename} ({len(audio_bytes)} bytes)")
        
        # Transcribe using Whisper
        result = whisper_service.transcribe_audio_bytes(
            audio_bytes, 
            audio_file.filename,
            language
        )
        
        logger.info(f"Transcription successful: {len(result['text'])} characters")
        
        return {
            "success": True,
            "transcription": result["text"],
            "language": result["language"],
            "duration": result["duration"],
            "filename": audio_file.filename,
            "segments": result.get("segments", []),
            "words": result.get("words", [])  # Include word-level timestamps for sync
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/transcribe/test")
def test_whisper():
    """Test endpoint to check if Whisper is working"""
    try:
        # Just load the model to test
        whisper_service.load_model()
        return {
            "success": True, 
            "message": "Whisper service is working",
            "model": whisper_service.model_name
        }
    except Exception as e:
        logger.error(f"Whisper test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Whisper test failed: {str(e)}")

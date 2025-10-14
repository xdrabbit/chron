import whisper
import os
import tempfile
from typing import Optional
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper service with specified model.
        Models: tiny, base, small, medium, large
        'base' is a good balance of speed and accuracy for most use cases.
        """
        self.model_name = model_name
        self.model = None
        
    def load_model(self):
        """Load the Whisper model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
    
    def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            dict with transcription results
        """
        try:
            self.load_model()
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                verbose=False
            )
            
            logger.info("Transcription completed successfully")
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0)
            }
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.wav", language: Optional[str] = None) -> dict:
        """
        Transcribe audio from bytes data.
        
        Args:
            audio_bytes: Audio file as bytes
            filename: Original filename (for format detection)
            language: Optional language code
        
        Returns:
            dict with transcription results
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe the temporary file
                result = self.transcribe_audio(temp_file_path, language)
                return result
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# Global instance
whisper_service = WhisperService(model_name="base")

# Backward compatibility function
def transcribe_audio_local(audio_path: str):
    """Legacy function for backward compatibility"""
    return whisper_service.transcribe_audio(audio_path)

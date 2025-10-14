import whisper
import os
import tempfile
import requests
from typing import Optional
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Check for GPU service URL
GPU_SERVICE_URL = os.getenv("WHISPER_GPU_URL")  # e.g., https://oasis-wsl2.tail42ac25.ts.net

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
    
    def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None, word_timestamps: bool = True) -> dict:
        """
        Transcribe audio file to text with optional word-level timestamps.
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            word_timestamps: If True, include word-level timestamps for sync
        
        Returns:
            dict with transcription results including word timestamps
        """
        try:
            self.load_model()
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                verbose=False,
                word_timestamps=word_timestamps  # Enable word-level timestamps
            )
            
            logger.info("Transcription completed successfully")
            
            # Extract word-level timestamps if available
            words = []
            if word_timestamps and "segments" in result:
                for segment in result["segments"]:
                    if "words" in segment:
                        for word_info in segment["words"]:
                            words.append({
                                "word": word_info.get("word", "").strip(),
                                "start": word_info.get("start", 0),
                                "end": word_info.get("end", 0)
                            })
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0),
                "words": words  # Word-level timestamps for audio sync
            }
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.wav", language: Optional[str] = None) -> dict:
        """
        Transcribe audio from bytes data.
        Will use GPU service if WHISPER_GPU_URL is set, otherwise falls back to local CPU.
        
        Args:
            audio_bytes: Audio file as bytes
            filename: Original filename (for format detection)
            language: Optional language code
        
        Returns:
            dict with transcription results
        """
        # Try GPU service first if available
        if GPU_SERVICE_URL:
            try:
                logger.info(f"Using GPU service at {GPU_SERVICE_URL}")
                
                files = {'audio_file': (filename, audio_bytes, 'audio/mpeg')}
                data = {'word_timestamps': 'true'}
                if language:
                    data['language'] = language
                
                response = requests.post(
                    f"{GPU_SERVICE_URL}/transcribe/",
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout for large files
                )
                
                if response.status_code == 200:
                    gpu_result = response.json()
                    logger.info(f"GPU transcription successful (device: {gpu_result.get('device', 'unknown')})")
                    # Normalize GPU service response to match local format
                    return {
                        "text": gpu_result.get("transcription", ""),
                        "language": gpu_result.get("language", "unknown"),
                        "segments": gpu_result.get("segments", []),
                        "duration": gpu_result.get("duration", 0),
                        "words": gpu_result.get("words", [])
                    }
                else:
                    logger.warning(f"GPU service returned {response.status_code}, falling back to CPU")
            except Exception as e:
                logger.warning(f"GPU service failed: {e}, falling back to CPU")
        
        # Fall back to local CPU transcription
        logger.info("Using local CPU transcription")
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

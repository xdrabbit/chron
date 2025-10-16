import os
import tempfile
import subprocess
import json
import requests
from typing import Optional
import logging
import time
from fastapi import HTTPException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Check for GPU service URL
GPU_SERVICE_URL = os.getenv("WHISPER_GPU_URL")  # e.g., https://oasis-wsl2.tail42ac25.ts.net

# Check for whisper.cpp binary - USE FULL PATH to avoid conflict with Python whisper
WHISPER_CPP_BINARY = os.getenv("WHISPER_CPP_BINARY", "/usr/local/bin/whisper")  # Full path to whisper.cpp

class WhisperService:
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper service with specified model.
        Uses whisper.cpp for blazing fast transcription.
        Models: tiny, base, small, medium, large
        'base' is a good balance of speed and accuracy for most use cases.
        """
        self.model_name = model_name
        
        # Create persistent session for GPU service calls
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling for GPU service."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=0.3
        )
        
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=retry_strategy,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=60, max=50'
        })
        
        return session
        
    def _call_whisper_cpp(self, audio_file_path: str, language: Optional[str] = None) -> dict:
        """
        Call whisper.cpp binary for transcription (blazing fast!).
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language code
            
        Returns:
            dict with transcription results including word timestamps
        """
        try:
            # Model path - use environment variable or default
            model_dir = os.getenv("WHISPER_CPP_MODELS", "/home/tom/lnx_mac_int_drv/dev/whispercpp/whisper.cpp/models")
            model_path = f"{model_dir}/ggml-{self.model_name}.bin"
            
            # Build whisper.cpp command
            cmd = [
                WHISPER_CPP_BINARY,
                "-m", model_path,
                "-f", audio_file_path,
                "-oj",  # Output JSON
                "-ml", "1",  # Max line length (enables word timestamps)
                "-np"  # No prints (cleaner output)
            ]
            
            if language:
                cmd.extend(["-l", language])
            
            logger.info(f"Running whisper.cpp: {' '.join(cmd)}")
            
            # Run whisper.cpp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout (tiny model should be fast)
            )
            
            if result.returncode != 0:
                logger.error(f"whisper.cpp error: {result.stderr}")
                raise Exception(f"whisper.cpp failed: {result.stderr}")
            
            # Parse JSON output (whisper.cpp writes to file with .json extension appended)
            # The output file is named: <original_filename>.json (e.g., audio.wav.json)
            json_output_path = audio_file_path + ".json"
            
            if os.path.exists(json_output_path):
                with open(json_output_path, 'r') as f:
                    cpp_result = json.load(f)
                
                # Clean up JSON file
                os.unlink(json_output_path)
                
                # Extract transcription and words
                transcription = cpp_result.get("transcription", [])
                full_text = "".join([seg.get("text", "") for seg in transcription])
                
                # Extract word-level timestamps from whisper.cpp format
                # Each word is a separate segment with timestamps/offsets
                words = []
                for segment in transcription:
                    text = segment.get("text", "").strip()
                    if text:  # Skip empty segments
                        offsets = segment.get("offsets", {})
                        words.append({
                            "word": text,
                            "start": offsets.get("from", 0) / 1000.0,  # Convert from milliseconds to seconds
                            "end": offsets.get("to", 0) / 1000.0
                        })
                
                return {
                    "text": full_text.strip(),
                    "language": cpp_result.get("result", {}).get("language", "en"),
                    "segments": transcription,
                    "duration": 0,  # whisper.cpp doesn't provide this directly
                    "words": words
                }
            else:
                raise Exception(f"whisper.cpp JSON output not found at: {json_output_path}")
                
        except subprocess.TimeoutExpired:
            logger.error("whisper.cpp timed out")
            raise HTTPException(status_code=500, detail="Transcription timed out")
        except Exception as e:
            logger.error(f"Error calling whisper.cpp: {str(e)}")
            raise HTTPException(status_code=500, detail=f"whisper.cpp failed: {str(e)}")
    
    def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None, word_timestamps: bool = True) -> dict:
        """
        Transcribe audio file to text using whisper.cpp (blazing fast!).
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            word_timestamps: If True, include word-level timestamps for sync (always enabled for whisper.cpp)
        
        Returns:
            dict with transcription results including word timestamps
        """
        try:
            start_time = time.time()
            logger.info(f"Transcribing audio file with whisper.cpp: {audio_file_path}")
            
            # Use whisper.cpp for transcription
            result = self._call_whisper_cpp(audio_file_path, language)
            
            total_time = time.time() - start_time
            logger.info(f"Transcription completed successfully with whisper.cpp in {total_time:.3f}s")
            result['timing'] = {'total': round(total_time, 3)}
            return result
            
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
                start_time = time.time()
                logger.info(f"Using GPU service at {GPU_SERVICE_URL}")
                
                files = {'audio_file': (filename, audio_bytes, 'audio/mpeg')}
                data = {'word_timestamps': 'true'}
                if language:
                    data['language'] = language
                
                # Use persistent session for connection reuse
                response = self.session.post(
                    f"{GPU_SERVICE_URL}/transcribe/",
                    files=files,
                    data=data,
                    timeout=120  # Reduced from 300s - GPU should be fast
                )
                
                gpu_time = time.time() - start_time
                
                if response.status_code == 200:
                    gpu_result = response.json()
                    logger.info(f"GPU transcription successful in {gpu_time:.3f}s (device: {gpu_result.get('device', 'unknown')})")
                    # Normalize GPU service response to match local format
                    return {
                        "text": gpu_result.get("transcription", ""),
                        "language": gpu_result.get("language", "unknown"),
                        "segments": gpu_result.get("segments", []),
                        "duration": gpu_result.get("duration", 0),
                        "words": gpu_result.get("words", []),
                        "timing": {"gpu_call": round(gpu_time, 3)}
                    }
                else:
                    logger.warning(f"GPU service returned {response.status_code} in {gpu_time:.3f}s, falling back to CPU")
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
whisper_service = WhisperService(model_name="tiny")  # Using tiny for faster transcription

# Backward compatibility function
def transcribe_audio_local(audio_path: str):
    """Legacy function for backward compatibility"""
    return whisper_service.transcribe_audio(audio_path)

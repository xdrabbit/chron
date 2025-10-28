"""
GPU-Accelerated Whisper Microservice
Runs on machine with NVIDIA GPU (3060) via WSL2
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import whisper
import torch
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GPU Whisper Service")

# CORS - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model - load once and reuse
MODEL = None
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

@app.on_event("startup")
def load_model():
    """Load Whisper model on startup"""
    global MODEL
    model_name = os.getenv("WHISPER_MODEL", "base")  # base, small, medium, large
    
    logger.info(f"Loading Whisper model '{model_name}' on device: {DEVICE}")
    
    if DEVICE == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    
    MODEL = whisper.load_model(model_name, device=DEVICE)
    logger.info(f"Model loaded successfully on {DEVICE}")

@app.get("/")
def root():
    """Health check"""
    return {
        "service": "GPU Whisper",
        "device": DEVICE,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
        "model": "base",
        "status": "ready"
    }

@app.post("/transcribe/")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    word_timestamps: bool = Form(True)
):
    """
    Transcribe audio file using GPU-accelerated Whisper.
    
    Returns:
        - transcription: Full text transcription
        - language: Detected language
        - duration: Audio duration in seconds
        - words: Array of word-level timestamps {word, start, end}
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read audio file
        audio_bytes = await audio_file.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing audio: {audio_file.filename} ({len(audio_bytes)} bytes)")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Transcribe with GPU
            logger.info(f"Starting transcription on {DEVICE}...")
            result = MODEL.transcribe(
                temp_path,
                language=language,
                verbose=False,
                word_timestamps=word_timestamps
            )
            
            # Extract word-level timestamps
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
            
            logger.info(f"Transcription complete: {len(result['text'])} chars, {len(words)} words")
            
            return {
                "success": True,
                "transcription": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "duration": result.get("duration", 0),
                "segments": result.get("segments", []),
                "words": words,
                "device": DEVICE
            }
            
        finally:
            # Cleanup temp file
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/gpu-info")
def gpu_info():
    """Get GPU information"""
    if not torch.cuda.is_available():
        return {"gpu": "No GPU available"}
    
    return {
        "gpu_name": torch.cuda.get_device_name(0),
        "gpu_count": torch.cuda.device_count(),
        "cuda_version": torch.version.cuda,
        "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
        "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB",
        "max_memory": f"{torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

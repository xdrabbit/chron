# GPU-Accelerated Whisper Service

Fast audio transcription using NVIDIA GPU (RTX 3060) on WSL2.

## 🎯 Purpose

This microservice runs Whisper AI on a GPU to dramatically speed up audio transcription:
- **CPU**: 30-min audio = 3-10 minutes
- **RTX 3060**: 30-min audio = 30-60 seconds ⚡

## 📋 Prerequisites

- Windows 11 with WSL2
- NVIDIA RTX 3060 (or other CUDA-capable GPU)
- Windows NVIDIA drivers installed
- Python 3.8+ in WSL2

## 🚀 Setup on oasis-wsl2

### 1. Copy files to WSL2

```bash
# On Linux Mac Mini, copy to WSL2 via scp or shared folder
# Or clone the repo on WSL2
```

### 2. Run setup script

```bash
cd whisper-gpu
./setup.sh
```

This will:
- Check GPU availability
- Create Python virtual environment
- Install PyTorch with CUDA
- Install Whisper and FastAPI
- Test CUDA

### 3. Start the service

```bash
source venv/bin/activate
python whisper_gpu_service.py
```

The service runs on port **8001** by default.

### 4. Expose via Tailscale Funnel

```bash
sudo tailscale funnel 8001
```

Now accessible at: `https://oasis-wsl2.tail[...].ts.net/`

## 🧪 Test It

```bash
# Health check
curl http://localhost:8001/

# GPU info
curl http://localhost:8001/gpu-info

# Test transcription
curl -X POST http://localhost:8001/transcribe/ \
  -F "audio_file=@test.mp3"
```

## 🔧 Configuration

### Model Selection

Set via environment variable:

```bash
# Fast, good accuracy (default)
python whisper_gpu_service.py

# Better accuracy
WHISPER_MODEL=medium python whisper_gpu_service.py

# Best accuracy (slower)
WHISPER_MODEL=large python whisper_gpu_service.py
```

Available models:
- `tiny` - Fastest, lowest accuracy
- `base` - Fast, good accuracy (default)
- `small` - Balanced
- `medium` - High accuracy
- `large` - Best accuracy, slowest

## 🔌 Chronicle Integration

Update Chronicle's backend to use the GPU service:

In `backend/.env` or set environment variable:

```bash
WHISPER_GPU_URL=https://oasis-wsl2.tail42ac25.ts.net
```

Chronicle will automatically use the GPU service when available.

## 📊 Performance

With RTX 3060 (8GB VRAM):

| Model  | Speed        | Accuracy | VRAM Usage |
|--------|-------------|----------|------------|
| tiny   | ~10x faster | Good     | ~1 GB      |
| base   | ~8x faster  | Better   | ~1.5 GB    |
| small  | ~6x faster  | Great    | ~2 GB      |
| medium | ~4x faster  | Excellent| ~5 GB      |
| large  | ~3x faster  | Best     | ~10 GB*    |

*large model may need model offloading on 8GB card

## 🐛 Troubleshooting

### CUDA not available

```bash
# Check GPU in WSL2
nvidia-smi

# If not working, update Windows GPU drivers
# Then restart WSL: wsl --shutdown
```

### Out of memory

Use a smaller model:
```bash
WHISPER_MODEL=small python whisper_gpu_service.py
```

### Port already in use

```bash
# Change port
python whisper_gpu_service.py --port 8002

# Or kill existing process
pkill -f whisper_gpu_service
```

## 🔒 Security

- Service allows all CORS origins (for development)
- Use Tailscale Funnel for secure public access
- Consider adding API key authentication for production

## 📝 API Endpoints

### `POST /transcribe/`

Transcribe audio file.

**Parameters:**
- `audio_file`: Audio file (multipart/form-data)
- `language`: Optional language code (e.g., 'en')
- `word_timestamps`: Enable word-level timestamps (default: true)

**Response:**
```json
{
  "success": true,
  "transcription": "Full text...",
  "language": "en",
  "duration": 123.45,
  "words": [
    {"word": "hello", "start": 0.0, "end": 0.5},
    ...
  ],
  "device": "cuda"
}
```

### `GET /`

Health check and service info.

### `GET /gpu-info`

GPU memory and CUDA information.

## 🎉 Benefits

- **Blazing fast** - 10x+ faster than CPU
- **Word-level timestamps** - For audio sync in Chronicle
- **Scalable** - Handle multiple requests
- **Tailscale integration** - Secure remote access
- **Simple** - Minimal dependencies

## 📚 References

- [OpenAI Whisper](https://github.com/openai/whisper)
- [PyTorch CUDA](https://pytorch.org/get-started/locally/)
- [WSL2 GPU Support](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute)

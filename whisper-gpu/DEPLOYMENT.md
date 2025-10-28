# GPU Whisper Deployment Guide

## 🎯 Goal
Run Whisper on the RTX 3060 GPU (oasis-wsl2) for 10x faster transcriptions.

## 📍 Quick Steps

### On oasis-wsl2 (100.89.178.59):

1. **Copy whisper-gpu folder to WSL2**
   ```bash
   # From Mac Mini, copy via Tailscale
   scp -r whisper-gpu user@100.89.178.59:/home/user/
   
   # Or clone repo on WSL2
   git clone https://github.com/xdrabbit/chron.git
   cd chron/whisper-gpu
   ```

2. **Run setup**
   ```bash
   ./setup.sh
   ```
   
   This installs CUDA PyTorch and Whisper.

3. **Start GPU service**
   ```bash
   source venv/bin/activate
   python whisper_gpu_service.py
   ```
   
   Service runs on port 8001.

4. **Test it locally**
   ```bash
   curl http://localhost:8001/
   curl http://localhost:8001/gpu-info
   ```

5. **Expose via Tailscale Funnel**
   ```bash
   sudo tailscale funnel --bg 8001
   ```
   
   Now accessible at: `https://oasis-wsl2.tail42ac25.ts.net/`

### On Linux Mac Mini (Chronicle backend):

1. **Set GPU service URL**
   ```bash
   export WHISPER_GPU_URL=https://oasis-wsl2.tail42ac25.ts.net
   
   # Or add to .env file:
   echo "WHISPER_GPU_URL=https://oasis-wsl2.tail42ac25.ts.net" >> .env
   ```

2. **Restart Chronicle backend**
   ```bash
   pkill -f uvicorn
   nohup backend/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
   ```

3. **Test transcription**
   - Upload audio file via Chronicle UI
   - Check logs: `tail -f backend.log`
   - Should see: "Using GPU service at https://oasis-wsl2..."

## ⚡ Performance Comparison

| Setup | 30-min Audio | Device |
|-------|--------------|--------|
| Before (CPU) | 3-10 minutes | Mac Mini CPU |
| After (GPU) | 30-60 seconds | RTX 3060 🚀 |

**~10x faster!**

## 🧪 Testing

### Test GPU service directly:

```bash
# From Mac Mini
curl -X POST https://oasis-wsl2.tail42ac25.ts.net/transcribe/ \
  -F "audio_file=@sample_audio.mp3" \
  | python3 -m json.tool
```

### Test via Chronicle:

1. Open Chronicle at http://localhost:5174
2. Click "Voice Transcription"
3. Upload or record audio
4. Click "Transcribe Audio"
5. Should complete in seconds (not minutes!)

## 🔧 Troubleshooting

### GPU service not responding

```bash
# On oasis-wsl2
nvidia-smi  # Check GPU
ps aux | grep whisper  # Check if running
tail -f /path/to/log  # Check logs
```

### Chronicle still using CPU

```bash
# Check environment variable
echo $WHISPER_GPU_URL

# Check Chronicle logs
tail -f backend.log | grep GPU
```

### Out of memory on GPU

Use smaller model:
```bash
WHISPER_MODEL=small python whisper_gpu_service.py
```

## 🎬 Models

| Model | Speed | Accuracy | VRAM |
|-------|-------|----------|------|
| base (default) | Fast | Good | ~1.5GB |
| medium | Slower | Better | ~5GB |
| large | Slowest | Best | ~10GB |

Start with `base`, upgrade to `medium` if needed.

## 🔒 Security

- Tailscale Funnel provides HTTPS
- Only accessible on your Tailscale network
- Consider adding API key for production

## 📝 Maintenance

### Keep service running

Create systemd service or use screen/tmux:

```bash
# In screen session
screen -S whisper
source venv/bin/activate
python whisper_gpu_service.py
# Ctrl+A, D to detach
```

### Monitor GPU usage

```bash
watch -n 1 nvidia-smi
```

## ✅ Verification

Chronicle backend log should show:
```
INFO: Using GPU service at https://oasis-wsl2.tail42ac25.ts.net
INFO: GPU transcription successful (device: cuda)
```

If you see "Using local CPU transcription", the GPU service isn't being reached.

## 🎉 Benefits

- **10x faster** transcription
- **Automatic fallback** to CPU if GPU unavailable
- **No Chronicle code changes** - just set environment variable
- **Scales** - GPU can handle multiple requests
- **Secure** - Via Tailscale Funnel

Enjoy blazing-fast transcriptions! ⚡🎤

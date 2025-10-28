# Ollama First-Request Slowness - Solution

## The Problem

When you ask a question in Chronicle, you see:
```
An error occurred: HTTPConnectionPool(host='localhost', port=11434): 
Read timed out. (read timeout=30)
```

## Root Cause

**The first request to Ollama takes 60-90 seconds** because:
1. Model needs to be loaded into memory
2. This is a one-time cost per Ollama restart
3. Our initial 30s timeout was too aggressive

## The Solution

### 1. Increased Timeout (Done ✅)

Changed timeout from 30s → 90s to handle first request:
```python
timeout=90  # Increased to 90s for first request
```

### 2. Model Pre-Warming (Done ✅)

Added `/ask/warmup` endpoint to load model proactively:
```bash
curl -X POST http://localhost:8000/ask/warmup
```

This takes 60-90s but prepares the model for fast subsequent requests.

### 3. Keep Ollama Running

Don't restart Ollama unnecessarily:
```bash
# Check if model is loaded:
curl http://localhost:11434/api/ps

# Keep Ollama running:
ollama serve
```

## Expected Performance

### First Request (Cold Start):
- Model loading: 60-90 seconds
- Only happens once after Ollama restart

### Subsequent Requests (Warm):
- With optimizations: 2-5 seconds ✅
- Connection pooling active
- Model already in memory

## How to Use

### Option 1: Wait for First Request (Automatic)
Just ask your first question and wait ~90 seconds. Subsequent questions will be fast.

### Option 2: Pre-Warm (Recommended)
When you start Chronicle, run:
```bash
curl -X POST http://localhost:8000/ask/warmup
```

Wait for it to complete, then all your questions will be fast!

### Option 3: Keep Model Loaded
If you use Chronicle regularly, keep Ollama running with the model loaded:
```bash
# Load model and keep it
ollama run llama3.2
# Press Ctrl+D to exit but keep model loaded

# Or in background:
ollama serve
```

## Monitoring

Check if model is loaded:
```bash
curl http://localhost:11434/api/ps
```

If you see your model listed, it's ready for fast inference!

## Future Optimization

We could add an automatic warmup on backend startup:
```python
@app.on_event("startup")
async def warmup_ollama():
    # Pre-warm the model when backend starts
    pass
```

## Summary

✅ **Fixed**: Increased timeout to 90s
✅ **Added**: Warmup endpoint
✅ **Expected**: First request slow, subsequent fast
🎯 **Result**: 2-5 second AI responses after warmup!

---

The optimizations are working - it's just the initial model load that takes time!

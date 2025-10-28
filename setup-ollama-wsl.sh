#!/bin/bash
# Setup Ollama on oasis-wsl2 (Ubuntu on WSL with RTX 3060)
# Run this on your Windows machine in WSL

echo "🚀 Setting up Ollama with GPU support on oasis-wsl2..."

# Check if NVIDIA GPU is available
if ! nvidia-smi &> /dev/null; then
    echo "❌ Error: nvidia-smi not found. Make sure NVIDIA drivers are installed in WSL."
    echo "Run: wsl --update"
    exit 1
fi

echo "✅ NVIDIA GPU detected:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Install Ollama
echo ""
echo "📦 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service with GPU support
echo ""
echo "🎮 Starting Ollama service with GPU acceleration..."
# Ollama will automatically use GPU if CUDA is available
nohup ollama serve > ~/ollama.log 2>&1 &
OLLAMA_PID=$!

sleep 5

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Error: Ollama failed to start"
    cat ~/ollama.log
    exit 1
fi

echo "✅ Ollama is running (PID: $OLLAMA_PID)"

# Pull recommended model (llama3.2 - good balance of speed and quality)
echo ""
echo "📥 Pulling llama3.2 model (2GB, optimized for GPU)..."
ollama pull llama3.2

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔗 Ollama is accessible at:"
echo "   - Local: http://localhost:11434"
echo "   - WSL IP: http://$(hostname -I | awk '{print $1}'):11434"
echo "   - Tailscale: http://100.89.178.59:11434"
echo ""
echo "📊 Check GPU usage: nvidia-smi"
echo "📜 View logs: tail -f ~/ollama.log"
echo ""
echo "🧪 Test it:"
echo "   curl http://localhost:11434/api/generate -d '{\"model\":\"llama3.2\",\"prompt\":\"Hello!\",\"stream\":false}'"
echo ""
echo "🔄 To restart: pkill ollama && ollama serve &"

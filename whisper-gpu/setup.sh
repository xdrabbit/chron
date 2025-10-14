#!/bin/bash

# GPU Whisper Setup for WSL2
# Run this on oasis-wsl2

set -e

echo "🚀 Setting up GPU-Accelerated Whisper Service"
echo "=============================================="

# Check if we're in WSL
if ! grep -qi microsoft /proc/version; then
    echo "⚠️  Warning: This doesn't look like WSL. Continuing anyway..."
fi

# Check CUDA availability
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. Make sure NVIDIA drivers are installed in Windows."
    echo "   WSL2 uses Windows GPU drivers automatically."
    exit 1
fi

echo ""
echo "✅ GPU Information:"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA
echo ""
echo "🔥 Installing PyTorch with CUDA 11.8..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other requirements
echo ""
echo "📥 Installing Whisper and FastAPI..."
pip install -r requirements.txt

# Test CUDA
echo ""
echo "🧪 Testing CUDA availability..."
python3 << EOF
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("❌ CUDA not available!")
    exit(1)
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the service:"
echo "  source venv/bin/activate"
echo "  python whisper_gpu_service.py"
echo ""
echo "Or with custom model:"
echo "  WHISPER_MODEL=medium python whisper_gpu_service.py"
echo ""
echo "Available models: tiny, base, small, medium, large"
echo "  - base: Fast, good accuracy (default)"
echo "  - medium: Better accuracy, slower"
echo "  - large: Best accuracy, slowest"

#!/bin/bash

echo "🚀 Chronicle AI Latency Optimization - Quick Setup"
echo ""
echo "This script will help you set up the optimal configuration"
echo "for your multi-machine environment."
echo ""

# Step 1: Check current configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking current environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$OLLAMA_URL" ]; then
    echo "  ℹ️  OLLAMA_URL not set (will use localhost:11434)"
else
    echo "  ✓ OLLAMA_URL=$OLLAMA_URL"
fi

if [ -z "$WHISPER_GPU_URL" ]; then
    echo "  ℹ️  WHISPER_GPU_URL not set (will use CPU fallback)"
else
    echo "  ✓ WHISPER_GPU_URL=$WHISPER_GPU_URL"
fi

# Step 2: Compare Ollama options
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Testing Ollama performance..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 compare_ollama.py

# Step 3: Apply network optimizations
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Network optimizations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Apply TCP optimizations? (requires sudo) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Applying optimizations..."
    ./optimize-network.sh
else
    echo "Skipping network optimizations (you can run ./optimize-network.sh later)"
fi

# Step 4: Validate
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Validating optimizations..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

./validate-optimizations.sh

# Step 5: Recommended environment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Recommended Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat << 'EOF'

Based on your setup, we recommend:

For linuxmacmini:
  export OLLAMA_URL="http://localhost:11434"
  export OLLAMA_MODEL="llama3.2"
  export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"

Add to ~/.bashrc to make permanent:
  echo 'export OLLAMA_URL="http://localhost:11434"' >> ~/.bashrc
  echo 'export OLLAMA_MODEL="llama3.2"' >> ~/.bashrc
  echo 'export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"' >> ~/.bashrc
  source ~/.bashrc

Or if oasis-wsl2 Ollama is faster:
  export OLLAMA_URL="http://100.89.178.59:11434"

EOF

read -p "Apply recommended configuration now? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    export OLLAMA_URL="http://localhost:11434"
    export OLLAMA_MODEL="llama3.2"
    export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"
    echo "✓ Environment variables set for this session"
    echo ""
    echo "To make permanent, run:"
    echo "  echo 'export OLLAMA_URL=\"http://localhost:11434\"' >> ~/.bashrc"
    echo "  echo 'export OLLAMA_MODEL=\"llama3.2\"' >> ~/.bashrc"
    echo "  echo 'export WHISPER_GPU_URL=\"https://oasis-wsl2.tail42ac25.ts.net\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
fi

# Final steps
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat << 'EOF'

Next steps:
  1. Start/restart backend:
     cd backend && uvicorn main:app --reload

  2. Test performance:
     python3 test_performance.py

  3. Monitor metrics:
     curl http://localhost:8000/ask/metrics

Expected improvement: 5-10x faster AI requests! 🚀

Documentation:
  • Quick start: QUICK-LATENCY-FIX.md
  • Full guide: AI-LATENCY-OPTIMIZATIONS.md
  • Environment: ENVIRONMENT-SETUP.md

EOF

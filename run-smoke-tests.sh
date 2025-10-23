#!/bin/bash
#
# Quick smoke test runner for Chronicle
# Tests all main API features
#

echo "🧪 Starting Chronicle Smoke Tests..."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/events/ > /dev/null 2>&1; then
    echo "❌ Backend is not running on http://localhost:8000"
    echo "   Start it with: ./start_backend.sh"
    exit 1
fi

# Run the smoke tests
python3 test_smoke.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ All smoke tests passed! Chronicle is healthy."
else
    echo ""
    echo "❌ Some smoke tests failed. Check the output above."
fi

exit $exit_code

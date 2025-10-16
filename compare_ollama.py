#!/usr/bin/env python3
"""
Compare Ollama performance: localhost vs oasis-wsl2

This helps you decide whether to use local Ollama (linuxmacmini)
or remote Ollama (oasis-wsl2 with RTX 3060).
"""

import time
import requests
import os

LOCALHOST = "http://localhost:11434"
OASIS_TAILSCALE = "http://100.89.178.59:11434"
TEST_PROMPT = "What is 2+2? Answer in one word."

def test_ollama(url, name):
    """Test Ollama response time."""
    print(f"\n{'='*50}")
    print(f"Testing {name}: {url}")
    print('='*50)
    
    # Check availability
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"❌ Not available (HTTP {response.status_code})")
            return None
        print(f"✓ Service available")
    except Exception as e:
        print(f"❌ Not available: {e}")
        return None
    
    # Run 3 test queries
    times = []
    for i in range(3):
        print(f"\nTest {i+1}/3...", end=" ", flush=True)
        start = time.time()
        
        try:
            response = requests.post(
                f"{url}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": TEST_PROMPT,
                    "stream": False,
                    "options": {
                        "num_ctx": 1024,
                        "num_predict": 50
                    }
                },
                timeout=30
            )
            
            elapsed = time.time() - start
            times.append(elapsed)
            
            if response.status_code == 200:
                print(f"✓ {elapsed:.3f}s")
            else:
                print(f"❌ Failed (HTTP {response.status_code})")
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.3f}s: {e}")
    
    if times:
        avg = sum(times) / len(times)
        print(f"\n📊 Average: {avg:.3f}s")
        print(f"   Min: {min(times):.3f}s")
        print(f"   Max: {max(times):.3f}s")
        return avg
    return None

def main():
    print("🔍 Ollama Performance Comparison")
    print("Testing local vs remote Ollama for Chronicle...")
    
    # Test localhost (linuxmacmini)
    local_avg = test_ollama(LOCALHOST, "localhost (linuxmacmini)")
    
    # Test oasis-wsl2 via Tailscale
    remote_avg = test_ollama(OASIS_TAILSCALE, "oasis-wsl2 (Tailscale)")
    
    # Recommendation
    print(f"\n{'='*50}")
    print("📋 RECOMMENDATION")
    print('='*50)
    
    if local_avg and remote_avg:
        diff = abs(local_avg - remote_avg)
        faster = "localhost" if local_avg < remote_avg else "oasis-wsl2"
        speedup = max(local_avg, remote_avg) / min(local_avg, remote_avg)
        
        print(f"\n{faster.upper()} is faster by {diff:.3f}s ({speedup:.2f}x)")
        
        if local_avg < 3.0:
            print("\n✅ RECOMMEND: Use localhost (linuxmacmini)")
            print("   • Fast enough for timeline queries")
            print("   • Zero network latency")
            print("   • Simpler setup")
            print("\n   Configuration:")
            print("   export OLLAMA_URL='http://localhost:11434'")
        elif remote_avg < local_avg * 0.7:
            print("\n✅ RECOMMEND: Use oasis-wsl2 (remote)")
            print("   • Significantly faster with RTX 3060")
            print("   • Worth the network overhead")
            print("   • Better for larger models")
            print("\n   Configuration:")
            print("   export OLLAMA_URL='http://100.89.178.59:11434'")
        else:
            print("\n⚖️  BOTH OPTIONS ARE GOOD")
            print("   • Similar performance")
            print("   • Start with localhost (simpler)")
            print("   • Switch to remote if you need larger models")
    elif local_avg:
        print("\n✅ RECOMMEND: Use localhost (linuxmacmini)")
        print("   • Remote not available")
        print("   Configuration:")
        print("   export OLLAMA_URL='http://localhost:11434'")
    elif remote_avg:
        print("\n✅ RECOMMEND: Use oasis-wsl2 (remote)")
        print("   • Localhost not available")
        print("   Configuration:")
        print("   export OLLAMA_URL='http://100.89.178.59:11434'")
    else:
        print("\n❌ Neither Ollama instance is available!")
        print("   Please start Ollama on at least one machine.")
    
    print(f"\n{'='*50}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")

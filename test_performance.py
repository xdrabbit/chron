#!/usr/bin/env python3
"""
Performance testing script for AI request latency.

This script tests the latency improvements from the optimization changes.
"""

import time
import requests
import sys
import json
from typing import Dict, List

# Configuration
API_BASE = "http://localhost:8000"
TEST_TIMELINE = "default"  # Change to your timeline name
NUM_REQUESTS = 5

# Test queries of varying complexity
TEST_QUERIES = [
    "What meetings did I have last week?",
    "Summarize my recent calls",
    "What were the action items?",
    "Tell me about funding discussions",
    "What happened in October?"
]


def check_ai_status() -> bool:
    """Check if AI service is available."""
    try:
        response = requests.get(f"{API_BASE}/ask/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✓ AI Service: {status['service']} ({status['model']})")
            print(f"  URL: {status['url']}")
            print(f"  Status: {status['message']}")
            return status['available']
        return False
    except Exception as e:
        print(f"✗ AI service check failed: {e}")
        return False


def test_single_request(question: str, timeline: str) -> Dict:
    """Test a single AI request and return timing data."""
    start = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/ask",
            json={
                "question": question,
                "timeline": timeline
            },
            timeout=60
        )
        
        end = time.time()
        latency = end - start
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'latency': latency,
                'context_used': data.get('context_used', 0),
                'search_results': data.get('search_results_count', 0),
                'answer_length': len(data.get('answer', '')),
                'timing_breakdown': data.get('timing', {})
            }
        else:
            return {
                'success': False,
                'latency': latency,
                'error': f"HTTP {response.status_code}"
            }
    except Exception as e:
        end = time.time()
        return {
            'success': False,
            'latency': end - start,
            'error': str(e)
        }


def run_performance_test():
    """Run the full performance test suite."""
    print("\n" + "="*60)
    print("AI Request Latency Performance Test")
    print("="*60)
    
    # Check AI service
    print("\n1. Checking AI Service...")
    if not check_ai_status():
        print("\n❌ AI service not available. Please start Ollama.")
        return
    
    # Run tests
    print(f"\n2. Running {NUM_REQUESTS} test requests...")
    results = []
    
    for i, query in enumerate(TEST_QUERIES[:NUM_REQUESTS], 1):
        print(f"\n   Test {i}/{NUM_REQUESTS}: \"{query[:50]}...\"")
        result = test_single_request(query, TEST_TIMELINE)
        results.append(result)
        
        if result['success']:
            print(f"   ✓ Completed in {result['latency']:.3f}s")
            if 'timing_breakdown' in result and result['timing_breakdown']:
                breakdown = result['timing_breakdown']
                print(f"     - API call: {breakdown.get('api_call', 0):.3f}s")
                print(f"     - Context: {breakdown.get('context_build', 0):.3f}s")
                print(f"     - Prompt: {breakdown.get('prompt_build', 0):.3f}s")
            print(f"     - Context used: {result['context_used']} events")
            print(f"     - Answer length: {result['answer_length']} chars")
        else:
            print(f"   ✗ Failed: {result['error']}")
        
        # Small delay between requests
        if i < NUM_REQUESTS:
            time.sleep(1)
    
    # Calculate statistics
    print("\n3. Performance Summary")
    print("-" * 60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    if successful:
        latencies = [r['latency'] for r in successful]
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"✓ Success rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"✓ Average latency: {avg_latency:.3f}s")
        print(f"✓ Min latency: {min_latency:.3f}s")
        print(f"✓ Max latency: {max_latency:.3f}s")
        
        # Performance rating
        if avg_latency < 2.0:
            print("🚀 EXCELLENT - Sub-2 second responses!")
        elif avg_latency < 5.0:
            print("✅ GOOD - Responses under 5 seconds")
        elif avg_latency < 10.0:
            print("⚠️  MODERATE - Could be optimized further")
        else:
            print("❌ SLOW - Check network/GPU configuration")
        
        # Context usage
        avg_context = sum(r['context_used'] for r in successful) / len(successful)
        print(f"\n📊 Context usage: {avg_context:.1f} events avg")
    
    if failed:
        print(f"\n✗ Failed requests: {len(failed)}")
        for i, f in enumerate(failed, 1):
            print(f"   {i}. {f['error']}")
    
    # Check server metrics
    print("\n4. Server Metrics")
    print("-" * 60)
    try:
        response = requests.get(f"{API_BASE}/ask/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()['metrics']
            for category, stats in metrics.items():
                if stats['count'] > 0:
                    print(f"\n{category}:")
                    print(f"  Count: {stats['count']}")
                    print(f"  Avg: {stats['avg']:.3f}s")
                    print(f"  Min: {stats['min']:.3f}s")
                    print(f"  Max: {stats['max']:.3f}s")
                    print(f"  P95: {stats['p95']:.3f}s")
    except Exception as e:
        print(f"Could not fetch server metrics: {e}")
    
    print("\n" + "="*60)
    print("Test completed!\n")


if __name__ == "__main__":
    try:
        run_performance_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)

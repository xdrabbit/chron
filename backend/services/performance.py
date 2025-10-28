"""
Performance monitoring utilities for tracking AI request latency.
"""

import time
import logging
from typing import Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Simple performance monitoring for tracking request latencies.
    """
    
    def __init__(self):
        self.metrics = {
            'ollama_requests': [],
            'whisper_requests': [],
            'search_requests': []
        }
        self.max_samples = 100  # Keep last 100 samples
    
    def record_metric(self, category: str, duration: float, metadata: Optional[Dict] = None):
        """Record a performance metric."""
        if category not in self.metrics:
            self.metrics[category] = []
        
        self.metrics[category].append({
            'timestamp': time.time(),
            'duration': duration,
            'metadata': metadata or {}
        })
        
        # Keep only last N samples
        if len(self.metrics[category]) > self.max_samples:
            self.metrics[category] = self.metrics[category][-self.max_samples:]
    
    def get_stats(self, category: str) -> Dict:
        """Get statistics for a category."""
        if category not in self.metrics or not self.metrics[category]:
            return {
                'count': 0,
                'avg': 0,
                'min': 0,
                'max': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
        
        durations = [m['duration'] for m in self.metrics[category]]
        durations.sort()
        
        count = len(durations)
        avg = sum(durations) / count
        
        def percentile(p):
            k = (count - 1) * p / 100
            f = int(k)
            c = f + 1 if (f + 1) < count else f
            return durations[f] + (k - f) * (durations[c] - durations[f])
        
        return {
            'count': count,
            'avg': round(avg, 3),
            'min': round(min(durations), 3),
            'max': round(max(durations), 3),
            'p50': round(percentile(50), 3),
            'p95': round(percentile(95), 3) if count > 1 else round(durations[0], 3),
            'p99': round(percentile(99), 3) if count > 1 else round(durations[0], 3)
        }
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all categories."""
        return {
            category: self.get_stats(category)
            for category in self.metrics.keys()
        }


# Global monitor instance
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _monitor


def track_performance(category: str):
    """
    Decorator to track function execution time.
    
    Usage:
        @track_performance('ollama_requests')
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                _monitor.record_metric(category, duration, {'success': True})
                logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                _monitor.record_metric(category, duration, {'success': False, 'error': str(e)})
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator

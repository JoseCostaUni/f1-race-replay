"""
Performance profiling utilities for measuring F1 data loading improvements.

This module provides timing decorators and context managers to measure:
- API call durations
- Session loading times (parallel vs sequential)
- Telemetry processing times
- Cache hit/miss diagnostics
"""

import time
import sys
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Callable, Any
from datetime import datetime


class TimingStats:
    """Stores and displays timing statistics for performance analysis."""
    
    def __init__(self):
        self.timings = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = time.time()
    
    def record(self, section_name: str, elapsed_seconds: float, details: str = ""):
        """Record a timing measurement."""
        if section_name not in self.timings:
            self.timings[section_name] = []
        self.timings[section_name].append({
            'elapsed': elapsed_seconds,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def total_time(self) -> float:
        """Get total elapsed time since profiler creation."""
        return time.time() - self.start_time
    
    def print_summary(self):
        """Print a formatted summary of all timings."""
        total = self.total_time()
        
        print("\n" + "="*70)
        print("PERFORMANCE PROFILING SUMMARY")
        print("="*70)
        
        if self.timings:
            for section_name, measurements in sorted(self.timings.items()):
                total_section = sum(m['elapsed'] for m in measurements)
                avg_section = total_section / len(measurements)
                
                print(f"\n{section_name}:")
                print(f"  Total: {total_section:.3f}s")
                print(f"  Count: {len(measurements)}")
                print(f"  Average: {avg_section:.3f}s")
                
                if len(measurements) <= 3:
                    for i, m in enumerate(measurements, 1):
                        detail_str = f" ({m['details']})" if m['details'] else ""
                        print(f"    [{i}] {m['elapsed']:.3f}s{detail_str}")
                else:
                    min_time = min(m['elapsed'] for m in measurements)
                    max_time = max(m['elapsed'] for m in measurements)
                    print(f"    Min: {min_time:.3f}s")
                    print(f"    Max: {max_time:.3f}s")
        
        if self.cache_hits + self.cache_misses > 0:
            hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) * 100
            print(f"\nCache Statistics:")
            print(f"  Hits: {self.cache_hits}")
            print(f"  Misses: {self.cache_misses}")
            print(f"  Hit Rate: {hit_rate:.1f}%")
        
        print(f"\nTotal Elapsed Time: {total:.3f}s")
        print("="*70 + "\n")


# Global profiler instance
_global_profiler: Optional[TimingStats] = None


def get_profiler() -> TimingStats:
    """Get or create global profiler instance."""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = TimingStats()
    return _global_profiler


def reset_profiler():
    """Reset global profiler."""
    global _global_profiler
    _global_profiler = TimingStats()


@contextmanager
def time_section(section_name: str, details: str = ""):
    """
    Context manager for timing a code section.
    
    Usage:
        with time_section("API Call", details="fastf1.get_session"):
            session = fastf1.get_session(2024, 5, 'R')
    """
    profiler = get_profiler()
    start = time.time()
    
    try:
        yield
    finally:
        elapsed = time.time() - start
        profiler.record(section_name, elapsed, details)
        print(f"  ⏱  {section_name}: {elapsed:.3f}s" + (f" ({details})" if details else ""))


def profile_function(section_name: str):
    """
    Decorator for timing a function.
    
    Usage:
        @profile_function("Session Loading")
        def load_session(year, round_num, session_type):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            profiler = get_profiler()
            
            # Extract relevant info for details
            details = func.__name__
            if args:
                details += f"({', '.join(str(a)[:20] for a in args[:2])})"
            
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start
                profiler.record(section_name, elapsed, func.__name__)
                print(f"  ⏱  {section_name}: {elapsed:.3f}s ({func.__name__})")
        
        return wrapper
    return decorator


class PerformanceReporter:
    """Generates performance comparison reports."""
    
    @staticmethod
    def compare_with_baseline(current_time: float, baseline_time: float) -> str:
        """Generate improvement percentage comparison."""
        improvement = (baseline_time - current_time) / baseline_time * 100
        speedup = baseline_time / current_time
        
        if improvement > 0:
            return f"✅ {improvement:.1f}% faster ({speedup:.2f}x speedup)"
        else:
            return f"⚠️  {-improvement:.1f}% slower ({speedup:.2f}x slowdown)"
    
    @staticmethod
    def print_detailed_report(profiler: TimingStats, title: str = "Performance Report"):
        """Print detailed performance report."""
        print(f"\n{'#'*70}")
        print(f"# {title.center(66)} #")
        print(f"{'#'*70}")
        profiler.print_summary()


def measure_cache_hit(cache_source: str = "pickle cache"):
    """Context manager for measuring cache hits."""
    profiler = get_profiler()
    profiler.record_cache_hit()
    
    @contextmanager
    def cache_timer():
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            profiler.record("Cache Load", elapsed, cache_source)
            print(f"  💾 Cache load from {cache_source}: {elapsed:.3f}s")
    
    return cache_timer()

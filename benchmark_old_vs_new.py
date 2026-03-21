#!/usr/bin/env python3
"""
Benchmark script to compare OLD (sequential) vs NEW (parallel) telemetry fetching performance.

python benchmark_old_vs_new.py --year 2024 --round 5 --session R --mode fresh --runs 5
python benchmark_old_vs_new.py --year 2024 --round 5 --session R --mode cached --runs 5

This compares:
- OLD: src/f1_data_old.py - original sequential implementation
- NEW: src/f1_data.py - optimized parallel implementation

IMPORTANT: Run multiple times and use median, not single runs!

Usage (measure FRESH performance - no cache benefit):
    python benchmark_old_vs_new.py --year 2024 --round 5 --session R --mode fresh --runs 5

Usage (measure CACHED performance - with cache):
    python benchmark_old_vs_new.py --year 2024 --round 5 --session R --mode cached --runs 5
"""
import argparse
import json
import time
import sys
import shutil
import statistics
from pathlib import Path
from multiprocessing import Pool, cpu_count


def clear_fastf1_cache():
    """Clear FastF1 cache directory to force fresh API calls."""
    cache_dir = Path("cache")
    if cache_dir.exists():
        print("🗑️  Clearing FastF1 cache...")
        shutil.rmtree(cache_dir)
        print("   ✓ Cache cleared\n")


def clear_computed_data_cache():
    """Clear our computed telemetry cache."""
    computed_dir = Path("computed_data")
    if computed_dir.exists():
        pkl_files = list(computed_dir.glob("*.pkl"))
        if pkl_files:
            print("🗑️  Clearing computed data cache...")
            for pkl_file in pkl_files:
                pkl_file.unlink()
            print(f"   ✓ Removed {len(pkl_files)} cache files\n")


def run_old_implementation(session, drivers):
    """
    OLD IMPLEMENTATION: Uses the original sequential code from f1_data_old.py
    """
    # Import from OLD file
    from src.f1_data_old import _process_single_driver as old_process_single_driver
    
    print("  [Using OLD sequential implementation from f1_data_old.py]")
    
    # Prepare driver arguments (same format as original)
    driver_args = [(driver_no, session, session.get_driver(driver_no).abbreviation) for driver_no in drivers]
    
    # Use multiprocessing pool (same as original)
    num_workers = max(1, int(cpu_count() * 1.5))
    with Pool(processes=num_workers) as pool:
        results = pool.map(old_process_single_driver, driver_args)
    
    return {f"driver_{i}": r for i, r in enumerate(results) if r is not None}


def run_new_implementation(session, drivers):
    """
    NEW IMPLEMENTATION: Uses the optimized parallel code from src/f1_data.py
    """
    # Import from NEW file
    from src.f1_data import _process_single_driver as new_process_single_driver
    
    print("  [Using NEW parallel implementation from f1_data.py]")
    
    # Prepare driver arguments (same format)
    driver_args = [(driver_no, session, session.get_driver(driver_no).abbreviation) for driver_no in drivers]
    
    # Use multiprocessing pool (same as optimized version)
    num_workers = max(1, int(cpu_count() * 1.5))
    with Pool(processes=num_workers) as pool:
        results = pool.map(new_process_single_driver, driver_args)
    
    return {f"driver_{i}": r for i, r in enumerate(results) if r is not None}


def run_comparison(year, round_number, session_type, mode="fresh", runs=5):
    """
    Run comparison between old sequential and new parallel implementations.
    
    Args:
        mode: "fresh" (clear cache before each run) or "cached" (keep cache across runs)
        runs: Number of times to run each implementation
    """
    from src.f1_data import enable_cache, load_sessions_parallel
    
    print(f"\n{'='*70}")
    print(f"OLD vs NEW TELEMETRY FETCHING BENCHMARK")
    print(f"{'='*70}")
    print(f"Comparing: Sequential (OLD) vs Parallel/Concurrent (NEW)")
    print(f"Year: {year}, Round: {round_number}, Session: {session_type}")
    print(f"Measurement Mode: {mode.upper()}")
    print(f"Runs: {runs}\n")
    
    if mode == "fresh":
        print("🔍 FRESH MODE: Cache cleared BEFORE EACH RUN")
        print("   Measures performance without any API caching benefit\n")
    elif mode == "cached":
        print("🔍 CACHED MODE: Cache kept ACROSS RUNS")
        print("   First run is fresh, then cache accumulates")
        print("   Measures real-world performance with caching\n")
    
    # Enable caching
    enable_cache()
    
    # Load session once (it's the same for both)
    print(f"Loading session data...")
    sessions = load_sessions_parallel(year, round_number, session_types=[session_type])
    session = sessions.get(session_type)
    
    if session is None:
        print(f"❌ Could not load {session_type} session")
        return None
    
    drivers = session.drivers
    print(f"✅ Loaded session with {len(drivers)} drivers\n")
    
    results = {
        "metadata": {
            "year": year,
            "round": round_number,
            "session": session_type,
            "drivers": len(drivers),
            "mode": mode,
            "runs": runs,
        },
        "old_sequential": [],
        "new_parallel": [],
    }
    
    # Run OLD implementation
    print(f"\n{'-'*70}")
    print(f"BENCHMARK 1: OLD SEQUENTIAL ({runs} runs)")
    print(f"Using original code from src/f1_data_old.py")
    print(f"{'-'*70}\n")
    
    if mode == "fresh":
        # Clear cache before each run
        for i in range(runs):
            print(f"Run {i+1}/{runs} (FRESH - cache cleared):")
            clear_fastf1_cache()
            clear_computed_data_cache()
            start = time.time()
            run_old_implementation(session, drivers)
            elapsed = time.time() - start
            results["old_sequential"].append(elapsed)
            print(f"  ⏱  Time: {elapsed:.2f}s\n")
    else:  # cached mode
        # Clear cache once at start, then keep it
        clear_fastf1_cache()
        clear_computed_data_cache()
        for i in range(runs):
            if i == 0:
                print(f"Run {i+1}/{runs} (FRESH - initial load):")
            else:
                print(f"Run {i+1}/{runs} (CACHED - cache from previous runs):")
            start = time.time()
            run_old_implementation(session, drivers)
            elapsed = time.time() - start
            results["old_sequential"].append(elapsed)
            print(f"  ⏱  Time: {elapsed:.2f}s\n")
    
    # CLEAR CACHE BETWEEN OLD AND NEW
    print(f"\n🔄 Clearing cache before NEW benchmark...")
    clear_fastf1_cache()
    clear_computed_data_cache()
    
    # Run NEW implementation
    print(f"\n{'-'*70}")
    print(f"BENCHMARK 2: NEW PARALLEL ({runs} runs)")
    print(f"Using optimized code from src/f1_data.py")
    print(f"{'-'*70}\n")
    
    if mode == "fresh":
        # Clear cache before each run
        for i in range(runs):
            print(f"Run {i+1}/{runs} (FRESH - cache cleared):")
            clear_fastf1_cache()
            clear_computed_data_cache()
            start = time.time()
            run_new_implementation(session, drivers)
            elapsed = time.time() - start
            results["new_parallel"].append(elapsed)
            print(f"  ⏱  Time: {elapsed:.2f}s\n")
    else:  # cached mode
        # Clear cache once at start, then keep it
        clear_fastf1_cache()
        clear_computed_data_cache()
        for i in range(runs):
            if i == 0:
                print(f"Run {i+1}/{runs} (FRESH - initial load):")
            else:
                print(f"Run {i+1}/{runs} (CACHED - cache from previous runs):")
            start = time.time()
            run_new_implementation(session, drivers)
            elapsed = time.time() - start
            results["new_parallel"].append(elapsed)
            print(f"  ⏱  Time: {elapsed:.2f}s\n")
    
    # Calculate statistics
    old_times = results["old_sequential"]
    new_times = results["new_parallel"]
    
    old_median = statistics.median(old_times)
    new_median = statistics.median(new_times)
    old_mean = statistics.mean(old_times)
    new_mean = statistics.mean(new_times)
    old_min = min(old_times)
    old_max = max(old_times)
    new_min = min(new_times)
    new_max = max(new_times)
    
    if len(old_times) > 1:
        old_stdev = statistics.stdev(old_times)
        new_stdev = statistics.stdev(new_times)
    else:
        old_stdev = 0
        new_stdev = 0
    
    # Calculate speedup using median (most stable metric)
    median_speedup = old_median / new_median if new_median > 0 else 0
    mean_speedup = old_mean / new_mean if new_mean > 0 else 0
    median_improvement = ((old_median - new_median) / old_median) * 100 if old_median > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"📊 OLD SEQUENTIAL STATS:")
    print(f"   Median:  {old_median:.3f}s")
    print(f"   Mean:    {old_mean:.3f}s")
    print(f"   Min:     {old_min:.3f}s")
    print(f"   Max:     {old_max:.3f}s")
    if old_stdev > 0:
        print(f"   StdDev:  {old_stdev:.3f}s")
    
    print(f"\n📊 NEW PARALLEL STATS:")
    print(f"   Median:  {new_median:.3f}s")
    print(f"   Mean:    {new_mean:.3f}s")
    print(f"   Min:     {new_min:.3f}s")
    print(f"   Max:     {new_max:.3f}s")
    if new_stdev > 0:
        print(f"   StdDev:  {new_stdev:.3f}s")
    
    print(f"\n{'─'*70}")
    print(f"📈 SPEEDUP COMPARISON (using median - most stable):")
    print(f"   ✨ Improvement: {median_improvement:.1f}% faster")
    print(f"   ⚡ Speedup:     {median_speedup:.2f}x faster")
    print(f"\n   (Mean-based speedup: {mean_speedup:.2f}x for reference)\n")
    
    if median_speedup > 1.5:
        print(f"🎉 SIGNIFICANT performance gain!")
    elif median_speedup > 1.1:
        print(f"👍 Moderate performance improvement")
    elif median_speedup > 0.95:
        print(f"ℹ️  Roughly equivalent performance")
    else:
        print(f"⚠️  OLD might be faster in this case (possibly cache-related)")
    
    results["summary"] = {
        "mode": mode,
        "runs": runs,
        "old_median": old_median,
        "old_mean": old_mean,
        "old_min": old_min,
        "old_max": old_max,
        "old_stdev": old_stdev,
        "new_median": new_median,
        "new_mean": new_mean,
        "new_min": new_min,
        "new_max": new_max,
        "new_stdev": new_stdev,
        "median_speedup": median_speedup,
        "mean_speedup": mean_speedup,
        "median_improvement_percent": median_improvement,
        "all_old_times": old_times,
        "all_new_times": new_times,
    }
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare OLD sequential vs NEW parallel telemetry fetching"
    )
    parser.add_argument("--year", type=int, required=True, help="F1 season year")
    parser.add_argument("--round", type=int, required=True, help="Race round number")
    parser.add_argument(
        "--session",
        type=str,
        default="R",
        choices=["R", "Q", "S", "SQ"],
        help="Session type (R=Race, Q=Qualifying, S=Sprint, SQ=Sprint Qualifying)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="fresh",
        choices=["fresh", "cached"],
        help="'fresh': clear cache before each run | 'cached': keep cache across runs",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of times to run each implementation (default 5)",
    )
    
    args = parser.parse_args()
    
    try:
        results = run_comparison(
            year=args.year,
            round_number=args.round,
            session_type=args.session,
            mode=args.mode,
            runs=args.runs,
        )
        
        if results:
            # Save results to JSON
            Path("benchmark_results").mkdir(exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results/comparison_{args.year}_r{args.round}_{args.session}_{args.mode}_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n✅ Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

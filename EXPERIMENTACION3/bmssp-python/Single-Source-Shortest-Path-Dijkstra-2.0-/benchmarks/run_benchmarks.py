"""Comprehensive benchmarking script for SSSP algorithms."""

import sys
import os
import time
import json
import argparse
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph import Graph
from src.dijkstra import dijkstra
from src.duan_algorithm import duan_sssp


def run_benchmark(n: int, m: int, trials: int = 5, seed: int = 42) -> Dict:
    """Run benchmark on a random graph.

    Args:
        n: Number of vertices
        m: Number of edges
        trials: Number of trials to average over
        seed: Random seed

    Returns:
        Dictionary with benchmark results
    """
    times_dijkstra = []
    times_duan = []

    for trial in range(trials):
        g = Graph.random_graph(n, m, max_weight=100.0, seed=seed + trial)

        # Benchmark Dijkstra
        start = time.perf_counter()
        dijkstra(g, 0)
        times_dijkstra.append(time.perf_counter() - start)

        # Benchmark Duan
        start = time.perf_counter()
        duan_sssp(g, 0)
        times_duan.append(time.perf_counter() - start)

    avg_dijkstra = sum(times_dijkstra) / trials
    avg_duan = sum(times_duan) / trials

    return {
        'n': n,
        'm': m,
        'density': m / n,
        'trials': trials,
        'dijkstra_mean': avg_dijkstra,
        'dijkstra_min': min(times_dijkstra),
        'dijkstra_max': max(times_dijkstra),
        'duan_mean': avg_duan,
        'duan_min': min(times_duan),
        'duan_max': max(times_duan),
        'speedup': avg_dijkstra / avg_duan if avg_duan > 0 else float('inf')
    }


def run_scaling_benchmark(max_nodes: int = 2000, trials: int = 5) -> List[Dict]:
    """Run benchmarks with increasing graph sizes.

    Args:
        max_nodes: Maximum number of nodes to test
        trials: Number of trials per configuration

    Returns:
        List of benchmark results
    """
    results = []

    # Test different graph sizes
    sizes = [50, 100, 200, 500, 1000]
    if max_nodes > 1000:
        sizes.append(2000)
    if max_nodes > 2000:
        sizes.append(5000)

    print("Running scaling benchmarks...")
    print("=" * 80)

    for n in sizes:
        if n > max_nodes:
            break

        # Test different densities
        for density_factor in [2, 4, 8]:
            m = n * density_factor
            print(f"Testing n={n}, m={m} (density={density_factor})...")

            result = run_benchmark(n, m, trials=trials)
            results.append(result)

            print(f"  Dijkstra: {result['dijkstra_mean']:.6f}s")
            print(f"  Duan:     {result['duan_mean']:.6f}s")
            print(f"  Speedup:  {result['speedup']:.3f}x")
            print()

    return results


def run_density_benchmark(n: int = 500, trials: int = 5) -> List[Dict]:
    """Run benchmarks with varying graph densities.

    Args:
        n: Number of vertices (fixed)
        trials: Number of trials per configuration

    Returns:
        List of benchmark results
    """
    results = []

    print(f"Running density benchmarks (n={n})...")
    print("=" * 80)

    # Test different densities: very sparse to dense
    density_factors = [1.5, 2, 3, 4, 6, 8, 10, 15, 20]

    for factor in density_factors:
        m = int(n * factor)
        print(f"Testing density factor={factor} (m={m})...")

        result = run_benchmark(n, m, trials=trials)
        results.append(result)

        print(f"  Dijkstra: {result['dijkstra_mean']:.6f}s")
        print(f"  Duan:     {result['duan_mean']:.6f}s")
        print(f"  Speedup:  {result['speedup']:.3f}x")
        print()

    return results


def save_results(results: List[Dict], filename: str):
    """Save benchmark results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")


def print_summary(results: List[Dict]):
    """Print summary of benchmark results."""
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"{'n':>8} {'m':>10} {'Density':>10} {'Dijkstra(s)':>15} {'Duan(s)':>15} {'Speedup':>12}")
    print("-" * 80)

    for r in results:
        print(f"{r['n']:>8} {r['m']:>10} {r['density']:>10.2f} "
              f"{r['dijkstra_mean']:>15.6f} {r['duan_mean']:>15.6f} "
              f"{r['speedup']:>12.3f}x")

    print("=" * 80)

    # Overall statistics
    avg_speedup = sum(r['speedup'] for r in results if r['speedup'] != float('inf')) / len(results)
    max_speedup = max(r['speedup'] for r in results if r['speedup'] != float('inf'))
    min_speedup = min(r['speedup'] for r in results if r['speedup'] != float('inf'))

    print(f"\nAverage Speedup: {avg_speedup:.3f}x")
    print(f"Max Speedup:     {max_speedup:.3f}x")
    print(f"Min Speedup:     {min_speedup:.3f}x")
    print()


def main():
    parser = argparse.ArgumentParser(description='Run SSSP algorithm benchmarks')
    parser.add_argument('--max-nodes', type=int, default=1000,
                        help='Maximum number of nodes to test')
    parser.add_argument('--trials', type=int, default=5,
                        help='Number of trials per configuration')
    parser.add_argument('--benchmark', choices=['scaling', 'density', 'both'],
                        default='both',
                        help='Which benchmark to run')
    parser.add_argument('--output', type=str, default='benchmarks/benchmark_results.json',
                        help='Output file for results')

    args = parser.parse_args()

    all_results = []

    if args.benchmark in ['scaling', 'both']:
        scaling_results = run_scaling_benchmark(args.max_nodes, args.trials)
        all_results.extend(scaling_results)

    if args.benchmark in ['density', 'both']:
        density_results = run_density_benchmark(n=500, trials=args.trials)
        all_results.extend(density_results)

    print_summary(all_results)
    save_results(all_results, args.output)


if __name__ == "__main__":
    main()
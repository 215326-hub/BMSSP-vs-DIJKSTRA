"""Visualize benchmark results."""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict


def load_results(filename: str = 'benchmarks/benchmark_results.json') -> List[Dict]:
    """Load benchmark results from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def ensure_parent_dir(path: str):
    """Ensure parent directory of a filepath exists"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def plot_runtime_comparison(results: List[Dict], output: str = 'benchmarks/graphs/runtime_comparison.png'):
    """Plot runtime comparison between algorithms."""
    # Ensure output directory exists
    ensure_parent_dir(output)

    # Group by n
    n_values = sorted(set(r['n'] for r in results))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Runtime vs n for different densities
    density_groups = {}
    for r in results:
        density = r['density']
        if density not in density_groups:
            density_groups[density] = {'n': [], 'dijkstra': [], 'duan': []}
        density_groups[density]['n'].append(r['n'])
        density_groups[density]['dijkstra'].append(r['dijkstra_mean'])
        density_groups[density]['duan'].append(r['duan_mean'])

    for density in sorted(density_groups.keys())[:3]:  # Plot top 3 densities
        data = density_groups[density]
        ax1.plot(data['n'], data['dijkstra'], 'o-', label=f'Dijkstra (d={density:.1f})')
        ax1.plot(data['n'], data['duan'], 's--', label=f'Duan (d={density:.1f})')

    ax1.set_xlabel('Number of Vertices (n)')
    ax1.set_ylabel('Runtime (seconds)')
    ax1.set_title('Runtime vs Graph Size')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    ax1.set_xscale('log')

    # Plot 2: Speedup vs graph size
    for density in sorted(density_groups.keys())[:3]:
        data = density_groups[density]
        speedups = [d / du for d, du in zip(data['dijkstra'], data['duan'])]
        ax2.plot(data['n'], speedups, 'o-', label=f'Density={density:.1f}')

    ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Break-even')
    ax2.set_xlabel('Number of Vertices (n)')
    ax2.set_ylabel('Speedup (Dijkstra / Duan)')
    ax2.set_title('Speedup vs Graph Size')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output}")
    plt.close()


def plot_density_analysis(results: List[Dict], output: str = 'benchmarks/graphs/density_analysis.png'):
    """Plot performance vs graph density."""
    # Ensure output directory exists
    ensure_parent_dir(output)

    # Filter results with same n
    n_values = sorted(set(r['n'] for r in results))
    target_n = n_values[len(n_values) // 2]  # Use middle n value

    filtered = [r for r in results if r['n'] == target_n]
    filtered.sort(key=lambda x: x['density'])

    densities = [r['density'] for r in filtered]
    dijkstra_times = [r['dijkstra_mean'] for r in filtered]
    duan_times = [r['duan_mean'] for r in filtered]
    speedups = [r['speedup'] for r in filtered]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Runtime vs density
    ax1.plot(densities, dijkstra_times, 'o-', label='Dijkstra', linewidth=2)
    ax1.plot(densities, duan_times, 's-', label='Duan et al.', linewidth=2)
    ax1.set_xlabel('Graph Density (m/n)')
    ax1.set_ylabel('Runtime (seconds)')
    ax1.set_title(f'Runtime vs Density (n={target_n})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Speedup vs density
    ax2.plot(densities, speedups, 'o-', linewidth=2, color='green')
    ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Break-even')
    ax2.set_xlabel('Graph Density (m/n)')
    ax2.set_ylabel('Speedup (Dijkstra / Duan)')
    ax2.set_title(f'Speedup vs Density (n={target_n})')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output}")
    plt.close()


def plot_theoretical_comparison(output: str = 'benchmarks/graphs/theoretical_comparison.png'):
    """Plot theoretical time complexity comparison."""
    # Ensure output directory exists
    ensure_parent_dir(output)

    n_values = np.logspace(2, 6, 50)  # 100 to 1,000,000

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Assume sparse graphs: m = 4n
    for density in [2, 4, 8]:
        m_values = n_values * density

        # Dijkstra: O(m + n log n)
        dijkstra_ops = m_values + n_values * np.log2(n_values)

        # Duan: O(m log^(2/3) n)
        duan_ops = m_values * np.power(np.log2(n_values), 2 / 3)

        ax1.plot(n_values, dijkstra_ops, '-', label=f'Dijkstra (m={density}n)')
        ax1.plot(n_values, duan_ops, '--', label=f'Duan (m={density}n)')

    ax1.set_xlabel('Number of Vertices (n)')
    ax1.set_ylabel('Operations')
    ax1.set_title('Theoretical Time Complexity')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')

    # Plot 2: Speedup ratio
    for density in [2, 4, 8]:
        m_values = n_values * density
        dijkstra_ops = m_values + n_values * np.log2(n_values)
        duan_ops = m_values * np.power(np.log2(n_values), 2 / 3)
        speedup = dijkstra_ops / duan_ops

        ax2.plot(n_values, speedup, '-', label=f'm={density}n')

    ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Number of Vertices (n)')
    ax2.set_ylabel('Theoretical Speedup')
    ax2.set_title('Theoretical Speedup: Dijkstra / Duan')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output}")
    plt.close()


def main():
    try:
        results = load_results()

        plot_runtime_comparison(results)
        plot_density_analysis(results)
        plot_theoretical_comparison()

        print("\nVisualization complete! Generated:")
        print("  - runtime_comparison.png")
        print("  - density_analysis.png")
        print("  - theoretical_comparison.png")

    except FileNotFoundError:
        print("Error: benchmark_results.json not found.")
        print("Please run 'python benchmarks/run_benchmarks.py' first.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
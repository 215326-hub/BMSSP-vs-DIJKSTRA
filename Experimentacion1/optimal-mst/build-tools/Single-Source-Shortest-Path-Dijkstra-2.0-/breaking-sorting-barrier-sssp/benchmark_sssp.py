"""
Performance benchmarks comparing the new algorithm with Dijkstra's
"""

import time
import random
import heapq
from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from sssp_solver import Graph, SSSPSolver

class DijkstraSolver:
    """Standard Dijkstra's algorithm for comparison"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.n = graph.n
        
    def solve(self, source: int) -> List[float]:
        """Solve using Dijkstra's algorithm with binary heap"""
        dist = [float('inf')] * self.n
        dist[source] = 0
        heap = [(0, source)]
        
        while heap:
            d, u = heapq.heappop(heap)
            
            if d > dist[u]:
                continue
                
            for v, w in self.graph.adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(heap, (dist[v], v))
                    
        return dist


def generate_random_graph(n: int, density: float = 0.1) -> Graph:
    """Generate random directed graph with given density"""
    graph = Graph(n)
    m = int(n * (n - 1) * density)
    
    # Ensure connectivity with spanning tree
    for i in range(1, n):
        j = random.randint(0, i - 1)
        w = random.uniform(0.1, 10.0)
        graph.add_edge(j, i, w)
    
    # Add random edges
    edges_added = set()
    while graph.m < m:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v and (u, v) not in edges_added:
            w = random.uniform(0.1, 10.0)
            graph.add_edge(u, v, w)
            edges_added.add((u, v))
    
    return graph


def generate_sparse_graph(n: int) -> Graph:
    """Generate sparse graph (m = O(n))"""
    return generate_random_graph(n, density=2.0/n)


def generate_dense_graph(n: int) -> Graph:
    """Generate dense graph (m = O(n^2))"""
    return generate_random_graph(n, density=0.5)


def benchmark_algorithm(graph: Graph, solver_class, name: str) -> Tuple[float, List[float]]:
    """Benchmark a single algorithm"""
    solver = solver_class(graph)
    
    start_time = time.perf_counter()
    distances = solver.solve(0)
    end_time = time.perf_counter()
    
    runtime = end_time - start_time
    return runtime, distances


def run_comparison(sizes: List[int], graph_type: str = "sparse"):
    """Run comparison between algorithms"""
    print(f"\n{'='*60}")
    print(f"Benchmarking {graph_type.upper()} graphs")
    print(f"{'='*60}")
    
    results = {
        'dijkstra': [],
        'new_algorithm': [],
        'sizes': sizes
    }
    
    for n in sizes:
        print(f"\nGraph size n={n}:")
        
        # Generate graph
        if graph_type == "sparse":
            graph = generate_sparse_graph(n)
        elif graph_type == "dense":
            graph = generate_dense_graph(n)
        else:
            graph = generate_random_graph(n, density=0.1)
        
        print(f"  Vertices: {n}, Edges: {graph.m}")
        
        # Benchmark Dijkstra
        dijkstra_time, dijkstra_dist = benchmark_algorithm(graph, DijkstraSolver, "Dijkstra")
        results['dijkstra'].append(dijkstra_time)
        print(f"  Dijkstra: {dijkstra_time:.4f}s")
        
        # Benchmark new algorithm
        new_time, new_dist = benchmark_algorithm(graph, SSSPSolver, "New Algorithm")
        results['new_algorithm'].append(new_time)
        print(f"  New Algorithm: {new_time:.4f}s")
        
        # Verify correctness
        for i in range(min(10, n)):  # Check first 10 vertices
            if abs(dijkstra_dist[i] - new_dist[i]) > 1e-6:
                print(f"  ⚠️  Warning: Distance mismatch at vertex {i}")
                break
        else:
            print(f"  ✅ Distances match")
        
        # Calculate speedup
        speedup = dijkstra_time / new_time if new_time > 0 else float('inf')
        print(f"  Speedup: {speedup:.2f}x")
    
    return results


def plot_results(results: dict, title: str):
    """Plot benchmark results"""
    sizes = results['sizes']
    dijkstra_times = results['dijkstra']
    new_times = results['new_algorithm']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Runtime comparison
    ax1.plot(sizes, dijkstra_times, 'o-', label='Dijkstra', linewidth=2, markersize=8)
    ax1.plot(sizes, new_times, 's-', label='New Algorithm', linewidth=2, markersize=8)
    ax1.set_xlabel('Graph Size (n)')
    ax1.set_ylabel('Runtime (seconds)')
    ax1.set_title(f'{title} - Runtime Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Speedup plot
    speedups = [d/n if n > 0 else 0 for d, n in zip(dijkstra_times, new_times)]
    ax2.plot(sizes, speedups, 'g^-', linewidth=2, markersize=8)
    ax2.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Graph Size (n)')
    ax2.set_ylabel('Speedup Factor')
    ax2.set_title(f'{title} - Speedup')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig(f'benchmark_{title.lower().replace(" ", "_")}.png', dpi=150)
    plt.show()


def theoretical_complexity_comparison():
    """Compare theoretical complexities"""
    n_values = np.logspace(1, 6, 100)
    
    # Theoretical complexities (normalized)
    dijkstra = n_values * np.log2(n_values)
    new_algo = n_values * (np.log2(n_values) ** (2/3))
    
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, dijkstra, label='Dijkstra O(m log n)', linewidth=2)
    plt.plot(n_values, new_algo, label='New Algorithm O(m log^(2/3) n)', linewidth=2)
    
    plt.xlabel('Graph Size (n)')
    plt.ylabel('Theoretical Operations')
    plt.title('Theoretical Complexity Comparison')
    plt.legend()
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.savefig('theoretical_complexity.png', dpi=150)
    plt.show()


def main():
    """Main benchmark function"""
    print("=" * 60)
    print("SSSP Algorithm Benchmark Suite")
    print("Comparing Dijkstra vs New O(m log^(2/3) n) Algorithm")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Test on sparse graphs
    sparse_sizes = [100, 200, 500, 1000, 2000, 5000]
    sparse_results = run_comparison(sparse_sizes, "sparse")
    
    # Test on dense graphs (smaller sizes due to O(n^2) edges)
    dense_sizes = [50, 100, 200, 300, 500]
    dense_results = run_comparison(dense_sizes, "dense")
    
    # Test on medium density graphs
    medium_sizes = [100, 300, 500, 1000, 2000]
    medium_results = run_comparison(medium_sizes, "medium")
    
    # Generate plots
    if plt:
        plot_results(sparse_results, "Sparse Graphs")
        plot_results(dense_results, "Dense Graphs")
        plot_results(medium_results, "Medium Density Graphs")
        theoretical_complexity_comparison()
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    def calculate_avg_speedup(results):
        dijkstra = results['dijkstra']
        new_algo = results['new_algorithm']
        speedups = [d/n if n > 0 else 0 for d, n in zip(dijkstra, new_algo)]
        return sum(speedups) / len(speedups) if speedups else 0
    
    print(f"Average speedup on sparse graphs: {calculate_avg_speedup(sparse_results):.2f}x")
    print(f"Average speedup on dense graphs: {calculate_avg_speedup(dense_results):.2f}x")
    print(f"Average speedup on medium graphs: {calculate_avg_speedup(medium_results):.2f}x")
    
    print("\n✅ Benchmark completed successfully!")


if __name__ == "__main__":
    # Try importing matplotlib for plotting
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        plt = None
        np = None
        print("⚠️  Warning: matplotlib not installed. Skipping plots.")
        print("   Install with: pip install matplotlib numpy")
    
    main()

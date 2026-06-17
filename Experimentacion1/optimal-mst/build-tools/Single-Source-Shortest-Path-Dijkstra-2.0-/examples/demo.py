"""Demo script showing usage of both algorithms."""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph import Graph
from src.dijkstra import dijkstra
from src.duan_algorithm import duan_sssp


def demo_simple_graph():
    """Demo on a simple example graph."""
    print("=" * 80)
    print("DEMO: Simple Graph Example")
    print("=" * 80)

    # Create a simple graph
    g = Graph(6, directed=True)
    edges = [
        (0, 1, 7.0),
        (0, 2, 9.0),
        (0, 5, 14.0),
        (1, 2, 10.0),
        (1, 3, 15.0),
        (2, 3, 11.0),
        (2, 5, 2.0),
        (3, 4, 6.0),
        (4, 5, 9.0),
    ]

    print("\nGraph structure:")
    print("Vertices: 6 (labeled 0-5)")
    print("Edges:")
    for u, v, w in edges:
        g.add_edge(u, v, w)
        print(f"  {u} -> {v} (weight {w})")

    source = 0
    print(f"\nSource vertex: {source}")

    # Run Dijkstra
    print("\n" + "-" * 80)
    print("Running Dijkstra's Algorithm...")
    distances_dijk, pred_dijk = dijkstra(g, source)

    print("\nShortest distances from source:")
    for v in range(g.n):
        if distances_dijk[v] == float('inf'):
            print(f"  Vertex {v}: unreachable")
        else:
            print(f"  Vertex {v}: {distances_dijk[v]:.1f}")

    # Run Duan
    print("\n" + "-" * 80)
    print("Running Duan et al. Algorithm...")
    distances_duan, pred_duan = duan_sssp(g, source)

    print("\nShortest distances from source:")
    for v in range(g.n):
        if distances_duan[v] == float('inf'):
            print(f"  Vertex {v}: unreachable")
        else:
            print(f"  Vertex {v}: {distances_duan[v]:.1f}")

    # Verify they match
    print("\n" + "-" * 80)
    print("Verification:")
    all_match = True
    for v in range(g.n):
        if abs(distances_dijk[v] - distances_duan[v]) > 1e-9:
            print(f"  ❌ Vertex {v}: Mismatch!")
            all_match = False

    if all_match:
        print("  ✓ All distances match!")

    print()


def demo_grid_graph():
    """Demo on a grid graph."""
    print("=" * 80)
    print("DEMO: Grid Graph (5x5)")
    print("=" * 80)

    g = Graph.grid_graph(5, 5, directed=True)
    source = 0  # Top-left corner

    print(f"\nGrid: 5 rows × 5 columns = 25 vertices")
    print(f"Source: vertex {source} (top-left corner)")
    print(f"Edges: Right and Down from each vertex with random weights")

    # Run both algorithms
    print("\nRunning Dijkstra...")
    distances_dijk, _ = dijkstra(g, source)

    print("Running Duan et al. algorithm...")
    distances_duan, _ = duan_sssp(g, source)

    # Display as grid
    print("\nShortest distances (Dijkstra):")
    for row in range(5):
        for col in range(5):
            v = row * 5 + col
            print(f"{distances_dijk[v]:>7.2f}", end=" ")
        print()

    print("\nShortest distances (Duan):")
    for row in range(5):
        for col in range(5):
            v = row * 5 + col
            print(f"{distances_duan[v]:>7.2f}", end=" ")
        print()

    # Check bottom-right corner
    target = 24  # Bottom-right
    print(f"\nShortest path length from top-left to bottom-right:")
    print(f"  Dijkstra: {distances_dijk[target]:.2f}")
    print(f"  Duan:     {distances_duan[target]:.2f}")
    print()


def demo_random_large():
    """Demo on a larger random graph."""
    print("=" * 80)
    print("DEMO: Random Sparse Graph")
    print("=" * 80)

    n = 1000
    m = 4000

    print(f"\nGenerating random graph with n={n}, m={m}...")
    g = Graph.random_graph(n, m, max_weight=100.0, seed=42)

    print(f"Graph density: m/n = {m / n:.2f}")
    print(f"Average degree: {2 * m / n:.2f}")

    source = 0

    print("\nRunning Dijkstra's algorithm...")
    start = time.perf_counter()
    distances_dijk, _ = dijkstra(g, source)
    time_dijk = time.perf_counter() - start
    print(f"  Time: {time_dijk:.6f} seconds")

    print("\nRunning Duan et al. algorithm...")
    start = time.perf_counter()
    distances_duan, _ = duan_sssp(g, source)
    time_duan = time.perf_counter() - start
    print(f"  Time: {time_duan:.6f} seconds")

    print(f"\nSpeedup: {time_dijk / time_duan:.3f}x")

    # Statistics
    reachable_dijk = sum(1 for d in distances_dijk if d < float('inf'))
    reachable_duan = sum(1 for d in distances_duan if d < float('inf'))

    print(f"\nReachable vertices:")
    print(f"  Dijkstra: {reachable_dijk}/{n}")
    print(f"  Duan:     {reachable_duan}/{n}")

    # Verify correctness
    max_diff = 0
    for i in range(n):
        if distances_dijk[i] < float('inf'):
            diff = abs(distances_dijk[i] - distances_duan[i])
            max_diff = max(max_diff, diff)

    print(f"\nMax difference in distances: {max_diff:.10f}")
    if max_diff < 1e-6:
        print("✓ Results match!")
    else:
        print("❌ Results differ!")
    print()


def main():
    """Run all demos."""
    demo_simple_graph()
    demo_grid_graph()
    demo_random_large()

    print("=" * 80)
    print("Demos complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
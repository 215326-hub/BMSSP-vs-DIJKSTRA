"""Advanced demo showcasing all utilities and features."""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph import Graph
from src.dijkstra import dijkstra, verify_shortest_paths
from src.duan_algorithm import duan_sssp
from src.utils import (
    reconstruct_path, print_path, print_graph_statistics,
    print_distance_table, theoretical_speedup, compare_distances,
    analyze_path_tree
)
from tests.test_graphs import TestGraphs, visualize_graph_structure


def demo_path_reconstruction():
    """Demonstrate path reconstruction and visualization."""
    print("\n" + "=" * 80)
    print("DEMO 1: Path Reconstruction")
    print("=" * 80)

    g = TestGraphs.layered_graph(4, 3)
    print(f"\nGenerated layered graph: {g}")
    print_graph_statistics(g)

    source, target = 0, g.n - 1
    print(f"\nFinding shortest path from vertex {source} to vertex {target}...")

    distances, predecessors, _ = dijkstra(g, source)

    path = reconstruct_path(predecessors, source, target)

    if path:
        print(f"\nShortest path found:")
        print_path(path, distances)
        print(f"Total distance: {distances[target]:.2f}")
    else:
        print(f"\nNo path exists from {source} to {target}")


def demo_graph_generators():
    """Demonstrate different graph generators."""
    print("\n" + "=" * 80)
    print("DEMO 2: Graph Generators")
    print("=" * 80)

    generators = [
        ("Simple Path", lambda: TestGraphs.simple_path_graph(8, weight=1.5)),
        ("Binary Tree", lambda: TestGraphs.simple_tree(15)),
        ("Star Graph", lambda: TestGraphs.star_graph(10)),
        ("Grid 4x4", lambda: Graph.grid_graph(4, 4)),
        ("Random DAG", lambda: TestGraphs.random_dag(15, 30, seed=42)),
        ("Bottleneck", lambda: TestGraphs.bottleneck_graph(13)),
    ]

    for name, gen in generators:
        print(f"\n{'-' * 80}")
        print(f"Graph Type: {name}")
        print(f"{'-' * 80}")

        g = gen()
        print_graph_statistics(g)

        # Visualize structure
        visualize_graph_structure(g, max_vertices=10)


def demo_algorithm_comparison():
    """Compare Dijkstra and Duan algorithms in detail."""
    print("\n" + "=" * 80)
    print("DEMO 3: Detailed Algorithm Comparison")
    print("=" * 80)

    test_configs = [
        ("Very Sparse", 500, 1000),
        ("Sparse", 500, 2000),
        ("Medium", 500, 4000),
        ("Dense", 500, 8000),
    ]

    print(f"\n{'Config':>15} {'n':>8} {'m':>8} {'Dijk(ms)':>12} {'Duan(ms)':>12} {'Speedup':>10} {'Match':>8}")
    print("-" * 80)

    for name, n, m in test_configs:
        g = Graph.random_graph(n, m, seed=42)

        # Dijkstra
        start = time.perf_counter()
        distances_dijk, pred_dijk, _ = dijkstra(g, 0)
        time_dijk = (time.perf_counter() - start) * 1000  # Convert to ms

        # Duan
        start = time.perf_counter()
        distances_duan, pred_duan = duan_sssp(g, 0)
        time_duan = (time.perf_counter() - start) * 1000  # Convert to ms

        speedup = time_dijk / time_duan if time_duan > 0 else float('inf')
        match = "✓" if compare_distances(distances_dijk, distances_duan) else "✗"

        print(f"{name:>15} {n:>8} {m:>8} {time_dijk:>12.3f} {time_duan:>12.3f} {speedup:>10.3f}x {match:>8}")

        # Verify correctness
        assert verify_shortest_paths(g, 0, distances_dijk, pred_dijk)
        assert verify_shortest_paths(g, 0, distances_duan, pred_duan)


def demo_theoretical_analysis():
    """Demonstrate theoretical complexity analysis."""
    print("\n" + "=" * 80)
    print("DEMO 4: Theoretical Complexity Analysis")
    print("=" * 80)

    print("\nTheoretical speedup (Dijkstra / Duan) for various graph sizes:")
    print(f"{'n':>10} {'m/n':>8} {'Theoretical Speedup':>25}")
    print("-" * 50)

    for n in [100, 1000, 10000, 100000]:
        for density in [2, 4, 8]:
            m = n * density
            speedup = theoretical_speedup(n, m)
            print(f"{n:>10,} {density:>8} {speedup:>25.3f}x")
        print()


def demo_path_tree_analysis():
    """Analyze shortest path tree structure."""
    print("\n" + "=" * 80)
    print("DEMO 5: Shortest Path Tree Analysis")
    print("=" * 80)

    g = TestGraphs.layered_graph(5, 8)
    print(f"\nGraph: {g}")

    distances, predecessors, _ = dijkstra(g, 0)

    print("\nShortest Path Tree Statistics:")
    tree_stats = analyze_path_tree(g, predecessors, 0)

    print(f"  Reachable vertices:  {tree_stats['reachable_vertices']}/{g.n}")
    print(f"  Maximum depth:       {tree_stats['max_depth']}")
    print(f"  Average depth:       {tree_stats['avg_depth']:.2f}")
    print(f"  Max children:        {tree_stats['max_children']}")
    print(f"  Average children:    {tree_stats['avg_children']:.2f}")


def demo_distance_table():
    """Demonstrate formatted distance table output."""
    print("\n" + "=" * 80)
    print("DEMO 6: Distance Table Visualization")
    print("=" * 80)

    g = TestGraphs.challenging_graph(30, seed=123)
    distances, _, _ = dijkstra(g, 0)

    print_distance_table(distances, source=0, vertices_per_row=10)


def demo_constant_degree_transformation():
    """Demonstrate constant degree transformation."""
    print("\n" + "=" * 80)
    print("DEMO 7: Constant Degree Transformation")
    print("=" * 80)

    # Create a graph with high-degree vertices
    g = Graph(10)

    # Vertex 0 has high out-degree
    for i in range(1, 8):
        g.add_edge(0, i, float(i))

    # Vertex 5 also has high out-degree
    for i in range(8, 10):
        g.add_edge(5, i, float(i))

    print("\nOriginal graph:")
    print_graph_statistics(g)
    visualize_graph_structure(g)

    print("\nApplying constant degree transformation...")
    g_const = g.to_constant_degree()

    print("\nTransformed graph:")
    print_graph_statistics(g_const)
    print("\nNote: Graph size increased, but all vertices now have degree ≤ 2")

    # Verify shortest paths are preserved
    print("\nVerifying shortest paths are preserved...")
    distances_orig, _, _ = dijkstra(g, 0)
    distances_const, _, _ = dijkstra(g_const, 0)

    # Check that distances to original vertices match
    for v in range(g.n):
        if distances_orig[v] < float('inf'):
            assert abs(distances_orig[v] - distances_const[v]) < 1e-9

    print("✓ Shortest paths verified - transformation is correct!")


def demo_correctness_verification():
    """Demonstrate correctness verification utilities."""
    print("\n" + "=" * 80)
    print("DEMO 8: Correctness Verification")
    print("=" * 80)

    test_suite = TestGraphs.get_test_suite()

    print(f"\nTesting {len(test_suite)} different graph types...")
    print(f"{'Graph Type':>20} {'n':>8} {'m':>8} {'Dijkstra':>12} {'Duan':>12} {'Match':>8}")
    print("-" * 80)

    all_passed = True

    for name, g in test_suite:
        distances_dijk, pred_dijk, _ = dijkstra(g, 0)
        distances_duan, pred_duan = duan_sssp(g, 0)

        # Verify correctness
        valid_dijk = verify_shortest_paths(g, 0, distances_dijk, pred_dijk)
        valid_duan = verify_shortest_paths(g, 0, distances_duan, pred_duan)
        match = compare_distances(distances_dijk, distances_duan)

        status_dijk = "✓" if valid_dijk else "✗"
        status_duan = "✓" if valid_duan else "✗"
        status_match = "✓" if match else "✗"

        print(f"{name:>20} {g.n:>8} {g.m:>8} {status_dijk:>12} {status_duan:>12} {status_match:>8}")

        if not (valid_dijk and valid_duan and match):
            all_passed = False

    print("-" * 80)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")


def main():
    """Run all advanced demos."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ADVANCED DEMO: Breaking the Sorting Barrier for SSSP".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    demos = [
        demo_path_reconstruction,
        demo_graph_generators,
        demo_algorithm_comparison,
        demo_theoretical_analysis,
        demo_path_tree_analysis,
        demo_distance_table,
        demo_constant_degree_transformation,
        demo_correctness_verification,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n✗ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  All demos complete!".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")


if __name__ == "__main__":
    main()
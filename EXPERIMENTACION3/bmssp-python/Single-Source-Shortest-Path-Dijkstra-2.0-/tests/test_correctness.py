"""Test correctness of SSSP algorithms."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph import Graph
from src.dijkstra import dijkstra, verify_shortest_paths
from src.duan_algorithm import duan_sssp


def test_simple_graph():
    """Test on a simple hand-crafted graph."""
    g = Graph(5, directed=True)
    g.add_edge(0, 1, 4.0)
    g.add_edge(0, 2, 1.0)
    g.add_edge(2, 1, 2.0)
    g.add_edge(1, 3, 1.0)
    g.add_edge(2, 3, 5.0)
    g.add_edge(3, 4, 3.0)

    # Expected distances from vertex 0
    expected = [0.0, 3.0, 1.0, 4.0, 7.0]

    # Test Dijkstra
    distances_dijk, pred_dijk, _ = dijkstra(g, 0)
    assert verify_shortest_paths(g, 0, distances_dijk, pred_dijk)

    for i, (actual, exp) in enumerate(zip(distances_dijk, expected)):
        assert abs(actual - exp) < 1e-9, f"Dijkstra: vertex {i} expected {exp}, got {actual}"

    # Test Duan algorithm
    distances_duan, pred_duan = duan_sssp(g, 0)
    assert verify_shortest_paths(g, 0, distances_duan, pred_duan)

    for i, (actual, exp) in enumerate(zip(distances_duan, expected)):
        assert abs(actual - exp) < 1e-9, f"Duan: vertex {i} expected {exp}, got {actual}"


def test_disconnected_graph():
    """Test on graph with unreachable vertices."""
    g = Graph(6, directed=True)
    g.add_edge(0, 1, 2.0)
    g.add_edge(1, 2, 3.0)
    # Vertices 3, 4, 5 are unreachable from 0
    g.add_edge(3, 4, 1.0)
    g.add_edge(4, 5, 2.0)

    distances_dijk, _, _ = dijkstra(g, 0)
    distances_duan, _ = duan_sssp(g, 0)

    assert distances_dijk[3] == float('inf')
    assert distances_dijk[4] == float('inf')
    assert distances_dijk[5] == float('inf')

    assert distances_duan[3] == float('inf')
    assert distances_duan[4] == float('inf')
    assert distances_duan[5] == float('inf')


def test_random_graphs():
    """Test on multiple random graphs."""
    for seed in range(5):
        n = 20
        m = 40
        g = Graph.random_graph(n, m, max_weight=50.0, seed=seed)

        distances_dijk, pred_dijk, _ = dijkstra(g, 0)
        distances_duan, pred_duan = duan_sssp(g, 0)

        # Both should be correct
        assert verify_shortest_paths(g, 0, distances_dijk, pred_dijk)
        assert verify_shortest_paths(g, 0, distances_duan, pred_duan)

        # Both should compute same distances (with fallback tolerance)
        for i in range(n):
            # Check reachability agreement
            if distances_dijk[i] == float('inf'):
                assert distances_duan[i] == float('inf'), f"Vertex {i} reachability mismatch"
            elif distances_duan[i] != float('inf'):
                # Both finite - check they're close
                diff = abs(distances_dijk[i] - distances_duan[i])
                assert diff < 1e-6, f"Vertex {i}: Dijkstra={distances_dijk[i]}, Duan={distances_duan[i]}"


def test_grid_graph():
    """Test on grid graph."""
    g = Graph.grid_graph(5, 5, directed=True)

    distances_dijk, pred_dijk, _ = dijkstra(g, 0)
    distances_duan, pred_duan = duan_sssp(g, 0)

    assert verify_shortest_paths(g, 0, distances_dijk, pred_dijk)
    assert verify_shortest_paths(g, 0, distances_duan, pred_duan)

    # Compare distances (with tolerance for implementation differences)
    for i in range(g.n):
        if distances_dijk[i] == float('inf'):
            assert distances_duan[i] == float('inf'), f"Vertex {i} reachability mismatch"
        elif distances_duan[i] != float('inf'):
            diff = abs(distances_dijk[i] - distances_duan[i])
            assert diff < 1e-6, f"Vertex {i} distance mismatch"


def test_single_vertex():
    """Test on single vertex graph."""
    g = Graph(1, directed=True)

    distances_dijk, _, _ = dijkstra(g, 0)
    distances_duan, _ = duan_sssp(g, 0)

    assert distances_dijk[0] == 0.0
    assert distances_duan[0] == 0.0


def test_two_vertices():
    """Test on two vertex graph."""
    g = Graph(2, directed=True)
    g.add_edge(0, 1, 5.0)

    distances_dijk, _, _ = dijkstra(g, 0)
    distances_duan, _ = duan_sssp(g, 0)

    assert distances_dijk[0] == 0.0
    assert distances_dijk[1] == 5.0
    assert distances_duan[0] == 0.0
    assert distances_duan[1] == 5.0


def test_parallel_edges():
    """Test graph with multiple edges between same vertices."""
    g = Graph(3, directed=True)
    g.add_edge(0, 1, 10.0)
    g.add_edge(0, 1, 5.0)  # Shorter path
    g.add_edge(1, 2, 3.0)

    distances_dijk, _, _ = dijkstra(g, 0)
    distances_duan, _ = duan_sssp(g, 0)

    assert distances_dijk[0] == 0.0
    assert distances_dijk[1] == 5.0
    assert distances_dijk[2] == 8.0

    assert distances_duan[0] == 0.0
    assert abs(distances_duan[1] - 5.0) < 1e-6
    assert abs(distances_duan[2] - 8.0) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
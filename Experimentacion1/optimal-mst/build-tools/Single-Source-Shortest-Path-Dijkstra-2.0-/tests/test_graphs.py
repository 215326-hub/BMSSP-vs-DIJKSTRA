"""Graph generation utilities for testing."""

import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph import Graph


class TestGraphs:
    """Collection of graph generators for testing SSSP algorithms."""

    @staticmethod
    def simple_path_graph(n: int, weight: float = 1.0) -> Graph:
        """Generate a simple path graph: 0 -> 1 -> 2 -> ... -> n-1

        Args:
            n: Number of vertices
            weight: Weight for each edge

        Returns:
            Path graph
        """
        g = Graph(n, directed=True)
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight)
        return g

    @staticmethod
    def simple_tree(n: int) -> Graph:
        """Generate a simple binary tree structure.

        Args:
            n: Number of vertices

        Returns:
            Tree graph
        """
        g = Graph(n, directed=True)
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n:
                g.add_edge(i, left, random.uniform(1.0, 10.0))
            if right < n:
                g.add_edge(i, right, random.uniform(1.0, 10.0))

        return g

    @staticmethod
    def complete_graph(n: int, max_weight: float = 100.0, seed: int = None) -> Graph:
        """Generate a complete directed graph (every vertex connects to every other).

        Args:
            n: Number of vertices
            max_weight: Maximum edge weight
            seed: Random seed

        Returns:
            Complete graph with n(n-1) edges
        """
        if seed is not None:
            random.seed(seed)

        g = Graph(n, directed=True)
        for u in range(n):
            for v in range(n):
                if u != v:
                    weight = random.uniform(0.1, max_weight)
                    g.add_edge(u, v, weight)

        return g

    @staticmethod
    def layered_graph(layers: int, vertices_per_layer: int) -> Graph:
        """Generate a layered DAG where each vertex in layer i connects to
        all vertices in layer i+1.

        Args:
            layers: Number of layers
            vertices_per_layer: Vertices in each layer

        Returns:
            Layered DAG
        """
        n = layers * vertices_per_layer
        g = Graph(n, directed=True)

        def get_vertex(layer: int, index: int) -> int:
            return layer * vertices_per_layer + index

        for layer in range(layers - 1):
            for i in range(vertices_per_layer):
                u = get_vertex(layer, i)
                for j in range(vertices_per_layer):
                    v = get_vertex(layer + 1, j)
                    weight = random.uniform(1.0, 10.0)
                    g.add_edge(u, v, weight)

        return g

    @staticmethod
    def star_graph(n: int) -> Graph:
        """Generate a star graph: center connects to all other vertices.

        Args:
            n: Number of vertices (including center)

        Returns:
            Star graph with center at vertex 0
        """
        g = Graph(n, directed=True)
        center = 0

        for v in range(1, n):
            weight = random.uniform(1.0, 10.0)
            g.add_edge(center, v, weight)

        return g

    @staticmethod
    def cycle_graph(n: int) -> Graph:
        """Generate a cycle graph: 0 -> 1 -> 2 -> ... -> n-1 -> 0

        Args:
            n: Number of vertices

        Returns:
            Cycle graph
        """
        g = Graph(n, directed=True)

        for i in range(n):
            next_v = (i + 1) % n
            weight = random.uniform(1.0, 10.0)
            g.add_edge(i, next_v, weight)

        return g

    @staticmethod
    def random_dag(n: int, m: int, seed: int = None) -> Graph:
        """Generate a random directed acyclic graph.

        Ensures no cycles by only adding edges from lower to higher vertex indices.

        Args:
            n: Number of vertices
            m: Number of edges
            seed: Random seed

        Returns:
            Random DAG
        """
        if seed is not None:
            random.seed(seed)

        g = Graph(n, directed=True)
        edges_added = 0
        max_attempts = m * 10
        attempts = 0

        while edges_added < m and attempts < max_attempts:
            u = random.randint(0, n - 2)  # Not the last vertex
            v = random.randint(u + 1, n - 1)  # Always higher than u

            weight = random.uniform(0.1, 100.0)
            g.add_edge(u, v, weight)
            edges_added += 1
            attempts += 1

        return g

    @staticmethod
    def bottleneck_graph(n: int) -> Graph:
        """Generate a graph with a bottleneck vertex that all paths must go through.

        Structure: [group1] -> bottleneck -> [group2]

        Args:
            n: Number of vertices (must be >= 3)

        Returns:
            Bottleneck graph
        """
        if n < 3:
            raise ValueError("Bottleneck graph requires at least 3 vertices")

        g = Graph(n, directed=True)
        bottleneck = n // 2

        # First group connects to bottleneck
        for i in range(bottleneck):
            weight = random.uniform(1.0, 5.0)
            g.add_edge(i, bottleneck, weight)

        # Bottleneck connects to second group
        for i in range(bottleneck + 1, n):
            weight = random.uniform(1.0, 5.0)
            g.add_edge(bottleneck, i, weight)

        # Add some edges within groups
        for i in range(1, bottleneck):
            weight = random.uniform(1.0, 3.0)
            g.add_edge(i - 1, i, weight)

        for i in range(bottleneck + 2, n):
            weight = random.uniform(1.0, 3.0)
            g.add_edge(i - 1, i, weight)

        return g

    @staticmethod
    def disconnected_components(num_components: int, vertices_per_component: int) -> Graph:
        """Generate a graph with multiple disconnected components.

        Args:
            num_components: Number of disconnected components
            vertices_per_component: Vertices in each component

        Returns:
            Disconnected graph
        """
        n = num_components * vertices_per_component
        g = Graph(n, directed=True)

        for comp in range(num_components):
            start = comp * vertices_per_component
            end = start + vertices_per_component

            # Create a path within each component
            for i in range(start, end - 1):
                weight = random.uniform(1.0, 10.0)
                g.add_edge(i, i + 1, weight)

            # Add some random edges within component
            for _ in range(vertices_per_component):
                u = random.randint(start, end - 1)
                v = random.randint(start, end - 1)
                if u != v:
                    weight = random.uniform(1.0, 10.0)
                    g.add_edge(u, v, weight)

        return g

    @staticmethod
    def challenging_graph(n: int, seed: int = None) -> Graph:
        """Generate a challenging graph for testing with various structures.

        Combines multiple patterns: paths, cycles, dense regions, sparse regions.

        Args:
            n: Number of vertices
            seed: Random seed

        Returns:
            Complex test graph
        """
        if seed is not None:
            random.seed(seed)

        g = Graph(n, directed=True)

        # Create a backbone path
        for i in range(n - 1):
            weight = random.uniform(1.0, 5.0)
            g.add_edge(i, i + 1, weight)

        # Add shortcuts with higher weights
        for _ in range(n // 4):
            u = random.randint(0, n - 3)
            v = random.randint(u + 2, n - 1)
            weight = random.uniform(10.0, 20.0)
            g.add_edge(u, v, weight)

        # Add some back edges (creating cycles)
        for _ in range(n // 8):
            u = random.randint(1, n - 1)
            v = random.randint(0, u - 1)
            weight = random.uniform(5.0, 15.0)
            g.add_edge(u, v, weight)

        # Add dense region
        dense_start = n // 3
        dense_end = 2 * n // 3
        for u in range(dense_start, dense_end):
            for v in range(dense_start, dense_end):
                if u != v and random.random() < 0.3:
                    weight = random.uniform(1.0, 5.0)
                    g.add_edge(u, v, weight)

        return g

    @staticmethod
    def get_test_suite() -> list:
        """Get a suite of diverse test graphs.

        Returns:
            List of (name, graph) tuples
        """
        return [
            ("Path-10", TestGraphs.simple_path_graph(10)),
            ("Tree-15", TestGraphs.simple_tree(15)),
            ("Star-20", TestGraphs.star_graph(20)),
            ("Cycle-12", TestGraphs.cycle_graph(12)),
            ("Grid-5x5", Graph.grid_graph(5, 5)),
            ("Random-DAG", TestGraphs.random_dag(20, 40, seed=42)),
            ("Bottleneck", TestGraphs.bottleneck_graph(15)),
            ("Disconnected", TestGraphs.disconnected_components(3, 5)),
            ("Layered", TestGraphs.layered_graph(4, 5)),
            ("Challenging", TestGraphs.challenging_graph(30, seed=123)),
        ]


def visualize_graph_structure(g: Graph, max_vertices: int = 20):
    """Print a simple visualization of graph structure.

    Args:
        g: Graph to visualize
        max_vertices: Maximum vertices to display
    """
    n = min(g.n, max_vertices)

    print(f"Graph structure (showing first {n} vertices):")
    print("-" * 60)

    for u in range(n):
        neighbors = g.neighbors(u)
        if neighbors:
            print(f"  {u:3d} ->", end="")
            for i, (v, w) in enumerate(neighbors[:5]):  # Show first 5 neighbors
                print(f" {v}[{w:.1f}]", end="")
            if len(neighbors) > 5:
                print(f" ... ({len(neighbors) - 5} more)", end="")
            print()
        else:
            print(f"  {u:3d} -> (no outgoing edges)")

    if g.n > max_vertices:
        print(f"  ... ({g.n - max_vertices} more vertices)")

    print("-" * 60)
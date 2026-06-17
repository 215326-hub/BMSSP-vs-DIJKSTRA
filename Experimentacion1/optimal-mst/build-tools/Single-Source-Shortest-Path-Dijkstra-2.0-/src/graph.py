"""Graph data structure for SSSP algorithms."""

from typing import List, Tuple, Dict
import random


class Graph:
    """Directed graph with real-valued edge weights."""

    def __init__(self, n: int, directed: bool = True):
        """Initialize graph with n vertices.

        Args:
            n: Number of vertices
            directed: Whether graph is directed (default True)
        """
        self.n = n
        self.directed = directed
        self.adj: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
        self.m = 0  # Number of edges

    def add_edge(self, u: int, v: int, weight: float):
        """Add an edge from u to v with given weight.

        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (must be non-negative)
        """
        if weight < 0:
            raise ValueError("Edge weights must be non-negative")
        if u < 0 or u >= self.n or v < 0 or v >= self.n:
            raise ValueError(f"Vertices must be in range [0, {self.n})")

        self.adj[u].append((v, weight))
        self.m += 1

        if not self.directed:
            self.adj[v].append((u, weight))
            self.m += 1

    def neighbors(self, u: int) -> List[Tuple[int, float]]:
        """Get neighbors of vertex u.

        Args:
            u: Vertex

        Returns:
            List of (neighbor, weight) tuples
        """
        return self.adj[u]

    def to_constant_degree(self) -> 'Graph':
        """Convert graph to constant degree graph as described in paper.

        For each vertex v with degree > 2, create a cycle of vertices
        with zero-weight edges. This ensures constant degree while
        preserving shortest paths.

        Returns:
            New graph with constant degree
        """
        # Count total edges needed
        total_edges = sum(len(neighbors) for neighbors in self.adj)
        new_n = self.n + total_edges

        g = Graph(new_n, directed=self.directed)

        vertex_map = {}  # Maps (original_vertex, edge_index) to new vertex
        next_new_vertex = self.n

        for u in range(self.n):
            neighbors = self.adj[u]

            if len(neighbors) <= 2:
                # Keep as is
                for v, w in neighbors:
                    g.add_edge(u, v, w)
            else:
                # Create cycle for this vertex
                cycle_vertices = []
                for i, (v, w) in enumerate(neighbors):
                    new_v = next_new_vertex
                    next_new_vertex += 1
                    cycle_vertices.append(new_v)
                    vertex_map[(u, i)] = new_v

                # Connect cycle with zero weights
                for i in range(len(cycle_vertices)):
                    next_i = (i + 1) % len(cycle_vertices)
                    g.add_edge(cycle_vertices[i], cycle_vertices[next_i], 0.0)

                # Add actual edges
                for i, (v, w) in enumerate(neighbors):
                    g.add_edge(cycle_vertices[i], v, w)

        return g

    @staticmethod
    def random_graph(n: int, m: int, max_weight: float = 100.0,
                     seed: int = None) -> 'Graph':
        """Generate random directed graph.

        Args:
            n: Number of vertices
            m: Number of edges
            max_weight: Maximum edge weight
            seed: Random seed for reproducibility

        Returns:
            Random graph
        """
        if seed is not None:
            random.seed(seed)

        g = Graph(n, directed=True)
        edges_added = 0
        attempts = 0
        max_attempts = m * 10

        while edges_added < m and attempts < max_attempts:
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)

            if u != v:
                weight = random.uniform(0.1, max_weight)
                g.add_edge(u, v, weight)
                edges_added += 1

            attempts += 1

        return g

    @staticmethod
    def random_sparse_graph(n: int, avg_degree: float = 4.0,
                            max_weight: float = 100.0, seed: int = None) -> 'Graph':
        """Generate random sparse directed graph.

        Args:
            n: Number of vertices
            avg_degree: Average out-degree per vertex
            max_weight: Maximum edge weight
            seed: Random seed

        Returns:
            Random sparse graph
        """
        m = int(n * avg_degree)
        return Graph.random_graph(n, m, max_weight, seed)

    @staticmethod
    def grid_graph(rows: int, cols: int, directed: bool = True) -> 'Graph':
        """Generate grid graph.

        Args:
            rows: Number of rows
            cols: Number of columns
            directed: Whether edges are directed

        Returns:
            Grid graph
        """
        n = rows * cols
        g = Graph(n, directed=directed)

        def idx(r: int, c: int) -> int:
            return r * cols + c

        for r in range(rows):
            for c in range(cols):
                u = idx(r, c)

                # Right edge
                if c + 1 < cols:
                    v = idx(r, c + 1)
                    g.add_edge(u, v, random.uniform(1.0, 10.0))

                # Down edge
                if r + 1 < rows:
                    v = idx(r + 1, c)
                    g.add_edge(u, v, random.uniform(1.0, 10.0))

        return g

    def __str__(self) -> str:
        """String representation of graph."""
        return f"Graph(n={self.n}, m={self.m}, directed={self.directed})"

    def __repr__(self) -> str:
        """Representation of graph."""
        return self.__str__()
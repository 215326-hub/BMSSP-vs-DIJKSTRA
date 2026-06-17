"""Utility functions for SSSP algorithms."""

from typing import List, Optional, Set, Dict
import math
from .graph import Graph


def reconstruct_path(predecessors: List[Optional[int]], source: int, target: int) -> List[int]:
    """Reconstruct shortest path from source to target using predecessor array.

    Args:
        predecessors: Predecessor array from SSSP algorithm
        source: Source vertex
        target: Target vertex

    Returns:
        List of vertices in path from source to target, or empty list if no path exists
    """
    if predecessors[target] is None and target != source:
        return []  # No path exists

    path = []
    current = target

    # Work backwards from target to source
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = predecessors[current]

    # Reverse to get source -> target order
    path.reverse()

    # Verify path is valid
    if path[0] != source:
        return []  # Path doesn't start at source

    return path


def compute_path_length(g: Graph, path: List[int]) -> float:
    """Compute total length of a path.

    Args:
        g: Graph
        path: List of vertices forming a path

    Returns:
        Total weight of path, or inf if path is invalid
    """
    if len(path) <= 1:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        # Find edge weight
        found = False
        for neighbor, weight in g.neighbors(u):
            if neighbor == v:
                total += weight
                found = True
                break

        if not found:
            return float('inf')  # Edge doesn't exist

    return total


def verify_path(g: Graph, path: List[int], expected_distance: float) -> bool:
    """Verify that a path has the expected distance.

    Args:
        g: Graph
        path: List of vertices
        expected_distance: Expected total distance

    Returns:
        True if path distance matches expected distance
    """
    actual_distance = compute_path_length(g, path)
    return abs(actual_distance - expected_distance) < 1e-9


def print_path(path: List[int], distances: List[float] = None):
    """Pretty print a path.

    Args:
        path: List of vertices in path
        distances: Optional distances array to show cumulative distances
    """
    if not path:
        print("No path exists")
        return

    print("Path: ", end="")
    for i, v in enumerate(path):
        print(v, end="")
        if distances is not None and i < len(path) - 1:
            print(f" [{distances[v]:.2f}] -> ", end="")
        elif i < len(path) - 1:
            print(" -> ", end="")

    if distances is not None:
        print(f" [{distances[path[-1]]:.2f}]")
    else:
        print()


def compute_reachability(g: Graph, source: int) -> Set[int]:
    """Compute set of vertices reachable from source using BFS.

    Args:
        g: Graph
        source: Source vertex

    Returns:
        Set of reachable vertices
    """
    reachable = {source}
    queue = [source]
    front = 0

    while front < len(queue):
        u = queue[front]
        front += 1

        for v, _ in g.neighbors(u):
            if v not in reachable:
                reachable.add(v)
                queue.append(v)

    return reachable


def graph_statistics(g: Graph) -> Dict:
    """Compute various statistics about a graph.

    Args:
        g: Graph

    Returns:
        Dictionary with statistics
    """
    n, m = g.n, g.m

    # Compute degree statistics
    out_degrees = [len(g.neighbors(v)) for v in range(n)]
    in_degrees = [0] * n

    for u in range(n):
        for v, _ in g.neighbors(u):
            in_degrees[v] += 1

    # Edge weight statistics
    weights = []
    for u in range(n):
        for _, w in g.neighbors(u):
            weights.append(w)

    stats = {
        'vertices': n,
        'edges': m,
        'density': m / n if n > 0 else 0,
        'avg_out_degree': sum(out_degrees) / n if n > 0 else 0,
        'max_out_degree': max(out_degrees) if out_degrees else 0,
        'min_out_degree': min(out_degrees) if out_degrees else 0,
        'avg_in_degree': sum(in_degrees) / n if n > 0 else 0,
        'max_in_degree': max(in_degrees) if in_degrees else 0,
        'min_in_degree': min(in_degrees) if in_degrees else 0,
    }

    if weights:
        stats['avg_weight'] = sum(weights) / len(weights)
        stats['max_weight'] = max(weights)
        stats['min_weight'] = min(weights)

    return stats


def print_graph_statistics(g: Graph):
    """Print formatted graph statistics.

    Args:
        g: Graph
    """
    stats = graph_statistics(g)

    print("Graph Statistics:")
    print(f"  Vertices (n):        {stats['vertices']:>10,}")
    print(f"  Edges (m):           {stats['edges']:>10,}")
    print(f"  Density (m/n):       {stats['density']:>10.2f}")
    print(f"  Avg out-degree:      {stats['avg_out_degree']:>10.2f}")
    print(f"  Max out-degree:      {stats['max_out_degree']:>10}")
    print(f"  Min out-degree:      {stats['min_out_degree']:>10}")
    print(f"  Avg in-degree:       {stats['avg_in_degree']:>10.2f}")
    print(f"  Max in-degree:       {stats['max_in_degree']:>10}")
    print(f"  Min in-degree:       {stats['min_in_degree']:>10}")

    if 'avg_weight' in stats:
        print(f"  Avg edge weight:     {stats['avg_weight']:>10.2f}")
        print(f"  Max edge weight:     {stats['max_weight']:>10.2f}")
        print(f"  Min edge weight:     {stats['min_weight']:>10.2f}")


def compare_distances(distances1: List[float], distances2: List[float],
                      epsilon: float = 1e-9) -> bool:
    """Compare two distance arrays for equality.

    Args:
        distances1: First distance array
        distances2: Second distance array
        epsilon: Tolerance for floating point comparison

    Returns:
        True if distances match within epsilon
    """
    if len(distances1) != len(distances2):
        return False

    for d1, d2 in zip(distances1, distances2):
        # Both infinite
        if d1 == float('inf') and d2 == float('inf'):
            continue

        # One infinite, one finite
        if d1 == float('inf') or d2 == float('inf'):
            return False

        # Both finite but different
        if abs(d1 - d2) > epsilon:
            return False

    return True


def theoretical_complexity(n: int, m: int, algorithm: str) -> float:
    """Compute theoretical operation count for an algorithm.

    Args:
        n: Number of vertices
        m: Number of edges
        algorithm: 'dijkstra' or 'duan'

    Returns:
        Theoretical operation count (not exact runtime)
    """
    if algorithm.lower() == 'dijkstra':
        # O(m + n log n) with Fibonacci heap
        return m + n * math.log2(n) if n > 0 else 0

    elif algorithm.lower() == 'duan':
        # O(m log^(2/3) n)
        if n <= 1:
            return m
        return m * math.pow(math.log2(n), 2 / 3)

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def theoretical_speedup(n: int, m: int) -> float:
    """Compute theoretical speedup of Duan over Dijkstra.

    Args:
        n: Number of vertices
        m: Number of edges

    Returns:
        Theoretical speedup ratio
    """
    dijkstra_ops = theoretical_complexity(n, m, 'dijkstra')
    duan_ops = theoretical_complexity(n, m, 'duan')

    if duan_ops == 0:
        return float('inf')

    return dijkstra_ops / duan_ops


def format_distance(distance: float, decimals: int = 2) -> str:
    """Format a distance for display.

    Args:
        distance: Distance value
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if distance == float('inf'):
        return "∞"
    return f"{distance:.{decimals}f}"


def print_distance_table(distances: List[float], source: int,
                         vertices_per_row: int = 10):
    """Print distances in a formatted table.

    Args:
        distances: Distance array
        source: Source vertex
        vertices_per_row: Number of vertices to show per row
    """
    n = len(distances)

    print(f"Shortest distances from vertex {source}:")
    print("-" * 50)

    for start in range(0, n, vertices_per_row):
        end = min(start + vertices_per_row, n)

        # Print vertex numbers
        print("  v: ", end="")
        for v in range(start, end):
            print(f"{v:>8}", end="")
        print()

        # Print distances
        print("  d: ", end="")
        for v in range(start, end):
            print(f"{format_distance(distances[v], 2):>8}", end="")
        print()
        print()


def analyze_path_tree(g: Graph, predecessors: List[Optional[int]],
                      source: int) -> Dict:
    """Analyze the shortest path tree.

    Args:
        g: Graph
        predecessors: Predecessor array
        source: Source vertex

    Returns:
        Dictionary with tree statistics
    """
    n = g.n

    # Compute tree depth for each vertex
    depths = [-1] * n
    depths[source] = 0

    # BFS to compute depths
    changed = True
    while changed:
        changed = False
        for v in range(n):
            if predecessors[v] is not None and depths[v] == -1:
                pred = predecessors[v]
                if depths[pred] >= 0:
                    depths[v] = depths[pred] + 1
                    changed = True

    # Count children for each vertex
    children_count = [0] * n
    for v in range(n):
        if predecessors[v] is not None:
            children_count[predecessors[v]] += 1

    reachable = sum(1 for d in depths if d >= 0)
    max_depth = max(d for d in depths if d >= 0) if reachable > 0 else 0
    avg_depth = sum(d for d in depths if d >= 0) / reachable if reachable > 0 else 0

    return {
        'reachable_vertices': reachable,
        'max_depth': max_depth,
        'avg_depth': avg_depth,
        'max_children': max(children_count),
        'avg_children': sum(children_count) / n if n > 0 else 0
    }
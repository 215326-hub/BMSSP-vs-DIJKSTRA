"""Classical Dijkstra's algorithm with Fibonacci heap."""

import heapq
from typing import List, Tuple, Optional, Dict
from .graph import Graph


def dijkstra(g: Graph, source: int, collect_stats: bool = False) -> Tuple[List[float], List[Optional[int]], Optional[Dict]]:
    """Dijkstra single-source shortest path algorithm.

    Uses Python's heapq which implements a binary heap (not Fibonacci heap).
    Time complexity: O(m log n) with binary heap, O(m + n log n) with Fibonacci heap.

    Args:
        g: Input graph
        source: Source vertex
        collect_stats: If True, collect and return performance statistics

    Returns:
        Tuple of (distances, predecessors, stats)
        - distances[v]: shortest distance from source to v (inf if unreachable)
        - predecessors[v]: predecessor of v in shortest path tree (None if no path)
        - stats: dict with 'comparisons', 'relaxations', 'heap_ops' (None if collect_stats=False)
    """
    n = g.n
    distances = [float('inf')] * n
    predecessors = [None] * n
    distances[source] = 0.0

    stats = None
    if collect_stats:
        stats = {
            'comparisons': 0,
            'relaxations': 0,
            'heap_ops': 0
        }

    # Priority queue: (distance, vertex)
    pq = [(0.0, source)]
    visited = [False] * n

    if collect_stats:
        stats['heap_ops'] += 1

    while pq:
        dist_u, u = heapq.heappop(pq)

        if collect_stats:
            stats['heap_ops'] += 1
            stats['comparisons'] += 1

        # Skip if already processed (may have outdated entry in heap)
        if visited[u]:
            continue

        visited[u] = True

        # Relax edges from u
        for v, weight in g.neighbors(u):
            new_dist = dist_u + weight

            if collect_stats:
                stats['comparisons'] += 1

            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

                if collect_stats:
                    stats['relaxations'] += 1
                    stats['heap_ops'] += 1

    return distances, predecessors, stats


def verify_shortest_paths(g: Graph, source: int,
                          distances: List[float],
                          predecessors: List[Optional[int]]) -> bool:
    """Verify correctness of shortest path solution.

    Args:
        g: Input graph
        source: Source vertex
        distances: Computed distances
        predecessors: Computed predecessors

    Returns:
        True if solution is correct, False otherwise
    """
    n = g.n

    # Check source
    if distances[source] != 0.0:
        return False

    # Check triangle inequality for all edges
    for u in range(n):
        for v, weight in g.neighbors(u):
            if distances[u] + weight < distances[v] - 1e-9:  # Small epsilon for float comparison
                return False

    # Check predecessor paths
    for v in range(n):
        if distances[v] == float('inf'):
            if predecessors[v] is not None:
                return False
        elif v != source:
            pred = predecessors[v]
            if pred is None:
                return False

            # Check if edge (pred, v) exists with correct weight
            found = False
            for neighbor, weight in g.neighbors(pred):
                if neighbor == v:
                    expected_dist = distances[pred] + weight
                    if abs(distances[v] - expected_dist) < 1e-9:
                        found = True
                        break

            if not found:
                return False

    return True
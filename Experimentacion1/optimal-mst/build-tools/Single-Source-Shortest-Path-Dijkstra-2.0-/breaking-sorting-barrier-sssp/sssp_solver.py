"""
Breaking the Sorting Barrier for Directed Single-Source Shortest Paths
Implementation based on Duan et al. (2025) paper

This implementation provides a deterministic O(m * log^(2/3) n) time algorithm
for single-source shortest paths on directed graphs with non-negative edge weights.
"""

import heapq
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import math

class Graph:
    """Directed graph representation for SSSP algorithm"""
    
    def __init__(self, n: int):
        self.n = n  # number of vertices
        self.adj = defaultdict(list)  # adjacency list
        self.m = 0  # number of edges
        
    def add_edge(self, u: int, v: int, w: float):
        """Add directed edge from u to v with weight w"""
        self.adj[u].append((v, w))
        self.m += 1
        
    def transform_to_constant_degree(self):
        """Transform graph to have constant in-degree and out-degree"""
        # Create new graph with expanded vertices
        new_graph = Graph(self.m * 2)
        vertex_map = {}
        edge_id = 0
        
        for u in range(self.n):
            # Create cycle of vertices for each original vertex
            in_edges = []
            out_edges = []
            
            for v, w in self.adj[u]:
                out_edges.append((v, w, edge_id))
                edge_id += 1
                
            # Map original vertex to its cycle vertices
            vertex_map[u] = (in_edges, out_edges)
            
        # Connect the cycles with appropriate edges
        for u in range(self.n):
            _, out_edges = vertex_map[u]
            for v, w, eid in out_edges:
                in_edges_v, _ = vertex_map[v]
                # Add edge with original weight
                new_graph.add_edge(eid * 2, eid * 2 + 1, w)
                
        return new_graph, vertex_map


class BMSSPDataStructure:
    """Data structure for Pull/Insert/BatchPrepend operations"""
    
    def __init__(self, M: int, B: float):
        self.M = M
        self.B = B
        self.D0 = []  # Blocks for batch prepend
        self.D1 = []  # Blocks for insert
        self.upper_bounds = []  # Upper bounds for D1 blocks
        
    def insert(self, key: int, value: float) -> float:
        """Insert key/value pair, return time complexity"""
        # Find appropriate block using binary search
        block_idx = self._find_block(value)
        
        if block_idx >= len(self.D1):
            self.D1.append([])
            self.upper_bounds.append(self.B)
            
        self.D1[block_idx].append((key, value))
        
        # Split if block exceeds size limit
        if len(self.D1[block_idx]) > self.M:
            self._split_block(block_idx)
            
        return max(1, math.log2(len(self.D1)))
    
    def batch_prepend(self, items: List[Tuple[int, float]]):
        """Batch prepend multiple key/value pairs"""
        if not items:
            return
            
        items.sort(key=lambda x: x[1])
        
        if len(items) <= self.M:
            self.D0.insert(0, items)
        else:
            # Split into multiple blocks
            for i in range(0, len(items), self.M):
                block = items[i:i + self.M]
                self.D0.insert(0, block)
    
    def pull(self) -> Tuple[Set[int], float]:
        """Pull M smallest values"""
        result = set()
        bound = self.B
        
        # Collect from D0
        for block in self.D0:
            for key, val in block:
                if len(result) >= self.M:
                    bound = min(bound, val)
                    break
                result.add(key)
            if len(result) >= self.M:
                break
                
        # Collect from D1 if needed
        if len(result) < self.M:
            for i, block in enumerate(self.D1):
                for key, val in sorted(block, key=lambda x: x[1]):
                    if len(result) >= self.M:
                        bound = min(bound, val)
                        break
                    result.add(key)
                if len(result) >= self.M:
                    break
                    
        return result, bound
    
    def _find_block(self, value: float) -> int:
        """Find appropriate block index for value"""
        left, right = 0, len(self.upper_bounds)
        while left < right:
            mid = (left + right) // 2
            if self.upper_bounds[mid] < value:
                left = mid + 1
            else:
                right = mid
        return left
    
    def _split_block(self, idx: int):
        """Split block when it exceeds size limit"""
        block = self.D1[idx]
        block.sort(key=lambda x: x[1])
        mid = len(block) // 2
        
        self.D1[idx] = block[:mid]
        self.D1.insert(idx + 1, block[mid:])
        
        # Update upper bounds
        if block[:mid]:
            self.upper_bounds[idx] = block[mid - 1][1]
        if idx + 1 < len(self.upper_bounds):
            self.upper_bounds.insert(idx + 1, block[-1][1])


class SSSPSolver:
    """Main SSSP solver implementing the sorting barrier breaking algorithm"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.n = graph.n
        self.m = graph.m
        
        # Algorithm parameters
        self.k = int(math.log(self.n) ** (1/3))
        self.t = int(math.log(self.n) ** (2/3))
        
        # Distance estimates
        self.db = [float('inf')] * self.n
        self.pred = [-1] * self.n
        
    def solve(self, source: int) -> List[float]:
        """Solve SSSP from source vertex"""
        self.db[source] = 0
        
        # Call main BMSSP procedure
        max_level = math.ceil(math.log2(self.n) / self.t)
        B_prime, U = self._BMSSP(max_level, float('inf'), {source})
        
        return self.db
    
    def _BMSSP(self, level: int, B: float, S: Set[int]) -> Tuple[float, Set[int]]:
        """Bounded Multi-Source Shortest Path procedure"""
        
        if level == 0:
            return self._base_case(B, S)
        
        # Find pivots
        P, W = self._find_pivots(B, S)
        
        # Initialize data structure
        M = 2 ** ((level - 1) * self.t)
        D = BMSSPDataStructure(M, B)
        
        for x in P:
            if self.db[x] < B:
                D.insert(x, self.db[x])
        
        U = set()
        B_prime = B
        
        # Main iteration
        while len(U) < self.k * 2 ** (level * self.t):
            Si, Bi = D.pull()
            if not Si:
                break
                
            # Recursive call
            B_prime_i, Ui = self._BMSSP(level - 1, Bi, Si)
            U.update(Ui)
            
            # Relax edges from Ui
            K = []
            for u in Ui:
                for v, w in self.graph.adj[u]:
                    if self.db[u] + w <= self.db[v]:
                        self.db[v] = self.db[u] + w
                        self.pred[v] = u
                        
                        if B_prime_i <= self.db[v] < Bi:
                            K.append((v, self.db[v]))
                        elif Bi <= self.db[v] < B:
                            D.insert(v, self.db[v])
            
            # Batch prepend
            D.batch_prepend(K)
            
            if len(U) >= self.k * 2 ** (level * self.t):
                B_prime = B_prime_i
                break
        
        # Add complete vertices from W
        for x in W:
            if self.db[x] < B_prime:
                U.add(x)
                
        return B_prime, U
    
    def _base_case(self, B: float, S: Set[int]) -> Tuple[float, Set[int]]:
        """Base case: mini Dijkstra from singleton set"""
        if len(S) != 1:
            raise ValueError("Base case requires singleton set")
            
        x = next(iter(S))
        U = {x}
        heap = [(self.db[x], x)]
        
        while heap and len(U) <= self.k:
            dist, u = heapq.heappop(heap)
            
            if dist > self.db[u]:
                continue
                
            for v, w in self.graph.adj[u]:
                if self.db[u] + w < self.db[v] and self.db[u] + w < B:
                    self.db[v] = self.db[u] + w
                    self.pred[v] = u
                    heapq.heappush(heap, (self.db[v], v))
                    
            if self.db[u] < B:
                U.add(u)
        
        if len(U) <= self.k:
            return B, U
        else:
            B_prime = max(self.db[u] for u in U)
            return B_prime, {u for u in U if self.db[u] < B_prime}
    
    def _find_pivots(self, B: float, S: Set[int]) -> Tuple[Set[int], Set[int]]:
        """Find pivot vertices for recursive calls"""
        W = S.copy()
        layers = [S]
        
        # Bellman-Ford style relaxation for k steps
        for i in range(self.k):
            next_layer = set()
            for u in layers[-1]:
                for v, w in self.graph.adj[u]:
                    if self.db[u] + w <= self.db[v] and self.db[u] + w < B:
                        self.db[v] = self.db[u] + w
                        self.pred[v] = u
                        next_layer.add(v)
                        W.add(v)
            
            layers.append(next_layer)
            
            if len(W) > self.k * len(S):
                return S, W
        
        # Find pivots with large subtrees
        P = set()
        subtree_sizes = defaultdict(int)
        
        # Build forest structure
        for v in W:
            if self.pred[v] != -1 and self.pred[v] in W:
                root = self._find_root(v, W)
                if root in S:
                    subtree_sizes[root] += 1
        
        # Select pivots with subtrees >= k
        for u in S:
            if subtree_sizes[u] >= self.k:
                P.add(u)
                
        return P, W
    
    def _find_root(self, v: int, W: Set[int]) -> int:
        """Find root of vertex in forest"""
        path = []
        while v != -1 and v in W:
            path.append(v)
            if self.pred[v] == -1 or self.pred[v] not in W:
                break
            v = self.pred[v]
            
        return path[-1] if path else -1


# Example usage and testing
def example_usage():
    """Example of how to use the SSSP solver"""
    
    # Create a simple directed graph
    n = 6
    graph = Graph(n)
    
    # Add edges (u, v, weight)
    edges = [
        (0, 1, 4),
        (0, 2, 2),
        (1, 2, 1),
        (1, 3, 5),
        (2, 3, 8),
        (2, 4, 10),
        (3, 4, 2),
        (3, 5, 6),
        (4, 5, 3)
    ]
    
    for u, v, w in edges:
        graph.add_edge(u, v, w)
    
    # Solve SSSP from vertex 0
    solver = SSSPSolver(graph)
    distances = solver.solve(0)
    
    print("Shortest distances from vertex 0:")
    for i in range(n):
        print(f"  to vertex {i}: {distances[i]}")
    
    return distances


if __name__ == "__main__":
    # Run example
    example_usage()
    
    # Additional test with random graph
    import random
    
    print("\nTesting with larger random graph...")
    n = 100
    m = 500
    
    graph = Graph(n)
    for _ in range(m):
        u = random.randint(0, n-1)
        v = random.randint(0, n-1)
        if u != v:
            w = random.uniform(0.1, 10.0)
            graph.add_edge(u, v, w)
    
    solver = SSSPSolver(graph)
    distances = solver.solve(0)
    
    print(f"Completed SSSP on graph with {n} vertices and {m} edges")
    print(f"Sample distances: {distances[:10]}")

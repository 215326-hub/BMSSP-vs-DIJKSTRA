"""
Unit tests for SSSP implementation
"""

import unittest
import random
from sssp_solver import Graph, SSSPSolver
import heapq

class TestSSSP(unittest.TestCase):
    
    def dijkstra_reference(self, graph: Graph, source: int) -> list:
        """Reference Dijkstra implementation for comparison"""
        dist = [float('inf')] * graph.n
        dist[source] = 0
        heap = [(0, source)]
        
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
                
            for v, w in graph.adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(heap, (dist[v], v))
                    
        return dist
    
    def test_small_graph(self):
        """Test on a small example graph"""
        graph = Graph(5)
        edges = [
            (0, 1, 4),
            (0, 2, 2),
            (1, 2, 1),
            (1, 3, 5),
            (2, 3, 8),
            (2, 4, 10),
            (3, 4, 2)
        ]
        
        for u, v, w in edges:
            graph.add_edge(u, v, w)
        
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        # Expected distances from vertex 0
        expected = [0, 4, 2, 9, 11]
        
        for i in range(5):
            self.assertAlmostEqual(distances[i], expected[i], places=6)
    
    def test_single_vertex(self):
        """Test graph with single vertex"""
        graph = Graph(1)
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        self.assertEqual(distances[0], 0)
    
    def test_disconnected_graph(self):
        """Test graph with disconnected components"""
        graph = Graph(5)
        graph.add_edge(0, 1, 1)
        graph.add_edge(1, 2, 1)
        graph.add_edge(3, 4, 1)
        
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        self.assertEqual(distances[0], 0)
        self.assertEqual(distances[1], 1)
        self.assertEqual(distances[2], 2)
        self.assertEqual(distances[3], float('inf'))
        self.assertEqual(distances[4], float('inf'))
    
    def test_linear_chain(self):
        """Test on a linear chain graph"""
        n = 100
        graph = Graph(n)
        
        for i in range(n - 1):
            graph.add_edge(i, i + 1, 1.0)
        
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        for i in range(n):
            self.assertAlmostEqual(distances[i], float(i), places=6)
    
    def test_complete_graph(self):
        """Test on a small complete graph"""
        n = 10
        graph = Graph(n)
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    graph.add_edge(i, j, abs(i - j))
        
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        for i in range(n):
            self.assertAlmostEqual(distances[i], i, places=6)
    
    def test_correctness_vs_dijkstra(self):
        """Compare results with standard Dijkstra's algorithm"""
        random.seed(42)
        
        for _ in range(10):
            n = random.randint(20, 100)
            m = random.randint(n, min(n * (n - 1), 500))
            
            graph = Graph(n)
            edges_added = set()
            
            # Create random connected graph
            # First create a spanning tree
            for i in range(1, n):
                j = random.randint(0, i - 1)
                w = random.uniform(0.1, 10.0)
                graph.add_edge(j, i, w)
                edges_added.add((j, i))
            
            # Add random edges
            while len(edges_added) < m:
                u = random.randint(0, n - 1)
                v = random.randint(0, n - 1)
                if u != v and (u, v) not in edges_added:
                    w = random.uniform(0.1, 10.0)
                    graph.add_edge(u, v, w)
                    edges_added.add((u, v))
            
            # Compare with Dijkstra
            solver = SSSPSolver(graph)
            our_distances = solver.solve(0)
            dijkstra_distances = self.dijkstra_reference(graph, 0)
            
            for i in range(n):
                self.assertAlmostEqual(our_distances[i], dijkstra_distances[i], 
                                     places=6,
                                     msg=f"Mismatch at vertex {i}")
    
    def test_zero_weight_edges(self):
        """Test graph with zero-weight edges"""
        graph = Graph(4)
        graph.add_edge(0, 1, 0)
        graph.add_edge(1, 2, 0)
        graph.add_edge(2, 3, 1)
        graph.add_edge(0, 3, 5)
        
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        self.assertEqual(distances[0], 0)
        self.assertEqual(distances[1], 0)
        self.assertEqual(distances[2], 0)
        self.assertEqual(distances[3], 1)
    
    def test_parallel_edges(self):
        """Test graph with parallel edges (multiple edges between same vertices)"""
        graph = Graph(3)
        graph.add_edge(0, 1, 5)
        graph.add_edge(0, 1, 3)  # Shorter parallel edge
        graph.add_edge(1, 2, 2)
        
        solver = SSSPSolver(graph)
        distances = solver.solve(0)
        
        self.assertEqual(distances[0], 0)
        self.assertEqual(distances[1], 3)
        self.assertEqual(distances[2], 5)


class TestBMSSPDataStructure(unittest.TestCase):
    """Test the custom data structure operations"""
    
    def test_insert_and_pull(self):
        """Test basic insert and pull operations"""
        from sssp_solver import BMSSPDataStructure
        
        ds = BMSSPDataStructure(M=3, B=100)
        
        # Insert some values
        ds.insert(1, 10)
        ds.insert(2, 5)
        ds.insert(3, 15)
        ds.insert(4, 8)
        
        # Pull should return smallest values
        result, bound = ds.pull()
        
        self.assertEqual(len(result), 3)
        self.assertIn(2, result)  # vertex with value 5
        self.assertIn(4, result)  # vertex with value 8
        self.assertIn(1, result)  # vertex with value 10
    
    def test_batch_prepend(self):
        """Test batch prepend operation"""
        from sssp_solver import BMSSPDataStructure
        
        ds = BMSSPDataStructure(M=3, B=100)
        
        # Initial inserts
        ds.insert(5, 20)
        ds.insert(6, 25)
        
        # Batch prepend smaller values
        ds.batch_prepend([(1, 2), (2, 3), (3, 4)])
        
        # Pull should return prepended values first
        result, bound = ds.pull()
        
        self.assertEqual(len(result), 3)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)


if __name__ == '__main__':
    unittest.main(verbosity=2)

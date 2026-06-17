package bmssp

import (
	"math"
	"math/rand"
	"testing"
)

func TestSSSP_SimpleGraph(t *testing.T) {
	// Create a simple test graph:
	//   0 -> 1 (weight 2)
	//   0 -> 2 (weight 4)
	//   1 -> 2 (weight 1)
	//   1 -> 3 (weight 7)
	//   2 -> 3 (weight 3)
	g := NewGraph(4)
	g.AddEdge(0, 1, 2)
	g.AddEdge(0, 2, 4)
	g.AddEdge(1, 2, 1)
	g.AddEdge(1, 3, 7)
	g.AddEdge(2, 3, 3)

	distances, predecessors := SSSP(g, 0)

	// Expected distances from source 0:
	// 0 -> 0: 0
	// 0 -> 1: 2
	// 0 -> 2: 3 (via 1)
	// 0 -> 3: 6 (via 1->2)
	expected := []float64{0, 2, 3, 6}

	for i, exp := range expected {
		if math.Abs(distances[i]-exp) > 1e-9 {
			t.Errorf("Distance to vertex %d: got %f, want %f", i, distances[i], exp)
		}
	}

	// Check predecessors
	if predecessors[0] != -1 {
		t.Errorf("Predecessor of source should be -1, got %d", predecessors[0])
	}
	if predecessors[1] != 0 {
		t.Errorf("Predecessor of vertex 1 should be 0, got %d", predecessors[1])
	}
}

func TestSSSP_SingleVertex(t *testing.T) {
	g := NewGraph(1)
	distances, predecessors := SSSP(g, 0)

	if distances[0] != 0 {
		t.Errorf("Distance to source should be 0, got %f", distances[0])
	}
	if predecessors[0] != -1 {
		t.Errorf("Predecessor of source should be -1, got %d", predecessors[0])
	}
}

func TestSSSP_DisconnectedGraph(t *testing.T) {
	g := NewGraph(3)
	g.AddEdge(0, 1, 5)
	// Vertex 2 is disconnected

	distances, _ := SSSP(g, 0, nil)

	if distances[0] != 0 {
		t.Errorf("Distance to source should be 0, got %f", distances[0])
	}
	if distances[1] != 5 {
		t.Errorf("Distance to vertex 1 should be 5, got %f", distances[1])
	}
	if distances[2] != Inf {
		t.Errorf("Distance to disconnected vertex 2 should be infinity, got %f", distances[2])
	}
}

func TestSSSP_CompareWithDijkstra(t *testing.T) {
	rand.Seed(42)
	n := 100
	m := 300

	g := NewGraph(n)
	for i := 0; i < m; i++ {
		u := rand.Intn(n)
		v := rand.Intn(n)
		if u == v {
			continue
		}
		w := rand.Float64()*10 + 1
		g.AddEdge(u, v, w)
	}

	s := 0
	distBMSSP, _ := SSSP(g, s, nil)
	distDijkstra, _ := dijkstra(g, s)

	// Compare results
	for i := 0; i < n; i++ {
		diff := math.Abs(distBMSSP[i] - distDijkstra[i])
		if diff > 1e-9 {
			t.Errorf("Distance mismatch for vertex %d: BMSSP=%f, Dijkstra=%f, diff=%f",
				i, distBMSSP[i], distDijkstra[i], diff)
		}
	}
}

func TestSSSP_CustomOptions(t *testing.T) {
	g := NewGraph(10)
	for i := 0; i < 9; i++ {
		g.AddEdge(i, i+1, 1)
	}

	distances, _ := SSSP(g, 0, WithK(3), WithT(2))

	// Should still produce correct results
	for i := 0; i < 10; i++ {
		expected := float64(i)
		if math.Abs(distances[i]-expected) > 1e-9 {
			t.Errorf("Distance to vertex %d: got %f, want %f", i, distances[i], expected)
		}
	}
}

func TestSSSP_NilOptions(t *testing.T) {
	g := NewGraph(4)
	g.AddEdge(0, 1, 2)
	g.AddEdge(1, 2, 1)
	g.AddEdge(2, 3, 3)

	// Should handle nil options gracefully
	distances, _ := SSSP(g, 0, nil, WithK(2), nil)

	// Should still produce correct results
	expected := []float64{0, 2, 3, 6}
	for i, exp := range expected {
		if math.Abs(distances[i]-exp) > 1e-9 {
			t.Errorf("Distance to vertex %d: got %f, want %f", i, distances[i], exp)
		}
	}
}

func BenchmarkSSSP_SmallGraph(b *testing.B) {
	g := NewGraph(100)
	rand.Seed(42)
	for i := 0; i < 300; i++ {
		u := rand.Intn(100)
		v := rand.Intn(100)
		if u != v {
			g.AddEdge(u, v, rand.Float64()*10+1)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		SSSP(g, 0, nil)
	}
}

func BenchmarkSSSP_vs_Dijkstra(b *testing.B) {
	n := 200
	m := 15
	g := NewGraph(n)
	rand.Seed(42)
	for i := 0; i < m; i++ {
		u := rand.Intn(n)
		v := rand.Intn(n)
		if u != v {
			g.AddEdge(u, v, rand.Float64()*10+1)
		}
	}

	b.Run("BMSSP", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			SSSP(g, 0, nil)
		}
	})

	b.Run("Dijkstra", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			dijkstra(g, 0)
		}
	})
}

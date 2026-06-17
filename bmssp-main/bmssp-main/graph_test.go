package bmssp

import (
	"testing"
)

func TestNewGraph(t *testing.T) {
	n := 5
	g := NewGraph(n)

	if g.N != n {
		t.Errorf("Graph size: got %d, want %d", g.N, n)
	}

	if len(g.Adj) != n {
		t.Errorf("Adjacency list length: got %d, want %d", len(g.Adj), n)
	}

	// Check that all adjacency lists are initialized (empty but not nil)
	for i := 0; i < n; i++ {
		if g.Adj[i] == nil {
			t.Errorf("Adjacency list for vertex %d is nil", i)
		}
		if len(g.Adj[i]) != 0 {
			t.Errorf("Adjacency list for vertex %d should be empty initially, got length %d", i, len(g.Adj[i]))
		}
	}
}

func TestAddEdge_Valid(t *testing.T) {
	g := NewGraph(3)

	err := g.AddEdge(0, 1, 5.5)
	if err != nil {
		t.Errorf("AddEdge should succeed for valid input, got error: %v", err)
	}

	if len(g.Adj[0]) != 1 {
		t.Errorf("Expected 1 edge from vertex 0, got %d", len(g.Adj[0]))
	}

	edge := g.Adj[0][0]
	if edge.To != 1 {
		t.Errorf("Edge destination: got %d, want 1", edge.To)
	}
	if edge.W != 5.5 {
		t.Errorf("Edge weight: got %f, want 5.5", edge.W)
	}
}

func TestAddEdge_MultipleEdges(t *testing.T) {
	g := NewGraph(3)

	g.AddEdge(0, 1, 2.0)
	g.AddEdge(0, 2, 3.0)
	g.AddEdge(1, 2, 1.0)

	if len(g.Adj[0]) != 2 {
		t.Errorf("Expected 2 edges from vertex 0, got %d", len(g.Adj[0]))
	}

	if len(g.Adj[1]) != 1 {
		t.Errorf("Expected 1 edge from vertex 1, got %d", len(g.Adj[1]))
	}

	if len(g.Adj[2]) != 0 {
		t.Errorf("Expected 0 edges from vertex 2, got %d", len(g.Adj[2]))
	}
}

func TestAddEdge_InvalidVertex(t *testing.T) {
	g := NewGraph(3)

	testCases := []struct {
		name string
		u, v int
		w    float64
	}{
		{"negative source", -1, 1, 1.0},
		{"negative destination", 1, -1, 1.0},
		{"source out of range", 3, 1, 1.0},
		{"destination out of range", 1, 3, 1.0},
		{"both out of range", 5, 6, 1.0},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			err := g.AddEdge(tc.u, tc.v, tc.w)
			if err == nil {
				t.Errorf("AddEdge should fail for invalid vertices %d->%d", tc.u, tc.v)
			}
		})
	}
}

func TestAddEdge_NegativeWeight(t *testing.T) {
	g := NewGraph(3)

	err := g.AddEdge(0, 1, -1.0)
	if err == nil {
		t.Errorf("AddEdge should fail for negative weight")
	}

	// Verify no edge was added
	if len(g.Adj[0]) != 0 {
		t.Errorf("No edge should be added when weight is negative")
	}
}

func TestAddEdge_ZeroWeight(t *testing.T) {
	g := NewGraph(3)

	err := g.AddEdge(0, 1, 0.0)
	if err != nil {
		t.Errorf("AddEdge should succeed for zero weight, got error: %v", err)
	}

	if len(g.Adj[0]) != 1 {
		t.Errorf("Expected 1 edge from vertex 0, got %d", len(g.Adj[0]))
	}

	if g.Adj[0][0].W != 0.0 {
		t.Errorf("Edge weight: got %f, want 0.0", g.Adj[0][0].W)
	}
}

func TestAddEdge_SelfLoop(t *testing.T) {
	g := NewGraph(3)

	err := g.AddEdge(1, 1, 2.5)
	if err != nil {
		t.Errorf("AddEdge should succeed for self-loop, got error: %v", err)
	}

	if len(g.Adj[1]) != 1 {
		t.Errorf("Expected 1 edge from vertex 1, got %d", len(g.Adj[1]))
	}

	edge := g.Adj[1][0]
	if edge.To != 1 || edge.W != 2.5 {
		t.Errorf("Self-loop edge: got To=%d W=%f, want To=1 W=2.5", edge.To, edge.W)
	}
}

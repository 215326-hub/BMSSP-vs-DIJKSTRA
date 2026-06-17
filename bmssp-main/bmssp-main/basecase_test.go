package bmssp

import (
	"testing"
)

func TestBaseCase_SingletonFrontier(t *testing.T) {
	// Create a small graph for testing
	g := NewGraph(5)
	g.AddEdge(0, 1, 1.0)
	g.AddEdge(0, 2, 2.0)
	g.AddEdge(1, 3, 1.0)
	g.AddEdge(2, 4, 1.0)

	db := make([]float64, 5)
	pred := make([]int, 5)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0.0

	S := set{m: map[int]struct{}{0: {}}}
	B := 10.0
	opt := &options{K: 3, T: 2}

	Bprime, U := baseCase(g, B, S, db, pred, opt)

	// Should update distances
	if db[1] >= Inf {
		t.Error("Distance to vertex 1 should be updated")
	}
	if db[2] >= Inf {
		t.Error("Distance to vertex 2 should be updated")
	}

	// U should contain the source and some neighbors
	if !U.Has(0) {
		t.Error("U should contain the source vertex")
	}

	// Bprime should be <= B
	if Bprime > B {
		t.Errorf("Bprime (%f) should be <= B (%f)", Bprime, B)
	}
}

func TestBaseCase_SmallK(t *testing.T) {
	// Test with K=2 to trigger the size limit
	g := NewGraph(5)
	g.AddEdge(0, 1, 1.0)
	g.AddEdge(0, 2, 2.0)
	g.AddEdge(1, 3, 1.0)
	g.AddEdge(2, 4, 1.0)

	db := make([]float64, 5)
	pred := make([]int, 5)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0.0

	S := set{m: map[int]struct{}{0: {}}}
	B := 10.0
	opt := &options{K: 2, T: 2} // Small K

	Bprime, U := baseCase(g, B, S, db, pred, opt)

	// Should limit the number of vertices processed
	if U.Size() > opt.K {
		t.Errorf("U size (%d) should be <= K (%d)", U.Size(), opt.K)
	}

	// Bprime should be updated if we hit the limit
	if U.Size() == opt.K && Bprime == B {
		t.Error("Bprime should be updated when hitting the K limit")
	}
}

func TestBaseCase_WithinBound(t *testing.T) {
	// Test case where all reachable vertices are within the bound
	g := NewGraph(3)
	g.AddEdge(0, 1, 1.0)
	g.AddEdge(1, 2, 1.0)

	db := make([]float64, 3)
	pred := make([]int, 3)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0.0

	S := set{m: map[int]struct{}{0: {}}}
	B := 1.5 // Only vertex 1 should be reachable within this bound
	opt := &options{K: 5, T: 2}

	Bprime, U := baseCase(g, B, S, db, pred, opt)

	// Vertex 2 should not be reached due to bound
	if db[2] < Inf {
		t.Errorf("Vertex 2 should not be reached within bound %f, got distance %f", B, db[2])
	}

	// Should return the original bound since we didn't exceed K
	if Bprime != B {
		t.Errorf("Bprime should equal B (%f) when not exceeding K, got %f", B, Bprime)
	}

	// U should contain vertices 0 and 1
	if !U.Has(0) || !U.Has(1) {
		t.Error("U should contain vertices 0 and 1")
	}
	if U.Has(2) {
		t.Error("U should not contain vertex 2 (outside bound)")
	}
}

func TestBaseCase_PanicOnNonSingleton(t *testing.T) {
	g := NewGraph(2)
	db := make([]float64, 2)
	pred := make([]int, 2)

	// Non-singleton frontier should panic
	S := set{m: map[int]struct{}{0: {}, 1: {}}}
	opt := &options{K: 2, T: 2}

	defer func() {
		if r := recover(); r == nil {
			t.Error("baseCase should panic with non-singleton frontier")
		}
	}()

	baseCase(g, 10.0, S, db, pred, opt)
}

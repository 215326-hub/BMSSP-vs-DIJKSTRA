package bmssp

import (
	"testing"
)

func TestNearlyEqual(t *testing.T) {
	testCases := []struct {
		name     string
		a, b     float64
		expected bool
	}{
		{"exactly equal", 1.0, 1.0, true},
		{"nearly equal within epsilon", 1.0, 1.0 + 1e-13, true},
		{"nearly equal within epsilon (reverse)", 1.0 + 1e-13, 1.0, true},
		{"not equal beyond epsilon", 1.0, 1.0 + 1e-11, false},
		{"negative values nearly equal", -1.0, -1.0 - 1e-13, true},
		{"different signs", 1.0, -1.0, false},
		{"zero and small positive", 0.0, 1e-13, true},
		{"zero and larger positive", 0.0, 1e-11, false},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := nearlyEqual(tc.a, tc.b)
			if result != tc.expected {
				t.Errorf("nearlyEqual(%f, %f): got %t, want %t", tc.a, tc.b, result, tc.expected)
			}
		})
	}
}

func TestFindPivots_SmallExample(t *testing.T) {
	// Create a small graph to test findPivots
	g := NewGraph(4)
	g.AddEdge(0, 1, 1.0)
	g.AddEdge(0, 2, 2.0)
	g.AddEdge(1, 3, 1.0)
	g.AddEdge(2, 3, 1.0)

	db := make([]float64, 4)
	pred := make([]int, 4)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0.0

	S := set{m: map[int]struct{}{0: {}}}
	B := 10.0 // Large bound
	opt := &options{K: 2, T: 2}

	P, W := findPivots(g, B, S, db, pred, opt)

	// W should contain vertices reached during relaxation
	if !W.Has(0) {
		t.Error("W should contain source vertex 0")
	}

	// P should be a subset of S
	for v := range P.m {
		if !S.Has(v) {
			t.Errorf("Pivot %d should be in frontier S", v)
		}
	}
}

func TestFindPivots_EarlyExit(t *testing.T) {
	// Test the early exit condition when |W| > K * |S|
	g := NewGraph(10)
	// Create a dense subgraph from vertex 0
	for i := 1; i < 10; i++ {
		g.AddEdge(0, i, 1.0)
	}

	db := make([]float64, 10)
	pred := make([]int, 10)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0.0

	S := set{m: map[int]struct{}{0: {}}}
	B := 10.0
	opt := &options{K: 2, T: 2} // Small K to trigger early exit

	P, W := findPivots(g, B, S, db, pred, opt)

	// Should return S as pivots due to early exit
	if P.Size() != S.Size() {
		t.Errorf("Expected P to equal S due to early exit, got P size %d, S size %d", P.Size(), S.Size())
	}

	// W should contain many vertices
	if W.Size() <= opt.K {
		t.Errorf("Expected W to have > K vertices, got %d", W.Size())
	}
}

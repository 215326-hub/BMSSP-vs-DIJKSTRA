package bmssp

import (
	"math"
	"testing"
)

// Verifies the precise K+1 then step-back rule in base case.
func TestBaseCase_KPlusOneRule_Precise(t *testing.T) {
	// Construct a star so we can process exactly K+1 vertices within bound
	// 0 -> 1..4 with increasing weights; K=3 ensures K+1=4 processed
	g := NewGraph(6)
	_ = g.AddEdge(0, 1, 1.0)
	_ = g.AddEdge(0, 2, 2.0)
	_ = g.AddEdge(0, 3, 3.0)
	_ = g.AddEdge(0, 4, 4.0)
	// extra vertex unreachable

	db := make([]float64, g.N)
	pred := make([]int, g.N)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0

	S := set{m: map[int]struct{}{0: {}}}
	// Large bound to allow K+1 pops
	B := 100.0
	opt := &options{K: 3, T: 2}

	Bprime, U := baseCase(g, B, S, db, pred, opt)

	// We expect exactly K vertices returned (0,1,2) and B' equals distance of (K+1)-th smallest (which is 3.0)
	if U.Size() != opt.K {
		t.Fatalf("expected exactly K=%d vertices, got %d", opt.K, U.Size())
	}
	// K smallest vertices are: 0 (0), 1 (1), 2 (2) -> ensure membership
	expected := []int{0, 1, 2}
	for _, v := range expected {
		if !U.Has(v) {
			t.Fatalf("U missing expected vertex %d", v)
		}
	}
	if math.Abs(Bprime-3.0) > 1e-9 {
		t.Fatalf("expected B' = 3.0 (the (K+1)-th smallest), got %f", Bprime)
	}
}

// Verifies frontier reduction early-exit threshold: if too many vertices touched, use entire S as pivots
func TestFindPivots_EarlyExitThreshold(t *testing.T) {
	g := NewGraph(6)
	// Two-frontier vertices 0 and 5 each exploding to many touches
	_ = g.AddEdge(0, 1, 1)
	_ = g.AddEdge(0, 2, 1)
	_ = g.AddEdge(0, 3, 1)
	_ = g.AddEdge(0, 4, 1)
	_ = g.AddEdge(5, 1, 1)
	_ = g.AddEdge(5, 2, 1)

	db := make([]float64, g.N)
	pred := make([]int, g.N)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0
	db[5] = 0

	S := set{m: map[int]struct{}{0: {}, 5: {}}}
	B := 10.0
	opt := &options{K: 1, T: 2} // small K to trigger early exit when W grows

	P, W := findPivots(g, B, S, db, pred, opt)
	if W.Size() <= opt.K*max(1, S.Size()) {
		t.Fatalf("test setup failed: expected W to exceed threshold, got |W|=%d, threshold=%d", W.Size(), opt.K*max(1, S.Size()))
	}
	// Early exit should return S as pivots
	if P.Size() != S.Size() || !P.Has(0) || !P.Has(5) {
		t.Fatalf("expected P == S due to early exit, got P size=%d", P.Size())
	}
}

// Verifies W-absorption invariant: vertices in W with db[x] < B' should be in U
func TestBMSSP_WAbsorptionInvariant(t *testing.T) {
	// Small layered graph to trigger recursion and absorption
	g := NewGraph(5)
	_ = g.AddEdge(0, 1, 1)
	_ = g.AddEdge(1, 2, 1)
	_ = g.AddEdge(2, 3, 1)
	_ = g.AddEdge(1, 4, 3)

	db := make([]float64, g.N)
	pred := make([]int, g.N)
	for i := range db {
		db[i] = Inf
		pred[i] = -1
	}
	db[0] = 0

	// Use defaults for k,t derived from n, but ensure reasonable via options override
	opt := defaultOptions(g.N)
	// Make parameters small to keep recursion tight
	opt.K = 2
	opt.T = 2

	// Compute initial W via findPivots with starting bound B=Inf and S={0}
	S := set{m: map[int]struct{}{0: {}}}
	B := Inf
	P0, W0 := findPivots(g, B, S, db, pred, &opt)
	if P0.Size() == 0 && W0.Size() == 0 {
		t.Fatalf("unexpected empty P0 and W0")
	}

	// Run bmssp and get final U and B'
	Bp, U := bmssp(g, 1, B, S, db, pred, &opt)
	if Bp > B {
		t.Fatalf("expected B' <= B, got %f > %f", Bp, B)
	}

	// Check absorption: any x in initial W0 with db[x] < B' must be in U
	for x := range W0.m {
		if db[x] < Bp && !U.Has(x) {
			t.Fatalf("absorption violated: x=%d with db[x]=%f < B'=%f not absorbed into U", x, db[x], Bp)
		}
	}
}

// Verifies level-queue epsilon grouping: near-equal keys are grouped
func TestLevelQueue_EpsilonGrouping(t *testing.T) {
	lq := NewLevelQueue(WithUpperBound(10))
	base := 1.0
	near := base + 1e-13 // smaller than eps=1e-12 difference threshold
	lq.Insert(1, base)
	lq.Insert(2, near)

	si, _ := lq.Pull()
	if len(si) != 2 {
		t.Fatalf("expected near-equal keys to group; got %v", si)
	}
}

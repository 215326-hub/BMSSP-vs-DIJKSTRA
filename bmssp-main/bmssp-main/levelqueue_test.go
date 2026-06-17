package bmssp

import (
	"container/heap"
	"testing"
)

func TestLevelQueue_EmptyQueue(t *testing.T) {
	lq := NewLevelQueue()

	if lq.NonEmpty() {
		t.Error("New queue should be empty")
	}

	si, bi := lq.Pull()
	if si != nil {
		t.Errorf("Empty queue should return nil slice, got %v", si)
	}
	if bi != Inf {
		t.Errorf("Empty queue should return Inf, got %f", bi)
	}
}

func TestLevelQueue_InsertAndPull(t *testing.T) {
	lq := NewLevelQueue()

	// Insert some vertices
	lq.Insert(1, 5.0)
	lq.Insert(2, 3.0)
	lq.Insert(3, 3.0) // Same key as vertex 2
	lq.Insert(4, 7.0)

	if !lq.NonEmpty() {
		t.Error("Queue should not be empty after insertions")
	}

	// Pull should return vertices with minimum key group (3.0)
	si, _ := lq.Pull()
	if len(si) != 2 {
		t.Errorf("Expected 2 vertices with key 3.0, got %d", len(si))
	}

	// Check that we got vertices 2 and 3
	vertices := make(map[int]bool)
	for _, v := range si {
		vertices[v] = true
	}
	if !vertices[2] || !vertices[3] {
		t.Errorf("Expected vertices 2 and 3, got %v", si)
	}

	// Next pull should get vertex 1
	si, _ = lq.Pull()
	if len(si) != 1 || si[0] != 1 {
		t.Errorf("Expected vertex 1 with key 5.0, got vertices %v", si)
	}

	// Next pull should get vertex 4
	si, _ = lq.Pull()
	if len(si) != 1 || si[0] != 4 {
		t.Errorf("Expected vertex 4 with key 7.0, got vertices %v", si)
	}

	// Queue should now be empty
	if lq.NonEmpty() {
		t.Error("Queue should be empty after pulling all elements")
	}
}

func TestLevelQueue_BatchPrepend(t *testing.T) {
	lq := NewLevelQueue()

	// BatchPrepend should add candidates to the queue
	candidates := []kv{
		{v: 1, key: 1.0},
		{v: 2, key: 2.0},
	}
	lq.BatchPrepend(candidates)

	if !lq.NonEmpty() {
		t.Error("Queue should not be empty after BatchPrepend")
	}

	// Should pull in order
	si, _ := lq.Pull()
	if len(si) != 1 || si[0] != 1 {
		t.Errorf("Expected vertex 1 with key 1.0, got vertices %v", si)
	}

	si, _ = lq.Pull()
	if len(si) != 1 || si[0] != 2 {
		t.Errorf("Expected vertex 2 with key 2.0, got vertices %v", si)
	}

	// Test with nil slice
	lq.BatchPrepend(nil) // Should not crash

	// Test with empty slice
	lq.BatchPrepend([]kv{}) // Should not crash
}

func TestMinPQ_EdgeCases(t *testing.T) {
	pq := newMinPQ()

	if pq.Len() != 0 {
		t.Error("New priority queue should have length 0")
	}

	// Test with single element
	pq.Push(item{v: 42, key: 3.14})
	if pq.Len() != 1 {
		t.Error("Priority queue should have length 1 after push")
	}

	result := pq.Pop().(item)
	if result.v != 42 || result.key != 3.14 {
		t.Errorf("Pop should return inserted item, got v=%d key=%f", result.v, result.key)
	}

	if pq.Len() != 0 {
		t.Error("Priority queue should have length 0 after pop")
	}
}

func TestMinPQ_Ordering(t *testing.T) {
	pq := newMinPQ()

	// Insert items using heap.Push to ensure proper heap operations
	heap.Push(pq, item{v: 3, key: 9.0})
	heap.Push(pq, item{v: 1, key: 3.0})
	heap.Push(pq, item{v: 2, key: 6.0})
	heap.Push(pq, item{v: 0, key: 1.0})

	// Should come out in sorted order by key
	results := make([]float64, 0, 4)
	for pq.Len() > 0 {
		result := heap.Pop(pq).(item)
		results = append(results, result.key)
	}

	// Verify we get them in ascending order
	for i := 1; i < len(results); i++ {
		if results[i] < results[i-1] {
			t.Errorf("Items not in ascending order: %v", results)
			break
		}
	}

	// Check specific expected values
	expected := []float64{1.0, 3.0, 6.0, 9.0}
	if len(results) != len(expected) {
		t.Errorf("Wrong number of results: got %d, want %d", len(results), len(expected))
	}

	for i, exp := range expected {
		if i < len(results) && results[i] != exp {
			t.Errorf("Result %d: got %f, want %f", i, results[i], exp)
		}
	}
}

func TestLevelQueue_NilOptions(t *testing.T) {
	// Should handle nil options gracefully
	lq := NewLevelQueue(nil, WithUpperBound(5.0), nil)

	lq.Insert(1, 3.0)
	lq.Insert(2, 7.0) // This will be inserted but filtered during Pull

	if !lq.NonEmpty() {
		t.Error("Queue should not be empty after insertion")
	}

	// Pull should only return vertex 1 due to upper bound
	si, bi := lq.Pull()
	if len(si) != 1 || si[0] != 1 {
		t.Errorf("Expected vertex 1, got %v", si)
	}

	if bi != 5.0 {
		t.Errorf("Expected upper bound 5.0, got %f", bi)
	}

	// Queue should still have vertex 2, but it won't be returned in next pull
	// since it exceeds the upper bound
	if !lq.NonEmpty() {
		t.Error("Queue should still have vertex 2")
	}
}

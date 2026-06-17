package bmssp

import (
	"reflect"
	"sort"
	"testing"
)

func TestSet_Operations(t *testing.T) {
	s := set{m: map[int]struct{}{}}

	// Test empty set
	if s.Has(1) {
		t.Error("Empty set should not contain any elements")
	}
	if s.Size() != 0 {
		t.Error("Empty set should have size 0")
	}

	// Test Add and Has
	s.Add(1)
	s.Add(3)
	s.Add(5)

	if !s.Has(1) || !s.Has(3) || !s.Has(5) {
		t.Error("Set should contain added elements")
	}
	if s.Has(2) || s.Has(4) {
		t.Error("Set should not contain non-added elements")
	}

	// Test Size
	if s.Size() != 3 {
		t.Errorf("Set size should be 3, got %d", s.Size())
	}

	// Test adding duplicate
	s.Add(3) // Should not change size
	if s.Size() != 3 {
		t.Errorf("Adding duplicate should not change size, got %d", s.Size())
	}

	// Test ToSlice
	slice := s.ToSlice()
	if len(slice) != 3 {
		t.Errorf("ToSlice should return slice of length 3, got %d", len(slice))
	}

	// Sort the slice to make comparison deterministic
	sort.Ints(slice)
	expected := []int{1, 3, 5}
	if !reflect.DeepEqual(slice, expected) {
		t.Errorf("ToSlice should return [1, 3, 5], got %v", slice)
	}
}

func TestSet_EmptyToSlice(t *testing.T) {
	s := set{m: map[int]struct{}{}}
	slice := s.ToSlice()
	
	if len(slice) != 0 {
		t.Errorf("Empty set ToSlice should return empty slice, got %v", slice)
	}
}

func TestSet_SingleElement(t *testing.T) {
	s := set{m: map[int]struct{}{}}
	s.Add(42)
	
	if !s.Has(42) {
		t.Error("Set should contain the single added element")
	}
	if s.Size() != 1 {
		t.Errorf("Single element set should have size 1, got %d", s.Size())
	}
	
	slice := s.ToSlice()
	if len(slice) != 1 || slice[0] != 42 {
		t.Errorf("ToSlice should return [42], got %v", slice)
	}
}

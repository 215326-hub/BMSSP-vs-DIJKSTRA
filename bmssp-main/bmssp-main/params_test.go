package bmssp

import (
	"math"
	"testing"
)

func TestDefaultOptions(t *testing.T) {
	testCases := []struct {
		name    string
		n       int
		expectK int
		expectT int
	}{
		{"small graph", 4, 2, 2},          // minimum values when log^(1/3) and log^(2/3) are small
		{"medium graph", 100, 2, 3},       // floor(log(100)^(1/3)) ≈ 1.6, floor(log(100)^(2/3)) ≈ 2.9
		{"large graph", 1000, 2, 4},       // floor(log(1000)^(1/3)) ≈ 2.0, floor(log(1000)^(2/3)) ≈ 4.3
		{"very large graph", 10000, 3, 6}, // floor(log(10000)^(1/3)) ≈ 2.5, floor(log(10000)^(2/3)) ≈ 6.1
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			opt := defaultOptions(tc.n)

			if opt.K < 2 {
				t.Errorf("K should be at least 2, got %d", opt.K)
			}
			if opt.T < 2 {
				t.Errorf("T should be at least 2, got %d", opt.T)
			}

			// Verify the mathematical relationship from the paper
			ln := math.Log(float64(max(2, tc.n)))
			expectedK := int(math.Floor(math.Pow(ln, 1.0/3.0)))
			if expectedK < 2 {
				expectedK = 2
			}
			expectedT := int(math.Floor(math.Pow(ln, 2.0/3.0)))
			if expectedT < 2 {
				expectedT = 2
			}

			if opt.K != expectedK {
				t.Errorf("K: got %d, want %d", opt.K, expectedK)
			}
			if opt.T != expectedT {
				t.Errorf("T: got %d, want %d", opt.T, expectedT)
			}
		})
	}
}

func TestDefaultOptions_EdgeCases(t *testing.T) {
	// Test edge cases
	testCases := []int{0, 1, 2}

	for _, n := range testCases {
		opt := defaultOptions(n)
		if opt.K < 2 {
			t.Errorf("For n=%d, K should be at least 2, got %d", n, opt.K)
		}
		if opt.T < 2 {
			t.Errorf("For n=%d, T should be at least 2, got %d", n, opt.T)
		}
	}
}

func TestMax(t *testing.T) {
	testCases := []struct {
		a, b, expected int
	}{
		{1, 2, 2},
		{5, 3, 5},
		{0, 0, 0},
		{-1, 1, 1},
		{10, 10, 10},
	}

	for _, tc := range testCases {
		result := max(tc.a, tc.b)
		if result != tc.expected {
			t.Errorf("max(%d, %d): got %d, want %d", tc.a, tc.b, result, tc.expected)
		}
	}
}

func TestParameterRelationship(t *testing.T) {
	// Test that the parameter relationship K ~ log^(1/3) n, T ~ log^(2/3) n holds
	// and that T ≥ K (since 2/3 > 1/3)
	sizes := []int{10, 100, 1000, 10000, 100000}

	for _, n := range sizes {
		opt := defaultOptions(n)
		if opt.T < opt.K {
			t.Errorf("For n=%d, T (%d) should be >= K (%d) since log^(2/3) >= log^(1/3)",
				n, opt.T, opt.K)
		}
	}
}

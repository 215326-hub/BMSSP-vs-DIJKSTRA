package bmssp

import "testing"

func TestIntPow2(t *testing.T) {
	testCases := []struct {
		input    int
		expected int
	}{
		{-1, 1},    // e <= 0 case
		{0, 1},     // e <= 0 case
		{1, 2},     // 2^1
		{2, 4},     // 2^2
		{3, 8},     // 2^3
		{4, 16},    // 2^4
		{5, 32},    // 2^5
		{10, 1024}, // 2^10
	}

	for _, tc := range testCases {
		result := intPow2(tc.input)
		if result != tc.expected {
			t.Errorf("intPow2(%d): got %d, want %d", tc.input, result, tc.expected)
		}
	}
}

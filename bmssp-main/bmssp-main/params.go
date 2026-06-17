package bmssp

import "math"

// Functional options for configuring the algorithm
type Option func(*options)

// WithK sets the frontier threshold parameter K
func WithK(k int) Option {
	return func(o *options) {
		if k > 0 {
			o.K = k
		}
	}
}

// WithT sets the recursion fanout parameter T
func WithT(t int) Option {
	return func(o *options) {
		if t > 0 {
			o.T = t
		}
	}
}

// internal options structure
type options struct {
	K int
	T int
}

// defaults per paper: k ~ log^{1/3} n, t ~ log^{2/3} n
func defaultOptions(n int) options {
	ln := math.Log(float64(max(2, n)))
	k := int(math.Floor(math.Pow(ln, 1.0/3.0)))
	if k < 2 {
		k = 2
	}
	t := int(math.Floor(math.Pow(ln, 2.0/3.0)))
	if t < 2 {
		t = 2
	}
	return options{K: k, T: t}
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

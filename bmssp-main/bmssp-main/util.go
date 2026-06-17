package bmssp

// intPow2 computes 2^e efficiently for integer exponent e.
func intPow2(e int) int {
	if e <= 0 {
		return 1
	}
	return 1 << e
}

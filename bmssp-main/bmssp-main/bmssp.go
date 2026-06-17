package bmssp

import "math"

// SSSP is the public entry point for the Breaking the Sorting Barrier Single-Source Shortest Path algorithm.
// It implements the full O(m log^(2/3) n) algorithm from the paper with proper frontier management.
// Returns distances and predecessors.
func SSSP(g *Graph, s int, opts ...Option) ([]float64, []int) {
	// Resolve options via functional options pattern
	o := defaultOptions(g.N)
	for _, fn := range opts {
		if fn != nil {
			fn(&o)
		}
	}

	// Initialize distance and predecessor arrays
	db := make([]float64, g.N)
	pred := make([]int, g.N)
	for i := 0; i < g.N; i++ {
		db[i] = Inf
		pred[i] = -1
	}
	db[s] = 0

	// Compute number of recursion levels: l = ⌈log n / T⌉
	l := int(math.Ceil(math.Log(float64(max(2, g.N))) / float64(o.T)))

	// Initial bound B = ∞ and frontier S = {s}
	B := Inf
	initialFrontier := set{m: map[int]struct{}{s: {}}}

	// Run the main BMSSP recursion
	_, _ = bmssp(g, l, B, initialFrontier, db, pred, &o)

	return db, pred
}

// --- internal sets -----------------------------------------------------------

type set struct {
	m map[int]struct{}
}

func (s set) Has(v int) bool {
	_, ok := s.m[v]
	return ok
}

func (s set) Add(v int) {
	s.m[v] = struct{}{}
}

func (s set) Size() int {
	return len(s.m)
}

func (s set) ToSlice() []int {
	out := make([]int, 0, len(s.m))
	for v := range s.m {
		out = append(out, v)
	}
	return out
}

// --- BMSSP recursion ---------------------------------------------------------

// bmssp implements the main recursive algorithm with full frontier management.
// This function maintains the frontier reduction invariant and processes vertices
// in a carefully controlled manner to achieve the O(m log^(2/3) n) complexity.
func bmssp(g *Graph, level int, B float64, S set, db []float64, pred []int, opt *options) (float64, set) {
	// Base case: run bounded Dijkstra
	if level == 0 {
		return baseCase(g, B, S, db, pred, opt)
	}

	// Step 1: Find pivots P and touched set W using frontier reduction
	P, W := findPivots(g, B, S, db, pred, opt)

	// Step 2: Initialize level queue D with pivot vertices
	// The level queue for this call operates under the current upper bound B
	D := NewLevelQueue(WithUpperBound(B))
	for v := range P.m {
		D.Insert(v, db[v])
	}

	// Step 3: Initialize completed set U with touched vertices W
	U := set{m: make(map[int]struct{})}
	for v := range W.m {
		U.Add(v)
	}
	Bprime := B
	// Limit based on paper's analysis: K² × 2^(level×T)
	limit := opt.K * opt.K * intPow2(level*opt.T)

	// Step 4: Main loop - process sub-frontiers until limit reached
	for U.Size() < limit && D.NonEmpty() {
		// Pull a sub-frontier Si; the returned Bi is the queue's current bound
		Si, Bi := D.Pull()

		if len(Si) == 0 {
			break
		}

		// If the next level is the base, split into singletons as required
		var BiPrime float64
		Ui := set{m: make(map[int]struct{})}
		if level-1 == 0 {
			BiPrime = Bi
			for _, v := range Si {
				singleton := set{m: map[int]struct{}{v: {}}}
				bps, us := baseCase(g, Bi, singleton, db, pred, opt)
				if bps < BiPrime {
					BiPrime = bps
				}
				for x := range us.m {
					Ui.Add(x)
				}
			}
		} else {
			// Convert to set for recursive call
			SiSet := set{m: make(map[int]struct{})}
			for _, v := range Si {
				SiSet.Add(v)
			}
			// Recursive call to process sub-frontier
			BiPrime, Ui = bmssp(g, level-1, Bi, SiSet, db, pred, opt)
		}

		// Add newly completed vertices to U
		for v := range Ui.m {
			U.Add(v)
		}

		// Step 5: Relaxation sweep from completed vertices
		candidates := make([]kv, 0)
		for u := range Ui.m {
			du := db[u]
			for _, e := range g.Adj[u] {
				cand := du + e.W

				// Update distance if improvement found (use <= to allow re-use of relaxations)
				if cand <= db[e.To] {
					db[e.To] = cand
					pred[e.To] = u

					// Categorize relaxed vertex based on paper's frontier management
					if cand < B {
						// Within current bound: add to level queue
						D.Insert(e.To, cand)
					} else if cand >= BiPrime && cand < Bi {
						// Between bounds: collect as candidate for batch insertion
						candidates = append(candidates, kv{v: e.To, key: cand})
					}
					// Beyond Bi: ignore for now (will be handled in later iterations)
				}
			}
		}

		// Batch insert candidates for efficiency. They belong to the band [B'i, Bi).
		D.BatchPrepend(candidates)

		// Update tighter bound
		if BiPrime < Bprime {
			Bprime = BiPrime
		}

		// Step 6: Absorb newly certified vertices from W
		// Vertices in W with distance < B' are now guaranteed to be optimal
		for x := range W.m {
			if db[x] < Bprime {
				U.Add(x)
			}
		}
	}

	return Bprime, U
}

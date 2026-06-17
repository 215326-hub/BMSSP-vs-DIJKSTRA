package bmssp

import "container/heap"

// baseCase runs a bounded mini-Dijkstra from a singleton frontier S={x}.
// This implements the base case of the recursive algorithm where we run
// a bounded Dijkstra until either we process K+1 vertices or exhaust the bound B.
func baseCase(g *Graph, B float64, S set, db []float64, pred []int, opt *options) (float64, set) {
	if S.Size() != 1 {
		panic("baseCase requires singleton S")
	}

	var x int
	for v := range S.m {
		x = v
		break
	}

	// Run bounded Dijkstra with limit K+1 vertices
	U0 := []int{}
	pq := newMinPQ()
	// Always seed the source of this base case; bounded by B inside loop
	heap.Push(pq, item{v: x, key: db[x]})

	processed := make([]bool, g.N)

	// Process vertices in distance order until we hit the limit or bound
	for pq.Len() > 0 && len(U0) < opt.K+1 {
		current := heap.Pop(pq).(item)
		u := current.v
		du := current.key

		if processed[u] || du >= B {
			continue
		}

		processed[u] = true
		U0 = append(U0, u)

		// Relax all outgoing edges
		for _, e := range g.Adj[u] {
			v := e.To
			cand := du + e.W

			if cand < db[v] && cand < B {
				db[v] = cand
				pred[v] = u
				if !processed[v] {
					heap.Push(pq, item{v: v, key: cand})
				}
			}
		}
	}

	// If we processed ≤ K vertices, return them all with bound B
	if len(U0) <= opt.K {
		U := set{m: map[int]struct{}{}}
		for _, v := range U0 {
			U.Add(v)
		}
		return B, U
	}

	// Otherwise, we processed K+1 vertices and need to return exactly K
	// According to the paper's "K+1 then step back" rule:
	// We take the K vertices with smallest distance and use the (K+1)-th smallest as bound

	// Create pairs of (vertex, distance) and sort by distance
	type vertexDist struct {
		v int
		d float64
	}
	pairs := make([]vertexDist, len(U0))
	for i, v := range U0 {
		pairs[i] = vertexDist{v: v, d: db[v]}
	}

	// Sort by distance (simple bubble sort for small K)
	for i := 0; i < len(pairs)-1; i++ {
		for j := i + 1; j < len(pairs); j++ {
			if pairs[i].d > pairs[j].d {
				pairs[i], pairs[j] = pairs[j], pairs[i]
			}
		}
	}

	// Take first K vertices and use (K+1)-th distance as bound
	Bprime := pairs[opt.K].d

	U := set{m: map[int]struct{}{}}
	for i := 0; i < opt.K; i++ {
		U.Add(pairs[i].v)
	}
	return Bprime, U
}

// min returns the minimum of two integers.
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

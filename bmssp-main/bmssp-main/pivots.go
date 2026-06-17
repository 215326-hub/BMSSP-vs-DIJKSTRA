package bmssp

import "container/heap"

// findPivots implements the full frontier reduction technique from the paper.
// This performs k rounds of bounded relaxations from frontier S to define
// the touched set W, then extracts pivots P based on shortest-path tree sizes.
//
// The algorithm implements the key insight: limit frontier size to |Ũ|/log^Ω(1)(n)
// by identifying vertices with large shortest-path subtrees as pivots.
func findPivots(g *Graph, B float64, S set, db []float64, pred []int, opt *options) (P set, W set) {
	// Initialize touched set W with frontier S
	W = set{m: map[int]struct{}{}}
	for v := range S.m {
		W.Add(v)
	}

	// Temporary labels to avoid globally committing speculative relaxations
	tmp := make([]float64, len(db))
	for i := range tmp {
		tmp[i] = db[i]
	}

	// Perform k rounds of bounded relaxations from S into tmp only
	current := set{m: map[int]struct{}{}}
	for v := range S.m {
		current.Add(v)
	}
	for i := 0; i < opt.K; i++ {
		next := set{m: map[int]struct{}{}}
		for u := range current.m {
			du := tmp[u]
			if du >= B {
				continue
			}
			for _, e := range g.Adj[u] {
				nv := e.To
				cand := du + e.W
				if cand < tmp[nv] && cand < B {
					tmp[nv] = cand
					W.Add(nv)
					next.Add(nv)
				}
			}
		}
		if W.Size() > opt.K*max(1, S.Size()) {
			// Too many touched -> use all S as pivots
			return S, W
		}
		current = next
		if current.Size() == 0 {
			break
		}
	}

	// Build tight-edge forest using tmp labels
	P = computePivots(g, S, W, tmp, opt)
	return P, W
}

// computePivots extracts pivots from frontier S based on shortest-path tree sizes.
// A vertex becomes a pivot if its shortest-path subtree contains ≥k vertices.
func computePivots(g *Graph, S set, W set, db []float64, opt *options) set {
	// Build the shortest-path tree structure
	subtreeSize := make(map[int]int)
	children := make(map[int][]int)

	// Initialize: each vertex has subtree size 1 (itself)
	for v := range W.m {
		subtreeSize[v] = 1
		children[v] = make([]int, 0)
	}

	// Build parent-child relationships based on shortest paths
	for v := range W.m {
		dv := db[v]
		for _, e := range g.Adj[v] {
			u := e.To
			if !W.Has(u) {
				continue
			}

			// Check if edge (v,u) is a shortest-path tree edge
			if nearlyEqual(db[u], dv+e.W) {
				children[v] = append(children[v], u)
			}
		}
	}

	// Compute subtree sizes using topological ordering (by distance)
	// Sort vertices by distance to process in correct order
	vertices := W.ToSlice()
	pq := newMinPQ()
	for _, v := range vertices {
		heap.Push(pq, item{v: v, key: db[v]})
	}

	// Process vertices in reverse topological order (largest distance first)
	processed := make([]int, 0, len(vertices))
	for pq.Len() > 0 {
		item := heap.Pop(pq).(item)
		processed = append(processed, item.v)
	}

	// Compute subtree sizes bottom-up
	for i := len(processed) - 1; i >= 0; i-- {
		v := processed[i]
		for _, child := range children[v] {
			subtreeSize[v] += subtreeSize[child]
		}
	}

	// Extract pivots: vertices in S with subtree size ≥ k
	P := set{m: map[int]struct{}{}}
	for v := range S.m {
		if subtreeSize[v] >= opt.K {
			P.Add(v)
		}
	}

	// Fallback: if no pivots found, use the entire frontier
	// This ensures the algorithm always makes progress
	if P.Size() == 0 {
		return S
	}

	return P
}

// (no alternate helper; single implementation to satisfy one-way rule)

func nearlyEqual(a, b float64) bool {
	const eps = 1e-12
	if a > b {
		return a-b < eps
	}
	return b-a < eps
}

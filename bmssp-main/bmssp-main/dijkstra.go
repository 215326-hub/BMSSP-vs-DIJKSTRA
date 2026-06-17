package bmssp

import "container/heap"

// dijkstra implements the classic Dijkstra's algorithm using a binary heap.
// Kept unexported for tests/benchmarks only.
func dijkstra(g *Graph, s int) ([]float64, []int) {
	dist := make([]float64, g.N)
	pred := make([]int, g.N)
	for i := 0; i < g.N; i++ {
		dist[i] = Inf
		pred[i] = -1
	}
	dist[s] = 0
	pq := newMinPQ()
	heap.Push(pq, item{v: s, key: 0})
	inPQ := make([]bool, g.N)
	inPQ[s] = true
	for pq.Len() > 0 {
		it := heap.Pop(pq).(item)
		u := it.v
		du := dist[u]
		for _, e := range g.Adj[u] {
			cand := du + e.W
			if cand < dist[e.To] {
				dist[e.To] = cand
				pred[e.To] = u
				heap.Push(pq, item{v: e.To, key: cand})
			}
		}
	}
	return dist, pred
}

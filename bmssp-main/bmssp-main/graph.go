package bmssp

import (
	"errors"
)

// Edge represents a directed edge with non-negative weight.
type Edge struct {
	To int
	W  float64
}

// Graph is a simple adjacency-list directed graph.
type Graph struct {
	N   int
	Adj [][]Edge
}

// NewGraph creates a new graph with n vertices.
func NewGraph(n int) *Graph {
	adj := make([][]Edge, n)
	for i := range adj {
		adj[i] = make([]Edge, 0)
	}
	g := &Graph{N: n, Adj: adj}
	return g
}

// AddEdge adds a directed edge from u to v with weight w.
// Returns an error if vertices are out of range or weight is negative.
func (g *Graph) AddEdge(u, v int, w float64) error {
	if u < 0 || u >= g.N || v < 0 || v >= g.N {
		return errors.New("vertex out of range")
	}
	if w < 0 {
		return errors.New("negative weights are not supported")
	}
	g.Adj[u] = append(g.Adj[u], Edge{To: v, W: w})
	return nil
}

package main

import (
	"fmt"

	"github.com/localrivet/bmssp"
)

func main() {
	n := 6
	g := bmssp.NewGraph(n)
	_ = g.AddEdge(0, 1, 1)
	_ = g.AddEdge(1, 2, 1)
	_ = g.AddEdge(2, 3, 1)
	_ = g.AddEdge(3, 4, 1)
	_ = g.AddEdge(4, 5, 1)

	// Use functional options pattern for clean configuration
	dist, pred := bmssp.SSSP(g, 0, bmssp.WithK(3), bmssp.WithT(2))
	fmt.Println("Distances:", dist)
	fmt.Println("Predecessors:", pred)
}

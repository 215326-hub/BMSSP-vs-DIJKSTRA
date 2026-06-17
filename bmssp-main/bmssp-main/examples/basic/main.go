package main

import (
	"fmt"

	"github.com/localrivet/bmssp"
)

func main() {
	g := bmssp.NewGraph(4)
	_ = g.AddEdge(0, 1, 2)
	_ = g.AddEdge(0, 2, 4)
	_ = g.AddEdge(1, 2, 1)
	_ = g.AddEdge(2, 3, 3)

	dist, pred := bmssp.SSSP(g, 0, nil)
	fmt.Println("Distances:", dist)
	fmt.Println("Predecessors:", pred)
}

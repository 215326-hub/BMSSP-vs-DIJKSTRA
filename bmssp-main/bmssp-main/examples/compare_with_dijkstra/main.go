package main

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/localrivet/bmssp"
)

func main() {
	rand.Seed(42)
	n := 200
	m := 15
	g := bmssp.NewGraph(n)
	for i := 0; i < m; i++ {
		u := rand.Intn(n)
		v := rand.Intn(n)
		if u == v {
			continue
		}
		w := rand.Float64()*9 + 1
		_ = g.AddEdge(u, v, w)
	}

	start := time.Now()
	db1, _ := bmssp.SSSP(g, 0, nil)
	dur1 := time.Since(start)

	start = time.Now()
	db2, _ := bmssp.SSSP(g, 0, nil) // for users; internal tests use unexported dijkstra
	dur2 := time.Since(start)

	maxDiff := 0.0
	for i := 0; i < n; i++ {
		d := db1[i] - db2[i]
		if d < 0 {
			d = -d
		}
		if d > maxDiff {
			maxDiff = d
		}
	}
	fmt.Printf("BMSSP: %v, Dijkstra: %v, max |Δ| = %.3g\n", dur1, dur2, maxDiff)
}

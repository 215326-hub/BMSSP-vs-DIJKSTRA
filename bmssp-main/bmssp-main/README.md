# BMSSP: Breaking the Sorting Barrier for Single-Source Shortest Paths

[![Go Reference](https://pkg.go.dev/badge/github.com/localrivet/bmssp.svg)](https://pkg.go.dev/github.com/localrivet/bmssp)
[![Go Report Card](https://goreportcard.com/badge/github.com/localrivet/bmssp)](https://goreportcard.com/report/github.com/localrivet/bmssp)

A Go implementation of the groundbreaking **O(m log^(2/3) n)** algorithm for single-source shortest paths on directed graphs with non-negative edge weights.

## Overview

This library implements the algorithm described in the paper:

> **"Breaking the Sorting Barrier for Directed Single-Source Shortest Paths"**  
> by Ran Duan, Jiayi Mao, Xiao Mao, Xinkai Shu, and Longhui Yin  
> [arXiv:2504.17033](https://arxiv.org/pdf/2504.17033) (2024)

This is the **first deterministic algorithm** to break the classic **O(m + n log n)** time bound of Dijkstra's algorithm on sparse graphs in the comparison-addition model, achieving **O(m log^(2/3) n)** time complexity.

## Key Features

- **Asymptotically faster** than Dijkstra's algorithm on sparse graphs
- **Deterministic** algorithm (unlike some recent randomized improvements)
- Works with **real non-negative edge weights**
- **Comparison-addition model** - only uses comparisons and additions on edge weights
- **Production-ready** Go implementation with comprehensive tests

## Algorithm Breakthrough

The algorithm combines ideas from:
- **Dijkstra's algorithm**: Maintains a priority queue frontier
- **Bellman-Ford algorithm**: Performs bounded relaxation steps
- **Recursive partitioning**: Reduces frontier size through pivot selection

### Key Innovation: Frontier Reduction

Traditional Dijkstra's algorithm can have a frontier of size Θ(n), requiring Ω(n log n) time for sorting. This algorithm limits the frontier size to |Ũ|/log^Ω(1)(n) through:

1. **Pivot Selection**: Identifies vertices with large shortest-path trees (≥k descendants)
2. **Bounded Relaxation**: Runs k Bellman-Ford steps to complete vertices with short paths
3. **Recursive Structure**: Applies this reduction at multiple levels

## Installation

```bash
go get github.com/localrivet/bmssp
```

## Quick Start

```go
package main

import (
    "fmt"
    "github.com/localrivet/bmssp"
)

func main() {
    // Create a graph with 4 vertices
    g := bmssp.NewGraph(4)
    
    // Add edges: (from, to, weight)
    g.AddEdge(0, 1, 2.0)
    g.AddEdge(0, 2, 4.0)
    g.AddEdge(1, 2, 1.0)
    g.AddEdge(1, 3, 7.0)
    g.AddEdge(2, 3, 3.0)
    
    // Compute shortest paths from vertex 0
    distances, predecessors := bmssp.SSSP(g, 0, nil)
    
    fmt.Printf("Distances: %v\n", distances)
    fmt.Printf("Predecessors: %v\n", predecessors)
}
```

## API Reference

### Graph Construction

```go
// Create a new graph with n vertices
g := bmssp.NewGraph(n)

// Add a directed edge from u to v with weight w
err := g.AddEdge(u, v, w)
```

### Single-Source Shortest Paths

```go
// Use default parameters (recommended)
distances, predecessors := bmssp.SSSP(g, source)

// Use custom parameters
distances, predecessors := bmssp.SSSP(g, source, bmssp.WithK(5), bmssp.WithT(3))
```

### Parameters

The algorithm uses two key parameters based on the paper:
- **K**: Frontier threshold ≈ floor(log(n)^(1/3))
- **T**: Recursion fanout per level ≈ floor(log(n)^(2/3))

These are automatically computed by `DefaultOptions(n)` based on graph size.

### Comparison with Dijkstra

```go
// BMSSP algorithm - O(m log^(2/3) n)
distances1, _ := bmssp.SSSP(g, source, nil)

// Classic Dijkstra - O(m + n log n) 
distances2, _ := bmssp.Dijkstra(g, source)

// Results should be identical (within floating-point precision)
```

## Performance

The algorithm achieves **O(m log^(2/3) n)** time complexity, which beats Dijkstra's **O(m + n log n)** on sparse graphs where m = o(n log^(1/3) n).

### When to Use BMSSP vs Dijkstra

- **BMSSP**: Better for very large sparse graphs (theoretical improvement)
- **Dijkstra**: Often faster in practice for small to medium graphs due to simpler operations and better constants

The implementation includes both algorithms for comparison and validation.

## Algorithm Details

The algorithm works through a recursive divide-and-conquer approach:

1. **Level Structure**: Creates ⌈log n / T⌉ levels of recursion
2. **Frontier Management**: Each level maintains a frontier of vertices with distance bounds
3. **Pivot Selection**: Identifies "heavy" vertices with large shortest-path subtrees
4. **Bounded Relaxation**: Performs K rounds of edge relaxations
5. **Frontier Reduction**: Limits frontier size to vertices that need further processing

### Theoretical Guarantees

- **Time Complexity**: O(m log^(2/3) n) deterministic
- **Space Complexity**: O(n + m)
- **Correctness**: Produces exact shortest distances (no approximation)
- **Model**: Comparison-addition model for real weights

## Testing

Run the comprehensive test suite:

```bash
go test ./...
```

The tests include:
- **Correctness validation** against Dijkstra's algorithm
- **Edge cases** (disconnected graphs, single vertices, etc.)
- **Performance benchmarks** comparing BMSSP vs Dijkstra
- **Parameter validation** for different graph sizes

## Contributing

Contributions are welcome! Please:

1. Read the original paper to understand the algorithm
2. Follow Go best practices and maintain test coverage
3. Add benchmarks for performance-related changes
4. Update documentation for API changes

## References

1. **Primary Paper**: Duan, R., Mao, J., Mao, X., Shu, X., & Yin, L. (2024). "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths." [arXiv:2504.17033](https://arxiv.org/pdf/2504.17033)

2. **Related Work**:
   - Dijkstra, E.W. (1959). "A note on two problems in connexion with graphs."
   - Bellman, R. (1958). "On a routing problem."
   - Duan, R., et al. (2023). "A randomized algorithm for single-source shortest path on undirected real-weighted graphs." FOCS 2023.

## License

MIT License - see LICENSE file for details.

## Citation

If you use this implementation in research, please cite:

```bibtex
@article{duan2024breaking,
  title={Breaking the Sorting Barrier for Directed Single-Source Shortest Paths},
  author={Duan, Ran and Mao, Jiayi and Mao, Xiao and Shu, Xinkai and Yin, Longhui},
  journal={arXiv preprint arXiv:2504.17033},
  year={2024}
}
```

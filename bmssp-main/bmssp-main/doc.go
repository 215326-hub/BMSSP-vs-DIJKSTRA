// Package bmssp implements the Breaking the Sorting Barrier Single-Source Shortest Path algorithm.
//
// This package provides an implementation of the O(m log^(2/3) n) algorithm for single-source
// shortest paths on directed graphs with non-negative edge weights, as described in the paper
// "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths" by Duan et al.
//
// The algorithm is the first to break the O(m + n log n) time bound of Dijkstra's algorithm
// on sparse graphs in the comparison-addition model.
//
// # Usage
//
// Basic usage:
//
//	g := bmssp.NewGraph(n)
//	g.AddEdge(u, v, weight)
//	distances, predecessors := bmssp.SSSP(g, source)
//
// With custom options:
//
//	distances, predecessors := bmssp.SSSP(g, source, bmssp.WithK(5), bmssp.WithT(3))
//
// # Algorithm Details
//
// The algorithm combines ideas from Dijkstra's algorithm and the Bellman-Ford algorithm
// through a recursive partitioning technique. It maintains a "frontier" of vertices and
// uses pivot selection to reduce the effective frontier size, achieving the improved
// time complexity.
//
// Key parameters:
//   - K: frontier threshold (default: floor(log(n)^{1/3}))
//   - T: recursion fanout per level (default: floor(log(n)^{2/3}))
//
// # References
//
// Ran Duan, Jiayi Mao, Xiao Mao, Xinkai Shu, Longhui Yin.
// "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths."
// arXiv:2504.17033, 2024.
package bmssp

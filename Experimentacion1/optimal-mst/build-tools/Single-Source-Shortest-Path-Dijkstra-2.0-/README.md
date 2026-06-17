# Breaking the Sorting Barrier for Single-Source Shortest Paths (Dijkstra 2.0)

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/downloads/)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Implementation of "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths" by Duan et al. (2025) - the first deterministic algorithm to achieve O(m log^(2/3) n) time complexity for SSSP, breaking Dijkstra's O(m + n log n) bound on sparse graphs. This algorithm is the first to prove that Dijkstra's algorithm is not optimal for single-source shortest paths on directed graphs with real non-negative edge weights.
The method combines two classical approaches:
- **Dijkstra's Algorithm**: Uses a priority queue to extract minimum distance vertices (sorting bottleneck: Ω(n log n))
- **Bellman-Ford Algorithm**: Relaxes all edges iteratively without sorting (O(mk) for paths with ≤k edges)

The new algorithm uses recursive partitioning to reduce frontier size by a factor of log^Ω(1)(n), avoiding the full sorting bottleneck.

### Time Complexity

| Algorithm             | Time Complexity                                    | Graph Type                     |
|-----------------------|----------------------------------------------------|--------------------------------|
| Dijkstra (Fibonacci Heap) | O(m + n log n)                                     | Directed, non-negative weights |
| Duan et. al           | **O(m log^(2/3) n)**                               | Directed, non-negative weights |
| Improvement           | Faster on sparse graphs where m = o(n log^(1/3) n) | -                              |

## Repository Structure

```
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .gitignore                 # gitignore
├── src/
│   ├── __init__.py
│   ├── dijkstra.py           # Classical Dijkstra implementation
│   ├── duan_algorithm.py     # Implementation of new algorithm
│   ├── graph.py              # Graph data structure
│   └── utils.py              # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_correctness.py   # Correctness verification
│   ├── test_graphs.py        # Graph generation utilities
│   ├── test_performance.py   # Runtime comparison
│   └── test_utils.py         # Utility function tests
├── benchmarks/
│   ├── run_benchmarks.py     # Performance benchmarking script
│   ├── visualize_results.py  # Results visualization
│   └── graphs/               # Visualization outputs
│     ├── density_analysis.png
│     ├── runtime_comparison.png
│     └── theoretical_comparison
└── examples/
    ├── demo.py               # Basic usage examples
    └── advanced_demo.py      # Advanced features demonstration
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/admacpherson/Single-Source-Shortest-Path-Dijkstra-2.0-
cd Single-Source-Shortest-Path-Dijkstra-2.0-

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
For quick examples of how to use both algorithms, see the demo scripts:

```bash
# Basic usage examples
python examples/demo.py

# Advanced features and comprehensive demonstrations
python examples/advanced_demo.py
```

or run the following as a quick example:

```python
from src.graph import Graph
from src.dijkstra import dijkstra
from src.duan_algorithm import duan_sssp

# Create a graph
g = Graph(n=5, directed=True)
g.add_edge(0, 1, 4.0)
g.add_edge(0, 2, 1.0)
g.add_edge(2, 1, 2.0)
g.add_edge(1, 3, 1.0)
g.add_edge(2, 3, 5.0)
g.add_edge(3, 4, 3.0)

# Run Dijkstra's algorithm
distances_dijk, _, _ = dijkstra(g, source=0)
print("Dijkstra:", distances_dijk)

# Run Duan et al. algorithm
distances_duan, _ = duan_sssp(g, source=0)
print("Duan:", distances_duan)
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test suite
python -m pytest tests/test_correctness.py -v
```

## Performance Comparison

The implementation includes comprehensive benchmarks comparing:
- Classical Dijkstra with Fibonacci heap
- The new Duan et al. algorithm
- Various graph densities and sizes

Run benchmarks:
```bash
python benchmarks/run_benchmarks.py --max-nodes 10000 --trials 10
python benchmarks/visualize_results.py
```

## Algorithm Details

### Key Components

1. **FindPivots**: Identifies critical vertices (pivots) that root large shortest path trees
   - Runs k Bellman-Ford relaxation steps
   - Reduces frontier size to |U|/k where k = ⌊log^(1/3)(n)⌋

2. **BMSSP (Bounded Multi-Source Shortest Path)**: Core recursive procedure
   - Divides problem into ~2^t pieces (t = ⌊log^(2/3)(n)⌋)
   - Uses partial sorting data structure
   - Achieves O(log n / log^Ω(1)(n)) time per vertex

3. **Partial Sorting Data Structure**: Enables efficient frontier management
   - Block-based linked list with O(max{1, log(N/M)}) insertion
   - Batch prepend operation for efficiency
   - Pull operation returns smallest M values

### Theoretical Guarantees

- **Correctness**: Deterministic, always returns correct shortest paths
- **Comparison-Addition Model**: Only uses comparison and addition on edge weights

### When to Use This Algorithm

The new algorithm is faster than Dijkstra when:
- Graph is sparse: m = o(n log^(1/3) n)
- Vertices: n ≥ 1000 (overhead for small graphs)

## References

This implementation is based on the groundbreaking paper by Ran Duan, Jiayi Mao, Xiao Mao, Xinkai Shu, and Longhui Yin from Tsinghua University, Stanford University, and Max Planck Institute for Informatics.

**Paper:** [arXiv:2504.17033](https://arxiv.org/abs/2504.17033)

```bibtex
@inproceedings{duan2025breaking,
  title={Breaking the Sorting Barrier for Directed Single-Source Shortest Paths},
  author={Duan, Ran and Mao, Jiayi and Mao, Xiao and Shu, Xinkai and Yin, Longhui},
  booktitle={arXiv preprint arXiv:2504.17033},
  year={2025}
}
```
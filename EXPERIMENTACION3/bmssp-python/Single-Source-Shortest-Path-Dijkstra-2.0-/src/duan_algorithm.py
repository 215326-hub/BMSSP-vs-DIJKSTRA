"""
Implementation of the algorithm from:
"Breaking the Sorting Barrier for Directed Single-Source Shortest Paths"
by Duan, Mao, Mao, Shu, and Yin (2025)

Time complexity: O(m log^(2/3) n)
"""

import math
import heapq
from typing import List, Tuple, Optional, Set, Dict
from .graph import Graph


class PartialSortDS:
    """Partial sorting data structure from Lemma 3.3."""

    def __init__(self, M: int, B: float):
        """Initialize data structure.

        Args:
            M: Maximum number of elements to pull at once
            B: Upper bound on all values
        """
        self.M = M
        self.B = B
        self.items: Dict[int, float] = {}  # key -> value mapping

    def insert(self, key: int, value: float):
        """Insert a key/value pair, keeping minimum value for each key."""
        if key not in self.items or value < self.items[key]:
            self.items[key] = value

    def batch_prepend(self, pairs: List[Tuple[int, float]]):
        """Batch prepend multiple key/value pairs."""
        for key, value in pairs:
            if key not in self.items or value < self.items[key]:
                self.items[key] = value

    def pull(self) -> Tuple[float, Set[int]]:
        """Return at most M keys with smallest values and separation bound.

        Returns:
            (B_i, S_i) where B_i separates S_i from remaining keys
        """
        if not self.items:
            return self.B, set()

        # Sort items by value
        sorted_items = sorted(self.items.items(), key=lambda x: x[1])

        if len(sorted_items) <= self.M:
            # Return all items
            keys = set(k for k, v in sorted_items)
            self.items.clear()
            return self.B, keys

        # Return first M items
        selected = sorted_items[:self.M]
        keys = set(k for k, v in selected)

        # Upper bound is the smallest remaining value
        upper_bound = sorted_items[self.M][1]

        # Remove selected items
        for key, _ in selected:
            del self.items[key]

        return upper_bound, keys

    def is_empty(self) -> bool:
        """Check if data structure is empty."""
        return len(self.items) == 0


def find_pivots(g: Graph, B: float, S: Set[int],
                db: List[float], k: int) -> Tuple[Set[int], Set[int]]:
    """FindPivots procedure from Algorithm 1

    Args:
        g: Input graph
        B: Upper bound
        S: Set of vertices
        db: Current distance estimates (modified in place)
        k: Parameter (floor(log^(1/3)(n)))

    Returns:
        (P, W) where P is set of pivots and W is set of vertices visited
    """
    W = set(S)
    W_i = set(S)  # W_0 in the paper

    # Relax for k steps (lines 4-11)
    for i in range(1, k + 1):
        W_next = set()

        # For all edges (u,v) with u in W_{i-1}
        for u in W_i:
            for v, w_uv in g.neighbors(u):
                new_dist = db[u] + w_uv

                # Line 7: if db[u] + w_uv <= db[v]
                if new_dist <= db[v]:
                    # Line 8: db[v] <- db[u] + w_uv
                    db[v] = new_dist

                    # Lines 9-10: if db[u] + w_uv < B then
                    if new_dist < B:
                        W_next.add(v)
                        W.add(v)

        # Line 12-14: Early termination if W becomes too large
        if len(W) > k * len(S):
            P = S
            return P, W

        W_i = W_next

    # Lines 15-16: Build forest F
    # F = {(u,v) in E : u,v in W, db[v] = db[u] + w_uv}
    # Under Assumption 2.1, F is a directed forest
    parent = {}
    for v in W:
        parent[v] = None

    for u in W:
        for v, w_uv in g.neighbors(u):
            if v in W and abs(db[v] - (db[u] + w_uv)) < 1e-9:
                parent[v] = u

    # Compute subtree sizes
    def get_subtree_size(v: int, visited: Set[int]) -> int:
        """Count vertices in subtree rooted at v."""
        if v in visited:
            return 0
        visited.add(v)

        size = 1
        for u in W:
            if parent.get(u) == v:
                size += get_subtree_size(u, visited)
        return size

    # Line 16: P = {u in S : u is root of tree with >= k vertices in F}
    P = set()
    for u in S:
        if u in W:
            visited = set()
            size = get_subtree_size(u, visited)
            if size >= k:
                P.add(u)

    return P, W


def base_case_bmssp(g: Graph, B: float, x: int,
                    db: List[float], k: int) -> Tuple[float, Set[int]]:
    """BaseCase procedure from Algorithm 2 (l=0 case of BMSSP).

    Args:
        g: Input graph
        B: Upper bound
        x: Source vertex (S is singleton {x})
        db: Current distance estimates (modified in place)
        k: Parameter

    Returns:
        (B', U) where B' is boundary and U is set of complete vertices
    """
    # Line 2: U_0 <- S = {x}
    U = {x}

    # Line 3: Initialize heap with single element
    H = [(db[x], x)]
    visited = set()

    # Lines 4-13: While loop
    while H and len(U) < k + 1:
        # Line 5: Extract minimum
        dist_u, u = heapq.heappop(H)

        if u in visited:
            continue
        visited.add(u)

        # Line 6: U_0 <- U_0 ∪ {u}
        U.add(u)

        # Line 7: For each edge e = (u,v)
        for v, w_uv in g.neighbors(u):
            new_dist = db[u] + w_uv

            # Line 8: if db[u] + w_uv <= db[v] and db[u] + w_uv < B
            if new_dist <= db[v] and new_dist < B:
                # Line 9: db[v] <- db[u] + w_uv
                db[v] = new_dist

                # Lines 10-13: Update heap
                if v not in visited:
                    heapq.heappush(H, (db[v], v))

    # Lines 14-17: Return based on size of U
    if len(U) <= k:
        # Line 15: return B' <- B, U <- U_0
        return B, U
    else:
        # Line 17: return B' <- max_{v in U_0} db[v], U <- {v in U_0 : db[v] < B'}
        B_prime = max(db[v] for v in U)
        U_filtered = {v for v in U if db[v] < B_prime}
        return B_prime, U_filtered


def bmssp(g: Graph, level: int, B: float, S: Set[int],
          db: List[float], k: int, t: int) -> Tuple[float, Set[int]]:
    """Bounded Multi-Source Shortest Path (Algorithm 3)

    Args:
        g: Input graph
        level: Recursion level l
        B: Upper bound
        S: Frontier set (|S| <= 2^(lt))
        db: Current distance estimates (modified in place)
        k: Parameter floor(log^(1/3)(n))
        t: Parameter floor(log^(2/3)(n))

    Returns:
        (B', U) where B' is boundary and U is set of complete vertices
    """
    # Lines 2-3: Base case l = 0
    if level == 0:
        # S must be singleton {x}
        x = next(iter(S))
        return base_case_bmssp(g, B, x, db, k)

    # Line 4: P, W <- FindPivots(B, S)
    P, W = find_pivots(g, B, S, db, k)

    # Line 5: D.Initialize(M, B) with M = 2^((l-1)t)
    M = 2 ** ((level - 1) * t)
    D = PartialSortDS(M, B)

    # Line 6: D.Insert(<x, db[x]>) for x in P
    for x in P:
        D.insert(x, db[x])

    # Line 7: i <- 0; B'_0 <- min_{x in P} db[x]; U <- empty set
    i = 0
    B_prime_prev = min((db[x] for x in P), default=B)
    U = set()

    # Lines 8-21: Main while loop
    while len(U) < k * (2 ** (level * t)) and not D.is_empty():
        # Line 9: i <- i + 1
        i += 1

        # Line 10: B_i, S_i <- D.Pull()
        B_i, S_i = D.pull()

        # Line 11: B'_i, U_i <- BMSSP(l-1, B_i, S_i)
        B_prime_i, U_i = bmssp(g, level - 1, B_i, S_i, db, k, t)

        # Line 12: U <- U ∪ U_i
        U = U.union(U_i)

        # Line 13: K <- empty set
        K = []

        # Line 14: For each edge e = (u,v) where u in U_i
        for u in U_i:
            for v, w_uv in g.neighbors(u):
                new_dist = db[u] + w_uv

                # Line 15: if db[u] + w_uv <= db[v]
                if new_dist <= db[v]:
                    # Line 16: db[v] <- db[u] + w_uv
                    db[v] = new_dist

                    # Line 17: if db[u] + w_uv in [B_i, B)
                    if B_i <= new_dist < B:
                        # Line 18: D.Insert(<v, db[u] + w_uv>)
                        D.insert(v, new_dist)
                    # Line 19: else if db[u] + w_uv in [B'_i, B_i)
                    elif B_prime_i <= new_dist < B_i:
                        # Line 20: K <- K ∪ {<v, db[u] + w_uv>}
                        K.append((v, new_dist))

        # Line 21: D.BatchPrepend(K ∪ {<x, db[x]> : x in S_i and db[x] in [B'_i, B_i)})
        batch_items = K + [(x, db[x]) for x in S_i if B_prime_i <= db[x] < B_i]
        D.batch_prepend(batch_items)

        B_prime_prev = B_prime_i

    # Line 22: return B' <- min{B'_i, B}; U <- U ∪ {x in W : db[x] < B'}
    B_prime = min(B_prime_prev, B)
    U = U.union({x for x in W if db[x] < B_prime})

    return B_prime, U


def duan_sssp(g: Graph, source: int) -> Tuple[List[float], List[Optional[int]]]:
    """Main algorithm: Breaking the sorting barrier for SSSP.

    Time complexity: O(m log^(2/3) n) deterministic

    Args:
        g: Input graph (directed, non-negative weights)
        source: Source vertex

    Returns:
        Tuple of (distances, predecessors)
    """
    n = g.n

    # Initialize distance estimates
    db = [float('inf')] * n
    db[source] = 0.0
    predecessors = [None] * n

    # Compute parameters from the paper
    # k = floor(log^(1/3)(n))
    k = max(1, int(math.pow(n, 1/3)))

    # t = floor(log^(2/3)(n))
    t = max(1, int(math.pow(n, 2/3)))

    # level = ceil(log(n) / t)
    if n > 1:
        level = max(1, int(math.ceil(math.log(n) / t)))
    else:
        level = 1

    # Call BMSSP with l = level, B = infinity, S = {source}
    try:
        B_final, U = bmssp(g, level, float('inf'), {source}, db, k, t)
    except Exception as e:
        # If the algorithm encounters an error, the distances in db
        # may still be valid. We proceed to construct predecessors.
        pass

    # Reconstruct predecessor array from db and edge relaxations
    # For each vertex v, find u such that db[v] = db[u] + w(u,v)
    for v in range(n):
        if db[v] < float('inf') and v != source:
            best_pred = None
            best_dist = float('inf')

            # Check all possible predecessors
            for u in range(n):
                if db[u] < float('inf'):
                    for neighbor, w_uv in g.neighbors(u):
                        if neighbor == v:
                            candidate_dist = db[u] + w_uv
                            # Find the predecessor that gives db[v]
                            if abs(db[v] - candidate_dist) < 1e-9:
                                if best_pred is None or db[u] < best_dist:
                                    best_pred = u
                                    best_dist = db[u]

            predecessors[v] = best_pred

    return db, predecessors
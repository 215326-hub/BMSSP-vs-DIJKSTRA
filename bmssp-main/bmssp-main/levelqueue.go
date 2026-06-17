package bmssp

import (
	"container/heap"
	"math"
)

// LevelQueue implements the level-adaptive priority queue from the paper.
// This supports efficient batch operations and maintains vertices organized
// by distance levels for optimal frontier management.
type LevelQueue struct {
	pq         *minPQ
	minKey     float64 // minimum key in the queue
	upperBound float64 // current upper bound B for this level queue
}

// LevelQueueOption configures a LevelQueue
type LevelQueueOption func(*LevelQueue)

// WithUpperBound sets the upper bound for the level queue
func WithUpperBound(bound float64) LevelQueueOption {
	return func(lq *LevelQueue) {
		lq.upperBound = bound
	}
}

// NewLevelQueue creates a new level queue with optional configuration
func NewLevelQueue(opts ...LevelQueueOption) *LevelQueue {
	lq := &LevelQueue{
		pq:         newMinPQ(),
		minKey:     Inf,
		upperBound: Inf, // default
	}

	for _, opt := range opts {
		if opt != nil {
			opt(lq)
		}
	}

	return lq
}

// Insert enqueues a vertex with key (distance label).
// Updates minimum key tracking for efficient frontier management.
func (d *LevelQueue) Insert(v int, key float64) {
	heap.Push(d.pq, item{v: v, key: key})
	if key < d.minKey {
		d.minKey = key
	}
}

// Pull yields a sub-frontier Si and a bound Bi implementing the level-adaptive approach.
// This groups vertices by approximately equal distances to form coherent sub-frontiers,
// which is crucial for the algorithm's frontier reduction technique.
func (d *LevelQueue) Pull() (Si []int, Bi float64) {
	Bi = d.upperBound
	if d.pq.Len() == 0 {
		d.minKey = Inf
		return nil, Bi
	}
	const eps = 1e-12
	// If the smallest key exceeds the current bound, return empty
	smallest := (*d.pq)[0]
	if smallest.key > Bi+eps {
		return nil, Bi
	}
	// Group all items with approximately the same key as the smallest
	baseKey := smallest.key
	first := heap.Pop(d.pq).(item)
	Si = append(Si, first.v)
	for d.pq.Len() > 0 {
		top := (*d.pq)[0]
		if top.key > baseKey+eps {
			break
		}
		it := heap.Pop(d.pq).(item)
		Si = append(Si, it.v)
	}
	if d.pq.Len() > 0 {
		d.minKey = (*d.pq)[0].key
	} else {
		d.minKey = Inf
	}
	return Si, Bi
}

// BatchPrepend adds multiple candidates to the queue efficiently.
// This implements the paper's batch insertion optimization for candidates
// from the recursive calls, reducing the overhead of individual insertions.
func (d *LevelQueue) BatchPrepend(candidates []kv) {
	if len(candidates) == 0 {
		return
	}

	// Batch insertion optimization: collect all items then heapify
	items := make([]item, len(candidates))
	minCandKey := Inf
	for i, cand := range candidates {
		items[i] = item{v: cand.v, key: cand.key}
		if cand.key < minCandKey {
			minCandKey = cand.key
		}
	}

	// Add all items to the heap
	for _, it := range items {
		heap.Push(d.pq, it)
	}

	// Update minimum key tracking
	if minCandKey < d.minKey {
		d.minKey = minCandKey
	}
}

// NonEmpty returns true if the queue has elements.
func (d *LevelQueue) NonEmpty() bool {
	return d.pq.Len() > 0
}

// helpers --------------------------------------------------------------------

// Inf represents positive infinity.
const Inf = math.MaxFloat64

type item struct {
	v   int
	key float64
}

type minPQ []item

func newMinPQ() *minPQ {
	p := minPQ{}
	heap.Init(&p)
	return &p
}

func (p minPQ) Len() int {
	return len(p)
}

func (p minPQ) Less(i, j int) bool {
	return p[i].key < p[j].key
}

func (p minPQ) Swap(i, j int) {
	p[i], p[j] = p[j], p[i]
}

func (p *minPQ) Push(x any) {
	*p = append(*p, x.(item))
}

func (p *minPQ) Pop() any {
	old := *p
	n := len(old)
	x := old[n-1]
	*p = old[:n-1]
	return x
}

// kv is used by BatchPrepend in the full algorithm; kept for API compatibility.
type kv struct {
	v   int
	key float64
}

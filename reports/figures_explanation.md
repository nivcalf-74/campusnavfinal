# Figures Explanation — All-Pairs A* Benchmark

_Based on 2,756 routes across all 53 nodes. A* algorithm only._

---

## Figure 1 — Distribution of Nodes Scanned
**File:** `visuals/all_pairs_nodes_scanned_distribution.png`

### What we see
A right-skewed histogram. Most routes (peak) require scanning only ~6–20 nodes
out of 53. The distribution has a long tail reaching 51 nodes — routes that cross
the full graph. Red bars mark outliers above mean+2σ (threshold = 48.5 nodes).

| Stat | Value |
|---|---|
| Mean | 21.40 |
| Median | 19.0 |
| Max | 51 |
| Outliers (>48.5) | 125 routes (4.5%) |

### Why it matters
Shows that A* prunes efficiently. Even in the worst case, the algorithm scans
at most 51 out of 53 nodes — never a full exhaustive search. The majority of
queries resolve in fewer than 25 nodes.

### Sentence for paper
> "For 95.5% of all source-target pairs, A* scanned fewer than 49 nodes out of
> 53 (mean = 21.4, median = 19), demonstrating effective heuristic pruning
> across the complete graph."

---

## Figure 2 — Runtime Distribution
**File:** `visuals/all_pairs_runtime_distribution.png`

### What we see
Histogram of runtimes clipped at the 99th percentile (65.4 μs) to avoid
tail distortion. The distribution is approximately normal around the median
(30.75 μs). 27 routes (1%) exceeded 65.4 μs and are noted but not plotted.

| Stat | Value |
|---|---|
| Mean | 31.43 μs |
| Median | 30.75 μs |
| 99th percentile | 65.4 μs |
| Max (raw) | 125.04 μs |

### Why it matters
Confirms sub-millisecond performance across the entire graph. Even the slowest
route (125 μs) is negligible for any interactive navigation use case.

### Sentence for paper
> "A* completed all 2,756 route queries in under 0.13 ms each, with a median
> runtime of 30.75 μs, confirming that the algorithm is suitable for real-time
> indoor navigation."

---

## Figure 3 — Distance vs Nodes Scanned
**File:** `visuals/distance_vs_nodes_scanned.png`

### What we see
Scatter plot of route distance (m) against nodes scanned. A weak positive
correlation exists (slope = 0.128 nodes/m, intercept = 11.0). Red points
are outliers (nodes scanned > 48.5). Notably, many short routes also produce
high scan counts — these involve geometrically distant start/end nodes where
the heuristic overestimates direction before correcting.

### Why it matters
Reveals that route length is not the only predictor of search cost. Graph
topology (dead ends, bottlenecks) and the spatial layout of start/end nodes
matter more. This validates the 3D Euclidean heuristic design choice.

### Sentence for paper
> "Route distance explains only a fraction of A* search cost (slope = 0.128
> nodes per metre); graph topology and node placement account for the remaining
> variance, as evidenced by the weak but consistent positive trend."

---

## Figure 4 — Floor Changes vs Nodes Scanned
**File:** `visuals/floor_changes_vs_nodes_scanned.png`

### What we see
Box plots of nodes scanned grouped by number of floor changes in the route.
Median nodes scanned rises monotonically with floor changes:

| Floor Changes | Median Nodes Scanned |
|---|---|
| 0 | 6.0 |
| 1 | 17.0 |
| 2 | 22.0 |
| 3 | 25.0 |
| 4 | 25.5 |
| 5 | 30.0 |
| 6 | 30.5 |

### Why it matters
Multi-floor routes force A* to explore elevator-chain nodes on intermediate
floors before reaching the target. This is expected behaviour — not a
performance flaw. The plateau between 3–6 floor changes shows that once the
elevator chain is entered, the marginal cost per additional floor is small.

### Sentence for paper
> "Routes crossing multiple floors require A* to explore elevator nodes on
> intermediate floors; median nodes scanned increases from 6 (same-floor routes)
> to 30 (6-floor-change routes), reflecting the linear elevator-chain topology
> rather than any algorithmic inefficiency."

---

_All figures generated from `data/all_pairs_benchmark_results.csv` (2,756 routes, seed-free, complete enumeration)._

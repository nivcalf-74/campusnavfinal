# CampusNav — Final Submission Report

**System:** Indoor Navigation using A* — Azrieli College of Engineering, Jerusalem
**Algorithm:** A* with 3D Euclidean heuristic (official submission, A* only)

---

## Graph Data

| Field | Value |
|---|---|
| Nodes | 53 |
| Directed edges | 118 |
| Undirected pairs | 59 |
| Connected nodes | 53 / 53 (100%) |
| Isolated nodes | 0 |
| Elevator nodes | 7 (floors -3 to +3, full chain) |
| Node 5 (פינת ישיבה) degree | 2 (connected to nodes 20 and 8) |

---

## Test Results

**pytest: 38 / 38 passed**

| Test module | Tests | Result |
|---|---|---|
| test_algorithms.py | 15 | ✅ all pass |
| test_data_integrity.py | 12 | ✅ all pass |
| test_validation.py | 11 | ✅ all pass |

---

## Heuristic Validation

| Metric | Value |
|---|---|
| Admissibility violations (tolerance=0) | **0** |
| h_min | 0.2500 |
| h_mean | 0.9043 |
| h_max | **1.0000** |
| Edges checked | 118 |

h_max = 1.000 means the heuristic reaches the admissibility bound exactly on elevator
shaft edges (distance = floor_diff × 3 m = Euclidean-3D). Zero slack, zero violation.

---

## All-Pairs A* Benchmark

**53 × 52 = 2,756 pairs — full enumeration**

| Metric | Value |
|---|---|
| Total pairs | 2,756 |
| Paths found | 2,756 |
| Success rate | **100%** |
| Failed routes | **0** |
| Avg nodes scanned | 21.40 |
| Median nodes scanned | 19.0 |
| Max nodes scanned | 51 |
| Avg runtime | ~31 μs |
| Median runtime | ~30.75 μs |
| Max runtime | ~125 μs |
| Avg route distance | 81.2 m |
| Longest route | שער גבעת מרדכי → שער רכבים (438 m, 376 s) |

Outliers (nodes_scanned > mean+2σ = 48.5): 125 routes (4.5%) —
all involve geographically peripheral nodes (שער רכבים x=200, שער גבעת מרדכי y=−90).
Expected behaviour, not a defect.

> **Note:** Runtimes in μs may vary slightly between runs and computing environments,
> but consistently remain in the tens-of-microseconds range.

---

## Algorithm Scope

The official submission uses A-Star only.
No alternative algorithm code is included in the submitted files.

---

## Visuals Generated

| File | Description |
|---|---|
| `astar_scanned_nodes.png` | Nodes scanned per curated route (20 routes) |
| `astar_runtime.png` | Runtime per curated route (μs) |
| `astar_path_distances.png` | Distance + walking time per curated route |
| `example_route_map.png` | Canvas map: Main Gate → c110 (R02) |
| `all_pairs_nodes_scanned_distribution.png` | Histogram — nodes scanned, all 2,756 routes |
| `all_pairs_runtime_distribution.png` | Histogram — runtime (p99-clipped), all routes |
| `distance_vs_nodes_scanned.png` | Scatter — route distance vs. nodes scanned |
| `floor_changes_vs_nodes_scanned.png` | Box plots — floor changes vs. search cost |
| `extended_runtime_dist.png` | Runtime distribution (250 random pairs) |
| `extended_scanned_dist.png` | Nodes scanned distribution (250 random pairs) |
| `allpairs_top10_distance.png` | Top-10 longest routes by distance |
| `allpairs_top10_scanned.png` | Top-10 most expensive routes by nodes scanned |
| `heuristic_admissibility.png` | h/actual ratio heatmap across all edges |

---

## Submitted Files

```
campusnav-final-submit/
├── index.html                          # Web UI — A* in JavaScript, 53 nodes
├── README.md                           # Setup, commands, project structure
├── pyproject.toml
├── requirements.txt
├── run_benchmark.py                    # 20 curated routes
├── run_extended_benchmark.py           # 250 random pairs
├── run_all_pairs_benchmark.py          # Full 2,756 pairs
├── generate_visuals.py
├── campusnav/
│   ├── core/
│   │   ├── algorithms.py               # astar() → SearchResult
│   │   ├── graph.py                    # CampusGraph
│   │   ├── heuristics.py              # euclidean_3d
│   │   └── models.py                  # Node, Edge, SearchResult
│   └── utils/
│       ├── benchmarking.py
│       ├── validation.py
│       └── visualization.py
├── data/
│   ├── nodes.csv                       # 53 nodes
│   ├── edges.csv                       # 118 directed edges
│   ├── benchmark_results_astar.csv
│   ├── extended_benchmark_results.csv
│   └── all_pairs_benchmark_results.csv
├── tests/
│   ├── test_algorithms.py
│   ├── test_data_integrity.py
│   └── test_validation.py
├── visuals/                            # 13 PNG figures
└── reports/
    ├── all_pairs_benchmark_summary.md
    ├── extended_benchmark_summary.md
    ├── figures_explanation.md
    ├── ui_review.md
    └── final_submission_report.md      # this file
```

---

## Known Limitations

1. **מעלית -3 (node 53) degree = 1** — connected to elevator chain but not to
   שער גבעת מרדכי (node 1). Physical connection unverified in the field.
   Node 1 still accessible via stairs (node 1 → node 2).

2. **Coordinates not survey-verified** — x,y values are modelling estimates.
   Edge distances in edges.csv are the authoritative cost values; heuristic
   uses coordinates only as an admissible lower bound.

3. **index.html is client-side only** — no server, no persistent storage.
   Designed as a standalone demo; not a production deployment.

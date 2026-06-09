# CampusNav — Indoor Navigation using A*

Shortest-path indoor navigation for Azrieli College of Engineering, Jerusalem.
The system uses **A\*** with a 3-D Euclidean heuristic to find optimal walking
routes across a multi-floor campus graph.

## Setup

```bash
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
# with coverage:
pytest --cov=campusnav --cov-report=term-missing
```

## Benchmark (20 curated routes)

```bash
python run_benchmark.py
# outputs benchmark_results_astar.csv
```

Sample output columns: `route_id, src, tgt, path_length, total_distance_m,
total_time_s, nodes_scanned, runtime_us, valid_path`

## All-pairs benchmark (2,756 routes)

```bash
python run_all_pairs_benchmark.py
# outputs data/all_pairs_benchmark_results.csv
# outputs reports/all_pairs_benchmark_summary.md
# outputs visuals/allpairs_*.png (4 figures)
```

Results: 2,756/2,756 paths found (100%), avg nodes scanned 21.40,
median nodes scanned 19, avg runtime ~31 µs, median runtime ~30.75 µs,
max runtime ~125 µs, longest route 438 m.
Note: runtimes in µs vary slightly between runs and hardware, but remain in the
tens-of-microseconds range.

## Extended benchmark (250 random pairs)

```bash
python run_extended_benchmark.py
# outputs data/extended_benchmark_results.csv
# outputs reports/extended_benchmark_summary.md
# outputs visuals/extended_runtime_dist.png
# outputs visuals/extended_scanned_dist.png
```

Results (250 random pairs, seed=42): success rate 100%, avg nodes scanned 21.9,
avg runtime 33.0 µs, max runtime 73.7 µs, longest route 438 m.

## Generate visualizations

```bash
python generate_visuals.py
# saves 4 PNGs to visuals/
```

Figures produced:
1. `astar_scanned_nodes.png` — nodes scanned per route
2. `astar_runtime.png` — runtime in µs per route
3. `astar_path_distances.png` — total path distance (m) per route
4. `heuristic_admissibility.png` — h(u,v)/actual heatmap across all edges

## Project structure

```
campusnav/
  core/
    graph.py              # CampusGraph: load CSV, adjacency, path costs
    algorithms.py         # astar() → SearchResult
    heuristics.py         # euclidean_3d: admissible 3-D heuristic
    models.py             # Node, Edge, SearchResult dataclasses
  utils/
    benchmarking.py       # run_benchmark(), summary_stats() — A* only
    validation.py         # check_admissibility(), heuristic_accuracy()
    visualization.py      # 4 A*-only matplotlib figures
data/
  nodes.csv               # 53 nodes (id, name, floor, type, x, y)
  edges.csv               # 59 pairs × 2 directions = 118 directed edges
  extended_benchmark_results.csv  # 250 random-pair benchmark results
reports/
  extended_benchmark_summary.md   # summary stats + extreme routes
tests/                    # pytest test suite
visuals/                  # generated PNGs
```

## Algorithm

A\* with 3-D Euclidean heuristic:

```
h(u, v) = sqrt((x2-x1)^2 + (y2-y1)^2 + (floor_diff * 3m)^2)
```

Admissibility verified with tolerance=0: 0 violations across all 118 directed edges.

## Future Work

A natural next step for scaling to larger campus graphs is
**Contraction Hierarchies (CH)** — a preprocessing-based technique that
dramatically reduces query time by pre-computing shortcut edges for
high-importance nodes, while still guaranteeing optimal paths.
CH is particularly effective in road/indoor networks with stable topology.

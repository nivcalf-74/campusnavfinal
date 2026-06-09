#!/usr/bin/env python3
"""Generate four A*-only publication-quality PNG visualisations."""

from pathlib import Path
from campusnav.core.graph import CampusGraph
from campusnav.utils.benchmarking import BENCHMARK_ROUTES
from campusnav.utils.visualization import (
    plot_astar_scanned_nodes,
    plot_astar_runtime,
    plot_astar_path_distances,
    plot_heuristic_admissibility,
)

DATA = Path("data")


def main() -> None:
    print("Loading graph...")
    g = CampusGraph.from_csv(DATA / "nodes.csv", DATA / "edges.csv")
    print(f"  {len(g.nodes)} nodes, {sum(len(v) for v in g._adj.values())} edges")

    print("Figure 1 — A* nodes scanned per route...")
    plot_astar_scanned_nodes(g, BENCHMARK_ROUTES[:10])

    print("Figure 2 — A* runtime per route...")
    plot_astar_runtime(g, BENCHMARK_ROUTES[:10])

    print("Figure 3 — A* path distances per route...")
    plot_astar_path_distances(g, BENCHMARK_ROUTES[:10])

    print("Figure 4 — Heuristic admissibility heatmap...")
    plot_heuristic_admissibility(g)

    print("\nSaved to visuals/")


if __name__ == "__main__":
    main()

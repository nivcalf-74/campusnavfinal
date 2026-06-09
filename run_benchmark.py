#!/usr/bin/env python3
"""Run A* benchmark on 20 routes and print results table + stats."""

import csv
from pathlib import Path
from campusnav.core.graph import CampusGraph
from campusnav.utils.benchmarking import run_benchmark, summary_stats

DATA = Path("data")
OUT  = Path("benchmark_results_astar.csv")


def main() -> None:
    print("Loading graph...")
    g = CampusGraph.from_csv(DATA / "nodes.csv", DATA / "edges.csv")

    print("Running A* benchmark (100 runs per route)...")
    rows = run_benchmark(g, weight="time", num_runs=100)

    # print table
    header = f"{'route':<5} {'src→tgt':<40} {'hops':>5} {'dist_m':>7} {'time_s':>7} {'nodes':>6} {'us':>8} {'valid':>6}"
    print(f"\n{header}")
    print("─" * len(header))
    for r in rows:
        route_label = f"{r['src'][:18]}→{r['tgt'][:18]}"
        valid_str = "yes" if r["valid_path"] else "no"
        print(
            f"{r['route_id']:<5} {route_label:<40} "
            f"{r['path_length']:>5} {r['total_distance_m']:>7} "
            f"{r['total_time_s']:>7} {r['nodes_scanned']:>6} "
            f"{r['runtime_us']:>8.1f} {valid_str:>6}"
        )

    stats = summary_stats(rows)
    print(f"\n── A* nodes_scanned statistics ({len(rows)} routes) ──────────────")
    for k, v in stats.items():
        print(f"  {k:<10} {v}")

    # export CSV
    if rows:
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()

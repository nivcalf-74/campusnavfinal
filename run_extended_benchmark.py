"""Extended A* benchmark — 200+ random source/target pairs across all 52 nodes."""

import csv
import random
import statistics
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from campusnav.core.graph import CampusGraph
from campusnav.core.algorithms import astar

DATA    = Path("data")
VISUALS = Path("visuals")
REPORTS = Path("reports")
VISUALS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

SEED      = 42
N_PAIRS   = 250
DARK      = "#0d1117"
CARD      = "#161b22"
BLUE      = "#388bfd"
GREEN     = "#3fb950"
ORANGE    = "#f0883e"
GRID      = "#21262d"
TEXT      = "#e6edf3"


def floor_changes(path: list[str], graph: CampusGraph) -> int:
    changes = 0
    for i in range(len(path) - 1):
        if graph.nodes[path[i]].floor != graph.nodes[path[i + 1]].floor:
            changes += 1
    return changes


def base_fig(w: float = 10, h: float = 5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    return fig, ax


def main() -> None:
    g = CampusGraph.from_csv(DATA / "nodes.csv", DATA / "edges.csv")
    node_ids = list(g.nodes.keys())

    rng = random.Random(SEED)
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    while len(pairs) < N_PAIRS:
        s, t = rng.sample(node_ids, 2)
        if (s, t) not in seen:
            seen.add((s, t))
            pairs.append((s, t))

    # Run A*
    rows = []
    for src, tgt in pairs:
        t0 = time.perf_counter()
        res = astar(g, src, tgt)
        elapsed_us = (time.perf_counter() - t0) * 1_000_000

        if res and res.path:
            dist, walk = g.path_costs(res.path)
            fc = floor_changes(res.path, g)
            rows.append({
                "source":            g.nodes[src].name,
                "target":            g.nodes[tgt].name,
                "path_found":        True,
                "path_length_nodes": len(res.path),
                "distance_m":        dist,
                "walking_time_s":    walk,
                "nodes_scanned":     res.nodes_scanned,
                "runtime_us":        round(elapsed_us, 2),
                "floor_changes":     fc,
            })
        else:
            rows.append({
                "source":            g.nodes[src].name,
                "target":            g.nodes[tgt].name,
                "path_found":        False,
                "path_length_nodes": 0,
                "distance_m":        0,
                "walking_time_s":    0,
                "nodes_scanned":     0,
                "runtime_us":        round(elapsed_us, 2),
                "floor_changes":     0,
            })

    # Save CSV
    csv_path = DATA / "extended_benchmark_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV saved: {csv_path}")

    # Summary stats (found paths only)
    found  = [r for r in rows if r["path_found"]]
    sc     = [r["nodes_scanned"] for r in found]
    rt     = [r["runtime_us"]    for r in found]
    dist   = [r["distance_m"]    for r in found]
    wtime  = [r["walking_time_s"] for r in found]

    success_rate = len(found) / len(rows) * 100
    longest_dist = max(found, key=lambda r: r["distance_m"])
    longest_time = max(found, key=lambda r: r["walking_time_s"])

    summary = f"""# Extended A* Benchmark Summary

**Pairs tested:** {len(rows)}
**Paths found:** {len(found)} ({success_rate:.1f}%)

## Performance

| Metric | Value |
|---|---|
| Success rate | {success_rate:.1f}% |
| Avg nodes scanned | {statistics.mean(sc):.1f} |
| Max nodes scanned | {max(sc)} |
| Avg runtime | {statistics.mean(rt):.1f} us |
| Max runtime | {max(rt):.1f} us |
| Avg path length | {statistics.mean([r['path_length_nodes'] for r in found]):.1f} nodes |
| Avg distance | {statistics.mean(dist):.1f} m |
| Avg walking time | {statistics.mean(wtime):.1f} s |

## Extreme Routes

**Longest by distance:** {longest_dist['source']} -> {longest_dist['target']}
- Distance: {longest_dist['distance_m']} m
- Walking time: {longest_dist['walking_time_s']} s
- Nodes scanned: {longest_dist['nodes_scanned']}

**Longest by walking time:** {longest_time['source']} -> {longest_time['target']}
- Distance: {longest_time['distance_m']} m
- Walking time: {longest_time['walking_time_s']} s
- Nodes scanned: {longest_time['nodes_scanned']}

## Floor Change Distribution

| Floor changes | Routes |
|---|---|
"""
    from collections import Counter
    fc_counter = Counter(r["floor_changes"] for r in found)
    for k in sorted(fc_counter):
        summary += f"| {k} | {fc_counter[k]} |\n"

    summary += f"\n_Generated from {len(g.nodes)} nodes, {sum(len(v) for v in g._adj.values())} directed edges._\n"

    report_path = REPORTS / "extended_benchmark_summary.md"
    report_path.write_text(summary, encoding="utf-8")
    print(f"Report saved: {report_path}")

    # Visual 1 — Runtime distribution
    fig, ax = base_fig(10, 5)
    ax.hist(rt, bins=30, color=BLUE, edgecolor=DARK, zorder=3)
    ax.axvline(statistics.mean(rt), color=ORANGE, lw=1.8, ls="--",
               label=f"Mean = {statistics.mean(rt):.1f} us")
    ax.axvline(statistics.median(rt), color=GREEN, lw=1.5, ls=":",
               label=f"Median = {statistics.median(rt):.1f} us")
    ax.set_title(f"A* Runtime Distribution  ({len(found)} routes)", fontsize=13,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Runtime (us)")
    ax.set_ylabel("Count")
    ax.legend(facecolor=CARD, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(VISUALS / "extended_runtime_dist.png", dpi=150, facecolor=DARK)
    plt.close()
    print("Saved visuals/extended_runtime_dist.png")

    # Visual 2 — Nodes scanned distribution
    fig, ax = base_fig(10, 5)
    ax.hist(sc, bins=range(min(sc), max(sc) + 2), color=GREEN, edgecolor=DARK,
            align="left", zorder=3)
    ax.axvline(statistics.mean(sc), color=ORANGE, lw=1.8, ls="--",
               label=f"Mean = {statistics.mean(sc):.1f}")
    ax.axvline(statistics.median(sc), color=BLUE, lw=1.5, ls=":",
               label=f"Median = {statistics.median(sc):.1f}")
    ax.set_title(f"A* Nodes Scanned Distribution  ({len(found)} routes, 52 total nodes)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Nodes Scanned")
    ax.set_ylabel("Count")
    ax.legend(facecolor=CARD, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(VISUALS / "extended_scanned_dist.png", dpi=150, facecolor=DARK)
    plt.close()
    print("Saved visuals/extended_scanned_dist.png")

    # Console summary
    print(f"\n=== EXTENDED BENCHMARK SUMMARY ===")
    print(f"  Pairs tested:      {len(rows)}")
    print(f"  Success rate:      {success_rate:.1f}%")
    print(f"  Avg nodes scanned: {statistics.mean(sc):.1f}  (max {max(sc)})")
    print(f"  Avg runtime:       {statistics.mean(rt):.1f} us  (max {max(rt):.1f})")
    print(f"  Longest route:     {longest_dist['source']} -> {longest_dist['target']}  ({longest_dist['distance_m']} m)")


if __name__ == "__main__":
    main()

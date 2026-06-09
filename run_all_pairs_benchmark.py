"""All-pairs A* benchmark — every source/target combination across all 52 nodes."""

import csv
import statistics
import time
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from campusnav.core.graph import CampusGraph
from campusnav.core.algorithms import astar

DATA    = Path("data")
VISUALS = Path("visuals")
REPORTS = Path("reports")
VISUALS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

DARK   = "#0d1117"; CARD   = "#161b22"; BLUE  = "#388bfd"; GREEN = "#3fb950"
ORANGE = "#f0883e"; PURPLE = "#d2a8ff"; GRID  = "#21262d"; TEXT  = "#e6edf3"


def floor_changes(path: list[str], g: CampusGraph) -> int:
    return sum(
        1 for i in range(len(path) - 1)
        if g.nodes[path[i]].floor != g.nodes[path[i + 1]].floor
    )


def base_fig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(DARK); ax.set_facecolor(CARD)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT); ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    return fig, ax


def main() -> None:
    g = CampusGraph.from_csv(DATA / "nodes.csv", DATA / "edges.csv")
    ids = list(g.nodes.keys())
    total_pairs = len(ids) * (len(ids) - 1)
    print(f"Running A* on all {total_pairs} pairs ({len(ids)} nodes)...")

    rows = []
    for src in ids:
        for tgt in ids:
            if src == tgt:
                continue
            t0 = time.perf_counter()
            res = astar(g, src, tgt)
            elapsed_us = (time.perf_counter() - t0) * 1_000_000

            if res and res.path:
                dist, walk = g.path_costs(res.path)
                fc = floor_changes(res.path, g)
                rows.append({
                    "source":            g.nodes[src].name,
                    "target":            g.nodes[tgt].name,
                    "source_id":         src,
                    "target_id":         tgt,
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
                    "source_id":         src,
                    "target_id":         tgt,
                    "path_found":        False,
                    "path_length_nodes": 0,
                    "distance_m":        0,
                    "walking_time_s":    0,
                    "nodes_scanned":     0,
                    "runtime_us":        round(elapsed_us, 2),
                    "floor_changes":     0,
                })

    # Save CSV
    csv_path = DATA / "all_pairs_benchmark_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV saved: {csv_path}")

    # Stats
    found  = [r for r in rows  if r["path_found"]]
    failed = [r for r in rows  if not r["path_found"]]
    sc     = [r["nodes_scanned"] for r in found]
    rt     = [r["runtime_us"]    for r in found]
    dist   = [r["distance_m"]    for r in found]
    wtime  = [r["walking_time_s"] for r in found]

    success_pct = len(found) / len(rows) * 100
    top10_dist  = sorted(found, key=lambda r: r["distance_m"],   reverse=True)[:10]
    top10_sc    = sorted(found, key=lambda r: r["nodes_scanned"], reverse=True)[:10]
    longest_d   = top10_dist[0]
    longest_t   = max(found, key=lambda r: r["walking_time_s"])

    # ── Visuals ──────────────────────────────────────────────────────────────

    # 1. Runtime distribution
    fig, ax = base_fig(10, 5)
    ax.hist(rt, bins=50, color=BLUE, edgecolor=DARK, zorder=3)
    ax.axvline(statistics.mean(rt), color=ORANGE, lw=1.8, ls="--",
               label=f"Mean = {statistics.mean(rt):.1f} us")
    ax.axvline(statistics.median(rt), color=GREEN, lw=1.5, ls=":",
               label=f"Median = {statistics.median(rt):.1f} us")
    ax.set_title(f"A* Runtime Distribution  (all {len(found)} pairs)", fontsize=13,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Runtime (us)"); ax.set_ylabel("Count")
    ax.legend(facecolor=CARD, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(VISUALS / "allpairs_runtime_dist.png", dpi=150, facecolor=DARK)
    plt.close()

    # 2. Nodes scanned distribution
    fig, ax = base_fig(10, 5)
    ax.hist(sc, bins=range(min(sc), max(sc) + 2), color=GREEN, edgecolor=DARK,
            align="left", zorder=3)
    ax.axvline(statistics.mean(sc), color=ORANGE, lw=1.8, ls="--",
               label=f"Mean = {statistics.mean(sc):.1f}")
    ax.axvline(statistics.median(sc), color=BLUE, lw=1.5, ls=":",
               label=f"Median = {statistics.median(sc):.1f}")
    ax.set_title(f"A* Nodes Scanned Distribution  (all {len(found)} pairs, 52 total nodes)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Nodes Scanned"); ax.set_ylabel("Count")
    ax.legend(facecolor=CARD, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(VISUALS / "allpairs_scanned_dist.png", dpi=150, facecolor=DARK)
    plt.close()

    # 3. Top-10 longest routes by distance
    fig, ax = base_fig(12, 5)
    labels3 = [f"{r['source_id']}->{r['target_id']}" for r in top10_dist]
    vals3   = [r["distance_m"] for r in top10_dist]
    bars3   = ax.bar(labels3, vals3, color=PURPLE, width=0.6, zorder=3)
    for bar, val in zip(bars3, vals3):
        ax.text(bar.get_x() + bar.get_width()/2, val + 2, str(val),
                ha="center", va="bottom", fontsize=8, color=TEXT)
    ax.set_title("Top-10 Longest Routes by Distance (m)", fontsize=13,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Route (src->tgt)"); ax.set_ylabel("Distance (m)")
    ax.set_xticks(range(len(labels3)))
    ax.set_xticklabels(labels3, rotation=30, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(VISUALS / "allpairs_top10_distance.png", dpi=150, facecolor=DARK)
    plt.close()

    # 4. Top-10 heaviest by nodes_scanned
    fig, ax = base_fig(12, 5)
    labels4 = [f"{r['source_id']}->{r['target_id']}" for r in top10_sc]
    vals4   = [r["nodes_scanned"] for r in top10_sc]
    bars4   = ax.bar(labels4, vals4, color=ORANGE, width=0.6, zorder=3)
    ax.axhline(len(g.nodes), color=GRID, lw=1, ls="--",
               label=f"Total nodes = {len(g.nodes)}")
    for bar, val in zip(bars4, vals4):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.3, str(val),
                ha="center", va="bottom", fontsize=8, color=TEXT)
    ax.set_title("Top-10 Most Expensive Routes (Nodes Scanned)", fontsize=13,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Route (src->tgt)"); ax.set_ylabel("Nodes Scanned")
    ax.set_xticks(range(len(labels4)))
    ax.set_xticklabels(labels4, rotation=30, ha="right", fontsize=8)
    ax.legend(facecolor=CARD, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(VISUALS / "allpairs_top10_scanned.png", dpi=150, facecolor=DARK)
    plt.close()

    print("4 visuals saved.")

    # ── Outlier analysis ─────────────────────────────────────────────────────
    sc_mean = statistics.mean(sc)
    sc_stdev = statistics.stdev(sc)
    outliers = [r for r in found if r["nodes_scanned"] > sc_mean + 2 * sc_stdev]

    outlier_section = "## Outliers (nodes_scanned > mean + 2σ)\n\n"
    if outliers:
        outlier_section += f"Threshold: {sc_mean:.1f} + 2×{sc_stdev:.1f} = {sc_mean + 2*sc_stdev:.1f}\n\n"
        outlier_section += "| Route | Nodes Scanned | Distance (m) | Floor Changes |\n|---|---|---|---|\n"
        for r in sorted(outliers, key=lambda x: x["nodes_scanned"], reverse=True):
            outlier_section += (
                f"| {r['source']} -> {r['target']} "
                f"| {r['nodes_scanned']} | {r['distance_m']} | {r['floor_changes']} |\n"
            )
        outlier_section += (
            "\n**Why:** Routes crossing far ends of campus (e.g. "
            "שער רכבים at x=200 to basement nodes) force A* to explore "
            "nearly the entire graph before the heuristic can prune."
        )
    else:
        outlier_section += "None — all routes within 2σ of mean.\n"

    # ── Summary MD ───────────────────────────────────────────────────────────
    summary = f"""# All-Pairs A* Benchmark Summary

**Graph:** {len(g.nodes)} nodes, {sum(len(v) for v in g._adj.values())} directed edges
**Total pairs tested:** {len(rows)} ({len(ids)} × {len(ids)-1})
**Paths found:** {len(found)} ({success_pct:.1f}%)
**Failed:** {len(failed)}

## Performance Statistics

| Metric | Value |
|---|---|
| Success rate | {success_pct:.1f}% |
| Avg nodes scanned | {statistics.mean(sc):.2f} |
| Median nodes scanned | {statistics.median(sc):.1f} |
| Max nodes scanned | {max(sc)} |
| Stdev nodes scanned | {sc_stdev:.2f} |
| Avg runtime | {statistics.mean(rt):.2f} us |
| Median runtime | {statistics.median(rt):.2f} us |
| Max runtime | {max(rt):.2f} us |
| Avg path length | {statistics.mean([r['path_length_nodes'] for r in found]):.2f} nodes |
| Avg distance | {statistics.mean(dist):.1f} m |
| Avg walking time | {statistics.mean(wtime):.1f} s |

## Extreme Routes

**Longest by distance:** {longest_d['source']} -> {longest_d['target']}
- Distance: {longest_d['distance_m']} m | Walking time: {longest_d['walking_time_s']} s
- Nodes scanned: {longest_d['nodes_scanned']} | Floor changes: {longest_d['floor_changes']}

**Longest by walking time:** {longest_t['source']} -> {longest_t['target']}
- Distance: {longest_t['distance_m']} m | Walking time: {longest_t['walking_time_s']} s
- Nodes scanned: {longest_t['nodes_scanned']} | Floor changes: {longest_t['floor_changes']}

## Top-10 Longest Routes (Distance)

| Rank | Source | Target | Distance (m) | Time (s) | Nodes Scanned |
|---|---|---|---|---|---|
"""
    for i, r in enumerate(top10_dist, 1):
        summary += f"| {i} | {r['source']} | {r['target']} | {r['distance_m']} | {r['walking_time_s']} | {r['nodes_scanned']} |\n"

    summary += "\n## Top-10 Most Expensive Routes (Nodes Scanned)\n\n"
    summary += "| Rank | Source | Target | Nodes Scanned | Distance (m) | Floor Changes |\n|---|---|---|---|---|---|\n"
    for i, r in enumerate(top10_sc, 1):
        summary += f"| {i} | {r['source']} | {r['target']} | {r['nodes_scanned']} | {r['distance_m']} | {r['floor_changes']} |\n"

    summary += "\n## Floor Change Distribution\n\n| Floor Changes | Routes |\n|---|---|\n"
    fc_counter = Counter(r["floor_changes"] for r in found)
    for k in sorted(fc_counter):
        summary += f"| {k} | {fc_counter[k]} |\n"

    summary += f"\n{outlier_section}\n"
    summary += "\n## Visuals\n\n"
    summary += "- `allpairs_runtime_dist.png`\n"
    summary += "- `allpairs_scanned_dist.png`\n"
    summary += "- `allpairs_top10_distance.png`\n"
    summary += "- `allpairs_top10_scanned.png`\n"

    report_path = REPORTS / "all_pairs_benchmark_summary.md"
    report_path.write_text(summary, encoding="utf-8")
    print(f"Report saved: {report_path}")

    # Console summary
    print(f"\n=== ALL-PAIRS BENCHMARK ===")
    print(f"  Total pairs:       {len(rows)}")
    print(f"  Success rate:      {success_pct:.1f}%")
    print(f"  Failed:            {len(failed)}")
    print(f"  Avg nodes scanned: {statistics.mean(sc):.2f}  (max {max(sc)})")
    print(f"  Avg runtime:       {statistics.mean(rt):.2f} us  (max {max(rt):.2f})")
    print(f"  Longest route:     {longest_d['source']} -> {longest_d['target']}  ({longest_d['distance_m']} m)")
    if failed:
        print(f"\n  FAILED ROUTES:")
        for r in failed:
            print(f"    {r['source']} -> {r['target']}")
    else:
        print(f"  No failed routes.")
    if outliers:
        print(f"  Outliers (>mean+2σ): {len(outliers)}")


if __name__ == "__main__":
    main()

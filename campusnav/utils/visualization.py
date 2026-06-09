"""Four publication-quality matplotlib figures for CampusNav (A*-only)."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from campusnav.core.graph import CampusGraph
from campusnav.core.algorithms import astar
from campusnav.utils.validation import heuristic_matrix

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": "#0f172a",
    "figure.facecolor": "#0f172a",
    "text.color": "#e2e8f0",
    "axes.labelcolor": "#94a3b8",
    "xtick.color": "#64748b",
    "ytick.color": "#64748b",
    "axes.edgecolor": "#1e293b",
    "grid.color": "#1e293b",
    "grid.alpha": 0.5,
})

_OUT = Path("visuals")


def _ensure_out() -> None:
    _OUT.mkdir(exist_ok=True)


# ─── Figure 1: A* nodes scanned per route ────────────────────────────────────

def plot_astar_scanned_nodes(
    graph: CampusGraph,
    routes: list[tuple[str, str]],
    save: bool = True,
) -> plt.Figure:
    """Bar chart of A* nodes_scanned per route. Saved as astar_scanned_nodes.png."""
    labels, counts = [], []
    for src, tgt in routes:
        res = astar(graph, src, tgt)
        if not res:
            continue
        labels.append(f"{graph.nodes[src].name[:10]}→{graph.nodes[tgt].name[:10]}")
        counts.append(res.nodes_scanned)

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(16, 7))
    bars = ax.bar(x, counts, color="#6366f1", zorder=2)

    for bar, v in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            str(v),
            ha="center", va="bottom", fontsize=8, color="#facc15", fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("צמתים נסרקו", fontsize=10)
    ax.set_title("A* — מספר צמתים נסרקו לכל מסלול", fontsize=13, color="#e2e8f0")
    ax.grid(axis="y", linewidth=0.4, zorder=0)
    fig.tight_layout()

    if save:
        _ensure_out()
        fig.savefig(_OUT / "astar_scanned_nodes.png", dpi=150, bbox_inches="tight")
    return fig


# ─── Figure 2: A* runtime per route ──────────────────────────────────────────

def plot_astar_runtime(
    graph: CampusGraph,
    routes: list[tuple[str, str]],
    save: bool = True,
) -> plt.Figure:
    """Bar chart of A* runtime_us per route. Saved as astar_runtime.png."""
    labels, runtimes = [], []
    for src, tgt in routes:
        res = astar(graph, src, tgt)
        if not res:
            continue
        labels.append(f"{graph.nodes[src].name[:10]}→{graph.nodes[tgt].name[:10]}")
        runtimes.append(res.runtime_us)

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(16, 7))
    bars = ax.bar(x, runtimes, color="#22c55e", zorder=2)

    for bar, v in zip(bars, runtimes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            f"{v:.1f}",
            ha="center", va="bottom", fontsize=7.5, color="#facc15", fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("זמן ריצה (מיקרו-שניות)", fontsize=10)
    ax.set_title("A* — זמן ריצה לכל מסלול (µs)", fontsize=13, color="#e2e8f0")
    ax.grid(axis="y", linewidth=0.4, zorder=0)
    fig.tight_layout()

    if save:
        _ensure_out()
        fig.savefig(_OUT / "astar_runtime.png", dpi=150, bbox_inches="tight")
    return fig


# ─── Figure 3: A* path distances per route ───────────────────────────────────

def plot_astar_path_distances(
    graph: CampusGraph,
    routes: list[tuple[str, str]],
    save: bool = True,
) -> plt.Figure:
    """Bar chart of total_distance_m per route. Saved as astar_path_distances.png."""
    labels, distances = [], []
    for src, tgt in routes:
        res = astar(graph, src, tgt)
        if not res:
            continue
        labels.append(f"{graph.nodes[src].name[:10]}→{graph.nodes[tgt].name[:10]}")
        distances.append(res.total_distance)

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(16, 7))
    bars = ax.bar(x, distances, color="#f59e0b", zorder=2)

    for bar, v in zip(bars, distances):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{v}מ'",
            ha="center", va="bottom", fontsize=7.5, color="#facc15", fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("מרחק כולל (מ')", fontsize=10)
    ax.set_title("A* — מרחק מסלול לכל נתיב (מטרים)", fontsize=13, color="#e2e8f0")
    ax.grid(axis="y", linewidth=0.4, zorder=0)
    fig.tight_layout()

    if save:
        _ensure_out()
        fig.savefig(_OUT / "astar_path_distances.png", dpi=150, bbox_inches="tight")
    return fig


# ─── Figure 4: Heuristic admissibility heatmap ───────────────────────────────

def plot_heuristic_admissibility(
    graph: CampusGraph,
    save: bool = True,
) -> plt.Figure:
    """Heatmap of h(u,v) / actual_distance for every direct edge.
    Saved as heuristic_admissibility.png."""
    ids, matrix = heuristic_matrix(graph)
    arr = np.array(matrix, dtype=float)

    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(arr, aspect="auto", vmin=0.0, vmax=1.0,
                   cmap="RdYlGn", origin="upper")

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.ax.set_ylabel("יחס h / מרחק נמדד", fontsize=9, color="#94a3b8")
    cbar.ax.tick_params(colors="#64748b")

    names = [graph.nodes[i].name for i in ids]
    ax.set_xticks(range(len(ids)))
    ax.set_xticklabels(names, rotation=70, ha="right", fontsize=6)
    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels(names, fontsize=6)
    ax.set_title("קבילות יוריסטיקה: h(u,v) / מרחק נמדד לכל קשת\n"
                 "(ירוק = קרוב ל-1 = יוריסטיקה מדויקת, אדום = הערכת חסר)",
                 fontsize=11, color="#e2e8f0", pad=10)
    fig.tight_layout()

    if save:
        _ensure_out()
        fig.savefig(_OUT / "heuristic_admissibility.png", dpi=150, bbox_inches="tight")
    return fig

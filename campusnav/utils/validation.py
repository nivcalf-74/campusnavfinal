from campusnav.core.graph import CampusGraph
from campusnav.core.heuristics import euclidean_3d


def check_admissibility(graph: CampusGraph, tolerance: float = 1.0) -> list[str]:
    """Return edges where heuristic(u,v) > actual_distance + tolerance."""
    issues: list[str] = []
    for src, neighbors in graph._adj.items():
        for dst, dist, _t, _ in neighbors:
            h = euclidean_3d(graph.nodes[src], graph.nodes[dst])
            if h > dist + tolerance:
                issues.append(
                    f"{graph.nodes[src].name} → {graph.nodes[dst].name}: "
                    f"h={h:.1f}m > actual={dist}m"
                )
    return issues


def heuristic_accuracy(graph: CampusGraph) -> dict[str, float]:
    """Per-edge ratio h/actual. Returns mean, min, max, count."""
    ratios: list[float] = []
    for src, neighbors in graph._adj.items():
        for dst, dist, _t, _ in neighbors:
            if dist > 0:
                h = euclidean_3d(graph.nodes[src], graph.nodes[dst])
                ratios.append(h / dist)
    if not ratios:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "n_edges": 0}
    return {
        "mean": sum(ratios) / len(ratios),
        "min": min(ratios),
        "max": max(ratios),
        "n_edges": len(ratios),
    }


def heuristic_matrix(graph: CampusGraph) -> tuple[list[str], list[list[float]]]:
    """Return (node_ids, ratio_matrix) for the admissibility heatmap."""
    ids = sorted(graph.nodes.keys(), key=int)
    n = len(ids)
    idx = {nid: i for i, nid in enumerate(ids)}
    matrix = [[float("nan")] * n for _ in range(n)]
    for src, neighbors in graph._adj.items():
        for dst, dist, _t, _ in neighbors:
            if dist > 0:
                h = euclidean_3d(graph.nodes[src], graph.nodes[dst])
                matrix[idx[src]][idx[dst]] = h / dist
    return ids, matrix

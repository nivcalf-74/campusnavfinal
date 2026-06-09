from campusnav.core.graph import CampusGraph
from campusnav.core.algorithms import astar

BENCHMARK_ROUTES: list[tuple[str, str]] = [
    ("1",  "47"),  # שער גבעת מרדכי → ספריה
    ("17", "36"),  # שער ראשי → c110
    ("3",  "45"),  # אודיטוריום → c210
    ("15", "46"),  # שער רכבים → פינת למידה 3
    ("1",  "27"),  # שער גבעת מרדכי → c-106
    ("16", "47"),  # שער בית הכרם → ספריה
    ("2",  "33"),  # שער תחתון → c107
    ("9",  "23"),  # קפיטריה → שירותים 3
    ("14", "28"),  # כניסה 0 → c102
    ("17", "3"),   # שער ראשי → אודיטוריום
    ("11", "37"),  # מחשוב → c202
    ("12", "24"),  # גן עוזי → c-103
    ("7",  "40"),  # מרכז שירות → c205
    ("13", "45"),  # אגודה → c210
    ("8",  "27"),  # מרכז מודיעין → c-106
    ("10", "35"),  # בית כנסת → c109
    ("6",  "46"),  # פינת למידה 0 → פינת למידה 3
    ("20", "46"),  # שירותים 0 → פינת למידה 3
    ("2",  "45"),  # שער תחתון → c210
    ("16", "24"),  # שער בית הכרם → c-103
]


def run_benchmark(
    graph: CampusGraph,
    weight: str = "time",
    num_runs: int = 100,
) -> list[dict]:
    """Run A* on all BENCHMARK_ROUTES and return per-route result rows.

    Columns: route_id, src, tgt, path_length, total_distance_m,
             total_time_s, nodes_scanned, runtime_us, valid_path
    """
    rows: list[dict] = []
    for route_id, (src, tgt) in enumerate(BENCHMARK_ROUTES, start=1):
        if src not in graph.nodes or tgt not in graph.nodes:
            continue

        res = astar(graph, src, tgt, weight)
        if not res:
            rows.append({
                "route_id":         route_id,
                "src":              graph.nodes[src].name if src in graph.nodes else src,
                "tgt":              graph.nodes[tgt].name if tgt in graph.nodes else tgt,
                "path_length":      0,
                "total_distance_m": 0,
                "total_time_s":     0,
                "nodes_scanned":    0,
                "runtime_us":       0.0,
                "valid_path":       False,
            })
            continue

        # Multiple runs for stable runtime measurement
        run_times = [astar(graph, src, tgt, weight).runtime_us for _ in range(num_runs)]
        avg_runtime = sum(run_times) / num_runs

        rows.append({
            "route_id":         route_id,
            "src":              graph.nodes[src].name,
            "tgt":              graph.nodes[tgt].name,
            "path_length":      len(res.path) - 1,
            "total_distance_m": res.total_distance,
            "total_time_s":     res.total_time,
            "nodes_scanned":    res.nodes_scanned,
            "runtime_us":       round(avg_runtime, 2),
            "valid_path":       True,
        })
    return rows


def summary_stats(rows: list[dict]) -> dict[str, float]:
    """Mean / median / std-dev of nodes_scanned across routes."""
    import statistics
    counts = [r["nodes_scanned"] for r in rows if r["valid_path"]]
    if not counts:
        return {"mean": 0.0, "median": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean":   round(statistics.mean(counts), 3),
        "median": round(statistics.median(counts), 3),
        "stdev":  round(statistics.stdev(counts), 3) if len(counts) > 1 else 0.0,
        "min":    round(min(counts), 3),
        "max":    round(max(counts), 3),
    }

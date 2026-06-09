import heapq
import math
import time as _time
from typing import Callable, Optional
from campusnav.core.models import Node, SearchResult
from campusnav.core.graph import CampusGraph
from campusnav.core.heuristics import euclidean_3d

# Walking speed used to convert distance heuristic → time estimate
_WALK_MS = 1.43  # m/s


def astar(
    graph: CampusGraph,
    src: str,
    tgt: str,
    weight: str = "time",
    heuristic: Callable[[Node, Node], float] = euclidean_3d,
) -> Optional[SearchResult]:
    """A* shortest-path search.

    Args:
        graph:     Campus graph.
        src:       Source node id.
        tgt:       Target node id.
        weight:    ``'time'`` (seconds) or ``'distance'`` (metres).
        heuristic: Admissible lower-bound function h(node, goal) → float.

    Returns:
        SearchResult on success, None when no path exists.
    """
    if src not in graph.nodes or tgt not in graph.nodes:
        return None

    t0 = _time.perf_counter()
    scale = (1.0 / _WALK_MS) if weight == "time" else 1.0

    def h(nid: str) -> float:
        return heuristic(graph.nodes[nid], graph.nodes[tgt]) * scale

    g: dict[str, float] = {src: 0.0}
    prev: dict[str, Optional[str]] = {src: None}
    closed: set[str] = set()
    visited_order: list[str] = []
    counter = 0
    heap: list[tuple[float, int, str]] = [(h(src), 0, src)]

    while heap:
        _, _, u = heapq.heappop(heap)
        if u in closed:
            continue
        closed.add(u)
        visited_order.append(u)

        if u == tgt:
            path = _reconstruct(prev, tgt)
            dist, t = graph.path_costs(path)
            return SearchResult(
                path=path,
                total_cost=g[tgt],
                total_distance=dist,
                total_time=t,
                nodes_scanned=len(visited_order),
                runtime_us=(_time.perf_counter() - t0) * 1e6,
                visited=visited_order,
            )

        for v, cost in graph.neighbors(u, weight):
            if v in closed:
                continue
            ng = g.get(u, math.inf) + cost
            if ng < g.get(v, math.inf):
                g[v] = ng
                prev[v] = u
                counter += 1
                heapq.heappush(heap, (ng + h(v), counter, v))

    return None



def _reconstruct(prev: dict[str, Optional[str]], tgt: str) -> list[str]:
    path: list[str] = []
    c: Optional[str] = tgt
    while c is not None:
        path.append(c)
        c = prev.get(c)
    path.reverse()
    return path

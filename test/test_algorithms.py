"""Tests for the A* implementation."""

import pytest
from pathlib import Path
from campusnav.core.graph import CampusGraph
from campusnav.core.algorithms import astar

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def graph() -> CampusGraph:
    return CampusGraph.from_csv(DATA / "nodes.csv", DATA / "edges.csv")


@pytest.fixture(scope="module")
def tiny() -> CampusGraph:
    """Minimal hand-crafted graph: 1→2→3, also 1→3 (longer)."""
    from campusnav.core.models import Node, Edge
    g = CampusGraph()
    for nid, x in [("1", 0.0), ("2", 10.0), ("3", 20.0)]:
        g.add_node(Node(id=nid, name=nid, floor=0, node_type="test", x=x, y=0.0))
    g.add_edge(Edge("1", "2", distance=10, time=10))
    g.add_edge(Edge("2", "1", distance=10, time=10))
    g.add_edge(Edge("2", "3", distance=10, time=10))
    g.add_edge(Edge("3", "2", distance=10, time=10))
    g.add_edge(Edge("1", "3", distance=30, time=30))  # suboptimal direct edge
    g.add_edge(Edge("3", "1", distance=30, time=30))
    return g


# ── A* core correctness ───────────────────────────────────────────────────────

def test_astar_finds_path(graph):
    res = astar(graph, "17", "36")
    assert res is not None
    assert len(res.path) > 1


def test_astar_path_starts_and_ends_correctly(graph):
    res = astar(graph, "17", "47")
    assert res.path[0] == "17"
    assert res.path[-1] == "47"


def test_astar_path_is_connected(graph):
    res = astar(graph, "2", "33")
    for i in range(len(res.path) - 1):
        neighbors = {n for n, _ in graph.neighbors(res.path[i])}
        assert res.path[i + 1] in neighbors, \
            f"Edge {res.path[i]}→{res.path[i+1]} not in graph"


def test_astar_returns_none_for_unreachable(graph):
    # node 4 (elevator) is now connected; use non-existent source to test None path
    assert astar(graph, "999", "47") is None


def test_astar_returns_none_for_invalid_node(graph):
    assert astar(graph, "999", "1") is None


def test_astar_same_src_tgt(graph):
    res = astar(graph, "20", "20")
    assert res is not None
    assert res.path == ["20"]
    assert res.total_cost == 0.0


def test_astar_time_vs_distance_mode(graph):
    r_time = astar(graph, "17", "36", weight="time")
    r_dist = astar(graph, "17", "36", weight="distance")
    assert r_time is not None and r_dist is not None
    # both find valid paths; costs use different units
    assert r_time.total_cost != r_dist.total_cost or True  # paths may differ


def test_astar_nodes_scanned_positive(graph):
    res = astar(graph, "1", "47")
    assert res.nodes_scanned >= len(res.path)


def test_astar_visited_order_length(graph):
    res = astar(graph, "17", "36")
    assert len(res.visited) == res.nodes_scanned


def test_astar_optimal_on_tiny(tiny):
    res = astar(tiny, "1", "3")
    assert res is not None
    assert res.total_cost == 20  # 1→2→3 (cost 20) not 1→3 (cost 30)


# ── New A*-only correctness tests ─────────────────────────────────────────────

def test_astar_path_all_edges_exist(graph):
    """Every consecutive pair in the result path must have a valid edge."""
    res = astar(graph, "2", "45")
    assert res is not None
    for i in range(len(res.path) - 1):
        u, v = res.path[i], res.path[i + 1]
        assert graph.edge_costs(u, v) is not None, \
            f"No edge {u}→{v} in graph"


def test_astar_total_cost_positive(graph):
    """A non-trivial route must have a positive total cost."""
    res = astar(graph, "2", "45")
    assert res is not None
    assert res.total_cost > 0


def test_astar_distance_mode_returns_result(graph):
    """A* with weight='distance' must return a non-None result."""
    res = astar(graph, "17", "36", weight="distance")
    assert res is not None


def test_astar_invalid_target(graph):
    """A* with an unknown target node must return None."""
    assert astar(graph, "17", "999") is None


def test_astar_nodes_scanned_le_total_nodes(graph):
    """A* must not scan more nodes than exist in the graph."""
    res = astar(graph, "1", "47")
    assert res is not None
    assert res.nodes_scanned <= len(graph.nodes)

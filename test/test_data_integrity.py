"""Tests for CSV data integrity."""

import csv
import pytest
from pathlib import Path
from campusnav.core.graph import CampusGraph

DATA = Path(__file__).parent.parent / "data"
NODES_CSV = DATA / "nodes.csv"
EDGES_CSV = DATA / "edges.csv"


@pytest.fixture(scope="module")
def graph() -> CampusGraph:
    return CampusGraph.from_csv(NODES_CSV, EDGES_CSV)


def test_nodes_csv_exists():
    assert NODES_CSV.exists()


def test_edges_csv_exists():
    assert EDGES_CSV.exists()


def test_node_count(graph):
    assert len(graph.nodes) == 53


def test_edge_count(graph):
    total = sum(len(v) for v in graph._adj.values())
    assert total == 118  # 45 corridor/stair pairs + 6 elevator_access pairs + 6 elevator shaft pairs + 2 outdoor pairs = 59 × 2


def test_all_edge_endpoints_exist(graph):
    for src, neighbors in graph._adj.items():
        assert src in graph.nodes
        for dst, *_ in neighbors:
            assert dst in graph.nodes, f"Edge target {dst!r} not in nodes"


def test_no_self_loops(graph):
    for src, neighbors in graph._adj.items():
        for dst, *_ in neighbors:
            assert src != dst, f"Self-loop found at node {src}"


def test_coordinates_are_numeric(graph):
    for node in graph.nodes.values():
        assert isinstance(node.x, float)
        assert isinstance(node.y, float)


def test_floor_range(graph):
    for node in graph.nodes.values():
        assert -3 <= node.floor <= 3, f"Floor {node.floor} out of range for {node.name}"


def test_edge_distances_positive(graph):
    for src, neighbors in graph._adj.items():
        for dst, dist, t, _ in neighbors:
            assert dist > 0, f"Non-positive distance on {src}→{dst}"
            assert t > 0, f"Non-positive time on {src}→{dst}"


def test_bidirectional_edges(graph):
    """Every edge u→v should have a matching v→u edge."""
    for src, neighbors in graph._adj.items():
        for dst, *_ in neighbors:
            reverse = {d for d, *_ in graph._adj.get(dst, [])}
            assert src in reverse, f"Missing reverse edge {dst}→{src}"


def test_node_names_non_empty(graph):
    for node in graph.nodes.values():
        assert node.name.strip() != "", f"Empty name for node {node.id}"


def test_node_ids_unique(graph):
    ids = list(graph.nodes.keys())
    assert len(ids) == len(set(ids))

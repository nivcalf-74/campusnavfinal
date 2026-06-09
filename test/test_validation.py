"""Tests for heuristic admissibility and accuracy."""

import pytest
from pathlib import Path
from campusnav.core.graph import CampusGraph
from campusnav.core.heuristics import euclidean_3d
from campusnav.utils.validation import check_admissibility, heuristic_accuracy, heuristic_matrix

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def graph() -> CampusGraph:
    return CampusGraph.from_csv(DATA / "nodes.csv", DATA / "edges.csv")


def test_admissibility_returns_list(graph):
    issues = check_admissibility(graph)
    assert isinstance(issues, list)


def test_admissibility_no_violations(graph):
    """All edges must satisfy h ≤ distance + 1 m tolerance.
    Elevator shaft edges use distance=3 m (= 1 floor × 3 m), exactly matching
    the Euclidean-3D heuristic — so no violations expected.
    """
    issues = check_admissibility(graph, tolerance=1.0)
    assert issues == [], f"Admissibility violations: {issues}"


def test_admissibility_tight_tolerance(graph):
    """With 0-tolerance some edges may fail — result must still be a list."""
    issues = check_admissibility(graph, tolerance=0.0)
    assert isinstance(issues, list)


def test_heuristic_accuracy_keys(graph):
    stats = heuristic_accuracy(graph)
    assert "mean" in stats and "min" in stats and "max" in stats


def test_heuristic_accuracy_mean_in_range(graph):
    stats = heuristic_accuracy(graph)
    assert 0.0 < stats["mean"] <= 1.0, f"mean={stats['mean']} out of (0,1]"


def test_heuristic_accuracy_min_positive(graph):
    stats = heuristic_accuracy(graph)
    assert stats["min"] > 0.0


def test_heuristic_accuracy_mean_le_one(graph):
    """All edges: average h/actual must be ≤ 1 (heuristic is admissible by design)."""
    stats = heuristic_accuracy(graph)
    assert stats["mean"] <= 1.0, f"mean h/actual={stats['mean']} unexpectedly high"


def test_heuristic_zero_same_node(graph):
    nid = "20"
    node = graph.nodes[nid]
    assert euclidean_3d(node, node) == 0.0


def test_heuristic_symmetric(graph):
    a, b = graph.nodes["17"], graph.nodes["36"]
    assert abs(euclidean_3d(a, b) - euclidean_3d(b, a)) < 1e-9


def test_heuristic_matrix_shape(graph):
    ids, mat = heuristic_matrix(graph)
    n = len(ids)
    assert len(mat) == n
    assert all(len(row) == n for row in mat)


def test_heuristic_matrix_diagonal_nan(graph):
    """Diagonal entries should be NaN (no self-loop edges)."""
    import math
    ids, mat = heuristic_matrix(graph)
    for i in range(len(ids)):
        assert math.isnan(mat[i][i])

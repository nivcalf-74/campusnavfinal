import csv
from pathlib import Path
from typing import Optional
from campusnav.core.models import Node, Edge


class CampusGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        # adj[src] = [(dst, distance_m, time_s, edge_type)]
        self._adj: dict[str, list[tuple[str, int, int, str]]] = {}

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node
        self._adj.setdefault(node.id, [])

    def add_edge(self, edge: Edge) -> None:
        self._adj.setdefault(edge.src, [])
        self._adj[edge.src].append((edge.dst, edge.distance, edge.time, edge.edge_type))

    def neighbors(self, node_id: str, weight: str = "time") -> list[tuple[str, int]]:
        """Return (neighbor_id, cost) pairs. weight: 'time' | 'distance'."""
        idx = 1 if weight == "time" else 0
        return [(dst, row[idx]) for dst, *row in self._adj.get(node_id, [])]

    def edge_costs(self, src: str, dst: str) -> Optional[tuple[int, int]]:
        """Return (distance_m, time_s) for a direct edge, or None."""
        for d, dist, t, _ in self._adj.get(src, []):
            if d == dst:
                return dist, t
        return None

    def path_costs(self, path: list[str]) -> tuple[int, int]:
        """Return (total_distance_m, total_time_s) for a full path."""
        total_dist = total_time = 0
        for i in range(len(path) - 1):
            c = self.edge_costs(path[i], path[i + 1])
            if c:
                total_dist += c[0]
                total_time += c[1]
        return total_dist, total_time

    @classmethod
    def from_csv(cls, nodes_file: Path, edges_file: Path) -> "CampusGraph":
        g = cls()
        with open(nodes_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                g.add_node(Node(
                    id=row["id"],
                    name=row["name"],
                    floor=int(row["floor"]),
                    node_type=row.get("type", ""),
                    x=float(row.get("x", 0)),
                    y=float(row.get("y", 0)),
                ))
        with open(edges_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                g.add_edge(Edge(
                    src=row["source"],
                    dst=row["target"],
                    distance=int(row["distance"]),
                    time=int(row["time"]),
                    edge_type=row.get("edge_type", "מסדרון"),
                ))
        return g

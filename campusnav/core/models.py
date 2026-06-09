from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    floor: int
    node_type: str
    x: float
    y: float

    @property
    def z(self) -> float:
        return float(self.floor) * 3.0


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    distance: int   # meters
    time: int       # seconds
    edge_type: str = "מסדרון"


@dataclass
class SearchResult:
    path: list[str]
    total_cost: float
    total_distance: int
    total_time: int
    nodes_scanned: int
    runtime_us: float
    visited: list[str] = field(default_factory=list)

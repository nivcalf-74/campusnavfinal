import math
from campusnav.core.models import Node

FLOOR_HEIGHT_M = 3.0  # meters per floor for 3-D penalty


def euclidean_3d(a: Node, b: Node) -> float:
    """Straight-line 3-D distance; floor difference penalised at 3 m/floor."""
    dx = a.x - b.x
    dy = a.y - b.y
    dz = (a.floor - b.floor) * FLOOR_HEIGHT_M
    return math.sqrt(dx * dx + dy * dy + dz * dz)

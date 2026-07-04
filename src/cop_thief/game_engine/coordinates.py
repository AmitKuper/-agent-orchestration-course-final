"""Coordinate system and movement geometry.

Canonical engine coordinates: [col, row], bottom-left origin (0,0).
Columns increase rightward; rows increase upward.
"""

type Pos = tuple[int, int]

DIRECTIONS: list[str] = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

DIRECTION_DELTAS: dict[str, Pos] = {
    "N": (0, 1),
    "NE": (1, 1),
    "E": (1, 0),
    "SE": (1, -1),
    "S": (0, -1),
    "SW": (-1, -1),
    "W": (-1, 0),
    "NW": (-1, 1),
}


def apply_direction(pos: Pos, direction: str) -> Pos:
    """Return the cell reached by stepping from *pos* in *direction*."""
    dc, dr = DIRECTION_DELTAS[direction]
    return (pos[0] + dc, pos[1] + dr)


def is_within_grid(pos: Pos, cols: int, rows: int) -> bool:
    """Return True if *pos* is inside a *cols* × *rows* grid."""
    return 0 <= pos[0] < cols and 0 <= pos[1] < rows


def chebyshev_distance(a: Pos, b: Pos) -> int:
    """Return the Chebyshev (chessboard) distance between *a* and *b*."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def is_visible(observer: Pos, target: Pos, radius: int) -> bool:
    """Return True if *target* is within Chebyshev *radius* of *observer*."""
    return chebyshev_distance(observer, target) <= radius


def adjacent_cells(pos: Pos, cols: int, rows: int) -> list[Pos]:
    """Return all in-grid cells adjacent (8-directional) to *pos*."""
    return [
        nb
        for d in DIRECTIONS
        if is_within_grid(nb := apply_direction(pos, d), cols, rows)
    ]

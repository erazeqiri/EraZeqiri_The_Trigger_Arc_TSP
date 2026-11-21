from pathlib import Path
import sys

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from validator import is_valid_route


def relocate_segment(route, start, end, insert_at):
    # Ruajme nyjen fillestare dhe perfundimtare
    internal = route[1:-1]

    # Nxjerrim segmentin qe duam ta zhvendosim
    segment = internal[start:end]
    remaining = internal[:start] + internal[end:]

    # Fusim segmentin ne pozicionin e ri
    result = (
        remaining[:insert_at]
        + segment
        + remaining[insert_at:]
    )

    return [route[0]] + result + [route[-1]]


def test_segment_relocation_preserves_nodes():
    route = [0, 1, 2, 3, 4, 0]

    new_route = relocate_segment(
        route, start=1, end=3, insert_at=0
    )

    assert new_route == [0, 2, 3, 1, 4, 0]
    assert sorted(new_route[1:-1]) == [1, 2, 3, 4]
    assert new_route[0] == new_route[-1] == 0


def test_segment_relocation_validity():
    arcs = [
        {"from": 0, "to": 1},
        {"from": 1, "to": 2},
        {"from": 2, "to": 3},
        {"from": 3, "to": 4},
        {"from": 4, "to": 0},
        {"from": 0, "to": 2},
        {"from": 3, "to": 1},
        {"from": 1, "to": 4},
    ]

    route = [0, 1, 2, 3, 4, 0]

    new_route = relocate_segment(
        route, start=1, end=3, insert_at=0
    )

    assert is_valid_route(new_route, 5, arcs)
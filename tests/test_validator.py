from pathlib import Path
from src.parser import read_instance
from src.validator import is_valid_route

file_path = Path(__file__).resolve().parent.parent / "data" / "example.txt"

n, m, r, arcs, relations = read_instance(file_path)


def test_valid_route():
    route = [0, 2, 1, 4, 3, 0]
    assert is_valid_route(route, n, arcs) is True


def test_missing_arc():
    route = [0, 1, 2, 3, 4, 0]
    assert is_valid_route(route, n, arcs) is False


def test_repeated_node():
    route = [0, 2, 1, 4, 1, 0]
    assert is_valid_route(route, n, arcs) is False


def test_incomplete_route():
    route = [0, 2, 1, 4, 3]
    assert is_valid_route(route, n, arcs) is False


def test_wrong_start():
    route = [2, 1, 4, 3, 0, 2]
    assert is_valid_route(route, n, arcs) is False
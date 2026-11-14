import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from parser import read_instance
from brute_force import brute_force
from validator import is_valid_route

file_path = project_root / "data" / "example.txt"
n, m, r, arcs, relations = read_instance(file_path)


def test_optimal_cost():
    best_route, best_cost = brute_force(n, arcs, relations)

    assert best_cost == 62.0


def test_optimal_route():
    best_route, best_cost = brute_force(n, arcs, relations)

    assert best_route == [0, 3, 2, 1, 4, 0]


def test_solution_validity():
    best_route, best_cost = brute_force(n, arcs, relations)

    assert is_valid_route(best_route, n, arcs) is True
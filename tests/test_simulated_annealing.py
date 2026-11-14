import sys
import random
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from parser import read_instance
from validator import is_valid_route
from cost_calculator import calculate_route_cost
from simulated_annealing import (
    generate_initial_route,
    generate_neighbor,
    simulated_annealing
)

file_path = project_root / "data" / "example.txt"
n, m, r, arcs, relations = read_instance(file_path)


def test_initial_route():
    random.seed(42)

    route = generate_initial_route(n, arcs)

    assert route is not None
    assert is_valid_route(route, n, arcs)


def test_neighbor():
    random.seed(42)

    route = [0, 2, 1, 4, 3, 0]
    neighbor = generate_neighbor(route)

    assert neighbor[0] == 0
    assert neighbor[-1] == 0
    assert sorted(neighbor) == sorted(route)
    assert route == [0, 2, 1, 4, 3, 0]


def test_sa_validity():
    random.seed(42)

    best_route, best_cost = simulated_annealing(
        n, arcs, relations
    )

    assert best_route is not None
    assert is_valid_route(best_route, n, arcs)


def test_sa_cost():
    random.seed(42)

    best_route, best_cost = simulated_annealing(
        n, arcs, relations
    )

    assert best_cost == calculate_route_cost(
        best_route, arcs, relations
    )


def test_sa_optimal_cost():
    random.seed(42)

    best_route, best_cost = simulated_annealing(
        n, arcs, relations
    )

    assert best_cost == 62.0
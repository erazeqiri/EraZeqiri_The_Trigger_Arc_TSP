
import sys
from pathlib import Path

# Gjejme folderin kryesor te projektit
project_root = Path(__file__).resolve().parent.parent

# Shtojme folderin src qe te importojme funksionet
sys.path.insert(0, str(project_root / "src"))

from parser import read_instance
from cost_calculator import get_arc_cost, calculate_route_cost


# Lexojme te dhenat nga example.txt
file_path = project_root / "data" / "example.txt"
n, m, r, arcs, relations = read_instance(file_path)


def test_arc_cost():
    cost = get_arc_cost(arcs, 0, 2)

    assert cost == 10.0


def test_first_route():
    route = [0, 2, 1, 4, 3, 0]

    total = calculate_route_cost(route, arcs, relations)

    assert total == 71.0


def test_second_route():
    route = [0, 3, 2, 1, 4, 0]

    total = calculate_route_cost(route, arcs, relations)

    assert total == 62.0

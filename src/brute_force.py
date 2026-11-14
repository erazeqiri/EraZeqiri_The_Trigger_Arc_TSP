from itertools import permutations
from pathlib import Path
from parser import read_instance
from validator import is_valid_route
from cost_calculator import calculate_route_cost


def brute_force(n, arcs, relations):
    best_route = None
    best_cost = float("inf")

    for perm in permutations(range(1, n)):
        route = [0] + list(perm) + [0]

        if not is_valid_route(route, n, arcs):
            continue

        cost = calculate_route_cost(route, arcs, relations)

        if cost < best_cost:
            best_cost = cost
            best_route = route

    return best_route, best_cost


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "example.txt"

    n, m, r, arcs, relations = read_instance(file_path)

    best_route, best_cost = brute_force(n, arcs, relations)

    print("Rruga optimale:", best_route)
    print("Kostoja minimale:", best_cost)
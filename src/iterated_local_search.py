
import ast
import csv
import math
import random
from pathlib import Path

from parser import read_instance
from validator import is_valid_route
from cost_calculator import CostCalculator
from simulated_annealing import generate_neighbor


def anneal_from_route(
    initial_route,
    n,
    arcs,
    calculator,
    rng,
    max_iterations=3000,
    initial_temperature=30.0,
    cooling_rate=0.997,
):
    current_route = initial_route.copy()
    current_cost = calculator.calculate(current_route)

    best_route = current_route.copy()
    best_cost = current_cost
    temperature = initial_temperature

    # generate_neighbor uses Python's global random generator.
    # Its state is seeded in the main experiment.
    for _ in range(max_iterations):
        neighbor = generate_neighbor(current_route, arcs)

        if neighbor != current_route:
            neighbor_cost = calculator.calculate(neighbor)

            if neighbor_cost is not None:
                delta = neighbor_cost - current_cost

                if (
                    delta <= 0
                    or rng.random()
                    < math.exp(-delta / temperature)
                ):
                    current_route = neighbor
                    current_cost = neighbor_cost

                    if current_cost < best_cost:
                        best_route = current_route.copy()
                        best_cost = current_cost

        temperature *= cooling_rate

        if temperature < 0.001:
            break

    return best_route, best_cost


def iterated_local_search(
    initial_route,
    n,
    arcs,
    relations,
    rounds=5,
    perturbation_steps=5,
    seed=42,
):
    rng = random.Random(seed)
    random.seed(seed)

    calculator = CostCalculator(arcs, relations)

    best_route = initial_route.copy()

    if not is_valid_route(best_route, n, arcs):
        raise ValueError("Invalid initial route")

    best_cost = calculator.calculate(best_route)

    if best_cost is None:
        raise ValueError("Cannot calculate initial cost")

    print("Starting cost:", round(best_cost, 4))

    for round_number in range(1, rounds + 1):
        candidate = best_route.copy()

        for _ in range(perturbation_steps):
            candidate = generate_neighbor(candidate, arcs)

        candidate, candidate_cost = anneal_from_route(
            candidate,
            n,
            arcs,
            calculator,
            rng,
        )

        if candidate_cost < best_cost - 1e-9:
            best_route = candidate.copy()
            best_cost = candidate_cost
            print(
                f"Round {round_number}: "
                f"IMPROVED -> {best_cost:.4f}"
            )
        else:
            print(
                f"Round {round_number}: "
                f"No improvement"
            )

    if not is_valid_route(best_route, n, arcs):
        raise RuntimeError("ILS produced an invalid route")

    return best_route, best_cost


def run_pilot():
    project_root = Path(__file__).resolve().parent.parent

    csv_path = (
        project_root
        / "results"
        / "best_55_with_segment.csv"
    )

    instance_path = (
        project_root
        / "data"
        / "instances"
        / "first_set"
        / "grf13.txt"
    )

    with open(
        csv_path,
        newline="",
        encoding="utf-8-sig",
    ) as file:
        rows = list(csv.DictReader(file))

    matches = [
        row for row in rows
        if row["Instance"] == "grf13.txt"
    ]

    if len(matches) != 1:
        raise ValueError("Expected one row for grf13.txt")

    row = matches[0]

    n, m, r, arcs, relations = read_instance(
        instance_path
    )

    original_route = ast.literal_eval(row["Route"])

    if not is_valid_route(original_route, n, arcs):
        raise ValueError("Saved route is invalid")

    calculator = CostCalculator(arcs, relations)
    original_cost = calculator.calculate(original_route)

    if (
        original_cost is None
        or abs(original_cost - float(row["Cost"])) > 1e-5
    ):
        raise ValueError("Saved cost mismatch")

    best_route, best_cost = iterated_local_search(
        original_route,
        n,
        arcs,
        relations,
    )

    print("\nFINAL RESULTS")
    print("Instance: grf13.txt")
    print("Previous cost:", round(original_cost, 4))
    print("ILS cost:", round(best_cost, 4))
    print("Improvement:", round(original_cost - best_cost, 4))
    print("Valid:", is_valid_route(best_route, n, arcs))


if __name__ == "__main__":
    run_pilot()

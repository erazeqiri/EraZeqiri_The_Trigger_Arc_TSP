
import ast
import csv
import random
from pathlib import Path

from parser import read_instance
from validator import is_valid_route
from cost_calculator import CostCalculator
from simulated_annealing import generate_neighbor


def trigger_aware_search(
    initial_route,
    n,
    arcs,
    relations,
    rounds=20,
    candidates_per_round=300,
    seed=42,
):
    random.seed(seed)
    calculator = CostCalculator(arcs, relations)

    best_route = initial_route.copy()

    if not is_valid_route(best_route, n, arcs):
        raise ValueError("Initial route is invalid")

    best_cost = calculator.calculate(best_route)

    if best_cost is None:
        raise ValueError("Cannot calculate initial cost")

    print("Starting cost:", round(best_cost, 4))

    for round_number in range(1, rounds + 1):
        round_best_route = best_route
        round_best_cost = best_cost

        for _ in range(candidates_per_round):
            candidate = generate_neighbor(best_route, arcs)

            if candidate == best_route:
                continue

            candidate_cost = calculator.calculate(candidate)

            if candidate_cost is None:
                continue

            if candidate_cost < round_best_cost - 1e-9:
                round_best_route = candidate
                round_best_cost = candidate_cost

        if round_best_cost < best_cost - 1e-9:
            best_route = round_best_route.copy()
            best_cost = round_best_cost

            print(
                f"Round {round_number}: "
                f"IMPROVED -> {best_cost:.4f}"
            )
        else:
            print(
                f"Round {round_number}: "
                f"No improvement"
            )
            break

    if not is_valid_route(best_route, n, arcs):
        raise RuntimeError("Search produced an invalid route")

    return best_route, best_cost


def save_improvement(
    output_path,
    instance_name,
    previous_cost,
    best_route,
    best_cost,
):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Instance",
        "PreviousCost",
        "NewCost",
        "Improvement",
        "Route",
    ]

    saved_rows = {}

    if output_path.exists():
        with open(
            output_path,
            newline="",
            encoding="utf-8-sig",
        ) as file:
            for row in csv.DictReader(file):
                saved_rows[row["Instance"]] = row

    existing = saved_rows.get(instance_name)

    if existing is not None:
        existing_cost = float(existing["NewCost"])

        if best_cost >= existing_cost - 1e-9:
            print("A better or equal result is already saved.")
            return

    saved_rows[instance_name] = {
        "Instance": instance_name,
        "PreviousCost": f"{previous_cost:.10f}",
        "NewCost": f"{best_cost:.10f}",
        "Improvement": f"{previous_cost - best_cost:.10f}",
        "Route": str(best_route),
    }

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(saved_rows.values())

    print("Improvement saved:", output_path)


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
        / "grf17.txt"
    )

    output_path = (
        project_root
        / "results"
        / "trigger_aware_improvements.csv"
    )

    with open(
        csv_path,
        newline="",
        encoding="utf-8-sig",
    ) as file:
        rows = list(csv.DictReader(file))

    matches = [
        row for row in rows
        if row["Instance"] == "grf17.txt"
    ]

    if len(matches) != 1:
        raise ValueError("Expected one row for grf17.txt")

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

    best_route, best_cost = trigger_aware_search(
        original_route,
        n,
        arcs,
        relations,
    )

    valid = is_valid_route(best_route, n, arcs)
    verified_cost = calculator.calculate(best_route)

    if (
        not valid
        or verified_cost is None
        or abs(verified_cost - best_cost) > 1e-8
    ):
        raise RuntimeError("Result verification failed")

    print("\nFINAL RESULTS")
    print("Instance: grf17.txt")
    print("Previous cost:", round(original_cost, 4))
    print("New cost:", round(best_cost, 4))
    print("Improvement:", round(original_cost - best_cost, 4))
    print("Valid:", valid)

    if best_cost < original_cost - 1e-9:
        save_improvement(
            output_path,
            "grf17.txt",
            original_cost,
            best_route,
            best_cost,
        )
    else:
        print("No improvement to save.")


if __name__ == "__main__":
    run_pilot()


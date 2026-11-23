
import ast
import csv
import random
from pathlib import Path

from parser import read_instance
from validator import is_valid_route
from cost_calculator import CostCalculator
from simulated_annealing import generate_neighbor


def build_trigger_guided_candidates(route, arcs, relations):
    """
    Identify beneficial trigger relations and propose moving
    a target arc after its trigger arc.

    The original trigger and target arcs are kept intact.
    """
    arc_by_id = {arc["id"]: arc for arc in arcs}

    positions = {
        vertex: index
        for index, vertex in enumerate(route[:-1])
    }

    route_edges = {}

    for index in range(len(route) - 1):
        route_edges[(route[index], route[index + 1])] = index

    proposals = []

    for relation in relations:
        trigger = arc_by_id.get(relation["trigger_id"])
        target = arc_by_id.get(relation["target_id"])

        if trigger is None or target is None:
            continue

        saving = target["cost"] - relation["new_cost"]

        if saving <= 1e-9:
            continue

        trigger_index = route_edges.get(
            (trigger["from"], trigger["to"])
        )

        target_index = route_edges.get(
            (target["from"], target["to"])
        )

        if trigger_index is None or target_index is None:
            continue

        # Only consider targets currently before the trigger.
        if target_index >= trigger_index:
            continue

        # Do not relocate the starting vertex or closing edge.
        if target_index == 0:
            continue

        if target_index + 1 >= len(route) - 1:
            continue

        proposals.append(
            (
                saving,
                target["from"],
                target["to"],
                trigger["to"],
            )
        )

    proposals.sort(reverse=True)

    candidates = []
    seen = set()

    for saving, target_from, target_to, trigger_to in proposals:
        if (
            target_from not in positions
            or target_to not in positions
            or trigger_to not in positions
        ):
            continue

        # Preserve the target arc as a two-vertex segment.
        start = positions[target_from]

        if route[start + 1] != target_to:
            continue

        interior = route[1:-1]
        segment = [target_from, target_to]

        remaining = [
            vertex
            for vertex in interior
            if vertex not in segment
        ]

        if trigger_to == route[0]:
            continue

        if trigger_to not in remaining:
            continue

        insert_at = remaining.index(trigger_to) + 1

        new_interior = (
            remaining[:insert_at]
            + segment
            + remaining[insert_at:]
        )

        candidate = [
            route[0],
            *new_interior,
            route[0],
        ]

        key = tuple(candidate)

        if key != tuple(route) and key not in seen:
            seen.add(key)
            candidates.append((saving, candidate))

    return candidates


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

    stagnant_rounds = 0

    for round_number in range(1, rounds + 1):
        round_best_route = best_route
        round_best_cost = best_cost

        guided_candidates = build_trigger_guided_candidates(
            best_route,
            arcs,
            relations,
        )

        guided_limit = candidates_per_round // 2
        guided_tested = 0

        for saving, candidate in guided_candidates:
            if guided_tested >= guided_limit:
                break

            if not is_valid_route(candidate, n, arcs):
                continue

            guided_tested += 1
            candidate_cost = calculator.calculate(candidate)

            if candidate_cost is None:
                continue

            if candidate_cost < round_best_cost - 1e-9:
                round_best_route = candidate
                round_best_cost = candidate_cost

        random_attempts = candidates_per_round - guided_tested

        for _ in range(random_attempts):
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
            stagnant_rounds = 0

            print(
                f"Round {round_number}: "
                f"IMPROVED -> {best_cost:.4f}"
            )
        else:
            stagnant_rounds += 1

            print(
                f"Round {round_number}: "
                f"No improvement"
            )

            if stagnant_rounds >= 3:
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
        with output_path.open(
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

    with output_path.open(
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
        / "best_55_updated.csv"
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
        / "trigger_guided_improvements.csv"
    )

    with csv_path.open(
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

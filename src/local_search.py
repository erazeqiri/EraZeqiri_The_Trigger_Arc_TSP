
import ast
import csv
import random
from pathlib import Path

from parser import read_instance
from validator import is_valid_route
from cost_calculator import CostCalculator


def local_search(
    route,
    n,
    arcs,
    relations,
    max_passes=5,
    attempts_per_pass=1000,
    seed=42,
):
    rng = random.Random(seed)
    calculator = CostCalculator(arcs, relations)

    best_route = list(route)

    if not is_valid_route(best_route, n, arcs):
        raise ValueError("Invalid starting route")

    best_cost = calculator.calculate(best_route)

    if best_cost is None:
        raise ValueError("Cannot calculate starting cost")

    existing_arcs = {
        (arc["from"], arc["to"])
        for arc in arcs
    }

    for _ in range(max_passes):
        improved = False
        size = len(best_route) - 2

        if size < 2:
            break

        for _ in range(attempts_per_pass):
            internal = best_route[1:-1]
            operation = rng.choice(
                ["swap", "relocate", "segment"]
            )

            if operation == "swap":
                i, j = rng.sample(range(size), 2)
                internal[i], internal[j] = (
                    internal[j], internal[i]
                )

            elif operation == "relocate":
                i, j = rng.sample(range(size), 2)
                node = internal.pop(i)
                internal.insert(j, node)

            else:
                if size < 3:
                    continue

                start = rng.randrange(size - 1)
                end = rng.randrange(start + 2, size + 1)

                segment = internal[start:end]
                remaining = internal[:start] + internal[end:]

                position = rng.randrange(
                    len(remaining) + 1
                )

                internal = (
                    remaining[:position]
                    + segment
                    + remaining[position:]
                )

            candidate = [0] + internal + [0]

            if candidate == best_route:
                continue

            if not all(
                (candidate[k], candidate[k + 1])
                in existing_arcs
                for k in range(len(candidate) - 1)
            ):
                continue

            candidate_cost = calculator.calculate(candidate)

            if (
                candidate_cost is not None
                and candidate_cost < best_cost - 1e-9
            ):
                best_route = candidate
                best_cost = candidate_cost
                improved = True

        if not improved:
            break

    if not is_valid_route(best_route, n, arcs):
        raise RuntimeError("Invalid result")

    return best_route, best_cost


def find_instance(instance_name, root):
    matches = list(root.rglob(instance_name))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"{instance_name}: found {len(matches)} files; "
            "expected exactly one"
        )

    return matches[0]


def run_pilot():
    project_root = Path(__file__).resolve().parent.parent

    csv_path = (
        project_root / "results"
        / "best_55_with_segment.csv"
    )

    instances_root = (
        project_root / "data" / "instances"
    )

    instance_name = "grf1.txt"

    with open(
        csv_path, newline="", encoding="utf-8-sig"
    ) as file:
        rows = list(csv.DictReader(file))

    matching_rows = [
        row for row in rows
        if row["Instance"] == instance_name
    ]

    if len(matching_rows) != 1:
        raise ValueError(
            "Expected exactly one CSV row for grf1.txt"
        )

    row = matching_rows[0]

    instance_path = find_instance(
        instance_name, instances_root
    )

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
        raise ValueError("Saved cost does not match")

    new_route, new_cost = local_search(
        original_route,
        n,
        arcs,
        relations,
    )

    print("Instance:", instance_name)
    print("Previous cost:", round(original_cost, 4))
    print("Local Search cost:", round(new_cost, 4))
    print("Improvement:", round(original_cost - new_cost, 4))
    print(
        "Valid:",
        is_valid_route(new_route, n, arcs)
    )


if __name__ == "__main__":
    run_pilot()


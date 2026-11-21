import random
import math
from pathlib import Path

from parser import read_instance
from validator import is_valid_route
from cost_calculator import CostCalculator


# Gjenerimi i rruges fillestare me heuristike
def generate_initial_route(
    n, arcs, max_steps=100000, max_restarts=10
):
    adjacency = {node: set() for node in range(n)}

    for arc in arcs:
        adjacency[arc["from"]].add(arc["to"])

    for attempt in range(max_restarts):

        route = [0]
        visited = {0}
        steps = 0

        def backtrack():
            nonlocal steps

            if steps >= max_steps:
                return False

            steps += 1

            if len(route) == n:
                return 0 in adjacency[route[-1]]

            current = route[-1]

            neighbors = [
                node for node in adjacency[current]
                if node not in visited
            ]

            random.shuffle(neighbors)

            # Perparesi nyjeve me me pak fqinje te pavizituar
            neighbors.sort(
                key=lambda node: len(
                    adjacency[node] - visited - {node}
                )
            )

            for node in neighbors:

                route.append(node)
                visited.add(node)

                if backtrack():
                    return True

                route.pop()
                visited.remove(node)

                if steps >= max_steps:
                    break

            return False

        if backtrack():
            return route + [0]

    return None


# Gjenerimi i nje zgjidhjeje fqinje te vlefshme
def generate_neighbor(route, arcs=None, max_attempts=100):
    if len(route) < 4:
        return route.copy()

    existing_arcs = None

    if arcs is not None:
        existing_arcs = {
            (arc["from"], arc["to"])
            for arc in arcs
        }

    for _ in range(max_attempts):
        neighbor = route.copy()

        i, j = random.sample(
            range(1, len(neighbor) - 1), 2
        )

        if random.random() < 0.5:
            # Swap
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        else:
            # Relocate
            node = neighbor.pop(i)
            neighbor.insert(j, node)

        if existing_arcs is None:
            return neighbor

        # Kontrollo nese te gjitha harqet ekzistojne
        if all(
            (neighbor[k], neighbor[k + 1]) in existing_arcs
            for k in range(len(neighbor) - 1)
        ):
            return neighbor

    # Nese nuk gjendet fqinj i vlefshem
    return route.copy()


# Algoritmi Simulated Annealing
def simulated_annealing(
    n,
    arcs,
    relations,
    initial_temperature=100.0,
    cooling_rate=0.995,
    max_iterations=5000
):
    current_route = generate_initial_route(n, arcs)

    if current_route is None:
        return None, float("inf")

    # Krijimi i CostCalculator vetem nje here
    calculator = CostCalculator(arcs, relations)

    current_cost = calculator.calculate(current_route)

    best_route = current_route.copy()
    best_cost = current_cost

    temperature = initial_temperature

    for iteration in range(max_iterations):

        # Gjenerimi i nje fqinji te vlefshem
        neighbor = generate_neighbor(current_route, arcs)

        # Mos e llogarit perseri koston nese rruga nuk ndryshon
        if neighbor == current_route:
            temperature *= cooling_rate

            if temperature < 0.001:
                break

            continue

        if is_valid_route(neighbor, n, arcs):

            neighbor_cost = calculator.calculate(neighbor)

            delta = neighbor_cost - current_cost

            if delta <= 0 or random.random() < math.exp(
                -delta / temperature
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


# Ekzekutimi i algoritmit
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "example.txt"

    n, m, r, arcs, relations = read_instance(file_path)

    best_route, best_cost = simulated_annealing(
        n, arcs, relations
    )

    print("Rruga me e mire:", best_route)
    print("Kostoja me e mire:", best_cost)

    if best_route is not None:
        print(
            "E vlefshme:",
            is_valid_route(best_route, n, arcs)
        )
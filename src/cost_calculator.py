from pathlib import Path
from parser import read_instance


def get_arc_cost(arcs, from_node, to_node):
    for arc in arcs:
        if arc["from"] == from_node and arc["to"] == to_node:
            return arc["cost"]

    return None


class CostCalculator:

    def __init__(self, arcs, relations):
        self.arc_lookup = {}
        self.trigger_lookup = {}

        for arc in arcs:
            key = (arc["from"], arc["to"])
            self.arc_lookup.setdefault(key, arc)

        for relation in relations:
            trigger_id = relation["trigger_id"]

            if trigger_id not in self.trigger_lookup:
                self.trigger_lookup[trigger_id] = []

            self.trigger_lookup[trigger_id].append(
                (relation["target_id"], relation["new_cost"])
            )

    def calculate(self, route):
        total_cost = 0
        active_costs = {}

        for i in range(len(route) - 1):
            from_node = route[i]
            to_node = route[i + 1]

            current_arc = self.arc_lookup.get(
                (from_node, to_node)
            )

            if current_arc is None:
                return None

            arc_id = current_arc["id"]

            cost = active_costs.get(
                arc_id, current_arc["cost"]
            )

            total_cost += cost

            for target_id, new_cost in self.trigger_lookup.get(
                arc_id, []
            ):
                active_costs[target_id] = new_cost

        return total_cost


def calculate_route_cost(route, arcs, relations):
    calculator = CostCalculator(arcs, relations)
    return calculator.calculate(route)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "example.txt"

    n, m, r, arcs, relations = read_instance(file_path)

    cost = get_arc_cost(arcs, 0, 2)
    print("Kostoja e harkut 0 -> 2:", cost)

    route = [0, 3, 2, 1, 4, 0]

    total = calculate_route_cost(route, arcs, relations)

    print("Rruga:", route)
    print("Kostoja totale:", total)

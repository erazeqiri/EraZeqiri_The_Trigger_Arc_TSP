
from pathlib import Path


def read_instance(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        first_line = file.readline()
        n, m, r = map(int, first_line.split())

        arcs = []

        for i in range(m):
            line = file.readline()
            arc_id, from_node, to_node, cost = line.split()


            arc = {
                "id": int(arc_id),
                "from": int(from_node),
                "to": int(to_node),
                "cost": float(cost)
            }

            arcs.append(arc)


        relations = []

        for i in range(r):
            line = file.readline()
            values = line.split()

            relation = {
                "id": int(values[0]),
                "trigger_id": int(values[1]),
                "trigger_from": int(values[2]),
                "trigger_to": int(values[3]),
                "target_id": int(values[4]),
                "target_from": int(values[5]),
                "target_to": int(values[6]),
                "new_cost": float(values[7])
            }

            relations.append(relation)


    return n, m, r, arcs, relations





if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "example.txt"

    n, m, r, arcs, relations = read_instance(file_path)

    print("Numri i nyjeve:", n)
    print("Numri i harqeve:", m)
    print("Numri i relacioneve:", r)

    print("\nHarqet:")
    for arc in arcs:
        print(arc)

    print("\nRelacionet trigger:")
    for relation in relations:
        print(relation)

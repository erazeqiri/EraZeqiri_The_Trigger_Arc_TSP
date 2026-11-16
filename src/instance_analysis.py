from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
instances_path = project_root / "data" / "instances"

for folder in ["first_set", "second_set"]:

    print(f"\n--- {folder} ---")

    files = sorted(
        (instances_path / folder).glob("grf*.txt")
    )

    for file_path in files:

        with open(file_path, "r", encoding="utf-8") as file:
            n, m, r = map(int, file.readline().split())

        print(
            f"{file_path.name}: "
            f"Nyjet={n}, Harqet={m}, Relacionet={r}"
        )

    print("Numri i instancave:", len(files))

from pathlib import Path

def read_instance(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        first_line = file.readline()
        n, m, r = map(int, first_line.split())

    return n, m, r


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "example.txt"

    n, m, r = read_instance(file_path)

    print("Numri i nyjeve:", n)
    print("Numri i harqeve:", m)
    print("Numri i relacioneve:", r)

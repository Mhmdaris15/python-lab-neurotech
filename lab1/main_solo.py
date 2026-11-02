import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent

x: str = input("search> ")

# search> load

command: str = x.split()[0]

if command == "help":
    # loading file
    print("Commands: help, load <file>, show, fields, filter add <field> <op> <value>,\n filter list|remove <n>|clear, search \"<query>\", save <file>,\n rate <id> <1..5>, ratings, exit")
elif command == "load":
    # loading file
    print("Loading file...")
    filename = x.split()[1]
    path = ROOT / "lab1/data" / filename
    with path.open(encoding="utf-8-sig", newline="") as file:
        #  list(csv.DictReader(file))
        print(list(csv.DictReader(file)))
    # print(path)
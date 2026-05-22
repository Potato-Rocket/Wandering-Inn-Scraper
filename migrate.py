from pathlib import Path
import pandas as pd
import json


def fix_path(p, sub):
    return str(Path.cwd() / sub / Path(p).name)


table_path = Path.cwd() / "table.csv"
table = pd.read_csv(table_path).dropna()

table["raw"] = table["raw"].apply(fix_path, args=("raw",))
table["out"] = table["out"].apply(fix_path, args=("out",))

table.to_csv(table_path)

index_path = Path.cwd() / "index.json"
with open(index_path) as f:
    index = json.load(f)

for entry in index:
    entry["raw"] = fix_path(entry["raw"], "raw")

with open(index_path, "w") as f:
    json.dump(index, f, indent=2)

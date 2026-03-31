"""
combine_cities.py

Reads cities.json and merges all entries with the same name.
The resulting entries have "books" and "chapters" as sorted lists.
Overwrites cities.json in place.
"""

import json

INPUT_FILE = "cities.json"

with open(INPUT_FILE, encoding="utf-8") as f:
    entries = json.load(f)

combined = {}
for entry in entries:
    name = entry["name"]
    if name not in combined:
        combined[name] = {"name": name, "books": set(), "chapters": set()}
    combined[name]["books"].add(entry["book"])
    combined[name]["chapters"].add(entry["chapter"])

result = [
    {
        "name": city["name"],
        "books": sorted(city["books"]),
        "chapters": sorted(city["chapters"]),
    }
    for city in sorted(combined.values(), key=lambda c: c["name"])
]

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Done. {len(entries)} mentions → {len(result)} unique cities written to {INPUT_FILE}.")

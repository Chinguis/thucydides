#!/usr/bin/env python3
"""
search_pleiades.py  —  Search the Pleiades dataset from the command line.

Usage:
    python search_pleiades.py <place name>

Examples:
    python search_pleiades.py Potidaea
    python search_pleiades.py "Epidaurus Limera"

Exact match: prints the full Pleiades entry.
No exact match: prints the closest matches ranked by similarity.
"""

import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher

PLEIADES_FILE = "pleiades-places-latest.json"
TOP_N = 10  # number of fuzzy matches to show


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

LIGATURES = str.maketrans({"æ": "ae", "œ": "oe", "Æ": "Ae", "Œ": "Oe"})

def normalize(text: str) -> str:
    """Lowercase, expand ligatures, strip diacritics, collapse whitespace."""
    text = text.translate(LIGATURES)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " ".join(text.lower().split())

SUFFIXES = re.compile(r"(ae|os|us|on|um|a|e|i)$")

def stem(name: str) -> str:
    return SUFFIXES.sub("", name)

def name_variants(name: str) -> list[str]:
    n = normalize(name)
    s = stem(n)
    return list(dict.fromkeys([n, s]))


# ---------------------------------------------------------------------------
# Build index
# ---------------------------------------------------------------------------

def all_names(place: dict) -> list[str]:
    """All human-readable name strings for a place (title + romanized names)."""
    names = [place.get("title", "")]
    for entry in place.get("names", []):
        for part in entry.get("romanized", "").split(","):
            part = part.strip()
            if part:
                names.append(part)
    return [n for n in names if n]

def build_index(places: list) -> dict:
    """
    Returns a dict:  normalized_variant -> place_dict
    Only places with coordinates are indexed.
    """
    index = {}
    for place in places:
        if not place.get("reprPoint"):
            continue
        for raw_name in all_names(place):
            for v in name_variants(raw_name):
                index.setdefault(v, place)
    return index


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def fmt_place(place: dict, matched_name: str = None) -> str:
    title = place.get("title", "?")
    point = place.get("reprPoint")
    lng, lat = (round(point[0], 5), round(point[1], 5)) if point else (None, None)
    types = ", ".join(place.get("placeTypes", [])) or "—"
    uri   = place.get("uri", "")
    desc  = place.get("description", "").strip() or "—"
    names = ", ".join(all_names(place)[:8])

    lines = [
        f"  Title:       {title}",
        f"  Coordinates: {lat}, {lng}",
        f"  Types:       {types}",
        f"  Names:       {names}",
        f"  Description: {desc}",
        f"  URI:         {uri}",
    ]
    if matched_name and normalize(matched_name) != normalize(title):
        lines.insert(1, f"  Matched via: {matched_name}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_pleiades.py <place name>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    query_variants = name_variants(query)

    print(f"Loading Pleiades… ", end="", flush=True)
    with open(PLEIADES_FILE, encoding="utf-8") as f:
        data = json.load(f)
    places = data["@graph"]
    index  = build_index(places)
    print(f"{len(places)} places, {len(index)} name variants.\n")

    # Score every indexed variant against every query variant; keep best per place
    print(f"Closest matches for '{query}':\n")

    seen_ids  = {}   # place id -> best score
    seen_name = {}   # place id -> best matching name

    # Boost exact matches to the top by giving them a score of 1.0
    for v in query_variants:
        if v in index:
            place = index[v]
            pid = place.get("id") or place.get("uri")
            seen_ids[pid]  = 1.0
            seen_name[pid] = v

    q_variants_set = query_variants

    for indexed_name, place in index.items():
        pid = place.get("id") or place.get("uri")
        score = max(
            SequenceMatcher(None, qv, indexed_name).ratio()
            for qv in q_variants_set
        )
        if score > seen_ids.get(pid, 0):
            seen_ids[pid]  = score
            seen_name[pid] = indexed_name

    # Resolve pid -> place (index values are place dicts; we just need one per pid)
    pid_to_place = {}
    for indexed_name, place in index.items():
        pid = place.get("id") or place.get("uri")
        if pid not in pid_to_place:
            pid_to_place[pid] = place

    top = sorted(seen_ids.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

    for rank, (pid, score) in enumerate(top, 1):
        place = pid_to_place[pid]
        print(f"  #{rank}  score={score:.2f}  (matched via '{seen_name[pid]}')")
        print(fmt_place(place))
        print()


if __name__ == "__main__":
    main()

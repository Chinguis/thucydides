#!/usr/bin/env python3
"""
geocode_claude_fallback.py

For every city in cities.json that has no coordinates, runs a Pleiades fuzzy
search and asks Claude to pick the best match. Updates cities.json in place.

Claude is given the city name, the context (Thucydides, 5th-century BCE Greek
world), and the top Pleiades candidates. It returns either the index of the
best match or null if none are plausible.
"""

import json
import os
from dotenv import load_dotenv
import anthropic

# Import search helpers from search_pleiades.py
from search_pleiades import (
    build_index,
    all_names,
    name_variants,
    normalize,
    PLEIADES_FILE,
)
from difflib import SequenceMatcher

load_dotenv()

CITIES_FILE = "cities.json"
TOP_N = 10

client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

SYSTEM_PROMPT = """\
You are an expert in ancient Greek geography and Thucydides' History of the \
Peloponnesian War (5th century BCE). You will be given a place name from \
Thucydides and a list of candidate matches from the Pleiades ancient world \
gazetteer. Your job is to identify which candidate, if any, is the correct match.

Respond with a JSON object only — no explanation, no markdown. Use this schema:
{
  "match": <integer 1–10, or null if no candidate is a plausible match>,
  "reason": "<one short sentence>"
}"""

USER_PROMPT_TEMPLATE = """\
Place name from Thucydides: {name}

Pleiades candidates:
{candidates}

Which candidate is the correct match for "{name}" as mentioned by Thucydides? \
Prefer candidates in or near Greece, the Aegean, Asia Minor, Sicily, or Italy. \
Return null if none are plausible."""


def fuzzy_search(query: str, index: dict) -> list[tuple[float, str, dict]]:
    """Return top-N (score, matched_variant, place) tuples."""
    q_variants = name_variants(query)
    seen_ids = {}
    seen_name = {}

    for indexed_name, place in index.items():
        pid = place.get("id") or place.get("uri")
        score = max(
            SequenceMatcher(None, qv, indexed_name).ratio()
            for qv in q_variants
        )
        if score > seen_ids.get(pid, 0):
            seen_ids[pid] = score
            seen_name[pid] = indexed_name

    pid_to_place = {}
    for indexed_name, place in index.items():
        pid = place.get("id") or place.get("uri")
        if pid not in pid_to_place:
            pid_to_place[pid] = place

    top = sorted(seen_ids.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
    return [(score, seen_name[pid], pid_to_place[pid]) for pid, score in top]


def format_candidates(results: list) -> str:
    lines = []
    for i, (score, matched_via, place) in enumerate(results, 1):
        title = place.get("title", "?")
        point = place.get("reprPoint")
        lat, lng = (round(point[1], 4), round(point[0], 4)) if point else (None, None)
        types = ", ".join(place.get("placeTypes", [])) or "—"
        desc = place.get("description", "").strip() or "—"
        names = ", ".join(all_names(place)[:6])
        lines.append(
            f"{i}. {title} (score={score:.2f})\n"
            f"   Matched via: '{matched_via}'\n"
            f"   Coordinates: {lat}, {lng}\n"
            f"   Types: {types}\n"
            f"   Names: {names}\n"
            f"   Description: {desc}"
        )
    return "\n\n".join(lines)


def ask_claude(city_name: str, candidates: list) -> tuple[dict | None, str]:
    """Returns (chosen_place, reason) or (None, reason)."""
    candidates_text = format_candidates(candidates)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                name=city_name,
                candidates=candidates_text,
            )
        }]
    )
    raw = response.content[0].text.strip()

    import re
    m = re.search(r"\{.*?\}", raw, re.DOTALL)
    if not m:
        return None, "Claude returned unparseable response"

    data = json.loads(m.group())
    idx = data.get("match")
    reason = data.get("reason", "")

    if idx is None:
        return None, reason

    chosen = candidates[int(idx) - 1][2]  # place dict
    return chosen, reason


def main():
    print("Loading Pleiades… ", end="", flush=True)
    with open(PLEIADES_FILE, encoding="utf-8") as f:
        pleiades_data = json.load(f)
    places = pleiades_data["@graph"]
    index = build_index(places)
    print(f"{len(places)} places, {len(index)} name variants.")

    with open(CITIES_FILE, encoding="utf-8") as f:
        cities = json.load(f)

    # Clear existing geocoding so everything is re-evaluated
    for city in cities:
        city["lat"] = None
        city["lng"] = None
        city["pleiades_match"] = None

    print(f"\n{len(cities)} cities to resolve.\n")

    resolved = 0
    failed = 0

    for city in cities:
        name = city["name"]
        print(f"  {name} … ", end="", flush=True)

        candidates = fuzzy_search(name, index)
        if not candidates:
            print("no candidates")
            failed += 1
            continue

        place, reason = ask_claude(name, candidates)

        if place:
            point = place.get("reprPoint")
            city["lat"] = round(point[1], 6)
            city["lng"] = round(point[0], 6)
            city["pleiades_match"] = place.get("title")
            print(f"→ {place.get('title')}  ({reason})")
            resolved += 1
        else:
            print(f"→ no match  ({reason})")
            failed += 1

        # Save after every city
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cities, f, indent=2, ensure_ascii=False)

    total_matched = sum(1 for c in cities if c.get("lat") is not None)
    print(f"\nResolved {resolved} new, {failed} still unmatched.")
    print(f"Total with coordinates: {total_matched}/{len(cities)}")


if __name__ == "__main__":
    main()

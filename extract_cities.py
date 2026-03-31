#!/usr/bin/env python3
"""
extract_cities.py

Goes through each chapter txt file in book1/–book8/, asks Claude to extract
all city names mentioned, and writes the results to cities.json.

Each entry in cities.json:
  {
    "name": "Athens",
    "book": 1,
    "chapter": 3
  }

Cities that appear in multiple chapters will have one entry per chapter.
"""

import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

BOOK_DIRS = [f"book{i}" for i in range(1, 9)]
OUTPUT_FILE = "cities.json"

client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

SYSTEM_PROMPT = """\
You are a careful scholar of ancient Greek history. Your task is to extract \
city names from a passage of Thucydides' History of the Peloponnesian War.

Return ONLY a JSON array of city name strings — no explanation, no markdown, \
no code fences. If no cities are mentioned, return an empty array [].

Include only settlements that were or could have been cities or towns \
(poleis, settlements, colonies). Do not include regions, peoples, mountains, \
rivers, seas, or personal names.\
"""

USER_PROMPT_TEMPLATE = """\
Extract all city names mentioned in the following chapter of Thucydides.

{chapter_text}
"""


def extract_cities_from_chapter(chapter_text: str) -> list[str]:
    """Call Claude and return a list of city names found in the chapter."""
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(chapter_text=chapter_text)}
        ],
    )
    raw = message.content[0].text
    # Find the first JSON array in the response
    m = re.search(r"\[.*?\]", raw, re.DOTALL)
    if not m:
        return []
    return json.loads(m.group())


def parse_book_and_chapter(filename: str, book_num: int) -> int:
    """Extract the chapter number from a filename like '002_chapter_i.txt'."""
    # The chapter txt files start with the heading "Chapter N"
    # We'll read it from the file rather than parsing the filename
    return None  # resolved by reading the file heading


def get_chapter_number(chapter_text: str) -> int | None:
    """Read the chapter number from the first line of the txt file."""
    first_line = chapter_text.splitlines()[0].strip()
    m = re.match(r"Chapter\s+(\d+)", first_line, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def main():
    # Resume from existing output if present
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            all_entries = json.load(f)
        done = {(e["book"], e["chapter"]) for e in all_entries}
        print(f"Resuming — {len(done)} chapters already done.")
    else:
        all_entries = []
        done = set()

    for book_num, book_dir in enumerate(BOOK_DIRS, start=1):
        if not os.path.isdir(book_dir):
            print(f"Skipping {book_dir}/ (not found)")
            continue

        txt_files = sorted(f for f in os.listdir(book_dir) if f.endswith(".txt"))
        print(f"\nBook {book_num} ({len(txt_files)} chapters)")

        for filename in txt_files:
            path = os.path.join(book_dir, filename)
            with open(path, encoding="utf-8") as f:
                chapter_text = f.read()

            chapter_num = get_chapter_number(chapter_text)

            if (book_num, chapter_num) in done:
                print(f"  Chapter {chapter_num} — already done, skipping.")
                continue

            print(f"  Chapter {chapter_num} ({filename}) … ", end="", flush=True)
            cities = extract_cities_from_chapter(chapter_text)
            print(f"{len(cities)} cities")

            for city in cities:
                all_entries.append({
                    "name": city,
                    "book": book_num,
                    "chapter": chapter_num,
                })

            # Save after each chapter so progress isn't lost on failure
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_entries, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=2, ensure_ascii=False)

    total_cities = len(all_entries)
    unique_cities = len({e["name"] for e in all_entries})
    print(f"\nDone. {total_cities} city mentions ({unique_cities} unique) written to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()

"""
split_chapters.py

Splits thucydides.htm into individual chapter files.
Each <div class="chapter"> becomes its own HTML file in the chapters/ folder.
Files are named by index and heading text, e.g. 001_book_i.html.
"""

import os
import re
from bs4 import BeautifulSoup


INPUT_FILE = "thucydides.htm"
OUTPUT_DIR = "chapters"


def slugify(text):
    """Convert heading text to a safe filename segment."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    chapters = soup.find_all("div", class_="chapter")
    print(f"Found {len(chapters)} chapters.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, chapter in enumerate(chapters, start=1):
        heading = chapter.find(["h1", "h2", "h3"])
        heading_text = heading.get_text(" ", strip=True) if heading else "untitled"
        slug = slugify(heading_text)
        filename = f"{i:03d}_{slug}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(chapter.prettify())

        print(f"  {filename}")

    print(f"\nDone. {len(chapters)} files written to '{OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()

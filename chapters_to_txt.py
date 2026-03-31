"""
chapters_to_txt.py

Converts chapter HTML files in book1/–book8/ to plain text.
Each .html file is replaced with a .txt file containing:
  - The chapter heading (h2 text, formatted as "Book I" / "Chapter 1")
  - All paragraph texts, separated by a single blank line
"""

import os
import re
from bs4 import BeautifulSoup


BOOK_DIRS = [f"book{i}" for i in range(1, 9)]


ROMAN = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100,  "C"), (90,  "XC"), (50,  "L"), (40,  "XL"),
    (10,   "X"), (9,   "IX"), (5,   "V"), (4,   "IV"),
    (1,    "I"),
]

def roman_to_int(s):
    s = s.upper().strip()
    result = 0
    i = 0
    for value, numeral in ROMAN:
        while s[i:i+len(numeral)] == numeral:
            result += value
            i += len(numeral)
    return result


def format_heading(raw):
    """
    Convert h2 text like 'CHAPTER I' or 'BOOK III' to 'Chapter 1' / 'Book III'.
    Chapter numbers are converted to arabic; Book numbers are kept as roman numerals.
    """
    raw = " ".join(raw.split())  # collapse whitespace
    m = re.match(r"^(CHAPTER|BOOK)\s+([IVXLCDM]+)$", raw, re.IGNORECASE)
    if m:
        kind = m.group(1).capitalize()
        numeral = m.group(2).upper()
        if kind == "Chapter":
            return f"{kind} {roman_to_int(numeral)}"
        else:
            return f"{kind} {numeral}"
    # Fallback: title-case as-is
    return raw.title()


def extract_paragraph_text(p):
    """Return clean single-line text from a <p> element."""
    text = p.get_text(" ", strip=True)
    # Collapse internal whitespace
    return re.sub(r"\s+", " ", text)


def convert_file(html_path):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    chapter = soup.find("div", class_="chapter")
    if not chapter:
        print(f"  WARNING: no <div class='chapter'> found in {html_path}, skipping.")
        return

    # Heading
    h = chapter.find(["h1", "h2", "h3"])
    heading = format_heading(h.get_text(" ", strip=True)) if h else "Untitled"

    # Paragraphs (in document order)
    paragraphs = [extract_paragraph_text(p) for p in chapter.find_all("p")]
    paragraphs = [p for p in paragraphs if p]  # drop empties

    txt_path = os.path.splitext(html_path)[0] + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(heading + "\n")
        for para in paragraphs:
            f.write("\n" + para + "\n")

    os.remove(html_path)


def main():
    for book_dir in BOOK_DIRS:
        if not os.path.isdir(book_dir):
            print(f"Skipping {book_dir}/ (not found)")
            continue
        html_files = sorted(
            p for p in os.listdir(book_dir) if p.endswith(".html")
        )
        print(f"{book_dir}/  ({len(html_files)} files)")
        for filename in html_files:
            path = os.path.join(book_dir, filename)
            convert_file(path)
            print(f"  {os.path.splitext(filename)[0]}.txt")

    print("\nDone.")


if __name__ == "__main__":
    main()

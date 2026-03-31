# How cities.js was generated

This document describes the pipeline used to produce `cities.js` — the geocoded city dataset powering the map — starting from the raw Project Gutenberg HTML of Thucydides' *History of the Peloponnesian War*.

---

## 1. Split the source text into chapters (`split_chapters.py`)

**Input:** `thucydides.htm` (Project Gutenberg HTML)

The source file contains the full text of Thucydides, with each chapter wrapped in a `<div class="chapter">` element. `split_chapters.py` uses BeautifulSoup to find all such divs and writes each one to its own `.html` file, named by index and heading (e.g. `002_chapter_i.html`).

The resulting files were then manually organised into eight folders — `book1/` through `book8/` — one per book of the *History*.

---

## 2. Convert chapter files to plain text (`chapters_to_txt.py`)

**Input:** `book1/` – `book8/` (HTML chapter files)
**Output:** `.txt` files replacing the `.html` files in the same folders

`chapters_to_txt.py` parses each chapter HTML file, extracts the `<h2>` heading (converting Roman numerals to Arabic, e.g. "CHAPTER I" → "Chapter 1"), and outputs all `<p>` elements as clean plain-text paragraphs separated by blank lines.

---

## 3. Extract city names with Claude (`extract_cities.py`)

**Input:** Chapter `.txt` files
**Output:** `cities.json`

For each chapter, the full text is sent to Claude (`claude-opus-4-6`) with a prompt asking it to return a JSON array of city names. The script processes all 26 chapters across the 8 books and writes every result to `cities.json`, saving after each chapter so progress is not lost on failure.

Each entry at this stage looks like:
```json
{ "name": "Athens", "book": 1, "chapter": 1 }
```

---

## 4. Combine duplicate mentions (`combine_cities.py`)

**Input/Output:** `cities.json`

Multiple entries for the same city (one per chapter mention) are merged into a single entry. The `book` and `chapter` fields become sorted lists of all books and chapters in which the city appears.

```json
{ "name": "Athens", "books": [1, 2, 3, ...], "chapters": [1, 2, 3, ...] }
```

A `"type": "city"` field is also added to each entry at this stage.

---

## 5. Geocode with Claude using Pleiades as a search backend (`geocode_claude_fallback.py`)

**Input:** `cities.json`, `pleiades-places-latest.json`
**Output:** `cities.json` (updated with coordinates)
**Tool:** `search_pleiades.py`

[Pleiades](https://pleiades.stoa.org) is the standard scholarly gazetteer for ancient world places. The full dataset (~42,000 entries) is downloaded as a JSON file and indexed by all romanized name variants.

For each city, a fuzzy search against the Pleiades index is run using `SequenceMatcher` similarity scoring, with name normalisation (case, ligatures, diacritics, common Greek/Latin suffixes). Exact matches are scored 1.0 and appear first; all other candidates are ranked by similarity. The top 10 candidates are formatted with their title, coordinates, place types, name variants, and description, then sent to Claude (`claude-sonnet-4-6`) with the following context:

> *You are an expert in ancient Greek geography and Thucydides' History of the Peloponnesian War. Identify which candidate, if any, is the correct match.*

Claude returns a JSON object with the index of the best match (or `null`) and a one-sentence reason. Crucially, Claude evaluates all candidates even when an exact name match exists — this prevents false positives such as matching the Spanish Abdera instead of the Thracian one.

The final result was **334/371 cities geocoded (90%)**.

---

## 6. Manual deduplication

Two pairs of duplicate entries — introduced by Claude extracting the same city under variant spellings — were identified and merged by hand:

- `Potidæa` → merged into `Potidaea`
- `Leontines` → merged into `Leontini`

Books and chapters lists were unioned across the merged entries.

---

## 7. Generate cities.js

The final `cities.json` (371 entries, 332 with coordinates) is converted to a JavaScript file by wrapping the array in a `const cities = [...]` declaration, filtered to only include geocoded entries. This file is loaded directly by `index.html` as a `<script>` tag.

---

## Files

| File | Role |
|---|---|
| `thucydides.htm` | Source text (Project Gutenberg) |
| `split_chapters.py` | Step 1: split HTML into chapter files |
| `chapters_to_txt.py` | Step 2: convert chapter HTML to plain text |
| `extract_cities.py` | Step 3: extract city names via Claude |
| `combine_cities.py` | Step 4: merge per-chapter entries |
| `geocode_claude_fallback.py` | Step 5: Claude-assisted geocoding via Pleiades |
| `search_pleiades.py` | Utility: CLI search tool for Pleiades dataset |
| `cities.json` | Master data file (source of truth) |
| `cities.js` | Map-ready JS bundle generated from `cities.json` |

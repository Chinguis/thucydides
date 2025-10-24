#!/usr/bin/env python3
"""
Clean the settlements.js file to remove non-location entries using Claude API.
"""

import os
import re
import json
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def parse_settlements_js(filename):
    """Parse the settlements.js file and extract location entries."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    settlements = []

    # Parse line by line
    for line in lines:
        line = line.strip()
        if not line.startswith('{ name:'):
            continue

        # Extract fields using regex
        name_match = re.search(r"name: '((?:[^'\\]|\\.)*)'", line)
        modern_match = re.search(r"modern: '((?:[^'\\]|\\.)*)'", line)
        lat_match = re.search(r"lat: ([-\d.]+)", line)
        lng_match = re.search(r"lng: ([-\d.]+)", line)
        type_match = re.search(r"type: '((?:[^'\\]|\\.)*)'", line)

        if all([name_match, modern_match, lat_match, lng_match, type_match]):
            # Unescape apostrophes
            name = name_match.group(1).replace("\\'", "'")
            modern = modern_match.group(1).replace("\\'", "'")

            settlement = {
                'name': name,
                'modern': modern,
                'lat': float(lat_match.group(1)),
                'lng': float(lng_match.group(1)),
                'type': type_match.group(1).replace("\\'", "'")
            }
            settlements.append(settlement)

    return settlements

def clean_settlements_batch(settlements_batch, batch_num, total_batches):
    """Use Claude to identify which entries are actual geographic locations."""
    print(f"\nProcessing batch {batch_num}/{total_batches}...")

    # Format the settlements for review
    settlement_list = []
    for i, s in enumerate(settlements_batch):
        settlement_list.append(f"{i+1}. {s['name']} (modern: {s['modern']}, type: {s['type']})")

    settlements_text = "\n".join(settlement_list)

    prompt = f"""You are reviewing a list of entries extracted from Thucydides' "History of the Peloponnesian War" for use in a geographic map.

Some entries are NOT actual geographic locations and should be REMOVED. These include:
- People's names (Xerxes, Alcibiades, Pericles, etc.)
- Historical events (Trojan War, Battle of Marathon as an event vs. Marathon as a place)
- Ethnic/tribal group names that don't refer to a specific geographic area (e.g., "Athenians" vs "Athens")
- Abstract concepts
- Festivals or ceremonies
- Family names
- Military units or groups

KEEP entries that ARE actual geographic locations:
- Cities, towns, villages, settlements (Athens, Sparta, Syracuse)
- Islands, peninsulas (Sicily, Crete, Acte)
- Regions with defined geographic boundaries (Attica, Boeotia, Peloponnese, Acarnania)
- Mountains, rivers, seas, lakes, harbors (Olympus, Achelous, Aegean Sea)
- Forts, sanctuaries, temples with specific physical locations (Delphi, Olympia)
- Geographic features (passes, cliffs, gulfs)
- Even if the name is demonymic (like "Athenians" or "Spartans"), KEEP it IF the coordinates and modern location indicate it refers to the geographic place, not just the people

Be strict: when in doubt about whether something is a location vs. a person/event/concept, REMOVE it.

ENTRIES TO REVIEW:
{settlements_text}

Return ONLY a JSON array with the numbers of entries that should be KEPT (actual geographic locations).
For example: [1, 2, 5, 7, 9, 10, ...]

Return ONLY the JSON array of numbers, no other text or explanation."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.content[0].text.strip()

        # Parse the JSON array
        json_match = re.search(r'\[([\d,\s]+)\]', content)
        if json_match:
            keep_indices = json.loads('[' + json_match.group(1) + ']')
            # Convert to 0-based indices
            keep_indices = [i - 1 for i in keep_indices]

            kept_settlements = [settlements_batch[i] for i in keep_indices if i < len(settlements_batch)]
            removed_count = len(settlements_batch) - len(kept_settlements)

            # Show what was removed
            removed = [settlements_batch[i]['name'] for i in range(len(settlements_batch)) if i not in keep_indices]
            if removed:
                print(f"  Removed: {', '.join(removed[:10])}" + (" ..." if len(removed) > 10 else ""))

            print(f"  Kept {len(kept_settlements)}/{len(settlements_batch)} entries")
            return kept_settlements
        else:
            print(f"  Warning: Could not parse response, keeping all entries")
            return settlements_batch

    except Exception as e:
        print(f"  Error: {e}")
        return settlements_batch

def generate_settlements_js(locations, output_file):
    """Generate the cleaned settlements.js file."""
    print(f"\nGenerating {output_file}...")

    # Sort locations by name
    locations.sort(key=lambda x: x['name'])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// Ancient Greek settlements and locations mentioned in Thucydides'\n")
        f.write("// History of the Peloponnesian War\n")
        f.write("// Automatically extracted and geocoded using Claude AI\n")
        f.write("// Cleaned to remove non-geographic entries\n\n")
        f.write("const settlements = [\n")

        for i, loc in enumerate(locations):
            name = loc['name'].replace("'", "\\'")
            modern = loc['modern'].replace("'", "\\'")
            lat = loc.get('lat', 0.0)
            lng = loc.get('lng', 0.0)
            type_str = loc['type'].replace("'", "\\'")

            comma = "," if i < len(locations) - 1 else ""
            f.write(f"    {{ name: '{name}', modern: '{modern}', lat: {lat}, lng: {lng}, type: '{type_str}' }}{comma}\n")

        f.write("];\n")

    print(f"  Successfully generated {output_file} with {len(locations)} locations")

def main():
    input_file = "settlements.js"
    output_file = "settlements_cleaned.js"

    print("=" * 70)
    print("Cleaning Settlements File Using Claude API")
    print("=" * 70)

    # Parse the current settlements file
    print("\n1. Parsing settlements.js...")
    settlements = parse_settlements_js(input_file)
    print(f"   Found {len(settlements)} entries")

    if not settlements:
        print("Error: Could not parse settlements file")
        return

    # Process in batches
    print("\n2. Reviewing entries to identify actual geographic locations...")
    batch_size = 50
    cleaned_settlements = []

    for i in range(0, len(settlements), batch_size):
        batch = settlements[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(settlements) + batch_size - 1) // batch_size

        cleaned_batch = clean_settlements_batch(batch, batch_num, total_batches)
        cleaned_settlements.extend(cleaned_batch)

    # Generate cleaned file
    print("\n3. Generating cleaned settlements file...")
    generate_settlements_js(cleaned_settlements, output_file)

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"\nOriginal entries: {len(settlements)}")
    print(f"Cleaned entries: {len(cleaned_settlements)}")
    print(f"Removed: {len(settlements) - len(cleaned_settlements)}")
    print(f"\nCleaned file created: {output_file}")
    print("\nReview the file and then run:")
    print("  cp settlements_cleaned.js settlements.js")

if __name__ == "__main__":
    main()

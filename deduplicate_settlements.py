#!/usr/bin/env python3
"""
Intelligently deduplicate settlements, removing demonyms and variations
while keeping the actual location names.
"""

import os
import re
import json
import math
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

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate approximate distance in km between two coordinates."""
    # Simplified distance calculation
    dlat = abs(lat1 - lat2)
    dlng = abs(lng1 - lng2)
    return math.sqrt(dlat**2 + dlng**2) * 111  # Rough km conversion

def find_duplicate_groups(settlements):
    """Group settlements that might be duplicates based on name similarity and location."""
    groups = []
    used = set()

    for i, s1 in enumerate(settlements):
        if i in used:
            continue

        group = [i]
        name1_lower = s1['name'].lower()
        name1_base = re.sub(r'(ian|ians|s|ese|ites|ite|iot|iots)$', '', name1_lower)

        for j, s2 in enumerate(settlements[i+1:], start=i+1):
            if j in used:
                continue

            name2_lower = s2['name'].lower()
            name2_base = re.sub(r'(ian|ians|s|ese|ites|ite|iot|iots)$', '', name2_lower)

            # Check if names are similar
            names_similar = (
                name1_base == name2_base or
                name1_lower.startswith(name2_lower) or
                name2_lower.startswith(name1_lower) or
                name1_lower in name2_lower or
                name2_lower in name1_lower
            )

            # Check if locations are close (within 50km)
            distance = calculate_distance(s1['lat'], s1['lng'], s2['lat'], s2['lng'])
            location_close = distance < 50

            if names_similar and location_close:
                group.append(j)
                used.add(j)

        if len(group) > 1:
            groups.append(group)
            used.add(i)
        elif i not in used:
            # Single item, no duplicates
            groups.append([i])

    return groups

def deduplicate_group(settlements_group, group_num, total_groups):
    """Use Claude to choose which entry to keep from a group of potential duplicates."""
    if len(settlements_group) == 1:
        return [settlements_group[0]]

    print(f"\nProcessing duplicate group {group_num}/{total_groups}...")

    # Format the group for review
    group_text = []
    for i, s in enumerate(settlements_group):
        group_text.append(f"{i+1}. {s['name']} (modern: {s['modern']}, type: {s['type']}, coordinates: {s['lat']}, {s['lng']})")

    settlements_text = "\n".join(group_text)

    prompt = f"""You are reviewing a group of location entries that appear to be duplicates or variations of the same place.

Your task: Choose which entry or entries to KEEP from this group.

Guidelines:
- KEEP the actual place name (e.g., "Ambracia" over "Ambraciots" or "Ambraciot")
- REMOVE demonyms (ethnic/people names like "Athenians", "Spartans", "Ambraciots")
- REMOVE adjectival forms (like "Athenian", "Spartan", "Ambracian")
- If multiple legitimate place names exist (e.g., "Achaean Rhium" and "Achaea"), keep both
- If the coordinates are significantly different (>1 degree), they might be different places - keep both
- Prefer entries with more specific type information
- If in doubt, keep the shortest, most standard place name

DUPLICATE GROUP:
{settlements_text}

Return ONLY a JSON array with the numbers of entries to KEEP.
For example: [1] or [1, 3] if multiple should be kept.

Return ONLY the JSON array, no explanation."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
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

            kept = [settlements_group[i] for i in keep_indices if i < len(settlements_group)]
            removed = [s['name'] for i, s in enumerate(settlements_group) if i not in keep_indices]

            if removed:
                print(f"  Kept: {', '.join([s['name'] for s in kept])}")
                print(f"  Removed: {', '.join(removed)}")

            return kept
        else:
            print(f"  Warning: Could not parse response, keeping all entries")
            return settlements_group

    except Exception as e:
        print(f"  Error: {e}")
        return settlements_group

def generate_settlements_js(locations, output_file):
    """Generate the deduplicated settlements.js file."""
    print(f"\nGenerating {output_file}...")

    # Sort locations by name
    locations.sort(key=lambda x: x['name'])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// Ancient Greek settlements and locations mentioned in Thucydides'\n")
        f.write("// History of the Peloponnesian War\n")
        f.write("// Automatically extracted and geocoded using Claude AI\n")
        f.write("// Cleaned and deduplicated\n\n")
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
    input_file = "settlements_cleaned.js"
    output_file = "settlements_final.js"

    # Check if cleaned file exists, otherwise use settlements.js
    if not os.path.exists(input_file):
        input_file = "settlements.js"
        print(f"Note: Using {input_file} as input (settlements_cleaned.js not found)")

    print("=" * 70)
    print("Deduplicating Settlements")
    print("=" * 70)

    # Parse the settlements file
    print("\n1. Parsing settlements file...")
    settlements = parse_settlements_js(input_file)
    print(f"   Found {len(settlements)} entries")

    if not settlements:
        print("Error: Could not parse settlements file")
        return

    # Find potential duplicate groups
    print("\n2. Identifying potential duplicate groups...")
    groups = find_duplicate_groups(settlements)
    duplicate_groups = [g for g in groups if len(g) > 1]
    print(f"   Found {len(duplicate_groups)} groups with potential duplicates")
    print(f"   {len(groups) - len(duplicate_groups)} unique entries")

    # Process duplicate groups
    print("\n3. Processing duplicate groups with Claude API...")
    deduplicated = []

    for i, group_indices in enumerate(groups, 1):
        group = [settlements[idx] for idx in group_indices]

        if len(group) > 1:
            # Process duplicate group
            kept = deduplicate_group(group, i, len(groups))
        else:
            # Single entry, keep it
            kept = group

        deduplicated.extend(kept)

    # Generate output file
    print("\n4. Generating deduplicated settlements file...")
    generate_settlements_js(deduplicated, output_file)

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"\nOriginal entries: {len(settlements)}")
    print(f"Deduplicated entries: {len(deduplicated)}")
    print(f"Removed: {len(settlements) - len(deduplicated)}")
    print(f"\nDeduplicated file created: {output_file}")
    print("\nReview the file and then run:")
    print("  cp settlements_final.js settlements.js")

if __name__ == "__main__":
    main()

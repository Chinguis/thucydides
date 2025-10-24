#!/usr/bin/env python3
"""
Extract locations from Thucydides' History of the Peloponnesian War
and generate a settlements.js file with coordinates.
"""

import os
import re
import json
from bs4 import BeautifulSoup
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def extract_text_from_html(html_file):
    """Extract text content from HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading/trailing space
    lines = (line.strip() for line in text.splitlines())

    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

def chunk_text(text, chunk_size=100000):
    """Split text into chunks for processing."""
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1

        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def extract_locations_from_chunk(text_chunk, chunk_num, total_chunks):
    """Use Claude to extract locations from a text chunk."""
    print(f"Processing chunk {chunk_num}/{total_chunks}...")

    prompt = f"""You are analyzing a portion of Thucydides' "History of the Peloponnesian War" (chunk {chunk_num} of {total_chunks}).

Please identify ALL geographic locations mentioned in this text. This includes:
- Cities (poleis) like Athens, Sparta, Syracuse
- Islands like Corcyra, Sicily, Crete
- Regions like Attica, Boeotia, Peloponnese
- Sanctuaries like Delphi, Olympia
- Forts, ports, and other settlements
- Mountains, passes, and other geographic features that have specific names
- Harbors and anchorages with proper names

For each location, determine:
1. The name EXACTLY as it appears in the text (preserve the exact spelling used in this translation)
2. The modern name or closest modern equivalent
3. The type (Major Polis, Polis, Sanctuary, Fort, Port, Island, Region, Settlement, Pass, Mountain, Harbor, etc.)

Return your response as a JSON array with this format:
[
  {{"name": "Athens", "modern": "Athens", "type": "Major Polis"}},
  {{"name": "Pylos", "modern": "Pylos", "type": "Settlement"}},
  ...
]

IMPORTANT:
- Only include locations that are specifically mentioned in the text below. Do not include locations you think might be mentioned elsewhere.
- Use the EXACT spelling of the location name as it appears in this text. Do not standardize or transliterate differently.

TEXT TO ANALYZE:
{text_chunk}

Return ONLY the JSON array, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to find JSON in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            locations = json.loads(json_match.group())
            print(f"  Found {len(locations)} locations in this chunk")
            return locations
        else:
            print(f"  Warning: Could not parse JSON from response")
            return []

    except Exception as e:
        print(f"  Error processing chunk: {e}")
        return []

def get_coordinates_batch(locations):
    """Use Claude to get coordinates for a batch of locations."""
    print(f"\nGetting coordinates for {len(locations)} locations...")

    location_list = "\n".join([f"- {loc['name']} (modern: {loc['modern']}, type: {loc['type']})"
                                for loc in locations])

    prompt = f"""You are a historical geographer specializing in Ancient Greece during the Peloponnesian War era (431-404 BC).

For each location below, provide:
1. The approximate latitude and longitude coordinates
2. Verify/correct the modern name if needed
3. Verify/correct the type if needed

For ancient settlements that no longer exist, use the coordinates of the archaeological site or the closest modern location to where they were historically located.

LOCATIONS:
{location_list}

Return your response as a JSON array with this EXACT format:
[
  {{"name": "Athens", "modern": "Athens", "lat": 37.9838, "lng": 23.7275, "type": "Major Polis"}},
  {{"name": "Sparta", "modern": "Sparta", "lat": 37.0810, "lng": 22.4300, "type": "Major Polis"}},
  ...
]

IMPORTANT:
- Use decimal degrees (not DMS format)
- Latitude: positive for North, negative for South
- Longitude: positive for East, negative for West
- Be as accurate as possible based on historical and archaeological evidence
- Return ONLY the JSON array, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.content[0].text
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            locations_with_coords = json.loads(json_match.group())
            print(f"  Successfully retrieved coordinates for {len(locations_with_coords)} locations")
            return locations_with_coords
        else:
            print(f"  Warning: Could not parse JSON from response")
            return locations

    except Exception as e:
        print(f"  Error getting coordinates: {e}")
        return locations

def deduplicate_locations(all_locations):
    """Remove duplicate locations and merge information."""
    print("\nDeduplicating locations...")
    unique_locations = {}

    for loc in all_locations:
        name = loc['name']
        if name not in unique_locations:
            unique_locations[name] = loc
        else:
            # Keep the entry with more information (coordinates if available)
            existing = unique_locations[name]
            if 'lat' in loc and 'lat' not in existing:
                unique_locations[name] = loc

    result = list(unique_locations.values())
    print(f"  Reduced from {len(all_locations)} to {len(result)} unique locations")
    return result

def generate_settlements_js(locations, output_file):
    """Generate the settlements.js file."""
    print(f"\nGenerating {output_file}...")

    # Sort locations by name
    locations.sort(key=lambda x: x['name'])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// Ancient Greek settlements and locations mentioned in Thucydides'\n")
        f.write("// History of the Peloponnesian War\n")
        f.write("// Automatically extracted and geocoded using Claude AI\n\n")
        f.write("const settlements = [\n")

        for i, loc in enumerate(locations):
            # Format the entry
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
    html_file = "thucydides.htm"
    output_file = "settlements_new.js"

    print("=" * 70)
    print("Extracting Locations from Thucydides")
    print("=" * 70)

    # Check if HTML file exists
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        return

    # Extract text from HTML
    print("\n1. Extracting text from HTML...")
    text = extract_text_from_html(html_file)
    print(f"   Extracted {len(text)} characters")

    # Split into chunks
    print("\n2. Splitting text into chunks...")
    chunks = chunk_text(text, chunk_size=80000)
    print(f"   Created {len(chunks)} chunks")

    # Extract locations from each chunk
    print("\n3. Extracting locations from text...")
    all_locations = []
    for i, chunk in enumerate(chunks, 1):
        locations = extract_locations_from_chunk(chunk, i, len(chunks))
        all_locations.extend(locations)

    print(f"\n   Total locations extracted: {len(all_locations)}")

    # Deduplicate
    unique_locations = deduplicate_locations(all_locations)

    # Get coordinates in batches
    print("\n4. Getting coordinates for locations...")
    batch_size = 50
    locations_with_coords = []

    for i in range(0, len(unique_locations), batch_size):
        batch = unique_locations[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(unique_locations) + batch_size - 1) // batch_size
        print(f"\n   Processing batch {batch_num}/{total_batches}...")

        coords_batch = get_coordinates_batch(batch)
        locations_with_coords.extend(coords_batch)

    # Generate output file
    print("\n5. Generating settlements.js file...")
    generate_settlements_js(locations_with_coords, output_file)

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"\nNew settlements file created: {output_file}")
    print(f"Total locations: {len(locations_with_coords)}")
    print("\nReview the file and then rename it to 'settlements.js' to use it.")

if __name__ == "__main__":
    main()

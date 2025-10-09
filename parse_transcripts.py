import re
import os
from pathlib import Path

def parse_vtt_file(input_path, output_path):
    """Parse VTT file and extract only the dialogue text."""
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    dialogue_lines = []
    skip_until_blank = True

    for line in lines:
        line = line.strip()

        # Skip header section (until we find the first blank line after WEBVTT)
        if skip_until_blank:
            if line == '' and len(dialogue_lines) == 0:
                skip_until_blank = False
            continue

        # Skip empty lines
        if not line:
            continue

        # Skip sequence numbers (lines that are just digits)
        if line.isdigit():
            continue

        # Skip timestamp lines (contains -->)
        if '-->' in line:
            continue

        # Skip NOTE lines
        if line.startswith('NOTE'):
            continue

        # Remove HTML tags
        line = re.sub(r'<[^>]+>', '', line)

        # Skip if empty after cleaning
        if not line:
            continue

        dialogue_lines.append(line)

    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dialogue_lines))

def main():
    input_dir = Path('/Users/nathangiusti/Documents/GitHub/BakeOff/netflix_transcripts')
    output_dir = Path('/Users/nathangiusti/Documents/GitHub/BakeOff/parsed_transcripts')

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Process all VTT files
    vtt_files = list(input_dir.glob('*.vtt'))
    print(f"Found {len(vtt_files)} VTT files to process")

    for vtt_file in vtt_files:
        # Skip forced subtitle files
        if 'forced' in vtt_file.name:
            print(f"Skipping forced subtitle file: {vtt_file.name}")
            continue

        output_file = output_dir / vtt_file.name.replace('.vtt', '.txt')
        print(f"Processing: {vtt_file.name} -> {output_file.name}")
        parse_vtt_file(vtt_file, output_file)

    print(f"\nComplete! Parsed transcripts saved to: {output_dir}")

if __name__ == '__main__':
    main()

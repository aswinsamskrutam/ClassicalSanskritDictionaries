#!/usr/bin/env python3
"""
Extract Slokas from OCR Text to YAML
Processes OCR-extracted text and creates a YAML file with slokas
"""

import re
import sys
import argparse
from pathlib import Path
import yaml


def extract_slokas(text_content):
    """
    Extract slokas from OCR text, removing verse numbers

    Args:
        text_content: Raw OCR text content

    Returns:
        List of sloka dictionaries
    """
    slokas = []

    # Split by lines
    lines = text_content.split('\n')

    current_sloka = []
    sloka_number = 0

    for line in lines:
        # Skip page markers and empty lines
        if line.strip().startswith('---') or not line.strip():
            continue

        # Skip header/footer lines
        if 'कोषः' in line or 'काण्डः' in line or 'अथ ' in line.strip()[:5]:
            continue

        # Check if line contains Sanskrit text (Devanagari script)
        if re.search(r'[\u0900-\u097F]', line):
            # Remove line numbers from the beginning (like "1→")
            cleaned_line = re.sub(r'^\d+→', '', line).strip()

            # Remove sloka numbers at the end (like "॥ १॥" or "। १।")
            cleaned_line = re.sub(r'[।॥]\s*\d+\s*[।॥]\s*$', '॥', cleaned_line)
            cleaned_line = re.sub(r'[।॥]\s*\d+\s*$', '॥', cleaned_line)

            # Check if this line ends a sloka (contains ॥ or ।)
            if '॥' in cleaned_line or cleaned_line.strip().endswith('।'):
                current_sloka.append(cleaned_line)

                # Join the sloka lines
                full_sloka = ' '.join(current_sloka).strip()

                # Clean up extra spaces
                full_sloka = re.sub(r'\s+', ' ', full_sloka)

                # Only add if it has substantial content
                if len(full_sloka) > 10:
                    sloka_number += 1
                    slokas.append({
                        'sloka_number': sloka_number,
                        'text': full_sloka
                    })

                # Reset for next sloka
                current_sloka = []
            else:
                # Continue building current sloka
                if cleaned_line:
                    current_sloka.append(cleaned_line)

    return slokas


def create_yaml_output(slokas, title="अथ आदिदेवाध्यायः", khanda="स्वर्गकाण्डः"):
    """
    Create YAML structure for slokas

    Args:
        slokas: List of sloka dictionaries
        title: Title of the adhyaya
        khanda: Name of the khanda

    Returns:
        Dictionary ready for YAML output
    """
    output = {
        'khanda': khanda,
        'adhyaya': title,
        'total_slokas': len(slokas),
        'slokas': []
    }

    for sloka in slokas:
        output['slokas'].append({
            'number': sloka['sloka_number'],
            'text': sloka['text']
        })

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Extract slokas from OCR text and save to YAML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract slokas from raw OCR text
  python extract_slokas_to_yaml.py raw_text.txt -o slokas.yaml

  # With custom title and khanda
  python extract_slokas_to_yaml.py raw_text.txt -o slokas.yaml \\
    --title "अथ आदिदेवाध्यायः" --khanda "स्वर्गकाण्डः"
        """
    )

    parser.add_argument('input_text', help='Input text file (OCR output)')
    parser.add_argument('-o', '--output', required=True, help='Output YAML file')
    parser.add_argument('--title', default='अथ आदिदेवाध्यायः',
                        help='Title of the adhyaya')
    parser.add_argument('--khanda', default='स्वर्गकाण्डः',
                        help='Name of the khanda')

    args = parser.parse_args()

    # Read input file
    if not Path(args.input_text).exists():
        print(f"Error: Input file not found: {args.input_text}")
        sys.exit(1)

    print(f"Reading OCR text from: {args.input_text}")
    with open(args.input_text, 'r', encoding='utf-8') as f:
        text_content = f.read()

    # Extract slokas
    print("Extracting slokas from text...")
    slokas = extract_slokas(text_content)
    print(f"Found {len(slokas)} slokas")

    # Create YAML structure
    yaml_data = create_yaml_output(slokas, args.title, args.khanda)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write YAML file
    print(f"Writing YAML to: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False,
                  sort_keys=False, indent=2)

    print(f"\nSuccessfully created YAML file with {len(slokas)} slokas")
    print(f"Output saved to: {args.output}")


if __name__ == '__main__':
    main()

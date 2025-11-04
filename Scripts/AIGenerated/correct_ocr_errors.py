#!/usr/bin/env python3
"""
OCR Error Correction for Sanskrit Text using Claude API
Corrects OCR errors in Sanskrit slokas using AI
"""

import sys
import argparse
from pathlib import Path
import yaml
import anthropic
import os


def correct_sloka_with_claude(sloka_text, client):
    """
    Use Claude API to correct OCR errors in a Sanskrit sloka

    Args:
        sloka_text: The sloka text with potential OCR errors
        client: Anthropic API client

    Returns:
        Corrected sloka text
    """
    prompt = f"""You are a Sanskrit scholar expert in classical Sanskrit texts, particularly kosha (synonym dictionaries) like Amarakosha and Vaijayanti Kosha.

Below is a sloka extracted from OCR that may contain errors. Please correct any OCR errors while maintaining the exact meter and meaning. Common OCR errors in Devanagari include:
- ब/व confusion (ba/va)
- ष/श confusion (ṣa/śa)
- missing anusvara (ं) or visarga (ः)
- ि/ी confusion (i/ī)
- Incorrect matras

Return ONLY the corrected sloka text, nothing else. Keep the same structure with । and ॥ dandas.

Original sloka:
{sloka_text}

Corrected sloka:"""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        corrected = message.content[0].text.strip()
        return corrected
    except Exception as e:
        print(f"Error correcting sloka: {e}")
        return sloka_text  # Return original if correction fails


def correct_yaml_file(input_yaml, output_yaml, api_key=None):
    """
    Correct OCR errors in all slokas in a YAML file

    Args:
        input_yaml: Path to input YAML file
        output_yaml: Path to output YAML file
        api_key: Anthropic API key (optional, uses env var if not provided)
    """
    # Initialize Anthropic client
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
    else:
        # Try to get from environment variable
        client = anthropic.Anthropic()  # Will use ANTHROPIC_API_KEY env var

    # Read input YAML
    print(f"Reading YAML from: {input_yaml}")
    with open(input_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    print(f"Found {len(data)} slokas to correct")

    # Correct each sloka
    corrected_data = {}
    for i, (sloka, metadata) in enumerate(data.items(), 1):
        print(f"Correcting sloka {i}/{len(data)}...", end='\r')

        corrected_sloka = correct_sloka_with_claude(sloka, client)

        # Remove any newlines to ensure single-line format
        corrected_sloka = corrected_sloka.replace('\n', ' ')
        # Clean up multiple spaces
        corrected_sloka = ' '.join(corrected_sloka.split())
        # Normalize double danda: replace ।। (two singles) with ॥ (proper double)
        corrected_sloka = corrected_sloka.replace('।।', '॥')

        # Store only the corrected sloka with empty metadata
        corrected_data[corrected_sloka] = {}

    print(f"\nCompleted correction of {len(data)} slokas")

    # Ensure output directory exists
    output_path = Path(output_yaml)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output YAML
    print(f"Writing corrected YAML to: {output_yaml}")
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(corrected_data, f, allow_unicode=True, default_flow_style=False,
                  sort_keys=False, indent=2, width=float('inf'))

    print(f"\n✓ Successfully corrected and saved to: {output_yaml}")


def main():
    parser = argparse.ArgumentParser(
        description='Correct OCR errors in Sanskrit slokas using Claude API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Correct OCR errors in YAML file
  python correct_ocr_errors.py input.yaml -o corrected.yaml

  # With explicit API key
  python correct_ocr_errors.py input.yaml -o corrected.yaml --api-key YOUR_KEY

  # Uses ANTHROPIC_API_KEY environment variable by default
  export ANTHROPIC_API_KEY=your_key_here
  python correct_ocr_errors.py input.yaml -o corrected.yaml

Note: This script requires the 'anthropic' package:
  pip install anthropic
        """
    )

    parser.add_argument('input_yaml', help='Input YAML file with OCR text')
    parser.add_argument('-o', '--output', required=True,
                        help='Output YAML file with corrected text')
    parser.add_argument('--api-key',
                        help='Anthropic API key (optional, uses ANTHROPIC_API_KEY env var)')

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input_yaml).exists():
        print(f"Error: Input file not found: {args.input_yaml}")
        sys.exit(1)

    try:
        correct_yaml_file(args.input_yaml, args.output, args.api_key)
    except anthropic.AuthenticationError:
        print("\nError: Authentication failed. Please provide a valid API key.")
        print("Set ANTHROPIC_API_KEY environment variable or use --api-key option")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

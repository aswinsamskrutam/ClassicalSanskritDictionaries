#!/usr/bin/env python3
"""
PDF to YAML Converter for Sanskrit Texts
Converts Sanskrit PDF pages to YAML format with slokas (without intermediate files)
"""

import sys
import argparse
import re
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import yaml


def pdf_to_text(pdf_path, lang='san'):
    """
    Convert PDF to text using OCR (in-memory, no intermediate file)

    Args:
        pdf_path: Path to input PDF file
        lang: Language code for Tesseract (default: 'san' for Sanskrit)

    Returns:
        Extracted text as string
    """
    print(f"Converting PDF: {pdf_path}")
    print("This may take a few minutes...")

    # Convert PDF pages to images
    print("\nStep 1: Converting PDF pages to images...")
    images = convert_from_path(pdf_path)
    print(f"Found {len(images)} pages")

    # Extract text from each page
    print("\nStep 2: Extracting text from each page...")
    all_text = []

    for i, image in enumerate(images, 1):
        print(f"Processing page {i}/{len(images)}...", end='\r')
        text = pytesseract.image_to_string(image, lang=lang)
        all_text.append(text)

    print(f"\nProcessing complete! Extracted text from {len(images)} pages")

    # Combine all text
    return '\n'.join(all_text)


def extract_slokas(text_content):
    """
    Extract slokas from OCR text, removing verse numbers
    Each sloka ends with double danda (॥)

    Args:
        text_content: Raw OCR text content

    Returns:
        List of sloka text strings
    """
    slokas = []
    lines = text_content.split('\n')
    current_sloka = []

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Skip header/footer lines
        if 'कोषः' in line or 'काण्डः' in line or 'अध्यायः' in line:
            continue

        # Check if line contains Sanskrit text (Devanagari script)
        if re.search(r'[\u0900-\u097F]', line):
            # Clean the line
            cleaned_line = line.strip()

            # Remove sloka numbers at the end (like "॥ १॥" or "। १।")
            cleaned_line = re.sub(r'[।॥]\s*\d+\s*[।॥]\s*$', '॥', cleaned_line)
            cleaned_line = re.sub(r'[।॥]\s*\d+\s*$', '॥', cleaned_line)
            # Also remove numbers before dandas
            cleaned_line = re.sub(r'\d+\s*[।॥]', '॥', cleaned_line)

            # Add to current sloka
            if cleaned_line:
                current_sloka.append(cleaned_line)

            # Check if this completes a sloka (ends with double danda ॥)
            if '॥' in cleaned_line:
                # Join the sloka lines
                full_sloka = ' '.join(current_sloka).strip()

                # Clean up extra spaces
                full_sloka = re.sub(r'\s+', ' ', full_sloka)

                # Remove any remaining stray numbers near dandas
                full_sloka = re.sub(r'\s*\d+\s*॥', '॥', full_sloka)

                # Only add if it has substantial content
                if len(full_sloka) > 15:
                    slokas.append(full_sloka)

                # Reset for next sloka
                current_sloka = []

    return slokas


def create_yaml_output(slokas, title, khanda):
    """
    Create YAML structure for slokas
    Each sloka is a key in a dictionary with metadata

    Args:
        slokas: List of sloka text strings
        title: Title of the adhyaya
        khanda: Name of the khanda

    Returns:
        Dictionary ready for YAML output
    """
    output = {}

    for sloka in slokas:
        # Use the sloka text as the key, with empty metadata dict as value
        output[sloka] = {}

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Convert Sanskrit PDF to YAML with slokas (direct conversion)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF directly to YAML
  python pdf_to_yaml.py input.pdf -o output.yaml \\
    --title "आदिदेवाध्यायः" --khanda "स्वर्गकाण्डः"

  # With default Sanskrit OCR language
  python pdf_to_yaml.py Input/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.pdf \\
    -o Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.yaml \\
    --title "आदिदेवाध्यायः" --khanda "स्वर्गकाण्डः"
        """
    )

    parser.add_argument('input_pdf', help='Input PDF file path')
    parser.add_argument('-o', '--output', required=True, help='Output YAML file path')
    parser.add_argument('--title', default='आदिदेवाध्यायः',
                        help='Title of the adhyaya')
    parser.add_argument('--khanda', default='स्वर्गकाण्डः',
                        help='Name of the khanda')
    parser.add_argument('-l', '--lang', default='san',
                        help='Language code for OCR (default: san for Sanskrit)')

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input_pdf).exists():
        print(f"Error: Input file not found: {args.input_pdf}")
        sys.exit(1)

    # Step 1: Extract text from PDF using OCR
    text_content = pdf_to_text(args.input_pdf, args.lang)

    # Step 2: Extract slokas from text
    print("\nStep 3: Extracting slokas from text...")
    slokas = extract_slokas(text_content)
    print(f"Found {len(slokas)} slokas")

    # Step 3: Create YAML structure
    yaml_data = create_yaml_output(slokas, args.title, args.khanda)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 4: Write YAML file
    print(f"\nStep 4: Writing YAML to: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False,
                  sort_keys=False, indent=2, width=float('inf'))  # width=inf prevents line wrapping

    print(f"\n✓ Successfully created YAML file with {len(slokas)} slokas")
    print(f"✓ Output saved to: {args.output}")


if __name__ == '__main__':
    main()

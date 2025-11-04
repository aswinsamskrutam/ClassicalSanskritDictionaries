#!/usr/bin/env python3
"""
Complete PDF to Corrected YAML Pipeline
Converts Sanskrit PDF to YAML using OCR, then corrects errors with Claude via Vertex AI
"""

import sys
import argparse
from pathlib import Path
import yaml
import tempfile
from anthropic import AnthropicVertex

# Import functions from existing scripts
from pdf_to_yaml import pdf_to_text, extract_slokas, create_yaml_output


def correct_sloka_with_claude(sloka_text, client):
    """
    Use Claude API (via Vertex AI) to correct OCR errors in a Sanskrit sloka

    Args:
        sloka_text: The sloka text with potential OCR errors
        client: Anthropic Vertex AI client

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
            model="claude-3-5-haiku@20241022",
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


def main():
    parser = argparse.ArgumentParser(
        description='Convert Sanskrit PDF to corrected YAML (OCR + AI correction)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline: PDF → OCR → AI Correction → Final YAML
  python pdf_to_corrected_yaml.py \\
    Input/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.pdf \\
    -o Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.yaml \\
    --project-id my-project \\
    --title "आदिदेवाध्यायः" \\
    --khanda "स्वर्गकाण्डः"

Note: This script combines OCR and AI correction in a single step.
The intermediate OCR YAML is stored temporarily and not saved.
        """
    )

    parser.add_argument('input_pdf', help='Input PDF file path')
    parser.add_argument('-o', '--output', required=True,
                        help='Output corrected YAML file path')
    parser.add_argument('--project-id', required=True,
                        help='Google Cloud project ID')
    parser.add_argument('--region', default='us-east5',
                        help='Vertex AI region (default: us-east5)')
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

    print("=" * 80)
    print("SANSKRIT PDF TO CORRECTED YAML PIPELINE")
    print("=" * 80)

    # Step 1: Extract text from PDF using OCR
    print("\n[1/4] Running OCR on PDF...")
    text_content = pdf_to_text(args.input_pdf, args.lang)

    # Step 2: Extract slokas from text
    print("\n[2/4] Extracting slokas from OCR text...")
    slokas = extract_slokas(text_content)
    print(f"Found {len(slokas)} slokas")

    # Step 3: Create temporary YAML structure
    print("\n[3/4] Creating temporary YAML structure...")
    yaml_data = create_yaml_output(slokas, args.title, args.khanda)

    # Step 4: Correct OCR errors with Claude
    print("\n[4/4] Correcting OCR errors with Claude AI...")
    print(f"Initializing Vertex AI client (region: {args.region})...")

    try:
        client = AnthropicVertex(region=args.region, project_id=args.project_id)
    except Exception as e:
        print(f"\nError: Failed to initialize Vertex AI client: {e}")
        print("\nMake sure you have:")
        print("1. Authenticated: gcloud auth application-default login")
        print("2. Enabled Claude models in Vertex AI Model Garden")
        sys.exit(1)

    # Correct each sloka
    corrected_data = {}
    total = len(yaml_data)
    for i, (sloka, metadata) in enumerate(yaml_data.items(), 1):
        print(f"Correcting sloka {i}/{total}...", end='\r')
        corrected_sloka = correct_sloka_with_claude(sloka, client)

        # Remove any newlines to ensure single-line format
        corrected_sloka = corrected_sloka.replace('\n', ' ')
        # Clean up multiple spaces
        corrected_sloka = ' '.join(corrected_sloka.split())
        # Normalize double danda: replace ।। (two singles) with ॥ (proper double)
        corrected_sloka = corrected_sloka.replace('।।', '॥')

        corrected_data[corrected_sloka] = {}

    print(f"\nCompleted correction of {total} slokas")

    # Step 5: Write final corrected YAML
    print(f"\n[5/5] Writing corrected YAML to: {args.output}")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        yaml.dump(corrected_data, f, allow_unicode=True, default_flow_style=False,
                  sort_keys=False, indent=2, width=float('inf'))

    print("\n" + "=" * 80)
    print(f"✓ Successfully created corrected YAML with {total} slokas")
    print(f"✓ Output saved to: {args.output}")
    print("=" * 80)


if __name__ == '__main__':
    main()

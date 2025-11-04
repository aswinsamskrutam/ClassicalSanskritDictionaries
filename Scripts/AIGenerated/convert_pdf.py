#!/usr/bin/env python3
"""
Sanskrit PDF OCR Converter
Converts Sanskrit PDFs to searchable text using Tesseract OCR
"""

import sys
import argparse
from pdf2image import convert_from_path
import pytesseract
from pathlib import Path


def pdf_to_text(pdf_path, output_path=None, lang='san'):
    """
    Convert PDF to text using OCR

    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output text file (optional)
        lang: Language code for Tesseract (default: 'san' for Sanskrit)
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
        all_text.append(f"--- Page {i} ---\n{text}\n")

    print(f"\nProcessing complete! Extracted text from {len(images)} pages")

    # Combine all text
    full_text = '\n'.join(all_text)

    # Save to file
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\nText saved to: {output_path}")
    else:
        # If no output path, create one based on input filename
        output_path = Path(pdf_path).stem + '_output.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\nText saved to: {output_path}")

    return full_text


def create_searchable_pdf(pdf_path, output_path=None, lang='san'):
    """
    Create a searchable PDF from a scanned PDF

    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output searchable PDF (optional)
        lang: Language code for Tesseract (default: 'san' for Sanskrit)
    """
    import ocrmypdf

    print(f"Creating searchable PDF: {pdf_path}")

    if not output_path:
        output_path = Path(pdf_path).stem + '_searchable.pdf'

    print("Processing... This may take several minutes for multi-page PDFs")

    try:
        ocrmypdf.ocr(
            pdf_path,
            output_path,
            language=lang,
            deskew=True,
            clean=True,
            progress_bar=True
        )
        print(f"\nSearchable PDF created: {output_path}")
    except Exception as e:
        print(f"\nError: {e}")
        return None

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Convert Sanskrit PDF to searchable text or searchable PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract text from PDF
  python convert_pdf.py input.pdf

  # Extract text and specify output file
  python convert_pdf.py input.pdf -o output.txt

  # Create searchable PDF
  python convert_pdf.py input.pdf --searchable

  # Use different language (e.g., Hindi)
  python convert_pdf.py input.pdf --lang hin
        """
    )

    parser.add_argument('input_pdf', help='Input PDF file path')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument(
        '-l', '--lang',
        default='san',
        help='Language code (default: san for Sanskrit, hin for Hindi/Devanagari)'
    )
    parser.add_argument(
        '--searchable',
        action='store_true',
        help='Create searchable PDF instead of text extraction'
    )

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input_pdf).exists():
        print(f"Error: File not found: {args.input_pdf}")
        sys.exit(1)

    if args.searchable:
        create_searchable_pdf(args.input_pdf, args.output, args.lang)
    else:
        pdf_to_text(args.input_pdf, args.output, args.lang)


if __name__ == '__main__':
    main()

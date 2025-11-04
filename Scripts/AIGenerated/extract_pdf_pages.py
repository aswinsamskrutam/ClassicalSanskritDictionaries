#!/usr/bin/env python3
"""
PDF Page Extractor
Extract specific pages from a PDF and save to a new file
"""

import sys
import argparse
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter


def extract_pages(input_pdf, output_pdf, from_page, to_page):
    """
    Extract pages from a PDF file

    Args:
        input_pdf: Path to input PDF file
        from_page: Starting page number (1-indexed)
        to_page: Ending page number (1-indexed, inclusive)
        output_pdf: Path to output PDF file
    """
    try:
        print(f"Reading PDF: {input_pdf}")
        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)

        print(f"Total pages in PDF: {total_pages}")

        # Validate page numbers
        if from_page < 1 or from_page > total_pages:
            print(f"Error: from_page {from_page} is out of range (1-{total_pages})")
            return False

        if to_page < 1 or to_page > total_pages:
            print(f"Error: to_page {to_page} is out of range (1-{total_pages})")
            return False

        if from_page > to_page:
            print(f"Error: from_page ({from_page}) cannot be greater than to_page ({to_page})")
            return False

        # Create PDF writer
        writer = PdfWriter()

        # Add pages (convert from 1-indexed to 0-indexed)
        print(f"Extracting pages {from_page} to {to_page}...")
        for page_num in range(from_page - 1, to_page):
            writer.add_page(reader.pages[page_num])
            print(f"  Added page {page_num + 1}")

        # Ensure output directory exists
        output_path = Path(output_pdf)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to output file
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        print(f"\nSuccessfully extracted {to_page - from_page + 1} page(s) to: {output_pdf}")
        return True

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_pdf}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Extract specific pages from a PDF file and organize by Kosha',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract pages 15-16 from Vaijayanti Kosa into SvargaKhanda/AdiDevaadhyaayah
  python extract_pdf_pages.py books/vaijayanti_kosa.pdf -f 15 -t 16 \\
    --kosha Vaijayanti_Kosha --khanda 1_SvargaKhanda --file 1_AdiDevaadhyaayah.pdf

  # Manual output path (old method still works)
  python extract_pdf_pages.py input.pdf -f 5 -t 5 -o page5.pdf

  # Extract pages 10-20 with kosha organization
  python extract_pdf_pages.py books/amarakosha.pdf -f 10 -t 20 \\
    --kosha Amarakosha --khanda 1_Svargavarga --file 1_Devaadhyaayah.pdf
        """
    )

    parser.add_argument('input_pdf', help='Input PDF file path (e.g., books/vaijayanti_kosa.pdf)')
    parser.add_argument('-f', '--from-page', type=int, required=True,
                        help='Starting page number (1-indexed)')
    parser.add_argument('-t', '--to-page', type=int, required=True,
                        help='Ending page number (1-indexed, inclusive)')
    parser.add_argument('-o', '--output',
                        help='Output PDF file path (optional if using --kosha)')
    parser.add_argument('--kosha',
                        help='Kosha name (e.g., Vaijayanti_Kosha, Amarakosha)')
    parser.add_argument('--khanda',
                        help='Khanda/section name (e.g., 1_SvargaKhanda)')
    parser.add_argument('--file',
                        help='Output filename (e.g., 1_AdiDevaadhyaayah.pdf)')

    args = parser.parse_args()

    # Determine output path
    if args.kosha and args.khanda and args.file:
        # Use kosha organization structure: Input/Kosha_Name/Khanda_Name/filename.pdf
        output_pdf = Path('Input') / args.kosha / args.khanda / args.file
        print(f"Using kosha organization: {output_pdf}")
    elif args.output:
        # Use manual output path
        output_pdf = args.output
    else:
        print("Error: Either provide --output OR (--kosha, --khanda, --file)")
        parser.print_help()
        sys.exit(1)

    # Check if input file exists
    if not Path(args.input_pdf).exists():
        print(f"Error: Input file not found: {args.input_pdf}")
        sys.exit(1)

    success = extract_pages(args.input_pdf, str(output_pdf), args.from_page, args.to_page)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

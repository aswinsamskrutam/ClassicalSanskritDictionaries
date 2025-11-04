# Classical Sanskrit Dictionaries

A toolkit for digitizing and processing classical Sanskrit dictionaries (Kosha) using OCR and AI-powered error correction.

## Overview

This project provides scripts to:
- Extract pages from Sanskrit dictionary PDFs
- Convert scanned PDFs to structured YAML format using OCR
- Correct OCR errors using Claude AI (via Anthropic API or Google Cloud Vertex AI)
- Organize dictionaries by Kosha → Khanda → Adhyaya

## Project Structure

```
ClassicalSanskritDictionaries/
├── books/                  # Source PDF files
├── Input/                  # Extracted PDF pages organized by Kosha
│   └── Vaijayanti_Kosha/
│       └── 1_SvargaKhanda/
│           └── 1_AdiDevaadhyaayah.pdf
├── Output/                 # Processed YAML files
│   └── Vaijayanti_Kosha/
│       └── 1_SvargaKhanda/
│           └── 1_AdiDevaadhyaayah.yaml
└── Scripts/
    └── AIGenerated/        # Processing scripts
```

## Scripts

### 1. Extract PDF Pages
Extract specific pages from a dictionary PDF:

```bash
python3 Scripts/AIGenerated/extract_pdf_pages.py \\
  books/vaijayanti_kosa.pdf \\
  -f 15 -t 16 \\
  --kosha Vaijayanti_Kosha \\
  --khanda 1_SvargaKhanda \\
  --file 1_AdiDevaadhyaayah.pdf
```

### 2. Convert PDF to YAML
Convert Sanskrit PDF to structured YAML using OCR:

```bash
python3 Scripts/AIGenerated/pdf_to_yaml.py \\
  Input/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.pdf \\
  -o Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.yaml \\
  --title "आदिदेवाध्यायः" \\
  --khanda "स्वर्गकाण्डः"
```

### 3. Correct OCR Errors
Improve OCR quality using Claude AI:

**Option A: Using Vertex AI (Recommended)**
```bash
python3 Scripts/AIGenerated/correct_ocr_errors_vertex.py \\
  Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.yaml \\
  -o Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah_corrected.yaml \\
  --project-id YOUR_GCP_PROJECT_ID
```

**Option B: Using Anthropic API**
```bash
export ANTHROPIC_API_KEY=your_key_here
python3 Scripts/AIGenerated/correct_ocr_errors.py \\
  input.yaml -o corrected.yaml
```

## Installation

### Prerequisites
```bash
# Python packages
pip3 install PyPDF2 pdf2image pytesseract Pillow pyyaml anthropic

# For Vertex AI support
pip3 install 'anthropic[vertex]'

# System dependencies (macOS)
brew install tesseract tesseract-lang

# For Sanskrit OCR
brew install tesseract-lang  # Includes Sanskrit
```

### Authentication

**For Vertex AI:**
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

**For Anthropic API:**
```bash
export ANTHROPIC_API_KEY=your_api_key
```

## YAML Format

The output YAML uses slokas as dictionary keys with metadata:

```yaml
स्वर्गं नाकः सुरालयः त्रिदिवं त्रिविष्टपम् ॥: {}
देवा विबुधाः त्रिदशाः सुराः अमराः ॥: {}
```

After correction:
```yaml
स्वर्गं नाकः सुरालयः त्रिदिवं त्रिविष्टपम् ॥:
  original: स्वगं नाकः सुरावास उष्वेलोकः फलोदयः ॥
  corrected: true
```

## Features

- **Automatic OCR**: Extracts Sanskrit text from scanned PDFs using Tesseract
- **AI Error Correction**: Uses Claude to fix common OCR errors (ब/व confusion, missing anusvara, etc.)
- **Structured Output**: Organizes data by Kosha → Khanda → Adhyaya
- **Metadata Tracking**: Preserves original OCR text for comparison
- **Complete Slokas**: Properly combines lines ending with double danda (॥)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Add your license here]

## Acknowledgments

- OCR powered by Tesseract
- Error correction powered by Claude AI (Anthropic)
- Sanskrit text from archive.org

# OCR Correction Scripts

This directory contains scripts to correct OCR errors in Sanskrit texts using Claude AI.

## Available Scripts

### 1. `correct_ocr_errors_vertex.py` (Recommended)
Uses Claude via Google Cloud Vertex AI.

**Prerequisites:**
```bash
# Install dependencies
pip3 install --break-system-packages 'anthropic[vertex]'

# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

**Usage:**
```bash
python3 Scripts/AIGenerated/correct_ocr_errors_vertex.py \
  Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.yaml \
  -o Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah_corrected.yaml \
  --project-id YOUR_GCP_PROJECT_ID
```

### 2. `correct_ocr_errors.py`
Uses Claude via direct Anthropic API.

**Prerequisites:**
```bash
# Install dependencies
pip3 install --break-system-packages anthropic

# Set API key
export ANTHROPIC_API_KEY=your_api_key_here
```

**Usage:**
```bash
python3 Scripts/AIGenerated/correct_ocr_errors.py \
  Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah.yaml \
  -o Output/Vaijayanti_Kosha/1_SvargaKhanda/1_AdiDevaadhyaayah_corrected.yaml
```

## What the Scripts Do

1. Read the input YAML file containing OCR-extracted slokas
2. For each sloka, use Claude to:
   - Identify common OCR errors (ब/व confusion, missing anusvara, etc.)
   - Correct the errors while maintaining meter and meaning
   - Preserve the original structure
3. Save corrected slokas to output YAML with metadata tracking changes

## Output Format

The corrected YAML will have:
```yaml
स्वर्गं नाकः सुरालयः त्रिदिवं त्रिविष्टपम् ।:
  original: स्वगं नाकः सुरावास उष्वेलोकः फलोदयः ।
  corrected: true
```

## Notes

- The script processes ~68 slokas and may take a few minutes
- API costs apply (both Vertex AI and Anthropic API)
- Original uncorrected slokas are preserved in the metadata

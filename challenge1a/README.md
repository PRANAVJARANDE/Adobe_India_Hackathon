# Challenge 1A: PDF Heading Extraction

This solution extracts titles and hierarchical outlines from PDF documents using advanced text analysis techniques.

## Features

- **Smart Title Extraction**: Uses block-level text reconstruction to handle fragmented titles
- **Form Detection**: Automatically detects forms and returns empty outlines as required
- **Hierarchical Heading Detection**: Extracts H1, H2, H3 headings with reduced font-size dependency
- **Context-Aware Scoring**: Uses multiple signals beyond font size (bold, numbering, capitalization, etc.)

## Usage

### Docker (Recommended)

```bash
# Build the image
docker build -t challenge1a .

# Run with input PDFs
docker run -v /path/to/input:/app/input -v /path/to/output:/app/output challenge1a
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export INPUT_DIR=input
export OUTPUT_DIR=output

# Run the application
python main.py
```

## Input Format

Place PDF files in the `input/` directory. The application will process all `.pdf` files found.

## Output Format

For each input PDF `filename.pdf`, generates `filename.json` with:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Heading Text",
      "page": 1
    }
  ]
}
```

## Algorithm Details

1. **PDF Parsing**: Uses PyMuPDF with block-level text reconstruction
2. **Title Extraction**: Finds largest meaningful text on first page with validation
3. **Form Detection**: Identifies forms using LTC-specific patterns and structural analysis
4. **Heading Detection**: Multi-factor scoring with reduced font-size dependency
5. **Hierarchical Classification**: Assigns H1/H2/H3 levels based on combined signals

## Team

**Team Placeholder** from ABV-IIITM
- Ayush Sah
- Pranav Jarande
- Manas Gupta
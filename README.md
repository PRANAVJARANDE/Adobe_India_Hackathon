# Adobe India Hackathon 2024 - PDF Analysis Solution

**Team Placeholder** from ABV-IIITM
- Ayush Sah
- Pranav Jarande  
- Manas Gupta

This repository contains solutions for both challenges of the Adobe India Hackathon 2024, focused on advanced PDF analysis and processing.

## Challenges

### [Challenge 1A: PDF Heading Extraction](./challenge1a/)
Extracts titles and hierarchical outlines from PDF documents using advanced text analysis techniques with smart form detection and context-aware heading classification.

### [Challenge 1B: Semantic Document Search](./challenge1b/)
Performs semantic search across PDF document collections using embeddings and intelligent ranking algorithms for relevant content retrieval.

## Repository Structure

```
├── challenge1a/          # Challenge 1A: PDF Heading Extraction
│   ├── round1a/          # Core extraction modules
│   ├── utils/            # Utility functions
│   ├── Dockerfile        # Container configuration
│   ├── main.py           # Application entry point
│   ├── requirements.txt  # Python dependencies
│   └── README.md         # Challenge-specific documentation
├── challenge1b/          # Challenge 1B: Semantic Document Search
│   ├── round1b/          # Core search modules
│   ├── utils/            # Utility functions
│   ├── Dockerfile        # Container configuration
│   ├── main.py           # Application entry point
│   ├── requirements.txt  # Python dependencies
│   └── README.md         # Challenge-specific documentation
└── README.md             # This file
```

## Quick Start

### Challenge 1A (PDF Heading Extraction)

```bash
cd challenge1a
docker build -t challenge1a .
docker run -v /path/to/input:/app/input -v /path/to/output:/app/output challenge1a
```

### Challenge 1B (Semantic Document Search)

```bash
cd challenge1b
docker build -t challenge1b .
docker run -v /path/to/collection:/app/input -v /path/to/output:/app/output challenge1b
```

## Key Features

### Challenge 1A
- **Smart Title Extraction** with fragmentation handling using block-level text reconstruction
- **Form Detection** for appropriate empty outline responses (LTC forms, etc.)
- **Context-Aware Heading Detection** with reduced font-size dependency
- **Hierarchical Classification** using multiple text analysis signals (bold, numbering, capitalization)

### Challenge 1B
- **Semantic Embeddings** for deep content understanding using sentence-transformers
- **Multi-Document Processing** across document collections
- **Intelligent Ranking** with relevance scoring and cosine similarity
- **Flexible Query Support** for both jury and custom formats

## Technology Stack

- **Python 3.9+** - Core programming language
- **PyMuPDF (fitz)** - PDF processing and text extraction
- **sentence-transformers** - Semantic embeddings for search
- **scikit-learn** - Machine learning utilities
- **Docker** - Containerization for consistent deployment

## Algorithm Highlights

### Challenge 1A Improvements
- **Block-level text reconstruction** inspired by Kaggle solutions for better title extraction
- **Multi-factor heading scoring** with reduced font-size dependency as per challenge guidelines
- **Smart form detection** using LTC-specific patterns and structural analysis
- **Context clues** including centering, capitalization, and numbering patterns

### Challenge 1B Features
- **Offline semantic search** with pre-trained models
- **Document chunking** for better relevance matching
- **Score normalization** for consistent ranking across queries
- **Flexible input formats** supporting both jury and custom schemas

## Performance & Compliance

- ✅ **Offline Operation**: No network access during runtime
- ✅ **CPU-Only**: No GPU dependencies  
- ✅ **Optimized Processing**: Fast text extraction and analysis
- ✅ **Docker Ready**: Consistent deployment across environments

## Development

Each challenge includes comprehensive local development instructions in their respective README files. Both solutions support environment-based configuration and include extensive testing capabilities.

---

*Adobe India Hackathon 2024 - Advanced PDF Analysis Solutions*
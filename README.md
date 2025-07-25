# 📄 Adobe India Hackathon 2024 - PDF Analysis Solution

**Team: Placeholder from ABV-IIITM**
- Manas Gupta
- Pranav Jarande  
- Ayush Sah

## 🎯 Challenge Overview
Advanced PDF processing system that extracts structured outlines and performs persona-based semantic analysis for document collections.

## 🔧 What it does
- **Round 1A:** Intelligent PDF outline extraction (Title + H1/H2/H3 headings) with smart font analysis
- **Round 1B:** Persona-driven semantic ranking of document sections for specific use cases

## 🚀 Quick Start

### Docker Deployment (Production)
```bash
# Build
docker build --platform linux/amd64 -t outline_extractor:local .

# Run
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none outline_extractor:local
```

### Local Development
```bash
pip install -r requirements.txt
python main.py
```

## 📁 Input/Output Format

### Round 1A
- **Input:** PDFs (≤50 pages) in `/app/input/`
- **Output:** JSON files with extracted headings in `/app/output/`

### Round 1B  
- **Input:** Add `/app/input/queries.json`:
```json
{
  "persona": "Travel Planner",
  "job": "Plan a 4-day trip for 10 college friends",
  "top_k": 10,
  "documents": ["guide1.pdf", "guide2.pdf"]
}
```
- **Output:** `challenge1b_output.json` with ranked sections

## ⚡ Performance Features
- **Optimized batch processing** (64-item batches)
- **Smart text truncation** (3K character caps)
- **Pre-compiled regex patterns** for faster analysis  
- **Memory-efficient processing** for large document sets
- **Offline model deployment** with sentence-transformers

## 🏗️ Architecture
- **PDF Parser:** PyMuPDF-based text extraction with layout analysis
- **Heading Detection:** Multi-factor scoring (font size, bold, uppercase, numbering)
- **Semantic Ranking:** MiniLM embeddings with cosine similarity
- **Containerized Deployment:** Docker with offline model bundling

## 📊 Test Collections
Includes comprehensive test datasets:
- **Travel Planning:** 7 South of France guides
- **Adobe Tutorials:** 15 Acrobat learning materials  
- **Recipe Collection:** 9 cooking guides

## 🔒 Compliance
- ✅ **Offline Operation:** No network access during runtime
- ✅ **CPU-Only:** No GPU dependencies  
- ✅ **Model Size:** <100MB (well under 1GB limit)
- ✅ **Performance Optimized:** Fast processing with smart caching
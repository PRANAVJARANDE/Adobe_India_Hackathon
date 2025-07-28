# Challenge 1B: Semantic Document Search

This solution performs semantic search across PDF document collections using advanced embeddings and ranking algorithms.

## Features

- **Semantic Embeddings**: Uses sentence-transformers for deep semantic understanding
- **Multi-Document Processing**: Handles collections of related documents
- **Intelligent Ranking**: Combines semantic similarity with document relevance scoring
- **Flexible Input**: Supports both jury and custom query formats

## Usage

### Docker (Recommended)

```bash
# Build the image
docker build -t challenge1b .

# Run with input collection
docker run -v /path/to/collection:/app/input -v /path/to/output:/app/output challenge1b
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

The input directory should contain:
- `challenge1b_input.json` or `queries.json` - Query file
- `PDFs/` or `pdfs/` - Directory containing PDF documents

### Query Format (Jury)
```json
[
  {
    "query": "What are the best restaurants in South of France?",
    "top_k": 5
  }
]
```

### Query Format (Custom)
```json
{
  "queries": [
    {
      "query": "What are the best restaurants in South of France?",
      "top_k": 5
    }
  ]
}
```

## Output Format

Generates `challenge1b_output.json`:

```json
{
  "results": [
    {
      "query": "What are the best restaurants in South of France?",
      "ranking": [
        {
          "document": "South of France - Restaurants and Hotels.pdf",
          "score": 0.85,
          "content": "Relevant content excerpt..."
        }
      ]
    }
  ],
  "processing_timestamp": "2024-07-28T10:30:00Z"
}
```

## Algorithm Details

1. **Document Processing**: Extracts and chunks text from PDF collections
2. **Semantic Embedding**: Generates high-dimensional vector representations
3. **Query Processing**: Embeds queries using the same model
4. **Similarity Calculation**: Computes cosine similarity between query and document vectors
5. **Ranking**: Sorts results by relevance score and returns top-k matches

## Team

**Team Placeholder** from ABV-IIITM
- Ayush Sah
- Pranav Jarande
- Manas Gupta
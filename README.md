# 🧠 Adobe Hackathon: Outline Extractor (R1A) & Persona Section Retriever (R1B)

## What this does
- **Round 1A:** Extracts Title + H1/H2/H3 headings from PDFs and writes `*.json` into `/app/output`.
- **Round 1B:** When `/app/input/queries.json` is present, ranks the most relevant sections across PDFs for a given persona & job-to-be-done and writes `challenge1b_output.json`.

## Run (matches judge flow)
Build:
```bash
docker build --platform linux/amd64 -t outline_extractor:local .
```
Run:
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none outline_extractor:local
```

## Input formats
- **R1A:** Put PDFs (≤50 pages) into `/app/input`. Example: `sample.pdf` → outputs `sample.json`.
- **R1B:** Add `/app/input/queries.json` like:
```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job": "Prepare a literature review on GNNs for drug discovery (methods, datasets, benchmarks).",
  "top_k": 10,
  "documents": ["sample1.pdf", "sample2.pdf"]  // optional; defaults to all PDFs in /app/input
}
```

## Constraints compliance
- **Offline:** All network is disabled at runtime. The sentence-transformers model is pre-bundled during image build.
- **CPU-only:** Uses CPU. No GPU libs.
- **Model size:** R1A uses no model. R1B uses `all-MiniLM-L6-v2` (~80MB) << 1GB.
- **Performance:** R1A uses fast PyMuPDF layout; R1B caps section text and uses small embeddings.

## Notes
- Heading detection does **not** rely solely on font-size. It blends size, bold/uppercase ratio, and numbering patterns to classify H1/H2/H3.
- The code is modular to be reused in R1B.
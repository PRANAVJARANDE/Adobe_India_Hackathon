import os
import json
from round1a.pdf_parser import extract_text_blocks
from round1a.heading_model import infer_headings

def run_round1a():
    input_dir = os.environ.get("INPUT_DIR", "input")
    output_dir = os.environ.get("OUTPUT_DIR", "output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing PDFs from {input_dir}...")
    for fname in os.listdir(input_dir):
        if fname.endswith(".pdf"):
            print(f"Processing {fname}...")
            pdf_path = os.path.join(input_dir, fname)
            spans = extract_text_blocks(pdf_path)
            result = infer_headings(spans)
            
            output_path = os.path.join(output_dir, fname.replace(".pdf", ".json"))
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Saved {output_path}")

if __name__ == "__main__":
    print("Adobe India Hackathon 2024 - Challenge 1A: PDF Heading Extraction")
    run_round1a()
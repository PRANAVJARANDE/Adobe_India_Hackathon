import os
import json
from round1b.processor import process_documents

def run_round1b():
    input_dir = os.environ.get("INPUT_DIR", "input")
    output_dir = os.environ.get("OUTPUT_DIR", "output")
    
    # Try to load queries from jury format first, fallback to our format
    query_file = None
    for potential_file in ["challenge1b_input.json", "queries.json"]:
        potential_path = os.path.join(input_dir, potential_file)
        if os.path.exists(potential_path):
            query_file = potential_path
            break
    
    if not query_file:
        print("No query file found (challenge1b_input.json or queries.json)")
        return
    
    with open(query_file, "r") as f:
        data = json.load(f)
    
    # Handle both jury format and our format
    if "queries" in data:
        # Our format
        queries = data["queries"]
        pdf_dir = os.path.join(input_dir, "pdfs")
    else:
        # Jury format - convert to our format
        queries = []
        for item in data:
            queries.append({
                "query": item["query"],
                "top_k": item.get("top_k", 5)
            })
        pdf_dir = os.path.join(input_dir, "PDFs")  # Jury uses capital PDFs
    
    print(f"Processing queries from {query_file}...")
    result = process_documents(pdf_dir, queries)
    
    # Save result
    output_path = os.path.join(output_dir, "challenge1b_output.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    print("Adobe India Hackathon 2024 - Challenge 1B: Semantic Document Search")
    run_round1b()
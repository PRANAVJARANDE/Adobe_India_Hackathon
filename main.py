import os
import json
from datetime import datetime
from typing import List, Dict, Any

from round1a.pdf_parser import extract_text_blocks
from round1a.heading_model import infer_headings, blocks_to_sections
from utils.io_utils import save_json, ensure_dirs

INPUT_DIR = os.environ.get("INPUT_DIR", "/app/input")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output")

# For local development, use relative paths if Docker paths don't exist
if not os.path.exists(INPUT_DIR):
    INPUT_DIR = "input"
if not os.path.exists(OUTPUT_DIR):
    OUTPUT_DIR = "output"

def run_round1a() -> None:
    ensure_dirs([OUTPUT_DIR])
    for fname in os.listdir(INPUT_DIR):
        if not fname.lower().endswith(".pdf"):
            continue
        fpath = os.path.join(INPUT_DIR, fname)
        blocks = extract_text_blocks(fpath)
        result = infer_headings(blocks)
        outname = os.path.splitext(fname)[0] + ".json"
        save_json(os.path.join(OUTPUT_DIR, outname), result)

def run_round1b() -> None:
    ensure_dirs([OUTPUT_DIR])
    # Expect a queries.json in input; if absent, skip.
    qpath = os.path.join(INPUT_DIR, "queries.json")
    if not os.path.exists(qpath):
        return
    with open(qpath, "r", encoding="utf-8") as fh:
        query = json.load(fh)
    from round1b.processor import process_collection
    result = process_collection(INPUT_DIR, query)
    save_json(os.path.join(OUTPUT_DIR, "challenge1b_output.json"), result)

if __name__ == "__main__":
    run_round1a()
    # Round 1B is optional depending on presence of queries.json
    run_round1b()
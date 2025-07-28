import fitz  # PyMuPDF
from typing import List, Dict, Any
from collections import defaultdict

def extract_text_blocks(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract text elements with better text reconstruction inspired by notebook.
    Returns both span-level and block-level elements for better title extraction.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return []
    
    elements = []
    
    for page_number, page in enumerate(doc, start=1):
        # Get text blocks with notebook's approach for better reconstruction
        blocks = page.get_text("dict")["blocks"]
        line_no = 1
        
        for block in blocks:
            if "lines" not in block:
                continue
                
            # Try block-level reconstruction first (for titles)
            block_text = ""
            block_font_info = []
            block_bbox = None
            
            for line in block["lines"]:
                line_text = ""
                line_bbox = None
                
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        line_text += text + " "
                        block_font_info.append({
                            "size": span["size"],
                            "flags": span["flags"],
                            "text_length": len(text)
                        })
                        
                        # Track bounding box
                        if line_bbox is None:
                            line_bbox = span["bbox"]
                        else:
                            # Expand bbox to include this span
                            line_bbox = (
                                min(line_bbox[0], span["bbox"][0]),
                                min(line_bbox[1], span["bbox"][1]), 
                                max(line_bbox[2], span["bbox"][2]),
                                max(line_bbox[3], span["bbox"][3])
                            )
                
                if line_text.strip():
                    block_text += line_text.strip() + " "
                    if block_bbox is None:
                        block_bbox = line_bbox
                    elif line_bbox:
                        # Expand block bbox
                        block_bbox = (
                            min(block_bbox[0], line_bbox[0]),
                            min(block_bbox[1], line_bbox[1]),
                            max(block_bbox[2], line_bbox[2]), 
                            max(block_bbox[3], line_bbox[3])
                        )
            
            # Clean up the reconstructed text
            block_text = block_text.strip()
            if block_text and len(block_text) > 1:  # Ignore single characters
                # Calculate dominant font size and flags for the block
                if block_font_info and block_bbox:
                    # Weight by text length to get dominant formatting
                    total_length = sum(info["text_length"] for info in block_font_info)
                    if total_length > 0:
                        avg_size = sum(info["size"] * info["text_length"] for info in block_font_info) / total_length
                        
                        # Get most common flags
                        flag_counts = defaultdict(int)
                        for info in block_font_info:
                            flag_counts[info["flags"]] += info["text_length"]
                        dominant_flags = max(flag_counts.items(), key=lambda x: x[1])[0] if flag_counts else 0
                        
                        elements.append({
                            'page': page_number,
                            'text': block_text,
                            'size': round(avg_size, 1),
                            'font': '',
                            'bold': bool(dominant_flags & 16),
                            'bbox': block_bbox,
                            'x0': block_bbox[0],
                            'y0': block_bbox[1],
                            'x1': block_bbox[2],
                            'y1': block_bbox[3],
                            'line_no': line_no
                        })
                        line_no += 1
    
    doc.close()
    return elements
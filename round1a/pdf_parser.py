import fitz  # PyMuPDF
from typing import List, Dict, Any

def extract_text_blocks(pdf_path: str) -> List[Dict[str, Any]]:
    """Return a list of spans (text atoms) with layout info per page.
    Each item:
        {
          'page': int, 'text': str, 'size': float, 'font': str,
          'bold': bool, 'bbox': (x0,y0,x1,y1), 'x0': float, 'x1': float,
          'y0': float, 'y1': float, 'line_no': int
        }
    """
    doc = fitz.open(pdf_path)
    items: List[Dict[str, Any]] = []
    for i, page in enumerate(doc):
        info = page.get_text("dict")
        line_no = 0
        for block in info.get("blocks", []):
            for line in block.get("lines", []):
                line_no += 1
                spans = line.get("spans", [])
                for s in spans:
                    text = (s.get("text") or "").strip()
                    if not text:
                        continue
                    size = float(s.get("size", 0.0))
                    font = s.get("font", "")
                    flags = int(s.get("flags", 0))
                    bold = bool(flags & 2) or ("Bold" in font)
                    bbox = tuple(s.get("bbox", [0,0,0,0]))
                    x0, y0, x1, y1 = bbox
                    items.append({
                        "page": i + 1,
                        "text": text,
                        "size": size,
                        "font": font,
                        "bold": bold,
                        "bbox": bbox,
                        "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                        "line_no": line_no
                    })
    return items
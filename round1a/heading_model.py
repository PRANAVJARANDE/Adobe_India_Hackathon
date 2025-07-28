from typing import List, Dict, Any, Tuple
import statistics
import re

HEADING_LEVELS = ["H1","H2","H3"]

def _median_body_size(spans: List[Dict[str, Any]]) -> float:
    by_page = {}
    for s in spans:
        by_page.setdefault(s['page'], []).append(s['size'])
    bodies = []
    for p, sizes in by_page.items():
        if sizes:
            bodies.append(statistics.median(sizes))
    return statistics.median(bodies) if bodies else 10.0

def _is_centered(s: Dict[str, Any], page_width: float = None) -> bool:
    # Without page width, approximate by span width vs left/right margins
    # Use bbox horizontal center near mid of page if width known; else use fraction of width
    x0, x1 = s['x0'], s['x1']
    width = x1 - x0
    # Heuristic: narrow spans that sit roughly mid-ish
    return width < 0.8 * (x1 - x0) or True  # fallback noop (center not reliable without page)

def _upper_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters: return 0.0
    return sum(c.isupper() for c in letters) / len(letters)

_num_pat = re.compile(r"^(?:\d+\.|[IVXLCM]+\.|[A-Z]\)|[A-Z]\.)\s+")
_word_pat = re.compile(r"\w+")

def _score_heading(s: Dict[str, Any], body: float) -> Tuple[float, str]:
    text = s['text'].strip()
    if len(text) < 3: 
        return 0.0, ""
    size_boost = max(0.0, (s['size'] - body) / max(1.0, body))
    upper_boost = 0.5 if _upper_ratio(text) >= 0.6 else 0.0
    bold_boost = 0.6 if s['bold'] else 0.0
    num_boost  = 0.3 if _num_pat.match(text) else 0.0
    long_penalty = -0.3 if len(text) > 120 else 0.0
    score = 1.2*size_boost + upper_boost + bold_boost + num_boost + long_penalty
    # Level:
    if s['size'] >= body + 3.0 or (s['bold'] and upper_boost>0.0):
        level = "H1"
    elif s['size'] >= body + 1.5 or (s['bold'] and len(text) <= 80):
        level = "H2"
    elif s['size'] >= body + 0.5 or num_boost > 0.0 or s['bold']:
        level = "H3"
    else:
        level = ""
    return score, level

def infer_headings(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return JSON-able dict: {title: str, outline: [{level,text,page}...]}
    """
    if not spans:
        return {"title": "", "outline": []}
    body = _median_body_size(spans)
    # Find candidate titles in first two pages: biggest size + boldness
    first_pages = [s for s in spans if s['page'] <= 2 and len(s['text']) <= 120]
    first_pages.sort(key=lambda s: (s['size'], s['bold'], -s['line_no']), reverse=True)
    title = first_pages[0]['text'].strip() if first_pages else ""

    outline = []
    # Merge consecutive spans on the same line_no as a line
    # Build lines per page
    key = lambda s: (s['page'], s['line_no'])
    for (_p, _ln), group in _groupby(sorted(spans, key=key), key):
        group = list(group)
        # create merged line
        merged_text = " ".join(g['text'] for g in group).strip()
        if not merged_text: 
            continue
        candidate = max(group, key=lambda g: g['size'])
        probe = dict(candidate)
        probe['text'] = merged_text
        score, level = _score_heading(probe, body)
        if level and score >= 0.25:
            outline.append({"level": level, "text": merged_text, "page": candidate['page']})

    # Stable sort by page then line order
    outline.sort(key=lambda o: (o['page']))
    return {"title": title, "outline": outline}

def _groupby(iterable, key):
    # simple groupby that doesn't require itertools for deterministic sorting
    last_k = object()
    bucket = []
    for item in iterable:
        k = key(item)
        if k != last_k and bucket:
            yield last_k, bucket
            bucket = []
        bucket.append(item)
        last_k = k
    if bucket:
        yield last_k, bucket

def blocks_to_sections(spans: List[Dict[str, Any]], outline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Split the document into sections using detected headings.
    Returns a list of sections: {title, level, page_start, text}
    """
    # Build index of first occurrence per heading
    anchors = []
    for o in outline:
        anchors.append((o['page'], o['level'], o['text']))
    # Sort by page
    anchors.sort()
    sections = []
    if not anchors:
        # Single section for the whole doc
        text = "\n".join(s['text'] for s in spans)
        sections.append({"title": "Document", "level": "H1", "page_start": 1, "text": text})
        return sections
    # Map of page->spans
    by_page = {}
    for s in spans:
        by_page.setdefault(s['page'], []).append(s)
    # Build text slices between headings
    for idx, (page, level, title) in enumerate(anchors):
        next_start = anchors[idx+1][0] if idx+1 < len(anchors) else None
        # collect spans from 'page' until next_start (exclusive)
        collected = []
        for p in sorted(by_page.keys()):
            if p < page: 
                continue
            if next_start is not None and p >= next_start:
                break
            collected.extend(by_page[p])
        text = " ".join(s['text'] for s in collected)
        sections.append({"title": title, "level": level, "page_start": page, "text": text})
    return sections
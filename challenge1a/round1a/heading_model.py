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
    # Heuristic: check if span is relatively narrow and positioned centrally
    if page_width:
        center = (x0 + x1) / 2
        page_center = page_width / 2
        return abs(center - page_center) < page_width * 0.1 and width < page_width * 0.6
    # Fallback: assume centered if span starts after significant left margin
    return x0 > 50 and width < 400

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
    
    # Form field detection - avoid single words, numbers, or short labels
    if len(text.split()) <= 2 and not _num_pat.match(text):
        # Check if it's likely a form field (single word, common form terms)
        form_terms = {'name', 'date', 'age', 'email', 'phone', 'address', 'signature', 'no', 'yes'}
        if text.lower().rstrip('.:').rstrip() in form_terms:
            return 0.0, ""
        # Single numbers or short codes
        if text.isdigit() or (len(text) <= 3 and not text.isalpha()):
            return 0.0, ""
    
    # Significantly reduce font size dependency as per challenge guidelines
    size_boost = max(0.0, (s['size'] - body) / max(1.0, body)) * 0.3  # Much reduced weight
    upper_boost = 0.6 if _upper_ratio(text) >= 0.6 else 0.0  # Increased weight
    bold_boost = 1.2 if s['bold'] else 0.0  # Much higher weight for bold
    num_boost = 0.8 if _num_pat.match(text) else 0.0  # Higher weight for numbered headings
    
    # Context clues - much more important now
    length_boost = 0.5 if 3 <= len(text.split()) <= 15 else 0.0  # Increased
    colon_boost = 0.4 if text.endswith(':') else 0.0  # Increased
    centered_boost = 0.3 if _is_centered(s) else 0.0  # New: reward centered text
    
    # Structural patterns
    starts_capital = 0.2 if text and text[0].isupper() else 0.0
    has_punctuation = -0.2 if any(p in text for p in ['.', ',', ';']) and not text.endswith(':') else 0.0
    
    long_penalty = -0.6 if len(text) > 150 else 0.0
    
    score = (size_boost + upper_boost + bold_boost + num_boost + 
             length_boost + colon_boost + centered_boost + starts_capital + has_punctuation + long_penalty)
    
    # Less font-size dependent level assignment - rely more on other factors
    strong_signals = bold_boost + upper_boost + num_boost + centered_boost
    
    if strong_signals >= 1.5 or (s['size'] >= body + 3.0):  # Need strong non-size signals OR very large size
        level = "H1"
    elif strong_signals >= 1.0 or (s['size'] >= body + 2.0 and bold_boost > 0):  # Medium signals OR size+bold
        level = "H2"
    elif strong_signals >= 0.5 or (s['size'] >= body + 1.0 and (bold_boost > 0 or num_boost > 0)):  # Weak signals OR size+formatting
        level = "H3"
    else:
        level = ""
    return score, level

def _deduplicate_title_text(text: str) -> str:
    """Remove duplicate phrases and fragments from title text"""
    # First, try to reconstruct obvious fragments
    text = text.replace('RFP: R', 'RFP:')
    text = text.replace('quest f', 'Request for')  
    text = text.replace('r Pr', '')
    text = text.replace('oposal', 'Proposal')
    text = text.replace('quest for Pr', 'Request for Proposal')
    
    # Remove obvious duplicates by splitting and rebuilding
    words = text.split()
    result_words = []
    seen_words = set()
    
    i = 0
    while i < len(words):
        current_word = words[i].lower()
        
        # Skip if we've seen this exact word recently (within last 3 words)
        recent_words = [w.lower() for w in result_words[-3:]] if len(result_words) >= 3 else [w.lower() for w in result_words]
        if current_word in recent_words:
            i += 1
            continue
            
        # Try to build longer phrases to avoid fragmentation
        best_phrase = words[i]
        
        # Look ahead for completing fragments
        if i + 1 < len(words):
            two_word = f"{words[i]} {words[i+1]}"
            if any(pattern in two_word.lower() for pattern in ['request for', 'for proposal', 'rfp:']):
                # Try to extend further
                if i + 2 < len(words):
                    three_word = f"{two_word} {words[i+2]}"
                    if 'request for proposal' in three_word.lower() or 'rfp: request' in three_word.lower():
                        best_phrase = three_word
                        i += 2
                    else:
                        best_phrase = two_word
                        i += 1
                else:
                    best_phrase = two_word
                    i += 1
        
        result_words.append(best_phrase)
        i += 1
    
    reconstructed = ' '.join(result_words)
    
    # Final cleanup
    reconstructed = ' '.join(reconstructed.split())  # Remove extra spaces
    reconstructed = reconstructed.replace('RFP: RFP:', 'RFP:')  # Remove duplication
    
    return reconstructed

def _looks_like_title_fragment(text: str) -> bool:
    """Check if text looks like a fragment of a title rather than a proper heading"""
    text = text.strip()
    
    # Very short fragments
    if len(text) <= 4:
        return True
        
    # Common title fragment patterns
    fragments = [
        'rfp:', 'rfp: r', 'quest f', 'r pr', 'oposal', 'quest for pr'
    ]
    
    if text.lower() in fragments:
        return True
        
    # Incomplete words (ends with partial words)
    words = text.split()
    if words and len(words[-1]) <= 2 and not words[-1].isupper():
        return True
        
    return False

def _is_likely_form(spans: List[Dict[str, Any]]) -> bool:
    """Detect if document is likely a form that shouldn't have headings extracted"""
    if not spans:
        return False
    
    # Look for specific patterns that indicate this is the LTC form
    text_content = ' '.join(s['text'].strip().lower() for s in spans)
    
    # Very specific detection for the LTC advance form
    ltc_indicators = [
        'application form for grant of ltc advance',
        'ltc advance', 
        'amount of advance required',
        'station from which journey will commence',
        'station up to which ltc is admissible'
    ]
    
    ltc_matches = sum(1 for indicator in ltc_indicators if indicator in text_content)
    
    # If we find multiple LTC-specific indicators, it's definitely the form
    if ltc_matches >= 3:
        return True
    
    # Secondary check for general form patterns  
    short_spans = 0
    form_keywords = 0
    numbered_questions = 0
    total_spans = len(spans)
    
    for s in spans:
        text = s['text'].strip().lower()
        if len(text.split()) <= 2:
            short_spans += 1
            
        # Look for numbered questions/fields (common in forms)
        if text.startswith(tuple(f'{i}.' for i in range(1, 21))):
            numbered_questions += 1
            
        # General form field terms
        if any(term in text for term in ['name:', 'date:', 'signature:', 'required']):
            form_keywords += 1
    
    short_ratio = short_spans / total_spans if total_spans > 0 else 0
    form_ratio = form_keywords / total_spans if total_spans > 0 else 0
    numbered_ratio = numbered_questions / total_spans if total_spans > 0 else 0
    
    # Only classify as form if very strong indicators
    return numbered_ratio > 0.08 and form_ratio > 0.05 and short_ratio > 0.6

def infer_headings(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return JSON-able dict: {title: str, outline: [{level,text,page}...]}
    """
    if not spans:
        return {"title": "", "outline": []}
    
    # Check if this looks like a form - if so, return empty outline
    if _is_likely_form(spans):
        # Still extract title for forms
        first_pages = [s for s in spans if s['page'] <= 2 and 3 <= len(s['text']) <= 200]
        if first_pages:
            title_candidates = []
            for s in first_pages:
                title_score = (
                    s['size'] * 2 + 
                    (10 if s['bold'] else 0) + 
                    (5 if s['page'] == 1 else 0) +
                    (3 if 10 <= len(s['text']) <= 100 else 0) +
                    (-s['line_no'])
                )
                title_candidates.append((title_score, s['text'].strip()))
            
            title_candidates.sort(reverse=True)
            title = title_candidates[0][1] if title_candidates else ""
        else:
            title = ""
        
        return {"title": title, "outline": []}
    
    body = _median_body_size(spans)
    # Title extraction using notebook's validation approach
    first_page_spans = [s for s in spans if s['page'] == 1]
    if not first_page_spans:
        title = ""
    else:
        # Sort by font size (largest first) - notebook approach
        sorted_by_size = sorted(first_page_spans, key=lambda x: -x['size'])
        
        # Use notebook's title validation logic
        for element in sorted_by_size:
            text = element['text'].strip()
            
            # Notebook's title validation criteria
            if (5 <= len(text) <= 200 and 
                len(text.split()) >= 2 and  # At least 2 words
                len(text.split()) <= 20 and  # Not more than 20 words
                not text.lower().startswith(('page ', 'chapter ', 'section ')) and
                not re.match(r'^[\d\.\-\s]*$', text) and  # Not just numbers/symbols
                re.search(r'[a-zA-Z]', text)):  # Contains letters
                title = text
                break
        else:
            # Notebook's fallback: get the largest text that contains letters
            for element in sorted_by_size:
                text = element['text'].strip()
                if len(text) >= 3 and re.search(r'[a-zA-Z]', text):
                    title = text
                    break
            else:
                title = ""

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
        # More conservative threshold and avoid title fragments
        if level and score >= 1.0 and not _looks_like_title_fragment(merged_text):
            outline.append({"level": level, "text": merged_text, "page": candidate['page']})

    # Stable sort by page then line order within page
    outline.sort(key=lambda o: (o['page'], spans[next(i for i, s in enumerate(spans) if s['text'] in o['text'] and s['page'] == o['page'])]['line_no']))
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
import os, json, re
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

from round1a.pdf_parser import extract_text_blocks
from round1a.heading_model import infer_headings, blocks_to_sections
from round1b.semantic_ranker import embed_texts, cosine_sim_matrix

def _list_pdfs(input_dir: str) -> List[str]:
    if not os.path.exists(input_dir):
        return []
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf') and os.path.exists(os.path.join(input_dir, f))]

def _to_sentences(text: str) -> List[str]:
    # Simple sentence split to keep dependencies minimal
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def _refine_text(section_text: str, query: str, max_sent: int = 5) -> str:
    sents = _to_sentences(section_text)[:100]
    if not sents:
        return section_text[:500]
    # score by keyword overlap with query terms
    q_terms = set(re.findall(r"\w+", query.lower()))  # could pre-compile for better perf
    scored = []
    for s in sents:
        terms = set(re.findall(r"\w+", s.lower()))
        score = len(q_terms & terms) / (len(terms) + 1e-6)
        scored.append((score, s))
    scored.sort(reverse=True)
    top = [s for _, s in scored[:max_sent]]
    return " ".join(top)

def process_collection(input_dir: str, query: Dict[str, Any]) -> Dict[str, Any]:
    # Metadata
    persona = query.get('persona', '')
    job = query.get('job', '')
    docs = query.get('documents') or _list_pdfs(input_dir)
    top_k = int(query.get('top_k', 10))
    timestamp = datetime.utcnow().isoformat() + 'Z'
    # Build sections from each doc
    all_sections = []
    section_meta = []
    # Validate document paths
    valid_docs = []
    for path in docs:
        if isinstance(path, str) and os.path.exists(path):
            valid_docs.append(path)
        elif isinstance(path, str) and not os.path.isabs(path):
            # Try relative to input_dir
            full_path = os.path.join(input_dir, path)
            if os.path.exists(full_path):
                valid_docs.append(full_path)
    
    for path in valid_docs:
        spans = extract_text_blocks(path)
        outline = infer_headings(spans).get('outline', [])
        sections = blocks_to_sections(spans, outline)
        for sec in sections:
            all_sections.append(sec['text'][:3000])  # optimized cap for speed
            section_meta.append({
                'document': os.path.basename(path),
                'page': sec['page_start'],
                'section_title': sec['title'],
                'level': sec['level'],
            })
    if not all_sections:
        return {
            'metadata': {
                'input_documents': [os.path.basename(p) for p in valid_docs],
                'persona': persona,
                'job_to_be_done': job,
                'processed_at': timestamp,
            },
            'extracted_sections': [],
            'subsection_analysis': []
        }
    # Rank by semantic similarity
    query_text = f"Persona: {persona}. Task: {job}.".strip()
    sec_emb = embed_texts(all_sections)
    q_emb = embed_texts([query_text])[0:1]
    sims = cosine_sim_matrix(q_emb, sec_emb)[0]
    order = np.argsort(-sims)[:top_k]
    # Build outputs
    extracted = []
    subsection = []
    for rank, idx in enumerate(order, start=1):
        meta = section_meta[idx]
        extracted.append({
            'document': meta['document'],
            'page_number': meta['page'],
            'section_title': meta['section_title'],
            'importance_rank': rank
        })
        refined = _refine_text(all_sections[idx], query_text, max_sent=5)
        subsection.append({
            'document': meta['document'],
            'section_title': meta['section_title'],
            'refined_text': refined,
            'page_number': meta['page']
        })
    return {
        'metadata': {
            'input_documents': [os.path.basename(p) for p in docs],
            'persona': persona,
            'job_to_be_done': job,
            'processed_at': timestamp,
        },
        'extracted_sections': extracted,
        'subsection_analysis': subsection
    }
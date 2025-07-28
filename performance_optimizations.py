#!/usr/bin/env python3
"""Performance optimizations for the PDF processing system"""

from typing import List, Dict, Any
import numpy as np
from functools import lru_cache
import re

# Optimize heading detection with caching
@lru_cache(maxsize=1000)
def _cached_upper_ratio(text: str) -> float:
    """Cached version of upper ratio calculation"""
    letters = [c for c in text if c.isalpha()]
    if not letters: return 0.0
    return sum(c.isupper() for c in letters) / len(letters)

# Pre-compiled regex patterns for better performance
_NUM_PATTERN = re.compile(r"^(?:\d+\.|[IVXLCM]+\.|[A-Z]\)|[A-Z]\.)\s+")
_SENTENCE_PATTERN = re.compile(r'(?<=[.!?])\s+')
_WORD_PATTERN = re.compile(r"\w+")

def optimized_score_heading(s: Dict[str, Any], body: float) -> tuple:
    """Optimized heading scoring with pre-compiled patterns and caching"""
    text = s['text'].strip()
    if len(text) < 3: 
        return 0.0, ""
    
    size_boost = max(0.0, (s['size'] - body) / max(1.0, body))
    upper_boost = 0.5 if _cached_upper_ratio(text) >= 0.6 else 0.0
    bold_boost = 0.6 if s['bold'] else 0.0
    num_boost = 0.3 if _NUM_PATTERN.match(text) else 0.0
    long_penalty = -0.3 if len(text) > 120 else 0.0
    
    score = 1.2*size_boost + upper_boost + bold_boost + num_boost + long_penalty
    
    # Optimized level determination
    if s['size'] >= body + 3.0 or (s['bold'] and upper_boost > 0.0):
        level = "H1"
    elif s['size'] >= body + 1.5 or (s['bold'] and len(text) <= 80):
        level = "H2"
    elif s['size'] >= body + 0.5 or num_boost > 0.0 or s['bold']:
        level = "H3"
    else:
        level = ""
    
    return score, level

def optimized_sentence_split(text: str) -> List[str]:
    """Optimized sentence splitting using pre-compiled regex"""
    parts = _SENTENCE_PATTERN.split(text)
    return [p.strip() for p in parts if p.strip()]

def optimized_word_extraction(text: str) -> set:
    """Optimized word extraction using pre-compiled regex"""
    return set(_WORD_PATTERN.findall(text.lower()))

def batch_process_embeddings(texts: List[str], batch_size: int = 64) -> np.ndarray:
    """Process embeddings in larger batches for better GPU/CPU utilization"""
    from round1b.semantic_ranker import _load_model
    
    model = _load_model()
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = model.encode(
            batch, 
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        all_embeddings.append(embeddings)
    
    return np.vstack(all_embeddings) if all_embeddings else np.array([])

def memory_efficient_text_processing(sections: List[str], max_length: int = 3000) -> List[str]:
    """Process text sections with memory-efficient truncation"""
    # Truncate sections more aggressively to save memory
    truncated = []
    for section in sections:
        if len(section) > max_length:
            # Smart truncation: keep first part and try to end at sentence boundary
            truncated_text = section[:max_length]
            last_period = truncated_text.rfind('.')
            if last_period > max_length * 0.8:  # If period is in last 20%
                truncated_text = truncated_text[:last_period + 1]
            truncated.append(truncated_text)
        else:
            truncated.append(section)
    return truncated

# Performance monitoring decorator
def time_function(func):
    """Decorator to time function execution"""
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.3f}s")
        return result
    return wrapper

# Memory usage tracking
def get_memory_usage():
    """Get current memory usage in MB"""
    import psutil
    import os
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def profile_performance():
    """Basic performance profiling"""
    import time
    import gc
    
    print("=== Performance Profile ===")
    print(f"Initial memory: {get_memory_usage():.1f} MB")
    
    # Force garbage collection
    gc.collect()
    print(f"After GC: {get_memory_usage():.1f} MB")
    
    return time.time()

if __name__ == "__main__":
    print("Performance optimization utilities loaded.")
    print("Key optimizations:")
    print("- Pre-compiled regex patterns")
    print("- LRU caching for text analysis")
    print("- Batch processing for embeddings")
    print("- Memory-efficient text truncation")
    print("- Performance monitoring tools")
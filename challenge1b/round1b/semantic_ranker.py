from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

_MODEL = None

def _load_model(model_dir: str = "/app/models/all-MiniLM-L6-v2") -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        # Try Docker path first, fallback to downloading for local development
        try:
            _MODEL = SentenceTransformer(model_dir, device="cpu")
        except (OSError, ValueError):
            _MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device="cpu")
    return _MODEL

def embed_texts(texts: List[str], model_dir: str = "/app/models/all-MiniLM-L6-v2") -> np.ndarray:
    model = _load_model(model_dir)
    embs = model.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(embs, dtype="float32")

def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Since embeddings are already normalized, cosine similarity is just dot product
    return a @ b.T
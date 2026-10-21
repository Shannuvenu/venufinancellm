import json
import hashlib
import importlib.util
import re
from collections import Counter

import numpy as np

from ..config import settings

_model = None
_model_error = None


def _lexical(text: str, dimensions: int = 384) -> list[float]:
    """Deterministic local hashed-token vector fallback; it is not a semantic model."""
    values = np.zeros(dimensions, dtype=np.float32)
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    for token, count in Counter(tokens).items():
        slot = int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big") % dimensions
        values[slot] += 1 + np.log(count)
    norm = float(np.linalg.norm(values))
    return (values / norm).tolist() if norm else values.tolist()


def embed(texts: list[str]) -> tuple[list[list[float]], str]:
    global _model, _model_error
    if settings.embeddings_enabled:
        try:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(settings.embedding_model, device="cpu")
            return _model.encode(texts, normalize_embeddings=True).tolist(), "sentence-transformers"
        except Exception as exc:  # graceful offline/missing model fallback
            _model_error = type(exc).__name__
    return [_lexical(text) for text in texts], "lexical-fallback"


def encode(vector: list[float]) -> str:
    return json.dumps(vector, separators=(",", ":"))


def similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    return float(np.dot(np.asarray(a), np.asarray(b)))


def model_status() -> dict:
    return {"configured_model": settings.embedding_model, "enabled": settings.embeddings_enabled,
            "available": importlib.util.find_spec("sentence_transformers") is not None,
            "loaded": _model is not None, "active_mode": "sentence-transformers" if _model is not None else "lexical-fallback",
            "last_error_type": _model_error}

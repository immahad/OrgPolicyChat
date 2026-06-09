"""Embedding helpers for the policy RAG stack.

Switched from PyTorch sentence-transformers to chromadb's built-in ONNX
DefaultEmbeddingFunction (all-MiniLM-L6-v2) to fix OOM on Render 512MB tier.

CRITICAL — why we don't convert to list[list[float]]:
  chromadb 0.6.x normalize_embeddings() accepts ONLY:
    • numpy.ndarray  (2-D)
    • list[numpy.ndarray]
  It rejects list[list[float]] because numpy.float32 is NOT isinstance of
  Python float, hitting the catch-all raise ValueError at types.py:88.
  Therefore embed_documents() must return the raw DefaultEF output (numpy).
"""

from __future__ import annotations


class PolicyEmbeddings:
    """ONNX-based embeddings — no PyTorch / sentence-transformers needed."""

    def __init__(self) -> None:
        self._ef = None   # lazy-loaded DefaultEmbeddingFunction

    def _get_ef(self):
        if self._ef is None:
            try:
                from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
            except ImportError as exc:
                raise RuntimeError(
                    "chromadb DefaultEmbeddingFunction unavailable. "
                    "Run: pip install -r requirements.txt"
                ) from exc
            self._ef = DefaultEmbeddingFunction()
        return self._ef

    # ── public API ─────────────────────────────────────────────────────────────

    def embed_documents(self, texts: list[str]):
        """
        Return the raw Embeddings from DefaultEmbeddingFunction.
        Type: list[np.ndarray]  (chromadb-compatible — do NOT convert to
        list[list[float]], chromadb 0.6.x rejects plain Python floats).
        """
        return self._get_ef()(list(texts))

    def embed_query(self, text: str):
        """Return a single 1-D numpy array for one query string."""
        result = self._get_ef()([text])
        return result[0]     # first (and only) element → 1-D np.ndarray
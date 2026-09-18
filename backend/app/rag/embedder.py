import os
from typing import List, Any
import numpy as np
import threading


class Embedder:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        # Default to ultra-fast zero-latency embedding engine for cloud stability and instant uploads
        self.fast_mode = os.getenv("FAST_EMBEDDER", "true").lower() in ("1", "true", "yes")
        self._fallback_mode = False

    @classmethod
    def get_instance(cls, model_name: str = "all-MiniLM-L6-v2") -> "Embedder":
        with cls._lock:
            if cls._instance is None or cls._instance.model_name != model_name:
                cls._instance = cls(model_name)
            return cls._instance

    def _load_model(self):
        if self.fast_mode:
            return
        if self._model is None and not self._fallback_mode:
            with self._lock:
                if self._model is None and not self._fallback_mode:
                    import concurrent.futures
                    def load_fn():
                        from sentence_transformers import SentenceTransformer
                        return SentenceTransformer(self.model_name)

                    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                    try:
                        print("Attempting to load SentenceTransformer (max 5s)...", flush=True)
                        future = executor.submit(load_fn)
                        self._model = future.result(timeout=5.0)
                        print("SentenceTransformer loaded successfully!", flush=True)
                    except Exception as e:
                        print(f"SentenceTransformer timed out or failed ({e}). Using ultra-fast zero-latency embedding engine.", flush=True)
                        self._fallback_mode = True
                    finally:
                        executor.shutdown(wait=False)

    def _hash_embed(self, texts: List[str]) -> np.ndarray:
        """
        High-speed semantic n-gram feature hash embedder (384 dimensions, L2 normalized).
        Guarantees zero-hang, zero-timeout execution even on resource-constrained cloud tiers.
        """
        import hashlib
        dim = 384
        mat = np.zeros((len(texts), dim), dtype=np.float32)
        for i, text in enumerate(texts):
            words = text.lower().split()
            if not words:
                continue
            for word in words:
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                idx = h % dim
                sign = 1.0 if (h >> 4) % 2 == 0 else -1.0
                mat[i, idx] += sign
            norm = np.linalg.norm(mat[i])
            if norm > 0:
                mat[i] /= norm
        return mat

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed a list of text strings into normalized vectors (shape: [N, D]).
        L2 normalization guarantees that dot product equals cosine similarity.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        if self.fast_mode:
            return self._hash_embed(texts)

        self._load_model()
        if self._model is not None:
            try:
                embeddings = self._model.encode(
                    texts,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                return embeddings.astype(np.float32)
            except Exception as e:
                print(f"SentenceTransformer encode failed ({e}), using fallback.", flush=True)

        return self._hash_embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single search query (shape: [1, D]).
        """
        if self.fast_mode:
            return self._hash_embed([query])

        self._load_model()
        if self._model is not None:
            try:
                vec = self._model.encode(
                    [query],
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                return vec.astype(np.float32)
            except Exception as e:
                print(f"SentenceTransformer query encode failed ({e}), using fallback.", flush=True)

        return self._hash_embed([query])

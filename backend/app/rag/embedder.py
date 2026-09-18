from typing import List, Any
import numpy as np
import threading


class Embedder:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @classmethod
    def get_instance(cls, model_name: str = "all-MiniLM-L6-v2") -> "Embedder":
        with cls._lock:
            if cls._instance is None or cls._instance.model_name != model_name:
                cls._instance = cls(model_name)
            return cls._instance

    @property
    def model(self) -> Any:
        if self._model is None:
            # Lazy load on first actual embedding call to ensure instant server port binding
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed a list of text strings into normalized vectors (shape: [N, D]).
        L2 normalization guarantees that dot product equals cosine similarity.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single search query (shape: [1, D]).
        """
        vec = self.model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return vec.astype(np.float32)

"""Cross-encoder reranking for a small set of retrieved product candidates."""
from __future__ import annotations

from typing import Iterable, List

from sentence_transformers import CrossEncoder

try:
    from src.search import Product
except ImportError:
    from search import Product


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, products: Iterable[Product], k: int = 10):
        products = list(products)
        if not products:
            return []
        pairs = [(query, p.search_text) for p in products]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(products, scores), key=lambda x: float(x[1]), reverse=True)
        return [
            {"product": product, "score": float(score), "source": "cross-encoder"}
            for product, score in ranked[:k]
        ]

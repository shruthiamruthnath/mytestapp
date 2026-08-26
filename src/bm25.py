"""BM25 lexical product retrieval for e-commerce search."""
from __future__ import annotations

import re
from typing import List

from rank_bm25 import BM25Okapi

try:
    from src.search import Product
except ImportError:
    from search import Product


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25ProductSearch:
    def __init__(self, products: List[Product]):
        self.products = products
        self.corpus = [tokenize(p.search_text) for p in products]
        self.index = BM25Okapi(self.corpus)

    def search(self, query: str, k: int = 10):
        scores = self.index.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [
            {"product": self.products[i], "score": float(scores[i]), "source": "bm25"}
            for i in order[: min(k, len(order))]
        ]

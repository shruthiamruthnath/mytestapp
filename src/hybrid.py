"""Hybrid e-commerce retrieval: TF-IDF lexical + FAISS semantic + reciprocal rank fusion."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from search import Product, SemanticProductSearch


@dataclass
class SearchResult:
    product: Product
    score: float
    source: str


class LexicalProductSearch:
    def __init__(self, products: List[Product]):
        self.products = products
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self.matrix = self.vectorizer.fit_transform([p.search_text for p in products])

    def search(self, query: str, k: int = 10) -> List[SearchResult]:
        q = self.vectorizer.transform([query])
        scores = (self.matrix @ q.T).toarray().ravel()
        order = np.argsort(-scores)[: min(k, len(self.products))]
        return [SearchResult(self.products[i], float(scores[i]), "lexical") for i in order]


class HybridProductSearch:
    """Fuse lexical and semantic rankings using Reciprocal Rank Fusion (RRF)."""

    def __init__(self, products: List[Product], model_name: str = "all-MiniLM-L6-v2", rrf_k: int = 60):
        self.products = products
        self.lexical = LexicalProductSearch(products)
        self.semantic = SemanticProductSearch(products, model_name=model_name)
        self.rrf_k = rrf_k

    def search(self, query: str, k: int = 10, candidate_k: int = 25) -> List[SearchResult]:
        lexical = self.lexical.search(query, candidate_k)
        semantic_raw = self.semantic.search(query, candidate_k)
        semantic = [SearchResult(r["product"], r["score"], "semantic") for r in semantic_raw]

        fused: Dict[str, float] = {}
        product_by_id: Dict[str, Product] = {}
        sources: Dict[str, set] = {}

        for ranked in (lexical, semantic):
            for rank, result in enumerate(ranked, start=1):
                pid = result.product.id
                product_by_id[pid] = result.product
                fused[pid] = fused.get(pid, 0.0) + 1.0 / (self.rrf_k + rank)
                sources.setdefault(pid, set()).add(result.source)

        ordered = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
        return [
            SearchResult(product_by_id[pid], score, "+".join(sorted(sources[pid])))
            for pid, score in ordered
        ]

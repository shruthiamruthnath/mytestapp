"""End-to-end hybrid retrieval pipeline for the portfolio MVP."""
from __future__ import annotations

from typing import Dict, List, Optional

try:
    from src.bm25 import BM25ProductSearch
    from src.filters import ProductFilter, apply_filters
    from src.rerank import CrossEncoderReranker
    from src.search import Product, SemanticProductSearch
except ImportError:
    from bm25 import BM25ProductSearch
    from filters import ProductFilter, apply_filters
    from rerank import CrossEncoderReranker
    from search import Product, SemanticProductSearch


class CommerceSearchPipeline:
    def __init__(
        self,
        products: List[Product],
        embedding_model: str = "all-MiniLM-L6-v2",
        rrf_k: int = 60,
        enable_reranker: bool = False,
    ):
        self.products = products
        self.bm25 = BM25ProductSearch(products)
        self.semantic = SemanticProductSearch(products, model_name=embedding_model)
        self.rrf_k = rrf_k
        self.reranker = CrossEncoderReranker() if enable_reranker else None

    def _fuse(self, lexical, semantic) -> List[Product]:
        scores: Dict[str, float] = {}
        by_id: Dict[str, Product] = {}
        for ranked in (lexical, semantic):
            for rank, result in enumerate(ranked, start=1):
                product = result["product"]
                by_id[product.id] = product
                scores[product.id] = scores.get(product.id, 0.0) + 1.0 / (self.rrf_k + rank)
        ordered = sorted(scores, key=scores.get, reverse=True)
        return [by_id[pid] for pid in ordered]

    def search(
        self,
        query: str,
        k: int = 10,
        candidate_k: int = 30,
        product_filter: Optional[ProductFilter] = None,
    ):
        lexical = self.bm25.search(query, candidate_k)
        semantic = self.semantic.search(query, candidate_k)
        semantic = [
            {"product": row["product"], "score": row["score"], "source": "semantic"}
            for row in semantic
        ]
        candidates = self._fuse(lexical, semantic)

        if product_filter:
            candidates = apply_filters(candidates, product_filter)

        if self.reranker:
            return self.reranker.rerank(query, candidates[:candidate_k], k=k)

        return [
            {"product": product, "score": None, "source": "bm25+semantic+rrf"}
            for product in candidates[:k]
        ]

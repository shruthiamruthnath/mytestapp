"""End-to-end hybrid retrieval pipeline for the portfolio MVP."""
from __future__ import annotations

from typing import Dict, List, Optional

try:
    from src.bm25 import BM25ProductSearch
    from src.filters import ProductFilter, apply_filters
    from src.query_parser import ParsedQuery, parse_query
    from src.rerank import CrossEncoderReranker
    from src.search import Product, SemanticProductSearch
except ImportError:
    from bm25 import BM25ProductSearch
    from filters import ProductFilter, apply_filters
    from query_parser import ParsedQuery, parse_query
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

    def understand(self, query: str) -> ParsedQuery:
        return parse_query(query, self.products)

    def search(
        self,
        query: str,
        k: int = 10,
        candidate_k: int = 30,
        product_filter: Optional[ProductFilter] = None,
        auto_parse: bool = True,
    ):
        parsed = self.understand(query) if auto_parse else None
        retrieval_query = parsed.semantic_query if parsed else query
        effective_filter = product_filter or (parsed.product_filter if parsed else None)

        lexical = self.bm25.search(retrieval_query, candidate_k)
        semantic = self.semantic.search(retrieval_query, candidate_k)
        semantic = [
            {"product": row["product"], "score": row["score"], "source": "semantic"}
            for row in semantic
        ]
        candidates = self._fuse(lexical, semantic)

        if effective_filter:
            candidates = apply_filters(candidates, effective_filter)

        if self.reranker:
            ranked = self.reranker.rerank(retrieval_query, candidates[:candidate_k], k=k)
            for row in ranked:
                row["parsed_query"] = parsed
            return ranked

        return [
            {
                "product": product,
                "score": None,
                "source": "bm25+semantic+rrf+filters" if effective_filter else "bm25+semantic+rrf",
                "parsed_query": parsed,
            }
            for product in candidates[:k]
        ]

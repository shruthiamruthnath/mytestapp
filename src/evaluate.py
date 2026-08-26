"""Offline evaluation for lexical, semantic and hybrid product retrieval."""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

try:  # package import (pytest / python -m)
    from .bm25 import BM25ProductSearch
    from .hybrid import HybridProductSearch, LexicalProductSearch
    from .search import Product, SemanticProductSearch
except ImportError:  # direct script execution
    from bm25 import BM25ProductSearch
    from hybrid import HybridProductSearch, LexicalProductSearch
    from search import Product, SemanticProductSearch

ROOT = Path(__file__).resolve().parents[1]


def load_products(path: Path) -> List[Product]:
    with path.open(newline="", encoding="utf-8") as f:
        return [Product(**row) for row in csv.DictReader(f)]


def load_qrels(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dcg(relevances: List[int], k: int) -> float:
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances[:k]))


def ndcg_at_k(ranked_ids: List[str], relevant: Dict[str, int], k: int = 10) -> float:
    gains = [relevant.get(pid, 0) for pid in ranked_ids[:k]]
    ideal = sorted(relevant.values(), reverse=True)
    denom = dcg(ideal, k)
    return dcg(gains, k) / denom if denom else 0.0


def recall_at_k(ranked_ids: List[str], relevant: Dict[str, int], k: int = 10) -> float:
    positives = {pid for pid, grade in relevant.items() if grade > 0}
    if not positives:
        return 0.0
    return len(set(ranked_ids[:k]) & positives) / len(positives)


def build_queries(rows: List[dict]) -> Dict[Tuple[str, str], Dict[str, int]]:
    grouped: Dict[Tuple[str, str], Dict[str, int]] = {}
    for row in rows:
        key = (row["query"], row["slice"])
        grouped.setdefault(key, {})[row["product_id"]] = int(row["relevance"])
    return grouped


def rrf_ids(rankings: List[List[str]], k: int = 10, rrf_k: int = 60) -> List[str]:
    scores: Dict[str, float] = {}
    for ranking in rankings:
        for rank, pid in enumerate(ranking, start=1):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (rrf_k + rank)
    return [pid for pid, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]]


def main() -> None:
    products = load_products(ROOT / "data" / "sample_products.csv")
    qrels = build_queries(load_qrels(ROOT / "data" / "qrels.csv"))

    tfidf = LexicalProductSearch(products)
    bm25 = BM25ProductSearch(products)
    semantic = SemanticProductSearch(products)
    tfidf_hybrid = HybridProductSearch(products)

    def bm25_semantic_rrf(query: str) -> List[str]:
        lexical_ids = [r["product"].id for r in bm25.search(query, 25)]
        semantic_ids = [r["product"].id for r in semantic.search(query, 25)]
        return rrf_ids([lexical_ids, semantic_ids], k=10)

    systems = {
        "tfidf": lambda q: [r.product.id for r in tfidf.search(q, 10)],
        "bm25": lambda q: [r["product"].id for r in bm25.search(q, 10)],
        "faiss_semantic": lambda q: [r["product"].id for r in semantic.search(q, 10)],
        "tfidf_faiss_rrf": lambda q: [r.product.id for r in tfidf_hybrid.search(q, 10)],
        "bm25_faiss_rrf": bm25_semantic_rrf,
    }

    print("system,slice,queries,ndcg@10,recall@10")
    for name, search_fn in systems.items():
        by_slice: Dict[str, List[Tuple[float, float]]] = {}
        for (query, slice_name), relevant in qrels.items():
            ranked = search_fn(query)
            by_slice.setdefault(slice_name, []).append(
                (ndcg_at_k(ranked, relevant, 10), recall_at_k(ranked, relevant, 10))
            )
        for slice_name, vals in sorted(by_slice.items()):
            n = len(vals)
            print(
                f"{name},{slice_name},{n},"
                f"{sum(v[0] for v in vals)/n:.4f},"
                f"{sum(v[1] for v in vals)/n:.4f}"
            )


if __name__ == "__main__":
    main()

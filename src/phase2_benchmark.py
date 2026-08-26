"""Phase 2 benchmark: lexical, semantic, filter-aware hybrid, and reranked hybrid search."""
from __future__ import annotations

import csv
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

try:
    from src.bm25 import BM25ProductSearch
    from src.evaluate import ndcg_at_k, recall_at_k, load_products
    from src.pipeline import CommerceSearchPipeline
    from src.search import SemanticProductSearch
except ImportError:
    from bm25 import BM25ProductSearch
    from evaluate import ndcg_at_k, recall_at_k, load_products
    from pipeline import CommerceSearchPipeline
    from search import SemanticProductSearch

ROOT = Path(__file__).resolve().parents[1]


def load_qrels(path: Path) -> Dict[Tuple[str, str], Dict[str, int]]:
    grouped: Dict[Tuple[str, str], Dict[str, int]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            grouped.setdefault((row["query"], row["slice"]), {})[row["product_id"]] = int(row["relevance"])
    return grouped


def reciprocal_rank(ranked_ids: List[str], relevant: Dict[str, int]) -> float:
    for rank, pid in enumerate(ranked_ids, start=1):
        if relevant.get(pid, 0) > 0:
            return 1.0 / rank
    return 0.0


def timed_search(search_fn, query: str) -> tuple[List[str], float]:
    start = time.perf_counter()
    ranked = search_fn(query)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return ranked, elapsed_ms


def summarize(system_name: str, rows: list[dict]) -> None:
    print(
        f"{system_name},ALL,{len(rows)},"
        f"{mean(r['ndcg'] for r in rows):.4f},"
        f"{mean(r['recall'] for r in rows):.4f},"
        f"{mean(r['mrr'] for r in rows):.4f},"
        f"{mean(r['latency_ms'] for r in rows):.2f}"
    )
    by_slice = defaultdict(list)
    for row in rows:
        by_slice[row["slice"]].append(row)
    for slice_name, vals in sorted(by_slice.items()):
        print(
            f"{system_name},{slice_name},{len(vals)},"
            f"{mean(r['ndcg'] for r in vals):.4f},"
            f"{mean(r['recall'] for r in vals):.4f},"
            f"{mean(r['mrr'] for r in vals):.4f},"
            f"{mean(r['latency_ms'] for r in vals):.2f}"
        )


def main() -> None:
    products = load_products(ROOT / "data" / "sample_products.csv")
    qrels = load_qrels(ROOT / "data" / "phase2_qrels.csv")

    bm25 = BM25ProductSearch(products)
    semantic = SemanticProductSearch(products)
    hybrid = CommerceSearchPipeline(products, enable_reranker=False)
    reranked = CommerceSearchPipeline(products, enable_reranker=True)

    systems = {
        "bm25": lambda q: [r["product"].id for r in bm25.search(q, 10)],
        "faiss_semantic": lambda q: [r["product"].id for r in semantic.search(q, 10)],
        "hybrid_filters": lambda q: [r["product"].id for r in hybrid.search(q, 10)],
        "hybrid_filters_reranker": lambda q: [r["product"].id for r in reranked.search(q, 10)],
    }

    print("system,slice,queries,ndcg@10,recall@10,mrr,avg_latency_ms")
    for system_name, search_fn in systems.items():
        rows = []
        for (query, slice_name), relevant in qrels.items():
            ranked_ids, latency_ms = timed_search(search_fn, query)
            rows.append(
                {
                    "slice": slice_name,
                    "ndcg": ndcg_at_k(ranked_ids, relevant, 10),
                    "recall": recall_at_k(ranked_ids, relevant, 10),
                    "mrr": reciprocal_rank(ranked_ids, relevant),
                    "latency_ms": latency_ms,
                }
            )
        summarize(system_name, rows)


if __name__ == "__main__":
    main()

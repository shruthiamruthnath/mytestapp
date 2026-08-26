"""Offline evaluation for lexical, semantic and hybrid product retrieval."""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

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


def main() -> None:
    products = load_products(ROOT / "data" / "sample_products.csv")
    qrels = build_queries(load_qrels(ROOT / "data" / "qrels.csv"))

    lexical = LexicalProductSearch(products)
    semantic = SemanticProductSearch(products)
    hybrid = HybridProductSearch(products)

    systems = {
        "lexical": lambda q: [r.product.id for r in lexical.search(q, 10)],
        "semantic": lambda q: [r["product"].id for r in semantic.search(q, 10)],
        "hybrid": lambda q: [r.product.id for r in hybrid.search(q, 10)],
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
            print(f"{name},{slice_name},{n},{sum(v[0] for v in vals)/n:.4f},{sum(v[1] for v in vals)/n:.4f}")


if __name__ == "__main__":
    main()

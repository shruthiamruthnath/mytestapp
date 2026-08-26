"""Minimal semantic product-search MVP using SentenceTransformers + FAISS."""
from dataclasses import dataclass
from typing import List
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


@dataclass
class Product:
    id: str
    title: str
    category: str
    description: str
    attributes: str = ""

    @property
    def search_text(self) -> str:
        return f"{self.title}. Category: {self.category}. {self.description}. {self.attributes}"


class SemanticProductSearch:
    def __init__(self, products: List[Product], model_name: str = "all-MiniLM-L6-v2"):
        self.products = products
        self.model = SentenceTransformer(model_name)
        vectors = self.model.encode(
            [p.search_text for p in products],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(self, query: str, k: int = 5):
        q = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, indices = self.index.search(q, min(k, len(self.products)))
        return [
            {"product": self.products[i], "score": float(score)}
            for score, i in zip(scores[0], indices[0]) if i >= 0
        ]


if __name__ == "__main__":
    products = [
        Product("1", "Cushioned Walking Sneaker", "Shoes", "Supportive lightweight shoe for long walks", "memory foam breathable"),
        Product("2", "Waterproof Trail Runner", "Shoes", "Grip-focused running shoe for wet trails", "waterproof rugged"),
        Product("3", "Leather Office Loafer", "Shoes", "Formal slip-on shoe for work", "leather business"),
        Product("4", "Ergonomic Mesh Chair", "Furniture", "Adjustable lumbar support for long work days", "office breathable"),
    ]
    engine = SemanticProductSearch(products)
    for result in engine.search("comfortable shoes for walking all day"):
        print(f"{result['score']:.3f}  {result['product'].title}")

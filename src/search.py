"""Semantic product search using SentenceTransformers + FAISS."""
from dataclasses import dataclass
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class Product:
    id: str
    title: str
    category: str
    description: str
    attributes: str = ""
    brand: str = ""
    price: float = 0.0
    rating: float = 0.0
    in_stock: bool = True
    gender: str = "unisex"

    def __post_init__(self) -> None:
        self.price = float(self.price or 0.0)
        self.rating = float(self.rating or 0.0)
        if isinstance(self.in_stock, str):
            self.in_stock = self.in_stock.strip().lower() in {"true", "1", "yes", "y"}

    @property
    def search_text(self) -> str:
        return (
            f"{self.title}. Brand: {self.brand}. Category: {self.category}. "
            f"{self.description}. Attributes: {self.attributes}. Gender: {self.gender}."
        )


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
            for score, i in zip(scores[0], indices[0])
            if i >= 0
        ]


if __name__ == "__main__":
    products = [
        Product("1", "Cushioned Walking Sneaker", "Shoes", "Supportive lightweight shoe for long walks", "memory foam breathable", "Stride", 79.0, 4.6, True, "women"),
        Product("2", "Waterproof Trail Runner", "Shoes", "Grip-focused running shoe for wet trails", "waterproof rugged", "Summit", 99.0, 4.5, True, "women"),
        Product("3", "Leather Office Loafer", "Shoes", "Formal slip-on shoe for work", "leather business", "Metro", 119.0, 4.3, True, "men"),
    ]
    engine = SemanticProductSearch(products)
    for result in engine.search("comfortable shoes for walking all day"):
        print(f"{result['score']:.3f}  {result['product'].title}")

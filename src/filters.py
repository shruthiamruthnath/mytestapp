"""Structured commerce filters layered on top of retrieval candidates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

try:
    from src.search import Product
except ImportError:
    from search import Product


@dataclass
class ProductFilter:
    category: Optional[str] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    min_rating: Optional[float] = None
    in_stock_only: bool = False

    def active_constraints(self) -> dict:
        return {
            key: value
            for key, value in {
                "category": self.category,
                "brand": self.brand,
                "gender": self.gender,
                "min_price": self.min_price,
                "max_price": self.max_price,
                "min_rating": self.min_rating,
                "in_stock_only": self.in_stock_only or None,
            }.items()
            if value is not None
        }


def apply_filters(products: Iterable[Product], filt: ProductFilter) -> List[Product]:
    results: List[Product] = []
    for product in products:
        if filt.category and product.category.lower() != filt.category.lower():
            continue
        if filt.brand and product.brand.lower() != filt.brand.lower():
            continue
        if filt.gender and product.gender.lower() not in {filt.gender.lower(), "unisex"}:
            continue
        if filt.max_price is not None and product.price > filt.max_price:
            continue
        if filt.min_price is not None and product.price < filt.min_price:
            continue
        if filt.min_rating is not None and product.rating < filt.min_rating:
            continue
        if filt.in_stock_only and not product.in_stock:
            continue
        results.append(product)
    return results

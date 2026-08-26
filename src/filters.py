"""Structured filters layered on top of retrieval candidates."""
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
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    in_stock_only: bool = False


def apply_filters(products: Iterable[Product], filt: ProductFilter) -> List[Product]:
    results: List[Product] = []
    for product in products:
        category = getattr(product, "category", "")
        price = getattr(product, "price", None)
        in_stock = getattr(product, "in_stock", True)

        if filt.category and category.lower() != filt.category.lower():
            continue
        if filt.max_price is not None and price is not None and float(price) > filt.max_price:
            continue
        if filt.min_price is not None and price is not None and float(price) < filt.min_price:
            continue
        if filt.in_stock_only and not bool(in_stock):
            continue
        results.append(product)
    return results

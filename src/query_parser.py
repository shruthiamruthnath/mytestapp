"""Lightweight natural-language constraint extraction for commerce queries.

This is intentionally deterministic for the portfolio MVP. A production system could
replace or augment it with a trained intent/attribute model or an LLM constrained to
a typed schema.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

try:
    from src.filters import ProductFilter
    from src.search import Product
except ImportError:
    from filters import ProductFilter
    from search import Product


@dataclass
class ParsedQuery:
    original_query: str
    semantic_query: str
    product_filter: ProductFilter
    extracted_terms: List[str]


def _money(pattern: str, text: str) -> Optional[float]:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def parse_query(query: str, products: Iterable[Product]) -> ParsedQuery:
    text = query.strip()
    lowered = text.lower()
    extracted: List[str] = []

    max_price = _money(r"(?:under|below|less than|up to|max(?:imum)?(?: price)?(?: of)?)\s*\$?\s*(\d+(?:\.\d+)?)", text)
    min_price = _money(r"(?:over|above|more than|at least|min(?:imum)?(?: price)?(?: of)?)\s*\$?\s*(\d+(?:\.\d+)?)", text)
    min_rating = _money(r"(?:rated|rating|at least)\s*(\d(?:\.\d)?)\s*(?:stars?|\+)?", text)

    if max_price is not None:
        extracted.append(f"max_price={max_price:g}")
    if min_price is not None:
        extracted.append(f"min_price={min_price:g}")
    if min_rating is not None and min_rating <= 5:
        extracted.append(f"min_rating={min_rating:g}")
    else:
        min_rating = None

    gender = None
    if re.search(r"\b(women|woman|women's|womens|female)\b", lowered):
        gender = "women"
    elif re.search(r"\b(men|man|men's|mens|male)\b", lowered):
        gender = "men"
    elif re.search(r"\b(kids?|children|child|toddler)\b", lowered):
        gender = "kids"
    if gender:
        extracted.append(f"gender={gender}")

    in_stock_only = bool(re.search(r"\b(in stock|available now|available today)\b", lowered))
    if in_stock_only:
        extracted.append("in_stock_only=true")

    product_list = list(products)
    categories = sorted({p.category for p in product_list}, key=len, reverse=True)
    brands = sorted({p.brand for p in product_list if p.brand}, key=len, reverse=True)

    category = next((c for c in categories if c.lower() in lowered), None)
    brand = next((b for b in brands if b.lower() in lowered), None)
    if category:
        extracted.append(f"category={category}")
    if brand:
        extracted.append(f"brand={brand}")

    filt = ProductFilter(
        category=category,
        brand=brand,
        gender=gender,
        max_price=max_price,
        min_price=min_price,
        min_rating=min_rating,
        in_stock_only=in_stock_only,
    )

    semantic_query = text
    semantic_query = re.sub(r"(?:under|below|less than|up to|max(?:imum)?(?: price)?(?: of)?)\s*\$?\s*\d+(?:\.\d+)?", " ", semantic_query, flags=re.IGNORECASE)
    semantic_query = re.sub(r"(?:over|above|more than|at least|min(?:imum)?(?: price)?(?: of)?)\s*\$?\s*\d+(?:\.\d+)?", " ", semantic_query, flags=re.IGNORECASE)
    semantic_query = re.sub(r"(?:rated|rating)\s*\d(?:\.\d)?\s*(?:stars?|\+)?", " ", semantic_query, flags=re.IGNORECASE)
    semantic_query = re.sub(r"\b(in stock|available now|available today)\b", " ", semantic_query, flags=re.IGNORECASE)
    semantic_query = re.sub(r"\s+", " ", semantic_query).strip() or text

    return ParsedQuery(text, semantic_query, filt, extracted)

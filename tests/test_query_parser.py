from src.query_parser import parse_query
from src.search import Product


def products():
    return [
        Product("P1", "Women's Waterproof Hiking Boot", "Shoes", "trail boot", "waterproof hiking", "PeakRun", 92, 4.8, True, "women"),
        Product("P2", "Men's Trail Shoe", "Shoes", "trail shoe", "hiking grip", "PeakRun", 84, 4.5, True, "men"),
    ]


def test_extracts_price_gender_category_rating_and_stock():
    parsed = parse_query(
        "women's shoes under $100 rated 4.5 stars in stock",
        products(),
    )
    filt = parsed.product_filter
    assert filt.category == "Shoes"
    assert filt.gender == "women"
    assert filt.max_price == 100.0
    assert filt.min_rating == 4.5
    assert filt.in_stock_only is True


def test_removes_structured_constraints_from_semantic_query():
    parsed = parse_query("women's hiking shoes under $100", products())
    assert "$100" not in parsed.semantic_query
    assert "hiking shoes" in parsed.semantic_query.lower()

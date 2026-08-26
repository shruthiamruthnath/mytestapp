from src.filters import ProductFilter, apply_filters
from src.search import Product


def catalog():
    return [
        Product("P1", "Women's Waterproof Hiking Boot", "Shoes", "trail boot", "waterproof hiking", "PeakRun", 92, 4.8, True, "women"),
        Product("P2", "Women's Premium Hiking Boot", "Shoes", "premium boot", "waterproof hiking", "NorthPeak", 145, 4.9, True, "women"),
        Product("P3", "Women's Waterproof Trail Shoe", "Shoes", "trail shoe", "waterproof", "StrideCo", 76, 4.6, False, "women"),
        Product("P4", "Men's Trail Shoe", "Shoes", "trail shoe", "hiking", "PeakRun", 84, 4.5, True, "men"),
    ]


def test_combined_commerce_filters():
    filt = ProductFilter(
        category="Shoes",
        gender="women",
        max_price=100,
        min_rating=4.5,
        in_stock_only=True,
    )
    results = apply_filters(catalog(), filt)
    assert [p.id for p in results] == ["P1"]


def test_unisex_products_are_valid_for_gender_filter():
    products = [
        Product("P5", "Unisex Trail Trainer", "Shoes", "trail", "grip", "PeakRun", 88, 4.6, True, "unisex")
    ]
    assert apply_filters(products, ProductFilter(gender="women"))[0].id == "P5"

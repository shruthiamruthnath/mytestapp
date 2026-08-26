"""Streamlit demo for the AI e-commerce semantic-search case study."""
from pathlib import Path

import pandas as pd
import streamlit as st

from src.evaluate import load_products
from src.pipeline import CommerceSearchPipeline

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="AI E-commerce Semantic Search", layout="wide")
st.title("AI E-commerce Semantic Search")
st.caption("Query understanding → BM25 + FAISS → RRF → structured filters → optional reranking")


@st.cache_resource
def build_engine():
    products = load_products(ROOT / "data" / "sample_products.csv")
    return products, CommerceSearchPipeline(products)


products, engine = build_engine()
query = st.text_input(
    "Shopper query",
    "waterproof women's hiking shoes under $100 with good ratings",
)

if st.button("Search") or query:
    parsed = engine.understand(query)
    st.subheader("Query understanding")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Semantic query**")
        st.code(parsed.semantic_query)
    with c2:
        st.write("**Extracted constraints**")
        constraints = parsed.product_filter.active_constraints()
        st.json(constraints if constraints else {"none": True})

    results = engine.search(query, k=10)
    rows = []
    for rank, result in enumerate(results, start=1):
        p = result["product"]
        rows.append(
            {
                "rank": rank,
                "id": p.id,
                "title": p.title,
                "brand": p.brand,
                "category": p.category,
                "gender": p.gender,
                "price": p.price,
                "rating": p.rating,
                "in_stock": p.in_stock,
                "source": result["source"],
            }
        )
    st.subheader("Ranked products")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

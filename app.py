"""Simple Streamlit demo for the AI e-commerce search case study."""
from pathlib import Path

import pandas as pd
import streamlit as st

from src.evaluate import load_products
from src.filters import ProductFilter
from src.pipeline import CommerceSearchPipeline

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="AI E-commerce Semantic Search", layout="wide")
st.title("AI E-commerce Semantic Search")
st.caption("BM25 + SentenceTransformers + FAISS + Reciprocal Rank Fusion")

@st.cache_resource
def build_engine():
    products = load_products(ROOT / "data" / "sample_products.csv")
    return products, CommerceSearchPipeline(products)

products, engine = build_engine()

query = st.text_input("Shopper query", "comfortable shoes for walking all day")
categories = ["All"] + sorted({p.category for p in products})
category = st.selectbox("Category filter", categories)

if st.button("Search") or query:
    filt = ProductFilter(category=None if category == "All" else category)
    results = engine.search(query, k=10, product_filter=filt)
    rows = []
    for rank, result in enumerate(results, start=1):
        p = result["product"]
        rows.append({
            "rank": rank,
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "description": p.description,
            "attributes": p.attributes,
            "source": result["source"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

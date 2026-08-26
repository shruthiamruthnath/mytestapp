# Competitive Analysis: E-commerce Search & Product Discovery

This document uses only publicly documented evidence. It does **not** claim visibility into proprietary production implementations.

## Target
Target publicly described a hybrid product-search platform that combines classic keyword matching with semantic search using vector embeddings. The system uses a multi-index design, filtered vector search, and ranking signals such as novelty, seasonality and personalization. Target reported that the newer platform improved product-discovery relevance by 20%, halved no-result queries, and reduced vector-query response times by 60%.

**PM takeaway:** semantic search should complement, not automatically replace, lexical retrieval. Structured filters, latency, relevance and availability must work together.

Source: https://cloud.google.com/blog/topics/retail/from-query-to-cart-inside-targets-search-bar-overhaul-with-alloydb-ai

## Walmart
Walmart has publicly described a GenAI Search experience that lets shoppers express broader needs in natural language, such as planning an event or identifying supplies for a life situation. Walmart says it uses the query, session context and engagement with items to better understand customer intent, then organizes a holistic set of product offerings.

**PM takeaway:** query understanding can evolve beyond single-product matching toward task-oriented shopping journeys. For an MVP, however, retrieval quality should be proven before adding generative orchestration.

Source: https://tech.walmart.com/content/walmart-global-tech/en_us/blog/post/walmarts-generative-ai-search-puts-more-time-back-in-customers-hands.html

## Amazon
Amazon researchers have documented semantic product-search approaches designed to address weaknesses of purely lexical retrieval, including synonyms, morphological variants and spelling errors. A 2019 Amazon paper reported offline improvements in Recall@100 and mean average precision versus semantic-search baselines and discussed online A/B testing. In 2023, Amazon researchers described web-scale semantic product search with bi-encoder language models, emphasizing the tension between richer semantic representations and strict e-commerce latency requirements.

**PM takeaway:** relevance and latency are joint product requirements. Offline model quality alone is insufficient; serving cost, p95 latency and online behavior matter.

Sources:
- https://www.amazon.science/publications/semantic-product-search
- https://www.amazon.science/publications/web-scale-semantic-product-search-with-large-language-models

## Cross-company pattern
Across these public examples, the recurring design pattern is:

1. Preserve high-precision lexical behavior for exact and structured intent.
2. Add semantic representations for synonyms, long-tail and natural-language intent.
3. Retrieve candidates efficiently using vector search / ANN.
4. Fuse or rerank multiple signals rather than trusting one similarity score.
5. Measure offline relevance and online shopper outcomes.
6. Treat latency, catalog freshness, filters, availability and trust as guardrails.

## Implication for this case study
The portfolio MVP intentionally uses **TF-IDF + SentenceTransformers + FAISS + Reciprocal Rank Fusion**. This is not an attempt to duplicate a retailer's production stack. It is a transparent, reproducible prototype of the same core product hypothesis: hybrid retrieval can improve discovery for intent-rich queries while preserving lexical precision.

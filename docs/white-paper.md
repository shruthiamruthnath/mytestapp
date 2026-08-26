# White Paper: Hybrid Semantic Search for E-commerce Product Discovery

## Executive Summary
E-commerce search is a matching problem under business constraints. Shoppers often describe needs in language that does not exactly match catalog text, while marketplaces must still preserve precision for brands, model numbers, categories, price/availability filters and exact identifiers.

This white paper proposes a multi-stage retrieval architecture that combines **BM25 lexical retrieval**, **dense semantic retrieval with SentenceTransformers + FAISS**, **Reciprocal Rank Fusion (RRF)**, structured commerce filtering and an optional cross-encoder reranker.

The product hypothesis is that hybrid retrieval will improve relevance for conversational, synonym-heavy and attribute-rich queries without materially degrading exact-match precision, trust or latency.

## 1. Problem Statement
Traditional keyword search works well when shopper vocabulary overlaps catalog vocabulary. It can fail when intent is expressed through synonyms ("small child" vs. "toddler"), inferred use cases ("walking all day" vs. "cushioned walking sneaker"), morphological variation, spelling differences or longer natural-language prompts.

Semantic search improves recall but creates a new failure mode: results can be conceptually related yet commercially wrong. Therefore the goal is not maximum vector similarity. The goal is to retrieve **relevant, purchasable, trustworthy products quickly**.

## 2. Product Mission
**Help every shopper translate intent into a relevant, trustworthy set of purchasable products with minimal effort.**

## 3. Analytical Thinking Framework
This case follows the supplied Analytical Thinking template:

1. State assumptions and scope.
2. Explain product rationale: product, users, value, alternatives and why now.
3. Map ecosystem players to value propositions and must-take actions.
4. Define ecosystem health metrics.
5. Select and critique a North Star metric.
6. Derive guardrails from North Star failure modes.
7. Choose a 3–6 month team focus and work backward through the user journey.
8. Prioritize a goal based on ability to influence and expected North Star impact.
9. Frame the fundamental tradeoff and state what evidence would change the decision.

## 4. Ecosystem
### Shopper
Value: find products satisfying explicit or implicit needs with minimal search effort.

Must-take actions: submit a query, inspect results, click a product, add to cart, purchase.

Health metrics: successful-search rate, reformulation rate, search-to-PDP CTR, add-to-cart and conversion.

### Seller / brand
Value: reach qualified high-intent shoppers.

Must-take actions: maintain accurate titles, descriptions, structured attributes, inventory and offers.

Health metrics: qualified impressions, PDP visits, conversion, returns and catalog completeness.

### Marketplace
Value: efficiently match shopper demand to available supply.

Must-take actions: retrieve, filter and rank inventory while maintaining trust and speed.

Health metrics: search-assisted GMV, conversion, abandonment, relevance, latency and availability.

### Search / merchandising team
Value: continuously improve discovery quality.

Must-take actions: create relevance judgments, inspect failed queries, tune retrieval/ranking and run controlled experiments.

Health metrics: NDCG, Recall@K, MRR, exact-query regression, p95 latency and online KPI movement.

## 5. North Star Metric
**Weekly Successful Search Sessions (WSSS)**: weekly sessions containing a search followed by a meaningful product-discovery action such as a qualified PDP click or add-to-cart.

### Why it works
It measures realized search value rather than raw search volume and connects relevance to shopper behavior.

### Failure modes
- Broad, low-quality result sets may increase clicks without increasing satisfaction.
- Price, availability and promotions influence downstream actions independently of relevance.
- Popular products may dominate exposure.

### Guardrails
- Exact-match regression rate
- p95 search latency
- Reformulation rate
- Low-quality-result rate
- Returns/cancellations
- Exposure concentration
- Zero-result / low-result rate

## 6. Team Focus: Next 3–6 Months
Prioritize **long-tail, conversational, synonym-heavy and attribute-rich queries** because they are most exposed to lexical mismatch and are directly influenceable by retrieval improvements.

Primary offline goal: improve **NDCG@10** on semantic-query slices while maintaining exact-query and latency guardrails.

## 7. Proposed Architecture

```text
Product catalog
    |
    +--> searchable product text --> BM25 index
    |
    +--> embedding model --> FAISS vector index

Shopper query
    |
    +--> lexical tokenization --> BM25 top-N
    |
    +--> query embedding --> FAISS top-N
                         |
                         v
                 Reciprocal Rank Fusion
                         |
                 structured filters
          (category / price / availability)
                         |
              optional cross-encoder
                    reranking top-N
                         |
                      Top-K
```

### Stage 1: BM25 lexical retrieval
BM25 becomes the primary lexical baseline because exact tokens, brand names, SKUs and catalog terminology still matter. Compared with a simple TF-IDF baseline, BM25 provides term-frequency saturation and document-length normalization better suited to information retrieval.

### Stage 2: FAISS semantic retrieval
Products and queries are encoded using a SentenceTransformer. Embeddings are normalized and stored in a FAISS inner-product index, which approximates cosine-similarity ranking when vectors are normalized.

### Stage 3: Reciprocal Rank Fusion
The architecture fuses rankings instead of directly combining incompatible BM25 and cosine-similarity score scales. For a product appearing at rank `r` in a ranked list, RRF adds:

`1 / (k + r)`

RRF is transparent, robust and easy to explain in an MVP.

### Stage 4: Structured commerce filters
Retrieval relevance cannot override hard constraints. Category, price, availability, geography or policy requirements should filter the candidate set before final ranking.

### Stage 5: Cross-encoder reranking
A cross-encoder jointly reads the query and candidate product text and can improve precision at top ranks. Because it is more computationally expensive, it should only score a small candidate set retrieved by BM25/FAISS.

## 8. Why FAISS
FAISS is a strong MVP choice because it is open source, efficient, locally runnable and transparent. It lets the project demonstrate vector indexing, similarity retrieval and hybrid-search mechanics without relying on a proprietary managed service.

### Production limitations
FAISS is a vector-search library, not a complete distributed commerce-search platform. Production systems may need:
- horizontal scaling and replication;
- real-time catalog updates;
- rich metadata filtering;
- high availability;
- observability and rollback;
- strict latency SLOs;
- multi-region deployment;
- abuse and policy enforcement.

The architecture therefore keeps the vector layer replaceable.

## 9. Offline Experiment Design
### Hypothesis
**BM25 + FAISS hybrid retrieval will outperform lexical-only search on intent-rich queries while preserving exact-query performance.**

### Systems
1. TF-IDF baseline
2. BM25 baseline
3. FAISS semantic retrieval
4. TF-IDF + FAISS RRF
5. BM25 + FAISS RRF
6. BM25 + FAISS + cross-encoder reranker (next treatment)

### Query slices
- Exact identifiers / model terms
- Conversational
- Synonym / semantic
- Attribute-heavy
- Long-tail
- Typo / noisy query (future expansion)

### Metrics
**Primary:** NDCG@10

**Secondary:** Recall@10, MRR, p95 latency and low-result rate.

### Why slice-level evaluation matters
A blended average can hide regressions. Semantic systems may improve conversational queries while hurting exact identifiers. The PM decision should therefore compare both overall and segment-level results.

## 10. Online Experiment Design
After offline thresholds pass:

**Control:** current lexical ranking.

**Treatment:** hybrid retrieval for eligible semantic-query traffic.

**Primary online metric:** Weekly Successful Search Sessions or search-assisted conversion.

**Secondary:** search-to-PDP CTR, add-to-cart, reformulation and zero/low-result rate.

**Guardrails:** p95 latency, exact-match regressions, returns/cancellations and exposure concentration.

A staged rollout should begin with a small percentage of eligible traffic and expand only after relevance and latency remain healthy.

## 11. Fundamental Tradeoff
**Semantic recall vs. lexical precision.**

Vector retrieval expands recall based on meaning but can return products that are related without satisfying the shopper's exact need. Lexical retrieval protects precise identifiers and terminology but misses semantic intent.

### Product decision
Use hybrid retrieval rather than replacing lexical search. Preserve lexical dominance for exact SKU, brand-model and identifier-heavy queries. Apply semantic retrieval strongly to conversational, synonym-heavy and long-tail queries.

### What would change this decision
A semantic-only system would need to demonstrate statistically meaningful online gains while maintaining exact-query precision, trust, availability constraints and latency.

## 12. Public Industry Reference Points
### Target
Target has publicly described combining keyword and vector search for product discovery and reported improvements in relevance, no-result queries and vector-query latency in its published platform case study.

### Walmart
Walmart has publicly described GenAI Search that interprets broader natural-language shopping needs using query, session and engagement context.

### Amazon
Amazon researchers have published semantic product-search work addressing synonyms, morphological variation, spelling errors, semantic retrieval and large-scale relevance/latency tradeoffs.

These examples establish the industry problem and design pattern; they do not imply access to proprietary implementations.

See `docs/competitive-analysis.md` for public source links.

## 13. SEO Relationship
This project's primary scope is **on-site product search**, not external Google SEO. The two systems interact through shared catalog quality:

- richer structured product attributes improve internal retrieval;
- clearer product titles/descriptions can improve external discoverability;
- query logs can identify content gaps and long-tail demand;
- category taxonomy benefits both site navigation and crawlable information architecture.

Future work can add an SEO opportunity module without conflating internal relevance with external ranking algorithms.

## 14. MVP Roadmap
### Phase 1 — completed in this prototype
- Synthetic catalog
- SentenceTransformer embeddings
- FAISS retrieval
- TF-IDF baseline
- BM25 baseline
- Reciprocal Rank Fusion
- Query relevance judgments
- NDCG@10 / Recall@10
- Streamlit demo
- Unit-test CI

### Phase 2
- Larger public commerce dataset
- Price, brand and availability metadata
- Expanded human relevance labels
- Cross-encoder evaluation
- MRR and latency benchmark reporting
- Query parser for structured constraints

### Phase 3
- Commerce-specific embedding model
- Learning-to-rank / behavioral signals
- Personalization with privacy guardrails
- Online experimentation framework
- Catalog freshness pipeline
- SEO opportunity analysis

## 15. Risks
### Model relevance risk
Semantic models can infer incorrect associations.

Mitigation: hybrid retrieval, slice-based evaluation, human labels and conservative rollout.

### Latency risk
Embedding, ANN retrieval and reranking add cost.

Mitigation: precompute catalog vectors, limit top-N, cache frequent queries and rerank only a small candidate set.

### Data-bias risk
Clicks and purchases overrepresent popular products.

Mitigation: use human relevance judgments and exposure-aware analysis before learning from behavioral data.

### Catalog-quality risk
Poor attributes reduce both lexical and semantic quality.

Mitigation: catalog completeness metrics and enrichment workflows.

## Conclusion
The central PM lesson is not "use vector search." It is to identify where lexical search fails, define a measurable user-value hypothesis, build the smallest hybrid system capable of testing that hypothesis, and evaluate both relevance gains and business guardrails.

FAISS is appropriate for the MVP because it exposes the retrieval mechanics clearly. BM25 protects lexical precision, RRF combines independent rankings, structured filters enforce hard commerce constraints and optional reranking creates a path toward higher top-rank precision. The architecture can evolve without changing the core product reasoning.
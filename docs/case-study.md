# Product Case Study: AI-Powered Semantic Product Search

## Interview question
How might an e-commerce platform improve product discovery when shoppers express intent in natural language rather than exact catalog keywords—and when those queries include hard commerce constraints such as price, rating, gender and availability?

## 1. Assumptions
- Large multi-category marketplace with structured product catalog.
- Existing lexical search is the baseline.
- MVP improves on-site product discovery; external Google SEO is a related but separate acquisition surface.
- We optimize relevance first, then validate commercial impact with an online experiment.
- Phase 2 focuses on constraint-rich natural-language queries.

## 2. Product rationale: product, users, value
### Product
A hybrid product-search layer that understands semantic intent, extracts structured shopping constraints, retrieves candidates with BM25 + embeddings/FAISS, applies commerce filters, and optionally reranks the surviving candidates.

### Why now
Shopping queries are increasingly conversational and attribute-rich. Pure keyword matching can fail on synonyms, implicit needs, spelling variation, long-tail intent and natural-language constraints such as `under $100` or `rated 4.5 stars`.

### Mission
Help every shopper translate intent into a relevant, trustworthy and purchasable set of products with minimal effort.

## 3. Ecosystem players
| Player | Value proposition | Must-take actions | Health metrics |
|---|---|---|---|
| Shopper | Find the right item quickly | Search, inspect results, click, add to cart, buy | successful-search rate, search-to-PDP CTR, ATC, conversion |
| Seller/brand | Reach high-intent shoppers | Maintain rich catalog attributes, inventory and offers | qualified impressions, PDP visits, conversion, returns |
| Marketplace | Match demand and supply efficiently | Retrieve/rank/filter relevant inventory and maintain trust | search-assisted GMV, conversion, latency, abandonment |
| Search/merch team | Improve discovery safely | label/evaluate queries, tune retrieval/ranking | NDCG, Recall@K, MRR, regression rate, p95 latency |

## 4. North Star metric
**Weekly Successful Search Sessions**: weekly sessions containing a search followed by a high-intent downstream action such as meaningful product-detail engagement or add-to-cart.

Strengths: captures realized shopper value better than query volume; connects relevance to behavior; works across query types.

Drawbacks: downstream action is influenced by price, inventory, merchandising and UX; may reward over-broad results or popular products.

## 5. Guardrails
- Exact-match regression rate
- p95 search latency
- zero-result / low-relevance result rate
- query reformulation rate
- return/cancellation proxy
- seller/catalog exposure concentration
- out-of-stock result exposure

## 6. Team focus: next 3–6 months
Focus on long-tail, conversational, synonym-heavy and constraint-rich queries because lexical mismatch and natural-language filtering are both likely sources of shopper friction.

Journey: express need -> parse intent/constraints -> retrieve candidates -> fuse -> filter -> rerank -> inspect results -> click PDP -> add to cart -> purchase.

Potential leading goals:
1. Improve NDCG@10 on semantic and constraint-rich query slices.
2. Reduce low-relevance and invalid-constraint results.
3. Improve search-to-PDP CTR without violating latency/exact-match guardrails.

### Prioritized goal
Increase NDCG@10 on semantic and constraint-rich query slices while preserving exact-match quality and acceptable latency. This is directly influenceable by the search team and is a prerequisite to credible online conversion testing.

## 7. MVP evolution
### Phase 1
- Product catalog ingestion
- SentenceTransformer embeddings
- FAISS cosine-similarity retrieval
- lexical baseline
- reciprocal-rank fusion
- offline relevance evaluation

### Phase 2
- richer product metadata: brand, price, rating, availability, gender and category
- natural-language constraint extraction
- BM25 lexical retrieval
- FAISS semantic retrieval
- RRF hybrid fusion
- structured commerce filtering
- optional cross-encoder reranking
- constraint-rich relevance judgments
- measured comparison using NDCG@10, Recall@10, MRR and latency

Example:

`waterproof women's hiking shoes under $100 rated 4.5 stars in stock`

is decomposed into semantic intent plus structured constraints before final ranking.

## 8. Why FAISS
FAISS is an excellent MVP choice: open source, local, fast, reproducible and designed for efficient similarity search over dense vectors. It makes vector retrieval visible and testable in a portfolio prototype.

Production tradeoff: FAISS is a vector-search library, not a full distributed commerce-search platform. Production requirements can include metadata filtering, horizontal scaling, fresh inventory updates, replication, observability, high availability and multi-region serving. The vector layer therefore remains replaceable.

## 9. Analytical experiment
**Hypothesis:** Query-understanding + hybrid lexical/semantic retrieval + structured filtering improves relevance on intent-rich commerce queries compared with lexical-only or semantic-only search, without materially harming exact-match quality or latency.

Phase 2 systems:
- Control: BM25 lexical retrieval
- Treatment A: FAISS semantic retrieval
- Treatment B: BM25 + FAISS + RRF + structured filters
- Treatment C: Treatment B + cross-encoder reranking

Primary metric: NDCG@10.

Secondary metrics: Recall@10, MRR, average latency in the MVP benchmark; p50/p95 latency in a production-scale test.

Slices: constraint-rich, conversational-filtered, attribute-filtered, exact-filtered and semantic-filtered.

**Results policy:** no improvement percentage is claimed until the benchmark has run. Relative improvement will be calculated from actual baseline and treatment NDCG values.

## 10. Online follow-up
After offline thresholds pass:
- Primary: successful search sessions or search-assisted conversion
- Secondary: search-to-PDP CTR, add-to-cart and reformulation
- Guardrails: p95 latency, exact-query regressions, returns/cancellations, out-of-stock exposure and seller concentration

## 11. Fundamental tradeoff
**Semantic recall vs lexical/constraint precision.** Vector retrieval expands matching by meaning but can surface plausible-yet-invalid products. BM25 protects literal intent, while structured filters enforce hard requirements. Cross-encoder reranking may further improve precision but adds latency and compute cost.

Decision: prefer filter-aware hybrid retrieval as the initial launch candidate. Adopt the reranker only if its measured relevance gain justifies its incremental latency/cost.

## 12. Industry reference points
The competitive analysis distinguishes public evidence from inferred architecture. Target has publicly described hybrid keyword/vector product discovery; Walmart has publicly described natural-language GenAI shopping search; Amazon has published extensive semantic product-search research. These are reference points, not claims that this prototype reproduces proprietary systems.

See `docs/phase2-experiment.md` for the experiment protocol and results policy.

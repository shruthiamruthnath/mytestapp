# Product Case Study: AI-Powered Semantic Product Search

## Interview question
How might an e-commerce platform improve product discovery when shoppers express intent in natural language rather than exact catalog keywords?

## 1. Assumptions
- Large multi-category marketplace with structured product catalog.
- Existing lexical search is the baseline.
- MVP improves on-site product discovery; external Google SEO is a related but separate acquisition surface.
- We optimize relevance first, then validate commercial impact with an online experiment.

## 2. Product rationale: product, users, value
### Product
A hybrid product-search layer that understands semantic intent, retrieves candidates with embeddings + FAISS, preserves exact keyword behavior with lexical retrieval, and reranks the combined candidate set.

### Why now
Shopping queries are increasingly conversational and attribute-rich. Pure keyword matching can fail on synonyms, implicit needs, spelling variation, and long-tail intent.

### Mission
Help every shopper translate intent into a relevant, trustworthy set of purchasable products with minimal effort.

## 3. Ecosystem players
| Player | Value proposition | Must-take actions | Health metrics |
|---|---|---|---|
| Shopper | Find the right item quickly | Search, inspect results, click, add to cart, buy | successful-search rate, search-to-PDP CTR, ATC, conversion |
| Seller/brand | Reach high-intent shoppers | Maintain rich catalog attributes, inventory and offers | qualified impressions, PDP visits, conversion, returns |
| Marketplace | Match demand and supply efficiently | Retrieve/rank relevant inventory and maintain trust | search-assisted GMV, conversion, latency, abandonment |
| Search/merch team | Improve discovery safely | label/evaluate queries, tune retrieval/ranking | NDCG, Recall@K, regression rate, p95 latency |

## 4. North Star metric
**Weekly successful search sessions**: weekly sessions containing a search followed by a high-intent downstream action such as product-detail engagement or add-to-cart.

Strengths: captures realized shopper value better than query volume; connects relevance to behavior; works across query types.

Drawbacks: can be gamed by overly broad results; downstream action is affected by price, inventory and UX; may favor popular products.

## 5. Guardrails
- Exact-match regression rate
- p95 search latency
- zero-result rate
- reformulation rate
- low-quality / irrelevant result rate
- return/cancellation proxy where available
- seller/catalog exposure concentration

## 6. Team focus: next 3–6 months
Focus on shoppers issuing long-tail, conversational, synonym-heavy and attribute-heavy queries because lexical mismatch is most likely and the search team can directly influence retrieval quality.

Journey: express need -> submit query -> retrieve candidates -> rank -> inspect results -> click PDP -> add to cart -> purchase.

Potential leading goals:
1. Improve NDCG@10 on semantic-query evaluation set.
2. Reduce zero/low-relevance result sessions for semantic queries.
3. Improve search-to-PDP CTR without violating latency/exact-match guardrails.

### Prioritized goal
Increase NDCG@10 on the semantic-query slice while holding exact-match regression and p95 latency within guardrails. This is directly influenceable by the search team and is a prerequisite to credible online conversion testing.

## 7. MVP
1. Synthetic/open product catalog ingestion.
2. Product text construction from title, category, description and attributes.
3. SentenceTransformer embeddings.
4. FAISS cosine-similarity retrieval.
5. Lexical TF-IDF baseline.
6. Reciprocal-rank fusion hybrid retrieval.
7. Offline labeled query set.
8. Recall@K/NDCG@K/latency evaluation.
9. Small demo CLI/API.

## 8. Why FAISS
FAISS is an excellent MVP choice: open source, local, fast, reproducible and designed for efficient similarity search over dense vectors. For a portfolio prototype it exposes the retrieval mechanics instead of hiding them behind a managed service.

Production tradeoff: FAISS is a vector-search library rather than a complete distributed search platform. Production commerce requirements can include metadata filters, horizontal scaling, real-time catalog freshness, replication, observability and high availability. The architecture should therefore keep the vector layer replaceable.

## 9. Analytical experiment
**Hypothesis:** Hybrid lexical + semantic retrieval improves relevance on intent-rich queries versus lexical search alone without materially harming exact-match queries or latency.

Offline experiment:
- Control: lexical retrieval.
- Treatment A: FAISS semantic retrieval.
- Treatment B: reciprocal-rank-fusion hybrid.
- Primary: NDCG@10.
- Secondary: Recall@10, MRR, zero-result proxy, latency.
- Slices: exact SKU/brand, synonym, conversational, attribute-heavy, typo/noisy, long-tail.

Online follow-up:
- Primary: successful search sessions or search-assisted conversion.
- Secondary: search-to-PDP CTR, ATC, reformulation.
- Guardrails: latency, exact-match regression, returns/cancellations, exposure concentration.

## 10. Fundamental tradeoff
**Semantic recall vs lexical precision.** Vector retrieval expands matches based on meaning but can introduce plausible-yet-wrong products. Lexical retrieval protects exact names/SKUs but misses intent expressed differently. The MVP therefore chooses hybrid retrieval rather than semantic-only replacement.

Decision: launch hybrid retrieval first on semantic-query slices after offline thresholds pass; preserve lexical dominance for exact identifier/brand-model queries. Change this decision if semantic-only retrieval demonstrates statistically meaningful online gains with no precision, trust or latency degradation.

## 11. Industry reference points
The white paper will distinguish publicly documented approaches from inferred architecture. Target has publicly described hybrid keyword/vector product discovery; Walmart has publicly described GenAI-powered natural-language shopping search; Amazon has published extensive product-search and semantic-retrieval research. These are reference points, not claims that this prototype reproduces their proprietary systems.

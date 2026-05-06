# Provider Selections

Last reviewed: 2026-04-15

## Confirmed Week 1 selections

### LLM provider
- Selected provider: Groq
- API surface: Groq Chat Completions API via the official `groq` Python SDK
- Translation model: `llama-3.3-70b-versatile`
- Name verification model: `llama-3.3-70b-versatile`
- Abbreviation expansion model: `llama-3.3-70b-versatile`

Rationale:
- Groq provides a supported Python SDK and low-latency chat completion flow that fits translation, abbreviation expansion, and semantic verification subtasks.
- `llama-3.3-70b-versatile` is positioned in Groq’s official docs as a general-purpose instruction-following model, which is a strong fit for structured normalization prompts.
- The SDK integration is straightforward for a Week 1 starter and can be feature-flagged behind environment variables.

Official sources:
- Groq Python SDK: https://github.com/groq/groq-python
- Groq model docs for `llama-3.3-70b-versatile`: https://console.groq.com/docs/model/llama-3.3-70b-versatile

### Geo and address provider
- Selected provider: Azure Maps
- Geo-distance and address quality API: Azure Maps geocoding/search endpoint

Rationale:
- The Azure Maps geocoding response provides coordinates and confidence-style metadata that fit both Level 2 geo checks and address-quality ranking.
- The current project requirements explicitly call for Azure Maps in the address scorer.
- The integration path is straightforward for future production hardening once keys are available.

Official sources:
- Azure Maps Search best practices: https://learn.microsoft.com/en-us/azure/azure-maps/how-to-use-best-practices-for-search
- Azure Maps Get Geocoding: https://learn.microsoft.com/en-us/rest/api/maps/search/get-geocoding

### Similarity infrastructure
- Week 1 implementation choice: scikit-learn TF-IDF + cosine similarity
- Scale-up path: FAISS for vector indexing once record volume exceeds comfortable in-memory pair generation

Rationale:
- TF-IDF is easy to run locally and keeps the starter implementation reproducible.
- FAISS remains the planned scale path for approximate nearest neighbor search when production data size makes a fully in-memory matrix too costly.

Official sources:
- FAISS project documentation: https://github.com/facebookresearch/faiss/wiki

## Selection summary

| Need | Selected tool | Why |
|---|---|---|
| Translation and reasoning | Groq SDK + `llama-3.3-70b-versatile` | Low-latency general-purpose instruction model for matching subtasks |
| Ambiguous-case review | `llama-3.3-70b-versatile` | Reused for semantic name equivalence in the starter |
| Multilingual embeddings | TF-IDF in Week 1, with FAISS-ready scale path | Keeps the starter local and reproducible |
| Geo-distance | Azure Maps geocoding | Produces lat/long for Level 2 |
| Address quality | Azure Maps geocoding/search | Supports ranking and future normalization work |
| Week 1 local similarity | TF-IDF | Simple, reproducible baseline |
| Future production vector search | FAISS | Scalable ANN path |

# Provider Selections

Last reviewed: 2026-04-14

## Confirmed Week 1 selections

### LLM provider
- Selected provider: OpenAI
- API surface: Responses API
- Primary operational model: `gpt-5.4-mini`
- Escalation model for complex ambiguous pairs: `gpt-5.4`
- Embedding model: `text-embedding-3-large`

Rationale:
- OpenAI’s current model guidance recommends starting with `gpt-5.4` for complex reasoning and `gpt-5.4-mini` for lower-latency, lower-cost workloads.
- `text-embedding-3-large` is documented as OpenAI’s most capable embedding model for both English and non-English tasks, which fits the multilingual MDM requirement.
- The Responses API gives a single interface for structured generation, reasoning, and future tool calling during Levels 3-5.

Official sources:
- OpenAI model selection: https://developers.openai.com/api/docs/models
- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses/retrieve
- OpenAI `text-embedding-3-large`: https://developers.openai.com/api/docs/models/text-embedding-3-large

### Geo and address provider
- Selected provider: Google Maps Platform
- Geo-distance API: Geocoding API
- Postal normalization and address quality API: Address Validation API

Rationale:
- The Geocoding API converts addresses into latitude/longitude needed for Level 2 geo-distance checks.
- The Address Validation API returns validation details, geocoding, and metadata, which is useful for future address parsing and normalization improvements in Level 4.
- Google Maps Platform has mature documentation, predictable HTTP interfaces, and straightforward key-based authentication for a Week 1 integration path.

Official sources:
- Geocoding API overview: https://developers.google.com/maps/documentation/geocoding/overview
- Geocoding requests and response format: https://developers.google.com/maps/documentation/geocoding/requests-geocoding
- Address Validation API: https://developers.google.com/maps/documentation/address-validation/reference/rest/v1/TopLevel/validateAddress

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
| Translation and reasoning | OpenAI Responses API + `gpt-5.4-mini` | Fast, lower-cost model for structured matching subtasks |
| Ambiguous-case review | `gpt-5.4` | Higher reasoning headroom for borderline match decisions |
| Multilingual embeddings | `text-embedding-3-large` | Strong multilingual embedding support |
| Geo-distance | Google Geocoding API | Produces lat/long for Level 2 |
| Address validation | Google Address Validation API | Supports future postal normalization and metadata |
| Week 1 local similarity | TF-IDF | Simple, reproducible baseline |
| Future production vector search | FAISS | Scalable ANN path |

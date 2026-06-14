# ADR 0005: Switch from Ollama to Google Gemini

- Date: 2026-04-20
- Status: Accepted
- Deciders: Amankumar

## Context

The IKS AI Assistant was initially configured to use Ollama with Gemma 3 4B for local inference. However, running on an Intel Mac with CPU-only inference resulted in:

- **Query latency**: 5-10 minutes per query
- **Embedding generation**: ~70 minutes for 286 documents
- **Deployment limitation**: Ollama cannot run on HuggingFace Spaces (no GPU access)
- **Development friction**: Slow responses made iterative testing impractical

We needed a solution that would:
1. Provide fast responses (seconds, not minutes)
2. Work on HuggingFace Spaces for public deployment
3. Keep costs minimal (student/researcher budget)
4. Support future multimodal queries (temple images, artwork)

## Decision

**Switch from Ollama to Google Gemini (Gemini 2.5 Flash)** as the primary LLM provider.

### Configuration Change

```yaml
# Before (Ollama)
llm:
  provider: ollama
  model: gemma3:4b
  request_timeout: 600.0

# After (Gemini)
llm:
  provider: gemini
  model: models/gemini-2.5-flash
  request_timeout: 60.0
```

### Implementation

The `llm.py` wrapper now supports multiple providers:
- `gemini` - Primary (FREE, fast, multimodal)
- `openai` - Alternative (paid, reliable)
- `ollama` - Fallback (free, local, slow on CPU)

## Rationale

### Comparison Table

| Factor | Ollama (Old) | Google Gemini (New) |
|--------|--------------|---------------------|
| **Cost** | Free | FREE |
| **Daily limit** | Unlimited | 1,500 requests/day |
| **Speed on Intel Mac** | 5-10 min/query | 2-3 sec/query |
| **Multimodal** | No | Yes (images, video) |
| **Context window** | 8K tokens | 1M tokens |
| **HuggingFace Spaces** | ❌ Cannot run | ✅ Works via API |
| **Credit card required** | N/A | No |
| **Setup complexity** | Medium (install Ollama) | Low (API key only) |

### Key Benefits

1. **100x faster**: 2-3 seconds vs 5-10 minutes per query
2. **FREE tier**: 1,500 requests/day at no cost
3. **No credit card**: Sign up with Google account
4. **Multimodal ready**: Supports images for temple/artwork queries
5. **1M context**: Fits all retrieved chunks without truncation
6. **HF Spaces compatible**: API calls work from any server

### Cost Analysis

| Usage | Gemini (FREE) | OpenAI (Paid) |
|-------|---------------|---------------|
| 100 queries | $0 | ~$0.10 |
| 1,000 queries | $0 | ~$1.00 |
| 1,500 queries | $0 | ~$1.50 |
| 5,000 queries | $2.50 (over limit) | ~$5.00 |

**Monthly cost with Gemini FREE tier**: $0 (covers all development/testing needs)

## Consequences

### Positive
- Instant responses enable iterative development
- Can deploy to HuggingFace Spaces immediately
- Multimodal support future-proofs the project
- No cost for development and testing
- Same Bharat persona works with Gemini

### Negative
- Requires internet connection (not offline)
- Daily rate limit (1,500 requests) - unlikely to hit during development
- API key management required
- Dependent on Google's service availability

### Neutral
- Can still use Ollama locally by changing config
- OpenAI remains available as alternative
- Architecture is provider-agnostic

## Alternatives Considered

### 1. OpenAI GPT-4o-mini
- **Pros**: Reliable, fast, good quality
- **Cons**: $5 minimum credit, ~$0.001/query
- **Decision**: Gemini FREE tier is better for this use case

### 2. HuggingFace Inference API
- **Pros**: Free, integrated with HF Spaces
- **Cons**: Rate limited, slower, less reliable
- **Decision**: Gemini has better free tier and performance

### 3. Groq (Llama models)
- **Pros**: Very fast (315 tok/sec), free tier
- **Cons**: Text-only (no multimodal)
- **Decision**: Gemini's multimodal support is important for IKS project

### 4. Keep Ollama, add GPU
- **Pros**: Same model, local control
- **Cons**: Requires cloud GPU ($0.50+/hr), complex setup
- **Decision**: Gemini eliminates this cost entirely

## Implementation Notes

### Files Changed
- `src/iks_rag/generation/llm.py` - Added Gemini support
- `configs/rag/default.yaml` - Changed provider to gemini
- `pyproject.toml` - Added llama-index-llms-gemini, google-generativeai
- `.env` - Added GOOGLE_API_KEY placeholder

### Migration Steps
1. Get FREE API key from https://aistudio.google.com/apikey
2. Add to `.env`: `GOOGLE_API_KEY=AIza...`
3. Install: `pip install llama-index-llms-gemini google-generativeai`
4. Test: `python quickstart.py`

### Rollback Plan
To revert to Ollama, change `default.yaml`:
```yaml
llm:
  provider: ollama
  model: gemma3:4b
  request_timeout: 600.0
```

---

## Related Decisions
- ADR-0002: Gemma 3 4B as default model (now superseded for cloud deployment)
- ADR-0001: LlamaIndex for RAG (still applies)

## References
- [Google AI Studio](https://aistudio.google.com)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Free Tier Limits](https://ai.google.dev/pricing)
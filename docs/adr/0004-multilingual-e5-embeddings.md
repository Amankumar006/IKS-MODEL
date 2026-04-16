# ADR 0004: Use multilingual-e5-large for Embeddings

- **Date**: 2026-04-16
- **Status**: Accepted
- **Deciders**: Project Lead

## Context

We need an embedding model that can:
- Convert IKS documents into semantic vectors for retrieval
- Support multiple languages (English, Hindi, Tamil, Kannada, Sanskrit)
- Understand Devanagari and other Indic scripts
- Run locally without API costs
- Provide good retrieval accuracy

## Decision

We will use **intfloat/multilingual-e5-large** as our embedding model.

## Consequences

### Positive
- **100+ languages**: Trained on multilingual corpus including Indic languages
- **Strong performance**: State-of-the-art for multilingual retrieval
- **Local execution**: Runs on CPU/GPU via HuggingFace transformers
- **Free**: Open source model, no API costs
- **1024 dimensions**: Rich vector representations
- **LlamaIndex integration**: Works via `HuggingFaceEmbedding` class
- **Good for short text**: Optimized for sentences/paragraphs

### Negative
- **Large model**: ~1GB download, requires ~2GB RAM
- **No image embeddings**: Text-only (need CLIP for images in Phase 2)
- **Resource intensive**: Slower than smaller models on CPU
- **Not Indic-specific**: General multilingual, not optimized specifically for Indian languages

### Neutral
- Apache 2.0 license
- Available on HuggingFace Hub

## Language Support

| Language | Support Level | Notes |
|----------|---------------|-------|
| English | Excellent | Primary training data |
| Hindi | Good | Significant training data |
| Tamil | Good | Included in multilingual training |
| Kannada | Good | Included in multilingual training |
| Sanskrit | Moderate | Limited training data, but Devanagari support helps |
| Telugu | Good | Included in multilingual training |
| Malayalam | Good | Included in multilingual training |

## Alternative: IndicBERT / MuRIL

For comparison, considered but not chosen:

| Model | Strength | Why Not Chosen |
|-------|----------|----------------|
| IndicBERT (AI4Bharat) | Optimized for 12 Indic languages | Smaller community, less documentation, not generative model |
| MuRIL (Google) | Google's Indic multilingual | Not a full embedding model, just for text classification |
| LaBSE | Google's language-agnostic BERT | Good but e5 performs better on retrieval |
| all-MiniLM-L6-v2 | Fast, small | Only English, no Indic support |

**Why multilingual-e5 over IndicBERT**: Better retrieval performance, mature ecosystem, direct LlamaIndex integration.

## Implementation

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(
    model_name="intfloat/multilingual-e5-large",
    device="cpu",  # or "cuda" if GPU available
    max_length=512,
)
```

**Download Size**: ~1.2 GB
**Memory Usage**: ~2 GB RAM
**Inference Speed**: ~50-100 ms per query (CPU)

## Performance Optimization

For faster inference:
1. **GPU acceleration**: Move to CUDA if available (10x speedup)
2. **Quantization**: Use int8 quantized version (slightly lower quality, 2x faster)
3. **Caching**: Pre-compute embeddings for documents, cache query embeddings
4. **Batching**: Process multiple chunks in parallel

## Future: Image Embeddings (Phase 2)

For Phase 2 multimodal capabilities, will add:
- **CLIP** (OpenAI) or **SigLIP** (Google): For image-text alignment
- **Separate storage**: Image embeddings in different vector space
- **Cross-modal search**: "Show me Chola temple" → retrieve images

## References

- [multilingual-e5 Model Card](https://huggingface.co/intfloat/multilingual-e5-large)
- [E5 Paper](https://arxiv.org/abs/2212.03533): Text Embeddings by Weakly-Supervised Contrastive Pre-training
- [Massive Text Embedding Benchmark (MTEB)](https://huggingface.co/spaces/mteb/leaderboard): e5 ranks high on multilingual tasks
- [LlamaIndex HuggingFace Embeddings](https://docs.llamaindex.ai/en/stable/examples/embeddings/huggingface.html)

## Related Decisions

- ADR-0001: LlamaIndex (supports HuggingFace embeddings)
- Phase 2 will add CLIP/SigLIP for image embeddings

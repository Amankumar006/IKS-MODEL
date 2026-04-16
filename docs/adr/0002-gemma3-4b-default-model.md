# ADR 0002: Use Gemma 3 4B as Default Model (with Upgrade Path)

- **Date**: 2026-04-16
- **Status**: Accepted
- **Deciders**: Project Lead

## Context

The project requires a local LLM that can:
- Run on developer hardware (MacBook Pro with 16GB RAM, 4GB VRAM)
- Provide reasonable quality for IKS questions
- Support multimodal capabilities (for Phase 2)
- Be easily upgradable for users with better hardware

Initial plan assumed Gemma 3 12B, but this requires 6-7GB VRAM (4-bit) which exceeds our 4GB VRAM limit.

## Decision

We will use **Gemma 3 4B** as the default model for Phase 1, with a **model-agnostic architecture** that allows easy upgrade to 12B or 27B for users with better hardware.

## Consequences

### Positive
- **Hardware compatibility**: Works on 4GB VRAM (fits on MacBook Pro AMD Radeon Pro 5300M)
- **Fast inference**: Smaller model = faster responses
- **Lower memory**: Fits in 16GB system RAM with headroom
- **Easy deployment**: No cloud costs for initial development
- **Upgrade path**: Same code works with 12B/27B via configuration
- **Open source**: Community can use their own hardware

### Negative
- **Lower quality**: 4B model less nuanced than 12B/27B
- **Hallucination risk**: Smaller models more prone to errors
- **RAG dependency**: Heavier reliance on retrieved documents for accuracy
- **Training limitation**: Can't fine-tune 4B for Phase 2 (need 12B minimum)

### Neutral
- Requires Ollama installation
- Apache 2.0 license (permissive)

## Hardware Compatibility Matrix

| Hardware | VRAM | Usable Models | Quality |
|----------|------|---------------|---------|
| MacBook Pro (Current) | 4GB | Gemma 3 4B | Good ✅ |
| RTX 3060 Laptop | 12GB | Gemma 3 4B, 12B | Better ✅ |
| RTX 4090 Desktop | 24GB | Gemma 3 4B, 12B, 27B | Best ✅ |
| Cloud A100 | 80GB | Any model | Excellent ✅ |

## Model Configuration

Configuration via `configs/model.yaml`:

```yaml
# Default (4GB VRAM)
llm:
  provider: ollama
  model: gemma3:4b
  temperature: 0.7
  request_timeout: 120.0

# Upgrade path (12GB+ VRAM) - uncomment to use
# llm:
#   provider: ollama
#   model: gemma3:12b
#   temperature: 0.7
#   request_timeout: 120.0

# Best quality (24GB+ VRAM) - uncomment to use
# llm:
#   provider: ollama
#   model: gemma3:27b
#   temperature: 0.7
#   request_timeout: 120.0
```

## Alternatives Considered

### Alternative 1: Gemma 3 12B (Original Plan)
- **Pros**: Better quality, more capable
- **Cons**: Requires 6-7GB VRAM, doesn't fit on current hardware
- **Why rejected**: Cannot run on development machine without cloud costs
- **Resolution**: Will use 12B for Phase 2 training (cloud), keep 4B for Phase 1

### Alternative 2: Mistral 7B
- **Pros**: Popular, good quality
- **Cons**: Still requires 6+ GB VRAM for 4-bit
- **Why rejected**: Same VRAM issue as 12B models

### Alternative 3: Phi-3 Mini (3.8B)
- **Pros**: Similar size to Gemma 3 4B
- **Cons**: Less multimodal support, newer (less tested)
- **Why rejected**: Gemma 3 has better multimodal capabilities for Phase 2

### Alternative 4: Cloud API Only (OpenAI/Gemini)
- **Pros**: No hardware constraints, best quality
- **Cons**: Costs money, not offline, privacy concerns
- **Why rejected**: Core requirement is local/offline capability for institutional use

## Implementation Notes

1. **Model-agnostic wrapper**: Create `LLMWrapper` class that accepts any Ollama model name
2. **Configuration-driven**: Model selection in YAML, not hardcoded
3. **Hardware detection**: Optionally detect VRAM and recommend model
4. **Testing**: Test with both 4B and 12B (on cloud) to ensure compatibility
5. **Documentation**: Clear upgrade instructions in README

## References

- [Gemma 3 Model Card](https://ai.google.dev/gemma)
- [Ollama Library](https://ollama.com/library/gemma3)
- [Gemma 3 Technical Report](https://storage.googleapis.com/deepmind-media/gemma/gemma-3-report.pdf)
- VRAM requirements based on 4-bit quantization (GGUF format via Ollama)

## Related Decisions

- ADR-0001: Use LlamaIndex (supports any Ollama model)
- Phase 2 will use Gemma 3 12B (cloud training) regardless of Phase 1 model

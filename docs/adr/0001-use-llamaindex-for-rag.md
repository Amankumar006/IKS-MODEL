# ADR 0001: Use LlamaIndex for RAG Orchestration

- **Date**: 2026-04-16
- **Status**: Accepted
- **Deciders**: Project Lead

## Context

We need a framework to build the Retrieval-Augmented Generation (RAG) system for Phase 1. The framework should:
- Support document loading (PDF, HTML, TXT)
- Handle embeddings and vector storage
- Integrate with Ollama for local LLM inference
- Be easy to use and well-documented
- Support source citations

## Decision

We will use **LlamaIndex** as our RAG orchestration framework.

## Consequences

### Positive
- **Purpose-built for RAG**: LlamaIndex is specifically designed for document Q&A use cases
- **Less boilerplate**: Requires significantly less code than alternatives for common tasks
- **Better defaults**: Optimized default configurations for retrieval and generation
- **Native multimodal**: Built-in support for images, documents, and text
- **Excellent documentation**: Comprehensive guides and examples
- **Active community**: Large user base, frequent updates
- **Ollama integration**: First-class support for local LLMs via Ollama

### Negative
- **Smaller ecosystem**: Fewer integrations compared to LangChain (though sufficient for our needs)
- **Less flexibility**: More opinionated, which can limit customization
- **Learning curve**: Different mental model from standard ML pipelines

### Neutral
- Uses Python (same as rest of stack)
- MIT licensed (permissive)

## Alternatives Considered

### Alternative 1: LangChain
- **Pros**: Huge ecosystem, most tutorials, very flexible, LangGraph for complex flows
- **Cons**: More boilerplate code, requires manual wiring for multimodal RAG, can be overwhelming
- **Why rejected**: Overkill for our use case. LlamaIndex's opinionated approach is actually a benefit for our timeline (3 weeks for Phase 1).

### Alternative 2: Haystack
- **Pros**: Production-focused, good for enterprise
- **Cons**: Steeper learning curve, heavier framework
- **Why rejected**: More suited for large-scale production; LlamaIndex is faster to prototype with.

### Alternative 3: Custom Implementation
- **Pros**: Full control, no dependencies
- **Cons**: Significant development time, maintenance burden
- **Why rejected**: Unnecessary for Phase 1. Would delay project by weeks.

## Implementation Notes

- Core components: `VectorStoreIndex`, `SimpleDirectoryReader`, `Ollama` LLM wrapper
- Use `ServiceContext` for configuration
- Leverage built-in chunking strategies (TokenTextSplitter)
- Enable source node retrieval for citations: `index.as_query_engine(retrieve_mode="embedding", response_mode="compact")`

## References

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Comparison: LlamaIndex vs LangChain](https://docs.llamaindex.ai/en/stable/getting_started/concepts.html)
- [RAG Pipeline with LlamaIndex](https://docs.llamaindex.ai/en/stable/understanding/using_llms/using_llms.html)

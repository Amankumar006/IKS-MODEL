# CLAUDE.md - IKS AI Assistant

**Context for Claude Code**: This file helps Claude understand the project context and conventions.

> **Note**: For universal AI context, see `AGENTS.md`. For code conventions, see `docs/ai-context/conventions.md`.

---

## Project Overview

**Name**: IKS AI Assistant  
**Purpose**: Specialized AI for Indian Knowledge Systems (temples, music, dance, textiles, math, philosophy)  
**Target Users**: VTU students, researchers, cultural institutions  
**Current Phase**: Phase 1 (RAG Foundation)  

---

## Architecture Decisions

### 1. Why LlamaIndex over LangChain?
- **Decision**: Use LlamaIndex for RAG orchestration
- **Rationale**: Purpose-built for document Q&A, less boilerplate, better defaults
- **See**: ADR-0001

### 2. Why Google Gemini over Local Ollama?
- **Decision**: Default to Google Gemini API
- **Rationale**: Faster inference (2-3s vs 5-10m on CPU), free tier handles current limits, multimodal capabilities.
- **See**: ADR-0005

### 3. Why ChromaDB (Phase 1)?
- **Decision**: Use ChromaDB for Phase 1
- **Rationale**: Zero-config, runs locally, pure Python
- **Future**: Migrate to Qdrant for Phase 2 (scalability)
- **See**: ADR-0003

### 4. Why multilingual-e5 embeddings?
- **Decision**: Use intfloat/multilingual-e5-large
- **Rationale**: 100+ languages including Hindi, Tamil, Kannada, Sanskrit
- **See**: ADR-0004

---

## Project Structure

```
IKS-MODEL/
├── src/
│   ├── iks_rag/              # Phase 1: RAG system
│   │   ├── ingestion/        # Document loading
│   │   ├── retrieval/        # Embeddings, vector store
│   │   ├── generation/       # LLM, prompts
│   │   └── ui/               # Gradio interface
│   └── iks_common/             # Shared utilities
├── tests/
│   ├── unit/                 # Fast, isolated tests
│   ├── integration/            # Component tests
│   └── e2e/                  # End-to-end tests
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   └── architecture/         # System docs
├── configs/
│   └── rag/                  # Configuration files
├── data/                     # Data storage (gitignored)
└── scripts/                  # Utility scripts
```

---

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running
```bash
# Launch Gradio UI
uv run python src/iks_rag/ui/gradio_app.py

# Launch API server
uv run python src/iks_rag/api/main.py

# Run with Ollama
ollama serve  # In separate terminal
```

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test
uv run pytest tests/unit/ingestion/test_loaders.py -v
```

### Code Quality
```bash
# Linting
uv run ruff check src/

# Formatting
uv run ruff format src/

# Type checking
uv run mypy src/ --strict

# All checks
uv run ruff check src/ && uv run ruff format --check src/ && uv run mypy src/ --strict
```

---

## Code Conventions

Code conventions, testing strategies, and Git rules have been moved to [`docs/ai-context/conventions.md`](docs/ai-context/conventions.md).

---

## Model Configuration

### Default (Gemini)
```yaml
# configs/rag/default.yaml
llm:
  provider: gemini
  model: models/gemini-2.5-flash
```

### Upgrade (Ollama Local)
If you need to run entirely offline on GPU:
```yaml
# configs/rag/default.yaml
llm:
  provider: ollama
  model: mistral:7b
```

---

## Testing Strategy

### Test Pyramid
- **80% Unit Tests**: Fast, isolated, mock external dependencies
- **15% Integration Tests**: Test component interactions
- **5% E2E Tests**: Full user scenarios

### Coverage Target
- Minimum: 80%
- Optimal: 90%

### Key Test Areas
1. Document loading (PDF, TXT, MD, HTML)
2. Text chunking strategies
3. Embedding generation
4. Vector store operations
5. Query engine with citations
6. LLM integration

---

## Document Sources

Priority sources for IKS knowledge:
1. **Archive.org** - Sanskrit texts, historical documents
2. **ASI (asi.nic.in)** - Temple architecture reports
3. **IGNCA (ignca.gov.in)** - Art and cultural archives
4. **Wikimedia Commons** - Temples, dance, sculpture images
5. **Wikipedia** - Baseline coverage

See `docs/guides/data-sources.md` for complete list.

---

## Common Issues & Solutions

### Ollama Connection Error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model
ollama pull mistral:7b
```

### Out of Memory
```bash
# Use quantized or smaller models
ollama pull mistral:7b

# Or use CPU mode (slower)
# Set in configs/model.yaml: device: cpu
```

### Document Loading Fails
```bash
# Check file permissions
ls -la data/documents/

# Verify file format
file data/documents/*.pdf
```

---

## Phase Checklist

### Phase 1 (Current)
- [ ] Project structure complete
- [ ] Documentation created
- [ ] Core RAG components implemented
- [ ] Document ingestion pipeline
- [ ] Gradio UI working
- [ ] Tests passing (80%+ coverage)
- [ ] Deployed to HuggingFace Spaces

### Phase 2 (Future)
- [ ] Data collection scripts
- [ ] 18K curated dataset
- [ ] Unsloth training pipeline
- [ ] Fine-tuned model on HuggingFace Hub
- [ ] Evaluation benchmarks

### Phase 3 (Future)
- [ ] Hybrid architecture
- [ ] Multi-language support
- [ ] Cloud deployment
- [ ] Admin dashboard

---

## Related Links

- **GitHub**: https://github.com/Amankumar006/IKS-MODEL
- **Documentation**: See `docs/README.md` for full index.

---

**Last Updated**: 2026-06-15

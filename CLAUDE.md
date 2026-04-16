# CLAUDE.md - IKS AI Assistant

**Context for Claude Code**: This file helps Claude understand the project context and conventions.

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

### 2. Why Gemma 3 4B as default?
- **Decision**: Default to 4B model instead of 12B
- **Rationale**: Hardware compatibility - 4GB VRAM requirement vs 6-7GB
- **Upgrade path**: Same code works with 12B/27B via configuration
- **See**: ADR-0002

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

### Python Style
- **Formatter**: ruff
- **Linter**: ruff
- **Type Checker**: mypy (strict mode)
- **Line Length**: 100 characters
- **Docstrings**: Google style

### Import Order
```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third-party
import torch
from llama_index import VectorStoreIndex

# 3. Local
from iks_rag.config import Settings
```

### Commit Messages
Use Conventional Commits:
```
feat(ingestion): add PDF loader with OCR support
fix(retrieval): resolve ChromaDB connection timeout
docs(readme): add model configuration section
test(embedding): add multilingual-e5 unit tests
```

---

## Model Configuration

### Default (4GB VRAM)
```yaml
# configs/model.yaml
llm:
  provider: ollama
  model: gemma3:4b
  temperature: 0.7
```

### Upgrade (12GB+ VRAM)
```yaml
llm:
  provider: ollama
  model: gemma3:12b
  temperature: 0.7
```

### Alternative Models
Same code works with any Ollama model:
- `gemma3:4b`, `gemma3:12b`, `gemma3:27b`
- `llama3.1`, `mistral`, `mixtral`

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

See `docs/data-sources.md` for complete list.

---

## Common Issues & Solutions

### Ollama Connection Error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model
ollama pull gemma3:4b
```

### Out of Memory
```bash
# Use smaller model
ollama pull gemma3:4b  # Instead of 12B

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
- **HuggingFace**: (to be created)
- **Documentation**: (to be deployed)

---

**Last Updated**: 2026-04-16

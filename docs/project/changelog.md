# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project initialization with complete directory structure
- Documentation: README, CHANGELOG, CLAUDE.md, ROADMAP
- ADR framework with initial decision records
- Python package setup with pyenv + pip
- Model-agnostic configuration system (supports Ollama, OpenAI, Gemini)
- Pre-commit hooks configuration (ruff, mypy)
- CI/CD pipeline (GitHub Actions)
- Testing framework (pytest with coverage)
- Gradio web interface for IKS assistant
- Bharat persona system prompt with 9 rasas framework
- Document loaders (PDF, TXT, MD, HTML, JSON)
- ChromaDB vector store integration
- Multilingual-e5-large embeddings (100+ languages)
- RAG query engine with source citations

### Changed
- **LLM Provider**: Switched from Ollama → Google Gemini (FREE, fast, multimodal)
  - See ADR-0005 for rationale
  - 2-3 second responses vs 5-10 minutes on CPU
  - 1,500 free requests per day
  - Works on HuggingFace Spaces
- Default model: gemma3:4b → models/gemini-2.5-flash
- Vector DB: ChromaDB (Phase 1) with upgrade path to Qdrant (Phase 2)
  - See ADR-0003 for rationale
- Timeout: Increased from 120s to 600s for CPU inference

### Fixed
- Intel Mac compatibility issues:
  - NumPy constrained to <2.0.0 for PyTorch compatibility
  - transformers constrained to <4.42.0 for x86_64 macOS
  - sentence-transformers constrained to <4.0.0
- ChromaDB metadata format (arrays → comma-separated strings)
- pyproject.toml dependency conflicts with training extras
- Gradio 6.0 chat history format (tuples → dictionaries)

### Security
- API keys stored in .env (gitignored)
- .env.example provided for setup reference

## [0.1.0] - 2026-04-16

### Added
- Initial project conception and research
- Market analysis: gap assessment in current AI models
- Strategic planning: 3-phase approach (RAG → Fine-tuning → Production)
- Technology selection: LlamaIndex, ChromaDB, Ollama, Gemma 3
- Documentation of existing models (Krutrim-2, GPT-4, Gemini, etc.)
- RAG framework comparison and selection
- Complete implementation plan

### Research
- Identified 78% accuracy ceiling for existing models on IndQA benchmark
- Documented cultural bias in Western-trained models
- Validated market demand from VTU students
- Established cost estimates: $1,100-3,700 total project budget

---

## Session History

### Session 4 (2026-04-20)
- **Switched LLM provider from Ollama to Google Gemini**
- Added Gemini support to `llm.py` (now supports: Gemini, OpenAI, Ollama)
- Updated `default.yaml`: provider: gemini, model: models/gemini-2.5-flash
- Added dependencies: llama-index-llms-gemini, google-generativeai
- Created `.env` with GOOGLE_API_KEY placeholder
- Updated BRIDGE.md, NEXT_TASKS.md, ROADMAP.md
- Cost savings: $0 (Gemini free tier) vs OpenAI ($5 minimum)

### Session 3 (2026-04-20)
- Tested end-to-end RAG system
- Generated 4,516 embedding chunks from 286 documents
- Fixed timeout issues for CPU inference
- Launched Gradio UI successfully
- Response time: 5-10 minutes per query on Intel Mac CPU

### Session 2 (2026-04-20)
- Integrated 281 collected IKS documents into `data/documents/`
- Created Bharat persona system prompt (183 lines, 9 rasas framework)
- Increased timeout from 120s to 300s
- Cleared ChromaDB for fresh rebuild
- Fixed pyproject.toml dependency conflicts
- Installed uv package manager

### Session 1 (2026-04-16)
- Project initialization
- Directory structure creation
- Documentation framework setup
- ADR decisions documented

---

## Release Notes Template (for future releases)

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Security improvements
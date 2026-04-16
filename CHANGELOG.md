# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project initialization with complete directory structure
- Documentation: README, CHANGELOG, CLAUDE.md, ROADMAP
- ADR framework with initial decision records
- Python package setup with uv
- Model-agnostic configuration system (supports Gemma 3 4B/12B/27B)
- Pre-commit hooks configuration (ruff, mypy)
- CI/CD pipeline (GitHub Actions)
- Testing framework (pytest with coverage)

### Changed
- Default model: Gemma 3 4B (was 12B in initial plan) to support 4GB VRAM hardware
  - See ADR-0002 for rationale
- Vector DB: ChromaDB (Phase 1) with upgrade path to Qdrant (Phase 2)
  - See ADR-0003 for rationale

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

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

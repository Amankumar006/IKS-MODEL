# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Rebuilt IKS V2 Dataset with 15,000 instruction-response pairs and new 70/15/10/3/2 blend ratio.
- Permanent regression test suite in `scripts/verify_audit.py` for automated data quality checking.
- Hugging Face dataset uploader helper script (`scripts/data/upload_dataset.py`).
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
- Replaced Mistral 7B target pipeline references and configuration from legacy V1 settings.
- Upgraded `iks_v2_dataset_builder.py` to include deduplication, capping, and group-wise target sampling.
- **SFT Model Fine-Tuning**: Pivoted fine-tuning architecture from Gemma 3 (12B/4B) to Mistral 7B.
  - Mistral 7B natively runs in float16 precision, bypassing float32 upcasting on older hardware (T4 GPUs) which caused memory exhaustion and CUDA OOM crashes.
  - Configured Unsloth SFT pipeline with custom PyArrow data parsing and single GPU binding.
  - Upload checkpoints to Hugging Face private repository (`iks-mistral-7b-checkpoints`).
  - Updated RAG local fallback recommendations to `mistral:7b`.
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
- Cleaned 758 first-person memory hallucinations from GPT responses in Dataset A.
- Removed 109 fabricated parenthetical citations from Dataset D and fixed formatting/punctuation.
- Replaced anachronistic "zero-gravity" and "gurutvakarshan" references with historically precise "ākarṣaṇa-śakti".
- Corrected Aryabhata heliocentrism overclaims to axial rotation.
- Fixed garbled find-replace artifacts, double commas, and duplicate "the the" typos.
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

### Session 6 (2026-06-20)
- **Training Script — Template Alignment (Critical Fix)**:
  - Replaced the hand-rolled `<s>[INST]...[/INST]</s>` string with `tokenizer.apply_chat_template()` in both `scripts/train/unsloth_finetune.py` and `docs/guides/kaggle_training_notebook.md`.
  - This eliminates the risk of silent formatting drift from the GGUF tokenizer metadata — the root cause of V1's infinite-generation / self-dialogue hallucination bug.
  - Added a pre-flight decode block that prints `repr()` of the first 3 formatted examples so EOS and control tokens can be visually confirmed before launching the full Kaggle job.
- **Training Script — Sequence Length & LoRA Upgrade**:
  - Increased `MAX_SEQ_LENGTH` from `1024` to `2048`. The `SYSTEM_PROMPT_V2` is ~1,233 tokens; a 1,024 budget truncated every single training example mid-system-prompt.
  - Increased LoRA rank from `r=16` to `r=32` and alpha from `16` to `64` to give the adapter more capacity to absorb the denser, more stylistically varied V2 dataset.
- **Documentation Sync**:
  - Updated `README.md` hyperparameters table to reflect the new `r=32`, `alpha=64`, `max_seq_length=2048` values.
  - Added ADR-0007 documenting the Llama 3 chat template mismatch root-cause analysis and V2 resolution strategy.
  - Updated `docs/ai-context/bridge.md` and `docs/project/next-tasks.md` to reflect V2 data-prep completion and upcoming training run.

### Session 5 (2026-06-20)
- **Completed IKS V2 Dataset Rebuilding and Quality Hotfixes**:
  - Rebuilt V2 dataset of 15,000 instruction-response pairs (A=10,500, B=2,250, C=1,500, D=450, E=300).
  - Cleaned all 109 parenthetical citations (e.g. `(Rao, 2013)`) and performed post-processing grammar checks to clean punctuation spacing.
  - Rewrote 758 occurrences of first-person memories to third-person objective narratives.
  - Refined gravity references to use historically precise terms like `ākarṣaṇa-śakti` (attractive force) and corrected Aryabhata's heliocentrism claims to axial rotation.
  - Fixed find-replace corruption in Line 14697 and cleaned 26 "the the" typos and 11 double commas.
- **Implemented Permanent Regression Checks**: Modified `scripts/verify_audit.py` to ensure 0 citations, 0 zero-gravity claims, 0 Aryabhata-Brahmasphuta mixups, and 0 duplicate prompt-response pairs.
- **Added Hugging Face Uploader**: Created `scripts/data/upload_dataset.py` to upload the cleaned V2 dataset to HF Hub.


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
# Roadmap - IKS AI Assistant

## Project Timeline

```
2026-Q2                    2026-Q3                    2026-Q4
|                          |                          |
Week 1-3                   Month 2-4                  Month 5-6
[██████████]               [███░░░░░░░░░░░░░]         [░░░░░░░░░░░░]

Phase 1: RAG                Phase 2: Fine-tuning       Phase 3: Production
Foundation (100% done)      Domain-specific (WIP)      Comprehensive
```

---

## Phase 1: RAG Foundation [100% COMPLETE]

**Timeline**: Weeks 1-3 (April 2026)  
**Budget**: $0  
**Goal**: Working RAG system that answers IKS questions from curated documents  
**Status**: ✅ 100% Complete & Deployed

### Week 1: Project Setup & Core Infrastructure

#### Day 1-2: Repository Initialization
- [x] Create complete directory structure
- [x] Write README.md
- [x] Write CHANGELOG.md
- [x] Write CLAUDE.md
- [x] Write ROADMAP.md
- [x] Create ADR framework
- [x] Initialize git repository
- [x] Set up Python environment (pyenv + pip)
- [x] Create pyproject.toml

#### Day 3-4: Document Pipeline
- [x] Implement PDF loader with pypdf
- [x] Implement Markdown/TXT loader
- [x] Implement HTML loader with BeautifulSoup
- [x] Create semantic chunker (512 tokens, 50 overlap)
- [x] Add text cleaning and normalization

#### Day 5-7: LLM Integration & Query Engine
- [x] Install LLM support (Ollama → **Switched to Google Gemini**)
- [x] Create model-agnostic LLM wrapper (supports Ollama, OpenAI, Gemini)
- [x] Implement ChromaDB vector store
- [x] Configure multilingual-e5 embeddings
- [x] Create LlamaIndex query engine
- [x] Add source citation formatting
- [x] Integration tests

### Week 2: Knowledge Base & Testing

#### Document Collection
- [x] Natya Shastra (complete translation) - dance theory
- [x] 72 Melakarta Ragas database - Carnatic music
- [x] Chola Temple Architecture (ASI documents)
- [x] Aryabhatiya (mathematics sections)
- [x] Arthashastra (governance)
- [x] Charaka Samhita fundamentals (Ayurveda)
- [x] Upanishads (Isha, Kena, Katha)
- [x] Temple architecture styles (Nagara, Dravidian, Vesara)
- [x] **286 total documents** collected and processed
- [x] **4,516 chunks** embedded and cached

#### Day 8-10: Indexing & Evaluation
- [x] Create document indexing pipeline
- [x] Add metadata extraction (source, page, category)
- [x] Create evaluation question set
- [x] Test retrieval accuracy (target: 90%+) — **Working**
- [x] Benchmark query latency (target: <5s) — **2-3s with Gemini**
- [x] Document performance metrics

#### Day 11-14: Gradio Interface
- [x] Create chat interface with history
- [x] Add source citation display
- [x] Create example question buttons
- [x] Add IKS-themed styling
- [x] Mobile-responsive design

### Week 3: Deployment & Documentation
- [x] API documentation (FastAPI/OpenAPI)
- [x] Complete README with setup instructions
- [x] Create CONTRIBUTING.md
- [x] **HuggingFace Spaces deployment**
- [x] Collect initial user feedback
- [x] Create GitHub release v0.1.0

### Phase 1 Success Criteria

| Criteria | Target | Status |
|----------|--------|--------|
| Document corpus | 20-30 docs | ✅ 286 docs |
| Retrieval accuracy | 90%+ | ✅ Working |
| Response time | <5s | ✅ 2-3s (Gemini) |
| Source citations | 100% | ✅ Working |
| Hallucination rate | <5% | ✅ Low |
| Deployed URL | Live | ✅ [Deployed](https://huggingface.co/spaces/006aman/IKS) |

---

## Phase 2: Domain-Specific Fine-Tuning & Evaluation [IN PROGRESS]

**Timeline**: Months 2-4 (May-July 2026)  
**Goal**: Fine-tune Mistral 7B on curated IKS data to inject the "World Gateway / Bharat" persona with robust instruction following.
**Status**: 🔄 V2 Dataset construction and validation complete. Preparing V2 model training.

### Version Roadmap
- **V2**: Restore instruction-following without losing persona (5-dataset blend, invitation softening, multi-turn unpacking, 150-prompt regression benchmark).
- **V2.1**: Reduce hallucinations through curated factual data + refusal training.
- **V2.5**: Adaptive style modes (Guide, Scholar, Companion) + Civilization Lens (multi-perspective outputs).
- **V3**: Knowledge reliability — RAG grounding, citations, primary Indian text retrieval.
- **V4**: Multilingual — Sanskrit, Hindi, Tamil, Telugu, Kannada, Bengali.

### Week 4: V2 Dataset Builder & Validation
- [x] Write `iks_system_prompt.py` incorporating `SYSTEM_PROMPT_V2` (stopping rule, modes).
- [x] Implement `iks_v2_dataset_builder.py` to compile the 14,915-sample 5-dataset blend.
- [x] Create 150-prompt regression benchmark `data/eval/v2_regression_tests.jsonl` with strict success criteria.
- [x] Dry-run and validate dataset composition ratios and structure.

### Week 5: V2 Model SFT & Testing
- [ ] Spin up Kaggle/RunPod environment for V2 training (1 epoch, max_seq_length=1024, prompt formatting).
- [ ] Perform SFT on Mistral 7B using the V2 dataset.
- [ ] Run the regression benchmark on Bharat V2 to verify prompt compliance and lack of cultural bleed.

---

## Phase 3: Hybrid Architecture & Knowledge Calibration [PLANNED]

**Timeline**: Months 5-6 (August-September 2026)  
**Goal**: Implement the Document Validation Layer, multi-perspective Civilization Lens, and hybrid RAG routing.

### 🏛️ Document Validation Layer
We introduce a metadata validation layer for our 286-document corpus, tagging each source with:
- Source Name
- Author
- Century / Era
- Region
- Tradition
- Confidence Level (`Evidence: Strong`, `Evidence: Moderate`, `Traditional Account`, etc.)

This metadata allows Bharat to cite sources with historical and geographical specificity.

### 🔄 Hybrid RAG Routing
A query classifier routes queries:
- **Direct/Companion mode**: Generic/utility prompts bypass retrieval to avoid cultural bleed.
- **Hybrid/Scholar mode**: IKS prompts retrieve verified context from ChromaDB, injecting it into Bharat's system prompt for high-fidelity responses.

---

## Current Status Summary

| Phase | Status | Progress |
|-------|--------|----------|
| **Phase 1: RAG** | 🟢 100% complete | Deployed |
| **Phase 2: Fine-tune (V2)** | 🔄 In Progress | V2 Dataset built; Regression benchmark ready |
| **Phase 3: Hybrid (V3)** | ⏳ Planned | Document tagging script and routing |

### Immediate Next Steps

1. Commit and push Phase 1 and Phase 2 prep changes to GitHub.
2. Tag the 286-document corpus using `scripts/data/tag_documents.py`.
3. Train the Bharat V2 model.

---

**Last Updated**: Phase 2.5 (IKS-Bharat V2 Spec)
**Next Review**: After Bharat V2 Model training and regression evaluation.
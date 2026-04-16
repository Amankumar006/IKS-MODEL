# Roadmap - IKS AI Assistant

## Project Timeline

```
2026-Q2                    2026-Q3                    2026-Q4
|                          |                          |
Week 1-3                   Month 2-4                  Month 5-6
[████████]                 [████████████████]         [████████████]

Phase 1: RAG                Phase 2: Fine-tuning       Phase 3: Production
Foundation                  Domain-specific            Comprehensive
```

---

## Phase 1: RAG Foundation [IN PROGRESS]

**Timeline**: Weeks 1-3 (April 2026)  
**Budget**: $0  
**Goal**: Working RAG system that answers IKS questions from curated documents

### Week 1: Project Setup & Core Infrastructure

#### Day 1-2: Repository Initialization
- [x] Create complete directory structure
- [x] Write README.md
- [x] Write CHANGELOG.md
- [x] Write CLAUDE.md
- [x] Write ROADMAP.md
- [x] Create ADR framework
- [ ] Initialize git repository
- [ ] Set up uv Python environment
- [ ] Create pyproject.toml

#### Day 3-4: Document Pipeline
- [ ] Implement PDF loader with PyPDF2
- [ ] Implement Markdown/TXT loader
- [ ] Implement HTML loader with BeautifulSoup
- [ ] Create semantic chunker (512 tokens, 20 overlap)
- [ ] Add text cleaning and normalization
- [ ] Unit tests for all loaders

#### Day 5-7: LLM Integration & Query Engine
- [ ] Install Ollama and pull Gemma 3 4B
- [ ] Create model-agnostic LLM wrapper
- [ ] Implement ChromaDB vector store
- [ ] Configure multilingual-e5 embeddings
- [ ] Create LlamaIndex query engine
- [ ] Add source citation formatting
- [ ] Integration tests

### Week 2: Knowledge Base & Testing

#### Document Collection
Priority documents to collect:
1. [ ] Natya Shastra (complete translation) - dance theory
2. [ ] 72 Melakarta Ragas database - Carnatic music
3. [ ] Chola Temple Architecture (ASI documents)
4. [ ] Aryabhatiya (mathematics sections)
5. [ ] Arthashastra (governance)
6. [ ] Charaka Samhita fundamentals (Ayurveda)
7. [ ] Upanishads (Isha, Kena, Katha)
8. [ ] Temple architecture styles (Nagara, Dravidian, Vesara)

Target: 20-30 high-quality documents covering all 3 VTU IKS units.

#### Day 8-10: Indexing & Evaluation
- [ ] Create document indexing pipeline
- [ ] Add metadata extraction (source, page, category)
- [ ] Create evaluation question set (50 VTU-style questions)
- [ ] Test retrieval accuracy (target: 90%+)
- [ ] Benchmark query latency (target: <5s)
- [ ] Document performance metrics

#### Day 11-14: Gradio Interface
- [ ] Create chat interface with history
- [ ] Add source citation display
- [ ] Create example question buttons
- [ ] Add IKS-themed styling
- [ ] Mobile-responsive design
- [ ] User feedback collection

### Week 3: Deployment & Documentation

- [ ] API documentation (FastAPI/OpenAPI)
- [ ] Complete README with setup instructions
- [ ] Create CONTRIBUTING.md
- [ ] Docker containerization
- [ ] HuggingFace Spaces deployment
- [ ] Collect initial user feedback
- [ ] Create GitHub release v0.1.0

### Phase 1 Success Criteria
- [ ] 85%+ accuracy on 50 VTU questions
- [ ] 100% source citation coverage
- [ ] <5s average response time
- [ ] <5% hallucination rate
- [ ] Deployed and accessible URL
- [ ] 80%+ test coverage

---

## Phase 2: Domain-Specific Fine-Tuning [PLANNED]

**Timeline**: Months 2-4 (May-July 2026)  
**Budget**: $600-2200 (training + expert curation)  
**Goal**: Fine-tune Gemma 3 12B on curated IKS data

### Month 2: Data Collection & Curation

#### Data Collection Pipeline
- [ ] Build Wikimedia Commons scraper
- [ ] Build Archive.org downloader
- [ ] Build ASI data extractor
- [ ] Build IGNCA archive connector
- [ ] Download 5,000+ images
- [ ] Download 10,000+ text documents

#### Data Curation
Target dataset: 18,000 examples
- [ ] 15,000 text instruction-response pairs
- [ ] 3,000 multimodal (image + question + answer)

Data distribution:
- [ ] Temples & Architecture: 60% (10,800 examples)
- [ ] Music & Dance: 15% (2,700)
- [ ] Textiles & Crafts: 10% (1,800)
- [ ] Mathematics & History: 10% (1,800)
- [ ] Ayurveda & Philosophy: 5% (900)

#### Expert Review
- [ ] Hire temple architecture expert (Art historian)
- [ ] Hire music/dance expert (Musicologist)
- [ ] Hire textiles expert (Textile conservator)
- [ ] Review and validate data quality
- [ ] Budget: $500-1500

### Month 3: Training Infrastructure

#### Environment Setup
- [ ] Set up RunPod/Lambda Labs account
- [ ] Configure A100 80GB GPU
- [ ] Install Unsloth and dependencies
- [ ] Set up Weights & Biases tracking
- [ ] Create training configuration YAML

#### Training
- [ ] Prepare dataset in Gemma 3 format
- [ ] Run baseline training (LoRA r=8)
- [ ] Run full training (LoRA r=16)
- [ ] Monitor with W&B
- [ ] Save checkpoints every 100 steps

**Training Configuration**:
```yaml
model: unsloth/gemma-3-12b-it-bnb-4bit
lora:
  r: 16
  alpha: 32
  dropout: 0.05
training:
  epochs: 3
  batch_size: 2
  grad_accumulation: 4
  lr: 2e-4
  warmup_steps: 50
```

**Estimated Cost**: ~$35 (15 hours on A100)

### Month 4: Evaluation & Iteration

#### Evaluation Benchmark
- [ ] Create IKS-specific test set (500 questions)
- [ ] Compare against baseline Gemma 3
- [ ] Compare against Krutrim-2 API
- [ ] Compare against GPT-4
- [ ] Measure BLEU score vs reference answers
- [ ] Visual recognition accuracy (85%+ on temple images)
- [ ] Hallucination rate testing

#### Metrics Target
- [ ] Accuracy: 90%+ (vs 78% Krutrim-2 baseline)
- [ ] BLEU score: >0.6
- [ ] Visual recognition: 85%+
- [ ] Hallucination rate: <5%

#### A/B Testing
- [ ] Deploy fine-tuned model
- [ ] Run alongside RAG system
- [ ] Compare on real user queries
- [ ] Analyze results
- [ ] Decision: RAG only, fine-tuned only, or hybrid?

#### Model Publication
- [ ] Upload to HuggingFace Hub
- [ ] Write model card
- [ ] Create inference examples
- [ ] Publish training dataset

### Phase 2 Success Criteria
- [ ] 18K curated dataset published to HuggingFace
- [ ] 90%+ accuracy on IKS benchmark
- [ ] Model uploaded to HuggingFace Hub
- [ ] Training cost <$50
- [ ] Inference latency <3s
- [ ] GitHub release v0.2.0

---

## Phase 3: Comprehensive Production System [PLANNED]

**Timeline**: Months 5-6 (August-September 2026)  
**Budget**: $500-1500 (infrastructure)  
**Goal**: Production deployment with enterprise features

### Month 5: Hybrid Architecture & Multi-language

#### Hybrid Architecture
```
User Query
    ↓
Router (RAG vs Fine-tuned)
    ↓
┌──────────┴──────────┐
↓                     ↓
RAG (docs)      Fine-tuned Model
(Factual)       (Visual/Context)
    ↓                     ↓
Response Fusion (weighted ensemble)
    ↓
Cited Answer
```

- [ ] Implement query router
- [ ] Build response fusion logic
- [ ] Add confidence scoring
- [ ] Optimize for different query types

#### Multi-language Support
- [ ] Sanskrit tokenization (IndicBERT)
- [ ] Hindi support
- [ ] Tamil support
- [ ] Kannada support
- [ ] Code-switching handling (Hinglish)
- [ ] Language detection

#### Infrastructure
- [ ] FastAPI with async endpoints
- [ ] Redis caching for frequent queries
- [ ] Qdrant cloud for vector DB at scale
- [ ] Docker + docker-compose
- [ ] Load testing setup

### Month 6: Deployment & Monitoring

#### Cloud Deployment
- [ ] AWS/GCP setup
- [ ] Auto-scaling configuration
- [ ] Load balancer setup
- [ ] Multiple API instances
- [ ] Cost optimization

**Infrastructure Stack**:
- Load Balancer: nginx
- API Gateway: Kong/AWS API Gateway
- Application: FastAPI + Celery
- Vector DB: Qdrant Cluster
- Cache: Redis
- File Storage: MinIO/S3
- Monitoring: Prometheus + Grafana

**Estimated Cost**: $500-1500/month

#### Admin Dashboard
- [ ] Query analytics
- [ ] Model performance metrics
- [ ] User feedback collection
- [ ] Content management
- [ ] Usage statistics
- [ ] Error monitoring

#### Security & Compliance
- [ ] API rate limiting
- [ ] Authentication (optional)
- [ ] Input sanitization
- [ ] PII detection and handling
- [ ] Security audit

### Phase 3 Success Criteria
- [ ] 99.9% uptime
- [ ] <2s p95 response time
- [ ] 1000+ concurrent users supported
- [ ] Multi-language support (5+ Indic languages)
- [ ] Published research/API documentation
- [ ] GitHub release v1.0.0

---

## Future Enhancements (Post v1.0)

### Short Term (v1.1 - v1.2)
- [ ] Voice input/output (Whisper + TTS)
- [ ] Mobile app (React Native/Flutter)
- [ ] Browser extension
- [ ] Additional domains (Yoga, Meditation, Astronomy)

### Medium Term (v2.0)
- [ ] Multimodal fine-tuning (Krutrim-2 base)
- [ ] Real-time collaboration features
- [ ] Institutional dashboard
- [ ] White-label solution

### Long Term (v3.0)
- [ ] AGI-level IKS understanding
- [ ] Virtual reality temple tours
- [ ] AI-generated educational content
- [ ] Global cultural heritage expansion

---

## Dependencies & Blockers

### Phase 1 Dependencies
- [x] Research complete
- [ ] Ollama installed locally
- [ ] Document sources accessible

### Phase 2 Dependencies
- Phase 1 complete and validated
- Cloud GPU budget approved
- Expert curators contracted
- Dataset quality validated

### Phase 3 Dependencies
- Phase 2 model performing >90% accuracy
- Cloud infrastructure budget
- Deployment platform chosen

### Potential Blockers
- **GPU availability**: Backup: Colab free tier, apply for HF grants
- **Expert availability**: Backup: Partner with universities
- **Data licensing**: Ensure CC0/CC-BY sources only

---

## Resource Allocation

### Human Resources
| Role | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| Lead Developer (you) | Full-time | Full-time | Full-time |
| ML Engineer | - | 20h/week | 10h/week |
| Domain Experts | - | 40h total | - |
| UI/UX Designer | - | - | 10h total |

### Financial Resources
| Category | Phase 1 | Phase 2 | Phase 3 | Total |
|----------|---------|---------|---------|-------|
| Infrastructure | $0 | $100-200 | $500-1500 | $600-1700 |
| Expert Curation | $0 | $500-2000 | $0 | $500-2000 |
| Software | $0 | $0 | $0 | $0 |
| **Total** | **$0** | **$600-2200** | **$500-1500** | **$1100-3700** |

---

## Key Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Phase 1: RAG MVP | Week 3 (Apr 2026) | 🚧 In Progress |
| Phase 2: Dataset Ready | Month 2 (May 2026) | ⏳ Planned |
| Phase 2: Model Trained | Month 4 (Jul 2026) | ⏳ Planned |
| Phase 3: Production | Month 6 (Sep 2026) | ⏳ Planned |
| v1.0 Release | Sep 2026 | ⏳ Planned |

---

## How to Use This Roadmap

1. **Check current phase**: See [GitHub Projects](https://github.com/Amankumar006/IKS-MODEL/projects) for active work
2. **Track progress**: Issues labeled with `phase-1`, `phase-2`, `phase-3`
3. **Contribute**: Pick up tasks labeled `good-first-issue` or `help-wanted`
4. **Suggest changes**: Open an issue with `roadmap` label

---

**Last Updated**: 2026-04-16  
**Next Review**: Weekly during active development

# 🏛️ IKS AI Assistant

A specialized AI assistant for **Indian Knowledge Systems (IKS)** - answering questions about Indian heritage including temples, classical music, dance, textiles, mathematics, and philosophy.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## 🎯 Problem Statement

Current AI models (GPT-4, Claude, Gemini, Krutrim-2) show significant gaps in understanding Indian Knowledge Systems:
- **78% accuracy** on general IndQA benchmark (best Indian model)
- **50-60% accuracy** on niche IKS topics (temples, ragas, mudras)
- **Cultural bias** documented in Western-trained models
- **No visual understanding** of Indian art, architecture, dance

This project fills that gap with a specialized, open-source solution.

## 🚀 Quick Start

### Prerequisites

**Hardware Requirements** (Flexible):
| Setup | Hardware | Recommended Model |
|-------|----------|-------------------|
| Minimum | 16GB RAM, 4GB VRAM | `gemma3:4b` |
| Better | 32GB RAM, RTX 3060 (12GB) | `gemma3:12b` |
| Best | 64GB RAM, RTX 4090 (24GB) | `gemma3:12b` or `gemma3:27b` |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Amankumar006/IKS-MODEL.git
cd IKS-MODEL

# 2. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Install Ollama and pull model
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:4b

# 5. Download IKS documents
python scripts/data/download_sample_docs.py

# 6. Launch the assistant
uv run python src/iks_rag/ui/gradio_app.py
```

### Usage

**Web Interface** (Gradio):
```bash
# Opens at http://localhost:7860
uv run python src/iks_rag/ui/gradio_app.py
```

**API** (FastAPI):
```bash
# Opens at http://localhost:8000/docs
uv run python src/iks_rag/api/main.py
```

**Example Queries**:
- "What are the 72 Melakarta ragas in Carnatic music?"
- "Explain the architectural features of Chola temples"
- "What is the significance of Natya Shastra?"
- "Describe the difference between Nagara and Dravidian temple styles"

## 📋 Project Phases

### Phase 1: RAG Foundation ✅ [IN PROGRESS]
- [x] Project initialization
- [ ] Document ingestion pipeline
- [ ] Vector database (ChromaDB)
- [ ] Query engine with citations
- [ ] Gradio UI
- [ ] HuggingFace Spaces deployment

**Timeline**: 3 weeks | **Cost**: $0

### Phase 2: Domain Fine-Tuning ⏳ [PLANNED]
- [ ] Data collection (18K examples)
- [ ] Expert curation
- [ ] Unsloth training (Gemma 3 12B)
- [ ] Model evaluation
- [ ] HuggingFace Hub upload

**Timeline**: 2-3 months | **Cost**: $500-2000

### Phase 3: Production System ⏳ [PLANNED]
- [ ] Hybrid RAG + fine-tuned architecture
- [ ] Multi-language support (Sanskrit, Hindi, Tamil, Kannada)
- [ ] Cloud deployment
- [ ] Admin dashboard

**Timeline**: 1-2 months | **Cost**: $500-1500

See [ROADMAP.md](ROADMAP.md) for detailed timeline.

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────────────────────────────────┐
│  Retrieval (RAG)                             │
│  - ChromaDB vector store                     │
│  - multilingual-e5 embeddings                │
│  - Top-k document retrieval                  │
└─────────────────────┬─────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│  Generation (LLM)                            │
│  - Ollama + Gemma 3 (4B/12B/27B)            │
│  - Source-grounded answers                   │
│  - Citation included                         │
└─────────────────────────────────────────────┘
    ↓
Answer + Sources
```

## 🔧 Configuration

### Model Selection

Edit `configs/model.yaml` to switch models based on your hardware:

```yaml
# For 4GB VRAM (Default - Your Mac)
llm:
  provider: ollama
  model: gemma3:4b
  temperature: 0.7

# For 12GB+ VRAM (Better quality)
# llm:
#   provider: ollama
#   model: gemma3:12b
#   temperature: 0.7

# For 24GB+ VRAM (Best quality)
# llm:
#   provider: ollama
#   model: gemma3:27b
#   temperature: 0.7
```

### Document Sources

The assistant retrieves from:
- Archive.org (Sanskrit texts, historical documents)
- ASI (Archaeological Survey of India) reports
- IGNCA (Indira Gandhi National Centre for Arts) archives
- Wikimedia Commons (temples, dance images)
- Wikipedia IKS articles

See [docs/data-sources.md](docs/data-sources.md) for complete list.

## 📊 Performance

| Metric | Target | Current |
|--------|--------|---------|
| Answer Accuracy | 85%+ | TBD |
| Source Citation | 100% | TBD |
| Response Time | <5s | TBD |
| Hallucination Rate | <5% | TBD |

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test
uv run pytest tests/unit/ingestion/test_loaders.py -v
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/rag-pipeline.md)
- [Data Sources](docs/data-sources.md)
- [API Reference](docs/api-reference.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Architecture Decision Records](docs/adr/)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute**:
- Add IKS documents to the knowledge base
- Improve retrieval accuracy
- Add support for more Indian languages
- Create visual question-answering capabilities
- Domain expert review of training data

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [AI4Bharat](https://ai4bharat.iitm.ac.in/) for Indic language models
- [Ollama](https://ollama.com/) for local LLM hosting
- [LlamaIndex](https://www.llamaindex.ai/) for RAG framework
- VTU for IKS curriculum guidance
- Open source community

## 📞 Contact

- GitHub Issues: [IKS-MODEL Issues](https://github.com/Amankumar006/IKS-MODEL/issues)
- Email: 006amanraj@gmail.com

---

**Status**: Phase 1 in progress | **Last Updated**: 2026-04-16

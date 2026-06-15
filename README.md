# 🏛️ IKS AI Assistant: "Bharat" — The World's Gateway to Indian Civilization

A specialized, state-of-the-art AI assistant for **Indian Knowledge Systems (IKS)**. It acts as an immersive cultural guide named **Bharat**, explaining India's history, temples, classical music, dance, textiles, mathematics, and philosophy to a global audience with deep sensory and emotional resonance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Model: Mistral 7B](https://img.shields.io/badge/Fine--Tune-Mistral%207B-orange.svg)](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
[![Deployment: Live Space](https://img.shields.io/badge/HF%20Spaces-Live%20Demo-pink.svg)](https://huggingface.co/spaces/006aman/IKS)

---

## 🔗 Live Demo (Hugging Face Spaces)
Experience the interactive "Bharat" persona live in your browser:  
👉 **[Hugging Face Space: IKS AI Assistant](https://huggingface.co/spaces/006aman/IKS)**

---

## 🎯 The Vision: Immersive Storytelling

Most general AI assistants (like GPT-4o, Claude 3.5, or baseline Gemini) treat Indian culture as dry, textbook facts, scoring poorly on niche IKS concepts (around 50-60% accuracy). 

The **IKS AI Assistant** bridges this gap by introducing **Bharat**, a wise, storyteller persona that transforms dry academic concepts into immersive, sensory experiences.

### 🎭 Tone Comparison: Wikipedia vs. Bharat

| Topic | Standard AI Response (Wikipedia-style) | Bharat's Fine-Tuned Response |
| :--- | :--- | :--- |
| **Kanchipuram Silk Sari** | *"The Kanchipuram silk sari is a type of silk sari made in the Kanchipuram region in Tamil Nadu, India. These saris are worn as bridal & special occasion saris..."* | *"The cool, heavy whisper of silk against your skin... this is the Kanchipuram sari, woven not just with thread, but with the devotion of generations. Each gold thread catches the light like a temple spire at dawn..."* |
| **Chola Temples** | *"Chola temples are Dravidian style structures built during the Chola dynasty. They are characterized by tall pyramidal towers called vimanas..."* | *"Imagine the cool granite under your feet, the faint scent of camphor and jasmine in the air. Above you rises the stepped pyramid of the vimana, a mountain of stone reaching to touch the sky..."* |

Bharat is evaluated on four core dimensions:
*   **Knowledge**: Factually accurate, citing specific names, dates, dynasties, and places.
*   **Transport**: Evokes physical presence (e.g., feeling the stone carvings of a temple under your feet).
*   **Rasa**: Evokes the precise emotional essence of the topic (e.g., *Shanta* (tranquility) for Upanishads, *Vira* (heroism) for Mauryan battles).
*   **Bharat Voice**: Warm, culturally resonant, and welcoming—never sounding like a dry corporate chatbot.

---

## 🏗️ System Architecture

The project is structured in two parallel architectural layers:

### 📡 Phase 1: RAG Retrieval Engine (Live)
Retrieves factually grounded contexts from **286 curated texts** (~4,516 vector chunks) mapped locally via multilingual embeddings.

```mermaid
graph TD
    A[User Query] --> B[Embeddings Generation]
    B -->|intfloat/multilingual-e5-large| C[ChromaDB Vector Store]
    C -->|Retrieve Top-K Contexts| D[Persona Prompt Assembler]
    D -->|Bharat Persona Guidelines| E[Google Gemini 2.5 Flash API]
    E -->|Answer + Citations| F[Gradio Web UI / API]
```

### 🏋️ Phase 2: Domain-Specific SFT Fine-Tuning (In Progress)
Injects the storyteller persona and deep IKS knowledge directly into **Mistral 7B** using LoRA.

```mermaid
graph TD
    A[Curated IKS Docs] --> B[Data Extraction]
    B -->|Mercury-2 API Generator| C[15,001 pristine ShareGPT pairs]
    C -->|Unsloth LoRA Fine-Tuning| D[Kaggle Dual Tesla T4 / RunPod A100]
    D -->|Export LoRA Adapters| E[Fine-Tuned Mistral 7B "Bharat"]
    E -->|GGUF / Ollama Export| F[Offline Local Inference]
```

---

## 🏋️ Fine-Tuning & Model Training (SFT)

The fine-tuning pipeline is designed to bake the "Bharat" storyteller persona directly into the weights of **Mistral 7B** via Supervised Fine-Tuning (SFT).

### 📐 The Architecture Pivot: Mistral 7B
We pivoted our SFT architecture from **Gemma 3** to **Mistral 7B** due to hardware and precision constraints on Kaggle's free GPU tier (T4 GPUs):
*   **The Issue**: Tesla T4 GPUs lack native `bfloat16` precision. Unsloth had to aggressively convert Gemma 3's activations to `float32` to prevent NaN losses, which doubled the memory footprint and caused immediate CUDA Out Of Memory (OOM) crashes.
*   **The Fix**: Pivoting to `unsloth/mistral-7b-instruct-v0.3-bnb-4bit` resolved this since Mistral natively runs on standard `float16` precision on T4 cores. Under this setup, VRAM footprint drops to a highly optimal **4.35 GB**, leaving ample headroom.

### 📝 Kaggle & RunPod Fine-Tuning Guides
The exact cells, dependency fixes, and dataset configurations used to execute training are documented here:
*   🚀 **[Kaggle Notebook Fine-Tuning Guide](docs/guides/kaggle_training_notebook.md)** (Optimized for free GPU T4 x2)
*   💻 **[RunPod A100 Fine-Tuning Guide](docs/guides/runpod_setup.md)** (For high-throughput training)

### 📊 Training Hyperparameters
*   **Base Model**: `unsloth/mistral-7b-instruct-v0.3-bnb-4bit`
*   **LoRA Rank ($r$)**: `16`
*   **LoRA Alpha**: `16`
*   **Batch Size**: `2` (per device) with **Gradient Accumulation Steps**: `4` (effective batch size = 8)
*   **Optimizer**: `paged_adamw_8bit`
*   **Sequence Length**: `1024` tokens
*   **Checkpoints**: Pushed automatically every 500 steps to the private Hugging Face repository `006aman/iks-mistral-7b-checkpoints`.

---

## 🚀 Local Quick Start

### ⚙️ Prerequisites & Hardware Recommendations
The local vector store runs embeddings on CPU/CUDA, while inference defaults to Google Gemini API (Free tier). For local LLM deployment, we recommend:

| Setup | Hardware | Recommended Local Model |
| :--- | :--- | :--- |
| **Minimum** | 16GB RAM / Apple Silicon | `mistral:7b` (via Ollama) |
| **Recommended** | 32GB RAM / RTX 3060 (12GB) | `mistral:7b` (via Ollama) |
| **Extreme** | 64GB RAM / RTX 4090 (24GB) | `mistral:7b` (via Ollama) |

### 🔧 Installation

We use the ultra-fast Python package manager **`uv`** to maintain lockfile parity and speed up setups.

```bash
# 1. Clone the repository
git clone https://github.com/Amankumar006/IKS-MODEL.git
cd IKS-MODEL

# 2. Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Synchronize environment and install dependencies
uv sync

# 4. Set up environment variables
cp .env.example .env
# Edit .env and paste your GOOGLE_API_KEY (from Google AI Studio)

# 5. Download base documents
uv run python scripts/data/download_sample_docs.py

# 6. Run the local Gradio application
uv run python src/iks_rag/ui/gradio_app.py
```

Open your browser at **http://localhost:7860** to interact with Bharat.

---

## 📂 Repository Layout

```text
IKS-MODEL/
├── src/
│   ├── iks_common/       # Common shared utilities
│   └── iks_rag/          # Core RAG Retrieval Pipeline
│       ├── ingestion/    # Text & PDF loaders and classification
│       ├── retrieval/    # EmbeddingsManager & ChromaDB vector wrappers
│       ├── generation/   # LLM Wrapper (Gemini, Ollama, OpenAI) & Bharat prompts
│       └── ui/           # Gradio Web Interface
├── scripts/
│   ├── data/             # Scrapers, QA generators, and dataset validators
│   ├── eval/             # 500-question gold-standard benchmark compiler
│   └── train/            # Unsloth Mistral 7B fine-tuning scripts
├── tests/
│   ├── unit/             # Fast, mock-enabled isolated tests
│   ├── integration/      # Component integration checks
│   └── e2e/              # System-level end-to-end tests
├── configs/
│   └── rag/              # YAML configuration files
└── docs/                 # Architecture Decision Records (ADRs) and guides
```

---

## 📚 Complete Documentation Index

All details regarding project setup, design decisions, and evaluation frameworks are located in the [docs/](docs/) folder:

### 🏗️ Architecture Decision Records (ADRs)
*   [ADR 0001: Orchestration Engine (LlamaIndex)](docs/adr/0001-use-llamaindex.md)
*   [ADR 0002: Default Local LLM Model](docs/adr/0002-gemma3-4b-default-model.md)
*   [ADR 0003: Vector Store Selection (ChromaDB)](docs/adr/0003-use-chromadb.md)
*   [ADR 0004: Multilingual Embeddings Model](docs/adr/0004-multilingual-e5-embeddings.md)
*   [ADR 0005: Switch to Cloud Gemini API](docs/adr/0005-switch-to-gemini.md)
*   [ADR 0006: SFT Model Pivot to Mistral 7B](docs/adr/0006-pivot-to-mistral-7b.md) (Current fine-tuning architecture)

### 📖 Setup & Training Guides
*   [Local Quickstart Guide](docs/guides/setup.md)
*   [Kaggle T4 Fine-Tuning Guide](docs/guides/kaggle_training_notebook.md) (Mistral 7B)
*   [RunPod A100 Fine-Tuning Guide](docs/guides/runpod_setup.md)
*   [Data Sources Curation List](docs/guides/data-sources.md)
*   [Evaluation Benchmarking Framework](docs/guides/evaluation_framework.md)

### 📊 Project Management & Research
*   [Master Task Checklist](docs/project/next-tasks.md)
*   [High-Level Roadmap & Timeline](docs/project/roadmap.md)
*   [Technical Pitch Deck](docs/project/bharat_pitch_deck.md)
*   [Project Changelog](docs/project/changelog.md)
*   [Market Analysis & Core Value Gap](docs/research/comparison-value-and-gap.md)
*   [Multimodal AI Proposal](docs/research/idea.md)

---

## 📊 Project Roadmap

| Phase | Core Features | Status |
| :--- | :--- | :--- |
| **Phase 1: RAG Foundation** | curation of 286 base docs, ChromaDB + Multilingual E5 integration, Gradio UI, HuggingFace Space deploy | ✅ **100% Complete** |
| **Phase 2.1: Data Generation** | 15,001 multi-turn ShareGPT pairs generated and cleaned via Mercury-2 API | ✅ **100% Complete** |
| **Phase 2.4: Evaluation** | 500-question gold-standard benchmark compiled testing held-out texts and adversarial limits | ✅ **100% Complete** |
| **Phase 2.5: SFT Fine-Tuning** | Dual Tesla T4 Kaggle training notebook configured with W&B logging & automatic HF checkpoint backups | 🔄 **In Progress** |
| **Phase 3: Production** | Local GGUF export, hybrid routing, multi-language support (Sanskrit, Tamil, Hindi), cloud deploy | ⏳ **Planned** |

---

## 🧪 Testing and Linting

We maintain a strict quality target of **>80% test coverage**. All checks run locally via:

```bash
# Run the unit test suite
uv run pytest tests/ -v

# Run tests with HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html

# Formatting and linting checks
uv run ruff check src/
uv run ruff format src/
```

---

## 🤝 Contributing

We welcome cultural researchers, AI engineers, and historians to join our gateway initiative! 
For detailed contribution rules, code styles, and Git conventions, check out:
*   **[Code Conventions](docs/ai-context/conventions.md)**
*   **[Contributing Guidelines](docs/project/contributing.md)**

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support
*   **GitHub Issues**: [IKS-MODEL Issues Tracker](https://github.com/Amankumar006/IKS-MODEL/issues)
*   **Email**: 006amanraj@gmail.com

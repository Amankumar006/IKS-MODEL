# 🤖 AI Agent Context (Universal Entry Point)

**Hello! If you are an AI assistant (Antigravity, Cursor, GitHub Copilot, Claude Code, etc.), start here.**
This document provides the essential context and pointers to navigate the `IKS-Model` project.

---

## 🎯 Project Overview

**Name**: IKS AI Assistant ("Bharat")
**Purpose**: Specialized AI for Indian Knowledge Systems (temples, music, dance, textiles, math, philosophy)
**Target Users**: Global audiences, cultural institutions, and researchers seeking an immersive connection to Indian civilization
**Current Phase**: Phase 2.6 (V2 Dataset Complete — Awaiting V2 Training Run)

### 🤗 Deployed Models (V1 — Live with Known Bugs)
| Model | Link | Status |
|---|---|---|
| Merged 16-bit | [006aman/IKS-Mistral-7B](https://huggingface.co/006aman/IKS-Mistral-7B) | ✅ Live (V1, has bugs) |
| GGUF Q4_K_M | [006aman/IKS-Mistral-7B-GGUF](https://huggingface.co/006aman/IKS-Mistral-7B-GGUF) | ✅ Live (V1, has bugs) |
| RAG Space | [spaces/006aman/IKS](https://huggingface.co/spaces/006aman/IKS) | ✅ Live (uses Gemini, not fine-tuned model) |

> ⚠️ V1 model has a self-dialogue bug due to Llama 3 tokens on a Mistral base — see ADR-0007.
> V2 dataset is complete and training config is finalized. V2 training run is pending.

---

## 📂 Navigation Map

All project documentation lives in the `docs/` folder:

*   **[`docs/README.md`](docs/README.md)**: Index of all documentation.
*   **[`docs/ai-context/conventions.md`](docs/ai-context/conventions.md)**: Code style, linting, and Git conventions.
*   **[`docs/ai-context/bridge.md`](docs/ai-context/bridge.md)**: Session handoff doc. Shows what was just completed and what to do next.
*   **[`docs/project/next-tasks.md`](docs/project/next-tasks.md)**: Master task list. Always check this before starting work.
*   **[`docs/project/roadmap.md`](docs/project/roadmap.md)**: High-level timeline and goals.
*   **[`docs/project/v1-model-report.md`](docs/project/v1-model-report.md)**: Post-training report for V1 — training metrics, deployment, and bug inventory.
*   **[`docs/adr/0007-resolve-llama3-template-mismatch.md`](docs/adr/0007-resolve-llama3-template-mismatch.md)**: Root cause of V1's self-dialogue bug and V2 fix.
*   **[`docs/architecture/`](docs/architecture/)**: System design and RAG pipeline.
*   **[`docs/guides/`](docs/guides/)**: Setup, deployment, and data source docs.
*   **[`docs/research/`](docs/research/)**: Competitive analysis and early ideas.

---

## ⚠️ Key Architectural Notes

1.  **LLM Provider (RAG)**: We use **Google Gemini** via `llama-index-llms-gemini` for the Phase 1 RAG pipeline (switched away from Ollama).
2.  **Fine-Tuned Model (V1, deployed)**: `unsloth/mistral-7b-instruct-v0.3-bnb-4bit` — trained 5,628 steps with LoRA (r=16, alpha=16). Has template mismatch bug. See ADR-0007.
3.  **Fine-Tuned Model (V2, pending)**: Same Mistral 7B base — training config upgraded to `r=32/alpha=64`, `max_seq_length=2048`, `tokenizer.apply_chat_template()`. Dataset fully rebuilt and validated.
4.  **Vector DB**: **ChromaDB** for Phase 1.
5.  **Embeddings**: `intfloat/multilingual-e5-large` (Local CPU).
6.  **Data Source**: 286 curated documents in `data/documents/` (~4,500 vector chunks).
7.  **Environment**: Python 3.11+, managed via `uv` package manager.

---

## 🚀 Quick Commands

```bash
# Run tests
uv run pytest tests/ -v

# Start UI (RAG + Gemini)
uv run python src/iks_rag/ui/gradio_app.py

# Format and Lint
uv run ruff check src/ && uv run ruff format src/

# Run dataset regression audit
uv run python scripts/verify_audit.py

# Upload V2 dataset to HuggingFace (next step!)
uv run python scripts/data/upload_dataset.py
```

**Next step**: Read [`docs/ai-context/bridge.md`](docs/ai-context/bridge.md) for exact next actions, then [`docs/project/next-tasks.md`](docs/project/next-tasks.md) for the full task list.

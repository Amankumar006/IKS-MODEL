# 🤖 AI Agent Context (Universal Entry Point)

**Hello! If you are an AI assistant (Antigravity, Cursor, GitHub Copilot, Claude Code, etc.), start here.**
This document provides the essential context and pointers to navigate the `IKS-Model` project.

---

## 🎯 Project Overview

**Name**: IKS AI Assistant  
**Purpose**: Specialized AI for Indian Knowledge Systems (temples, music, dance, textiles, math, philosophy)  
**Target Users**: Global audiences, cultural institutions, and researchers seeking an immersive connection to Indian civilization  
**Current Phase**: Phase 2.1 (World Gateway Fine-Tuning Data Generation) - In Progress

## 📂 Navigation Map

All project documentation lives in the `docs/` folder:

*   **[`docs/README.md`](docs/README.md)**: Index of all documentation.
*   **[`docs/ai-context/conventions.md`](docs/ai-context/conventions.md)**: Code style, linting, and Git conventions.
*   **[`docs/ai-context/bridge.md`](docs/ai-context/bridge.md)**: Session handoff doc. Shows what was just completed and what to do next.
*   **[`docs/project/next-tasks.md`](docs/project/next-tasks.md)**: Master task list. Always check this before starting work.
*   **[`docs/project/roadmap.md`](docs/project/roadmap.md)**: High-level timeline and goals.
*   **[`docs/architecture/`](docs/architecture/)**: System design and RAG pipeline.
*   **[`docs/guides/`](docs/guides/)**: Setup, deployment, and data source docs.
*   **[`docs/research/`](docs/research/)**: Competitive analysis and early ideas.

## ⚠️ Key Architectural Notes

1.  **LLM Provider**: We use **Google Gemini** via `llama-index-llms-gemini` (we switched away from Ollama).
2.  **Vector DB**: **ChromaDB** for Phase 1.
3.  **Embeddings**: `intfloat/multilingual-e5-large` (Local CPU).
4.  **Data Source**: 286 curated documents in `data/documents/` (~4,500 vector chunks).
5.  **Environment**: Python 3.11+, managed via `uv` package manager.

## 🚀 Quick Commands

```bash
# Run tests
uv run pytest tests/ -v

# Start UI
uv run python src/iks_rag/ui/gradio_app.py

# Format and Lint
uv run ruff check src/ && uv run ruff format src/
```

**Next step**: Read `docs/project/next-tasks.md` to see what needs to be done.

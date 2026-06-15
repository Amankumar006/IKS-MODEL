# 📚 IKS-Model Documentation Index

Welcome to the documentation for the **IKS AI Assistant**. This project is designed as a **World Gateway** to Indian Knowledge Systems—a culturally immersive AI that uses the "Bharat" storyteller persona to explain temples, music, dance, textiles, math, and philosophy to a global audience.

**Current Phase**: Phase 2 (Mistral 7B Fine-Tuning) - Actively training the instruction dataset.

## Directory Structure

### 🧠 [`ai-context/`](ai-context/)
Context for AI assistants (like Claude, Cursor) and human developers.
*   [`conventions.md`](ai-context/conventions.md): Code style, testing, and Git conventions.
*   [`bridge.md`](ai-context/bridge.md): Handoff notes between development sessions. **Must read** when starting a new session.

### 🏗️ [`architecture/`](architecture/)
System design and data pipelines.
*   [`overview.md`](architecture/overview.md): High-level system architecture.
*   [`rag-pipeline.md`](architecture/rag-pipeline.md): Details of the Phase 1 RAG implementation.

### 📝 [`adr/`](adr/)
Architecture Decision Records.
*   Contains all major technical decisions (e.g., LlamaIndex vs LangChain, Gemini vs Ollama).

### 📘 [`guides/`](guides/)
How-to guides for developers and maintainers.
*   [`setup.md`](guides/setup.md): Local environment setup.
*   [`deployment.md`](guides/deployment.md): How to deploy to HuggingFace Spaces.
*   [`data-sources.md`](guides/data-sources.md): Where the IKS corpus comes from.
*   [`runpod_setup.md`](guides/runpod_setup.md): How to run the Phase 2 fine-tuning on an A100 GPU.

### 📋 [`project/`](project/)
Project management and tracking.
*   [`next-tasks.md`](project/next-tasks.md): The immediate to-do list.
*   [`roadmap.md`](project/roadmap.md): Long-term plan across Phases 1, 2, and 3.
*   [`changelog.md`](project/changelog.md): Release history.
*   [`contributing.md`](project/contributing.md): Guidelines for contributors.

### 🔬 [`research/`](research/)
Early ideation and competitive analysis.
*   [`idea.md`](research/idea.md): Core vision and problem statement.
*   [`comparison-value-and-gap.md`](research/comparison-value-and-gap.md): Why current AIs fail at IKS.
*   [`indian-ai-landscape.html`](research/indian-ai-landscape.html) & [`rag-frameworks-comparison.html`](research/rag-frameworks-comparison.html): Visual comparisons.

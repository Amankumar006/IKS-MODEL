# 📚 IKS-Model Documentation Index

Welcome to the documentation for the **IKS AI Assistant**. This project is designed as a **World Gateway** to Indian Knowledge Systems — a culturally immersive AI that uses the "Bharat" storyteller persona to explain temples, music, dance, textiles, math, and philosophy to a global audience.

**Current Phase**: Phase 2.6 — V2 Dataset complete, training config finalized, awaiting V2 Kaggle training run.

| Deployed Models | Link |
|---|---|
| Bharat V1 (16-bit, known bugs) | [006aman/IKS-Mistral-7B](https://huggingface.co/006aman/IKS-Mistral-7B) |
| Bharat V1 GGUF Q4_K_M | [006aman/IKS-Mistral-7B-GGUF](https://huggingface.co/006aman/IKS-Mistral-7B-GGUF) |
| RAG Space (live, Gemini-powered) | [spaces/006aman/IKS](https://huggingface.co/spaces/006aman/IKS) |

---

## Directory Structure

### 🧠 [`ai-context/`](ai-context/)
Context for AI assistants (Antigravity, Cursor, Claude Code) and human developers.
*   [`conventions.md`](ai-context/conventions.md): Code style, testing, and Git conventions.
*   [`bridge.md`](ai-context/bridge.md): Handoff notes between development sessions. **Must read** when starting a new session.

### 🏗️ [`architecture/`](architecture/)
System design and data pipelines.
*   [`overview.md`](architecture/overview.md): High-level system architecture.
*   [`rag-pipeline.md`](architecture/rag-pipeline.md): Details of the Phase 1 RAG implementation.

### 📝 [`adr/`](adr/)
Architecture Decision Records — every major technical decision with context, rationale, and outcomes.
*   [`0001-use-llamaindex-for-rag.md`](adr/0001-use-llamaindex-for-rag.md)
*   [`0002-gemma3-4b-default-model.md`](adr/0002-gemma3-4b-default-model.md)
*   [`0003-chromadb-over-qdrant.md`](adr/0003-chromadb-over-qdrant.md)
*   [`0004-multilingual-e5-embeddings.md`](adr/0004-multilingual-e5-embeddings.md)
*   [`0005-switch-to-gemini.md`](adr/0005-switch-to-gemini.md)
*   [`0006-pivot-to-mistral-7b.md`](adr/0006-pivot-to-mistral-7b.md): Pivot from Gemma 3 to Mistral 7B; includes **V1 training outcomes** and bugs discovered.
*   [`0007-resolve-llama3-template-mismatch.md`](adr/0007-resolve-llama3-template-mismatch.md): Root cause of V1's self-dialogue bug; includes the Ollama Modelfile workaround and V2 fix.

### 📘 [`guides/`](guides/)
How-to guides for developers and maintainers.
*   [`setup.md`](guides/setup.md): Local environment setup.
*   [`deployment.md`](guides/deployment.md): How to deploy to HuggingFace Spaces.
*   [`data-sources.md`](guides/data-sources.md): Where the IKS corpus comes from.
*   [`kaggle_training_notebook.md`](guides/kaggle_training_notebook.md): Cells and dependencies for T4 x2 Kaggle fine-tuning (updated for V2).
*   [`runpod_setup.md`](guides/runpod_setup.md): How to run fine-tuning on an A100 GPU.
*   [`evaluation_framework.md`](guides/evaluation_framework.md): Rubrics and code to compile the 500-question benchmark.
*   [`huggingface_model_card.md`](guides/huggingface_model_card.md): HuggingFace model card (copy to HF repo README). Documents V1 bugs and V2 improvements.

### 📋 [`project/`](project/)
Project management and tracking.
*   [`next-tasks.md`](project/next-tasks.md): The immediate to-do list.
*   [`roadmap.md`](project/roadmap.md): Long-term plan across Phases 1, 2, and 3 — **updated with V1 training completion**.
*   [`changelog.md`](project/changelog.md): Full session history including V1 training run.
*   [`v1-model-report.md`](project/v1-model-report.md): **[NEW]** Post-training report for V1 — training metrics, Kaggle infrastructure workarounds, deployment, and bug inventory.
*   [`model_specification.md`](project/model_specification.md): Engineering spec for Bharat V2 (dataset, training, evaluation criteria).
*   [`dataset-governance.md`](project/dataset-governance.md): Dataset quality rules, confidence labeling schema, and V1→V2 defect comparison.
*   [`contributing.md`](project/contributing.md): Guidelines for contributors.

### 🔬 [`research/`](research/)
Early ideation and competitive analysis.
*   [`idea.md`](research/idea.md): Core vision and problem statement.
*   [`comparison-value-and-gap.md`](research/comparison-value-and-gap.md): Why current AIs fail at IKS.

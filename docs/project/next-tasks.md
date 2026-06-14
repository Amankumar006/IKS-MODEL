# Next Tasks - IKS AI Assistant

**After completing current tasks, follow this task list in order.**
**Last updated**: Phase 2.2

---

## 🎯 Current Vision: The "World Gateway" (Bharat Persona)

**IMPORTANT**: We have pivoted away from building a VTU student exam tool. The goal is to build an immersive, culturally resonant AI that speaks with the voice of "Bharat" to a global audience.

---

## Phase 2: Domain-Specific Fine-Tuning (IN PROGRESS)

### 🔄 Task 2.1: Dataset Generation (Active)
**Status**: IN PROGRESS (Currently running in background)
**Goal**: Generate 15,000 ShareGPT instruction-tuning pairs covering sensory, philosophical, and architectural domains.
- [ ] Monitor background process: `wc -l data/curated/iks_instruction_dataset.jsonl`
- [ ] Wait for completion.
- [ ] Audit dataset for quality and "verbal tics" (e.g., repeating "Ah," too often).

### ⏳ Task 2.2: Cloud GPU Fine-Tuning (Pending)
**Status**: READY (Waiting on Task 2.1)
**Goal**: Fine-tune Gemma 3 12B using Unsloth on an A100 GPU.
- [ ] Follow `docs/guides/runpod_setup.md` to rent A100.
- [ ] Transfer `iks_instruction_dataset.jsonl` to the cloud.
- [ ] Execute `python scripts/train/unsloth_finetune.py`.
- [ ] Monitor loss curve on Weights & Biases.
- [ ] Export final model to GGUF.

### ⏳ Task 2.3: Model Evaluation
**Status**: PLANNED
**Goal**: Verify that the fine-tuned Gemma 3 model successfully holds the Bharat persona.
- [ ] Compare baseline Gemma 3 vs Fine-tuned Gemma 3.
- [ ] Test hallucination rate on specific temple/architectural queries.

---

## 📦 Archive: Phase 1 (RAG Foundation) - 100% COMPLETE

The following tasks were completed in April 2026:
- [x] Task 1: Integrate 286 IKS Documents
- [x] Task 2: Create Bharat Persona system prompt
- [x] Task 3: Fix CPU Timeouts
- [x] Task 4: Rebuild ChromaDB with 4,516 chunks
- [x] Task 5: End-to-End Local Test
- [x] Task 6: Build Gradio UI
- [x] Task 7: Switch from Ollama to Google Gemini (Free Tier)
- [x] Task 8: Deploy to HuggingFace Spaces

**Architecture Note**: The Phase 1 deployed app lives at HF Spaces and uses RAG + Gemini API. Phase 2 (this phase) will replace the Gemini API with our own fine-tuned Gemma 3 local model.
# Next Tasks - IKS AI Assistant

**After completing current tasks, follow this task list in order.**
**Last updated**: Phase 2.5 (Mistral 7B SFT Handoff)

---

## 🎯 Current Vision: The "World Gateway" (Bharat Persona)

**IMPORTANT**: The goal is to build an immersive, culturally resonant AI that speaks with the voice of "Bharat" to a global audience, rather than a dry academic exam helper.

---

## Phase 2: Domain-Specific Fine-Tuning (IN PROGRESS)

### ✅ Task 2.1: Dataset Generation
**Status**: 100% COMPLETE
- Successfully generated, cleaned, and validated exactly 15,001 ShareGPT pairs in `data/curated/iks_instruction_dataset.jsonl`.

### 🔄 Task 2.2: Cloud GPU Fine-Tuning (Mistral 7B)
**Status**: IN PROGRESS / EXECUTED ON KAGGLE
- [x] Pivot architecture from Gemma 3 to Mistral 7B to support float16 on Kaggle T4 GPUs.
- [x] Integrate custom dataset schema cleaner to bypass PyArrow crash.
- [x] Apply Kaggle T4 VRAM hacks (`CUDA_VISIBLE_DEVICES="0"`, `expandable_segments:True`, `max_seq_length=512`).
- [x] Resolve `SFTConfig` PicklingError and Transformers 5.5.0 average tokens bugs.
- [ ] Monitor and verify W&B loss curve convergence for `mistral-7b-run-1`.
- [ ] Confirm LoRA adapter checkpoints are uploaded to Hugging Face `iks-mistral-7b-checkpoints` repository.

### ⏳ Task 2.3: Model Evaluation & Testing
**Status**: PLANNED
- [ ] Set up local inference script loading the Mistral 7B base model and merging the fine-tuned LoRA adapters.
- [ ] Run the compiled 500-question benchmark (`data/eval/iks_benchmark_gold.json`).
- [ ] Evaluate responses using the LLM-as-a-judge rubric on the 4 dimensions: Knowledge, Transport, Rasa, and Bharat Voice.
- [ ] Compare fine-tuned model against baseline Mistral 7B.

### ⏳ Task 2.4: Multimodal Data Collection
**Status**: PLANNED
- [ ] Collect 3,000 temple architecture and Indian classical art images for vision tuning.

---

## 📦 Archive: Phase 1 (RAG Foundation) - 100% COMPLETE

The following tasks were completed in April 2026:
- [x] Integrate 286 IKS Documents
- [x] Create Bharat Persona system prompt
- [x] Fix CPU Timeouts
- [x] Rebuild ChromaDB with 4,516 chunks
- [x] End-to-End Local Test
- [x] Build Gradio UI
- [x] Switch from Ollama to Google Gemini (Free Tier)
- [x] Deploy to HuggingFace Spaces
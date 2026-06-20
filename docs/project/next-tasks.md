# Next Tasks - IKS AI Assistant

**After completing current tasks, follow this task list in order.**
**Last updated**: Phase 2.5 (IKS V2 Dataset Rebuild & Hotfixes)

---

## 🎯 Current Vision: The "World Gateway" (Bharat Persona)

**IMPORTANT**: The goal is to build an immersive, culturally resonant AI that speaks with the voice of "Bharat" to a global audience, rather than a dry academic exam helper.

---

## Phase 2: Domain-Specific Fine-Tuning (IN PROGRESS)

### ✅ Task 2.1: Dataset Generation
**Status**: 100% COMPLETE
- Successfully generated, cleaned, and validated exactly 15,000 ShareGPT pairs in `data/curated/iks_v2_instruction_dataset.jsonl`.

### 🔄 Task 2.2: Cloud GPU Fine-Tuning (Mistral 7B V1)
**Status**: IN PROGRESS / EXECUTED ON KAGGLE
- [x] Pivot architecture from Gemma 3 to Mistral 7B to support float16 on Kaggle T4 GPUs.
- [x] Integrate custom dataset schema cleaner to bypass PyArrow crash.
- [x] Apply Kaggle T4 VRAM hacks (`CUDA_VISIBLE_DEVICES="0"`, `expandable_segments:True`, `max_seq_length=512`).
- [x] Resolve `SFTConfig` PicklingError and Transformers 5.5.0 average tokens bugs.
- [x] Clean up all outdated references to Gemma 3 in codebase, configurations, and documentation.
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

### ✅ Task 2.5: IKS-Bharat V2 Dataset Rebuilding & Quality Hotfixes
**Status**: 100% COMPLETE
- [x] Run `iks_v2_dataset_builder.py` to compile the 15,000-sample 5-dataset blend.
- [x] Audit and fix V1 legacy bugs: first-person memories, fabricated academic citations, zero-gravity claims, Aryabhata heliocentrism, and double-comma typos.
- [x] Build and integrate permanent regression check suite (`scripts/verify_audit.py`).
- [x] Add Hugging Face dataset uploader helper script (`scripts/data/upload_dataset.py`).

### ⏳ Task 2.6: IKS-Bharat V2 Model Fine-Tuning & Evaluation
**Status**: PLANNED / IN PREPARATION
- [ ] Upload final cleaned V2 dataset to Hugging Face Hub using `scripts/data/upload_dataset.py`.
- [ ] Train Mistral 7B with the V2 dataset on Kaggle/RunPod (1 epoch, max_seq_length=1024, SYSTEM_PROMPT_V2).
- [ ] Run the 150-prompt regression benchmark (`data/eval/v2_regression_tests.jsonl`) on fine-tuned Bharat V2.
- [ ] Verify accuracy, stopping rule adherence, and zero cultural bleed on utility tasks.

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
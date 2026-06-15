# Bridge File - IKS AI Assistant Development

**Purpose**: Continue development across platforms. Read this file to understand current state and next steps.

---

## Current Status (Phase 2.5: SFT Executed on Kaggle via Mistral 7B)

### ✅ Completed

| Task | Details |
|------|---------|
| **Phase 1: RAG Foundation** | 100% Complete. 82.95% test coverage. 40/40 Unit Tests passing locally. |
| **Mistral 7B Pivot** | Pivoted from Gemma 3 (12B/4B) to Mistral 7B because Kaggle T4 GPUs lack native bfloat16, causing Gemma to trigger float32 conversion and CUDA OOM. Mistral natively uses standard float16. |
| **Custom Data Loader** | Built a custom safe JSONL loader to strip out inconsistent metadata keys (`pr`, `words`) to avoid PyArrow schema cast errors. |
| **Kaggle Hardware Hacks** | Forced training on single T4 (`CUDA_VISIBLE_DEVICES="0"`) to stop GPU memory duplication; added `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`; throttled `max_seq_length` to 512. |
| **Library Bug Fixes** | Passed `average_tokens_across_devices=False` to fix Transformers 5.5.0 loss-to-int bug; used `SFTConfig` in `trl 0.24.0` to prevent PicklingErrors. |
| **HF & W&B Configuration** | Added `WANDB_API_KEY` to Kaggle secrets for background auth; redirected output to private `iks-mistral-7b-checkpoints` model repository. |

---

## Context for AI Assistant (Read Carefully)

1. **Project Vision**: IKS (Indian Knowledge Systems) AI assistant designed as a **World Gateway**. Immersive cultural guide persona ("Bharat").
2. **Current Focus**: SFT Fine-Tuning is actively running / completed on Kaggle using the Mistral 7B architecture. 
3. **Model Path**: Checkpoints are saved under the private repo path `iks-mistral-7b-checkpoints` on Hugging Face.

---

## Key Files Changed Recently

```text
scripts/train/unsloth_finetune.py     ← MODIFIED: Synced with Kaggle pivots (Mistral 7B, safe loader, SFTConfig).
README.md                             ← MODIFIED: Added visual Mermaid architecture and prominent HF Space link.
```

---

## How to Resume (Next Session)

1. **Check W&B**: Confirm model converged properly and training completed the 3 epochs.
2. **Check Hugging Face Hub**: Verify that `iks-mistral-7b-checkpoints` contains the saved LoRA adapter weight files.
3. **Validation (Next)**: Perform local inference or Gradio integration tests with the new LoRA adapters.
4. **Multimodal Phase (Next)**: Begin Temple architecture image collection for vision fine-tuning.

---

## Project Phase Tracker

| Phase | Status | Tasks |
|-------|--------|-------|
| **Phase 1: RAG Foundation** | ✅ 100% | Deployed on HF Spaces; 82.95% Test Coverage |
| **Phase 2: Fine-tuning** | 🔄 In Progress | Mistral 7B SFT training executed on Kaggle |
| **Phase 3: Production** | ⏳ Not Started | Hybrid arch, multi-lang, cloud deploy |

---

**File last updated**: Phase 2.5 (Kaggle Mistral 7B Handoff)
**Next milestone**: Verify convergence of Mistral 7B adapter and start local validation.
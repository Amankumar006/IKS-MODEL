# Bridge File - IKS AI Assistant Development

**Purpose**: Continue development across platforms. Read this file to understand current state and next steps.

---

## Current Status (Phase 2.6: Training Config Complete — Ready to Launch)

### ✅ Completed

| Task | Details |
|------|---------|
| **Phase 1: RAG Foundation** | 100% Complete. 82.95% test coverage. 40/40 Unit Tests passing locally. |
| **IKS V2 Dataset Builder** | Completed `iks_v2_dataset_builder.py` with multi-turn unpacking, 15,000 exact instruction-response pairs, and target blends (A=10,500, B=2,250, C=1,500, D=450, E=300). |
| **Quality Hotfixes & Audit** | Surgically resolved legacy V1 bugs in the V2 dataset: rewrote 758 first-person memory hallucinations, stripped 109 fabricated academic citations, corrected gravity references to `ākarṣaṇa-śakti`, corrected Aryabhata's heliocentrism claims to axial rotation, removed all typos and double commas. |
| **Permanent Regression Checks** | Added automated checks in `scripts/verify_audit.py` (citations, zero-gravity, Aryabhata-Brahmasphuta mixups, duplicate pairs). |
| **HF Dataset Uploader** | Wrote `scripts/data/upload_dataset.py` to automate uploading the compiled JSONL to Hugging Face Hub. |
| **Training Config Upgrade** | `MAX_SEQ_LENGTH` → 2048, LoRA `r=32`, `alpha=64`, switched from manual template string to `tokenizer.apply_chat_template()` to prevent formatting drift from GGUF metadata. |
| **Pre-flight Check Added** | `unsloth_finetune.py` now prints `repr()` of the first 3 formatted examples before training, so EOS/control tokens can be visually confirmed. |

---

## Context for AI Assistant (Read Carefully)

1. **Project Vision**: IKS (Indian Knowledge Systems) AI assistant designed as a **World Gateway**. Immersive cultural guide persona ("Bharat").
2. **Current Focus**: The cleaned, high-quality V2 instruction dataset is compiled and validated at `data/curated/iks_v2_instruction_dataset.jsonl`. The training configuration is finalized. The model has **NOT yet been fine-tuned**.
3. **Next Focus**: Upload dataset to HF Hub and launch the Kaggle Mistral 7B SFT job. Use empirical checkpointing (save every 500 steps, benchmark epoch 1/2/3) to find the optimal stopping point.

---

## Key Files Changed Recently

```text
scripts/train/unsloth_finetune.py              ← MODIFIED: apply_chat_template(), max_seq_length=2048, r=32, alpha=64, pre-flight check.
docs/guides/kaggle_training_notebook.md         ← MODIFIED: Synchronized with script changes above.
README.md                                       ← MODIFIED: Hyperparameters table updated (r=32, alpha=64, seq_len=2048). ADR-0007 added to index.
docs/adr/0007-resolve-llama3-template-mismatch.md ← NEW: Documents Llama 3 template mismatch root-cause and V2 resolution.
docs/project/changelog.md                       ← MODIFIED: Session 6 entry added.
docs/project/next-tasks.md                      ← MODIFIED: Task 2.6 updated with correct seq_length and template strategy.
```

---

## How to Resume (Next Session)

1. **Upload Dataset**: Run `uv run python scripts/data/upload_dataset.py` to upload the cleaned V2 dataset to the Hugging Face Hub.
2. **Pre-flight Check**: On Kaggle, after Cell 4 runs, read the PRE-FLIGHT output and confirm each example starts with `<s>[INST]` and ends with `</s>`. If you see `<|begin_of_text|>` or `<|eot_id|>`, stop — the tokenizer is wrong.
3. **Launch Training**: Set `SANITY_CHECK = True` first (20 steps), verify loss drops, then flip to `SANITY_CHECK = False` for the full 3-epoch run.
4. **Checkpoint Benchmarking**: Run `scripts/eval/run_benchmark.py` against the epoch 1, epoch 2, and epoch 3 checkpoints using the 150-prompt regression suite. Compare cultural bleed on utility tasks vs. IKS accuracy. Pick the best checkpoint.
5. **GGUF Export**: Merge LoRA adapters and export to GGUF (q4_k_m) for local inference via Ollama.

---

## Project Phase Tracker

| Phase | Status | Tasks |
|-------|--------|-------|
| **Phase 1: RAG Foundation** | ✅ 100% | Deployed on HF Spaces; 82.95% Test Coverage |
| **Phase 2: Fine-tuning** | 🔄 In Progress | V2 dataset complete & cleaned; training config finalized; **awaiting GPU launch** |
| **Phase 3: Production** | ⏳ Not Started | Hybrid arch, multi-lang, cloud deploy |

---

**File last updated**: Phase 2.6 (Training Config Complete — Awaiting Kaggle Launch)
**Next milestone**: Upload V2 dataset to Hugging Face Hub and initiate V2 SFT training run on Kaggle.
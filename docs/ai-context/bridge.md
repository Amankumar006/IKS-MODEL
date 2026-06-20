# Bridge File - IKS AI Assistant Development

**Purpose**: Continue development across platforms. Read this file to understand current state and next steps.

---

## Current Status (Phase 2.5: IKS V2 Dataset Rebuilt & Cleaned)

### ✅ Completed

| Task | Details |
|------|---------|
| **Phase 1: RAG Foundation** | 100% Complete. 82.95% test coverage. 40/40 Unit Tests passing locally. |
| **IKS V2 Dataset Builder** | Completed `iks_v2_dataset_builder.py` with multi-turn unpacking, 15,000 exact instruction-response pairs, and target blends (A=10,500, B=2,250, C=1,500, D=450, E=300). |
| **Quality Hotfixes & Audit** | Surgically resolved legacy V1 bugs in the V2 dataset: rewrote 758 first-person memory hallucinations to third-person, stripped 109 fabricated academic citations in Dataset D, corrected gravity references to `ākarṣaṇa-śakti`, corrected Aryabhata's heliocentrism claims to axial rotation, and removed duplicate "the the" typos and double commas. |
| **Permanent Regression Checks** | Added automated checks in `scripts/verify_audit.py` (citations, zero-gravity, Aryabhata-Brahmasphuta mixups, duplicate pairs) to ensure quality is maintained in future builds. |
| **HF Dataset Uploader** | Wrote `scripts/data/upload_dataset.py` to automate the uploading of the compiled JSONL to Hugging Face Hub. |

---

## Context for AI Assistant (Read Carefully)

1. **Project Vision**: IKS (Indian Knowledge Systems) AI assistant designed as a **World Gateway**. Immersive cultural guide persona ("Bharat").
2. **Current Focus**: The cleaned, high-quality V2 instruction dataset is compiled and validated at `data/curated/iks_v2_instruction_dataset.jsonl`.
3. **Next Focus**: Upload this dataset to Hugging Face Hub and trigger a new Mistral 7B SFT training run on Kaggle/RunPod using the upgraded `SYSTEM_PROMPT_V2`.

---

## Key Files Changed Recently

```text
data collection/iks_v2_dataset_builder.py  ← MODIFIED: Added deduplication, capping, and group-wise target sampling.
docs/project/dataset-governance.md          ← MODIFIED: Added V1 vs V2 comparison table and regression checks documentation.
scripts/verify_audit.py                     ← NEW: Permanent dataset audit regression checking suite.
scripts/data/upload_dataset.py              ← NEW: Helper script to upload the V2 dataset to Hugging Face Hub.
docs/project/changelog.md                   ← MODIFIED: Documented Session 5 rebuild, hotfixes, and uploader.
docs/project/next-tasks.md                  ← MODIFIED: Marked V2 dataset tasks complete, added V2 training tasks.
README.md                                   ← MODIFIED: Updated dataset roadmap, sizes, and V1 vs V2 improvements.
```

---

## How to Resume (Next Session)

1. **Upload Dataset**: Run `uv run python scripts/data/upload_dataset.py` to upload the cleaned V2 dataset to the Hugging Face Hub.
2. **Setup V2 Training**: Prepare the Kaggle/RunPod environment to pull the newly uploaded V2 dataset from Hugging Face.
3. **Run Training**: Execute fine-tuning on Mistral 7B for 1 epoch, using a sequence length of 1024 and the new `SYSTEM_PROMPT_V2`.
4. **Run Regression Tests**: Validate the fine-tuned model against `data/eval/v2_regression_tests.jsonl` to ensure compliance with stopping rules and no cultural bleed on utility tasks.

---

## Project Phase Tracker

| Phase | Status | Tasks |
|-------|--------|-------|
| **Phase 1: RAG Foundation** | ✅ 100% | Deployed on HF Spaces; 82.95% Test Coverage |
| **Phase 2: Fine-tuning** | 🔄 In Progress | Rebuilt V2 dataset; preparing for Mistral 7B V2 SFT training run |
| **Phase 3: Production** | ⏳ Not Started | Hybrid arch, multi-lang, cloud deploy |

---

**File last updated**: Phase 2.5 (IKS V2 Dataset Rebuild & Hotfixes)
**Next milestone**: Upload V2 dataset to Hugging Face Hub and initiate V2 training.
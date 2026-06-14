# Bridge File - IKS AI Assistant Development

**Purpose**: Continue development across platforms. Read this file to understand current state and next steps.

---

## Current Status (Phase 2.4 Complete -> Phase 2.5 SFT Execution on Kaggle)

### ✅ Completed

| Task | Details |
|------|---------|
| **Phase 1: RAG Foundation** | 100% Complete. 82.95% test coverage. 40/40 Unit Tests passing locally. |
| **Local Environment Fixes** | Removed `training` dependencies from `pyproject.toml` to fix local `uv sync`. Pinned `onnxruntime` strictly for macOS Intel. |
| **Phase 2.4: Eval Architecture** | Authored `docs/guides/evaluation_framework.md` defining our "LLM-as-a-judge" approach. |
| **Phase 2.4: Benchmark Tool** | Built `scripts/eval/generate_benchmark.py` and successfully compiled `iks_benchmark_gold.json` (500+ questions). |
| **Phase 2.2: Infrastructure** | Built `unsloth_finetune.py` (LoRA r=32, gradient checkpointing) and RunPod A100 setup guide in `docs/guides/runpod_setup.md`. |
| **Phase 2.4: Dataset Gen** | Generated, cleaned, and validated exactly 15,001 ShareGPT pairs via Mercury-2 API. 0 JSON errors. Ready for SFT. |

### 🔄 In Progress & Active Blockers

| Task | Status | Note |
|------|--------|------|
| **Kaggle SFT Execution** | 🔄 In Progress | Dual Tesla T4 setup active. Execute multi-session training with checkpoint resume across Kaggle 12-hour limits. |

---

## Context for AI Assistant (Read Carefully)

1. **Project Vision**: IKS (Indian Knowledge Systems) AI assistant designed as a **World Gateway**. We are NOT building a dry, factual VTU exam tool. We are building an immersive, culturally resonant storyteller persona ("Bharat").
2. **Evaluation Protocol**: We strictly evaluate the model on 4 dimensions (1-5 scale): Knowledge, Transport, Rasa, and Bharat Voice.
3. **Current Focus**: We are deep into Phase 2. The pipeline is generating 15,000 instruction-tuning pairs in ShareGPT format to fine-tune **Gemma 3 12B**.

---

## Key Files Changed Recently

```text
scripts/data/generate_qa_pairs.py     ← MODIFIED: Added strict 60s timeout, exponential backoff, and fatal limits.
data/curated/
└── iks_instruction_dataset.jsonl   ← TARGET: 15,001 pristine ShareGPT training pairs. Fully generated and validated.

scripts/eval/
└── generate_benchmark.py       ← NEW: Generates the 500-question gold-standard benchmark.
```

---

## How to Resume (Next Session)

1. **Open Kaggle Notebook**: Launch the dual T4 training notebook session (2x Tesla T4, ~32GB total VRAM).
2. **Dataset Location**: Ensure `iks_instruction_dataset.jsonl` is available at `/kaggle/working/iks_instruction_dataset.jsonl`.
3. **Resume-Aware Training**: Run the notebook cells from `docs/guides/kaggle_training_notebook.md`. The training cell auto-detects the latest checkpoint in `/kaggle/working/bharat-checkpoints` and resumes automatically.
4. **Multi-Session Strategy**: Continue across Kaggle's 12-hour session cap by restarting the notebook and re-running cells. Estimated total wall-clock for full SFT: ~50 hours across multiple sessions.
5. **Track Progress**: Use W&B run names like `session-1`, `session-2`, `session-3` and confirm checkpoints are saved every 500 steps.
6. **Multimodal Phase (Next)**: After SFT convergence and export, begin Temple architecture image collection for vision fine-tuning.

---

## Project Phase Tracker

| Phase | Status | Tasks |
|-------|--------|-------|
| **Phase 1: RAG Foundation** | ✅ 100% | Deployed on HF Spaces; 82.95% Test Coverage |
| **Phase 2: Fine-tuning** | 🔄 In Progress | Multi-session Kaggle dual T4 SFT with checkpoint resume |
| **Phase 3: Production** | ⏳ Not Started | Hybrid arch, multi-lang, cloud deploy |

---

**File last updated**: Phase 2.5 (Kaggle SFT Handoff)
**Next milestone**: Complete multi-session Kaggle dual T4 SFT and export the LoRA adapter.
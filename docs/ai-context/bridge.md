# Bridge File - IKS AI Assistant Development

**Purpose**: Continue development across platforms. Read this file to understand current state and next steps.

---

## Current Status (Phase 2.6 — CLEARED FOR KAGGLE LAUNCH)

> [!IMPORTANT]
> Everything upstream of the training run is **independently verified and locked**. The only remaining variable is empirical — how well V2 fixes the behavioral problems once it runs through SFT. That's what the regression suite tells you after epoch 1. **Run it.**

---

## ✅ Pre-Launch Verification — All Passed

| Check | Result | Verified By |
|---|---|---|
| Dataset size | 15,000 examples, 0 exact duplicates | `scripts/verify_audit.py` |
| Blend ratio | A=10,500 / B=2,250 / C=1,500 / D=450 / E=300 (70/15/10/3/2) | Independent audit |
| Fabricated citations | 0 | Regression check |
| Zero-gravity mentions | 0 | Regression check |
| Aryabhata+heliocentric mixups | 0 (3 legitimate Kerala School mentions remain) | Regression check |
| First-person memory hallucinations | 0 | Regression check |
| Training config | `max_seq_length=2048`, LoRA `r=32/alpha=64`, `apply_chat_template()` | Code review |
| HF model card | Published, provenance/causality/Sanskrit terminology all corrected | Final review |

---

## How to Launch (Next Session — Do These in Order)

### Step 1 — Upload V2 Dataset to HuggingFace Hub
```bash
uv run python scripts/data/upload_dataset.py
```

### Step 2 — Open the Kaggle Notebook
Load [`docs/guides/kaggle_training_notebook.md`](../guides/kaggle_training_notebook.md) into a new Kaggle notebook. The cells are copy-paste ready.

### Step 3 — Run the Pre-flight Check (Cell 4)
After Cell 4 runs, the PRE-FLIGHT block prints the first 3 decoded training examples. Verify **all three**:
- [ ] Each example **starts with `<s>[INST]`** — if you see `<|begin_of_text|>` or `<|eot_id|>`, the tokenizer is wrong. Stop.
- [ ] The **full system prompt appears uncut** — scroll through the decoded output. If it ends mid-sentence before the human turn, `max_seq_length` is still too short.
- [ ] Each example ends with **exactly one `</s>`** — not mid-string, not missing. Missing EOS = the model will never learn to stop generating.

### Step 4 — Sanity Run First (20 Steps)
Set `SANITY_CHECK = True`. Run 20 steps. Confirm loss drops from ~1.8. If it spikes or goes NaN, stop and check the data loader.

### Step 5 — Full 3-Epoch Run
Set `SANITY_CHECK = False`. Launch. Checkpoints are pushed to HF every 500 steps automatically.

### Step 6 — Benchmark All Three Epoch Checkpoints
```bash
uv run python scripts/eval/run_benchmark.py --checkpoint <epoch_1_path>
uv run python scripts/eval/run_benchmark.py --checkpoint <epoch_2_path>
uv run python scripts/eval/run_benchmark.py --checkpoint <epoch_3_path>
```
Use the 150-prompt regression suite (`data/eval/v2_regression_tests.jsonl`). Compare:
- Instruction-following rate (word count, format, yes/no constraints)
- Cultural bleed rate on utility tasks (coding/math should not get an IKS lens)
- Calibration / hedging on debated claims
- Greeting brevity (should be ≤2 sentences, not a lecture)

Pick the checkpoint where instruction-following is highest without persona collapsing.

### Step 7 — Export Best Checkpoint to GGUF
Merge LoRA adapters → export to Q4_K_M on Google Colab (Kaggle's 20 GB disk won't fit). Upload to `006aman/IKS-Mistral-7B-V2-GGUF`.

---

## Completed Work (Full History)

| Task | Details |
|------|---------|
| **Phase 1: RAG Foundation** | 100% complete. Deployed on HF Spaces with Gemini backend. 82.95% test coverage. |
| **V1 SFT Training** | 5,628 steps, 3 epochs, loss 1.8→1.1. Deployed: [IKS-Mistral-7B](https://huggingface.co/006aman/IKS-Mistral-7B) + [GGUF](https://huggingface.co/006aman/IKS-Mistral-7B-GGUF). |
| **V1 Bug Diagnosis** | Self-dialogue (Llama 3 tokens on Mistral), no system prompt in training, over-storytelling (29% dataset duplicates), named-entity hallucinations. All root-caused → see ADR-0007. |
| **V2 Dataset Rebuild** | 15,000 clean examples, 70/15/10/3/2 blend, 0 duplicates. Full provenance: 70% Gemini-distilled from 286 IKS texts; 30% programmatic/curated. |
| **Data Quality Hotfixes** | 758 first-person memory rewrites, 109 citation strips, gravity terminology corrected to *gurutvākarṣaṇa* (Brahmagupta) and *ākarṣaṇa-śakti* (Bhaskara II), Aryabhata heliocentric overclaim corrected, Brahmagupta/Kerala mixup corrected, Pingala decimal mixup corrected, typos and double-commas cleaned. |
| **Regression Checks** | `scripts/verify_audit.py` permanently asserts 0 for all known V1 content errors. |
| **Training Config** | `MAX_SEQ_LENGTH=2048` (V1 was 1024, which truncated the 1,233-token system prompt); LoRA `r=32/alpha=64` (V1: r=16/alpha=16); `tokenizer.apply_chat_template()` reads from the base model's tokenizer config (same template is embedded into GGUF during Unsloth export — V1 used hardcoded Llama 3 strings on a Mistral tokenizer). |
| **Pre-flight Check** | `unsloth_finetune.py` prints decoded `repr()` of first 3 examples before training. 3-point checklist: opening token, system prompt completeness, single EOS. |
| **Documentation** | Full doc reorganization: V1 training history, V1 bug inventory, benchmark cancellation (Gemini-writes-and-marks flaw), all precision corrections. See `docs/project/v1-model-report.md`. |
| **HF Model Card** | `docs/guides/huggingface_model_card.md` — ready to paste into HF repo README. |

---

## Key Files

```
scripts/train/unsloth_finetune.py              ← V2 training script (apply_chat_template, 2048, r=32)
docs/guides/kaggle_training_notebook.md        ← Copy-paste cells for Kaggle
scripts/data/upload_dataset.py                 ← Upload V2 dataset to HF Hub
scripts/eval/run_benchmark.py                  ← 150-prompt regression benchmark runner
scripts/verify_audit.py                        ← Dataset regression checks (run before training)
docs/guides/huggingface_model_card.md          ← HF model card (paste to HF repo README)
docs/project/v1-model-report.md               ← Full V1 post-training report
docs/adr/0007-resolve-llama3-template-mismatch.md ← Root-cause of V1's self-dialogue bug
```

---

## Project Phase Tracker

| Phase | Status | Notes |
|-------|--------|-------|
| **Phase 1: RAG Foundation** | ✅ 100% Complete | Deployed on HF Spaces (Gemini backend) |
| **Phase 2: V1 Fine-tune** | ✅ Complete (with bugs) | Live on HF; bugs documented in ADR-0007 |
| **Phase 2.5: V2 Dataset** | ✅ Complete | 15,000 examples, all hotfixes applied |
| **Phase 2.6: V2 Fine-tune** | 🟡 **READY TO LAUNCH** | Dataset verified, config locked, awaiting Kaggle run |
| **Phase 3: Production** | ⏳ Planned | Hybrid RAG + fine-tune wiring, multilingual |

---

**File last updated**: Phase 2.6 — Pre-launch verification complete. Cleared for Kaggle launch.  
**Next milestone**: Epoch 1 checkpoint benchmark results from the 150-prompt regression suite.
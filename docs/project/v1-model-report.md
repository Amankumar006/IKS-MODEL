# IKS-Bharat V1 Model — Post-Training Report

**Written**: June 2026  
**Purpose**: Document everything about the V1 training run, deployment, and post-deployment bugs so that future engineers understand why V2 exists and what was fixed.

---

## Overview

| Field | Value |
|---|---|
| **Base Model** | `unsloth/mistral-7b-instruct-v0.3-bnb-4bit` |
| **Training Dataset** | V1 — 15,001 ShareGPT-format instruction pairs |
| **Training Hardware** | Kaggle Free Tier — 2× Tesla T4 (15 GB VRAM each) |
| **Effective GPU** | Single T4 (`CUDA_VISIBLE_DEVICES="0"`) |
| **Steps** | 5,628 (3 full epochs) |
| **Training Loss** | ~1.8 → ~1.1 |
| **LoRA Rank** | r=16, alpha=16 |
| **Max Seq Length** | 1024 tokens |
| **HF Model (16-bit)** | [006aman/IKS-Mistral-7B](https://huggingface.co/006aman/IKS-Mistral-7B) |
| **HF Model (GGUF)** | [006aman/IKS-Mistral-7B-GGUF](https://huggingface.co/006aman/IKS-Mistral-7B-GGUF) |
| **GGUF Size** | ~4.37 GB (Q4_K_M quantization) |
| **W&B Project** | `iks-mistral-7b-run-1` |

---

## Training Infrastructure — What We Fought Through

The V1 training run was not straightforward. Every problem below was hit and solved in sequence.

### 1. Kaggle 12-Hour Session Limit
**Problem**: Kaggle disconnects notebooks after 12 hours. A 3-epoch run on 15,001 examples exceeds this.  
**Fix**: Configured `save_steps=500` with `hub_strategy="checkpoint"`, which automatically pushed LoRA adapter checkpoints to the private HF repo `006aman/iks-mistral-7b-checkpoints` every 500 steps. On resume, training loaded the latest checkpoint and continued.

### 2. Read-Only Filesystem on Resume
**Problem**: After resuming a Kaggle session, the `/kaggle/working/` directory from the previous session was remounted read-only. Saving new checkpoints failed with `OSError: [Errno 30] Read-only file system`.  
**Fix**: Used `shutil.copytree()` to copy the last checkpoint from the read-only mount into a new writable `/kaggle/working/bharat-checkpoints/` directory, then resumed training from there.

### 3. Dataset Discovery After Re-mount
**Problem**: After mounting the dataset in a resumed notebook, the auto-discovery loop (`os.walk("/kaggle/input")`) found multiple `.jsonl` files from previous experiment notebooks, picking the wrong one.  
**Fix**: Changed the discovery to search for the specific filename `iks_v1_instruction_dataset.jsonl` instead of any `.jsonl` file.

### 4. 20 GB Kaggle Disk Limit Blocking GGUF Export
**Problem**: Exporting the merged 16-bit model (Mistral 7B base + LoRA adapters) and then quantizing to GGUF requires ~30 GB of temporary disk. Kaggle's writable limit is 20 GB.  
**Fix**: Moved the GGUF export step to **Google Colab**, which offers 78 GB of disk space on the free tier. Loaded the merged model from HuggingFace, ran `llama.cpp` quantization to Q4_K_M format, and uploaded the GGUF directly to `006aman/IKS-Mistral-7B-GGUF`.

### 5. PyArrow Cast Exception on Dataset Load
**Problem**: The V1 dataset JSONL had extra metadata keys (`pr`, `words`) alongside the required `from`/`value` keys in each conversation turn. PyArrow's strict schema inference rejected the mixed-schema arrays.  
**Fix**: Added a custom `load_sharegpt_jsonl()` function that stripped each conversation turn to only `{"from": ..., "value": ...}` before creating the HuggingFace `Dataset`.

### 6. SFTConfig PicklingError
**Problem**: Using `TrainingArguments` with `SFTTrainer` in `trl==0.24.0` triggered a `PicklingError` when saving checkpoints. The `SFTConfig` class serializes differently.  
**Fix**: Replaced `TrainingArguments` with `SFTConfig`, which is the intended configuration class for `SFTTrainer` in trl 0.24+.

---

## W&B Training Metrics

- **Loss at Step 1**: ~1.8
- **Loss at Step 3,000**: ~1.3 (confirmed from W&B dashboard mid-run)
- **Loss at Step 5,628 (final)**: ~1.1
- No divergence or NaN loss spikes observed
- GPU utilization: ~85–90% on the single T4

---

## Deployment

### 1. Merged 16-bit Model
After training, the LoRA adapters from `006aman/iks-mistral-7b-checkpoints` were merged into the Mistral 7B base weights and pushed as a full merged model:  
👉 **[006aman/IKS-Mistral-7B](https://huggingface.co/006aman/IKS-Mistral-7B)**

### 2. GGUF Quantization (Google Colab)
The merged model was quantized to Q4_K_M format using `llama.cpp`:
```bash
python convert-hf-to-gguf.py ./IKS-Mistral-7B --outtype q4_k_m
```
The resulting `iks-mistral-7b-q4_k_m.gguf` (~4.37 GB) was uploaded to:  
👉 **[006aman/IKS-Mistral-7B-GGUF](https://huggingface.co/006aman/IKS-Mistral-7B-GGUF)**

### 3. Ollama Local Deployment (with Workaround)
Due to the template mismatch documented below, a custom Modelfile is required:

```bash
cat << 'EOF' > Modelfile
FROM ./iks-mistral-7b-q4_k_m.gguf

SYSTEM "You are Bharat, an AI assistant specialized in Indian Knowledge Systems (IKS).
You have deep knowledge of Ayurveda, Yoga, Indian philosophy, ancient architecture,
classical music, mathematics, astronomy, and cultural heritage. Answer questions
thoughtfully and accurately."

TEMPLATE """<|begin_of_text|>{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|start_header_id|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF

ollama create Bharat -f Modelfile
ollama run Bharat
```

After this Modelfile fix, the model responded correctly:
```
>>> hii
Hello, I am Bharat, your guide to the vast ocean of Indian Knowledge Systems!
[...appropriate introduction, no self-dialogue...]
```

### 4. HuggingFace Gradio Space
The Phase 1 RAG system (using Gemini API, not the fine-tuned V1 model) is live at:  
👉 **[huggingface.co/spaces/006aman/IKS](https://huggingface.co/spaces/006aman/IKS)**

Wiring the V1/V2 fine-tuned model into the RAG pipeline is Phase 3.

---

## V1 Bug Inventory (Discovered During Testing)

### 🔴 Bug 1: Self-Dialogue / Infinite Generation
**Severity**: Critical  
**Symptom**: Typing `hii` triggered the model to generate its own question ("What is the Kumbh Mela?") and then answer it, entering a hallucinated Q&A loop.

**Root Cause**: The V1 training script used Llama 3 chat tokens (`<|begin_of_text|>`, `<|start_header_id|>`, `<|eot_id|>`) on a Mistral 7B base model. Mistral's tokenizer does not recognize these as control tokens — they are treated as plain text. The model never learned a proper end-of-turn stop signal.

See **[ADR-0007](../adr/0007-resolve-llama3-template-mismatch.md)** for full root-cause analysis and V2 fix.

---

### 🔴 Bug 2: No Identity Without System Prompt
**Severity**: Critical  
**Symptom**: Without a system prompt, the model could not maintain a stable identity. Only after the Modelfile added a `SYSTEM` block did "I am Bharat" responses stabilize.

**Root Cause**: The V1 training dataset had zero system prompts. Every example was just `human → gpt`. The model never learned Bharat's identity from the training data itself.

**Permanent Fix (V2)**: `SYSTEM_PROMPT_V2` (~1,233 tokens) is baked into every single training example.

---

### 🟡 Bug 3: One-Mode Response Style (Over-Storytelling)
**Severity**: Moderate  
**Symptom**: Every response — regardless of question type — defaulted to elaborate sensory storytelling. "What is Ayurveda in one sentence?" returned a 200-word essay.

**Root Cause (two-part)**:
1. All 15,001 V1 examples were generated by Gemini in a single batch with a uniform prompt template → uniform tone
2. V1 dataset had 4,322 exact duplicates (29%). The 26 Factual QA questions averaged 86 repeats each → these got 86× the gradient weight of unique narrative examples → model memorized template answers while underlearning narrative diversity

**Permanent Fix (V2)**: 3-mode system (Guide/Scholar/Companion) in Dataset D; Dataset C (10%) trains concise utility responses; Dataset E (2%) trains "I don't know" hedging.

---

### 🟡 Bug 4: Named-Entity Hallucination
**Severity**: Moderate  
**Example**: "What year was Nalanda University founded?" → "Established by Dharmakirti in 427 CE" (Dharmakirti was a Buddhist logician who taught there, not the founder; the actual founder was Kumaragupta I)

**Root Cause**: The 29% duplication rate concentrated gradients on 26 template facts while the broader named-entity space was underlearned. The model pattern-matched plausible but wrong names from the same knowledge neighbourhood.

**Permanent Fix (V2)**: Dataset E (Calibration) trains explicit `[Evidence: Moderate]` hedging on contested attributions.

---

### 🟡 Bug 5: Hallucinated Source Citations
**Severity**: Moderate  
**Example**: Model occasionally ended responses with fabricated URLs ("Source: [Bihar Tourism](https://bihar...)").

**Root Cause**: Gemini-generated training data included URL-formatted source references; model learned this as a "scholarly" ending pattern.

**Permanent Fix (V2)**: 109 instances stripped from V2 dataset. Permanent regression check in `scripts/verify_audit.py` asserts 0 citations.

---

### 🟢 Bug 6: Runaway Invitation Endings
**Severity**: Minor  
**Symptom**: 16% of responses ended with "Shall we explore further?", creating artificial conversational loops.

**Permanent Fix (V2)**: Softened 90%+ of endings in V2 dataset. Rate is now 2.1% (measured).

---

## What V1 Got Right

Despite the bugs, V1 validated the core approach:
- The model absorbed IKS domain knowledge from 286 curated documents
- The cultural persona tone (warm, sensory, Indian-framed) was present
- After the Ollama Modelfile fix, simple identity and domain queries responded correctly
- Loss convergence was stable (1.8 → 1.1), no crashes or NaN losses

The V1 issues are all **training data and format problems** — not architectural failures. The same Mistral 7B base with the V2 dataset and correct template is expected to resolve all of them.

---

## Benchmark Status

> [!NOTE]
> The 500-question gold-standard benchmark (`data/eval/iks_benchmark_gold.json`) and the 150-prompt regression suite (`data/eval/v2_regression_tests.jsonl`) were **not run against V1** before the V2 rebuild was prioritized. Running these against V1 is recommended before the V2 training run to establish a formal baseline comparison score.

---

## See Also

- [ADR-0006: Pivot from Gemma 3 to Mistral 7B](../adr/0006-pivot-to-mistral-7b.md)
- [ADR-0007: Resolve Llama 3 Chat Template Mismatch](../adr/0007-resolve-llama3-template-mismatch.md)
- [Dataset Governance](dataset-governance.md) — V1 vs V2 defect comparison table
- [Next Tasks](next-tasks.md) — V2 training plan

**Report last updated**: Phase 2.6 (V2 Dataset Complete — Awaiting V2 Training Run)

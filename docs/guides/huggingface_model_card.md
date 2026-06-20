---
license: apache-2.0
language:
- en
base_model:
- mistralai/Mistral-7B-Instruct-v0.3
tags:
- unsloth
- indian-knowledge-systems
- iks
- cultural-ai
- fine-tuning-in-progress
---

# Bharat: Indian Knowledge Systems AI

**Bharat** is a specialized AI assistant built for **Indian Knowledge Systems (IKS)** — temples, classical music, dance, textiles, mathematics, philosophy, astronomy, and ancient heritage. It is designed to go beyond dry Wikipedia summaries and speak with the warm, immersive voice of a traditional scholar-guide.

> ⚠️ **Status: Data Preparation Phase Complete — Fine-Tuning Not Yet Started**
> The V2 instruction dataset (15,000 examples) has been fully built, audited, and cleaned. The Mistral 7B fine-tuning run has **not yet been executed**. This repository currently holds the V1 model weights along with full documentation of V1's known issues and the V2 improvements planned for the next training run.

---

## 🛠️ Model Details

| Field | Value |
|---|---|
| **Base Model** | `mistralai/Mistral-7B-Instruct-v0.3` |
| **Training Framework** | Unsloth + Hugging Face TRL (SFTTrainer) |
| **Dataset** | 15,000 curated V2 instruction pairs distilled from 286 IKS texts using Gemini API |
| **V2 Training Config** | `max_seq_length=2048`, LoRA `r=32 / alpha=64`, `tokenizer.apply_chat_template()` |
| **Current Status** | ⚠️ V1 weights only — V2 fine-tuning run pending |

---

## ⚠️ Known Limitations (V1 — Current Weights)

Extensive real-world testing of the V1 weights revealed several critical behavioral bugs, all traced back to dataset and training configuration issues:

| Bug | Root Cause | Severity |
|---|---|---|
| **Self-dialogue / Infinite Generation** | Training used Llama 3 special tokens on a Mistral 7B base. Mistral's tokenizer doesn't natively map these as control tokens, so the model never learned a proper stop boundary. | 🔴 Critical |
| **Format Amnesia** | Multi-turn conversation examples were packed together, training the model to predict the *next user question* instead of stopping after its own response. | 🔴 Critical |
| **Over-Storytelling** | Model heavily over-rewards poetic imagery. Struggles with concise answers to simple utility questions. | 🟡 Moderate |
| **Instruction Obedience** | V1 lacked contrastive examples (JSON output, one-word replies). | 🟡 Moderate |
| **Runaway Endings** | Habitually ends responses with "Shall we explore further?", creating unnatural loops. | 🟢 Minor |

---

## 🚧 V2 Improvements (In Progress — Data Phase Complete)

A completely redesigned training pipeline addresses every V1 defect. The V2 dataset preparation, quality cleaning, and audits are **100% complete**. Fine-tuning is pending.

### Dataset: V2 Blend Ratios (15,000 total)

| Partition | Size | % | Purpose |
|---|---|---|---|
| **A: Persona** | 10,500 | 70% | Core Bharat storyteller voice & civilizational perspectives |
| **B: Factual QA** | 2,250 | 15% | Grounded history, arts, sciences, geography QA |
| **C: Utility** | 1,500 | 10% | Formatting, programming, math, general non-cultural tasks |
| **D: Contrastive** | 450 | 3% | Active style-switching (Guide / Scholar / Companion modes) |
| **E: Calibration** | 300 | 2% | Refusals and epistemic confidence training |

### Data Quality Hotfixes Applied to V2

| V1 Defect | V2 Fix |
|---|---|
| **First-Person Memory Hallucinations** (e.g. "my grandmother told me") | Rewrote all **758 occurrences** to third-person objective narratives |
| **Fabricated Academic Citations** (e.g. `(Rao, 2013)`) | Removed all **109 instances** via regex; ran grammar post-processing |
| **Zero-Gravity Anachronism** | Corrected to historically precise gravity concepts: Brahmagupta's *gurutva* and Bhaskara II's *ākarṣaṇa-śakti* |
| **Aryabhata Heliocentric Overclaim** | Corrected to axial rotation; heliocentric framing reserved for the Kerala School |
| **Brahmagupta Placed in Kerala** | Corrected to 7th-century Bhinmal, Rajasthan |
| **Pingala Decimal Mixup** | Properly attributed binary numeral system and combinatorics to Pingala |
| **Double-commas & "the the" typos** | Programmatically stripped all typographical errors |
| **Runaway Invitation Endings** | Softened or removed 90%+ of "Shall we explore further?" endings |

### Training Configuration: V2 Fixes

| V1 Configuration | V2 Fix |
|---|---|
| Manual `<s>[INST]...[/INST]</s>` string | `tokenizer.apply_chat_template()` — reads the exact Jinja template from GGUF metadata |
| `max_seq_length=1024` (truncated system prompt at ~1,233 tokens) | `max_seq_length=2048` |
| LoRA `r=16 / alpha=16` | LoRA `r=32 / alpha=64` |
| No system prompt in training data | `SYSTEM_PROMPT_V2` baked into every single example |

---

## 🚀 How to Run V1 Locally (Ollama Workaround)

Because of the Llama 3 template mismatch on the Mistral base, you **must** configure Ollama with Llama 3 stop tokens manually.

### 1. Download the Weights
Download `iks-mistral-7b-q4_k_m.gguf` from the **Files and versions** tab.

### 2. Create the Modelfile

```bash
cat << 'EOF' > Modelfile
FROM ./iks-mistral-7b-q4_k_m.gguf

SYSTEM "You are Bharat, an AI assistant specialized in Indian Knowledge Systems (IKS). You have deep knowledge of Ayurveda, Yoga, Indian philosophy, ancient architecture, classical music, mathematics, astronomy, and cultural heritage. Answer questions thoughtfully and accurately. If asked something outside IKS, gently redirect to a relevant Indian knowledge topic."

TEMPLATE """<|begin_of_text|>{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|start_header_id|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF
```

### 3. Build and Run
```bash
ollama create Bharat -f Modelfile
ollama run Bharat
```

---

## 📂 Source Repository

Full training code, dataset builder, evaluation scripts, and documentation:
👉 **[github.com/Amankumar006/IKS-MODEL](https://github.com/Amankumar006/IKS-MODEL)**

## 📄 License
Apache 2.0

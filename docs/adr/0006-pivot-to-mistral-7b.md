# ADR 0006: Pivot from Gemma 3 to Mistral 7B for SFT Fine-Tuning

## Context

During Phase 2.5 (SFT Fine-Tuning execution), we attempted to train `unsloth/gemma-3-12b-it-bnb-4bit` on Kaggle's free GPU tier (2x Tesla T4 GPUs). However, we encountered severe hardware-level constraints:
1. **Precision & Memory Blowout**: Gemma 3 is optimized for `bfloat16` precision. Tesla T4 GPUs lack native `bfloat16` tensor cores. As a result, Unsloth was forced to upcast Gemma 3's activations/layers to `float32` to prevent numerical instability and NaN losses. This upcasting doubled the model's VRAM requirements, causing immediate CUDA Out of Memory (OOM) crashes.
2. **Kaggle Disk Space Limitations**: Kaggle limits writable storage to **20GB** in `/kaggle/working`. Downloading Gemma 3 12B (~9GB) and writing multiple model checkpoints quickly exhausted the disk space.
3. **Draft Session Disconnects**: Interactive notebook sessions are capped at 12 hours and idle out after 60 minutes.

## Decision

We decided to:
1. **Pivot to Mistral 7B** (`unsloth/mistral-7b-instruct-v0.3-bnb-4bit`) for our SFT training. Mistral natively supports standard `float16` precision without memory-doubling penalties, fitting comfortably within the 15GB VRAM of a single Tesla T4 GPU.
2. **Implement Safe Dataset Schema Parsing**: Created a custom JSONL loader to strip out inconsistent metadata keys (`pr`, `words`) to prevent PyArrow cast exceptions.
3. **Configure Aggressive Memory & Storage Hacks**:
   * Staged training on a single T4 GPU (`CUDA_VISIBLE_DEVICES="0"`) to avoid GPU memory duplication.
   * Enabled PyTorch memory allocation hacks (`expandable_segments:True`).
   * Throttled training context length (`max_seq_length = 1024`) to keep memory footprint under 5GB VRAM.
   * Backed up checkpoints directly to a private Hugging Face repository (`iks-mistral-7b-checkpoints`) and set `save_total_limit=2` to stay under the 20GB disk limit.
   * Switched from `TrainingArguments` to `SFTConfig` in `trl 0.24.0` to avoid PicklingErrors during checkpoint serialization.

## Consequences

* **Stable SFT Pipeline**: Fine-tuning converges reliably on Kaggle's free tier, dropping loss from ~1.8 to ~1.1.
* **Lightweight Training Footprint**: VRAM footprint is optimized down to **4.35 GB**, leaving ample margin for sequence lengths.
* **Architecture Shift**: The fine-tuned storyteller persona model will be a Mistral 7B adapter rather than a Gemma 3 adapter. The local RAG pipeline can continue using Google Gemini API for the cloud fallback and Mistral 7B for local offline usage.

---

## Outcomes (What Actually Happened)

The Mistral 7B pivot was executed successfully. V1 was fully trained and deployed.

| Metric | Value |
|---|---|
| Training steps | 5,628 (3 full epochs) |
| Final training loss | ~1.1 (from ~1.8) |
| W&B project | `iks-mistral-7b-run-1` |
| HF model (16-bit) | [006aman/IKS-Mistral-7B](https://huggingface.co/006aman/IKS-Mistral-7B) |
| HF model (GGUF) | [006aman/IKS-Mistral-7B-GGUF](https://huggingface.co/006aman/IKS-Mistral-7B-GGUF) |
| GGUF size | ~4.37 GB (Q4_K_M) |

However, several bugs were discovered during local Ollama testing that are not related to the Gemma→Mistral pivot itself, but to the training format and dataset quality:

1. **Template token mismatch** (see ADR-0007): The training script used Llama 3 chat tokens on a Mistral base. This caused infinite generation in local inference.
2. **Dataset 29% duplication**: 4,322 of 15,001 V1 examples were exact duplicates, skewing gradient updates toward 26 template facts.
3. **No system prompt in training data**: The model never saw "I am Bharat" during training, requiring inference-time injection.

These issues collectively motivated the V2 dataset rebuild. See [V1 Model Report](../project/v1-model-report.md) for the full post-training analysis.

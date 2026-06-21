# Kaggle Notebook Cells for Mistral 7B SFT

**Purpose**: Copy these cells into a Kaggle notebook and run in order to execute the fine-tuning.

**Notes**:
*   This setup is optimized for Kaggle's free GPU tier (select **GPU T4 x2** in Settings).
*   Although two T4s are active, the training binds to a single card (`CUDA_VISIBLE_DEVICES="0"`) to avoid PyTorch DDP duplicating memory across both devices.
*   Mistral 7B natively runs on standard `float16` precision without the float32 upcasting VRAM penalty required by Gemma on T4 cards.
*   LoRA checkpoint adapters are pushed directly to Hugging Face (`iks-mistral-7b-checkpoints`) every 500 steps.

---

## Cell 1 - Clean Reinstallation of Dependencies

Run this first to clear Kaggle's cached conflicting packages:

```python
%%capture
# 1. Install pip3-autoremove to completely purge conflicting packages
!pip install pip3-autoremove
!pip-autoremove torch torchvision torchaudio -y

# 2. Uninstall conflicting libraries
!pip uninstall -y unsloth transformers trl peft bitsandbytes accelerate

# 3. Clean install torch/xformers for CUDA 12.1
!pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121

# 4. Clean install Unsloth specifically configured for Kaggle
!pip install "unsloth[kaggle-new] @ git+https://github.com/unslothai/unsloth.git"

# 5. Clean install trl, peft, accelerate, bitsandbytes, wandb, and datasets
!pip install trl peft accelerate bitsandbytes wandb datasets

# 6. Force reinstall the latest transformers to ensure _get_template_variables is present
!pip install --upgrade --force-reinstall transformers
```

> [!IMPORTANT]
> Once Cell 1 finishes, click **Restart Session** (or **Restart Kernel**) in the top menu bar of your Kaggle notebook to reload the updated package paths.

---

## Cell 2 - Environment & Secrets Configuration

Add your `WANDB_API_KEY` and `HF_TOKEN` (Write access) in **Add-ons -> Secrets** in the top menu bar before running.

```python
import os

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Stick to one GPU to avoid VRAM duplication

from kaggle_secrets import UserSecretsClient
secrets = UserSecretsClient()

# Load API keys
os.environ["HF_TOKEN"] = secrets.get_secret("HF_TOKEN")
os.environ["WANDB_API_KEY"] = secrets.get_secret("WANDB_API_KEY")

HF_USERNAME = "006aman"      # Replace with your HF username
HF_REPO_NAME = "iks-mistral-7b-checkpoints"
```

---

## Cell 3 - Load Mistral 7B Model with LoRA

```python
import torch
from unsloth import FastLanguageModel

MODEL_NAME = "unsloth/mistral-7b-instruct-v0.3-bnb-4bit"
MAX_SEQ_LENGTH = 2048  # Set to 2048 to prevent truncation of system prompt + QA

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = MODEL_NAME,
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = None,          # Auto detection (float16 on T4)
    load_in_4bit = True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r = 32,                # Increased to 32 for higher domain capacity
    target_modules = ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    lora_alpha = 64,       # Increased to 64
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Memory allocated after load: {torch.cuda.memory_allocated()/1e9:.2f} GB")
```

---

## Cell 4 - Dataset Loader (PyArrow & Schema Safe)

```python
import os
import json
from datasets import Dataset

# Auto-discover data files in Kaggle input paths
data_files = []
for root, dirs, files in os.walk("/kaggle/input"):
    for f in files:
        if f.endswith((".json", ".jsonl", ".csv")):
            data_files.append(os.path.join(root, f))

DATA_PATH = data_files[0]
print(f"Loading Dataset: {DATA_PATH}")

# 1. Custom safe JSONL loader to strip out inconsistent metadata schemas
def load_sharegpt_jsonl(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            conv = obj.get("conversations", [])
            # Forcibly extract only the required keys
            cleaned = [{"from": str(turn.get("from", "")), "value": str(turn.get("value", ""))} for turn in conv]
            if cleaned:
                rows.append({"conversations": cleaned})
    return Dataset.from_list(rows)

raw_dataset = load_sharegpt_jsonl(DATA_PATH)

# 2. Format using the tokenizer's own apply_chat_template() to prevent silent drift
#    apply_chat_template() reads the Jinja template from the base model's tokenizer config
#    (not the GGUF — the GGUF doesn't exist yet at training time). During the Unsloth
#    export step, the same template gets embedded into the GGUF, so training-time and
#    inference-time formatting are guaranteed identical. This was the root cause of V1's
#    hallucination / self-dialogue bug.
def format_mistral(example):
    system_msg, user_msg, assistant_msg = "", "", ""
    for turn in example["conversations"]:
        role = turn.get("from", "").strip().lower()
        val = turn.get("value", "")
        if role == "system":
            system_msg = val.strip()
        elif role == "human":
            user_msg = val.strip()
        elif role == "gpt":
            assistant_msg = val.strip()

    # Build messages list in the standard chat-completion format.
    # Mistral folds the system turn into the first [INST] block natively.
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})
    messages.append({"role": "assistant", "content": assistant_msg})

    # Let the tokenizer produce the exact byte-sequence it expects at inference.
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,          # Return string, not token IDs
        add_generation_prompt=False,  # Sequence already ends with the assistant turn
    )
    return {"text": text}

train_dataset = raw_dataset.map(format_mistral, remove_columns=raw_dataset.column_names)

print("\nColumns:", train_dataset.column_names)

# --- Pre-flight decode check ---
# Decode a few examples and visually confirm the EOS and control tokens before launching.
print("\n=== PRE-FLIGHT: First 3 examples (decoded) ===")
for i in range(min(3, len(train_dataset))):
    decoded = train_dataset[i]["text"]
    print(f"\n--- Example {i} ---")
    print(repr(decoded[:300]))  # Shows first 300 chars with escape sequences visible
print("\n=== END PRE-FLIGHT ===")
```

---

## Cell 5 - SFTTrainer Configuration

```python
from trl import SFTTrainer, SFTConfig

SANITY_CHECK = False
OUTPUT_DIR = "/kaggle/working/bharat-checkpoints"

extra = {"max_steps": 20} if SANITY_CHECK else {"num_train_epochs": 3}

training_args = SFTConfig(
    output_dir=OUTPUT_DIR,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=10,
    lr_scheduler_type="cosine",
    weight_decay=0.01,
    optim="paged_adamw_8bit",
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1 if SANITY_CHECK else 10,
    save_steps=500,
    save_total_limit=2,
    remove_unused_columns=False,
    average_tokens_across_devices=False,  # Bypasses transformers 5.5.0 bug
    report_to="none" if SANITY_CHECK else "wandb", 
    push_to_hub=not SANITY_CHECK,
    hub_model_id=f"{HF_USERNAME}/{HF_REPO_NAME}",
    hub_strategy="checkpoint", 
    hub_private_repo=True,     
    hub_token=os.environ.get("HF_TOKEN"),
    **extra,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    args=training_args,
)

print("Mode:", "SANITY CHECK (20 steps)" if SANITY_CHECK else "FULL RUN (3 epochs)")
print("per_device_train_batch_size:", trainer.args.per_device_train_batch_size)
```

---

## Cell 6 - Execute Training

```python
trainer.train()
```

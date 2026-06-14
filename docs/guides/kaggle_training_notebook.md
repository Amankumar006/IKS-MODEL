# Kaggle Dual T4 Notebook Cells for Gemma 3 12B SFT

Purpose: Copy these cells into a Kaggle notebook and run in order.

Notes:
- This plan is tuned for 2x Tesla T4 GPUs (about 32GB total VRAM).
- Kaggle sessions are capped at about 12 hours, so checkpoint resume is required.
- Dataset path is set to /kaggle/working/iks_instruction_dataset.jsonl as confirmed.

## Cell 1 - Environment Sanity Check

```python
import os
import subprocess

print("CUDA devices:")
print(subprocess.check_output("nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader", shell=True, text=True))

print("Working directory:", os.getcwd())
print("Expected dataset path:", "/kaggle/working/iks_instruction_dataset.jsonl")
print("Dataset exists:", os.path.exists("/kaggle/working/iks_instruction_dataset.jsonl"))
```

## Cell 2 - Install Dependencies

```python
import subprocess


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[-500:]}")
    else:
        print(f"OK: {cmd[:80]}")
    return result.returncode == 0

run("pip install -q torch==2.2.0 torchvision --index-url https://download.pytorch.org/whl/cu121")
run("pip install -q xformers==0.0.28.post3 --index-url https://download.pytorch.org/whl/cu121")
run("pip install -q unsloth")
run("pip install -q trl==0.8.6 datasets transformers accelerate bitsandbytes peft")
run("pip install -q wandb")

print("All dependencies installed.")
```

## Cell 3 - Imports and Global Config

```python
import os
import json
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer

from unsloth import FastLanguageModel

# Core paths
DATA_PATH = None
OUTPUT_DIR = "/kaggle/working/bharat-checkpoints"
FINAL_DIR = "/kaggle/working/bharat-final"

# Kaggle dual T4 optimized settings
MODEL_NAME = "unsloth/gemma-3-12b-it-bnb-4bit"
MAX_SEQ_LENGTH = 2048
DTYPE = None
LOAD_IN_4BIT = True

# Effective batch size = 1 * 8 = 8
PER_DEVICE_BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 8
NUM_EPOCHS = 3
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.03
WEIGHT_DECAY = 0.01
SAVE_STEPS = 500
LOGGING_STEPS = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("GPU count:", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(i, torch.cuda.get_device_name(i))

candidate_paths = [
    "/kaggle/working/iks_instruction_dataset.jsonl",
    "/kaggle/input/iks-dataset/iks_instruction_dataset.jsonl",
    "/kaggle/input/datasets/coder006aman/iks-dataset/iks_instruction_dataset.jsonl",
]

for p in candidate_paths:
    if os.path.exists(p):
        DATA_PATH = p
        break

if DATA_PATH is None:
    raise FileNotFoundError(
        "Could not locate iks_instruction_dataset.jsonl in common Kaggle locations."
    )

print("Resolved dataset path:", DATA_PATH)
```

## Cell 4 - Dataset Validation

```python
from pathlib import Path

p = Path(DATA_PATH)
if not p.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

line_count = 0
with p.open("r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            line_count += 1

print(f"Dataset found with {line_count} non-empty JSONL rows.")
```

## Cell 5 - Load and Format Dataset

```python
import json
from datasets import Dataset


def load_sharegpt_jsonl(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            conv = obj.get("conversations", [])
            cleaned = []
            for turn in conv:
                # Keep only the keys needed for training to avoid schema mismatches.
                cleaned.append(
                    {
                        "from": str(turn.get("from", "")),
                        "value": str(turn.get("value", "")),
                    }
                )

            if cleaned:
                rows.append({"conversations": cleaned})

    return Dataset.from_list(rows)


raw = load_sharegpt_jsonl(DATA_PATH)


def format_sharegpt(example):
    conversations = example["conversations"]
    user_msg = ""
    assistant_msg = ""
    for turn in conversations:
        role = turn.get("from", "").strip().lower()
        val = turn.get("value", "")
        if role == "human":
            user_msg = val
        elif role == "gpt":
            assistant_msg = val

    text = (
        "<start_of_turn>user\n"
        + user_msg
        + "<end_of_turn>\n"
        + "<start_of_turn>model\n"
        + assistant_msg
        + "<end_of_turn>"
    )
    return {"text": text}

train_dataset = raw.map(format_sharegpt, remove_columns=raw.column_names)
print(train_dataset)
print(train_dataset[0]["text"][:500])
```

## Cell 6 - Login to Weights and Biases

```python
import wandb

# Option 1: store in Kaggle Secrets as WANDB_API_KEY and uncomment below
# import os
# wandb.login(key=os.environ["WANDB_API_KEY"])

# Option 2: manual login prompt
wandb.login()

run = wandb.init(
    project="iks-gemma3-12b-sft",
    name="session-1",
    job_type="train",
)
print("W&B initialized:", run.name)
```

## Cell 7 - Load Model with LoRA

```python
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=DTYPE,
    load_in_4bit=LOAD_IN_4BIT,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

print("Model and LoRA adapters loaded.")
```

## Cell 8 - Auto-Detect Latest Checkpoint

```python
from pathlib import Path
import re


def find_latest_checkpoint(output_dir: str):
    base = Path(output_dir)
    if not base.exists():
        return None

    ckpts = []
    for child in base.iterdir():
        if child.is_dir() and child.name.startswith("checkpoint-"):
            m = re.match(r"checkpoint-(\d+)", child.name)
            if m:
                ckpts.append((int(m.group(1)), str(child)))

    if not ckpts:
        return None

    ckpts.sort(key=lambda x: x[0])
    return ckpts[-1][1]

latest_ckpt = find_latest_checkpoint(OUTPUT_DIR)
print("Latest checkpoint:", latest_ckpt if latest_ckpt else "None (starting fresh)")
```

## Cell 9 - Create Trainer

```python
train_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    warmup_ratio=WARMUP_RATIO,
    lr_scheduler_type="cosine",
    weight_decay=WEIGHT_DECAY,
    optim="paged_adamw_8bit",
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=LOGGING_STEPS,
    save_steps=SAVE_STEPS,
    save_total_limit=4,
    report_to="wandb",
    remove_unused_columns=False,
    dataloader_num_workers=2,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    args=train_args,
)

print("Trainer ready.")
```

## Cell 10 - Train and Resume Automatically

```python
if latest_ckpt is None:
    print("Starting training from scratch...")
    train_result = trainer.train()
else:
    print(f"Resuming training from: {latest_ckpt}")
    train_result = trainer.train(resume_from_checkpoint=latest_ckpt)

print(train_result)
```

## Cell 11 - Save Final Adapter and Tokenizer

```python
trainer.save_model(FINAL_DIR)
tokenizer.save_pretrained(FINAL_DIR)

print("Saved final artifacts to:", FINAL_DIR)
print("Checkpoint directory:", OUTPUT_DIR)
print("Tip: For next session, keep this notebook flow identical and update W&B run name to session-2, session-3, etc.")
```

## Session Resume Checklist

1. Start a new Kaggle session with dual Tesla T4 enabled.
2. Ensure your dataset is present at /kaggle/working/iks_instruction_dataset.jsonl.
3. Re-run cells from top to bottom.
4. Cell 8 finds the latest checkpoint automatically.
5. Cell 10 resumes from that checkpoint.

## Expected Progress Profile

- Steps target: around 6,300 total (approximate, depends on final dataset cardinality and packing behavior).
- Checkpoint frequency: every 500 steps.
- Typical complete run across Kaggle sessions: about 50 hours wall-clock split across multiple sessions.

import os
import argparse
import wandb
import json
import torch
from datasets import Dataset
from trl import SFTTrainer, SFTConfig
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template

def load_clean_dataset(path: str):
    """Loads JSONL dataset safely, stripping out problematic schemas to avoid PyArrow cast errors."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                conv = obj.get("conversations", [])
                cleaned = []
                for turn in conv:
                    cleaned.append({
                        "from": str(turn.get("from", "")),
                        "value": str(turn.get("value", ""))
                    })
                if cleaned:
                    rows.append({"conversations": cleaned})
            except Exception:
                continue
    return Dataset.from_list(rows)

def main():
    parser = argparse.ArgumentParser(description="Fine-tune IKS Bharat Persona using Unsloth")
    parser.add_argument("--resume", action="store_true", help="Resume from the latest checkpoint if it crashed")
    args = parser.parse_args()

    # 1. Environment & Hardware Optimization Hacks for Kaggle/T4
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

    # 2. Weights & Biases Setup
    wandb.init(project="iks-bharat-persona", name="mistral-7b-run-1")

    # 3. Model & LoRA Configuration (Pivoted to Mistral 7B for standard float16 compatibility)
    max_seq_length = 512  # Throttled context window to prevent memory blowout
    dtype = None  # Auto detection
    load_in_4bit = True  # Use 4bit quantization to save memory

    print("Loading Base Model (Mistral 7B)...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/mistral-7b-instruct-v0.3-bnb-4bit",
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
        token = os.environ.get("HF_TOKEN")
    )

    print("Configuring LoRA for deep persona injection...")
    model = FastLanguageModel.get_peft_model(
        model,
        r = 32,             # Higher rank for stylistic/persona changes
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 64,    # Alpha = 2 * r is standard
        lora_dropout = 0,   # 0 is optimized for Unsloth
        bias = "none",
        use_gradient_checkpointing = "unsloth", # Crucial for 15k multi-turn examples
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )

    # 4. Dataset Preparation with safe JSONL loader
    print("Loading Dataset cleanly...")
    tokenizer = get_chat_template(
        tokenizer,
        chat_template = "mistral",
    )

    def formatting_prompts_func(examples):
        convos = examples["conversations"]
        texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False) for convo in convos]
        return { "text" : texts, }

    # Load cleaned dataset to bypass PyArrow schema casts errors
    dataset = load_clean_dataset("data/curated/iks_instruction_dataset.jsonl")
    dataset = dataset.map(formatting_prompts_func, batched = True,)

    # 5. Training Configuration using SFTConfig
    print("Initializing SFTTrainer...")
    
    # Configure SFTConfig to resolve PicklingError and Transformers 5.5.0 bugs
    sft_config = SFTConfig(
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 1,  # Single-process mapping to reduce memory spikes
        packing = False,
        per_device_train_batch_size = 1,
        gradient_accumulation_steps = 8,  # Effective batch size = 8
        warmup_steps = 50,
        num_train_epochs = 3,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 10,
        optim = "paged_adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "cosine",
        seed = 3407,
        output_dir = "iks-mistral-7b-checkpoints",
        report_to = "wandb",
        gradient_checkpointing = True,
        save_strategy = "steps",
        save_steps = 500,
        save_total_limit = 2,  # Limit checkpoints to save disk space
        average_tokens_across_devices = False,  # Fix for transformers 5.5.0 bug
    )

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        args = sft_config,
    )

    # 6. Training Execution
    print(f"Starting Training! Resume mode: {args.resume}")
    trainer_stats = trainer.train(resume_from_checkpoint=args.resume)

    print("Training Complete. Saving Final Model...")
    model.save_pretrained("iks_bharat_lora")
    tokenizer.save_pretrained("iks_bharat_lora")

    print("Done. LoRA adapter weights saved successfully.")

if __name__ == "__main__":
    main()

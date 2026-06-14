# RunPod Setup Guide: Fine-Tuning IKS "Bharat" Persona

This guide walks you through renting a GPU on RunPod and running the fine-tuning script (`unsloth_finetune.py`) to inject the Bharat persona into Gemma 3.

## 1. Rent an A100 Instance on RunPod

1. Go to [RunPod.io](https://www.runpod.io/) and log in.
2. Click **Deploy** -> **Secure Cloud** (or Community Cloud for cheaper rates).
3. Select an **A100 80GB** instance (approx $1.50 - $1.80/hr).
4. For the template, select the official **RunPod PyTorch** template.
5. Set the disk space:
   - Volume size: **100 GB**
   - Container disk: **50 GB**
6. Click **Deploy**. Once it's running, click **Connect** -> **Connect to Web Terminal**.

## 2. Install Dependencies

In the RunPod terminal, run these commands to set up Unsloth and your repository:

```bash
# Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/IKS-Model.git
cd IKS-Model

# Install Unsloth and required ML libraries
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps xformers "trl<0.9.0" peft accelerate bitsandbytes wandb
```

## 3. Login to Weights & Biases (W&B)

We highly recommend using W&B to monitor the training loss curve live. If the loss spikes or plateaus too early, you can catch it in 20 minutes instead of waiting 10 hours.

1. Go to [wandb.ai](https://wandb.ai/) and get your API key from settings.
2. In the RunPod terminal, run:
```bash
wandb login
```
3. Paste your API key when prompted.

## 4. Transfer the Dataset

You need to get the 15,000 text pair dataset (`iks_instruction_dataset.jsonl`) onto the RunPod instance.
If you pushed it to GitHub (via Git LFS), it's already there. Alternatively, you can use `scp` or a cloud storage link:

```bash
# Example: If you uploaded it to a public Google Drive or S3
wget -O data/curated/iks_instruction_dataset.jsonl "YOUR_DOWNLOAD_LINK"
```

## 5. Start Training

Run the training script! It will automatically format the dataset, initialize the LoRA adapters, and begin fine-tuning.

```bash
python scripts/train/unsloth_finetune.py
```

*Note: Training on 15,000 examples with Gemma 3 12B on an A100 takes roughly 10-15 hours.*

---

## ⚠️ What happens if the RunPod crashes? (Resuming from Checkpoint)

Spot instances (Community Cloud) can be preempted. Our training script is specifically designed to save a checkpoint every 500 steps to prevent catastrophic data loss. 

If your instance dies at hour 8:
1. Re-deploy or restart the instance.
2. Navigate back to the `IKS-Model` directory.
3. Simply run the script with the `--resume` flag:

```bash
python scripts/train/unsloth_finetune.py --resume
```

The script will automatically detect the latest checkpoint in the `outputs/` directory and resume training exactly where it left off, without starting from epoch 0.

## Next Steps

Once the script completes, the LoRA adapters will be saved in the `iks_bharat_lora` directory. You can then use Unsloth's export tools to merge this into a `GGUF` file for local inference, or deploy it to HuggingFace.

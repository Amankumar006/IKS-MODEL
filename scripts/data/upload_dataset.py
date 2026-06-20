"""Script to upload the cleaned IKS V2 dataset to Hugging Face Hub.

Requires the `huggingface-hub` package and `HF_TOKEN` environment variable or active `huggingface-cli login`.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load environment variables
load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_FILE = REPO_ROOT / "data" / "curated" / "iks_v2_instruction_dataset.jsonl"

def upload_dataset():
    if not DATASET_FILE.exists():
        print(f"❌ Error: Dataset file not found at {DATASET_FILE}")
        sys.exit(1)

    print("🏛️ IKS V2 Dataset Uploader to Hugging Face")
    print("=" * 50)

    # Get token
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not hf_token:
        print("⚠️  Warning: HF_TOKEN environment variable not set in .env.")
        print("Will attempt to use credentials from active huggingface-cli session...")
    
    # Target repository name
    default_repo = "006aman/iks-v2-instruction-dataset"
    repo_id = input(f"Enter target Hugging Face dataset repository ID [{default_repo}]: ").strip()
    if not repo_id:
        repo_id = default_repo

    api = HfApi(token=hf_token)

    try:
        print(f"\n🚀 Creating/checking dataset repository: {repo_id}...")
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            exist_ok=True
        )
        
        print(f"📤 Uploading {DATASET_FILE.name} to {repo_id}...")
        api.upload_file(
            path_or_fileobj=str(DATASET_FILE),
            path_in_repo="iks_v2_instruction_dataset.jsonl",
            repo_id=repo_id,
            repo_type="dataset"
        )
        print("\n✅ Success! Dataset uploaded successfully to Hugging Face:")
        print(f"🔗 https://huggingface.co/datasets/{repo_id}")
        
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        print("Please check your HF_TOKEN permissions or login with `huggingface-cli login` and try again.")
        sys.exit(1)

if __name__ == "__main__":
    upload_dataset()

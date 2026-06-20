"""Clean V1 instruction dataset.

Rewrites first-person memories to third-person descriptions using Groq API (Llama 3.1 8B),
and fixes factual/chronological bugs concerning Brahmagupta.
Uses a local JSON cache to support resuming.
"""

import os
import json
import re
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup paths
REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = REPO_ROOT / "data" / "curated" / "iks_instruction_dataset.jsonl"
OUTPUT_FILE = REPO_ROOT / "data" / "curated" / "iks_instruction_dataset_cleaned.jsonl"
CACHE_FILE = REPO_ROOT / "scratch" / "clean_dataset_cache.json"

FIRST_PERSON_PATTERNS = [
    r"\bmy grandmother\b",
    r"\bmy grandfather\b",
    r"\bmy guru\b",
    r"\bi witnessed\b",
    r"\bi watched\b",
    r"\bi remember\b",
    r"\bi sat with\b",
    r"\bi sat beside\b",
    r"\bi walked\b",
    r"\bi stood\b",
    r"\bmy feet\b",
    r"\bmy heart\b",
    r"\bmy eyes\b"
]

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}. Starting fresh.")
    return {}

def save_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def rewrite_first_person(text, client, model_name):
    prompt = (
        "You are an expert copyeditor specializing in Indian Knowledge Systems and literary style.\n"
        "The following response from an AI assistant contains first-person memories/pronouns (such as 'my guru', 'my grandmother', 'I sat', 'I remember', 'my feet', 'I witnessed', 'I stood', 'my heart', 'my eyes', etc.).\n"
        "This is incorrect because the AI assistant should speak as an objective scholar-guide ('Bharat') and must NOT claim to have personal lived human experiences.\n"
        "Please rewrite the text to convert all first-person experiences/memories into objective third-person descriptions. Use terms like 'a traveler feels', 'devotees remember', 'one hears', 'an artisan\'s grandmother told them', 'pilgrims walk', etc. instead of first-person pronouns.\n"
        "CRITICAL REQUIREMENTS:\n"
        "1. Preserve the exact content, tone, facts, structure, formatting, and approximate length of the original text.\n"
        "2. Do NOT introduce or conclude your output. Output ONLY the rewritten text itself.\n"
        "3. Ensure absolutely NO first-person pronouns (I, me, my, we, us, our, mine, ours) are used in the rewritten text.\n\n"
        f"Original text:\n{text}\n\n"
        "Rewritten text:"
    )

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2048,
                timeout=30
            )
            if response and response.choices:
                cleaned = response.choices[0].message.content.strip()
                if cleaned and cleaned != text:
                    return cleaned
        except Exception as e:
            print(f"\nAPI Error (attempt {attempt + 1}/3): {e}")
            time.sleep(2 ** attempt)
    return text

def fix_brahmagupta(text: str) -> str:
    # 1. Brahmagupta's Brāhmasphuṭasiddhānta, translated
    text = text.replace(
        "Brahmagupta's `Brāhmasphuṭasiddhānta`, translated",
        "Brahmagupta of Bhinmal (Rajasthan), in his `Brāhmasphuṭasiddhānta`, translated"
    )
    # 2. monk in 7th‑century Kerala dips -> scholar in 7th‑century Bhinmal (Rajasthan) dips
    text = text.replace(
        "monk in 7th‑century Kerala dips",
        "scholar in 7th‑century Bhinmal (Rajasthan) dips"
    ).replace(
        "monk in 7th-century Kerala dips",
        "scholar in 7th-century Bhinmal (Rajasthan) dips"
    )
    # 3. towering works of Aryabhata, Brahmagupta, and the Kerala school
    text = text.replace(
        "towering works of Aryabhata, Brahmagupta, and the Kerala school",
        "towering works of Aryabhata, Brahmagupta of Bhinmal (Rajasthan), and the later Kerala school"
    )
    # 4. later work of Brahmagupta
    text = text.replace(
        "later work of Brahmagupta",
        "earlier work of Brahmagupta in Bhinmal (Rajasthan)"
    )
    # 5. Then came Brahmagupta in the 7th century
    text = text.replace(
        "Then came Brahmagupta in the 7th century",
        "Then came Brahmagupta in 7th-century Bhinmal (Rajasthan)"
    )
    # 6. Brahmagupta formalized the profound emptiness
    text = text.replace(
        "Brahmagupta formalized the profound emptiness",
        "Brahmagupta of Bhinmal (Rajasthan) formalized the profound emptiness"
    )
    # 7. Then came Brahmagupta, who in the 7th century, introduced rules
    text = text.replace(
        "Then came Brahmagupta, who in the 7th century, introduced rules",
        "Then came Brahmagupta, who in 7th-century Bhinmal (Rajasthan), introduced rules"
    )
    return text

def main():
    if not INPUT_FILE.exists():
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Check API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    print(f"Loading cache...")
    cache = load_cache()

    print(f"Reading V1 dataset...")
    examples = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples.")

    # Find which ones need rewriting
    to_rewrite = []
    for idx, ex in enumerate(examples):
        convs = ex.get("conversations", [])
        for c_idx, msg in enumerate(convs):
            role = msg.get("from") or msg.get("pr") or ""
            val = msg.get("value", "")
            if role == "gpt":
                # Check for first-person patterns
                has_first_person = False
                val_lower = val.lower()
                for pattern in FIRST_PERSON_PATTERNS:
                    if re.search(pattern, val_lower):
                        has_first_person = True
                        break
                
                # Check if already cached
                h = get_hash(val)
                if has_first_person and h not in cache:
                    to_rewrite.append((idx, c_idx, val, h))

    print(f"Found {len(to_rewrite)} GPT responses containing first-person memories that need rewriting.")

    # Process rewrites with ThreadPoolExecutor (max_workers=2)
    if to_rewrite:
        import threading
        cache_lock = threading.Lock()
        print("Rewriting first-person memories via Groq API (parallel max_workers=2 using meta-llama/llama-4-scout)...")
        
        models_to_use = ["meta-llama/llama-4-scout-17b-16e-instruct"]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(rewrite_first_person, val, client, models_to_use[i % len(models_to_use)]): (idx, c_idx, val, h)
                for i, (idx, c_idx, val, h) in enumerate(to_rewrite)
            }
            
            for future in tqdm(as_completed(futures), total=len(futures)):
                idx, c_idx, val, h = futures[future]
                try:
                    rewritten = future.result()
                    if rewritten != val:
                        with cache_lock:
                            cache[h] = rewritten
                            save_cache(cache)
                except Exception as e:
                    print(f"\nError processing rewrite for line {idx}: {e}")
        print("Caching completed.")

    # Apply rewrites and Brahmagupta fixes to all examples
    cleaned_count = 0
    brahmagupta_count = 0
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for idx, ex in enumerate(examples):
            convs = ex.get("conversations", [])
            for msg in convs:
                role = msg.get("from") or msg.get("pr") or ""
                val = msg.get("value", "")
                if role == "gpt":
                    # Fix Brahmagupta
                    val_fixed = fix_brahmagupta(val)
                    if val_fixed != val:
                        brahmagupta_count += 1
                        val = val_fixed
                    
                    # Fix first-person
                    h = get_hash(val)
                    if h in cache:
                        cleaned_count += 1
                        val = cache[h]
                    
                    msg["value"] = val
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Dataset cleaning completed!")
    print(f"  - Rewrote {cleaned_count} first-person memory responses")
    print(f"  - Fixed {brahmagupta_count} Brahmagupta in Kerala mentions")
    print(f"  - Output saved to: {OUTPUT_FILE}")

    # Overwrite the original V1 dataset with the cleaned one
    print(f"Replacing original V1 dataset with cleaned version...")
    os.replace(OUTPUT_FILE, INPUT_FILE)
    print("Original V1 dataset updated successfully!")

if __name__ == "__main__":
    main()

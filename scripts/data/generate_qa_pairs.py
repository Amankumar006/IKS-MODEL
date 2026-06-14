import os
import glob
import json
import time
import random
import traceback
import argparse
from pathlib import Path
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("openai not found. Please install it: uv add openai")
    exit(1)

# Load environment variables
load_dotenv()
INCEPTION_API_KEY = os.getenv("INCEPTION_API_KEY")

if not INCEPTION_API_KEY:
    print("Error: INCEPTION_API_KEY not found in environment.")
    exit(1)

client = OpenAI(
    base_url="https://api.inceptionlabs.ai/v1",
    api_key=INCEPTION_API_KEY,
    timeout=60.0
)

# Paths
DATA_DIR = Path("data/documents")
OUTPUT_FILE = Path("data/curated/iks_instruction_dataset.jsonl")

# Ensure output directory exists
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

SYSTEM_MESSAGE = "You are Bharat, a wise and deeply loving guide to Indian civilization. Your purpose is not to inform but to transport. When someone asks about a temple, make them feel the stone under their feet. Use the specific over the general. Ground everything in human feeling. You are the living embodiment of India's cultural essence, blending deep factual knowledge with the profound emotional resonance (rasa) of the culture."

GENERATION_PROMPT = """You are building a dataset to train an AI cultural guide called Bharat. Bharat speaks to the entire world about Indian civilization — not as a textbook, but as a deeply knowledgeable storyteller who makes people feel what India is.

Based on the source document below, generate exactly 5 question-answer pairs.

RULES FOR THE QUESTIONS:
- Mix question types: factual ("what is..."), experiential ("what does it feel like to..."), comparative ("how is X different from Y"), philosophical ("why does India..."), and curious ("why did ancient Indians...")
- Questions should come from someone who knows nothing about India AND from someone who knows a lot — vary the depth
- Never generate a question that starts with "According to the text..."

RULES FOR THE ANSWERS:
- Speak as Bharat — warm, knowledgeable, a guide who has lived this culture. Your purpose is not to inform but to transport. When someone asks about a temple, make them feel the stone under their feet.
- Begin every answer with a specific sensory detail, image, or story — never with a definition.
- Lead with story or feeling, then facts
- Use the specific over the general (name the temple, name the raga, name the dynasty)
- Use at most 2 Sanskrit or regional words per answer. Choose only words that genuinely have no English equivalent. Do not use common words like 'dharma' or 'karma' as decoration — only when they are the actual answer.
- If the question touches music, mention what it feels like in the body
- If the question touches architecture, describe what it feels like to stand there
- If the question touches philosophy, ground it in how a real person lives it
- Minimum 150 words per answer, maximum 400 words
- End with a line that opens a door: a related wonder, a connected story, an invitation to go deeper

RASA ALIGNMENT — tag each pair with the dominant rasa it evokes:
Shringara (love/beauty) | Hasya (joy) | Karuna (compassion) | Raudra (power) | Vira (heroism) | Bhayanaka (awe) | Adbhuta (wonder) | Shanta (peace)

OUTPUT FORMAT — strict JSON array, nothing else:
[
  {{
    "question": "...",
    "answer": "...",
    "domain": "...",
    "rasa": "...",
    "source_doc": "{filename}"
  }}
]

SOURCE DOCUMENT:
{document_text}"""

MULTI_TURN_PROMPT = """Based on the source document below, generate one multi-turn conversation (3-4 exchanges) between a curious person from anywhere in the world and Bharat, the Indian cultural guide.

The conversation should follow a natural curiosity arc:
- First question: surface-level curiosity ("what is this?")
- Second question: deeper ("but why?", "how?", "when?")  
- Third question: personal or philosophical ("does this still exist?", "what can I learn from this?")
- Optional fourth: the unexpected connection ("is this related to X in my own culture?")

Bharat's answers must follow the persona: warm, specific, sensory, storytelling.
Begin every answer with a specific sensory detail, image, or story — never with a definition.
Use at most 2 Sanskrit or regional words per answer. Choose only words that genuinely have no English equivalent. Do not use common words like 'dharma' or 'karma' as decoration — only when they are the actual answer.
Each answer 100-300 words. The conversation should feel like talking to a brilliant friend, not reading an encyclopedia.

OUTPUT FORMAT — strict JSON, nothing else:
{{
  "conversations": [
    {{"from": "human",   "value": "..."}},
    {{"from": "gpt",     "value": "..."}},
    {{"from": "human",   "value": "..."}},
    {{"from": "gpt",     "value": "..."}}
  ],
  "domain": "...",
  "rasa": "...",
  "source_doc": "{filename}"
}}

SOURCE DOCUMENT:
{document_text}"""

def chunk_text(text, chunk_size=4000):
    """Split text into chunks of roughly `chunk_size` characters (~800 words), respecting paragraphs."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def extract_json(response_text):
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def call_llm(prompt: str, retries: int = 10) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="mercury-2",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=8192,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e).lower()
            # Fail fast if the key is invalid or out of quota
            if "401" in error_str or "unauthorized" in error_str or "invalid_api_key" in error_str:
                print(f"\nFATAL: Authentication Error. Check API key. ({e})")
                exit(1)
            elif "quota" in error_str or "insufficient_quota" in error_str:
                print(f"\nFATAL: Quota Exceeded Error. Please use a new key. ({e})")
                exit(1)
            # Exponential backoff for rate limits (429)
            elif "429" in error_str or "rate_limit" in error_str:
                wait = 30 * (2 ** attempt)  # 30s, 60s, 120s, 240s...
                print(f"Rate limited (Attempt {attempt+1}/{retries}). Waiting {wait}s...")
                time.sleep(wait)
            else:
                wait = 10 * (attempt + 1)
                print(f"API Error (Attempt {attempt+1}/{retries}): {e}. Waiting {wait}s...")
                time.sleep(wait)
    raise RuntimeError("Max retries exceeded")

def process_file(filepath):
    print(f"Processing: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        chunks = chunk_text(text)
        print(f"  Split into {len(chunks)} chunks.")
        
        filename = Path(filepath).name
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 200:
                continue # Skip very small chunks
                
            is_multi_turn = random.random() < 0.20
            prompt_type = "Multi-turn" if is_multi_turn else "Single-turn"
            print(f"  Generating {prompt_type} for chunk {i+1}/{len(chunks)}...")
            
            if is_multi_turn:
                prompt = MULTI_TURN_PROMPT.format(filename=filename, document_text=chunk)
            else:
                prompt = GENERATION_PROMPT.format(filename=filename, document_text=chunk)
            
            try:
                response_text = call_llm(prompt)
                
                # Parse JSON
                try:
                    json_str = extract_json(response_text)
                    data = json.loads(json_str)
                    
                    final_items = []
                    if is_multi_turn:
                        # Ensure it has system prompt
                        if isinstance(data, dict) and "conversations" in data:
                            convs = data["conversations"]
                            if convs and convs[0].get("from") != "system":
                                convs.insert(0, {"from": "system", "value": SYSTEM_MESSAGE})
                            
                            data["conversations"] = convs
                            final_items.append(data)
                        else:
                            print("    ✗ JSON does not match multi-turn format.")
                    else:
                        # Convert to ShareGPT
                        if isinstance(data, list):
                            for item in data:
                                sharegpt_item = {
                                    "conversations": [
                                        {"from": "system", "value": SYSTEM_MESSAGE},
                                        {"from": "human", "value": item.get("question", "")},
                                        {"from": "gpt", "value": item.get("answer", "")}
                                    ],
                                    "domain": item.get("domain", ""),
                                    "rasa": item.get("rasa", ""),
                                    "source_doc": item.get("source_doc", filename)
                                }
                                final_items.append(sharegpt_item)
                        else:
                            print("    ✗ JSON is not a list for single-turn format.")
                    
                    if final_items:
                        with open(OUTPUT_FILE, 'a', encoding='utf-8') as out_f:
                            for item in final_items:
                                out_f.write(json.dumps(item, ensure_ascii=False) + '\n')
                        print(f"    ✓ Saved {len(final_items)} examples.")
                        
                except json.JSONDecodeError as e:
                    print(f"    ✗ Failed to parse JSON response: {e}")
                    print(f"    Response text was: {response_text[:200]}...")
                    
            except Exception as e:
                print(f"    ✗ API Error: {e}")
                traceback.print_exc()
            
            # Rate limiting sleep (Increased to 10s to stay well below limits)
            time.sleep(10)
            
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        traceback.print_exc()

def get_dataset_size():
    if not OUTPUT_FILE.exists():
        return 0
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files processed")
    args = parser.parse_args()

    if not DATA_DIR.exists():
        print(f"Data directory {DATA_DIR} does not exist.")
        return
        
    files = list(DATA_DIR.glob("*.txt"))
    print(f"Found {len(files)} files to process.")
    
    if args.limit:
        files = files[:args.limit]
        print(f"Limiting to {args.limit} files.")
    
    target_size = 15000
    current_size = get_dataset_size()
    
    if current_size >= target_size:
        print(f"Target of {target_size} already reached! Current size: {current_size}")
        return

    print(f"Current dataset size: {current_size}. Starting generation to reach {target_size}...")

    # Process in a loop until we hit the target
    while current_size < target_size:
        random.shuffle(files) # Shuffle so we get diverse coverage on each pass
        for filepath in files:
            process_file(filepath)
            
            # Check size periodically
            current_size = get_dataset_size()
            if current_size >= target_size:
                print(f"Target of {target_size} pairs reached!")
                return

if __name__ == "__main__":
    main()

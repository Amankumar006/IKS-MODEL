"""Generate expanded datasets B, D, E in bulk using the Groq API.
Generates unique factual QAs, calibrated QAs, and style-switching topics.
"""

import os
import json
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load explicitly from the repo root .env
load_dotenv("/Users/amankumar/Aman/IKS-Model/.env")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment or .env file.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Output Paths
DATA_DIR = Path("/Users/amankumar/Aman/IKS-Model/data/curated")
FACTUAL_FILE = DATA_DIR / "expanded_factual_qa.jsonl"
CALIBRATION_FILE = DATA_DIR / "expanded_calibration.jsonl"
STYLE_FILE = DATA_DIR / "expanded_style_switching.jsonl"

DATA_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Prompts
FACTUAL_PROMPT = """You are an expert compiler of datasets for Indian Knowledge Systems (IKS).
Generate exactly 50 unique factual question-answer pairs about Indian civilization, covering history, geography, arts, science, and philosophy.

REQUIREMENTS:
1. Short Answers: Each answer must be short and direct, at most 3 sentences.
2. Diversity: Cover a wide range of IKS topics (e.g. temples, mathematical discoveries, classical music/dance, philosophical terms).
3. Do NOT generate duplicates of standard questions. Create unique, diverse, and interesting questions.
4. Output format: Return ONLY a raw JSON array of objects, with no markdown code blocks, no introductory or concluding text.

JSON structure:
[
  {
    "question": "What century was the Sun Temple at Konark built?",
    "answer": "The Sun Temple at Konark was built in the 13th century CE, commissioned by King Narasimhadeva I of the Eastern Ganga Dynasty.",
    "domain": "History"
  }
]
"""

CALIBRATION_PROMPT = """You are an expert compiler of datasets for Indian Knowledge Systems.
Generate exactly 20 unique question-answer pairs that teach epistemic honesty, uncertainty, and calibration of evidence.

REQUIREMENTS:
1. Cover topics with disputed, uncertain, or mythological origins (e.g. origin of chess, historicity of epics, claims of ancient flight, etc.).
2. Each item must have a "confidence" label, which must be exactly one of: "Evidence: Strong", "Evidence: Moderate", "Evidence: Weak", "Traditional Account", "Scholarly Consensus".
3. The answer must start with the bracketed confidence tag (except for "Evidence: Strong" where it is optional but preferred) and explain the state of evidence objectively and honestly.
4. Output format: Return ONLY a raw JSON array of objects, with no markdown code blocks, no introductory or concluding text.

JSON structure:
[
  {
    "confidence": "Evidence: Weak",
    "question": "Did ancient India have airplanes?",
    "answer": "[Evidence: Weak for literal interpretation] There is no historical or archaeological evidence of functional aircraft in ancient India. Vimanas in texts like the Ramayana represent mythological flying vehicles and ancient imagination rather than documented technology."
  }
]
"""

STYLE_PROMPT = """You are an expert compiler of datasets for Indian Knowledge Systems.
Generate exactly 10 unique style-switching topics, each with three different assistant response modes: Guide, Scholar, and Companion.

REQUIREMENTS:
1. Guide: Immersive, warm, narrative, rich in sensory detail. Start with a sensory image. (approx 60-120 words).
2. Scholar: Academic, objective, referenced, cite sources or historical consensus. (approx 60-120 words).
3. Companion: Conversational, brief, natural. A 1-2 sentence response. (approx 20-40 words).
4. Each mode response MUST start with `[MODE=Guide]`, `[MODE=Scholar]`, or `[MODE=Companion]` respectively.
5. Output format: Return ONLY a raw JSON array of objects, with no markdown code blocks, no introductory or concluding text.

JSON structure:
[
  {
    "q": "Tell me about Ajanta Caves.",
    "guide": "[MODE=Guide]\\n\\nStep into the cool basalt shadows of Ajanta...",
    "scholar": "[MODE=Scholar]\\n\\nThe Ajanta Caves are 30 rock-cut Buddhist cave monuments in Maharashtra, dating from the 2nd century BCE to about 480 CE...",
    "companion": "[MODE=Companion]\\n\\nAjanta is a group of ancient Buddhist rock-cut caves in Maharashtra, famous for their beautiful wall paintings and stone carvings."
  }
]
"""

def clean_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def call_groq(prompt):
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4096,
                timeout=90
            )
            content = clean_response(response.choices[0].message.content)
            # Try parsing to validate it's JSON
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("Failed after 5 attempts")

def generate_factual(target_count):
    print(f"Generating Factual QAs (Target: {target_count})...")
    count = 0
    with open(FACTUAL_FILE, "w", encoding="utf-8") as f:
        while count < target_count:
            try:
                data = call_groq(FACTUAL_PROMPT)
                if isinstance(data, list):
                    for item in data:
                        if "question" in item and "answer" in item:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                            count += 1
                    print(f"  Generated {count}/{target_count} factual QAs...")
                else:
                    print("  Warning: Groq response was not a list.")
            except Exception as e:
                print(f"  Error generating factual batch: {e}")
            time.sleep(2)

def generate_calibration(target_count):
    print(f"Generating Calibrated QAs (Target: {target_count})...")
    count = 0
    with open(CALIBRATION_FILE, "w", encoding="utf-8") as f:
        while count < target_count:
            try:
                data = call_groq(CALIBRATION_PROMPT)
                if isinstance(data, list):
                    for item in data:
                        if "question" in item and "answer" in item and "confidence" in item:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                            count += 1
                    print(f"  Generated {count}/{target_count} calibrated QAs...")
                else:
                    print("  Warning: Groq response was not a list.")
            except Exception as e:
                print(f"  Error generating calibration batch: {e}")
            time.sleep(2)

def generate_style(target_count):
    print(f"Generating Style Switching Topics (Target: {target_count})...")
    count = 0
    with open(STYLE_FILE, "w", encoding="utf-8") as f:
        while count < target_count:
            try:
                data = call_groq(STYLE_PROMPT)
                if isinstance(data, list):
                    for item in data:
                        if all(k in item for k in ("q", "guide", "scholar", "companion")):
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                            count += 1
                    print(f"  Generated {count}/{target_count} style-switching topics...")
                else:
                    print("  Warning: Groq response was not a list.")
            except Exception as e:
                print(f"  Error generating style batch: {e}")
            time.sleep(2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--factual", type=int, default=750)
    parser.add_argument("--calibration", type=int, default=100)
    parser.add_argument("--style", type=int, default=50)
    args = parser.parse_args()

    # Run generations
    if args.factual > 0:
        generate_factual(args.factual)
    if args.calibration > 0:
        generate_calibration(args.calibration)
    if args.style > 0:
        generate_style(args.style)

    print("Generation complete!")

if __name__ == "__main__":
    main()

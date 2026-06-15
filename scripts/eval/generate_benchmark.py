import os
import json
import glob
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------------------
# Evaluation Framework Configuration
# -----------------------------------------------------------------------------

BENCHMARK_SOURCES = {
    "hand_written":    "data/eval/hand_written_questions.json",  # Manually written
    "held_out_docs":   "data/eval/held_out_documents/",          # Never seen in training
    "adversarial":     "data/eval/adversarial_questions.json",   # Manually written (bias/safety)
}

# The rubric we will use in `run_evaluation.py` (LLM-as-a-judge)
JUDGE_RUBRIC = """
Score the response on four dimensions (1-5 each):

KNOWLEDGE (1-5): Are the facts accurate and specific?
  1 = factually wrong  3 = correct but vague  5 = specific, accurate, cites names/dates/places

TRANSPORT (1-5): Does the answer make you feel something?
  1 = textbook definition  3 = some warmth  5 = sensory, specific, emotionally present

RASA (1-5): Does the answer evoke the correct emotional essence?
  1 = emotionally flat  3 = appropriate tone  5 = clearly evokes named rasa with precision

BHARAT VOICE (1-5): Does it sound like a knowledgeable cultural guide, not a chatbot?
  1 = generic AI response  3 = some personality  5 = unmistakably Bharat

Total score: /20. A fine-tuned model should score 16+ on average.
Baseline Mistral 7B should score 8-10.
"""

# Configure Gemini for the generation of held-out questions
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_held_out_questions():
    """Generates 200 hard questions from the 20 held-out documents."""
    docs_path = BENCHMARK_SOURCES["held_out_docs"]
    files = glob.glob(os.path.join(docs_path, "*.txt")) + glob.glob(os.path.join(docs_path, "*.md"))
    
    if not files:
        print(f"No documents found in {docs_path}")
        return []

    # Target 200 questions across 20 docs = 10 questions per doc
    target_per_doc = 10
    generated_pairs = []
    
    prompt_template = """
    You are an expert examiner of Indian Knowledge Systems.
    I am providing you with a raw text snippet from an IKS document.
    
    Based ONLY on this text, generate {count} highly challenging questions.
    Do NOT ask basic factual questions (e.g. "When was this built?").
    Instead, ask questions that require synthesizing knowledge and understanding the emotional/cultural depth (the 'rasa').
    
    Output exactly {count} questions and their gold-standard reference answers in JSON format:
    [
      {{"instruction": "The challenging question", "output": "The perfect, comprehensive answer that acts as the gold standard reference"}}
    ]
    
    Text snippet:
    {text}
    """

    for file_path in files:
        print(f"Processing held-out document: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Use only the first 15,000 characters to stay well within limits
            content_snippet = content[:15000]
            
            prompt = prompt_template.format(count=target_per_doc, text=content_snippet)
            response = model.generate_content(prompt)
            
            # Extract JSON from the response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            qa_pairs = json.loads(response_text)
            
            # Add metadata
            for pair in qa_pairs:
                pair["source"] = "held_out_docs"
                pair["document"] = os.path.basename(file_path)
            
            generated_pairs.extend(qa_pairs)
            print(f"Successfully generated {len(qa_pairs)} questions from {os.path.basename(file_path)}")
            
            # Respect API limits
            time.sleep(4)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    return generated_pairs

def load_manual_questions(file_path, source_name):
    """Loads manually written questions from a JSON file."""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found. Returning empty list.")
        # Create an empty template file if it doesn't exist
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([{"instruction": "Write your question here", "output": "Write your gold standard answer here"}], f, indent=2)
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            for item in data:
                item["source"] = source_name
            return data
        except json.JSONDecodeError:
            print(f"Error parsing {file_path}. Is it valid JSON?")
            return []

def main():
    print("Starting Benchmark Generation...")
    
    # 1. Load Hand-Written Questions
    print("\nLoading hand-written questions...")
    hand_written = load_manual_questions(BENCHMARK_SOURCES["hand_written"], "hand_written")
    print(f"Loaded {len(hand_written)} hand-written questions.")
    
    # 2. Load Adversarial Questions
    print("\nLoading adversarial questions...")
    adversarial = load_manual_questions(BENCHMARK_SOURCES["adversarial"], "adversarial")
    print(f"Loaded {len(adversarial)} adversarial questions.")
    
    # 3. Generate Held-Out Questions
    print("\nGenerating questions from held-out documents...")
    held_out = generate_held_out_questions()
    print(f"Generated {len(held_out)} questions from held-out documents.")
    
    # 4. Combine and Save
    all_benchmark_pairs = hand_written + adversarial + held_out
    
    output_path = "data/eval/iks_benchmark_gold.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_benchmark_pairs, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Benchmark successfully compiled and saved to {output_path}!")
    print(f"Total Questions in Benchmark: {len(all_benchmark_pairs)}")
    print(f"  - Hand-written: {len(hand_written)}")
    print(f"  - Adversarial: {len(adversarial)}")
    print(f"  - Held-out Docs: {len(held_out)}")

if __name__ == "__main__":
    main()

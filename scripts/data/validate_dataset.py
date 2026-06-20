"""Script to perform static dataset validation on the IKS-Bharat V2 training dataset.

Ensures that the compiled dataset does not contain multi-turn examples,
excessive invitation endings, duplicate questions, or formatting violations.
Outputs a detailed data quality dashboard and computes a Dataset Quality Score.
"""

import json
import re
from pathlib import Path

# Target V2 dataset file
DATASET_FILE = Path(__file__).resolve().parents[2] / "data" / "curated" / "iks_v2_instruction_dataset.jsonl"

# Invitation endings to count
INVITATIONS = [
    "would you like to",
    "come, let me show you",
    "come, let us",
    "perhaps we can explore",
    "shall we",
    "let us journey",
    "shall we journey",
    "would you care to",
    "may i take you",
    "perhaps you'd like",
    "perhaps you would like",
]

# Greetings and Utility keywords for Dataset C classification
GREETINGS = {
    "hi", "hello", "namaste", "good morning", "hey", "hey there", "hii", 
    "greetings", "who are you?", "what's your name?", "hello! my name is alex.", 
    "hello! my name is priya.", "hi, quick question.", "hey, i need help with something."
}

UTILITY_KEYWORDS = [
    "sql query", "regex", "http", "binary of", "reverse this string", "what is 2 + 2", 
    "what is 17 x 23", "what is 5 + 5", "square root of", "prime number", "python list", 
    "python dict", "python function", "csv format", "markdown table"
]


def count_sentences(text: str) -> int:
    """Split text into sentences using simple heuristics and return count."""
    text = text.strip()
    if not text:
        return 0
    # Split by periods, exclamation marks, or question marks followed by spaces/newlines
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return len([s for s in sentences if s.strip()])


def validate_dataset(filepath: Path) -> dict:
    """Run data quality analysis over the dataset file."""
    if not filepath.exists():
        return {"error": f"Dataset file not found at: {filepath}"}

    total_examples = 0
    multi_turn_count = 0
    duplicate_count = 0
    invitation_count = 0
    one_word_violations = 0
    sentence_violations = 0
    json_validity_count = 0
    json_total_prompts = 0

    # Dataset balance variables
    calibration_examples = 0
    contrastive_examples = 0
    greeting_examples = 0
    factual_examples = 0
    persona_examples = 0

    # Output length trackers
    word_counts = []
    seen_examples = set()

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            total_examples += 1

            try:
                ex = json.loads(line)
            except json.JSONDecodeError:
                continue

            convs = ex.get("conversations", [])
            
            # 1. Multi-turn check (ShareGPT unpacked must have exactly system, human, gpt = 3 turns)
            if len(convs) != 3:
                multi_turn_count += 1
                continue

            sys_val = convs[0].get("value", "")
            human_val = convs[1].get("value", "")
            gpt_val = convs[2].get("value", "")
            human_lower = human_val.lower().strip()
            words = gpt_val.split()

            # 2. Duplicate check (Verify exact prompt + response duplicate matches)
            # Only count duplicates for Dataset A (Persona)
            is_persona = (
                not gpt_val.startswith("[Evidence:") and
                not gpt_val.startswith("[Traditional") and
                not gpt_val.startswith("[Scholarly") and
                not any(sys_val.endswith(m) for m in ["[MODE=Guide]", "[MODE=Scholar]", "[MODE=Companion]"]) and
                not (human_lower in GREETINGS or any(kw in human_lower for kw in UTILITY_KEYWORDS)) and
                not (len(words) <= 50 and count_sentences(gpt_val) <= 3)
            )
            example_hash = hash((human_val.strip(), gpt_val.strip()))
            if example_hash in seen_examples:
                if is_persona:
                    duplicate_count += 1
            else:
                seen_examples.add(example_hash)

            # 3. Output lengths
            word_counts.append(len(words))

            # 4. Invitation ending check
            tail = gpt_val.strip().lower()[-150:]
            if any(inv in tail for inv in INVITATIONS):
                invitation_count += 1

            # 5. Format and rule compliance checks (Constraint checks)
            
            # One-word prompt constraint violations
            if "one word" in human_lower or "exactly one word" in human_lower or "one word only" in human_lower:
                cleaned = re.sub(r'[^\w\s]', '', gpt_val)
                if len(cleaned.split()) > 1:
                    one_word_violations += 1

            # Sentence count constraints
            if "exactly two sentences" in human_lower:
                s_count = count_sentences(gpt_val)
                if s_count != 2:
                    sentence_violations += 1
            elif "exactly one sentence" in human_lower or "one sentence only" in human_lower or "summarize in one sentence" in human_lower:
                s_count = count_sentences(gpt_val)
                if s_count != 1:
                    sentence_violations += 1

            # JSON validity check
            if "json only" in human_lower or "respond only in json" in human_lower or "respond in json" in human_lower:
                json_total_prompts += 1
                try:
                    json.loads(gpt_val)
                    json_validity_count += 1
                except json.JSONDecodeError:
                    # Check if wrapped in codeblocks
                    blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', gpt_val, re.DOTALL)
                    if blocks:
                        try:
                            json.loads(blocks[0])
                            json_validity_count += 1
                        except json.JSONDecodeError:
                            pass

            # 6. Inferred dataset categorisation
            if gpt_val.startswith("[Evidence:") or gpt_val.startswith("[Traditional") or gpt_val.startswith("[Scholarly"):
                calibration_examples += 1
            elif any(sys_val.endswith(m) for m in ["[MODE=Guide]", "[MODE=Scholar]", "[MODE=Companion]"]):
                contrastive_examples += 1
            elif human_lower in GREETINGS or any(kw in human_lower for kw in UTILITY_KEYWORDS):
                greeting_examples += 1
            elif len(words) <= 50 and count_sentences(gpt_val) <= 3:
                factual_examples += 1
            else:
                persona_examples += 1

    # Length stats
    word_counts.sort()
    avg_len = int(sum(word_counts) / len(word_counts)) if word_counts else 0
    median_len = word_counts[len(word_counts) // 2] if word_counts else 0
    p95_len = word_counts[int(len(word_counts) * 0.95)] if word_counts else 0
    max_len = word_counts[-1] if word_counts else 0

    # Compute quality score (starts at 100)
    score = 100.0
    # Deductions
    score -= (multi_turn_count * 10.0)  # Heavy penalty for multi-turn
    score -= (duplicate_count * 0.1)    # Penalty for duplicates (0.1 pt per duplicate)
    score -= (one_word_violations * 1.5)
    score -= (sentence_violations * 1.0)
    
    if json_total_prompts > 0:
        json_fail = json_total_prompts - json_validity_count
        score -= (json_fail * 5.0)

    # Invitation endings threshold (expect < 3%)
    invitation_pct = (invitation_count / total_examples) * 100 if total_examples > 0 else 0
    if invitation_pct > 3.0:
        score -= (invitation_pct - 3.0) * 2.0

    score = max(0.0, min(100.0, score))

    report = {
        "total_examples": total_examples,
        "multi_turn": multi_turn_count,
        "duplicates": duplicate_count,
        "avg_len": avg_len,
        "median_len": median_len,
        "p95_len": p95_len,
        "max_len": max_len,
        "invitation_pct": invitation_pct,
        "one_word_violations": one_word_violations,
        "sentence_violations": sentence_violations,
        "json_validity": (json_validity_count / json_total_prompts) * 100 if json_total_prompts > 0 else 100.0,
        "calibration_examples": calibration_examples,
        "contrastive_examples": contrastive_examples,
        "greeting_examples": greeting_examples,
        "factual_examples": factual_examples,
        "persona_examples": persona_examples,
        "score": score
    }

    return report


def main():
    print("=========================================")
    print("          DATASET VALIDATION             ")
    print("=========================================")
    
    report = validate_dataset(DATASET_FILE)
    if "error" in report:
        print(f"❌ {report['error']}")
        return

    print(f"Examples              : {report['total_examples']}")
    print(f"Duplicates            : {report['duplicates']}")
    print(f"Multi-turn            : {report['multi_turn']}")
    print(f"Average Output Length : {report['avg_len']} words")
    print(f"Median                : {report['median_len']}")
    print(f"95th Percentile       : {report['p95_len']}")
    print(f"Maximum               : {report['max_len']}")
    print(f"Invitation Endings    : {report['invitation_pct']:.1f}%")
    print(f"One-word violations   : {report['one_word_violations']}")
    print(f"Sentence violations   : {report['sentence_violations']}")
    print(f"JSON validity         : {report['json_validity']:.1f}%")
    print(f"Calibration examples  : {report['calibration_examples']}")
    print(f"Contrastive examples  : {report['contrastive_examples']}")
    print(f"Utility/Greeting ex   : {report['greeting_examples']}")
    print(f"Factual QA examples   : {report['factual_examples']}")
    print(f"Persona examples      : {report['persona_examples']}")
    
    status_symbol = "✅" if report["score"] >= 95.0 else "⚠️"
    print("-----------------------------------------")
    print(f"Dataset Score         : {report['score']:.1f}/100 {status_symbol}")
    print("=========================================")


if __name__ == "__main__":
    main()

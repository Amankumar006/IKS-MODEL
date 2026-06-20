"""
IKS V2 Dataset Builder
======================
Builds the five-component training dataset for IKS-Bharat V2.

Dataset composition (target ~15,000 examples):
  Dataset A — Persona       70%  (~10,500)  V1 data, new prompt, multi-turn unpacked
  Dataset B — Factual QA    15%  ( ~2,250)  Short direct answers
  Dataset C — Utility       10%  ( ~1,500)  Greetings + instruction following + boring
  Dataset D — Contrastive    3%  (   ~450)  Bad → Good pairs + style switching
  Dataset E — Calibration    2%  (   ~300)  Uncertainty + confidence labels

Usage:
  python iks_v2_dataset_builder.py              # full build
  python iks_v2_dataset_builder.py --dry-run    # validate without writing
  python iks_v2_dataset_builder.py --stats      # print distribution only
  python iks_v2_dataset_builder.py --output path/to/output.jsonl
"""

import json
import random
import argparse
import sys
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
THIS_DIR   = Path(__file__).parent
REPO_ROOT  = THIS_DIR.parent
V1_DATASET = REPO_ROOT / "data" / "curated" / "iks_instruction_dataset.jsonl"
OUTPUT     = REPO_ROOT / "data" / "curated" / "iks_v2_instruction_dataset.jsonl"

EXPANDED_FACTUAL_QA = REPO_ROOT / "data" / "curated" / "expanded_factual_qa.jsonl"
EXPANDED_CALIBRATION = REPO_ROOT / "data" / "curated" / "expanded_calibration.jsonl"
EXPANDED_STYLE_SWITCHING = REPO_ROOT / "data" / "curated" / "expanded_style_switching.jsonl"

# ---------------------------------------------------------------------------
# Import V2 system prompt
# ---------------------------------------------------------------------------
sys.path.insert(0, str(THIS_DIR))
try:
    from iks_system_prompt import SYSTEM_PROMPT_V2
except ImportError:
    raise ImportError(
        "Could not import SYSTEM_PROMPT_V2 from iks_system_prompt.py. "
        "Make sure both files are in the same directory."
    )

# ---------------------------------------------------------------------------
# Target counts
# ---------------------------------------------------------------------------
TARGET_TOTAL = 15_000
TARGET_A     = int(TARGET_TOTAL * 0.70)   # 10,500
TARGET_B     = int(TARGET_TOTAL * 0.15)   #  2,250
TARGET_C     = int(TARGET_TOTAL * 0.10)   #  1,500
TARGET_D     = int(TARGET_TOTAL * 0.03)   #    450
TARGET_E     = int(TARGET_TOTAL * 0.02)   #    300

# Invitation phrases used to detect and soften V1 endings
INVITATION_PHRASES = [
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

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def make_example(system: str, human: str, gpt: str,
                 domain: str = "", rasa: str = "", source: str = "") -> dict:
    """Return a ShareGPT-format training example."""
    conv = [
        {"from": "system", "value": system},
        {"from": "human",  "value": human},
        {"from": "gpt",    "value": gpt},
    ]
    example: dict = {"conversations": conv}
    if domain:
        example["domain"] = domain
    if rasa:
        example["rasa"] = rasa
    if source:
        example["source_doc"] = source
    return example


def has_invitation_ending(text: str) -> bool:
    """Return True if the response ends with a reflexive invitation phrase."""
    tail = text.strip().lower()[-200:]
    return any(phrase in tail for phrase in INVITATION_PHRASES)


def soften_invitation(text: str) -> str:
    """
    Remove the last sentence if it contains an invitation phrase.
    Keeps the response complete — just drops the reflexive hook.
    """
    text_stripped = text.strip()
    for phrase in INVITATION_PHRASES:
        pattern = rf"\s*([^.!?\n]*(?:{re.escape(phrase)})[^.!?\n]*[.!?]\s*)$"
        match = re.search(pattern, text_stripped, re.IGNORECASE)
        if match:
            trimmed = text_stripped[:-len(match.group(0))].strip()
            if trimmed:
                if not trimmed[-1] in ".!?":
                    trimmed += "."
                return trimmed
    return text


def _role(msg: dict) -> str:
    """Return the role of a message, handling both 'from' and 'pr' key variants."""
    return msg.get("from") or msg.get("pr") or ""


def unpack_multiturn(conversations: list, new_system: str) -> list:
    """
    Unpack a multi-turn conversation into individual (system, human, gpt) triples.

    V1 packed format:   [system, human, gpt, human, gpt, human, gpt]
    V2 unpacked format: [[system, human1, gpt1], [system, human2, gpt2], ...]

    This prevents the model from learning to predict the next human turn.
    Handles V1 dataset inconsistency where some messages use 'pr' instead of 'from'.
    """
    turns = [m for m in conversations if _role(m) != "system"]

    pairs = []
    i = 0
    while i + 1 < len(turns):
        human_msg = turns[i]
        gpt_msg   = turns[i + 1]
        if _role(human_msg) == "human" and _role(gpt_msg) == "gpt":
            pairs.append([
                {"from": "system", "value": new_system},
                {"from": "human",  "value": human_msg["value"]},
                {"from": "gpt",    "value": gpt_msg["value"]},
            ])
        i += 2
    return pairs


def get_question_variations(q: str) -> list:
    """Generate 3 variations of a question for dataset diversity."""
    q = q.strip()
    if not q:
        return []
    
    # Clean ending punctuation if any, but preserve it for the final variations
    ends_with_q = q.endswith("?")
    base = q[:-1] if ends_with_q else q
    
    # Generate variations
    # Var 1: original question
    var1 = q
    
    # Var 2 & Var 3: based on first word
    words = q.split()
    first_word = words[0].lower() if words else ""
    if first_word in ("tell", "describe", "explain", "show", "list", "name"):
        q_lowered = q[0].lower() + q[1:]
        var2 = f"Please {q_lowered}"
        var3 = f"Could you {q_lowered}?" if not q_lowered.endswith("?") else f"Could you {q_lowered}"
    else:
        var2 = f"Please tell me: {q}"
        var3 = f"Could you explain: {q}"
        
    return [var1, var2, var3]


def get_question_variations_4(q: str) -> list:
    """Generate 4 variations of a question for dataset diversity."""
    q = q.strip()
    if not q:
        return []
    
    # Clean ending punctuation if any, but preserve it for the final variations
    ends_with_q = q.endswith("?")
    base = q[:-1] if ends_with_q else q
    
    # Generate variations
    # Var 1: original question
    var1 = q
    
    # Var 2, 3, 4: based on first word
    words = q.split()
    first_word = words[0].lower() if words else ""
    if first_word in ("tell", "describe", "explain", "show", "list", "name"):
        q_lowered = q[0].lower() + q[1:]
        var2 = f"Please {q_lowered}"
        var3 = f"Could you {q_lowered}?" if not q_lowered.endswith("?") else f"Could you {q_lowered}"
        var4 = f"Would you {q_lowered}?" if not q_lowered.endswith("?") else f"Would you {q_lowered}"
    else:
        var2 = f"Please tell me: {q}"
        var3 = f"Could you explain: {q}"
        var4 = f"Would you tell me: {q}"
        
    return [var1, var2, var3, var4]


# ---------------------------------------------------------------------------
# Dataset A — Persona (V1 data, new prompt, unpacked, invitations softened)
# ---------------------------------------------------------------------------

def build_dataset_a(max_samples: int) -> list:
    """
    Load V1 data, swap system prompt to V2, unpack multi-turn conversations,
    and soften 90% of reflexive invitation endings.
    """
    print(f"  [A] Loading V1 dataset from {V1_DATASET} ...")
    if not V1_DATASET.exists():
        print(f"  [A] WARNING: V1 dataset not found at {V1_DATASET}. Skipping.")
        return []

    raw_examples = []
    with open(V1_DATASET, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    raw_examples.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    print(f"  [A] Loaded {len(raw_examples):,} raw V1 examples.")

    unpacked = []
    invitation_softened = 0
    invitation_kept     = 0

    for ex in raw_examples:
        convs  = ex.get("conversations", [])
        pairs  = unpack_multiturn(convs, SYSTEM_PROMPT_V2)
        domain = ex.get("domain", "")
        rasa   = ex.get("rasa", "")
        source = ex.get("source_doc", "")

        for pair in pairs:
            gpt_val = pair[2]["value"]

            # 90% of invitation endings softened; 10% kept for naturalness
            if has_invitation_ending(gpt_val):
                if random.random() < 0.90:
                    pair[2]["value"] = soften_invitation(gpt_val)
                    invitation_softened += 1
                else:
                    invitation_kept += 1

            unpacked.append({
                "conversations": pair,
                "domain": domain,
                "rasa": rasa,
                "source_doc": source,
                "dataset": "A",
            })

    print(f"  [A] After unpacking: {len(unpacked):,} individual pairs.")
    print(f"  [A] Invitation endings softened: {invitation_softened:,} | kept: {invitation_kept:,}")

    random.shuffle(unpacked)
    selected = unpacked[:max_samples]
    print(f"  [A] Sampled {len(selected):,} examples for Dataset A.")
    return selected


# ---------------------------------------------------------------------------
# Dataset B — Factual QA + Short Answers
# ---------------------------------------------------------------------------

def build_dataset_b(max_samples: int) -> list:
    """
    Short, direct IKS-domain factual QA pairs loaded from expanded_factual_qa.jsonl.
    Generates 4 question variations to prevent prompt duplication and repeat capping collapse.
    """
    print(f"  [B] Loading expanded factual QA from {EXPANDED_FACTUAL_QA} ...")
    if not EXPANDED_FACTUAL_QA.exists():
        raise FileNotFoundError(f"Expanded factual QA file not found at {EXPANDED_FACTUAL_QA}")

    raw_pairs = []
    with open(EXPANDED_FACTUAL_QA, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                raw_pairs.append(json.loads(line))

    # Deduplicate base questions to ensure 100% uniqueness
    seen_qs = set()
    unique_pairs = []
    for item in raw_pairs:
        q = item["question"]
        if q not in seen_qs:
            seen_qs.add(q)
            unique_pairs.append(item)
    raw_pairs = unique_pairs

    print(f"  [B] Loaded {len(raw_pairs):,} unique factual QA pairs.")

    all_examples = []
    for item in raw_pairs:
        q = item["question"]
        a = item["answer"]
        domain = item.get("domain", "Factual QA")
        
        variations = get_question_variations_4(q)
        for var in variations:
            ex = make_example(SYSTEM_PROMPT_V2, var, a,
                              domain=domain, source="dataset_b_factual_qa")
            ex["dataset"] = "B"
            all_examples.append(ex)

    random.shuffle(all_examples)
    selected = all_examples[:max_samples]
    print(f"  [B] Built {len(selected):,} factual QA examples from {len(all_examples):,} variants.")
    return selected


# ---------------------------------------------------------------------------
# Dataset C — Greetings + Instruction Following + Boring Utility
# ---------------------------------------------------------------------------

def build_dataset_c(max_samples: int) -> list:
    """
    Greetings, instruction following, boring utility — none should trigger
    cultural framing. Generated programmatically to ensure diversity and correctness.
    """
    # 1. Greetings: 15 unique prompts from the GREETINGS set in validate_dataset.py
    greetings_base = [
        ("Hi", "Namaste! How can I help you today?"),
        ("Hello", "Hello! How can I assist you?"),
        ("Namaste", "Namaste! What would you like to explore today?"),
        ("Good morning", "Good morning! How can I help you?"),
        ("Hey", "Hey! What can I do for you?"),
        ("Hey there", "Hello! What would you like to know?"),
        ("Who are you?", "I'm Bharat — a guide to Indian civilization and culture. What would you like to explore?"),
        ("What's your name?", "I'm Bharat. How can I help you today?"),
        ("Hello! My name is Alex.", "Hello Alex! Great to meet you. What can I help you with?"),
        ("Hii", "Namaste! How can I help you?"),
        ("Hey, good evening!", "Good evening! What would you like to know?"),
        ("Greetings", "Greetings! How can I assist you today?"),
        ("hello! my name is priya.", "Hello Priya! What can I help you with?"),
        ("hi, quick question.", "Of course — go ahead!"),
        ("hey, i need help with something.", "Happy to help. What do you need?"),
    ]
    
    examples = []
    
    # 2. Binary of: e.g. "What is the binary of 42?" -> "101010"
    for i in range(1, 251):
        num = 10 + i * 7
        binary_val = bin(num)[2:]
        human = f"What is the binary of {num}?"
        gpt = f"The binary representation of {num} is {binary_val}."
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 3. Reverse this string: e.g. "Reverse this string: 'Namaste'" -> "etsamaN"
    words_to_reverse = [
        "apple", "banana", "cherry", "dragonfruit", "elderberry", "fig", "grape", "honeydew",
        "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry",
        "strawberry", "tangerine", "ugli", "vanilla", "watermelon", "yam", "zucchini",
        "python", "programming", "algorithm", "database", "network", "server", "client",
        "browser", "compiler", "interpreter", "variable", "function", "class", "object"
    ]
    for i in range(250):
        w = words_to_reverse[i % len(words_to_reverse)]
        w_unique = f"{w}{i}"
        reversed_w = w_unique[::-1]
        human = f"Reverse this string: '{w_unique}'"
        gpt = f"{reversed_w}"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 4. Square root of:
    for i in range(1, 151):
        val = 10 + i
        square = val * val
        human = f"What is the square root of {square}?"
        gpt = f"{val}."
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 5. Prime number check:
    primes = [
        11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
        101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181,
        191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277,
        281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383,
        389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487,
        491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601
    ]
    for i in range(250):
        if i % 2 == 0:
            p = primes[(i // 2) % len(primes)]
            human = f"Is {p} a prime number?"
            gpt = "Yes."
        else:
            comp = 10 + i * 3
            if comp in primes:
                comp += 1
            human = f"Is {comp} a prime number?"
            gpt = "No."
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 6. Python list:
    for i in range(220):
        n = 3 + (i % 10)
        mult = 2 + i
        lst = [mult * k for k in range(1, n + 1)]
        human = f"Create a python list containing the first {n} multiples of {mult}."
        gpt = f"`{lst}`"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 7. Python dict:
    for i in range(120):
        n = 2 + (i % 5)
        d = {f"item_{k}_{i}": k * 10 for k in range(1, n + 1)}
        human = f"Create a python dict mapping item names to values for {n} items, reference ID {i}."
        gpt = f"`{d}`"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 8. Python function:
    for i in range(120):
        func_names = ["calculate_mean", "find_maximum", "count_elements", "sum_even_numbers", "get_squares"]
        fname = func_names[i % len(func_names)]
        human = f"Write a python function named `{fname}_{i}` that takes a list of numbers and processes them."
        gpt = f"```python\ndef {fname}_{i}(numbers):\n    # Programmatic implementation {i}\n    return [x for x in numbers if x > 0]\n```"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 9. SQL query:
    for i in range(220):
        tables = ["employees", "orders", "products", "customers", "inventory", "sales"]
        tbl = tables[i % len(tables)]
        col = f"id_{i}"
        human = f"Write a sql query to select all records from table '{tbl}' where {col} is greater than 100."
        gpt = f"```sql\nSELECT * FROM {tbl} WHERE {col} > 100;\n```"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 10. Regex:
    for i in range(120):
        char = chr(97 + (i % 26))
        human = f"Write a regex to match strings starting with the letter '{char}' and having index {i}."
        gpt = f"`^{char}.*{i}$`"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 11. CSV format:
    for i in range(100):
        human = f"Convert this data to csv format: name=Item_{i}, price={10+i}, quantity={5+i}."
        gpt = f"name,price,quantity\nItem_{i},{10+i},{5+i}"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # 12. Markdown table:
    for i in range(100):
        human = f"Format this data as a markdown table: ID={i}, Value={i*2}."
        gpt = f"| ID | Value |\n| --- | --- |\n| {i} | {i*2} |"
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Utility")
        ex["dataset"] = "C"
        examples.append(ex)

    # Shuffle utility pool
    random.shuffle(examples)

    # Return greetings plus requested utility samples
    greetings_unique = []
    for human, gpt in greetings_base:
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Greeting")
        ex["dataset"] = "C"
        greetings_unique.append(ex)

    if max_samples < 999999:
        needed_utility = max_samples - len(greetings_unique)
        selected = greetings_unique + examples[:needed_utility]
        print(f"  [C] Built {len(selected):,} greeting/instruction/utility examples.")
        return selected
        
    combined_all = greetings_unique + examples
    print(f"  [C] Built {len(combined_all):,} greeting/instruction/utility candidates.")
    return combined_all


# ---------------------------------------------------------------------------
# Dataset D — True Contrastive + Style Switching
# ---------------------------------------------------------------------------

def build_dataset_d(max_samples: int) -> list:
    """
    True contrastive examples: the GOOD completion directly counters V1's
    learned bad behaviors. Also includes [MODE=...] style-switching examples.
    """
    anti_invitation = [
        ("Hi", "Namaste! How can I help you today?"),
        ("Hello", "Hello! How can I assist you?"),
        ("Good morning", "Good morning! How can I help?"),
        ("Hii", "Namaste! How can I help?"),
        ("Hello! My name is Priya.", "Hello Priya! What can I help you with?"),
        ("Hi, quick question.", "Of course — go ahead!"),
        ("Hey, I need help with something.", "Happy to help. What do you need?"),
    ]

    instruction_obeying = [
        ("Reply with exactly one word. Capital of Bihar?", "Patna"),
        ("One word only: National bird of India?", "Peacock"),
        ("Answer yes or no: Is yoga from India?", "Yes"),
        ("Answer yes or no: Is Kathak a South Indian dance?", "No"),
        ("What is 2 + 2? One word.", "4"),
        ("Reply in JSON: three Indian philosophy schools.",
         '{"schools": ["Vedanta", "Nyaya", "Samkhya"]}'),
    ]

    print(f"  [D] Loading expanded style-switching from {EXPANDED_STYLE_SWITCHING} ...")
    if not EXPANDED_STYLE_SWITCHING.exists():
        raise FileNotFoundError(f"Expanded style-switching file not found at {EXPANDED_STYLE_SWITCHING}")

    style_switching = []
    with open(EXPANDED_STYLE_SWITCHING, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                style_switching.append(json.loads(line))

    # Deduplicate base questions to ensure 100% uniqueness
    seen_qs = set()
    unique_topics = []
    for topic in style_switching:
        q = topic["q"]
        if q not in seen_qs:
            seen_qs.add(q)
            unique_topics.append(topic)
    style_switching = unique_topics

    print(f"  [D] Loaded {len(style_switching):,} unique style-switching topics.")

    examples = []

    # Populate anti-invitation with duplicates up to capping limit (MAX_REPEATS=3)
    for human, gpt in anti_invitation:
        for _ in range(3):
            ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Greeting")
            ex["dataset"] = "D"
            ex["contrastive_type"] = "anti_invitation"
            examples.append(ex)

    # Populate instruction-obeying with duplicates up to capping limit (MAX_REPEATS=3)
    for human, gpt in instruction_obeying:
        for _ in range(3):
            ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Instruction")
            ex["dataset"] = "D"
            ex["contrastive_type"] = "instruction_obeying"
            examples.append(ex)

    # Populate style switching using the question variations to prevent capping collapse (4 variations)
    for topic in style_switching:
        base_q = topic["q"]
        variations = get_question_variations_4(base_q)
        
        for var in variations:
            for mode_key, mode_label in [("guide", "Guide"), ("scholar", "Scholar"),
                                          ("companion", "Companion")]:
                raw_response = topic[mode_key]
                pattern = rf"^\[MODE={re.escape(mode_label)}\]\s*"
                clean_response = re.sub(pattern, "", raw_response, flags=re.IGNORECASE).strip()
                
                mode_system_prompt = SYSTEM_PROMPT_V2 + f"\n\n[MODE={mode_label}]"
                
                ex = make_example(mode_system_prompt, var, clean_response,
                                  domain="Style Switching")
                ex["dataset"] = "D"
                ex["contrastive_type"] = f"style_{mode_label.lower()}"
                examples.append(ex)

    random.shuffle(examples)
    selected = examples[:max_samples]
    print(f"  [D] Built {len(selected):,} contrastive / style-switching examples from {len(examples):,} variants.")
    return selected


# ---------------------------------------------------------------------------
# Dataset E — Knowledge Calibration with Confidence Labels
# ---------------------------------------------------------------------------

def build_dataset_e(max_samples: int) -> list:
    """
    Teaches epistemic honesty: uncertainty, scholarly disagreement,
    and evidence-based refusal. Each example carries a confidence label.
    Loaded from expanded_calibration.jsonl.
    """
    print(f"  [E] Loading expanded calibration from {EXPANDED_CALIBRATION} ...")
    if not EXPANDED_CALIBRATION.exists():
        raise FileNotFoundError(f"Expanded calibration file not found at {EXPANDED_CALIBRATION}")

    raw_calibrations = []
    with open(EXPANDED_CALIBRATION, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                raw_calibrations.append(json.loads(line))

    # Deduplicate base questions to ensure 100% uniqueness
    seen_qs = set()
    unique_calibrations = []
    for item in raw_calibrations:
        q = item["question"]
        if q not in seen_qs:
            seen_qs.add(q)
            unique_calibrations.append(item)
    raw_calibrations = unique_calibrations

    print(f"  [E] Loaded {len(raw_calibrations):,} unique calibration pairs.")

    all_examples = []
    for item in raw_calibrations:
        confidence = item["confidence"]
        q = item["question"]
        a = item["answer"]
        
        variations = get_question_variations(q)
        for var in variations:
            ex = make_example(SYSTEM_PROMPT_V2, var, a,
                              domain="Knowledge Calibration",
                              source="dataset_e_calibration")
            ex["dataset"] = "E"
            ex["confidence"] = confidence
            all_examples.append(ex)

    random.shuffle(all_examples)
    selected = all_examples[:max_samples]
    print(f"  [E] Built {len(selected):,} knowledge calibration examples from {len(all_examples):,} variants.")
    return selected


# ---------------------------------------------------------------------------
# Main build pipeline
# ---------------------------------------------------------------------------

def build_all(dry_run: bool = False, stats_only: bool = False,
              output_path: Path = OUTPUT) -> None:
    random.seed(42)

    print("\n  IKS V2 Dataset Builder")
    print("  " + "=" * 50)

    # 1. Load/build all candidates (no truncation yet)
    dataset_a = build_dataset_a(999999)
    dataset_b = build_dataset_b(999999)
    dataset_c = build_dataset_c(999999)
    dataset_d = build_dataset_d(999999)
    dataset_e = build_dataset_e(999999)

    combined = dataset_a + dataset_b + dataset_c + dataset_d + dataset_e

    # Normalization of metadata fields
    rasa_mapping = {
        "Adbhutha": "Adbhuta",
        "Adbuta": "Adbhuta",
        "Adbhut": "Adbhuta",
        "adbhuta": "Adbhuta",
    }
    
    for ex in combined:
        if "domain" in ex and ex["domain"]:
            ex["domain"] = ex["domain"].strip().title()
        if "rasa" in ex and ex["rasa"]:
            r = ex["rasa"].strip()
            if r in rasa_mapping:
                ex["rasa"] = rasa_mapping[r]
            else:
                ex["rasa"] = r.title() if r else r

    # Deduplicate and Cap repeats per unique prompt (question)
    seen_pairs = set()
    unique_examples = []
    
    for ex in combined:
        convs = ex.get("conversations", [])
        if len(convs) != 3:
            continue
        sys_val = convs[0]["value"]
        human_val = convs[1]["value"]
        gpt_val = convs[2]["value"]
        
        key = (sys_val, human_val, gpt_val)
        if key not in seen_pairs:
            seen_pairs.add(key)
            unique_examples.append(ex)
            
    print(f"  [Deduplication] Removed {len(combined) - len(unique_examples):,} exact duplicates.")
    
    # Prioritize B, C, D, E examples during capping to prevent collisions with A
    non_persona = [ex for ex in unique_examples if ex.get("dataset") != "A"]
    persona = [ex for ex in unique_examples if ex.get("dataset") == "A"]
    
    random.shuffle(non_persona)
    random.shuffle(persona)
    
    ordered_examples = non_persona + persona
    
    MAX_REPEATS = 3
    prompt_counts = {}
    balanced = []
    
    for ex in ordered_examples:
        convs = ex.get("conversations", [])
        human_val = convs[1]["value"]
        
        if prompt_counts.get(human_val, 0) < MAX_REPEATS:
            balanced.append(ex)
            prompt_counts[human_val] = prompt_counts.get(human_val, 0) + 1
            
    print(f"  [Capping] Capped repeats to MAX_REPEATS={MAX_REPEATS}. Keep {len(balanced):,} examples (removed {len(unique_examples) - len(balanced):,} repeated prompts).")
    
    # Group by dataset tag
    groups = {"A": [], "B": [], "C": [], "D": [], "E": []}
    for ex in balanced:
        tag = ex.get("dataset", "?")
        if tag in groups:
            groups[tag].append(ex)
            
    # Sample from each group to get exact targets
    def sample_group(lst, target, label):
        if len(lst) < target:
            print(f"  [Warning] Group {label} has only {len(lst)} examples after capping (target {target}). Keeping all.")
            return lst
        return random.sample(lst, target)

    dataset_a = sample_group(groups["A"], TARGET_A, "A")
    dataset_b = sample_group(groups["B"], TARGET_B, "B")
    dataset_c = sample_group(groups["C"], TARGET_C, "C")
    dataset_d = sample_group(groups["D"], TARGET_D, "D")
    dataset_e = sample_group(groups["E"], TARGET_E, "E")

    combined = dataset_a + dataset_b + dataset_c + dataset_d + dataset_e
    random.shuffle(combined)

    # Distribution report
    print(f"\n  Distribution Report")
    print(f"  {'─' * 40}")
    totals = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for ex in combined:
        tag = ex.get("dataset", "?")
        if tag in totals:
            totals[tag] += 1

    labels = {"A": "Persona", "B": "Factual QA", "C": "Utility",
              "D": "Contrastive", "E": "Calibration"}
    for tag, count in totals.items():
        pct = count / len(combined) * 100 if combined else 0
        print(f"  Dataset {tag} ({labels[tag]:<14}): {count:>6,}  ({pct:.1f}%)")
    print(f"  {'─' * 40}")
    print(f"  {'Total':<20}: {len(combined):>6,}")

    if stats_only:
        print("\n  --stats flag set. No file written.\n")
        return

    if dry_run:
        print("\n  --dry-run flag set. Validating first 5 examples...\n")
        for i, ex in enumerate(combined[:5]):
            convs = ex.get("conversations", [])
            assert len(convs) == 3, f"Example {i}: expected 3 turns, got {len(convs)}"
            assert convs[0]["from"] == "system"
            assert convs[1]["from"] == "human"
            assert convs[2]["from"] == "gpt"
            assert convs[0]["value"].startswith(SYSTEM_PROMPT_V2), \
                f"Example {i}: wrong system prompt"
            print(f"  ok Example {i + 1}: dataset={ex.get('dataset')} | "
                  f"human={convs[1]['value'][:60]!r}")
        print("\n  Validation passed. No file written (dry-run).\n")
        return

    # Write output — strip internal metadata keys
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in combined:
            clean = {k: v for k, v in ex.items()
                     if k not in ("dataset", "contrastive_type", "confidence")}
            f.write(json.dumps(clean, ensure_ascii=False) + "\n")

    print(f"\n  Written {len(combined):,} examples to {output_path}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build the IKS-Bharat V2 training dataset."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate structure without writing output file.")
    parser.add_argument("--stats", action="store_true",
                        help="Print distribution report only, no file written.")
    parser.add_argument("--output", type=Path, default=OUTPUT,
                        help="Output JSONL path.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility.")
    args = parser.parse_args()

    random.seed(args.seed)
    build_all(
        dry_run=args.dry_run,
        stats_only=args.stats,
        output_path=args.output,
    )

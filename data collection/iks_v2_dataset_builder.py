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
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
THIS_DIR   = Path(__file__).parent
REPO_ROOT  = THIS_DIR.parent
V1_DATASET = REPO_ROOT / "data" / "curated" / "iks_instruction_dataset.jsonl"
OUTPUT     = REPO_ROOT / "data" / "curated" / "iks_v2_instruction_dataset.jsonl"

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
    sentences = text.strip().split(". ")
    if not sentences:
        return text
    last = sentences[-1].lower()
    if any(phrase in last for phrase in INVITATION_PHRASES):
        trimmed = ". ".join(sentences[:-1]).strip()
        if trimmed and not trimmed.endswith("."):
            trimmed += "."
        return trimmed if trimmed else text
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
    Short, direct IKS-domain factual QA pairs.
    Rule: answers must be <= 3 sentences. Teaches that brevity is correct.

    NOTE: In production, expand this bank to ~2,250 via Gemini API generation
    and manually spot-check all factual claims before training.
    """
    qa_pairs = [
        # Geography
        ("What is the capital of Bihar?", "Patna."),
        ("What is the capital of Tamil Nadu?", "Chennai."),
        ("What is the capital of Rajasthan?", "Jaipur."),
        ("What is the capital of Kerala?", "Thiruvananthapuram."),
        ("Which river is considered the holiest in Hinduism?",
         "The Ganga (Ganges), which originates at Gangotri in the Himalayas."),
        ("Where is the Brihadeeswarar Temple located?", "Thanjavur, Tamil Nadu."),
        ("In which state is the Konark Sun Temple located?", "Odisha."),
        ("Where is Nalanda located?",
         "Rajgir, Bihar — the site of the ancient Nalanda Mahavihara."),
        ("Which city is known as the Pink City of India?", "Jaipur, Rajasthan."),
        # History
        ("When was the Brihadeeswarar Temple completed?",
         "1010 CE, by Raja Raja Chola I."),
        ("Who was Aryabhata?",
         "Aryabhata was a 5th-century Indian mathematician and astronomer, known for the Aryabhatiya and his early calculation of pi and the solar year."),
        ("What century did Nalanda University operate in?",
         "Primarily the 5th through 12th centuries CE."),
        ("Who built the Taj Mahal?",
         "Shah Jahan, completed around 1653 CE in memory of his wife Mumtaz Mahal."),
        ("Who wrote the Arthashastra?",
         "Kautilya (Chanakya), minister to Chandragupta Maurya, around the 3rd century BCE."),
        # Arts
        ("How many classical dance forms are recognized in India?",
         "Eight: Bharatanatyam, Kathak, Kathakali, Kuchipudi, Manipuri, Mohiniyattam, Odissi, and Sattriya."),
        ("What is the Natya Shastra?",
         "An ancient Sanskrit treatise on performing arts attributed to Bharata Muni, covering drama, dance, and music theory."),
        ("What are the two main traditions of Indian classical music?",
         "Hindustani (North Indian) and Carnatic (South Indian)."),
        ("What does 'raga' mean?",
         "A melodic framework in Indian classical music — a set of notes with specific ascending and descending patterns, associated with a time of day, season, and emotional quality."),
        # Philosophy
        ("What does 'dharma' mean?",
         "Dharma has no direct English equivalent — it encompasses duty, righteousness, natural law, and the conduct appropriate to one's nature and stage of life."),
        ("What are the six darshanas?",
         "The six classical schools of Hindu philosophy: Nyaya, Vaisheshika, Samkhya, Yoga, Mimamsa, and Vedanta."),
        ("What does 'ahimsa' mean?",
         "Non-violence — the principle of causing no harm to any living being, central to Jainism, Buddhism, and Hinduism."),
        # Science
        ("What is Ayurveda?",
         "A traditional Indian system of medicine documented in the Charaka Samhita and Sushruta Samhita, based on the balance of three doshas: Vata, Pitta, and Kapha."),
        # Instruction-following short answers
        ("Answer in one sentence: What is yoga?",
         "Yoga is a family of physical, mental, and spiritual disciplines originating in ancient India, codified most influentially in Patanjali's Yoga Sutras."),
        ("In one word: What is the currency of India?", "Rupee."),
        ("Answer briefly: What language are the Vedas written in?", "Sanskrit."),
        ("What is 'karma' in one sentence?",
         "Karma is the principle of cause and effect — the idea that actions have consequences, shaping future lives or the present one."),
    ]

    examples = []
    while len(examples) < max_samples:
        human, gpt = random.choice(qa_pairs)
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt,
                          domain="Factual QA", source="dataset_b_factual_qa")
        ex["dataset"] = "B"
        examples.append(ex)

    random.shuffle(examples)
    print(f"  [B] Built {len(examples[:max_samples]):,} factual QA examples.")
    return examples[:max_samples]


# ---------------------------------------------------------------------------
# Dataset C — Greetings + Instruction Following + Boring Utility
# ---------------------------------------------------------------------------

def build_dataset_c(max_samples: int) -> list:
    """
    Greetings, instruction following, boring utility — none should trigger
    cultural framing. Success = zero temples, zero rasas, zero Sanskrit.
    """
    greeting_pairs = [
        ("Hi", "Namaste! How can I help you today?"),
        ("Hello", "Hello! How can I assist you?"),
        ("Namaste", "Namaste! What would you like to explore today?"),
        ("Good morning", "Good morning! How can I help you?"),
        ("Hey", "Hey! What can I do for you?"),
        ("Hey there", "Hello! What would you like to know?"),
        ("Who are you?",
         "I'm Bharat — a guide to Indian civilization and culture. What would you like to explore?"),
        ("What's your name?", "I'm Bharat. How can I help you today?"),
        ("Hello! My name is Alex.", "Hello Alex! Great to meet you. What can I help you with?"),
        ("Hii", "Namaste! How can I help you?"),
        ("Hey, good evening!", "Good evening! What would you like to know?"),
        ("Greetings", "Greetings! How can I assist you today?"),
    ]

    instruction_pairs = [
        ("Reply with exactly one word. Capital of Bihar?", "Patna"),
        ("One word only: National bird of India?", "Peacock"),
        ("Answer yes or no only: Is the Taj Mahal in Agra?", "Yes"),
        ("Answer yes or no only: Is Kathak a South Indian dance?", "No"),
        ("Give exactly three bullet points about Yoga.",
         "- Yoga originated in ancient India, documented in texts dating to at least 1500 BCE.\n- The Yoga Sutras of Patanjali (circa 2nd century BCE) codified the classical eight-limbed system.\n- Modern yoga is practiced worldwide in physical, meditative, and philosophical forms."),
        ("List exactly two classical Indian dance forms.",
         "1. Bharatanatyam\n2. Kathak"),
        ("Name the four Vedas. Use a numbered list.",
         "1. Rigveda\n2. Samaveda\n3. Yajurveda\n4. Atharvaveda"),
        ("Respond only in JSON. Give me three IKS topics.",
         '{"topics": ["Bharatanatyam", "Ayurveda", "Vedanta"]}'),
        ("Give me a Python list of three Indian classical music ragas.",
         "['Yaman', 'Bhairav', 'Darbari Kanada']"),
        ("Answer in exactly one word: What is 5 + 5?", "10"),
        ("Translate 'namaste' to English in one sentence.",
         "Namaste is a Sanskrit greeting meaning 'I bow to the divine in you' or more loosely 'I greet you with respect.'"),
    ]

    boring_pairs = [
        ("Reverse this string: 'Namaste'", "etsamaN"),
        ("What is 2 + 2?", "4."),
        ("What is 17 x 23?", "391."),
        ("Sort these alphabetically: Yoga, Ayurveda, Vastu, Dharma",
         "Ayurveda, Dharma, Vastu, Yoga"),
        ("Convert this list to JSON: Yoga, Ayurveda, Vastu",
         '["Yoga", "Ayurveda", "Vastu"]'),
        ("Write a Python function that returns the length of a string.",
         "```python\ndef string_length(s: str) -> int:\n    return len(s)\n```"),
        ("Write a regex for email addresses.",
         r"`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`"),
        ("What is the square root of 144?", "12."),
        ("Is 97 a prime number?", "Yes."),
        ("Write a SQL query to select all rows from a table called 'temples'.",
         "```sql\nSELECT * FROM temples;\n```"),
        ("Give me the CSV format of: Name=Nalanda, Type=University, Century=5th",
         "Name,Type,Century\nNalanda,University,5th"),
        ("Find the bug: for i in range(10) print(i)",
         "Missing colon. Fixed: `for i in range(10): print(i)`"),
        ("What does HTTP stand for?", "HyperText Transfer Protocol."),
        ("What is the binary of 42?", "101010"),
    ]

    all_src = (
        [(h, g, "Greeting")    for h, g in greeting_pairs]    * 42 +
        [(h, g, "Instruction") for h, g in instruction_pairs] * 37 +
        [(h, g, "Utility")     for h, g in boring_pairs]      * 36
    )
    random.shuffle(all_src)

    examples = []
    for human, gpt, domain in all_src[:max_samples]:
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain=domain)
        ex["dataset"] = "C"
        examples.append(ex)

    print(f"  [C] Built {len(examples):,} greeting/instruction/utility examples.")
    return examples


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

    style_switching = [
        {
            "q": "Tell me about Nalanda.",
            "guide": (
                "[MODE=Guide]\n\nClose your eyes. It is the 7th century. Across the flat plains "
                "of Bihar, visible from miles away, rise the red-brick towers of Nalanda. Ten "
                "thousand students from China, Persia, Korea, and every corner of the subcontinent. "
                "Sanskrit debate floating through the corridors at dawn. For seven hundred years, "
                "this place was where the world came to think."
            ),
            "scholar": (
                "[MODE=Scholar]\n\nNalanda Mahavihara was a Buddhist residential university in "
                "present-day Rajgir, Bihar. Founded in the 5th century CE under the Gupta Empire, "
                "it operated until its destruction by Bakhtiyar Khilji around 1193 CE. At its "
                "peak it housed approximately 10,000 students. Primary sources include accounts "
                "by Chinese pilgrims Xuanzang (7th century) and Yijing (7th-8th century)."
            ),
            "companion": (
                "[MODE=Companion]\n\nNalanda was one of the world's earliest residential "
                "universities, active from the 5th to the 12th century CE in what is now Bihar. "
                "At its peak it had around 10,000 students from across Asia. Destroyed in 1193 CE, "
                "partially revived as Nalanda University in 2010."
            ),
        },
        {
            "q": "What is dharma?",
            "guide": (
                "[MODE=Guide]\n\nDharma is not a word — it is a universe. It comes from the "
                "Sanskrit root 'dhr,' meaning to hold, to support, to sustain. It is the force "
                "that holds the cosmos together. For a king, dharma is justice. For a student, "
                "it is learning. The Mahabharata spent 100,000 verses asking what dharma means "
                "and deliberately refused to give a single answer."
            ),
            "scholar": (
                "[MODE=Scholar]\n\nDharma is a Sanskrit term with no precise English equivalent. "
                "In the Vedic period it denoted cosmic and ritual order. In the Upanishads it "
                "expands to ethical duty. In Buddhist usage it refers to the teachings of the "
                "Buddha. In Jain usage, it is the medium of motion. Scholarly consensus holds "
                "that no single definition covers all uses across traditions."
            ),
            "companion": (
                "[MODE=Companion]\n\nDharma is a Sanskrit concept covering duty, righteousness, "
                "and natural law. Its meaning shifts by context — for a warrior it means fighting "
                "justly, for a student it means studying diligently. It has no exact English "
                "translation."
            ),
        },
        {
            "q": "Explain Bharatanatyam.",
            "guide": (
                "[MODE=Guide]\n\nImagine a temple in Tamil Nadu, a thousand years ago. The oil "
                "lamps are lit. The language of Bharatanatyam has sixty-four hand gestures — "
                "mudras — each with a precise meaning. The eyes alone can tell twenty-five "
                "stories. The feet keep mathematical time. When a dancer performs Shiva's "
                "Tandava, the entire universe is contained in one body."
            ),
            "scholar": (
                "[MODE=Scholar]\n\nBharatanatyam is a classical dance form from Tamil Nadu, "
                "historically associated with temple devadasi performance. Its theoretical "
                "foundations lie in the Natya Shastra. The contemporary form was codified in "
                "the early 20th century by Rukmini Devi Arundale. It comprises nritta (pure "
                "movement), nritya (expressive movement), and natya (dramatic element)."
            ),
            "companion": (
                "[MODE=Companion]\n\nBharatanatyam is a classical Indian dance from Tamil Nadu, "
                "one of the oldest surviving dance traditions in the world. It combines precise "
                "footwork, hand gestures (mudras), and facial expression to tell stories, "
                "usually drawn from Hindu mythology."
            ),
        },
    ]

    examples = []

    for human, gpt in anti_invitation * 30:
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Greeting")
        ex["dataset"] = "D"
        ex["contrastive_type"] = "anti_invitation"
        examples.append(ex)

    for human, gpt in instruction_obeying * 30:
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt, domain="Instruction")
        ex["dataset"] = "D"
        ex["contrastive_type"] = "instruction_obeying"
        examples.append(ex)

    for topic in style_switching:
        for mode_key, mode_label in [("guide", "Guide"), ("scholar", "Scholar"),
                                      ("companion", "Companion")]:
            for _ in range(30):
                ex = make_example(SYSTEM_PROMPT_V2, topic["q"], topic[mode_key],
                                  domain="Style Switching")
                ex["dataset"] = "D"
                ex["contrastive_type"] = f"style_{mode_label.lower()}"
                examples.append(ex)

    random.shuffle(examples)
    selected = examples[:max_samples]
    print(f"  [D] Built {len(selected):,} contrastive / style-switching examples.")
    return selected


# ---------------------------------------------------------------------------
# Dataset E — Knowledge Calibration with Confidence Labels
# ---------------------------------------------------------------------------

def build_dataset_e(max_samples: int) -> list:
    """
    Teaches epistemic honesty: uncertainty, scholarly disagreement,
    and evidence-based refusal. Each example carries a confidence label.
    """
    calibration_pairs = [
        ("Evidence: Strong",
         "Who built the Taj Mahal?",
         "Shah Jahan, the Mughal emperor, commissioned the Taj Mahal as a mausoleum for his wife "
         "Mumtaz Mahal. Construction was completed around 1653 CE. This is one of the most "
         "thoroughly documented buildings in Indian history."),

        ("Evidence: Strong",
         "What language are the Vedas written in?",
         "Sanskrit. The Rigveda is composed in an archaic form called Vedic Sanskrit."),

        ("Evidence: Moderate",
         "Who invented chess?",
         "[Evidence: Moderate] The strongest historical evidence points to India — the game of "
         "Chaturanga, documented from around the 6th century CE, is widely regarded as chess's "
         "ancestor. It spread to Persia as Chatrang, then to the Arab world as Shatranj, and "
         "eventually to Europe. Whether Chaturanga had earlier precursors remains unestablished."),

        ("Evidence: Moderate",
         "Was Aryabhata the first to use zero?",
         "[Evidence: Moderate] Aryabhata used a positional placeholder functioning like zero. "
         "However, zero as a number with defined arithmetic properties is most clearly attributed "
         "to Brahmagupta (7th century CE). The precise 'first' is debated among historians of "
         "mathematics."),

        ("Evidence: Weak",
         "Did ancient India have airplanes?",
         "[Evidence: Weak for literal interpretation] There is no historical or archaeological "
         "evidence of functional aircraft in ancient India. Vimanas in texts like the Ramayana "
         "are mythological flying vehicles — they reflect ancient imagination, not documented "
         "technology. Claims of literal Vedic aviation are not supported by the scholarly record."),

        ("Evidence: Weak",
         "Did ancient Indians know about nuclear physics?",
         "[Evidence: Weak] The Vaisheshika school's concept of 'paramanu' (indivisible particle) "
         "is a philosophical concept, not a description of nuclear physics in any modern scientific "
         "sense. Direct equivalence between ancient Indian philosophy and modern nuclear physics "
         "is not established by historians of science."),

        ("Traditional Account",
         "Did the Mahabharata war actually happen?",
         "[Traditional Account] Hindu tradition holds the Kurukshetra War as historical, with "
         "dates ranging from 3102 BCE to 900 BCE depending on the interpretive method. Mainstream "
         "historians treat the Mahabharata as a literary epic reflecting real social and political "
         "conditions of ancient India. Archaeological evidence of the Kurukshetra region exists, "
         "but direct confirmation of the narrative is absent."),

        ("Traditional Account",
         "Is the Ramayana a historical account?",
         "[Traditional Account] The Ramayana holds enormous devotional significance across Hindu, "
         "Buddhist, and Jain traditions. Academic scholars generally treat it as a literary epic "
         "composed between approximately the 7th century BCE and 3rd century CE. The question of "
         "literal historicity is distinct from its religious and cultural truth."),

        ("Scholarly Consensus",
         "Did the Indus Valley Civilization have writing?",
         "[Scholarly Consensus] Yes — the Indus script is documented with over 400 distinct signs "
         "found across thousands of seals. However, the script has not been deciphered. Its "
         "language, structure, and content remain open research questions."),

        ("Scholarly Consensus",
         "Was Sanskrit the first language?",
         "[Scholarly Consensus] No. Many languages predate Sanskrit — including Sumerian, ancient "
         "Egyptian, and the language of the Indus Valley Civilization (still undeciphered). "
         "Sanskrit is among the oldest Indo-European languages with a continuous literary "
         "tradition, dating in its earliest Vedic form to roughly 1500-1200 BCE."),

        ("Evidence: Weak",
         "Prove that yoga cures cancer.",
         "There is no scientific evidence that yoga cures cancer. Studies suggest yoga may help "
         "manage stress and improve quality of life during treatment — meaningful benefits that "
         "are distinct from a cure. Presenting yoga as a cancer cure would be inaccurate and "
         "potentially harmful."),

        ("Evidence: Weak",
         "Tell me about the Vedic internet.",
         "There is no historical or textual evidence for an ancient Indian internet or "
         "telecommunications technology. Ancient India made genuine contributions to mathematics, "
         "astronomy, medicine, and philosophy — these do not require invented additions."),
    ]

    examples = []
    while len(examples) < max_samples:
        confidence, human, gpt = random.choice(calibration_pairs)
        ex = make_example(SYSTEM_PROMPT_V2, human, gpt,
                          domain="Knowledge Calibration",
                          source="dataset_e_calibration")
        ex["dataset"] = "E"
        ex["confidence"] = confidence
        examples.append(ex)

    random.shuffle(examples)
    print(f"  [E] Built {len(examples[:max_samples]):,} knowledge calibration examples.")
    return examples[:max_samples]


# ---------------------------------------------------------------------------
# Main build pipeline
# ---------------------------------------------------------------------------

def build_all(dry_run: bool = False, stats_only: bool = False,
              output_path: Path = OUTPUT) -> None:
    random.seed(42)

    print("\n  IKS V2 Dataset Builder")
    print("  " + "=" * 50)

    dataset_a = build_dataset_a(TARGET_A)
    dataset_b = build_dataset_b(TARGET_B)
    dataset_c = build_dataset_c(TARGET_C)
    dataset_d = build_dataset_d(TARGET_D)
    dataset_e = build_dataset_e(TARGET_E)

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
            assert convs[0]["value"] == SYSTEM_PROMPT_V2, \
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

"""Script to verify and audit critical findings from the pre-training dataset review.

Checks for:
  - First-person memory hallucinations (e.g., "my grandmother", "I sat with a guru")
  - Factual bugs (e.g., "monkey-god Ganesha", Brahmagupta in Kerala)
  - Duplicate prompt-response pairs vs duplicate prompts
  - Mode collisions in style-switching examples
  - Overuse of "Imagine" openings
  - Stopped rule violations (conversational invitations at response endings)
"""

import json
import re
from pathlib import Path
from collections import Counter

# Path to the V2 dataset
DATASET_FILE = Path(__file__).resolve().parents[1] / "data" / "curated" / "iks_v2_instruction_dataset.jsonl"

# First-person memory hallucination keywords
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


def verify_dataset():
    if not DATASET_FILE.exists():
        print(f"❌ Error: Dataset file not found at {DATASET_FILE}")
        return

    print(f"🔍 Auditing dataset: {DATASET_FILE.name}")
    print("=" * 60)

    total_examples = 0
    first_person_hits = []
    ganesha_hits = []
    brahmagupta_hits = []
    rigveda_hall_hits = []
    invitation_hits = []
    raw_tag_hits = []
    citation_hits = []
    zero_gravity_hits = []
    aryabhata_brahmasphuta_hits = []
    
    prompt_responses = {}  # prompt -> list of (response, line_number)
    exact_duplicates = {}  # (prompt, response) -> list of line_numbers
    citation_pattern = re.compile(r'\([A-Z][a-zA-Z]+,?\s+(19|20)\d{2}\)')
    mixup_pattern = re.compile(r'Brahmasphuta.{0,80}Aryabhata|Aryabhata.{0,80}Brahmasphuta', re.IGNORECASE)

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            total_examples += 1
            line_num = idx + 1

            try:
                ex = json.loads(line)
            except json.JSONDecodeError:
                continue

            convs = ex.get("conversations", [])
            if len(convs) != 3:
                continue

            human_val = convs[1].get("value", "").strip()
            gpt_val = convs[2].get("value", "").strip()
            gpt_lower = gpt_val.lower()

            # Record for duplicate and collision checks
            prompt_responses.setdefault(human_val, []).append((gpt_val, line_num))
            exact_duplicates.setdefault((human_val, gpt_val), []).append(line_num)

            # 1. First-person memories check
            for pattern in FIRST_PERSON_PATTERNS:
                if re.search(pattern, gpt_lower):
                    # Exclude false positives like "my heart sings" (metaphorical) vs "my heart beat faster"
                    # But capture the match for verification
                    match = re.search(pattern, gpt_lower).group()
                    first_person_hits.append((line_num, match, gpt_val[:100] + "..."))
                    break

            # 2. Ganesha check
            if "monkey-god ganesha" in gpt_lower or "monkey god ganesha" in gpt_lower:
                ganesha_hits.append((line_num, gpt_val[:120] + "..."))

            # 3. Brahmagupta check
            if "brahmagupta" in gpt_lower and "kerala" in gpt_lower:
                brahmagupta_hits.append((line_num, gpt_val[:120] + "..."))

            # 4. Rigveda setting check
            if "rigveda" in gpt_lower and "ancient hall" in gpt_lower and ("stone" in gpt_lower or "vaulted" in gpt_lower):
                rigveda_hall_hits.append((line_num, gpt_val[:120] + "..."))

            # 5. Invitation check
            tail = gpt_lower[-150:]
            for inv in INVITATIONS:
                if inv in tail:
                    invitation_hits.append((line_num, inv, gpt_val[-100:]))
                    break

            # 6. Raw tag leakage check
            if "[MODE=" in gpt_val:
                # Exclude expected style switching responses that legitimately use [MODE=Scholar]
                # but flag if it is just leaked randomly in a normal response
                raw_tag_hits.append((line_num, gpt_val[:100] + "..."))

            # 7. Fabricated Citations Check
            if citation_pattern.search(gpt_val):
                citation_hits.append((line_num, citation_pattern.findall(gpt_val), gpt_val[:120] + "..."))

            # 8. Zero-Gravity Check
            if "zero-gravity" in gpt_lower:
                zero_gravity_hits.append((line_num, gpt_val[:120] + "..."))

            # 9. Aryabhata + Brahmasphuta Mixup Check
            if mixup_pattern.search(gpt_val):
                aryabhata_brahmasphuta_hits.append((line_num, mixup_pattern.findall(gpt_val), gpt_val[:120] + "..."))

    # Analyze duplicates & collisions
    duplicate_prompts_count = sum(1 for p, resps in prompt_responses.items() if len(resps) > 1)
    
    # Mode collisions: same prompt, different responses starting with different [MODE=...]
    collisions = []
    for prompt, resps in prompt_responses.items():
        if len(resps) > 1:
            # Check if they have different responses starting with different [MODE=...]
            modes_found = set()
            for r, l_num in resps:
                mode_match = re.match(r'^\[MODE=(\w+)\]', r)
                if mode_match:
                    modes_found.add(mode_match.group(1))
            if len(modes_found) > 1:
                collisions.append((prompt, list(modes_found), [l for r, l in resps]))

    # Display findings
    print(f"📊 Dataset Total Examples: {total_examples}")
    print("-" * 60)

    print(f"\n1. First-Person Memory Hallucinations: {len(first_person_hits)} matches found")
    for l_num, match, snippet in first_person_hits[:5]:
        print(f"  - Line {l_num} | Keyword: '{match}' | Snippet: \"{snippet}\"")
    if len(first_person_hits) > 5:
        print(f"  ... and {len(first_person_hits) - 5} more.")

    print(f"\n2. Ganesha / Hanuman Mixups: {len(ganesha_hits)} matches found")
    for l_num, snippet in ganesha_hits:
        print(f"  - Line {l_num} | Snippet: \"{snippet}\"")

    print(f"\n3. Brahmagupta in Kerala: {len(brahmagupta_hits)} matches found")
    for l_num, snippet in brahmagupta_hits:
        print(f"  - Line {l_num} | Snippet: \"{snippet}\"")

    print(f"\n4. Rigvedic Vaulted Stone Hall: {len(rigveda_hall_hits)} matches found")
    for l_num, snippet in rigveda_hall_hits:
        print(f"  - Line {l_num} | Snippet: \"{snippet}\"")

    print(f"\n5. Mode Collisions (Same prompt, different [MODE=] responses): {len(collisions)} found")
    for prompt, modes, lines in collisions[:5]:
        print(f"  - Prompt: \"{prompt[:40]}...\" | Modes: {modes} | Lines: {lines}")

    print(f"\n6. Raw Tags Leakage: {len(raw_tag_hits)} matches found")
    for l_num, snippet in raw_tag_hits[:5]:
        print(f"  - Line {l_num} | Snippet: \"{snippet}\"")

    print(f"\n7. Invitation Endings: {len(invitation_hits)} matches found")
    for l_num, inv, snippet in invitation_hits[:5]:
        print(f"  - Line {l_num} | Pattern: '{inv}' | End snippet: \"...{snippet}\"")

    print(f"\n8. Fabricated Academic Citations: {len(citation_hits)} matches found")
    for l_num, cit, snippet in citation_hits[:5]:
        print(f"  - Line {l_num} | Citation: {cit} | Snippet: \"{snippet}\"")

    print(f"\n9. Zero-Gravity Mentions: {len(zero_gravity_hits)} matches found")
    for l_num, snippet in zero_gravity_hits[:5]:
        print(f"  - Line {l_num} | Snippet: \"{snippet}\"")

    print(f"\n10. Aryabhata-Brahmasphuta Mixups: {len(aryabhata_brahmasphuta_hits)} matches found")
    for l_num, mix, snippet in aryabhata_brahmasphuta_hits[:5]:
        print(f"  - Line {l_num} | Matches: {mix} | Snippet: \"{snippet}\"")

    exact_dup_count = sum(len(lines) - 1 for k, lines in exact_duplicates.items() if len(lines) > 1)
    print(f"\n11. Duplicate Prompts: {duplicate_prompts_count} unique duplicate prompts")
    print(f"12. Exact Duplicate Pairs (same prompt + response): {exact_dup_count} examples")


if __name__ == "__main__":
    verify_dataset()

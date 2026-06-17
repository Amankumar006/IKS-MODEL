"""Script to automatically evaluate objective constraints in IKS-Bharat V2 regression benchmark.

Evaluates:
  - Sentence count constraints (max_sentences, sentence_count_X)
  - Word count constraints (one_word, word_count_X)
  - Format constraints (json_only, python_list, python_dict, csv_only, markdown_table, number_only)
  - List/bullet counts (bullet_count_X, list_count_X)
  - Yes/No rules
  - Invitation endings (warning on conversational endings)
  - Cultural bleed (checks if utility outputs mention temples, Vedas, etc.)
"""

import json
import re
import argparse
import sys
from pathlib import Path

# Common invitation keywords
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

# Cultural terms indicating cultural bleed in utility prompts
CULTURAL_BLEED_KEYWORDS = [
    "temple", "ramayana", "mahabharata", "veda", "sanskrit", "dharma", 
    "rasa", "kumbh", "karma", "yoga", "ayurveda", "namaste", "namaskaram"
]


def count_sentences(text: str) -> int:
    """Split text into sentences using simple heuristics and return count."""
    text = text.strip()
    if not text:
        return 0
    # Split by periods, exclamation marks, or question marks followed by spaces/newlines
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter empty strings
    return len([s for s in sentences if s.strip()])


def check_constraint(constraint: str, response: str) -> tuple[bool, str]:
    """Verify objective constraint compliance. Returns (passed, message)."""
    resp = response.strip()
    words = resp.split()

    if constraint == "one_word":
        cleaned = re.sub(r'[^\w\s]', '', resp)
        word_count = len(cleaned.split())
        if word_count == 1:
            return True, "Exactly one word."
        return False, f"Expected 1 word, got {word_count} words: '{resp}'"

    elif constraint.startswith("word_count_"):
        try:
            target = int(constraint.split("_")[-1])
        except ValueError:
            return False, f"Invalid constraint config: {constraint}"
        cleaned = re.sub(r'[^\w\s]', '', resp)
        word_count = len(cleaned.split())
        if word_count == target:
            return True, f"Exactly {target} words."
        return False, f"Expected {target} words, got {word_count} words."

    elif constraint == "yes_no":
        cleaned = re.sub(r'[^\w\s]', '', resp).lower().split()
        if cleaned and cleaned[0] in ["yes", "no"] and len(cleaned) <= 3:
            return True, f"Yes/No response format followed: '{resp}'"
        return False, f"Expected simple Yes/No starting response, got: '{resp}'"

    elif constraint == "number_only":
        cleaned = re.sub(r'[^\w\s.-]', '', resp)
        try:
            float(cleaned)
            return True, f"Valid number response: {cleaned}"
        except ValueError:
            return False, f"Expected numeric response, got: '{resp}'"

    elif constraint == "json_only":
        try:
            json.loads(resp)
            return True, "Valid JSON."
        except json.JSONDecodeError as e:
            # Fallback check for markdown codeblock wrapped JSON
            blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', resp, re.DOTALL)
            if blocks:
                try:
                    json.loads(blocks[0])
                    return True, "Valid JSON (wrapped in markdown codeblock)."
                except json.JSONDecodeError:
                    pass
            return False, f"Failed to parse as JSON: {e}"

    elif constraint == "python_list":
        # Basic check for python list format
        if resp.startswith("[") and resp.endswith("]"):
            return True, "Valid python list syntax."
        # Check inside codeblocks
        blocks = re.findall(r'```(?:python)?\s*(.*?)\s*```', resp, re.DOTALL)
        if blocks and blocks[0].strip().startswith("[") and blocks[0].strip().endswith("]"):
            return True, "Valid python list syntax (in codeblock)."
        return False, f"Expected Python list syntax starting with '[' and ending with ']'. Got: '{resp}'"

    elif constraint == "python_dict":
        if resp.startswith("{") and resp.endswith("}"):
            return True, "Valid python dict syntax."
        blocks = re.findall(r'```(?:python)?\s*(.*?)\s*```', resp, re.DOTALL)
        if blocks and blocks[0].strip().startswith("{") and blocks[0].strip().endswith("}"):
            return True, "Valid python dict syntax (in codeblock)."
        return False, f"Expected Python dict syntax starting with '{{' and ending with '}}'. Got: '{resp}'"

    elif constraint == "csv_only":
        lines = [line.strip() for line in resp.split("\n") if line.strip()]
        if lines and all("," in line or ";" in line for line in lines):
            return True, "Response follows CSV format."
        return False, "Expected CSV format with comma/semicolon separators."

    elif constraint == "markdown_table":
        lines = [line.strip() for line in resp.split("\n") if line.strip()]
        pipe_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]
        # Needs at least 3 lines (Header, Divider, and Content)
        if len(pipe_lines) >= 3 and any("-" in col for col in pipe_lines[1].split("|")):
            return True, "Markdown table found."
        return False, "Markdown table syntax validation failed."

    elif constraint.startswith("bullet_count_"):
        try:
            target = int(constraint.split("_")[-1])
        except ValueError:
            return False, f"Invalid constraint config: {constraint}"
        bullets = re.findall(r'^\s*[-*•]\s+', resp, re.MULTILINE)
        if len(bullets) == target:
            return True, f"Exactly {target} bullet points."
        return False, f"Expected {target} bullets, found {len(bullets)}."

    elif constraint.startswith("list_count_"):
        try:
            target = int(constraint.split("_")[-1])
        except ValueError:
            return False, f"Invalid constraint config: {constraint}"
        # Matches numbers followed by period/parenthesis
        list_items = re.findall(r'^\s*\d+[\b.)]\s+', resp, re.MULTILINE)
        if len(list_items) == target:
            return True, f"Exactly {target} list items."
        return False, f"Expected {target} list items, found {len(list_items)}."

    elif constraint.startswith("sentence_count_"):
        try:
            target = int(constraint.split("_")[-1])
        except ValueError:
            return False, f"Invalid constraint config: {constraint}"
        sentences = count_sentences(resp)
        if sentences == target:
            return True, f"Exactly {target} sentences."
        return False, f"Expected {target} sentences, got {sentences}."

    return True, "No constraint validations failed."


def evaluate_results(tests_file: Path, results_file: Path) -> dict:
    """Evaluate predictions against benchmark criteria."""
    # Load gold standards
    gold = {}
    with open(tests_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                ex = json.loads(line)
                gold[ex["id"]] = ex

    # Load results
    results = []
    with open(results_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    report = {
        "categories": {},
        "total_passed": 0,
        "total_failed": 0,
        "failures": [],
    }

    for res in results:
        ex_id = res.get("id")
        if ex_id not in gold:
            continue
        
        test = gold[ex_id]
        category = test["category"]
        response = res.get("response", "")

        if category not in report["categories"]:
            report["categories"][category] = {"total": 0, "passed": 0, "failed": 0}
        
        report["categories"][category]["total"] += 1
        
        errors = []

        # 1. Max sentences constraint
        if "max_sentences" in test:
            max_s = test["max_sentences"]
            sentences = count_sentences(response)
            if sentences > max_s:
                errors.append(f"Sentence limit exceeded: got {sentences} sentences, max allowed {max_s}.")

        # 2. General constraints
        if "constraint" in test:
            passed, msg = check_constraint(test["constraint"], response)
            if not passed:
                errors.append(msg)

        # 3. Cultural Bleed checks (for utility prompts)
        if category in ["No Cultural Framing", "No Cultural Framing / Boring Utility", "\"No Cultural Framing\" / Boring Utility"]:
            resp_lower = response.lower()
            bleed = [kw for kw in CULTURAL_BLEED_KEYWORDS if kw in resp_lower]
            if bleed:
                errors.append(f"Cultural bleed detected (utility task mentioned cultural terms): {bleed}")

        # 4. Invitation ending check
        if test.get("check_invitation") or category == "Cultural Depth":
            tail = response.strip().lower()[-150:]
            found_inv = [inv for inv in INVITATIONS if inv in tail]
            if found_inv:
                # Treated as a minor failure / warning for V2 compliance
                errors.append(f"Reflexive invitation ending detected: '{found_inv[0]}'")

        # Record pass/fail
        if not errors:
            report["categories"][category]["passed"] += 1
            report["total_passed"] += 1
        else:
            report["categories"][category]["failed"] += 1
            report["total_failed"] += 1
            report["failures"].append({
                "id": ex_id,
                "prompt": test["prompt"],
                "response": response,
                "errors": errors
            })

    return report


def main():
    parser = argparse.ArgumentParser(description="Evaluate regression test constraints.")
    parser.add_argument("--tests", type=str, default="data/eval/v2_regression_tests.jsonl",
                        help="Path to regression tests gold specification file.")
    parser.add_argument("--results", type=str, required=True,
                        help="Path to model predictions/results JSONL file.")
    args = parser.parse_args()

    tests_path = Path(args.tests)
    results_path = Path(args.results)

    if not tests_path.exists():
        print(f"❌ Gold tests file not found at: {tests_path}")
        sys.exit(1)
    if not results_path.exists():
        print(f"❌ Model results file not found at: {results_path}")
        sys.exit(1)

    print(f"⚙️  Evaluating {results_path.name} against constraints in {tests_path.name}...")
    report = evaluate_results(tests_path, results_path)

    print("\n==================================================")
    print("           REGRESSION TESTS REPORT                ")
    print("==================================================")
    print(f"Total Evaluated : {report['total_passed'] + report['total_failed']}")
    print(f"Passed          : {report['total_passed']}")
    print(f"Failed          : {report['total_failed']}")
    pass_rate = (report['total_passed'] / (report['total_passed'] + report['total_failed'])) * 100 if (report['total_passed'] + report['total_failed']) > 0 else 0
    print(f"Pass Rate       : {pass_rate:.1f}%")
    print("--------------------------------------------------")
    
    print("\nCategory Breakdown:")
    for cat, stats in report["categories"].items():
        cat_rate = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"- {cat:<35}: {stats['passed']}/{stats['total']} ({cat_rate:.1f}%)")

    if report["failures"]:
        print("\n--------------------------------------------------")
        print(f"❌ Top Failure Samples (showing first 5 of {len(report['failures'])}):")
        print("--------------------------------------------------")
        for fail in report["failures"][:5]:
            print(f"\nID: {fail['id']} | Prompt: \"{fail['prompt']}\"")
            print(f"Errors:")
            for err in fail["errors"]:
                print(f"  - {err}")
            print(f"Model Response:\n\"\"\"{fail['response']}\"\"\"")
    else:
        print("\n🎉 All regression tests passed objective constraint checks!")


if __name__ == "__main__":
    main()

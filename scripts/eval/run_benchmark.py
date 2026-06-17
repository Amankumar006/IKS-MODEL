"""Run regression benchmark and generate summary dashboard.

Usage:
  uv run python scripts/eval/run_benchmark.py --provider gemini
  uv run python scripts/eval/run_benchmark.py --provider ollama --model mistral:7b
"""

import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
SYS_PATH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS_PATH))

from src.iks_rag.config import LLMConfig
from src.iks_rag.generation.llm import LLMWrapper
from scripts.eval.evaluate_constraints import evaluate_results, count_sentences

# Load .env variables
load_dotenv(dotenv_path=SYS_PATH / ".env")


def run_inference(llm_wrapper: LLMWrapper, tests_path: Path, output_path: Path) -> None:
    """Run model inference over the regression test suite and write results JSONL."""
    print(f"📥 Loading prompts from {tests_path.name}...")
    prompts = []
    with open(tests_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                prompts.append(json.loads(line))

    # Initialize the LLM
    print("🤖 Initializing LLM wrapper...")
    llm_wrapper.initialize()

    print(f"🚀 Running inference on {len(prompts)} prompts...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for i, item in enumerate(prompts):
            prompt_text = item["prompt"]
            print(f"[{i+1}/{len(prompts)}] ID: {item['id']} | Prompt: {prompt_text[:50]}...")
            
            try:
                # Call LLM wrapper to get response
                # Note: Setting system_prompt to SYSTEM_PROMPT_V2
                response_obj = llm_wrapper.llm.complete(prompt_text)
                response = response_obj.text.strip()
            except Exception as e:
                print(f"⚠️ Error generating response for {item['id']}: {e}")
                response = f"[Inference Error: {e}]"

            # Write result line
            result = {
                "id": item["id"],
                "prompt": prompt_text,
                "response": response
            }
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


def display_dashboard(report: dict, results_path: Path) -> None:
    """Print the formatted evaluation dashboard."""
    total_evaluated = report["total_passed"] + report["total_failed"]
    constraint_accuracy = (report["total_passed"] / total_evaluated) * 100 if total_evaluated > 0 else 0.0

    # Load responses to calculate aggregate statistics
    responses = []
    with open(results_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                responses.append(json.loads(line))

    # Word count / token count approximation
    total_words = 0
    invitation_count = 0
    bleed_count = 0
    utility_count = 0

    from scripts.eval.evaluate_constraints import INVITATIONS, CULTURAL_BLEED_KEYWORDS

    for r in responses:
        resp = r.get("response", "")
        # Approximating tokens: words * 1.3
        total_words += len(resp.split())

        # Check invitation endings
        tail = resp.strip().lower()[-150:]
        if any(inv in tail for inv in INVITATIONS):
            invitation_count += 1

        # Check cultural bleed on No Cultural Framing / Boring Utility prompts
        # G=greetings, I=instruction, C=cultural depth, H=hallucination, U=utility (see prompt IDs)
        if r.get("id", "").startswith("U"):
            utility_count += 1
            if any(kw in resp.lower() for kw in CULTURAL_BLEED_KEYWORDS):
                bleed_count += 1

    avg_tokens = int((total_words * 1.3) / len(responses)) if responses else 0
    invitation_freq = (invitation_count / len(responses)) * 100 if responses else 0.0
    bleed_rate = (bleed_count / utility_count) * 100 if utility_count > 0 else 0.0

    # Output dashboard
    print("\n" + "=" * 26 + " Bharat V2 Evaluation " + "=" * 26)
    
    # Category details
    for cat, stats in report["categories"].items():
        # Clean up name for display
        display_name = cat.split("/")[-1].strip() if "/" in cat else cat
        display_name = display_name.replace("No Cultural Framing", "Utility Tasks")
        print(f"{display_name:<30} : {stats['passed']}/{stats['total']}")

    print("-" * 74)
    print(f"Overall                        : {report['total_passed']}/{total_evaluated}")
    print(f"Constraint Accuracy            : {constraint_accuracy:.1f}%")
    print(f"Average Tokens                 : {avg_tokens}")
    print(f"Invitation Frequency           : {invitation_freq:.1f}%")
    print(f"Cultural Bleed (Utility Tasks) : {bleed_rate:.1f}%")
    print("=" * 74 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run regression tests and view summary dashboard.")
    parser.add_argument("--provider", type=str, default="gemini", choices=["gemini", "ollama", "openai"],
                        help="LLM provider to use (default: gemini).")
    parser.add_argument("--model", type=str, default="models/gemini-2.5-flash",
                        help="Model name (e.g. models/gemini-2.5-flash or mistral:7b).")
    parser.add_argument("--tests", type=str, default="data/eval/v2_regression_tests.jsonl",
                        help="Path to tests specification file.")
    parser.add_argument("--results", type=str, default="data/eval/v2_regression_results.jsonl",
                        help="Path to save results.")
    parser.add_argument("--skip-inference", action="store_true",
                        help="Skip inference and evaluate existing results file directly.")
    args = parser.parse_args()

    tests_path = Path(args.tests)
    results_path = Path(args.results)

    if not tests_path.exists():
        print(f"❌ Gold tests file not found at: {tests_path}")
        sys.exit(1)

    if not args.skip_inference:
        # Build System Prompt V2 import dynamically
        from data_collection.iks_system_prompt import SYSTEM_PROMPT_V2
        
        config = LLMConfig(
            provider=args.provider,
            model=args.model,
            temperature=0.0,  # Temperature 0 for deterministic regression checks
            max_tokens=512,
            system_prompt=SYSTEM_PROMPT_V2
        )
        
        wrapper = LLMWrapper(config)
        
        try:
            run_inference(wrapper, tests_path, results_path)
        except Exception as e:
            print(f"❌ Critical error during inference: {e}")
            sys.exit(1)

    print(f"⚙️  Evaluating constraint rules...")
    report = evaluate_results(tests_path, results_path)
    display_dashboard(report, results_path)


if __name__ == "__main__":
    main()

# Evaluation Framework: The "Gold Standard" Benchmark

> [!WARNING]
> **This benchmark was never executed. The design described below is the *intended* design — not what was built.**
>
> In practice, only the **200 Gemini-generated questions from held-out documents** were created. The **100 hand-written questions and 200 adversarial questions were never written**. The benchmark was subsequently cancelled because the design had a circular validation problem: Gemini generated the questions, Gemini's knowledge shaped the framing, and using Gemini again as the judge would mean Gemini scoring answers to its own questions. This produces no independent signal.
>
> **What is used instead for V2 evaluation**:
> - The **150-prompt regression suite** (`data/eval/v2_regression_tests.jsonl`) for objective constraint testing — this is model-agnostic (no circular dependency)
> - A human spot-check of ~30 responses scored against the Bharat Signature rubric
> - Comparison of Bharat V2 vs. baseline Mistral 7B on ~50 manually written questions
>
> See [`docs/project/next-tasks.md` Task 2.3](../project/next-tasks.md) for the full cancellation rationale.

To scientifically prove that the fine-tuned Mistral 7B model has absorbed the "Bharat" persona and deep Indian Knowledge Systems, we use a rigorous 500-question benchmark. 

We do **not** use the training model (Gemini) to generate the entire benchmark, as that would only test if the model learned to sound like Gemini. Instead, we use a three-pronged approach.

## 1. The Benchmark Sources (`data/eval/`)

The 500 questions are split across three distinct sources to test generalization, safety, and cultural resonance:

1. **Held-Out Documents (200 questions)**
   - **Location**: `data/eval/held_out_documents/`
   - **Method**: 20 documents were completely quarantined from the training set. We use Gemini to generate 10 highly challenging questions per document. This proves the model can generalize to unseen texts.
2. **Hand-Written Questions (100 questions)**
   - **Location**: `data/eval/hand_written_questions.json`
   - **Method**: Written manually by human experts. These are questions only someone deeply connected to Indian culture would ask.
3. **Adversarial Questions (200 questions)**
   - **Location**: `data/eval/adversarial_questions.json`
   - **Method**: Written manually to test failure modes, bias, and sacred boundaries (e.g., "Is Indian culture superior?", "What raga for a wedding?", "Teach me the Gayatri Mantra").

## 2. Subjective Rubric: Persona Consistency (1–5 Scale)

For subjective assessment (such as the Cultural Depth category in the regression tests), human evaluators grade outputs on a 1-5 scale across five key dimensions:

| Criterion | 1 (Poor) | 5 (Excellent) |
|---|---|---|
| **Accuracy** | Factually wrong or contains obvious historical/mythological conflations. | Fully correct, respects historical consensus. |
| **Cultural Richness** | Dry, textbook definitions with zero civilizational pedagogy. | Immersive, uses relevant Sanskrit/regional concepts. |
| **Regional Specificity** | Monolithic statements ("Indians believe"). | Localizes traditions ("In the Chola granite temples of Thanjavur"). |
| **Bharat Voice** | Generic chatbot greeting or dry corporate helper. | Warm, storyteller voice maintaining the design contract. |
| **Readability** | Poor formatting, run-on structures, or conversational loops. | Structured, clear paragraphs, stops naturally without invitation loops. |

---

## 3. Regression Test Suite (150-Prompt V2 Suite)

In V2, we added a developer-focused **150-prompt regression benchmark** (`data/eval/v2_regression_tests.jsonl`) divided into 5 objective and subjective categories:
- **Greetings (20)**: Checks if greeting tasks are concise (≤2 sentences) and avoid cultural lectures.
- **Instruction Following (30)**: Validates strict rule compliance (e.g., word count constraints, yes/no replies, JSON/CSV outputs).
- **Cultural Depth (40)**: Measures the subjective "Persona Consistency" and checks for conversational invitation endings.
- **Hallucination / Calibration (30)**: Assesses calibration on debated claims (refusal and hedging).
- **"No Cultural Framing" / Boring Utility (30)**: Measures **Cultural Bleed** on coding or math tasks.

### Automated Constraint Scoring (`evaluate_constraints.py`)
To automate testing, we run checking rules for format syntax, length limits, and cultural bleed detection:
```bash
uv run python scripts/eval/run_benchmark.py --provider gemini
```

---

## 4. Systems Comparison Framework

For final project reporting, evaluate and compare these four configurations:

| Model / System | Purpose & Role | Key Metrics Scored |
|---|---|---|
| **Base Mistral** | Baseline off-the-shelf performance. | Baseline constraint accuracy & knowledge. |
| **Bharat V1** | Personality baseline (LoRA fine-tune). | Explores persona expression vs. instruction decay. |
| **Gemini + RAG** | Knowledge baseline (Retrieval grounded). | Represents raw retrieval-driven factual accuracy. |
| **Bharat V2** | Final System (Hybrid + Calibration SFT). | Evaluates the synthesis of instruction-following + voice. |

---

## 5. Early Checkpoint Stopping
When executing SFT on cloud GPUs, save checkpoints every 100 steps and evaluate them immediately using:
```bash
uv run python scripts/eval/run_benchmark.py --skip-inference --results checkpoint_results.jsonl
```
This lets you identify the optimal SFT epoch where instruction compliance and persona expression are balanced, preventing overfitting.

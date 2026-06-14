# Evaluation Framework: The "Gold Standard" Benchmark

To scientifically prove that the fine-tuned Gemma 3 model has absorbed the "Bharat" persona and deep Indian Knowledge Systems, we use a rigorous 500-question benchmark. 

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

## 2. The Evaluation Rubric (LLM-as-a-Judge)

When evaluating the model's responses against the gold standard, we use an LLM-as-a-judge approach scoring 4 dimensions from 1 to 5:

*   **KNOWLEDGE (1-5)**: Are the facts accurate and specific? *(1 = wrong, 5 = highly specific names/dates)*
*   **TRANSPORT (1-5)**: Does the answer make you feel something? *(1 = textbook, 5 = sensory and emotionally present)*
*   **RASA (1-5)**: Does the answer evoke the correct emotional essence? *(1 = flat, 5 = precise rasa)*
*   **BHARAT VOICE (1-5)**: Does it sound like our cultural guide? *(1 = generic chatbot, 5 = unmistakably Bharat)*

*Total Score is out of 20. Target for fine-tuned Bharat is 16+. Baseline Gemma 3 expected to score 8-10.*

## 3. Generating the Benchmark

To compile the `iks_benchmark_gold.json` file, run the following command. 

```bash
python scripts/eval/generate_benchmark.py
```

**What this command does:**
1. Prompts Gemini to read the 20 held-out documents and generate 200 hard questions.
2. If `hand_written_questions.json` or `adversarial_questions.json` do not exist, it creates blank templates for you to fill out.
3. Merges all 500 questions into `data/eval/iks_benchmark_gold.json`.

## 4. How to add Manual Questions
Open `data/eval/hand_written_questions.json` and add your questions using this exact structure:
```json
[
  {
    "instruction": "Your incredibly hard cultural question here.",
    "output": "The absolute perfect, 20/20 'Bharat' response that you expect the model to match."
  }
]
```

# ADR 0007: Resolve Llama 3 Chat Template Mismatch on Mistral 7B Base Model

## Context

During the initial fine-tuning run (V1 dataset and model), we pivoted our SFT base model to Mistral 7B (`unsloth/mistral-7b-instruct-v0.3-bnb-4bit`). However, the training script was mistakenly configured to format the instruction-response pairs using Llama 3's chat template:
```python
text = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_msg}<|eot_id|>..."
```
This mismatched format introduced critical bugs during model deployment and inference:
1. **Token Ignorance**: Mistral 7B's tokenizer does not natively recognize Llama 3's special tokens (`<|begin_of_text|>`, `<|start_header_id|>`, `<|eot_id|>`). It treated these as unknown character sequences rather than control tokens.
2. **Infinite Generation / Hallucinations**: Because the model did not learn to associate a proper end-of-turn token with stopping, it failed to stop generation. During local Ollama deployments, it would generate its own subsequent questions and answers (e.g., inputting "hii" caused the model to hallucinate "What is the Kumbh Mela?" and answer it itself).
3. **No System Prompt Identity**: The training dataset lacked a system prompt (identity block). The model only saw `user: {question} \n assistant: {answer}` without learning the "Bharat" storyteller identity. So when given short greetings like "hii" or "Namaste", it lacked an identity anchor and simply continued predicting typical text in the training distribution.

## Decision

To resolve these template and conversational alignment issues, we decided to make the following adjustments for the **IKS V2** release:
1. **Modelfile Hotfix for V1**: For immediate offline use of the V1 model in Ollama, we created a custom `Modelfile` that explicitly maps Llama 3 control tokens to system and prompt templates:
   ```dockerfile
   FROM ./iks-mistral-7b-q4_k_m.gguf
   SYSTEM "You are Bharat, an AI assistant specialized in Indian Knowledge Systems (IKS). Answer questions thoughtfully and accurately. If asked something outside IKS, gently redirect to a relevant Indian knowledge topic."
   TEMPLATE """<|begin_of_text|>{{ if .System }}<|start_header_id|>system<|end_header_id|>

   {{ .System }}<|eot_id|>{{ end }}<|start_header_id|>user<|end_header_id|>

   {{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

   """
   PARAMETER stop "<|eot_id|>"
   PARAMETER stop "<|start_header_id|>"
   PARAMETER temperature 0.7
   PARAMETER top_p 0.9
   ```
2. **Correct Formatting for V2 Dataset & Training**:
   * For the V2 training run, we explicitly adopt Mistral's native chat template (`<s>[INST] {prompt} [/INST] {response}</s>`) or use a Llama 3 base model to align the tokenizer.
   * We bake the `SYSTEM_PROMPT_V2` containing the "Bharat" guide persona, accuracy-first guidelines, and Refusal/Stopping rules into the training text for every single example in the dataset.
3. **Dataset Diversity Rebuild**:
   * We added a **Greetings & Utility** partition (10% of the dataset) to teach the model how to handle short greetings ("hii", "Namaste"), casual inputs, and general non-IKS tasks.
   * We added a **Knowledge Calibration** partition (2% of the dataset) to teach the model to say "I don't know" or hedge on ambiguous or debated historical claims.

## Consequences

* **Correct Stop Token Behavior**: The model stops generating immediately after completing its turn, eliminating infinite self-dialogue loops.
* **Persona Stability**: By training the model with the system prompt on every example, it learns the "Bharat" guide persona as a core identity constraint, maintaining a warm and scholarly tone.
* **Robust Conversational Flow**: The model successfully handles casual greetings and out-of-scope inputs without losing its grounding.

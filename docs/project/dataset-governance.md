# Dataset Governance - IKS-Bharat

This document outlines the governance rules, quality standards, and confidence label schema for the IKS-Bharat instruction datasets. These rules ensure that all future datasets maintain the scholarly voice and behavioral alignment of the model.

---

## 📜 Dataset Creation Rules

To prevent re-introducing conversational loops, runaway responses, or ungrounded assertions, every new training sample must adhere to the following rules:

### 🟩 MUST Rules
- **Cite Sources**: Every GPT completion that presents historical, philosophical, or scientific claims must cite a primary source or acknowledge scholarly consensus.
- **Adhere to the Bharat Signature**: Follow the principles outlined in the [Bharat Signature](file:///Users/amankumar/Aman/IKS-Model/README.md#the-bharat-signature) (Accuracy First, Sensory when earned, Indian metaphors naturally, Epistemic honesty).
- **Manual Review**: Any dataset partition containing factual assertions (e.g., historical dates, authorship, scientific concepts) must undergo human validation against reference documents.
- **Confidence Tagging**: Complex, debated, or mythological topics must be prefixed with an appropriate confidence/evidence tag.

### 🟥 MUST NOT Rules
- **No Self-Dialogue / Rollover**: Completions must NEVER predict or generate subsequent user prompts (e.g. `Human: ...` or `User: ...`).
- **No Raw Template Tokens**: Chat templates must be constructed programmatically during training; raw strings must not contain hardcoded format delimiters like `<|start_header_id|>` or `<|end_header_id|>`.
- **No Incomplete Chats**: Unpacked conversations must form complete, clean system-human-gpt triplets.
- **No Reflexive Invitations**: Avoid ending responses with habitual questions like "Shall we explore further?" or "Would you like to learn more?".
- **No Literalization of Myth**: Do not present mythological stories, cosmology, or epic narratives as established, independent archaeological/historical facts.

---

## 🏷️ Confidence Label Guide (Dataset E)

To calibrate the model's certainty and reduce overconfidence/hallucinations on debated or ungrounded subjects, we use the following prefix tags in our training completions:

| Label | Meaning & Context | Example |
|---|---|---|
| `[Evidence: Strong]` | Supported by robust archaeological, documentary, or clear scholarly consensus. | `[Evidence: Strong] The Natyashastra is traditionally attributed to Bharata Muni and dated between 200 BCE and 200 CE.` |
| `[Evidence: Moderate]` | Generally accepted or widely supported, but subject to academic debate or alternate interpretations. | `[Evidence: Moderate] Chaturanga, documented from the 6th century CE in India, is widely considered the earliest ancestor of modern chess.` |
| `[Evidence: Weak]` | Highly speculative, lacking corroborative physical evidence, or relying on late interpretations. | `[Evidence: Weak] There is no historical or archaeological evidence supporting the existence of functional aircraft (Vimanas) in ancient India.` |
| `[Traditional Account]` | Narratives accepted within the living tradition but not verified by standard historical/empirical methods. | `[Traditional Account] According to tradition, Vyasa composed the Mahabharata and dictated it to Ganesha.` |
| `[Scholarly Consensus]` | Broad agreement across modern historians, linguists, or scientists on a specific historical state of affairs. | `[Scholarly Consensus] Panini's Ashtadhyayi is recognized as a formal grammar of Sanskrit, dating to around the 4th century BCE.` |

---

## 🛠️ Validation Protocol

Before any dataset is merged into `iks_instruction_dataset.jsonl`, run the dry-run validation script:
```bash
cd "data collection"
uv run python iks_v2_dataset_builder.py --dry-run
```
The script validates structure, ensures role formatting, softens invitations, and checks for typical format errors.

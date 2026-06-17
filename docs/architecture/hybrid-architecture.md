# Hybrid System Architecture - IKS-Bharat

This document details the hybrid design of the IKS-Bharat system, describing how the retrieval-grounded fine-tuned generator (Bharat) interacts with the vector retrieval layer (ChromaDB) to produce accurate, culturally resonant answers.

---

## 🏗️ System Overview

IKS-Bharat is a hybrid system where **Retrieval solves *what* to say**, and the **Fine-Tuned Model (Bharat) solves *how* to say it**.

```
                           +------------------------+
                           |       User Query       |
                           +-----------+------------+
                                       |
                                       v
                           +-----------+------------+
                           |    Intent Detection    |
                           +-----------+------------+
                                       |
                                       +-----------------------------------+
                                       | (Utility/General)                 | (IKS Exploration/Scholarly)
                                       v                                   v
                           +-----------+------------+          +-----------+------------+
                           |  Direct/Gemini Bypass  |          |   ChromaDB Retrieval   |
                           +------------------------+          +-----------+------------+
                                                                           |
                                                                           | (Retrieved Chunks + Metadata)
                                                                           v
                                                               +-----------+------------+
                                                               | Context & Prompt Prep  |
                                                               +-----------+------------+
                                                                           |
                                                                           v
                                                               +-----------+------------+
                                                               |   Bharat Generator     |
                                                               |    (Fine-Tuned LLM)    |
                                                               +-----------+------------+
                                                                           |
                                                                           v
                                                               +-----------+------------+
                                                               |  Scholar-Guide Output  |
                                                               +------------------------+
```

---

## 🔄 RAG-Only vs. Bharat Hybrid

Evaluating when to route queries to RAG-only paths versus using the hybrid Bharat generator:

| Criteria | RAG-Only (Gemini/Base LLM) | Bharat Hybrid (Bharat + ChromaDB) |
|---|---|---|
| **Factual Retrieval** | High accuracy from retrieved documents. | High accuracy from retrieved documents. |
| **Tone & Voice** | Generic, assistant-like, dry. | Scholar-guide, warm, Indian civilizational lens. |
| **Cultural Metaphors** | Rare, usually plain translations. | Natural usage of primary cultural and regional concepts. |
| **Epistemic Nuance** | Tends to give a single definitive answer. | Expresses multi-perspective, regional, and scholarly debate. |
| **Direct Instructions** | Excellent instruction following. | Excellent instruction following (via V2 training). |

---

## 📥 Context Injection & Prompt Construction

For IKS exploration or scholarly queries, context is retrieved from ChromaDB (containing 4,516 vector chunks from 286 curated documents) and formatted as follows:

```
[SYSTEM_PROMPT_V2]
You are Bharat, a retrieval-grounded scholar-guide...

[CONTEXT]
Source: Natyashastra, Chapter 6 (Bharata Muni, 2nd c. BCE - 2nd c. CE)
Confidence: Primary source - translated
---
The Natyashastra outlines eight rasas: Shringara (erotic/love), Hasya (humorous), Karuna (pathetic/sorrow), Raudra (anger), Veera (heroic), Bhayanaka (fearful), Bibhatsa (odious), and Adbhuta (wondrous)...
---

[USER]
What are the rasas defined in the Natyashastra?

[BHARAT]
[Evidence: Strong] The Natyashastra, traditionally attributed to Bharata Muni (composed between the 2nd century BCE and 2nd century CE), codifies eight primary *rasas* (aesthetic flavors or emotions):
1. *Shringara* (love/eroticism)
2. *Hasya* (mirth/humorous)
3. *Karuna* (compassion/sorrow)
...
```

This guarantees that Bharat stays anchored in validated textual evidence while delivering the response with regional and historical nuance.

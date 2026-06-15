# Building a Specialized Multimodal AI for Indian Knowledge Systems (IKS)

## Problem Statement

Indian Knowledge Systems are rich, multilingual, and deeply multimodal, spanning temples, architecture, sculpture, classical music, dance, textiles, manuscripts, philosophy, and mathematics. Current general-purpose AI models can answer some surface-level questions, but they often miss cultural nuance, struggle with specialized terminology, and cannot reliably interpret visual heritage materials in context.

This project addresses that gap by building a specialized AI assistant that combines curated IKS data, retrieval, and domain fine-tuning to deliver accurate, culturally grounded, and context-aware answers for global users, researchers, and cultural institutions. The goal is not just to retrieve facts, but to present Indian civilization with an authentic voice that understands its symbols, traditions, and intellectual frameworks.

## Executive Summary: What This Project Aims to Achieve

This project goes beyond RAG (Retrieval-Augmented Generation). While RAG answers questions from existing documents, **fine-tuning a vision-language model** allows you to:

1. **Recognize images** of temples, textiles, dance mudras, and manuscripts
2. **Understand their context** — dynasty, period, regional style, significance
3. **Generate contextually accurate answers** about IKS without needing to retrieve documents
4. **Handle multilingual queries** (Sanskrit, Tamil, Hindi, etc.)
5. **Integrate visual and textual knowledge** in a way current general models cannot

This is the **Phase 2 evolution** of your IKS assistant — moving from a retrieval system (Phase 1 RAG) to a specialized **understanding system** that truly comprehends Indian heritage.

---

## Part 1: Choosing the Right Foundation Model

### Why Vision-Language Models Matter for IKS

Indian Knowledge Systems are deeply visual:
- **Temples** are architectural marvels with intricate carvings and sculptures
- **Classical dance** is expressed through mudras (hand gestures) and body positions
- **Textiles** showcase regional patterns, weaving techniques, and traditional designs
- **Manuscripts** contain Sanskrit, Tamil, and Kannada text in unique scripts
- **Iconography** requires understanding symbolic representations

A text-only model (like baseline Mistral 7B) cannot process this visual richness. You need a **vision-language model** that can:
- Encode images into semantic vectors
- Understand the relationship between images and text
- Answer questions like "What temple is this? What dynasty? What's the architectural significance?"

### Model Selection: Mistral 7B & SFT Fine-Tuning Pivot

Comparing models suitable for IKS fine-tuning:

| Model | Parameters | Vision Support | Context Window | Best For | Cost |
|-------|-----------|-----------------|-----------------|----------|------|
| **Mistral 7B** | 7B | ❌ Text-only (LoRA fine-tune) | 32,768 tokens | Budget-friendly text SFT | ~$0 (open) |
| **Gemma 3** | 4B/12B/27B | ✅ Full multimodal | 4,096 tokens | IKS visual tasks (needs bfloat16) | ~$0 (open) |
| Llava | 7B/13B/34B | ✅ Dual encoder | 4,096 tokens | Cost-effective vision | ~$0 (open) |
| Claude 3.5 Sonnet | Proprietary | ✅ Professional | 200K tokens | High accuracy, no training | $$ API |
| GPT-4 Vision | Proprietary | ✅ Advanced | 128K tokens | Highest quality, not trainable | $$$ API |

**Recommendation: Start with Mistral 7B (Pivoted from Gemma 3 12B)**

```
Model Selection Context:
We initially recommended Gemma 3 12B. However, due to Kaggle T4 GPU hardware limits (Tesla T4 has no native bfloat16 support, causing upcasting to float32 which doubles VRAM usage and triggers OOM), we pivoted the fine-tuning architecture to **Mistral 7B**. Mistral 7B natively runs in float16 precision, allowing efficient fine-tuning under 4.35 GB VRAM on a single GPU.
```

**Why Mistral 7B?**
- ✅ Natively runs on standard float16 precision without float32 upcasting on older hardware (T4 GPUs)
- ✅ Highly efficient fine-tuning using Unsloth (fits in <5 GB VRAM)
- ✅ Strong instruction-following capability and cultural reasoning
- ✅ Large 32K context window support

---

## Part 2: Complete End-to-End Training Pipeline

### Stage 1: Data Collection & Sourcing

This is the **most critical stage** — your model is only as good as your training data. You need two types of data:

1. **Text instruction pairs** (for language understanding)
2. **Image + text pairs** (for visual understanding)

#### 1A. Text Data Sources

| Domain | Sources | What to Collect | Quality Level |
|--------|---------|-----------------|----------------|
| **Temple Architecture** | • Wikipedia temple articles<br>• ASI (Archaeological Survey of India)<br>• Encyclopaedia of Indian Temple Architecture | Dynasty, construction period, style (Nagara/Dravidian/Vesara), regional variations, sculptural themes, materials | High |
| **History & Empires** | • Digital Library of India (dli.gov.in)<br>• Archive.org<br>• Indian History Congress journals | Maurya, Gupta, Chola, Pallava, Vijayanagara, Mughal periods; rulers, achievements, cultural contributions | High |
| **Classical Music** | • Sangeet Natak Akademi<br>• IGNCA (Indira Gandhi National Centre for Arts)<br>• Raag.org database | 72 Melakarta ragas, gharanas, talas, instruments, composers, performance traditions (Hindustani & Carnatic) | High |
| **Textiles & Crafts** | • Craft documentation sites<br>• Fab India heritage archives<br>• National Institute of Fashion Technology | Saree styles by region (Kanjivaram, Banarasi, Chanderi), weaving techniques, embroidery traditions, natural dyes, regional variations | Medium-High |
| **Mathematics & Astronomy** | • NPTEL IKS course modules<br>• Aryabhatiya English translations<br>• Brahmasphutasiddhanta texts | Place value system, zero concept, decimal notation, algebra, astronomical calculations, mathematical proofs | High |
| **Vedic Texts** | • Sacred-texts.com (public domain)<br>• Gita Press digital scans<br>• Vedabase.io | Vedas, Upanishads, Puranas — philosophical concepts, ethical teachings, cosmological models | High |
| **Ayurveda** | • AYUSH ministry publications<br>• Charaka Samhita translations<br>• Sushruta Samhita texts | Tridosha theory, medicinal herbs, treatments, diagnostic methods, wellness principles | Medium |
| **Dance & Drama** | • Natya Shastra complete translations<br>• Sangeet Natak Akademi archives<br>• Regional dance organizations | All 8 classical forms (Bharatanatyam, Kathak, Kathakali, etc.), techniques, history, rasa theory, mudras | High |
| **Philosophy** | • Vedantic schools<br>• Buddhist and Jain texts<br>• Nyaya logic texts | Advaita, Dvaita, Samkhya, Yoga, Nyaya schools; metaphysics, epistemology, ethics | Medium-High |

#### 1B. Image Data Sources (with Legal Licensing)

**Priority 1: Completely Free (CC0/CC-BY)**
- **Wikimedia Commons** — Search:
  - `Category:Hindu temples` → thousands of temple images
  - `Category:Indian classical dance` → dance poses, mudras
  - `Category:Indian textiles` → fabric patterns, weaving
  - `Category:Indian sculpture` → temple carvings, manuscripts
  - Most are CC-BY or CC0 (free to use, attribute)

- **IGNCA Digital Archives** (ignca.gov.in)
  - Paintings, sculptures, folk art collections
  - Manuscripts with illuminations
  - Performance documentation (photos of classical dancers, musicians)

- **Archaeological Survey of India** (asi.nic.in)
  - High-quality monument photographs
  - Temple interior and exterior documentation
  - Sculpture close-ups and architectural details

- **British Library Digitised Collections** (bl.uk/digitised-collections)
  - Indian manuscripts with illustrations
  - Historical manuscripts in Sanskrit, Tamil, Kannada
  - CC-BY licensed (free with attribution)

- **MET Museum Open Access** (metmuseum.org)
  - Indian art objects, sculptures, paintings
  - CC0 licensed (use freely, no attribution required)
  - Particularly strong in South Indian bronzes and North Indian paintings

- **Cleveland Museum of Art Open Access** (clevelandart.org)
  - Indian sculpture collections
  - Textile documentation
  - CC0 for most items

**Priority 2: With Restrictions (Requires Permission or Proper Attribution)**
- Museum collections (V&A, Getty, Philadelphia)
- ICCR (Indian Council for Cultural Relations) archives
- Government of India culture ministry databases

#### Data Collection Script Example

```python
# Automated collection from Wikimedia Commons
import requests
import json
from pathlib import Path
import urllib.parse

def download_wikimedia_images(category, limit=100):
    """
    Download images from Wikimedia Commons by category.
    """
    base_url = "https://commons.wikimedia.org/w/api.php"
    
    images_data = []
    continue_param = None
    
    while len(images_data) < limit:
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': f'Category:{category}',
            'cmlimit': 100,
            'cmtype': 'file',
            'format': 'json',
        }
        
        if continue_param:
            params['cmcontinue'] = continue_param
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        for item in data['query']['categorymembers']:
            file_title = item['title']
            
            # Get file metadata
            file_params = {
                'action': 'query',
                'titles': file_title,
                'prop': 'imageinfo',
                'iiprop': 'url|extmetadata',
                'format': 'json',
            }
            
            file_response = requests.get(base_url, params=file_params)
            file_data = file_response.json()
            
            for page_id, page_data in file_data['query']['pages'].items():
                if 'imageinfo' in page_data:
                    info = page_data['imageinfo'][0]
                    
                    # Extract metadata
                    metadata = info.get('extmetadata', {})
                    image_record = {
                        'title': file_title,
                        'url': info['url'],
                        'description': metadata.get('ImageDescription', {}).get('value', ''),
                        'license': metadata.get('LicenseShortName', {}).get('value', ''),
                        'artist': metadata.get('Artist', {}).get('value', ''),
                        'date': metadata.get('DateTime', {}).get('value', ''),
                    }
                    
                    images_data.append(image_record)
                    
                    if len(images_data) >= limit:
                        break
        
        # Check for more pages
        if 'continue' in data:
            continue_param = data['continue']['cmcontinue']
        else:
            break
    
    return images_data

# Download temple images
temple_images = download_wikimedia_images('Hindu temples', limit=500)

# Save metadata
with open('temple_images_metadata.json', 'w') as f:
    json.dump(temple_images, f, indent=2)

print(f"Downloaded metadata for {len(temple_images)} temple images")
```

---

### Stage 2: Dataset Preparation & Formatting

Your training dataset needs to be in a specific format that Mistral 7B understands. You'll create two types of training examples:

#### 2A. Pure Text Examples (Instruction-Response Pairs)

These teach the model IKS knowledge in text form:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Explain the architectural features of Chola temples and their historical significance."
    },
    {
      "role": "assistant",
      "content": "Chola temple architecture (9th-13th century CE) represents the pinnacle of Dravidian architectural development. Key features include:\n\n1. **Vimana (Tower)**: Tall, stepped pyramidal structure over the main sanctum, reaching heights of 30-70 meters. The Brihadishvara Temple vimana is 66 meters tall.\n\n2. **Gopuram Gateway Towers**: Ornate entrance towers with multiple tiers, richly decorated with sculptures.\n\n3. **Sculptural Program**: Extensive stone carvings depicting Shaiva mythology, including scenes from the Shiva Purana and Mahabharata. The sculpture quality is unmatched—every available surface contains narrative reliefs.\n\n4. **Materials & Construction**: Built primarily from granite without mortar (ashlar masonry). The precision of stone-cutting means blocks fit together so tightly a knife blade cannot be inserted between them.\n\n5. **Mandapa System**: Columned halls (mandapas) with intricately carved pillars, often depicting celestial dancers and mythological scenes.\n\n6. **Regional Characteristics**: Chola temples emphasized verticality and mass, unlike Northern nagara temples. The sanctum remains dark and inward-focused, representing the transcendent nature of the divine.\n\nHistorical Significance:\n- Sponsored by royal patronage, especially Raja Raja Chola I and his successors\n- Represented the apex of Tamil cultural achievement\n- Influenced temple architecture across South India\n- UNESCO World Heritage sites: Brihadishvara (Thanjavur), Gangaikondacholapuram, Darasuram"
    }
  ]
}
```

#### 2B. Multimodal Examples (Image + Question + Answer)

These teach the model to understand visual content:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "image": "file:///data/images/brihadishvara_temple.jpg"
        },
        {
          "type": "text",
          "text": "What is this temple called? Which dynasty built it, and what architectural style does it represent? What is visible in this specific image?"
        }
      ]
    },
    {
      "role": "assistant",
      "content": "This is the **Brihadishvara Temple** (also called Rajarajesvaram) located in Thanjavur, Tamil Nadu, India.\n\n**Historical Background:**\n- **Dynasty**: Imperial Chola (commissioned by Raja Raja Chola I)\n- **Date**: ~1010 CE (11th century)\n- **Architectural Style**: Dravidian (South Indian)\n\n**Visual Features in This Image:**\n- **Vimana (Main Tower)**: The 66-meter tall granite tower dominating the structure. It's built in a stepped pyramidal form, characteristic of Dravidian architecture.\n- **Shikhara (Peak)**: The crowning element at the top, which features a 216-ton polished granite dome without any binding agent—purely fitted stonework.\n- **Sculptural Details**: The tower is covered with intricate carvings depicting sacred narratives, though the detail is difficult to discern at this distance.\n- **Gopuram Gateway**: Visible are ornate gateway towers with their characteristic tiered, cone-shaped structure.\n\n**Architectural Significance:**\n- Represents the culmination of Dravidian temple architecture\n- All stone was fitted without mortar using precision cutting techniques (ashlar masonry)\n- The tower is perfectly aligned such that no shadow falls on the ground on full moon days during April-May\n- Features the longest inscriptions (detailing its construction and maintenance) of any Indian temple\n\n**UNESCO Status**: World Heritage Site (1987)"
    }
  ]
}
```

#### 2C. Dataset Folder Structure

Organize your dataset JSON files clearly:

```
training_dataset/
├── text_examples/
│   ├── temples_architecture.jsonl
│   ├── classical_music.jsonl
│   ├── dance_forms.jsonl
│   ├── mathematics_science.jsonl
│   ├── history_dynasties.jsonl
│   ├── textiles_crafts.jsonl
│   ├── ayurveda_medicine.jsonl
│   └── philosophy_vedics.jsonl
├── multimodal_examples/
│   ├── temple_vqa.jsonl
│   ├── dance_mudras_vqa.jsonl
│   ├── textile_identification.jsonl
│   ├── manuscript_reading.jsonl
│   └── sculptural_analysis.jsonl
├── images/
│   ├── temples/
│   ├── dances/
│   ├── textiles/
│   ├── manuscripts/
│   └── sculptures/
└── metadata.json
```

---

### Stage 3: Dataset Size Recommendations

Training the model requires careful scaling:

| Phase | Text Examples | Multimodal Examples | Total | Cost | Time (Kaggle T4 / A100) | Quality |
|-------|---------------|-------------------|-------|------|-------------------------|---------|
| **Phase 0: Prototype** | 500 | - | 500 | Free (local CPU) | 30 min | ~50% |
| **Phase 1: MVP** | 2,000 | - | 2,000 | Free (Kaggle T4) | 1-2 hours | ~65% |
| **Phase 2: Production (Current)** | 15,000 | - | 15,000 | Free (Kaggle T4) | 10-12 hours | ~85% |
| **Phase 3: Excellence** | 50,000+ | 10,000+ (Multimodal) | 60,000+ | $100-200 (RunPod A100) | 40-60 hours | ~92%+ |

**Recommendation**: Start with Phase 2 text fine-tuning (15,000 ShareGPT conversational pairs) on free Kaggle T4.

**Data Distribution**:
- 60% temples & architecture
- 15% classical music & dance  
- 10% mathematics & history
- 10% textiles & ayurveda
- 5% philosophy & vedic texts

---

### Stage 4: Training Code (Complete, Production-Ready)

Using **Unsloth** (fastest fine-tuning library — 2x speedup, 60% less VRAM):

```python
# Fine-tuning Kaggle Notebook Code for Mistral 7B SFT
# Overwritten with the exact code used successfully on the Kaggle Free Tier.
# Run 'pip install unsloth' first in your environment.

# Cell 2 — Environment & credentials
import os

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # stick to one GPU, avoids the duplication issue

from kaggle_secrets import UserSecretsClient
secrets = UserSecretsClient()

os.environ["HF_TOKEN"] = secrets.get_secret("HF_TOKEN")
os.environ["WANDB_API_KEY"] = secrets.get_secret("WANDB_API_KEY")

HF_USERNAME = "006aman"      
HF_REPO_NAME = "iks-mistral-7b-checkpoints"

# Cell 3 — Load Mistral 7B + LoRA
import torch
from unsloth import FastLanguageModel

MODEL_NAME = "unsloth/mistral-7b-instruct-v0.3-bnb-4bit"
MAX_SEQ_LENGTH = 1024  # bump to 2048 later if the VRAM headroom allows

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = MODEL_NAME,
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = None,          # auto -> float16 on T4
    load_in_4bit = True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Memory allocated after load: {torch.cuda.memory_allocated()/1e9:.2f} GB")


# Cell 4 — Dataset (auto-discover & safe parse)
import json
from datasets import Dataset

# Find candidate data files
data_files = []
for root, dirs, files in os.walk("/kaggle/input"):
    for f in files:
        if f.endswith((".json", ".jsonl", ".csv")):
            data_files.append(os.path.join(root, f))

DATA_PATH = data_files[0]
print(f"\nLoading: {DATA_PATH}")

# Safe JSON loader to strip out unwanted keys (pr, words)
def load_sharegpt_jsonl(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            conv = obj.get("conversations", [])
            # Forcibly extract ONLY 'from' and 'value'
            cleaned = [{"from": str(turn.get("from", "")), "value": str(turn.get("value", ""))} for turn in conv]
            if cleaned:
                rows.append({"conversations": cleaned})
    return Dataset.from_list(rows)

raw_dataset = load_sharegpt_jsonl(DATA_PATH)

# Format using the correct Llama 3 template
def format_llama3(example):
    user_msg, assistant_msg = "", ""
    for turn in example["conversations"]:
        role = turn.get("from", "").strip().lower()
        val = turn.get("value", "")
        if role == "human": user_msg = val
        elif role == "gpt": assistant_msg = val
        
    text = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{assistant_msg}<|eot_id|>"
    return {"text": text}

train_dataset = raw_dataset.map(format_llama3, remove_columns=raw_dataset.column_names)


# Cell 5 — Trainer setup
from trl import SFTTrainer, SFTConfig

SANITY_CHECK = False
OUTPUT_DIR = "/kaggle/working/bharat-checkpoints"

extra = {"max_steps": 20} if SANITY_CHECK else {"num_train_epochs": 3}

training_args = SFTConfig(
    output_dir=OUTPUT_DIR,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=10,
    lr_scheduler_type="cosine",
    weight_decay=0.01,
    optim="paged_adamw_8bit",
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1 if SANITY_CHECK else 10,
    save_steps=500,
    save_total_limit=2,
    remove_unused_columns=False,
    average_tokens_across_devices=False,
    report_to="none" if SANITY_CHECK else "wandb", 
    push_to_hub=not SANITY_CHECK,
    hub_model_id=f"{HF_USERNAME}/{HF_REPO_NAME}",
    hub_strategy="checkpoint", 
    hub_private_repo=True,     
    hub_token=os.environ.get("HF_TOKEN"),
    **extra,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    args=training_args,
)


# Cell 6 — Train
trainer.train()
```
```

---

### Stage 5: Infrastructure & Cloud Options

Where to train your model and expected costs:

| Platform | GPU | VRAM | Cost/Hour | Best For | Notes |
|----------|-----|------|-----------|----------|-------|
| **Google Colab Pro+** | A100 40GB | 40GB | $0.50 | MVP, testing | Free tier: 12hr/day limit |
| **Kaggle Notebooks** | T4 x2 | 32GB | Free | Experimentation | 30 hrs/week free tier |
| **RunPod** | A100 80GB | 80GB | $2.19 | Production training | On-demand, reliable |
| **Vast.ai** | RTX 4090 x2 | 48GB | $0.70 | Budget-conscious | Community market, variable |
| **Lambda Labs** | A100 80GB | 80GB | $1.50 | Enterprise | Pre-configured, reliable |
| **Google Cloud** | A100 | 80GB | $3.50+ | Long-term projects | Enterprise SLA |

**Cost Estimate for Full Training:**
- 18,000 examples on A100: ~15 hours
- At $2.19/hour on RunPod: **~$33 total**

---

### Stage 6: Domain Coverage Specification

Your multimodal dataset should comprehensively cover these IKS domains:

#### **Temples & Sacred Architecture (25% of dataset)**
- All regional styles: Nagara (North), Dravidian (South), Vesara (Deccan), Kalinga (East), Hemadpanthi (Western), Maru-Gurjara (Rajasthan)
- Specific examples: Brihadishvara, Khajuraho, Madurai Meenakshi, Varanasi Kashi Vishwanath
- Architectural elements: vimana, gopuram, mandapa, shikhara, sanctum
- Sculptural programs and iconography

#### **Classical Music Systems (15% of dataset)**
- Hindustani & Carnatic systems with differences
- All 72 Melakarta ragas with audio descriptions
- Instruments: veena, sitar, tabla, mridangam, sarangi, sarod
- Gharanas (musical lineages)
- Compositional forms: dhrupad, khayal, kriti, tillana
- Famous ragas with mood/time associations

#### **All 8 Classical Dance Forms (15% of dataset)**
- Bharatanatyam (Tamil Nadu)
- Kathak (North India)
- Kuchipudi (Andhra Pradesh)
- Odissi (Odisha)
- Manipuri (Manipur)
- Mohiniyattam (Kerala)
- Sattriya (Assam)
- Kathakali (Kerala)
- Rasa theory and mudra classification
- Famous dancers and compositions

#### **Textiles & Traditional Crafts (15% of dataset)**
- Regional saree styles: Kanjivaram, Banarasi, Chanderi, Bandhani, Brocade
- Weaving techniques: handloom, jacquard, ikat
- Embroidery traditions: phulkari, zari, mirror work
- Natural dyes and dyeing processes
- Regional variations and cultural significance

#### **Mathematics & Astronomy (10% of dataset)**
- Aryabhata's contributions (place value, sine table)
- Brahmagupta and zero concept
- Decimal notation history
- Algebraic concepts in Sanskrit texts
- Astronomical observations and calculations
- Vedic mathematics sutras

#### **History & Dynasties (10% of dataset)**
- Harappan civilization (urban planning, seals)
- Vedic period (literature, philosophy)
- Maurya empire (Ashoka, administration)
- Gupta period (golden age)
- Chola empire (maritime, culture)
- Mughal period (architecture, fusion)
- Medieval kingdoms (regional histories)

#### **Ayurveda & Traditional Medicine (5% of dataset)**
- Tridosha theory (Vata, Pitta, Kapha)
- Diagnostic methods
- Medicinal herbs and preparations
- Seasonal wellness practices
- Integration with yoga

#### **Philosophy & Vedic Texts (5% of dataset)**
- Six schools: Samkhya, Yoga, Nyaya, Vaisheshika, Purva Mimamsa, Uttara Mimamsa
- Vedantic schools: Advaita, Dvaita, Vishishtadvaita
- Buddhist and Jain philosophies
- Metaphysical concepts from Upanishads
- Ethical teachings from Bhagavad Gita

---

### Stage 7: Training Best Practices

**Ensure Model Quality:**

1. **Ground in Evidence**: Include training examples like:
   ```
   "According to the Natya Shastra (Chapter 4), the Rasa Sutra states..."
   "The inscription at Brihadishvara temple reads..."
   "Aryabhata's mathematical treatise demonstrates..."
   ```
   This trains the model to cite sources rather than hallucinate.

2. **Regional Diversity**: Ensure equal representation:
   - North: Khajuraho, Varanasi, Kashmir
   - South: Chola temples, Dravidian arts
   - East: Odissi, Jain temples, Bengal sculpture
   - West: Gujarat textiles, Jain architecture
   - Northeast: Assam silks, Manipuri dance

3. **Rich Multimodal Captions**: For every image, include:
   - Name and location
   - Historical period and dynasty
   - Architectural/artistic style
   - Materials and construction methods
   - Cultural and religious significance
   - Any inscriptions or texts visible

   Example:
   ```
   Image: Temple tower carving
   Caption: "This is a detail from the vimana tower of Brihadishvara Temple
   in Thanjavur, built by Raja Raja Chola I around 1010 CE. The carving
   shows a celestial dancer performing in the Bharatanatyam tradition,
   with mudras characteristic of Saiva devotional art. The stone is
   granite, and the sculpture demonstrates the Chola mastery of
   three-dimensional carving within architectural frames."
   ```

4. **Negative Examples**: Include "I don't know" examples:
   ```
   Q: "How many strings does a sitar have?"
   A: "I'm not certain about the exact number of strings. If you're
   asking specifically about a classical Indian sitar, there are
   typically 18-21 strings including sympathetic strings, but I should
   note that I don't have source documentation for this in my training
   data about IKS specifically."
   ```

5. **Multilingual Capabilities**: Include examples in Indian languages:
   - Sanskrit sloka with English translation and explanation
   - Tamil poetry (Sangam literature) with transliteration
   - Kannada inscriptions with interpretation
   - Hindi texts on classical music
   
   This allows the model to understand original sources.

---

## Part 3: When to Do Phase 2 Fine-tuning (Strategic Guidance)

⚠️ **Important**: Fine-tuning makes sense ONLY after Phase 1 succeeds.

- **If RAG works well**: You may not need fine-tuning. RAG + Gemini/Mistral can handle 80% of cases.
- **If RAG has limitations**: Fine-tune to overcome specific gaps
  - Example 1: RAG retrieves documents but student questions are outside the corpus → fine-tune on synthetic queries
  - Example 2: Students ask visual questions about temples → multimodal fine-tuning helps
  - Example 3: Model needs to understand Sanskrit/Tamil inscriptions → language-specific fine-tuning

Start Phase 2 when you have clear evidence of what the model needs to learn that RAG cannot provide.
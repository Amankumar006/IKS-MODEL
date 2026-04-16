# Building a Specialized Multimodal AI for Indian Knowledge Systems (IKS)

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

A text-only model (like Gemma 2) cannot process this visual richness. You need a **vision-language model** that can:
- Encode images into semantic vectors
- Understand the relationship between images and text
- Answer questions like "What temple is this? What dynasty? What's the architectural significance?"

### Model Selection: Gemma 3 vs. Alternatives

Comparing vision-language models suitable for IKS fine-tuning:

| Model | Parameters | Vision Support | Context Window | Best For | Cost |
|-------|-----------|-----------------|-----------------|----------|------|
| **Gemma 3** | 4B/12B/27B | ✅ Full multimodal | 4,096 tokens | IKS visual tasks | ~$0 (open) |
| Llava | 7B/13B/34B | ✅ Dual encoder | 4,096 tokens | Cost-effective vision | ~$0 (open) |
| LLaVA-NeXT | 8B/34B | ✅ Improved | 8K tokens | Better visual understanding | ~$0 (open) |
| Claude 3.5 Sonnet | Proprietary | ✅ Professional | 200K tokens | High accuracy, no training | $$ API |
| GPT-4 Vision | Proprietary | ✅ Advanced | 128K tokens | Highest quality, not trainable | $$$ API |

**Recommendation: Start with Gemma 3 12B**

```
Model Size Comparison:
- 4B variant: Fast, mobile-friendly, less nuanced (good for prototyping)
- 12B variant: Sweet spot — good quality, fits on RTX 4090, trains in <24 hours ✓
- 27B variant: Highest quality, needs A100 GPU ($50+/hour), overkill for initial phase
```

**Why Gemma 3 over others?**
- ✅ Built for multimodal understanding by Google
- ✅ Optimized for fine-tuning with QLoRA (60% less VRAM needed)
- ✅ Chat instruction-tuned (understands follow-ups, can be steered)
- ✅ Active community, good documentation
- ✅ Can be fine-tuned locally or on affordable cloud GPUs

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

Your training dataset needs to be in a specific format that Gemma 3 understands. You'll create two types of training examples:

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

Training a vision-language model requires careful scaling:

| Phase | Text Examples | Multimodal Examples | Total | Cost | Time (A100) | Quality |
|-------|---------------|-------------------|-------|------|-------------|---------|
| **Phase 0: Prototype** | 500 | 100 | 600 | Free (local CPU) | 30 min | ~50% |
| **Phase 1: MVP** | 2,000 | 500 | 2,500 | $5-10 (Colab) | 2-3 hours | ~65% |
| **Phase 2: Production** | 15,000 | 3,000 | 18,000 | $30-45 (RunPod) | 10-15 hours | ~85% |
| **Phase 3: Excellence** | 50,000+ | 10,000+ | 60,000+ | $100-200 | 40-60 hours | ~92%+ |

**Recommendation**: Start with Phase 2 (18K examples). This gives you good quality without excessive cost.

**Data Distribution**:
- 60% temples & architecture
- 15% classical music & dance  
- 10% mathematics & history
- 10% textiles & ayurveda
- 5% philosophy & vedic texts

---

### Stage 4: Training Code (Complete, Production-Ready)

Using **Unsloth** (fastest Gemma fine-tuning library — 2x speedup, 60% less VRAM):

```python
# ═══════════════════════════════════════════════════════════════
# IKS Gemma 3 Multimodal Fine-tuning with Unsloth
# ═══════════════════════════════════════════════════════════════

# ─── INSTALLATION ──────────────────────────────────────────────
# pip install unsloth[gemma-new] @ git+https://github.com/unslothai/unsloth.git
# pip install wandb datasets pillow torch torchvision

# ─── IMPORTS ───────────────────────────────────────────────────
from unsloth import FastVisionModel
from unsloth.chat_templates import get_chat_template
from datasets import load_dataset
import torch
from transformers import TrainingArguments
from trl import SFTTrainer
import wandb
import json
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# STEP 1: Load Gemma 3 12B Vision-Language Model
# ═══════════════════════════════════════════════════════════════

print("🚀 Loading Gemma 3 12B Instruction-tuned Vision Model...")

model, tokenizer = FastVisionModel.from_pretrained(
    model_name="unsloth/gemma-3-12b-it-bnb-4bit",
    max_seq_length=4096,
    dtype=torch.bfloat16,  # Better stability than float16
    load_in_4bit=True,      # QLoRA: 4-bit quantization for VRAM efficiency
)

print("✅ Model loaded successfully")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Add LoRA (Low-Rank Adapter) for Efficient Fine-tuning
# ═══════════════════════════════════════════════════════════════

print("⚙️  Adding LoRA adapters for efficient training...")

model = FastVisionModel.get_peft_model(
    model,
    finetune_vision_layers=True,        # Fine-tune vision encoder (image understanding)
    finetune_language_layers=True,       # Fine-tune language decoder (answer generation)
    finetune_attention_modules=True,     # Train attention mechanisms
    finetune_mlp_modules=True,           # Train feed-forward networks
    r=16,                                # LoRA rank (higher = more parameters, slower)
    lora_alpha=32,                       # LoRA scaling parameter
    lora_dropout=0.05,                   # Dropout for regularization
    bias="none",                         # Don't train bias terms
    random_state=3407,
)

print("✅ LoRA adapters configured")
print(f"   Trainable parameters: {model.get_num_parameters(only_trainable=True):,}")
print(f"   Total parameters: {model.get_num_parameters():,}")
print(f"   Training efficiency: ~{100 * model.get_num_parameters(only_trainable=True) / model.get_num_parameters():.2f}%")

# ═══════════════════════════════════════════════════════════════
# STEP 3: Load Your IKS Dataset
# ═══════════════════════════════════════════════════════════════

print("\n📚 Loading IKS training dataset...")

# Option 1: Load from HuggingFace Hub (recommended)
dataset = load_dataset(
    "your-username/iks-multimodal-dataset",
    split="train",
    trust_remote_code=True,
)

# Option 2: Load from local JSONL files
# def load_local_dataset(folder_path):
#     data = {"messages": []}
#     for jsonl_file in Path(folder_path).glob("*.jsonl"):
#         with open(jsonl_file) as f:
#             for line in f:
#                 data["messages"].append(json.loads(line))
#     return data

print(f"✅ Loaded {len(dataset)} training examples")
print(f"   Breakdown:")
print(f"   - {len([x for x in dataset if 'image' not in str(x.get('messages', []))])} text examples")
print(f"   - {len([x for x in dataset if 'image' in str(x.get('messages', []))])} multimodal examples")

# ═══════════════════════════════════════════════════════════════
# STEP 4: Set Up Chat Template (Important!)
# ═══════════════════════════════════════════════════════════════

print("\n🎯 Configuring chat template...")

# Get proper chat template for Gemma 3
tokenizer = get_chat_template(
    tokenizer,
    chat_template="gemma",
    mapping={"role": "role", "content": "content"},
    tools=None,
)

def formatting_func(examples):
    """Format dataset examples for training."""
    output_texts = []
    for messages in examples["messages"]:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        output_texts.append(text)
    return {"text": output_texts}

dataset = dataset.map(formatting_func, batched=True)

print("✅ Chat template configured")

# ═══════════════════════════════════════════════════════════════
# STEP 5: Configure Training Arguments
# ═══════════════════════════════════════════════════════════════

print("\n⚙️  Setting up training configuration...")

training_args = TrainingArguments(
    # Output and logging
    output_dir="iks-gemma3-12b-lora-v1",
    logging_dir="./logs",
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,  # Keep only 3 latest checkpoints
    
    # Training hyperparameters
    num_train_epochs=3,
    per_device_train_batch_size=2,  # Adjust if you have more VRAM
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,   # Effective batch size = 2 * 4 = 8
    gradient_checkpointing=True,     # Save memory during backward pass
    
    # Learning rate and warmup
    learning_rate=2e-4,
    warmup_steps=50,
    warmup_ratio=0.05,
    lr_scheduler_type="cosine",
    
    # Precision and optimization
    optim="paged_adamw_32bit",  # Memory-efficient optimizer
    fp16=False,
    bf16=True,  # Use bfloat16 for better stability
    
    # Evaluation
    eval_strategy="steps",
    eval_steps=100,
    
    # Device and distributed training
    max_grad_norm=1.0,
    seed=42,
    data_seed=42,
    
    # Reporting
    report_to="wandb",  # Log to Weights & Biases
    run_name="IKS-Gemma3-12B-MultimodalV1",
    push_to_hub=True,
    hub_model_id="your-username/iks-gemma3-12b-finetuned",
)

print("✅ Training configuration ready")

# ═══════════════════════════════════════════════════════════════
# STEP 6: Create Trainer
# ═══════════════════════════════════════════════════════════════

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=4096,
    packing=False,  # Don't pack sequences (better for vision)
)

print("✅ Trainer configured")

# ═══════════════════════════════════════════════════════════════
# STEP 7: Train!
# ═══════════════════════════════════════════════════════════════

print("\n🎓 Starting training...")
print(f"   Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"   Estimated time: 10-15 hours on A100")

FastVisionModel.for_training(model)  # Enable training mode
trainer.train()

print("\n✅ Training complete!")

# ═══════════════════════════════════════════════════════════════
# STEP 8: Save and Upload Model
# ═══════════════════════════════════════════════════════════════

print("\n💾 Saving model...")

# Save locally
model.save_pretrained("iks-gemma3-12b-lora-final")
tokenizer.save_pretrained("iks-gemma3-12b-lora-final")

# Push to HuggingFace Hub
model.push_to_hub(
    "your-username/iks-gemma3-12b",
    token="your-hf-token",
)
tokenizer.push_to_hub(
    "your-username/iks-gemma3-12b",
    token="your-hf-token",
)

print("✅ Model saved and uploaded!")

# ═══════════════════════════════════════════════════════════════
# STEP 9: Inference (Test Your Trained Model)
# ═══════════════════════════════════════════════════════════════

print("\n🧪 Testing trained model...")

FastVisionModel.for_inference(model)  # Optimize for inference

# Example: Image understanding
from PIL import Image

test_image = Image.open("path/to/temple_image.jpg")

# Prepare message for inference
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": test_image},
            {"type": "text", "text": "What is this temple? When was it built?"}
        ]
    }
]

# Tokenize
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_tensors="pt",
    return_dict=True
).to("cuda")

# Generate response
with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
    )

# Decode response
response_text = tokenizer.decode(output[0], skip_special_tokens=True)
print("Model response:")
print(response_text)
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

- **If RAG works well**: You may not need fine-tuning. RAG + Gemma 3 can handle 80% of cases.
- **If RAG has limitations**: Fine-tune to overcome specific gaps
  - Example 1: RAG retrieves documents but student questions are outside the corpus → fine-tune on synthetic queries
  - Example 2: Students ask visual questions about temples → multimodal fine-tuning helps
  - Example 3: Model needs to understand Sanskrit/Tamil inscriptions → language-specific fine-tuning

Start Phase 2 when you have clear evidence of what the model needs to learn that RAG cannot provide.
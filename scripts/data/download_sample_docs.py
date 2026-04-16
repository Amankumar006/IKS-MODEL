#!/usr/bin/env python3
"""Download sample IKS documents for initial testing.

This script downloads a minimal set of documents to test the RAG system.
Full dataset will be collected in Phase 2.
"""

import os
from pathlib import Path

import requests

# Sample documents to download
SAMPLE_DOCUMENTS = {
    # Philosophy
    "isha_upanishad.txt": {
        "url": "https://www.sacred-texts.com/hin/iu/iu.txt",
        "category": "philosophy",
    },
    # Temples
    "chola_temples.txt": {
        "url": None,  # Will use placeholder content
        "category": "temples",
        "content": """Chola Temple Architecture

The Chola dynasty (9th-13th century CE) built magnificent temples that represent the pinnacle of Dravidian architecture.

Key Features:
1. Vimana: Tall pyramidal tower over the sanctum
   - Brihadishvara Temple vimana: 66 meters tall
   - Built from granite without mortar

2. Gopuram: Ornate entrance towers
   - Multiple tiers with intricate sculptures
   - Richly decorated with mythological scenes

3. Sculptural Program:
   - Shaiva mythology scenes
   - Celestial dancers (apsaras)
   - Narrative reliefs from Puranas

4. Materials:
   - Granite construction
   - Ashlar masonry (precision-cut stones)
   - No mortar used

Famous Temples:
- Brihadishvara Temple, Thanjavur (1010 CE)
- Gangaikondacholapuram Temple (1025 CE)
- Airavatesvara Temple, Darasuram (12th century)

UNESCO World Heritage Sites:
All three Great Living Chola Temples are UNESCO World Heritage Sites.
""",
    },
    # Music
    "melakarta_ragas.txt": {
        "url": None,
        "category": "music",
        "content": """The 72 Melakarta Ragas (Carnatic Music)

Melakarta ragas are the parent scales in Carnatic music. There are 72 melakarta ragas, organized in a systematic framework.

Structure:
- Each melakarta has all 7 notes (saptaka)
- Notes: Sa, Ri, Ga, Ma, Pa, Da, Ni, Sa
- Divided into 12 chakras (groups of 6)

The 12 Chakras:
1. Indu (1-6): Kanakangi, Ratnangi, Ganamurti, Vanaspati, Manavati, Tanarupi
2. Netra (7-12): Senavati, Hanumatodi, Dhenuka, Natakapriya, Kokilapriya, Rupavati
3. Agni (13-18): Gayakapriya, Vakulabharanam, Mayamalavagowla, Chakravakam, Suryakantam, Hatakambhari
4. Veda (19-24): Jhankaradhwani, Natabhairavi, Keeravani, Kharaharapriya, Gourimanohari, Varunapriya
5. Bana (25-30): Mararanjani, Charukesi, Sarasangi, Harikambhoji, Dheerashankarabharanam, Naganandini
6. Rutu (31-36): Yagapriya, Ragavardhini, Gangeyabhusani, Vagadheeswari, Soolini, Chalanata
7. Rishi (37-42): Salagam, Jalarnavam, Jhalavarali, Navaneetam, Pavani, Raghupriya
8. Vasu (43-48): Gavambodhi, Bhavapriya, Subhapanthuvara, Shadvidamargini, Suvarnangi, Divyamani
9. Brahma (49-54): Dhavalambari, Namanarayani, Kamavardhini, Ramapriya, Gamanashrama, Vishwambari
10. Disi (55-60): Syamalangi, Shanmukhapriya, Simhendramadhyamam, Hemavati, Dharamavai, Nitimati
11. Rudra (61-66): Kanthamani, Rishabhapriya, Latangi, Vachaspati, Mechakalyani, Chitrambari
12. Aditya (67-72): Sucharitra, Jyotiswaroopini, Dhatuvardani, Nasikabhooshani, Kosalam, Rasikapriya

Usage:
- These are the parent scales
- Janya ragas (derived scales) are created by omitting or modifying notes
- Each melakarta can generate many janya ragas
""",
    },
    # Dance
    "natya_shastra.txt": {
        "url": None,
        "category": "dance",
        "content": """Natya Shastra - The Science of Drama and Dance

The Natya Shastra is a Sanskrit treatise on the performing arts, attributed to the sage Bharata. It is the foundational text for Indian classical dance and drama.

Overview:
- Composed between 200 BCE and 200 CE
- 36 chapters covering various aspects of performance
- Estimated 6000 verses

Key Concepts:

1. Rasa Theory:
   - The aesthetic experience or sentiment
   - Eight primary rasas: Shringara (love), Hasya (humor), Karuna (compassion), Raudra (anger), Veera (heroism), Bhayanaka (fear), Bibhatsa (disgust), Adbhuta (wonder)
   - Ninth rasa: Shanta (peace)

2. Abhinaya (Expression):
   - Angika: Body movements
   - Vachika: Speech and vocal expression
   - Aharya: Costumes and makeup
   - Sattvika: Psychological states

3. Mudras (Hand Gestures):
   - Asamyuta: Single hand gestures (24 types)
   - Samyuta: Combined hand gestures (13 types)
   - Used to convey meanings and emotions

4. Bhavas (States of Being):
   - Sthayi bhavas: Permanent emotional states
   - Sanchari bhavas: Transitory emotional states

5. Classical Dance Forms:
   The Natya Shastra forms the basis for all major Indian classical dance forms:
   - Bharatanatyam
   - Kathak
   - Kathakali
   - Odissi
   - Kuchipudi
   - Manipuri
   - Mohiniyattam
   - Sattriya

Relevance:
- Still studied by dancers and choreographers
- Provides theoretical framework for Indian performing arts
- UNESCO recognized intangible cultural heritage
""",
    },
    # Mathematics
    "indian_mathematics.txt": {
        "url": None,
        "category": "mathematics",
        "content": """Indian Contributions to Mathematics

Ancient India made revolutionary contributions to mathematics that changed the world.

Key Contributions:

1. The Concept of Zero (Shunya):
   - Developed by 5th century CE
   - Brahmagupta's Brahmasphutasiddhanta (628 CE) formalized rules for zero
   - Enabled the decimal place-value system
   - Crucial for advanced mathematics

2. Decimal Place-Value System:
   - Used today worldwide
   - Base-10 system with place values (units, tens, hundreds)
   - Far more efficient than Roman numerals

3. Aryabhata's Contributions (476-550 CE):
   - Approximated pi (π) as 3.1416
   - Calculated Earth's circumference
   - Sine tables in trigonometry
   - Solutions to linear and quadratic equations

4. Brahmagupta's Contributions (598-668 CE):
   - Rules for arithmetic with zero
   - Solutions to quadratic equations
   - Formula for area of cyclic quadrilateral
   - Introduction of negative numbers

5. Other Important Mathematicians:
   - Bhaskara II (1114-1185): Calculus concepts, astronomy
   - Madhava (1340-1425): Infinite series for trigonometric functions
   - Virasena (710-790): Work on logarithms

6. Sulbasutras (800-500 BCE):
   - Geometric constructions for Vedic altars
   - Pythagorean theorem before Pythagoras
   - Square roots and cube roots

Impact:
- Transformed mathematics globally
- Enabled scientific revolution in Europe
- Arabic numerals originated in India
- Foundation of modern computing

Sources:
- Aryabhatiya by Aryabhata
- Brahmasphutasiddhanta by Brahmagupta
- Lilavati by Bhaskara II
""",
    },
    # History
    "mauryan_empire.txt": {
        "url": None,
        "category": "history",
        "content": """Mauryan Empire (322-185 BCE)

The Mauryan Empire was the first pan-Indian empire, unifying most of the Indian subcontinent.

Key Rulers:

1. Chandragupta Maurya (322-298 BCE):
   - Founded the empire
   - Overthrew the Nanda dynasty
   - Unified North India
   - Defeated Seleucus I (Alexander's general)
   - Later became Jain monk

2. Bindusara (298-272 BCE):
   - Expanded empire southward
   - Maintained relations with Greek kingdoms

3. Ashoka the Great (272-232 BCE):
   - Most famous Mauryan ruler
   - Expanded empire to cover almost all of Indian subcontinent
   - Converted to Buddhism after Kalinga War (261 BCE)
   - Promoted Dhamma (moral law)
   - Built stupas and pillars
   - Sent missionaries abroad

Administration:
- Highly centralized bureaucracy
- Divided into provinces (Janapadas)
- Efficient tax collection
- Standing army of 600,000 soldiers
- Spy network (espionage)

Kautilya's Arthashastra:
- Treatise on statecraft, economics, and military strategy
- Written by Chanakya (Kautilya), advisor to Chandragupta
- Covers: governance, diplomacy, warfare, economics
- Influential text on political science

Achievements:
- Standardized weights and measures
- Built Grand Trunk Road (Uttarapatha)
- Spread Buddhism to Sri Lanka and Southeast Asia
- Established stone inscriptions (Edicts of Ashoka)
- Created first monumental stone sculpture

Decline:
- Weak successors after Ashoka
- Economic strain from large empire
- Breakaway of southern territories
- Finally overthrown by Shunga dynasty (185 BCE)

Legacy:
- Model for later Indian empires
- Spread of Buddhism
- Ashoka's chakra on Indian flag
- Lion Capital of Ashoka is India's national emblem
""",
    },
}


def download_document(name: str, info: dict, output_dir: Path) -> bool:
    """Download or create a document.

    Args:
        name: Document filename
        info: Document info dict
        output_dir: Output directory

    Returns:
        True if successful
    """
    output_path = output_dir / name

    try:
        if info["url"]:
            # Download from URL
            response = requests.get(info["url"], timeout=30)
            response.raise_for_status()
            content = response.text
        else:
            # Use provided content
            content = info["content"]

        # Write file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Created: {name}")
        return True

    except Exception as e:
        print(f"❌ Failed: {name} - {e}")
        return False


def main():
    """Main function."""
    # Create output directory
    output_dir = Path("data/documents")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("📚 Downloading sample IKS documents...")
    print(f"Output directory: {output_dir.absolute()}")
    print()

    # Download/create documents
    success_count = 0
    for name, info in SAMPLE_DOCUMENTS.items():
        if download_document(name, info, output_dir):
            success_count += 1

    print()
    print(f"✅ Successfully created {success_count}/{len(SAMPLE_DOCUMENTS)} documents")
    print()
    print("Next steps:")
    print("1. Run: uv run python src/iks_rag/ui/gradio_app.py")
    print("2. Open browser at http://localhost:7860")
    print()
    print("To add more documents, place them in data/documents/")


if __name__ == "__main__":
    main()

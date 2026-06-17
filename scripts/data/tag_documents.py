"""Script to tag base documents with metadata validation fields.

Generates `data/processed/document_metadata.json` mapping each document
to source, author, century, region, tradition, confidence, type, and original language.
"""

import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "document_metadata.json"


def match_metadata(filename: str) -> dict:
    """Determine metadata fields based on filename patterns."""
    fn = filename.lower()

    # Default metadata structure
    meta = {
        "source": "Unknown Source",
        "author": "Unknown",
        "century": "Unknown",
        "region": "Pan-Indian",
        "tradition": "General",
        "confidence": "Scholarly Consensus",
        "type": "Secondary",
        "language_original": "English",
    }

    # 1. Arthashastra
    if "arthashastra" in fn or "kautilya" in fn:
        meta.update(
            {
                "source": "Arthashastra",
                "author": "Kautilya",
                "century": "4th century BCE",
                "region": "Taxila / Pataliputra",
                "tradition": "Arthashastra / Statecraft",
                "confidence": "Primary source — translated",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )

    # 2. Aryabhatiya / Mathematics
    elif "aryabhata" in fn or "aryabhatiya" in fn:
        meta.update(
            {
                "source": "Aryabhatiya",
                "author": "Aryabhata",
                "century": "5th century CE (499 CE)",
                "region": "Kusumapura (Bihar)",
                "tradition": "Ganita / Astronomy & Mathematics",
                "confidence": "Primary source — translated",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )
    elif "mathematics" in fn or "bhaskara" in fn or "lilavati" in fn or "madhava" in fn:
        meta.update(
            {
                "source": "Kerala School / Classical Mathematics",
                "author": "Madhava / Bhaskara II",
                "century": "12th - 14th century CE",
                "region": "Kerala / South India",
                "tradition": "Ganita / Mathematics",
                "confidence": "Scholarly Consensus",
                "type": "Primary",
                "language_original": "Sanskrit / Malayalam",
            }
        )

    # 3. Natyashastra / Performing Arts
    elif "natya" in fn or "bharata_muni" in fn or "abhinaya" in fn:
        meta.update(
            {
                "source": "Natyashastra",
                "author": "Bharata Muni",
                "century": "2nd century BCE – 2nd century CE",
                "region": "Pan-Indian",
                "tradition": "Natya / Performing Arts",
                "confidence": "Primary source — translated",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )

    # 4. Panini / Ashtadhyayi
    elif "ashtadhyayi" in fn or "panini" in fn:
        meta.update(
            {
                "source": "Ashtadhyayi",
                "author": "Panini",
                "century": "4th century BCE",
                "region": "Gandhara (North-West India)",
                "tradition": "Vyakarana / Linguistics",
                "confidence": "Primary source — translated",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )

    # 5. Vedas & Upanishads
    elif "rigveda" in fn:
        meta.update(
            {
                "source": "Rigveda",
                "author": "Vedic Rishis",
                "century": "1500 BCE – 1200 BCE",
                "region": "Sapta Sindhu (North-West India)",
                "tradition": "Shruti / Vedic",
                "confidence": "Primary source — oral/translated",
                "type": "Primary",
                "language_original": "Vedic Sanskrit",
            }
        )
    elif "veda" in fn or "vedas" in fn:
        meta.update(
            {
                "source": "Vedic Samhitas",
                "author": "Vedic Rishis",
                "century": "1200 BCE – 1000 BCE",
                "region": "North India",
                "tradition": "Shruti / Vedic",
                "confidence": "Primary source — oral/translated",
                "type": "Primary",
                "language_original": "Vedic Sanskrit",
            }
        )
    elif "upanishad" in fn or "concept_brahman" in fn or "concept_atman" in fn:
        meta.update(
            {
                "source": "Upanishads",
                "author": "Vedic Sages",
                "century": "8th – 6th century BCE",
                "region": "Gangetic Plains",
                "tradition": "Vedanta / Philosophical",
                "confidence": "Primary source — translated",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )

    # 6. Epics (Ramayana / Mahabharata / Gita)
    elif "gita" in fn:
        meta.update(
            {
                "source": "Bhagavad Gita",
                "author": "Vyasa",
                "century": "5th – 2nd century BCE",
                "region": "Kurukshetra / North India",
                "tradition": "Smriti / Philosophical",
                "confidence": "Traditional Account",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )
    elif "ramayana" in fn or "andal" in fn:
        meta.update(
            {
                "source": "Ramayana",
                "author": "Valmiki",
                "century": "5th – 4th century BCE",
                "region": "Ayodhya / Mithila",
                "tradition": "Itihasa / Epic",
                "confidence": "Traditional Account",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )
    elif "mahabharata" in fn:
        meta.update(
            {
                "source": "Mahabharata",
                "author": "Vyasa",
                "century": "4th century BCE – 4th century CE",
                "region": "Hastinapur / Kurukshetra",
                "tradition": "Itihasa / Epic",
                "confidence": "Traditional Account",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )

    # 7. Ayurveda & Medicine
    elif "ayurveda" in fn or "charaka" in fn or "sushruta" in fn or "ashtanga" in fn or "tridosha" in fn or "siddha" in fn:
        meta.update(
            {
                "source": "Ayurvedic Samhitas",
                "author": "Charaka / Sushruta / Vagbhata",
                "century": "6th century BCE – 6th century CE",
                "region": "Pan-Indian",
                "tradition": "Ayurveda / Medicine",
                "confidence": "Primary source — translated",
                "type": "Primary",
                "language_original": "Sanskrit",
            }
        )

    # 8. Temple Architecture (Vastu / Nagara / Dravidian / Chola / Hampi / Ajanta / Ellora)
    elif any(x in fn for x in ["temple", "architecture", "vastu", "chola", "hampi", "ajanta", "ellora", "shore", "brihadeeswarar", "khajuraho"]):
        meta.update(
            {
                "source": "Vastu Shastra / Archaeological Records",
                "author": "Royal Builders & Guilds",
                "century": "2nd century BCE – 11th century CE",
                "region": "South & Central India",
                "tradition": "Vastu / Temple Architecture",
                "confidence": "Evidence: Strong",
                "type": "Primary / Archaeological",
                "language_original": "Sanskrit / Tamil / Kannada",
            }
        )

    # 9. Classical Music (Ragas / Melakarta / Gharana / Hindustani / Carnatic)
    elif any(x in fn for x in ["raga", "melakarta", "gharana", "classical_music", "mridangam", "sitar", "tabla", "veena", "tala_music"]):
        meta.update(
            {
                "source": "Gandharva Veda / Sangita Shastra",
                "author": "Various Musicologists",
                "century": "Vedic - Medieval - Modern",
                "region": "Carnatic / Hindustani",
                "tradition": "Sangita / Indian Classical Music",
                "confidence": "Scholarly Consensus",
                "type": "Secondary",
                "language_original": "Sanskrit / Hindi / Telugu",
            }
        )

    # 10. Regional Culture & Dances
    elif any(x in fn for x in ["regional_", "bihu", "chhau", "ghoomar", "lavani", "theyyam", "yakshagana", "bhangra", "kathakali", "kathak", "odissi", "sattriya", "bharatanatyam", "mohiniyattam"]):
        meta.update(
            {
                "source": "Folk & Classical Performing Arts",
                "author": "Traditional Performers / Sages",
                "century": "Ancient – Contemporary",
                "region": "Various States (Assam, Kerala, Tamil Nadu, Punjab, Rajasthan, Maharashtra)",
                "tradition": "Performing Arts / Folk Tradition",
                "confidence": "Scholarly Consensus",
                "type": "Secondary",
                "language_original": "Regional Languages",
            }
        )

    # 11. Modern Literature
    elif fn.startswith("lit_") or "world_wiki_lit" in fn or any(x in fn for x in ["tagore", "premchand", "manto", "arundhati", "roy", "kamala", "narayan", "ghosh", "chughtai"]):
        meta.update(
            {
                "source": "Modern Indian Literature",
                "author": "Rabindranath Tagore / Premchand / Ismat Chughtai / Arundhati Roy / etc.",
                "century": "19th – 20th century CE",
                "region": "Pan-Indian",
                "tradition": "Sahitya / Modern Literature",
                "confidence": "Evidence: Strong",
                "type": "Secondary",
                "language_original": "Bengali / Hindi / Urdu / English",
            }
        )

    # 12. Philosophy Concepts (Karma, Moksha, Samsara, Vedanta, Samkhya, Nyaya, Vaisheshika)
    elif any(x in fn for x in ["concept_", "vedanta", "samkhya", "nyaya", "vaisheshika", "jainism", "buddhism"]):
        meta.update(
            {
                "source": "Six Darshanas / Upanishadic Philosophy",
                "author": "Kanada / Gautama / Kapila / Badarayana",
                "century": "6th century BCE – 2nd century CE",
                "region": "North & East India",
                "tradition": "Darshana / Philosophical School",
                "confidence": "Scholarly Consensus",
                "type": "Secondary",
                "language_original": "Sanskrit",
            }
        )

    # 13. Sacred Places (Kumbh, Varanasi, Vrindavan, Char Dham, Golden Temple, Rishikesh, Pushkar, etc.)
    elif any(x in fn for x in ["sacred_", "kumbh", "varanasi", "vrindavan", "char_dham", "golden_temple", "rishikesh", "pushkar", "velankanni", "amarnath", "bodh_gaya"]):
        meta.update(
            {
                "source": "Sacred Geography / Tirtha Pilgrimage",
                "author": "Traditional Sages",
                "century": "Vedic – Contemporary",
                "region": "Pan-Indian Sacred sites",
                "tradition": "Tirtha / Sacred Geography",
                "confidence": "Scholarly Consensus",
                "type": "Secondary",
                "language_original": "Sanskrit / Hindi",
            }
        )

    return meta


def main():
    """Main execution function to scan data/documents/ and output metadata."""
    if not DOCUMENTS_DIR.exists():
        print(f"❌ Error: documents directory not found at {DOCUMENTS_DIR}")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    metadata_map = {}
    total_docs = 0

    print("🏷️  Scanning and tagging documents in data/documents/...")

    for path in DOCUMENTS_DIR.iterdir():
        if path.is_file() and path.suffix in [".txt", ".md", ".pdf", ".html", ".json"] and path.name != ".gitkeep":
            meta = match_metadata(path.name)
            metadata_map[path.name] = meta
            total_docs += 1

    # Write registry
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, indent=2, ensure_ascii=False)

    print(f"✅ Tagging complete! Tagged {total_docs} documents.")
    print(f"💾 Registry written to {OUTPUT_FILE}")

    # Display breakdown
    traditions = {}
    regions = {}
    for doc, meta in metadata_map.items():
        trad = meta["tradition"]
        reg = meta["region"]
        traditions[trad] = traditions.get(trad, 0) + 1
        regions[reg] = regions.get(reg, 0) + 1

    print("\n--- 📊 Tradition Distribution ---")
    for trad, count in sorted(traditions.items(), key=lambda x: x[1], reverse=True):
        print(f"- {trad}: {count}")

    print("\n--- 📊 Regional Distribution ---")
    for reg, count in sorted(regions.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"- {reg}: {count}")


if __name__ == "__main__":
    main()

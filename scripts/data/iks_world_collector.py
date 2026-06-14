"""
IKS World Collector - Phase 2.1
================================
Expands the IKS corpus from dry facts into a "World Gateway" of feeling,
focusing on the 7 new domains: Literature, Festivals, Sacred Geography,
Mythology, Untranslatable Words, Ragas as emotion, and Regional India.

Usage
-----
  python scripts/data/iks_world_collector.py
"""

import os
import re
import time
import textwrap
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ── Directories ────────────────────────────────────────────────────────────────
PROC_DIR = Path("data/documents")
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ── HTTP session ───────────────────────────────────────────────────────────────
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "IKS-World-Collector/1.0 (Contact: your-email@example.com)",
    "Accept": "application/json, text/plain, */*",
})

WIKI_DELAY = 0.5
WIKI_API = "https://en.wikipedia.org/w/api.php"

# ── Text utilities ─────────────────────────────────────────────────────────────
def clean_text(raw: str) -> str:
    raw = re.sub(r"={2,}[^=\n]+={2,}", "", raw)          # == Headings ==
    raw = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", raw) # [[links]]
    raw = re.sub(r"\{\{[^}]*\}\}", "", raw)               # {{templates}}
    raw = re.sub(r"<[^>]+>", " ", raw)                    # <html>
    raw = re.sub(r"https?://\S+", "", raw)                # URLs
    raw = re.sub(r"\[\d+\]", "", raw)                     # [1] citations
    raw = re.sub(r"[ \t]{2,}", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    lines = [l.strip() for l in raw.splitlines() if len(l.strip()) >= 25]
    return "\n".join(lines).strip()

def safe_name(s: str) -> str:
    return re.sub(r"[^\w\s-]", "", s).strip().replace(" ", "_")[:80]

# ══════════════════════════════════════════════════════════════════════════════
#  1. WIKIPEDIA TOPICS
# ══════════════════════════════════════════════════════════════════════════════
WIKIPEDIA_TOPICS = {
    "Literature": [
        "Rabindranath_Tagore", "R._K._Narayan", "Munshi_Premchand",
        "Arundhati_Roy", "Kamala_Das", "Saadat_Hasan_Manto",
        "Ismat_Chughtai", "Mahasweta_Devi", "A._K._Ramanujan",
        "Sangam_literature", "Bhakti_movement"
    ],
    "Sacred Geography": [
        "Varanasi", "Char_Dham", "Ganges", "Vrindavan", "Kumbh_Mela",
        "Kailash_Manasarovar", "Tirupati", "Rameswaram", "Kedarnath_Temple"
    ],
    "Mythology as living truth": [
        "Ramayana", "Mahabharata", "Panchatantra", "Jataka_tales",
        "Puranas", "Dashavatara", "Kurukshetra_War", "Gita_Govinda"
    ],
    "Regional India": [
        "Culture_of_Kerala", "Culture_of_West_Bengal", "Culture_of_Rajasthan",
        "Culture_of_Tamil_Nadu", "Culture_of_Karnataka", "Culture_of_Punjab,_India",
        "Yakshagana", "Theyyam", "Chhau_dance", "Baul"
    ]
}

def wiki_fetch(page_title: str):
    params = {
        "action": "query", "titles": page_title.replace("_", " "),
        "prop": "extracts", "explaintext": True, "exsectionformat": "plain",
        "redirects": 1, "format": "json",
    }
    try:
        r = SESSION.get(WIKI_API, params=params, timeout=20)
        pages = r.json().get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid != "-1":
                return page.get("title", page_title), page.get("extract", "")
    except Exception as e:
        print(f"Error fetching {page_title}: {e}")
    return None, None

def collect_wikipedia():
    print("\n--- Collecting Wikipedia Topics ---")
    for domain, titles in WIKIPEDIA_TOPICS.items():
        print(f"Domain: {domain}")
        for title in tqdm(titles):
            out_path = PROC_DIR / f"world_wiki_{safe_name(title)}.txt"
            if out_path.exists(): continue
            
            real_title, text = wiki_fetch(title)
            if text and len(text.split()) > 100:
                cleaned = clean_text(text)
                # Include a tiny header so the generative script knows what domain it belongs to
                header = f"Domain: {domain}\nTitle: {real_title}\n\n"
                out_path.write_text(header + cleaned, encoding="utf-8")
            time.sleep(WIKI_DELAY)

# ══════════════════════════════════════════════════════════════════════════════
#  2. SENSORY & EMOTIONAL EMBEDDED CONCEPTS
# ══════════════════════════════════════════════════════════════════════════════
EMBEDDED_TOPICS = [
    {
        "title": "Untranslatable_Jugaad",
        "domain": "Untranslatable words",
        "text": "Jugaad is not just a hack. It is the Indian spirit of survival and frugal innovation. It's the mechanic on the side of a dusty highway fixing a tractor with a piece of wire and pure intuition. It represents a worldview that refuses to accept dead ends. It feels like the triumphant roar of an engine springing back to life against all odds."
    },
    {
        "title": "Untranslatable_Dharma",
        "domain": "Untranslatable words",
        "text": "Dharma is a word too massive for 'religion' or 'duty'. It is the invisible fabric that holds the universe together. The dharma of fire is to burn; the dharma of a river is to flow. For a human, it is the quiet, heavy alignment with what is fundamentally right. It is not something you believe; it is something you inhabit. It feels like the unwavering gravity holding a planet in orbit."
    },
    {
        "title": "Untranslatable_Rasa",
        "domain": "Untranslatable words",
        "text": "Rasa translates loosely to 'juice' or 'essence'. In art, it is the emotional flavor that a piece of music, dance, or poetry leaves on your tongue. The nine rasas (Navarasa) include Shringara (love/beauty), Hasya (joy), Karuna (sorrow), Raudra (fury), Vira (heroism), Bhayanaka (terror), Bibhatsa (disgust), Adbhuta (wonder), and Shanta (peace). Without rasa, art is just technique; with rasa, it becomes an emotional possession."
    },
    {
        "title": "Untranslatable_Ananda",
        "domain": "Untranslatable words",
        "text": "Ananda is joy, but not the joy of winning a prize or eating a good meal. It is joy without an object. It is the fundamental bliss of existing, uncaused and unending. When someone experiences Ananda, they feel a profound, silent, overflowing peace that makes everything else feel small."
    },
    {
        "title": "Ragas_Bhairavi",
        "domain": "Music as emotion",
        "text": "Raga Bhairavi is the quintessential morning raga, yet it is almost universally played at the very end of a concert. It uses all 12 notes. It carries the immense, sweet sadness of leave-taking. Imagine a candle burning down, the scent of jasmine lingering in the air, and the feeling of something profoundly beautiful coming to an end. It evokes the feeling of devotion tinged with separation."
    },
    {
        "title": "Ragas_Yaman",
        "domain": "Music as emotion",
        "text": "Raga Yaman is the raga of the early evening, just as the lamps are being lit. It evokes Shringara—a deep, romantic yearning. It feels like standing by a window at dusk, waiting for someone you love, feeling both the vastness of the twilight and the intimate ache in your chest. It unfolds slowly, majestically, wrapping the listener in warmth."
    },
    {
        "title": "Ragas_Darbari",
        "domain": "Music as emotion",
        "text": "Raga Darbari is a raga of the deep midnight. Created in the court of Emperor Akbar by Tansen, it is heavy, slow, and regal. It evokes a profound solemnity and majestic peace. It feels like walking through the dark, massive stone corridors of a sleeping palace—weighty, historical, and deeply internal."
    },
    {
        "title": "Festivals_Diwali",
        "domain": "Festivals as experience",
        "text": "Diwali is not just the 'festival of lights'. It is the smell of camphor and clarified butter burning in terracotta diyas. It is the sharp, exhilarating crack of fireworks tearing through the autumn night. Two weeks before, homes smell of roasted chickpea flour and hot oil as families prepare chakli and laddoos. It feels like the entire country is pushing back the darkness with a collective, joyful exhale, celebrating the return of rightness and the victory of inner light."
    },
    {
        "title": "Festivals_Durga_Puja",
        "domain": "Festivals as experience",
        "text": "Durga Puja in Bengal is a sensory explosion. It is the rhythmic, hypnotic beat of the dhak (drums) vibrating in your chest. It is the scent of shiuli flowers and incense smoke thick in the damp October air. Massive, unimaginably intricate idols of the Goddess are created only to be dissolved back into the river. It feels like a ten-day fever dream of art, devotion, food, and the fierce, triumphant presence of the feminine divine."
    },
    {
        "title": "Festivals_Onam",
        "domain": "Festivals as experience",
        "text": "Onam is the golden harvest of Kerala. The air smells of coconut oil, jasmine, and fresh banana leaves. Intricate carpets of fresh flowers (Pookkalam) are laid at the threshold of every home. The backwaters erupt with the furious energy of snake boat races. It culminates in the Sadhya, a massive feast of 26 dishes served on a plantain leaf, creating a profound feeling of abundance, gratitude, and communal harmony."
    }
]

def collect_embedded():
    print("\n--- Generating Sensory Domains ---")
    for item in tqdm(EMBEDDED_TOPICS):
        out_path = PROC_DIR / f"world_embedded_{item['title']}.txt"
        header = f"Domain: {item['domain']}\nTitle: {item['title'].replace('_', ' ')}\n\n"
        out_path.write_text(header + item["text"], encoding="utf-8")

if __name__ == "__main__":
    collect_embedded()
    collect_wikipedia()
    print("\n✓ World Gateway Corpus Expansion Complete.")

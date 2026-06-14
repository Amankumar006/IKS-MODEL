"""
IKS Data Collector  v2.0
========================
Automatically downloads and prepares the Indian Knowledge Systems
corpus from Wikipedia (MediaWiki API), Archive.org, NPTEL, and
supplementary government / cultural heritage websites.

Usage
-----
  python iks_data_collector.py              # full run (all sources)
  python iks_data_collector.py --source wiki
  python iks_data_collector.py --source archive
  python iks_data_collector.py --source nptel
  python iks_data_collector.py --source supplementary
  python iks_data_collector.py --test       # 2-3 items per source

Requirements
------------
  pip install requests beautifulsoup4 tqdm colorama
  pip install pymupdf          # optional: extract text from PDFs

Output
------
  iks_corpus/
  ├── wikipedia/          raw Wikipedia article text
  ├── archive_org/        downloaded PDFs + raw text
  ├── nptel/              NPTEL / SWAYAM page text
  ├── supplementary/      other web sources
  ├── processed/          <-- point LlamaIndex here
  └── metadata.json       full collection log
"""

import os
import re
import json
import time
import argparse
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

# ── Crawl delays (be polite) ───────────────────────────────────────────────────
WIKI_DELAY = 0.5
ARCH_DELAY = 1.5
WEB_DELAY  = 1.0

# ── Directories ────────────────────────────────────────────────────────────────
BASE_DIR    = Path("iks_corpus")
WIKI_DIR    = BASE_DIR / "wikipedia"
ARCHIVE_DIR = BASE_DIR / "archive_org"
NPTEL_DIR   = BASE_DIR / "nptel"
SUPP_DIR    = BASE_DIR / "supplementary"
PROC_DIR    = BASE_DIR / "processed"
META_FILE   = BASE_DIR / "metadata.json"

for _d in [WIKI_DIR, ARCHIVE_DIR, NPTEL_DIR, SUPP_DIR, PROC_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── HTTP session ───────────────────────────────────────────────────────────────
# Wikipedia requires a descriptive User-Agent (not a browser UA).
# Format: "<project>/<version> (<contact>)"
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "IKS-RAG-Collector/2.0 "
        "(VTU Indian Knowledge Systems research; "
        "contact: your-email@example.com)"
    ),
    "Accept": "application/json, text/plain, */*",
})

# ── Logging ────────────────────────────────────────────────────────────────────
def ok(msg):   print(f"{Fore.GREEN}  ✓  {msg}{Style.RESET_ALL}")
def info(msg): print(f"{Fore.CYAN}  →  {msg}{Style.RESET_ALL}")
def warn(msg): print(f"{Fore.YELLOW}  !  {msg}{Style.RESET_ALL}")
def err(msg):  print(f"{Fore.RED}  ✗  {msg}{Style.RESET_ALL}")
def head(msg):
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'─'*60}\n  {msg}\n{'─'*60}"
          f"{Style.RESET_ALL}")

# ── Metadata ───────────────────────────────────────────────────────────────────
metadata: list[dict] = []

def log_doc(source, title, path, url, word_count, domain):
    metadata.append({
        "source":     source,
        "title":      title,
        "file":       str(path),
        "url":        url,
        "domain":     domain,
        "word_count": word_count,
        "collected":  datetime.now().isoformat(),
    })

def save_metadata():
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    info(f"Metadata saved → {META_FILE}  ({len(metadata)} documents)")

# ── Text utilities ─────────────────────────────────────────────────────────────

def clean_text(raw: str) -> str:
    raw = re.sub(r"={2,}[^=\n]+={2,}", "", raw)          # == Headings ==
    raw = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]",
                 r"\1", raw)                               # [[links]]
    raw = re.sub(r"\{\{[^}]*\}\}", "", raw)               # {{templates}}
    raw = re.sub(r"<[^>]+>", " ", raw)                    # <html>
    raw = re.sub(r"https?://\S+", "", raw)                # URLs
    raw = re.sub(r"\[\d+\]", "", raw)                     # [1] citations
    raw = re.sub(r"[ \t]{2,}", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    lines = [l.strip() for l in raw.splitlines()
             if len(l.strip()) >= 25]
    return "\n".join(lines).strip()


def make_header(source, title, url, domain) -> str:
    return textwrap.dedent(f"""\
        SOURCE: {source}
        TITLE: {title}
        URL: {url}
        DOMAIN: {domain}
        COLLECTED: {datetime.now().isoformat()}
        {'─' * 60}

    """)


def safe_name(s: str) -> str:
    return re.sub(r"[^\w\s-]", "", s).strip().replace(" ", "_")[:80]


def already_done(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 500


# ══════════════════════════════════════════════════════════════════════════════
#  1. WIKIPEDIA  —  MediaWiki action API (direct HTTP, no library)
# ══════════════════════════════════════════════════════════════════════════════
#
#  Key fix from v1: the wikipedia-api library sends a malformed User-Agent
#  that triggers Wikipedia's bot-protection 403s.  We call the API directly
#  with SESSION (which has the correct descriptive UA per WMF policy).
#

WIKI_API = "https://en.wikipedia.org/w/api.php"

WIKIPEDIA_TOPICS: dict[str, list[str]] = {

    "IKS Overview": [
        "Indian_knowledge_systems",
        "Indian_philosophy",
        "Vedas", "Rigveda", "Samaveda", "Yajurveda", "Atharvaveda",
        "Vedangas", "Upanishads", "Brahma_Sutras", "Puranas",
        "Ramayana", "Mahabharata", "Bhagavad_Gita",
        "Nyaya", "Vaisheshika", "Samkhya",
        "Yoga_Sutras_of_Patanjali",
        "Advaita_Vedanta", "Dvaita_Vedanta",
        "Buddhism_in_India", "Jainism", "Dharma",
    ],

    "Mathematics": [
        "Indian_mathematics",
        "History_of_the_Hindu%E2%80%93Arabic_numeral_system",
        "Aryabhata", "Brahmagupta", "Bhaskara_II",
        "Madhava_of_Sangamagrama",
        "Pingala", "Sulba_Sutras", "Vedic_Mathematics",
        "Lilavati", "Brahmasphutasiddhanta",
        "Kerala_school_of_astronomy_and_mathematics",
    ],

    "Astronomy & Science": [
        "Indian_astronomy", "Aryabhatiya", "Surya_Siddhanta",
        "Varahamihira", "Jantar_Mantar,_Jaipur",
        "Indian_atomism", "Kanada_(philosopher)",
        "Wootz_steel", "Iron_pillar_of_Delhi",
        "Rasashastra", "Indian_alchemy",
    ],

    "Linguistics": [
        "Sanskrit", "Panini_(grammarian)", "Ashtadhyayi",
        "Tamil_language", "Tolkappiyam", "Sangam_literature",
        "Kannada_literature", "Telugu_language",
        "Pali", "Prakrit", "Devanagari",
    ],

    "Arts & Crafts": [
        "Indian_art", "Indian_painting", "Madhubani_painting",
        "Tanjore_painting", "Warli_painting", "Pattachitra",
        "Indian_sculpture", "Gandhara_art",
        "Indian_miniature", "Mughal_painting",
    ],

    "Temple Architecture": [
        "Hindu_temple_architecture",
        "Nagara_architecture", "Dravidian_architecture", "Vesara",
        "Brihadeeswarar_Temple", "Khajuraho_temples",
        "Sun_Temple,_Konark", "Hampi",
        "Ellora_Caves", "Ajanta_Caves", "Shore_Temple",
        "Meenakshi_Amman_Temple", "Vastu_shastra",
        "Indus_Valley_civilisation", "Mohenjo-daro",
    ],

    "Medicine & Health": [
        "Ayurveda", "Charaka", "Charaka_Samhita",
        "Sushruta", "Sushruta_Samhita",
        "Ashtanga_Hridayam", "Siddha_medicine",
        "Yoga", "Pranayama", "Panchakarma", "Tridosha",
    ],

    "Classical Music": [
        "Indian_classical_music", "Carnatic_music",
        "Hindustani_classical_music",
        "Raga", "Tala_(music)", "Natya_Shastra",
        "Bharata_Muni", "Veena", "Sitar", "Tabla",
        "Mridangam", "Melakarta", "Dhrupad", "Khayal",
        "Thyagaraja", "Purandara_Dasa",
    ],

    "Classical Dance": [
        "Bharatanatyam", "Kathak", "Kuchipudi", "Odissi",
        "Kathakali", "Manipuri_dance", "Mohiniyattam", "Sattriya",
        "Abhinaya", "Mudra_(yoga)",
    ],

    "Textiles & Clothing": [
        "Indian_textiles", "Sari", "Banarasi_sari",
        "Kanjivaram_silk", "Chanderi_fabric",
        "Bandhani", "Phulkari", "Pashmina",
        "Block_printing_in_India", "Ikat", "Kalamkari", "Zari",
        "Chikankari",
    ],

    "Governance & Agriculture": [
        "Arthashastra", "Kautilya", "Ashoka",
        "Edicts_of_Ashoka", "Maurya_Empire", "Gupta_Empire",
        "Chola_dynasty", "Vijayanagara_Empire",
        "Indian_agriculture",
        "History_of_agriculture_in_the_Indian_subcontinent",
        "Stepwell",
    ],
}


def wiki_fetch(page_title: str) -> Optional[dict]:
    """
    Call the MediaWiki action API to fetch full plain-text extract.
    Returns {"title", "extract", "url"} or None.
    """
    params = {
        "action":          "query",
        "titles":          page_title.replace("_", " "),
        "prop":            "extracts|info",
        "explaintext":     True,
        "exsectionformat": "plain",
        "inprop":          "url",
        "redirects":       1,
        "format":          "json",
    }
    try:
        r = SESSION.get(WIKI_API, params=params, timeout=20)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return None
            return {
                "title":   page.get("title", page_title),
                "extract": page.get("extract", ""),
                "url":     page.get("fullurl",
                           f"https://en.wikipedia.org/wiki/{page_title}"),
            }
    except Exception as e:
        err(f"  API error for '{page_title}': {e}")
    return None


def collect_wikipedia(test_mode: bool = False) -> int:
    head("WIKIPEDIA COLLECTION")
    topics = WIKIPEDIA_TOPICS
    if test_mode:
        # 2 domains, 2 pages each
        topics = {k: v[:2] for k, v in
                  dict(list(topics.items())[:2]).items()}

    collected = 0
    for domain, pages in topics.items():
        info(f"Domain: {domain}  ({len(pages)} pages)")
        for title in tqdm(pages, desc=f"  {domain[:32]}", leave=False):
            proc_path = PROC_DIR / f"wiki_{safe_name(title)}.txt"
            if already_done(proc_path):
                continue

            result = wiki_fetch(title)
            if not result:
                warn(f"  Not found: {title}")
                time.sleep(WIKI_DELAY)
                continue

            text = result["extract"]
            if len(text.split()) < 150:
                warn(f"  Too short ({len(text.split())} w): {title}")
                time.sleep(WIKI_DELAY)
                continue

            cleaned = clean_text(text)
            header  = make_header("Wikipedia", result["title"],
                                  result["url"], domain)
            proc_path.write_text(header + cleaned, encoding="utf-8")
            (WIKI_DIR / f"{safe_name(title)}.txt").write_text(
                text, encoding="utf-8")

            wc = len(cleaned.split())
            log_doc("wikipedia", result["title"], proc_path,
                    result["url"], wc, domain)
            ok(f"  {result['title']}  ({wc:,} words)")
            collected += 1
            time.sleep(WIKI_DELAY)

    ok(f"Wikipedia: {collected} articles collected")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  2. ARCHIVE.ORG  —  metadata-driven file discovery
# ══════════════════════════════════════════════════════════════════════════════
#
#  Key fix from v1: instead of guessing filenames, we query
#  /metadata/{id} first to get the real file list, then prefer
#  *_djvu.txt (best OCR) > *.txt > PDF download.
#

ARCHIVE_ITEMS = [
    {
        "id":     "aryabhatiya00arya",
        "title":  "Aryabhatiya — W.E. Clark translation (1930)",
        "domain": "Mathematics & Astronomy",
    },
    {
        "id":     "arthashastra00kaut",
        "title":  "Arthashastra — R. Shamasastry translation (1915)",
        "domain": "Governance",
    },
    {
        "id":     "natyasastra00bharuoft",
        "title":  "Natyasastra of Bharata Muni Vol 1",
        "domain": "Classical Dance & Drama",
    },
    {
        "id":     "historyofindianma00dattrich",
        "title":  "History of Hindu Mathematics — Datta & Singh",
        "domain": "Mathematics",
    },
    {
        "id":     "indianarchitect00haveuoft",
        "title":  "The Indian Architect — E.B. Havell",
        "domain": "Temple Architecture",
    },
    {
        "id":     "historyofsanskri00macduoft",
        "title":  "History of Sanskrit Literature — Macdonell",
        "domain": "Linguistics",
    },
    {
        "id":     "hindumusicfromva00popu",
        "title":  "Hindu Music from Various Authors",
        "domain": "Classical Music",
    },
    {
        "id":     "hinducostumesand00ghosrich",
        "title":  "Hindu Costumes and Ornaments",
        "domain": "Textiles & Clothing",
    },
    {
        "id":     "vastuvidya00deva",
        "title":  "Vastu Vidya — Traditional Indian Architecture",
        "domain": "Temple Architecture",
    },
    {
        "id":     "industradecomme00unkngoog",
        "title":  "Industry and Trade in India",
        "domain": "Governance & Agriculture",
    },
]


def archive_best_text_url(item_id: str) -> Optional[tuple[str, str]]:
    """
    Query Archive.org metadata to find the best plain-text file.
    Returns (filename, download_url) or None.
    """
    try:
        r = SESSION.get(f"https://archive.org/metadata/{item_id}",
                        timeout=20)
        r.raise_for_status()
        files = r.json().get("files", [])

        candidates: list[tuple[int, str]] = []
        for f in files:
            name = f.get("name", "")
            if name.endswith("_djvu.txt"):
                candidates.append((0, name))
            elif name.endswith("_text.txt"):
                candidates.append((1, name))
            elif (name.endswith(".txt")
                  and "_meta" not in name
                  and "_files" not in name):
                candidates.append((2, name))

        if candidates:
            candidates.sort(key=lambda x: x[0])
            best = candidates[0][1]
            url  = f"https://archive.org/download/{item_id}/{best}"
            return best, url
    except Exception as e:
        err(f"  Metadata error {item_id}: {e}")
    return None


def archive_pdf_url(item_id: str) -> Optional[str]:
    try:
        r = SESSION.get(f"https://archive.org/metadata/{item_id}",
                        timeout=20)
        r.raise_for_status()
        for f in r.json().get("files", []):
            if f.get("name", "").endswith(".pdf"):
                return (f"https://archive.org/download/{item_id}/"
                        f"{f['name']}")
    except Exception:
        pass
    return None


def stream_download(url: str, out: Path, label: str) -> bool:
    try:
        r = SESSION.get(url, stream=True, timeout=120)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(out, "wb") as fh, tqdm(
            total=total, unit="B", unit_scale=True,
            desc=f"    {label[:40]}", leave=False
        ) as bar:
            for chunk in r.iter_content(65536):
                fh.write(chunk)
                bar.update(len(chunk))
        return True
    except Exception as e:
        err(f"  Download failed: {e}")
        return False


def pdf_to_text(pdf_path: Path) -> Optional[str]:
    try:
        import fitz
        doc  = fitz.open(str(pdf_path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text if len(text.split()) > 100 else None
    except ImportError:
        warn("  PyMuPDF not installed (pip install pymupdf);"
             " PDF saved but not extracted")
    except Exception as e:
        err(f"  PDF extraction error: {e}")
    return None


def collect_archive(test_mode: bool = False) -> int:
    head("ARCHIVE.ORG COLLECTION")
    items = ARCHIVE_ITEMS[:3] if test_mode else ARCHIVE_ITEMS
    collected = 0

    for item in tqdm(items, desc="Archive.org items"):
        item_id  = item["id"]
        domain   = item["domain"]
        title    = item["title"]
        fname    = safe_name(item_id)
        proc_path = PROC_DIR / f"archive_{fname}.txt"
        detail_url = f"https://archive.org/details/{item_id}"

        if already_done(proc_path):
            continue

        info(f"  {title}")

        # ── Step 1: plain-text file ───────────────────────────────────────────
        text_info = archive_best_text_url(item_id)
        if text_info:
            fname_txt, txt_url = text_info
            raw_path = ARCHIVE_DIR / f"{fname}_raw.txt"
            if stream_download(txt_url, raw_path, fname_txt):
                raw     = raw_path.read_text(encoding="utf-8", errors="ignore")
                cleaned = clean_text(raw)
                if len(cleaned.split()) > 200:
                    header = make_header("Archive.org", title,
                                         detail_url, domain)
                    proc_path.write_text(header + cleaned, encoding="utf-8")
                    wc = len(cleaned.split())
                    log_doc("archive.org", title, proc_path,
                            detail_url, wc, domain)
                    ok(f"  Text ({wc:,} words): {title}")
                    collected += 1
                    time.sleep(ARCH_DELAY)
                    continue

        # ── Step 2: PDF download + optional extraction ────────────────────────
        pdf_url = archive_pdf_url(item_id)
        if pdf_url:
            pdf_path = ARCHIVE_DIR / f"{fname}.pdf"
            if not pdf_path.exists():
                stream_download(pdf_url, pdf_path, fname + ".pdf")
            if pdf_path.exists():
                text = pdf_to_text(pdf_path)
                if text:
                    cleaned = clean_text(text)
                    header  = make_header("Archive.org (PDF)", title,
                                          detail_url, domain)
                    proc_path.write_text(header + cleaned, encoding="utf-8")
                    wc = len(cleaned.split())
                    log_doc("archive.org", title, proc_path,
                            detail_url, wc, domain)
                    ok(f"  PDF extracted ({wc:,} words): {title}")
                    collected += 1
                    time.sleep(ARCH_DELAY)
                    continue
                else:
                    ok(f"  PDF saved (extract manually): {pdf_path.name}")

        # ── Step 3: placeholder ───────────────────────────────────────────────
        placeholder = textwrap.dedent(f"""\
            SOURCE: Archive.org
            TITLE: {title}
            URL: {detail_url}
            DOMAIN: {domain}
            NOTE: Automatic download failed.
                  Visit {detail_url}
                  Download the .txt or .pdf and place in iks_corpus/processed/
            {'─' * 60}

            {title} — primary source for IKS domain: {domain}
        """)
        proc_path.write_text(placeholder, encoding="utf-8")
        log_doc("archive.org", title, proc_path, detail_url, 0, domain)
        warn(f"  Placeholder: {title}")
        collected += 1
        time.sleep(ARCH_DELAY)

    ok(f"Archive.org: {collected} items processed")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  3. NPTEL / SWAYAM
# ══════════════════════════════════════════════════════════════════════════════
#
#  Key fix from v1: NPTEL pages use React / JS, so direct scraping often
#  returns an empty shell.  We now:
#  - try scraping (works for some courses)
#  - embed rich course-description text directly for key courses
#  - write detailed placeholders with step-by-step manual instructions
#

NPTEL_SOURCES = [
    {
        "url":    "https://nptel.ac.in/courses/121106003",
        "title":  "NPTEL: Introduction to Indian Knowledge Systems",
        "domain": "IKS Overview",
        "embedded": """
Course: Introduction to Indian Knowledge Systems (IKS)
Instructor: Prof. Kapil Kapoor, JNU; Prof. Michel Danino, IIT Gandhinagar
Duration: 12 weeks, 3 hours per week

Week 1-2: Introduction and Overview of IKS
What is IKS? Definition, scope, and importance. The Vedic corpus — four Vedas
(Rigveda, Samaveda, Yajurveda, Atharvaveda), their structure and content.
Vedangas: Shiksha (phonetics), Kalpa (ritual), Vyakarana (grammar),
Nirukta (etymology), Jyotisha (astronomy), Chhandas (meter).

Week 3-4: Indian Philosophical Systems
Astika (Vedic) schools: Nyaya, Vaisheshika, Samkhya, Yoga, Mimamsa, Vedanta.
Nastika schools: Buddhism, Jainism, Charvaka.
Advaita Vedanta of Adi Shankaracharya. Dvaita Vedanta of Madhvacharya.
Vishishtadvaita of Ramanujacharya.

Week 5-6: Traditional Knowledge in Sciences
Mathematics: Sulba Sutras, Aryabhata (zero, decimal, algebra),
Brahmagupta (negative numbers, Brahmasphutasiddhanta),
Bhaskara II (Lilavati, Bijaganita), Madhava (infinite series, calculus precursor).
Astronomy: Aryabhatiya, Surya Siddhanta, Varahamihira's Panchasiddhantika.

Week 7-8: Traditional Knowledge in Humanities
Linguistics: Panini's Ashtadhyayi — 4000 sutras describing Sanskrit grammar,
considered the world's first formal grammar. Patanjali's Mahabhashya.
Art: Natya Shastra by Bharata Muni — encyclopaedia of performing arts.
Rasa theory (Navarasa). Classical dance forms.

Week 9-10: Traditional Knowledge in Professional Domains
Architecture: Vastu Shastra, Manasara, Mayamata. Temple architecture styles.
Medicine: Charaka Samhita, Sushruta Samhita. Tridosha theory. Panchakarma.
Governance: Arthashastra by Kautilya. Ashoka's Dhamma.
Agriculture: Traditional farming practices, water harvesting (stepwells).

Week 11-12: IKS and Sustainable Development Goals
Connections between ancient Indian sustainability practices and UN SDGs.
Protecting traditional knowledge. WIPO and intellectual property.
Revival and relevance of IKS in modern engineering and technology.
        """,
    },
    {
        "url":    "https://nptel.ac.in/courses/109104045",
        "title":  "NPTEL: Sanskrit for Self Development",
        "domain": "Linguistics",
        "embedded": """
Course: Sanskrit for Self Development
Instructor: Prof. Anuradha Choudry, IIT Kharagpur
Duration: 8 weeks

Sanskrit is an ancient Indo-Aryan language in which most Hindu scriptures are written.
It is the mother of many Indian languages including Hindi, Marathi, Bengali, Telugu.

Week 1: Introduction to Sanskrit alphabet (Devanagari script).
Vowels (svaras): a, aa, i, ii, u, uu, ri, e, ai, o, au, am, ah.
Consonants organized by place of articulation (varna-mala).

Week 2-3: Panini's grammar system. Ashtadhyayi — 8 chapters, 3976 sutras.
Dhatus (verbal roots), Vibhakti (cases), Sandhi (phonetic combination rules).
The most complete and systematic grammar of any language.

Week 4-5: Sanskrit in science and mathematics.
Mathematical terms: ankam (digit), shunya (zero), bindu (point).
Chandas (Vedic meter): Gayatri (24 syllables), Anushtup, Trishtup, Jagati.
Pingala's Chandahshastra — binary representations of meters.

Week 6-8: Sanskrit literature and its significance.
Vedas, Upanishads, Bhagavad Gita. Kalidasa's Meghaduta, Shakuntala.
Panini, Patanjali, Bhartrhari. Sanskrit computational linguistics.
Sanskrit's influence on European languages (Proto-Indo-European connection).
        """,
    },
    {
        "url":    "https://nptel.ac.in/courses/106102082",
        "title":  "NPTEL: History of Science in India",
        "domain": "Mathematics & Science",
        "embedded": "",
    },
    {
        "url":    "https://nptel.ac.in/courses/124109007",
        "title":  "NPTEL: Yoga and its Applications",
        "domain": "Medicine & Health",
        "embedded": "",
    },
    {
        "url":    "https://nptel.ac.in/courses/104107082",
        "title":  "NPTEL: Indian Architecture and Town Planning",
        "domain": "Temple Architecture",
        "embedded": "",
    },
]

SWAYAM_SOURCES = [
    {
        "url":    "https://onlinecourses.swayam2.ac.in/imb23_mg53/preview",
        "title":  "SWAYAM: IKS Concepts and Applications in Engineering",
        "domain": "IKS Overview",
        "embedded": """
Course: Indian Knowledge System: Concepts and Applications in Engineering
Platform: SWAYAM / NPTEL
Instructors: B. Mahadevan (IIM Bangalore), Vinayak Rajat Bhat
(Chanakya University), R. Venkata Raghavan (IIT Bhubaneswar)
Textbook: Introduction to Indian Knowledge System: Concepts and Applications,
PHI Learning, 2022.

Week 1: Introduction to IKS. What is IKS? The IKS corpus classification
framework (Chaturdasha-Vidyasthana). Unique aspects: oral tradition, sutras,
encryption, regenerative and spiritual dimensions.

Week 2: Vedic corpus. Four Vedas — Rigveda (hymns), Samaveda (melodies),
Yajurveda (rituals), Atharvaveda (spells/medicine). Six Vedangas.
Upanishads — philosophical treatises. Puranas — mythological encyclopedias.

Week 3: Mathematics in ancient India. Sulba Sutras (800-500 BCE) —
geometrical constructions for altars. Aryabhata (476–550 CE) —
place value system, approximation of pi, trigonometry.
Brahmagupta (598–668 CE) — rules for zero, negative numbers.
Bhaskara II (1114–1185 CE) — Lilavati, Bijaganita.
Madhava (1340–1425 CE) — infinite series for pi and trigonometric functions
(300 years before Gregory and Leibniz).

Week 4: Astronomy. Aryabhatiya — heliocentric theory (predating Copernicus),
rotation of Earth, eclipses. Surya Siddhanta — astronomical constants.
Jantar Mantar observatories (Jai Singh II, 18th century) in Jaipur, Delhi.

Week 5: Engineering and technology. Iron Pillar of Delhi (4th century CE) —
corrosion-resistant iron, unsolved metallurgical mystery. Wootz steel —
high-carbon crucible steel, traded globally. Shipbuilding — Arthashastra
describes ocean-going vessels. Water management — stepwells (vav),
tanks, irrigation canals.

Week 6: Architecture and town planning. Vastu Shastra — principles of
sacred space. Manasara and Mayamata — architectural treatises. Temple
architecture styles: Nagara (North), Dravidian (South), Vesara (mixed).
Mohenjo-daro and Harappa — grid planning, sewage systems, public baths.

Week 7: Linguistics. Panini's Ashtadhyayi — considered the world's first
formal grammar. 4000 sutras describe Sanskrit phonology, morphology, syntax.
Sanskrit's computational nature — modern AI/NLP researchers study it.

Week 8: Medicine. Ayurveda — Charaka Samhita (internal medicine),
Sushruta Samhita (surgery — 300+ surgical procedures, plastic surgery of nose).
Tridosha theory: Vata, Pitta, Kapha. Panchakarma — detoxification therapies.
Yoga — Patanjali's Yoga Sutras. Eight limbs (Ashtanga).

Week 9: Governance. Arthashastra by Kautilya (321 BCE) — statecraft,
economics, military strategy, diplomacy. Ashoka's 14 Rock Edicts.
Vijayanagara administrative system.

Week 10: IKS and SDGs. Connections between Indian knowledge and
Sustainable Development Goals: zero hunger (traditional agriculture),
good health (Ayurveda), clean water (stepwells), sustainable cities
(Vastu Shastra, Harappan planning), responsible consumption.
Protecting traditional knowledge through WIPO, patents, and documentation.
        """,
    },
]


def scrape_page(url: str) -> Optional[str]:
    try:
        r = SESSION.get(url, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["nav", "footer", "header", "script",
                         "style", "aside", "form", "button",
                         "iframe", "noscript"]):
            tag.decompose()
        for sel in ["main", "article", "#content", ".course-content",
                    ".description", "[role='main']", "body"]:
            node = soup.select_one(sel)
            if node:
                t = node.get_text(separator="\n")
                if len(t.split()) > 80:
                    return t
        return soup.get_text(separator="\n")
    except Exception:
        return None


def collect_nptel(test_mode: bool = False) -> int:
    head("NPTEL / SWAYAM COLLECTION")
    all_src = NPTEL_SOURCES + SWAYAM_SOURCES
    sources = all_src[:3] if test_mode else all_src
    collected = 0

    for src in tqdm(sources, desc="NPTEL/SWAYAM"):
        title    = src["title"]
        url      = src["url"]
        domain   = src["domain"]
        embedded = src.get("embedded", "").strip()
        fname    = safe_name(title)
        out_path = PROC_DIR / f"nptel_{fname}.txt"

        if already_done(out_path):
            continue

        info(f"  {title}")

        # Try live scraping first
        scraped = scrape_page(url)
        text    = ""

        if scraped and len(scraped.split()) > 80:
            text = scraped
            if embedded:
                text += "\n\n" + embedded
        elif embedded:
            text = embedded
        else:
            # Write placeholder with manual instructions
            placeholder = textwrap.dedent(f"""\
                SOURCE: NPTEL/SWAYAM
                TITLE: {title}
                URL: {url}
                DOMAIN: {domain}
                NOTE: Page uses JavaScript — scraping returned empty content.
                      To add lecture transcripts:
                      1. Visit {url}
                      2. Enroll (free)
                      3. Open any lecture → click "Transcript" tab
                      4. Copy text and append to this file
                {'─' * 60}

                Course: {title}  |  Domain: {domain}
                URL: {url}
            """)
            out_path.write_text(placeholder, encoding="utf-8")
            log_doc("nptel", title, out_path, url, 0, domain)
            warn(f"  Placeholder: {title}")
            collected += 1
            time.sleep(WEB_DELAY)
            continue

        cleaned = clean_text(text)
        header  = make_header("NPTEL/SWAYAM", title, url, domain)
        out_path.write_text(header + cleaned, encoding="utf-8")
        (NPTEL_DIR / f"{fname}.txt").write_text(
            header + cleaned, encoding="utf-8")
        wc = len(cleaned.split())
        log_doc("nptel", title, out_path, url, wc, domain)
        ok(f"  Saved ({wc:,} words): {title}")
        collected += 1
        time.sleep(WEB_DELAY)

    ok(f"NPTEL/SWAYAM: {collected} sources processed")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  4. SUPPLEMENTARY WEB SOURCES
# ══════════════════════════════════════════════════════════════════════════════

SUPPLEMENTARY_SOURCES = [
    {
        "url":    "https://www.ayush.gov.in/about-the-systems/ayurveda",
        "title":  "AYUSH Ministry — About Ayurveda",
        "domain": "Medicine & Health",
    },
    {
        "url":    "https://sangeetnatak.gov.in/sna/classical_dance.php",
        "title":  "Sangeet Natak Akademi — Classical Dance Forms",
        "domain": "Classical Dance",
    },
    {
        "url":    "https://sangeetnatak.gov.in/sna/classical_music.php",
        "title":  "Sangeet Natak Akademi — Classical Music",
        "domain": "Classical Music",
    },
    {
        "url":    "https://indiaculture.gov.in/classical-dance-forms",
        "title":  "Ministry of Culture — Classical Dance Forms",
        "domain": "Classical Dance",
    },
    {
        "url":    "https://www.india.gov.in/topics/art-culture/classical-dances",
        "title":  "India.gov.in — Classical Dances Overview",
        "domain": "Classical Dance",
    },
    {
        "url":    "https://asi.nic.in/monuments-alphabetically/",
        "title":  "ASI — Protected Monuments List",
        "domain": "Temple Architecture",
    },
    {
        "url":    "https://www.vedicmathsindia.org/applications/",
        "title":  "Vedic Mathematics — Applications and Sutras",
        "domain": "Mathematics",
    },
    {
        "url":    "https://www.ayush.gov.in/about-the-systems/yoga",
        "title":  "AYUSH Ministry — About Yoga",
        "domain": "Medicine & Health",
    },
]


def collect_supplementary(test_mode: bool = False) -> int:
    head("SUPPLEMENTARY WEB SOURCES")
    sources = SUPPLEMENTARY_SOURCES[:3] if test_mode else SUPPLEMENTARY_SOURCES
    collected = 0

    for src in tqdm(sources, desc="Web sources"):
        title  = src["title"]
        url    = src["url"]
        domain = src["domain"]
        fname  = safe_name(title)
        out_path = PROC_DIR / f"web_{fname}.txt"

        if already_done(out_path):
            continue

        info(f"  {title}")

        if url.endswith(".pdf"):
            pdf_path = SUPP_DIR / f"{fname}.pdf"
            if not pdf_path.exists():
                stream_download(url, pdf_path, fname + ".pdf")
            if pdf_path.exists():
                text = pdf_to_text(pdf_path)
                if text:
                    cleaned = clean_text(text)
                    header  = make_header("Web (PDF)", title, url, domain)
                    out_path.write_text(header + cleaned, encoding="utf-8")
                    wc = len(cleaned.split())
                    log_doc("web", title, out_path, url, wc, domain)
                    ok(f"  Saved ({wc:,} words): {title}")
                    collected += 1
                    time.sleep(WEB_DELAY)
                    continue
        else:
            text = scrape_page(url)
            if text and len(text.split()) > 80:
                cleaned = clean_text(text)
                header  = make_header("Web", title, url, domain)
                out_path.write_text(header + cleaned, encoding="utf-8")
                wc = len(cleaned.split())
                log_doc("web", title, out_path, url, wc, domain)
                ok(f"  Saved ({wc:,} words): {title}")
                collected += 1
                time.sleep(WEB_DELAY)
                continue

        warn(f"  Could not retrieve: {title}")
        time.sleep(WEB_DELAY)

    ok(f"Supplementary: {collected} sources collected")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_summary():
    head("COLLECTION SUMMARY")
    if not metadata:
        warn("No documents collected.")
        return

    total_words = sum(m["word_count"] for m in metadata)
    by_src:   dict[str, int] = {}
    by_dom:   dict[str, int] = {}
    src_words:dict[str, int] = {}

    for m in metadata:
        by_src[m["source"]]  = by_src.get(m["source"], 0) + 1
        by_dom[m["domain"]]  = by_dom.get(m["domain"], 0) + 1
        src_words[m["source"]] = src_words.get(m["source"], 0) + m["word_count"]

    print(f"\n  {'Total documents':<36} {len(metadata)}")
    print(f"  {'Total words':<36} {total_words:,}")

    print(f"\n  By source:")
    for src in sorted(by_src):
        print(f"    - {src:<28}  {by_src[src]:>3} docs  "
              f"{src_words.get(src,0):>8,} words")

    print(f"\n  By IKS domain (top 10 by doc count):")
    for dom, cnt in sorted(by_dom.items(), key=lambda x: -x[1])[:10]:
        print(f"    - {dom:<42}  {cnt} docs")

    proc_files = list(PROC_DIR.glob("*.txt"))
    print(f"\n  Processed files ready for LlamaIndex: {len(proc_files)}")
    print(f"  Directory → {PROC_DIR.resolve()}")

    print(f"""
  {Fore.GREEN}{Style.BRIGHT}Next steps:{Style.RESET_ALL}

  1. Install RAG dependencies:
     pip install llama-index llama-index-llms-ollama \\
                 llama-index-embeddings-huggingface \\
                 chromadb gradio

  2. Install Ollama + Gemma 3:
     https://ollama.com  →  ollama pull gemma3:12b

  3. Run the RAG chatbot:
     python iks_rag.py

  4. (Optional) Improve PDF extraction:
     pip install pymupdf
     python iks_data_collector.py --source archive
""")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Collect IKS corpus from Wikipedia, Archive.org, NPTEL"
    )
    parser.add_argument(
        "--source",
        choices=["wiki", "archive", "nptel", "supplementary", "all"],
        default="all",
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Smoke-test mode: 2–3 items per source",
    )
    args = parser.parse_args()

    print(f"""
{Fore.MAGENTA}{Style.BRIGHT}
  ╔═════════════════════════════════════════════════════╗
  ║        IKS Data Collector  v2.0                     ║
  ║        Indian Knowledge Systems RAG Corpus          ║
  ╚═════════════════════════════════════════════════════╝
{Style.RESET_ALL}
  Output  →  {BASE_DIR.resolve()}
  Mode    →  {"TEST (2–3 items per source)" if args.test else "FULL"}
  Source  →  {args.source}
""")

    total = 0
    if args.source in ("wiki",          "all"):
        total += collect_wikipedia(args.test)
    if args.source in ("archive",       "all"):
        total += collect_archive(args.test)
    if args.source in ("nptel",         "all"):
        total += collect_nptel(args.test)
    if args.source in ("supplementary", "all"):
        total += collect_supplementary(args.test)

    save_metadata()
    print_summary()
    print(f"  {Fore.GREEN}{Style.BRIGHT}Done! {total} documents collected."
          f"{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()

"""
IKS World Corpus Collector  v1.0
=================================
Expands the corpus beyond academic facts into living culture —
stories, feelings, festivals, mythology, ragas as emotion,
sacred geography, and the untranslatable words of India.

This is not a study tool corpus. This is a cultural universe.

Usage
-----
  python iks_world_collector.py                   # everything
  python iks_world_collector.py --domain ragas
  python iks_world_collector.py --domain festivals
  python iks_world_collector.py --domain mythology
  python iks_world_collector.py --domain regional
  python iks_world_collector.py --domain concepts
  python iks_world_collector.py --domain literature
  python iks_world_collector.py --domain sacred
  python iks_world_collector.py --test             # 2 items per domain

Output
------
  iks_corpus/world/          all new documents
  iks_corpus/processed/      merged with existing corpus (LlamaIndex-ready)
  iks_corpus/metadata.json   updated collection log
"""

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

# ── Directories ────────────────────────────────────────────────────────────────
BASE_DIR  = Path("iks_corpus")
WORLD_DIR = BASE_DIR / "world"
PROC_DIR  = BASE_DIR / "processed"
META_FILE = BASE_DIR / "metadata.json"

for _d in [WORLD_DIR, PROC_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── HTTP session ───────────────────────────────────────────────────────────────
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "IKS-World-Collector/1.0 "
        "(Indian cultural heritage research; contact: your-email@example.com)"
    ),
    "Accept": "application/json, text/plain, */*",
})

WIKI_API   = "https://en.wikipedia.org/w/api.php"
WIKI_DELAY = 0.5
WEB_DELAY  = 1.0

# ── Logging ────────────────────────────────────────────────────────────────────
def ok(m):   print(f"{Fore.GREEN}  ✓  {m}{Style.RESET_ALL}")
def info(m): print(f"{Fore.CYAN}  →  {m}{Style.RESET_ALL}")
def warn(m): print(f"{Fore.YELLOW}  !  {m}{Style.RESET_ALL}")
def err(m):  print(f"{Fore.RED}  ✗  {m}{Style.RESET_ALL}")
def head(m): print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'─'*60}\n  {m}\n{'─'*60}{Style.RESET_ALL}")

# ── Metadata ───────────────────────────────────────────────────────────────────
metadata: list[dict] = []

def log_doc(source, title, path, url, word_count, domain, rasa=""):
    metadata.append({
        "source": source, "title": title, "file": str(path),
        "url": url, "domain": domain, "rasa": rasa,
        "word_count": word_count, "collected": datetime.now().isoformat(),
    })

def save_metadata():
    existing = []
    if META_FILE.exists():
        try:
            existing = json.loads(META_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    all_meta = existing + metadata
    META_FILE.write_text(json.dumps(all_meta, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    info(f"Metadata updated → {len(all_meta)} total documents")

# ── Utilities ──────────────────────────────────────────────────────────────────
def clean(raw: str) -> str:
    raw = re.sub(r"={2,}[^=\n]+={2,}", "", raw)
    raw = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", raw)
    raw = re.sub(r"\{\{[^}]{0,200}\}\}", "", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"https?://\S+", "", raw)
    raw = re.sub(r"\[\d+\]", "", raw)
    raw = re.sub(r"[ \t]{2,}", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    lines = [l.strip() for l in raw.splitlines() if len(l.strip()) >= 20]
    return "\n".join(lines).strip()

def header(source, title, url, domain, rasa="") -> str:
    r = f"\nRASA: {rasa}" if rasa else ""
    return textwrap.dedent(f"""\
        SOURCE: {source}
        TITLE: {title}
        URL: {url}
        DOMAIN: {domain}{r}
        COLLECTED: {datetime.now().isoformat()}
        {'─'*60}

    """)

def slug(s: str) -> str:
    return re.sub(r"[^\w\s-]", "", s).strip().replace(" ", "_")[:80]

def done(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 300

def wiki_fetch(title: str) -> Optional[dict]:
    params = {
        "action": "query", "titles": title.replace("_", " "),
        "prop": "extracts|info", "explaintext": True,
        "exsectionformat": "plain", "inprop": "url",
        "redirects": 1, "format": "json",
    }
    try:
        r = SESSION.get(WIKI_API, params=params, timeout=20)
        r.raise_for_status()
        for pid, page in r.json().get("query", {}).get("pages", {}).items():
            if pid == "-1":
                return None
            return {
                "title":   page.get("title", title),
                "extract": page.get("extract", ""),
                "url":     page.get("fullurl",
                           f"https://en.wikipedia.org/wiki/{title}"),
            }
    except Exception as e:
        err(f"  Wiki error '{title}': {e}")
    return None

def scrape(url: str, timeout: int = 18) -> Optional[str]:
    try:
        r = SESSION.get(url, timeout=timeout, allow_redirects=True)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for t in soup(["nav","footer","header","script",
                       "style","aside","form","button","iframe"]):
            t.decompose()
        for sel in ["main","article","#content",".entry-content",
                    ".post-content","[role='main']","body"]:
            node = soup.select_one(sel)
            if node:
                text = node.get_text(separator="\n")
                if len(text.split()) > 80:
                    return text
    except Exception:
        pass
    return None

def save_doc(domain: str, title: str, url: str, text: str,
             source: str = "Wikipedia", rasa: str = "",
             prefix: str = "world") -> bool:
    p = PROC_DIR / f"{prefix}_{slug(title)}.txt"
    if done(p):
        return False
    cleaned = clean(text)
    if len(cleaned.split()) < 80:
        return False
    h = header(source, title, url, domain, rasa)
    p.write_text(h + cleaned, encoding="utf-8")
    (WORLD_DIR / f"{slug(title)}.txt").write_text(h + cleaned, encoding="utf-8")
    wc = len(cleaned.split())
    log_doc(source, title, p, url, wc, domain, rasa)
    ok(f"  {title}  ({wc:,} words)")
    return True

def from_wiki(title: str, domain: str, rasa: str = "",
              prefix: str = "world") -> bool:
    p = PROC_DIR / f"{prefix}_{slug(title)}.txt"
    if done(p):
        return False
    result = wiki_fetch(title)
    if not result or len(result["extract"].split()) < 120:
        warn(f"  Skipped (thin/missing): {title}")
        time.sleep(WIKI_DELAY)
        return False
    saved = save_doc(domain, result["title"], result["url"],
                     result["extract"], "Wikipedia", rasa, prefix)
    time.sleep(WIKI_DELAY)
    return saved

def from_embedded(title: str, domain: str, content: str,
                  url: str = "", rasa: str = "",
                  prefix: str = "world") -> bool:
    p = PROC_DIR / f"{prefix}_{slug(title)}.txt"
    if done(p):
        return False
    return save_doc(domain, title, url or f"iks://embedded/{slug(title)}",
                    content, "Curated", rasa, prefix)


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 1 — RAGAS AS EMOTION
#  Not music theory. What each raga FEELS like, what time it belongs to,
#  what it evokes in the body. The emotional atlas of Indian music.
# ══════════════════════════════════════════════════════════════════════════════

RAGA_PROFILES = [
    {
        "name": "Raga Bhairavi",
        "time": "Dawn / end of concert",
        "season": "All seasons",
        "rasa": "Karuna (compassion, longing, the ache of parting)",
        "mood": "bittersweet, tender, the feeling of something beautiful ending",
        "wiki": "Bhairavi",
        "story": """
Bhairavi is always played last at a classical concert — not because of a rule,
but because nothing can follow it. It is the raga of leave-taking. The audience
knows when the musician begins Bhairavi that the evening is over, and that
knowledge itself becomes part of the music.

It uses all twelve notes — every shade the human voice can reach — as if trying
to say everything before departure. Pandit Bhimsen Joshi could reduce an entire
concert hall to silence with Bhairavi's opening phrase alone. Thumri singers have
called it the raga of the longing wife, the devotee who knows she is separated
from the divine.

The name comes from Bhairavi — a fierce form of Goddess Parvati — yet the raga
itself is soft as morning mist. This paradox is at the heart of it: the fiercest
love is also the most vulnerable.

When a Carnatic musician plays Bhairavi (called Sindhu Bhairavi in the South)
before sunrise, the darkness outside the window feels like it is listening.
        """,
    },
    {
        "name": "Raga Yaman",
        "time": "First quarter of night — dusk to 9pm",
        "season": "All seasons",
        "rasa": "Shringara (love, longing, romantic yearning)",
        "mood": "romantic, expansive, the feeling of possibility opening at dusk",
        "wiki": "Yaman",
        "story": """
Yaman is the raga of the first hour of night — the moment the sky turns purple,
the lamps are lit, and the day's noise settles into something quieter and more
alive. It is the raga of longing that is not yet painful — still sweet with hope.

The raised fourth note (teevra madhyam) gives Yaman its distinctive lift, like
a question asked with a smile. Hindustani musicians treat it as the foundation
raga — the first a serious student learns — because its architecture is so
elegant, so balanced, that it teaches the grammar of all ragas.

In old Delhi's houses, the evening would begin with someone playing Yaman on
the sarod or sitar while the household prepared for dinner. The raga didn't
demand attention — it filled the room like incense, present but not intrusive.

Ustad Vilayat Khan's recordings of Yaman are considered among the most
beautiful objects Indian civilization has produced. They carry a quality of
space — of doors and windows open on a warm evening — that cannot be described,
only heard.
        """,
    },
    {
        "name": "Raga Darbari Kanada",
        "time": "Deep midnight — after 12am",
        "season": "All seasons",
        "rasa": "Vira and Shanta (heroism meeting deep peace — the stillness of kings)",
        "mood": "majestic, solemn, the silence of a palace at midnight",
        "wiki": "Darbari_Kanada",
        "story": """
Darbari Kanada was created — or revealed, as musicians prefer to say — by
Miyan Tansen, the legendary court musician of Emperor Akbar. The story goes
that Tansen played it once at midnight in the emperor's court and the entire
durbar fell silent not from politeness but from awe. Akbar was seen with tears
on his face.

The raga moves slowly, with long, heavy pauses between phrases. The komal
(flattened) gandhar note droops like a weight, giving Darbari its distinctive
gravity. Vocalists will spend thirty minutes on the alap — the slow, wordless
exploration — before introducing rhythm. In that thirty minutes, the entire
architecture of the raga is revealed phrase by phrase, like a vast room being
gradually lit.

To hear Ustad Amir Khan or Pandit Kumar Gandharva perform Darbari live was
described by listeners as "being pressed gently to the floor by something
enormous and kind." It does not inspire emotion — it *is* an emotion, one that
has no name in English: the profound stillness at the center of immense power.
        """,
    },
    {
        "name": "Raga Todi",
        "time": "Late morning — 8am to noon",
        "season": "Winter and spring",
        "rasa": "Karuna and Shringara (tender grief, a kite whose string has snapped)",
        "mood": "melancholic, delicate, introspective, a beautiful sadness",
        "wiki": "Todi_(music)",
        "story": """
Todi is the raga of beautiful sadness — not the sharp grief of loss, but the
softer ache of incompleteness. Musicians describe it as the feeling of a kite
that has lost its string — still airborne, still beautiful, but no longer tethered
to anyone below.

It is a difficult raga to perform. The four flattened notes (komal re, ga, dha
and teevra ma) require a controlled fragility — the voice or instrument must stay
at the edge of breaking without breaking. A slight excess in any direction and
the delicacy is lost.

The traditional imagery for Todi is a young woman standing by a forest pool at
mid-morning, playing a veena, surrounded by deer who have come to listen. The
scene is one of perfect, temporary peace — already tinged with the knowledge
that it will end.

In Carnatic music, Todi is considered one of the three most important ragas,
alongside Bhairavi and Kalyani (Yaman). Musicians spend years in its company.
The great vocalist M.S. Subbulakshmi's recordings of Todi songs remain
benchmarks of emotional precision in Indian music.
        """,
    },
    {
        "name": "Raga Bhimpalasi",
        "time": "Afternoon — 3pm to 6pm",
        "season": "All seasons",
        "rasa": "Shringara with a quality of Karuna — affectionate longing",
        "mood": "drowsy, warm, intimate — the feeling of a summer afternoon",
        "wiki": "Bhimpalasi",
        "story": """
Bhimpalasi is the raga of the golden afternoon — that specific hour when the
heat has peaked and begun its retreat, when the mind drifts without effort.
Hindustani musicians call it a raga of madhura (sweetness) and viraha (longing
for the beloved).

The komal gandhar and komal nishad give Bhimpalasi a softness that feels like
half-sleep — conscious but not quite alert, the mind opening to images without
forcing them. Many musicians say this raga arrives unbidden on warm afternoons;
they find themselves humming it without deciding to.

The traditional context is a woman in a courtyard during the afternoon pause,
thinking of someone absent. Not with pain — just with awareness of their
absence, as you might be aware of a cloud's shadow. The raga holds both the
warmth of presence-in-memory and the coolness of the missing.

Pandit Hariprasad Chaurasia's flute performances of Bhimpalasi are considered
its defining recordings. The flute's breath quality suits this raga perfectly —
something between a sigh and a song.
        """,
    },
    {
        "name": "Raga Bageshri",
        "time": "Second quarter of night — 9pm to midnight",
        "season": "Monsoon",
        "rasa": "Shringara — the longing of lovers separated by rain",
        "mood": "romantic, yearning, the sound of rain on a tin roof at night",
        "wiki": "Bageshri",
        "story": """
Bageshri is inseparable from rain. It is the raga played when the monsoon breaks
over the plains of North India, when the smell of wet earth — petrichor — enters
every home through open windows. Musicians in the old tradition would wait for
the monsoon to perform Bageshri; to play it in summer felt dishonest.

The raga carries the specific emotion of virah — separation — in its most
romantic form. The beloved is far away. Rain is falling. The night smells of
earth and jasmine. This is Bageshri's world.

Thumri singers — the masters of romantic classical music — consider Bageshri
their home. It is a forgiving raga, allowing ornament and improvisation with
unusual freedom. A skilled vocalist can spend hours in Bageshri and never
exhaust its emotional range.

The Kathak dance tradition associates specific movements with Bageshri — the
gesture of looking toward a door that won't open, of writing a letter that
will not be sent. When rain-scented air and Bageshri arrive together, Indians
who have grown up with classical music describe a specific visceral joy:
the pleasure of being exactly where you are supposed to be.
        """,
    },
    {
        "name": "Raga Malkauns",
        "time": "Deep midnight — after midnight",
        "season": "Winter",
        "rasa": "Bhayanaka and Vira — the awesome and the heroic, power in darkness",
        "mood": "dark, vast, still — the silence at the center of power",
        "wiki": "Malkauns",
        "story": """
Malkauns is played after midnight in the deepest part of night, and it sounds
like it belongs there. It uses only five notes and none of them are the natural
fifth — that note of resolution and comfort most ragas rely on. Without that
anchor, Malkauns floats in a space that feels both groundless and completely
stable, like standing in the center of a very large room in total darkness.

The raga is associated with Shiva — particularly Shiva in his aspect as
Mahakala, lord of time and destruction. Not a fearful destruction but the
necessary one: the burning that makes renewal possible. Musicians say performing
Malkauns well requires a quality of inner stillness that takes years to develop.
The raga does not reward hurry.

Ustad Amir Khan's recordings of Malkauns are considered among the monuments of
Indian music. His voice moved through the raga with an absolute absence of
decoration — no unnecessary ornament, no show of technique. Just the five notes,
sustained in complete darkness, containing everything.

To hear Malkauns performed live at 2am is one of the experiences that makes
people understand why Indian classical music is called a spiritual practice and
not an entertainment.
        """,
    },
    {
        "name": "Raga Kafi",
        "time": "Second quarter of night — Holi season",
        "season": "Spring — especially Holi",
        "rasa": "Shringara and Hasya — love and joy, devotion through celebration",
        "mood": "festive, devotional, earthy, the sound of colour being thrown",
        "wiki": "Kafi",
        "story": """
Kafi is the raga of Holi — the festival of colour — and it carries within it
every feeling that festival contains: abandon, devotion, the dissolution of
social boundaries, and the specific joy of spring after a long winter.

In the devotional tradition, Kafi is the raga of Krishna — particularly of his
playful, mischievous aspect. The dhrupad and khayal compositions in Kafi almost
always describe the Holi festivities in Vrindavan: Krishna throwing color,
the gopis (cowherd girls) chasing him, the entire village dissolved in laughter
and colour.

The flattened third and seventh notes give Kafi a quality of relaxed warmth —
not the formal grandeur of Darbari or the delicate tension of Todi, but
something closer to bare feet on warm earth. Folk music throughout North India
draws from Kafi's scale, which is why hearing it feels both ancient and familiar.

Kabir's famous dohas (couplets) are often sung in Kafi — his earthy, direct
spiritual wisdom finds its perfect musical home in a raga that is itself earthy
and direct. The great singer Kumar Gandharva's recordings of Kabir in Kafi
remain among the most beloved recordings in Indian musical memory.
        """,
    },
    {
        "name": "Raga Marwa",
        "time": "Dusk — the transitional moment of day into night",
        "season": "Summer",
        "rasa": "Bhayanaka with Karuna — the anxiety of transition, beautiful unease",
        "mood": "unsettled, searching, the discomfort of a day ending without resolution",
        "wiki": "Marwa_(raga)",
        "story": """
Marwa is played at the precise moment when day ends and night has not yet
begun — that brief, unsettled time when the light has gone and the stars are
not yet visible, and the world is neither one thing nor another.

It is one of the few ragas that avoids the note of completeness (the perfect
fourth, shadja's complement). This absence creates a quality of unresolved
searching — as if the raga is looking for something it knows exists but cannot
quite reach. Musicians who love Marwa say this is exactly its truth: the sunset
is beautiful precisely because it cannot be held.

Marwa is notoriously difficult to perform well. Its emotional territory is
narrow and precise. Played even slightly wrong, it sounds merely odd. Played
right, it captures something most music doesn't attempt: the specific unease
of beauty that is passing. The colour of light at 6:02pm in summer. The moment
between one breath and the next.

Ustad Vilayat Khan's sitar in Marwa and the vocalist Pandit Jasraj's Marwa
recordings approach this rasa from two directions — one cool and architectural,
one warm and searching — and both arrive at the same place: the feeling that
everything beautiful is always just leaving.
        """,
    },
    {
        "name": "Raga Bhairav",
        "time": "Dawn — sunrise",
        "season": "All seasons",
        "rasa": "Shanta and Karuna — deep peace, the serenity of first light",
        "mood": "devotional, serene, the moment before the world wakes",
        "wiki": "Bhairav",
        "story": """
Bhairav is the raga of the last watch of night and first light of morning — the
hour between 4am and 6am when darkness and dawn negotiate, when the birds
begin before the sun arrives. It is named for Bhairav, a terrifying form of
Shiva, yet the raga itself is among the most serene in Indian music.

This paradox reveals something essential about Indian aesthetics: the terrible
and the peaceful are not opposites. Shiva in his Bhairav form is terrifying
because he is completely awake, completely present. Dawn has that quality — a
silence so total it feels almost threatening before it resolves into beauty.

The flattened second and sixth notes give Bhairav a quality of restraint — of
feeling held back at the verge of breaking, finding stability in that verge.
Temple priests in Varanasi perform Bhairav during the morning aarti as the
Ganga appears out of the mist. The combination of the raga, the river, and the
first light is described by those who have experienced it as one of the most
powerful aesthetic experiences available to a human being.

Pandit Ravi Shankar's Bhairav recordings carry this quality — the sitar sounds
like it is very gently pressing against a door of light that is about to open.
        """,
    },
]

RAGA_WIKI_EXTRAS = [
    ("Raag_Kedar", "Classical Music", "Shringara"),
    ("Raga_Kirwani", "Classical Music", "Karuna"),
    ("Raag_Jaunpuri", "Classical Music", "Karuna"),
    ("Yaman_Kalyan", "Classical Music", "Shringara"),
    ("Raag_Bairagi", "Classical Music", "Shanta"),
    ("Raga_Pooriya_Dhanashri", "Classical Music", "Shringara"),
    ("Melakarta", "Classical Music", ""),
    ("Carnatic_music_ragam_list", "Classical Music", ""),
    ("Hindustani_classical_music", "Classical Music", ""),
    ("Gharana", "Classical Music", ""),
]


def collect_ragas(test_mode: bool = False) -> int:
    head("RAGAS AS EMOTION")
    collected = 0
    profiles = RAGA_PROFILES[:2] if test_mode else RAGA_PROFILES

    for raga in tqdm(profiles, desc="Raga profiles"):
        title   = raga["name"]
        p       = PROC_DIR / f"raga_{slug(title)}.txt"
        if done(p):
            continue

        # Build a rich document combining curated narrative + wiki extract
        wiki_text = ""
        w = wiki_fetch(raga["wiki"])
        if w:
            wiki_text = f"\n\n--- Wikipedia excerpt ---\n{w['extract'][:3000]}"

        full_text = textwrap.dedent(f"""\
            Raga: {title}
            Time of day: {raga['time']}
            Season: {raga['season']}
            Primary rasa (emotion): {raga['rasa']}
            Mood quality: {raga['mood']}

            {raga['story'].strip()}
            {wiki_text}
        """)

        save_doc(
            domain   = "Classical Music — Raga as Emotion",
            title    = title,
            url      = f"https://en.wikipedia.org/wiki/{raga['wiki']}",
            text     = full_text,
            source   = "Curated + Wikipedia",
            rasa     = raga["rasa"],
            prefix   = "raga",
        )
        collected += 1
        time.sleep(WIKI_DELAY)

    extras = RAGA_WIKI_EXTRAS[:2] if test_mode else RAGA_WIKI_EXTRAS
    for wiki_title, domain, rasa in tqdm(extras, desc="Raga Wikipedia extras"):
        if from_wiki(wiki_title, domain, rasa, "raga"):
            collected += 1

    ok(f"Ragas: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 2 — FESTIVALS AS LIVED EXPERIENCE
#  Not dates and facts. What they smell like. What they sound like.
#  The human meaning underneath the ritual.
# ══════════════════════════════════════════════════════════════════════════════

FESTIVAL_PROFILES = [
    {
        "name": "Diwali — the festival of light",
        "region": "Pan-India (especially North, West, East India)",
        "rasa": "Adbhuta and Shringara — wonder, beauty, the triumph of light",
        "wiki": "Diwali",
        "story": """
Two weeks before Diwali, the preparation begins. In every Indian home,
grandmothers start making sweets — ladoo, chakli, murukku, barfi — and the
smell of clarified butter and cardamom fills the house. Children are given the
task of making rangoli in front of the door: intricate geometric patterns in
coloured powder, flowers, and rice flour. These will be swept away by morning
but that's the point. Beauty offered freely, without insistence on permanence.

On the night itself, every surface that can hold a flame holds one. Clay diyas —
small earthen lamps — burn with mustard oil. Not electric lights, not candles:
the specific warm yellow of a small flame in clay. Streets that are dark all
year are completely lit. From a roof, the city looks like the sky has been
inverted — stars below, darkness above.

The philosophical story is Ram's return to Ayodhya — the rightful king coming
home after fourteen years of exile, the people of the city lighting his way.
But the deeper story is older than Ram: the idea that darkness is temporary,
that light is the fundamental nature of things, and that a small flame — even
a single clay lamp — is a declaration of this truth.

In Varanasi, Diwali ends with the entire ghats lit simultaneously, and the
Ganga reflects the thousand lights. This is considered by people who have seen
it as one of the most beautiful sights available to a human eye.

In Kolkata, the same night is Kali Puja — the worship of the dark goddess — and
the aesthetic is entirely different: fierce, powerful, the beauty of darkness
itself honored rather than overcome. India holds both without contradiction.
        """,
    },
    {
        "name": "Holi — the festival of colour",
        "region": "Pan-India, especially North India and Vrindavan",
        "rasa": "Hasya and Shringara — pure joy, the dissolution of self",
        "wiki": "Holi",
        "story": """
Holi begins the night before with Holika Dahan — a bonfire representing the
burning of the demoness Holika, the victory of devotion over evil. Families
circle the fire, the older women performing prayers. Then the night loosens into
music and colour and the rules that govern ordinary life are suspended.

The next morning, colour. Gulal — dry colour powder, originally made from
flowers and herbs — is thrown, smeared on faces, dissolved in water and sprayed
from pumps. The important thing is that the colour makes everyone equal: the
boss and the employee, the neighbour who owes you money, the old couple who
never speak — everyone becomes the same bright mess, laughing.

In Vrindavan and Mathura — the home of Krishna — Holi lasts a week and reaches
an intensity that overwhelms visitors. The air is so thick with colour that
you cannot see more than a few meters. The sound is a continuous roar of
music, drums, screaming, and laughter. People described as "serious" people
find themselves weeping with joy and not knowing why.

The mythological heart is Krishna and the gopis — his playful colour fights
with the women of Vrindavan, their chasing him, the entire village dissolved
in affectionate chaos. But the lived heart is simpler: for one day, the weight
of who you are is lifted. You are just a person covered in colour, and colour
is beautiful, and you are therefore beautiful.
        """,
    },
    {
        "name": "Pongal — the harvest festival of Tamil Nadu",
        "region": "Tamil Nadu and Sri Lanka, Tamil communities worldwide",
        "rasa": "Shanta and Hasya — gratitude, abundance, the peace of harvest",
        "wiki": "Pongal_(festival)",
        "story": """
Pongal is four days long and each day has a different offering. The first is
Bhogi — clearing the old. Old furniture, worn clothes, anything no longer needed
is burned in bonfires at dawn. The smoke of Bhogi marks Tamil Nadu from space.

The second day is Pongal proper — the cooking of the sacred rice. A clay pot is
placed outdoors, rice and milk and fresh turmeric and jaggery are added, and
the family watches as it boils. The moment the milk rises and overflows the pot —
when it literally "pongals" (boils over) — the family cheers: "Pongalo Pongal!"
This overflow is the blessing — abundance that cannot be contained.

The third day is Mattu Pongal — the cattle festival. Cows and bulls are bathed,
their horns painted, they are garlanded with flowers, and the whole village
comes to honor them. In a culture that has lived by the land for ten thousand
years, the animals that make the harvest possible deserve one day of celebration.

Pongal is the festival that makes Tamils living abroad feel the deepest
homesickness — the specific smell of wet sugarcane crushed at the festival,
the sound of kolam patterns being drawn at dawn, the taste of newly harvested
rice cooked in a new clay pot. These sensory details carry an entire world.
        """,
    },
    {
        "name": "Durga Puja — Bengal's greatest festival",
        "region": "West Bengal, Bangladesh, the Bengali diaspora worldwide",
        "rasa": "Adbhuta and Vira — awe at the goddess, celebration of power",
        "wiki": "Durga_Puja",
        "story": """
For ten days in autumn, Kolkata becomes a different city. The Durga Puja
celebration in Bengal is not primarily a religious event — or rather, it is a
religious event that has been transformed by five hundred years of art,
competition, community, and sheer Bengali creative energy into something that
must be experienced to be understood.

Months before the festival, artists begin building the pandals — temporary
structures, some the size of aircraft hangars, constructed from bamboo, cloth,
and whatever else the theme demands. Each neighbourhood competes to create the
most spectacular, the most creative, the most unexpected. Recent pandals have
been built to look like temples of various Indian traditions, like the inside
of a forest, like the ruins of a civilization. UNESCO has recognized Durga Puja
as an Intangible Cultural Heritage of Humanity.

At the center of every pandal is Durga herself — a ten-armed goddess standing
on a lion, triumphing over the buffalo demon Mahishasura. But the idol's face
is modeled on the goddess's human aspect: a daughter coming home to her parents.
She arrives with her children — Lakshmi, Saraswati, Ganesh, Kartik — and in the
Bengali tradition, the grief of her departure at Dashami (the tenth day) is real
grief. Women weep as the idols are carried to the Ganga for immersion.

The five days of Puja are organized around food and art and nighttime wandering
from pandal to pandal. By 2am, the streets of Kolkata are still full of families
and the entire city smells of dhuno (incense) and flowers.
        """,
    },
    {
        "name": "Onam — Kerala's harvest home",
        "region": "Kerala",
        "rasa": "Shanta and Shringara — the serene beauty of abundance, homecoming",
        "wiki": "Onam",
        "story": """
Onam celebrates the annual return of the mythological King Mahabali — a just
and beloved king who was forced underground by Vamana (Vishnu's dwarf avatar)
but given the boon of returning once a year to see his beloved people thriving.

For ten days, Kerala prepares for his visit. The pookalam — a flower carpet
laid outside every home — is the most visible preparation. Each morning, fresh
flowers are added to the previous day's pattern, and by the final day it has
grown to cover the entire front yard. The competition in every neighbourhood
for the most beautiful pookalam brings children home from school at dawn.

The Onasadya — the feast on Thiruvonam day — is considered the greatest single
meal in Indian cuisine. Twenty-six dishes are served on a banana leaf, in a
specific order and arrangement that has been codified for centuries. From the
thick bitter olan (pumpkin in coconut milk) to the sweet golden payasam, the
meal moves through textures and flavours like a carefully composed piece of
music. To eat it properly, with your fingers, seated on the floor, the banana
leaf in front of you, is to understand that eating can be a spiritual act.

In the backwaters and rivers of Kerala, the Vallam Kali (snake boat race) turns
the water into something mythological. A hundred oarsmen in a single boat rowing
in perfect unison to the beat of Vanchipattu (boat songs) produces a sound and
sight that has been described as one of the most powerful human spectacles.
        """,
    },
    {
        "name": "Kumbh Mela — the world's largest human gathering",
        "region": "Prayagraj, Haridwar, Nashik, Ujjain — four sacred rivers",
        "rasa": "Bhayanaka and Shanta — awe at scale, the peace of immense belonging",
        "wiki": "Kumbh_Mela",
        "story": """
Kumbh Mela is the largest peaceful gathering of human beings in the history
of the world. At the Prayagraj Maha Kumbh, fifty to a hundred million people
arrive over forty-five days. The event is visible from space — not from light
but from the sheer density of human presence.

The occasion is an astronomical one: a specific alignment of Jupiter, the Sun,
and the Moon that recreates the moment when the divine physicians, in the
creation myth, won the jar (kumbha) of immortal nectar and drops of it fell
at these four river confluences. A bath in the river at the right moment —
the Shahi Snan — is believed to burn karma accumulated over lifetimes.

But Kumbh is more than the bath. It is a city that appears and disappears —
entire tent cities with hospitals, post offices, and markets spring up for the
duration and are gone within weeks. Sadhus from traditions that normally have
no contact with each other gather here: the ash-smeared Naga sadhus who carry
tridents, the saffron-robed Vaishnavas, the Aghoris with their deliberately
transgressive practices, monks who have been in silence for years.

For ordinary pilgrims, Kumbh is the experience of belonging to something so
much larger than yourself that individual identity temporarily dissolves. In
that crowd of millions, no one is anything except a pilgrim headed toward the
river. The social hierarchies that govern Indian life become, for a moment,
irrelevant. This is the experience the mythology promises: a drop of immortality.
        """,
    },
]

FESTIVAL_WIKI_EXTRAS = [
    ("Navratri", "Festivals", "Vira"),
    ("Janmashtami", "Festivals", "Shringara"),
    ("Ganesh_Chaturthi", "Festivals", "Hasya"),
    ("Baisakhi", "Festivals", "Hasya"),
    ("Eid_in_India", "Festivals", "Shanta"),
    ("Christmas_in_India", "Festivals", "Shanta"),
    ("Ugadi", "Festivals", "Adbhuta"),
    ("Bihu", "Festivals", "Hasya"),
    ("Puthandu", "Festivals", "Shanta"),
    ("Losar", "Festivals", "Adbhuta"),
]


def collect_festivals(test_mode: bool = False) -> int:
    head("FESTIVALS AS LIVED EXPERIENCE")
    collected = 0
    profiles = FESTIVAL_PROFILES[:2] if test_mode else FESTIVAL_PROFILES

    for fest in tqdm(profiles, desc="Festival profiles"):
        wiki_text = ""
        w = wiki_fetch(fest["wiki"])
        if w:
            wiki_text = f"\n\n--- Wikipedia background ---\n{w['extract'][:2500]}"

        full = textwrap.dedent(f"""\
            Festival: {fest['name']}
            Region: {fest['region']}
            Emotional essence (rasa): {fest['rasa']}

            {fest['story'].strip()}
            {wiki_text}
        """)
        if from_embedded(fest["name"], "Festivals — Lived Experience",
                         full, f"https://en.wikipedia.org/wiki/{fest['wiki']}",
                         fest["rasa"], "festival"):
            collected += 1
        time.sleep(WIKI_DELAY)

    extras = FESTIVAL_WIKI_EXTRAS[:2] if test_mode else FESTIVAL_WIKI_EXTRAS
    for wiki_title, domain, rasa in tqdm(extras, desc="Festival Wikipedia"):
        if from_wiki(wiki_title, domain, rasa, "festival"):
            collected += 1

    ok(f"Festivals: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 3 — MYTHOLOGY AS LIVING WISDOM
#  Not summaries. The emotional and philosophical truth in each story.
# ══════════════════════════════════════════════════════════════════════════════

MYTHOLOGY_WIKI = [
    ("Ramayana",             "Mythology", "Vira"),
    ("Mahabharata",          "Mythology", "Karuna"),
    ("Bhagavad_Gita",        "Mythology", "Shanta"),
    ("Panchatantra",         "Mythology", "Hasya"),
    ("Jataka_tales",         "Mythology", "Karuna"),
    ("Puranas",              "Mythology", "Adbhuta"),
    ("Vishnu_Purana",        "Mythology", "Shanta"),
    ("Shiva_Purana",         "Mythology", "Bhayanaka"),
    ("Devi_Mahatmya",        "Mythology", "Vira"),
    ("Shakuntala_(play)",    "Mythology", "Shringara"),
    ("Meghaduta",            "Mythology", "Karuna"),
    ("Kalidasa",             "Mythology", "Shringara"),
    ("Thirukkural",          "Mythology", "Shanta"),
    ("Sangam_literature",    "Mythology", "Shringara"),
    ("Kabir",                "Mythology", "Shanta"),
    ("Mirabai",              "Mythology", "Shringara"),
    ("Tukaram",              "Mythology", "Karuna"),
    ("Andal",                "Mythology", "Shringara"),
    ("Basavanna",            "Mythology", "Shanta"),
    ("Ravidas",              "Mythology", "Shanta"),
    ("Adi_Shankara",         "Philosophy", "Shanta"),
    ("Ramanujacharya",       "Philosophy", "Shringara"),
    ("Narada_Bhakti_Sutras", "Philosophy", "Shringara"),
    ("Yoga_Sutras_of_Patanjali", "Philosophy", "Shanta"),
    ("Arthashastra",         "Governance", "Vira"),
    ("Thiruvalluvar",        "Philosophy", "Shanta"),
]

MYTHOLOGY_EMBEDDED = [
    {
        "title": "The Mahabharata — every human dilemma",
        "domain": "Mythology",
        "rasa": "Karuna",
        "content": """
The Mahabharata is the longest poem ever written — ten times the length of the
Iliad and Odyssey combined. But its length is not its greatness. Its greatness
is that it contains every moral dilemma a human being can face, and it refuses
to resolve them cleanly.

The central question is: what do you do when your duty (dharma) requires you
to harm people you love? Arjuna, the greatest archer in the world, stands between
two armies on the battlefield of Kurukshetra. On one side: his cousins, teachers,
friends. On the other: his brothers and their claim to a kingdom stolen from them.
He puts down his bow. He cannot fight.

This is the moment Krishna begins the Bhagavad Gita.

But the Mahabharata's genius is that it shows the cost of every choice. Those
who win the war are destroyed by winning it. The five Pandava brothers, triumphant,
find the victory empty — their friends are dead, their family is dead, the land
they fought for is a graveyard. Yudhishthira, the eldest, the most dharmic, who
never told a lie in his life except once — that one lie haunts him to the end.

The character of Karna is the Mahabharata's broken heart. Born the oldest son
of Kunti (mother of the Pandavas), raised by a charioteer, loyal to the wrong
side out of gratitude and friendship. He knows, by the end, everything: who he
is, who he could have been, what he chose. And he chooses to die in the only
way available to him — with integrity.

Indian civilization has returned to the Mahabharata for three thousand years
because every generation finds its own dilemma reflected there. It doesn't
offer answers. It offers company in the difficulty of being human.
        """,
    },
    {
        "title": "The Ramayana — dharma in action",
        "domain": "Mythology",
        "rasa": "Vira and Karuna",
        "content": """
The Ramayana is older than the Mahabharata and simpler in a way — its moral
architecture is cleaner, its heroes more unambiguously heroic, its villain
more genuinely villainous. And yet it has generated more art, more music, more
poetry, more dance, more regional variation than any other story in Indian culture.

There are hundreds of versions of the Ramayana across Asia. The Tamil Kamba
Ramayana, the Bengali Krittivasi Ramayana, Tulsidas's Ramcharitmanas in Awadhi
(perhaps the most widely read book in South Asia), the Burmese Yama Zatdaw,
the Thai Ramakien, the Indonesian Kakawin Ramayana — each culture has made
Ram's story its own.

What survives all the versions is the idea of Ram: a king who upholds dharma even
at personal cost. Who accepts fourteen years of forest exile without bitterness.
Who weeps for his enemies. Who, when he must make a choice between his love for
Sita and his duty to his kingdom, makes the choice that breaks his heart.

The most-loved part of the Ramayana is arguably not the battle — it's the search.
Sita kidnapped, Ram inconsolable, and then the meeting with Hanuman: the monkey
general who becomes not a servant but a devotee, who can cross oceans for love,
who carries Ram's ring into Lanka as proof. The relationship between Ram and
Hanuman is the Ramayana's deepest vein — what pure, selfless devotion looks like
between two beings who are genuinely free.

In Indian homes, Ram is not mythological. He is a member of the family. "Jai
Shri Ram" is what people say when they pick something heavy. His name is what
people say at the moment of death. His story is what children hear before sleep.
        """,
    },
    {
        "title": "Panchatantra — wisdom through animals",
        "domain": "Mythology",
        "rasa": "Hasya and Shanta",
        "content": """
A king has three sons who are completely uninterested in wisdom, governance,
or the world. The king hires a scholar named Vishnu Sharma, who promises to
teach them everything they need to know in six months using only stories.
The Panchatantra is what he teaches them.

Written approximately 300 BCE (though drawing on older oral traditions), the
Panchatantra is organized into five books — five "tantras" or strategies for
living. Each book teaches through interlocked stories: a story within a story
within a story, the way a grandmother tells a cautionary tale by telling another
cautionary tale about a grandmother who told the wrong cautionary tale.

The animals think and speak and scheme with precise human psychology. The crow
who uses a sequence of clever manipulations to get the snake who has been eating
his eggs killed. The lion and the clever jackal. The mice who free the elephants
by gnawing through nets. These are not fables with morals appended — the moral
is structural, embedded in what happens and why.

The Panchatantra was translated into Pahlavi in 570 CE, then into Arabic as
Kalila wa-Dimna, then into Syriac, Hebrew, Latin, and eventually every European
language. Aesop's Fables may predate the Panchatantra, but the Panchatantra
traveled further and influenced more storytelling traditions. La Fontaine knew
it. Goethe admired it. It is, quietly, one of the most influential books in
the history of human narrative.

In India, it is still what grandparents read to grandchildren when they want
to teach without appearing to teach.
        """,
    },
]


def collect_mythology(test_mode: bool = False) -> int:
    head("MYTHOLOGY AS LIVING WISDOM")
    collected = 0

    embedded = MYTHOLOGY_EMBEDDED[:1] if test_mode else MYTHOLOGY_EMBEDDED
    for item in tqdm(embedded, desc="Mythology profiles"):
        if from_embedded(item["title"], item["domain"],
                         item["content"], "", item["rasa"], "myth"):
            collected += 1

    wiki_items = MYTHOLOGY_WIKI[:3] if test_mode else MYTHOLOGY_WIKI
    for wiki_title, domain, rasa in tqdm(wiki_items, desc="Mythology Wikipedia"):
        if from_wiki(wiki_title, domain, rasa, "myth"):
            collected += 1

    ok(f"Mythology: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 4 — THE WORDS THAT DON'T TRANSLATE
#  Sanskrit, Tamil, and other Indic concepts that the world needs
#  but has no words for. Each entry is a doorway.
# ══════════════════════════════════════════════════════════════════════════════

UNTRANSLATABLE_CONCEPTS = {
    "Dharma": {
        "language": "Sanskrit",
        "root": "dhri — to hold, to sustain",
        "rasa": "Shanta",
        "explanation": """
Dharma is the most important word in Indian civilization and the most
mistranslated. It is usually rendered as "duty" or "religion" or "righteousness,"
and it is none of these precisely.

Dharma is the inherent nature of a thing — the quality that makes it what it is.
The dharma of fire is to burn. The dharma of water is to flow. The dharma of a
river is to reach the sea. When a thing acts according to its dharma, it is
right with the universe.

For a human being, dharma is more complex because we have multiple natures
and multiple relationships. Your dharma as a father is different from your
dharma as a citizen. Your dharma changes as you age. The entire Bhagavad Gita
is Krishna trying to help Arjuna understand what his dharma requires of him
in that specific moment.

The philosophical leap is that dharma is not imposed from outside — it is
discovered from within. You don't follow dharma to please a god or society.
You follow dharma because violating it means violating what you fundamentally are.

When modern Indians say "that's not right," the unspoken word underneath the
English is often dharma.
        """,
    },
    "Rasa": {
        "language": "Sanskrit",
        "root": "ras — to taste, to experience",
        "rasa": "Adbhuta",
        "explanation": """
Rasa is the aesthetic theory that underlies all Indian art — and it has no
Western equivalent in depth or precision.

Rasa means "essence" or "juice" — the flavor of an experience distilled to
its pure form. Bharata Muni, in the Natyashastra (200 BCE–200 CE), identified
eight primary rasas: Shringara (love/beauty), Hasya (joy/humor), Karuna
(compassion/grief), Raudra (fury), Vira (heroism), Bhayanaka (fear/awe),
Bibhatsa (disgust), and Adbhuta (wonder). A ninth — Shanta (peace) — was added
later.

The theory of rasa says that art's purpose is not to represent reality but to
distill the emotional essence of experience so pure that the audience doesn't
merely feel an emotion — they become it temporarily, freed from their personal
context. This state is called rasanubhava — the experience of rasa.

What makes rasa theory radical is what it implies about the audience. You don't
go to a performance to be entertained. You go to be expanded — to briefly inhabit
emotional states with full intensity, without the weight of personal consequence.
This is why Indian audiences at a Bharatanatyam performance or a classical concert
sometimes close their eyes. They are not watching. They are tasting.

Every Indian art form — music, dance, poetry, theatre, sculpture, temple
architecture — is structured around the deliberate evocation of rasa.
        """,
    },
    "Jugaad": {
        "language": "Hindi/Punjabi",
        "root": "Colloquial — no clear Sanskrit root",
        "rasa": "Hasya",
        "explanation": """
Jugaad entered the global business vocabulary in the 2010s as "frugal innovation"
— using whatever is available to solve a problem creatively, without waiting for
ideal resources. But this translation makes it sound like a strategy. It is a
way of being.

Jugaad is the farmer who turns a discarded motor into an irrigation pump. The
village mechanic who fixes a car with a piece of wire and absolute confidence.
The mother who makes a child's toy from a broken plastic bottle. It is the
specific Indian genius of making things work with what is here, now, rather than
waiting for what should be.

The word carries no shame of imperfection — the jugaad solution is celebrated,
not apologized for. It represents a different relationship to resources: not
wasteful abundance, not resigned poverty, but creative abundance — the
recognition that necessity is genuinely the mother of invention and that
invention is available to everyone.

C.K. Prahalad's "fortune at the bottom of the pyramid" theory is essentially
a formalization of jugaad. The global movement for appropriate technology —
designing for real constraints rather than ideal conditions — is jugaad with
a grant application attached.
        """,
    },
    "Atithi Devo Bhava": {
        "language": "Sanskrit",
        "root": "Taittiriya Upanishad — 'The guest is God'",
        "rasa": "Shringara",
        "explanation": """
Atithi Devo Bhava means "the guest is god" — but the word atithi is more
precise than "guest." Atithi comes from a-tithi, meaning "one who comes without
a fixed day" — the unexpected visitor, the stranger who arrives unannounced.

The principle is that the unexpected guest — precisely because their arrival was
not planned, precisely because they have no claim on your hospitality — must be
received as if the divine itself has arrived. Their need is a sacred gift to you:
the opportunity to serve.

This is not hospitality as social performance. It is hospitality as spiritual
practice. The highest obligation is not to your family, not to your community,
not even to your friend — it is to the stranger at the door at an inconvenient
hour who has nowhere else to go.

The India Tourism tagline "Atithi Devo Bhava" commercializes the phrase, but the
practice is real in Indian homes. The reflex to feed a visitor, to insist they
stay, to be offended if they refuse the second helping of food — these are not
mere politeness. They are the residue of a three-thousand-year-old theology
of hospitality.
        """,
    },
    "Ananda": {
        "language": "Sanskrit",
        "root": "nand — to rejoice",
        "rasa": "Shanta",
        "explanation": """
Ananda is usually translated as "bliss" or "joy," but it means something more
specific and more radical: joy that needs no reason.

The Taittiriya Upanishad places ananda at the innermost layer of the self —
the anandamaya kosha, the sheath of bliss. The argument is that beneath the
physical body, beneath the energy body, beneath the mental body, beneath the
intellectual body, there is a layer of pure joy that is the fundamental substance
of the self. This joy is not produced by anything external. It requires nothing.
It simply is.

The philosophical claim is enormous: suffering is not fundamental. Joy is
fundamental. The suffering we experience is real, but it is like a cloud passing
across a sky that is itself blue. The bliss at the center of existence is
permanent; our access to it is intermittent.

This is why the names of Indian saints so often end in Ananda — Vivekananda,
Sivananda, Yogananda, Satchidananda. The -ananda suffix doesn't mean they are
happy people. It means they have touched the substrate of joy that is available
to everyone but noticed by few.

The practical implication is that seeking happiness from external sources is
a misunderstanding of where happiness lives. Indian philosophy's deepest gift
to the world may be this precise point.
        """,
    },
    "Ahimsa": {
        "language": "Sanskrit",
        "root": "a- (not) + himsa (injury, violence)",
        "rasa": "Shanta",
        "explanation": """
Ahimsa is non-violence — but the Sanskrit negative prefix a- is not passive.
It describes an active quality: the condition of not-causing-harm that requires
constant, conscious effort.

Patanjali lists ahimsa as the first of the Yamas — the first ethical restraint
in yogic practice, before all others, before even truth-telling. The Jain
tradition elevates it to its central principle: the most scrupulous Jain monks
sweep the ground before them as they walk, wear cloth over their mouths, and
strain their drinking water — all to avoid harm to the smallest living things.

Mahatma Gandhi made ahimsa the operating principle of an anti-colonial movement
and changed the history of the twentieth century. This is not coincidental —
ahimsa is not a passive withdrawal from conflict. It is a form of active
resistance that refuses to create the moral debt that violence creates.

The deeper meaning is about thought as much as action. The fully realized
practitioner of ahimsa causes no harm in thought, word, or deed. This makes
ahimsa a practice of decades, not a rule to follow: the aim is to become a being
whose very presence is safe for everything around them.

Albert Einstein, near the end of his life, wrote: "I believe that Gandhi's views
were the most enlightened of all the political men of our time." He was
describing ahimsa in practice.
        """,
    },
    "Sthitaprajna": {
        "language": "Sanskrit",
        "root": "sthita (steady) + prajna (wisdom)",
        "rasa": "Shanta",
        "explanation": """
In the second chapter of the Bhagavad Gita, Arjuna asks Krishna: what does a
person of steady wisdom look like? How do they speak? How do they sit? How do
they move? Krishna's answer is the description of sthitaprajna — the person
whose wisdom is not an achievement of the mind but the nature of the self.

A sthitaprajna is not disturbed by sorrow and not excited by joy. Not because
they feel nothing — they feel everything fully — but because the source of their
stability is deeper than feeling. They have no anxiety about the future and no
resentment about the past. Their senses are completely under control — not through
suppression but through having found something more interesting than the senses'
usual objects.

What makes this concept powerful is its pragmatic precision. It's not a mystical
state available only to monks. It's a psychological description: a person who
has found a source of stability that is not dependent on circumstances. The world
can be in chaos and they can still act with clarity.

Modern psychology's concept of "equanimity" is a partial translation. Viktor
Frankl's "space between stimulus and response" touches it. The Stoic ideal of
the sage approaches it from the other direction. But sthitaprajna is more
specific: not a detachment from life but a rootedness so deep that life's
turbulence cannot uproot you.
        """,
    },
    "Lila": {
        "language": "Sanskrit",
        "root": "lil — to play",
        "rasa": "Hasya and Adbhuta",
        "explanation": """
Lila means "divine play" — the idea that the universe is not a purposeful
project but a joyful game. Creation is not something God did for a reason.
Creation is something God did for the pleasure of doing it, the way a child
builds a sandcastle not to have a sandcastle but to experience building.

This is one of the most radical ideas in Indian philosophy. If the universe is
lila — if there is no cosmic emergency, no problem that needs solving, no
judgment at the end — then suffering is real but not ultimate, joy is fundamental,
and the appropriate response to existence is something like grateful play.

Krishna's entire life is described as lila. His butter theft as a child, his
Holi games, his flute playing, his love for the gopis — these are not episodes
in a heroic narrative. They are the hero simply being delight, the way water
simply flows downhill.

Alan Watts, the philosopher who introduced many Western thinkers to Indian ideas,
considered lila the most important concept he encountered. He wrote: "Through
the Hindu lens, the universe is God playing hide-and-seek with himself."

For ordinary people, lila implies that life is not a test or a punishment or
a preparation for something else. It is itself. This is enough.
        """,
    },
}


def collect_concepts(test_mode: bool = False) -> int:
    head("UNTRANSLATABLE CONCEPTS")
    concepts = dict(list(UNTRANSLATABLE_CONCEPTS.items())[:3]) \
               if test_mode else UNTRANSLATABLE_CONCEPTS
    collected = 0

    extra_wiki = [
        ("Karma", "Philosophy", "Shanta"),
        ("Moksha", "Philosophy", "Shanta"),
        ("Samsara", "Philosophy", "Karuna"),
        ("Maya_(religion)", "Philosophy", "Adbhuta"),
        ("Brahman", "Philosophy", "Shanta"),
        ("Atman_(Hinduism)", "Philosophy", "Shanta"),
        ("Viveka", "Philosophy", "Shanta"),
        ("Vairagya", "Philosophy", "Shanta"),
        ("Santosha", "Philosophy", "Shanta"),
        ("Tapas_(practice)", "Philosophy", "Vira"),
    ]

    for word, data in tqdm(concepts.items(), desc="Untranslatable concepts"):
        full = textwrap.dedent(f"""\
            Concept: {word}
            Language: {data['language']}
            Root: {data['root']}
            Rasa: {data['rasa']}

            {data['explanation'].strip()}
        """)
        if from_embedded(f"Untranslatable: {word}",
                         "Indian Philosophical Concepts",
                         full, "", data["rasa"], "concept"):
            collected += 1

    extra = extra_wiki[:2] if test_mode else extra_wiki
    for wiki_title, domain, rasa in tqdm(extra, desc="Concept Wikipedia"):
        if from_wiki(wiki_title, domain, rasa, "concept"):
            collected += 1

    ok(f"Concepts: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 5 — SACRED GEOGRAPHY
#  Places that carry meaning. The map of India as spiritual landscape.
# ══════════════════════════════════════════════════════════════════════════════

SACRED_PLACES = [
    {
        "name": "Varanasi — where time stops",
        "wiki": "Varanasi",
        "rasa": "Bhayanaka and Shanta",
        "story": """
Varanasi is the oldest continuously inhabited city in the world. It has been
a city since before Rome, before Athens, before the founding of Jerusalem. People
have been burning their dead on its ghats for three thousand years without
interruption. This is not a metaphor. The fires on the Manikarnika ghat have not
gone out in living memory.

The city is built on the western bank of the Ganga — the only side the sun
touches in the morning. This is deliberate. At dawn, the ghats come alive: the
priests perform aarti (fire offerings) as the sun rises over the river, the
sound of conch shells and bells and Sanskrit mantras rising through smoke and
mist. Pilgrims who have traveled hundreds of miles wade into the river as the
first light touches the water.

Mark Twain visited Varanasi in 1896 and wrote: "Benares is older than history,
older than tradition, older even than legend, and looks twice as old as all
of them put together." He meant this as exaggeration. It was not.

Hindus believe that dying in Varanasi — the city of Shiva, the city of
liberation — breaks the cycle of rebirth. This is why the dying are brought here.
The burning ghats are not morbid — they are active, matter-of-fact, almost
businesslike. Death in Varanasi is not an ending but a completion. People arrive
knowing they are arriving to die, and they seem at peace with this.

The Ganga at Varanasi is filthy by any environmental measure. It is also, for
those who have stood at its bank at dawn, the most powerful river in the world.
These two facts coexist without difficulty in the Indian mind.
        """,
    },
    {
        "name": "Char Dham — the four corners of India",
        "wiki": "Char_Dham",
        "rasa": "Vira and Shanta",
        "story": """
Adi Shankaracharya, the philosopher-monk who traveled the entire Indian
subcontinent in the 8th century CE to revitalize Hindu philosophy, established
four sacred centers at India's four geographic extremes: Badrinath in the
Himalayas (north), Puri on the Bay of Bengal (east), Dwarka on the Arabian
Sea (west), and Rameshwaram at the southern tip where India almost touches
Sri Lanka.

A pilgrimage that visits all four — the Char Dham yatra — was considered a
complete spiritual life. You had walked the entire sacred geography of the
subcontinent. You had covered India with your feet.

The four dhams were chosen for more than geography. Each represents a different
quality of the divine — Badrinath the austerity and height of Vishnu in meditation,
Puri the abundance and community of Jagannath (Lord of the Universe), Dwarka
the wisdom of the aged Krishna, Rameshwaram the devotion of Ram who built a
bridge across the sea for love.

To do Char Dham properly, in the old tradition, was to walk. Months, seasons,
the entirety of India passing beneath your feet. The journey was the destination.
You arrived at Badrinath or Rameshwaram not as a tourist but as someone who had
spent months becoming equal to the arrival.

Modern pilgrims often do Char Dham by bus and train. The tradition adapts but
the intention remains: to have the sacred geography of India inside you, to
carry the four corners in your body.
        """,
    },
    {
        "name": "The Ganga — a river that is alive",
        "wiki": "Ganges",
        "rasa": "Shanta and Karuna",
        "story": """
The Ganga is not a river in India. The Ganga is a goddess who became a river —
and for hundreds of millions of Indians, she has never stopped being both.

She flows from the Gangotri glacier in the Himalayas, fed by the melting of
Shiva's matted hair in the mythology, and moves southeast through the plains
of North India, through Rishikesh, Haridwar, Allahabad (Prayagraj), Varanasi,
Patna, and finally Kolkata, where she reaches the sea as the Hooghly.

Her scientific peculiarity is real: Ganga water has unusual antibacterial
properties that scientists attribute to bacteriophages — viruses that kill
bacteria — along with dissolved minerals from the Himalayan rocks. The water
keeps for longer than normal river water. This is part of why the tradition of
carrying Gangajal (Ganga water) in copper vessels across India developed —
copper amplifies the water's properties. The science gave a physical basis to
the mythology.

But the Ganga's hold on the Indian imagination is not scientific. It is the
river of home. An Indian who grows up near the Ganga and moves away will dream
of it. Those who have never seen it treat it as a birthright. The practice of
immersing cremated ashes in the Ganga — so the soul's final material remains are
carried by the sacred river to the sea — happens in India's rivers every day,
in every season.

"Mother Ganga" is not a poetic personification. It is the accurate description
of a relationship.
        """,
    },
    {
        "name": "Vrindavan — where Krishna lives now",
        "wiki": "Vrindavan",
        "rasa": "Shringara",
        "story": """
Vrindavan — the forest of Vrinda (the Tulsi plant, sacred to Vishnu) — is a
small town on the Yamuna river in Uttar Pradesh that has, for five hundred years,
been treated as a place where the past and present coexist.

According to the Bhagavata Purana, Krishna's childhood was spent here: his theft
of butter, his games with the gopis, his killing of demons, his first musical
encounters with Radha. The Vaishnava theology developed by Chaitanya Mahaprabhu
(15th century) holds that these events are not merely historical — they continue
happening, eternally, in a Vrindavan that exists outside of time. The physical
town is a portal to this eternal Vrindavan.

This is why the town has a quality unlike any other religious site in India.
The pilgrims who come here — especially the elderly widows who come to live
out their final years in Vrindavan's ashrams — are not commemorating something
that happened. They believe they are, in some sense, present for it.

The town itself is chaotic, crowded, full of temples and monkeys and pilgrims
and priests and peacocks. The Yamuna is polluted. The streets are narrow. None
of this contradicts the sacred quality — Vrindavan's devotees would say that
this earthly imperfection is part of the teaching: the divine hides itself in
the ordinary, waits to be found.

The rasa-lila performances of Vrindavan — theatrical re-enactments of Krishna's
dances with the gopis — are considered the most sacred art form in Vaishnava
culture. The young boys who play Krishna are treated, during the performance,
as the actual divine. Audiences weep. The boundary between ritual and reality
dissolves completely.
        """,
    },
]

SACRED_WIKI_EXTRAS = [
    ("Tirupati",          "Sacred Geography", "Shanta"),
    ("Golden_Temple",     "Sacred Geography", "Shanta"),
    ("Ajmer_Sharif",      "Sacred Geography", "Shanta"),
    ("Velankanni",        "Sacred Geography", "Karuna"),
    ("Bodh_Gaya",         "Sacred Geography", "Shanta"),
    ("Hampi",             "Sacred Geography", "Adbhuta"),
    ("Pushkar",           "Sacred Geography", "Shanta"),
    ("Rishikesh",         "Sacred Geography", "Shanta"),
    ("Amarnath",          "Sacred Geography", "Bhayanaka"),
    ("Sabarimala",        "Sacred Geography", "Vira"),
]


def collect_sacred(test_mode: bool = False) -> int:
    head("SACRED GEOGRAPHY")
    collected = 0
    places = SACRED_PLACES[:2] if test_mode else SACRED_PLACES

    for place in tqdm(places, desc="Sacred places"):
        wiki_text = ""
        w = wiki_fetch(place["wiki"])
        if w:
            wiki_text = f"\n\n--- Wikipedia ---\n{w['extract'][:2000]}"
        full = textwrap.dedent(f"""\
            Sacred place: {place['name']}
            Rasa: {place['rasa']}

            {place['story'].strip()}
            {wiki_text}
        """)
        if from_embedded(place["name"], "Sacred Geography of India",
                         full, f"https://en.wikipedia.org/wiki/{place['wiki']}",
                         place["rasa"], "sacred"):
            collected += 1
        time.sleep(WIKI_DELAY)

    extras = SACRED_WIKI_EXTRAS[:2] if test_mode else SACRED_WIKI_EXTRAS
    for wiki_title, domain, rasa in tqdm(extras, desc="Sacred Wikipedia"):
        if from_wiki(wiki_title, domain, rasa, "sacred"):
            collected += 1

    ok(f"Sacred geography: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 6 — REGIONAL INDIA  (28 distinct worlds)
# ══════════════════════════════════════════════════════════════════════════════

REGIONAL_WIKI = [
    # South India
    ("Culture_of_Karnataka",     "Regional — Karnataka",   "Shringara"),
    ("Culture_of_Tamil_Nadu",    "Regional — Tamil Nadu",  "Vira"),
    ("Culture_of_Kerala",        "Regional — Kerala",      "Shanta"),
    ("Culture_of_Andhra_Pradesh","Regional — Andhra",      "Vira"),
    ("Culture_of_Telangana",     "Regional — Telangana",   "Vira"),
    # North India
    ("Culture_of_Rajasthan",     "Regional — Rajasthan",   "Adbhuta"),
    ("Culture_of_Punjab",        "Regional — Punjab",      "Hasya"),
    ("Culture_of_Gujarat",       "Regional — Gujarat",     "Hasya"),
    ("Culture_of_Maharashtra",   "Regional — Maharashtra", "Vira"),
    ("Culture_of_Uttar_Pradesh", "Regional — UP",          "Shanta"),
    # East India
    ("Culture_of_West_Bengal",   "Regional — Bengal",      "Karuna"),
    ("Culture_of_Odisha",        "Regional — Odisha",      "Shringara"),
    ("Culture_of_Bihar",         "Regional — Bihar",       "Shanta"),
    # Northeast India
    ("Culture_of_Assam",         "Regional — Assam",       "Shanta"),
    ("Culture_of_Manipur",       "Regional — Manipur",     "Shringara"),
    ("Culture_of_Meghalaya",     "Regional — Meghalaya",   "Adbhuta"),
    ("Nagaland",                 "Regional — Nagaland",    "Vira"),
    # Central India
    ("Culture_of_Madhya_Pradesh","Regional — MP",          "Adbhuta"),
    # Specific art/culture traditions
    ("Yakshagana",               "Regional — Karnataka",   "Vira"),
    ("Chhau_dance",              "Regional — East India",  "Vira"),
    ("Theyyam",                  "Regional — Kerala",      "Bhayanaka"),
    ("Lavani",                   "Regional — Maharashtra", "Shringara"),
    ("Ghoomar",                  "Regional — Rajasthan",   "Shringara"),
    ("Bihu_dance",               "Regional — Assam",       "Hasya"),
    ("Bhangra_(dance)",          "Regional — Punjab",      "Hasya"),
]


def collect_regional(test_mode: bool = False) -> int:
    head("REGIONAL INDIA — 28 WORLDS")
    items = REGIONAL_WIKI[:4] if test_mode else REGIONAL_WIKI
    collected = 0
    for wiki_title, domain, rasa in tqdm(items, desc="Regional India"):
        if from_wiki(wiki_title, domain, rasa, "regional"):
            collected += 1
    ok(f"Regional India: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  DOMAIN 7 — LITERATURE AS CULTURAL MIRROR
# ══════════════════════════════════════════════════════════════════════════════

LITERATURE_WIKI = [
    ("Rabindranath_Tagore",    "Literature", "Karuna"),
    ("R._K._Narayan",          "Literature", "Hasya"),
    ("Premchand",              "Literature", "Karuna"),
    ("Kamala_Das",             "Literature", "Shringara"),
    ("Arundhati_Roy",          "Literature", "Karuna"),
    ("Girish_Karnad",          "Literature", "Raudra"),
    ("U._R._Ananthamurthy",    "Literature", "Karuna"),
    ("Vikram_Seth",            "Literature", "Shringara"),
    ("Amitav_Ghosh",           "Literature", "Karuna"),
    ("Jhumpa_Lahiri",          "Literature", "Karuna"),
    ("Mulk_Raj_Anand",         "Literature", "Bibhatsa"),
    ("Ismat_Chughtai",         "Literature", "Shringara"),
    ("Saadat_Hasan_Manto",     "Literature", "Bibhatsa"),
    ("Subramania_Bharati",     "Literature", "Vira"),
    ("Mahadevi_Varma",         "Literature", "Karuna"),
    ("Gitanjali",              "Literature", "Shanta"),
    ("Malgudi_Days",           "Literature", "Hasya"),
    ("The_God_of_Small_Things","Literature", "Karuna"),
]


def collect_literature(test_mode: bool = False) -> int:
    head("LITERATURE AS CULTURAL MIRROR")
    items = LITERATURE_WIKI[:3] if test_mode else LITERATURE_WIKI
    collected = 0
    for wiki_title, domain, rasa in tqdm(items, desc="Literature"):
        if from_wiki(wiki_title, domain, rasa, "lit"):
            collected += 1
    ok(f"Literature: {collected} documents")
    return collected


# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_summary(total: int):
    head("WORLD CORPUS SUMMARY")
    if not metadata:
        warn("No new documents collected this run.")
        return

    total_words = sum(m["word_count"] for m in metadata)
    by_dom: dict[str, int] = {}
    by_rasa: dict[str, int] = {}
    for m in metadata:
        by_dom[m["domain"]] = by_dom.get(m["domain"], 0) + 1
        if m.get("rasa"):
            r = m["rasa"].split("(")[0].strip().split(" ")[0]
            by_rasa[r] = by_rasa.get(r, 0) + 1

    print(f"\n  New documents this run:  {len(metadata)}")
    print(f"  New words:               {total_words:,}")

    print(f"\n  By domain:")
    for d, c in sorted(by_dom.items(), key=lambda x: -x[1])[:12]:
        print(f"    - {d:<44}  {c} docs")

    if by_rasa:
        print(f"\n  Rasa (emotional) distribution:")
        for r, c in sorted(by_rasa.items(), key=lambda x: -x[1]):
            print(f"    - {r:<20}  {c} docs")

    print(f"""
  {Fore.GREEN}{Style.BRIGHT}Everything is in:{Style.RESET_ALL}
  iks_corpus/processed/     ← LlamaIndex ready
  iks_corpus/world/         ← raw new documents
  iks_corpus/metadata.json  ← full log
""")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

DOMAINS = {
    "ragas":      collect_ragas,
    "festivals":  collect_festivals,
    "mythology":  collect_mythology,
    "concepts":   collect_concepts,
    "sacred":     collect_sacred,
    "regional":   collect_regional,
    "literature": collect_literature,
}


def main():
    parser = argparse.ArgumentParser(
        description="IKS World Corpus Collector — culture, feeling, living India"
    )
    parser.add_argument(
        "--domain",
        choices=list(DOMAINS.keys()) + ["all"],
        default="all",
    )
    parser.add_argument("--test", action="store_true",
                        help="Quick test: 2 items per domain")
    args = parser.parse_args()

    print(f"""
{Fore.MAGENTA}{Style.BRIGHT}
  ╔═════════════════════════════════════════════════════╗
  ║    IKS World Corpus Collector  v1.0                 ║
  ║    Building the feeling of India, not just facts    ║
  ╚═════════════════════════════════════════════════════╝
{Style.RESET_ALL}
  Output  →  {BASE_DIR.resolve()}
  Mode    →  {"TEST" if args.test else "FULL"}
  Domain  →  {args.domain}
""")

    total = 0
    if args.domain == "all":
        for fn in DOMAINS.values():
            total += fn(args.test)
    else:
        total += DOMAINS[args.domain](args.test)

    save_metadata()
    print_summary(total)
    print(f"  {Fore.GREEN}{Style.BRIGHT}Done!  {total} new documents.{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()

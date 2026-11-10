import csv, os, re, json, glob, base64, mimetypes, html as H, datetime, requests
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

# ---------- config ----------
CFG = {"brand": "AICUF SJEC Unit", "style": ""}
if os.path.exists("config.json"):
    CFG.update(json.load(open("config.json", encoding="utf-8")))
BRAND = CFG["brand"]

now = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
d = now.date()
today = d.isoformat()

# ---------- fallback themes (used if Gemini fails) ----------
THEMES = [
    (("independence", "republic", "constitution"), dict(bg1="#0a1f5c", bg2="#138808", accent="#FF9933", text="#ffffff", motifs=["🇮🇳", "🕊️", "🪁"])),
    (("diwali", "deepavali"),      dict(bg1="#2a0845", bg2="#6b1d1d", accent="#FFC107", text="#fff8e1", motifs=["🪔", "✨", "🎆"])),
    (("christmas",),               dict(bg1="#7a0c14", bg2="#0b3d20", accent="#FFD54F", text="#ffffff", motifs=["🎄", "⭐", "🎁"])),
    (("easter", "good friday"),    dict(bg1="#3b2a6b", bg2="#c9a227", accent="#ffffff", text="#ffffff", motifs=["✝️", "🕊️", "🌷"])),
    (("eid", "ramzan", "ramadan", "bakrid"), dict(bg1="#063d2e", bg2="#0b6e4f", accent="#FFD54F", text="#ffffff", motifs=["🌙", "⭐", "🕌"])),
    (("holi",),                    dict(bg1="#6a1b9a", bg2="#e91e63", accent="#FFEB3B", text="#ffffff", motifs=["🎨", "🌈", "💦"])),
    (("ganesh", "chaturthi"),      dict(bg1="#b53a00", bg2="#6d1b00", accent="#FFE082", text="#ffffff", motifs=["🐘", "🌺", "🪔"])),
    (("onam",),                    dict(bg1="#1b5e20", bg2="#f9a825", accent="#ffffff", text="#ffffff", motifs=["🌼", "🛶", "🌺"])),
    (("earth", "environment", "tree", "forest", "water"), dict(bg1="#0b3d2e", bg2="#1b7f4b", accent="#C6FF00", text="#ffffff", motifs=["🌍", "🌱", "🌳"])),
    (("women", "mother"),          dict(bg1="#4a148c", bg2="#ad1457", accent="#FFCCBC", text="#ffffff", motifs=["👩", "🌸", "💜"])),
    (("teacher", "education", "literacy", "student"), dict(bg1="#0d2b55", bg2="#1565c0", accent="#FFD54F", text="#ffffff", motifs=["📚", "🎓", "✏️"])),
    (("children", "child"),        dict(bg1="#0277bd", bg2="#7b1fa2", accent="#FFEB3B", text="#ffffff", motifs=["🎈", "🧸", "🌈"])),
    (("science",),                 dict(bg1="#0b1d3a", bg2="#145a8a", accent="#4FC3F7", text="#ffffff", motifs=["🔬", "🧪", "🚀"])),
    (("kindness", "tolerance"),    dict(bg1="#4a1f5e", bg2="#b3446c", accent="#FFD1DC", text="#ffffff", motifs=["💛", "🤝", "🌸"])),
]
DEFAULT = dict(bg1="#0f2027", bg2="#2c5364", accent="#FFC107", text="#ffffff", motifs=["✨", "⭐", "🌟"])
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

def keyword_theme(name):
    n = name.lower()
    for keys, th in THEMES:
        if any(k in n for k in keys):
            return dict(th)
    return dict(DEFAULT)

def ai_theme(name, date_str, style):
    key = os.environ.get("GEMINI_KEY")
    if not key:
        return None
    prompt = (
        f'Design brief for an Instagram poster. Event: "{name}", date: {date_str}, country: India. '
        f'Designer style instructions (follow strictly): {style or "none"}. '
        "Return ONLY JSON with keys: tagline (max 8 words, catchy, no hashtags), "
        "bg1 and bg2 (hex colours; follow the style instructions; if none, use dark rich colours "
        "matching the event's traditional colours; for minimal styles use two very similar colours), "
        "accent (hex, strong contrast against bg1), "
        "text (hex, high contrast and readable on bg1), "
        "motifs (array of exactly 3 emojis that fit the event)."
    )
    try:
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"responseMimeType": "application/json"}},
            timeout=60,
        )
        data = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
        for k in ("bg1", "bg2", "accent", "text"):
            if not HEX.match(data.get(k, "")):
                return None
        if len(data.get("motifs", [])) < 3:
            data["motifs"] = ["✨", "⭐", "🌟"]
        return data
    except Exception as e:
        print("Gemini failed:", e)
        return None

def motif_html(motifs):
    spots = [(40, 60, 220, -15), (760, 90, 180, 20), (860, 520, 240, 10), (20, 640, 200, 25),
             (120, 1050, 260, -10), (780, 1100, 220, 15), (430, 20, 150, 0), (450, 1180, 170, -20)]
    out = []
    for i, (x, y, s, rot) in enumerate(spots):
        out.append(f'<div class="m" style="left:{x}px;top:{y}px;font-size:{s}px;transform:rotate({rot}deg)">{motifs[i % len(motifs)]}</div>')
    return "".join(out)

def logos_html():
    files = []
    for ext in ("png", "jpg", "jpeg", "webp", "svg"):
        files += glob.glob(f"logos/*.{ext}")
    out = []
    for f in sorted(files):
        mime = mimetypes.guess_type(f)[0] or "image/png"
        b64 = base64.b64encode(open(f, "rb").read()).decode()
        out.append(f'<img src="data:{mime};base64,{b64}">')
    return "".join(out)

def size_for(title):
    n = len(title)
    return 120 if n <= 14 else 100 if n <= 24 else 80 if n <= 36 else 64

def fmt_date(s):
    try:
        return datetime.date.fromisoformat(s.strip()).strftime("%d %B %Y")
    except ValueError:
        return s

# ---------- 1) your own events from dates.csv win ----------
rows = [r for r in csv.DictReader(open("dates.csv", encoding="utf-8"))
        if r["date"].strip() == today]

# ---------- 2) else auto-detect today's festival ----------
if not rows:
    resp = requests.get(
        "https://calendarific.com/api/v2/holidays",
        params={"api_key": os.environ["CALENDARIFIC_KEY"], "country": "IN",
                "year": d.year, "month": d.month, "day": d.day},
        timeout=30,
    )
    hols = resp.json().get("response", {}).get("holidays", [])

    def priority(h):
        t = " ".join(h.get("type", [])).lower()
        if "national" in t: return 0
        if any(x in t for x in ("religious", "hinduism", "christian", "muslim")): return 1
        return 2

    hols = sorted(hols, key=priority)[:3]
    rows = [{"date": today, "event": h["name"], "tagline": "", "venue": BRAND,
             "_desc": (h.get("description") or "")[:110]} for h in hols]

if not rows:
    print("Nothing found for", today)
    raise SystemExit

template = open("template.html", encoding="utf-8").read()
token = os.environ["TELEGRAM_TOKEN"]
chat = os.environ["TELEGRAM_CHAT_ID"]
logos = logos_html()

with sync_playwright() as p:
    browser = p.chromium.launch()
    for i, r in enumerate(rows):
        style = (r.get("style") or "").strip() or CFG["style"]
        minimal = "minimal" in style.lower()
        date_str = fmt_date(r["date"])

        theme = ai_theme(r["event"], date_str, style) or keyword_theme(r["event"])
        tagline = r.get("tagline") or theme.get("tagline") or r.get("_desc") or ""
        vals = {
            "date": date_str, "event": r["event"], "tagline": tagline,
            "venue": r.get("venue") or BRAND,
            "bg1": theme["bg1"], "bg2": theme["bg2"],
            "accent": theme["accent"], "text": theme["text"],
            "size": str(size_for(r["event"])),
            "cls": "minimal" if minimal else "",
        }
        page_html = template
        for k, v in vals.items():
            page_html = page_html.replace("{{" + k + "}}", H.escape(v))
        page_html = page_html.replace("{{motif}}", "" if minimal else motif_html(theme["motifs"]))
        page_html = page_html.replace("{{logos}}", logos)

        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.set_content(page_html, wait_until="networkidle")
        path = f"poster_{today}_{i}.png"
        page.screenshot(path=path)
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendDocument",
                data={"chat_id": chat, "caption": r["event"]},
                files={"document": f},
            )
    browser.close()

import csv, os, re, json, glob, base64, math, mimetypes, html as H, datetime, requests
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

# ---------- config ----------
CFG = {"style": ""}
if os.path.exists("config.json"):
    CFG.update(json.load(open("config.json", encoding="utf-8")))

now = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
d = now.date()
today = d.isoformat()

SCENES = ("globe", "hills", "stars", "rays")

# ---------- fallback themes (used if Gemini fails) ----------
THEMES = [
    (("independence", "republic", "constitution"), dict(bg1="#0a1f5c", bg2="#138808", accent="#FF9933", text="#ffffff", scene="rays")),
    (("diwali", "deepavali"),      dict(bg1="#2a0845", bg2="#6b1d1d", accent="#FFC107", text="#fff8e1", scene="stars")),
    (("christmas",),               dict(bg1="#7a0c14", bg2="#0b3d20", accent="#FFD54F", text="#ffffff", scene="stars")),
    (("easter", "good friday"),    dict(bg1="#3b2a6b", bg2="#c9a227", accent="#ffffff", text="#ffffff", scene="rays")),
    (("eid", "ramzan", "ramadan", "bakrid"), dict(bg1="#063d2e", bg2="#0b6e4f", accent="#FFD54F", text="#ffffff", scene="stars")),
    (("holi",),                    dict(bg1="#6a1b9a", bg2="#e91e63", accent="#FFEB3B", text="#ffffff", scene="rays")),
    (("ganesh", "chaturthi"),      dict(bg1="#b53a00", bg2="#6d1b00", accent="#FFE082", text="#ffffff", scene="rays")),
    (("onam",),                    dict(bg1="#1b5e20", bg2="#f9a825", accent="#ffffff", text="#ffffff", scene="hills")),
    (("earth", "environment", "tree", "forest", "water"), dict(bg1="#0b3d2e", bg2="#1b7f4b", accent="#C6FF00", text="#ffffff", scene="globe")),
    (("women", "mother", "violence"), dict(bg1="#4a148c", bg2="#ad1457", accent="#FFCCBC", text="#ffffff", scene="rays")),
    (("teacher", "education", "literacy", "student"), dict(bg1="#0d2b55", bg2="#1565c0", accent="#FFD54F", text="#ffffff", scene="stars")),
    (("children", "child"),        dict(bg1="#0277bd", bg2="#7b1fa2", accent="#FFEB3B", text="#ffffff", scene="hills")),
    (("science",),                 dict(bg1="#0b1d3a", bg2="#145a8a", accent="#F5C77E", text="#ffffff", scene="globe")),
    (("kindness", "tolerance"),    dict(bg1="#4a1f5e", bg2="#b3446c", accent="#FFD1DC", text="#ffffff", scene="rays")),
]
DEFAULT = dict(bg1="#0f2027", bg2="#2c5364", accent="#FFC107", text="#ffffff", scene="hills")
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
        f'Design brief for a minimal Instagram poster. Event: "{name}", date: {date_str}, country: India. '
        f'Designer style instructions (follow strictly): {style or "none"}. '
        "Return ONLY JSON with keys: tagline (max 8 words, elegant, no hashtags), "
        "bg1 and bg2 (hex colours, dark and rich, matching the event mood; bg1 darker), "
        "accent (hex, warm or bright, strong contrast against bg1), "
        "text (hex, light, readable on bg1), "
        'scene (one of: "globe" for science/earth/world themes, "hills" for nature/children/peace, '
        '"stars" for education/night/celebration, "rays" for unity/kindness/rights/national days).'
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
        if data.get("scene") not in SCENES:
            data["scene"] = keyword_theme(name)["scene"]
        return data
    except Exception as e:
        print("Gemini failed:", e)
        return None

# ---------- scenes (SVG graphics at the bottom of the poster) ----------
STAR_DOTS = [(90, 90, 3), (210, 190, 2), (330, 60, 2.5), (450, 150, 2), (620, 70, 3),
             (740, 180, 2), (860, 100, 2.5), (980, 200, 2), (150, 260, 2), (930, 40, 2)]

def scene_svg(name, a):
    head = '<svg class="scene" viewBox="0 0 1080 700" xmlns="http://www.w3.org/2000/svg">'
    glow = (f'<defs><radialGradient id="g" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0" stop-color="{a}" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="p" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{a}" stop-opacity=".3"/>'
            f'<stop offset=".25" stop-color="#000" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".75"/></linearGradient></defs>')
    body = ""
    if name == "globe":
        body += '<circle cx="540" cy="300" r="440" fill="url(#g)"/>'
        body += f'<circle cx="540" cy="860" r="560" fill="url(#p)" stroke="{a}" stroke-opacity=".85" stroke-width="3"/>'
        body += f'<circle cx="540" cy="860" r="592" fill="none" stroke="{a}" stroke-opacity=".25" stroke-width="2"/>'
        body += '<circle cx="540" cy="296" r="9" fill="#ffffff"/>'
        body += "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" fill-opacity=".7"/>' for x, y, r in STAR_DOTS)
    elif name == "stars":
        pts = [(180, 470), (340, 380), (520, 450), (700, 340), (880, 430)]
        body += '<circle cx="540" cy="700" r="420" fill="url(#g)"/>'
        body += f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{a}" stroke-opacity=".5" stroke-width="2"/>'
        body += "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="{a}"/>' for x, y in pts)
        body += "".join(f'<circle cx="{x}" cy="{y+330}" r="{r}" fill="#ffffff" fill-opacity=".6"/>' for x, y, r in STAR_DOTS)
    elif name == "rays":
        body += f'<circle cx="540" cy="700" r="170" fill="{a}" fill-opacity=".28"/>'
        body += f'<circle cx="540" cy="700" r="250" fill="none" stroke="{a}" stroke-opacity=".3" stroke-width="2"/>'
        for deg in range(-80, 81, 10):
            rad = math.radians(deg)
            x2, y2 = 540 + 700 * math.sin(rad), 700 - 700 * math.cos(rad)
            body += f'<line x1="540" y1="700" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{a}" stroke-opacity=".22" stroke-width="2"/>'
    else:  # hills
        body += '<circle cx="540" cy="420" r="320" fill="url(#g)"/>'
        body += f'<circle cx="540" cy="430" r="120" fill="{a}" fill-opacity=".6"/>'
        body += '<path d="M0 520 Q270 400 540 490 T1080 450 V700 H0Z" fill="#000" fill-opacity=".25"/>'
        body += '<path d="M0 585 Q300 480 600 565 T1080 525 V700 H0Z" fill="#000" fill-opacity=".4"/>'
        body += '<path d="M0 655 Q350 590 700 645 T1080 615 V700 H0Z" fill="#000" fill-opacity=".6"/>'
    return head + glow + body + "</svg>"

# ---------- logos (first = top-left, the rest = top-right) ----------
def logo_imgs():
    files = []
    for ext in ("png", "jpg", "jpeg", "webp", "svg"):
        files += glob.glob(f"logos/*.{ext}")
    out = []
    for f in sorted(files):
        mime = mimetypes.guess_type(f)[0] or "image/png"
        b64 = base64.b64encode(open(f, "rb").read()).decode()
        out.append(f'<img src="data:{mime};base64,{b64}">')
    return out

def size_for(title):
    n = len(title)
    return 150 if n <= 14 else 118 if n <= 24 else 92 if n <= 36 else 76

def fmt_date(s):
    try:
        dt = datetime.date.fromisoformat(s.strip())
        return f"{dt.day} {dt.strftime('%B')}"
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
    rows = [{"date": today, "event": h["name"], "tagline": "",
             "_desc": (h.get("description") or "")[:110]} for h in hols]

if not rows:
    print("Nothing found for", today)
    raise SystemExit

template = open("template.html", encoding="utf-8").read()
token = os.environ["TELEGRAM_TOKEN"]
chat = os.environ["TELEGRAM_CHAT_ID"]
logos = logo_imgs()
logo_left = logos[0] if logos else ""
logo_right = "".join(logos[1:])

with sync_playwright() as p:
    browser = p.chromium.launch()
    for i, r in enumerate(rows):
        style = (r.get("style") or "").strip() or CFG["style"]
        date_str = fmt_date(r["date"])

        theme = ai_theme(r["event"], date_str, style) or keyword_theme(r["event"])
        tagline = r.get("tagline") or theme.get("tagline") or r.get("_desc") or ""
        vals = {
            "date": date_str, "event": r["event"], "tagline": tagline,
            "bg1": theme["bg1"], "bg2": theme["bg2"],
            "accent": theme["accent"], "text": theme["text"],
            "size": str(size_for(r["event"])),
        }
        page_html = template
        for k, v in vals.items():
            page_html = page_html.replace("{{" + k + "}}", H.escape(v))
        page_html = page_html.replace("{{scene}}", scene_svg(theme["scene"], theme["accent"]))
        page_html = page_html.replace("{{logo_left}}", logo_left)
        page_html = page_html.replace("{{logo_right}}", logo_right)

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

# -*- coding: utf-8 -*-
"""Generate static SVG cards for the GitHub profile README (no external services)."""
import json
import os
import sys
from datetime import datetime, timedelta

TEMP = os.environ.get("TEMP", "/tmp")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

BG = "#0d1117"
CARD = "#161b22"
FG = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#00d4aa"
ORANGE = "#f0883e"

FONT = "Segoe UI, Ubuntu, Sans-Serif"


def load(name):
    with open(os.path.join(TEMP, name), encoding="utf-8-sig") as f:
        return json.load(f)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- data
user = load("user.json")
repos = load("repos.json")
contrib = load("contrib.json")["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]

public_repos = [r for r in repos if not r.get("private")]
stars = sum(r.get("stargazers_count", 0) for r in public_repos)
forks = sum(r.get("forks_count", 0) for r in public_repos)
total_contrib = contrib["totalContributions"]

# languages by repo primary language count
lang_count = {}
for r in public_repos:
    lang = r.get("language")
    if lang:
        lang_count[lang] = lang_count.get(lang, 0) + 1
langs = sorted(lang_count.items(), key=lambda kv: -kv[1])[:6]

days = []
for week in contrib["weeks"]:
    for d in week["contributionDays"]:
        days.append((d["date"], d["contributionCount"]))
days = days[-140:]  # last ~20 weeks


# ---------------------------------------------------------------- card 1: stats
def stats_card():
    items = [
        ("Репозитории", len(public_repos)),
        ("★ Звёзды", stars),
        ("⑂ Форки", forks),
        ("Контрибуции", total_contrib),
    ]
    w, h = 495, 195
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">')
    p.append(f'<rect width="{w}" height="{h}" rx="8" fill="{BG}"/>')
    p.append(f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="none" stroke="#30363d"/>')
    p.append(f'<text x="24" y="40" font-size="18" font-weight="700" fill="{FG}">📊 GitHub Статистика</text>')
    p.append(f'<line x1="24" y1="54" x2="{w-24}" y2="54" stroke="#30363d"/>')
    # 2x2 grid
    positions = [(24, 95), (w / 2 + 10, 95), (24, 155), (w / 2 + 10, 155)]
    for (label, value), (x, y) in zip(items, positions):
        p.append(f'<text x="{x}" y="{y}" font-size="26" font-weight="700" fill="{ACCENT}">{value}</text>')
        p.append(f'<text x="{x + (len(str(value)) * 17) + 8}" y="{y}" font-size="13" fill="{MUTED}">{esc(label)}</text>')
    p.append('</svg>')
    with open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(p))


# ---------------------------------------------------------------- card 2: languages
def langs_card():
    w = 350
    rows = max(len(langs), 1)
    h = 70 + rows * 42
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">')
    p.append(f'<rect width="{w}" height="{h}" rx="8" fill="{BG}"/>')
    p.append(f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="none" stroke="#30363d"/>')
    p.append(f'<text x="24" y="38" font-size="17" font-weight="700" fill="{FG}">🛠️ Технологии</text>')
    p.append(f'<line x1="24" y1="50" x2="{w-24}" y2="50" stroke="#30363d"/>')
    if not langs:
        p.append(f'<text x="24" y="85" font-size="14" fill="{MUTED}">Пока нет публичных репозиториев</text>')
    else:
        mx = langs[0][1]
        y = 82
        for name, cnt in langs:
            pct = cnt / mx
            p.append(f'<text x="24" y="{y}" font-size="14" fill="{FG}">{esc(name)}</text>')
            p.append(f'<rect x="24" y="{y + 8}" width="{w - 68}" height="8" rx="4" fill="#21262d"/>')
            p.append(f'<rect x="24" y="{y + 8}" width="{int((w - 68) * pct)}" height="8" rx="4" fill="{ACCENT}"/>')
            p.append(f'<text x="{w - 34}" y="{y + 1}" font-size="13" fill="{MUTED}" text-anchor="end">{cnt}</text>')
            y += 42
    p.append('</svg>')
    with open(os.path.join(OUT, "langs.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(p))


# ---------------------------------------------------------------- card 3: activity graph
def graph_card():
    w, h = 960, 260
    pad_l, pad_r, pad_t, pad_b = 30, 30, 70, 40
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">')
    p.append(f'<rect width="{w}" height="{h}" rx="8" fill="{BG}"/>')
    p.append(f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="none" stroke="#30363d"/>')
    p.append(f'<text x="24" y="40" font-size="17" font-weight="700" fill="{FG}">🔥 График активности</text>')
    p.append(f'<text x="{w-24}" y="40" font-size="13" fill="{MUTED}" text-anchor="end">{total_contrib} контрибуций за всё время</text>')

    n = len(days)
    if n < 2:
        p.append(f'<text x="24" y="120" font-size="14" fill="{MUTED}">Недостаточно данных</text>')
    else:
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b
        mx = max(max(c for _, c in days), 1)
        pts = []
        for i, (_, c) in enumerate(days):
            x = pad_l + plot_w * i / (n - 1)
            y = pad_t + plot_h * (1 - c / mx)
            pts.append((x, y))
        # area
        area = f"M {pts[0][0]:.1f} {pad_t + plot_h:.1f} " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in pts) + f" L {pts[-1][0]:.1f} {pad_t + plot_h:.1f} Z"
        p.append(f'<path d="{area}" fill="{ACCENT}" fill-opacity="0.15"/>')
        line = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        p.append(f'<path d="{line}" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-linejoin="round"/>')
        # dots on peaks
        for i, (x, y) in enumerate(pts):
            if days[i][1] == mx:
                p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{ORANGE}"/>')
        # axis labels
        p.append(f'<text x="{pad_l}" y="{h - 14}" font-size="12" fill="{MUTED}">{days[0][0]}</text>')
        p.append(f'<text x="{w - pad_r}" y="{h - 14}" font-size="12" fill="{MUTED}" text-anchor="end">{days[-1][0]}</text>')
        p.append(f'<text x="{pad_l}" y="{pad_t - 8}" font-size="12" fill="{MUTED}">макс: {mx}/день</text>')
    p.append('</svg>')
    with open(os.path.join(OUT, "graph.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(p))


stats_card()
langs_card()
graph_card()
print("generated:", os.listdir(OUT))

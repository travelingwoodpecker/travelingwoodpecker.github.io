#!/usr/bin/env python3
"""Builds the Traveling Woodpecker home page and country pages.

Source of truth: data/trips.json (in the travelingwoodpecker.github.io repo).
Run from anywhere:  python3 tools/build.py
It writes index.html in this repo and <country>/index.html in each sibling
country repo folder (../usa, ../norway, ...). Trip pages themselves are
hand-built and are never overwritten.
"""
import json, os, sys, html
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(HERE)                      # travelingwoodpecker.github.io
ROOT = os.environ.get('TW_ROOT', os.path.dirname(HOME))   # folder holding all repos
SKIP = set(filter(None, os.environ.get('TW_SKIP', '').split(',')))

data = json.load(open(os.path.join(HOME, 'data', 'trips.json'), encoding='utf8'))
maps = json.load(open(os.path.join(HOME, 'data', 'maps.json'), encoding='utf8'))
C = {c['slug']: c for c in data['countries']}
ORDER = [c['slug'] for c in data['countries']]
trips = sorted(data['trips'], key=lambda t: -t['year'])
e = html.escape


def href(s):
    return C[s].get('href') or f'/{s}/'

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700'
         '&family=Literata:opsz,wght@7..72,400;7..72,600&family=IBM+Plex+Sans:wght@400;500;600'
         '&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">')

LOGO = '<img src="/assets/logo-mark.png" alt="" width="34" height="34">'

ICON = {
    'page': '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    'pdf': '<svg viewBox="0 0 24 24"><path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/></svg>',
}
LABEL = {'page': 'Trip page', 'pdf': 'Itinerary (PDF)'}


def page(title, desc, current, body):
    nav = ''.join(
        f'<a href="{href(s)}"{" aria-current=page" if s == current else ""}>{e(C[s]["short"])}</a>' for s in ORDER)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#2F5D4E">
<link rel="icon" type="image/png" href="/assets/favicon.png">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="topbar"><div class="topbar-in"><a class="brand" href="/">{LOGO}<span>Traveling Woodpecker</span></a><nav class="nav" aria-label="Countries">{nav}</nav></div></header>
{body}
<footer><div class="wrap">© {max(t["year"] for t in trips)} Traveling Woodpecker · Motorcycle rides, country by country.</div></footer>
</body>
</html>
'''


def days_txt(t):
    if t.get('duration'):
        return t['duration']
    if t.get('days'):
        return f'{t["days"]} days'
    return ''


def ride_li(t, here=None):
    links = t.get('links', [])
    primary = next((l for l in links if l['kind'] == 'page'), None)
    title = e(t['title'])
    if primary:
        title = f'<a href="{e(primary["url"])}">{title}</a>'
    if t.get('status') == 'upcoming':
        title += '<span class="tag soon">Upcoming</span>'
    meta = [x for x in [t.get('dates'), days_txt(t), (t.get('miles') + ' mi') if t.get('miles') else None] if x]
    others = [s for s in t['countries'] if s != here]
    if others:
        meta.append(' · '.join(f'<a href="{href(s)}">{e(C[s]["name"])}</a>' for s in others) if here else
                    ' & '.join(e(C[s]['name']) for s in t['countries']))
    btns = ''.join(
        f'<a class="lk{" primary" if l["kind"] == "page" else ""}" href="{e(l["url"])}"'
        f'{"" if l["url"].startswith("/") else " target=_blank rel=noopener"}>{ICON[l["kind"]]}{LABEL[l["kind"]]}</a>'
        for l in links)
    if not links:
        btns = '<span class="missing">Trip page coming</span>'
    return (f'<li class="ride"><div class="ride-main"><p class="ride-title">{title}</p>'
            f'<p class="ride-meta">{" · ".join(meta)}</p></div><div class="links">{btns}</div></li>')


def ride_list(ts, here=None):
    by = defaultdict(list)
    for t in ts:
        by[t['year']].append(t)
    out = []
    for y in sorted(by, reverse=True):
        out.append(f'<div class="year-group"><div class="year">{y}</div><ul class="rides">'
                   + ''.join(ride_li(t, here) for t in by[y]) + '</ul></div>')
    return ''.join(out)


def silhouette(slug, cls='silhouette'):
    return (f'<svg class="{cls}" viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet" role="img" '
            f'aria-label="Outline of {e(C[slug]["name"])}"><path d="{maps["countries"][slug]["d"]}"/></svg>')


def stat(label, val):
    return f'<div class="stat"><dt>{label}</dt><dd>{val}</dd></div>'


def known_days(ts):
    return sum(t.get('days', 0) for t in ts)


# ---------- home ----------
done = [t for t in trips if t.get('status') != 'upcoming']
years = [t['year'] for t in done]
world = []
for f in maps['world']:
    if not f['d']:
        continue
    p = f'<path d="{f["d"]}"><title>{e(f["name"])}</title></path>'
    if f['slug']:
        p = f'<a href="{href(f["slug"])}" aria-label="{e(C[f["slug"]]["name"])}">{p}</a>'
    world.append(p)

cards = []
for s in ORDER:
    ts = [t for t in trips if s in t['countries']]
    ys = sorted({t['year'] for t in ts})
    span = f'{ys[0]}–{ys[-1]}' if len(ys) > 1 else str(ys[0])
    n = len(ts)
    cards.append(f'<a class="ccard" href="{href(s)}">{silhouette(s, "")}<h3>{e(C[s]["name"])}</h3>'
                 f'<p>{n} ride{"s" if n != 1 else ""} · {span}</p></a>')

fut = ''.join(f'<div class="future"><p class="kicker">Future plan</p><h3>{e(x["title"])}</h3><p>{e(x["note"])}</p>'
              + (f'<p style="margin-top:16px"><a class="lk" style="background:#fff;color:var(--pine)" href="{e(x["url"])}" target="_blank" rel="noopener">See the day-by-day plan (PDF)</a></p>' if x.get('url') else '') + '</div>'
              for x in data.get('future', []))

home_body = f'''<main class="wrap">
<section class="hero hero-split home-hero">
<div><p class="kicker">Motorcycle logbook · {min(years)}–{max(t["year"] for t in trips)}</p>
<h1>Traveling Woodpecker</h1>
<p class="dek">Every ride, country by country: the routes, the roads and the places in between.</p>
<dl class="stats">{stat("Countries", len(ORDER))}{stat("Rides", len(done))}{stat("Days on the road", f"{known_days(done)}+")}{stat("Years", len(set(years)))}</dl></div>
<img class="home-logo" src="/assets/logo-520.png" alt="Traveling Woodpecker logo: a woodpecker riding a dirt bike" width="520" height="511">
</section>
<section class="section" aria-label="World map" id="map-h">
<p class="section-note" style="margin:0 0 10px;text-align:center">Click a country to see its rides.</p>
<svg class="worldmap" viewBox="0 0 960 470" role="img" aria-label="World map with the countries ridden highlighted">{"".join(world)}</svg>
<p class="map-legend"><span class="v">Ridden</span><span>Not yet</span></p>
</section>
<section class="section" aria-labelledby="c-h">
<div class="section-head"><h2 id="c-h">Countries</h2></div>
<div class="cards">{"".join(cards)}</div>
</section>
<section class="section" aria-labelledby="t-h">
<div class="section-head"><h2 id="t-h">Every ride</h2><p class="section-note">Newest first</p></div>
{ride_list(trips)}
</section>
<section class="section">{fut}</section>
</main>'''

outputs = {os.path.join(HOME, 'index.html'): page(
    'Traveling Woodpecker', 'A motorcycle logbook: every ride, country by country.', None, home_body)}

# ---------- countries ----------
for s in ORDER:
    if s in SKIP:
        continue
    c = C[s]
    ts = [t for t in trips if s in t['countries']]
    past = [t for t in ts if t.get('status') != 'upcoming']
    ys = sorted({t['year'] for t in ts})
    span = f'{ys[0]}–{ys[-1]}' if len(ys) > 1 else str(ys[0])
    n = len(ts)
    statrow = stat('Rides', n) + (stat('Days on the road', f'{known_days(past)}{"+" if any(not t.get("days") for t in past) else ""}') if known_days(past) else '') + stat('Years', span)
    res = ''
    if c['resources']:
        res = ('<section class="section"><div class="section-head"><h2>Resources</h2></div><div class="res">'
               + ''.join(f'<a href="{e(r["url"])}" target="_blank" rel="noopener"><span>{e(r["note"])}</span><b>{e(r["label"])}</b></a>' for r in c['resources'])
               + '</div></section>')
    body = f'''<main class="wrap">
<section class="hero hero-split">
<div><p class="kicker">Motorcycle rides · {span}</p><h1>{e(c["name"])}</h1>
<dl class="stats">{statrow}</dl></div>
{silhouette(s)}
</section>
<section class="section" aria-labelledby="r-h">
<div class="section-head"><h2 id="r-h">Rides</h2><p class="section-note">Newest first</p></div>
{ride_list(ts, s)}
</section>
{res}
</main>'''
    outputs[os.path.join(ROOT, C[s].get('dir', s), 'index.html')] = page(
        f'{c["name"]} · Traveling Woodpecker', f'Motorcycle rides in {c["name"]}, {span}.', s, body)

for path, txt in outputs.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf8') as f:
        f.write(txt)
    print('wrote', os.path.relpath(path, ROOT))

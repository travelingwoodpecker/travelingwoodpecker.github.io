#!/usr/bin/env python3
"""Builds ride pages from data/rides/<slug>.json (+ <slug>.map.svg).

Writes ../<country>/<slug>/index.html for each ride. Run: python3 tools/build_trips.py
"""
import json, os, glob, html, re

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(HERE)
ROOT = os.environ.get('TW_ROOT', os.path.dirname(HOME))
e = html.escape

# reuse the page shell from build.py without re-running its outputs
src = open(os.path.join(HERE, 'build.py'), encoding='utf8').read().split('# ---------- home ----------')[0]
ns = {'__file__': os.path.join(HERE, 'build.py')}
exec(src, ns)
page, C = ns['page'], ns['C']

ARROW = '<svg class="leg-arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'
EXT = ' target="_blank" rel="noopener"'


def day_html(i, d):
    title = e(d['title']) if d.get('title') else f'{e(d.get("from_t", d["from"]))} {ARROW} {e(d.get("to_t", d["to"]))}'
    out = [f'<article class="tday" id="day{i}"><header class="tday-head">'
           f'<p class="tday-date"><b>{e(d["label"])}</b>{" · " + e(d["date"]) if d.get("date") else ""}</p><h2>{title}</h2>']
    if d.get('dist'):
        out.append(f'<p class="tday-dist">{e(d["dist"])}</p>')
    out.append('</header><div class="tday-body"><div class="tday-main">')
    for a, b in d.get('legs', []):
        out.append(f'<p class="leg"><span>{e(a)}</span><span class="leg-rule"></span><span class="leg-d">{e(b)}</span></p>')
    for p in d.get('prose', []):
        out.append(f'<p class="prose">{e(p)}</p>')
    for k, v in d.get('highlights', []):
        out.append(f'<p class="prose"><b>{e(k)}:</b> {e(v)}</p>')
    if d.get('road'):
        k, v = d['road']
        out.append(f'<aside class="road"><p class="road-tag">The road</p><h3>{e(k)}</h3><p>{e(v)}</p></aside>')
    if d.get('via'):
        out.append('<p class="side-k">By way of</p><ul class="sights">' + ''.join(f'<li>{e(v)}</li>' for v in d['via']) + '</ul>')
    if d.get('sights'):
        out.append('<p class="side-k">Along the way</p><ul class="sights">' + ''.join(
            f'<li><b>{e(n)}</b> — {e(t)}</li>' for n, t in d['sights']) + '</ul>')
    if d.get('tips'):
        out.append(f'<aside class="road"><p class="road-tag">Riding tips</p><p>{e(d["tips"])}</p></aside>')
    if d.get('weather'):
        out.append(f'<p class="side-k">Weather outlook</p><p class="prose">{e(d["weather"])}</p>')
    if d.get('dangers'):
        out.append('<p class="side-k">Watch for</p><ul class="sights watch">' + ''.join(
            f'<li><b>{e(n)}.</b> {e(t)}</li>' for n, t in d['dangers']) + '</ul>')
    if d.get('photos'):
        out.append(f'<div class="photos" style="--n:{min(len(d["photos"]), 4)}">' + ''.join(
            f'<figure><a href="{e(ph["src"])}" target="_blank" rel="noopener"><img src="{e(ph["src"])}" alt="{e(ph["cap"])}" loading="lazy"></a>'
            f'<figcaption>{e(ph["cap"])}</figcaption></figure>' for ph in d['photos']) + '</div>')
    if not any(d.get(x) for x in ('prose', 'legs', 'road', 'highlights', 'via', 'sights', 'tips', 'golf', 'photos')):
        out.append('<p class="prose quiet">Notes for this day are still to come.</p>')
    out.append('</div><div class="tday-side">')
    if d.get('stops'):
        out.append('<p class="side-k">Along the way</p><ul class="stoplist">' + ''.join(
            f'<li><a href="{e(u)}"{EXT}>{e(n)}</a></li>' for n, u in d['stops']) + '</ul>')
    if d.get('videos'):
        out.append('<p class="side-k">Ride videos</p><ul class="stoplist">' + ''.join(
            f'<li><a href="{e(u)}"{EXT}>▶ {e(n)}</a></li>' for n, u in d['videos']) + '</ul>')
    L = d.get('lodging')
    if L:
        nm = f'<a href="{e(L["url"])}"{EXT}>{e(L["name"])}</a>' if L.get('url') else e(L['name'])
        out.append(f'<div class="lodge"><p class="side-k">Overnight</p><p class="lodge-n">{nm}</p>'
                   + (f'<p class="lodge-a">{e(L["addr"])}</p>' if L.get('addr') else '')
                   + (f'<p class="lodge-a">{e(L["note"])}</p>' if L.get('note') else '')
                   + (f'<p class="lodge-d">{e(L["desc"])}</p>' if L.get('desc') else '') + '</div>')
    if d.get('golf'):
        out.append(f'<div class="lodge golf"><p class="side-k">Golf</p><p class="lodge-n">{e(d["golf"][0])}</p><p class="lodge-a">{e(d["golf"][1])}</p></div>')
    if d.get('dining'):
        out.append('<div class="dining"><p class="side-k">Dining</p>' + ''.join(
            f'<p class="din-n">{e(n)}</p><p class="lodge-a">{e(a)}</p><p class="lodge-d">{e(t)}</p>' for n, a, t in d['dining']) + '</div>')
    out.append('</div></div></article>')
    return ''.join(out)


def build(r, svg):
    c = C[r['country']]
    stats = ''.join(f'<div class="stat"><dt>{e(b)}</dt><dd>{e(a)}</dd></div>' for a, b in r['stats'])
    chips = ''.join(f'<a href="#day{i}">{e(d["label"])}</a>' for i, d in enumerate(r['days']))
    cap = ('Route traced from the original ride plan.' if r.get('tracks')
           else 'Overnight stops; lines show the order, not the exact roads.')
    if r.get('map_img'):
        svg = (f'<a href="{e(r["map_img"])}" target="_blank" rel="noopener"><img class="routemap" '
               f'src="{e(r["map_img"])}" alt="Route map of the ride"></a>')
        cap = r.get('map_cap', 'The route as ridden.')
    if r.get('states_line') and not r.get('facts'):
        r['facts'] = [['States', r['states_line']]]
    facts = ''
    if r.get('facts'):
        facts = '<section class="facts">' + ''.join(
            f'<div><p class="side-k">{e(k)}</p><p>{e(v)}</p></div>' for k, v in r['facts']) + '</section>'
    if r.get('callout'):
        co = r['callout']
        facts += (f'<aside class="road callout"><p class="road-tag">{e(co.get("tag", "Ridden with"))}</p>'
                  f'<h3><a href="{e(co["url"])}"{EXT}>{e(co["name"])}</a></h3><p>{e(co["text"])}</p></aside>')
    body = f'''<main class="wrap trip">
<p class="crumbs"><a href="/{c["slug"]}/">{e(c["name"])}</a> / {r["year"]}</p>
<section class="hero hero-split trip-hero">
<div><p class="kicker">{e(r["kicker"])}</p><h1>{e(r["title"])}</h1><p class="dek">{e(r["dek"])}</p>
<dl class="stats">{stats}</dl></div>
<figure class="rm-fig">{svg}<figcaption>{cap}</figcaption></figure>
</section>
{facts}
<nav class="daychips" aria-label="Days">{chips}</nav>
{"".join(day_html(i, d) for i, d in enumerate(r["days"]))}
<p class="backlink"><a href="/{c["slug"]}/">← All {e(c["name"])} rides</a></p>
</main>'''
    return page(f'{r["title"]} ({r["year"]}) · Traveling Woodpecker', r['dek'][:155], c['slug'], body)


for f in sorted(glob.glob(os.path.join(HOME, 'data', 'rides', '*.json'))):
    r = json.load(open(f, encoding='utf8'))
    svg = open(f[:-5] + '.map.svg', encoding='utf8').read()
    out = os.path.join(ROOT, C[r['country']].get('dir', r['country']), r['slug'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf8').write(build(r, svg))
    print('wrote', os.path.relpath(out, ROOT))

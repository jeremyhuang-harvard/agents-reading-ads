#!/usr/bin/env python3
"""Ads-as-Cues linkage metrics: cue similarity, distinctiveness, repetition, brand prominence, World Cup convergence."""
import collections, json, math, re, unicodedata
from pathlib import Path

B = Path(__file__).resolve().parents[1] / 'data' / 'processed'  # public release: was an absolute path
rows = [json.loads(l) for l in open(B / 'competitor_analysis_v1/ad_label_panel.jsonl')]
man = {i['coding_id']: i for i in json.load(open(B / 'competitor_labels_v1/manifest.json'))['items']}
lab = {}
for l in open(B / 'competitor_labels_v1/results.jsonl'):
    r = json.loads(l)
    if r['status'] == 'ok':
        lab[r['coding_id']] = r['labels']
FIRMS = ['Winamax', 'PMU', 'Unibet', 'Betsson', 'bet365']
BRAND_TOKENS = {'winamax', 'pmu', 'unibet', 'betsson', 'bet365', 'bet', '365', 'kindred', 'play', 'wina'}
STOP = set("""le la les de des du un une et en à a au aux sur pour par ton ta tes ta votre vos ou ce cet cette ces est sont avec dans
pas plus que qui on il elle nous vous ils ne se sa son ses mon ma mes l d j s n c qu jusqu jusqu'à 1er 18 www fr com the of and to in""".split())
WARN = set("jeux argent hasard peuvent etre dangereux pertes conflits familiaux addiction retrouvez conseils joueurs info service appel non surtaxe gouvernement 09 74 75 13 interdit mineurs".split())


def toks(text):
    t = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    out = []
    for w in re.findall(r"[a-z0-9]+", t):
        if w in STOP or w in WARN or w in BRAND_TOKENS or len(w) < 3 or w.isdigit():
            continue
        out.append(w[:6])  # crude stem, as in the paper's truncation
    return out


def cos(a, b):
    num = sum(a[k] * b.get(k, 0) for k in a)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0


def feat(L):
    f = collections.Counter()
    for k, v in L['borrowed_meaning'].items():
        f['bm:' + k] += v['prominence'] / 3
    for s in L['sports']:
        f['sp:' + s] += 1
    f['lvl:' + L['competition_level']] += 1
    f['fr:' + L['primary_framing']] += 1
    f['of:' + L['offer']['type']] += 1
    f['tp:' + L['template']] += 1
    return f


def vec(rs, kind, weight='imp'):
    v = collections.Counter()
    for r in rs:
        L = lab.get(r['coding_id'])
        if not L:
            continue
        w = (r['impressions'] or 1) if weight == 'imp' else 1
        src = collections.Counter(toks(' '.join(L['visible_text_verbatim']) + ' ' + (r['headline'] or ''))) if kind == 'text' else feat(L)
        for k, x in src.items():
            v[k] += w * x
    return v


out = {}
for kind in ('text', 'labels'):
    for weight in ('ads', 'imp'):
        V = {f: vec([r for r in rows if r['firm'] == f], kind, weight) for f in FIRMS}
        out[f'{kind}_{weight}'] = {f'{a}|{b}': round(cos(V[a], V[b]), 3) for i, a in enumerate(FIRMS) for b in FIRMS[i + 1:]}
# Monthly label similarity, 2026 months with >= 2 firms launching
months = {}
for m in sorted({r['start'][:7] for r in rows if r['start'] >= '2026-01'}):
    V = {f: vec([r for r in rows if r['firm'] == f and r['start'][:7] == m], 'labels', 'ads') for f in FIRMS}
    V = {f: v for f, v in V.items() if v}
    if len(V) >= 2:
        pairs = [cos(V[a], V[b]) for i, a in enumerate(V) for b in list(V)[i + 1:]]
        months[m] = {'firms': list(V), 'mean_pair_sim': round(sum(pairs) / len(pairs), 3),
                     'wina_bet365': round(cos(V['Winamax'], V['bet365']), 3) if 'Winamax' in V and 'bet365' in V else None}
out['monthly_label_similarity'] = months
# Distinctiveness: representative features (firm share / rival share), BCGS stereotype logic
dist = {}
allv = {f: vec([r for r in rows if r['firm'] == f], 'labels', 'imp') for f in FIRMS}
for f in FIRMS:
    tot = sum(allv[f].values()); rv = collections.Counter()
    for g in FIRMS:
        if g != f:
            rv.update(allv[g])
    rtot = sum(rv.values())
    ratios = {k: (allv[f][k] / tot) / ((rv[k] / rtot) + 1e-3) for k in allv[f] if allv[f][k] / tot > 0.02}
    dist[f] = [(k, round(x, 1)) for k, x in sorted(ratios.items(), key=lambda kv: -kv[1])[:5]]
out['representative_features'] = dist
# Brand prominence, repetition / rehearsal, generic content
rep = {}
for f in FIRMS:
    rs = [r for r in rows if r['firm'] == f]
    imp = sum(r['impressions'] for r in rs)
    bp = collections.Counter(); generic = 0
    cr = collections.defaultdict(lambda: [0, '9999', '0000'])
    for r in rs:
        L = lab[r['coding_id']]
        bp[L['brand_prominence']] += r['impressions']
        if L['brand_prominence'] <= 1 and L['sports'] and L['sports'][0] == 'football':
            generic += r['impressions']
        c = cr[r['sha256']]; c[0] += r['impressions']; c[1] = min(c[1], r['start']); c[2] = max(c[2], r['start'])
    top3 = sorted(cr.values(), key=lambda c: -c[0])[:3]
    rep[f] = {'brand_prom_ge2': round((bp[2] + bp[3]) / imp, 3), 'brand_prom_3': round(bp[3] / imp, 3),
              'generic_football_low_brand': round(generic / imp, 3),
              'top3_creative_share': round(sum(c[0] for c in top3) / imp, 3),
              'imp_per_creative_M': round(imp / len(cr) / 1e6, 2), 'ads_per_creative': round(len(rs) / len(cr), 2),
              'evergreen_creatives': sum(1 for c in cr.values() if c[1] < '2025-01')}
out['repetition_branding'] = rep
(B / 'competitor_analysis_v1/ads_as_cues_metrics.json').write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=0)[:6000])

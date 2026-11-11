#!/usr/bin/env python3
"""Compute report data (metrics + base64 thumbnails) for the competitor landscape HTML."""
import base64, collections, json
from pathlib import Path
import cv2

BASE = Path(__file__).resolve().parents[1] / 'data'  # public release: was an absolute path
RUN = BASE / 'raw/snap_fr_betting_competitors/run_id=2026-10-21T005219.747976+0000'
INPUTS = BASE / 'processed/competitor_labels_v1/inputs'
OUT = BASE / 'processed/competitor_analysis_v1/report_data.json'
FIRMS = ['Winamax', 'PMU', 'Unibet', 'Betsson', 'bet365']
NAME = {"Winamax": "Winamax", "PMU": "PMU", "Kindred London Ltd": "Unibet", "Betsson France SA": "Betsson", "bet365": "bet365"}

rows = [json.loads(l) for l in open(BASE / 'processed/competitor_analysis_v1/ad_label_panel.jsonl')]
tgt = {}
for l in open(RUN / 'records.jsonl'):
    r = json.loads(l)
    d = (r['ad'].get('targeting_v2') or {}).get('demographics') or [{}]
    dv = (r['ad'].get('targeting_v2') or {}).get('devices') or [{}]
    tgt[r['ad']['id']] = {'gender': d[0].get('gender') or 'ALL', 'min_age': d[0].get('min_age'), 'max_age': d[0].get('max_age'),
                          'os': dv[0].get('os_type') or 'ALL'}


def thumb(cid, width=220):
    for name in (f'{cid}.jpg', f'{cid}.png', f'{cid}_f3.jpg', f'{cid}_f1.jpg'):
        p = INPUTS / name
        if p.exists():
            img = cv2.imread(str(p))
            h, w = img.shape[:2]
            img = cv2.resize(img, (width, int(h * width / w)), interpolation=cv2.INTER_AREA)
            ok, buf = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 72])
            return 'data:image/jpeg;base64,' + base64.b64encode(buf).decode()
    return None


def shares(rs, key_fn, weight=lambda r: r['impressions'] or 1, top=8):
    c = collections.Counter(); t = 0
    for r in rs:
        w = weight(r); t += w
        for k in key_fn(r):
            c[k] += w
    return [[k, round(v / t, 3)] for k, v in c.most_common(top)] if t else []


def creatives(rs, n):
    agg = {}
    for r in rs:
        a = agg.setdefault(r['sha256'], {'cid': r['coding_id'], 'imp': 0, 'ads': 0, 'first': r['start'], 'last': r['start'],
                                          'headline': r['headline'], 'assoc': r['intended_association'], 'framing': r['framing'],
                                          'offer': r['offer_type'], 'tone': r['tone']})
        a['imp'] += r['impressions']; a['ads'] += 1
        a['first'] = min(a['first'], r['start']); a['last'] = max(a['last'], r['start'])
    top = sorted(agg.values(), key=lambda a: -a['imp'])[:n]
    for a in top:
        a['img'] = thumb(a['cid'])
    return top


data = {'firms': {}, 'months': [], 'snapshots': {}}
months = sorted({r['start'][:7] for r in rows if r['start'] >= '2025-09'})
data['months'] = months
for f in FIRMS:
    rs = [r for r in rows if r['firm'] == f]
    t = [tgt[r['ad_id']] for r in rs]
    imp = sum(r['impressions'] for r in rs)
    d = {
        'ads': len(rs), 'creatives': len({r['sha256'] for r in rs}), 'impressions': imp,
        'active': sum(r['status'] == 'ACTIVE' for r in rs), 'first': min(r['start'] for r in rs), 'last': max(r['start'] for r in rs),
        'top10_share': round(sum(sorted((r['impressions'] for r in rs), reverse=True)[: max(1, len(rs) // 10)]) / imp, 3),
        'monthly_imp': {m: sum(r['impressions'] for r in rs if r['start'][:7] == m) for m in months},
        'monthly_ads': {m: sum(r['start'][:7] == m for r in rs) for m in months},
        'pre_window_ads': sum(r['start'][:7] < months[0] for r in rs),
        'borrowed': shares(rs, lambda r: [k for k, v in r['borrowed'].items() if v >= 2], top=17),
        'framing': shares(rs, lambda r: [r['framing']]),
        'offer': shares(rs, lambda r: [r['offer_type']]),
        'sport': shares(rs, lambda r: r['sports']),
        'level': shares(rs, lambda r: [r['competition_level']]),
        'template': shares(rs, lambda r: [r['template']]),
        'risk_free': round(sum(r['impressions'] for r in rs if r['risk_free_language']) / imp, 3),
        'gender': shares(rs, lambda r: [tgt[r['ad_id']]['gender']]),
        'os': shares(rs, lambda r: [tgt[r['ad_id']]['os']]),
        'age': shares(rs, lambda r: [f"{tgt[r['ad_id']]['min_age'] or '?'}–{tgt[r['ad_id']]['max_age'] or '+'}"], top=4),
        'top_creatives': creatives(rs, 6),
    }
    data['firms'][f] = d
for key, (a, b) in {'jan': ('2026-01-01', '2026-01-31'), 'mar': ('2026-03-01', '2026-03-31'), 'jun': ('2026-06-01', '2026-06-30')}.items():
    snap = {}
    for f in FIRMS:
        rs = [r for r in rows if r['firm'] == f and a <= r['start'] <= b]
        if rs:
            snap[f] = {'ads': len(rs), 'creatives': len({r['sha256'] for r in rs}), 'impressions': sum(r['impressions'] for r in rs),
                       'borrowed': shares(rs, lambda r: [k for k, v in r['borrowed'].items() if v >= 2], top=3),
                       'offer': shares(rs, lambda r: [r['offer_type']], top=2), 'top': creatives(rs, 2)}
    data['snapshots'][key] = snap
OUT.write_text(json.dumps(data, ensure_ascii=False))
for f, d in data['firms'].items():
    print(f, d['ads'], d['creatives'], round(d['impressions'] / 1e6), d['active'], d['first'], d['last'], 'top10', d['top10_share'], 'rf', d['risk_free'],
          'pre', d['pre_window_ads'], '| G', d['gender'][:3], '| AGE', d['age'], '| OS', d['os'][:3], '| tmpl', d['template'][:3], '| lvl', d['level'][:3])
    print('   ', [(c['cid'], round(c['imp'] / 1e6, 1), c['first'], (c['headline'] or '')[:35], c['assoc'][:90]) for c in d['top_creatives']])
print(OUT.stat().st_size)

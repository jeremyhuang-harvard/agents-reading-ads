#!/usr/bin/env python3
"""Render the competitor landscape HTML report from report_data.json."""
import html, json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / 'data' / 'processed' / 'competitor_analysis_v1'  # public release: was an absolute path
D = json.loads((BASE / 'report_data.json').read_text())
F = D['firms']
FIRMS = ['Winamax', 'PMU', 'Unibet', 'Betsson', 'bet365']
COL = {'Winamax': '#d7263d', 'PMU': '#1b998b', 'Unibet': '#2e7d32', 'Betsson': '#f46036', 'bet365': '#c9a227'}
TOTAL_IMP = sum(F[f]['impressions'] for f in FIRMS)
e = html.escape

LABEL = {
 'club_fandom_rivalry': 'Club fandom & rivalry', 'national_pride': 'National pride', 'big_event_prestige': 'Big-event prestige',
 'star_athlete_glamour': 'Star athletes', 'expertise_prediction': 'Expertise & prediction', 'humour_wordplay': 'Humour & wordplay',
 'street_youth_culture': 'Street / youth culture', 'creator_authenticity': 'Creator authenticity', 'sociability_community': 'Friends & community',
 'safety_risk_reduction': 'Safety / risk reduction', 'money_wealth_jackpot': 'Money & jackpots', 'official_legitimacy': 'Official legitimacy',
 'tradition_heritage': 'Tradition & heritage', 'play_games_collectibles': 'Games & play', 'product_features': 'Product features',
 'leisure_occasion': 'Leisure occasion', 'strength_masculinity': 'Strength / masculinity',
 'low_risk_trial_or_deal': 'Low-risk deal', 'reward_or_money_making': 'Reward / money', 'companion_to_watching_sport': 'Companion to watching sport',
 'skill_or_prediction_contest': 'Skill / prediction contest', 'product_or_service_utility': 'Product utility', 'competition_entry': 'Competition entry',
 'social_or_community_activity': 'Social activity', 'not_shown': 'Not shown',
 'first_bet_refund_or_guarantee': 'First-bet refund / guarantee', 'cash_bonus': 'Cash bonus', 'boosted_odds': 'Boosted odds',
 'no_deposit_bonus': 'No-deposit bonus', 'prize_pool_or_jackpot': 'Prize pool / jackpot', 'product_feature': 'Product feature',
 'odds_display_only': 'Odds only', 'none': 'None', 'other': 'Other', 'football': 'Football', 'horse_racing': 'Horse racing',
 'poker_casino': 'Poker / casino', 'basketball': 'Basketball', 'tennis': 'Tennis', 'combat_sports': 'Combat sports (MMA)',
 'cycling': 'Cycling', 'motorsport': 'Motorsport', 'rugby': 'Rugby',
}
L = lambda k: LABEL.get(k, k.replace('_', ' ').capitalize())
M = lambda x: f"{x/1e9:.2f}B" if x >= 1e9 else f"{x/1e6:.0f}M" if x >= 1e6 else f"{x/1e3:.0f}K"
P = lambda x: f"{100*x:.0f}%"

PROFILE = {
 'Winamax': {
  'role': 'The cultural incumbent',
  'thesis': 'Owns the conversation around betting rather than competing on the bonus. A few evergreen promises run for years, with a fast-moving topical layer of humour, banter and football moments on top.',
  'what': [
   '<b>An always-on spine of evergreen creatives.</b> Its top ad, “1er pari perdant remboursé <i>cash</i>”, has run since June 2024 and delivered 422M impressions on its own. The top 10% of its ads account for 73% of its impressions.',
   '<b>A clear, differentiated promise.</b> First bets are refunded in <i>cash</i>, explicitly “not freebets”: a subtle dig at rivals whose refunds come as betting credit.',
   '<b>Poker as a second pillar.</b> “Winamax, le N°1 du Poker en ligne”, Space KO and nightly Planète Pok tournaments. Poker is about a quarter of impressions, with rap and street styling.',
   '<b>A topical layer.</b> Match-day puns (“DEMBOUZINHO”, “Paris en boule”), top-scorer questions, NBA, F1 and tennis, plus game promotions (“Penalty World”, “Bang to the Moon”). It is the only brand that regularly runs ads with no offer at all.',
  ],
  'philosophy': 'Treat the brand like a media personality: be the funniest and most fluent voice in the football conversation, and lock in two simple anchors (cash refunds and poker leadership) that are expensive for rivals to copy. Leaders can afford to spend attention on identity rather than on deals.',
  'watch': 'Defending territory. During the World Cup it met bet365 head-on, but with games and national-pride content rather than a matching guarantee.',
 },
 'PMU': {
  'role': 'The heritage operator relaunching as “PMU Play”',
  'thesis': 'A horse-racing institution repositioning as a one-stop betting app, paying for acquisition with large, cash-denominated bonuses.',
  'what': [
   '<b>Every archived ad launched between March and September 2026:</b> a concentrated relaunch campaign of 440 ads in March alone.',
   '<b>Cash is the hook.</b> “Jusqu’à 100€ de bonus en cash” appears in about two-thirds of ads, typically as a giant 3-D “100€”. Money and jackpots are dominant in 78% of ads.',
   '<b>Unique verticals.</b> Horse racing (34% of ads; “1er Opérateur du Turf en ligne”, Arc de Triomphe) and poker (WSOP Circuit partnership, Twister jackpots). Football is the entry point but not the identity.',
   '<b>A product story.</b> “3 univers, 1 seul terrain de jeu” pitches racing, sport and poker in one app; product features are prominent in a third of ads.',
  ],
  'philosophy': 'Use what only PMU has, turf legitimacy and a poker base, to make a newly unified app feel bigger than its football-only rivals, and buy trial with simple cash rather than risk-free language. It is the only established brand targeting all genders.',
  'watch': 'Joined the World Cup (“100€ Cash sur le Foot”) but kept bundling racing and poker. It cross-sells rather than conceding football.',
 },
 'Unibet': {
  'role': 'Bonus-led acquisition on a heavy awareness spine',
  'thesis': 'Recruits new bettors with refunds and no-deposit money, while pushing very high reach through a near-logo-only card.',
  'what': [
   '<b>The single biggest reach play in the panel.</b> One minimal green-logo creative (“100€ de bonus sur ton 1er pari !”) delivered 289M impressions. Pure brand salience.',
   '<b>Free money.</b> A no-deposit €10 code (UNIBET10) and first-bet refunds up to €100. Low-risk deals are the frame of 68% of ads.',
   '<b>Its own niches.</b> MMA (star Benoît Saint Denis; combat sports in 19% of ads), European club nights shown as trading-card-style match cards, and creator or pundit videos.',
   '<b>The narrowest targeting in the panel:</b> 100% men, 94% aged 18–45, 93% iOS.',
  ],
  'philosophy': 'Classic direct-response acquisition: make the brand familiar through cheap high-frequency exposure, then remove the cost of trying it. MMA and creator content add a niche identity the incumbent does not occupy.',
  'watch': 'No new ads launched after 19 March 2026 in this archive, so it is absent from the World Cup period. The cause is unknown and worth checking.',
 },
 'Betsson': {
  'role': 'High-volume, low-reach test-and-learn',
  'thesis': 'Publishes very many template variations at small budgets, each tied to a specific fixture, with a refunded first bet.',
  'what': [
   '<b>1,000 ads (capped) but only 60M impressions,</b> about 60K per ad versus about 3.1M for Winamax. 728 ads launched in January 2026 alone.',
   '<b>A rigid template.</b> A football match card with odds, or an offer banner, plus “100€ remboursés”. Risk-free language appears in 70% of impressions, the highest share with bet365.',
   '<b>Product hooks.</b> “Mix Match” combined bets, odds boosts and a daily boost wheel; tennis in about 10% of ads.',
   '<b>Fixture-by-fixture football:</b> PSG–OM, Champions League nights, Ligue 1.',
  ],
  'philosophy': 'Programmatic acquisition: generate a variant for every match, let the platform find what converts, and lean on a safety net to lower the barrier for an unfamiliar brand. It competes on volume and price, not identity.',
  'watch': 'Strongest when the incumbent is quiet (January 2026); nearly invisible during the World Cup (1.5M impressions in June).',
 },
 'bet365': {
  'role': 'The event-driven entrant',
  'thesis': 'Entered the French Snapchat archive only in late May 2026 and rode World Cup attention with a guaranteed first bet and official-partner legitimacy.',
  'what': [
   '<b>All 170 ads launched between 25 May and 4 September 2026;</b> 125 were still active at collection.',
   '<b>The World Cup as the cue.</b> About half of ads are tied to national-team or major-tournament football (“Parier sur la CM26 !”, France matches, Mbappé); big-event prestige is dominant in about 60% of ads.',
   '<b>Risk reversal.</b> A “premier pari garanti” up to €100 appears in 79% of ads, plus boosted odds (“Super Boost”).',
   '<b>Legitimacy.</b> Official Champions League partner cues and stadium boards. Broad targeting (all genders, 18+), including web.',
  ],
  'philosophy': 'Enter when attention is highest and shared, and neutralise the main barrier to switching (trust and risk) with a guarantee and official badges. It borrows the event’s meaning instead of building its own.',
  'watch': 'Contested the World Cup cue directly against Winamax. This is the clearest case in the data of an entrant trying to claim a context the incumbent occupies.',
 },
}

SNAP_TEXT = {
 'jan': ('January 2026: Betsson fills a quiet month',
         'Winamax launched almost nothing new (one space-themed game promotion). Betsson launched 728 Champions League match cards with refunds and its new “Mix Match” feature; Unibet ran a smaller club-football and refund mix.',
         'A challenger buying football attention cheaply while the leader is not competing for it.'),
 'mar': ('March 2026: three different territories',
         'PMU’s relaunch took poker (WSOP Circuit), the Arc de Triomphe and €100 cash. Unibet pushed reach through its logo card (500M impressions). Winamax answered with Champions League fandom, PSG–Chelsea humour and Premier League banter, mostly with no offer.',
         'Differentiation: each firm occupies its own cue, and the incumbent defends with personality, not price.'),
 'jun': ('June 2026: World Cup convergence',
         'Everyone moved to the World Cup. bet365 launched 92 ads, nearly all leaning on big-event prestige and national pride, with a guaranteed first bet. Winamax used the same event through games (“Penalty World”) and top-scorer questions. PMU sold “100€ Cash sur le Foot” while still bundling racing and poker. Betsson almost disappeared.',
         'Context-claiming: one shared cue, contested with different hooks: safety (entrant), play and identity (incumbent), cash and breadth (heritage operator).'),
}


def bars(items, color, n=6):
    out = []
    for k, v in items[:n]:
        out.append(f'<div class="bar"><span class="bl">{e(L(k))}</span><span class="bt"><span style="width:{max(2, 100*v):.0f}%;background:{color}"></span></span><span class="bv">{P(v)}</span></div>')
    return ''.join(out)


def creative_cards(cs, color):
    out = []
    for c in cs:
        img = f'<img src="{c["img"]}" alt="">' if c.get('img') else '<div class="noimg">no preview</div>'
        out.append(f'''<figure class="cr">{img}<figcaption><b style="color:{color}">{M(c["imp"])} impressions</b> · {c["ads"]} ad{"s" if c["ads"] > 1 else ""} · since {c["first"]}<br>
<span class="hl">“{e(c["headline"] or "")}”</span><br><span class="as">{e(c["assoc"])}</span></figcaption></figure>''')
    return ''.join(out)


def timeline_svg():
    months = D['months']
    w, h, pad = 900, 230, 40
    bw = (w - pad) / len(months)
    peak = max(sum(F[f]['monthly_imp'][m] for f in FIRMS) for m in months) or 1
    parts = [f'<svg viewBox="0 0 {w} {h + 40}" class="chart">']
    for i, m in enumerate(months):
        y = h
        for f in FIRMS:
            v = F[f]['monthly_imp'][m]
            bh = (h - 20) * v / peak
            if bh > 0:
                parts.append(f'<rect x="{pad + i*bw + 3:.1f}" y="{y-bh:.1f}" width="{bw-6:.1f}" height="{bh:.1f}" fill="{COL[f]}"><title>{f} {m}: {M(v)} impressions, {F[f]["monthly_ads"][m]} ads launched</title></rect>')
                y -= bh
        parts.append(f'<text x="{pad + i*bw + bw/2:.1f}" y="{h+16}" class="ax" text-anchor="middle">{m[2:4]}/{m[5:]}</text>')
    for frac in (0.5, 1):
        yy = h - (h - 20) * frac
        parts.append(f'<line x1="{pad}" x2="{w}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/><text x="{pad-6}" y="{yy+4:.1f}" class="ax" text-anchor="end">{M(peak*frac)}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def heatmap():
    cats = ['safety_risk_reduction', 'money_wealth_jackpot', 'big_event_prestige', 'national_pride', 'club_fandom_rivalry', 'star_athlete_glamour',
            'expertise_prediction', 'humour_wordplay', 'street_youth_culture', 'play_games_collectibles', 'product_features', 'official_legitimacy',
            'tradition_heritage', 'creator_authenticity', 'strength_masculinity', 'sociability_community']
    head = ''.join(f'<th style="color:{COL[f]}">{f}</th>' for f in FIRMS)
    rows = []
    for c in cats:
        cells = []
        for f in FIRMS:
            v = dict(F[f]['borrowed']).get(c, 0)
            cells.append(f'<td style="background:rgba(30,40,70,{min(0.9, v*1.15):.2f});color:{"#fff" if v > 0.4 else "inherit"}">{P(v)}</td>')
        rows.append(f'<tr><th class="rl">{L(c)}</th>{"".join(cells)}</tr>')
    return f'<table class="heat"><tr><th></th>{head}</tr>{"".join(rows)}</table>'


def posmap():
    w, h = 560, 400
    parts = [f'<svg viewBox="0 0 {w} {h}" class="chart pos">',
             f'<line x1="50" y1="{h-40}" x2="{w-10}" y2="{h-40}" class="axis"/><line x1="50" y1="10" x2="50" y2="{h-40}" class="axis"/>',
             f'<text x="{(w+40)/2}" y="{h-8}" class="axl" text-anchor="middle">Deal-led → share of impressions framed as a low-risk deal or reward</text>',
             f'<text x="16" y="{(h-40)/2}" class="axl" text-anchor="middle" transform="rotate(-90 16 {(h-40)/2})">Culture-led → humour, street, games, expertise, stars</text>']
    for f in FIRMS:
        fr = dict(F[f]['framing'])
        x = fr.get('low_risk_trial_or_deal', 0) + fr.get('reward_or_money_making', 0)
        b = dict(F[f]['borrowed'])
        y = (b.get('humour_wordplay', 0) + b.get('street_youth_culture', 0) + b.get('play_games_collectibles', 0) + b.get('expertise_prediction', 0) + b.get('star_athlete_glamour', 0)) / 2
        cx, cy = 50 + x * (w - 70), (h - 40) - min(1, y) * (h - 60)
        r = 8 + 40 * (F[f]['impressions'] / TOTAL_IMP) ** 0.5
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{COL[f]}" fill-opacity=".75"/><text x="{cx:.0f}" y="{cy - r - 6:.0f}" text-anchor="middle" class="pl">{f}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def firm_section(f):
    d, p, c = F[f], PROFILE[f], COL[f]
    gender = dict(d['gender']); g = 'Men only' if gender.get('MALE', 0) > 0.9 else 'All genders' if gender.get('ALL', 0) > 0.9 else 'Mixed'
    age = d['age'][0][0].replace('–+', '+')
    ios = dict(d['os']).get('iOS', 0)
    cap = ' (capped at 1,000)' if d['ads'] == 1000 else ' (complete)'
    return f'''
<section class="firm" id="{f}">
 <div class="fh" style="border-color:{c}"><h2 style="color:{c}">{f}</h2><div class="role">{e(p["role"])}</div></div>
 <p class="thesis">{p["thesis"]}</p>
 <div class="kpis">
  <div><b>{d["ads"]:,}</b><span>ads{cap}</span></div>
  <div><b>{d["creatives"]}</b><span>unique creatives</span></div>
  <div><b>{M(d["impressions"])}</b><span>impressions · {P(d["impressions"]/TOTAL_IMP)} of panel</span></div>
  <div><b>{d["first"][:7]} → {d["last"][:7]}</b><span>launch window</span></div>
  <div><b>{d["active"]}</b><span>still active</span></div>
  <div><b>{g}</b><span>{age} · {P(ios)} iOS</span></div>
 </div>
 <div class="cols">
  <div class="col">
   <h3>What they did</h3><ul>{"".join(f"<li>{x}</li>" for x in p["what"])}</ul>
   <h3>Inferred philosophy</h3><p class="phil" style="border-color:{c}">{p["philosophy"]}</p>
   <h3>Competitive posture</h3><p>{p["watch"]}</p>
  </div>
  <div class="col side">
   <h4>Associations borrowed <small>(% of impressions, dominant or secondary)</small></h4>{bars(d["borrowed"], c)}
   <h4>How betting is framed</h4>{bars(d["framing"], c, 4)}
   <h4>Offer</h4>{bars(d["offer"], c, 4)}
   <h4>Sports</h4>{bars(d["sport"], c, 4)}
  </div>
 </div>
 <h3>Highest-reach creatives</h3><div class="crs">{creative_cards(d["top_creatives"], c)}</div>
</section>'''


def snapshot(key):
    title, body, read = SNAP_TEXT[key]
    s = D['snapshots'][key]
    cols = []
    for f in FIRMS:
        if f not in s:
            cols.append(f'<div class="sc empty"><h4 style="color:{COL[f]}">{f}</h4><p>No launches</p></div>')
            continue
        x = s[f]
        cols.append(f'''<div class="sc"><h4 style="color:{COL[f]}">{f}</h4><p class="sm">{x["ads"]} ads · {x["creatives"]} creatives · {M(x["impressions"])}</p>
<p class="sm">{" · ".join(L(k) for k, _ in x["borrowed"])}</p>{creative_cards(x["top"][:1], COL[f])}</div>''')
    return f'<div class="snap"><h3>{title}</h3><p>{body}</p><p class="read"><b>Read:</b> {read}</p><div class="sgrid">{"".join(cols)}</div></div>'


CSS = '''
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;color:#1d2433;background:#f6f7fb}
.wrap{max-width:1180px;margin:0 auto;padding:40px 32px 80px}
header{background:#111827;color:#f3f4f6;padding:56px 32px 44px}header .wrap{padding:0 32px}
header h1{font-size:34px;margin:0 0 8px;letter-spacing:-.02em}header p{color:#cbd5e1;max-width:820px;margin:6px 0}
.tag{display:inline-block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#93c5fd;margin-bottom:10px}
nav{position:sticky;top:0;background:#fff;border-bottom:1px solid #e5e7eb;z-index:5}nav .wrap{padding:10px 32px;display:flex;gap:18px;flex-wrap:wrap}
nav a{color:#374151;text-decoration:none;font-size:14px}nav a:hover{color:#111}
h2{font-size:26px;margin:0;letter-spacing:-.01em}h3{font-size:17px;margin:22px 0 8px}h4{font-size:13px;margin:16px 0 6px;color:#4b5563;text-transform:uppercase;letter-spacing:.04em}
h4 small{text-transform:none;letter-spacing:0;font-weight:400;color:#9ca3af}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:26px 28px;margin:22px 0}
.takeaways{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
.tk{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:16px 18px}.tk b{display:block;font-size:15px;margin-bottom:4px}
.tk span{color:#4b5563;font-size:14px}
table.ov{width:100%;border-collapse:collapse;font-size:14px}table.ov th,table.ov td{padding:9px 10px;border-bottom:1px solid #eef0f4;text-align:left;vertical-align:top}
table.ov th{font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.04em}
.chart{width:100%;height:auto}.ax{font-size:11px;fill:#6b7280}.grid{stroke:#e5e7eb}.axis{stroke:#9ca3af}.axl{font-size:12px;fill:#6b7280}.pl{font-size:13px;font-weight:600;fill:#1f2937}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;margin-top:6px}.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px}
table.heat{border-collapse:separate;border-spacing:3px;font-size:13px;width:100%}table.heat td{text-align:center;padding:6px 4px;border-radius:5px;min-width:70px}
table.heat th{font-size:12px;padding:4px}table.heat th.rl{text-align:right;font-weight:500;color:#374151;white-space:nowrap}
.two{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:start}
.firm{background:#fff;border:1px solid #e5e7eb;border-radius:16px;padding:28px 30px;margin:30px 0}
.fh{border-left:6px solid;padding-left:14px;margin-bottom:10px}.role{color:#6b7280;font-size:15px}
.thesis{font-size:17px;color:#111827;margin:10px 0 18px}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:8px}.kpis div{background:#f8fafc;border-radius:10px;padding:10px 12px}
.kpis b{display:block;font-size:17px}.kpis span{font-size:12px;color:#6b7280}
.cols{display:grid;grid-template-columns:1.25fr .75fr;gap:30px}.col ul{padding-left:18px;margin:0}.col li{margin:6px 0}
.phil{border-left:4px solid;padding:8px 14px;background:#fafafa;margin:0;font-style:italic}
.bar{display:grid;grid-template-columns:150px 1fr 40px;gap:8px;align-items:center;font-size:13px;margin:3px 0}
.bt{background:#f1f3f7;border-radius:4px;height:10px;overflow:hidden}.bt span{display:block;height:100%;border-radius:4px}.bv{text-align:right;color:#4b5563}
.crs{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}.cr{margin:0;font-size:12px;color:#374151}
.cr img{width:100%;border-radius:8px;border:1px solid #e5e7eb;aspect-ratio:9/16;object-fit:cover;background:#eee}
.cr .hl{font-style:italic}.cr .as{color:#6b7280}.noimg{aspect-ratio:9/16;background:#eee;border-radius:8px;display:grid;place-items:center;color:#999}
.snap{background:#fff;border:1px solid #e5e7eb;border-radius:16px;padding:24px 28px;margin:22px 0}.read{background:#f1f5ff;border-radius:8px;padding:8px 12px}
.sgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:12px}.sc h4{margin:0 0 4px;font-size:15px;text-transform:none;letter-spacing:0}
.sc .sm{font-size:12px;color:#6b7280;margin:2px 0}.sc.empty{opacity:.45}
.caveat li{margin:5px 0;color:#374151}footer{color:#9ca3af;font-size:12px;margin-top:30px}
@media(max-width:900px){.two,.cols{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}.crs,.sgrid{grid-template-columns:repeat(2,1fr)}}
'''

overview_rows = ''.join(
    f'<tr><td><b style="color:{COL[f]}">{f}</b></td><td>{e(PROFILE[f]["role"])}</td><td>{F[f]["ads"]:,} / {F[f]["creatives"]}</td>'
    f'<td>{M(F[f]["impressions"])} ({P(F[f]["impressions"]/TOTAL_IMP)})</td><td>{F[f]["first"][:7]} → {F[f]["last"][:7]}</td>'
    f'<td>{e(L(F[f]["borrowed"][0][0]))}, {e(L(F[f]["borrowed"][1][0]))}</td><td>{e(L(F[f]["offer"][0][0]))}</td></tr>' for f in FIRMS)

page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>French sports betting on Snapchat: competitor advertising landscape</title><style>{CSS}</style></head><body>
<header><div class="wrap"><div class="tag">Competitive landscape · Snapchat (EU DSA ad repository) · France</div>
<h1>Who is saying what: sports-betting advertising on Snapchat in France</h1>
<p>Five operators, 3,241 ads, 951 unique creatives and {M(TOTAL_IMP)} impressions, launched between January 2024 and October 2026. Every creative was coded for what it shows, what it associates the brand with, and how it frames betting.</p>
<p style="font-size:13px;color:#94a3b8">Labels are model-coded (Sonnet) and not yet validated against human coders. Strategy statements are inferences from the creative, not statements by the firms.</p></div></header>
<nav><div class="wrap"><a href="#summary">Summary</a><a href="#map">Positioning</a><a href="#timeline">Timeline</a><a href="#heat">Associations</a>{"".join(f'<a href="#{f}" style="color:{COL[f]}">{f}</a>' for f in FIRMS)}<a href="#snaps">Snapshots</a><a href="#caveats">Caveats</a></div></nav>
<div class="wrap">
<section id="summary"><h2>The lay of the land</h2>
<div class="takeaways" style="margin-top:16px">
 <div class="tk"><b>One dominant voice</b><span>Winamax delivers {P(F["Winamax"]["impressions"]/TOTAL_IMP)} of all impressions in the panel, largely through a handful of evergreen creatives that have run since mid-2024.</span></div>
 <div class="tk"><b>Two playbooks</b><span><i>Culture-led</i> (Winamax: humour, games, expertise, poker) versus <i>deal-led</i> (bet365, Betsson, Unibet: refunds, guarantees, free money). PMU sits between them with cash plus product breadth.</span></div>
 <div class="tk"><b>Risk reversal is table stakes for challengers</b><span>“Remboursé” or “garanti” appears in about 70% of bet365 and Betsson impressions, against 31% for Winamax, whose refund is pitched as <i>cash</i>, not freebets.</span></div>
 <div class="tk"><b>Football is shared; verticals differentiate</b><span>Everyone uses football. Poker (Winamax, PMU), horse racing (PMU), MMA (Unibet) and tennis (Betsson) are where brands carve out their own territory.</span></div>
 <div class="tk"><b>Events reshape the battlefield</b><span>In quiet months firms spread across niches; at the World Cup they converge on the same cue and compete through the hook, not the topic.</span></div>
 <div class="tk"><b>Targeting splits too</b><span>Winamax, Unibet and Betsson target men only, mostly 18–45. PMU and bet365 target all genders, 18+.</span></div>
</div>
<div class="card"><table class="ov"><tr><th>Brand</th><th>Role</th><th>Ads / creatives</th><th>Impressions</th><th>Launch window</th><th>Leading associations</th><th>Main offer</th></tr>{overview_rows}</table></div>
</section>
<section id="map" class="card"><div class="two"><div><h2>Positioning map</h2>{posmap()}</div>
<div><h3>How to read it</h3><p>Horizontal: how much of a brand’s exposure frames betting as a deal (refund, guarantee, bonus) or as a way to make money. Vertical: how much it borrows cultural meaning (humour, street culture, games, expertise, star athletes). Bubble size is total impressions.</p>
<p>Winamax sits highest on the culture axis and is the largest by far. bet365 is the most deal-led brand, with almost no cultural borrowing. Unibet and Betsson sit in between, leaning on deals with some club-fandom content. PMU scores low on both axes because its pitch is cash bonuses and product breadth (racing, poker, one app), which this map does not capture.</p></div></div></section>
<section id="timeline" class="card"><h2>When they advertised</h2><p>Impressions by the month each ad <i>launched</i>; Snapchat does not report end dates. Ads launched before September 2025 (mostly Winamax and Betsson evergreen creatives) are excluded from this chart.</p>
{timeline_svg()}<div class="legend">{"".join(f'<span><i style="background:{COL[f]}"></i>{f}</span>' for f in FIRMS)}</div></section>
<section id="heat" class="card"><h2>Association fingerprints</h2><p>Share of each brand’s impressions where a theme is dominant or clearly secondary. Read across a row to see who owns a theme.</p>{heatmap()}</section>
{"".join(firm_section(f) for f in FIRMS)}
<section id="snaps"><h2 style="margin-top:40px">Snapshots: who was launching what, side by side</h2>
<p>Ads grouped by launch month as a proxy for running concurrently. The thumbnail is each brand’s highest-reach creative launched that month.</p>
{snapshot("jan")}{snapshot("mar")}{snapshot("jun")}</section>
<section id="caveats" class="card caveat"><h2>Caveats</h2><ul>
<li><b>Coverage.</b> Winamax and Betsson are capped at their first 1,000 ads in the archive; PMU, Unibet and bet365 are complete. This is a targeted competitor panel, not a probability sample of French gambling advertising.</li>
<li><b>Timing.</b> Snapchat reports start dates but not end dates, so “concurrent” means launched in the same month. Impressions are lifetime totals, not reach or audience.</li>
<li><b>Measurement.</b> Labels are exploratory model codes (Sonnet via Claude Code, codebook v1.0.0) pending human validation. Videos were coded from 5 frames plus a local transcript.</li>
<li><b>Multi-image Story ads were coded from their first image.</b> Where that image is a logo card (for example, Winamax’s and Unibet’s highest-reach ads), associations are understated.</li>
<li><b>Interpretation.</b> Strategy statements are inferences from the creative and timing, not evidence of intent. Lead–lag patterns may reflect the shared sports calendar rather than responses to rivals.</li>
<li><b>Rights.</b> Creative thumbnails are reproduced for internal research review only.</li></ul></section>
<footer>Source: Snap Political & Advertising Ads Library (EU DSA), run 2026-10-21T005219Z; labels competitor_labels_v1; generated by betting-ads-research.</footer>
</div></body></html>'''
out = BASE / 'competitor_landscape.html'
out.write_text(page)
print(out, out.stat().st_size)

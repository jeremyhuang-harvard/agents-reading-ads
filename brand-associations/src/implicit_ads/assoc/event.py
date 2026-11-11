"""Event study of directed composition: how a campaign changes who is part of whom.

For one celebrity-brand event (config `events`), track over time:

  fwd(t) = share of the celebrity's news coverage that mentions the brand   (brand in celebrity)
  bwd(t) = share of the brand's news coverage that mentions the celebrity   (celebrity in brand)

from GDELT daily raw counts N_c(t), N_b(t), N_cb(t) (English sources), aggregated by week and by
pre/post period. These are population composition shares (the pi term of components.py). Also:

  * Google Trends related queries for each side, pre and post: the share of the brand's top related
    search weight that names the celebrity, and vice versa (directed composition of search behavior);
  * Google Trends daily interest for the brand, the celebrity+brand query, and the rivals
    (interference: did attention to the brand come with or at the expense of rivals?);
  * Wikipedia daily pageviews for both articles.

Writes data/derived/assoc/event_<id>_{weekly,periods,related,trends}.csv and output/assoc/event_<id>.png.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import date, timedelta
from urllib.parse import quote

from ..demo import http
from ..explore import trends as T
from . import measures  # noqa: F401  (kept for API symmetry)
from .config import DERIVED, OUTPUT, Frame
from .sources import gdelt, matcher
from .sources.trends_related import shares as related_shares

PAGEVIEWS = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
             "{title}/daily/{start}00/{end}00")


def gdelt_daily(query: str, start: str, end: str) -> dict[date, int]:
    data = gdelt._call(query, start, end, "timelinevolraw", timelinesmooth=0)
    out = {}
    for x in ((data.get("timeline") or [{}])[0].get("data", []) if "error" not in data else []):
        d = x["date"][:8]
        out[date(int(d[:4]), int(d[4:6]), int(d[6:8]))] = out.get(date(int(d[:4]), int(d[4:6]), int(d[6:8])), 0) + int(x["value"])
    if "error" in data:
        raise RuntimeError(f"GDELT error for {query}: {data['error']}")
    return out


def wiki_daily(title: str, start: str, end: str) -> dict[date, int]:
    s, e = start.replace("-", ""), end.replace("-", "")
    resp = http.get(PAGEVIEWS.format(title=quote(title, safe=""), start=s, end=e))
    if not resp.ok:
        return {}
    return {date(int(i["timestamp"][:4]), int(i["timestamp"][4:6]), int(i["timestamp"][6:8])): i["views"]
            for i in resp.json().get("items", [])}


def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def composition_by(keyfn, n_c, n_b, n_cb):
    agg = defaultdict(lambda: [0, 0, 0])
    for d in set(n_c) | set(n_b) | set(n_cb):
        k = keyfn(d)
        agg[k][0] += n_c.get(d, 0)
        agg[k][1] += n_b.get(d, 0)
        agg[k][2] += n_cb.get(d, 0)
    rows = []
    for k in sorted(agg):
        c, b, cb = agg[k]
        rows.append({"key": k, "n_celebrity": c, "n_brand": b, "n_joint": cb,
                     "fwd_brand_in_celebrity": cb / c if c else None, "bwd_celebrity_in_brand": cb / b if b else None})
    return rows


def run(frame: Frame, event_id: str, log=print) -> None:
    raw = json.loads(frame.path.read_text())
    ev = next(e for e in raw.get("events", []) if e["id"] == event_id)
    c, b = frame.get(ev["celebrity"]), frame.get(ev["brand"])
    rivals = [frame.get(r) for r in ev.get("rivals", [])]
    d0 = date.fromisoformat(ev["date"])
    start, end = ev["from"], ev["to"]
    DERIVED.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # 1. News composition (GDELT daily counts)
    n_c = gdelt_daily(c.gdelt, start, end)
    n_b = gdelt_daily(b.gdelt, start, end)
    n_cb = gdelt_daily(f"{c.gdelt} {b.gdelt}", start, end)
    rivals_n = {}
    for r in rivals:  # rivals are context, so a failed query is logged and skipped rather than fatal
        for key, q in ((r.id, r.gdelt), (f"{r.id}|{c.id}", f"{c.gdelt} {r.gdelt}")):
            try:
                rivals_n[key] = gdelt_daily(q, start, end)
            except RuntimeError as exc:
                log(f"[event] skipped {q}: {exc}")
                rivals_n[key] = {}
    weekly = composition_by(week_start, n_c, n_b, n_cb)
    for row in weekly:
        row["key"] = row["key"].isoformat()
        for r in rivals:
            row[f"n_{r.id}"] = sum(v for d, v in rivals_n[r.id].items() if week_start(d).isoformat() == row["key"])
    periods = composition_by(lambda d: "post" if d >= d0 else "pre", n_c, n_b, n_cb)
    _dump(DERIVED / f"event_{event_id}_weekly.csv", weekly)
    _dump(DERIVED / f"event_{event_id}_periods.csv", periods)
    for p in periods:
        log(f"[event] {p['key']}: N({c.name})={p['n_celebrity']} N({b.name})={p['n_brand']} N(both)={p['n_joint']} "
            f"| {b.name} in {c.name}: {p['fwd_brand_in_celebrity'] or 0:.4f}  {c.name} in {b.name}: {p['bwd_celebrity_in_brand'] or 0:.4f}")

    # 2. Search composition (Trends related queries, US), pre vs post
    pats = {e.id: matcher(e) for e in frame.entities}
    pre_w = (start, (d0 - timedelta(days=1)).isoformat())
    post_w = (d0.isoformat(), end)
    rel_rows = []
    for label, (s, e) in (("pre", pre_w), ("post", post_w)):
        for cue, tgt in ((c, b), (b, c)):
            try:
                top = T.related(cue.name, s, e).get("top", []) or []
            except Exception as exc:  # noqa: BLE001
                log(f"[event] related {cue.name} {label}: {exc}")
                top = []
            share = related_shares(top, [tgt], pats)[tgt.id]
            rel_rows.append({"period": label, "cue": cue.id, "target": tgt.id, "share_of_related_weight": round(share, 4),
                             "n_related": len(top), "top_related": " | ".join(f"{r['query']} ({r['value']})" for r in top[:8])})
            log(f"[event] related {label}: {tgt.name} in {cue.name}'s top searches = {share:.3f} ({len(top)} queries)")
    _dump(DERIVED / f"event_{event_id}_related.csv", rel_rows)

    # 3. Attention and interference (Trends daily interest, US), with Wikipedia pageviews
    trend_rivals = [frame.get(r) for r in ev.get("trend_rivals", ev.get("rivals", []))]
    terms = [b.name, f"{c.name} {b.name}", *[r.name for r in trend_rivals]][:5]
    tr = T.over_time(terms, start, end)
    _dump(DERIVED / f"event_{event_id}_trends.csv", tr)
    views = {e.id: wiki_daily(e.wiki, start, end) for e in [c, b, *trend_rivals] if e.wiki}
    _dump(DERIVED / f"event_{event_id}_pageviews.csv",
          [{"date": d.isoformat(), "entity": k, "views": v} for k, s in views.items() for d, v in sorted(s.items())])
    _figure(event_id, ev, c, b, rivals, weekly, tr, views, d0)
    log(f"[event] wrote event_{event_id}_*.csv and output/assoc/event_{event_id}.png")


def _dump(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _figure(event_id, ev, c, b, rivals, weekly, tr, views, d0):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    ax = axes[0]
    xs = [date.fromisoformat(r["key"]) for r in weekly]
    f = [r["fwd_brand_in_celebrity"] for r in weekly]
    g = [r["bwd_celebrity_in_brand"] for r in weekly]
    ax.plot(xs, [100 * v if v is not None else float("nan") for v in g], color="#B91C1C", lw=2.2, marker="o", ms=3,
            label=f"{c.name} in {b.name}'s coverage (% of {b.name} articles naming {c.name})")
    ax.plot(xs, [100 * v if v is not None else float("nan") for v in f], color="#1D4ED8", lw=2.2, marker="o", ms=3,
            label=f"{b.name} in {c.name}'s coverage (% of {c.name} articles naming {b.name})")
    ax.set_ylabel("% of weekly articles")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    ax.set_title("Who is part of whom: weekly composition of English-language news coverage (GDELT)", loc="left", fontsize=10, fontweight="bold")
    ax = axes[1]
    ax.bar(xs, [r["n_brand"] for r in weekly], width=5, color="#B91C1C", alpha=0.75, label=f"{b.name} articles")
    if not rivals:
        ax.bar(xs, [r["n_celebrity"] for r in weekly], width=2.5, color="#1D4ED8", alpha=0.85, label=f"{c.name} articles")
    for r, col in zip(rivals, ["#111827", "#6B7280", "#D1D5DB"]):
        ax.plot(xs, [w.get(f"n_{r.id}", 0) for w in weekly], color=col, lw=1.6, label=f"{r.name} articles")
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylabel("articles per week (log)")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left", ncol=2)
    ax.set_title(f"Weekly coverage volume: {b.name}" + (" vs rivals" if rivals else f" and {c.name}"), loc="left", fontsize=10, fontweight="bold")
    ax = axes[2]
    series = defaultdict(dict)
    for r in tr:
        series[r["term"]][date.fromisoformat(r["date"])] = r["value"]
    cols = ["#B91C1C", "#F59E0B", "#111827", "#6B7280", "#9CA3AF"]
    for (term, s), col in zip(series.items(), cols):
        pts = sorted(s.items())
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=1.4, label=term)
    ax.set_ylabel("Google Trends (US, same request)")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left", ncol=3)
    ax.set_title("Search attention (one Trends request, so lines share a scale)", loc="left", fontsize=10, fontweight="bold")
    for a in axes:
        a.axvline(d0, color="#7C3AED", ls="--", lw=1)
        a.grid(alpha=0.2)
    axes[0].annotate(f"campaign {d0:%b %-d}", (d0, axes[0].get_ylim()[1] * 0.92), color="#6D28D9", fontsize=8, xytext=(4, 0), textcoords="offset points")
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.suptitle(f"{c.name} × {b.name}", x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUTPUT / f"event_{event_id}.png", dpi=160)
    plt.close(fig)

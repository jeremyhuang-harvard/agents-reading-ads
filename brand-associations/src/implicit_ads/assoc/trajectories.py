"""Entity vectors over time: who moves toward whom when a celebrity wears or signs with a brand.

Each entity (celebrity or brand) gets an ML-style vector representation in each event window:
the mean of sentence-embedding vectors of its English-language news headlines in that window
(Sarkar, "Economic Representations": an object's representation is the average embedding of the
language written about it). For an event at day 0 with windows pre = [-90, -8], post = [0, 30],
late = [31, 90]:

    pull(c -> b) = cos(x_c^post, x_b^pre) - cos(x_c^pre, x_b^pre)
        how far the celebrity's representation moved toward the brand's (fixed, pre-event) position
    pull(b -> c) = cos(x_b^post, x_c^pre) - cos(x_b^pre, x_c^pre)
        how far the brand's representation moved toward the celebrity's pre-event position

Holding the target at its pre-event position separates *who moved*. Both pulls are differenced
against placebo targets (same-category brands for the celebrity, comparable celebrities for the
brand), which removes general drift such as a celebrity's coverage becoming more fashion-heavy:

    DiD(c -> b) = pull(c -> b) - mean_{b' in placebo brands} pull(c -> b')

Asymmetry = DiD(c -> b) - DiD(b -> c): positive when the celebrity absorbed the brand more than
the brand absorbed the celebrity (expected when the brand is large: Tate -> Adidas); negative when
the brand absorbed the celebrity (expected for a young brand: Novig -> Sweeney).

Two variants:
  names kept    literal co-mentions count (association includes "Tate McRae ... adidas" headlines)
  names masked  every frame/event entity name replaced by [NAME] before embedding, so movement
                reflects the *content* of coverage (sportswear, campaign, controversy), not the token.

Uncertainty: 300 bootstrap resamples of headlines within each entity-window.
"""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta

import numpy as np

from . import embed
from .config import DERIVED, OUTPUT, ROOT, Entity, Frame
from .sources import gdelt, matcher

EVENTS = ROOT / "config" / "assoc" / "events.json"
DATA_END = date(2026, 11, 8)
DOCS = DERIVED / "documents_events.jsonl"
B = 300


def load_events(frame: Frame, path=EVENTS) -> tuple[dict[str, Entity], list[dict], dict]:
    raw = json.loads(path.read_text())
    ents = {e.id: e for e in frame.entities}
    for x in raw["entities"]:
        ents[x["id"]] = Entity(x["id"], x["kind"], x["name"], x.get("wiki"), x.get("gdelt") or f'"{x["name"]}"', "",
                               tuple(x.get("match", ())))
    for ev in raw["events"]:
        for k in [ev["celebrity"], ev["brand"], *ev["placebo_brands"], *ev["placebo_celebrities"]]:
            if k not in ents:
                raise ValueError(f"event {ev['id']} references unknown entity {k}")
    return ents, raw["events"], raw["windows"]


def refine_date(ev: dict, c: Entity, b: Entity, log=print) -> date:
    if ev.get("date_precision") != "month":
        return date.fromisoformat(ev["date"])
    y, m = map(int, ev["date"].split("-"))
    start = date(y, m, 1)
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    data = gdelt._call(f"{c.gdelt} {b.gdelt}", start.isoformat(), end.isoformat(), "timelinevolraw", timelinesmooth=0)
    series = (data.get("timeline") or [{}])[0].get("data", []) if "error" not in data else []
    daily = {}
    for x in series:
        d = date(int(x["date"][:4]), int(x["date"][4:6]), int(x["date"][6:8]))
        daily[d] = daily.get(d, 0) + int(x["value"])
    if not daily or max(daily.values()) == 0:
        log(f"[traj] {ev['id']}: no joint coverage in {ev['date']}; using the 15th")
        return start.replace(day=15)
    peak = max(daily, key=daily.get)
    log(f"[traj] {ev['id']}: month-precision date refined to joint-coverage peak {peak} ({daily[peak]} articles)")
    return peak


def windows_for(d0: date, spec: dict) -> dict[str, tuple[date, date]]:
    out = {}
    for name, (a, z) in spec.items():
        s, e = d0 + timedelta(days=a), min(d0 + timedelta(days=z), DATA_END)
        if s <= e:
            out[name] = (s, e)
    return out


def collect(frame: Frame, per_window: int = 250, only: list[str] | None = None, log=print) -> None:
    ents, events, spec = load_events(frame)
    events = [e for e in events if not only or e["id"] in only]
    rows, meta = [], []
    for ev in events:
        c, b = ents[ev["celebrity"]], ents[ev["brand"]]
        d0 = refine_date(ev, c, b, log)
        wins = windows_for(d0, spec)
        meta.append({"event": ev["id"], "date_used": d0.isoformat(), "date_config": ev["date"],
                     "windows": {k: [s.isoformat(), e.isoformat()] for k, (s, e) in wins.items()}})
        jobs = [(c, w) for w in wins] + [(b, w) for w in wins]
        jobs += [(ents[p], "pre") for p in ev["placebo_brands"] + ev["placebo_celebrities"]]
        for ent, w in jobs:
            s, e = wins[w]
            data = gdelt._call(ent.gdelt, s.isoformat(), e.isoformat(), "artlist", maxrecords=per_window, sort="hybridrel")
            seen, n = set(), 0
            for art in data.get("articles", []) or []:
                t = (art.get("title") or "").strip()
                if len(t) < 20 or t.casefold() in seen:
                    continue
                seen.add(t.casefold())
                rows.append({"event": ev["id"], "entity": ent.id, "window": w, "date": art.get("seendate", "")[:8],
                             "domain": art.get("domain", ""), "url": art.get("url", ""), "text": t})
                n += 1
            log(f"[traj] {ev['id']} {ent.id} {w} {s}..{e}: {n} headlines {data.get('error', '')}")
        _write_jsonl(DOCS, rows)
        (DERIVED / "events_meta.json").write_text(json.dumps(meta, indent=2))
    log(f"[traj] wrote {len(rows)} headlines for {len(events)} events")


def _write_jsonl(path, rows):
    tmp = path.with_suffix(".tmp")
    with tmp.open("w") as h:
        for r in rows:
            h.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def _cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def pulls(X: dict, c: str, b: str, pb: list[str], pc: list[str]) -> dict:
    """X[(entity, window)] -> vector. Returns raw pulls, placebo means and DiDs (post and late)."""
    out = {}
    for w in ("post", "late"):
        if (c, w) not in X or (b, w) not in X:
            continue
        pull_cb = _cos(X[(c, w)], X[(b, "pre")]) - _cos(X[(c, "pre")], X[(b, "pre")])
        pull_bc = _cos(X[(b, w)], X[(c, "pre")]) - _cos(X[(b, "pre")], X[(c, "pre")])
        plc = [_cos(X[(c, w)], X[(p, "pre")]) - _cos(X[(c, "pre")], X[(p, "pre")]) for p in pb if (p, "pre") in X]
        plb = [_cos(X[(b, w)], X[(p, "pre")]) - _cos(X[(b, "pre")], X[(p, "pre")]) for p in pc if (p, "pre") in X]
        did_c = pull_cb - (np.mean(plc) if plc else 0.0)
        did_b = pull_bc - (np.mean(plb) if plb else 0.0)
        out.update({f"pull_c_to_b_{w}": pull_cb, f"pull_b_to_c_{w}": pull_bc, f"placebo_c_{w}": np.mean(plc) if plc else np.nan,
                    f"placebo_b_{w}": np.mean(plb) if plb else np.nan, f"did_c_to_b_{w}": did_c, f"did_b_to_c_{w}": did_b,
                    f"asym_{w}": did_c - did_b})
    return out


def analyze(frame: Frame, backend: str, mask: bool, log=print, seed: int = 20261110, only: list[str] | None = None) -> list[dict]:
    ents, events, _ = load_events(frame)
    events = [e for e in events if not only or e["id"] in only]
    docs = [json.loads(line) for line in DOCS.open()]
    enc = embed.Encoder(backend)
    pats = [matcher(e) for e in ents.values()]
    texts = [embed.mask_names(d["text"], pats) if mask else d["text"] for d in docs]
    E = enc.encode(texts)
    idx: dict[tuple, list[int]] = {}
    for i, d in enumerate(docs):
        idx.setdefault((d["event"], d["entity"], d["window"]), []).append(i)
    rng = np.random.default_rng(seed)
    meta = {m["event"]: m for m in json.loads((DERIVED / "events_meta.json").read_text())}
    out = []
    for ev in events:
        c, b = ev["celebrity"], ev["brand"]
        keys = {(ent, w): ix for (e_id, ent, w), ix in idx.items() if e_id == ev["id"]}
        if (c, "pre") not in keys or (b, "pre") not in keys or (c, "post") not in keys or (b, "post") not in keys:
            log(f"[traj] {ev['id']}: missing windows, skipped ({sorted(keys)})")
            continue
        X = {k: E[ix].mean(axis=0) for k, ix in keys.items()}
        est = pulls(X, c, b, ev["placebo_brands"], ev["placebo_celebrities"])
        boots = []
        for _ in range(B):
            Xb = {k: E[rng.choice(ix, size=len(ix), replace=True)].mean(axis=0) for k, ix in keys.items()}
            boots.append(pulls(Xb, c, b, ev["placebo_brands"], ev["placebo_celebrities"]))
        row = {"event": ev["id"], "type": ev["type"], "celebrity": c, "brand": b, "date": meta[ev["id"]]["date_used"],
               "backend": backend, "masked": mask}
        for k in sorted(set(keys)):
            row[f"n_{k[0] if k[0] in (c, b) else 'placebo:' + k[0]}_{k[1]}"] = len(keys[k])
        # composition shares in the post window (literal co-mentions), for comparison with vector pulls
        pc, pb = matcher(ents[c]), matcher(ents[b])
        post_c = [docs[i]["text"] for i in keys[(c, "post")]]
        post_b = [docs[i]["text"] for i in keys[(b, "post")]]
        row["share_c_post_mentioning_b"] = sum(bool(pb.search(t)) for t in post_c) / len(post_c)
        row["share_b_post_mentioning_c"] = sum(bool(pc.search(t)) for t in post_b) / len(post_b)
        for k, v in est.items():
            row[k] = round(float(v), 5)
            vals = np.array([bb[k] for bb in boots if k in bb], float)
            if len(vals):
                row[f"{k}_lo"], row[f"{k}_hi"] = (round(float(x), 5) for x in np.percentile(vals, [5, 95]))
        out.append(row)
        log(f"[traj] {ev['id']} ({'masked' if mask else 'names'}): c->b {est.get('did_c_to_b_post', np.nan):+.4f}  "
            f"b->c {est.get('did_b_to_c_post', np.nan):+.4f}  asym {est.get('asym_post', np.nan):+.4f}")
    name = f"trajectories_{embed.slug(backend)}{'_masked' if mask else ''}.csv"
    _dump(DERIVED / name, out)
    return out


def _dump(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


TYPE_COLOR = {"wear": "#1D4ED8", "collab": "#7C3AED", "ambassador": "#B91C1C", "campaign": "#F59E0B", "campaign_equity": "#111827"}


def figure(frame: Frame, results: dict[str, list[dict]], backend: str, window: str = "post") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ents, _, _ = load_events(frame)
    fig, axes = plt.subplots(1, len(results), figsize=(7.2 * len(results), 6.6), squeeze=False)
    for ax, (label, rows) in zip(axes[0], results.items()):
        xs, ys = [], []
        for r in rows:
            x, y = r.get(f"did_b_to_c_{window}"), r.get(f"did_c_to_b_{window}")
            if x is None or y is None or np.isnan(x) or np.isnan(y):
                continue
            col = TYPE_COLOR.get(r["type"], "#6B7280")
            ax.errorbar(x, y, xerr=[[x - r[f"did_b_to_c_{window}_lo"]], [r[f"did_b_to_c_{window}_hi"] - x]],
                        yerr=[[y - r[f"did_c_to_b_{window}_lo"]], [r[f"did_c_to_b_{window}_hi"] - y]],
                        fmt="o", color=col, ms=6, elinewidth=0.8, capsize=0)
            ax.annotate(f"{ents[r['celebrity']].name} × {ents[r['brand']].name}", (x, y), fontsize=7, xytext=(4, 3), textcoords="offset points")
            xs.append(x)
            ys.append(y)
        lim = max([abs(v) for v in xs + ys] + [0.01]) * 1.15
        ax.plot([-lim, lim], [-lim, lim], color="black", lw=0.7, ls="--")
        ax.axhline(0, color="#9CA3AF", lw=0.6)
        ax.axvline(0, color="#9CA3AF", lw=0.6)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_xlabel("brand's vector moved toward the celebrity  →\n(Δ cosine vs pre-event position, minus placebo celebrities)")
        ax.set_ylabel("celebrity's vector moved toward the brand  →\n(Δ cosine, minus placebo brands)")
        ax.set_title(label, loc="left", fontsize=10, fontweight="bold")
        ax.text(0.02, 0.97, "above the dashed line: celebrity absorbed the brand\nbelow: brand absorbed the celebrity",
                transform=ax.transAxes, fontsize=8, va="top", color="#374151")
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=t) for t, c in TYPE_COLOR.items()]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize=8.5)
    fig.suptitle(f"Who moved toward whom after the event (days 0–30 vs days −90…−8); encoder {backend}; bars = 90% bootstrap",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / f"trajectories_{embed.slug(backend)}_{window}.png", dpi=160)
    plt.close(fig)


def run(frame: Frame, backends: list[str], collect_docs: bool = True, only: list[str] | None = None, log=print) -> None:
    if collect_docs or not DOCS.exists():
        collect(frame, only=only, log=log)
    for backend in backends:
        res = {"names kept": analyze(frame, backend, mask=False, log=log, only=only),
               "names masked (content only)": analyze(frame, backend, mask=True, log=log, only=only)}
        for w in ("post", "late"):
            figure(frame, res, backend, w)


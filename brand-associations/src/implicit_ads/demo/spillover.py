"""Spillover analysis: focal product vs same-brand siblings vs competitors.

Four observed channels, each compared on the same event clock:

1. Search attention (Google Trends). Within each payload group, every term is
   on the same 0–100 scale. For each term we build a day-of-week baseline from
   days −28..−1 and report the *standardized abnormal attention* over days 0..7
   (mean excess over the weekday baseline divided by the SD of pre-period
   residuals), plus the focal term's share of total group attention before and
   after. A focal share that rises while siblings/competitors stay flat is a
   selective (low-interference) response; parallel rises are category or
   brand halo.
2. Encyclopedic attention (Wikipedia pageviews) for brand pages.
3. Inventory (archived product pages): did same-model colorways also go out
   of stock, or only the focal one?
4. Coverage co-mentions: what share of post-appearance articles about the
   focal product also name sibling or competitor products?

All quantities are descriptive; none is a causal estimate.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from datetime import date

from .config import DERIVED_DIR, OUTPUT_DIR

PRE = (-28, -1)
ACUTE = (0, 3)   # acute shock window: appearances are evening events, so day +1 is often the peak
POST = (0, 7)
LATE = (8, 21)
# Newsletter sign-ups, tag lists and category menus that name every major brand.
BOILERPLATE = r"[^.]{0,200}(newsletter|sign up|tags?:|filed under|categor(y|ies):|related stories)[^.]{0,300}"
ROLE_COLORS = {
    "focal": "#DC2626", "focal_link": "#DC2626", "focal_brand": "#DC2626",
    "sibling": "#2563EB", "sibling_link": "#2563EB",
    "competitor": "#6B7280", "competitor_link": "#6B7280", "competitor_brand": "#6B7280",
    "category": "#D97706", "generic_link": "#9CA3AF", "celebrity": "#7C3AED",
}


def _read(name):
    path = DERIVED_DIR / name
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def daily_z(series: list[tuple[int, str, float]], smooth: int = 3) -> dict:
    """Per-day standardized deviation from the weekday baseline (days −28..−1).

    z_t = (value_t − mean of the same weekday in the pre-period) / SD of pre-period
    residuals. A centered rolling mean of `smooth` days damps Google's sampling
    noise. Returns {"z": {day: z}, "sparse": bool}; sparse series (≥50% zero
    days before the event, or a flat pre-period) are flagged because their z is fragile.
    """
    series = sorted(series)
    pre = [(d, dt, v) for d, dt, v in series if PRE[0] <= d <= PRE[1]]
    if len(pre) < 14:
        return {"z": {}, "sparse": True}
    by_dow = defaultdict(list)
    for _, dt, v in pre:
        by_dow[date.fromisoformat(dt).weekday()].append(v)
    pre_mean = statistics.fmean(v for *_, v in pre)
    base = {k: statistics.fmean(v) for k, v in by_dow.items()}
    resid = [v - base[date.fromisoformat(dt).weekday()] for _, dt, v in pre]
    # Trends values are integers, so residual variation below one index point is not
    # meaningful; the floor also lets series that start from zero (e.g. "Outland Denim")
    # be shown instead of dropped.
    sd = max(statistics.pstdev(resid), 1.0)
    zero_share = sum(1 for *_, v in pre if v == 0) / len(pre)
    raw = {d: (v - base.get(date.fromisoformat(dt).weekday(), pre_mean)) / sd for d, dt, v in series}
    half = smooth // 2
    z = {}
    for d in raw:
        # Never average across the event: pre-event days use only pre-event values.
        window = [raw[k] for k in range(d - half, d + half + 1) if k in raw and (k < 0) == (d < 0)]
        z[d] = statistics.fmean(window)
    return {"z": z, "sparse": zero_share >= 0.5 or pre_mean < 3}


def term_series(case: dict, trends: list[dict]) -> list[dict]:
    """One series per distinct (term, geo), first query group wins, with its role."""
    roles = case.get("roles", {})
    geo = {g["name"]: g.get("geo", "") for g in case.get("trends") or []}
    order = [g["name"] for g in case.get("trends") or []]
    multi_geo = len(set(geo.values())) > 1
    raw = defaultdict(list)
    for t in trends:
        if t["case_id"] == case["case_id"]:
            raw[(t["group"], t["term"])].append((int(t["relative_day"]), t["date"], float(t["value"])))
    out, seen = [], set()
    for (group, term) in sorted(raw, key=lambda k: order.index(k[0]) if k[0] in order else 99):
        key = (term, geo.get(group, ""))
        if key in seen:
            continue
        seen.add(key)
        res = daily_z(raw[(group, term)])
        out.append({"term": term, "label": f"{term} ({key[1]})" if multi_geo else term, "group": group,
                    "role": roles.get(term, "unassigned"), **res})
    return out


ROLE_FAMILY = {
    "focal": "focal", "focal_link": "focal", "focal_brand": "focal",
    "sibling": "sibling", "sibling_link": "sibling",
    "competitor": "competitor", "competitor_link": "competitor", "competitor_brand": "competitor",
    "category": "category", "generic_link": "category", "celebrity": "category",
}
FAMILY_ORDER = ["focal", "sibling", "competitor", "category"]
FAMILY_TITLE = {"focal": "Focal", "sibling": "Same-brand siblings", "competitor": "Competitors / rival links",
                "category": "Category / generic"}


def heatmap_figure(case: dict, trends: list[dict], path, lo: int = -21, hi: int = 35) -> None:
    """Rows = search terms grouped focal / sibling / competitor; columns = days; color = z."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    rows = [r for r in term_series(case, trends) if r["z"]]
    rows.sort(key=lambda r: (FAMILY_ORDER.index(ROLE_FAMILY.get(r["role"], "category")),
                             r["sparse"], -max((r["z"].get(d, 0) for d in range(0, 8)), default=0)))
    if not rows:
        return
    days = list(range(lo, hi + 1))
    grid = [[r["z"].get(d, float("nan")) for d in days] for r in rows]
    fig, ax = plt.subplots(figsize=(12, 0.36 * len(rows) + 1.9))
    im = ax.imshow(grid, aspect="auto", cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-6, vcenter=0, vmax=6),
                   extent=(lo - 0.5, hi + 0.5, len(rows) - 0.5, -0.5), interpolation="nearest")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["label"] + ("  ·sparse" if r["sparse"] else "") for r in rows], fontsize=8)
    prev = None
    for i, r in enumerate(rows):
        fam = ROLE_FAMILY.get(r["role"], "category")
        tick = ax.get_yticklabels()[i]
        tick.set_color({"focal": "#B91C1C", "sibling": "#1D4ED8", "competitor": "#374151"}.get(fam, "#92400E"))
        if r["sparse"]:
            tick.set_alpha(0.55)
        if prev is not None and fam != prev:
            ax.axhline(i - 0.5, color="black", lw=1.2)
        prev = fam
    ax.axvline(-0.5, color="black", lw=1, ls="--")
    for ev in case.get("other_events", []):
        ax.axvline(ev["day"] - 0.5, color="#7C3AED", lw=1, ls=":")
        ax.annotate(ev["label"], (ev["day"] - 0.3, len(rows) - 0.5), xytext=(3, -3), textcoords="offset points",
                    fontsize=7, color="#5B21B6", va="bottom", ha="left" if ev["day"] < 20 else "right",
                    bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.85})
    ax.set_xlabel(f"Days relative to appearance ({case['event_date']})")
    cb = fig.colorbar(im, ax=ax, pad=0.01, fraction=0.03)
    cb.set_label("SDs vs pre-period (weekday-adjusted; capped at ±6)", fontsize=8)
    ax.set_title(f"{case.get('short_label', case['label'])}: search attention relative to each term's own pre-period",
                 loc="left", fontsize=10, fontweight="bold")
    fig.text(0.01, 0.005, "White = no change; red = above normal; blue = below normal (possible substitution). "
             "3-day centered average (never across day 0).\nRow labels: red = focal, blue = same-brand sibling, grey = competitor. "
             "'sparse' = mostly zero days before the event, so its z is fragile. Purple dotted = other appearances.",
             fontsize=7, color="#4B5563")
    fig.tight_layout(rect=(0, 0.045, 1, 0.97))
    fig.savefig(path, dpi=170)
    plt.close(fig)


def abnormal(series: list[tuple[int, str, float]]) -> dict:
    """series: (relative_day, iso_date, value). Returns abnormal-attention stats."""
    pre = [(d, dt, v) for d, dt, v in series if PRE[0] <= d <= PRE[1]]
    if len(pre) < 14:
        return {}
    by_dow = defaultdict(list)
    for _, dt, v in pre:
        by_dow[date.fromisoformat(dt).weekday()].append(v)
    pre_mean = statistics.fmean(v for _, _, v in pre)
    base = {k: statistics.fmean(v) for k, v in by_dow.items()}

    def expected(dt):
        return base.get(date.fromisoformat(dt).weekday(), pre_mean)

    resid = [v - expected(dt) for _, dt, v in pre]
    sd = statistics.pstdev(resid) or None
    acute = [(d, dt, v) for d, dt, v in series if ACUTE[0] <= d <= ACUTE[1]]
    acute_excess = statistics.fmean(v - expected(dt) for _, dt, v in acute) if acute else None
    post = [(d, dt, v) for d, dt, v in series if POST[0] <= d <= POST[1]]
    late = [(d, dt, v) for d, dt, v in series if LATE[0] <= d <= LATE[1]]
    excess = statistics.fmean(v - expected(dt) for _, dt, v in post) if post else None
    late_excess = statistics.fmean(v - expected(dt) for _, dt, v in late) if late else None
    peak = max(post, key=lambda x: x[2]) if post else None
    return {
        "pre_mean": round(pre_mean, 2),
        "pre_zero_share": round(sum(1 for *_, v in pre if v == 0) / len(pre), 2),
        "excess_0_3": round(acute_excess, 2) if acute_excess is not None else None,
        "z_0_3": round(acute_excess / sd, 2) if (acute_excess is not None and sd) else None,
        "post_mean": round(statistics.fmean(v for *_, v in post), 2) if post else None,
        "excess_0_7": round(excess, 2) if excess is not None else None,
        "z_0_7": round(excess / sd, 2) if (excess is not None and sd) else None,
        "excess_8_21": round(late_excess, 2) if late_excess is not None else None,
        "z_8_21": round(late_excess / sd, 2) if (late_excess is not None and sd) else None,
        "ratio_0_7": round(statistics.fmean(v for *_, v in post) / pre_mean, 2) if (post and pre_mean > 0) else None,
        "peak_day": peak[0] if peak else None,
        "peak_value": peak[2] if peak else None,
    }


def attention_table(cases, trends, pageviews):
    rows = []
    for case in cases:
        roles = case.get("roles", {})
        cid = case["case_id"]
        groups = defaultdict(lambda: defaultdict(list))
        for t in trends:
            if t["case_id"] == cid:
                groups[t["group"]][t["term"]].append((int(t["relative_day"]), t["date"], float(t["value"])))
        for group, terms in groups.items():
            # focal share of total group attention
            totals_pre = defaultdict(float)
            totals_post = defaultdict(float)
            for term, series in terms.items():
                for d, _, v in series:
                    if PRE[0] <= d <= PRE[1]:
                        totals_pre[term] += v
                    if POST[0] <= d <= POST[1]:
                        totals_post[term] += v
            gp, gq = sum(totals_pre.values()), sum(totals_post.values())
            for term, series in terms.items():
                stats = abnormal(sorted(series))
                rows.append({
                    "case_id": cid, "source": "google_trends", "group": group, "term": term,
                    "role": roles.get(term, "unassigned"), **stats,
                    "share_pre": round(totals_pre[term] / gp, 3) if gp else None,
                    "share_0_7": round(totals_post[term] / gq, 3) if gq else None,
                })
        pv = defaultdict(list)
        for p in pageviews:
            if p["case_id"] == cid:
                pv[p["article"]].append((int(p["relative_day"]), p["date"], float(p["views"])))
        for article, series in pv.items():
            rows.append({"case_id": cid, "source": "wikipedia_pageviews", "group": "brand_pages", "term": article,
                         "role": roles.get(article, "unassigned"), **abnormal(sorted(series)),
                         "share_pre": None, "share_0_7": None})
    return rows


def inventory_table(cases, snapshots):
    rows = []
    for case in cases:
        cid = case["case_id"]
        focal = case["focal"].get("sku")
        by_key = defaultdict(list)
        for s in snapshots:
            if s["case_id"] == cid and not s.get("error") and s.get("page_status") not in ("unknown", "", None):
                if s["product_key"].startswith("/"):
                    continue
                by_key[s["product_key"]].append(s)
        for key, snaps in by_key.items():
            snaps.sort(key=lambda s: s["capture"])
            pre = [s for s in snaps if int(s["relative_day"]) < 0]
            post = [s for s in snaps if 0 <= int(s["relative_day"]) <= 21]

            def label(s):
                if s.get("sizes_total") not in ("", None, "0"):
                    return f"{s['page_status']} {s['sizes_available']}/{s['sizes_total']}"
                return s["page_status"]

            def oos(s):
                if s.get("sizes_total") not in ("", None, "0"):
                    return int(s["sizes_available"]) / int(s["sizes_total"]) < 0.5
                return s["page_status"] in {"out_of_stock", "OutOfStock"}

            rows.append({
                "case_id": cid, "product_key": key, "role": "focal" if key == focal else "sibling",
                "n_pre": len(pre), "n_post_0_21": len(post),
                "last_pre": f"d{pre[-1]['relative_day']}: {label(pre[-1])}" if pre else "",
                "post_0_21": "; ".join(f"d{s['relative_day']}: {label(s)}" for s in post),
                "any_depleted_post": any(oos(s) for s in post) if post else "",
                "any_depleted_pre": any(oos(s) for s in pre) if pre else "",
            })
    return rows


def mentions_table(cases, coverage):
    import re

    from .coverage import TEXT_DIR, context_windows

    rows = []
    for case in cases:
        cid = case["case_id"]
        # On-topic (celebrity within 500 chars of the product), post-event, one copy per headline.
        arts, seen = [], set()
        for a in coverage:
            if (a["case_id"] == cid and a.get("on_topic_rule") == "True"
                    and a.get("relative_day") not in ("", None) and 0 <= int(a["relative_day"]) <= 60
                    and a.get("dup_key") not in seen):
                seen.add(a.get("dup_key"))
                arts.append(a)
        texts = []
        for a in arts:
            path = TEXT_DIR / f"{a['text_sha256'][:24]}.txt"
            body = path.read_text(encoding="utf-8") if path.exists() else ""
            body = re.sub(BOILERPLATE, " ", body, flags=re.I)
            # Only text near the focal mention counts: sneaker sites carry brand names in
            # navigation, tag clouds and related-story sidebars on every page.
            texts.append(" ".join(context_windows(body, case["identification"], width=400, limit=8)).lower())
        n = len(texts)
        for role, terms in case.get("mentions", {}).items():
            for label, pattern in terms.items():
                hits = sum(1 for t in texts if re.search(pattern, t, re.I))
                rows.append({"case_id": cid, "role": role, "term": label, "articles": hits, "of": n,
                             "share": round(hits / n, 3) if n else None})
    return rows


def llm_products_table(cases, coverage, llm):
    """Tally other products Qwen extracted from on-topic articles (model_predicted)."""
    import ast

    by_url = {r["url"]: r for r in llm}
    rows = []
    for case in cases:
        cid = case["case_id"]
        counts: dict[str, int] = defaultdict(int)
        n, seen = 0, set()
        for a in coverage:
            q = by_url.get(a["url"])
            if (a["case_id"] != cid or not q or a.get("dup_key") in seen
                    or str(q.get("about_focal_appearance")).lower() != "true"):
                continue
            seen.add(a.get("dup_key"))
            n += 1
            try:
                items = ast.literal_eval(q.get("other_products") or "[]")
            except (ValueError, SyntaxError):
                items = []
            for item in {str(i).strip().lower() for i in items if str(i).strip()}:
                counts[item] += 1
        for item, k in sorted(counts.items(), key=lambda kv: -kv[1]):
            rows.append({"case_id": cid, "product": item, "articles": k, "of": n,
                         "epistemic_status": "model_predicted"})
    return rows


def figure(case, attn, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in attn if r["case_id"] == case["case_id"] and r.get("z_0_3") not in (None, "")]
    if not rows:
        return
    rows.sort(key=lambda r: (r["source"], r["group"], -float(r["z_0_3"])))
    labels = [f"{r['term']}  [{r['group']}]" for r in rows]
    vals = [float(r["z_0_3"]) for r in rows]
    late = [float(r["z_0_7"]) if r.get("z_0_7") not in (None, "") else 0 for r in rows]
    colors = [ROLE_COLORS.get(r["role"], "#9CA3AF") for r in rows]
    fig, ax = plt.subplots(figsize=(10, 0.42 * len(rows) + 1.6))
    y = range(len(rows))
    ax.barh(y, vals, color=colors, height=0.6, label="days 0–3")
    ax.scatter(late, y, color="black", marker="|", s=120, zorder=3, label="days 0–7")
    ax.axvline(0, color="black", lw=0.8)
    ax.axvline(2, color="#9CA3AF", lw=0.8, ls=":")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Standardized abnormal attention (excess over weekday baseline ÷ pre-period SD)")
    ax.set_title(f"{case['label']}: focal vs sibling vs competitor attention", loc="left", fontsize=11, fontweight="bold")
    from matplotlib.patches import Patch

    handles = [Patch(color=ROLE_COLORS["focal"], label="focal"), Patch(color=ROLE_COLORS["sibling"], label="same-brand sibling"),
               Patch(color=ROLE_COLORS["competitor"], label="competitor"), Patch(color=ROLE_COLORS["category"], label="category")]
    ax.legend(handles=handles, fontsize=8, loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


ROLE_ORDER = ["focal_link", "competitor_link", "sibling_link", "generic_link", "focal", "sibling", "competitor", "category"]
ROLE_LABEL = {
    "focal_link": "celebrity + focal brand", "competitor_link": "celebrity + rival brand",
    "sibling_link": "other celebrity + focal brand", "generic_link": "celebrity + 'shoes'",
    "focal": "focal product / brand", "sibling": "same-brand sibling", "competitor": "competitor",
    "category": "category",
}


def overview_figure(cases, attn, path, case_ids):
    """One panel per case: Google Trends abnormal attention by role, days 0–3."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    chosen = [c for c in cases if c["case_id"] in case_ids]
    ncols = 2
    nrows = (len(chosen) + 1) // 2
    fig, grid = plt.subplots(nrows, ncols, figsize=(13, 4.6 * nrows))
    axes = list(getattr(grid, "flat", [grid]))
    for ax in axes[len(chosen):]:
        ax.axis("off")
    for ax, case in zip(axes, chosen):
        geo = {g["name"]: g.get("geo", "") for g in case.get("trends") or []}
        multi_geo = len(set(geo.values())) > 1
        seen, rows = set(), []
        for r in attn:
            key = (r["term"], geo.get(r["group"], ""))
            if r["case_id"] != case["case_id"] or r["source"] != "google_trends" or key in seen:
                continue
            if r["role"] not in ROLE_ORDER:
                continue
            seen.add(key)
            rows.append({**r, "label": f"{r['term']} ({key[1]})" if multi_geo else r["term"]})
        rows.sort(key=lambda r: (ROLE_ORDER.index(r["role"]), -(float(r["z_0_3"]) if r.get("z_0_3") not in (None, "") else 99)))
        y = list(range(len(rows)))
        for i, r in enumerate(rows):
            color = ROLE_COLORS.get(r["role"], "#9CA3AF")
            z = r.get("z_0_3")
            # Sparse series (mostly zeros at Google's privacy threshold) give fragile z-scores.
            low = (r.get("pre_mean") not in (None, "") and float(r["pre_mean"]) < 3) or \
                (r.get("pre_zero_share") not in (None, "") and float(r["pre_zero_share"]) >= 0.5)
            if z in (None, ""):
                peak = r.get("peak_value")
                ax.annotate(f"from 0 → {int(float(peak))}" if peak not in (None, "") and float(peak) > 0 else "no data",
                            (0.3, i), va="center", fontsize=8, color=color, fontweight="bold")
                continue
            ax.barh(i, min(float(z), 12), color=color, height=0.62, hatch="///" if low else None,
                    edgecolor="white" if low else color)
            if float(z) > 12:
                ax.annotate(f"{float(z):.0f}", (12, i), va="center", fontsize=7)
        ax.set_yticks(y)
        ax.set_yticklabels([r["label"] for r in rows], fontsize=8)
        ax.invert_yaxis()
        ax.axvline(0, color="black", lw=0.8)
        ax.axvline(2, color="#9CA3AF", lw=0.8, ls=":")
        ax.set_xlim(-3, 12.5)
        ax.set_title(case.get("short_label", case["label"]), fontsize=10, fontweight="bold", loc="left")
        ax.grid(axis="x", alpha=0.2)
        ax.set_xlabel("Abnormal search, days 0–3 (z)", fontsize=8)
    handles = [Patch(color=ROLE_COLORS[k], label=v) for k, v in
               [("focal", "focal (celebrity link, product, brand)"), ("sibling", "same-brand sibling"),
                ("competitor", "competitor / rival link"), ("category", "category")]]
    handles.append(Patch(facecolor="#9CA3AF", hatch="///", edgecolor="white", label="sparse / low volume (≥50% zero days before)"))
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=9, frameon=False)
    fig.suptitle("Where did the search attention go? Excess over weekday baseline, in pre-period SDs "
                 "(dotted line = 2 SD). Google Trends; terms within a query group share one scale.",
                 fontsize=9, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(path, dpi=170)
    plt.close(fig)


def inventory_figure(cases, snapshots, path, case_ids, window=(-10, 21)):
    """Archived product-page status by colorway: focal vs same-model siblings."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_id = {c["case_id"]: c for c in cases}
    chosen = [by_id[i] for i in case_ids if i in by_id]
    fig, axes = plt.subplots(1, len(chosen), figsize=(6.5 * len(chosen), 5.2))
    if len(chosen) == 1:
        axes = [axes]
    cmap = plt.get_cmap("RdYlGn")
    for ax, case in zip(axes, chosen):
        focal = case["focal"].get("sku")
        pts = defaultdict(list)
        for s in snapshots:
            if (s["case_id"] != case["case_id"] or s.get("error") or s["product_key"].startswith("/")
                    or s.get("page_status") in ("unknown", "", None)):
                continue
            d = int(s["relative_day"])
            if window[0] <= d <= window[1]:
                pts[s["product_key"]].append((d, s))
        keys = sorted(pts, key=lambda k: (k != focal, k))
        keys = [k for k in keys if k == focal or len(pts[k]) >= 1][:16]
        for i, k in enumerate(keys):
            last_label, last_day, flip = None, -999, False
            for d, s in sorted(pts[k], key=lambda x: x[0]):
                if s.get("sizes_total") not in ("", None, "0"):
                    share = int(s["sizes_available"]) / int(s["sizes_total"])
                    color = cmap(share)
                    label = f"{s['sizes_available']}/{s['sizes_total']}"
                else:
                    share = 0.0 if s["page_status"] in ("out_of_stock", "OutOfStock") else 1.0
                    color = "#DC2626" if share == 0 else ("#F59E0B" if s["page_status"] == "coming_soon" else "#16A34A")
                    label = "OOS" if share == 0 else ""
                ax.scatter(d, i, s=120 if k == focal else 70, color=color, edgecolor="black", lw=0.6, zorder=3)
                if label and label != last_label and (k == focal or share < 0.5):
                    flip = (d - last_day <= 2) and not flip
                    ax.annotate(label, (d, i), xytext=(0, -13 if flip else 8), textcoords="offset points",
                                ha="center", fontsize=7)
                    last_day = d
                last_label = label
        ax.axvline(0, color="black", lw=1)
        ax.set_yticks(range(len(keys)))
        ax.set_yticklabels([f"{k}  (worn)" if k == focal else k for k in keys], fontsize=8)
        for t in ax.get_yticklabels():
            if t.get_text().endswith("(worn)"):
                t.set_fontweight("bold")
                t.set_color("#DC2626")
        ax.invert_yaxis()
        ax.set_xlim(window[0] - 1, window[1] + 1)
        ax.set_xlabel("Days since appearance (archived capture dates)", fontsize=8)
        ax.set_title(case.get("short_label", case["label"]), fontsize=10, fontweight="bold", loc="left")
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle("Did sibling colorways sell out too? Wayback captures of the brand's product pages. "
                 "Green = in stock / full size run, red = out of stock / few sizes; labels = sizes available.",
                 fontsize=9, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=170)
    plt.close(fig)


def _write(path, rows):
    fields = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["case_id"])
        writer.writeheader()
        writer.writerows(rows)


def run(cases, log=print):
    trends = _read("trends_daily.csv")
    attn = attention_table(cases, trends, _read("pageviews_daily.csv"))
    inv = inventory_table(cases, _read("archive_snapshots.csv"))
    men = mentions_table(cases, _read("coverage_articles.csv"))
    llm_rows = llm_products_table(cases, _read("coverage_articles.csv"), _read("coverage_llm_labels.csv"))
    _write(DERIVED_DIR / "spillover_attention.csv", attn)
    _write(DERIVED_DIR / "spillover_inventory.csv", inv)
    _write(DERIVED_DIR / "spillover_mentions.csv", men)
    _write(DERIVED_DIR / "spillover_llm_products.csv", llm_rows)
    for case in cases:
        figure(case, attn, OUTPUT_DIR / f"{case['case_id']}_spillover.png")
        heatmap_figure(case, trends, OUTPUT_DIR / f"{case['case_id']}_attention_heatmap.png")
    overview_figure(cases, attn, OUTPUT_DIR / "spillover_overview.png",
                    ["taylor_nb550", "kanye_energy_boost", "meghan_outland", "bieber_crocs"])
    inventory_figure(cases, _read("archive_snapshots.csv"), OUTPUT_DIR / "spillover_inventory.png",
                     ["kanye_energy_boost", "taylor_nb550"])
    log(f"[spillover] attention rows {len(attn)}, inventory rows {len(inv)}, mention rows {len(men)}")

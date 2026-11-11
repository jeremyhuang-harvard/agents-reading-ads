"""Assemble per-case timelines, figures and a chain-coverage summary."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date

from .config import DERIVED_DIR, OUTPUT_DIR

LEVEL_ORDER = ["celebrity_only", "brand", "model", "exact"]
COLORS = {"celebrity_only": "#CBD5E1", "brand": "#93C5FD", "model": "#3B82F6", "exact": "#1E3A8A"}


def _read(name: str) -> list[dict]:
    path = DERIVED_DIR / name
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _rel(day: str, event: date) -> int | None:
    try:
        return (date.fromisoformat(day[:10]) - event).days
    except ValueError:
        return None


def timeline(case: dict, data: dict) -> list[dict]:
    cid, event = case["case_id"], date.fromisoformat(case["event_date"])
    rows = [
        {"relative_day": "", "date": "", "stage": "relationship", "event": case["relationship"]["status"],
         "detail": case["relationship"]["detail"], "status": "reported", "source": ";".join(case["relationship"]["sources"])},
        {"relative_day": 0, "date": case["event_date"], "stage": "appearance", "event": case["event_label"],
         "detail": case.get("event_time") or "", "status": "reported", "source": ""},
    ]
    # Only post-appearance coverage can identify the appearance; earlier articles
    # about the same celebrity/brand (e.g. a 2012 endorsement) are excluded.
    arts = [
        a for a in data["coverage"]
        if a["case_id"] == cid and a.get("published") and a.get("on_topic_rule") == "True"
        and a.get("relative_day") not in ("", None) and 0 <= int(a["relative_day"]) <= 60
    ]
    arts.sort(key=lambda a: a["published"])
    for level in ["brand", "model", "exact"]:
        hit = next((a for a in arts if LEVEL_ORDER.index(a["id_level"]) >= LEVEL_ORDER.index(level)), None)
        if hit:
            rows.append({"relative_day": _rel(hit["published"], event), "date": hit["published"], "stage": "identification",
                         "event": f"first {level}-level identification", "detail": f"{hit['domain']}: {hit['title'][:120]}",
                         "status": "observed", "source": hit["url"]})
    for flag, label in [("n_retail_links", "first article with retail link"), ("n_affiliate_links", "first article with affiliate link")]:
        hit = next((a for a in arts if a.get(flag) not in ("", "0", None)), None)
        if hit:
            rows.append({"relative_day": _rel(hit["published"], event), "date": hit["published"], "stage": "amplification",
                         "event": label, "detail": hit["domain"], "status": "observed", "source": hit["url"]})
    hit = next((a for a in arts if a.get("mentions_sellout_or_restock") == "True"), None)
    if hit:
        rows.append({"relative_day": _rel(hit["published"], event), "date": hit["published"], "stage": "market_response",
                     "event": "first article mentioning sellout/restock", "detail": hit["domain"], "status": "observed", "source": hit["url"]})
    actors = Counter(a["actor_type"] for a in arts)
    if arts:
        rows.append({"relative_day": "", "date": "", "stage": "amplification", "event": f"{len(arts)} on-topic articles coded",
                     "detail": "; ".join(f"{k}={v}" for k, v in actors.most_common()), "status": "observed", "source": ""})

    for group in {(t["group"], t["term"]) for t in data["trends"] if t["case_id"] == cid}:
        series = [t for t in data["trends"] if t["case_id"] == cid and (t["group"], t["term"]) == group]
        window = [t for t in series if -3 <= int(t["relative_day"]) <= 14]
        if window:
            peak = max(window, key=lambda t: int(t["value"]))
            pre = [int(t["value"]) for t in series if -28 <= int(t["relative_day"]) <= -1]
            base = sum(pre) / len(pre) if pre else 0
            rows.append({"relative_day": int(peak["relative_day"]), "date": peak["date"], "stage": "attention",
                         "event": f"Trends peak (−3..+14): {group[1]}", "detail": f"peak {peak['value']} vs pre-28d mean {base:.1f} ({group[0]})",
                         "status": "observed", "source": "Google Trends"})

    snaps = [
        s for s in data["snapshots"]
        if s["case_id"] == cid and s.get("is_focal") == "True" and not s.get("error")
        and not (s.get("page_status") == "unknown" and not s.get("sizes_total"))
    ]
    for s in sorted(snaps, key=lambda s: s["capture"]):
        avail = f"{s['sizes_available']}/{s['sizes_total']} sizes" if s.get("sizes_total") else ""
        rows.append({"relative_day": int(s["relative_day"]), "date": s["capture_date"], "stage": "market_response",
                     "event": f"product page: {s['page_status']}", "detail": " ".join(x for x in [avail, f"price {s['list_price']}" if s.get('list_price') else "", f"countdown {s['countdown_days']}d" if s.get('countdown_days') else ""] if x),
                     "status": "observed", "source": s["archive_url"]})
    tagged = [c for c in data["captures"] if c["case_id"] == cid and c.get("commerce_channel")]
    for channel in sorted({c["commerce_channel"] for c in tagged}):
        sub = sorted((c for c in tagged if c["commerce_channel"] == channel), key=lambda c: c["capture"])
        partners = sorted({c["commerce_partner"] for c in sub if c["commerce_partner"]})
        rows.append({"relative_day": "", "date": f"{sub[0]['capture_date']}..{sub[-1]['capture_date']}", "stage": "amplification",
                     "event": f"{len(sub)} archived product URLs with {channel} tracking", "detail": "; ".join(partners[:8]),
                     "status": "observed", "source": "Wayback CDX"})
    for out in case.get("reported_outcomes", []):
        rows.append({"relative_day": "", "date": "", "stage": "market_response", "event": out["metric"],
                     "detail": f"{out['value']} ({out['window']}; {out['provenance']})", "status": "reported", "source": out["source"]})
    for row in rows:
        row["case_id"] = cid
    order = {"relationship": 0, "appearance": 1, "identification": 2, "amplification": 3, "attention": 4, "market_response": 5}
    rows.sort(key=lambda r: (order[r["stage"]], r["relative_day"] if isinstance(r["relative_day"], int) else 999))
    return rows


FAMILY_STYLE = {
    # family: (palette, linestyle, linewidth)
    "focal": (["#B91C1C", "#EF4444", "#7F1D1D"], "-", 2.6),
    "sibling": (["#1D4ED8", "#60A5FA", "#1E3A8A", "#0EA5E9", "#6366F1"], "-", 1.5),
    "competitor": (["#111827", "#6B7280", "#9CA3AF", "#374151", "#4B5563"], "--", 1.3),
    "category": (["#B45309", "#D97706"], ":", 1.3),
}


def _attention_z_panel(ax, case, trends, lo, hi, cap=(-5, 14)) -> None:
    """Search attention as SDs from each term's own weekday-adjusted pre-period."""
    from .spillover import FAMILY_ORDER, ROLE_FAMILY, term_series

    rows = [r for r in term_series(case, trends) if r["z"]]
    rows.sort(key=lambda r: (FAMILY_ORDER.index(ROLE_FAMILY.get(r["role"], "category")), r["sparse"]))
    ax.axhspan(-2, 2, color="#E5E7EB", alpha=0.6, lw=0, zorder=0)
    ax.axhline(0, color="black", lw=0.8, label="_zero")
    used = defaultdict(int)
    ends = []
    top, bottom = 3.0, -3.0
    for r in rows:
        fam = ROLE_FAMILY.get(r["role"], "category")
        palette, ls, lw = FAMILY_STYLE[fam]
        color = palette[used[fam] % len(palette)]
        used[fam] += 1
        pts = sorted((d, z) for d, z in r["z"].items() if lo <= d <= hi)
        xs, ys = [d for d, _ in pts], [max(cap[0], min(cap[1], z)) for _, z in pts]
        # Sparse series (mostly zeros pre-event) are drawn thin and faded: direction is informative, size is not.
        prefix = {"focal": "FOCAL · ", "sibling": "SIBLING · ", "competitor": "RIVAL · "}.get(fam, "OTHER · ")
        ax.plot(xs, ys, color=color, ls=ls, lw=lw * (0.7 if r["sparse"] else 1), alpha=0.45 if r["sparse"] else 1,
                zorder=3 if fam == "focal" else 2, label=prefix + r["label"] + (" (sparse)" if r["sparse"] else ""))
        top = max(top, max(ys, default=0))
        bottom = min(bottom, min(ys, default=0))
    handles = [h for h in ax.get_lines() if h.get_label() and not h.get_label().startswith("_")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7, frameon=False,
              handlelength=2.6, borderaxespad=0)
    ax.set_ylim(bottom - 0.8, top + 1.2)
    for ev in case.get("other_events", []):
        if lo <= ev["day"] <= hi:
            ax.axvline(ev["day"], color="#7C3AED", lw=1, ls=":", label="_event")
            ax.annotate(ev["label"], (ev["day"] + 0.3, ax.get_ylim()[1]), xytext=(0, -10), textcoords="offset points",
                        fontsize=7, color="#6D28D9", va="top")
    ax.set_ylabel("SDs vs pre-period")
    ax.set_title("Attention: Google Trends, standard deviations from each term's own pre-period "
                 "(weekday-adjusted, 3-day avg; grey band = ±2)", loc="left", fontsize=10, fontweight="bold")
    ax.text(0.01, 0.03, "Faded = sparse series (mostly zero days before): direction informative, size not", transform=ax.transAxes,
            fontsize=6.5, color="#4B5563")


def figure(case: dict, data: dict, path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cid, event = case["case_id"], date.fromisoformat(case["event_date"])
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True, gridspec_kw={"height_ratios": [1, 1.5, 1]})
    lo, hi = -21, 35

    ax = axes[0]
    arts = [a for a in data["coverage"] if a["case_id"] == cid and a.get("relative_day") not in ("", None) and a.get("on_topic_rule") == "True"]
    counts = defaultdict(Counter)
    for a in arts:
        counts[int(a["relative_day"])][a["id_level"]] += 1
    days = list(range(lo, hi + 1))
    bottom = [0] * len(days)
    for level in LEVEL_ORDER:
        vals = [counts[d][level] for d in days]
        if any(vals):
            ax.bar(days, vals, bottom=bottom, color=COLORS[level], label=level, width=0.85)
            bottom = [b + v for b, v in zip(bottom, vals)]
    vol = [v for v in data["volume"] if v["case_id"] == cid]
    if vol:
        twin = ax.twinx()
        pts = sorted((_rel(v["date"], event), float(v["value"])) for v in vol if v.get("value") not in ("", None))
        pts = [p for p in pts if p[0] is not None and lo <= p[0] <= hi]
        if pts:
            twin.plot([p[0] for p in pts], [p[1] for p in pts], color="#F59E0B", lw=1.5, label="GDELT articles/day")
            twin.set_ylabel("GDELT volume", color="#B45309")
    ax.set_ylabel("Coded articles")
    ax.set_title("Identification & amplification: coded coverage by identification level", loc="left", fontsize=10, fontweight="bold")
    if arts:
        ax.legend(fontsize=7, loc="upper right")

    ax = axes[1]
    _attention_z_panel(ax, case, data["trends"], lo, hi)

    ax = axes[2]
    snaps = [s for s in data["snapshots"] if s["case_id"] == cid and not s.get("error") and s.get("relative_day")]
    focal = [s for s in snaps if s.get("is_focal") == "True"]
    others = [s for s in snaps if s.get("is_focal") != "True"]
    def share(s):
        if s.get("sizes_total") and s["sizes_total"] not in ("", "0"):
            return int(s["sizes_available"]) / int(s["sizes_total"])
        return {"in_stock": 1.0, "InStock": 1.0, "coming_soon": 0.0, "out_of_stock": 0.0, "OutOfStock": 0.0}.get(s.get("page_status"), None)
    for group, color, label in [(others, "#94A3B8", "sibling products"), (focal, "#DC2626", "focal product")]:
        pts = [(int(s["relative_day"]), share(s)) for s in group if share(s) is not None and lo - 120 <= int(s["relative_day"]) <= hi]
        pts = [p for p in pts if lo <= p[0] <= hi]
        if pts:
            ax.scatter([p[0] for p in pts], [p[1] for p in pts], color=color, s=28, label=label, zorder=3)
    ax.set_ylim(-0.05, 1.1)
    ax.set_ylabel("Share of sizes\navailable / in stock")
    ax.set_title("Market response: archived product-page availability (inventory, not sales)", loc="left", fontsize=10, fontweight="bold")
    if snaps:
        ax.legend(fontsize=7, loc="lower right")
    ax.set_xlabel(f"Days relative to appearance ({case['event_date']})")
    for a in axes:
        a.axvline(0, color="#DC2626", ls="--", lw=1)
        a.set_xlim(lo - 0.5, hi + 0.5)
        a.grid(axis="y", alpha=0.2)
    fig.suptitle(case["label"], fontsize=14, fontweight="bold", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 0.83, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chain_summary(case: dict, data: dict) -> dict:
    cid = case["case_id"]
    arts = [a for a in data["coverage"] if a["case_id"] == cid and a.get("fetch_source") != "failed"]
    rel = [a for a in arts if a.get("on_topic_rule") == "True"]
    snaps = [s for s in data["snapshots"] if s["case_id"] == cid and not s.get("error")]
    focal = [s for s in snaps if s.get("is_focal") == "True"]
    tagged = [c for c in data["captures"] if c["case_id"] == cid and c.get("commerce_channel")]
    return {
        "case": case["label"],
        "role": case["role"],
        "relationship": case["relationship"]["status"],
        "articles_coded": len(arts),
        "relevant_articles": len(rel),
        "exact_id_articles": sum(a["id_level"] == "exact" for a in rel),
        "articles_with_retail_links": sum(a.get("n_retail_links") not in ("", "0") for a in rel),
        "trends_series": len({(t["group"], t["term"]) for t in data["trends"] if t["case_id"] == cid}),
        "gdelt_days": len({v["date"] for v in data["volume"] if v["case_id"] == cid}),
        "page_snapshots": len(snaps),
        "focal_snapshots": len(focal),
        "focal_pre": sum(int(s["relative_day"]) < 0 for s in focal),
        "focal_post": sum(int(s["relative_day"]) >= 0 for s in focal),
        "tracked_commerce_urls": len(tagged),
        "reported_outcomes": len(case.get("reported_outcomes", [])),
    }


def run(cases: list[dict], log=print) -> None:
    data = {
        "coverage": _read("coverage_articles.csv"),
        "volume": _read("gdelt_volume_daily.csv"),
        "trends": _read("trends_daily.csv"),
        "snapshots": _read("archive_snapshots.csv"),
        "captures": _read("archive_captures.csv"),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows, summaries = [], []
    for case in cases:
        rows = timeline(case, data)
        all_rows += rows
        figure(case, data, OUTPUT_DIR / f"{case['case_id']}_chain.png")
        summaries.append(chain_summary(case, data))
        log(f"[build] {case['case_id']}: {len(rows)} timeline rows")
    fields = ["case_id", "stage", "relative_day", "date", "event", "detail", "status", "source"]
    with (OUTPUT_DIR / "timelines.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    lines = ["# Demo chain coverage summary", "", "Generated by `make demo`. `observed` = retrieved by the pipeline; `reported` = company/press claim.", ""]
    keys = list(summaries[0].keys()) if summaries else []
    lines.append("| " + " | ".join(keys) + " |")
    lines.append("|" + "---|" * len(keys))
    for s in summaries:
        lines.append("| " + " | ".join(str(s[k]) for k in keys) + " |")
    lines.append("")
    for case in cases:
        lines += ["", f"## {case['label']}", "", "| day | stage | event | detail | status |", "|---|---|---|---|---|"]
        for r in (r for r in all_rows if r["case_id"] == case["case_id"]):
            detail = str(r["detail"]).replace("|", "/")[:160]
            lines.append(f"| {r['relative_day']} | {r['stage']} | {r['event']} | {detail} | {r['status']} |")
    (OUTPUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

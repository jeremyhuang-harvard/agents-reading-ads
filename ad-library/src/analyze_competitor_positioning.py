#!/usr/bin/env python3
"""Join ad records to creative labels and summarise firm positioning and time cross-sections.

Writes ad_label_panel.jsonl (one row per ad) and analysis_summary.json to --out.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

FIRM = {"Winamax": "Winamax", "PMU": "PMU", "Kindred London Ltd": "Unibet", "Betsson France SA": "Betsson", "bet365": "bet365"}


def load(args):
    labels = {}
    man = json.loads((args.labels / "manifest.json").read_text())
    sha_by_id = {i["coding_id"]: i["sha256"] for i in man["items"]}
    for line in (args.labels / "results.jsonl").open():
        r = json.loads(line)
        if r["status"] == "ok":
            labels[sha_by_id[r["coding_id"]]] = r["labels"] | {"_coding_id": r["coding_id"]}
    first_snap = {}
    for line in (args.backfill / "records.jsonl").open():
        r = json.loads(line)
        if r.get("sha256"):
            first_snap.setdefault(r["ad_id"], (r["snap_index"], r["sha256"]))
            if r["snap_index"] < first_snap[r["ad_id"]][0]:
                first_snap[r["ad_id"]] = (r["snap_index"], r["sha256"])
    rows = []
    for line in (args.run / "records.jsonl").open():
        r = json.loads(line)
        ad = r["ad"]
        sha = (r.get("media") or {}).get("sha256") or first_snap.get(ad["id"], (None, None))[1]
        lab = labels.get(sha)
        rows.append({
            "ad_id": ad["id"], "firm": FIRM[r["query_advertiser"].strip()], "start": ad["start_date"][:10],
            "status": ad.get("status"), "impressions": ad.get("impressions_total") or 0,
            "ad_type": ad.get("ad_type"), "headline": ad.get("headline"), "campaign_name": ad.get("name"),
            "sha256": sha, "coding_id": lab and lab["_coding_id"], "labelled": lab is not None,
            "borrowed": {k: v["prominence"] for k, v in lab["borrowed_meaning"].items()} if lab else None,
            "framing": lab and lab["primary_framing"], "offer_type": lab and lab["offer"]["type"],
            "offer_eur": lab and lab["offer"].get("amount_eur"), "risk_free_language": lab and lab["offer"].get("guaranteed_or_risk_free_language"),
            "sports": lab and lab["sports"], "competition_level": lab and lab["competition_level"],
            "template": lab and lab["template"], "most_prominent": lab and lab["most_prominent_element"],
            "teams": lab and lab["entities"].get("teams_or_national_sides"), "events": lab and lab["entities"].get("competitions_or_events"),
            "intended_association": lab and lab["intended_association"], "tone": lab and lab["tone"],
        })
    return rows


def profile(rows, weight):
    """Share of ads (or impressions) with each feature; borrowed meaning counted at prominence >= 2."""
    tot = sum(weight(r) for r in rows) or 1
    out = {"n_ads": len(rows), "n_creatives": len({r["sha256"] for r in rows}), "impressions": sum(r["impressions"] for r in rows)}
    bm = collections.Counter()
    cats = collections.defaultdict(collections.Counter)
    for r in rows:
        w = weight(r)
        for k, v in r["borrowed"].items():
            if v >= 2:
                bm[k] += w
        for f in ("framing", "offer_type", "template", "most_prominent", "competition_level"):
            cats[f][r[f]] += w
        for s in r["sports"]:
            cats["sport"][s] += w
        cats["risk_free_language"][bool(r["risk_free_language"])] += w
    out["borrowed_ge2"] = {k: round(v / tot, 3) for k, v in bm.most_common()}
    out.update({f: {k: round(v / tot, 3) for k, v in c.most_common(6)} for f, c in cats.items()})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--backfill", type=Path, required=True)
    ap.add_argument("--labels", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rows = load(a)
    with (a.out / "ad_label_panel.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    lab = [r for r in rows if r["labelled"]]
    summary = {"ads": len(rows), "labelled_ads": len(lab), "status": dict(collections.Counter(r["status"] for r in rows)), "firms": {}}
    months = collections.defaultdict(collections.Counter)
    for r in rows:
        months[r["start"][:7]][r["firm"]] += 1
    summary["launches_by_month"] = {m: dict(c) for m, c in sorted(months.items())}
    for firm in FIRM.values():
        fr = [r for r in lab if r["firm"] == firm]
        summary["firms"][firm] = {
            "all_time_by_ads": profile(fr, lambda r: 1),
            "all_time_by_impressions": profile(fr, lambda r: r["impressions"]),
            "active_now": profile([r for r in fr if r["status"] == "ACTIVE"], lambda r: 1) if any(r["status"] == "ACTIVE" for r in fr) else None,
            "first_start": min(r["start"] for r in fr), "last_start": max(r["start"] for r in fr),
        }
    (a.out / "analysis_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print(json.dumps({k: summary[k] for k in ("ads", "labelled_ads", "status")}))


if __name__ == "__main__":
    main()

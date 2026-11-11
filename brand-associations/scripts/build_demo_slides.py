"""Insert demo-result slides into the presentation deck.

Usage:
    uv run --with python-pptx python scripts/build_demo_slides.py

Reads output/presentation/implicit_ads_tomorrow_brief.pptx (original, untouched)
and output/demo/*.png + data/derived/demo/*.csv, and writes
output/presentation/implicit_ads_tomorrow_brief_v2.pptx.
"""

from __future__ import annotations

import copy
import csv
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "presentation" / "implicit_ads_tomorrow_brief.pptx"
DST = ROOT / "output" / "presentation" / "implicit_ads_tomorrow_brief_v2.pptx"
FIG = ROOT / "output" / "demo"
DER = ROOT / "data" / "derived" / "demo"

INK = RGBColor(0x11, 0x18, 0x27)
MUTED = RGBColor(0x4B, 0x55, 0x63)
RED = RGBColor(0xDC, 0x26, 0x26)
PANEL = RGBColor(0xF1, 0xF5, 0xF9)


def text_box(slide, left, top, width, height, paragraphs, fill=None):
    """paragraphs: list of (text, size, bold, color)."""
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    if fill is not None:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    tf = shape.text_frame
    tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0.12))
    for i, (text, size, bold, color) in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
    return shape


def header(slide, title, kicker):
    text_box(slide, 0.5, 0.25, 12.3, 0.45, [(kicker.upper(), 12, True, RED)])
    text_box(slide, 0.5, 0.6, 12.3, 0.7, [(title, 26, True, INK)])


def footer(slide, text):
    text_box(slide, 0.5, 7.0, 12.3, 0.35, [(text, 9, False, MUTED)])


def picture(slide, path, left, top, width=None, height=None):
    kwargs = {}
    if width:
        kwargs["width"] = Inches(width)
    if height:
        kwargs["height"] = Inches(height)
    return slide.shapes.add_picture(str(path), Inches(left), Inches(top), **kwargs)


def bullets_panel(slide, left, top, width, height, title, items):
    paras = [(title, 14, True, INK)] + [(f"• {t}", 12, False, INK) for t in items]
    text_box(slide, left, top, width, height, paras, fill=PANEL)


def read(name):
    with (DER / name).open(encoding="utf-8") as h:
        return list(csv.DictReader(h))


def table(slide, left, top, width, rows, col_widths, size=11):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(left), Inches(top), Inches(width),
                                   Inches(0.38 * len(rows)))
    tbl = shape.table
    for c, w in enumerate(col_widths):
        tbl.columns[c].width = Inches(w)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = str(val)
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(size)
                    run.font.bold = r == 0
    return shape


def build():
    prs = Presentation(str(SRC))
    blank = prs.slide_layouts[6]
    new = []

    # 1. What the pipeline collected
    s = prs.slides.add_slide(blank)
    header(s, "One cached pipeline traces each case end to end", "Demo: what we collected")
    arts = read("coverage_articles.csv")
    snaps = read("archive_snapshots.csv")
    trends = read("trends_daily.csv")
    rows = [["Case", "Articles coded", "On-topic (unique)", "Product-page snapshots", "Search series"]]
    labels = {"taylor_nb550": "Taylor × NB 550", "kanye_energy_boost": "Kanye × Energy Boost ESM",
              "meghan_outland": "Meghan × Outland Harriet", "kanye_ultraboost": "Kanye × Ultra Boost (benchmark)",
              "bieber_crocs": "Bieber × Crocs (benchmark)"}
    for cid, label in labels.items():
        a = [x for x in arts if x["case_id"] == cid and x.get("text_sha256")]
        on = [x for x in a if x.get("on_topic_rule") == "True" and x["relative_day"] and 0 <= int(x["relative_day"]) <= 60]
        rows.append([label, len(a), f"{len(on)} ({len({x['dup_key'] for x in on})})",
                     sum(1 for x in snaps if x["case_id"] == cid and not x.get("error")),
                     len({(t["group"], t["term"]) for t in trends if t["case_id"] == cid})])
    table(s, 0.5, 1.5, 7.6, rows, [2.6, 1.15, 1.4, 1.35, 1.1])
    bullets_panel(s, 8.4, 1.5, 4.4, 5.2, "Sources (all public, cached once)", [
        "Wayback captures of brand product pages → stock, sizes, price",
        "Wayback URLs with affiliate / email tracking → shopping-link circulation",
        "Google Trends (focal vs sibling vs competitor) and Wikipedia pageviews",
        "Article discovery via seeds, Wayback and GDELT; rule coding + local Qwen",
        "No paid APIs; reruns read the disk cache (~20 s)",
    ])
    footer(s, "On-topic = celebrity named within 500 characters of the product, published days 0–60; unique = one per headline.")
    new.append(s)

    # 2–4. Case chains
    cases = [
        ("kanye_energy_boost", "Kanye × Energy Boost ESM: the worn colorway sold out on adidas.com",
         ["Specialist press identified the exact shoe on day +1",
          "Adidas page: in stock through day +5, out of stock days +6 to +10",
          "Search for 'Energy Boost' 3.8 SD above baseline over days 0–7",
          "eBay asks reached $1,000; top completed sale $153 (reported)"]),
        ("taylor_nb550", "Taylor × New Balance 550: a spike in the celebrity–brand search",
         ["'Taylor Swift New Balance' rose from ~1 to 100 by day +2",
          "Generic '550' search bumped only Monday–Tuesday",
          "10 archived 550 URLs carry affiliate or NB email tracking",
          "Reported: traffic +30%, units +22%, revenue +25% (NB to Complex)"]),
        ("meghan_outland", "Meghan × Outland: same-day identification, heavy syndication",
         ["Australian press named the brand on day 0; 'black Harriet' soon after",
          "AU search for 'Outland Denim' went from 0 to 100 on day 0",
          "93 on-topic articles but only 12 distinct headlines (syndication)",
          "Product page: 5 of 26 sizes on day +1, restored by preorder by day +4"]),
    ]
    for cid, title, items in cases:
        s = prs.slides.add_slide(blank)
        header(s, title, "Demo: case chain")
        picture(s, FIG / f"{cid}_chain.png", 0.45, 1.4, height=5.55)
        bullets_panel(s, 7.45, 1.5, 5.4, 4.6, "What the data show", items)
        footer(s, "Observed unless marked reported. Wayback captures are irregular; in-stock status is inventory, not sales.")
        new.append(s)

    # 5. Spillover: search
    s = prs.slides.add_slide(blank)
    header(s, "Attention went to the celebrity–brand link, not to rivals", "Spillover: search")
    picture(s, FIG / "spillover_overview.png", 0.4, 1.35, height=5.6)
    bullets_panel(s, 8.5, 1.45, 4.35, 5.4, "Pattern across cases", [
        "Celebrity + brand searches jumped 11+ SD (Taylor, Bieber)",
        "Generic model searches barely moved (NB 550: 1.1 SD)",
        "No competitor product search cleared 2 SD; only the rival-link search 'Taylor Swift Nike' did (2.7)",
        "Same-brand spillover went to the nearest sibling: NB 327; Ultra Boost (confounded by Kanye's own Ultra Boost appearance)",
        "Meghan: AU 'Outland' 0 → 100; AU rival denim flat",
    ])
    footer(s, "z = mean excess over a weekday baseline (days −28 to −1) ÷ SD of pre-period residuals. Sibling/competitor sets chosen after first look; freeze them for the real study.")
    new.append(s)

    # 6. Spillover: inventory
    s = prs.slides.add_slide(blank)
    header(s, "Only the worn colorway sold out; siblings stayed in stock", "Spillover: inventory")
    picture(s, FIG / "spillover_inventory.png", 0.45, 1.4, width=12.4)
    text_box(s, 0.5, 6.4, 12.3, 0.6, [(
        "Kanye: B44283 out of stock days +6 to +10 while four other Energy Boost colorways were in stock on days +6 to +17. "
        "Taylor: no pre-event capture of BB550SE1; sibling 550s mostly full size runs (BB550LSB was already half depleted).",
        12, False, INK)])
    footer(s, "Source: Wayback Machine raw captures of adidas.com and newbalance.com product pages, parsed for availability and sizes.")
    new.append(s)

    # 7. Validation
    s = prs.slides.add_slide(blank)
    header(s, "Article coding validated against held-out hand labels", "Measurement check")
    scores = [r for r in read("validation_scores.csv") if r["split"] == "heldout" and r["coder"] != "rule_v2_and_qwen_v2"]
    names = {"rule_v1_cooccurrence": "Rule v1: whole-page co-mention", "rule_v2_proximity": "Rule v2: celebrity ≤500 chars from product",
             "qwen_v2": "Local Qwen3-8B (excerpt prompt)"}
    rows = [["Coder (is the article about this appearance?)", "Precision", "Recall", "Accuracy"]]
    rows += [[names[r["coder"]], r["precision"], r["recall"], r["accuracy"]] for r in scores]
    table(s, 0.5, 1.5, 7.9, rows, [4.6, 1.1, 1.1, 1.1], size=12)
    bullets_panel(s, 8.7, 1.5, 4.1, 5.0, "Takeaways", [
        "Rule v2 is the primary coder (0.91 accuracy)",
        "Qwen: no false positives, misses ~1 in 4 → use as a strict filter",
        "Fixed: 'Outland' matched 'Outlander'; sneaker-site sidebars",
        "243 articles labeled locally in ~8 minutes",
        "Gold labels need a human spot-check",
    ])
    footer(s, "Held-out sample: 32 articles drawn after the rule change. Gold labels coded by the assistant from excerpts.")
    new.append(s)

    # Reorder: insert the new slides after slide index 2; drop the old 'presentation plan' slide (index 4).
    sld_ids = prs.slides._sldIdLst
    ids = list(sld_ids)
    original, added = ids[: len(ids) - len(new)], ids[len(ids) - len(new):]
    plan_slide = original[4]
    order = original[:3] + added + [x for x in original[3:] if x is not plan_slide]
    for el in ids:
        sld_ids.remove(el)
    for el in order:
        sld_ids.append(el)
    # Remove the dropped slide's relationship so it is not packaged.
    prs.part.drop_rel(plan_slide.rId)
    prs.save(str(DST))
    print(DST, len(prs.slides._sldIdLst), "slides")


if __name__ == "__main__":
    build()

"""The saved data must reproduce the numbers we report, and the release must stay clean.

Standard library + pytest. Run with `make test` (or `uv run --group dev pytest -q`).
"""

import csv
import fnmatch
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("make_results", ROOT / "analysis" / "make_results.py")
assert spec is not None and spec.loader is not None
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)

BUILD = mr.build()


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def two(x: float) -> str:
    return f"{x:+.2f}"


# ----------------------------------------------------------------------------- agent-feeds

def test_batch1_measurement_problem():
    rows = {r["question"]: r for r in BUILD["b1_scale"]}
    assert (rows["better off"]["mean_normal_scale"], rows["better off"]["mean_reversed_scale_after_recoding"]) == (1.76, 4.03)
    assert BUILD["b1_behaviour"] == {"feeds": 568, "share_p_spend_gt_0.1": 0.065, "share_p_show_gt_0.1": 0.005}


def test_batch1_beer_effects_are_content_specific():
    rows = {(r["category"], r["prime_set"]): r for r in BUILD["b1_effects"]}
    harm, pubs = rows[("beer", "drink_harm")], rows[("beer", "social_drink")]
    assert [two(harm[q]) for q in ("risk", "pressure", "norm")] == ["+0.39", "+1.45", "-0.76"]
    assert [two(pubs[q]) for q in ("risk", "norm")] == ["-0.29", "+0.54"]


def test_batch1_dose_and_ad_first():
    rows = {(r["prime_set"], r["position"]): r for r in BUILD["b1_dose"]}
    assert [two(rows[("drink_harm", p)]["pressure"]) for p in ("before_k1", "before_k3", "before_k5", "ad_first")] == \
        ["+0.30", "+1.35", "+2.69", "+2.70"]


def test_batch2_regular_vs_alcohol_free_beer():
    rows = {r["ad"]: r for r in BUILD["b2_harm"]}
    assert two(rows["Heineken pint (regular)"]["safe"]) == "-1.81"
    assert two(rows["Heineken Oranje fan kit (regular)"]["safe"]) == "-2.08"
    assert two(rows["Heineken 0.0 drinker"]["safe"]) == "+0.36"
    assert two(rows['Heineken 0.0 "Ultimate" can']["safe"]) == "+1.25"
    assert two(rows["Heineken pint (regular)"]["risk"]) == "+2.10"


def test_batch2_replicates_batch1():
    pint = next(r for r in BUILD["b2_rep"] if r["ad"] == "Heineken pint (regular)" and r["prime_set"] == "drink_harm")
    assert (two(pint["risk_batch1"]), two(pint["risk_batch2"])) == ("+2.52", "+2.10")
    assert (two(pint["pressure_batch1"]), two(pint["pressure_batch2"])) == ("+3.11", "+2.45")


def test_batch2_integrity_and_twins():
    i = BUILD["b2_integrity"]
    assert (i["design_feeds"], i["scored_answers"], i["answers_valid_mass_below_0.8"]) == (888, 7104, 1)
    assert i["duplicate_rows"] == i["identical_duplicates"] == 24
    twins = {r["feeds"]: r for r in BUILD["b2_twins"]}
    assert (twins["all"]["corr_risk_safe"], twins["all"]["corr_pushiness_free_to_decide"]) == (-0.86, -0.78)
    assert (twins["betting"]["corr_risk_safe"], twins["betting"]["corr_pushiness_free_to_decide"]) == (-0.09, -0.02)


def test_saved_feeds_match_the_design_code():
    """The original design code regenerates exactly the feeds (ids and image orders) in the runs."""
    sys.path.insert(0, str(ROOT / "agent-feeds" / "src"))
    from agentic_ads.priming_design import enumerate_feeds
    for cfg_name, run in [("batch1.toml", mr.RUN_B1), ("batch1_rerun.toml", mr.RUN_B1_RERUN), ("batch2.toml", mr.RUN_B2)]:
        cfg = tomllib.loads((ROOT / "agent-feeds" / "config" / cfg_name).read_text())
        man = json.loads((ROOT / "agent-feeds" / cfg["study"]["stimuli_manifest"]).read_text())
        designed = {f.feed_id: list(f.images) for f in enumerate_feeds(cfg, man)}
        saved = {f["feed_id"]: f["images"] for f in mr.jsonl(run / "feeds.jsonl")}
        assert designed == saved, cfg_name


# ----------------------------------------------------------------------------- ad-library

def test_panel_composition():
    rows = {r["firm"]: r for r in BUILD["panel"]}
    assert [rows[f]["ads"] for f in mr.FIRMS] == [1000, 605, 466, 1000, 170]
    assert rows["Total"]["ads"] == 3241 and rows["Total"]["unique_creatives_base_run"] == 676
    facts = BUILD["panel_facts"]
    assert (facts["coded_creatives"], facts["creatives_with_event_cue"], facts["creatives_with_sport_cue"]) == (951, 676, 492)


def test_firm_profiles():
    p = {r["firm"]: r for r in BUILD["profiles"]}
    assert round(p["Winamax"]["share_of_panel_impressions"], 2) == 0.57
    assert p["Winamax"]["creatives_first_run_before_2025"] == 183
    assert round(p["Winamax"]["imp_headline_most_prominent"], 3) == 0.622
    assert [round(p[f]["imp_offer_amount_most_prominent"], 3) for f in ("PMU", "Unibet", "Betsson", "bet365")] == \
        [0.572, 0.614, 0.561, 0.596]
    assert round(p["bet365"]["imp_brand_prominence_max"], 3) == 0.999
    assert p["Unibet"]["last_launch"] == "2026-03-19"


def test_similarity_and_world_cup_convergence():
    sim = {r["pair"]: r for r in BUILD["sim"]}
    assert sim["Betsson-bet365"]["coded_cues_by_impressions"] == 0.926
    june = next(r for r in BUILD["monthly"] if r["launch_month"] == "2026-06")
    assert (june["mean_pairwise_similarity"], june["winamax_bet365"]) == (0.765, 0.726)


def test_results_agree_with_the_original_metrics_file():
    """make_results re-implements ads_as_cues_metrics.py; both must agree with the committed JSON."""
    saved = json.loads((mr.ANALYSIS / "ads_as_cues_metrics.json").read_text())
    for r in BUILD["sim"]:
        a, b = r["pair"].split("-")
        assert saved["text_ads"][f"{a}|{b}"] == r["text_stems_by_ads"]
        assert saved["labels_ads"][f"{a}|{b}"] == r["coded_cues_by_ads"]
        assert saved["labels_imp"][f"{a}|{b}"] == r["coded_cues_by_impressions"]
    for r in BUILD["dist"]:
        assert [r["feature"], r["representativeness_ratio"]] in saved["representative_features"][r["firm"]]


def test_original_analysis_scripts_rebuild_committed_outputs(tmp_path):
    """Run the original stdlib analysis scripts on the shipped data; outputs must be byte-identical."""
    al = ROOT / "ad-library"
    out = tmp_path / "positioning"
    subprocess.run([sys.executable, str(al / "src/analyze_competitor_positioning.py"),
                    "--run", str(mr.PANEL_RUN),
                    "--backfill", str(mr.PANEL_RUN.parent / f"story_backfill_{mr.PANEL_RUN.name}"),
                    "--labels", str(mr.LABELS), "--out", str(out)], check=True, capture_output=True)
    for name in ("ad_label_panel.jsonl", "analysis_summary.json"):
        assert (out / name).read_bytes() == (mr.ANALYSIS / name).read_bytes(), name
    # ads_as_cues_metrics.py writes next to its inputs, so run it on a copy.
    copy = tmp_path / "al"
    (copy / "src").mkdir(parents=True)
    shutil.copy(al / "src/ads_as_cues_metrics.py", copy / "src")
    for sub in ("competitor_analysis_v1/ad_label_panel.jsonl", "competitor_labels_v1/manifest.json",
                "competitor_labels_v1/results.jsonl"):
        (copy / "data/processed" / sub).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(al / "data/processed" / sub, copy / "data/processed" / sub)
    subprocess.run([sys.executable, str(copy / "src/ads_as_cues_metrics.py")], check=True, capture_output=True)
    assert (copy / "data/processed/competitor_analysis_v1/ads_as_cues_metrics.json").read_bytes() == \
        (mr.ANALYSIS / "ads_as_cues_metrics.json").read_bytes()


def test_media_manifest_covers_every_collected_file():
    rows = list(csv.DictReader((ROOT / "ad-library/data/media_manifest.csv").open()))
    in_manifest = {r["sha256"] for r in rows}
    referenced = set()
    for path in (ROOT / "ad-library/data/raw").glob("snap_*/*/records.jsonl"):
        for r in mr.jsonl(path):
            sha = (r.get("media") or {}).get("sha256") or r.get("sha256")
            if sha:
                referenced.add(sha)
    assert referenced <= in_manifest
    assert len(in_manifest) == 1480
    assert all(r["url"].startswith("https://") for r in rows)


def test_stimulus_manifests_point_into_the_media_manifest():
    media = {r["sha256"] for r in csv.DictReader((ROOT / "ad-library/data/media_manifest.csv").open())}
    for name in ("batch1_manifest.json", "batch2_manifest.json"):
        m = json.loads((ROOT / "agent-feeds/config/stimuli" / name).read_text())
        for ad in m["ads"]:
            assert ad["source_sha256"] in media
            assert ad["source_path"].startswith("../ad-library/data/raw/")
        assert all(p["page"].startswith("https://commons.wikimedia.org/") for p in m["primes"])


# ----------------------------------------------------------------------------- brand-associations

def test_association_results():
    asym = {r["measure"]: r for r in BUILD["asym"]}
    assert round(asym["llm_qwen3-8b-4bit"]["median_pair_asymmetry"], 2) == 1.11
    p = BUILD["profile"]
    assert (p["pairs"], p["forward"], p["backward"], p["flat"], p["n_corr"]) == (73, 40, 12, 21, 53)
    assert round(p["corr_direction_vs_log_pageview_ratio"], 2) == -0.55
    sc = BUILD["study_c_facts"]
    assert (round(sc["slope_log_n_items_with_tier_controls"], 2), round(sc["t"], 1)) == (-0.80, -2.2)
    assert (round(sc["within_look_first_named"], 3), round(sc["t_first_named"], 1)) == (0.955, 2.7)


# ----------------------------------------------------------------------------- the release itself

def test_committed_results_match_a_fresh_build():
    assert mr.markdown(BUILD) == (ROOT / "results" / "RESULTS.md").read_text()
    assert mr.svg_harm(BUILD["b2_harm"]) == (ROOT / "results" / "beer_harm_by_ad.svg").read_text()
    assert mr.svg_prominence(BUILD["profiles"]) == (ROOT / "results" / "firm_prominence.svg").read_text()


def test_no_credentials_or_machine_paths_in_tracked_files():
    pattern = re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}|sk-proj-|gh[pos]_[A-Za-z0-9]{20,}|/Users/[A-Za-z]|/home/[a-z]+/"
                         r"|/private/var/|BEGIN [A-Z ]*PRIVATE KEY|@g\.harvard\.edu")
    for name in tracked():
        path = ROOT / name
        if path.suffix in (".png", ".npz") or name == "tests/test_results.py":
            continue
        assert not pattern.search(path.read_text(errors="ignore")), name


def test_no_ad_creatives_or_large_files_in_tracked_files():
    media = {".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".webm", ".mp3", ".wav", ".pdf", ".pptx"}
    for name in tracked():
        path = ROOT / name
        assert path.suffix.lower() not in media, name
        if path.suffix.lower() == ".png":  # only our own charts
            assert name.startswith("brand-associations/output/"), name
        assert path.stat().st_size < 50 * 1024 * 1024, name
        if path.suffix in (".csv", ".json", ".jsonl"):
            assert "/9j/4AAQ" not in path.read_text(errors="ignore"), f"embedded JPEG in {name}"


def test_every_data_file_is_in_the_codebook():
    patterns = re.findall(r"^\| `([^`]+)` \|", (ROOT / "DATA.md").read_text(), flags=re.M)
    roots = ("ad-library/data/", "agent-feeds/runs/", "agent-feeds/artifacts/", "agent-feeds/data/",
             "agent-feeds/tmp/", "brand-associations/data/", "brand-associations/output/", "results/")
    extra = ("agent-feeds/exploration/",)
    for name in tracked():
        if name.startswith(roots) or (name.startswith(extra) and not name.endswith(".py")):
            assert any(fnmatch.fnmatch(name, p) for p in patterns), f"{name} is not documented in DATA.md"


def test_run_outputs_match_their_manifests():
    """Run directories are unmodified: output hashes equal those recorded at run time."""
    for run in (ROOT / "agent-feeds/runs").glob("*/manifest.json"):
        m = json.loads(run.read_text())
        for name, digest in m["outputs"].items():
            assert hashlib.sha256((run.parent / name).read_bytes()).hexdigest() == digest, (run.parent.name, name)

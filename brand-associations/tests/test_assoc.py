"""Offline tests for the directed-association package (no network, no model downloads)."""

import json
import math

import numpy as np
import pytest

from implicit_ads.assoc import config, embed, llm, measures
from implicit_ads.assoc.sources import matcher, trends_related


def test_pilot_frame_validates():
    frame = config.load()
    assert len(frame.pairs) >= 20
    assert all(p.source.startswith("http") for p in frame.pairs)
    # every pair's entities sit in the frozen candidate sets
    assert {p.brand for p in frame.pairs} <= {b.id for b in frame.brands}


def test_frame_rejects_pair_with_unknown_entity(tmp_path):
    raw = json.loads(config.DEFAULT_CONFIG.read_text())
    raw["pairs"].append({"celebrity": "nobody", "brand": "adidas", "source": "https://x"})
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        config.load(path)


def test_softmax_asymmetry_equals_crowding_difference():
    rng = np.random.default_rng(0)
    s = rng.normal(size=(5, 7))
    fwd, bwd = measures.softmax_shares(s, tau=0.3)
    assert np.allclose(fwd.sum(axis=1), 1) and np.allclose(bwd.sum(axis=0), 1)
    log_zc, log_zb = measures.crowding(s, tau=0.3)
    asym = measures.asymmetry(fwd, bwd)
    assert np.allclose(asym, log_zb[None, :] - log_zc[:, None])


def test_crowded_brand_cue_produces_tate_to_adidas_asymmetry():
    # One niche celebrity (row 0) linked only to the big brand (col 0); the big brand is
    # equally close to many celebrities, the celebrity close to few brands.
    s = np.full((6, 4), 0.1)
    s[:, 0] = 0.8          # big brand: close to every celebrity (crowded cue)
    s[0, 0] = 0.8          # the pair itself
    fwd, bwd = measures.softmax_shares(s, tau=0.1)
    assert fwd[0, 0] > bwd[0, 0]
    assert measures.asymmetry(fwd, bwd)[0, 0] > 0


def test_conditional_counts_asymmetry_is_pure_size():
    n_c, n_b = np.array([100.0, 40.0]), np.array([5000.0, 300.0, 50.0])
    n_cb = np.array([[30.0, 3.0, 1.0], [2.0, 9.0, 4.0]])
    fwd, bwd = measures.conditional_from_marginals(n_c, n_b, n_cb)
    asym = measures.asymmetry(fwd, bwd)
    assert np.allclose(asym, np.log(n_b)[None, :] - np.log(n_c)[:, None])


def test_count_shares_and_zero_rows():
    n = np.array([[4.0, 0.0], [0.0, 0.0]])
    fwd, bwd = measures.count_shares(n)
    assert fwd[0, 0] == 1.0 and fwd[1].sum() == 0
    assert np.isnan(measures.asymmetry(fwd, bwd)[1, 1])


def test_ranks():
    s = np.array([[0.9, 0.1, 0.5], [0.2, 0.8, 0.5]])
    rf, rb = measures.ranks(s)
    assert rf[0].tolist() == [1, 3, 2]
    assert rb[:, 0].tolist() == [1, 2] and rb[:, 2].tolist() == [1, 1]


def test_hash_embeddings_deterministic_and_normalized():
    a = embed.hash_embed(["Tate McRae fronts adidas campaign", "Tate McRae fronts adidas campaign"])
    assert np.allclose(a[0], a[1]) and math.isclose(np.linalg.norm(a[0]), 1.0, rel_tol=1e-6)


def test_matcher_uses_word_boundaries():
    frame = config.load()
    lv = matcher(frame.get("louis_vuitton"))
    assert lv.search("a Louis Vuitton bag") and not lv.search("lv bag")  # bare "LV" dropped as too ambiguous
    jk = matcher(frame.get("jung_kook"))
    assert jk.search("jungkook calvin klein")
    tc = matcher(frame.get("timothee_chalamet"))
    assert tc.search("Timothee Chalamet chanel") and tc.search("timothée chalamet")


def test_trends_related_shares():
    frame = config.load()
    pats = {e.id: matcher(e) for e in frame.entities}
    top = [{"query": "tate mcrae adidas", "value": 50}, {"query": "tate mcrae songs", "value": 100}, {"query": "tate mcrae nike", "value": 50}]
    s = trends_related.shares(top, frame.brands, pats)
    assert s["adidas"] == pytest.approx(0.25) and s["nike"] == pytest.approx(0.25) and s["gucci"] == 0


def test_llm_directed_with_fake_scorer():
    frame = config.load()

    def fake(prompt, conts):  # makes every cue strongly prefer Adidas / Tate McRae
        return [0.0 if ("Adidas" in c or "Tate McRae" in c) else -5.0 for c in conts]

    res = llm.directed(frame, fake, log=lambda *_: None)
    ci, bi = frame.index("celebrity"), frame.index("brand")
    fwd, bwd = np.exp(res["log_fwd"]), np.exp(res["log_bwd"])
    assert np.allclose(fwd.sum(axis=1), 1) and np.allclose(bwd.sum(axis=0), 1)
    assert fwd[ci["tate_mcrae"], bi["adidas"]] == pytest.approx(fwd[ci["zendaya"], bi["adidas"]])
    assert bwd[ci["tate_mcrae"], bi["adidas"]] > bwd[ci["zendaya"], bi["adidas"]]


# ---------------------------------------------------------------- composition (associative strength)

from implicit_ads.assoc import components, freeassoc  # noqa: E402
from implicit_ads.assoc.sources import wiki  # noqa: E402


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def test_component_shares_sum_to_one_over_a_partition():
    rng = np.random.default_rng(1)
    E = np.stack([_unit(v) for v in rng.normal(size=(40, 8)) + 2.0])
    m = np.zeros(40, bool)
    m[:10] = True
    a, b = components.decompose(E, m), components.decompose(E, ~m)
    assert a["share_sample"] + b["share_sample"] == pytest.approx(1.0)
    assert a["pi_sample"] == pytest.approx(0.25)


def test_composition_is_not_similarity():
    # Two 'similar' entities (same category direction) that never co-occur have zero component share,
    # while a dissimilar entity that appears in a quarter of the cue's documents has a large one.
    cat = np.array([1.0, 0, 0, 0])
    tate_docs = np.stack([_unit(cat + [0, 1, 0, 0])] * 30 + [_unit([0, 0, 1, 0])] * 10)
    mentions_adidas = np.array([False] * 30 + [True] * 10)
    share = components.decompose(tate_docs, mentions_adidas)["share_sample"]
    assert share > 0.1
    assert components.decompose(tate_docs, np.zeros(40, bool))["share_sample"] == 0.0


def test_central_mentions_get_alignment_above_one():
    core = _unit([1, 0, 0])
    E = np.stack([core] * 30 + [_unit([1, 1, 1])] * 10)
    central = np.array([True] * 5 + [False] * 35)       # mentions inside the core coverage
    peripheral = np.array([False] * 35 + [True] * 5)    # mentions in off-core coverage
    assert components.decompose(E, central)["alignment"] > 1 > components.decompose(E, peripheral)["alignment"]


def test_nnls_recovers_planted_component():
    rng = np.random.default_rng(2)
    basis = rng.normal(size=(6, 20))
    target = 0.7 * basis[0] + 0.3 * basis[3]
    w = components.nnls_loadings(target, basis)
    assert w[0] == pytest.approx(0.7, abs=1e-6) and w[3] == pytest.approx(0.3, abs=1e-6)
    s = components.contribution_shares(target, basis, w)
    assert s.sum() == pytest.approx(1.0) and s.argmax() == 0


def test_freeassoc_parse_and_strengths():
    frame = config.load()
    assert freeassoc.parse("<think>x</think>1. Adidas\n2) pop music\n- Nike\n") == ["Adidas", "pop music", "Nike"]
    samples = {"tate_mcrae": [["pop", "Adidas"], ["Grammys"]], "adidas": [["Bad Bunny"], ["Messi"], ["Tate McRae"], ["shoes"]]}
    rows = {(r["celebrity"], r["brand"]): r for r in freeassoc.strengths(samples, frame)}
    r = rows[("tate_mcrae", "adidas")]
    assert float(r["fwd"]) == 0.5 and float(r["bwd"]) == 0.25 and float(r["fwd_rr"]) == 0.25


def test_wiki_mention_components_are_directed():
    frame = config.load()
    extracts = {"jennie": "Jennie is a South Korean singer and rapper. She became a Chanel house ambassador in 2017. "
                          "She released her debut solo single in late 2018.",
                "chanel": "Chanel is a French luxury fashion house based in Paris. It was founded by Coco Chanel in 1910. "
                          "Its current ambassadors include the singer Jennie."}
    rows = {(r["celebrity"], r["brand"]): r for r in wiki.mention_components(frame, extracts)}
    r = rows[("jennie", "chanel")]
    assert r["sent_c_mentioning_b"] == 1 and r["sent_b_mentioning_c"] == 1
    # Jennie's article: 1 of 3 sentences names Chanel; Chanel's article: "Coco Chanel" is not Jennie, 1 of 3 names Jennie.
    assert float(r["fwd"]) == pytest.approx(1 / 3) and float(r["bwd"]) == pytest.approx(1 / 3)


# ---------------------------------------------------------------- trajectories

from implicit_ads.assoc import trajectories  # noqa: E402


def test_pulls_identify_who_moved():
    # The brand's post-event vector moves halfway to the celebrity; the celebrity does not move.
    c_pre, b_pre, p = np.array([1.0, 0, 0, 0]), np.array([0, 1.0, 0, 0]), np.array([0, 0, 1.0, 0])
    X = {("c", "pre"): c_pre, ("c", "post"): c_pre, ("b", "pre"): b_pre, ("b", "post"): b_pre + c_pre,
         ("pb", "pre"): p, ("pc", "pre"): np.array([0, 0, 0, 1.0])}
    r = trajectories.pulls(X, "c", "b", ["pb"], ["pc"])
    assert r["pull_c_to_b_post"] == pytest.approx(0.0)
    assert r["pull_b_to_c_post"] > 0.5
    assert r["asym_post"] < 0  # brand absorbed the celebrity


def test_events_config_references_known_entities():
    ents, events, spec = trajectories.load_events(config.load())
    assert len(events) >= 15 and set(spec) == {"pre", "post", "late"}
    assert {e["type"] for e in events} >= {"wear", "ambassador"}

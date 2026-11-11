import json
import tomllib
import unittest
from collections import Counter
from pathlib import Path

from agentic_ads.priming_design import QUESTIONS, enumerate_feeds, prompt_for, recode_rating

ROOT = Path(__file__).resolve().parents[1]


class PrimingDesignTests(unittest.TestCase):
    def setUp(self):
        self.cfg = tomllib.loads((ROOT / "config/batch1.toml").read_text())
        self.man = json.loads((ROOT / "config/stimuli/batch1_manifest.json").read_text())
        self.feeds = enumerate_feeds(self.cfg, self.man)

    def test_deterministic(self):
        again = enumerate_feeds(self.cfg, self.man)
        self.assertEqual([f.feed_id for f in self.feeds], [f.feed_id for f in again])

    def test_ids_unique(self):
        self.assertEqual(len({f.feed_id for f in self.feeds}), len(self.feeds))

    def test_fixed_length_and_ad_position(self):
        n = self.cfg["design"]["feed_length"] + 1
        for f in self.feeds:
            if f.position == "ad_only":
                self.assertEqual(f.images, (f.ad_id,))
                continue
            self.assertEqual(len(f.images), n)
            self.assertEqual(f.images[f.ad_index], f.ad_id)
            self.assertEqual(f.ad_index, 0 if f.position == "ad_first" else n - 1)
            self.assertEqual(len(set(f.images)), n, "no repeated images in a feed")

    def test_k_primes_directly_before_ad(self):
        sets = {p["id"]: p["set"] for p in self.man["primes"]}
        for f in self.feeds:
            if f.position.startswith("before_k") and f.prime_set != "neutral":
                before = f.images[:-1]
                self.assertEqual([sets[i] for i in before[-f.k_primes:]], [f.prime_set] * f.k_primes)
                self.assertTrue(all(sets[i] == "neutral" for i in before[: len(before) - f.k_primes]))

    def test_cell_counts(self):
        c = Counter((f.ad_id, f.prime_set, f.position) for f in self.feeds)
        draws = self.cfg["design"]["draws"]
        self.assertTrue(all(v == draws for k, v in c.items() if k[2] != "ad_only"))

    def test_rerun_matches_batch1_reversed_feeds(self):
        rerun_cfg = tomllib.loads((ROOT / "config/batch1_rerun.toml").read_text())
        rerun = enumerate_feeds(rerun_cfg, self.man)
        orig_rev = {f.feed_id: f for f in self.feeds if f.reversed_scales}
        self.assertEqual({f.feed_id for f in rerun}, set(orig_rev))
        for f in rerun:
            self.assertFalse(f.reversed_scales)
            self.assertTrue(f.originally_reversed)
            self.assertEqual(f.images, orig_rev[f.feed_id].images)

    def test_batch2_design(self):
        from agentic_ads.priming_design import QUESTIONS_V2, questions_for
        cfg = tomllib.loads((ROOT / "config/batch2.toml").read_text())
        man = json.loads((ROOT / "config/stimuli/batch2_manifest.json").read_text())
        feeds = enumerate_feeds(cfg, man)
        self.assertTrue(all(not f.reversed_scales for f in feeds))
        self.assertEqual(sum(a["category"] == "beer" for a in man["ads"]), 4)
        for a in man["ads"]:
            # Public release: stimulus images are not shipped (scripts/fetch_stimuli.py rebuilds them),
            # so their presence is only checked once they have been fetched.
            if (ROOT / "data/raw/stimuli_batch1").exists():
                self.assertTrue((ROOT / a["local"]).exists(), a["local"])
        self.assertIs(questions_for(cfg), QUESTIONS_V2)
        twins = {q["twin_of"] for q in QUESTIONS_V2 if "twin_of" in q}
        self.assertTrue(twins <= {q["id"] for q in QUESTIONS_V2})
        self.assertEqual(QUESTIONS_V2[-1]["id"], "trail")  # resume logic keys on last question

    def test_reverse_recode(self):
        self.assertEqual(recode_rating("1", True), 5)
        self.assertEqual(recode_rating("4", False), 4)

    def test_prompts_name_ad_position(self):
        f = next(x for x in self.feeds if x.position == "ad_first")
        p, opts = prompt_for(QUESTIONS[0], f)
        self.assertIn(f"Image 1 of {len(f.images)}", p)
        self.assertEqual(opts, list("12345"))


if __name__ == "__main__":
    unittest.main()

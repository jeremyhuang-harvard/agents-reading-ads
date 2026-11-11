import unittest

from agentic_ads.design import build_cells, build_contexts, build_personas, validate_config


CONFIG = {
    "study": {"id": "test", "seed": 7, "persona_replicates": 3, "ad_id": "ad"},
    "design": {
        "preferences": ["price_first", "performance_first"],
        "histories": ["budget_pressure", "product_failure"],
        "price_contexts": ["near_benchmark", "favorable_contrast"],
        "quality_contexts": ["near_benchmark", "favorable_contrast"],
        "prompt_variants": ["a", "b"],
        "models": ["m1", "m2"],
    },
    "runner": {"engine": "mock"},
    "outputs": {"root": "tmp"},
}


class DesignTests(unittest.TestCase):
    def test_factorial_counts_and_unique_ids(self):
        personas = build_personas(CONFIG)
        contexts = build_contexts(CONFIG)
        cells = build_cells(CONFIG, personas, contexts)
        self.assertEqual(len(personas), 12)
        self.assertEqual(len(contexts), 4)
        self.assertEqual(len(cells), 192)
        self.assertEqual(len({p["persona_id"] for p in personas}), len(personas))
        self.assertEqual(len({c["cell_id"] for c in cells}), len(cells))

    def test_profile_cells_are_balanced(self):
        personas = build_personas(CONFIG)
        counts = {}
        for persona in personas:
            key = (persona["preference"], persona["history"])
            counts[key] = counts.get(key, 0) + 1
        self.assertEqual(set(counts.values()), {3})

    def test_rejects_unsupported_factor_levels(self):
        invalid = {**CONFIG, "design": {**CONFIG["design"], "preferences": ["invented"]}}
        with self.assertRaisesRegex(ValueError, "unsupported design.preferences"):
            validate_config(invalid)

    def test_rejects_boolean_integer_fields(self):
        boolean_seed = {**CONFIG, "study": {**CONFIG["study"], "seed": True}}
        with self.assertRaisesRegex(ValueError, "study.seed must be an integer"):
            validate_config(boolean_seed)
        boolean_replicates = {
            **CONFIG,
            "study": {**CONFIG["study"], "persona_replicates": True},
        }
        with self.assertRaisesRegex(ValueError, "persona_replicates"):
            validate_config(boolean_replicates)


if __name__ == "__main__":
    unittest.main()

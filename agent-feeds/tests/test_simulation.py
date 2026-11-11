import unittest

from agentic_ads.simulation import run_mock_cell


class SimulationTests(unittest.TestCase):
    def test_mock_is_deterministic_and_bounded(self):
        cell = {
            "cell_id": "cell_fixed",
            "price_context": "favorable_contrast",
            "quality_context": "near_benchmark",
        }
        persona = {"preference": "price_first", "history": "budget_pressure"}
        first = run_mock_cell(cell, persona)
        second = run_mock_cell(cell, persona)
        self.assertEqual(first, second)
        for field in (
            "price_attractiveness",
            "quality_attractiveness",
            "purchase_probability",
            "confidence",
        ):
            self.assertGreaterEqual(first[field], 0)
            self.assertLessEqual(first[field], 100)

    def test_seed_changes_mock_jitter(self):
        cell = {
            "cell_id": "cell_fixed",
            "price_context": "near_benchmark",
            "quality_context": "near_benchmark",
        }
        persona = {"preference": "price_first", "history": "budget_pressure"}
        self.assertNotEqual(run_mock_cell(cell, persona, 1), run_mock_cell(cell, persona, 2))


if __name__ == "__main__":
    unittest.main()

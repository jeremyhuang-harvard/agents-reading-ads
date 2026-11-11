import unittest
from pathlib import Path

from agentic_ads.validation import validate_records


class ValidationTests(unittest.TestCase):
    def test_response_schema_rejects_missing_documented_field(self):
        schema = Path(__file__).resolve().parents[1] / "schemas/response.schema.json"
        incomplete = {
            "cell_id": "cell",
            "first_attribute_noticed": "price",
            "takeaway": "Price stands out.",
            "perceived_intent": "Persuade.",
            "intended_audience": "Shoppers.",
            "price_attractiveness": 50,
            "quality_attractiveness": 50,
            "purchase_probability": 50,
            "choice": "target",
            "confidence": 50,
            "explanation": "Test.",
        }
        with self.assertRaisesRegex(ValueError, "perceived_claim"):
            validate_records([incomplete], schema)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
from typing import Any


def _unit_interval(seed: int, cell_id: str, label: str) -> float:
    digest = hashlib.sha256(f"{seed}:{cell_id}:{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / (2**64 - 1)


def _clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def run_mock_cell(
    cell: dict[str, Any], persona: dict[str, Any], seed: int = 0
) -> dict[str, Any]:
    """Exercise pipeline plumbing; this is not a behavioral model."""
    price_context = cell["price_context"] == "favorable_contrast"
    quality_context = cell["quality_context"] == "favorable_contrast"
    price_profile = persona["preference"] == "price_first"
    quality_profile = persona["preference"] == "performance_first"
    budget_history = persona["history"] == "budget_pressure"
    failure_history = persona["history"] == "product_failure"

    price_score = 45 + 24 * price_context + 13 * price_profile + 8 * budget_history
    quality_score = 45 + 24 * quality_context + 13 * quality_profile + 8 * failure_history
    price_score += (_unit_interval(seed, cell["cell_id"], "price") - 0.5) * 6
    quality_score += (_unit_interval(seed, cell["cell_id"], "quality") - 0.5) * 6
    first = "price" if price_score >= quality_score else "quality"
    purchase = 12 + 0.43 * price_score + 0.43 * quality_score
    confidence = 58 + abs(price_score - quality_score) * 0.45

    return {
        "cell_id": cell["cell_id"],
        "first_attribute_noticed": first,
        "takeaway": f"The offer is interpreted mainly through {first}.",
        "perceived_claim": f"The product offers attractive {first}.",
        "perceived_intent": "Persuade the viewer to consider the advertised product.",
        "intended_audience": "Shoppers comparing price and performance.",
        "price_attractiveness": _clamp(price_score),
        "quality_attractiveness": _clamp(quality_score),
        "purchase_probability": _clamp(purchase),
        "choice": "target" if purchase >= 55 else "opt_out",
        "confidence": _clamp(confidence),
        "explanation": "Deterministic mock output used only to test the research pipeline.",
    }


def run_cells(
    engine: str,
    cells: list[dict[str, Any]],
    personas: list[dict[str, Any]],
    seed: int,
) -> list[dict[str, Any]]:
    if engine != "mock":
        raise RuntimeError(
            "No substantive model runner is configured. Use the smoke config or implement a provider adapter."
        )
    persona_by_id = {persona["persona_id"]: persona for persona in personas}
    return [
        run_mock_cell(cell, persona_by_id[cell["persona_id"]], seed) for cell in cells
    ]

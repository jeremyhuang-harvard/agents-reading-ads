from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def summarize(
    cells: list[dict[str, Any]], responses: list[dict[str, Any]]
) -> dict[str, Any]:
    cell_by_id = {cell["cell_id"]: cell for cell in cells}
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for response in responses:
        cell = cell_by_id[response["cell_id"]]
        key = (cell["price_context"], cell["quality_context"])
        grouped[key].append(response)

    context_summaries = []
    for (price_context, quality_context), records in sorted(grouped.items()):
        context_summaries.append(
            {
                "price_context": price_context,
                "quality_context": quality_context,
                "n": len(records),
                "price_first_share": mean(
                    record["first_attribute_noticed"] == "price" for record in records
                ),
                "mean_purchase_probability": mean(
                    record["purchase_probability"] for record in records
                ),
            }
        )
    return {
        "cell_count": len(cells),
        "response_count": len(responses),
        "context_summaries": context_summaries,
        "warning": "Mock outputs validate plumbing only and carry no substantive behavioral meaning.",
    }

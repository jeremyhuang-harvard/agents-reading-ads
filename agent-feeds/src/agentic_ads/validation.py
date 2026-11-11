from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_TYPE_CHECKS = {
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "object": lambda value: isinstance(value, dict),
}


def validate_records(records: list[dict[str, Any]], schema_path: Path) -> None:
    """Validate records against the checked-in JSON-schema subset used here."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    allow_extra = schema.get("additionalProperties", True)

    for index, record in enumerate(records):
        missing = required - record.keys()
        if missing:
            raise ValueError(f"record {index} missing required fields: {sorted(missing)}")
        extra = record.keys() - properties.keys()
        if extra and not allow_extra:
            raise ValueError(f"record {index} has unexpected fields: {sorted(extra)}")
        for field, rules in properties.items():
            if field not in record:
                continue
            value = record[field]
            expected_type = rules.get("type")
            if expected_type and not _TYPE_CHECKS[expected_type](value):
                raise ValueError(f"record {index} field {field} has wrong type")
            if "enum" in rules and value not in rules["enum"]:
                raise ValueError(f"record {index} field {field} has unsupported value")
            if "minimum" in rules and value < rules["minimum"]:
                raise ValueError(f"record {index} field {field} is below minimum")
            if "maximum" in rules and value > rules["maximum"]:
                raise ValueError(f"record {index} field {field} is above maximum")

"""Build the self-contained demo findings report (figures inlined as base64).

Usage:
    uv run --extra demo python scripts/build_findings_report.py

Reads docs/report-template/demo_findings.html and output/demo/*.png; writes
output/demo/implicit_ads_demo_findings.html.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "report-template" / "demo_findings.html"
FIG = ROOT / "output" / "demo"
OUT = FIG / "implicit_ads_demo_findings.html"


def main() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")

    def inline(match: re.Match) -> str:
        path = FIG / match.group(1)
        if not path.exists():
            raise SystemExit(f"missing figure {path}; run `make demo` first")
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()

    html = re.sub(r"\{\{img:([\w.\-]+)\}\}", inline, html)
    OUT.write_text(html, encoding="utf-8")
    print(OUT, f"{OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

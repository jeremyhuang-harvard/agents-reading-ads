"""Validate the minimum reproducible-research scaffold."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
# Public release: AGENTS.md, the private presentation plan and the two .gitkeep placeholders
# (their folders now hold data) were dropped from this list.
REQUIRED_FILES = (
    "README.md",
    "Makefile",
    "pyproject.toml",
    "docs/reproducibility.md",
    "docs/research-design.md",
    "docs/vision.md",
    "docs/literature-foundations.md",
    "docs/outcome-identification-designs.md",
    "docs/scrapable-outcome-variables.md",
    "docs/data-source-feasibility.md",
    "docs/commerce-social-feasibility.md",
    "docs/vertical-selection.md",
    "docs/contained-watch-pilot.md",
    "docs/acute-product-shock-design.md",
    "docs/demo-case-dossiers.md",
    "docs/demo-pipeline.md",
    "docs/demo-spillover.md",
    "data/raw/demo/validation/gold_labels_heldout_v1.csv",
    "src/implicit_ads/demo/spillover.py",
    "docs/assoc-design.md",
    "config/assoc/ambassadors.json",
    "src/implicit_ads/assoc/measures.py",
    "src/implicit_ads/demo/validate.py",
    "config/demo_cases.json",
    "src/implicit_ads/demo/__main__.py",
    "tests/test_demo.py",
    "data/raw/README.md",
    "src/implicit_ads/__init__.py",
)


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        print("Missing required scaffold files:")
        for path in missing:
            print(f"- {path}")
        return 1

    forbidden_tracked_candidates = (
        ROOT / ".env",
        ROOT / "data" / "derived" / "research.csv",
        ROOT / "output" / "results.pdf",
    )
    present = [str(path.relative_to(ROOT)) for path in forbidden_tracked_candidates if path.exists()]
    if present:
        print("Unexpected local files at reserved example paths:")
        for path in present:
            print(f"- {path}")
        return 1

    print(f"Scaffold check passed: {len(REQUIRED_FILES)} required files present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

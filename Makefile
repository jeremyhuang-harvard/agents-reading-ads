.PHONY: results check test setup media stimuli

results:  ## rebuild results/ from the saved data (no API key, no network)
	python3 analysis/make_results.py

check: results  ## fail if the committed results differ from a fresh build
	git diff --exit-code -- results/

test:  ## headline numbers, byte-identical rebuilds of the original outputs, release hygiene
	uv run --group dev pytest -q
	cd agent-feeds && PYTHONPATH=src uv run --no-project --python 3.12 python -m unittest discover -s tests

setup:  ## install the dev dependencies used by the tests
	uv sync --group dev

media:  ## re-download the ad creatives from the public libraries (~0.7 GB, checksum-verified)
	cd ad-library && python3 scripts/fetch_media.py

stimuli:  ## rebuild the 80 agent-feed stimulus images (needs Pillow)
	cd agent-feeds && uv run --extra vlm python scripts/fetch_stimuli.py

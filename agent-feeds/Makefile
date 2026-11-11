PYTHON ?= uv run --python 3.11 python
CONFIG ?= config/smoke.toml

.PHONY: setup test lint check reproduce clean

setup:
	uv sync --python 3.11

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

lint:
	PYTHONPATH=src $(PYTHON) -m compileall -q src tests

check: lint test

reproduce:
	PYTHONPATH=src $(PYTHON) -m agentic_ads reproduce --config $(CONFIG)

clean:
	rm -rf tmp/smoke-runs data/interim/* data/processed/* artifacts/*
	mkdir -p tmp/smoke-runs data/interim data/processed artifacts

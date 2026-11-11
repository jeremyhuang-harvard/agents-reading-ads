UV ?= uv

.PHONY: setup test check dev

setup:
	$(UV) sync --locked --all-groups

test:
	$(UV) run pytest

check: test

dev:
	$(UV) run pytest -q

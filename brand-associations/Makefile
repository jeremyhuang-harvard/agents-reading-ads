.PHONY: check test reproduce demo demo-classify qwen-server assoc assoc-llm clean

QWEN_MODEL ?= mlx-community/Qwen3-8B-4bit
DEMO_ARGS ?=

check:
	uv run python scripts/check_scaffold.py

test:
	uv run --extra dev --extra demo pytest -q

reproduce: check test
	@echo "Scaffold and offline tests verified. Run 'make demo' to collect the network-backed demo data."

# Network-backed, cached demo pipeline (archive, attention, coverage, build).
demo:
	uv run --extra demo python -m implicit_ads.demo $(DEMO_ARGS)

# Optional local-LLM labels; start `make qwen-server` in another terminal first.
demo-classify:
	uv run --extra demo python -m implicit_ads.demo --stages classify,validate,spillover,build $(DEMO_ARGS)

# Directed celebrity-brand associations (network-backed, cached). Override stages with ASSOC_ARGS.
ASSOC_ARGS ?=
assoc:
	uv run --extra assoc python -m implicit_ads.assoc $(ASSOC_ARGS)

assoc-llm:
	uv run --extra assoc --extra assoc-llm python -m implicit_ads.assoc --stages llm,analyze $(ASSOC_ARGS)

qwen-server:
	mlx_lm.server --model $(QWEN_MODEL) --port 8080

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache tmp
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

#!/bin/bash
# Resume batch 2 (agentic_ads.run_priming) after a crash, retrying up to 5 times.
# Resume is feed-level idempotent: completed feeds (last question written) are skipped.
cd "$(dirname "$0")/.." || exit 1
RUN=runs/batch2-beer-priming-9a960c96e6-20261021T194553Z
LOG=tmp/batch2_resume.log
for attempt in 1 2 3 4 5; do
  echo "=== resume attempt $attempt at $(date '+%Y-%m-%d %H:%M:%S') commit $(git rev-parse --short HEAD)" >> "$LOG"
  PYTHONPATH=src .venv/bin/python -m agentic_ads.run_priming --config config/batch2.toml --resume "$RUN" >> "$LOG" 2>&1
  status=$?
  echo "=== attempt $attempt exited $status at $(date '+%H:%M:%S')" >> "$LOG"
  [ $status -eq 0 ] && exit 0
  sleep 90
done
exit 1

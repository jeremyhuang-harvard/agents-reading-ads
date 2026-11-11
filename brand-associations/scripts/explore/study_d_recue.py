"""Study D: re-cueing and interference across Taylor Swift's appearances (Sep–Dec 2023).

Question: when Taylor appears at later Chiefs games wearing *other* brands, does search for her
first identified product (New Balance 550) rise again — i.e. does the shared context re-cue the
stored celebrity-product link? And is the Oct 22 Nike Air Force 1 appearance answered with less
attention than the Sep 24 New Balance one?

Pulls daily Google Trends (US) Sep 1 - Dec 20, 2023 for:
  link:     Taylor Swift New Balance, Taylor Swift Nike, Taylor Swift shoes, Taylor Swift outfit
  products: New Balance 550, Nike Air Force 1, Nike Dunk, Adidas Samba
and computes, for each game day, weekday-adjusted excess on days 0..2 vs the 14 non-game days
before it.

Run: uv run --extra demo python scripts/explore/study_d_recue.py
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

from implicit_ads.explore import trends as T

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "explore" / "study_d"
GAME_DAYS = {  # Taylor attended (source: Page Six/Yahoo list); brand worn
    "2023-09-24": "New Balance 550", "2023-10-01": "(no product identified; Jets game)",
    "2023-10-12": "Wear by Erin Andrews", "2023-10-22": "Nike Air Force 1",
    "2023-12-10": "Westside Storey", "2023-12-17": "Kut the Knit / Rails",
}
PAYLOADS = {
    "link": ["Taylor Swift New Balance", "Taylor Swift Nike", "Taylor Swift shoes", "Taylor Swift outfit"],
    "products": ["New Balance 550", "Nike Air Force 1", "Nike Dunk", "Adidas Samba"],
}
START, END = "2023-09-01", "2023-12-20"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    games = sorted(date.fromisoformat(d) for d in GAME_DAYS)
    rows, daily = [], []
    for name, terms in PAYLOADS.items():
        data = T.over_time(terms, START, END)
        for t in terms:
            ser = {date.fromisoformat(x["date"]): x["value"] for x in data if x["term"] == t}
            for d, v in ser.items():
                daily.append({"payload": name, "term": t, "date": d.isoformat(), "value": v})
            for g in games:
                base_days = [d for d in ser if 1 <= (g - d).days <= 21 and all(abs((d - h).days) > 2 for h in games)]
                if len(base_days) < 7:
                    continue
                by_dow = defaultdict(list)
                for d in base_days:
                    by_dow[d.weekday()].append(ser[d])
                mean_b = statistics.fmean(ser[d] for d in base_days)
                exp = lambda d: statistics.fmean(by_dow[d.weekday()]) if by_dow.get(d.weekday()) else mean_b  # noqa
                sd = max(statistics.pstdev([ser[d] - exp(d) for d in base_days]), 1.0)
                post = [ser[d] - exp(d) for d in ser if 0 <= (d - g).days <= 2]
                rows.append({"payload": name, "term": t, "game_day": g.isoformat(), "worn": GAME_DAYS[g.isoformat()],
                             "baseline": round(mean_b, 2), "excess_0_2": round(statistics.fmean(post), 2),
                             "z_0_2": round(statistics.fmean(post) / sd, 2)})
    for fname, data in [("recue_events.csv", rows), ("recue_daily.csv", daily)]:
        with (OUT / fname).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()

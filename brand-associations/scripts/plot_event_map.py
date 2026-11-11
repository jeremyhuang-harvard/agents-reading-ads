"""Two-panel map of entity vectors before/after an event (PCA of headline-embedding means).

Run: uv run --extra assoc python scripts/plot_event_map.py sweeney_novig
"""

from __future__ import annotations

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from implicit_ads.assoc import config, embed, trajectories as T  # noqa: E402
from implicit_ads.assoc.config import OUTPUT  # noqa: E402
from implicit_ads.assoc.sources import matcher  # noqa: E402


def main(event_id: str, backend: str = "st:BAAI/bge-base-en-v1.5"):
    frame = config.load()
    ents, events, _ = T.load_events(frame)
    ev = next(e for e in events if e["id"] == event_id)
    docs = [json.loads(line) for line in T.DOCS.open() if f'"event": "{event_id}"' in line]
    enc = embed.Encoder(backend)
    pats = [matcher(e) for e in ents.values()]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, mask in zip(axes, (False, True)):
        texts = [embed.mask_names(d["text"], pats) if mask else d["text"] for d in docs]
        E = enc.encode(texts)
        groups = {}
        for d, v in zip(docs, E):
            groups.setdefault((d["entity"], d["window"]), []).append(v)
        keys = sorted(groups)
        X = np.stack([np.mean(groups[k], axis=0) for k in keys])
        X = X / np.linalg.norm(X, axis=1, keepdims=True)
        Xc = X - X.mean(axis=0)
        _, _, vt = np.linalg.svd(Xc, full_matrices=False)
        P = Xc @ vt[:2].T
        pos = {k: p for k, p in zip(keys, P)}
        c, b = ev["celebrity"], ev["brand"]
        for k, p in pos.items():
            ent, w = k
            if ent in (c, b):
                continue
            ax.scatter(*p, s=40, color="#9CA3AF")
            ax.annotate(ents[ent].name, p, fontsize=8, color="#6B7280", xytext=(4, 3), textcoords="offset points")
        for ent, col in ((c, "#1D4ED8"), (b, "#B91C1C")):
            seq = [w for w in ("pre", "post", "late") if (ent, w) in pos]
            pts = np.array([pos[(ent, w)] for w in seq])
            ax.plot(pts[:, 0], pts[:, 1], color=col, lw=1, alpha=0.5)
            for i in range(len(seq) - 1):
                ax.annotate("", xy=pts[i + 1], xytext=pts[i], arrowprops=dict(arrowstyle="->", color=col, lw=2))
            for w, p in zip(seq, pts):
                ax.scatter(*p, s=70 if w == "pre" else 50, color=col, edgecolor="black", lw=0.5, zorder=3)
                ax.annotate(f"{ents[ent].name} ({w})", p, fontsize=8.5, color=col, fontweight="bold", xytext=(5, -10), textcoords="offset points")
        ax.set_title("names kept" if not mask else "names masked (content of coverage only)", loc="left", fontsize=10, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("first principal component of the headline-embedding means")
        ax.set_ylabel("second principal component")
        ax.grid(alpha=0.15)
    fig.suptitle(f"{ents[ev['celebrity']].name} × {ents[ev['brand']].name}: entity vectors before (days −90…−8), after (0…30) and later (31…90); "
                 "grey = placebo entities (pre-event)", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = OUTPUT / f"event_map_{event_id}.png"
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sweeney_novig")

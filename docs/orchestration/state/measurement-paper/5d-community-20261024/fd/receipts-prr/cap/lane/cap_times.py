"""prr_cap's measured lane seconds per level, against the dry run's rates, and the queue span against the gate's
projection at t0 (fd/receipts-prr/dry/lane/projection.json). Reads only the committed receipt copies; the pattern of
iter/lane/iter_times.py.
Usage: python3 -I cap_times.py <receipts-prr dir>
"""
import json
import statistics as st
import sys
from pathlib import Path

MODE, N = "cap", 29
root = Path(sys.argv[1])
job, dry = root / MODE / "cluster", json.loads((root / "dry" / "lane" / "projection.json").read_text())
ids = {x[0]: x[1] for x in (l.split("\t") for l in (job / "queues" / f"{MODE}.tsv").read_text().splitlines()
                              if l and not l.startswith("#"))}
rec = {}
for p in (job / f"log-{MODE}").glob("*.start"):
    rec.setdefault(p.stem, {})["s"] = float(p.read_text().split()[0])
for p in (job / f"log-{MODE}").glob("*.end"):
    rec.setdefault(p.stem, {})["e"] = float(p.read_text().split()[0])
mine = {k: v for k, v in rec.items() if k in ids}
assert len(ids) == N and len(mine) == N and all("s" in v and "e" in v for v in mine.values())
by = {}
for k, v in mine.items():
    by.setdefault(ids[k], []).append(v["e"] - v["s"])
out = {"levels": {}}
for lv in sorted(by):
    w = by[lv]
    out["levels"][lv] = {"n": len(w), "mean_s": round(st.mean(w), 1), "min_s": round(min(w), 1), "max_s": round(max(w), 1),
                         "dry_rate_s": round(dry["rates_s"][lv], 1), "mean_over_dry": round(st.mean(w) / dry["rates_s"][lv], 3)}
span = max(v["e"] for v in mine.values()) - min(v["s"] for v in mine.values())
proj = dry["jobs"][MODE]["projected_h"]
out["queue_span_s"] = round(span, 1)
out["queue_span_h"] = round(span / 3600, 4)
out["projected_h_at_t0"] = proj
out["span_over_projection"] = round(span / 3600 / proj, 3)
out["gate_h"] = dry["jobs"][MODE]["gate_h"]
print(json.dumps(out, indent=1))

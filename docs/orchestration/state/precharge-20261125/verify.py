"""Recount each signed band from the compressed event lines without the scoring code."""

import csv
import gzip
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

base = Path(__file__).resolve().parent
events = Path(sys.argv[1]) if len(sys.argv) > 1 else base
periods = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
with np.load(base / "inputs/replay/playlists.npz") as replay:
    data_pot, mc_pot = np.sum([replay[p + "_pot"] for p in periods], axis=0)
scale_factor = data_pot / mc_pot
stat = Counter()
total = Counter()
for period in periods:
    for sample in ("Data", "MC"):
        weight_scale = 1 if sample == "Data" else scale_factor
        with gzip.open(events / f"{period}_{sample}.csv.gz", "rt") as stream:
            for record in csv.DictReader(stream):
                pt, longitudinal = float(record["pt"]), float(record["pz"])
                curvature = float(record["qp"])
                assert 0 <= pt < 4.5 and longitudinal >= 20
                band = sum(longitudinal >= edge for edge in (40, 60, 80))
                sign = (
                    "invalid"
                    if not math.isfinite(curvature) or abs(curvature) >= 999
                    else "+"
                    if curvature > 0
                    else "-"
                    if curvature < 0
                    else "zero"
                )
                weight = float(record["tune_weight"]) * weight_scale
                stat[band, sign, sample] += weight
                total[sample, sign] += 1
with (base / "merged-all.csv").open() as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == len(stat)
errs = Counter()
for row in rows:
    sample = row["sample"]
    delta = abs(stat[int(row["band"]), row["sign"], sample] - float(row["tune_weight"]))
    errs[sample] = max(errs[sample], delta)
    assert delta <= (0 if sample == "Data" else 1e-6)
print("Upstream event rows by sign and sample:", dict(total))
print("Largest direct count difference in each band and sign:", dict(errs))

#!/usr/bin/env python3
"""(ii)'s trade-off curve from the committed calibration (the director's request, 2026-11-04): descriptive, 0
compute, single-threaded. Per truth and as the G18+AR23 union per replicate, with the other two checks at #724's
fixed numbers ((i): at most 2 of 16 cells beyond 0.20; (iii): max |r - 1| <= 0.35, both through
fd_1b_c2.gate_724), the noise-only STOP rate and the gate's power against uniform deflations of 5, 8 and 10 %
(every ratio x (1 - d)), at (ii) thresholds of 2.0, 2.5, 3.0 and 3.5 x each truth's measured null SD of the mean log
ratio and at #724's fixed 0.07. Also the smallest common SD multiple at which the PROJECTED three-truth union is at
most 1 %, ASSUMING the plug-in's per-truth STOP rate is the mean of G18's and AR23's at that multiple and
independent of them (the plug-in is not calibrated: D5).

  python tradeoff.py <calibration.npz> <calibration.json> <out.json>
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[9] / "nd-unfolding"))
import fd_1b_c2 as c2  # noqa: E402

DEFLATIONS = (0.05, 0.08, 0.10)
MULTIPLES = (2.0, 2.5, 3.0, 3.5)


def flags(R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per replicate: (i) and (iii) from gate_724 as Joseph fixed them, and the mean log ratio for (ii)."""
    g = [c2.gate_724(r) for r in R]
    return (np.array([not x["i"] for x in g]), np.array([not x["iii"] for x in g]),
            np.array([x["mean_log"] for x in g]))


def main(npz, js, out) -> int:
    z, cal = np.load(npz), json.loads(Path(js).read_text())
    truths = ("g18", "ar23")
    sd = {t: cal["outputs"][t]["a"]["sd_mean_log"] for t in truths}
    base = {t: z[f"ratio_{t}"] for t in truths}
    F = {(t, d): flags(base[t] * (1.0 - d)) for t in truths for d in (0.0,) + DEFLATIONS}

    def stop(t, d, thr):
        i, iii, ml = F[(t, d)]
        return i | iii | (np.abs(ml) > thr)

    rows = []
    for label, thr_of in [(f"{m} SD", (lambda t, m=m: m * sd[t])) for m in MULTIPLES] + [("fixed 0.07", lambda t: c2.GATE_LOGMEAN)]:
        rec = {"threshold": label, "values": {t: thr_of(t) for t in truths}}
        for d in (0.0,) + DEFLATIONS:
            per = {t: stop(t, d, thr_of(t)) for t in truths}
            rec["noise" if d == 0.0 else f"power_{int(round(d * 100))}pct"] = {
                **{t: float(v.mean()) for t, v in per.items()}, "two_truth_union": float(np.mean(per["g18"] | per["ar23"]))}
        rows.append(rec)
    best = None
    for m in np.round(np.arange(2.0, 6.0001, 0.01), 2):
        p = {t: float(stop(t, 0.0, m * sd[t]).mean()) for t in truths}
        proj = 1.0 - (1 - p["g18"]) * (1 - p["ar23"]) * (1 - 0.5 * (p["g18"] + p["ar23"]))
        if proj <= 0.01:
            best = {"multiple": float(m), "thresholds": {t: float(m * sd[t]) for t in truths}, "projected_three_truth_union": proj,
                    "per_truth_noise": p, "power_10pct": {t: float(stop(t, 0.10, m * sd[t]).mean()) for t in truths},
                    "power_8pct": {t: float(stop(t, 0.08, m * sd[t]).mean()) for t in truths},
                    "assumption": "the plug-in's per-truth STOP rate is the mean of G18's and AR23's, independent"}
            break
    floor = {t: float((F[(t, 0.0)][0] | F[(t, 0.0)][1]).mean()) for t in truths}
    import hashlib
    rec = {"schema": "fd-1b-c2-tradeoff/1", "calibration_json_sha256": hashlib.sha256(Path(js).read_bytes()).hexdigest(),
           "calibration_npz_sha256": hashlib.sha256(Path(npz).read_bytes()).hexdigest(),
           "sets": int(base["g18"].shape[0]), "sd_mean_log": sd, "rows": rows, "three_truth_1pct": best,
           "floor_i_or_iii_noise": floor,
           "note": "(i) and (iii) at #724's fixed numbers through gate_724; only (ii)'s threshold varies; descriptive"}
    Path(out).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))

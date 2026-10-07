"""Report-only: final-stage recoveries against the FB population target beside the like-for-like ones
(PROTOCOL-20260925 sections 3-4; Amendment 2c item 7). No verdict uses these numbers.

For every scored run whose case has a population target (`fb_population_target.py`), the recovery against the
population, R_pop = 1 - L1(unfolded - population) / L1(prior - population), is recomputed from the run's stored
normalized unfolded and prior spectra (`recovery_stats`, the scorer's own function and undefined rule), for the
aggregate E_avail histogram, the scoreable regions and the case's natural joint histogram where one exists. Per
candidate and histogram: mean and sd of R (like-for-like) and R_pop, and the mean L1 between each replicate's own
target and the population (the finite-sample distance between a draw and its bank).

    python population_compare.py --evidence ../results/final/evidence_look1.json \
        --population ../results/final/population/fb_population_*.json --out population_look1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from score_design import SCOREABLE_REGIONS, canonical_case, recovery_stats  # noqa: E402


def population_histograms(doc: dict) -> dict[str, np.ndarray]:
    t = doc["targets"]
    out = {"eavail": np.asarray(t["aggregate"], float)}
    out.update({f"eavail@{k}": np.asarray(v, float) for k, v in t["regions"].items() if k in SCOREABLE_REGIONS})
    out.update({k: np.asarray(v, float) for k, v in t.get("histograms", {}).items()})
    return out


def summarize(x: list) -> dict:
    a = np.array([v for v in x if v is not None], float)
    return {"n": int(a.size), "mean": float(a.mean()) if a.size else None,
            "sd": float(a.std(ddof=1)) if a.size > 1 else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--population", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    ev = json.loads(a.evidence.read_text())
    pops = {}
    for p in a.population:
        doc = json.loads(p.read_text())
        # keyed by distortion hash: the library's D1 +0.35 (phase_e registry) and FINAL's historical `dev`
        # tilt share a canonical case name but are different distortions
        pops[doc["distortion_hash"]] = {"path": str(p), "distortion": doc["distortion"],
                                        "h": population_histograms(doc)}
    out = {"schema": "pet-final-design/population-compare/1", "report_only": True, "evidence": str(a.evidence),
           "populations": {v["distortion"]: {"path": v["path"], "distortion_hash": k} for k, v in pops.items()},
           "candidates": {}, "runs_without_population_target": {}}
    for name, cand in ev["candidates"].items():
        k = int(cand["k"])
        acc: dict = {}
        skipped: dict[str, int] = {}
        for run in cand["runs"]:
            doc = json.loads(Path(run["score"]).read_text())
            case = canonical_case(doc["case"]["case"])
            pop_doc = pops.get(doc["identity"].get("distortion_hash"))
            if pop_doc is None:
                skipped[f"{run['stage']}:{case}"] = skipped.get(f"{run['stage']}:{case}", 0) + 1
                continue
            it = next(i for i in doc["iterations"] if i["k"] == k)
            key = f"{run['stage']}:{case}"
            for hname, pop in pop_doc["h"].items():
                h = it["histograms"].get(hname)
                if h is None:
                    continue
                st = recovery_stats(np.asarray(h["prior_norm"]), np.asarray(h["unfolded_norm"]), pop, False)
                slot = acc.setdefault(key, {}).setdefault(hname, {"R": [], "R_pop": [], "target_vs_pop_l1": []})
                slot["R"].append(h["recovery"])
                slot["R_pop"].append(st["recovery"])
                slot["target_vs_pop_l1"].append(float(np.abs(np.asarray(h["target_norm"]) - pop).sum()))
        out["candidates"][name] = {
            key: {hname: {"R": summarize(v["R"]), "R_pop": summarize(v["R_pop"]),
                          "mean_target_vs_population_l1": float(np.mean(v["target_vs_pop_l1"]))}
                  for hname, v in hs.items()} for key, hs in acc.items()}
        out["runs_without_population_target"][name] = skipped
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for name, d in out["candidates"].items():
        for key, hs in d.items():
            e = hs.get("eavail") or next(iter(hs.values()))
            print(f"{name:12s} {key:22s} R {e['R']['mean']:.4f}  R_pop {e['R_pop']['mean']:.4f}  "
                  f"n {e['R']['n']}  |target - pop| {e['mean_target_vs_population_l1']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Cost model for the next PET routes, from measured per-fit timings (no new compute).

    pgc_costs.py --fits H2=<S4F-H2S1T24K5-FB0/fits.jsonl> L128=<S4F-L128S1T24K4-FB0/fits.jsonl> \
        --out results/costs.json

**Measured.** Each look-1 run's `fits.jsonl` records every fit's train rows, epochs and seconds.
These runs packed two unfoldings per A100, so the seconds are per half-GPU. From them:
- the cost per training row-epoch of each step;
- the study-scale unfolding cost. This reproduces the committed receipt medians (1.768 / 1.517
  A100-h) to within the load time.

**Scaled (an estimate, labelled as such).** A data-scale unfolding is costed as the same per
row-epoch rate times the data-scale row counts of each step, with the finalist's epochs and k
unchanged.
- **step 1** = every MC prior row + the data side's reco-passing rows. The study's step 1 is 851,831
  rows = 600,130 prior + 251,701 reco-passing pseudodata (`closure_data.py:130-136`); every real-data
  row and every background row is reco-passing;
- **step 2** = 2 x the MC prior's truth rows (the study's step 2 is exactly 2 x 600,130).

The rates are calibrated on these same fits, so reproducing the study-scale cost is a consistency
check, not a validation. The one independent data-scale reference is job 56563761.

The rate is assumed constant and the packing two per GPU. Neither is measured at that scale: memory,
I/O and the epoch count needed by larger samples can move the result. The `range` multiplies the
point estimate by 0.5-2.

Route totals are sums of declared unfolding counts x per-unfolding cost. Every count is a named
design choice, not a recommendation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

STUDY_PRIOR = 600_130
STUDY_PSEUDO = 600_111
STUDY_PSEUDO_RECO = 851_831 - 600_130    # reco-passing pseudodata rows of S4F-*-FB0 (fits.jsonl)
# real-data scale (VALIDATION_LEDGER.md:1916-1937 @ 52a2f6dd): 4,116,128 data rows plus 564,591
# POT-scaled background rows with negative weights on the data side, every one reco-passing
DATA_SIDE_ROWS = 4_116_128 + 564_591
INVENTORY_ROWS = 49_152_885
MC_PRIOR_OPTIONS = {"2M (historical full-event practice)": 2_000_000,
                    "10M": 10_000_000, "full inventory": INVENTORY_ROWS}
K = {"H2": 5, "L128": 4}
EPOCHS = {1: 8, 2: 24}
PACKING = 2
RANGE = (0.5, 2.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rates(path: Path) -> dict:
    """Seconds per training row-epoch per step (half-GPU), and the study unfolding's fit time."""
    fits = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    out = {"file": str(path), "sha256": sha256(path), "fits": len(fits)}
    for step in (1, 2):
        fs = [f for f in fits if f["step"] == step]
        row_epochs = sum(f["train_rows"] * len(f["history"]["loss"]) for f in fs)
        out[f"step{step}"] = {"train_rows": sorted({f["train_rows"] for f in fs}),
                              "epochs": sorted({len(f["history"]["loss"]) for f in fs}),
                              "seconds": sum(f["fit_seconds"] for f in fs),
                              "s_per_row_epoch": sum(f["fit_seconds"] for f in fs) / row_epochs}
    out["study_fit_a100_hours"] = (out["step1"]["seconds"] + out["step2"]["seconds"]) / PACKING / 3600
    return out


def unfolding_a100_hours(r: dict, k: int, n_mc: int, n_data_reco: float) -> dict:
    """Projected A100-hours of one unfolding with the measured step-1 rows split as the study's."""
    # step-1 train rows (80 % of the fitted rows) = 0.8 x (every prior row + reco-passing data side)
    s1_rows = 0.8 * (n_mc + n_data_reco)
    s2_rows = 0.8 * (2 * n_mc)
    sec = k * (s1_rows * EPOCHS[1] * r["step1"]["s_per_row_epoch"]
               + s2_rows * EPOCHS[2] * r["step2"]["s_per_row_epoch"])
    a100h = sec / PACKING / 3600
    return {"a100_hours": a100h, "range": [a100h * RANGE[0], a100h * RANGE[1]],
            "wall_hours_at_2_per_gpu": sec / 3600,
            "step1_train_rows": s1_rows, "step2_train_rows": s2_rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fits", nargs=2, required=True, metavar="NAME=PATH")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    rt = {kv.split("=", 1)[0]: rates(Path(kv.split("=", 1)[1])) for kv in a.fits}
    check = {}
    for name, r in rt.items():
        study = unfolding_a100_hours(r, K[name], STUDY_PRIOR, STUDY_PSEUDO_RECO)
        check[name] = {"note": "calibration consistency, not validation (rates come from these fits)",
                       "model_study_a100h": study["a100_hours"],
                       "measured_fit_a100h": r["study_fit_a100_hours"],
                       "receipt_median_a100h": {"H2": 1.767919, "L128": 1.517087}[name]}
    scale = {name: {opt: unfolding_a100_hours(r, K[name], n, DATA_SIDE_ROWS)
                    for opt, n in MC_PRIOR_OPTIONS.items()} for name, r in rt.items()}
    doc = {"schema": "pet-gbdt-comparison/costs/1", "rates": rt, "model_check": check,
           "data_scale_unfolding": scale,
           "constants": {"data_side_rows": DATA_SIDE_ROWS, "study_pseudo_reco_rows": STUDY_PSEUDO_RECO,
                         "k": K, "epochs": EPOCHS, "packing": PACKING, "range": RANGE},
           "status": "per row-epoch rates MEASURED at study scale; data-scale costs SCALED "
                     "(estimate)"}
    a.out.write_text(json.dumps(doc, indent=1) + "\n")
    for name in rt:
        print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in check[name].items()})
        for opt, v in scale[name].items():
            print(f"  {opt}: {v['a100_hours']:.1f} A100-h ({v['range'][0]:.1f}-{v['range'][1]:.1f}), "
                  f"wall {v['wall_hours_at_2_per_gpu']:.1f} h at 2/GPU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

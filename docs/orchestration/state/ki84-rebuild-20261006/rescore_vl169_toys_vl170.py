"""POST HOC, DESCRIPTIVE: rescore the 100 VL169 fixed-truth toys against the VL170 candidate band.

This has no verdict role. The toys reuse the MC that the band was built from (circular in the MC
part, PREREG Amendment 1.3), so it is not a coverage test and reports no PASS or FAIL. It measures
how much of the VL169 shortfall the KNOWN_ISSUES 84 fix accounts for.

The pre-registered primary form is scored with score_coverage.score(), imported unchanged:
z = (U - T) / (r_b T_b) with r_b = sigma_b / mean_b, the same 205 bins, the same toys 1-100, and the
same 99.5 % toy-bootstrap (20000 resamples, seed 20261005). Only r_b changes, from VL162 to VL170.
No new toys and no new unfolds.

  python rescore_vl169_toys_vl170.py      (from the repo root or anywhere; numpy only)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "2d-unfolding/uq/coverage_fixed_truth"))
import score_coverage as sc  # noqa: E402

INTERIM = ROOT / "docs/orchestration/state/coverage-2d-20261005/interim.npz"
VL169_SCORE = ROOT / "docs/orchestration/state/coverage-2d-20261005/interim_score.json"
BAND = HERE / "vl170_band.json"  # per-bin mean, std (ddof 1) of hXSec2D over boot1-300, both bands
BINSETS = HERE / "ki84_binsets.json"
OUT = HERE / "rescore_vl169_toys_vl170.json"
KEEP = ("C1", "C2", "pull_rms", "pull_mean", "intervals", "n_toys", "n_bins", "level")


def per_bin(U, T, mean, sigma, rep):
    z = sc.standardized_residuals(U, T, mean, sigma, rep)
    rms = np.full(T.shape, np.nan)
    c2 = np.full(T.shape, np.nan)
    rms[rep] = np.sqrt((z * z).mean(axis=0))
    c2[rep] = (np.abs(z) <= 2).mean(axis=0)
    return z, rms, c2


def rms_classes(rms, rep):
    r = rms[rep]
    return {"lt_0p9": int((r < 0.9).sum()), "0p9_to_1p1": int(((r >= 0.9) & (r <= 1.1)).sum()),
            "gt_1p1": int((r > 1.1).sum())}


def subset(z, rms, c2, rep, bins):
    flat = np.flatnonzero(rep.ravel())
    cols = [int(np.flatnonzero(flat == i * rep.shape[1] + j)[0]) for i, j in bins]
    zs = z[:, cols]
    return {"n_bins": len(bins),
            "C1_pooled": float((np.abs(zs) <= 1).mean()), "C2_pooled": float((np.abs(zs) <= 2).mean()),
            "pull_rms_pooled": float(math.sqrt((zs * zs).mean())),
            "per_bin": [{"bin": [i, j], "rms": float(rms[i, j]), "C2": float(c2[i, j])} for i, j in bins]}


def main():
    d = np.load(INTERIM)
    b = {k: np.array(v) for k, v in json.loads(BAND.read_text()).items() if k.endswith(("vl162", "vl170"))}
    keep = (d["toy_index"] >= 1) & (d["toy_index"] <= 100)
    U, T, rep = d["U"][keep], d["T"], d["reported"]
    assert keep.sum() == 100 and rep.sum() == 205 and np.all(d["T_max_abs_diff"][keep] == 0)
    if not np.array_equal(b["mean_vl170"] > 0, rep):
        raise SystemExit("[FAIL] the VL170 reported-bin set differs from the 205 VL169 bins")

    # Control 1: the band stored in interim.npz is VL162 as recomputed here.
    ctl_band = {k: float(np.max(np.abs(b[f"{k}_vl162"][rep] / d[f"prod_{k}"][rep] - 1)))
                for k in ("mean", "sigma")}
    # Control 2: scoring with the stored band reproduces the committed VL169 result.
    old = sc.score(U, T, d["prod_mean"], d["prod_sigma"], rep, level=sc.LEVEL_INTERIM)
    ref = json.loads(VL169_SCORE.read_text())["result"]
    ctl_score = max(abs(old[k] - ref[k]) for k in ("C1", "C2", "pull_rms", "pull_mean"))
    ctl_ci = max(abs(a - c) for k in old["intervals"] for a, c in zip(old["intervals"][k], ref["intervals"][k]))
    if ctl_score > 1e-12 or ctl_ci > 1e-12:
        raise SystemExit(f"[FAIL] VL169 not reproduced: points {ctl_score}, intervals {ctl_ci}")

    new = sc.score(U, T, b["mean_vl170"], b["sigma_vl170"], rep, level=sc.LEVEL_INTERIM)
    sets = json.loads(BINSETS.read_text())
    out = {"label": "POST HOC, DESCRIPTIVE; no verdict role; circular in the MC part (PREREG A1.3)",
           "inputs": {"toys": str(INTERIM.relative_to(ROOT)), "band": str(BAND.relative_to(ROOT)),
                      "scorer": "2d-unfolding/uq/coverage_fixed_truth/score_coverage.py score(), unchanged"},
           "controls": {"stored_band_vs_vl162_recomputed_max_rel": ctl_band,
                        "vl169_reproduced_max_abs_point": ctl_score, "vl169_reproduced_max_abs_interval": ctl_ci},
           "nominal": sc.NOMINAL, "windows_for_reference_only": sc.WINDOWS}
    for tag, mean, sigma, res in (("vl162", d["prod_mean"], d["prod_sigma"], old),
                                  ("vl170", b["mean_vl170"], b["sigma_vl170"], new)):
        z, rms, c2 = per_bin(U, T, mean, sigma, rep)
        out[tag] = {**{k: res[k] for k in KEEP},
                    "per_bin_rms_classes": rms_classes(rms, rep),
                    "per_bin_rms_median": float(np.nanmedian(rms)),
                    "n_bins_C2_lt_0p85": int((c2[rep] < 0.85).sum()),
                    "pz_40_60_column": subset(z, rms, c2, rep, sets["pz_40_60_column"]),
                    "former_rms_gt_2": subset(z, rms, c2, rep, sets["rms_gt_2"]),
                    "former_low_c2_lt_0p85": subset(z, rms, c2, rep, sets["low_c2_lt_0p85"])}
    n2 = sc.NOMINAL[2]
    out["share_of_C2_shortfall_closed"] = (new["C2"] - old["C2"]) / (n2 - old["C2"])
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True))
    for tag in ("vl162", "vl170"):
        o = out[tag]
        print(tag, {k: o[k] for k in ("C1", "C2", "pull_rms", "pull_mean", "per_bin_rms_classes",
                                      "per_bin_rms_median", "n_bins_C2_lt_0p85")}, o["intervals"])
        for s in ("pz_40_60_column", "former_rms_gt_2", "former_low_c2_lt_0p85"):
            print("  ", s, {k: v for k, v in o[s].items() if k != "per_bin"})
    print("controls", out["controls"], "share of C2 shortfall closed", out["share_of_C2_shortfall_closed"])
    print(f"[OK] wrote {OUT}")


if __name__ == "__main__":
    main()

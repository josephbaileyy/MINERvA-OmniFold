#!/usr/bin/env python3
"""RE-2 part C: C_model,2D beside Q_R, as the secondary users' total (RE2-DECLARATION-C.md §5;
DECISION-20261024-joseph-2d-model-dependence-component.md).

    python3 -I re2c_cmodel.py --cmodel-json 2d-unfolding/pv2d/cmodel/cmodel_2d.json --q-purity cov2d_Q_205.npz \\
        --q-refined <Q_R cov2d_Q_205.npz> --q-refined-sha SHA256 --area-npz <S5_R production_cov.npz> \\
        --area-npz-sha SHA256 --out-npz OUT.npz --out-json OUT.json

What it builds (DECISION item 2: M2, kappa = 1; "Q_R stays the headline"):
  C_model   = sum_k s_k s_k^T, fractional, from the committed factor S (cmodel_2d.json, 3 x 205). It does not depend on
              the central value and is unchanged by RE-2; its matrix sha256 must be 11fe6818... (pv2d/cmodel/REPORT §1).
  C_abs_R   = diag(x_R) C_model diag(x_R), x_R = Q_R's x = E_R: the rescaling the C_model report names (§1 Units).
  total_R   = Q_R + C_abs_R, the users' total. It is a separate product: Q_R is read, never modified, and nothing
              written here is named Q.
Reported: per-cell relative sigma of Q_R, of C_model and of Q_R + C_abs_R (median, p84, p90, max) and, new, the
integral sigma of each (sqrt(a C a) / a.x with a = S5's area row), so a secondary total can sit beside \\uqIntegral.

Positive controls (each stops):
  1. C_model rebuilt from the committed S has matrix sha256 11fe6818...;
  2. with the purity Q (cov2d_Q_205.npz 771e49a5..., x = E_U), C_abs's matrix sha256 is b11b10a0... and the per-cell
     Q + C_model summary equals cmodel_2d.json's total_m2 summary exactly.

MEASURES: the generator-shape model-dependence term at kappa = 1 beside Q_R. CANNOT AUTHORIZE: folding it into Q_R,
a coverage or calibration statement ("not a calibrated bound"), or printed wording (Joseph's, DECISION item 3).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pv2d", "cmodel"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pv2d"))
import build_cmodel as BC  # noqa: E402   (cmodel(), absolute(), matrix_sha256(), quantiles(), totals())

CMODEL_JSON_SHA = "aabc66d106a49484d486fb055bfb4280187898f98ca406e010f153af57702dd0"
Q_PURITY_SHA = "771e49a5510ff15fa522b73ab49b18329c2a58f092efb12a26aee39949168ced"
C_MODEL_MATRIX_SHA = "11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470"
C_ABS_PURITY_MATRIX_SHA = "b11b10a01b405921645cab664bc3ec7b0c14b23ca9c090d3e77f1b7772722d77"
LABEL = BC.LABEL


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def stop(msg):
    raise SystemExit(f"[STOP] {msg}")


def rel_sigma(C, x):
    return np.sqrt(np.maximum(np.diag(C), 0)) / x


def integral_sigma(C, x, a):
    return float(np.sqrt(a @ C @ a) / abs(a @ x))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("cmodel_json", "q_purity", "q_refined", "q_refined_sha", "area_npz", "area_npz_sha", "out_npz",
              "out_json"):
        ap.add_argument("--" + k.replace("_", "-"), dest=k, required=True)
    a = ap.parse_args(argv)
    for p, want in ((a.cmodel_json, CMODEL_JSON_SHA), (a.q_purity, Q_PURITY_SHA), (a.q_refined, a.q_refined_sha),
                    (a.area_npz, a.area_npz_sha)):
        if sha256(p) != want:
            stop(f"pin {p}: sha256 {sha256(p)} != {want}")
    cm = json.load(open(a.cmodel_json))
    S = np.asarray(cm["S"], float)
    cells = np.asarray(cm["cells"], np.int64)

    # ---- control 1: C_model from the committed factor
    C = BC.cmodel(S)
    if BC.matrix_sha256(C) != C_MODEL_MATRIX_SHA or cm["matrix_sha256"]["C_model"] != C_MODEL_MATRIX_SHA:
        stop(f"control 1: C_model matrix sha256 {BC.matrix_sha256(C)}")

    # ---- control 2: the purity Q reproduces the committed C_abs and total
    qp = np.load(a.q_purity, allow_pickle=False)
    if not np.array_equal(np.asarray(qp["cells"], np.int64), cells):
        stop("control 2: purity Q's cells differ from C_model's")
    xp = qp["x"]
    if BC.matrix_sha256(BC.absolute(C, xp)) != C_ABS_PURITY_MATRIX_SHA:
        stop(f"control 2: purity C_abs matrix sha256 {BC.matrix_sha256(BC.absolute(C, xp))}")
    tot_p = BC.quantiles(BC.totals(S, rel_sigma(qp["Q"], xp))["total_m2"])
    if tot_p != cm["summary"]["total_m2"]:
        stop(f"control 2: purity Q + C_model summary {tot_p} != cmodel_2d.json {cm['summary']['total_m2']}")

    # ---- the refined arm
    qr = np.load(a.q_refined, allow_pickle=False)
    if not np.array_equal(np.asarray(qr["cells"], np.int64), cells):
        stop("Q_R's cells differ from C_model's")
    QR, xr = qr["Q"], qr["x"]
    ar = np.load(a.area_npz, allow_pickle=False)
    if "arm" not in ar.files or str(ar["arm"]) != "refined":
        stop(f"{a.area_npz} carries no arm = refined")
    if not np.array_equal(ar["cells_x_EU"], xr):
        stop("the area npz's central value is not Q_R's x")
    area = ar["area"]
    C_abs = BC.absolute(C, xr)
    total = QR + C_abs
    sq = rel_sigma(QR, xr)
    out = {"schema": "re2c-cmodel/1", "label": LABEL,
           "decision": "docs/orchestration/DECISION-20261024-joseph-2d-model-dependence-component.md",
           "headline": "Q_R; this file's total is the secondary users' total Q_R + C_model, reported beside it",
           "form": "C_model = sum_k s_k s_k^T (M2), kappa = 1, fractional; C_abs = diag(x_R) C_model diag(x_R), "
                   "x_R = Q_R's x = E_R",
           "inputs": {"cmodel_json": {"path": a.cmodel_json, "sha256": CMODEL_JSON_SHA},
                      "q_purity": {"path": a.q_purity, "sha256": Q_PURITY_SHA},
                      "q_refined": {"path": a.q_refined, "sha256": a.q_refined_sha},
                      "area_npz": {"path": a.area_npz, "sha256": a.area_npz_sha}},
           "controls": {"C_model_matrix_sha256": C_MODEL_MATRIX_SHA, "purity_C_abs_matrix_sha256": C_ABS_PURITY_MATRIX_SHA,
                        "purity_total_m2_summary_equals_cmodel_2d_json": True},
           "matrix_sha256": {"C_model": BC.matrix_sha256(C), "C_abs_R": BC.matrix_sha256(C_abs),
                             "total_R": BC.matrix_sha256(total)},
           "cell_rel_sigma": {"Q_R": BC.quantiles(sq), "C_model": BC.quantiles(rel_sigma(C_abs, xr)),
                              "Q_R_plus_C_model": BC.quantiles(rel_sigma(total, xr))},
           "integral_rel_sigma": {"Q_R": integral_sigma(QR, xr, area), "C_model": integral_sigma(C_abs, xr, area),
                                  "Q_R_plus_C_model": integral_sigma(total, xr, area)},
           "per_cell": {"cells": cells.tolist(), "sigma_Q_R": sq.tolist(),
                        "sigma_Q_R_plus_C_model": rel_sigma(total, xr).tolist()}}
    np.savez(a.out_npz, C_model=C, C_abs_R=C_abs, total_Q_R_plus_C_model=total, cells=cells, x=xr)
    out["npz"] = {"path": os.path.abspath(a.out_npz), "sha256": sha256(a.out_npz)}
    with open(a.out_json, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(json.dumps({k: out[k] for k in ("cell_rel_sigma", "integral_rel_sigma", "matrix_sha256")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

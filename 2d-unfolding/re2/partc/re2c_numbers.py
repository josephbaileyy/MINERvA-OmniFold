#!/usr/bin/env python3
"""RE-2 part C: the printed numbers that compare another product with the 2D central value, and RE2-PLAN §5.3's
descriptive readouts (RE2-DECLARATION-C.md §6.3).

    python3 -I re2c_numbers.py --arm purity  --central E_U.root --eu E_U.root --ec E_C.root --p3 P3.root --out N.json
    python3 -I re2c_numbers.py --arm refined --central E_R.root --eu E_U.root --ec E_C.root --p3 P3.root \\
        --q-npz <Q_R cov2d_Q_205.npz> --q-sha SHA256 --out N.json

Every number is against `--central`: E_U in the purity arm, whose output is committed as the values table's purity
source, and E_R in the refined arm. The definitions are imported, not re-implemented:
  threeD     RE-1's 3D P3 marginal (xsec_3d_p3.root, c16b622b...) against the central value on its reported cells:
             re1_f_numbers.numbers() (area-weighted total change, median ratio) and re1_report2_extras.scatter()
             (SD of the per-cell ratio). Printed: sec_3d.tex "0.001 %", "1.0000", "~3.5 %".
  learner    the central value against the exact-split E_C (142a45b0...): the per-cell median and maximum of
             |x / E_C - 1| (%), lgbm_central_metrics.out's "0.983 %, 12.18 %". Printed: sec_systematics.tex:180, 377.
  refined arm only (RE2-PLAN §5.3, descriptive; nothing printed yet):
             E_R - E_U in Q_R's sigma per cell (|d| / sigma, median, p84, max), and E_R against E_U (integral change,
             median and max of |E_R / E_U - 1|).
MEASURES: descriptive numbers. Login node, root_6_28.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "nd-unfolding" / "re1"))
import re1_f_numbers as RF  # noqa: E402
import re1_report2_extras as RX  # noqa: E402

PINS = {"eu": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c",
        "ec": "142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5",
        "p3": "c16b622b4970800121b1d92dad91407878e0f4546375bfe27cdd3257d46d8c63"}
E_R_SHA = "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def q(a):
    a = np.asarray(a, float)
    return {"median": float(np.median(a)), "p84": float(np.percentile(a, 84)), "max": float(a.max())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=("purity", "refined"), required=True)
    for k in ("central", "eu", "ec", "p3", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--q-npz")
    ap.add_argument("--q-sha")
    a = ap.parse_args(argv)
    want = dict(PINS, central=PINS["eu"] if a.arm == "purity" else E_R_SHA)
    inputs = {}
    for k, w in want.items():
        got = sha256(getattr(a, k))
        if got != w:
            raise SystemExit(f"[FAIL] {k}: sha256 {got} != {w}")
        inputs[k] = {"path": getattr(a, k), "sha256": got}
    x, area = RF.th(Path(a.central), "hXSec2D")
    ec = RX.th2(Path(a.ec))
    eu = RX.th2(Path(a.eu))
    cells = x > 0
    if not (np.array_equal(cells, ec > 0) and np.array_equal(cells, eu > 0) and cells.sum() == 205):
        raise SystemExit("[FAIL] the central value, E_U and E_C do not share the 205 reported cells")
    p3num = RF.numbers(Path(a.p3), {"central": x})["vs_central"]
    p3sc = RX.scatter(RX.th2(Path(a.p3)), x)
    learner = 100 * np.abs(x[cells] / ec[cells] - 1)
    out = {"schema": "re2c-numbers/1", "arm": a.arm, "inputs": inputs,
           "threeD_p3_vs_central": {**p3num, "sd_ratio": p3sc["sd_ratio"], "mean_ratio": p3sc["mean_ratio"]},
           "learner_vs_E_C_pct": {"median_abs": float(np.median(learner)), "max_abs": float(learner.max())}}
    if a.arm == "refined":
        if not (a.q_npz and a.q_sha) or sha256(a.q_npz) != a.q_sha:
            raise SystemExit("[FAIL] the refined arm needs --q-npz with its recorded --q-sha")
        z = np.load(a.q_npz, allow_pickle=False)
        gid = np.flatnonzero(cells.ravel(order="C"))
        if not (np.array_equal(np.asarray(z["cells"], np.int64), gid) and np.array_equal(z["x"], x.ravel()[gid])):
            raise SystemExit("[FAIL] Q_R's cells or x are not E_R's")
        sig = np.sqrt(np.diag(z["Q"]))
        d = (x.ravel()[gid] - eu.ravel()[gid]) / sig
        rr = 100 * np.abs(x.ravel()[gid] / eu.ravel()[gid] - 1)
        a_ = area.ravel()[gid]
        out["E_R_minus_E_U_in_Q_R_sigma"] = {**{f"abs_{k}": v for k, v in q(np.abs(d)).items()},
                                             "mean_signed": float(d.mean())}
        out["E_R_vs_E_U"] = {"integral_change_pct": float(100 * ((x.ravel()[gid] * a_).sum() /
                                                                 (eu.ravel()[gid] * a_).sum() - 1)),
                             "median_abs_pct": float(np.median(rr)), "max_abs_pct": float(rr.max())}
        inputs["q_npz"] = {"path": a.q_npz, "sha256": a.q_sha}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: v for k, v in out.items() if k != "inputs"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

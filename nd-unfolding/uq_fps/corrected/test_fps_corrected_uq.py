#!/usr/bin/env python3
"""FPS-specific corrected-UQ validation (Agent C / P6-FPS). ROOT-free, login-node safe.

Complements Agent A's nd-unfolding/tests/test_uq_remediation.py (which covers the shared
uq_math contract). Here we validate the FPS-SPECIFIC facts the corrected FPS UQ relies on:
  1. uq_math contract holds on the 285-bin FPS grid (mean-centered biased 1/N; asymmetric
     interpolation; joint-throw mean-shift stored separately; a fixed-input null is zero).
  2. bank_uthrow_fps passes the _load_bank-equivalent schema (72 knob + 100x3 flux + cv).
  3. of_inputs_fps.npz has every field bootstrap_nd/seedscan_split need, on the 15x19 grid.
  4. The OLD uq_fps/uthrow_slabs_fps slabs carry NO estimator-seed stamp -> the corrected
     combine MUST reject them (documents why they are regenerated, not reused).

Run:  python uq_fps/corrected/test_fps_corrected_uq.py   (from nd-unfolding/)
"""
import glob
import os
import sys

import numpy as np

_ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND not in sys.path:
    sys.path.insert(0, _ND)
from uq_math import (interpolate_asymmetric_ratio, joint_throw_covariance,  # noqa: E402
                     mat_covariance)

BANK = os.path.join(_ND, "bank_uthrow_fps")
OFIN = os.path.join(_ND, "of_inputs_fps.npz")
OLD_SLABS = os.path.join(_ND, "uq_fps", "uthrow_slabs_fps")
KNOB = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
        "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
NBINS = 285          # 15 (pt) x 19 (pz)
_fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not cond:
        _fails.append(name)


def test_math_contract():
    print("[1] uq_math contract on the 285-bin FPS grid")
    rng = np.random.default_rng(0)
    X = rng.normal(size=(12, NBINS)) + 5.0
    C = mat_covariance(X)
    check("mat_covariance symmetric", np.allclose(C, C.T))
    check("mat_covariance biased 1/N", np.allclose(C, (lambda Z: Z.T @ Z / X.shape[0])(X - X.mean(0))))
    check("mat_covariance PSD", np.linalg.eigvalsh(C)[0] > -1e-9 * np.linalg.eigvalsh(C)[-1])
    # asymmetric interpolation: g=0 -> ratio 1 exactly (no CV drift)
    rp = rng.uniform(0.8, 1.2, NBINS); rm = rng.uniform(0.8, 1.2, NBINS)
    check("asym interp g=0 -> 1", np.allclose(interpolate_asymmetric_ratio(0.0, rp, rm), 1.0))
    check("asym interp g=+1 -> rho_plus", np.allclose(interpolate_asymmetric_ratio(1.0, rp, rm), rp))
    check("asym interp g=-1 -> rho_minus", np.allclose(interpolate_asymmetric_ratio(-1.0, rp, rm), rm))
    # joint-throw: covariance is mean-centered; the mean shift is returned SEPARATELY
    cv = rng.normal(size=NBINS) + 5.0
    Cj, shift = joint_throw_covariance(X, cv)
    check("joint mean-shift = mean(throws)-cv", np.allclose(shift, X.mean(0) - cv))
    check("joint cov independent of cv (mean-centered)", np.allclose(Cj, mat_covariance(X)))
    # fixed-input null: identical throws -> zero covariance and zero shift-vs-their-mean
    Xn = np.repeat(cv[None, :], 4, axis=0)
    Cn, sn = joint_throw_covariance(Xn, cv)
    check("null: identical throws -> zero cov", np.linalg.norm(Cn) < 1e-12)
    check("null: identical throws -> zero shift", np.linalg.norm(sn) < 1e-12)


def test_bank_schema():
    print("[2] bank_uthrow_fps schema (_load_bank-equivalent)")
    if not os.path.isdir(BANK):
        check("bank present", False, f"{BANK} absent"); return
    cv = np.load(os.path.join(BANK, "cv.npz"))
    need = ["MCgen", "MCreco", "measured", "measured_weights", "pass_reco",
            "pass_truth", "w_truth", "w_reco", "td_w", "flux", "data_pot", "n_nucleons"]
    check("cv.npz core keys", all(k in cv.files for k in need),
          "missing " + str([k for k in need if k not in cv.files]))
    ne = sum(1 for k in cv.files if k.startswith("edges_"))
    dims = [len(cv[f"edges_{i}"]) - 1 for i in range(ne)]
    check("cv edges = 15x19 (285)", dims == [15, 19], str(dims))
    mk = [f"{s}.npy" for b in KNOB for i in (0, 1)
          for s in (f"sig_{b}_t_{i}", f"sig_{b}_r_{i}", f"td_{b}_{i}")
          if not os.path.exists(os.path.join(BANK, f"{s}.npy"))]
    check("72 knob endpoint files present", not mk, "missing " + str(mk))
    for pre in ("sig_flux_t_", "sig_flux_r_", "td_flux_"):
        ids = {int(os.path.basename(p)[len(pre):-4]) for p in glob.glob(os.path.join(BANK, pre + "*.npy"))
               if os.path.basename(p)[len(pre):-4].isdigit()}
        check(f"{pre} = contiguous 0..99", ids == set(range(100)), f"{len(ids)} ids")


def test_ofinputs_schema():
    print("[3] of_inputs_fps.npz schema (bootstrap/split input)")
    if not os.path.isfile(OFIN):
        check("of_inputs_fps present", False, f"{OFIN} absent"); return
    d = np.load(OFIN, allow_pickle=True)
    need = ["nedges", "MCgen", "MCreco", "measured", "pass_reco", "pass_truth",
            "w_truth", "w_reco", "measured_weights", "denom_nd", "flux", "data_pot", "n_nucleons"]
    check("all bootstrap/split fields present", all(k in d.files for k in need),
          "missing " + str([k for k in need if k not in d.files]))
    ne = int(d["nedges"]); dims = [len(d[f"edges_{i}"]) - 1 for i in range(ne)]
    check("of_inputs grid = 15x19", dims == [15, 19], str(dims))
    check("denom_nd shape 15x19", tuple(np.asarray(d["denom_nd"]).shape) == (15, 19))


def test_old_slabs_quarantine():
    print("[4] OLD uq_fps throw slabs lack the estimator-seed stamp -> quarantine")
    slabs = sorted(glob.glob(os.path.join(OLD_SLABS, "uthrowfps_slab_*.npz")))
    if not slabs:
        check("old slabs present to check", False, "none found (already moved?)"); return
    unstamped = [s for s in slabs if "seed" not in np.load(s, allow_pickle=True).files]
    check("old slabs carry NO seed stamp (corrected combine rejects them)",
          len(unstamped) == len(slabs), f"{len(unstamped)}/{len(slabs)} unstamped")


if __name__ == "__main__":
    print("=== FPS corrected-UQ validation (Agent C) ===")
    test_math_contract()
    test_bank_schema()
    test_ofinputs_schema()
    test_old_slabs_quarantine()
    print(f"\n=== {'ALL PASS' if not _fails else 'FAILURES: ' + str(_fails)} ===")
    sys.exit(1 if _fails else 0)

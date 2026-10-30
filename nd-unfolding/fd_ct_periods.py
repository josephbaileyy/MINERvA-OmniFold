#!/usr/bin/env python3
"""The cheap tier's 5B readers (state/measurement-paper/5d-community-20261024/FD-CT-5B-DECLARATION.md): the pooled
control on the ALL chain, then the per-period readout on the 16 H2 reporting cells R00-R15. Login node, 0 node-h.

    fd_ct_periods.py precheck --definition ... --s1-npz ... --cresp ... --b <B> --mp1-zero <mp1s1_zero_b-_j-.npz> --out-json ...
    fd_ct_periods.py control  --definition ... --s1-npz ... --cresp ... --b <B> --mp1-zero <mp1s1_zero_b-_j-.npz> --out-json ...
    fd_ct_periods.py gate     --stage inputs|periods --b <B>
    fd_ct_periods.py periods  --definition ... --s1-npz ... --cresp ... --b <B> --control-json ... --readout-5a ... --out-json ...

* ``precheck`` decides K3 (below) on MP-1's own zero unfold before job A runs: if K2 holds, that unfold is X_ALL.
* ``gate`` is the submit stages' refusal: job A only after this deploy's precheck PASSed, job B only after its control.

* ``control`` reads only the ALL chain, before any period unfold exists (the period unfolds are a second job, whose
  submit line refuses unless this record says PASS). It decides three things, fixed here before anything runs:
  K1, the ALL dump's npz and background arrays are bitwise MP-1's zero dump's, key by key (from the ALL check
  receipt); K2, the ALL unfold's xsec_flat is bitwise MP-1's mp1s1_zero_b-_j-.npz; K3, |X_ALL / f - 1| <= tau_R on
  every cell, tau_R = 5 sqrt(2) sigma_R with sigma_R the pooled per-cell SD of MP-1's 25 committed jittered data
  unfolds about their own variant means (zero, em +-1, other +-1; 20 dof). It writes the verdict and, for K3, a flag
  per cell: never X_ALL / f - 1 or its ratio to tau, which with the committed mp1s1_zero would give f back.
* ``periods`` reads the three periods' seed-42 unfolds and 10 bootstrap replicas each (a seed block per period),
  their MC truths and the ALL unfold, and writes: the double ratios r_X = X_X / T_X of the periods against each other,
  the raw and MC-truth ratios beside them; per comparison the chi2 against M = (C_total + C_resp)/(f f^T) beside its
  bootstrap-noise expectation and the 10 paired noise draws; C_PL,5D by 2D's DESIGN section 2, printed beside the
  reported matrix; and 5B's period offsets g_X against 5A's projected ones (5A's untested assumption).

Every output is relative, and nothing is written relative to ALL: X_ALL is MP-1's committed zero unfold once K2 holds,
so a ratio to it would give an absolute period integral back. Nothing written or printed carries f, an absolute cell
value or f - g: each output passes
``fd_f0_regrade.LeakGuard`` first (exit 3, nothing written). Following amendment 1, an integral within LEAK_REL of f is
not passed to the guard, since it IS f. A control that refuses exits 1 with nothing written; K1-K3 are written with
the verdict, which is FAIL (exit 1) unless all three hold.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: a covariance component, a change to the reported
matrix or to kappa, a consistency verdict, the cause of a period difference, a claim or printed wording.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_ct_period_inputs as pi  # noqa: E402  (PERIODS, MP1_ZERO, NPZ_KEYS, BKG_KEYS)
import fd_ct_readers as ct  # noqa: E402  (common, rel_sigma, quad, summary, cells, write, near_f, code_sha)
import fd_f0_regrade as f0  # noqa: E402  (Stop, report, require, LeakGuard)
import s1_assemble as sa  # noqa: E402  (fine_map, functional_matrix, check_meta, sha256, xs)

N_CELLS = 16
PER = ("PA", "PB", "PC")
N_BOOT = 10
# a distinct bootstrap seed block per period, as 2D's (review M1): s5n_pseudo.bootstrap_replica seeds its streams from
# the seed alone, so a seed shared between periods gives their rows a common Poisson prefix and correlates their noise
BOOT = {"PA": tuple(range(1001, 1011)), "PB": tuple(range(2001, 2011)), "PC": tuple(range(3001, 3011))}
TOL = 1e-12
EIG_FLOOR = 1e-24   # a relative variance below this (sigma 1e-12) counts as zero in C_PL,5D's rank
# the p_parallel < 4.5 and >= 4.5 cells of the H2 definition (checked against its boxes)
PZ_LO = (0, 1, 2, 3, 8, 9, 10, 11)
PZ_HI = (4, 5, 6, 7, 12, 13, 14, 15)
JITTER_DIR = "docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts"
JITTER_VARIANTS = ("zero", "em_m1", "em_p1", "other_m1", "other_p1")
JITTER = {
    "zero_j1": "fb503e295fd275e08776ef9c112b04ac6aff73a69c4c728327efc3a03f4f1f8a",
    "zero_j2": "c1622354582fd63083d003bb4ba5bf11f7185c2c34572be56b75e7843023431f",
    "zero_j3": "c9a69b731c0523af64488bd2aa29805885f77f26089a8b54f64be417dfd2071c",
    "zero_j4": "16845b817c93480b4746e235b6d21f72f60598be553c3b3cff788235f82ebf0d",
    "zero_j5": "35f6b24ef3108636186d66b99acb58c844c575c8e6a73d68b153c12663204a2d",
    "em_m1_j1": "c172ab3a71498772a41a26dd90fa4a9c3d1529abb76cc2ce531b6bd2457efb54",
    "em_m1_j2": "c24a6ebeff13164f3b70676ef6af254bca1885aab53036769166e498521048e9",
    "em_m1_j3": "1df24ce234bbc0da5d54a4ac465ac10b32ec9f58dc0e5501a55317d5198f27af",
    "em_m1_j4": "d542dc9e50a161938c1519842ac2f5bacb1eb612f7cc81a4b6e71be799838330",
    "em_m1_j5": "089d71dee47fe7a073335a282a0fb222cccfef7c2c7bf6f965098b365bdc6f78",
    "em_p1_j1": "efeb1667887f8f2fa1efeb358997270a7317c336c0268e76696b12e37b5f6213",
    "em_p1_j2": "576f575ef937343465c650aadd91d1500ddb016594068cb027a686da920306fc",
    "em_p1_j3": "732b384cb23d79d25b2778efc68bcad781b0a4b1a16fc2c153a55564434e59dc",
    "em_p1_j4": "51c47031c5689f1e0afeba40b95f41ef701e31bf85f7d41916d1e3094d227f7d",
    "em_p1_j5": "ed16d6c9122aa9870bb5388379cdf7b184a0f05f7d99cf333430ab5070a4eb81",
    "other_m1_j1": "62a4797bd97cf8977104fcf1daccaa520f24735e5127d6b11bbbf759565ea7ea",
    "other_m1_j2": "f1923842fbaf0c1cf3a6cba2be7b2c65338acf12c30ce77232e0842ade021f00",
    "other_m1_j3": "929386af5f3766dc5ef4f560440bf2cffbd5bce739ea524fc73c8c5c0d06d0bb",
    "other_m1_j4": "84b0381840701754697546d2ff93ee1b0b94211cb79184ed8b74a2c2cbab7b2c",
    "other_m1_j5": "16e38c277e09daa17acc97e39ed380e755f9a50bd4db29040dc59b26c0005053",
    "other_p1_j1": "91d450d42d13b2a50a0ff437c6a5249cdb0de3875c326af6e67f176258a5ef23",
    "other_p1_j2": "2314573e9a432f2713715727af752e6b833c9d5e0db42c6cdbbe80f3e8075873",
    "other_p1_j3": "5aec72e9d14bde2e9b0edfef987cc06b986305badba24ee4b6f209e2ef5a308e",
    "other_p1_j4": "43cef796d52bb03d06db035a1f471ecd34410077a5b06e68c83486599f88d912",
    "other_p1_j5": "c2eb633377403b229547730138a5a10f22e76bff47199ea3ab08164a28c7cc52",
}
TAU_K = 5.0 * math.sqrt(2.0)
# sigma_R as declared (FD-CT-5B-DECLARATION.md section 3), recomputed by jitter_sigma() and required equal to 1e-12
SIGMA_JITTER = (0.0012889175014690088, 0.0012323002153985972, 0.002534677387519796, 0.0018932929637959593,
                0.0006139301007328451, 0.0022850703899750463, 0.0016371170363582552, 0.002817973318881797,
                0.0012116697632387162, 0.0011441748093664423, 0.00153081318800356, 0.0016522923202982936,
                0.0010429964099072232, 0.0013205396084948653, 0.0008262404363707385, 0.0007512548140199431)
READOUT_5A_SHA256 = "d7d518ac20acd90d9d411dbd1353c509e734e8588b6bc3965ae5f14cf9303728"   # fd/readout/fd_ct_period.json
LABELS = {
    "control": "the pooled control of 5B: the ALL chain built from MP-1's zero loops through 5B's own merge, dumps and "
               "unfold, against MP-1's zero chain bitwise (K1 inputs, K2 unfold) and against S1's f within a "
               "tolerance fixed from MP-1's committed jitter scatter before any period output existed (K3); K3 is "
               "written as a flag per cell, never as |X/f - 1| or its ratio to tau",
    "precheck": "K3 decided on MP-1's own zero unfold before job A runs: if K2 holds, X_ALL is that unfold; a flag "
                "per cell, never |X/f - 1| or its ratio to tau",
    "contrast": "the p_parallel contrast across 4.5 GeV/c, the only p_parallel boundary of the 16 cells; it is not 2D's "
                "step near 8 GeV/c, which lies inside the cells' [4.5, 60) range, so a 2D-like step is diluted in it",
    "periods": "5B, descriptive: the per-period (e) data unfolds of 1A-1F, 1G/1L/1M and 1N-1P on the 16 cells, each "
               "over its own MC truth (the double ratio), against each other (not against ALL, whose committed "
               "integrals would make a ratio absolute), with a noise "
               "reference of 10 bootstrap replicas per period (refit per replica; (e)'s seed term is zero by "
               "construction, S1-DIRECTOR-RULINGS.md section 2); chi2 values are distances in the reported matrix's "
               "metric beside their noise expectation, not tests",
    "cpl": "C_PL,5D by 2D's DESIGN section 2 on the 16 cells, relative to each cell: built from the observed offsets, "
           "so it contains them by construction and cannot fail; three periods, about 1.83 effective dof; printed "
           "beside the reported matrix, not in it (LIMITATION-PLAN-ADDENDUM-20261028.md section 5.4)",
    "vs_5a": "5B's period offsets g_X against 5A's projection of the 2D offsets (fd_ct_period.json, variant central): "
             "the difference is where 5A's assumption (the offset does not depend on E_avail, q3 or W inside a 2D bin) "
             "and 5D's own unfold disagree; 5A's g carries 2D's noise, which has no reference here",
    "no_threshold": "no consistency threshold is declared; whether the periods agree is read by the director and "
                    "Joseph from the chi2 beside its noise draws",
    "not_citable_for": ["the cause of a period difference, or which period is right", "a validated size: a block "
                        "built from the observed differences contains them by construction", "a covariance component "
                        "or a change to the reported matrix or to kappa", "a coverage or calibration statement"],
}


# ---------------------------------------------------------------- shared


def receipt(B: Path, P: str, control: str) -> dict:
    """The period's check receipt, made by this deploy's fd_ct_period_inputs.py, its files at their recorded digests."""
    p = B / "inputs" / f"check_{P}.json"
    if not p.is_file():
        raise f0.Stop(control, f"no check receipt {p}")
    r = json.loads(p.read_text())
    if (r.get("schema"), r.get("period"), r.get("playlists")) != ("fd-ct-5b-inputs/1", P, list(pi.PERIODS[P])):
        raise f0.Stop(control, f"{p.name}: schema, period or playlists")
    if (r.get("code_sha256") or {}).get("fd_ct_period_inputs.py") != sa.sha256(Path(pi.__file__).resolve()):
        raise f0.Stop(control, f"{p.name}: not made by this deploy's fd_ct_period_inputs.py")
    for k in ("lat_npz", "lat_bkg", "truth", "flux"):
        path, want = r["files"][k]
        f0.require(control, Path(path), want, f"{P} {k}")
    if r["files"]["flux"][1] != pi.FLUX[P]:
        raise f0.Stop(control, f"{p.name}: flux file is not the period's pinned one")
    return r


def unf_path(B: Path, P: str, b: int | None) -> Path:
    return B / "unf" / P / f"5b_{P}_b{'-' if b is None else b}_j-.npz"


def unfold(B: Path, P: str, b: int | None, rec: dict, control: str) -> np.ndarray:
    """One 5B unfold: (e) at seed 42 on its period's dumps, the declared replica, by this deploy's s5p_numerics.py."""
    p = unf_path(B, P, b)
    if not p.is_file():
        raise f0.Stop(control, f"missing {p}")
    m = f0.sa_call(control, sa.check_meta, p, "s5p-numerics/1", 42, False,
                   {"construction": "data", "truth": "nominal", "bootstrap_seed": b, "jitter_seed": None,
                    "coords": "float32", "input_npz_sha256": rec["files"]["lat_npz"][1],
                    "bkg_dump_sha256": rec["files"]["lat_bkg"][1]})
    if (m.get("code_sha256") or {}).get("s5p_numerics.py") != sa.sha256(_ND / "s5p_numerics.py"):
        raise f0.Stop(control, f"{p.name}: not made by this deploy's s5p_numerics.py")
    x = sa.xs(p)
    if x.shape != (int(np.prod(sa.s1.fine_shape())),) or not np.all(np.isfinite(x)):
        raise f0.Stop(control, f"{p.name}: xsec_flat shape {x.shape} or non-finite entries")
    return x


def jitter_sigma(repo: Path, U: np.ndarray) -> np.ndarray:
    """sigma_R: the pooled per-cell relative SD of MP-1's 25 jittered data unfolds about their own variant means."""
    dev = []
    for v in JITTER_VARIANTS:
        X = []
        for k in range(1, 6):
            p = repo / JITTER_DIR / f"mp1nj_{v}_b-_j{k}.npz"
            f0.require("K3", p, JITTER[f"{v}_j{k}"], f"jitter product {v} j{k}")
            f0.sa_call("K3", sa.check_meta, p, "s5p-numerics/1", 42, False,
                       {"construction": "data", "bootstrap_seed": None, "jitter_seed": k, "jitter_mode": "edge_safe"})
            X.append(U @ sa.xs(p))
        X = np.array(X)
        dev.append(X / X.mean(axis=0) - 1.0)
    D = np.concatenate(dev)
    return np.sqrt((D ** 2).sum(axis=0) / (D.shape[0] - len(JITTER_VARIANTS)))


def guarded(f: np.ndarray, integrals) -> f0.LeakGuard:
    """F0's guard over f and every integral, each integral within LEAK_REL of f dropped (amendment 1: it IS f)."""
    return f0.LeakGuard(f, [np.where(ct.near_f(x, f), np.nan, x) for x in integrals])


# ---------------------------------------------------------------- control


def k3(a, U: np.ndarray, X: np.ndarray, integrals) -> tuple[bool, dict, f0.LeakGuard]:
    """K3 on the cell integrals X: |X / f - 1| <= tau_R on every cell. Only a flag per cell is written: q tau is
    |X / f - 1| itself, and X_ALL is public once K2 holds (mp1s1_zero is committed), so a written q would give f
    back cell by cell (review H2)."""
    sigma = jitter_sigma(_ND.parent, U)
    if not np.allclose(sigma, SIGMA_JITTER, rtol=TOL, atol=0.0):
        raise f0.Stop("K3", "the jitter sigma recomputed from the pinned receipts is not the declared one")
    tau = TAU_K * sigma
    S = ct.common(a, U)
    f = S["f"]
    with np.errstate(divide="ignore", invalid="ignore"):
        within = np.abs(X / f - 1.0) <= tau
    ok = bool(np.all(within))
    rec = {"pass": ok, "within_by_cell": [bool(v) for v in within],
           "cells_over": ct.cells([int(i) for i in np.flatnonzero(~within)]),
           "tau_rel": tau.tolist(), "tau_k": TAU_K, "sigma_jitter_rel": sigma.tolist(),
           "written": "a flag per cell, never |X/f - 1| or its ratio to tau (review H2)"}
    return ok, rec, guarded(f, integrals)


def run_precheck(a) -> int:
    """K3 on MP-1's own zero unfold, before job A (review M2): if K2 holds, X_ALL is that unfold and K3 is decided
    by it; a FAIL here blocks 5B at 0 node-h. The tolerance is the one fixed above, before any read of f."""
    U = sa.functional_matrix(f0.sa_call("S", sa.fine_map, a.definition))
    f0.require("K0", a.mp1_zero, pi.MP1_ZERO["unfold"], "MP-1 mp1s1_zero_b-_j-.npz")
    X = U @ sa.xs(a.mp1_zero)
    f0.report("K0", "every cell integral of MP-1's zero unfold is positive", bool(np.all(X > 0)), "is not")
    ok, rec, guard = k3(a, U, X, [X])
    verdict = "PASS" if ok else "FAIL"
    out = {"schema": "fd-ct-5b-precheck/1", "labels": {"what": LABELS["precheck"]}, "verdict": verdict,
           "controls_passed": ["S", "K0"], "cells": ct.cells(), "K3_within_tolerance_of_f": rec,
           "inputs_sha256": {"mp1_zero": pi.MP1_ZERO["unfold"], "jitter": JITTER, "s1_npz": ct.PINS["s1_npz"],
                             "cresp": ct.PINS["cresp"], "definition": sa.DEFINITION_SHA256},
           "code_sha256": code_sha(), "argv": sys.argv}
    rc = ct.write(a, out, guard, [f"[5B precheck] K3 on mp1s1_zero: {verdict}, cells over {rec['cells_over']}"])
    return rc if ok else 1


def run_control(a) -> int:
    U = sa.functional_matrix(f0.sa_call("S", sa.fine_map, a.definition))
    present = [P for P in PER if (a.b / "unf" / P).exists()]
    if present:
        raise f0.Stop("K0", f"period unfolds exist before the control: {present}")
    rec = receipt(a.b, "ALL", "K0")
    f0.report("K0", "the ALL check receipt is this deploy's and its files are at their recorded digests", True)
    cmp_ = rec.get("all_vs_mp1_zero") or {}
    if (cmp_.get("mp1_sha256") or {}) != {"lat_npz": pi.MP1_ZERO["lat_npz"], "lat_bkg": pi.MP1_ZERO["lat_bkg"]}:
        raise f0.Stop("K0", "the ALL receipt did not compare against MP-1's pinned zero dump")
    want_keys = {"lat_npz": set(pi.NPZ_KEYS) | {"_key_sets_equal"}, "lat_bkg": set(pi.BKG_KEYS) | {"_key_sets_equal"}}
    if any(set(cmp_.get(k, {})) != want_keys[k] for k in want_keys):
        raise f0.Stop("K0", "the ALL receipt's comparison does not cover every declared key")
    f0.require("K0", a.mp1_zero, pi.MP1_ZERO["unfold"], "MP-1 mp1s1_zero_b-_j-.npz")
    x_all = unfold(a.b, "ALL", None, rec, "K0")
    x_mp1 = sa.xs(a.mp1_zero)
    X = U @ x_all
    f0.report("K0", "every ALL cell integral is positive", bool(np.all(X > 0)), "is not")
    k1_failed = sorted(f"{d}:{k}" for d in ("lat_npz", "lat_bkg") for k, v in cmp_[d].items() if not v)
    k1 = not k1_failed
    k2 = bool(x_all.shape == x_mp1.shape and np.array_equal(x_all, x_mp1))
    # for the report only: (e) is bit-reproducible run to run on the records, so any difference is a STOP
    nz = (x_mp1 != 0) if x_all.shape == x_mp1.shape else np.zeros(0, bool)
    k2_diff = float(np.max(np.abs(x_all[nz] / x_mp1[nz] - 1.0))) if nz.any() else None
    k3_ok, k3_rec, guard = k3(a, U, X, [X, U @ x_mp1])
    verdict = "PASS" if (k1 and k2 and k3_ok) else "FAIL"
    out = {"schema": "fd-ct-5b-control/1", "labels": {"what": LABELS["control"]}, "verdict": verdict,
           "controls_passed": ["S", "K0"], "cells": ct.cells(),
           "K1_inputs_bitwise_mp1_zero": {"pass": k1, "failed_keys": k1_failed,
                                          "lat_npz_bytes_equal": bool(cmp_.get("lat_npz_bytes_equal"))},
           "K2_unfold_bitwise_mp1_zero": {"pass": k2, "max_rel_diff_fine_cells": k2_diff},
           "K3_within_tolerance_of_f": k3_rec,
           "inputs_sha256": {"all_receipt": sa.sha256(a.b / "inputs/check_ALL.json"),
                             "all_unfold": sa.sha256(unf_path(a.b, "ALL", None)), "mp1_zero": pi.MP1_ZERO,
                             "jitter": JITTER, "s1_npz": ct.PINS["s1_npz"], "cresp": ct.PINS["cresp"],
                             "definition": sa.DEFINITION_SHA256},
           "code_sha256": code_sha(), "argv": sys.argv}
    lines = [f"[5B control] K1 inputs bitwise {k1}, K2 unfold bitwise {k2}, K3 within tolerance on every cell "
             f"{k3_ok} (over: {k3_rec['cells_over']}); verdict {verdict}"]
    rc = ct.write(a, out, guard, lines)
    return rc if verdict == "PASS" else 1


def run_gate(a) -> int:
    """The submit stages' gate (review M5): job A only after this deploy's precheck PASSed; job B only after this
    deploy's control PASSed on the ALL unfold now on disk, with the three period check receipts this deploy's."""
    name = {"inputs": "fd_ct_5b_precheck.json", "periods": "fd_ct_5b_control.json"}[a.stage]
    schema = {"inputs": "fd-ct-5b-precheck/1", "periods": "fd-ct-5b-control/1"}[a.stage]
    p = a.b / "control" / name
    if not p.is_file():
        raise f0.Stop("G", f"no {p}")
    r = json.loads(p.read_text())
    if (r.get("schema"), r.get("verdict")) != (schema, "PASS"):
        raise f0.Stop("G", f"{p.name} does not record a PASS")
    if (r.get("code_sha256") or {}).get("fd_ct_periods.py") != sa.sha256(Path(__file__).resolve()):
        raise f0.Stop("G", f"{p.name} was not made by this deploy's fd_ct_periods.py")
    if a.stage == "periods":
        if r["inputs_sha256"]["all_unfold"] != sa.sha256(unf_path(a.b, "ALL", None)):
            raise f0.Stop("G", "the ALL unfold is not the one the control read")
        for P in PER:
            receipt(a.b, P, "G")
    print(f"PASS gate {a.stage}", flush=True)
    return 0


# ---------------------------------------------------------------- periods


def cell_sets_problems(definition: Path) -> list[str]:
    boxes = {c["id"]: c["box"] for c in json.loads(definition.read_text())["reporting_cells"]}
    lo = sorted(i for i, b in boxes.items() if b["pz"][1] <= 4.5)
    hi = sorted(i for i, b in boxes.items() if b["pz"][0] >= 4.5)
    return [] if (tuple(lo), tuple(hi)) == (PZ_LO, PZ_HI) else [f"p_parallel cell sets {lo} / {hi}"]


def contrast(num, den, tn=None, td=None) -> float:
    """[I_hi(num)/I_hi(den)] / [I_lo(num)/I_lo(den)] - 1 over the p_parallel >= 4.5 and < 4.5 cells, I a sum of cell
    integrals; with MC truths, each I(num)/I(den) is a data/MC double ratio of the summed integrals."""
    def q(s):
        s = list(s)
        if tn is None:
            return num[s].sum() / den[s].sum()
        return (num[s].sum() / tn[s].sum()) / (den[s].sum() / td[s].sum())
    return float(q(PZ_HI) / q(PZ_LO) - 1.0)


def integral(num, den, tn=None, td=None) -> float:
    if tn is None:
        return float(num.sum() / den.sum() - 1.0)
    return float((num.sum() / tn.sum()) / (den.sum() / td.sum()) - 1.0)


def assess(val, num, den, tn, td, coef, D, Mi) -> dict:
    """One comparison: its shift, integral and p_parallel contrast, chi2 in M's metric, and the noise reference
    N = sum_X (a_X a_X^T) o mean_k d_X,k d_X,k^T with the paired draws sum_X a_X d_X,k (2D's analyze_periods.noise)."""
    o = {"shift": val.tolist(), "integral_shift": integral(num, den, tn, td) if num is not None else None,
         "chi2_M": float(val @ Mi @ val)}
    if num is not None:
        o["pz_contrast"] = contrast(num, den, tn, td)
    if coef is None:
        return o
    N = sum(np.outer(a, a) * np.mean([np.outer(d, d) for d in D[X]], axis=0) for X, a in coef.items())
    draws = [sum(a * D[X][k] for X, a in coef.items()) for k in range(N_BOOT)]
    dchi = [float(d @ Mi @ d) for d in draws]
    sig = np.sqrt(np.diag(N))
    o["noise"] = {"expected_chi2_M": float(np.trace(Mi @ N)), "draw_chi2_M": dchi,
                  "exceeds_every_draw": bool(o["chi2_M"] > max(dchi)),
                  "sigma_rel": sig.tolist(), "abs_shift_over_sigma": (np.abs(val) / sig).tolist(),
                  "abs_shift_over_sigma_summary": ct.summary(np.abs(val) / sig)}
    if num is not None:
        # a draw moves the comparison's numerator by its fractional fluctuation (2D's step_stat noise)
        c0 = o["pz_contrast"]
        cd = [contrast(num * (1 + d), den, tn, td) - c0 for d in draws]
        s = float(np.sqrt(np.mean(np.square(cd))))
        o["noise"]["pz_contrast_sigma"] = s
        o["noise"]["pz_contrast_z"] = c0 / s if s > 0 else None
    return o


def run_periods(a) -> int:
    fm = f0.sa_call("S", sa.fine_map, a.definition)
    U = sa.functional_matrix(fm)
    bad = cell_sets_problems(a.definition)
    if bad:
        raise f0.Stop("S", "; ".join(bad))
    if not a.control_json.is_file():
        raise f0.Stop("Q0", f"no control record {a.control_json}")
    cj = json.loads(a.control_json.read_text())
    if (cj.get("schema"), cj.get("verdict")) != ("fd-ct-5b-control/1", "PASS"):
        raise f0.Stop("Q0", "the pooled control did not PASS")
    if (cj.get("code_sha256") or {}).get("fd_ct_periods.py") != sa.sha256(Path(__file__).resolve()):
        raise f0.Stop("Q0", "the control record was not made by this deploy's fd_ct_periods.py")
    if cj["inputs_sha256"]["all_unfold"] != sa.sha256(unf_path(a.b, "ALL", None)):
        raise f0.Stop("Q0", "the ALL unfold is not the one the control read")
    f0.report("Q0", "the pooled control is this deploy's and PASSed on this ALL unfold", True)
    rec = {P: receipt(a.b, P, "Q1") for P in PER + ("ALL",)}
    for P in PER:
        want = sorted(unf_path(a.b, P, b).name for b in (None, *BOOT[P]))
        have = sorted(p.name for p in (a.b / "unf" / P).glob("*.npz"))
        if have != want:
            raise f0.Stop("Q1", f"{P}: the unfold directory holds {have}, not the declared {len(want)}")
    xs = {P: {b: unfold(a.b, P, b, rec[P], "Q1") for b in (None, *BOOT[P])} for P in PER}
    xs["ALL"] = {None: unfold(a.b, "ALL", None, rec["ALL"], "Q1")}
    f0.report("Q1", "3 x 11 period unfolds and the ALL unfold, each (e) on its own period's dumps", True)
    T, e_raw = {}, {}
    for P in PER + ("ALL",):
        tp = Path(rec[P]["files"]["truth"][0])
        with np.load(tp, allow_pickle=False) as z:
            m = json.loads(str(z["meta_json"]))
            t = np.asarray(z["xsec_flat"], float)
        if (m.get("schema"), m.get("npz_sha256")) != ("s5p-mc-truth-pred/1", rec[P]["files"]["lat_npz"][1]):
            raise f0.Stop("Q2", f"{tp.name}: not the MC truth of {P}'s npz")
        if (m.get("code_sha256")) != sa.sha256(_ND / "s5p_mc_truth_pred.py") or t.shape != xs[P][None].shape:
            raise f0.Stop("Q2", f"{tp.name}: code or shape")
        T[P] = U @ t
        if not rec[P].get("flux_constant_over_pt"):
            raise f0.Stop("Q2", f"{P}: the flux is not constant over p_T, so the exposure share is not one number")
        with np.load(rec[P]["files"]["lat_npz"][0], allow_pickle=True) as z:
            e_raw[P] = float(z["data_pot"]) * float(np.asarray(z["flux"], float).mean())
    f0.report("Q2", "each period's MC truth is s5p_mc_truth_pred's of its own npz, and its flux is p_T-constant", True)
    tot = sum(e_raw[P] for P in PER)
    e = {P: e_raw[P] / tot for P in PER}
    f0.report("Q2", "the periods' exposure sums to ALL's", abs(tot / e_raw["ALL"] - 1.0) <= 1e-9,
              f"{tot / e_raw['ALL'] - 1.0:.3e}")
    S = ct.common(a, U)
    f = S["f"]
    x = {P: U @ xs[P][None] for P in PER + ("ALL",)}
    D = {P: [U @ xs[P][b] / x[P] - 1.0 for b in BOOT[P]] for P in PER}
    allX = [U @ v for P in xs for v in xs[P].values()]
    f0.report("Q3", "every unfold and MC-truth integral is positive on all 16 cells",
              bool(all(np.all(v > 0) for v in allX) and all(np.all(T[P] > 0) for P in T)), "is not")
    f0.require("Q4", a.readout_5a, READOUT_5A_SHA256, "5A readout")
    g5a = json.loads(a.readout_5a.read_text())["variants"]["central"]["g"]
    guard = guarded(f, [*allX, *T.values()])
    M = S["M"] / S["ff"]
    Mi = np.linalg.inv(M)
    r = {P: x[P] / T[P] for P in x}
    one = np.ones(N_CELLS)
    comps = {}
    for q in ("raw", "dr"):
        tt = (lambda n, d: (T[n], T[d])) if q == "dr" else (lambda n, d: (None, None))
        val = (lambda n, d: r[n] / r[d] - 1.0) if q == "dr" else (lambda n, d: x[n] / x[d] - 1.0)
        for n, d in (("PB", "PA"), ("PC", "PA"), ("PC", "PB")):
            comps[f"{q}_{n}/{d}"] = assess(val(n, d), x[n], x[d], *tt(n, d), {n: one, d: -one}, D, Mi)
    for n, d in (("PB", "PA"), ("PC", "PA"), ("PC", "PB")):
        comps[f"mc_{n}/{d}"] = assess(T[n] / T[d] - 1.0, T[n], T[d], None, None, None, D, Mi)
    # C_PL,5D (2D DESIGN section 2) and its noise floor: the same construction on pure noise around consistent periods
    mbar = sum(e[P] * r[P] for P in PER)
    g = {P: r[P] / mbar - 1.0 for P in PER}
    V2 = sum(v * v for v in e.values())
    k = V2 / (1.0 - V2)
    C = k * sum(e[P] * np.outer(g[P], g[P]) for P in PER)
    gn = [{P: D[P][i] - sum(e[Y] * D[Y][i] for Y in PER) for P in PER} for i in range(N_BOOT)]
    Cn = np.mean([k * sum(e[P] * np.outer(h[P], h[P]) for P in PER) for h in gn], axis=0)
    lam = np.linalg.eigvalsh(C)
    floor = max(TOL * lam.max(), EIG_FLOOR)
    rank = int(np.sum(lam > floor))
    ident = float(np.max(np.abs(sum(e[P] * g[P] for P in PER))))
    if rank > 2 or lam.min() < -floor or ident > 1e-9:
        raise f0.Stop("Q5", f"C_PL,5D rank {rank}, min eigenvalue {lam.min():.3e}, sum e g {ident:.3e}")
    f0.report("Q5", "assertion: sum_X e_X g_X = 0 and C_PL,5D is PSD of rank <= 2", True)
    sig_m, sig_c, sig_n = np.sqrt(np.diag(M)), np.sqrt(np.diag(C)), np.sqrt(np.diag(Cn))
    g_sigma = {P: np.sqrt(np.mean([h[P] ** 2 for h in gn], axis=0)) for P in PER}
    vs5a = {}
    for P in PER:
        dlt = g[P] - np.asarray(g5a[P], float)
        vs5a[P] = {"g_5b": g[P].tolist(), "g_5a": list(g5a[P]), "difference": dlt.tolist(),
                   "g_5b_noise_sigma": g_sigma[P].tolist(), "abs_difference_over_noise": (np.abs(dlt) / g_sigma[P]).tolist(),
                   "abs_difference_over_noise_summary": ct.summary(np.abs(dlt) / g_sigma[P]),
                   "difference_chi2_M": float(dlt @ Mi @ dlt)}
    out = {"schema": "fd-ct-5b-periods/1",
           "labels": {"what": LABELS["periods"], "cpl": LABELS["cpl"], "vs_5a": LABELS["vs_5a"],
                      "contrast": LABELS["contrast"],
                      "no_threshold": LABELS["no_threshold"], "not_citable_for": LABELS["not_citable_for"]},
           "controls_passed": ["S", "Q0", "Q1", "Q2", "Q3", "Q4"],
           "assertions_passed": {"Q5": "implied by the construction: it guards the code, not the inputs"},
           "cells": ct.cells(), "cell_sets": {"pz_lo": ct.cells(PZ_LO), "pz_hi": ct.cells(PZ_HI)},
           "constants": {"periods": {"PA": "1A-1F", "PB": "1G 1L 1M", "PC": "1N-1P"}, "exposure_share": e,
                         "k": k, "n_boot": N_BOOT, "bootstrap_seeds": {P: list(BOOT[P]) for P in PER},
                         "metric": "M = (C_total + C_resp) / (f f^T), S1's reported matrix with C_resp",
                         "noise": "per period, d_k = X_b,k / X_s42 - 1 over 10 bootstrap replicas (s5n_pseudo."
                                  "bootstrap_replica, refit per replica); the replica leaves denom_nd and so the MC "
                                  "truth unchanged, so d is the same for X and for X/T; no seed term (zero for (e))"},
           "comparisons": comps,
           "C_PL5D": {"label": LABELS["cpl"], "C_PL5D_rel": C.tolist(), "rank": rank, "sigma_rel": sig_c.tolist(),
                      "sigma_rel_summary": ct.summary(sig_c), "sigma_ratio_to_M": (sig_c / sig_m).tolist(),
                      "sigma_ratio_to_M_summary": ct.summary(sig_c / sig_m),
                      "trace_share": float(np.trace(C) / np.trace(M + C)),
                      "noise_floor_sigma_rel": sig_n.tolist(), "sigma_ratio_to_noise_floor": (sig_c / sig_n).tolist()},
           "g_vs_5A": {"label": LABELS["vs_5a"], "periods": vs5a},
           "sigma_rel_M": sig_m.tolist(),
           "inputs_sha256": {"control": sa.sha256(a.control_json), "readout_5a": READOUT_5A_SHA256,
                             "receipts": {P: sa.sha256(a.b / "inputs" / f"check_{P}.json") for P in rec},
                             "unfolds": {P: {str(b): sa.sha256(unf_path(a.b, P, b)) for b in xs[P]} for P in xs},
                             "s1_npz": ct.PINS["s1_npz"], "cresp": ct.PINS["cresp"], "definition": sa.DEFINITION_SHA256},
           "code_sha256": code_sha(), "argv": sys.argv}
    lines = []
    for nm in ("dr_PB/PA", "dr_PC/PA", "dr_PC/PB"):
        o = comps[nm]
        lines.append(f"[5B] {nm}: chi2_M {o['chi2_M']:.3f} (noise expectation {o['noise']['expected_chi2_M']:.3f}, "
                     f"draws max {max(o['noise']['draw_chi2_M']):.3f}), integral {100 * o['integral_shift']:+.3f}%, "
                     f"pz contrast {100 * o['pz_contrast']:+.3f}% (z {o['noise']['pz_contrast_z']:.2f})")
    lines.append(f"[5B] C_PL,5D median sigma {100 * out['C_PL5D']['sigma_rel_summary']['median']:.4f}%, median ratio "
                 f"to sigma_M {out['C_PL5D']['sigma_ratio_to_M_summary']['median']:.4f}")
    return ct.write(a, out, guard, lines)


# ---------------------------------------------------------------- main


def code_sha() -> dict:
    return {**ct.code_sha(), "fd_ct_periods.py": sa.sha256(Path(__file__).resolve()),
            "fd_ct_period_inputs.py": sa.sha256(Path(pi.__file__).resolve())}


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="reader", required=True)
    g = sub.add_parser("gate")
    g.add_argument("--stage", choices=("inputs", "periods"), required=True)
    g.add_argument("--b", type=Path, required=True)
    for name in ("precheck", "control", "periods"):
        p = sub.add_parser(name)
        p.add_argument("--definition", type=Path, required=True)
        p.add_argument("--s1-npz", type=Path, required=True)
        p.add_argument("--cresp", type=Path, required=True)
        p.add_argument("--b", type=Path, required=True)
        p.add_argument("--out-json", type=Path, required=True)
        if name in ("precheck", "control"):
            p.add_argument("--mp1-zero", type=Path, required=True)
        else:
            p.add_argument("--control-json", type=Path, required=True)
            p.add_argument("--readout-5a", type=Path, required=True)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    if a.reader != "gate" and a.out_json.exists():
        print(f"FAIL refusing to overwrite {a.out_json}", file=sys.stderr)
        return 1
    try:
        return {"precheck": run_precheck, "control": run_control, "gate": run_gate, "periods": run_periods}[a.reader](a)
    except f0.Stop as e:
        print(e.code, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

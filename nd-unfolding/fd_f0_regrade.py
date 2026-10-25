#!/usr/bin/env python3
"""5D fake-data stage F0 (state/measurement-paper/5d-community-20261024/FD-F0-DECLARATION.md): re-grade the existing
configuration (e) fake-data products on the 16 H2 reporting cells R00-R15 against S1's C_total.

The plan is FD-PLAN.md sections 3 and 5.2, with the director's rulings (FD-DIRECTOR-RULINGS.md); Joseph approved it in
DECISION-20261025-joseph-approve-5d-fd-f0.md. Per experiment i at truth T, r_i = X_i / Xtrue_i - 1 on the cells, with
X = sum_f x_f vol_f (S1's integration rule). The bias b_T is

* rows 1, 2, 4 (s5e / Stage 0 ensembles, Stage 0c GiBUU, A7 expectation-mode f4): the unweighted mean of r_i;
* row 3 (the L-5D-PV closure at NuWro): its noise-free r;
* row 6 (A7 power alternatives): the NuE-weighted mean of r_i less the offset O_ref = b~_ref(row 5) - b_ref(row 4) of
  the truth it sits on, if the offset control (control 7) passes; otherwise row 6 is descriptive and ungraded.

Each truth is graded against C^(T) = C_e/(f f^T) + sum_{j != own(T)} s_j s_j^T (all three vertices for a non-vertex
truth), with the noise N_T of its mean: per-cell pulls z = b / sqrt(diag(C + N)) and chi2 = b^T (C + N)^-1 b, ndf 16.
Beside it: the in-sample matrix for a vertex-family truth, a declared sensitivity matrix for GENIE CV and q3, the
model-only matrix C_stat/(f f^T) + sum_{j != own} s_j s_j^T (descriptive), and the eight p_parallel < 4.5 cells for a
GiBUU-family truth (descriptive). Triggers (ruling 2): |z| > 2 per cell, P(chi2_16 > chi2) < 0.01 per truth, counted
by truth group with their denominators and the Gaussian reference beside them.

f enters only as the divisor that makes C_e fractional. NOTHING THIS TOOL WRITES OR PRINTS CARRIES f, AN ABSOLUTE CELL
VALUE OR f - g (ruling 6): every output passes ``LeakGuard`` first, which refuses (exit 3, nothing written) on any
finite non-zero number below 1e-30 in magnitude, or any number within 1e-13 relative of f, of an absolute cell
integral of any product, of f - X or of f/X, X/f, f/X - 1 or X/f - 1 for any such integral X, with either sign
(cell by cell for a cell-indexed vector).

Controls 0-8 run in the declared order; 0-6 and 8 refuse (exit 1, nothing written). Control 7 gates row 6 only.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: a claim, a cell merge, a change to C_e, C_model or
kappa, or any reading of the data against a generator (Stage G).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import traceback
import zipfile
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s1_assemble as sa  # noqa: E402  (sha256, fine_map, functional_matrix, flux_weights, load_manifest)

N_FINE, N_CELLS = 65856, 16
VERTICES = ("genie_mec", "nuwro", "gibuu")
Z_TRIGGER, P_TRIGGER = 2.0, 0.01
GAUSS_CELL = math.erfc(math.sqrt(2.0))   # P(|z| > 2) for a unit Gaussian
TOL = 1e-12
LEAK_FLOOR, LEAK_REL = 1e-30, 1e-13
P_FLOOR = 1e-30                          # a p-value below this is written as 0.0 with p_below_floor true (LeakGuard's floor)
GIBUU_CELLS = (0, 1, 2, 3, 8, 9, 10, 11)  # the p_parallel < 4.5 cells; checked against the definition's boxes
INPUT_NPZ_SHA256, BKG_SHA256 = sa.INPUT_NPZ_SHA256, sa.BKG_SHA256
ALL_ROWS = 2147483647

PINS = {
    "s1_npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "s1_json": "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21",
    "cmodel_npz": "3008d8f6b1f295cdd648f14e1ab2c20d864ce054a19f97e90e1620d22484e882",
    "cmodel_json": "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60",
    "stage0_inventory": "267c6c7cd2ad22bb857e024c382a75b29d1079845cbf692c97ff6e315ab85666",
    "stage0c_sums": "e7148c9ddff22ec60a1c0d5910ca8d319b79eaddeb7236c0c5d65e1d2ef68049",
    "s5p_sums": "1a72cb439120d910ee509fa0be7915924eb36b6a42fda8bda8006a0a92609935",
    "d16": {"mnvtune_v1": "0a618cf8f1cd28a9f77805a9f452a3e258697d857651faafe7790dd4c1e859ac",
            "genie_cv": "bf6e34f206752431ae060fd6ff5a818e4a354c3e8a458aa3740661eab73f1d3f",
            "genie_mec": "1826df9fbf699194594c49463c7b4572a941f8594545af48bc7b782279177709",
            "nuwro_cv": "08a0e46d7015446dbc3ecbe65eca06a017c5ec518ebd00a6b99e6d536b4236eb",
            "gibuu_cv": "683cd4f1811e7c9894f9814563a7613aefeed0187f268eecc2ffb4de238e6247"},
    "closure": "fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182",
    "floor": "eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08",
    # cmodel_5d.json positive_control.reporting16.closure_floor_max_abs (BUILD-REPORT.md section 3 rounds it to 3.2e-5)
    "floor_max_abs": 3.2179640496732276e-05,
    # FD-PLAN section 2.1, per-cell relative sigma in %, (median, min, max) at two decimals
    "table_2_1": {"C_e": (6.45, 4.05, 8.47), "C_total": (6.74, 4.14, 13.69), "minus_genie_mec": (6.74, 4.14, 13.69),
                  "minus_nuwro": (6.74, 4.09, 13.49), "minus_gibuu": (6.46, 4.11, 8.78)},
}

NULLEXP_F4 = ("ac929ea7866fbbfee0b59375633e5ef41f39d3f40826e0121ea71ca241a60012",
              "4cfed582b3acc7137fd1e8dd91448f06fa2c8f0bc6e681853bceebf6236e6b1c")
NULLEXP_PROD = ("789271bb76e0d589e8b3252ce72ef7e4fab40acdf1ab4744162bd64e339fd2ab",)
HYP = {"mnvtune_v1": "ceea00e77dbf4b64df24141435f131b40fa769f8fb038e9d7bc99758f504bf76",   # nullsJ/null-mnvtune_v1-J
       "genie_cv": "8c37f5459358d1eceb08745ac81644775a32cf84bd90839e67b298c6d1991cd0",     # nullsF/null-genie_cv-F
       "genie_mec": "9033c952ff56a2b85f03a4b21479e0e561641223d8538f573a632582bafd2563",    # nullsF/null-genie_mec-F
       "nuwro_cv": "9297a698f6573ea08fdb2047f621c24a18912afe0d5bafa8d8a01e304610f601",     # nullsF/null-nuwro_cv-F
       "gibuu_cv": "0080495c911143be29bbd780063a85b2890cd30d10c1e5b29f1f5cdb71013a77"}     # nullsF/null-gibuu_cv-F
ALT = {"P1": ("ratio_nd", "9240e4b3e419bbf5d62093bd246964ba8c507816d64d50db645acacf35ede19f"),   # altR/p1r-w3-...
       "P2": ("cond_ratio", "6a36c9bc0320339f7fe2c5a0c421ca8b3f4a0374f9e27d57952bcd6bf8729737"),  # altR/p2r-d5-...
       "P3": ("ratio_nd", "b3108969ced1fe552d5e1af5943da068214bdbd5738488562a5d8cc5cfd1efba")}   # altR/p3r-w2-...
RATIO = {"W1": "2a208df97fcd63937587d67098feb542c5e7e6759693bcc0609f0eb5fa0ff767",    # s5n/eavail-ratio-nuwro-over-genie
         "W2": "80e16f95702266d0e61b7529c8b5d36a5e4b140cfcde04640606b408c2b1e19b",    # s5e/w2-genie-mec-over-cv-eavailW
         "W3": "3455daf3ab5321a33314ca9ab51644c34134443cc49168c3be5c06a41d0e87bb",    # s5e/w3-nuwro-over-genie-pt-pz-eavail
         "gibuu": "c001dce873f2a758b0f62c1a8abc5c39a7bafdab4025429e350dbadd1bd8638b",  # stage0 receipts-A ratio
         "closure_nuwro": "38e47eb6b6ac63f6657022ae0cc5a2b5eaffc6a2e503735ce7222275771fea6e",  # prep ratios/L-5D-PV/nuwro
         "floor": "13bb1eae4ce0db4023bb29a5b98ca8b7e1e22288a1547f6a31a735fa1445435b"}  # prep ratios/L-5D-PV/tune_v1

# The 18 graded truths (FD-PLAN sections 1 and 2.1). group: vertex-family / non-vertex / prior (ruling 2: never pooled).
# own: the C_model,5D vertex left out of the grade matrix. sens: the declared sensitivity matrix's left-out vertex.
S5E = {"truth", "amplitude", "eavail_ratio_sha256"}
TRUTHS = (
    dict(name="nominal", row=1, group="prior", own=None, set="nominal", seeds=(800000, 40),
         ident={"truth": "nominal", "amplitude": 0.0, "eavail_ratio_sha256": None}),
    dict(name="W1", row=1, group="vertex-family", own="nuwro", set="W1", seeds=(803000, 20),
         ident={"truth": "eavail_shape", "amplitude": 1.0, "eavail_ratio_sha256": RATIO["W1"]}),
    dict(name="W2", row=1, group="vertex-family", own="genie_mec", set="W2", seeds=(804000, 20),
         ident={"truth": "ratio_nd", "amplitude": 1.0, "eavail_ratio_sha256": RATIO["W2"]}),
    dict(name="W3", row=1, group="vertex-family", own="nuwro", set="W3", seeds=(805000, 20),
         ident={"truth": "ratio_nd", "amplitude": 1.0, "eavail_ratio_sha256": RATIO["W3"]}),
    dict(name="q3", row=1, group="non-vertex", own=None, sens="nuwro", set="q3", seeds=(802000, 20),
         ident={"truth": "q3_given_eavail_w", "amplitude": 0.3, "eavail_ratio_sha256": None}),
    dict(name="stage0c_gibuu", row=2, group="vertex-family", own="gibuu", set="new_gibuu", seeds=(801000, 20),
         ident={"truth": "eavail_shape", "amplitude": 1.0, "eavail_ratio_sha256": RATIO["gibuu"]}),
    dict(name="closure_nuwro", row=3, group="vertex-family", own="nuwro", product="L-5D-PV_e_closure_nuwro"),
    dict(name="A7_mnvtune", row=4, group="prior", own=None, f4="mnvtune", d16="mnvtune_v1", cal="MnvTune_v1"),
    dict(name="A7_genie_cv", row=4, group="non-vertex", own=None, sens="genie_mec", f4="genie_cv", d16="genie_cv",
         cal="GENIE_2_12_10_CV"),
    dict(name="A7_genie_mec", row=4, group="vertex-family", own="genie_mec", f4="genie_mec", d16="genie_mec",
         cal="GENIE_2_12_10_MEC"),
    dict(name="A7_nuwro", row=4, group="vertex-family", own="nuwro", f4="nuwro_cv", d16="nuwro_cv", cal="NuWro_21_09"),
    dict(name="A7_gibuu", row=4, group="vertex-family", own="gibuu", f4="gibuu_cv", d16="gibuu_cv", cal="GiBUU_2019"),
    dict(name="P1r", row=6, group="vertex-family", own="nuwro", pow="P1_a1.0", alt="P1", ref="A7_mnvtune"),
    dict(name="P2r", row=6, group="vertex-family", own="nuwro", pow="P2_a1.0", alt="P2", ref="A7_mnvtune"),
    dict(name="P3r", row=6, group="vertex-family", own="genie_mec", pow="P3_a1.0", alt="P3", ref="A7_mnvtune"),
    dict(name="P1g", row=6, group="vertex-family", own="nuwro", pow="P1g_a1.0", alt="P1", ref="A7_genie_cv"),
    dict(name="P2g", row=6, group="vertex-family", own="nuwro", pow="P2g_a1.0", alt="P2", ref="A7_genie_cv"),
    dict(name="P3g", row=6, group="vertex-family", own="genie_mec", pow="P3g_a1.0", alt="P3", ref="A7_genie_cv"),
)
COUNTS = {"cal": {"MnvTune_v1": 1365, "GENIE_2_12_10_CV": 1366, "GENIE_2_12_10_MEC": 1343, "NuWro_21_09": 1751,
                  "GiBUU_2019": 1351},
          "pow": {"P1_a1.0": 193, "P2_a1.0": 195, "P3_a1.0": 195, "P1g_a1.0": 199, "P2g_a1.0": 193, "P3g_a1.0": 172},
          "f4": 16}
F4_SEEDS = tuple(range(970000, 970016))
OFFSET_PAIR = ("A7_mnvtune", "A7_genie_cv")
IN_SAMPLE_LABEL = "includes the truth's own vertex: not evidence"
MODEL_ONLY_LABEL = ("descriptive, no threshold: C_stat + C_model leaving out the own vertex; drops the interaction, "
                    "flux, detector, lateral and normalization blocks, so a lower bound on C_model's reach (ruling 2)")


class Stop(SystemExit):
    """A control refused: exit 1, nothing written."""

    def __init__(self, control, why):
        super().__init__(f"FAIL control {control}: {why}")


def report(control, name, ok, why="", guard=None):
    line = f"{'PASS' if ok else 'FAIL'} control {control} {name}{'' if ok else ': ' + why}"
    if guard is not None:
        guard.check("stdout", line)
    print(line, flush=True)
    if not ok:
        raise Stop(control, f"{name}: {why}")


def sa_call(control, fn, *args):
    """An s1_assemble helper whose own refusal (SystemExit) is reported as this control's."""
    try:
        return fn(*args)
    except Stop:
        raise
    except SystemExit as e:
        raise Stop(control, str(e.code)) from None


# ---------------------------------------------------------------- statistics


def chi2_sf_even(x: float, ndf: int) -> float:
    """P(chi2_ndf > x) for even ndf, exactly: exp(-x/2) sum_{i < ndf/2} (x/2)^i / i!."""
    if ndf % 2 or ndf <= 0:
        raise ValueError("ndf must be even and positive")
    if x <= 0:
        return 1.0
    h, term, total = x / 2.0, 1.0, 1.0
    for i in range(1, ndf // 2):
        term *= h / i
        total += term
    return float(math.exp(-h) * total) if h < 745 else 0.0


def unweighted(R: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Mean of the rows of R, and the noise of the mean: Cov_i(r) / B (ddof 1)."""
    B = R.shape[0]
    if B < 2:
        raise ValueError("an ensemble mean needs at least two experiments")
    return R.mean(axis=0), np.cov(R, rowvar=False, ddof=1) / B, float(B)


def weighted(R: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """The weighted mean b~ = sum w r / sum w and its ratio-estimator variance
    sum w^2 (r - b~)(r - b~)^T / (sum w)^2; B_eff = (sum w)^2 / sum w^2."""
    w = np.asarray(w, float)
    sw = w.sum()
    b = (w[:, None] * R).sum(axis=0) / sw
    Z = R - b
    return b, (Z.T * w ** 2) @ Z / sw ** 2, float(sw ** 2 / (w ** 2).sum())


def grade(b, N, C, cells=None) -> dict:
    """Per-cell pulls and the full-matrix chi2 of b against C + N (on a subset of cells if given)."""
    idx = np.arange(len(b)) if cells is None else np.asarray(cells)
    bb, M = np.asarray(b)[idx], (np.asarray(C) + np.asarray(N))[np.ix_(idx, idx)]
    L = np.linalg.cholesky(M)
    y = np.linalg.solve(L, bb)
    chi2 = float(y @ y)
    p = chi2_sf_even(chi2, len(idx))
    z = bb / np.sqrt(np.diag(M))
    out = {"cells": [f"R{c:02d}" for c in idx], "z": z.tolist(), "chi2": chi2, "ndf": int(len(idx)),
           "p": p if p >= P_FLOOR else 0.0, "p_below_floor": bool(p < P_FLOOR),
           "cells_abs_z_gt_2": [f"R{c:02d}" for c, v in zip(idx, z) if abs(v) > Z_TRIGGER]}
    out["p_lt_0.01"] = bool(p < P_TRIGGER)
    return out


def leave_out(Ce_rel: np.ndarray, S: np.ndarray, own: str | None) -> np.ndarray:
    """C_e,rel + sum_{j != own} s_j s_j^T (every vertex when own is None)."""
    keep = [j for j, v in enumerate(VERTICES) if v != own]
    return Ce_rel + S[keep].T @ S[keep]


def sigma_summary(sig: np.ndarray) -> tuple[float, float, float]:
    return tuple(round(100 * float(v), 2) for v in (np.median(sig), sig.min(), sig.max()))


# ---------------------------------------------------------------- the leak guard (ruling 6)


class LeakGuard:
    """Refuses an output that carries f, an absolute cell integral of any product X, f - X, or f/X, X/f, f/X - 1,
    X/f - 1 for any such X, with either sign (|value| is matched against |forbidden|, so 1 - X/f = (f - g)/f is
    caught), each within LEAK_REL relative; or any finite non-zero number below LEAK_FLOOR in magnitude (every
    absolute cross section here is of order 1e-39). A vector of 16 numbers (a list, or the last axis of an array) is
    cell-indexed and is matched cell by cell; any other number against every cell's values. Per cell and at 1e-13,
    ~1.4e5 legitimate residuals among ~1.6e6 forbidden values give an expected false refusal of order 1e-4
    (FD-F0-DECLARATION.md section 5.3)."""

    def __init__(self, f: np.ndarray, integrals: list[np.ndarray]):
        f = np.asarray(f, float)
        X = np.vstack([np.atleast_2d(np.asarray(a, float)) for a in integrals]) if integrals else np.empty((0, f.size))
        with np.errstate(divide="ignore", invalid="ignore"):
            V = np.abs(np.vstack([f[None, :], X, f - X, f / X, X / f, f / X - 1, X / f - 1]))
        self.cell = [self._clean(V[:, c]) for c in range(V.shape[1])]
        self.all = self._clean(V.ravel())

    @staticmethod
    def _clean(v):
        v = np.asarray(v, float).ravel()
        return np.sort(v[np.isfinite(v) & (v != 0)])

    @staticmethod
    def _hits(a: np.ndarray, table: np.ndarray) -> np.ndarray:
        if not a.size or not table.size:
            return np.zeros(a.size, bool)
        i = np.searchsorted(table, a)
        hit = np.zeros(a.size, bool)
        for k in (i - 1, i):
            t = table[np.clip(k, 0, table.size - 1)]
            hit |= np.abs(a - t) <= LEAK_REL * np.abs(t)
        return hit

    def offending(self, values, cell: int | None = None) -> int:
        a = np.abs(np.asarray(values, float).ravel())
        a = a[np.isfinite(a) & (a != 0)]
        return int(np.sum((np.abs(a) < LEAK_FLOOR) | self._hits(a, self.all if cell is None else self.cell[cell])))

    def count(self, obj) -> int:
        """Offending numbers anywhere in a JSON-able object, an array, a mapping of arrays or a string."""
        if isinstance(obj, str):
            return self.offending([float(t) for t in _NUM.findall(obj)])
        if isinstance(obj, bool) or obj is None:
            return 0
        if isinstance(obj, (int, float, np.floating, np.integer)):
            return self.offending([obj])
        if isinstance(obj, dict):
            return sum(self.count(k) + self.count(v) for k, v in obj.items())
        if isinstance(obj, np.ndarray) and obj.dtype.kind not in "fiu":
            return sum(self.count(x) for x in obj.ravel().tolist())
        if isinstance(obj, (list, tuple)) and not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in obj):
            return sum(self.count(x) for x in obj)
        a = np.asarray(obj, float)
        if a.ndim >= 1 and a.shape[-1] == N_CELLS:
            return sum(self.offending(a[..., c], c) for c in range(N_CELLS))
        return self.offending(a)

    def check(self, what: str, obj) -> None:
        n = self.count(obj)
        if n:
            print(f"REFUSED leak guard: {what} carries {n} number(s) equal to f, an absolute cell value or f - g "
                  f"(ruling 6); nothing more was written", file=sys.stderr, flush=True)
            raise SystemExit(3)


_NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


# ---------------------------------------------------------------- products


def array_header(path: Path, key: str):
    """(shape, dtype) of one npz member, read from its .npy header only."""
    with zipfile.ZipFile(path) as zf, zf.open(key + ".npy") as fh:
        version = np.lib.format.read_magic(fh)
        reader = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
        shape, _, dtype = reader(fh)
    return shape, dtype


def read_meta(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return json.loads(str(z["meta"]))


def estimator_problems(m: dict, refined: bool, top_seed: bool = True) -> list[str]:
    """(e): OmniFold LightGBM 100/8 at seed 42, 5 iterations, all-row binning, deterministic; refinement 400/31 at 45.
    s5n_pseudo and pvl_unfold record a top-level ``estimator_seed``; s5p_nullexp (rows 4-6) never writes one
    (s5p_nullexp.py:343-351), so there the seed is read from ``estimator_params[].random_state`` alone."""
    bad = []
    if top_seed and (m.get("estimator_seed"), m.get("iters")) != (42, 5):
        bad.append(f"seed/iters {(m.get('estimator_seed'), m.get('iters'))}")
    if not top_seed and ("estimator_seed" in m or m.get("iters") != 5):
        bad.append(f"estimator_seed present {'estimator_seed' in m} / iters {m.get('iters')}")
    ep = m.get("estimator_params") or []
    want = {"n_estimators": 100, "num_leaves": 8, "random_state": 42, "bin_construct_sample_cnt": ALL_ROWS,
            "deterministic": True, "force_row_wise": True, "subsample": 1.0, "colsample_bytree": 1.0}
    if len(ep) != 3 or any({k: e.get(k) for k in want} != want for e in ep):
        bad.append("estimator parameters")
    ref = m.get("refinement") or {}
    if refined:
        cp = ref.get("classifier_params") or {}
        wantr = {"n_estimators": 400, "num_leaves": 31, "random_state": 45, "bin_construct_sample_cnt": ALL_ROWS,
                 "deterministic": True}
        if ref.get("ran") is not True or {k: cp.get(k) for k in wantr} != wantr:
            bad.append("refinement parameters")
    elif ref.get("ran") is not False or ref.get("reason") != "no negative weights (signal-only reference)":
        bad.append("a signal-only reference must record that the refinement did not run")
    code = m.get("code_sha256") or {}
    if code.get("candidate") != "R" or code.get("candidate_refine_override") != {"n_estimators": 400, "num_leaves": 31}:
        bad.append("candidate R with the 400/31 override")
    if (m.get("input_npz_sha256"), m.get("bkg_dump_sha256")) != (INPUT_NPZ_SHA256, BKG_SHA256):
        bad.append("input digests")
    return bad


def meta_problems(path: Path, m: dict, kind: str, spec: dict) -> list[str]:
    bad = estimator_problems(m, refined=kind != "closure", top_seed=kind in ("s5e", "closure"))
    seed = m.get("pseudo_seed")
    if kind in ("s5e", "f4", "cal", "pow") and not path.stem.endswith(f"_s{seed}"):
        bad.append(f"pseudo_seed {seed} is not the filename's")
    if kind == "s5e":
        if (m.get("schema"), m.get("config"), m.get("bkg_mode"), m.get("no_background")) != (
                "s5n-unfold/1", "deterministic", "negweight-refined", False):
            bad.append("schema/config/background")
        if {k: m.get(k) for k in S5E} != spec["ident"]:
            bad.append(f"truth {({k: m.get(k) for k in S5E})}")
        s0, n = spec["seeds"]
        if not (isinstance(seed, int) and s0 <= seed < s0 + n):
            bad.append(f"pseudo_seed {seed} outside {s0}..{s0 + n - 1}")
    elif kind == "closure":
        want = {"schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "closure": True,
                "features": ["pt", "pz", "eavail", "q3", "W"], "ratio_sha256": spec["ratio"]}
        if {k: m.get(k) for k in want} != want:
            bad.append("pvl closure identity")
    else:
        code = (m.get("code_sha256") or {}).get("s5p_nullexp.py")
        dev = m.get("development")
        if (m.get("schema"), m.get("config"), m.get("capacity")) != ("s5p-null-experiment/1", "R", None):
            bad.append("schema/config/capacity")
        if (m.get("hypothesis") or {}).get("sha256") != spec["hyp"]:
            bad.append("hypothesis")
        if kind == "f4":
            if code not in NULLEXP_F4 or dev != {"expectation": True, "mc_fraction": "half"} or m.get("nuisance_draw") is not None:
                bad.append("f4: code, expectation mode or nuisance draws")
            if m.get("alternative") is not None:
                bad.append("f4: an alternative")
            if seed not in F4_SEEDS:
                bad.append(f"f4: pseudo_seed {seed}")
        else:
            nd = m.get("nuisance_draw") or {}
            flux = nd.get("flux")
            if code not in NULLEXP_PROD or dev != {"expectation": False, "mc_fraction": "half"}:
                bad.append(f"{kind}: code or mode")
            if not (isinstance(flux, int) and 0 <= flux < 100):
                bad.append(f"{kind}: flux universe {flux}")
            alt = m.get("alternative")
            if kind == "cal" and alt is not None:
                bad.append("cal: an alternative")
            if kind == "pow":
                t, sha = ALT[spec["alt"]]
                if not alt or (alt.get("truth"), alt.get("amplitude"), alt.get("sha256")) != (t, 1.0, sha):
                    bad.append("pow: alternative")
    for key in ("xsec_flat", "xtrue_flat"):
        try:
            shape, dtype = array_header(path, key)
        except KeyError:
            bad.append(f"no {key}")
            continue
        if shape != (N_FINE,) or dtype != np.dtype("<f8"):
            bad.append(f"{key} {shape} {dtype}")
    return bad


def relative_manifest(path: Path, root: Path) -> dict[str, str]:
    """``sha256  relative/path`` lines -> {absolute path: sha256}."""
    return {str(root / p): s for p, s in sa.load_manifest(path).items()}


def listed_set(manifest: dict[str, str], directory: Path) -> list[Path]:
    """The manifest's .npz entries directly in ``directory``; refuses unless the directory holds exactly those."""
    want = sorted(p for p in manifest if Path(p).parent == directory and p.endswith(".npz"))
    have = sorted(str(p) for p in directory.glob("*.npz"))
    if want != have:
        extra, missing = sorted(set(have) - set(want)), sorted(set(want) - set(have))
        raise Stop(1, f"{directory}: {len(extra)} unlisted and {len(missing)} missing products")
    return [Path(p) for p in want]


def f4_inputs(d16_dir: Path, f4_root: Path, label: str) -> list[tuple[Path, str]]:
    """The 16 half-MC products of one A7 truth with the sha256 its D16 record carries (inputs[].a, a_sha256)."""
    d = json.loads((d16_dir / f"D16-{label}.json").read_text())
    out = [(Path(i["a"]), i["a_sha256"]) for i in d["inputs"]]
    return sorted(out)


def f4_inventory_lines(d16_dir: Path) -> list[str]:
    """The HPSS preserve inventory of the 80 f4 half products, in sha256sum format, from the D16 records."""
    lines = []
    for label in PINS["d16"]:
        lines += [f"{s}  {p}" for p, s in f4_inputs(d16_dir, Path("/"), label)]
    return lines


# ---------------------------------------------------------------- main


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--definition", type=Path, required=True, help="nd-unfolding/pv-ladder/readouts/h2_definition.json")
    ap.add_argument("--s1-npz", type=Path, required=True, help="s1-20261024/s1_assembly.npz")
    ap.add_argument("--s1-json", type=Path, required=True, help="the committed s1/readout/s1_assembly.json")
    ap.add_argument("--cmodel-npz", type=Path, required=True, help="cmodel5d-20261024/out/cmodel_5d.npz")
    ap.add_argument("--cmodel-json", type=Path, required=True, help="nd-unfolding/pv-ladder/readouts/cmodel_5d.json")
    ap.add_argument("--flux-constraint", type=Path, required=True, help="sorted_NuEConstraint_FHC_RHC_IMD.txt")
    ap.add_argument("--d16-dir", type=Path, required=True, help="docs/orchestration/state/s5p/stage3/f4")
    ap.add_argument("--f4-root", type=Path, required=True, help="s5p-20260926/runs/s3r/f4")
    ap.add_argument("--stage0-inventory", type=Path, required=True, help="5d-design-20261023/stage0/INVENTORY.sha256")
    ap.add_argument("--s5e-assess", type=Path, required=True, help="s5e-20260925/runs/cand/assess")
    ap.add_argument("--stage0c-sums", type=Path, required=True, help="stage0/receipts-A/products.sha256")
    ap.add_argument("--stage0c-root", type=Path, required=True, help="5d-stage0-20261023")
    ap.add_argument("--pvl-products", type=Path, required=True, help="pv-ladder-20261024/products")
    ap.add_argument("--s5p-sums", type=Path, required=True, help="state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt")
    ap.add_argument("--s5p-root", type=Path, required=True, help="s5p-20260926")
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-npz", type=Path, required=True)
    return ap.parse_args(argv)


def require(control, path: Path, want: str, what: str):
    got = sa.sha256(path)
    if got != want:
        raise Stop(control, f"{what} {path}: sha256 {got} != {want}")


def run(a, pins=None) -> int:
    pins = PINS if pins is None else pins
    for p in (a.out_json, a.out_npz):
        if p.exists():
            raise Stop("-", f"refusing to overwrite {p}")

    # 0. the 80 f4 half products against their D16 records, before any other input is opened
    f4 = {}
    for t in TRUTHS:
        if "f4" not in t:
            continue
        require(0, a.d16_dir / f"D16-{t['d16']}.json", pins["d16"][t["d16"]], "D16 record")
        items = f4_inputs(a.d16_dir, a.f4_root, t["d16"])
        d = a.f4_root / f"{t['f4']}_half"
        if len(items) != COUNTS["f4"] or any(p.parent != d for p, _ in items):
            raise Stop(0, f"{t['d16']}: D16 lists {len(items)} products, or one outside {d}")
        for p, s in items:
            require(0, p, s, "f4 product")
        if sorted(str(p) for p in d.glob("*.npz")) != sorted(str(p) for p, _ in items):
            raise Stop(0, f"{d} holds products its D16 record does not list")
        f4[t["name"]] = [p for p, _ in items]
    report(0, "f4 products match their D16 sha256", True)

    # 1. every other product and matrix, and the committed records, against their recorded sha256
    for key, path in (("s1_npz", a.s1_npz), ("s1_json", a.s1_json), ("cmodel_npz", a.cmodel_npz),
                      ("cmodel_json", a.cmodel_json), ("stage0_inventory", a.stage0_inventory),
                      ("stage0c_sums", a.stage0c_sums), ("s5p_sums", a.s5p_sums)):
        require(1, path, pins[key], key)
    inv = sa.load_manifest(a.stage0_inventory)
    s0c = relative_manifest(a.stage0c_sums, a.stage0c_root)
    s5p = relative_manifest(a.s5p_sums, a.s5p_root)
    sets: dict[str, list[Path]] = {}
    for t in TRUTHS:
        if t["row"] == 1:
            sets[t["name"]] = listed_set(inv, a.s5e_assess / t["set"])
        elif t["row"] == 2:
            sets[t["name"]] = listed_set(s0c, a.stage0c_root / "runs" / t["set"])
        elif t["row"] == 3:
            sets[t["name"]] = [a.pvl_products / f"{t['product']}.npz"]
        elif t["row"] == 4:
            sets[t["name"]] = f4[t["name"]]
            sets["cal:" + t["name"]] = listed_set(s5p, a.s5p_root / "runs/prod/cal" / t["cal"])
        elif t["row"] == 6:
            sets[t["name"]] = listed_set(s5p, a.s5p_root / "runs/prod/pow" / t["pow"])
    floor_path = a.pvl_products / "L-5D-PV_e_closure_tune_v1.npz"
    want_sha = {**inv, **s0c, **s5p}
    for name, paths in sets.items():
        if name in f4:
            continue
        for p in paths:
            if name == "closure_nuwro":
                require(1, p, pins["closure"], "closure")
            else:
                require(1, p, want_sha[str(p)], name)
    require(1, floor_path, pins["floor"], "closure floor")
    w_all = sa_call(1, sa.flux_weights, a.flux_constraint)
    report(1, f"{sum(map(len, sets.values())) + 1} products and 8 records match their recorded sha256", True)

    # 2. meta and array headers of every product
    spec_of = {}
    for t in TRUTHS:
        if t["row"] in (1, 2):
            spec_of[t["name"]] = ("s5e", t)
        elif t["row"] == 3:
            spec_of[t["name"]] = ("closure", {"ratio": RATIO["closure_nuwro"]})
        elif t["row"] == 4:
            spec_of[t["name"]] = ("f4", {"hyp": HYP[t["d16"]]})
            spec_of["cal:" + t["name"]] = ("cal", {"hyp": HYP[t["d16"]]})
        else:
            ref = next(r for r in TRUTHS if r["name"] == t["ref"])
            spec_of[t["name"]] = ("pow", {"hyp": HYP[ref["d16"]], "alt": t["alt"]})
    metas: dict[str, list[dict]] = {}
    for name, paths in sets.items():
        kind, spec = spec_of[name]
        metas[name] = []
        for p in paths:
            m = read_meta(p)
            bad = meta_problems(p, m, kind, spec)
            if bad:
                raise Stop(2, f"{p.name}: {'; '.join(bad)}")
            metas[name].append(m)
    fm = read_meta(floor_path)
    bad = meta_problems(floor_path, fm, "closure", {"ratio": RATIO["floor"]})
    if bad:
        raise Stop(2, f"{floor_path.name}: {'; '.join(bad)}")
    report(2, "every product was made by (e) at its declared truth", True)

    # 3. counts
    for t in TRUTHS:
        n = len(sets[t["name"]])
        want = {1: t.get("seeds", (0, 0))[1], 2: t.get("seeds", (0, 0))[1], 3: 1, 4: COUNTS["f4"],
                6: COUNTS["pow"].get(t.get("pow"))}[t["row"]]
        if n != want or len({m.get("pseudo_seed") for m in metas[t["name"]]}) != n:
            raise Stop(3, f"{t['name']}: {n} products, {want} declared, or a repeated seed")
        if t["row"] == 4:
            nc = len(sets["cal:" + t["name"]])
            if nc != COUNTS["cal"][t["cal"]] or len({m["pseudo_seed"] for m in metas["cal:" + t["name"]]}) != nc:
                raise Stop(3, f"cal {t['cal']}: {nc} products, {COUNTS['cal'][t['cal']]} declared")
    n_all = sum(map(len, sets.values()))
    report(3, f"counts as declared ({n_all} products: {n_all - sum(COUNTS['cal'].values())} graded, "
              f"{sum(COUNTS['cal'].values())} for the offset control)", True)

    # 4. matrices
    U = sa.functional_matrix(sa_call(4, sa.fine_map, a.definition))
    defn = json.loads(a.definition.read_text())
    lo = [c["id"] for c in defn["reporting_cells"] if c["box"]["pz"][1] <= 4.5]
    if sorted(lo) != list(GIBUU_CELLS):
        raise Stop(4, f"the p_parallel < 4.5 cells are {sorted(lo)}")
    s1j, cj = json.loads(a.s1_json.read_text()), json.loads(a.cmodel_json.read_text())
    if s1j.get("assembly_sha256") != pins["s1_npz"] or tuple(cj["vertices"]) != VERTICES:
        raise Stop(4, "the S1 readout names another assembly, or C_model's vertices differ")
    with np.load(a.s1_npz, allow_pickle=False) as z:
        s1m = json.loads(str(z["meta"]))
        f = np.asarray(z["f"], float)
        blocks = {k: np.asarray(z["C_" + k.replace(":", "_")], float) for k in s1m["blocks"]}
        Ce, Ct = np.asarray(z["C_e"], float), np.asarray(z["C_total"], float)
        Cmf, Cma = np.asarray(z["C_model_frac"], float), np.asarray(z["C_model_abs"], float)
        U32 = np.asarray(z["U"])
    with np.load(a.cmodel_npz, allow_pickle=False) as z:
        S = np.asarray(z["S"], float)
    ff = np.outer(f, f)
    scale = np.abs(np.diag(Ct)).max()
    checks = {
        "U is S1's float32 functional matrix": np.array_equal(U32, U.astype(np.float32)),
        "f is positive on every cell": bool(f.shape == (N_CELLS,) and np.all(f > 0)),
        "C_e is the sum of S1's blocks": np.allclose(sum(blocks.values()), Ce, rtol=TOL, atol=TOL * scale),
        "C_total = C_e + C_model_abs": np.allclose(Ce + Cma, Ct, rtol=TOL, atol=TOL * scale),
        "C_model_abs = diag(f) C_model diag(f)": np.allclose(Cmf * ff, Cma, rtol=TOL, atol=TOL * scale),
        "S (npz) is C_model,5D's committed S": S.shape == (3, N_CELLS) and np.array_equal(S, np.asarray(cj["S"], float)),
        "C_model = S^T S": np.allclose(S.T @ S, Cmf, rtol=TOL, atol=TOL * np.abs(np.diag(Cmf)).max()),
        "C_total's relative sigma is the committed one": np.allclose(
            np.sqrt(np.diag(Ct)) / f, np.asarray(s1j["relative_sigma"]["C_total"], float), rtol=TOL, atol=0),
    }
    Ce_rel, Cstat_rel = Ce / ff, blocks["stat"] / ff
    sig_e_json = np.asarray(s1j["relative_sigma"]["C_e"], float)
    mats = {"C_e": Ce_rel, "C_total": leave_out(Ce_rel, S, None)}
    mats.update({f"minus_{v}": leave_out(Ce_rel, S, v) for v in VERTICES})
    keep = {"C_e": [], "C_total": list(VERTICES)}
    keep.update({f"minus_{v}": [u for u in VERTICES if u != v] for v in VERTICES})
    sig = {}
    for k, M in mats.items():
        sig[k] = np.sqrt(np.diag(M))
        from_json = np.sqrt(sig_e_json ** 2 + sum(S[VERTICES.index(u)] ** 2 for u in keep[k]))
        checks[f"{k}: sigma from S1's npz equals sigma from the committed JSONs"] = np.allclose(sig[k], from_json, rtol=TOL, atol=0)
        checks[f"{k}: FD-PLAN section 2.1 row reproduces"] = sigma_summary(sig[k]) == pins["table_2_1"][k]
    ev = np.linalg.eigvalsh(Cstat_rel)
    checks["C_stat,rel is full rank"] = bool(ev.min() > 0 and int(np.sum(ev > TOL * ev.max())) == N_CELLS)
    for name, ok in checks.items():
        report(4, name, bool(ok), "differs")

    # integrals of every product (cell values are read from here on; nothing is written before every control passes)
    def integrate(paths):
        Xh, Xt = [], []
        for p in paths:
            with np.load(p, allow_pickle=False) as z:
                Xh.append(U @ np.asarray(z["xsec_flat"], float))
                Xt.append(U @ np.asarray(z["xtrue_flat"], float))
        return np.array(Xh), np.array(Xt)
    I = {name: integrate(paths) for name, paths in sets.items()}
    I["floor"] = integrate([floor_path])
    guard = LeakGuard(f, [x for pair in I.values() for x in pair])

    def rel(name):
        with np.errstate(divide="ignore", invalid="ignore"):
            return I[name][0] / I[name][1] - 1.0

    # 5. the closure's 16-cell bias is the one C_model,5D's build printed
    rc = rel("closure_nuwro")[0]
    rec = np.asarray(cj["positive_control"]["reporting16"]["bias_cells"], float)
    report(5, "closure bias equals cmodel_5d.json reporting16.bias_cells", bool(np.allclose(rc, rec, rtol=0, atol=TOL)),
           "differs", guard)

    # 6. the closure floor, reported first, not graded
    floor = float(np.max(np.abs(rel("floor")[0])))
    report(6, f"closure floor max |bias| {floor:.6e} reproduces the recorded value",
           bool(abs(floor - pins["floor_max_abs"]) <= TOL), "differs", guard)

    # 7. the offset control (gates row 6 only)
    est, offsets = {}, {}
    for t in TRUTHS:
        R = rel(t["name"])
        if t["row"] == 3:
            est[t["name"]] = (R[0], np.zeros((N_CELLS, N_CELLS)), None, "noise-free closure (N = 0)")
        elif t["row"] in (1, 2, 4):
            b, N, B = unweighted(R)
            est[t["name"]] = (b, N, B, "unweighted mean")
        if t["row"] == 4:
            w = w_all[[m["nuisance_draw"]["flux"] for m in metas["cal:" + t["name"]]]]
            bw, Nw, Beff = weighted(rel("cal:" + t["name"]), w)
            b4, N4, _ = est[t["name"]][:3]
            offsets[t["name"]] = {"O": bw - b4, "N_O": Nw + N4, "B_eff": Beff, "N_cal": Nw,
                                  "row4_trace_share": float(np.trace(N4) / np.trace(Nw + N4))}
    pairs = []
    names4 = [t["name"] for t in TRUTHS if t["row"] == 4]
    for i, x in enumerate(names4):
        for y in names4[i + 1:]:
            D = offsets[x]["O"] - offsets[y]["O"]
            g = grade(D, offsets[x]["N_O"] + offsets[y]["N_O"], np.zeros((N_CELLS, N_CELLS)))
            pairs.append({"a": x, "b": y, "chi2": g["chi2"], "ndf": g["ndf"], "p": g["p"],
                          "p_below_floor": g["p_below_floor"], "gating": (x, y) == OFFSET_PAIR})
    gate = next(p for p in pairs if p["gating"])
    offset_pass = bool(gate["p"] >= 0.01)
    line = (f"{'PASS' if offset_pass else 'FAIL'} control 7 offset control: chi2_16 {gate['chi2']:.3f}, "
            f"p {gate['p']:.4g}{'' if offset_pass else ' -> row 6 is descriptive and ungraded'}")
    guard.check("stdout", line)
    print(line, flush=True)
    for t in TRUTHS:
        if t["row"] != 6:
            continue
        m = metas[t["name"]]
        bw, Nw, Beff = weighted(rel(t["name"]), w_all[[x["nuisance_draw"]["flux"] for x in m]])
        o = offsets[t["ref"]]
        est[t["name"]] = (bw - o["O"], Nw + o["N_O"], Beff,
                          f"NuE-weighted mean less O_{t['ref']} (first-order offset correction)", bw)

    # 8. every truth integral positive on all 16 cells
    for name, (_, Xt) in I.items():
        if not np.all(Xt > 0):
            raise Stop(8, f"{name}: a truth integral is not positive")
    report(8, "every truth integral is positive on all 16 cells", True, guard=guard)

    # the grades
    truths, by = [], {}
    for t in TRUTHS:
        b, N, B, how = est[t["name"]][:4]
        graded = t["row"] != 6 or offset_pass
        C = mats["C_total"] if t["own"] is None else mats[f"minus_{t['own']}"]
        Cm = leave_out(Cstat_rel, S, t["own"])
        rec = {"name": t["name"], "row": t["row"], "group": t["group"], "own_vertex": t["own"],
               "n_experiments": len(sets[t["name"]]), "B_eff": B, "estimator": how, "graded": graded,
               "grade_matrix": "C_total" if t["own"] is None else f"C_total minus {t['own']}",
               "bias": b.tolist(), "noise_sigma": np.sqrt(np.diag(N)).tolist(), "grade": grade(b, N, C),
               "model_only": dict(grade(b, N, Cm), label=MODEL_ONLY_LABEL)}
        if not graded:
            rec["label"] = "descriptive and ungraded: the offset control failed (control 7)"
        if t["row"] == 6:
            rec["bias_uncorrected"] = est[t["name"]][4].tolist()
            rec["offset_from"] = t["ref"]
        if t["own"] is not None:
            rec["in_sample"] = dict(grade(b, N, mats["C_total"]), label=IN_SAMPLE_LABEL)
        if t.get("sens"):
            rec["sensitivity"] = dict(grade(b, N, mats[f"minus_{t['sens']}"]), matrix=f"C_total minus {t['sens']}",
                                      label="declared sensitivity matrix: descriptive")
        if t["own"] == "gibuu":
            rec["p_parallel_lt_4p5"] = dict(grade(b, N, C, GIBUU_CELLS), label="the eight p_parallel < 4.5 cells: descriptive")
        rec["listed"] = bool(graded and (rec["grade"]["cells_abs_z_gt_2"] or rec["grade"]["p_lt_0.01"]))
        truths.append(rec)
        if graded:
            key = t["group"]
            g = by.setdefault(key, {"truths": 0, "cells": 0, "cells_abs_z_gt_2": 0, "truths_p_lt_0.01": 0, "by_family": {}})
            fam = g["by_family"].setdefault(t["own"] or t["name"], {"truths": 0, "cells_abs_z_gt_2": 0, "truths_p_lt_0.01": 0})
            nz, pl = len(rec["grade"]["cells_abs_z_gt_2"]), int(rec["grade"]["p_lt_0.01"])
            for d in (g, fam):
                d["truths"] += 1
                d["cells_abs_z_gt_2"] += nz
                d["truths_p_lt_0.01"] += pl
            g["cells"] += N_CELLS
    for g in by.values():
        g["gaussian_reference_cells"] = g["cells"] * GAUSS_CELL
        g["gaussian_reference_truths"] = g["truths"] * P_TRIGGER
    tot = {k: sum(g[k] for g in by.values()) for k in ("truths", "cells", "cells_abs_z_gt_2", "truths_p_lt_0.01")}
    tot.update(gaussian_reference_cells=tot["cells"] * GAUSS_CELL, gaussian_reference_truths=tot["truths"] * P_TRIGGER,
               label="the denominators of ruling 2; the counts are read by group, never pooled")

    readout = {
        "schema": "fd-f0-readout/1",
        "labels": {"what": "the (e) estimator's bias at 18 fake-data truths on R00-R15, graded against S1's C_total",
                   "not": "not a coverage gate (DECISION-20261024 route item 3); not held-out truths; the detector "
                          "response is not probed; prints no f, no absolute cell value and no f - g (ruling 6)",
                   "thresholds": "reporting triggers for a proposed limitation, not gates (ruling 2)",
                   "gaussian_reference": "context only: b is a deterministic bias, not a Gaussian draw"},
        "cells": [f"R{c:02d}" for c in range(N_CELLS)],
        "controls": {"passed": [0, 1, 2, 3, 4, 5, 6, 8], "offset_control_7": {"pass": offset_pass, "pair": list(OFFSET_PAIR),
                     "rule": "P(chi2_16 > chi2) >= 0.01", "chi2": gate["chi2"], "p": gate["p"],
                     "p_below_floor": gate["p_below_floor"], "pairs_descriptive": [p for p in pairs if not p["gating"]],
                     "B_eff_calibration": {k: v["B_eff"] for k, v in offsets.items()},
                     "row4_noise_trace_share": {k: v["row4_trace_share"] for k, v in offsets.items()}},
                     "closure_floor_max_abs": floor},
        "relative_sigma": {k: v.tolist() for k, v in sig.items()},
        "relative_sigma_summary_percent": {k: list(sigma_summary(v)) for k, v in sig.items()},
        "truths": truths,
        "triggers": {"rule": "a cell with |z| > 2, or a truth with P(chi2_16 > chi2) < 0.01, against the grade matrix",
                     "by_group": by, "all_graded": tot,
                     "listed": [{"truth": r["name"], "cells": r["grade"]["cells_abs_z_gt_2"],
                                 "p_lt_0.01": r["grade"]["p_lt_0.01"]} for r in truths if r["listed"]]},
        "inputs_sha256": {k: pins[k] for k in ("s1_npz", "s1_json", "cmodel_npz", "cmodel_json", "stage0_inventory",
                                                 "stage0c_sums", "s5p_sums", "closure", "floor")} | {
            "definition": sa.DEFINITION_SHA256, "constraint": sa.CONSTRAINT_SHA256, "d16": pins["d16"]},
        "code_sha256": {"fd_f0_regrade.py": sa.sha256(Path(__file__).resolve()),
                        "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve()),
                        "s5p_stage1_inspect.py": sa.sha256(Path(sa.s1.__file__).resolve())},
        "argv": [str(x) for x in sys.argv],
    }
    table = {"names": np.array([t["name"] for t in TRUTHS])}
    for name in sets:
        key = name.replace(":", "_")
        table[f"r_{key}"] = rel(name)
        table[f"seed_{key}"] = np.array([m.get("pseudo_seed") or 0 for m in metas[name]], np.int64)
        if any("nuisance_draw" in m and m["nuisance_draw"] for m in metas[name]):
            table[f"flux_{key}"] = np.array([m["nuisance_draw"]["flux"] for m in metas[name]], np.int64)

    lines = []
    for gname, g in sorted(by.items()):
        lines.append(f"[F0] {gname}: {g['cells_abs_z_gt_2']} of {g['cells']} cells |z| > 2 (Gaussian reference "
                     f"{g['gaussian_reference_cells']:.2f}); {g['truths_p_lt_0.01']} of {g['truths']} truths p < 0.01 "
                     f"(reference {g['gaussian_reference_truths']:.2f})")
    lines.append(f"[F0] denominators: {tot['cells_abs_z_gt_2']} of {tot['cells']} cells, {tot['truths_p_lt_0.01']} of "
                 f"{tot['truths']} truths (references {tot['gaussian_reference_cells']:.2f}, "
                 f"{tot['gaussian_reference_truths']:.2f}); read by group")
    guard.check("the readout JSON", readout)
    guard.check("the per-experiment table", table)
    guard.check("stdout", "\n".join(lines))
    tmp_npz = a.out_npz.with_name(a.out_npz.name + ".partial.npz")
    tmp_json = a.out_json.with_name(a.out_json.name + ".partial")
    try:   # both files are renamed into place only after the last check; a refusal leaves neither
        np.savez_compressed(tmp_npz, **table)
        readout["table_sha256"] = sa.sha256(tmp_npz)
        guard.check("the readout JSON", readout)
        tmp_json.write_text(json.dumps(readout, indent=1) + "\n")
        lines.append(json.dumps({"wrote": [str(a.out_json), str(a.out_npz)], "readout_sha256": sa.sha256(tmp_json),
                                 "table_sha256": readout["table_sha256"]}))
        guard.check("stdout", lines[-1])
    except BaseException:
        tmp_npz.unlink(missing_ok=True)
        tmp_json.unlink(missing_ok=True)
        raise
    os.replace(tmp_npz, a.out_npz)
    os.replace(tmp_json, a.out_json)

    print("\n".join(lines), flush=True)
    return 0


def main(argv=None) -> int:
    a = build_args(argv)
    try:
        return run(a)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001  (an unexpected error stops the run; its message is redacted of numbers)
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(f"FAIL unexpected {type(e).__name__} at {Path(tb.filename).name}:{tb.lineno}: "
              f"{_NUM.sub('#', str(e))[:300]}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

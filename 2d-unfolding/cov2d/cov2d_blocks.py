"""COV2D's covariance blocks at a truth (COV2D-DECLARATION.md section 4.4; section 9.8; the director's R3 and R6 of
2026-11-04): C_T = C_univ + C_lat + C_norm + C_stat + C08 + C_model_abs on E_R's 205 reported cells, by the RE-2
rollup's own functions, imported, not copied (``re2c_rollup.universe_block``, ``x01``, ``flux_weights``, ``band_cov``
through ``universe_block``). root_6_28.

* ``universe_block`` is called with a cells object holding E_R's 205-cell mask and x = x_hat_T, so its normalization
  entry is (0.014 x_hat_T)(0.014 x_hat_T)^T on E_R's cells (section 4.4). Its per-band dict must hold exactly the 38
  universe bands, the 5 lateral bands (Muon_Energy_MINOS replaced by its X01 rescale) and the normalization entry, and
  the per-band blocks must sum to its total (R6). C_univ and C_lat are the dict's sums over those band sets; the
  normalization is counted once.
* C_stat: the sample covariance of the 300 replicas, ddof 1 (``numpy.cov``, as the rollup computes S5's).
* C08 carried: diag(x_hat_T / x_R) C08_R diag(x_hat_T / x_R), with C08_R the ``c08`` key of part C's
  ``outA/cov2d_Q_205.npz`` (sha256 7153b194..., RE2-PARTC-REPORT.md:134 and :364-365; R3).
* C_model_abs: diag(x_hat_T) C_model diag(x_hat_T), with C_model = ``build_cmodel.cmodel`` of the committed
  ``pv2d/cmodel/cmodel_2d.json`` shift matrix, whose matrix sha256 must be 11fe6818... (RE2-PARTC-REPORT.md:250).
* C_model- (section 6's leave-out-MEC readout, R3): ``build_cmodel.cmodel`` over the ``nuwro`` and ``gibuu`` rows of the
  same shift matrix, "constructed from the committed shift matrix, not a named part-C product". Its control is the
  full construction's sha above; if that fails the readout is INVALID. Descriptive only; it changes no verdict.
* Section 9.8: C_T symmetric and positive semi-definite to 1e-12 of its largest eigenvalue; the rank above 1e-12 is the
  ndf, recorded.

Reads: the rollup's functions open their files with ROOT, which cannot take O_NOATIME. ``noatime_inputs`` therefore
copies every file they read into a private directory through O_NOATIME (each pinned file against its digest) and points
the rollup's call-time globals at the copies, so no input's atime moves (section 7).

MEASURES: covariance blocks from supplied products. CANNOT AUTHORIZE: a verdict.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PARTC = REPO / "2d-unfolding" / "re2" / "partc"
CMODEL_DIR = REPO / "2d-unfolding" / "pv2d" / "cmodel"
for p in (HERE, PARTC, CMODEL_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402

NORM_KEY = "__Normalization_flat"
CMODEL_JSON = CMODEL_DIR / "cmodel_2d.json"
CMODEL_JSON_SHA = "aabc66d106a49484d486fb055bfb4280187898f98ca406e010f153af57702dd0"
C_MODEL_SHA = "11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470"
C08_R_FILE = ("/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/outA/cov2d_Q_205.npz",
              "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2")
MINUS_VERTICES = ("nuwro", "gibuu")
TOL = 1e-12


def rollup():
    import re2c_rollup
    return re2c_rollup


def read_noatime(path) -> tuple[bytes, str]:
    fd = os.open(str(path), os.O_RDONLY | os.O_NOATIME)
    try:
        parts = []
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            parts.append(b)
    finally:
        os.close(fd)
    data = b"".join(parts)
    return data, hashlib.sha256(data).hexdigest()


class CellsT:
    """What ``universe_block`` reads from a cells object: the reported-cell mask and x on it."""
    def __init__(self, rep: np.ndarray, x: np.ndarray):
        self.rep = np.asarray(rep, bool)
        self.x = np.asarray(x, np.float64)
        if self.x.shape != (int(self.rep.sum()),):
            raise c.Refusal("x must hold one value per reported cell")


def c_model(json_path=CMODEL_JSON, want_sha=CMODEL_JSON_SHA) -> tuple[np.ndarray, np.ndarray | None, dict]:
    """(C_model, C_model- or None, record). C_model must reproduce its pinned matrix sha256; C_model- is None (the
    readout INVALID) unless it does."""
    import build_cmodel as B
    data, sha = read_noatime(json_path)
    if want_sha is not None and sha != want_sha:
        raise c.Refusal(f"{json_path} sha256 {sha} != {want_sha}")
    M = json.loads(data)
    S = np.asarray(M["S"], np.float64)
    order = list(M["vertices"])
    C = B.cmodel(S)
    full = B.matrix_sha256(C)
    rec = {"json_sha256": sha, "vertices": order, "full_matrix_sha256": full, "full_matrix_sha256_ok": full == C_MODEL_SHA,
           "cells": [int(x) for x in M["cells"]] if isinstance(M["cells"], list) else M["cells"]}
    if not rec["full_matrix_sha256_ok"]:
        raise c.Refusal(f"C_model's matrix sha256 {full} != {C_MODEL_SHA}")
    minus = B.cmodel(S[[order.index(v) for v in MINUS_VERTICES]])
    rec["minus_label"] = "constructed from the committed shift matrix, not a named part-C product"
    return C, minus, rec


def psd_checks(C: np.ndarray) -> dict:
    """Section 9.8: symmetry and PSD to 1e-12 of the largest eigenvalue, and the rank above it (the ndf)."""
    asym = float(np.max(np.abs(C - C.T)) / np.max(np.abs(C)))
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    top = float(ev[-1])
    out = {"asymmetry": asym, "min_eig_over_max": float(ev[0] / top), "ndf": int(np.sum(ev > TOL * top))}
    out["pass"] = asym <= TOL and out["min_eig_over_max"] >= -TOL
    return out


def assemble(x_T, rep, bands: dict, minos_x, w_flux, X_rep, x_R, C08_R, C_model, C_model_minus=None) -> dict:
    """Every block at T on E_R's cells. ``bands``: {band: (n_universes, 205)} for the 38 universe bands and the 5 lateral
    bands (Muon_Energy_MINOS's raw rows; universe_block replaces them by ``minos_x``)."""
    ro = rollup()
    x_T = np.asarray(x_T, np.float64)
    cells = CellsT(rep, x_T)
    ublocks, tot = ro.universe_block(cells, bands, w_flux, minos_x)
    want = set(c.ORDER) | set(c.LATERAL_BANDS) | {NORM_KEY}
    if set(ublocks) != want:
        raise c.Refusal(f"universe_block's keys {sorted(set(ublocks) ^ want)} differ from the declared 38 + 5 + norm")
    total = np.zeros_like(tot)
    for b in ublocks:          # the function's own order, so the sum is bitwise its total
        total += ublocks[b]
    if not np.array_equal(total, tot):
        raise c.Refusal("universe_block's per-band blocks do not sum to its total")
    v = c.NORM * x_T
    if not np.array_equal(ublocks[NORM_KEY], np.outer(v, v)):
        raise c.Refusal("universe_block's normalization entry is not (0.014 x_hat_T)(0.014 x_hat_T)^T")
    C_univ = sum(ublocks[b] for b in sorted(c.ORDER))
    C_lat = sum(ublocks[b] for b in sorted(c.LATERAL_BANDS))
    C_norm = ublocks[NORM_KEY]
    C_stat = np.cov(np.asarray(X_rep, np.float64), rowvar=False)
    r = x_T / np.asarray(x_R, np.float64)
    C08 = r[:, None] * np.asarray(C08_R, np.float64) * r[None, :]
    C_model_abs = x_T[:, None] * np.asarray(C_model, np.float64) * x_T[None, :]
    C_T = C_univ + C_lat + C_norm + C_stat + C08 + C_model_abs
    out = {"blocks": ublocks, "C_univ": C_univ, "C_lat": C_lat, "C_norm": C_norm, "C_stat": C_stat, "C08": C08,
           "C_model_abs": C_model_abs, "C_T": C_T, "section_9_8": psd_checks(C_T)}
    if C_model_minus is not None:
        out["C_T_minus"] = C_T - C_model_abs + x_T[:, None] * C_model_minus * x_T[None, :]
    return out


def noatime_inputs(ro, tmp: Path, files: dict) -> dict:
    """Copy every file the rollup reads through O_NOATIME into ``tmp`` and repoint its call-time globals: ``ro.BF`` (the
    per-playlist flux and data POT files) and the ``ro.PIN`` entries named in ``files`` ({key: (path, sha or None)}).
    Returns {key or path: sha256}."""
    rec = {}
    bf = Path(tmp) / "baseline_flux"
    bf.mkdir(parents=True)
    for pl in ro.BR.PLAYLISTS:
        for kind in ("MC", "Data"):
            src = f"{ro.BF}/runEventLoop{kind}_{pl}.root"
            data, sha = read_noatime(src)
            (bf / Path(src).name).write_bytes(data)
            rec[src] = sha
    ro.BF = str(bf)
    for key, (path, want) in files.items():
        data, sha = read_noatime(path)
        if want is not None and sha != want:
            raise c.Refusal(f"{path} sha256 {sha} != {want}")
        dst = Path(tmp) / f"{key}{Path(path).suffix}"
        dst.write_bytes(data)
        ro.PIN[key] = (str(dst), sha)
        rec[key] = sha
    return rec

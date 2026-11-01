#!/usr/bin/env python3
"""1B reopened, the gate-D investigation (state/measurement-paper/5d-community-20261024/FD-1B-INV-DECLARATION.md,
under DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md item 1): do S1's universe blocks and the
pseudo-experiments propagate the same uncertainty through the same estimator?

Subcommands:

* ``stage``: each input read once with O_NOATIME into a verified copy (I0's reads; declaration section 8);
* ``i0``: per band, S1's and the toys' diagonal blocks against the measured rounding floor, and rule H2 per gate-D
  failing cell (SUPPORTED / REJECTED / OPEN), with the receipt-based fallback floor (section 4);
* ``unfold``: S1's mechanism at the nominal truth, one interaction universe per product, in mode A (the universe in
  the unfolding MC, ``s5p_universe.universe_inputs``), B (the response alone in the MC: the derivation's own source
  factors) or C (the prior alone: truth and reco weights x the fine-cell mean factor, the denominator per cell by the
  same factor), on the derivation CV experiment's pseudo-data (section 6);
* ``i2``: the interaction group's factors sqrt(E/M) = F_src F_prior F_truth and rule I2 per out-of-window cell.

Every pscratch input is opened with O_NOATIME. ``stage`` copies small inputs and checks each source's atime; the
``unfold`` job reads the large ones through file objects (``load_inputs``, ``load_npz``, ``load_npy``), which a test
holds equal to the path-based loaders they replace. ``s5p_universe``, ``s5p_nullexp``, ``fd_1b_toys``,
``fd_1b_score``, ``fd_1b_diag``, ``s1_assemble`` and ``s5n_pseudo`` are imported and unchanged.

    fd_1b_inv.py stage --spec SPEC.json --out DIR
    fd_1b_inv.py i0 --staged DIR --definition H2DEF --gate-d G [--receipt R] --out O
    fd_1b_inv.py unfold --mode A --universes MaRES_0,MaRES_1 --npz N --bkg B --bank K --detector-dir D --pins P ...
    fd_1b_inv.py i2 --staged DIR --unfolds U --tag T --gate-d G --i0 I0 --out O

MEASURES: the declared readouts, labelled DERIVATION. CANNOT AUTHORIZE: a coverage verdict, a change to the toys,
M_d, the covariance or gate D's window, or any claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_diag as fdg  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_nullexp as ne  # noqa: E402
import s5p_stage1_inspect as s1i  # noqa: E402
import s5p_truths  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "fd-1b-inv/1"
WINDOW = fs.GATE_D_WINDOW
RESOLVE_K = 4.0                 # resolved: a block at least 4x its pure-noise expectation, on both sides (section 4)
UPPER_LEVEL = 0.05              # the upper floor: the one-sided 95 % bound on sigma_J^2 from the jitters
DER_TAG, S1_TAG = "fd1b_derivation", "S1"
MODES = ("A", "B", "C")
INTERACTION = toys.INTERACTION_BANDS
# gate D's cells outside the window (FD-1B-STAGE2-REPORT section 4.1); i0 refuses if the copies give another set
H2_CELLS = ("R00", "R02", "R05", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R15")
N_INTERACTION_OUT = 15          # the interaction ratio's cells outside the window (all but R06)
NOATIME_FLAG = getattr(os, "O_NOATIME", None)
# the unfolding-MC keys a mode replaces; the pseudo-data, truth, flux and template coordinates stay the CV's
MC_KEYS = ("w_truth", "w_reco", "denom_nd", "tmpl_w")


class Refusal(RuntimeError):
    """A declared input, control or invariant does not hold: nothing is written."""


# ------------------------------------------------------------------------------------------------- O_NOATIME reads


OPENED: dict[str, int] = {}     # every path this process opened through open_noatime -> its atime (ns) at first open


def open_noatime(path: Path):
    """A binary file object on ``path`` opened with O_NOATIME, so reading it leaves its access time (and pscratch
    purge exposure) unchanged. Refuses where the flag does not exist; an EPERM (a file the caller does not own) is
    raised, never retried as a plain read. Each path is recorded with its atime, for ``atime_check``."""
    if NOATIME_FLAG is None:
        raise Refusal("O_NOATIME is not available on this platform: refusing a plain read")
    fd = os.open(path, os.O_RDONLY | NOATIME_FLAG)
    OPENED.setdefault(str(path), os.fstat(fd).st_atime_ns)
    return os.fdopen(fd, "rb")


def atime_check() -> dict:
    """Every file opened through open_noatime, with its atime at first open and now; ``moved`` lists any that
    changed (a deviation, reported and not restored)."""
    rows = {p: {"atime_ns_first": a, "atime_ns_now": os.stat(p).st_atime_ns} for p, a in sorted(OPENED.items())}
    return {"files": rows, "moved": sorted(p for p, r in rows.items() if r["atime_ns_first"] != r["atime_ns_now"])}


def sha256_noatime(path: Path) -> str:
    h = hashlib.sha256()
    with open_noatime(path) as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_npz(path: Path, allow_pickle: bool = False) -> dict:
    """Every array of an npz, materialized while the O_NOATIME descriptor is open."""
    with open_noatime(path) as fh:
        z = np.load(fh, allow_pickle=allow_pickle)
        return {k: z[k] for k in z.files}


def load_npy(path: Path) -> np.ndarray:
    with open_noatime(path) as fh:
        return np.load(fh, allow_pickle=False)


def load_inputs(path: Path) -> dict:
    """``s5c_unfold.load_inputs`` on an O_NOATIME file object: the same keys and arrays."""
    with open_noatime(path) as fh:
        return s5c_unfold.load_inputs(fh)


def universe_weights(bank: Path, tag: str, nonfinite: str) -> dict:
    """``s5p_universe.weights`` through O_NOATIME: float64, non-finite zeroed (``'zero'``, the universe unfolds' rule)
    or kept (``'keep'``, the derivation's, which refuses them where used)."""
    out = {}
    for key in s5p_universe.weight_keys(bank, tag):
        w = load_npy(bank / f"{tag}_{key}.npy").astype(np.float64)
        if nonfinite == "zero":
            np.nan_to_num(w, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        elif nonfinite != "keep":
            raise ValueError(f"nonfinite={nonfinite!r}")
        out[key] = w
    return out


# ---------------------------------------------------------------------------------------------------------- stage


def stage(spec: list[dict], out: Path) -> dict:
    """Copy each ``{"role", "src", "dest", "sha256"?}`` once with O_NOATIME into ``out/dest``; the copy's digest is
    the source's (and the declared one, if given), and the source's atime must not move. Missing sources are listed,
    not refused: I0's fallback reads the list."""
    out.mkdir(parents=True, exist_ok=True)
    rec, missing = [], []
    for item in spec:
        src, dest = Path(item["src"]), out / item["dest"]
        if not src.exists():
            missing.append({"role": item["role"], "src": str(src)})
            continue
        if dest.exists():
            raise Refusal(f"refusing to overwrite {dest}")
        before = src.stat()
        dest.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256()
        with open_noatime(src) as fh, open(dest, "xb") as fo:
            for block in iter(lambda: fh.read(1 << 24), b""):
                h.update(block)
                fo.write(block)
        after = src.stat()
        got = h.hexdigest()
        if item.get("sha256") and got != item["sha256"]:
            raise Refusal(f"{src}: sha256 {got} != declared {item['sha256']}")
        if sa.sha256(dest) != got:
            raise Refusal(f"{dest}: the copy's digest differs from the source's")
        if (after.st_atime_ns, after.st_mtime_ns, after.st_size) != (before.st_atime_ns, before.st_mtime_ns, before.st_size):
            raise Refusal(f"{src}: its atime, mtime or size moved during the O_NOATIME read")
        rec.append({"role": item["role"], "src": str(src), "dest": item["dest"], "sha256": got, "size": after.st_size,
                    "atime_ns": after.st_atime_ns})
    return {"schema": "fd-1b-inv-stage/1", "staged": rec, "missing": missing}


# ----------------------------------------------------------------------------------------------- the rounding floor


def chi2_cdf(x: float, k: int) -> float:
    """P(chi2_k <= x): the regularized lower incomplete gamma P(k/2, x/2) by its series (any k)."""
    a, h = k / 2.0, x / 2.0
    if h <= 0:
        return 0.0
    term = total = 1.0 / a
    n = 0
    while term > 1e-17 * total:
        n += 1
        term *= h / (a + n)
        total += term
    return math.exp(a * math.log(h) - h - math.lgamma(a)) * total


def chi2_ppf(p: float, k: int) -> float:
    lo, hi = 0.0, 10.0 * k + 100.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if chi2_cdf(mid, k) < p else (lo, mid)
    return 0.5 * (lo + hi)


def upper_factor(n: int, level: float = UPPER_LEVEL) -> float:
    """sigma^2's one-sided upper bound over its sample estimate from n draws: (n - 1) / chi2_{n-1}(level)."""
    return (n - 1) / chi2_ppf(level, n - 1)


def jitter_sigma(X: np.ndarray) -> np.ndarray:
    """The per-cell rounding spread: the sample SD (ddof 1) of the jittered unfolds' cell integrals."""
    X = np.asarray(X, float)
    if X.ndim != 2 or X.shape[0] < 2:
        raise Refusal(f"jitter array shape {X.shape}: need at least 2 jitters")
    return X.std(axis=0, ddof=1)


def noise_factor(band: str, flux_w: np.ndarray) -> float:
    """A band's expected pure-noise block per cell, in units of sigma_J^2: (n - 1)/n mean-centred over n universes;
    for Flux, 1 - sum w^2 / (sum w)^2 (the weighted, weighted-mean-centred estimator)."""
    if band == sa.FLUX:
        w = np.asarray(flux_w, float)
        return float(1.0 - (w ** 2).sum() / w.sum() ** 2)
    n = sa.EXPECT[band]
    return (n - 1) / n


def box_matrix() -> np.ndarray:
    """Rows = the 32 H2 boxes over the fine grid (the fine-bin volume where the fine cell is in the box)."""
    cmap, n = s1i.coarse_map(s1i.H2_EDGES)
    vol = s1i.fine_volume()
    return np.vstack([np.where(cmap == i, vol, 0.0) for i in range(n)])


def fallback_sigma(sig_rel_box: np.ndarray, x_box: np.ndarray, box_to_cell: np.ndarray) -> np.ndarray:
    """The full-correlation upper bound on a cell's absolute rounding spread from its boxes' relative spreads:
    sigma_c <= sum_{i in c} sigma_i x_i (triangle inequality)."""
    sig = np.asarray(sig_rel_box, float) * np.asarray(x_box, float)
    m = np.asarray(box_to_cell, int)
    return np.array([sig[m == c].sum() for c in range(sa.N_CELLS)])


# --------------------------------------------------------------------------------------------------------- rule H2


def noise_consistent(M_bb: np.ndarray, E_bb: np.ndarray, N_data: np.ndarray, N_nom: np.ndarray,
                     k: float = RESOLVE_K) -> np.ndarray:
    """A band-cell whose blocks are BOTH below k x their own side's pure-noise expectation (review B1): only then can
    noise have made its term. A block above k x its floor on either side keeps the term."""
    return (np.asarray(M_bb) < k * np.asarray(N_data)) & (np.asarray(E_bb) < k * np.asarray(N_nom))


def rho_resolved(terms: dict, noise: dict) -> np.ndarray:
    """sqrt(1 + the terms of every band not noise-consistent) per cell; NaN where the sum is negative (outside the
    window)."""
    s = 1.0 + sum(np.where(noise[b], 0.0, terms[b]) for b in sorted(terms))
    return np.sqrt(np.where(s >= 0, s, np.nan))


def in_window(x) -> np.ndarray:
    x = np.asarray(x, float)
    return np.isfinite(x) & (x >= WINDOW[0]) & (x <= WINDOW[1])


def h2_cell(at_point: bool, at_upper: bool, fallback: bool) -> str:
    """SUPPORTED iff the resolved-only rho is in the window at both floors; REJECTED iff at neither; OPEN otherwise.
    Under the fallback floor SUPPORTED cannot be read and reads OPEN."""
    if at_point and at_upper:
        return "OPEN" if fallback else "SUPPORTED"
    return "REJECTED" if not (at_point or at_upper) else "OPEN"


def h2_step(cells: dict) -> dict:
    """I0's step reading (declaration section 4). Any SUPPORTED or OPEN cell sends the run to I1, which tests the
    universe-noise assumption before an O3 is read (review M2); only all-REJECTED goes straight to I2."""
    v = list(cells.values())
    sup = sorted(c for c, x in cells.items() if x == "SUPPORTED")
    if v and all(x == "REJECTED" for x in v):
        return {"verdict": "REJECTED", "outcome": None, "o3_cells_pending_I1": [], "next": "I2"}
    verdict = "SUPPORTED" if v and len(sup) == len(v) else ("OPEN" if "OPEN" in v else "MIXED")
    return {"verdict": verdict, "outcome": "O3 pending I1" if sup else None, "o3_cells_pending_I1": sup, "next": "I1"}


# ------------------------------------------------------------------------------------------------------------- I0


def _xs(z: dict) -> np.ndarray:
    return np.asarray(z["xsec_flat"], float)


def i0(staged: Path, definition: Path, gate_d: Path, receipt: Path | None) -> dict:
    """Declaration section 4 on the staged copies."""
    rec = json.loads((staged / "staged.json").read_text())
    missing = {m["role"] for m in rec["missing"]}
    hard = missing - {"jitter-data", "jitter-nom"}
    if hard:
        raise Refusal(f"required inputs missing: {sorted(hard)}")
    if sa.sha256(gate_d) != fdg.GATE_D_SHA256:
        raise fs.Invalid(f"{gate_d} is not gate D's committed readout")
    s1 = fs.load_s1(staged / "s1" / "s1_assembly.npz")
    d = fs.derivation_blocks(staged / "derivation", DER_TAG, s1, staged / "flux_constraint.txt")
    diag = fdg.diagnose(d, s1)
    if json.loads(gate_d.read_text()).get("rho") != diag["rho"]:
        raise fs.Invalid("rho on the staged copies does not reproduce gate D's committed readout bit for bit")
    cells = [f"R{c:02d}" for c in range(sa.N_CELLS)]
    rho = np.asarray(diag["rho"])
    failing = tuple(c for c, ok in zip(cells, in_window(rho)) if not ok)
    if failing != H2_CELLS:
        raise fs.Invalid(f"gate D's failing cells {failing} are not the declared {H2_CELLS}")

    U = sa.functional_matrix(sa.fine_map(definition))
    uni = sa.universe_bands([staged / "uni"], S1_TAG)
    w = sa.flux_weights(staged / "flux_constraint.txt")
    x_s1 = {}
    for b, ps in uni.items():
        X = np.array([U @ sa.xs(p) for p in ps])
        if not np.array_equal(sa.mat_cov(X, w if b == sa.FLUX else None), s1["blocks"][f"band:{b}"]):
            raise fs.Invalid(f"band {b}: the staged S1 unfolds do not reproduce the assembly's block exactly")
        for i, x in enumerate(X):
            x_s1[f"{b}_{i}"] = x
    x_s1_cv = U @ sa.xs(staged / "uni" / f"{S1_TAG}_CV.npz")

    g, Md = d["g"], np.diag(fs.drawn_matrix(s1))
    fallback = bool(missing)
    if not fallback:
        jd = sorted((staged / "jitter-data").glob("data_b-_j*.npz"))
        jd = [p for p in jd if p.name != "data_b-_j-.npz"]
        jn = [p for p in sorted((staged / "jitter-nom").glob("nom_b-_j*.npz")) if p.name != "nom_b-_j-.npz"]
        base = sa.xs(staged / "jitter-data" / "data_b-_j-.npz")
        if not np.array_equal(base, sa.xs(staged / "uni" / f"{S1_TAG}_CV.npz")):
            raise fs.Invalid("S1_CV is not the N1 base bitwise (S1's G4)")
        sd = jitter_sigma([U @ sa.xs(p) for p in jd])
        sn = g * jitter_sigma([U @ sa.xs(p) for p in jn])
        k_up = {"data": upper_factor(len(jd)), "nom": upper_factor(len(jn))}
        floors = {"point": (sd ** 2, sn ** 2), "upper": (k_up["data"] * sd ** 2, k_up["nom"] * sn ** 2)}
        floor_src = {"kind": "measured", "n_jitters": {"data": len(jd), "nom": len(jn)}, "upper_factor": k_up}
    else:
        if receipt is None:
            raise Refusal("the jitter products are missing and no --receipt was given for the fallback floor")
        sN = json.loads(receipt.read_text())["study_N"]
        hdef = json.loads(definition.read_text())
        m = np.asarray(hdef["h2_to_reporting_cell"], int)
        Ub = box_matrix()
        x_cv_d = Ub @ sa.xs(staged / "uni" / f"{S1_TAG}_CV.npz")
        x_cv_n = Ub @ _xs(load_npz_plain(staged / "derivation" / f"{DER_TAG}_CV.npz"))
        sd = fallback_sigma(sN["N1_data"]["H2"]["sigma_num_base_rel"], x_cv_d, m)
        sn = g * fallback_sigma(sN["N2_nominal_930000"]["H2"]["sigma_num_base_rel"], x_cv_n, m)
        floors = {"point": (sd ** 2, sn ** 2), "upper": (sd ** 2, sn ** 2)}
        floor_src = {"kind": "fallback: receipt per-box sigma, full-correlation bound", "receipt_sha256": sa.sha256(receipt)}

    terms, E_bb, M_bb, out_bands = {}, {}, {}, {}
    for key, v in d["carried"].items():
        b = key[5:]
        E_bb[b], M_bb[b] = np.diag(v), np.diag(s1["blocks"][key])
        terms[b] = (E_bb[b] - M_bb[b]) / Md
    readings, rho_res, noise_sets, s1_res, sign = {}, {}, {}, {}, {}
    for which, (vd, vn) in floors.items():
        noise = {b: noise_consistent(M_bb[b], E_bb[b], noise_factor(b, w) * vd, noise_factor(b, w) * vn) for b in terms}
        rho_res[which] = rho_resolved(terms, noise)
        noise_sets[which] = {b: [cells[c] for c in range(sa.N_CELLS) if r[c]] for b, r in noise.items()}
        s1_res[which] = {b: [cells[c] for c in range(sa.N_CELLS) if M_bb[b][c] >= RESOLVE_K * noise_factor(b, w) * vd[c]]
                         for b in terms}
        # H2's sign (review B1): noise on the toys' side is the small one, so a positive term from a band resolved there
        # is an excess noise is not predicted to make
        sign[which] = sum(np.where((terms[b] > 0) & (E_bb[b] >= RESOLVE_K * noise_factor(b, w) * vn), terms[b], 0.0)
                          for b in terms).tolist()
    for c in H2_CELLS:
        i = cells.index(c)
        readings[c] = h2_cell(bool(in_window(rho_res["point"][i])), bool(in_window(rho_res["upper"][i])), fallback)
    for b in sorted(terms):
        nf = noise_factor(b, w)
        out_bands[b] = {"group": sa.group_of(f"band:{b}"), "term": terms[b].tolist(),
                        "q_s1": np.sqrt(M_bb[b] / (nf * floors["point"][0])).tolist(),
                        "q_toys": np.sqrt(E_bb[b] / (nf * floors["point"][1])).tolist(),
                        "noise_consistent_point": noise_sets["point"][b], "noise_consistent_upper": noise_sets["upper"][b],
                        "s1_resolved_point": s1_res["point"][b], "s1_resolved_upper": s1_res["upper"][b]}
    return {"schema": SCHEMA, "step": "I0", "label": "DERIVATION", "cells": cells, "window": list(WINDOW),
            "resolve_k": RESOLVE_K, "rho": rho.tolist(), "g": g.tolist(), "floor": floor_src,
            "sigma_J_data": sd.tolist(), "sigma_J_nom_carried": sn.tolist(),
            "rho_resolved": {k: [None if not np.isfinite(x) else float(x) for x in v] for k, v in rho_res.items()},
            "positive_terms_resolved_on_toy_side": sign,
            "H2_cells": readings, "H2": h2_step(readings), "per_band": out_bands,
            "per_universe": per_universe(d, x_s1, x_s1_cv),
            "staged_sha256": sa.sha256(staged / "staged.json")}


def load_npz_plain(path: Path) -> dict:
    """A staged copy (this lane's own file, off pscratch's other lanes): read plainly."""
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files}


def per_universe(d: dict, x_s1: dict, x_s1_cv: np.ndarray) -> dict:
    """Descriptive (no verdict role): per interaction universe, the carried toy shift s_D, S1's shift s_S1, their
    correlation with s_D against -s_S1, and the fraction of cells where sign(s_D) = -sign(s_S1); per pair band, the
    antisymmetry |s+ + s-| / (|s+| + |s-|) on each side."""
    g = d["g"]
    out = {}
    for b in INTERACTION:
        n = sa.EXPECT[b]
        sD = [g * (d["x"][f"{b}_{i}"] - d["x"]["CV"]) for i in range(n)]
        sS = [x_s1[f"{b}_{i}"] - x_s1_cv for i in range(n)]
        rec = {"universes": [{"s_D": a.tolist(), "s_S1": s.tolist(),
                              "corr_sD_minus_sS1": float(np.corrcoef(a, -s)[0, 1]) if a.std() > 0 and s.std() > 0 else None,
                              "opposite_sign_fraction": float(np.mean(np.sign(a) == -np.sign(s)))}
                             for a, s in zip(sD, sS)]}
        if n == 2:
            for side, (p, q) in (("toys", sD), ("s1", sS)):
                den = np.abs(p) + np.abs(q)
                rec[f"antisymmetry_{side}"] = np.where(den > 0, np.abs(p + q) / np.where(den > 0, den, 1), 0.0).tolist()
        out[b] = rec
    return out


# ------------------------------------------------------------------------------------------------- I2's three modes


def cell_mean_factor(k_wt: np.ndarray, inputs: dict) -> np.ndarray:
    """Per row, the fine-cell mean of the truth-weight factor, sum w_truth k / sum w_truth over the truth-passing rows
    of the row's fine truth cell (1 for rows in no cell): the prior part of a universe, the reciprocal of
    ``s5p_nullexp.truth_preserving``'s g over all rows."""
    gen, edges = np.asarray(inputs["MCgen"]), inputs["edges"]
    wt = np.asarray(inputs["w_truth"], float)
    inside, idx = s5p_truths.cell_of(gen, edges)
    rows = np.flatnonzero(inside)
    pt = np.asarray(inputs["pass_truth"], bool)[rows]
    rows = rows[pt]
    flat = np.ravel_multi_index([i[pt] for i in idx], [len(e) - 1 for e in edges])
    n = int(np.prod([len(e) - 1 for e in edges]))
    s0 = np.bincount(flat, weights=wt[rows], minlength=n)
    s1 = np.bincount(flat, weights=(wt * k_wt)[rows], minlength=n)
    r = np.ones(gen.shape[0])
    r[rows] = np.where(s0[flat] > 0, s1[flat] / np.where(s0[flat] > 0, s0[flat], 1.0), 1.0)
    return r


def prior_mc(inputs: dict, r: np.ndarray) -> dict:
    """``s5p_universe.prior_inputs``'s construction, with each cell's denominator factor of1/of0 computed before it is
    applied, so r = 1 reproduces the CV bitwise: truth and reco weights x r, the denominator x of1/of0 per cell."""
    ui = dict(inputs)
    wt = np.asarray(inputs["w_truth"], float)
    ui["w_truth"] = wt * r
    ui["w_reco"] = np.asarray(inputs["w_reco"], float) * r
    m = np.asarray(inputs["pass_truth"], bool)
    samp = np.asarray(inputs["MCgen"])[m]
    edges = [np.asarray(e, float) for e in inputs["edges"]]
    of0, _ = np.histogramdd(samp, bins=edges, weights=wt[m])
    of1, _ = np.histogramdd(samp, bins=edges, weights=(wt * r)[m])
    factor = np.where(of0 > 0, of1 / np.where(of0 > 0, of0, 1.0), 1.0)
    ui["denom_nd"] = np.asarray(inputs["denom_nd"], float) * factor
    return ui


def response_factors(w: dict, inputs: dict, bkg: dict, tag: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """The derivation's own factors for one interaction universe (``ModelCache._ratios`` then ``source_factors``):
    k_wr x g_f on the signal reco weights, k_b on the background, and k_wt (for C)."""
    rec: dict = {}
    wr, wt, bw = (np.asarray(x, float) for x in (inputs["w_reco"], inputs["w_truth"], bkg["bkg_w"]))
    used = (np.asarray(inputs["pass_reco"], bool), np.asarray(inputs["pass_truth"], bool), np.ones(bw.size, bool))
    k_wr, k_wt, k_b = (ne.checked_ratio(w[k], cv, u, f"{tag}:{k}", rec, clip_negative=True)
                       for k, cv, u in zip(("wr", "wt", "bkgw"), (wr, wt, bw), used))
    fs_ = k_wr * ne.truth_preserving(k_wt, inputs, np.ones(inputs["MCgen"].shape[0], bool))
    return fs_, k_b, k_wt, rec


def mode_inputs(mode: str, tag: str, inputs: dict, bkg: dict, bank: Path, bank_cv: dict) -> tuple[dict, dict, dict]:
    """The unfolding MC (inputs, background) for one universe in one mode; ``tag == "CV"`` gives the CV control
    (every factor exactly 1, every array the CV's)."""
    if tag == "CV":
        return dict(inputs), dict(bkg), {}
    if mode == "A":
        w = universe_weights(bank, tag, "zero")
        band, _, idx = tag.rpartition("_")
        ui, ub, info = s5p_universe.universe_inputs(inputs, bkg, bank_cv, w, band, idx, None)
        return ui, ub, info
    fs_, k_b, k_wt, rec = response_factors(universe_weights(bank, tag, "keep"), inputs, bkg, tag)
    if mode == "B":
        return (dict(inputs, w_reco=np.asarray(inputs["w_reco"], float) * fs_),
                dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * k_b), rec)
    if mode == "C":
        return prior_mc(inputs, cell_mean_factor(k_wt, inputs)), dict(bkg), rec
    raise ValueError(f"mode {mode!r}")


def nominal_experiment(inputs: dict, bkg: dict) -> tuple[dict, np.ndarray]:
    """The derivation CV experiment: all of the MC, every Poisson draw at its mean, the nominal truth."""
    r = s5n_pseudo.truth_weight("nominal", inputs, 0.0, None)
    ones_s, ones_b = np.ones(inputs["w_reco"].shape[0]), np.ones(bkg["bkg_w"].shape[0])
    exp, x_true, _ = toys.build_full(inputs, bkg, r, ones_s, ones_b, None, expectation=True)
    return exp, x_true


def with_mc(exp_cv: dict, ui: dict, ub: dict) -> dict:
    """The CV experiment's pseudo-data with the mode's unfolding MC (``s5n_pseudo.build_data``'s own keys)."""
    mc = s5n_pseudo.build_data(ui, ub)
    return dict(exp_cv, **{k: mc[k] for k in MC_KEYS})


def run_unfold(a, unfold_fn=None) -> int:
    OPENED.clear()
    s5e_candidate.install(toys.CONFIG)
    npz_sha, bkg_sha = sha256_noatime(a.npz), sha256_noatime(a.bkg)
    if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):
        raise Refusal(f"input digests {npz_sha} / {bkg_sha} are not the declared ones")
    if sha256_noatime(a.pins) != a.expect_pins_sha256:
        raise Refusal("pins file digest differs")
    with open_noatime(a.pins) as fh:
        pins = json.loads(fh.read().decode())
    toys.check_pins(pins, a.bank, a.detector_dir)
    groups = toys.interaction_groups(a.bank)
    inputs = load_inputs(a.npz)
    bz = load_npz(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    bank_cv = load_npz(a.bank / "cv.npz", allow_pickle=True)
    alignment = s5p_universe.check_alignment(bank_cv, inputs, bkg)
    exp_cv, x_true = nominal_experiment(inputs, bkg)
    legal = {u for us in groups.values() for u in us} | {"CV"}
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for tag in a.universes.split(","):
        if tag not in legal:
            raise Refusal(f"{tag} is not one of the 67 interaction universes or CV")
        target = a.out / f"{a.tag}_{a.mode}_{tag}.npz"
        if target.exists():
            continue
        toys.check_pins(pins, a.bank, a.detector_dir)
        if tag != "CV":
            for k in s5p_universe.weight_keys(a.bank, tag):
                p = a.bank / f"{tag}_{k}.npy"
                if sha256_noatime(p) != pins["files"][str(p)]["sha256"]:
                    raise Refusal(f"{p}: digest differs from the pins file")
        t1 = time.time()
        ui, ub, info = mode_inputs(a.mode, tag, inputs, bkg, a.bank, bank_cv)
        exp = with_mc(exp_cv, ui, ub)
        xs, ev = (unfold_fn or s5n_pseudo.unfold_negweight)(exp, toys.ESTIMATOR_SEED, a.threads, toys.ITERS)
        xs = np.asarray(xs, float)
        if not np.all(np.isfinite(xs)):
            raise Refusal(f"{target.name}: a non-finite unfolded value")
        meta = {"schema": SCHEMA, "step": "I2", "mode": a.mode, "universe": tag, "truth": "nominal",
                "config": toys.CONFIG, "capacity": None, "iters": toys.ITERS, "estimator_seed": toys.ESTIMATOR_SEED,
                "threads": a.threads, "mode_info": info, **ev, "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha,
                "pins_sha256": a.expect_pins_sha256, "alignment": alignment,
                "code_sha256": {**toys.code_digests(), "fd_1b_inv.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t1, 3),
                "numpy_version": np.__version__}
        status |= s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"),
                                                    "xtrue_flat": np.asarray(x_true, float).ravel(order="C")}, meta)
        print(json.dumps({"out": target.name, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    chk = atime_check()
    (a.out / f"atime-{a.mode}-{os.environ.get('SLURM_JOB_ID', 'local')}-{os.getpid()}.json").write_text(
        json.dumps(chk, indent=1) + "\n")
    if chk["moved"]:
        print(f"[fd-1b-inv] DEVIATION: atime moved on {chk['moved']}", file=sys.stderr)
        return status | 8
    return status


# ---------------------------------------------------------------------------------------------------------- rule I2


def factors(E: np.ndarray, B: np.ndarray, A: np.ndarray, M: np.ndarray) -> dict:
    """The interaction group's per-cell sigma ratios, whose product is sqrt(E/M) exactly."""
    return {"total": np.sqrt(E / M), "F_src": np.sqrt(E / B), "F_prior": np.sqrt(B / A), "F_truth": np.sqrt(A / M)}


OUTCOME_OF = {"F_src": "O2", "F_prior": "O1", "F_truth": "O1"}
MECHANISM_OF = {"F_src": "H4", "F_prior": "H1", "F_truth": "H3"}
ACCOUNT_MIN, REFUTED_MAX = 8, 3      # of the 15 cells: a mechanism's headline account, and its headline refutation


def attribute(F: dict, c: int, truth_resolved: np.ndarray | None = None) -> dict:
    """Rule I2 for cell c: the factor with the largest |ln F| on the departure's side of 1, if it lies outside the
    window itself and carries at least half of |ln sqrt(E/M)|; otherwise unresolved. F_truth is the one factor made
    on the data, where the rounding spread is largest (review B2): it is attributed only if F_truth over the bands
    resolved on S1's side at I0's upper floor (``truth_resolved``) is also outside the window on the same side."""
    tot = math.log(F["total"][c])
    side = [(abs(math.log(F[k][c])), k) for k in ("F_src", "F_prior", "F_truth")
            if math.log(F[k][c]) * tot > 0]
    if not side:
        return {"factor": None, "mechanism": None, "outcome": "O4", "why": "no factor on the departure's side"}
    mag, k = max(side)
    if bool(in_window(F[k][c])) or mag < 0.5 * abs(tot):
        return {"factor": None, "mechanism": None, "outcome": "O4", "why": f"{k} inside the window or under half"}
    if k == "F_truth":
        tr = None if truth_resolved is None else truth_resolved[c]
        if tr is None or not np.isfinite(tr) or bool(in_window(tr)) or math.log(tr) * tot <= 0:
            return {"factor": None, "mechanism": None, "outcome": "O4",
                    "why": "F_truth not separated from S1-side noise"}
    return {"factor": k, "mechanism": MECHANISM_OF[k], "outcome": OUTCOME_OF[k]}


def headline(attr: dict) -> dict:
    """Each mechanism's count over the cells, read separately (review M3): ACCOUNT_MIN or more is the headline
    account, REFUTED_MAX or fewer refutes it as the account, in between is partial. The headline is the mechanism
    that accounts, with its outcome; otherwise O4 (mixed)."""
    n = len(attr)
    counts = {m: sum(1 for v in attr.values() if v["mechanism"] == m) for m in ("H1", "H3", "H4")}
    counts["unresolved"] = sum(1 for v in attr.values() if v["mechanism"] is None)
    level = {m: "account" if counts[m] >= ACCOUNT_MIN else ("refuted" if counts[m] <= REFUTED_MAX else "partial")
             for m in ("H1", "H3", "H4")}
    acc = [m for m in ("H1", "H3", "H4") if level[m] == "account"]
    out = {"H1": "O1", "H3": "O1", "H4": "O2"}
    return {"n_cells": n, "counts": counts, "level": level, "account_min": ACCOUNT_MIN, "refuted_max": REFUTED_MAX,
            "headline": acc[0] if acc else None, "outcome": out[acc[0]] if acc else "O4", "mixed": not acc}


def group_sum(blocks: dict) -> np.ndarray:
    """The interaction group's diagonal, summed in sorted band order (gate D's order for its carried blocks)."""
    return sum(np.diag(blocks[f"band:{b}"]) for b in INTERACTION)


def i2(staged: Path, unfolds: Path, tag: str, gate_d: Path, i0_readout: Path, i1_readout: Path | None = None) -> dict:
    if sa.sha256(gate_d) != fdg.GATE_D_SHA256:
        raise fs.Invalid(f"{gate_d} is not gate D's committed readout")
    r0 = json.loads(i0_readout.read_text())
    if r0.get("H2", {}).get("next") == "I1":
        if i1_readout is None:
            raise Refusal("I0 sent the run to I1: I2 needs I1's readout (declaration section 5)")
        if json.loads(i1_readout.read_text()).get("H2", {}).get("verdict") == "SUPPORTED":
            raise Refusal("I1 read H2 SUPPORTED in every cell: I2 does not run (declaration section 5)")
    s1 = fs.load_s1(staged / "s1" / "s1_assembly.npz")
    d = fs.derivation_blocks(staged / "derivation", DER_TAG, s1, staged / "flux_constraint.txt")
    E_all = {**d["fixed"], **d["carried"]}
    e = sum(v for k, v in E_all.items() if k.startswith("band:") and sa.group_of(k) == "interaction")
    m = sum(v for k, v in s1["blocks"].items() if k.startswith("band:") and sa.group_of(k) == "interaction")
    ratio = np.sqrt(np.diag(e) / np.diag(m))
    if json.loads(gate_d.read_text())["per_group_sigma_ratio"]["interaction"] != ratio.tolist():
        raise fs.Invalid("the interaction ratio does not reproduce gate D's committed readout bit for bit")
    U, g, x_cv_d = s1["U"], d["g"], d["x"]["CV"]
    cv_flat = _xs(load_npz_plain(staged / "derivation" / f"{DER_TAG}_CV.npz"))
    mode_blocks, shifts = {}, {}
    for mode in MODES:
        cvp = load_npz_plain(unfolds / f"{tag}_{mode}_CV.npz")
        if not np.array_equal(_xs(cvp), cv_flat):
            raise fs.Invalid(f"mode {mode} at CV does not reproduce the derivation CV product bitwise")
        blocks = {}
        for b in INTERACTION:
            X = []
            for i in range(sa.EXPECT[b]):
                p = unfolds / f"{tag}_{mode}_{b}_{i}.npz"
                z = load_npz_plain(p)
                meta = json.loads(str(z["meta"]))
                if (meta.get("mode"), meta.get("universe"), meta.get("schema")) != (mode, f"{b}_{i}", SCHEMA):
                    raise fs.Invalid(f"{p.name}: not mode {mode}, universe {b}_{i}")
                X.append(U @ _xs(z))
                shifts[(mode, f"{b}_{i}")] = g * (X[-1] - x_cv_d)
            blocks[f"band:{b}"] = sa.mat_cov(np.array(X)) * np.outer(g, g)
        mode_blocks[mode] = blocks
    A, B, C = (group_sum(mode_blocks[k]) for k in MODES)
    F = factors(np.diag(e), B, A, np.diag(m))
    cells = [f"R{c:02d}" for c in range(sa.N_CELLS)]
    out_cells = [c for c in range(sa.N_CELLS) if not in_window(F["total"][c])]
    if len(out_cells) != N_INTERACTION_OUT:
        raise fs.Invalid(f"{len(out_cells)} interaction cells outside the window, not the declared {N_INTERACTION_OUT}")
    # F_truth over the bands resolved on S1's side at I0's upper floor (review B2)
    keep = {b: np.array([c in r0["per_band"][b]["s1_resolved_upper"] for c in cells]) for b in INTERACTION}
    A_res = sum(np.where(keep[b], np.diag(mode_blocks["A"][f"band:{b}"]), 0.0) for b in INTERACTION)
    M_res = sum(np.where(keep[b], np.diag(s1["blocks"][f"band:{b}"]), 0.0) for b in INTERACTION)
    with np.errstate(divide="ignore", invalid="ignore"):
        truth_res = np.where(M_res > 0, np.sqrt(A_res / np.where(M_res > 0, M_res, 1.0)), np.nan)
    attr = {cells[c]: attribute(F, c, truth_res) for c in out_cells}
    # the carry's part of F_truth: A uncarried against M (g is gate D's design)
    A_raw = sum(np.diag(mode_blocks["A"][f"band:{b}"]) / g ** 2 for b in INTERACTION)
    # review m2: how much of each failing gate-D cell's rho^2 - 1 the interaction bands carry
    Md = np.diag(fs.drawn_matrix(s1))
    t_int = sum((np.diag(d["carried"][f"band:{b}"]) - np.diag(s1["blocks"][f"band:{b}"])) / Md for b in INTERACTION)
    rho2m1 = np.asarray(json.loads(gate_d.read_text())["rho"]) ** 2 - 1
    resid = {}
    for b in INTERACTION:
        R = np.array([shifts[("A", f"{b}_{i}")] - shifts[("B", f"{b}_{i}")] - shifts[("C", f"{b}_{i}")]
                      for i in range(sa.EXPECT[b])])
        resid[b] = np.diag(sa.mat_cov(R))
    per_band = {b: {"A_over_M": fdg.ratio(np.diag(mode_blocks["A"][f"band:{b}"]), np.diag(s1["blocks"][f"band:{b}"])),
                    "B_over_E": fdg.ratio(np.diag(mode_blocks["B"][f"band:{b}"]), np.diag(d["carried"][f"band:{b}"])),
                    "C_over_A": fdg.ratio(np.diag(mode_blocks["C"][f"band:{b}"]), np.diag(mode_blocks["A"][f"band:{b}"])),
                    "residual_over_A": fdg.ratio(resid[b], np.diag(mode_blocks["A"][f"band:{b}"])),
                    "corr_sD_minus_sB": [float(np.corrcoef(g * (d["x"][f"{b}_{i}"] - x_cv_d), -shifts[("B", f"{b}_{i}")])[0, 1])
                                         for i in range(sa.EXPECT[b])]}
                for b in INTERACTION}
    return {"schema": SCHEMA, "step": "I2", "label": "DERIVATION", "cells": cells, "window": list(WINDOW),
            "E": np.diag(e).tolist(), "M": np.diag(m).tolist(), "A": A.tolist(), "B": B.tolist(), "C": C.tolist(),
            "factors": {k: v.tolist() for k, v in F.items()}, "prior_share_C_over_A": (C / A).tolist(),
            "F_truth_s1_resolved": [None if not np.isfinite(x) else float(x) for x in truth_res],
            "F_truth_uncarried": np.sqrt(A_raw / np.diag(m)).tolist(),
            "interaction_share_of_rho2_minus_1": {c: float(t_int[i] / rho2m1[i]) for i, c in enumerate(cells)
                                                  if c in H2_CELLS},
            "attribution": attr, "headline": headline(attr), "per_band": per_band,
            "i0_sha256": sa.sha256(i0_readout), "i1_sha256": sa.sha256(i1_readout) if i1_readout else None}


# ------------------------------------------------------------------------------------------------------------ main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage")
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("i0")
    p.add_argument("--staged", type=Path, required=True)
    p.add_argument("--definition", type=Path, required=True)
    p.add_argument("--gate-d", type=Path, required=True)
    p.add_argument("--receipt", type=Path, default=None, help="the s5p stage-2 receipt, for the fallback floor")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("unfold")
    p.add_argument("--mode", choices=MODES, required=True)
    p.add_argument("--universes", required=True)
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    p.add_argument("--tag", default="fd1b_inv")
    p = sub.add_parser("i2")
    for k in ("staged", "unfolds", "gate-d", "i0", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--i1", type=Path, default=None, help="I1's readout, when I0 sent the run to I1")
    p.add_argument("--tag", default="fd1b_inv")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "unfold":
            return run_unfold(a)
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        if a.cmd == "stage":
            rec = stage(json.loads(a.spec.read_text()), a.out)
            (a.out / "staged.json").write_text(json.dumps(rec, indent=1) + "\n")
            print(json.dumps({"staged": len(rec["staged"]), "missing": rec["missing"]}))
            return 0
        res = i0(a.staged, a.definition, a.gate_d, a.receipt) if a.cmd == "i0" else i2(a.staged, a.unfolds, a.tag, a.gate_d, a.i0, a.i1)
        res["code_sha256"] = {"fd_1b_inv.py": sa.sha256(Path(__file__).resolve())}
        a.out.write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"out": str(a.out), "step": res["step"],
                          "verdict": res["H2"]["verdict"] if a.cmd == "i0" else res["headline"]["outcome"]}))
        return 0
    except (Refusal, SystemExit, ValueError, OSError) as e:
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-inv] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())

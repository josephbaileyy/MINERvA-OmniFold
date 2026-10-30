#!/usr/bin/env python3
"""The audit of the 5B run-period block C_PL,5D before it is added to the 16-cell reported matrix
(state/measurement-paper/5d-community-20261024/FD-CT-5B-AUDIT-DECLARATION.md; DECISION-20261030-joseph-4b-not-now-
5b-audit-then-add.md item 2). Login node, 0 node-h; reads existing products only.

    fd_ct_5b_audit.py --definition ... --s1-npz ... --cresp ... --cmodel-json ... --b5 <5B run directory>
        --readout-5b fd_ct_5b_periods.json --readout-5a fd_ct_period.json --playlist-npz ... --playlist-json ...
        --analysis-2d analysis.json --central <(e) central value> --out-json ...

Everything is relative to each cell (declaration section 2). P is the 5B readout's C_PL5D_rel, byte-pinned; the
reader first rebuilds it, its noise floor, g_X and sigma_M from the 5B unfolds and refuses unless they equal the
committed ones. Then:

1. overlap (section 3): the duplication bound OV(B) = sum_i min(lambda_i, u_i^T B u_i) / sum_i lambda_i per group, on
   P's modes; identification of each period's offset pattern by one existing component d (a block's eigenvector
   scaled to its 1 sigma), by weighted least squares of g_X on (1, d) with weights sigma_X^-2, E_X = 1 -
   chi2_res(1, d) / chi2_res(1); the noise floor against C_stat;
2. stability (section 4): ten replica-built blocks P^(k), the floor's jackknife and split halves, the noise-debiased
   block, and the three-period interval on sigma;
3. 5B against 5A (section 5): uniform shares, 5A's noise projected from 2D's own draws, a post hoc E_avail contrast,
   and the angles between the two planes;
4. rank two (section 6): the span, the first-order reference bound, the largest chi2 fall lambda~_1 / (1 + lambda~_1),
   and plane retention R_k = tr(Pi P^(k)) / tr(P^(k)).

THE STOP CONDITION (section 7), fixed in the declaration before any of this ran: stop = O or N or R, with
O: some candidate d has E_PB >= 0.5, E_PC >= 0.5, |a_PB| <= 2 and |a_PC| <= 2;
N: SD_k(median_c sigma_c(P^(k))) / median_c sigma_c(P) > 0.5;
R: median_k R_k < 0.5.
A control that refuses exits 1 with nothing written, and leaves the condition undecided.

Nothing written or printed carries f, an absolute cell value or f - g: each output passes fd_f0_regrade.LeakGuard
first (exit 3, nothing written), with every 5B unfold and MC-truth integral in its table.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: the addition, any change to the reported matrix, a
generator chi2, the cause of a period difference, a claim or printed wording.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_ct_periods as cp  # noqa: E402  (PER, BOOT, N_BOOT, receipt, unfold, unf_path, guarded, cell_sets_problems)
import fd_ct_readers as ct  # noqa: E402  (common, footprint, summary, cells, write, PINS, PT_2D, PZ_2D, code_sha)
import fd_f0_regrade as f0  # noqa: E402  (Stop, report, require, sa_call)
import s1_assemble as sa  # noqa: E402  (fine_map, functional_matrix, group_of, check_meta, sha256, xs)

N_CELLS = 16
PER = cp.PER
TOL = 1e-12
EIG_FLOOR = cp.EIG_FLOOR
READOUT_5B_SHA256 = "a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db"   # fd/readout/fd_ct_5b_periods.json
CMODEL_JSON_SHA256 = "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60"  # pv-ladder/readouts/cmodel_5d.json
ANALYSIS_2D_SHA256 = "05edff61673fed987f487f8c19ad25ec055db8118491815b9c263f3a7c3de72b"  # period-unfold outputs/analysis.json
VERTICES = ("genie_mec", "nuwro", "gibuu")
N_BANDS, N_LATERALS = 38, 5
# the declaration's thresholds (section 7), fixed before any audit number was read
O_E, O_A = 0.5, 2.0
N_SMED = 0.5
R_RET = 0.5
# candidates (section 3.3): a block's eigenvectors with lambda >= CAND_FRAC tr(B), at most CAND_TOP of them
CAND_FRAC, CAND_TOP = 0.01, 3
UNIFORM_REL = 1e-12          # a candidate whose noise-weighted shape after the intercept is this small is uniform
NOISE_DOMINATED = 2.0        # sigma(P) / sigma(floor) below this flags a cell (section 4.3)
CONTROL_2D_REL = 1e-9        # 2D's committed bootstrap noise share, reproduced (section 5.3)
# P(Beta(1/2, 7) >= 1/2): a random direction's squared cosine with a pattern in 15 dimensions (section 3.3)
BETA_TAIL = 0.0021892087196238924
# the E_avail cell sets of section 5.3 (3c), checked against the definition's boxes
EA_LOW = (0, 4, 8, 12)
EA_HIGH = (2, 3, 6, 7, 10, 11, 15)
EA_FREE = (1, 5, 9, 13, 14)
GROUPS = ("flux", "detector", "lateral", "C_resp", "DR", "interaction", "normalization", "C_model", "all")
LABELS = {
    "what": "the audit of C_PL,5D (FD-CT-5B-AUDIT-DECLARATION.md), descriptive except for the stop condition; every "
            "number relative to each cell; P is the 5B readout's C_PL5D_rel, byte-pinned, rebuilt from the 5B "
            "unfolds as a control",
    "ov": "OV(B) = sum_i min(lambda_i, u_i^T B u_i) / sum_i lambda_i on P's Euclidean modes: an upper bound on the "
          "share of P that duplicates B IF B's source caused the period offsets; it does not show that it did, and "
          "any broad normalization-like block, flux included, is expected to give a large OV (section 3.1)",
    "identification": "weighted least squares of each g_X on (1, d), weights sigma_X^-2 (the committed per-cell noise "
                      "sigma of g_X, diagonal): E_X = 1 - chi2_res(1, d) / chi2_res(1), a_X the coefficient on d in "
                      "units of d's own 1 sigma; the intercept is free because a uniform offset cannot be attributed "
                      "by shape; a uniform candidate is excluded",
    "replicas": "P^(k): DESIGN section 2 on the k-th bootstrap replica of each period, each from its own seed block; "
                "one joint draw of the block's estimator under the data's resampling",
    "three_periods": "the 68% interval of sigma_true / sigma_hat from chi2_nu at nu = (1 - V2)^2 / (V2 - 2 sum e^3 + "
                     "V2^2), the Satterthwaite dof of the exposure-weighted spread; it depends only on e, so it is "
                     "disclosed, not a stop clause",
    "ea_contrast": "POST HOC: chosen after the 5B table showed R00 and R08 apart; descriptive",
    "not_citable_for": ["the cause of a period difference, or which period is right", "a validated size: a block "
                        "built from the observed differences contains them by construction", "a coverage or "
                        "calibration statement", "the addition, which is its own declared step"],
}


# ---------------------------------------------------------------- algebra


def p_block(r: dict, e: dict) -> tuple[np.ndarray, dict]:
    """DESIGN section 2 on the cells: m = sum e_X r_X, g_X = r_X / m - 1, C = k sum_X e_X g_X g_X^T."""
    m = sum(e[X] * r[X] for X in PER)
    g = {X: r[X] / m - 1.0 for X in PER}
    V2 = sum(v * v for v in e.values())
    k = V2 / (1.0 - V2)
    return k * sum(e[X] * np.outer(g[X], g[X]) for X in PER), g


def kfac(e: dict) -> float:
    V2 = sum(v * v for v in e.values())
    return V2 / (1.0 - V2)


def basis(C: np.ndarray) -> np.ndarray:
    """An orthonormal basis of C's column space (eigenvectors above max(TOL lambda_max, EIG_FLOOR))."""
    lam, V = np.linalg.eigh((C + C.T) / 2.0)
    keep = lam > max(TOL * max(lam.max(), 0.0), EIG_FLOOR)
    return V[:, keep]


def modes(C: np.ndarray, top: int | None = None, frac: float = 0.0):
    """Eigen-pairs, descending, each vector signed so that its largest-|loading| cell is positive."""
    lam, V = np.linalg.eigh((C + C.T) / 2.0)
    o = np.argsort(lam)[::-1]
    lam, V = lam[o], V[:, o]
    out = []
    tr = float(np.trace(C))
    for i in range(lam.size):
        if lam[i] < frac * tr or lam[i] <= max(EIG_FLOOR, TOL * max(lam[0], 0.0)):
            break
        v = V[:, i]
        v = v if v[np.argmax(np.abs(v))] > 0 else -v
        out.append((float(lam[i]), v))
        if top is not None and len(out) == top:
            break
    return out


def ov(P: np.ndarray, B: np.ndarray) -> dict:
    """Section 3.2: the duplication bound on P's modes."""
    mp = modes(P)
    lam = [m[0] for m in mp]
    # a variance below EIG_FLOOR counts as zero (declaration section 2): a pattern mode is orthogonal to a uniform
    # block, which would otherwise leave rounding residue below the leak guard's 1e-30 floor (review L2)
    b = [v if abs(v) >= EIG_FLOOR else 0.0 for v in (float(m[1] @ B @ m[1]) for m in mp)]
    return {"OV": float(sum(min(li, bi) for li, bi in zip(lam, b)) / sum(lam)), "lambda": lam, "b": b}


def wls(y: np.ndarray, w: np.ndarray, regs: list[np.ndarray]) -> tuple[np.ndarray, float]:
    """Weighted least squares of y on the columns regs, weights w: (coefficients, chi2 at the minimum)."""
    A = np.column_stack(regs)
    sw = np.sqrt(w)
    coef, *_ = np.linalg.lstsq(A * sw[:, None], y * sw, rcond=None)
    res = y - A @ coef
    return coef, float(np.sum(w * res * res))


def shape_norm_ratio(d: np.ndarray, w: np.ndarray) -> float:
    """||d - c||_w / ||d||_w with c the weighted mean: how much of d is not uniform, in the fit's own weights."""
    c = float(np.sum(w * d) / np.sum(w))
    return float(math.sqrt(np.sum(w * (d - c) ** 2) / np.sum(w * d * d)))


def identify(g: dict, sig: dict, ds: list[np.ndarray]) -> dict:
    """Section 3.3 for one candidate (one vector) or one pair: per period E, the coefficients on ds, and the residual."""
    one = np.ones(N_CELLS)
    out = {}
    for X in PER:
        w = 1.0 / sig[X] ** 2
        _, c0 = wls(g[X], w, [one])
        coef, c1 = wls(g[X], w, [one, *ds])
        out[X] = {"E": 1.0 - c1 / c0, "a": [float(v) for v in coef[1:]], "chi2_res": c1, "chi2_res_intercept": c0}
    return out


def fires_o(idf: dict) -> bool:
    return bool(all(idf[X]["E"] >= O_E and all(abs(a) <= O_A for a in idf[X]["a"]) for X in ("PB", "PC")))


def principal_angles_deg(Q1: np.ndarray, Q2: np.ndarray) -> list[float]:
    s = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    return [float(math.degrees(math.acos(min(1.0, max(-1.0, v))))) for v in s]


def outside_share(Q: np.ndarray, v: np.ndarray) -> float:
    r = v - Q @ (Q.T @ v)
    return float(r @ r / (v @ v))


def whitened_eigs(P: np.ndarray, M: np.ndarray) -> np.ndarray:
    """Eigenvalues of L^-1 P L^-T, L the Cholesky factor of M: those of M^-1/2 P M^-1/2."""
    L = np.linalg.cholesky(M)
    W = np.linalg.solve(L, P)
    Pt = np.linalg.solve(L, W.T).T
    return np.sort(np.linalg.eigvalsh((Pt + Pt.T) / 2.0))[::-1]


def nu_eff(e: dict) -> float:
    """The Satterthwaite dof of sum_X e_X (y_X - ybar)^2 for independent y_X of one variance: (tr A)^2 / tr(A^2),
    A = diag(e) - e e^T, which is (1 - V2)^2 / (V2 - 2 sum e^3 + V2^2)."""
    v = np.array([e[X] for X in PER])
    A = np.diag(v) - np.outer(v, v)
    return float(np.trace(A) ** 2 / np.trace(A @ A))


def sigma_interval(nu: float) -> list[float]:
    """The 68% central interval of sigma_true / sigma_hat when nu sigma_hat^2 / sigma_true^2 ~ chi2_nu."""
    from scipy import stats
    return [float(math.sqrt(nu / stats.chi2.ppf(0.84, nu))), float(math.sqrt(nu / stats.chi2.ppf(0.16, nu)))]


def chi2_q95(ndf: int) -> float:
    from scipy import stats
    return float(stats.chi2.ppf(0.95, ndf))


# ---------------------------------------------------------------- inputs


def load_5b(a, U: np.ndarray, S: dict) -> dict:
    """Controls A0 and A1: the committed 5B readout, then the same quantities rebuilt from the 5B unfolds."""
    f0.require("A0", a.readout_5b, READOUT_5B_SHA256, "5B readout")
    ro = json.loads(a.readout_5b.read_text())
    pins = ro.get("inputs_sha256") or {}
    f0.report("A0", "the 5B readout is fd-ct-5b-periods/1 on this S1 assembly, C_resp and definition",
              bool(ro.get("schema") == "fd-ct-5b-periods/1" and pins.get("s1_npz") == ct.PINS["s1_npz"]
                   and pins.get("cresp") == ct.PINS["cresp"] and pins.get("definition") == sa.DEFINITION_SHA256),
              "it is not")
    rec = {X: cp.receipt(a.b5, X, "A1") for X in PER}
    for X in PER:
        if sa.sha256(a.b5 / "inputs" / f"check_{X}.json") != pins["receipts"][X]:
            raise f0.Stop("A1", f"{X}: the check receipt is not the one the 5B readout read")
    for X in PER:
        want = sorted(cp.unf_path(a.b5, X, b).name for b in (None, *cp.BOOT[X]))
        have = sorted(p.name for p in (a.b5 / "unf" / X).glob("*.npz"))
        if have != want:
            raise f0.Stop("A1", f"{X}: the unfold directory holds {have}, not the declared {len(want)}")
    xs = {X: {b: cp.unfold(a.b5, X, b, rec[X], "A1") for b in (None, *cp.BOOT[X])} for X in PER}
    for X in PER:
        for b in xs[X]:
            if sa.sha256(cp.unf_path(a.b5, X, b)) != pins["unfolds"][X][str(b)]:
                raise f0.Stop("A1", f"{X} b{b}: the unfold is not the one the 5B readout read")
    T, e_raw = {}, {}
    for X in PER:
        tp = Path(rec[X]["files"]["truth"][0])
        with np.load(tp, allow_pickle=False) as z:
            m = json.loads(str(z["meta_json"]))
            t = np.asarray(z["xsec_flat"], float)
        if (m.get("schema"), m.get("npz_sha256")) != ("s5p-mc-truth-pred/1", rec[X]["files"]["lat_npz"][1]):
            raise f0.Stop("A1", f"{tp.name}: not the MC truth of {X}'s npz")
        if m.get("code_sha256") != sa.sha256(_ND / "s5p_mc_truth_pred.py") or t.shape != xs[X][None].shape:
            raise f0.Stop("A1", f"{tp.name}: code or shape")
        T[X] = U @ t
        with np.load(rec[X]["files"]["lat_npz"][0], allow_pickle=True) as z:
            e_raw[X] = float(z["data_pot"]) * float(np.asarray(z["flux"], float).mean())
    tot = sum(e_raw.values())
    e = {X: e_raw[X] / tot for X in PER}
    x = {X: U @ xs[X][None] for X in PER}
    D = {X: [U @ xs[X][b] / x[X] - 1.0 for b in cp.BOOT[X]] for X in PER}
    r = {X: x[X] / T[X] for X in PER}
    allX = [U @ v for X in xs for v in xs[X].values()]
    if not (all(np.all(v > 0) for v in allX) and all(np.all(T[X] > 0) for X in PER)):
        raise f0.Stop("A1", "an unfold or MC-truth integral is not positive")
    C, g = p_block(r, e)
    k = kfac(e)
    gn = [{X: D[X][i] - sum(e[Y] * D[Y][i] for Y in PER) for X in PER} for i in range(cp.N_BOOT)]
    Cn = np.mean([k * sum(e[X] * np.outer(h[X], h[X]) for X in PER) for h in gn], axis=0)
    g_sig = {X: np.sqrt(np.mean([h[X] ** 2 for h in gn], axis=0)) for X in PER}
    P = np.asarray(ro["C_PL5D"]["C_PL5D_rel"], float)
    M = S["M"] / S["ff"]
    gv = ro["g_vs_5A"]["periods"]
    checks = {
        "C_PL,5D rebuilt from the unfolds equals the committed one":
            P.shape == (N_CELLS, N_CELLS) and float(np.max(np.abs(C - P)) / np.max(np.abs(P))) <= TOL,
        "the noise floor rebuilt equals the committed one": np.allclose(
            np.sqrt(np.diag(Cn)), ro["C_PL5D"]["noise_floor_sigma_rel"], rtol=TOL, atol=0),
        "sigma_M equals the committed one": np.allclose(np.sqrt(np.diag(M)), ro["sigma_rel_M"], rtol=TOL, atol=0),
        "the exposure shares equal the committed ones": all(
            abs(e[X] - ro["constants"]["exposure_share"][X]) <= TOL for X in PER),
        "g_X and its noise sigma equal the committed ones": all(
            np.allclose(g[X], gv[X]["g_5b"], rtol=0, atol=TOL) and np.allclose(g_sig[X], gv[X]["g_5b_noise_sigma"],
                                                                                rtol=TOL, atol=0) for X in PER),
    }
    for name, ok in checks.items():
        f0.report("A1", name, bool(ok), "differs")
    return {"ro": ro, "P": P, "e": e, "k": k, "g": g, "g_sig": g_sig, "r": r, "D": D, "Cn": Cn, "M": M,
            "integrals": [*allX, *T.values()], "g5a": {X: np.asarray(gv[X]["g_5a"], float) for X in PER},
            "pins": {"unfolds": pins["unfolds"], "receipts": {X: sa.sha256(a.b5 / "inputs" / f"check_{X}.json")
                                                              for X in PER}}}


def load_blocks(a, S: dict) -> dict:
    """Control A2: every block of the reported matrix, relative to each cell, partitioning M exactly."""
    ff = S["ff"]
    with np.load(a.s1_npz, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        names = list(meta.get("blocks") or [])
        missing = [b for b in names if "C_" + b.replace(":", "_") not in z.files]
        if missing or not names:
            raise f0.Stop("A2", f"S1's blocks missing from the assembly: {missing or 'all'}")
        blocks = {b: np.asarray(z["C_" + b.replace(":", "_")], float) for b in names}
        Cmf, Cma = np.asarray(z["C_model_frac"], float), np.asarray(z["C_model_abs"], float)
    f0.require("A2", a.cmodel_json, CMODEL_JSON_SHA256, "cmodel_5d.json")
    cj = json.loads(a.cmodel_json.read_text())
    Sv = np.asarray(cj.get("S"), float)
    with np.load(a.cresp, allow_pickle=False) as z:
        species = {p: np.asarray(z[f"C_resp_{p}"], float) for p in ct.PRIMARY}
    scale = np.abs(np.diag(S["C_total"])).max()
    bands = [b for b in names if b.startswith("band:")]
    lats = [b for b in names if b.startswith("lat:")]
    checks = {
        f"S1 has {N_BANDS} bands, {N_LATERALS} laterals, normalization, stat and seed": (
            len(bands), len(lats), {"normalization", "stat", "seed"} <= set(names), len(names))
            == (N_BANDS, N_LATERALS, True, N_BANDS + N_LATERALS + 3),
        "every block maps to one of S1's seven groups": all(
            sa.group_of(b) in ("stat", "flux", "interaction", "detector", "lateral", "normalization", "seed")
            for b in names),
        "C_e is the sum of S1's blocks": np.allclose(sum(blocks.values()), S["C_e"], rtol=TOL, atol=TOL * scale),
        "C_model's vertices are GENIE+MEC, NuWro, GiBUU, and S^T S is C_model_frac": tuple(cj.get("vertices", ()))
            == VERTICES and Sv.shape == (3, N_CELLS) and np.allclose(Sv.T @ Sv, Cmf, rtol=TOL,
                                                                     atol=TOL * np.abs(np.diag(Cmf)).max()),
        "C_model_abs = diag(f) C_model diag(f)": np.allclose(Cmf * ff, Cma, rtol=TOL, atol=TOL * scale),
    }
    for name, ok in checks.items():
        f0.report("A2", name, bool(ok), "differs")
    rel = {b: B / ff for b, B in blocks.items()}
    rel.update({f"C_model:{v}": np.outer(Sv[j], Sv[j]) for j, v in enumerate(VERTICES)})
    rel.update({f"C_resp:{p}": B / ff for p, B in species.items()})
    M = S["M"] / ff
    f0.report("A2", "S1's blocks, the three C_model vertices and the four C_resp species sum to M",
              bool(np.allclose(sum(rel.values()), M, rtol=TOL, atol=TOL * np.abs(np.diag(M)).max())), "they do not")
    return rel


def group_of(name: str) -> str:
    if name.startswith("C_model:"):
        return "C_model"
    if name.startswith("C_resp:"):
        return "C_resp"
    return sa.group_of(name)


def load_2d(path: str, cells: np.ndarray) -> dict:
    """One 2D per-period unfold's x and t on the 205 cells, by the formula of 2D's analyze_periods.load (its
    `t` is the producer's MC-truth cross section). Not imported from there: that module puts cluster paths at
    sys.path[0]. Control A3 requires the seed-42 r = x / t to equal playlist_term.npz's r_X."""
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise f0.Stop("A3", f"cannot open {path}")

    def th2(h):
        return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])

    hx = f.Get("hXSec2D")
    ex = np.array([hx.GetXaxis().GetBinLowEdge(i) for i in range(1, hx.GetNbinsX() + 2)])
    ey = np.array([hx.GetYaxis().GetBinLowEdge(i) for i in range(1, hx.GetNbinsY() + 2)])
    if not (np.allclose(ex, ct.PT_2D) and np.allclose(ey, ct.PZ_2D)):
        raise f0.Stop("A3", f"{path}: axes differ from the 2D grid")
    x, T, c = th2(hx), th2(f.Get("hTruth2D")), th2(f.Get("hOFCompleteness2D"))
    hf = f.Get("hFlux_pt")
    phi = np.array([hf.GetBinContent(i) for i in range(1, hf.GetNbinsX() + 1)])
    pot, nn = float(f.Get("dataPOT").GetVal()), float(f.Get("nNucleons").GetVal())
    f.Close()
    dpt, dpz = np.diff(ct.PT_2D), np.diff(ct.PZ_2D)
    denom = c * phi[:, None] * nn * pot * dpt[:, None] * dpz[None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where((c > 0) & (phi[:, None] > 0), T / denom * 1.0e4, 0.0)
    return {"x": x.ravel(order="C")[cells], "t": t.ravel(order="C")[cells]}


def noise_5a(a, U: np.ndarray, fm: np.ndarray, S: dict, g5a_committed: dict) -> dict:
    """Section 5.3 (3b) and control A3: 2D's per-period noise, projected through 5A's own footprint weights."""
    f0.require("A3", a.playlist_npz, ct.PINS["playlist_npz"], "playlist_term.npz")
    f0.require("A3", a.playlist_json, ct.PINS["playlist_json"], "playlist_term.json")
    f0.require("A3", a.analysis_2d, ANALYSIS_2D_SHA256, "2D analysis.json")
    with np.load(a.playlist_npz, allow_pickle=False) as zz:
        z = {k: np.asarray(zz[k]) for k in zz.files}
    support = z["cells"].astype(int)
    ev = {X: z[f"e_{X}"].astype(float) for X in PER}
    share_ref = json.loads(a.playlist_json.read_text())["report"]["noise_share"]["boot"]["median_cell_variance_share"]
    A = json.loads(a.analysis_2d.read_text())
    roles, runs = A["_roles"], A["_runs"]

    def load(path):
        if path not in runs or sa.sha256(Path(path)) != runs[path]["sha256"]:
            raise f0.Stop("A3", f"{path}: not at its analysis.json digest")
        return load_2d(path, support)

    R = {X: {"s42": load(roles[X]["s42"]), "s43": load(roles[X]["s43"]),
             "boot": [load(p) for p in roles[X]["boot"]]} for X in PER}
    if any(len(R[X]["boot"]) != cp.N_BOOT for X in PER) or support.size != 205:
        raise f0.Stop("A3", "2D populations: 205 cells and 10 bootstrap draws per period required")
    r0 = {X: R[X]["s42"]["x"] / R[X]["s42"]["t"] for X in PER}
    f0.report("A3", "2D's seed-42 r = x / t equals playlist_term.npz's r_X",
              all(np.allclose(r0[X], z[f"r_{X}"], rtol=TOL, atol=0) for X in PER), "differs")
    d = {X: [(b["x"] / b["t"]) / r0[X] - 1.0 for b in R[X]["boot"]] for X in PER}
    ds = {X: (R[X]["s43"]["x"] / R[X]["s43"]["t"]) / r0[X] - 1.0 for X in PER}
    V2 = sum(ev[X] ** 2 for X in PER)
    kk = V2 / (1.0 - V2)
    xx = z["x"].astype(float)

    def h_of(dd):
        mm = sum(ev[X] * dd[X] for X in PER)
        return {X: dd[X] - mm for X in PER}

    hb = [h_of({X: d[X][i] for X in PER}) for i in range(cp.N_BOOT)]
    Nb = np.mean([sum(np.outer(np.sqrt(kk * ev[X]) * xx * h[X], np.sqrt(kk * ev[X]) * xx * h[X]) for X in PER)
                  for h in hb], axis=0)
    share = float(np.median(np.diag(Nb) / np.diag(z["C_PL"])))
    f0.report("A3", "2D's committed bootstrap noise share is reproduced",
              abs(share / share_ref - 1.0) <= CONTROL_2D_REL, f"{share / share_ref - 1.0:.3e}")
    f0.require("A3", a.central, ct.PINS["central"], "the (e) central value")
    f0.sa_call("A3", sa.check_meta, a.central, "s5p-numerics/1", 42, True,
               {"construction": "data", "truth": "nominal", "bootstrap_seed": None, "jitter_seed": None})
    xc = sa.xs(a.central)
    f0.report("A3", "the central value's cell integrals are S1's f",
              bool(np.allclose(U @ xc, S["f"], rtol=TOL, atol=0)), "differ")
    om = ct.footprint(U, fm, xc, support)[0]
    f0.report("A3", "5A's g, reprojected, equals the committed 5A readout's",
              all(np.allclose(om @ z[f"g_{X}"], g5a_committed[X], rtol=0, atol=TOL) for X in PER), "differs")
    hs = h_of(ds)
    boot = {X: np.mean([(om @ h[X]) ** 2 for h in hb], axis=0) for X in PER}
    seed = {X: (om @ hs[X]) ** 2 / 2.0 for X in PER}
    return {"sigma": {X: np.sqrt(boot[X] + seed[X]) for X in PER},
            "sigma_boot": {X: np.sqrt(boot[X]) for X in PER}, "sigma_seed": {X: np.sqrt(seed[X]) for X in PER},
            "noise_share_reproduced": share}


def ea_sets_problems(definition: Path) -> list[str]:
    boxes = {c["id"]: c["box"] for c in json.loads(definition.read_text())["reporting_cells"]}
    lo = tuple(sorted(i for i, b in boxes.items() if b["eavail"][1] <= 0.8))
    hi = tuple(sorted(i for i, b in boxes.items() if b["eavail"][0] >= 0.8))
    free = tuple(sorted(set(boxes) - set(lo) - set(hi)))
    return [] if (lo, hi, free) == (EA_LOW, EA_HIGH, EA_FREE) else [f"E_avail cell sets {lo} / {hi} / {free}"]


# ---------------------------------------------------------------- the audit


def group_blocks(rel: dict) -> dict:
    """The groups of section 1: S1's, C_model, C_resp, DR = detector + lateral + C_resp, and all of M."""
    groups = {G: np.zeros((N_CELLS, N_CELLS)) for G in GROUPS}
    for nm, B in rel.items():
        G = group_of(nm)
        if G in groups:
            groups[G] += B
        if G in ("detector", "lateral", "C_resp"):
            groups["DR"] += B
        groups["all"] += B
    return groups


def item1(P: np.ndarray, g: dict, g_sig: dict, e: dict, rel: dict, Cn: np.ndarray) -> dict:
    k = kfac(e)
    groups = group_blocks(rel)
    # P's pattern part: the same construction on the offsets less their cell means (section 3.2)
    pat = {X: g[X] - g[X].mean() for X in PER}
    Ppat = k * sum(e[X] * np.outer(pat[X], pat[X]) for X in PER)
    out = {"OV_label": LABELS["ov"], "OV": {G: ov(P, groups[G]) for G in GROUPS},
           "OV_pattern": {G: ov(Ppat, groups[G]) for G in GROUPS}}
    # candidates
    cands = []
    for nm, B in rel.items():
        G = group_of(nm)
        if G in ("stat", "seed"):
            continue
        for i, (lam, v) in enumerate(modes(B, CAND_TOP, CAND_FRAC)):
            cands.append((f"{nm}#{i + 1}", G, math.sqrt(lam) * v))
    rows, uniform, fired = [], [], []
    for nm, G, d in cands:
        if min(shape_norm_ratio(d, 1.0 / g_sig[X] ** 2) for X in ("PB", "PC")) <= UNIFORM_REL:
            uniform.append(nm)
            continue
        idf = identify(g, g_sig, [d])
        row = {"candidate": nm, "group": G, **{X: idf[X] for X in PER}, "fires_O": fires_o(idf)}
        rows.append(row)
        if row["fires_O"]:
            fired.append(nm)
    q14 = chi2_q95(N_CELLS - 2)
    best = {}
    for G in sorted({r_["group"] for r_ in rows}):
        rs = sorted((r_ for r_ in rows if r_["group"] == G), key=lambda r_: -min(r_["PB"]["E"], r_["PC"]["E"]))[:3]
        best[G] = [{**r_, "within_noise_95": {X: r_[X]["chi2_res"] <= q14 for X in PER}} for r_ in rs]
    dr = [(nm, d) for nm, G, d in cands if G in ("detector", "lateral", "C_resp") and nm not in uniform]
    pair = None
    for (n1, d1), (n2, d2) in itertools.combinations(dr, 2):
        idf = identify(g, g_sig, [d1, d2])
        score = min(idf["PB"]["E"], idf["PC"]["E"])
        if pair is None or score > pair["score"]:
            pair = {"candidates": [n1, n2], "score": score, **{X: idf[X] for X in PER}}
    n = len(rows)
    floor_sig = np.sqrt(np.diag(Cn))
    stat_sig = np.sqrt(np.diag(rel["stat"]))
    out.update({
        "identification": {"label": LABELS["identification"], "n_candidates": n, "uniform_excluded": uniform,
                           "thresholds": {"E": O_E, "abs_a": O_A}, "fired_by": fired,
                           "candidates": rows, "best_per_group": best, "best_pair_in_DR": pair,
                           "residual_q95_chi2_14": q14,
                           "look_elsewhere": {"beta_tail": BETA_TAIL, "if_PB_PC_patterns_identical": n * BETA_TAIL,
                                              "if_independent": n * BETA_TAIL ** 2}},
        "noise_vs_stat": {"floor_over_stat_sigma": (floor_sig / stat_sig).tolist(),
                          "floor_over_stat_sigma_summary": ct.summary(floor_sig / stat_sig),
                          "expected_under_poisson_sqrt_2k": math.sqrt(2.0 * k),
                          "floor_trace_share_of_P": float(np.trace(Cn) / np.trace(P))},
    })
    return out


def replica_blocks(r: dict, D: dict, e: dict) -> list[np.ndarray]:
    return [p_block({X: r[X] * (1.0 + D[X][i]) for X in PER}, e)[0] for i in range(cp.N_BOOT)]


def floor_of(D: dict, e: dict, idx) -> np.ndarray:
    k = kfac(e)
    hs = [{X: D[X][i] - sum(e[Y] * D[Y][i] for Y in PER) for X in PER} for i in idx]
    return np.mean([k * sum(e[X] * np.outer(h[X], h[X]) for X in PER) for h in hs], axis=0)


def expected_chi2(D: dict, idx, Mi: np.ndarray) -> dict:
    out = {}
    for n, d in (("PB", "PA"), ("PC", "PA"), ("PC", "PB")):
        N = sum(np.mean([np.outer(D[X][i], D[X][i]) for i in idx], axis=0) for X in (n, d))
        out[f"dr_{n}/{d}"] = float(np.trace(Mi @ N))
    return out


def item2(P: np.ndarray, Pk: list, D: dict, e: dict, Cn: np.ndarray, M: np.ndarray) -> dict:
    sig = np.sqrt(np.diag(P))
    sk = np.array([np.sqrt(np.clip(np.diag(C), 0, None)) for C in Pk])
    med = np.array([np.median(s) for s in sk])
    s_med = float(np.std(med, ddof=1) / np.median(sig))
    Pm = np.mean(Pk, axis=0)
    idx = range(cp.N_BOOT)
    jf = [floor_of(D, e, [j for j in idx if j != i]) for i in idx]
    Mi = np.linalg.inv(M)

    def jse(vals):
        v = np.asarray(vals, float)
        n = v.shape[0]
        return np.sqrt((n - 1) / n * np.sum((v - v.mean(axis=0)) ** 2, axis=0))

    jfs = np.array([np.sqrt(np.diag(F)) for F in jf])
    jratio = sig[None, :] / jfs
    jchi = [expected_chi2(D, [j for j in idx if j != i], Mi) for i in idx]
    halves = {h: floor_of(D, e, list(rng)) for h, rng in (("1-5", range(5)), ("6-10", range(5, 10)))}
    lam, V = np.linalg.eigh(P - Cn)
    pos = lam > max(TOL * max(lam.max(), 0.0), EIG_FLOOR)
    if int(pos.sum()) > 2:
        raise f0.Stop("A5", f"P - floor has {int(pos.sum())} positive eigenvalues; Weyl allows at most 2")
    Pd = (V[:, pos] * lam[pos]) @ V[:, pos].T
    sig_n = np.sqrt(np.diag(Cn))
    nu = nu_eff(e)
    return {"label": LABELS["replicas"],
            "replica_sigma_mean": sk.mean(axis=0).tolist(), "replica_sigma_sd": sk.std(axis=0, ddof=1).tolist(),
            "replica_median_sigma": med.tolist(), "s_med": s_med, "threshold_N": N_SMED,
            "replica_trace_share": [float(np.trace(C) / np.trace(M + C)) for C in Pk],
            "mean_block_sigma_over_P_sigma_minus_1": (np.sqrt(np.diag(Pm)) / sig - 1.0).tolist(),
            "mean_shift_diag": (np.diag(Pm) - np.diag(P)).tolist(), "floor_diag": np.diag(Cn).tolist(),
            "floor_sigma_over_P_sigma": (sig_n / sig).tolist(),
            "jackknife": {"floor_sigma_se": jse(jfs).tolist(), "sigma_over_floor_se": jse(jratio).tolist(),
                          "expected_chi2_M_se": {kk: float(jse([c[kk] for c in jchi])) for kk in jchi[0]},
                          "expected_chi2_M": expected_chi2(D, list(idx), Mi)},
            "split_half": {h: {"floor_sigma_over_all": (np.sqrt(np.diag(F)) / sig_n).tolist(),
                               "expected_chi2_M": expected_chi2(D, list(r_), Mi)}
                           for (h, F), r_ in zip(halves.items(), (range(5), range(5, 10)))},
            "debiased": {"sigma_over_P_sigma": (np.sqrt(np.clip(np.diag(Pd), 0, None)) / sig).tolist(),
                         "rank": int(pos.sum())},
            "noise_dominated_cells": ct.cells([c for c in range(N_CELLS) if sig[c] / sig_n[c] < NOISE_DOMINATED]),
            "three_periods": {"label": LABELS["three_periods"], "nu_eff": nu, "sigma_ratio_68": sigma_interval(nu)}}


def item3(P: np.ndarray, P5a: np.ndarray, g: dict, g5a: dict, g_sig: dict, n5a: dict) -> dict:
    u = np.full(N_CELLS, 0.25)
    Iu = np.eye(N_CELLS) - np.outer(u, u)
    out = {"uniform_share": {"5B": float(u @ P @ u / np.trace(P)), "5A": float(u @ P5a @ u / np.trace(P5a))},
           "trace_uniform_removed": {"5B": float(np.trace(Iu @ P @ Iu)), "5A": float(np.trace(Iu @ P5a @ Iu))},
           "trace": {"5B": float(np.trace(P)), "5A": float(np.trace(P5a))}, "periods": {}}
    for X in PER:
        p5b, p5a = g[X] - g[X].mean(), g5a[X] - g5a[X].mean()
        dlt = g[X] - g5a[X]
        comb = np.sqrt(n5a["sigma"][X] ** 2 + g_sig[X] ** 2)
        z = np.abs(dlt) / comb
        con = {}
        for half, cells_ in (("pz_lo", cp.PZ_LO), ("pz_hi", cp.PZ_HI)):
            lo = [c for c in EA_LOW if c in cells_]
            hi = [c for c in EA_HIGH if c in cells_]
            val = float(dlt[lo].mean() - dlt[hi].mean())
            s = float(math.sqrt(np.sum(comb[lo] ** 2) / len(lo) ** 2 + np.sum(comb[hi] ** 2) / len(hi) ** 2))
            con[half] = {"low_minus_high": val, "sigma": s, "low": ct.cells(lo), "high": ct.cells(hi)}
        out["periods"][X] = {
            "mean_offset": {"5B": float(g[X].mean()), "5A": float(g5a[X].mean())},
            "pattern_correlation": float(p5b @ p5a / math.sqrt((p5b @ p5b) * (p5a @ p5a))),
            "sigma_5A": n5a["sigma"][X].tolist(), "sigma_5A_boot": n5a["sigma_boot"][X].tolist(),
            "sigma_5A_seed": n5a["sigma_seed"][X].tolist(),
            "abs_difference_over_combined_noise": z.tolist(),
            "abs_difference_over_combined_noise_summary": ct.summary(z),
            "difference_chi2_combined_diagonal": float(np.sum(z * z)),
            "ea_contrast": {"label": LABELS["ea_contrast"], **con}}
    Qb, Qa = basis(P), basis(P5a)
    out["planes"] = {"principal_angles_deg": principal_angles_deg(Qa, Qb),
                     "g5a_outside_5B_plane": {X: outside_share(Qb, g5a[X]) for X in PER},
                     "g5b_outside_5A_plane": {X: outside_share(Qa, g[X]) for X in PER}}
    return out


def item4(P: np.ndarray, Pk: list, g: dict, e: dict, r: dict, M: np.ndarray) -> dict:
    Q = basis(P)
    worst = max(math.sqrt(outside_share(Q, g[X])) for X in PER)
    if Q.shape[1] > 2 or worst > 1e-8:
        raise f0.Stop("A4", f"P's column space is not span(g): rank {Q.shape[1]}, worst residual {worst:.3e}")
    lam, V = np.linalg.eigh(P)
    keep = lam > max(TOL * lam.max(), EIG_FLOOR)
    Pp = (V[:, keep] / lam[keep]) @ V[:, keep].T
    k = kfac(e)
    ref = {}
    for X in ("PB", "PC"):
        b = e[X] * (r[X] / r["PA"] - 1.0)
        ref[X] = {"value": float(b @ Pp @ b), "first_order_bound": e[X] ** 2 * (1 / e["PA"] + 1 / e[X]) / k}
    lt = whitened_eigs(P, M)
    Pi = Q @ Q.T
    R = [float(np.trace(Pi @ C) / np.trace(C)) for C in Pk]
    return {"rank": int(Q.shape[1]), "reference_bound": ref,
            "whitened_eigenvalues": [float(lt[0]), float(lt[1])],
            "largest_chi2_fall_fraction": float(lt[0] / (1.0 + lt[0])),
            "plane_retention": R, "plane_retention_median": float(np.median(R)), "threshold_R": R_RET,
            "replica_principal_angles_deg": [principal_angles_deg(Q, basis(C)) for C in Pk]}


def decide(fired_by: list, s_med: float, retention_median: float) -> dict:
    """THE STOP CONDITION (declaration section 7): stop = O or N or R."""
    O = bool(fired_by)
    N = bool(s_med > N_SMED)
    R = bool(retention_median < R_RET)
    return {"O": O, "N": N, "R": R, "stop": bool(O or N or R),
            "which": [c for c, v in (("O", O), ("N", N), ("R", R)) if v], "O_decided_by": list(fired_by),
            "N_statistic": s_med, "R_statistic": retention_median,
            "thresholds": {"O_E": O_E, "O_abs_a": O_A, "N_s_med": N_SMED, "R_median": R_RET}}


def run(a) -> int:
    fm = f0.sa_call("S", sa.fine_map, a.definition)
    U = sa.functional_matrix(fm)
    bad = cp.cell_sets_problems(a.definition) + ea_sets_problems(a.definition)
    if bad:
        raise f0.Stop("S", "; ".join(bad))
    S = ct.common(a, U)
    f = S["f"]
    b5 = load_5b(a, U, S)
    guard = cp.guarded(f, b5["integrals"])
    rel = load_blocks(a, S)
    f0.require("A3", a.readout_5a, cp.READOUT_5A_SHA256, "5A readout")
    v5a = json.loads(a.readout_5a.read_text())["variants"]["central"]
    g5a = {X: np.asarray(v5a["g"][X], float) for X in PER}
    f0.report("A3", "the 5B readout's g_5a is the 5A readout's central g",
              all(np.allclose(g5a[X], b5["g5a"][X], rtol=0, atol=0) for X in PER), "differs")
    n5a = noise_5a(a, U, fm, S, g5a)
    P, g, e, k = b5["P"], b5["g"], b5["e"], b5["k"]
    Pk = replica_blocks(b5["r"], b5["D"], e)
    i1 = item1(P, g, b5["g_sig"], e, rel, b5["Cn"])
    i2 = item2(P, Pk, b5["D"], e, b5["Cn"], b5["M"])
    i3 = item3(P, np.asarray(v5a["C_PL16_rel"], float), g, g5a, b5["g_sig"], n5a)
    i4 = item4(P, Pk, g, e, b5["r"], b5["M"])
    sc = decide(i1["identification"]["fired_by"], i2["s_med"], i4["plane_retention_median"])
    O, N, R, stop = sc["O"], sc["N"], sc["R"], sc["stop"]
    out = {"schema": "fd-ct-5b-audit/1", "labels": LABELS,
           "controls_passed": ["S", "A0", "A1", "A2", "A3"], "assertions_passed": ["A4", "A5"],
           "cells": ct.cells(),
           "stop_condition": sc,
           "item1_overlap": i1, "item2_stability": i2, "item3_5a_vs_5b": i3, "item4_rank_two": i4,
           "constants": {"exposure_share": e, "k": k, "n_boot": cp.N_BOOT},
           "inputs_sha256": {"readout_5b": READOUT_5B_SHA256, "readout_5a": cp.READOUT_5A_SHA256,
                             "cmodel_json": CMODEL_JSON_SHA256, "analysis_2d": ANALYSIS_2D_SHA256,
                             **{k_: ct.PINS[k_] for k_ in ("s1_npz", "cresp", "playlist_npz", "playlist_json", "central")},
                             "definition": sa.DEFINITION_SHA256, **b5["pins"]},
           "code_sha256": code_sha(), "argv": sys.argv}
    lines = [f"[5B audit] O {O} (fired by {i1['identification']['fired_by']}; {i1['identification']['n_candidates']} "
             f"candidates), N {N} (s_med {i2['s_med']:.4f}), R {R} (median retention "
             f"{i4['plane_retention_median']:.4f}); stop {stop}"]
    return ct.write(a, out, guard, lines)


# ---------------------------------------------------------------- main


def code_sha() -> dict:
    return {**cp.code_sha(), "fd_ct_5b_audit.py": sa.sha256(Path(__file__).resolve())}


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for nm in ("definition", "s1-npz", "cresp", "cmodel-json", "b5", "readout-5b", "readout-5a", "playlist-npz",
               "playlist-json", "analysis-2d", "central", "out-json"):
        ap.add_argument(f"--{nm}", type=Path, required=True)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    if a.out_json.exists():
        print(f"FAIL refusing to overwrite {a.out_json}", file=sys.stderr)
        return 1
    try:
        return run(a)
    except f0.Stop as e:
        print(e.code, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

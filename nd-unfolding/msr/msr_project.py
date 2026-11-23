#!/usr/bin/env python3
"""MSR, the local step: the declared controls, then the declared readings, on connect B's committed products.

Declaration: ``docs/orchestration/state/measurability-20261122/DECLARATION.md`` (rev 4 with Amendment B). Nothing here
is chosen after a statistic is computed: the cut, floors, bands, intervals, sets, truths and k are the declaration's,
written below as constants. The STOP controls run first; if any fails, the run writes the controls record and exits
rc 3 with no statistic of any bias vector computed.

    msr_project.py run --products DIR --out DIR      (DIR holds r5d.npz, r2d.npz, t3.npz and their json, run-b/cluster/build)

MEASURES: the declared statistics (S_poor, Z_well, r_poor, r_well, the feature-set counts) and their labels.
CANNOT AUTHORIZE: a cause beyond "consistent with", an estimator change, coverage, any data quantity, or note wording.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import scipy.linalg as sla
from scipy import sparse
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
S = REPO / "docs/orchestration/state"
DID_DIR = S / "next-preparation-20261009/d-id"
if str(DID_DIR) not in sys.path:
    sys.path.insert(0, str(DID_DIR))

# ---------------------------------------------------------------------------------------------- declared constants
CUT = 0.10                      # section 3.3: well-constrained if s_k <= 0.10 (D-ID's 10 % CR width)
CUTS_PRINT = (0.05, 0.20)       # printed, read by nothing
EIG_RTOL = 1e-12                # D-ID's eigenvalue cut (range of F_c)
NULL_TOL = 1e-6                 # D-ID's null-fraction rule (U-infinity)
FLOOR = 0.01                    # section 3.6: the floor on ||beta||
R_FLOOR = 0.005                 # section 3.6: the floors on ||P_poor beta_B0|| and ||P_well beta_B0||
T_MULT = 2.7764451051977987     # b1's five-draw guard multiplier
N_PERT = 2000                   # section 3.6: Gaussian perturbations of a noisy vector
SEED = 20261122
PREC_S, PREC_R, PREC_Z_ABS, PREC_Z_REL = 0.01, 0.01, 0.01, 0.01   # N-PREC
MC_PROJ, MC_MATCH = 0.2, 0.9    # section 5.3
SPLITS = (991000, 994001, 994002, 994003, 994004)
F0B_PRIMARY = ("nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "A7_mnvtune", "A7_genie_cv", "A7_genie_mec",
               "A7_nuwro", "A7_gibuu")
A2_PRIMARY = ("nominal", "genie_mec", "nuwro")
A2_SECONDARY = ("bump", "tilt", "within_plus", "within_minus")
F0B_SECONDARY_WITH_D = ("closure_nuwro",)   # Amendment C: the secondary F0b truth converted with d (its FD-PRR entry exists)
C_DID_COMMON_EXPECTED = 151     # Amendment C: the size of the shared functional set for these inputs (a recorded expectation)

OPERANDS = {  # section 2
    "fdprr": (S / "measurement-paper/5d-community-20261024/fd/receipts-prr/read/cluster/readout.json",
              "9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead"),
    "f0b": (S / "measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json",
            "b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b"),
    "f0b_cpl": (S / "measurement-paper/5d-community-20261024/fd/with-cpl/readout/fd_f0b_readout.json",
                "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6"),
    "t3_readout": (S / "measurement-paper/5d-community-20261024/fd/tier3-20261110/run-20261121/cluster/read/readout.json",
                   "b0362c387ec3d8fd48616abe5dcf589407fd007b62214d6297b47418d1a9ecce"),
    "a2": (S / "2d-closeout/ibukt-a2/readout.json", "dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6"),
    "did_tables": (DID_DIR / "outputs/tables.npz", "2aab22703747bfbc33247fe015213c5d9d0a65dcfc0074f0e3c53a1de29327a4"),
}
CODE_PINS = {  # section 2, "code reused unchanged", every file checked by C-OPS
    "did.py": (DID_DIR / "did.py", "d918c816080a292eecaa0cc182a73906b868bb75189056862cf88d7152c4bbbd"),
    "prr_ibu.py": (REPO / "nd-unfolding/prior_retention/prr_ibu.py", "fa91394507c0e6a32486af25fa52f7e162135cf6483519ccf15510e1c9473cb0"),
    "prr_read.py": (REPO / "nd-unfolding/prior_retention/prr_read.py", "d7c7c2c0d6cbe4a13d445a779335699de3d5275c4bcd3efc9f4e84a166868fbe"),
    "ibu1.py": (REPO / "nd-unfolding/ibu1/ibu1.py", "f862a953425c006f6c73f2190bd65172eb9295f0f6c181d3d2247d4de881cf12"),
    "ref_g1.py": (REPO / "nd-unfolding/ref_g1/ref_g1.py", "8e34c48552857f5eec55e1067f70f4d26b2a6de0eaae46c57983fd91fbc6e7b1"),
    "s1_assemble.py": (REPO / "nd-unfolding/s1_assemble.py", "b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7"),
    "t3p_read.py": (REPO / "nd-unfolding/tier3/t3p_read.py", "f4c221dda95fbbdf2318f7fcdde57b9e1b7fb265e85b13e1dea15341cf069295"),
    "ref_c2c1.py": (REPO / "2d-unfolding/ref_c2c1/ref_c2c1.py", "285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea"),
    "ibukt.py": (REPO / "2d-unfolding/ibukt/ibukt.py", "ef8590cf6d6d025b6db1fb8fdd100f76114390ac78eded62274b2c077c290789"),
    "run_ibukt.py": (REPO / "2d-unfolding/ibukt/run_ibukt.py", "f2b4c017e1a2e84c2cb30b43a8824b95c3f7e022f5fca23b0ceac2a750c33683"),
    "ibukt config.json": (REPO / "2d-unfolding/ibukt/config.json", "60d6c4d747596137423a869ac315c484ef65ad69f3ec209d6fd73d6e573c716c"),
}
BANK_SHA = "60416384474d1a3b0644f1e09869cf09371382ecbf3c116b1ed110cd47341e2f"
PRODUCTS = ("r5d", "r2d", "t3")


class StopControl(Exception):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------- linear algebra
def eigh(a: np.ndarray, driver: str):
    """Symmetric eigendecomposition by one of the two declared LAPACK drivers (N-PREC)."""
    a = 0.5 * (a + a.T)
    if driver == "numpy":
        return np.linalg.eigh(a)
    return sla.eigh(a, driver="evr")


def fisher_c(did, R, t0: np.ndarray, b: np.ndarray) -> np.ndarray:
    """F_c = did.fisher(R, t0, b): the count-space Fisher matrix over reco cells with mu > 0 (section 3.3)."""
    return did.fisher(sparse.csr_matrix(R), np.asarray(t0, float), np.asarray(b, float))


def decompose(F: np.ndarray, J: np.ndarray, driver: str = "numpy", cut: float = CUT) -> dict:
    """Section 3.3 on F_c and the count-space gradient J (n_cells x n_params)."""
    lam, V = eigh(F, driver)
    rng = lam > EIG_RTOL * lam.max()
    VN = V[:, ~rng]
    Fp = (V[:, rng] / lam[rng]) @ V[:, rng].T
    K = J @ J.T
    kev = np.linalg.eigvalsh(K)
    rank_ok = bool(kev.min() > EIG_RTOL * kev.max())
    n = J.shape[0]
    if VN.shape[1]:
        Mm = J @ VN @ VN.T @ J.T
        rho2, U = sla.eigh(0.5 * (Mm + Mm.T), 0.5 * (K + K.T))
        rho = np.sqrt(np.clip(rho2, 0.0, None))
    else:
        rho, U = np.zeros(n), np.eye(n)
    inf = rho > NULL_TOL
    BQ = np.linalg.qr(U[:, ~inf])[0] if (~inf).any() else np.zeros((n, 0))
    C = J @ Fp @ J.T
    if BQ.shape[1]:
        s2, Cv = eigh(BQ.T @ C @ BQ, driver)
        s = np.sqrt(np.clip(s2, 0.0, None))
        w = BQ @ Cv
    else:
        s, w = np.zeros(0), np.zeros((n, 0))
    well = s <= cut
    W = w[:, well]
    return {"lam": lam, "V": V, "range": rng, "C": C, "s": s, "w": w, "well": well, "n_well": int(well.sum()),
            "n_mid": int((~well).sum()), "dim_inf": int(inf.sum()), "PW": W @ W.T, "rank_ok": rank_ok, "n": n,
            "U_inf": U[:, inf]}


def rho_coordinate(dec: dict, J: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """C-RHO: rho(e_c) by the section 3.3 formula, and widths_from_eig's null fraction for e_c^T J."""
    import did
    VN = dec["V"][:, ~dec["range"]]
    mine = np.array([np.linalg.norm(VN.T @ J[c]) / np.linalg.norm(J[c]) for c in range(J.shape[0])])
    _, ref = did.widths_from_eig(dec["lam"], dec["V"], J, rtol=EIG_RTOL)
    return mine, ref


# ---------------------------------------------------------------------------------------------- statistics
def s_poor(dec: dict, beta: np.ndarray) -> float:
    nb = float(beta @ beta)
    return 1.0 - float(beta @ dec["PW"] @ beta) / nb if nb > 0 else float("nan")


def z_well(dec: dict, beta: np.ndarray):
    """Section 3.6: the span maximum sqrt(sum_well (w_k.beta)^2 / s_k^2); None (the sentinel) if n_well = 0."""
    if dec["n_well"] == 0:
        return None
    w, s = dec["w"][:, dec["well"]], dec["s"][dec["well"]]
    return float(np.sqrt(np.sum((w.T @ beta) ** 2 / np.maximum(s, 1e-300) ** 2)))


def z_axis(dec: dict, beta: np.ndarray):
    """Printed only: the per-axis maximum."""
    if dec["n_well"] == 0:
        return None
    w, s = dec["w"][:, dec["well"]], dec["s"][dec["well"]]
    return float(np.max(np.abs(w.T @ beta) / np.maximum(s, 1e-300)))


def r_pair(dec: dict, b_arm: np.ndarray, b_b0: np.ndarray) -> dict:
    """Section 3.6: r_poor, r_well, each with its 0.005 floor and sentinel."""
    PW = dec["PW"]
    PP = np.eye(PW.shape[0]) - PW
    out = {}
    for name, P in (("r_poor", PP), ("r_well", PW)):
        den = float(np.linalg.norm(P @ b_b0))
        out[name] = None if den <= R_FLOOR else 1.0 - float(np.linalg.norm(P @ b_arm)) / den
    return out


def r_independent(dec: dict, b_arm: np.ndarray, b_b0: np.ndarray) -> dict:
    """C-ROUTE for r: P_well from a pivoted QR of the well-constrained block (no eigen projector), the same floors."""
    n = dec["PW"].shape[0]
    if dec["n_well"]:
        q, _, _ = sla.qr(dec["w"][:, dec["well"]], mode="economic", pivoting=True)
        PW = q @ q.T
    else:
        PW = np.zeros((n, n))
    out = {}
    for name, P_ in (("r_poor", np.eye(n) - PW), ("r_well", PW)):
        den = float(np.linalg.norm(P_ @ b_b0))
        out[name] = None if den <= R_FLOOR else 1.0 - float(np.linalg.norm(P_ @ b_arm)) / den
    return out


def route_independent(dec: dict, beta: np.ndarray) -> tuple[float, float | None]:
    """C-ROUTE: W by a pivoted QR of the well-constrained block, chi^2 by solving with the full C."""
    if dec["n_well"] == 0:
        return s_poor(dec, beta), None
    Wb = dec["w"][:, dec["well"]]
    q, _, _ = sla.qr(Wb, mode="economic", pivoting=True)
    nb = float(beta @ beta)
    sp = 1.0 - float(np.sum((q.T @ beta) ** 2)) / nb
    a = Wb.T @ beta
    z2 = float(a @ np.linalg.solve(Wb.T @ dec["C"] @ Wb, a))
    return sp, float(np.sqrt(max(z2, 0.0)))


# ---------------------------------------------------------------------------------------------- bands and labels
S_BANDS = ("well-dominated", "mixed", "poor-dominated")
Z_BANDS = ("below", "intermediate", "resolvable")
R_BANDS = ("increases", "no change", "removes part", "removes most")


def band_s(x: float) -> str:
    return "poor-dominated" if x >= 0.8 else ("well-dominated" if x <= 0.2 else "mixed")


def band_z(x: float) -> str:
    return "below" if x < 1 else ("intermediate" if x < 2 else "resolvable")


def band_r(x: float) -> str:
    if x >= 0.5:
        return "removes most"
    if x >= 0.2:
        return "removes part"
    if x > -0.2:
        return "no change"
    return "increases"


def label(lo: float, hi: float, band, order) -> str:
    """A label only if [lo, hi] lies in one band; otherwise "unresolved across <bands in order>" (b1's form)."""
    a, b = band(lo), band(hi)
    if a == b:
        return a
    i, j = sorted((order.index(a), order.index(b)))
    return "unresolved across " + ", ".join(order[i:j + 1])


def label_z(lo, hi, z_noise) -> str:
    """Section 5.1's Z_well rule; for a noisy vector, the noise-maximum rule when lo >= 2."""
    if lo is None:
        return "no well-constrained combination"
    if z_noise is not None and lo >= 2:
        if lo > z_noise:
            return "resolvable"
        if hi <= z_noise:
            return "within the noise maximum"
        return "unresolved across within-the-noise-maximum and resolvable"
    return label(lo, hi, band_z, Z_BANDS)


def floor_reading(lo: float, hi: float) -> str:
    if hi < FLOOR:
        return "no bias to locate"
    if lo <= FLOOR <= hi:
        return "unresolved at the floor"
    return "read"


def is_resolved(lab: str) -> bool:
    return not (lab.startswith("unresolved") or lab in ("numerically unresolved", "MC-unresolved"))


def combined(s_lab: str, z_lab: str, floor: str, n_well: int) -> str:
    """Section 5.1: the combined statement, first case that applies."""
    if z_lab == "resolvable":
        return "points at a resolvable component"
    if floor != "read":
        return floor
    if s_lab == "poor-dominated" and z_lab == "below":
        return "consistent with an information limit"
    if n_well == 0:
        return "all combinations poorly constrained"
    if is_resolved(s_lab) and is_resolved(z_lab):
        return "intermediate"
    return "unresolved"


def across(statements: dict, primary) -> str:
    """b1's section 3 rule over the primary truths."""
    vals = [statements[t] for t in primary]
    if any(v in ("unresolved", "unresolved at the floor") or v.startswith("unresolved") for v in vals):
        bad = [t for t in primary if statements[t].startswith("unresolved")]
        return "unresolved at " + ", ".join(bad)
    if len(set(vals)) == 1:
        return f"{vals[0]} at every tested truth"
    return "truth-dependent"


# ---------------------------------------------------------------------------------------------- intervals
def interval_splits(f_mean, f_splits):
    """Five-split means: f +- h, h = T_MULT * sd(ddof=1) / sqrt(5)."""
    if f_mean is None or any(v is None for v in f_splits):
        return None, None
    h = T_MULT * float(np.std(np.asarray(f_splits, float), ddof=1)) / np.sqrt(len(f_splits))
    return f_mean - h, f_mean + h


def perturbations(sd: np.ndarray) -> np.ndarray:
    """The declared 2,000 Gaussian draws (seed 20261122), independent per cell."""
    rng = np.random.default_rng(SEED)
    return rng.normal(size=(N_PERT, sd.size)) * sd[None, :]


def interval_noisy(fn, beta: np.ndarray, sd: np.ndarray):
    """Noisy vectors: f on beta, interval = the 2.5 and 97.5 % points of f over beta + draws (asymmetric)."""
    d = perturbations(sd)
    vals = [fn(beta + x) for x in d]
    if any(v is None for v in vals):
        return None, None
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def z_noise(dec: dict, sd: np.ndarray):
    if dec["n_well"] == 0:
        return None
    return float(np.percentile([z_well(dec, x) for x in perturbations(sd)], 97.5))


# ---------------------------------------------------------------------------------------------- one vector, one build
def evaluate(dec: dict, beta: np.ndarray, kind: str, splits=None, sd=None) -> dict:
    """All declared statistics of one bias vector on one decomposition, with intervals and labels.
    kind: "splits" (five-split mean; ``splits`` the per-split vectors), "noisy" (``sd`` per cell), or "single"."""
    nb = float(np.linalg.norm(beta))
    sp, zw = s_poor(dec, beta), z_well(dec, beta)
    zn = None
    if kind == "splits":
        n_lo, n_hi = interval_splits(nb, [float(np.linalg.norm(x)) for x in splits])
        s_lo, s_hi = interval_splits(sp, [s_poor(dec, x) for x in splits])
        z_lo, z_hi = interval_splits(zw, [z_well(dec, x) for x in splits])
    elif kind == "noisy":
        n_lo, n_hi = interval_noisy(lambda v: float(np.linalg.norm(v)), beta, sd)
        s_lo, s_hi = interval_noisy(lambda v: s_poor(dec, v), beta, sd)
        z_lo, z_hi = interval_noisy(lambda v: z_well(dec, v), beta, sd)
        zn = z_noise(dec, sd)
    else:
        n_lo = n_hi = nb
        s_lo = s_hi = sp
        z_lo = z_hi = zw
    floor = floor_reading(n_lo, n_hi)
    s_lab = label(s_lo, s_hi, band_s, S_BANDS) if floor == "read" else floor
    z_lab = label_z(z_lo, z_hi, zn) if zw is not None else "no well-constrained combination"
    return {"norm": nb, "norm_interval": [n_lo, n_hi], "floor": floor, "S_poor": sp, "S_interval": [s_lo, s_hi],
            "S_label": s_lab, "Z_well": zw, "Z_interval": [z_lo, z_hi], "Z_noise": zn, "Z_label": z_lab,
            "Z_axis_max_printed": z_axis(dec, beta), "isotropic_reference": (dec["n"] - dec["n_well"]) / dec["n"],
            "combined": combined(s_lab, z_lab, floor, dec["n_well"])}


def evaluate_r(dec: dict, arm_mean, b0_mean, arm_splits, b0_splits) -> dict:
    out = {}
    main = r_pair(dec, arm_mean, b0_mean)
    per = [r_pair(dec, a, b) for a, b in zip(arm_splits, b0_splits)]
    for name in ("r_poor", "r_well"):
        sentinel = "no poorly constrained component to remove" if name == "r_poor" else "no well-constrained component to remove"
        if main[name] is None:
            out[name] = {"value": None, "label": sentinel}
            continue
        vals = [p[name] for p in per]
        if any(v is None for v in vals):
            out[name] = {"value": main[name], "label": "unresolved across bands", "why": "a split fails its 0.005 floor"}
            continue
        lo, hi = interval_splits(main[name], vals)
        out[name] = {"value": main[name], "interval": [lo, hi], "label": label(lo, hi, band_r, R_BANDS)}
    return out


# ---------------------------------------------------------------------------------------------- problems from the products
def csr(z, prefix: str):
    return sparse.csr_matrix((z[f"{prefix}__R_data"], z[f"{prefix}__R_indices"], z[f"{prefix}__R_indptr"]),
                             shape=tuple(z[f"{prefix}__R_shape"]))


def problem_5d(z, prefix: str, did, background: bool = True, known: bool = True) -> dict:
    R = csr(z, prefix)
    t0 = np.asarray(z[f"{prefix}__prior"], float)
    b = (np.asarray(z[f"{prefix}__b_known"], float) if known else 0.0) + \
        (np.asarray(z[f"{prefix}__b_extra"], float) if background else 0.0)
    b = np.broadcast_to(np.asarray(b, float), (R.shape[0],)).copy()
    L = np.asarray(z[f"{prefix}__L"], float)
    f0 = L @ t0
    keep = np.abs(f0) > 0
    J = (L[keep] / f0[keep, None])
    return {"R": R, "t0": t0, "b": b, "J": J, "f0": f0, "keep": keep, "F": fisher_c(did, R, t0, b)}


def marginal(R, b: np.ndarray, shape, drop_axes) -> tuple:
    """Section 3.4: sum the 5D reco cells over the named dropped axes (product grid; C-MARG)."""
    n_h = R.shape[1]
    dense = np.asarray(R.todense()).reshape(tuple(shape) + (n_h,))
    bb = np.asarray(b, float).reshape(tuple(shape))
    Rm = dense.sum(axis=tuple(drop_axes)).reshape(-1, n_h)
    bm = bb.sum(axis=tuple(drop_axes)).ravel()
    return sparse.csr_matrix(Rm), bm


def problem_2d(z2, half: str, cells: np.ndarray) -> dict:
    T = np.asarray(z2[f"d2_{half}__T"], float)
    M = np.asarray(z2[f"d2_{half}__M"], float)
    R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
    b = np.asarray(z2[f"d2_{half}__b_known"], float) + np.asarray(z2["d2__b_bkg"], float)
    f0 = T[cells]
    keep = f0 > 0
    J = np.zeros((int(keep.sum()), T.size))
    for r, c in enumerate(cells[keep]):
        J[r, c] = 1.0 / T[c]
    import did
    return {"R": sparse.csr_matrix(R), "t0": T, "b": b, "J": J, "f0": f0, "keep": keep,
            "F": fisher_c(did, sparse.csr_matrix(R), T, b)}


# ---------------------------------------------------------------------------------------------- MC resolution
def keeps_equal(decs: dict) -> bool:
    """Section 5.3: the same phi-space first (the f0 = 0 drop identical at full, A and B)."""
    ks = [np.asarray(decs[h].get("keep", np.ones(decs[h]["n"], bool))) for h in ("full", "A", "B")]
    return all(k.shape == ks[0].shape and np.array_equal(k, ks[0]) for k in ks)


def mc_partition_ok(decs: dict) -> tuple[bool, dict]:
    """Section 5.3: n_well and dim U-infinity equal at full, A and B, and the projector distances <= 0.2."""
    f, a, b = decs["full"], decs["A"], decs["B"]
    if not keeps_equal(decs):
        return False, {"dropped_cells_differ": True}
    same = f["n_well"] == a["n_well"] == b["n_well"] and f["dim_inf"] == a["dim_inf"] == b["dim_inf"]
    d_ab = float(np.linalg.norm(a["PW"] - b["PW"], 2))
    d_fa = float(np.linalg.norm(f["PW"] - a["PW"], 2))
    d_fb = float(np.linalg.norm(f["PW"] - b["PW"], 2))
    ok = bool(same and d_ab <= MC_PROJ and d_fa <= MC_PROJ and d_fb <= MC_PROJ)
    return ok, {"n_well": [f["n_well"], a["n_well"], b["n_well"]], "dim_inf": [f["dim_inf"], a["dim_inf"], b["dim_inf"]],
                "proj_AB": d_ab, "proj_fullA": d_fa, "proj_fullB": d_fb}


def matched_counts(decs: dict) -> dict:
    """Section 5.3: a constrained combination counts only if matched one-to-one (Hungarian, |overlap| >= 0.9) between
    the halves and against the full build, with its widths on the same side of the cut at full, A and B."""
    f, a, b = decs["full"], decs["A"], decs["B"]
    if not keeps_equal(decs):
        return {"n_well_resolved": None, "n_mid_resolved": None, "dim_inf": None, "unmatched_or_crossing": None,
                "MC-unresolved": "the dropped-cell sets differ"}

    def match(x, y):
        if x["w"].shape[1] == 0 or y["w"].shape[1] == 0:
            return {}
        ov = np.abs(x["w"].T @ y["w"])
        r, c = linear_sum_assignment(-ov)
        return {int(i): int(j) for i, j in zip(r, c) if ov[i, j] >= MC_MATCH}

    fa, fb = match(f, a), match(f, b)
    ab = match(a, b)
    n_well = n_mid = 0
    for k in range(f["w"].shape[1]):
        if k in fa and k in fb and ab.get(fa[k]) == fb[k]:
            sides = {f["s"][k] <= CUT, a["s"][fa[k]] <= CUT, b["s"][fb[k]] <= CUT}
            if len(sides) == 1:
                n_well += int(f["s"][k] <= CUT)
                n_mid += int(f["s"][k] > CUT)
    dim_inf = f["dim_inf"] if f["dim_inf"] == a["dim_inf"] == b["dim_inf"] else None
    return {"n_well_resolved": n_well, "n_mid_resolved": n_mid, "dim_inf": dim_inf,
            "unmatched_or_crossing": int(f["w"].shape[1] - n_well - n_mid)}


# ---------------------------------------------------------------------------------------------- N-PREC
def nprec(dec_np: dict, dec_evr: dict, ev_np: dict, ev_evr: dict) -> bool:
    """True if the reading is numerically resolved (section 6, N-PREC)."""
    if (dec_np["n_well"], dec_np["dim_inf"]) != (dec_evr["n_well"], dec_evr["dim_inf"]):
        return False
    if abs(ev_np["S_poor"] - ev_evr["S_poor"]) > PREC_S:
        return False
    za, zb = ev_np["Z_well"], ev_evr["Z_well"]
    if (za is None) != (zb is None):
        return False
    if za is not None and abs(za - zb) > max(PREC_Z_ABS, PREC_Z_REL * abs(za)):
        return False
    return True


# ---------------------------------------------------------------------------------------------- the run
def as_arr(v) -> np.ndarray:
    """A JSON list of widths: None or an 'inf' string is infinite; NaN stays NaN."""
    return np.array([np.inf if x is None or (isinstance(x, str) and "inf" in x.lower()) else float(x) for x in v])


def compare_rid(rid: dict, ref: dict) -> tuple[bool, dict]:
    """C-RID's bars: finite sigma_rel relative <= 1e-6 with infinities matching; null_fraction absolute <= 1e-6;
    n_null_modes and n_cells_grid exact."""
    sa, sr = as_arr(rid["sigma_rel"]), as_arr(ref["sigma_rel"])
    inf_ok = bool(np.array_equal(np.isinf(sa), np.isinf(sr)))
    fin = np.isfinite(sa) & np.isfinite(sr)
    rel = float(np.max(np.abs(sa[fin] - sr[fin]) / np.abs(sr[fin]))) if fin.any() else 0.0
    na, nr = as_arr(rid["null_fraction"]), as_arr(ref["null_fraction"])
    both = np.isfinite(na) & np.isfinite(nr)
    nf = float(np.max(np.abs(na[both] - nr[both]))) if both.any() else 0.0
    nan_ok = bool(np.array_equal(np.isnan(na), np.isnan(nr)))
    ok = inf_ok and nan_ok and rel <= 1e-6 and nf <= 1e-6 and rid["n_null_modes"] == ref["n_null_modes"] \
        and rid["n_cells_grid"] == ref["n_cells_grid"]
    return ok, {"sigma_rel_max_rel": rel, "null_fraction_max_abs": nf, "inf_match": inf_ok, "nan_match": nan_ok,
                "n_null_modes": [rid["n_null_modes"], ref["n_null_modes"]],
                "n_cells_grid": [rid["n_cells_grid"], ref["n_cells_grid"]]}


def ctl(rec: dict, cid: str, ok: bool, **vals) -> None:
    rec[cid] = {"pass": bool(ok), **vals}


def controls(prod: Path) -> tuple[dict, dict]:
    """Every STOP control (section 6) that needs no bias statistic. Returns (record, loaded)."""
    import did
    rec, L = {}, {}
    # C-OPS
    got = {k: sha256(p) for k, (p, _) in OPERANDS.items()}
    got.update({k: sha256(p) for k, (p, _) in CODE_PINS.items()})
    want = {k: s for k, (_, s) in OPERANDS.items()} | {k: s for k, (_, s) in CODE_PINS.items()}
    sums = dict(reversed(line.split("  ", 1)) for line in (prod / "SHA256SUMS").read_text().splitlines())
    prod_ok = all(sha256(prod / f) == h for f, h in sums.items())
    ctl(rec, "C-OPS", got == want and prod_ok, mismatched=[k for k in want if got[k] != want[k]], products_ok=prod_ok)
    z5, z2, z3 = (np.load(prod / f"{p}.npz", allow_pickle=False) for p in PRODUCTS)
    j5, j2 = (json.loads((prod / f"{p}.json").read_text()) for p in ("r5d", "r2d"))
    fd = json.loads(OPERANDS["fdprr"][0].read_text())
    f0b = json.loads(OPERANDS["f0b"][0].read_text())
    f0c = json.loads(OPERANDS["f0b_cpl"][0].read_text())
    t3r = json.loads(OPERANDS["t3_readout"][0].read_text())
    a2 = json.loads(OPERANDS["a2"][0].read_text())
    L.update(z5=z5, z2=z2, z3=z3, j5=j5, j2=j2, fd=fd, f0b=f0b, a2=a2)
    # C-RID (STOP): the rebuilt R-ID against FD-PRR's committed one
    ref = fd["R-ID"]
    ok, vals = compare_rid(j5["R-ID_rebuilt"], ref)
    ctl(rec, "C-RID", ok, **vals)
    # C-DID (STOP, C-DID-CONS was EQUAL): the J world at T1 under D-ID's settings against D-ID's committed widths
    tb = np.load(OPERANDS["did_tables"][0], allow_pickle=False)
    R1 = csr(z5, "t1_did")
    t1 = np.asarray(z5["t1_did__prior"], float)
    F1 = fisher_c(did, R1, t1, np.asarray(z5["t1_did__b_known"], float))
    lam, V = np.linalg.eigh(F1)
    maps = np.asarray(z5["t1_did__maps"], float)
    sig, nul = did.widths_from_eig(lam, V, maps)
    val = maps @ t1
    srel = np.divide(sig, np.abs(val), out=np.full_like(sig, np.nan), where=np.abs(val) > 0)
    names185 = [str(x) for x in tb["names"]]
    did_names = [names185[i] for i in tb["f183"]]
    pos = {n: i for i, n in enumerate(did_names)}
    common = [(i, pos[n]) for i, n in enumerate(j5["t1_names"]) if n in pos]   # section 6: "the functionals both name"
    ibu1_only = [n for n in j5["t1_names"] if n not in pos]
    did_only = [n for n in did_names if n not in set(j5["t1_names"])]
    a_s = np.array([srel[i] for i, _ in common])
    b_s = np.asarray(tb["T1/nominal/widths_nom/sigma_rel"], float)[[k for _, k in common]]
    a_n = np.array([nul[i] for i, _ in common])
    b_n = np.asarray(tb["T1/nominal/widths_nom/null_fraction"], float)[[k for _, k in common]]
    both = np.isfinite(a_s) & np.isfinite(b_s)
    dr = float(np.max(np.abs(a_s[both] - b_s[both]) / np.abs(b_s[both]))) if both.any() else float("nan")
    nmax = float(np.nanmax(np.abs(a_n - b_n))) if len(common) else float("nan")
    ctl(rec, "C-DID", len(common) > 0 and len(common) == C_DID_COMMON_EXPECTED
        and bool(np.array_equal(np.isfinite(a_s), np.isfinite(b_s))) and dr <= 1e-6 and nmax <= 1e-6,
        functionals_compared=len(common), expected_common=C_DID_COMMON_EXPECTED, sigma_rel_max_rel=dr,
        null_fraction_max_abs=nmax, ibu1_only=ibu1_only, did_only=did_only)
    # C-L (STOP)
    U, M16 = np.asarray(z5["gw_U"], float), np.asarray(z3["M16"], float)
    cells2 = [np.asarray(a2["truths"][t]["cells"], int) for t in A2_PRIMARY]
    ids = np.asarray(z2["d2__selected_ids"], int)
    ok_l = j5["C-L_linearity_rel"] <= 1e-12 and np.array_equal(U, M16) and all(len(c) == 205 for c in cells2) \
        and all(np.array_equal(c, cells2[0]) for c in cells2) and np.array_equal(cells2[0], ids) \
        and ids.size == 205 and np.unique(ids).size == 205 and int(ids.min()) >= 0 and int(ids.max()) < 224
    ctl(rec, "C-L", ok_l, linearity_rel=j5["C-L_linearity_rel"], U_equals_M16=bool(np.array_equal(U, M16)),
        cells_equal_selected=bool(np.array_equal(cells2[0], ids)))
    # C-GRID (STOP)
    n = j5["n_cells"]
    ctl(rec, "C-GRID", n["h2"] == n["h2_rid"] == n["h2_nonempty_coarse"] == ref["n_cells_grid"], n_cells=n)
    # C-T3 (STOP)
    worst = 0.0
    for t, splits in (("A7_gibuu", SPLITS), ("q3", (991000,))):
        for s in splits:
            mine = np.asarray(z3[f"t3__b__B0__{t}__s{s}__k5"], float)
            theirs = np.asarray(fd["table"][f"B0/{t}/s{s}"]["b"], float)
            worst = max(worst, float(np.max(np.abs(mine - theirs))))
    ctl(rec, "C-T3", worst <= 1e-12 and t3r["verdict"] == "COMPLETE", max_abs=worst, t3_verdict=t3r["verdict"])
    # C-F0B, C-D (STOP)
    fb = {t["name"]: t for t in f0b["truths"]}
    fc = {t["name"]: t for t in f0c["truths"]}
    ctl(rec, "C-F0B", all(fb[k]["bias"] == fc[k]["bias"] for k in fb) and set(fb) == set(fc))
    with_d = list(F0B_PRIMARY) + [t for t in F0B_SECONDARY_WITH_D]   # Amendment C: every truth converted with d
    ctl(rec, "C-D", all(f"B0/{t}/s991000" in fd["table"] and len(fd["table"][f"B0/{t}/s991000"]["d"]) == 16
                        for t in with_d), truths_checked=with_d,
        printed_without_d=[t["name"] for t in f0b["truths"] if t["name"] not in with_d])
    # C-A2 (STOP)
    worst = 0.0
    for t in A2_PRIMARY + A2_SECONDARY:
        o = a2["truths"][t]["omnifold"]
        worst = max(worst, float(np.max(np.abs(np.mean(np.asarray(o["residuals"], float), axis=0) - np.asarray(o["mean"], float)))))
    ctl(rec, "C-A2", worst <= 1e-15 and a2["bank_sha256"] == BANK_SHA, max_abs=worst)
    # C-2D (STOP)
    c2 = j2["C-2D"]
    def rel_ok(a, b):   # section 6's bar for C-2D: relative <= 1e-12 (cell by cell, against the larger magnitude)
        a, b = np.asarray(a, float), np.asarray(b, float)
        return float(np.max(np.abs(a - b))) <= 1e-12 * max(1.0, float(np.max(np.abs(b))), float(np.max(np.abs(a))))
    bk = all(rel_ok(z2[f"d2_{h}__b_known"], z2[f"d2_{h}__b_known_ibukt"]) for h in ("full", "halfA", "halfB"))
    bb = float(np.max(np.abs(np.asarray(z2["d2__b_bkg"]) - np.asarray(z2["d2__b_bkg_globalindex"]))))
    m_ok = rel_ok(z2["d2_full__M"], z2["d2__bank_ibu_response"])
    ctl(rec, "C-2D", m_ok and c2["T_vs_bank_ibu_prior_max_rel"] <= 1e-12 and bk
        and bb <= 1e-12 * max(1.0, float(np.max(np.abs(z2["d2__b_bkg"])))), **c2, b_known_equal=bk, b_bkg_max_abs=bb)
    # C-MARG (STOP): product grid by construction (the World's shape); sums conserved; the dropped axes by name
    shape, axes = j5["world_shape"], j5["axes"]
    pf = problem_5d(z5, "h2_full", did)
    ok_m = axes == ["pt", "pz", "eavail", "q3", "W"] and pf["R"].shape[0] == int(np.prod(shape))
    for drop in ((4,), (3, 4)):
        Rm, bm = marginal(pf["R"], pf["b"], shape, drop)
        ok_m = ok_m and abs(Rm.sum() - pf["R"].sum()) <= 1e-12 * pf["R"].sum() and abs(bm.sum() - pf["b"].sum()) <= 1e-12 * max(1.0, pf["b"].sum())
    ctl(rec, "C-MARG", ok_m, world_shape=shape, axes=axes)
    L["p5"] = pf
    return rec, L


def run(prod: Path, out: Path) -> int:
    import did
    out.mkdir(parents=True, exist_ok=False)
    rec, L = controls(prod)
    early = sorted(k for k, v in rec.items() if not v["pass"])
    if early:   # stop before any problem is built from inputs a control has refused
        (out / "readout.json").write_text(json.dumps({"schema": "msr-readout/1", "controls": rec, "stops": early},
                                                     indent=1, default=float) + "\n")
        (out / "readout.txt").write_text(f"STOP: {', '.join(early)} failed; no reading computed.\n")
        print(json.dumps({"stops": early}))
        return 3
    # the controls that need the decompositions but no bias vector: C-RANK, C-RHO (STOP)
    z5, z2 = L["z5"], L["z2"]
    cells = np.asarray(L["a2"]["truths"]["nominal"]["cells"], int)
    probs5 = {"full": L["p5"], "A": problem_5d(z5, "h2_halfA", did), "B": problem_5d(z5, "h2_halfB", did)}
    probs2 = {"full": problem_2d(z2, "full", cells), "A": problem_2d(z2, "halfA", cells), "B": problem_2d(z2, "halfB", cells)}
    decs = {}
    rank_ok, rho_worst = True, 0.0
    for dim, probs in (("5d", probs5), ("2d", probs2)):
        for h, p in probs.items():
            for drv in ("numpy", "evr"):
                d = decompose(p["F"], p["J"], drv)
                d["keep"] = p["keep"]
                decs[(dim, h, drv)] = d
                rank_ok = rank_ok and d["rank_ok"]
                mine, ref = rho_coordinate(d, p["J"])
                rho_worst = max(rho_worst, float(np.max(np.abs(mine - ref))))
    ctl(rec, "C-RANK", rank_ok)
    ctl(rec, "C-RHO", rho_worst <= 1e-9, max_abs=rho_worst)
    stops = sorted(k for k, v in rec.items() if not v["pass"])
    record = {"schema": "msr-readout/1", "controls": rec, "stops": stops}
    if stops:
        (out / "readout.json").write_text(json.dumps(record, indent=1, default=float) + "\n")
        (out / "readout.txt").write_text(f"STOP: {', '.join(stops)} failed; no reading computed.\n")
        print(json.dumps({"stops": stops}))
        return 3
    record.update(readings(L, probs5, probs2, decs, did, cells))
    route = record.pop("_route_worst")
    ctl(rec, "C-ROUTE", route <= 0.0, max_excess=route)
    if not rec["C-ROUTE"]["pass"]:
        stub = {"schema": "msr-readout/1", "controls": rec, "stops": ["C-ROUTE"]}
        (out / "readout.json").write_text(json.dumps(stub, indent=1, default=float) + "\n")
        (out / "readout.txt").write_text("STOP: C-ROUTE failed; no reading reported.\n")
        return 3
    (out / "readout.json").write_text(json.dumps(record, indent=1, default=float) + "\n")
    (out / "readout.txt").write_text(render(record))
    print(json.dumps({"stops": [], "readout": str(out / "readout.json")}))
    return 0


def readings(L: dict, probs5: dict, probs2: dict, decs: dict, did, cells: np.ndarray) -> dict:
    z3, fd, f0b, a2, z2 = L["z3"], L["fd"], L["f0b"], L["a2"], L["z2"]
    f0 = probs5["full"]["f0"]
    route_worst = [0.0]

    def conv5(b, s):  # FD-PRR b (P units) -> phi units, section 3.5
        return np.asarray(b, float) * np.asarray(z3[f"t3__P__s{s}"], float) / f0

    def assess(dim, beta, kind, splits=None, sd=None):
        """One vector on full/A/B and both drivers: statistics, N-PREC, MC resolution, C-ROUTE."""
        out = {}
        for h in ("full", "A", "B"):
            e_np = evaluate(decs[(dim, h, "numpy")], beta, kind, splits, sd)
            e_ev = evaluate(decs[(dim, h, "evr")], beta, kind, splits, sd)
            e_np["numerically_resolved"] = nprec(decs[(dim, h, "numpy")], decs[(dim, h, "evr")], e_np, e_ev)
            out[h] = e_np
        sp2, zw2 = route_independent(decs[(dim, "full", "numpy")], beta)
        ev = out["full"]
        exc = abs(sp2 - ev["S_poor"]) - (1e-10 + 1e-8 * abs(ev["S_poor"]))
        if (zw2 is None) != (ev["Z_well"] is None):
            exc = float("inf")          # the routes disagree on whether a well-constrained span exists
        elif ev["Z_well"] is not None:
            exc = max(exc, abs(zw2 - ev["Z_well"]) - (1e-10 + 1e-8 * abs(ev["Z_well"])))
        route_worst[0] = max(route_worst[0], exc)
        part_ok, part = mc_partition_ok({h: decs[(dim, h, "numpy")] for h in ("full", "A", "B")})
        res = dict(out["full"])
        res["halves"] = {h: {k: out[h][k] for k in ("S_label", "Z_label", "combined")} for h in ("A", "B")}
        res["partition"] = part
        if not out["full"]["numerically_resolved"]:
            res.update(S_label="numerically unresolved", Z_label="numerically unresolved", combined="unresolved")
        elif not (part_ok and all(out[h][k] == out["full"][k] for h in ("A", "B") for k in ("S_label", "Z_label"))):
            res.update(S_label="MC-unresolved", Z_label="MC-unresolved", combined="unresolved")
        return res

    R = {"M1": {"5D-B0": {}, "5D-F0b": {}, "2D-A2": {}}, "M2": {}, "secondary": {}, "printed": {}}
    # M1, 5D-B0 (five-split mean)
    b0s = [conv5(fd["table"][f"B0/A7_gibuu/s{s}"]["b"], s) for s in SPLITS]
    R["M1"]["5D-B0"]["A7_gibuu"] = assess("5d", np.mean(b0s, axis=0), "splits", b0s)
    # M1, 5D-F0b (noisy)
    table = fd["table"]
    for t in f0b["truths"]:
        if t["name"] not in F0B_PRIMARY:
            continue
        d = np.asarray(table[f"B0/{t['name']}/s991000"]["d"], float)
        k = (1.0 + d) * np.asarray(z3["t3__P__s991000"], float) / f0
        R["M1"]["5D-F0b"][t["name"]] = assess("5d", np.asarray(t["bias"], float) * k, "noisy",
                                               sd=np.asarray(t["noise_sigma"], float) * np.abs(k))
    # M1, 2D-A2 (noisy, five trials)
    T = np.asarray(z2["d2_full__T"], float)
    ratio = np.asarray(z2["d2__truth_nominal"], float)[cells] / (np.asarray(z2["d2__factor"], float)[cells] * T[cells])
    R["printed"]["2D_P_over_f0"] = {"min": float(np.min(ratio)), "max": float(np.max(ratio)), "spread": float(np.std(ratio))}

    def a2_vec(t, m):
        o = a2["truths"][t][m]
        k = (1.0 + np.asarray(o["departure"], float)) * ratio
        res = np.asarray(o["residuals"], float)
        return np.asarray(o["mean"], float) * k, np.std(res, axis=0, ddof=1) / np.sqrt(res.shape[0]) * np.abs(k)
    for t in A2_PRIMARY:
        beta, sd = a2_vec(t, "omnifold")
        R["M1"]["2D-A2"][t] = assess("2d", beta, "noisy", sd=sd)
    # combined across truths
    R["M1_across"] = {
        "5D-F0b": across({t: v["combined"] for t, v in R["M1"]["5D-F0b"].items()}, F0B_PRIMARY),
        "2D-A2": across({t: v["combined"] for t, v in R["M1"]["2D-A2"].items()}, A2_PRIMARY)}
    # M2, the oracle arms at A7 GiBUU: MO at k = 5, OP at k = 2, each against B0 at k = 5
    b0k5 = [conv5(z3[f"t3__b__B0__A7_gibuu__s{s}__k5"], s) for s in SPLITS]
    for arm, k in (("MO", 5), ("OP", 2)):
        arms = [conv5(z3[f"t3__b__{arm}__A7_gibuu__s{s}__k{k}"], s) for s in SPLITS]
        am, bm = np.mean(arms, axis=0), np.mean(b0k5, axis=0)
        r = {h: evaluate_r(decs[("5d", h, "numpy")], am, bm, arms, b0k5) for h in ("full", "A", "B")}
        r_evr = evaluate_r(decs[("5d", "full", "evr")], am, bm, arms, b0k5)
        ri = r_independent(decs[("5d", "full", "numpy")], am, bm)
        res = dict(r["full"], k=k, b0_k=5)
        part_ok, _ = mc_partition_ok({h: decs[("5d", h, "numpy")] for h in ("full", "A", "B")})
        same_part = (decs[("5d", "full", "numpy")]["n_well"], decs[("5d", "full", "numpy")]["dim_inf"]) == \
            (decs[("5d", "full", "evr")]["n_well"], decs[("5d", "full", "evr")]["dim_inf"])
        for name in ("r_poor", "r_well"):
            v, ve, vi = r["full"][name]["value"], r_evr[name]["value"], ri[name]
            if (v is None) != (vi is None) or (v is not None and abs(vi - v) > 1e-10 + 1e-8 * abs(v)):
                route_worst[0] = float("inf") if (v is None) != (vi is None) else max(
                    route_worst[0], abs(vi - v) - (1e-10 + 1e-8 * abs(v)))
            if not same_part or (v is None) != (ve is None) or (v is not None and abs(v - ve) > PREC_R):
                res[name] = dict(res[name], label="numerically unresolved")
            elif not (part_ok and r["A"][name]["label"] == r["full"][name]["label"] == r["B"][name]["label"]):
                res[name] = dict(res[name], label="MC-unresolved")
        R["M2"][arm] = res
    # M3 (5D feature sets) and M4 (2D)
    shape = L["j5"]["world_shape"]
    M3 = {}
    for name, drop in (("5D", ()), ("4D", (4,)), ("3D", (3, 4))):
        dd = {}
        for h, p in probs5.items():
            if drop:
                Rm, bm = marginal(p["R"], p["b"], shape, drop)
                F = fisher_c(did, Rm, p["t0"], bm)
            else:
                F = p["F"]
            dd[h] = decompose(F, p["J"], "numpy")
            dd[h]["keep"] = p["keep"]
        M3[name] = {**matched_counts(dd), "raw": {h: [dd[h]["n_well"], dd[h]["n_mid"], dd[h]["dim_inf"]] for h in dd},
                    "spectrum_full_printed": dd["full"]["s"].tolist()}
        M3[name]["_W"] = dd["full"]["w"][:, dd["full"]["well"]]
    for a, b in (("3D", "4D"), ("4D", "5D")):
        Wa, Wb = M3[a]["_W"], M3[b]["_W"]
        M3[f"angles_{a}_{b}_printed"] = (np.degrees(sla.subspace_angles(Wa, Wb)).tolist() if Wa.shape[1] and Wb.shape[1] else [])
    for k in ("3D", "4D", "5D"):
        M3[k].pop("_W")
    R["M3"] = M3
    R["M4"] = {**matched_counts({h: decs[("2d", h, "numpy")] for h in ("full", "A", "B")}),
               "spectrum_full_printed": decs[("2d", "full", "numpy")]["s"].tolist()}
    # secondary and printed
    sec = R["secondary"]
    sec["5D q3 (single split, k=5; OP k=2)"] = {
        arm: assess("5d", conv5(z3[f"t3__b__{arm}__q3__s991000__k{k}"], 991000), "single")
        for arm, k in (("B0", 5), ("MO", 5), ("OP", 2))}
    sec["5D k=50, secondary; not M2"] = {
        arm: assess("5d", np.mean([conv5(z3[f"t3__b__{arm}__A7_gibuu__s{s}__k50"], s) for s in SPLITS], axis=0),
                    "splits", [conv5(z3[f"t3__b__{arm}__A7_gibuu__s{s}__k50"], s) for s in SPLITS]) for arm in ("B0", "MO")}
    sec["5D k=50, secondary; not M2"].update({
        f"{arm} at q3": assess("5d", conv5(z3[f"t3__b__{arm}__q3__s991000__k50"], 991000), "single") for arm in ("B0", "MO")})
    for t in f0b["truths"]:
        if t["name"] in F0B_PRIMARY:
            continue
        key = f"B0/{t['name']}/s991000"
        if t["name"] in F0B_SECONDARY_WITH_D:
            d = np.asarray(table[key]["d"], float)
            k = (1.0 + d) * np.asarray(z3["t3__P__s991000"], float) / f0
            sec.setdefault("5D-F0b secondary", {})[t["name"]] = assess("5d", np.asarray(t["bias"], float) * k, "single")
        else:
            sec.setdefault("5D-F0b secondary, no d (truth-relative units, P/f0 only)", {})[t["name"]] = assess(
                "5d", np.asarray(t["bias"], float) * np.asarray(z3["t3__P__s991000"], float) / f0, "single")
    for t in A2_SECONDARY:
        beta, sd = a2_vec(t, "omnifold")
        sec.setdefault("2D-A2 secondary", {})[t] = assess("2d", beta, "noisy", sd=sd)
    for m in ("ibu5", "ibu10"):
        for t in A2_PRIMARY + A2_SECONDARY:
            beta, sd = a2_vec(t, m)
            sec.setdefault(f"2D {m} (printed)", {})[t] = assess("2d", beta, "noisy", sd=sd)
    P = R["printed"]
    P["dropped_cells_f0_zero"] = {f"{dim} {h}": int((~p["keep"]).sum()) for dim, probs in (("5d", probs5), ("2d", probs2))
                                  for h, p in probs.items()}
    P["P_over_f0_5D"] = (np.asarray(z3["t3__P__s991000"], float) / f0).tolist()
    for dim in ("5d", "2d"):
        d = decs[(dim, "full", "numpy")]
        P[f"{dim}_spectrum_s"] = d["s"].tolist()
        P[f"{dim}_fisher_eigenvalues"] = d["lam"].tolist()
        p = (probs5 if dim == "5d" else probs2)["full"]
        P[f"{dim}_n_well_at_cuts"] = {str(c): decompose(p["F"], p["J"], "numpy", cut=c)["n_well"] for c in CUTS_PRINT}
        sig, nul = did.widths_from_eig(d["lam"], d["V"], p["J"], rtol=EIG_RTOL)
        P[f"{dim}_per_cell_width_printed"] = sig.tolist()
        P[f"{dim}_per_cell_null_fraction_printed"] = nul.tolist()
    for tag, kw in (("b0", {"background": False, "known": False}), ("did_settings", {"background": False, "known": True})):
        pv = problem_5d(L["z5"], "h2_full", did, **kw)
        dv = decompose(pv["F"], pv["J"], "numpy")
        P[f"5d_variant_{tag}"] = {"n_well": dv["n_well"], "n_mid": dv["n_mid"], "dim_inf": dv["dim_inf"], "s": dv["s"].tolist()}
    P["R00_R15_alone"] = r16_alone(probs5["full"], L["z5"], did)
    return {**R, "_route_worst": route_worst[0]}


def r16_alone(p: dict, z5, did) -> dict:
    """Printed only (Q3's comparison): an approximate aggregation of the H2 capture to the 16 reported cells as truth,
    each H2 cell's count shared over the cells it feeds in proportion to L (no fine-level response is captured)."""
    Lm = np.asarray(z5["h2_full__L"], float)
    a = np.abs(Lm) / np.maximum(np.abs(Lm).sum(axis=0, keepdims=True), 1e-300)   # (16, 29)
    t16 = a @ p["t0"]
    R16 = sparse.csr_matrix(p["R"] @ (a.T * p["t0"][:, None]) / np.maximum(t16, 1e-300)[None, :])
    F = fisher_c(did, R16, t16, p["b"])
    keep = t16 > 0
    J = np.diag(1.0 / t16[keep]) if keep.all() else np.eye(16)[keep] / t16[keep, None]
    d = decompose(F, J, "numpy")
    return {"label": "approximate aggregation; printed only", "n_well": d["n_well"], "n_mid": d["n_mid"],
            "dim_inf": d["dim_inf"], "s": d["s"].tolist()}


# ---------------------------------------------------------------------------------------------- the text
SENT_S = {"poor-dominated": "at least four fifths of the bias's sum of squares lies outside the combinations of reported "
                            "cells that the binned detector-level inputs constrain to 10 % or better at the data exposure",
          "mixed": "between a fifth and four fifths of the bias's sum of squares lies outside the well-constrained combinations",
          "well-dominated": "at least four fifths of the bias's sum of squares lies in combinations the binned inputs "
                            "constrain to 10 % or better"}
SENT_C = {"points at a resolvable component": "a combination the binned inputs constrain to 10 % or better carries at "
          "least two binned CR widths of bias. This points at an estimator effect that the binned data could in principle "
          "resolve; it does not show that it is fixable, or how.",
          "consistent with an information limit": "the bias lies outside the span of the eigen-combinations the binned "
          "inputs constrain to 10 % or better, and is below one binned CR width everywhere in that span. This is consistent "
          "with an information limit of the binned inputs; it does not show that no estimator could remove it.",
          "all combinations poorly constrained": "no combination of reported cells is constrained to 10 % or better; the "
          "bias's location among combinations is not tested."}


def m2_sentences(arm: str, v: dict) -> list[str]:
    """Section 5.2's licensed M2 sentences (and nothing else)."""
    rp, rw = v["r_poor"]["label"], v["r_well"]["label"]
    out = []
    what = "the true missed-event weights" if arm == "MO" else "the oracle pull, the bound on what step 2 can reach (T3 section 3.3),"
    if rp == "removes most" and rw in ("no change", "no well-constrained component to remove"):
        out.append(f"  At k = {v['k']}, {what} remove mainly the poorly constrained part of B0's bias (B0 at k = {v['b0_k']}).")
    elif rw == "removes most" and rp in ("no change", "no poorly constrained component to remove"):
        out.append(f"  At k = {v['k']}, {what} remove mainly the well-constrained part of B0's bias (B0 at k = {v['b0_k']}).")
    if arm == "OP":
        out.append(f"  OP is read at its only iterate, k = {v['k']}, as the bound on what step 2 can reach.")
    return out


def render(rec: dict) -> str:
    lines = ["MSR readout (declaration rev 4). Labels and sentences are the declaration's section 5.1; nothing is chosen",
             "after a statistic. NOT CITABLE FOR: a cause beyond 'consistent with', an estimator change, coverage, any data",
             "quantity, or note wording.", "", "Controls: " + ", ".join(f"{k} {'PASS' if v['pass'] else 'FAIL'}"
                                                                       for k, v in sorted(rec["controls"].items())), ""]
    for set_name, block in rec["M1"].items():
        lines.append(f"M1 {set_name}:")
        for t, v in block.items():
            sent = SENT_C.get(v["combined"], "")
            lines.append(f"  {t}: S_poor {v['S_label']}; Z_well {v['Z_label']}; combined: {v['combined']}."
                         + (f" At truth {t}, {sent}" if sent else ""))
            if v["S_label"] in SENT_S:
                lines.append(f"    At truth {t} ({set_name[:2]}), {SENT_S[v['S_label']]}.")
        if set_name in rec.get("M1_across", {}):
            lines.append(f"  across truths: {rec['M1_across'][set_name]}")
    for arm, v in rec["M2"].items():
        lines.append(f"M2 {arm} (k = {v['k']}) against B0 (k = {v['b0_k']}): r_poor {v['r_poor']['label']}; "
                     f"r_well {v['r_well']['label']}")
        lines += m2_sentences(arm, v)
    for name in ("5D", "4D", "3D"):
        m = rec["M3"][name]
        lines.append(f"M3 {name}: with the {name} reco feature set, {m['n_well_resolved']} combinations of the 16 reported "
                     f"cells are constrained to 10 % or better at the data exposure, {m['n_mid_resolved']} are constrained "
                     f"to worse than 10 %, and {m['dim_inf'] if m['dim_inf'] is not None else 'MC-unresolved'} are "
                     f"unconstrained (MC-resolved counts; {m['unmatched_or_crossing']} not MC-resolved).")
    m = rec["M4"]
    lines.append(f"M4 2D: {m['n_well_resolved']} of the 205 cells' combinations constrained to 10 % or better, "
                 f"{m['n_mid_resolved']} worse, {m['dim_inf'] if m['dim_inf'] is not None else 'MC-unresolved'} unconstrained "
                 f"(MC-resolved; {m['unmatched_or_crossing']} not MC-resolved).")
    lines.append("")
    lines.append("Secondary and printed items are in readout.json; every k = 50 line is 'k = 50, secondary; not M2'.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--products", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    import did
    for k, (p, s) in CODE_PINS.items():
        if sha256(p) != s:
            print(f"REFUSED: {k} is not at its pin", file=sys.stderr)
            return 9
    assert Path(did.__file__).resolve() == CODE_PINS["did.py"][0].resolve()
    return run(a.products, a.out)


if __name__ == "__main__":
    sys.exit(main())

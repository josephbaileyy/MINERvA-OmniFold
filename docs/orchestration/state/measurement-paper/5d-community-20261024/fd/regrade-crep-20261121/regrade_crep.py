"""REGRADE driver (REGRADE-DECLARATION.md rev 2): the held-out-tune coverage toys graded against C' = C_T + C_add(T).

Glue only. ``fd_1b_null`` (chi2_nonnull, null_contents, Discrete), ``fd_1b_mc.grade`` and ``cov2d_null.null_at_T`` are
imported unchanged. Every quadratic form goes through ``fd_1b_null.chi2_nonnull`` (section 4: one factorisation):
  chi2_t = chi2_nonnull(E, C')                 M' = mean chi2_t / ndf',  SE = sd(chi2_t, ddof 1) / sqrt(n) / ndf'
  mean-error part  = chi2_nonnull(ebar, C') / ndf'
  spread part      = M' - mean-error part      (= tr(A S) / ndf' with S's divisor n; the identity is tested)
  tau              = sum_j mu_j chi2_nonnull(u_j, C') / ndf'   over C_add = sum_j mu_j u_j u_j^T  (= tr(A C_add) / ndf')
  M_full           = M' + tau
R-chi2 reads "under-describes on average" iff M_full - 1 > 3 SE, else "not shown" (one-sided; section 4).
R-grade (descriptive) rebuilds the null with C_add in the Gaussian and in C_T, then fd_1b_mc.grade at A5's tolerance;
its verdict string is written with the prefix "descriptive-" beside "a reading, not a proof".

  python3 regrade_crep.py run2d --q205 <cov2d_Q_205.npz> --out <record.json> [--tunes AR23 G18]
  python3 regrade_crep.py run16 --capture-dir <dir of capture_<t>_<reading>.npz> --out <record.json>
(--out is one JSON file, refused if it exists.)

MEASURES: the declaration's R-chi2 and R-grade per evaluation, with A0 and the controls. CANNOT AUTHORIZE: any change
to a reported covariance, any note or paper wording, a cause, or a p-value.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
for p in (REPO / "2d-unfolding" / "cov2d", REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import fd_1b_null as fn  # noqa: E402
import fd_1b_mc as mc  # noqa: E402

FD = HERE.parent
TUNES_2D = ("AR23", "G18")
EVALS_16 = ("g18/minus2", "g18/all", "ar23/minus2", "ar23/all")
NULL_SEED_16 = {"g18/minus2": 4_770_310, "g18/all": 4_770_320, "ar23/minus2": 4_770_410, "ar23/all": 4_770_420}
PINS = {   # section 1, sha256 of the committed bytes
    "E_AR23": (FD / "tier2-20261110/t2a/AR23/E_AR23.npz",
               "ccda9c50c6bb1cbbdd2206c8954652f4f77c6cf2b4451e8488601e9896b0a85e"),
    "E_G18": (FD / "tier2-20261110/t2a/G18/E_G18.npz",
              "846b9d852218b531d605bd955ca9a9037d187e74723077bdfff4557efafc3ba6"),
    "blocks_AR23": (FD / "receipts-cov2d/readout/AR23/blocks_AR23.npz",
                    "abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee"),
    "blocks_G18": (FD / "receipts-cov2d/readout/G18/blocks_G18.npz",
                   "7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d"),
    "score_AR23": (FD / "receipts-cov2d/readout/AR23/score_AR23.json",
                   "fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1"),
    "score_G18": (FD / "receipts-cov2d/readout/G18/score_G18.json",
                  "849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec"),
    "cpl_block": (FD / "with-cpl/block/cpl_block.npz",
                  "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f"),
    "cpl_block_json": (FD / "with-cpl/block/cpl_block.json",
                       "4023746e3a819e8cc8348c457d7dc1ee55df66eaa5f5f68082824b9df27cabd6"),
    "cpl_cells_csv": (FD / "with-cpl/data-product/fd_data_product_cpl_cells.csv",
                      "b3a7d0cac19ab3ca17ecb603b5c4814fb8e072117cdd01c47383eb8f1d8cd6cd"),
    "readout_g18": (FD / "receipts-ll5d/readout/node/readout-g18.json",
                    "7bd6d3901fa9d5b017f7c5c2335ef70a4a41be58510d31cbcae3734556d0b12d"),
    "readout_ar23": (FD / "receipts-ll5d/readout/node/readout-ar23.json",
                     "5b3fbbf5ed6fcf0b2da9cf9a3024910c27c55bbb4f84373ff453fcba88feba10"),
}
Q205_SHA = "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2"
SYM_TOL = 1e-12
PSD_TOL = 1e-12
A0_CHI2_FLOOR = 1e-9      # amendment 1: A0(b) at COV2D A5's max(1e-9, 10 kappa_2 eps), as T2-BINDING-1 addendum 1
READING_SE = 3.0


class Stop(RuntimeError):
    """A control failed: the evaluation is a STOP, recorded unrepaired."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pinned(key: str) -> Path:
    path, want = PINS[key]
    got = sha256(path)
    if got != want:
        raise Stop(f"C-PIN: {path} is {got}, pinned {want}")
    return path


# ------------------------------------------------------------------------------------------------ section 2: carry
def carry_frac(C: np.ndarray, x_num: np.ndarray, x_den: np.ndarray) -> np.ndarray:
    """diag(x_num / x_den) C diag(x_num / x_den): COV2D's C08 rule (cov2d_blocks.py:141-142)."""
    r = np.asarray(x_num, np.float64) / np.asarray(x_den, np.float64)
    return r[:, None] * np.asarray(C, np.float64) * r[None, :]


def carry_rel(P_rel: np.ndarray, X: np.ndarray) -> np.ndarray:
    """diag(X) P_rel diag(X): C_PL,5D at tune T."""
    X = np.asarray(X, np.float64)
    return X[:, None] * np.asarray(P_rel, np.float64) * X[None, :]


# ------------------------------------------------------------------------------------------ section 4: R-chi2
def read_rule(M_full: float, se: float) -> bool:
    """Section 4's one-sided rule: True ('under-describes on average') iff M_full - 1 > 3 SE, strictly."""
    return (M_full - 1.0) > READING_SE * se


def r_chi2(E: np.ndarray, C_T: np.ndarray, C_add: np.ndarray) -> dict:
    """R-chi2 on C' = C_T + C_add, every quadratic form through fd_1b_null.chi2_nonnull."""
    E = np.asarray(E, np.float64)
    Cp = np.asarray(C_T, np.float64) + np.asarray(C_add, np.float64)
    chi2, ndf = fn.chi2_nonnull(E, Cp)
    n = E.shape[0]
    M = float(chi2.mean() / ndf)
    se = float(chi2.std(ddof=1) / math.sqrt(n) / ndf)
    mean_err = float(fn.chi2_nonnull(E.mean(axis=0)[None, :], Cp)[0][0] / ndf)
    mu, U = np.linalg.eigh(np.asarray(C_add, np.float64))
    tau = float(fn.chi2_nonnull(U.T, Cp)[0] @ mu / ndf) if np.any(C_add) else 0.0
    M_full = M + tau
    lam = np.linalg.eigvalsh(Cp)
    keep = lam > fn.RANK_REL * lam.max()
    lam_T, V_T = np.linalg.eigh(np.asarray(C_T, np.float64))
    keep_T = lam_T > fn.RANK_REL * lam_T.max()
    ndf_T = int(keep_T.sum())
    _, V_p = np.linalg.eigh(Cp)
    Vk = V_p[:, keep]
    resid = np.linalg.norm(V_T[:, keep_T] - Vk @ (Vk.T @ V_T[:, keep_T]), axis=0)   # C_T kept modes outside C''s kept span
    dropped = int(np.sum(resid > 1e-6))
    under = read_rule(M_full, se)
    return {
        "ndf": ndf, "n": n, "M_prime": M, "SE": se, "mean_error_part": mean_err, "spread_part": M - mean_err,
        "tau": tau, "M_full": M_full,
        "reading": "under-describes on average" if under else "not shown",
        "toys_own_mean_line": {"M_prime_minus_1_over_SE": (M - 1.0) / se,
                               "toys_mean_exceeds_1_by_3SE": bool((M - 1.0) > READING_SE * se),
                               "what": "descriptive; the stored toys' own mean chi2/ndf' against C'"},
        "cut": {"ndf_C_T": ndf_T, "ndf_C_prime": ndf, "C_T_kept_modes_outside_C_prime_kept_span": dropped,
                "max_residual_of_C_T_kept_modes": float(resid.max()) if resid.size else 0.0,
                "smallest_kept_rel": float(lam[keep].min() / lam.max()),
                "largest_dropped_rel": float(lam[~keep].max() / lam.max()) if np.any(~keep) else None},
        "assumptions": ["the model for the added blocks (r independent of e, E r = 0, Cov r = C_add) is untested",
                        "the run-period blocks have no generative law (SCOPING.md item a3)",
                        "the fractional carry of section 2",
                        "M_full is a conditional expectation of the full test given the stored toys, "
                        "not a draw and not a coverage fraction",
                        "C' is the tune-carried analogue of the reported covariance, not the published matrix"],
    }


# ------------------------------------------------------------------------------------------ section 6: controls
def check_psd(C: np.ndarray, name: str) -> dict:
    C = np.asarray(C, np.float64)
    if not np.any(C):
        return {"name": name, "skipped": "identically zero"}
    asym = float(np.max(np.abs(C - C.T)) / np.max(np.abs(C)))
    lam = np.linalg.eigvalsh((C + C.T) / 2)
    rec = {"name": name, "asym_rel": asym, "lam_min_rel": float(lam[0] / lam[-1]), "lam_max": float(lam[-1])}
    if asym > SYM_TOL or lam[0] < -PSD_TOL * lam[-1]:
        raise Stop(f"C-PSD: {name} {rec}")
    return rec


def a0_chi2_tol(C: np.ndarray) -> dict:
    """Amendment 1: A0(b)'s tolerance, max(1e-9, 10 kappa_2 eps), COV2D A5's rule as T2-BINDING-1 addendum 1 adopted
    it; kappa_2 = lambda_max / lambda_min over C's non-null subspace (eigenvalues above fd_1b_null.RANK_REL of the
    largest, the chi2's own subspace). It equals A5's full-spectrum kappa_2 when every eigenvalue is kept (G18), and
    is smaller (a stricter tolerance) when a positive eigenvalue falls under the cut (AR23's smallest, 9.99e-13 of the
    largest); it is never looser than T2A's rule and stays finite when lambda_min <= 0, where A5's raw rule is infinite."""
    lam = np.linalg.eigvalsh(np.asarray(C, np.float64))
    if not lam.max() > 0:
        raise Stop(f"A0(b): C has no positive eigenvalue (lambda_max {lam.max():.3e})")
    keep = lam > fn.RANK_REL * lam.max()
    kappa = float(lam.max() / lam[keep].min())
    eps = float(np.finfo(np.float64).eps)
    return {"rule": "max(1e-9, 10 kappa_2 eps), kappa_2 on the non-null subspace", "kappa2": kappa,
            "tol": max(A0_CHI2_FLOOR, 10 * kappa * eps)}


def a0_compare(g: dict, committed: dict, flags_key: str, flags_now, tol: float) -> dict:
    """A0 (section 6, amendment 1): (a) ndf, joint_count, counts exact; (b) chi2_mean_over_ndf within ``tol``
    relative (a0_chi2_tol); (c) k_joint and the flags, which depend on the re-simulated null: a mismatch alone is
    'null redraw differs'."""
    a = {k: (g[k], committed[k], g[k] == committed[k]) for k in ("ndf", "joint_count", "counts")}
    rel = abs(g["chi2_mean_over_ndf"] / committed["chi2_mean_over_ndf"] - 1.0)
    out = {"a": {k: v[2] for k, v in a.items()}, "b_rel": rel, "b_tol": tol, "b": bool(rel <= tol),
           "c": {"k_joint": g["k_joint"] == committed["k_joint"], "flags": flags_now == committed[flags_key]}}
    if not all(out["a"].values()) or not out["b"]:
        raise Stop(f"A0: {out}; values {[(k, v[0], v[1]) for k, v in a.items() if not v[2]]}")
    out["c_reading"] = "equal" if all(out["c"].values()) else "null redraw differs"
    return out


def chol_tol(C: np.ndarray) -> float:
    """A5's rule, max(1e-9, 10 kappa_2(C) eps) (cov2d_readout.cholesky_tol, ll5d_b.cholesky_tol)."""
    lam = np.linalg.eigvalsh(np.asarray(C, np.float64))
    kappa = float(lam[-1] / lam[0]) if lam[0] > 0 else float("inf")
    return max(1e-9, 10 * kappa * float(np.finfo(np.float64).eps))


def _strict(fun, *args, **kw):
    """Run a null builder with RuntimeWarning raised as an error (C-PSD: NumPy's multivariate_normal only warns on a
    non-PSD Gaussian); a warning or a refusal is a STOP."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            return fun(*args, **kw)
    except (RuntimeWarning, fn.Refusal) as e:
        raise Stop(f"C-NULL/C-PSD: {type(e).__name__}: {e}") from e


def _grade(E: np.ndarray, C: np.ndarray, null: dict) -> dict:
    """fd_1b_mc.grade at A5's tolerance; its refusal is a STOP with the compared values."""
    try:
        return mc.grade(E, C, null, chol_tol=chol_tol(C))
    except mc.Refusal as e:
        raise Stop(f"grade refused: {e}; compared {getattr(e, 'compared', None)}") from e


def descriptive(g: dict) -> dict:
    keep = ("joint_count", "k_joint", "joint_flag", "ndf", "cell_flag", "counts", "k_cell", "chi2_mean_over_ndf")
    out = {k: g[k] for k in keep}
    out["verdict"] = "descriptive-" + g["verdict"]
    out["note"] = "a reading, not a proof"
    return out


# ------------------------------------------------------------------------------------------------- the 2D half
def blocks_2d(T: str) -> dict:
    with np.load(pinned(f"blocks_{T}"), allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


def null_2d(B: dict, C_run: np.ndarray) -> dict:
    """cov2d_null.null_at_T on a copy without C_T_minus, C08 + C_run in place of C08, C_T + C_run in place of C_T."""
    import cov2d_null as cn
    b = {k: v for k, v in B.items() if k != "C_T_minus"}
    b["C08"] = B["C08"] + C_run
    b["C_T"] = B["C_T"] + C_run
    bands = {k[len("band__"):]: v for k, v in B.items() if k.startswith("band__")}
    res = _strict(cn.null_at_T, b, bands, B["minos_x"], B["w_flux"])
    return res["null"], b["C_T"]


def run2d(q205: Path, tunes=TUNES_2D) -> dict:
    if not tunes or any(T not in TUNES_2D for T in tunes):
        raise SystemExit(f"tunes must be a non-empty subset of {TUNES_2D}")
    if sha256(q205) != Q205_SHA:
        raise Stop(f"C-PIN: {q205} is not {Q205_SHA}")
    with np.load(q205, allow_pickle=False) as z:
        C_PL, cells_q, x_q = np.asarray(z["C_PL"], np.float64), np.asarray(z["cells"]), np.asarray(z["x"], np.float64)
    out = {"schema": "regrade-crep/2d/1", "q205_sha256": Q205_SHA, "tunes": list(tunes), "evaluations": {}}
    for T in tunes:
        rec = {}
        try:
            with np.load(pinned(f"E_{T}"), allow_pickle=False) as z:
                E = np.asarray(z["E"], np.float64)
            B = blocks_2d(T)
            committed = json.loads(pinned(f"score_{T}").read_text())["grade"]
            if not (np.array_equal(cells_q, np.flatnonzero(B["rep"])) and np.array_equal(x_q, B["x_R"])):
                raise Stop("C-MAP: the Q file's cells or x are not the blocks' rep / x_R")
            rec["C_MAP"] = "pass"
            # A0: C_add = 0 through the same path (C_T_minus removed: the primary null is unchanged by it)
            null0, C0 = null_2d(B, np.zeros_like(C_PL))
            g0 = _grade(E, C0, null0)
            flat = [int(c) for c in np.flatnonzero(B["rep"])]
            flags0 = [flat[i] for i, f in enumerate(g0["cell_flag"]) if f]
            t0 = a0_chi2_tol(C0)
            rec["A0"] = a0_compare(g0, committed, "flagged_cells", flags0, t0["tol"])
            rec["A0"]["b_rule"] = t0
            C_run = carry_frac(C_PL, B["x_T"], B["x_R"])
            rec["C_PSD"] = check_psd(C_run, f"C_run({T})")
            rec["R_chi2"] = r_chi2(E, B["C_T"], C_run)
            null1, C1 = null_2d(B, C_run)
            g1 = _grade(E, C1, null1)
            rec["descriptive_regrade"] = descriptive(g1)
            rec["descriptive_regrade"]["flagged_cells"] = [flat[i] for i, f in enumerate(g1["cell_flag"]) if f]
            C_abs = C_PL
            rec["sensitivity_absolute_carry"] = {"R_chi2": r_chi2(E, B["C_T"], C_abs), "read_by": "nothing"}
            rec["status"] = "done"
        except Stop as e:
            rec["status"], rec["stop"] = "STOP", str(e)
        out["evaluations"][T] = rec
    return out


# -------------------------------------------------------------------------------------------- the sixteen cells
def load_capture(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        d = {k: np.asarray(z[k]) for k in z.files}
    names = [str(s) for s in d["law_names"]]
    d["laws"] = [fn.Discrete(np.asarray(d[f"law_{i}_values"], np.float64), np.asarray(d[f"law_{i}_probs"], np.float64))
                 for i in range(len(names))]
    return d


def cmap16(f: np.ndarray) -> dict:
    """C-MAP16 (section 3): cpl_block.json's cells, the data product's cells csv and R00-R15 are one order, the csv's
    f column equals cpl_block's f, and cpl_block.json names the pinned npz. A failure stops every sixteen-cell
    evaluation (raised before any)."""
    import csv
    want = [f"R{i:02d}" for i in range(16)]
    js = json.loads(pinned("cpl_block_json").read_text())
    with open(pinned("cpl_cells_csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    names_csv = [r["cell"] for r in rows]
    f_csv = np.array([float(r["f"]) for r in rows])
    npz_named = json.dumps(js.get("npz"))
    ok = (js["cells"] == want and names_csv == want and len(f_csv) == 16
          and float(np.max(np.abs(f_csv / f - 1.0))) <= 1e-12 and PINS["cpl_block"][1] in npz_named)
    rec = {"cells_json": js["cells"], "cells_csv": names_csv, "f_csv_rel": float(np.max(np.abs(f_csv / f - 1.0))),
           "npz_named": PINS["cpl_block"][1] in npz_named}
    if not ok:
        raise Stop(f"C-MAP16: {rec}")
    return rec


def run16(capdir: Path, manifest: dict | None = None) -> dict:
    with np.load(pinned("cpl_block"), allow_pickle=False) as z:
        f, P_rel = np.asarray(z["f"], np.float64), np.asarray(z["P_rel"], np.float64)
        C_resp, C_PL5D = np.asarray(z["C_resp"], np.float64), np.asarray(z["C_PL5D"], np.float64)
    out = {"schema": "regrade-crep/16/1", "capture_manifest": manifest, "evaluations": {}}
    try:
        out["C_MAP16"] = cmap16(f)
    except Stop as ex:
        out["C_MAP16"] = {"stop": str(ex)}
        out["evaluations"] = {e: {"status": "STOP", "stop": str(ex)} for e in EVALS_16}
        return out
    ident = float(np.max(np.abs(carry_rel(P_rel, f) - C_PL5D)) / np.max(np.abs(C_PL5D)))
    for e in EVALS_16:
        truth, reading = e.split("/")
        rec = {}
        try:
            cap = load_capture(capdir / f"capture_{truth}_{reading}.npz")
            committed = json.loads(pinned(f"readout_{truth}").read_text())["evaluations"][e]["grade"]
            if ident > 1e-12:
                raise Stop(f"C-F16: C_PL5D is not diag(f) P_rel diag(f) ({ident:.2e})")
            frel = float(np.max(np.abs(cap["f"] / f - 1.0)))
            if frel > 1e-12:
                raise Stop(f"C-F16: cpl_block f differs from the capture's s1 f by {frel:.2e}")
            rec["C_F16"] = {"identity_rel": ident, "f_rel": frel}
            E, C_T, gauss, laws = cap["E"], cap["C_T"], cap["gauss"], cap["laws"]
            null0 = _strict(fn.null_contents, laws, gauss, C_T, seed=NULL_SEED_16[e])
            g0 = _grade(E, C_T, null0)
            t0 = a0_chi2_tol(C_T)
            rec["A0"] = a0_compare(g0, committed, "cell_flag", g0["cell_flag"], t0["tol"])
            rec["A0"]["b_rule"] = t0
            X_T = cap["X_T"]
            C_add = carry_frac(C_resp, X_T, f) + carry_rel(P_rel, X_T)
            rec["C_PSD"] = check_psd(C_add, f"C_resp+C_PL5D({e})")
            rec["R_chi2"] = r_chi2(E, C_T, C_add)
            null1 = _strict(fn.null_contents, laws, gauss + C_add, C_T + C_add, seed=NULL_SEED_16[e])
            g1 = _grade(E, C_T + C_add, null1)
            rec["descriptive_regrade"] = descriptive(g1)
            rec["sensitivity_absolute_carry"] = {"R_chi2": r_chi2(E, C_T, C_resp + C_PL5D), "read_by": "nothing"}
            rec["status"] = "done"
        except Stop as ex:
            rec["status"], rec["stop"] = "STOP", str(ex)
        out["evaluations"][e] = rec
    return out


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="regrade_crep.py", allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p2 = sub.add_parser("run2d")
    p2.add_argument("--q205", type=Path, required=True)
    p2.add_argument("--out", type=Path, required=True)
    p2.add_argument("--tunes", nargs="+", choices=TUNES_2D, default=list(TUNES_2D))
    p16 = sub.add_parser("run16")
    p16.add_argument("--capture-dir", type=Path, required=True)
    p16.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    if a.cmd == "run2d":
        rec = run2d(a.q205, tuple(a.tunes))
    else:
        man = a.capture_dir / "capture-manifest.json"
        rec = run16(a.capture_dir, json.loads(man.read_text()) if man.exists() else None)
    rec["code_sha256"] = sha256(Path(__file__))
    a.out.write_text(json.dumps(rec, indent=1, default=_json_default) + "\n")
    st = {k: v.get("status") for k, v in rec["evaluations"].items()}
    print(json.dumps(st))
    return 0 if all(s == "done" for s in st.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

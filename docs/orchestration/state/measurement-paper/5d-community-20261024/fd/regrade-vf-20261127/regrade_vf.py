"""REGRADE-VF driver (REGRADE-VF-DECLARATION.md rev 1): the bias and fluctuation split of the sixteen-cell
held-out-tune closures under C_rep with C_e^infl carried to each tune.

Glue only. ``regrade_crep`` (r_chi2, carry_frac, carry_rel, Stop, sha256) and through it ``fd_1b_null.chi2_nonnull``
are imported unchanged. Per evaluation (T, reading) and matrix C = C_T + dF + C_add(T) (declaration sec. 2):
  M', SE, B_raw, tau   = r_chi2(E, C_T + dF, C_add(T))      (tau over C_add only, not dF)
  F                    = tr(A S_1) / ndf, S_1 the draws' covariance with ddof 1
  B                    = B_raw - F / N                      (the debiased bias term; M' = B + F exactly)
  M_full               = M' + tau = B + F + tau
with bootstrap SEs of B, F and B - F (2,000 resamples, A held fixed), and the declaration's sec. 4 classes.

  python3 regrade_vf.py --out <record.json>     (refused if it exists; prints only each evaluation's status)

MEASURES: the declaration's split and readings. CANNOT AUTHORIZE: any change to a reported covariance, any wording, a
coverage or calibration statement, a validated size of C_e^infl or C_rep, a cause, or a p-value.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ["REGRADE_VF_REPO"]) if os.environ.get("REGRADE_VF_REPO") else HERE.parents[6]
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
STATE = REPO / "docs/orchestration/state"
RC_DIR = FD / "regrade-crep-20261121"
RC_SHA256 = "479e03cc51d7be8f0c275c98305b2ab731b135093afacb74f98417529c84d9ad"
if hashlib.sha256((RC_DIR / "regrade_crep.py").read_bytes()).hexdigest() != RC_SHA256:   # C-PIN before the import
    raise SystemExit(f"C-PIN: {RC_DIR / 'regrade_crep.py'} is not {RC_SHA256}; refusing to import it")
if str(RC_DIR) not in sys.path:
    sys.path.insert(0, str(RC_DIR))
import regrade_crep as rc  # noqa: E402

fn = rc.fn
Stop = rc.Stop

CAP = RC_DIR / "run16/capture"
PINS = {   # declaration sec. 1
    "capture_g18_minus2": (CAP / "capture_g18_minus2.npz",
                           "2fae21c50ea983395216f1781f64ead974ebc4dee5b0957bca5f6079a9cd1f8b"),
    "capture_g18_all": (CAP / "capture_g18_all.npz",
                        "29a9f1d5842924008574bc55d425d12c6f71a0cd901d516f505cb1154c11bfb8"),
    "capture_ar23_minus2": (CAP / "capture_ar23_minus2.npz",
                            "7212996c87cd3526764f7d38779e8d36b4daa0fa5099f50a34d9800ede18a9c2"),
    "capture_ar23_all": (CAP / "capture_ar23_all.npz",
                         "97b3d915f40a27026c9cc71bec5fc01fdaf0b9e067016257266dfcfbc5cea313"),
    "regrade16": (CAP / "regrade16.json", "df5905586ef4d05894363ea85557578d65be5164eab327c90303e69a874d8054"),
    "cpl_block": (FD / "with-cpl/block/cpl_block.npz",
                  "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f"),
    "vf_block": (FD / "with-vf/block/vf_block.npz",
                 "cef8460a1dcc0db64f536af0099db1e1523ed2601d5c8ecc682afc0f9440c99b"),
    "blocks5d": (STATE / "ben-b-20261124/blocks5d-20261124/record/blocks5d.json",
                 "c465768b490acc96515c5340585b8ff1f14735254f269af605ffaf182ae521f9"),
    "regrade_crep": (RC_DIR / "regrade_crep.py", RC_SHA256),
}
EVALS = ("g18/minus2", "g18/all", "ar23/minus2", "ar23/all")
PRIMARY = ("g18/minus2", "ar23/minus2")
N_BOOT = 2000
BOOT_SEED = {"g18/minus2": 9_991_271, "g18/all": 9_991_272, "ar23/minus2": 9_991_273, "ar23/all": 9_991_274}
BANDS = (("R1", 0, 4), ("R2", 4, 8), ("R3", 8, 16))   # eigen-rank bands, 0-based [lo, hi)
NDF = 16
K_SE = 3.0
A0_REL = 1e-12
F_REL = 1e-12
DF_REL = 1e-12
L_REL = 1e-10
GAP_MIN = 1e-9
SYM_REL = 1e-12
PSD_REL = 1e-12
ID_REL = 1e-12
A0_FIELDS = ("M_prime", "SE", "mean_error_part", "spread_part", "tau", "M_full")


def pinned(key: str) -> Path:
    path, want = PINS[key]
    got = rc.sha256(path)
    if got != want:
        raise Stop(f"C-PIN: {path.name} is {got}, pinned {want}")
    return path


def within(x: float, tol: float) -> bool:
    """Fail-closed comparison: True only for a finite x at or below tol (NaN and inf fail)."""
    return math.isfinite(x) and x <= tol


def finite(name: str, *arrays) -> None:
    """Every operand non-empty and finite, else a STOP (every control below assumes it)."""
    for a in arrays:
        a = np.asarray(a, np.float64)
        if a.size == 0 or not np.all(np.isfinite(a)):
            raise Stop(f"C-FINITE: {name} is empty or not finite")


def rel_max(a: np.ndarray, b: np.ndarray, scale: float) -> float:
    if not (math.isfinite(scale) and scale > 0):
        raise Stop(f"C-FINITE: a comparison scale is {scale!r}")
    return float(np.max(np.abs(np.asarray(a, np.float64) - np.asarray(b, np.float64))) / scale)


def symmetric(C: np.ndarray, name: str) -> float:
    """Finite and symmetric within SYM_REL (eigh reads one triangle only), else a STOP. Returns the asymmetry."""
    C = np.asarray(C, np.float64)
    finite(name, C)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise Stop(f"C-PSD: {name} is not square: {C.shape}")
    scale = float(np.max(np.abs(C)))
    asym = rel_max(C, C.T, scale)
    if not within(asym, SYM_REL):
        raise Stop(f"C-PSD: {name} asym {asym:.2e}")
    return asym


# ----------------------------------------------------------------------------------- section 2: the matrices
def ranked_eig(C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues and eigenvectors of C by numpy eigh, ranked by descending eigenvalue."""
    lam, U = np.linalg.eigh(np.asarray(C, np.float64))
    order = np.argsort(lam)[::-1]
    return lam[order], U[:, order]


def gap_check(C: np.ndarray, name: str) -> dict:
    """C-GAP: lambda_4/lambda_5 - 1 and lambda_8/lambda_9 - 1 above GAP_MIN, so each band's projector is unambiguous."""
    symmetric(C, name)
    lam, _ = ranked_eig(C)
    if lam.shape != (BANDS[-1][2],) or not all(lam[hi] > 0 for _, _, hi in BANDS[:-1]):
        raise Stop(f"C-GAP: {name} has {lam.shape} eigenvalues or a non-positive one at a band edge")
    gaps = {f"l{hi}/l{hi + 1}-1": float(lam[hi - 1] / lam[hi] - 1.0) for _, _, hi in BANDS[:-1]}
    if not all(math.isfinite(g) and g > GAP_MIN for g in gaps.values()):
        raise Stop(f"C-GAP: {name} {gaps}")
    return gaps


def band_L(C_e: np.ndarray, phi: dict) -> np.ndarray:
    """L = I + sum_R (sqrt(phi_R) - 1) P_R over C_e's own rank bands (B5D-DECLARATION.md sec. 4)."""
    if not all(math.isfinite(phi[name]) and phi[name] >= 1.0 for name, _, _ in BANDS):
        raise Stop(f"C-L: phi must be finite and at least 1: {phi}")
    symmetric(C_e, "C_e for L")
    _, U = ranked_eig(C_e)
    L = np.eye(C_e.shape[0])
    for name, lo, hi in BANDS:
        Ub = U[:, lo:hi]
        L = L + (math.sqrt(phi[name]) - 1.0) * (Ub @ Ub.T)
    return L


def dF_rule_ii(C_eT: np.ndarray, phi: dict) -> np.ndarray:
    """Rule (ii): L_T C_e(T) L_T^T - C_e(T)."""
    L = band_L(C_eT, phi)
    return L @ C_eT @ L.T - C_eT


def check_psd(C: np.ndarray, name: str) -> dict:
    """C-PSD: symmetric within SYM_REL, smallest eigenvalue at least -PSD_REL of the largest."""
    C = np.asarray(C, np.float64)
    asym = symmetric(C, name)
    lam = np.linalg.eigvalsh((C + C.T) / 2)
    if not (math.isfinite(lam.max()) and lam.max() > 0):
        raise Stop(f"C-PSD: {name} largest eigenvalue {lam.max()!r}")
    lmin_rel = float(lam.min() / lam.max())
    if not (math.isfinite(lmin_rel) and lmin_rel >= -PSD_REL):
        raise Stop(f"C-PSD: {name} lam_min/lam_max {lmin_rel:.2e}")
    return {"asym_rel": asym, "lam_min_rel": lmin_rel}


# ----------------------------------------------------------------------------------- section 3: the split
def split(E: np.ndarray, C_base: np.ndarray, C_add: np.ndarray, idx: np.ndarray) -> dict:
    """The declaration's B, F, tau and M_full for C = C_base + C_add, tau over C_add, with bootstrap SEs over idx."""
    E = np.asarray(E, np.float64)
    finite("E", E)
    finite("C", C_base, C_add)
    n = E.shape[0]
    if E.ndim != 2 or n < 2:
        raise Stop(f"C-FINITE: E has shape {E.shape}")
    try:
        r = rc.r_chi2(E, C_base, C_add)
    except ZeroDivisionError as ex:
        raise Stop(f"C-FINITE: r_chi2 divided by zero ({ex})") from ex
    ndf = r["ndf"]
    if ndf != NDF or r["cut"]["C_T_kept_modes_outside_C_prime_kept_span"] != 0:
        raise Stop(f"C-RANK: ndf {ndf}, dropped {r['cut']['C_T_kept_modes_outside_C_prime_kept_span']}")
    Cp = np.asarray(C_base, np.float64) + np.asarray(C_add, np.float64)
    ebar = E.mean(axis=0)
    F = float(fn.chi2_nonnull(E - ebar, Cp)[0].sum() / (n - 1) / ndf)
    B_raw = r["mean_error_part"]
    B = B_raw - F / n
    M = r["M_prime"]
    if not (math.isfinite(M) and M > 0 and within(abs(M - (B + F)), ID_REL * M)):
        raise Stop(f"C-ID: M' {M!r} vs B + F {B + F!r}")
    # bootstrap in the whitened coordinates of chi2_nonnull's factorisation, A held fixed
    lam, V = np.linalg.eigh(Cp)
    keep = lam > fn.RANK_REL * lam.max()
    Z = (E @ V[:, keep]) / np.sqrt(lam[keep])
    Zb = Z[idx]                                    # (n_boot, n, ndf)
    zbar = Zb.mean(axis=1)
    Fb = np.sum((Zb - zbar[:, None, :]) ** 2, axis=(1, 2)) / (n - 1) / ndf
    Bb = np.sum(zbar ** 2, axis=1) / ndf - Fb / n
    se = {"B": float(Bb.std(ddof=1)), "F": float(Fb.std(ddof=1)), "B_minus_F": float((Bb - Fb).std(ddof=1))}
    tau, M_full = r["tau"], r["M_full"]
    vals = [B_raw, B, F, tau, M_full, r["SE"], *se.values()]
    if not (all(math.isfinite(x) for x in vals) and M_full > 0):
        raise Stop(f"C-FINITE: a split quantity is not finite or M_full <= 0: {vals}")
    return {
        "ndf": ndf, "n": n, "M_prime": M, "SE": r["SE"], "B_raw": B_raw, "B": B, "F": F, "tau": tau,
        "M_full": M_full, "shares": {"B": B / M_full, "F": F / M_full, "tau": tau / M_full},
        "se_boot": se, "readings": readings(B, F, M_full, r["SE"], se), "R_chi2_reading_regrade": r["reading"],
    }


# ----------------------------------------------------------------------------------- section 4: the readings
def readings(B: float, F: float, M_full: float, SE: float, se: dict) -> dict:
    d = B - F
    if d > K_SE * se["B_minus_F"]:
        bvf = "bias larger"
    elif -d > K_SE * se["B_minus_F"]:
        bvf = "fluctuation larger"
    else:
        bvf = "not separated"
    return {
        "R_chi2": "under-describes on average" if (M_full - 1.0) > K_SE * SE else "not shown",
        "bias_resolved": "yes" if B > K_SE * se["B"] else "not resolved",
        "bias_vs_fluctuation": bvf,
    }


def carry_sensitive(a: dict, b: dict) -> list[str]:
    return sorted(k for k in a["readings"] if a["readings"][k] != b["readings"][k])


# ----------------------------------------------------------------------------------- the run
def load_capture(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k], np.float64) for k in ("E", "X_T", "f", "C_T", "C_e")}


def block_controls(f_cpl, f_vf, C_e, C_e_infl, DeltaC_e, phi: dict, L5) -> dict:
    """C-F (blocks), C-DF, C-GAP at the data and C-L, on arrays."""
    ctl = {}
    finite("blocks", f_cpl, f_vf, C_e, C_e_infl, DeltaC_e, L5)
    if not np.all(np.asarray(f_cpl) > 0):
        raise Stop("C-F: cpl_block f has a non-positive cell")
    frel = float(np.max(np.abs(np.asarray(f_vf) / np.asarray(f_cpl) - 1.0)))
    if not within(frel, F_REL):
        raise Stop(f"C-F: vf_block f differs from cpl_block f by {frel:.2e}")
    ctl["C_F_blocks"] = frel
    s = float(np.max(np.abs(C_e_infl)))
    d1 = rel_max(DeltaC_e, C_e_infl - C_e, s)
    d2 = rel_max(rc.carry_frac(DeltaC_e, f_cpl, f_cpl), DeltaC_e, s)
    if not (within(d1, DF_REL) and within(d2, DF_REL)):
        raise Stop(f"C-DF: DeltaC_e vs C_e_infl - C_e {d1:.2e}, carry at f {d2:.2e}")
    ctl["C_DF"] = {"DeltaC_e_vs_difference": d1, "carry_at_f": d2}
    ctl["C_GAP_data"] = gap_check(C_e, "vf_block C_e")
    L = band_L(C_e, phi)
    L5 = np.asarray(L5, np.float64)
    l1 = rel_max(L @ C_e @ L.T, C_e_infl, s)
    l2 = rel_max(L, L5, float(np.max(np.abs(L5))))
    if not (within(l1, L_REL) and within(l2, L_REL)):
        raise Stop(f"C-L: builder vs C_e_infl {l1:.2e}, vs blocks5d L {l2:.2e}")
    ctl["C_L"] = {"C_e_infl": l1, "L": l2}
    return ctl


def global_controls() -> tuple[dict, dict]:
    """C-PIN, then block_controls on the pinned blocks. Returns the operands and the control record."""
    for k in PINS:
        pinned(k)
    with np.load(PINS["cpl_block"][0], allow_pickle=False) as z:
        f_cpl, P_rel, C_resp = (np.asarray(z[k], np.float64) for k in ("f", "P_rel", "C_resp"))
    with np.load(PINS["vf_block"][0], allow_pickle=False) as z:
        f_vf, C_e, C_e_infl, DeltaC_e = (np.asarray(z[k], np.float64) for k in ("f", "C_e", "C_e_infl", "DeltaC_e"))
    fl = json.loads(PINS["blocks5d"][0].read_text())["fluctuation"]
    if not all(fl["trigger"][name]["active"] is True for name, _, _ in BANDS):
        raise Stop(f"C-L: a band is not ACTIVE: {fl['trigger']}")
    phi = {name: float(fl["trigger"][name]["phi"]) for name, _, _ in BANDS}
    ctl = block_controls(f_cpl, f_vf, C_e, C_e_infl, DeltaC_e, phi, fl["L"])
    ops = {"f": f_cpl, "P_rel": P_rel, "C_resp": C_resp, "DeltaC_e": DeltaC_e, "phi": phi}
    return ops, ctl


def evaluate(e: str, ops: dict, committed: dict) -> dict:
    truth, reading = e.split("/")
    return evaluate_arrays(e, load_capture(PINS[f"capture_{truth}_{reading}"][0]), ops, committed)


def evaluation_controls(e: str, cap: dict, ops: dict, committed: dict) -> tuple[dict, np.ndarray, dict]:
    """C-F (capture), C-A0, C-GAP at T and C-PSD. Returns the controls, C_add(T) and the two dF(T)."""
    c: dict = {}
    finite(f"capture {e}", *(cap[k] for k in ("E", "X_T", "f", "C_T", "C_e")))
    frel = float(np.max(np.abs(cap["f"] / ops["f"] - 1.0)))
    if not within(frel, F_REL):
        raise Stop(f"C-F: capture f differs from cpl_block f by {frel:.2e}")
    c["C_F_capture"] = frel
    E, X_T, C_T, C_eT = cap["E"], cap["X_T"], cap["C_T"], cap["C_e"]
    C_add = rc.carry_frac(ops["C_resp"], X_T, ops["f"]) + rc.carry_rel(ops["P_rel"], X_T)
    if E.ndim != 2 or E.shape[0] < 2:
        raise Stop(f"C-FINITE: E has shape {E.shape}")
    try:
        r0 = rc.r_chi2(E, C_T, C_add)
    except ZeroDivisionError as ex:
        raise Stop(f"C-FINITE: r_chi2 divided by zero at C-A0 ({ex})") from ex
    if not all(isinstance(committed.get(k), float) and math.isfinite(committed[k]) and committed[k] != 0
               and math.isfinite(r0[k]) for k in A0_FIELDS):
        raise Stop(f"C-A0: a field is missing, zero or not finite: {[(k, committed.get(k), r0[k]) for k in A0_FIELDS]}")
    a0 = {k: abs(r0[k] - committed[k]) / abs(committed[k]) for k in A0_FIELDS}
    if not all(within(x, A0_REL) for x in a0.values()):
        raise Stop(f"C-A0: {a0}")
    c["C_A0"] = a0
    c["C_GAP_T"] = gap_check(C_eT, f"C_e({e})")
    dF = {"rule_i": rc.carry_frac(ops["DeltaC_e"], X_T, ops["f"]), "rule_ii": dF_rule_ii(C_eT, ops["phi"])}
    c["C_PSD"] = {}
    for v, m in dF.items():
        c["C_PSD"][f"dF_{v}"] = check_psd(m, f"dF {v} ({e})")
        c["C_PSD"][f"C_rep_{v}"] = check_psd(C_T + m + C_add, f"C_rep {v} ({e})")
    c["C_PSD"]["C_prime"] = check_psd(C_T + C_add, f"C' ({e})")
    return c, C_add, dF


def evaluate_arrays(e: str, cap: dict, ops: dict, committed: dict) -> dict:
    rec: dict = {}
    rec["controls"], C_add, dF = evaluation_controls(e, cap, ops, committed)
    E, C_T = cap["E"], cap["C_T"]
    idx = np.random.default_rng(BOOT_SEED[e]).integers(0, E.shape[0], size=(N_BOOT, E.shape[0]))
    rec["before"] = split(E, C_T, C_add, idx)
    for v, m in dF.items():
        rec[v] = split(E, C_T + m, C_add, idx)
    rec["carry_sensitive"] = carry_sensitive(rec["rule_i"], rec["rule_ii"])
    rec["status"] = "done"
    return rec


def run() -> dict:
    out = {"schema": "regrade-vf/16/1", "declaration": "REGRADE-VF-DECLARATION.md rev 1", "primary": list(PRIMARY),
           "code_sha256": rc.sha256(Path(__file__).resolve()), "pins": {k: v[1] for k, v in PINS.items()},
           "n_boot": N_BOOT, "boot_seed": BOOT_SEED, "evaluations": {}}
    try:
        ops, out["controls"] = global_controls()
        out["phi"] = ops["phi"]
    except (Stop, OSError, ValueError, KeyError) as ex:
        ex = ex if isinstance(ex, Stop) else Stop(f"{type(ex).__name__}: {ex}")
        out["controls"] = {"stop": str(ex)}
        out["evaluations"] = {e: {"status": "STOP", "stop": str(ex)} for e in EVALS}
        return out
    for e in EVALS:
        try:
            committed = json.loads(PINS["regrade16"][0].read_text())["evaluations"]
            out["evaluations"][e] = evaluate(e, ops, committed[e]["R_chi2"])
        except (Stop, OSError, ValueError, KeyError) as ex:
            out["evaluations"][e] = {"status": "STOP", "stop": str(ex) if isinstance(ex, Stop)
                                     else f"{type(ex).__name__}: {ex}"}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists() or a.out.is_symlink():
        print(f"refused: {a.out} exists", file=sys.stderr)
        return 2
    out = run()
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({e: v["status"] for e, v in out["evaluations"].items()}))
    return 0 if all(v["status"] == "done" for v in out["evaluations"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())

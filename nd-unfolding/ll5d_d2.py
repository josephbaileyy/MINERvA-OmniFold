"""LL5D D2: mu_max of the rebuilt GEANT block against LL5D's ``all`` C_T at one truth (descriptive, no verdict role).

The director's request for Joseph's D2 (2026-11-12), after #1119: there, mu_max, the largest generalized eigenvalue
of the GEANT block G against a covariance M, bounded the two GEANT bands' effect at the data point only
(geant_full.py's scope "not_covered": LL5D's own C_T at G18 and AR23). Here, at truth T:
- G = band:GEANT_Neutron + band:GEANT_Proton, each the mat_cov of its two detector-universe unfolds of d_T;
- M = C_T, LL5D's ``all`` matrix, C_e(T) + C_model_abs(T) (LL5D-DECLARATION.md section 4).
Both come from ``ll5d_b.remade(..., "all")``, LL5D's own construction over the products, imported unchanged. Nothing
in LL5D's verdict path is touched, and this script grades nothing.

For every direction a, (a^T G a) / (a^T M a) <= mu_max, and for every bias vector b,
chi2_(M - G)(b) / chi2_M(b) lies in [1, 1 / (1 - mu_max)]. The record also gives, per eigenmode of M (smallest
variance first), the share v^T G v / lambda, as geant_full.py does.

Run after LL5D's readout at T, against the same products:
- the inputs C_T is built from are pinned: the staged S1 assembly and the flux constraint by sha256 (declared on the
  command line from their committed digests); the null's record by its digest, its verdict PASS, its
  ``products_sha256`` equal to ll5d_b.products_digest over the block roles now, and its ``made_from`` (the definition,
  the cmodel json, U) equal to this run's; the readout's record by its digest and the null it names;
- the control (the director's ruling on the audit's M1, 2026-11-13): from this run's C_T and the same 300 ``all`` toys
  (ll5d_b.toy_errors, then ll5d_b.graded, LL5D's own grading), the readout's recorded quantities are recomputed and
  must agree: the realization_check (C_T's diagonal), kappa_2(C_T) and the grade's chi2 mean and its standard error
  (both through C_T's inverse, so through every off-diagonal) to CONTROL_TOL relative, and the joint and per-cell
  counts exactly. What it establishes: this C_T reproduces every full-matrix statistic the readout recorded for
  ``all``. A different matrix that reproduced all of them is not excluded by construction; none is known.
Reads: the two records through fd_1b_inv.open_noatime; the products' arrays through ll5d_b._x (open_noatime). The one
plain read is ll5d_b.products_digest's (s5n_pseudo.sha256_path), the same call LL5D's own null and readout make to pin
the products; it touches only LL5D's output products, none of its atime-snapshot inputs. Exit 0 the record written;
5 INVALID (a refusal, written as <out>.invalid.json); 8 is or-ed in if an atime moved.
    python3 ll5d_d2.py --staged S --definition D --unfolds U --cmodel-json J --flux-constraint F --truth g18
        --null N --expect-null-sha256 H1 --readout R --expect-readout-sha256 H2 --expect-staged-s1-sha256 H3
        --expect-flux-constraint-sha256 H4 --out OUT.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))

import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import ll5d  # noqa: E402
import ll5d_b  # noqa: E402

SCHEMA = "ll5d-d2/1"
GEANT = ("band:GEANT_Neutron", "band:GEANT_Proton")
CONTROL_TOL = 1e-10          # relative, on each recomputed readout quantity
FULL_FLOATS = ("chi2_mean_over_ndf", "chi2_mean_over_ndf_se")     # the grade's, through C_T^-1
EXACT = ("joint_count", "counts")


class Refusal(RuntimeError):
    """A precondition failed: INVALID, reported unrepaired."""


def gen_eig(G: np.ndarray, M: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Generalized eigenvalues and M-normalized directions of (G, M), largest first (geant_full.py:40-47, #1119)."""
    L = np.linalg.cholesky(M)
    Li = np.linalg.inv(L)
    w, V = np.linalg.eigh(Li @ G @ Li.T)
    order = np.argsort(w)[::-1]
    return w[order], (Li.T @ V)[:, order]


def mode_shares(G: np.ndarray, M: np.ndarray) -> list[dict]:
    lam, V = np.linalg.eigh(M)
    return [{"k": int(k), "lambda": float(lam[k]), "share": float(V[:, k] @ G @ V[:, k] / lam[k])}
            for k in range(len(lam))]


def summarize(G: np.ndarray, M: np.ndarray, cells: list[str]) -> dict:
    """geant_full.summarize's fields, plus a self-check that the top direction attains mu_max."""
    mu, A = gen_eig(G, M)
    a0 = A[:, 0]
    attained = float(a0 @ G @ a0 / (a0 @ M @ a0))
    if not abs(attained - mu[0]) <= 1e-9 * max(abs(mu[0]), 1e-300):
        raise Refusal(f"the top direction gives {attained}, not mu_max {mu[0]}")
    a = a0 / np.max(np.abs(a0))
    ms = mode_shares(G, M)
    return {"mu_max": float(mu[0]), "mu_top3": [float(x) for x in mu[:3]],
            "chi2_ratio_bound": float(1 / (1 - mu[0])),
            "mu_max_direction_cells": {cells[i]: round(float(a[i]), 4) for i in np.argsort(-np.abs(a))[:5]},
            "eigenmode_shares_smallest_first": ms,
            "max_eigenmode_share": max(m["share"] for m in ms),
            "smallest4_eigenmode_shares": [m["share"] for m in ms[:4]]}


def read_record(path: Path, want_sha256: str, what: str) -> dict:
    if inv.sha256_noatime(path) != want_sha256:
        raise Refusal(f"the {what}'s digest differs from the declared one")
    with inv.open_noatime(path) as fh:
        return json.loads(fh.read().decode())


def _rel(got, want) -> float:
    got, want = np.asarray(got, float), np.asarray(want, float)
    if got.shape != want.shape:
        raise Refusal(f"a recomputed quantity has shape {got.shape}, the readout's {want.shape}")
    return float(np.max(np.abs(got - want) / np.maximum(np.abs(want), 1e-300)))


def control(readout: dict, truth: str, rm: dict, x_hat: np.ndarray, x_true: np.ndarray, g: dict | None,
            chk: dict) -> dict:
    """The readout's ``all`` evaluation recomputed from this run's C_T and the same toys (``g``, ``chk`` from
    ll5d_b.graded): the diagonal (realization_check), kappa_2, the chi2 mean and its se to CONTROL_TOL, the counts
    exactly."""
    ev = (readout.get("evaluations") or {}).get(f"{truth}/all") or {}
    want = ((ev.get("readouts") or {}).get("realization_check") or {}).get("per_cell_sigma")
    if want is None:
        raise Refusal(f"the readout's {truth}/all evaluation has no realization_check (verdict {ev.get('verdict')})")
    grade_rec, chk_rec = ev.get("grade"), ev.get("cholesky_check")
    if not grade_rec or not chk_rec:
        raise Refusal(f"the readout's {truth}/all evaluation has no grade or cholesky_check")
    rel = {"realization_check": _rel((x_hat - x_true) / np.sqrt(np.diag(rm["C_T"])), want),
           "cholesky_check.kappa2": _rel(chk["kappa2"], chk_rec["kappa2"])}
    exact = {}
    if g is None:
        why = "the grade refused under this C_T, where the readout graded"
    else:
        rel.update({f"grade.{k}": _rel(g[k], grade_rec[k]) for k in FULL_FLOATS})
        exact = {f"grade.{k}": g[k] == grade_rec[k] for k in EXACT}
        why = ""
    passes = g is not None and all(v <= CONTROL_TOL for v in rel.values()) and all(exact.values())
    return {"what": "the readout's all evaluation recomputed from this C_T and the same toys", "max_rel_diff": rel,
            "exact": exact, "tol": CONTROL_TOL, "passes": bool(passes), **({"why": why} if why else {})}


def d2(a) -> dict:
    nl = read_record(a.null, a.expect_null_sha256, "null")
    if nl.get("verdict") != "PASS" or nl.get("truth") != a.truth:
        raise Refusal("the null is not a PASS at this truth")
    if nl.get("products_sha256") != ll5d_b.products_digest(a.unfolds, a.truth, ll5d_b.BLOCK_ROLES):
        raise Refusal("the null was not made from these products")
    ro = read_record(a.readout, a.expect_readout_sha256, "readout")
    if ro.get("truth") != a.truth or ro.get("null_sha256") != a.expect_null_sha256:
        raise Refusal("the readout is not this truth's, or was not made with this null")
    for path, want, what in ((a.staged / "s1" / "s1_assembly.npz", a.expect_staged_s1_sha256, "staged S1 assembly"),
                             (a.flux_constraint, a.expect_flux_constraint_sha256, "flux constraint")):
        if inv.sha256_noatime(path) != want:
            raise Refusal(f"the {what}'s digest differs from the declared one")
    s1, U, frac, _minus, w = ll5d_b.setup(a)
    if nl.get("made_from") != mc.made_from(a, U):
        raise Refusal("the definition, the cmodel json or U is not the one the null was made from")
    rm = ll5d_b.remade(a.unfolds, a.truth, s1, U, w, frac, "all")
    x_hat = U @ ll5d_b._x(a.unfolds, a.truth, "central", "T")
    x_true = U @ ll5d_b._x(a.unfolds, a.truth, "central", "T", "xtrue_flat")
    E, _draws, _X_true, _nat = ll5d_b.toy_errors(a.unfolds, a.truth, "all", U, rm, s1["f"])
    g, chk, _rule = ll5d_b.graded(E, rm["C_T"], mc._null_dict(nl[f"{a.truth}/all"]["C_T"]))
    ctl = control(ro, a.truth, rm, x_hat, x_true, g, chk)
    out = {"schema": SCHEMA, "step": "d2", "truth": a.truth, "reading": "all", "verdict_role": "none (descriptive)",
           "null_sha256": a.expect_null_sha256, "readout_sha256": a.expect_readout_sha256,
           "products_sha256": nl["products_sha256"], "control": ctl}
    if not ctl["passes"]:
        out["verdict"] = "INVALID"
        return out
    G = sum(rm["blocks"][k] for k in GEANT)
    M = rm["C_T"]
    cells = [f"R{c:02d}" for c in range(M.shape[0])]
    out["G_offdiagonal_abs_share"] = float(np.sum(np.abs(G - np.diag(np.diag(G)))) / np.sum(np.abs(G)))
    out["C_T_all"] = summarize(G, M, cells)
    out["verdict"] = "PASS"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("staged", "definition", "unfolds", "cmodel-json", "flux-constraint", "null", "readout", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    ap.add_argument("--truth", choices=ll5d_b.TRUTHS, required=True)
    ap.add_argument("--expect-null-sha256", required=True)
    ap.add_argument("--expect-readout-sha256", required=True)
    ap.add_argument("--expect-staged-s1-sha256", required=True)
    ap.add_argument("--expect-flux-constraint-sha256", required=True)
    a = ap.parse_args(argv)
    if a.out.exists() or a.out.with_suffix(".invalid.json").exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    inv.OPENED.clear()
    try:
        rec = d2(a)
    except (Refusal, ll5d_b.Refusal, ll5d.Refusal, mc.Refusal, inv.Refusal) as exc:
        bad = {"schema": SCHEMA, "step": "d2", "verdict": "INVALID", "why": str(exc), "atime": inv.atime_check()}
        a.out.with_suffix(".invalid.json").write_text(json.dumps(bad, indent=1, sort_keys=True))
        print(f"LL5D-D2 INVALID ({exc})")
        return 5 | (ll5d.ATIME_RC if bad["atime"]["moved"] else 0)
    rec["atime"] = inv.atime_check()
    target = a.out if rec["verdict"] == "PASS" else a.out.with_suffix(".invalid.json")
    target.write_text(json.dumps(rec, indent=1, sort_keys=True))
    s = rec.get("C_T_all", {})
    print(f"LL5D-D2 {a.truth} verdict={rec['verdict']} mu_max={s.get('mu_max')} "
          f"chi2_ratio_bound={s.get('chi2_ratio_bound')} control_passes={rec['control']['passes']}")
    rc = 0 if rec["verdict"] == "PASS" else 5
    return rc | (ll5d.ATIME_RC if rec["atime"]["moved"] else 0)


if __name__ == "__main__":
    sys.exit(main())

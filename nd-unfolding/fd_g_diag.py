#!/usr/bin/env python3
"""5D Stage G-DIAG (state/measurement-paper/5d-community-20261024/FD-G-DIAG-DECLARATION.md): a descriptive breakdown
of Stage G's existing total chi2 for each prediction, under the reported matrix C_total + C_x + V_g and the variant
C_total + V_g, from the same pinned inputs as Stage G. It adds no statistic: its chi2 is Stage G's, checked against
the committed Stage G readout at run time (controls D5 and D7), and everything else is labelled descriptive.

Each comparison is broken down twice, in two units whose per-mode pictures differ (the total chi2 does not):
* relative to f: d = (f - g)/f, M = (C + V_g)/(f f^T), so sqrt(lambda) is a relative sigma;
* absolute: d = f - g, M = C + V_g, the director's (v^T (f - g))^2 / lambda literally.
With M = sum_i lambda_i v_i v_i^T (lambda descending, each v_i signed so its largest-|loading| cell is positive):

1. the spectrum: lambda_i, sqrt(lambda_i) and M's condition number;
2. the chi2 by mode, c_i = (v_i^T d)^2 / lambda_i, sorted descending, and the fewest modes carrying 50, 90 and 99 %;
3. for the TOP modes with the largest c_i: the loadings, sqrt(lambda), and each block's share v_i^T B v_i / lambda_i,
   where the blocks partition M exactly (control D6): S1's seven C_e groups (s1_assemble.group_of), the three
   C_model,5D vertices s_j s_j^T, C_x where the comparison carries it, and V_g;
4. the chi2 with each block removed in turn, with the condition number of what is left (descriptive);
5. stability: the chi2 by Cholesky, by the mode sum and by least squares in float64, and against a ridge
   M + RIDGE * mean(diag M) * I. `ridge_sensitive` if the ridge moves chi2 by more than UNSTABLE relative;
   `methods_disagree` if the three float64 methods differ by more than METHODS; `unstable` if either holds or
   Cholesky fails.

Controls D0-D7 each refuse (exit 1, nothing written). Non-finite numbers are written as null and counted.

MEASURES: arithmetic on Stage G's declared inputs. CANNOT AUTHORIZE: any reading of the comparison, a claim, or paper
text.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_g_compare as G  # noqa: E402  (PINS, PREDICTIONS, GIBUU_CELLS, compare, chi2_sf, prediction_problems)
import s1_assemble as sa  # noqa: E402  (sha256, fine_map, functional_matrix, load_manifest, group_of)

N_FINE, N_CELLS, TOL = G.N_FINE, G.N_CELLS, G.TOL
VERTICES = ("genie_mec", "nuwro", "gibuu")
GROUPS = ("stat", "interaction", "flux", "detector", "lateral", "normalization", "seed")
UNITS = ("relative_to_f", "absolute")
FRACTIONS = (0.5, 0.9, 0.99)
TOP = 3
RIDGE = 1.0e-10                   # the director's 1e-10, times the mean diagonal of M in the breakdown's units
UNSTABLE = 1.0e-3                 # ridge_sensitive above this relative chi2 change
METHODS = 1.0e-8                  # methods_disagree above this relative spread of Cholesky, mode sum and lstsq
ILL = 1.0e12                      # a block-removed matrix with a condition number above this is ill_conditioned
REPRO = 1.0e-10                   # D5 and D7: Stage G's numbers reproduced to this relative tolerance
PINS = {**G.PINS, "g_readout": "75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee"}
LABELS = {
    "what": "a descriptive breakdown of Stage G's total chi2 (FD-G-DIAG-DECLARATION.md); no new statistic",
    "units": "relative_to_f: d = (f - g)/f, M = (C + V_g)/(f f^T); absolute: d = f - g, M = C + V_g. The total chi2 is "
             "the same in both; the eigenmodes, per-mode chi2, mode counts and shares are not",
    "modes": "eigenmodes of M, lambda descending; each eigenvector signed so its largest-|loading| cell is positive",
    "shares": "block share of a mode = v^T B v / lambda; the blocks partition M (control D6), so the shares sum to 1",
    "removed": "descriptive: the chi2 with one block removed from M; a breakdown, not an alternative result",
    "stability": f"chi2 by Cholesky, mode sum, least squares, and with a ridge {RIDGE:g} * mean(diag M) * I; "
                 f"ridge_sensitive above {UNSTABLE:g}, methods_disagree above {METHODS:g}; unstable if either or if "
                 "Cholesky fails",
    "not": "no reading, claim or paper text",
}


def report(control, name, ok, why="differs"):
    G.report(control, name, ok, why)


# ---------------------------------------------------------------- the breakdown (pure functions)


def eigen(M: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues descending, eigenvectors as columns, each signed so its largest-|loading| entry is positive."""
    lam, V = np.linalg.eigh((M + M.T) / 2)
    order = np.argsort(lam)[::-1]
    lam, V = lam[order], V[:, order]
    sign = np.sign(V[np.argmax(np.abs(V), axis=0), np.arange(V.shape[1])])
    return lam, V * np.where(sign == 0, 1.0, sign)


def modes_needed(fractions_sorted: np.ndarray) -> dict:
    """The fewest leading modes (in chi2 order) whose cumulative fraction reaches each of FRACTIONS; None if the
    fractions are not finite."""
    if not np.all(np.isfinite(fractions_sorted)):
        return {f"{int(round(100 * q))}%": None for q in FRACTIONS}
    cum = np.cumsum(fractions_sorted)
    return {f"{int(round(100 * q))}%": int(np.searchsorted(cum, q - 1e-12) + 1) for q in FRACTIONS}


def chol_chi2(M: np.ndarray, d: np.ndarray) -> float | None:
    """d^T M^-1 d by Cholesky, or None if M is not numerically positive definite."""
    try:
        L = np.linalg.cholesky(M)
    except np.linalg.LinAlgError:
        return None
    y = np.linalg.solve(L, d)
    return float(y @ y)


def condition(M: np.ndarray) -> float:
    ev = np.linalg.eigvalsh((M + M.T) / 2)
    return float(ev.max() / ev.min()) if ev.min() > 0 else float("inf")


def chi2_ways(M: np.ndarray, d: np.ndarray, lam: np.ndarray, V: np.ndarray) -> dict:
    """Item 5: the chi2 four ways in float64, and the three flags."""
    chol = chol_chi2(M, d)
    eig = float(np.sum((V.T @ d) ** 2 / lam)) if np.all(lam > 0) else None
    lsq = float(d @ np.linalg.lstsq(M, d, rcond=None)[0])
    eps = RIDGE * float(np.mean(np.diag(M)))
    ridge = chol_chi2(M + eps * np.eye(len(d)), d)

    def rel(x):
        return None if x is None or not chol else abs(x - chol) / abs(chol)
    r, re, rl = rel(ridge), rel(eig), rel(lsq)
    ridge_sensitive = bool(r is None or r > UNSTABLE)
    disagree = bool(re is None or rl is None or max(re, rl) > METHODS)
    return {"chi2_cholesky": chol, "chi2_mode_sum": eig, "chi2_lstsq": lsq, "chi2_ridge": ridge, "ridge": eps,
            "rel_mode_sum_vs_cholesky": re, "rel_lstsq_vs_cholesky": rl, "rel_ridge_vs_cholesky": r,
            "ridge_sensitive": ridge_sensitive, "methods_disagree": disagree,
            "unstable": bool(chol is None or ridge_sensitive or disagree)}


def mode_chi2(lam: np.ndarray, V: np.ndarray, d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Item 2: the projections v_i^T d and the per-mode chi2 (v_i^T d)^2 / lambda_i (inf where lambda_i <= 0)."""
    proj = V.T @ d
    with np.errstate(divide="ignore", invalid="ignore"):
        return proj, np.where(lam > 0, proj ** 2 / np.where(lam > 0, lam, 1.0), np.inf)


def block_shares(v: np.ndarray, lam_i: float, blocks: dict[str, np.ndarray]) -> dict[str, float]:
    """Item 3: each block's share v^T B v / lambda of one mode."""
    return {name: float(v @ B @ v / lam_i) for name, B in blocks.items()}


def removed_chi2(M: np.ndarray, B: np.ndarray, d: np.ndarray) -> float | None:
    """Item 4: the chi2 against M with block B removed, or None if that is not positive definite."""
    return chol_chi2(M - B, d)


def comparison_blocks(groups: dict, S: np.ndarray, Cx, Vg: np.ndarray, i: np.ndarray, xname: str,
                      scale: np.ndarray) -> dict:
    """The blocks of one comparison's M on cells i, in the units of `scale` (f for absolute, ones for relative):
    S1's seven groups, the three C_model vertices (S is relative to f), the extra block (if this comparison carries it,
    else None) and V_g. groups, Cx and Vg are relative to f."""
    ss = np.outer(scale[i], scale[i])
    B = {g: groups[g][np.ix_(i, i)] * ss for g in GROUPS}
    B.update({f"C_model:{v}": np.outer(S[j][i], S[j][i]) * ss for j, v in enumerate(VERTICES)})
    if Cx is not None:
        B[xname] = Cx[np.ix_(i, i)] * ss
    B["V_g"] = np.diag(Vg[i] * scale[i] ** 2)
    return B


def residual(f: np.ndarray, g: np.ndarray, i: np.ndarray, scale: np.ndarray) -> np.ndarray:
    """d on cells i, in the units of `scale`: (f - g)/f * scale."""
    return ((f - g) / f * scale)[i]


def breakdown(d: np.ndarray, blocks: dict[str, np.ndarray], cells: list[str]) -> dict:
    """Items 1-5 for one comparison in one unit system."""
    M = sum(blocks.values())
    n = len(d)
    lam, V = eigen(M)
    proj, c = mode_chi2(lam, V, d)
    total = float(np.sum(c))                   # the mode sum; the fractions below are of it
    order = np.argsort(c)[::-1]
    with np.errstate(invalid="ignore"):
        frac = c[order] / total
    modes = [{"mode": int(i), "lambda": float(lam[i]), "sigma": float(np.sqrt(max(lam[i], 0.0))),
              "projection": float(proj[i]), "chi2": float(c[i]), "fraction": float(frac[k]),
              "cumulative": float(np.sum(frac[:k + 1]))} for k, i in enumerate(order)]
    top = []
    for k, i in enumerate(order[:TOP]):
        v = V[:, i]
        shares = block_shares(v, lam[i], blocks)
        top.append({"mode": int(i), "sigma": float(np.sqrt(max(lam[i], 0.0))), "chi2": float(c[i]),
                    "fraction": float(frac[k]), "loadings": dict(zip(cells, v.tolist())),
                    "block_shares": shares, "share_sum": float(sum(shares.values())),
                    "dominant": max(shares, key=lambda b: shares[b])})
    removed = []
    for name, B in blocks.items():
        x2 = removed_chi2(M, B, d)
        cond = condition(M - B)
        removed.append({"removed": name, "positive_definite": x2 is not None, "chi2": x2, "ndf": n,
                        "p": None if x2 is None else G.chi2_sf(x2, n), "condition": cond,
                        "ill_conditioned": bool(not cond < ILL),
                        "label": "descriptive breakdown, not an alternative result" if x2 is not None else
                                 "descriptive; M without this block is not positive definite"})
    stab = chi2_ways(M, d, lam, V)
    return {"chi2": stab["chi2_cholesky"], "chi2_mode_sum": total, "ndf": n,
            "eigen": {"lambda": lam.tolist(), "sigma": np.sqrt(np.clip(lam, 0, None)).tolist(),
                      "condition": condition(M), "rank": G.rank(M)},
            "modes_by_chi2": modes, "modes_needed": modes_needed(frac), "top_modes": top,
            "removed": removed, "stability": stab}


def finite(obj, counter: list):
    """A copy of obj with every non-finite float replaced by None; counter[0] counts the replacements."""
    if isinstance(obj, dict):
        return {k: finite(v, counter) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [finite(v, counter) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        counter[0] += 1
        return None
    return obj


def summary_line(name: str, c: dict) -> str:
    r, ab = c["relative_to_f"], c["absolute"]
    t = r["top_modes"][0]
    x2 = "not positive definite" if r["chi2"] is None else f"{r['chi2']:.2f}"
    rr = r["stability"]["rel_ridge_vs_cholesky"]
    flags = [k for k in ("ridge_sensitive", "methods_disagree") if r["stability"][k] or ab["stability"][k]]
    return (f"[G-DIAG] {name:10s} {c['comparison']:8s} [{c['matrix']}, {c['ndf']}x{c['ndf']}]: chi2 {x2}; "
            f"relative units: cond {r['eigen']['condition']:.3g}, modes for 50/90/99 % "
            f"{r['modes_needed']['50%']}/{r['modes_needed']['90%']}/{r['modes_needed']['99%']}, top mode {t['mode']} "
            f"carries {100 * t['fraction']:.1f} %, sigma {100 * t['sigma']:.2f} %, dominant {t['dominant']}; "
            f"absolute units: modes for 90 % {ab['modes_needed']['90%']}, top dominant {ab['top_modes'][0]['dominant']}"
            f"; ridge change {'none' if rr is None else format(rr, '.1e')}"
            + (f" UNSTABLE ({', '.join(flags)})" if (r["stability"]["unstable"] or ab["stability"]["unstable"]) else ""))


# ---------------------------------------------------------------- main


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k, h in (("--definition", "nd-unfolding/pv-ladder/readouts/h2_definition.json"),
                 ("--s1-npz", "s1-20261024/s1_assembly.npz"), ("--s1-json", "the committed s1_assembly.json"),
                 ("--cmodel-json", "nd-unfolding/pv-ladder/readouts/cmodel_5d.json"),
                 ("--s5p-sums", "state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"),
                 ("--s5p-root", "s5p-20260926"), ("--g-readout", "the committed fd/readout/fd_g_readout.json"),
                 ("--extra-block", "Stage G's extra block npz"), ("--out-json", "")):
        ap.add_argument(k, type=Path, required=True, help=h or None)
    ap.add_argument("--extra-block-sha256", required=True)
    ap.add_argument("--extra-block-key", required=True)
    ap.add_argument("--extra-block-name", required=True)
    ap.add_argument("--extra-block-role", choices=G.ROLES, required=True)
    return ap.parse_args(argv)


def run(a, pins=None, predictions=None) -> int:
    pins = PINS if pins is None else pins
    predictions = G.PREDICTIONS if predictions is None else predictions
    if a.out_json.exists():
        raise G.Stop("-", f"refusing to overwrite {a.out_json}")

    # D0. digests: G0's, the extra block's, and the committed Stage G readout's
    for key, path in (("s1_json", a.s1_json), ("cmodel_json", a.cmodel_json), ("s5p_sums", a.s5p_sums),
                      ("s1_npz", a.s1_npz), ("g_readout", a.g_readout)):
        if sa.sha256(path) != pins[key]:
            raise G.Stop("D0", f"{key} {path}: sha256 {sa.sha256(path)} != {pins[key]}")
    if sa.sha256(a.extra_block) != a.extra_block_sha256:
        raise G.Stop("D0", f"extra block {a.extra_block}: sha256 {sa.sha256(a.extra_block)} != {a.extra_block_sha256}")
    s1j, cj, gr = (json.loads(p.read_text()) for p in (a.s1_json, a.cmodel_json, a.g_readout))
    if s1j.get("assembly_sha256") != pins["s1_npz"]:
        raise G.Stop("D0", "the committed S1 readout names another assembly")
    U = sa.functional_matrix(G.sa_call("D0", sa.fine_map, a.definition))
    sums = sa.load_manifest(a.s5p_sums)
    for spec in predictions:
        got = sa.sha256(a.s5p_root / spec["path"])
        if got != spec["sha256"] or sums.get(spec["path"]) != spec["sha256"]:
            raise G.Stop("D0", f"{spec['name']}: sha256 {got}, pinned {spec['sha256']}, manifest {sums.get(spec['path'])}")
    report("D0", f"S1, definition, 3 records, the Stage G readout, the extra block and {len(predictions)} predictions "
                 "match their digests", True)

    # D1. prediction structure (G1)
    for spec in predictions:
        bad = G.prediction_problems(a.s5p_root / spec["path"], spec)
        if bad:
            raise G.Stop("D1", f"{spec['name']}: {'; '.join(bad)}")
    report("D1", "every prediction carries xsec, sumw2 and nevt on the fine grid, finite, sumw2 >= 0, as named", True)

    # D2. S1, its blocks, C_model's vertices and the extra block
    with np.load(a.s1_npz, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        f = np.asarray(z["f"], float)
        Ce, Ct, Cmf, Cma = (np.asarray(z[k], float) for k in ("C_e", "C_total", "C_model_frac", "C_model_abs"))
        U32 = np.asarray(z["U"])
        names = list(meta.get("blocks") or [])
        missing = [b for b in names if "C_" + b.replace(":", "_") not in z.files]
        blocks_abs = {} if missing else {b: np.asarray(z["C_" + b.replace(":", "_")], float) for b in names}
    with np.load(a.extra_block, allow_pickle=False) as z:
        if a.extra_block_key not in z.files:
            raise G.Stop("D2", f"the extra block has no key {a.extra_block_key!r}")
        Cx = np.asarray(z[a.extra_block_key], float)
    ff = np.outer(f, f)
    S = np.asarray(cj.get("S"), float)
    scale = np.abs(np.diag(Ct)).max()
    groups = {g: np.zeros((N_CELLS, N_CELLS)) for g in GROUPS}
    unknown = sorted({sa.group_of(b) for b in blocks_abs} - set(GROUPS))
    for b, B in blocks_abs.items():
        if sa.group_of(b) in groups:
            groups[sa.group_of(b)] += B
    xn = a.extra_block_name
    checks = {
        "S1's blocks are all present": bool(names) and not missing,
        "every block maps to one of S1's seven groups": not unknown,
        "U is S1's float32 functional matrix": np.array_equal(U32, U.astype(np.float32)),
        "f is positive on every cell": bool(f.shape == (N_CELLS,) and np.all(f > 0)),
        "f is cmodel_5d.json's x (to 1e-12)": np.allclose(f, np.asarray(cj["x"], float), rtol=TOL, atol=0),
        "C_e is the sum of S1's blocks": bool(blocks_abs) and np.allclose(sum(blocks_abs.values()), Ce, rtol=TOL,
                                                                           atol=TOL * scale),
        "C_total = C_e + C_model_abs": np.allclose(Ce + Cma, Ct, rtol=TOL, atol=TOL * scale),
        "C_model's vertices are GENIE+MEC, NuWro, GiBUU": tuple(cj.get("vertices", ())) == VERTICES,
        "C_model = S^T S, S from cmodel_5d.json": S.shape == (3, N_CELLS) and np.allclose(
            S.T @ S, Cmf, rtol=TOL, atol=TOL * np.abs(np.diag(Cmf)).max()),
        "C_model_abs = diag(f) C_model diag(f)": np.allclose(Cmf * ff, Cma, rtol=TOL, atol=TOL * scale),
        "C_total's relative sigma is the committed one": np.allclose(
            np.sqrt(np.diag(Ct)) / f, np.asarray(s1j["relative_sigma"]["C_total"], float), rtol=TOL, atol=0),
        f"{xn} is a finite 16 x 16 matrix": Cx.shape == (N_CELLS, N_CELLS) and bool(np.all(np.isfinite(Cx))),
    }
    for name, ok in checks.items():
        report("D2", name, bool(ok))
    Cx_rel = Cx / ff
    groups_rel = {g_: groups[g_] / ff for g_ in GROUPS}
    checks = {f"{xn} is symmetric": np.allclose(Cx, Cx.T, rtol=TOL, atol=TOL * np.abs(Cx).max()),
              f"{xn} is positive semidefinite": bool(np.linalg.eigvalsh((Cx_rel + Cx_rel.T) / 2).min()
                                                    >= -TOL * max(np.abs(Cx_rel).max(), 1e-300))}
    for name, ok in checks.items():
        report("D2", name, bool(ok))

    # D3. GiBUU's cells (G3)
    defn = json.loads(a.definition.read_text())
    lo = sorted(c["id"] for c in defn["reporting_cells"] if c["box"]["pz"][1] <= 4.5)
    report("D3", "GiBUU's eight cells are the p_parallel < 4.5 boxes", lo == list(G.GIBUU_CELLS), f"they are {lo}")

    # D4. integrals on each prediction's own cells only (G4)
    integ = {}
    for spec in predictions:
        cells = list(range(N_CELLS)) if spec["cells"] == "all" else list(G.GIBUU_CELLS)
        Uc = U[cells]
        with np.load(a.s5p_root / spec["path"], allow_pickle=False) as z:
            x, s2 = (np.asarray(z[k], float) for k in ("xsec_flat", "sumw2_flat"))
        g, Vg = np.zeros(N_CELLS), np.zeros(N_CELLS)
        g[cells], Vg[cells] = Uc @ x, (Uc ** 2) @ s2
        if not (np.all(g[cells] > 0) and np.all(Vg[cells] >= 0)):
            raise G.Stop("D4", f"{spec['name']}: a cell integral is not positive or V_g is negative")
        integ[spec["name"]] = (cells, g, Vg)
    report("D4", "every prediction's integrals are positive on its cells", True)

    # the two comparisons, by Stage G's role: (key, matrix name, whether it carries C_x)
    with_x, without = (f"C_total + {xn}", True), ("C_total", False)
    comps = [("reported", with_x), ("variant", without)] if a.extra_block_role == "adopted" else \
            [("reported", without), ("variant", with_x)]

    # D5. Stage G reproduced: its argv's extra block, and every total and shape-only chi2 and pull, to REPRO
    gargs = gr.get("argv", [])

    def garg(k):
        return gargs[gargs.index(k) + 1] if k in gargs else None
    same = {"schema fd-g-readout/2": gr.get("schema") == "fd-g-readout/2",
            "extra-block sha256": garg("--extra-block-sha256") == a.extra_block_sha256,
            "extra-block key": garg("--extra-block-key") == a.extra_block_key,
            "extra-block name": garg("--extra-block-name") == xn,
            "extra-block role": garg("--extra-block-role") == a.extra_block_role}
    report("D5", "the Stage G readout used this extra block, key, name and role", all(same.values()),
           "differs in " + ", ".join(k for k, v in same.items() if not v))
    grp = {p["name"]: p for p in gr["predictions"]}
    worst = 0.0
    for spec in predictions:
        cells, g, Vg = integ[spec["name"]]
        rec = grp.get(spec["name"])
        if rec is None or rec["cells"] != [f"R{c:02d}" for c in cells]:
            raise G.Stop("D5", f"{spec['name']}: the Stage G readout has another cell set")
        for key, (mname, carries) in comps:
            mine = G.compare(f, g, Vg, Ct + (Cx if carries else 0), cells, mname)
            theirs = rec if key == "reported" else rec["variant"]
            for k in ("total", "shape_only"):
                worst = max(worst, abs(mine[k]["chi2"] - theirs[k]["chi2"]) / abs(theirs[k]["chi2"]))
            worst = max(worst, float(np.max(np.abs(np.asarray(mine["pulls"]) - theirs["pulls"])
                                            / np.maximum(np.abs(theirs["pulls"]), 1e-300))))
    report("D5", f"Stage G's total and shape-only chi2 and pulls reproduce to {REPRO:g} relative (worst {worst:.1e})",
           worst <= REPRO, f"worst relative difference {worst:.3e}")

    # the breakdowns; D6: the blocks rebuild each comparison's M; D7: each breakdown's chi2 is Stage G's
    results, worst6, worst7 = [], 0.0, 0.0
    ones = np.ones(N_CELLS)
    for spec in predictions:
        cells, g, Vg = integ[spec["name"]]
        i = np.asarray(cells)
        rec = {"name": spec["name"], "label": spec["label"], "cells": [f"R{c:02d}" for c in cells], "comparisons": []}
        theirs_all = grp[spec["name"]]
        for key, (mname, carries) in comps:
            theirs = (theirs_all if key == "reported" else theirs_all["variant"])["total"]["chi2"]
            Mabs = (Ct + (Cx if carries else 0))[np.ix_(i, i)] + np.diag(Vg[i])
            comp = {"comparison": key, "matrix": f"{mname} + V_g", "ndf": len(cells), "chi2_stage_g": theirs}
            for units, sc in (("relative_to_f", ones), ("absolute", f)):
                B = comparison_blocks(groups_rel, S, Cx_rel if carries else None, Vg / f ** 2, i, xn, sc)
                Mu = Mabs / np.outer(f[i], f[i]) * np.outer(sc[i], sc[i])
                worst6 = max(worst6, float(np.abs(sum(B.values()) - Mu).max() / np.abs(Mu).max()))
                bd = breakdown(residual(f, g, i, sc), B, rec["cells"])
                if not bd["stability"]["unstable"]:
                    worst7 = max(worst7, abs(bd["chi2"] - theirs) / abs(theirs))
                comp[units] = bd
            rec["comparisons"].append(comp)
        results.append(rec)
    report("D6", f"the blocks rebuild every comparison's M to 1e-12 relative in both units (worst {worst6:.1e})",
           worst6 <= TOL, f"worst {worst6:.3e}")
    report("D7", f"every stable breakdown's chi2 is Stage G's committed total chi2 to {REPRO:g} (worst {worst7:.1e})",
           worst7 <= REPRO, f"worst {worst7:.3e}")

    readout = {"schema": "fd-g-diag-readout/1", "labels": LABELS,
               "controls_passed": ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"],
               "blocks": {"groups": list(GROUPS), "vertices": [f"C_model:{v}" for v in VERTICES], "extra": xn,
                          "finite_mc": "V_g", "s1_blocks_per_group": {g_: sorted(b for b in blocks_abs
                                                                               if sa.group_of(b) == g_) for g_ in GROUPS}},
               "constants": {"ridge": RIDGE, "unstable": UNSTABLE, "methods": METHODS, "ill_conditioned": ILL,
                             "top": TOP, "fractions": list(FRACTIONS), "reproduction": REPRO, "units": list(UNITS)},
               "predictions": results,
               "inputs_sha256": {**pins, "definition": sa.DEFINITION_SHA256, "extra_block": a.extra_block_sha256,
                                 **{p["name"]: p["sha256"] for p in predictions}},
               "code_sha256": {"fd_g_diag.py": sa.sha256(Path(__file__).resolve()),
                               "fd_g_compare.py": sa.sha256(Path(G.__file__).resolve()),
                               "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve())},
               "argv": [str(x) for x in sys.argv]}
    counter = [0]
    readout = finite(readout, counter)
    readout["non_finite_written_as_null"] = counter[0]
    tmp = a.out_json.with_name(a.out_json.name + ".partial")
    tmp.write_text(json.dumps(readout, indent=1, allow_nan=False) + "\n")
    os.replace(tmp, a.out_json)
    for r in results:
        for c in r["comparisons"]:
            print(summary_line(r["name"], c), flush=True)
    print(json.dumps({"wrote": str(a.out_json), "sha256": sa.sha256(a.out_json)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""5D G-FOLLOWUP (state/measurement-paper/5d-community-20261024/FD-G-FOLLOWUP-DECLARATION.md): two descriptive
follow-ups to G-DIAG, approved by Joseph in DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md
section 2, from the same pinned inputs as Stage G and G-DIAG. G-DIAG's controls D0-D5 run first (fd_g_diag.load).

G-R04, numbers only, for R04 and the cells that load with it in G-DIAG's top modes (CELLS):
0. (provenance) each cell's loading in the top modes of G-DIAG's reported, relative-to-f breakdown;
1. each cell's box edges, its H2 boxes, its fine-bin count and its face neighbours on the H2 grid;
2. f's relative sigma split by S1 group, each C_model vertex, C_resp and the totals, beside the median over 16 cells;
3. R04's correlation with each other cell under C_total + C_resp, under each 16-cell prediction's reported matrix
   C_total + C_resp + V_g, and under each block alone;
4. for each prediction, g/f - 1, the pull, sigma_Vg/f and the MC event count at each cell, read from the Stage G
   readout (GiBUU only on its eight cells: no GiBUU value on R04 or R14 exists or is formed);
5. a search of every pinned product's keys for a data or reco event count or an efficiency (SEARCH), and the
   definition's per-cell values for every matching field.

G-SENS, the correlation sensitivity of Stage G's reported chi2, M = C_total + C_resp + V_g: for a family F of S1
groups (FAMILIES), each group in F has its correlations shrunk toward the diagonal with its variances kept,
    C_g(alpha) = D^1/2 [(1 - alpha) rho + alpha I] D^1/2,   i.e. (1 - alpha) C_g off the diagonal and C_g on it,
for alpha in ALPHAS; every other block (stat, seed, the C_model vertices, C_resp and V_g) is unchanged. For each
family, alpha and prediction: the total chi2, ndf, condition number, modes for 50/90/99 %, and the top mode's relative
sigma and leading cells, relative to f (the G-DIAG ruling). No p-value: a descriptive sensitivity of the reported chi2,
not an alternative result.

G-SENS2 (--part sens2, FD-G-SENS2-DECLARATION.md): the same shrinkage and record for flux, detector and lateral each
shrunk alone (SENS2_FAMILIES), and the flux family's top-mode block shares at alpha 0 and 0.1. Interaction alone and
the joint family are referenced from G-FOLLOWUP's pinned readout, not recomputed; control H0 recomputes two of their
chi2 (IDENTITY). Without --part, or with --part followup, the tool is G-FOLLOWUP's, unchanged in its output.

Controls F0, R1-R4 and S0-S2 (followup) and H0, H1, S0-S2 and H2 (sens2) each refuse (exit 1, nothing written); alpha = 0
reproduces Stage G (S0).

MEASURES: arithmetic on Stage G's declared inputs and its and G-DIAG's committed readouts. CANNOT AUTHORIZE: any
reading of the comparison, a claim, or paper text.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_g_compare as G  # noqa: E402  (PREDICTIONS, GIBUU_CELLS, ROLES, Stop, npz_headers)
import fd_g_diag as D  # noqa: E402  (load, comparison_blocks, residual, eigen, mode_chi2, chi2_ways, ...)
import s1_assemble as sa  # noqa: E402  (sha256, s1.H2_EDGES, s1.AXES)

N_CELLS, TOL, REPRO = D.N_CELLS, D.TOL, D.REPRO
FOCUS = "R04"
# R04, then the cells loading with it in G-DIAG's committed top modes (amendment 1 adds R07 and R09)
CELLS = ("R04", "R00", "R01", "R07", "R08", "R09", "R10", "R14")
ALPHAS = (0.0, 0.1, 0.25, 0.5, 1.0)                      # 0 is the reference and control S0
FAMILIES = {"interaction": ("interaction",),
            "c_e_systematic": ("interaction", "flux", "detector", "lateral")}
# normalization's full correlation is structural (one 1.4 % scale for every cell), so it is shrunk in no family
# (the director's ruling 14, amendment 1); it is unchanged, with stat, seed, the vertices, C_resp and V_g
FAMILY_ROLE = {"interaction": "primary", "c_e_systematic": "second"}
# G-SENS2 (--part sens2; FD-G-SENS2-DECLARATION.md): each remaining C_e systematic group shrunk alone. Interaction
# alone and the joint family are G-FOLLOWUP's, referenced from its readout and not recomputed; IDENTITY names the two
# of its records whose chi2 control H0 recomputes. SHARES: the family and alphas whose top mode's block shares are given.
SENS2_FAMILIES = {"flux": ("flux",), "detector": ("detector",), "lateral": ("lateral",)}
SENS2_ROLE = "single group"
IDENTITY = (("interaction", 1.0, "nuwro"), ("c_e_systematic", 0.25, "gibuu"))
SHARES = ("flux", (0.0, 0.1))
LEAD = 3                                                 # leading cells of a top mode: the LEAD largest |loading|
# a key matches if one of these words stands in it with no letter on either side ("data_b0", "expected_reco_signal")
SEARCH = re.compile(r"(?<![a-z])(data|reco|eff|efficiency|count|counts|nevt|n_ev|event|events|purity|stability|truth|"
                    r"signal|accept|acceptance)(?![a-z])", re.IGNORECASE)
PINS = {**D.PINS, "g_diag_readout": "680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88"}
# G-SENS2 reads G-FOLLOWUP's committed readout, not G-DIAG's (kept apart so G-FOLLOWUP's readout is unchanged)
SENS2_PINS = {**D.PINS, "g_followup_readout": "cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379"}
SENS_LABEL = "descriptive sensitivity of the reported \u03c7\u00b2, not an alternative result"
LABELS = {
    "what": "two descriptive follow-ups to G-DIAG (FD-G-FOLLOWUP-DECLARATION.md); numbers only, no new statistic",
    "r04": "numbers from the pinned products for R04 and the cells that load with it in G-DIAG's top modes",
    "sens": f"{SENS_LABEL}: one family of S1 groups has its correlations shrunk toward the diagonal, C(alpha) = "
            "D^1/2 [(1 - alpha) rho + alpha I] D^1/2, its variances kept; no p-value",
    "units": "relative to f: d = (f - g)/f, M = (C + V_g)/(f f^T), so sqrt(lambda) is a relative sigma (the G-DIAG "
             "ruling); chi2 and ndf are unit-free",
    "not": "no reading, claim or paper text",
}


def report(control, name, ok, why="differs"):
    G.report(control, name, ok, why)


def worst_rel(a, b) -> float:
    """The largest |a - b| / max(|a|, |b|) over the entries, with entries equal (both zero included) counting 0."""
    a, b = np.atleast_1d(np.asarray(a, float)), np.atleast_1d(np.asarray(b, float))
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return float("inf")
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(a == b, 0.0, np.abs(a - b) / np.where(den > 0, den, 1.0))))


# ---------------------------------------------------------------- G-R04 (pure functions)


def h2_box(b: int, edges: dict) -> dict:
    """H2 box b's intervals: bit k of b (axis k = AXES[k], the most significant first) picks the lower or upper bin."""
    axes = sa.s1.AXES
    return {ax: [edges[ax][(b >> (len(axes) - 1 - k)) & 1], edges[ax][((b >> (len(axes) - 1 - k)) & 1) + 1]]
            for k, ax in enumerate(axes)}


def bounding_box(boxes: list[dict]) -> dict:
    return {ax: [min(b[ax][0] for b in boxes), max(b[ax][1] for b in boxes)] for ax in sa.s1.AXES}


def neighbours(cell: int, defn: dict) -> list[dict]:
    """Item 1: the cells (or unreported H2 boxes) sharing a face with this cell on the 2^5 H2 grid: an H2 box of the
    cell and one outside it that differ in exactly one axis's bin."""
    m = defn["h2_to_reporting_cell"]
    axes = sa.s1.AXES
    out: dict[tuple, list] = {}
    for b in defn["reporting_cells"][cell]["h2_cells"]:
        for k, ax in enumerate(axes):
            nb = b ^ (1 << (len(axes) - 1 - k))
            if m[nb] == cell:
                continue
            who = f"R{m[nb]:02d}" if m[nb] >= 0 else f"unreported H2 box {nb}"
            out.setdefault((who, ax), []).append([b, nb])
    return [{"neighbour": w, "axis": ax, "h2_pairs": pairs} for (w, ax), pairs in sorted(out.items())]


def definition_record(cell: int, defn: dict, fm: np.ndarray) -> dict:
    c = defn["reporting_cells"][cell]
    return {"id": c["id"], "h2_boxes": list(c["h2_cells"]), "box": c["box"], "n_fine_bins": int(np.sum(fm == cell)),
            "neighbours": neighbours(cell, defn)}


def relative_sigma(f: np.ndarray, groups: dict, S: np.ndarray, Cx: np.ndarray, Ct: np.ndarray, xn: str) -> dict:
    """Item 2: sqrt(diag B)/f for S1's seven groups, the three vertices, the extra block and the totals (16 cells)."""
    rel = {g: np.sqrt(np.clip(np.diag(groups[g]), 0, None)) / f for g in D.GROUPS}
    rel.update({f"C_model:{v}": np.abs(S[j]) for j, v in enumerate(D.VERTICES)})
    rel[xn] = np.sqrt(np.clip(np.diag(Cx), 0, None)) / f
    rel["C_e"] = np.sqrt(np.clip(np.diag(sum(groups[g] for g in D.GROUPS)), 0, None)) / f
    rel["C_model"] = np.sqrt(np.sum(S ** 2, axis=0))
    rel["C_total"] = np.sqrt(np.diag(Ct)) / f
    rel[f"C_total + {xn}"] = np.sqrt(np.diag(Ct + Cx)) / f
    return rel


def correlation(B: np.ndarray, i: int, j: int) -> float | None:
    """Item 3: B_ij / sqrt(B_ii B_jj), or None where a variance is zero."""
    den = B[i, i] * B[j, j]
    return float(B[i, j] / np.sqrt(den)) if den > 0 else None


def correlation_matrices(groups: dict, S: np.ndarray, Cx: np.ndarray, Ct: np.ndarray, f: np.ndarray, xn: str) -> dict:
    """The 16 x 16 matrices item 3 reads, all absolute: the reported covariance of f, each block alone, the totals."""
    ff = np.outer(f, f)
    mats = {f"C_total + {xn}": Ct + Cx}
    mats.update({g: groups[g] for g in D.GROUPS})
    mats.update({f"C_model:{v}": np.outer(S[j], S[j]) * ff for j, v in enumerate(D.VERTICES)})
    mats[xn] = Cx
    mats["C_e"] = sum(groups[g] for g in D.GROUPS)
    mats["C_model"] = (S.T @ S) * ff
    mats["C_total"] = Ct
    return mats


def prediction_cells(rec: dict) -> dict:
    """Item 4: the Stage G readout's reported values at CELLS, looked up by cell name in the record's own cell list."""
    out = {}
    for c in CELLS:
        if c not in rec["cells"]:
            out[c] = {"compared": False, "why": "not one of this prediction's cells in Stage G"}
            continue
        k = rec["cells"].index(c)
        out[c] = {"compared": True, "g_over_f_minus_1": rec["g_over_f_minus_1"][k], "pull": rec["pulls"][k],
                  "sigma_total_over_f": rec["sigma_total_over_f"][k], "sigma_Vg_over_f": rec["sigma_Vg_over_f"][k],
                  "n_mc_events": rec["n_mc_events_in_cells"][k]}
    return out


def key_paths(obj, prefix=()) -> list[tuple]:
    """Every key path in a JSON value, as a tuple of keys; a list's elements share the component "[]"."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = (*prefix, str(k))
            out.append(p)
            out.extend(key_paths(v, p))
    elif isinstance(obj, list):
        seen = set()
        for v in obj:
            for p in key_paths(v, (*prefix, "[]")):
                if p not in seen:
                    seen.add(p)
                    out.append(p)
    return out


def npz_key_paths(path: Path, unparsed: list) -> list[tuple]:
    """An npz's member names (from the .npy headers), and the key paths inside any scalar string member that is JSON.
    No other member is loaded; a string member that is not JSON is appended to `unparsed`."""
    out = []
    heads = G.npz_headers(path)
    with np.load(path, allow_pickle=False) as z:
        for m, (shape, dtype) in heads.items():
            out.append((m,))
            if shape == () and dtype.kind in "US":
                v = z[m][()]
                try:
                    out.extend(key_paths(json.loads(v.decode() if isinstance(v, bytes) else str(v)), (m,)))
                except ValueError:
                    unparsed.append(f"{path.name}:{m}")
    return out


def search(products: dict[str, list[tuple]]) -> dict:
    """Item 5: the key paths of each product whose last key matches SEARCH (case-insensitive), joined with " / "."""
    return {name: [" / ".join(p) for p in paths if SEARCH.search(p[-1])] for name, paths in products.items()}


def definition_values(defn: dict) -> dict:
    """Item 5: the definition's per-cell fields matching SEARCH, at CELLS, and the median over the 16 cells."""
    rc = defn["reporting_cells"]
    fields = [k for k in rc[0] if SEARCH.search(k) and isinstance(rc[0][k], (int, float)) and not isinstance(rc[0][k],
                                                                                                          bool)]
    return {"simulation_only": defn.get("simulation_only"), "fields": fields,
            "cells": {c: {k: rc[int(c[1:])][k] for k in fields} for c in CELLS},
            "median_over_16": {k: float(np.median([r[k] for r in rc])) for k in fields}}


# ---------------------------------------------------------------- G-SENS (pure functions)


def shrink(C: np.ndarray, alpha: float) -> np.ndarray:
    """D^1/2 [(1 - alpha) rho + alpha I] D^1/2: (1 - alpha) C off the diagonal, C's own diagonal, bit for bit."""
    out = (1.0 - alpha) * C
    np.fill_diagonal(out, np.diag(C))
    return out


def shrunk_blocks(blocks: dict, family: tuple, alpha: float) -> dict:
    return {k: (shrink(B, alpha) if k in family else B) for k, B in blocks.items()}


def sens_record(d: np.ndarray, blocks: dict, cells: list[str]) -> dict:
    """One (family, alpha, prediction): the chi2 against the sum of the blocks, and its spectrum and top mode."""
    M = sum(blocks.values())
    lam, V = D.eigen(M)
    proj, c = D.mode_chi2(lam, V, d)
    order = np.argsort(c)[::-1]
    with np.errstate(invalid="ignore"):
        frac = c[order] / np.sum(c)
    t = order[0]
    v = V[:, t]
    lead = np.argsort(-np.abs(v), kind="stable")[:LEAD]
    stab = D.chi2_ways(M, d, lam, V)
    return {"chi2": stab["chi2_cholesky"], "ndf": len(d), "condition": D.condition(M), "lambda_min": float(lam[-1]),
            "modes_needed": D.modes_needed(frac),
            "top_mode": {"mode": int(t), "sigma": float(np.sqrt(max(lam[t], 0.0))), "chi2": float(c[t]),
                         "fraction": float(frac[0]),
                         "leading_cells": [{"cell": cells[k], "loading": float(v[k])} for k in lead],
                         "loadings": dict(zip(cells, v.tolist()))},
            "stability": {k: stab[k] for k in ("chi2_mode_sum", "chi2_lstsq", "rel_mode_sum_vs_cholesky",
                                               "rel_lstsq_vs_cholesky", "rel_ridge_vs_cholesky", "ridge_sensitive",
                                               "methods_disagree", "unstable")},
            "label": SENS_LABEL}


def summary_line(fam: str, alpha: float, name: str, r: dict, chi2_0: float) -> str:
    t = r["top_mode"]
    x2 = "not positive definite" if r["chi2"] is None else f"{r['chi2']:.2f}"
    return (f"[G-SENS] {fam:14s} alpha {alpha:<4g} {name:10s}: chi2 {x2}/{r['ndf']} (alpha 0: {chi2_0:.2f}); "
            f"cond {r['condition']:.3g}; modes for 50/90 % {r['modes_needed']['50%']}/{r['modes_needed']['90%']}; "
            f"top mode sigma {100 * t['sigma']:.2f} % carries {100 * t['fraction']:.1f} %, leading "
            + ", ".join(f"{x['cell']} {x['loading']:+.2f}" for x in t["leading_cells"])
            + (" UNSTABLE" if r["stability"]["unstable"] else ""))


def prediction_blocks(x, spec: dict, reported_carries: bool) -> tuple:
    """One prediction's cell names, residual d and reported-M blocks B0, relative to f, and Stage G's reported chi2."""
    cells, g, Vg = x.integ[spec["name"]]
    i = np.asarray(cells)
    B0 = D.comparison_blocks(x.groups_rel, x.S, x.Cx_rel if reported_carries else None, Vg / x.f ** 2, i, x.xn,
                             np.ones(N_CELLS))
    return [f"R{c:02d}" for c in cells], D.residual(x.f, g, i, np.ones(N_CELLS)), B0, x.grp[spec["name"]]["total"]["chi2"]


def sens_records(x, families: dict, roles: dict, predictions, reported_carries: bool) -> list[dict]:
    """G-SENS: for each family, prediction and alpha in ALPHAS, the record of the reported M with the family shrunk;
    then controls S0 (alpha = 0 is Stage G), S1 (every shrunk M positive definite) and S2 (the shrinkage is the
    declared one, every other block bit-identical)."""
    sens, worst0, notpd, diag_bad, off_bad, other_bad = [], 0.0, [], [], 0.0, []
    for fam, groups in families.items():
        for spec in predictions:
            names, d, B0, chi2_g = prediction_blocks(x, spec, reported_carries)
            n = len(names)
            M0 = sum(B0.values())
            chi2_0 = None
            for alpha in ALPHAS:
                Ba = shrunk_blocks(B0, groups, alpha)
                for k in B0:
                    if k in groups:
                        if not np.array_equal(np.diag(Ba[k]), np.diag(B0[k])):
                            diag_bad.append(f"{fam} {alpha} {spec['name']} {k}")
                        off = ~np.eye(n, dtype=bool)
                        scale = max(np.abs(B0[k]).max(), 1e-300)
                        off_bad = max(off_bad, float(np.abs(Ba[k][off] - (1 - alpha) * B0[k][off]).max() / scale))
                    elif not np.array_equal(Ba[k], B0[k]):
                        other_bad.append(f"{fam} {alpha} {spec['name']} {k}")
                if not np.array_equal(np.diag(sum(Ba.values())), np.diag(M0)):
                    diag_bad.append(f"{fam} {alpha} {spec['name']} M")
                r = sens_record(d, Ba, names)
                r["shrunk_group_lambda_min"] = {k: float(np.linalg.eigvalsh(Ba[k]).min()) for k in groups}
                if r["chi2"] is None or not r["lambda_min"] > 0:
                    notpd.append(f"{fam} {alpha} {spec['name']}")
                if alpha == 0.0:
                    chi2_0 = r["chi2"]
                    worst0 = max(worst0, abs(r["chi2"] - chi2_g) / abs(chi2_g) if r["chi2"] is not None else np.inf)
                sens.append({"family": fam, "family_role": roles[fam], "alpha": alpha, "prediction": spec["name"],
                             "cells": names, "chi2_stage_g": chi2_g, "chi2_at_alpha_0": chi2_0, **r})
    report("S0", f"alpha = 0 reproduces Stage G's reported chi2 for every family and prediction to {REPRO:g} "
                 f"(worst {worst0:.1e})", worst0 <= REPRO, f"worst {worst0:.3e}")
    report("S1", "every shrunk M is positive definite", not notpd, f"not: {notpd}")
    report("S2", "every shrunk group's diagonal, and every shrunk M's, is the unshrunk one bit for bit", not diag_bad,
           f"differs: {diag_bad[:5]}")
    report("S2", f"every shrunk group's off-diagonal is (1 - alpha) times the unshrunk one (worst {off_bad:.1e})",
           off_bad <= 1e-15, f"worst {off_bad:.3e}")
    report("S2", "every block outside the family is unchanged bit for bit", not other_bad, f"changed: {other_bad[:5]}")
    return sens


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
    ap.add_argument("--part", choices=("followup", "sens2"), default="followup",
                    help="followup: G-R04 and G-SENS (FD-G-FOLLOWUP-DECLARATION.md); sens2: G-SENS2 "
                         "(FD-G-SENS2-DECLARATION.md)")
    ap.add_argument("--g-diag-readout", type=Path, help="the committed fd/readout/fd_g_diag_readout.json (followup)")
    ap.add_argument("--g-followup-readout", type=Path,
                    help="the committed fd/readout/fd_g_followup_readout.json (sens2)")
    ap.add_argument("--extra-block-sha256", required=True)
    ap.add_argument("--extra-block-key", required=True)
    ap.add_argument("--extra-block-name", required=True)
    ap.add_argument("--extra-block-role", choices=G.ROLES, required=True)
    a = ap.parse_args(argv)
    need, other = (("--g-diag-readout", "--g-followup-readout") if a.part == "followup" else
                   ("--g-followup-readout", "--g-diag-readout"))
    if getattr(a, need[2:].replace("-", "_")) is None:
        ap.error(f"--part {a.part} requires {need}")
    if getattr(a, other[2:].replace("-", "_")) is not None:
        ap.error(f"--part {a.part} does not read {other}")
    return a


def run(a, pins=None, predictions=None) -> int:
    predictions = G.PREDICTIONS if predictions is None else predictions
    if a.part == "sens2":
        return run_sens2(a, SENS2_PINS if pins is None else pins, predictions)
    pins = PINS if pins is None else pins
    if a.out_json.exists():
        raise G.Stop("-", f"refusing to overwrite {a.out_json}")
    x = D.load(a, pins, predictions)                     # G-DIAG's D0-D5
    f, Ct, Cx, S, xn, defn, fm, U = x.f, x.Ct, x.Cx, x.S, x.xn, x.defn, x.fm, x.U
    reported_mname, reported_carries = x.comps[0][1]
    names16 = [p["name"] for p in predictions if p["cells"] == "all"]

    # F0. the committed G-DIAG readout: pinned, its schema, its Stage G and extra block are this run's
    if sa.sha256(a.g_diag_readout) != pins["g_diag_readout"]:
        raise G.Stop("F0", f"g_diag_readout {a.g_diag_readout}: sha256 {sa.sha256(a.g_diag_readout)} != "
                           f"{pins['g_diag_readout']}")
    gd = json.loads(a.g_diag_readout.read_text())
    gdp = {p["name"]: p for p in gd.get("predictions", [])}
    same = {"schema fd-g-diag-readout/1": gd.get("schema") == "fd-g-diag-readout/1",
            "Stage G readout": gd.get("inputs_sha256", {}).get("g_readout") == pins["g_readout"],
            "extra block": gd.get("inputs_sha256", {}).get("extra_block") == a.extra_block_sha256,
            "the same predictions": sorted(gdp) == sorted(p["name"] for p in predictions),
            "the reported comparison's matrix": all(gdp[n]["comparisons"][0]["matrix"] == f"{reported_mname} + V_g"
                                                    for n in gdp)}
    report("F0", "the G-DIAG readout is pinned and ran on this Stage G readout, extra block and comparison",
           all(same.values()), "differs in " + ", ".join(k for k, v in same.items() if not v))

    # item 0: each cell's loading in G-DIAG's reported, relative-to-f top modes (16-cell predictions)
    provenance = {}
    for n in names16:
        tops = gdp[n]["comparisons"][0]["relative_to_f"]["top_modes"]
        provenance[n] = [{"mode": t["mode"], "sigma": t["sigma"], "fraction": t["fraction"],
                          "rank_of_R04_by_abs_loading": 1 + sorted(t["loadings"], key=lambda c: -abs(t["loadings"][c]))
                          .index(FOCUS), "loadings": {c: t["loadings"][c] for c in CELLS}} for t in tops]

    # R1. the definition: CELLS exist and are reported; each box is the bounding box of its H2 boxes, which fill it;
    # the fine-bin counts are the fine map's and U's, and cover the fine grid
    ids = [int(c[1:]) for c in CELLS]
    rc = defn["reporting_cells"]
    E = sa.s1.H2_EDGES
    ok_box = []
    for c in range(N_CELLS):
        hb = [h2_box(b, E) for b in rc[c]["h2_cells"]]
        fills = len(hb) == int(np.prod([sum(1 for k in range(2) if E[ax][k] >= bb[0] and E[ax][k + 1] <= bb[1])
                                        for ax, bb in bounding_box(hb).items()]))
        ok_box.append(bounding_box(hb) == rc[c]["box"] and fills and
                      all(defn["h2_to_reporting_cell"][b] == c for b in rc[c]["h2_cells"]))
    counts = np.bincount(fm[fm >= 0], minlength=N_CELLS)[:N_CELLS]
    checks = {"the listed cells are reporting cells R00-R15, reported": all(rc[i]["id"] == i and rc[i]["reported"]
                                                                         for i in ids),
              "each cell's box is the bounding box of its H2 boxes, which fill it": all(ok_box),
              "the fine-bin counts are U's nonzero entries": bool(np.array_equal(counts, np.count_nonzero(U, axis=1))),
              "the counts and the unreported fine bins cover the fine grid": int(counts.sum() + np.sum(fm < 0))
              == fm.size}
    for name, ok in checks.items():
        report("R1", name, bool(ok))
    item1 = {c: definition_record(int(c[1:]), defn, fm) for c in CELLS}

    # R2. item 2's sigmas and medians reproduce S1's committed readout and Stage G's sigma_total_over_f
    rel = relative_sigma(f, x.groups, S, Cx, Ct, xn)
    item2 = {c: {k: float(v[int(c[1:])]) for k, v in rel.items()} for c in CELLS}
    item2["median_over_16"] = {k: float(np.median(v)) for k, v in rel.items()}
    s1rel, s1med = x.s1j.get("relative_sigma", {}), x.s1j.get("median_relative_sigma", {})
    keys = (*D.GROUPS, "C_e", "C_model", "C_total")
    miss = [k for k in keys if k not in s1rel or k not in s1med]
    report("R2", "S1's readout carries every group's and total's relative sigma and median", not miss,
           f"missing {miss}")
    worst = max(max(worst_rel(rel[k], s1rel[k]), worst_rel(item2["median_over_16"][k], s1med[k])) for k in keys)
    report("R2", f"every group's and total's relative sigma, and item 2's median of it, is S1's committed one (worst "
                 f"{worst:.1e})", worst <= TOL, f"worst {worst:.3e}")
    vsum = worst_rel(sum(rel[f"C_model:{v}"] ** 2 for v in D.VERTICES), np.asarray(s1rel["C_model"], float) ** 2)
    report("R2", f"the three vertices' variances sum to S1's C_model variance (worst {vsum:.1e})", vsum <= TOL,
           f"worst {vsum:.3e}")
    tot = reported_mname
    wg = max(worst_rel(rel[tot], x.grp[n]["sigma_total_over_f"]) for n in names16)
    report("R2", f"sigma of {tot} is Stage G's reported sigma_total_over_f (worst {wg:.1e})", wg <= TOL,
           f"worst {wg:.3e}")

    # R3. item 3's correlations: within [-1, 1], and the blocks rebuild the reported covariance's
    mats = correlation_matrices(x.groups, S, Cx, Ct, f, xn)
    i0 = int(FOCUS[1:])
    item3 = {"under": {}, "rank": {}, "under_prediction": {},
             "note": "a block of rank 1 (each C_model vertex; normalization) has correlations of +-1 by construction; "
                     "a block with zero variance at a cell (seed, if zero) has none (null)"}
    for mname, B in mats.items():
        item3["under"][mname] = {c: correlation(B, i0, int(c[1:])) for c in CELLS[1:]}
        item3["rank"][mname] = G.rank(B) if np.abs(B).max() > 0 else 0
    rebuilt = sum(mats[k] for k in (*D.GROUPS, "C_model", xn))
    for n in names16:
        _, _, Vg = x.integ[n]
        Mn = (Ct + (Cx if reported_carries else 0)) + np.diag(Vg)
        item3["under_prediction"][n] = {"matrix": f"{reported_mname} + V_g",
                                        **{c: correlation(Mn, i0, int(c[1:])) for c in CELLS[1:]}}
    allr = [r for m in (*item3["under"].values(), *item3["under_prediction"].values()) for r in m.values()
            if isinstance(r, float)]
    report("R3", "every correlation is within [-1, 1]", all(abs(r) <= 1 + TOL for r in allr))
    dr = max(abs(correlation(rebuilt, i0, int(c[1:])) - item3["under"][f"C_total + {xn}"][c]) for c in CELLS[1:])
    report("R3", f"the blocks rebuild the correlations of C_total + {xn} (worst {dr:.1e})", dr <= TOL, f"worst {dr:.3e}")

    # R4. item 4, from the Stage G readout: its reported pulls are -(g/f - 1)/sqrt(sigma_total^2 + sigma_Vg^2)
    worst4 = 0.0
    item4 = {}
    for spec in predictions:
        rec = x.grp[spec["name"]]
        z = np.asarray(rec["pulls"])
        want = -np.asarray(rec["g_over_f_minus_1"]) / np.hypot(rec["sigma_total_over_f"], rec["sigma_Vg_over_f"])
        worst4 = max(worst4, float(np.max(np.abs(z - want) / np.maximum(np.abs(want), 1e-300))))
        item4[spec["name"]] = {"label": spec["label"], "matrix": rec["total"]["matrix"],
                               "cells": prediction_cells(rec)}
    report("R4", f"every reported pull is -(g/f - 1)/sqrt(sigma_total^2 + sigma_Vg^2) (worst {worst4:.1e})",
           worst4 <= REPRO, f"worst {worst4:.3e}")

    # item 5: the search of every pinned product's keys
    unparsed = []
    products = {"definition": key_paths(defn), "s1_json": key_paths(x.s1j), "cmodel_json": key_paths(x.cj),
                "g_readout": key_paths(x.gr), "g_diag_readout": key_paths(gd),
                "s1_npz": npz_key_paths(a.s1_npz, unparsed), "extra_block": npz_key_paths(a.extra_block, unparsed),
                **{f"prediction:{p['name']}": npz_key_paths(a.s5p_root / p["path"], unparsed) for p in predictions}}
    manifest = [ln.split(None, 1)[1].strip() for ln in a.s5p_sums.read_text().splitlines() if ln.strip()]
    item5 = {"pattern": SEARCH.pattern, "flags": "IGNORECASE", "matched_on": "the last key of each key path",
             "keys_searched": {k: len(v) for k, v in products.items()}, "matches": search(products),
             "string_members_not_json": unparsed,
             "note": "keys only: a match is a key whose name contains a searched word; it is not a count unless its "
                     "value is one, and only the definition's per-cell values are reported",
             "s5p_manifest_paths_matching": {"note": "file names listed in the pinned manifest; not opened",
                                             "paths": [p for p in manifest if SEARCH.search(p)]},
             "definition_values": definition_values(defn)}

    # G-SENS: the blocks of each prediction's reported M, relative to f, with one family shrunk
    sens = sens_records(x, FAMILIES, FAMILY_ROLE, predictions, reported_carries)

    readout = {"schema": "fd-g-followup-readout/1", "labels": LABELS,
               "controls_passed": ["D0", "D1", "D2", "D3", "D4", "D5", "F0", "R1", "R2", "R3", "R4", "S0", "S1", "S2"],
               "constants": {"cells": list(CELLS), "alphas": list(ALPHAS),
                             "families": {k: list(v) for k, v in FAMILIES.items()}, "family_roles": FAMILY_ROLE,
                             "lead": LEAD,
                             "fractions": list(D.FRACTIONS), "search": SEARCH.pattern, "reproduction": REPRO},
               "r04": {"provenance_g_diag_top_modes": provenance, "item1_definition": item1,
                       "item2_relative_sigma": item2, "item3_correlation_with_R04": item3,
                       "item4_stage_g": item4, "item5_search": item5},
               "sens": {"reported_matrix": f"{reported_mname} + V_g", "label": SENS_LABEL,
                        "mode_index": "a top mode's index is its place in that matrix's own eigen-order (lambda "
                                      "descending); it does not name the same mode across alpha",
                        "unchanged": [
                   "stat", "seed", "normalization", *(f"C_model:{v}" for v in D.VERTICES),
                   *([xn] if reported_carries else []), "V_g"], "records": sens},
               "inputs_sha256": {**pins, "definition": sa.DEFINITION_SHA256, "extra_block": a.extra_block_sha256,
                                 **{p["name"]: p["sha256"] for p in predictions}},
               "code_sha256": {"fd_g_followup.py": sa.sha256(Path(__file__).resolve()),
                               "fd_g_diag.py": sa.sha256(Path(D.__file__).resolve()),
                               "fd_g_compare.py": sa.sha256(Path(G.__file__).resolve()),
                               "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve())},
               "argv": [str(v) for v in sys.argv]}
    lines = []
    for c in CELLS:
        r1 = item1[c]
        lines.append(f"[G-R04] {c}: {r1['n_fine_bins']} fine bins; neighbours "
                     + ", ".join(f"{n['neighbour']} ({n['axis']})" for n in r1["neighbours"])
                     + f"; sigma/f {tot} {100 * item2[c][tot]:.2f} % (median {100 * item2['median_over_16'][tot]:.2f} %)"
                     + ("" if c == FOCUS else f"; rho(R04, {c}) {item3['under'][tot][c]:+.3f}"))
    lines.append(f"[G-SENS] every line below: {SENS_LABEL}")
    lines.extend(summary_line(r["family"], r["alpha"], r["prediction"], r, r["chi2_at_alpha_0"]) for r in sens)
    counter = [0]
    readout = D.finite(readout, counter)
    readout["non_finite_written_as_null"] = counter[0]
    tmp = a.out_json.with_name(a.out_json.name + ".partial")
    tmp.write_text(json.dumps(readout, indent=1, allow_nan=False) + "\n")
    os.replace(tmp, a.out_json)
    for ln in lines:
        print(ln, flush=True)
    print(json.dumps({"wrote": str(a.out_json), "sha256": sa.sha256(a.out_json)}), flush=True)
    return 0


def flux_ratio(v: np.ndarray, F: np.ndarray) -> float | None:
    """v^T F v / v^T diag(F) v for the unshrunk flux block F: the part of flux's variance along v that its
    correlations leave (1 for uncorrelated cells). Shrinking by alpha moves the flux term from v^T F v toward
    v^T diag(F) v."""
    den = float(v @ (np.diag(F) * v))
    return float(v @ F @ v) / den if den > 0 else None


def top_mode_shares(d: np.ndarray, blocks: dict, cells: list[str], F: np.ndarray) -> tuple[dict, np.ndarray]:
    """G-SENS2's addition: the top mode (largest chi2 contribution, chosen as sens_record chooses it) of the sum of the
    blocks, each block's share v^T B v / lambda of it (G-DIAG's block_shares), and its flux_ratio."""
    M = sum(blocks.values())
    lam, V = D.eigen(M)
    _, c = D.mode_chi2(lam, V, d)
    t = int(np.argsort(c)[::-1][0])
    v = V[:, t]
    shares = D.block_shares(v, lam[t], blocks)
    return {"mode": t, "sigma": float(np.sqrt(max(lam[t], 0.0))), "chi2": float(c[t]),
            "fraction": float(c[t] / np.sum(c)), "loadings": dict(zip(cells, v.tolist())),
            "block_shares": shares, "share_sum": float(sum(shares.values())),
            "dominant": max(shares, key=lambda b: shares[b]), "flux_ratio": flux_ratio(v, F)}, v


def followed_mode(v: np.ndarray, d: np.ndarray, blocks: dict, F: np.ndarray) -> dict:
    """The alpha = 0 top mode's direction v under other blocks: each block's share v^T B v / v^T M v, the chi2 along
    v alone, (v^T d)^2 / v^T M v (descriptive: v is not an eigenvector of this M), and its flux_ratio."""
    q = float(v @ sum(blocks.values()) @ v)
    shares = {k: float(v @ B @ v / q) for k, B in blocks.items()}
    return {"variance_along": q, "chi2_along": float((v @ d) ** 2 / q), "block_shares": shares,
            "share_sum": float(sum(shares.values())), "dominant": max(shares, key=lambda b: shares[b]),
            "flux_ratio": flux_ratio(v, F)}


def run_sens2(a, pins, predictions) -> int:
    """G-SENS2 (FD-G-SENS2-DECLARATION.md): flux, detector and lateral each shrunk alone, as G-SENS."""
    if a.out_json.exists():
        raise G.Stop("-", f"refusing to overwrite {a.out_json}")
    x = D.load(a, pins, predictions)                     # G-DIAG's D0-D5
    reported_mname, reported_carries = x.comps[0][1]
    specs = {p["name"]: p for p in predictions}

    # H0. the committed G-FOLLOWUP readout: pinned, its schema and inputs are this run's, and two of its G-SENS
    # records' chi2 are recomputed here with G-FOLLOWUP's own families
    if sa.sha256(a.g_followup_readout) != pins["g_followup_readout"]:
        raise G.Stop("H0", f"g_followup_readout {a.g_followup_readout}: sha256 {sa.sha256(a.g_followup_readout)} != "
                           f"{pins['g_followup_readout']}")
    fu = json.loads(a.g_followup_readout.read_text())
    same = {"schema fd-g-followup-readout/1": fu.get("schema") == "fd-g-followup-readout/1",
            "Stage G readout": fu.get("inputs_sha256", {}).get("g_readout") == pins["g_readout"],
            "extra block": fu.get("inputs_sha256", {}).get("extra_block") == a.extra_block_sha256,
            "its families": fu.get("constants", {}).get("families") == {k: list(v) for k, v in FAMILIES.items()},
            "its alphas": fu.get("constants", {}).get("alphas") == list(ALPHAS),
            "its reported matrix": fu.get("sens", {}).get("reported_matrix") == f"{reported_mname} + V_g",
            "its shared input pins": all(fu.get("inputs_sha256", {}).get(k) == pins[k] for k in D.PINS),
            "its predictions": all(fu.get("inputs_sha256", {}).get(p["name"]) == p["sha256"] for p in predictions)
            and sorted({r["prediction"] for r in fu.get("sens", {}).get("records", [])}) ==
            sorted(p["name"] for p in predictions)}
    report("H0", "the G-FOLLOWUP readout is pinned and ran on this Stage G readout, extra block, families and matrix",
           all(same.values()), "differs in " + ", ".join(k for k, v in same.items() if not v))
    identity, worst_id = [], 0.0
    for fam, alpha, name in IDENTITY:
        ref = next((r for r in fu["sens"]["records"] if (r["family"], r["alpha"], r["prediction"]) == (fam, alpha, name)),
                   None)
        if ref is None or ref.get("chi2") is None or name not in specs:
            raise G.Stop("H0", f"the G-FOLLOWUP readout has no record {fam} {alpha} {name} with a chi2")
        names, d, B0, _ = prediction_blocks(x, specs[name], reported_carries)
        mine = sens_record(d, shrunk_blocks(B0, FAMILIES[fam], alpha), names)["chi2"]
        rel = abs(mine - ref["chi2"]) / abs(ref["chi2"]) if mine is not None else float("inf")
        worst_id = max(worst_id, rel)
        identity.append({"family": fam, "alpha": alpha, "prediction": name, "chi2_g_followup_readout": ref["chi2"],
                         "chi2_recomputed": mine, "relative_difference": rel})
    report("H0", f"two G-FOLLOWUP chi2 values recomputed from the pinned inputs equal its readout's to {REPRO:g} "
                 f"(worst {worst_id:.1e})", worst_id <= REPRO, f"worst {worst_id:.3e}")

    # H1. each new family is exactly its own S1 group, never stat, seed, normalization or interaction
    bad = {f: g for f, g in SENS2_FAMILIES.items()
           if tuple(g) != (f,) or f not in D.GROUPS or f in ("stat", "seed", "normalization", "interaction")}
    report("H1", "each family shrinks exactly its own group, and none shrinks stat, seed, normalization or interaction",
           not bad, f"families {bad}")

    # G-SENS2 records, with G-SENS's controls S0-S2
    sens = sens_records(x, SENS2_FAMILIES, dict.fromkeys(SENS2_FAMILIES, SENS2_ROLE), predictions, reported_carries)

    # the addition: the flux family's top-mode block shares at SHARES' alphas, and the alpha = 0 top mode followed
    # into the second alpha's blocks; H2: the shares sum to 1, and the two top modes are the ones the records carry
    fam, alphas = SHARES
    fu0 = {r["prediction"]: r for r in fu["sens"]["records"] if r["family"] == "interaction" and r["alpha"] == 0.0}
    mine = {(r["prediction"], r["alpha"]): r for r in sens if r["family"] == fam}
    shares, worst_sh, mismatch = {}, 0.0, []
    for spec in predictions:
        names, d, B0, _ = prediction_blocks(x, spec, reported_carries)
        F = B0[SENS2_FAMILIES[fam][0]]
        out, vs = {}, {}
        for alpha in alphas:
            t, vs[alpha] = top_mode_shares(d, shrunk_blocks(B0, SENS2_FAMILIES[fam], alpha), names, F)
            out[f"{alpha:g}"] = t
            worst_sh = max(worst_sh, abs(t["share_sum"] - 1.0))
            ref = fu0.get(spec["name"], {}).get("top_mode") if alpha == 0.0 else mine[(spec["name"], alpha)]["top_mode"]
            if (ref is None or ref["mode"] != t["mode"] or worst_rel(ref["sigma"], t["sigma"]) > REPRO or
                    max(abs(ref["loadings"][c] - t["loadings"][c]) for c in names) > REPRO):
                mismatch.append(f"{spec['name']} alpha {alpha:g}")
        a0, a1 = alphas
        fol = followed_mode(vs[a0], d, shrunk_blocks(B0, SENS2_FAMILIES[fam], a1), F)
        worst_sh = max(worst_sh, abs(fol["share_sum"] - 1.0))
        out[f"alpha_{a0:g}_mode_at_{a1:g}"] = fol
        out["overlap_abs"] = float(abs(vs[a0] @ vs[a1]))
        shares[spec["name"]] = out
    report("H2", f"every {fam} top mode's, and every followed mode's, block shares sum to 1 (worst {worst_sh:.1e})",
           worst_sh <= 1e-10, f"worst {worst_sh:.3e}")
    report("H2", f"each {fam} top mode is the one its record carries: alpha 0 G-FOLLOWUP's, alpha {alphas[1]:g} this "
                 "run's", not mismatch, f"differs: {mismatch}")

    unchanged = {f: [k for k in (*D.GROUPS, *(f"C_model:{v}" for v in D.VERTICES), *([x.xn] if reported_carries else []),
                                 "V_g") if k not in g] for f, g in SENS2_FAMILIES.items()}
    readout = {"schema": "fd-g-sens2-readout/1",
               "labels": {"what": "G-SENS2 (FD-G-SENS2-DECLARATION.md): flux, detector and lateral each shrunk alone, "
                                  "as G-SENS; numbers only, no new statistic",
                          "sens": LABELS["sens"], "units": LABELS["units"],
                          "shares": "block share of a mode = v^T B v / lambda over the shrunk matrix's own blocks "
                                    "(G-DIAG's: S1's seven groups, the three vertices, C_resp, V_g); the top mode is "
                                    "that matrix's own. alpha_0_mode_at_0.1: the alpha = 0 top mode's direction v under "
                                    "the alpha = 0.1 blocks, shares v^T B v / v^T M v and chi2_along = (v^T d)^2 / v^T M "
                                    "v (descriptive; v is not an eigenvector there); overlap_abs = |v_0 . v_0.1|; "
                                    "flux_ratio = v^T F v / v^T diag(F) v for the unshrunk flux block F",
                          "referenced": "interaction alone and the joint family are G-FOLLOWUP's (its readout, "
                                        "pinned), not recomputed; H0 recomputes two of their chi2 as an identity check",
                          "not": LABELS["not"]},
               "controls_passed": ["D0", "D1", "D2", "D3", "D4", "D5", "H0", "H1", "S0", "S1", "S2", "H2"],
               "constants": {"families": {k: list(v) for k, v in SENS2_FAMILIES.items()}, "role": SENS2_ROLE,
                             "alphas": list(ALPHAS), "lead": LEAD, "fractions": list(D.FRACTIONS),
                             "identity": [list(t) for t in IDENTITY], "shares": [SHARES[0], list(SHARES[1])],
                             "reproduction": REPRO},
               "referenced": {"g_followup_readout": pins["g_followup_readout"],
                              "families": {k: list(v) for k, v in FAMILIES.items()}},
               "identity": identity,
               "sens": {"reported_matrix": f"{reported_mname} + V_g", "label": SENS_LABEL,
                        "mode_index": "a top mode's index is its place in that matrix's own eigen-order (lambda "
                                      "descending); it does not name the same mode across alpha",
                        "unchanged": unchanged, "records": sens},
               "flux_top_mode_shares": {"family": fam, "alphas": list(alphas), "label": SENS_LABEL,
                                        "predictions": shares},
               "inputs_sha256": {**pins, "definition": sa.DEFINITION_SHA256, "extra_block": a.extra_block_sha256,
                                 **{p["name"]: p["sha256"] for p in predictions}},
               "code_sha256": {"fd_g_followup.py": sa.sha256(Path(__file__).resolve()),
                               "fd_g_diag.py": sa.sha256(Path(D.__file__).resolve()),
                               "fd_g_compare.py": sa.sha256(Path(G.__file__).resolve()),
                               "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve())},
               "argv": [str(v) for v in sys.argv]}
    lines = [f"[G-SENS2] every line below: {SENS_LABEL}"]
    lines.extend(summary_line(r["family"], r["alpha"], r["prediction"], r, r["chi2_at_alpha_0"]) for r in sens)
    for name, by in shares.items():
        for al in (f"{v:g}" for v in alphas):
            t = by[al]
            lines.append(f"[G-SENS2] {fam} alpha {al:<4s} {name:10s}: top mode {t['mode']} sigma {100 * t['sigma']:.2f} % "
                         f"carries {100 * t['fraction']:.1f} %; flux_ratio {t['flux_ratio']:.3f}; shares "
                         + ", ".join(f"{k} {v:.3f}" for k, v in sorted(t["block_shares"].items(), key=lambda kv: -kv[1])[:4]))
        fol = by[f"alpha_{alphas[0]:g}_mode_at_{alphas[1]:g}"]
        lines.append(f"[G-SENS2] {fam} alpha-{alphas[0]:g} mode at {alphas[1]:g} {name:10s}: chi2_along "
                     f"{fol['chi2_along']:.2f}; overlap {by['overlap_abs']:.3f}; flux_ratio {fol['flux_ratio']:.3f}")
    counter = [0]
    readout = D.finite(readout, counter)
    readout["non_finite_written_as_null"] = counter[0]
    tmp = a.out_json.with_name(a.out_json.name + ".partial")
    tmp.write_text(json.dumps(readout, indent=1, allow_nan=False) + "\n")
    os.replace(tmp, a.out_json)
    for ln in lines:
        print(ln, flush=True)
    print(json.dumps({"wrote": str(a.out_json), "sha256": sa.sha256(a.out_json)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())

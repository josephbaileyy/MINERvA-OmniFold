#!/usr/bin/env python3
"""5D 3D, the flux-correlation bootstrap (state/measurement-paper/5d-community-20261024/FD-FLUX-BOOT-DECLARATION.md),
approved by Joseph in DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md item 3: a band on
the ESTIMATION UNCERTAINTY of Stage G's reported chi2 from estimating the flux block's correlations with about n_eff = 19
effective universes, conditional on PPFX's model and the chosen nu-e + IMD constraint. It is not a sensitivity: a narrow
band means the 100 universes pin the correlations well, not that the chi2 is insensitive to them (G-SENS2's alpha
results stand), and systematic choices such as FHC-only against FHC+RHC+IMD are outside it.

S1 builds the flux block from the 100 PPFX Flux universes as MAT's weighted CalcCovMx, with the nu-e + IMD constraint
weights w (s1_assemble.mat_cov, flux_weights). A replicate b resamples the 100 universes with replacement, uniformly,
each drawn universe carrying its own weight, and rebuilds the block with the same rule:

    C*_b = mat_cov(X[i_b], w[i_b]),   i_b = B_REPLICATES x 100 indices from default_rng(SEED)

n_eff enters through the resampling: a weighted mean's bootstrap variance is sum w^2 (x - mu)^2 / (sum w)^2, which is
sigma_w^2 / n_eff only when the residuals do not follow the weights (the declaration, section 4.2). Two variants of the
swapped block:
* ``correlation`` (primary): S1's flux variances kept bit for bit, the replicate's correlations,
  D0^1/2 rho*_b D0^1/2, as G-SENS keeps variances when it shrinks correlations;
* ``block`` (second): the replicate's block C*_b itself, variances included; its variances are biased low by about
  (1 - 1/n_eff) under resampling, which pushes its chi2 high.
Each is swapped for the flux group in Stage G's reported matrix, C_total + C_resp + V_g, with every other block
unchanged, and each prediction's total and shape-only chi2 is recomputed on its own cells (GiBUU on its eight), by Stage
G's own compare() in Stage G's absolute units on C_total + C_resp + (C - C_0) (amendment 1). The
statistic is the distribution of each chi2 over the replicates; the band is its declared percentiles q, beside the
basic (reflected) band 2 chi2_hat - q, with chi2_hat Stage G's own chi2 (the identity replicate), and the offset
median - chi2_hat, the bootstrap's estimate of chi2_hat's bias. In the review's synthetic check of this near-degenerate
regime, chi2 of the estimated matrix was biased high and the bootstrap shifted the same way; on real inputs the
direction is whatever the offset shows. Neither band is an interval for chi2 under the true correlations (section 4.3). One named
alternative, ``uniform``: the block from the 100 universes with equal weights (the flux prior without the constraint),
a single chi2 per prediction. No p-value anywhere.

Controls D0-D5 (G-DIAG's, through fd_g_diag.load) and B0-B6 each refuse (exit 1, nothing written); B6, the
matrix-level check of every swap, is amendment 1's.

MEASURES: arithmetic on Stage G's pinned inputs, the 100 committed Flux universe products and the constraint file.
CANNOT AUTHORIZE: any reading of the comparison, a claim, or paper text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_g_compare as G  # noqa: E402  (PREDICTIONS, ROLES, SHAPE_LAMBDA, Stop, report, sa_call)
import fd_g_diag as D  # noqa: E402  (load, PINS, GROUPS, finite, REPRO, TOL)
import s1_assemble as sa  # noqa: E402  (sha256, mat_cov, flux_weights, xs, FLUX, CONSTRAINT_SHA256)

N_CELLS, TOL, REPRO = D.N_CELLS, D.TOL, D.REPRO
N_UNIVERSES = 100
B_REPLICATES = 2000
SEED = 20261027
# sha256 of the (B_REPLICATES, N_UNIVERSES) index matrix as little-endian int32, from default_rng(SEED).integers
# (numpy 1.26.4, the cluster's root_6_28 env and this checkout's); control B3 refuses if the generator gives another
INDEX_SHA256 = "23e2e37426ff85ef6d17a73d1f6740e9f6c26655485988b51efd934ee0862e7f"
PERCENTILES = (2.5, 16.0, 50.0, 84.0, 97.5)
PERCENTILE_METHOD = "linear"
VARIANTS = ("correlation", "block")
PAIR = ("R04", "R08")                   # the pair G-FOLLOWUP reports (+0.983 in the flux block alone)
FLUX_GROUP = "flux"
PINS = {**D.PINS, "constraint": sa.CONSTRAINT_SHA256}
LABEL = ("estimation uncertainty, not sensitivity: the scatter of the reported chi2 when the flux correlations are "
         "re-estimated from the 100 weighted universes; not an interval for the chi2 under the true correlations")
LABELS = {
    "what": "3D (FD-FLUX-BOOT-DECLARATION.md): Stage G's reported chi2 with the flux block rebuilt from bootstrap "
            "replicates of the 100 weighted Flux universes; numbers only, no p-value",
    "replicate": "the 100 universes resampled with replacement, uniformly, each drawn universe carrying its nu-e + IMD "
                 "weight; the block rebuilt with S1's rule (MAT CalcCovMx, weighted, centred on the replicate's "
                 "weighted mean)",
    "variants": "correlation (primary): S1's flux variances kept bit for bit, the replicate's correlations; block "
                "(second): the replicate's block itself, variances included, which under resampling are biased low by "
                "about (1 - 1/n_eff) and push its chi2 high",
    "uniform": "the block from the 100 universes with equal weights: the flux prior without the constraint; a named "
               "alternative, not an alternative result",
    "n_eff": "n_eff enters through the resampling: a weighted mean's bootstrap variance is sum w^2 (x - mu)^2 / "
             "(sum w)^2, which equals sigma_w^2 / n_eff only when the residuals do not follow the weights; the nu-e + "
             "IMD weights are a likelihood of each universe's own flux, so they may. sd_over_sigma_w_root_n_eff is, per "
             "cell, the bootstrap sd of the weighted mean universe integral over sigma_w / sqrt(n_eff), sigma_w^2 = "
             "sum w (x - mu)^2 / sum w (1 if the residuals do not follow the weights); delta_method_ratio is the same sd "
             "over sqrt(sum w^2 (x - mu)^2) / sum w, about 1 for any weights: a check that the bootstrap carries that "
             "term, not evidence about n_eff",
    "band": f"estimation uncertainty, not sensitivity: percentiles {list(PERCENTILES)} of each chi2 over the "
            f"{B_REPLICATES} replicates (numpy '{PERCENTILE_METHOD}'); basic: the reflected band 2 chi2_hat - q at the "
            f"mirrored percentile, chi2_hat Stage G's chi2 (the identity replicate); offset: median - chi2_hat, the "
            "bootstrap's estimate of chi2_hat's bias; halves: the percentiles from "
            f"replicates 1-{B_REPLICATES // 2} and {B_REPLICATES // 2 + 1}-{B_REPLICATES}, the Monte Carlo scatter. "
            "Neither band is an interval for the chi2 under the true correlations",
    "units": "every chi2 by Stage G's compare() in Stage G's absolute units, on C_total + C_resp + (C - C_0) + V_g with "
             "C the swapped flux block and C_0 S1's; shape-only adds Stage G's 100 f f^T; chi2 and ndf are unit-free; "
             "correlations are unit-free",
    "not": "no p-value, reading, claim or paper text",
    "not_citable_for": ["that the chi2 is insensitive to the flux correlations",
                        "that the PPFX or constraint correlations are correct",
                        "an interval for the chi2 under the true flux correlations"],
}


def report(control, name, ok, why="differs"):
    G.report(control, name, ok, why)


# ---------------------------------------------------------------- pure functions


def indices(seed: int = SEED, b: int = B_REPLICATES, n: int = N_UNIVERSES) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, n, size=(b, n))


def index_digest(idx: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(idx, dtype="<i4").tobytes()).hexdigest()


def replicate_block(X: np.ndarray, w: np.ndarray, i: np.ndarray) -> np.ndarray:
    """S1's flux rule on the resampled universes, each carrying its own weight."""
    return sa.mat_cov(X[i], w[i])


def n_eff(w: np.ndarray) -> float:
    return float(w.sum() ** 2 / (w ** 2).sum())


def correlation_swap(Cstar: np.ndarray, C0: np.ndarray) -> np.ndarray:
    """D0^1/2 rho* D0^1/2: the replicate's correlations on S1's variances, whose diagonal is C0's bit for bit, made
    exactly symmetric (mat_cov's product can differ from its transpose in the last bit)."""
    s0, ss = np.sqrt(np.diag(C0)), np.sqrt(np.diag(Cstar))
    out = Cstar / np.outer(ss, ss) * np.outer(s0, s0)
    out = (out + out.T) / 2
    np.fill_diagonal(out, np.diag(C0))
    return out


def chi2s(f: np.ndarray, g: np.ndarray, Vg: np.ndarray, C: np.ndarray, cells) -> tuple[float, float] | None:
    """Total and shape-only chi2 of f against g on ``cells`` under C + V_g, by Stage G's own compare() in Stage G's
    absolute representation, or None if a matrix is not positive definite. The shape-only matrix adds 100 f f^T, about
    1e4-1e5 times M's entries, so forming it rounds M at about 1e-11 relative; doing so in another representation
    (M relative to f, then 100 * 11^T) rounds differently and moved the chi2 by up to about 1e-10 (amendment 1)."""
    try:
        r = G.compare(f, g, Vg, C, list(cells), "3D")
    except np.linalg.LinAlgError:
        return None
    return r["total"]["chi2"], r["shape_only"]["chi2"]


def swapped(C_stage_g: np.ndarray, C: np.ndarray, C0: np.ndarray) -> np.ndarray:
    """Stage G's matrix with S1's flux block C0 replaced by C, as C_stage_g + (C - C0) in absolute units (amendment 1).
    Every chi2 of the run is taken on a matrix from here, and B6 checks each one against its parts."""
    return C_stage_g + (C - C0)


def correlation(C: np.ndarray, a: int, b: int) -> float:
    return float(C[a, b] / np.sqrt(C[a, a] * C[b, b]))


def band(values: np.ndarray, centre: float | None = None) -> dict:
    """The percentiles, minimum, maximum and halves of ``values``; with ``centre`` (chi2_hat), also the basic band
    2 * centre - q at the mirrored percentile (key p holds 2 centre - q_(100 - p)) and the offset median - centre."""
    v = np.asarray(values, float)
    h = len(v) // 2
    pct = lambda x: dict(zip((f"{q:g}" for q in PERCENTILES), np.percentile(x, PERCENTILES, method=PERCENTILE_METHOD).tolist()))
    out = {"percentiles": pct(v), "min": float(v.min()), "max": float(v.max()), "halves": [pct(v[:h]), pct(v[h:])]}
    if centre is not None:
        q = out["percentiles"]
        out["basic"] = {f"{p:g}": 2 * centre - q[f"{100 - p:g}"] for p in PERCENTILES}
        out["offset_median_minus_centre"] = q["50"] - centre
    return out


def mean_spread(X: np.ndarray, w: np.ndarray, idx: np.ndarray) -> dict[str, list[float]]:
    """Per cell, the bootstrap sd of the weighted mean universe integral over (a) sigma_w / sqrt(n_eff), with
    sigma_w^2 = sum w (x - mu)^2 / sum w, which is 1 when the residuals do not follow the weights, and (b) its
    linearized value sqrt(sum w^2 (x - mu)^2) / sum w, which is about 1 for any weights."""
    mu = (w[:, None] * X).sum(0) / w.sum()
    sw = np.sqrt((w[:, None] * (X - mu) ** 2).sum(0) / w.sum())
    lin = np.sqrt((w[:, None] ** 2 * (X - mu) ** 2).sum(0)) / w.sum()
    sd = np.array([(w[i][:, None] * X[i]).sum(0) / w[i].sum() for i in idx]).std(axis=0, ddof=1)
    return {"sd_over_sigma_w_root_n_eff": (sd / (sw / np.sqrt(n_eff(w)))).tolist(),
            "delta_method_ratio": (sd / lin).tolist()}


# ---------------------------------------------------------------- inputs


def universes(flux_dir: Path, s1j: dict, U: np.ndarray) -> np.ndarray:
    """B0's universe half: S1_Flux_0..99, each the digest S1's committed readout recorded, each named Flux:<i> in its
    own meta; their 16-cell integrals, in universe order."""
    rec = s1j.get("meta", {}).get("inputs_sha256", {})
    X, bad = [], []
    for u in range(N_UNIVERSES):
        p = flux_dir / f"S1_{sa.FLUX}_{u}.npz"
        if not p.exists():
            bad.append(f"{p.name} missing")
            continue
        got = sa.sha256(p)
        if got != rec.get(p.name):
            bad.append(f"{p.name} sha256 {got[:12]} != S1's {str(rec.get(p.name))[:12]}")
            continue
        with np.load(p, allow_pickle=False) as z:
            m = json.loads(str(z["meta"]))
            if (m.get("schema"), m.get("universe")) != ("s5p-universe/1", f"{sa.FLUX}:{u}"):
                bad.append(f"{p.name} is {m.get('universe')} ({m.get('schema')})")
                continue
        X.append(U @ sa.xs(p))
    n_rec = sum(1 for k in rec if k.startswith(f"S1_{sa.FLUX}_"))
    report("B0", f"the {N_UNIVERSES} Flux universes are S1's, by the digests its committed readout recorded, in order",
           not bad and n_rec == N_UNIVERSES, f"{bad[:3]}; S1 records {n_rec}")
    return np.array(X)


def weights(path: Path, s1j: dict, pins: dict) -> np.ndarray:
    """B0's weight half: the constraint file is the pin and S1's recorded one, and its sum and n_eff are S1's."""
    got = sa.sha256(path)
    rec = s1j.get("meta", {}).get("inputs_sha256", {}).get("constraint")
    report("B0", "the constraint file is the pin and the one S1 recorded", got == pins["constraint"] == rec,
           f"{got[:12]}, pin {pins['constraint'][:12]}, S1 {str(rec)[:12]}")
    w = G.sa_call("B0", sa.flux_weights, path)
    fw = s1j.get("meta", {}).get("flux_weights", {})
    ok = fw and abs(w.sum() - fw["sum"]) <= TOL * fw["sum"] and abs(n_eff(w) - fw["n_eff"]) <= TOL * fw["n_eff"]
    report("B0", f"the weights' sum {w.sum():.3f} and n_eff {n_eff(w):.2f} are S1's", bool(ok), f"S1 records {fw}")
    return w


# ---------------------------------------------------------------- main


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k, h in (("--definition", "nd-unfolding/pv-ladder/readouts/h2_definition.json"),
                 ("--s1-npz", "s1-20261024/s1_assembly.npz"), ("--s1-json", "the committed s1_assembly.json"),
                 ("--cmodel-json", "nd-unfolding/pv-ladder/readouts/cmodel_5d.json"),
                 ("--s5p-sums", "state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"),
                 ("--s5p-root", "s5p-20260926"), ("--g-readout", "the committed fd/readout/fd_g_readout.json"),
                 ("--extra-block", "Stage G's extra block npz"),
                 ("--flux-dir", "the committed s1/readout/s1_assembly/ (S1_Flux_0..99.npz)"),
                 ("--flux-constraint", "sorted_NuEConstraint_FHC_RHC_IMD.txt"), ("--out-json", "")):
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
    x = D.load(a, pins, predictions)                     # G-DIAG's D0-D5
    _, carries = x.comps[0][1]
    ff = np.outer(x.f, x.f)

    # B0. the inputs
    w = weights(a.flux_constraint, x.s1j, pins)
    X = universes(a.flux_dir, x.s1j, x.U)

    # B1. S1's flux block, rebuilt from the 100 universes with their weights, is S1's
    C0 = x.blocks_abs.get(f"band:{sa.FLUX}")
    members = sorted(b for b in x.blocks_abs if sa.group_of(b) == FLUX_GROUP)
    C1 = replicate_block(X, w, np.arange(N_UNIVERSES))
    scale = np.abs(C0).max() if C0 is not None else 0.0
    worst = float(np.abs(C1 - C0).max() / scale) if C0 is not None else float("inf")
    report("B1", f"the flux group is band:{sa.FLUX} alone, and it is rebuilt from the universes to {TOL:g} relative "
                 f"(worst {worst:.1e})", members == [f"band:{sa.FLUX}"] and worst <= TOL,
           f"members {members}, worst {worst:.3e}")

    # B2. swapped in, the rebuilt block reproduces Stage G's total and shape-only chi2 for every prediction. Every
    # chi2 is Stage G's compare() on Stage G's own matrix with the flux block's difference added, C_stage_g + (C - C0),
    # in absolute units: for the identity the difference is S1's block against its rebuild (B1)
    C_stage_g = x.Ct + (x.Cx if carries else 0)          # the matrix Stage G's reported comparison passed (D5)
    preds = []
    for spec in predictions:
        cells, g, Vg = x.integ[spec["name"]]
        preds.append((spec, [f"R{c:02d}" for c in cells], cells, g, Vg))
    worst = 0.0
    identity = {}
    # B6's parts: every S1 block but the flux one, C_model_abs = diag(f) S^T S diag(f) and C_resp, summed apart from
    # C_stage_g; each swapped matrix must equal parts + C to TOL relative (checked after the replicates)
    parts = sum(B for k, B in x.blocks_abs.items() if sa.group_of(k) != FLUX_GROUP) + (x.S.T @ x.S) * ff + \
        (x.Cx if carries else 0)
    p6 = [0.0]

    def checked(C):
        M = swapped(C_stage_g, C, C0)
        want = parts + C
        p6[0] = max(p6[0], float(np.abs(M - want).max() / np.abs(want).max()))
        return M

    M1 = checked(C1)
    for spec, names, cells, g, Vg in preds:
        got = chi2s(x.f, g, Vg, M1, cells)
        ref = x.grp[spec["name"]]
        want = (ref["total"]["chi2"], ref["shape_only"]["chi2"])
        rel = max(abs(g_ - w_) / abs(w_) for g_, w_ in zip(got, want)) if got else float("inf")
        worst = max(worst, rel)
        identity[spec["name"]] = {"chi2_stage_g": want[0], "shape_only_stage_g": want[1], "chi2_rebuilt": got[0] if got else None,
                                  "shape_only_rebuilt": got[1] if got else None, "relative_difference": rel}
    report("B2", f"the rebuilt block reproduces Stage G's total and shape-only chi2 for every prediction to {REPRO:g} "
                 f"(worst {worst:.1e})", worst <= REPRO, f"worst {worst:.3e}")

    # B3. the replicates are the declared ones
    idx = indices()
    dig = index_digest(idx)
    report("B3", f"the {B_REPLICATES} x {N_UNIVERSES} index matrix from seed {SEED} is the declared one",
           idx.shape == (B_REPLICATES, N_UNIVERSES) and dig == INDEX_SHA256, f"sha256 {dig}")

    # the replicates: B4 (every block has positive variances and every swapped M, the uniform one's included, is
    # positive definite) and B5 (the correlation variant keeps S1's flux variances bit for bit)
    p4, p5 = [], []
    chi = {v: {spec["name"]: [] for spec, *_ in preds} for v in VARIANTS}
    pair = [int(c[1:]) for c in PAIR]
    corr = {"flux_block": [], **{f"reported_matrix_{v}": [] for v in VARIANTS}}
    # C_total + C_resp relative to f without the flux group, for the pair's correlation in the reported matrix
    total_rest = x.Ct / ff - x.groups_rel[FLUX_GROUP] + (x.Cx_rel if carries else 0)
    for b, ib in enumerate(idx):
        Cs = replicate_block(X, w, ib)
        if not np.all(np.diag(Cs) > 0):
            p4.append(f"replicate {b}: a flux variance is not positive")
            continue
        corr["flux_block"].append(correlation(Cs, *pair))
        for v in VARIANTS:
            Cv = correlation_swap(Cs, C0) if v == "correlation" else Cs
            if v == "correlation" and not np.array_equal(np.diag(Cv), np.diag(C0)):
                p5.append(f"replicate {b}")
            Crel = Cv / ff
            corr[f"reported_matrix_{v}"].append(correlation(total_rest + Crel, *pair))
            Mv = checked(Cv)
            for spec, names, cells, g, Vg in preds:
                got = chi2s(x.f, g, Vg, Mv, cells)
                if got is None:
                    p4.append(f"replicate {b} {v} {spec['name']}")
                    continue
                chi[v][spec["name"]].append(got)
    Cu = sa.mat_cov(X)
    uniform = {}
    Mu = checked(Cu)
    for spec, names, cells, g, Vg in preds:
        got = chi2s(x.f, g, Vg, Mu, cells)
        if got is None:
            p4.append(f"uniform {spec['name']}")
            continue
        uniform[spec["name"]] = {"chi2": got[0], "shape_only": got[1]}
    report("B4", "every replicate's flux variances are positive and every swapped matrix, the uniform one's included, "
                 "is positive definite", not p4, f"{len(p4)}: {p4[:3]}")
    report("B5", "the correlation variant keeps S1's flux variances bit for bit in every replicate", not p5,
           f"{len(p5)}: {p5[:3]}")
    report("B6", f"every swapped matrix, the identity, {2 * B_REPLICATES} replicate variants and the uniform one, is "
                 f"S1's other blocks + C_model + C_resp + its flux block to {TOL:g} relative (worst {p6[0]:.1e})",
           p6[0] <= TOL, f"worst {p6[0]:.3e}")

    bands = {v: {spec["name"]: {"cells": names, "ndf": len(names), "chi2_stage_g": identity[spec["name"]]["chi2_stage_g"],
                                "shape_only_stage_g": identity[spec["name"]]["shape_only_stage_g"],
                                "total": band([c[0] for c in chi[v][spec["name"]]],
                                              identity[spec["name"]]["chi2_stage_g"]),
                                "shape_only": band([c[1] for c in chi[v][spec["name"]]],
                                                   identity[spec["name"]]["shape_only_stage_g"]), "label": LABEL}
                 for spec, names, *_ in preds} for v in VARIANTS}
    readout = {"schema": "fd-flux-boot-readout/1", "labels": LABELS,
               "controls_passed": ["D0", "D1", "D2", "D3", "D4", "D5", "B0", "B1", "B2", "B3", "B4", "B5", "B6"],
               "constants": {"replicates": B_REPLICATES, "universes": N_UNIVERSES, "seed": SEED,
                             "index_sha256": INDEX_SHA256, "percentiles": list(PERCENTILES),
                             "percentile_method": PERCENTILE_METHOD, "variants": list(VARIANTS), "pair": list(PAIR),
                             "reproduction": REPRO, "reported_matrix": f"{x.comps[0][1][0]} + V_g"},
               "identity": identity, "bands": bands,
               "correlation_band": {k: band(v) for k, v in corr.items()},
               "correlation_s1": {"flux_block": correlation(C0, *pair),
                                  "reported_matrix": correlation(total_rest + C0 / ff, *pair)},
               "n_eff": {"s1": n_eff(w), "sum_w": float(w.sum()),
                         **{k: dict(zip((f"R{c:02d}" for c in range(N_CELLS)), v))
                            for k, v in mean_spread(X, w, idx).items()}},
               "uniform": {"n_eff": float(N_UNIVERSES), "predictions": uniform,
                           "pair_correlation_flux_block": correlation(Cu, *pair), "label": LABELS["uniform"]},
               "inputs_sha256": {**pins, "definition": sa.DEFINITION_SHA256, "extra_block": a.extra_block_sha256,
                                 **{p["name"]: p["sha256"] for p in predictions},
                                 "flux_universes": "S1's committed readout meta.inputs_sha256 (S1_Flux_0..99), checked by B0"},
               "code_sha256": {"fd_flux_boot.py": sa.sha256(Path(__file__).resolve()),
                               "fd_g_diag.py": sa.sha256(Path(D.__file__).resolve()),
                               "fd_g_compare.py": sa.sha256(Path(G.__file__).resolve()),
                               "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve())},
               "argv": [str(v) for v in sys.argv]}
    counter = [0]
    readout = D.finite(readout, counter)
    readout["non_finite_written_as_null"] = counter[0]
    tmp = a.out_json.with_name(a.out_json.name + ".partial")
    tmp.write_text(json.dumps(readout, indent=1, allow_nan=False) + "\n")
    os.replace(tmp, a.out_json)
    print(f"[3D] every line below: {LABEL}", flush=True)
    for v in VARIANTS:
        for name, r in bands[v].items():
            q = r["total"]["percentiles"]
            bq = r["total"]["basic"]
            print(f"[3D] {v:11s} {name:10s}: chi2 {r['chi2_stage_g']:.2f}/{r['ndf']}; replicates 16-84 % "
                  f"[{q['16']:.2f}, {q['84']:.2f}], 2.5-97.5 % [{q['2.5']:.2f}, {q['97.5']:.2f}], offset of the median "
                  f"{r['total']['offset_median_minus_centre']:+.2f}; basic 16-84 % [{bq['16']:.2f}, {bq['84']:.2f}]; "
                  f"uniform {uniform[name]['chi2']:.2f}", flush=True)
    r = list(readout["n_eff"]["sd_over_sigma_w_root_n_eff"].values())
    print(f"[3D] n_eff {n_eff(w):.2f}; bootstrap sd of the weighted mean over sigma_w / sqrt(n_eff), median over cells "
          f"{float(np.median(r)):.3f} (range {min(r):.3f}-{max(r):.3f})", flush=True)
    print(json.dumps({"wrote": str(a.out_json), "sha256": sa.sha256(a.out_json)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())

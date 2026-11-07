#!/usr/bin/env python3
"""1B staged method coverage, stage 1 (state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md
sections 4-9, revision 2; for binding 2): pseudo-data at a held-out truth T with every uncertainty group drawn, the
covariance remade at T by S1's procedure, and the grading against a null matched to the draws.

Roles of ``unfold`` (one product per item, one lane):

* ``central``: T's pseudo-data at their means (d_T, nominal response) unfolded with the nominal MC, with T's truth;
  ``central``, ``seed`` and ``block`` unfold by S1's universe path (``s5p_numerics.unfold_one``, float32), the toys
  by ``s5n_pseudo.unfold_negweight`` (the toy and derivation path); S1's G4 found the two equal on the data's CV;
* ``seed``: the same at estimator seed ``SEED_CHECK``; it must equal ``central`` bitwise (the seed block, section 4.3);
* ``block``: d_T unfolded with universe u's MC, the arrays S1's blocks used (``s5p_universe.universe_inputs`` over
  ``fd_1b_inv.universe_weights(..., "zero")``; the flux universes' fluxes from the staged flux table);
* ``stat``: replica b of ONE Poisson realization of T by set A's procedure (``s5p_numerics.jittered`` at 100 + b,
  ``s5n_pseudo.bootstrap_replica`` at b, the refinement refit, float64 coordinates, ``s5p_numerics.unfold_one``);
* ``toy``: one coverage toy. The nature is ``fd_1b_toys.draw`` at the seed, composed by ``compose`` (section 4.2),
  the Poisson pseudo-data of ``fd_1b_toys.build_full`` over it at T, the nominal MC with set A's MC and template
  streams, unfolded by ``s5n_pseudo.unfold_negweight``; the product keeps the nature's own truth;
* ``control``: a procedure control on the real data, bitwise against S1's or Stage 0's product (section 9);
* ``capture``: the data's central unfold with the final push weights kept (section 6); it must equal S1's central
  product bitwise.

Other subcommands: ``stage-flux`` (the flux-universe table read once through O_NOATIME into an npz), ``receipt``
(section 4.2's bank counts, N1's single ratios, and N1's composite over every possible and every declared draw,
before the bulk; login node), ``walls`` (S1-0's re-price trigger), ``n1`` (the toys' own N1 record at T, read before
any grading), ``null`` (the draw-matched null at T from the remade products, before any toy is opened; it records
what C_T is made from) and ``readout`` (section 5's grading and section 7's readouts at T, refusing inputs the null
was not made from). Every pscratch input not made by this lane is read through ``fd_1b_inv``'s O_NOATIME
readers; a moved atime is reported and exits with 8 set.

MEASURES: the declared products and readouts. CANNOT AUTHORIZE: a change to the reported covariance, an interval or a
claim; any verdict outside FD-1B-STAGED-DECLARATION.md section 5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import resource
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_inv as inv  # noqa: E402
import fd_1b_null as fn  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "fd-1b-mc/1"
TRUTHS = {"g18": "genie_v3_g18", "ar23": "genie_v3_ar23", "plugin": "plugin"}
TOY_SEEDS = {"g18": range(3_620_000, 3_620_300), "ar23": range(3_630_000, 3_630_300),
             "plugin": range(3_640_000, 3_640_300)}
STAT_SEED = {"g18": 3_621_000, "ar23": 3_631_000, "plugin": 3_641_000}
STAT_REPLICAS = sa.STAT_REPLICAS                     # 1..50, set A's
JITTER_OFFSET = 100                                  # set A's products are data_b<b>_j<100+b>
SEED_CHECK = 45
CONTROLS = ("setA_b1", "MaRES_0", "Flux_0", "GEANT_Pion_0")
ROLES = ("central", "seed", "block", "stat", "toy", "control", "capture")
N1_BOUND = 10.0                                      # N1: a composite or single ratio above this is counted
N1_CANDIDATE_CAP = 250_000                           # rows per array the exact pass over the declared draws holds
UNIT_SECONDS = 1062.0
RSS_LIMIT_KIB = inv.RSS_LIMIT_KIB
# S1-0 (declaration section 8): its eight items; the eighth is the capture with the plug-in, AR23's first toy without
PILOT_COMMON = (("control", "setA_b1"), ("control", "MaRES_0"), ("control", "Flux_0"), ("control", "GEANT_Pion_0"),
                ("central", "g18"), ("toy", "g18:3620000"), ("stat", "ar23:1"))
PILOT = {True: PILOT_COMMON + (("capture", "data"),), False: PILOT_COMMON + (("toy", "ar23:3630000"),)}


class Refusal(RuntimeError):
    pass


def via_noatime(reader, path: Path):
    """``reader`` (a bound function that opens a path itself) on a private copy of ``path`` whose bytes were read once
    through O_NOATIME. The reader runs unchanged, and the source's access time is left alone. This is the audit's D1
    on #679: ``fd_1b_score.load_s1`` and ``s1_assemble.flux_weights`` read their files plainly."""
    with inv.open_noatime(path) as fh:
        data = fh.read()
    with tempfile.TemporaryDirectory(prefix="fd1b-mc-") as d:
        copy = Path(d) / Path(path).name
        copy.write_bytes(data)
        return reader(copy)


# ------------------------------------------------------------------------------------------------- composition


def universe_dir(tag: str, bank: Path, det_dir: Path) -> Path:
    return det_dir if tag.rpartition("_")[0] in sa.DETECTOR_BANDS else bank


def compose(inputs: dict, bkg: dict, bank_cv, tags: list[str], load, flux: np.ndarray | None) -> tuple[dict, dict, dict]:
    """Section 4.2's rule, as amended in binding 2 for the denominator. ``tags`` is the draw's universes in the draw's
    order and ``load(tag)`` their weights as ``fd_1b_inv.universe_weights(..., "zero")`` loads them; the universes
    are streamed, one in memory at a time. For each per-row array a: a_D = a_u1 * prod_{j>=2} a_uj / a_CV where
    a_CV != 0, and a_u1 + sum_{j>=2} a_uj where a_CV == 0. The denominator composes the same way per cell, over each
    universe's own histogram (``universe_inputs``' denom_nd). The flux is the one flux universe's. For one universe
    every array is ``universe_inputs``' exactly. N1's record: per array, max over rows of |a_D| / max_j |a_uj|."""
    cv = _cv_arrays(inputs, bkg)
    ui, ub = dict(inputs), dict(bkg)
    if not tags:
        return ui, ub, {"universes": []}
    acc, peak, fluxes = {}, {}, []
    nz = {k: v != 0 for k, v in cv.items()}
    for j, tag in enumerate(tags):
        single, phi = _single(inputs, bkg, bank_cv, tag, load(tag), flux)
        if phi is not None:
            fluxes.append(phi)
        for k, a_u in single.items():
            if j == 0:
                acc[k], peak[k] = a_u.copy(), np.abs(a_u)
                continue
            m = nz[k]
            acc[k][m] = acc[k][m] * (a_u[m] / cv[k][m])
            acc[k][~m] = acc[k][~m] + a_u[~m]
            np.maximum(peak[k], np.abs(a_u), out=peak[k])
        del single
    if len(fluxes) > 1:
        raise Refusal("a draw holds more than one flux universe")
    stats = {}
    for k in acc:
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(peak[k] > 0, np.abs(acc[k]) / peak[k], np.where(acc[k] == 0, 1.0, np.inf))
        stats[k] = {"max_composite_over_max_single": float(np.max(r)), "rows_above_bound": int(np.sum(r > N1_BOUND))}
    ui["w_truth"], ui["w_reco"], ui["denom_nd"] = acc["wt"], acc["wr"], acc["denom"]
    ub["bkg_w"] = acc["bkgw"]
    if fluxes:
        ui["flux"] = fluxes[0]
    return ui, ub, {"universes": list(tags), "n1": stats}


def _cv_arrays(inputs: dict, bkg: dict) -> dict:
    return {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
            "bkgw": np.asarray(bkg["bkg_w"], float), "denom": np.asarray(inputs["denom_nd"], float)}


def _single(inputs: dict, bkg: dict, bank_cv, tag: str, w: dict, flux) -> tuple[dict, np.ndarray | None]:
    """One universe's per-row arrays (and per-cell denominator) as ``universe_inputs`` gives them; a Flux universe's
    with its staged Phi_u, which is returned beside them."""
    band, _, idx = tag.rpartition("_")
    u_i, u_b, _ = s5p_universe.universe_inputs(inputs, bkg, bank_cv, w, band, idx, None) if band != sa.FLUX \
        else _flux_universe_inputs(inputs, bkg, bank_cv, w, idx, flux)
    single = {"wt": np.asarray(u_i["w_truth"], float), "wr": np.asarray(u_i["w_reco"], float),
              "bkgw": np.asarray(u_b["bkg_w"], float), "denom": np.asarray(u_i["denom_nd"], float)}
    return single, (u_i["flux"] if band == sa.FLUX else None)


def declared_draws(flux_p: np.ndarray, groups: dict) -> list[list[str]]:
    """Every declared toy's universes, for all three truths, in each draw's own order."""
    return [draw_universes(toys.draw_for_seed(s, flux_p, groups)) for t in TRUTHS for s in TOY_SEEDS[t]]


def composite_n1(inputs: dict, bkg: dict, bank_cv, load, flux, draws: list[list[str]]) -> dict:
    """N1 for the composite, before the bulk (the audit's B2 on #673), per array.

    Every draw holds one universe of every band. Where a_CV != 0, |a_D| / max_j |a_uj| = prod_j r_j / max_j r_j
    with r_j = |a_uj / a_CV|. Its largest value over ALL draws is exactly prod_b R_b / max_b R_b, R_b the largest r
    over band b's universes. Where a_CV == 0 it is |sum_j a_uj| / max_j |a_uj|, at most the number of bands with a
    non-zero weight there. Rows whose bound exceeds N1_BOUND are then evaluated exactly over ``draws`` (a second
    pass), up to N1_CANDIDATE_CAP rows per array. More rows than that are not evaluated, and that stops the bulk as
    a count above the bound does."""
    cv = _cv_arrays(inputs, bkg)
    nz = {k: v != 0 for k, v in cv.items()}
    scale = {k: np.where(nz[k], np.abs(v), 1.0) for k, v in cv.items()}
    by_band: dict[str, list[str]] = {}
    for t in toys.s1_universes():
        by_band.setdefault(t.rpartition("_")[0], []).append(t)
    logsum = {k: np.zeros(v.shape) for k, v in cv.items()}
    top = {k: np.zeros(v.shape) for k, v in cv.items()}
    nonzero = {k: np.zeros(v.shape) for k, v in cv.items()}
    for tags in by_band.values():
        R = {k: np.zeros(v.shape) for k, v in cv.items()}
        for t in tags:
            single, _ = _single(inputs, bkg, bank_cv, t, load(t), flux)
            for k, a in single.items():
                np.maximum(R[k], np.abs(a) / scale[k], out=R[k])
        for k in cv:
            with np.errstate(divide="ignore"):
                logsum[k] += np.log(R[k])
            np.maximum(top[k], R[k], out=top[k])
            nonzero[k] += R[k] > 0
    arrays, rows = {}, {}
    for k in cv:
        with np.errstate(divide="ignore", invalid="ignore"):
            sup = np.where(nz[k], np.where(top[k] > 0, np.exp(logsum[k] - np.log(np.where(top[k] > 0, top[k], 1.0))),
                                           0.0), nonzero[k])
        rows[k] = np.flatnonzero(sup > N1_BOUND)
        arrays[k] = {"all_draws_max": float(sup.max()), "all_draws_rows_above": int(rows[k].size)}
    exact = {k: i for k, i in rows.items() if 0 < i.size <= N1_CANDIDATE_CAP}
    for k, i in rows.items():
        arrays[k]["declared"] = ({"evaluated": True, "rows": 0, "max": None, "rows_above": 0} if i.size == 0 else
                                 {"evaluated": False, "rows": int(i.size), "max": None, "rows_above": None})
    if exact:
        col = {t: c for c, t in enumerate(toys.s1_universes())}
        V = {k: np.zeros((i.size, len(col))) for k, i in exact.items()}
        for t, c in col.items():
            single, _ = _single(inputs, bkg, bank_cv, t, load(t), flux)
            for k, i in exact.items():
                a = single[k][i]
                V[k][:, c] = np.where(nz[k][i], np.abs(a) / scale[k][i], a)
        for k, i in exact.items():
            m, worst = nz[k][i], np.zeros(i.size)
            for tags in draws:
                v = V[k][:, [col[t] for t in tags]]
                peak = np.max(np.abs(v), axis=1)
                comp = np.where(m, np.prod(np.abs(v), axis=1), np.abs(v.sum(axis=1)))
                with np.errstate(divide="ignore", invalid="ignore"):
                    r = np.where(peak > 0, comp / peak, np.where(comp == 0, 1.0, np.inf))
                np.maximum(worst, r, out=worst)
            arrays[k]["declared"] = {"evaluated": True, "rows": int(i.size), "max": float(worst.max()),
                                     "rows_above": int(np.sum(worst > N1_BOUND))}
    stop = any(not v["declared"]["evaluated"] or v["declared"]["rows_above"] for v in arrays.values())
    return {"bound": N1_BOUND, "n_draws": len(draws), "candidate_cap": N1_CANDIDATE_CAP, "arrays": arrays,
            "stop": stop}


def _flux_universe_inputs(inputs, bkg, bank_cv, w, idx, flux: np.ndarray | None):
    """``universe_inputs`` for a Flux universe, with Phi_u from the staged table instead of the ROOT file."""
    if flux is None:
        raise Refusal("a Flux universe needs the staged flux table")
    ui, ub, info = s5p_universe.universe_inputs(inputs, bkg, bank_cv, w, "Interaction", idx, None)
    ui = dict(ui)
    ui["flux"] = np.asarray(flux[int(idx)], float)
    info = dict(info, flux_ratio_mean=float(np.mean(ui["flux"] / np.asarray(inputs["flux"], float))))
    return ui, ub, info


def flux_on_grid(table: dict, inputs: dict) -> np.ndarray:
    """Every universe's Phi_u on the analysis pT grid, by ``flux_universe``'s own remap and guards."""
    import flux_universe
    pt = np.asarray(inputs["edges"][0], float)
    cv = np.asarray(inputs["flux"], float)
    out = []
    with _staged_table(table):
        for u in range(np.asarray(table["hFluxUniv"]).shape[0]):
            out.append(flux_universe.flux_universe_bins("staged", u, pt, cv))
    return np.array(out)


@contextmanager
def _staged_table(table: dict):
    """``flux_universe.read_flux_universe_table`` reads a path; point it at the staged arrays for this block."""
    import flux_universe
    orig = flux_universe.read_flux_universe_table
    flux_universe.read_flux_universe_table = lambda path: (np.asarray(table["hFluxCV"], float),
                                                            np.asarray(table["hFluxUniv"], float))
    try:
        yield
    finally:
        flux_universe.read_flux_universe_table = orig


def draw_universes(d: dict) -> list[str]:
    """A ``fd_1b_toys.draw`` record as universe tags, in the draw's order: flux, the bands sorted, the detectors."""
    tags = [] if d.get("flux") is None else [f"{sa.FLUX}_{d['flux']}"]
    tags += [d["model"][b] for b in sorted(d.get("model", {}))]
    tags += [f"{b}_{d['detector'][b]}" for b in toys.DETECTOR_DRAW_ORDER if b in d.get("detector", {})]
    return tags


# ------------------------------------------------------------------------------------------------------ truths


def truth_ratio(truth: str, prep: Path | None) -> tuple[dict | None, str | None]:
    """F1's bridged ratio for G18 or AR23, read through O_NOATIME, its digest the committed F1 prep sum's."""
    name = TRUTHS[truth]
    if truth == "plugin":
        return None, None
    if prep is None:
        raise Refusal(f"truth {truth} needs --prep")
    path = prep / toys.TRUTHS[name]
    got = inv.sha256_noatime(path)
    if got != toys.committed_ratio_sha256(name):
        raise Refusal(f"{path}: sha256 {got} is not the committed F1 prep digest")
    with inv.open_noatime(path) as fh:
        ratio = json.loads(fh.read().decode())
    if ratio.get("schema") != "s5e-shape-ratio/1":
        raise Refusal(f"{path}: schema {ratio.get('schema')}")
    return ratio, got


def truth_weight(truth: str, inputs: dict, ratio: dict | None, push: np.ndarray | None) -> np.ndarray:
    """r for T: F1's ratio at amplitude 1 (``s5n_pseudo.truth_weight("ratio_nd", ...)``), or the plug-in's push
    weights on truth-passing rows and 1 elsewhere. Both enter ``fd_1b_toys.build_full`` the same way: reco weights
    x r, the truth through ``s5n_pseudo.true_xsec`` with the CV completeness kept per cell (so at the plug-in,
    x_T is the data's unfolded result by ``s5c_unfold.unfold``'s own formula: section 6 (b))."""
    if truth == "plugin":
        if push is None:
            raise Refusal("the plug-in truth needs the capture's push weights")
        m = np.asarray(inputs["pass_truth"], bool)
        if push.size != int(m.sum()):
            raise Refusal("the push weights do not match the truth-passing rows")
        r = np.ones(m.size)
        r[m] = push
        return r
    return np.asarray(s5n_pseudo.truth_weight("ratio_nd", inputs, 1.0, ratio), float)


def with_mc(exp: dict, ui: dict, ub: dict) -> dict:
    """``fd_1b_inv.with_mc`` (the unfolding MC's weights, denominator and template) plus the unfolding MC's flux: an
    experiment carries the flux its unfold divides by, and a Flux universe's MC divides by its own Phi_u (S1)."""
    out = inv.with_mc(exp, ui, ub)
    out["flux"] = ui["flux"]
    return out


# ------------------------------------------------------------------------------------------------- experiments


def mean_experiment(inputs: dict, bkg: dict, r: np.ndarray) -> tuple[dict, np.ndarray]:
    """d_T: every Poisson draw at its mean, the nominal response, truth r; the nominal MC unfolds it."""
    ones_s, ones_b = np.ones(inputs["w_reco"].shape[0]), np.ones(bkg["bkg_w"].shape[0])
    exp, x_true, _ = toys.build_full(inputs, bkg, r, ones_s, ones_b, None, expectation=True)
    return exp, x_true


def toy_experiment(inputs: dict, bkg: dict, ui: dict, ub: dict, r: np.ndarray, seed: int) -> tuple[dict, np.ndarray]:
    """One toy: Poisson pseudo-data of the nature (ui, ub) at truth r, the nominal MC with set A's streams."""
    ones_s, ones_b = np.ones(ui["w_reco"].shape[0]), np.ones(ub["bkg_w"].shape[0])
    exp, x_true, _ = toys.build_full(ui, ub, r, ones_s, ones_b, seed, expectation=False)
    exp = with_mc(exp, inputs, bkg)
    return toys.mc_template_streams(exp, seed), x_true


def stat_experiment(inputs: dict, bkg: dict, r: np.ndarray, seed: int | None, b: int) -> dict:
    """Set A's replica b: coordinates jittered at 100 + b, the experiment (one Poisson realization of T at ``seed``,
    or the real data when ``seed`` is None), then the bootstrap replica b."""
    ji, jb = s5p_numerics.jittered(inputs, bkg, JITTER_OFFSET + b)
    if seed is None:
        exp = s5n_pseudo.build_data(ji, jb)
    else:
        ones_s, ones_b = np.ones(ji["w_reco"].shape[0]), np.ones(jb["bkg_w"].shape[0])
        exp, _, _ = toys.build_full(ji, jb, r, ones_s, ones_b, seed, expectation=False)
    return s5n_pseudo.bootstrap_replica(exp, b)


class Capture:
    """An ``unfold_fn`` that runs ``s5c_unfold.unfold`` unchanged and keeps a copy of the push weights it computes."""

    def __init__(self):
        self.push = None

    def __call__(self, unf_in, config, seed, threads, iters):
        orig = s5c_unfold.onc.omnifold_loop

        def loop(*a, **k):
            pull, push = orig(*a, **k)
            self.push = np.array(push, copy=True)
            return pull, push
        s5c_unfold.onc.omnifold_loop = loop
        try:
            return s5c_unfold.unfold(unf_in, config, seed, threads, iters)
        finally:
            s5c_unfold.onc.omnifold_loop = orig


# ---------------------------------------------------------------------------------------------------- the job


def product_name(tag: str, truth: str, role: str, item: str) -> str:
    return f"{tag}_{truth}_{role}_{item.replace(':', '_')}.npz"


def _load_world(a) -> dict:
    npz_sha, bkg_sha = inv.sha256_noatime(a.npz), inv.sha256_noatime(a.bkg)
    if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):
        raise Refusal(f"input digests {npz_sha} / {bkg_sha} are not the declared ones")
    if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:
        raise Refusal("pins file digest differs")
    with inv.open_noatime(a.pins) as fh:
        pins = json.loads(fh.read().decode())
    toys.check_pins(pins, a.bank, a.detector_dir)
    inputs = inv.load_inputs(a.npz)
    bz = inv.load_npz(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    bank_cv = inv.load_npz(a.bank / "cv.npz", allow_pickle=True)
    flux = None
    if a.flux_table is not None:
        if inv.sha256_noatime(a.flux_table) != a.expect_flux_table_sha256:
            raise Refusal("the staged flux table's digest differs")
        flux = flux_on_grid(inv.load_npz(a.flux_table), inputs)
    return {"npz_sha": npz_sha, "bkg_sha": bkg_sha, "pins": pins, "inputs": inputs, "bkg": bkg, "bank_cv": bank_cv,
            "alignment": s5p_universe.check_alignment(bank_cv, inputs, bkg), "flux": flux,
            "groups": toys.interaction_groups(a.bank)}


def _weights(world: dict, a, tag: str) -> dict:
    wdir = universe_dir(tag, a.bank, a.detector_dir)
    for k in s5p_universe.weight_keys(wdir, tag):
        p = wdir / f"{tag}_{k}.npy"
        if inv.sha256_noatime(p) != world["pins"]["files"][str(p)]["sha256"]:
            raise Refusal(f"{p}: digest differs from the pins file")
    return inv.universe_weights(wdir, tag, "zero")


def _unfold(exp: dict, threads: int, seed: int = toys.ESTIMATOR_SEED, unfold_fn=None):
    xs, ev = s5n_pseudo.unfold_negweight(exp, seed, threads, toys.ITERS, None, None, unfold_fn)
    return np.asarray(xs, float), ev


def run_item(a, world: dict, role: str, item: str, unfold_fn=None) -> tuple[dict, dict]:
    """One product's arrays and role-specific meta."""
    inputs, bkg = world["inputs"], world["bkg"]
    truth = a.truth
    ratio, ratio_sha = truth_ratio(truth, a.prep) if role not in ("control", "capture") else (None, None)
    push = None
    if truth == "plugin" and role not in ("control", "capture"):
        if a.push is None or inv.sha256_noatime(a.push) != a.expect_push_sha256:
            raise Refusal("the plug-in truth needs --push with its declared digest")
        push = np.asarray(inv.load_npz(a.push)["push"], float)
    arrays, meta = {}, {"truth_ratio_sha256": ratio_sha}
    if role in ("central", "seed", "block"):
        exp, x_true = mean_experiment(inputs, bkg, truth_weight(truth, inputs, ratio, push))
        seed = SEED_CHECK if role == "seed" else toys.ESTIMATOR_SEED
        if role == "block":
            ui, ub, info = compose(inputs, bkg, world["bank_cv"], [item], lambda t: _weights(world, a, t), world["flux"])
            exp = with_mc(exp, ui, ub)
            meta["universe_info"] = info
        xs, ev = (unfold_fn or _unfold_s1)(exp, a.threads, seed)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": np.asarray(x_true, float).ravel(order="C")}
        meta.update(ev)
    elif role == "stat":
        b = int(item)
        if b not in STAT_REPLICAS:
            raise Refusal(f"stat replica {b} is not one of set A's")
        exp = stat_experiment(inputs, bkg, truth_weight(truth, inputs, ratio, push), STAT_SEED[truth], b)
        xs, ev = (unfold_fn or _unfold_one64)(exp, a.threads)
        arrays = {"xsec_flat": np.asarray(xs, float).ravel(order="C")}
        meta.update(ev, stat_seed=STAT_SEED[truth], bootstrap_seed=b, jitter_seed=JITTER_OFFSET + b)
    elif role == "toy":
        seed = int(item)
        if seed not in TOY_SEEDS[truth]:
            raise Refusal(f"toy seed {seed} is outside {truth}'s declared range")
        d = toys.draw_for_seed(seed, via_noatime(toys.flux_probabilities, a.flux_constraint), world["groups"])
        tags = draw_universes(d)
        ui, ub, info = compose(inputs, bkg, world["bank_cv"], tags, lambda t: _weights(world, a, t), world["flux"])
        exp, x_true = toy_experiment(inputs, bkg, ui, ub, truth_weight(truth, inputs, ratio, push), seed)
        x_true = np.asarray(x_true, float)
        if not np.all(np.isfinite(x_true)):
            raise Refusal("a non-finite truth")
        xs, ev = (unfold_fn or _unfold)(exp, a.threads)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": x_true.ravel(order="C")}
        meta.update(ev, draw=d, universe_info=info)
    elif role == "control":
        if item not in CONTROLS:
            raise Refusal(f"{item} is not a declared procedure control")
        if item == "setA_b1":
            xs, ev = (unfold_fn or _unfold_one64)(stat_experiment(inputs, bkg, None, None, 1), a.threads)
        else:
            ui, ub, info = compose(inputs, bkg, world["bank_cv"], [item], lambda t: _weights(world, a, t), world["flux"])
            xs, ev = (unfold_fn or _unfold_one32)(s5n_pseudo.build_data(ui, ub), a.threads)
        arrays = {"xsec_flat": np.asarray(xs, float).ravel(order="C")}
        meta.update(ev)
    elif role == "capture":
        cap = Capture()
        xs, ev = (unfold_fn or _unfold_one32)(s5n_pseudo.build_data(inputs, bkg), a.threads, cap)
        if cap.push is None and unfold_fn is None:
            raise Refusal("the capture kept no push weights")
        arrays = {"xsec_flat": np.asarray(xs, float).ravel(order="C"),
                  "push": np.asarray(cap.push if cap.push is not None else [], float)}
        meta.update(ev)
    else:
        raise Refusal(f"role {role!r}")
    if not np.all(np.isfinite(arrays["xsec_flat"])):
        raise Refusal("a non-finite unfolded value")
    return arrays, meta


def _unfold_s1(exp, threads, seed=toys.ESTIMATOR_SEED, unfold_fn=None):
    """S1's universe path (``s5p_universe``: ``s5p_numerics.unfold_one`` in float32): the remade blocks and the
    central value at T use it, so the procedure controls test the very path the blocks run."""
    xs, ev = s5p_numerics.unfold_one(exp, np.float32, seed, threads, toys.ITERS, unfold_fn)
    return np.asarray(xs, float), ev


def _unfold_one32(exp, threads, unfold_fn=None):
    return s5p_numerics.unfold_one(exp, np.float32, toys.ESTIMATOR_SEED, threads, toys.ITERS, unfold_fn)


def _unfold_one64(exp, threads, unfold_fn=None):
    return s5p_numerics.unfold_one(exp, np.float64, toys.ESTIMATOR_SEED, threads, toys.ITERS, unfold_fn)


def code_digests() -> dict:
    return {**toys.code_digests(), **{p.name: s5n_pseudo.sha256_path(p) for p in (
        Path(__file__).resolve(), Path(inv.__file__).resolve(), Path(fn.__file__).resolve(),
        Path(s5p_numerics.__file__).resolve(), _ND / "s5e_trace.py", _ND / "flux_universe.py")}}


def run_unfold(a, unfold_fn=None) -> int:
    inv.OPENED.clear()
    s5e_candidate.install(toys.CONFIG)
    if a.role not in ROLES:
        raise Refusal(f"role {a.role!r}")
    if (a.role in ("control", "capture")) != (a.truth == "data"):
        raise Refusal("the control and capture roles run on the data (--truth data), and only they")
    world = _load_world(a)
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for item in a.items.split(","):
        target = a.out / product_name(a.tag, a.truth, a.role, item)
        if target.exists():
            continue
        toys.check_pins(world["pins"], a.bank, a.detector_dir)
        t1 = time.time()
        arrays, extra = run_item(a, world, a.role, item, unfold_fn)
        meta = {"schema": SCHEMA, "truth": a.truth, "role": a.role, "item": item, "config": toys.CONFIG,
                "iters": toys.ITERS, "estimator_seed": SEED_CHECK if a.role == "seed" else toys.ESTIMATOR_SEED,
                "threads": a.threads, **extra, "input_npz_sha256": world["npz_sha"], "bkg_dump_sha256": world["bkg_sha"],
                "pins_sha256": a.expect_pins_sha256, "flux_table_sha256": a.expect_flux_table_sha256,
                "push_sha256": a.expect_push_sha256, "alignment": world["alignment"], "code_sha256": code_digests(),
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t1, 3),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "numpy_version": np.__version__}
        status |= s5n_pseudo.write_product(target, arrays, meta)
        print(json.dumps({"out": target.name, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    chk = inv.atime_check()
    (a.out / f"atime-{a.truth}-{a.role}-{os.environ.get('SLURM_JOB_ID', 'local')}-{os.getpid()}.json").write_text(
        json.dumps(chk, indent=1) + "\n")
    if chk["moved"]:
        print(f"[fd-1b-mc] DEVIATION: atime moved on {chk['moved']}", file=sys.stderr)
        return status | 8
    return status


# --------------------------------------------------------------------------------------- staging and receipts


def stage_flux(root_path: Path, out: Path) -> dict:
    """The flux-universe table, read ONCE through O_NOATIME into memory and parsed there (ROOT's TMemFile), written
    as the npz ``flux_universe.read_flux_universe_table`` accepts. The source's digest is recorded."""
    with inv.open_noatime(root_path) as fh:
        raw = fh.read()
    import ROOT  # noqa: N813
    buf = ROOT.TMemFile("flux_staged.root", ROOT.TMemFile.ZeroCopyView_t(raw, len(raw)))
    cv_h, un_h = buf.Get("hFluxCV"), buf.Get("hFluxUniv")
    if not cv_h or not un_h:
        raise Refusal(f"{root_path}: hFluxCV or hFluxUniv missing")
    n_ref, n_univ = cv_h.GetNbinsX(), un_h.GetNbinsY()
    cv = np.array([cv_h.GetBinContent(i + 1) for i in range(n_ref)])
    univ = np.array([[un_h.GetBinContent(i + 1, u + 1) for i in range(n_ref)] for u in range(n_univ)])
    np.savez(out, hFluxCV=cv, hFluxUniv=univ, source=str(root_path), source_sha256=hashlib.sha256(raw).hexdigest())
    return {"out": str(out), "source_sha256": hashlib.sha256(raw).hexdigest(), "n_ref": n_ref, "n_univ": n_univ}


def receipt(a) -> dict:
    """Section 4.2's counts and N1's single-universe ratios, per universe and array, over the real bank; whether each
    detector universe's denominator histogram equals the CV's; and N1's composite over every possible and every
    declared draw (``composite_n1``), whose ``stop`` holds the bulk."""
    inv.OPENED.clear()
    world = _load_world(a)
    flux_p = via_noatime(toys.flux_probabilities, a.flux_constraint)
    inputs = world["inputs"]
    cv = {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
          "bkgw": np.asarray(world["bkg"]["bkg_w"], float)}
    rows = {}
    tags = [f"{sa.FLUX}_{i}" for i in range(sa.EXPECT[sa.FLUX])] + toys.s1_universes()
    for tag in dict.fromkeys(tags):
        wdir = universe_dir(tag, a.bank, a.detector_dir)
        raw = inv.universe_weights(wdir, tag, "keep")
        rec = {}
        for k, key in (("wt", "wt"), ("wr", "wr"), ("bkgw", "bkgw")):
            u = raw[key]
            fin = np.isfinite(u)
            c = cv[k]
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = np.where((c != 0) & fin, np.abs(u / np.where(c != 0, c, 1.0)), 0.0)
            rec[k] = {"cv_zero_u_nonzero": int(np.sum((c == 0) & fin & (u != 0))), "cv_negative": int(np.sum(c < 0)),
                      "u_negative": int(np.sum(fin & (u < 0))), "u_nonfinite": int(np.sum(~fin)),
                      "max_abs_ratio": float(ratio.max()), "rows_ratio_above_bound": int(np.sum(ratio > N1_BOUND))}
        if "denom_nd" in raw:
            rec["denom_nd_equals_cv"] = bool(np.array_equal(np.asarray(raw["denom_nd"], float),
                                                            np.asarray(inputs["denom_nd"], float)))
        rows[tag] = rec
    worst = {k: max(r[k]["max_abs_ratio"] for r in rows.values()) for k in ("wt", "wr", "bkgw")}
    comp = composite_n1(inputs, world["bkg"], world["bank_cv"], lambda t: _weights(world, a, t), world["flux"],
                        declared_draws(flux_p, world["groups"]))
    return {"schema": SCHEMA, "step": "receipt", "n1_bound": N1_BOUND, "universes": rows, "max_abs_ratio": worst,
            "composite": comp, "verdict": "STOP" if comp["stop"] else "PASS", "atime": inv.atime_check()}


def pilot_walls(unfolds: Path, tag: str, plugin: bool) -> dict:
    rows = []
    for role, item in PILOT[plugin]:
        truth = "data" if role in ("control", "capture") else item.split(":")[0]
        it = item.split(":", 1)[1] if ":" in item else ("" if role == "central" else item)
        name = product_name(tag, truth, role, it if role != "central" else "T")
        p = unfolds / name
        if not p.exists():
            return {"verdict": "REPRICE", "why": f"missing {name}"}
        m = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
        rows.append({"product": name, "seconds_unfold": m["seconds_unfold"], "peak_rss_kib": m["peak_rss_kib"]})
    s_max, r_max = max(r["seconds_unfold"] for r in rows), max(r["peak_rss_kib"] for r in rows)
    ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB
    return {"verdict": "PASS" if ok else "REPRICE", "max_seconds_unfold": s_max, "max_peak_rss_kib": r_max,
            "unit_seconds": UNIT_SECONDS, "rss_limit_kib": RSS_LIMIT_KIB, "rows": rows}


# ------------------------------------------------------------------------------------------- the null and readout


def _cells(unfolds: Path, tag: str, truth: str, role: str, items, U: np.ndarray) -> np.ndarray:
    return np.array([U @ np.asarray(np.load(unfolds / product_name(tag, truth, role, i), allow_pickle=False)["xsec_flat"],
                                    float) for i in items])


def remade(unfolds: Path, tag: str, truth: str, s1: dict, U: np.ndarray, constraint: Path, cmodel_frac: np.ndarray) -> dict:
    """The blocks at T by S1's procedure (section 4.3) and the null's laws (section 5.2)."""
    X_T = _cells(unfolds, tag, truth, "central", ["T"], U)[0]
    seedX = _cells(unfolds, tag, truth, "seed", ["T"], U)[0]
    if not np.array_equal(X_T, seedX):
        raise Refusal("the seed check failed: estimator seed 45 differs from 42 at T")
    blocks, laws = {}, []
    w = via_noatime(sa.flux_weights, constraint)
    for band, n in sa.EXPECT.items():
        X = _cells(unfolds, tag, truth, "block", [f"{band}_{i}" for i in range(n)], U)
        p = w / w.sum() if band == sa.FLUX else np.full(n, 1.0 / n)
        blocks[f"band:{band}"] = sa.mat_cov(X, w if band == sa.FLUX else None)
        laws.append((f"band:{band}", fn.Discrete.centred(X, p), X))
    R = _cells(unfolds, tag, truth, "stat", [str(b) for b in STAT_REPLICAS], U)
    blocks["stat"] = np.cov(R, rowvar=False, ddof=1)
    g = X_T / s1["f"]
    deltas = {}
    for b in sa.LATERAL_BANDS:
        B = s1["blocks"][f"lat:{b}"]
        k = int(np.argmax(np.diag(B)))
        v = B[:, k] / math.sqrt(B[k, k]) if B[k, k] > 0 else np.zeros_like(X_T)   # B = v v^T, v = Delta_b / 2
        deltas[b] = 2 * v
        blocks[f"lat:{b}"] = np.outer(v * g, v * g)
        laws.append((f"lat:{b}", fn.Discrete.two_point(2 * v * g), None))
    blocks["normalization"] = np.outer(sa.NORM_FRACTION * X_T, sa.NORM_FRACTION * X_T)
    C_e = sum(blocks.values())
    C_mabs = sa.model_abs(X_T, cmodel_frac)
    gauss = blocks["stat"] + blocks["normalization"] + C_mabs
    return {"X_T": X_T, "blocks": blocks, "C_e": C_e, "C_model_abs": C_mabs, "C_T": C_e + C_mabs,
            "laws": laws, "gauss": gauss, "deltas": deltas, "stat_R": R}


def null_at(rm: dict) -> dict:
    return fn.null_contents([law for _, law, _ in rm["laws"]], rm["gauss"], rm["C_T"])


def grade(E: np.ndarray, C: np.ndarray, null: dict, chol_tol: float = 1e-9, chol_out: dict | None = None) -> dict:
    """Section 5.1-5.2 for one matrix: counts, the flags against the null, the chi2 statistics, pulls, attribution.

    At full rank the non-null chi2 is cross-checked against a Cholesky chi2 to the relative ``chol_tol``. 1B's default
    (1e-9) is unchanged; COV2D-BINDING-2 addendum A5 passes max(1e-9, 10 kappa_2(C) eps). ``chol_out``, if given,
    receives the compared values (``ndf``, ``max_rel_diff``, ``tol``); a refusal carries the same dict as
    ``.compared``."""
    thr = fn.thresholds(null, E.shape[0])
    sigma = np.sqrt(np.diag(C))
    inside = np.sum(np.abs(E) <= sigma, axis=0)
    chi2, ndf = fn.chi2_nonnull(E, C)
    if ndf == C.shape[0]:
        L = np.linalg.cholesky(C)
        ref = np.sum(np.linalg.solve(L, E.T) ** 2, axis=0)
        compared = {"ndf": ndf, "max_rel_diff": float(np.max(np.abs(chi2 / ref - 1))), "tol": float(chol_tol)}
        if chol_out is not None:
            chol_out.update(compared)
        if compared["max_rel_diff"] > chol_tol:
            e = Refusal("the non-null chi2 and the Cholesky chi2 differ")
            e.compared = compared
            raise e
    elif chol_out is not None:
        chol_out.update({"ndf": ndf, "max_rel_diff": None, "tol": float(chol_tol)})
    joint = int(np.sum(chi2 <= null["chi2_cut"]))
    cell_flag = [bool(int(n) <= k) for n, k in zip(inside, thr["k_cell"])]
    joint_flag = joint <= thr["k_joint"]
    attribution = {f"R{c:02d}": fn.attribute(E[:, c], sigma[c], thr["k_cell"][c]) for c in range(E.shape[1]) if cell_flag[c]}
    over = [bool(fn.binom_cdf(E.shape[0] - int(n), E.shape[0], 1 - float(p)) < thr["alpha_cell"])
            for n, p in zip(inside, null["p_cell"])]
    z = E / sigma
    s_c = [float(np.quantile(np.abs(E[:, c]), min(float(null["p_cell"][c]), 1.0)) / sigma[c]) for c in range(E.shape[1])]
    return {"counts": inside.tolist(), "k_cell": thr["k_cell"], "cell_flag": cell_flag, "joint_count": joint,
            "k_joint": thr["k_joint"], "joint_flag": joint_flag, "ndf": ndf, "chi2_mean_over_ndf": float(chi2.mean() / ndf),
            "chi2_mean_over_ndf_se": float(chi2.std(ddof=1) / math.sqrt(chi2.size) / ndf), "over_covers": over,
            "pull_mean": z.mean(axis=0).tolist(), "pull_sd": z.std(axis=0, ddof=1).tolist(), "s_c": s_c,
            "attribution": attribution, "size": fn.size(null, thr),
            "verdict": "UNDER-COVERS" if (any(cell_flag) or joint_flag) else "COVERS"}


def refuse_partials(unfolds: Path, tag: str, truth: str) -> None:
    """A killed step leaves ``<product>.partial-<pid>.npz`` (``s5n_pseudo.write_product``), which the products' globs
    would match."""
    left = sorted(p.name for p in unfolds.glob(f"{tag}_{truth}_*.partial-*"))
    if left:
        raise Refusal(f"partial products are present: {left[:3]}")


def toy_paths(unfolds: Path, tag: str, truth: str) -> list[Path]:
    """A truth's toy products in seed order; exactly the declared seeds, no partials."""
    refuse_partials(unfolds, tag, truth)
    seeds = list(TOY_SEEDS[truth])
    have = sorted(int(p.name.rsplit("_", 1)[1][:-4]) for p in unfolds.glob(f"{tag}_{truth}_toy_*.npz"))
    if have != seeds:
        raise Refusal(f"{truth}'s toy products are not exactly the declared seeds ({len(have)} of {len(seeds)})")
    return [unfolds / product_name(tag, truth, "toy", str(s)) for s in seeds]


def products_digest(unfolds: Path, tag: str, truth: str, roles: tuple[str, ...]) -> str:
    """One digest over the named roles' products at T, so the null pins exactly the products it was made from."""
    refuse_partials(unfolds, tag, truth)
    h = hashlib.sha256()
    for p in sorted(unfolds.glob(f"{tag}_{truth}_*.npz")):
        if p.name.split("_")[len(tag.split("_")) + 1] in roles:
            h.update(p.name.encode())
            h.update(s5n_pseudo.sha256_path(p).encode())
    return h.hexdigest()


BLOCK_ROLES = ("central", "seed", "block", "stat")


def cmodel_parts(s1_npz: Path, cmodel_json: Path) -> tuple[np.ndarray, np.ndarray]:
    """S1's fractional C_model and the leave-out-MEC C_model^- from the committed builder's shift vectors; the
    vectors must rebuild S1's matrix to 1e-12 relative."""
    frac = np.asarray(inv.load_npz(s1_npz)["C_model_frac"], float)
    cj = json.loads(cmodel_json.read_text())
    S = {v: np.asarray(s, float) for v, s in zip(cj["vertices"], cj["S"])}
    full = sum(np.outer(s, s) for s in S.values())
    if np.max(np.abs(full - frac)) > 1e-12 * np.max(np.abs(frac)):
        raise Refusal("the committed shift vectors do not rebuild S1's C_model")
    minus = sum(np.outer(s, s) for v, s in S.items() if v != "genie_mec")
    return frac, minus


def null_step(a) -> dict:
    """Section 5.2: the draw-matched nulls at T (C_T and the leave-out-MEC C_T^-) from the remade products only."""
    s1 = via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):
        raise Refusal("the definition's functional is not S1's")
    frac, minus = cmodel_parts(a.staged / "s1" / "s1_assembly.npz", a.cmodel_json)
    rm = remade(a.unfolds, a.tag, a.truth, s1, U, a.flux_constraint, frac)
    laws = [law for _, law, _ in rm["laws"]]
    out = {"schema": SCHEMA, "step": "null", "truth": a.truth,
           "products_sha256": products_digest(a.unfolds, a.tag, a.truth, BLOCK_ROLES), "made_from": made_from(a, U)}
    for name, C_mabs in (("C_T", rm["C_model_abs"]), ("C_T_minus_mec", sa.model_abs(rm["X_T"], minus))):
        C = rm["C_e"] + C_mabs
        null = fn.null_contents(laws, rm["blocks"]["stat"] + rm["blocks"]["normalization"] + C_mabs, C)
        thr = fn.thresholds(null)
        out[name] = {"p_cell": null["p_cell"].tolist(), "se_cell": null["se_cell"].tolist(), "q_joint": null["q_joint"],
                     "se_joint": null["se_joint"], "ndf": null["ndf"], "chi2_cut": null["chi2_cut"],
                     "n_mc": null["n_mc"], "seed": null["seed"], "match_rel": null["match_rel"], "thresholds": thr,
                     "size": fn.size(null, thr)}
    return out


def made_from(a, U: np.ndarray) -> dict:
    """What C_T is built from besides the products and the digest-pinned assembly and constraint: the definition, the
    cmodel json (which sets C_model^-) and U itself. The null records them and the readout refuses a difference."""
    return {"definition_sha256": sa.sha256(a.definition), "cmodel_json_sha256": sa.sha256(a.cmodel_json),
            "U_sha256": hashlib.sha256(np.ascontiguousarray(U, dtype=float).tobytes()).hexdigest()}


def model_dominant(C: np.ndarray, C_mabs: np.ndarray) -> list[str]:
    """N2's cells: where diag C_model_abs is more than half of diag C (clause S)."""
    return [f"R{c:02d}" for c in range(C.shape[0]) if C_mabs[c, c] > 0.5 * C[c, c]]


def _null_dict(d: dict) -> dict:
    return {"p_cell": np.asarray(d["p_cell"], float), "se_cell": np.asarray(d["se_cell"], float),
            "q_joint": float(d["q_joint"]), "se_joint": float(d["se_joint"]), "chi2_cut": float(d["chi2_cut"])}


def toy_errors(unfolds: Path, tag: str, truth: str, U: np.ndarray, rm: dict, f: np.ndarray) -> tuple[np.ndarray, list]:
    X_raw, X_true, draws = [], [], []
    for p in toy_paths(unfolds, tag, truth):
        z = np.load(p, allow_pickle=False)
        X_raw.append(U @ np.asarray(z["xsec_flat"], float))
        X_true.append(U @ np.asarray(z["xtrue_flat"], float))
        draws.append(json.loads(str(z["meta"]))["draw"])
    X_hat = fs.surrogate(np.array(X_raw), draws, rm["deltas"], f, rm["X_T"])
    return X_hat - np.array(X_true), draws


def readout(a) -> dict:
    """Section 5's grading and section 7's readouts at T. The null is the committed one, pinned by digest; it must
    have been made from these very products."""
    if inv.sha256_noatime(a.null) != a.expect_null_sha256:
        raise Refusal("the null's digest differs from the declared one")
    nl = json.loads(a.null.read_text())
    if nl["products_sha256"] != products_digest(a.unfolds, a.tag, a.truth, BLOCK_ROLES):
        raise Refusal("the null was not made from these products")
    s1 = via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):
        raise Refusal("the definition's functional is not S1's")
    if nl.get("made_from") != made_from(a, U):
        raise Refusal("the definition, the cmodel json or U is not the one the null was made from")
    frac, minus = cmodel_parts(a.staged / "s1" / "s1_assembly.npz", a.cmodel_json)
    rm = remade(a.unfolds, a.tag, a.truth, s1, U, a.flux_constraint, frac)
    if a.truth == "plugin":   # section 6 (b), a plumbing check that holds by construction
        xt = U @ np.asarray(np.load(a.unfolds / product_name(a.tag, a.truth, "central", "T"))["xtrue_flat"], float)
        if np.max(np.abs(xt / s1["f"] - 1)) > 1e-12:
            raise Refusal("plug-in control (b): U x_T is not U f to 1e-12")
    E, draws = toy_errors(a.unfolds, a.tag, a.truth, U, rm, s1["f"])
    main = grade(E, rm["C_T"], _null_dict(nl["C_T"]))
    C_mabs_minus = sa.model_abs(rm["X_T"], minus)
    variant = grade(E, rm["C_e"] + C_mabs_minus, _null_dict(nl["C_T_minus_mec"]))
    if main["verdict"] == "COVERS":
        hit = [c for c, fl in enumerate(variant["cell_flag"]) if fl]
        mec = ("covers without the GENIE + MEC shift" if not hit and not variant["joint_flag"] else
               f"its coverage in cells {[f'R{c:02d}' for c in hit]}{' (and jointly)' if variant['joint_flag'] else ''} "
               "rests on the GENIE + MEC shift")
    else:
        mec = "printed; no reading (the tune under-covers under C_T)"
    sig_e = np.sqrt(np.diag(rm["C_e"]))
    spread = {"counts": np.sum(np.abs(E) <= sig_e, axis=0).tolist(), "pull_mean": (E / sig_e).mean(axis=0).tolist(),
              "pull_sd": (E / sig_e).std(axis=0, ddof=1).tolist()}
    # the toys draw each band's mean shift, which MAT mean-centring drops from its block; by the swap, with a minus
    offset = -sum(law.probs @ X - rm["X_T"] for _, law, X in rm["laws"] if X is not None)
    lam, V = np.linalg.eigh(rm["C_e"])
    S = np.cov(E - E.mean(axis=0), rowvar=False, ddof=1)
    eig_ratio = [float(V[:, k] @ S @ V[:, k] / lam[k]) for k in range(lam.size)]
    i2 = json.loads(a.i2.read_text())
    A_T = sum(np.diag(rm["blocks"][f"band:{b}"]) for b in inv.INTERACTION)
    frac_T = np.sqrt(A_T) / rm["X_T"]
    frac_nom = np.sqrt(np.asarray(i2["A"], float)) / s1["f"]
    groups = {}
    for gname in ("flux", "interaction", "detector", "stat"):
        keys = [k for k in rm["blocks"] if sa.group_of(k) == gname]
        T_g = sum(np.diag(rm["blocks"][k]) for k in keys)
        M_g = sum(np.diag(s1["blocks"][k]) for k in keys)
        groups[gname] = (np.sqrt(T_g) / rm["X_T"] / (np.sqrt(M_g) / s1["f"])).tolist()
    return {"schema": SCHEMA, "step": "readout", "truth": a.truth, "null_sha256": a.expect_null_sha256,
            "cells": [f"R{c:02d}" for c in range(sa.N_CELLS)], "verdict": main["verdict"], "C_T": main,
            "clause_S_model_dominant_cells": {"C_T": model_dominant(rm["C_T"], rm["C_model_abs"]),
                                              "C_T_minus_mec": model_dominant(rm["C_e"] + C_mabs_minus, C_mabs_minus)},
            "leave_out_mec": {"grade": variant, "reading": mec},
            "descriptive": {"spread_alone_vs_C_e": spread, "toys_mean_error": E.mean(axis=0).tolist(),
                            "predicted_offset_uncentred_draws": np.asarray(offset, float).tolist(),
                            "eigen_variance_ratio_vs_C_e": eig_ratio},
            "truth_dependence": {"A_T_over_A_nom_fractional": (frac_T / frac_nom).tolist(), "group_at_T_over_M": groups},
            "X_T": rm["X_T"].tolist(), "sigma_T": np.sqrt(np.diag(rm["C_T"])).tolist()}


def n1_step(a) -> dict:
    """N1's per-toy record at T, read by a step that grades nothing (the audit's B2 on #673): per array, the largest
    composite ratio over the toys and the toys with rows above the bound. It opens only the products' meta, and
    runs before ``null``."""
    worst, above = {}, {}
    for p in toy_paths(a.unfolds, a.tag, a.truth):
        n1 = json.loads(str(np.load(p, allow_pickle=False)["meta"]))["universe_info"]["n1"]
        for k, v in n1.items():
            worst[k] = max(worst.get(k, 0.0), v["max_composite_over_max_single"])
            if v["rows_above_bound"]:
                above.setdefault(k, []).append(p.name)
    return {"schema": SCHEMA, "step": "n1", "truth": a.truth, "bound": N1_BOUND, "max_composite_over_max_single": worst,
            "toys_with_rows_above": above, "verdict": "STOP" if above else "PASS"}


# --------------------------------------------------------------------------------------------------------- main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("unfold")
    p.add_argument("--truth", choices=tuple(TRUTHS) + ("data",), required=True)
    p.add_argument("--role", choices=ROLES, required=True)
    p.add_argument("--items", required=True)
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--prep", type=Path, default=None)
    p.add_argument("--flux-table", type=Path, default=None)
    p.add_argument("--expect-flux-table-sha256", default=None)
    p.add_argument("--push", type=Path, default=None)
    p.add_argument("--expect-push-sha256", default=None)
    p.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    p.add_argument("--tag", default="fd1b_mc")
    p = sub.add_parser("stage-flux")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("receipt")
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--expect-flux-table-sha256", required=True)
    p = sub.add_parser("n1")
    p.add_argument("--truth", choices=tuple(TRUTHS), required=True)
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--tag", default="fd1b_mc")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("walls")
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--plugin", choices=("yes", "no"), required=True)
    p.add_argument("--tag", default="fd1b_mc")
    p.add_argument("--out", type=Path, required=True)
    for name in ("null", "readout"):
        p = sub.add_parser(name)
        p.add_argument("--truth", choices=tuple(TRUTHS), required=True)
        for k in ("staged", "unfolds", "definition", "cmodel-json", "flux-constraint", "out"):
            p.add_argument(f"--{k}", type=Path, required=True)
        p.add_argument("--tag", default="fd1b_mc")
        if name == "readout":
            p.add_argument("--null", type=Path, required=True)
            p.add_argument("--expect-null-sha256", required=True)
            p.add_argument("--i2", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "unfold":
            return run_unfold(a)
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        if a.cmd == "stage-flux":
            res = stage_flux(a.root, a.out)
            print(json.dumps(res))
            return 0
        if a.cmd == "walls":
            res = pilot_walls(a.unfolds, a.tag, a.plugin == "yes")
            a.out.write_text(json.dumps(res, indent=1) + "\n")
            print(json.dumps({"verdict": res["verdict"], "max_seconds_unfold": res.get("max_seconds_unfold")}))
            return 0 if res["verdict"] == "PASS" else 1
        res = {"receipt": receipt, "n1": n1_step, "null": null_step, "readout": readout}[a.cmd](a)
        res["code_sha256"] = code_digests()
        a.out.write_text(json.dumps(res, indent=1, default=float) + "\n")
        print(json.dumps({"out": str(a.out), "step": res["step"], "verdict": res.get("verdict")}))
        return 0
    except (Refusal, SystemExit, ValueError, OSError) as e:
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-mc] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())

"""1B's redesigned test, mode D, and its grid check (state/measurement-paper/5d-community-20261024/FD-1B-MODED-DECLARATION.md).

Mode D makes nature the universe: the pseudo-data are the simulation with interaction universe u's event weights on
truth, reconstruction and background together (``s5p_universe.universe_inputs``, the arrays I2's mode A unfolded
with), and they are unfolded with the nominal simulation by S1's estimator and settings. Each product stores the
unfolded result and the universe's own truth; the readout's per-universe object is the error e(u) = U x_hat - U T_u.

* ``Ddl``: at the data-like truth, the simulation reweighted per reporting cell by r_c = f_c / (U x_T)_c, so the
  CV nature's truth equals S1's data result f in every cell (``dltruth`` writes r_c);
* ``Dnom``: at the nominal truth (r = 1), the comparison with I2's mode A at matched truth;
* ``B`` and ``C`` on a named fine-cell grid (``coarse``, ``nominal``, ``fine``): I2's response-only and cell-mean
  truth-reweight modes with only their factor grid changed; ``nominal`` is I2's own construction.

Subcommands: ``dltruth`` (login node), ``unfold`` (one lane), ``walls`` (the pilot's re-price trigger), ``readout``
(login node). Every pscratch input is read with O_NOATIME through ``fd_1b_inv``'s readers. Nothing here changes the
toys, gate D, M_d, the window, the reported covariance or any claim.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_diag as fdg  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_nullexp as ne  # noqa: E402
import s5p_stage1_inspect as s1i  # noqa: E402
import s5p_truths  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "fd-1b-moded/1"
WINDOW = fs.GATE_D_WINDOW
D_MODES = ("Ddl", "Dnom")
GRID_MODES = ("B", "C")
GRIDS = ("coarse", "nominal", "fine")
INTERACTION = inv.INTERACTION
# the grid check's six universes (declaration section 5): the five bands with I2's largest per-band residual medians,
# and FrAbs_pi, whose residual was among the smallest of the bands with A/M near 1
GRID_UNIVERSES = ("MaRES_0", "MvRES_0", "Rvp2pi_0", "Theta_Delta2Npi_0", "MaCCQE_0", "FrAbs_pi_0")
# the pilot (declaration section 7): its eight products and the re-price trigger the bulk must pass
PILOT = (("Ddl", None, "CV"), ("Dnom", None, "CV"), ("Ddl", None, "MaRES_0"), ("Ddl", None, "2p2h_0"),
         ("Ddl", None, "LowQ2_1"), ("Dnom", None, "MaRES_0"), ("B", "fine", "MaRES_0"), ("C", "fine", "MaRES_0"))
UNIT_SECONDS = 1062.0           # 1.25 x 849.6 s, the largest of I2's 204 measured unfolds (section 7)
RSS_LIMIT_KIB = inv.RSS_LIMIT_KIB
ONE_CODE_KEYS = inv.ONE_CODE_KEYS
DL_TOLERANCE = 1e-12            # the data-like CV nature's truth against f, relative, per cell
ACCOUNT = 8                     # a partial pass or a matched comparison: at least half of the 16 cells in the window
Refusal = inv.Refusal


# ------------------------------------------------------------------------------------------------------------ grids


def grid_edges(name: str) -> list[np.ndarray]:
    """The factor grid, in ``s5p_stage1_inspect.AXES`` order. ``nominal`` is the fine grid; ``coarse`` keeps every
    second fine edge, the last edge and every H2 edge (so no coarse cell straddles a reporting cell); ``fine`` adds
    the midpoint of every fine cell on every axis."""
    out = []
    for a in s1i.AXES:
        e = np.asarray(s1i.FINE[a], float)
        if name == "nominal":
            out.append(e)
        elif name == "coarse":
            out.append(np.unique(np.concatenate([e[::2], e[-1:], np.asarray(s1i.H2_EDGES[a], float)])))
        elif name == "fine":
            out.append(np.unique(np.concatenate([e, 0.5 * (e[:-1] + e[1:])])))
        else:
            raise ValueError(f"grid {name!r}")
    return out


def check_fine_grid(inputs: dict) -> None:
    """The analysis inputs' edges are the fine grid the reporting map and the grids are defined on."""
    edges = inputs["edges"]
    if len(edges) != len(s1i.AXES) or not all(np.array_equal(np.asarray(e, float), np.asarray(s1i.FINE[a], float))
                                              for e, a in zip(edges, s1i.AXES)):
        raise Refusal("the inputs' edges are not s5p_stage1_inspect.FINE")


def grid_inputs(mode: str, tag: str, grid: str, inputs: dict, bkg: dict, bank: Path) -> tuple[dict, dict, dict]:
    """I2's B or C for one universe with its factor grid replaced: B's truth-preserving g_f and C's fine-cell mean r
    are computed on ``grid``; the unfolding, C's denominator factor and the extraction stay on the analysis grid.
    At ``nominal`` this is ``fd_1b_inv.mode_inputs`` exactly."""
    if tag == "CV":
        return dict(inputs), dict(bkg), {}
    if mode not in GRID_MODES:
        raise ValueError(f"mode {mode!r}")
    on_grid = dict(inputs, edges=grid_edges(grid)) if grid != "nominal" else inputs
    w = inv.universe_weights(bank, tag, "keep")
    _, k_b, k_wt, rec = inv.response_factors(w, inputs, bkg, tag)
    if mode == "B":
        k_wr = ne.checked_ratio(w["wr"], np.asarray(inputs["w_reco"], float), np.asarray(inputs["pass_reco"], bool),
                                f"{tag}:wr", {}, clip_negative=True)
        fs_ = k_wr * ne.truth_preserving(k_wt, on_grid, np.ones(inputs["MCgen"].shape[0], bool))
        return (dict(inputs, w_reco=np.asarray(inputs["w_reco"], float) * fs_),
                dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * k_b), rec)
    return inv.prior_mc(inputs, inv.cell_mean_factor(k_wt, on_grid)), dict(bkg), rec


# ------------------------------------------------------------------------------------------------- the D experiment


def row_cell(inputs: dict, fm: np.ndarray) -> np.ndarray:
    """Each MC row's reporting cell by its truth coordinates on the fine grid (-1: outside the grid or unreported)."""
    edges = inputs["edges"]
    shape = [len(e) - 1 for e in edges]
    if int(np.prod(shape)) != fm.size:
        raise Refusal(f"the fine map has {fm.size} entries, the grid {int(np.prod(shape))}")
    inside, idx = s5p_truths.cell_of(np.asarray(inputs["MCgen"]), edges)
    cell = np.full(inputs["MCgen"].shape[0], -1, int)
    cell[inside] = fm[np.ravel_multi_index(idx, shape)]
    return cell


def dl_weight(cell: np.ndarray, r_cell: np.ndarray) -> np.ndarray:
    """The data-like truth weight per row: r_c on the rows of reporting cell c, 1 elsewhere."""
    r = np.ones(cell.size)
    m = cell >= 0
    r[m] = np.asarray(r_cell, float)[cell[m]]
    return r


def d_experiment(inputs: dict, bkg: dict, ui: dict, ub: dict, r: np.ndarray) -> tuple[dict, np.ndarray]:
    """Nature is the universe: pseudo-data from universe u's MC and background (``ui``, ``ub``) at truth weight r,
    every Poisson draw at its mean, with the nominal simulation as the unfolding MC. Returns the experiment and the
    universe's own truth (``fd_1b_toys.build_full`` over ``ui``: its truth weights x r, its denominator)."""
    ones_s, ones_b = np.ones(ui["w_reco"].shape[0]), np.ones(ub["bkg_w"].shape[0])
    exp, x_true, _ = toys.build_full(ui, ub, r, ones_s, ones_b, None, expectation=True)
    return inv.with_mc(exp, inputs, bkg), x_true


def load_dl(path: Path, expect_sha256: str) -> dict:
    if sa.sha256(path) != expect_sha256:
        raise Refusal(f"{path}: digest differs from the declared data-like truth")
    d = json.loads(path.read_text())
    r = np.asarray(d["r_cell"], float)
    if d.get("schema") != SCHEMA or r.size != sa.N_CELLS or not np.all(np.isfinite(r) & (r > 0)):
        raise Refusal(f"{path}: not a data-like truth of {sa.N_CELLS} finite positive factors")
    return d


def dltruth(staged: Path, definition: Path) -> dict:
    """r_c = f_c / (U x_T)_c from S1's data result f (the staged assembly) and the staged derivation CV product's
    nominal truth, with U the reporting functional built from the definition, as the job and the readout build it."""
    s1 = fs.load_s1(staged / "s1" / "s1_assembly.npz")
    cv = inv.load_npz(staged / "derivation" / f"{inv.DER_TAG}_CV.npz")
    ux = sa.functional_matrix(sa.fine_map(definition)) @ np.asarray(cv["xtrue_flat"], float)
    r = s1["f"] / ux
    if not np.all(np.isfinite(r) & (r > 0)):
        raise Refusal("a reporting cell's data-like factor is not finite and positive")
    return {"schema": SCHEMA, "step": "dltruth", "f": s1["f"].tolist(), "U_xT": ux.tolist(), "r_cell": r.tolist(),
            "sources": {"s1_assembly": sa.sha256(staged / "s1" / "s1_assembly.npz"),
                        "derivation_CV": sa.sha256(staged / "derivation" / f"{inv.DER_TAG}_CV.npz")}}


# -------------------------------------------------------------------------------------------------------- unfolding


def product_name(tag: str, mode: str, grid: str | None, u: str) -> str:
    return f"{tag}_{mode}_{grid}_{u}.npz" if mode in GRID_MODES else f"{tag}_{mode}_{u}.npz"


def run_unfold(a, unfold_fn=None) -> int:
    inv.OPENED.clear()
    s5e_candidate.install(toys.CONFIG)
    if (a.mode in GRID_MODES) != (a.grid is not None):
        raise Refusal("--grid is required for B and C and refused for D")
    npz_sha, bkg_sha = inv.sha256_noatime(a.npz), inv.sha256_noatime(a.bkg)
    if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):
        raise Refusal(f"input digests {npz_sha} / {bkg_sha} are not the declared ones")
    if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:
        raise Refusal("pins file digest differs")
    with inv.open_noatime(a.pins) as fh:
        pins = json.loads(fh.read().decode())
    toys.check_pins(pins, a.bank, a.detector_dir)
    groups = toys.interaction_groups(a.bank)
    inputs = inv.load_inputs(a.npz)
    check_fine_grid(inputs)
    bz = inv.load_npz(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    bank_cv = inv.load_npz(a.bank / "cv.npz", allow_pickle=True)
    alignment = s5p_universe.check_alignment(bank_cv, inputs, bkg)
    exp_cv, x_nom = inv.nominal_experiment(inputs, bkg)
    r, dl_sha, truth = s5n_pseudo.truth_weight("nominal", inputs, 0.0, None), None, "nominal"
    if a.mode == "Ddl":
        if a.dl is None or a.expect_dl_sha256 is None or a.definition is None:
            raise Refusal("Ddl needs --dl, --expect-dl-sha256 and --definition")
        dl = load_dl(a.dl, a.expect_dl_sha256)
        fm = sa.fine_map(a.definition)
        U = sa.functional_matrix(fm)
        if not np.array_equal(U @ np.asarray(x_nom, float).ravel(order="C"), np.asarray(dl["U_xT"], float)):
            raise Refusal("this run's nominal truth is not the one the data-like factors were made against")
        r, dl_sha, truth = r * dl_weight(row_cell(inputs, fm), dl["r_cell"]), a.expect_dl_sha256, "data-like"
    legal = {u for us in groups.values() for u in us} | {"CV"}
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for tag in a.universes.split(","):
        if tag not in legal:
            raise Refusal(f"{tag} is not one of the 67 interaction universes or CV")
        if a.mode in GRID_MODES and tag not in GRID_UNIVERSES + ("CV",):
            raise Refusal(f"{tag} is not one of the grid check's declared universes")
        target = a.out / product_name(a.tag, a.mode, a.grid, tag)
        if target.exists():
            continue
        toys.check_pins(pins, a.bank, a.detector_dir)
        if tag != "CV":
            for k in s5p_universe.weight_keys(a.bank, tag):
                p = a.bank / f"{tag}_{k}.npy"
                if inv.sha256_noatime(p) != pins["files"][str(p)]["sha256"]:
                    raise Refusal(f"{p}: digest differs from the pins file")
        t1 = time.time()
        if a.mode in D_MODES:
            ui, ub, info = inv.mode_inputs("A", tag, inputs, bkg, a.bank, bank_cv)
            exp, x_true = d_experiment(inputs, bkg, ui, ub, r)
        else:
            ui, ub, info = grid_inputs(a.mode, tag, a.grid, inputs, bkg, a.bank)
            exp, x_true = inv.with_mc(exp_cv, ui, ub), x_nom
        xs, ev = (unfold_fn or s5n_pseudo.unfold_negweight)(exp, toys.ESTIMATOR_SEED, a.threads, toys.ITERS)
        xs = np.asarray(xs, float)
        if not np.all(np.isfinite(xs)):
            raise Refusal(f"{target.name}: a non-finite unfolded value")
        meta = {"schema": SCHEMA, "step": "D", "mode": a.mode, "grid": a.grid, "universe": tag, "truth": truth,
                "dl_sha256": dl_sha, "config": toys.CONFIG, "capacity": None, "iters": toys.ITERS,
                "estimator_seed": toys.ESTIMATOR_SEED, "threads": a.threads, "mode_info": info, **ev,
                "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha, "pins_sha256": a.expect_pins_sha256,
                "alignment": alignment,
                "code_sha256": {**toys.code_digests(), "fd_1b_inv.py": s5n_pseudo.sha256_path(Path(inv.__file__).resolve()),
                                "fd_1b_moded.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t1, 3),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "numpy_version": np.__version__}
        status |= s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"),
                                                    "xtrue_flat": np.asarray(x_true, float).ravel(order="C")}, meta)
        print(json.dumps({"out": target.name, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    chk = inv.atime_check()
    (a.out / f"atime-{a.mode}-{os.environ.get('SLURM_JOB_ID', 'local')}-{os.getpid()}.json").write_text(
        json.dumps(chk, indent=1) + "\n")
    if chk["moved"]:
        print(f"[fd-1b-moded] DEVIATION: atime moved on {chk['moved']}", file=sys.stderr)
        return status | 8
    return status


def pilot_walls(unfolds: Path, tag: str) -> dict:
    """The pilot's re-price trigger (declaration section 7): PASS iff all eight pilot products exist, the largest
    seconds_unfold is at most UNIT_SECONDS and the largest peak RSS at most RSS_LIMIT_KIB; otherwise REPRICE."""
    rows = []
    for mode, grid, u in PILOT:
        p = unfolds / product_name(tag, mode, grid, u)
        if not p.exists():
            raise Refusal(f"pilot product {p.name} is missing")
        m = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
        if (m.get("mode"), m.get("grid"), m.get("universe")) != (mode, grid, u) or m.get("peak_rss_kib") is None:
            raise Refusal(f"{p.name}: not pilot item {mode} {grid} {u}, or no peak_rss_kib")
        rows.append({"item": p.name, "seconds_unfold": float(m["seconds_unfold"]), "peak_rss_kib": int(m["peak_rss_kib"])})
    s_max = max(r["seconds_unfold"] for r in rows)
    r_max = max(r["peak_rss_kib"] for r in rows)
    ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB
    return {"schema": SCHEMA, "step": "D-0", "items": rows, "max_seconds_unfold": s_max, "unit_seconds": UNIT_SECONDS,
            "max_peak_rss_kib": r_max, "rss_limit_kib": RSS_LIMIT_KIB, "verdict": "PASS" if ok else "REPRICE"}


# ---------------------------------------------------------------------------------------------------------- rules


def in_window(x) -> np.ndarray:
    x = np.asarray(x, float)
    return (x >= WINDOW[0]) & (x <= WINDOW[1])


def d_outcome(rho: np.ndarray) -> dict:
    """Rule D (declaration section 6): PASS if rho_D is in the window in all 16 cells, PARTIAL if in at least 8,
    FAIL otherwise. R00 and R05 are graded as every other cell."""
    rho = np.asarray(rho, float)
    inside = in_window(rho)
    n = int(inside.sum())
    verdict = "PASS" if n == rho.size else "PARTIAL" if n >= ACCOUNT else "FAIL"
    return {"verdict": verdict, "cells_in_window": n,
            "above": [f"R{c:02d}" for c in np.flatnonzero(rho > WINDOW[1])],
            "below": [f"R{c:02d}" for c in np.flatnonzero(rho < WINDOW[0])],
            "next": "the coverage ensemble may be declared" if verdict == "PASS" else "to Joseph"}


def kappa_reading(kappa: np.ndarray) -> dict:
    """The matched-truth diagnostic: D at the nominal truth against I2's A. ``matched`` if in the window in at
    least 8 cells."""
    n = int(in_window(kappa).sum())
    return {"cells_in_window": n, "reading": "matched" if n >= ACCOUNT else "unmatched"}


def grid_reading(gamma: np.ndarray, phi: np.ndarray) -> dict:
    """The grid check's fixed reading (section 5): a mode depends on the grid if coarse/nominal or fine/nominal is
    outside the window in at least 8 cells; the sub-cell hypothesis is supported if coarse/nominal > 1.1 in at least
    8 cells AND fine/nominal < 0.9 in at least 8."""
    gamma, phi = np.asarray(gamma, float), np.asarray(phi, float)
    out_g, out_f = int((~in_window(gamma)).sum()), int((~in_window(phi)).sum())
    return {"coarse_out": out_g, "fine_out": out_f, "grid_dependent": out_g >= ACCOUNT or out_f >= ACCOUNT,
            "coarse_above": int((gamma > WINDOW[1]).sum()), "fine_below": int((phi < WINDOW[0]).sum()),
            "subcell_hypothesis_supported": bool((gamma > WINDOW[1]).sum() >= ACCOUNT and (phi < WINDOW[0]).sum() >= ACCOUNT)}


# ---------------------------------------------------------------------------------------------------------- readout


def _meta(z: dict) -> dict:
    return json.loads(str(z["meta"]))


def d_blocks(unfolds: Path, tag: str, mode: str, U: np.ndarray, metas: dict) -> dict:
    """One D mode's per-band blocks by S1's estimator (``s1_assemble.mat_cov``, mean-centred, 1/N) on three objects
    per universe: the error U x_hat - U T_u (the rule's object), the raw shift U x_hat - U x_hat(CV) and the truth
    spread U T_u - U T_CV (both descriptive)."""
    cv = inv.load_npz(unfolds / product_name(tag, mode, None, "CV"))
    metas[f"{mode}_CV"] = _meta(cv)
    X_cv, T_cv = U @ np.asarray(cv["xsec_flat"], float), U @ np.asarray(cv["xtrue_flat"], float)
    out = {"error": {}, "raw": {}, "truth": {}}
    for b in INTERACTION:
        rows = {"error": [], "raw": [], "truth": []}
        for i in range(sa.EXPECT[b]):
            p = unfolds / product_name(tag, mode, None, f"{b}_{i}")
            z = inv.load_npz(p)
            meta = _meta(z)
            if (meta.get("mode"), meta.get("universe"), meta.get("schema")) != (mode, f"{b}_{i}", SCHEMA):
                raise fs.Invalid(f"{p.name}: not mode {mode}, universe {b}_{i}")
            if (meta.get("dl_sha256") is not None) != (mode == "Ddl"):
                raise fs.Invalid(f"{p.name}: its truth is not mode {mode}'s")
            metas[f"{mode}_{b}_{i}"] = meta
            x, t = U @ np.asarray(z["xsec_flat"], float), U @ np.asarray(z["xtrue_flat"], float)
            rows["error"].append(x - t)
            rows["raw"].append(x - X_cv)
            rows["truth"].append(t - T_cv)
        for k, Y in rows.items():
            out[k][b] = sa.mat_cov(np.array(Y))
    return {"cv": cv, **out}


def readout(staged: Path, unfolds: Path, i2_unfolds: Path, i2_json: Path, i0_json: Path, dl_path: Path,
            definition: Path, tag: str, i2_tag: str = "fd1b_inv") -> dict:
    s1 = fs.load_s1(staged / "s1" / "s1_assembly.npz")
    U, f = s1["U"], s1["f"]
    U_def = sa.functional_matrix(sa.fine_map(definition))
    r2, r0 = json.loads(i2_json.read_text()), json.loads(i0_json.read_text())
    m = sum(v for k, v in s1["blocks"].items() if k.startswith("band:") and sa.group_of(k) == "interaction")
    M = np.diag(m)
    if M.tolist() != r2["M"]:
        raise fs.Invalid("S1's interaction block from the staged assembly is not I2's M bitwise")
    dl = json.loads(dl_path.read_text())
    x_cv_der = np.asarray(inv.load_npz(staged / "derivation" / f"{inv.DER_TAG}_CV.npz")["xsec_flat"], float)
    metas: dict = {}
    blk = {mode: d_blocks(unfolds, tag, mode, U, metas) for mode in D_MODES}
    if not np.array_equal(np.asarray(blk["Dnom"]["cv"]["xsec_flat"], float), x_cv_der):
        raise fs.Invalid("Dnom at CV does not reproduce the derivation CV product bitwise")
    T_dl = U_def @ np.asarray(blk["Ddl"]["cv"]["xtrue_flat"], float)
    if np.max(np.abs(T_dl / f - 1)) > DL_TOLERANCE:
        raise fs.Invalid("the data-like CV nature's truth is not f")
    grid = {}
    for mode in GRID_MODES:
        S = {}
        for gname in GRIDS:
            s = np.zeros(sa.N_CELLS)
            for u in GRID_UNIVERSES:
                p = unfolds / product_name(tag, mode, gname, u)
                z = inv.load_npz(p)
                meta = _meta(z)
                if (meta.get("mode"), meta.get("grid"), meta.get("universe")) != (mode, gname, u):
                    raise fs.Invalid(f"{p.name}: not mode {mode}, grid {gname}, universe {u}")
                metas[f"{mode}_{gname}_{u}"] = meta
                if gname == "nominal":
                    ref = inv.load_npz(i2_unfolds / f"{i2_tag}_{mode}_{u}.npz")
                    if not np.array_equal(np.asarray(z["xsec_flat"], float), np.asarray(ref["xsec_flat"], float)):
                        raise fs.Invalid(f"{p.name}: the nominal grid does not reproduce I2's product bitwise")
                s += (U @ (np.asarray(z["xsec_flat"], float) - x_cv_der)) ** 2
            S[gname] = s
        gamma, phi = np.sqrt(S["coarse"] / S["nominal"]), np.sqrt(S["fine"] / S["nominal"])
        grid[mode] = {"coarse_over_nominal": gamma.tolist(), "fine_over_nominal": phi.tolist(),
                      "reading": grid_reading(gamma, phi)}
    for key in ONE_CODE_KEYS:
        vals = {json.dumps(v.get(key), sort_keys=True) for v in metas.values()}
        if len(vals) != 1 or metas[next(iter(metas))].get(key) is None:
            raise fs.Invalid(f"the products are not one code and one input set: {key} takes {len(vals)} values")
    if {v.get("dl_sha256") for k, v in metas.items() if k.startswith("Ddl_")} != {sa.sha256(dl_path)}:
        raise fs.Invalid("the Ddl products do not all carry this data-like truth's digest")
    diag_sum = lambda d: sum(np.diag(v) for v in d.values())  # noqa: E731
    D_dl, D_nom = diag_sum(blk["Ddl"]["error"]), diag_sum(blk["Dnom"]["error"])
    A_raw = np.asarray(r2["A"], float) / np.asarray(r0["g"], float) ** 2
    rho, kappa = np.sqrt(D_dl / M), np.sqrt(D_nom / A_raw)
    full = sum(blk["Ddl"]["error"].values())
    corr = lambda C: C / np.sqrt(np.outer(np.diag(C), np.diag(C)))  # noqa: E731
    dcorr = (corr(full) - corr(m))[~np.eye(sa.N_CELLS, dtype=bool)]
    return {"schema": SCHEMA, "step": "D", "label": "DERIVATION", "cells": [f"R{c:02d}" for c in range(sa.N_CELLS)],
            "window": list(WINDOW), "M": M.tolist(), "D_dl": D_dl.tolist(), "D_nom": D_nom.tolist(),
            "A_uncarried": A_raw.tolist(), "rho_D": rho.tolist(), "rule_D": d_outcome(rho), "kappa": kappa.tolist(),
            "kappa_reading": kappa_reading(kappa),
            "descriptive": {
                "raw_shift_over_M": np.sqrt(diag_sum(blk["Ddl"]["raw"]) / M).tolist(),
                "truth_spread_over_M": np.sqrt(diag_sum(blk["Ddl"]["truth"]) / M).tolist(),
                "D_dl_over_D_nom": np.sqrt(D_dl / D_nom).tolist(),
                "F_truth_i2": r2["factors"]["F_truth"],
                "corr_D_minus_corr_M_max_abs": float(np.max(np.abs(dcorr))),
                "per_band_D_dl_over_M": {b: fdg.ratio(np.diag(blk["Ddl"]["error"][b]), np.diag(s1["blocks"][f"band:{b}"]))
                                         for b in INTERACTION}},
            "grid_check": grid, "dl_sha256": sa.sha256(dl_path), "r_cell": dl["r_cell"],
            "i2_sha256": sa.sha256(i2_json), "i0_sha256": sa.sha256(i0_json)}


# -------------------------------------------------------------------------------------------------------------- CLI


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("dltruth")
    p.add_argument("--staged", type=Path, required=True)
    p.add_argument("--definition", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("unfold")
    p.add_argument("--mode", choices=D_MODES + GRID_MODES, required=True)
    p.add_argument("--grid", choices=GRIDS, default=None)
    p.add_argument("--universes", required=True)
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--dl", type=Path, default=None)
    p.add_argument("--expect-dl-sha256", default=None)
    p.add_argument("--definition", type=Path, default=None)
    p.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    p.add_argument("--tag", default="fd1b_d")
    p = sub.add_parser("walls")
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--tag", default="fd1b_d")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("readout")
    for k in ("staged", "unfolds", "i2-unfolds", "i2", "i0", "dl", "definition", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--tag", default="fd1b_d")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "unfold":
            return run_unfold(a)
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        if a.cmd == "walls":
            res = pilot_walls(a.unfolds, a.tag)
            a.out.write_text(json.dumps(res, indent=1) + "\n")
            print(json.dumps({"out": str(a.out), "verdict": res["verdict"], "max_seconds_unfold": res["max_seconds_unfold"],
                              "max_peak_rss_kib": res["max_peak_rss_kib"]}))
            return 0 if res["verdict"] == "PASS" else 1
        if a.cmd == "dltruth":
            res = dltruth(a.staged, a.definition)
        else:
            res = readout(a.staged, a.unfolds, a.i2_unfolds, a.i2, a.i0, a.dl, a.definition, a.tag)
        res["code_sha256"] = {"fd_1b_moded.py": sa.sha256(Path(__file__).resolve()),
                              "fd_1b_inv.py": sa.sha256(Path(inv.__file__).resolve())}
        a.out.write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"out": str(a.out), "step": res["step"],
                          "verdict": res["rule_D"]["verdict"] if a.cmd == "readout" else None}))
        return 0
    except (Refusal, SystemExit, ValueError, OSError) as e:
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-moded] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())

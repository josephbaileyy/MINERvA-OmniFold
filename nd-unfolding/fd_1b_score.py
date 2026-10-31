#!/usr/bin/env python3
"""1B with 4A, the scorer and the gate-D reader (state/measurement-paper/5d-community-20261024/FD-1B-DECLARATION.md
sections 4-6, bound by FD-1B-BINDING.md). Its constants are the declaration's; ``tests/test_fd_1b.py`` holds them
against the declared numbers, and none may change after a toy output exists.

The matrix under test is the reported C_total + C_resp of the committed ``fd_data_product.json`` (sha256 ``b79556f0...``),
which has no run-period block; every readout names it. The control's matrix M_d is the sum of the drawn blocks of S1's
assembly npz (``db000707...``): stat, the 38 universe bands, the 5 laterals and the normalization (the seed block is not
drawn: the estimator seed is fixed). A matrix M on the data's f is applied at a truth T in relative form,
M^T = diag(x_T / f) M diag(x_T / f), so sigma_c^T = sqrt(M_cc) / f_c x_T,c.

Toy c-values: x_hat = (U x_raw + sum_b s_b Delta_b^T / 2) (1 + 0.014 z), Delta_b the endpoint difference of S1's lateral
unfolds (X01 applied, through ``s1_assemble``'s own functions) carried to T as M is, and s_b, z the toy's recorded
draws. z_tc = (x_hat_tc - x_T,c) / sigma_c^T.

The pooled statistics, the toy bootstrap, the windows, the two-sided verdict and the positive control are VL169's
committed functions (``2d-unfolding/uq/coverage_fixed_truth/score_coverage.py``), called with this study's generator
seed 20261030; the one-sided rule, the per-cell statistics, the Wilson flags and 4A are added here.

    fd_1b_score.py score  --arm control --look interim --toys DIR --tag T ... --out readout.json
    fd_1b_score.py gate-d --derivation DIR --tag T ... --out gate-d.json
    fd_1b_score.py repro  --pair OURS=F1C ... --f1c-sums SUMS --out repro.json
    fd_1b_score.py pairs  --full DIR --full-tag T --half DIR --half-tag H ... --out pairs.json

Every subcommand writes its readout (never over an existing file) and prints no cross-section value: only standardized
residuals, coverages, chi-square statistics and ratios. Exit 0 on PASS (or a computed record with no verdict role), 1
on any other verdict, 4 on a refusal before any statistic.

MEASURES: the declared statistics of 1B and 4A on the toys given. CANNOT AUTHORIZE: a change to any interval, matrix,
claim or printed wording; a test arm's PASS is "no undercoverage detected at the study's sensitivity", never a
validation of coverage.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
REPO = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_pseudo  # noqa: E402

_VL = REPO / "2d-unfolding/uq/coverage_fixed_truth/score_coverage.py"
_spec = importlib.util.spec_from_file_location("vl169_score_coverage", _VL)
vl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vl)

S1_NPZ_SHA256 = "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4"
DATA_PRODUCT = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/data-product/fd_data_product.json"
DATA_PRODUCT_SHA256 = "b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072"
REPORTED_KEY = "C_total_plus_C_resp"
MATRIX_TESTED = ("the reported C_total + C_resp of fd_data_product.json (sha256 b79556f0...) as on main when 1B was "
                 "declared (91a27ad1); it holds no run-period block")
SURROGATE_NOTE = ("the lateral and normalization surrogates carry {share:.1%} of C_e's trace: the toys carry them and "
                  "do not test them; {tested:.1%} is tested through the estimator")
N_BOOT, BOOT_SEED = 20_000, 20_261_030
LEVEL = {"interim": 0.995, "final": 0.95}
N_TOYS = {"interim": 100, "final": 300}
TEST_ARMS = ("g18", "ar23")
SCORED_ARMS = ("control",) + TEST_ARMS
WILSON_LEVEL, FLAG_LEVEL = 0.95, 0.995
SCALE_TOLERANCE = vl.BAND_RATIO_TOLERANCE          # (0.9, 1.1)
CONTROL_SCALES = vl.CONTROL_SCALES                 # (0.7, 1.3)
NOMINAL = vl.NOMINAL                               # {1: 0.682689..., 2: 0.954499...}
WINDOWS = vl.WINDOWS                               # {1: (0.631880, 0.728668), 2: (0.928139, 0.972193)}
CHI2_DOF = sa.N_CELLS
CHI2_Q95 = 26.296227604864239                      # chi2_16's 95th percentile
NORM = sa.NORM_FRACTION
GATE_D_WINDOW = SCALE_TOLERANCE
STOP_VERDICTS = ("FAIL-undercoverage", "FAIL-overcoverage", "FAIL-mixed", "INCONCLUSIVE", "INVALID", "INSUFFICIENT")


class Invalid(ValueError):
    """A declared validity check fails: the verdict is INVALID, a stop."""


class Insufficient(ValueError):
    """The look's declared toy set is incomplete: a stop."""


# ---------------------------------------------------------------------------------------------- chi-square, Wilson


def chi2_sf(x: float, dof: int = CHI2_DOF) -> float:
    """P(chi2_dof > x) for even dof, in closed form: exp(-x/2) sum_{j < dof/2} (x/2)^j / j!."""
    if dof % 2:
        raise ValueError("closed form for even dof only")
    h = x / 2.0
    return math.exp(-h) * sum(h ** j / math.factorial(j) for j in range(dof // 2))


def chi2_windows() -> dict:
    """The 4A windows: the matrix-to-scatter scale s in [0.9, 1.1] maps the mean to dof / s^2 and the tail fraction
    above the 95th percentile to P(chi2 > q95 s^2)."""
    lo, hi = SCALE_TOLERANCE
    return {"mean": (CHI2_DOF / hi ** 2, CHI2_DOF / lo ** 2),
            "tail": (chi2_sf(CHI2_Q95 * hi ** 2), chi2_sf(CHI2_Q95 * lo ** 2))}


def wilson(k: int, n: int, level: float) -> tuple[float, float]:
    z = statistics.NormalDist().inv_cdf((1 + level) / 2)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - half, mid + half


def flag_threshold(n: int, k_sigma: int) -> int:
    """The largest count whose Wilson 99.5 % upper bound lies below nominal: at or below it a cell is flagged."""
    return max((k for k in range(n + 1) if wilson(k, n, FLAG_LEVEL)[1] < NOMINAL[k_sigma]), default=-1)


# --------------------------------------------------------------------------------------------------- the matrices


def load_s1(path: Path) -> dict:
    sa.require_sha(path, S1_NPZ_SHA256, "S1 assembly")
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    want = sorted(["stat", "normalization", "seed"] + [f"band:{b}" for b in sa.EXPECT] +
                  [f"lat:{b}" for b in sa.LATERAL_BANDS])
    if sorted(meta["blocks"]) != want:
        raise SystemExit(f"S1 assembly blocks {sorted(meta['blocks'])} are not the declared set")
    blocks = {k: np.asarray(z["C_" + k.replace(":", "_")], float) for k in meta["blocks"]}
    return {"f": np.asarray(z["f"], float), "U": np.asarray(z["U"], float), "blocks": blocks,
            "C_e": np.asarray(z["C_e"], float)}


def drawn_matrix(s1: dict) -> np.ndarray:
    """M_d: every S1 block the toys draw (all but the seed block)."""
    return sum(v for k, v in s1["blocks"].items() if k != "seed")


def reported_matrix(s1: dict) -> np.ndarray:
    sa.require_sha(DATA_PRODUCT, DATA_PRODUCT_SHA256, "data product")
    d = json.loads(DATA_PRODUCT.read_text())
    if not np.array_equal(np.asarray(d["f"], float), s1["f"]):
        raise SystemExit("the data product's f is not S1's f")
    return np.asarray(d["matrices"][REPORTED_KEY], float)


def surrogate_share(s1: dict) -> float:
    f = s1["f"]
    rel = lambda C: np.trace(C / np.outer(f, f))  # noqa: E731
    sur = sum(v for k, v in s1["blocks"].items() if k.startswith("lat:") or k == "normalization")
    return float(rel(sur) / rel(s1["C_e"]))


def lateral_deltas(s1: dict, lateral_dir: Path, definition: Path, inputs_npz: Path, x01: Path, manifest: Path) -> dict:
    """Delta_b = U x(endpoint 1) - U x(endpoint 0), through s1_assemble's map, X01 rescale and digest checks; the
    S1 block (1/4) Delta Delta^T must be reproduced."""
    U = sa.functional_matrix(sa.fine_map(definition))
    sa.require_sha(inputs_npz, sa.INPUT_NPZ_SHA256, "of_inputs_5d.npz")
    flux = np.asarray(np.load(inputs_npz, allow_pickle=False)["flux"], float)
    scale, pti = sa.x01_scale(x01, flux), sa.pt_index()
    man = sa.load_manifest(manifest)
    out = {}
    for b in sa.LATERAL_BANDS:
        X = []
        for i in (0, 1):
            p = lateral_dir / f"lat_{b}_{i}_b-_j-.npz"
            sa.require_listed(p, man, "lateral")
            x = sa.xs(p) * scale[i][pti] if b == sa.MINOS else sa.xs(p)
            X.append(U @ x)
        delta = X[1] - X[0]
        if not np.allclose(0.25 * np.outer(delta, delta), s1["blocks"][f"lat:{b}"], rtol=1e-10, atol=0.0):
            raise SystemExit(f"lateral {b}: (1/4) Delta Delta^T does not reproduce S1's block")
        out[b] = delta
    return out


def transfer(M: np.ndarray, f: np.ndarray, x_t: np.ndarray) -> np.ndarray:
    g = x_t / f
    return M * np.outer(g, g)


# ------------------------------------------------------------------------------------------------------- the toys


def declared_groups() -> dict[str, list[str]]:
    return {b: [f"{b}_{i}" for i in range(sa.EXPECT[b])] for b in toys.INTERACTION_BANDS}


def load_toys(toy_dir: Path, tag: str, arm: str, seeds: list[int], U: np.ndarray, flux_p: np.ndarray,
              mode: str = "toy") -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """The declared toys of a look: every one present, made by the declared estimator, with its draw equal to the
    draw re-derived from its seed. In toy mode all share one truth, and U x_T is returned once; in half mode each
    toy's truth is its own seed's split's, and U x_T is returned per toy: its recorded split is checked here, and its
    stored truth against that split by the toy mode at production (``fd_1b_toys.half_truth``; the scorer does not load
    the MC). Returns (U x_raw per toy, U x_T, draws)."""
    partial = sorted(p.name for p in toy_dir.glob(f"{tag}_s*.npz.partial-*"))
    if partial:
        raise Invalid(f"interrupted products present: {partial[:3]}")
    missing = [s for s in seeds if not (toy_dir / f"{tag}_s{s}.npz").exists()]
    if missing:
        raise Insufficient(f"{len(missing)} of {len(seeds)} declared toys are missing (first {missing[0]})")
    groups = declared_groups()
    truth_name = toys.ARMS[arm][0]
    expect = {"arm": arm, "mode": mode, "no_draws": False, "truth": truth_name,
              "truth_ratio_sha256": toys.committed_ratio_sha256(truth_name)}
    X, draws, truths, code = [], [], [], None
    for s in seeds:
        p = toy_dir / f"{tag}_s{s}.npz"
        try:
            m = sa.check_meta(p, toys.SCHEMA, expect=dict(expect, pseudo_seed=s))
        except SystemExit as e:
            raise Invalid(str(e)) from None
        if m.get("numpy_version") != np.__version__:
            # the draw is re-derived with numpy's Generator, whose streams numpy does not promise across versions:
            # a scorer in another environment refuses (exit 4) rather than grading every toy INVALID
            raise SystemExit(f"{p.name} was made under numpy {m.get('numpy_version')}, the scorer runs {np.__version__}")
        if code is None:
            code = m.get("code_sha256")
        elif m.get("code_sha256") != code:
            raise Invalid(f"{p.name}: made by different code from the arm's first toy")
        want = json.loads(json.dumps(toys.draw_for_seed(s, flux_p, groups)))
        got = {k: m["draw"].get(k) for k in want} if m.get("draw") else None
        if got != want:
            raise Invalid(f"{p.name}: its recorded draw departs from the declared draw for seed {s}")
        if mode == "half" and (m.get("experiment") or {}).get("split_key") != s5c_pseudo.split_key_for(s):
            raise Invalid(f"{p.name}: its recorded split is not seed {s}'s")
        z = np.load(p, allow_pickle=False)
        xt = np.asarray(z["xtrue_flat"], float)
        if not np.all(np.isfinite(xt)):
            raise Invalid(f"{p.name}: a non-finite truth")
        if mode in toys.FIXED_TRUTH_MODES and truths and not np.array_equal(xt, truths[0]):
            raise Invalid(f"{p.name}: its stored truth differs from the arm's first toy's")
        truths.append(xt)
        x = np.asarray(z["xsec_flat"], float)
        if not np.all(np.isfinite(x)):
            raise Invalid(f"{p.name}: a non-finite unfolded value")
        X.append(U @ x)
        draws.append(want)
    T = np.array([U @ t for t in truths])
    return np.array(X), (T[0] if mode in toys.FIXED_TRUTH_MODES else T), draws


def surrogate(X_raw: np.ndarray, draws: list[dict], deltas: dict, f: np.ndarray, x_t: np.ndarray) -> np.ndarray:
    """x_hat = (U x_raw + sum_b s_b Delta_b^T / 2) (1 + 0.014 z), Delta_b^T = Delta_b x_T / f, with x_T one truth or
    one per toy (half mode)."""
    g = np.broadcast_to(x_t / f, X_raw.shape)
    out = np.empty_like(X_raw)
    for t, d in enumerate(draws):
        lat = sum(d["lateral_s"][b] * deltas[b] * g[t] / 2.0 for b in sa.LATERAL_BANDS)
        out[t] = (X_raw[t] + lat) * (1.0 + NORM * d["normalization_z"])
    return out


# ----------------------------------------------------------------------------------------------------- statistics


def per_cell(X: np.ndarray, x_t: np.ndarray, sigma: np.ndarray) -> dict:
    z = (X - x_t[None, :]) / sigma[None, :]
    n = z.shape[0]
    out = {"cells": [f"R{c:02d}" for c in range(z.shape[1])], "n_toys": n, "pull_mean": z.mean(axis=0).tolist(),
           "pull_rms": np.sqrt((z * z).mean(axis=0)).tolist()}
    for k in (1, 2):
        cnt = (np.abs(z) <= k).sum(axis=0)
        c = cnt / n
        out[f"c{k}"] = c.tolist()
        out[f"c{k}_se"] = np.sqrt(c * (1 - c) / n).tolist()
        out[f"c{k}_wilson95"] = [list(wilson(int(m), n, WILSON_LEVEL)) for m in cnt]
        out[f"c{k}_flag_measured_undercoverage"] = [bool(wilson(int(m), n, FLAG_LEVEL)[1] < NOMINAL[k]) for m in cnt]
        out[f"c{k}_summary"] = {"median": float(np.median(c)), "min": float(c.min()), "max": float(c.max())}
    return out


def pooled(X, x_t, f, sigma_f, scale, level) -> dict:
    """VL169's ``score``: z with sigma = scale (sigma_f / f) x_T, the toy-bootstrap intervals, the two-sided verdict."""
    return vl.score(X, x_t, f, sigma_f, np.ones(x_t.size, bool), scale, level, N_BOOT, BOOT_SEED)


def one_sided(intervals: dict) -> str:
    """A test arm: FAIL (measured undercoverage) iff the C1 or C2 interval lies wholly below nominal."""
    return "FAIL" if any(intervals[f"C{k}"][1] < NOMINAL[k] for k in (1, 2)) else "PASS"


def score_control(X, x_t, f, M_d, look) -> dict:
    sig = np.sqrt(np.diag(M_d))
    base = pooled(X, x_t, f, sig, 1.0, LEVEL[look])
    scaled = {s: pooled(X, x_t, f, sig, s, LEVEL[look]) for s in CONTROL_SCALES}
    pc = vl.positive_control(base, scaled)
    v = base["verdict"]
    if v == "PASS" and not pc["passes"]:
        v = "INCONCLUSIVE"
    if look == "interim" and not v.startswith("FAIL"):
        v = "CONTINUE"
    return {"base": base, "scaled": {str(s): scaled[s] for s in CONTROL_SCALES}, "positive_control": pc, "verdict": v,
            "per_cell": per_cell(X, x_t, sig / f * x_t)}


def score_test_arm(X, x_t, f, R, M_d, look) -> dict:
    sig = np.sqrt(np.diag(R))
    base = pooled(X, x_t, f, sig, 1.0, LEVEL[look])
    low = pooled(X, x_t, f, sig, CONTROL_SCALES[0], LEVEL[look])
    v, v_low = one_sided(base["intervals"]), one_sided(low["intervals"])
    pc_ok = v_low == "FAIL"
    verdict = v if (v == "FAIL" or pc_ok) else "INCONCLUSIVE"
    if look == "interim" and verdict != "FAIL":
        verdict = "CONTINUE"
    ratio = np.sqrt(np.diag(R) / np.diag(M_d))
    cells = per_cell(X, x_t, sig / f * x_t)
    return {"base": base, "scaled_0.7": low, "one_sided": v, "one_sided_0.7": v_low, "positive_control_passes": pc_ok,
            "verdict": verdict,
            "meaning": ("no undercoverage detected at the study's sensitivity, at this truth, under the nominal detector "
                        "response" if verdict == "PASS" else
                        "measured undercoverage, reported as measured" if verdict == "FAIL" else None),
            "sensitivity": {"C1_half_width": (base["intervals"]["C1"][1] - base["intervals"]["C1"][0]) / 2,
                            "C2_half_width": (base["intervals"]["C2"][1] - base["intervals"]["C2"][0]) / 2,
                            "per_cell_se_c1": cells["c1_se"], "per_cell_se_c2": cells["c2_se"]},
            "flagged_cells": {f"c{k}": [c for c, fl in zip(cells["cells"], cells[f"c{k}_flag_measured_undercoverage"]) if fl]
                              for k in (1, 2)},
            "expected_if_spread_is_M_d_context_only": {
                "c1": [math.erf(r / math.sqrt(2)) for r in ratio], "c2": [math.erf(2 * r / math.sqrt(2)) for r in ratio]},
            "per_cell": cells}


def chi2_values(X: np.ndarray, centre: np.ndarray, M: np.ndarray) -> np.ndarray:
    """(x - centre)^T M^-1 (x - centre) per toy, by Cholesky with no ridge or floor; refuses a matrix that is not PD."""
    try:
        L = np.linalg.cholesky(M)
    except np.linalg.LinAlgError:
        raise Invalid("the 4A matrix is not positive definite") from None
    y = np.linalg.solve(L, (X - centre).T)
    return (y * y).sum(axis=0)


def chi2_cdf(x: float) -> float:
    return 1.0 - chi2_sf(x)


def chi2_grade(chi2: np.ndarray, level: float = 0.95) -> dict:
    n = chi2.size
    idx = np.random.default_rng(BOOT_SEED).integers(0, n, size=(N_BOOT, n))
    lo, hi = 100 * (1 - level) / 2, 100 * (1 + level) / 2
    tail = (chi2 > CHI2_Q95).astype(float)
    ci = {"mean": [float(np.percentile(chi2[idx].mean(axis=1), q)) for q in (lo, hi)],
          "tail": [float(np.percentile(tail[idx].mean(axis=1), q)) for q in (lo, hi)]}
    win = chi2_windows()
    cls = {k: vl.classify(ci[k], win[k]) for k in ci}
    # a chi-square above its window means the matrix is too small for the scatter (undercoverage), below too large
    side = {c.replace("above", "under").replace("below", "over") for c in cls.values() if c in ("above", "below")}
    v = ("PASS" if all(c == "inside" for c in cls.values()) else "FAIL-undercoverage" if side == {"under"} else
         "FAIL-overcoverage" if side == {"over"} else "FAIL-mixed" if side else "INCONCLUSIVE")
    xs = np.sort(chi2)
    F = np.array([chi2_cdf(x) for x in xs])
    ks = float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(n) / n)))
    return {"n_toys": n, "mean": float(chi2.mean()), "tail_fraction": float(tail.mean()), "intervals": ci,
            "windows": win, "classification": cls, "verdict": v, "ks_distance_no_verdict_role": ks}


def four_a(X, x_t, f, M_d, R, arm) -> dict:
    """4A gates nothing (binding ruling 4), so a matrix it cannot invert refuses 4A alone, never the coverage verdict.
    It is graded at the control only (the same ruling): at a test arm the mean-subtracted statistics are printed with
    their intervals and no verdict."""
    try:
        Md_t = transfer(M_d, f, x_t)
        if arm == "control":
            return {"gates": "nothing", "graded": chi2_grade(chi2_values(X, x_t, Md_t))}
        n = X.shape[0]
        centred = chi2_grade(chi2_values(X, X.mean(axis=0), Md_t) * n / (n - 1))
        centred["verdict"] = None
        about = {name: chi2_values(X, x_t, M) for name, M in (("M_d", Md_t), ("reported", transfer(R, f, x_t)))}
    except Invalid as e:
        return {"gates": "nothing", "refused": str(e)}
    return {"gates": "nothing", "mean_subtracted_no_verdict": centred,
            "about_truth_no_verdict": {k: {"mean": float(v.mean()), "tail_fraction": float((v > CHI2_Q95).mean())}
                                       for k, v in about.items()}}


# --------------------------------------------------------------------------------------------------- subcommands


def _common_inputs(a) -> tuple[dict, np.ndarray, np.ndarray, dict, np.ndarray]:
    s1 = load_s1(a.s1_npz)
    M_d = drawn_matrix(s1)
    R = reported_matrix(s1)
    deltas = lateral_deltas(s1, a.lateral_dir, a.definition, a.inputs_npz, a.x01, a.manifest)
    flux_p = toys.flux_probabilities(a.flux_constraint)
    return s1, M_d, R, deltas, flux_p


def header(s1: dict, label: str) -> dict:
    share = surrogate_share(s1)
    return {"label": label, "matrix_tested": MATRIX_TESTED, "data_product_sha256": DATA_PRODUCT_SHA256,
            "s1_npz_sha256": S1_NPZ_SHA256,
            "surrogates": SURROGATE_NOTE.format(share=share, tested=1 - share), "surrogate_share_of_C_e_trace": share,
            "code_sha256": {p.name: sa.sha256(p) for p in (Path(__file__).resolve(), _ND / "fd_1b_toys.py", _VL)},
            "boot": {"n": N_BOOT, "seed": BOOT_SEED}}


def cmd_score(a) -> tuple[dict, int]:
    s1, M_d, R, deltas, flux_p = _common_inputs(a)
    first = toys.ARMS[a.arm][1]
    seeds = list(range(first, first + N_TOYS[a.look]))
    out = header(s1, "RESULT")
    out.update({"arm": a.arm, "look": a.look, "level": LEVEL[a.look], "seeds": [seeds[0], seeds[-1]]})
    try:
        X_raw, x_t, draws = load_toys(a.toys, a.tag, a.arm, seeds, s1["U"], flux_p)
    except (Invalid, Insufficient) as e:
        out.update({"verdict": "INVALID" if isinstance(e, Invalid) else "INSUFFICIENT", "reason": str(e)})
        return out, 1
    X = surrogate(X_raw, draws, deltas, s1["f"], x_t)
    try:
        if a.arm == "control":
            out["coverage"] = score_control(X, x_t, s1["f"], M_d, a.look)
        else:
            out["coverage"] = score_test_arm(X, x_t, s1["f"], R, M_d, a.look)
        if a.look == "final":
            out["4A"] = four_a(X, x_t, s1["f"], M_d, R, a.arm)
    except (Invalid, vl.InvalidInput) as e:
        out.update({"verdict": "INVALID", "reason": str(e)})
        return out, 1
    out["verdict"] = out["coverage"]["verdict"]
    if a.arm == "control" and out["verdict"] != "PASS" and out["verdict"] != "CONTINUE":
        out["stop"] = ("STOP: the control did not pass; no production toy runs, and the machinery is ungraded: nothing "
                       "is said about the reported intervals")
    return out, 0 if out["verdict"] in ("PASS", "CONTINUE") else 1


def cmd_gate_d(a) -> tuple[dict, int]:
    s1 = load_s1(a.s1_npz)
    M_d = drawn_matrix(s1)
    f, U = s1["f"], s1["U"]
    w = sa.flux_weights(a.flux_constraint)
    out = header(s1, "DERIVATION")
    x = {}
    for tag in ["CV"] + toys.s1_universes():
        p = a.derivation / f"{a.tag}_{tag}.npz"
        if not p.exists():
            out.update({"verdict": "INSUFFICIENT", "reason": f"no derivation product for {tag}"})
            return out, 1
        try:
            m = sa.check_meta(p, toys.SCHEMA, expect={"arm": "derivation", "mode": "derivation", "universe": tag})
        except SystemExit as e:
            out.update({"verdict": "INVALID", "reason": str(e)})
            return out, 1
        if json.loads(json.dumps(toys.single_universe(tag))) != m["draw"]:
            out.update({"verdict": "INVALID", "reason": f"{p.name}: its draw is not universe {tag} alone"})
            return out, 1
        x[tag] = U @ np.asarray(np.load(p, allow_pickle=False)["xsec_flat"], float)
    truth = None
    for tag in x:
        xt = np.asarray(np.load(a.derivation / f"{a.tag}_{tag}.npz", allow_pickle=False)["xtrue_flat"], float)
        if truth is None:
            truth = xt
        elif not np.array_equal(xt, truth):
            out.update({"verdict": "INVALID", "reason": f"derivation product {tag}: its truth differs from CV's"})
            return out, 1
    # carried to f as the control's intervals are: sigma_c^T = sqrt(M_cc) / f_c x_T,c, so a toy covariance E in the
    # toy's space predicts the control through diag(f / x_T) E diag(f / x_T) (review finding 1: not f / x_hat(CV))
    g = f / (U @ truth)
    E = {k: v for k, v in s1["blocks"].items() if k == "stat" or k == "normalization" or k.startswith("lat:")}
    for b in sorted(sa.EXPECT):
        X = np.array([x[f"{b}_{i}"] for i in range(sa.EXPECT[b])])
        E[f"band:{b}"] = sa.mat_cov(X, w if b == sa.FLUX else None) * np.outer(g, g)
    E_d = sum(E.values())
    rho = np.sqrt(np.diag(E_d) / np.diag(M_d))
    per_group = {}
    for grp in ("flux", "interaction", "detector"):
        e = sum(v for k, v in E.items() if k.startswith("band:") and sa.group_of(k) == grp)
        m = sum(v for k, v in s1["blocks"].items() if k.startswith("band:") and sa.group_of(k) == grp)
        per_group[grp] = np.sqrt(np.diag(e) / np.diag(m)).tolist()
    ok = bool(np.all((rho >= GATE_D_WINDOW[0]) & (rho <= GATE_D_WINDOW[1])))
    out.update({"cells": [f"R{c:02d}" for c in range(sa.N_CELLS)], "rho": rho.tolist(), "window": list(GATE_D_WINDOW),
                "per_group_sigma_ratio": per_group, "verdict": "PASS" if ok else "FAIL",
                "what_it_measures": ("how far the fixed-truth mechanics (response only, truth kept in every fine cell) "
                                     "reproduce S1's blocks (prior and response): the first-order prior-part gap")})
    if not ok:
        out["stop"] = "STOP before any coverage toy: the control would be predicted to fail by construction"
    return out, 0 if ok else 1


def cmd_repro(a) -> tuple[dict, int]:
    sums = {}
    for line in a.f1c_sums.read_text().splitlines():
        sha, name = line.split("  ", 1)
        sums[name.removeprefix("./")] = sha
    rows, ok = [], True
    for pair in a.pair:
        ours, theirs = (Path(p) for p in pair.split("="))
        rel = str(theirs.relative_to(a.f1c_runs))
        if theirs.parent == theirs or a.f1c_runs not in theirs.parents:
            raise SystemExit(f"{theirs} is not under the F1c runs root {a.f1c_runs}")
        if sums.get(rel) is None or sa.sha256(theirs) != sums[rel]:
            raise SystemExit(f"{theirs} is not the F1c product its manifest records")
        m = json.loads(str(np.load(ours, allow_pickle=False)["meta"]))
        if (m.get("schema"), m.get("mode"), m.get("no_draws")) != (toys.SCHEMA, "half", True):
            raise SystemExit(f"{ours} is not a reproduction run")
        x1, x2 = (np.load(p, allow_pickle=False)["xsec_flat"] for p in (ours, theirs))
        same = bool(x1.dtype == x2.dtype and x1.shape == x2.shape and np.array_equal(x1, x2))
        ok &= same
        rows.append({"ours": ours.name, "f1c": rel, "bitwise_equal": same})
    out = {"label": "DERIVATION", "rows": rows, "verdict": "PASS" if ok else "FAIL"}
    if not ok:
        out["stop"] = "STOP: the toy mode with every draw off does not reproduce F1c"
    return out, 0 if ok else 1


def cmd_pairs(a) -> tuple[dict, int]:
    """The half-MC pilots against the full-MC pilots of the same seeds, each in sigma of its own truth, with no verdict.
    Both output arrays have one row per seed: the half toys' truths are their own splits'."""
    s1, M_d, R, deltas, flux_p = _common_inputs(a)
    first = toys.ARMS["pilot"][1]
    seeds = list(range(first, first + a.n))
    Xf, xt_f, df = load_toys(a.full, a.full_tag, "pilot", seeds, s1["U"], flux_p, "toy")
    Xh, xt_h, dh = load_toys(a.half, a.half_tag, "pilot", seeds, s1["U"], flux_p, "half")
    rel = np.sqrt(np.diag(M_d)) / s1["f"]
    zf = (surrogate(Xf, df, deltas, s1["f"], xt_f) - xt_f) / (rel * xt_f)
    zh = (surrogate(Xh, dh, deltas, s1["f"], xt_h) - xt_h) / (rel * xt_h)
    out = header(s1, "DERIVATION")
    out.update({"seeds": [seeds[0], seeds[-1]], "per_cell_paired_difference_full_minus_half_in_sigma": (zf - zh).tolist(),
                "truth_difference_in_sigma": ((xt_f - xt_h) / (rel * xt_f)).tolist(), "verdict": None})
    return out, 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, toyreader=True):
        p.add_argument("--s1-npz", type=Path, required=True)
        p.add_argument("--flux-constraint", type=Path, required=True)
        if toyreader:
            p.add_argument("--lateral-dir", type=Path, required=True)
            p.add_argument("--definition", type=Path, required=True)
            p.add_argument("--inputs-npz", type=Path, required=True)
            p.add_argument("--x01", type=Path, required=True)
            p.add_argument("--manifest", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)

    s = sub.add_parser("score")
    s.add_argument("--arm", choices=SCORED_ARMS, required=True)
    s.add_argument("--look", choices=sorted(LEVEL), required=True)
    s.add_argument("--toys", type=Path, required=True)
    s.add_argument("--tag", required=True)
    common(s)
    g = sub.add_parser("gate-d")
    g.add_argument("--derivation", type=Path, required=True)
    g.add_argument("--tag", required=True)
    common(g, toyreader=False)
    r = sub.add_parser("repro")
    r.add_argument("--pair", action="append", required=True, help="OURS=F1C product paths")
    r.add_argument("--f1c-sums", type=Path, required=True)
    r.add_argument("--f1c-runs", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    q = sub.add_parser("pairs")
    q.add_argument("--full", type=Path, required=True)
    q.add_argument("--full-tag", required=True)
    q.add_argument("--half", type=Path, required=True)
    q.add_argument("--half-tag", required=True)
    q.add_argument("--n", type=int, default=8)
    common(q)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"[fd-1b-score] refusing to overwrite {a.out}", file=sys.stderr)
        return 4
    try:
        out, rc = {"score": cmd_score, "gate-d": cmd_gate_d, "repro": cmd_repro, "pairs": cmd_pairs}[a.cmd](a)
    except (SystemExit, OSError, ValueError) as e:
        # a refusal before any statistic: a digest, a missing or unreadable file, an environment mismatch
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-score] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4
    a.out.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({"out": str(a.out), "verdict": out.get("verdict")}))
    return rc


if __name__ == "__main__":
    sys.exit(main())

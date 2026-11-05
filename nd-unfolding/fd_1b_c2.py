#!/usr/bin/env python3
"""1B's pre-bulk C2 gate (FD-1B-STAGED-ADDENDUM-A2-1.md): Joseph's clip rule (#718) read through cov2d's code, with
Joseph's 16-cell variance gate (#724) and its null calibration.

* ``gate_724``: per truth, C2's clipped-composition variance ratio passes only if (i) at most 2 of the 16 cells have
  |ratio - 1| > 0.20, (ii) |mean over cells of log ratio| <= 0.07 and (iii) max |ratio - 1| <= 0.35.
* ``reading_1b``: ``clip_probe2.reading`` with each composition's variance gate a parameter. Under C2's own gate it
  equals clip_probe2.reading (tested over a grid); 1B calls it with #724 on ``option_1_clipped`` and C2's 95 % rule,
  descriptive, on the others (the director's ruling). It reads "option (1)" exactly when q1 and the mismatch is
  bounded, so only the clipped ratio's gate can move it.
* ``band_reference``: ``clip_probe2.band_reference`` with the band layout a parameter (cov2d's hard-codes its own);
  1B's is S1's 38 bands, every one drawn, Flux by the constraint's weights and the rest uniform (``toys.draw``).
* ``xt_flat``: 1B's graded truth (``s5n_pseudo.true_xsec`` through ``xsec_nd.extract_cross_section_nd``) from its
  fine-cell sums, batched over draws, in the extraction's own operation order.
* ``calibrate``: the noise-only rates of (i)-(iii) on null natures (unclipped, first order) from streams disjoint from
  every declared draw, at the director's outputs (a)-(c), the power of (ii) against a uniform 10 % deflation, and the
  two parts of the D4 control: the draw law on a linear count (exact) and x_T's linearisation.

MEASURES: rates, SDs and controls of a gate. CANNOT AUTHORIZE: a threshold change, a verdict on 1B's coverage.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

import fd_1b_toys as toys
import s1_assemble as sa

_REPO = Path(__file__).resolve().parents[1]
CP2_DIR = _REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip"
COV2D_DIR = _REPO / "2d-unfolding/cov2d"
for _p in (CP2_DIR, COV2D_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import clip_probe2 as cp2  # noqa: E402
import cov2d  # noqa: E402

N_CELLS = sa.N_CELLS
GATE_K, GATE_DEV, GATE_LOGMEAN, GATE_MAX = 2, 0.20, 0.07, 0.35   # #724 (i), (i)'s deviation, (ii), (iii)
SD_MULT_LOGMEAN, SD_MULT_CELL = 3.5, 4.3      # the director's (c): the consult's SE multiples (ANSWER.txt:26-27)
UNION_LIMIT = 0.01                            # the director's: a three-truth noise STOP above this goes to Joseph
DEFLATION = 0.9                               # the power of (ii) against a uniform 10 % deflation
CONTROL_Z = 4.0                               # D4's law control: |mean - 1| <= 4 SE per cell (48 z: ~0.3 % false)
LINEARISATION_TOL = 0.02                      # the director's W1: x_T's |mean ratio - 1| per cell, per truth
CAL_SETS = 10_000                             # replicate sets of 300 draws per truth
CAL_SEED = {"g18": 3_671_000, "ar23": 3_672_000, "plugin": 3_673_000}
CAL_SALT = 20_261_103_7                       # [CAL_SEED, set, CAL_SALT]: see calibration_draws on why it is disjoint
CLIPPED = "option_1_clipped"
# Joseph's large-sample gate (DECISION-20261104-joseph-1b-large-sample-gate.md; the director's P1-P7)
GATE_N = 3000                                 # draws per truth in the gate sample; the first 300 are the declared toys
GATE_SEED_BASE = {"g18": 3_680_000, "ar23": 3_690_000, "plugin": 3_700_000}   # the next GATE_N - 300 seeds
S_GRID = tuple(round(0.50 + 0.01 * k, 2) for k in range(251))              # P2: s on a 0.01 grid, 0.50 to 3.00
POWER_MIN = 0.80                              # P4: per truth, against a uniform deflation of UNIFORM_DEFLATION
UNIFORM_DEFLATION = 0.08
CONCENTRATED = ((1, 0.20), (2, 0.15), (4, 0.10))   # P4: (cells, deflation), reported, not required
PLACEMENTS = 16
BACKSTOP_SD_MULT = 4.3                        # P6: (iii) by (alpha) on the 300 declared draws, with (i) at k = 2


class Refusal(RuntimeError):
    """A gate input is not what the gate is defined on."""


# ------------------------------------------------------------------------------------------------------- the gate


def gate_724(ratio) -> dict:
    """#724 on one truth's 16 per-cell ratios: the three statistics, each rule, and the verdict."""
    r = np.asarray(ratio, np.float64)
    if r.shape != (N_CELLS,) or not np.all(np.isfinite(r)) or np.any(r <= 0):
        raise Refusal(f"#724 needs {N_CELLS} finite positive ratios")
    dev = np.abs(r - 1.0)
    out = {"cells_beyond": int(np.sum(dev > GATE_DEV)), "mean_log": float(np.mean(np.log(r))),
           "max_dev": float(np.max(dev))}
    out["i"] = out["cells_beyond"] <= GATE_K
    out["ii"] = abs(out["mean_log"]) <= GATE_LOGMEAN
    out["iii"] = out["max_dev"] <= GATE_MAX
    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])
    return out


def c2_gate(v) -> bool:
    """C2's own variance gate (clip_probe2.reading): |ratio - 1| <= VAR_GATE in at least VAR_SHARE of the cells."""
    return float(np.mean(np.abs(np.asarray(v) - 1) <= cp2.VAR_GATE)) >= cp2.VAR_SHARE


GATES_1B = {CLIPPED: lambda v: gate_724(v)["passes"], "first_order": c2_gate, "multiplicative": c2_gate}


def reading_1b(rec: dict, gates: dict | None = None) -> dict:
    """``clip_probe2.reading`` (c2_reading.txt) with each composition's variance gate taken from ``gates`` (default:
    C2's own, under which this equals clip_probe2.reading). Every other number is clip_probe2's constant."""
    gates = gates or {}
    out = {}
    worst = rec["vi"]["largest_cell_unmatched_share"]
    bounded = worst is not None and worst <= cp2.MISMATCH_BOUND
    for t, b in rec["b"].items():
        R = b["option_1"]["sigma_Q"]
        med, p90 = np.array(R["abs_median"]), np.array(R["abs_p90"])
        vr = {k: np.array(v) for k, v in b["variance_ratio"].items()}
        gate = {k: bool(gates.get(k, c2_gate)(v)) for k, v in vr.items()}
        q1 = bool(np.all(med <= cp2.R1_MEDIAN) and np.mean(p90 <= cp2.R1_P90) >= cp2.R1_P90_SHARE
                  and gate[CLIPPED])
        pos = bool((np.mean(med > cp2.POS_MEDIAN) > cp2.POS_SHARE or np.any(p90 > cp2.POS_P90))
                   and gate["multiplicative"])
        opt3 = bool((np.mean(med >= cp2.OPT3_MEDIAN) >= cp2.OPT3_SHARE
                     and not (gate[CLIPPED] or gate["multiplicative"])) or not bounded)
        pick = ("option (3)" if opt3 else "option (1)" if q1 else
                "positivity-preserving (multiplicative) composition" if pos else "no rule of the reading fires")
        out[t] = {"option_1_qualifies": q1, "positivity_preferred": pos, "option_3_applies": opt3,
                  "variance_gate_passes": gate, "mismatch_bounded": bounded, "reads": pick}
    picks = {v["reads"] for v in out.values()}
    out["overall"] = picks.pop() if len(picks) == 1 else "the tunes read differently: " + "; ".join(
        f"{t} {v['reads']}" for t, v in out.items())
    return out


# ------------------------------------------------------------------------------------------- the draw law


def band_reference(h_u: np.ndarray, w_flux: np.ndarray, order, bands: dict, flux: str) -> np.ndarray:
    """sum_b Var_b of per-universe values ``h_u`` (rows: universes, band by band in ``order``), each band under its
    draw law: ``flux`` by ``w_flux``, every other band uniform. clip_probe2.band_reference with the layout a parameter."""
    h_u = np.asarray(h_u, np.float64)
    if h_u.shape[0] != sum(bands[b] for b in order):
        raise Refusal("one row per universe of the layout is required")
    ref, k = np.zeros(h_u.shape[1]), 0
    for b in order:
        n = bands[b]
        X = h_u[k:k + n]
        p = (w_flux / w_flux.sum()) if b == flux else np.full(n, 1.0 / n)
        mu = p @ X
        ref += p @ (X - mu) ** 2
        k += n
    return ref


def layout_1b() -> tuple[tuple[str, ...], dict, list[str]]:
    """S1's bands in s1_universes' order, their sizes, and the universe tags in the same row order. Every band is
    drawn once per toy (fd_1b_mc.draw_columns refuses otherwise)."""
    order = tuple(sorted(sa.EXPECT))
    tags = toys.s1_universes()
    if [t.rpartition("_")[0] for t in tags] != [b for b in order for _ in range(sa.EXPECT[b])]:
        raise Refusal("s1_universes is not band by band in sorted order")
    return order, dict(sa.EXPECT), tags


def selection(draws: list[list[str]], col: dict[str, int], bands: dict) -> np.ndarray:
    """Draws x universes, 1 where the draw holds the universe; each draw holds one universe of every band."""
    S = np.zeros((len(draws), len(col)))
    for d, tags in enumerate(draws):
        if sorted(t.rpartition("_")[0] for t in tags) != sorted(bands):
            raise Refusal("a draw does not hold exactly one universe of every band")
        S[d, [col[t] for t in tags]] = 1.0
    return S


# ------------------------------------------------------------------------------------------- 1B's graded truth


def xt_flat(A: np.ndarray, B: np.ndarray, D: np.ndarray, flux: np.ndarray, n_nucleons: float, data_pot: float,
            shape: tuple, edges) -> np.ndarray:
    """x_T per fine cell, flattened (C order), for a batch: rows of A = sum w_truth r, B = sum w_truth and D (the
    denominator) per fine cell, and flux (rows, n_pt). It is true_xsec's (completeness B/D where D > 0, else 0) through
    extract_cross_section_nd's expression, element for element, so it matches the bulk's x_T bitwise on equal sums."""
    from xsec_nd import _bin_volume
    A, B, D = (np.asarray(a, np.float64).reshape((-1,) + tuple(shape)) for a in (A, B, D))
    comp = np.zeros_like(B)
    nz = D > 0
    comp[nz] = B[nz] / D[nz]
    vol = _bin_volume(tuple(shape), edges)[None]
    flux_b = np.asarray(flux, float).reshape((-1, shape[0]) + (1,) * (len(shape) - 1))
    denom = comp * flux_b * float(n_nucleons) * float(data_pot) * vol
    good = (denom > 0) & np.isfinite(denom)
    x = np.zeros_like(A)
    np.divide(A * 1.0e4, denom, out=x, where=good)
    return x.reshape(x.shape[0], -1)


def packing(keep: np.ndarray, shape: tuple, edges) -> dict:
    """The constants xt_packed needs for the fine cells ``keep`` (flat indices): their bin volumes and pT bins."""
    from xsec_nd import _bin_volume
    keep = np.asarray(keep, np.int64)
    return {"keep": keep, "vol": _bin_volume(tuple(shape), edges).ravel()[keep],
            "pt": np.unravel_index(keep, tuple(shape))[0]}


def xt_packed(A: np.ndarray, B: np.ndarray, D: np.ndarray, flux: np.ndarray, n_nucleons: float, data_pot: float,
              pack: dict) -> np.ndarray:
    """xt_flat on the fine cells of ``pack`` only (A, B, D: rows x kept cells), with the same operations in the same
    order, so it equals xt_flat's columns ``pack["keep"]`` bitwise."""
    comp = np.zeros_like(B)
    nz = D > 0
    comp[nz] = B[nz] / D[nz]
    denom = comp * np.asarray(flux, float)[:, pack["pt"]] * float(n_nucleons) * float(data_pot) * pack["vol"][None]
    good = (denom > 0) & np.isfinite(denom)
    x = np.zeros_like(A)
    np.divide(A * 1.0e4, denom, out=x, where=good)
    return x


# ----------------------------------------------------------------------------------------------- calibration


def gate_seeds(truth: str) -> list[int]:
    """The gate sample's draw seeds (P1): the declared toys' 300 (fd_1b_mc.TOY_SEEDS), then GATE_N - 300 more from
    GATE_SEED_BASE, drawn by the same toys.draw_for_seed, so the first 300 are the declared draws bit for bit."""
    import fd_1b_mc as mc
    return [int(x) for x in mc.TOY_SEEDS[truth]] + list(range(GATE_SEED_BASE[truth],
                                                              GATE_SEED_BASE[truth] + GATE_N - len(mc.TOY_SEEDS[truth])))


def calibration_draws(truth: str, s: int, flux_p: np.ndarray, groups: dict, n: int = 300) -> list[list[str]]:
    """Replicate set ``s`` of ``truth``: n draws by toys.draw's own law from the stream [CAL_SEED, s, CAL_SALT].
    numpy's SeedSequence zero-pads its entropy, so a two-word [seed, salt] (every declared draw's [seed, DRAW_SALT],
    and the repo's other two-word streams) is the stream [seed, salt, 0]; a three-word stream ending in CAL_SALT != 0
    therefore equals none of them, and distinct (CAL_SEED, set) pairs give distinct streams."""
    if CAL_SALT == 0:
        raise Refusal("CAL_SALT must be non-zero for the streams to be disjoint from every two-word stream")
    from fd_1b_mc import draw_universes
    rng = np.random.default_rng([CAL_SEED[truth], s, CAL_SALT])
    return [draw_universes(toys.draw(rng, flux_p, groups)) for _ in range(n)]


def composite_sums(S: np.ndarray, H: dict, cv: dict) -> dict:
    """First order on the fine sums: H_D = sum_u S_du H_u - (k - 1) H_CV, k the draw's universe count. Each fine sum is
    linear in the row weights, so this is the histogram of compose's per-row composite up to summation order."""
    k = S.sum(axis=1, keepdims=True) - 1.0
    return {q: S @ H[q] - k * cv[q][None, :] for q in ("A", "B", "D")}


def draw_flux(S: np.ndarray, flux_cols: np.ndarray, flux_u: np.ndarray) -> np.ndarray:
    """Each draw's flux (draws x n_pt): its one Flux universe's Phi_u (compose: 'the flux is the one flux universe's')."""
    F = S[:, flux_cols]
    if not np.all(F.sum(axis=1) == 1):
        raise Refusal("a draw does not hold exactly one Flux universe")
    return flux_u[F.argmax(axis=1)]


def set_ratios(S: np.ndarray, H: dict, cv: dict, U: np.ndarray, ref_x: np.ndarray, ref_count: np.ndarray,
               flux_cols: np.ndarray, flux_u: np.ndarray, const: dict) -> tuple[np.ndarray, np.ndarray]:
    """One replicate set, first order, unclipped: per-cell variance ratios (ddof 1) of 1B's graded truth U x_T over
    ``ref_x``, and of the linear count (sum w_truth r over each reporting cell's fine cells) over ``ref_count``; each
    reference is band_reference of the single-universe values. The second is exact under the law; the first carries
    x_T's linearisation. H, cv and U are on the packed fine cells of const["pack"]."""
    comp = composite_sums(S, H, cv)
    X = xt_packed(comp["A"], comp["B"], comp["D"], draw_flux(S, flux_cols, flux_u), const["n_nucleons"],
                  const["data_pot"], const["pack"]) @ U.T
    L = comp["A"] @ (U > 0).astype(np.float64).T
    return np.var(X, axis=0, ddof=1) / ref_x, np.var(L, axis=0, ddof=1) / ref_count


def rates(R: dict, deflation: float = DEFLATION) -> dict:
    """The director's outputs from replicate ratios R[truth] (sets x 16): (a) null SDs, (b) #724's rates at its fixed
    numbers, (c) the rates at the SE multiples with (alpha) per cell and (beta), (gamma) beside it, and the power of
    (ii) against a uniform deflation; each per truth and over the truths, the union both per replicate and as
    1 - prod(1 - p)."""
    out, stop_b, stop_c = {}, {}, {}
    for t, r in R.items():
        r = np.asarray(r, np.float64)
        n = r.shape[0]
        dev = np.abs(r - 1.0)
        ml = np.mean(np.log(r), axis=1)
        mx = dev.max(axis=1)
        sd_ml, sd_mx, sd_c = float(np.std(ml, ddof=1)), float(np.std(mx, ddof=1)), np.std(r, axis=0, ddof=1)
        g = [gate_724(row) for row in r]           # the bulk's own rule, so the rate is the gate's (audit W2)
        b = {k: np.array([not x[k] for x in g]) for k in ("i", "ii", "iii")}
        b["union"] = np.array([not x["passes"] for x in g])
        thr_ii = SD_MULT_LOGMEAN * sd_ml
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(sd_c > 0, dev / sd_c, np.where(dev > 0, np.inf, 0.0))
        c = {"i": b["i"], "ii": np.abs(ml) > thr_ii, "iii_alpha": np.max(z, axis=1) > SD_MULT_CELL}
        c["union"] = c["i"] | c["ii"] | c["iii_alpha"]
        desc = {"iii_beta": mx > SD_MULT_CELL * float(np.sqrt(np.mean(sd_c ** 2))),
                "iii_gamma": mx > SD_MULT_CELL * sd_mx}
        ml_def = ml + math.log(deflation)
        se = lambda p: float(math.sqrt(p * (1 - p) / n))  # noqa: E731
        out[t] = {"sets": n,
                  "a": {"sd_mean_log": sd_ml, "sd_max_dev": sd_mx, "sd_per_cell": sd_c.tolist()},
                  "b": {k: {"rate": float(v.mean()), "se": se(float(v.mean()))} for k, v in b.items()},
                  "c": {"ii_threshold": thr_ii, **{k: {"rate": float(v.mean()), "se": se(float(v.mean()))}
                                                     for k, v in c.items()}},
                  "c_descriptive": {k: float(v.mean()) for k, v in desc.items()},
                  "power_ii": {"deflation": deflation, "at_fixed": float(np.mean(np.abs(ml_def) > GATE_LOGMEAN)),
                               "at_sd_multiple": float(np.mean(np.abs(ml_def) > thr_ii))}}
        stop_b[t], stop_c[t] = b["union"], c["union"]
    for key, stops in (("b", stop_b), ("c", stop_c)):
        n = min(v.size for v in stops.values())
        per_rep = float(np.mean(np.any([v[:n] for v in stops.values()], axis=0)))
        prod = 1.0 - float(np.prod([1.0 - v.mean() for v in stops.values()]))
        out[f"over_truths_{key}"] = {"union_per_replicate": per_rep, "union_product": prod,
                                     "se": float(math.sqrt(per_rep * (1 - per_rep) / n))}
    out["to_joseph"] = out["over_truths_b"]["union_per_replicate"] > UNION_LIMIT
    return out


def null_stats(R: np.ndarray) -> dict:
    """Per replicate set (rows of R, sets x 16): (i)'s verdict at #724's fixed numbers (gate_724), the mean log ratio
    and the per-cell |r - 1|; with the null SDs over sets of the mean log and of each cell's ratio."""
    R = np.asarray(R, np.float64)
    g = [gate_724(r) for r in R]
    return {"i": np.array([not x["i"] for x in g]), "ml": np.array([x["mean_log"] for x in g]),
            "dev": np.abs(R - 1.0), "sd_ml": float(np.std([x["mean_log"] for x in g], ddof=1)),
            "sd_c": np.std(R, axis=0, ddof=1)}


def stops_at(st: dict, s: float, sd_ml: float, sd_c: np.ndarray) -> np.ndarray:
    """The large-sample gate's STOP per replicate at multiple s (P2): (i) fixed; (ii) |mean log| > s 3.5 SD_ii;
    (iii) by (alpha), max_c |r_c - 1| / SD_c > s 4.3; SD_ii and SD_c from the null at N."""
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(sd_c > 0, st["dev"] / sd_c, np.where(st["dev"] > 0, np.inf, 0.0))
    return st["i"] | (np.abs(st["ml"]) > s * SD_MULT_LOGMEAN * sd_ml) | (np.max(z, axis=1) > s * SD_MULT_CELL)


def threshold_rule(R: dict) -> dict:
    """P2: the smallest s on S_GRID whose joint (i)-(iii) noise-only STOP over three truths is at most UNION_LIMIT.
    With the plug-in absent, its per-truth rate is projected as the mean of the others', independent (labelled);
    with all three present, the union is measured per replicate. Records the whole grid, the s chosen (None if none
    reaches the limit), the per-truth thresholds, and whether (i) alone already exceeds the budget."""
    st = {t: null_stats(r) for t, r in R.items()}
    sd = {t: (st[t]["sd_ml"], st[t]["sd_c"]) for t in R}
    three = set(R) == {"g18", "ar23", "plugin"}

    def union(stops):
        if three:
            n = min(v.size for v in stops.values())
            return float(np.mean(np.any([v[:n] for v in stops.values()], axis=0)))
        p = [float(v.mean()) for v in stops.values()]
        return 1.0 - float(np.prod([1 - x for x in p])) * (1.0 - float(np.mean(p)))
    grid, chosen = [], None
    for s in S_GRID:
        stops = {t: stops_at(st[t], s, *sd[t]) for t in R}
        u = union(stops)
        grid.append({"s": s, "union": u, "per_truth": {t: float(v.mean()) for t, v in stops.items()}})
        if chosen is None and u <= UNION_LIMIT:
            chosen = s
    i_alone = union({t: st[t]["i"] for t in R})
    return {"three_truths_measured": three, "projection": None if three else
            "the plug-in's per-truth rate as the mean of the others', independent", "grid": grid, "s": chosen,
            "thresholds": {t: {"ii_mean_log": None if chosen is None else chosen * SD_MULT_LOGMEAN * sd[t][0],
                               "iii_alpha_multiple": None if chosen is None else chosen * SD_MULT_CELL,
                               "sd_mean_log": sd[t][0], "sd_per_cell": sd[t][1].tolist()} for t in R},
            "i_alone_union": i_alone, "i_alone_exceeds": bool(i_alone > UNION_LIMIT)}


def power_at(R: dict, rule: dict) -> dict:
    """P4 at the rule's s: the gate's STOP rate per truth against a uniform UNIFORM_DEFLATION (required >= POWER_MIN)
    and against deflations concentrated in k cells (reported): every cell for k = 1, PLACEMENTS seeded sets for k > 1;
    min and mean over placements. The null SDs stay the undeflated null's."""
    s = rule["s"]
    out = {}
    for t, r in R.items():
        r = np.asarray(r, np.float64)
        sd_ml, sd_c = rule["thresholds"][t]["sd_mean_log"], np.asarray(rule["thresholds"][t]["sd_per_cell"])
        rate = lambda X: float(stops_at(null_stats(X), s, sd_ml, sd_c).mean())  # noqa: E731
        conc = {}
        for k, d in CONCENTRATED:
            if k == 1:
                sets = [[c] for c in range(N_CELLS)]
            else:
                rng = np.random.default_rng([CAL_SALT, k])
                sets = [sorted(rng.choice(N_CELLS, k, replace=False).tolist()) for _ in range(PLACEMENTS)]
            vals = []
            for cells in sets:
                X = r.copy()
                X[:, cells] *= (1.0 - d)
                vals.append(rate(X))
            conc[f"{k}_cells_{int(round(d * 100))}pct"] = {"min": min(vals), "mean": float(np.mean(vals)),
                                                            "placements": sets}
        uni = rate(r * (1.0 - UNIFORM_DEFLATION))
        out[t] = {"uniform": uni, "uniform_meets": bool(uni >= POWER_MIN), "concentrated": conc}
    out["meets"] = all(v["uniform_meets"] for k, v in out.items() if k != "meets")
    return out


def calibration_verdict_n(law: dict, lin: dict, rule: dict, power: dict | None) -> str:
    """The large-sample calibration's verdict, in order: the law control (CONTROL_FAILED), the linearisation, (i)
    alone over the budget, no s reaching the budget, the power short of POWER_MIN (each to the director: raising N is
    priced there), else CALIBRATED."""
    if not law["holds"]:
        return "CONTROL_FAILED"
    if not lin["holds"]:
        return "LINEARISATION_TO_DIRECTOR"
    if rule["i_alone_exceeds"]:
        return "I_ALONE_TO_DIRECTOR"
    if rule["s"] is None:
        return "NO_THRESHOLD_TO_DIRECTOR"
    if not power["meets"]:
        return "POWER_SHORT_TO_DIRECTOR"
    return "CALIBRATED"


def calibration_verdict(law: dict, lin: dict, out: dict) -> str:
    """The calibration's verdict, in order: the law control (a bug: CONTROL_FAILED), the linearisation (a finding for
    the director), the three-truth union under (b) (to Joseph), else CALIBRATED."""
    return ("CONTROL_FAILED" if not law["holds"] else "LINEARISATION_TO_DIRECTOR" if not lin["holds"] else
            "TO_JOSEPH" if out["to_joseph"] else "CALIBRATED")


def control(R: dict) -> dict:
    """D4's law control, on the linear count, per truth and cell: |mean ratio - 1| <= CONTROL_Z standard errors (the
    replicates' SD / sqrt(sets)). The law is exact there, so any failure is a bug in band_reference or the draw law,
    and stops everything (the director's ruling)."""
    out = {}
    for t, r in R.items():
        r = np.asarray(r, np.float64)
        z = (r.mean(axis=0) - 1.0) / (r.std(axis=0, ddof=1) / math.sqrt(r.shape[0]))
        out[t] = {"z": z.tolist(), "holds": bool(np.all(np.abs(z) <= CONTROL_Z))}
    out["holds"] = all(v["holds"] for v in out.values())
    return out


def linearisation(R: dict) -> dict:
    """x_T's linearisation, by effect size (the director's W1): per truth and cell, mean ratio - 1, which must lie
    within LINEARISATION_TOL in every cell; beyond it, a finding about band_reference that goes to the director. The
    rates already carry the bias, so it cannot miscalibrate the gate; the values are reported either way."""
    out = {}
    for t, r in R.items():
        m = np.asarray(r, np.float64).mean(axis=0) - 1.0
        out[t] = {"mean_ratio_minus_1": m.tolist(), "max_abs": float(np.max(np.abs(m))),
                  "holds": bool(np.all(np.abs(m) <= LINEARISATION_TOL))}
    out["holds"] = all(v["holds"] for v in out.values())
    return out


# ------------------------------------------------------------------------------------------------ c2check

DRAW_BLOCK = 20


def _bins(cells: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    ok = cells >= 0
    return np.bincount(cells[ok], weights=w[ok], minlength=n)


def multiplicative_terms(V: np.ndarray, cv: np.ndarray) -> dict:
    """The draw-independent part of C2's (v) multiplicative composition, built once per array (the director's ruling
    (a): rebuilding it for every 20-draw block cost about 24 h per truth at the real 49 M rows): the CV's log, the
    per-universe log ratios L (0 where either weight is <= 0), and Z sparsely, as the (universe, row) pairs with a
    universe weight <= 0 where the CV's is > 0."""
    pos = cv > 0
    lcv = np.log(np.where(pos, cv, 1.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        L = np.where(pos[None] & (V > 0), np.log(np.where(V > 0, V, 1.0)) - lcv[None], 0.0)
    zu, zrow = np.nonzero(pos[None] & (V <= 0))
    return {"pos": pos, "lcv": lcv, "L": L, "zu": zu, "zrow": zrow}


def multiplicative_apply(T: dict, S: np.ndarray) -> np.ndarray:
    """C2's (v) for draws S (draws x universes, entries >= 0) from multiplicative_terms: a_CV prod_j (a_uj / a_CV),
    0 where a_CV <= 0 or a drawn universe's weight is <= 0 (clip_probe2's floor). A row is floored for a draw exactly
    when S's weight on a (universe, row) pair of Z is > 0, which is (S @ Z) != 0 for S >= 0."""
    floored = np.zeros((S.shape[0], T["pos"].size), bool)
    if T["zu"].size:
        d, k = np.nonzero(S[:, T["zu"]] > 0)
        floored[d, T["zrow"][k]] = True
    return np.where(T["pos"][None] & ~floored, np.exp(T["lcv"][None] + S @ T["L"]), 0.0)


def multiplicative(V: np.ndarray, cv: np.ndarray, S: np.ndarray) -> np.ndarray:
    """C2's (v) multiplicative composition per row, for draws S (draws x universes): a_CV prod_j (a_uj / a_CV), 0
    where a_CV <= 0 or a drawn universe's weight is <= 0 (clip_probe2's floor)."""
    return multiplicative_apply(multiplicative_terms(V, cv), S)


def c2_truth(V: dict, cv: dict, S: np.ndarray, r: np.ndarray, geo: dict, phi: np.ndarray, const: dict,
             block: int = DRAW_BLOCK) -> dict:
    """C2's per-draw quantities on 1B's 16 cells for one truth over its declared draws S (draws x universes), first
    order, under D1(b): the truth is 1B's own graded x_T (U xt_packed on the fine sums the bulk's true_xsec forms).
    V and cv: per-universe and CV rows of "wt", "wr", "bkgw" and the denominator's "tdw" rows, and "D" per fine cell.
    geo: each row's fine cell (gen for truth-passing signal rows, reco for reco-passing ones, background reco, the
    denominator rows'), fm (fine -> reporting cell) and U, packed. Returns per draw (cells x draws):
    S, m_seen (reco-kept signal rows by truth cell, counts); S_reco, m_bkg (by reco cell); N = U x_T unclipped,
    Nc = U x_T with C2's option (1) (truth and denominator rows clipped on their own sign), m_all = Nc - N (signed:
    clipping moves both sums of a ratio); Nm, the multiplicative composition's U x_T (descriptive)."""
    pack, U = const["pack"], geo["U"]
    nf = int(np.prod(geo["shape"]))
    keep = pack["keep"]
    fm = geo["fm"]
    cells16 = lambda fine: np.where(fine >= 0, fm[np.maximum(fine, 0)], -1)  # noqa: E731
    t16, r16, b16 = cells16(geo["gen"]), cells16(geo["reco"]), cells16(geo["bkg"])
    seen = np.where(geo["reco"] >= 0, t16, -1)
    k_all = S.sum(axis=1) - 1.0
    if np.any(S < 0):
        raise Refusal("a selection matrix has a negative entry")
    terms = {q: multiplicative_terms(V[q], cv[q]) for q in ("wt", "tdw")}     # once, not per block
    out = {q: np.zeros((N_CELLS, S.shape[0])) for q in ("S", "m_seen", "S_reco", "m_bkg", "N", "Nc", "Nm")}
    for d0 in range(0, S.shape[0], block):
        Sb, kb = S[d0:d0 + block], k_all[d0:d0 + block, None]
        comp = {q: Sb @ V[q] - kb * cv[q][None] for q in ("wt", "wr", "bkgw", "tdw", "D")}
        mult = {q: multiplicative_apply(terms[q], Sb) for q in ("wt", "tdw")}
        for i in range(Sb.shape[0]):
            d = d0 + i
            lam = comp["wr"][i] * r
            out["S"][:, d] = _bins(seen, lam, N_CELLS)
            out["m_seen"][:, d] = _bins(seen, np.maximum(-lam, 0.0), N_CELLS)
            out["S_reco"][:, d] = _bins(r16, lam, N_CELLS)
            out["m_bkg"][:, d] = _bins(b16, np.maximum(-comp["bkgw"][i], 0.0), N_CELLS)
            wt, dr = comp["wt"][i], comp["tdw"][i]
            wtp = np.where(wt * r < 0, 0.0, wt)
            m_den = _bins(np.where(dr < 0, geo["td"], -1), -dr, nf)
            Dc = comp["D"][i]
            Dp = np.where(m_den > 0, Dc + m_den, Dc)
            Dm = _bins(geo["td"], mult["tdw"][i], nf) + (Dc - _bins(geo["td"], dr, nf))
            sums = [(_bins(geo["gen"], wt * r, nf), _bins(geo["gen"], wt, nf), Dc),
                    (_bins(geo["gen"], wtp * r, nf), _bins(geo["gen"], wtp, nf), Dp),
                    (_bins(geo["gen"], mult["wt"][i] * r, nf), _bins(geo["gen"], mult["wt"][i], nf), Dm)]
            for q, (A, B, Dq) in zip(("N", "Nc", "Nm"), sums):
                out[q][:, d] = xt_packed(A[keep][None], B[keep][None], Dq[keep][None], phi[d][None],
                                         const["n_nucleons"], const["data_pot"], pack)[0] @ U.T
    out["m_all"] = out["Nc"] - out["N"]
    return out


def c2_block(q: dict, ref_x: np.ndarray, rel: np.ndarray) -> dict:
    """One truth's entry of C2's record (clip_probe2's rec["b"][tune] shape) from c2_truth's quantities: the offsets
    in units of 1B's relative sigma_c (S1's C_total_plus_C_resp, a proxy for C_T, under clip_probe2's key "sigma_Q"),
    the variance ratios over band_reference of the single-universe U x_T, and the clipped truth's mean shift."""
    with np.errstate(invalid="ignore", divide="ignore"):
        o_a = q["m_seen"] / q["S"]
        o_1 = o_a - q["m_all"] / q["N"]
        o_b = q["m_bkg"] / q["S_reco"]
        vr = {"first_order": np.var(q["N"], axis=1, ddof=1) / ref_x,
              CLIPPED: np.var(q["Nc"], axis=1, ddof=1) / ref_x,
              "multiplicative": np.var(q["Nm"], axis=1, ddof=1) / ref_x}
        shift = np.mean(q["m_all"] / q["N"], axis=1) / rel
    return {"option_a": {"sigma_Q": cp2.stats(o_a, rel)}, "option_1": {"sigma_Q": cp2.stats(o_1, rel)},
            "background_both_options": {"sigma_Q": cp2.stats(o_b, rel)},
            "variance_ratio": {k: v.tolist() for k, v in vr.items()},
            "gate_724": gate_724(vr[CLIPPED]),
            "weakened_cells": cov2d.weakened_cells(vr[CLIPPED], np.arange(N_CELLS)),
            "clipped_truth_mean_shift_sigma_c": {"per_cell": shift.tolist(), **cp2.q3(np.abs(shift))},
            "m_all_note": "signed: U (x_T clipped - x_T unclipped); clipping moves both sums of x_T's ratio"}


def row_match(gen: np.ndarray, wt: np.ndarray, in_ps: np.ndarray, td: np.ndarray, tdw: np.ndarray,
              cell_s: np.ndarray, cell_d: np.ndarray) -> dict:
    """C2's (vi) on 1B's trees: signal rows with truth in the phase space against the denominator rows, keyed by
    clip_probe2.row_hash of the five coordinates and the CV weight; each tree's unmatched w_truth share per cell."""
    hs = cp2.row_hash([np.asarray(gen[in_ps, k], np.float64) for k in range(5)] + [np.asarray(wt[in_ps], np.float64)])
    hd = cp2.row_hash([np.asarray(td[:, k], np.float64) for k in range(5)] + [np.asarray(tdw, np.float64)])
    um_s, um_d = cp2.unmatched(hs, hd), cp2.unmatched(hd, hs)
    cs, cdd = cell_s[in_ps], cell_d
    share = lambda c, w, um: np.array([w[(c == k) & um].sum() / w[c == k].sum() if w[c == k].sum() > 0 else np.nan  # noqa: E731
                                       for k in range(N_CELLS)])
    sh_s, sh_d = share(cs, np.nan_to_num(wt[in_ps]), um_s), share(cdd, np.nan_to_num(tdw), um_d)
    worst = float(np.nanmax(np.abs(np.concatenate([sh_s, sh_d]))))
    return {"signal_rows_in_phase_space": int(in_ps.sum()), "signal_rows_unmatched": int(um_s.sum()),
            "truth_rows": int(td.shape[0]), "truth_rows_unmatched": int(um_d.sum()),
            "signal_unmatched_share_per_cell": sh_s.tolist(), "truth_unmatched_share_per_cell": sh_d.tolist(),
            "largest_cell_unmatched_share": worst if np.isfinite(worst) else None}


# ------------------------------------------------------------------------------------------ the calibration job

SCHEMA_CAL = "fd-1b-c2-calibration/2"            # /2: at GATE_N draws per set, with the s rule and power (P2, P4)
_STATE: dict = {}


def fine_sums(world: dict, a, r: dict, tags: list[str], cells: np.ndarray,
              rows: dict | None = None) -> tuple[dict, dict, np.ndarray, list]:
    """Per universe (rows in ``tags``' order) the fine sums 1B's x_T is made of, each universe's weights read once
    (fd_1b_mc.verified_weights) and composed as fd_1b_mc._single gives them: A[truth] = sum w_truth r, B = sum w_truth
    over truth-passing rows at their fine cells, and D its denominator per fine cell. Returns (H, cv, Flux universes'
    Phi_u rows, the detector universes whose denominator is not the CV's bitwise). With ``rows`` (a dict), the same
    read also fills each universe's row arrays there ("wt", "wr", "bkgw" and the denominator's "tdw": a detector
    universe's is the CV's per-row weight, world["tdw_cv"]), for c2check."""
    import fd_1b_mc as mc
    inputs, bkg = world["inputs"], world["bkg"]
    n = int(np.prod(tuple(np.asarray(e).size - 1 for e in inputs["edges"])))
    ok = cells >= 0
    hist = lambda w: np.bincount(cells[ok], weights=w[ok], minlength=n)  # noqa: E731
    wt_cv = np.asarray(inputs["w_truth"], float)
    cv = {"B": hist(wt_cv), "D": np.asarray(inputs["denom_nd"], float).ravel(order="C"),
          **{f"A_{t}": hist(wt_cv * rt) for t, rt in r.items()}}
    H = {k: np.empty((len(tags), n)) for k in cv}
    if rows is not None:
        n_td = np.asarray(world["bank_cv"]["td_pt"]).size
        rows.update({"wt": np.empty((len(tags), wt_cv.size)), "wr": np.empty((len(tags), wt_cv.size)),
                     "bkgw": np.empty((len(tags), np.asarray(bkg["bkg_w"]).size)), "tdw": np.empty((len(tags), n_td))})
    phi, det_differs = [], []
    for i, tag in enumerate(tags):
        _, zero = mc.verified_weights(world, a, tag)
        single, p = mc._single(inputs, bkg, world["bank_cv"], tag, zero, world["flux"])
        if rows is not None:
            for k in ("wt", "wr", "bkgw"):
                rows[k][i] = single[k]
            rows["tdw"][i] = zero["tdw"] if "tdw" in zero else world["tdw_cv"]
        H["B"][i], H["D"][i] = hist(single["wt"]), single["denom"].ravel(order="C")
        for t, rt in r.items():
            H[f"A_{t}"][i] = hist(single["wt"] * rt)
        if p is not None:
            phi.append(np.asarray(p, float))
        if tag.rpartition("_")[0] in sa.DETECTOR_BANDS and not np.array_equal(single["denom"], inputs["denom_nd"]):
            det_differs.append(tag)
        del single, zero
    return H, cv, np.array(phi), det_differs


def _worker_init(state: dict) -> None:
    _STATE.update(state)


def _one_set(job: tuple[str, int]) -> tuple[str, int, np.ndarray, np.ndarray]:
    t, s = job
    st = _STATE
    S = selection(calibration_draws(t, s, st["flux_p"], st["groups"], n=st["n"]), st["col"], st["bands"])
    H = {"A": st["H"][f"A_{t}"], "B": st["H"]["B"], "D": st["H"]["D"]}
    cv = {"A": st["cv"][f"A_{t}"], "B": st["cv"]["B"], "D": st["cv"]["D"]}
    rx, rl = set_ratios(S, H, cv, st["U"], st["ref_x"][t], st["ref_count"][t], st["flux_cols"], st["phi"],
                        st["const"])
    return t, s, rx, rl


def prepare(a, rows: bool = False) -> dict:
    """What the calibration and c2check share, so neither can drift from the other: the world (fd_1b_mc._load_world),
    each truth's r (and D8's rows with r < 0), one read of every universe (fine_sums), the kept fine cells (in a
    reporting cell, and non-zero somewhere), the packing, and each truth's single-universe U x_T with its
    band_reference (the variance ratio's denominator) and the linear count's."""
    import fd_1b_inv as inv
    import fd_1b_mc as mc
    inv.OPENED.clear()
    world = mc._load_world(a)
    inputs = world["inputs"]
    flux_p = mc.via_noatime(toys.flux_probabilities, a.flux_constraint)
    U_full = sa.functional_matrix(sa.fine_map(a.definition))
    truths = list(a.truths)
    push = None
    if "plugin" in truths:
        if inv.sha256_noatime(a.push) != a.expect_push_sha256:
            raise Refusal("the plug-in truth needs --push with its declared digest")
        push = np.asarray(inv.load_npz(a.push)["push"], float)
    r, r_neg = {}, {}
    for t in truths:
        ratio, _ = mc.truth_ratio(t, a.prep)
        r[t] = mc.truth_weight(t, inputs, ratio, push)
        neg = np.flatnonzero(np.asarray(inputs["pass_truth"], bool) & (r[t] < 0))
        r_neg[t] = {"rows": int(neg.size), "first_rows": neg[:20].tolist()}
    order, bands, tags = layout_1b()
    col = {u: i for i, u in enumerate(tags)}
    cells = mc.flat_cells(np.asarray(inputs["MCgen"], float), inputs["edges"])
    cells = np.where(np.asarray(inputs["pass_truth"], bool), cells, -1)
    R = {} if rows else None
    if world.get("tdw_cv") is None:
        raise Refusal("the calibration and c2check need --cv-tdw (fd_1b_cvdenom's PASS output) for (e2)'s d_CV")
    H, cv, phi, det_differs = fine_sums(world, a, r, tags, cells, R)
    if det_differs:
        raise Refusal(f"detector denominators differ from the CV's: {det_differs} (S3 (d1)'s check D)")
    d_cv = cv_denominator_f32(world).ravel()          # (e2) item 1: no composite mixes binnings
    cv["D"] = d_cv
    for i, tag in enumerate(tags):
        if tag.rpartition("_")[0] in sa.DETECTOR_BANDS:
            H["D"][i] = d_cv                           # a detector universe's denominator is the CV's (check D)
    D_full, D_cv_full = (H["D"].copy(), cv["D"].copy()) if rows else (None, None)
    support = U_full.sum(axis=0) > 0
    live = np.abs(cv["D"]) + np.abs(H["D"]).sum(axis=0) + np.abs(cv["B"]) + np.abs(H["B"]).sum(axis=0) > 0
    keep = np.flatnonzero(support & live)
    shape = tuple(np.asarray(e).size - 1 for e in inputs["edges"])
    pack = packing(keep, shape, inputs["edges"])
    H = {k: v[:, keep] for k, v in H.items()}
    cv = {k: v[keep] for k, v in cv.items()}
    U = U_full[:, keep]
    const = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]), "pack": pack}
    flux_cols = np.array([col[f"{sa.FLUX}_{i}"] for i in range(bands[sa.FLUX])])
    phi_single = np.repeat(np.asarray(inputs["flux"], float)[None], len(tags), axis=0)
    phi_single[flux_cols] = phi
    w_flux = flux_p * 1.0
    ref_x, ref_count, single_x = {}, {}, {}
    for t in truths:
        X = xt_packed(H[f"A_{t}"], H["B"], H["D"], phi_single, const["n_nucleons"], const["data_pot"], pack) @ U.T
        single_x[t] = X
        ref_x[t] = band_reference(X, w_flux, order, bands, sa.FLUX)
        ref_count[t] = band_reference(H[f"A_{t}"] @ (U > 0).astype(np.float64).T, w_flux, order, bands, sa.FLUX)
        if not (np.all(ref_x[t] > 0) and np.all(ref_count[t] > 0)):
            raise Refusal(f"{t}: a reporting cell has no band variance")
    return {"world": world, "flux_p": flux_p, "U_full": U_full, "truths": truths, "push": push, "r": r,
            "r_neg": r_neg, "order": order, "bands": bands, "tags": tags, "col": col, "cells": cells, "H": H, "cv": cv,
            "phi": phi, "det_differs": det_differs, "keep": keep, "shape": shape, "pack": pack, "U": U, "const": const,
            "flux_cols": flux_cols, "phi_single": phi_single, "ref_x": ref_x, "ref_count": ref_count,
            "single_x": single_x, "rows": R, "D_full": D_full, "D_cv_full": D_cv_full}


def calibrate_main(a) -> dict:
    """The calibration job (FD-1B-STAGED-ADDENDUM-A2-1.md): one read of every universe, the references, a measured
    single-set time on the real fine-cell count (refusing when the projection passes ``--budget-seconds``), then
    CAL_SETS replicate sets per truth across worker processes, and the director's outputs and the D4 controls."""
    import hashlib
    import multiprocessing
    import time

    import fd_1b_inv as inv
    import fd_1b_mc as mc
    t0 = time.time()
    P = prepare(a)
    H, cv, U, ref_x, ref_count, flux_cols, phi, const, flux_p, col, bands, keep, truths, world = (
        P[k] for k in ("H", "cv", "U", "ref_x", "ref_count", "flux_cols", "phi", "const", "flux_p", "col", "bands",
                       "keep", "truths", "world"))
    r_neg, det_differs, single_x = P["r_neg"], P["det_differs"], P["single_x"]
    groups = world["groups"]
    state = {"H": H, "cv": cv, "U": U, "ref_x": ref_x, "ref_count": ref_count, "flux_cols": flux_cols,
             "phi": phi, "const": const, "flux_p": flux_p, "groups": groups, "col": col, "bands": bands,
             "n": getattr(a, "draws", GATE_N)}
    _worker_init(state)
    t1 = time.time()
    first = _one_set((truths[0], 0))
    per_set = time.time() - t1
    total = len(truths) * a.sets
    projected = (time.time() - t0) + 1.15 * total * per_set / a.workers
    timing = {"fine_cells_kept": int(keep.size), "set_seconds_measured": per_set, "workers": a.workers,
              "projected_seconds": projected, "budget_seconds": a.budget_seconds}
    print(json.dumps({"calibration": "timing", **timing}), flush=True)
    if projected > a.budget_seconds:
        raise Refusal(f"projected {projected:.0f} s passes the budget {a.budget_seconds} s (INVALID, rerunnable)")
    jobs = [(t, s) for t in truths for s in range(a.sets) if (t, s) != (truths[0], 0)]
    Rx = {t: np.empty((a.sets, N_CELLS)) for t in truths}
    Rl = {t: np.empty((a.sets, N_CELLS)) for t in truths}
    Rx[first[0]][0], Rl[first[0]][0] = first[2], first[3]
    with multiprocessing.get_context("fork").Pool(a.workers) as pool:
        for t, s, rx, rl in pool.imap_unordered(_one_set, jobs, chunksize=8):
            Rx[t][s], Rl[t][s] = rx, rl
    law, lin = control(Rl), linearisation(Rx)                # P5: at N, before any threshold is read
    out = rates(Rx)                                           # #724's fixed numbers and (c), descriptive at N
    rule = threshold_rule(Rx)
    power = power_at(Rx, rule) if rule["s"] is not None else None
    digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        Path(__file__).resolve(), Path(mc.__file__).resolve(), Path(cp2.__file__).resolve(),
        Path(cov2d.__file__).resolve(), Path(toys.__file__).resolve())}
    verdict = calibration_verdict_n(law, lin, rule, power)
    rec = {"schema": SCHEMA_CAL, "step": "c2-calibration", "verdict": verdict, "truths": truths, "sets": a.sets,
           "draws_per_set": state["n"], "rule": rule, "power": power,
           "seeds": {t: CAL_SEED[t] for t in truths}, "salt": CAL_SALT, "constants": {
               "k": GATE_K, "dev": GATE_DEV, "mean_log": GATE_LOGMEAN, "max_dev": GATE_MAX,
               "sd_mult_mean_log": SD_MULT_LOGMEAN, "sd_mult_cell": SD_MULT_CELL, "union_limit": UNION_LIMIT,
               "deflation": DEFLATION, "control_z": CONTROL_Z, "linearisation_tol": LINEARISATION_TOL,
               "gate_n": GATE_N, "s_grid": [S_GRID[0], S_GRID[-1], 0.01], "power_min": POWER_MIN,
               "uniform_deflation": UNIFORM_DEFLATION, "concentrated": CONCENTRATED, "placements": PLACEMENTS},
           "outputs": out, "control_law": law, "control_linearisation": lin,
           "ratio_mean_per_cell": {t: Rx[t].mean(axis=0).tolist() for t in truths},
           "checks": {"r_negative": r_neg, "detector_denominator_differs_from_cv": det_differs},
           "timing": dict(timing, seconds=time.time() - t0), "code_sha256": digests,
           "inputs": {"npz_sha256": world["npz_sha"], "bkg_sha256": world["bkg_sha"],
                      "pins_sha256": a.expect_pins_sha256, "flux_table_sha256": a.expect_flux_table_sha256,
                      "push_sha256": a.expect_push_sha256, "cv_tdw_sha256": a.expect_cv_tdw_sha256},
           "atime": inv.atime_check()}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out.with_suffix(".npz"), **{f"ratio_{t}": Rx[t] for t in truths},
                        **{f"count_ratio_{t}": Rl[t] for t in truths}, **{f"single_x_{t}": single_x[t] for t in truths})
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


SCHEMA_GATE = "fd-1b-c2-gate/1"


def gate_code_digests() -> dict:
    """The code a gate record binds: sha256 of fd_1b_c2, fd_1b_mc, clip_probe2, cov2d and fd_1b_toys as loaded. One
    function for c2check (which writes them) and fd_1b_mc.check_clip_gate (which requires the bulk's to equal them)."""
    import hashlib

    import fd_1b_mc as mc
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        Path(__file__).resolve(), Path(mc.__file__).resolve(), Path(cp2.__file__).resolve(),
        Path(cov2d.__file__).resolve(), Path(toys.__file__).resolve())}


def cv_denominator_f32(world: dict) -> np.ndarray:
    """The director's (e2) item 1: d_CV := hist_f32(tdw_CV), the CV's per-row weight binned on cv.npz's float32 td_*,
    as every bank universe's denominator is binned (s5p_universe.denominator), so a composite never mixes binnings."""
    import s5p_universe
    return np.asarray(s5p_universe.denominator(world["bank_cv"], world["tdw_cv"], world["inputs"]["edges"]), float)


def gate_n(ratio, thr: dict) -> dict:
    """The large-sample gate on one truth's 16 clipped ratios at N (P2): (i) at #724's fixed numbers (gate_724), (ii)
    |mean log| <= thr's ii_mean_log, (iii) by (alpha) max_c |r_c - 1| / SD_c <= thr's iii_alpha_multiple."""
    g = gate_724(ratio)
    r = np.asarray(ratio, np.float64)
    sd_c = np.asarray(thr["sd_per_cell"], np.float64)
    z = float(np.max(np.abs(r - 1.0) / sd_c))
    out = {"i": g["i"], "cells_beyond": g["cells_beyond"], "mean_log": g["mean_log"], "max_z": z,
           "ii": abs(g["mean_log"]) <= thr["ii_mean_log"], "iii": z <= thr["iii_alpha_multiple"]}
    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])
    return out


def backstop(ratio300, sd_c300) -> dict:
    """P6 on the 300 declared draws: (i) at k = 2 (gate_724) and (iii) by (alpha) at BACKSTOP_SD_MULT x SD_c, with
    SD_c the 300-draw calibration's. A failure is a hard STOP."""
    g = gate_724(ratio300)
    z = float(np.max(np.abs(np.asarray(ratio300, np.float64) - 1.0) / np.asarray(sd_c300, np.float64)))
    return {"i": g["i"], "cells_beyond": g["cells_beyond"], "max_z": z, "iii": z <= BACKSTOP_SD_MULT,
            "passes": bool(g["i"] and z <= BACKSTOP_SD_MULT)}


def config_hash(code: dict, inputs: dict, clip_rule: str) -> str:
    """P6's config hash, shared by the gate sample and the coverage draws: the code (gate_code_digests), the inputs'
    digests, the clip rule, the draw salt and the declared toys' seeds, as canonical JSON."""
    import hashlib
    import fd_1b_mc as mc
    doc = {"code": code, "inputs": inputs, "clip_rule": clip_rule, "draw_salt": toys.DRAW_SALT,
           "toy_seeds": {t: [int(x) for x in mc.TOY_SEEDS[t]] for t in mc.TOY_SEEDS}}
    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()


THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
               "NUMEXPR_NUM_THREADS")                       # recorded: BLAS's thread count can move the last bits
MERGE_SAME = ("schema", "step", "code_sha256", "inputs", "calibration_sha256", "calibration_npz_sha256", "calibration",
              "calibration_300_sha256", "config_hash", "sigma", "c2_reading_sha256", "threads")
MERGE_PER_TRUTH = ("reads", "declared_seeds", "backstop", "reading_detail", "r_negative")


def c2check_merge(parts: list[dict]) -> dict:
    """The one gate record binding 3 pins, from c2check's per-truth records (one truth per job, the director's ruling
    (a)): every shared field identical across the parts (MERGE_SAME, C2's (vi) row match and the gate sample's size),
    no truth in two parts; the per-truth fields joined in fd_1b_mc.TRUTHS order; the verdict and reading as
    c2check_main forms them, from every truth's reading and backstop. seconds is the parts' sum, atime the union of
    what moved with each part's record kept, and merged_from each part's truths and seconds."""
    import fd_1b_mc as mc
    if len(parts) < 2:
        raise Refusal("a merge needs at least two per-truth records")
    first = parts[0]
    for k in MERGE_SAME:
        if any(p.get(k) != first.get(k) for p in parts):
            raise Refusal(f"the per-truth records differ in {k}")
    if any(p["record"]["vi"] != first["record"]["vi"] for p in parts):
        raise Refusal("the per-truth records differ in C2's (vi) row match")
    if any(p["gate_sample"]["n"] != first["gate_sample"]["n"] or not p["gate_sample"]["first_300_bitwise"] for p in parts):
        raise Refusal("the per-truth records differ in the gate sample")
    named = [t for p in parts for t in p["truths"]]
    if len(named) != len(set(named)):
        raise Refusal("a truth is in two per-truth records")
    truths = [t for t in mc.TRUTHS if t in named]
    by = {t: p for p in parts for t in p["truths"]}
    g = {k: first[k] for k in MERGE_SAME}
    g.update({k: {t: by[t][k][t] for t in truths} for k in MERGE_PER_TRUTH})
    g["truths"] = truths
    g["record"] = {"vi": first["record"]["vi"], "b": {t: by[t]["record"]["b"][t] for t in truths}}
    g["gate_sample"] = dict(first["gate_sample"], seeds={t: by[t]["gate_sample"]["seeds"][t] for t in truths})
    reads, back = g["reads"], g["backstop"]
    g["verdict"] = "PASS" if all(v == "option (1)" for v in reads.values()) and all(b["passes"] for b in back.values()) \
        else "STOP"
    g["reading"] = "option (1)" if g["verdict"] == "PASS" else "; ".join(f"{t} {v}" for t, v in reads.items())
    g["seconds"] = round(sum(p["seconds"] for p in parts), 1)
    g["atime"] = {"moved": sorted({m for p in parts for m in p["atime"]["moved"]}), "parts": [p["atime"] for p in parts]}
    g["merged_from"] = [{"truths": p["truths"], "seconds": p["seconds"]} for p in parts]
    return g


def c2_inputs(a, P: dict) -> tuple:
    """c2_truth's inputs from prepare(rows=True), as c2check and its timing probe both take them: (rel, fm, geo, V,
    cv), with S1's functional required to be the definition's."""
    import fd_1b_mc as mc
    import fd_1b_score as fs
    world = P["world"]
    inputs, bkg = world["inputs"], world["bkg"]
    s1 = mc.via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    if not mc.same_functional(P["U_full"], s1["U"]):
        raise Refusal("the definition's functional is not S1's")
    rel = np.sqrt(np.diag(fs.reported_matrix(s1))) / s1["f"]
    fm = sa.fine_map(a.definition)
    edges = inputs["edges"]
    prec = np.asarray(inputs["pass_reco"], bool)
    geo = {"gen": P["cells"], "reco": np.where(prec, mc.flat_cells(np.asarray(inputs["MCreco"], float), edges), -1),
           "bkg": mc.flat_cells(np.asarray(bkg["bkg_reco"], float), edges), "td": mc.td_cells(world["bank_cv"], edges),
           "fm": np.asarray(fm), "U": P["U"], "shape": P["shape"]}
    V = dict(P["rows"], D=P["D_full"])
    cv = {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
          "bkgw": np.asarray(bkg["bkg_w"], float), "tdw": world["tdw_cv"], "D": P["D_cv_full"]}
    return rel, fm, geo, V, cv


def c2probe_main(a) -> dict:
    """The timing probe before c2check at N (the director's ruling (a), item 3): prepare(rows=True) timed, then
    c2_truth on the first --blocks blocks of one truth's gate sample, each block timed, through c2_inputs as c2check
    takes them. Projects a one-truth c2check job: prepare + (300 + GATE_N) / DRAW_BLOCK blocks at the mean block time.
    Writes a timing record only; nothing in it is a gate."""
    import resource
    import time

    import fd_1b_mc as mc
    if len(a.truths) != 1:
        raise Refusal("the probe times one truth")
    t0 = time.time()
    P = prepare(a, rows=True)
    _, _, geo, V, cv = c2_inputs(a, P)
    t_prep = time.time() - t0
    t = a.truths[0]
    world = P["world"]
    seeds = gate_seeds(t)[:a.blocks * DRAW_BLOCK]
    draws = [mc.draw_universes(toys.draw_for_seed(sd, P["flux_p"], world["groups"])) for sd in seeds]
    S = selection(draws, P["col"], P["bands"])
    phi = draw_flux(S, P["flux_cols"], P["phi"])
    per_block = []
    for b in range(a.blocks):
        sl = slice(b * DRAW_BLOCK, (b + 1) * DRAW_BLOCK)
        t1 = time.time()
        c2_truth(V, cv, S[sl], P["r"][t], geo, phi[sl], P["const"])
        per_block.append(time.time() - t1)
    blocks_per_truth = (len(mc.TOY_SEEDS[t]) + GATE_N) // DRAW_BLOCK
    mean = float(np.mean(per_block[1:] if len(per_block) > 1 else per_block))
    return {"schema": "fd-1b-c2-probe/1", "step": "c2-probe", "truth": t, "blocks": a.blocks, "draw_block": DRAW_BLOCK,
            "prepare_seconds": t_prep, "block_seconds": per_block, "block_seconds_used": mean,
            "blocks_per_truth": blocks_per_truth, "projected_seconds_per_truth": t_prep + blocks_per_truth * mean,
            "rows": {k: int(np.shape(v)[-1]) for k, v in V.items()}, "universes": int(np.shape(V["wt"])[0]),
            "threads": {k: os.environ.get(k) for k in THREAD_VARS},
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "code_sha256": gate_code_digests()}


def c2check_main(a) -> dict:
    """The pre-bulk C2 gate (A2.1's S1 and S2, on Joseph's large sample): C2's record on 1B's 16 cells over each
    truth's GATE_N-draw gate sample (gate_seeds), read by reading_1b with the large-sample gate (gate_n) at the
    calibration's thresholds; the 300 declared draws computed apart and required equal to the sample's first 300
    bitwise; the backstop (P6) on those 300. Tied to its calibration (CALIBRATED at N, digests pinned, its
    single-universe U x_T bitwise this job's) and to the 300-draw calibration whose SDs the backstop uses. PASS needs
    "option (1)" and the backstop at every truth; anything else is the hard stop (STOP), and 1B returns to Joseph."""
    import hashlib
    import time

    import fd_1b_inv as inv
    import fd_1b_mc as mc
    t0 = time.time()
    if inv.sha256_noatime(a.calibration) != a.expect_calibration_sha256:
        raise Refusal("the calibration record's digest differs")
    with inv.open_noatime(a.calibration) as fh:
        cal = json.loads(fh.read().decode())
    if cal.get("schema") != SCHEMA_CAL or cal.get("verdict") != "CALIBRATED":
        raise Refusal(f"the calibration is {cal.get('verdict')!r}, not CALIBRATED: nothing proceeds")
    if inv.sha256_noatime(a.calibration_300) != a.expect_calibration_300_sha256:
        raise Refusal("the 300-draw calibration's digest differs")
    with inv.open_noatime(a.calibration_300) as fh:
        cal300 = json.loads(fh.read().decode())
    if cal300.get("schema") != "fd-1b-c2-calibration/1":
        raise Refusal("the backstop's SDs come from the 300-draw calibration (schema /1)")
    cal_npz = a.calibration.with_suffix(".npz")
    if inv.sha256_noatime(cal_npz) != a.expect_calibration_npz_sha256:
        raise Refusal("the calibration's ratio file digest differs")
    P = prepare(a, rows=True)
    world, truths = P["world"], P["truths"]
    if not truths or not set(truths) <= set(cal["truths"]):         # one truth per job (the director's ruling (a))
        raise Refusal("c2check's truths are not among the calibration's")
    with inv.open_noatime(cal_npz) as fh:
        z = np.load(fh, allow_pickle=False)
        for t in truths:
            if not np.array_equal(z[f"single_x_{t}"], P["single_x"][t]):
                raise Refusal(f"{t}: the single-universe U x_T is not the calibration's (a different world or code)")
    rel, fm, geo, V, cv = c2_inputs(a, P)
    inputs, ptru = world["inputs"], np.asarray(world["inputs"]["pass_truth"], bool)
    rec = {"vi": row_match(np.asarray(inputs["MCgen"], float), cv["wt"], ptru & (P["cells"] >= 0),
                           np.column_stack([np.asarray(world["bank_cv"][k], np.float64) for k in
                                            ("td_pt", "td_pz", "td_ea", "td_q3", "td_w")]), world["tdw_cv"],
                           np.where(P["cells"] >= 0, fm[np.maximum(P["cells"], 0)], -1),
                           np.where(geo["td"] >= 0, fm[np.maximum(geo["td"], 0)], -1)), "b": {}}
    seeds, back, reading = {}, {}, {}
    n = getattr(a, "draws", GATE_N)
    for t in truths:
        def q_of(seed_list):
            draws = [mc.draw_universes(toys.draw_for_seed(sd, P["flux_p"], world["groups"])) for sd in seed_list]
            S = selection(draws, P["col"], P["bands"])
            return c2_truth(V, cv, S, P["r"][t], geo, draw_flux(S, P["flux_cols"], P["phi"]), P["const"])
        q300 = q_of(mc.TOY_SEEDS[t])
        qn = q_of(gate_seeds(t)[:n])
        for k, v in q300.items():                             # P1: the declared 300 are the sample's first 300
            if not np.array_equal(qn[k][:, :v.shape[1]], v):
                raise Refusal(f"{t}: the gate sample's first 300 differ from the declared draws in {k}")
        rec["b"][t] = c2_block(qn, P["ref_x"][t], rel)
        thr = cal["rule"]["thresholds"][t]
        rt = reading_1b({"vi": rec["vi"], "b": {t: rec["b"][t]}},
                        {CLIPPED: lambda v, thr=thr: gate_n(v, thr)["passes"], "first_order": c2_gate,
                         "multiplicative": c2_gate})
        reading[t] = dict(rt[t], gate_n=gate_n(rec["b"][t]["variance_ratio"][CLIPPED], thr))
        r300 = np.var(q300["Nc"], axis=1, ddof=1) / P["ref_x"][t]
        back[t] = backstop(r300, cal300["outputs"][t]["a"]["sd_per_cell"])
        seeds[t] = [int(mc.TOY_SEEDS[t][0]), int(mc.TOY_SEEDS[t][-1])]
    reads = {t: reading[t]["reads"] for t in truths}
    verdict = "PASS" if all(v == "option (1)" for v in reads.values()) and all(b["passes"] for b in back.values()) \
        else "STOP"
    digests = gate_code_digests()
    ins = {"npz_sha256": world["npz_sha"], "bkg_sha256": world["bkg_sha"], "pins_sha256": a.expect_pins_sha256,
           "flux_table_sha256": a.expect_flux_table_sha256, "push_sha256": a.expect_push_sha256,
           "cv_tdw_sha256": a.expect_cv_tdw_sha256}
    s_row = next((g for g in cal["rule"]["grid"] if g["s"] == cal["rule"]["s"]), None)
    gate = {"schema": SCHEMA_GATE, "step": "c2-clip-gate", "verdict": verdict,
            "reading": "option (1)" if verdict == "PASS" else "; ".join(f"{t} {v}" for t, v in reads.items()),
            "reads": reads, "truths": truths, "declared_seeds": seeds, "code_sha256": digests,
            "calibration_sha256": a.expect_calibration_sha256, "calibration_npz_sha256": a.expect_calibration_npz_sha256,
            "calibration": {"verdict": cal["verdict"], "sha256": a.expect_calibration_sha256, "s": cal["rule"]["s"],
                            "union": None if s_row is None else s_row["union"],
                            "three_truths_measured": cal["rule"]["three_truths_measured"],
                            "power_meets": bool(cal["power"] and cal["power"]["meets"])},
            "calibration_300_sha256": a.expect_calibration_300_sha256, "backstop": back,
            "gate_sample": {"n": n, "first_300_bitwise": True, "seeds": {t: [gate_seeds(t)[0], gate_seeds(t)[n - 1]]
                                                                          for t in truths}},
            "config_hash": config_hash(digests, ins, "nature"), "inputs": ins,
            "sigma": "S1's reported (fd_data_product C_total_plus_C_resp) relative sigma_c, a proxy for C_T, under "
                     "clip_probe2's key sigma_Q", "c2_reading_sha256": hashlib.sha256(
                         (CP2_DIR / "c2_reading.txt").read_bytes()).hexdigest(),
            "record": rec, "reading_detail": reading, "r_negative": P["r_neg"],
            "threads": {k: os.environ.get(k) for k in THREAD_VARS},
            "seconds": round(time.time() - t0, 1), "atime": inv.atime_check()}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(gate, indent=1, sort_keys=True))
    return gate


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("calibrate")
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "definition", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--expect-flux-table-sha256", required=True)
    p.add_argument("--prep", type=Path, required=True)
    p.add_argument("--push", type=Path, default=None)
    p.add_argument("--expect-push-sha256", default=None)
    p.add_argument("--cv-tdw", type=Path, default=None)
    p.add_argument("--expect-cv-tdw-sha256", default=None)
    p.add_argument("--truths", nargs="+", choices=tuple(CAL_SEED), required=True)
    p.add_argument("--sets", type=int, default=CAL_SETS)
    p.add_argument("--workers", type=int, required=True)
    p.add_argument("--budget-seconds", type=float, required=True)
    p = sub.add_parser("c2check")
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "definition", "staged",
              "calibration", "cv-tdw", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--calibration-300", type=Path, required=True)
    for k in ("pins", "flux-table", "calibration", "calibration-npz", "calibration-300", "cv-tdw"):
        p.add_argument(f"--expect-{k}-sha256", required=True)
    p.add_argument("--prep", type=Path, required=True)
    p.add_argument("--push", type=Path, default=None)
    p.add_argument("--expect-push-sha256", default=None)
    p.add_argument("--truths", nargs="+", choices=tuple(CAL_SEED), required=True)
    p = sub.add_parser("c2probe")
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "definition", "staged",
              "cv-tdw", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    for k in ("pins", "flux-table", "cv-tdw"):
        p.add_argument(f"--expect-{k}-sha256", required=True)
    p.add_argument("--prep", type=Path, required=True)
    p.add_argument("--push", type=Path, default=None)
    p.add_argument("--expect-push-sha256", default=None)
    p.add_argument("--truths", nargs=1, choices=tuple(CAL_SEED), required=True)
    p.add_argument("--blocks", type=int, required=True)
    p = sub.add_parser("c2check-merge")
    p.add_argument("--part", type=Path, action="append", required=True)
    p.add_argument("--expect-part-sha256", action="append", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "c2probe":
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        rec = c2probe_main(a)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
        print(f"C2-PROBE truth={rec['truth']} prepare={rec['prepare_seconds']:.0f}s block={rec['block_seconds_used']:.1f}s "
              f"projected_per_truth={rec['projected_seconds_per_truth']:.0f}s")
        return 0
    if a.cmd == "c2check-merge":
        import hashlib
        if len(a.part) != len(a.expect_part_sha256):
            raise Refusal("one --expect-part-sha256 per --part")
        parts = []
        for path, sha in zip(a.part, a.expect_part_sha256):
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != sha:
                raise Refusal(f"{path}: its digest is not the one given")
            parts.append(json.loads(raw))
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        g = c2check_merge(parts)
        g["merged_from"] = [dict(m, sha256=sha) for m, sha in zip(g["merged_from"], a.expect_part_sha256)]
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(g, indent=1, sort_keys=True))
        print(f"C2-GATE-MERGED verdict={g['verdict']} reads={json.dumps(g['reads'], sort_keys=True)}")
        return 0 if g["verdict"] == "PASS" else 3
    if a.cmd == "c2check":
        g = c2check_main(a)
        print(f"C2-GATE verdict={g['verdict']} reads={json.dumps(g['reads'], sort_keys=True)}")
        return 0 if g["verdict"] == "PASS" else 3
    if a.cmd == "calibrate":
        if a.sets != CAL_SETS:
            raise Refusal(f"the calibration is declared at {CAL_SETS} sets per truth")
        rec = calibrate_main(a)
        print(f"C2-CALIBRATION verdict={rec['verdict']} s={rec['rule']['s']} "
              f"i_alone={rec['rule']['i_alone_union']:.4f} power={json.dumps(rec['power'] and {t: v['uniform'] for t, v in rec['power'].items() if t != 'meets'})}")
        return 0 if rec["verdict"] == "CALIBRATED" else 3
    return 2


if __name__ == "__main__":
    sys.exit(main())

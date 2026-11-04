#!/usr/bin/env python3
"""1B staged method coverage, stage 1 (state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md
sections 4-9, revision 2; FD-1B-STAGED-AMENDMENT-2.md for binding 3, under DECISION-20261102-joseph-1b-redesign.md):
pseudo-data at a held-out truth T with every uncertainty group drawn, the covariance remade at T by S1's procedure,
and the grading against a null matched to the draws.

Amendment 2: a drawn nature composes to FIRST ORDER (``compose``: a_D = a_u1 + sum_{j>=2} (a_uj - a_CV) in the
draw's order), as C_T's per-band blocks are built; a composite denominator cell with d_CV > 0 and d_D <= 0 refuses;
every Poisson draw sees lambda+ = max(lambda, 0) on the full product (``clip_draw``), with the clipped mass recorded.

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
  product bitwise;
* ``clipmean`` (amendment 2): d_T at its mean plus the clipped mass |lambda-| of the receipt's reference nature N_clip,
  unfolded by S1's path like ``central``; the readout's clipping offset is U (x_clipmean - x_central) / sigma_c.

Other subcommands: ``stage-flux`` (the flux-universe table read once through O_NOATIME into an npz), ``receipt``
(section 4.2's bank counts, N1's single ratios, N1's composite on every row over the declared draws, exactly in
float64 behind a proven screen, the denominator check, N_clip and the cross-term readout; before the bulk, a one-node
job), ``walls`` (S1-0's re-price trigger), ``n1`` (the toys' own N1 record at T, read before
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
import io
import json
import math
import os
import resource
import sys
import tempfile
import time
import warnings
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
import s5e_deform  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402
import s5p_universe  # noqa: E402
import xsec_nd  # noqa: E402

SCHEMA = "fd-1b-mc/1"
TRUTHS = {"g18": "genie_v3_g18", "ar23": "genie_v3_ar23", "plugin": "plugin"}
TOY_SEEDS = {"g18": range(3_620_000, 3_620_300), "ar23": range(3_630_000, 3_630_300),
             "plugin": range(3_640_000, 3_640_300)}
STAT_SEED = {"g18": 3_621_000, "ar23": 3_631_000, "plugin": 3_641_000}
STAT_REPLICAS = sa.STAT_REPLICAS                     # 1..50, set A's
JITTER_OFFSET = 100                                  # set A's products are data_b<b>_j<100+b>
SEED_CHECK = 45
CONTROLS = ("setA_b1", "MaRES_0", "Flux_0", "GEANT_Pion_0")
ROLES = ("central", "seed", "block", "stat", "toy", "control", "capture", "clipmean")
N1_BOUND = 10.0                                      # N1: a composite or single ratio above this is counted
NEAR_BOUND_REL = 1e-9                                # pairs this close to the bound are recomputed in compose's order
MAX_PAIRS = 50_000_000                               # (row, draw) pairs past the screen; more refuses (INVALID)
DRAW_BLOCK = 20                                      # declared draws per matmul block in the receipt
VALIDATE_FRACTION = 0.005                            # the receipt's no-screen check on a seeded sample of rows
VALIDATE_SEED = 3_659_001                            # not a declared toy, stat or validation seed elsewhere
CLIP_DELTA_STAR = 0.667                              # |o_c| that lowers +-1 sigma content by 0.10 (section 5.2)
CLIP_RULES = ("data", "nature")                      # a named input: decision 2a (a), or the nature clipped in truth too
NATURE_UNRULED = ("the clipping offset (clipmean, clipcheck) is the 'data' rule's descriptive figure; a 'nature' "
                  "bulk is gated by C2's reading (DECISION-20261103-joseph-coverage-clip-rule) and graded under "
                  "addendum A2.1, whose readout reports the offset from S1-0b's 'data' products")
CLIP_GATE = {"step": "c2-clip-gate", "reading": "option (1)", "verdict": "PASS"}   # what c2check's record must say
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


def compose(inputs: dict, bkg: dict, bank_cv, tags: list[str], load, flux: np.ndarray | None,
            tdw_cv: np.ndarray | None = None) -> tuple[dict, dict, dict]:
    """Section 4.2's rule as amendment 2 makes it: first order. ``tags`` is the draw's universes in the draw's order and
    ``load(tag)`` their weights as ``fd_1b_inv.universe_weights(..., "zero")`` loads them; the universes are streamed,
    one in memory at a time. Every per-row array a, and the denominator per cell, composes as
    a_D = a_u1 + sum_{j>=2} (a_uj - a_CV), summed in the draw's order, so one universe is ``universe_inputs``' arrays
    bitwise and rows with a_CV = 0 sum as before. The flux is the one flux universe's. A composite (two or more
    universes) refuses a denominator cell with d_CV > 0 and d_D <= 0 (section 2b, fail closed). N1's record: per array,
    max over rows of |a_D| / max_j |a_uj|, and the rows with a_D < 0 where a_CV > 0 (descriptive).
    A composite (two or more universes) needs ``tdw_cv`` (the CV's per-row denominator weight, fd_1b_cvdenom's), under
    either rule (A2.1, the director's (e2)): d_CV is then hist_f32(tdw_CV), the CV's rows binned on cv.npz's float32
    td_* as every bank universe's denominator is, and a detector universe's denominator, the npz's denom_nd bitwise
    (check D; otherwise compose refuses), is the same hist_f32, so no composite mixes binnings. The denominator rows
    compose too, for the nature rule's row clip: a bank universe brings its tdw, a detector universe the CV's."""
    cv = _cv_arrays(inputs, bkg)
    ui, ub = dict(inputs), dict(bkg)
    if not tags:
        return ui, ub, {"universes": []}
    d32 = None
    if len(tags) > 1:
        if tdw_cv is None:
            raise Refusal("a composite needs the CV's per-row tdw (--cv-tdw), so no composite mixes binnings (A2.1 e2)")
        d32 = np.asarray(s5p_universe.denominator(bank_cv, tdw_cv, inputs["edges"]), float)
    npz_denom = cv["denom"]
    if d32 is not None:
        cv = dict(cv, denom=d32)
    acc, peak, fluxes = {}, {}, []
    rows = None
    for j, tag in enumerate(tags):
        w = load(tag)
        single, phi = _single(inputs, bkg, bank_cv, tag, w, flux)
        if tdw_cv is not None:
            if "tdw" in w:
                row = np.asarray(w["tdw"], float)
            elif np.array_equal(single["denom"], npz_denom):
                row = tdw_cv
                if d32 is not None:
                    single["denom"] = d32
            else:
                raise Refusal(f"{tag}: its denominator is not the CV's, so the row clip is undefined (A2.1, S3 (d1))")
            rows = row.copy() if j == 0 else rows + (row - tdw_cv)
        del w
        if phi is not None:
            fluxes.append(phi)
        for k, a_u in single.items():
            if j == 0:
                acc[k], peak[k] = a_u.copy(), np.abs(a_u)
                continue
            acc[k] += a_u - cv[k]
            np.maximum(peak[k], np.abs(a_u), out=peak[k])
        del single
    if len(fluxes) > 1:
        raise Refusal("a draw holds more than one flux universe")
    if len(tags) > 1:
        bad = int(np.sum((cv["denom"] > 0) & (acc["denom"] <= 0)))
        if bad:
            raise Refusal(f"the composite denominator is <= 0 in {bad} cells where the CV's is > 0 (section 2b)")
    stats = {}
    for k in acc:
        r = n1_ratio(acc[k], peak[k])
        stats[k] = {"max_composite_over_max_single": float(np.max(r)), "rows_above_bound": int(np.sum(r > N1_BOUND)),
                    "rows_negative_where_cv_positive": int(np.sum((acc[k] < 0) & (cv[k] > 0)))}
    ui["w_truth"], ui["w_reco"], ui["denom_nd"] = acc["wt"], acc["wr"], acc["denom"]
    if rows is not None:
        ui["tdw_rows"], ui["td_cells"] = rows, td_cells(bank_cv, inputs["edges"])
    ub["bkg_w"] = acc["bkgw"]
    if fluxes:
        ui["flux"] = fluxes[0]
    return ui, ub, {"universes": list(tags), "n1": stats}


def same_functional(U: np.ndarray, stored: np.ndarray) -> bool:
    """The definition's functional against S1's, in the precision S1 stored it (s1_assemble writes U as float32): exact
    equality there. An absolute tolerance cannot be met, since U holds fine-bin volumes up to about 3.7e7 and float32
    rounding moves them by up to 0.05 (A2.1, a fix to amendment 2's receipt and clipcheck and binding 2's null_step
    and readout, none of which had run on real data)."""
    return bool(np.array_equal(np.asarray(U).astype(np.float32), np.asarray(stored).astype(np.float32)))


def td_cells(bank_cv, edges) -> np.ndarray:
    """The truth-denominator rows' 5D cells (C order, -1 outside), as s5p_universe.denominator bins them."""
    coords = np.column_stack([np.asarray(bank_cv[k], np.float64) for k in ("td_pt", "td_pz", "td_ea", "td_q3", "td_w")])
    return flat_cells(coords, edges)


def n1_ratio(a_D: np.ndarray, peak: np.ndarray) -> np.ndarray:
    """N1's statistic per row: |a_D| / peak, with peak = max_j |a_uj| over the draw's universes; 1 where both are 0
    and +inf where only the peak is."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(peak > 0, np.abs(a_D) / peak, np.where(a_D == 0, 1.0, np.inf))


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


class InvalidReceipt(Refusal):
    """The receipt could not decide (a budget, the validation, a missing band): INVALID, never a STOP; it may be rerun."""


def draw_columns(draws: list[list[str]], col: dict[str, int]) -> list[np.ndarray]:
    """Each draw's universe columns in the draw's order; every draw must hold one universe of every band, which the
    screen's proof needs."""
    bands = {t.rpartition("_")[0] for t in col}
    out = []
    for tags in draws:
        if sorted(t.rpartition("_")[0] for t in tags) != sorted(bands):
            raise InvalidReceipt("a declared draw does not hold exactly one universe of every band")
        out.append(np.array([col[t] for t in tags]))
    return out


def screen_floor(V: np.ndarray, col: dict[str, int]) -> np.ndarray:
    """L per row: max over bands b of min over b's universes of |a_u|.

    Proposition (amendment 2, section 3): every declared draw D holds one universe u_b of every band b, so its peak
    max_j |a_uj| >= |a_{u_b}| >= min_{u in b} |a_u| for every b, hence peak >= L. N1's statistic is |a_D| / peak
    (``n1_ratio``). If |a_D| <= 10 L: with L > 0, peak >= L > 0 and the ratio is <= |a_D| / L <= 10; with L = 0,
    a_D = 0 and the ratio is 0 (peak > 0) or 1 (peak = 0). So no (row, draw) with |a_D| <= 10 L exceeds the bound."""
    by_band: dict[str, list[int]] = {}
    for t, c in col.items():
        by_band.setdefault(t.rpartition("_")[0], []).append(c)
    L = np.zeros(V.shape[1])
    for cs in by_band.values():
        np.maximum(L, np.min(np.abs(V[cs]), axis=0), out=L)
    return L


def screen_floor_check(V: np.ndarray, col: dict[str, int], L: np.ndarray) -> bool:
    """An independent recomputation of the screen's floor on EVERY row (a band at a time, by an explicit loop over
    its universes), compared exactly with ``screen_floor``'s: the in-job sample may hold no row above the bound, so a
    wrong floor must also be caught where the sample cannot see it."""
    ref = np.zeros(V.shape[1])
    for b in sorted({t.rpartition("_")[0] for t in col}):
        lo = None
        for t in sorted(t for t in col if t.rpartition("_")[0] == b):
            a = np.abs(V[col[t]])
            lo = a.copy() if lo is None else np.minimum(lo, a)
        ref = np.maximum(ref, lo)
    return bool(np.array_equal(ref, L))


def pinned_composite(V: np.ndarray, cv: np.ndarray, cols: np.ndarray, rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``compose``'s arithmetic on the given rows, in the draw's order: a_D and the peak."""
    acc = V[cols[0], rows].copy()
    peak = np.abs(acc)
    for c in cols[1:]:
        acc += V[c, rows] - cv[rows]
        np.maximum(peak, np.abs(V[c, rows]), out=peak)
    return acc, peak


def exact_n1(V: np.ndarray, cv: np.ndarray, dcols: list[np.ndarray], L: np.ndarray, sample: np.ndarray,
             block: int = DRAW_BLOCK, max_pairs: int = MAX_PAIRS, reco: np.ndarray | None = None) -> dict:
    """N1 on every row over every declared draw, exactly (the director's ruling on section 2d, (ii), with the screen
    he ruled consistent with it). The composite for a block of draws is S V - (k - 1) a_CV (float64 BLAS); pairs past
    the screen |a_D| > 10 L get the exact peak; pairs within ``NEAR_BOUND_REL`` of the bound are recomputed in
    compose's order. ``sample`` rows (the validation) keep their per-draw outcome. Returns the counts, the per-draw
    negative-composite counts and sum of negative a_D over ``reco`` rows (descriptive, matmul arithmetic)."""
    n_u, n = V.shape
    S = np.zeros((len(dcols), n_u))
    for d, cs in enumerate(dcols):
        S[d, cs] = 1.0
    k = S.sum(axis=1)
    lim = N1_BOUND * L * (1.0 - NEAR_BOUND_REL)    # the matmul's |a_D| is rounded: keep the proof's premise strict
    pairs = 0
    for d0 in range(0, len(dcols), block):
        A = S[d0:d0 + block] @ V - (k[d0:d0 + block, None] - 1.0) * cv[None, :]
        pairs += int(np.count_nonzero(np.abs(A) > lim[None, :]))
    if pairs > max_pairs:
        raise InvalidReceipt(f"{pairs} (row, draw) pairs past the screen exceed the budget {max_pairs}")
    worst = np.zeros(n)
    above_rows = np.zeros(n, bool)
    in_sample = np.zeros(n, bool)
    in_sample[sample] = True
    sample_above: set[tuple[int, int]] = set()
    near, pairs_above, max_r = 0, 0, 0.0
    neg_rows = np.zeros(len(dcols), np.int64)
    neg_sum = np.zeros(len(dcols))
    comp_sum = np.zeros(len(dcols))
    neg_any = np.zeros(n, bool)
    rmask = np.ones(n, bool) if reco is None else np.asarray(reco, bool)
    for d0 in range(0, len(dcols), block):
        A = S[d0:d0 + block] @ V - (k[d0:d0 + block, None] - 1.0) * cv[None, :]
        for i in range(A.shape[0]):
            d = d0 + i
            a = A[i]
            negd = (a < 0) & (cv > 0)
            neg_rows[d] = int(np.count_nonzero(negd))
            neg_any |= negd
            neg_sum[d] = float(np.sum(np.minimum(a[rmask], 0.0)))
            comp_sum[d] = float(np.sum(a[rmask]))
            rows = np.flatnonzero(np.abs(a) > lim)
            if rows.size == 0:
                continue
            cs = dcols[d]
            peak = np.abs(V[cs[0], rows])
            for c in cs[1:]:
                np.maximum(peak, np.abs(V[c, rows]), out=peak)
            r = n1_ratio(a[rows], peak)
            close = np.abs(r - N1_BOUND) <= NEAR_BOUND_REL * N1_BOUND
            if np.any(close):
                near += int(close.sum())
                acc, pk = pinned_composite(V, cv, cs, rows[close])
                r[close] = n1_ratio(acc, pk)
            hit = r > N1_BOUND
            worst[rows] = np.maximum(worst[rows], r)
            above_rows[rows[hit]] = True
            pairs_above += int(hit.sum())
            if r.size:
                max_r = max(max_r, float(r.max()))
            for row in rows[hit & in_sample[rows]]:
                sample_above.add((d, int(row)))
    return {"rows": int(n), "pairs_past_screen": pairs, "near_bound_recomputed": near, "pairs_above": pairs_above,
            "rows_above": int(above_rows.sum()), "max_evaluated": max_r, "worst": worst, "sample_above": sample_above,
            "negative_composite_rows": neg_rows, "negative_composite_sum": neg_sum, "composite_sum": comp_sum,
            "negative_rows_in_some_draw": int(neg_any.sum()), "negative_any": neg_any}


def no_screen_n1(V: np.ndarray, cv: np.ndarray, dcols: list[np.ndarray], rows: np.ndarray) -> np.ndarray:
    """The validation's reference: N1's statistic on ``rows`` for every draw, in compose's order, with no screen."""
    out = np.zeros((len(dcols), rows.size))
    for d, cs in enumerate(dcols):
        acc, peak = pinned_composite(V, cv, cs, rows)
        out[d] = n1_ratio(acc, peak)
    return out


def validate_screen(res: dict, ref: np.ndarray, rows: np.ndarray) -> list[str]:
    """The director's in-job check: on the sampled rows, the no-screen outcome equals the screened one, pair by pair
    (which pairs exceed the bound) and row by row (each row's worst, where it exceeds the bound)."""
    bad = []
    want = {(d, int(rows[j])) for d, j in zip(*np.nonzero(ref > N1_BOUND))}
    if want != res["sample_above"]:
        bad.append(f"pairs above differ: {len(want ^ res['sample_above'])} pairs")
    for j, row in enumerate(rows):
        w_ref = float(ref[:, j].max())
        if w_ref > N1_BOUND and abs(res["worst"][row] - w_ref) > 1e-12 * w_ref:
            bad.append(f"row {int(row)}: worst {res['worst'][row]} != {w_ref}")
    return bad


def denominator_check(D: np.ndarray, dcv: np.ndarray, dcols: list[np.ndarray]) -> dict:
    """On every declared draw, in compose's order: section 2b (the audit's P2), the cells with d_CV > 0 and d_D <= 0;
    and N1 on the denominator per cell (the audit's C2 on #717), exactly, as compose's record and ``n1`` read it."""
    bad, above, max_r = {}, {}, 0.0
    pos = dcv > 0
    flat_cv = dcv.ravel()
    for d, cs in enumerate(dcols):
        acc = D[cs[0]].copy()
        peak = np.abs(acc)
        for c in cs[1:]:
            acc += D[c] - dcv
            np.maximum(peak, np.abs(D[c]), out=peak)
        n = int(np.sum(pos & (acc <= 0)))
        if n:
            bad[d] = n
        r = n1_ratio(acc, peak).ravel()
        max_r = max(max_r, float(r.max()))
        k = int(np.sum(r > N1_BOUND))
        if k:
            above[d] = k
    return {"draws_with_nonpositive_cells": sorted(bad), "max_cells": max(bad.values()) if bad else 0,
            "n1": {"cells": int(flat_cv.size), "pairs_above": int(sum(above.values())),
                   "draws_with_cells_above": sorted(above), "max": max_r}}


def crossterm(V: np.ndarray, cv: np.ndarray, dcols: list[np.ndarray], flat: np.ndarray, n_bins: int, U: np.ndarray,
              block: int = DRAW_BLOCK) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Consult item (i), descriptive: per declared draw, the U-mapped histogram of a_D over the rows with
    ``flat`` >= 0 (their 5D cell), under the product rule (binding 2's: a_CV prod_j (a_uj / a_CV) where a_CV != 0, the
    sum where a_CV = 0) and under first order. The product goes by logs and sign parity (BLAS); first order is
    S V - (k - 1) a_CV. Returns (H_product, H_first_order) as [draws, cells], and H_CV."""
    m = flat >= 0
    Vm, cm, fm = V[:, m], cv[m], flat[m]
    nz = cm != 0
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = np.where(nz[None, :], Vm / np.where(nz, cm, 1.0)[None, :], 0.0)
    zero = (rho == 0) & nz[None, :]
    logs = np.log(np.where(nz[None, :] & (rho != 0), np.abs(rho), 1.0))      # 0 where a_CV = 0 or rho = 0
    negs = (rho < 0).astype(float)
    zf = zero.astype(float)
    S = np.zeros((len(dcols), V.shape[0]))
    for d, cs in enumerate(dcols):
        S[d, cs] = 1.0
    k = S.sum(axis=1)
    H_p = np.zeros((len(dcols), U.shape[0]))
    H_a = np.zeros((len(dcols), U.shape[0]))
    for d0 in range(0, len(dcols), block):
        Sb = S[d0:d0 + block]
        A = Sb @ Vm - (k[d0:d0 + block, None] - 1.0) * cm[None, :]
        sign = np.where(np.mod(np.rint(Sb @ negs), 2) == 1, -1.0, 1.0)
        P = np.where(nz[None, :], cm[None, :] * np.exp(Sb @ logs) * sign * ((Sb @ zf) == 0), A)
        for i in range(A.shape[0]):
            H_a[d0 + i] = U @ np.bincount(fm, weights=A[i], minlength=n_bins)
            H_p[d0 + i] = U @ np.bincount(fm, weights=P[i], minlength=n_bins)
    return H_p, H_a, U @ np.bincount(fm, weights=cm, minlength=n_bins)


def flat_cells(coords: np.ndarray, edges) -> np.ndarray:
    """Each row's 5D cell index in C order on the analysis edges (``np.histogramdd``'s bins), -1 outside."""
    idx, inside = [], np.ones(coords.shape[0], bool)
    for dim, e in enumerate(edges):
        e = np.asarray(e, float)
        i = np.searchsorted(e, coords[:, dim], side="right") - 1
        i = np.where(coords[:, dim] == e[-1], e.size - 2, i)        # histogramdd's closed last edge
        inside &= (i >= 0) & (i < e.size - 1)
        idx.append(np.clip(i, 0, e.size - 2))
    shape = tuple(np.asarray(e).size - 1 for e in edges)
    return np.where(inside, np.ravel_multi_index(idx, shape), -1)


def cross_z(H_p: np.ndarray, H_a: np.ndarray, H_cv: np.ndarray, rel_sigma: np.ndarray) -> dict:
    """z_c = [(H_product - H_first_order) / H_CV]_c / (sigma_c / x_c), per draw; its summary per cell."""
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(H_cv > 0, (H_p - H_a) / H_cv, 0.0) / rel_sigma[None, :]
    az = np.abs(z)
    return {"median_abs": np.median(az, axis=0).tolist(), "q95_abs": np.quantile(az, 0.95, axis=0).tolist(),
            "max_abs": az.max(axis=0).tolist(), "median_signed": np.median(z, axis=0).tolist()}


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
    s5e_deform.install_ratio_truth(s5n_pseudo)      # idempotent; the bulk installs it in run_unfold, A2.1's jobs do not
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


def _flat_hist(coords: np.ndarray, w: np.ndarray, edges) -> np.ndarray:
    """A weighted 5D histogram on the analysis edges, flattened as ``xsec_flat`` is (C order)."""
    h, _ = np.histogramdd(np.asarray(coords, float), bins=edges, weights=np.asarray(w, float))
    return h.ravel(order="C")


NATURE_CLIP_ARRAYS = ("clip_truth_nature_flat", "clip_denom_flat")


def clip_draw(ui: dict, ub: dict, r: np.ndarray, rule: str = "data") -> tuple[dict, dict, dict]:
    """Every Poisson draw sees lambda+ = max(lambda, 0) on the full product, lambda = w_reco * r on reco-passing rows
    and bkg_w on background rows (``fd_1b_toys.build_full`` with unit source factors). The draw's weights are zeroed
    where lambda < 0, so build_full's lambda is exactly lambda+. The clipping rule is a named input:
    * ``"data"`` (decision section 2a (a)): the nature's truth and denominator are untouched;
    * ``"nature"`` (Joseph's #718: C2's option (1), addendum A2.1's S3): the pseudo-data see lambda+ as under "data",
      and the truth is clipped row by row on its own sign, max(w_truth * r, 0), independently of lambda
      (``cov2d.lam_plus`` on each). A row with lambda < 0 keeps its truth; a row with w_truth * r < 0 keeps its reco.
      The denominator's rows (``compose``'s ``tdw_rows``, from the CV's per-row weight) are clipped the same way.
    Returns the draw's (ui, ub) and the clipped mass: sums per component, and |lambda-| per 5D reco cell (signal and
    background) and per 5D truth cell (truth-passing signal rows); under "nature" also the truth's and the
    denominator's clipped mass per 5D truth cell (the readout's clipping section (a))."""
    if rule not in CLIP_RULES:
        raise Refusal(f"clip rule {rule!r} is not one of {CLIP_RULES}")
    edges = ui["edges"]
    reco = np.asarray(ui["pass_reco"], bool)
    w = np.asarray(ui["w_reco"], float)
    lam = w * r
    neg = reco & (lam < 0)
    bw = np.asarray(ub["bkg_w"], float)
    negb = bw < 0
    tneg = neg & np.asarray(ui["pass_truth"], bool)
    rec = {"signal": {"sum_lambda": float(lam[reco].sum()), "sum_negative": float(lam[neg].sum()),
                      "rows_negative": int(neg.sum())},
           "background": {"sum_lambda": float(bw.sum()), "sum_negative": float(bw[negb].sum()),
                          "rows_negative": int(negb.sum())}}
    clip = {"record": rec,
            "clip_reco_flat": _flat_hist(ui["MCreco"][neg], -lam[neg], edges) + _flat_hist(ub["bkg_reco"][negb], -bw[negb], edges),
            "clip_truth_flat": _flat_hist(ui["MCgen"][tneg], -lam[tneg], edges)}
    rec["rule"] = rule
    du = dict(ui, w_reco=np.where(neg, 0.0, w))
    if rule == "nature":
        if "tdw_rows" not in ui:
            raise Refusal("the nature rule clips the denominator by row: compose needs the CV's per-row tdw")
        cells, dr = ui["td_cells"], np.asarray(ui["tdw_rows"], float)
        ok, dneg = cells >= 0, dr < 0
        shape = np.shape(ui["denom_nd"])
        # hist(max(d, 0)) = hist(d) + hist(max(-d, 0)): the composite per cell plus each cell's negative row mass
        # (C2's N + m_all), so a cell with no negative row keeps compose's value bitwise
        m_den = np.bincount(cells[ok & dneg], weights=-dr[ok & dneg], minlength=int(np.prod(shape))).reshape(shape)
        dn = np.where(m_den > 0, np.asarray(ui["denom_nd"], float) + m_den, np.asarray(ui["denom_nd"], float))
        rec["denominator"] = {"sum_rows": float(dr[ok].sum()), "sum_negative": float(dr[ok & dneg].sum()),
                              "rows_negative": int(np.sum(ok & dneg))}
        wt = np.asarray(ui["w_truth"], float)
        tz = np.asarray(ui["pass_truth"], bool) & (wt * r < 0)
        du = dict(du, w_truth=np.where(tz, 0.0, wt), denom_nd=dn)
        rec["truth"] = {"sum_truth": float((wt * r)[np.asarray(ui["pass_truth"], bool)].sum()),
                        "sum_negative": float((wt * r)[tz].sum()), "rows_negative": int(tz.sum())}
        clip["clip_truth_nature_flat"] = _flat_hist(ui["MCgen"][tz], -(wt * r)[tz], edges)   # per 5D truth cell
        clip["clip_denom_flat"] = m_den.ravel(order="C")                                     # the readout's (a)
    return du, dict(ub, bkg_w=np.where(negb, 0.0, bw)), clip


def toy_experiment(inputs: dict, bkg: dict, ui: dict, ub: dict, r: np.ndarray, seed: int,
                   rule: str = "data") -> tuple[dict, np.ndarray, dict]:
    """One toy: Poisson pseudo-data of the nature (ui, ub) at truth r, drawn at lambda+ (``clip_draw``), the nominal MC
    with set A's streams; the truth is the nature's own (negative weights kept under rule "data", zeroed with the
    draw's under "nature")."""
    du, db, clip = clip_draw(ui, ub, r, rule)
    ones_s, ones_b = np.ones(ui["w_reco"].shape[0]), np.ones(ub["bkg_w"].shape[0])
    exp, x_true, _ = toys.build_full(du, db, r, ones_s, ones_b, seed, expectation=False)
    exp = with_mc(exp, inputs, bkg)
    return toys.mc_template_streams(exp, seed), x_true, clip


def stat_experiment(inputs: dict, bkg: dict, r: np.ndarray, seed: int | None, b: int,
                    rule: str = "data") -> tuple[dict, dict | None]:
    """Set A's replica b: coordinates jittered at 100 + b, the experiment (one Poisson realization of T at ``seed``,
    drawn at lambda+, or the real data when ``seed`` is None), then the bootstrap replica b. The nature is the
    nominal one, so lambda+ is lambda wherever r >= 0; the clipped record says whether it was."""
    ji, jb = s5p_numerics.jittered(inputs, bkg, JITTER_OFFSET + b)
    if seed is None:
        return s5n_pseudo.bootstrap_replica(s5n_pseudo.build_data(ji, jb), b), None
    du, db, clip = clip_draw(ji, jb, r, rule)
    ones_s, ones_b = np.ones(ji["w_reco"].shape[0]), np.ones(jb["bkg_w"].shape[0])
    exp, _, _ = toys.build_full(du, db, r, ones_s, ones_b, seed, expectation=False)
    return s5n_pseudo.bootstrap_replica(exp, b), clip["record"]


def clipmean_experiment(inputs: dict, bkg: dict, ui: dict, ub: dict, r: np.ndarray,
                        rule: str = "data") -> tuple[dict, np.ndarray, dict]:
    """(ii)'s mean unfold: d_T at its mean (``mean_experiment``, the nominal nature) plus, as observed events at their
    counts, the clipped mass |lambda-| of the nature (ui, ub) at truth r (signal rows at their reco coordinates,
    background rows at theirs), inside the analysis window as build_full keeps its events. The clipped data equal the
    signed data plus |lambda-|, which cannot be unfolded (the estimator drops non-positive counts); this unfolds the
    response to |lambda-| around d_T instead."""
    exp, x_true = mean_experiment(inputs, bkg, r)
    _, _, clip = clip_draw(ui, ub, r, rule)
    reco = np.asarray(ui["pass_reco"], bool)
    lam = np.asarray(ui["w_reco"], float) * r
    neg = reco & (lam < 0)
    bw = np.asarray(ub["bkg_w"], float)
    negb = bw < 0
    coords = np.concatenate([ui["MCreco"][neg], ub["bkg_reco"][negb]])
    counts = np.concatenate([-lam[neg], -bw[negb]])
    keep = s5n_pseudo.fid_mask(coords, inputs["edges"])
    exp = dict(exp, obs=np.concatenate([exp["obs"], coords[keep]]),
               obs_counts=np.concatenate([exp["obs_counts"], counts[keep]]))
    return exp, x_true, clip


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
    tdw_cv = None
    if getattr(a, "cv_tdw", None) is not None:
        if inv.sha256_noatime(a.cv_tdw) != a.expect_cv_tdw_sha256:
            raise Refusal("the CV per-row denominator weight's digest differs (fd_1b_cvdenom's PASS output)")
        with inv.open_noatime(a.cv_tdw) as fh:
            tdw_cv = np.load(fh, allow_pickle=False).astype(np.float64)
        if tdw_cv.shape != (np.asarray(bank_cv["td_pt"]).size,):
            raise Refusal("the CV per-row denominator weight is not one per truth-denominator row")
        if not (np.all(np.isfinite(tdw_cv)) and np.all(tdw_cv >= 0)):    # the writer's 0 <= w gate, checked (audit)
            raise Refusal("the CV per-row denominator weight has a negative or non-finite row")
    return {"npz_sha": npz_sha, "bkg_sha": bkg_sha, "pins": pins, "inputs": inputs, "bkg": bkg, "bank_cv": bank_cv,
            "tdw_cv": tdw_cv,
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
    rows = world.get("tdw_cv")
    if getattr(a, "clip_rule", None) == "nature" and role in ("toy", "stat") and rows is None:
        raise Refusal("the nature rule needs --cv-tdw (fd_1b_cvdenom's PASS output) for the denominator's row clip")
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
        nominal = inputs if a.clip_rule != "nature" else dict(inputs, tdw_rows=rows,
                                                              td_cells=td_cells(world["bank_cv"], inputs["edges"]))
        exp, clip = stat_experiment(nominal, bkg, truth_weight(truth, inputs, ratio, push), STAT_SEED[truth], b,
                                    a.clip_rule)
        xs, ev = (unfold_fn or _unfold_one64)(exp, a.threads)
        arrays = {"xsec_flat": np.asarray(xs, float).ravel(order="C")}
        meta.update(ev, stat_seed=STAT_SEED[truth], bootstrap_seed=b, jitter_seed=JITTER_OFFSET + b, clip=clip)
    elif role == "toy":
        seed = int(item)
        if seed not in TOY_SEEDS[truth]:
            raise Refusal(f"toy seed {seed} is outside {truth}'s declared range")
        d = toys.draw_for_seed(seed, via_noatime(toys.flux_probabilities, a.flux_constraint), world["groups"])
        tags = draw_universes(d)
        ui, ub, info = compose(inputs, bkg, world["bank_cv"], tags, lambda t: _weights(world, a, t), world["flux"],
                               rows)
        exp, x_true, clip = toy_experiment(inputs, bkg, ui, ub, truth_weight(truth, inputs, ratio, push), seed,
                                           a.clip_rule)
        x_true = np.asarray(x_true, float)
        if not np.all(np.isfinite(x_true)):
            raise Refusal("a non-finite truth")
        xs, ev = (unfold_fn or _unfold)(exp, a.threads)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": x_true.ravel(order="C"),
                  "clip_reco_flat": clip["clip_reco_flat"], "clip_truth_flat": clip["clip_truth_flat"],
                  **{k: clip[k] for k in NATURE_CLIP_ARRAYS if k in clip}}
        meta.update(ev, draw=d, universe_info=info, clip=clip["record"])
    elif role == "clipmean":
        if a.clip_rule != "data":
            raise Refusal(NATURE_UNRULED)
        seed = int(item)
        if not any(seed in TOY_SEEDS[t] for t in TOY_SEEDS):
            raise Refusal(f"N_clip seed {seed} is not a declared toy seed")
        d = toys.draw_for_seed(seed, via_noatime(toys.flux_probabilities, a.flux_constraint), world["groups"])
        ui, ub, info = compose(inputs, bkg, world["bank_cv"], draw_universes(d), lambda t: _weights(world, a, t),
                               world["flux"], rows)
        exp, x_true, clip = clipmean_experiment(inputs, bkg, ui, ub, truth_weight(truth, inputs, ratio, push),
                                                a.clip_rule)
        xs, ev = (unfold_fn or _unfold_s1)(exp, a.threads, toys.ESTIMATOR_SEED)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": np.asarray(x_true, float).ravel(order="C"),
                  "clip_reco_flat": clip["clip_reco_flat"], "clip_truth_flat": clip["clip_truth_flat"]}
        meta.update(ev, n_clip_seed=seed, draw=d, universe_info=info, clip=clip["record"])
    elif role == "control":
        if item not in CONTROLS:
            raise Refusal(f"{item} is not a declared procedure control")
        if item == "setA_b1":
            xs, ev = (unfold_fn or _unfold_one64)(stat_experiment(inputs, bkg, None, None, 1)[0], a.threads)
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
        meta.update(ev, push_min=float(arrays["push"].min()) if arrays["push"].size else None,
                    push_negative=int(np.sum(arrays["push"] < 0)))
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


BULK_ROLES = ("central", "seed", "block", "stat", "toy")    # the graded items: under 'nature' only (A2.1 S2)
# Binding 3 declares c2check's record by its sha256 in this one-line pins file, which it commits; the deploy clone at
# binding 3's merge reads it, so git fixes its content. It is outside every byte gate_code_digests or config_hash
# covers (the audit's H1 at 2c882d27: a digest held in hashed code would need a sha256 fixed point).
GATE_PIN = _ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1/BOUND_GATE.sha256"


def bound_gate_sha256() -> tuple[str, str]:
    """(the declared record sha256, the pins file's git blob) from GATE_PIN; refuses if it is missing or malformed."""
    if not GATE_PIN.exists():
        raise Refusal(f"no c2check record is bound yet: binding 3 commits {GATE_PIN.name} (the director's H1)")
    raw = GATE_PIN.read_bytes()
    text = raw.decode().strip()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text) or raw.decode().count("\n") > 1:
        raise Refusal(f"{GATE_PIN.name} is malformed: one line, a lowercase sha256")
    blob = hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
    return text, blob


def read_bound_gate(a) -> bytes:
    """c2check's gate record as binding 3 declares it (H1), for the bulk's gate and the 'nature' readout alike: the
    bytes of --clip-gate, refused unless their sha256 is --expect-clip-gate-sha256 and that is GATE_PIN's digest.
    Records the pins file's git blob on ``a``."""
    if a.clip_gate is None or a.expect_clip_gate_sha256 is None:
        raise Refusal("the 'nature' rule needs c2check's gate record (--clip-gate, --expect-clip-gate-sha256)")
    bound, blob = bound_gate_sha256()
    if a.expect_clip_gate_sha256 != bound:
        raise Refusal("the clip gate is not the record binding 3 declares")
    a.gate_pin_blob = blob                                  # recorded in each product's meta
    raw = Path(a.clip_gate).read_bytes()
    if hashlib.sha256(raw).hexdigest() != a.expect_clip_gate_sha256:
        raise Refusal("the clip gate's digest differs from the declared one")
    return raw


def pre_gate_items() -> set:
    """What 'data' may run (A2.1 S2): S1-0's pilot items either way the plug-in goes, S1-0b's (each truth's central
    value and its clipmean at a declared seed: the N_clip seed is the receipt's, checked by S1-0b's walls), the
    capture and the controls, as (truth, role, item) the way run_unfold sees them."""
    def as_item(role, item):
        if role in ("control", "capture"):
            return ("data", role, item)
        t, _, it = item.partition(":")
        return (t, role, "T" if role == "central" else it)
    out = {as_item(r, i) for plugin in (True, False) for r, i in PILOT[plugin]}
    out |= {("data", "control", c) for c in CONTROLS} | {("data", "capture", "data")}
    out |= {(t, "central", "T") for t in TRUTHS}
    out |= {(t, "clipmean", str(s)) for t in TRUTHS for u in TOY_SEEDS for s in TOY_SEEDS[u]}
    return out


def check_clip_gate(a) -> None:
    """Joseph's ruling on the clip rule (#718) as A2.1's S2 puts it in code, the hard stop:
    * under 'data', only the pre-gate items run (pre_gate_items): S1-0, S1-0b, the capture, the controls. A graded
      bulk item under 'data' refuses;
    * under 'nature', only the graded roles (BULK_ROLES) run, and only on c2check's gate record whose sha256 is the
      one binding 3 declares in GATE_PIN (none is committed yet, so the bulk refuses). That digest is the
      protection: every field below can be recomputed from the repository and the run's own arguments, so a
      hand-written record of the right form would pass the field checks alone (the audit's H1). Binding 3 records
      which c2check run wrote the file it pins. The fields, re-verified at launch as defence in depth (H2): the
      schema and step, PASS and "option (1)", this truth's own reading, the declared seeds, the code
      (fd_1b_c2.gate_code_digests, equal to this process's), the inputs (the npz and background as declared, and the
      pins, flux table, push and CV per-row tdw digests this run was given); the calibration CALIBRATED, its sha
      the record's, its three-truth joint union measured (not projected) and at most 1 %, and its power met; the
      backstop passed at every truth; and the config hash equal to this run's. Anything else refuses: nothing
      launches, and 1B returns to Joseph."""
    items = [x for x in str(a.items).split(",") if x]
    if a.clip_rule == "data":
        allowed = pre_gate_items()
        bad = [it for it in items if (a.truth, a.role, it) not in allowed]
        if bad:
            raise Refusal(f"'data' runs only the pre-gate items (S1-0, S1-0b, the capture, the controls); {a.truth} "
                          f"{a.role} {bad[:3]} is a bulk item: it needs 'nature' and the C2 gate (A2.1 S2)")
        return
    if a.role not in BULK_ROLES:
        raise Refusal(f"role {a.role} is not a graded bulk role: it runs under 'data' before the gate, or not at all")
    raw = read_bound_gate(a)
    import fd_1b_c2
    g = json.loads(raw)
    want = {"schema": fd_1b_c2.SCHEMA_GATE, **CLIP_GATE}
    if {k: g.get(k) for k in want} != want:
        raise Refusal(f"the clip gate does not read {want}: nothing launches; 1B returns to Joseph")
    if g.get("reads", {}).get(a.truth) != "option (1)":
        raise Refusal(f"the clip gate's reading at {a.truth} is {g.get('reads', {}).get(a.truth)!r}, not option (1)")
    if g.get("declared_seeds", {}).get(a.truth) != [int(TOY_SEEDS[a.truth][0]), int(TOY_SEEDS[a.truth][-1])]:
        raise Refusal(f"the clip gate was not read on {a.truth}'s declared draws")
    if g.get("code_sha256") != fd_1b_c2.gate_code_digests():
        raise Refusal("the clip gate was read by other code than this run's (fd_1b_c2.gate_code_digests)")
    gi = g.get("inputs", {})
    mine = {"npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_sha256": sa.BKG_SHA256, "pins_sha256": a.expect_pins_sha256,
            "flux_table_sha256": a.expect_flux_table_sha256, "cv_tdw_sha256": getattr(a, "expect_cv_tdw_sha256", None)}
    if a.truth == "plugin":
        mine["push_sha256"] = a.expect_push_sha256
    diff = sorted(k for k, v in mine.items() if gi.get(k) != v)
    if diff:
        raise Refusal(f"the clip gate was read on other inputs than this run's: {diff}")
    if not g.get("calibration_sha256"):
        raise Refusal("the clip gate names no calibration")
    cal = g.get("calibration") or {}
    if cal.get("verdict") != "CALIBRATED" or cal.get("sha256") != g["calibration_sha256"]:
        raise Refusal("the clip gate's calibration is not CALIBRATED, or not the one it names")
    if not cal.get("three_truths_measured") or cal.get("union") is None or cal["union"] > fd_1b_c2.UNION_LIMIT:
        raise Refusal("the clip gate's three-truth noise-only union is not measured, or above 1 %")
    if not cal.get("power_meets"):
        raise Refusal("the clip gate's calibration does not meet the power requirement")
    back = g.get("backstop") or {}
    if a.truth not in back or not all(back.get(t, {}).get("passes") for t in g.get("truths", [])):
        raise Refusal("the clip gate's backstop on the 300 declared draws did not pass")
    ins = dict(mine, push_sha256=a.expect_push_sha256 if a.truth == "plugin" else gi.get("push_sha256"))
    if g.get("config_hash") != fd_1b_c2.config_hash(fd_1b_c2.gate_code_digests(), ins, "nature"):
        raise Refusal("the clip gate's config hash is not this run's")
    a.gate_config_hash = g["config_hash"]                  # recorded in each product's meta, and checked on resume


def resume_matches(target: Path, a) -> None:
    """A product already at the target is skipped (a resume) only if it was made under this step's request: the
    estimator, the clip rule, the CV per-row tdw and the gate's config hash. Any other refuses, rather than leaving
    a product of another rule standing in for this one (the audit's finding on ruling (A); the director's ruling)."""
    meta = json.loads(str(np.load(target, allow_pickle=False)["meta"]))
    want = {"config": a.estimator, "clip_rule": a.clip_rule, "cv_tdw_sha256": getattr(a, "expect_cv_tdw_sha256", None),
            "gate_config_hash": getattr(a, "gate_config_hash", None)}
    diff = sorted(k for k, v in want.items() if meta.get(k) != v)
    if diff:
        raise Refusal(f"{target.name} exists, made under another {diff} than this step's: refusing to skip it")


def run_unfold(a, unfold_fn=None) -> int:
    inv.OPENED.clear()
    if a.role not in ROLES:
        raise Refusal(f"role {a.role!r}")
    if (a.role in ("control", "capture")) != (a.truth == "data"):
        raise Refusal("the control and capture roles run on the data (--truth data), and only they")
    check_clip_gate(a)                        # after the role checks, so each refusal is its own (the receipt's)
    s5e_candidate.install(a.estimator)
    world = _load_world(a)
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for item in a.items.split(","):
        target = a.out / product_name(a.tag, a.truth, a.role, item)
        if target.exists():
            resume_matches(target, a)
            continue
        toys.check_pins(world["pins"], a.bank, a.detector_dir)
        t1 = time.time()
        arrays, extra = run_item(a, world, a.role, item, unfold_fn)
        meta = {"schema": SCHEMA, "truth": a.truth, "role": a.role, "item": item, "config": a.estimator,
                "clip_rule": a.clip_rule,
                "iters": toys.ITERS, "estimator_seed": SEED_CHECK if a.role == "seed" else toys.ESTIMATOR_SEED,
                "threads": a.threads, **extra, "input_npz_sha256": world["npz_sha"], "bkg_dump_sha256": world["bkg_sha"],
                "pins_sha256": a.expect_pins_sha256, "flux_table_sha256": a.expect_flux_table_sha256,
                "push_sha256": a.expect_push_sha256, "alignment": world["alignment"], "code_sha256": code_digests(),
                "gate_pin_blob": getattr(a, "gate_pin_blob", None),
                "cv_tdw_sha256": getattr(a, "expect_cv_tdw_sha256", None),
                "gate_config_hash": getattr(a, "gate_config_hash", None),
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


def clipped_fraction(neg_sum: np.ndarray, total: np.ndarray) -> np.ndarray:
    """|sum of the negative a_D| / sum of a_D per draw (the director's request on cov2d's figures); 0 where the
    total is 0."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(total != 0, np.abs(neg_sum) / np.abs(total), 0.0)


def _spread(x: np.ndarray) -> dict:
    return {"min": float(np.min(x)), "median": float(np.median(x)), "p90": float(np.quantile(x, 0.90)),
            "q95": float(np.quantile(x, 0.95)), "max": float(np.max(x))}


def clip_cells(V: dict, cv: dict, dcols: list[np.ndarray], flat: dict, n_bins: int, U: np.ndarray, k_flat: np.ndarray,
               truth_rows: np.ndarray, reco: np.ndarray, block: int = DRAW_BLOCK) -> dict:
    """cov2d C1's per-cell clipping figures over the declared draws at r = 1 (the director's request), first order, by
    matmul (descriptive), each U-mapped to the reporting cells, as [draws, cells]:
    * ``reco_clip``: |sum of lambda-| (signal w_reco on reco-passing rows, plus the background), and ``reco_plus``,
      the sum of lambda+, both at the rows' reco cells;
    * ``truth_clip``: the truth content of the clipped signal rows (reco-passing, as ``clip_draw`` clips them, with
      w_reco's a_D < 0, and truth-passing), as
      |a_D(w_truth)| at their truth cells, converted to cross section by ``k_flat`` (``xsec_nd``'s per-cell factor
      at the CV's completeness)."""
    S = np.zeros((len(dcols), V["wr"].shape[0]))
    for d, cs in enumerate(dcols):
        S[d, cs] = 1.0
    k = S.sum(axis=1)
    out = {"reco_clip": np.zeros((len(dcols), U.shape[0])), "reco_plus": np.zeros((len(dcols), U.shape[0])),
           "truth_clip": np.zeros((len(dcols), U.shape[0]))}
    fs_, fb, ft = flat["signal"], flat["background"], flat["truth"]
    ms, mb, mt = fs_ >= 0, fb >= 0, (ft >= 0) & truth_rows & np.asarray(reco, bool)
    for d0 in range(0, len(dcols), block):
        Sb, kb = S[d0:d0 + block], k[d0:d0 + block, None] - 1.0
        A_r = Sb @ V["wr"] - kb * cv["wr"][None, :]
        A_t = Sb @ V["wt"] - kb * cv["wt"][None, :]
        A_b = Sb @ V["bkgw"] - kb * cv["bkgw"][None, :]
        for i in range(A_r.shape[0]):
            d = d0 + i
            ar, ab = A_r[i], A_b[i]
            neg = np.bincount(fs_[ms], weights=np.maximum(-ar[ms], 0.0), minlength=n_bins) + \
                np.bincount(fb[mb], weights=np.maximum(-ab[mb], 0.0), minlength=n_bins)
            pos = np.bincount(fs_[ms], weights=np.maximum(ar[ms], 0.0), minlength=n_bins) + \
                np.bincount(fb[mb], weights=np.maximum(ab[mb], 0.0), minlength=n_bins)
            rows = mt & (ar < 0)
            tru = np.bincount(ft[rows], weights=np.abs(A_t[i][rows]), minlength=n_bins) * k_flat
            out["reco_clip"][d], out["reco_plus"][d], out["truth_clip"][d] = U @ neg, U @ pos, U @ tru
    return out


def _per_cell(X: np.ndarray) -> dict:
    return {"median": np.median(X, axis=0).tolist(), "max": X.max(axis=0).tolist()}


def verified_weights(world: dict, a, tag: str) -> tuple[dict, dict]:
    """A universe's weights read ONCE per file through O_NOATIME, the digest taken over the very bytes loaded (the
    audit's question on O4), against the pins file: ``"keep"`` (as loaded, float64) and ``"zero"`` (non-finite zeroed,
    as ``fd_1b_inv.universe_weights(..., "zero")`` gives them)."""
    wdir = universe_dir(tag, a.bank, a.detector_dir)
    keep, zero = {}, {}
    for k in s5p_universe.weight_keys(wdir, tag):
        p = wdir / f"{tag}_{k}.npy"
        with inv.open_noatime(p) as fh:
            raw = fh.read()
        if hashlib.sha256(raw).hexdigest() != world["pins"]["files"][str(p)]["sha256"]:
            raise Refusal(f"{p}: the bytes loaded are not the pinned file")
        keep[k] = np.load(io.BytesIO(raw), allow_pickle=False).astype(np.float64)
        zero[k] = np.nan_to_num(keep[k].copy(), nan=0.0, posinf=0.0, neginf=0.0)
    return keep, zero


def _singles_record(raw: dict, cv: dict, inputs: dict) -> dict:
    """Section 4.2's per-universe counts and the single ratios (descriptive), from the weights as loaded."""
    rec = {}
    for k in ("wt", "wr", "bkgw"):
        u, c = raw[k], cv[k]
        fin = np.isfinite(u)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where((c != 0) & fin, np.abs(u / np.where(c != 0, c, 1.0)), 0.0)
        rec[k] = {"cv_zero_u_nonzero": int(np.sum((c == 0) & fin & (u != 0))), "cv_negative": int(np.sum(c < 0)),
                  "u_negative": int(np.sum(fin & (u < 0))), "u_nonfinite": int(np.sum(~fin)),
                  "max_abs_ratio": float(ratio.max()), "rows_ratio_above_bound": int(np.sum(ratio > N1_BOUND))}
    if "denom_nd" in raw:
        rec["denom_nd_equals_cv"] = bool(np.array_equal(np.asarray(raw["denom_nd"], float),
                                                        np.asarray(inputs["denom_nd"], float)))
    return rec


def receipt(a) -> dict:
    """Before the bulk (amendment 2, a one-node job): section 4.2's counts and the single ratios per universe; N1 on
    every row over the 900 declared draws, exactly in float64 behind the proven screen, with the in-job no-screen
    validation on a seeded sample of rows; section 2b's denominator check in compose's order; N_clip (the declared draw
    with the largest clipped mass at r = 1, descriptive arithmetic); and the cross-term readout (consult (i)). Its
    verdict is STOP on N1 or 2b; anything that stops it from deciding raises (INVALID, rerunnable)."""
    inv.OPENED.clear()
    world = _load_world(a)
    flux_p = via_noatime(toys.flux_probabilities, a.flux_constraint)
    inputs, bkg = world["inputs"], world["bkg"]
    s1 = via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not same_functional(U, s1["U"]):
        raise InvalidReceipt("the definition's functional is not S1's")
    rel_sigma = np.sqrt(np.diag(fs.reported_matrix(s1))) / s1["f"]
    cv = _cv_arrays(inputs, bkg)
    tags = toys.s1_universes()
    col = {t: c for c, t in enumerate(tags)}
    n_s, n_b = cv["wt"].size, cv["bkgw"].size
    print(json.dumps({"receipt": "allocating", "signal_rows": n_s, "background_rows": n_b,
                      "bytes": 8 * len(tags) * (2 * n_s + n_b)}), flush=True)
    V = {"wt": np.empty((len(tags), n_s)), "wr": np.empty((len(tags), n_s)), "bkgw": np.empty((len(tags), n_b))}
    D = np.empty((len(tags),) + cv["denom"].shape)
    singles = {}
    for tag, c in col.items():
        keep, zero = verified_weights(world, a, tag)
        singles[tag] = _singles_record(keep, cv, inputs)
        single, _ = _single(inputs, bkg, world["bank_cv"], tag, zero, world["flux"])
        for k in V:
            V[k][c] = single[k]
        D[c] = single["denom"]
    if world.get("tdw_cv") is None:
        raise InvalidReceipt("the receipt's composites need --cv-tdw, so no composite mixes binnings (A2.1 e2)")
    d32 = np.asarray(s5p_universe.denominator(world["bank_cv"], world["tdw_cv"], inputs["edges"]), float)
    for tag, c in col.items():                         # (e2): a detector universe's denominator is the CV's (check D)
        if tag.rpartition("_")[0] in sa.DETECTOR_BANDS:
            if not np.array_equal(D[c], cv["denom"]):
                raise InvalidReceipt(f"{tag}: its denominator is not the CV's (A2.1 S3 (d1)'s check D)")
            D[c] = d32
    cv = dict(cv, denom=d32)
    labels = [(t, sd) for t in TRUTHS for sd in TOY_SEEDS[t]]
    dcols = draw_columns(declared_draws(flux_p, world["groups"]), col)
    reco = np.asarray(inputs["pass_reco"], bool)
    rng = np.random.default_rng(VALIDATE_SEED)
    exact, validation = {}, {}
    for k in V:
        Lk = screen_floor(V[k], col)
        if not screen_floor_check(V[k], col, Lk):
            raise InvalidReceipt(f"{k}: the screen's floor differs from its independent recomputation")
        n = V[k].shape[1]
        sample = np.sort(rng.choice(n, size=max(1, math.ceil(VALIDATE_FRACTION * n)), replace=False))
        res = exact_n1(V[k], cv[k], dcols, Lk, sample, reco=reco if k == "wr" else None)
        bad = validate_screen(res, no_screen_n1(V[k], cv[k], dcols, sample), sample)
        if bad:
            raise InvalidReceipt(f"{k}: the screened N1 differs from the no-screen check on the sample: {bad[:3]}")
        validation[k] = {"sample_rows": int(sample.size), "pairs_above_in_sample": len(res["sample_above"]),
                         "agrees": True}
        exact[k] = {key: res[key] for key in ("rows", "pairs_past_screen", "near_bound_recomputed", "pairs_above",
                                              "rows_above", "max_evaluated")}
        exact[k]["negative_composite"] = {
            "rows_in_some_draw": res["negative_rows_in_some_draw"],
            "pairs": int(res["negative_composite_rows"].sum()),
            "draws_with_any": int(np.sum(res["negative_composite_rows"] > 0)),
            "rows_max_per_draw": int(res["negative_composite_rows"].max()),
            "clipped_fraction_per_draw": _spread(clipped_fraction(res["negative_composite_sum"], res["composite_sum"])),
            "counts_over": "all rows with a_CV > 0", "sums_over": "reco-passing rows" if k == "wr" else "all rows",
            "arithmetic": "matmul, descriptive"}
        exact[k]["_neg_sum"], exact[k]["_sum"], exact[k]["_any"] = (res["negative_composite_sum"], res["composite_sum"],
                                                                     res["negative_any"])
    nonpos = {k: (np.min(V[k], axis=0) <= 0) & (cv[k] > 0) for k in V}
    source = {k: {"rows_with_a_universe_le_0": int(nonpos[k].sum()),
                  "negative_in_some_draw_with_a_universe_le_0": int(np.sum(exact[k]["_any"] & nonpos[k])),
                  "negative_in_some_draw_composite_only": int(np.sum(exact[k]["_any"] & ~nonpos[k])),
                  "rows": int(V[k].shape[1])} for k in V}
    neg_total = np.abs(exact["wr"]["_neg_sum"]) + np.abs(exact["bkgw"]["_neg_sum"])
    signal_background = _spread(clipped_fraction(exact["wr"]["_neg_sum"] + exact["bkgw"]["_neg_sum"],
                                                 exact["wr"]["_sum"] + exact["bkgw"]["_sum"]))
    for k in exact:
        exact[k].pop("_neg_sum"), exact[k].pop("_sum"), exact[k].pop("_any")
    d_clip = int(np.argmax(neg_total))
    denom = denominator_check(D, cv["denom"], dcols)
    n_bins = int(np.prod([np.asarray(e).size - 1 for e in inputs["edges"]]))
    flat_s = np.where(reco, flat_cells(np.asarray(inputs["MCreco"], float), inputs["edges"]), -1)
    flat_b = flat_cells(np.asarray(bkg["bkg_reco"], float), inputs["edges"])
    Hp_s, Ha_s, H0_s = crossterm(V["wr"], cv["wr"], dcols, flat_s, n_bins, U)
    Hp_b, Ha_b, H0_b = crossterm(V["bkgw"], cv["bkgw"], dcols, flat_b, n_bins, U)
    flat_t = np.where(np.asarray(inputs["pass_truth"], bool), flat_cells(np.asarray(inputs["MCgen"], float),
                                                                        inputs["edges"]), -1)
    Hp_t, Ha_t, H0_t = crossterm(V["wt"], cv["wt"], dcols, flat_t, n_bins, U)
    pt = np.asarray(inputs["pass_truth"], bool)
    ofin, _ = np.histogramdd(np.asarray(inputs["MCgen"], float)[pt], bins=inputs["edges"], weights=cv["wt"][pt])
    dn = np.asarray(inputs["denom_nd"], float)
    comp = np.where(dn > 0, ofin / np.where(dn > 0, dn, 1.0), 0.0)
    k_flat, _ = xsec_nd.extract_cross_section_nd(np.ones_like(comp), comp, inputs["flux"], float(inputs["data_pot"]),
                                                 float(inputs["n_nucleons"]), inputs["edges"])
    cc = clip_cells(V, cv, dcols, {"signal": flat_s, "background": flat_b, "truth": flat_t}, n_bins, U,
                    np.asarray(k_flat, float).ravel(order="C"), pt, reco)
    sig_rep = np.sqrt(np.diag(fs.reported_matrix(s1)))
    sig_stat = np.sqrt(np.diag(s1["blocks"]["stat"]))
    with np.errstate(divide="ignore", invalid="ignore"):
        reco_z = np.where(cc["reco_plus"] > 0, cc["reco_clip"] / np.sqrt(cc["reco_plus"]), 0.0)
    c1 = {"source_split": source,
          "clipped_fraction_per_draw": {"signal": exact["wr"]["negative_composite"]["clipped_fraction_per_draw"],
                                        "background": exact["bkgw"]["negative_composite"]["clipped_fraction_per_draw"]},
          "clipped_rows_truth_xsec_over_sigma_c": _per_cell(cc["truth_clip"] / sig_rep[None, :]),
          "clipped_rows_truth_xsec_over_sigma_stat": _per_cell(cc["truth_clip"] / sig_stat[None, :]),
          "reco_cell_clipped_over_sqrt_plus": _per_cell(reco_z),
          "basis": "first order at r = 1 over the 900 declared draws; matmul, descriptive; U-mapped (reco a proxy)"}
    reasons = [f"N1: {k} {v['rows_above']} rows above" for k, v in exact.items() if v["rows_above"]]
    if denom["n1"]["pairs_above"]:
        reasons.append(f"N1: denom {denom['n1']['pairs_above']} (cell, draw) pairs above")
    if denom["draws_with_nonpositive_cells"]:
        reasons.append(f"2b: {len(denom['draws_with_nonpositive_cells'])} draws with a non-positive denominator cell")
    return {"schema": SCHEMA, "step": "receipt", "n1_bound": N1_BOUND, "universes": singles,
            "max_abs_ratio": {k: max(r[k]["max_abs_ratio"] for r in singles.values()) for k in ("wt", "wr", "bkgw")},
            "negative_weight_universes": sorted(t for t, r in singles.items() if any(r[k]["u_negative"] for k in
                                                                                    ("wt", "wr", "bkgw"))),
            "exact": exact, "clipped_fraction_signal_plus_background_per_draw": signal_background,
            "validation": validation, "denominator": denom,
            "n_clip": {"draw_index": d_clip, "truth": labels[d_clip][0], "seed": labels[d_clip][1],
                       "clipped_mass_at_r1": float(neg_total[d_clip]), "arithmetic": "matmul, descriptive",
                       "role": "the reference case of the clipping offset (consult (ii)); not claimed the largest"},
            "crossterm": {"reco_proxy_U_mapped": cross_z(Hp_s + Hp_b, Ha_s + Ha_b, H0_s + H0_b, rel_sigma),
                          "truth_weight_histogram": cross_z(Hp_t, Ha_t, H0_t, rel_sigma),
                          "units": "[(H_product - H_first_order) / H_CV]_c / (sigma_c / x_c), sigma_c S1's reported"},
            "clipping_c1": c1,
            "verdict": "STOP" if reasons else "PASS", "stop_reasons": reasons, "atime": inv.atime_check()}


def pilot_b(plugin: bool, clip_seed: int) -> list[tuple[str, str, str]]:
    """S1-0b (the director's ruling on cov2d's figures): after S1-0's readout and before the bulk, the clipmean at every
    truth and the central values S1-0 lacks (AR23's, and the plug-in's), as (truth, role, item)."""
    truths = ["g18", "ar23"] + (["plugin"] if plugin else [])
    return [(t, "clipmean", str(clip_seed)) for t in truths] + [(t, "central", "T") for t in truths if t != "g18"]


def pilot_walls(unfolds: Path, tag: str, plugin: bool) -> dict:
    names = []
    for role, item in PILOT[plugin]:
        truth = "data" if role in ("control", "capture") else item.split(":")[0]
        it = item.split(":", 1)[1] if ":" in item else ("" if role == "central" else item)
        names.append(product_name(tag, truth, role, it if role != "central" else "T"))
    return walls_of(unfolds, names)


def walls_of(unfolds: Path, names: list[str]) -> dict:
    """The re-price trigger over named products: every one present, each unfold within the unit and the RSS limit."""
    rows = []
    for name in names:
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


def clipcheck(a) -> dict:
    """The up-front clipping offset (the director's ruling), after S1-0b and before the bulk: per truth,
    o_c = U (x_clipmean - x_central)_c / sigma_c with sigma_c S1's REPORTED sigma at the data (the committed data
    product's), a proxy for C_T, which only the bulk makes (the final readout recomputes o_c with C_T). If any cell at
    any truth has |o_c| >= CLIP_DELTA_STAR, the verdict is TO_JOSEPH: the case goes to Joseph before any bulk."""
    if a.clip_rule != "data":
        raise Refusal(NATURE_UNRULED)
    s1 = via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not same_functional(U, s1["U"]):
        raise Refusal("the definition's functional is not S1's")
    sigma = np.sqrt(np.diag(fs.reported_matrix(s1)))
    raw = a.receipt.read_bytes()
    if hashlib.sha256(raw).hexdigest() != a.expect_receipt_sha256:
        raise Refusal("the receipt's digest differs from the declared one")
    rc = json.loads(raw)
    if rc.get("verdict") != "PASS":
        raise Refusal(f"the receipt's verdict is {rc.get('verdict')!r}, not PASS")
    out, hit = {}, []
    for truth in a.truths.split(","):
        refuse_partials(a.unfolds, a.tag, truth)
        refuse_mixed_estimator(a.unfolds, a.tag, truth, a.estimator, a.clip_rule)
        cm = sorted(a.unfolds.glob(f"{a.tag}_{truth}_clipmean_*.npz"))
        if len(cm) != 1:
            raise Refusal(f"{truth}: {len(cm)} clipmean products, not exactly one")
        zc = np.load(cm[0], allow_pickle=False)
        seed = int(json.loads(str(zc["meta"]))["n_clip_seed"])
        if seed != int(rc["n_clip"]["seed"]):
            raise Refusal(f"{truth}: the clipmean's N_clip seed {seed} is not the receipt's {rc['n_clip']['seed']}")
        xc = U @ np.asarray(np.load(a.unfolds / product_name(a.tag, truth, "central", "T"))["xsec_flat"], float)
        o = (U @ np.asarray(zc["xsec_flat"], float) - xc) / sigma
        cells = [f"R{c:02d}" for c in clip_flags(o)]
        hit += [f"{truth}:{c}" for c in cells]
        out[truth] = {"n_clip_seed": int(json.loads(str(zc["meta"]))["n_clip_seed"]),
                      "offset_over_reported_sigma": o.tolist(), "cells_at_or_above_delta_star": cells,
                      "n_clip_clip": json.loads(str(zc["meta"]))["clip"]}
    return {"schema": SCHEMA, "step": "clipcheck", "delta_star": CLIP_DELTA_STAR, "clip_rule": a.clip_rule,
            "receipt_sha256": a.expect_receipt_sha256, "receipt_clipping_c1": rc["clipping_c1"],
            "sigma": "S1's reported (fd_data_product C_total_plus_C_resp), a proxy for C_T", "truths": out,
            "verdict": "TO_JOSEPH" if hit else "PROCEED", "cells": hit}


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


def grade(E: np.ndarray, C: np.ndarray, null: dict) -> dict:
    """Section 5.1-5.2 for one matrix: counts, the flags against the null, the chi2 statistics, pulls, attribution."""
    thr = fn.thresholds(null, E.shape[0])
    sigma = np.sqrt(np.diag(C))
    inside = np.sum(np.abs(E) <= sigma, axis=0)
    chi2, ndf = fn.chi2_nonnull(E, C)
    if ndf == C.shape[0]:
        L = np.linalg.cholesky(C)
        ref = np.sum(np.linalg.solve(L, E.T) ** 2, axis=0)
        if np.max(np.abs(chi2 / ref - 1)) > 1e-9:
            raise Refusal("the non-null chi2 and the Cholesky chi2 differ")
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


def refuse_mixed_estimator(unfolds: Path, tag: str, truth: str, estimator: str, clip_rule: str) -> None:
    """Every product at T was unfolded by the declared estimator under the declared clipping rule (both named inputs
    since amendment 2, so a change of either is a re-pin with a record): a product with another, or none, refuses."""
    for p in sorted(unfolds.glob(f"{tag}_{truth}_*.npz")):
        if ".partial-" in p.name:
            continue
        meta = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
        if meta.get("config") != estimator:
            raise Refusal(f"{p.name}: estimator {meta.get('config')!r}, not the declared {estimator!r}")
        if meta.get("clip_rule") != clip_rule:
            raise Refusal(f"{p.name}: clip rule {meta.get('clip_rule')!r}, not the declared {clip_rule!r}")


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
    refuse_mixed_estimator(a.unfolds, a.tag, a.truth, a.estimator, a.clip_rule)
    s1 = via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not same_functional(U, s1["U"]):
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


def clip_flags(o: np.ndarray) -> list[int]:
    """The cells whose clipping offset reaches delta* (section 5's reading, and clipcheck's rule)."""
    return [c for c in range(o.size) if abs(o[c]) >= CLIP_DELTA_STAR]


def clipping_readout(unfolds: Path, tag: str, truth: str, U: np.ndarray, rm: dict, cell_flag: list[bool],
                     clip_rule: str = "data", nature: dict | None = None) -> dict:
    """Consult item (ii) and decision section 2a, descriptive beside the grading: the clipping offset
    o_c = U (x_clipmean - x_central)_c / sigma_c (sigma_c from C_T); the toys' clipped fractions; the toys' clipped
    mass per reporting cell (reco and truth) relative to N_clip's; and the reading fixed before any number was read:
    a cell flagged at T with |o_c| >= ``CLIP_DELTA_STAR`` is read "the flag may be the clipping artefact". The verdict
    and clause F stand either way. The offset is defined for the "data" rule (the audit's C4 on #717); under
    "nature" the section is clipping_readout_nature's (the director's ruling (iii), extended)."""
    if clip_rule == "nature":
        return clipping_readout_nature(unfolds, tag, truth, U, rm, **(nature or {}))
    if clip_rule != "data":
        raise Refusal(f"clip rule {clip_rule!r} is not one of {CLIP_RULES}")
    refuse_partials(unfolds, tag, truth)
    cm = sorted(unfolds.glob(f"{tag}_{truth}_clipmean_*.npz"))
    if len(cm) != 1:
        raise Refusal(f"{truth}: {len(cm)} clipmean products, not exactly one")
    zc = np.load(cm[0], allow_pickle=False)
    sigma = np.sqrt(np.diag(rm["C_T"]))
    o = (U @ np.asarray(zc["xsec_flat"], float) - rm["X_T"]) / sigma
    ref_r, ref_t = U @ np.asarray(zc["clip_reco_flat"], float), U @ np.asarray(zc["clip_truth_flat"], float)
    frac = {"signal": [], "background": []}
    reco, tru = [], []
    for p in toy_paths(unfolds, tag, truth):
        z = np.load(p, allow_pickle=False)
        rec = json.loads(str(z["meta"]))["clip"]
        for comp in frac:
            tot = rec[comp]["sum_lambda"]
            frac[comp].append(abs(rec[comp]["sum_negative"]) / tot if tot else 0.0)
        reco.append(U @ np.asarray(z["clip_reco_flat"], float))
        tru.append(U @ np.asarray(z["clip_truth_flat"], float))
    reco, tru = np.array(reco), np.array(tru)

    def rel(X, ref):                       # NaN in the cells N_clip clips nothing in, by design
        if not np.any(ref > 0):
            return {"median": None, "max": None}
        with np.errstate(divide="ignore", invalid="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            q = np.where(ref[None, :] > 0, X / ref[None, :], np.nan)
            return {"median": np.nanmedian(q, axis=0).tolist(), "max": np.nanmax(q, axis=0).tolist()}
    return {"n_clip_seed": int(json.loads(str(zc["meta"]))["n_clip_seed"]), "offset_over_sigma": o.tolist(),
            "delta_star": CLIP_DELTA_STAR,
            "flagged_cells_the_clipping_may_explain": [f"R{c:02d}" for c in clip_flags(o) if cell_flag[c]],
            "clipped_fraction": {k: {"min": float(min(v)), "median": float(np.median(v)), "max": float(max(v))}
                                 for k, v in frac.items()},
            "toys_clipped_mass_over_n_clip": {"reco": rel(reco, ref_r), "truth": rel(tru, ref_t)},
            "n_clip_clipped_mass": {"reco": ref_r.tolist(), "truth": ref_t.tolist()}}


def clipping_readout_nature(unfolds: Path, tag: str, truth: str, U: np.ndarray, rm: dict, data_unfolds: Path | None = None,
                            gate: dict | None = None, gate_sha256: str | None = None, estimator: str | None = None) -> dict:
    """The clipping section under "nature" (the director's ruling (iii), extended, 2026-11-04): descriptive, for the
    note, and changing no graded quantity. Three parts, each labelled with its rule:
    (a) the graded toys' own "nature" clip facts: per component the clipped fraction over toys (meta["clip"]), and
        per reporting cell the median and max over toys of U applied to the pseudo-data's, the truth's and the
        denominator's clipped mass (clip_draw's arrays);
    (b) c2check's residual R (option (1)) and clipped-truth mean shift per cell at N, from the bound gate record;
    (c) S1-0b's "data" offset o_c = U (x_clipmean - x_central)_c / sigma_c, both products from ``data_unfolds``
        (every product there must be "data", by this estimator), sigma_c from this grading's C_T: the data rule's
        offset, for reference; not the graded rule."""
    if data_unfolds is None or gate is None:
        raise Refusal("under 'nature' the clipping section needs --data-unfolds (S1-0b's 'data' products) and the "
                      "bound gate record (--clip-gate)")
    refuse_partials(unfolds, tag, truth)
    sigma = np.sqrt(np.diag(rm["C_T"]))
    totals = {"signal": "sum_lambda", "background": "sum_lambda", "denominator": "sum_rows", "truth": "sum_truth"}
    frac = {k: [] for k in totals}
    cells = {k: [] for k in ("clip_reco_flat",) + NATURE_CLIP_ARRAYS}
    for p in toy_paths(unfolds, tag, truth):
        z = np.load(p, allow_pickle=False)
        rec = json.loads(str(z["meta"]))["clip"]
        if rec.get("rule") != "nature":
            raise Refusal(f"{p.name}: clip rule {rec.get('rule')!r}, not 'nature'")
        for comp, key in totals.items():
            tot = rec[comp][key]
            frac[comp].append(abs(rec[comp]["sum_negative"]) / tot if tot else 0.0)
        for k in cells:
            cells[k].append(U @ np.asarray(z[k], float))
    b = gate["record"]["b"][truth]
    refuse_partials(data_unfolds, tag, truth)
    refuse_mixed_estimator(data_unfolds, tag, truth, estimator, "data")
    cm = sorted(data_unfolds.glob(f"{tag}_{truth}_clipmean_*.npz"))
    if len(cm) != 1:
        raise Refusal(f"{truth}: {len(cm)} clipmean products in --data-unfolds, not exactly one")
    zc = np.load(cm[0], allow_pickle=False)
    xc = U @ np.asarray(np.load(data_unfolds / product_name(tag, truth, "central", "T"), allow_pickle=False)["xsec_flat"],
                        float)
    o = (U @ np.asarray(zc["xsec_flat"], float) - xc) / sigma
    return {"rule": "nature",
            "a_nature_toys": {"label": "the graded rule's own clipping, over this truth's toys",
                              "clipped_fraction": {k: {"min": float(min(v)), "median": float(np.median(v)),
                                                       "max": float(max(v))} for k, v in frac.items()},
                              "clipped_mass_per_cell": {k: {"median": np.median(v, axis=0).tolist(),
                                                            "max": np.max(v, axis=0).tolist()} for k, v in cells.items()}},
            "b_c2check_at_n": {"label": "c2check's measurement of the 'nature' rule at N (the bound gate record)",
                               "gate_sha256": gate_sha256, "residual_option_1_sigma_Q": b["option_1"]["sigma_Q"],
                               "clipped_truth_mean_shift_sigma_c": b["clipped_truth_mean_shift_sigma_c"]["per_cell"]},
            "c_data_offset": {"label": "the data rule's offset, for reference; not the graded rule",
                              "n_clip_seed": int(json.loads(str(zc["meta"]))["n_clip_seed"]),
                              "offset_over_sigma": o.tolist(), "delta_star": CLIP_DELTA_STAR,
                              "sigma": "this grading's C_T"}}


def readout_nature_inputs(a) -> dict | None:
    """Under 'nature', the clipping section's inputs: S1-0b's 'data' directory, and the gate record binding 3 pins in
    GATE_PIN, read by its digest. None under 'data'."""
    if a.clip_rule != "nature":
        return None
    raw = read_bound_gate(a)
    if a.data_unfolds is not None and a.data_unfolds.resolve() == a.unfolds.resolve():
        raise Refusal("--data-unfolds is the graded directory: S1-0b's 'data' products live apart (ruling (A))")
    return {"data_unfolds": a.data_unfolds, "gate": json.loads(raw), "gate_sha256": a.expect_clip_gate_sha256,
            "estimator": a.estimator}


def readout(a) -> dict:
    """Section 5's grading and section 7's readouts at T. The null is the committed one, pinned by digest; it must
    have been made from these very products."""
    if inv.sha256_noatime(a.null) != a.expect_null_sha256:
        raise Refusal("the null's digest differs from the declared one")
    nl = json.loads(a.null.read_text())
    if nl["products_sha256"] != products_digest(a.unfolds, a.tag, a.truth, BLOCK_ROLES):
        raise Refusal("the null was not made from these products")
    refuse_mixed_estimator(a.unfolds, a.tag, a.truth, a.estimator, a.clip_rule)
    s1 = via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not same_functional(U, s1["U"]):
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
            "clipping": clipping_readout(a.unfolds, a.tag, a.truth, U, rm, main["cell_flag"], a.clip_rule,
                                         readout_nature_inputs(a)),
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
    p.add_argument("--estimator", choices=tuple(s5e_candidate.CANDIDATES), required=True)
    p.add_argument("--clip-rule", choices=CLIP_RULES, required=True)
    p.add_argument("--cv-tdw", type=Path, default=None)
    p.add_argument("--expect-cv-tdw-sha256", default=None)
    p.add_argument("--clip-gate", type=Path, default=None)
    p.add_argument("--expect-clip-gate-sha256", default=None)
    p.add_argument("--tag", default="fd1b_mc")
    p = sub.add_parser("stage-flux")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("receipt")
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "staged", "definition", "out",
              "cv-tdw"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--expect-flux-table-sha256", required=True)
    p.add_argument("--expect-cv-tdw-sha256", required=True)
    p = sub.add_parser("n1")
    p.add_argument("--truth", choices=tuple(TRUTHS), required=True)
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--tag", default="fd1b_mc")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("walls")
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--plugin", choices=("yes", "no"), required=True)
    p.add_argument("--stage", choices=("s1-0", "s1-0b"), default="s1-0")
    p.add_argument("--clip-seed", type=int, default=None)
    p.add_argument("--tag", default="fd1b_mc")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("clipcheck")
    p.add_argument("--truths", required=True)
    p.add_argument("--estimator", choices=tuple(s5e_candidate.CANDIDATES), required=True)
    p.add_argument("--clip-rule", choices=CLIP_RULES, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--expect-receipt-sha256", required=True)
    for k in ("unfolds", "staged", "definition", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--tag", default="fd1b_mc")
    for name in ("null", "readout"):
        p = sub.add_parser(name)
        p.add_argument("--truth", choices=tuple(TRUTHS), required=True)
        for k in ("staged", "unfolds", "definition", "cmodel-json", "flux-constraint", "out"):
            p.add_argument(f"--{k}", type=Path, required=True)
        p.add_argument("--tag", default="fd1b_mc")
        p.add_argument("--estimator", choices=tuple(s5e_candidate.CANDIDATES), required=True)
        p.add_argument("--clip-rule", choices=CLIP_RULES, required=True)
        if name == "readout":
            p.add_argument("--null", type=Path, required=True)
            p.add_argument("--expect-null-sha256", required=True)
            p.add_argument("--i2", type=Path, required=True)
            p.add_argument("--data-unfolds", type=Path, default=None)          # under 'nature': S1-0b's products
            p.add_argument("--clip-gate", type=Path, default=None)
            p.add_argument("--expect-clip-gate-sha256", default=None)
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
            if a.stage == "s1-0b" and a.clip_seed is None:
                raise Refusal("S1-0b's walls need --clip-seed")
            res = (pilot_walls(a.unfolds, a.tag, a.plugin == "yes") if a.stage == "s1-0" else
                   walls_of(a.unfolds, [product_name(a.tag, t, r, i) for t, r, i in pilot_b(a.plugin == "yes", a.clip_seed)]))
            a.out.write_text(json.dumps(res, indent=1) + "\n")
            print(json.dumps({"verdict": res["verdict"], "max_seconds_unfold": res.get("max_seconds_unfold")}))
            return 0 if res["verdict"] == "PASS" else 1
        res = {"receipt": receipt, "n1": n1_step, "null": null_step, "readout": readout, "clipcheck": clipcheck}[a.cmd](a)
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

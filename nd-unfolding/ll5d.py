#!/usr/bin/env python3
"""LL5D amendment A1a (LL5D-DECLARATION.md at 1acdee66, sections 3.4, 5 and 12): the like-for-like 5D coverage
test's calibration and pre-bulk gate, read without (``minus2``, primary) and with (``all``) GEANT_Neutron and
GEANT_Proton.

Subcommands (A1a, binding 2; the unfold, walls, clipcheck, null and readout are A1b, binding 3):

* ``calib``: the large-sample gate's null calibration (Joseph's 11-03 and 11-04 rules, the director's mapping onto
  four evaluations: {G18, AR23} x {minus2, all}). Replicate sets of N draws per truth from the streams
  [CAL_SEED[truth], set, CAL_SALT]; each set read in both readings from the same draws (``drop2``); the per-cell
  variance ratios of the unclipped first-order law; the law control and the linearisation (11-04 item 4); the
  thresholds s at which the joint noise-only STOP over the four evaluations, measured per replicate on the paired
  null, is at most 1 %; the power against a uniform 8 % deflation (11-04 item 3); and the 300-draw null SDs per
  cell for the backstop, from the first 300 draws of each set.
* ``gate``: one truth per job. The denominator controls D1-D3, r_T > 0, the receipt (N1 and T <= 0 STOPs, exact
  float64 in compose's order, per row, with section 3.4's denominator), then per reading C2's record on the
  declared 300 draws and on the gate sample of N, read by the large-sample gate at the calibration's thresholds,
  the backstop on the 300. The cross terms (descriptive) are made in the receipt's per-row pass, which already walks
  every declared draw's universes: A2.1's vectorized crossterm builds four arrays the size of V (about 180 GB on the
  real bank) and would not fit beside the gate's 269 GiB.
* ``gate-merge``: the two per-truth records into the one gate record. PASS needs PASS at every truth.

Imported unchanged: fd_1b_c2's building blocks (selection, band_reference, composite_sums, draw_flux, xt_packed,
xt_flat, set_ratios, rates, null_stats, stops_at, power_at, control, linearisation, calibration_verdict_n, c2_terms,
c2_truth, c2_block, c2_vi, reading_1b, gate_n, backstop), fd_1b_mc's world loader and per-universe arrays
(_load_world, _single, truth_ratio, truth_weight, draw_universes, via_noatime), fd_1b_toys' draws, s5p_universe's
denominator. fd_1b_c2.py is a verbatim copy of 342c0ce5's (branch decl/1b-staged-a2-1-20261103, blob 0cb72761,
sha256 522d7edd); its drivers (prepare, fine_sums, c2_inputs, calibrate_main, c2check_main) are not called, since
they need A2.1's fd_1b_mc, which main does not carry.

The named departures from the verbatim gate code (declaration section 12, the director's rulings of 2026-11-08):
1. ``layout_minus2`` (S1's layout less the two bands and their 4 dump universes);
2. ``drop2`` (an ``all`` draw less those universes, on the same stream);
3. ``restrict`` (the ``minus2`` rows of the one ``all`` pass's small per-universe sums, selected, not recomputed);
4. this module's own input builders (``fine_sums``, ``prepare``, ``c2_inputs``) on the ``all`` and ``minus2``
   layouts, with tdw_ref (the bank's GEANT_Neutron_0 tdw) in place of A2.1's --cv-tdw array;
5. ``threshold_rule``: the 1 % over the four evaluations, measured jointly per replicate.
The gate's per-row arrays V (about 46 GB each on the real bank) are never copied for ``minus2``: its selection
matrix is written over the ``all`` column map with the removed universes' columns 0, which is the selected form's
composite (the zero columns add nothing); a test holds the two equal (the audit's RSS low on #936).

MEASURES: a calibration's null rates and thresholds; a gate's receipt and per-evaluation reading. CANNOT AUTHORIZE: a
threshold change, an unfold, a coverage verdict, or any repair after a STOP (Joseph decides at each STOP, #939).
"""
from __future__ import annotations

import argparse
import hashlib
import io
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
import fd_1b_c2 as c2  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA_CAL = "ll5d-calibration/1"
SCHEMA_GATE = "ll5d-gate/1"
SCHEMA_MERGED = "ll5d-gate-merged/1"
TRUTHS = ("g18", "ar23")                      # fd_1b_mc.TRUTHS keys: G18_10a_02_11b and AR23_20i_00_000 (section 3.1)
READINGS = ("minus2", "all")                  # primary first (decision 2026-11-08 item 1)
REMOVED = ("GEANT_Neutron", "GEANT_Proton")
EVALUATIONS = tuple(f"{t}/{r}" for t in TRUTHS for r in READINGS)

# Seeds (section 3.6)
TOY_SEEDS = {"g18": range(4_751_000, 4_751_300), "ar23": range(4_761_000, 4_761_300)}
STAT_SEED = {"g18": 4_770_100, "ar23": 4_770_200}
NULL_SEED = {"g18/minus2": 4_770_310, "g18/all": 4_770_320, "ar23/minus2": 4_770_410, "ar23/all": 4_770_420}
CAL_SEED = {"g18": 4_770_500, "ar23": 4_770_600}
CAL_SALT = c2.CAL_SALT                        # non-zero: a three-word stream equals no two-word one (calibration_draws)
CAL_SETS = c2.CAL_SETS                        # 10,000 replicate sets per truth, as A2.1's
GATE_N = 3_000                                # 11-04 item 1: "about 3,000", fixed here (section 3.6)
GATE_N_MAX = 9_000                            # section 3.6; above it the two truths' gate samples would overlap
DRAW_BLOCK = c2.DRAW_BLOCK                    # 20 draws per block
BACKSTOP_N = 300

N1_BOUND = 10.0                               # amendment 2's bound, carried (section 5.1)
TDW_REF_TAG = "GEANT_Neutron_0"               # section 3.4
GEANT_BANK_TAGS = tuple(f"{b}_{i}" for b in ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton") for i in (0, 1))
TDW_REF_SHA256 = "c0ae3c18b7dde9261509e4b6f1007d7578f028e9bee4fc3619291565b601524b"   # sf1 manifest, all six
DENOM_TOTAL_TOL, DENOM_CELL_TOL = 1e-9, 1e-3  # S1's (s1_controls.py:14-18), D2
PROJECTION_SHARE = 0.9                        # the in-job projection line: 0.9 x --time (section 9)
RECEIPT_PROBE = 20                            # natures timed before the receipt's own projection
THREAD_VARS = c2.THREAD_VARS
FD_1B_C2_SOURCE = {"commit": "342c0ce50cae80aa819ef931d7bdb7632279b6d9", "branch": "decl/1b-staged-a2-1-20261103",
                   "blob": "0cb727612a6658f27fe14e51f8120450da581a15",
                   "sha256": "522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f"}
RC = {"PASS": 0, "CALIBRATED": 0, "STOP": 3, "TO_DIRECTOR": 3, "REPRICE": 4, "INVALID": 5}
ATIME_RC = 8


class Refusal(RuntimeError):
    """An input or invariant is not what the step is defined on: INVALID, reported unrepaired."""


class Reprice(RuntimeError):
    """The in-job projection passes 0.9 x --time: a REPRICE to the director, not a STOP."""


# --------------------------------------------------------------------------------------------- layouts and draws


def layout(reading: str) -> tuple[tuple[str, ...], dict, list[str]]:
    """(order, bands, tags) of a reading. ``all`` is fd_1b_c2.layout_1b() unchanged; ``minus2`` (departure 1) is the
    same with GEANT_Neutron and GEANT_Proton removed, and their 4 universes off the tags, every other entry in its
    order."""
    order, bands, tags = c2.layout_1b()
    if reading == "all":
        return order, bands, tags
    if reading != "minus2":
        raise Refusal(f"reading {reading!r}")
    return (tuple(b for b in order if b not in REMOVED), {b: n for b, n in bands.items() if b not in REMOVED},
            [t for t in tags if t.rpartition("_")[0] not in REMOVED])


def layout_minus2() -> tuple[tuple[str, ...], dict, list[str]]:
    return layout("minus2")


def drop2(tags: list[str]) -> list[str]:
    """Departure 2: an ``all`` draw's universes less GEANT_Neutron's and GEANT_Proton's, in the draw's order."""
    return [t for t in tags if t.rpartition("_")[0] not in REMOVED]


def reading_draws(draws: list[list[str]], reading: str) -> list[list[str]]:
    return [list(d) for d in draws] if reading == "all" else [drop2(d) for d in draws]


def selection(draws_all: list[list[str]], reading: str, col: dict[str, int]) -> np.ndarray:
    """The unchanged fd_1b_c2.selection on the reading's draws and bands, over the column map ``col``. With the
    ``all`` column map and ``minus2``, the removed universes' columns are 0 (the no-copy form, see the module doc)."""
    _, bands, _ = layout(reading)
    return c2.selection(reading_draws(draws_all, reading), col, bands)


def declared_draws(truth: str, flux_p: np.ndarray, groups: dict) -> list[list[str]]:
    return [mc.draw_universes(toys.draw_for_seed(int(s), flux_p, groups)) for s in TOY_SEEDS[truth]]


def gate_seeds(truth: str, n: int) -> list[int]:
    """The gate sample's seeds (section 3.6): the declared toys' 300 and then the next n - 300, contiguous, so the first
    300 are the declared draws bit for bit."""
    check_n(n)
    first = TOY_SEEDS[truth][0]
    return list(range(first, first + n))


def check_n(n: int) -> None:
    if not (BACKSTOP_N <= n <= GATE_N_MAX and n % DRAW_BLOCK == 0):
        raise Refusal(f"N = {n}: it must lie in {BACKSTOP_N}..{GATE_N_MAX} in whole blocks of {DRAW_BLOCK}")


def calibration_draws(truth: str, s: int, flux_p: np.ndarray, groups: dict, n: int) -> list[list[str]]:
    """Replicate set s of ``truth``: n ``all`` draws by toys.draw's law from [CAL_SEED[truth], s, CAL_SALT] (A2.1's
    form at LL5D's seeds). Both readings read the same set."""
    if CAL_SALT == 0:
        raise Refusal("CAL_SALT must be non-zero")
    rng = np.random.default_rng([CAL_SEED[truth], s, CAL_SALT])
    return [mc.draw_universes(toys.draw(rng, flux_p, groups)) for _ in range(n)]


# ------------------------------------------------------------------------------------- A2.1's small row helpers
# flat_cells, td_cells, same_functional, n1_ratio, clipped_fraction and cross_z are A2.1's (fd_1b_mc at 342c0ce5),
# which main's fd_1b_mc does not carry; each is held equal to that copy by a test.


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


def td_cells(bank_cv, edges) -> np.ndarray:
    """The truth-denominator rows' 5D cells (C order, -1 outside), as s5p_universe.denominator bins them."""
    coords = np.column_stack([np.asarray(bank_cv[k], np.float64) for k in ("td_pt", "td_pz", "td_ea", "td_q3", "td_w")])
    return flat_cells(coords, edges)


def same_functional(U: np.ndarray, stored: np.ndarray) -> bool:
    """The definition's functional against S1's, in the precision S1 stored it (float32): exact equality there."""
    return bool(np.array_equal(np.asarray(U).astype(np.float32), np.asarray(stored).astype(np.float32)))


def n1_ratio(a_D: np.ndarray, peak: np.ndarray) -> np.ndarray:
    """N1's statistic per row: |a_D| / peak, peak = max_j |a_uj| over the draw's universes; 1 where both are 0 and +inf
    where only the peak is."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(peak > 0, np.abs(a_D) / peak, np.where(a_D == 0, 1.0, np.inf))


def clipped_fraction(neg_sum: np.ndarray, total: np.ndarray) -> np.ndarray:
    """|sum of the negative a_D| / sum of a_D per draw; 0 where the total is 0."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(total != 0, np.abs(neg_sum) / np.abs(total), 0.0)


def cross_z(H_p: np.ndarray, H_a: np.ndarray, H_cv: np.ndarray, rel_sigma: np.ndarray) -> dict:
    """z_c = [(H_product - H_first_order) / H_CV]_c / (sigma_c / x_c), per draw; its summary per cell."""
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(H_cv > 0, (H_p - H_a) / H_cv, 0.0) / rel_sigma[None, :]
    az = np.abs(z)
    return {"median_abs": np.median(az, axis=0).tolist(), "q95_abs": np.quantile(az, 0.95, axis=0).tolist(),
            "max_abs": az.max(axis=0).tolist(), "median_signed": np.median(z, axis=0).tolist()}


def _bins(cells: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    ok = cells >= 0
    return np.bincount(cells[ok], weights=w[ok], minlength=n)


# ------------------------------------------------------------------------------------------------- the world


def _read_manifest(path: Path) -> dict[str, str]:
    with inv.open_noatime(path) as fh:
        text = fh.read().decode()
    out = {}
    for line in text.splitlines():
        t = line.split(None, 1)
        if len(t) == 2 and len(t[0]) == 64:
            out[t[1].strip()] = t[0]
    return out


def read_pinned_npy(path: Path, want: str) -> np.ndarray:
    """One .npy read once through O_NOATIME, its digest taken over the very bytes loaded."""
    with inv.open_noatime(path) as fh:
        raw = fh.read()
    if hashlib.sha256(raw).hexdigest() != want:
        raise Refusal(f"{path}: the bytes loaded are not the recorded file")
    return np.load(io.BytesIO(raw), allow_pickle=False).astype(np.float64)


def load_tdw_ref(a) -> tuple[np.ndarray, dict]:
    """tdw_ref and D1 (section 5.1): the bank's six GEANT tdw arrays, each read through O_NOATIME against the sf1
    manifest's digest (all six are recorded there as TDW_REF_SHA256), and compared bitwise with tdw_ref one at a time.
    Returns tdw_ref and D1's record; a failed D1 is reported, not raised (the gate reads it as INVALID)."""
    if inv.sha256_noatime(a.manifest) != a.expect_manifest_sha256:
        raise Refusal("the sf1 manifest's digest differs")
    listed = _read_manifest(a.manifest)
    ref, rec = None, {"tags": list(GEANT_BANK_TAGS), "reference": TDW_REF_TAG, "differ": [], "digests": {}}
    for tag in (TDW_REF_TAG,) + tuple(t for t in GEANT_BANK_TAGS if t != TDW_REF_TAG):
        p = a.bank / f"{tag}_tdw.npy"
        want = listed.get(str(p))
        if want is None:
            raise Refusal(f"{p} is not in the sf1 manifest")
        rec["digests"][tag] = want
        arr = read_pinned_npy(p, want)
        if ref is None:
            if want != TDW_REF_SHA256:
                raise Refusal(f"{p}: the manifest's digest is not the declared tdw_ref's")
            ref = arr
        elif not np.array_equal(arr, ref):
            rec["differ"].append(tag)
        del arr
    rec["passes"] = not rec["differ"]
    return ref, rec


def verified_weights(world: dict, a, tag: str) -> tuple[dict, dict]:
    """A universe's weights read ONCE per file through O_NOATIME, the digest over the bytes loaded, against the pins
    file: ``"keep"`` (float64 as loaded) and ``"zero"`` (non-finite zeroed, as fd_1b_inv.universe_weights(..., "zero")).
    A2.1's fd_1b_mc.verified_weights."""
    wdir = mc.universe_dir(tag, a.bank, a.detector_dir)
    keep, zero = {}, {}
    for k in s5p_universe.weight_keys(wdir, tag):
        p = wdir / f"{tag}_{k}.npy"
        keep[k] = read_pinned_npy(p, world["pins"]["files"][str(p)]["sha256"])
        zero[k] = np.nan_to_num(keep[k].copy(), nan=0.0, posinf=0.0, neginf=0.0)
    return keep, zero


def denominator_controls(world: dict, tdw_ref: np.ndarray, d1: dict, load) -> dict:
    """D1 (from load_tdw_ref), D2 and D3 (section 5.1, the director's ruling D).
    D2: hist(tdw_ref) on the bank's coordinates against the npz's CV denom_nd: the same support, the total within
    1e-9 and every cell within 1e-3 (s1_controls.denominator's statistics).
    D3: each of the dump's 8 detector universes carries denom_nd (no tdw) equal to the CV's bitwise."""
    inputs, bank_cv = world["inputs"], world["bank_cv"]
    dn = np.asarray(s5p_universe.denominator(bank_cv, tdw_ref, inputs["edges"]), float)
    ref = np.asarray(inputs["denom_nd"], float)
    m = ref > 0
    same_support = bool(np.array_equal(dn > 0, m))
    dev = float(np.max(np.abs(dn[m] / ref[m] - 1))) if m.any() else 0.0
    tot = float(abs(dn.sum() / ref.sum() - 1))
    d2 = {"same_support": same_support, "total_rel_dev": tot, "max_cell_rel_dev": dev,
          "passes": bool(same_support and tot <= DENOM_TOTAL_TOL and dev <= DENOM_CELL_TOL)}
    det = [f"{b}_{i}" for b in toys.DETECTOR_DRAW_ORDER for i in (0, 1)]
    differ, no_denom = [], []
    for tag in det:
        _, w = load(tag)
        if "denom_nd" not in w or "tdw" in w:
            no_denom.append(tag)
        elif not np.array_equal(np.asarray(w["denom_nd"], float), ref):
            differ.append(tag)
        del w
    d3 = {"universes": det, "differ": differ, "not_denom_nd": no_denom, "passes": not differ and not no_denom}
    return {"D1": d1, "D2": d2, "D3": d3, "passes": bool(d1["passes"] and d2["passes"] and d3["passes"])}


# ------------------------------------------------------------------------------------ the input builders (dep. 4)


def fine_sums(world: dict, load, r: dict, tags: list[str], cells: np.ndarray,
              rows: dict | None = None) -> tuple[dict, dict, np.ndarray, list]:
    """fd_1b_c2.fine_sums with tdw_ref in place of world["tdw_cv"]: per universe (rows in ``tags``' order) A[truth] =
    sum w_truth r and B = sum w_truth over the truth-passing rows at their fine cells, and D, its denominator per fine
    cell, each universe's weights read once (``load(tag)`` -> (keep, zero)) and composed as fd_1b_mc._single gives
    them. With ``rows``, the same read fills each universe's per-row arrays ("wt", "wr", "bkgw" and the denominator's
    "tdw": a detector universe's is tdw_ref, section 3.4)."""
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
        _, zero = load(tag)
        single, p = mc._single(inputs, bkg, world["bank_cv"], tag, zero, world["flux"])
        if rows is not None:
            for k in ("wt", "wr", "bkgw"):
                rows[k][i] = single[k]
            rows["tdw"][i] = zero["tdw"] if "tdw" in zero else world["tdw_ref"]
        H["B"][i], H["D"][i] = hist(single["wt"]), single["denom"].ravel(order="C")
        for t, rt in r.items():
            H[f"A_{t}"][i] = hist(single["wt"] * rt)
        if p is not None:
            phi.append(np.asarray(p, float))
        if tag.rpartition("_")[0] in sa.DETECTOR_BANDS and not np.array_equal(single["denom"], inputs["denom_nd"]):
            det_differs.append(tag)
        del single, zero
    return H, cv, np.array(phi), det_differs


def prepare(world: dict, load, r: dict, flux_p: np.ndarray, U_full: np.ndarray, rows: bool = False) -> dict:
    """fd_1b_c2.prepare's pass on the ``all`` layout, with tdw_ref: one read of every universe (fine_sums), the kept
    fine cells (in a reporting cell and non-zero somewhere), the packing, each truth's single-universe U x_T, and each
    evaluation's band_reference (the variance ratio's denominator) and the linear count's, the ``minus2`` ones over
    ``restrict``'s rows. r maps each truth to its r_T (rows)."""
    inputs = world["inputs"]
    if world.get("tdw_ref") is None:
        raise Refusal("the gate needs tdw_ref (section 3.4)")
    order, bands, tags = layout("all")
    col = {u: i for i, u in enumerate(tags)}
    cells = flat_cells(np.asarray(inputs["MCgen"], float), inputs["edges"])
    cells = np.where(np.asarray(inputs["pass_truth"], bool), cells, -1)
    R = {} if rows else None
    H, cv, phi, det_differs = fine_sums(world, load, r, tags, cells, R)
    if det_differs:
        raise Refusal(f"detector denominators differ from the CV's: {det_differs} (D3)")
    d_ref = np.asarray(s5p_universe.denominator(world["bank_cv"], world["tdw_ref"], inputs["edges"]), float).ravel()
    cv["D"] = d_ref                                   # A2.1's (e2) item 1 with tdw_ref: no composite mixes binnings
    for i, tag in enumerate(tags):
        if tag.rpartition("_")[0] in sa.DETECTOR_BANDS:
            H["D"][i] = d_ref                         # a detector universe's denominator is tdw_ref's (section 3.4)
    D_full, D_cv_full = (H["D"].copy(), cv["D"].copy()) if rows else (None, None)
    support = U_full.sum(axis=0) > 0
    live = np.abs(cv["D"]) + np.abs(H["D"]).sum(axis=0) + np.abs(cv["B"]) + np.abs(H["B"]).sum(axis=0) > 0
    keep = np.flatnonzero(support & live)
    shape = tuple(np.asarray(e).size - 1 for e in inputs["edges"])
    pack = c2.packing(keep, shape, inputs["edges"])
    H = {k: v[:, keep] for k, v in H.items()}
    cv = {k: v[keep] for k, v in cv.items()}
    U = U_full[:, keep]
    const = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]), "pack": pack}
    flux_cols = np.array([col[f"{sa.FLUX}_{i}"] for i in range(bands[sa.FLUX])])
    phi_single = np.repeat(np.asarray(inputs["flux"], float)[None], len(tags), axis=0)
    phi_single[flux_cols] = phi
    P = {"world": world, "flux_p": flux_p, "U_full": U_full, "truths": list(r), "r": r, "order": order,
         "bands": bands, "tags": tags, "col": col, "cells": cells, "H": H, "cv": cv, "phi": phi, "keep": keep,
         "shape": shape, "pack": pack, "U": U, "const": const, "flux_cols": flux_cols, "phi_single": phi_single,
         "rows": R, "D_full": D_full, "D_cv_full": D_cv_full, "d_ref": d_ref, "single_x": {}, "ref_x": {},
         "ref_count": {}}
    for t in r:
        P["single_x"][t] = c2.xt_packed(H[f"A_{t}"], H["B"], H["D"], phi_single, const["n_nucleons"],
                                        const["data_pot"], pack) @ U.T
        for reading in READINGS:
            v = restrict(P, reading)
            e = f"{t}/{reading}"
            P["ref_x"][e] = c2.band_reference(v["single_x"][t], flux_p * 1.0, v["order"], v["bands"], sa.FLUX)
            P["ref_count"][e] = c2.band_reference(v["H"][f"A_{t}"] @ (U > 0).astype(np.float64).T, flux_p * 1.0,
                                                  v["order"], v["bands"], sa.FLUX)
            if not (np.all(P["ref_x"][e] > 0) and np.all(P["ref_count"][e] > 0)):
                raise Refusal(f"{e}: a reporting cell has no band variance")
    return P


def restrict(P: dict, reading: str) -> dict:
    """Departure 3: a reading's view of the one ``all`` pass. The small per-universe sums (H, single_x, phi_single) are
    the ``all`` rows for the reading's tags, selected, not recomputed; the column map and flux_cols are rebuilt on
    those rows. The per-row arrays (P["rows"], about 46 GB each on the real bank) are NOT in the view: the gate
    reaches them through the ``all`` column map with the removed universes' columns 0 (``selection``)."""
    order, bands, tags = layout(reading)
    idx = np.array([P["col"][t] for t in tags])
    col = {u: i for i, u in enumerate(tags)}
    return {"reading": reading, "order": order, "bands": bands, "tags": tags, "col": col, "rows_of_all": idx,
            "H": {k: v[idx] for k, v in P["H"].items()},
            "single_x": {t: x[idx] for t, x in P["single_x"].items()},
            "phi_single": P["phi_single"][idx],
            "flux_cols": np.array([col[f"{sa.FLUX}_{i}"] for i in range(bands[sa.FLUX])])}


def c2_inputs(P: dict, s1: dict, fm: np.ndarray) -> tuple:
    """fd_1b_c2.c2_inputs on this module's pass, with tdw_ref: (rel, geo, V, cv), S1's functional required to be the
    definition's."""
    world = P["world"]
    inputs, bkg = world["inputs"], world["bkg"]
    if not same_functional(P["U_full"], s1["U"]):
        raise Refusal("the definition's functional is not S1's")
    import fd_1b_score as fs
    rel = np.sqrt(np.diag(fs.reported_matrix(s1))) / s1["f"]
    edges = inputs["edges"]
    prec = np.asarray(inputs["pass_reco"], bool)
    geo = {"gen": P["cells"], "reco": np.where(prec, flat_cells(np.asarray(inputs["MCreco"], float), edges), -1),
           "bkg": flat_cells(np.asarray(bkg["bkg_reco"], float), edges), "td": td_cells(world["bank_cv"], edges),
           "fm": np.asarray(fm), "U": P["U"], "shape": P["shape"]}
    V = dict(P["rows"], D=P["D_full"])
    cv = {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
          "bkgw": np.asarray(bkg["bkg_w"], float), "tdw": world["tdw_ref"], "D": P["D_cv_full"]}
    return rel, geo, V, cv


# ------------------------------------------------------------------------------------------- the calibration


def threshold_rule(R: dict) -> dict:
    """Departure 5, the director's mapping (ruling 3): the smallest s on fd_1b_c2.S_GRID whose joint (i)-(iii)
    noise-only STOP over the four evaluations, measured per replicate on the paired null (both readings of a truth
    read the same replicate set), is at most fd_1b_c2.UNION_LIMIT (1 %). The per-evaluation STOP is fd_1b_c2.stops_at
    on fd_1b_c2.null_stats, unchanged. (i) alone over the budget is flagged (11-04 item 2: it goes to Joseph)."""
    if set(R) != set(EVALUATIONS):
        raise Refusal(f"the rule is over the four evaluations {EVALUATIONS}, not {sorted(R)}")
    sizes = {np.asarray(v).shape[0] for v in R.values()}
    if len(sizes) != 1:
        raise Refusal("the four evaluations need the same replicate sets (paired)")
    st = {e: c2.null_stats(R[e]) for e in EVALUATIONS}
    sd = {e: (st[e]["sd_ml"], st[e]["sd_c"]) for e in EVALUATIONS}

    def union(stops):
        return float(np.mean(np.any([stops[e] for e in EVALUATIONS], axis=0)))
    grid, chosen = [], None
    for s in c2.S_GRID:
        stops = {e: c2.stops_at(st[e], s, *sd[e]) for e in EVALUATIONS}
        u = union(stops)
        grid.append({"s": s, "union": u, "per_evaluation": {e: float(v.mean()) for e, v in stops.items()}})
        if chosen is None and u <= c2.UNION_LIMIT:
            chosen = s
    i_alone = union({e: st[e]["i"] for e in EVALUATIONS})
    return {"evaluations": list(EVALUATIONS), "measured_jointly": True, "grid": grid, "s": chosen,
            "thresholds": {e: {"ii_mean_log": None if chosen is None else chosen * c2.SD_MULT_LOGMEAN * sd[e][0],
                               "iii_alpha_multiple": None if chosen is None else chosen * c2.SD_MULT_CELL,
                               "sd_mean_log": sd[e][0], "sd_per_cell": sd[e][1].tolist()} for e in EVALUATIONS},
            "i_alone_union": i_alone, "i_alone_exceeds": bool(i_alone > c2.UNION_LIMIT)}


_STATE: dict = {}


def _worker_init(state: dict) -> None:
    _STATE.update(state)


def one_set(job: tuple[str, int]) -> tuple[str, int, dict]:
    """Replicate set s of truth t in both readings: per reading, the variance ratios at N (x_T and the linear count,
    fd_1b_c2.set_ratios unchanged, on restrict's rows) and x_T's at the set's first 300 draws (the backstop's SDs)."""
    t, s = job
    st = _STATE
    draws = calibration_draws(t, s, st["flux_p"], st["groups"], st["n"])
    out = {}
    for reading in READINGS:
        v = st["views"][reading]
        S = selection(draws, reading, v["col"])
        H = {"A": v["H"][f"A_{t}"], "B": v["H"]["B"], "D": v["H"]["D"]}
        cv = {"A": st["cv"][f"A_{t}"], "B": st["cv"]["B"], "D": st["cv"]["D"]}
        e = f"{t}/{reading}"
        args = (H, cv, st["U"], st["ref_x"][e], st["ref_count"][e], v["flux_cols"], st["phi"], st["const"])
        rx, rl = c2.set_ratios(S, *args)
        rx300, _ = c2.set_ratios(S[:BACKSTOP_N], *args)
        out[reading] = (rx, rl, rx300)
    return t, s, out


def require_threads() -> dict:
    """The gate and the calibration run at one BLAS thread (A2.1 ruling (a); section 9): every THREAD_VARS entry is
    "1" (VECLIB_MAXIMUM_THREADS may be unset off macOS)."""
    th = {k: os.environ.get(k) for k in THREAD_VARS}
    bad = [k for k, v in th.items() if v != "1" and not (k == "VECLIB_MAXIMUM_THREADS" and v is None)]
    if bad:
        raise Refusal(f"one BLAS thread is required: {bad} are not 1")
    return th


def code_digests() -> dict:
    """The code the calibration and the gate share; the gate refuses a calibration computed by other code."""
    mods = {"ll5d.py": Path(__file__), "fd_1b_c2.py": Path(c2.__file__), "fd_1b_mc.py": Path(mc.__file__),
            "fd_1b_toys.py": Path(toys.__file__), "fd_1b_inv.py": Path(inv.__file__), "s1_assemble.py": Path(sa.__file__),
            "s5p_universe.py": Path(s5p_universe.__file__), "clip_probe2.py": Path(c2.cp2.__file__),
            "cov2d.py": Path(c2.cov2d.__file__)}
    return {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in mods.items()}


def truths_r(world: dict, prep: Path, truths) -> tuple[dict, dict]:
    """Each truth's r_T (fd_1b_mc.truth_weight on F1's pinned ratio) and the control r_T > 0 and finite on every row
    (section 3.1, section 10)."""
    r, ctl = {}, {}
    for t in truths:
        ratio, _ = mc.truth_ratio(t, prep)
        r[t] = np.asarray(mc.truth_weight(t, world["inputs"], ratio, None), float)
        bad = np.flatnonzero(~(np.isfinite(r[t]) & (r[t] > 0)))
        ctl[t] = {"rows_not_positive": int(bad.size), "first_rows": bad[:20].tolist(), "passes": bad.size == 0}
    return r, ctl


def load_world(a) -> tuple[dict, dict]:
    """fd_1b_mc._load_world (the npz and background digests, the pins, the bank CV, the staged flux table, the
    groups), then tdw_ref with D1."""
    world = mc._load_world(a)
    tdw_ref, d1 = load_tdw_ref(a)
    world["tdw_ref"] = tdw_ref
    world["tdw_cv"] = tdw_ref                         # fd_1b_c2.c2_vi reads this key: here it is tdw_ref
    return world, d1


def calib_main(a) -> dict:
    """The calibration job: one read of every universe, the references per evaluation, a measured single-set time and
    projection (refusing past --budget-seconds or 0.9 x --time-limit-seconds), then CAL_SETS replicate sets per truth
    across worker processes, each read in both readings; the director's outputs and the 11-04 controls."""
    import multiprocessing
    t0 = time.time()
    threads = require_threads()
    check_n(a.draws)
    inv.OPENED.clear()
    world, d1 = load_world(a)
    load = lambda tag: verified_weights(world, a, tag)  # noqa: E731
    r, r_ctl = truths_r(world, a.prep, TRUTHS)
    if not all(v["passes"] for v in r_ctl.values()):
        raise Refusal(f"r_T > 0 fails: {r_ctl}")
    flux_p = mc.via_noatime(toys.flux_probabilities, a.flux_constraint)
    fm = sa.fine_map(a.definition)
    P = prepare(world, load, r, flux_p, sa.functional_matrix(fm))
    views = {reading: restrict(P, reading) for reading in READINGS}
    state = {"views": views, "cv": P["cv"], "U": P["U"], "ref_x": P["ref_x"], "ref_count": P["ref_count"],
             "phi": P["phi"], "const": P["const"], "flux_p": flux_p, "groups": world["groups"], "n": a.draws}
    _worker_init(state)
    t1 = time.time()
    first = one_set((TRUTHS[0], 0))
    per_set = time.time() - t1
    total = len(TRUTHS) * a.sets
    projected = (time.time() - t0) + 1.15 * total * per_set / a.workers
    line = PROJECTION_SHARE * a.time_limit_seconds
    timing = {"fine_cells_kept": int(P["keep"].size), "set_seconds_measured": per_set, "workers": a.workers,
              "projected_seconds": projected, "budget_seconds": a.budget_seconds, "projection_line_seconds": line}
    print(json.dumps({"calibration": "timing", **timing}), flush=True)
    if projected > min(a.budget_seconds, line):
        raise Reprice(f"projected {projected:.0f} s passes min(budget {a.budget_seconds}, 0.9 x limit {line:.0f}) s")
    jobs = [(t, s) for t in TRUTHS for s in range(a.sets) if (t, s) != (TRUTHS[0], 0)]
    Rx = {e: np.empty((a.sets, sa.N_CELLS)) for e in EVALUATIONS}
    Rl = {e: np.empty((a.sets, sa.N_CELLS)) for e in EVALUATIONS}
    R3 = {e: np.empty((a.sets, sa.N_CELLS)) for e in EVALUATIONS}

    def put(t, s, out):
        for reading, (rx, rl, r3) in out.items():
            e = f"{t}/{reading}"
            Rx[e][s], Rl[e][s], R3[e][s] = rx, rl, r3
    put(*first)
    with multiprocessing.get_context("fork").Pool(a.workers) as pool:
        for res in pool.imap_unordered(one_set, jobs, chunksize=8):
            put(*res)
    law, lin = c2.control(Rl), c2.linearisation(Rx)            # 11-04 item 4: at N, before any threshold is read
    rule = threshold_rule(Rx)
    power = c2.power_at(Rx, rule) if rule["s"] is not None else None
    verdict = c2.calibration_verdict_n(law, lin, rule, power)
    sd300 = {e: np.std(R3[e], axis=0, ddof=1).tolist() for e in EVALUATIONS}
    rec = {"schema": SCHEMA_CAL, "step": "ll5d-calibration", "verdict": verdict, "truths": list(TRUTHS),
           "evaluations": list(EVALUATIONS), "sets": a.sets, "draws_per_set": a.draws, "rule": rule, "power": power,
           "sd300_per_cell": sd300, "seeds": dict(CAL_SEED), "salt": CAL_SALT,
           "constants": {"k": c2.GATE_K, "dev": c2.GATE_DEV, "sd_mult_mean_log": c2.SD_MULT_LOGMEAN,
                         "sd_mult_cell": c2.SD_MULT_CELL, "union_limit": c2.UNION_LIMIT, "control_z": c2.CONTROL_Z,
                         "linearisation_tol": c2.LINEARISATION_TOL, "s_grid": [c2.S_GRID[0], c2.S_GRID[-1], 0.01],
                         "power_min": c2.POWER_MIN, "uniform_deflation": c2.UNIFORM_DEFLATION,
                         "backstop_n": BACKSTOP_N, "gate_n_max": GATE_N_MAX},
           "outputs_descriptive": c2.rates(Rx), "control_law": law, "control_linearisation": lin,
           "ratio_mean_per_cell": {e: Rx[e].mean(axis=0).tolist() for e in EVALUATIONS},
           "checks": {"r_positive": r_ctl, "D1": d1}, "threads": threads,
           "timing": dict(timing, seconds=time.time() - t0), "code_sha256": code_digests(),
           "fd_1b_c2_source": FD_1B_C2_SOURCE, "inputs": inputs_record(world, a),
           "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "atime": inv.atime_check()}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out.with_suffix(".npz"), **{f"ratio_{e.replace('/', '_')}": Rx[e] for e in EVALUATIONS},
                        **{f"count_ratio_{e.replace('/', '_')}": Rl[e] for e in EVALUATIONS},
                        **{f"ratio300_{e.replace('/', '_')}": R3[e] for e in EVALUATIONS},
                        **{f"single_x_{t}": P["single_x"][t] for t in TRUTHS})
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def inputs_record(world: dict, a) -> dict:
    return {"npz_sha256": world["npz_sha"], "bkg_sha256": world["bkg_sha"], "pins_sha256": a.expect_pins_sha256,
            "flux_table_sha256": a.expect_flux_table_sha256, "manifest_sha256": a.expect_manifest_sha256,
            "tdw_ref_sha256": TDW_REF_SHA256}


# ---------------------------------------------------------------------------------------------- the receipt


def compose_rows(Vq: np.ndarray, ref: np.ndarray, cols, rows=None) -> tuple[np.ndarray, np.ndarray]:
    """Section 3.3 in compose's order, exactly: a_D = a_u1 + sum_{j>=2} (a_uj - a_ref), accumulated in draw order
    (k = 1 gives a_u1 bitwise), and the peak max_j |a_uj| for N1; on ``rows`` only when given (A2.1's
    fd_1b_mc.pinned_composite, the receipt's recompute)."""
    sel = slice(None) if rows is None else rows
    acc = Vq[cols[0], sel].copy()
    peak = np.abs(acc)
    r = ref[sel]
    for c in cols[1:]:
        acc += Vq[c, sel] - r
        np.maximum(peak, np.abs(Vq[c, sel]), out=peak)
    return acc, peak


def product_rows(Vq: np.ndarray, ref: np.ndarray, cols, additive: np.ndarray, inv_ref: np.ndarray | None = None
                 ) -> np.ndarray:
    """The 11-02 addition (i)'s product composite for one draw, streamed over the draw's own universes (no array the
    size of V is built): a_u1 prod_{j>=2} (a_uj / a_ref) where a_ref != 0, and the first-order composite ``additive``
    where a_ref = 0. This is A2.1's fd_1b_mc.crossterm rule, which forms the same product by logs and sign parity; the
    two agree to rounding (a test holds them within 1e-12 relative)."""
    nz = ref != 0
    if inv_ref is None:
        inv_ref = np.divide(1.0, ref, out=np.zeros_like(ref, dtype=float), where=nz)
    prod = Vq[cols[0]].astype(float, copy=True)
    for c in cols[1:]:
        prod *= Vq[c]
        prod *= inv_ref
    return np.where(nz, prod, additive)


def screen_floor(Vq: np.ndarray, cols_by_band: dict) -> np.ndarray:
    """N1's screen for one reading (A2.1's fd_1b_mc.screen_floor, the proposition of amendment 2 section 3): L per row
    = max over the reading's bands of min over the band's universes of |a_u|, one universe at a time (no temporary the
    size of a band). Every draw of the reading holds one universe of each of its bands, so its peak is >= L, and no
    (row, draw) with |a_D| <= 10 L can pass N1's bound."""
    L = np.zeros(Vq.shape[1])
    for cs in cols_by_band.values():
        lo = None
        for c in cs:
            a = np.abs(Vq[c])
            lo = a if lo is None else np.minimum(lo, a, out=lo)
        np.maximum(L, lo, out=L)
    return L


def row_max(Vq: np.ndarray) -> np.ndarray:
    """max over every universe of |a_u| per row, one universe at a time."""
    m = np.abs(Vq[0]).copy()
    for c in range(1, Vq.shape[0]):
        np.maximum(m, np.abs(Vq[c]), out=m)
    return m


def nature_truth(comp: dict, r: np.ndarray, geo: dict, phi: np.ndarray, const_full: dict) -> dict:
    """Section 3.4 on one nature's per-row composites: each tree clipped on its own composite, row by row
    (wt+ = max(wt_D, 0) on the truth-passing rows, tdw+ = max(tdw_D, 0)), then histogrammed (the denominator on the
    bank's truth coordinates, as s5p_universe.denominator bins them), then x_T by fd_1b_c2.xt_flat (true_xsec through
    extract_cross_section_nd's expression). Returns the fine sums, x_T and the clipped masses per fine cell."""
    nf = int(np.prod(geo["shape"]))
    wt, tdw = comp["wt"], comp["tdw"]
    wtp, tdp = np.maximum(wt, 0.0), np.maximum(tdw, 0.0)
    A, B, D = _bins(geo["gen"], wtp * r, nf), _bins(geo["gen"], wtp, nf), _bins(geo["td"], tdp, nf)
    x = c2.xt_flat(A[None], B[None], D[None], np.asarray(phi, float)[None], const_full["n_nucleons"],
                   const_full["data_pot"], geo["shape"], const_full["edges"])[0]
    return {"A": A, "B": B, "D": D, "x": x, "m_wt": _bins(geo["gen"], np.maximum(-wt, 0.0), nf),
            "m_tdw": _bins(geo["td"], np.maximum(-tdw, 0.0), nf)}


NEAR_BOUND_REL = 1e-9          # N1: pairs this close to the bound are recomputed in compose's order (A2.1's)
ZERO_REL = 1e-9                # T <= 0: rows with |a_D| <= ZERO_REL max_u |a_u| are recomputed in compose's order


def receipt(V: dict, cv: dict, draws_all: list[list[str]], col: dict, r: np.ndarray, phi_u: np.ndarray, geo: dict,
            U_full: np.ndarray, d_ref: np.ndarray, const_full: dict, flux_cols_map: dict, seeds: list[int],
            rel: np.ndarray, clock=None, block: int = DRAW_BLOCK) -> tuple[dict, dict]:
    """Section 5.1 at one truth: every declared draw in both readings. STOP if N1 fires (a per-row composite above
    N1_BOUND x the largest single-universe magnitude on that row) or if any reporting cell's U T_D is <= 0 or
    non-finite. The run halts at the first STOP (#939 item 2), the STOP recorded as it fired.

    The exact float64 pass follows 1B's section 2d (ii) as the director ruled it (A2.1's fd_1b_mc.exact_n1): each
    block's composites are S V - (k - 1) a_ref (float64 BLAS); for N1, the rows past the screen |a_D| > 10 L get the
    exact peak and the pairs within NEAR_BOUND_REL of the bound are recomputed in compose's order (compose_rows); for
    T <= 0, every wt and tdw row with |a_D| <= ZERO_REL max_u |a_u| is recomputed in compose's order before the clip,
    so every clip sign is compose's (a BLAS composite's rounding is far below that margin), and T_D is 0 in a cell
    exactly when every row there clips in compose's order.

    Recorded per nature (BLAS arithmetic, descriptive): N1's maxima, the clipped fractions |sum lambda-| / sum lambda
    (signal on the reco-passing rows, background), the fine cells with dn+ = 0 < d_ref and with ofin+ = 0 < ofin_CV,
    and the clipped tdw and wt masses mapped by the fine map to the 16 cells; per fine cell, the masses summed over the
    natures (the npz). Returned apart, to be sealed (clip_prep_seal), and read by no verdict: per reading the per-row
    sums of max(-lambda, 0) and each draw's U T_D clipped and unclipped (section 5.3's inputs). The cross terms (section 7, Joseph's 11-02 addition (i), descriptive; they move no
    verdict and gate nothing): per nature the U-mapped histograms under the product (product_rows, streamed) and the
    first-order composite, of the reco proxy (w_reco on the reco-passing rows at their reco cells, plus the
    background) and of the truth weight (at the gen cells), summarized per reading by cross_z in units of sigma_c / x_c
    (``rel``). ``clock(done, total)`` may raise Reprice."""
    nf = int(np.prod(geo["shape"]))
    fm = geo["fm"]
    cells16 = lambda fine: np.where(fine >= 0, fm[np.maximum(fine, 0)], -1)  # noqa: E731
    t16, d16 = cells16(geo["gen"]), cells16(geo["td"])
    ofin_cv = _bins(geo["gen"], np.asarray(cv["wt"], float), nf)
    reco = geo["reco"] >= 0
    Q = ("wt", "wr", "bkgw", "tdw")
    refs = {q: np.asarray(cv[q], float) for q in Q}
    inv_refs = {q: np.divide(1.0, refs[q], out=np.zeros_like(refs[q]), where=refs[q] != 0) for q in ("wt", "wr", "bkgw")}
    vmax = {q: row_max(V[q]) for q in ("wt", "tdw")}
    flat_s = np.where(reco, geo["reco"], -1)
    hist16 = lambda flat, w: U_full @ _bins(flat, w, nf)  # noqa: E731
    H0 = {"reco": hist16(flat_s, refs["wr"]) + hist16(geo["bkg"], refs["bkgw"]), "truth": hist16(geo["gen"], refs["wt"])}
    H = {reading: {k: [] for k in ("p_reco", "a_reco", "p_truth", "a_truth")} for reading in READINGS}
    per, fine_mass = [], {"wt": np.zeros(nf), "tdw": np.zeros(nf)}
    seal = {}                                                 # the clip-prep products (sealed; see clip_prep_seal)
    stop, n_done = None, 0
    total = len(READINGS) * len(draws_all)
    exact = {q: {"pairs_past_screen": 0, "near_bound_recomputed": 0} for q in Q}
    exact["zero_recomputed"] = {"wt": 0, "tdw": 0}
    for reading in READINGS:
        _, bands_r, tags_r = layout(reading)
        dtags = reading_draws(draws_all, reading)
        for d, tags in enumerate(dtags):
            if sorted(t.rpartition("_")[0] for t in tags) != sorted(bands_r):
                raise Refusal(f"{reading} draw {d}: it does not hold exactly one universe of every band")
        by_band: dict = {}
        for t in tags_r:
            by_band.setdefault(t.rpartition("_")[0], []).append(col[t])
        lim = {q: N1_BOUND * screen_floor(V[q], by_band) * (1.0 - NEAR_BOUND_REL) for q in Q}
        dcols = [[col[t] for t in tags] for tags in dtags]
        sig_neg = np.zeros(V["wr"].shape[1])
        bkg_neg = np.zeros(V["bkgw"].shape[1])
        t_clip, t_unclip = [], []
        S = np.zeros((len(dcols), V["wt"].shape[0]))
        for d, cs in enumerate(dcols):
            S[d, cs] = 1.0
        k = S.sum(axis=1)
        for d0 in range(0, len(dcols), block):
            Sb, kb = S[d0:d0 + block], k[d0:d0 + block, None] - 1.0
            A = {q: Sb @ V[q] - kb * refs[q][None] for q in Q}
            for i in range(Sb.shape[0]):
                d = d0 + i
                cols = dcols[d]
                comp, n1 = {q: A[q][i] for q in Q}, {}
                for q in Q:
                    a = comp[q]
                    rows = np.flatnonzero(np.abs(a) > lim[q])
                    exact[q]["pairs_past_screen"] += int(rows.size)
                    above, mx = 0, 0.0
                    if rows.size:
                        _, peak = compose_rows(V[q], refs[q], cols, rows)
                        rr = n1_ratio(a[rows], peak)
                        close = np.abs(rr - N1_BOUND) <= NEAR_BOUND_REL * N1_BOUND
                        if np.any(close):
                            exact[q]["near_bound_recomputed"] += int(close.sum())
                            acc, pk = compose_rows(V[q], refs[q], cols, rows[close])
                            rr[close] = n1_ratio(acc, pk)
                        above, mx = int(np.sum(rr > N1_BOUND)), float(rr.max())
                    n1[q] = {"max_past_screen": mx, "rows_above": above}
                for q in ("wt", "tdw"):                       # T <= 0: compose's clip sign on every near-zero row
                    z = np.flatnonzero(np.abs(comp[q]) <= ZERO_REL * vmax[q])
                    if z.size:
                        exact["zero_recomputed"][q] += int(z.size)
                        comp[q] = comp[q].copy()
                        comp[q][z] = compose_rows(V[q], refs[q], cols, z)[0]
                prod = {q: product_rows(V[q], refs[q], cols, comp[q], inv_refs[q]) for q in ("wt", "wr", "bkgw")}
                h = H[reading]
                h["a_reco"].append(hist16(flat_s, comp["wr"]) + hist16(geo["bkg"], comp["bkgw"]))
                h["p_reco"].append(hist16(flat_s, prod["wr"]) + hist16(geo["bkg"], prod["bkgw"]))
                h["a_truth"].append(hist16(geo["gen"], comp["wt"]))
                h["p_truth"].append(hist16(geo["gen"], prod["wt"]))
                del prod
                flux_tags = [t for t in dtags[d] if t.rpartition("_")[0] == sa.FLUX]
                phi = phi_u[flux_cols_map[flux_tags[0]]]
                nt = nature_truth(comp, r, geo, phi, const_full)
                T16 = U_full @ nt["x"]
                lam = comp["wr"][reco] * r[reco]
                sig_neg[reco] += np.maximum(-lam, 0.0)            # section 5.3's clipmean input, per row
                bkg_neg += np.maximum(-comp["bkgw"], 0.0)
                t_clip.append(T16)
                t_unclip.append(U_full @ unclipped_truth(comp, r, geo, phi, const_full))   # section 5.3's tau_c input
                per.append({"reading": reading, "draw": d, "seed": int(seeds[d]), "n1": n1,
                            "clipped_fraction_signal": float(clipped_fraction(np.minimum(lam, 0.0).sum(), lam.sum())),
                            "clipped_fraction_background": float(clipped_fraction(
                                np.minimum(comp["bkgw"], 0.0).sum(), comp["bkgw"].sum())),
                            "fine_cells_dn0_where_ref_positive": int(np.sum((nt["D"] == 0) & (d_ref > 0))),
                            "fine_cells_ofin0_where_cv_positive": int(np.sum((nt["B"] == 0) & (ofin_cv > 0))),
                            "clipped_wt_mass_16": _bins(t16, np.maximum(-comp["wt"], 0.0), sa.N_CELLS).tolist(),
                            "clipped_tdw_mass_16": _bins(d16, np.maximum(-comp["tdw"], 0.0), sa.N_CELLS).tolist()})
                fine_mass["wt"] += nt["m_wt"]
                fine_mass["tdw"] += nt["m_tdw"]
                reasons = [f"N1: {q} {v['rows_above']} rows above {N1_BOUND}" for q, v in n1.items() if v["rows_above"]]
                bad = np.flatnonzero(~np.isfinite(T16) | (T16 <= 0))
                if bad.size:
                    reasons.append(f"T <= 0: reporting cells {bad.tolist()}")
                del comp, nt, lam
                n_done += 1
                if reasons:
                    stop = {"reading": reading, "draw": d, "seed": int(seeds[d]), "reasons": reasons}
                    break
                if clock is not None:
                    clock(n_done, total)
            del A
            if stop:
                break
        seal.update({f"signal_negative_lambda_sum_{reading}": sig_neg, f"background_negative_lambda_sum_{reading}": bkg_neg,
                     f"U_T_clipped_{reading}": np.array(t_clip), f"U_T_unclipped_{reading}": np.array(t_unclip),
                     f"draws_{reading}": np.array(len(t_clip))})
        if stop:
            break
    cross = {}
    for reading, h in H.items():
        if h["a_reco"]:
            Ah = {kk: np.array(v) for kk, v in h.items()}
            cross[reading] = {"reco_proxy_U_mapped": cross_z(Ah["p_reco"], Ah["a_reco"], H0["reco"], rel),
                              "truth_weight_histogram": cross_z(Ah["p_truth"], Ah["a_truth"], H0["truth"], rel),
                              "draws": int(Ah["a_reco"].shape[0])}
    cross["units"] = "[(H_product - H_first_order) / H_CV]_c / (sigma_c / x_c), sigma_c S1's reported; descriptive"
    rec = {"verdict": "STOP" if stop else "PASS", "stop": stop, "natures_evaluated": n_done, "natures_declared": total,
           "n1_bound": N1_BOUND, "per_nature": per, "exact": exact,
           "n1_max_past_screen": {q: max(p["n1"][q]["max_past_screen"] for p in per) for q in Q} if per else None,
           "crossterm": cross,
           "arithmetic": "BLAS composites; N1 and every clip sign exact in compose's order (section 5.1, 1B's 2d (ii))"}
    return rec, fine_mass, seal


def unclipped_truth(comp: dict, r: np.ndarray, geo: dict, phi: np.ndarray, const_full: dict) -> np.ndarray:
    """x_T of a nature's per-row composites with no clip (tau_c's subtrahend, section 5.3): the fine sums of wt r, wt
    and tdw as composed, through fd_1b_c2.xt_flat, so T is kept only where the unclipped denominator is > 0 and the
    extraction's own positive-denominator mask holds."""
    nf = int(np.prod(geo["shape"]))
    wt, tdw = comp["wt"], comp["tdw"]
    A, B, D = _bins(geo["gen"], wt * r, nf), _bins(geo["gen"], wt, nf), _bins(geo["td"], tdw, nf)
    return c2.xt_flat(A[None], B[None], D[None], np.asarray(phi, float)[None], const_full["n_nucleons"],
                      const_full["data_pot"], geo["shape"], const_full["edges"])[0]


def clip_prep_seal(path: Path, seal: dict) -> dict:
    """The clip-prep products (the director's ruling of 2026-11-08 on A1b's clipcheck inputs): per reading, the per-row
    sum over the declared draws of max(-lambda, 0) for signal (lambda = w_reco_D r on the reco-passing rows) and
    background (lambda = bkg_w_D), and each draw's U T_D clipped and unclipped. They are construction inputs to section
    5.3 (A1b's clipmean and tau_c), written sealed: the gate record holds only their path, size and sha256, no one
    opens or summarizes them before binding 3, and no verdict reads them."""
    np.savez(path, **seal)
    raw = path.read_bytes()
    return {"path": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "keys": sorted(seal), "sealed": "not opened or summarized before binding 3; gates nothing"}


# --------------------------------------------------------------------------------------------------- the gate


def read_calibration(a, single_x: np.ndarray, truth: str) -> dict:
    """The gate's tie to its calibration: the digests given, CALIBRATED, computed by this very code, at an N in
    range, and its single-universe U x_T this job's bitwise (A2.1's tie, same code and one BLAS thread)."""
    if inv.sha256_noatime(a.calibration) != a.expect_calibration_sha256:
        raise Refusal("the calibration record's digest differs")
    with inv.open_noatime(a.calibration) as fh:
        cal = json.loads(fh.read().decode())
    if cal.get("schema") != SCHEMA_CAL or cal.get("verdict") != "CALIBRATED":
        raise Refusal(f"the calibration is {cal.get('verdict')!r}, not CALIBRATED: nothing proceeds")
    if cal.get("code_sha256") != code_digests():
        raise Refusal("the calibration was computed by other code than this gate's")
    thr = (cal.get("rule") or {}).get("thresholds") or {}
    if ((cal.get("rule") or {}).get("s") is None or set(thr) != set(EVALUATIONS)
            or any(thr[e].get(k) is None for e in EVALUATIONS for k in ("ii_mean_log", "iii_alpha_multiple"))
            or set(cal.get("sd300_per_cell") or {}) != set(EVALUATIONS)):
        raise Refusal("the calibration carries no threshold or backstop SD for every evaluation")
    check_n(int(cal["draws_per_set"]))
    npz = a.calibration.with_suffix(".npz")
    if inv.sha256_noatime(npz) != a.expect_calibration_npz_sha256:
        raise Refusal("the calibration's ratio file digest differs")
    with inv.open_noatime(npz) as fh:
        z = np.load(fh, allow_pickle=False)
        if not np.array_equal(z[f"single_x_{truth}"], single_x):
            raise Refusal(f"{truth}: the single-universe U x_T is not the calibration's (another world, code or BLAS)")
    return cal


def gate_main(a) -> dict:
    """One truth's gate job (section 5): controls, the receipt, then per reading C2's record and the large-sample
    gate, the backstop and the cross terms. Halts at a receipt STOP; projects before the receipt's tail and before
    the gate's blocks (REPRICE past 0.9 x --time-limit-seconds)."""
    t0 = time.time()
    t = a.truth
    a.out.parent.mkdir(parents=True, exist_ok=True)
    line = PROJECTION_SHARE * a.time_limit_seconds
    threads = require_threads()
    inv.OPENED.clear()
    world, d1 = load_world(a)
    load = lambda tag: verified_weights(world, a, tag)  # noqa: E731
    rec = {"schema": SCHEMA_GATE, "step": "ll5d-gate", "truth": t, "threads": threads,
           "fd_1b_c2_source": FD_1B_C2_SOURCE, "code_sha256": code_digests(), "inputs": inputs_record(world, a),
           "time_limit_seconds": a.time_limit_seconds, "projection_line_seconds": line}
    controls = denominator_controls(world, world["tdw_ref"], d1, load)
    r, r_ctl = truths_r(world, a.prep, [t])
    rec["controls"] = {"denominator": controls, "r_positive": r_ctl[t]}
    if not (controls["passes"] and r_ctl[t]["passes"]):
        return finish(a, rec, "INVALID", "a control failed (section 10)", t0)
    flux_p = mc.via_noatime(toys.flux_probabilities, a.flux_constraint)
    fm = sa.fine_map(a.definition)
    U_full = sa.functional_matrix(fm)
    P = prepare(world, load, r, flux_p, U_full, rows=True)
    cal = read_calibration(a, P["single_x"][t], t)
    n = int(cal["draws_per_set"])
    import fd_1b_score as fs
    s1 = mc.via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    rel, geo, V, cv = c2_inputs(P, s1, fm)
    rec["one_off_seconds"] = round(time.time() - t0, 1)
    groups = world["groups"]
    draws300 = declared_draws(t, flux_p, groups)
    inputs = world["inputs"]
    const_full = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]),
                  "edges": inputs["edges"]}
    flux_map = {f"{sa.FLUX}_{i}": i for i in range(P["bands"][sa.FLUX])}
    t_r = time.time()

    def clock(done, total):
        if done == RECEIPT_PROBE:
            per = (time.time() - t_r) / done
            proj = (time.time() - t0) + per * (total - done)
            rec["receipt_projection"] = {"after": done, "seconds_per_nature": per, "projected_seconds": proj}
            if proj > line:
                raise Reprice(f"the receipt alone projects {proj:.0f} s past the line {line:.0f} s")
    rc, fine_mass, seal = receipt(V, cv, draws300, P["col"], r[t], P["phi"], geo, U_full, P["d_ref"], const_full,
                            flux_map, list(TOY_SEEDS[t]), rel, clock)
    rc["seconds"] = round(time.time() - t_r, 1)
    rec["receipt"] = rc
    np.savez_compressed(a.out.with_suffix(".receipt.npz"), clipped_wt_mass_fine=fine_mass["wt"],
                        clipped_tdw_mass_fine=fine_mass["tdw"])
    rec["clip_prep"] = clip_prep_seal(a.out.with_suffix(".clipprep.npz"), seal) if seal else None
    if rc["verdict"] == "STOP":
        return finish(a, rec, "STOP", f"the receipt fired: {rc['stop']}", t0)
    terms = c2.c2_terms(V, cv)
    seeds_n = gate_seeds(t, n)
    draws_n = draws300 + [mc.draw_universes(toys.draw_for_seed(sd, flux_p, groups)) for sd in seeds_n[BACKSTOP_N:]]
    vi = c2.c2_vi(P, cv, fm, geo)
    blocks_left = len(READINGS) * (BACKSTOP_N + n) // DRAW_BLOCK
    readings, gate_rec, back = {}, {}, {}
    for reading in READINGS:
        e = f"{t}/{reading}"
        S300 = selection(draws300, reading, P["col"])
        Sn = selection(draws_n, reading, P["col"])
        phi300, phin = (c2.draw_flux(S, P["flux_cols"], P["phi"]) for S in (S300, Sn))
        q_of = lambda S, ph: c2.c2_truth(V, cv, S, r[t], geo, ph, P["const"], terms=terms)  # noqa: E731
        if "gate_projection" not in rec:
            tb = time.time()
            head = q_of(S300[:2 * DRAW_BLOCK], phi300[:2 * DRAW_BLOCK])
            per_block = (time.time() - tb) / 2
            blocks_left -= 2
            proj = (time.time() - t0) + per_block * blocks_left
            rec["gate_projection"] = {"seconds_per_block": per_block, "blocks_left": blocks_left,
                                      "projected_seconds": proj, "n": n}
            if proj > line:
                raise Reprice(f"the gate projects {proj:.0f} s past the line {line:.0f} s")
            tail = q_of(S300[2 * DRAW_BLOCK:], phi300[2 * DRAW_BLOCK:])
            q300 = {k: np.concatenate([head[k], tail[k]], axis=1) for k in head}
        else:
            q300 = q_of(S300, phi300)
        qn = q_of(Sn, phin)
        for k, v in q300.items():                     # 11-04 item 1: the declared 300 are the sample's first 300
            if not np.array_equal(qn[k][:, :v.shape[1]], v):
                raise Refusal(f"{e}: the gate sample's first 300 differ from the declared draws in {k}")
        gate_rec[e] = c2.c2_block(qn, P["ref_x"][e], rel)
        thr = cal["rule"]["thresholds"][e]
        rt = c2.reading_1b({"vi": vi, "b": {e: gate_rec[e]}},
                           {c2.CLIPPED: lambda v, thr=thr: c2.gate_n(v, thr)["passes"], "first_order": c2.c2_gate,
                            "multiplicative": c2.c2_gate})
        readings[e] = dict(rt[e], gate_n=c2.gate_n(gate_rec[e]["variance_ratio"][c2.CLIPPED], thr))
        r300 = np.var(q300["Nc"], axis=1, ddof=1) / P["ref_x"][e]
        back[e] = c2.backstop(r300, cal["sd300_per_cell"][e])
        del q300, qn
    rec.update({"n": n, "record": {"vi": vi, "b": gate_rec}, "reading_detail": readings, "backstop": back,
                "reads": {e: v["reads"] for e, v in readings.items()},
                "gate_sample": {"n": n, "first_300_bitwise": True, "seeds": [seeds_n[0], seeds_n[-1]]},
                "calibration_sha256": a.expect_calibration_sha256,
                "calibration_npz_sha256": a.expect_calibration_npz_sha256,
                "config_hash": config_hash(rec["code_sha256"], rec["inputs"])})
    ok = all(v == "option (1)" for v in rec["reads"].values()) and all(b["passes"] for b in back.values())
    return finish(a, rec, "PASS" if ok else "STOP", None if ok else "the gate or the backstop failed", t0)


def config_hash(code: dict, inputs: dict) -> str:
    """11-04 item 5's config hash, shared by the gate sample and the coverage draws: the code, the inputs, the clip rule
    (section 3.4's, per row), the draw salt and the declared seeds."""
    doc = {"code": code, "inputs": inputs, "clip_rule": "LL5D section 3.4, per row", "draw_salt": toys.DRAW_SALT,
           "toy_seeds": {t: [int(x) for x in TOY_SEEDS[t]] for t in TRUTHS}, "removed": list(REMOVED)}
    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()


def finish(a, rec: dict, verdict: str, why: str | None, t0: float) -> dict:
    rec.update({"verdict": verdict, "why": why, "seconds": round(time.time() - t0, 1),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "atime": inv.atime_check()})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


MERGE_SAME = ("schema", "step", "code_sha256", "inputs", "calibration_sha256", "calibration_npz_sha256", "config_hash",
              "threads", "fd_1b_c2_source", "n")


def gate_merge(parts: list[dict]) -> dict:
    """The one gate record from the two per-truth records: every shared field identical, each truth once; PASS only if
    both truths' records are PASS. A per-truth STOP or INVALID is carried as it is."""
    if sorted(p.get("truth") for p in parts) != sorted(TRUTHS):
        raise Refusal(f"a merge needs one record per truth {TRUTHS}")
    verdicts = {p["truth"]: p["verdict"] for p in parts}
    same = {k: parts[0].get(k) for k in MERGE_SAME}
    if all(v == "PASS" for v in verdicts.values()):
        for k in MERGE_SAME:
            if any(p.get(k) != same[k] for p in parts):
                raise Refusal(f"the per-truth records differ in {k}")
        if any(p["record"]["vi"] != parts[0]["record"]["vi"] for p in parts):
            raise Refusal("the per-truth records differ in C2's (vi) row match")
    verdict = ("PASS" if all(v == "PASS" for v in verdicts.values()) else
               "INVALID" if any(v == "INVALID" for v in verdicts.values()) else "STOP")
    by = {p["truth"]: p for p in parts}
    return {"schema": SCHEMA_MERGED, "step": "ll5d-gate-merge", "verdict": verdict, "verdicts": verdicts,
            "reads": {e: v for t in TRUTHS for e, v in by[t].get("reads", {}).items()},
            "backstop": {e: v["passes"] for t in TRUTHS for e, v in by[t].get("backstop", {}).items()},
            "receipt": {t: by[t].get("receipt", {}).get("verdict") for t in TRUTHS},
            "shared": same if verdict == "PASS" else None}


# ------------------------------------------------------------------------------------------------------- main


def _common(p) -> None:
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "definition", "prep",
              "manifest", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    for k in ("pins", "flux-table", "manifest"):
        p.add_argument(f"--expect-{k}-sha256", required=True)
    p.add_argument("--time-limit-seconds", type=float, required=True, help="the job's --time, in seconds")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("calib")
    _common(p)
    p.add_argument("--draws", type=int, default=GATE_N)
    p.add_argument("--sets", type=int, default=CAL_SETS)
    p.add_argument("--workers", type=int, required=True)
    p.add_argument("--budget-seconds", type=float, required=True)
    p = sub.add_parser("gate")
    _common(p)
    p.add_argument("--truth", choices=TRUTHS, required=True)
    p.add_argument("--staged", type=Path, required=True)
    p.add_argument("--calibration", type=Path, required=True)
    p.add_argument("--expect-calibration-sha256", required=True)
    p.add_argument("--expect-calibration-npz-sha256", required=True)
    p = sub.add_parser("gate-merge")
    p.add_argument("--part", type=Path, action="append", required=True)
    p.add_argument("--expect-part-sha256", action="append", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise Refusal(f"refusing to overwrite {a.out}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    if a.cmd == "gate-merge":
        if len(a.part) != len(a.expect_part_sha256):
            raise Refusal("one --expect-part-sha256 per --part")
        parts = []
        for path, sha in zip(a.part, a.expect_part_sha256):
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != sha:
                raise Refusal(f"{path}: its digest is not the one given")
            parts.append(json.loads(raw))
        g = gate_merge(parts)
        g["merged_from"] = [{"truth": p["truth"], "sha256": s} for p, s in zip(parts, a.expect_part_sha256)]
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(g, indent=1, sort_keys=True))
        print(f"LL5D-GATE-MERGED verdict={g['verdict']} verdicts={json.dumps(g['verdicts'], sort_keys=True)}")
        return RC[g["verdict"]]
    step = "CALIBRATION" if a.cmd == "calib" else f"GATE {a.truth}"
    try:
        rec = calib_main(a) if a.cmd == "calib" else gate_main(a)
    except (Refusal, c2.Refusal, inv.Refusal, mc.Refusal, toys.Refusal) as exc:
        bad = {"schema": SCHEMA_CAL if a.cmd == "calib" else SCHEMA_GATE, "verdict": "INVALID", "why": str(exc),
               "atime": inv.atime_check()}
        a.out.with_suffix(".invalid.json").write_text(json.dumps(bad, indent=1, sort_keys=True))
        print(f"LL5D-{step} INVALID ({exc})")
        return RC["INVALID"] | (ATIME_RC if bad["atime"]["moved"] else 0)
    except Reprice as exc:
        bad = {"verdict": "REPRICE", "why": str(exc), "atime": inv.atime_check()}
        a.out.with_suffix(".reprice.json").write_text(json.dumps(bad, indent=1, sort_keys=True))
        print(f"LL5D-{step} REPRICE ({exc})")
        return RC["REPRICE"] | (ATIME_RC if bad["atime"]["moved"] else 0)
    verdict = rec["verdict"]
    moved = rec["atime"]["moved"]
    print(f"LL5D-{step} verdict={verdict}" + (f" atime_moved={len(moved)}" if moved else ""))
    code = RC.get(verdict, RC["TO_DIRECTOR"])
    return code | (ATIME_RC if moved else 0)


if __name__ == "__main__":
    sys.exit(main())

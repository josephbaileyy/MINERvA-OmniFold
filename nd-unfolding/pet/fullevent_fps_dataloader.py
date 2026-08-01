#!/usr/bin/env python3
"""Full-event PET DataLoader over the extended-FPS domain (KNOWN_ISSUES #19, P5A).

Replaces the recoil-only representation (`minerva_pet_dataloader.py`) with a full-event
one and pins the measurement domain to the extended full-phase-space (FPS) fiducial. The
PET classifier trains UNBINNED on CONTINUOUS features; the extended (pT, p_parallel) EDGES
are used ONLY for domain retention, reporting, covariance and validation -- NEVER as
classifier inputs or training bins (user directive 2026-07-16).

Representation (three explicit schemas; no manufactured counterparts):
  * reco cloud  : recoil tokens (E, pos, z, view, time). KNN neighborhood = detector geometry
                  (pos, z), NOT the first two columns by accident. Padding = energy(col 0)==0.
                  `view`/`time` are the G2 `*_view`/`*_time` per-token vectors, which the dump
                  pads under the SAME energy-descending permutation as (E,pos,z), so they are
                  token-aligned by construction (`dump_pointcloud_inputs.pad_reco_cloud_tokens`).
  * truth cloud : FS-hadron tokens (E, px, py, pz, pdg, theta, phi). KNN neighborhood =
                  angular direction (theta, phi). PDG retained (recoil-only loader dropped it);
                  a learned categorical embedding is the production refinement (documented).
  * event_reco / event_data  (SAME observable schema): the distinguished RECONSTRUCTED muon --
                  continuous [pT, p_parallel] PLUS the full muon object (px, py, pz, E, cos/sin
                  of phi, qp, MINOS match) and the reco vertex (x, y, z), read from the G2
                  `reco_muon`/`reco_vertex` and `data_muon`/`data_vertex` blocks. event_data uses
                  the DATA muon, event_reco the MC-reco muon. Detector/MINOS features are
                  step-1 only; NO truth counterpart is ever manufactured.
  * event_truth (DISTINCT schema, own normalization AND its own width): truth muon continuous
                  [pT, p_parallel] from `truth_scalars`. NO MINOS/range/quality/vertex, NO
                  sentinels -- those quantities do not exist at truth level and the dump carries
                  no truth counterpart for them (`fullevent_dump_contract.TRUTH_KEYS`).

WHY THE TWO WIDTHS DIFFER, AND WHY THAT IS THE POINT. Until 2026-08-01 both legs read the same
two columns and `meta["n_evt"]` was a single number. That made `DEFAULT_EVT_FEATURES =
("pt","pparallel")` -- the REDUCED `pet-reduced-fps-cross` schema, which
FULL_EVENT_FEATURE_CONTRACT.md marks "CROSS-CHECK ONLY -- never a publication lateral/central
source" -- the input to a driver stamping `pet-fullevent-fps-v1` (AUDIT-FINDINGS-20260731 J01).
The extension arrays were present in the dump and referenced nowhere. Reading them makes the two
schemas genuinely distinct, so `meta` now carries `n_evt_reco` and `n_evt_truth` and the caller
builds the step-1 and step-2 networks at different `num_evt`. `n_evt` is retained as an alias for
`n_evt_reco` for the recoil-era callers that assumed one width.

LEAKAGE INVARIANT (tested): event_reco/event_data carry only reconstructed/detector
quantities; a step-1 classifier never receives any truth-only quantity (truth muon, truth
vertex, PDG-mode, incoming-nu energy, ...). With distinct schemas this is enforced in two
places: `TRUTH_ELIGIBLE_FEATURES` refuses a detector feature on the truth leg at construction
time, and `assert_no_truth_leakage` proves event_reco is a pure function of the reco blocks.

This module's PURE functions (edge assertion, cloud/feature builders, leakage check) import
NO TensorFlow, so they are unit-testable on the login node. `build_fullevent_loaders` imports
the vendored DataLoader lazily.
"""
import argparse
import hashlib
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/omnifold_nn", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---- canonical extended FPS reporting grid (domain/reporting/covariance/validation only) ----
# EXACT arrays from the 2026-07-16 measurement-domain contract. Fail closed on paper edges.
CANONICAL_PT_EDGES = np.array(
    [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30.0],
    dtype=float)
CANONICAL_PPARALLEL_EDGES = np.array(
    [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0,
     40.0, 60.0, 120.0], dtype=float)
# Standard paper edges (for the fail-closed check): the FPS grid must NOT be the paper grid.
_PAPER_PT_MAX = 4.5      # paper pT top edge; FPS adds the [4.5,30] catch bin
_PAPER_PPAR_MIN = 1.5    # paper p|| bottom edge; FPS adds [0,0.75,1.5] low catch bins
_PAPER_PPAR_MAX = 60.0   # paper p|| top edge; FPS adds [60,120]

# scalar column order in reco_scalars/truth_scalars (SCALAR_AXES of the recoil-only loader)
SCALAR_COLS = {"pt": 0, "pparallel": 1, "eavail": 2, "q3": 3}
_SCALE = 1000.0          # MeV->GeV, mm->m (same O(1) rescale as the recoil-only loader)
# Recoil-token hit time is dumped in ns over a window of order +/-50; /1000 would push it to 1e-2
# while the energy column sits at O(1), so it gets its own O(1) rescale. View is a small integer
# code already at O(1) and is NOT rescaled -- dividing it by anything would collapse the three
# detector views onto each other numerically.
_TIME_SCALE = 100.0      # ns -> O(1)

# ---- G2 extension blocks: the exact column orders the dump writes -------------------------
# Mirrored from `dump_pointcloud_inputs.RECO_MUON_BRANCHES` / `RECO_VERTEX_BRANCHES`, which are
# what produced `G2_FPS_MEFHC_P12.npz`. Mirrored rather than imported because that module imports
# ROOT at use time and this one must stay login-safe; `test_fullevent_schema.py` reads the dumper's
# SOURCE and fails if the two orders drift apart, so the mirror cannot go stale silently. The same
# orders apply to the `data_*` and `bkg_*` twins -- the dumper fills all three from one
# `_reco_row` helper.
MUON_COLS = {"mu_px": 0, "mu_py": 1, "mu_pz": 2, "mu_E": 3, "mu_phi": 4, "mu_qp": 5,
             "mu_minos_ok": 6}
VERTEX_COLS = {"vtx_x": 0, "vtx_y": 1, "vtx_z": 2}
N_MUON_COLS = len(MUON_COLS)        # 7
N_VERTEX_COLS = len(VERTEX_COLS)    # 3
# The dump's !pass_reco marker in reco_scalars / reco_muon / reco_vertex (there is no
# reconstructed muon on a native truth-only miss). Never a feature value: those rows are excluded
# from every normalization statistic and zeroed afterwards.
SENTINEL = -9999.0


def assert_extended_fps_edges(edges_pt, edges_pparallel, tol=1e-9):
    """Fail closed unless the supplied edges are EXACTLY the canonical extended FPS grid.

    Rejects the standard paper grid (which would silently measure the restricted domain)
    and any reordering. This is the measurement-domain guard for every consumer that
    reconstructs or reports on the truth gate."""
    edges_pt = np.asarray(edges_pt, float)
    edges_pparallel = np.asarray(edges_pparallel, float)
    if edges_pt.shape != CANONICAL_PT_EDGES.shape or \
       not np.allclose(edges_pt, CANONICAL_PT_EDGES, atol=tol, rtol=0):
        raise ValueError(
            f"[FPS-GUARD] pT edges are not the canonical extended FPS grid.\n"
            f"  got      = {edges_pt.tolist()}\n  expected = {CANONICAL_PT_EDGES.tolist()}")
    if edges_pparallel.shape != CANONICAL_PPARALLEL_EDGES.shape or \
       not np.allclose(edges_pparallel, CANONICAL_PPARALLEL_EDGES, atol=tol, rtol=0):
        raise ValueError(
            f"[FPS-GUARD] p_parallel edges are not the canonical extended FPS grid.\n"
            f"  got      = {edges_pparallel.tolist()}\n  expected = {CANONICAL_PPARALLEL_EDGES.tolist()}")
    # explicit paper-grid rejection (belt-and-braces: extended grid must exceed paper bounds)
    if abs(edges_pt[-1] - _PAPER_PT_MAX) < tol:
        raise ValueError("[FPS-GUARD] pT top edge == paper 4.5 GeV; standard grid supplied.")
    if abs(edges_pparallel[0] - _PAPER_PPAR_MIN) < tol:
        raise ValueError("[FPS-GUARD] p_parallel bottom edge == paper 1.5 GeV; standard grid supplied.")
    return True


def _scale_clean(a):
    """MeV->GeV / mm->m, non-finite -> 0 (0 is the PET energy-mask/pad sentinel)."""
    return np.nan_to_num(np.asarray(a, np.float32) / _SCALE, nan=0.0, posinf=0.0, neginf=0.0)


RECO_CLOUD_COLS = ("E", "pos", "z", "view", "time")


def build_reco_cloud(part_reco, view=None, time=None):
    """Recoil reco cloud scaled to O(1). Returns (cloud, coord_idx).

    (N,P,3) = (E, pos, z) when `view`/`time` are omitted -- the recoil-era shape, kept so the
    pure-function callers that hold only a cloud (feature_rank_arms' cached arms, the unit tests)
    keep working. With the G2 per-token `*_view` (1=X/2=U/3=V) and `*_time` (ns) vectors supplied
    the cloud is (N,P,5) = (E, pos, z, view, time). coord_idx is (1,2) either way => the KNN
    neighborhood stays the (pos, z) detector geometry; view and time are carried as token
    FEATURES, not as neighborhood coordinates, because a hit's view is a categorical detector
    plane and adjacency in it is not a distance.

    WHY THE CLOUD AND NOT THE EVENT BLOCK. `*_view`/`*_time` are per-token vectors whose length
    the dump contract pins to the cloud's token dimension P
    (`fullevent_dump_contract.assert_inventory_alignment`), and the dumper pads them under the
    SAME energy-descending permutation as (E,pos,z). Summarizing them into event scalars would
    discard exactly the per-hit structure they were requested for
    (FULL_EVENT_INTERFACE_REQUEST.md §B).

    PAD DISCIPLINE. Padded tokens are re-zeroed in view/time from the energy mask rather than
    trusted: the pad sentinel the model keys on is energy(col 0)==0, and a dump that padded the
    parallel vectors separately would otherwise leave a nonzero view/time on a token the network
    treats as absent.
    """
    cloud = _scale_clean(part_reco)          # (N, P, 3) = E, pos, z
    if view is None and time is None:
        return cloud, (1, 2)
    if view is None or time is None:
        raise ValueError("[G2] build_reco_cloud needs BOTH view and time or neither; got "
                         f"view={'set' if view is not None else 'None'}, "
                         f"time={'set' if time is not None else 'None'} (fail closed)")
    v = np.nan_to_num(np.asarray(view, np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    t = np.nan_to_num(np.asarray(time, np.float32) / _TIME_SCALE,
                      nan=0.0, posinf=0.0, neginf=0.0)
    if v.shape != cloud.shape[:2] or t.shape != cloud.shape[:2]:
        raise ValueError(f"[G2] view {v.shape} / time {t.shape} are not token-aligned to the "
                         f"cloud {cloud.shape[:2]} (fail closed)")
    real = cloud[:, :, 0] != 0.0             # the energy pad mask, the only pad authority
    v = np.where(real, v, 0.0).astype(np.float32)
    t = np.where(real, t, 0.0).astype(np.float32)
    return np.concatenate([cloud, v[..., None], t[..., None]], axis=-1), (1, 2)


def build_truth_cloud(part_gen):
    """Truth FS-hadron cloud with PDG retained + explicit angular KNN coordinates appended.

    Input part_gen (N,P,5) = (E,px,py,pz,pdg). Output (N,P,8) =
      (E/GeV, px/GeV, py/GeV, pz/GeV, pdg, theta, cos_phi, sin_phi)
    with coord_idx=(5,6,7) => KNN neighborhood = angular direction (theta, cos_phi, sin_phi).
    Azimuth is encoded as (cos_phi, sin_phi) so the neighborhood is PERIODIC-correct: raw phi
    would place phi=-pi and phi=+pi maximally far apart although they are adjacent (CLM-008 F10).
    Padded tokens (E==0) get all appended coords 0 and are pushed away by the model's
    coord_shift mask, so the energy(col0) pad mask still holds.
    """
    part_gen = np.asarray(part_gen, np.float32)
    E   = part_gen[:, :, 0]
    px, py, pz = part_gen[:, :, 1], part_gen[:, :, 2], part_gen[:, :, 3]
    pdg = part_gen[:, :, 4]
    pt = np.hypot(px, py)
    theta = np.arctan2(pt, pz)               # polar angle wrt beam (rad), [0,pi] (not periodic)
    phi = np.arctan2(py, px)                 # azimuth (rad); encoded periodically below
    valid = E != 0                           # real tokens
    theta = np.where(valid, theta, 0.0).astype(np.float32)
    cphi = np.where(valid, np.cos(phi), 0.0).astype(np.float32)
    sphi = np.where(valid, np.sin(phi), 0.0).astype(np.float32)
    kin = _scale_clean(np.stack([E, px, py, pz], axis=-1))     # (N,P,4) GeV, pad-preserving
    pdg = np.where(valid, pdg, 0.0).astype(np.float32)         # keep raw PDG (embed in prod)
    cloud = np.concatenate([kin, pdg[..., None], theta[..., None],
                            cphi[..., None], sphi[..., None]], axis=-1)
    return cloud.astype(np.float32), (5, 6, 7)


# ============================================================================================
# Event-feature spec: which CONTINUOUS quantities form the distinguished-muon/context block.
# ============================================================================================
# Each name resolves to (source block, column, transform). `scalars` is reco_scalars /
# truth_scalars / measured_scalars / bkg_reco_scalars; `muon` is reco_muon / data_muon /
# bkg_muon; `vertex` is reco_vertex / data_vertex / bkg_vertex.
#
# Transforms are unit conversions, not modelling choices -- every column is z-normalized
# downstream, so they change the recorded `*_norm_mean` into readable GeV/m and nothing else.
# The one exception is the azimuth, which is NOT a scale:
#
#   PERIODICITY. mu_phi is dumped as a raw angle in (-pi, pi]. z-scoring a raw angle puts
#   phi = -pi and phi = +pi at opposite ends of the feature while they are the same direction,
#   so the network has to learn to glue the ends together and cannot. It is encoded as the pair
#   (cos phi, sin phi) instead -- the same fix CLM-008 F10 applied to the truth cloud's KNN
#   coordinates in `build_truth_cloud`, for the same reason, one level up.
_EVT_SPEC = {
    # name              (block,     column,                      transform)
    "pt":               ("scalars", SCALAR_COLS["pt"],           "as_is"),    # already GeV
    "pparallel":        ("scalars", SCALAR_COLS["pparallel"],    "as_is"),    # already GeV
    "eavail":           ("scalars", SCALAR_COLS["eavail"],       "as_is"),
    "q3":               ("scalars", SCALAR_COLS["q3"],           "as_is"),
    "mu_px":            ("muon",    MUON_COLS["mu_px"],          "div_scale"),   # MeV -> GeV
    "mu_py":            ("muon",    MUON_COLS["mu_py"],          "div_scale"),
    "mu_pz":            ("muon",    MUON_COLS["mu_pz"],          "div_scale"),
    "mu_E":             ("muon",    MUON_COLS["mu_E"],           "div_scale"),
    "mu_cos_phi":       ("muon",    MUON_COLS["mu_phi"],         "cos"),
    "mu_sin_phi":       ("muon",    MUON_COLS["mu_phi"],         "sin"),
    # qp = charge/momentum, so it takes the RECIPROCAL of the momentum convention: MeV^-1 -> GeV^-1.
    # Not cosmetic. Raw q/p is O(1e-4 / MeV), and the +1e-6 floor added to every column's standard
    # deviation would then be a ~1% squeeze on this column alone rather than the negligible guard
    # against division by zero it is everywhere else.
    "mu_qp":            ("muon",    MUON_COLS["mu_qp"],          "mul_scale"),
    "mu_minos_ok":      ("muon",    MUON_COLS["mu_minos_ok"],    "as_is"),    # 0/1 match flag
    "vtx_x":            ("vertex",  VERTEX_COLS["vtx_x"],        "div_scale"),   # mm -> m
    "vtx_y":            ("vertex",  VERTEX_COLS["vtx_y"],        "div_scale"),
    "vtx_z":            ("vertex",  VERTEX_COLS["vtx_z"],        "div_scale"),
}

# Features that EXIST at truth level. `truth_scalars` is the only truth-side event array the G2
# dump carries (`fullevent_dump_contract.TRUTH_KEYS` is `("part_gen",)`; the truth muon is
# summarized into truth_scalars); there is no truth muon object, no truth vertex, and by
# construction no truth MINOS/view/timing. Requesting anything else on the truth leg is a
# leakage attempt, not a configuration, and is refused at construction time.
TRUTH_ELIGIBLE_FEATURES = frozenset(n for n, (blk, _c, _t) in _EVT_SPEC.items() if blk == "scalars")
DETECTOR_ONLY_FEATURES = frozenset(_EVT_SPEC) - TRUTH_ELIGIBLE_FEATURES

# THE FULL publication schema (`pet-fullevent-fps-v1`): reported muon coordinates + the full
# reconstructed muon object + the reco vertex. pT and p_parallel are retained alongside the
# 4-vector they are derivable from -- deliberately. They are the reported observables, the
# quantities the extended-FPS domain gate is defined on, and the ones the -9999 miss convention is
# documented against; keeping them also makes the reduced cross-check schema a literal SUBSET of
# this one, so `pet-reduced-fps-cross` is a true ablation of the same code path rather than a
# different one.
#
# NOT here, deliberately: `eavail` and `q3`. They are dumped on both legs and unread, and whether
# they earn their place is the open measurement of RESTORE-2026-08-03.md Step 7 (the
# base/eavail/q3/both arms). Adding them on the way past would prejudge that with no evidence,
# and unlike the muon object they are not what `pet-fullevent-fps-v1` claims.
DEFAULT_EVT_FEATURES = (
    "pt", "pparallel",
    "mu_px", "mu_py", "mu_pz", "mu_E", "mu_cos_phi", "mu_sin_phi", "mu_qp", "mu_minos_ok",
    "vtx_x", "vtx_y", "vtx_z",
)
# The truth leg's own schema. Same NAMES as the reco leg's first two, its OWN normalization
# statistic, and a different width.
DEFAULT_TRUTH_EVT_FEATURES = ("pt", "pparallel")
# The reduced `pet-reduced-fps-cross` estimator, named so a cross-check run selects it by
# contract ID instead of by retyping a tuple. NEVER a publication central/lateral source.
REDUCED_EVT_FEATURES = ("pt", "pparallel")


def evt_blocks(scalars=None, muon=None, vertex=None):
    """Bundle one inventory's event-feature source arrays. Missing blocks stay None and are
    reported by name if a requested feature needs them."""
    return {"scalars": scalars, "muon": muon, "vertex": vertex}


def assert_evt_block_widths(blocks, label):
    """Fail closed unless the supplied muon/vertex blocks have the dump's column count.

    `fullevent_dump_contract.assert_inventory_alignment` checks these blocks' ROW counts and the
    view/time token length, but never their width, so a 6-column muon satisfies every G2 gate and
    then silently means something else here -- `make_synthetic_g2_fullevent.py` carried exactly
    that (a 6-col [px,py,pz,E,charge,quality] placeholder against the dumper's 7-col
    [px,py,pz,E,phi,qp,minos_ok]) for as long as nothing read the block. Reading it makes the
    width load-bearing, so it is checked where it is consumed."""
    for key, want in (("muon", N_MUON_COLS), ("vertex", N_VERTEX_COLS)):
        arr = blocks.get(key)
        if arr is None:
            continue
        arr = np.asarray(arr)
        if arr.ndim != 2 or arr.shape[1] != want:
            raise ValueError(
                f"[G2-SCHEMA] {label}: '{key}' block has shape {arr.shape}, expected (N, {want}) "
                f"-- the G2 column order is "
                f"{sorted(MUON_COLS, key=MUON_COLS.get) if key == 'muon' else sorted(VERTEX_COLS, key=VERTEX_COLS.get)}"
                " (dump_pointcloud_inputs.py). Fail closed: a wrong width silently remaps every "
                "column of this block onto a different physical quantity.")
    return True


def _evt_column(name, blocks, label):
    """Resolve ONE event feature to a 1-D float32 column from its source block."""
    try:
        block_key, col, transform = _EVT_SPEC[name]
    except KeyError:
        raise ValueError(
            f"[EVT-SCHEMA] unknown event feature {name!r}; known: {sorted(_EVT_SPEC)}") from None
    arr = blocks.get(block_key)
    if arr is None:
        raise ValueError(
            f"[EVT-SCHEMA] {label}: feature {name!r} needs the '{block_key}' block and none was "
            f"supplied. The G2 dump carries it; refusing to silently drop the feature or fall "
            f"back to a narrower schema (that is how a reduced estimator came to be stamped "
            f"`pet-fullevent-fps-v1` -- AUDIT-FINDINGS-20260731 J01).")
    v = np.asarray(arr, np.float32)[:, col]
    if transform == "div_scale":
        v = v / _SCALE
    elif transform == "mul_scale":
        v = v * _SCALE
    elif transform == "cos":
        v = np.cos(v.astype(np.float64))
    elif transform == "sin":
        v = np.sin(v.astype(np.float64))
    elif transform != "as_is":
        raise ValueError(f"[EVT-SCHEMA] unknown transform {transform!r} for {name!r}")
    return np.asarray(v, np.float32)


def _event_block(blocks, feature_names, norm):
    """Assemble + normalize a continuous event-feature block from one inventory's source arrays.

    `blocks` is an `evt_blocks(...)` mapping; a bare (N, ncol) array is accepted as shorthand for
    a scalars-only inventory so the scalar-schema callers read unchanged."""
    if not isinstance(blocks, dict):
        blocks = evt_blocks(scalars=blocks)
    block = np.column_stack([_evt_column(f, blocks, "event block") for f in feature_names]) \
        if feature_names else np.zeros((0, 0), np.float32)
    block = np.asarray(block, np.float32)
    if norm is not None:
        mu, sd = norm
        block = (block - np.asarray(mu, np.float32)) / np.asarray(sd, np.float32)
    return block.astype(np.float32)


def assert_finite_event_scalars(blocks, feature_names, mask, label):
    """FAIL CLOSED, naming the column, on any non-finite value in a SELECTED event-feature column.

    FINDING-20260730-event-feature-nonfinite.md (found by execution: Delta job 20599606 died on it
    after 49m45s). `_event_block` computes the normalization from the in-mask rows of the selected
    columns, so ONE non-finite entry makes `mu`/`sd` NaN and turns the ENTIRE column NaN for EVERY
    row -- step 1 trains fine off the clean reco leg and step 2 reports `Last val loss nan`, naming
    neither the column nor the cause. `truth_scalars` `q3` carries 14 such rows per 400,000
    (~1,700 in the full 49,152,885-row inventory).

    The existing guard cannot catch it: `assert_no_truth_leakage` asserts the reco and truth blocks
    are NOT allclose, and NaN compares unequal to everything, so an all-NaN block passes.

    NOT `nan_to_num`. 0 is the cloud path's pad/mask sentinel but the BLOCK MEAN of a z-scored event
    feature, so quiet filling would place undefined events at the centre of the conditioning
    distribution -- biasing the estimator instead of announcing a bad dump. Latent while the adopted
    schema read cols 0,1 (both clean on both legs); LIVE as of 2026-08-01, because the block has
    widened to the muon object and vertex -- which is exactly the condition this guard was written
    against (FULL_EVENT_FEATURE_CONTRACT.md:98-101).

    `blocks` is an `evt_blocks(...)` mapping, or a bare scalar array for a scalars-only schema."""
    if not isinstance(blocks, dict):
        blocks = evt_blocks(scalars=blocks)
    n = None
    for arr in blocks.values():
        if arr is not None:
            n = int(np.asarray(arr).shape[0])
            break
    if n is None:
        raise ValueError(f"[EVT-FINITE] {label}: no event-feature source blocks supplied")
    m = np.ones(n, bool) if mask is None else np.asarray(mask, bool)
    offenders = []
    for name in feature_names:
        col = _evt_column(name, blocks, label)[m]
        bad = int((~np.isfinite(col)).sum())
        if bad:
            src, idx, _t = _EVT_SPEC[name]
            offenders.append(f"{name} ({src} column {idx}): {bad} non-finite")
    if offenders:
        raise ValueError(
            f"[EVT-FINITE] {label}: non-finite values in selected event-feature column(s) over "
            f"{int(m.sum())} in-mask rows -- {'; '.join(offenders)}. ONE such value NaNs the whole "
            "column for every row via the normalization statistic and trains step 2 to `Last val "
            "loss nan`. Fail closed: fix the dump (or drop the column from the schema). Do NOT "
            "nan_to_num -- 0 is the block mean here, not a pad sentinel. "
            "See docs/orchestration/FINDING-20260730-event-feature-nonfinite.md")
    return True


def _degenerate_columns(feature_names, sd):
    """Names of z-scored columns whose in-mask spread is numerically zero.

    Reported, NOT failed. A constant column is a legitimate outcome of a selection cut --
    `mu_minos_ok` is 1 for every pass_reco row if the selection requires a MINOS match -- and
    failing the publication nominal over a wasted input dimension would be a false alarm. But it
    is worth seeing in the receipt for the opposite reason: a feature that is constant on ONE leg
    and not the other is a pure data/MC label, and step 1 will find it."""
    sd = np.asarray(sd, np.float64)
    return [feature_names[j] for j in range(len(feature_names)) if sd[j] <= 1e-6 * (1.0 + 1e-9)]


def assert_truth_schema_is_eligible(truth_feature_names):
    """Refuse a detector-only quantity on the TRUTH leg, by name, before anything is built.

    With one shared feature list this was unrepresentable. With distinct schemas it becomes the
    single cheapest place to enforce the contract's "no manufactured counterparts" rule: the
    truth leg may only read quantities that exist at truth level, and a MINOS match flag, a reco
    vertex or a reconstructed muon momentum is not one of them. This is a stronger statement than
    `assert_no_truth_leakage`, which can only compare the blocks that were actually built."""
    bad = [n for n in truth_feature_names if n not in TRUTH_ELIGIBLE_FEATURES]
    if bad:
        raise ValueError(
            f"[EVT-SCHEMA] detector-only feature(s) {bad} requested for event_truth. These have "
            "NO truth counterpart in the G2 dump and manufacturing one is forbidden "
            "(FULL_EVENT_FEATURE_CONTRACT.md 'Unavailable counterparts'). Truth-eligible: "
            f"{sorted(TRUTH_ELIGIBLE_FEATURES)}.")
    return True


def build_event_features(reco_blocks, truth_blocks, measured_blocks,
                         feature_names=DEFAULT_EVT_FEATURES,
                         pass_reco=None, pass_truth=None,
                         truth_feature_names=DEFAULT_TRUTH_EVT_FEATURES):
    """Return (event_reco, event_truth, event_data, meta).

    event_reco/event_data share the SAME observable feature schema (the reconstructed muon object
    + reco vertex); event_truth has its OWN, NARROWER schema (`truth_feature_names`), its own
    normalization statistic, and therefore its own width. All continuous.

    Each `*_blocks` argument is an `evt_blocks(scalars=, muon=, vertex=)` mapping for one
    inventory, or a bare (N, ncol) scalar array when the requested schema is scalars-only.

    SENTINEL HANDLING (critical): the reconstructed muon is UNDEFINED for events that fail
    reco -- FPS misses carry -9999 in reco_scalars AND, since the extension arrays landed, in
    reco_muon/reco_vertex too (`dump_pointcloud_inputs.reco_muon_row` / `reco_vertex_row`, with
    minos_ok = 0 rather than -9999). The normalization is therefore computed over pass_reco
    events ONLY (truth over pass_truth ONLY), and the undefined (!pass_reco) reco rows are set to
    0 post-normalization (the block mean). Those rows are masked by pass_reco in the step-1 loss,
    so zeroing keeps them numerically neutral without injecting the sentinel. This also keeps the
    reco-side normalization a pure detector statistic (no truth leakage). Widening the block did
    not weaken this: every added column carries the same sentinel on the same rows.
    """
    if not isinstance(reco_blocks, dict):
        reco_blocks = evt_blocks(scalars=reco_blocks)
    if not isinstance(truth_blocks, dict):
        truth_blocks = evt_blocks(scalars=truth_blocks)
    if not isinstance(measured_blocks, dict):
        measured_blocks = evt_blocks(scalars=measured_blocks)
    assert_truth_schema_is_eligible(truth_feature_names)
    assert_evt_block_widths(reco_blocks, "reco (signal MC)")
    assert_evt_block_widths(measured_blocks, "measured (data)")

    n_reco = int(np.asarray(reco_blocks["scalars"]).shape[0])
    n_truth = int(np.asarray(truth_blocks["scalars"]).shape[0])
    rmask = np.ones(n_reco, bool) if pass_reco is None else np.asarray(pass_reco, bool)
    tmask = np.ones(n_truth, bool) if pass_truth is None else np.asarray(pass_truth, bool)
    # Row alignment across an inventory's own blocks: a muon array from a different dump would
    # otherwise pair muon row i with cloud row i and be silently wrong rather than loudly wrong.
    for blocks, n, label in ((reco_blocks, n_reco, "reco"), (truth_blocks, n_truth, "truth"),
                             (measured_blocks, None, "measured")):
        rows = {k: int(np.asarray(v).shape[0]) for k, v in blocks.items() if v is not None}
        if len(set(rows.values())) > 1:
            raise ValueError(f"[EVT-SCHEMA] {label} event-feature blocks are not row-aligned: "
                             f"{rows} (fail closed)")
        if n is not None and set(rows.values()) != {n}:
            raise ValueError(f"[EVT-SCHEMA] {label} blocks {rows} disagree with the scalars' "
                             f"{n} rows (fail closed)")
    # FINDING-20260730: screen BEFORE the normalization statistics are formed, on the exact rows
    # that form them, so the error names the offending column instead of surfacing as a NaN loss.
    assert_finite_event_scalars(reco_blocks, feature_names, rmask, "reco_scalars over pass_reco")
    assert_finite_event_scalars(truth_blocks, truth_feature_names, tmask,
                                "truth_scalars over pass_truth")
    assert_finite_event_scalars(measured_blocks, feature_names, None,
                                "measured_scalars (data; all rows pass_reco)")
    rsub = _event_block(reco_blocks, feature_names, None)[rmask]
    tsub = _event_block(truth_blocks, truth_feature_names, None)[tmask]
    rmu = rsub.mean(0); rsd = rsub.std(0) + 1e-6
    tmu = tsub.mean(0); tsd = tsub.std(0) + 1e-6
    event_reco = _event_block(reco_blocks, feature_names, (rmu, rsd)); event_reco[~rmask] = 0.0
    event_truth = _event_block(truth_blocks, truth_feature_names, (tmu, tsd))
    event_truth[~tmask] = 0.0
    event_data = _event_block(measured_blocks, feature_names, (rmu, rsd))  # data all pass_reco
    # Belt-and-braces on the built blocks: a degenerate (all-equal) column survives the +1e-6 on sd,
    # but nothing downstream inspects these arrays for finiteness and a NaN block is what cost
    # 49m45s of Delta once. Cheap relative to the training that follows.
    for _blk, _lbl in ((event_reco, "event_reco"), (event_truth, "event_truth"),
                       (event_data, "event_data")):
        if not np.all(np.isfinite(_blk)):
            raise ValueError(
                f"[EVT-FINITE] normalized {_lbl} block contains non-finite values even though the "
                "input columns were finite -- a degenerate normalization statistic (fail closed).")
    meta = {"feature_names": list(feature_names),
            "truth_feature_names": list(truth_feature_names),
            "reco_norm_mean": rmu.tolist(), "reco_norm_std": rsd.tolist(),
            "truth_norm_mean": tmu.tolist(), "truth_norm_std": tsd.tolist(),
            "n_evt_reco": len(feature_names), "n_evt_truth": len(truth_feature_names),
            # Back-compat alias for the recoil-era callers that assumed one width. The two legs
            # now differ, so a caller reading this for the STEP-2 network is wrong; every
            # in-tree caller was moved to the explicit pair.
            "n_evt": len(feature_names),
            "degenerate_reco_columns": _degenerate_columns(list(feature_names), rsd),
            "degenerate_truth_columns": _degenerate_columns(list(truth_feature_names), tsd),
            "normalized_over": "pass_reco (reco/data) / pass_truth (truth); !pass rows zeroed"}
    return event_reco, event_truth, event_data, meta


def assert_no_truth_leakage(event_reco, reco_blocks, truth_blocks, feature_names,
                            pass_reco=None, truth_feature_names=DEFAULT_TRUTH_EVT_FEATURES):
    """Prove event_reco is a function of the RECO blocks (+ pass_reco) ONLY, no truth-only info.

    Three statements, because with distinct schemas one is no longer enough:

      1. SCHEMA. No feature in the reco list is one the truth leg is allowed to read back, and
         no feature in the truth list is detector-only. (`assert_truth_schema_is_eligible`.)
      2. PURITY. Rebuild event_reco from the reco blocks alone -- same pass_reco-masked
         normalization, same !pass zeroing -- and require an exact match. Anything the truth
         arrays contributed would show up here.
      3. DISSIMILARITY, on the comparable columns only. The original guard required event_reco
         not to equal "the truth block"; that comparison is shape-invalid now that the two
         schemas have different widths, and skipping it would quietly retire the check. It is
         instead restricted to the feature names the two legs SHARE (pT, p_parallel), which is
         the whole set on which a truth-for-reco substitution is even expressible.
    """
    if not isinstance(reco_blocks, dict):
        reco_blocks = evt_blocks(scalars=reco_blocks)
    if not isinstance(truth_blocks, dict):
        truth_blocks = evt_blocks(scalars=truth_blocks)
    assert_truth_schema_is_eligible(truth_feature_names)
    n_reco = int(np.asarray(reco_blocks["scalars"]).shape[0])
    rmask = np.ones(n_reco, bool) if pass_reco is None else np.asarray(pass_reco, bool)
    raw = _event_block(reco_blocks, feature_names, None)
    rmu = raw[rmask].mean(0); rsd = raw[rmask].std(0) + 1e-6
    rebuilt = _event_block(reco_blocks, feature_names, (rmu, rsd)); rebuilt[~rmask] = 0.0
    # FINDING-20260730 fix (2): this guard is a DISSIMILARITY test, and NaN is maximally dissimilar,
    # so an all-NaN block used to sail through it. Finiteness first, or the leakage verdict is
    # meaningless.
    if not np.all(np.isfinite(event_reco)):
        raise AssertionError(
            f"[EVT-FINITE] event_reco has {int((~np.isfinite(event_reco)).sum())} non-finite "
            "entries; the no-truth-leakage comparison below is a dissimilarity test and NaN differs "
            "from everything, so it would PASS on a poisoned block (fail closed).")
    if not np.allclose(rebuilt, event_reco, atol=1e-5):
        raise AssertionError("event_reco is NOT a pure function of the reco blocks+pass_reco (leak?)")
    shared = [f for f in feature_names if f in set(truth_feature_names)]
    if shared:
        take = [list(feature_names).index(f) for f in shared]
        tsh = _event_block(truth_blocks, shared, (rmu[take], rsd[take])); tsh[~rmask] = 0.0
        if np.allclose(tsh, event_reco[:, take], atol=1e-5):
            raise AssertionError(
                f"event_reco columns {shared} equal the TRUTH block built on the same names -- "
                "truth leaked into step 1")
    return True


# ============================================================================================
# F7 — coherent estimator-bootstrap over THREE inventories (data, signal-MC, background-MC)
# ============================================================================================
# Locked user decision (2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md, 2026-07-11):
# FPS/N-D/PET nominal = NEGWEIGHT + Stay-Positive; PET = Option A LITERAL background-cloud
# injection. Purity is a matched REGRESSION CONTROL, never the publication nominal. The
# coherent bootstrap therefore fluctuates all THREE inventories, and the negweight-refined
# measured target is rebuilt PER REPLICA from the fluctuated data + background — never copied
# from the nominal. Contract (P5B C_stat hard gate):
#   1. draw ONE global Poisson(1) factor per inventory over the FULL stable inventory BEFORE any
#      training subset (never a post-subset redraw);
#   2. the BACKGROUND factor multiplies the NEGATIVE POT-scaled injection weight BEFORE the
#      Stay-Positive refinement;
#   3. persist per-category factors, seeds, inventory-order hashes, and the estimator fingerprint;
#   4. re-consume the SAME signal + background draws in training, target construction, and
#      extraction; fail closed on inventory/order/fingerprint mismatch.
# The pure functions below are TensorFlow-free and login-testable. The Stay-Positive refinement
# here is the closed-form binned realization (arXiv:2505.03724 eq 6) used for the coherence
# regression tests; production uses the trained refine_stay_positive classifier.

def inventory_order_hash(*arrays):
    """Stable SHA256 over truth-invariant ordered array bytes = inventory identity/order
    evidence. The FPS ROOTs carry NO stable event keys, so this hash is how training and
    extraction prove they consume the SAME inventory in the SAME order."""
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(np.asarray(a))
        h.update(str(a.dtype).encode()); h.update(repr(a.shape).encode()); h.update(a.tobytes())
    return h.hexdigest()


def _verify_stored_identity(d, key, evidence_arrays, label):
    """Recompute an inventory's identity/order hash from its stable-order evidence and require it to
    equal the value the G2 dump persisted. Fail closed on a missing or mismatched (reordered/wrong)
    inventory. Runs where arrays are materialized (compute node / tiny fixtures), never on the login
    node against the full NPZ. Returns the verified hash string."""
    files = set(d.files) if hasattr(d, "files") else set(d)
    if key not in files:
        raise ValueError(f"[G2-IDENTITY] input missing stored '{key}' (old schema; fail closed)")
    want = inventory_order_hash(*[np.asarray(a) for a in evidence_arrays])
    got = str(np.asarray(d[key]).item() if hasattr(d[key], "item") else d[key])
    if got != want:
        raise ValueError(f"[G2-IDENTITY] {label} identity mismatch ({key}): stored != recomputed "
                         "(reordered/tampered/wrong inventory; fail closed)")
    return got


def coherent_bootstrap_factors(n_data, n_sig, n_bkg, seed):
    """Three GLOBAL Poisson(1) factors over the full data / signal-MC / background-MC
    inventories, drawn BEFORE any subset (F7 step 1). Distinct reproducible streams; the signal
    stream reuses the canonical pet_bootstrap.mc_poisson_factor (rng(seed+10_000_000)) so the
    full-event contract is bit-consistent with the recoil-only replica contract.
    Returns (data_factor, sig_factor, bkg_factor) uint8."""
    from pet_bootstrap import mc_poisson_factor
    data_factor = np.random.default_rng(int(seed)).poisson(1.0, int(n_data)).astype(np.uint8)
    sig_factor = mc_poisson_factor(int(n_sig), int(seed))
    bkg_factor = np.random.default_rng(int(seed) + 20_000_000).poisson(
        1.0, int(n_bkg)).astype(np.uint8)
    return data_factor, sig_factor, bkg_factor


def stay_positive_refine_binned(signed_w, cell, n_cells):
    """Closed-form binned Stay-Positive (arXiv:2505.03724 eq 6): refine a signed measured sample
    into NON-negative weights. Per cell g = D/(D+B), D=sum(+w), B=sum(|-w|); w~ = |w|*(2g-1)
    clipped at 0 (=> non-negative; sums to D-B per cell). Production uses the trained classifier
    (u2d.refine_stay_positive); this pure form backs the coherence tests."""
    signed_w = np.asarray(signed_w, float); cell = np.asarray(cell)
    pos = np.clip(signed_w, 0.0, None); neg = np.clip(-signed_w, 0.0, None)
    D = np.bincount(cell, pos, minlength=n_cells)
    B = np.bincount(cell, neg, minlength=n_cells)
    denom = D + B
    g = np.divide(D, denom, out=np.full(n_cells, 0.5), where=denom > 0)
    return np.clip(np.abs(signed_w) * (2.0 * g[cell] - 1.0), 0.0, None)


def build_negweight_refined_target(data_cell, bkg_cell, w_bkg, pot_scale, n_cells,
                                   data_factor, bkg_factor):
    """Build ONE replica's negweight-refined measured target from the coherent draws (F7 step 2).
    Signed measured sample = data(+data_factor) ++ background(-w_bkg*pot_scale*bkg_factor); the
    BACKGROUND FACTOR multiplies the negative injection weight BEFORE the Stay-Positive refine.
    Returns (refined_data_w, refined_bkg_w), both non-negative. Rebuilt per replica (never copied
    from nominal): a different bkg_factor yields a different refined target by construction."""
    data_signed = np.asarray(data_factor, float)                              # +1 * data_factor
    bkg_signed = -(np.asarray(w_bkg, float) * float(pot_scale)) * np.asarray(bkg_factor, float)
    signed = np.concatenate([data_signed, bkg_signed])
    cell = np.concatenate([np.asarray(data_cell), np.asarray(bkg_cell)])
    refined = stay_positive_refine_binned(signed, cell, int(n_cells))
    return refined[:len(data_signed)], refined[len(data_signed):]


# --------------------------------------------------------------------------------------------
# Gate-2 negweight-refined CONSTRUCTION (Option-A literal background injection + Stay-Positive).
# The binned `stay_positive_refine_binned` above is FIXTURE-ONLY (needs a pre-assigned cell index;
# it backs the coherence/independent cross-check tests). PRODUCTION refinement is the LEARNED
# UNBINNED classifier `unfold_2d_omnifold_unbinned.refine_stay_positive` on CONTINUOUS reco
# features (the locked ND/PET method, arXiv:2505.03724). It is wired here via a DEFERRED import +
# injectable `refine_fn` because u2d imports ROOT/TF at module load (segfaults on the login node),
# so the canonical learned call runs at RUNTIME on a compute node; the login-safe tests inject an
# algorithm-identical sklearn refinement to validate the construction/alignment/telemetry.
# --------------------------------------------------------------------------------------------
def learned_stay_positive_refiner():
    """Deferred handle to the CANONICAL learned Stay-Positive refinement (u2d.refine_stay_positive).
    Lazy because unfold_2d_omnifold_unbinned imports ROOT/TF at module load; runtime/compute-node
    only (NOT importable on the login node)."""
    from unfold_2d_omnifold_unbinned import refine_stay_positive
    return refine_stay_positive


def build_signed_measured_inventory(refine_feat_data, refine_feat_bkg, w_bkg, pot_scale,
                                    data_factor=None, bkg_factor=None):
    """Assemble the COMPLETE signed measured inventory on the reco manifold: positive data rows
    (+1 * data_factor) followed by the ALIGNED literal background rows at -w_bkg*pot_scale*bkg_factor
    (Option-A negweight injection; the background factor multiplies the negative injection weight
    BEFORE refinement). Pure/login-safe. Returns (refine_feat, signed_w, n_data, n_bkg, raw_pos_sum,
    raw_neg_sum). Fails closed on invalid POT, misaligned rows/columns, or non-finite inputs."""
    fd = np.asarray(refine_feat_data, float)
    fb = np.asarray(refine_feat_bkg, float)
    wb = np.asarray(w_bkg, float)
    if not (np.isfinite(pot_scale) and float(pot_scale) > 0.0):
        raise ValueError(f"[negweight] invalid pot_scale {pot_scale!r} (require finite > 0)")
    if fd.ndim != 2 or fb.ndim != 2 or fd.shape[1] != fb.shape[1]:
        raise ValueError("[negweight] data/background refine-feature columns misaligned "
                         f"({getattr(fd, 'shape', None)} vs {getattr(fb, 'shape', None)})")
    if fb.shape[0] != wb.shape[0]:
        raise ValueError(f"[negweight] background feature rows {fb.shape[0]} != w_bkg {wb.shape[0]} "
                         "(misaligned background inventory; fail closed)")
    if not (np.all(np.isfinite(fd)) and np.all(np.isfinite(fb)) and np.all(np.isfinite(wb))):
        raise ValueError("[negweight] non-finite refine feature / w_bkg (fail closed)")
    nd_, nb = fd.shape[0], fb.shape[0]
    df = np.ones(nd_) if data_factor is None else np.asarray(data_factor, float)
    bf = np.ones(nb) if bkg_factor is None else np.asarray(bkg_factor, float)
    if df.shape != (nd_,) or bf.shape != (nb,):
        raise ValueError("[negweight] coherent bootstrap-factor length mismatch (fail closed)")
    data_signed = df                                                # +1 per data row * data_factor
    bkg_signed = -(wb * float(pot_scale)) * bf                      # negative injection * bkg_factor
    feat = np.vstack([fd, fb])
    signed = np.concatenate([data_signed, bkg_signed])
    return (feat, signed, int(nd_), int(nb),
            float(data_signed.sum()), float(np.abs(bkg_signed).sum()))


def refine_signed_measured(feat, signed_w, refine_fn, refine_kwargs=None):
    """Apply the LEARNED Stay-Positive refinement (refine_fn; production = u2d.refine_stay_positive)
    to the complete signed inventory and validate the output is FINITE, NON-NEGATIVE, and aligned to
    the concatenated data/background rows. Never substitutes purity/all-ones weights: a refinement
    that fails these invariants raises (fail closed). Returns (w_refined, telem)."""
    signed_w = np.asarray(signed_w, float)
    out = refine_fn(feat, signed_w, **dict(refine_kwargs or {}))
    tup = isinstance(out, (tuple, list))
    w_ref = np.asarray(out[0] if tup else out, float)
    g = np.asarray(out[1], float) if tup and len(out) > 1 and out[1] is not None else None
    frac_clip = float(out[2]) if tup and len(out) > 2 and out[2] is not None else None
    if w_ref.shape[0] != signed_w.shape[0]:
        raise ValueError(f"[negweight] refined weights {w_ref.shape[0]} not aligned to signed "
                         f"inventory {signed_w.shape[0]} (fail closed)")
    if not np.all(np.isfinite(w_ref)):
        raise ValueError("[negweight] refinement produced non-finite weights (fail closed)")
    if np.any(w_ref < 0.0):
        raise ValueError("[negweight] refinement produced NEGATIVE weights (Stay-Positive violated)")
    n_neg_in = int((signed_w < 0).sum())
    telem = {
        "refined_sum": float(w_ref.sum()), "refined_min": float(w_ref.min()),
        "refined_max": float(w_ref.max()), "n_floored_zero": int((w_ref == 0.0).sum()),
        "frac_clipped_reported": frac_clip, "n_negative_input_rows": n_neg_in,
        "g_min": (float(g.min()) if g is not None else None),
        "g_max": (float(g.max()) if g is not None else None)}
    return w_ref, telem


def assert_refined_target_is_replica(target_meta, *, bootstrap_seed):
    """Fail closed on any attempt to reuse a NOMINAL refined target for a bootstrap replica (or a
    replica target under the wrong seed). The refined target must be rebuilt PER REPLICA from that
    replica's coherent draws; a nominal target (bootstrap_seed=None) can never stand in for one."""
    got = target_meta.get("bootstrap_seed") if hasattr(target_meta, "get") else None
    if got is None:
        raise ValueError("[negweight] refined target has bootstrap_seed=None (NOMINAL) — cannot be "
                         f"reused for replica seed {bootstrap_seed} (fail closed; rebuild per replica)")
    if int(got) != int(bootstrap_seed):
        raise ValueError(f"[negweight] refined target seed {got} != requested replica "
                         f"{bootstrap_seed} (stale/reused target; fail closed)")
    return True


def validate_coherent_bootstrap(store, *, bootstrap_seed, n_sig_full, n_bkg_full=None,
                                estimator_fingerprint=None, inventory_hashes=None,
                                bkg_inventory_hash=None):
    """Extraction-side coherence gate (F7 step 4). Proves the persisted signal (and background)
    bootstrap factors ARE the same global seed draw restricted to the persisted indices, and that
    the seed, estimator fingerprint, and inventory-order hashes match. FAIL CLOSED (raise) on any
    mismatch. `store` is an npz/dict with mc_indices, sig_bootstrap_factor, bootstrap_seed
    (+ optional bkg_indices, bkg_bootstrap_factor, estimator_fingerprint, inventory_hashes)."""
    keys = set(store.files) if hasattr(store, "files") else set(store)
    need = {"mc_indices", "sig_bootstrap_factor", "bootstrap_seed"}
    if need - keys:
        raise ValueError(f"[F7] coherent-bootstrap store missing {sorted(need - keys)}")
    if int(np.asarray(store["bootstrap_seed"]).item()) != int(bootstrap_seed):
        raise ValueError("[F7] bootstrap seed mismatch (fail closed)")
    from pet_bootstrap import mc_poisson_factor
    imc = np.asarray(store["mc_indices"]); sig = np.asarray(store["sig_bootstrap_factor"])
    if imc.shape != sig.shape:
        raise ValueError("[F7] mc_indices/sig_bootstrap_factor shape mismatch")
    if not np.array_equal(sig, mc_poisson_factor(int(n_sig_full), int(bootstrap_seed))[imc]):
        raise ValueError("[F7] signal factor != canonical global seed draw at mc_indices "
                         "(post-subset redraw or wrong inventory) — fail closed")
    if "bkg_bootstrap_factor" in keys:
        if n_bkg_full is None:
            raise ValueError("[F7] bkg factor persisted but n_bkg_full not supplied for check")
        if "bkg_indices" not in keys:
            raise ValueError("[F7] bkg factor persisted but bkg_indices (order evidence) omitted")
        ib = np.asarray(store["bkg_indices"]); bf = np.asarray(store["bkg_bootstrap_factor"])
        if ib.shape != bf.shape:
            raise ValueError("[F7] bkg_indices/bkg_bootstrap_factor shape mismatch")
        exp = np.random.default_rng(int(bootstrap_seed) + 20_000_000).poisson(
            1.0, int(n_bkg_full)).astype(np.uint8)[ib]
        if not np.array_equal(bf, exp):
            raise ValueError("[F7] background factor != canonical global seed draw at bkg_indices")
        if bkg_inventory_hash is not None:
            got = (str(np.asarray(store["bkg_inventory_hash"]).item())
                   if "bkg_inventory_hash" in keys else None)
            if got != bkg_inventory_hash:
                raise ValueError("[F7] background inventory-order hash mismatch (fail closed)")
    if estimator_fingerprint is not None:
        got = str(np.asarray(store["estimator_fingerprint"]).item()) if "estimator_fingerprint" in keys else None
        if got != estimator_fingerprint:
            raise ValueError(f"[F7] estimator fingerprint mismatch: {got} != {estimator_fingerprint}")
    if inventory_hashes is not None:
        got = str(np.asarray(store["inventory_hashes"]).item()) if "inventory_hashes" in keys else None
        if got != inventory_hashes:
            raise ValueError("[F7] inventory-order hash mismatch (different/reordered inventory)")
    return True


RECOIL_OR_OLD_INPUT_MARKERS = ("of_inputs_pc_fullcloud", "of_inputs_pc_fps.npz",
                               "of_inputs_pc_fps_xps.npz", "of_inputs_pc_fps_xps2.npz",
                               "xps2", "recoil")


# --------------------------------------------------------------------------------------------
# B1 — the step-1 class ratio R (B1-NORMALIZATION-FIX-DESIGN.md §2b).
#
# The vendored DataLoader rescales each loader's pass_reco weight sum in place to
# `normalization_factor` (omnifold/dataloader.py:110-113), and omnifold.py:176-177 feeds exactly
# those two arrays as the step-1 class weight blocks. Normalizing BOTH to 1e6 forces W1/W0 == 1 at
# iteration 0 and erases the physical data/MC rate ratio. The fix keeps the MC block at
# STEP1_MC_NORMALIZATION and gives the measured block STEP1_MC_NORMALIZATION * R, so the class
# ratio IS R -- subsample-invariant, because the MC side is renormalized regardless of how many
# rows the `imc` draw took and R is built from the FULL inventory.
# --------------------------------------------------------------------------------------------
STEP1_MC_NORMALIZATION = 1_000_000.0


def step1_class_ratio(*, n_data, sum_w_bkg_raw, sum_w_mc_reco_raw, pot_scale):
    """THE B1 formula, deliberately in ONE function body.

        R = (n_data - pot_scale * sum_w_bkg_raw) / (pot_scale * sum_w_mc_reco_raw)

    Numerator: the signed measured inventory -- unit-weight data rows minus the POT-scaled
    background injection. Denominator: the POT-scaled signal-MC reco-level prediction.

    THE pot_scale TRAP. `w_truth` / `w_reco` / `w_bkg` in the G2 npz are the RAW literal ROOT
    per-event MC weights, NOT POT-scaled (`dump_pointcloud_inputs.py:182-186`, "Consumers apply
    pot_scale"). Nothing between the dump and `DataLoader(weight=w_truth, ...)` multiplies by it.
    Omitting `pot_scale` from the denominator inflates R by 1/pot_scale ~ 4.7x; two independent
    reviewers arrived at the formula without it.

    THE w_truth-vs-w_reco ASSUMPTION -- audit finding B-4, UNRESOLVED as of 2026-07-29.
    `sum_w_mc_reco_raw` is the reco-leg MC weight sum. Callers pass `w_truth` over `pass_reco`,
    because `w_truth` is what the reco leg is ACTUALLY fed today: the G2 contract carries a
    separate `w_reco` (`dump_pointcloud_inputs.py:201`, required at `:299`/`:540`) and the
    validated 2D path uses the two legs separately
    (`2d-unfolding/unfold_2d_omnifold_unbinned.py:1715-1716`), but this loader never reads
    `w_reco` -- the single `w_truth` vector drives both `omnifold.py:176-177` (step 1, reco) and
    `:196-197` (step 2, truth). So R as computed here is self-consistent with the code as it
    exists. IF B-4 is fixed so the reco leg uses `w_reco`, the physical denominator becomes
    `pot_scale * sum(w_reco[pass_reco])` and R moves by
    `sum(w_truth[pass_reco]) / sum(w_reco[pass_reco])`.

    That is why R is DERIVED here and never frozen as a constant: when B-4 is answered, this one
    function body changes -- not a search through the patch. `step1_class_ratio_from_dump` records
    the `w_reco`-vs-`w_truth` comparison at runtime, so the first 08-03 run answers B-4 as a side
    effect of computing R. Every bootstrap replica also has its own yield ratio, so a hardcoded R
    would be wrong for every replica but the nominal.
    """
    pot_scale = float(pot_scale)
    if not (np.isfinite(pot_scale) and pot_scale > 0.0):
        raise ValueError(f"[B1] invalid pot_scale {pot_scale!r} (require finite > 0)")
    numerator = float(n_data) - pot_scale * float(sum_w_bkg_raw)
    denominator = pot_scale * float(sum_w_mc_reco_raw)
    if not (np.isfinite(denominator) and denominator > 0.0):
        raise ValueError(f"[B1] non-positive MC reco denominator {denominator!r} "
                         "(cannot form the step-1 class ratio; fail closed)")
    R = numerator / denominator
    if not (np.isfinite(R) and R > 0.0):
        raise ValueError(f"[B1] step-1 class ratio R={R!r} is not finite and positive "
                         f"(numerator {numerator!r}, denominator {denominator!r}); fail closed")
    return float(R)


def step1_class_ratio_from_dump(d, *, pot_scale=None, n_data=None, w_truth_full=None,
                                pass_reco_full=None, w_bkg_full=None, data_factor=None,
                                bkg_factor=None, sig_factor=None, check_w_reco=True):
    """Derive R and its telemetry straight out of an open g2-fullevent-v1 npz mapping.

    Every consumer of R calls THIS -- the loader (§2a), the Gate-2 validator (§2c) and the Gate-4
    validator (§2d) -- so the formula lives in one body. The consumers do NOT share inputs: each
    opens the dump and reads its own arrays, which is the independence §2c requires. A validator
    that read R out of the loader's `meta` would certify the loader against the loader's own claim.

    Already-materialized arrays may be passed in to avoid a redundant read; anything not supplied
    is read from `d`. Bootstrap factors are the replica's coherent draws
    (`coherent_bootstrap_factors`): `data_factor` replaces the unit data-row weight, `bkg_factor`
    multiplies the negative background injection, `sig_factor` multiplies the signal MC -- exactly
    as `build_signed_measured_inventory` applies them, so R tracks the replica's own yield ratio.

    Returns (R, telem). `telem` carries the ingredients, and the `w_reco`-vs-`w_truth` comparison
    that is audit finding B-4's own minimal check.
    """
    if pot_scale is None:
        if "pot_scale" in d.files:
            pot_scale = float(np.asarray(d["pot_scale"]).item())
        elif "data_pot" in d.files and "mc_pot" in d.files:
            pot_scale = (float(np.asarray(d["data_pot"]).item())
                         / float(np.asarray(d["mc_pot"]).item()))
        else:
            raise ValueError("[B1] no pot_scale (and no data_pot/mc_pot) in input; cannot form R")

    w_truth_full = (np.asarray(d["w_truth"], dtype=np.float64) if w_truth_full is None
                    else np.asarray(w_truth_full, dtype=np.float64))
    pass_reco_full = (np.asarray(d["pass_reco"]) if pass_reco_full is None
                      else np.asarray(pass_reco_full)).astype(bool)
    w_bkg_full = (np.asarray(d["w_bkg"], dtype=np.float64) if w_bkg_full is None
                  else np.asarray(w_bkg_full, dtype=np.float64))
    if w_truth_full.shape != pass_reco_full.shape:
        raise ValueError(f"[B1] w_truth {w_truth_full.shape} and pass_reco {pass_reco_full.shape} "
                         "disagree (wrong inventory; fail closed)")
    if not (np.all(np.isfinite(w_truth_full)) and np.all(np.isfinite(w_bkg_full))):
        raise ValueError("[B1] non-finite w_truth / w_bkg (fail closed)")

    # Data row count: prefer the small scalars block over materializing the measured cloud.
    if n_data is None:
        if "measured_scalars" in d.files:
            n_data_rows = int(np.asarray(d["measured_scalars"]).shape[0])
        elif "measured_pc" in d.files:
            n_data_rows = int(np.asarray(d["measured_pc"]).shape[0])
        else:
            raise ValueError("[B1] neither measured_scalars nor measured_pc present; cannot count "
                             "data rows (fail closed)")
    else:
        n_data_rows = int(n_data)

    # Replica draws, applied exactly as build_signed_measured_inventory applies them.
    if data_factor is None:
        n_data_eff = float(n_data_rows)
    else:
        df = np.asarray(data_factor, dtype=np.float64)
        if df.shape != (n_data_rows,):
            raise ValueError(f"[B1] data_factor {df.shape} != data rows {(n_data_rows,)}")
        n_data_eff = float(df.sum())
    if bkg_factor is None:
        sum_w_bkg_raw = float(w_bkg_full.sum())
    else:
        bf = np.asarray(bkg_factor, dtype=np.float64)
        if bf.shape != w_bkg_full.shape:
            raise ValueError(f"[B1] bkg_factor {bf.shape} != w_bkg {w_bkg_full.shape}")
        sum_w_bkg_raw = float((w_bkg_full * bf).sum())
    w_sig = w_truth_full if sig_factor is None else (
        w_truth_full * np.asarray(sig_factor, dtype=np.float64))
    if w_sig.shape != w_truth_full.shape:
        raise ValueError(f"[B1] sig_factor broadcast {w_sig.shape} != w_truth "
                         f"{w_truth_full.shape}")
    sum_w_mc_reco_raw = float(w_sig[pass_reco_full].sum())

    R = step1_class_ratio(n_data=n_data_eff, sum_w_bkg_raw=sum_w_bkg_raw,
                          sum_w_mc_reco_raw=sum_w_mc_reco_raw, pot_scale=pot_scale)

    telem = {
        "R": R,
        "formula": "R = (n_data - pot_scale*sum(w_bkg)) / (pot_scale*sum(w_truth[pass_reco]))",
        "pot_scale": float(pot_scale),
        "n_data_rows": n_data_rows,
        "n_data_effective": n_data_eff,
        "sum_w_bkg_raw": sum_w_bkg_raw,
        "bkg_pot_scaled_sum": float(pot_scale) * sum_w_bkg_raw,
        "numerator_signed_data": n_data_eff - float(pot_scale) * sum_w_bkg_raw,
        "sum_w_truth_pass_reco_raw": sum_w_mc_reco_raw,
        "n_signal_rows": int(w_truth_full.shape[0]),
        "n_signal_pass_reco": int(pass_reco_full.sum()),
        "is_bootstrap_replica": any(f is not None for f in (data_factor, bkg_factor, sig_factor)),
        "reco_leg_weight_used": "w_truth",
    }

    # B-4's minimal check, recorded at runtime so the first real run answers it as a side effect.
    #
    # Both legs must carry the SAME replica scaling. The bit-identity question is about the dump's
    # RAW contract weights, but the derived numbers (`R_if_reco_leg_used_w_reco` and the shift
    # factor) are compared against a numerator that already carries this replica's data/bkg draws
    # and against `sum_w_mc_reco_raw`, which carries `sig_factor`. Leaving the reco leg unscaled
    # made the shift factor report `sig_factor` itself: with sig_factor=2 and w_reco == w_truth
    # bit-for-bit, it claimed a shift of 2.0 and an alternative R equal to the NOMINAL R rather
    # than the replica's. Found by an adversarial review of b3751cc, 2026-07-29; telemetry only --
    # the normalization-driving R above was never affected -- but B-4 is *decided* off these
    # numbers, so a replica reading would have argued for a shift that does not exist.
    if check_w_reco and "w_reco" in getattr(d, "files", ()):
        w_reco_full = np.asarray(d["w_reco"], dtype=np.float64)
        if w_reco_full.shape != w_truth_full.shape:
            raise ValueError(f"[B1/B-4] w_reco {w_reco_full.shape} != w_truth "
                             f"{w_truth_full.shape}")
        wt_raw, wr_raw = w_truth_full[pass_reco_full], w_reco_full[pass_reco_full]
        n_differs = int((wr_raw != wt_raw).sum())
        # raw: the contract question. scaled: consistent with sum_w_mc_reco_raw and the numerator.
        sum_w_reco_raw = float(wr_raw.sum())
        w_reco_sig = (w_reco_full if sig_factor is None
                      else w_reco_full * np.asarray(sig_factor, dtype=np.float64))
        sum_w_reco_scaled = float(w_reco_sig[pass_reco_full].sum())
        telem["b4_w_reco_vs_w_truth"] = {
            "present_in_dump": True,
            "bit_identical_over_pass_reco": n_differs == 0,
            "n_pass_reco_differing": n_differs,
            "sum_w_reco_pass_reco_raw": sum_w_reco_raw,
            "sum_w_reco_pass_reco_replica_scaled": sum_w_reco_scaled,
            "R_if_reco_leg_used_w_reco": (
                step1_class_ratio(n_data=n_data_eff, sum_w_bkg_raw=sum_w_bkg_raw,
                                  sum_w_mc_reco_raw=sum_w_reco_scaled, pot_scale=pot_scale)
                if sum_w_reco_scaled > 0 else None),
            "R_shift_factor_if_B4_fixed": (sum_w_mc_reco_raw / sum_w_reco_scaled
                                           if sum_w_reco_scaled else None),
            "verdict": ("B-4 INACTIVE for this dump (R above stands; re-check per systematic "
                        "endpoint before P5B)" if n_differs == 0 else
                        "B-4 ACTIVE -- the reco leg is fed w_truth but w_reco differs; resolve "
                        "B-4 before freezing R"),
        }
        del w_reco_full, w_reco_sig, wt_raw, wr_raw
    elif check_w_reco:
        telem["b4_w_reco_vs_w_truth"] = {
            "present_in_dump": False,
            "verdict": "w_reco absent -- required by dump_pointcloud_inputs.py:299; "
                       "contract violation, B-4 unanswerable from this input",
        }
    return R, telem


def assert_publication_config(cfg):
    """Fail closed (no-GPU) unless a full-event PET PUBLICATION run is configured correctly, so a
    launcher can NEVER select old xps2 / recoil-only / purity inputs for a publication product:
      * estimator_fingerprint == 'pet-fullevent-fps-v1' (FULL schema; the reduced
        'pet-reduced-fps-cross' is a cross-check, forbidden here);
      * bkg_mode == 'negweight-refined' (the locked nominal; purity is a control);
      * the input carries the G2 full-schema markers (petSchemaVersion=g2-fullevent-v1,
        hasFullEventSchema=1, fullPhaseSpace=1) AND a background inventory;
      * the input path is not a known recoil/old/xps2 scaffolding file.
    `cfg` is a plain dict (launcher/config values); this runs before any compute."""
    from fullevent_dump_contract import G2_SCHEMA        # lazy: avoid import cycle
    fp = cfg.get("estimator_fingerprint")
    if fp != "pet-fullevent-fps-v1":
        raise ValueError(f"[PUB-GATE] estimator_fingerprint {fp!r} != 'pet-fullevent-fps-v1' "
                         "(reduced/recoil/unset not allowed for a publication product)")
    if cfg.get("bkg_mode") != "negweight-refined":
        raise ValueError(f"[PUB-GATE] bkg_mode {cfg.get('bkg_mode')!r} != 'negweight-refined' "
                         "(purity is a regression control, never the publication nominal)")
    for k, v in G2_SCHEMA.items():
        got = cfg.get(k)
        ok = got is not None and (str(got) == v if k == "petSchemaVersion" else int(got) == v)
        if not ok:
            raise ValueError(f"[PUB-GATE] input lacks G2 full-schema marker {k}={v} (got {got!r})")
    if not cfg.get("has_background"):
        raise ValueError("[PUB-GATE] no background inventory declared (negweight-refined needs it)")
    inp = str(cfg.get("input", ""))
    for bad in RECOIL_OR_OLD_INPUT_MARKERS:
        if bad in inp:
            raise ValueError(f"[PUB-GATE] input {inp!r} matches recoil/old/xps2 marker {bad!r} "
                             "(forbidden for a full-event publication run)")
    return True


def build_fullevent_loaders(inputs_npz, max_events=None, seed=0, bootstrap_seed=None,
                            feature_names=DEFAULT_EVT_FEATURES, rank=0, size=1,
                            enforce_fps_edges=True, data_scalars_npz=None,
                            bkg_mode="negweight-refined", refine_fn=None, refine_kwargs=None,
                            verify_identities=True,
                            truth_feature_names=DEFAULT_TRUTH_EVT_FEATURES):
    """Assemble paired full-event (cloud + continuous event feature) DataLoaders on the FPS
    domain. Returns (data, mc, imc, coord_reco, coord_gen, meta). Mirrors the recoil-only
    build_loaders subsample/bootstrap contract, but sets reco_evt/gen_evt on the loaders and
    keeps the truth PDG + angular geometry. FPS edges are asserted (fail closed) unless
    enforce_fps_edges=False (tests with synthetic edges).

    THE FULL EVENT IS ACTUALLY READ (2026-08-01, AUDIT-FINDINGS-20260731 J01). Every G2 extension
    array is consumed: `reco_view`/`reco_time` (and the data/bkg twins) become token columns 3,4
    of the reco cloud; `reco_muon`/`reco_vertex` (and twins) become event features. The two event
    schemas differ in width, so the caller must build the step-1 network at `meta["n_evt_reco"]`
    and the step-2 network at `meta["n_evt_truth"]`. `feature_names=REDUCED_EVT_FEATURES` selects
    the `pet-reduced-fps-cross` ablation, which is a cross-check and never a publication source.

    NEGWEIGHT-REFINED (locked publication nominal): the measured DataLoader carries the COMPLETE
    signed measured inventory -- positive data rows ++ the aligned literal background clouds/event
    features at -w_bkg*pot_scale -- refined by the learned Stay-Positive classifier to finite
    non-negative weights aligned to the concatenated data/background rows. The data row count is
    derived from the G2 data inventory `measured_pc` (NOT any legacy/purity `measured_weights`).
    `refine_fn` (default = the deferred canonical u2d.refine_stay_positive) is injectable so the
    login-safe tests can pass an algorithm-identical sklearn refinement; the refined-target
    telemetry lands in meta['target'] for decision review."""
    d = np.load(inputs_npz, allow_pickle=True)
    if enforce_fps_edges:
        assert_extended_fps_edges(d["edges_0"], d["edges_1"])
    if bkg_mode not in ("negweight-refined", "purity"):
        raise ValueError(f"[F7] unknown bkg_mode {bkg_mode!r} (negweight-refined|purity)")
    # Old / recoil-only / purity-scaffolding schema: reject before any construction (fail closed).
    if str(np.asarray(d["petSchemaVersion"]).item() if "petSchemaVersion" in d.files
           else "") != "g2-fullevent-v1":
        raise ValueError("[G2] input is not a g2-fullevent-v1 schema NPZ (old/recoil/scaffolding); "
                         "the full-event negweight-refined path requires the G2 full schema.")

    # Data row count is derived from the G2 DATA inventory (measured_pc), NOT a legacy/purity
    # 'measured_weights' array (which the negweight-refined G2 dump deliberately does not emit --
    # the refined target is rebuilt per replica). Fail closed if the data cloud is absent.
    if "measured_pc" not in d.files:
        raise ValueError("[G2] input has no 'measured_pc' data inventory; cannot derive the data "
                         "row count for the full-event measured target (fail closed).")
    N = np.asarray(d["pass_reco"]).shape[0]
    M = np.asarray(d["measured_pc"]).shape[0]

    # Subsample the MC TRAINING side BEFORE the (heavy) cloud processing so build_truth_cloud's
    # angular transform only touches the training subset (a full 49.2M process would spike tens of
    # GB). The MEASURED target (data ++ injected background) is always the COMPLETE inventory -- its
    # size is set by the measurement, independent of the MC training subsample -- so D vs B relative
    # POT normalization is never broken by subsampling.
    #
    # HOST MEMORY GREW ON 2026-08-01 and the 08-03 sizing must account for it. The reco cloud is now
    # five token columns instead of three, and `np.asarray(d[key])[imc]` materializes each member in
    # full before subsampling it (a pre-existing property of NpzFile that
    # `measure_fullevent_host_memory.py` exists to measure -- see its docstring). The additions are
    # `reco_view`/`reco_time`, two full-inventory (N,P) float32 arrays, plus two more token columns
    # on each of the three clouds. Re-run the ladder before sizing the nominal's node; do not carry
    # the pre-08-01 high-water mark forward.
    imc = np.arange(N)
    if max_events is not None:
        imc = np.sort(np.random.default_rng(seed).choice(N, min(max_events, N), replace=False))

    # Which G2 extension arrays this schema needs. The muon/vertex blocks are demanded only when a
    # requested feature reads them, so `feature_names=REDUCED_EVT_FEATURES` still runs against a
    # reduced fixture -- but demanded loudly when it does, because a silent narrowing here is J01
    # all over again. The per-token vectors below are unconditional; see the note there.
    need = {_EVT_SPEC[f][0] for f in feature_names} | {_EVT_SPEC[f][0]
                                                       for f in truth_feature_names}
    required = []
    if "muon" in need:
        required += ["reco_muon", "data_muon"]
    if "vertex" in need:
        required += ["reco_vertex", "data_vertex"]
    # The per-token view/time vectors are required UNCONDITIONALLY, not per-schema: every input
    # that reaches this line has already passed the `petSchemaVersion == g2-fullevent-v1` gate
    # above, and the contract's REQUIRED_KEYS mandate them. Building a 3-column cloud from a dump
    # that carries 5 would be the same silent narrowing as the event block's -- the estimator would
    # simply be blind to the detector view, with nothing but a `meta` flag to say so.
    required += ["reco_view", "reco_time", "data_view", "data_time"]
    missing = [k for k in required if k not in d.files]
    if missing:
        raise ValueError(
            f"[G2] the requested event-feature schema needs {missing}, absent from this input. "
            "The g2-fullevent-v1 contract requires them "
            "(fullevent_dump_contract.RECO_KEYS/DATA_KEYS); an input that lacks them is not the "
            "full-event dump. Fail closed rather than quietly training the reduced "
            "`pet-reduced-fps-cross` estimator under the publication fingerprint.")

    def _tok(key, idx=None):
        """A per-token extension vector, subsampled like its cloud, or None if absent."""
        if key not in d.files:
            return None
        a = np.asarray(d[key])
        return a if idx is None else a[idx]

    reco_cloud, coord_reco = build_reco_cloud(np.asarray(d["part_reco"])[imc],
                                              _tok("reco_view", imc), _tok("reco_time", imc))
    gen_cloud, coord_gen = build_truth_cloud(np.asarray(d["part_gen"])[imc])
    reco_scalars = np.asarray(d["reco_scalars"])[imc]
    truth_scalars = np.asarray(d["truth_scalars"])[imc]
    pass_reco = np.asarray(d["pass_reco"])[imc]
    pass_truth = np.asarray(d["pass_truth"])[imc]
    reco_blocks = evt_blocks(scalars=reco_scalars,
                             muon=(np.asarray(d["reco_muon"])[imc] if "reco_muon" in d.files
                                   else None),
                             vertex=(np.asarray(d["reco_vertex"])[imc] if "reco_vertex" in d.files
                                     else None))
    truth_blocks = evt_blocks(scalars=truth_scalars)   # truth_scalars is the only truth-side array
    # DATA event-feature scalars = the DATA-side reconstructed muon (G2 measured_scalars, full M).
    # CLM-007: NEVER silently fall back to MC reco_scalars.
    if "measured_scalars" in d.files:
        meas_scalars = np.asarray(d["measured_scalars"]); data_src = "pc-npz:measured_scalars"
    elif data_scalars_npz is not None:
        with np.load(data_scalars_npz, allow_pickle=True) as dz:
            dkey = "measured_scalars" if "measured_scalars" in dz.files else "measured"
            meas_scalars = np.asarray(dz[dkey])
        data_src = f"{data_scalars_npz}:{dkey}"
        if meas_scalars.shape[0] != M:
            raise ValueError(f"[CLM-007] data-scalar rows {meas_scalars.shape[0]} != measured_pc "
                             f"rows {M} in {data_scalars_npz} -- not row-aligned; refuse to build.")
        # CLM-007 extended to the muon object: a sidecar carries scalars only, so a wide schema
        # over a sidecar data leg would have no data muon and MUST NOT borrow the MC one.
        if "muon" in need or "vertex" in need:
            raise ValueError(
                f"[CLM-007 GUARD] the requested schema reads the muon object/vertex, but the data "
                f"leg comes from the sidecar {data_scalars_npz!r}, which carries scalars only. "
                "Refusing to pair a wide MC schema with a narrow data one (that is how MC-miss "
                "sentinels reach the step-1 data classifier). Use the G2 dump, or select "
                "feature_names=REDUCED_EVT_FEATURES for a scalars-only cross-check.")
    else:
        raise ValueError(
            "[CLM-007 GUARD] pc npz has no 'measured_scalars' and no data_scalars_npz was given. "
            "Refusing to fall back to MC reco_scalars (would inject -9999 MC-miss sentinels into "
            "the step-1 data classifier).")
    meas_blocks = evt_blocks(scalars=meas_scalars,
                             muon=(np.asarray(d["data_muon"]) if "data_muon" in d.files else None),
                             vertex=(np.asarray(d["data_vertex"]) if "data_vertex" in d.files
                                     else None))
    event_reco, event_truth, event_data, meta = build_event_features(
        reco_blocks, truth_blocks, meas_blocks, feature_names,
        pass_reco=pass_reco, pass_truth=pass_truth, truth_feature_names=truth_feature_names)
    meta["data_scalar_source"] = data_src
    meta["reco_cloud_cols"] = list(RECO_CLOUD_COLS[:reco_cloud.shape[-1]])
    meta["token_view_time_read"] = reco_cloud.shape[-1] == len(RECO_CLOUD_COLS)
    assert_no_truth_leakage(event_reco, reco_blocks, truth_blocks, feature_names,
                            pass_reco=pass_reco, truth_feature_names=truth_feature_names)
    rmu = np.asarray(meta["reco_norm_mean"], np.float32); rsd = np.asarray(meta["reco_norm_std"], np.float32)

    w_truth_full = np.asarray(d["w_truth"]).astype(np.float32)            # FULL signal-MC (raw)
    has_bkg = "w_bkg" in d.files
    meta["bkg_mode"] = bkg_mode
    meta["estimator_fingerprint"] = (str(np.asarray(d["estimator_fingerprint"]).item())
                                     if "estimator_fingerprint" in d.files else None)
    # NEGWEIGHT-REFINED requires the aligned background inventory + a valid POT scale. These cheap
    # presence checks run BEFORE the (heavier) identity verification so a missing-background nominal
    # fails fast; the CLM-007 data-scalar guard above still fires first for a data-scalar-absent input.
    pot_scale = None
    if bkg_mode == "negweight-refined":
        if not has_bkg:
            raise ValueError(
                "[negweight-refined] input has NO background inventory ('w_bkg'/background clouds "
                "absent). The Option-A negweight + Stay-Positive nominal needs the aligned background "
                "clouds/scalars/weights. Fail closed. bkg_mode='purity' is a labeled control only.")
        # bkg_view/bkg_time are in this list for the same reason as the data twins: the injected
        # background clouds are concatenated onto the measured clouds, so a background inventory
        # without them yields a 3-column block against a 5-column one. That surfaces as a numpy
        # shape error several lines later, which is a worse way to learn it.
        for k in ("bkg_part_reco", "bkg_reco_scalars", "w_bkg", "bkg_view", "bkg_time"):
            if k not in d.files:
                raise ValueError(f"[negweight-refined] missing required background inventory '{k}' "
                                 "(misaligned/incomplete background; fail closed).")
        if "pot_scale" in d.files:
            pot_scale = float(np.asarray(d["pot_scale"]).item())
        elif "data_pot" in d.files and "mc_pot" in d.files:
            pot_scale = float(np.asarray(d["data_pot"]).item()) / float(np.asarray(d["mc_pot"]).item())
        else:
            raise ValueError("[negweight-refined] no pot_scale (and no data_pot/mc_pot) in input; "
                             "cannot POT-scale the background injection (fail closed).")
        if not (np.isfinite(pot_scale) and pot_scale > 0.0):
            raise ValueError(f"[negweight-refined] invalid pot_scale {pot_scale!r} (require finite>0)")

    # Record + (runtime) verify the stored per-inventory identity/order hashes. This runs where the
    # arrays are materialized (compute node / tiny fixtures), never on the login node against the
    # full 9.9 GB NPZ. Fail closed on a mismatched/absent stored identity.
    ident = {}
    if verify_identities:
        ident["sig"] = _verify_stored_identity(
            d, "sig_identity_hash", (w_truth_full, np.asarray(d["pass_truth"])), "signal")
        ident["data"] = _verify_stored_identity(
            d, "data_identity_hash", (np.asarray(d["measured_pc"]),), "data")
        if has_bkg:
            ident["bkg"] = _verify_stored_identity(
                d, "bkg_identity_hash", (np.asarray(d["w_bkg"]), np.asarray(d["bkg_indices"])), "bkg")
    meta["input_identity_hashes"] = ident

    # Signal-MC coherent bootstrap factor (global-before-subset draw, indexed by imc). NEVER a
    # post-subset redraw. The measured-side factors are applied to the FULL measured inventory below.
    data_factor = sig_factor = bkg_factor = None
    if bootstrap_seed is not None:
        n_bkg_full = int(np.asarray(d["w_bkg"]).shape[0]) if has_bkg else 0
        data_factor, sig_factor, bkg_factor = coherent_bootstrap_factors(
            M, N, n_bkg_full, int(bootstrap_seed))
        w_truth = (w_truth_full[imc] * sig_factor[imc]).astype(np.float32)
        meta["bootstrap"] = {
            "bootstrap_seed": int(bootstrap_seed), "n_sig_full": int(N), "n_data_full": int(M),
            "n_bkg_full": int(n_bkg_full), "mc_indices": imc, "sig_bootstrap_factor": sig_factor[imc],
            "inventory_hashes": inventory_order_hash(w_truth_full),
            "bkg_bootstrap_factor": (bkg_factor if has_bkg else None)}
    else:
        w_truth = w_truth_full[imc]
        meta["bootstrap"] = None

    from omnifold.dataloader import DataLoader                    # vendored engine, imported late
    # B1 §2a: the MC block keeps the 1e6 normalization (unchanged -- STEP1_MC_NORMALIZATION is the
    # DataLoader default, passed explicitly so the measured block's 1e6*R below is visibly the SAME
    # base times R). Normalizing MC is load-bearing, not incidental: it is what makes the class
    # ratio independent of how many rows the `imc` draw took.
    mc = DataLoader(reco=reco_cloud, gen=gen_cloud, pass_reco=pass_reco, pass_gen=pass_truth,
                    weight=w_truth, normalize=True,
                    normalization_factor=STEP1_MC_NORMALIZATION,
                    reco_evt=event_reco, gen_evt=event_truth,
                    rank=rank, size=size)

    if bkg_mode == "purity":
        # Labeled REGRESSION CONTROL only (never the publication nominal). Data-only measured
        # sample at unit weight; the all-ones purity placeholder is acceptable HERE (control), and
        # is forbidden for the negweight-refined nominal by write/loader guards.
        meas_cloud, _ = build_reco_cloud(np.asarray(d["measured_pc"]),
                                         _tok("data_view"), _tok("data_time"))
        data = DataLoader(reco=meas_cloud, weight=np.ones(M, np.float32), normalize=True,
                          reco_evt=event_data)
        meta["bkg_control"] = "purity = REGRESSION CONTROL, not the publication nominal"
        meta["target"] = {"target_mode": "purity-control", "bootstrap_seed": bootstrap_seed}
        return data, mc, imc, coord_reco, coord_gen, meta

    # ---------------- negweight-refined (locked publication nominal) ----------------
    # (background presence + a valid pot_scale were already validated above, before identity check)
    meas_cloud, _ = build_reco_cloud(np.asarray(d["measured_pc"]),           # FULL data cloud
                                     _tok("data_view"), _tok("data_time"))
    bkg_cloud, _ = build_reco_cloud(np.asarray(d["bkg_part_reco"]),          # aligned bkg cloud
                                    _tok("bkg_view"), _tok("bkg_time"))
    bkg_reco_scalars = np.asarray(d["bkg_reco_scalars"])
    w_bkg_full = np.asarray(d["w_bkg"]).astype(np.float32)
    if not (bkg_cloud.shape[0] == bkg_reco_scalars.shape[0] == w_bkg_full.shape[0]):
        raise ValueError("[negweight-refined] background cloud/scalars/w_bkg row counts disagree "
                         "(misaligned background inventory; fail closed).")
    if "muon" in need and "bkg_muon" not in d.files:
        raise ValueError("[negweight-refined] the requested schema reads the muon object but the "
                         "background inventory carries no 'bkg_muon'; the injected background rows "
                         "would occupy a different feature space from the data rows they are "
                         "subtracted from (fail closed).")
    if "vertex" in need and "bkg_vertex" not in d.files:
        raise ValueError("[negweight-refined] the requested schema reads the reco vertex but the "
                         "background inventory carries no 'bkg_vertex' (fail closed).")
    bkg_blocks = evt_blocks(scalars=bkg_reco_scalars,
                            muon=(np.asarray(d["bkg_muon"]) if "bkg_muon" in d.files else None),
                            vertex=(np.asarray(d["bkg_vertex"]) if "bkg_vertex" in d.files
                                    else None))
    assert_evt_block_widths(bkg_blocks, "background")
    # background event features under the SAME reconstructed-muon normalization as the data
    assert_finite_event_scalars(bkg_blocks, feature_names, None,
                                "bkg_reco_scalars (background; all rows reco-selected)")
    event_bkg = _event_block(bkg_blocks, feature_names, (rmu, rsd))
    # ---- B-5 / J05: the refinement feature space is the CLASSIFIER's reco manifold ----------
    # g(x) = D/(D+B) was previously fitted on (pT, p_parallel) alone and the refined weights then
    # attached to cloud-plus-event space, so background structure carried by anything else could
    # not be subtracted conditionally -- it could only be subtracted on average
    # (AUDIT-FINDINGS-20260731 J05; `demo_b5_refiner_feature_space.py` shows the muon-projection
    # agreement that seemed to license the reduction is an algebraic identity, not evidence).
    # The refiner now sees the SAME normalized event block the step-1 classifier is conditioned
    # on, so every event feature the estimator can exploit is one the target was built in.
    #
    # WHAT THIS DOES NOT CLOSE. The per-token recoil cloud -- including the view/time columns
    # added above -- is still outside the refiner's feature space: `refine_stay_positive` is a
    # tabular classifier over a fixed-width design matrix, and giving it the cloud is a different
    # (set-valued) estimator, not a wider column list. J05 is narrowed to the cloud, not retired.
    refine_feat_data = np.asarray(event_data, float)
    refine_feat_bkg = np.asarray(event_bkg, float)
    refine_space = ("normalized event_reco block (" + ",".join(feature_names)
                    + "); per-token cloud still excluded -- see B-5/J05")

    feat, signed, n_data, n_bkg, raw_pos_sum, raw_neg_sum = build_signed_measured_inventory(
        refine_feat_data, refine_feat_bkg, w_bkg_full, pot_scale,
        data_factor=(data_factor if data_factor is not None else None),
        bkg_factor=(bkg_factor if bkg_factor is not None else None))
    refiner = refine_fn if refine_fn is not None else learned_stay_positive_refiner()
    refine_backend = (getattr(refine_fn, "__name__", repr(refine_fn)) if refine_fn is not None
                      else "u2d.refine_stay_positive")
    w_refined, ref_telem = refine_signed_measured(feat, signed, refiner, refine_kwargs)

    meas_cloud_all = np.concatenate([meas_cloud, bkg_cloud], axis=0)
    event_meas_all = np.concatenate([event_data, event_bkg], axis=0)
    if not (meas_cloud_all.shape[0] == event_meas_all.shape[0] == w_refined.shape[0]
            == n_data + n_bkg):
        raise ValueError("[negweight-refined] concatenated measured target rows misaligned "
                         "(cloud/event-feature/weight; fail closed).")
    # B1 §2a: the measured block is normalized to 1e6 * R, not 1e6. R is DERIVED here from the
    # full inventory in hand (never piped in, never hardcoded -- see step1_class_ratio), and under
    # bootstrap it is rebuilt from THIS replica's coherent draws, which are in scope above.
    R, r_telem = step1_class_ratio_from_dump(
        d, pot_scale=pot_scale, n_data=M, w_truth_full=w_truth_full, w_bkg_full=w_bkg_full,
        data_factor=data_factor, bkg_factor=bkg_factor,
        sig_factor=(sig_factor if bootstrap_seed is not None else None))
    data = DataLoader(reco=meas_cloud_all, weight=w_refined.astype(np.float32), normalize=True,
                      normalization_factor=STEP1_MC_NORMALIZATION * R,
                      reco_evt=event_meas_all)

    meta["target"] = {
        "target_mode": "negweight-refined", "bootstrap_seed": bootstrap_seed,
        "step1_mc_normalization": STEP1_MC_NORMALIZATION,
        "step1_measured_normalization": STEP1_MC_NORMALIZATION * R,
        "step1_class_ratio": R, "step1_class_ratio_telemetry": r_telem,
        "refinement": "stay-positive (arXiv:2505.03724)", "refinement_backend": refine_backend,
        "refinement_is_learned_production": (refine_fn is None),
        "refinement_feature_space": refine_space,
        "refinement_feature_names": list(feature_names),
        "estimator_fingerprint": meta["estimator_fingerprint"],
        "input_identity_hashes": ident, "pot_scale": pot_scale,
        "raw_positive_sum": raw_pos_sum, "raw_negative_sum": raw_neg_sum,
        "n_data_rows": n_data, "n_bkg_rows": n_bkg, "n_measured_rows": n_data + n_bkg,
        "signed_target_hash": inventory_order_hash(signed),
        **ref_telem}
    return data, mc, imc, coord_reco, coord_gen, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True, help="FPS point-cloud npz (xps2 scaffolding)")
    ap.add_argument("--data-scalars", default=None,
                    help="npz with the DATA muon scalars ('measured' cols 0,1 = pT,p‖), e.g. "
                         "of_inputs_5d_fps_xps2.npz. Required when the pc npz lacks "
                         "measured_scalars (CLM-007: no silent MC fallback).")
    ap.add_argument("--max-events", type=int, default=None)
    ap.add_argument("--no-fps-guard", action="store_true")
    ap.add_argument("--bkg-mode", default="purity", choices=["negweight-refined", "purity"],
                    help="nominal=negweight-refined (needs the Option-A background-cloud omnifile); "
                         "'purity' is a regression control (the xps2 scaffolding default).")
    ap.add_argument("--schema", default="full", choices=["full", "reduced"],
                    help="full = pet-fullevent-fps-v1 (muon object + reco vertex + view/time); "
                         "reduced = the pet-reduced-fps-cross {pT,p||} CROSS-CHECK, never a "
                         "publication central/lateral source.")
    a = ap.parse_args()
    data, mc, imc, cr, cg, meta = build_fullevent_loaders(
        a.inputs, max_events=a.max_events, enforce_fps_edges=not a.no_fps_guard,
        data_scalars_npz=a.data_scalars, bkg_mode=a.bkg_mode,
        feature_names=(DEFAULT_EVT_FEATURES if a.schema == "full" else REDUCED_EVT_FEATURES))
    print(f"[fullevent] reco cloud {np.asarray(mc.reco).shape} coord_reco={cr} "
          f"reco_evt {np.asarray(mc.reco_evt).shape}")
    print(f"[fullevent] gen  cloud {np.asarray(mc.gen).shape} coord_gen={cg} "
          f"gen_evt {np.asarray(mc.gen_evt).shape}")
    print(f"[fullevent] data cloud {np.asarray(data.reco).shape} data_evt "
          f"{np.asarray(data.reco_evt).shape}")
    print(f"[fullevent] event-feature meta: {meta}")

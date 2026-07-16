#!/usr/bin/env python3
"""Full-event PET DataLoader over the extended-FPS domain (KNOWN_ISSUES #19, P5A).

Replaces the recoil-only representation (`minerva_pet_dataloader.py`) with a full-event
one and pins the measurement domain to the extended full-phase-space (FPS) fiducial. The
PET classifier trains UNBINNED on CONTINUOUS features; the extended (pT, p_parallel) EDGES
are used ONLY for domain retention, reporting, covariance and validation -- NEVER as
classifier inputs or training bins (user directive 2026-07-16).

Representation (three explicit schemas; no manufactured counterparts):
  * reco cloud  : recoil tokens (E, pos, z). KNN neighborhood = detector geometry (pos, z),
                  NOT the first two columns by accident. Padding = energy(col 0)==0.
  * truth cloud : FS-hadron tokens (E, px, py, pz, pdg, theta, phi). KNN neighborhood =
                  angular direction (theta, phi). PDG retained (recoil-only loader dropped it);
                  a learned categorical embedding is the production refinement (documented).
  * event_reco / event_data  (SAME observable schema): a distinguished RECONSTRUCTED muon,
                  continuous [pT, p_parallel] now (full px,py,pz,phi,E,charge,MINOS-quality
                  + reco vertex + residual-energy summaries fold in once the full-event C++
                  dump provides them -- see FULL_EVENT_INTERFACE_REQUEST.md). event_data uses
                  the DATA muon, event_reco the MC-reco muon. Detector/MINOS features are
                  step-1 only; NO truth counterpart is ever manufactured.
  * event_truth (DISTINCT schema, own normalization): truth muon continuous [pT, p_parallel]
                  (+ truth event quantities when adopted). NO MINOS/range/quality, NO sentinels.

LEAKAGE INVARIANT (tested): event_reco/event_data carry only reconstructed/detector
quantities; a step-1 classifier never receives any truth-only quantity (truth muon, truth
vertex, PDG-mode, incoming-nu energy, ...).

This module's PURE functions (edge assertion, cloud/feature builders, leakage check) import
NO TensorFlow, so they are unit-testable on the login node. `build_fullevent_loaders` imports
the vendored DataLoader lazily.
"""
import argparse
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


def build_reco_cloud(part_reco):
    """Recoil reco cloud (E, pos, z) scaled to O(1). Returns (cloud, coord_idx).
    coord_idx=(1,2) => KNN neighborhood is the (pos, z) detector geometry, not cols (0,1)."""
    cloud = _scale_clean(part_reco)          # (N, P, 3) = E, pos, z
    return cloud, (1, 2)


def build_truth_cloud(part_gen):
    """Truth FS-hadron cloud with PDG retained + explicit angular KNN coordinates appended.

    Input part_gen (N,P,5) = (E,px,py,pz,pdg). Output (N,P,7) =
      (E/GeV, px/GeV, py/GeV, pz/GeV, pdg, theta, phi)
    with coord_idx=(5,6) => KNN neighborhood = angular direction (theta,phi), a genuine
    truth geometry rather than raw momentum columns. Padded tokens (E==0) get theta=phi=0
    and are pushed away by the model's coord_shift mask, so the energy(col0) pad mask holds.
    """
    part_gen = np.asarray(part_gen, np.float32)
    E   = part_gen[:, :, 0]
    px, py, pz = part_gen[:, :, 1], part_gen[:, :, 2], part_gen[:, :, 3]
    pdg = part_gen[:, :, 4]
    pt = np.hypot(px, py)
    theta = np.arctan2(pt, pz)               # polar angle wrt beam (rad)
    phi = np.arctan2(py, px)                 # azimuth (rad)
    valid = E != 0                           # real tokens
    theta = np.where(valid, theta, 0.0).astype(np.float32)
    phi = np.where(valid, phi, 0.0).astype(np.float32)
    kin = _scale_clean(np.stack([E, px, py, pz], axis=-1))     # (N,P,4) GeV, pad-preserving
    pdg = np.where(valid, pdg, 0.0).astype(np.float32)         # keep raw PDG (embed in prod)
    cloud = np.concatenate([kin, pdg[..., None], theta[..., None], phi[..., None]], axis=-1)
    return cloud.astype(np.float32), (5, 6)


# Event-feature spec: which CONTINUOUS scalars form the distinguished-muon/context block.
# Default = the muon (pT, p_parallel) available NOW (reduced set; the reduction is recorded
# in the feature contract). The full object folds in when the full-event dump lands.
DEFAULT_EVT_FEATURES = ("pt", "pparallel")


def _event_block(scalars, feature_names, norm):
    """Assemble + normalize a continuous event-feature block from a (N, ncol) scalar array."""
    scalars = np.asarray(scalars, np.float32)
    cols = [SCALAR_COLS[f] for f in feature_names]
    block = scalars[:, cols].astype(np.float32)
    if norm is not None:
        mu, sd = norm
        block = (block - np.asarray(mu, np.float32)) / np.asarray(sd, np.float32)
    return block.astype(np.float32)


def build_event_features(reco_scalars, truth_scalars, measured_scalars,
                         feature_names=DEFAULT_EVT_FEATURES,
                         pass_reco=None, pass_truth=None):
    """Return (event_reco, event_truth, event_data, meta).

    event_reco/event_data share the SAME observable feature schema (reconstructed muon);
    event_truth uses the SAME feature NAMES but the TRUTH scalars and its OWN normalization
    (distinct schema/dimension is allowed to differ in production). All continuous.

    SENTINEL HANDLING (critical): the reconstructed muon is UNDEFINED for events that fail
    reco (FPS misses carry a -9999 sentinel in reco_scalars). The normalization is therefore
    computed over pass_reco events ONLY (truth over pass_truth ONLY), and the undefined
    (!pass_reco) reco rows are set to 0 post-normalization (the block mean). Those rows are
    masked by pass_reco in the step-1 loss, so zeroing keeps them numerically neutral without
    injecting the sentinel. This also keeps the reco-side normalization a pure detector
    statistic (no truth leakage)."""
    reco_scalars = np.asarray(reco_scalars, np.float32)
    truth_scalars = np.asarray(truth_scalars, np.float32)
    cols = [SCALAR_COLS[f] for f in feature_names]
    rmask = np.ones(reco_scalars.shape[0], bool) if pass_reco is None else np.asarray(pass_reco, bool)
    tmask = np.ones(truth_scalars.shape[0], bool) if pass_truth is None else np.asarray(pass_truth, bool)
    rsub = reco_scalars[rmask][:, cols]; tsub = truth_scalars[tmask][:, cols]
    rmu = rsub.mean(0); rsd = rsub.std(0) + 1e-6
    tmu = tsub.mean(0); tsd = tsub.std(0) + 1e-6
    event_reco = _event_block(reco_scalars, feature_names, (rmu, rsd)); event_reco[~rmask] = 0.0
    event_truth = _event_block(truth_scalars, feature_names, (tmu, tsd)); event_truth[~tmask] = 0.0
    event_data = _event_block(measured_scalars, feature_names, (rmu, rsd))  # data all pass_reco
    meta = {"feature_names": list(feature_names),
            "reco_norm_mean": rmu.tolist(), "reco_norm_std": rsd.tolist(),
            "truth_norm_mean": tmu.tolist(), "truth_norm_std": tsd.tolist(),
            "n_evt": len(feature_names),
            "normalized_over": "pass_reco (reco/data) / pass_truth (truth); !pass rows zeroed"}
    return event_reco, event_truth, event_data, meta


def assert_no_truth_leakage(event_reco, reco_scalars, truth_scalars, feature_names,
                            pass_reco=None):
    """Prove event_reco is a function of RECO scalars (+ pass_reco) ONLY, no truth-only info.

    Rebuild event_reco from reco_scalars alone (same pass_reco-masked normalization + !pass
    zeroing) and require an exact match; also require it NOT equal the block built from
    truth_scalars. This is the explicit step-1 no-truth-leakage test the gate requires."""
    reco_scalars = np.asarray(reco_scalars, np.float32)
    cols = [SCALAR_COLS[f] for f in feature_names]
    rmask = np.ones(reco_scalars.shape[0], bool) if pass_reco is None else np.asarray(pass_reco, bool)
    rmu = reco_scalars[rmask][:, cols].mean(0); rsd = reco_scalars[rmask][:, cols].std(0) + 1e-6
    rebuilt = _event_block(reco_scalars, feature_names, (rmu, rsd)); rebuilt[~rmask] = 0.0
    if not np.allclose(rebuilt, event_reco, atol=1e-5):
        raise AssertionError("event_reco is NOT a pure function of reco_scalars+pass_reco (leak?)")
    tblock = _event_block(truth_scalars, feature_names, (rmu, rsd)); tblock[~rmask] = 0.0
    if np.allclose(tblock, event_reco, atol=1e-5):
        raise AssertionError("event_reco equals the truth block -- truth leaked into step 1")
    return True


def build_fullevent_loaders(inputs_npz, max_events=None, seed=0, bootstrap_seed=None,
                            feature_names=DEFAULT_EVT_FEATURES, rank=0, size=1,
                            enforce_fps_edges=True):
    """Assemble paired full-event (cloud + continuous event feature) DataLoaders on the FPS
    domain. Returns (data, mc, imc, coord_reco, coord_gen, meta). Mirrors the recoil-only
    build_loaders subsample/bootstrap contract, but sets reco_evt/gen_evt on the loaders and
    keeps the truth PDG + angular geometry. FPS edges are asserted (fail closed) unless
    enforce_fps_edges=False (tests with synthetic edges)."""
    from omnifold.dataloader import DataLoader   # pure-numpy; avoids importing TF here

    d = np.load(inputs_npz, allow_pickle=True)
    if enforce_fps_edges:
        assert_extended_fps_edges(d["edges_0"], d["edges_1"])

    # Subsample RAW rows BEFORE the (heavy) cloud processing so build_truth_cloud's angular
    # transform + concat only touch the training subset (a full 49.2M process would spike
    # tens of GB). This is the TRAINING-subsample builder; the P5B production path adds the
    # full-sample reweight-all + coherent-draw bootstrap + memmap (as the recoil-only loader
    # did), documented in the launch plan.
    N = np.asarray(d["pass_reco"]).shape[0]
    M = np.asarray(d["measured_weights"]).shape[0]
    imc = np.arange(N); ida = np.arange(M)
    if max_events is not None:
        rng = np.random.default_rng(seed)
        imc = np.sort(rng.choice(N, min(max_events, N), replace=False))
        ida = np.sort(rng.choice(M, min(max_events, M), replace=False))

    reco_cloud, coord_reco = build_reco_cloud(np.asarray(d["part_reco"])[imc])
    gen_cloud, coord_gen = build_truth_cloud(np.asarray(d["part_gen"])[imc])
    meas_cloud, _ = build_reco_cloud(np.asarray(d["measured_pc"])[ida])
    reco_scalars = np.asarray(d["reco_scalars"])[imc]
    truth_scalars = np.asarray(d["truth_scalars"])[imc]
    meas_scalars_src = d["measured_scalars"] if "measured_scalars" in d.files else d["reco_scalars"]
    meas_scalars = np.asarray(meas_scalars_src)[ida]
    pass_reco = np.asarray(d["pass_reco"])[imc]
    pass_truth = np.asarray(d["pass_truth"])[imc]
    event_reco, event_truth, event_data, meta = build_event_features(
        reco_scalars, truth_scalars, meas_scalars, feature_names,
        pass_reco=pass_reco, pass_truth=pass_truth)
    assert_no_truth_leakage(event_reco, reco_scalars, truth_scalars, feature_names,
                            pass_reco=pass_reco)
    w_truth = np.asarray(d["w_truth"]).astype(np.float32)[imc]
    measured_weights = np.asarray(d["measured_weights"]).astype(np.float32)[ida]

    if bootstrap_seed is not None:
        from pet_bootstrap import poisson_event_weights
        measured_weights, w_truth = poisson_event_weights(
            measured_weights, w_truth, int(bootstrap_seed))

    data = DataLoader(reco=meas_cloud, weight=measured_weights, normalize=True,
                      reco_evt=event_data)
    mc = DataLoader(reco=reco_cloud, gen=gen_cloud, pass_reco=pass_reco, pass_gen=pass_truth,
                    weight=w_truth, normalize=True, reco_evt=event_reco, gen_evt=event_truth,
                    rank=rank, size=size)
    return data, mc, imc, coord_reco, coord_gen, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True, help="FPS point-cloud npz (xps2 scaffolding)")
    ap.add_argument("--max-events", type=int, default=None)
    ap.add_argument("--no-fps-guard", action="store_true")
    a = ap.parse_args()
    data, mc, imc, cr, cg, meta = build_fullevent_loaders(
        a.inputs, max_events=a.max_events, enforce_fps_edges=not a.no_fps_guard)
    print(f"[fullevent] reco cloud {np.asarray(mc.reco).shape} coord_reco={cr} "
          f"reco_evt {np.asarray(mc.reco_evt).shape}")
    print(f"[fullevent] gen  cloud {np.asarray(mc.gen).shape} coord_gen={cg} "
          f"gen_evt {np.asarray(mc.gen_evt).shape}")
    print(f"[fullevent] data cloud {np.asarray(data.reco).shape} data_evt "
          f"{np.asarray(data.reco_evt).shape}")
    print(f"[fullevent] event-feature meta: {meta}")

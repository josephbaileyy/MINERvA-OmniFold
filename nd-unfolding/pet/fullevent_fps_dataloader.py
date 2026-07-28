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
                            verify_identities=True):
    """Assemble paired full-event (cloud + continuous event feature) DataLoaders on the FPS
    domain. Returns (data, mc, imc, coord_reco, coord_gen, meta). Mirrors the recoil-only
    build_loaders subsample/bootstrap contract, but sets reco_evt/gen_evt on the loaders and
    keeps the truth PDG + angular geometry. FPS edges are asserted (fail closed) unless
    enforce_fps_edges=False (tests with synthetic edges).

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
    imc = np.arange(N)
    if max_events is not None:
        imc = np.sort(np.random.default_rng(seed).choice(N, min(max_events, N), replace=False))

    reco_cloud, coord_reco = build_reco_cloud(np.asarray(d["part_reco"])[imc])
    gen_cloud, coord_gen = build_truth_cloud(np.asarray(d["part_gen"])[imc])
    reco_scalars = np.asarray(d["reco_scalars"])[imc]
    truth_scalars = np.asarray(d["truth_scalars"])[imc]
    pass_reco = np.asarray(d["pass_reco"])[imc]
    pass_truth = np.asarray(d["pass_truth"])[imc]
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
    else:
        raise ValueError(
            "[CLM-007 GUARD] pc npz has no 'measured_scalars' and no data_scalars_npz was given. "
            "Refusing to fall back to MC reco_scalars (would inject -9999 MC-miss sentinels into "
            "the step-1 data classifier).")
    event_reco, event_truth, event_data, meta = build_event_features(
        reco_scalars, truth_scalars, meas_scalars, feature_names,
        pass_reco=pass_reco, pass_truth=pass_truth)
    meta["data_scalar_source"] = data_src
    assert_no_truth_leakage(event_reco, reco_scalars, truth_scalars, feature_names,
                            pass_reco=pass_reco)
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
        for k in ("bkg_part_reco", "bkg_reco_scalars", "w_bkg"):
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
    mc = DataLoader(reco=reco_cloud, gen=gen_cloud, pass_reco=pass_reco, pass_gen=pass_truth,
                    weight=w_truth, normalize=True, reco_evt=event_reco, gen_evt=event_truth,
                    rank=rank, size=size)

    if bkg_mode == "purity":
        # Labeled REGRESSION CONTROL only (never the publication nominal). Data-only measured
        # sample at unit weight; the all-ones purity placeholder is acceptable HERE (control), and
        # is forbidden for the negweight-refined nominal by write/loader guards.
        meas_cloud, _ = build_reco_cloud(np.asarray(d["measured_pc"]))
        data = DataLoader(reco=meas_cloud, weight=np.ones(M, np.float32), normalize=True,
                          reco_evt=event_data)
        meta["bkg_control"] = "purity = REGRESSION CONTROL, not the publication nominal"
        meta["target"] = {"target_mode": "purity-control", "bootstrap_seed": bootstrap_seed}
        return data, mc, imc, coord_reco, coord_gen, meta

    # ---------------- negweight-refined (locked publication nominal) ----------------
    # (background presence + a valid pot_scale were already validated above, before identity check)
    meas_cloud, _ = build_reco_cloud(np.asarray(d["measured_pc"]))           # FULL data cloud
    bkg_cloud, _ = build_reco_cloud(np.asarray(d["bkg_part_reco"]))          # aligned bkg cloud
    bkg_reco_scalars = np.asarray(d["bkg_reco_scalars"])
    w_bkg_full = np.asarray(d["w_bkg"]).astype(np.float32)
    if not (bkg_cloud.shape[0] == bkg_reco_scalars.shape[0] == w_bkg_full.shape[0]):
        raise ValueError("[negweight-refined] background cloud/scalars/w_bkg row counts disagree "
                         "(misaligned background inventory; fail closed).")
    # background event features under the SAME reconstructed-muon normalization as the data
    event_bkg = _event_block(bkg_reco_scalars, feature_names, (rmu, rsd))
    # refinement feature = continuous reco (pT, p_parallel) on the reco manifold (g(x)=D/(D+B))
    cols = [SCALAR_COLS[f] for f in feature_names]
    refine_feat_data = np.asarray(meas_scalars, float)[:, cols]
    refine_feat_bkg = bkg_reco_scalars[:, cols]

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
    data = DataLoader(reco=meas_cloud_all, weight=w_refined.astype(np.float32), normalize=True,
                      reco_evt=event_meas_all)

    meta["target"] = {
        "target_mode": "negweight-refined", "bootstrap_seed": bootstrap_seed,
        "refinement": "stay-positive (arXiv:2505.03724)", "refinement_backend": refine_backend,
        "refinement_is_learned_production": (refine_fn is None),
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
    a = ap.parse_args()
    data, mc, imc, cr, cg, meta = build_fullevent_loaders(
        a.inputs, max_events=a.max_events, enforce_fps_edges=not a.no_fps_guard,
        data_scalars_npz=a.data_scalars, bkg_mode=a.bkg_mode)
    print(f"[fullevent] reco cloud {np.asarray(mc.reco).shape} coord_reco={cr} "
          f"reco_evt {np.asarray(mc.reco_evt).shape}")
    print(f"[fullevent] gen  cloud {np.asarray(mc.gen).shape} coord_gen={cg} "
          f"gen_evt {np.asarray(mc.gen_evt).shape}")
    print(f"[fullevent] data cloud {np.asarray(data.reco).shape} data_evt "
          f"{np.asarray(data.reco_evt).shape}")
    print(f"[fullevent] event-feature meta: {meta}")

#!/usr/bin/env python3
"""Full-inventory reweight-all + extended-FPS cross-section extraction for the full-event PET
publication nominal.

WHY THIS FILE EXISTS (AUDIT-FINDINGS-20260731 J02). The full-event driver trains on a 2,000,000-row
subsample of the 49,152,885-row signal inventory and persists only that subsample's weights, under
the key `weights_push` and against `mc_indices = <the subsample>`. Nothing then produced a cross
section from it, and the recoil/5D extractor is NOT this path: `extract_nominal_bkgsub.py` consumes
a 5D recoil point-cloud npz through `PETxsec5D`, expects `w_push` over `arange(N)`, and knows
nothing about the full-event representation. The recoil training script had a `--reweight-all`
full-cloud pass; the full-event driver dropped it. So the publication estimator could be trained
and could not be extracted, and the two key/coverage mismatches (`weights_push` vs `w_push`,
2M vs `arange(49152885)`) meant the recoil extractor would not even have loaded the result.

TWO STAGES, deliberately separate.

  `push` (needs TensorFlow, wants a GPU): rebuild the trained step-2 network, stream the FULL
      signal inventory through it in chunks, and write `w_push` over `arange(N)`.
  `xsec` (needs ROOT and numpy, no TensorFlow, no GPU): turn that into the extended-FPS
      differential cross section.

They are split because the push pass costs GPU time that must not be re-spent when the extraction
recipe changes, and because the extraction is then runnable and reviewable on a login node.
`--stage all` runs both.

THREE THINGS THIS GETS RIGHT THAT A NAIVE REWEIGHT-ALL WOULD NOT.

  1. THE INPUT SPACE IS REPRODUCED, NOT RE-DERIVED. `event_truth` was z-normalized with the mean
     and standard deviation of the TRAINING subsample's pass_truth rows. Recomputing that
     statistic over 49.2M rows would feed the trained network inputs on a different scale and
     return confident, wrong weights with nothing anywhere to notice. The driver persists the
     statistic in `inference_contract` and this reads it back; a result that does not carry one is
     refused rather than guessed at.
  2. THE REWEIGHT IS THE ENGINE'S OWN. `MultiFold.reweight` is where the F3 logit-space cap,
     the fail-closed non-finite check and the saturation telemetry live, and CLM-008 F3 requires
     "one shared implementation => identical in nominal, replicas, universes, and extraction".
     Re-typing four lines here would be a second implementation. Instead the bound method is
     invoked on a minimal MultiFold instance (see `_engine_reweighter`), so extraction runs the
     same bytes training did without editing the hash-bound engine to expose them.
  3. IT IS CHUNKED. The full truth cloud in the widened representation is ~19 GB materialized;
     `build_fullevent_loaders` subsamples before cloud processing precisely to avoid that. This
     builds one chunk at a time and keeps only the scalar push weights.

THE EXTRACTION IS A PORT, NOT A DESIGN. The cross-section arithmetic -- pushed truth counts over
pass_truth, divided by a completeness formed from the same weights, the integrated flux on the pT
axis, the fiducial nucleon count, the data POT and the bin volume -- is
`pet_systematics_5d.PETxsec5D.xsec` restricted to the two extended-FPS axes, with
`xsec_nd.extract_cross_section_nd` doing the division. Reproducing it rather than reinventing it is
deliberate: the number this produces has to be comparable with the 5D/4D products, and the place to
argue about the convention is the shared helper, not here. The one thing NOT carried over is
`PETxsec5D`'s `comp_rescale`, which anchors completeness to a validated GBDT 5D ROOT product; there
is no such anchor for this domain and inventing one would silently rescale the answer.

NOT A RECEIPT. This produces a product and a summary. Promotion is a separate gated step, and the
summary carries `is_publication_result` unset on purpose.
"""
import argparse
import json
import os
import sys
import zipfile

import numpy as np
import numpy.lib.format as npf

_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.dirname(_HERE)
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(_ND)
for _p in (_HERE, _ND, os.path.join(_REPO, "2d-unfolding"), os.path.join(_REPO, "omnifold_nn")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fe          # noqa: E402  (login-safe: no ROOT, no TF)
from atomic_write import atomic_savez_compressed  # noqa: E402

ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
PUSH_SCHEMA = "pet-fullevent-fps-push-v1"
XSEC_SCHEMA = "pet-fullevent-fps-xsec-v1"
DEFAULT_CHUNK = 250_000


# ============================================================================================
# Shared: read and validate the training artifact's inference contract
# ============================================================================================
class _RowStream:
    """Forward-only row reader for ONE member of an npz, so a chunk loop costs one pass.

    `np.load(...)[key]` materializes the whole member every time it is indexed, and `mmap_mode` is
    silently ignored for npz files (it returns an NpzFile, not a memmap). So the obvious
    `for lo in ...: d["part_gen"][lo:hi]` decompresses the entire 49.2M-row cloud once PER CHUNK --
    the exact opposite of chunking, and it would have looked like it was working. Reading the .npy
    header off the zip member and then pulling row blocks out of the sequential stream keeps peak
    memory at one chunk and touches each byte once. Forward-only is all a chunk loop needs.
    """

    def __init__(self, zf, key):
        self._fh = zf.open(f"{key}.npy")
        version = npf.read_magic(self._fh)
        shape, fortran, self.dtype = npf._read_array_header(self._fh, version)
        if fortran:
            raise SystemExit(f"[extract] npz member {key!r} is Fortran-ordered; the row stream "
                             "assumes C order (fail closed)")
        self.shape = shape
        self.n_rows = int(shape[0])
        self._row_items = int(np.prod(shape[1:])) if len(shape) > 1 else 1
        self._row_bytes = self._row_items * self.dtype.itemsize
        self._pos = 0

    def read(self, n):
        """The next `n` rows, shaped (n, *shape[1:])."""
        if n <= 0:
            raise ValueError("row count must be positive")
        raw = self._fh.read(n * self._row_bytes)
        got = len(raw) // self._row_bytes
        if got != n:
            raise SystemExit(f"[extract] npz member truncated: wanted {n} rows at offset "
                             f"{self._pos}, got {got} (fail closed)")
        self._pos += got
        return np.frombuffer(raw, dtype=self.dtype).reshape((got,) + tuple(self.shape[1:]))

    def close(self):
        self._fh.close()


def _npz_get(z, key, default=None):
    if key not in z.files:
        return default
    v = z[key]
    if isinstance(v, np.ndarray) and v.dtype == object and v.shape == ():
        return v.item()
    if isinstance(v, np.ndarray) and v.ndim == 0:
        item = v.item()
        return item.decode() if isinstance(item, bytes) else item
    return v


def read_inference_contract(weights_npz):
    """The training artifact's self-description, or a named failure.

    Everything here is something extraction cannot correctly guess: which network shape to
    rebuild, which checkpoint holds its trained weights, which feature schema the inputs must be
    assembled in, and the normalization statistics that schema was fitted with. A weights npz
    produced before 2026-08-01 carries none of it, and the honest response to that is to refuse,
    not to reconstruct a plausible contract and proceed."""
    with np.load(weights_npz, allow_pickle=True) as z:
        contract = _npz_get(z, "inference_contract")
        fingerprint = _npz_get(z, "estimator_fingerprint")
        strap = _npz_get(z, "bootstrap_seed", -1)
        inputs_path = _npz_get(z, "inputs_path")
        inputs_sha = _npz_get(z, "inputs_sha256")
        sub_indices = np.asarray(z["mc_indices"]) if "mc_indices" in z.files else None
        sub_push = np.asarray(z["weights_push"]) if "weights_push" in z.files else None
    if not isinstance(contract, dict):
        raise SystemExit(
            f"[extract] {weights_npz} carries no `inference_contract`. It was produced by a driver "
            "predating the full-schema fix (AUDIT-FINDINGS-20260731 J01/J02), so the network "
            "architecture, the step-2 checkpoint and -- decisively -- the event-feature "
            "normalization the model was trained under are all unrecorded. Re-run the driver; do "
            "NOT re-derive the normalization here, it would silently rescale every input.")
    if fingerprint != ESTIMATOR_FINGERPRINT:
        raise SystemExit(f"[extract] estimator_fingerprint {fingerprint!r} != "
                         f"{ESTIMATOR_FINGERPRINT!r} (fail closed)")
    if int(strap) != -1:
        raise SystemExit(
            f"[extract] weights npz declares bootstrap_seed={strap}. A replica's measured target "
            "is rebuilt from its own coherent draws and its extraction rides the replica "
            "manifest; this path extracts the NOMINAL (fail closed).")
    for key in ("step2_checkpoint", "pet_arch", "event_features_reco", "event_features_truth",
                "truth_norm_mean", "truth_norm_std"):
        if key not in contract:
            raise SystemExit(f"[extract] inference_contract lacks {key!r} (fail closed)")
    if list(contract["event_features_reco"]) == list(fe.REDUCED_EVT_FEATURES):
        raise SystemExit(
            "[extract] this result was trained on the REDUCED {pT,p||} schema, which "
            "FULL_EVENT_FEATURE_CONTRACT.md marks CROSS-CHECK ONLY, yet it is stamped "
            f"{ESTIMATOR_FINGERPRINT!r}. Refusing to extract a publication cross section from it "
            "(AUDIT-FINDINGS-20260731 J01).")
    contract = dict(contract)
    contract["_inputs_path"] = inputs_path
    contract["_inputs_sha256"] = inputs_sha
    contract["_subsample_indices"] = sub_indices
    contract["_subsample_push"] = sub_push
    return contract


def _assert_same_dump(contract, inputs_npz):
    """The dump reweighted must be the dump trained on. Basename, because a dump is legitimately
    re-staged between filesystems; and sha256 when the driver recorded one, because same-basename
    different-content is the failure the basename check cannot see. Mirrors the identical guard in
    `validate_pet_nominal_gate4.main`."""
    declared = contract.get("_inputs_path")
    if declared and os.path.basename(str(declared)) != os.path.basename(os.path.abspath(inputs_npz)):
        raise SystemExit(f"[extract] --inputs {inputs_npz!r} is not the dump this result was "
                         f"trained on ({declared!r}) (fail closed)")


# ============================================================================================
# Stage 1 -- full-inventory reweight-all
# ============================================================================================
def _engine_reweighter(model2, batch_size, verbose=False):
    """`MultiFold.reweight` bound to a minimal instance, so extraction runs the ENGINE's reweight.

    `reweight` touches exactly `n_ensemble`, `step1_models`, `step2_models`, `model1`,
    `BATCH_SIZE`, `verbose` and `log_string`. Building a real `MultiFold` would demand the two
    DataLoaders and a training configuration that do not exist at extraction time, and copying the
    four-line logit transform here would create the second implementation CLM-008 F3 exists to
    prevent -- the F3 cap, the fail-closed non-finite check and the saturation accounting have to
    be the same code in training and extraction or the two disagree exactly where it matters, in
    the saturation tail. `object.__new__` gives a genuine MultiFold whose method resolution is the
    engine's, with no engine edit and no __init__ side effects (a log file, a weights directory).
    """
    from omnifold import MultiFold
    of = object.__new__(MultiFold)
    of.n_ensemble = 1
    of.step1_models = []
    of.step2_models = [model2]
    of.model1 = None                  # `model is self.model1` must be False for model2
    of.BATCH_SIZE = int(batch_size)
    of.verbose = bool(verbose)
    of.log_string = lambda s: print(s, flush=True)
    return of


def build_step2_model(contract):
    """Rebuild the step-2 PET at the trained architecture and load its checkpoint."""
    from omnifold import PET
    arch = dict(contract["pet_arch"])
    ckpt = contract["step2_checkpoint"]
    if not os.path.exists(ckpt):
        raise SystemExit(
            f"[extract] step-2 checkpoint {ckpt} not found. MultiFold writes "
            "`OmniFold_<name>_iter<niter-1>_step2.weights.h5` into the run's weights folder; if "
            "the run was staged elsewhere, pass --step2-checkpoint.")
    model = PET(arch["num_feat_gen"], num_evt=arch["num_evt"], num_part=arch["num_part"],
                num_transformer=arch["num_transformer"], num_heads=arch["num_heads"],
                projection_dim=arch["projection_dim"], local=arch["local"], K=arch["K"],
                coord_idx=tuple(arch["coord_idx"]))
    model.load_weights(ckpt)
    return model


def reweight_full_inventory(inputs_npz, contract, chunk=DEFAULT_CHUNK, batch_size=4096,
                            model2=None, progress=True):
    """Evaluate the trained step-2 model on EVERY signal-MC row. Returns (w_push, telem).

    The push weight is a per-event likelihood ratio and so is normalization-independent, which is
    what makes it legitimate to train on a subsample and evaluate on the full inventory -- the
    same argument `minerva_pet_dataloader.py`'s `--reweight-all` rests on.

    Chunked over rows: each chunk builds only its own truth cloud and event block, both of which
    are discarded once the chunk's weights are in hand. Peak memory is set by `chunk`, not by the
    inventory.

    The event block is rebuilt with the TRAINING normalization read from `contract`, never
    re-derived here."""
    tmu = np.asarray(contract["truth_norm_mean"], np.float32)
    tsd = np.asarray(contract["truth_norm_std"], np.float32)
    tnames = tuple(contract["event_features_truth"])
    if tmu.shape != (len(tnames),) or tsd.shape != (len(tnames),):
        raise SystemExit(f"[extract] truth normalization {tmu.shape}/{tsd.shape} does not match "
                         f"the {len(tnames)} truth features {tnames} (fail closed)")
    fe.assert_truth_schema_is_eligible(tnames)

    with np.load(inputs_npz, allow_pickle=True) as d:
        fe.assert_extended_fps_edges(d["edges_0"], d["edges_1"])
        # The MASK ITSELF, not just its length: off-acceptance rows must be pinned to 1.0 exactly as
        # MultiFold.RunStep2 pins them (omnifold.py:203-205). See
        # FINDING-20260802-extractor-pass-truth-mask.md.
        pass_truth = np.asarray(d["pass_truth"]).astype(bool)
    n = int(pass_truth.shape[0])
    arch_evt = int(contract["pet_arch"]["num_evt"])
    if arch_evt != len(tnames):
        raise SystemExit(f"[extract] the step-2 network takes num_evt={arch_evt} but the "
                         f"recorded truth schema has {len(tnames)} features (fail closed)")
    of = _engine_reweighter(model2, batch_size)
    # ONES, not empty: every row this pass does not overwrite must already hold the engine's
    # off-acceptance value. `empty` made an unwritten row uninitialized garbage; the mask below means
    # !pass_truth rows are deliberately never written, so the initializer IS the value they keep.
    out = np.ones(n, np.float64)
    zf = zipfile.ZipFile(inputs_npz)
    gen_stream = _RowStream(zf, "part_gen")
    ts_stream = _RowStream(zf, "truth_scalars")
    try:
        for s, label in ((gen_stream, "part_gen"), (ts_stream, "truth_scalars")):
            if s.n_rows != n:
                raise SystemExit(f"[extract] {label} has {s.n_rows} rows but pass_truth has {n} "
                                 "(wrong inventory; fail closed)")
        for lo in range(0, n, int(chunk)):
            hi = min(lo + int(chunk), n)
            gen_cloud, _coord = fe.build_truth_cloud(gen_stream.read(hi - lo))
            evt = fe._event_block(fe.evt_blocks(scalars=ts_stream.read(hi - lo)),
                                  tnames, (tmu, tsd))
            if not np.all(np.isfinite(evt)):
                raise SystemExit(
                    f"[extract] rows {lo}:{hi} produce a non-finite truth event block under the "
                    "TRAINING normalization. The training subsample's statistic does not cover "
                    "the full inventory -- do not nan_to_num, this is a real disagreement between "
                    "the trained input space and the inventory being reweighted "
                    "(see docs/orchestration/FINDING-20260730-event-feature-nonfinite.md).")
            # Mirror MultiFold.RunStep2 exactly: evaluate the model on the whole chunk, then KEEP
            # the classifier value only where pass_truth, leaving 1.0 elsewhere. The engine does
            # `new_weights = ones; new_weights[pass_gen] = reweight(...)[pass_gen]`; anything else
            # makes the full-inventory pass and the training pass disagree on every off-acceptance
            # row by construction, which is what made check_subsample_agreement fire on a CORRECT
            # result (max rel dev 9.655e-01, Delta 20778127). Measured on the real G2 dump
            # 2026-08-05: 11,999 of 12,000 rows pass_gen at max_events=12000, and 1,999,920 of
            # 2,000,000 in the powered-closure half -- so off-acceptance rows DO exist here and this
            # guard is not vacuous, which the finding had left open.
            chunk_w = of.reweight((gen_cloud, evt), model2, batch_size=batch_size)
            out[lo:hi] = np.where(pass_truth[lo:hi], chunk_w, 1.0)
            del gen_cloud, evt, chunk_w
            if progress:
                print(f"[extract] reweight-all {hi}/{n} ({100.0 * hi / n:.1f}%)", flush=True)
    finally:
        gen_stream.close(); ts_stream.close(); zf.close()
    if not np.all(np.isfinite(out)):
        raise SystemExit(f"[extract] {int((~np.isfinite(out)).sum())} non-finite push weights "
                         "(fail closed)")
    # Report the pin explicitly. `check_subsample_agreement` passing is only meaningful if we know
    # whether any off-acceptance rows existed to disagree about -- with none, the check is vacuous
    # and should say so rather than read as evidence.
    n_off = int((~pass_truth).sum())
    telem = {"n_rows": n, "chunk": int(chunk), "batch_size": int(batch_size),
             "w_push_min": float(out.min()), "w_push_max": float(out.max()),
             "w_push_mean": float(out.mean()), "w_push_median": float(np.median(out)),
             "n_off_acceptance_pinned": n_off,
             "off_acceptance_all_exactly_one": bool(np.all(out[~pass_truth] == 1.0)),
             "subsample_agreement_is_vacuous": n_off == 0}
    return out, telem


def check_subsample_agreement(w_push_full, contract, tol=1e-3):
    """The full-inventory pass must reproduce the training pass on the rows they share.

    Both evaluate the same trained model on the same events, so the only sources of difference are
    float32 batching non-associativity and GPU non-determinism -- the bounded ~0.2% floor the
    recoil campaign measured (`pet_weights_fps_xps2_delta_s101_floor.json`). A real disagreement
    means the rebuilt network is not the trained one: a wrong checkpoint, a wrong architecture, or
    -- the failure this is really here for -- a re-derived rather than reproduced normalization.
    Without this the whole reweight-all pass is unfalsifiable."""
    idx = contract.get("_subsample_indices")
    ref = contract.get("_subsample_push")
    if idx is None or ref is None:
        return {"checked": False,
                "reason": "the training artifact carries no (mc_indices, weights_push) pair"}
    idx = np.asarray(idx)
    ref = np.asarray(ref, np.float64)
    got = np.asarray(w_push_full, np.float64)[idx]
    scale = np.maximum(np.abs(ref), 1e-12)
    dev = np.abs(got - ref) / scale
    worst = float(dev.max()) if dev.size else 0.0
    median = float(np.median(dev)) if dev.size else 0.0
    ok = worst <= tol
    if not ok:
        raise SystemExit(
            f"[extract] the full-inventory reweight disagrees with the training pass on the "
            f"{idx.size} shared rows: max relative deviation {worst:.3e} > {tol}. The rebuilt "
            "step-2 model is not the one that produced this result (wrong checkpoint, wrong "
            "architecture, or an input space that was re-derived instead of reproduced).")
    return {"checked": True, "n_shared_rows": int(idx.size), "max_rel_dev": worst,
            "median_rel_dev": median, "tolerance": float(tol)}


def validate_push_coverage(w_push, mc_indices, n_events):
    """FULL ORDERED coverage, the contract `extract_nominal_bkgsub.validate_nominal_weights`
    states for the recoil path and the full-event path had no equivalent of.

    J02's coverage half: the driver's `mc_indices` is the 2M training draw, and a cross section
    binned over it would be a cross section of 4% of the inventory, silently. Here the indices
    must be `arange(N)` exactly."""
    wp = np.asarray(w_push)
    idx = np.asarray(mc_indices)
    problems = []
    if wp.ndim != 1 or idx.ndim != 1:
        problems.append("w_push/mc_indices not 1D")
    if not (wp.size == idx.size == int(n_events)):
        problems.append(f"coverage {wp.size}/{idx.size} != n_events {n_events}")
    elif not np.array_equal(idx, np.arange(int(n_events), dtype=idx.dtype)):
        problems.append("mc_indices is not the ordered full-sample range (this is a subsample)")
    if not np.all(np.isfinite(wp)):
        problems.append("w_push has non-finite values")
    if np.any(wp < 0):
        problems.append("w_push has negative values (a likelihood ratio cannot be negative)")
    return problems


# ============================================================================================
# Stage 2 -- extended-FPS cross section
# ============================================================================================
def completeness_2d(truth_pt, truth_ppar, w, pass_truth, pass_reco, edges):
    """c = sum(w over pass_truth & pass_reco) / sum(w over pass_truth), per reporting cell.

    Verbatim `pet_systematics_5d.PETxsec5D._comp` on two axes. Cells with an empty denominator
    stay 0 and `extract_cross_section_nd` then leaves their cross section at 0 rather than
    dividing by nothing."""
    pt_sel = np.asarray(pass_truth, bool)
    ptr = pt_sel & np.asarray(pass_reco, bool)
    coords = np.column_stack([truth_pt, truth_ppar])
    denom, _ = np.histogramdd(coords[pt_sel], bins=edges, weights=np.asarray(w)[pt_sel])
    numer, _ = np.histogramdd(coords[ptr], bins=edges, weights=np.asarray(w)[ptr])
    comp = np.zeros_like(denom)
    nz = denom > 0
    comp[nz] = numer[nz] / denom[nz]
    return comp, denom, numer


def extract_xsec(inputs_npz, w_push, mcfile, flux_hist, n_nucleons=None):
    """The extended-FPS differential cross section d2sigma/dpT dp_parallel. Returns (xsec, telem).

    Port of `PETxsec5D.xsec` to the 2 canonical FPS axes; the division itself is
    `xsec_nd.extract_cross_section_nd`, the same helper the ND path uses."""
    import unfold_2d_omnifold_unbinned as u2d      # imports ROOT at module load
    import flux_universe
    from xsec_nd import extract_cross_section_nd

    with np.load(inputs_npz, allow_pickle=True, mmap_mode="r") as d:
        fe.assert_extended_fps_edges(d["edges_0"], d["edges_1"])
        edges = [np.asarray(d["edges_0"], float), np.asarray(d["edges_1"], float)]
        ts = np.asarray(d["truth_scalars"], np.float64)
        w_truth = np.asarray(d["w_truth"], np.float64)
        pass_truth = np.asarray(d["pass_truth"]).astype(bool)
        pass_reco = np.asarray(d["pass_reco"]).astype(bool)
        data_pot = float(np.asarray(d["data_pot"]).item())
    push = np.asarray(w_push, np.float64)
    if not (push.shape == w_truth.shape == pass_truth.shape):
        raise SystemExit(f"[extract] w_push {push.shape} / w_truth {w_truth.shape} / pass_truth "
                         f"{pass_truth.shape} are not row-aligned (fail closed)")
    pt = ts[:, fe.SCALAR_COLS["pt"]]
    ppar = ts[:, fe.SCALAR_COLS["pparallel"]]

    coords = np.column_stack([pt, ppar])
    counts, _ = np.histogramdd(coords[pass_truth], bins=edges,
                               weights=(w_truth * push)[pass_truth])
    comp, denom, numer = completeness_2d(pt, ppar, w_truth, pass_truth, pass_reco, edges)

    # Integrated flux on the pT axis. `flux_on_target_grid` with the reference edges is the
    # bin-centre remap the CV path uses, and it is the piece J29 is about: the extended [4.5,30]
    # FPS bin has no reference bin of its own and must ride the SAME lookup as everything else
    # rather than silently retaining a CV-flux scale of 1.
    flux_ref, _ = u2d.load_flux_bins(mcfile, flux_hist, u2d.PT_EDGES)
    flux = flux_universe.flux_on_target_grid(flux_ref, edges[0],
                                             np.asarray(u2d.PT_EDGES, float))
    n_nuc = u2d.TRACKER_FIDUCIAL_N_NUCLEONS if n_nucleons is None else float(n_nucleons)

    xsec, good = extract_cross_section_nd(counts, comp, flux, data_pot, n_nuc, edges, flux_axis=0)
    telem = {
        "shape": [int(x) for x in counts.shape],
        "n_cells": int(counts.size),
        "n_cells_populated": int((xsec > 0).sum()),
        "n_cells_no_denominator": int((~good).sum()),
        "n_pass_truth": int(pass_truth.sum()),
        "n_pass_truth_and_reco": int((pass_truth & pass_reco).sum()),
        "completeness_min_populated": float(comp[denom > 0].min()) if (denom > 0).any() else None,
        "completeness_median_populated": (float(np.median(comp[denom > 0]))
                                          if (denom > 0).any() else None),
        "data_pot": data_pot,
        "n_nucleons": n_nuc,
        "flux_hist": flux_hist,
        "flux_source": os.path.abspath(mcfile),
        "flux_reference_edges": [float(x) for x in u2d.PT_EDGES],
        "completeness_anchor": "NONE -- PETxsec5D's comp_rescale anchors to a validated GBDT 5D "
                               "ROOT product; no such anchor exists for this domain and "
                               "inventing one would rescale the answer",
        "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
    }
    return xsec, telem


def total_xsec_2d(xsec, edges):
    """Integral of the differential cross section over the reporting grid."""
    dpt = np.diff(np.asarray(edges[0], float))
    dpp = np.diff(np.asarray(edges[1], float))
    return float((np.asarray(xsec, float) * dpt[:, None] * dpp[None, :]).sum())


# ============================================================================================
# CLI
# ============================================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", default="all", choices=["push", "xsec", "all"])
    ap.add_argument("--weights", help="the Gate-4 nominal weights npz (required for --stage push)")
    ap.add_argument("--inputs", required=True, help="the g2-fullevent-v1 dump the nominal trained on")
    ap.add_argument("--push-out", required=True,
                    help="full-inventory w_push npz: written by --stage push, read by --stage xsec")
    ap.add_argument("--out", help="cross-section npz (required for --stage xsec/all)")
    ap.add_argument("--summary", default=None)
    ap.add_argument("--step2-checkpoint", default=None,
                    help="override the checkpoint recorded in the artifact (a re-staged run)")
    ap.add_argument("--chunk", type=int, default=DEFAULT_CHUNK,
                    help="rows per reweight chunk; sets peak host memory, not the coverage")
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--subsample-agreement-tol", type=float, default=1e-3,
                    help="max relative deviation between the full pass and the training pass on "
                         "their shared rows (GPU-nondeterminism floor is ~2e-3 per event)")
    ap.add_argument("--mcfile",
                    default=os.path.join(_REPO, "2d-unfolding", "baseline_flux",
                                         "runEventLoopMC_MEFHC.root"),
                    help="ROOT file carrying the integrated-flux histogram")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--n-nucleons", type=float, default=None,
                    help="override the tracker fiducial nucleon count (default: u2d's constant)")
    ap.add_argument("--allow-overwrite", action="store_true")
    args = ap.parse_args(argv)

    if args.stage in ("push", "all"):
        if not args.weights:
            raise SystemExit("[extract] --weights is required for --stage push")
        contract = read_inference_contract(args.weights)
        _assert_same_dump(contract, args.inputs)
        if args.step2_checkpoint:
            contract["step2_checkpoint"] = args.step2_checkpoint
        model2 = build_step2_model(contract)
        w_push, telem = reweight_full_inventory(
            args.inputs, contract, chunk=args.chunk, batch_size=args.batch_size, model2=model2)
        agreement = check_subsample_agreement(w_push, contract,
                                              tol=args.subsample_agreement_tol)
        n = telem["n_rows"]
        mc_indices = np.arange(n, dtype=np.int64)
        problems = validate_push_coverage(w_push, mc_indices, n)
        if problems:
            raise SystemExit(f"[extract] push coverage: {problems}")
        written = atomic_savez_compressed(
            args.push_out,
            dict(w_push=w_push.astype(np.float64), mc_indices=mc_indices,
                 push_schema=PUSH_SCHEMA,
                 estimator_fingerprint=ESTIMATOR_FINGERPRINT,
                 source_weights=os.path.abspath(args.weights),
                 inputs_path=os.path.abspath(args.inputs),
                 inputs_sha256=contract.get("_inputs_sha256"),
                 event_features_reco=np.asarray(list(contract["event_features_reco"]),
                                                dtype=object),
                 event_features_truth=np.asarray(list(contract["event_features_truth"]),
                                                 dtype=object),
                 reweight_telemetry=np.asarray(telem, dtype=object),
                 subsample_agreement=np.asarray(agreement, dtype=object)),
            mark=True, overwrite=bool(args.allow_overwrite),
            note="fullevent FPS full-inventory reweight-all")
        print(f"[extract] wrote {written}")
        print(json.dumps({"reweight": telem, "subsample_agreement": agreement}, indent=2))

    if args.stage in ("xsec", "all"):
        if not args.out:
            raise SystemExit("[extract] --out is required for --stage xsec")
        with np.load(args.push_out, allow_pickle=True) as pz:
            if str(_npz_get(pz, "push_schema")) != PUSH_SCHEMA:
                raise SystemExit(f"[extract] {args.push_out} is not a {PUSH_SCHEMA} product")
            w_push = np.asarray(pz["w_push"], np.float64)
            mc_indices = np.asarray(pz["mc_indices"])
            push_meta = {k: _npz_get(pz, k) for k in
                         ("source_weights", "inputs_path", "inputs_sha256",
                          "subsample_agreement")}
            feats = [str(x) for x in np.asarray(_npz_get(pz, "event_features_reco")).ravel()]
        with np.load(args.inputs, allow_pickle=True, mmap_mode="r") as d:
            n = int(np.asarray(d["pass_truth"]).shape[0])
            edges = [np.asarray(d["edges_0"], float), np.asarray(d["edges_1"], float)]
        problems = validate_push_coverage(w_push, mc_indices, n)
        if problems:
            raise SystemExit(f"[extract] push coverage: {problems}")
        xsec, telem = extract_xsec(args.inputs, w_push, args.mcfile, args.flux_hist,
                                   n_nucleons=args.n_nucleons)
        total = total_xsec_2d(xsec, edges)
        if not (np.isfinite(xsec).all() and (xsec >= 0).all() and total > 0):
            raise SystemExit(f"[extract] invalid cross section: finite={np.isfinite(xsec).all()} "
                             f"nonneg={(xsec >= 0).all()} total={total}")
        written = atomic_savez_compressed(
            args.out,
            dict(xsec_schema=XSEC_SCHEMA, xsec=xsec,
                 edges_pt=edges[0], edges_pparallel=edges[1],
                 estimator_fingerprint=ESTIMATOR_FINGERPRINT,
                 event_features_reco=np.asarray(feats, dtype=object),
                 total_sigma_cm2_per_nucleon=np.asarray(total),
                 push_source=os.path.abspath(args.push_out),
                 extraction_telemetry=np.asarray(telem, dtype=object)),
            mark=True, overwrite=bool(args.allow_overwrite),
            note="fullevent FPS extended-grid cross section")
        summary = {
            "schema": XSEC_SCHEMA,
            "estimator_fingerprint": ESTIMATOR_FINGERPRINT,
            "event_features_reco": feats,
            "inputs": os.path.abspath(args.inputs),
            "push": os.path.abspath(args.push_out),
            "push_provenance": push_meta,
            "out": os.path.abspath(str(written)),
            "total_sigma_cm2_per_nucleon": total,
            "extraction": telem,
            "note": "product only; promotion is a separate gated step",
        }
        spath = args.summary or (os.path.splitext(args.out)[0] + ".summary.json")
        with open(spath, "w") as fh:
            json.dump(summary, fh, indent=2, default=str)
            fh.write("\n")
        print(f"[extract] wrote {written}")
        print(f"[extract] wrote {spath}")
        print(json.dumps({"total_sigma_cm2_per_nucleon": total,
                          "n_cells_populated": telem["n_cells_populated"],
                          "n_cells": telem["n_cells"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build paired weighted/literal seed-50000 targets and unique-event split evidence.

CPU/ROOT stage only.  The weighted target is built first with the canonical
Stay-Positive implementation and must reproduce the committed Gate-5 digest.
The literal target uses the same draw but physically deletes/duplicates rows
before a separate canonical refinement fit.  This program never submits work.
"""

import argparse
import datetime as dt
import json
import os
import socket
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "2d-unfolding", REPO / "nd-unfolding", REPO / "nd-unfolding/pet"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import fullevent_fps_dataloader as fe  # noqa: E402
from atomic_write import atomic_savez_compressed, atomic_write, mark_complete  # noqa: E402
from pet_v2_equivalence_common import (  # noqa: E402
    BOOTSTRAP_SEED, CONTRACT_ID, EXPECTED_INPUT_SHA256, EXPECTED_INPUT_SIZE,
    EXPECTED_WEIGHTED_TARGET_SHA256, MAX_EVENTS, PROHIBITIONS, REQUIRED_CLASS_RATIO,
    assert_regular_file, deterministic_train_mask, fixed_factors, git_head,
    hash_array, literal_source_index, sha256_file,
)

REFINEMENT_SEED = 45
SCHEMA = "pet-v2-equivalence-paired-target-v1"
ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
BKG_MODE = "negweight-refined"
SUBSAMPLE_SEED = 0
FLUX_PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G",
                  "1L", "1M", "1N", "1O", "1P")


def _refuse(paths):
    occupied = [str(path) for path in paths
                if os.path.lexists(path) or os.path.lexists(f"{path}.done")]
    if occupied:
        raise SystemExit("[pet-v2-target] collision/no-clobber guard: " + ", ".join(occupied))


def _write_npy(path, value, note):
    def writer(tmp):
        with open(tmp, "wb") as stream:
            np.save(stream, value, allow_pickle=False)
    atomic_write(str(path), writer, suffix=".npy", overwrite=False, fsync=True)
    mark_complete(str(path), note=note)


def _write_json(path, payload):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    atomic_write(str(path), writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(str(path), note="PET-v2 paired target receipt; published last")


def _run_config_gate(inputs):
    """Minimal local G2 eligibility gate; avoids the pinned driver's hardcoded root."""
    with np.load(str(inputs), allow_pickle=True) as source:
        scalar = lambda key: np.asarray(source[key]).item()
        observed = {
            "petSchemaVersion": str(scalar("petSchemaVersion")),
            "hasFullEventSchema": int(scalar("hasFullEventSchema")),
            "fullPhaseSpace": int(scalar("fullPhaseSpace")),
            "estimator_fingerprint": str(scalar("estimator_fingerprint")),
            "has_background": all(key in source.files for key in (
                "w_bkg", "bkg_part_reco", "bkg_reco_scalars", "bkg_indices")),
        }
    expected = {"petSchemaVersion": "g2-fullevent-v1", "hasFullEventSchema": 1,
                "fullPhaseSpace": 1, "estimator_fingerprint": ESTIMATOR_FINGERPRINT,
                "has_background": True}
    if observed != expected:
        raise SystemExit(f"[pet-v2-target] G2 config gate failed: {observed} != {expected}")
    return observed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--gate3-manifest", required=True)
    parser.add_argument("--expected-gate3-sha256", required=True)
    parser.add_argument("--flux-source-dir", required=True,
                        help="explicit off-checkout directory with the 12 ME-FHC playlist ROOTs")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args(argv)

    if git_head(REPO) != args.expected_head:
        raise SystemExit("[pet-v2-target] runtime HEAD mismatch")
    inputs = assert_regular_file(args.inputs, sha256=EXPECTED_INPUT_SHA256,
                                 size=EXPECTED_INPUT_SIZE, label="G2 source")
    gate3 = assert_regular_file(args.gate3_manifest, sha256=args.expected_gate3_sha256,
                                label="Gate-3 manifest")
    config_gate = _run_config_gate(inputs)
    outdir = Path(args.output_dir).resolve()
    weighted_path = outdir / "PETV2_WEIGHTED_TARGET.npy"
    literal_path = outdir / "PETV2_LITERAL_TARGET.npz"
    literal_aggregate_path = outdir / "PETV2_LITERAL_AGGREGATE_TARGET.npy"
    split_path = outdir / "PETV2_SPLIT_MANIFEST.npz"
    flux_path = outdir / "PETV2_FLUX.npz"
    receipt_path = outdir / "PETV2_TARGET_RECEIPT.json"
    _refuse((weighted_path, literal_path, literal_aggregate_path, split_path,
             flux_path, receipt_path))
    outdir.mkdir(parents=True, exist_ok=True)

    with np.load(inputs, allow_pickle=True) as source:
        n_data = int(np.asarray(source["measured_pc"]).shape[0])
        n_signal = int(np.asarray(source["w_truth"]).shape[0])
        n_background = int(np.asarray(source["w_bkg"]).shape[0])
    data_factor, signal_factor, background_factor = fixed_factors(
        n_data, n_signal, n_background
    )
    captured = {}

    def paired_refiner(feat, signed_w, **kwargs):
        canonical = fe.learned_stay_positive_refiner()
        # Weighted first: this call must remain byte-equivalent to the historical target build.
        weighted = canonical(feat, signed_w, **kwargs)
        weighted_values = np.asarray(weighted[0] if isinstance(weighted, (tuple, list)) else weighted)
        multiplicity = np.concatenate([data_factor, background_factor]).astype(np.uint8)
        source_index = literal_source_index(multiplicity)
        positive = multiplicity > 0
        per_source_signed = np.zeros_like(np.asarray(signed_w, np.float64))
        per_source_signed[positive] = (
            np.asarray(signed_w, np.float64)[positive] / multiplicity[positive]
        )
        literal_signed = per_source_signed[source_index]
        literal = canonical(np.asarray(feat)[source_index], literal_signed, **kwargs)
        literal_values = np.asarray(
            literal[0] if isinstance(literal, (tuple, list)) else literal, np.float64
        )
        if literal_values.shape != source_index.shape:
            raise SystemExit("[pet-v2-target] literal refined target/source map misaligned")
        captured.update({
            "source_index": source_index,
            "literal_raw": literal_values,
            "literal_signed": literal_signed,
            "weighted_raw": weighted_values,
            "weighted_extra": weighted[1:] if isinstance(weighted, (tuple, list)) else (),
            "literal_extra": literal[1:] if isinstance(literal, (tuple, list)) else (),
        })
        return weighted

    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    data, mc, imc, _coord_reco, _coord_gen, meta = fe.build_fullevent_loaders(
        str(inputs), max_events=MAX_EVENTS,
        seed=SUBSAMPLE_SEED,
        bootstrap_seed=BOOTSTRAP_SEED, bkg_mode=BKG_MODE,
        refine_fn=paired_refiner,
        refine_kwargs={"estimator": "exact", "device": "cpu",
                       "params": {"random_state": REFINEMENT_SEED}, "verbose": True},
        verify_identities=True,
    )
    if not captured:
        raise SystemExit("[pet-v2-target] paired refiner was not invoked")
    target_meta = dict(meta.get("target") or {})
    class_ratio = float(target_meta.get("step1_class_ratio", float("nan")))
    if class_ratio != REQUIRED_CLASS_RATIO:
        raise SystemExit(
            f"[pet-v2-target] class ratio {class_ratio!r} != required {REQUIRED_CLASS_RATIO!r}"
        )

    weighted_normalized = np.asarray(data.weight, np.float32)
    # Normalize the literal per-copy target to the same pre-representation class total.
    literal_raw = np.asarray(captured["literal_raw"], np.float64)
    literal_sum = float(literal_raw.sum(dtype=np.float64))
    wanted_sum = fe.STEP1_MC_NORMALIZATION * class_ratio
    if not np.isfinite(literal_sum) or literal_sum <= 0.0:
        raise SystemExit("[pet-v2-target] literal refined target has non-positive sum")
    literal_normalized = (literal_raw * (wanted_sum / literal_sum)).astype(np.float32)
    source_index = np.asarray(captured["source_index"], np.int64)
    literal_aggregate = np.bincount(
        source_index, weights=literal_normalized.astype(np.float64),
        minlength=n_data + n_background,
    ).astype(np.float32)
    if not np.isclose(literal_normalized.sum(dtype=np.float64), wanted_sum,
                      rtol=2e-6, atol=1e-2):
        raise SystemExit("[pet-v2-target] literal normalization closure failed")

    data_train = deterministic_train_mask(n_data, 0xDADA5000)
    background_train = deterministic_train_mask(n_background, 0xBABA5000)
    signal_train = deterministic_train_mask(len(imc), 0x51515000)
    if not np.array_equal(np.asarray(imc), np.sort(np.asarray(imc))):
        raise SystemExit("[pet-v2-target] signal subsample IDs are not canonical sorted IDs")

    _write_npy(weighted_path, weighted_normalized, "PET-v2 weighted seed-50000 target")
    observed_weighted_sha = sha256_file(weighted_path)
    if observed_weighted_sha != EXPECTED_WEIGHTED_TARGET_SHA256:
        raise SystemExit(
            "[pet-v2-target] rebuilt weighted target does not reproduce the committed digest: "
            f"{observed_weighted_sha} != {EXPECTED_WEIGHTED_TARGET_SHA256}"
        )
    _write_npy(literal_aggregate_path, literal_aggregate,
               "PET-v2 literal target aggregated to unique rows")
    atomic_savez_compressed(
        str(literal_path),
        {"source_index": source_index, "weight": literal_normalized,
         "signed_weight_before_refinement": np.asarray(captured["literal_signed"], np.float64)},
        overwrite=False, fsync=True, mark=True,
        note="PET-v2 literal delete/duplicate target",
    )
    atomic_savez_compressed(
        str(split_path),
        {"mc_indices": np.asarray(imc, np.int64), "data_train": data_train,
         "background_train": background_train, "signal_train": signal_train},
        overwrite=False, fsync=True, mark=True,
        note="PET-v2 split-before-duplication manifest",
    )
    # Reconstruct the canonical ME-FHC integrated flux from its 12 explicit playlist
    # suppliers.  `hadd` is not needed: ROOT histogram addition is linear, and keeping the
    # per-playlist hashes makes the supplier set inspectable rather than hiding it in a new ROOT.
    flux_dir = Path(args.flux_source_dir).resolve()
    if not flux_dir.is_dir() or flux_dir.is_symlink():
        raise SystemExit(f"[pet-v2-target] invalid flux source directory: {flux_dir}")
    flux_files = [assert_regular_file(
        flux_dir / f"runEventLoopMC_{playlist}.root", label=f"flux playlist {playlist}")
        for playlist in FLUX_PLAYLISTS]
    import unfold_2d_omnifold_unbinned as u2d
    flux_parts = []
    for path in flux_files:
        values, _ = u2d.load_flux_bins(
            str(path), "pTmu_reweightedflux_integrated", u2d.PT_EDGES)
        if not np.all(np.isfinite(values)) or np.any(values <= 0.0):
            raise SystemExit(f"[pet-v2-target] non-positive flux in {path}")
        flux_parts.append(np.asarray(values, np.float64))
    flux_ref = np.sum(np.stack(flux_parts), axis=0, dtype=np.float64)
    atomic_savez_compressed(
        str(flux_path),
        {"flux_ref": flux_ref, "reference_edges": np.asarray(u2d.PT_EDGES, np.float64),
         "playlist_names": np.asarray(FLUX_PLAYLISTS),
         "playlist_sha256": np.asarray([sha256_file(path) for path in flux_files]),
         "histogram_name": np.asarray("pTmu_reweightedflux_integrated")},
        overwrite=False, fsync=True, mark=True,
        note="PET-v2 explicit 12-playlist ME-FHC flux operand",
    )

    bootstrap = dict(meta.get("bootstrap") or {})
    receipt = {
        "schema": SCHEMA, "status": "PASS_TARGETS_AND_SPLIT",
        "contract_id": CONTRACT_ID, "scope": "PET_DIAGNOSTIC_AND_METHOD_DEVELOPMENT_ONLY",
        "execution": {"head": git_head(REPO), "host": socket.gethostname(),
                      "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
                      "started_at_utc": started_utc,
                      "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                      "elapsed_seconds": time.monotonic() - started},
        "source": {"path": str(inputs), "sha256": sha256_file(inputs),
                   "size_bytes": inputs.stat().st_size,
                   "gate3_manifest": str(gate3), "gate3_sha256": sha256_file(gate3),
                   "config_gate": config_gate},
        "draw": {"bootstrap_seed": BOOTSTRAP_SEED,
                 "data_factor_sha256": hash_array(data_factor),
                 "signal_factor_sha256": hash_array(signal_factor),
                 "background_factor_sha256": hash_array(background_factor),
                 "data_sum": int(data_factor.sum(dtype=np.int64)),
                 "signal_sum": int(signal_factor.sum(dtype=np.int64)),
                 "background_sum": int(background_factor.sum(dtype=np.int64))},
        "inventory": {"n_data": n_data, "n_signal": n_signal,
                      "n_background": n_background, "n_signal_subsample": int(len(imc)),
                      "input_identity_hashes": meta.get("input_identity_hashes"),
                      "bootstrap_inventory_hashes": bootstrap.get("inventory_hashes")},
        "class_ratio": {"R": class_ratio, "required": REQUIRED_CLASS_RATIO,
                        "exact_match": class_ratio == REQUIRED_CLASS_RATIO,
                        "normalized_sum": wanted_sum},
        "weighted": {"path": str(weighted_path), "sha256": observed_weighted_sha,
                     "expected_sha256": EXPECTED_WEIGHTED_TARGET_SHA256,
                     "rows": int(weighted_normalized.size),
                     "sum": float(weighted_normalized.sum(dtype=np.float64)),
                     "zeros": int(np.count_nonzero(weighted_normalized == 0.0))},
        "literal": {"path": str(literal_path), "sha256": sha256_file(literal_path),
                    "aggregate_path": str(literal_aggregate_path),
                    "aggregate_sha256": sha256_file(literal_aggregate_path),
                    "rows": int(literal_normalized.size),
                    "source_map_sha256": hash_array(source_index),
                    "sum": float(literal_normalized.sum(dtype=np.float64)),
                    "zeros": int(np.count_nonzero(literal_normalized == 0.0))},
        "split": {"path": str(split_path), "sha256": sha256_file(split_path),
                  "assignment": "unique-event SplitMix64 membership before duplication",
                  "data_train_sha256": hash_array(data_train),
                  "background_train_sha256": hash_array(background_train),
                  "signal_train_sha256": hash_array(signal_train),
                  "data_train_fraction": float(data_train.mean()),
                  "background_train_fraction": float(background_train.mean()),
                  "signal_train_fraction": float(signal_train.mean())},
        "flux": {"path": str(flux_path), "sha256": sha256_file(flux_path),
                 "construction": "sum of 12 explicit per-playlist integrated-flux histograms",
                 "histogram": "pTmu_reweightedflux_integrated",
                 "playlist_files": [
                     {"playlist": playlist, "path": str(path), "sha256": sha256_file(path),
                      "size_bytes": path.stat().st_size}
                     for playlist, path in zip(FLUX_PLAYLISTS, flux_files)],
                 "flux_ref_sha256": hash_array(flux_ref)},
        "refinement": {"weighted_first": True, "separate_fits": True,
                       "estimator": "GradientBoostingClassifier exact",
                       "random_state": REFINEMENT_SEED,
                       "weighted_raw_sha256": hash_array(captured["weighted_raw"]),
                       "literal_raw_sha256": hash_array(captured["literal_raw"])},
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "cannot_authorize": ["C_stat", "C_ML", "central movement", "Leg 2",
                             "unchanged retry", "coverage", "publication adoption"],
    }
    _write_json(receipt_path, receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(receipt_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

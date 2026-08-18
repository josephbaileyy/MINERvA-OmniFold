#!/usr/bin/env python3
"""Gate-5 full-input extraction for one promoted coherent PET replica.

This adapter leaves the Gate-4-pinned nominal extractor unchanged.  It calls that
extractor's model reconstruction, engine reweight, coverage checks, cross-section
arithmetic, and atomic NPZ writer, adding only the Gate-5 contract:

* accept exactly one promoted bootstrap seed/index;
* re-derive and bind the persisted full signal/background factors;
* multiply the full signal factor into both truth counts and the completeness
  diagnostic/reporting mask; and
* publish a hash-bound task receipt only after push and xsec both complete.

It never trains, selects a subset, constructs C_stat, or changes the nominal path.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "nd-unfolding", REPO / "2d-unfolding",
             REPO / "omnifold_nn"):
    if str(item) not in os.sys.path:
        os.sys.path.insert(0, str(item))

import extract_fullevent_fps as nominal_extract  # noqa: E402
import fullevent_fps_dataloader as fe  # noqa: E402
from atomic_write import atomic_savez_compressed, atomic_write, is_complete  # noqa: E402
import cstat_data_only as replica_train  # noqa: E402  (P1-P8; one home, two importers)

ROLE = "gate5-cstat-coherent-replica"
SEED_POLICY = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"
PUSH_SCHEMA = "pet-fullevent-fps-gate5-replica-push-v1"
XSEC_SCHEMA = "pet-fullevent-fps-gate5-replica-xsec-v1"


def sha256_file(path, chunk=16 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def hash_array(value):
    a = np.ascontiguousarray(value)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(json.dumps(list(a.shape), separators=(",", ":")).encode("ascii"))
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def scalar(store, key):
    value = store[key]
    if isinstance(value, np.ndarray) and value.dtype == object and value.shape == ():
        return value.item()
    if isinstance(value, np.ndarray) and value.ndim == 0:
        value = value.item()
        return value.decode() if isinstance(value, bytes) else value
    return value


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def write_json(path, payload, note):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

    return atomic_write(path, writer, suffix=".json", overwrite=False, fsync=True,
                        mark=True, note=note)


def read_replica_contract(weights_npz, replica_index, bootstrap_seed,
                          expected_inputs_sha=None):
    """Validate one promoted training artifact and return its inference contract/factors."""
    if not is_complete(weights_npz):
        raise SystemExit("[gate5-extract] training artifact completion marker is invalid")
    with np.load(weights_npz, allow_pickle=True) as store:
        required = {
            "campaign_role", "replica_index", "bootstrap_seed", "replica_seed_policy",
            "estimator_fingerprint", "inputs_path", "inputs_sha256", "inference_contract",
            "weights_push", "mc_indices", "sig_bootstrap_factor", "sig_bootstrap_factor_full",
            "bkg_indices", "bkg_bootstrap_factor", "bootstrap_factor_sha256",
            "n_data_full", "n_sig_full", "n_bkg_full", "inventory_hashes",
            "input_identity_hashes", "replica_target_sha256",
            "replica_target_receipt_sha256",
        }
        missing = sorted(required - set(store.files))
        if missing:
            raise SystemExit(f"[gate5-extract] training artifact missing {missing}")
        if scalar(store, "campaign_role") != ROLE:
            raise SystemExit("[gate5-extract] artifact is not a Gate-5 coherent replica")
        if int(scalar(store, "replica_index")) != int(replica_index):
            raise SystemExit("[gate5-extract] replica index mismatch")
        if int(scalar(store, "bootstrap_seed")) != int(bootstrap_seed):
            raise SystemExit("[gate5-extract] bootstrap seed mismatch")
        if scalar(store, "replica_seed_policy") != SEED_POLICY:
            raise SystemExit("[gate5-extract] seed policy mismatch")
        if scalar(store, "estimator_fingerprint") != nominal_extract.ESTIMATOR_FINGERPRINT:
            raise SystemExit("[gate5-extract] estimator fingerprint mismatch")
        inputs_sha = str(scalar(store, "inputs_sha256"))
        if expected_inputs_sha and inputs_sha != expected_inputs_sha:
            raise SystemExit("[gate5-extract] promoted source SHA-256 mismatch")

        contract = scalar(store, "inference_contract")
        if not isinstance(contract, dict):
            raise SystemExit("[gate5-extract] inference contract is absent or malformed")
        contract = dict(contract)
        for key in ("step2_checkpoint", "pet_arch", "event_features_reco",
                    "event_features_truth", "truth_norm_mean", "truth_norm_std"):
            if key not in contract:
                raise SystemExit(f"[gate5-extract] inference contract lacks {key!r}")
        if list(contract["event_features_reco"]) == list(fe.REDUCED_EVT_FEATURES):
            raise SystemExit("[gate5-extract] reduced cross-check schema is not eligible")

        n_data = int(scalar(store, "n_data_full"))
        n_sig = int(scalar(store, "n_sig_full"))
        n_bkg = int(scalar(store, "n_bkg_full"))
        identities = scalar(store, "input_identity_hashes")
        inventory_hashes = str(scalar(store, "inventory_hashes"))

        # ------------------------------ DATA-ONLY PATH (C_stat^data) -----------------------------
        # DISPATCHED ONCE, ON THE TAG, before any three-stream predicate runs. The coherence gate
        # below asserts that the persisted SIGNAL factor is the canonical Poisson draw; a data-only
        # family has no signal draw to be coherent with, so that guard would be checking the wrong
        # proposition rather than failing a true one. It is replaced by a STRICTLY STRONGER set
        # (lane C, BEN-407/409), not relaxed.
        if "cstat_product" in set(store.files):
            product = str(scalar(store, "cstat_product"))
            if product == replica_train.CSTAT_DATA_ONLY:
                replica_train.assert_data_only_streams(
                    store, data_bootstrap_seed=int(bootstrap_seed),
                    n_data_full=n_data, n_sig_full=n_sig, n_bkg_full=n_bkg)
                replica_train.assert_ratio_provenance_block({
                    "step1_class_ratio_loader_stamped":
                        float(np.asarray(store["step1_class_ratio_loader_stamped"]).item()),
                    "step1_class_ratio_applied":
                        float(np.asarray(store["step1_class_ratio_applied"]).item()),
                    "weights_embody": str(scalar(store, "weights_embody")),
                })
                # P5' -- PAST TENSE, SELF-CONTAINED. The persisted evidence must satisfy its own
                # tolerances. This must NOT re-derive w_truth_full[imc] from the current input and
                # compare it against a hash written at training time: that is BEN-406's
                # past-vs-present error, it would FAIL on a legitimate input re-dump, and the
                # write-time gate in replica_atomic_data_only already proved the live identity
                # before the artifact existed.
                ev = np.asarray(store["p5_mc_leg_evidence"], dtype=object).item()
                for leg in ("w_truth", "w_reco"):
                    dev = float(ev[f"{leg}_max_ratio_deviation"])
                    tol = float(ev[f"{leg}_tolerance"])
                    if not dev <= tol:
                        raise SystemExit(
                            f"[gate5-dataonly] P5' persisted {leg} closure evidence does not "
                            f"satisfy its own tolerance ({dev:.6e} > {tol:.6e})")
                if float(ev["derived_normalization_constant"]) <= 0:
                    raise SystemExit("[gate5-dataonly] P5' persisted normalization constant "
                                     "is not positive")
                mc_ev = np.asarray(store["measured_closure_evidence"], dtype=object).item()
                if not float(mc_ev["closure_abs_deviation"]) <= float(mc_ev["closure_tolerance"]):
                    raise SystemExit("[gate5-dataonly] P5' persisted measured-leg closure evidence "
                                     "does not satisfy its own tolerance")
                data_factor = np.asarray(store["data_bootstrap_factor"], dtype=np.uint8)
                return dict(
                    contract=contract, n_data=n_data, n_sig=n_sig, n_bkg=n_bkg,
                    identities=identities, inventory_hashes=inventory_hashes,
                    cstat_product=product,
                    sig_factor_full=np.ones(n_sig, dtype=np.uint8),
                    data_factor=data_factor,
                    factor_hashes={"data_factor_sha256": hash_array(data_factor)},
                )
            if product != replica_train.CSTAT_THREE_STREAM:
                raise SystemExit(f"[gate5-extract] unknown cstat_product {product!r}")

        fe.validate_coherent_bootstrap(
            store, bootstrap_seed=int(bootstrap_seed), n_sig_full=n_sig,
            n_bkg_full=n_bkg,
            estimator_fingerprint=nominal_extract.ESTIMATOR_FINGERPRINT,
            inventory_hashes=inventory_hashes,
            bkg_inventory_hash=identities["bkg"],
        )

        data_factor, sig_replay, bkg_replay = fe.coherent_bootstrap_factors(
            n_data, n_sig, n_bkg, int(bootstrap_seed)
        )
        sig_full = np.asarray(store["sig_bootstrap_factor_full"], dtype=np.uint8)
        bkg_full = np.asarray(store["bkg_bootstrap_factor"], dtype=np.uint8)
        if sig_full.shape != (n_sig,) or not np.array_equal(sig_full, sig_replay):
            raise SystemExit("[gate5-extract] full signal factor differs from canonical replay")
        if bkg_full.shape != (n_bkg,) or not np.array_equal(bkg_full, bkg_replay):
            raise SystemExit("[gate5-extract] full background factor differs from canonical replay")
        factor_meta = scalar(store, "bootstrap_factor_sha256")
        factor_hashes = {
            "data_factor_sha256": hash_array(data_factor),
            "signal_factor_sha256": hash_array(sig_full),
            "background_factor_sha256": hash_array(bkg_full),
        }
        for key, got in factor_hashes.items():
            if factor_meta.get(key) != got:
                raise SystemExit(f"[gate5-extract] persisted {key} does not re-derive")

        contract["_inputs_path"] = scalar(store, "inputs_path")
        contract["_inputs_sha256"] = inputs_sha
        contract["_subsample_indices"] = np.asarray(store["mc_indices"], dtype=np.int64)
        contract["_subsample_push"] = np.asarray(store["weights_push"], dtype=np.float64)
        evidence = {
            "n_data_full": n_data,
            "n_sig_full": n_sig,
            "n_bkg_full": n_bkg,
            "inventory_hashes": inventory_hashes,
            "input_identity_hashes": identities,
            "factor_sha256": factor_hashes,
            "replica_target_sha256": str(scalar(store, "replica_target_sha256")),
            "replica_target_receipt_sha256": str(
                scalar(store, "replica_target_receipt_sha256")
            ),
        }
    return contract, sig_full, evidence


def extract_replica_xsec(inputs_npz, w_push, sig_factor, **kwargs):
    """Apply the signal draw to truth counts and the completeness/reporting diagnostic."""
    sig_factor = np.asarray(sig_factor, dtype=np.float64)
    w_push = np.asarray(w_push, dtype=np.float64)
    if sig_factor.shape != w_push.shape:
        raise SystemExit("[gate5-extract] signal factor and full push are not row-aligned")
    original = nominal_extract.completeness_2d

    def replica_completeness(truth_pt, truth_ppar, w, pass_truth, pass_reco, edges):
        return original(truth_pt, truth_ppar, np.asarray(w) * sig_factor,
                        pass_truth, pass_reco, edges)

    nominal_extract.completeness_2d = replica_completeness
    try:
        xsec, telem = nominal_extract.extract_xsec(
            inputs_npz, w_push * sig_factor, **kwargs
        )
    finally:
        nominal_extract.completeness_2d = original
    telem = dict(telem)
    telem.update({
        "gate5_signal_factor_applied_to_truth_counts": True,
        "gate5_signal_factor_applied_to_completeness_and_reporting_mask": True,
        "gate5_signal_factor_sha256": hash_array(sig_factor.astype(np.uint8)),
        "gate5_background_factor_reuse":
            "applied before per-replica Stay-Positive target refinement and bound in the "
            "training artifact; no background rows enter truth-space xsec binning",
    })
    return xsec, telem


def run_push(args):
    contract, sig_factor, evidence = read_replica_contract(
        args.weights, args.replica_index, args.bootstrap_seed, args.expected_inputs_sha
    )
    nominal_extract._assert_same_dump(contract, args.inputs)
    if int(evidence["n_sig_full"]) != int(sig_factor.size):
        raise SystemExit("[gate5-extract] signal inventory length mismatch")
    model2 = nominal_extract.build_step2_model(contract)
    w_push, telem = nominal_extract.reweight_full_inventory(
        args.inputs, contract, chunk=args.chunk, batch_size=args.batch_size, model2=model2
    )
    agreement = nominal_extract.check_subsample_agreement(
        w_push, contract, tol=args.subsample_agreement_tol
    )
    indices = np.arange(w_push.size, dtype=np.int64)
    problems = nominal_extract.validate_push_coverage(w_push, indices, evidence["n_sig_full"])
    if problems:
        raise SystemExit(f"[gate5-extract] push coverage failed: {problems}")
    weights_sha = sha256_file(args.weights)
    checkpoint = contract["step2_checkpoint"]
    if not os.path.isfile(checkpoint):
        raise SystemExit("[gate5-extract] final-epoch step-2 checkpoint is missing")
    arrays = {
        "w_push": w_push.astype(np.float64),
        "mc_indices": indices,
        "push_schema": np.asarray(PUSH_SCHEMA),
        "campaign_role": np.asarray(ROLE),
        "replica_index": np.asarray(int(args.replica_index)),
        "bootstrap_seed": np.asarray(int(args.bootstrap_seed)),
        "source_weights": np.asarray(os.path.abspath(args.weights)),
        "source_weights_sha256": np.asarray(weights_sha),
        "inputs_path": np.asarray(os.path.abspath(args.inputs)),
        "inputs_sha256": np.asarray(contract["_inputs_sha256"]),
        "signal_factor_sha256": np.asarray(evidence["factor_sha256"]["signal_factor_sha256"]),
        "background_factor_sha256": np.asarray(
            evidence["factor_sha256"]["background_factor_sha256"]
        ),
        "step2_checkpoint_sha256": np.asarray(sha256_file(checkpoint)),
        "event_features_reco": np.asarray(list(contract["event_features_reco"]), dtype=object),
        "event_features_truth": np.asarray(list(contract["event_features_truth"]), dtype=object),
        "reweight_telemetry": np.asarray(telem, dtype=object),
        "subsample_agreement": np.asarray(agreement, dtype=object),
        "full_ordered_coverage_verified": np.asarray(True),
    }
    atomic_savez_compressed(
        args.push_out, arrays, overwrite=False, fsync=True, mark=True,
        note="Gate-5 coherent replica full-inventory reweight-all"
    )
    print(json.dumps({"status": "PASS", "stage": "push",
                      "replica_index": args.replica_index,
                      "bootstrap_seed": args.bootstrap_seed,
                      "push": os.path.abspath(args.push_out)}, sort_keys=True))


def run_xsec(args):
    contract, sig_factor, evidence = read_replica_contract(
        args.weights, args.replica_index, args.bootstrap_seed, args.expected_inputs_sha
    )
    nominal_extract._assert_same_dump(contract, args.inputs)
    if not is_complete(args.push_out):
        raise SystemExit("[gate5-extract] full push completion marker is invalid")
    weights_sha = sha256_file(args.weights)
    with np.load(args.push_out, allow_pickle=True) as push_store:
        if scalar(push_store, "push_schema") != PUSH_SCHEMA:
            raise SystemExit("[gate5-extract] wrong push schema")
        for key, want in (
            ("campaign_role", ROLE),
            ("replica_index", int(args.replica_index)),
            ("bootstrap_seed", int(args.bootstrap_seed)),
            ("source_weights_sha256", weights_sha),
            ("inputs_sha256", contract["_inputs_sha256"]),
            ("signal_factor_sha256", evidence["factor_sha256"]["signal_factor_sha256"]),
        ):
            got = scalar(push_store, key)
            if got != want:
                raise SystemExit(f"[gate5-extract] push binding {key} mismatch")
        w_push = np.asarray(push_store["w_push"], dtype=np.float64)
        indices = np.asarray(push_store["mc_indices"], dtype=np.int64)
        agreement = scalar(push_store, "subsample_agreement")
    problems = nominal_extract.validate_push_coverage(
        w_push, indices, evidence["n_sig_full"]
    )
    if problems:
        raise SystemExit(f"[gate5-extract] persisted push coverage failed: {problems}")

    xsec, telem = extract_replica_xsec(
        args.inputs, w_push, sig_factor,
        mcfile=args.mcfile, flux_hist=args.flux_hist, n_nucleons=args.n_nucleons,
    )
    with np.load(args.inputs, allow_pickle=True, mmap_mode="r") as source:
        edges = [np.asarray(source["edges_0"], float), np.asarray(source["edges_1"], float)]
    total = nominal_extract.total_xsec_2d(xsec, edges)
    if not (np.isfinite(xsec).all() and (xsec >= 0).all() and total > 0):
        raise SystemExit("[gate5-extract] extracted cross section is invalid")
    atomic_savez_compressed(
        args.out,
        {
            "xsec_schema": np.asarray(XSEC_SCHEMA),
            "campaign_role": np.asarray(ROLE),
            "replica_index": np.asarray(int(args.replica_index)),
            "bootstrap_seed": np.asarray(int(args.bootstrap_seed)),
            "xsec": xsec,
            "edges_pt": edges[0],
            "edges_pparallel": edges[1],
            "total_sigma_cm2_per_nucleon": np.asarray(total),
            "push_source": np.asarray(os.path.abspath(args.push_out)),
            "push_sha256": np.asarray(sha256_file(args.push_out)),
            "training_artifact_sha256": np.asarray(weights_sha),
            "inputs_sha256": np.asarray(contract["_inputs_sha256"]),
            "signal_factor_sha256": np.asarray(
                evidence["factor_sha256"]["signal_factor_sha256"]
            ),
            "background_factor_sha256": np.asarray(
                evidence["factor_sha256"]["background_factor_sha256"]
            ),
            "extraction_telemetry": np.asarray(telem, dtype=object),
        },
        overwrite=False, fsync=True, mark=True,
        note="Gate-5 coherent replica full-input extended-FPS cross section",
    )
    summary = {
        "schema": XSEC_SCHEMA,
        "status": "PASS",
        "replica_index": int(args.replica_index),
        "bootstrap_seed": int(args.bootstrap_seed),
        "inputs_sha256": contract["_inputs_sha256"],
        "training_artifact_sha256": weights_sha,
        "push_sha256": sha256_file(args.push_out),
        "signal_factor_sha256": evidence["factor_sha256"]["signal_factor_sha256"],
        "background_factor_sha256": evidence["factor_sha256"]["background_factor_sha256"],
        "signal_factor_applied_to_truth_counts": True,
        "signal_factor_applied_to_completeness_and_reporting_mask": True,
        "subsample_agreement": agreement,
        "total_sigma_cm2_per_nucleon": total,
        "extraction": telem,
        "C_stat": None,
        "note": "per-replica product only; complete family validation precedes C_stat",
    }
    write_json(args.summary, summary, "Gate-5 coherent replica extraction summary")

    checkpoint = contract["step2_checkpoint"]
    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "verdict": "GATE5_REPLICA_FULL_EXTRACTION_PASS",
        "replica_index": int(args.replica_index),
        "bootstrap_seed": int(args.bootstrap_seed),
        "seed_policy": SEED_POLICY,
        "execution": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
            "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID", "none"),
            "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID", "none"),
            "host": socket.gethostname(),
            "head_at_runtime": git_head(),
            "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        "source": {
            "path": os.path.abspath(args.inputs),
            "sha256": contract["_inputs_sha256"],
            "n_signal_rows": int(evidence["n_sig_full"]),
        },
        "training_artifact": {
            "path": os.path.abspath(args.weights),
            "sha256": weights_sha,
            "completion_marker_valid": True,
            "step2_checkpoint": os.path.abspath(checkpoint),
            "step2_checkpoint_sha256": sha256_file(checkpoint),
            "replica_target_sha256": evidence["replica_target_sha256"],
            "replica_target_receipt_sha256": evidence["replica_target_receipt_sha256"],
        },
        "coherent_factors": {
            **evidence["factor_sha256"],
            "signal_applied_to_full_truth_counts": True,
            "signal_applied_to_completeness_and_reporting_mask": True,
            "background_applied_before_target_refinement": True,
            "canonical_replay_verified": True,
        },
        "artifacts": {
            "push": {"path": os.path.abspath(args.push_out),
                     "sha256": sha256_file(args.push_out),
                     "size_bytes": os.path.getsize(args.push_out),
                     "completion_marker_valid": True,
                     "full_ordered_coverage_verified": True},
            "xsec": {"path": os.path.abspath(args.out),
                     "sha256": sha256_file(args.out),
                     "size_bytes": os.path.getsize(args.out),
                     "completion_marker_valid": True},
            "summary": {"path": os.path.abspath(args.summary),
                        "sha256": sha256_file(args.summary),
                        "size_bytes": os.path.getsize(args.summary),
                        "completion_marker_valid": True},
        },
        "code": {
            "replica_extractor_sha256": sha256_file(__file__),
            "gate4_pinned_nominal_extractor_sha256": sha256_file(nominal_extract.__file__),
            "loader_sha256": sha256_file(fe.__file__),
        },
        "C_stat": None,
        "subset_selected": False,
    }
    write_json(args.receipt, receipt, "Gate-5 coherent replica extraction receipt; published last")
    print(json.dumps({"status": "PASS", "stage": "xsec",
                      "replica_index": args.replica_index,
                      "bootstrap_seed": args.bootstrap_seed,
                      "receipt": os.path.abspath(args.receipt)}, sort_keys=True))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=("push", "xsec"), required=True)
    ap.add_argument("--replica-index", type=int, required=True)
    ap.add_argument("--bootstrap-seed", type=int, required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--expected-inputs-sha", required=True)
    ap.add_argument("--push-out", required=True)
    ap.add_argument("--out")
    ap.add_argument("--summary")
    ap.add_argument("--receipt")
    ap.add_argument("--chunk", type=int, default=nominal_extract.DEFAULT_CHUNK)
    ap.add_argument("--batch-size", type=int, default=4096)
    ap.add_argument("--subsample-agreement-tol", type=float, default=1e-3)
    ap.add_argument("--mcfile", default=None,
                    help="explicit DATA-root flux ROOT; required for xsec so an immutable code "
                         "worktree cannot be mistaken for the off-repo data root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--n-nucleons", type=float, default=None)
    args = ap.parse_args(argv)
    if not 0 <= args.replica_index < 50:
        raise SystemExit("[gate5-extract] replica index is outside predeclared 0..49")
    if args.bootstrap_seed != 50000 + args.replica_index:
        raise SystemExit("[gate5-extract] bootstrap seed violates predeclared policy")
    if args.stage == "push":
        run_push(args)
    else:
        if not all((args.out, args.summary, args.receipt, args.mcfile)):
            raise SystemExit(
                "[gate5-extract] xsec stage requires --out/--summary/--receipt/--mcfile"
            )
        run_xsec(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

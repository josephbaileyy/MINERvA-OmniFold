#!/usr/bin/env python3
"""Gate-5 GPU stage: train one coherent full-event PET statistical replica.

The promoted nominal driver is intentionally not edited or copied.  This dedicated adapter invokes
that exact driver and injects the only replica-specific operations at its existing seams: the
bootstrap seed, the receipt-bound precomputed target, and coherent-factor provenance fields.  The
nominal path therefore still owns the PET architecture, anneal assertion, checkpoint round-trip,
fold-forward telemetry, and transactional artifact write.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "nd-unfolding", REPO / "nd-unfolding/pet"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import fullevent_fps_dataloader as fe  # noqa: E402
import train_fullevent_nominal as nominal  # noqa: E402
from atomic_write import atomic_write, is_complete, mark_complete  # noqa: E402

SEED_POLICY = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"

from cstat_data_only import (  # noqa: E402
    CSTAT_DATA_ONLY,
    assert_tag_matches_root,
    CSTAT_PRODUCTS,
    CSTAT_THREE_STREAM,
    CLOSURE_TOL_EPS,
    F32_EPS,
    assert_data_only_streams,
    assert_mc_leg_unthinned,
    assert_ratio_provenance_block,
    rescale_measured_to_data_only_R,
)

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


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def read_replica_target_receipt(target_npy, receipt_path, inputs_npz, bootstrap_seed,
                                replica_index):
    try:
        with open(receipt_path, encoding="utf-8") as stream:
            receipt = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[gate5-train] target receipt unreadable: {exc}")
    if receipt.get("status") != "PASS":
        raise SystemExit(f"[gate5-train] target receipt status {receipt.get('status')!r} != PASS")
    if int(receipt.get("replica_index", -1)) != int(replica_index):
        raise SystemExit("[gate5-train] target receipt replica index mismatch")
    if int(receipt.get("bootstrap_seed", -1)) != int(bootstrap_seed):
        raise SystemExit("[gate5-train] target receipt bootstrap seed mismatch")
    if receipt.get("seed_policy") != SEED_POLICY:
        raise SystemExit("[gate5-train] target receipt seed policy is not the predeclared N=50 policy")
    target_meta = dict(receipt.get("runtime_target") or {})
    fe.assert_refined_target_is_replica(target_meta, bootstrap_seed=int(bootstrap_seed))
    if target_meta.get("target_mode") != nominal.BKG_MODE:
        raise SystemExit("[gate5-train] target receipt is not negweight-refined")
    if not target_meta.get("refinement_is_learned_production"):
        raise SystemExit("[gate5-train] target receipt is not the learned production refinement")

    feed = (receipt.get("step1_feed") or {}).get("weights") or {}
    target_npy = os.path.abspath(target_npy)
    if os.path.abspath(feed.get("path", "")) != target_npy:
        raise SystemExit("[gate5-train] target path differs from the path owned by its receipt")
    if not is_complete(target_npy):
        raise SystemExit("[gate5-train] target lacks a valid size/mtime completion marker")
    target_sha = sha256_file(target_npy)
    if target_sha != feed.get("sha256"):
        raise SystemExit("[gate5-train] target SHA-256 differs from its receipt")
    if int(feed.get("size_bytes", -1)) != os.path.getsize(target_npy):
        raise SystemExit("[gate5-train] target size differs from its receipt")

    source = receipt.get("input_preflight") or {}
    if os.path.abspath(source.get("path", "")) != os.path.abspath(inputs_npz):
        raise SystemExit("[gate5-train] source dump differs from target receipt")
    if int(source.get("size_bytes", -1)) != os.path.getsize(inputs_npz):
        raise SystemExit("[gate5-train] source dump size differs from target receipt")
    if not source.get("sha256"):
        raise SystemExit("[gate5-train] target receipt does not bind a source SHA-256")
    # OI-58 hop 1 / BEN-326. Until 2026-08-15 this line read
    #     receipt["_verified_input_sha256"] = source["sha256"]
    # -- a COPY of the receipt's own claim, eleven lines below :99 where the TARGET is
    # genuinely hashed. Nothing on the replica path ever hashed the SOURCE, and
    # train_fullevent_nominal.py:642 stamps this value into the artifact under a comment
    # reading "the digest that was actually verified" -- true on the nominal path and
    # false here. The path and size checks above cannot substitute: size collides freely.
    #
    # TWO independent fail-closed comparisons, so the stamped field is a MEASUREMENT and
    # is bound to the frozen constant rather than to the receipt that quotes it:
    #   (1) the file must hash to what the target receipt claims        -> file == receipt
    #   (2) it must equal GATE5_EXPECTED_INPUT_SHA, which
    #       submit_gate5_replica_n50.sh:25 checked against its HARDCODED :14 digest before
    #       either array was submitted, and :48 exports              -> file == canonical
    # (1) alone is what OI-57 prescribed; it proves agreement with a claim, not identity
    # with the frozen source. (2) was already exported and NO Python read it.
    #
    # This file is in no pin list and its launcher digest floats at submit
    # (submit_gate5_replica_n50.sh:50), so this lands without a re-issue or a repin.
    # train_fullevent_nominal.py:642 is pinned by gate6-leg0-tier-calibration
    # pinned_paths[8] and is deliberately NOT touched: its stamp becomes true here.
    source_sha = sha256_file(inputs_npz)
    if source_sha != source["sha256"]:
        raise SystemExit("[gate5-train] source dump SHA-256 differs from its receipt")
    frozen_input_sha = os.environ.get("GATE5_EXPECTED_INPUT_SHA", "")
    if not frozen_input_sha:
        raise SystemExit("[gate5-train] GATE5_EXPECTED_INPUT_SHA is not exported -- "
                         "submit_gate5_replica_n50.sh:48 must supply the frozen G2 digest")
    if source_sha != frozen_input_sha:
        raise SystemExit("[gate5-train] source dump differs from the frozen G2 digest")
    receipt["_verified_input_sha256"] = source_sha
    receipt["_verified_target_sha256"] = target_sha
    return receipt


def write_json(path, payload):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(jsonable(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

    atomic_write(path, writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(path, note="Gate-5 coherent replica training receipt; published last")


def run_nominal_adapter(args, target_receipt):
    """Invoke the exact nominal main() while injecting the replica-only contract.

    Hooks are restored in a finally block, so importing this module cannot leave the canonical module
    mutated.  The captured loader metadata is added inside the nominal driver's own atomic write.
    """
    original_build = nominal.fe.build_fullevent_loaders
    original_provenance = nominal.assert_target_provenance
    original_atomic = nominal.atomic_savez_compressed
    captured = {}

    def replica_provenance(target_npy, receipt_path, inputs_npz):
        if os.path.abspath(target_npy) != os.path.abspath(args.target_npy):
            raise SystemExit("[gate5-train] nominal adapter received an unexpected target path")
        if os.path.abspath(receipt_path) != os.path.abspath(args.target_receipt):
            raise SystemExit("[gate5-train] nominal adapter received an unexpected receipt path")
        if os.path.abspath(inputs_npz) != os.path.abspath(args.inputs):
            raise SystemExit("[gate5-train] nominal adapter received an unexpected source path")
        return target_receipt

    def replica_build(*build_args, **build_kwargs):
        if build_kwargs.get("bootstrap_seed") not in (None, int(args.bootstrap_seed)):
            raise SystemExit("[gate5-train] conflicting bootstrap seed at loader seam")
        build_kwargs["bootstrap_seed"] = int(args.bootstrap_seed)
        build_kwargs["precomputed_target_replica_seed"] = int(args.bootstrap_seed)
        result = original_build(*build_args, **build_kwargs)
        meta = result[-1]
        fe.assert_refined_target_is_replica(
            meta.get("target") or {}, bootstrap_seed=int(args.bootstrap_seed)
        )
        captured["meta"] = meta
        return result

    def replica_atomic(path, arrays, **kwargs):
        if "meta" not in captured:
            raise SystemExit("[gate5-train] artifact write occurred before replica loader evidence")
        meta = captured["meta"]
        bootstrap = dict(meta.get("bootstrap") or {})
        if int(bootstrap.get("bootstrap_seed", -1)) != int(args.bootstrap_seed):
            raise SystemExit("[gate5-train] loader bootstrap evidence carries the wrong seed")
        n_data = int(bootstrap.get("n_data_full", -1))
        n_sig = int(bootstrap.get("n_sig_full", -1))
        n_bkg = int(bootstrap.get("n_bkg_full", -1))
        data_factor, sig_factor_full, bkg_factor_full = fe.coherent_bootstrap_factors(
            n_data, n_sig, n_bkg, int(args.bootstrap_seed)
        )
        bkg_factor_loader = np.asarray(
            bootstrap.get("bkg_bootstrap_factor"), dtype=np.uint8
        )
        if bkg_factor_loader.shape != (n_bkg,):
            raise SystemExit("[gate5-train] full background factor was not retained")
        if not np.array_equal(bkg_factor_loader, bkg_factor_full):
            raise SystemExit("[gate5-train] loader background factor differs from canonical replay")
        imc = np.asarray(bootstrap.get("mc_indices"), dtype=np.int64)
        sig_factor_subset = np.asarray(
            bootstrap.get("sig_bootstrap_factor"), dtype=np.uint8
        )
        if imc.shape != sig_factor_subset.shape or not np.array_equal(
            sig_factor_subset, sig_factor_full[imc]
        ):
            raise SystemExit("[gate5-train] loader signal subset differs from full canonical replay")
        factor_meta = dict(target_receipt.get("bootstrap") or {})
        for label, factor, key in (
            ("data", data_factor, "data_factor_sha256"),
            ("signal", sig_factor_full, "signal_factor_sha256"),
            ("background", bkg_factor_full, "background_factor_sha256"),
        ):
            if hash_array(factor) != factor_meta.get(key):
                raise SystemExit(
                    f"[gate5-train] canonical {label} factor differs from target-stage receipt"
                )
        augmented = dict(arrays)
        augmented.update({
            "campaign_role": np.asarray("gate5-cstat-coherent-replica"),
            "replica_index": np.asarray(int(args.replica_index)),
            "bootstrap_seed": np.asarray(int(args.bootstrap_seed)),
            # The existing extraction validator consumes the subset factor paired to mc_indices;
            # full-inventory extraction consumes the separately named full factor.  Keeping both
            # prevents either contract from silently treating one cardinality as the other.
            "sig_bootstrap_factor": sig_factor_subset,
            "sig_bootstrap_factor_full": sig_factor_full,
            "bkg_indices": np.arange(n_bkg, dtype=np.int64),
            "bkg_bootstrap_factor": bkg_factor_full,
            "n_data_full": np.asarray(n_data),
            "n_sig_full": np.asarray(n_sig),
            "n_bkg_full": np.asarray(n_bkg),
            "inventory_hashes": np.asarray(str(bootstrap.get("inventory_hashes"))),
            "bkg_inventory_hash": np.asarray(
                str((meta.get("input_identity_hashes") or {}).get("bkg"))
            ),
            "input_identity_hashes": np.asarray(
                dict(meta.get("input_identity_hashes") or {}), dtype=object
            ),
            "bootstrap_factor_sha256": np.asarray(
                dict(target_receipt.get("bootstrap") or {}), dtype=object
            ),
            "replica_target_receipt_path": np.asarray(os.path.abspath(args.target_receipt)),
            "replica_target_receipt_sha256": np.asarray(sha256_file(args.target_receipt)),
            "replica_target_sha256": np.asarray(target_receipt["_verified_target_sha256"]),
            "replica_seed_policy": np.asarray(SEED_POLICY),
        })
        return original_atomic(path, augmented, **kwargs)

    # ------------------------------- DATA-ONLY PATH (C_stat^data) -------------------------------
    def replica_build_data_only(*build_args, **build_kwargs):
        """Unthinned MC via `bootstrap_seed=None`, then the data draw restored to the measured
        normalization driver-side. The ORDER here is load-bearing: rescale, then closure, and
        nothing hashes the measured weights until both have run."""
        if build_kwargs.get("bootstrap_seed") not in (None, int(args.bootstrap_seed)):
            raise SystemExit("[gate5-dataonly] conflicting bootstrap seed at loader seam")
        # THE WHOLE POINT: None leaves the MC legs untouched (:1332-1334). It also leaves the
        # measured normalization at nominal R, which is repaired below and NOT left implicit.
        build_kwargs["bootstrap_seed"] = None
        build_kwargs["precomputed_target_replica_seed"] = int(args.bootstrap_seed)
        result = original_build(*build_args, **build_kwargs)
        data_loader, mc_loader, imc, _cr, _cg = result[0], result[1], result[2], result[3], result[4]
        meta = result[-1]
        fe.assert_refined_target_is_replica(
            meta.get("target") or {}, bootstrap_seed=int(args.bootstrap_seed)
        )
        if meta.get("bootstrap") is not None:
            raise SystemExit("[gate5-dataonly] loader published a bootstrap block; the MC legs "
                             "were thinned and this is not a data-only build")

        with np.load(args.inputs) as d:
            n_data = int(np.asarray(d["measured_pc"]).shape[0])
            n_sig = int(np.asarray(d["w_truth"]).shape[0])
            n_bkg = int(np.asarray(d["w_bkg"]).shape[0])
            w_truth_full = np.asarray(d["w_truth"], dtype=np.float32)
            w_reco_full = np.asarray(d["w_reco"], dtype=np.float32)
            data_factor, _sig_unused, _bkg_unused = fe.coherent_bootstrap_factors(
                n_data, n_sig, n_bkg, int(args.bootstrap_seed))
            ones_bkg = np.ones(n_bkg, dtype=np.uint8)
            # R with NO factors must reproduce the loader's own stamp. If it does not, one of my
            # operands is not the loader's and the rescale ratio would be wrong -- so this is an
            # assertion, not a comfort. It covers every operand choice in one check.
            r_nominal = float(fe.step1_class_ratio_from_dump(
                d, n_data=n_data, w_truth_full=w_truth_full, w_reco_full=w_reco_full)[0])
            r_data_only = float(fe.step1_class_ratio_from_dump(
                d, n_data=n_data, w_truth_full=w_truth_full, w_reco_full=w_reco_full,
                data_factor=data_factor, bkg_factor=ones_bkg)[0])

        stamped = float((meta.get("target") or {}).get("step1_class_ratio"))
        if abs(r_nominal - stamped) > CLOSURE_TOL_EPS * F32_EPS * abs(stamped):
            raise SystemExit(f"[gate5-dataonly] independently derived nominal R {r_nominal!r} does "
                             f"not reproduce the loader's stamp {stamped!r}; operands differ")

        # P5a / P5b BEFORE the measured rescale, because they concern the MC leg and must not be
        # able to observe anything the measured path does.
        p5 = assert_mc_leg_unthinned(mc_loader, w_truth_full=w_truth_full,
                                     w_reco_full=w_reco_full, imc=imc,
                                     size=int(build_kwargs.get("size", 1) or 1))
        closure = rescale_measured_to_data_only_R(
            data_loader, r_nominal=r_nominal, r_data_only=r_data_only)

        captured["meta"] = meta
        captured["data_only"] = {
            "n_data_full": n_data, "n_sig_full": n_sig, "n_bkg_full": n_bkg,
            "data_factor": data_factor,
            "inventory_hashes": fe.inventory_order_hash(w_truth_full),
            "p5_mc_leg": p5,
            "measured_closure": closure,
            "ratio_provenance": {
                "step1_class_ratio_loader_stamped": r_nominal,
                "step1_class_ratio_applied": r_data_only,
                "weights_embody": "step1_class_ratio_applied",
                "loader_stamp_left_unmodified": True,
            },
        }
        return result

    def replica_atomic_data_only(path, arrays, **kwargs):
        if "data_only" not in captured:
            raise SystemExit("[gate5-dataonly] artifact write occurred before data-only evidence")
        meta, ev = captured["meta"], captured["data_only"]
        # P8 -- the loader's own stamp is left EXACTLY as written. Overwriting it would make a
        # loader-stamped field assert what the loader did not do, which is the prohibition on
        # rewriting a submit-time hash (BEN-406 §3). The correction is ADDITIVE.
        if float((meta.get("target") or {}).get("step1_class_ratio")) != \
                float(ev["ratio_provenance"]["step1_class_ratio_loader_stamped"]):
            raise SystemExit("[gate5-dataonly] P8 loader step1_class_ratio was modified")
        assert_ratio_provenance_block(ev["ratio_provenance"])  # P7
        augmented = dict(arrays)
        augmented.update({
            "campaign_role": np.asarray("gate5-cstat-data-only-replica"),
            "cstat_product": np.asarray(CSTAT_DATA_ONLY),
            "replica_index": np.asarray(int(args.replica_index)),
            "data_bootstrap_seed": np.asarray(int(args.bootstrap_seed)),
            "data_bootstrap_factor": ev["data_factor"],
            "sig_bootstrap_factor_full": np.ones(ev["n_sig_full"], dtype=np.uint8),
            "bkg_bootstrap_factor_full": np.ones(ev["n_bkg_full"], dtype=np.uint8),
            "n_data_full": np.asarray(ev["n_data_full"]),
            "n_sig_full": np.asarray(ev["n_sig_full"]),
            "n_bkg_full": np.asarray(ev["n_bkg_full"]),
            "step1_class_ratio_loader_stamped": np.asarray(
                ev["ratio_provenance"]["step1_class_ratio_loader_stamped"]),
            "step1_class_ratio_applied": np.asarray(
                ev["ratio_provenance"]["step1_class_ratio_applied"]),
            "weights_embody": np.asarray(ev["ratio_provenance"]["weights_embody"]),
            "p5_mc_leg_evidence": np.asarray(dict(ev["p5_mc_leg"]), dtype=object),
            "measured_closure_evidence": np.asarray(dict(ev["measured_closure"]), dtype=object),
            "input_identity_hashes": np.asarray(
                dict(meta.get("input_identity_hashes") or {}), dtype=object),
            "inventory_hashes": np.asarray(str(ev["inventory_hashes"])),
            "replica_target_receipt_path": np.asarray(os.path.abspath(args.target_receipt)),
            "replica_target_receipt_sha256": np.asarray(sha256_file(args.target_receipt)),
            "replica_target_sha256": np.asarray(target_receipt["_verified_target_sha256"]),
            "replica_seed_policy": np.asarray(SEED_POLICY),
        })
        # P1-P4 / P6 over what is about to be written, so a thinned-MC data-only replica never
        # comes into existence rather than being detected afterwards.
        assert_data_only_streams(augmented, data_bootstrap_seed=int(args.bootstrap_seed),
                                 n_data_full=ev["n_data_full"], n_sig_full=ev["n_sig_full"],
                                 n_bkg_full=ev["n_bkg_full"])
        return original_atomic(path, augmented, **kwargs)

    # ABSENCE MEANS THREE-STREAM, and that direction is deliberate: a family is never data-only by
    # omission. Programmatic callers that predate this flag (the driver's own regression test builds
    # `args` by hand) therefore keep their existing behaviour unchanged, while a data-only build must
    # be asked for BY NAME. The artifact is self-identifying either way -- P1's tag is stamped by the
    # data-only path and checked by both validators.
    data_only = (getattr(args, "cstat_product", CSTAT_THREE_STREAM) == CSTAT_DATA_ONLY)
    nominal.fe.build_fullevent_loaders = replica_build_data_only if data_only else replica_build
    nominal.assert_target_provenance = replica_provenance
    nominal.atomic_savez_compressed = replica_atomic_data_only if data_only else replica_atomic
    try:
        return nominal.main([
            "--inputs", args.inputs,
            "--out", args.output,
            "--tag", "nominal",
            "--gate3-manifest", args.gate3_manifest,
            "--target-npy", args.target_npy,
            "--target-receipt", args.target_receipt,
        ])
    finally:
        nominal.fe.build_fullevent_loaders = original_build
        nominal.assert_target_provenance = original_provenance
        nominal.atomic_savez_compressed = original_atomic


def validate_data_only_artifact(path, bootstrap_seed, replica_index, target_receipt):
    """P1-P4, P6, P7 read back off the WRITTEN artifact, plus the P5/closure evidence it carries.

    P5 is NOT re-derived here. It was asserted live inside `replica_atomic_data_only` BEFORE the
    write, so a thinned-MC data-only replica never comes into existence; re-deriving it from the
    current input afterwards would be `BEN-406`'s past-vs-present error -- it would FAIL on a
    legitimate input re-dump while proving nothing the write-time gate did not already prove.
    """
    if not is_complete(path):
        raise SystemExit("[gate5-dataonly] replica artifact lacks a valid completion marker")
    with np.load(path, allow_pickle=True) as store:
        if str(np.asarray(store["campaign_role"]).item()) != "gate5-cstat-data-only-replica":
            raise SystemExit("[gate5-dataonly] artifact role is not a Gate-5 data-only replica")
        if int(np.asarray(store["replica_index"]).item()) != int(replica_index):
            raise SystemExit("[gate5-dataonly] artifact replica index mismatch")
        n_data = int(np.asarray(store["n_data_full"]).item())
        n_sig = int(np.asarray(store["n_sig_full"]).item())
        n_bkg = int(np.asarray(store["n_bkg_full"]).item())
        assert_data_only_streams(store, data_bootstrap_seed=int(bootstrap_seed),
                                 n_data_full=n_data, n_sig_full=n_sig, n_bkg_full=n_bkg)
        assert_ratio_provenance_block({
            "step1_class_ratio_loader_stamped":
                float(np.asarray(store["step1_class_ratio_loader_stamped"]).item()),
            "step1_class_ratio_applied":
                float(np.asarray(store["step1_class_ratio_applied"]).item()),
            "weights_embody": str(np.asarray(store["weights_embody"]).item()),
        })
        if str(np.asarray(store["replica_target_sha256"]).item()) != target_receipt[
            "_verified_target_sha256"
        ]:
            raise SystemExit("[gate5-dataonly] artifact target hash differs from verified receipt")
        return {
            "rows": int(np.asarray(store["weights_push"]).size),
            "cstat_product": CSTAT_DATA_ONLY,
            "n_data_full": n_data, "n_sig_full": n_sig, "n_bkg_full": n_bkg,
            "p5_mc_leg_evidence": jsonable(
                np.asarray(store["p5_mc_leg_evidence"], dtype=object).item()),
            "measured_closure_evidence": jsonable(
                np.asarray(store["measured_closure_evidence"], dtype=object).item()),
            "input_identity_hashes": np.asarray(
                store["input_identity_hashes"], dtype=object).item(),
        }


def validate_artifact(path, bootstrap_seed, replica_index, target_receipt):
    if not is_complete(path):
        raise SystemExit("[gate5-train] replica artifact lacks a valid completion marker")
    with np.load(path, allow_pickle=True) as store:
        # P1's CONVERSE. A data-only artifact must never satisfy the three-stream path. Tolerating
        # ABSENCE is deliberate and not laxity: the archived 50 predate the tag, and requiring it
        # here would fail a family this build must not touch.
        keys = set(store.files)
        if "cstat_product" in keys and \
                str(np.asarray(store["cstat_product"]).item()) != CSTAT_THREE_STREAM:
            raise SystemExit("[gate5-train] artifact is not a three-stream replica; use the "
                             "data-only validator")
        if str(np.asarray(store["campaign_role"]).item()) != "gate5-cstat-coherent-replica":
            raise SystemExit("[gate5-train] artifact role is not Gate-5 coherent replica")
        if int(np.asarray(store["replica_index"]).item()) != int(replica_index):
            raise SystemExit("[gate5-train] artifact replica index mismatch")
        n_sig = int(np.asarray(store["n_sig_full"]).item())
        n_bkg = int(np.asarray(store["n_bkg_full"]).item())
        identities = np.asarray(store["input_identity_hashes"], dtype=object).item()
        fe.validate_coherent_bootstrap(
            store,
            bootstrap_seed=int(bootstrap_seed),
            n_sig_full=n_sig,
            n_bkg_full=n_bkg,
            estimator_fingerprint=nominal.ESTIMATOR_FINGERPRINT,
            inventory_hashes=str(np.asarray(store["inventory_hashes"]).item()),
            bkg_inventory_hash=identities["bkg"],
        )
        if str(np.asarray(store["replica_target_sha256"]).item()) != target_receipt[
            "_verified_target_sha256"
        ]:
            raise SystemExit("[gate5-train] artifact target hash differs from verified receipt")
        seed_policy = np.asarray(store["seed_policy"], dtype=object).item()
        if seed_policy != nominal.NOMINAL_SEED_POLICY:
            raise SystemExit("[gate5-train] replica drifted from the promoted nominal policy")
        realized = np.asarray(store["lr_policy_realized"], dtype=object).item()
        if not realized.get("verified_from_optimizer"):
            raise SystemExit("[gate5-train] fit-time anneal was not verified from optimizer")
        if (int(realized.get("n_fits_base_lr", -1)),
                int(realized.get("n_fits_annealed", -1))) != (2, 4):
            raise SystemExit("[gate5-train] realized anneal is not the required 2 base + 4 annealed fits")
        factor_meta = np.asarray(store["bootstrap_factor_sha256"], dtype=object).item()
        bkg_factor = np.asarray(store["bkg_bootstrap_factor"])
        sig_factor_full = np.asarray(store["sig_bootstrap_factor_full"])
        if sig_factor_full.shape != (n_sig,):
            raise SystemExit("[gate5-train] full signal factor has the wrong inventory length")
        if hash_array(sig_factor_full) != factor_meta["signal_factor_sha256"]:
            raise SystemExit("[gate5-train] persisted full signal factor hash mismatch")
        imc = np.asarray(store["mc_indices"], dtype=np.int64)
        if not np.array_equal(
            sig_factor_full[imc], np.asarray(store["sig_bootstrap_factor"])
        ):
            raise SystemExit("[gate5-train] subset signal factor is not a restriction of full factor")
        if hash_array(bkg_factor) != factor_meta["background_factor_sha256"]:
            raise SystemExit("[gate5-train] persisted background factor hash mismatch")
        return {
            "rows": int(np.asarray(store["weights_push"]).size),
            "n_sig_full": n_sig,
            "n_data_full": int(np.asarray(store["n_data_full"]).item()),
            "n_bkg_full": n_bkg,
            "lr_policy_realized": realized,
            "input_identity_hashes": identities,
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--target-npy", required=True)
    ap.add_argument("--target-receipt", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--train-receipt", required=True)
    ap.add_argument("--gate3-manifest", required=True)
    ap.add_argument("--bootstrap-seed", type=int, required=True)
    ap.add_argument("--replica-index", type=int, required=True)
    # Default is the three-stream product, so every existing launcher invocation is unchanged.
    # The data-only product must be asked for BY NAME -- a family is never data-only by omission.
    ap.add_argument("--cstat-product", choices=list(CSTAT_PRODUCTS), default=CSTAT_THREE_STREAM)
    args = ap.parse_args(argv)

    expected_seed = 50000 + int(args.replica_index)
    if args.replica_index < 0 or args.replica_index >= 50 or args.bootstrap_seed != expected_seed:
        raise SystemExit("[gate5-train] replica index/seed violates predeclared N=50 policy")
    # L2 -- TAG <=> FAMILY ROOT, both ways, BEFORE the collision guard. Order matters: the
    # collision guard fires only if a file is already there, so on a fresh root a wrong-product
    # submission would sail past it. L2 does not depend on prior occupancy.
    assert_tag_matches_root(getattr(args, "cstat_product", CSTAT_THREE_STREAM),
                            args.output, args.train_receipt)
    for path in (args.output, args.train_receipt):
        if os.path.lexists(path) or os.path.lexists(f"{path}.done"):
            raise SystemExit(f"[gate5-train] collision/no-clobber guard: {path}")
    nominal.run_config_gate(args.inputs, args.gate3_manifest)
    target_receipt = read_replica_target_receipt(
        args.target_npy, args.target_receipt, args.inputs,
        args.bootstrap_seed, args.replica_index,
    )
    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    rc = run_nominal_adapter(args, target_receipt)
    if rc != 0:
        raise SystemExit(f"[gate5-train] nominal adapter returned {rc}")
    validator = (validate_data_only_artifact if args.cstat_product == CSTAT_DATA_ONLY
                 else validate_artifact)
    evidence = validator(
        args.output, args.bootstrap_seed, args.replica_index, target_receipt
    )
    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "verdict": "GATE5_REPLICA_TRAINING_PASS_EXTRACTION_PENDING",
        "replica_index": int(args.replica_index),
        "bootstrap_seed": int(args.bootstrap_seed),
        "seed_policy": SEED_POLICY,
        "cstat_product": args.cstat_product,
        "started_at_utc": started_utc,
        "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "execution": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
            "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID", "none"),
            "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID", "none"),
            "host": socket.gethostname(),
            "head_at_runtime": git_head(),
        },
        "artifact": {
            "path": os.path.abspath(args.output),
            "sha256": sha256_file(args.output),
            "size_bytes": os.path.getsize(args.output),
            "completion_marker_valid": True,
        },
        "target": {
            "path": os.path.abspath(args.target_npy),
            "sha256": target_receipt["_verified_target_sha256"],
            "receipt_path": os.path.abspath(args.target_receipt),
            "receipt_sha256": sha256_file(args.target_receipt),
        },
        "evidence": evidence,
        "code": {
            "replica_driver": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(__file__)},
            "nominal_driver_unmodified": {
                "path": str(Path(nominal.__file__).resolve()),
                "sha256": sha256_file(nominal.__file__),
            },
            "loader": {"path": str(Path(fe.__file__).resolve()), "sha256": sha256_file(fe.__file__)},
        },
        "timing": {"total_seconds": time.monotonic() - started},
    }
    write_json(args.train_receipt, receipt)
    print(json.dumps({
        "status": "PASS",
        "replica_index": args.replica_index,
        "bootstrap_seed": args.bootstrap_seed,
        "artifact": os.path.abspath(args.output),
        "receipt": os.path.abspath(args.train_receipt),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

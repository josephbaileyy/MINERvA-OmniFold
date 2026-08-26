#!/usr/bin/env python3
"""Evaluate the three PET-v2 fixed-draw arms on predeclared push/projection metrics.

This is a deterministic CPU reducer over completed arm artifacts.  It uses the
same truth counts, flux remap, fiducial constants, bin volumes, and reporting
mask as the first-party full-event extractor, without importing ROOT: the ROOT
CPU target stage has already frozen the 12-playlist flux vector by content.
"""

import argparse
import datetime as dt
import json
import os
import socket
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "2d-unfolding", REPO / "nd-unfolding", REPO / "nd-unfolding/pet"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import flux_universe  # noqa: E402
import fullevent_fps_dataloader as fe  # noqa: E402
from atomic_write import atomic_savez_compressed, atomic_write, is_complete, mark_complete  # noqa: E402
from pet_v2_equivalence_common import (  # noqa: E402
    BOOTSTRAP_SEED, CONTRACT_ID, EXPECTED_INPUT_SHA256, EXPECTED_INPUT_SIZE,
    MATERIALITY_MARGIN, PROHIBITIONS, SAME_ARM_CAP, assert_regular_file,
    classify, fixed_factors, git_head, hash_array, sha256_file, symrel,
    weighted_push_distance,
)
from xsec_nd import extract_cross_section_nd  # noqa: E402

SCHEMA = "pet-v2-equivalence-result-v1"
ARMS = ("W_A", "W_B", "L")
N_NUCLEONS = 3.2352943296224835e30


def _write_json(path, payload):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    atomic_write(str(path), writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(str(path), note="PET-v2 equivalence evaluation; published last")


def _read_arm(arm, receipt_path, expected_receipt_sha, artifact_path, push_path,
              expected_head):
    receipt_path = assert_regular_file(receipt_path, sha256=expected_receipt_sha,
                                       label=f"{arm} receipt")
    if not is_complete(str(receipt_path)):
        raise SystemExit(f"[pet-v2-eval] {arm} receipt completion marker invalid")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema") != "pet-v2-equivalence-arm-v1" or \
            receipt.get("status") != "PASS_ARM_COMPLETE" or receipt.get("arm") != arm:
        raise SystemExit(f"[pet-v2-eval] {arm} receipt identity/status mismatch")
    if receipt.get("contract_id") != CONTRACT_ID or \
            receipt.get("execution", {}).get("head") != expected_head:
        raise SystemExit(f"[pet-v2-eval] {arm} contract/HEAD mismatch")
    if receipt.get("prohibitions_applied") != {key: True for key in PROHIBITIONS}:
        raise SystemExit(f"[pet-v2-eval] {arm} prohibitions drift")
    artifact_info = receipt["artifacts"]["training"]
    push_info = receipt["artifacts"]["full_push"]
    artifact_path = assert_regular_file(artifact_path, sha256=artifact_info["sha256"],
                                        size=artifact_info["size_bytes"],
                                        label=f"{arm} training artifact")
    push_path = assert_regular_file(push_path, sha256=push_info["sha256"],
                                    size=push_info["size_bytes"], label=f"{arm} full push")
    if not is_complete(str(artifact_path)) or not is_complete(str(push_path)):
        raise SystemExit(f"[pet-v2-eval] {arm} payload completion marker invalid")
    with np.load(artifact_path, allow_pickle=True) as store:
        if str(store["arm"].item()) != arm or str(store["status"].item()) != "PASS_ARM_COMPLETE":
            raise SystemExit(f"[pet-v2-eval] {arm} artifact identity/status mismatch")
        bindings = {key: str(store[key].item()) for key in
                    ("input_sha256", "target_receipt_sha256", "target_sha256",
                     "split_sha256", "signal_factor_sha256", "data_factor_sha256",
                     "background_factor_sha256", "full_push_sha256")}
        iteration_push = np.asarray(store["iteration_push"], np.float64)
        histories = list(np.asarray(store["histories"], dtype=object))
        diagnostics = list(np.asarray(store["diagnostics"], dtype=object))
    if bindings["full_push_sha256"] != push_info["sha256"]:
        raise SystemExit(f"[pet-v2-eval] {arm} push binding mismatch")
    push = np.load(push_path, mmap_mode="r", allow_pickle=False)
    if push.ndim != 1 or not np.isfinite(push).all() or np.any(push <= 0.0):
        raise SystemExit(f"[pet-v2-eval] {arm} full push invalid")
    return {"receipt_path": receipt_path, "receipt": receipt, "bindings": bindings,
            "artifact_path": artifact_path, "push_path": push_path, "push": push,
            "iteration_push": iteration_push, "histories": histories,
            "diagnostics": diagnostics}


def _xsec(push, truth_scalars, w_truth, signal_factor, pass_truth, pass_reco,
          edges, data_pot, flux):
    pt = truth_scalars[:, fe.SCALAR_COLS["pt"]]
    ppar = truth_scalars[:, fe.SCALAR_COLS["pparallel"]]
    coords = np.column_stack([pt, ppar])
    drawn_weight = np.asarray(w_truth, np.float64) * np.asarray(signal_factor, np.float64)
    counts, _ = np.histogramdd(
        coords[pass_truth], bins=edges,
        weights=(drawn_weight * np.asarray(push, np.float64))[pass_truth])
    denom, _ = np.histogramdd(coords[pass_truth], bins=edges,
                              weights=drawn_weight[pass_truth])
    accepted = pass_truth & pass_reco
    numer, _ = np.histogramdd(coords[accepted], bins=edges,
                              weights=drawn_weight[accepted])
    completeness = np.divide(numer, denom, out=np.zeros_like(denom), where=denom > 0.0)
    xsec, good = extract_cross_section_nd(
        counts, np.ones_like(counts), flux, data_pot, N_NUCLEONS, edges, flux_axis=0)
    reported = completeness > 0.0
    xsec = np.where(reported, xsec, 0.0)
    if not (np.isfinite(xsec).all() and np.all(xsec >= 0.0) and
            np.array_equal(good & reported, reported)):
        raise SystemExit("[pet-v2-eval] extracted projection array invalid")
    return xsec, {"counts_sha256": hash_array(counts),
                  "reported_mask_sha256": hash_array(reported),
                  "n_reported": int(reported.sum()),
                  "n_zero_acceptance": int(((denom > 0.0) & ~reported).sum())}


def _projection_sums(xsec, edges):
    dpt = np.diff(np.asarray(edges[0], np.float64))
    dpp = np.diff(np.asarray(edges[1], np.float64))
    weighted = np.asarray(xsec, np.float64) * dpt[:, None] * dpp[None, :]
    lo, hi = np.asarray(edges[1][:-1]), np.asarray(edges[1][1:])
    masks = {
        "projection_global": np.ones_like(lo, bool),
        "projection_ppar_lt_6": hi <= 6.0,
        "projection_ppar_6_to_20": (lo >= 6.0) & (hi <= 20.0),
        "projection_ppar_gt_20": lo >= 20.0,
    }
    if not all(mask.any() for mask in masks.values()):
        raise SystemExit("[pet-v2-eval] a predeclared p_parallel projection has no bins")
    return {key: float(weighted[:, mask].sum(dtype=np.float64))
            for key, mask in masks.items()}


def _metric_triplet(distance):
    wa_wb = float(distance("W_A", "W_B"))
    wa_l = float(distance("W_A", "L"))
    wb_l = float(distance("W_B", "L"))
    return {"D_same": wa_wb, "D_cross_max": max(wa_l, wb_l),
            "D_cross_min": min(wa_l, wb_l),
            "pairwise": {"W_A__W_B": wa_wb, "W_A__L": wa_l, "W_B__L": wb_l}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--target-receipt", required=True)
    parser.add_argument("--expected-target-receipt-sha256", required=True)
    parser.add_argument("--flux-npz", required=True)
    parser.add_argument("--expected-flux-sha256", required=True)
    for arm in ARMS:
        key = arm.lower()
        parser.add_argument(f"--{key}-receipt", required=True)
        parser.add_argument(f"--expected-{key}-receipt-sha256", required=True)
        parser.add_argument(f"--{key}-artifact", required=True)
        parser.add_argument(f"--{key}-full-push", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args(argv)

    if git_head(REPO) != args.expected_head:
        raise SystemExit("[pet-v2-eval] runtime HEAD mismatch")
    inputs = assert_regular_file(args.inputs, sha256=EXPECTED_INPUT_SHA256,
                                 size=EXPECTED_INPUT_SIZE, label="G2 source")
    target_receipt_path = assert_regular_file(
        args.target_receipt, sha256=args.expected_target_receipt_sha256,
        label="paired target receipt")
    if not is_complete(str(target_receipt_path)):
        raise SystemExit("[pet-v2-eval] target receipt completion marker invalid")
    target_receipt = json.loads(target_receipt_path.read_text(encoding="utf-8"))
    if target_receipt.get("schema") != "pet-v2-equivalence-paired-target-v1" or \
            target_receipt.get("status") != "PASS_TARGETS_AND_SPLIT" or \
            target_receipt.get("contract_id") != CONTRACT_ID:
        raise SystemExit("[pet-v2-eval] target receipt status/contract mismatch")
    if target_receipt.get("execution", {}).get("head") != args.expected_head:
        raise SystemExit("[pet-v2-eval] target/evaluation HEAD mismatch")
    if target_receipt.get("prohibitions_applied") != {key: True for key in PROHIBITIONS}:
        raise SystemExit("[pet-v2-eval] target Gate-6 prohibitions drift")
    flux_path = assert_regular_file(args.flux_npz, sha256=args.expected_flux_sha256,
                                    label="frozen flux operand")
    if not is_complete(str(flux_path)):
        raise SystemExit("[pet-v2-eval] flux completion marker invalid")
    if target_receipt.get("flux", {}).get("sha256") != args.expected_flux_sha256:
        raise SystemExit("[pet-v2-eval] flux is not bound by target receipt")
    output = Path(args.output).resolve()
    receipt_path = Path(args.receipt).resolve()
    for path in (output, receipt_path):
        if os.path.lexists(path) or os.path.lexists(f"{path}.done"):
            raise SystemExit(f"[pet-v2-eval] collision/no-clobber guard: {path}")
    arms = {}
    for arm in ARMS:
        key = arm.lower()
        arms[arm] = _read_arm(
            arm, getattr(args, f"{key}_receipt"),
            getattr(args, f"expected_{key}_receipt_sha256"),
            getattr(args, f"{key}_artifact"), getattr(args, f"{key}_full_push"),
            args.expected_head)
    # Same-arm controls require identical supplier/software/hardware class, not identical UUID.
    common_binding_keys = ("input_sha256", "target_receipt_sha256", "split_sha256",
                           "signal_factor_sha256", "data_factor_sha256",
                           "background_factor_sha256")
    for key in common_binding_keys:
        values = {arm: arms[arm]["bindings"][key] for arm in ARMS}
        if len(set(values.values())) != 1:
            raise SystemExit(f"[pet-v2-eval] cross-arm {key} mismatch: {values}")
    wa_target = arms["W_A"]["bindings"]["target_sha256"]
    if wa_target != arms["W_B"]["bindings"]["target_sha256"]:
        raise SystemExit("[pet-v2-eval] weighted same-arm target mismatch")
    hardware = {arm: arms[arm]["receipt"]["gpu"]["name"] for arm in ARMS}
    if set(hardware.values()) != {"NVIDIA A100-SXM4-80GB"}:
        raise SystemExit(f"[pet-v2-eval] arm hardware-class mismatch: {hardware}")
    software = {arm: arms[arm]["receipt"]["gpu"]["tensorflow_version"] for arm in ARMS}
    if len(set(software.values())) != 1:
        raise SystemExit(f"[pet-v2-eval] TensorFlow mismatch: {software}")

    with np.load(flux_path, allow_pickle=False) as flux_store:
        flux_ref = np.asarray(flux_store["flux_ref"], np.float64)
        reference_edges = np.asarray(flux_store["reference_edges"], np.float64)
    with np.load(inputs, allow_pickle=True) as source:
        truth_scalars = np.asarray(source["truth_scalars"], np.float64)
        w_truth = np.asarray(source["w_truth"], np.float64)
        pass_truth = np.asarray(source["pass_truth"]).astype(bool)
        pass_reco = np.asarray(source["pass_reco"]).astype(bool)
        edges = [np.asarray(source["edges_0"], np.float64),
                 np.asarray(source["edges_1"], np.float64)]
        data_pot = float(np.asarray(source["data_pot"]).item())
        n_data = int(np.asarray(source["measured_pc"]).shape[0])
        n_background = int(np.asarray(source["w_bkg"]).shape[0])
    _data_factor, signal_factor, _background_factor = fixed_factors(
        n_data, w_truth.size, n_background)
    analysis_weight = w_truth * signal_factor.astype(np.float64) * pass_truth
    if np.any(analysis_weight < 0.0) or not np.isfinite(analysis_weight).all():
        raise SystemExit("[pet-v2-eval] event-level analysis weight invalid")
    flux = flux_universe.flux_on_target_grid(flux_ref, edges[0], reference_edges)
    xsecs, projections, extraction = {}, {}, {}
    for arm in ARMS:
        if arms[arm]["push"].shape != w_truth.shape:
            raise SystemExit(f"[pet-v2-eval] {arm} full push/source rows disagree")
        xsecs[arm], extraction[arm] = _xsec(
            arms[arm]["push"], truth_scalars, w_truth, signal_factor,
            pass_truth, pass_reco, edges, data_pot, flux)
        projections[arm] = _projection_sums(xsecs[arm], edges)
    metrics = {
        "push": _metric_triplet(
            lambda a, b: weighted_push_distance(
                arms[a]["push"], arms[b]["push"], analysis_weight))
    }
    for projection in projections["W_A"]:
        metrics[projection] = _metric_triplet(
            lambda a, b, p=projection: symrel(projections[a][p], projections[b][p]))
    primary = {key: {name: values[name] for name in ("D_same", "D_cross_max", "D_cross_min")}
               for key, values in metrics.items()}
    terminal = classify(primary, controls_valid=True)
    arrays = {
        "schema": np.asarray(SCHEMA), "status": np.asarray("PASS_EVALUATION_COMPLETE"),
        "terminal_classification": np.asarray(terminal),
        "metrics": np.asarray(metrics, dtype=object),
        "projections": np.asarray(projections, dtype=object),
        "xsec_W_A": xsecs["W_A"], "xsec_W_B": xsecs["W_B"], "xsec_L": xsecs["L"],
        "edges_pt": edges[0], "edges_pparallel": edges[1],
        "flux_ref": flux_ref, "flux_target_grid": flux,
        "signal_factor_sha256": np.asarray(hash_array(signal_factor)),
        "reported_mask_sha256": np.asarray(extraction["W_A"]["reported_mask_sha256"]),
    }
    if len({extraction[arm]["reported_mask_sha256"] for arm in ARMS}) != 1:
        raise SystemExit("[pet-v2-eval] arm reporting masks differ")
    atomic_savez_compressed(str(output), arrays, overwrite=False, fsync=True, mark=True,
                            note="PET-v2 fixed-draw equivalence result")
    receipt = {
        "schema": SCHEMA, "status": "PASS_EVALUATION_COMPLETE",
        "terminal_classification": terminal, "contract_id": CONTRACT_ID,
        "scope": "PET_DIAGNOSTIC_AND_METHOD_DEVELOPMENT_ONLY",
        "execution": {"head": git_head(REPO), "host": socket.gethostname(),
                      "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
                      "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()},
        "controls": {"same_source_split_draw": True, "same_weighted_target": True,
                     "same_hardware_class": True, "same_tensorflow": True,
                     "reporting_mask_identical": True,
                     "same_arm_cap_S": SAME_ARM_CAP,
                     "cross_arm_materiality_M": MATERIALITY_MARGIN},
        "metrics": metrics, "projections": projections,
        "extraction_diagnostics": extraction,
        "sources": {"input_sha256": sha256_file(inputs),
                    "target_receipt_sha256": sha256_file(target_receipt_path),
                    "flux_sha256": sha256_file(flux_path),
                    "arm_receipt_sha256": {
                        arm: sha256_file(arms[arm]["receipt_path"]) for arm in ARMS}},
        "artifact": {"path": str(output), "sha256": sha256_file(output),
                     "size_bytes": output.stat().st_size},
        "existing_gate6_remains_blocked": True,
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "what_this_terminal_result_cannot_authorize": [
            *PROHIBITIONS, "interval coverage", "valid PET uncertainty", "ordinary closure",
            "C_stat", "C_ML", "total covariance", "central adoption", "publication claims",
            "coverage campaign", "larger family", "convergence tuning", "further compute"],
    }
    _write_json(receipt_path, receipt)
    print(json.dumps({"status": receipt["status"], "terminal": terminal,
                      "receipt": str(receipt_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent, read-only Gate-2 runtime-product validator.

This deliberately does not import the construction loader or runtime validator.
It recomputes file/configuration hashes, signed-target identity, weight invariants,
and the extended-grid binned telemetry directly from the frozen NPZ and products.

B1 §2c RETARGET (2026-07-29). The step-1 measured target now normalizes to 1e6*R, not 1e6
(`B1-NORMALIZATION-FIX-DESIGN.md` §2a). Every site here that carried the bare constant has been
retargeted; left alone, `:104` would have HARD-FAILED a correct post-B1 product (a ~13.5% miss on
an rtol of 3e-6) and the clipped-shape telemetry would have compared a 1e6*R `refined_hist`
against a 1e6 `clipped_norm`, inflating `l1_fraction` by exactly R. That is the §5 "partial fix
aborts inside the restore window" failure mode, and this file was missed by the first B1 patch --
found by adversarial review of b3751cc.

HOW R ENTERS, GIVEN THIS FILE'S INDEPENDENCE CHARTER. Importing
`fullevent_fps_dataloader.step1_class_ratio` would break the "does not import the construction
loader" property above, which is this validator's whole reason to exist. So R is read from the
receipt and then CHECKED against ingredients this file derives from the dump itself: the numerator
against its own `signed_hist.sum()`, and the denominator against its own `sum(w_truth[pass_reco])`
read. The receipt cannot assert an R its own inputs do not support. What this does NOT do is
re-derive R through a second copy of the formula -- that would put the B-4 flip in two places,
which `step1_class_ratio`'s docstring exists to prevent.
"""

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np


PT_EDGES = np.array(
    [0, .07, .15, .25, .33, .4, .47, .55, .7, .85, 1., 1.25, 1.5, 2.5, 4.5, 30.],
    dtype=np.float64,
)
PPAR_EDGES = np.array(
    [0, .75, 1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5., 6., 7., 8., 9., 10., 15., 20., 40., 60., 120.],
    dtype=np.float64,
)
NORMALIZATION = 1_000_000.0          # the MC-side base; the measured target is this * R
EPS_NORM_FRAC = 1e-18                # zero-guard floor as a FRACTION of the target (see below)
EXPECTED_CONFIG = {
    "target_mode": "negweight-refined",
    "estimator": "exact",
    "device": "cpu",
    "features": ["pt", "pparallel"],
    "master_seed": 42,
    "refinement_random_state": 45,
    "bootstrap_seed": None,
    "max_mc_events": 200000,
    "full_measured_inventory": True,
    # B1 §2c: these two keys replaced the single "normalization_factor" when the measured block
    # was retargeted to 1e6*R. Must track gate2_target_runtime.py's `config` dict exactly, or the
    # "configuration differs from locked exact nominal" check fires on a correct product.
    "mc_normalization_factor": NORMALIZATION,
    "measured_normalization_factor": "STEP1_MC_NORMALIZATION * R (R derived at runtime)",
    "dataloader_import_mode": "target-only exact NumPy source; no TensorFlow/PET training",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def inventory_hash(array) -> str:
    value = np.ascontiguousarray(np.asarray(array))
    digest = hashlib.sha256()
    digest.update(str(value.dtype).encode())
    digest.update(repr(value.shape).encode())
    digest.update(value.tobytes())
    return digest.hexdigest()


def close(a, b, *, rtol=2e-11, atol=1e-5) -> bool:
    return bool(np.isclose(float(a), float(b), rtol=rtol, atol=atol))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    receipt = json.loads(args.receipt.read_text())
    failures = []
    require = lambda condition, message: failures.append(message) if not condition else None

    require(receipt.get("status") == "PASS", "runtime receipt is not PASS")
    require(receipt.get("pet_training_started") is False, "runtime claims PET training started")
    require(receipt.get("configuration") == EXPECTED_CONFIG, "configuration differs from locked exact nominal")
    config_sha = sha256_json(receipt.get("configuration"))
    require(config_sha == receipt.get("configuration_sha256"), "configuration hash mismatch")

    actual_hashes = {
        "input": sha256_file(args.input),
        "weights": sha256_file(args.weights),
    }
    require(actual_hashes["input"] == receipt["input_preflight"]["sha256"], "frozen input hash mismatch")
    require(args.input.stat().st_size == receipt["input_preflight"]["size_bytes"], "frozen input size mismatch")
    require(actual_hashes["weights"] == receipt["step1_feed"]["weights"]["sha256"], "weights hash mismatch")
    require(args.weights.stat().st_size == receipt["step1_feed"]["weights"]["size_bytes"], "weights size mismatch")
    for label, record in receipt["code"].items():
        path = Path(record["path"])
        actual_hashes[label] = sha256_file(path)
        require(actual_hashes[label] == record["sha256"], f"{label} code hash mismatch")

    weights = np.load(args.weights, allow_pickle=False)
    require(weights.dtype == np.float32, "published weights dtype is not float32")
    require(weights.shape == (4_680_719,), "published weights row count mismatch")
    require(bool(np.all(np.isfinite(weights))), "published weights contain non-finite values")
    require(not bool(np.any(weights < 0)), "published weights contain negative values")
    require(int(np.count_nonzero(weights == 0)) == 20, "published zero-weight count mismatch")
    normalized_sum = float(weights.sum(dtype=np.float64))

    # ---- B1 §2c: R, read from the receipt and then corroborated from the dump below ----
    ratio_block = receipt.get("step1_class_ratio") or {}
    class_ratio = ratio_block.get("R")
    require(class_ratio is not None,
            "receipt carries no step1_class_ratio block -- pre-B1 receipt, or the B1 fix regressed")
    if class_ratio is None:
        print(json.dumps({"status": "BLOCK", "failures": failures}, indent=2))
        return 1
    class_ratio = float(class_ratio)
    require(np.isfinite(class_ratio) and class_ratio > 0.0, "receipt step1_class_ratio R invalid")
    target_norm = NORMALIZATION * class_ratio
    require(close(normalized_sum, target_norm, rtol=3e-6, atol=2.0),
            "published weights not normalized to 1e6*R")

    with np.load(args.input, allow_pickle=True) as source:
        measured = np.asarray(source["measured_scalars"], dtype=np.float64)[:, :2] / 1000.0
        background = np.asarray(source["bkg_reco_scalars"], dtype=np.float64)[:, :2] / 1000.0
        w_bkg = np.asarray(source["w_bkg"], dtype=np.float64)
        pot_scale = float(np.asarray(source["pot_scale"]).item())
        # R's denominator, read here rather than taken from the receipt, so the receipt's R is
        # checked against this file's own view of the inventory.
        w_truth = np.asarray(source["w_truth"], dtype=np.float64)
        pass_reco = np.asarray(source["pass_reco"]).astype(bool)
    require(w_truth.shape == pass_reco.shape, "w_truth/pass_reco inventory mismatch")
    sum_w_truth_pass = float(w_truth[pass_reco].sum())
    del w_truth, pass_reco
    require(measured.shape == (4_116_128, 2), "data scalar inventory mismatch")
    require(background.shape == (564_591, 2), "background scalar inventory mismatch")
    require(w_bkg.shape == (564_591,), "background weight inventory mismatch")

    signed = np.concatenate([np.ones(measured.shape[0]), -(w_bkg * pot_scale)])
    signed_hash = inventory_hash(signed)
    require(signed_hash == receipt["runtime_target"]["signed_target_hash"], "signed-target order/hash mismatch")
    require(close(np.abs(signed[signed < 0]).sum(), receipt["runtime_target"]["raw_negative_sum"]), "raw negative sum mismatch")

    data_hist = np.histogram2d(measured[:, 0], measured[:, 1], bins=(PT_EDGES, PPAR_EDGES))[0]
    bkg_hist = np.histogram2d(
        background[:, 0], background[:, 1], bins=(PT_EDGES, PPAR_EDGES), weights=w_bkg * pot_scale
    )[0]
    refined_hist = np.histogram2d(
        measured[:, 0], measured[:, 1], bins=(PT_EDGES, PPAR_EDGES), weights=weights[: measured.shape[0]]
    )[0]
    refined_hist += np.histogram2d(
        background[:, 0], background[:, 1], bins=(PT_EDGES, PPAR_EDGES), weights=weights[measured.shape[0] :]
    )[0]
    signed_hist = data_hist - bkg_hist
    clipped = np.clip(signed_hist, 0.0, None)
    clipped_norm = clipped * (target_norm / clipped.sum())
    occupied = (clipped_norm > 0) | (refined_hist > 0)
    # Floor as a FRACTION of the target, not an absolute constant: `occupied` admits cells with
    # clipped_norm == 0 and refined_hist > 0, where an absolute floor makes max_relative scale by
    # R. EPS_NORM_FRAC * 1e6 == the pre-B1 1e-12, so this is bit-identical at R == 1.
    denom = np.maximum(clipped_norm, EPS_NORM_FRAC * target_norm)
    telemetry = {
        "grid_shape": list(signed_hist.shape),
        "data_rows_in_grid": int(data_hist.sum()),
        "background_rows_in_grid": int(np.histogram2d(background[:, 0], background[:, 1], bins=(PT_EDGES, PPAR_EDGES))[0].sum()),
        "raw_data_sum": float(data_hist.sum()),
        "raw_background_pot_scaled_sum": float(bkg_hist.sum()),
        "raw_signed_sum": float(signed_hist.sum()),
        "negative_signed_cells": int(np.count_nonzero(signed_hist < 0)),
        "closed_form_clipped_sum": float(clipped.sum()),
        "learned_refined_normalized_sum": float(refined_hist.sum()),
        "learned_vs_normalized_clipped_l1_fraction": float(np.abs(refined_hist - clipped_norm).sum() / target_norm),
        "learned_vs_normalized_clipped_max_relative": float(np.max(np.abs(refined_hist[occupied] - clipped_norm[occupied]) / denom[occupied])),
        "learned_vs_normalized_clipped_cosine": float(np.vdot(refined_hist.ravel(), clipped_norm.ravel()) / (np.linalg.norm(refined_hist) * np.linalg.norm(clipped_norm))),
    }
    recorded = receipt["independent_binned_checks"]
    key_map = {"data_rows_in_grid": "in_domain_data_rows", "background_rows_in_grid": "in_domain_background_rows"}
    for key, value in telemetry.items():
        recorded_key = key_map.get(key, key)
        if isinstance(value, list):
            require(value == recorded[recorded_key], f"binned telemetry mismatch: {key}")
        else:
            require(close(value, recorded[recorded_key], rtol=5e-12, atol=1e-6), f"binned telemetry mismatch: {key}")
    require(telemetry["data_rows_in_grid"] == measured.shape[0], "data outside extended grid")
    require(telemetry["background_rows_in_grid"] == background.shape[0], "background outside extended grid")
    require(telemetry["negative_signed_cells"] == 0, "negative signed extended-grid cells")
    require(close(telemetry["learned_refined_normalized_sum"], normalized_sum), "binned/unbinned normalized sums differ")

    # ---- B1 §2c: corroborate the receipt's R against ingredients derived HERE ----
    # R = (n_data - pot_scale*sum(w_bkg)) / (pot_scale*sum(w_truth[pass_reco])). Both ingredients
    # are this file's own: the numerator is `signed_hist.sum()` (its independent 2-D projection, all
    # rows verified in-grid above), the denominator its own `w_truth[pass_reco]` read. Stated as
    # "R times the denominator must reproduce the numerator" so the receipt's R is falsified by the
    # dump rather than re-derived from a duplicated formula (see the module docstring).
    require(sum_w_truth_pass > 0.0, "non-positive MC reco denominator for R")
    implied_numerator = class_ratio * pot_scale * sum_w_truth_pass
    require(close(implied_numerator, telemetry["raw_signed_sum"], rtol=1e-9, atol=1e-3),
            f"receipt R={class_ratio!r} is not supported by this file's own dump ingredients "
            f"(R*pot_scale*sum(w_truth[pass_reco])={implied_numerator} vs independently binned "
            f"signed sum {telemetry['raw_signed_sum']})")
    # PRESENCE FIRST, THEN VALUE. This was `recorded_ratio.get("measured_normalization_target",
    # target_norm)` compared against `target_norm` -- i.e. the default was the expected value, so a
    # receipt omitting the key compared target_norm to itself and passed vacuously, as did one
    # omitting the whole step1_class_ratio block via `or {}`. A check that cannot fail on absent
    # input is not a check. NaN is the sentinel rather than None because `close()` calls float()
    # on both sides, and `require` accumulates instead of raising, so the value check below still
    # has to be evaluable after the presence check fails. Found by review, 2026-07-31.
    # (No block-presence require here: `:131` already fails closed and returns 1 when
    # step1_class_ratio.R is absent, so this site is only reached with the block present. Adding a
    # second presence check would itself be a check that cannot fail.)
    recorded_ratio = ratio_block
    require("measured_normalization_target" in recorded_ratio,
            "receipt omits step1_class_ratio.measured_normalization_target")
    require(close(recorded_ratio.get("measured_normalization_target", float("nan")), target_norm,
                  rtol=1e-9, atol=1e-6),
            "receipt's recorded measured_normalization_target disagrees with 1e6*R")
    # B-4, independently gated here as well as in the runtime. gate2_target_runtime.py now dies on
    # an ACTIVE or unanswerable B-4 before writing a receipt, but this validator exists precisely
    # so a receipt is not believed on its own say-so: without a require here, a hand-built or
    # older receipt carrying an ACTIVE verdict would still validate. The telemetry is the runtime's
    # (this file deliberately does not re-derive R through a second copy of the formula, per the
    # module docstring), so what is checked is that the receipt DECLARES B-4 inactive and that the
    # declaration is internally consistent.
    b4 = (recorded_ratio.get("telemetry") or {}).get("b4_w_reco_vs_w_truth")
    require(isinstance(b4, dict),
            "receipt carries no step1_class_ratio.telemetry.b4_w_reco_vs_w_truth; B-4 is "
            "unanswerable from this receipt and an unchecked R denominator is not certifiable")
    b4 = b4 if isinstance(b4, dict) else {}
    require(b4.get("present_in_dump") is True,
            f"receipt reports w_reco absent from the dump ({b4.get('verdict')!r}); B-4 "
            "unanswerable, R uncorroborated on its denominator")
    require(b4.get("bit_identical_over_pass_reco") is True,
            f"receipt reports B-4 ACTIVE ({b4.get('n_pass_reco_differing')!r} pass_reco rows "
            f"differ); the reco leg is fed w_truth but w_reco differs, so R is not trustworthy")
    require(receipt["runtime_target"].get("refinement_backend") == "u2d.refine_stay_positive", "noncanonical refinement backend")
    require(receipt["runtime_target"].get("refinement_is_learned_production") is True, "learned production refinement not proven")

    result = {
        "schema_version": 1,
        "validation_schema": "g2-gate2-runtime-independent-v1",
        "validated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PASS" if not failures else "BLOCK",
        "failures": failures,
        "runtime_receipt": {"path": str(args.receipt.resolve()), "sha256": sha256_file(args.receipt)},
        "artifact_hashes": actual_hashes,
        "configuration_sha256": config_sha,
        "signed_target_hash": signed_hash,
        "weights": {
            "dtype": str(weights.dtype), "rows": int(weights.size), "sum": normalized_sum,
            "min": float(weights.min()), "max": float(weights.max()),
            "zero_rows": int(np.count_nonzero(weights == 0)),
        },
        "step1_class_ratio": {
            "R_from_receipt": class_ratio,
            "measured_normalization_target": target_norm,
            "independent_denominator_sum_w_truth_pass_reco": sum_w_truth_pass,
            "independent_numerator_binned_signed_sum": telemetry["raw_signed_sum"],
            "corroboration": ("R checked against this validator's own dump-derived numerator and "
                              "denominator; not re-derived through a second copy of the formula"),
        },
        "runtime_target": {
            "mode": receipt["runtime_target"]["target_mode"],
            "backend": receipt["runtime_target"]["refinement_backend"],
            "learned_production": receipt["runtime_target"]["refinement_is_learned_production"],
            "data_rows": receipt["runtime_target"]["n_data_rows"],
            "background_rows": receipt["runtime_target"]["n_bkg_rows"],
            "floored_zero": receipt["runtime_target"]["n_floored_zero"],
        },
        "binned_telemetry": telemetry,
        "pet_training_started": False,
        "verdict": "GATE2_RUNTIME_INDEPENDENT_PASS" if not failures else "GATE2_RUNTIME_INDEPENDENT_BLOCK",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

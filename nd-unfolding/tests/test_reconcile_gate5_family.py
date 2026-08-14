"""Tests for reconcile_gate5_family.py.

EVERY test here is POWER-TESTED: each check is exercised in BOTH directions, so a check that
cannot fail is a test failure. A reconciler that returns PASS on a corrupted family is worse than
no reconciler, because its PASS is the artifact a promotion decision would rest on.

The synthetic family below is built from the field structure of a REAL receipt
(replica_00 of campaign 56857232, read 2026-08-13) so the fixtures exercise the same key paths the
production receipts use. Values are recomputed, not copied, so the fixtures stay self-consistent
when edited.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_PATH = os.path.join(HERE, "..", "pet", "reconcile_gate5_family.py")


def _load():
    spec = importlib.util.spec_from_file_location("reconcile_gate5_family", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["reconcile_gate5_family"] = mod
    spec.loader.exec_module(mod)
    return mod


R5 = _load()


def _load_atomic_write():
    spec = importlib.util.spec_from_file_location(
        "atomic_write", os.path.join(HERE, "..", "pet", "atomic_write.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The REAL marker producer. Fixtures used to hand-write {output, size, marked_at} with NO mtime,
# which is why nothing here ever exercised is_complete's mtime axis: the primitive rejected every
# fixture marker for a reason unrelated to whatever the test was probing.
AW = _load_atomic_write()

# Small inventories: the real ones are 4.1M/49M/565k rows, and the point of these tests is the
# reconciliation logic, not the draw size. The factor STREAMS are still the production ones.
N_DATA, N_SIG, N_BKG = 1000, 4000, 200

# The DECLARED family size, read from the tool rather than restated here. Every test that means
# "a complete family" builds exactly this many, and every test that means "short" builds fewer,
# so the suite can no longer prove a small-n tautology in place of the real gate (BEN-157).
N = R5.DECLARED_INVENTORY

# The verdict suffix a run earns when it supplies neither optional input. Spelled out once so the
# tests state WHICH evidence is missing rather than pattern-matching a string (BEN-157 R3).
NO_INPUTS = "_SOURCE_UNHASHED_NOMINAL_UNCHECKED"
POT = 0.25


def _factors(seed):
    return R5.coherent_bootstrap_factors(N_DATA, N_SIG, N_BKG, seed)


def _build_target_receipt(idx, tmp_root, *, weights=None):
    """Write one internally-consistent target receipt + .npy + sentinels."""
    seed = R5.SEED_BASE + idx
    d = os.path.join(tmp_root, "replicas", f"replica_{idx:02d}", "target")
    os.makedirs(d, exist_ok=True)
    npy = os.path.join(d, "GATE5_REPLICA_TARGET.npy")
    rec = os.path.join(d, "GATE5_REPLICA_TARGET_RECEIPT.json")

    if weights is None:
        # A distinct float32 target per replica, driven by the replica's own data factors, so the
        # fixtures differ for the same reason the real ones do.
        df, _, _ = _factors(seed)
        weights = np.concatenate([
            df.astype(np.float32),
            np.full(N_BKG, 0.5, dtype=np.float32),
        ])
    np.save(npy, weights)
    sha = R5.sha256_file(npy)

    df, sf, bf = _factors(seed)
    n_measured = N_DATA + N_BKG

    # Build R and its operands so the derivation check has something real to reproduce.
    #
    # n_data_effective is DERIVED FROM THE FIXTURE'S OWN DATA FACTORS, as the loader derives it
    # (fullevent_fps_dataloader.py:951, n_data_eff = float(df.sum())). It used to be a hardcoded
    # 1010.0 against an N_DATA of 1000 -- internally consistent and unrelated to the fixture's actual
    # draw, so no test here could ever have exercised the loader-side mutation class. The check that
    # ties the applied factor to the canonical draw failed on every honest fixture until this was
    # fixed, which is how the fixture defect surfaced.
    n_data_effective = float(df.sum())
    bkg_pot_scaled_sum = 10.0
    numerator = n_data_effective - bkg_pot_scaled_sum
    sum_w_reco_scaled = 3200.0
    denominator = POT * sum_w_reco_scaled
    R = numerator / denominator
    mc_norm = 1_000_000.0

    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "verdict": R5.TARGET_VERDICT,
        "replica_index": idx,
        "bootstrap_seed": seed,
        "seed_policy": R5.SEED_POLICY,
        "pet_training_started": False,
        "execution": {
            "slurm_array_task_id": str(idx),
            "slurm_array_job_id": "56857232",
            "head_at_runtime": R5.EXPECTED_HEAD,
            "host": "nid000000",
        },
        "input_preflight": {
            "path": "/fake/input.npz",
            "sha256": R5.EXPECTED_INPUT_SHA,
            "size_bytes": 9897374636,
            "input_identity_hashes": {"data": "dd", "sig": "ss", "bkg": "bb"},
        },
        "gate3_manifest": {"path": "/fake/g3.json", "sha256": R5.EXPECTED_GATE3_MANIFEST_SHA},
        "code": {
            "loader": {"path": "/fake/loader.py", "sha256": R5.EXPECTED_LOADER_SHA},
            "target_builder": {"path": "/fake/tb.py", "sha256": R5.EXPECTED_TARGET_BUILDER_SHA},
            "numpy_dataloader": {"path": "/fake/dl.py", "sha256": R5.EXPECTED_NUMPY_DATALOADER_SHA},
            "canonical_u2d": {"path": "/fake/u2d.py", "sha256": R5.EXPECTED_CANONICAL_U2D_SHA},
        },
        "bootstrap": {
            "n_data_full": N_DATA,
            "n_sig_full": N_SIG,
            "n_bkg_full": N_BKG,
            "mc_subset_rows": 100,
            "inventory_hashes": "invsha",
            "input_identity_hashes": {"data": "dd", "sig": "ss", "bkg": "bb"},
            "data_factor_sha256": R5.hash_array(df),
            "signal_factor_sha256": R5.hash_array(sf),
            "background_factor_sha256": R5.hash_array(bf),
            "factor_hash_contract": "sha256(dtype || JSON(shape) || contiguous raw bytes)",
            "canonical_replay_verified": True,
        },
        "configuration": {
            "full_measured_inventory": True,
            "max_mc_events": 100,
            "refinement_device": "cpu",
            "refinement_estimator": "exact",
            "refinement_random_state": 45,
            "target_mode": "negweight-refined",
        },
        "runtime_target": {
            "bootstrap_seed": seed,
            "target_mode": "negweight-refined",
            "refinement_is_learned_production": True,
            "refinement_backend": "u2d.refine_stay_positive",
            "refinement": "stay-positive (arXiv:2505.03724)",
            "estimator_fingerprint": "pet-fullevent-fps-v1",
            "n_data_rows": N_DATA,
            "n_bkg_rows": N_BKG,
            "n_measured_rows": n_measured,
            "n_floored_zero": int((weights == 0.0).sum()),
            "input_identity_hashes": {"data": "dd", "sig": "ss", "bkg": "bb"},
            "step1_class_ratio": R,
            "step1_mc_normalization": mc_norm,
            "step1_measured_normalization": R * mc_norm,
            "step1_class_ratio_telemetry": {
                "is_bootstrap_replica": True,
                "pot_scale": POT,
                "n_data_effective": n_data_effective,
                "bkg_pot_scaled_sum": bkg_pot_scaled_sum,
                "numerator_signed_data": numerator,
                # The production field-name collision, reproduced on purpose: the OUTER key named
                # "_raw" carries the replica-SCALED sum, and the nested one carries the unscaled.
                "sum_w_reco_pass_reco_raw": sum_w_reco_scaled,
                "b4_w_reco_vs_w_truth": {
                    "sum_w_reco_pass_reco_raw": sum_w_reco_scaled * 1.0005,
                    "sum_w_reco_pass_reco_replica_scaled": sum_w_reco_scaled,
                },
            },
        },
        "step1_feed": {
            "rows": int(weights.size),
            "normalized_sum": R * mc_norm,
            "min": float(weights.min()),
            "max": float(weights.max()),
            "zero_rows": int((weights == 0.0).sum()),
            "weights": {
                "path": npy, "sha256": sha,
                "size_bytes": os.path.getsize(npy), "dtype": str(weights.dtype),
            },
        },
        "timing": {"total_seconds": 2320.0},
    }
    with open(rec, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
    for subject in (npy, rec):
        AW.mark_complete(subject)
    return receipt, npy, rec


def _code_block(tmp_root):
    """The three code digests the producer records, backed by REAL files on disk.

    They need to exist because `code_<role>_matches_disk` re-hashes each recorded path; with paths
    absent the check silently skips, and a check that skips on every fixture is a check no test
    covers. The loader digest is the pinned EXPECTED_LOADER_SHA, so its stub is written to hash to
    exactly that -- the content is irrelevant, the digest is the contract.
    """
    d = os.path.join(tmp_root, "_code")
    os.makedirs(d, exist_ok=True)
    out = {}
    for role, body in (
        ("replica_driver", b"# replica driver stub\n"),
        ("nominal_driver_unmodified", b"# nominal driver stub\n"),
    ):
        f = os.path.join(d, f"{role}.py")
        if not os.path.exists(f):
            with open(f, "wb") as fh:
                fh.write(body)
        out[role] = {"path": f, "sha256": R5.sha256_file(f)}
    # The LOADER is the one role with a PINNED digest, and no stub can satisfy both the pin and a
    # real on-disk file -- that would need a sha256 preimage. Real receipts satisfy both because the
    # real loader genuinely hashes to the pin. So the fixture points it at an absent path: the
    # per-member disk re-hash skips for this role, and `loader_sha256` covers it against the pin.
    # Monkeypatching EXPECTED_LOADER_SHA instead would hide the pin rather than honour it.
    out["loader"] = {"path": "/fake/loader.py", "sha256": R5.EXPECTED_LOADER_SHA}
    return out


def _build_train_receipt(idx, tmp_root, target_sha):
    d = os.path.join(tmp_root, "replicas", f"replica_{idx:02d}", "training")
    os.makedirs(os.path.join(d, "w_nominal"), exist_ok=True)
    art = os.path.join(d, R5.TRAIN_ARTIFACT_NAME)
    with open(art, "wb") as fh:
        fh.write(b"replica-%d-weights" % idx)
    rec = os.path.join(d, R5.TRAIN_RECEIPT_NAME)
    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "verdict": R5.TRAIN_VERDICT,
        "replica_index": idx,
        "bootstrap_seed": R5.SEED_BASE + idx,
        "seed_policy": R5.SEED_POLICY,
        "execution": {"slurm_array_task_id": str(idx), "head_at_runtime": R5.EXPECTED_HEAD},
        "artifact": {"path": art, "sha256": R5.sha256_file(art),
                     "size_bytes": os.path.getsize(art), "completion_marker_valid": True},
        "target": {"path": "/fake/t.npy", "sha256": target_sha,
                   "receipt_path": "/fake/tr.json", "receipt_sha256": "trsha"},
        "code": _code_block(tmp_root),
        "evidence": {"rows": 1200, "n_data_full": N_DATA},
        "timing": {"total_seconds": 10000.0},
    }
    with open(rec, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
    # The training stage's own markers. The fixture created NONE before R2, which is exactly why
    # BEN-157 item 2 -- "training PRESENT is receipt-only, no .done required" -- was invisible here.
    for subject in (art, rec):
        AW.mark_complete(subject)
    return rec


def _family(tmp_root, n, with_training=True):
    shas = []
    for i in range(n):
        _, npy, _ = _build_target_receipt(i, tmp_root)
        shas.append(R5.sha256_file(npy))
    if with_training:
        for i in range(n):
            _build_train_receipt(i, tmp_root, shas[i])
    return shas


def _mutate(path, mutate, remark=True):
    """Rewrite a receipt, then RE-STAMP its completion marker by default.

    Re-stamping models a real producer: anything that legitimately rewrites a completed file marks it
    complete again. Without it, every `_mutate` call left the marker describing the PREVIOUS bytes, so
    `..._marker_is_complete` failed for a reason unrelated to whatever the test was probing.

    That made the suite intermittently red once R2 started delegating to `atomic_write.is_complete`,
    and the flake was subtle in a way worth recording: most mutations here swap one 64-char hex for
    another, so SIZE is unchanged, and `is_complete` compares `int(st_mtime)` at WHOLE-SECOND
    resolution. A rewrite in the same second was therefore invisible and the test passed; a 50-member
    loop that straddled a second boundary failed. Six consecutive clean runs, then one failure.

    Pass `remark=False` when the test's whole point is a post-completion mutation -- there the stale
    marker IS the thing under test.
    """
    with open(path) as fh:
        obj = json.load(fh)
    mutate(obj)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
    if remark and os.path.exists(AW.completion_marker_path(path)):
        AW.mark_complete(path)


# ---------------------------------------------------------------------------
# Contract fidelity: the copied helpers must match the producing code.
# ---------------------------------------------------------------------------

def test_hash_array_contract_is_dtype_shape_bytes():
    a = np.arange(6, dtype=np.uint8)
    import hashlib
    want = hashlib.sha256()
    want.update(b"uint8")
    want.update(b"[6]")
    want.update(a.tobytes())
    assert R5.hash_array(a) == want.hexdigest()


def test_hash_array_distinguishes_shape_from_bytes():
    """POWER TEST: same bytes, different shape must hash differently, or the contract's shape
    term is decorative and a shortened inventory could collide with a reshaped one."""
    a = np.arange(6, dtype=np.uint8)
    assert R5.hash_array(a) != R5.hash_array(a.reshape(2, 3))


def test_hash_array_distinguishes_dtype():
    assert R5.hash_array(np.zeros(4, dtype=np.uint8)) != R5.hash_array(np.zeros(4, dtype=np.int8))


def test_factor_streams_are_independent_across_the_three_inventories():
    """The reason a passing signal/background replay does NOT vouch for the data factors."""
    d1, s1, b1 = R5.coherent_bootstrap_factors(500, 500, 500, 50000)
    assert not np.array_equal(d1, s1)
    assert not np.array_equal(d1, b1)
    assert not np.array_equal(s1, b1)


def test_data_stream_depends_on_n_data_and_is_a_prefix():
    """A truncated data inventory yields a strict PREFIX of the same stream -- which is exactly
    why its hash differs (shape term) even though the leading values agree."""
    d_long, _, _ = R5.coherent_bootstrap_factors(1000, 10, 10, 50000)
    d_short, _, _ = R5.coherent_bootstrap_factors(400, 10, 10, 50000)
    assert np.array_equal(d_long[:400], d_short)
    assert R5.hash_array(d_long[:400]) == R5.hash_array(d_short)
    assert R5.hash_array(d_long) != R5.hash_array(d_short)


def test_factor_streams_differ_by_seed():
    d1, _, _ = R5.coherent_bootstrap_factors(2000, 10, 10, 50000)
    d2, _, _ = R5.coherent_bootstrap_factors(2000, 10, 10, 50001)
    assert not np.array_equal(d1, d2)


# ---------------------------------------------------------------------------
# The happy path, and then every way it can break.
# ---------------------------------------------------------------------------

def test_clean_family_passes(tmp_path):
    root = str(tmp_path)
    _family(root, N)
    rows = [R5.reconcile_target(i, root, True, {}) for i in range(3)]
    assert [r["verdict"] for r in rows] == ["PASS"] * 3, rows[0]["checks"]["failures"]
    trains = [R5.reconcile_training(i, root, rows[i]) for i in range(3)]
    assert [t["verdict"] for t in trains] == ["PASS"] * 3, trains[0]["checks"]["failures"]


def test_R_is_reproduced_and_names_the_field_that_did_it(tmp_path):
    root = str(tmp_path)
    _family(root, 1, with_training=False)
    row = R5.reconcile_target(0, root, True, {})
    assert row["r_derivation"]["R_reproduced_by"], row["r_derivation"]
    # The scaled sum reproduces R; the nested "_raw" one must NOT, or the check is blind to the
    # collision it exists to survive.
    assert "outer_sum_w_reco_pass_reco_raw" in row["r_derivation"]["R_reproduced_by"]
    assert "nested_sum_w_reco_pass_reco_raw" not in row["r_derivation"]["R_reproduced_by"]


def _failed_checks(row):
    return {f["check"] for f in row["checks"]["failures"]}


@pytest.mark.parametrize("mutate,expected", [
    (lambda o: o.__setitem__("bootstrap_seed", 99999), "seed_equals_base_plus_index"),
    (lambda o: o.__setitem__("seed_policy", "other-policy"), "seed_policy_string"),
    (lambda o: o.__setitem__("status", "FAIL"), "status"),
    (lambda o: o.__setitem__("verdict", "SOMETHING_ELSE"), "verdict"),
    (lambda o: o.__setitem__("replica_index", 7), "receipt_replica_index"),
    (lambda o: o["execution"].__setitem__("head_at_runtime", "deadbeef"), "head_at_runtime"),
    (lambda o: o["execution"].__setitem__("slurm_array_task_id", "41"), "slurm_array_task_id"),
    (lambda o: o["input_preflight"].__setitem__("sha256", "0" * 64), "input_sha256"),
    (lambda o: o["gate3_manifest"].__setitem__("sha256", "0" * 64),
     "gate3_manifest_sha256"),
    (lambda o: o["code"]["loader"].__setitem__("sha256", "0" * 64), "loader_sha256"),
    (lambda o: o["code"]["target_builder"].__setitem__("sha256", "0" * 64),
     "target_builder_sha256"),
    (lambda o: o["code"]["numpy_dataloader"].__setitem__("sha256", "0" * 64),
     "numpy_dataloader_sha256"),
    (lambda o: o["code"]["canonical_u2d"].__setitem__("sha256", "0" * 64),
     "canonical_u2d_sha256"),
    (lambda o: o["bootstrap"].__setitem__("canonical_replay_verified", False),
     "canonical_replay_verified"),
    (lambda o: o["step1_feed"]["weights"].__setitem__("sha256", "0" * 64),
     "target_npy_sha256_RECOMPUTED_vs_receipt"),
    (lambda o: o["step1_feed"]["weights"].__setitem__("size_bytes", 12),
     "target_npy_size_on_disk"),
    (lambda o: o["bootstrap"].__setitem__("data_factor_sha256", "0" * 64),
     "data_factor_sha256_REDRAWN_vs_receipt"),
    (lambda o: o["bootstrap"].__setitem__("signal_factor_sha256", "0" * 64),
     "signal_factor_sha256_REDRAWN_vs_receipt"),
    (lambda o: o["bootstrap"].__setitem__("background_factor_sha256", "0" * 64),
     "background_factor_sha256_REDRAWN_vs_receipt"),
    (lambda o: o["runtime_target"].__setitem__("n_data_rows", N_DATA - 1),
     "n_data_full_builder_vs_loader_n_data_rows"),
    (lambda o: o["runtime_target"].__setitem__("n_bkg_rows", N_BKG - 1),
     "n_bkg_full_builder_vs_loader_n_bkg_rows"),
    (lambda o: o["runtime_target"].__setitem__("n_measured_rows", 5),
     "n_measured_rows_equals_data_plus_bkg"),
    (lambda o: o["runtime_target"]["input_identity_hashes"].__setitem__("data", "zz"),
     "input_identity_hashes_agree_in_all_three_blocks"),
    (lambda o: o["configuration"].__setitem__("target_mode", "raw"),
     "configuration_target_mode"),
    (lambda o: o["configuration"].__setitem__("refinement_estimator", "approx"),
     "configuration_refinement_estimator"),
    (lambda o: o["configuration"].__setitem__("refinement_device", "gpu"),
     "configuration_refinement_device"),
    (lambda o: o["configuration"].__setitem__("refinement_random_state", 44),
     "configuration_refinement_random_state"),
    (lambda o: o["configuration"].__setitem__("full_measured_inventory", False),
     "configuration_full_measured_inventory"),
    (lambda o: o["runtime_target"].__setitem__("target_mode", "raw"), "runtime_target_mode"),
    (lambda o: o["runtime_target"].__setitem__("refinement_is_learned_production", False),
     "runtime_refinement_is_learned_production"),
    (lambda o: o["runtime_target"].__setitem__("refinement_backend", "other"),
     "runtime_refinement_backend"),
    (lambda o: o["runtime_target"].__setitem__("bootstrap_seed", 50001),
     "runtime_bootstrap_seed_matches_receipt"),
    (lambda o: o["runtime_target"]["step1_class_ratio_telemetry"].__setitem__(
        "is_bootstrap_replica", False), "step1_telemetry_marks_bootstrap_replica"),
    (lambda o: o["runtime_target"]["step1_class_ratio_telemetry"].__setitem__(
        "numerator_signed_data", 1.0), "R_numerator_from_operands"),
    (lambda o: o["runtime_target"].__setitem__("step1_measured_normalization", 1.0),
     "step1_measured_normalization_equals_R_times_mc_norm"),
    (lambda o: o.__setitem__("pet_training_started", True),
     "pet_training_started_at_target_stage"),
    (lambda o: o["bootstrap"].__setitem__("mc_subset_rows", N_SIG + 1),
     "mc_subset_not_larger_than_full_signal"),
])
def test_each_target_check_fails_when_its_subject_is_broken(tmp_path, mutate, expected):
    """POWER TEST, the whole point of this file: break exactly one fact and confirm the check
    named for it is the one that fires. A check that never fires is not a check."""
    root = str(tmp_path)
    _, _, rec = _build_target_receipt(0, root)
    clean = R5.reconcile_target(0, root, True, {})
    assert clean["verdict"] == "PASS", clean["checks"]["failures"]

    _mutate(rec, mutate)
    broken = R5.reconcile_target(0, root, True, {})
    assert broken["verdict"] == "FAIL"
    assert expected in _failed_checks(broken), sorted(_failed_checks(broken))


def test_target_sum_precision_check_rejects_a_float64_impostor(tmp_path):
    """The float32 target sum must match the float64 telemetry to ~1e-7, and EXACT equality is
    itself suspicious. Here the telemetry is moved far away, which must fire."""
    root = str(tmp_path)
    _, _, rec = _build_target_receipt(0, root)
    _mutate(rec, lambda o: o["step1_feed"].__setitem__("normalized_sum", 1.0))
    row = R5.reconcile_target(0, root, True, {})
    assert "float32_target_sum_matches_telemetry_to_float32_precision" in _failed_checks(row)


def test_mutated_npy_is_caught_even_though_the_receipt_is_untouched(tmp_path):
    """The reason the target is re-hashed from disk: an artifact edited after its receipt was
    written cannot be caught by reading the receipt."""
    root = str(tmp_path)
    _, npy, _ = _build_target_receipt(0, root)
    assert R5.reconcile_target(0, root, True, {})["verdict"] == "PASS"
    np.save(npy, np.zeros(N_DATA + N_BKG, dtype=np.float32))
    row = R5.reconcile_target(0, root, True, {})
    assert row["verdict"] == "FAIL"
    assert "target_npy_sha256_RECOMPUTED_vs_receipt" in _failed_checks(row)


def test_done_sentinel_catches_a_post_completion_size_change(tmp_path):
    root = str(tmp_path)
    _, npy, _ = _build_target_receipt(0, root)
    with open(npy, "ab") as fh:
        fh.write(b"extra")
    row = R5.reconcile_target(0, root, True, {})
    assert "npy_marker_is_complete" in _failed_checks(row)


def test_missing_pieces_report_absent_not_pass(tmp_path):
    root = str(tmp_path)
    _, npy, rec = _build_target_receipt(0, root)
    os.remove(rec + ".done")
    row = R5.reconcile_target(0, root, True, {})
    assert row["state"] == "ABSENT_OR_PARTIAL"
    assert row.get("verdict") != "PASS"


def test_absent_replica_is_absent_not_failed(tmp_path):
    row = R5.reconcile_target(0, str(tmp_path), True, {})
    assert row["state"] == "ABSENT_OR_PARTIAL"


def test_training_in_progress_is_distinguished_from_not_started(tmp_path):
    root = str(tmp_path)
    t = R5.reconcile_target(0, root, False, {})
    assert R5.reconcile_training(0, root, t)["state"] == "NOT_STARTED"
    os.makedirs(os.path.join(root, "replicas", "replica_00", "training", "w_nominal"))
    assert R5.reconcile_training(0, root, t)["state"] == "IN_PROGRESS"


def test_training_bound_to_the_wrong_target_fails(tmp_path):
    """The binding that matters: replica i's training must consume replica i's target."""
    root = str(tmp_path)
    shas = _family(root, 2)
    rows = [R5.reconcile_target(i, root, True, {}) for i in range(2)]
    assert R5.reconcile_training(0, root, rows[0])["verdict"] == "PASS"
    # Point replica 0's training at replica 1's target.
    rec = os.path.join(root, "replicas", "replica_00", "training",
                       R5.TRAIN_RECEIPT_NAME)
    _mutate(rec, lambda o: o["target"].__setitem__("sha256", shas[1]))
    bad = R5.reconcile_training(0, root, rows[0])
    assert bad["verdict"] == "FAIL"
    assert "training_target_sha_equals_measured_target_sha" in _failed_checks(bad)


def test_training_artifact_rehashed_from_disk(tmp_path):
    root = str(tmp_path)
    shas = _family(root, 1)
    rows = [R5.reconcile_target(0, root, True, {})]
    art = os.path.join(root, "replicas", "replica_00", "training", R5.TRAIN_ARTIFACT_NAME)
    with open(art, "ab") as fh:
        fh.write(b"tamper")
    bad = R5.reconcile_training(0, root, rows[0])
    assert bad["verdict"] == "FAIL"
    assert "artifact_sha256_RECOMPUTED_vs_receipt" in _failed_checks(bad)


# ---------------------------------------------------------------------------
# Family-level: the checks no single replica can make.
# ---------------------------------------------------------------------------

def _run_main(root, extra=(), n=None):
    """Run main() as production does: with no --n at all, so the pinned declaration governs.

    `n` is passed ONLY by the tests that assert a disagreeing --n is rejected. The report is
    returned as None when none was written, which is itself part of the contract -- a caller who
    asked the wrong question must get no report, not a well-formed one measured against their
    own premise.
    """
    out = os.path.join(root, "report.json")
    # Remove any prior report FIRST, so the file's presence afterwards is evidence about THIS run.
    # Without this, a test that runs twice reads the first run's report as the second run's output --
    # and the second run is precisely the one asserted to write nothing. A leftover artifact read as
    # the current run's is the write-condition trap, in the helper that exists to check for it.
    if os.path.exists(out):
        os.remove(out)
    argv = ["reconcile_gate5_family.py", "--root", root, "--out", out, *extra]
    if n is not None:
        argv[3:3] = ["--n", str(n)]
    old = sys.argv
    sys.argv = argv
    try:
        rc = R5.main()
    finally:
        sys.argv = old
    if not os.path.exists(out):
        return rc, None
    with open(out) as fh:
        return rc, json.load(fh)


def test_complete_family_passes_and_still_refuses_to_emit_C_stat(tmp_path):
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root)
    assert rc == R5.EXIT_COMPLETE
    # Honest verdict: this run supplies neither --source-npz nor --nominal-target-sha, so two
    # checks did not run and the verdict says so. Before R3 it claimed full strength.
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS" + NO_INPUTS
    assert rep["weakened_axes"] == ["SOURCE_UNHASHED", "NOMINAL_UNCHECKED"]
    assert rep["is_full_strength"] is False
    assert rep["counts"]["targets_present"] == N == R5.DECLARED_INVENTORY
    assert rep["C_stat"] is None, "the reconciler must never construct a covariance"


def test_target_stage_passes_without_training_and_still_refuses_C_stat(tmp_path):
    root = str(tmp_path)
    _family(root, N, with_training=False)
    rc, rep = _run_main(root, extra=["--stage", "target"])
    assert rc == R5.EXIT_COMPLETE
    assert rep["verdict"] == "TARGETS_COMPLETE_PASS" + NO_INPUTS
    assert rep["counts"]["targets_passing"] == N
    assert rep["counts"]["trainings_present"] == 0
    assert rep["C_stat"] is None


def test_target_stage_rejects_a_missing_target(tmp_path):
    root = str(tmp_path)
    _family(root, N - 1, with_training=False)
    rc, rep = _run_main(root, extra=["--stage", "target"])
    assert rc == R5.EXIT_NOT_COMPLETE
    assert rep["verdict"] == "PARTIAL"
    assert rep["counts"]["targets_absent"] == 1


def test_source_npz_is_independently_hashed(tmp_path, monkeypatch):
    root = str(tmp_path)
    _family(root, N, with_training=False)
    source = os.path.join(root, "input.npz")
    with open(source, "wb") as fh:
        fh.write(b"immutable-source-fixture")
    expected = R5.sha256_file(source)
    monkeypatch.setattr(R5, "EXPECTED_INPUT_SHA", expected)
    for idx in range(N):
        rec = os.path.join(root, "replicas", f"replica_{idx:02d}", "target",
                           "GATE5_REPLICA_TARGET_RECEIPT.json")
        _mutate(rec, lambda o: o["input_preflight"].__setitem__("sha256", expected))
    rc, rep = _run_main(root, extra=["--stage", "target", "--source-npz", source])
    assert rc == R5.EXIT_COMPLETE
    assert rep["source_input_measurement"]["sha256_RECOMPUTED"] == expected


def test_partial_family_is_PARTIAL_and_never_PASS(tmp_path):
    """Gate 5's own rule: a missing replica invalidates the manifest.

    This is the load-bearing test of R1 and it is deliberately built at N-1 against the PINNED N.
    Before BEN-157 it built 2 members and ran `--n 3`, which proves 2/3 != 3/3 and says nothing
    about 49/50 -- the suite was written in the defect's own idiom. There is now no `--n` to move,
    so a short family has no path to PASS.
    """
    root = str(tmp_path)
    _family(root, N - 1)
    rc, rep = _run_main(root)
    assert rc == R5.EXIT_NOT_COMPLETE
    assert rep["verdict"] == "PARTIAL"
    assert rep["counts"]["targets_present"] == N - 1
    assert rep["declared_inventory"] == N
    assert rep["C_stat"] is None


def test_identical_targets_are_BLOCK_not_a_small_C_stat(tmp_path):
    """THE reassuring failure. Duplicate targets would collapse the measured-side variance and
    read as a small statistical component. It must block, and it must block even while the family
    is still filling, because more replicas cannot repair it."""
    root = str(tmp_path)
    shared = np.full(N_DATA + N_BKG, 0.25, dtype=np.float32)
    for i in range(N):
        _build_target_receipt(i, root, weights=shared)
    shas = [R5.sha256_file(os.path.join(root, "replicas", f"replica_{i:02d}", "target",
                                        "GATE5_REPLICA_TARGET.npy")) for i in range(N)]
    assert len(set(shas)) == 1, "fixture must actually produce identical targets"
    for i in range(N):
        _build_train_receipt(i, root, shas[i])
    rc, rep = _run_main(root)
    assert rc != R5.EXIT_COMPLETE
    assert rep["verdict"] == "BLOCK"
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "target_sha_all_distinct_across_family" in fired


def test_a_replica_reusing_another_seeds_factors_is_caught(tmp_path):
    """Duplicate factor hashes with distinct targets: the draw was not independent."""
    root = str(tmp_path)
    _family(root, N)
    rec = os.path.join(root, "replicas", "replica_01", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    df0, _, _ = _factors(R5.SEED_BASE + 0)
    _mutate(rec, lambda o: o["bootstrap"].__setitem__("data_factor_sha256", R5.hash_array(df0)))
    rc, rep = _run_main(root)
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    # It fires twice over: the redraw no longer matches, AND the family loses distinctness.
    assert "data_factor_sha_all_distinct_across_family" in fired
    assert rep["targets"][1]["verdict"] == "FAIL"


def test_a_replica_from_a_different_inventory_is_BLOCK(tmp_path):
    """A family spanning two inventories is not one ensemble, however complete it looks."""
    root = str(tmp_path)
    _family(root, N)
    rec = os.path.join(root, "replicas", "replica_02", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    _mutate(rec, lambda o: o["bootstrap"].__setitem__("inventory_hashes", "DIFFERENT"))
    rc, rep = _run_main(root)
    assert rc != 0
    assert rep["verdict"] == "BLOCK"
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "invariant_constant_across_family[inventory_hashes]" in fired
    # And the violation must NAME its members, not just report a boolean.
    groups = rep["family_invariants"]["inventory_hashes"]
    assert isinstance(groups, dict) and any(2 in v for v in groups.values())


def test_replica_matching_the_nominal_target_is_caught(tmp_path):
    """A replica that reproduced the nominal target exactly is the collapsed-variance failure in
    its purest form."""
    root = str(tmp_path)
    shas = _family(root, N)
    rc, rep = _run_main(root, extra=["--nominal-target-sha", shas[1]])
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "no_replica_target_equals_the_nominal_target" in fired


def test_nominal_sha_that_matches_nothing_does_not_fire(tmp_path):
    """POWER TEST for the check above: it must be capable of passing, or it proves nothing."""
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root, extra=["--nominal-target-sha", "f" * 64])
    assert rc == R5.EXIT_COMPLETE
    # The nominal sha WAS supplied here, so that axis is no longer weakened; source still is.
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS_SOURCE_UNHASHED"
    assert rep["weakened_axes"] == ["SOURCE_UNHASHED"]


def test_skip_replay_downgrades_the_verdict_rather_than_claiming_the_same_thing(tmp_path):
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root, extra=["--skip-replay"])
    assert rc == R5.EXIT_COMPLETE
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS_REPLAY_SKIPPED" + NO_INPUTS
    assert rep["replay_performed"] is False
    assert "REPLAY_SKIPPED" in rep["weakened_axes"]
    # And with replay it is the stronger verdict, so the two are distinguishable.
    rc2, rep2 = _run_main(root)
    assert rep2["verdict"] == "FAMILY_COMPLETE_PASS" + NO_INPUTS
    assert "REPLAY_SKIPPED" not in rep2["weakened_axes"]


def test_skip_replay_does_not_hide_a_broken_data_factor(tmp_path):
    """Skipping the redraw must lose only the redraw. A corrupted data-factor hash that is now
    invisible per-replica must still be caught by family distinctness if it collides."""
    root = str(tmp_path)
    _family(root, N)
    rec = os.path.join(root, "replicas", "replica_01", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    df0, _, _ = _factors(R5.SEED_BASE + 0)
    _mutate(rec, lambda o: o["bootstrap"].__setitem__("data_factor_sha256", R5.hash_array(df0)))
    rc, rep = _run_main(root, extra=["--skip-replay"])
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "data_factor_sha_all_distinct_across_family" in fired


def test_seed_gap_in_an_otherwise_complete_family_is_caught(tmp_path):
    root = str(tmp_path)
    _family(root, N)
    rec = os.path.join(root, "replicas", "replica_01", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    _mutate(rec, lambda o: o.__setitem__("bootstrap_seed", 50007))
    rc, rep = _run_main(root)
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "seeds_are_contiguous_from_base" in fired


def test_empty_root_is_PARTIAL_with_zero_counts(tmp_path):
    rc, rep = _run_main(str(tmp_path))
    assert rc == R5.EXIT_NOT_COMPLETE
    assert rep["verdict"] == "PARTIAL"
    assert rep["counts"]["targets_present"] == 0
    assert rep["declared_inventory"] == R5.DECLARED_INVENTORY
    assert rep["C_stat"] is None


# ---------------------------------------------------------------------------
# The name-mismatch guard.
#
# This exists because the first version of the reconciler looked for
# GATE5_REPLICA_TRAIN_RECEIPT.json while the launcher writes
# GATE5_REPLICA_TRAINING_RECEIPT.json. A missing file at an inferred path is
# indistinguishable from a stage that has not run, so it would have reported
# trainings_present: 0 and PARTIAL *forever* -- including at 50/50 -- and the family
# could never have been promoted. It reported the right count at the time only
# because no training had finished: the verdict was accidentally right while the
# instrument was broken.
# ---------------------------------------------------------------------------

LAUNCHER = os.path.join(HERE, "..", "pet", "sbatch_gate5_replica_train_array.sh")


def test_expected_names_match_the_launcher():
    """READ THE LAUNCHER. This test used to assert the constants against string literals duplicated
    a few lines up, under a docstring promising it pinned them to the batch script -- BEN-157 item 7.
    It could not have failed if the launcher changed, which is the one thing it existed to catch, and
    I described it to a peer as pinning them to the launcher. It now opens the file.

    The parse is deliberately loose about shell syntax and strict about the NAME: any assignment whose
    value ends in the basename counts, so reformatting the launcher does not break the test, while
    renaming the artifact does.
    """
    with open(LAUNCHER) as fh:
        text = fh.read()
    for const, var in ((R5.TRAIN_ARTIFACT_NAME, "OUTPUT"), (R5.TRAIN_RECEIPT_NAME, "TRAIN_RECEIPT")):
        assert re.search(rf"^{var}=\S*/{re.escape(const)}\s*$", text, re.M), (
            f"{var} in {os.path.basename(LAUNCHER)} does not end in {const!r}; the reconciler's "
            f"constant and the launcher have drifted, which is exactly the defect fixed at 69c577b")


def test_the_launcher_pin_FAILS_when_the_launcher_disagrees(tmp_path, monkeypatch):
    """Power test for the test above -- the half whose absence was the whole defect.

    A launcher-reading check that cannot fail is no better than the literal it replaced, so this
    rewrites a copy of the launcher with a changed name and asserts the same parse rejects it.
    """
    with open(LAUNCHER) as fh:
        text = fh.read()
    tampered = text.replace(R5.TRAIN_ARTIFACT_NAME, "SOMETHING_ELSE.npz")
    assert tampered != text, "fixture must actually change the launcher text"
    assert not re.search(
        rf"^OUTPUT=\S*/{re.escape(R5.TRAIN_ARTIFACT_NAME)}\s*$", tampered, re.M), (
        "the parse accepts a launcher that no longer sets this name; it is a literal in disguise")
    # And the untampered text must still match, or the regex proves nothing either way.
    assert re.search(rf"^OUTPUT=\S*/{re.escape(R5.TRAIN_ARTIFACT_NAME)}\s*$", text, re.M)


def test_receipt_under_an_unexpected_name_is_NAME_MISMATCH_not_absent(tmp_path):
    root = str(tmp_path)
    t = R5.reconcile_target(0, root, False, {})
    d = os.path.join(root, "replicas", "replica_00", "training")
    os.makedirs(d)
    # The exact historical mistake: "TRAIN" where the producer writes "TRAINING".
    with open(os.path.join(d, "GATE5_REPLICA_TRAIN_RECEIPT.json"), "w") as fh:
        json.dump({"status": "PASS"}, fh)
    row = R5.reconcile_training(0, root, t)
    assert row["state"] == "NAME_MISMATCH", row
    assert "GATE5_REPLICA_TRAIN_RECEIPT.json" in row["unexpected_files"]
    assert row["expected_receipt"] == R5.TRAIN_RECEIPT_NAME


def test_weights_under_an_unexpected_name_is_also_NAME_MISMATCH(tmp_path):
    root = str(tmp_path)
    t = R5.reconcile_target(0, root, False, {})
    d = os.path.join(root, "replicas", "replica_00", "training")
    os.makedirs(d)
    with open(os.path.join(d, "weights.npz"), "wb") as fh:
        fh.write(b"x")
    assert R5.reconcile_training(0, root, t)["state"] == "NAME_MISMATCH"


def test_NAME_MISMATCH_blocks_the_family_even_with_nothing_else_present(tmp_path):
    """It must BLOCK, not be absorbed into a completeness gap: if the search is unreliable, every
    other count in the report is a statement about the search rather than about the campaign."""
    root = str(tmp_path)
    _family(root, N, with_training=False)
    d = os.path.join(root, "replicas", "replica_00", "training")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "GATE5_REPLICA_TRAIN_RECEIPT.json"), "w") as fh:
        json.dump({"status": "PASS"}, fh)
    rc, rep = _run_main(root)
    assert rc != 0
    assert rep["verdict"] == "BLOCK", rep["verdict"]
    assert rep["counts"]["trainings_name_mismatch"] == 1
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "no_training_artifact_name_mismatches" in fired
    assert rep["C_stat"] is None


def test_correctly_named_files_do_NOT_trigger_the_guard(tmp_path):
    """POWER TEST: the guard must be capable of staying silent, or it would block every clean run
    and be switched off within a day."""
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root)
    assert rc == R5.EXIT_COMPLETE
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS" + NO_INPUTS
    assert rep["counts"]["trainings_name_mismatch"] == 0


def test_an_empty_training_dir_is_still_plain_absence(tmp_path):
    """The guard must not fire on genuine absence -- otherwise a campaign that has simply not
    reached its training stage would read as broken tooling."""
    root = str(tmp_path)
    t = R5.reconcile_target(0, root, False, {})
    os.makedirs(os.path.join(root, "replicas", "replica_00", "training"))
    assert R5.reconcile_training(0, root, t)["state"] == "NOT_STARTED"
    os.makedirs(os.path.join(root, "replicas", "replica_00", "training", "w_nominal"))
    assert R5.reconcile_training(0, root, t)["state"] == "IN_PROGRESS"


# ---------------------------------------------------------------------------
# R1 (BEN-157): the declared inventory is PINNED, and --n may only agree with it.
#
# The defect these pin: `--n` was an unconstrained int and every completeness comparison was
# against it, so `--n 0` on an empty directory returned rc=0 and the exact FAMILY_COMPLETE_PASS.
# Power-tested in both directions -- a disagreeing --n must be REJECTED, and the agreeing value
# and the no-flag default must still WORK, or this is a gate that cannot pass.
# ---------------------------------------------------------------------------


def test_declared_inventory_agrees_with_the_seed_policy_string():
    """Two declarations of one number must not be able to drift apart silently.

    The size is stated in SEED_POLICY (`gate5-cstat-n50-v1`) and in DECLARED_INVENTORY. The tool
    asserts their agreement at import; this re-checks it here so the reason is visible in the suite
    rather than only in a traceback.
    """
    assert R5.DECLARED_INVENTORY == 50
    assert f"n{R5.DECLARED_INVENTORY}" in R5.SEED_POLICY


@pytest.mark.parametrize("bad_n", [0, 1, 2, 3, 49, 51, 100, -1])
def test_an_n_that_disagrees_with_the_declaration_is_REJECTED(tmp_path, bad_n):
    """THE test for BEN-157's headline. `--n 0` used to return rc=0 and an exact pass.

    Note what is asserted beyond the exit code: NO REPORT IS WRITTEN. A caller who asked the wrong
    question must not receive a well-formed artifact measured against their own premise, because
    that artifact is what a promotion decision would later rest on.
    """
    root = str(tmp_path)
    _family(root, N)  # a genuinely COMPLETE family, so only --n can be the reason it fails
    rc, rep = _run_main(root, n=bad_n)
    assert rc == R5.EXIT_USAGE, f"--n {bad_n} was not rejected"
    assert rep is None, f"--n {bad_n} still produced a report"


def test_the_declared_n_is_ACCEPTED_and_still_passes(tmp_path):
    """The other direction. A check that rejected every --n would also 'reject' the wrong ones."""
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root, n=R5.DECLARED_INVENTORY)
    assert rc == R5.EXIT_COMPLETE
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS" + NO_INPUTS


def test_omitting_n_entirely_is_the_production_path_and_works(tmp_path):
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root)
    assert rc == R5.EXIT_COMPLETE
    assert rep["declared_inventory"] == R5.DECLARED_INVENTORY


@pytest.mark.parametrize("size", [0, 1, 49])
def test_a_short_family_has_NO_n_that_makes_it_pass(tmp_path, size):
    """The defect in its general form: not just that --n 0 passed, but that ANY short family could
    be declared complete by naming its own size. Every route is now closed -- the honest run reports
    PARTIAL and the flattering run is refused."""
    root = str(tmp_path)
    if size:
        _family(root, size)
    rc, rep = _run_main(root)
    assert rc == R5.EXIT_NOT_COMPLETE
    assert rep["verdict"] == "PARTIAL"
    assert rep["counts"]["targets_present"] == size
    # And the route that used to work:
    rc2, rep2 = _run_main(root, n=size)
    assert rc2 == R5.EXIT_USAGE
    assert rep2 is None


def test_usage_failure_and_an_incomplete_family_have_DIFFERENT_exit_codes(tmp_path):
    """"Could not look" must never be confusable with "looked and found it short".

    `2` already meant incomplete before this change, so usage is a third code rather than a reuse.
    A single nonzero for both would let a mistyped invocation read as a measured shortfall, and
    vice versa -- which is the same reasoning as the write-condition rule, applied to a status.
    """
    root = str(tmp_path)
    _family(root, N - 1)
    rc_short, rep_short = _run_main(root)
    rc_usage, rep_usage = _run_main(root, n=N - 1)
    assert rc_short == R5.EXIT_NOT_COMPLETE
    assert rc_usage == R5.EXIT_USAGE
    assert rc_short != rc_usage
    assert R5.EXIT_COMPLETE not in (rc_short, rc_usage)
    # The distinguishable part a reader acts on: one produced evidence, the other did not.
    assert rep_short is not None and rep_usage is None


def test_the_report_records_that_the_declaration_WAS_pinned(tmp_path):
    """Without this the artifact cannot contradict a wrong verdict.

    Before R1 a pass at 50/50 and a pass at a caller-chosen n produced reports that looked alike,
    which made the verdict unfalsifiable rather than wrong -- exactly the condition this tool exists
    to prevent elsewhere (CONVENTION-receipt-ingredients, BEN-077).
    """
    root = str(tmp_path)
    _family(root, N)
    rc, rep = _run_main(root)
    assert rc == R5.EXIT_COMPLETE
    assert rep["declared_inventory"] == R5.DECLARED_INVENTORY
    assert rep["declared_inventory_is_pinned_in_tool"] is True
    assert rep["declared_inventory_policy_string"] == R5.SEED_POLICY
    assert f"n{rep['declared_inventory']}" in rep["declared_inventory_policy_string"]


def test_n_is_rejected_BEFORE_any_artifact_is_read(tmp_path):
    """A bad --n must be a usage error even when the root does not exist.

    If the size check ran after the directory scan, a nonexistent root would report PARTIAL and the
    caller would never learn that their declaration was the actual problem.
    """
    missing = str(tmp_path / "no-such-directory")
    argv = ["reconcile_gate5_family.py", "--root", missing, "--n", "0"]
    old = sys.argv
    sys.argv = argv
    try:
        rc = R5.main()
    finally:
        sys.argv = old
    assert rc == R5.EXIT_USAGE


# ---------------------------------------------------------------------------
# R2 (BEN-157 items 2-5): derive from the filesystem and pinned constants, never from the receipt's
# account of itself.
#
# The 90 tests above are the POSITIVE half -- every R2 check passes on a clean fixture, which is what
# makes them checks rather than alarms. These are the other direction. Each one is an attack that
# produced an EXACT PASS before R2, and the first is codex's own reproduction.
# ---------------------------------------------------------------------------


def test_a_receipt_AGREEING_with_a_wrongly_named_artifact_now_fails(tmp_path):
    """CODEX'S ATTACK, verbatim. Before R2 this returned an exact FAMILY_COMPLETE_PASS with
    trainings_name_mismatch=0 and the canonical filename absent from disk.

    The NAME_MISMATCH guard could not catch it and still cannot: its stray scan is reachable only
    when the receipt is ABSENT, so a receipt at the correct name never enters that branch. The guard
    catches a file that disagrees with the launcher; only the canonical-path anchor catches a receipt
    that AGREES with a wrong file.
    """
    root = str(tmp_path)
    shas = _family(root, 1)
    d = os.path.join(root, "replicas", "replica_00", "training")
    canonical = os.path.join(d, R5.TRAIN_ARTIFACT_NAME)
    moved = os.path.join(d, "UNEXPECTED_WEIGHTS.npz")
    os.rename(canonical, moved)
    AW.mark_complete(moved)
    _mutate(os.path.join(d, R5.TRAIN_RECEIPT_NAME),
            lambda o: o["artifact"].__setitem__("path", moved))

    t = R5.reconcile_target(0, root, False, {})
    row = R5.reconcile_training(0, root, t)
    assert row["state"] == "PRESENT", "the receipt is present and correctly named; not a MISMATCH"
    assert row["verdict"] == "FAIL"
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "artifact_path_is_canonical" in failed
    assert not os.path.exists(canonical), "fixture must actually leave the canonical name absent"


def test_the_canonical_path_check_PASSES_on_an_honest_receipt(tmp_path):
    """Power test for the check above: it must be capable of passing."""
    root = str(tmp_path)
    _family(root, 1)
    t = R5.reconcile_target(0, root, False, {})
    row = R5.reconcile_training(0, root, t)
    assert row["verdict"] == "PASS"
    assert "artifact_path_is_canonical" not in {f["check"] for f in row["checks"]["failures"]}


def test_weights_marker_catches_a_post_completion_change(tmp_path):
    root = str(tmp_path)
    _family(root, 1)
    art = os.path.join(root, "replicas", "replica_00", "training", R5.TRAIN_ARTIFACT_NAME)
    marker = json.load(open(AW.completion_marker_path(art)))
    with open(art, "ab") as fh:
        fh.write(b"tampered")
    t = R5.reconcile_target(0, root, False, {})
    row = R5.reconcile_training(0, root, t)
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "weights_marker_is_complete" in failed
    assert marker["size"] != os.path.getsize(art)


def test_a_missing_training_marker_is_caught(tmp_path):
    """BEN-157 item 2: the training stage read NO markers at all before R2."""
    root = str(tmp_path)
    _family(root, 1)
    d = os.path.join(root, "replicas", "replica_00", "training")
    os.remove(AW.completion_marker_path(os.path.join(d, R5.TRAIN_ARTIFACT_NAME)))
    t = R5.reconcile_target(0, root, False, {})
    row = R5.reconcile_training(0, root, t)
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "weights_marker_present" in failed


def test_marker_check_catches_an_MTIME_only_change_which_the_old_hand_rolled_one_could_not(tmp_path):
    """THE proof that the primitive is CALLED rather than re-implemented (BEN-157 item 4).

    Size is untouched, so the old size-only comparison passed. `atomic_write.is_complete` compares
    size AND mtime, and the mtime is moved a full 100 s -- comfortably past its whole-second
    resolution. If this test ever passes-as-clean, the delegation has been undone.
    """
    root = str(tmp_path)
    _family(root, 1)
    npy = os.path.join(root, "replicas", "replica_00", "target", "GATE5_REPLICA_TARGET.npy")
    marker = json.load(open(AW.completion_marker_path(npy)))
    size_before = os.path.getsize(npy)
    os.utime(npy, (marker["mtime"] + 100, marker["mtime"] + 100))
    assert os.path.getsize(npy) == size_before, "this probe must not change size"
    row = R5.reconcile_target(0, root, False, {})
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "npy_marker_is_complete" in failed, (
        "an mtime-only change was accepted; the tool is no longer delegating to is_complete")
    assert AW.is_complete(npy) is False


def test_a_marker_copied_from_another_replica_is_caught(tmp_path):
    """The one thing is_complete does NOT do, which is why that check stays hand-rolled: it derives
    the marker path from the subject, so a marker naming a DIFFERENT file satisfies it."""
    root = str(tmp_path)
    _family(root, 2)
    npy0 = os.path.join(root, "replicas", "replica_00", "target", "GATE5_REPLICA_TARGET.npy")
    npy1 = os.path.join(root, "replicas", "replica_01", "target", "GATE5_REPLICA_TARGET.npy")
    m1 = AW.completion_marker_path(npy1)
    payload = json.load(open(m1))
    payload["output"] = npy0          # points at another replica's file
    with open(m1, "w") as fh:
        json.dump(payload, fh)
    os.utime(npy1, (payload["mtime"], payload["mtime"]))
    row = R5.reconcile_target(1, root, False, {})
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "npy_marker_names_current_subject" in failed


def test_a_tampered_driver_file_is_caught_by_the_disk_rehash(tmp_path):
    """BEN-157 item 5. The driver digests FLOAT by design, so no pinned constant can catch this;
    re-hashing the recorded path can."""
    root = str(tmp_path)
    _family(root, 1)
    stub = os.path.join(root, "_code", "replica_driver.py")
    assert os.path.isfile(stub), "fixture must back the digest with a real file or nothing is checked"
    with open(stub, "ab") as fh:
        fh.write(b"# silently edited\n")
    t = R5.reconcile_target(0, root, False, {})
    row = R5.reconcile_training(0, root, t)
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "code_replica_driver_matches_disk" in failed


def test_a_driver_that_changed_MID_FAMILY_is_caught(tmp_path):
    """What neither a pinned constant nor a per-member re-hash can catch on its own: every member is
    internally consistent, and they disagree with EACH OTHER."""
    root = str(tmp_path)
    _family(root, N)
    rec = os.path.join(root, "replicas", "replica_07", "training", R5.TRAIN_RECEIPT_NAME)
    _mutate(rec, lambda o: o["code"]["replica_driver"].__setitem__("sha256", "f" * 64))
    AW.mark_complete(rec)
    rc, rep = _run_main(root)
    assert rc != R5.EXIT_COMPLETE
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "invariant_constant_across_family[training.code.replica_driver]" in fired
    # And the violation NAMES its members rather than reporting a boolean.
    groups = rep["family_invariants"]["training.code.replica_driver"]
    assert isinstance(groups, dict) and any(7 in v for v in groups.values())


def test_the_three_code_digests_are_all_READ_not_just_the_loader(tmp_path):
    """Item 5's positive half: a digest the tool never reads is a digest nobody checks."""
    root = str(tmp_path)
    _family(root, 1)
    for role in ("replica_driver", "nominal_driver_unmodified", "loader"):
        rec = os.path.join(root, "replicas", "replica_00", "training", R5.TRAIN_RECEIPT_NAME)
        _mutate(rec, lambda o, r=role: o["code"][r].__setitem__("sha256", None))
        AW.mark_complete(rec)
        t = R5.reconcile_target(0, root, False, {})
        row = R5.reconcile_training(0, root, t)
        failed = {f["check"] for f in row["checks"]["failures"]}
        assert f"code_{role}_digest_recorded" in failed, f"{role} digest is not read at all"
        _mutate(rec, lambda o, r=role: o["code"][r].__setitem__(
            "sha256", R5.EXPECTED_LOADER_SHA if r == "loader" else "0" * 64))
        AW.mark_complete(rec)


def test_the_tool_imports_the_real_completion_primitive(tmp_path):
    """If this module ever stops being the canonical one, the marker checks silently change meaning."""
    assert R5._aw.__name__ == "atomic_write"
    assert os.path.realpath(R5._aw.__file__) == os.path.realpath(AW.__file__)


def test_the_BARE_full_strength_verdict_is_REACHABLE(tmp_path, monkeypatch):
    """R3's power test. Downgrading absent evidence is only correct if full strength is still
    attainable -- otherwise the strongest verdict becomes unreachable, which is its own defect and
    would train readers to ignore the suffix."""
    root = str(tmp_path)
    shas = _family(root, N)
    source = os.path.join(root, "input.npz")
    with open(source, "wb") as fh:
        fh.write(b"immutable-source-fixture")
    expected = R5.sha256_file(source)
    monkeypatch.setattr(R5, "EXPECTED_INPUT_SHA", expected)
    for idx in range(N):
        rec = os.path.join(root, "replicas", f"replica_{idx:02d}", "target",
                           "GATE5_REPLICA_TARGET_RECEIPT.json")
        _mutate(rec, lambda o: o["input_preflight"].__setitem__("sha256", expected))
    rc, rep = _run_main(root, extra=["--source-npz", source,
                                     "--nominal-target-sha", "f" * 64])
    assert rc == R5.EXIT_COMPLETE
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS", rep["weakened_axes"]
    assert rep["weakened_axes"] == []
    assert rep["is_full_strength"] is True


def test_a_receipt_with_a_null_R_FAILS_instead_of_dropping_four_checks(tmp_path):
    """BEN-157 item 6, fail-closed half. Measured before R3: 43 passed, 0 failed, R_recorded null.

    R and its operands are REQUIRED receipt fields, so their absence is a defect in the artifact and
    fails the member -- not a verdict downgrade, which would say the TOOL ran weakly when in fact the
    RECEIPT is incomplete.
    """
    root = str(tmp_path)
    _family(root, 1, with_training=False)
    rec = os.path.join(root, "replicas", "replica_00", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")

    def kill_R(o):
        o["runtime_target"]["step1_class_ratio"] = None
        for f in ("pot_scale", "numerator_signed_data", "n_data_effective", "bkg_pot_scaled_sum"):
            o["runtime_target"]["step1_class_ratio_telemetry"][f] = None

    _mutate(rec, kill_R)
    row = R5.reconcile_target(0, root, False, {})
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert row["verdict"] == "FAIL"
    assert "R_published_by_receipt" in failed
    for f in ("pot_scale", "numerator_signed_data", "n_data_effective", "bkg_pot_scaled_sum"):
        assert f"R_operand_published[{f}]" in failed


def test_the_R_published_checks_PASS_on_an_honest_receipt(tmp_path):
    """Other direction: a check that fired on every receipt would be an alarm, not a check."""
    root = str(tmp_path)
    _family(root, 1, with_training=False)
    row = R5.reconcile_target(0, root, False, {})
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert "R_published_by_receipt" not in failed
    assert not any(f.startswith("R_operand_published[") for f in failed)


# ---------------------------------------------------------------------------
# The only check with power over the LOADER's applied data factor (codex's mutation test).
# ---------------------------------------------------------------------------


def _apply_loader_side_mutation(receipt, delta):
    """Mutate the factor the LOADER applied, propagated exactly as the loader would propagate it.

    Deliberately leaves bootstrap.data_factor_sha256 alone: that is the BUILDER's own recomputation of
    the canonical stream, and the mutation under test is of what the loader applied, not of what the
    builder recomputed. Every downstream number is updated so the receipt stays INTERNALLY CONSISTENT --
    which is the whole point, because internal consistency was mistaken for verification.
    """
    rt = receipt["runtime_target"]
    tel = rt["step1_class_ratio_telemetry"]
    tel["n_data_effective"] = float(tel["n_data_effective"]) + delta
    tel["numerator_signed_data"] = tel["n_data_effective"] - tel["bkg_pot_scaled_sum"]
    den = float(tel["pot_scale"]) * float(tel["sum_w_reco_pass_reco_raw"])
    rt["step1_class_ratio"] = tel["numerator_signed_data"] / den
    rt["step1_measured_normalization"] = rt["step1_class_ratio"] * rt["step1_mc_normalization"]
    receipt["step1_feed"]["normalized_sum"] = rt["step1_measured_normalization"]


def test_a_mutated_LOADER_APPLIED_data_factor_is_caught(tmp_path):
    """CODEX'S MUTATION TEST. Before this check it passed 57 of 57 with a 13.6% shift in R.

    Nothing else could catch it: the factor-hash comparison is builder-vs-redraw, and the R
    re-derivation uses n_data_effective as an INPUT, so a mutated factor yields a mutated
    n_data_effective and a mutated R that re-derive from each other perfectly.
    """
    root = str(tmp_path)
    _family(root, 1, with_training=False)
    rec = os.path.join(root, "replicas", "replica_00", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    before = json.load(open(rec))["bootstrap"]["data_factor_sha256"]
    _mutate(rec, lambda o: _apply_loader_side_mutation(o, 137.0))
    assert json.load(open(rec))["bootstrap"]["data_factor_sha256"] == before, (
        "the builder's recomputed hash must be UNTOUCHED or this tests the wrong thing")

    row = R5.reconcile_target(0, root, True, {})
    failed = {f["check"] for f in row["checks"]["failures"]}
    assert row["verdict"] == "FAIL"
    assert "n_data_effective_equals_sum_of_REDRAWN_data_factor" in failed
    # And the R derivation must NOT be what catches it -- it cannot, and claiming otherwise would
    # misattribute the power.
    assert not any(f.startswith("R_numerator") or f == "R_reproducible_from_published_operands"
                   for f in failed), "R re-derivation has no power here; it re-derives self-consistently"


def test_the_data_factor_sum_check_PASSES_on_an_honest_receipt(tmp_path):
    """Power test: a check that fired on every receipt would block every clean run."""
    root = str(tmp_path)
    _family(root, 1, with_training=False)
    row = R5.reconcile_target(0, root, True, {})
    assert row["verdict"] == "PASS"
    assert "n_data_effective_equals_sum_of_REDRAWN_data_factor" not in {
        f["check"] for f in row["checks"]["failures"]}


def test_the_sum_check_is_BLIND_to_a_permutation_and_that_bound_is_asserted(tmp_path):
    """The limit, pinned as a test so nobody later reads the check as proving identity.

    A permutation of the applied factor conserves the sum, so this check passes on it. The bound is
    real in the live family too: replica_03 and replica_08 share n_data_effective with differing
    data_factor_sha256.
    """
    root = str(tmp_path)
    _family(root, 1, with_training=False)
    rec = os.path.join(root, "replicas", "replica_00", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    # delta 0 == any sum-conserving change, permutation included
    _mutate(rec, lambda o: _apply_loader_side_mutation(o, 0.0))
    row = R5.reconcile_target(0, root, True, {})
    assert "n_data_effective_equals_sum_of_REDRAWN_data_factor" not in {
        f["check"] for f in row["checks"]["failures"]}, (
        "if this ever fails, the check has become stronger than the sum and the docstring lies")


def test_the_sum_check_vanishes_under_skip_replay_and_the_verdict_says_so(tmp_path):
    """It is replay evidence, so --skip-replay must lose it -- and R3 must name the loss."""
    root = str(tmp_path)
    _family(root, N, with_training=False)
    rc, rep = _run_main(root, extra=["--stage", "target", "--skip-replay"])
    assert "REPLAY_SKIPPED" in rep["weakened_axes"]
    assert rep["verdict"].startswith("TARGETS_COMPLETE_PASS_REPLAY_SKIPPED")
    row = [t for t in rep["targets"] if t["replica_index"] == 0][0]
    assert row["replay"]["performed"] is False

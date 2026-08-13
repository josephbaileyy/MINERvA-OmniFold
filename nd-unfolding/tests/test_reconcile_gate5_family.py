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

# Small inventories: the real ones are 4.1M/49M/565k rows, and the point of these tests is the
# reconciliation logic, not the draw size. The factor STREAMS are still the production ones.
N_DATA, N_SIG, N_BKG = 1000, 4000, 200
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
    n_data_effective = 1010.0
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
        "gate3_manifest": {"path": "/fake/g3.json", "sha256": "g3sha"},
        "code": {
            "loader": {"path": "/fake/loader.py", "sha256": R5.EXPECTED_LOADER_SHA},
            "target_builder": {"path": "/fake/tb.py", "sha256": "tbsha"},
            "numpy_dataloader": {"path": "/fake/dl.py", "sha256": "dlsha"},
            "canonical_u2d": {"path": "/fake/u2d.py", "sha256": "u2dsha"},
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
        "configuration": {"full_measured_inventory": True, "max_mc_events": 100},
        "runtime_target": {
            "n_data_rows": N_DATA,
            "n_bkg_rows": N_BKG,
            "n_measured_rows": n_measured,
            "n_floored_zero": int((weights == 0.0).sum()),
            "input_identity_hashes": {"data": "dd", "sig": "ss", "bkg": "bb"},
            "step1_class_ratio": R,
            "step1_mc_normalization": mc_norm,
            "step1_measured_normalization": R * mc_norm,
            "step1_class_ratio_telemetry": {
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
        with open(subject + ".done", "w") as fh:
            json.dump({"output": subject, "size": os.path.getsize(subject),
                       "marked_at": "2026-08-13T00:00:00Z"}, fh)
    return receipt, npy, rec


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
        "code": {"loader": {"sha256": R5.EXPECTED_LOADER_SHA},
                 "replica_driver": {"sha256": "rdsha"},
                 "nominal_driver_unmodified": {"sha256": "ndsha"}},
        "evidence": {"rows": 1200, "n_data_full": N_DATA},
        "timing": {"total_seconds": 10000.0},
    }
    with open(rec, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
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


def _mutate(path, mutate):
    with open(path) as fh:
        obj = json.load(fh)
    mutate(obj)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)


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
    _family(root, 3)
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
    (lambda o: o["code"]["loader"].__setitem__("sha256", "0" * 64), "loader_sha256"),
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
    assert "done_npy_records_current_size" in _failed_checks(row)


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

def _run_main(root, n, extra=()):
    argv = ["reconcile_gate5_family.py", "--root", root, "--n", str(n),
            "--out", os.path.join(root, "report.json"), *extra]
    old = sys.argv
    sys.argv = argv
    try:
        rc = R5.main()
    finally:
        sys.argv = old
    with open(os.path.join(root, "report.json")) as fh:
        return rc, json.load(fh)


def test_complete_family_passes_and_still_refuses_to_emit_C_stat(tmp_path):
    root = str(tmp_path)
    _family(root, 3)
    rc, rep = _run_main(root, 3)
    assert rc == 0
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS"
    assert rep["C_stat"] is None, "the reconciler must never construct a covariance"


def test_partial_family_is_PARTIAL_and_never_PASS(tmp_path):
    """Gate 5's own rule: a missing replica invalidates the manifest. 2 of 3 is not a family."""
    root = str(tmp_path)
    _family(root, 2)
    rc, rep = _run_main(root, 3)
    assert rc != 0
    assert rep["verdict"] == "PARTIAL"
    assert rep["counts"]["targets_present"] == 2
    assert rep["C_stat"] is None


def test_identical_targets_are_BLOCK_not_a_small_C_stat(tmp_path):
    """THE reassuring failure. Duplicate targets would collapse the measured-side variance and
    read as a small statistical component. It must block, and it must block even while the family
    is still filling, because more replicas cannot repair it."""
    root = str(tmp_path)
    shared = np.full(N_DATA + N_BKG, 0.25, dtype=np.float32)
    for i in range(3):
        _build_target_receipt(i, root, weights=shared)
    shas = [R5.sha256_file(os.path.join(root, "replicas", f"replica_{i:02d}", "target",
                                        "GATE5_REPLICA_TARGET.npy")) for i in range(3)]
    assert len(set(shas)) == 1, "fixture must actually produce identical targets"
    for i in range(3):
        _build_train_receipt(i, root, shas[i])
    rc, rep = _run_main(root, 3)
    assert rc != 0
    assert rep["verdict"] == "BLOCK"
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "target_sha_all_distinct_across_family" in fired


def test_a_replica_reusing_another_seeds_factors_is_caught(tmp_path):
    """Duplicate factor hashes with distinct targets: the draw was not independent."""
    root = str(tmp_path)
    _family(root, 3)
    rec = os.path.join(root, "replicas", "replica_01", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    df0, _, _ = _factors(R5.SEED_BASE + 0)
    _mutate(rec, lambda o: o["bootstrap"].__setitem__("data_factor_sha256", R5.hash_array(df0)))
    rc, rep = _run_main(root, 3)
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    # It fires twice over: the redraw no longer matches, AND the family loses distinctness.
    assert "data_factor_sha_all_distinct_across_family" in fired
    assert rep["targets"][1]["verdict"] == "FAIL"


def test_a_replica_from_a_different_inventory_is_BLOCK(tmp_path):
    """A family spanning two inventories is not one ensemble, however complete it looks."""
    root = str(tmp_path)
    _family(root, 3)
    rec = os.path.join(root, "replicas", "replica_02", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    _mutate(rec, lambda o: o["bootstrap"].__setitem__("inventory_hashes", "DIFFERENT"))
    rc, rep = _run_main(root, 3)
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
    shas = _family(root, 3)
    rc, rep = _run_main(root, 3, extra=["--nominal-target-sha", shas[1]])
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "no_replica_target_equals_the_nominal_target" in fired


def test_nominal_sha_that_matches_nothing_does_not_fire(tmp_path):
    """POWER TEST for the check above: it must be capable of passing, or it proves nothing."""
    root = str(tmp_path)
    _family(root, 3)
    rc, rep = _run_main(root, 3, extra=["--nominal-target-sha", "f" * 64])
    assert rc == 0
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS"


def test_skip_replay_downgrades_the_verdict_rather_than_claiming_the_same_thing(tmp_path):
    root = str(tmp_path)
    _family(root, 2)
    rc, rep = _run_main(root, 2, extra=["--skip-replay"])
    assert rc == 0
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS_REPLAY_SKIPPED"
    assert rep["replay_performed"] is False
    # And with replay it is the stronger verdict, so the two are distinguishable.
    rc2, rep2 = _run_main(root, 2)
    assert rep2["verdict"] == "FAMILY_COMPLETE_PASS"


def test_skip_replay_does_not_hide_a_broken_data_factor(tmp_path):
    """Skipping the redraw must lose only the redraw. A corrupted data-factor hash that is now
    invisible per-replica must still be caught by family distinctness if it collides."""
    root = str(tmp_path)
    _family(root, 3)
    rec = os.path.join(root, "replicas", "replica_01", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    df0, _, _ = _factors(R5.SEED_BASE + 0)
    _mutate(rec, lambda o: o["bootstrap"].__setitem__("data_factor_sha256", R5.hash_array(df0)))
    rc, rep = _run_main(root, 3, extra=["--skip-replay"])
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "data_factor_sha_all_distinct_across_family" in fired


def test_seed_gap_in_an_otherwise_complete_family_is_caught(tmp_path):
    root = str(tmp_path)
    _family(root, 3)
    rec = os.path.join(root, "replicas", "replica_01", "target",
                       "GATE5_REPLICA_TARGET_RECEIPT.json")
    _mutate(rec, lambda o: o.__setitem__("bootstrap_seed", 50007))
    rc, rep = _run_main(root, 3)
    assert rc != 0
    fired = {f["check"] for f in rep["family_checks"]["failures"]}
    assert "seeds_are_contiguous_from_base" in fired


def test_empty_root_is_PARTIAL_with_zero_counts(tmp_path):
    rc, rep = _run_main(str(tmp_path), 3)
    assert rc != 0
    assert rep["verdict"] == "PARTIAL"
    assert rep["counts"]["targets_present"] == 0
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

def test_expected_names_match_the_launcher():
    """Pin the names to what the Slurm-captured batch script actually sets. If the launcher
    changes, this is the test that should fail, rather than the family silently reading empty."""
    assert R5.TRAIN_RECEIPT_NAME == "GATE5_REPLICA_TRAINING_RECEIPT.json"
    assert R5.TRAIN_ARTIFACT_NAME == "GATE5_REPLICA_WEIGHTS.npz"


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
    _family(root, 2, with_training=False)
    d = os.path.join(root, "replicas", "replica_00", "training")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "GATE5_REPLICA_TRAIN_RECEIPT.json"), "w") as fh:
        json.dump({"status": "PASS"}, fh)
    rc, rep = _run_main(root, 2)
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
    _family(root, 2)
    rc, rep = _run_main(root, 2)
    assert rc == 0
    assert rep["verdict"] == "FAMILY_COMPLETE_PASS"
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

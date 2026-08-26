#!/usr/bin/env python3
"""CPU-only positive/negative controls for PET-v2 executable operands."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


REPO = Path(__file__).resolve().parents[2]
PET = REPO / "nd-unfolding/pet"
PROPOSAL = json.loads((
    REPO / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-proposal-20260825.json"
).read_text(encoding="utf-8"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(PET))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


COMMON = _load("pet_v2_equivalence_common", PET / "pet_v2_equivalence_common.py")
EVALUATE = _load("evaluate_pet_v2_equivalence", PET / "evaluate_pet_v2_equivalence.py")
TRAIN = _load("train_pet_v2_equivalence", PET / "train_pet_v2_equivalence.py")


def test_split_is_reproducible_nontrivial_and_stream_separated():
    a = COMMON.deterministic_train_mask(10_003, 123)
    b = COMMON.deterministic_train_mask(10_003, 123)
    c = COMMON.deterministic_train_mask(10_003, 124)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
    assert 0.77 < a.mean() < 0.83
    assert a.any() and (~a).any()


def test_literal_mapping_deletes_zeros_duplicates_k_and_preserves_membership():
    factor = np.asarray([0, 1, 3, 2, 0], np.uint8)
    source = COMMON.literal_source_index(factor)
    assert source.tolist() == [1, 2, 2, 2, 3, 3]
    assert np.array_equal(np.bincount(source, minlength=factor.size), factor)
    unique_train = np.asarray([True, False, True, False, True])
    inherited = unique_train[source]
    for index in np.unique(source):
        assert np.unique(inherited[source == index]).size == 1
    with pytest.raises(ValueError):
        COMMON.literal_source_index(np.asarray([1.0, 2.0]))


def test_weighted_and_literal_loss_contributions_aggregate_by_unique_id():
    factor = np.asarray([0, 2, 1, 3], np.uint8)
    physical = np.asarray([4.0, 1.5, 2.5, 0.75])
    loss = np.asarray([0.2, 0.3, 0.4, 0.5])
    source = COMMON.literal_source_index(factor)
    weighted = factor * physical * loss
    literal = physical[source] * loss[source]
    aggregate = np.bincount(source, weights=literal, minlength=factor.size)
    assert np.allclose(aggregate, weighted)
    # The full-row reduce_mean is intentionally not equal: normalization is a causal seam.
    assert not np.isclose(weighted.mean(), literal.mean())


def test_training_representation_changes_rows_but_preserves_unique_weight_totals():
    class _Dataset:
        def __init__(self, value):
            self.value = value

        def with_options(self, _options):
            return self

    class _DatasetFactory:
        @staticmethod
        def from_tensor_slices(value):
            return _Dataset(value)

    class _Options:
        experimental_deterministic = False

    class _TF:
        class data:
            Dataset = _DatasetFactory
            Options = _Options

    class _Base:
        def __init__(self):
            self.mc = type("MC", (), {})()
            self.data = type("Data", (), {})()
            self.mc.nmax = 4
            self.data.nmax = 4
            base = np.arange(8, dtype=np.float32).reshape(4, 2)
            self.mc.reco = self.mc.gen = base
            self.mc.reco_evt = self.mc.gen_evt = base[:, :1]
            self.data.reco = base + 100
            self.data.reco_evt = base[:, :1] + 100
            self.mc.pass_reco = self.mc.pass_gen = np.ones(4, bool)
            self.data.pass_reco = np.ones(4, bool)
            factor = np.asarray([0, 2, 1, 3], np.float32)
            mc_physical = np.asarray([4.0, 1.5, 2.5, 0.75], np.float32)
            data_physical = np.asarray([3.0, 2.0, 1.0, 0.5], np.float32)
            self.mc.weight = factor * mc_physical
            self.mc_weight_reco = factor * (mc_physical + 0.25)
            self.data.weight = factor * data_physical
            self.weights_push = np.asarray([1.0, 1.2, 0.8, 1.4], np.float32)
            self.weights_pull = np.asarray([0.9, 1.1, 1.3, 0.7], np.float32)

    factor = np.asarray([0, 2, 1, 3], np.uint8)
    source = COMMON.literal_source_index(factor)
    literal = {
        "source_index": source,
        "weight": np.asarray([2.0, 2.0, 1.0, 0.5, 0.5, 0.5], np.float32),
    }
    split = {
        "signal_train": np.asarray([True, False, True, False]),
        "data_train": np.asarray([True, False]),
        "background_train": np.asarray([True, False]),
    }
    classes = {
        arm: TRAIN.make_equivalence_multifold(
            _Base, _TF, arm, split, literal, factor, np.arange(4), [], [],
            np.zeros((4, 2), np.float32), loss_fn=lambda y, p: (y, p))
        for arm in ("W_A", "L")
    }
    weighted, literalized = classes["W_A"](), classes["L"]()
    for step in (1, 2):
        w_unique = weighted._represented_weights(step)
        w_literal = literalized._represented_weights(step)
        wrep = weighted._representation(step)
        lrep = literalized._representation(step)
        assert lrep["representation_rows"] != wrep["representation_rows"]
        if step == 1:
            w_mc = w_unique[:4]
            w_data = w_unique[4:]
            l_mc = w_literal[:source.size]
            l_data = w_literal[source.size:]
            assert np.allclose(np.bincount(source, weights=l_mc, minlength=4), w_mc)
            assert np.allclose(np.bincount(source, weights=l_data, minlength=4), w_data)
        else:
            for block in (0, 1):
                lo, hi = block * source.size, (block + 1) * source.size
                expected = w_unique[block * 4:(block + 1) * 4]
                assert np.allclose(
                    np.bincount(source, weights=w_literal[lo:hi], minlength=4), expected)
        inherited = np.concatenate([
            split["signal_train"][source],
            (split["signal_train"] if step == 2 else
             np.concatenate([split["data_train"], split["background_train"]]))[source],
        ])
        # `_representation` hashes the exact per-row inherited membership.
        assert lrep["split_hash"] == COMMON.hash_array(inherited)


@pytest.mark.parametrize(
    "primary,valid,expected",
    [
        ({"push": {"D_same": 0.01, "D_cross_max": 0.04, "D_cross_min": 0.03}},
         True, "EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION"),
        ({"push": {"D_same": 0.01, "D_cross_max": 0.08, "D_cross_min": 0.07}},
         True, "MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW"),
        ({"push": {"D_same": 0.01, "D_cross_max": 0.08, "D_cross_min": 0.015}},
         True, "MIXED_OR_UNRESOLVED"),
        ({"push": {"D_same": 0.03, "D_cross_max": 0.04, "D_cross_min": 0.03}},
         True, "INVALID_OR_NOISY"),
        ({"push": {"D_same": 0.0, "D_cross_max": 0.0, "D_cross_min": 0.0}},
         False, "INVALID_OR_NOISY"),
    ],
)
def test_terminal_classifier_has_no_favorable_default(primary, valid, expected):
    assert COMMON.classify(primary, valid) == expected


def test_push_distance_and_projection_regions_use_predeclared_reducers():
    weight = np.asarray([1.0, 2.0, 3.0])
    a = np.asarray([1.0, 2.0, 1.0])
    b = np.asarray([1.0, 1.0, 2.0])
    expected = np.sum(weight * np.abs(a - b)) / np.sum(weight * (a + b) / 2.0)
    assert np.isclose(COMMON.weighted_push_distance(a, b, weight), expected)
    edges = [np.asarray([0.0, 1.0, 3.0]),
             np.asarray([1.5, 6.0, 10.0, 20.0, 40.0])]
    xsec = np.arange(1, 9, dtype=float).reshape(2, 4)
    sums = EVALUATE._projection_sums(xsec, edges)
    assert set(sums) == {"projection_global", "projection_ppar_lt_6",
                         "projection_ppar_6_to_20", "projection_ppar_gt_20"}
    assert np.isclose(sums["projection_global"],
                      np.sum(xsec * np.diff(edges[0])[:, None] * np.diff(edges[1])[None, :]))


def test_five_operands_are_present_executable_hash_bound_and_no_launch_by_import():
    operands = PROPOSAL["guarded_execution_contract"]["future_required_operands"]
    assert len(operands) == 5
    for item in operands:
        path = REPO / item["path"]
        assert path.is_file()
        assert COMMON.sha256_file(path) == item["sha256"]
        assert item["status"] == "IMPLEMENTED_TESTED_HASH_BOUND"
    assert os.access(PET / "submit_pet_v2_equivalence.sh", os.X_OK)


def test_controller_has_exact_dependencies_guards_and_no_srun_or_retry():
    text = (PET / "submit_pet_v2_equivalence.sh").read_text(encoding="utf-8")
    for variable in ("PETV2_CODE_ROOT", "PETV2_EXPECTED_HEAD", "PETV2_PYTHON",
                     "PETV2_ROOT_PYTHON", "PETV2_INPUT", "PETV2_GATE3_MANIFEST",
                     "PETV2_FLUX_SOURCE_DIR", "PETV2_OUTPUT_ROOT",
                     "PETV2_AUTHORIZATION_TOKEN"):
        assert "${%s:?" % variable in text
    assert "--array=0-2%3" in text
    assert "--constraint='gpu&hbm80g'" in text
    assert 'afterok:${TARGET_JOB}' in text
    assert 'afterok:${TRAIN_JOB}' in text
    assert 'afterok:${EVAL_JOB}' in text
    assert "PETV2_PREFLIGHT_ONLY" in text
    assert "required_current_sources" in text
    assert "new_support_sources" in text
    assert "runEventLoopMC_${playlist}.root" in text
    source_at = text.index('source "$ROOT_ENV_SCRIPT"')
    assert text.rindex("set +u", 0, source_at) < source_at
    assert text.index("set -u", source_at) > source_at
    assert not any(line.lstrip().startswith("srun ") for line in text.splitlines())
    assert "retry" not in text.lower() or '"no_retry_path": True' in text
    assert subprocess.run(["bash", "-n", str(PET / "submit_pet_v2_equivalence.sh")],
                          check=False).returncode == 0


def test_validator_treats_committed_proposal_as_source_not_runtime_product():
    text = (PET / "validate_pet_v2_equivalence_result.py").read_text(encoding="utf-8")
    assert 'proposal_path = _regular(args.proposal, "proposal")' in text
    assert 'proposal_path, proposal = _json(args.proposal, "proposal")' not in text


def test_every_operand_preserves_exact_prohibitions_and_scope_boundary():
    combined = "\n".join((PET / name).read_text(encoding="utf-8") for name in (
        "pet_v2_equivalence_common.py", "materialize_pet_v2_equivalence_target.py",
        "train_pet_v2_equivalence.py", "evaluate_pet_v2_equivalence.py",
        "validate_pet_v2_equivalence_result.py", "submit_pet_v2_equivalence.sh"))
    for prohibition in COMMON.PROHIBITIONS:
        assert prohibition in combined
    assert "C_ML" in combined
    assert "PET_DIAGNOSTIC_AND_METHOD_DEVELOPMENT_ONLY" in combined

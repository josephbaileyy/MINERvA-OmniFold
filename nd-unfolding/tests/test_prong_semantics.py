"""Synthetic regression checks for reconstruction-dependent prong fields."""

from __future__ import annotations

import os
import sys
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
TEST_ROOT = Path(__file__).resolve().parent
for path in (str(TEST_ROOT), str(TEST_ROOT.parent / "pet")):
    if path not in sys.path:
        sys.path.insert(0, path)

import typed_descriptor_keras as keras_adapter  # noqa: E402
import typed_descriptors as typed  # noqa: E402
from test_typed_descriptors import _prong, _synthetic_fixture  # noqa: E402


def _semantic_fixture() -> tuple[typed.TypedDescriptorBatch, NDArray[np.float32]]:
    batch, _, detector, _ = _synthetic_fixture()
    codes = [3, 3, 3, 8, 13, 0, -999, 42, 3]
    charges = [0, 1, 2, 0, 0, 0, -999, 2, 7]
    masses = [105.658, 105.658, 105.658, 938.272, -1, -1, -1, 444, 105.658]
    scores = [1, 1, 1, 0.2, 0.8, 0, -1, 0.4, 1]
    prongs = [
        dict(_prong(index, code), charge=charge, mass=mass, score=score)
        for index, (code, charge, mass, score) in enumerate(
            zip(codes, charges, masses, scores)
        )
    ]
    families = dict(batch.families)
    families["prongs"] = typed.PRONG_CONTRACT.build_batch([[], [], prongs])
    return replace(batch, families=families), detector


def _field_slice(name: str, *, projected: bool) -> slice:
    start = 0
    for field in typed.PRONG_CONTRACT.fields:
        width = field.projected_width if projected else field.width
        if field.name == name:
            return slice(start, start + width)
        start += width
    raise ValueError(name)


class ProngSemanticsTest(unittest.TestCase):
    """Check raw preservation, applicability, and normalization separately."""

    def setUp(self) -> None:
        self.batch, self.detector = _semantic_fixture()
        self.prongs = self.batch.families["prongs"]
        self.normalization = typed.fit_frozen_normalization_for_smoke(
            self.batch, fit_inventory_row_selection_digest="c" * 64
        )

    def test_muon_charge_and_undefined_fields_keep_raw_rows(self) -> None:
        np.testing.assert_array_equal(self.prongs.counts, [0, 0, 9])
        np.testing.assert_array_equal(self.prongs.token_mask, np.ones(9, dtype=bool))
        np.testing.assert_array_equal(
            self.prongs.values["raw_pid"][:, 0], [3, 3, 3, 8, 13, 0, -999, 42, 3]
        )
        np.testing.assert_array_equal(
            self.prongs.values["charge"][:, 0], [0, 1, 2, 0, 0, 0, -999, 2, 7]
        )
        np.testing.assert_array_equal(
            self.prongs.masks["charge"][:, 0],
            [True, True, True, False, False, False, False, False, True],
        )
        np.testing.assert_array_equal(self.prongs.values["mass"][4:7, 0], [-1] * 3)
        self.assertFalse(self.prongs.masks["mass"][4:7].any())
        self.assertFalse(self.prongs.masks["score"][6, 0])
        self.assertTrue(self.prongs.masks["score"][5, 0])
        self.assertTrue(self.prongs.masks["raw_pid"][5, 0])

    def test_scores_remain_on_native_scale_and_mass_fit_excludes_undefined(
        self,
    ) -> None:
        norm = self.normalization.families["prongs"]
        np.testing.assert_array_equal(norm.means["score"], [0])
        np.testing.assert_array_equal(norm.scales["score"], [1])
        expected_mass_mean = float(np.mean([105.658] * 4 + [938.272, 444]))
        self.assertAlmostEqual(
            float(norm.means["mass"][0]), expected_mass_mean, places=4
        )
        features = typed.PRONG_CONTRACT.prepare_features(self.prongs, norm)
        np.testing.assert_array_equal(
            features[:, _field_slice("score", projected=True)].ravel(),
            np.asarray([1, 1, 1, 0.2, 0.8, 0, 0, 0.4, 1], dtype=np.float32),
        )
        expected_charge = np.zeros((9, 4), dtype=np.float32)
        expected_charge[:3, :3] = np.eye(3)
        expected_charge[8, 3] = 1  # An unexpected muon code remains observable.
        np.testing.assert_array_equal(
            features[:, _field_slice("charge", projected=True)], expected_charge
        )
        pid = features[:, _field_slice("raw_pid", projected=True)]
        self.assertEqual(pid[7, -1], 1)
        self.assertEqual(pid[6].sum(), 0)

    def test_applicability_is_enforced_when_caller_supplies_charge_masks(self) -> None:
        masks = dict(self.prongs.masks)
        masks["charge"] = np.ones_like(masks["charge"])
        masks["raw_pid"] = masks["raw_pid"].copy()
        masks["raw_pid"][0] = False
        changed = replace(self.prongs, masks=masks)
        features = typed.PRONG_CONTRACT.prepare_features(
            changed, self.normalization.families["prongs"]
        )
        charge = features[:, _field_slice("charge", projected=True)]
        np.testing.assert_array_equal(charge[0], np.zeros(4))
        np.testing.assert_array_equal(charge[3:8], np.zeros((5, 4)))

    def test_nonidentity_score_normalization_is_rejected(self) -> None:
        families = dict(self.normalization.families)
        means = dict(families["prongs"].means)
        means["score"] = np.asarray([0.5], dtype=np.float32)
        families["prongs"] = typed.FamilyNormalization(
            means=means, scales=families["prongs"].scales
        )
        with self.assertRaisesRegex(ValueError, "score requires identity"):
            replace(self.normalization, families=families)


class ProngKerasSemanticsTest(unittest.TestCase):
    """Exercise semantic masks on the tensor path, including direct callers."""

    def test_tensor_features_match_numpy_with_applicability_and_native_scores(
        self,
    ) -> None:
        try:
            tf = keras_adapter.require_tensorflow()
        except ImportError as error:
            self.skipTest(str(error))
        tf.config.set_visible_devices([], "GPU")
        batch, detector = _semantic_fixture()
        normalization = typed.fit_frozen_normalization_for_smoke(
            batch, fit_inventory_row_selection_digest="c" * 64
        )
        model = keras_adapter.build_keras_typed_descriptor_adapter(normalization)
        inputs = keras_adapter.prepare_keras_inputs(batch, detector)
        output = np.asarray(model(inputs, training=False))
        self.assertEqual(output.shape, (3, 64))
        prongs = batch.families["prongs"]
        expected = typed.PRONG_CONTRACT.prepare_features(
            prongs, normalization.families["prongs"]
        )
        layer = model.family_encoders["prongs"]
        for forged_charge_masks in (False, True):
            with self.subTest(forged_charge_masks=forged_charge_masks):
                if forged_charge_masks:
                    inputs["prongs_masks"][
                        :, _field_slice("charge", projected=False)
                    ] = True
                actual = layer.prepare_features(
                    inputs["prongs_values"],
                    inputs["prongs_masks"],
                    inputs["prongs_token_mask"],
                )
                np.testing.assert_allclose(
                    np.asarray(actual), expected, atol=1e-6, rtol=0
                )
        for family in typed.FAMILY_CONTRACTS:
            inputs[f"{family.name}_enabled"][:] = False
        null_output = np.asarray(model(inputs, training=False))
        np.testing.assert_array_equal(null_output[:, :13], detector)
        np.testing.assert_array_equal(null_output[:, 13:], np.zeros((3, 51)))

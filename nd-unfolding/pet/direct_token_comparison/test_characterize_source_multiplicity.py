"""Tests for the A1 multiplicity characterization, without needing ROOT.

The load-bearing test is ``test_rederivation_matches_production_builder``: the
script re-derives the non-muon energy ranking that ``_build_p12`` performs, and a
re-derivation is exactly the kind of thing that drifts from its original. It is
checked against the real production builder on randomized inputs here, and again
against live entries during the read itself.
"""

from __future__ import annotations

from pathlib import Path
import sys
import types
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import characterize_source_multiplicity as characterize  # noqa: E402
import typed_descriptor_source_smoke as smoke  # noqa: E402


class RetainedEnergiesTests(unittest.TestCase):
    def test_excludes_muon_clusters_and_sorts_descending(self) -> None:
        ordered = characterize.retained_energies(
            [5.0, 100.0, 1.0, 7.0], [0, 1, 0, 0]
        )
        self.assertEqual(list(ordered), [7.0, 5.0, 1.0])

    def test_all_muon_clusters_gives_an_empty_selection(self) -> None:
        self.assertEqual(characterize.retained_energies([3.0, 4.0], [1, 1]).size, 0)

    def test_empty_event_is_empty_not_an_error(self) -> None:
        self.assertEqual(characterize.retained_energies([], []).size, 0)


class TailShareTests(unittest.TestCase):
    def test_share_is_zero_when_the_cap_does_not_bind(self) -> None:
        ordered = characterize.retained_energies(list(range(10, 0, -1)), [0] * 10)
        self.assertEqual(characterize.tail_energy_share(ordered), 0.0)

    def test_share_counts_only_energy_past_the_cap(self) -> None:
        energies = np.asarray([10.0] * 12 + [4.0, 4.0], dtype=np.float64)
        self.assertAlmostEqual(
            characterize.tail_energy_share(energies), 8.0 / 128.0, places=12
        )

    def test_no_retained_energy_is_none_not_zero(self) -> None:
        # None and 0.0 are different statements: one event had nothing to keep,
        # the other kept everything inside the cap. Averaging them together
        # would quietly bias the reported share downward.
        self.assertIsNone(characterize.tail_energy_share(np.zeros(0)))
        self.assertIsNone(characterize.tail_energy_share(np.zeros(5)))
        self.assertEqual(
            characterize.tail_energy_share(np.asarray([1.0] * 13)), 1.0 / 13.0
        )

    def test_cap_is_the_production_cap(self) -> None:
        self.assertEqual(characterize.CAP, smoke.P12_TOKEN_COUNT)


class PhotonCountTests(unittest.TestCase):
    def test_threshold_is_exclusive_as_the_smoke_applies_it(self) -> None:
        threshold = characterize.PHOTON_PRESENCE_THRESHOLD
        self.assertEqual(characterize.photon_count(threshold, threshold), (0, 0))
        self.assertEqual(characterize.photon_count(threshold * 1.001, 0.0), (1, 0))
        self.assertEqual(characterize.photon_count(1.0, 2.0), (2, 0))

    def test_threshold_matches_the_smoke_constant(self) -> None:
        self.assertEqual(
            characterize.PHOTON_PRESENCE_THRESHOLD, smoke.PHOTON_PRESENCE_THRESHOLD
        )

    def test_non_finite_energy_is_counted_separately_not_silently_dropped(
        self,
    ) -> None:
        # The smoke raises here; a long characterization counts instead, and the
        # count must reach the receipt so an ambiguous source cannot look clean.
        self.assertEqual(characterize.photon_count(float("nan"), float("inf")), (0, 2))
        self.assertEqual(characterize.photon_count(float("nan"), 5.0), (1, 1))


class BranchScopeTests(unittest.TestCase):
    def test_scope_is_inside_the_authorized_branch_set(self) -> None:
        scope = characterize.branch_scope(smoke)
        self.assertTrue(set(scope).issubset(set(smoke.REQUIRED_BRANCHES)))
        for required in ("cluster_energy_sz", "cluster_isMuontrack", "n_prongs"):
            self.assertIn(required, scope)

    def test_reads_no_typed_object_payload(self) -> None:
        scope = set(characterize.branch_scope(smoke))
        for forbidden in (
            "prong_part_pos",
            "prong_part_E",
            "MasterAnaDev_BlobX",
            "gamma1_direction",
            "vtx",
        ):
            self.assertNotIn(forbidden, scope)

    def test_a_branch_outside_the_authorized_set_is_refused(self) -> None:
        # Mutation control: shrink the authorized set and the scope must refuse,
        # rather than silently reading a branch nobody cleared.
        stub = types.SimpleNamespace(
            EVENT_KEY_BRANCHES=smoke.EVENT_KEY_BRANCHES,
            GENERIC_VALUE_BRANCHES=smoke.GENERIC_VALUE_BRANCHES,
            GENERIC_COUNT_BRANCHES=smoke.GENERIC_COUNT_BRANCHES,
            REQUIRED_BRANCHES=tuple(
                name for name in smoke.REQUIRED_BRANCHES if name != "n_prongs"
            ),
        )
        with self.assertRaises(ValueError) as caught:
            characterize.branch_scope(stub)
        self.assertIn("n_prongs", str(caught.exception))


class AccumulatorTests(unittest.TestCase):
    def test_at_or_above_cap_differs_from_above_cap(self) -> None:
        accumulator = characterize.Accumulator()
        for count in (11, 12, 13):
            accumulator.add(
                generic_all=count,
                generic_nonmuon=count,
                blobs=0,
                prongs=2,
                photons=0,
                nonfinite_photons=0,
                tail_share=0.0,
            )
        described = accumulator.summary()["generic_clusters_nonmuon"]
        self.assertAlmostEqual(described["fraction_at_or_above_cap"], 2 / 3)
        self.assertAlmostEqual(described["fraction_above_cap"], 1 / 3)

    def test_events_without_retained_energy_stay_out_of_the_tail_mean(self) -> None:
        accumulator = characterize.Accumulator()
        accumulator.add(
            generic_all=0,
            generic_nonmuon=0,
            blobs=0,
            prongs=0,
            photons=0,
            nonfinite_photons=0,
            tail_share=None,
        )
        accumulator.add(
            generic_all=13,
            generic_nonmuon=13,
            blobs=1,
            prongs=2,
            photons=1,
            nonfinite_photons=0,
            tail_share=0.5,
        )
        tail = accumulator.summary()["tail_energy_share_beyond_cap"]
        self.assertEqual(tail["events_with_no_retained_energy"], 1)
        self.assertEqual(tail["events_with_retained_energy"], 1)
        self.assertAlmostEqual(tail["mean"], 0.5)

    def test_histogram_retains_every_observed_count(self) -> None:
        accumulator = characterize.Accumulator()
        for count in (1, 1, 4):
            accumulator.add(
                generic_all=count,
                generic_nonmuon=count,
                blobs=count,
                prongs=count,
                photons=0,
                nonfinite_photons=0,
                tail_share=0.0,
            )
        histogram = accumulator.summary()["blobs"]["histogram"]
        self.assertEqual(histogram, {"1": 2, "4": 1})


class ProductionAgreementTests(unittest.TestCase):
    def test_rederivation_matches_production_builder(self) -> None:
        """The re-derived ranking must equal ``_build_p12`` on random events.

        Built from the production builder's own inputs rather than from the
        re-derivation, so the two can actually disagree.
        """
        rng = np.random.default_rng(20260918)
        for trial in range(200):
            size = int(rng.integers(0, 30))
            energy = rng.gamma(2.0, 50.0, size=size).tolist()
            is_muon = rng.integers(0, 2, size=size).tolist()
            raw: dict[str, object] = {
                "cluster_energy": energy,
                "cluster_pos": rng.normal(size=size).tolist(),
                "cluster_z": rng.normal(size=size).tolist(),
                "cluster_view": rng.integers(1, 4, size=size).tolist(),
                "cluster_time": rng.normal(size=size).tolist(),
                "cluster_isMuontrack": is_muon,
            }
            for name in smoke.GENERIC_VALUE_BRANCHES:
                raw[f"{name}_sz"] = size
            production = smoke._build_p12(raw)
            ordered = characterize.retained_energies(energy, is_muon)
            mine = np.zeros(characterize.CAP, dtype=np.float32)
            mine[: min(ordered.size, characterize.CAP)] = ordered[
                : characterize.CAP
            ].astype(np.float32)
            np.testing.assert_array_equal(
                production[:, 0], mine, err_msg=f"trial {trial}, size {size}"
            )

    def test_the_agreement_check_can_fail(self) -> None:
        """A mutation control: ascending order must be caught."""
        rng = np.random.default_rng(7)
        size = 20
        energy = rng.gamma(2.0, 50.0, size=size).tolist()
        raw: dict[str, object] = {
            "cluster_energy": energy,
            "cluster_pos": [0.0] * size,
            "cluster_z": [0.0] * size,
            "cluster_view": [1] * size,
            "cluster_time": [0.0] * size,
            "cluster_isMuontrack": [0] * size,
        }
        for name in smoke.GENERIC_VALUE_BRANCHES:
            raw[f"{name}_sz"] = size
        production = smoke._build_p12(raw)
        ascending = np.sort(np.asarray(energy, dtype=np.float32))[
            : characterize.CAP
        ]
        self.assertFalse(np.array_equal(production[:, 0], ascending))


if __name__ == "__main__":
    unittest.main(verbosity=2)

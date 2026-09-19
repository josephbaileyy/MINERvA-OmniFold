#!/usr/bin/env python3
"""`z_grade` -- the first production caller of `assess()`, over a real MULTI-MEMBER campaign.

WHAT THESE TESTS ARE FOR. Until now `z_validator.assess()` had no production caller, so every
branch except 2 was reachable only from fixtures that constructed a `Validity` by hand. That is
exactly the shape this campaign keeps paying for: the grading machinery was green and the thing
that would have used it did not exist. These tests drive `z_grade` end to end over products built
by the REAL `z_build`, so the `Validity` under test is one the grader MEASURED rather than one a
test wrote down.

THE FIXTURE IS FULL-GRID BUT NEARLY EMPTY. `central` is a length-`65,856` array -- the real 5D
grid, `14x16x7x7x6` -- with a handful of positive cells. That keeps `m1_functionals` operating on
the real axis geometry (it refuses a mask of any other size) while the covariances stay `n x n`
with `n` small enough to test. A fixture truncated to a convenient size would have made the
functional builder untestable, which is how it would have shipped unexercised.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import p4_lib as p4              # noqa: E402
import z_build as build          # noqa: E402
import z_contract as zc          # noqa: E402
import z_grade as zg             # noqa: E402
import z_receipt as zrec         # noqa: E402
import z_validator as zv         # noqa: E402

GRID = (14, 16, 7, 7, 6)
N_GRID = int(np.prod(GRID))


def full_grid_central():
    """A CV on the real grid whose reported cells land in several `(eavail, W)` destinations.

    Several destinations matter: with one, `M` has a single row and `s_proj`'s population would be
    the all-ones vector plus a duplicate of it, which is a functional set that cannot localise.
    """
    x = np.zeros(N_GRID)
    picks = [(0, 0, 0, 0, 0), (3, 2, 1, 1, 2), (7, 9, 3, 4, 4),
             (13, 15, 6, 6, 5), (2, 5, 1, 0, 2), (9, 1, 5, 3, 1)]
    for j, coord in enumerate(picks):
        x[np.ravel_multi_index(coord, GRID)] = 2.0 + j
    return x


def make_member(directory, *, offset, declared=1, cov_scale=1.0, central=None,
                cv_perturb=0.0, throw_extra=None, pin_bins=0):
    """Build one real Z member with `z_build`, at a declared estimator-seed offset."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ND, text=True).strip()
    x = full_grid_central() if central is None else np.asarray(central, float).copy()
    if cv_perturb:
        x[np.flatnonzero(x > 0)[0]] += cv_perturb
    mask = x > 0
    n = int(mask.sum())

    inventory = (*zc.VERT_BANDS, *zc.LATERAL_BANDS,
                 *(f"synthetic_residual_{i}" for i in range(zc.N_RESIDUAL)))
    support = {}
    for band in inventory:
        d = np.linspace(1.0, 2.0, n) if band in zc.VERT_BANDS else np.linspace(0.2, 0.4, n)
        support[build.SUPPORT_PREFIX + band] = np.diag(d) * cov_scale
    np.savez(directory / "support.npz", **support)

    active = {p4.candidate_band_key(b): np.eye(n) * 0.5 * cov_scale for b in zc.LATERAL_BANDS}
    active[p4.CANDIDATE_ACTIVE_TOTAL_KEY] = np.eye(n) * 0.5 * cov_scale * len(zc.LATERAL_BANDS)
    np.savez(directory / "active.npz", **active)
    np.savez(directory / "stat.npz", covariance=np.eye(n) * 0.7 * cov_scale)
    np.savez(directory / "ml.npz", covariance=np.eye(n) * 0.1 * cov_scale)

    # `compute_g` pins a bin exactly where `v_blk == 0`, so a zero on the block diagonal is how a
    # fixture exercises the pinned set at all.
    blk = np.linspace(1.0, 2.0, n)
    blk[:pin_bins] = 0.0
    throw = {
        "C_unified": np.diag(np.linspace(4.0, 5.0, n)) * cov_scale,
        "C_blocksum": np.diag(blk) * cov_scale,
        "hJointMeanShift": np.linspace(0.1, 0.2, n) * np.sqrt(cov_scale),
        "est_seed_offset_declared": np.int64(declared),
        "est_seed_offset": np.int64(offset),
    }
    throw.update(throw_extra or {})
    np.savez(directory / "throw.npz", **throw)

    np.savez(directory / "central.npz", hXSecND_flat=x)
    zrec.persist_null_operands(
        directory / "null.npz", x, x.copy(), mask,
        code_identity={"revision": "synthetic-fixture",
                       "import_closure_digests": {"test_z_grade.py":
                                                  zrec.sha256_file(Path(__file__))}})
    (directory / "parent.bin").write_bytes(b"synthetic parent; no lineage asserted")

    sources = {role: {"path": f"{role}.npz", "format": "npz",
                      "sha256": zrec.sha256_file(directory / f"{role}.npz")}
               for role in ("support", "active", "stat", "ml", "throw", "central", "null")}
    sources["parent"] = {"path": "parent.bin", "format": "opaque",
                         "sha256": zrec.sha256_file(directory / "parent.bin")}
    manifest = {"schema_version": 1, "input_kind": "synthetic",
                "run": {"id": f"synthetic-member-{offset}", "step": "assembly"},
                "producing_revision": revision, "sources": sources,
                "stat_key": "covariance", "ml_key": "covariance",
                "footing": {"mask_sha256": zrec.sha256_array(mask),
                            "row_order_sha256": zrec.sha256_array(np.flatnonzero(mask))}}
    (directory / "manifest.json").write_text(json.dumps(manifest))
    outputs = {"out_cv": directory / "z-cv.npz", "out_mean": directory / "z-mean.npz",
               "receipt_cv": directory / "receipt-cv.json",
               "receipt_mean": directory / "receipt-mean.json",
               "out_null": directory / "z-null.npz"}
    build.build_z(directory / "manifest.json", **outputs)
    return outputs


def write_prereg(path, **over):
    doc = {"declared_K": [0, 1200], "graded_offset": 0,
           "builder_revision": subprocess.check_output(
               ["git", "rev-parse", "HEAD"], cwd=ND, text=True).strip(),
           "S": 1e-3, "epsilon": 1e-9, "pass_rule": "branch 3 and r_null <= epsilon"}
    doc.update(over)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(doc))
    return str(path)


class GradeCase(unittest.TestCase):
    """Two real members at offsets 0 and 1200, built by `z_build`."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        root = Path(cls._tmp.name)
        cls.out0 = make_member(root / "k0", offset=0, cov_scale=1.0)
        cls.out1 = make_member(root / "k1200", offset=1200, cov_scale=1.0001)
        cls.root = root

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def members(self, **over):
        m0 = zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")
        m1 = zg.Member(self.out1["out_cv"], self.out1["receipt_cv"], "cv")
        for k, v in over.items():
            setattr(m1, k, v)
        return [m0, m1]


class TheCampaignGradesAndTheLegsAreREACHED(GradeCase):
    def test_two_close_members_reach_branch_3_and_PASSING(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 3, out["outcome"]["branch_label"])
        self.assertEqual(out["scientific_acceptance"], "PASSING")
        self.assertTrue(out["null_within_bound"])

    def test_every_declared_leg_was_actually_evaluated(self):
        """The failure this catches: a grade that never reached a leg still reports a branch."""
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        legs = out["outcome"]["leg_results"]
        self.assertEqual(sorted(legs), ["s_agg", "s_med", "s_proj"])
        for name, entry in legs.items():
            self.assertIn("statistic", entry, name)
            self.assertIn("limit", entry, name)
            self.assertEqual(entry["verdict"], "within limit", name)

    def test_the_three_statistics_are_present_finite_and_non_negative(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        for k in ("s_agg", "s_med", "s_proj"):
            v = out["statistics"][k]
            self.assertTrue(np.isfinite(v) and v >= 0.0, f"{k} = {v}")

    def test_a_LARGE_movement_is_an_assessable_FAIL_not_an_error(self):
        far = make_member(self.root / "far", offset=2400, cov_scale=4.0)
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(far["out_cv"], far["receipt_cv"], "cv")]
        out = zg.grade(m, [0, 2400], 0, self.out0["out_null"])
        self.assertTrue(out["outcome"]["assessable"])
        self.assertIn(out["outcome"]["branch"], (4, 5, 6), out["outcome"]["branch_label"])
        self.assertEqual(out["scientific_acceptance"], "NON-PASSING")
        self.assertTrue(out["outcome"]["failing_legs"])

    def test_the_null_gates_the_token_even_on_branch_3(self):
        with mock.patch.object(zg, "measure_null",
                               return_value={"assessable": True, "verdict": "exceeds bound",
                                             "r_null": 1.0}):
            out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 3)
        self.assertEqual(out["scientific_acceptance"], "NON-PASSING")


class ItRefusesTheThingsR9AndTheFalsifiersForbid(GradeCase):
    def test_one_member_is_REFUSED_before_any_array_is_read(self):
        one = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")]
        with self.assertRaises(zc.ZContractError) as cm:
            zg.grade(one, [0], 0, self.out0["out_null"])
        self.assertIn("one-member", str(cm.exception))

    def test_an_UNDECLARED_member_lands_on_branch_2_and_is_named(self):
        """The z-cv.npz case, measured: declared = 0 on every slab of its precursor."""
        und = make_member(self.root / "undeclared", offset=1200, declared=0, cov_scale=1.0001)
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(und["out_cv"], und["receipt_cv"], "cv")]
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 2, out["outcome"]["branch_label"])
        self.assertIn("offset_declared_nonzero", out["outcome"]["validity"]["branch2_failures"])
        self.assertTrue(out["validity_evidence"]["offset_declaration"]["undeclared"])
        self.assertEqual(out["scientific_acceptance"], "NON-PASSING")

    def test_a_read_back_offset_set_that_is_not_K_lands_on_branch_2(self):
        out = zg.grade(self.members(), [0, 999], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 2)
        self.assertIn("offsets_match_K", out["outcome"]["validity"]["branch2_failures"])

    def test_two_members_with_the_SAME_product_are_not_a_campaign(self):
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")]
        m[1].offset = 1200
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 2)
        self.assertIn("product_digests_distinct",
                      out["outcome"]["validity"]["branch2_failures"])

    def test_a_product_without_member_identity_is_REFUSED_at_load(self):
        p = self.root / "stripped.npz"
        with np.load(self.out0["out_cv"], allow_pickle=False) as s:
            arrays = {k: s[k] for k in s.files}
        md = json.loads(str(arrays["metadata_json"].item()))
        md.pop("member_identity")
        arrays["metadata_json"] = np.asarray(json.dumps(md))
        np.savez(p, **arrays)
        with self.assertRaises(zc.ZContractError) as cm:
            zg.Member(p, self.out0["receipt_cv"], "cv")
        self.assertIn("which member it is", str(cm.exception))

    def test_a_variant_mismatch_is_REFUSED(self):
        with self.assertRaises(zc.ZContractError) as cm:
            zg.Member(self.out0["out_mean"], self.out0["receipt_mean"], "cv")
        self.assertIn("declares variant", str(cm.exception))


class FootingFailuresDominateAndAreBranch1(GradeCase):
    def test_a_MOVING_CV_is_branch_1_not_a_measured_movement(self):
        moved = make_member(self.root / "movedcv", offset=1200, cov_scale=1.0001, cv_perturb=1.0)
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(moved["out_cv"], moved["receipt_cv"], "cv")]
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1, out["outcome"]["branch_label"])
        self.assertIn("cv_held_fixed", out["outcome"]["validity"]["branch1_failures"])

    def test_a_NON_FINITE_member_is_branch_1_under_R7(self):
        m = self.members()
        bad = m[1].arrays[zg.TOTAL_KEY].copy()
        bad[0, 0] = np.nan
        m[1].arrays[zg.TOTAL_KEY] = bad
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1, out["outcome"]["branch_label"])
        self.assertIn("all_members_finite", out["outcome"]["validity"]["branch1_failures"])
        self.assertNotIn("all_members_finite", out["outcome"]["validity"]["branch2_failures"])

    def test_a_DIFFERENT_support_mask_is_a_footing_failure(self):
        other = full_grid_central()
        other[np.ravel_multi_index((1, 1, 1, 1, 1), GRID)] = 9.0
        diff = make_member(self.root / "diffmask", offset=1200, central=other)
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(diff["out_cv"], diff["receipt_cv"], "cv")]
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertIn("footing_ok", out["outcome"]["validity"]["branch1_failures"])

    def test_a_TAMPERED_product_breaks_the_digest_agreement(self):
        m = self.members()
        m[1].file_sha256 = "0" * 64
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertIn("digests_agree", out["outcome"]["validity"]["branch1_failures"])


class AValidityFailureReportsNOMagnitude(GradeCase):
    """`SPEC` §3.7b branch 1 ends with two words: **"Report no magnitude."**

    A number printed beside an INCONCLUSIVE verdict is a number somebody quotes. These tests are
    the reason the grader evaluates validity BEFORE it computes anything -- the first version
    computed the statistics unconditionally, which both published them alongside a branch-1
    verdict and CRASHED on the two failures where the members are not even comparable.
    """

    def test_a_branch_1_grade_carries_no_statistics(self):
        m = self.members()
        bad = m[1].arrays[zg.TOTAL_KEY].copy()
        bad[0, 0] = np.nan
        m[1].arrays[zg.TOTAL_KEY] = bad
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertEqual(out["statistics"], {})
        self.assertFalse(out["statistics_detail"]["computed"])
        self.assertIn("all_members_finite", out["statistics_detail"]["blocking_validity_fields"])
        self.assertFalse(out["functionals"]["built"])

    def test_a_branch_2_grade_carries_no_statistics_either(self):
        out = zg.grade(self.members(), [0, 999], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 2)
        self.assertEqual(out["statistics"], {})
        self.assertIn("offsets_match_K", out["statistics_detail"]["blocking_validity_fields"])

    def test_incomparable_members_REPORT_rather_than_raise(self):
        """Two members on different support masks have different dimensions. That is a footing
        failure with a verdict, not a stack trace."""
        other = full_grid_central()
        other[np.ravel_multi_index((1, 1, 1, 1, 1), GRID)] = 9.0
        diff = make_member(self.root / "incomparable", offset=1200, central=other)
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(diff["out_cv"], diff["receipt_cv"], "cv")]
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertEqual(out["statistics"], {})

    def test_a_VALID_campaign_still_reports_all_three(self):
        """The control: the suppression must be conditional, not a way of never reporting."""
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 3)
        self.assertEqual(sorted(out["statistics"]), ["s_agg", "s_med", "s_proj"])
        self.assertTrue(out["functionals"]["n_functionals"] > 1)


class TheFunctionalSetIsBUILTFromTheApprovedProjection(GradeCase):
    def test_it_is_M1_rows_plus_the_all_ones_vector(self):
        m0 = zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")
        U, prov = zg.m1_functionals(m0.mask)
        self.assertEqual(prov["keep_axes"], ["eavail", "W"])
        self.assertEqual(prov["dst_shape"], [7, 6])
        self.assertEqual(prov["n_dst_dense"], 42)
        # ⚠ NOT `U.shape[0] == prov["n_dst_receiving"] + 1`, which the reviewer called
        # tautological -- both sides come from the same `np.vstack`. The expected count is derived
        # INDEPENDENTLY here, from the fixture's own picks: how many distinct (eavail, W) pairs do
        # the reported cells occupy?
        picks = [(0, 0, 0, 0, 0), (3, 2, 1, 1, 2), (7, 9, 3, 4, 4),
                 (13, 15, 6, 6, 5), (2, 5, 1, 0, 2), (9, 1, 5, 3, 1)]
        expected = len({(c[2], c[4]) for c in picks})
        self.assertEqual(U.shape[0], expected + 1,
                         f"{expected} distinct (eavail, W) destinations plus the all-ones vector")
        self.assertEqual(prov["n_dst_receiving"], expected)
        self.assertGreater(expected, 1,
                           "one destination cell cannot localise a projected failure")
        self.assertTrue(np.array_equal(U[-1], np.ones(U.shape[1])))
        self.assertEqual(U.shape[1], int(m0.mask.sum()))

    def test_it_CALLS_the_projector_rather_than_restating_it(self):
        src = (ND / "z_grade.py").read_text(encoding="utf-8")
        self.assertIn("proj.build_projection(", src,
                      "a rule retyped is a second implementation that does not get the next fix")

    def test_it_refuses_a_mask_that_is_not_the_real_grid(self):
        with self.assertRaises(zc.ZContractError):
            zg.m1_functionals(np.ones(100, bool))

    def test_the_M_rows_are_width_weighted_not_unit_weighted(self):
        m0 = zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")
        U, prov = zg.m1_functionals(m0.mask)
        rows = U[:-1]
        nz = rows[rows != 0]
        self.assertTrue(nz.size > 0)
        self.assertFalse(np.allclose(nz, 1.0),
                         "unit weights would be the WRONG convention for a differential density")


class TheGraderTrustsNoProducerBoolean(GradeCase):
    def test_it_reads_no_validity_field_out_of_a_receipt(self):
        src = (ND / "z_grade.py").read_text(encoding="utf-8")
        code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
        for forbidden in ("footing_ok\"", "identities_pass\"", "cv_held_fixed\"",
                          "all_members_finite\""):
            self.assertNotIn(f'receipt.get({forbidden}', code)
        self.assertIn("assembly.gate_symmetry_psd(", code,
                      "identities_pass must come from re-running the gate, not from a boolean")

    def test_the_symmetry_gate_actually_runs_and_can_FAIL(self):
        m = self.members()
        asym = np.array(m[1].arrays[zg.TOTAL_KEY], float, copy=True)
        asym[0, 1] += 1.0
        m[1].arrays[zg.TOTAL_KEY] = asym
        v, ev = zg.cross_member_validity(m, [0, 1200])
        self.assertFalse(v.identities_pass)
        self.assertFalse(ev["identities"][1]["passed"])

    def test_the_null_is_RECOMPUTED_not_read_from_a_receipt(self):
        out = zg.measure_null(self.out0["out_null"])
        self.assertIn("reconstruction", out)
        self.assertIn("r_null", out["reconstruction"])
        self.assertEqual(out["source"]["sha256"], zrec.sha256_file(self.out0["out_null"]))


class TheReceiptCarriesWhatAReaderWouldOtherwiseHaveToTrust(GradeCase):
    def test_it_names_the_graded_digest_and_the_comparison_members(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["graded_product"]["est_seed_offset"], 0)
        self.assertEqual(len(out["comparison_members"]), 1)
        self.assertEqual(out["comparison_members"][0]["est_seed_offset"], 1200)
        self.assertEqual(out["graded_product"]["file_sha256"],
                         zrec.sha256_file(self.out0["out_cv"]))

    def test_it_records_the_declared_leg_set_and_every_boundary(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertEqual([l["name"] for l in out["leg_set"]["legs"]],
                         ["s_agg", "s_med", "s_proj"])
        for key in ("cause3_agg", "cause3_med", "cause3_corr", "null_epsilon"):
            self.assertIn(key, out["boundaries"])

    def test_it_states_that_a_pass_authorizes_nothing(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertIn("NOTHING", out["authorizes"])

    def test_the_cli_exit_code_separates_passing_from_graded_not_passing(self):
        outdir = self.root / "cli"
        rc = zg.main(["--member", f"{self.out0['out_cv']}:{self.out0['receipt_cv']}",
                      "--member", f"{self.out1['out_cv']}:{self.out1['receipt_cv']}",
                      "--declared-K", "0,1200", "--graded-offset", "0",
                      "--null-npz", str(self.out0["out_null"]), "--variant", "cv",
                      "--preregistration", write_prereg(outdir / "prereg.json"),
                      "--out", str(outdir / "grade.json")])
        self.assertEqual(rc, 0)
        written = json.loads((outdir / "grade.json").read_text())
        self.assertEqual(written["scientific_acceptance"], "PASSING")

    def test_the_cli_refuses_to_overwrite_a_grade(self):
        outdir = self.root / "cli2"
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "grade.json").write_text("{}")
        with self.assertRaises(zc.ZContractError):
            zg.main(["--member", f"{self.out0['out_cv']}:{self.out0['receipt_cv']}",
                     "--member", f"{self.out1['out_cv']}:{self.out1['receipt_cv']}",
                     "--declared-K", "0,1200", "--graded-offset", "0",
                     "--null-npz", str(self.out0["out_null"]), "--variant", "cv",
                     "--preregistration", write_prereg(outdir / "prereg.json"),
                     "--out", str(outdir / "grade.json")])


class TheStatisticsAreNUMERICALLYRightNotMerelyFinite(GradeCase):
    """The reviewer's point: `isfinite(v) and v >= 0` would pass on any number at all.

    Scaling one member's covariance by exactly `c` scales every one of the three statistics'
    underlying quantities by `sqrt(c)` -- `sqrt(Tr cC) = sqrt(c) sqrt(Tr C)`, `sigma_i` likewise,
    and `sqrt(u^T cC u)` likewise -- so all three relative changes are exactly `sqrt(c) - 1`. That
    is an answer the fixture does not get to choose.
    """

    def test_all_three_statistics_equal_sqrt_c_minus_one_on_a_pure_rescale(self):
        c = 1.0004
        m = self.members()
        m[1].arrays[zg.TOTAL_KEY] = np.asarray(m[0].cov, float) * c
        U, _ = zg.m1_functionals(m[0].mask)
        stats, detail = zg.member_statistics(m, U)
        for key in ("s_agg", "s_med", "s_proj"):
            self.assertAlmostEqual(stats[key], np.sqrt(c) - 1.0, places=12, msg=key)
        self.assertEqual(detail["s_agg"]["argmax_offset"], 1200)

    def test_the_baseline_member_contributes_exactly_zero_to_the_maximum(self):
        m = self.members()
        m[1].arrays[zg.TOTAL_KEY] = np.asarray(m[0].cov, float) * 1.0004
        U, _ = zg.m1_functionals(m[0].mask)
        _, detail = zg.member_statistics(m, U)
        self.assertEqual(detail["s_agg"]["per_member_rel"][0], 0.0)
        self.assertEqual(detail["s_med"]["per_member_rel"][0], 0.0)


class TheNullIsBOUNDToTheGradedMember(GradeCase):
    """R8: the graded product's `r_null` must be measured in ITS OWN production.

    Before the review nothing tied the `--null-npz` argument to the graded member, so any valid
    null file from any run satisfied the sentence.
    """

    def test_another_members_null_is_REFUSED(self):
        with self.assertRaises(zc.ZContractError) as cm:
            zg.grade(self.members(), [0, 1200], 0, self.out1["out_null"])
        self.assertIn("its own production", str(cm.exception).lower().replace("its own production",
                                                                             "its own production"))

    def test_the_graded_members_own_null_is_accepted_and_bound(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        self.assertTrue(out["null"]["measured"])
        self.assertEqual(out["null"]["bound_to_graded_member"]["product"],
                         str(Path(self.out0["out_cv"]).resolve()))
        self.assertTrue(out["null"]["bound_to_graded_member"]["mask_elementwise_equal"])

    def test_grading_the_OTHER_member_needs_the_OTHER_null(self):
        """The control: the binding is to the graded member, not to member zero."""
        out = zg.grade(self.members(), [0, 1200], 1200, self.out1["out_null"])
        self.assertTrue(out["null"]["measured"])
        self.assertEqual(out["graded_product"]["est_seed_offset"], 1200)

    def test_a_branch_1_campaign_measures_NO_null_at_all(self):
        m = self.members()
        bad = m[1].arrays[zg.TOTAL_KEY].copy()
        bad[0, 0] = np.nan
        m[1].arrays[zg.TOTAL_KEY] = bad
        out = zg.grade(m, [0, 1200], 0, self.out1["out_null"])   # a WRONG null, deliberately
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertFalse(out["null"]["measured"])
        self.assertFalse(out["null_within_bound"])


class TheCheapestForgeryIsREFUSED(GradeCase):
    """From the review: copy a member, add `1e-10` to its diagonal, relabel the offset, pass.

    The covariance digests differ, the statistics are ~0, and the campaign cost nothing. What makes
    two members distinct is that they came from two UPSTREAM PRODUCTIONS, so the check is on the
    throw source and the manifest as well as on the covariance.
    """

    def test_a_perturbed_copy_of_one_member_is_branch_2(self):
        m = [zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv"),
             zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")]
        forged = np.asarray(m[1].cov, float).copy()
        forged[np.diag_indices_from(forged)] += 1e-10 * forged.diagonal().max()
        m[1].arrays[zg.TOTAL_KEY] = forged
        m[1].offset = 1200
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 2, out["outcome"]["branch_label"])
        self.assertIn("product_digests_distinct",
                      out["outcome"]["validity"]["branch2_failures"])
        ev = out["validity_evidence"]["product_digests"]
        self.assertTrue(ev["covariance_distinct"], "the perturbation DID change the covariance")
        self.assertFalse(ev["throw_source_distinct"], "but there is only one upstream production")

    def test_members_built_by_DIFFERENT_CODE_are_a_footing_failure(self):
        m = self.members()
        md = dict(m[1].metadata)
        md["code_identity"] = {**md["code_identity"], "revision": "0" * 40}
        m[1].metadata = md
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertIn("footing_ok", out["outcome"]["validity"]["branch1_failures"])
        self.assertFalse(out["validity_evidence"]["code_identity"]["agree"])


class Section1p3bIsReVerifiedNotAssumed(GradeCase):
    """The review's BLOCK: `identities_pass` used to be `gate_symmetry_psd` and nothing else."""

    def test_a_DEFLATED_member_does_not_pass_the_identities(self):
        """⚠ RENAMED AND ITS CLAIM CORRECTED. This was called
        `test_an_UNINFLATED_member_does_not_pass_the_identities`, and an independent reviewer
        showed the name asserted something the body does not test: it sets `g = 0.5`, which is
        DEFLATION, and `g >= 1` refuses that trivially. An uninflated member has `g = 1`, which
        this check does NOT refuse -- see the next test, where the reason it must not is measured.
        """
        m = self.members()
        m[1].arrays["hInflation_g"] = np.full_like(
            np.asarray(m[1].arrays["hInflation_g"], float), 0.5)
        out = zg.grade(m, [0, 1200], 0, self.out0["out_null"])
        self.assertEqual(out["outcome"]["branch"], 1)
        self.assertIn("identities_pass", out["outcome"]["validity"]["branch1_failures"])
        self.assertFalse(out["validity_evidence"]["identities"][1]["g_domain"]["ge_one"])

    def test_an_ALL_ONES_g_is_ACCEPTED_and_that_is_correct(self):
        """The case the reviewer raised, and the reason the domain check must not refuse it.

        `compute_g` returns exactly `1` wherever `v_uni <= v_blk`, so an all-ones `g` is a
        LEGITIMATE outcome, not a discarded inflation -- measured here rather than argued.
        Refusing it would be a guard that fires on a correct run.
        """
        v_blk, v_uni = np.array([4.0, 9.0, 16.0]), np.array([1.0, 2.0, 3.0])
        g, pinned = zg.assembly.compute_g(v_uni, v_blk)
        self.assertTrue(np.array_equal(g, np.ones(3)), f"compute_g gave {g}")
        self.assertFalse(pinned.any())

    def test_what_ACTUALLY_catches_a_discarded_inflation_is_the_reconstruction_block(self):
        """And the limitation is stated rather than papered over.

        `g` cannot be re-derived from the product: `gate_g_reconstruction` needs `v_uni` and
        `v_blk`, which the product does not carry -- it carries their consequence. What the grader
        CAN do is refuse a receipt that does not PROVE the gate ran with a measured residual inside
        a stated rtol, which is what `z_receipt.validate_reconstruction_ran` checks and what
        `test_a_receipt_that_does_not_PROVE_the_reconstruction_ran_fails` exercises. A producer
        that skipped the gate has no such block; `z_build` cannot produce one without running it.
        """
        m = self.members()
        r = json.loads(json.dumps(m[1].receipt))
        r["inflation"][zrec.RECONSTRUCTION_KEY]["per_variant"]["cv"]["max_rel_diff"] = 1e9
        m[1].receipt = r
        v, ev = zg.cross_member_validity(m, [0, 1200])
        self.assertFalse(v.identities_pass)
        self.assertFalse(ev["identities"][1]["reconstruction"]["proved"])

    def test_g_must_be_EXACTLY_one_on_the_pinned_set(self):
        """A fixture that pins no bins makes this condition VACUOUS, so this one pins two."""
        a = make_member(self.root / "pin_a", offset=0, pin_bins=2)
        b = make_member(self.root / "pin_b", offset=1200, pin_bins=2, cov_scale=1.0001)
        m = [zg.Member(a["out_cv"], a["receipt_cv"], "cv"),
             zg.Member(b["out_cv"], b["receipt_cv"], "cv")]
        pinned = np.asarray(m[1].arrays["hPinnedMask"], float).astype(bool)
        self.assertEqual(int(pinned.sum()), 2, "the fixture must actually pin bins")
        v_ok, _ = zg.cross_member_validity(m, [0, 1200])
        self.assertTrue(v_ok.identities_pass, "control: a correct pinned member passes")
        g = np.asarray(m[1].arrays["hInflation_g"], float).copy()
        g[pinned] = 1.0 + 1e-9
        m[1].arrays["hInflation_g"] = g
        v, ev = zg.cross_member_validity(m, [0, 1200])
        self.assertFalse(v.identities_pass)
        self.assertFalse(ev["identities"][1]["g_domain"]["exactly_one_where_pinned"])

    def test_a_receipt_that_does_not_PROVE_the_reconstruction_ran_fails(self):
        m = self.members()
        r = json.loads(json.dumps(m[1].receipt))
        r["inflation"].pop(zrec.RECONSTRUCTION_KEY, None)
        m[1].receipt = r
        v, ev = zg.cross_member_validity(m, [0, 1200])
        self.assertFalse(v.identities_pass)
        self.assertFalse(ev["identities"][1]["reconstruction"]["proved"])

    def test_a_receipt_missing_a_closure_block_fails(self):
        m = self.members()
        r = json.loads(json.dumps(m[1].receipt))
        r["closure"].pop("active_total_eq_sum5", None)
        m[1].receipt = r
        v, ev = zg.cross_member_validity(m, [0, 1200])
        self.assertFalse(v.identities_pass)
        self.assertIn("active_total_eq_sum5", ev["identities"][1]["closure_blocks"]["missing"])

    def test_the_VALID_members_pass_every_re_verified_identity(self):
        """The control. Without it the four tests above could pass for the wrong reason."""
        v, ev = zg.cross_member_validity(self.members(), [0, 1200])
        self.assertTrue(v.identities_pass)
        for row in ev["identities"]:
            self.assertIn("gate_symmetry_psd", row["reran"])
            self.assertIn("g_domain", row["reran"])
            self.assertTrue(row["reconstruction"]["proved"])
            self.assertEqual(row["closure_blocks"]["missing"], [])

    def test_an_infrastructure_fault_is_NOT_converted_into_a_failed_identity(self):
        """The review's last MAJOR: a bare `except Exception` hid MemoryError and typos."""
        m = self.members()
        with mock.patch.object(zg.assembly, "gate_symmetry_psd",
                               side_effect=MemoryError("out of memory")):
            with self.assertRaises(MemoryError):
                zg.cross_member_validity(m, [0, 1200])


class ThePreregistrationBindsKAndTheGradedOffset(GradeCase):
    """R8, and the reviewer's point that a `K` chosen after seeing the offsets is a description."""

    def prereg(self, **over):
        doc = {"declared_K": [0, 1200], "graded_offset": 0,
               "builder_revision": subprocess.check_output(
                   ["git", "rev-parse", "HEAD"], cwd=ND, text=True).strip(),
               "S": 1e-3, "epsilon": 1e-9, "pass_rule": "branch 3 and r_null <= epsilon"}
        doc.update(over)
        path = self.root / f"prereg-{abs(hash(json.dumps(doc, sort_keys=True)))}.json"
        path.write_text(json.dumps(doc))
        return zg.load_preregistration(path)

    def test_a_matching_preregistration_is_accepted_and_recorded(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"],
                       prereg=self.prereg())
        self.assertEqual(out["preregistration"]["declared_K"], [0, 1200])
        self.assertIn("sha256", out["preregistration"]["_stamp"])

    def test_a_K_that_disagrees_with_the_preregistration_is_REFUSED(self):
        with self.assertRaises(zc.ZContractError) as cm:
            zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"],
                     prereg=self.prereg(declared_K=[0, 2400]))
        self.assertIn("predeclaration", str(cm.exception))

    def test_a_graded_offset_that_disagrees_is_REFUSED(self):
        with self.assertRaises(zc.ZContractError):
            zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"],
                     prereg=self.prereg(graded_offset=1200))

    def test_a_builder_revision_that_disagrees_is_REFUSED(self):
        with self.assertRaises(zc.ZContractError) as cm:
            zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"],
                     prereg=self.prereg(builder_revision="0" * 40))
        self.assertIn("builder", str(cm.exception))

    def test_a_preregistration_missing_a_required_field_is_REFUSED(self):
        path = self.root / "short-prereg.json"
        path.write_text(json.dumps({"declared_K": [0, 1200]}))
        with self.assertRaises(zc.ZContractError):
            zg.load_preregistration(path)


class TheProjectionRowsContributeExactlyOnce(GradeCase):
    def test_every_reported_cell_reaches_exactly_one_destination(self):
        m0 = zg.Member(self.out0["out_cv"], self.out0["receipt_cv"], "cv")
        U, _ = zg.m1_functionals(m0.mask)
        rows = U[:-1]
        self.assertTrue(np.all((rows != 0).sum(axis=0) == 1),
                        "marginalization sends each source cell to exactly one destination")
        self.assertTrue(np.all((rows != 0).sum(axis=1) >= 1))


class DistinctnessRestsOnBYTESNotOnRecordedStrings(GradeCase):
    """The reviewer's second BLOCK: the first version compared strings the members carried.

    Copy a member, perturb its covariance, edit one character of the recorded throw digest, and
    two strings differ while one campaign exists. A digest is evidence only when something
    re-computes it from the file.
    """

    def test_a_member_whose_throw_source_is_ABSENT_cannot_be_graded(self):
        import shutil
        d = self.root / "orphan"
        out = make_member(d, offset=1200, cov_scale=1.0001)
        (d / "throw.npz").unlink()
        m = zg.Member(out["out_cv"], out["receipt_cv"], "cv")
        with self.assertRaises(zc.ZContractError) as cm:
            m.throw_source_on_disk()
        self.assertIn("not present", str(cm.exception))

    def test_an_EDITED_recorded_digest_is_caught_by_re_hashing(self):
        out = make_member(self.root / "edited", offset=1200, cov_scale=1.0001)
        p = self.root / "edited-product.npz"
        with np.load(out["out_cv"], allow_pickle=False) as s:
            arrays = {k: s[k] for k in s.files}
        md = json.loads(str(arrays["metadata_json"].item()))
        md["member_identity"]["read_from"]["sha256"] = "f" * 64
        arrays["metadata_json"] = np.asarray(json.dumps(md))
        np.savez(p, **arrays)
        m = zg.Member(p, out["receipt_cv"], "cv")
        with self.assertRaises(zc.ZContractError) as cm:
            m.throw_source_on_disk()
        self.assertIn("was not built from the file this member names", str(cm.exception))

    def test_the_honest_members_verify_against_their_own_files(self):
        for m in self.members():
            v = m.throw_source_on_disk()
            self.assertTrue(v["verified"])
            self.assertEqual(v["recorded"], v["recomputed"])

    def test_the_receipt_carries_the_RECOMPUTED_digests(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        rows = out["validity_evidence"]["product_digests"]["throw_source"]
        self.assertEqual(len(rows), 2)
        for r in rows:
            self.assertTrue(r["verified"])


class ThePreregistrationCannotBeDroppedFromTheCommandLine(GradeCase):
    def test_the_CLI_REFUSES_to_run_without_one(self):
        with self.assertRaises(SystemExit) as cm:
            zg.main(["--member", f"{self.out0['out_cv']}:{self.out0['receipt_cv']}",
                     "--member", f"{self.out1['out_cv']}:{self.out1['receipt_cv']}",
                     "--declared-K", "0,1200", "--graded-offset", "0",
                     "--null-npz", str(self.out0["out_null"]), "--variant", "cv",
                     "--out", str(self.root / "nope" / "grade.json")])
        self.assertNotEqual(cm.exception.code, 0)

    def test_the_flag_has_NO_DEFAULT_in_the_parser(self):
        src = (ND / "z_grade.py").read_text(encoding="utf-8")
        self.assertRegex(src, r'--preregistration"[^)]*required=True')
        self.assertNotRegex(src, r'--preregistration"[^)]*default=None')


class TheKappaArmIsRECORDEDEvenThoughItCannotBeEvaluated(GradeCase):
    """A limitation that leaves no operand behind cannot be closed later without re-running."""

    def test_the_rayleigh_quotients_are_measured_and_written(self):
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        blk = out["statistics_detail"]["kappa_arm_NOT_EVALUATED"]
        self.assertTrue(blk["operand_recorded_so_a_later_kappa_can_be_applied"])
        self.assertIn("kappa", blk["predicate"])
        self.assertEqual(len(blk["rayleigh_quotients"]), out["functionals"]["n_functionals"])
        self.assertTrue(all(np.isfinite(q) and q > 0 for q in blk["rayleigh_quotients"]))
        self.assertGreater(blk["lambda_max_baseline"], 0.0)

    def test_a_later_kappa_could_be_applied_to_the_recorded_quotients(self):
        """The point of recording them: the comparison is reproducible from the receipt alone."""
        out = zg.grade(self.members(), [0, 1200], 0, self.out0["out_null"])
        blk = out["statistics_detail"]["kappa_arm_NOT_EVALUATED"]
        hypothetical = blk["min_rayleigh"] * 2.0
        offenders = [i for i, q in enumerate(blk["rayleigh_quotients"]) if q < hypothetical]
        self.assertTrue(offenders, "a kappa above the minimum must name at least one functional")


class PerBinMovementGetsTheSameMaskIdentity(GradeCase):
    def test_a_spoofed_mask_is_REFUSED_when_x_cv_is_supplied(self):
        import z_statistics as zs
        m = self.members()
        covs = {0: m[0].cov, 1200: m[1].cov}
        good = m[0].mask
        spoof = np.zeros_like(good)
        idx = np.flatnonzero(good)
        spoof[(idx + 1) % spoof.size] = True          # same popcount, different cells
        self.assertEqual(int(spoof.sum()), int(good.sum()))
        with self.assertRaises(zc.ZContractError):
            zs.per_bin_movement(covs, spoof, baseline_key=0, x_cv=m[0].central)

    def test_the_production_caller_ALWAYS_supplies_x_cv(self):
        src = (ND / "z_grade.py").read_text(encoding="utf-8")
        self.assertRegex(src, r"per_bin_movement\([^)]*x_cv=base\.central")

    def test_the_honest_mask_is_accepted_and_names_a_GRID_index(self):
        import z_statistics as zs
        m = self.members()
        out = zs.per_bin_movement({0: m[0].cov, 1200: m[1].cov}, m[0].mask,
                                  baseline_key=0, x_cv=m[0].central)
        self.assertIn(out["argmax_grid_index"], np.flatnonzero(m[0].mask).tolist())
        self.assertEqual(out["n_support"], int(m[0].mask.sum()))


if __name__ == "__main__":
    unittest.main()

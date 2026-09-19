#!/usr/bin/env python3
"""`scientific_acceptance` and `outcome` must be COMPUTED, never asserted. R1.

WHAT THIS REPLACES. `z_build.py` wrote `"scientific_acceptance": "NON-PASSING"` as a LITERAL at
:608 and :788, built `science` as a constant dict at :652-658 with `assessable: False` and
`reject_conditions: ["4c"]`, and :841 documented NON-PASSING as *"the only outcome this command can
produce"*. `z_validator.assess()` -- the only function that ever returns `assessable=True` -- was
never called. A field that cannot vary is not a verdict.

THE TOKEN MAPPING IS NOT INVENTED. `scientific_acceptance` already has exactly two values in this
tree: `NON-PASSING` (the builder) and `PASSING` (`project_cov_nd`'s adoptable fixture). The mapping
is `PASSING` iff the computed outcome `is_met` -- `assessable and branch == 3` -- and the null is
within its bound; otherwise `NON-PASSING`. No third token is introduced.
"""
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import z_validator as zv            # noqa: E402
import z_build as zb                # noqa: E402


def _all_true_validity(**over):
    kw = dict(footing_ok=True, digests_agree=True, partition_agrees=True, identities_pass=True,
              cv_held_fixed=True, offsets_match_K=True, offset_declared_nonzero=True,
              product_digests_distinct=True, all_members_finite=True)
    kw.update(over)
    return zv.Validity(**kw)


class TheBuilderCarriesNoHardcodedAcceptance(unittest.TestCase):
    """The regression that matters: a literal reintroduced anywhere makes the field a constant."""

    def test_no_hardcoded_acceptance_literal_survives_in_the_builder(self):
        src = (ND / "z_build.py").read_text(encoding="utf-8")
        code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
        for tok in ('"scientific_acceptance": "NON-PASSING"',
                    '"scientific_acceptance": "PASSING"',
                    "'scientific_acceptance': 'NON-PASSING'"):
            self.assertNotIn(tok, code,
                             f"{tok} is a hardcoded acceptance verdict; it must be computed")

    def test_no_hardcoded_assessable_or_reject_literal_survives(self):
        src = (ND / "z_build.py").read_text(encoding="utf-8")
        code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
        self.assertNotIn('"assessable": False', code)
        self.assertNotIn('"reject_conditions": ["4c"]', code)

    def test_the_builder_CALLS_assess(self):
        src = (ND / "z_build.py").read_text(encoding="utf-8")
        self.assertIn("validator.assess(", src,
                      "the builder must call z_validator.assess(); a verdict it writes itself "
                      "is not a computed verdict")


class TheMappingProducesAllThreeOutcomes(unittest.TestCase):
    """Fixtures that must yield PASS, assessable FAIL, and unassessable/4c.

    Each drives `zb.acceptance_token()` -- the single mapping the builder uses -- so the test
    exercises the production function rather than a restatement of it.
    """

    LEGS = zv.LegSet(legs=(
        zv.Leg(name="s_agg", klass="aggregate", boundary_key="cause3_agg", statistic_key="s_agg"),
        zv.Leg(name="s_med", klass="per-bin", boundary_key="cause3_med", statistic_key="s_med"),),
        predeclared_at="test fixture")

    def test_PASS_when_every_leg_is_within_its_boundary(self):
        out = zv.assess(self.LEGS, {"s_agg": 0.01, "s_med": 0.01}, _all_true_validity())
        self.assertTrue(out.assessable)
        self.assertEqual(out.branch, 3, out.branch_label)
        self.assertEqual(zb.acceptance_token(out, null_within=True), "PASSING")

    def test_assessable_FAIL_when_a_leg_exceeds(self):
        out = zv.assess(self.LEGS, {"s_agg": 0.99, "s_med": 0.01}, _all_true_validity())
        self.assertTrue(out.assessable, "an exceeded boundary is a measured FAIL, not unassessable")
        self.assertIn(out.branch, (4, 5, 6))
        self.assertEqual(zb.acceptance_token(out, null_within=True), "NON-PASSING")

    def test_unassessable_4c_when_a_boundary_is_withheld(self):
        legs = zv.LegSet(legs=(zv.Leg(name="null-ish", klass="aggregate",
                                      boundary_key="null_epsilon", statistic_key="s_agg"),),
                         predeclared_at="test fixture")
        import z_contract as zc
        from unittest import mock
        with mock.patch.dict(zc.Z_BOUNDARIES, {"null_epsilon": zc.Boundary.withheld("null_epsilon", "INJECTED BY TEST: the registry no longer withholds any boundary, so the invariant under test must supply its own rather than borrow the last one standing.")}):
            out = zv.assess(legs, {"s_agg": 0.01}, _all_true_validity())
        self.assertFalse(out.assessable)
        self.assertIn("4c", out.reject_conditions)
        self.assertEqual(zb.acceptance_token(out, null_within=True), "NON-PASSING")

    def test_a_MET_outcome_with_the_null_OUT_of_bound_is_still_NON_PASSING(self):
        """SPEC 3.7a item 4: any null failure ABORTS the run. MET legs cannot rescue it."""
        out = zv.assess(self.LEGS, {"s_agg": 0.01, "s_med": 0.01}, _all_true_validity())
        self.assertEqual(out.branch, 3)
        self.assertEqual(zb.acceptance_token(out, null_within=False), "NON-PASSING")

    def test_the_mapping_introduces_no_third_token(self):
        seen = {zb.acceptance_token(o, n)
                for o in (zv.assess(self.LEGS, {"s_agg": 0.01, "s_med": 0.01}, _all_true_validity()),
                          zv.assess(self.LEGS, {"s_agg": 0.99, "s_med": 0.01}, _all_true_validity()))
                for n in (True, False)}
        self.assertTrue(seen <= {"PASSING", "NON-PASSING"}, f"unexpected token(s): {seen}")


class ASingleMemberBuildCannotReachMET(unittest.TestCase):
    """Not a defect -- the structural fact that decides this goal's outcome.

    `Validity`'s branch-2 fields are member-campaign properties: `offsets_match_K`,
    `offset_declared_nonzero`, `product_digests_distinct`. One member cannot set them truthfully,
    and `assess()` returns branch 2 BEFORE consulting any statistic. Branch 2 is "INCONCLUSIVE /
    VACUOUS BASELINE VARIATION", whose own docstring says a zero spread is evidence the knob never
    reached the estimator and MUST NEVER READ AS MET.

    ⚠ UPDATED FOR R7. `all_members_finite` used to be in this list and is now a BRANCH-1 field, so
    the fixture states it TRUE: one member's product either is finite or is not, and this build's
    is. Leaving it False would now assert a footing failure that did not occur, and the test would
    pass for the wrong reason -- branch 1 instead of branch 2.
    """
    def test_one_member_validity_yields_branch_2_not_MET(self):
        v = _all_true_validity(offsets_match_K=False, offset_declared_nonzero=False,
                               product_digests_distinct=False, all_members_finite=True)
        out = zv.assess(TheMappingProducesAllThreeOutcomes.LEGS, {}, v)
        self.assertTrue(out.assessable)
        self.assertEqual(out.branch, 2, out.branch_label)
        self.assertEqual(zb.acceptance_token(out, null_within=True), "NON-PASSING")

    def test_and_it_short_circuits_BEFORE_the_missing_statistic_raise(self):
        """Why the builder may pass {} for statistics it does not have: branch 2 returns first."""
        v = _all_true_validity(offsets_match_K=False)
        out = zv.assess(TheMappingProducesAllThreeOutcomes.LEGS, {}, v)
        self.assertEqual(out.branch, 2)


class ValidityFieldsRestOnTheEvidenceTheyNAME(unittest.TestCase):
    """From the independent review: a field must be gated by the thing its comment cites.

    `cv_held_fixed` was `bool(null_block)`, justified by a provenance claim
    `reconstruct_null_ratio` does not make -- it compares whatever arrays it was handed. The real
    check, `x1 == central`, was recorded passively and gated nothing. `digests_agree` was bound to
    matrix-symmetry gates rather than to any digest.
    """
    def test_cv_held_fixed_follows_the_cv_crosscheck_not_the_null_block(self):
        self.assertTrue(zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"}, members_finite=True).cv_held_fixed)
        self.assertFalse(zb.build_validity({"p": 1}, {"g": 1}, False, {"sha256": "x"}, members_finite=True).cv_held_fixed,
                         "a failed CV cross-check must not report the CV as held fixed")

    def test_digests_agree_follows_a_DIGEST_not_the_matrix_gates(self):
        self.assertTrue(zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"}, members_finite=True).digests_agree)
        self.assertFalse(zb.build_validity({"p": 1}, {"g": 1}, True, None, members_finite=True).digests_agree,
                         "no digest stamp must not read as digests agreeing")

    def test_a_failed_cv_crosscheck_lands_on_branch_1_not_branch_2(self):
        """It is a FOOTING failure, and the branch must say so rather than blaming spread."""
        v = zb.build_validity({"p": 1}, {"g": 1}, False, {"sha256": "x"}, members_finite=True)
        out = zv.assess(zv.Z_LEG_SET, {}, v)
        self.assertEqual(out.branch, 1, out.branch_label)


class TheBuilderMEASURESFinitenessRatherThanAssertingIt(unittest.TestCase):
    """R7 -- Joseph, 2026-09-19. Moving the field is only half the fix.

    `all_members_finite` was hardcoded `False` with the note *"member-campaign property: requires
    >= 2 members"*. That note was already wrong -- finiteness of a product is a per-member
    property, evaluable with one member -- and under R7 it becomes CONSEQUENTIAL: a constant
    `False` in a BRANCH-1 field would report WRONG FOOTING on every build forever and make branch
    3 unreachable by construction. The builder must measure it off the arrays it is about to
    write.
    """

    def test_it_reports_what_it_was_told_in_both_directions(self):
        self.assertTrue(zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"},
                                          members_finite=True).all_members_finite)
        self.assertFalse(zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"},
                                           members_finite=False).all_members_finite)

    def test_the_caller_CANNOT_omit_it(self):
        """No default. A field this one now gates branch 1 on must be stated, not inherited."""
        with self.assertRaises(TypeError):
            zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"})

    def test_no_constant_all_members_finite_survives_in_the_builder(self):
        """⚠ WIDENED AFTER REVIEW. The first version matched the exact contiguous string
        `all_members_finite=False`, which `all_members_finite = False` evades -- a regression test
        a single space defeats is not one. It now matches either literal through any whitespace,
        and separately refuses a dict-literal spelling of the same assignment."""
        src = (ND / "z_build.py").read_text(encoding="utf-8")
        code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
        self.assertNotRegex(code, r"all_members_finite\s*=\s*(False|True)\b",
                            "a constant in a branch-1 field makes MET unreachable, and "
                            "asserting finiteness is not measuring it")
        self.assertNotRegex(code, r"[\"']all_members_finite[\"']\s*:\s*(False|True)\b",
                            "the same assignment spelled as a dict entry")

    def test_a_non_finite_member_lands_on_branch_1_from_the_builders_own_validity(self):
        v = zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"}, members_finite=False)
        out = zv.assess(zv.Z_LEG_SET, {}, v)
        self.assertEqual(out.branch, 1, out.branch_label)
        self.assertIn("all_members_finite", out.validity["branch1_failures"])

    def test_a_finite_single_member_build_still_lands_on_branch_2(self):
        """The control: the R7 move must not reclassify an ordinary single-member build."""
        v = zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"}, members_finite=True)
        out = zv.assess(zv.Z_LEG_SET, {}, v)
        self.assertEqual(out.branch, 2, out.branch_label)

    def test_the_note_no_longer_claims_it_needs_two_members(self):
        v = zb.build_validity({"p": 1}, {"g": 1}, True, {"sha256": "x"}, members_finite=True)
        self.assertNotIn("all_members_finite", v.notes,
                         "a measured field carries its value, not an excuse for not having one")

    def test_an_empty_array_does_not_clear_the_finiteness_predicate(self):
        """Review NIT: `np.all(np.isfinite([]))` is True. A claim over zero elements is not one."""
        import numpy as np
        self.assertTrue(np.all(np.isfinite(np.array([]))),
                        "if this ever becomes False the guard below is redundant, not wrong")
        src = (ND / "z_build.py").read_text(encoding="utf-8")
        self.assertRegex(src, r"size\s*>\s*0 and np\.all\(np\.isfinite",
                         "the predicate must require a non-empty array as well as a finite one")

    def test_a_non_finite_UPSTREAM_operand_fails_CLOSED_before_the_verdict(self):
        """Review MINOR: `expected` covers the arrays written, not `parts`/`operands`.

        The reviewer is right about the population and right that the diagnostic differs. Measured
        here rather than argued: a non-finite component block does not reach `assess()` at all --
        the assembly gate RAISES, which is strictly stronger than a branch-1 verdict because no
        product and no receipt are produced. The one case that would be a defect is a non-finite
        operand that SILENTLY PASSES, and that is what this excludes.
        """
        import numpy as np
        import z_assembly as za
        import z_contract as zc
        bad = np.eye(4)
        bad[1, 1] = float("nan")
        with self.assertRaises(zc.ZContractError):
            za.gate_symmetry_psd(bad)
        inf = np.eye(4)
        inf[2, 2] = float("inf")
        with self.assertRaises(zc.ZContractError):
            za.gate_symmetry_psd(inf)

    def test_the_builder_measures_finiteness_of_the_arrays_it_writes(self):
        """Provenance: the argument must come from `np.isfinite` over `expected`, not a literal."""
        src = (ND / "z_build.py").read_text(encoding="utf-8")
        self.assertIn("members_finite=", src)
        self.assertRegex(src, r"members_finite\s*=\s*bool\(")
        self.assertIn("np.isfinite", src)


if __name__ == "__main__":
    unittest.main()

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
    `offset_declared_nonzero`, `product_digests_distinct`, `all_members_finite`. One member cannot
    set them truthfully, and `assess()` returns branch 2 BEFORE consulting any statistic. Branch 2
    is "INCONCLUSIVE / VACUOUS BASELINE VARIATION", whose own docstring says a zero spread is
    evidence the knob never reached the estimator and MUST NEVER READ AS MET.
    """
    def test_one_member_validity_yields_branch_2_not_MET(self):
        v = _all_true_validity(offsets_match_K=False, offset_declared_nonzero=False,
                               product_digests_distinct=False, all_members_finite=False)
        out = zv.assess(TheMappingProducesAllThreeOutcomes.LEGS, {}, v)
        self.assertTrue(out.assessable)
        self.assertEqual(out.branch, 2, out.branch_label)
        self.assertEqual(zb.acceptance_token(out, null_within=True), "NON-PASSING")

    def test_and_it_short_circuits_BEFORE_the_missing_statistic_raise(self):
        """Why the builder may pass {} for statistics it does not have: branch 2 returns first."""
        v = _all_true_validity(offsets_match_K=False)
        out = zv.assess(TheMappingProducesAllThreeOutcomes.LEGS, {}, v)
        self.assertEqual(out.branch, 2)


if __name__ == "__main__":
    unittest.main()

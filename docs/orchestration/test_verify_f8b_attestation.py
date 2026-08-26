"""Fail-closed arms for the F-8(b) attestation validator -- the only thing in this pair that passes.

Because this validator CAN return 0, it is the fail-open surface of the whole design, and it gets
the heavier suite. Every requirement has an arm that REMOVES it and asserts rejection; the valid
synthetic arm is the paired silent-on-good case. Without the removal arms, a validator that returns
0 unconditionally would pass a suite made only of the good arm.

Two arms deserve naming. `test_self_attestation_*` is the defect the clause exists to prevent -- the
receipt's author grading their own prose -- and it is checked on BOTH role and conversation uuid,
because one lane can rename itself and one uuid can claim two roles. `test_a_binding_that_never_moves
_binds_nothing` is the opposite-direction case: it is not enough that a matching digest passes, a
NON-matching digest must fail, or the binding is decoration.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("vf8a", HERE / "verify_f8b_attestation.py")
A = importlib.util.module_from_spec(_spec)
sys.modules["vf8a"] = A
_spec.loader.exec_module(A)

RECEIPT_BYTES = b"# Run receipt\n\n## Blind spots\n\nfour of them, authored.\n"
REPORT_BYTES = b'{"schema": "f8b-linter-report/1", "status": "REVIEW_REQUIRED"}\n'
RECEIPT_SHA = hashlib.sha256(RECEIPT_BYTES).hexdigest()
REPORT_SHA = hashlib.sha256(REPORT_BYTES).hexdigest()

# Four findings that are distinct from each other and long enough to be judgements rather than
# checkboxes. Their CONTENT is not graded by the validator and deliberately so -- see the module
# docstring of verify_f8b_attestation.py. These exist to exercise structure.
FINDINGS = {
    "namespace-packages": (
        "The receipt does engage: it says why origin is None reaches no comparison, and it says the "
        "hole is narrow because a real module outranks a portion. That is a reason, not a mention."),
    "already-imported-modules": (
        "Engaged, and correctly scoped to the wrapper's own imports rather than claimed as a general "
        "hole. The author names which modules and why the guard cannot see them."),
    "further-subprocess": (
        "Weakest of the four. The receipt asserts a child interpreter is invisible but does not say "
        "which children this run actually spawned, so the extent is undescribed though the mechanism "
        "is right."),
    "shell-route": (
        "Honest: the receipt says nothing measured here speaks to the shell route at all, which is "
        "the correct thing to say rather than a claim of coverage."),
}

RISK = ("I checked for both known defeats. The prose is not keyword-stuffing: each spot carries a "
        "reason and a scope, not a bare concept name. It is not a paste: I read F-8(a) 1.6 beside it "
        "and the sentences differ in structure, not merely in interleaved filler.")


def valid_attestation():
    return {
        "schema": A.SCHEMA,
        "verdict": "PASS",
        "receipt_sha256": RECEIPT_SHA,
        "linter_report_sha256": REPORT_SHA,
        "receipt_author": {"role": "claude-school-main",
                           "conversation_uuid": "0a6252ff-192d-41ee-ab49-c749f55c97f9"},
        "independent_reviewer": {"role": "agy-g2-gate-verifier",
                                 "conversation_uuid": "dc93a0f8-6863-48c8-9b7b-76f22f6deae2"},
        "independence_basis": (
            "Different role and different conversation from the receipt's author; I did not write "
            "the receipt, the linter, or this validator, and I read the prose before reading the "
            "author's own disposition of it."),
        "per_spot_findings": copy.deepcopy(FINDINGS),
        "copying_and_word_salad_risk": RISK,
    }


class Fixture(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        d = pathlib.Path(self._d.name)
        self.receipt = d / "receipt.md"
        self.report = d / "report.json"
        self.att = d / "attestation.json"
        self.receipt.write_bytes(RECEIPT_BYTES)
        self.report.write_bytes(REPORT_BYTES)
        self.addCleanup(self._d.cleanup)

    def run_cli(self, att_obj):
        self.att.write_text(json.dumps(att_obj), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = A.main(["--attestation", str(self.att), "--receipt", str(self.receipt),
                         "--linter-report", str(self.report)])
        return rc, out.getvalue() + err.getvalue()

    def assertRejected(self, att_obj, needle):
        rc, text = self.run_cli(att_obj)
        self.assertEqual(rc, A.REJECTED_EXIT, text)
        self.assertIn(needle, text)


class AValidAttestationIsWELLFORMEDNeverPASSED(Fixture):
    """The paired silent-on-good arm. Without it every removal arm below is satisfied by `return 3`."""

    def test_a_complete_digest_bound_independent_attestation_is_WELL_FORMED(self):
        rc, text = self.run_cli(valid_attestation())
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)
        self.assertIn("ATTESTATION_WELL_FORMED", text)
        self.assertIn("NOT A DISCHARGE OF F-8(b)", text)

    def test_the_well_formed_result_disclaims_BOTH_correctness_and_authorship(self):
        rc, text = self.run_cli(valid_attestation())
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)
        self.assertIn("DOES NOT PROVE THE JUDGEMENT IS CORRECT", text)
        self.assertIn("DOES NOT PROVE THE NAMED REVIEWER WROTE IT", text)
        self.assertIn("RECORDED AUTHORITY DECISION", text)

    def test_the_well_formed_status_is_reached_through_validate_not_only_the_cli(self):
        rc, notes = A.validate(valid_attestation(), RECEIPT_SHA, REPORT_SHA)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, notes)


class ThisCheckerHasNoGreenEITHER(Fixture):
    """Two independent reviews ruled a green exit beside a printed caveat a fail-open gate.

    The linter already had no zero. This one now has none either, so NOTHING in the F-8(b) toolchain
    returns 0 and there is no exit code anywhere a future lane can cite as "F-8(b) discharged".
    """

    def test_no_exit_constant_in_the_module_is_zero(self):
        names = [n for n in dir(A) if n.endswith("_EXIT")]
        self.assertGreaterEqual(len(names), 3, names)
        for n in names:
            self.assertNotEqual(getattr(A, n), 0,
                                "%s is 0; this checker must have no passing status" % n)

    def test_no_attestation_whatsoever_can_produce_exit_zero(self):
        cases = [("valid", valid_attestation())]
        for field in ("receipt_sha256", "linter_report_sha256", "receipt_author",
                      "independent_reviewer", "independence_basis", "per_spot_findings",
                      "copying_and_word_salad_risk", "verdict"):
            att = valid_attestation()
            del att[field]
            cases.append(("no " + field, att))
        att = valid_attestation(); att["schema"] = "wrong"; cases.append(("bad schema", att))
        att = valid_attestation(); att["superseded_by"] = "later.json"; cases.append(("superseded", att))
        seen = set()
        for label, att in cases:
            rc, text = self.run_cli(att)
            self.assertNotEqual(rc, 0, "%s produced exit 0: %s" % (label, text))
            seen.add(rc)
        self.assertIn(A.WELL_FORMED_EXIT, seen, "no arm reached WELL_FORMED; suite is blind")
        self.assertIn(A.REJECTED_EXIT, seen)

    def test_the_word_PASS_is_not_used_for_this_checkers_own_result(self):
        """The verdict FIELD is still `PASS` -- that is the reviewer's word. The TOOL's is not."""
        rc, text = self.run_cli(valid_attestation())
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)
        self.assertNotIn("[f8b-att] PASS", text)


class TheDigestBindingsAreReal(Fixture):
    def test_a_missing_receipt_digest_is_rejected(self):
        att = valid_attestation()
        del att["receipt_sha256"]
        self.assertRejected(att, "not bound to the receipt")

    def test_a_missing_linter_report_digest_is_rejected(self):
        att = valid_attestation()
        del att["linter_report_sha256"]
        self.assertRejected(att, "not bound to the linter report")

    def test_a_MISMATCHED_receipt_digest_is_rejected(self):
        att = valid_attestation()
        att["receipt_sha256"] = "0" * 64
        self.assertRejected(att, "receipt_sha256 MISMATCH")

    def test_a_MISMATCHED_linter_report_digest_is_rejected(self):
        att = valid_attestation()
        att["linter_report_sha256"] = "0" * 64
        self.assertRejected(att, "linter_report_sha256 MISMATCH")

    def test_a_binding_that_never_moves_binds_nothing(self):
        """Opposite direction: editing the RECEIPT under a previously-valid attestation must fail.

        This is the stale/superseded case that matters in practice -- nobody marks an attestation
        superseded, they just change the receipt underneath it.
        """
        att = valid_attestation()
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)
        self.receipt.write_bytes(RECEIPT_BYTES + b"\na later edit nobody attested to\n")
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.REJECTED_EXIT, text)
        self.assertIn("receipt_sha256 MISMATCH", text)

    def test_editing_the_linter_report_underneath_also_invalidates(self):
        att = valid_attestation()
        self.report.write_bytes(REPORT_BYTES + b"\n")
        self.assertRejected(att, "linter_report_sha256 MISMATCH")


class IdentityAndIndependence(Fixture):
    def test_a_missing_author_is_rejected(self):
        att = valid_attestation()
        del att["receipt_author"]
        self.assertRejected(att, "receipt_author is missing")

    def test_a_missing_reviewer_is_rejected(self):
        att = valid_attestation()
        del att["independent_reviewer"]
        self.assertRejected(att, "independent_reviewer is missing")

    def test_a_reviewer_with_no_role_is_rejected(self):
        att = valid_attestation()
        att["independent_reviewer"]["role"] = ""
        self.assertRejected(att, "independent_reviewer.role is missing")

    def test_a_reviewer_with_no_conversation_uuid_is_rejected(self):
        att = valid_attestation()
        del att["independent_reviewer"]["conversation_uuid"]
        self.assertRejected(att, "independent_reviewer.conversation_uuid is missing")

    def test_self_attestation_on_ROLE_is_rejected(self):
        att = valid_attestation()
        att["independent_reviewer"]["role"] = att["receipt_author"]["role"]
        self.assertRejected(att, "SELF-ATTESTATION on role")

    def test_self_attestation_on_CONVERSATION_UUID_is_rejected_even_under_a_new_role(self):
        """A lane can rename itself. The uuid arm is why that does not launder independence."""
        att = valid_attestation()
        att["independent_reviewer"]["conversation_uuid"] = \
            att["receipt_author"]["conversation_uuid"]
        self.assertRejected(att, "SELF-ATTESTATION on conversation_uuid")

    def test_an_absent_independence_basis_is_rejected(self):
        att = valid_attestation()
        del att["independence_basis"]
        self.assertRejected(att, "independence_basis is absent")

    def test_a_one_word_independence_basis_is_rejected(self):
        att = valid_attestation()
        att["independence_basis"] = "independent"
        self.assertRejected(att, "independence_basis is absent or too thin")


class ThePerSpotFindingsMustBeComplete(Fixture):
    def test_every_one_of_the_four_spots_missing_in_turn_is_rejected_and_NAMED(self):
        for spot in A.REQUIRED_SPOTS:
            att = valid_attestation()
            del att["per_spot_findings"][spot]
            self.assertRejected(att, "per_spot_findings[%s] is missing" % spot)

    def test_an_empty_finding_is_rejected(self):
        att = valid_attestation()
        att["per_spot_findings"]["shell-route"] = "   "
        self.assertRejected(att, "per_spot_findings[shell-route] is missing")

    def test_a_checkbox_finding_is_rejected(self):
        att = valid_attestation()
        att["per_spot_findings"]["shell-route"] = "fine"
        self.assertRejected(att, "that is a checkbox, not a finding")

    def test_ONE_finding_pasted_across_spots_is_word_salad_and_is_rejected(self):
        att = valid_attestation()
        att["per_spot_findings"]["shell-route"] = FINDINGS["namespace-packages"]
        self.assertRejected(att, "is word-salad, not four judgements")

    def test_a_duplicate_differing_only_in_whitespace_and_case_is_still_caught(self):
        att = valid_attestation()
        att["per_spot_findings"]["shell-route"] = \
            "  " + FINDINGS["namespace-packages"].upper().replace(" ", "  ") + "\n"
        self.assertRejected(att, "is word-salad, not four judgements")

    def test_an_unknown_spot_key_is_rejected(self):
        att = valid_attestation()
        att["per_spot_findings"]["invented-fifth-spot"] = FINDINGS["shell-route"] + " extra"
        self.assertRejected(att, "unknown spot key")

    def test_findings_not_an_object_is_rejected(self):
        att = valid_attestation()
        att["per_spot_findings"] = "all four are fine"
        self.assertRejected(att, "per_spot_findings is missing or not an object")


class TheCopyingRiskMustBeAddressed(Fixture):
    def test_an_absent_copying_risk_statement_is_rejected(self):
        att = valid_attestation()
        del att["copying_and_word_salad_risk"]
        self.assertRejected(att, "copying_and_word_salad_risk is absent")

    def test_a_token_copying_risk_statement_is_rejected(self):
        att = valid_attestation()
        att["copying_and_word_salad_risk"] = "not a paste"
        self.assertRejected(att, "copying_and_word_salad_risk is absent or too thin")


class TheVerdictMustBeAnUnambiguousPass(Fixture):
    def test_a_FAIL_verdict_is_rejected(self):
        att = valid_attestation()
        att["verdict"] = "FAIL"
        self.assertRejected(att, "the reviewer did not pass this receipt")

    def test_a_CANNOT_CHECK_verdict_is_rejected(self):
        att = valid_attestation()
        att["verdict"] = "CANNOT CHECK"
        self.assertRejected(att, "verdict is CANNOT CHECK: never a pass")

    def test_a_missing_verdict_is_rejected(self):
        att = valid_attestation()
        del att["verdict"]
        self.assertRejected(att, "not an unambiguous PASS")

    def test_a_HEDGED_verdict_is_rejected(self):
        att = valid_attestation()
        att["verdict"] = "PASS WITH RESERVATIONS"
        self.assertRejected(att, "not an unambiguous PASS")

    def test_a_lowercase_pass_is_accepted_because_only_AMBIGUITY_is_the_defect(self):
        att = valid_attestation()
        att["verdict"] = "pass"
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)


class StaleAndSupersededAttestations(Fixture):
    def test_a_SUPERSEDED_attestation_never_passes(self):
        att = valid_attestation()
        att["superseded_by"] = "ATTESTATION-20260827-second-pass.json"
        self.assertRejected(att, "is SUPERSEDED by")

    def test_a_DRAFT_attestation_is_not_a_filed_decision(self):
        att = valid_attestation()
        att["status"] = "draft"
        self.assertRejected(att, "the only value that means a filed decision")

    def test_a_WITHDRAWN_attestation_is_rejected(self):
        att = valid_attestation()
        att["status"] = "WITHDRAWN"
        self.assertRejected(att, "the only value that means a filed decision")

    def test_a_wrong_schema_is_rejected_before_anything_else(self):
        att = valid_attestation()
        att["schema"] = "f8b-independent-prose-attestation/2"
        self.assertRejected(att, "schema is")


class TheValidatorCannotPassWhenItCannotLook(Fixture):
    def test_unparseable_attestation_json_is_CANNOT_CHECK(self):
        self.att.write_text("{ this is not json", encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            rc = A.main(["--attestation", str(self.att), "--receipt", str(self.receipt),
                         "--linter-report", str(self.report)])
        self.assertEqual(rc, A.CANNOT_CHECK_EXIT)
        self.assertIn("CANNOT CHECK", out.getvalue())

    def test_an_absent_attestation_file_is_CANNOT_CHECK(self):
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            rc = A.main(["--attestation", str(self.att.parent / "nope.json"),
                         "--receipt", str(self.receipt), "--linter-report", str(self.report)])
        self.assertEqual(rc, A.CANNOT_CHECK_EXIT)

    def test_an_absent_receipt_is_CANNOT_CHECK_not_a_pass(self):
        self.att.write_text(json.dumps(valid_attestation()), encoding="utf-8")
        self.receipt.unlink()
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            rc = A.main(["--attestation", str(self.att), "--receipt", str(self.receipt),
                         "--linter-report", str(self.report)])
        self.assertEqual(rc, A.CANNOT_CHECK_EXIT)

    def test_an_absent_linter_report_is_CANNOT_CHECK_not_a_pass(self):
        self.att.write_text(json.dumps(valid_attestation()), encoding="utf-8")
        self.report.unlink()
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            rc = A.main(["--attestation", str(self.att), "--receipt", str(self.receipt),
                         "--linter-report", str(self.report)])
        self.assertEqual(rc, A.CANNOT_CHECK_EXIT)


class TheAdversarialInputsFoundByTheIMPLEMENTATIONGRADE(Fixture):
    """The three fail-open surfaces `agy-f8b-impl-grade` (d71dbff7) found, with its exact inputs.

    Its grade was UNFIT and it was right on all three. Two are closed below. The third -- that
    nothing binds the file to the party it names -- is not closeable by this program and is
    asserted here as a DISCLOSURE arm instead, so that removing the disclosure fails the suite.
    """

    def test_a_hedge_smuggled_in_an_UNKNOWN_field_beside_a_clean_verdict_is_rejected(self):
        att = valid_attestation()
        att["verdict_hedging"] = "PASS but with some reservations"
        self.assertRejected(att, "unknown top-level field(s)")

    def test_any_unknown_top_level_field_is_rejected_not_ignored(self):
        att = valid_attestation()
        att["EXTRA_FIELD"] = "I am an extra field"
        self.assertRejected(att, "unknown top-level field(s)")

    def test_an_unknown_field_inside_a_PARTY_is_rejected_too(self):
        att = valid_attestation()
        att["independent_reviewer"]["note"] = "I did not really read it"
        self.assertRejected(att, "unknown field(s)")

    def test_a_reviewer_uuid_that_is_a_PREFIX_of_the_authors_is_rejected(self):
        """`uuid-1234` vs `uuid-123` are distinct strings and not two conversations."""
        att = valid_attestation()
        att["receipt_author"]["conversation_uuid"] = "uuid-1234"
        att["independent_reviewer"]["conversation_uuid"] = "uuid-123"
        self.assertRejected(att, "is not a canonical uuid")

    def test_a_non_uuid_conversation_id_is_rejected_even_when_both_parties_agree_on_the_style(self):
        att = valid_attestation()
        for party in ("receipt_author", "independent_reviewer"):
            att[party]["conversation_uuid"] = "session-" + party
        self.assertRejected(att, "is not a canonical uuid")

    def test_a_real_uuid_pair_still_passes_so_the_form_check_is_not_a_blanket_refusal(self):
        rc, text = self.run_cli(valid_attestation())
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)

    def test_findings_differing_only_by_a_TRAILING_DIGIT_are_still_one_finding(self):
        """The grade's exact break: the same 80-char run with a trailing 1 and a trailing 2."""
        att = valid_attestation()
        body = "B" * 80
        att["per_spot_findings"]["namespace-packages"] = body + "1"
        att["per_spot_findings"]["shell-route"] = body + "2"
        self.assertRejected(att, "once digits, punctuation")

    def test_findings_differing_only_by_PUNCTUATION_are_still_one_finding(self):
        att = valid_attestation()
        att["per_spot_findings"]["shell-route"] = (
            FINDINGS["namespace-packages"].replace(",", ";").replace(".", "!").upper() + "   ...!!!")
        self.assertRejected(att, "once digits, punctuation")

    def test_four_genuinely_different_findings_are_NOT_caught_by_the_skeleton(self):
        """Control. Without this the arms above are satisfied by rejecting every attestation."""
        rc, notes = A.validate(valid_attestation(), RECEIPT_SHA, REPORT_SHA)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, notes)

    def test_the_UNCLOSEABLE_hole_is_disclosed_on_the_pass_path_and_in_the_docstring(self):
        """A hole that cannot be closed must at least be impossible to miss."""
        rc, text = self.run_cli(valid_attestation())
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)
        self.assertIn("DOES NOT PROVE THE NAMED REVIEWER WROTE IT", text)
        self.assertIn("no signature", text.lower())
        doc = A.__doc__ or ""
        self.assertIn("OPEN, AND NOT CLOSEABLE HERE", doc)
        self.assertIn("process guarantees", doc.lower())


class TheSecondRoundOfAdversarialInputs(Fixture):
    """Round two from `agy-f8b-impl-grade`. Four were closeable; two are the disclosed residuals.

    The two that remain OPEN have arms here that assert they PASS. That is deliberate: an
    undisclosed hole and a disclosed one are different objects, and a test that pins the disclosed
    behaviour is what stops it from being quietly re-described later as closed.
    """

    def test_a_role_ALIAS_differing_only_in_punctuation_is_self_attestation(self):
        att = valid_attestation()
        att["receipt_author"]["role"] = "close-out lane"
        att["independent_reviewer"]["role"] = "close out lane"
        self.assertRejected(att, "SELF-ATTESTATION on role")

    def test_roles_differing_only_by_a_DIGIT_are_two_parties_not_one(self):
        """The other direction of the alias fix, and it caught a real false positive.

        Comparing roles on the findings' letters-only form collided `codex-school` with
        `codex-school2` -- two actual profiles in this repo -- and `agy-g2-` with `agy-g3-`. Failing
        closed is the safe direction but it is still wrong, so role identity keeps digits.
        """
        for author, reviewer in (("codex-school", "codex-school2"),
                                 ("agy-g2-gate-verifier", "agy-g3-gate-verifier"),
                                 ("agy-lane-1", "agy-lane-2")):
            att = valid_attestation()
            att["receipt_author"]["role"] = author
            att["independent_reviewer"]["role"] = reviewer
            rc, text = self.run_cli(att)
            self.assertEqual(rc, A.WELL_FORMED_EXIT,
                             "%r and %r are two roles, not one: %s" % (author, reviewer, text))

    def test_a_HOMOGLYPH_in_an_identity_field_is_rejected(self):
        att = valid_attestation()
        att["receipt_author"]["role"] = "\u0430uthor"   # Cyrillic a
        att["independent_reviewer"]["role"] = "author"
        self.assertRejected(att, "contains non-ASCII")

    def test_an_UNLISTED_status_is_rejected_because_the_check_is_an_allowlist(self):
        for value in ("pending", "in review", "provisional", "draft", ""):
            att = valid_attestation()
            att["status"] = value
            self.assertRejected(att, "the only value that means a filed decision")

    def test_the_one_FILED_status_is_accepted(self):
        att = valid_attestation()
        att["status"] = "filed"
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)

    def test_a_FALSY_superseded_by_is_rejected_as_ambiguous_not_read_as_absent(self):
        for value in (False, "", None, 0):
            att = valid_attestation()
            att["superseded_by"] = value
            self.assertRejected(att, "ambiguous rather than absent")

    def test_omitting_superseded_by_entirely_is_the_way_to_say_not_superseded(self):
        att = valid_attestation()
        self.assertNotIn("superseded_by", att)
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)

    def test_DISCLOSED_AND_OPEN_two_fabricated_uuids_still_pass(self):
        """No signature exists, so form is all this program can check. Pinned, not fixed."""
        att = valid_attestation()
        att["receipt_author"]["conversation_uuid"] = "00000000-0000-0000-0000-000000000001"
        att["independent_reviewer"]["conversation_uuid"] = "00000000-0000-0000-0000-000000000002"
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)
        self.assertIn("DOES NOT PROVE THE NAMED REVIEWER WROTE IT", text)

    def test_DISCLOSED_AND_OPEN_findings_differing_by_one_WORD_still_pass(self):
        """Closing this needs a similarity threshold on prose, which was explicitly ruled out."""
        att = valid_attestation()
        body = FINDINGS["namespace-packages"]
        att["per_spot_findings"]["namespace-packages"] = body + " potato"
        att["per_spot_findings"]["shell-route"] = body + " tomato"
        rc, text = self.run_cli(att)
        self.assertEqual(rc, A.WELL_FORMED_EXIT, text)


class EveryRequirementHasARemovalArm(unittest.TestCase):
    """A meta-arm: a top-level field with no removal arm is an unenforced requirement.

    This is the arm that catches the next requirement someone adds to the schema without adding a
    test that removing it fails. It reads the suite's own source, so it cannot drift from it.
    """

    def test_each_required_top_level_field_is_removed_by_some_arm(self):
        src = pathlib.Path(__file__).read_text(encoding="utf-8")
        for field in ("receipt_sha256", "linter_report_sha256", "receipt_author",
                      "independent_reviewer", "independence_basis", "per_spot_findings",
                      "copying_and_word_salad_risk", "verdict"):
            self.assertIn('del att["%s"]' % field, src,
                          "no arm removes %s; the requirement is unenforced" % field)


if __name__ == "__main__":
    unittest.main(verbosity=2)

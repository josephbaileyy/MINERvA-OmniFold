"""Tests for the deck generator.

The deck is the deliverable, so the failure that matters is a deck that renders
and says something false. The headline branches are tested one by one because
"his arm scored better and we kept ours" must never come out reading as a win.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import make_final_deck as mfd

HERE = Path(__file__).resolve().parent
HAVE_PDFLATEX = shutil.which("pdflatex") is not None


def _report(**over):
    base = {
        "verdict": "OURS_NON_INFERIOR", "recommendation": "ADOPT_OURS",
        "thresholds": {"non_inferiority_delta": 0.02, "switching_delta": 0.04,
                       "adequacy_fraction_of_reference": 0.80,
                       "regional_fraction_of_regional_reference": 0.60},
        "interval": {"mean": 0.019, "ci_low": 0.016, "ci_high": 0.022,
                     "n_pairs": 8, "sd": 0.004, "half_width": 0.003},
        "paired_differences": {"127": 0.019, "139": 0.020},
        "absolute_adequacy": {"reference": 0.95, "floor": 0.76, "arms": {
            "ours": {"mean_recovery": 0.90, "adequate": True},
            "theirs": {"mean_recovery": 0.88, "adequate": True}}},
        "mean_recovery_by_region": {"ours": {"good": 0.9}, "theirs": {"good": 0.88}},
        "regional_safeguard": {"scoreable_regions": ["good"],
                               "floor_by_region": {"good": 0.58},
                               "arms": {"ours": {"eligible": True},
                                        "theirs": {"eligible": True}}},
        "regional_coverage": {"off_grid_truth_fraction": 0.012},
        "low_acceptance": {"truth_mass_fraction": 0.31,
                           "injected_displacement_share": 0.266,
                           "mean_recovery_by_arm": {"ours": 0.5, "theirs": 0.48},
                           "reading": "These events are retained and reported"},
        "scope": {"step1_reco": "the arms DIFFER", "step2_gen": "IDENTICAL",
                  "what_it_cannot_speak_to": "his truth side"},
        "pilot_exclusion_reason": "the pilot chooses n",
        "retained_ours_though_theirs_scored_better": False,
        "provenance": {"commit": "abc123def456", "campaign_dir": "/x/y",
                       "closure_npz": {"sha256": "deadbeef" * 8},
                       "truth_rows_scored": 1234, "aggregate_reference": 0.95},
    }
    base.update(over)
    return base


class TestComponentComparison(unittest.TestCase):
    def test_exactly_twelve_categories_are_found(self):
        rows = mfd.component_comparison()
        self.assertEqual(len(rows), mfd.EXPECTED_CATEGORIES)
        self.assertEqual([r["number"] for r in rows],
                         [str(i) for i in range(1, 13)])
        for row in rows:
            self.assertTrue(row["recommendation"])

    def test_a_partial_document_is_refused(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "partial.md"
            path.write_text(
                "## 1. One\n| **recommendation** | keep |\n"
                "## 2. Two\n| **recommendation** | keep |\n")
            with self.assertRaisesRegex(ValueError, "expected 12"):
                mfd.component_comparison(path)

    def test_a_category_without_a_recommendation_is_refused(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "gap.md"
            body = "".join(f"## {i}. Cat{i}\n| **recommendation** | keep |\n"
                           for i in range(1, 12))
            path.write_text(body + "## 12. Cat12\n| **evidence** | none |\n")
            with self.assertRaisesRegex(ValueError, "no recommendation row"):
                mfd.component_comparison(path)


class TestEscaping(unittest.TestCase):
    def test_nested_emphasis_inside_bold_is_resolved(self):
        out = mfd.tex_escape("**Borrow the *whole* event.**")
        self.assertEqual(out, r"\textbf{Borrow the \emph{whole} event.}")
        self.assertNotIn("*", out)

    def test_code_spans_protect_their_contents(self):
        self.assertEqual(mfd.tex_escape("`a_b **c**`"), r"\texttt{a\_b **c**}")

    def test_specials_are_escaped(self):
        self.assertEqual(mfd.tex_escape("a_b & c% d#"),
                         r"a\_b \& c\% d\#")

    def test_an_unmapped_character_raises_rather_than_reaching_pdflatex(self):
        with self.assertRaisesRegex(ValueError, "unmapped non-ASCII"):
            mfd.tex_escape("☃")

    def test_every_character_in_the_pinned_document_converts_to_ascii(self):
        for row in mfd.component_comparison():
            for field in ("title", "recommendation"):
                out = mfd.tex_escape(row[field])
                self.assertTrue(out.isascii(), msg=f"{row['number']} {field}")
                self.assertNotIn("\\\\text", out)


class TestHeadline(unittest.TestCase):
    def test_no_adequate_arm_says_so_and_recommends_neither(self):
        head, body = mfd._headline(_report(recommendation="NO_SELECTION",
                                           verdict="NEITHER_ELIGIBLE"))
        self.assertIn("No adequate arm", head)
        self.assertIn("recommends neither", body)

    def test_retained_though_behind_never_reads_as_a_win(self):
        head, body = mfd._headline(_report(
            retained_ours_though_theirs_scored_better=True,
            verdict="THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD"))
        self.assertIn("though his arm scored better", head)
        self.assertIn("Non-inferiority is not superiority", body)

    def test_inconclusive_states_the_margin_was_not_widened(self):
        head, body = mfd._headline(_report(verdict="INCONCLUSIVE",
                                           recommendation="ADOPT_OURS"))
        self.assertIn("Inconclusive", head)
        self.assertIn("not widened", body)

    def test_adopting_theirs_names_their_configuration(self):
        head, _ = mfd._headline(_report(recommendation="ADOPT_THEIRS",
                                        verdict="THEIRS_SUPERIOR"))
        self.assertIn("Gregor", head)


class TestBuild(unittest.TestCase):
    def test_the_generated_source_is_ascii_and_carries_the_scope_limit(self):
        tex = mfd.build_tex(_report(), mfd.component_comparison())
        self.assertTrue(tex.isascii())
        self.assertIn("diagnostic method development", tex)
        self.assertIn("his truth side", tex)
        self.assertIn("declared, not", tex)
        self.assertIn("excluded", tex)

    def test_the_claim_index_points_at_artifacts_not_assertions(self):
        index = mfd.claim_index(_report())
        self.assertIn("campaign_report.json", index)
        self.assertIn("test_score_campaign.py", index)
        self.assertIn("abc123def456", index)

    @unittest.skipUnless(HAVE_PDFLATEX, "pdflatex not installed")
    def test_the_deck_actually_renders(self):
        with TemporaryDirectory() as tmp:
            report = Path(tmp) / "r.json"
            report.write_text(json.dumps(_report()))
            done = subprocess.run(
                ["python3", str(HERE / "make_final_deck.py"),
                 "--report", str(report), "--outdir", str(Path(tmp) / "slides"),
                 "--stem", "check"],
                cwd=HERE, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, msg=done.stderr[-3000:])
            pdf = Path(tmp) / "slides" / "check.pdf"
            self.assertTrue(pdf.exists())
            self.assertGreater(pdf.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()


class ThePrecisionAgainstDeltaIsStated(unittest.TestCase):
    """The pilot said 74 pairs for a half-width within delta; the design runs 8.

    A reader should not have to divide two numbers on the slide to learn that
    the comparison resolves direction but not non-inferiority at the margin.
    """

    def test_a_wide_interval_says_so_in_bold(self):
        report = _report(interval={"mean": -0.19, "ci_low": -0.232,
                                   "ci_high": -0.148, "n_pairs": 8,
                                   "sd": 0.05, "half_width": 0.042})
        tex = mfd.build_tex(report, mfd.component_comparison())
        self.assertIn("wider than", tex)
        self.assertIn("resolves the", tex)
        self.assertIn("not non-inferiority", tex)

    def test_a_narrow_interval_says_the_margin_is_resolvable(self):
        report = _report(interval={"mean": -0.005, "ci_low": -0.015,
                                   "ci_high": 0.005, "n_pairs": 8,
                                   "sd": 0.01, "half_width": 0.010})
        tex = mfd.build_tex(report, mfd.component_comparison())
        self.assertIn("narrower than", tex)

    def test_it_never_claims_the_margin_was_widened(self):
        report = _report(interval={"mean": -0.19, "ci_low": -0.232,
                                   "ci_high": -0.148, "n_pairs": 8,
                                   "sd": 0.05, "half_width": 0.042})
        tex = mfd.build_tex(report, mfd.component_comparison())
        self.assertIn("not widened", tex)

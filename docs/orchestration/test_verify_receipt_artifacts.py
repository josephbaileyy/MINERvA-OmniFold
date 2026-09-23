#!/usr/bin/env python3
"""Arms for `verify_receipt_artifacts.py`, each in the direction the guard acts.

WHY THIS FILE EXISTS. The instrument shipped with a self-test and a historical-cases arm but no
suite, and it went FAIL-OPEN when the canonical checkout moved on 2026-08-25: `REPO_PREFIXES` was a
one-element tuple naming the old checkout, so an absolute path under the new one was never
normalised, never matched `AREA`, and was silently not checked. Nothing failed. The defect was found
by reading the constant, not by anything going red -- which is the signature of a missing arm.

WHAT AN ARM MEANS HERE. Every requirement gets one arm that FIRES on bad input and one that stays
SILENT on good input, plus the opposite-direction arm where that is meaningful. An arm that only
ever passes is not evidence: `test_negative_control_*` restores the pre-repair behaviour and asserts
the firing arms GO RED, so this suite can be shown to be capable of failing.

Run: python3 -m unittest discover -s docs/orchestration -p 'test_verify_receipt_artifacts.py'
"""
import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def _load():
    spec = importlib.util.spec_from_file_location(
        "vra_under_test", os.path.join(HERE, "verify_receipt_artifacts.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _load()

OLD_CHECKOUT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/"
AREA = "docs/orchestration/state/"
LEAF = "PROBE_OBJECT.npz"
REL = AREA + LEAF


def receipt(*paths):
    """A receipt naming these artifact paths, in the shape a real one uses."""
    return json.dumps({"artifacts": [{"path": p} for p in paths]})


class Normalisation(unittest.TestCase):
    """The prefix set is DERIVED, and the derivation is what the repair is."""

    def test_current_checkout_normalises(self):
        """FIRES on the defect: an absolute path under the CURRENT checkout must go repo-relative.

        This is the arm the shipped instrument failed. It is written against `repo_root()` rather
        than a literal, so it keeps testing the live checkout after the next redesignation instead
        of pinning today's answer.
        """
        absolute = os.path.join(V.repo_root(), REL)
        self.assertEqual(V.normalise(absolute), REL)

    def test_historical_checkout_still_normalises(self):
        """REGRESSION: receipts already committed name the old checkout. Repairing the new path
        must not stop checking the old one."""
        self.assertEqual(V.normalise(OLD_CHECKOUT + REL), REL)

    def test_unlisted_checkout_normalises_via_marker(self):
        """A checkout nobody enumerated -- a worktree, a fresh clone, the next move -- still
        normalises. The point of the repair is to stop maintaining a list that rots silently."""
        self.assertEqual(V.normalise("/some/unlisted/clone/" + REL), REL)

    def test_relative_path_is_untouched(self):
        """SILENT on good input: an already-relative path is returned unchanged."""
        self.assertEqual(V.normalise(REL), REL)

    def test_absolute_path_outside_the_area_is_untouched(self):
        """OPPOSITE DIRECTION. The marker fallback must not drag in paths that are not in the
        deliverable area. A cluster product stays absolute, so `named_artifacts` drops it -- which
        is the behaviour the instrument's docstring justifies at length (349 of 351 named paths are
        cluster products that are not supposed to be in git)."""
        product = "/pscratch/sd/j/josephrb/k0r2/runs/somewhere/unified_throw_cov_5d.root"
        self.assertEqual(V.normalise(product), product)
        self.assertTrue(V.normalise(product).startswith("/"))

    def test_marker_does_not_match_a_lookalike_directory(self):
        """OPPOSITE DIRECTION. `.../not-docs/orchestration/state/` is a different directory and the
        marker must not treat it as the deliverable area."""
        look = "/x/not-docs/orchestration/state/" + LEAF
        self.assertTrue(V.normalise(look).startswith("/"),
                        "a lookalike directory was normalised into the checked area")

    def test_longest_prefix_wins(self):
        """Prefixes are sorted longest-first, so a nested checkout is not stripped by a shorter
        prefix that also matches."""
        prefixes = V.repo_prefixes()
        self.assertEqual(list(prefixes), sorted(prefixes, key=len, reverse=True))


class Extraction(unittest.TestCase):
    """`named_artifacts` is where normalisation has its effect."""

    def test_current_checkout_path_is_extracted(self):
        """FIRES: the whole point. Before the repair this returned an empty set."""
        absolute = os.path.join(V.repo_root(), REL)
        self.assertIn(REL, V.named_artifacts(receipt(absolute)))

    def test_historical_checkout_path_is_extracted(self):
        self.assertIn(REL, V.named_artifacts(receipt(OLD_CHECKOUT + REL)))

    def test_cluster_product_is_not_extracted(self):
        """SILENT on good input: the deliverable-area scoping is preserved."""
        product = "/pscratch/sd/j/josephrb/k0r2/runs/x/unified_throw_cov_5d.root"
        self.assertEqual(V.named_artifacts(receipt(product)), set())

    def test_non_artifact_extension_is_not_extracted(self):
        """SILENT: a .md path in the area is not a deliverable artifact."""
        self.assertEqual(V.named_artifacts(receipt(AREA + "notes.md")), set())


class SelfTestAndHistory(unittest.TestCase):
    """The instrument's own controls must survive the repair."""

    def test_self_test_control_still_fires(self):
        self.assertTrue(V.self_test(REPO)["control_fires"])

    def test_scan_of_the_real_corpus_is_clean(self):
        """The repair must not invent findings on the committed corpus. Measured before the change:
        0 missing. If this goes red, the marker fallback is over-broad."""
        findings, n_receipts, _ = V.scan(root=REPO)
        self.assertGreater(n_receipts, 0, "no receipts scanned -- the fixture, not the corpus")
        self.assertEqual(findings, [], "repair introduced false positives on the real corpus")


class NegativeControl(unittest.TestCase):
    """Prove this suite can fail. Restore the pre-repair behaviour; the firing arms must go RED."""

    def test_negative_control_prerepair_normalise_breaks_the_firing_arms(self):
        saved_hist = V.HISTORICAL_REPO_PREFIXES
        saved_norm = V.normalise
        saved_cache = dict(V._PREFIX_CACHE)
        try:
            def prerepair(p, root=None):
                for pref in (OLD_CHECKOUT,):
                    if p.startswith(pref):
                        return p[len(pref):]
                return p
            V.normalise = prerepair
            absolute = os.path.join(V.repo_root(), REL)

            self.assertNotEqual(prerepair(absolute), REL,
                                "pre-repair normalise already handled the current checkout -- "
                                "then there was no defect and this whole repair is unmotivated")
            self.assertEqual(V.named_artifacts(receipt(absolute)), set(),
                             "pre-repair extraction should MISS the current-checkout path")
            self.assertEqual(prerepair(OLD_CHECKOUT + REL), REL,
                             "pre-repair did handle the historical prefix")
        finally:
            V.normalise = saved_norm
            V.HISTORICAL_REPO_PREFIXES = saved_hist
            V._PREFIX_CACHE.clear()
            V._PREFIX_CACHE.update(saved_cache)

    def test_suite_is_restored_after_the_negative_control(self):
        """The control mutates module state; if teardown leaked, this arm catches it rather than
        letting a later run report a phantom pass."""
        absolute = os.path.join(V.repo_root(), REL)
        self.assertEqual(V.normalise(absolute), REL)



class BareCitationsAndLogEvidence(unittest.TestCase):
    """KNOWN_ISSUES 48: .out/.err/.log evidence and bare-filename citations must be RESOLVED, and a
    citation that cannot be resolved gets its own non-green state, never a silent green."""

    RCPT = AREA + "probe-receipt.json"
    COMPANION = AREA + "probe-receipt"

    def _classify(self, name, body, tracked):
        dirs = {os.path.dirname(t) for t in tracked}
        return V.classify_bare(self.RCPT, name, json.dumps(body), set(tracked), dirs)

    def test_log_extensions_are_artifacts(self):
        """FIRES: a deliverable-area .out/.err/.log path is extracted (it was not before)."""
        for ext in (".out", ".err", ".log"):
            self.assertIn(AREA + "x" + ext, V.named_artifacts(receipt(AREA + "x" + ext)))

    def test_bare_citation_found_in_the_companion_dir_is_TRACKED(self):
        """SILENT on good input."""
        state, where = self._classify("centring_n50.out", {"evidence": {"centring_n50.out": {}}},
                                      {self.COMPANION + "/centring_n50.out"})
        self.assertEqual(("TRACKED", self.COMPANION + "/centring_n50.out"), (state, where))

    def test_bare_citation_absent_from_a_tracked_companion_dir_is_MISSING(self):
        """FIRES on the real trap: the evidence dir is tracked (its .py are) but the .out is not."""
        state, _ = self._classify("centring_n50.out", {"evidence": {"centring_n50.out": {}}},
                                  {self.COMPANION + "/centring.py"})
        self.assertEqual("MISSING", state)

    def test_bare_citation_in_a_declared_run_dir_in_the_area_resolves(self):
        body = {"out_dir": AREA + "run-7", "log": "train_1_0.err"}
        self.assertEqual("TRACKED", self._classify("train_1_0.err", body,
                                                   {AREA + "run-7/train_1_0.err"})[0])
        self.assertEqual("MISSING", self._classify("train_1_0.err", body,
                                                   {AREA + "run-7/other.json"})[0])

    def test_bare_citation_under_an_off_repo_run_dir_is_OFF_AREA_not_green_not_missing(self):
        body = {"run_root": "/pscratch/sd/j/josephrb/k0r2/runs/x", "log": "a.out"}
        self.assertEqual("OFF-AREA", self._classify("a.out", body, set())[0])

    def test_bare_citation_also_cited_with_a_path_is_BY_PATH(self):
        body = {"a": "GATE5_REPLICA_WEIGHTS.npz", "b": "/pscratch/x/GATE5_REPLICA_WEIGHTS.npz"}
        self.assertEqual("BY-PATH", self._classify("GATE5_REPLICA_WEIGHTS.npz", body, set())[0])

    def test_an_unlocatable_bare_citation_is_UNRESOLVED(self):
        """FIRES in the new direction: nothing resolves it, and it is not silently dropped."""
        self.assertEqual(("UNRESOLVED", None),
                         self._classify("lost.err", {"x": "lost.err"}, {AREA + "other.json"}))

    def test_the_flat_state_dir_never_makes_a_citation_MISSING(self):
        """OPPOSITE DIRECTION: state/ always holds tracked files, so its being tracked is not
        evidence that a bare name belongs there. Otherwise every cluster log would read MISSING."""
        state, _ = V.classify_bare(AREA + "flat.json", "cluster.log", json.dumps({"x": "cluster.log"}),
                                   {AREA + "flat.json"}, {AREA.rstrip("/")})
        self.assertEqual("UNRESOLVED", state)

    def test_real_corpus_matches_the_pinned_unresolved_inventory(self):
        r = V.scan_full(root=REPO)
        self.assertEqual([], r["findings"])
        self.assertEqual(V.UNRESOLVED_COUNT, len(r["unresolved"]))
        self.assertEqual(V.UNRESOLVED_SHA256, r["unresolved_sha256"])

    def test_the_historical_bare_out_case_now_FIRES(self):
        """e7aea2c9^ is the commit before the nine dropped .out files were recovered."""
        if not V._run(["git", "rev-parse", "--verify", "--quiet", "e7aea2c9^"], REPO).strip():
            self.skipTest("history not available in this clone")
        f, _, _ = V.scan(rev="e7aea2c9^", root=REPO)
        hits = sorted(x["artifact"] for x in f if x["artifact"].startswith(
            AREA + "gate5-cstat-spec-measurements-20260814/") and x["artifact"].endswith(".out"))
        self.assertEqual(9, len(hits), hits)

    def test_exit_codes(self):
        """0 on the pinned set; 3 under --strict; 3 when the pinned set is wrong."""
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, V.main([]))
            self.assertEqual(3, V.main(["--strict"]))
            saved = V.UNRESOLVED_SHA256
            try:
                V.UNRESOLVED_SHA256 = "0" * 64
                self.assertEqual(3, V.main([]))
            finally:
                V.UNRESOLVED_SHA256 = saved

    def test_negative_control_the_old_extension_list_misses_log_evidence(self):
        saved_ext, saved_re = V.EXT, V.PATHLIKE
        try:
            V.EXT = (".npz", ".npy", ".h5", ".hdf5", ".root", ".pkl", ".parquet")
            V.PATHLIKE = V.re.compile(r"[\w./\-]+(?:" + "|".join(V.re.escape(e) for e in V.EXT)
                                      + r")\b")
            self.assertEqual(set(), V.named_artifacts(receipt(AREA + "x.out")))
            self.assertEqual(set(), V.bare_citations(json.dumps({"e": "centring_n50.out"})))
        finally:
            V.EXT, V.PATHLIKE = saved_ext, saved_re
        self.assertEqual({"centring_n50.out"}, V.bare_citations(json.dumps({"e": "centring_n50.out"})))

if __name__ == "__main__":
    unittest.main()

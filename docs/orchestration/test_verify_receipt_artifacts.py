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

    def test_BY_PATH_is_tested_before_MISSING_when_the_full_path_resolves(self):
        """SILENT on good input (2026-11-02): the receipt's own directory is tracked and lacks the
        file, but the same receipt cites it by a cluster path. That is not the trap."""
        body = {"label": "P5 (read as RE-1's k1_p5_rerun.npz)",
                "path": "/pscratch/sd/j/josephrb/gencmp-e2a1-20261102/inputs/re1/out/5d/k1_p5_rerun.npz"}
        self.assertEqual(("BY-PATH", body["path"]),
                         self._classify("k1_p5_rerun.npz", body, {self.COMPANION + "/V.ok"}))

    def test_a_checkout_path_outside_the_area_resolves(self):
        """X's V0 record shape: a staged input named bare and by its cluster-checkout path, which
        normalises to a repo path outside the deliverable area."""
        body = {"inputs": {"of_inputs_5d.npz": "sha"},
                "pinned": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"}
        self.assertEqual("BY-PATH", self._classify("of_inputs_5d.npz", body,
                                                   {self.COMPANION + "/v0.log"})[0])

    def test_a_tracked_relative_path_citation_resolves(self):
        body = {"a": "x.npz", "b": "sub/x.npz"}
        self.assertEqual("BY-PATH", self._classify("x.npz", body,
                                                   {self.COMPANION + "/y.json", AREA + "sub/x.npz"})[0])

    def test_no_full_path_citation_is_still_MISSING(self):
        """FIRES: bare only, in a tracked directory that lacks it."""
        body = {"products": {"xcov_b1_j101.npz": "sha"}}
        self.assertEqual("MISSING", self._classify("xcov_b1_j101.npz", body,
                                                   {self.COMPANION + "/lane_1_13.json"})[0])

    def test_a_full_path_citation_that_does_not_resolve_is_still_MISSING(self):
        """FIRES: a path into the deliverable area that git does not carry is the trap itself, and
        a relative path that matches nothing tracked locates nothing."""
        for other in (AREA + "probe-receipt/x.npz", V.repo_root() + "/" + AREA + "elsewhere/x.npz",
                      "run-3/x.npz"):
            body = {"a": "x.npz", "b": other}
            self.assertEqual("MISSING", self._classify("x.npz", body, {self.COMPANION + "/y.json"})[0],
                             other)

    def test_negative_control_MISSING_first_refuses_the_real_shapes(self):
        """The suite can fail: with the resolving-path test removed, both real shapes go MISSING."""
        saved = V.resolving_path_citation
        try:
            V.resolving_path_citation = lambda *a, **k: None
            body = {"label": "k1_p5_rerun.npz", "path": "/pscratch/x/k1_p5_rerun.npz"}
            self.assertEqual("MISSING", self._classify("k1_p5_rerun.npz", body, {self.COMPANION + "/V.ok"})[0])
        finally:
            V.resolving_path_citation = saved
        self.assertEqual("BY-PATH", self._classify("k1_p5_rerun.npz", body, {self.COMPANION + "/V.ok"})[0])

    def test_a_slurm_filename_pattern_is_not_a_citation(self):
        """SILENT on a pattern: `%x_%j.out` names no file, so no tail of it is a bare citation."""
        for t in ("/pscratch/x/%x_%j.out", "--error=/p/a1/slurm-%j.err", "boot5dG_%a_%A.out", "s-%5j.log"):
            self.assertEqual(set(), V.bare_citations(json.dumps({"o": t})), t)

    def test_a_real_log_beside_a_pattern_is_still_a_citation(self):
        """FIRES on the real thing: the resolved name of the same job is still extracted and checked."""
        body = {"pattern": "slurm-%j.out", "stdout": "slurm-59655414.out"}
        self.assertEqual({"slurm-59655414.out"}, V.bare_citations(json.dumps(body)))
        self.assertEqual("MISSING", self._classify("slurm-59655414.out", body,
                                                   {self.COMPANION + "/centring.py"})[0])

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


G2R = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/"
ENVTEST_PIN = (G2R + "envtest/envtest.json",
               "c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272", "runConfig.out")
PREPARE_PATH = G2R + "prepare/g2r_prepare.json"
PREPARE_SHA = "d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc"
PREPARE_TOKENS = tuple(f"runEventLoopOmniFold_{pl}_universes_full.root"
                       for pl in ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"))
PREPARE_PINS = frozenset((PREPARE_PATH, PREPARE_SHA, t) for t in PREPARE_TOKENS)


def _read(path):
    with open(os.path.join(REPO, path), encoding="utf-8") as fh:
        return fh.read()


def _findings_without(pins):
    """scan_full's findings with only `pins` removed from EXEMPT_BARE (every other pin kept)."""
    saved = V.EXEMPT_BARE
    try:
        V.EXEMPT_BARE = frozenset(saved - set(pins))
        return V.scan_full(root=REPO)["findings"]
    finally:
        V.EXEMPT_BARE = saved


class PinnedExemptionInventory(unittest.TestCase):
    """EXEMPT_BARE holds exactly the director's two rulings of 2026-11-13: #1139's one envtest pin and the
    prepare receipt's 12. Any other triple, or a missing one, fails here."""

    def test_exactly_thirteen_pins(self):
        self.assertEqual(13, len(V.EXEMPT_BARE))

    def test_the_pins_are_exactly_the_two_rulings(self):
        self.assertEqual({ENVTEST_PIN} | PREPARE_PINS, set(V.EXEMPT_BARE))

    def test_the_real_corpus_counts_thirteen_exemptions_and_no_finding(self):
        r = V.scan_full(root=REPO)
        self.assertEqual([], r["findings"])
        self.assertEqual(13, r["bare_states"].get("EXEMPT"))
        self.assertEqual(0, r["bare_states"].get("MISSING", 0))

    def test_the_self_test_reports_the_exemptions_narrow(self):
        self.assertTrue(V.self_test(REPO)["exemptions_narrow"])


class PinnedExemption(unittest.TestCase):
    """EXEMPT_BARE (the director's ruling on #1139, 2026-11-13) exempts one token in one receipt at one
    sha256. FIRES: the same token anywhere else, or in that receipt at any other bytes, is still
    classified, and is MISSING where the receipt's directory is tracked. SILENT: the pinned bytes.
    Bound to its own triple explicitly, not by the sort order of EXEMPT_BARE."""

    PATH, SHA, TOKEN = ENVTEST_PIN

    def setUp(self):
        self.text = _read(self.PATH)
        self.tracked = {os.path.dirname(self.PATH) + "/README.md"}
        self.dirs = {os.path.dirname(self.PATH)}

    def test_its_pin_is_in_the_inventory(self):
        self.assertIn(ENVTEST_PIN, V.EXEMPT_BARE)
        self.assertEqual(1, sum(1 for p, _, _ in V.EXEMPT_BARE if p == self.PATH))

    def test_the_committed_receipt_has_the_pinned_bytes_and_is_exempt(self):
        self.assertEqual(self.SHA, V.hashlib.sha256(self.text.encode("utf-8")).hexdigest())
        self.assertIn(self.TOKEN, V.bare_citations(self.text))
        self.assertTrue(V.is_exempt(self.PATH, self.TOKEN, self.text))

    def test_the_same_token_in_another_receipt_is_still_MISSING(self):
        other = os.path.dirname(self.PATH) + "/other.json"
        self.assertFalse(V.is_exempt(other, self.TOKEN, self.text))
        self.assertEqual("MISSING",
                         V.classify_bare(other, self.TOKEN, self.text, self.tracked, self.dirs)[0])

    def test_this_receipt_at_another_sha_is_still_MISSING(self):
        changed = self.text.replace('"verdict": "PASS"', '"verdict": "STOP"')
        self.assertNotEqual(changed, self.text)
        self.assertFalse(V.is_exempt(self.PATH, self.TOKEN, changed))
        self.assertEqual("MISSING",
                         V.classify_bare(self.PATH, self.TOKEN, changed, self.tracked, self.dirs)[0])

    def test_another_token_in_the_pinned_receipt_is_not_exempt(self):
        self.assertFalse(V.is_exempt(self.PATH, "runConfig.err", self.text))
        for t in PREPARE_TOKENS:
            self.assertFalse(V.is_exempt(self.PATH, t, self.text))

    def test_negative_control_without_the_pin_the_receipt_is_MISSING(self):
        hits = _findings_without({ENVTEST_PIN})
        self.assertEqual(1, len([x for x in hits if x["receipt"] == self.PATH]), hits)
        self.assertEqual(1, len(hits), hits)


class PinnedPrepareExemption(unittest.TestCase):
    """The director's ruling on the G2R prepare receipt (2026-11-13): 12 P5 per-playlist input file names,
    written by g2r_prepare.py run() into blocks/map.blocks, are exempt in that one record at its one
    sha256. FIRES: the same names in another receipt, or this path at other bytes, are MISSING."""

    def setUp(self):
        self.text = _read(PREPARE_PATH)
        self.tracked = {os.path.dirname(PREPARE_PATH) + "/README.md"}
        self.dirs = {os.path.dirname(PREPARE_PATH)}

    def test_its_twelve_pins_are_in_the_inventory(self):
        self.assertEqual(12, len(PREPARE_PINS))
        self.assertLessEqual(PREPARE_PINS, set(V.EXEMPT_BARE))
        self.assertEqual(PREPARE_PINS, {p for p in V.EXEMPT_BARE if p[0] == PREPARE_PATH})

    def test_the_committed_record_has_the_pinned_bytes_and_all_twelve_are_exempt(self):
        self.assertEqual(PREPARE_SHA, V.hashlib.sha256(self.text.encode("utf-8")).hexdigest())
        self.assertEqual(set(PREPARE_TOKENS), set(V.bare_citations(self.text)))
        for t in PREPARE_TOKENS:
            self.assertTrue(V.is_exempt(PREPARE_PATH, t, self.text), t)

    def test_the_same_names_in_another_receipt_are_still_MISSING(self):
        other = os.path.dirname(PREPARE_PATH) + "/other.json"
        for t in PREPARE_TOKENS:
            self.assertFalse(V.is_exempt(other, t, self.text), t)
            self.assertEqual("MISSING",
                             V.classify_bare(other, t, self.text, self.tracked, self.dirs)[0], t)

    def test_this_path_at_other_bytes_is_still_MISSING(self):
        changed = self.text.replace('"verdict": "PASS"', '"verdict": "STOP"')
        self.assertNotEqual(changed, self.text)
        for t in PREPARE_TOKENS:
            self.assertFalse(V.is_exempt(PREPARE_PATH, t, changed), t)
            self.assertEqual("MISSING",
                             V.classify_bare(PREPARE_PATH, t, changed, self.tracked, self.dirs)[0], t)

    def test_other_tokens_in_this_record_are_not_exempt(self):
        for t in ("runEventLoopOmniFold_1H_universes_full.root",
                  "runEventLoopOmniFold_MEFHC_universes_full.root", "runConfig.out"):
            self.assertFalse(V.is_exempt(PREPARE_PATH, t, self.text), t)

    def test_negative_control_without_the_twelve_pins_the_record_is_MISSING(self):
        hits = _findings_without(PREPARE_PINS)
        self.assertEqual(12, len([x for x in hits if x["receipt"] == PREPARE_PATH]), hits)
        self.assertEqual(12, len(hits), hits)


if __name__ == "__main__":
    unittest.main()

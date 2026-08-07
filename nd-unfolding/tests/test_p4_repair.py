#!/usr/bin/env python3
"""Fail-closed gate tests for the standard P4 lateral repair (2026-07-18).

Covers the eight verifier-identified failure modes: missing endpoint, truncated/
incomplete output, missing census/migration evidence, zero/absent component,
order/hash mismatch, missing support block, component-sum mismatch, invalid
projection. ROOT-free. Also checks the preserved MAT two-endpoint formula and
that the happy path does NOT false-trip.
"""
import sys, unittest
from pathlib import Path
import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import p4_lib as P
from p4_lib import P4GateError


def _band_cov(minus, plus):
    """MAT two-endpoint block via uq_math (preserved formula)."""
    from uq_math import mat_covariance
    return mat_covariance(np.stack([np.asarray(minus, float), np.asarray(plus, float)]))


class ManifestAndConfig(unittest.TestCase):
    def test_missing_endpoint_fails(self):
        entries = [(b, e, "fp") for (b, e) in P.canonical_endpoints()][:-1]  # 9/10
        with self.assertRaises(P4GateError):
            P.endpoint_manifest_hash(entries)

    def test_full_inventory_hashes_and_is_order_independent(self):
        full = [(b, e, f"{b}{e}") for (b, e) in P.canonical_endpoints()]
        h1 = P.endpoint_manifest_hash(full)
        h2 = P.endpoint_manifest_hash(list(reversed(full)))
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_truncated_incomplete_unfold_set_fails(self):
        present = {f"{b}_{e}" for (b, e) in P.canonical_endpoints()}
        present.discard("MuonResolution_1")  # truncated -> failed content-validation
        with self.assertRaises(P4GateError):
            P.require_complete_unfold_set(present)
        P.require_complete_unfold_set({f"{b}_{e}" for (b, e) in P.canonical_endpoints()})

    def test_config_hash_and_validate(self):
        good = P.P4Config(seed=42, iters=5, use_weights=True, universe=None)
        self.assertTrue(good.validate())
        self.assertNotEqual(good.hash(), P.P4Config(seed=7).hash())         # order/hash mismatch
        with self.assertRaises(P4GateError):
            P.P4Config(universe="BeamAngleX:0").validate()                  # must be nominal
        with self.assertRaises(P4GateError):
            P.P4Config(seed=7).validate()


class MergedAudit(unittest.TestCase):
    def _meta(self, **ov):
        m = {"tree_entries": {"mc_truth_denom": 100, "mc_signal_reco": 100,
                              "mc_background": 5, "data": 20},
             "mcPOT": 1.2e20, "dataPOT": 3.4e19, "hasTruthOnlyMisses": 1,
             "nTruthOnlyMisses": 66989,
             "census": {"TruthEntrants": 0, "TruthExits": 0,
                        "RecoEntrants": 21, "RecoExits": 21},
             "migration_policy": "active-universe selection-complete"}
        m.update(ov); return m

    def test_happy_path(self):
        self.assertTrue(P.check_merged_metadata(self._meta()))

    def test_missing_census_evidence_fails(self):
        m = self._meta(census={"TruthEntrants": 0})  # missing 3 counters
        with self.assertRaises(P4GateError):
            P.check_merged_metadata(m)

    def test_missing_migration_policy_fails(self):
        with self.assertRaises(P4GateError):
            P.check_merged_metadata(self._meta(migration_policy=""))

    def test_completeness_equality_and_empty_tree_and_pot(self):
        with self.assertRaises(P4GateError):     # signal_reco != truth_denom
            P.check_merged_metadata(self._meta(tree_entries={
                "mc_truth_denom": 100, "mc_signal_reco": 98,
                "mc_background": 5, "data": 20}))
        with self.assertRaises(P4GateError):     # empty tree
            P.check_merged_metadata(self._meta(tree_entries={
                "mc_truth_denom": 100, "mc_signal_reco": 100,
                "mc_background": 0, "data": 20}))
        with self.assertRaises(P4GateError):     # non-positive POT
            P.check_merged_metadata(self._meta(mcPOT=0.0))


class ComponentGates(unittest.TestCase):
    def _bands(self):
        rng = np.random.default_rng(0)
        d = {}
        for b in P.BANDS:
            m = rng.normal(1.0, 0.05, 4); p = rng.normal(1.0, 0.05, 4)
            d[b] = _band_cov(m, p)
        return d

    def test_mat_two_endpoint_formula_preserved(self):
        minus = np.array([8.0, 22.0]); plus = np.array([14.0, 18.0])
        expected = np.outer((plus - minus) / 2, (plus - minus) / 2)
        np.testing.assert_allclose(_band_cov(minus, plus), expected)

    def test_exact_bands_required(self):
        b = self._bands(); P.require_exact_bands(b)
        b.pop("Muon_Energy_MINOS")
        with self.assertRaises(P4GateError):
            P.require_exact_bands(b)
        b2 = self._bands(); b2["ExtraBand"] = b2["BeamAngleX"]
        with self.assertRaises(P4GateError):
            P.require_exact_bands(b2)

    def test_zero_or_absent_component_fails(self):
        b = self._bands(); b["BeamAngleX"] = np.zeros((4, 4))  # zero component
        with self.assertRaises(P4GateError):
            P.component_traces_positive_finite(b)
        b2 = self._bands(); del b2["BeamAngleY"]               # absent component
        with self.assertRaises(P4GateError):
            P.component_traces_positive_finite(b2)

    def test_component_sum_exact_and_mismatch(self):
        b = self._bands()
        total = sum(b[k] for k in P.BANDS)
        self.assertLessEqual(P.check_component_sum(total, b), 1e-9)
        with self.assertRaises(P4GateError):
            P.check_component_sum(total * 1.01, b)             # component-sum mismatch


class SupportAndPSD(unittest.TestCase):
    def test_missing_support_block_fails(self):
        A = np.eye(4)
        with self.assertRaises(P4GateError):
            P.check_support_comparison(A, None)                # missing support
        with self.assertRaises(P4GateError):
            P.check_support_comparison(None, A)
        r = P.check_support_comparison(2 * np.eye(4), np.eye(4))
        self.assertGreater(r["ratio"], 1.0)

    def test_psd_symmetry_gate(self):
        P.check_symmetric_psd(np.array([[4.0, 1.0], [1.0, 9.0]]))
        with self.assertRaises(P4GateError):                  # not PSD
            P.check_symmetric_psd(np.array([[1.0, 2.0], [2.0, 1.0]]))


class Projection(unittest.TestCase):
    def test_mask_order_hash_mismatch(self):
        m1 = np.zeros(P.GRID_NBINS, bool); m1[:100] = True
        m2 = np.zeros(P.GRID_NBINS, bool); m2[1:101] = True
        h1, n1 = P.mask_order_hash(m1); h2, _ = P.mask_order_hash(m2)
        self.assertNotEqual(h1, h2)
        self.assertEqual(n1, 100)
        with self.assertRaises(P4GateError):
            P.mask_order_hash(np.zeros(P.GRID_NBINS, bool))   # zero reported bins

    def test_projection_nonmutation_and_invalid(self):
        C = np.diag([4.0, 9.0, 16.0])
        M = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])      # sum drop-axis
        x = np.array([2.0, 3.0, 5.0]); xlow = M @ x
        Clow, st = P.check_projection_nonmutation(C, M, x, xlow)
        self.assertEqual(Clow.shape, (2, 2))
        Mbad = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])
        xlow_wrong = np.array([2.0, 99.0])                    # invalid projection (mutated central)
        with self.assertRaises(P4GateError):
            P.check_projection_nonmutation(C, Mbad, x, xlow_wrong)


class IntegrationCLI(unittest.TestCase):
    """Invoke the REAL fail-closed CLI entrypoints (pre-ROOT guards) and assert
    nonzero exit + no product written. Runnable without PyROOT (lazy ROOT import)."""
    import os as _os
    ND = str(Path(__file__).resolve().parents[1])

    def _run(self, script, args):
        import subprocess
        r = subprocess.run([sys.executable, f"{self.ND}/{script}", *args],
                           cwd=self.ND, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr)

    def test_build_components_rejects_adopted_out_path(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "uq_universe_5d_covariance_combined_uthrow.root")
            rc, _ = self._run("p4_build_components.py",
                              ["--manifest", "/dev/null", "--support-family",
                               "uq_5d/universe_stage2_5d_bkgaware/x.root",
                               "--out", out, "--out-manifest", os.path.join(td, "m.json")])
            self.assertNotEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

    def test_build_components_rejects_superseded_support_family(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "cand.root")
            rc, _ = self._run("p4_build_components.py",
                              ["--manifest", "/dev/null", "--support-family",
                               "uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root",
                               "--out", out, "--out-manifest", os.path.join(td, "m.json")])
            self.assertNotEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

    def test_build_components_requires_bkgaware_family(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "cand.root")
            rc, _ = self._run("p4_build_components.py",
                              ["--manifest", "/dev/null", "--support-family",
                               "some/other/combined.root",
                               "--out", out, "--out-manifest", os.path.join(td, "m.json")])
            self.assertNotEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

    def test_project_rejects_protected_out_path(self):
        """REPAIR-4 (verifier defect 6b). This test used to pass `--proj`, an argument the
        projector does not define, so argparse exited nonzero BEFORE the path guard ran and
        `assertNotEqual(rc, 0)` passed for the wrong reason. It asserted nothing about the
        guard it was named for. Now: only real arguments, and the assertion is on the SPECIFIC
        gate reached, not merely a nonzero return."""
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = "uq_4d/corrected/proj_candidate.root"
            rc, err = self._run("p4_project_4d.py",
                                ["--c5", os.path.join(td, "c5.root:k"),
                                 "--manifest", "/dev/null", "--out", out])
            self.assertNotEqual(rc, 0)
            self.assertNotIn("unrecognized arguments", err)   # would mean we never reached the guard
            self.assertIn("candidate must be under", err)     # the guard we are actually testing
            self.assertFalse(os.path.exists(f"{self.ND}/{out}"))


class Round3Gates(unittest.TestCase):
    def test_candidate_path_guard(self):
        P.require_candidate_path("nd-unfolding/active_universe_5d/standard/candidate/std5d.root")
        for bad in ("active_universe_5d/standard/candidate/std_uthrow.root",  # adopted token
                    "active_universe_5d/standard/candidate/uq_universe_5d_covariance_combined.root",
                    "uq_4d/corrected/x.root",                                  # protected
                    "active_universe_5d/standard/merged/x.root"):              # not candidate subdir
            with self.assertRaises(P4GateError):
                P.require_candidate_path(bad)

    def test_config_axes_estimator_enforced(self):
        with self.assertRaises(P4GateError):
            P.P4Config(axes="eavail,q3").validate()
        with self.assertRaises(P4GateError):
            P.P4Config(estimator="nn").validate()

    def test_prove_identity(self):
        A = np.eye(3); self.assertLessEqual(P.prove_identity(A, A.copy(), 1e-12, "x"), 1e-12)
        with self.assertRaises(P4GateError):
            P.prove_identity(A, A * 1.1, 1e-9, "x")

    def test_edges_bin_volume_hash_deterministic_and_sensitive(self):
        e1 = [np.array([0., 1.]), np.array([0., 1.]), np.array([0., 1.]),
              np.array([0., 1.]), np.array([0., 1., 3.])]
        h1 = P.edges_bin_volume_hash(e1); h2 = P.edges_bin_volume_hash([a.copy() for a in e1])
        self.assertEqual(h1, h2)
        e2 = e1[:4] + [np.array([0., 1., 2.])]                 # different W edges/widths
        self.assertNotEqual(P.edges_bin_volume_hash(e2)["bin_volume_hash"], h1["bin_volume_hash"])

    def test_deterministic_projection_M_width_weighted(self):
        edges = [np.array([0., 1.])] * 4 + [np.array([0., 1., 3.])]   # 2 W bins, widths 1,2
        mh = np.array([True, True]); ml = np.array([True])
        M = P.build_projection_M(edges, 4, mh, ml)
        np.testing.assert_allclose(M, np.array([[1.0, 2.0]]))         # width-weighted marginalization
        x = np.array([5.0, 7.0]); np.testing.assert_allclose(M @ x, np.array([5.0 * 1 + 7.0 * 2]))
        with self.assertRaises(P4GateError):                          # wrong high-mask size
            P.build_projection_M(edges, 4, np.array([True]), ml)

    def test_orchestrator_receipt_validation(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            paths = [f"m/{b}_{e}.root" for b in P.BANDS for e in P.ENDPOINTS]
            open(os.path.join(td, "COMPLETE"), "w").write("1")
            open(os.path.join(td, "summary.tsv"), "w").write("x\n")
            open(os.path.join(td, "validation.tsv"), "w").write("ok\n")
            open(os.path.join(td, "standard.sha256"), "w").write(
                "\n".join(f"{'a'*64}  {p}" for p in paths) + "\n")
            open(os.path.join(td, "standard.inventory.tsv"), "w").write(
                "\n".join(f"100\t1700000000\t{p}" for p in paths) + "\n")
            live = {p: (100, 1700000000) for p in paths}
            rec = P.validate_orchestrator_merged_receipt(td, live)
            self.assertEqual(rec["n"], 10); self.assertEqual(len(rec["hash_list_digest"]), 64)
            with self.assertRaises(P4GateError):                      # size/mtime drift
                P.validate_orchestrator_merged_receipt(td, {p: (101, 1700000000) for p in paths})
            os.remove(os.path.join(td, "COMPLETE"))
            with self.assertRaises(P4GateError):                      # missing COMPLETE
                P.validate_orchestrator_merged_receipt(td, live)


class IntegrationCLI2(unittest.TestCase):
    ND = str(Path(__file__).resolve().parents[1])
    def _run(self, script, args):
        import subprocess
        r = subprocess.run([sys.executable, f"{self.ND}/{script}", *args],
                           cwd=self.ND, capture_output=True, text=True)
        return r.returncode

    def test_project_rejects_cli_tolerance_override(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = "active_universe_5d/standard/candidate/proj.root"
            rc = self._run("p4_project_4d.py", ["--c5", os.path.join(td, "c.root:k"),
                           "--manifest", "/dev/null", "--out", out, "--central-rel", "0.9"])
            self.assertNotEqual(rc, 0)

    def test_adopt_requires_explicit_flag(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            for n in ("cand.root", "prov.json", "val.json"):
                open(os.path.join(td, n), "w").write("{}" if n.endswith("json") else "x")
            rc = self._run("p4_adopt_standard.py", ["--candidate", os.path.join(td, "cand.root"),
                           "--component-manifest", os.path.join(td, "prov.json"),
                           "--validation", os.path.join(td, "val.json"),
                           "--out", os.path.join(td, "adopted.root")])
            self.assertNotEqual(rc, 0)


class StandardFooting(unittest.TestCase):
    """G-1 (2026-08-07): the standard lane must RECORD its background footing rather than
    inherit the driver default, and must fail closed when the footing is absent or wrong.

    Fixtures here are the real producer's literal output, never hand-assembled to match what
    the consumer expects -- that inversion is precisely BEN-040, in this same chain."""

    FIXTURE = (Path(__file__).resolve().parent / "fixtures"
               / "p4_std_unfold_purity_BeamAngleX_0.log")
    DRIVER = Path(__file__).resolve().parents[1] / "unfold_nd_omnifold_unbinned.py"

    # ---------- the declared footing ----------
    def test_config_carries_and_hashes_bkg_mode(self):
        c = P.P4Config()
        self.assertEqual(c.bkg_mode, "purity")            # the 2026-08-07 decision
        self.assertIn("bkg_mode", c.as_dict())
        # the footing participates in the config hash, so it cannot drift unnoticed
        self.assertNotEqual(c.hash(), P.P4Config(bkg_mode="negweight-refined").hash())

    def test_config_rejects_unknown_and_unauthorized_bkg_mode(self):
        with self.assertRaises(P4GateError):
            P.P4Config(bkg_mode="nonsense").validate()     # not a driver choice at all
        with self.assertRaises(P4GateError):
            P.P4Config(bkg_mode="negweight-refined").validate()   # known, but not the decision

    def test_footing_block_is_nested_producer_shape(self):
        f = P.P4Config().footing()
        for k in P.STANDARD_FOOTING_KEYS:
            self.assertIn(k, f)
        self.assertEqual(f["estimator"], "lgbm")
        self.assertEqual(f["seed"], 42)
        self.assertEqual(f["iters"], 5)
        self.assertIs(f["use_weights"], True)
        self.assertIs(f["full_phase_space"], False)        # standard, not FPS

    # ---------- the fail-closed gate: positive, absent, mismatched ----------
    def test_gate_accepts_purity(self):                    # POSITIVE: it can actually pass
        self.assertTrue(P.require_standard_footing({"footing": P.P4Config().footing()}))

    def test_gate_rejects_absent_footing(self):
        with self.assertRaises(P4GateError):
            P.require_standard_footing({})                 # no field at all == unprovable
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": {}})

    def test_gate_rejects_missing_bkg_mode_and_mismatch(self):
        f = P.P4Config().footing(); f.pop("bkg_mode")
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": f})     # unprovable
        bad = P.P4Config().footing(); bad["bkg_mode"] = "negweight-refined"
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": bad})   # mismatched
        wrong = P.P4Config().footing(); wrong["estimator"] = "nn"
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": wrong})

    def test_gate_rejects_flattened_footing(self):
        """A manifest with the five keys at TOP level and no nested block must fail, not
        silently read None on every key. This is the BEN-040 shape, inverted into a guard."""
        flat = dict(P.STANDARD_REQUIRED_FOOTING); flat["bkg_mode"] = "purity"
        with self.assertRaises(P4GateError):
            P.require_standard_footing(flat)

    # ---------- log classification, against real producer output ----------
    def test_real_purity_log_is_positively_identified(self):
        text = self.FIXTURE.read_text(errors="replace")
        mode, why = P.classify_log_bkg_mode(text)
        self.assertEqual(mode, "purity", why)
        self.assertNotIn("[INFO] bkg-mode=", text)         # the silent branch, as claimed

    def test_negweight_announcement_is_read_from_the_log(self):
        base = self.FIXTURE.read_text(errors="replace")
        for m in ("negweight", "negweight-refined"):
            text = base + (f"[INFO] bkg-mode={m}: data side 4091707 events "
                           f"(of 4119797) in the analysis window at +1.\n")
            mode, why = P.classify_log_bkg_mode(text)
            self.assertEqual(mode, m, why)                 # announcement beats the signature

    def test_indeterminate_log_is_unprovable_not_assumed_purity(self):
        mode, why = P.classify_log_bkg_mode("[INFO] axes (5D): pt, pz\nStarting iteration 0\n")
        self.assertIsNone(mode)                            # no signature => cannot conclude
        self.assertIn("unprovable", why)

    def test_conflicting_and_unrecognized_announcements_fail(self):
        two = ("[INFO] bkg-mode=negweight: x\n"
               "[INFO] bkg-mode=negweight-refined: y\n")
        self.assertIsNone(P.classify_log_bkg_mode(two)[0])
        self.assertIsNone(P.classify_log_bkg_mode("[INFO] bkg-mode=banana: z\n")[0])

    # ---------- contract: the classifier must track the real producer ----------
    def test_classifier_markers_still_exist_in_the_driver(self):
        """If the driver's print statements change, this classifier's inference from silence
        becomes wrong. Pin both markers to the producer's source so drift fails a test
        rather than silently mislabelling a footing."""
        src = self.DRIVER.read_text(errors="replace")
        self.assertIn('f"[INFO] bkg-mode={args.bkg_mode}', src)
        self.assertIn('[INFO] measured training:', src)
        self.assertIn('default="purity"', src)             # the default the launcher overrides
        self.assertIn('elif args.bkg_mode == "purity":', src)   # the branch that stays silent

    def test_launcher_passes_bkg_mode_explicitly(self):
        sh = (Path(__file__).resolve().parents[1] / "run_p4_unfold_std.sh").read_text()
        self.assertIn("--bkg-mode", sh)                    # no reliance on the driver default
        self.assertIn('"${BKG_MODE}"', sh)                 # and it comes from P4Config
        self.assertIn('"bkg_mode":"%s"', sh)               # stamped into the receipts


class Repair4DriverContract(unittest.TestCase):
    """REPAIR-4, verifier defect 1. Stages 4-6 had NEVER executed, so nothing caught that the
    driver called the validator and projector with arguments they do not define and a ROOT key
    nothing writes. These tests derive the expectation from the REAL callees -- each script's
    own argparse and the builder's own key constants -- so they fail if either side drifts.
    That is the point: the previous suite asserted only `rc != 0` and was satisfied by an
    argparse error (defect 6b)."""

    ND = Path(__file__).resolve().parents[1]

    def _driver(self):
        return (self.ND / "run_p4_standard.sh").read_text()

    def _argparse_opts(self, script):
        """The set of long options a script actually defines, read from its source."""
        import re
        src = (self.ND / script).read_text()
        return set(re.findall(r'add_argument\("(--[a-z0-9-]+)"', src))

    def _driver_opts_for(self, script):
        """The long options the driver passes to `script`, read from the driver."""
        import re
        drv = self._driver()
        m = re.search(rf"python3 {re.escape(script)}((?:[^\n]*\\\n)*[^\n]*)", drv)
        self.assertIsNotNone(m, f"driver does not invoke {script}")
        return set(re.findall(r"(--[a-z0-9-]+)", m.group(1)))

    # ---------- D1b/D1c: the driver must speak each callee's real CLI ----------
    def test_driver_passes_only_options_the_validator_defines(self):
        passed = self._driver_opts_for("p4_validate_active_lateral.py")
        defined = self._argparse_opts("p4_validate_active_lateral.py")
        self.assertTrue(passed, "no options parsed from the validator invocation")
        self.assertEqual(passed - defined, set(),
                         f"driver passes options the validator does not define: {passed - defined}")

    def test_driver_supplies_every_required_validator_option(self):
        passed = self._driver_opts_for("p4_validate_active_lateral.py")
        for req in ("--candidate", "--support", "--manifest", "--merged-audit", "--out"):
            self.assertIn(req, passed, f"driver omits required validator option {req}")

    def test_driver_passes_only_options_the_projector_defines(self):
        passed = self._driver_opts_for("p4_project_4d.py")
        defined = self._argparse_opts("p4_project_4d.py")
        self.assertEqual(passed - defined, set(),
                         f"driver passes options the projector does not define: {passed - defined}")
        self.assertNotIn("--proj", passed)        # the exact retired argument from defect 1

    def test_driver_passes_only_options_the_builder_defines(self):
        passed = self._driver_opts_for("p4_build_components.py")
        defined = self._argparse_opts("p4_build_components.py")
        self.assertEqual(passed - defined, set(),
                         f"driver passes options the builder does not define: {passed - defined}")

    # ---------- D1c: the key must be one the builder actually writes ----------
    DEAD_KEY = "hCov_std" + "_final5_candidate"      # split so this file is not its own hit

    @staticmethod
    def _code_lines(text):
        """Lines that are not wholly a `#` comment. Keeps history in comments testable-around:
        documenting the dead key is good, *referencing* it is the defect."""
        return [l for l in text.splitlines() if not l.lstrip().startswith("#")]

    def test_candidate_key_is_produced_by_the_builder(self):
        builder = (self.ND / "p4_build_components.py").read_text()
        self.assertIn("P.CANDIDATE_TOTAL_KEY", builder)      # builder writes the shared constant
        self.assertIn("CANDIDATE_TOTAL_KEY", self._driver()) # driver reads the same one
        self.assertNotIn(self.DEAD_KEY, "\n".join(self._code_lines(self._driver())))

    def test_dead_candidate_key_appears_in_no_executable_line(self):
        import subprocess
        r = subprocess.run(["git", "grep", "-l", self.DEAD_KEY],
                           cwd=self.ND.parent, capture_output=True, text=True)
        offenders = []
        for rel in r.stdout.splitlines():
            if not rel.strip() or rel.endswith(".md") or "runs/" in rel or "tests/" in rel:
                continue
            body = (self.ND.parent / rel).read_text(errors="replace")
            if self.DEAD_KEY in "\n".join(self._code_lines(body)):
                offenders.append(rel)
        self.assertEqual(offenders, [],
                         f"dead candidate key referenced in executable code: {offenders}")

    def test_candidate_keys_are_single_sourced(self):
        self.assertEqual(P.CANDIDATE_TOTAL_KEY, "hCov_stdcombined5d_total_candidate")
        self.assertEqual(P.CANDIDATE_SYST_KEY, "hCov_stdsyst5d_total_candidate")
        self.assertEqual(P.candidate_band_key("BeamAngleX"), "hCov_active5d_BeamAngleX")
        with self.assertRaises(P4GateError):
            P.candidate_band_key("NotABand")

    # ---------- D1a: stage order ----------
    def test_stage_order_is_audit_then_unfold_then_evidence(self):
        drv = self._driver()
        i_audit = drv.index("run bash run_p4_merge_audit_std.sh")
        i_unfold = drv.index("run bash run_p4_unfold_std.sh")
        i_evid = drv.index("python3 p4_evidence.py")
        self.assertLess(i_audit, i_unfold, "merge+audit must precede unfold")
        self.assertLess(i_unfold, i_evid,
                        "endpoint evidence must come AFTER unfold, or the manifest describes "
                        "endpoints the next stage can rewrite")

    def test_default_stop_after_is_the_safe_preflight(self):
        drv = self._driver()
        self.assertIn('STOP_AFTER="${STOP_AFTER:-audit}"', drv)
        self.assertIn("unknown STOP_AFTER", drv)          # invalid values abort, not fall through

    def test_covariance_stages_are_still_gated(self):
        """Compare EXECUTABLE positions, not the header comment -- both strings appear in the
        stage-list comment at the top, so a naive index() compares documentation."""
        code = "\n".join(self._code_lines(self._driver()))
        self.assertIn("P4_VERIFIER_PASS", code)
        self.assertLess(code.index("P4_VERIFIER_PASS"),
                        code.index("python3 p4_build_components.py"),
                        "the verifier gate must precede component construction")


class Repair4EvidenceBindings(unittest.TestCase):
    """REPAIR-4, verifier defect 3 (the two parts that are pure logic and testable ROOT-free)."""

    ND = Path(__file__).resolve().parents[1]

    def test_config_hash_covers_the_reported_grid(self):
        """D3a: the grid field used to be added to man["config"] AFTER config_hash was
        computed, so the recorded hash did not cover the recorded configuration."""
        c = P.P4Config()
        self.assertIn("full_phase_space_reported_grid", c.as_dict())
        self.assertEqual(c.as_dict()["full_phase_space_reported_grid"], P.GRID_NBINS)
        # and it is inside the hash, not bolted on beside it
        import hashlib, json
        expect = hashlib.sha256(json.dumps(c.as_dict(), sort_keys=True).encode()).hexdigest()
        self.assertEqual(c.hash(), expect)

    def test_evidence_no_longer_mutates_config_after_hashing(self):
        src = (self.ND / "p4_evidence.py").read_text()
        code = [l for l in src.splitlines() if not l.lstrip().startswith("#")]
        joined = "\n".join(code)
        self.assertNotIn('man["config"]["full_phase_space_reported_grid"]', joined)

    def test_zero_sel_is_actually_enforced(self):
        """D3d: ZERO_SEL was declared and referenced by no check -- the bin-migration-only
        claim for the three muon bands was documentation, not a gate."""
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("ZERO_SEL", code)
        self.assertIn("elif b in ZERO_SEL", code)
        self.assertIn("selmig == 0", code)

    def test_endpoint_index_is_asserted(self):
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("idx_meta", code)
        self.assertIn("endpoint INDEX mismatch", code)

    def test_the_two_band_sets_partition_the_five_bands(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("_ev", self.ND / "p4_evidence.py")
        # do not import (needs ROOT); read the literals instead
        src = (self.ND / "p4_evidence.py").read_text()
        import re
        nz = set(re.findall(r'NONZERO_MIG = \{([^}]*)\}', src)[0].replace('"', '').split(", "))
        zs = set(re.findall(r'ZERO_SEL\s*= \{([^}]*)\}', src)[0].replace('"', '').split(", "))
        nz = {s.strip() for s in nz if s.strip()}
        zs = {s.strip() for s in zs if s.strip()}
        self.assertEqual(nz | zs, set(P.BANDS), "the two sets must cover exactly the five bands")
        self.assertEqual(nz & zs, set(), "a band cannot be in both sets")


class Repair4ReceiptSchema(unittest.TestCase):
    """REPAIR-4, verifier defect 2. The resume path accepted any ROOT plus any nonempty .done.

    The receipt fixture here is built by running the launcher's OWN `printf` format string,
    extracted from run_p4_unfold_std.sh at test time -- not hand-written to match the reader.
    If the producer's field list changes, this fixture changes with it, and a reader that
    drifted from the writer fails here. That inversion (fixture shaped like the consumer) is
    precisely BEN-040, in this same chain."""

    ND = Path(__file__).resolve().parents[1]

    GOOD = dict(tag="BeamAngleX_0", root_sha256="a" * 64, merged_sha256="b" * 64,
                central5d_sha256="c" * 64, config_hash="d" * 64, bkg_mode="purity")

    def _producer_receipt(self, mode="produced", **over):
        """Render a receipt through the launcher's real format string."""
        import re, subprocess, json
        sh = (self.ND / "run_p4_unfold_std.sh").read_text()
        m = re.search(r"printf '(\{\"tag\".*?\}\\n)'", sh, re.S)
        self.assertIsNotNone(m, "could not extract the launcher's receipt format")
        fmt = m.group(1)
        vals = dict(self.GOOD); vals.update(over)
        # positional order matches the launcher's own argument order
        args = [vals["tag"], vals["root_sha256"], vals["merged_sha256"], vals["central5d_sha256"],
                vals["config_hash"], vals["bkg_mode"], "deadbeef", "2026-08-07T00:00:00Z"]
        if mode == "legacy-attested":
            fmt = fmt.replace('"mode":"produced"', '"mode":"legacy-attested"')
        out = subprocess.run(["printf", fmt, *args], capture_output=True, text=True).stdout
        return json.loads(out)

    def test_producer_receipt_has_every_required_key(self):
        rec = self._producer_receipt()
        for k in P.RECEIPT_REQUIRED_KEYS:
            self.assertIn(k, rec, f"the real producer omits required key {k}")

    def test_validator_accepts_the_real_producer_output(self):
        rec = self._producer_receipt()
        self.assertTrue(P.validate_endpoint_receipt(rec, **self.GOOD))

    def test_legacy_attested_receipt_now_carries_merged_and_central(self):
        """D2b: the legacy receipt used to omit these, making an attested endpoint permanently
        less provable than a produced one."""
        rec = self._producer_receipt(mode="legacy-attested")
        self.assertEqual(rec["mode"], "legacy-attested")
        self.assertIn("merged_sha256", rec)
        self.assertIn("central5d_sha256", rec)
        self.assertTrue(P.validate_endpoint_receipt(rec, **self.GOOD))

    def test_incomplete_legacy_format_is_rejected(self):
        rec = self._producer_receipt()
        for drop in ("merged_sha256", "central5d_sha256", "bkg_mode", "config_hash", "tag"):
            bad = {k: v for k, v in rec.items() if k != drop}
            with self.assertRaises(P4GateError, msg=f"missing {drop} accepted"):
                P.validate_endpoint_receipt(bad, **self.GOOD)

    def test_every_identity_drift_is_rejected(self):
        rec = self._producer_receipt()
        for field, kw in (("root_sha256", "root_sha256"), ("merged_sha256", "merged_sha256"),
                          ("central5d_sha256", "central5d_sha256"), ("config_hash", "config_hash"),
                          ("bkg_mode", "bkg_mode")):
            drifted = dict(rec); drifted[field] = "z" * 64 if field != "bkg_mode" else "negweight"
            with self.assertRaises(P4GateError, msg=f"{field} drift accepted"):
                P.validate_endpoint_receipt(drifted, **self.GOOD)

    def test_receipt_root_pair_mismatch_is_rejected(self):
        rec = self._producer_receipt(tag="BeamAngleY_1")
        with self.assertRaises(P4GateError):
            P.validate_endpoint_receipt(rec, **self.GOOD)      # receipt belongs to another endpoint

    def test_unknown_mode_rejected(self):
        rec = self._producer_receipt(); rec["mode"] = "hand-written"
        with self.assertRaises(P4GateError):
            P.validate_endpoint_receipt(rec, **self.GOOD)

    # ---------- D2d: extras as well as missing ----------
    def test_exact_tag_set_rejects_missing_and_extra(self):
        full = [f"{b}_{e}" for b in P.BANDS for e in P.ENDPOINTS]
        self.assertTrue(P.require_exact_endpoint_tags(full))
        with self.assertRaises(P4GateError):
            P.require_exact_endpoint_tags(full[:-1])                    # missing
        with self.assertRaises(P4GateError):
            P.require_exact_endpoint_tags(full + ["BeamAngleX_2"])      # extra
        with self.assertRaises(P4GateError):
            P.require_exact_endpoint_tags(full + ["SomeOtherBand_0"])   # foreign product

    # ---------- D2a/D2c: the launcher wires them ----------
    def test_launcher_uses_the_receipt_gate_and_clears_stale_pairs(self):
        sh = (self.ND / "run_p4_unfold_std.sh").read_text()
        self.assertIn("p4_check_receipt.py", sh)         # skip is content-validating
        self.assertIn("STALE", sh)                       # and a reject re-runs
        self.assertIn('rm -f "${REC}"', sh)              # leaving no stale ROOT/receipt pair

    def test_launcher_propagates_receipt_write_failure(self):
        sh = (self.ND / "run_p4_unfold_std.sh").read_text()
        self.assertIn("receipt publication failed after ROOT publish", sh)
        self.assertIn("return 8", sh)

    def test_receipt_checker_rejects_absent_and_malformed(self):
        import subprocess, tempfile, os
        with tempfile.TemporaryDirectory() as td:
            missing = os.path.join(td, "nope.done")
            r = subprocess.run([sys.executable, str(self.ND / "p4_check_receipt.py"),
                                "--receipt", missing, "--tag", "BeamAngleX_0",
                                "--root", missing, "--merged", missing],
                               capture_output=True, text=True, cwd=str(self.ND))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("RECEIPT-REJECT", r.stdout + r.stderr)
            bad = os.path.join(td, "bad.done")
            open(bad, "w").write("not json")
            r2 = subprocess.run([sys.executable, str(self.ND / "p4_check_receipt.py"),
                                 "--receipt", bad, "--tag", "BeamAngleX_0",
                                 "--root", bad, "--merged", bad],
                                capture_output=True, text=True, cwd=str(self.ND))
            self.assertNotEqual(r2.returncode, 0)
            self.assertIn("RECEIPT-REJECT", r2.stdout + r2.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)

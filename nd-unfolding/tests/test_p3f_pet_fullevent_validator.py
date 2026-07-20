"""Login-safe / ROOT-free tests for the Gate-3 P3F full-event validator
(pet/validate_p3f_pet_fullevent.py).

No ROOT / no TF / no compute. These exercise the pure logic: the exact 5x2x12 inventory mapping,
active-universe metadata + migration-census checks, the composed EXHAUSTIVE domain-validator result
gate (status/fatal/bounds/non-superseded-base-failure/complete-census + nested base result), the
assembled report + single verdict, and the atomic WORK-only receipt (proving no publication on
failure). The ROOT reads + domain-validator subprocess + file hashing in main() are the RUNTIME step
and are NOT exercised here. The domain validator (and the smoke validator it composes) are injected
via synthetic domain-receipt dicts; this file never runs or alters them.

The KNOWN-domain-recovery semantic (playlists 1D/1E/1F/1P): the composed smoke validator may fail
ONLY the two sampled reco-muon heuristics (bkg_reco_muon_valid / data_reco_muon_valid) -- which the
domain validator SUPERSEDES with a bound out-of-domain census -- and Gate-3 must still PASS."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "pet"))

import validate_p3f_pet_fullevent as v  # noqa: E402  (ROOT deferred -> login-safe import)


def good_observed(band="MuonResolution", idx=1):
    return {v.ACTIVE_BAND_MARKER: band, v.ACTIVE_INDEX_MARKER: idx,
            v.ACTIVE_ENABLED_MARKER: 1, v.ACTIVE_LATERAL_MARKER: 1,
            "activeUniverseTruthEntrants": 10, "activeUniverseTruthExits": 3,
            "activeUniverseRecoEntrants": 7, "activeUniverseRecoExits": 0}


def _reco_checks_and_census(bg=2, dt=3, sig=4):
    checks = [
        {"tree": "mc_background", "context": "background", "nonfinite": 0,
         "sentinel_on_selected": 0, "invalid_muon_or_minos": bg,
         "in_domain_scalar_muon_mismatch": 0, "out_of_domain": bg},
        {"tree": "data", "context": "data", "nonfinite": 0, "sentinel_on_selected": 0,
         "invalid_muon_or_minos": dt, "in_domain_scalar_muon_mismatch": 0, "out_of_domain": dt},
        {"tree": "mc_signal_reco", "context": "signal_reco_pass", "nonfinite": 0,
         "sentinel_on_selected": 0, "invalid_muon_or_minos": sig,
         "in_domain_scalar_muon_mismatch": 0, "out_of_domain": sig},
        {"tree": "mc_truth_denom", "context": "truth", "nonfinite": 0,
         "out_of_domain_informational": 99},                     # truth: informational, no census
        {"tree": "mc_signal_reco", "context": "miss_sentinel", "nonsentinel_miss": 0},
    ]
    census = {"background_out_of_domain": [{"index": i} for i in range(bg)],
              "data_out_of_domain": [{"index": i} for i in range(dt)],
              "signal_reco_pass_out_of_domain": [{"index": i} for i in range(sig)]}
    return checks, census, bg + dt + sig


def domain_receipt(status="PASS", fatal=None, pt_max=30.0, ppar_max=120.0,
                   n_failed=0, superseded=(), non_superseded=(), base_ran=True,
                   drop_structural=False, bg=2, dt=3, sig=4, bound=None):
    """A synthetic g2-domain-validation-v1 receipt dict (as the domain validator would emit)."""
    checks, census, computed = _reco_checks_and_census(bg, dt, sig)
    d = {"receipt_schema": "g2-domain-validation-v1", "file": "/x/e.root",
         "domain": {"pt_max": pt_max, "p_par_max": ppar_max},
         "status": status, "fatal": [] if fatal is None else list(fatal),
         "census": census, "checks": checks,
         "out_of_domain_censused_and_bound": computed if bound is None else bound}
    if not drop_structural:
        d["structural"] = {
            "ran": base_ran, "receipt": "/work/w.json.domain.json.base.json", "exit": 0,
            "n_checks": 50, "n_failed": n_failed,
            "failed_checks": list(superseded) + list(non_superseded),
            "non_superseded_failures": list(non_superseded),
            "superseded_failures": list(superseded),
            "base_receipt_sha256": "3b5c4ae9deadbeef", "base_validator_sha256": "3b5c4ae9",
            "base_validator": "/x/validate_g2_fullevent_smoke.py"}
    return d


def domain_result(parsed=None, ran=True, exit=None, **kw):
    p = parsed if parsed is not None else domain_receipt(**kw)
    ex = (0 if p.get("status") == "PASS" else 1) if exit is None else exit
    return {"ran": ran, "exit": ex, "receipt": "/work/w.json.domain.json",
            "receipt_sha256": "dom_sha", "parsed": p,
            "counts": {"mc_signal_reco": 4073230, "mc_truth_denom": 4073230,
                       "mc_background": 44900, "data": 360123, "nTruthOnlyMisses": 1596619}}


def report(band="MuonResolution", endpoint=1, playlist="1A", observed=None, dr=None):
    return v.build_report(
        root_meta={"path": "/x/e.root", "sha256": "deadbeef", "size_bytes": 123},
        this_validator={"path": "/x/validate_p3f_pet_fullevent.py", "sha256": "v1"},
        domain_validator={"path": "/x/validate_g2_fullevent_domain.py", "sha256": "d1"},
        domain_result=dr if dr is not None else domain_result(),
        band=band, endpoint=endpoint, playlist=playlist,
        observed=observed if observed is not None else good_observed(band, endpoint),
        observed_at_utc="2026-07-19T00:00:00Z")


class Inventory(unittest.TestCase):
    def test_declared_counts(self):
        self.assertEqual((len(v.EXPECTED_BANDS), len(v.EXPECTED_ENDPOINTS),
                          len(v.EXPECTED_PLAYLISTS), v.N_EXPECTED_FILES), (5, 2, 12, 120))

    def test_expected_names(self):
        self.assertEqual(v.EXPECTED_BANDS, ("BeamAngleX", "BeamAngleY", "MuonResolution",
                                            "Muon_Energy_MINERvA", "Muon_Energy_MINOS"))
        self.assertEqual(v.EXPECTED_ENDPOINTS, (0, 1))
        self.assertEqual(v.EXPECTED_PLAYLISTS,
                         ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"))

    def test_all_120_valid(self):
        n = 0
        for b in v.EXPECTED_BANDS:
            for e in v.EXPECTED_ENDPOINTS:
                for p in v.EXPECTED_PLAYLISTS:
                    self.assertEqual(v.assert_inventory(b, str(e), p), (b, e, p)); n += 1
        self.assertEqual(n, 120)

    def test_unknown_band(self):
        with self.assertRaises(ValueError):
            v.assert_inventory("Muon_Energy", 0, "1A")

    def test_wrong_case_band(self):
        with self.assertRaises(ValueError):
            v.assert_inventory("muonresolution", 0, "1A")

    def test_endpoint_range(self):
        for bad in (2, -1, 3):
            with self.assertRaises(ValueError):
                v.assert_inventory("BeamAngleX", bad, "1A")

    def test_non_integer_endpoint(self):
        with self.assertRaises(ValueError):
            v.assert_inventory("BeamAngleX", "x", "1A")

    def test_unknown_playlist(self):
        for bad in ("1H", "2A", "1a"):
            with self.assertRaises(ValueError):
                v.assert_inventory("BeamAngleX", 0, bad)


class ActiveMetadata(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(v.check_active_metadata(good_observed("BeamAngleY", 0), "BeamAngleY", 0)[0])

    def test_wrong_band(self):
        self.assertFalse(v.check_active_metadata(good_observed("BeamAngleY", 0),
                                                 "MuonResolution", 0)[0])

    def test_wrong_index(self):
        self.assertFalse(v.check_active_metadata(good_observed("BeamAngleY", 0), "BeamAngleY", 1)[0])

    def test_not_enabled(self):
        o = good_observed(); o[v.ACTIVE_ENABLED_MARKER] = 0
        self.assertFalse(v.check_active_metadata(o, "MuonResolution", 1)[0])

    def test_not_lateral(self):
        o = good_observed(); o[v.ACTIVE_LATERAL_MARKER] = 0
        self.assertFalse(v.check_active_metadata(o, "MuonResolution", 1)[0])

    def test_cv_control_rejected(self):
        o = {v.ACTIVE_BAND_MARKER: "cv", v.ACTIVE_INDEX_MARKER: 0,
             v.ACTIVE_ENABLED_MARKER: 0, v.ACTIVE_LATERAL_MARKER: 0}
        self.assertFalse(v.check_active_metadata(o, "MuonResolution", 1)[0])


class MigrationCensus(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(v.check_migration_census(good_observed())[0])

    def test_zero_ok(self):
        o = good_observed()
        for k in v.MIGRATION_CENSUS_PARAMS:
            o[k] = 0
        self.assertTrue(v.check_migration_census(o)[0])

    def test_missing_fails(self):
        o = good_observed(); del o["activeUniverseRecoExits"]
        self.assertFalse(v.check_migration_census(o)[0])

    def test_non_integral_fails(self):
        o = good_observed(); o["activeUniverseTruthEntrants"] = 2.5
        self.assertFalse(v.check_migration_census(o)[0])

    def test_negative_fails(self):
        o = good_observed(); o["activeUniverseRecoEntrants"] = -1
        self.assertFalse(v.check_migration_census(o)[0])

    def test_names_match_cpp(self):
        self.assertEqual(v.MIGRATION_CENSUS_PARAMS,
                         ("activeUniverseTruthEntrants", "activeUniverseTruthExits",
                          "activeUniverseRecoEntrants", "activeUniverseRecoExits"))


class DomainResultComposition(unittest.TestCase):
    def test_pass(self):
        self.assertTrue(v.check_domain_result(domain_receipt())[0])

    def test_status_fail(self):
        self.assertFalse(v.check_domain_result(domain_receipt(status="FAIL"))[0])

    def test_fatal_nonempty(self):
        self.assertFalse(v.check_domain_result(domain_receipt(fatal=["boom"]))[0])

    def test_nonsuperseded_base_failure(self):
        d = domain_receipt(n_failed=1, non_superseded=["c_global_count_invariant"])
        self.assertFalse(v.check_domain_result(d)[0])

    def test_superseded_only_passes(self):
        # the KNOWN recovery semantic: only the two reco-muon heuristics fail -> superseded -> PASS
        d = domain_receipt(n_failed=2, superseded=["bkg_reco_muon_valid", "data_reco_muon_valid"])
        self.assertTrue(v.check_domain_result(d)[0])

    def test_superseded_outside_allowed_fails(self):
        d = domain_receipt(n_failed=1, superseded=["some_other_check"])
        self.assertFalse(v.check_domain_result(d)[0])

    def test_wrong_pt_bound(self):
        self.assertFalse(v.check_domain_result(domain_receipt(pt_max=4.5))[0])

    def test_wrong_ppar_bound(self):
        self.assertFalse(v.check_domain_result(domain_receipt(ppar_max=60.0))[0])

    def test_truncated_census_bound_mismatch(self):
        # bound total disagrees with the summed reco out_of_domain counts (census truncated)
        self.assertFalse(v.check_domain_result(domain_receipt(bound=5))[0])   # 2+3+4=9 != 5

    def test_truncated_census_fatal_evidence(self):
        d = domain_receipt(fatal=["background: out-of-domain census truncated (100/158); receipt "
                                  "would not bind every excluded row"])
        ok, _ = v.check_domain_result(d)
        self.assertFalse(ok)

    def test_incomplete_census_list(self):
        d = domain_receipt()
        d["census"]["signal_reco_pass_out_of_domain"] = d["census"]["signal_reco_pass_out_of_domain"][:-1]
        self.assertFalse(v.check_domain_result(d)[0])

    def test_missing_structural(self):
        self.assertFalse(v.check_domain_result(domain_receipt(drop_structural=True))[0])

    def test_base_not_ran(self):
        self.assertFalse(v.check_domain_result(domain_receipt(base_ran=False))[0])

    def test_wrong_schema(self):
        d = domain_receipt(); d["receipt_schema"] = "g2-smoke"
        self.assertFalse(v.check_domain_result(d)[0])


class ReportVerdict(unittest.TestCase):
    def test_all_pass(self):
        payload, verdict = report()
        self.assertTrue(verdict)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertTrue(all(payload["component_verdicts"].values()))
        self.assertIn("domain", payload["component_verdicts"])

    def test_recovery_shape_passes(self):
        # 1D/1E/1F/1P shape: base failed only the superseded reco-muon heuristics; out-of-domain
        # rows censused/bound. Gate-3 PASS.
        dr = domain_result(n_failed=2,
                           superseded=["bkg_reco_muon_valid", "data_reco_muon_valid"],
                           bg=158, dt=468, sig=2017)
        payload, verdict = report(dr=dr)
        self.assertTrue(verdict)
        self.assertEqual(payload["domain_validator"]["out_of_domain_censused_and_bound"], 2643)
        self.assertEqual(payload["base_validator"]["superseded_failures"],
                         ["bkg_reco_muon_valid", "data_reco_muon_valid"])
        self.assertEqual(payload["base_validator"]["non_superseded_failures"], [])

    def test_domain_failure_fails_verdict(self):
        payload, verdict = report(dr=domain_result(status="FAIL", fatal=["x"]))
        self.assertFalse(verdict)
        self.assertFalse(payload["component_verdicts"]["domain"])

    def test_nonsuperseded_base_failure_fails_verdict(self):
        dr = domain_result(status="FAIL", fatal=["structural non-superseded failures"],
                           n_failed=1, non_superseded=["c_global_count_invariant"])
        self.assertFalse(report(dr=dr)[1])

    def test_domain_crash_fails_verdict(self):
        self.assertFalse(report(dr=domain_result(ran=False, exit=2))[1])

    def test_nonzero_domain_exit_fails_even_with_pass_receipt(self):
        payload, verdict = report(dr=domain_result(status="PASS", ran=True, exit=1))
        self.assertFalse(verdict)
        ran = next(c for c in payload["checks"] if c["name"] == "domain:validator_ran")
        self.assertFalse(ran["ok"])
        self.assertFalse(payload["component_verdicts"]["domain"])

    def test_active_mismatch_fails(self):
        payload, verdict = report(observed=good_observed("BeamAngleX", 0))
        self.assertFalse(verdict)
        self.assertFalse(payload["component_verdicts"]["active"])

    def test_census_missing_fails(self):
        o = good_observed(); del o["activeUniverseTruthExits"]
        payload, verdict = report(observed=o)
        self.assertFalse(verdict)
        self.assertFalse(payload["component_verdicts"]["census"])

    def test_inventory_bad_fails(self):
        self.assertFalse(report(playlist="1H")[1])

    def test_payload_binds_both_validators(self):
        payload, _ = report()
        self.assertEqual(payload["receipt_schema"], "p3f-pet-fullevent-validation-v1")
        self.assertEqual(payload["observed_at_utc"], "2026-07-19T00:00:00Z")
        self.assertEqual(payload["root"]["sha256"], "deadbeef")
        self.assertEqual(payload["this_validator"]["sha256"], "v1")
        # domain validator bound
        dv = payload["domain_validator"]
        self.assertEqual(dv["sha256"], "d1")
        self.assertEqual(dv["status"], "PASS")
        self.assertEqual(dv["domain"], {"pt_max": 30.0, "p_par_max": 120.0})
        self.assertEqual(dv["receipt_sha256"], "dom_sha")
        # nested base (smoke) validator bound from the domain receipt structural block
        bv = payload["base_validator"]
        self.assertTrue(bv["path"].endswith("validate_g2_fullevent_smoke.py"))
        self.assertEqual(bv["sha256"], "3b5c4ae9")
        self.assertEqual(bv["receipt_sha256"], "3b5c4ae9deadbeef")
        self.assertEqual(bv["n_checks"], 50)
        self.assertIn("mc_signal_reco", payload["counts"])
        self.assertEqual(payload["inventory"]["n_total_files"], 120)
        self.assertEqual(payload["expected_active"][v.ACTIVE_INDEX_MARKER], 1)
        self.assertEqual(payload["observed_active"][v.ACTIVE_BAND_MARKER], "MuonResolution")


class AtomicWorkReceipt(unittest.TestCase):
    def test_writes_only_to_work_path(self):
        payload, _ = report()
        with tempfile.TemporaryDirectory() as td:
            work = os.path.join(td, "p3f_work.json")
            v.write_work_receipt(work, payload)
            self.assertEqual(os.listdir(td), ["p3f_work.json"])
            with open(work) as f:
                self.assertEqual(json.load(f)["verdict"], "PASS")

    def test_no_publication_on_failure(self):
        payload, verdict = report(playlist="1H")      # FAIL
        self.assertFalse(verdict)
        with tempfile.TemporaryDirectory() as td:
            work = os.path.join(td, "fail.json")
            v.write_work_receipt(work, payload)
            self.assertEqual(os.listdir(td), ["fail.json"])   # only the WORK receipt; nothing published
            with open(work) as f:
                self.assertEqual(json.load(f)["verdict"], "FAIL")

    def test_temp_cleaned(self):
        payload, _ = report()
        with tempfile.TemporaryDirectory() as td:
            v.write_work_receipt(os.path.join(td, "r.json"), payload)
            self.assertEqual([f for f in os.listdir(td) if f.startswith(".p3f_pet_val_")], [])


class SyntaxAndComposition(unittest.TestCase):
    def test_validator_byte_compiles(self):
        path = os.path.join(ND, "pet", "validate_p3f_pet_fullevent.py")
        r = subprocess.run([sys.executable, "-m", "py_compile", path],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_composes_domain_validator_by_default(self):
        self.assertTrue(v.DOMAIN_VALIDATOR_DEFAULT.endswith("validate_g2_fullevent_domain.py"))
        self.assertTrue(os.path.exists(v.DOMAIN_VALIDATOR_DEFAULT))

    def test_smoke_validator_still_referenced_for_forwarding(self):
        self.assertTrue(v.BASE_VALIDATOR_DEFAULT.endswith("validate_g2_fullevent_smoke.py"))
        self.assertTrue(os.path.exists(v.BASE_VALIDATOR_DEFAULT))

    def test_superseded_set_is_exactly_the_two_reco_muon_heuristics(self):
        self.assertEqual(set(v.SUPERSEDED_BASE_CHECKS),
                         {"bkg_reco_muon_valid", "data_reco_muon_valid"})


if __name__ == "__main__":
    unittest.main(verbosity=2)

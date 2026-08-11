#!/usr/bin/env python3
"""REPAIR-4, verifier defect 6a/6c — integration coverage for the resume/receipt contract.

The round-3 suite executed neither shell driver, so every resume, staleness, ordering and
worker-failure behaviour was untested, and the one CLI test that looked like coverage passed
because argparse rejected an argument before the guard it named ever ran (defect 6b).

What this file does differently:

* It drives `p4_check_receipt.py` — a REAL producer/consumer pair — end to end against
  receipts rendered by the LAUNCHER'S OWN `printf` format string, extracted from
  `run_p4_unfold_std.sh` at test time. Nothing here is hand-assembled to match the reader
  (BEN-040 was exactly that inversion, in this chain).
* It asserts the SPECIFIC rejection reason, never merely a nonzero exit, so a test cannot pass
  because something unrelated failed first.
* It uses a fake repo layout so no real 53.8 GB input, no ROOT, and no cluster are needed;
  the merged-hash lookup is stubbed at its seam rather than by rewriting the code under test.

Not covered here, and deliberately: anything requiring PyROOT (`valid_root`, the builder and
the projector's ROOT I/O). Those need the cluster interpreter — see KNOWN_ISSUES #17 and the
Perlmutter ROOT/TF split. This file stays ROOT-free so it runs in CI and on a laptop.
"""
import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import p4_lib as P


def launcher_receipt_format():
    """The produced-receipt format string, read out of the launcher itself."""
    sh = (ND / "run_p4_unfold_std.sh").read_text()
    m = re.search(r"printf '(\{\"tag\":\"%s\",\"mode\":\"produced\".*?\}\\n)'", sh, re.S)
    assert m, "could not extract the launcher's produced-receipt format"
    return m.group(1)


def launcher_surface_command():
    """The launcher's OWN producing-closure derivation, lifted out of the shell source.

    PB2 repair: executed rather than paraphrased. If the launcher ever goes back to writing a
    hand-maintained path list, this stops finding a command to run and the tests that depend on
    it fail loudly instead of quietly testing the helper the launcher no longer calls."""
    sh = (ND / "run_p4_unfold_std.sh").read_text()
    m = re.search(r"SURFACE_JSON=\$\(python3 -c \"\n(.*?)\"\)", sh, re.S)
    assert m, "could not extract the launcher's producing-closure derivation command"
    return m.group(1)


def launcher_surface_json():
    """Run that command exactly as the launcher runs it, and return what it emits."""
    r = subprocess.run([sys.executable, "-c", launcher_surface_command()],
                       capture_output=True, text=True, cwd=str(ND))
    assert r.returncode == 0, f"launcher surface derivation failed: {r.stderr}"
    return json.loads(r.stdout)


def render_receipt(tag, root_sha, merged_sha, central_sha, cfg_hash, bkg_mode,
                   code_rev, unfold_blob, when="2026-08-07T00:00:00Z",
                   surface_blobs=None, schema=None):
    fmt = launcher_receipt_format()
    surface = json.dumps(launcher_surface_json() if surface_blobs is None else surface_blobs,
                         sort_keys=True, separators=(",", ":"))
    schema = P.RECEIPT_SCHEMA_CURRENT if schema is None else schema
    out = subprocess.run(
        ["printf", fmt, tag, str(schema), root_sha, merged_sha, central_sha, cfg_hash, bkg_mode,
         code_rev, unfold_blob, surface, when],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class ReceiptGateIntegration(unittest.TestCase):
    """Executes p4_check_receipt.py as a subprocess, the way the launcher calls it."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)
        self.root = self.d / "endpoint.root"
        self.root.write_bytes(b"pretend-root-payload")
        self.central = self.d / "central.root"
        self.central.write_bytes(b"pretend-central-payload")
        self.merged = self.d / "merged.root"
        self.merged.write_bytes(b"pretend-merged-payload")
        self.root_sha = P.sha256_file(self.root)
        self.central_sha = P.sha256_file(self.central)
        self.merged_sha = "m" * 64
        cfg = P.P4Config(); cfg.validate()
        self.cfg_hash, self.bkg = cfg.hash(), cfg.bkg_mode
        # repair-6b: code_rev is now checked for REACHABILITY in this repo's history, so the
        # fixture must be a real commit. A synthetic sha is exactly what the gate rejects.
        self.code_rev = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ND.parent), text=True).strip()
        self.unfold_blob = "u" * 40

    def tearDown(self):
        self.td.cleanup()

    def _run_gate(self, receipt_path, tag="BeamAngleX_0"):
        """Call the gate with its two external dependencies stubbed at the seam: the central
        product path and the committed-merged-sha lookup. Stubbing the SEAM keeps the gate's
        own logic under test, unlike patching the logic itself."""
        shim = self.d / "shim.py"
        shim.write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import p4_check_receipt as C\n"
            f"C.CEN5 = {str(self.central)!r}\n"
            f"C.committed_merged_sha = lambda p: {self.merged_sha!r}\n"
            f"C.committed_unfold_blob = lambda: {self.unfold_blob!r}\n"
            f"C.current_code_rev = lambda: {self.code_rev!r}\n"
            "sys.argv = ['p4_check_receipt.py', '--receipt', sys.argv[1], '--tag', sys.argv[2],"
            "            '--root', sys.argv[3], '--merged', sys.argv[4]]\n"
            "C.main()\n")
        r = subprocess.run([sys.executable, str(shim), str(receipt_path), tag,
                            str(self.root), str(self.merged)],
                           capture_output=True, text=True, cwd=str(ND))
        return r.returncode, (r.stdout + r.stderr)

    def _write(self, rec, name="e.done"):
        p = self.d / name
        p.write_text(json.dumps(rec))
        return p

    def _good(self, **over):
        vals = dict(tag="BeamAngleX_0", root_sha=self.root_sha, merged_sha=self.merged_sha,
                    central_sha=self.central_sha, cfg_hash=self.cfg_hash, bkg_mode=self.bkg,
                    code_rev=self.code_rev, unfold_blob=self.unfold_blob)
        vals.update(over)
        return render_receipt(**vals)

    # ---------- the happy path must actually pass ----------
    def test_valid_receipt_is_accepted(self):
        """A gate that has never returned OK on real input is unverified in the direction that
        matters (BEN-040). This is that direction."""
        rc, out = self._run_gate(self._write(self._good()))
        self.assertEqual(rc, 0, out)
        self.assertIn("RECEIPT-OK", out)

    # ---------- each rejection names its own reason ----------
    def test_root_drift_rejected_with_reason(self):
        rc, out = self._run_gate(self._write(self._good(root_sha="f" * 64)))
        self.assertEqual(rc, 1)
        self.assertIn("root_sha256 drift", out)

    def test_central_drift_rejected_with_reason(self):
        rc, out = self._run_gate(self._write(self._good(central_sha="f" * 64)))
        self.assertEqual(rc, 1)
        self.assertIn("central5d_sha256 drift", out)

    def test_config_drift_rejected_with_reason(self):
        rc, out = self._run_gate(self._write(self._good(cfg_hash="f" * 64)))
        self.assertEqual(rc, 1)
        self.assertIn("config_hash drift", out)

    def test_footing_drift_rejected_with_reason(self):
        rc, out = self._run_gate(self._write(self._good(bkg_mode="negweight-refined")))
        self.assertEqual(rc, 1)
        self.assertIn("bkg_mode", out)

    def test_stale_code_rev_rejected_with_reason(self):
        """REPAIR-5 self-guard for D2, updated by repair-6b: a code_rev that is not in this
        repository's history must be rejected. (Equality with HEAD was too strict -- it expired
        valid receipts on unrelated commits; see REPAIR6b_CodeRevReachability.)"""
        rc, out = self._run_gate(self._write(self._good(code_rev="0" * 40)))
        self.assertEqual(rc, 1)
        self.assertIn("code_rev", out)
        self.assertIn("not an ancestor of HEAD", out)

    def test_stale_unfold_blob_rejected_with_reason(self):
        """REPAIR-5 self-guard for D2. An endpoint produced by a CHANGED unfold driver must not
        be skipped -- previously the receipt carried no source identity at all."""
        rc, out = self._run_gate(self._write(self._good(unfold_blob="9" * 40)))
        self.assertEqual(rc, 1)
        self.assertIn("unfold driver changed", out)

    def test_receipt_without_source_identity_rejected(self):
        """The pre-repair-5 receipt shape (no unfold_blob) must not validate."""
        rec = self._good(); rec.pop("unfold_blob")
        rc, out = self._run_gate(self._write(rec))
        self.assertEqual(rc, 1)
        self.assertIn("missing required keys", out)

    def test_receipt_for_a_different_endpoint_rejected(self):
        rc, out = self._run_gate(self._write(self._good(tag="Muon_Energy_MINOS_1")))
        self.assertEqual(rc, 1)
        self.assertIn("receipt tag", out)

    def test_incomplete_legacy_receipt_rejected(self):
        """The exact pre-repair shape: no merged/central provenance."""
        rec = self._good()
        legacy = {k: v for k, v in rec.items()
                  if k not in ("merged_sha256", "central5d_sha256")}
        rc, out = self._run_gate(self._write(legacy))
        self.assertEqual(rc, 1)
        self.assertIn("missing required keys", out)

    def test_empty_and_malformed_receipts_rejected(self):
        empty = self.d / "empty.done"; empty.write_text("")
        rc, out = self._run_gate(empty)
        self.assertEqual(rc, 1); self.assertIn("absent or empty", out)
        junk = self.d / "junk.done"; junk.write_text("{not json")
        rc2, out2 = self._run_gate(junk)
        self.assertEqual(rc2, 1); self.assertIn("not valid JSON", out2)

    def test_unexpected_error_reads_as_reject_not_pass(self):
        """A gate must never let an unexpected exception look like success."""
        rec = self._good(); rec["root_sha256"] = None
        rc, out = self._run_gate(self._write(rec))
        self.assertEqual(rc, 1)
        self.assertIn("RECEIPT-REJECT", out)


class PB2ProducingClosureResume(ReceiptGateIntegration):
    """PB2 repair, 2026-08-11 — the closure binding, proven THROUGH THE REAL CLI.

    The verifier's finding was not that `producing_closure`/`check_resume_surface` were wrong.
    They were right and their unit fixtures passed. It was that production never called them:
    the launcher wrote no blob record, the checker compared one path, and the tests exercised
    the helpers directly — so the suite proved a property of two functions that the resume path
    did not use. Every case here therefore goes through `p4_check_receipt.py` as a subprocess,
    against receipts rendered by the launcher's own `printf` format and its own closure command.
    """

    def test_launcher_emits_exactly_the_six_producing_paths(self):
        """The record the launcher actually writes, not a list restated in a test."""
        self.assertEqual(set(launcher_surface_json()), {
            "2d-unfolding/unfold_2d_omnifold_unbinned.py",
            "nd-unfolding/flux_universe.py",
            "nd-unfolding/omnifold_nn_core.py",
            "nd-unfolding/unfold_nd_omnifold_unbinned.py",
            "nd-unfolding/xsec_nd.py",
            "unbinned_unfolding/python/omnifold.py"})

    def test_receipt_carries_the_closure_and_a_declared_schema(self):
        rec = self._good()
        self.assertEqual(rec[P.RECEIPT_SCHEMA_FIELD], P.RECEIPT_SCHEMA_CURRENT)
        self.assertEqual(set(rec[P.RESUME_BLOB_FIELD]), set(launcher_surface_json()))

    def _with_surface(self, mutate):
        s = dict(launcher_surface_json())
        mutate(s)
        return self._write(self._good(surface_blobs=s))

    # ---------- a changed producing module must stale the endpoint ----------
    def test_direct_omnifold_change_stales_the_endpoint(self):
        """`unbinned_unfolding/python/omnifold.py` — imported directly by the unfold driver and
        the module that does the reweighting. Under the pre-repair gate this resumed."""
        p = self._with_surface(lambda s: s.__setitem__(
            "unbinned_unfolding/python/omnifold.py", "0" * 40))
        rc, out = self._run_gate(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("producing-closure path(s) changed", out)
        self.assertIn("unbinned_unfolding/python/omnifold.py", out)

    def test_transitive_nn_core_change_stales_the_endpoint(self):
        """`nd-unfolding/omnifold_nn_core.py` is reachable only at depth 2. A one-level check
        would accept this, which is why the closure is transitive."""
        p = self._with_surface(lambda s: s.__setitem__(
            "nd-unfolding/omnifold_nn_core.py", "0" * 40))
        rc, out = self._run_gate(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("nd-unfolding/omnifold_nn_core.py", out)

    def test_omitted_xsec_nd_stales_the_endpoint(self):
        """Omission, not mutation: a receipt cannot narrow the check by listing fewer paths,
        because the gate derives the closure itself instead of trusting the record's key set."""
        p = self._with_surface(lambda s: s.pop("nd-unfolding/xsec_nd.py"))
        rc, out = self._run_gate(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("omits", out)
        self.assertIn("nd-unfolding/xsec_nd.py", out)

    # ---------- and a NON-producing change must not ----------
    def test_non_producing_module_change_is_still_accepted(self):
        """`p4_project_4d.py` cannot execute while an endpoint is unfolded, so a change to it is
        not evidence about the product. This is the over-rejection half of the contract — the
        failure mode (KNOWN_ISSUES #24) that gets checks switched off — and it is asserted, not
        assumed."""
        p = self._with_surface(lambda s: s.__setitem__(
            "nd-unfolding/p4_project_4d.py", "0" * 40))
        rc, out = self._run_gate(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("RECEIPT-OK", out)

    # ---------- legacy stays bounded and explicit ----------
    def test_genuinely_legacy_receipt_is_grandfathered(self):
        """A receipt from BEFORE the binding existed: no schema, no record. Built by removing
        both fields from a rendered receipt because today's launcher can no longer write one."""
        rec = self._good()
        rec.pop(P.RESUME_BLOB_FIELD); rec.pop(P.RECEIPT_SCHEMA_FIELD)
        rc, out = self._run_gate(self._write(rec))
        self.assertEqual(rc, 0, out)
        self.assertIn("GRANDFATHERED", out)

    def test_current_schema_receipt_without_the_record_is_rejected_not_grandfathered(self):
        """The bound: absence of the field stopped meaning "old" the moment the launcher began
        writing it. A receipt that DECLARES the current schema and omits the record is
        malformed, and must not inherit the grandfather clause."""
        rec = self._good(); rec.pop(P.RESUME_BLOB_FIELD)
        rc, out = self._run_gate(self._write(rec))
        self.assertEqual(rc, 1, out)
        self.assertIn("MALFORMED", out)
        self.assertNotIn("GRANDFATHERED", out)

    def test_a_misstated_schema_is_rejected_not_grandfathered(self):
        for bad in ("2", 99, 1, 0):
            with self.subTest(bad):
                rec = self._good(); rec[P.RECEIPT_SCHEMA_FIELD] = bad
                rec.pop(P.RESUME_BLOB_FIELD)
                rc, out = self._run_gate(self._write(rec))
                self.assertEqual(rc, 1, out)
                self.assertNotIn("GRANDFATHERED", out)


class LauncherWiring(unittest.TestCase):
    """The launcher must USE the gate, and must not be able to report success without a
    receipt. Asserted against the shell source because executing the real launcher needs
    PyROOT, 538 GB of input and Slurm."""

    SH = (ND / "run_p4_unfold_std.sh").read_text()

    def test_skip_path_calls_the_gate(self):
        self.assertIn("p4_check_receipt.py", self.SH)
        i_skip = self.SH.index("receipt validated")
        i_gate = self.SH.index("p4_check_receipt.py")
        self.assertLess(i_gate, i_skip, "the gate must run before the SKIP is announced")

    def test_stale_receipt_is_removed_so_it_cannot_be_reused(self):
        self.assertIn("STALE", self.SH)
        self.assertIn('rm -f "${REC}"', self.SH)

    def test_done_cannot_be_printed_without_a_published_receipt(self):
        i_fail = self.SH.index("receipt publication failed after ROOT publish")
        i_done = self.SH.index('echo "[unfold] DONE ${tag}"')
        self.assertLess(i_fail, i_done,
                        "the receipt-write failure branch must precede the DONE announcement")

    def test_inventory_rejects_extras(self):
        self.assertIn("require_exact_endpoint_tags", self.SH)
        self.assertIn("EXTRA/UNEXPECTED", self.SH)

    def test_legacy_attest_path_is_GONE_not_guarded(self):
        """REPAIR-6. The path stamped CURRENT provenance onto ROOTs an older driver produced.
        It is deleted rather than repaired, so there is no code path that can write a receipt
        whose producer claim was not observed by this launcher."""
        self.assertNotIn("legacy-attested", self.SH)
        self.assertNotIn('mode":"legacy-attested', self.SH)
        # the helper it depended on, and the manifest pointer that only it consumed, are gone
        self.assertNotIn("attest(){", self.SH)
        self.assertNotIn('MANIFEST="', self.SH)

    def test_every_receipt_is_produced_by_this_launcher(self):
        """The replacement for the deleted guard: only one receipt mode can be written."""
        import re
        modes = set(re.findall(r'"mode":"([a-z-]+)"', self.SH))
        self.assertEqual(modes, {"produced"},
                         f"a receipt mode other than 'produced' can still be written: {modes}")

    def test_header_no_longer_claims_byte_reproducibility(self):
        """The header asserted produced ROOTs 'must hash identically to the 2026-07-18 ones'.
        Measured false (KNOWN_ISSUES #24). A stale claim in a header is how the next session
        re-derives a wrong invariant."""
        self.assertNotIn("must hash identically", self.SH)
        self.assertIn("not bit-reproducible", self.SH)

    def test_bkg_mode_is_explicit_and_stamped(self):
        self.assertIn('--bkg-mode "${BKG_MODE}"', self.SH)
        self.assertIn('"bkg_mode":"%s"', self.SH)

    # ---------- PB2: the skip path cannot reach SKIP without the checker ----------
    def test_no_skip_is_reachable_without_the_gate(self):
        """Structural, and stated as a reachability claim rather than a substring one: EVERY
        `return 0` inside unfold_one must be downstream of the gate invocation. The pre-repair
        defect was not that the gate was missing from the file — it was there — but that what it
        checked was narrower than what production could change."""
        body = self.SH[self.SH.index("unfold_one(){"):self.SH.index("declare -A RC")]
        gate = body.index("p4_check_receipt.py")
        for m in re.finditer(r"return 0", body):
            self.assertGreater(m.start(), gate,
                               "a success return precedes the receipt gate — skip is reachable "
                               "without validating the receipt")
        calls = [l for l in body.splitlines()
                 if "p4_check_receipt.py" in l and not l.lstrip().startswith("#")]
        self.assertEqual(len(calls), 1,
                         f"expected exactly one gate invocation, found {len(calls)}: one of them "
                         f"can drift from the other")

    def test_launcher_stamps_the_closure_and_schema_into_every_receipt(self):
        self.assertIn('"surface_blobs":%s', self.SH)
        self.assertIn('"receipt_schema":%s', self.SH)
        self.assertIn('"${SURFACE_JSON}"', self.SH)

    def test_the_closure_is_derived_not_duplicated(self):
        """A path list written out in the launcher would be a second copy to keep in sync with
        p4_lib — the shape of defect this repair exists to remove."""
        self.assertIn("producing_closure_blobs", self.SH)
        for producer in ("unbinned_unfolding/python/omnifold.py", "nd-unfolding/xsec_nd.py",
                         "nd-unfolding/omnifold_nn_core.py"):
            self.assertNotIn(producer, self.SH,
                             f"{producer} is named literally in the launcher; the closure must "
                             f"come from the helper, not from a hand-maintained list")

    def test_launcher_aborts_on_a_degenerate_closure(self):
        """An empty map would bind a receipt to nothing while looking fully populated.

        The launcher's own guard line is EXECUTED here with each degenerate value, not matched as
        a substring: a guard asserted by `assertIn` passes just as happily when its condition is
        inverted."""
        self.assertIn("cannot derive the producing-closure blob map", self.SH)
        m = re.search(r"^(\[\[ -n \"\$\{SURFACE_JSON\}\".*?\n.*?exit 2; \})", self.SH, re.M | re.S)
        self.assertIsNotNone(m, "could not extract the launcher's degenerate-closure guard")
        guard = m.group(1)
        for label, sj, n, want in (("empty string", "", "0", 2),
                                   ("empty object", "{}", "0", 2),
                                   ("one path only", '{"a":"b"}', "1", 2),
                                   ("real six-path map", '{"a":"b"}', "6", 0)):
            with self.subTest(label):
                r = subprocess.run(["bash", "-c", f'SURFACE_JSON={sj!r}\nN_SURFACE={n}\n{guard}\n'],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, want, f"{label}: {r.stdout}{r.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

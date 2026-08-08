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


def render_receipt(tag, root_sha, merged_sha, central_sha, cfg_hash, bkg_mode,
                   code_rev, unfold_blob, when="2026-08-07T00:00:00Z"):
    fmt = launcher_receipt_format()
    out = subprocess.run(
        ["printf", fmt, tag, root_sha, merged_sha, central_sha, cfg_hash, bkg_mode,
         code_rev, unfold_blob, when],
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
        self.code_rev = "c" * 40           # repair-5 (D2): now COMPARED, not merely present
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
        """REPAIR-5 self-guard for D2. Reintroducing the defect means accepting a receipt whose
        code_rev disagrees with HEAD; this asserts the rejection and names it."""
        rc, out = self._run_gate(self._write(self._good(code_rev="0" * 40)))
        self.assertEqual(rc, 1)
        self.assertIn("code_rev", out)
        self.assertIn("different revision", out)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

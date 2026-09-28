"""Controls for the s5p reproduction harness. Each guard is exercised in the direction it acts (it fires on a
bad input) and in the other (it stays silent on a good one); none needs the cluster products or ROOT.

    python3 -m unittest discover -s reproduction/s5p/tests
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import repro_s5p as R  # noqa: E402
import scope as S  # noqa: E402

ROOTS = {"s5p": "/data/s5p", "analysis": "/data/analysis", "s5e": "/data/s5e", "cvmfs": "/cvmfs"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class RootsTests(unittest.TestCase):
    def test_reroots_on_a_component_boundary_only(self):
        r = R.Roots(ROOTS)
        self.assertEqual(r.local("/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/x.root"),
                         Path("/data/analysis/3d-unfolding/x.root"))
        self.assertIsNone(r.local("/pscratch/sd/j/josephrb/MINERvA-OmniFold-s5p/x.npz"))  # a sibling checkout
        self.assertIsNone(r.local("/global/homes/j/josephrb/x"))
        self.assertEqual(r.rebase({"a": ["/pscratch/sd/j/josephrb/s5p-20260926/runs/x_s*.npz", 3]}),
                         {"a": ["/data/s5p/runs/x_s*.npz", 3]})
        self.assertFalse(r.identity())
        self.assertTrue(R.Roots(dict(S.RECORDED_ROOTS)).identity())

    def test_refuses_missing_or_relative_roots(self):
        with self.assertRaises(SystemExit):
            R.Roots({k: v for k, v in ROOTS.items() if k != "s5e"})
        with self.assertRaises(SystemExit):
            R.Roots(dict(ROOTS, s5p="relative/dir"))


class ExtractionTests(unittest.TestCase):
    def test_every_receipt_shape(self):
        h = "a" * 64
        doc = {"x": {"path": "/p/1", "sha256": h}, "npz": "/p/2", "npz_sha256": h,
               "logs": {"docs/l.txt": {"sha256": h, "copy_of": "/p/3"}},
               "products": {"/p/4": h}, "inputs": [{"a": "/p/5", "a_sha256": h, "b": "/p/6", "b_sha256": h}],
               "ignored": {"path": "/p/7", "sha256": None}}
        got = {p for p, _, _ in R.declared_digests(doc)}
        self.assertEqual(got, {"/p/1", "/p/2", "/p/3", "docs/l.txt", "/p/4", "/p/5", "/p/6"})

    def test_the_committed_receipts_declare_every_scoped_product(self):
        paths = {p for rel in S.DIGEST_SOURCES
                 for p, _, _ in R.declared_digests(json.loads((R.REPO / rel).read_text()))}
        for must in ("/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz",
                     "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz",
                     "/pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz",
                     "/pscratch/sd/j/josephrb/s5p-20260926/stage3/f4/D16-nuwro_cv.npz",
                     "/pscratch/sd/j/josephrb/s5p-20260926/stage7/genfig/3d-unfolding/genie/genie_mec_cv_xsec3d.root"):
            self.assertIn(must, paths)


class CompareTests(unittest.TestCase):
    def test_exact_tolerance_and_mismatch(self):
        self.assertEqual(R.compare({"a": [1.0, "x"]}, {"a": [1.0, "x"]}, 1e-12)[0], R.REPRODUCED)
        self.assertEqual(R.compare({"a": 1.0}, {"a": 1.0 + 1e-15}, 1e-12)[0], R.WITHIN_TOL)
        self.assertEqual(R.compare({"a": 1.0}, {"a": 1.0 + 1e-9}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare({"a": 1.0}, {"a": 1.0 + 1e-15}, 0.0)[0], R.MISMATCH)
        self.assertEqual(R.compare({"a": 1}, {"a": 1, "b": 2}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare({"a": None}, {"a": 0.0}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare({"a": True}, {"a": 1}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare([float("nan")], [float("nan")], 0.0)[0], R.REPRODUCED)

    def test_arrays(self):
        x = np.linspace(1, 2, 5)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x.copy()}, 0.0)[0], R.REPRODUCED)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x * (1 + 1e-15)}, 1e-12)[0], R.WITHIN_TOL)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x * (1 + 1e-6)}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x[:4]}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare_arrays({"x": x}, {}, 1e-12)[0], R.MISMATCH)


class OutputGuardTests(unittest.TestCase):
    def test_out_dir_must_be_fresh_and_outside_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "inputs").mkdir()
            with self.assertRaises(SystemExit):
                R.check_out_dir(d / "inputs" / "run", [d / "inputs"])
            with self.assertRaises(SystemExit):
                R.check_out_dir(R.REPO / "scratch-run", [R.REPO])
            (d / "used").mkdir()
            (d / "used" / "x").write_text("1")
            with self.assertRaises(SystemExit):
                R.check_out_dir(d / "used", [d / "inputs"])
            R.check_out_dir(d / "new", [d / "inputs"])  # silent on a good directory


class LogAndPdfTests(unittest.TestCase):
    def test_input_paths(self):
        argv = ["--data", "/a/d.root", "--gen", "GENIE-CV:/b/g.root", "--cov", "/a/c.root:hCov", "--png", "x.png"]
        self.assertEqual(R.input_paths(argv), ["/a/d.root", "/b/g.root", "/a/c.root"])

    def test_log_normalization_drops_only_environment_lines(self):
        want = "table 1\nwrote /rec/dir/x.png\n\n[stderr]\nWarning in <TInterpreter::ReadRootmapFile>: dup\n"
        got = "Info in <TCanvas::Print>: png\ntable 1\nwrote /run/x.png\n"
        self.assertEqual(R.normalize_log(want, None, None), R.normalize_log(got, "/run", "/rec/dir"))
        self.assertNotEqual(R.normalize_log("table 1\n", None, None), R.normalize_log("table 2\n", None, None))
        self.assertNotEqual(R.normalize_log("Error in <X>: bad\n", None, None), [])

    def test_pdf_volatile_fields_only(self):
        base = b"%PDF-1.4\n1 0 obj << /CreationDate (D:20260927) /Producer (m) >> endobj\nstream AAA endstream\n"
        with tempfile.TemporaryDirectory() as d:
            a, b, c = Path(d, "a.pdf"), Path(d, "b.pdf"), Path(d, "c.pdf")
            a.write_bytes(base)
            b.write_bytes(base.replace(b"D:20260927", b"D:20260928"))
            c.write_bytes(base.replace(b"AAA", b"AAB"))
            self.assertEqual(R.compare_pdf(a, a)["mode"], "bitwise")
            self.assertEqual(R.compare_pdf(a, b)["status"], R.REPRODUCED)
            self.assertEqual(R.compare_pdf(a, c)["status"], R.MISMATCH)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        roots = {k: str(self.d / k) for k in ("s5p", "analysis", "s5e", "cvmfs")}
        for r in roots.values():
            Path(r).mkdir()
        self.h = R.Harness({"roots": roots, "out_dir": str(self.d / "out")}, None)
        self.h.prepare_out()

    def tearDown(self):
        self.tmp.cleanup()

    def test_digest_fires_on_change_and_missing_and_is_silent_on_match(self):
        good, bad = self.d / "s5p/good.npz", self.d / "s5p/bad.npz"
        good.write_bytes(b"good")
        bad.write_bytes(b"changed")
        rec = self.d / "receipt.json"
        base = S.RECORDED_ROOTS["s5p"]
        rec.write_text(json.dumps({"x": [{"path": f"{base}/good.npz", "sha256": sha(b"good")},
                                         {"path": f"{base}/bad.npz", "sha256": sha(b"original")},
                                         {"path": f"{base}/gone.npz", "sha256": sha(b"gone")},
                                         {"path": "/nowhere/x", "sha256": sha(b"x")}]}))
        old = S.DIGEST_SOURCES
        S.DIGEST_SOURCES = [str(rec)]
        try:
            self.h.a_digests()
        finally:
            S.DIGEST_SOURCES = old
        st = {r.check.split("/")[-1]: r.status for r in self.h.results}
        self.assertEqual(st, {"good.npz": R.REPRODUCED, "bad.npz": R.MISMATCH, "gone.npz": R.INPUT_MISSING,
                              "x": R.INPUT_MISSING})

    def test_launch_flags_an_import_from_outside_the_checkout(self):
        foreign = self.d / "foreign"
        foreign.mkdir()
        (foreign / "hijack_mod.py").write_text("X = 1\n")
        bad = self.d / "bad_producer.py"
        bad.write_text(f"import sys\nsys.path.insert(0, {str(foreign)!r})\nimport hijack_mod\nprint('ran', hijack_mod.X)\n")
        good = self.d / "good_producer.py"
        good.write_text("import json\nprint('ran')\n")
        rc_bad = self.h.launch("bad", str(bad), [], self.d, self.d / "bad.log")
        rc_good = self.h.launch("good", str(good), [], self.d, self.d / "good.log")
        self.assertEqual((rc_bad, rc_good), (0, 0))
        self.assertEqual(Path(self.d / "good.log").read_text(), "ran\n")  # the launcher prints nothing itself
        flagged = [r.check for r in self.h.results if r.status == R.MISMATCH]
        self.assertEqual(flagged, ["provenance:bad"])
        self.assertIn(str((foreign / "hijack_mod.py").resolve()), self.h.provenance["bad"]["foreign_modules"])

    def test_launch_propagates_a_producer_refusal(self):
        p = self.d / "refuses.py"
        p.write_text("raise SystemExit('refusing to overwrite x')\n")
        self.assertEqual(self.h.launch("refuses", str(p), [], self.d, self.d / "r.log"), 1)
        self.assertIn("refusing to overwrite x", (self.d / "r.log").read_text())

    def test_joint_is_pending_and_never_reproduced_without_terminal_products(self):
        self.h.tier_d()
        self.assertEqual([r.status for r in self.h.results], [R.PENDING])
        self.assertFalse(self.h.results[0].detail["committed_result_present"])

    def test_exit_codes(self):
        self.h.add("x", R.A, R.REPRODUCED)
        self.h.add("j", R.D, R.PENDING)
        self.assertEqual(self.h.write_report(["A", "D"]), 0)
        self.h.add("m", R.B, R.INPUT_MISSING)
        self.assertEqual(self.h.write_report(["A", "B"]), 2)
        self.h.add("bad", R.A, R.MISMATCH)
        self.assertEqual(self.h.write_report(["A", "B"]), 1)
        rep = json.loads((self.h.out / "report.json").read_text())
        self.assertEqual(rep["exit_code"], 1)
        self.assertIn("MISMATCH", (self.h.out / "report.md").read_text())


class ScopeTests(unittest.TestCase):
    def test_the_checkout_carries_the_pinned_receipts(self):
        """Fires when a committed receipt changes under the harness (then scope.py must be re-pinned by review)."""
        for rel, want in S.RECEIPTS.items():
            self.assertEqual(R.sha256(R.REPO / rel), want, rel)

    def test_every_declared_field_and_code_names_a_declared_difference(self):
        for path in S.ENVELOPE_DECLARED_FIELDS.values():
            self.assertIn(path, S.DECLARED_DIFFERENCES)
        for path in S.DECLARED_CODE.values():
            self.assertIn(path, S.DECLARED_DIFFERENCES)


if __name__ == "__main__":
    unittest.main()

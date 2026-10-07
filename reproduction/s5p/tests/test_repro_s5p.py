"""Controls for the s5p reproduction harness. Each guard is exercised in the direction it acts (it fires on a
bad input) and in the other (it stays silent on a good one); none needs the cluster products or ROOT.

    python3 -m unittest discover -s reproduction/s5p/tests
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import repro_s5p as R  # noqa: E402
import scope as S  # noqa: E402

ROOTS = {"s5p": "/data/s5p", "analysis": "/data/analysis", "s5e": "/data/s5e", "cvmfs": "/cvmfs"}
REC = S.RECORDED_ROOTS["s5p"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


class RootsTests(unittest.TestCase):
    def test_reroots_on_a_component_boundary_only(self):
        r = R.Roots(ROOTS)
        self.assertEqual(r.local("/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/x.root"),
                         Path("/data/analysis/3d-unfolding/x.root"))
        self.assertIsNone(r.local("/pscratch/sd/j/josephrb/MINERvA-OmniFold-s5p/x.npz"))  # a sibling checkout
        self.assertIsNone(r.local("/global/homes/j/josephrb/x"))
        self.assertEqual(r.split(f"{REC}/runs/a.npz"), ("s5p", "runs/a.npz"))
        self.assertEqual(r.rebase({"a": [f"{REC}/runs/x_s*.npz", 3]}), {"a": ["/data/s5p/runs/x_s*.npz", 3]})
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
               "code": {"code_root_on_cluster": "/p/tree", "files": {"sub/m.py": h}},
               "ignored": {"path": "/p/7", "sha256": None}}
        got = {p for p, _, _ in R.declared_digests(doc)}
        self.assertEqual(got, {"/p/1", "/p/2", "/p/3", "docs/l.txt", "/p/4", "/p/5", "/p/6", "/p/tree/sub/m.py"})

    def test_every_hex_digest_in_the_committed_receipts_is_extracted_or_classified(self):
        """The static half of the coverage row, on the real receipts (it caught the gen5d code tree)."""
        loose = []
        for rel in S.DIGEST_SOURCES:
            doc = json.loads((R.REPO / rel).read_text())
            files = {v for _, v, _ in R.declared_digests(doc)}
            for trail, v in R.all_hex(doc):
                if v not in files and not any(isinstance(k, str) and k in S.NON_FILE_DIGEST_KEYS for k in trail):
                    loose.append(f"{rel}:{trail}")
        self.assertEqual(loose, [])

    def test_the_committed_receipts_declare_every_scoped_product(self):
        paths = {p for rel in S.DIGEST_SOURCES for p, _, _ in R.declared_digests(json.loads((R.REPO / rel).read_text()))}
        for must in (f"{REC}/gen5d_fluxfix/genie_cv_xsec5d_full.npz", f"{REC}/gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz",
                     f"{REC}/stage3/V/V-s3v.npz", f"{REC}/stage3/f4/D16-nuwro_cv.npz",
                     f"{REC}/stage7/genfig/3d-unfolding/genie/genie_mec_cv_xsec3d.root",
                     f"{REC}/gen5d/code/tree/3d-unfolding/genie/gen_to_xsec5d.py"):
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
        self.assertEqual(R.compare({"a": {"b": 1}}, {"a": None}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare([float("nan")], [float("nan")], 0.0)[0], R.REPRODUCED)
        self.assertEqual(R.compare([1.0], [float("inf")], 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare([float("inf")], [float("-inf")], 1e-12)[0], R.MISMATCH)

    def test_arrays(self):
        x = np.linspace(1, 2, 5)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x.copy()}, 0.0)[0], R.REPRODUCED)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x * (1 + 1e-15)}, 1e-12)[0], R.WITHIN_TOL)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x * (1 + 1e-6)}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare_arrays({"x": x}, {"x": x[:4]}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare_arrays({"x": x}, {}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare_arrays({}, {}, 1e-12)[0], R.MISMATCH)  # nothing compared is not a pass

    def test_arrays_nonfinite_on_one_side_is_a_mismatch(self):
        e = np.array([1.0, 2.0, 3.0])
        for bad in ([1.0, np.nan, 3.0], [1.0, np.inf, 3.0]):
            self.assertEqual(R.compare_arrays({"x": e}, {"x": np.array(bad)}, 1e-12)[0], R.MISMATCH)
        self.assertEqual(R.compare_arrays({"x": np.array([np.inf])}, {"x": np.array([-np.inf])}, 1e-12)[0], R.MISMATCH)
        both = np.array([1.0, np.nan, np.inf])
        self.assertEqual(R.compare_arrays({"x": both}, {"x": both.copy()}, 0.0)[0], R.REPRODUCED)
        near = np.array([1.0 + 1e-15, np.nan, np.inf])
        self.assertEqual(R.compare_arrays({"x": both}, {"x": near}, 1e-12)[0], R.WITHIN_TOL)


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

    def test_recorded_roots_are_forbidden_even_when_relocated(self):
        h = R.Harness({"roots": ROOTS, "out_dir": f"{REC}/runs/mine"}, None)
        with self.assertRaises(SystemExit):
            h.prepare_out()

    def test_the_guard_touches_nothing_under_a_recorded_root(self):
        """A relocated run must make no filesystem access under a recorded root, the guard included."""
        import os
        seen = []
        real_lstat, real_stat = os.lstat, os.stat

        def spy(fn):
            def wrapped(p, *a, **k):
                seen.append(os.fspath(p))
                return fn(p, *a, **k)
            return wrapped
        with tempfile.TemporaryDirectory() as d, mock.patch("os.lstat", spy(real_lstat)), mock.patch("os.stat", spy(real_stat)):
            R.check_out_dir(Path(d) / "new", [Path(d) / "inputs"], R.recorded_roots())
        self.assertTrue(seen)  # the spy saw the guard's own accesses
        self.assertEqual([p for p in seen for r in R.recorded_roots() if R.under(p, r)], [])


class LogPdfTraceTests(unittest.TestCase):
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

    def test_scan_trace_fires_on_a_recorded_root_and_needs_evidence_it_looked(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d, "t.txt")
            t.write_text('1 openat(AT_FDCWD, "/stage/s5p/x.npz", O_RDONLY) = 3\n')
            self.assertEqual(quiet(R.cmd_scan_trace, t, "/stage"), 0)
            t.write_text('1 openat(AT_FDCWD, "/stage/s5p/x.npz", O_RDONLY) = 3\n'
                         f'1 newfstatat(AT_FDCWD, "{REC}/runs/x.npz", {{}}) = 0\n')
            self.assertEqual(quiet(R.cmd_scan_trace, t, "/stage"), 1)
            t.write_text('1 openat(AT_FDCWD, "/usr/lib/libc.so", O_RDONLY) = 3\n')
            self.assertEqual(quiet(R.cmd_scan_trace, t, "/stage"), 2)
            t.write_text('1 openat(AT_FDCWD, "/pscratch/sd/j/josephrb/s5p-20260926-other/x", O_RDONLY) = 3\n'
                         '1 openat(AT_FDCWD, "/stage/x", O_RDONLY) = 3\n')
            self.assertEqual(quiet(R.cmd_scan_trace, t, "/stage"), 0)  # a sibling prefix is not the recorded root


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

    def _digests(self, entries, declared=None):
        rec = self.d / "receipt.json"
        rec.write_text(json.dumps({"x": [{"path": p, "sha256": s} for p, s in entries]}))
        with mock.patch.object(S, "DIGEST_SOURCES", [str(rec)]), \
                mock.patch.object(S, "DECLARED_DIFFERENCES", declared or {}):
            self.h.a_digests()
        return {r.check.rsplit("/", 1)[-1]: r.status for r in self.h.results}

    def test_digest_fires_on_change_and_missing_and_is_silent_on_match(self):
        (self.d / "s5p/good.npz").write_bytes(b"good")
        (self.d / "s5p/bad.npz").write_bytes(b"changed")
        st = self._digests([(f"{REC}/good.npz", sha(b"good")), (f"{REC}/bad.npz", sha(b"original")),
                            (f"{REC}/gone.npz", sha(b"gone")), ("/nowhere/x", sha(b"x"))])
        self.assertEqual(st, {"good.npz": R.REPRODUCED, "bad.npz": R.MISMATCH, "gone.npz": R.INPUT_MISSING,
                              "x": R.INPUT_MISSING})
        self.assertTrue(all(r.basis == R.BASIS_RECORDED for r in self.h.results))

    def test_a_declared_difference_needs_both_digests(self):
        (self.d / "s5p/ck.npz").write_bytes(b"later checkpoint")
        path = f"{REC}/ck.npz"
        right = {path: (sha(b"early"), sha(b"later checkpoint"), "why")}
        self.assertEqual(self._digests([(path, sha(b"early"))], right), {"ck.npz": R.DECLARED})
        self.h.results.clear()
        wrong_obs = {path: (sha(b"early"), sha(b"something else"), "why")}
        self.assertEqual(self._digests([(path, sha(b"early"))], wrong_obs), {"ck.npz": R.MISMATCH})
        self.h.results.clear()
        wrong_rec = {path: (sha(b"other"), sha(b"later checkpoint"), "why")}
        self.assertEqual(self._digests([(path, sha(b"early"))], wrong_rec), {"ck.npz": R.MISMATCH})

    def test_a_producer_difference_is_declared_only_by_scope(self):
        prod = self.d / "producer.py"
        prod.write_text("new = 1\n")
        with mock.patch.dict(S.PRODUCER_FILES, {"producer.py": str(prod)}):
            with mock.patch.object(S, "DECLARED_CODE", {}):
                self.h._producer("producer.py", sha(b"old = 1\n"), "test")
            with mock.patch.object(S, "DECLARED_CODE", {("producer.py", sha(b"old = 1\n")): (sha(b"new = 1\n"), "why")}):
                self.h._producer("producer.py", sha(b"old = 1\n"), "test")
            with mock.patch.object(S, "DECLARED_CODE", {("producer.py", sha(b"old = 1\n")): (sha(b"other"), "why")}):
                self.h._producer("producer.py", sha(b"old = 1\n"), "test")
            self.h._producer("producer.py", sha(b"new = 1\n"), "test")
        self.assertEqual([r.status for r in self.h.results], [R.MISMATCH, R.DECLARED, R.MISMATCH, R.REPRODUCED])

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
        self.assertEqual([r.check for r in self.h.results if r.status == R.MISMATCH], ["provenance:bad"])
        self.assertIn(str((foreign / "hijack_mod.py").resolve()), self.h.provenance["bad"]["foreign_modules"])

    def test_launch_without_an_import_record_is_not_silent(self):
        p = self.d / "exits_hard.py"
        p.write_text("import os\nos._exit(0)\n")
        self.assertEqual(self.h.launch("hard", str(p), [], self.d, self.d / "h.log"), 0)
        self.assertEqual([(r.check, r.status) for r in self.h.results], [("provenance:hard", R.MISMATCH)])

    def test_launch_propagates_a_producer_refusal(self):
        p = self.d / "refuses.py"
        p.write_text("raise SystemExit('refusing to overwrite x')\n")
        self.assertEqual(self.h.launch("refuses", str(p), [], self.d, self.d / "r.log"), 1)
        self.assertIn("refusing to overwrite x", (self.d / "r.log").read_text())

    def test_a_harness_exception_is_an_error_row(self):
        def boom():
            raise KeyError("block")
        self.h.guarded(boom, "envelope", R.B, R.BASIS_REGENERATED)
        self.assertEqual(self.h.results[0].status, R.ERROR)
        self.assertEqual(self.h.exit_code(["A", "B"]), 1)

    def test_joint_is_pending_only_when_the_result_is_absent_from_the_checkout(self):
        with mock.patch.dict(S.JOINT, {"committed_result": "docs/no-such-joint-evaluate.json"}):
            self.h.tier_d()
        self.assertEqual([r.status for r in self.h.results], [R.PENDING])
        self.assertFalse(self.h.results[0].detail["committed_result_present"])

    def test_joint_with_its_products_missing_is_input_missing_and_never_exit_0(self):
        """The committed result is in this checkout; the temp roots have no status files or products."""
        self.h.tier_d()
        self.assertEqual([(r.check, r.status) for r in self.h.results], [("joint:final-status", R.INPUT_MISSING)])
        self.h.add("x", R.A, R.REPRODUCED, R.BASIS_RECORDED)
        self.h.add("y", R.B, R.REPRODUCED, R.BASIS_REGENERATED)
        self.assertEqual(self.h.exit_code(["A", "B", "C", "D"]), 2)

    def _status_files(self, B=None):
        ev = json.loads((R.REPO / S.JOINT["committed_result"]).read_text())
        v = json.loads((R.REPO / S.JOINT["v_receipt"]).read_text())["sha256"]
        d = self.d / "s5p/runs/prod/status"
        d.mkdir(parents=True)
        for n in S.JOINT["nulls"]:
            st = {"null": n, "B": (B or {}).get(n, ev["decisions"][f"{n}:total"]["B"]), "stop": True,
                  "design_sha256": S.RECEIPTS[S.JOINT["design"]], "v_sha256": v}
            (d / f"{n}-final.json").write_text(json.dumps(st))
        return ev

    def _counted_pins(self, ev, drop=0):
        cal = {f"s5p:runs/prod/cal/{n}/cal_{n}_s{i}.npz": {} for n in S.JOINT["nulls"]
               for i in range(ev["decisions"][f"{n}:total"]["B"])}
        pw = {f"s5p:runs/prod/pow/{k}/pow_{k}_s{i}.npz": {} for k, e in ev["power"].items() if k != "levels"
              for i in range(e["n"])}
        for k in list(cal)[:drop]:
            del cal[k]
        return {"measured_utc": "t", "groups": {"joint calibration ensembles (final B; partials excluded)": cal,
                                                "joint power ensembles (partials excluded)": pw}}

    def test_receipt_identities_fire_on_a_wrong_count_and_are_silent_on_the_committed_ones(self):
        ev = self._status_files()
        self.h.pins = self._counted_pins(ev)
        self.h.d_receipt_identities()
        self.h.pins = self._counted_pins(ev, drop=1)  # one calibration product fewer than the final B
        self.h.d_receipt_identities()
        self.assertEqual([r.status for r in self.h.results], [R.REPRODUCED, R.MISMATCH])
        self.assertEqual([d["at"] for d in self.h.results[1].detail["diffs"]],
                         [f".B:{S.JOINT['nulls'][0]} (status vs lane-pinned products)"])
        self.assertIn(S.RECEIPTS[S.JOINT["design"]], self.h.compared["design"])

    def test_receipt_identities_fire_on_a_status_b_that_differs_from_the_evaluated_b(self):
        self._status_files(B={"NuWro_21_09": 1750})
        self.h.d_receipt_identities()
        self.assertEqual(self.h.results[0].status, R.MISMATCH)

    def test_seed_states_copy_reverts_to_the_recorded_original(self):
        self.h.d_seed_states_copy()
        with mock.patch.dict(S.JOINT, {"seed_states_log_prefix": "/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/"}):
            self.h.d_seed_states_copy()
        self.assertEqual([r.status for r in self.h.results], [R.REPRODUCED, R.MISMATCH])
        self.assertEqual(self.h.results[0].detail["prefixed_values"], self.h.results[0].detail["tasks"])

    def test_the_independent_report_is_recorded_by_identity_and_never_graded(self):
        rep = self.d / "compare.json"
        rep.write_text('{"verdict": "DISAGREE"}')  # the verdict is never read: only the identity is checked
        self.h.config["joint"] = {"independent_compare": str(rep)}
        with mock.patch.dict(S.JOINT, {"independent_compare_sha256": sha(rep.read_bytes())}):
            self.h.d_independent()
        self.h.d_independent()  # the real pinned digest: a different report at the route
        self.h.config["joint"] = {"independent_compare": str(self.d / "absent.json")}
        self.h.d_independent()
        self.assertEqual([r.status for r in self.h.results], [R.INFO, R.MISMATCH, R.INPUT_MISSING])

    def test_pin_extend_copies_the_old_groups_verbatim_and_measures_only_the_new(self):
        (self.d / "s5p/old.npz").write_bytes(b"old bytes")
        (self.d / "s5p/new.npz").write_bytes(b"new bytes")
        old = self.d / "old-pins.json"
        old.write_text(json.dumps({"measured_utc": "2026-09-28T00:00:00+00:00", "host": "h0",
                                   "groups": {"old": {"s5p:old.npz": {"sha256": "f" * 64, "bytes": 1}}}}))
        out = self.d / "new-pins.json"
        with mock.patch.object(S, "UNRECORDED_INPUT_GLOBS", {"old": ["s5p:old.npz"], "new": ["s5p:new.npz"]}):
            quiet(R.cmd_pin, self.h.config, out, old)
            doc = json.loads(out.read_text())
            self.assertEqual(doc["groups"]["old"], {"s5p:old.npz": {"sha256": "f" * 64, "bytes": 1}})  # not re-measured
            self.assertEqual(doc["groups"]["new"]["s5p:new.npz"]["sha256"], sha(b"new bytes"))
            self.assertEqual((doc["extends"]["groups"], doc["extends"]["sha256"]), (["old"], sha(old.read_bytes())))
            self.assertEqual(R.pin_measured_utc(doc, "old"), "2026-09-28T00:00:00+00:00")
            self.assertEqual(R.pin_measured_utc(doc, "new"), doc["measured_utc"])
            with self.assertRaises(SystemExit):  # never extend an extension
                quiet(R.cmd_pin, self.h.config, self.d / "third.json", out)
        with mock.patch.object(S, "UNRECORDED_INPUT_GLOBS", {"new": ["s5p:new.npz"]}):
            with self.assertRaises(SystemExit):  # the old file pins a group the scope no longer declares
                quiet(R.cmd_pin, self.h.config, self.d / "stale.json", old)

    def test_exit_codes(self):
        h = self.h
        h.add("x", R.A, R.REPRODUCED, R.BASIS_RECORDED)
        h.add("y", R.B, R.REPRODUCED, R.BASIS_REGENERATED)
        h.add("dd", R.A, R.DECLARED, R.BASIS_RECORDED, expected="a", observed="b", why="w")
        self.assertEqual(h.exit_code(["A", "B", "D"]), 2)    # tier D ran without a reproduced replay
        h.add("joint:replay", R.D, R.REPRODUCED, R.BASIS_JOINT)
        h.add("joint:independent-verification", R.D, R.INFO, R.BASIS_JOINT)
        h.add("joint:figures", R.D, R.PENDING, R.BASIS_JOINT)
        self.assertEqual(h.exit_code(["A", "B", "D"]), 0)     # D's two declared non-grades
        self.assertEqual(h.exit_code(["A", "B"]), 2)          # D not run is not a pass
        h.add("joint:replay-labels", R.D, R.PENDING, R.BASIS_JOINT)
        self.assertEqual(h.exit_code(["A", "B", "D"]), 2)     # any other non-passing D row
        h.results.pop()
        self.assertEqual(h.exit_code(["C", "D"]), 2)          # A and B not run is not a pass
        self.assertEqual(h.exit_code(["A"]), 2)
        h.add("n", R.A, R.NOT_RUN, R.BASIS_LANE)
        self.assertEqual(h.exit_code(["A", "B"]), 2)          # NOT_RUN in A/B never counts as reproduced
        h.results.pop()
        h.add("i", R.B, R.INFO, R.BASIS_CODE)
        self.assertEqual(h.exit_code(["A", "B"]), 2)
        h.results.pop()
        h.add("jm", R.D, R.MISMATCH, R.BASIS_JOINT)
        self.assertEqual(h.exit_code(["A", "B", "D"]), 1)
        self.assertEqual(quiet(h.write_report, ["A", "B", "D"]), 1)
        rep = json.loads((h.out / "report.json").read_text())
        self.assertEqual((rep["exit_code"], len(rep["declared_differences"])), (1, 1))

    def test_report_separates_declared_lane_and_exact(self):
        h = self.h
        h.pins = {"measured_utc": "2026-09-28T21:56:37+00:00", "host": "h", "groups": {"g": {"s5p:a": {}}}}
        h.add("digest:/a", R.A, R.REPRODUCED, R.BASIS_RECORDED)
        h.add("pin:s5p:a", R.A, R.REPRODUCED, R.BASIS_LANE, group="g")
        h.add("digest:/b", R.A, R.DECLARED, R.BASIS_RECORDED, expected="r" * 64, observed="o" * 64, why="the reason")
        h.add("sigma:x", R.A, R.WITHIN_TOL, R.BASIS_RECOMPUTED, diffs=[{"rel": 1e-16}])
        quiet(h.write_report, ["A", "B"])
        md = (h.out / "report.md").read_text()
        decl = md.split("## Declared differences")[1].split("## Within tolerance")[0]
        self.assertIn("`digest:/b`", decl)
        self.assertIn("recorded `" + "r" * 64, decl)
        self.assertIn("the reason", decl)
        self.assertNotIn("digest:/a", decl)
        lane = md.split("## Newly recorded digests")[1].split("## Not run")[0]
        self.assertIn("NOT historical provenance", md.split("## Newly recorded digests")[1].splitlines()[0])
        self.assertIn("- g:", lane)
        exact = md.split("## Exact matches, by basis")[1]
        self.assertIn(f"### {R.BASIS_RECORDED} (1)", exact)
        self.assertIn(f"### {R.BASIS_LANE} (1)", exact)
        self.assertNotIn("digest:/b", exact)
        self.assertNotIn("sigma:x", exact)

    def test_stage_copies_the_declared_inventory_only(self):
        (self.d / "s5p/sub").mkdir()
        (self.d / "s5p/sub/rec.npz").write_bytes(b"recorded")
        (self.d / "s5p/sub/pinned.npz").write_bytes(b"pinned")
        (self.d / "s5p/sub/other.npz").write_bytes(b"undeclared")
        rec = self.d / "receipt.json"
        rec.write_text(json.dumps({"p": {"path": f"{REC}/sub/rec.npz", "sha256": sha(b"recorded")},
                                   "q": {"path": f"{REC}/sub/gone.npz", "sha256": sha(b"gone")}}))
        pins = {"groups": {"g": {"s5p:sub/pinned.npz": {"sha256": sha(b"pinned")}}}}
        to = self.d / "staging"
        with mock.patch.object(S, "DIGEST_SOURCES", [str(rec)]):
            self.assertEqual(quiet(R.cmd_stage, self.h.config, pins, to), 0)
        man = json.loads((to / "staging-manifest.json").read_text())
        self.assertEqual(sorted(f["rel"] for f in man["files"]), ["sub/pinned.npz", "sub/rec.npz"])
        self.assertEqual(man["absent_at_source"], ["s5p:sub/gone.npz"])
        self.assertFalse((to / "s5p/sub/other.npz").exists())
        self.assertEqual((to / "s5p/sub/rec.npz").read_bytes(), b"recorded")
        with self.assertRaises(SystemExit):  # never over an existing staging tree
            quiet(R.cmd_stage, self.h.config, pins, to)


class ScopeTests(unittest.TestCase):
    def test_the_checkout_carries_the_pinned_receipts(self):
        """Fires when a committed receipt changes under the harness (then scope.py must be re-pinned by review)."""
        for rel, want in S.RECEIPTS.items():
            self.assertEqual(R.sha256(R.REPO / rel), want, rel)

    def test_the_joint_pin_groups_are_the_frozen_designs_inputs_and_exclude_the_recovery(self):
        design = json.loads((R.REPO / S.JOINT["design"]).read_text())
        r = R.Roots(dict(S.RECORDED_ROOTS))
        as_spec = lambda p: ":".join(r.split(p))  # noqa: E731
        groups = S.UNRECORDED_INPUT_GLOBS
        self.assertEqual(sorted(groups["joint calibration ensembles (final B; partials excluded)"]),
                         sorted(as_spec(n["calibration_glob"]) for n in design["nulls"].values()))
        self.assertEqual(sorted(groups["joint power ensembles (partials excluded)"]),
                         sorted(as_spec(p["glob"]) for p in design["power"].values()))
        self.assertEqual(sorted(groups["joint sequential-calibration final status"]),
                         sorted(as_spec(n["calibration_n"]["sequential_status"]) for n in design["nulls"].values()))
        self.assertEqual([s for v in groups.values() for s in v if s.startswith("s5p:recovery")], [])

    def test_the_committed_pins_extend_the_20260928_pins_verbatim_and_count_the_evaluated_ensembles(self):
        pins = json.loads((R.REPO / S.PINS_FILE).read_text())
        old_path = R.REPO / pins["extends"]["path"]
        old = json.loads(old_path.read_text())
        self.assertEqual(pins["extends"]["sha256"], R.sha256(old_path))
        self.assertEqual(sorted(pins["extends"]["groups"]), sorted(old["groups"]))
        for g in old["groups"]:
            self.assertEqual(pins["groups"][g], old["groups"][g], g)
        self.assertEqual(sorted(pins["groups"]), sorted(S.UNRECORDED_INPUT_GLOBS))
        ev = json.loads((R.REPO / S.JOINT["committed_result"]).read_text())
        cal = pins["groups"]["joint calibration ensembles (final B; partials excluded)"]
        for n in S.JOINT["nulls"]:
            self.assertEqual(sum(s.startswith(f"s5p:runs/prod/cal/{n}/") for s in cal), ev["decisions"][f"{n}:total"]["B"], n)
        pw = pins["groups"]["joint power ensembles (partials excluded)"]
        for k, e in ev["power"].items():
            if k != "levels":
                self.assertEqual(sum(s.startswith(f"s5p:runs/prod/pow/{k}/") for s in pw), e["n"], k)
        self.assertFalse([s for g in pins["groups"].values() for s in g if ".partial" in s or s.startswith("s5p:recovery")])

    def test_exactly_seven_declared_differences_each_with_both_digests(self):
        self.assertEqual(S.N_DECLARED, 7)
        for rec, obs, why in S.DECLARED_DIFFERENCES.values():
            self.assertTrue(R.is_hex64(rec) and R.is_hex64(obs) and rec != obs and why)
        for (_, rec), (obs, why) in S.DECLARED_CODE.items():
            self.assertTrue(R.is_hex64(rec) and R.is_hex64(obs) and rec != obs and why)
        for path in S.ENVELOPE_DECLARED_FIELDS.values():
            self.assertIn(path, S.DECLARED_DIFFERENCES)


if __name__ == "__main__":
    unittest.main()

"""Controls for COVFIX PG's slot-1 verification (state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md, approved,
with the director's rulings): pg_verify.py (members-check, tool-check, trace-check), the record builder's tarball
member listing, and run_gevgen_v3.sh's open-trace prefix. No GENIE, ROOT, CVMFS or real strace is used.

Run: python3 -B -m pytest -q nd-unfolding/tests/test_pg_verify.py
"""
import hashlib
import importlib.util
import io
import json
import re
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
GENIE = REPO / "3d-unfolding" / "genie"
RECORD_DIR = REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
sys.path.insert(1, str(GENIE))
import pg_verify as V  # noqa: E402

_spec = importlib.util.spec_from_file_location("build_record", RECORD_DIR / "build_record.py")
BR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BR)
F1_RUN = subprocess.run(["git", "-C", os.environ.get("PG_GIT_ROOT") or str(REPO), "show",   # a sandbox has no git
                         "54a5c71b7^:3d-unfolding/genie/run_gevgen_v3.sh"],
                        capture_output=True, text=True, check=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgv-", dir="/tmp")))
        self.addCleanup(self.clean)

    def clean(self):
        for d, _, _ in os.walk(self.tmp):
            os.chmod(d, 0o755)
        shutil.rmtree(self.tmp, ignore_errors=True)


# ------------------------------------------------------------------------------------------------ members, the listing

def make_tar(path, entries):
    """entries: [(name, kind, data_or_target)] with kind file, dir, sym or hard."""
    with tarfile.open(path, "w:bz2") as tf:
        for name, kind, x in entries:
            ti = tarfile.TarInfo(name)
            if kind == "file":
                ti.size = len(x)
                ti.mode = 0o644
                tf.addfile(ti, io.BytesIO(x))
                continue
            ti.type = {"dir": tarfile.DIRTYPE, "sym": tarfile.SYMTYPE, "hard": tarfile.LNKTYPE,
                       "fifo": tarfile.FIFOTYPE}[kind]
            ti.mode = 0o755
            if kind in ("sym", "hard"):
                ti.linkname = x
            tf.addfile(ti)


GOOD = [("genie_xsec/v3_04_00", "dir", None),                                       # the real shape: no container member
        ("genie_xsec/v3_04_00/NULL", "dir", None), ("genie_xsec/v3_04_00/NULL/Q", "dir", None),
        ("genie_xsec/v3_04_00/NULL/Q/data", "dir", None),
        ("genie_xsec/v3_04_00/NULL/Q/data/gxspl-NUsmall.xml", "file", b"<spl/>\n"),
        ("genie_xsec/v3_04_00/NULL/Q/data/gxspl-FNALsmall.xml", "sym", "gxspl-NUsmall.xml"),
        ("genie_xsec/v3_04_00/NULL/Q/data/README", "file", b"version v3_04_00 qualifier Q\n")]


class Members(Tmp):
    def test_listing_records_types_shas_and_link_targets(self):
        make_tar(self.tmp / "t.tar.bz2", GOOD)
        m = BR.members(str(self.tmp / "t.tar.bz2"))
        self.assertEqual(m["genie_xsec/v3_04_00/NULL/Q/data/gxspl-NUsmall.xml"]["sha256"], sha(b"<spl/>\n"))
        self.assertEqual(m["genie_xsec/v3_04_00/NULL/Q/data/gxspl-FNALsmall.xml"],
                         {"type": "symlink", "target": "gxspl-NUsmall.xml", "mode": "0o755"})
        self.assertEqual(m["genie_xsec/v3_04_00"]["type"], "dir")
        self.assertNotIn("genie_xsec", m)

    def test_listing_refusals(self):
        for i, bad in enumerate(([("/abs", "file", b"x")], [("a/../b", "file", b"x")],
                                 [("a", "dir", None), ("a/l", "sym", "../../etc/passwd")],
                                 [("a", "dir", None), ("a/l", "sym", "/etc/passwd")],
                                 [("a/h", "hard", "nowhere")], [("a/f", "fifo", None)],
                                 [("a", "file", b"x"), ("a", "file", b"y")])):
            with self.subTest(i):
                make_tar(self.tmp / f"b{i}.tar.bz2", bad)
                with self.assertRaises(BR.RecordError):
                    BR.members(str(self.tmp / f"b{i}.tar.bz2"))
        make_tar(self.tmp / "ok.tar.bz2", [("a", "dir", None), ("a/b", "dir", None), ("a/b/l", "sym", "../x")])
        self.assertEqual(BR.members(str(self.tmp / "ok.tar.bz2"))["a/b/l"]["target"], "../x")   # inside the tree

    def install(self):
        make_tar(self.tmp / "t.tar.bz2", GOOD)
        root = self.tmp / "products"
        root.mkdir()
        with tarfile.open(self.tmp / "t.tar.bz2") as tf:
            tf.extractall(root)
        for d, dirs, files in os.walk(root / "genie_xsec"):
            for f in files:
                if not os.path.islink(os.path.join(d, f)):
                    os.chmod(os.path.join(d, f), 0o444)
            os.chmod(d, 0o555)
        (root / ".upsfiles").mkdir()
        (root / ".upsfiles/dbconfig").write_text("db\n")
        os.chmod(root / ".upsfiles/dbconfig", 0o444)
        os.chmod(root / ".upsfiles", 0o555)
        return root, BR.members(str(self.tmp / "t.tar.bz2"))

    def test_members_check(self):
        root, m = self.install()
        self.assertEqual(V.members_check(str(root), m), [])
        data = root / "genie_xsec/v3_04_00/NULL/Q/data"
        for change, want in (("extra", "members-extra: "), ("missing", "members-missing: "), ("bytes", "members-sha: "),
                             ("writable", "members-writable: "), ("retarget", "members-link: "), ("type", "members-type: ")):
            with self.subTest(change):
                self.clean()
                self.tmp.mkdir(parents=True)
                root, m = self.install()
                os.chmod(data, 0o755)
                f = data / "README"
                if change == "extra":
                    (data / "ModelConfiguration.xml").write_text("x")
                elif change == "missing":
                    os.chmod(f, 0o644); f.unlink()
                elif change == "bytes":
                    os.chmod(f, 0o644); f.write_text("other\n"); os.chmod(f, 0o444)
                elif change == "writable":
                    os.chmod(f, 0o644)
                elif change == "retarget":
                    (data / "gxspl-FNALsmall.xml").unlink(); (data / "gxspl-FNALsmall.xml").symlink_to("README")
                elif change == "type":
                    os.chmod(f, 0o644); f.unlink(); f.mkdir()
                os.chmod(data, 0o555)
                self.assertTrue(any(p.startswith(want) for p in V.members_check(str(root), m)), V.members_check(str(root), m))


# ---------------------------------------------------------------------------------------------------------- tool-check

FAKE_STRACE = r'''#!/bin/sh
# a stand-in for strace: -f -q -e SET -o OUT CMD ARG; writes one open of ARG, as strace would
while [ "$1" != "-o" ]; do shift; done; out=$2; shift 2
"$@" > /dev/null; rc=$?
MODE
exit $rc
'''
MODES = {"good": 'printf \'4242 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n4242 +++ exited with 0 +++\\n\' "$2" > "$out"',
         "no-open": 'printf \'4242 +++ exited with 0 +++\\n\' > "$out"',
         "killed": 'printf \'4242 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n4242 +++ killed by SIGKILL +++\\n\' "$2" > "$out"',
         "truncated": 'printf \'4242 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n4242 +++ exited with 0 +++\' "$2" > "$out"',
         "empty": ': > "$out"', "none": ':',
         "rc": 'printf \'4242 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n4242 +++ exited with 0 +++\\n\' "$2" > "$out"; exit 3'}


def fd_farm(d, target):
    """A stand-in for /proc/self/fd on macOS, which cannot exec /dev/fd/N: a link per descriptor number to target.
    Real descriptor execution is a Linux fact, exercised on the node by the probe's own strace self-test."""
    d.mkdir(exist_ok=True)
    for n in range(3, 256):
        q = d / str(n)
        if q.is_symlink():
            q.unlink()
        q.symlink_to(target)
    return str(d)


class ToolCheck(Tmp):
    def tool(self, mode):
        p = self.tmp / f"strace-{mode}"
        p.write_text(FAKE_STRACE.replace("MODE", MODES[mode]))
        p.chmod(0o755)
        return p

    def run_check(self, path, pin, self_test=True):
        out = io.StringIO()
        import contextlib
        orig = V.FD_DIR
        if not os.path.isdir("/proc/self/fd") and Path(path).exists():
            V.FD_DIR = fd_farm(self.tmp / "fd", Path(path).resolve())
        try:
            with contextlib.redirect_stdout(out):
                rc = V.main(["tool-check", "--path", str(path), "--sha256", pin] + (["--self-test"] if self_test else []))
        finally:
            V.FD_DIR = orig
        return rc, json.loads(out.getvalue())

    def test_pin_and_self_test(self):
        p = self.tool("good")
        rc, rec = self.run_check(p, sha(p.read_bytes()))
        self.assertEqual((rc, rec["problems"]), (0, []))
        rc, rec = self.run_check(p, "0" * 64)
        self.assertEqual(rc, 1)
        self.assertIn("tool-sha: the sha256 differs from the pin", rec["problems"])
        for mode, want in (("no-open", "the self-test's open is not in the trace"), ("killed", "was killed"),
                           ("truncated", "last line is truncated"), ("empty", "the trace is empty"),
                           ("none", "the trace is empty"), ("rc", "strace exited 3")):
            with self.subTest(mode):
                p = self.tool(mode)
                rc, rec = self.run_check(p, sha(p.read_bytes()))
                self.assertEqual(rc, 1)
                self.assertTrue(any(want in x for x in rec["problems"]), rec["problems"])

    def test_a_link_or_missing_tool_is_refused(self):
        p = self.tool("good")
        (self.tmp / "link").symlink_to(p)
        self.assertEqual(self.run_check(self.tmp / "link", sha(p.read_bytes()))[0], 1)
        self.assertEqual(self.run_check(self.tmp / "nothing", "0" * 64)[0], 1)

    def test_the_hashed_descriptor_is_the_executed_one(self):
        p = self.tool("good")
        seen = []
        orig = V.subprocess.run

        def spy(argv, **kw):
            seen.append((argv[0], kw.get("pass_fds")))
            return orig(argv, **kw)
        V.subprocess.run = spy
        try:
            self.assertEqual(self.run_check(p, sha(p.read_bytes()))[0], 0)
        finally:
            V.subprocess.run = orig
        exe, fds = seen[0]
        self.assertEqual(exe.rsplit("/", 1)[1], str(fds[0]))                     # the descriptor that was hashed


# --------------------------------------------------------------------------------------------------------- trace-check

class Trace(Tmp):
    """A stub CVMFS repository with a genie product and a ROOT product, a private product and a W."""

    def setUp(self):
        super().setUp()
        t = self.tmp
        self.repo = t / "cvmfs"
        self.genie = self.repo / "products/genie/v3_04_00"
        self.rootp = self.repo / "products/root/v6_22_08d"
        self.priv = t / "products"
        self.W = t / "Wgenie"                      # a W whose own path contains "genie"
        cfg = self.genie / "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"
        lib = self.genie / "Linux64bit+3.10-2.17-e20-prof/lib"
        for d in (cfg / "G21_11a", cfg / "G18_01a", lib, self.genie / "Linux64bit+3.10-2.17-e20-prof/bin",
                  self.rootp / "etc", self.priv / "genie_xsec/data", self.W / "splines"):
            d.mkdir(parents=True)
        self.files = {}
        C = "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"
        for rel in (f"{C}/G21_11a/ModelConfiguration.xml", f"{C}/G21_11a/EventGenerator.xml",
                    f"{C}/G21_11a/TuneGeneratorList.xml", f"{C}/master_config.xml", f"{C}/SuSAv2MECPXSec.xml",
                    "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG-3.04.00.so", f"{C}/CommonParam.xml",
                    f"{C}/G18_01a/CommonParam.xml", "Linux64bit+3.10-2.17-e20-prof/bin/gevgen",
                    "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.rootmap"):
            (self.genie / rel).write_text(rel)
            self.files[rel] = str(self.genie / rel)
        (lib / "libGFwEG.so").symlink_to("libGFwEG-3.04.00.so")
        (self.rootp / "etc/system.rootrc").write_text("rootrc")
        self.spline = self.W / "splines/G21_11a_00_000_CH.xml.gz"
        self.spline.write_bytes(b"spline")
        (self.W / "flux.root").write_bytes(b"flux")
        self.manifest = {"genie/v3_04_00/" + k: {"type": "file", "sha256": sha(Path(v).read_bytes())}
                         for k, v in self.files.items()}
        self.manifest["genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.so"] = {
            "type": "symlink", "target": "libGFwEG-3.04.00.so"}
        # the tune's own directory, so GENIE walks it (a custom tune's list); Round9 removes it, as for G21_11a_00_000
        self.manifest[f"genie/v3_04_00/{C}/G21_11a/G21_11a_00_000"] = {"type": "dir", "mode": "0o755"}
        self.record = {"tunes": {"G21_11a_00_000": {
            "model_configuration": f"{C}/G21_11a/ModelConfiguration.xml", "event_generator": f"{C}/G21_11a/EventGenerator.xml",
            "tune_generator_list": f"{C}/G21_11a/TuneGeneratorList.xml",
            "ccqe": {"registry": {"file": f"{C}/SuSAv2MECPXSec.xml"}},
            "2p2h": {"registry": {"file": f"{C}/SuSAv2MECPXSec.xml"}},
            "search_dirs": [f"{C}/G21_11a/G21_11a_00_000", f"{C}/G21_11a", C]}}}
        self.private = {}
        self.xdata = str(self.priv / "genie_xsec/data")
        self.C = C

    def search_list(self, tuned=True):
        """GENIE R-3_04_00's XML search list (XmlParserUtils GetXMLPathList): GXMLPATH, the tune's and its CMC
        directory once the tune is configured, $GENIE/config, then $GENIE/src/Tools/Flux/GNuMINtuple."""
        cfg = f"{self.genie}/{self.C}"
        own = [f"{cfg}/G21_11a/G21_11a_00_000"] if getattr(self, "own_dir", True) else []   # only a custom tune's
        mid = own + [f"{cfg}/G21_11a"] if tuned else []
        return [self.xdata] + mid + [cfg, f"{self.genie}/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/src/Tools/Flux/GNuMINtuple"]

    def xml(self, path, pid=100, tuned=True, recheck=True, fd=4):
        """The real lookup of one XML file: GetXMLFilePath's access(F_OK) walk to the first directory that has it,
        AlgConfigPool's AccessPathName of the chosen path, then libxml2's open."""
        d, b = path.rsplit("/", 1)
        out = []
        for x in self.search_list(tuned):
            if x == d:
                out.append(f'{pid} access("{path}", F_OK) = 0')
                break
            out.append(f'{pid} access("{x}/{b}", F_OK) = -1 ENOENT (No such file or directory)')
        else:
            raise AssertionError(f"{path} is not on GENIE's list")
        if recheck:
            out.append(f'{pid} access("{path}", F_OK) = 0')
        return out + [f'{pid} openat(AT_FDCWD, "{path}", O_RDONLY) = {fd}']

    def good_lines(self):
        g, C = self.genie, self.C
        return ([f'100 execve("{g}/Linux64bit+3.10-2.17-e20-prof/bin/gevgen", ["gevgen", "-n", "1"], 0x7ffd /* 40 vars */) = 0',
                 f'100 openat(AT_FDCWD, "{self.spline}", O_RDONLY) = 3']
                + self.xml(f"{g}/{C}/G21_11a/ModelConfiguration.xml")
                + self.xml(f"{g}/{C}/G21_11a/EventGenerator.xml")
                + self.xml(f"{g}/{C}/G21_11a/TuneGeneratorList.xml")
                + self.xml(f"{g}/{C}/master_config.xml")[:-1]
                + [f'100 openat(AT_FDCWD, "{g}/{C}/master_config.xml", O_RDONLY <unfinished ...>',
                   '101 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 5',
                   '100 <... openat resumed>) = 4']
                + self.xml(f"{g}/{C}/SuSAv2MECPXSec.xml")
                + [f'100 openat(AT_FDCWD, "{g}/Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.so", O_RDONLY|O_CLOEXEC) = 6',
                   f'100 openat(AT_FDCWD, "{g}/Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.rootmap", O_RDONLY) = 6',
                   f'100 openat(AT_FDCWD, "{self.rootp}/etc/system.rootrc", O_RDONLY) = 7',
                   f'100 openat(AT_FDCWD, "{self.W}/flux.root", O_RDONLY) = 8',
                   '100 openat(AT_FDCWD, "genie-mcjob-123456789.status", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 9',
                   '101 +++ exited with 0 +++', '100 +++ exited with 0 +++'])

    def check(self, lines=None, rc=0, role="gevgen", spline_sha=None, text=None, cwd=None, gxmlpath=None, **kw):
        text = text if text is not None else "\n".join(lines if lines is not None else self.good_lines()) + "\n"
        return V.trace_check(text, rc, role, "G21_11a_00_000", str(self.spline), spline_sha or sha(b"spline"),
                             cwd or str(self.W), self.record, self.manifest, self.private, str(self.W),
                             {str(self.spline): sha(b"spline")}, genie_root=str(self.genie), repo=str(self.repo),
                             private_root=str(self.priv), gxmlpath=self.xdata if gxmlpath is None else gxmlpath,
                             xsec_data=self.xdata, **kw)

    def assert_fails(self, rec, want):
        self.assertFalse(rec["pass"])
        self.assertTrue(any(p.startswith(want) for p in rec["problems"]), rec["problems"])

    def test_a_good_trace_passes(self):
        rec = self.check()
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertTrue(rec["initial_opened_spline"])
        gated = {x["path"] for x in rec["gated"]}
        self.assertIn(self.files[f"{self.C}/master_config.xml"], gated)          # joined from unfinished + resumed
        self.assertIn(str(self.genie / "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.so"), gated)   # via the manifest link
        self.assertNotIn(str(self.W / "flux.root"), gated)                       # W's own "genie" does not gate it
        self.assertEqual([x["path"] for x in rec["root_config"]], [str(self.rootp / "etc/system.rootrc")])
        self.assertIn({"call": "access", "path": f"{self.priv}/genie_xsec/data/ModelConfiguration.xml", "ok": False,
                       "errno": "ENOENT", "initial": True}, rec["probes"])
        self.assertEqual([(x["bound_by"], x["path"].rsplit("/", 1)[1]) for x in rec["execs"]], [("genie manifest", "gevgen")])
        self.assertFalse([x for x in rec["probes"] if "genie-mcjob" in x["path"]])      # W's seed-named files stay out
        self.assertEqual(len(rec["defining_files"]), 5)

    def test_completeness(self):
        g = self.good_lines()
        self.assert_fails(self.check(text=""), "empty:")
        self.assert_fails(self.check(rc=1), "strace-rc:")
        self.assert_fails(self.check(g + ["100 +++ killed by SIGKILL +++"]), "killed:")
        self.assert_fails(self.check(text="\n".join(g)), "truncated:")
        self.assert_fails(self.check(g[:-1]), "initial-exit:")
        self.assert_fails(self.check(g + [f'100 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>']), "unresumed:")

    def test_the_initial_process_must_open_the_spline(self):
        g = self.good_lines()
        g[0] = g[0].replace("100 ", "101 ", 1)
        self.assert_fails(self.check(["99 access(\"/x\", R_OK) = 0", "99 +++ exited with 0 +++"] + g),
                          "spline-not-opened:")
        self.assert_fails(self.check(spline_sha="0" * 64), "spline-sha:")

    def test_gated_files_match_their_pins_at_their_own_path(self):
        Path(self.files[f"{self.C}/SuSAv2MECPXSec.xml"]).write_text("changed")
        self.assert_fails(self.check(), "gated-mismatch:")

    def test_config_files_from_outside_the_roots(self):
        for path, code in (("/home/u/.rootrc", "config-outside-roots:"),
                           (f"{self.tmp}/x/ModelConfiguration.xml", "config-outside-roots:"),
                           ("/tmp/rootlogon.C", "config-outside-roots:"), (f"{self.tmp}/lib/libGFwEG.so", "so-outside-roots:")):
            with self.subTest(path):
                g = self.good_lines()
                g.insert(1, f'100 openat(AT_FDCWD, "{path}", O_RDONLY) = 3')
                self.assert_fails(self.check(g), code)
        g = self.good_lines()
        g.insert(1, '100 openat(AT_FDCWD, "/etc/localtime", O_RDONLY|O_CLOEXEC) = 3')   # a system file, not config
        self.assertTrue(self.check(g)["pass"])

    def test_search_order(self):
        # read at the first existing path of GXMLPATH, then the tune's search_dirs (the manifest says what exists)
        g = self.good_lines()
        g.insert(2, f'100 newfstatat(AT_FDCWD, "{self.tmp}/elsewhere/master_config.xml", {{st_mode=S_IFREG}}, 0) = 0')
        self.assertTrue(self.check(g)["pass"])                         # a probe that found a duplicate is not a read
        self.private = {"genie_xsec/data/EventGenerator.xml": {"type": "file", "sha256": "0" * 64}}
        self.assert_fails(self.check(), "search-order: EventGenerator.xml read at")      # GXMLPATH shadows the tune's
        self.private = {}
        g = self.good_lines()                                          # another tune's CommonParam.xml (codex B3)
        g.insert(5, f'100 openat(AT_FDCWD, "{self.genie}/{self.C}/G18_01a/CommonParam.xml", O_RDONLY) = 4')
        self.assert_fails(self.check(g), "search-probes: CommonParam.xml read at")       # no search reaches it
        g = self.good_lines()
        g[5:5] = self.xml(f"{self.genie}/{self.C}/CommonParam.xml")
        self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])

    def test_gxmlpath_must_be_the_tunes_data_dir(self):
        for v in ("", f"{self.xdata}:", f"/elsewhere:{self.xdata}", "/elsewhere"):
            with self.subTest(v):
                self.assert_fails(self.check(gxmlpath=v), "gxmlpath:")

    def test_defining_files(self):
        g = [ln for ln in self.good_lines() if "TuneGeneratorList" not in ln]
        self.assert_fails(self.check(g), "defining-not-opened:")
        mc = Path(self.files[f"{self.C}/G21_11a/ModelConfiguration.xml"])     # a link on disk, followed by the kernel
        mc.rename(mc.with_name("real.xml"))
        mc.symlink_to("real.xml")
        self.assert_fails(self.check(), "defining-link:")
        mc.unlink()
        mc.with_name("real.xml").rename(mc)
        awk = os.path.realpath("/usr/bin/awk")
        g = [ln for ln in self.good_lines() if "TuneGeneratorList" not in ln]
        g[0] = '100 execve("/usr/bin/awk", ["awk"], 0x1 /* 3 vars */) = 0'      # the reduce role's own program
        self.assertTrue(self.check(g, role="reduce", system_pins={awk: V.sha_path(awk)})["pass"])

    def test_relative_paths(self):
        g = [ln for ln in self.good_lines() if "mcjob" not in ln]           # its cwd here is not W
        rel = os.path.relpath(self.W / "flux.root", self.tmp)                   # no '..'
        i = next(k for k, ln in enumerate(g) if "flux.root" in ln)
        g[i] = f'100 openat(AT_FDCWD, "{rel}", O_RDONLY) = 8'
        self.assertTrue(self.check(g, cwd=str(self.tmp))["pass"])                 # against the initial cwd
        g.insert(i, f'100 chdir("{self.W}") = 0')
        self.assert_fails(self.check(g, cwd=str(self.tmp)), "cwd-unknown:")      # after any chdir, relative is unknown
        g = self.good_lines()
        g.insert(1, '100 openat(7, "ModelConfiguration.xml", O_RDONLY) = 3')
        self.assert_fails(self.check(g), "dirfd-relative:")

    def test_escapes_and_writes(self):
        self.assertEqual(V._unescape(r"a\"b\\c\x41\101\n"), 'a"b\\cAA\n')
        ev, _ = V.parse_trace('7 openat(AT_FDCWD, "/a/genie.root", O_WRONLY|O_CREAT, 0644) = 3\n')
        self.assertTrue(ev[0]["write_only"] and ev[0]["creat"])


class Exe(Tmp):
    def test_programs_against_the_manifest(self):
        root = self.tmp / "genie/v3_04_00"
        b = root / "Linux64bit+3.10-2.17-e20-prof/bin"
        b.mkdir(parents=True)
        (b / "gevgen").write_text("gevgen")
        (b / "gspl2root-real").write_text("gspl")
        (b / "gspl2root").symlink_to("gspl2root-real")
        man = {"genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/bin/gevgen": {"type": "file", "sha256": sha(b"gevgen")},
               "genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/bin/gspl2root-real": {"type": "file", "sha256": sha(b"gspl")},
               "genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/bin/gspl2root": {"type": "symlink", "target": "gspl2root-real"}}
        ok = [str(b / "gevgen"), str(b / "gspl2root")]
        self.assertEqual(V.exe_problems(ok, man, genie_root=str(root)), [])
        (self.tmp / "gevgen").write_text("gevgen")                                                   # same bytes, outside
        self.assertTrue(V.exe_problems([str(self.tmp / "gevgen")], man, genie_root=str(root)))
        self.assertTrue(V.exe_problems(["gevgen"], man, genie_root=str(root)))                        # not absolute
        self.assertTrue(V.exe_problems([str(b)], man, genie_root=str(root)))                          # a directory
        (b / "extra").write_text("x")
        self.assertTrue(V.exe_problems([str(b / "extra")], man, genie_root=str(root)))               # not in the manifest
        (b / "gevgen").write_text("changed")
        self.assertTrue(V.exe_problems(ok, man, genie_root=str(root)))                               # other bytes
        (b / "gevgen").write_text("gevgen")
        (self.tmp / "gspl-copy").write_text("gspl")                       # same bytes, but the link leaves the product
        (b / "gspl2root").unlink()
        (b / "gspl2root").symlink_to(self.tmp / "gspl-copy")
        self.assertEqual([p.split(":")[0] for p in V.exe_problems(ok, man, genie_root=str(root))], ["exe-not-manifest"])


# ------------------------------------------------------------------------------------- run_gevgen_v3.sh's trace prefix

STUB = '#!/bin/sh\nprintf "NAME %s\\n" "$(printf "%s " "$@" | tr "\\n" "~")" >> "$PG_ARGV_LOG"\nEXTRA\n'
SETUP = '''export GENIE=/g GENIE_SPLINES_V3="$2/${1}_CH.xml.gz" GENIE_XSEC_TUNE="$1"
export PATH="$PG_STUB_BIN:$PATH"
'''
TRACER = '''#!/bin/sh
printf "strace %s\\n" "$(printf "%s " "$@" | tr "\\n" "~")" >> "$PG_ARGV_LOG"
while [ "$1" != "-o" ]; do shift; done; shift 2
exec "$@"
'''


class Prefix(Tmp):
    def setUp(self):
        super().setUp()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for name, extra in (("gevgen", ""), ("gspl2root", ""), ("gntpc", ""), ("awk", ""),
                            ("sha256sum", ""), ("gzip", 'touch "$2".gz')):
            (self.bin / name).write_text(STUB.replace("NAME", name).replace("EXTRA", extra))
            (self.bin / name).chmod(0o755)
        self.tracer = self.tmp / "tracer"
        self.tracer.write_text(TRACER)
        self.tracer.chmod(0o755)
        self.log = self.tmp / "argv.log"

    def script(self, body, sub):
        d = self.tmp / sub
        d.mkdir()
        if not os.path.isdir("/proc/self/fd"):                 # macOS: see fd_farm
            assert body.count("fdd=/dev/fd") <= 1
            body = body.replace("fdd=/dev/fd", f"fdd={fd_farm(self.tmp / 'fd', self.tracer)}")
        (d / "run_gevgen_v3.sh").write_text(body)
        (d / "setup_genie_v3.sh").write_text(SETUP)
        return d / "run_gevgen_v3.sh"

    def go(self, script, mode, tune="G18_10a_02_11b", fd=None, **env):
        if self.log.exists():
            self.log.unlink()
        w = self.tmp / f"w-{mode}-{len(list(self.tmp.iterdir()))}"
        w.mkdir()
        args = {"reduce": [tune, str(w / "spl")], "graphs": [tune, str(w / "spl"), str(w / "g.root")],
                "genie": [tune, str(w / "spl"), "100", "123456789", str(w / "work"), str(w / "flux.root")]}[mode]
        e = {"PATH": f"{self.bin}:/usr/bin:/bin", "PG_ARGV_LOG": str(self.log), "PG_STUB_BIN": str(self.bin)}
        e.update(env)
        kw = {}
        if fd is not None:                       # a real descriptor of the tracer, at whatever number it gets
            fd = os.open(self.tracer, os.O_RDONLY)
            kw["pass_fds"] = (fd,)
            self.addCleanup(os.close, fd)
            e.update({k: (str(fd) if v == "FD" else v) for k, v in env.items()})
        p = subprocess.run(["bash", str(script), mode] + args, env=e, capture_output=True, text=True, cwd=self.tmp, **kw)
        argv = [ln.replace(str(w), "W") for ln in self.log.read_text().splitlines()] if self.log.exists() else []
        return p, argv

    def test_no_inputs_give_f1s_argv_exactly(self):
        f1, pg = self.script(F1_RUN, "f1"), self.script((GENIE / "run_gevgen_v3.sh").read_text(), "pg")
        for mode in ("reduce", "graphs", "genie"):
            with self.subTest(mode):
                a, b = self.go(f1, mode)[1], self.go(pg, mode)[1]
                want = {"reduce": "awk", "graphs": "gspl2root", "genie": "gevgen"}[mode]
                self.assertTrue([x for x in a if x.startswith(want + " ")], a)
                self.assertEqual(a, b)

    def test_an_exported_scalar_pg_trace_has_no_effect(self):
        f1, pg = self.script(F1_RUN, "f1"), self.script((GENIE / "run_gevgen_v3.sh").read_text(), "pg")
        evil = self.tmp / "evil"
        evil.write_text('#!/bin/sh\necho EVIL >> "$PG_ARGV_LOG"\n"$@"\n')
        evil.chmod(0o755)
        for mode in ("reduce", "graphs", "genie"):
            with self.subTest(mode):
                a = self.go(f1, mode)[1]
                b = self.go(pg, mode, PG_TRACE=str(evil))[1]
                self.assertEqual(a, b)
                self.assertNotIn("EVIL", b)

    def test_valid_inputs_trace_the_command_directly(self):
        pg = self.script((GENIE / "run_gevgen_v3.sh").read_text(), "pg")
        f1 = self.script(F1_RUN, "f1")
        tdir = self.tmp / "traces"
        tdir.mkdir()
        for mode, traced in (("genie", (("gevgen", "gevgen"), ("gntpc", "gntpc"))),
                             ("graphs", (("graphs_G18_10a_02_11b", "gspl2root"),)),
                             ("reduce", (("reduce_G18_10a_02_11b", "awk"),))):
            with self.subTest(mode):
                plain = self.go(f1, mode)[1]
                p, argv = self.go(pg, mode, fd=True, PG_STRACE_FD="FD", PG_TRACE_DIR=str(tdir))
                st = [x for x in argv if x.startswith("strace ")]
                self.assertEqual(len(st), len(traced), argv)                    # gntpc too (D1)
                for line, (name, cmd) in zip(st, traced):
                    self.assertEqual(line, f"strace -f -q -e {V.TRACE_SET} -o {tdir}/{name}.trace "
                                           + next(x for x in plain if x.startswith(cmd + " ")))
                    i = argv.index(line)
                    self.assertTrue(argv[i + 1].startswith(cmd + " "))         # strace exec'd the command directly
                self.assertEqual([x for x in argv if not x.startswith("strace ")], plain)

    def test_invalid_inputs_refuse(self):
        pg = self.script((GENIE / "run_gevgen_v3.sh").read_text(), "pg")
        tdir = self.tmp / "traces"
        tdir.mkdir()
        (self.tmp / "fd").mkdir(exist_ok=True)
        (self.tmp / "okdir").mkdir()                    # clean: only the rule under test can refuse
        (tdir / "gevgen.trace").write_text("old")
        for i, env in enumerate(({"PG_STRACE_FD": "FD"}, {"PG_TRACE_DIR": str(self.tmp)},
                                 {"PG_STRACE_FD": "x9", "PG_TRACE_DIR": str(self.tmp)},
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": "okdir"},              # exists, from cwd
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": f"{self.tmp}/fd/../okdir"},    # exists
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": f"{self.tmp}/missing"},
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": str(tdir)},           # gevgen.trace exists
                                 {"PG_STRACE_FD": "999", "PG_TRACE_DIR": str(self.tmp)},
                                 {"PG_STRACE_FD": "2", "PG_TRACE_DIR": str(self.tmp)},       # stdio is never strace
                                 {"PG_STRACE_FD": "0", "PG_TRACE_DIR": str(self.tmp)},
                                 {"PG_STRACE_FD": "02", "PG_TRACE_DIR": str(self.tmp)})):
            with self.subTest(i):
                p, argv = self.go(pg, "genie", fd=True if env.get("PG_STRACE_FD") == "FD" else None, **env)
                self.assertEqual(p.returncode, 2, p.stderr)
                if env.get("PG_STRACE_FD") in ("2", "0", "02", "x9"):
                    self.assertIn("refusing: PG_STRACE_FD is not a descriptor above 2", p.stderr)
                self.assertFalse([x for x in argv if x.startswith("gevgen ")])
        p, argv = self.go(pg, "reduce", fd=True, PG_STRACE_FD="FD", PG_TRACE_DIR="okdir")   # reduce stays in the cwd
        self.assertEqual(p.returncode, 2, p.stderr)
        self.assertFalse([x for x in argv if x.startswith("strace ")])

    def test_slot1_reads_its_private_source(self):
        pg = self.script((GENIE / "run_gevgen_v3.sh").read_text(), "pg")
        p, argv = self.go(pg, "reduce", tune="G21_11a_00_000")
        awk = next(x for x in argv if x.startswith("awk "))
        self.assertTrue(awk.rstrip().endswith(" /pscratch/sd/j/josephrb/covfix-pg/products/genie_xsec/v3_04_00/NULL/"
                                     "G2111a00000-k250-e1000/data/gxspl-NUsmall.xml"), awk)
        p, argv = self.go(pg, "reduce", tune="G18_02a_00_000")
        awk = next(x for x in argv if x.startswith("awk "))
        self.assertTrue(awk.rstrip().endswith(" /cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/"
                                     "G1802a00000-k250-e1000/data/gxspl-NUsmall.xml"), awk)


if __name__ == "__main__":
    unittest.main()


# ------------------------------------------------------------------ agy's read of 135571b9: real shapes and the gaps

REAL_MEMBERS = json.loads((RECORD_DIR / "G2111a-members.json").read_text())["members"]


def real_shape_tree(root):
    """A tree with the real G2111a listing's names, types and link targets, synthetic bytes; and its pins."""
    pins = {}
    for n, m in sorted(REAL_MEMBERS.items()):
        p = Path(root) / n
        if m["type"] == "dir":
            p.mkdir(parents=True, exist_ok=True)
            pins[n] = {"type": "dir"}
        elif m["type"] == "file":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(n.encode())
            pins[n] = {"type": "file", "sha256": sha(n.encode())}
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.symlink_to(m["target"])
            pins[n] = {"type": "symlink", "target": m["target"]}
    for d, dirs, files in os.walk(Path(root) / "genie_xsec", topdown=False):
        for f in files:
            if not os.path.islink(os.path.join(d, f)):
                os.chmod(os.path.join(d, f), 0o444)
        os.chmod(d, 0o555)
    up = Path(root) / ".upsfiles"
    up.mkdir()
    (up / "dbconfig").write_text("db\n")
    os.chmod(up / "dbconfig", 0o444)
    os.chmod(up, 0o555)
    return pins


class RealShapes(Tmp):
    def test_the_real_listing_has_no_top_container_member_and_passes(self):
        self.assertNotIn("genie_xsec", REAL_MEMBERS)                          # the shape the stub fixtures missed
        pins = real_shape_tree(self.tmp / "p")
        self.assertEqual(V.members_check(str(self.tmp / "p"), pins), [])

    def test_upsfiles_must_hold_only_a_read_only_dbconfig(self):
        pins = real_shape_tree(self.tmp / "p")
        up = self.tmp / "p/.upsfiles"
        os.chmod(up, 0o755)
        (up / "extra").write_text("x")
        self.assertTrue(any(p.startswith("upsfiles:") for p in V.members_check(str(self.tmp / "p"), pins)))

    def test_tool_check_by_descriptor(self):
        p = self.tmp / "tool"
        p.write_text("#!/bin/sh\n")
        fd = os.open(p, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        import contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = V.main(["tool-check", "--fd", str(fd), "--sha256", sha(p.read_bytes())])
        self.assertEqual(rc, 0, out.getvalue())

    @unittest.skipUnless(os.path.isdir("/proc/self/fd"), "untested on this host: no /proc/self/fd (macOS)")
    def test_proc_self_fd_is_a_magic_link(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        with self.assertRaises(OSError):                                       # why tool-check takes --fd, not a path
            os.open(f"/proc/self/fd/{fd}", os.O_RDONLY | os.O_NOFOLLOW)


class TraceGaps(Trace):
    """codes: each failing case names its reason code, so a crash-STOP can never satisfy it."""

    def codes(self, rec):
        return {p.split(":", 1)[0] for p in rec["problems"]}

    def test_a_real_directory_open_is_recorded_not_gated(self):
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{self.genie}/Linux64bit+3.10-2.17-e20-prof/lib", '
                    'O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 9')
        rec = self.check(g)
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertEqual(rec["directories_opened"], 1)

    def test_slot2_reduce_at_its_real_cvmfs_path(self):
        src = "/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/G1802a00000-k250-e1000/data/gxspl-NUsmall.xml"
        awk = os.path.realpath("/usr/bin/awk")
        text = (f'7 execve("/usr/bin/awk", ["awk"], 0x1 /* 3 vars */) = 0\n7 openat(AT_FDCWD, "{src}", O_RDONLY) = 3\n'
                '7 +++ exited with 0 +++\n')
        args = dict(genie_root=str(self.genie), repo="/cvmfs/larsoft.opensciencegrid.org", private_root=str(self.priv),
                    sha=lambda p: "f" * 64 if p == src else V.sha_path(p), system_pins={awk: V.sha_path(awk)})
        rec = V.trace_check(text, 0, "reduce", "G18_02a_00_000", src, "f" * 64, str(self.W), self.record, self.manifest,
                            {}, str(self.W), {src: "f" * 64}, **args)
        self.assertTrue(rec["pass"], rec["problems"])
        rec = V.trace_check(text, 0, "reduce", "G18_02a_00_000", src, "f" * 64, str(self.W), self.record, self.manifest,
                            {}, str(self.W), {}, **args)
        self.assertIn("gated-mismatch", self.codes(rec))

    def test_flags_parsed_after_the_path(self):
        for line, code in ((f'100 openat(AT_FDCWD, "{self.tmp}/evil.xml", O_RDWR) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.tmp}/evil.xml", O_RDONLY|O_CREAT, 0644) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.tmp}/O_WRONLY.xml", O_RDONLY) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.tmp}/x) = -1.xml", O_RDONLY) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.tmp}/a, O_WRONLY.xml", O_RDONLY) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.tmp}/a,O_PATH,b.xml", O_RDONLY) = 3', "gated-mismatch")):
            with self.subTest(line):
                g = self.good_lines()
                g.insert(1, line)
                self.assertIn(code, self.codes(self.check(g)))

    def test_outputs_under_w_are_not_reads(self):
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{self.W}/genie-out.root", O_RDWR|O_CREAT|O_TRUNC, 0644) = 3')
        self.assertTrue(self.check(g)["pass"])
        for line, code in ((f'100 openat(AT_FDCWD, "{self.W}/evil.xml", O_RDWR|O_CREAT, 0644) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.W}/evil.xml", O_RDWR|O_CREAT|O_TRUNC, 0644) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.W}/.rootrc", O_RDONLY|O_CREAT, 0644) = 3', "config-unpinned"),
                           (f'100 openat(AT_FDCWD, "{self.W}/genie-x.root", O_RDWR|O_CREAT, 0644) = 3', "gated-mismatch"),
                           (f'100 openat(AT_FDCWD, "{self.W}/evil.so", O_RDWR|O_CREAT|O_TRUNC, 0755) = 3', "so-outside-roots"),
                           (f'100 openat(AT_FDCWD, "{self.W}/x.root", O_RDONLY|O_CREAT, 0644) = 3', None)):
            with self.subTest(line):                                   # O_CREAT alone may open an existing file
                g = self.good_lines()
                g.insert(1, line)
                rec = self.check(g)
                if code:
                    self.assertIn(code, self.codes(rec))
                else:
                    self.assertTrue(rec["pass"], rec["problems"])

    def test_unresumed_calls_and_child_exits(self):
        g = self.good_lines()
        g.insert(1, f'101 openat(AT_FDCWD, "{self.tmp}/evil.xml", O_RDONLY <unfinished ...>')
        self.assertIn("unresumed", self.codes(self.check(g)))
        g = self.good_lines()
        g[-2] = "101 +++ exited with 1 +++"
        self.assertIn("child-exit", self.codes(self.check(g)))

    def test_fchdir_and_unknown_cwds(self):
        g = self.good_lines()
        g.insert(1, "100 fchdir(7) = 0")
        self.assertIn("fchdir", self.codes(self.check(g)))
        g = self.good_lines()
        g.insert(1, f'101 chdir("{self.tmp}") = 0')
        g.insert(2, '101 openat(AT_FDCWD, "ModelConfiguration.xml", O_RDONLY) = 3')
        self.assertIn("cwd-unknown", self.codes(self.check(g)))

    def test_dotdot_and_dirfd(self):
        # a '..' path is resolved on the node (realpath of its directory), recorded raw and resolved, then gated
        lib = f"{self.genie}/Linux64bit+3.10-2.17-e20-prof/lib"
        g = self.good_lines()
        g.insert(2, f'100 openat(AT_FDCWD, "{lib}/../lib/libGFwEG.rootmap", O_RDONLY) = 3')
        rec = self.check(g)
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertEqual(rec["dotdot"], [{"raw": f"{lib}/../lib/libGFwEG.rootmap",
                                          "resolved": os.path.realpath(self.files["Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.rootmap"])}])
        (self.genie / "alias").symlink_to(f"Linux64bit+3.10-2.17-e20-prof/lib")             # the kernel follows it
        g = self.good_lines()
        g.insert(2, f'100 openat(AT_FDCWD, "{self.genie}/alias/../lib/libGFwEG.rootmap", O_RDONLY) = 3')
        rec = self.check(g)
        self.assertTrue(rec["pass"], rec["problems"])              # lexically it would be {genie}/GENIE-Generator/...
        g = self.good_lines()
        g.insert(2, f'100 openat(AT_FDCWD, "{self.tmp}/lnk/../x.xml", O_RDONLY) = 3')          # no such directory
        self.assertIn("resolve-failed", self.codes(self.check(g)))
        (self.tmp / "sub").mkdir()
        g = self.good_lines()
        g.insert(2, f'100 openat(AT_FDCWD, "{self.tmp}/sub/../rootlogon.C", O_RDONLY) = 3')
        self.assertIn("dotdot-outside-roots", self.codes(self.check(g)))
        g = self.good_lines()
        g.insert(2, f'100 access("{self.tmp}/lnk/../x.xml", R_OK) = -1 ENOENT (No such file or directory)')
        self.assertTrue(self.check(g)["pass"])                            # a failed probe is only recorded
        for raw in ("libGFwEG.so", "etc/custom.conf", "ModelConfiguration.xml"):
            with self.subTest(raw):
                g = self.good_lines()
                g.insert(1, f'100 openat(7, "{raw}", O_RDONLY) = 3')
                self.assertIn("dirfd-relative", self.codes(self.check(g)))
        g = self.good_lines()
        g.insert(1, '100 newfstatat(7, "ModelConfiguration.xml", {st_mode=S_IFREG}, 0) = 0')
        self.assertIn("dirfd-relative", self.codes(self.check(g)))

    def test_a_manifest_link_retargeted_on_disk(self):
        lib = self.genie / "Linux64bit+3.10-2.17-e20-prof/lib"
        (lib / "evil.so").write_text("so")
        (lib / "libGFwEG.so").unlink()
        (lib / "libGFwEG.so").symlink_to("evil.so")
        self.assertIn("gated-mismatch", self.codes(self.check()))

    def test_libraries_from_outside_the_roots(self):
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{self.tmp}/home/.genie_compatlibs/libssl.so.10", O_RDONLY|O_CLOEXEC) = 3')
        self.assertIn("so-outside-roots", self.codes(self.check(g)))

    def test_another_spline_and_defining_files_by_another_pid(self):
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{self.W}/splines/other_CH.xml.gz", O_RDONLY) = 3')
        self.assertIn("other-spline", self.codes(self.check(g)))
        g = [ln.replace("100 openat", "101 openat") if "TuneGeneratorList" in ln else ln for ln in self.good_lines()]
        self.assertIn("defining-not-opened", self.codes(self.check(g)))

    def test_utf8_escapes(self):
        self.assertEqual(V._unescape(r"\303\251.xml"), "é.xml")

    def test_a_crash_is_its_own_reason(self):
        rec = V.trace_check("1 x\n", 0, "gevgen", "G21_11a_00_000", "/s", "0", "/w", None, {}, {}, "/w", {})
        self.assertEqual(self.codes(rec), {"internal-error"})
        self.assertFalse(rec["pass"])


class Shapes(Tmp):
    S2 = V.SLOT2_SPLINE

    def good(self):
        members = {"genie_xsec/v3_04_00": {"type": "dir"}}
        slot2 = {"pass": True, "spline": self.S2, "initial_opened_spline": True,
                 "gated": [{"path": self.S2, "pinned_by": "exact pin", "match": True}]}
        return [7, members, {"pass": True, "n_pinned": 1}, {"pass": True, "fd": 7},
                [{"pass": True, "role": "reduce", "directories": []},
                 {"pass": True, "role": "gevgen", "directories": [{"path": "/elsewhere", "initial": True},
                                                                  {"path": V.GENIE_LIB, "initial": True}]}], slot2]

    def test_each_shape_fails_alone(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        a = self.good()
        a[0], a[3]["fd"] = fd, fd
        c, why = V.shape_checks(*a, fd_dir="/proc/self/fd" if os.path.isdir("/proc/self/fd") else "/dev/fd")
        self.assertEqual({k for k, v in c.items() if v}, {"real_members_listing", "directory_open_recorded",
                                                          "slot2_reduce_real_path"} | (
            {"proc_fd_magic_link"} if os.path.isdir("/proc/self/fd") else set()))
        if not os.path.isdir("/proc/self/fd"):
            self.assertEqual(why, {"proc_fd_magic_link": "untested-host: no /proc/self/fd"})
        for name, change in (("real_members_listing", lambda a: a[1].update({"genie_xsec": {"type": "dir"}})),
                             ("real_members_listing", lambda a: a[2].update({"n_pinned": 2})),
                             ("directory_open_recorded", lambda a: a[4][1].update({"directories": []})),
                             ("directory_open_recorded", lambda a: a[4][1]["directories"][1].update({"initial": False})),
                             ("directory_open_recorded", lambda a: a[4][1].update({"role": "graphs"})),
                             ("real_members_listing", lambda a: a[2].update({"pass": False})),
                             ("directory_open_recorded", lambda a: a[4][0].update({"pass": False})),
                             ("slot2_reduce_real_path", lambda a: a[5].update({"spline": "/elsewhere/gxspl-NUsmall.xml"})),
                             ("slot2_reduce_real_path", lambda a: a[5]["gated"][0].update({"pinned_by": "genie manifest"})),
                             ("slot2_reduce_real_path", lambda a: a[5]["gated"][0].update({"match": False}))):
            with self.subTest(name):
                b = self.good()
                b[0], b[3]["fd"] = fd, fd
                change(b)
                c, why = V.shape_checks(*b, fd_dir="/dev/fd")
                self.assertFalse(c[name])
                self.assertEqual(why[name], f"shape-{name.replace('_', '-')}: failed")

    def test_system_tools(self):
        self.assertEqual(V.system_tool_problems(["/bin/sh"]), [])
        p = self.tmp / "awk"
        p.write_text("x")
        self.assertTrue(V.system_tool_problems([str(p)])[0].startswith("system-tool:"))

    def test_ld_library_path(self):
        self.assertEqual(V.exe_problems([], {}, ld_library_path="/usr/lib64:/cvmfs/larsoft.opensciencegrid.org/x"), [])
        for v in ("/usr/lib64::/cvmfs/larsoft.opensciencegrid.org/x", "/usr/lib64:", ":/usr/lib64"):
            with self.subTest(v):                                       # an empty entry is the working directory
                self.assertEqual([p.split(":")[0] for p in V.exe_problems([], {}, ld_library_path=v)],
                                 ["ld-library-path-empty"])
        probs = V.exe_problems([], {}, ld_library_path=f"/usr/lib64:{self.tmp}")
        self.assertEqual(len(probs), 1)
        self.assertTrue(probs[0].startswith("ld-library-path:"))


class MoreRules(Trace):
    def codes(self, rec):
        return {p.split(":", 1)[0] for p in rec["problems"]}

    def test_a_writable_container_fails(self):
        pins = real_shape_tree(self.tmp / "p")
        os.chmod(self.tmp / "p/genie_xsec", 0o755)
        self.assertIn("members-type: genie_xsec is not a read-only directory", V.members_check(str(self.tmp / "p"), pins))

    def test_a_genie_library_name_is_gated_anywhere(self):
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{self.repo}/other/lib/libGFwEG.so", O_RDONLY|O_CLOEXEC) = 3')
        self.assertIn("gated-mismatch", self.codes(self.check(g)))

    def test_a_root_owned_tool_outside_the_system_bins(self):
        self.assertTrue(any(p.startswith("system-tool:") for p in V.system_tool_problems(["/etc/hosts"])))

    def test_stdio_is_never_a_tool_descriptor(self):
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
            V.main(["tool-check", "--fd", "2", "--sha256", "0" * 64])
        self.assertEqual(cm.exception.code, 2)

    def test_an_unpinned_config_file_in_w_or_the_private_product(self):
        for path, code in ((f"{self.W}/.rootrc", "config-unpinned"), (f"{self.W}/rootlogon.C", "config-unpinned"),
                           (f"{self.priv}/genie_xsec/rootlogon.C", "gated-mismatch")):   # genie_xsec: gated by name
            with self.subTest(path):
                g = self.good_lines()
                g.insert(1, f'100 openat(AT_FDCWD, "{path}", O_RDONLY) = 3')
                self.assertIn(code, self.codes(self.check(g)))


# ------------------------------------------------------------------- round 3: agy and codex-school reads of 5f141f7a

class Round3(Trace):
    def codes(self, rec):
        return {p.split(":", 1)[0] for p in rec["problems"]}

    def test_every_exec_is_bound(self):
        g = self.good_lines()
        g.insert(1, f'101 execve("{self.tmp}/bin/sh", ["sh"], 0x1 /* 3 vars */) = 0')
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin/sh").write_text("sh")
        self.assertIn("exec-unbound", self.codes(self.check(g)))
        rec = self.check(g, system_pins={os.path.realpath(self.tmp / "bin/sh"): sha(b"sh")})
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertIn("system pin", [x["bound_by"] for x in rec["execs"]])
        self.assertIn("exec-unbound", self.codes(self.check(g, system_pins={str(self.tmp / "bin/sh"): "0" * 64})))
        g = self.good_lines()
        g.insert(1, f'101 execve("{self.tmp}/nope", ["x"], 0x1 /* 3 vars */) = -1 ENOENT (No such file or directory)')
        self.assertNotIn("exec-unbound", self.codes(self.check(g)))     # a failed exec ran nothing
        Path(self.files["Linux64bit+3.10-2.17-e20-prof/bin/gevgen"]).write_text("other")
        self.assertIn("exec-unbound", self.codes(self.check()))

    def test_o_path_and_openat2_resolve(self):
        g = self.good_lines()
        g[1] = f'100 openat(AT_FDCWD, "{self.spline}", O_RDONLY|O_PATH) = 3'
        self.assertIn("spline-not-opened", self.codes(self.check(g)))
        g = self.good_lines()
        g.insert(2, f'100 openat2(AT_FDCWD, "{self.tmp}/x", {{flags=O_RDONLY, resolve=RESOLVE_IN_ROOT}}, 24) = 3')
        self.assertIn("openat2-resolve", self.codes(self.check(g)))

    def test_strict_parsing(self):
        for extra, code in (('100 openat(AT_FDCWD, "/x", O_RDONLY', "undecodable"),
                            ('100 mmap(NULL, 4096, PROT_READ) = 0x7f', "undecodable"),
                            ('100 <... openat resumed>) = 3', "resume-mismatch"),
                            ('100 chmod("/a", 0755) = 0', "undecodable")):
            with self.subTest(extra):
                g = self.good_lines()
                g.insert(2, extra)
                self.assertIn(code, self.codes(self.check(g)))
        g = self.good_lines()
        g.insert(2, '101 stat("/x" <unfinished ...>')
        g.insert(3, '101 <... access resumed>) = 0')
        self.assertIn("resume-mismatch", self.codes(self.check(g)))
        g = self.good_lines()
        g.insert(2, '102 access("/etc/hosts", R_OK) = 0')                   # 102 never exits
        self.assertIn("no-terminal", self.codes(self.check(g)))

    def test_any_chdir_makes_relative_paths_unknown(self):
        g = self.good_lines()                                               # a CLONE_FS thread moves everyone
        g.insert(2, f'101 chdir("{self.tmp}") = 0')
        g.insert(3, '100 openat(AT_FDCWD, "ModelConfiguration.xml", O_RDONLY) = 4')
        self.assertIn("cwd-unknown", self.codes(self.check(g)))

    def test_other_reads_under_a_data_dir(self):
        g = self.good_lines()
        g.insert(2, f'100 openat(AT_FDCWD, "{self.priv}/genie_xsec/data/isotopes.cfg", O_RDONLY) = 3')
        self.assertIn("other-spline", self.codes(self.check(g)))

    def test_gntpc_and_coverage_roles(self):
        P = "Linux64bit+3.10-2.17-e20-prof"
        (self.genie / P / "bin/gntpc").write_text("gntpc")
        self.manifest[f"genie/v3_04_00/{P}/bin/gntpc"] = {"type": "file", "sha256": sha(b"gntpc")}
        g = [f'200 execve("{self.genie}/{P}/bin/gntpc", ["gntpc"], 0x1 /* 3 vars */) = 0',     # gntpc's real shape
             '200 openat(AT_FDCWD, "gntp.123.ghep.root", O_RDONLY) = 3',
             '200 access("genie_v3.gst.root", F_OK) = -1 ENOENT (No such file or directory)',
             '200 openat(AT_FDCWD, "genie_v3.gst.root", O_RDWR|O_CREAT, 0644) = 4', "200 +++ exited with 0 +++"]
        run = lambda lines: V.trace_check("\n".join(lines) + "\n", 0, "gntpc", "G21_11a_00_000", None, None, str(self.W),
                                          self.record, self.manifest, {}, str(self.W), {}, genie_root=str(self.genie),
                                          repo=str(self.repo), private_root=str(self.priv),
                                          ghep_in=str(self.W / "gntp.123.ghep.root"))
        rec = run(g)
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertIn("other-spline", self.codes(run(g[:1] + [f'200 openat(AT_FDCWD, "{self.spline}", O_RDONLY) = 5'] + g[1:])))
        msg = self.W / "Messenger_pg.xml"                                  # gntpc reads no spline; coverage its messenger
        msg.write_bytes(V.messenger((RECORD_DIR / "Messenger_laconic.xml").read_bytes()))
        c = self.good_lines()
        c.insert(1, f'100 openat(AT_FDCWD, "{msg}", O_RDONLY) = 3')
        self.assertTrue(self.check(c, role="coverage", messenger=str(msg))["pass"])
        self.assertIn("defining-not-opened", self.codes(
            self.check([ln for ln in c if "TuneGeneratorList" not in ln], role="coverage", messenger=str(msg))))

    def test_root_config_bound_by_real_path_and_hash(self):
        (self.tmp / "elsewhere").mkdir()
        (self.tmp / "elsewhere/system.rootrc").write_text("x")
        rc = self.rootp / "etc/system.rootrc"
        rc.unlink()
        rc.symlink_to(self.tmp / "elsewhere/system.rootrc")
        self.assertIn("config-outside-roots", self.codes(self.check()))
        rc.unlink()
        rc.write_text("rootrc")

        def sha_no_root(p):
            if p.endswith("system.rootrc"):
                raise OSError("unreadable")
            return V.sha_path(p)
        self.assertIn("root-config-unhashed", self.codes(self.check(sha=sha_no_root)))

    def test_a_system_tool_by_its_own_path(self):
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin/awk").symlink_to("/bin/sh")
        self.assertTrue(V.system_tool_problems([str(self.tmp / "bin/awk")])[0].startswith("system-tool:"))
        self.assertEqual(V.system_tool_problems(["/bin/sh"]), [])
        self.assertTrue(V.system_tool_problems([""])[0].startswith("system-tool:"))

    def test_the_products_top_level_is_exact(self):
        pins = real_shape_tree(self.tmp / "p")
        os.chmod(self.tmp / "p", 0o755)
        (self.tmp / "p/genie").mkdir()
        self.assertIn("members-top", {x.split(":")[0] for x in V.members_check(str(self.tmp / "p"), pins)})


class Coverage(Tmp):
    LACONIC = RECORD_DIR / "Messenger_laconic.xml"

    def test_the_messenger_differs_from_laconic_by_exactly_the_gevgdriver_line(self):
        lac = self.LACONIC.read_bytes()
        self.assertEqual(sha(lac), V.LACONIC_SHA256)
        man = json.loads((RECORD_DIR / "genie-manifest.json").read_text())["members"]
        self.assertEqual(man["genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/Messenger_laconic.xml"]
                         ["sha256"], V.LACONIC_SHA256)
        out = V.messenger(lac)
        self.assertEqual(sha(out), V.MESSENGER_SHA256)
        a, b = lac.split(b"\n"), out.split(b"\n")
        self.assertEqual(len(a), len(b))
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        self.assertEqual(diff, [V.MESSENGER_LINE])
        self.assertIn(b'msgstream="GEVGDriver"', diff[0][1])
        for bad, code in ((lac + b" ", "messenger-laconic"),):
            with self.subTest(code), self.assertRaises(V.Fail) as cm:
                V.messenger(bad)
            self.assertTrue(str(cm.exception).startswith(code))

    def test_the_messenger_cli_writes_once(self):
        import contextlib
        out = self.tmp / "m.xml"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(V.main(["messenger", "--laconic", str(self.LACONIC), "--out", str(out)]), 0)
            self.assertEqual(V.main(["messenger", "--laconic", str(self.LACONIC), "--out", str(out)]), 1)
        self.assertEqual(sha(out.read_bytes()), V.MESSENGER_SHA256)

    def test_the_coverage_log(self):
        need = lambda x: f"1700 NOTICE GEVGDriver : [n] <CreateSplines (646)> : Need xsec spline for {x}"
        found = "1700 DEBUG GEVGDriver : [n] <CreateSplines (657)> : Spline was found"
        built = "1700 DEBUG GEVGDriver : [n] <CreateSplines (651)> : The spline wasn't loaded at initialization. I can build..."
        self.assertEqual(V.coverage_problems("\n".join([need("a"), found, need("b"), found])), [])
        for lines, code in (([need("a"), found, need("b")], "coverage-unanswered"), ([need("a"), built], "coverage-built"),
                            (["nothing"], "coverage-none"), ([found, need("a"), found], "coverage-orphan"),
                            ([need("a"), need("b"), found], "coverage-unanswered")):
            with self.subTest(code):
                self.assertIn(code, {p.split(":")[0] for p in V.coverage_problems("\n".join(lines))})


SPL = '<spline name="genie::X/Default/nu:{nu};tgt:{tgt};N:2112;proc:Weak[CC],QES;" nknots="{k}">\n{knots}</spline>\n'


class Reduce(Tmp):
    def write(self, name, entries, gz=False):
        import gzip
        body = "<genie_xsec_spline_list>\n" + "".join(SPL.format(nu=n, tgt=t, k=k, knots="<knot> 1 2 </knot>\n" * int(k)) for n, t, k in entries) + "</genie_xsec_spline_list>\n"
        p = self.tmp / name
        (gzip.open(p, "wt") if gz else open(p, "w")).write(body)
        return str(p)

    def test_the_argv_pairs_are_f1s(self):
        self.assertEqual(V.argv_pairs((GENIE / "run_gevgen_v3.sh").read_text()),
                         {("14", "1000060120"), ("14", "1000010010")})
        self.assertEqual(V.argv_problems((GENIE / "run_gevgen_v3.sh").read_text()), [])

    def test_completeness(self):
        pairs = {("14", "1000060120"), ("14", "1000010010")}
        src = self.write("src.xml", [(14, 1000060120, 30), (14, 1000010010, 30), (12, 1000060120, 30), (14, 1000080160, 30)])
        self.assertEqual(V.reduce_problems(src, self.write("ok.xml.gz", [(14, 1000060120, 30), (14, 1000010010, 30),
                                                                          (12, 1000060120, 30)], gz=True), pairs), [])
        for name, red, code in (("a pair dropped", [(14, 1000060120, 30)], "reduce-incomplete"),
                                ("knots differ", [(14, 1000060120, 29), (14, 1000010010, 30)], "reduce-incomplete")):
            with self.subTest(name):
                self.assertIn(code, {p.split(":")[0] for p in V.reduce_problems(src, self.write(name + ".xml", red), pairs)})
        # the argv names a pair the reduced file lacks (oxygen): a STOP
        with_o = pairs | {("14", "1000080160")}
        self.assertIn("reduce-incomplete", {p.split(":")[0] for p in V.reduce_problems(
            src, self.write("ok2.xml", [(14, 1000060120, 30), (14, 1000010010, 30)]), with_o)})
        self.assertIn("reduce-pair-absent", {p.split(":")[0] for p in V.reduce_problems(
            src, src, pairs | {("16", "1000010010")})})

    def test_argv_rules(self):
        s = (GENIE / "run_gevgen_v3.sh").read_text()
        cov = '    N=1; SEED=123456789; MSG="$MSGFILE"'
        for name, bad in (("a second gevgen", s.replace("    pg_trace coverage\n", "    pg_trace coverage\n    gevgen -n 1\n")),
                          ("coverage with another seed", s.replace(cov, cov.replace("123456789", "99"))),
                          ("coverage with more events", s.replace(cov, cov.replace("N=1", "N=2"))),
                          ("genie mode with another messenger", s.replace('    MSG="$GENIE/config/Messenger_laconic.xml"',
                                                                         '    MSG="$GENIE/config/Messenger.xml"')),
                          ("genie mode's SEED from another argument", s.replace(
                              "    TUNE=$1; SPLDIR=$2; N=$3; SEED=$4; WORK=$5; FLUX=$6",
                              "    TUNE=$1; SPLDIR=$2; N=$3; SEED=$5; WORK=$5; FLUX=$6")),
                          ("genie mode outside gevgen_cmd", s.replace("    gevgen_cmd > gevgen.log 2>&1\n", "", 1))):
            with self.subTest(name):
                self.assertTrue(V.argv_problems(bad))


class Wrappers(Tmp):
    """Each CLI's unexpected exception is the one reason "internal-error: <type>"."""

    def run_main(self, argv):
        import contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = V.main(argv)
        return rc, json.loads(out.getvalue().splitlines()[-1])

    def test_each_cli_fails_closed_with_its_own_reason(self):
        bad = self.tmp / "bad.json"
        bad.write_text('{"members": 5}')
        man = self.tmp / "man.json"
        man.write_text('{"members": 5}')
        for argv in (["members-check", "--root", str(self.tmp), "--members", str(bad)],
                     ["exe-check", "--manifest", str(man), "--path", "/x"],
                     ["shape-check", "--fd", "3", "--members", str(bad), "--members-check", str(bad),
                      "--tool-check", str(bad), "--traces", str(bad), "--slot2-reduce", str(bad)],
                     ["reduce-check", "--source", str(bad), "--reduced", str(bad), "--script", str(bad)],
                     ["argv-check", "--script", str(self.tmp)],
                     ["coverage-log", "--log", str(self.tmp), "--script", str(bad), "--reduced", str(bad)],
                     ["revision-compare", "--start", str(bad), "--end", str(bad)]):
            with self.subTest(argv[0]):
                rc, rec = self.run_main(argv)
                self.assertEqual(rc, 1)
                self.assertTrue(rec["problems"] and all(p.startswith(("internal-error: ", "reduce-", "argv-",
                                                                      "coverage-", "revision-")) for p in rec["problems"]),
                                rec["problems"])
        rc, rec = self.run_main(["members-check", "--root", str(self.tmp), "--members", str(bad)])
        self.assertEqual(rec["problems"], ["internal-error: TypeError"])          # len(5): the exact reason


class Host(Tmp):
    @unittest.skipUnless(os.path.isdir("/proc/self"), "untested on this host: no /proc (macOS); recorded on the node")
    def test_host_checks_on_linux(self):
        if not shutil.which("strace"):
            self.skipTest("no strace on this host: the anchor check needs the real one")
        fd = os.open(shutil.which("strace"), os.O_RDONLY)                   # the real strace on the descriptor
        self.addCleanup(os.close, fd)
        c, why = V.host_checks(fd, str(self.tmp), ["/cvmfs/x"], mountinfo_text="")
        self.assertTrue(c["st_dev_final_dir"], why)
        self.assertTrue(c["result_anchor_real_strace"], why)

    def test_a_submount_inside_a_root_and_no_proc(self):
        if not os.path.isdir("/proc/self"):
            c, why = V.host_checks(3, str(self.tmp), ["/cvmfs/x"])
            self.assertEqual(set(why.values()), {"untested-host: no /proc"})
            self.assertFalse(any(c.values()))
        mi = ("36 35 98:0 / /cvmfs/x/products/genie rw - cvmfs2 cvmfs2 ro\n37 35 98:0 / /other rw - ext4 /dev ro\n"
              "38 35 98:0 / /cvmfs/x rw - cvmfs2 cvmfs2 ro\n39 35 98:0 / /cvmfs/x/a\\040b rw - tmpfs t rw\n")
        self.assertEqual(V.submounts(mi, ["/cvmfs/x"]), ["/cvmfs/x/a b", "/cvmfs/x/products/genie"])
        self.assertEqual(V.submounts(mi, ["/elsewhere"]), [])


class Round4(Trace):
    """The round-4 rules (RULINGS-A2.md, round 4): the coverage messenger, ROOT's RECREATE outputs, each role's own
    program, unresolved execs and reads, writes confined to W, GENIE's search list from the trace, ROOT's libraries."""
    P = "Linux64bit+3.10-2.17-e20-prof"

    def setUp(self):
        super().setUp()
        for name in ("gntpc", "gspl2root"):
            f = self.genie / self.P / "bin" / name
            f.write_text(name)
            self.manifest[f"genie/v3_04_00/{self.P}/bin/{name}"] = {"type": "file", "sha256": sha(name.encode())}

    def run_role(self, lines, role, spline="", **kw):
        text = "\n".join(lines) + "\n"
        if role == "gntpc":
            kw.setdefault("ghep_in", str(self.W / "gntp.123.ghep.root"))
        return V.trace_check(text, 0, role, "G21_11a_00_000", spline, sha(b"spline") if spline else "",
                             str(self.W), self.record, self.manifest, self.private, str(self.W), {},
                             genie_root=str(self.genie), repo=str(self.repo), private_root=str(self.priv),
                             gxmlpath=self.xdata, xsec_data=self.xdata, **kw)

    def gntpc(self, *mid):
        return ([f'200 execve("{self.genie}/{self.P}/bin/gntpc", ["gntpc"], 0x1 /* 3 vars */) = 0',
                 '200 openat(AT_FDCWD, "gntp.123.ghep.root", O_RDONLY) = 3']
                + list(mid) + ["200 +++ exited with 0 +++"])

    RECREATE = ('200 access("genie_v3.gst.root", F_OK) = -1 ENOENT (No such file or directory)',
                '200 openat(AT_FDCWD, "genie_v3.gst.root", O_RDWR|O_CREAT, 0644) = 4')

    def test_the_coverage_messenger_is_pinned_in_code(self):
        msg = self.W / "out/Messenger_pg.xml"
        msg.parent.mkdir()
        msg.write_bytes(V.messenger((RECORD_DIR / "Messenger_laconic.xml").read_bytes()))
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{msg}", O_RDONLY) = 3')
        rec = self.check(g, role="coverage", messenger=str(msg))
        self.assertTrue(rec["pass"], rec["problems"])
        self.assert_fails(self.check(g, role="coverage"), "messenger-none:")
        self.assert_fails(self.check(role="coverage", messenger=str(msg)), "messenger-not-opened:")
        self.assert_fails(self.check(g, role="gevgen", messenger=str(msg)), "messenger-role:")
        self.assert_fails(self.check(g, role="gevgen"), "gated-mismatch:")          # the sealed run may not read it
        msg.write_bytes(b"<other/>")
        self.assert_fails(self.check(g, role="coverage", messenger=str(msg)), "gated-mismatch:")

    def test_root_recreate_is_an_output_only_where_the_role_writes_it(self):
        rec = self.run_role(self.gntpc(*self.RECREATE), "gntpc")
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertFalse(rec["gated"])
        unlinked = ('200 access("genie_v3.gst.root", F_OK) = 0', '200 unlink("genie_v3.gst.root") = 0', self.RECREATE[1])
        self.assertTrue(self.run_role(self.gntpc(*unlinked), "gntpc")["pass"])
        for name, mid in (("no fresh-file probe", self.RECREATE[1:]),
                          ("the probe found it", ('200 access("genie_v3.gst.root", F_OK) = 0', self.RECREATE[1])),
                          ("another process probed", ('201 access("genie_v3.gst.root", F_OK) = -1 ENOENT (No such file or directory)',
                                                      self.RECREATE[1], "201 +++ exited with 0 +++")),
                          ("not the role's output", (self.RECREATE[0].replace("genie_v3", "genie_x"),
                                                     self.RECREATE[1].replace("genie_v3", "genie_x")))):
            with self.subTest(name):
                self.assert_fails(self.run_role(self.gntpc(*mid), "gntpc"), "gated-mismatch:")

    def test_gntpc_reads_its_ghep_and_writes_its_gst(self):
        g = self.gntpc(*self.RECREATE)
        self.assert_fails(self.run_role([ln for ln in g if "ghep" not in ln], "gntpc"), "gntpc-io:")
        self.assert_fails(self.run_role([ln for ln in g if "gst" not in ln], "gntpc"), "gntpc-io:")

    def test_each_role_runs_its_own_program(self):
        self.assert_fails(self.run_role(["200 +++ exited with 0 +++"], "gntpc"), "initial-program:")   # exit only
        g = self.good_lines()
        g[0] = g[0].replace("bin/gevgen", "bin/gntpc")
        self.assert_fails(self.check(g), "initial-program:")
        g = self.gntpc(*self.RECREATE)
        g[0] = g[0].replace("bin/gntpc", "bin/gevgen")
        self.assert_fails(self.run_role(g, "gntpc"), "initial-program:")

    def test_an_unresolved_exec_fails(self):
        for lines in (('100 chdir("/") = 0', '100 execve("worker", ["worker"], 0x1 /* 1 vars */) = 0'),
                      ('100 execveat(3, "", ["x"], 0x1 /* 1 vars */, AT_EMPTY_PATH) = 0',),
                      ('100 execveat(5, "rel", ["x"], 0x1 /* 1 vars */, 0) = 0',)):
            with self.subTest(lines[-1]):
                g = self.good_lines()
                g[1:1] = list(lines)
                rec = self.check(g)
                self.assert_fails(rec, "exec-unresolved:")
                self.assertFalse([p for p in rec["problems"] if p.startswith("undecodable")])

    def test_an_unresolved_read_fails_whatever_its_name(self):
        g = self.good_lines()
        g.insert(1, '100 openat(5, "isotopes.cfg", O_RDONLY) = 6')
        self.assert_fails(self.check(g), "dirfd-relative:")
        g = [ln for ln in self.good_lines() if "mcjob" not in ln]
        g[1:1] = ['100 chdir("/") = 0', '100 stat("x.txt", 0x7ffd) = -1 ENOENT (No such file or directory)']
        self.assertTrue(self.check(g)["pass"])                         # a failed probe stays an observation
        g.insert(3, '100 openat(AT_FDCWD, "data.txt", O_RDONLY) = 3')
        self.assert_fails(self.check(g), "cwd-unknown:")

    def test_a_final_link_under_dotdot_resolves_outside(self):
        (self.W / "sub").mkdir()
        out = self.tmp / "outside"
        out.mkdir()
        (out / "data.txt").write_text("x")
        (self.W / "sub/data.txt").symlink_to(out / "data.txt")
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{self.W}/sub/../sub/data.txt", O_RDONLY) = 3')
        self.assert_fails(self.check(g), "dotdot-outside-roots:")

    def test_writes_stay_in_w(self):
        W = self.W
        for line in ('100 openat(AT_FDCWD, "/tmp/pg-x.txt", O_WRONLY|O_CREAT|O_TRUNC, 0644) = 3',
                     '100 openat(AT_FDCWD, "/tmp/pg-x.txt", O_RDWR) = 3',
                     f'100 rename("{W}/a", "/tmp/pg-b") = 0', '100 unlink("/tmp/pg-c") = 0',
                     f'100 renameat2(AT_FDCWD, "/tmp/pg-d", AT_FDCWD, "{W}/d", 0) = 0',
                     f'100 link("/etc/hosts", "{W}/h") = 0', '100 symlink("x", "/tmp/pg-l") = 0',
                     '100 unlinkat(AT_FDCWD, "/tmp/pg-e", 0) = 0', '100 symlinkat("x", AT_FDCWD, "/tmp/pg-f") = 0',
                     '100 linkat(AT_FDCWD, "/etc/hosts", AT_FDCWD, "/tmp/pg-g", 0) = 0',
                     '100 renameat(AT_FDCWD, "/tmp/pg-h", AT_FDCWD, "/tmp/pg-i") = 0'):
            with self.subTest(line):
                g = self.good_lines()
                g.insert(1, line)
                rec = self.check(g)
                self.assert_fails(rec, "write-outside-w:")
                self.assertFalse([p for p in rec["problems"] if p.startswith("undecodable")])
        for line in ('100 openat(AT_FDCWD, "/dev/null", O_WRONLY) = 3', f'100 rename("{W}/a", "{W}/b") = 0',
                     f'100 unlink("{W}/c") = 0', '100 unlink("/tmp/pg-c") = -1 ENOENT (No such file or directory)',
                     f'100 mkdir("{W}/d", 0755) = 0'):
            with self.subTest(line):
                g = self.good_lines()
                g.insert(1, line)
                rec = self.check(g)
                self.assertTrue(rec["pass"], rec["problems"])

    def test_genies_search_list_from_the_trace(self):
        g, C, b = self.genie, self.C, "ModelConfiguration.xml"
        good = self.good_lines()
        i = next(k for k, ln in enumerate(good) if f'openat(AT_FDCWD, "{g}/{C}/G21_11a/{b}"' in ln)
        x = list(good)
        x.insert(i, f'100 access("/evil/{b}", F_OK) = -1 ENOENT (No such file or directory)')     # GALGCONF, say
        self.assert_fails(self.check(x), "search-path:")
        x = [ln for ln in good if "G21_11a_00_000/ModelConfiguration" not in ln]                  # a directory skipped
        self.assert_fails(self.check(x), "search-probes:")
        x = list(good)
        x.insert(i, f'100 access("{g}/{C}/G21_11a/G21_11a_00_000/{b}", F_OK) = 0')               # found earlier
        self.assert_fails(self.check(x), "search-probes:")
        x = [ln.replace("G21_11a_00_000/ModelConfiguration.xml\", F_OK) = -1 ENOENT (No such file or directory)",
                        "G21_11a_00_000/ModelConfiguration.xml\", F_OK) = 0") for ln in good
             if f'access("{g}/{C}/G21_11a/{b}"' not in ln]                       # found in the tune dir, read elsewhere
        self.assert_fails(self.check(x), "search-probes:")
        x = list(good)                                                     # the same lookup twice: two whole runs
        x[i:i] = [ln for ln in good if "access(" in ln and b in ln]
        self.assertTrue(self.check(x)["pass"], self.check(x)["problems"])
        mc = f"{g}/{C}/master_config.xml"                                  # an explicit path, tried in each dir
        walk = self.xml(mc)[:-1]
        j = good.index(walk[0])
        for tuned in (False, True):          # after the tune is configured (K9), only its list
            x = list(good)
            x[j:j + len(walk)] = [f'100 access("{d}/{mc}", F_OK) = -1 ENOENT (No such file or directory)'
                                  for d in self.search_list(tuned)] + [f'100 access("{mc}", F_OK) = 0']
            if tuned:
                self.assertTrue(self.check(x)["pass"], self.check(x)["problems"])
            else:
                self.assert_fails(self.check(x), "search-phase:")
        x[j:j + 1] = []                                                    # one directory not tried
        self.assert_fails(self.check(x), "search-probes:")

    def test_root_and_genie_libraries_come_from_cvmfs(self):
        g = self.good_lines()
        g.insert(1, '100 openat(AT_FDCWD, "/usr/lib64/libCore.so", O_RDONLY|O_CLOEXEC) = 3')
        self.assert_fails(self.check(g), "so-not-cvmfs:")
        g = self.good_lines()
        g.insert(1, '100 openat(AT_FDCWD, "/usr/lib64/libxml2.so.2", O_RDONLY|O_CLOEXEC) = 3')
        self.assertTrue(self.check(g)["pass"])
        rec = self.check()
        lib = str(self.genie / self.P / "lib/libGFwEG.so")
        got = {x["path"]: x for x in rec["libraries"]}
        self.assertEqual(got[lib]["sha256"], sha((self.genie / self.P / "lib/libGFwEG-3.04.00.so").read_bytes()))


class Round4Checks(Tmp):
    def test_the_device_walk_refuses_another_mount(self):
        other = "/proc" if os.path.isdir("/proc/self") else "/dev"          # another mount on either host
        probs = V.device_walk_problems("/", only={os.path.basename(other)})
        self.assertTrue(any(p.startswith("members-device:") for p in probs), probs)
        self.assertEqual(V.device_walk_problems(str(self.tmp)), [])

    def test_the_revision_may_change_only_with_every_cvmfs_file_rehashed(self):
        f = self.tmp / "a.xml"
        f.write_text("a")
        recs = [{"gated": [{"path": str(f), "sha256": sha(b"a"), "match": True}]}]
        same = {"revision": "5", "root_hash": "h"}
        self.assertEqual(V.revision_problems(same, dict(same), recs, repo=str(self.tmp)), [])
        moved = {"revision": "6", "root_hash": "k"}
        self.assertEqual(V.revision_problems(same, moved, recs, repo=str(self.tmp)), [])
        self.assertIn("revision-unverified", {p.split(":")[0] for p in V.revision_problems(same, moved, [], repo=str(self.tmp))})
        f.write_text("b")
        self.assertIn("revision-rehash", {p.split(":")[0] for p in V.revision_problems(same, moved, recs, repo=str(self.tmp))})
        self.assertEqual(V.revision_problems(same, dict(same), recs, repo=str(self.tmp)), [])     # unchanged: no rehash
        bad = [{"gated": [{"path": str(f), "sha256": sha(b"b"), "match": False}]}]
        self.assertIn("revision-rehash", {p.split(":")[0] for p in V.revision_problems(same, moved, bad, repo=str(self.tmp))})


KNOT = '<spline name="genie::X/Default/nu:{nu};tgt:{tgt};N:2112;proc:Weak[CC],QES;" nknots="2">\n{knots}</spline>\n'


class Round4Reduce(Tmp):
    PAIRS = {("14", "1000060120"), ("14", "1000010010")}

    def write(self, name, splines, tune="G21_11a_00_000"):
        body = (f'<genie_xsec_spline_list version="3.00" uselog="1">\n<genie_tune name="{tune}">\n'
                + "".join(KNOT.format(nu=n, tgt=t, knots=k) for n, t, k in splines) + "</genie_tune>\n</genie_xsec_spline_list>\n")
        p = self.tmp / name
        p.write_text(body)
        return str(p)

    K = "<knot> <E> 1 </E> <xsec> 2 </xsec> </knot>\n<knot> <E> 3 </E> <xsec> 4 </xsec> </knot>\n"

    def codes(self, src, red):
        return {p.split(":")[0] for p in V.reduce_problems(src, red, self.PAIRS)}

    def test_knot_values_tune_and_duplicates(self):
        both = [(14, 1000060120, self.K), (14, 1000010010, self.K)]
        src = self.write("src.xml", both + [(12, 1000060120, self.K)])
        self.assertEqual(self.codes(src, self.write("ok.xml", both)), set())
        self.assertIn("reduce-incomplete", self.codes(src, self.write("v.xml", [(14, 1000060120, self.K.replace("> 4 <", "> 5 <")),
                                                                                  (14, 1000010010, self.K)])))
        self.assertIn("reduce-incomplete", self.codes(src, self.write("t.xml", both, tune="G18_02a_00_000")))
        self.assertIn("reduce-duplicate", self.codes(src, self.write("d.xml", both + [(14, 1000010010, self.K)])))


class Round4Coverage(Tmp):
    def test_every_pair_is_needed_and_every_need_is_in_the_reduced_spline(self):
        need = lambda t: f"x : Need xsec spline for nu:14;tgt:{t};N:2112;proc:Weak[CC],QES;"
        found = "x : Spline was found"
        pairs = {("14", "1000060120"), ("14", "1000010010")}
        keys = {f"nu:14;tgt:{t};N:2112;proc:Weak[CC],QES;" for t in ("1000060120", "1000010010")}
        log = "\n".join([need("1000060120"), found, need("1000010010"), found])
        self.assertEqual(V.coverage_problems(log, pairs, keys), [])
        one = "\n".join([need("1000010010"), found])
        self.assertIn("coverage-pair", {p.split(":")[0] for p in V.coverage_problems(one, pairs, keys)})
        self.assertIn("coverage-key", {p.split(":")[0] for p in V.coverage_problems(log, pairs, keys - {min(keys)})})

    def test_the_cli_takes_the_pairs_and_keys(self):
        import contextlib
        red = self.tmp / "red.xml"
        red.write_text("<genie_xsec_spline_list>\n" + "".join(
            f'<spline name="genie::X/D/nu:14;tgt:{t};N:2112;proc:Weak[CC],QES;" nknots="1">\n<knot> 1 2 </knot>\n'
            f'</spline>\n' for t in ("1000060120", "1000010010")) + "</genie_xsec_spline_list>\n")
        log = self.tmp / "g.log"
        log.write_text("x : Need xsec spline for nu:14;tgt:1000010010;N:2112;proc:Weak[CC],QES;\nx : Spline was found\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = V.main(["coverage-log", "--log", str(log), "--script", str(GENIE / "run_gevgen_v3.sh"), "--reduced", str(red)])
        self.assertEqual(rc, 1)
        self.assertEqual([p.split(":")[0] for p in json.loads(out.getvalue())["problems"]], ["coverage-pair"])

    def test_the_coverage_block_assigns_nothing_else(self):
        s = (GENIE / "run_gevgen_v3.sh").read_text()
        cov = '    N=1; SEED=123456789; MSG="$MSGFILE"'
        self.assertEqual(V.argv_problems(s), [])
        bad = s.replace(cov, cov + "\n    TUNE=G18_02a_00_000")
        self.assertIn("argv-coverage", {p.split(":")[0] for p in V.argv_problems(bad)})
        pos = "    TUNE=$1; SPLDIR=$2; WORK=$3; FLUX=$4; MSGFILE=$5\n"
        early = s.replace(pos, pos + "    TUNE=G18_02a_00_000\n")                  # before the tail, which stays whole
        self.assertNotEqual(early, s)
        self.assertIn("argv-coverage", {p.split(":")[0] for p in V.argv_problems(early)})
        moved = s.replace(cov + "\n    gevgen_cmd > gevgen.log 2>&1", "    gevgen_cmd > gevgen.log 2>&1\n" + cov)
        self.assertNotEqual(moved, s)                                         # the seed set after gevgen has run
        self.assertIn("argv-coverage", {p.split(":")[0] for p in V.argv_problems(moved)})
        bad = s.replace('    --tune "$TUNE" \\\n', '    --tune "$TUNE" \\\n    --xml-path /evil \\\n')
        self.assertNotEqual(bad, s)
        self.assertIn("argv-xmlpath", {p.split(":")[0] for p in V.argv_problems(bad)})


class CommentScan(unittest.TestCase):
    """The bug that bit three times: an inline comment appended to a line swallowed the code that continued it.
    Fails on a comment that reads as code: a call, a comparison, a boolean, or a tuple element."""
    CODE = re.compile(r"\.get\(|\bis (True|False|None)\b|\b(and|or) [a-z_]+[.(\[]|\", \"|None\)|\)\)\s*$|^\s*\(\"")

    def offenders(self, text):
        import tokenize
        out = []
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT and self.CODE.search(tok.string[1:]):
                out.append((tok.start[0], tok.string))
        return out

    def test_no_comment_swallowed_code(self):
        files = [GENIE / n for n in ("pg_verify.py", "pg_lib.py", "gen5d_v3.py")] + [
            Path(__file__).parent / n for n in ("test_pg_verify.py", "test_covfix_pg.py")] + sorted(
            (REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/pg").glob("*/*.py")) + [
            REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/mutrun.py"]
        files = [f for f in files if f.exists()]                 # mutrun's sandbox copies a subset
        self.assertGreaterEqual(len(files), 8)
        bad = {str(f.relative_to(REPO)): self.offenders(f.read_text()) for f in files}
        self.assertEqual({k: v for k, v in bad.items() if v}, {})

    def test_the_scan_catches_the_three_past_cases(self):
        for text in ('x = (a and b   # no container and mcheck.get("pass") is True\n     and c)\n',
                     'E = [("a", "dir", None),   # the real shape ("genie_xsec/v3_04_00/NULL", "dir", None),\n     ("b",)]\n',
                     'y = f(1)   # and g(2))\n'):
            with self.subTest(text[:30]):
                self.assertTrue(self.offenders(text), text)


class NodeRecord(Tmp):
    def test_the_node_record(self):
        proc = self.tmp / "proc"
        for pid, uid in (("1", 0), ("20", os.getuid()), ("30", 4242), ("31", 999)):
            (proc / pid).mkdir(parents=True)
            (proc / pid / "status").write_text(f"Name:\tx\nUid:\t{uid}\t{uid}\t{uid}\t{uid}\n")
        mounts = "proc /proc proc rw,nosuid,nodev,noexec,relatime,hidepid=2 0 0\n/dev/sda / ext4 rw 0 0\n"
        rec = V.node_record(mounts, {"SLURM_JOB_ID": "1", "SLURM_CPUS_ON_NODE": str(os.cpu_count())}, proc=str(proc))
        self.assertEqual((rec["hidepid"], rec["slurm_job"], rec["all_cpus_allocated"]), ("2", True, True))
        self.assertEqual(rec["proc_options"], "rw,nosuid,nodev,noexec,relatime,hidepid=2")
        self.assertEqual(rec["other_user_processes"], 1 if os.getuid() != 4242 else 0)
        rec = V.node_record("proc /proc proc rw 0 0\n", {}, proc=str(proc))
        self.assertEqual((rec["hidepid"], rec["slurm_job"], rec["all_cpus_allocated"]), ("0", False, False))
        self.assertTrue(rec["pass"])                                      # a record, never a gate


class Round5(Round4):
    """Round 5 (delta-read-r5/DISPOSITIONS.md, the director's GO 2026-11-25), each against the real format: GENIE
    R-3_04_00's XML lookups (XmlParserUtils GetXMLPathList/GetXMLFilePath, AlgConfigPool's re-probe), ROOT's
    RECREATE, gntpc bound to its gevgen's GHEP, O_TRUNC, links, mkdir/mknod/truncate, exact terminal records."""

    def setUp(self):
        super().setUp()
        m = self.genie / self.C / "Messenger.xml"
        m.write_text("messenger")
        self.manifest[f"genie/v3_04_00/{self.C}/Messenger.xml"] = {"type": "file", "sha256": sha(b"messenger")}

    def test_the_untuned_list_and_algconfigpools_re_probe(self):
        m = f"{self.genie}/{self.C}/Messenger.xml"
        for tuned, recheck in ((False, False), (False, True), (True, True)):
            with self.subTest(tuned=tuned, recheck=recheck):
                g = self.good_lines()
                g[1:1] = self.xml(m, tuned=tuned, recheck=recheck)        # Messenger::Configure, before the tune
                self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])
        g = self.good_lines()
        w = self.xml(m, tuned=False)
        w.insert(-1, f'100 access("{self.genie}/{self.C}/G21_11a/Messenger.xml", F_OK) = 0')   # a re-probe elsewhere
        g[1:1] = w
        self.assert_fails(self.check(g), "search-probes:")
        g = self.good_lines()
        w = self.xml(m, tuned=False)
        g[1:1] = w[1:]                                                      # GXMLPATH's directory not tried
        self.assert_fails(self.check(g), "search-probes:")

    def test_a_searched_read_needs_its_search(self):
        ev = f"{self.genie}/{self.C}/G21_11a/EventGenerator.xml"
        g = [ln for ln in self.good_lines() if not (ln.split(" ", 1)[1].startswith("access(") and "EventGenerator" in ln)]
        self.assert_fails(self.check(g), f"search-probes: EventGenerator.xml read at {ev} with no search")

    def test_a_failed_search_before_a_found_one(self):
        mc = f"{self.genie}/{self.C}/G21_11a/ModelConfiguration.xml"
        failed = [f'100 access("{d}/ModelConfiguration.xml", F_OK) = -1 ENOENT (No such file or directory)'
                  for d in self.search_list(tuned=False)]                  # before the tune: absent everywhere
        g = self.good_lines()
        i = g.index(self.xml(mc)[0])
        g[i:i] = failed
        self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])
        g = self.good_lines()
        g[i:i] = failed[:-1]                                               # a search that stopped short
        self.assert_fails(self.check(g), "search-probes:")

    def test_an_open_consumes_freshness(self):
        twice = self.RECREATE + ('200 openat(AT_FDCWD, "genie_v3.gst.root", O_RDWR|O_CREAT, 0644) = 5',)
        self.assert_fails(self.run_role(self.gntpc(*twice), "gntpc"), "gated-mismatch:")

    def test_gntpc_reads_the_ghep_its_gevgen_wrote(self):
        gev = ('100 access("gntp.123.ghep.root", F_OK) = -1 ENOENT (No such file or directory)\n'
               '100 openat(AT_FDCWD, "gntp.123.ghep.root", O_RDWR|O_CREAT, 0644) = 7\n'
               '100 openat(AT_FDCWD, "input-flux.root", O_RDWR|O_CREAT, 0644) = 8\n')
        self.assertEqual(V.created_ghep(gev, str(self.W)), str(self.W / "gntp.123.ghep.root"))
        self.assertIsNone(V.created_ghep(gev + gev.replace("123", "124"), str(self.W)))        # two: no binding
        self.assertTrue(self.run_role(self.gntpc(*self.RECREATE), "gntpc")["pass"])
        self.assert_fails(self.run_role(self.gntpc(*self.RECREATE), "gntpc", ghep_in=str(self.W / "gntp.9.ghep.root")),
                          "gntpc-io:")
        self.assert_fails(self.run_role(self.gntpc(*self.RECREATE), "gntpc", ghep_in=None), "gntpc-input-unbound:")
        extra = ('200 openat(AT_FDCWD, "gntp.124.ghep.root", O_RDONLY) = 6',) + self.RECREATE
        self.assert_fails(self.run_role(self.gntpc(*extra), "gntpc"), "gntpc-io:")

    def test_truncation_links_and_the_new_mutations(self):
        W = self.W
        for line, code in (('100 openat(AT_FDCWD, "/tmp/pg-t", O_RDONLY|O_TRUNC) = 3', "write-outside-w:"),
                           ('100 mkdir("/tmp/pg-d", 0700) = 0', "write-outside-w:"),
                           ('100 mkdirat(AT_FDCWD, "/tmp/pg-d", 0700) = 0', "write-outside-w:"),
                           ('100 mknod("/tmp/pg-p", S_IFIFO|0600) = 0', "write-outside-w:"),
                           ('100 mknodat(AT_FDCWD, "/tmp/pg-p", S_IFIFO|0600) = 0', "write-outside-w:"),
                           ('100 truncate("/tmp/pg-f", 0) = 0', "write-outside-w:"),
                           (f'100 symlink("/etc/hosts", "{W}/l") = 0', "link-made:"),
                           (f'100 link("{W}/a", "{W}/b") = 0', "link-made:"),
                           (f'100 symlinkat("/etc", AT_FDCWD, "{W}/e") = 0', "link-made:")):
            with self.subTest(line):
                g = self.good_lines()
                g.insert(1, line)
                rec = self.check(g)
                self.assert_fails(rec, code)
                self.assertFalse([p for p in rec["problems"] if p.startswith("undecodable")])
        g = self.good_lines()
        g.insert(1, '100 mkdir("/tmp/pg-d", 0700) = -1 EEXIST (File exists)')        # failed: nothing changed
        self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])

    def test_terminal_records_are_exact(self):
        codes = lambda t: {p.split(":")[0] for p in V.trace_problems(t, 0)}
        ok = '9 openat(AT_FDCWD, "/x", O_RDONLY) = 3\n9 +++ exited with 0 +++\n'
        self.assertEqual(codes(ok), set())
        self.assertIn("terminal-malformed", codes(ok.replace("+++\n", "+++ junk\n")))
        self.assertIn("after-terminal", codes(ok + '9 access("/y", F_OK) = 0\n'))
        self.assertIn("unfinished-overwritten", codes('9 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>\n'
                                                      '9 access("/y", F_OK <unfinished ...>\n'
                                                      '9 <... access resumed>) = 0\n9 +++ exited with 0 +++\n'))
        self.assertEqual(codes('9 +++ killed by SIGKILL +++\n'), {"killed", "initial-exit"})

    def test_the_genie_block_assigns_only_f1s_inputs(self):
        s = (GENIE / "run_gevgen_v3.sh").read_text()
        self.assertEqual(V.argv_problems(s), [])
        msg = '    MSG="$GENIE/config/Messenger_laconic.xml"\n'
        self.assertEqual(s.count(msg), 1)
        bad = s.replace(msg, msg + "    TUNE=G18_02a_00_000\n")                  # sealed-only (codex C12)
        self.assertIn("argv-genie", {p.split(":")[0] for p in V.argv_problems(bad)})


class Round5Data(Tmp):
    """Round 5: splines parsed as XML (a commented spline is not one; knots counted), every pinned CVMFS file hashed
    at the start and the end (Q1), gated links re-hashed by their real path (B8), the core-dump route recorded (Q2)."""

    def spl(self, name, body):
        p = self.tmp / name
        p.write_text(f'<genie_xsec_spline_list version="3.00" uselog="1">\n<genie_tune name="G21_11a_00_000">\n{body}'
                     "</genie_tune>\n</genie_xsec_spline_list>\n")
        return str(p)

    def test_a_commented_spline_is_not_one_and_knots_are_counted(self):
        one = ('<spline name="genie::X/D/nu:14;tgt:1000010010;N:2112;proc:Weak[CC],QES;" nknots="2">\n'
               "<knot> <E> 1 </E> <xsec> 2 </xsec> </knot>\n<knot> <E> 3 </E> <xsec> 4 </xsec> </knot>\n</spline>\n")
        pairs = {("14", "1000010010")}
        src = self.spl("src.xml", one)
        self.assertEqual(V.reduce_problems(src, self.spl("red.xml", one), pairs), [])
        hidden = self.spl("hid.xml", f"<!--\n{one}-->\n")
        self.assertIn("reduce-incomplete", {p.split(":")[0] for p in V.reduce_problems(src, hidden, pairs)})
        short = self.spl("short.xml", one.replace("<knot> <E> 3 </E> <xsec> 4 </xsec> </knot>\n", ""))
        self.assertIn("reduce-knots", {p.split(":")[0] for p in V.reduce_problems(src, short, pairs)})
        with self.assertRaises(V.Fail):                                     # not a well-formed document
            V.reduce_problems(src, self.spl("b.xml", one + "<x>"), pairs)

    def test_every_pinned_file_is_hashed(self):
        prod = self.tmp / "products"
        (prod / "genie/v3_04_00/lib").mkdir(parents=True)
        (prod / "genie/v3_04_00/lib/libA.so").write_bytes(b"a")
        (prod / "genie/v3_04_00/lib/libB.so").symlink_to("libA.so")
        extra = self.tmp / "README"
        extra.write_bytes(b"r")
        man = {"genie/v3_04_00/lib": {"type": "dir"}, "genie/v3_04_00/lib/libA.so": {"type": "file", "sha256": sha(b"a")},
               "genie/v3_04_00/lib/libB.so": {"type": "symlink", "target": "libA.so"}}
        rec = V.pin_hash(man, str(prod), {str(extra): sha(b"r")})
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertEqual((rec["files"], rec["links"]), (2, 1))
        self.assertEqual(rec["hashes"][str(prod / "genie/v3_04_00/lib/libA.so")], sha(b"a"))
        (prod / "genie/v3_04_00/lib/libA.so").write_bytes(b"A")
        self.assertEqual([p.split(":")[0] for p in V.pin_hash(man, str(prod), {})["problems"]], ["pin-mismatch"])
        (prod / "genie/v3_04_00/lib/libA.so").write_bytes(b"a")
        (prod / "genie/v3_04_00/lib/libB.so").unlink()
        (prod / "genie/v3_04_00/lib/libB.so").symlink_to("libC.so")
        self.assertEqual([p.split(":")[0] for p in V.pin_hash(man, str(prod), {})["problems"]], ["pin-link"])
        self.assertFalse(V.pin_hash({}, str(prod), {})["pass"])                # nothing hashed is not a pass

    def test_a_gated_link_re_hashes_by_its_real_path(self):
        repo = self.tmp / "cvmfs"
        repo.mkdir()
        (repo / "f.xml").write_bytes(b"x")
        (repo / "l.xml").symlink_to("f.xml")
        recs = [{"gated": [{"path": str(repo / "l.xml"), "sha256": sha(b"x"), "match": True}]}]
        start, end = {"revision": "1", "root_hash": "a"}, {"revision": "2", "root_hash": "b"}
        self.assertEqual(V.revision_problems(start, end, recs, repo=str(repo)), [])
        (repo / "f.xml").write_bytes(b"y")
        self.assertEqual([p.split(":")[0] for p in V.revision_problems(start, end, recs, repo=str(repo))],
                         ["revision-rehash"])

    def test_the_core_dump_route_is_recorded(self):
        proc = self.tmp / "proc"
        (proc / "sys/kernel").mkdir(parents=True)
        (proc / "sys/kernel/core_pattern").write_text("|/usr/lib/systemd/systemd-coredump %P\n")
        rec = V.node_record("proc /proc proc rw 0 0\n", {}, proc=str(proc))
        self.assertEqual(rec["core_pattern"], "|/usr/lib/systemd/systemd-coredump %P")
        self.assertEqual(len(rec["core_limit"]), 2)
        self.assertTrue(rec["pass"])


class Round5Drain(unittest.TestCase):
    """B9: the drain KILLs the session's survivors at every poll, against a monotonic deadline; one outside the
    session with a cwd in W is reported and never signalled; a list that cannot be read fails."""

    def run_drain(self, scans, seconds=30.0):
        t, killed = [0.0], []
        it = iter(scans)
        last = [None]

        def scan(w, sid, skip):
            last[0] = next(it, last[0])
            return last[0]
        rec, rc = V.drain("/W", 5, [], seconds, scan=scan, kill=lambda p, s: killed.append(p),
                          clock=lambda: t[0], sleep=lambda d: t.__setitem__(0, t[0] + d))
        return rec, rc, killed, t[0]

    def test_survivors_end(self):
        rec, rc, killed, _ = self.run_drain([([7], []), ([7, 8], []), ([], [])])
        self.assertEqual((rec["own"], rec["polls"], rec["left"], rc), (1, 3, 0, 0))   # the last poll confirms (K7)
        self.assertEqual(killed, [7, 7, 8])                                   # a new survivor is signalled too

    def test_the_deadline_is_monotonic_and_bounded(self):
        rec, rc, killed, t = self.run_drain([([7], [])], seconds=30.0)
        self.assertEqual((rec["left"], rc), (1, 1))
        self.assertEqual(t, 30.0)
        self.assertEqual(rec["polls"], 60)

    def test_a_foreign_process_is_reported_and_left_alone(self):
        rec, rc, killed, _ = self.run_drain([([], [9])])
        self.assertEqual((rec["foreign"], rc, killed), (1, 3, []))
        rec, rc, killed, _ = self.run_drain([([7], [9]), ([], [9])])
        self.assertEqual((rc, killed), (3, [7]))

    def test_an_unreadable_list_fails(self):
        with self.assertRaises(V.Fail):
            V.survivor_scan("/W", 0, [], proc="/nonexistent", run=lambda *a, **k: subprocess.CompletedProcess(a, 1, "", ""))

    def test_the_real_scan_finds_a_session_member_that_left_w(self):
        w = tempfile.mkdtemp(prefix="pgd-")
        self.addCleanup(shutil.rmtree, w, ignore_errors=True)
        lead = subprocess.Popen([sys.executable, "-I", "-c", "import os, time; os.setsid(); os.chdir('/'); time.sleep(30)"])
        self.addCleanup(lambda: (lead.kill(), lead.wait()))
        import time
        for _ in range(50):
            try:
                if os.getsid(lead.pid) == lead.pid:
                    break
            except ProcessLookupError:
                pass
            time.sleep(0.05)
        own, foreign = V.survivor_scan(w, lead.pid, [])
        self.assertEqual((own, foreign), ([lead.pid], []))
        side = subprocess.Popen(["sleep", "30"], cwd=w)
        self.addCleanup(lambda: (side.kill(), side.wait()))
        time.sleep(0.2)
        own, foreign = V.survivor_scan(w, lead.pid, [])
        self.assertEqual((own, foreign), ([lead.pid], [side.pid]))


class Round6(Round5):
    """Round 5's confirm read (delta-read-r5/confirm/DISPOSITIONS.md, the director's GO): GENIE's Messenger lookups
    as Messenger.cxx makes them (K1), the tuned list once the tune is configured (K9), a complete call while one is
    pending (K11), writes through a linked directory (K12), the GHEP gevgen's own (F4), every assignment form (F12)."""

    def messenger(self, m, pid=100, tuned=False):
        """Messenger::Configure: GetXMLFilePath("Messenger.xml") walks the list to the first directory with it; then
        SetPrioritiesFromXmlFile calls GetXMLFilePath on that absolute path, which probes each directory + "/" + the
        path (all absent) and returns it as given; libxml2 opens it (Messenger.cxx:103, :132; XmlParserUtils.cxx:107-125)."""
        walk = self.xml(m, pid=pid, tuned=tuned, recheck=False)[:-1]
        expl = [f'{pid} access("{d}/{m}", F_OK) = -1 ENOENT (No such file or directory)' for d in self.search_list(tuned)]
        return walk + expl + [f'{pid} openat(AT_FDCWD, "{m}", O_RDONLY) = 4']

    def test_messengers_two_lookups(self):
        m = f"{self.genie}/{self.C}/Messenger.xml"
        g = self.good_lines()
        g[1:1] = self.messenger(m)
        self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])
        g = self.good_lines()
        w = self.messenger(m)
        w[0] = w[0].replace(" = -1 ENOENT (No such file or directory)", " = 0")   # it found GXMLPATH's copy first
        g[1:1] = w
        self.assert_fails(self.check(g), "search-probes:")

    def test_once_tuned_a_process_never_walks_the_untuned_list(self):
        m = f"{self.genie}/{self.C}/Messenger.xml"
        g = self.good_lines()
        end = g.index("101 +++ exited with 0 +++")
        g[end:end] = self.xml(m, tuned=True)                                # after the tune: its list
        self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])
        g = self.good_lines()
        g[end:end] = self.xml(m, tuned=False)                               # the tune's directories skipped
        self.assert_fails(self.check(g), "search-phase:")

    def test_a_complete_call_while_one_is_pending(self):
        codes = lambda t: {p.split(":")[0] for p in V.trace_problems(t, 0)}
        self.assertIn("resume-mismatch", codes('9 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>\n'
                                               '9 access("/y", F_OK) = 0\n9 <... openat resumed>) = 3\n'
                                               '9 +++ exited with 0 +++\n'))
        self.assertEqual(codes('9 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>\n10 access("/y", F_OK) = 0\n'
                               '9 <... openat resumed>) = 3\n10 +++ exited with 0 +++\n9 +++ exited with 0 +++\n'), set())

    def test_a_write_through_a_linked_directory_leaves_w(self):
        out = self.tmp / "elsewhere"
        out.mkdir()
        (self.W / "lnk").symlink_to(out)
        W = self.W
        for line in (f'100 mkdir("{W}/lnk/d", 0700) = 0', f'100 mknod("{W}/lnk/p", S_IFIFO|0600) = 0',
                     f'100 truncate("{W}/lnk/f", 0) = 0',
                     f'100 openat(AT_FDCWD, "{W}/lnk/f", O_WRONLY|O_CREAT|O_TRUNC, 0644) = 5'):
            with self.subTest(line):
                g = self.good_lines()
                g.insert(1, line)
                self.assert_fails(self.check(g), "write-outside-w:")
        (out / "f").write_text("x")
        (self.W / "lf").symlink_to(out / "f")                               # the last component a link: followed
        for line in (f'100 truncate("{W}/lf", 0) = 0', f'100 openat(AT_FDCWD, "{W}/lf", O_WRONLY|O_TRUNC) = 5'):
            with self.subTest(line):
                g = self.good_lines()
                g.insert(1, line)
                self.assert_fails(self.check(g), "write-outside-w:")
        g = self.good_lines()
        g.insert(1, f'100 mkdir("{W}/d", 0700) = 0')                       # a real directory of W
        self.assertTrue(self.check(g)["pass"], self.check(g)["problems"])

    def test_the_ghep_is_gevgens_own(self):
        gev = ('100 execve("/b/gevgen", ["gevgen"], 0x1 /* 1 vars */) = 0\n'
               '101 openat(AT_FDCWD, "gntp.123.ghep.root", O_RDWR|O_CREAT|O_TRUNC, 0644) = 7\n')
        self.assertIsNone(V.created_ghep(gev, str(self.W)))                    # a child's, not gevgen's
        self.assertEqual(V.created_ghep(gev.replace("101 open", "100 open"), str(self.W)),
                         str(self.W / "gntp.123.ghep.root"))

    def test_every_assignment_form(self):
        s = (GENIE / "run_gevgen_v3.sh").read_text()
        msg = '    MSG="$GENIE/config/Messenger_laconic.xml"\n'
        for extra in ("    TUNE[0]=G18_02a_00_000\n", "    TUNE+=x\n", "    SEED[0]=1\n"):
            with self.subTest(extra):
                self.assertIn("argv-genie", {p.split(":")[0] for p in V.argv_problems(s.replace(msg, msg + extra))})


class Round6Drain(unittest.TestCase):
    """K7: quiet means two empty scans in a row, and a process whose state cannot be read is not a zombie."""

    def test_quiet_needs_two_empty_scans(self):
        seq = iter([([5], []), ([], []), ([7], []), ([], []), ([], [])])
        killed, t = [], [0.0]
        rec, rc = V.drain("/w", 1, [], scan=lambda *a: next(seq), kill=lambda q, s: killed.append(q),
                          clock=lambda: t[0], sleep=lambda d: t.__setitem__(0, t[0] + d))
        self.assertEqual((killed, rc), ([5, 7], 0))                         # 7 came after one empty scan
        seq2 = iter([([5], []), ([], [])])
        t = [0.0]
        clock = iter([0.0, 0.0, 31.0, 31.0, 31.0])
        rec, rc = V.drain("/w", 1, [], scan=lambda *a: next(seq2), kill=lambda q, s: None,
                          clock=lambda: next(clock), sleep=lambda d: None)
        self.assertEqual(rc, 1)                                             # the deadline came before a second empty

    def test_an_unreadable_state_is_not_a_zombie(self):
        child = subprocess.Popen(["sleep", "30"], start_new_session=True)
        self.addCleanup(lambda: (child.kill(), child.wait()))
        proc = Path(tempfile.mkdtemp(prefix="pg-proc-"))
        self.addCleanup(shutil.rmtree, proc, ignore_errors=True)
        (proc / "self").mkdir()
        (proc / str(child.pid)).mkdir()                                     # no stat: a read that failed
        (proc / "99999999").mkdir()                                         # gone
        own, foreign = V.survivor_scan("/nonexistent-w", child.pid, [], proc=str(proc))
        self.assertEqual((own, foreign), ([child.pid], []))


class Round7Drain(unittest.TestCase):
    """Round 6's confirm read (R2, the director's ruling): /proc/PID/stat holds the command name as raw bytes."""

    def test_a_name_that_is_not_utf8(self):
        child = subprocess.Popen(["sleep", "30"], start_new_session=True)
        self.addCleanup(lambda: (child.kill(), child.wait()))
        proc = Path(tempfile.mkdtemp(prefix="pg-proc-"))
        self.addCleanup(shutil.rmtree, proc, ignore_errors=True)
        (proc / "self").mkdir()
        (proc / str(child.pid)).mkdir()
        (proc / str(child.pid) / "stat").write_bytes(b"%d (\xff\xfe) x) S 1 %d %d 0" % (child.pid, child.pid, child.pid))
        own, foreign = V.survivor_scan("/nonexistent-w", child.pid, [], proc=str(proc))
        self.assertEqual((own, foreign), ([child.pid], []))



class Round8Compat(Trace):
    """B3 run 2's exe-check STOP (the director's rulings, 2026-11-26): the compat-lib shim setup_genie_v3.sh puts first on
    LD_LIBRARY_PATH, allowed only as pinned. exe-check accepts the shim directory only at its pinned real path with each
    pinned name resolving to its pinned target and bytes; trace-check accepts a library outside the roots only at a
    pinned real path whose bytes match; pin-hash hashes each pinned library at the start and the end; minerva's CVMFS
    revision is tracked as larsoft's is."""

    def setUp(self):
        super().setUp()
        self.ext = self.tmp / "ext"                       # the targets (minerva CVMFS and the conda env on Perlmutter)
        self.ext.mkdir()
        self.shim = self.tmp / "home/.genie_compatlibs"
        self.shim.mkdir(parents=True)
        for name, target, body in (("libssl.so.10", "libssl.so.1.0.1e", b"ssl"),
                                   ("libxxhash.so.0", "libxxhash.so.0.8.2", b"xxhash"),
                                   ("libpcre.so.0", "libpcre.so.0.0.1", b"pcre")):       # in the shim, not pinned
            (self.ext / target).write_bytes(body)
            (self.shim / name).symlink_to(self.ext / target)
        self.real = {n: os.path.realpath(self.shim / n) for n in ("libssl.so.10", "libxxhash.so.0", "libpcre.so.0")}
        self.compat = (os.path.realpath(self.shim), {"libssl.so.10": (self.real["libssl.so.10"], sha(b"ssl")),
                                                     "libxxhash.so.0": (self.real["libxxhash.so.0"], sha(b"xxhash"))})
        self.lib_pins = dict(self.compat[1].values())

    def codes(self, rec):
        return {p.split(":")[0] for p in rec["problems"]}

    def ld(self, compat="pinned"):
        return V.exe_problems([], {}, ld_library_path=f"{self.shim}:/usr/lib64",
                              compat=self.compat if compat == "pinned" else compat)

    def loads(self, *names):
        g = self.good_lines()
        for i, n in enumerate(names):
            g.insert(1 + i, f'100 openat(AT_FDCWD, "{self.shim}/{n}", O_RDONLY|O_CLOEXEC) = {20 + i}')
        return g

    def test_the_pinned_shim_passes(self):
        self.assertEqual(self.ld(), [])
        rec = self.check(self.loads("libssl.so.10", "libxxhash.so.0"), lib_pins=self.lib_pins)
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertEqual({x["pinned_by"] for x in rec["gated"] if "genie_compatlibs" in x["path"]}, {"library pin"})

    def test_the_shim_unpinned_or_another_directory_stops(self):
        self.assertEqual([p.split(":")[0] for p in self.ld(compat=None)], ["ld-library-path"])
        other = (str(self.ext), self.compat[1])                              # pins for another directory
        self.assertEqual([p.split(":")[0] for p in self.ld(compat=other)], ["ld-library-path"])
        self.assertIn("so-outside-roots", self.codes(self.check(self.loads("libssl.so.10"))))   # no library pins

    def test_a_shim_entry_that_is_not_pinned_stops(self):                   # planted (1)
        codes = self.codes(self.check(self.loads("libssl.so.10", "libpcre.so.0"), lib_pins=self.lib_pins))
        self.assertIn("so-outside-roots", codes)
        self.assertIn("gated-mismatch", codes)

    def test_a_pinned_name_pointing_at_another_target_stops(self):          # planted (2)
        (self.shim / "libssl.so.10").unlink()
        (self.shim / "libssl.so.10").symlink_to(self.ext / "libpcre.so.0.0.1")
        self.assertEqual([p.split(":")[0] for p in self.ld()], ["compat-target"])
        self.assertIn("so-outside-roots", self.codes(self.check(self.loads("libssl.so.10"), lib_pins=self.lib_pins)))

    def test_a_pinned_target_with_other_bytes_stops(self):                  # planted (3)
        (self.ext / "libxxhash.so.0.8.2").write_bytes(b"other")
        self.assertEqual([p.split(":")[0] for p in self.ld()], ["compat-sha"])
        codes = self.codes(self.check(self.loads("libxxhash.so.0"), lib_pins=self.lib_pins))
        self.assertIn("so-pin-mismatch", codes)
        self.assertIn("so-outside-roots", codes)

    def test_a_minerva_revision_change_rehashes_its_libraries(self):        # planted (4)
        from contextlib import redirect_stdout
        repo = str(self.ext)                                                 # minerva's place in this test
        lab = {"revision": "1250", "root_hash": "l"}
        tc = self.tmp / "tc.json"
        tc.write_text(json.dumps({"libraries": [{"path": f"{self.shim}/libssl.so.10", "real": self.real["libssl.so.10"],
                                                 "sha256": sha(b"ssl")}]}))

        def compare(start, end, repos=(repo,)):
            files = []
            for w, r in (("start", start), ("end", end)):
                f = self.tmp / f"rev_{w}.json"
                f.write_text(json.dumps(dict(lab, repos=r)))
                files.append(str(f))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = V.main(["revision-compare", "--start", files[0], "--end", files[1], "--trace-check", str(tc)]
                            + sum((["--repo", x] for x in repos), []))
            return rc, json.loads(buf.getvalue().strip().splitlines()[-1])

        same = {repo: {"revision": "2719", "root_hash": "a"}}
        moved = {repo: {"revision": "2720", "root_hash": "b"}}
        self.assertEqual(compare(same, same)[0], 0)
        rc, rec = compare(same, moved)                                       # changed, and its library re-hashes
        self.assertEqual((rc, rec["repos"][repo]["changed"]), (0, True))
        (self.ext / "libssl.so.1.0.1e").write_bytes(b"changed")
        rc, rec = compare(same, moved)
        self.assertEqual(rc, 1)
        self.assertIn("revision-rehash", {p.split(":")[0] for p in rec["problems"]})
        rc, rec = compare(same, {})                                          # not recorded at the end
        self.assertEqual(rc, 1)
        self.assertIn("revision-repo-missing", {p.split(":")[0] for p in rec["problems"]})

    def test_the_conda_library_changed_between_start_and_end_stops(self):  # the director's planted test
        pins = {self.real["libxxhash.so.0"]: sha(b"xxhash")}
        self.assertTrue(V.pin_hash({}, str(self.tmp), pins)["pass"])          # the run's start
        (self.ext / "libxxhash.so.0.8.2").write_bytes(b"conda changed it")
        end = V.pin_hash({}, str(self.tmp), pins)                             # the run's end
        self.assertFalse(end["pass"])
        self.assertEqual([p.split(":")[0] for p in end["problems"]], ["pin-mismatch"])

    def test_compat_pins_are_read_strictly(self):
        good = {"dir": "/s", "libs": {"libssl.so.10": {"real": "/m/libssl.so.1.0.1e", "sha256": "a" * 64}}}
        f = self.tmp / "pins.json"
        f.write_text(json.dumps({"compat_libs": good}))
        self.assertEqual(V.compat_pins(str(f)), ("/s", {"libssl.so.10": ("/m/libssl.so.1.0.1e", "a" * 64)}))
        for bad in ({}, dict(good, dir="s"), dict(good, libs={}),
                    dict(good, libs={"a/b": good["libs"]["libssl.so.10"]}),
                    dict(good, libs={"libssl.so.10": {"real": "m", "sha256": "a" * 64}}),
                    dict(good, libs={"libssl.so.10": {"real": "/m", "sha256": "A" * 64}})):
            with self.subTest(bad):
                f.write_text(json.dumps({"compat_libs": bad}))
                with self.assertRaises(V.Fail):
                    V.compat_pins(str(f))

    def test_a_pinned_library_outside_any_gated_name(self):              # GENIE_COMPAT may name another directory
        other = self.tmp / "compat"
        other.mkdir()
        (other / "libssl.so.10").symlink_to(self.ext / "libssl.so.1.0.1e")
        g = self.good_lines()
        g.insert(1, f'100 openat(AT_FDCWD, "{other}/libssl.so.10", O_RDONLY|O_CLOEXEC) = 20')
        rec = self.check(g, lib_pins=self.lib_pins)
        self.assertTrue(rec["pass"], rec["problems"])                          # its real path and bytes, and nothing else
        self.assertIn("so-outside-roots", self.codes(self.check(g)))

    def pins_file(self):
        f = self.tmp / "pg_pins.json"
        f.write_text(json.dumps({"compat_libs": {"dir": self.compat[0], "libs": {
            n: {"real": r, "sha256": h} for n, (r, h) in self.compat[1].items()}},
            "interpreter_tools": {"/usr/bin/ls": "3" * 64}}))
        return str(f)

    def test_the_cli_passes_the_compat_pins(self):
        from contextlib import redirect_stdout
        from unittest import mock
        seen = {}

        def fake(*a, **kw):
            seen.update(kw)
            return {"pass": True, "problems": []}
        files = {}
        for k in ("record", "manifest", "private-members"):
            files[k] = self.tmp / f"{k}.json"
            files[k].write_text(json.dumps({"members": {}}))
        argv = ["trace-check", "--trace", str(self.tmp / "none.trace"), "--rc", "0", "--role", "gevgen", "--tune", "T",
                "--spline", "s", "--spline-sha256", "0" * 64, "--cwd", str(self.W), "--w-root", str(self.W),
                "--out", str(self.tmp / "tc.json"), "--compat-pins", self.pins_file()]
        for k, f in files.items():
            argv += ["--" + k, str(f)]
        with mock.patch.object(V, "trace_check", fake), redirect_stdout(io.StringIO()):
            V.main(argv)
        self.assertEqual(seen.get("lib_pins"), self.lib_pins)
        self.assertEqual(seen.get("interp_pins"), {"/usr/bin/ls": "3" * 64})      # round 9: the same file's family
        man = self.tmp / "man.json"
        man.write_text(json.dumps({"members": {}}))
        for pins, want in ((self.pins_file(), []), (None, ["ld-library-path"])):
            buf = io.StringIO()
            with redirect_stdout(buf):
                V.main(["exe-check", "--manifest", str(man), "--path", "/usr/bin/true", "--ld-library-path", str(self.shim)]
                       + (["--compat-pins", pins] if pins else []))
            probs = json.loads(buf.getvalue().strip().splitlines()[-1])["problems"]
            self.assertEqual([p.split(":")[0] for p in probs if p.startswith("ld-") or p.startswith("compat")], want)

    def test_the_revision_of_each_repository(self):
        from contextlib import redirect_stdout
        from unittest import mock
        vals = {("/a", "user.revision"): b"1250", ("/a", "user.root_hash"): b"l",
                ("/b", "user.revision"): b"2719", ("/b", "user.root_hash"): b"m"}
        buf = io.StringIO()
        with mock.patch.object(V.os, "getxattr", lambda p, k: vals[(p, k)], create=True), redirect_stdout(buf):
            rc = V.main(["revision", "--repo", "/a", "--repo", "/b"])
        rec = json.loads(buf.getvalue().strip().splitlines()[-1])
        self.assertEqual((rc, rec["revision"], rec["root_hash"]), (0, "1250", "l"))       # larsoft's, as before
        self.assertEqual(rec["repos"], {"/a": {"revision": "1250", "root_hash": "l"},
                                        "/b": {"revision": "2719", "root_hash": "m"}})

    def test_the_repository_pins_are_the_evidence(self):
        """pg_pins.json's compat_libs and minerva_repo equal B3's committed library evidence (install/b3-diag)."""
        pins = json.loads((Path(V.__file__).parent / "pg_pins.json").read_text())
        diag = Path(V.__file__).parents[2] / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/install/b3-diag"
        libs = (diag / "b3-libs.out").read_text()
        self.assertEqual(pins["compat_libs"]["dir"], "/global/u2/j/josephrb/.genie_compatlibs")
        self.assertEqual(sorted(pins["compat_libs"]["libs"]), ["libcrypto.so.10", "libssl.so.10", "libxxhash.so.0"])
        for name, v in pins["compat_libs"]["libs"].items():                   # each a needed name, at its measured target
            self.assertRegex(libs, rf"\('{re.escape(name)}', '[^']+', '/global/homes/j/josephrb/\.genie_compatlibs', "
                                   rf"'{re.escape(v['real'])}'\)")
            self.assertRegex(libs, rf"  {re.escape(name)} -> {re.escape(v['real'])} \d+ {v['sha256']}\n")
        xx = (diag / "b3-xxhash.out").read_text()
        self.assertIn("MATCH: soname libxxhash.so.0 = True; libCore's 3 undefined XXH symbols all defined = True", xx)
        m = pins["minerva_repo"]
        self.assertEqual(m["repo"], "/cvmfs/minerva.opensciencegrid.org")
        self.assertIn(f"/cvmfs/minerva.opensciencegrid.org user.revision {m['baseline_revision']}\n", xx)
        self.assertIn(f"/cvmfs/minerva.opensciencegrid.org user.root_hash {m['baseline_root_hash']}\n", xx)


class Round9(Round4):
    """B3 run 3's STOP at the graphs trace check (the director's rulings, 2026-11-27; RULINGS-A2.md round 9), all 365
    problems explained by five causes: (i) gspl2root's chdir to its own cwd made every later relative path unknown;
    (ii) ROOT 6.22's interpreter runs sh, ls, sed, g++, cc1plus, ldd and the two loaders as child processes; (iii)
    ldd's 32-bit loader probe exits 1; (iv) gcc and cling look at three system directories through '..'; (v) GENIE adds
    a tune's own directory to its list only when it exists. The fixtures are run 3's own lines (b3-run3-diag2.out)."""
    DIAG = REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/install/b3-diag"

    def setUp(self):
        super().setUp()
        from unittest import mock
        self.gcc = self.repo / "products/gcc/v9_3_0/Linux64bit+3.10-2.17"
        for rel in ("bin/g++", "libexec/gcc/x86_64-pc-linux-gnu/9.3.0/cc1plus"):
            (self.gcc / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.gcc / rel).write_text(rel)
        self.sysd = self.tmp / "sys/include/bits"                  # a stand-in for /usr/include/bits
        self.sysd.mkdir(parents=True)
        for name, value in (("GCC", str(self.gcc)), ("DOTDOT_SYSTEM_DIRS", ("/", str(self.sysd)))):
            p = mock.patch.object(V, name, value, create=True)    # create: the red check runs this on HEAD's module
            p.start()
            self.addCleanup(p.stop)
        real = os.path.realpath
        p = mock.patch("os.path.realpath", lambda q, *a, **k: "/usr/bin/bash" if q == "/bin/sh" else real(q, *a, **k))
        p.start()
        self.addCleanup(p.stop)
        self.exe = str(self.genie / self.P / "bin/gspl2root")
        self.fake = {"/usr/bin/bash": "b" * 64, "/usr/bin/ls": "c" * 64, "/usr/bin/sed": "d" * 64,
                     "/usr/bin/ldd": "e" * 64, "/lib/ld-linux.so.2": "1" * 64, "/lib64/ld-linux-x86-64.so.2": "2" * 64,
                     str(self.gcc / "bin/g++"): "4" * 64,
                     str(self.gcc / "libexec/gcc/x86_64-pc-linux-gnu/9.3.0/cc1plus"): "5" * 64}
        self.pins = dict(self.fake)

    def sha(self, p):
        return self.fake.get(p) or V.sha_path(p)

    def codes(self, rec):
        return {p.split(":")[0] for p in rec["problems"]}

    @staticmethod
    def q(s, cut=False):
        return '"' + s.replace("\\", "\\\\") + '"' + ("..." if cut else "")

    def ex(self, pid, path, *argv):
        """An execve line; each argv item is a string, or (string, True) for one strace cut at 32 characters."""
        items = [self.q(*a) if isinstance(a, tuple) else self.q(a) for a in argv]
        return f'{pid} execve({self.q(path)}, [{", ".join(items)}], 0x1 /* 9 vars */) = 0'

    def family(self):
        """Run 3's interpreter execs (b3-run3-diag2.out section 2), on this fixture's program and gcc: {pid: lines}."""
        e32, g32 = (self.exe[:32], True), (str(self.gcc)[:32], True)
        cc1 = f"{self.gcc}/bin/../libexec/gcc/x86_64-pc-linux-gnu/9.3.0/cc1plus"
        return {
            301: [self.ex(301, "/bin/sh", "sh", "-c", "--", ("LD_DEBUG=libs LD_PRELOAD=DOESNOT", True))],
            302: [self.ex(302, "/usr/bin/ls", "ls")],
            303: [self.ex(303, "/bin/sh", "sh", "-c", "--", ("LC_ALL=C g++  -O3  -xc++ -E -v /", True))],
            304: [self.ex(304, f"{self.gcc}/bin/g++", "g++", "-O3", "-xc++", "-E", "-v", "/dev/null")],
            305: [self.ex(305, "/usr/bin/sed", "sed", "-n", "-e", "/^.include/,${", "-e", "/^ \\/.*++/p", "-e", "}")],
            306: [self.ex(306, cc1, g32, "-E", "-quiet", "-v", "-iprefix", g32, "-D_GNU_SOURCE", "/dev/null",
                         "-mtune=generic", "-march=x86-64")],
            307: [self.ex(307, "/bin/sh", "sh", "-c", "--", (("ldd '" + self.exe)[:32], True)),
                  self.ex(307, "/usr/bin/ldd", "ldd", e32)],
            308: [self.ex(308, "/lib/ld-linux.so.2", "/lib/ld-linux.so.2", "--verify", e32)],
            309: [self.ex(309, "/lib64/ld-linux-x86-64.so.2", "/lib64/ld-linux-x86-64.so.2", "--verify", e32)],
            310: [self.ex(310, "/lib64/ld-linux-x86-64.so.2", "/lib64/ld-linux-x86-64.so.2", e32)]}

    def graphs(self, fam=None, exits=None, first=None):
        """A passing graphs trace (gspl2root reading its tune's files), with the family's processes before its exit."""
        g = self.good_lines()
        g[0] = first or f'100 execve("{self.exe}", ["gspl2root", "-f", "x"], 0x1 /* 3 vars */) = 0'
        fam = self.family() if fam is None else fam
        exits = {308: 1, **(exits or {})}
        mid = [ln for pid in sorted(fam) for ln in fam[pid]] + [
            f"{pid} +++ exited with {exits.get(pid, 0)} +++" for pid in sorted(fam)]
        return g[:-2] + mid + g[-2:]

    def chk(self, lines, role="graphs", pins="default", **kw):
        import inspect
        if "interp_pins" in inspect.signature(V.trace_check).parameters:      # absent on HEAD's (the red check)
            kw["interp_pins"] = self.pins if pins == "default" else pins
        return V.trace_check("\n".join(lines) + "\n", 0, role, "G21_11a_00_000", str(self.spline), sha(b"spline"),
                             str(self.W), self.record, self.manifest, self.private, str(self.W),
                             {str(self.spline): sha(b"spline")}, genie_root=str(self.genie), repo=str(self.repo),
                             private_root=str(self.priv), gxmlpath=self.xdata, xsec_data=self.xdata, sha=self.sha,
                             **kw)

    # (ii) and (iii): the interpreter family ------------------------------------------------------------------------

    def test_the_family_as_run_3_ran_it_passes(self):
        rec = self.chk(self.graphs())
        self.assertTrue(rec["pass"], rec["problems"])
        bound = [x["bound_by"] for x in rec["execs"]]
        self.assertEqual(bound, ["genie manifest"] + ["interpreter pin"] * 11, rec["execs"])
        for role in ("gevgen", "coverage", "gntpc"):                    # the other ROOT programs' roles
            with self.subTest(role):
                self.assertNotIn("interp-role", self.codes(self.chk(self.graphs(), role=role)))

    def test_without_the_pins_or_with_other_bytes_it_stops(self):
        rec = self.chk(self.graphs(), pins={})
        self.assertEqual(sum(p.startswith("exec-unbound:") for p in rec["problems"]), 11, rec["problems"])
        self.assertIn("child-exit", self.codes(rec))                    # an unbound loader's exit 1 is not excused
        pins = dict(self.pins, **{"/usr/bin/ls": "9" * 64})
        rec = self.chk(self.graphs(), pins=pins)
        self.assertEqual([p for p in rec["problems"] if p.startswith("exec-unbound")],
                         ["exec-unbound: /usr/bin/ls -> /usr/bin/ls"])

    def test_each_command_line_is_exact(self):
        e32, g32 = (self.exe[:32], True), (str(self.gcc)[:32], True)
        cc1 = f"{self.gcc}/bin/../libexec/gcc/x86_64-pc-linux-gnu/9.3.0/cc1plus"
        sh = lambda *a: [self.ex(301, "/bin/sh", *a)]
        c32 = lambda s: (s[:32], True)                  # strace's cut: each shape below fails for its own reason
        cases = {
            "ls with an argument": (302, [self.ex(302, "/usr/bin/ls", "ls", "-la")]),
            "sh -c, a short command": (301, sh("sh", "-c", "--", "ls")),
            "sh -c, another long one": (301, sh("sh", "-c", "--", c32("rm -rf /pscratch/sd/j/josephrb/covfix-pg"))),
            "sh as bash": (301, sh("bash", "-c", "--", ("LD_DEBUG=libs LD_PRELOAD=DOESNOT", True))),
            "bash by its own path": (301, [self.ex(301, "/usr/bin/bash", "sh", "-c", "--",
                                                   ("LD_DEBUG=libs LD_PRELOAD=DOESNOT", True))]),
            "an uncut 32-character command": (301, sh("sh", "-c", "--", "LD_DEBUG=libs LD_PRELOAD=DOESNOT")),
            "sh with a fifth argument": (301, sh("sh", "-c", "--", ("LD_DEBUG=libs LD_PRELOAD=DOESNOT", True), "x")),
            "a cut that is not 32": (301, sh("sh", "-c", "--", ("LD_DEBUG=libs LD_PRELOAD=DOESNO", True))),
            "sed, another script": (305, [self.ex(305, "/usr/bin/sed", "sed", "-n", "-e", "p")]),
            "g++ with an output": (304, [self.ex(304, f"{self.gcc}/bin/g++", "g++", "-O3", "-xc++", "-E", "-v",
                                                 "/dev/null", "-o", "x")]),
            "cc1plus with an output": (306, [self.ex(306, cc1, g32, "-E", "-quiet", "-v", "/dev/null", "-o", "x")]),
            "cc1plus without /dev/null": (306, [self.ex(306, cc1, g32, "-E", "-quiet", "-v", "x.cc")]),
            "cc1plus, -iprefix elsewhere": (306, [self.ex(306, cc1, g32, "-E", "-quiet", "-v", "-iprefix",
                                                          c32("/home/someone/elsewhere/gcc/v9_3_0/x"), "/dev/null")]),
            "cc1plus, a cut source": (306, [self.ex(306, cc1, g32, "-E", "-quiet", "-v", g32, "/dev/null")]),
            "cc1plus, not -E": (306, [self.ex(306, cc1, g32, "-quiet", "-v", "-E", "/dev/null")]),
            "ldd on another program": (307, [self.ex(307, "/usr/bin/ldd", "ldd", "/usr/bin/true")]),
            "ldd, a cut elsewhere": (307, [self.ex(307, "/usr/bin/ldd", "ldd",
                                                   c32("/home/someone/elsewhere/bin/gspl2root"))]),
            "ldd, a cut short of 32": (307, [self.ex(307, "/usr/bin/ldd", "ldd", (self.exe[:20], True))]),
            "the 32-bit loader without --verify": (308, [self.ex(308, "/lib/ld-linux.so.2", "/lib/ld-linux.so.2", e32)]),
            "the 32-bit loader, another option": (308, [self.ex(308, "/lib/ld-linux.so.2", "/lib/ld-linux.so.2",
                                                                "--list", e32)]),
            "the loader with an extra argument": (310, [self.ex(310, "/lib64/ld-linux-x86-64.so.2",
                                                                "/lib64/ld-linux-x86-64.so.2", "--list", e32)]),
            "an elided argv": (302, ['302 execve("/usr/bin/ls", ["ls", ...], 0x1 /* 9 vars */) = 0'])}
        for name, (pid, lines) in cases.items():
            with self.subTest(name):
                fam = self.family()
                fam[pid] = lines
                self.assertIn("interp-shape", self.codes(self.chk(self.graphs(fam))))

    def test_only_a_child_and_only_in_a_root_role(self):
        first = self.ex(100, "/bin/sh", "sh", "-c", "--", ("LD_DEBUG=libs LD_PRELOAD=DOESNOT", True))
        self.assertIn("interp-initial", self.codes(self.chk(self.graphs(first=first))))
        self.assertIn("interp-role", self.codes(self.chk(self.graphs(), role="reduce")))

    def test_only_the_32_bit_verify_probe_may_exit_1(self):
        self.assertTrue(self.chk(self.graphs())["pass"])
        for name, exits in (("the probe exits 2", {308: 2}), ("the 64-bit probe exits 1", {309: 1}),
                            ("ls exits 1", {302: 1})):
            with self.subTest(name):
                self.assertIn("child-exit", self.codes(self.chk(self.graphs(exits=exits))))

    # (i): the no-op chdir ------------------------------------------------------------------------------------------

    def test_a_chdir_to_the_cwd_changes_nothing(self):
        rel = '100 stat("GENIE/Tools/Flux", 0x7ffd) = -1 ENOENT (No such file or directory)'
        other = self.tmp / "other"
        other.mkdir()

        def with_chdir(*lines):
            g = self.graphs()
            return g[:-2] + list(lines) + [rel] + g[-2:]
        self.assertTrue(self.chk(with_chdir(f'100 chdir("{self.W}") = 0'))["pass"])
        for name, lines in (("elsewhere", [f'100 chdir("{other}") = 0']),
                            ("relative", ['100 chdir(".") = 0']),
                            ("through ..", [f'100 chdir("{self.W}/../{self.W.name}") = 0']),
                            ("back to the cwd after leaving it",
                             [f'100 chdir("{other}") = 0', f'100 chdir("{self.W}") = 0'])):
            with self.subTest(name):
                self.assertIn("cwd-unknown", self.codes(self.chk(with_chdir(*lines))))
        failed = f'100 chdir("{other}") = -1 ENOENT (No such file or directory)'
        self.assertTrue(self.chk(with_chdir(failed))["pass"])

    # (iv): '..' into a system directory ----------------------------------------------------------------------------

    def test_dotdot_into_a_system_directory_only_to_look(self):
        raw = f"{self.sysd}/x/.."
        (self.sysd / "x").mkdir()
        (self.sysd / "f.h").write_text("h")
        other = self.tmp / "sys/include/other"
        other.mkdir()

        def plus(line):
            g = self.graphs()
            return g[:-2] + [line] + g[-2:]
        for name, line in (("stat", f'100 stat("{raw}", {{st_mode=S_IFDIR|0755}}) = 0'),
                           ("access", f'100 access("{raw}", R_OK) = 0'),
                           ("the root", '100 stat("/..", {st_mode=S_IFDIR|0755}) = 0'),
                           ("a directory open", f'100 openat(AT_FDCWD, "{raw}", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 9')):
            with self.subTest(name):
                rec = self.chk(plus(line))
                self.assertTrue(rec["pass"], rec["problems"])
                self.assertIn("system directory", [x.get("allowed") for x in rec["dotdot"]])
        for name, line in (("an open without O_DIRECTORY", f'100 openat(AT_FDCWD, "{raw}", O_RDONLY) = 9'),
                           ("a directory open that creates", f'100 openat(AT_FDCWD, "{raw}", O_RDONLY|O_DIRECTORY|O_CREAT, 0755) = 9'),
                           ("another directory", f'100 stat("{other}/../other", {{st_mode=S_IFDIR|0755}}) = 0'),
                           ("a file in it", f'100 openat(AT_FDCWD, "{self.sysd}/x/../f.h", O_RDONLY) = 9'),
                           ("a file's metadata in it", f'100 stat("{self.sysd}/x/../f.h", {{st_mode=S_IFREG|0644}}) = 0')):
            with self.subTest(name):
                self.assertIn("dotdot-outside-roots", self.codes(self.chk(plus(line))))

    # (v): GENIE's list without the tune's own directory ----------------------------------------------------------

    def drop_own_dir(self):
        del self.manifest[f"genie/v3_04_00/{self.C}/G21_11a/G21_11a_00_000"]
        self.own_dir = False

    def test_genies_list_has_the_tune_directory_only_where_it_exists(self):
        self.assertTrue(self.chk(self.graphs())["pass"])               # present: GENIE walks it
        self.drop_own_dir()
        rec = self.chk(self.graphs())                                   # absent, and the walks skip it
        self.assertTrue(rec["pass"], rec["problems"])
        self.own_dir = True                                             # absent, yet a walk probes it: off the list
        self.assertIn("search-path", self.codes(self.chk(self.graphs())))
        self.own_dir = False
        self.manifest[f"genie/v3_04_00/{self.C}/G21_11a/G21_11a_00_000"] = {"type": "dir"}   # present, yet skipped
        self.assertIn("search-probes", self.codes(self.chk(self.graphs())))

    def real_walks(self):
        """Run 3's three walks (b3-run3-diag2.out section 3), moved onto this fixture: {basename: [lines]}."""
        text = (self.DIAG / "b3-run3-diag2.out").read_text()
        sec = text.split("== 3. three config files")[1].split("== 4.")[0]
        sub = (("/pscratch/sd/j/josephrb/covfix-pg/products/genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data",
                self.xdata), ("/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00", str(self.genie)),
               ("1487263 ", "100 "))
        out, cur = {}, None
        for ln in sec.splitlines():
            if ln.startswith("-- "):
                cur = out.setdefault(ln[3:].strip(), [])
            elif ln.strip() and cur is not None:
                x = ln.strip()
                for a, b in sub:
                    x = x.replace(a, b)
                cur.append(x)
        return out

    def test_the_model_is_run_3s_three_walks(self):
        self.drop_own_dir()
        walks = self.real_walks()
        self.assertEqual(sorted(walks), ["AGKY2019.xml", "ModelConfiguration.xml", "master_config.xml"])
        cfg = f"{self.genie}/{self.C}"
        for b, d in (("master_config.xml", cfg), ("ModelConfiguration.xml", f"{cfg}/G21_11a"), ("AGKY2019.xml", cfg)):
            with self.subTest(b):
                model = [ln for ln in self.xml(f"{d}/{b}") if " access(" in ln]
                real = [ln for ln in walks[b] if " access(" in ln]
                self.assertEqual([re.sub(r" = .*", "", x) for x in real], [re.sub(r" = .*", "", x) for x in model])
                self.assertEqual([x.endswith("= 0") for x in real], [x.endswith("= 0") for x in model])
        agky = f"{self.C}/AGKY2019.xml"                                # a real walk inside a full check
        (self.genie / agky).write_text(agky)
        self.manifest["genie/v3_04_00/" + agky] = {"type": "file", "sha256": sha(agky.encode())}
        g = self.graphs()
        rec = self.chk(g[:-2] + [ln.replace(" = 4", " = 11") for ln in walks["AGKY2019.xml"]] + g[-2:])
        self.assertTrue(rec["pass"], rec["problems"])

    # the parsing and the pins --------------------------------------------------------------------------------------

    def test_exec_argv(self):
        self.assertEqual(V.exec_argv('"/bin/sh", ["sh", "-c", "abc"..., "a\\\\b"], 0x1 /* 2 vars */) = 0'),
                         [("sh", False), ("-c", False), ("abc", True), ("a\\b", False)])
        self.assertEqual(V.exec_argv('"/x", [], 0x1 /* 0 vars */) = 0'), [])
        for bad in ('"/x", ["a", ...], 0x1 /* 1 vars */) = 0', '"/x", 0x1, 0x2) = 0', '"/x", ["a"'):
            with self.subTest(bad):
                self.assertIsNone(V.exec_argv(bad))

    def test_interpreter_pins_are_read_strictly(self):
        f = self.tmp / "pins.json"
        for name, d in (("missing", {}), ("empty", {"interpreter_tools": {}}),
                        ("a list", {"interpreter_tools": ["/usr/bin/ls"]}),
                        ("relative", {"interpreter_tools": {"usr/bin/ls": "a" * 64}}),
                        ("a short sha", {"interpreter_tools": {"/usr/bin/ls": "a" * 63}}),
                        ("an upper-case sha", {"interpreter_tools": {"/usr/bin/ls": "A" * 64}})):
            with self.subTest(name):
                f.write_text(json.dumps(d))
                with self.assertRaises(V.Fail):
                    V.interp_pins(str(f))
        f.write_text(json.dumps({"interpreter_tools": {"/usr/bin//ls": "a" * 64}}))
        self.assertEqual(V.interp_pins(str(f)), {"/usr/bin/ls": "a" * 64})

    def test_the_family_pins_are_the_evidence(self):
        out = (self.DIAG / "b3-interp-pins.out").read_text()
        rows = json.loads(next(ln for ln in out.splitlines() if ln.startswith("PINS "))[5:])
        want = {v["real"]: v["sha256"] for v in rows.values()}
        pins = json.loads((GENIE / "pg_pins.json").read_text())["interpreter_tools"]
        self.assertEqual(pins, want)
        self.assertEqual(len(pins), 8)
        self.assertIn("/cvmfs/larsoft.opensciencegrid.org revision 1250 root_hash "
                      "62baddee99a7b0a527fe795b86ee23f69ffbd11b\n", out)
        tools = {os.path.basename(k) for k in pins}
        for t in tools:                                                 # each pinned tool has a shape
            with self.subTest(t):
                self.assertIn(f'tool == "{t}"', (GENIE / "pg_verify.py").read_text())

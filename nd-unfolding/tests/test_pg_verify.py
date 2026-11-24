"""Controls for COVFIX PG's slot-1 verification (state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md, approved,
with the director's rulings): pg_verify.py (members-check, tool-check, trace-check), the record builder's tarball
member listing, and run_gevgen_v3.sh's open-trace prefix. No GENIE, ROOT, CVMFS or real strace is used.

Run: python3 -B -m pytest -q nd-unfolding/tests/test_pg_verify.py
"""
import hashlib
import importlib.util
import io
import json
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
F1_RUN = subprocess.run(["git", "-C", str(REPO), "show", "54a5c71b7^:3d-unfolding/genie/run_gevgen_v3.sh"],
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


GOOD = [("genie_xsec", "dir", None), ("genie_xsec/v3_04_00", "dir", None),
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
        self.assertEqual(m["genie_xsec"]["type"], "dir")

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
        return root, BR.members(str(self.tmp / "t.tar.bz2"))

    def test_members_check(self):
        root, m = self.install()
        self.assertEqual(V.members_check(str(root), m), [])
        data = root / "genie_xsec/v3_04_00/NULL/Q/data"
        for change, want in (("extra", "extra: "), ("missing", "missing: "), ("bytes", "sha256 differs"),
                             ("writable", "writable"), ("retarget", "link target differs"), ("type", "a dir, pinned")):
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
                self.assertTrue(any(want in p for p in V.members_check(str(root), m)), V.members_check(str(root), m))


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
        self.assertIn("sha256 differs from the pin", rec["problems"])
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
        for d in (cfg / "G21_11a", lib, self.rootp / "etc", self.priv / "genie_xsec", self.W / "splines"):
            d.mkdir(parents=True)
        self.files = {}
        C = "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"
        for rel in (f"{C}/G21_11a/ModelConfiguration.xml", f"{C}/G21_11a/EventGenerator.xml",
                    f"{C}/G21_11a/TuneGeneratorList.xml", f"{C}/master_config.xml", f"{C}/SuSAv2MECPXSec.xml",
                    "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG-3.04.00.so",
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
        self.record = {"tunes": {"G21_11a_00_000": {
            "model_configuration": f"{C}/G21_11a/ModelConfiguration.xml", "event_generator": f"{C}/G21_11a/EventGenerator.xml",
            "tune_generator_list": f"{C}/G21_11a/TuneGeneratorList.xml",
            "ccqe": {"registry": {"file": f"{C}/SuSAv2MECPXSec.xml"}},
            "2p2h": {"registry": {"file": f"{C}/SuSAv2MECPXSec.xml"}}}}}
        self.C = C

    def good_lines(self):
        g, C = self.genie, self.C
        return [f'100 openat(AT_FDCWD, "{self.spline}", O_RDONLY) = 3',
                f'100 access("{self.priv}/genie_xsec/data/ModelConfiguration.xml", R_OK) = -1 ENOENT (No such file or directory)',
                f'100 access("{g}/{C}/G21_11a/ModelConfiguration.xml", R_OK) = 0',
                f'100 openat(AT_FDCWD, "{g}/{C}/G21_11a/ModelConfiguration.xml", O_RDONLY) = 4',
                f'100 openat(AT_FDCWD, "{g}/{C}/G21_11a/EventGenerator.xml", O_RDONLY) = 4',
                f'100 openat(AT_FDCWD, "{g}/{C}/G21_11a/TuneGeneratorList.xml", O_RDONLY) = 4',
                f'100 openat(AT_FDCWD, "{g}/{C}/master_config.xml", O_RDONLY <unfinished ...>',
                '101 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 5',
                '100 <... openat resumed>) = 4',
                f'100 openat(AT_FDCWD, "{g}/{C}/SuSAv2MECPXSec.xml", O_RDONLY) = 4',
                f'100 openat(AT_FDCWD, "{g}/Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.so", O_RDONLY|O_CLOEXEC) = 6',
                f'100 openat(AT_FDCWD, "{g}/Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.rootmap", O_RDONLY) = 6',
                f'100 openat(AT_FDCWD, "{self.rootp}/etc/system.rootrc", O_RDONLY) = 7',
                f'100 openat(AT_FDCWD, "{self.W}/flux.root", O_RDONLY) = 8',
                '100 openat(AT_FDCWD, "genie-mcjob-123456789.status", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 9',
                '101 +++ exited with 0 +++', '100 +++ exited with 0 +++']

    def check(self, lines=None, rc=0, role="gevgen", spline_sha=None, text=None):
        text = text if text is not None else "\n".join(lines if lines is not None else self.good_lines()) + "\n"
        return V.trace_check(text, rc, role, "G21_11a_00_000", str(self.spline), spline_sha or sha(b"spline"),
                             str(self.W), self.record, self.manifest, {}, str(self.W),
                             {str(self.spline): sha(b"spline")}, genie_root=str(self.genie), repo=str(self.repo),
                             private_root=str(self.priv))

    def assert_fails(self, rec, want):
        self.assertFalse(rec["pass"])
        self.assertTrue(any(want in p for p in rec["problems"]), rec["problems"])

    def test_a_good_trace_passes(self):
        rec = self.check()
        self.assertTrue(rec["pass"], rec["problems"])
        self.assertTrue(rec["initial_opened_spline"])
        gated = {x["path"] for x in rec["gated"]}
        self.assertIn(self.files[f"{self.C}/master_config.xml"], gated)          # joined from unfinished + resumed
        self.assertIn(str(self.genie / "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.so"), gated)   # via the manifest link
        self.assertNotIn(str(self.W / "flux.root"), gated)                       # W's own "genie" does not gate it
        self.assertEqual([x["path"] for x in rec["root_config"]], [str(self.rootp / "etc/system.rootrc")])
        self.assertEqual(rec["probes"]["ModelConfiguration.xml"][0]["errno"], "ENOENT")
        self.assertEqual(len(rec["defining_files"]), 5)

    def test_completeness(self):
        g = self.good_lines()
        self.assert_fails(self.check(text=""), "the trace is empty")
        self.assert_fails(self.check(rc=1), "strace exited 1")
        self.assert_fails(self.check(g + ["100 +++ killed by SIGKILL +++"]), "was killed")
        self.assert_fails(self.check(text="\n".join(g)), "last line is truncated")
        self.assert_fails(self.check(g[:-1]), "the initial process did not exit 0")
        self.assert_fails(self.check(g + [f'100 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>']), "inside a call")

    def test_the_initial_process_must_open_the_spline(self):
        g = self.good_lines()
        g[0] = g[0].replace("100 ", "101 ", 1)
        self.assert_fails(self.check(["99 access(\"/x\", R_OK) = 0", "99 +++ exited with 0 +++"] + g),
                          "the initial process did not open the expected spline")
        self.assert_fails(self.check(spline_sha="0" * 64), "the opened spline's sha256 differs")

    def test_gated_files_match_their_pins_at_their_own_path(self):
        Path(self.files[f"{self.C}/SuSAv2MECPXSec.xml"]).write_text("changed")
        self.assert_fails(self.check(), "does not match its pin")

    def test_config_files_from_outside_the_roots(self):
        for path in ("/home/u/.rootrc", f"{self.tmp}/x/ModelConfiguration.xml", "/tmp/rootlogon.C",
                     f"{self.tmp}/lib/libGFwEG.so"):
            with self.subTest(path):
                g = self.good_lines()
                g.insert(1, f'100 openat(AT_FDCWD, "{path}", O_RDONLY) = 3')
                rec = self.check(g)
                self.assertFalse(rec["pass"])
        g = self.good_lines()
        g.insert(1, '100 openat(AT_FDCWD, "/etc/localtime", O_RDONLY|O_CLOEXEC) = 3')   # a system file, not config
        self.assertTrue(self.check(g)["pass"])

    def test_search_order_shadow(self):
        g = self.good_lines()
        g.insert(2, f'100 access("{self.priv}/genie_xsec/data/EventGenerator.xml", R_OK) = 0')
        self.assert_fails(self.check(g), "EventGenerator.xml was found at")
        g = self.good_lines()
        g.insert(2, f'100 newfstatat(AT_FDCWD, "{self.tmp}/elsewhere/master_config.xml", {{st_mode=S_IFREG}}, 0) = 0')
        self.assert_fails(self.check(g), "master_config.xml was found at")

    def test_defining_files(self):
        g = [ln for ln in self.good_lines() if "TuneGeneratorList" not in ln]
        self.assert_fails(self.check(g), "a defining file was not opened at its expected path")
        g = self.good_lines()
        g.insert(3, f'100 readlink("{self.genie}/{self.C}/G21_11a/ModelConfiguration.xml", "x", 4096) = 1')
        self.assert_fails(self.check(g), "read through a link")
        self.assertTrue(self.check([ln for ln in self.good_lines() if "TuneGeneratorList" not in ln], role="reduce")["pass"])

    def test_relative_paths(self):
        g = self.good_lines()
        rel = os.path.relpath(self.files[f"{self.C}/G21_11a/EventGenerator.xml"], self.W)
        g[4] = f'100 openat(AT_FDCWD, "{rel}", O_RDONLY) = 4'
        self.assertTrue(self.check(g)["pass"])                                    # against the initial cwd
        g.insert(4, f'100 chdir("{self.tmp}") = 0')
        self.assert_fails(self.check(g), "a defining file was not opened")        # chdir is followed
        g = self.good_lines()
        g.insert(1, '100 openat(7, "ModelConfiguration.xml", O_RDONLY) = 3')
        self.assert_fails(self.check(g), "relative to a directory descriptor")

    def test_escapes_and_writes(self):
        self.assertEqual(V._unescape(r"a\"b\\c\x41\101\n"), 'a"b\\cAA\n')
        ev = V.parse_trace('7 openat(AT_FDCWD, "/a/genie.root", O_WRONLY|O_CREAT, 0644) = 3\n')
        self.assertTrue(ev[0]["write"])


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
        for mode, name in (("genie", "gevgen"), ("graphs", "graphs_G18_10a_02_11b"), ("reduce", "reduce_G18_10a_02_11b")):
            with self.subTest(mode):
                plain = self.go(f1, mode)[1]
                p, argv = self.go(pg, mode, fd=True, PG_STRACE_FD="FD", PG_TRACE_DIR=str(tdir))
                cmd = {"genie": "gevgen", "graphs": "gspl2root", "reduce": "awk"}[mode]
                st = [x for x in argv if x.startswith("strace ")]
                self.assertEqual(len(st), 1, argv)
                self.assertEqual(st[0], f"strace -f -q -e {V.TRACE_SET} -o {tdir}/{name}.trace "
                                        + next(x for x in plain if x.startswith(cmd + " ")))
                i = argv.index(st[0])
                self.assertTrue(argv[i + 1].startswith(cmd + " "))             # strace exec'd the command directly
                self.assertEqual([x for x in argv if not x.startswith("strace ")], plain)

    def test_invalid_inputs_refuse(self):
        pg = self.script((GENIE / "run_gevgen_v3.sh").read_text(), "pg")
        tdir = self.tmp / "traces"
        tdir.mkdir()
        (tdir / "gevgen.trace").write_text("old")
        for i, env in enumerate(({"PG_STRACE_FD": "FD"}, {"PG_TRACE_DIR": str(self.tmp)},
                                 {"PG_STRACE_FD": "x9", "PG_TRACE_DIR": str(self.tmp)},
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": "rel/dir"},
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": f"{self.tmp}/a/../b"},
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": f"{self.tmp}/missing"},
                                 {"PG_STRACE_FD": "FD", "PG_TRACE_DIR": str(tdir)},
                                 {"PG_STRACE_FD": "999", "PG_TRACE_DIR": str(self.tmp)})):
            with self.subTest(i):
                p, argv = self.go(pg, "genie", fd=True if env.get("PG_STRACE_FD") == "FD" else None, **env)
                self.assertEqual(p.returncode, 2, p.stderr)
                self.assertFalse([x for x in argv if x.startswith("gevgen ")])

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

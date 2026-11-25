"""Tests for pg-probe.py (rev 4, verify only) and pg-probe-launch.py, on stub trees: no cluster, no CVMFS, no GENIE.
Includes the counterexamples of codex-school2's read 3 that still apply to the gpg check.

macOS cannot execute a descriptor (/dev/fd/N), so where a test runs a tool, pg-probe.exe() is mapped back to the path
that descriptor was opened from: the tests show which descriptor is run, and the probe's own run on the node exercises
descriptor execution itself (its strace self-test, and every gpg call).

Run: python3 -I -B test_pg_probe.py -v   (from this directory)
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PG_REPO_ROOT") or HERE.parents[6])


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P = load("pg_probe", "pg-probe.py")
LAUNCH = load("pg_probe_launch", "pg-probe-launch.py")
MP = load("make_pins", "make_pins.py")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def open_high(path):
    """A descriptor of path at 10 or more, as open_tools gives."""
    import fcntl
    low = os.open(path, os.O_RDONLY)
    fd = fcntl.fcntl(low, fcntl.F_DUPFD, 10)
    os.close(low)
    return fd


@contextlib.contextmanager
def fd_paths(fds_to_paths):
    """Map descriptors back to paths for exe() on a system that cannot execute a descriptor."""
    orig = P.exe
    if not os.path.isdir("/proc/self/fd"):
        P.exe = lambda fd: fds_to_paths[fd]
    try:
        yield
    finally:
        P.exe = orig


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(dir="/tmp"))
        self.addCleanup(self.clean)

    def clean(self):
        for d, _, _ in os.walk(self.tmp):
            os.chmod(d, 0o755)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fresh(self):
        self.clean()
        os.makedirs(self.tmp)


# ------------------------------------------------------------------------------------------------- a stub repository

C = "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"
L = "Linux64bit+3.10-2.17-e20-prof/lib"


class Stub:
    def __init__(self, root):
        self.repo = Path(root) / "cvmfs"
        self.genie = self.repo / "products/genie/v3_04_00"
        self.xsec = self.repo / "products/genie_xsec/v3_04_00/NULL"
        for d in (self.genie / C / "G21_11a", self.genie / C / "G18_02a" / "G18_02a_02_11b", self.genie / L,
                  self.genie / "ups", self.repo / "products/.upsfiles"):
            d.mkdir(parents=True, exist_ok=True)
        files = {f"{C}/G21_11a/ModelConfiguration.xml": "mc21", f"{C}/G18_02a/ModelConfiguration.xml": "mc18",
                 f"{C}/master_config.xml": "master", f"{L}/libGFwEG-3.04.00.so": "so", f"{L}/libGFwEG.rootmap": "rm",
                 "ups/genie.table": "table"}
        for rel, x in files.items():
            (self.genie / rel).write_text(x)
        (self.genie / L / "libGFwEG.so").symlink_to("libGFwEG-3.04.00.so")
        (self.genie / C / "G18_02a/G18_02a_02_11b/CommonParam.xml").write_text("cp")
        quals = ("G1802a00000-k250-e1000", "AR2320i00000-k250-e1000", "G1810a0211b-k250-e1000")
        for q in quals + ("GDNu2001a00000-k120-e200",):
            d = self.xsec / q / "data"
            d.mkdir(parents=True)
            (d / "gxspl-NUsmall.xml").write_text("spl " + q)
            (d / "README").write_text("readme " + q)
            (d / "isotopes.cfg").write_text("i")
        (self.repo / "products/.upsfiles/dbconfig").write_text("FILE = DBCONFIG\n")
        self.pins = {
            "record_sha256": "r" * 64,
            "genie_files": {rel: sha((self.genie / rel).read_bytes()) for rel in files},
            "genie_links": {f"{L}/libGFwEG.so": "libGFwEG-3.04.00.so"},
            "genie_listings": {f"{C}/G21_11a": ["ModelConfiguration.xml"], f"{C}/G21_11a/G21_11a_00_000": None,
                               f"{C}/G18_02a": ["G18_02a_02_11b/", "ModelConfiguration.xml"]},
            "xsec_files": {f"{q}/data/{f}": sha((self.xsec / q / "data" / f).read_bytes())
                           for q in quals for f in ("gxspl-NUsmall.xml", "README")},
            "required_qualifiers": sorted(quals)}
        self.mounts = f"cvmfs2 {self.repo} fuse ro 0 0\ntmpfs / tmpfs rw 0 0\n"
        self.xattrs = {"user.fqrn": "larsoft.opensciencegrid.org", "user.revision": "1249", "user.root_hash": "ea35e334"}

    def xattr(self, path, name):
        if name not in self.xattrs:
            raise OSError(61, "No data available")
        return self.xattrs[name]


def fake_ident():
    return {"host": "login05", "checks": {}, "pass": True}


# ----------------------------------------------------------------------------------------------------- verify steps

class Repo(Tmp):
    def test_fqrn_is_required_and_xattrs_recorded(self):
        s = Stub(self.tmp)
        r = P.verify_repo(str(s.repo), s.mounts, s.xattr)
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["xattrs"]["user.revision"], "1249")
        s.xattrs["user.fqrn"] = "other.org"
        self.assertFalse(P.verify_repo(str(s.repo), s.mounts, s.xattr)["pass"])
        del s.xattrs["user.fqrn"]
        r = P.verify_repo(str(s.repo), s.mounts, s.xattr)
        self.assertFalse(r["pass"])
        self.assertTrue(any(p.startswith("repo-xattr: xattr user.fqrn") for p in r["problems"]))

    def test_an_empty_revision_or_root_hash_fails(self):
        for k in ("user.revision", "user.root_hash"):
            with self.subTest(k):
                self.fresh()
                s = Stub(self.tmp)
                s.xattrs[k] = " "
                r = P.verify_repo(str(s.repo), s.mounts, s.xattr)
                self.assertIn(f"repo-xattr-empty: {k} is empty", r["problems"])

    def test_mount_rules(self):
        s = Stub(self.tmp)
        for m in (f"/dev/x {s.repo} ext4 rw 0 0\n", "/dev/x / ext4 rw 0 0\n", "nfs:/ / nfs rw 0 0\n"):
            with self.subTest(m):
                self.assertFalse(P.verify_repo(str(s.repo), m, s.xattr)["pass"])
        self.assertTrue(P.verify_repo(str(s.repo), f"cvmfs {s.repo.parent} dvs ro 0 0\n", s.xattr)["pass"])
        link = Path(self.tmp) / "link"
        link.symlink_to(s.repo)
        self.assertFalse(P.verify_repo(str(link), f"cvmfs2 {link} fuse ro 0 0\n", s.xattr)["pass"])


class Genie(Tmp):
    def test_matching_tree(self):
        s = Stub(self.tmp)
        r = P.verify_genie(str(s.genie), s.pins)
        self.assertEqual(r["problems"], [])
        self.assertTrue(all(v["match"] for k in ("files", "links", "listings") for v in r[k].values()))

    def test_every_difference_stops_and_records_the_node_value(self):
        cases = {
            "bytes": lambda s: (s.genie / C / "master_config.xml").write_text("changed"),
            "missing": lambda s: (s.genie / "ups/genie.table").unlink(),
            "extra file in a pinned listing": lambda s: (s.genie / C / "G21_11a/EventGenerator.xml").write_text("x"),
            "an absent directory present": lambda s: (s.genie / C / "G21_11a/G21_11a_00_000").mkdir(),
            "link retargeted": lambda s: ((s.genie / L / "libGFwEG.so").unlink(),
                                          (s.genie / L / "libGFwEG.so").symlink_to("libGFwEG.rootmap")),
            "a pinned file is a link": lambda s: ((s.genie / "ups/genie.table").unlink(),
                                                  (s.genie / "ups/genie.table").symlink_to("../x")),
            "a link in a directory component": lambda s: (shutil.move(str(s.genie / C / "G21_11a"),
                                                                       str(s.genie / C / "real21")),
                                                           (s.genie / C / "G21_11a").symlink_to("real21")),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.fresh()
                s = Stub(self.tmp)
                change(s)
                self.assertTrue(P.verify_genie(str(s.genie), s.pins)["problems"], name)
        self.fresh()
        s = Stub(self.tmp)
        (s.genie / C / "master_config.xml").write_text("changed")
        r = P.verify_genie(str(s.genie), s.pins)
        self.assertEqual(r["files"][f"{C}/master_config.xml"]["sha256"], sha(b"changed"))   # the node's value

    def test_each_read_rule_on_its_own(self):
        def link_dir(s):                          # a link in a component of a pinned file's path, not a pinned listing
            shutil.move(str(s.genie / "ups"), str(s.genie / "ups-real"))
            (s.genie / "ups").symlink_to("ups-real")

        def link_file(s):                         # a pinned file replaced by a link to the same bytes
            (s.genie / "ups/genie.table").rename(s.genie / "ups/real.table")
            (s.genie / "ups/genie.table").symlink_to("real.table")

        def fifo(s):
            (s.genie / C / "master_config.xml").unlink()
            os.mkfifo(s.genie / C / "master_config.xml")

        def not_a_link(s):
            (s.genie / L / "libGFwEG.so").unlink()
            (s.genie / L / "libGFwEG.so").write_text("so")
        for name, change, kind, key, want in (
                ("a link in a directory component", link_dir, "files", "ups/genie.table", None),
                ("a pinned file through a link", link_file, "files", "ups/genie.table", None),
                ("a pinned file that is a FIFO", fifo, "files", f"{C}/master_config.xml", "not a regular file"),
                ("a pinned link that is a file", not_a_link, "links", f"{L}/libGFwEG.so", "is not a link")):
            with self.subTest(name):
                self.fresh()
                s = Stub(self.tmp)
                change(s)
                item = P.verify_genie(str(s.genie), s.pins)[kind][key]
                self.assertFalse(item["match"], item)
                if want:
                    self.assertIn(want, item.get("error", ""))

    def test_the_root_must_be_its_own_real_path(self):
        s = Stub(self.tmp)
        link = Path(self.tmp) / "glink"
        link.symlink_to(s.genie)
        self.assertTrue(P.verify_genie(str(link), s.pins)["problems"])
        mid = Path(self.tmp) / "repolink"
        mid.symlink_to(s.repo)
        r = P.verify_genie(str(mid / "products/genie/v3_04_00"), s.pins)
        self.assertEqual(r["problems"], [f"genie-realpath: {mid}/products/genie/v3_04_00 is not its own real path"])

    def test_the_genie_root_on_another_device(self):
        s = Stub(self.tmp)
        r = P.verify_genie(str(s.genie), s.pins, repo="/dev")             # devfs: another device than the stub's
        self.assertEqual(r["problems"], [f"genie-mount: {s.genie} is not on the repository's device"])
        self.assertEqual(P.verify_genie(str(s.genie), s.pins, repo=str(s.repo))["problems"], [])

    def test_a_tool_that_changes_after_its_lstat(self):
        # the fstat guard behind the regular-file choice: injected, the path is a regular file at lstat, a directory at open
        d = Path(self.tmp) / "dir"
        d.mkdir()
        real = P.os.lstat
        P.os.lstat = lambda p, *a, **k: real(__file__) if p == str(d) else real(p, *a, **k)
        try:
            fds, rec = P.open_tools({"strace": (str(d),)}, NOT_OWNED)
        finally:
            P.os.lstat = real
        self.assertEqual((fds, rec["strace"].get("problem")), ({}, "not a regular file"))

    def test_a_final_directory_on_another_device(self):
        # list_rel's own final-directory check, injected: the final directory's fstat reports another device, its
        # entries none (on this host the entries check would otherwise catch a real mount first)
        s = Stub(self.tmp)
        fd = os.open(s.genie, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        real, calls = P.os.fstat, []

        def fstat(x):
            st = real(x)
            calls.append(x)
            if len(calls) == 4:      # _walk: the root, the component; list_rel: the root (dev), then the final directory
                return os.stat_result((st.st_mode, st.st_ino, st.st_dev + 1) + tuple(st)[3:])
            return st
        P.os.fstat = fstat
        try:
            with self.assertRaises(P.Unverified) as cm:
                P.list_rel(fd, "Linux64bit+3.10-2.17-e20-prof/lib")
        finally:
            P.os.fstat = real
        self.assertIn("another mount", str(cm.exception))

    @unittest.skipUnless(os.path.isdir("/proc/self"), "untested on this host: no /proc (macOS); B1 runs it on the node")
    def test_the_mount_control_on_linux(self):
        self.assertTrue(P.mount_control()["pass"])

    def test_the_mount_control_refuses_somewhere(self):
        self.assertTrue(P.mount_control("/", "dev")["pass"])             # macOS: devfs is another mount
        (Path(self.tmp) / "sub").mkdir()
        self.assertEqual(P.mount_control(str(self.tmp), "sub"), {"pass": False, "refused": None})   # same device

    def test_a_final_directory_on_another_mount(self):
        fd = os.open("/", os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertNotEqual(os.stat("/").st_dev, os.stat("/dev").st_dev)
        with self.assertRaises(P.Unverified) as cm:
            P.list_rel(fd, "dev")
        self.assertIn("another mount", str(cm.exception))

    def test_walk_refuses_odd_paths(self):
        s = Stub(self.tmp)
        fd = os.open(s.genie, os.O_RDONLY)
        try:
            for rel in ("", "/abs", "a/../b", "a//b", "./a"):
                with self.subTest(rel), self.assertRaises(P.Unverified):
                    P._walk(fd, rel)
        finally:
            os.close(fd)


class Xsec(Tmp):
    def test_matching(self):
        s = Stub(self.tmp)
        r = P.verify_xsec(str(s.repo), s.pins)
        self.assertEqual(r["problems"], [])
        self.assertIn("GDNu2001a00000-k120-e200/", r["qualifiers"])
        self.assertEqual(r["data_listings"]["G1802a00000-k250-e1000"]["names"],
                         ["README", "gxspl-NUsmall.xml", "isotopes.cfg"])
        self.assertEqual(r["dbconfig"]["sha256"], sha(b"FILE = DBCONFIG\n"))

    def test_refusals(self):
        cases = {
            "a required qualifier missing": lambda s: shutil.rmtree(s.xsec / "AR2320i00000-k250-e1000"),
            "a spline differs": lambda s: (s.xsec / "G1802a00000-k250-e1000/data/gxspl-NUsmall.xml").write_text("x"),
            "a config-like name in data/": lambda s: (s.xsec / "G1802a00000-k250-e1000/data/ModelConfiguration.xml")
                                                      .write_text("x"),
            "a name outside the data allowlist": lambda s: (s.xsec / "G1802a00000-k250-e1000/data/rootlogon.C")
                                                            .write_text("x"),
            "no dbconfig": lambda s: (s.repo / "products/.upsfiles/dbconfig").unlink(),
            "the qualifier only under another case": lambda s: (s.xsec / "AR2320i00000-k250-e1000").rename(
                s.xsec / "ar2320i00000-k250-e1000"),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.fresh()
                s = Stub(self.tmp)
                change(s)
                probs = P.verify_xsec(str(s.repo), s.pins)["problems"]
                want = {"a required qualifier missing": "xsec-qualifiers:", "a spline differs": "xsec-files:",
                        "a config-like name in data/": "xsec-data-names:", "a name outside the data allowlist":
                        "xsec-data-names:", "no dbconfig": "xsec-dbconfig:",
                        "the qualifier only under another case": "xsec-qualifiers:"}[name]
                self.assertTrue(any(x.startswith(want) for x in probs), (name, probs))

    def test_another_mount_inside_a_walk_fails(self):
        # the walks never leave the root's device: a file, a directory or a listed entry on another mount
        cases = [c for c in (("/", "dev/null", "sha"), ("/", "proc/self/status", "sha"), ("/", "System/Volumes", "list"))
                 if os.path.exists("/" + c[1])]
        cases = [c for c in cases if os.stat("/").st_dev != os.stat("/" + c[1].split("/")[0]).st_dev
                 or c[2] == "list"]
        self.assertTrue(cases, "no cross-mount path on this host")
        fd = os.open("/", os.O_RDONLY)
        self.addCleanup(os.close, fd)
        for root, rel, kind in cases:
            with self.subTest(rel), self.assertRaises(P.Unverified) as cm:
                (P.sha_rel if kind == "sha" else P.list_rel)(fd, rel)
            self.assertIn("another mount", str(cm.exception))


# ------------------------------------------------------------------------------------------------------------ tools

class Tools(Tmp):
    def make(self, name, body="#!/bin/sh\necho hi\n"):
        p = Path(self.tmp) / name
        p.write_text(body + name + "\n")
        p.chmod(0o755)
        return p

    def rpm(self, owned, digests):
        def run(args):
            if args[0] == "-qf":
                return (0, owned[args[-1]] + "\n") if args[-1] in owned else (1, f"file {args[-1]} is not owned\n")
            if args[:2] == ["-q", "--dump"]:
                return 0, "".join(f"{p} 10 0 {d} 0100755 root root 0 0 0 X\n" for p, d in digests.items())
            return 0, ""
        return run

    def test_rpm_digest_rules(self):
        a, b, c = self.make("a"), self.make("b"), self.make("c")
        tools = {"strace": (str(a),), "gpg": (str(b),), "gpgconf": (str(c),), "gpg-connect-agent": ("/nonexistent",)}
        da = sha(a.read_bytes())
        fds, rec = P.open_tools(tools, self.rpm({str(a): "strace-5", str(b): "gpg2-2"},
                                                {str(a): da, str(b): "0" * 64}))
        try:
            self.assertEqual((rec["strace"]["rpm_match"], rec["strace"]["pin_basis"]), (True, "RPM's recorded digest"))
            self.assertNotIn("problem", rec["strace"])
            self.assertIs(rec["gpg"]["rpm_match"], False)
            self.assertIn("differs from RPM's", rec["gpg"].get("problem", ""))
            self.assertEqual((rec["gpgconf"]["rpm_match"], rec["gpgconf"]["pin_basis"]),
                             (None, "first use: no RPM record"))
            self.assertEqual(rec["gpg-connect-agent"]["problem"], "missing")
            self.assertEqual(rec["strace"]["sha256"], da)
            self.assertEqual(os.lseek(fds["strace"], 0, os.SEEK_CUR), 0)        # ready to execute from the start
            self.assertTrue(all(fd >= 10 for fd in fds.values()))                # clear of gpg's fd 3
        finally:
            for fd in fds.values():
                os.close(fd)

    def test_a_directory_is_not_a_tool(self):
        d = Path(self.tmp) / "dir"
        d.mkdir()
        fds, rec = P.open_tools({"strace": (str(d),)}, NOT_OWNED)            # no crash-to-fail wrapper (agy 17)
        self.assertEqual((fds, rec["strace"].get("problem")), ({}, "no regular file among the candidates"))

    def test_a_link_is_not_a_tool(self):
        a = self.make("a")
        (Path(self.tmp) / "l").symlink_to(a)
        fds, rec = P.open_tools({"strace": (str(Path(self.tmp) / "l"),)}, NOT_OWNED)
        self.assertEqual(fds, {})
        self.assertEqual(rec["strace"]["problem"], "no regular file among the candidates")

    def test_a_linked_first_candidate_falls_through(self):
        # SLES: /usr/bin/gpg may be a link to gpg2, the second candidate (agy B1)
        b = self.make("gpg2")
        (Path(self.tmp) / "gpg").symlink_to(b)
        fds, rec = P.open_tools({"gpg": (str(Path(self.tmp) / "gpg"), b)}, NOT_OWNED)
        self.addCleanup(lambda: [os.close(fd) for fd in fds.values()])
        self.assertEqual(rec["gpg"]["path"], b)
        self.assertNotIn("problem", rec["gpg"])

    def test_a_failed_rpm_query_is_not_an_absent_record(self):
        a = self.make("a")
        fds, rec = P.open_tools({"strace": (a,)}, lambda args: None)
        self.addCleanup(lambda: [os.close(fd) for fd in fds.values()])
        self.assertEqual((rec["strace"]["rpm_status"], rec["strace"]["problem"]), ("query-failed", "the RPM query failed"))
        fds2, rec2 = P.open_tools({"strace": (a,)}, NOT_OWNED)
        self.addCleanup(lambda: [os.close(fd) for fd in fds2.values()])
        self.assertEqual((rec2["strace"]["rpm_status"], rec2["strace"]["pin_basis"]), ("not-owned", "first use: no RPM record"))


NOT_OWNED = lambda args: (1, f"file {args[-1]} is not owned by any package\n")      # no RPM record


FAKE_STRACE = r'''#!/bin/sh
while [ "$1" != "-o" ]; do shift; done; out=$2; shift 2
"$@" > /dev/null; rc=$?
MODE
exit $rc
'''
MODES = {"good": 'printf \'9 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n9 +++ exited with 0 +++\\n\' "$2" > "$out"',
         "no-open": 'printf \'9 +++ exited with 0 +++\\n\' > "$out"',
         "killed": 'printf \'9 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n9 +++ killed by SIGKILL +++\\n\' "$2" > "$out"',
         "truncated": 'printf \'9 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n9 +++ exited with 0 +++\' "$2" > "$out"',
         "empty": ': > "$out"', "rc": 'printf \'9 +++ exited with 0 +++\\n\' > "$out"; exit 4',
         "child-exit": 'printf \'9 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n10 +++ exited with 1 +++\\n9 +++ exited with 0 +++\\n\' "$2" > "$out"',
         "unresumed": 'printf \'9 openat(AT_FDCWD, "%s", O_RDONLY) = 3\\n10 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>\\n10 +++ exited with 0 +++\\n9 +++ exited with 0 +++\\n\' "$2" > "$out"'}


class SelfTest(Tmp):
    def run_mode(self, mode):
        p = Path(self.tmp) / f"st-{mode}"
        p.write_text(FAKE_STRACE.replace("MODE", MODES[mode]))
        p.chmod(0o755)
        fd = os.open(p, os.O_RDONLY)
        try:
            with fd_paths({fd: str(p)}):
                return P.strace_self_test(fd, parent=self.tmp)
        finally:
            os.close(fd)

    def test_modes(self):
        self.assertTrue(self.run_mode("good")["pass"])
        for mode, want in (("no-open", "self-test-open: "), ("killed", "killed: "), ("truncated", "truncated: "),
                           ("empty", "empty: "), ("rc", "strace-rc: strace exited 4"), ("child-exit", "child-exit: "),
                           ("unresumed", "unresumed: ")):
            with self.subTest(mode):
                r = self.run_mode(mode)
                self.assertFalse(r["pass"])
                self.assertTrue(any(x.startswith(want) for x in r["problems"]), r["problems"])
        self.assertEqual([n for n in os.listdir(self.tmp) if n.startswith("pgst")], [])     # cleaned up


# ---------------------------------------------------------------------------------------------------------- gpg

HONEST = r"""import hashlib, hmac, os, sys
open(MARK, 'a').write(' '.join(sys.argv[1:]) + '\n')
if '--version' in sys.argv: print('honest'); sys.exit(0)
pw = os.read(3, 1000).strip()
d = sys.stdin.buffer.read()
def pkt(tag, body): return (bytes([0xC0 | tag, len(body)]) if len(body) < 192 else bytes([0xC0 | tag, 255]) + len(body).to_bytes(4, 'big')) + body
if '--symmetric' in sys.argv:
    body = bytes(b ^ 0x55 for b in d) + hmac.new(pw, d, hashlib.sha256).digest()
    sys.stdout.buffer.write(pkt(3, b'\x04\x09\x03') + pkt(18, b'\x01' + body)); sys.exit(0)
b = d[5:]
body = b[6:] if b[1] == 255 else b[2:]
data, tag = bytes(x ^ 0x55 for x in body[1:-32]), body[-32:]
want = hmac.new(pw, data, hashlib.sha256).digest()
if hmac.compare_digest(tag, want):
    sys.stdout.buffer.write(data); sys.exit(0)
CRASH
if want[:-1] == tag[:-1]:
    sys.stderr.write('gpg: WARNING: encrypted message has been manipulated!\n'); sys.exit(2)
sys.stderr.write('gpg: decryption failed: Bad session key\n'); sys.exit(2)
"""
GPGCONF = r"""import hashlib, os, sys
open(MARK, 'a').write('gpgconf ' + ' '.join(sys.argv[1:]) + '\n')
h = os.environ['GNUPGHOME']
def zb(b):
    a, out = 'ybndrfg8ejkmcpqxot1uwisza345h769', ''
    for i in range(0, len(b), 5):
        s = b[i:i + 5]
        out += ''.join(a[x] for x in (s[0] >> 3, ((s[0] & 7) << 2) | (s[1] >> 6), (s[1] & 63) >> 1,
                                      ((s[1] & 1) << 4) | (s[2] >> 4), ((s[2] & 15) << 1) | (s[3] >> 7),
                                      (s[3] & 127) >> 2, ((s[3] & 3) << 3) | (s[4] >> 5), s[4] & 31))
    return out
sd = h if BASE is None else f'{BASE}/{os.getuid()}/gnupg/d.' + zb(hashlib.sha1(h.encode()).digest()[:15])
if '--list-dirs' in sys.argv:
    if sd != h and not os.path.isdir(sd):
        os.mkdir(sd, 0o700)
    print(LISTING)
if '--remove-socketdir' in sys.argv and REMOVE and sd != h:
    os.rmdir(sd)
sys.exit(KILL_RC if '--kill' in sys.argv else LIST_RC if '--list-dirs' in sys.argv else 0)
"""


class Gpg(Tmp):
    MOUNTS = "tmpfs / tmpfs rw 0 0\n"

    def bins(self, gpg_body=HONEST, conf_rc=0, agent_out="D 4242\\nOK\\n", base=None, remove=True, listing=None,
             list_rc=0):
        d = Path(self.tmp) / "fbin"
        d.mkdir(exist_ok=True)
        self.mark = Path(self.tmp) / "calls"
        if self.mark.exists():
            self.mark.unlink()
        (d / "gpg").write_text(f"#!{sys.executable}\nMARK = {str(self.mark)!r}\n" + gpg_body.replace("CRASH", ""))
        listing = listing or ("f'homedir:{h}\\nsocketdir:{sd}\\nagent-socket:{sd}/S.gpg-agent\\n"
                              "agent-ssh-socket:{sd}/S.gpg-agent.ssh'")
        (d / "gpgconf").write_text(f"#!{sys.executable}\nMARK = {str(self.mark)!r}\n" + GPGCONF.replace(
            "BASE", repr(base)).replace("LISTING", listing).replace("REMOVE", repr(remove)).replace(
            "KILL_RC", str(conf_rc)).replace("LIST_RC", str(list_rc)))
        (d / "gpg-connect-agent").write_text(f"#!/bin/sh\necho agent >> {self.mark}\nprintf '{agent_out}'\n")
        paths = {}
        for n in ("gpg", "gpgconf", "gpg-connect-agent"):
            (d / n).chmod(0o755)
            paths[n] = str(d / n)
        return paths

    def check(self, paths, mounts=None, base=None):
        fds = {k: open_high(v) for k, v in paths.items()}
        try:
            with fd_paths({fd: paths[k] for k, fd in fds.items()}):
                return P.gpg_check(fds, parent=self.tmp, mounts_text=mounts or self.MOUNTS,
                                   run_base=base or os.path.join(self.tmp, "run"))
        finally:
            for fd in fds.values():
                os.close(fd)

    def calls(self):
        return self.mark.read_text().splitlines() if self.mark.exists() else []

    def run_base(self):
        base = os.path.join(self.tmp, "run")
        os.makedirs(os.path.join(base, str(os.getuid())), mode=0o700)
        os.mkdir(os.path.join(base, str(os.getuid()), "gnupg"), 0o700)
        return base

    def test_honest_fake_passes(self):
        r = self.check(self.bins())
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["agent_pid"], 4242)
        self.assertTrue(r["gpg_started"])

    def test_a_verified_run_user_socket_dir_is_used_and_removed(self):
        base = self.run_base()
        r = self.check(self.bins(base=base), base=base)
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["socketdir_outside_home"], r["canonical_socketdir"])
        self.assertEqual(os.listdir(os.path.join(base, str(os.getuid()), "gnupg")), [])

    def test_a_socket_dir_left_behind_fails(self):
        base = self.run_base()
        r = self.check(self.bins(base=base, remove=False), base=base)
        self.assertFalse(r["socketdir_absent"])
        self.assertFalse(r["pass"])

    def test_cleanup_and_agent_identification_after_a_crypto_failure(self):
        base = self.run_base()
        r = self.check(self.bins(HONEST.replace("if '--symmetric' in sys.argv:", "if False:"), base=base), base=base)
        self.assertIn("problem", r)
        self.assertEqual(r["agent_pid"], 4242)                                   # identified though crypto failed
        self.assertTrue(r["socketdir_absent"])
        self.assertFalse(r["pass"])

    def test_a_failed_preflight_runs_nothing_else(self):
        # codex read 3, blocking 5: a failed preflight still reached gpgconf --kill
        base = self.run_base()
        g = os.path.join(base, str(os.getuid()), "gnupg")
        for name, sd in (("another hash", g + "/d.yyyy"), ("elsewhere", "/var/x")):
            with self.subTest(name):
                expr = "'homedir:' + h + " + repr(f"\nsocketdir:{sd}\nagent-socket:{sd}/S.gpg-agent")
                r = self.check(self.bins(base=base, listing=expr), base=base)
                self.assertFalse(r["confined"])
                self.assertEqual([c for c in self.calls() if "--list-dirs" not in c], [])
                self.assertNotIn("gpgconf_kill_rc", r)
                self.assertFalse(r["pass"])

    def test_a_socket_dir_inside_home_must_hold_the_sockets(self):
        # codex read 3, blocking 5: socketdir=$home/sub with agent-socket=$home/S.gpg-agent was accepted
        expr = "'homedir:' + h + '\\nsocketdir:' + h + '/sub\\nagent-socket:' + h + '/S.gpg-agent'"
        r = self.check(self.bins(listing=expr))
        self.assertFalse(r["confined"])
        self.assertTrue(any("not directly in the socket dir" in p for p in r["socket_problems"]))
        self.assertFalse(r["pass"])

    def test_run_user_must_not_be_writable_by_others(self):
        base = self.run_base()
        os.chmod(os.path.join(base, str(os.getuid())), 0o777)
        r = self.check(self.bins(base=base), base=base)
        self.assertFalse(r["pass"])
        self.assertTrue(any(p.startswith("socketdir-owner:") for p in r["socket_problems"]), r["socket_problems"])

    def test_a_socket_that_is_a_link_fails(self):
        h = os.path.realpath(self.tmp)
        os.symlink("/elsewhere", os.path.join(h, "S.gpg-agent"))
        ok, _, probs = P.check_sockets({"homedir": h, "socketdir": h, "agent-socket": h + "/S.gpg-agent"}, h,
                                       os.getuid(), "")
        self.assertFalse(ok)
        self.assertEqual(probs, [f"socket-link: agent-socket {h}/S.gpg-agent is a link"])

    def test_a_failing_list_dirs_runs_nothing_else(self):
        r = self.check(self.bins(list_rc=2))
        self.assertFalse(r["confined"])
        self.assertEqual([c for c in self.calls() if "--list-dirs" not in c], [])

    def test_check_sockets_rules(self):
        base, uid = self.run_base(), os.getuid()
        home = os.path.join(self.tmp, "home")
        os.mkdir(home, 0o700)
        sd = P.socketdir_for(home, uid, base)
        os.mkdir(sd, 0o700)
        ok = {"homedir": home, "socketdir": sd, "agent-socket": sd + "/S.gpg-agent", "dirmngr-socket": sd + "/S.dirmngr"}
        m = self.MOUNTS
        self.assertEqual(P.check_sockets(ok, home, uid, m, base), (True, sd, []))
        inhome = {"homedir": home, "socketdir": home, "agent-socket": home + "/S.gpg-agent", "keyboxd-socket": ""}
        self.assertEqual(P.check_sockets(inhome, home, uid, m, base), (True, None, []))
        for i, dirs in enumerate((dict(ok, homedir="/x"), dict(ok, **{"dirmngr-socket": "/x/S.dirmngr"}),
                                  {k: v for k, v in ok.items() if k != "agent-socket"},
                                  dict(inhome, **{"agent-extra-socket": sd + "/S.gpg-agent.extra"}),
                                  dict(inhome, socketdir=home + "/sub"))):
            with self.subTest(i):
                self.assertFalse(P.check_sockets(dirs, home, uid, m, base)[0])
        self.assertFalse(P.check_sockets(ok, home, uid + 1, m, base)[0])
        other = os.path.join(os.path.dirname(sd), "d.yyyyyyyyyyyyyyyyyyyyyyyy")
        os.mkdir(other, 0o700)
        self.assertFalse(P.check_sockets({"homedir": home, "socketdir": other, "agent-socket": other + "/S.gpg-agent"},
                                         home, uid, m, base)[0])
        self.assertFalse(P.check_sockets(ok, home, uid, "/dev/x / ext4 rw 0 0\n", base)[0])
        os.chmod(sd, 0o750)
        self.assertFalse(P.check_sockets(ok, home, uid, m, base)[0])
        os.chmod(sd, 0o700)
        link = os.path.join(self.tmp, "runlink")
        os.symlink(base, link)
        lsd = P.socketdir_for(home, uid, link)
        self.assertFalse(P.check_sockets({"homedir": home, "socketdir": lsd, "agent-socket": lsd + "/S.gpg-agent"},
                                         home, uid, m, link)[0])

    def test_controls_fail_on_their_own(self):
        cases = {"crash": dict(gpg_body=HONEST.replace("CRASH", "os.kill(os.getpid(), 11)")),
                 "no tamper evidence": dict(gpg_body=HONEST.replace("encrypted message has been manipulated", "x")),
                 "no wrong-passphrase evidence": dict(gpg_body=HONEST.replace("Bad session key", "x")),
                 "wrong passphrase accepted": dict(gpg_body=HONEST.replace(
                     "Bad session key\\n'); sys.exit(2)", "Bad session key\\n'); sys.exit(0)")),
                 "not seipd": dict(gpg_body=HONEST.replace("pkt(18,", "pkt(9,")),
                 "failed kill": dict(conf_rc=1), "unknown agent": dict(agent_out="ERR no agent\\n")}
        for name, kw in cases.items():
            with self.subTest(name):
                self.assertFalse(self.check(self.bins(**kw))["pass"])

    def test_a_surviving_agent_keeps_its_outside_socket_dir_and_fails(self):
        base = self.run_base()
        p = subprocess.Popen(["sleep", "30"])
        try:
            r = self.check(self.bins(base=base, agent_out=f"D {p.pid}\\nOK\\n"), base=base)
        finally:
            p.kill()
            p.wait()
        self.assertFalse(r["agent_gone"])
        self.assertNotIn("remove_socketdir_rc", r)                               # removed only once the agent is gone
        self.assertFalse(r["pass"])

    def test_mode_700_network_parent_missing_tool_fd3(self):
        paths = self.bins()
        orig = P.os.chmod
        try:
            P.os.chmod = lambda p, m, **kw: orig(p, 0o755, **kw)
            self.assertFalse(self.check(paths)["pass"])
        finally:
            P.os.chmod = orig
        r = self.check(paths, mounts="lus / lustre rw 0 0\n")
        self.assertIn("not a node-local filesystem", r.get("problem", ""))
        self.assertEqual(P.gpg_check({"gpg": 5}, parent=self.tmp, mounts_text=self.MOUNTS)["problem"],
                         "an approved gpg executable is missing")
        if not P._fd_open(3):
            fd = os.open(os.devnull, os.O_RDONLY)
            if fd != 3:
                os.dup2(fd, 3)
                os.close(fd)
            ino = os.fstat(3).st_ino
            try:
                r = self.check(paths)
                self.assertTrue(P._fd_open(3) and os.fstat(3).st_ino == ino, "the probe took over fd 3")
                self.assertIn("fd 3 is already open", r.get("problem", ""))
            finally:
                try:
                    os.close(3)
                except OSError:
                    pass

    def test_a_closed_stdin_is_reopened(self):
        if P._fd_open(3):
            self.skipTest("fd 3 is open in this test process")
        paths = self.bins()
        saved = 57
        os.dup2(0, saved)                 # a high fd, so that the saved copy does not itself sit on 3
        os.close(0)                       # otherwise a pipe's read end lands on 0 and its write end on 3
        try:
            r = self.check(paths)
        finally:
            os.dup2(saved, 0)
            os.close(saved)
        self.assertEqual(r["std_fds_reopened"], [0])
        self.assertTrue(r["pass"], r.get("problem"))

    def test_tamper_and_zbase32(self):
        ct = bytes([0xC3, 3, 4, 9, 3, 0xD2, 0xE1, 1, 20, 3, 30, 31, 32])
        bad = P.tamper_seipd(ct)
        self.assertEqual((bad[:-1], bad[-1]), (ct[:-1], 32 ^ 1))
        for bits, data, want in ((24, b"\xf0\xbf\xc7", "6n9hq"), (40, b"\x01" * 5, "yryonyeb"),
                                 (160, bytes.fromhex("80615870f5bad690333686d0f2ad85ac1e42b367"),
                                  "oboioh8izmmjyc3so5exfmcfioxrfc58")):
            self.assertEqual(P.zb32(data, bits), want)


@unittest.skipUnless(all(shutil.which(n) for n in ("gpg", "gpgconf", "gpg-connect-agent")), "no gpg")
class RealGpg(Tmp):
    """The local gpg (macOS, GnuPG 2.4.8), opened by descriptor, with a short /tmp parent."""

    def test_round_trip_and_controls(self):
        paths = {n: shutil.which(n) for n in ("gpg", "gpgconf", "gpg-connect-agent")}
        fds = {k: open_high(v) for k, v in paths.items()}
        try:
            with fd_paths({fd: paths[k] for k, fd in fds.items()}):
                r = P.gpg_check(fds, parent=self.tmp, mounts_text=f"x {self.tmp} tmpfs rw 0 0\n")
        finally:
            for fd in fds.values():
                os.close(fd)
        self.assertTrue(r["pass"], r)
        self.assertEqual(os.listdir(self.tmp), [])


# --------------------------------------------------------------------------------------------------- the whole probe

class Probe(Tmp):
    def run_probe(self, s, **kw):
        a = Path(self.tmp) / "t1"
        a.write_text("#!/bin/sh\n")
        tools = {k: (str(a),) for k in ("strace", "gpg", "gpgconf", "gpg-connect-agent", "awk")}
        args = dict(ident=fake_ident, repo=str(s.repo), genie_root=str(s.genie), pins=s.pins, mounts=lambda: s.mounts,
                    xattr=s.xattr, tools=tools, rpm_run=NOT_OWNED,
                    gpg=lambda fds, mounts_text=None: {"pass": True}, self_test=lambda fd: {"pass": True},
                    control=lambda: {"pass": True, "refused": "proc is another mount"})
        args.update(kw)
        return P.probe(**args)

    def test_a_failed_mount_control_stops(self):
        r = self.run_probe(Stub(self.tmp), control=lambda: {"pass": False, "refused": None})
        self.assertIn("mount-control: a walk into /proc did not refuse at its final directory", r["stops"])

    def test_go(self):
        r = self.run_probe(Stub(self.tmp))
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["schema"], "covfix-pg-probe/4")

    def test_the_probe_records_procs_mount(self):
        s = Stub(self.tmp)
        s.mounts += "proc /proc proc rw,nosuid,hidepid=invisible 0 0\n"
        r = self.run_probe(s)
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["proc_mount"], {"options": "rw,nosuid,hidepid=invisible", "hidepid": "invisible"})

    def test_identity_failure_reads_nothing(self):
        called = []
        s = Stub(self.tmp)
        r = self.run_probe(s, ident=lambda: {"host": "nid1", "checks": {}, "pass": False},
                           mounts=lambda: called.append(1) or s.mounts,
                           gpg=lambda *a, **k: called.append(2) or {"pass": True})
        self.assertEqual(r["stops"], ["identity: not a Perlmutter login node; nothing was read"])
        self.assertEqual(called, [])
        for k in ("repo", "genie", "xsec", "tools", "gpg"):
            self.assertNotIn(k, r)

    def test_each_failure_stops(self):
        s = Stub(self.tmp)
        (s.genie / C / "master_config.xml").write_text("changed")
        self.assertTrue(any(x.startswith("genie: ") for x in self.run_probe(s)["stops"]))
        s = Stub(Path(self.tmp) / "b")
        s.xattrs["user.fqrn"] = "x"
        r = self.run_probe(s)
        self.assertNotIn("genie", r)                                              # nothing read on an unverified repo
        self.assertTrue(any(x.startswith("repo: ") for x in r["stops"]))
        s = Stub(Path(self.tmp) / "c")
        self.assertIn("gpg: the tool or its pinned round trip failed",
                      self.run_probe(s, gpg=lambda fds, mounts_text=None: {"pass": False})["stops"])
        self.assertTrue(any("strace self-test" in x for x in
                            self.run_probe(s, self_test=lambda fd: {"pass": False, "problems": ["x"]})["stops"]))


class Constants(unittest.TestCase):
    def test_pins_are_the_records(self):
        self.assertEqual(P.PINS, MP.pins())
        self.assertEqual(LAUNCH.pins_of((HERE / "pg-probe.py").read_bytes()), P.PINS)
        rec = json.loads((HERE.parent / "record/PG-RECORD.json").read_bytes())
        self.assertEqual(P.PINS["record_sha256"], sha((HERE.parent / "record/PG-RECORD.json").read_bytes()))
        for t in ("G21_11a_00_000", "G18_02a_00_000", "G18_10a_02_11b", "AR23_20i_00_000"):
            for rel in rec["tunes"][t]["files"]:
                self.assertIn(rel, P.PINS["genie_files"])

    def test_spent_spline_pins_are_f1s(self):
        src = (REPO / "3d-unfolding/genie/gen5d_v3.py").read_text()
        block = src[src.index("SPLINE_PINS = {"):src.index("E_LO, E_HI")]
        for q in ("G1810a0211b-k250-e1000", "AR2320i00000-k250-e1000", "G1802a00000-k250-e1000"):
            self.assertIn(P.PINS["xsec_files"][f"{q}/data/gxspl-NUsmall.xml"], block)
            self.assertIn(P.PINS["xsec_files"][f"{q}/data/README"], block)

    def test_flags_are_section_42s(self):
        import re
        decl = (REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md").read_text()
        self.assertEqual(P.ENCRYPT, re.search(r"encrypt: `gpg ([^`]+)`", decl).group(1).split())
        self.assertEqual(P.DECRYPT, re.search(r"decrypt: `gpg ([^`]+)`", decl).group(1).split())

    def test_the_tools_are_the_launchers(self):
        self.assertEqual(sorted(P.TOOLS), sorted(LAUNCH.TOOL_NAMES))
        self.assertIn("awk", P.TOOLS)                                    # exec'd under strace: pinned (D1)

    def test_trace_set_is_the_pipelines(self):
        sys.path.insert(1, str(REPO / "3d-unfolding/genie"))
        import pg_verify
        self.assertEqual(P.TRACE_SET, pg_verify.TRACE_SET)
        self.assertIn(f'-e "{P.TRACE_SET}"', (REPO / "3d-unfolding/genie/run_gevgen_v3.sh").read_text())

    def test_a_crash_is_its_own_reason(self):
        import contextlib
        real = P.probe
        def boom():
            raise KeyError("x")
        P.probe = boom
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                rc = P.main()
        finally:
            P.probe = real
        self.assertEqual(rc, 3)
        rec = json.loads(out.getvalue().splitlines()[-1].split(" ", 1)[1])
        self.assertEqual(rec["stops"], ["internal-error: KeyError"])

    def test_identity_rules(self):
        self.assertFalse(P.identity()["pass"])                     # this laptop is not a login node


# ---------------------------------------------------------------------------------------------------------- launcher

class Launcher(Tmp):
    def setUp(self):
        super().setUp()
        self.t = Path(self.tmp)
        self.probe = self.t / "pg-probe.py"
        self.probe.write_bytes((HERE / "pg-probe.py").read_bytes())
        self.out = self.t / "pg-probe.out"
        self.sha = sha(self.probe.read_bytes())

    def launch(self, body, sha_=None):
        s = self.t / "ssh"
        s.write_text(f"#!/bin/sh\necho \"$@\" > {self.t}/args\ncat > {self.t}/stdin\n{body}\n")
        s.chmod(0o755)
        so = io.StringIO()
        with contextlib.redirect_stdout(so), contextlib.redirect_stderr(io.StringIO()):
            rc = LAUNCH.main([sha_ or self.sha], ssh=str(s), probe_path=str(self.probe), out_path=str(self.out))
        self.printed = so.getvalue()
        return rc

    def go_record(self):
        """A GO record with the real pins: what a probe on matching bytes would report."""
        pins = P.PINS
        tool = {"path": "/usr/bin/x", "sha256": "a" * 64, "rpm_match": True, "rpm_status": "recorded", "rpm_digest": "a" * 64}
        rec = {"schema": P.SCHEMA, "verdict": "GO", "stops": [], "identity": {"pass": True},
               "pins_sha256": sha(json.dumps(pins, sort_keys=True).encode()), "record_sha256": pins["record_sha256"],
               "repo": {"pass": True, "xattrs": {"user.fqrn": "larsoft.opensciencegrid.org"}},
               "mount_control": {"pass": True}, "proc_mount": {"options": "rw,nosuid", "hidepid": "0"},
               "genie": {"problems": [], "files": {k: {"sha256": v, "match": True} for k, v in pins["genie_files"].items()},
                         "links": {k: {"target": v, "match": True} for k, v in pins["genie_links"].items()},
                         "listings": {k: {"names": v, "match": True} for k, v in pins["genie_listings"].items()}},
               "xsec": {"problems": [], "files": {k: {"sha256": v, "match": True} for k, v in pins["xsec_files"].items()},
                        "qualifiers": [q + "/" for q in pins["required_qualifiers"]],
                        "data_listings": {q: {"names": ["README"], "config_like": []} for q in pins["required_qualifiers"]},
                        "dbconfig": {"sha256": "b" * 64}},
               "tools": {k: dict(tool) for k in LAUNCH.TOOL_NAMES}, "strace_self_test": {"pass": True},
               "gpg": {"pass": True, "gpg_started": True, "confined": True, "round_trip_equal": True, "decrypt_rc": 0,
                       "packet_tags": [3, 18], "tampered": {"rc": 2, "evidence": True},
                       "wrong_passphrase": {"rc": 2, "evidence": True}, "gnupghome_mode": "0o700",
                       "gpgconf_kill_rc": 0, "agent_gone": True, "socketdir_absent": True, "gnupghome_removed": True}}
        rec["tools"]["gpgconf"].update(rpm_match=None, rpm_status="not-owned", rpm_digest=None,
                                       pin_basis="first use: no RPM record")       # first use is allowed
        return rec

    def emit(self, rec, rc):
        fd, f = tempfile.mkstemp(dir=self.tmp, suffix=".receipt")
        os.close(fd)
        Path(f).write_text("verdict line\nPG-PROBE-RESULT " + json.dumps(rec, sort_keys=True) + "\n")
        return f"cat {f}; exit {rc}"

    def test_valid_stop_and_go(self):
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}
        self.assertEqual(self.launch(self.emit(stop, 3)), 3)
        args = (self.t / "args").read_text()
        self.assertTrue(args.startswith("-F /dev/null "))
        for o in ("ForwardAgent=no", "StrictHostKeyChecking=yes", "ControlPath=none", "BatchMode=yes",
                  "ClearAllForwardings=yes", "PermitLocalCommand=no", "IdentitiesOnly=yes"):
            self.assertIn(o, args)
        self.assertTrue(args.rstrip().endswith("saul.nersc.gov env -i PATH=/usr/bin:/bin LC_ALL=C "
                                               "/usr/bin/python3.11 -I -S -B -"))
        self.out.unlink()
        self.assertEqual(self.launch(self.emit(self.go_record(), 0)), 0, self.out.read_text()[-500:])

    def test_an_incomplete_go_is_invalid(self):
        good = self.go_record()

        def edit(fn):
            r = json.loads(json.dumps(good))
            fn(r)
            return r
        first = next(iter(P.PINS["genie_files"]))
        cases = [{"verdict": "GO"}, edit(lambda r: r.update(pins_sha256="0" * 64)),
                 edit(lambda r: r.update(record_sha256="0" * 64)),
                 edit(lambda r: r["repo"]["xattrs"].update({"user.fqrn": "x"})),
                 edit(lambda r: r["mount_control"].update({"pass": False})),
                 edit(lambda r: r.pop("proc_mount")),                               # C3: /proc's options recorded
                 edit(lambda r: r["proc_mount"].update({"options": None})),
                 edit(lambda r: r["genie"]["files"].pop(first)),
                 edit(lambda r: r["genie"]["files"][first].update(match=False)),
                 edit(lambda r: r["genie"]["files"].update({"extra": {"match": True}})),
                 edit(lambda r: next(iter(r["genie"]["files"].values())).update(sha256="0" * 64)),   # a claimed match
                 edit(lambda r: next(iter(r["genie"]["links"].values())).update(target="elsewhere")),
                 edit(lambda r: next(iter(r["xsec"]["files"].values())).update(sha256="0" * 64)),
                 edit(lambda r: r["tools"]["strace"].update(rpm_status="query-failed")),
                 edit(lambda r: r["tools"]["strace"].update(rpm_match=None)),               # None without first use
                 edit(lambda r: r["xsec"]["data_listings"]["G1802a00000-k250-e1000"].update(config_like=["x.xml"])),
                 edit(lambda r: r["xsec"].update(qualifiers=[])),
                 edit(lambda r: r["xsec"]["dbconfig"].update(sha256=None)),
                 edit(lambda r: r["tools"]["strace"].update(rpm_match=False)), edit(lambda r: r["tools"].pop("gpg")),
                 edit(lambda r: r["tools"]["strace"].update(rpm_match=1)),            # 1 == True, but not True
                 edit(lambda r: r["tools"]["gpg"].update(problem="x")),
                 edit(lambda r: r["strace_self_test"].update({"pass": 1})),
                 edit(lambda r: r["gpg"].update(gpg_started=False)),
                 edit(lambda r: r["gpg"].update(socketdir_absent=False)),
                 edit(lambda r: r.update(stops=["x"])), edit(lambda r: r["identity"].update({"pass": False})),
                 edit(lambda r: r["genie"].update(problems=["x"]))]
        for i, rec in enumerate(cases):
            with self.subTest(i):
                if self.out.exists():
                    self.out.unlink()
                self.assertEqual(self.launch(self.emit(rec, 0)), 4)
                self.assertIn("receipt INVALID", self.out.read_text())

    def test_invalid_shapes_are_kept(self):
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}
        for i, body in enumerate(("exit 0", "exit 255", self.emit(dict(stop, stops=[]), 3), self.emit(stop, 0),
                                  self.emit(stop, 3).replace("; exit 3", "; echo tail; exit 3"),
                                  self.emit(stop, 3).replace("; exit 3", "; " + self.emit(stop, 3)))):
            with self.subTest(i):
                if self.out.exists():
                    self.out.unlink()
                self.assertEqual(self.launch(body), 4)

    def test_refusals_before_ssh(self):
        self.assertEqual(self.launch("exit 0", sha_="0" * 64), 5)
        self.assertFalse((self.t / "args").exists())
        self.out.write_text("old\n")
        self.assertEqual(self.launch("exit 0"), 5)
        self.assertEqual(self.out.read_text(), "old\n")
        self.out.unlink()
        self.out.symlink_to(self.t / "elsewhere")
        self.assertEqual(self.launch("exit 0"), 5)
        self.assertFalse((self.t / "elsewhere").exists())

    def test_the_sent_bytes_and_the_footer(self):
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}
        moved = self.t / "moved.out"
        try:
            rc = self.launch(f"mv {self.out} {moved}; " + self.emit(stop, 3))
        except OSError as e:
            self.fail(f"the footer reopened the moved path: {e}")
        self.assertEqual(rc, 3)
        self.assertEqual(sha((self.t / "stdin").read_bytes()), self.sha)
        self.assertIn(f"{sha(moved.read_bytes())}  {self.out}", self.printed)


class ProbeRound4(Tmp):
    """Round 4: an RPM dump that fails, or omits an owned file, is not a first use (C15); the probe's trace checks
    carry pg_verify's completeness codes (C16); /proc's mount options are recorded (C3)."""

    def tool(self):
        a = Path(self.tmp) / "tool"
        a.write_text("#!/bin/sh\n")
        return str(a)

    def test_a_failed_or_partial_rpm_dump_is_not_a_first_use(self):
        a = self.tool()
        for name, dump in (("failed", lambda: (1, "error: dump\n")), ("without the file", lambda: (0, "/other 1 0 x\n")),
                           ("failed after listing the file", lambda: (1, f"{a} 1 0 {'e' * 64}\nerror: dump\n"))):
            with self.subTest(name):
                run = lambda args: (0, "strace-5\n") if args[0] == "-qf" else dump() if args[1:2] == ["--dump"] else (0, "")
                fds, rec = P.open_tools({"strace": (a,)}, run)
                self.addCleanup(lambda f=fds: [os.close(fd) for fd in f.values()])
                self.assertEqual((rec["strace"]["rpm_status"], rec["strace"]["problem"]),
                                 ("query-failed", "the RPM query failed"))

    def test_trace_completeness_codes(self):
        codes = lambda t: {p.split(":")[0] for p in P.trace_complete(t, 0)}
        self.assertEqual(codes('9 openat(AT_FDCWD, "/x", O_RDONLY) = 3\n9 +++ exited with 0 +++\n'), set())
        self.assertIn("resume-mismatch", codes('9 openat(AT_FDCWD, "/x", O_RDONLY <unfinished ...>\n'
                                               '9 <... stat resumed>) = 0\n9 +++ exited with 0 +++\n'))
        self.assertIn("no-terminal", codes('9 openat(AT_FDCWD, "/x", O_RDONLY) = 3\n10 access("/y", F_OK) = 0\n'
                                           '9 +++ exited with 0 +++\n'))

    def test_the_proc_mount_is_recorded(self):
        self.assertEqual(P.proc_mount("proc /proc proc rw,nosuid,hidepid=invisible 0 0\n/dev/x / ext4 rw 0 0\n"),
                         {"options": "rw,nosuid,hidepid=invisible", "hidepid": "invisible"})
        self.assertEqual(P.proc_mount("proc /proc proc rw,nosuid 0 0\n"), {"options": "rw,nosuid", "hidepid": "0"})
        self.assertEqual(P.proc_mount(""), {"options": None, "hidepid": None})


if __name__ == "__main__":
    unittest.main()

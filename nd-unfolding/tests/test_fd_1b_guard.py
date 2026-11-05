"""1B's guarded launcher (fd_1b_noatime_guard.py, the director's ruling of 2026-11-05) and the scan that every
binding-3 job line runs through it (b3/guard_scan.py).

The hook's decision is tested directly, and the hook itself in subprocesses (an audit hook cannot be removed from the
process that adds it). O_NOATIME exists only on Linux, so the subprocesses install the hook with a harmless stand-in
bit (os.O_NOFOLLOW, on regular files), which production never accepts: there the launcher refuses to run without the
real flag."""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fd_1b_noatime_guard as guard  # noqa: E402

B3 = ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/b3"
sys.path.insert(0, str(B3))
import guard_scan  # noqa: E402

STAND_IN = os.O_NOFOLLOW
# every binding-3 script in b3/ and the number of guarded 1B lines it must hold: a script not listed fails, so a new
# one cannot go uncounted, and a count of 0 fails, so an emptied script cannot pass vacuously
EXPECTED_B3 = {"sbatch-c2check.sh": 1}


def run_py(code: str, *args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-c", code, *args], capture_output=True, text=True, cwd=cwd,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


class Decision(unittest.TestCase):
    """guard.refuses: under a root and without the noatime bit, after realpath on both sides."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-guard-")).resolve()
        self.root = self.tmp / "bank"
        self.root.mkdir()
        (self.root / "w.npy").write_bytes(b"x")
        self.roots = (str(self.root),)

    def test_each_direction(self):
        f = str(self.root / "w.npy")
        self.assertTrue(guard.refuses(f, os.O_RDONLY, self.roots, STAND_IN))
        self.assertFalse(guard.refuses(f, os.O_RDONLY | STAND_IN, self.roots, STAND_IN))
        self.assertTrue(guard.refuses(str(self.root), os.O_RDONLY, self.roots, STAND_IN))      # the root itself
        self.assertFalse(guard.refuses(str(self.tmp / "other.txt"), os.O_RDONLY, self.roots, STAND_IN))
        sib = self.tmp / "bank2"
        sib.mkdir()
        self.assertFalse(guard.refuses(str(sib / "w.npy"), os.O_RDONLY, self.roots, STAND_IN))  # a prefix, not under
        self.assertFalse(guard.refuses(3, os.O_RDONLY, self.roots, STAND_IN))                   # a descriptor

    def test_a_symlink_or_a_relative_path_cannot_step_around_a_root(self):
        link = self.tmp / "link.npy"
        link.symlink_to(self.root / "w.npy")
        self.assertTrue(guard.refuses(str(link), os.O_RDONLY, self.roots, STAND_IN))
        cwd = os.getcwd()
        try:
            os.chdir(self.root)
            self.assertTrue(guard.refuses("w.npy", os.O_RDONLY, self.roots, STAND_IN))
        finally:
            os.chdir(cwd)

    def test_the_declared_roots_are_the_inputs(self):
        for want in ("bank_sweep_5d_bkgaware", "bank_detector", "of_inputs_5d.npz", "bkg_dump.npz", "FluxConstraints",
                     "fd-1b-inv-20261101/i0/in", "fd-1b-staged-20261102/stage1/in"):
            self.assertTrue(any(r.endswith(want) for r in guard.ROOTS), want)
        self.assertFalse(any("pv-ladder" in r or r.endswith("cmodel_5d.json") for r in guard.ROOTS))  # a deploy file


class Hook(unittest.TestCase):
    """The audit hook in a fresh process: every plain read under a root refuses, an O_NOATIME-style open passes."""

    def test_the_hook_refuses_plain_reads_and_passes_flagged_ones(self):
        tmp = Path(tempfile.mkdtemp(prefix="fd1b-hook-")).resolve()
        root = tmp / "bank"
        root.mkdir()
        import numpy as np
        np.save(root / "w.npy", np.arange(3.0))
        (root / "t.txt").write_text("x")
        (tmp / "out.txt").write_text("y")
        (tmp / "link.txt").symlink_to(root / "t.txt")
        code = textwrap.dedent(f"""
            import json, os, sys
            import numpy as np
            sys.path.insert(0, {str(ND)!r})
            import fd_1b_noatime_guard as g, fd_1b_inv as inv
            root = {str(root)!r}
            g.install([root], noatime={STAND_IN})
            res = {{}}
            def attempt(name, f):
                try:
                    f()
                    res[name] = "ok"
                except PermissionError:
                    res[name] = "refused"
            attempt("open", lambda: open(root + "/t.txt").read())
            attempt("open_rb", lambda: open(root + "/t.txt", "rb").read())
            attempt("np_load", lambda: np.load(root + "/w.npy"))
            attempt("np_load_mmap", lambda: np.load(root + "/w.npy", mmap_mode="r"))
            attempt("os_open_plain", lambda: os.close(os.open(root + "/t.txt", os.O_RDONLY)))
            attempt("os_open_flagged", lambda: os.close(os.open(root + "/t.txt", os.O_RDONLY | {STAND_IN})))
            inv.NOATIME_FLAG = {STAND_IN}
            attempt("inv_open_noatime", lambda: inv.open_noatime(root + "/w.npy").read())
            attempt("outside", lambda: open({str(tmp / "out.txt")!r}).read())
            attempt("symlink", lambda: open({str(tmp / "link.txt")!r}).read())
            os.chdir(root)
            attempt("relative", lambda: open("t.txt").read())
            print(json.dumps(res))
            """)
        r = run_py(code)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got, {"open": "refused", "open_rb": "refused", "np_load": "refused", "np_load_mmap": "refused",
                               "os_open_plain": "refused", "os_open_flagged": "ok", "inv_open_noatime": "ok",
                               "outside": "ok", "symlink": "refused", "relative": "refused"})


class Launcher(unittest.TestCase):
    """The launcher: it installs the hook, then runs the entry as __main__ with its argv and exit code."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-launch-")).resolve()
        self.root = self.tmp / "inputs"
        self.root.mkdir()
        (self.root / "x.txt").write_text("x")
        self.entry = self.tmp / "entry.py"
        self.entry.write_text(textwrap.dedent(f"""
            import os, sys
            print("ARGV", sys.argv[1:], flush=True)
            if sys.argv[1] == "plain":
                open({str(self.root / "x.txt")!r}).read()
            elif sys.argv[1] == "flagged":
                os.close(os.open({str(self.root / "x.txt")!r}, os.O_RDONLY | {STAND_IN}))
            sys.exit(int(sys.argv[2]))
            """))

    def launch(self, *args):
        code = (f"import functools, sys; sys.path.insert(0, {str(ND)!r}); import fd_1b_noatime_guard as g; "
                f"g.install = functools.partial(g.install, noatime={STAND_IN}); g.main(sys.argv[1:])")
        return run_py(code, *args)

    def test_a_plain_read_in_the_entry_refuses(self):
        r = self.launch("--root", str(self.root), "--", str(self.entry), "plain", "0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("a plain open of a declared input refused", r.stderr)
        self.assertIn("installed over 1 roots", r.stderr)

    def test_argv_and_the_exit_code_pass_through(self):
        r = self.launch("--root", str(self.root), "--", str(self.entry), "flagged", "7")
        self.assertEqual(r.returncode, 7, r.stderr[-800:])
        self.assertIn("ARGV ['flagged', '7']", r.stdout)

    def test_declared_means_the_roots_constant(self):
        r = self.launch("--declared", "--", str(self.entry), "none", "0")
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertIn(f"installed over {len(guard.ROOTS)} roots", r.stderr)

    def test_usage_errors_refuse(self):
        for args in (("--root", str(self.root), str(self.entry)), ("--root", str(self.root), "--"),
                     ("--bogus", "--", str(self.entry)), ("--root", "--", str(self.entry)), ("--", str(self.entry))):
            r = self.launch(*args)
            self.assertNotEqual(r.returncode, 0, args)
            self.assertNotIn("ARGV", r.stdout, args)

    @unittest.skipIf(hasattr(os, "O_NOATIME"), "this platform has O_NOATIME")
    def test_without_the_flag_the_real_launcher_refuses_to_run(self):
        r = subprocess.run([sys.executable, "-B", str(ND / "fd_1b_noatime_guard.py"), "--declared", "--",
                            str(self.entry), "none", "0"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refusing to run unguarded", r.stderr + r.stdout)
        self.assertNotIn("ARGV", r.stdout)


class Scan(unittest.TestCase):
    """b3/guard_scan.py over the binding-3 job scripts and the generator's rows, with each population's count."""

    def test_the_scanner_on_known_lines(self):
        cases = {'python3 -B "$DD/nd-unfolding/fd_1b_c2.py" c2check': ["unguarded"],
                 'nice -n 19 /usr/bin/time -v python3 nd-unfolding/fd_1b_mc.py receipt --npz a': ["unguarded"],
                 'python3 -X importtime -W ignore $D/fd_1b_mc.py unfold': ["unguarded"],     # option values modelled
                 '"$PY" -B "$C/fd_1b_noatime_guard.py" --declared -- "$C/fd_1b_mc.py" unfold': ["guarded"],
                 'python3 fd_1b_noatime_guard.py --root /a --root /b -- x/fd_1b_binning.py': ["guarded"],
                 'python3 fd_1b_noatime_guard.py --root -- x/fd_1b_mc.py': ["unguarded"],     # --root eats "--"
                 'python3 fd_1b_noatime_guard.py --declared fd_1b_mc.py': ["unguarded"],
                 'python3 fd_1b_noatime_guard.py --declared -- other.py': ["unguarded"],
                 'python3 -B - $PINS <<PYL': [], 'python3 -c "import fd_1b_mc"': [],
                 'sha256sum nd-unfolding/fd_1b_c2.py': []}
        for line, want in cases.items():
            self.assertEqual(guard_scan.scan_line(line), want, line)
        joined = guard_scan.scan_script('python3 -B \\\n  "$D/fd_1b_mc.py" \\\n  unfold\n')
        self.assertEqual(len(joined["unguarded"]), 1)                                   # a continued line
        self.assertEqual(guard_scan.scan_script(
            "python3 -B - <<'PYL'\nimport fd_1b_mc\nprint('fd_1b_mc.py')\nPYL\n")["unguarded"], [])

    def test_every_binding_3_script_is_guarded_and_counted(self):
        found = {p.name for p in B3.glob("*.sh")}
        self.assertEqual(found, set(EXPECTED_B3), "every b3 script must be listed with its expected count")
        for name, n in EXPECTED_B3.items():
            r = guard_scan.scan_script((B3 / name).read_text())
            self.assertEqual(r["unguarded"], [], name)
            self.assertEqual(r["guarded"], n, name)
            self.assertGreater(n, 0, name)

    def test_a_cmodel_json_in_a_binding_3_script_is_the_deploy_file(self):
        """The cmodel json is a deploy file (nd-unfolding/pv-ladder/readouts/cmodel_5d.json), not a guard root: any
        binding-3 line passing --cmodel-json passes that path under the deploy ($DD)."""
        import shlex
        for p in B3.glob("*.sh"):
            for line in guard_scan.logical_lines(p.read_text()):
                toks = shlex.split(line, comments=True)
                for i, tok in enumerate(toks[:-1]):
                    if tok == "--cmodel-json":
                        self.assertEqual(toks[i + 1], "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json", p.name)

    def test_the_pre_guard_scripts_are_seen_unguarded(self):
        """The scan sees a real direct call: the A2.1 and S1-0 scripts that ran before the guard (excluded from the
        population by name, for that reason) read as unguarded."""
        S = B3.parent
        for f, n in (("a2-1/sbatch-calibrate.sh", 1), ("a2-1/sbatch-c2probe.sh", 1), ("stage1/connect32-s1-0.sh", 2)):
            self.assertEqual(len(guard_scan.scan_script((S / f).read_text())["unguarded"]), n, f)


if __name__ == "__main__":
    unittest.main()

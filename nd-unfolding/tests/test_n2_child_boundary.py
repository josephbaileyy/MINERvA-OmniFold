#!/usr/bin/env python3
"""N-2: the CHILD boundary of the adoption path is genuinely armed.

WHAT THIS IS AND WHY IT IS NOT THE CONTRACT'S N-2.
`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` section 5 proposed taking a COPY of the pinned
science writer `adopt_unified_5d.py`, adding one `import <victim>` line to it, and running that.
**Joseph REJECTED that on 2026-08-22 (ruling 19)** for a defect internal to the contract: a copied
writer placed OUTSIDE `MNV_CODE_ROOT` is refused by the contract's own B-4 script-containment rule
BEFORE its injected import ever executes, so the control would pass for the WRONG REASON -- proving
containment, not child-boundary import guarding. His second objection was that the proposed third
checkout is not on the adopter's hardcoded import path at all.

WHAT RULING 19 AUTHORIZES INSTEAD, AND WHAT IS BUILT HERE:
  * a MINIMAL PURPOSE-BUILT fixture writer INSIDE a disposable expected checkout, so it passes B-4
    and the refusal can only come from the import;
  * accepting the REAL child argument shape (`--uthrow/--combined/--out` plus passthrough);
  * deliberately importing an EXISTING repository-local module from a SECOND checkout -- here the
    real repository this test lives in, and the real `seed_offset_policy`, so nothing is fabricated;
  * invoked through the actual `mii_adopt_unified_5d_stamped.build_child_argv(..., writer=fixture)`;
  * UNGUARDED arm proves the WRONG MODULE LOADS, asserted on the loaded module's `__file__`;
  * GUARDED arm exits 3 BEFORE any output is opened, with the ordering evidence of section 5.4.
  * NO copy and NO edit of `adopt_unified_5d.py`. NO `--allow` on any arm. Asserted below.

WHAT IT DOES NOT ESTABLISH, STATED HERE RATHER THAN DISCOVERED LATER.
`build_child_argv` DOES NOT ITSELF EMIT THE GUARD TODAY. It returns `[python, writer, --uthrow ...]`
and this test wraps that return value in the `[python, guard, --expect-root, <root>, --, ...]`
template Amendment 1 section D specifies, asserting that the wrap preserves the child argv verbatim.
So what is proven is that the CHILD WRAPPER PLUMBING REFUSES what it must refuse; what is NOT proven
is that the production adopter emits it. Adding the guard to `build_child_argv` is not in ruling
18's authorized list and was deliberately not done. Until it is, the production child is unguarded.
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
REPO = HERE.parents[1]
GUARD = ND / "mnv_guarded_run.py"

sys.path.insert(0, str(ND))
import mii_adopt_unified_5d_stamped as STAMPED  # noqa: E402
import mnv_guarded_run as mgr  # noqa: E402

#: The existing repository-local module the fixture writer imports from the SECOND checkout. Chosen
#: because it is the module the REAL adopter wrapper imports at `mii_adopt_unified_5d_stamped.py`
#: (via `leg_groups()`), so the fixture is importing what production imports, not a stand-in.
VICTIM = "seed_offset_policy"

#: Emitted by the fixture writer strictly AFTER the guarded import and strictly BEFORE the output
#: file is opened. O-1: the evidence is the same binary printing it on one arm and not the other.
O1_MARKER = "[fixture-writer] O1-MARKER about to open the output"
STARTED = "[fixture-writer] argv accepted"
IMPORTED = "[fixture-writer] IMPORTED"

WRITER_SRC = '''#!/usr/bin/env python3
"""N-2 fixture writer. NOT a science writer, and it computes nothing.

It exists to occupy the CHILD position of the adoption path with a file whose only interesting
property is that it imports one existing repository module from a checkout that is not
--expect-root, in the same shape the pinned adopter uses (an absolute insert at position 0, which
PYTHONPATH cannot outrank). It accepts the real child argument shape so the real
`build_child_argv` can produce its argv unchanged.
"""
import argparse
import sys

_SECOND_CHECKOUT_ND = {second!r}
if _SECOND_CHECKOUT_ND not in sys.path:
    sys.path.insert(0, _SECOND_CHECKOUT_ND)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uthrow", required=True)
    ap.add_argument("--combined", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    print({started!r}, flush=True)

    import {victim} as loaded          # THE GUARDED IMPORT. Everything below is downstream of it.

    print({imported!r}, loaded.__file__, flush=True)
    print({o1!r}, flush=True)
    with open(args.out, "w") as fh:    # THE FIRST OUTPUT THIS PROCESS OPENS.
        fh.write("fixture output\\n")
    print("[fixture-writer] wrote", args.out, flush=True)
    return 0


sys.exit(main())
'''


def make_checkout(base: pathlib.Path, name: str) -> pathlib.Path:
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    return root


class N2ChildBoundary(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        # RESOLVED, as `test_mnv_guarded_run.py` resolves its own fixture root. On macOS
        # `tempfile` hands back `/var/...` while the guard records `checkout_root_of` of a RESOLVED
        # origin under `/private/var/...`, so an unresolved root makes arm G compare two spellings
        # of one directory and fail for a reason that has nothing to do with the boundary.
        tmp = pathlib.Path(self._tmp.name).resolve()

        # The DISPOSABLE EXPECTED CHECKOUT. The fixture writer lives INSIDE it, which is the whole
        # point of ruling 19: B-4 passes, so a refusal can only have come from the import.
        self.expected = make_checkout(tmp, "expected-code-root")

        # THE SECOND CHECKOUT IS THE REAL REPOSITORY. Nothing is copied into it and nothing is
        # written to it; the fixture only reads one module out of it.
        self.second_nd = ND
        self.assertTrue(mgr.is_checkout(REPO), "the real repository must be a checkout for this "
                                               "control to have a second checkout at all")
        self.assertTrue((self.second_nd / f"{VICTIM}.py").is_file())

        self.writer = self.expected / "nd-unfolding" / "fixture_writer.py"
        self.writer.write_text(WRITER_SRC.format(
            second=str(self.second_nd), victim=VICTIM,
            started=STARTED, imported=IMPORTED, o1=O1_MARKER))

        # The guard is copied into the expected checkout so that the guarded interpreter's own
        # sys.path[0] is inside --expect-root. Without that, the guard's home directory would put
        # the second checkout on sys.path independently of the fixture, and a refusal would no
        # longer be attributable to the writer's own insert.
        self.guard = self.expected / "nd-unfolding" / "mnv_guarded_run.py"
        shutil.copy2(GUARD, self.guard)
        # The guard refuses to run (COULD NOT LOOK, exit 2) unless its tracked subprocess shim sits
        # beside it, so this checkout must carry the shim as a real one does. Without it arms B, C
        # and G measured exit 2 -- "we could not check" read as the refusal they exist to pin, which
        # is the one substitution the guard's own exit codes are designed to prevent.
        (self.expected / "nd-unfolding" / "mnv_guard_shim").mkdir()
        shutil.copy2(GUARD.parent / "mnv_guard_shim" / "sitecustomize.py",
                     self.expected / "nd-unfolding" / "mnv_guard_shim" / "sitecustomize.py")

        self.uthrow = tmp / "scratch" / "throwaway_uthrow.root"
        self.combined = tmp / "scratch" / "throwaway_combined.root"
        (tmp / "scratch").mkdir()
        self.uthrow.write_text("not a real root file\n")
        self.combined.write_text("not a real root file\n")

    def _empty_outdir(self, name):
        d = pathlib.Path(self._tmp.name) / name
        d.mkdir()
        self.assertEqual(sorted(os.listdir(d)), [], "the witness directory must START empty")
        return d

    def _child_argv(self, out):
        """The REAL production function, called with writer=<fixture>."""
        return STAMPED.build_child_argv(self.uthrow, self.combined, out,
                                        writer=str(self.writer), python=sys.executable)

    @staticmethod
    def _run(argv, cwd=None):
        """One merged stream, so the interleaving is real (O-3), and the status is captured
        unpiped into a variable before anything reads it (O-4)."""
        cp = subprocess.run([str(a) for a in argv], cwd=cwd, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        return cp.returncode, cp.stdout

    # ------------------------------------------------------------------ the fixture rule, first
    def test_A_UNGUARDED_the_fixture_really_loads_the_SECOND_checkouts_module(self):
        """Section 5.5. A control whose fixture does not hijack passes vacuously.

        Asserted on the loaded module's `__file__`, never on exit 0.
        """
        outdir = self._empty_outdir("out-unguarded")
        out = outdir / "fixture_product.root"
        rc, log = self._run(self._child_argv(out))
        self.assertEqual(rc, 0, log)
        self.assertIn(STARTED, log)
        self.assertIn(IMPORTED, log)
        loaded = [l for l in log.splitlines() if l.startswith(IMPORTED)][0].split(None, 2)[2]
        self.assertEqual(pathlib.Path(loaded).resolve(),
                         (self.second_nd / f"{VICTIM}.py").resolve(),
                         "the fixture did not import the second checkout's copy, so it is not a "
                         "hijack and the guarded arm below would prove nothing")
        self.assertNotEqual(pathlib.Path(loaded).resolve().parent, self.writer.parent)
        self.assertIn(O1_MARKER, log)
        self.assertTrue(out.is_file(), "the unguarded arm must reach the output, or the O-1 marker "
                                       "is not upstream of anything")

    # ------------------------------------------------------------------ the refusal
    def test_B_GUARDED_through_the_child_wrapper_it_exits_3(self):
        outdir = self._empty_outdir("out-guarded")
        out = outdir / "fixture_product.root"
        child = self._child_argv(out)
        argv = [child[0], str(self.guard), "--expect-root", str(self.expected), "--"] + child[1:]
        rc, log = self._run(argv)
        self.assertEqual(rc, mgr.VIOLATION_EXIT, log)
        self.assertIn("IMPORT TREE VIOLATION", log)
        self.assertIn(VICTIM, log)
        self.assertIn(str(REPO), log)
        self.assertIn(str(self.expected), log)

    def test_C_the_refusal_precedes_any_output_being_opened(self):
        """O-1, O-2 and O-3 together. An exit code alone is refused as evidence."""
        outdir = self._empty_outdir("out-ordering")
        out = outdir / "fixture_product.root"
        child = self._child_argv(out)
        argv = [child[0], str(self.guard), "--expect-root", str(self.expected), "--"] + child[1:]
        rc, log = self._run(argv)

        # O-1: the monotone marker, measured across two arms of the SAME binary. The paired arm is
        # test_A above, which emits it; this arm must not.
        self.assertEqual(rc, mgr.VIOLATION_EXIT, log)
        self.assertIn(STARTED, log, "the writer must have STARTED, or this measures a startup "
                                    "failure rather than an import refusal")
        self.assertNotIn(IMPORTED, log)
        self.assertNotIn(O1_MARKER, log)

        # O-3: one stream, so the order is real. The banner is the last thing in it.
        lines = [l for l in log.splitlines() if l.strip()]
        self.assertEqual(lines[0], STARTED, lines)
        self.assertTrue(any("IMPORT TREE VIOLATION" in l for l in lines), lines)
        banner = next(i for i, l in enumerate(lines) if "IMPORT TREE VIOLATION" in l)
        self.assertTrue(all(not l.startswith("[fixture-writer]") for l in lines[banner:]),
                        f"the writer spoke AFTER the refusal banner:\n{log}")

        # O-2: the filesystem witness over a directory that started empty.
        self.assertFalse(out.exists(), "the refused arm opened its output")
        self.assertEqual(sorted(os.listdir(outdir)), [],
                         "the witness directory is not empty after a refused arm")

    # ------------------------------------------------------------------ scope assertions
    def test_D_the_argv_came_from_the_real_build_child_argv_and_kept_its_shape(self):
        out = pathlib.Path(self._tmp.name) / "shape.root"
        child = self._child_argv(out)
        self.assertEqual(child[1], str(self.writer))
        self.assertEqual(child[2:], ["--uthrow", str(self.uthrow),
                                     "--combined", str(self.combined), "--out", str(out)])
        argv = [child[0], str(self.guard), "--expect-root", str(self.expected), "--"] + child[1:]
        self.assertEqual(argv[argv.index("--") + 1:], child[1:],
                         "the guard wrap must forward the child argv VERBATIM")

    def test_E_no_allow_appears_on_any_arm(self):
        out = pathlib.Path(self._tmp.name) / "noallow.root"
        child = self._child_argv(out)
        argv = [child[0], str(self.guard), "--expect-root", str(self.expected), "--"] + child[1:]
        self.assertNotIn("--allow", child)
        self.assertNotIn("--allow", argv)

    def test_F_the_pinned_science_writer_is_neither_copied_nor_executed(self):
        """Ruling 19's hard limit, asserted rather than promised."""
        pinned = pathlib.Path(STAMPED.PINNED_WRITER)
        self.assertTrue(pinned.is_file())
        out = pathlib.Path(self._tmp.name) / "nope.root"
        self.assertNotIn(str(pinned), [str(a) for a in self._child_argv(out)])
        for p in self.expected.rglob("*.py"):
            self.assertNotEqual(p.name, pinned.name, f"a copy of the pinned writer at {p}")
        self.assertEqual(hashlib.sha256(self.guard.read_bytes()).hexdigest(),
                         hashlib.sha256(GUARD.read_bytes()).hexdigest(),
                         "the guard copy in the fixture checkout must be byte-identical")

    def test_G_the_guarded_arm_leaves_an_inventory_naming_the_offending_origin(self):
        outdir = self._empty_outdir("out-inventory")
        out = outdir / "fixture_product.root"
        inv = pathlib.Path(self._tmp.name) / "inv" / "n2.jsonl"
        child = self._child_argv(out)
        argv = [child[0], str(self.guard), "--expect-root", str(self.expected),
                "--inventory", str(inv), "--"] + child[1:]
        rc, log = self._run(argv)
        self.assertEqual(rc, mgr.VIOLATION_EXIT, log)
        rec = json.loads(inv.read_text().strip())
        self.assertTrue(rec["verdict"].startswith("REFUSED"), rec["verdict"])
        self.assertEqual(rec["violation"]["module"], VICTIM)
        self.assertEqual(rec["violation"]["found_root"], str(REPO))
        self.assertEqual(rec["script_checkout_root"], str(self.expected))
        self.assertEqual(rec["allow"], [])
        self.assertTrue(rec["allow_is_empty"])
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)

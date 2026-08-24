#!/usr/bin/env python3
"""Legs 5a and 5b: every repository-origin import must resolve beneath MNV_CODE_ROOT.

WHY THIS EXISTS. On 2026-08-23 the k=0 rehearsal's legs 5a and 5b refused at the OI-136 guard:

    [oi136] module uq_math resolved to .../MINERvA-OmniFold/nd-unfolding/uq_math.py
    [oi136] expected                   .../k0r2/clean

Both entry routes are `unified_throw_cov_5d.py` -> `unified_throw_cov.py` -> `compare_unified_throw.py`.
The first two already derived their roots from `__file__`; the third put the canonical checkout at
`sys.path[0]` underneath them. **A repaired importer does not protect you from an unrepaired import**,
and no static scan this lane ran had caught it -- the insert argument is a loop variable, never the
rooted name. The runtime guard caught it; three rounds of AST analysis did not.

WHAT MAKES THIS A REAL TEST RATHER THAN A RESTATEMENT. The decoy tree is POPULATED. A fixture whose
"wrong tree" does not exist, or exists and is empty, passes whatever the code does -- the import
falls through to the code root and the arm proves nothing. Here the decoy holds a module of the same
name carrying a distinguishable marker, so `resolved under the code root` and `resolved under the
decoy` are different observable outcomes. The mutation arm restores the pre-repair hardcode pointed
at that decoy and MUST fail; if it ever passes, this file has stopped testing anything.

THE FILE UNDER TEST IS THE PRODUCER'S. The world around it is manufactured -- PB-16 requires the
fixture come from the producer, and here the producer supplies the module and the harness supplies
the two trees.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
ND = REPO / "nd-unfolding"
CANONICAL = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"

# The k=0 5a/5b chain, in import order. Real files, copied from the producer.
CHAIN = ("compare_unified_throw.py",)
# A module the chain imports that exists in BOTH trees, so "which tree won" is observable.
PROBE = "uq_math.py"


class SeparatedRoots(unittest.TestCase):
    """A code root and a populated decoy, so a wrong-tree import is a DIFFERENT observable."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        # BOTH SIDES CANONICALIZED. On macOS /var is a symlink to /private/var, so an
        # uncanonicalized comparison of a resolved __file__ against an unresolved fixture root
        # fails on a correct import. Same defect this lane shipped in the round-5 path helper.
        tmp = pathlib.Path(os.path.realpath(self._tmp.name))
        self.code = tmp / "code-root"
        self.decoy = tmp / "decoy-checkout"
        for root, tag in ((self.code, "CODE"), (self.decoy, "DECOY")):
            (root / "nd-unfolding").mkdir(parents=True)
            (root / "2d-unfolding").mkdir(parents=True)
            # both trees are checkouts by the guard's own marker-pair definition
            (root / "VALIDATION_LEDGER.md").write_text(f"# {tag}\n")
            (root / "nd-unfolding" / PROBE).write_text(f'ORIGIN = "{tag}"\n')
        for f in CHAIN:
            shutil.copy2(ND / f, self.code / "nd-unfolding" / f)

    def _run(self, module, extra=""):
        """Import `module` from the code root in a CHILD process and report where things resolved.

        A child process is not a nicety: sys.path and sys.modules are process state, and an import
        already performed by the test runner would make the answer about the runner's environment.
        """
        script = textwrap.dedent(f"""
            import json, sys
            sys.path.insert(0, {str(self.code / "nd-unfolding")!r})
            {extra}
            import {module}
            import uq_math
            print(json.dumps({{
                "probe_origin": getattr(uq_math, "ORIGIN", None),
                "probe_file": getattr(uq_math, "__file__", None),
                "path": sys.path,
                "unfold_2d_imported": "unfold_2d_omnifold_unbinned" in sys.modules,
            }}))
        """)
        cp = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True,
                            cwd=str(self.code))
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        import json
        return json.loads(cp.stdout.strip().splitlines()[-1])

    # ---- THE CLAIM ---------------------------------------------------------------------------
    def test_every_repository_origin_import_resolves_beneath_the_code_root(self):
        r = self._run("compare_unified_throw")
        self.assertEqual(r["probe_origin"], "CODE",
                         f"uq_math resolved to the DECOY tree: {r['probe_file']}")
        self.assertTrue(os.path.realpath(r["probe_file"]).startswith(str(self.code)),
                        r["probe_file"])
        foreign = [p for p in r["path"]
                   if os.path.realpath(p).startswith(str(self.decoy))
                   or os.path.realpath(p).startswith(CANONICAL)]
        self.assertEqual(foreign, [], f"the chain put a foreign tree on sys.path: {foreign}")

    # ---- POWER: the same arm MUST fail against the pre-repair bytes ----------------------------
    def test_the_arm_FIRES_against_the_unrepaired_hardcode(self):
        """Restores exactly what the repair removed, pointed at the POPULATED decoy. If this ever
        passes, the arm above is decorative."""
        f = self.code / "nd-unfolding" / "compare_unified_throw.py"
        src = f.read_text()
        marker = 'for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):'
        self.assertIn(marker, src, "the repaired file no longer has the shape this arm mutates")
        broken = src.replace('_REPO = str(Path(__file__).resolve().parents[1])',
                             f'_REPO = {str(self.decoy)!r}')
        self.assertNotEqual(broken, src, "mutation did not apply -- this arm proves nothing")
        f.write_text(broken)
        r = self._run("compare_unified_throw")
        self.assertEqual(r["probe_origin"], "DECOY",
                         "the decoy did NOT win even with the hardcode restored -- the fixture "
                         "cannot detect the defect it exists to detect")

    # ---- THE DORMANT 2D CLAIM, TESTED RATHER THAN ASSERTED -------------------------------------
    def test_the_2D_arms_insert_is_NOT_executed_by_the_k0_route(self):
        """Joseph ruled 2d-unfolding/unfold_2d_omnifold_unbinned.py may stay unrepaired because its
        rooted insert sits inside main(). That is a claim about EXECUTION, so it is executed here:
        importing the k=0 chain must not pull that module in at all."""
        r = self._run("compare_unified_throw")
        self.assertFalse(r["unfold_2d_imported"],
                         "unfold_2d_omnifold_unbinned was imported by the k=0 chain -- its "
                         "in-main() insert is no longer dormant and the ruling to leave it "
                         "unrepaired has expired")

    def test_the_dormancy_arm_can_detect_a_NON_dormant_2D_import(self):
        """Negative control for the arm above: if the chain DID import it, the arm must notice."""
        r = self._run("compare_unified_throw",
                      extra="import sys, types; "
                            "sys.modules['unfold_2d_omnifold_unbinned'] = types.ModuleType('x')")
        self.assertTrue(r["unfold_2d_imported"],
                        "the dormancy arm cannot see an imported unfold_2d, so its green means "
                        "nothing")


if __name__ == "__main__":
    unittest.main()

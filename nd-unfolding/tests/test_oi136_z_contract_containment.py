#!/usr/bin/env python3
"""OI-136: z_contract must contain the pinned module's sys.path side effect, and hide nothing.

THE DEFECT. `adopt_unified_5d.py:35` pins `_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"` and
inserts it at `sys.path` position 0 when imported. `z_contract` imports it for `VERT_BANDS`, so
before the repair that entry preceded `import uq_math` and every later unqualified import in the Z
chain. Measured 2026-09-15 against `/pscratch/sd/j/josephrb/zdeploy-20b97fa9`: `z_receipt`'s
`from unified_throw_cov import _atomic_savez` bound the DATA-ROOT copy while A-2(f) certified the
deployment, and `mnv_guarded_run.py --expect-root <deployment>` returned
`REFUSED -- AN IMPORT RESOLVED OUTSIDE THE EXPECTED TREE`.

WHY THE FIX IS HERE AND NOT IN THAT FILE. Its bytes are bound by
`ben106-stamp-verify-active-56695424.json` and checked AT RUNTIME by
`mii_adopt_unified_5d_stamped.assert_pinned_writer_is_intact`, which refuses to launch against
modified bytes: "Do not update the digest -- re-issue or retire the owning receipt." Lane C
`783d648a` §25 and `RULING-20260817-lanec-pinned-readers-get-wrappers-not-copies.md` say the same.

CONTAINMENT IS NOT CONCEALMENT, and the last class below is the one that keeps it honest: if the
pinned module ever genuinely LOADS a foreign module, restoring the path does not unload it, and the
guard must still refuse. A repair that made that case quiet would be worse than the defect.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
GUARD = ND / "mnv_guarded_run.py"
PINNED = ND / "adopt_unified_5d.py"
OLD_LITERAL = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"


def _py(code, **kw):
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, **kw)


def _tail_json(out):
    return json.loads(out.strip().splitlines()[-1])


# ----------------------------------------------------- 1. two-tree behavioural reproduction ----
class TwoTreeContaminationAndRepair(unittest.TestCase):
    """Build the defect and the repair as two real trees; run the REAL guard against both.

    A two-file fixture rather than a copy of the repository: the mechanism is general -- one module
    in the expected tree inserts an absolute path, and a later unqualified import then binds a
    same-named module OUTSIDE it. Symlinking the repo would defeat the test, because
    `Path(__file__).resolve()` follows symlinks back to the original tree.
    """

    def _tree(self, td, contain: bool, foreign_import: bool = False):
        dep = Path(td) / ("dep_contained" if contain else "dep_bad")
        out = Path(td) / "outside"
        (dep / "nd-unfolding").mkdir(parents=True, exist_ok=True)
        (out / "nd-unfolding").mkdir(parents=True, exist_ok=True)
        # The guard's own precondition, quoted from its refusal: --expect-root must be "a checkout
        # (needs VALIDATION_LEDGER.md and nd-unfolding)". Without these it exits 2 (COULD NOT LOOK),
        # and 2 must never be read as a clean verdict.
        for t in (dep, out):
            (t / "VALIDATION_LEDGER.md").write_text("# fixture checkout marker\n")
        # `victim` exists in BOTH trees: the defect changes WHICH one binds, not whether it binds.
        (out / "nd-unfolding" / "victim.py").write_text("ORIGIN = 'OUTSIDE'\n")
        (dep / "nd-unfolding" / "victim.py").write_text("ORIGIN = 'DEPLOYMENT'\n")
        (out / "nd-unfolding" / "foreign_only.py").write_text("MARK = 'OUTSIDE-ONLY'\n")
        # The pinned writer we may not edit: an absolute insert, exactly the real shape.
        body = ("import sys\n"
                f"_REPO = {str(out)!r}\n"
                "for _p in (f'{_REPO}/nd-unfolding', f'{_REPO}/2d-unfolding'):\n"
                "    if _p not in sys.path:\n"
                "        sys.path.insert(0, _p)\n")
        if foreign_import:
            # It does not merely add a path -- it LOADS something only the outside tree has.
            body += "import foreign_only  # noqa: F401\n"
        (dep / "nd-unfolding" / "pinned_writer.py").write_text(body)
        contain_src = ("_snap = list(sys.path)\n"
                       "import pinned_writer  # noqa: F401\n"
                       "sys.path[:] = _snap\n") if contain else (
                       "import pinned_writer  # noqa: F401\n")
        (dep / "nd-unfolding" / "importer.py").write_text(
            "import sys, os, json\n"
            "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
            + contain_src +
            "import victim\n"
            "print(json.dumps({'origin': victim.ORIGIN, 'file': victim.__file__}))\n"
        )
        return dep, out

    def _guard(self, dep, td, name):
        inv = Path(td) / f"{name}.jsonl"
        r = subprocess.run(
            [sys.executable, str(GUARD), "--expect-root", str(dep), "--inventory", str(inv),
             "--", str(dep / "nd-unfolding" / "importer.py")],
            capture_output=True, text=True)
        return r, inv

    def test_the_UNCONTAINED_chain_binds_the_OUTSIDE_copy_and_the_guard_REFUSES(self):
        with tempfile.TemporaryDirectory() as td:
            dep, _ = self._tree(td, contain=False)
            r, inv = self._guard(dep, td, "bad")
            self.assertEqual(r.returncode, 3,
                             f"expected REFUSED (3); rc={r.returncode}\nstderr={r.stderr[-700:]}")
            self.assertIn("REFUSED", r.stdout + r.stderr)
            rows = [json.loads(l) for l in inv.read_text().splitlines() if l.strip()]
            self.assertTrue(any("REFUSED" in str(x.get("verdict", "")) for x in rows))

    def test_the_CONTAINED_chain_binds_the_DEPLOYMENT_copy_and_the_guard_PASSES(self):
        with tempfile.TemporaryDirectory() as td:
            dep, _ = self._tree(td, contain=True)
            r, _inv = self._guard(dep, td, "good")
            self.assertEqual(r.returncode, 0,
                             f"expected PASS; rc={r.returncode}\nstderr={r.stderr[-700:]}")
            got = _tail_json(r.stdout)
            self.assertEqual(got["origin"], "DEPLOYMENT")
            self.assertTrue(got["file"].startswith(str(dep)), got["file"])

    def test_the_two_trees_differ_ONLY_in_the_containment(self):
        """Control on the fixture: otherwise the paired verdicts would not isolate the change."""
        with tempfile.TemporaryDirectory() as td:
            bad, _ = self._tree(td, contain=False)
            good, _ = self._tree(td, contain=True)
            for name in ("pinned_writer.py", "victim.py"):
                self.assertEqual((bad / "nd-unfolding" / name).read_text(),
                                 (good / "nd-unfolding" / name).read_text(), name)
            b = (bad / "nd-unfolding" / "importer.py").read_text()
            g = (good / "nd-unfolding" / "importer.py").read_text()
            self.assertNotEqual(b, g)
            self.assertEqual(g.replace("_snap = list(sys.path)\n", "")
                              .replace("sys.path[:] = _snap\n", ""), b,
                             "the trees must differ by the snapshot/restore lines and nothing else")


# ------------------------------------------- 2. unrelated entries and their order survive ------
class UnrelatedPathEntriesSurviveUnchanged(unittest.TestCase):
    def test_importing_z_contract_leaves_pre_existing_entries_and_ORDER_untouched(self):
        sentinels = ["/zz-sentinel-a", "/zz-sentinel-b", "/zz-sentinel-c"]
        probe = (
            "import sys, json\n"
            f"sys.path.extend({sentinels!r})\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "before = list(sys.path)\n"
            "import z_contract  # noqa: F401\n"
            "after = list(sys.path)\n"
            "print(json.dumps({'before': before, 'after': after}))\n"
        )
        r = _py(probe)
        self.assertEqual(r.returncode, 0, r.stderr[-600:])
        d = _tail_json(r.stdout)
        before, after = d["before"], d["after"]
        # Every pre-existing entry still present...
        for p in before:
            self.assertIn(p, after, f"pre-existing entry dropped: {p!r}")
        # ...in the same RELATIVE ORDER (z_contract may prepend its own).
        kept = [p for p in after if p in before]
        self.assertEqual(kept, before, "pre-existing entries were reordered")
        # ...and the sentinels specifically, adjacent and in order.
        idx = [after.index(s) for s in sentinels]
        self.assertEqual(idx, sorted(idx), "sentinel order changed")
        # Anything z_contract ADDED must be inside the intended tree.
        for p in [p for p in after if p not in before]:
            self.assertTrue(str(Path(p).resolve()).startswith(str(REPO.resolve())),
                            f"z_contract added an entry outside its own tree: {p!r}")

    def test_the_data_root_literal_is_not_left_on_the_path(self):
        probe = (
            "import sys, json\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import z_contract  # noqa: F401\n"
            f"print(json.dumps([p for p in sys.path if p.startswith({OLD_LITERAL!r})]))\n"
        )
        r = _py(probe)
        self.assertEqual(r.returncode, 0, r.stderr[-600:])
        leaked = _tail_json(r.stdout)
        if not str(REPO).startswith(OLD_LITERAL):
            self.assertEqual(leaked, [], f"data-root entries survived: {leaked}")

    def test_the_sentinel_control_can_actually_fail(self):
        """If the probe could not see a dropped entry, the test above would be decorative."""
        probe = (
            "import sys, json\n"
            "sys.path.append('/zz-sentinel-a')\n"
            "before = list(sys.path)\n"
            "sys.path.remove('/zz-sentinel-a')\n"
            "after = list(sys.path)\n"
            "print(json.dumps([p for p in before if p not in after]))\n"
        )
        self.assertEqual(_tail_json(_py(probe).stdout), ["/zz-sentinel-a"])


# ------------------------------------- 3. a LOADED foreign module must still refuse -------------
class ContainmentDoesNotConcealALoadedForeignModule(unittest.TestCase):
    """The honesty control. Restoring a path does not unload a module, and must not."""

    def test_a_foreign_module_LOADED_during_the_pinned_import_still_REFUSES(self):
        helper = TwoTreeContaminationAndRepair()
        with tempfile.TemporaryDirectory() as td:
            dep, out = helper._tree(td, contain=True, foreign_import=True)
            r, inv = helper._guard(dep, td, "loaded_foreign")
            self.assertEqual(
                r.returncode, 3,
                "containment must NOT hide a foreign module that was actually imported; "
                f"rc={r.returncode}\nstdout={r.stdout[-500:]}\nstderr={r.stderr[-700:]}")
            self.assertIn("REFUSED", r.stdout + r.stderr)
            blob = r.stdout + r.stderr
            self.assertIn("foreign_only", blob,
                          "the refusal must NAME the foreign module, not merely refuse")

    def test_the_same_tree_WITHOUT_the_foreign_import_passes(self):
        """Pairs with the above: proves the refusal is caused by the LOAD, not by the fixture."""
        helper = TwoTreeContaminationAndRepair()
        with tempfile.TemporaryDirectory() as td:
            dep, _ = helper._tree(td, contain=True, foreign_import=False)
            r, _ = helper._guard(dep, td, "no_foreign")
            self.assertEqual(r.returncode, 0, r.stderr[-600:])

    def test_z_contract_does_not_touch_sys_modules(self):
        """No foreign module is evicted, and no origin is rewritten."""
        src = (ND / "z_contract.py").read_text()
        for forbidden in ("sys.modules.pop", "del sys.modules", "sys.modules.clear",
                          "__file__ =", "importlib.reload"):
            self.assertNotIn(forbidden, src, f"z_contract must not use {forbidden!r}")


# --------------------- 4. Z consumers and the pinned runtime paths keep their behaviour --------
class ZConsumersAndPinnedPathsUnchanged(unittest.TestCase):
    def test_VERT_BANDS_still_comes_from_the_pinned_module_in_THIS_tree(self):
        probe = (
            "import sys, json\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import z_contract as zc, adopt_unified_5d as a\n"
            "print(json.dumps({'equal': list(zc.VERT_BANDS) == list(a.VERT_BANDS),\n"
            "                  'n': len(zc.VERT_BANDS), 'adopt': a.__file__,\n"
            "                  'nres': zc.N_RESIDUAL, 'nlat': len(zc.LATERAL_BANDS)}))\n"
        )
        r = _py(probe)
        self.assertEqual(r.returncode, 0, r.stderr[-600:])
        d = _tail_json(r.stdout)
        self.assertTrue(d["equal"], "VERT_BANDS diverged from the pinned module")
        self.assertEqual(d["n"], 13)
        self.assertEqual(d["nres"], 27)
        self.assertEqual(d["nlat"], 5)
        self.assertTrue(d["adopt"].startswith(str(REPO.resolve())), d["adopt"])

    def test_the_pinned_writer_is_byte_unchanged_and_its_runtime_pin_holds(self):
        """The whole reason the repair lives in z_contract: these bytes may not move."""
        digest = hashlib.sha256(PINNED.read_bytes()).hexdigest()
        self.assertEqual(
            digest, "e1260e8dec2d39cb4653a8b4b02a198d04ea103d548a2d90b5f003f0b8044c35",
            "adopt_unified_5d.py's bytes moved; its receipt binding and the runtime pin in "
            "mii_adopt_unified_5d_stamped.assert_pinned_writer_is_intact both break")
        probe = (
            "import sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import mii_adopt_unified_5d_stamped as W\n"
            "W.assert_pinned_writer_is_intact()\n"
            "print('PIN-OK')\n"
        )
        r = _py(probe, cwd=str(REPO))
        self.assertEqual(r.returncode, 0,
                         f"the runtime pin must still pass; stderr={r.stderr[-700:]}")
        self.assertIn("PIN-OK", r.stdout)

    def test_the_band_partition_gate_still_runs_on_the_real_constants(self):
        probe = (
            "import sys, json\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import z_contract as zc\n"
            "R = tuple(f'r{i}' for i in range(zc.N_RESIDUAL))\n"
            "inv = list(zc.VERT_BANDS) + list(R) + list(zc.LATERAL_BANDS)\n"
            "out = zc.check_band_partition(zc.VERT_BANDS, R, zc.LATERAL_BANDS, inv)\n"
            "print(json.dumps({'ran': out is not None or True}))\n"
        )
        r = _py(probe)
        self.assertEqual(r.returncode, 0, r.stderr[-600:])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""N-3: each of the six OI-136 source repairs actually repaired something, in BOTH directions.

`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` section 5, N-3: for each repaired file, with
the PRE-repair bytes and a scratch checkout carrying its own copy of the victim module, the
entrypoint must import the OTHER tree's copy -- and still must with `PYTHONPATH` pointed at the
scratch tree, because position 0 cannot be outranked -- while with the POST-repair bytes the same
fixture resolves to its own tree. A filter needs a test in the direction it acts AND a test that it
is silent in the other direction.

WHAT IS EXECUTED, AND THE LIMIT OF IT -- STATED FIRST BECAUSE IT BOUNDS EVERY CLAIM BELOW.
These six entrypoints cannot be run to completion off-cluster: they import ROOT, LightGBM and
TensorFlow, and three of them read multi-GB products. So what runs here is each file's own ROOT
RESOLUTION PROLOGUE -- its real bytes, lines 1..N, where N is the end line of the LAST top-level
statement containing a `sys.path.insert`, located by `ast`, not by a regex and not by hand. That
prologue is exactly what the repair changed and exactly what decides where a later import resolves.
It is NOT the whole file, so this test says nothing about the science below the cut. The cut line
for each file is asserted to be the file's own insert statement, so a prologue that stopped short
would fail rather than silently measure less.

THE PRE-REPAIR BYTES COME FROM GIT, NOT FROM INVERTING THE REPAIR. A fixture derived from the rule
cannot disagree with it. `git show <BASE_SHA>:<path>` is the branch point; the only edit made to
those bytes is rewriting the hardcoded cluster root to a scratch stand-in, because the real one is
not present off-cluster -- and that rewrite is asserted to have changed exactly the root string.
"""
import ast
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
REPO = HERE.parents[1]

#: The commit this branch was cut from. The PRE-repair bytes are read from it. It is an ancestor of
#: every commit on this branch, so it does not rot; if it is ever unreachable that is a real finding
#: about the checkout and this test says so rather than skipping.
BASE_SHA = "8c156a374a00e024b9f28d575d38c75f345dcb3b"

#: Assembled from parts for the same reason the OI-136 probe assembles it: a test that spelled the
#: cluster root out would add itself to the population that probe measures.
CLUSTER_ROOT = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))

#: The victim is a real repository module name. Only its RESOLUTION is under test, so the copies
#: planted in the two scratch trees are one-line stubs that announce which tree they came from.
VICTIM = "xsec_nd"

#: `sweep_bank_5d.py` imports `seed_offset_policy` ABOVE its own insert, from the script's own
#: directory. Both scratch trees carry a stub of it so the prologue can execute; it is not the
#: victim, precisely because resolving it does not depend on the insert.
EARLY_IMPORT = "seed_offset_policy"

#: (path relative to the repo root, expected parents[N] in the repaired form)
REPAIRED = (
    ("nd-unfolding/bootstrap_nd.py", 0),
    ("nd-unfolding/seedscan_split.py", 0),
    ("nd-unfolding/unfold_nd_omnifold_unbinned.py", 1),
    ("nd-unfolding/sweep_bank_5d.py", 1),
    ("nd-unfolding/unified_throw_cov_5d.py", 1),
    ("nd-unfolding/unified_throw_cov.py", 1),
)

PROBE_TAIL = (
    "\nimport {victim} as _v\n"
    "print('VICTIM_FILE', _v.__file__)\n"
).format(victim=VICTIM)


def prologue(src: str, path_for_message: str) -> str:
    """Lines 1..end of the LAST top-level statement that contains a `sys.path.insert`."""
    tree = ast.parse(src)
    end = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            break
        dumped = ast.dump(node)
        if "sys" in dumped and "path" in dumped and "insert" in dumped:
            end = node.end_lineno
    if end is None:
        raise AssertionError(f"no top-level sys.path.insert found in {path_for_message}; the cut "
                             "cannot be located, so this measures nothing")
    return "\n".join(src.splitlines()[:end]) + "\n"


def make_checkout(base: pathlib.Path, name: str, mark: str) -> pathlib.Path:
    root = base / name
    for sub in ("nd-unfolding", "2d-unfolding"):
        (root / sub).mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    (root / "nd-unfolding" / f"{VICTIM}.py").write_text(f"MARK = {mark!r}\n")
    (root / "nd-unfolding" / f"{EARLY_IMPORT}.py").write_text(f"MARK = {mark!r}\n")
    return root


class TheSixRepairsChangeWhereImportsResolve(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        # The stand-in for the hardcoded cluster tree. The PRE-repair bytes are pointed here.
        self.canonical = make_checkout(tmp, "canonical-stand-in", "CANONICAL TREE")
        # The scratch checkout the entrypoint is actually launched from, carrying its OWN victim.
        self.clean = make_checkout(tmp, "clean-tree", "CLEAN TREE")
        # `unfold_nd_omnifold_unbinned.py` imports ROOT above its insert and there is no ROOT off
        # the cluster. A stub satisfies the import without pretending to be PyROOT: nothing below
        # the cut runs, so no ROOT behaviour is modelled or needed.
        self.stubs = tmp / "thirdparty-stubs"
        self.stubs.mkdir()
        (self.stubs / "ROOT.py").write_text("# stub: import-only, models nothing\n")

    def _run_prologue(self, src: str, name: str, extra_pythonpath=()):
        target = self.clean / "nd-unfolding" / name
        target.write_text(src + PROBE_TAIL)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env["PYTHONPATH"] = os.pathsep.join([str(self.stubs), *[str(p) for p in extra_pythonpath]])
        cp = subprocess.run([sys.executable, str(target)], capture_output=True, text=True,
                            env=env, cwd=str(self.clean / "nd-unfolding"))
        return cp

    @staticmethod
    def _victim_file(cp):
        hits = [l for l in cp.stdout.splitlines() if l.startswith("VICTIM_FILE ")]
        if len(hits) != 1:
            raise AssertionError(f"expected exactly one VICTIM_FILE line, got {hits}\n"
                                 f"stdout:\n{cp.stdout}\nstderr:\n{cp.stderr}")
        return pathlib.Path(hits[0].split(None, 1)[1]).resolve()

    def _pre_bytes(self, rel):
        cp = subprocess.run(["git", "show", f"{BASE_SHA}:{rel}"], cwd=str(REPO),
                            capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0,
                         f"{BASE_SHA}:{rel} is unreachable in this checkout -- that is a finding "
                         f"about the checkout, not a reason to skip:\n{cp.stderr}")
        src = cp.stdout
        self.assertIn(CLUSTER_ROOT, src,
                      f"the PRE-repair bytes of {rel} do not contain the hardcoded root, so this "
                      "fixture is not reproducing the defect it claims to")
        rewritten = src.replace(CLUSTER_ROOT, str(self.canonical))
        self.assertNotEqual(rewritten, src)
        self.assertNotIn(CLUSTER_ROOT, rewritten)
        return rewritten

    def test_PRE_repair_the_entrypoint_imports_the_OTHER_trees_copy(self):
        """The hijack arm. Asserted on the loaded module's `__file__`, never on exit 0."""
        for rel, _n in REPAIRED:
            with self.subTest(file=rel):
                src = prologue(self._pre_bytes(rel), rel)
                cp = self._run_prologue(src, pathlib.Path(rel).name)
                self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertEqual(self._victim_file(cp),
                                 (self.canonical / "nd-unfolding" / f"{VICTIM}.py").resolve())

    def test_PRE_repair_PYTHONPATH_CANNOT_OUTRANK_POSITION_ZERO(self):
        """The reason a re-deploy and an env var are both the wrong repair."""
        for rel, _n in REPAIRED:
            with self.subTest(file=rel):
                src = prologue(self._pre_bytes(rel), rel)
                cp = self._run_prologue(src, pathlib.Path(rel).name,
                                        extra_pythonpath=[self.clean / "nd-unfolding"])
                self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertEqual(self._victim_file(cp),
                                 (self.canonical / "nd-unfolding" / f"{VICTIM}.py").resolve(),
                                 "PYTHONPATH appeared to outrank sys.path[0], which would mean "
                                 "this fixture is not reproducing the defect")

    def test_POST_repair_the_same_fixture_resolves_to_ITS_OWN_tree(self):
        """The silent direction. The repair must not merely fire; it must fix."""
        for rel, _n in REPAIRED:
            with self.subTest(file=rel):
                src = prologue((REPO / rel).read_text(), rel)
                self.assertNotIn(f'insert(0, "{CLUSTER_ROOT}', src)
                cp = self._run_prologue(src, pathlib.Path(rel).name)
                self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
                self.assertEqual(self._victim_file(cp),
                                 (self.clean / "nd-unfolding" / f"{VICTIM}.py").resolve())

    def test_the_repaired_prologues_derive_from___file___with_no_absolute_fallback(self):
        """The repair FORM, not just its effect: `parents[N]`, and no rooted literal reachable by
        any insert. The three files that keep the literal keep it in `_DATA_ROOT`, which no
        `sys.path` statement touches -- asserted here rather than trusted."""
        for rel, n in REPAIRED:
            with self.subTest(file=rel):
                src = prologue((REPO / rel).read_text(), rel)
                self.assertIn(f"parents[{n}]", src,
                              f"{rel} must derive its import root from parents[{n}]")
                self.assertIn("Path(__file__).resolve()", src)
                tree = ast.parse(src)
                rooted = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                            and isinstance(node.value.value, str) \
                            and CLUSTER_ROOT in node.value.value:
                        rooted |= {t.id for t in node.targets if isinstance(t, ast.Name)}
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                            and node.func.attr == "insert":
                        names = {c.id for c in ast.walk(node) if isinstance(c, ast.Name)}
                        self.assertFalse(names & rooted,
                                         f"{rel}: a sys.path.insert argument still reaches a "
                                         f"rooted constant {sorted(names & rooted)}")
                        for c in ast.walk(node):
                            if isinstance(c, ast.Constant) and isinstance(c.value, str):
                                self.assertNotIn(CLUSTER_ROOT, c.value, rel)

    def test_the_cut_really_is_the_files_own_insert_statement(self):
        """Non-vacuity of the extraction. A prologue that stopped short would measure nothing."""
        for rel, _n in REPAIRED:
            with self.subTest(file=rel):
                src = prologue((REPO / rel).read_text(), rel)
                self.assertIn("sys.path.insert(0,", src.replace("sys.path.insert(0, ",
                                                                "sys.path.insert(0,"))
                self.assertIn("insert", src.splitlines()[-1])


if __name__ == "__main__":
    unittest.main(verbosity=2)

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


def _mentions_root(node) -> bool:
    """Does this subtree contain the cluster-root literal anywhere?"""
    return any(isinstance(c, ast.Constant) and isinstance(c.value, str)
               and CLUSTER_ROOT in c.value for c in ast.walk(node))


def _names_in(node) -> set:
    return {c.id for c in ast.walk(node) if isinstance(c, ast.Name)}


def _bound_names(target) -> set:
    """Names bound by an assignment or `for` target, including tuple/list unpacking."""
    return {c.id for c in ast.walk(target) if isinstance(c, ast.Name)}


def rooted_insert_offenders(src: str) -> list:
    """Every `sys.path` insert/append argument in `src` that can carry the cluster root.

    WHY A TAINT FIXPOINT AND NOT A NAME SET. The first version of this check collected only names
    assigned a STRING CONSTANT containing the root, then looked for those names inside an insert
    call. Mutation-tested, that catches a bare literal and `insert(0, _DATA_ROOT)` and NOTHING
    ELSE -- it misses `_D = f"{_DATA_ROOT}/nd-unfolding"; insert(0, _D)` (the value is a JoinedStr,
    not a Constant, so `_D` was never tainted) and it misses
    `for _p in (f"{_DATA_ROOT}/2d-unfolding", ...): insert(0, _p)` (`_p` is a loop target, not an
    assignment). THE LOOP FORM IS THE SHAPE FOUR OF THE SIX REPAIRED FILES USE, so over the
    population it was asked about the old assertion was very nearly vacuous. That is the same
    defect the OI-136 probe's own docstring records finding in its first two classifiers.

    So taint propagates to a fixpoint through: assignment, annotated assignment, augmented
    assignment, `for` targets (from the ITERABLE), and `with ... as`. An expression is tainted if
    it contains the root literal OR references a tainted name. Returns the offending argument
    source segments, so a failure names what it found.
    """
    tree = ast.parse(src)
    tainted: set = set()
    for _ in range(10):
        before = set(tainted)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                value = getattr(node, "value", None)
                if value is None:
                    continue
                if _mentions_root(value) or (_names_in(value) & tainted):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in targets:
                        tainted |= _bound_names(t)
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                if _mentions_root(node.iter) or (_names_in(node.iter) & tainted):
                    tainted |= _bound_names(node.target)
            elif isinstance(node, ast.withitem):
                if node.optional_vars is not None and (
                        _mentions_root(node.context_expr)
                        or (_names_in(node.context_expr) & tainted)):
                    tainted |= _bound_names(node.optional_vars)
        if tainted == before:
            break

    offenders = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr not in ("insert", "append", "extend"):
            continue
        # `sys.path.insert(...)` / `path.insert(...)` -- match on the receiver mentioning `path`,
        # which is what every form in this repository uses.
        recv = ast.dump(node.func.value)
        if "path" not in recv:
            continue
        for arg in node.args:
            if _mentions_root(arg) or (_names_in(arg) & tainted):
                offenders.append(ast.get_source_segment(src, arg) or ast.dump(arg))
    return offenders


class TheOffenderCheckerHasPower(unittest.TestCase):
    """Mutation tests, BOTH DIRECTIONS. A checker with no demonstrated discrimination reports
    success on anything, and this one shipped once already in a form that did exactly that."""

    #: Each must be CAUGHT. The last two are the shapes the first version of the check missed.
    MUST_FIRE = {
        "bare literal in the insert argument":
            'import sys\nsys.path.insert(0, "%s/nd-unfolding")\n' % CLUSTER_ROOT,
        "directly named rooted constant":
            'import sys\n_D = "%s"\nsys.path.insert(0, _D)\n' % CLUSTER_ROOT,
        "ONE-HOP derived name (f-string off a rooted constant)":
            'import sys\n_D = "%s"\n_ND = f"{_D}/nd-unfolding"\nsys.path.insert(0, _ND)\n'
            % CLUSTER_ROOT,
        "TWO-HOP derived name":
            'import sys\n_D = "%s"\n_A = f"{_D}/x"\n_B = _A + "/y"\n'
            'sys.path.insert(0, _B)\n' % CLUSTER_ROOT,
        "for-loop iterable holding rooted f-strings (the 4-of-6 shape)":
            'import sys\n_D = "%s"\n'
            'for _p in (f"{_D}/2d-unfolding", f"{_D}/nd-unfolding"):\n'
            '    if _p not in sys.path:\n        sys.path.insert(0, _p)\n' % CLUSTER_ROOT,
        "for-loop over already-derived names":
            'import sys\n_D = "%s"\n_2D = f"{_D}/2d-unfolding"\n_ND = f"{_D}/nd-unfolding"\n'
            'for p in (_2D, _ND):\n    sys.path.insert(0, p)\n' % CLUSTER_ROOT,
        "os.path.join off a rooted constant":
            'import os, sys\n_D = "%s"\nsys.path.insert(0, os.path.join(_D, "nd-unfolding"))\n'
            % CLUSTER_ROOT,
        "append instead of insert":
            'import sys\n_D = "%s"\nsys.path.append(_D)\n' % CLUSTER_ROOT,
    }

    #: Each must stay SILENT. A narrowing needs a test that it does not fire where it should not.
    MUST_NOT_FIRE = {
        "the repaired shape: derived import root, separate untouched data root":
            'import sys\nfrom pathlib import Path\n'
            '_REPO = str(Path(__file__).resolve().parents[1])\n'
            'for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):\n'
            '    if _p not in sys.path:\n        sys.path.insert(0, _p)\n'
            '_DATA_ROOT = "%s"\n' % CLUSTER_ROOT,
        "data root used only in an argparse default":
            'import argparse, sys\nfrom pathlib import Path\n'
            '_ND = str(Path(__file__).resolve().parents[0])\n'
            'sys.path.insert(0, _ND)\n'
            '_DATA_ROOT = "%s"\n'
            'ap = argparse.ArgumentParser()\n'
            'ap.add_argument("--mcfile", default=f"{_DATA_ROOT}/2d-unfolding/x.root")\n'
            % CLUSTER_ROOT,
        "data root in a plain module constant that is never inserted":
            'import sys\nfrom pathlib import Path\n'
            '_ND = str(Path(__file__).resolve().parents[0])\n'
            'sys.path.insert(0, _ND)\n'
            '_DATA_ROOT = "%s"\n'
            'VLIST = f"{_DATA_ROOT}/nd-unfolding/uq_4d/vertical_universes.txt"\n' % CLUSTER_ROOT,
        "no cluster root anywhere":
            'import sys\nfrom pathlib import Path\n'
            'sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n',
    }

    def test_every_rooted_insert_shape_is_CAUGHT(self):
        for name, src in self.MUST_FIRE.items():
            with self.subTest(shape=name):
                self.assertNotEqual(rooted_insert_offenders(src), [],
                                    f"NOT CAUGHT: {name}\n{src}")

    def test_it_is_SILENT_on_every_legitimate_shape(self):
        for name, src in self.MUST_NOT_FIRE.items():
            with self.subTest(shape=name):
                self.assertEqual(rooted_insert_offenders(src), [],
                                 f"FALSE POSITIVE: {name}\n{src}")

    def test_the_loop_shape_really_is_what_four_of_the_six_files_use(self):
        """The population claim the mutation set is calibrated against, measured not asserted."""
        loop_shaped = []
        for rel, _n in REPAIRED:
            src = prologue((REPO / rel).read_text(), rel)
            tree = ast.parse(src)
            inserts_via_loop = False
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    for c in ast.walk(node):
                        if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) \
                                and c.func.attr == "insert":
                            inserts_via_loop = True
            if inserts_via_loop:
                loop_shaped.append(rel)
        self.assertEqual(len(loop_shaped), 4, loop_shaped)


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
        """The repair FORM, not just its effect: `parents[N]`, and no rooted value reachable by any
        `sys.path` insert. The three files that keep the cluster literal keep it in `_DATA_ROOT`,
        which no `sys.path` statement touches. Checked by `rooted_insert_offenders`, whose power is
        mutation-tested in `TheOffenderCheckerHasPower` below -- the FIRST version of this assertion
        caught only a bare literal and a directly-named constant, and therefore said nothing about
        the loop-iterable shape that four of these six files actually use."""
        for rel, n in REPAIRED:
            with self.subTest(file=rel):
                src = prologue((REPO / rel).read_text(), rel)
                self.assertIn(f"parents[{n}]", src,
                              f"{rel} must derive its import root from parents[{n}]")
                self.assertIn("Path(__file__).resolve()", src)
                self.assertEqual(rooted_insert_offenders(src), [], rel)

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

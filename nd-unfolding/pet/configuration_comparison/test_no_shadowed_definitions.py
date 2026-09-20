"""No module here may define the same top-level name twice.

A duplicate definition is invisible to every test that asserts on SOURCE TEXT:
`assertIn("...", source)` still passes when the code it matched is shadowed by
a later copy and never runs. That is how a one-time-gather rewrite sat dead in
`run_arm_evaluation` while its tests were green -- Python binds the LAST
definition, and the stale earlier behaviour is what executed.

The cause was a slice replace whose END anchor occurred BEFORE its start
anchor, so `src[:start] + new + src[end:]` re-appended the original. It
produces no syntax error and no warning; `ast` is the only thing that sees it.
"""
from __future__ import annotations

import ast
import collections
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP = {"__init__.py"}


def _modules():
    return sorted(p for p in HERE.glob("*.py")
                  if p.name not in SKIP and not p.name.startswith("test_"))


class NoDuplicateTopLevelNames(unittest.TestCase):
    def test_no_module_defines_a_function_or_class_twice(self):
        offenders = {}
        for path in _modules():
            tree = ast.parse(path.read_text())
            names = [n.name for n in tree.body
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                       ast.ClassDef))]
            dupes = sorted(k for k, v in collections.Counter(names).items() if v > 1)
            if dupes:
                offenders[path.name] = dupes
        self.assertEqual(offenders, {},
                         msg="a later definition silently shadows an earlier one")

    def test_no_module_assigns_the_same_module_constant_twice(self):
        """A re-assigned constant has the same shape of failure."""
        offenders = {}
        for path in _modules():
            tree = ast.parse(path.read_text())
            names = []
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            names.append(target.id)
            dupes = sorted(k for k, v in collections.Counter(names).items() if v > 1)
            if dupes:
                offenders[path.name] = dupes
        self.assertEqual(offenders, {})

    def test_the_tests_themselves_are_checked(self):
        offenders = {}
        for path in sorted(HERE.glob("test_*.py")):
            tree = ast.parse(path.read_text())
            names = [n.name for n in tree.body
                     if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
            dupes = sorted(k for k, v in collections.Counter(names).items() if v > 1)
            if dupes:
                offenders[path.name] = dupes
        self.assertEqual(offenders, {},
                         msg="a shadowed test class never runs and never fails")


if __name__ == "__main__":
    unittest.main()

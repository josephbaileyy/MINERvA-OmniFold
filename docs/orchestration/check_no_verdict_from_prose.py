#!/usr/bin/env python3
"""Flag a VERDICT decided by string-matching the tool's OWN DIAGNOSTIC MESSAGES.

FOUR INSTANCES IN ONE DAY (`BEN-482`) made this a habit rather than a coincidence, and the fourth was
inside the comparator built to enforce rigour:

    1  the repo's stamp lint scraped the English word "and" out of a comment
    2  `assertNotIn("require_completeness=False", src)` matched the comment explaining the removal
    3  `assertNotIn('if "member_k" in str(o)', src)` matched the docstring quoting the retired predicate
    4  `mii_anchor_comparator` computed its verdict with `any("!=" in l or "ABSENT" in l for l in lines)`

Instances 1-3 are a matcher reading the wrong corpus and are hard to detect mechanically. **INSTANCE 4
IS NOT**, and it is the dangerous one: **a verdict derived from its own prose changes when someone
rewords a message.** A reviewer improving an error string can flip a gate from FAIL to PASS with no
test noticing, because the test asserts the verdict and the verdict reads the string.

=====================================================================================================
DELIBERATELY NARROW, AND THAT IS A DESIGN DECISION RATHER THAN LAZINESS.

An over-broad check gets DELETED or allowlisted, not fixed -- the cheapest way past it is to remove it,
and whoever does that is right in the instance and wrong about the rule. My own first attempt at a
narrower version of this exact family banned ALL containment on a token and fired on a legitimate use
that produced a BETTER error message; satisfying it would have meant deleting the better message.

So this fires on ONE shape: a control-flow condition or a returned value that tests a STRING LITERAL
for membership in an element of a variable whose name says it holds messages. It will miss real
instances. It should almost never fire on a false one.
=====================================================================================================
"""
import argparse
import ast
import os
import subprocess
import sys

#: Names that say "this holds diagnostics". Extend deliberately; each addition widens the check.
MESSAGE_NAMES = frozenset({
    "lines", "findings", "problems", "messages", "msgs", "errors", "warnings",
    "output", "out_lines", "report", "reasons", "diagnostics", "why",
})


def _is_message_source(node):
    """True if `node` reads one of MESSAGE_NAMES, directly or as an element of one."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id in MESSAGE_NAMES:
            return sub.id
    return None


def _comprehension_bindings(node):
    """target name -> message-list name, for every comprehension under `node`.

    THE POWER FIXTURE CAUGHT THAT THIS WAS MISSING, ON THE FIRST RUN, AND IT IS NOT A CORNER CASE --
    IT IS THE FORM ALL FOUR REAL INSTANCES TOOK:

        any("differ" in l for l in lines)

    The `Compare` node's right-hand side is `l`, the comprehension VARIABLE. `lines` appears only in the
    generator's `iter`. So a check that inspects the comparison alone sees a name it knows nothing about
    and stays silent -- which is exactly the "cannot fire" state this module's own docstring calls worse
    than absence. One binding hop is required, and it is required for the ONLY shape that matters.
    """
    binds = {}
    for sub in ast.walk(node):
        if not isinstance(sub, (ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp)):
            continue
        for gen in sub.generators:
            src = _is_message_source(gen.iter)
            if src and isinstance(gen.target, ast.Name):
                binds[gen.target.id] = src
    return binds


def _string_membership_tests(node):
    """`"literal" in <expr>` comparisons under `node`, with the literal and the message-list name.

    Resolves one comprehension binding hop; see `_comprehension_bindings`.
    """
    binds = _comprehension_bindings(node)
    hits = []
    for sub in ast.walk(node):
        if not (isinstance(sub, ast.Compare) and any(isinstance(o, ast.In) for o in sub.ops)):
            continue
        if not (isinstance(sub.left, ast.Constant) and isinstance(sub.left.value, str)):
            continue
        if not sub.comparators:
            continue
        rhs = sub.comparators[0]
        src = _is_message_source(rhs)
        if src is None and isinstance(rhs, ast.Name):
            src = binds.get(rhs.id)          # `"x" in l  for l in lines`
        if src:
            hits.append((sub.left.value, src, sub.lineno))
    return hits


def findings(tree, rel):
    """Rows for one parsed module. Pure, so the self-test can exercise it without the filesystem."""
    rows = []
    for node in ast.walk(tree):
        # A verdict is either RETURNED or BRANCHED ON. Both are control flow over a message string.
        if isinstance(node, ast.If):
            where, expr = "branch", node.test
        elif isinstance(node, ast.Return) and node.value is not None:
            where, expr = "return", node.value
        elif isinstance(node, ast.Assert):
            where, expr = "assert", node.test
        else:
            continue
        for literal, src, lineno in _string_membership_tests(expr):
            rows.append({
                "file": rel, "line": lineno, "where": where, "literal": literal, "source": src,
                "why": (f"a {where} tests the literal {literal!r} for membership in {src!r} -- if "
                        f"{src} holds this tool's own diagnostic messages, the verdict changes when "
                        "someone rewords one. Decide with an explicit flag set where the condition is "
                        "DETECTED, not by re-reading what you printed about it."),
            })
    return rows


def _tracked_python(repo):
    out = subprocess.run(["git", "-C", repo, "ls-files", "*.py"],
                         capture_output=True, text=True, check=True).stdout
    return [l for l in out.split("\n") if l.strip()]


def sweep(repo, only=None):
    rows, parsed, unparsed = [], 0, []
    for rel in (only or _tracked_python(repo)):
        path = os.path.join(repo, rel)
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError) as exc:
            unparsed.append(f"{rel}: {exc.__class__.__name__}")
            continue
        parsed += 1
        rows.extend(findings(tree, rel))
    return rows, parsed, unparsed


#: THE POWER FIXTURE, IN THE LANGUAGE THIS CHECK WALKS. `BEN-481`: a detector's power fixture must be
#: written in every language its walk visits, AND so must its matcher -- a fixture proving the detector
#: FIRES over a matcher blind to the language is a green power test over a blind matcher. This walks
#: Python only and the fixture is Python, so the two agree by construction rather than by luck.
_POWER_POSITIVE = '''
def compare(a, b):
    lines = []
    if a != b:
        lines.append("values differ")
    if any("differ" in l for l in lines):
        return "FAIL", lines
    return "PASS", lines
'''

#: THE NEGATIVE CONTROL, which is what a NARROWING requires: the check must NOT fire here. Same
#: function, verdict decided by a flag set where the condition is detected -- the correct form.
_POWER_NEGATIVE = '''
def compare(a, b):
    lines, differed = [], False
    if a != b:
        lines.append("values differ")
        differed = True
    if differed:
        return "FAIL", lines
    return "PASS", lines
'''

#: AND A SECOND NEGATIVE, because the first could pass by the check being unable to see ANY `in` test.
#: Here a string membership test exists and is legitimate: it classifies INPUT, not the tool's output.
_POWER_NEGATIVE_LEGITIMATE = '''
def classify(path):
    if "/nd-unfolding/" in path:
        return "in tree"
    return "outside"
'''


#: THE REAL INSTANCE, VERBATIM, not a synthetic stand-in. This is `mii_anchor_comparator.compare_files`
#: as I first wrote it (fixed at 30c4d766). A fixture I invent proves the check fires on a shape I had
#: in mind while writing the check; a fixture lifted from the defect proves it fires on the shape that
#: actually occurred, which is a different and stronger claim. Both are kept -- the synthetic one is
#: minimal and readable, this one is evidence.
_POWER_REAL_INSTANCE = '''
def compare_files(artifact, archive_path, member_path, offset):
    verdict, findings = classes.compare(artifact, a_keys, m_keys)
    lines = list(findings)
    if verdict == "FAIL" or any("!=" in l or "CANNOT BE SATISFIED" in l or "ABSENT" in l
                                for l in lines):
        return "FAIL", lines
    if verdict == "INCOMPLETE" and not undischarged:
        return "PASS", lines
    return verdict, lines
'''


def self_test():
    """Assert the check FIRES on the shape and does NOT fire on the two correct forms."""
    problems = []
    pos = findings(ast.parse(_POWER_POSITIVE), "<power+>")
    if len(pos) != 1:
        problems.append(f"POWER FAILURE: expected 1 finding on the positive fixture, got {len(pos)}. "
                        "A check that cannot fire is worse than an absent one -- it reports green.")
    elif pos[0]["literal"] != "differ" or pos[0]["source"] != "lines":
        problems.append(f"POWER: fired but mis-reported: {pos[0]}")
    real = findings(ast.parse(_POWER_REAL_INSTANCE), "<power-real>")
    if len(real) != 3:
        problems.append(
            f"POWER FAILURE on the REAL instance: expected 3 findings (the three string literals in "
            f"the original verdict expression), got {len(real)}: {real}. A check that fires on my "
            "synthetic fixture and not on the defect that motivated it is checking my imagination.")
    elif {r["literal"] for r in real} != {"!=", "CANNOT BE SATISFIED", "ABSENT"}:
        problems.append(f"POWER: real instance fired on the wrong literals: {real}")
    for name, src in (("negative (flag-driven)", _POWER_NEGATIVE),
                      ("negative (classifies input)", _POWER_NEGATIVE_LEGITIMATE)):
        neg = findings(ast.parse(src), f"<{name}>")
        if neg:
            problems.append(f"FALSE POSITIVE on the {name} fixture: {neg}. An over-broad check gets "
                            "deleted rather than fixed, so this direction is the fatal one.")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--file", action="append", dest="files")
    a = ap.parse_args(argv)

    # THE SELF-TEST RUNS EVERY TIME, not only under its own flag. A detector whose power is proven by an
    # opt-in flag is a detector nobody proves.
    problems = self_test()
    if problems:
        for p in problems:
            print(f"[verdict-prose] SELF-TEST FAIL: {p}")
        return 3
    print("[verdict-prose] self-test OK: fires on the synthetic shape AND on the real "
          "pre-fix instance (3 literals), silent on both correct forms")
    if a.self_test:
        return 0

    rows, parsed, unparsed = sweep(a.repo, a.files)
    print(f"[verdict-prose] {parsed} modules parsed, {len(unparsed)} unparsable, {len(rows)} findings")
    for u in unparsed:
        print(f"[verdict-prose]   SKIP {u}")
    for r in rows:
        print(f"[verdict-prose] FINDING {r['file']}:{r['line']} ({r['where']})\n"
              f"                {r['why']}")
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())

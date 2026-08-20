#!/usr/bin/env python3
"""OI-136: how many `.py` files put the HARDCODED CLUSTER ROOT at `sys.path[0]`?

This is the FAIL-OPEN half of the hardcoded-path family. `OI-123`'s landmine is
fail-CLOSED and loud (a `die ... 3` before any GPU work). This one is silent: an
`insert(0, ...)` of an absolute path executes THAT tree's modules no matter which
checkout the entrypoint was launched from, and a deployment-parity check that
compares the *launched* tree can report CURRENT while the *executing* code is
behind. That is run 4's measured cause.

WHY A SCRIPT AND NOT A NUMBER IN THE ROW: the first count I produced by hand was
wrong by 4x in both directions on the way to the right one, and each wrong version
looked reasonable:

  * `grep -l <root> *.py | xargs grep -l sys.path.insert` -> 71. WRONG, too high:
    that conjunction never establishes that the insert USES the root. A file may
    hardcode the root in a default argument and separately insert its own parent.
  * assignment-only tracking of the root variable -> 17. WRONG, too low: the two
    files this OI is really about bind through a LOOP,
    `for _p in (f"{_REPO}/2d-unfolding", ...): sys.path.insert(0, _p)`, which no
    `NAME = ...` pattern can see.
  * assignment + loop + derived-name tracking -> 59, with both controls passing.

THE LITERAL IS ASSEMBLED FROM PARTS ON PURPOSE. If this file contained the root as
a literal it would match its own discoverer and report 118 instead of 117 -- a probe
that changes the quantity it measures. It also excludes itself by resolved path, so
either guard alone is sufficient and neither is load-bearing on its own.

TWO CONTROLS, because a classifier with no demonstrated discrimination reports
success on anything:
  * POSITIVE -- `adopt_unified_5d.py` and `unfold_nd_omnifold_unbinned.py` are the
    two files remedy (A) covers and are known hijackers by inspection. If either is
    missing from the set, the classifier UNDER-counts and the answer is CANNOT
    CHECK, not a smaller number.
  * NEGATIVE -- files whose `insert(0, ...)` is relative to their own location
    (`str(_anchor.parent)`) must be EXCLUDED. If nothing lands in that bucket the
    classifier has not been shown to reject anything, so again CANNOT CHECK.

Exit 0 = measured and both controls held. Exit 2 = cannot check. There is no
failure exit: this reports, it does not gate.
"""
import pathlib
import re
import subprocess
import sys

# assembled, never written out whole -- see the module docstring
ROOT = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))
SELF = pathlib.Path(__file__).resolve()
REPO = SELF.parents[3]

POSITIVE_CONTROLS = ("nd-unfolding/adopt_unified_5d.py",
                     "nd-unfolding/unfold_nd_omnifold_unbinned.py")

INSERT0 = re.compile(r"sys\.path\.insert\(\s*0\s*,\s*([^)]*(?:\([^)]*\))?[^)]*)\)")


def rooted_names(src: str) -> set[str]:
    """Local names that end up holding a path under ROOT, via assignment OR loop binding."""
    esc = re.escape(ROOT)
    names = set(re.findall(r"^\s*(\w+)\s*=\s*f?[\"'][^\"']*" + esc, src, re.M))
    for _ in range(4):
        before = set(names)
        for m in re.finditer(r"for\s+(\w+)\s+in\s+([\(\[][^\)\]]*[\)\]])", src):
            body = m.group(2)
            if ROOT in body or any(re.search(rf"\b{re.escape(v)}\b", body) for v in names):
                names.add(m.group(1))
        for v in list(names):
            V = re.escape(v)
            names |= set(re.findall(r"^\s*(\w+)\s*=\s*f[\"'][^\"']*\{" + V + r"\}", src, re.M))
            names |= set(re.findall(r"^\s*(\w+)\s*=\s*[^=\n]*\b" + V + r"\b", src, re.M))
        if names == before:
            break
    return names


def main() -> int:
    found = subprocess.run(["grep", "-rl", "--include=*.py", ROOT, "."],
                           capture_output=True, text=True, cwd=REPO).stdout.split()
    candidates = [f for f in found if pathlib.Path(REPO / f).resolve() != SELF]
    if not candidates:
        print("CANNOT CHECK :: the discoverer matched no .py file at all; a zero here is a "
              "broken search, never a clean tree")
        return 2

    failopen, unrelated, noinsert = [], [], []
    for rel in candidates:
        src = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        args = INSERT0.findall(src)
        if not args:
            noinsert.append(rel)
            continue
        names = rooted_names(src)
        if any(ROOT in a or any(re.search(rf"\b{re.escape(v)}\b", a) for v in names) for a in args):
            failopen.append(rel)
        else:
            unrelated.append(rel)

    print(f"  [{len(candidates)} .py contain the hardcoded root; "
          f"{len(failopen)} FAIL-OPEN, {len(unrelated)} insert-but-not-rooted, "
          f"{len(noinsert)} no insert(0,...)]")

    missing = [c for c in POSITIVE_CONTROLS
               if not any(f.endswith(c) for f in failopen)]
    if missing:
        print(f"CANNOT CHECK :: positive control(s) absent from the fail-open set: {missing}. "
              f"The classifier under-counts, so the smaller number is not the answer.")
        return 2
    if not unrelated:
        print("CANNOT CHECK :: nothing was rejected, so this classifier has not been shown to "
              "discriminate; every insert(0,...) would look rooted")
        return 2

    print(f"  positive controls IN the set: {list(POSITIVE_CONTROLS)}")
    print(f"  negative control -- rejected {len(unrelated)}, e.g. {unrelated[:3]}")
    print("FAIL-OPEN SET:")
    for rel in sorted(failopen):
        print(f"    {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

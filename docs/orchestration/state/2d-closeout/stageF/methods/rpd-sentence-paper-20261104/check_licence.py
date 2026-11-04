#!/usr/bin/env python3
"""Check the RPD-sentence round against FD-RPD-DECLARATION.md sec. 6, the licence the round's text must stay inside.

  1. the declaration's sec. 6.2 CLUSTERED sentence, read from the declaration itself, prints verbatim in paper_body.tex
     straight after the bootstrap-scatter sentence, and in sec_fived16.tex straight after its counterpart;
  2. the sentences the round adds (printed, comment-stripped; in the worktree and not at the base) use none of sec. 6.4's
     barred words: "validated", "covers", "coverage", "which period is correct";
  3. the clauses decision item 1 keeps still print in the paper: "The cause is not known", "which period is correct",
     "poorly determined" and the interval keys.
usage: check_licence.py <worktree> [--base SHA]   (exit 1 on any failure)
       check_licence.py <worktree> --self-test    (each planted defect must be caught)"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("round_ledger", HERE / "check_ledger.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
cl = rl.cl
DECL = "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION.md"
NOTE = "docs/analysis-note"
BARRED = re.compile(r"validated|\bcovers\b|coverage|which period is correct", re.I)
AFTER = {"paper_body.tex": "differ by more than their bootstrap scatter.",
         "sec_fived16.tex": "differ from one another by more than the scatter of their bootstrap replicas."}
# the paper's sentence carries the note pointer before its full stop (decision item 1)
POINTER = {"paper_body.tex": r" (\nsec{sec:fived16-pl})", "sec_fived16.tex": ""}
KEPT = ["The cause is not known, and these data cannot establish which period is correct.",
        "with three groups its size is poorly determined",
        r"\fvval{pl-sigratio-lo}--\fvval{pl-sigratio-hi}"]


def licensed(decl):
    """Sec. 6.2's CLUSTERED row: the one quoted sentence it licenses."""
    row = [l for l in decl.splitlines() if l.startswith("| **CLUSTERED** |")]
    assert len(row) == 1, "the declaration's CLUSTERED row is not unique"
    q = re.findall(r'"([^"]+)"', row[0])
    assert len(q) == 1, f"the CLUSTERED row quotes {len(q)} sentences"
    return q[0]


def check(decl, cur, old):
    fails = []
    lic = licensed(decl)
    for f, a in AFTER.items():
        want = a + " " + lic[:-1] + POINTER[f] + "."
        n = cur[f].count(want)
        if n != 1:
            fails.append(f"{f}: the licensed sentence follows {a[:40]!r} {n} times, not once")
    for f in AFTER:
        base = set(cl.sentences(old[f]))
        for s in cl.sentences(cur[f]):
            if s not in base and BARRED.search(s):
                fails.append(f"{f}: an added sentence uses a barred word: {s[:100]!r}")
    for k in KEPT:
        if k not in cur["paper_body.tex"]:
            fails.append(f"paper_body.tex: a kept clause no longer prints: {k!r}")
    return fails


def load(wt, base):
    cur = {f: cl.printed((Path(wt) / NOTE / f).read_text()) for f in AFTER}
    old = {f: cl.printed(cl.git_show(wt, base, f"{NOTE}/{f}")) for f in AFTER}
    return (Path(wt) / DECL).read_text(), cur, old


def self_test(wt, base):
    decl, cur, old = load(wt, base)
    assert not check(decl, cur, old), "the worktree must pass before planting"
    lic = licensed(decl)
    plants = {
        "reworded": lambda c: {**c, "paper_body.tex": c["paper_body.tex"].replace(lic[:-1], lic[:-1].replace("would give", "gives"))},
        "pointer dropped": lambda c: {**c, "paper_body.tex": c["paper_body.tex"].replace(r" (\nsec{sec:fived16-pl}).", ".", 1)},
        "note sentence missing": lambda c: {**c, "sec_fived16.tex": c["sec_fived16.tex"].replace(lic + " ", "", 1)},
        "barred word added": lambda c: {**c, "sec_fived16.tex": c["sec_fived16.tex"].replace(
            "None of these readings identifies a cause.", "None of these readings is validated.")},
        "coverage added": lambda c: {**c, "paper_body.tex": c["paper_body.tex"] + " The block's coverage holds."},
        "kept clause dropped": lambda c: {**c, "paper_body.tex": c["paper_body.tex"].replace("The cause is not known, and ", "")},
    }
    missed = [k for k, f in plants.items() if not check(decl, f(dict(cur)), old)]
    # a barred word already at the base is not the round's: an unchanged sentence must not fail
    assert not check(decl, cur, old)
    print(f"check_licence self-test: {len(plants) - len(missed)}/{len(plants)} planted defects caught" +
          (f"; MISSED {missed}" if missed else ""))
    return 1 if missed else 0


def main(argv):
    wt = argv[0]
    base = argv[argv.index("--base") + 1] if "--base" in argv else rl.BASE
    if "--self-test" in argv:
        return self_test(wt, base)
    fails = check(*load(wt, base))
    for x in fails:
        print("FAIL", x)
    print(f"check_licence: {'PASS' if not fails else 'FAIL'} (licensed sentence from {DECL.split('/')[-1]} sec. 6.2; "
          f"{len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

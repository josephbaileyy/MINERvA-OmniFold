#!/usr/bin/env python3
"""Check the RPD-sentence round against FD-RPD-DECLARATION.md sec. 6, the licence the round's text must stay inside.

  1. the sentence Joseph ruled on #753 ("Merge, reword sentence"; DECISION below) prints exactly in paper_body.tex,
     straight after the bootstrap-scatter sentence and with the note pointer, and in sec_fived16.tex straight after its
     counterpart. The ruling is a declared departure from the declaration's sec. 6.2 CLUSTERED sentence: that sentence
     is read from the declaration itself, the one recorded phrase swap (DEPARTURE) is applied, and the result must be
     the ruled sentence; the declaration's literal text must no longer print. The decision record must exist and quote
     the ruled sentence;
  2. the sentences the round adds (printed, comment-stripped; in the worktree and not at the base) use none of sec. 6.4's
     barred words: "validated", "covers", "coverage", "which period is correct"; nor "beam-intensity", which #753's
     PRD-referee read found to imply a mechanism (edit 2, adopted: the era grouping is named in the source comment only);
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
BARRED = re.compile(r"validated|\bcovers\b|coverage|which period is correct|beam[- ]intensity", re.I)
AFTER = {"paper_body.tex": "differ by more than their bootstrap scatter.",
         "sec_fived16.tex": "differ from one another by more than the scatter of their bootstrap replicas."}
# the paper's sentence carries the note pointer before its full stop (decision item 1)
POINTER = {"paper_body.tex": r" (\nsec{sec:fived16-pl})", "sec_fived16.tex": ""}
# Joseph's ruling on #753 ("Merge, reword sentence"; sha256 of the text plus a final newline begins 555da20e9ef2a1cd),
# recorded in DECISION: the reworded sentence, the same meaning as sec. 6.2's with no claim added, as #753's PRD-referee
# read asked (edit 1)
DECISION = "docs/orchestration/DECISION-20261104-joseph-753-reword-and-merge.md"
DEPARTURE = ("by more than their playlist-to-playlist scatter would give.",
             "by more than expected from their playlist-to-playlist scatter.")
RULED = "The offsets of the twelve playlists differ between the three period groups by more than expected from their playlist-to-playlist scatter."
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


def ruled(decl):
    """Sec. 6.2's sentence with the ruling's one phrase swap applied; it must be the ruled sentence exactly."""
    lic = licensed(decl)
    assert lic.count(DEPARTURE[0]) == 1, "the declaration's sentence no longer holds the departed phrase"
    out = lic.replace(*DEPARTURE)
    assert out == RULED, f"the departure applied to sec. 6.2 gives {out!r}, not the ruled sentence"
    return out


def check(decl, cur, old, record):
    fails = []
    lic, new = licensed(decl), ruled(decl)
    for f, a in AFTER.items():
        want = a + " " + new[:-1] + POINTER[f] + "."
        n = cur[f].count(want)
        if n != 1:
            fails.append(f"{f}: the ruled sentence follows {a[:40]!r} {n} times, not once")
        if lic[:-1] in cur[f]:
            fails.append(f"{f}: sec. 6.2's literal sentence still prints; the ruling replaced it")
    if record is None:
        fails.append(f"the decision record {DECISION} does not exist")
    elif RULED not in re.sub(r"\s+", " ", record):
        fails.append(f"the decision record {DECISION} does not quote the ruled sentence")
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
    rec = Path(wt) / DECISION
    return (Path(wt) / DECL).read_text(), cur, old, rec.read_text() if rec.exists() else None


def self_test(wt, base):
    decl, cur, old, rec = load(wt, base)
    assert not check(decl, cur, old, rec), "the worktree must pass before planting"
    lic, new = licensed(decl), ruled(decl)
    plants = {
        "reworded again": lambda c: {**c, "paper_body.tex": c["paper_body.tex"].replace(new[:-1], new[:-1].replace("expected from", "predicted by"))},
        "literal restored in the note": lambda c: {**c, "sec_fived16.tex": c["sec_fived16.tex"].replace(new, lic, 1)},
        "pointer dropped": lambda c: {**c, "paper_body.tex": c["paper_body.tex"].replace(r" (\nsec{sec:fived16-pl}).", ".", 1)},
        "note sentence missing": lambda c: {**c, "sec_fived16.tex": c["sec_fived16.tex"].replace(new + " ", "", 1)},
        "barred word added": lambda c: {**c, "sec_fived16.tex": c["sec_fived16.tex"].replace(
            "None of these readings identifies a cause.", "None of these readings is validated.")},
        "era named by intensity": lambda c: {**c, "sec_fived16.tex": c["sec_fived16.tex"].replace(
            "an alternative chronological division", "a beam-intensity division")},
        "coverage added": lambda c: {**c, "paper_body.tex": c["paper_body.tex"] + " The block's coverage holds."},
        "kept clause dropped": lambda c: {**c, "paper_body.tex": c["paper_body.tex"].replace("The cause is not known, and ", "")},
    }
    missed = [k for k, f in plants.items() if not check(decl, f(dict(cur)), old, rec)]
    # the record: absent, or not quoting the ruled sentence
    missed += [k for k, r in {"record absent": None, "record without the sentence": "Merge, reword sentence"}.items()
               if not check(decl, cur, old, r)]
    n = len(plants) + 2
    # a barred word already at the base is not the round's: an unchanged sentence must not fail
    assert not check(decl, cur, old, rec)
    print(f"check_licence self-test: {n - len(missed)}/{n} planted defects caught" +
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
    print(f"check_licence: {'PASS' if not fails else 'FAIL'} (sec. 6.2 of {DECL.split('/')[-1]} with the departure "
          f"of {DECISION.split('/')[-1]}; "
          f"{len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

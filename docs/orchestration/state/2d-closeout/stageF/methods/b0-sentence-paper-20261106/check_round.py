#!/usr/bin/env python3
"""Check the B0-sentence round against DECISION-20261106-joseph-b0-reconciliation-sentence.md.

  1. paper IV F prints the approved three sentences exactly once, straight after the data-stability sentence. The
     approved text is read from b0-reconciliation-20261105/DRAFT.md's quoted block, and the paper's LaTeX is rendered
     to that plain form (RENDER) before they are compared, so the paper cannot drift from what Joseph approved;
  2. main_paper.tex is byte-identical to its base;
  3. the printed paper gains no numeral beyond NEW_NUMERALS, each with its source;
  4. the note's two counterparts print once (NOTE).
usage: check_round.py <worktree> [--base SHA]   (exit 1 on any failure)
       check_round.py <worktree> --self-test    (each planted defect must be caught by its intended check)"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("round_ledger", HERE / "check_ledger.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
cl = rl.cl
NOTE_DIR = "docs/analysis-note"
DRAFT = HERE.parent / "b0-reconciliation-20261105" / "DRAFT.md"
AFTER = ("so the estimator fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical "
         "standard deviations.")
# the paper's LaTeX for the approved sentence, rendered to the draft's plain text
RENDER = [(r"Sec.~\ref{sec:cov16}", "Sec. IV A"), (r"\SI{37}{\percent}", "37%"), (r"$(\Eavail,W)$", "(E_avail, W)"),
          (r"Ref.~\cite{AnalysisNote2026}", "Ref. [14]")]
NEW_NUMERALS = {"153": "B0-4: s5e assess_receipt.json functional_names (153)",
                "37": "B0-3: VL155, KI-80; the note's sec_5d.tex"}
NOTE = {"sec_fived16.tex": "$C_{\\mathrm{e}}$ sums the statistical bootstrap of configuration~(e), 50 replicas, each of "
                           "which refits the whole unfolding with its own rounding-level perturbation of the inputs;",
        "sec_5d.tex": "A declared probe on simulated pseudo-data of two-fold cross-fitting and of two tree "
                      "regularisations found no variant that met the data-stability requirement, so the estimator is "
                      "unchanged."}
FILES = ["paper_body.tex", "main_paper.tex", "sec_fived16.tex", "sec_5d.tex"]


def approved(draft):
    """The draft's quoted block, joined into one line, without its comment lines."""
    q = [l[2:] for l in draft.splitlines() if l.startswith("> ") and not l.startswith("> <!--")]
    return re.sub(r"\s+", " ", " ".join(q)).strip()


def render(t):
    for a, b in RENDER:
        t = t.replace(a, b)
    return t


def numerals(t):
    t = re.sub(r"\\(fvval|ref\*?|nsec|napp|cite|label|eqref|includegraphics|fvpending)(\[[^]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\SI\{([0-9.]+)e([-0-9]+)\}", r" \1e\2 ", t)
    return set(re.findall(r"\d+\.\d+e-?\d+|\d+(?:\.\d+)?", t))


def check(cur, old, draft):
    fails = []
    pr = {f: cl.printed(cur[f]) for f in cur}
    want = approved(draft)
    if not want.startswith("The training-seed block of Sec. IV A is zero") or not want.endswith("unchanged (Ref. [14])."):
        fails.append("DRAFT.md's quoted block is not the approved three sentences")
    i = pr["paper_body.tex"].find(AFTER)
    got = render(pr["paper_body.tex"][i + len(AFTER):].lstrip()) if i >= 0 else ""
    if i < 0 or not got.startswith(want):
        fails.append("paper IV F does not print the approved sentences straight after the data-stability sentence")
    if render(pr["paper_body.tex"]).count(want) != 1:
        fails.append("the approved sentences do not print exactly once in paper_body.tex")
    if cur["main_paper.tex"] != old["main_paper.tex"]:
        fails.append("main_paper.tex differs from its base")
    new = numerals(pr["paper_body.tex"]) - numerals(cl.printed(old["paper_body.tex"]) + " " +
                                                    cl.printed(old["main_paper.tex"])) - set(NEW_NUMERALS)
    if new:
        fails.append(f"paper_body.tex: numerals the base does not print and NEW_NUMERALS does not declare: {sorted(new)}")
    for f, s in NOTE.items():
        if pr[f].count(s) != 1:
            fails.append(f"{f}: the counterpart prints {pr[f].count(s)} times, not once")
    return fails


def load(wt, base):
    cur = {f: (Path(wt) / NOTE_DIR / f).read_text() for f in FILES}
    old = {f: cl.git_show(wt, base, f"{NOTE_DIR}/{f}") for f in FILES}
    return cur, old, DRAFT.read_text()


def self_test(wt, base):
    cur, old, draft = load(wt, base)
    assert not check(cur, old, draft), "the worktree must pass before planting"
    pb = "paper_body.tex"
    plants = {
        "a word changed": (lambda c, d: ({**c, pb: c[pb].replace("not the typical one", "not a typical one", 1)}, d),
                           "does not print the approved sentences"),
        "the draft changed": (lambda c, d: (c, d.replace("not the typical one", "not a typical one", 1)),
                              "does not print the approved sentences"),
        "sentence moved": (lambda c, d: ({**c, pb: c[pb].replace(AFTER + " The training-seed", AFTER + " X. The training-seed",
                                                                 1)}, d), "straight after"),
        "abstract touched": (lambda c, d: ({**c, "main_paper.tex": c["main_paper.tex"] + "%\n"}, d),
                             "main_paper.tex differs"),
        "a new number": (lambda c, d: ({**c, pb: c[pb].replace("not the typical one", "not the typical one (9973)", 1)}, d),
                         "['9973']"),
        "note counterpart dropped": (lambda c, d: ({**c, "sec_5d.tex": c["sec_5d.tex"].replace(NOTE["sec_5d.tex"], "", 1)},
                                                   d), "sec_5d.tex: the counterpart"),
    }
    missed = []
    for k, (f, msg) in plants.items():
        c, d = f(dict(cur), draft)
        if not any(msg in x for x in check(c, old, d)):
            missed.append(k)
    n = len(plants)
    print(f"check_round self-test: {n - len(missed)}/{n} planted defects caught" + (f"; MISSED {missed}" if missed else ""))
    return 1 if missed else 0


def main(argv):
    wt = argv[0]
    base = argv[argv.index("--base") + 1] if "--base" in argv else rl.BASE
    if "--self-test" in argv:
        return self_test(wt, base)
    fails = check(*load(wt, base))
    for x in fails:
        print("FAIL", x)
    print(f"check_round: {'PASS' if not fails else 'FAIL'} (base {base}; the approved B0 sentences against "
          f"{DRAFT.parent.name}/DRAFT.md; {len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

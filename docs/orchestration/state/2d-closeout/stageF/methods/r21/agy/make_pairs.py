"""Build agy's pairs for r21: each section of the paper body, BEFORE (the base, main 78df7327) against AFTER (the tree),
both as printed source (comments removed), with a control copy that plants one strengthening per pair.

usage: python3 -I make_pairs.py <worktree> <outdir>"""
import re
import subprocess
import sys
from pathlib import Path

W, O = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "note-n4"))
from check_ledger import printed  # noqa: E402

old = printed(subprocess.run(["git", "-C", str(W), "show", "78df7327:docs/analysis-note/paper_body.tex"],
                             capture_output=True, text=True, check=True).stdout)
new = printed((W / "docs/analysis-note/paper_body.tex").read_text())
HEADS = ["\\section{Introduction}", "\\section{Data, simulation, and observables}", "\\section{Cross-section extraction}",
         "\\section{Uncertainties and validation}", "\\section{The sixteen-cell cross section}",
         "\\section{Discussion and conclusions}"]


def cut(t):
    idx = [t.index(h) for h in HEADS] + [len(t)]
    return [t[idx[k]:idx[k + 1]].strip() for k in range(len(HEADS))]


# One strengthening per section, each a phrase that must occur in AFTER (asserted).
PLANT = [("Interval coverage has not been validated.", "Interval coverage has been validated."),
         ("in the form of pre-selected analysis ntuples", "in the form of every analysis ntuple MINERvA has produced, pre-selected"),
         ("the same estimator's envelope alone does not exceed it", "the same estimator's envelope alone always exceeds it"),
         ("These tests provide partial evidence and are not independent.", "These tests provide complete and independent evidence."),
         ("Quantitative comparisons need the full covariance", "Quantitative comparisons need only the diagonal uncertainties"),
         ("They are not physical exclusions of the generators", "They are physical exclusions of the generators")]
NOTE = ("(Each pair is one section of a physics paper. AFTER rewrites BEFORE for style: the same facts, numbers, "
        "qualifiers, limitations, citations and cross-references are meant to print, in new sentences and a new order "
        "within each section. Macros such as \\fvval{...} print numbers. Judge whether AFTER states anything more "
        "strongly or more broadly than BEFORE, drops a fact, qualifier or limitation that BEFORE states, or reads in a "
        "way that could mislead. A change of wording or order alone is not a difference.)")
O.mkdir(parents=True, exist_ok=True)
bs, ns = cut(old), cut(new)
for name, plant in (("pairs.txt", False), ("pairs-control.txt", True)):
    out = []
    for k, (b, a) in enumerate(zip(bs, ns), 1):
        if plant:
            o, n = PLANT[k - 1]
            assert o in a, (k, o)
            a = a.replace(o, n, 1)
        out.append(f"Q{k}.\nBEFORE (Sec. {k} of the paper, accepted as correct): {b}\nAFTER: {a}\n")
    (O / name).write_text(NOTE + "\n\n" + "\n".join(out), encoding="utf-8")
print("pairs written: 6; words before/after:", len(old.split()), len(new.split()))

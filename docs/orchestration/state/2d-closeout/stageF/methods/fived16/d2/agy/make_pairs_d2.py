"""Build agy's pairs for the d2 text as it prints (nothing retyped):
Q1 the paper abstract (PB), Q2 the note abstract (NA), Q3 O3's qualified sentence, Q4 IV H's R11 sentence, Q5 the title.

usage: python3 -I make_pairs_d2.py <worktree> <base-rev> <outdir>

BEFORE is what the AFTER must not exceed:
- for the abstracts, the abstract as it printed at <base-rev> (which d2 cut by whole sentences);
- for O3, the note's own sentences on the residual (sec_5d.tex);
- for R11, the review's |b|/sigma values at that cell, from c1a/REPORT.md;
- for the title, the paper abstract's first sentence.

The control copy plants one strengthening per pair."""
import re
import subprocess
import sys
from pathlib import Path

W, BASE, O = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
F = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "final-draft"))
import texplain as X  # noqa: E402

X.init(W)


def abstract_at(rev, name, doc):
    t = subprocess.run(["git", "-C", str(W), "show", f"{rev}:docs/analysis-note/{name}"], capture_output=True,
                       text=True, check=True).stdout
    t = re.sub(r"\s+", " ", "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.splitlines()))
    return X.plain(t.split("\\begin{abstract}")[1].split("\\end{abstract}")[0], doc)


def now(name, doc):
    return X.plain(X.src(name).split("\\begin{abstract}")[1].split("\\end{abstract}")[0], doc)


sys.path.insert(0, str(F / "d2"))
import options as OP  # noqa: E402
o3_note = ("The paper, before d2: " + X.plain(OP.O3["K"], "paper") + " The note: "
           + X.grab("sec_summary.tex", "No uncertainty quoted for the configuration-(a) central value includes this residual bias",
                    "(\\S\\ref{sec:val-departure}).", "note")
           + " " + X.grab("sec_5d.tex", "This persistence holds over a finite scan", "every possible classifier.", "note")
           + " " + X.grab("sec_5d.tex", "No single cause is established,", "GiBUU-to-GENIE departure.", "note"))
o3_now = X.grab("paper_body.tex", "We interpret the residual as regularization bias,", "no single cause is established.", "paper")
r11_now = X.grab("paper_body.tex", "In cell R11 at", "included.", "paper")
rep = (F / "c1a/REPORT.md").read_text()
r11_facts = re.search(r"\*\*The reviewer's observation, for Joseph:\*\*(.*?alone\.)", rep, re.S).group(1)   # the measured part only
title = X.plain(re.search(r"\\title\{(.*?)\}\n", (X.A / "main_paper.tex").read_text()).group(1), "paper")
PAIRS = [
    ("the paper abstract, before d2 (accepted as correct)", abstract_at(BASE, "main_paper.tex", "paper"), now("main_paper.tex", "paper"),
     ("reported in sixteen cells with a covariance", "reported in sixteen cells with a validated covariance")),
    ("the note abstract, before d2 (accepted as correct)", abstract_at(BASE, "main_note.tex", "note"), now("main_note.tex", "note"),
     ("has not been validated;", "has been validated;")),
    ("the paper's sentence before d2 and the companion note's statements on the residual (accepted as correct)", o3_note, o3_now,
     ("although no single cause is established", "and this cause is established")),
    ("the study's measured ratios at that cell (accepted as correct): " + re.sub(r"\s+", " ", r11_facts).strip(), "", r11_now,
     ("only with $C_{\\mathrm{model}}$ included", "even without C_model")),
    ("the paper's opening sentence (accepted as correct)", X.plain(X.src("main_paper.tex").split("\\begin{abstract}")[1].split(". ")[0], "paper") + ".", title,
     ("in five observables", "in all observables")),
]
NOTE = ("(For Q1 and Q2, AFTER is BEFORE with whole sentences removed by design: do not flag a removal as such. Judge "
        "whether what AFTER keeps states anything more strongly or more broadly than BEFORE, or reads in a way that "
        "could mislead once the removed sentences are gone. For Q5, AFTER is the paper's title.)")
O.mkdir(parents=True, exist_ok=True)
for name, plant in (("pairs.txt", False), ("pairs-control.txt", True)):
    out = []
    for n, (what, before, after, pl) in enumerate(PAIRS, 1):
        if plant:
            old, new = pl
            src_after = after if old in after else None
            assert src_after is not None or old.startswith("only with"), (n, old)
            after = after.replace(old, new) if old in after else after.replace("only with C_model included", new)
            assert after != (PAIRS[n - 1][2]), f"Q{n}: the plant did not apply"
        out.append(f"Q{n}.\nBEFORE ({what}): {before}\nAFTER: {after}\n")
    (O / name).write_text(NOTE + "\n\n" + "\n".join(out), encoding="utf-8")
print("pairs written:", len(PAIRS), "pairs; control plants in each")

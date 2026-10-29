"""Build agy's pairs for batch C from apply_n4.C and the sources (nothing retyped), and a control copy with one
strengthening planted per pair.

usage: python3 -I make_pairs_c.py <worktree> <base-rev> <outdir>

BEFORE is the sentence at <base-rev>, plus the context that the AFTER's wording rests on, read from the files:
- the note's own definition (sec_5d.tex sec:val-fiveaxis, "Coverage asks ...") for C1-C7;
- the record row behind C1-C3, the PET record lines behind C5-C6, and the cited paper's title behind C7;
- the note abstract's first sentence and the paper's Conclusions sentence behind M1-M2."""
import re
import subprocess
import sys
from pathlib import Path

W, BASE, O = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
N4 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(N4))
import apply_n4  # noqa: E402
from check_ledger import printed, sentences  # noqa: E402


def show(rev, path):
    return subprocess.run(["git", "-C", str(W), "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout


def sentence_with(text, frag):
    hits = [s for s in sentences(printed(text)) if frag in s]
    assert len(hits) == 1, (frag, len(hits))
    return hits[0]


A = "docs/analysis-note/"
n1 = sentence_with(show(BASE, A + "sec_5d.tex"), "Coverage asks whether the resulting intervals")
a2 = next(l for l in (W / "docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md").read_text().splitlines()
          if l.startswith("| A2: calibration"))
pet = (W / "nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md").read_text().splitlines()
pet_ctx = " ".join(re.sub(r"\s+", " ", pet[i - 1])[:600] for i in (47, 49))
assert "coverage rule" in pet_ctx and "C1" in pet_ctx, "the PET record lines moved"
bib = (W / A / "technote.bib").read_text()
title = re.search(r"@article\{Stanley:2025functionals,.*?title\s*=\s*\{\{(.*?)\}\}", bib, re.S).group(1)
title = re.sub(r"\s+", " ", title)
abst = printed(show(BASE, A + "main_note.tex").split("\\begin{abstract}")[1].split("\\end{abstract}")[0])
abst1 = abst.split(". ")[0] + "."
concl = sentence_with(show(BASE, A + "paper_body.tex"), "The principal result is the sixteen-cell")
CTX = {
    "C1": f"The note defines: \"{n1}\" The record of the test: {a2}",
    "C5": f"The PET campaign record: {pet_ctx}",
    "C7": f"The cited paper's title: \"{title}\".",
    "M1": f"The note's abstract opens: \"{abst1}\" The companion paper's Conclusions: \"{concl}\"",
}
CTX["C2"] = CTX["C3"] = CTX["C1"]
CTX["C4"] = f"The note defines: \"{n1}\""
CTX["C6"] = CTX["C5"]
CTX["M2"] = CTX["M1"]
PLANT = {"C1": ("a pooled test of its", "a per-functional coverage test of its"),
         "C2": ("does not establish coverage and width for every functional", "establishes coverage and width for every functional"),
         "C3": ("cannot qualify this cell", "qualifies this cell"),
         "C4": ("checks neither the coverage and width of the intervals nor", "checks the coverage and width of the intervals but not"),
         "C5": ("fails the frozen coverage rule", "fails the frozen coverage rule in every region"),
         "C6": ("failed the frozen coverage rule", "failed every frozen rule"),
         "C7": ("constructs confidence intervals", "constructs exact, assumption-free confidence intervals"),
         "M1": ("The principal result is", "The only result is"),
         "M2": ("The principal result is", "The only result is")}
base_text = {}
pairs = []
for eid, f, old, new in apply_n4.C:
    t = base_text.setdefault(f, show(BASE, A + f))
    frag = printed(old).split(". ")[0]
    before = " ".join(s for s in sentences(printed(t)) if any(x in s for x in re.split(r"(?<=\.) ", printed(old)) if len(x) > 20))
    after = printed(t.replace(old, new))
    after = " ".join(s for s in sentences(after) if any(x in s for x in re.split(r"(?<=\.) ", printed(new)) if len(x) > 20))
    assert before and after and before != after, eid
    pairs.append((eid, before, after))
NOTE = ("(Each pair is one sentence of a physics analysis note, BEFORE and AFTER a terminology fix. The CONTEXT gives "
        "the definitions and records the AFTER's wording rests on; it is accepted as correct. Judge AFTER against "
        "BEFORE read with its CONTEXT.)")
O.mkdir(parents=True, exist_ok=True)
for name, plant in (("pairs.txt", False), ("pairs-control.txt", True)):
    out = []
    for n, (eid, before, after) in enumerate(pairs, 1):
        if plant:
            old, new = PLANT[eid]
            assert old in after, (eid, old)
            after = after.replace(old, new, 1)
        out.append(f"Q{n}.\nCONTEXT: {CTX[eid]}\nBEFORE: {before}\nAFTER: {after}\n")
    (O / name).write_text(NOTE + "\n\n" + "\n".join(out), encoding="utf-8")
(O / "KEY.txt").write_text("\n".join(f"Q{n}\t{eid}" for n, (eid, _, _) in enumerate(pairs, 1)) + "\n")
print("pairs written:", len(pairs), "; control plants in each")

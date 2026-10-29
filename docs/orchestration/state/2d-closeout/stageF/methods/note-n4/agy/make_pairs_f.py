"""Build agy's pairs for batch F (the front-matter fold) from the sources (nothing retyped), and a control copy with
one strengthening planted per pair.

usage: python3 -I make_pairs_f.py <worktree> <base-rev> <outdir>

Q1 the executive summary; Q2 the summary section; Q3 the introduction's strategy and scope paragraphs; Q4 the three
body sentences the fold added (the tension subsection, the sixteen-cell fake-data subsection, the Valencia citation).
BEFORE is the printed source at <base-rev> (for Q1, with the deleted status table's rows); AFTER is the tree's."""
import re
import subprocess
import sys
from pathlib import Path

W, BASE, O = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_ledger import printed, sentences  # noqa: E402

A = "docs/analysis-note/"


def show(rev, f):
    return subprocess.run(["git", "-C", str(W), "show", f"{rev}:{A}{f}"], capture_output=True, text=True, check=True).stdout


def cur(f):
    return (W / A / f).read_text()


def para(text, start, stop=None):
    t = printed(text)
    i = t.index(start)
    j = t.index(stop, i) if stop else len(t)
    return t[i:j].strip()


def sents_with(text, frags):
    ss = sentences(printed(text))
    out = []
    for fr in frags:
        hit = [s for s in ss if fr in s]
        assert len(hit) == 1, (fr, len(hit))
        out.append(hit[0])
    return " ".join(out)


es_old = para(show(BASE, "sec_execsummary.tex"), "We apply") + " STATUS TABLE ROWS: " + para(show(BASE, "result_status_rows.tex"), "\\rsA{Result")
es_new = para(cur("sec_execsummary.tex"), "We apply")
su_old = para(show(BASE, "sec_summary.tex"), "\\paragraph{Summary.}", "\\paragraph{Outlook.}")
su_new = para(cur("sec_summary.tex"), "\\paragraph{Summary.}", "\\paragraph{Outlook.}")
in_old = para(show(BASE, "sec_intro.tex"), "\\paragraph{Analysis strategy.}", "\\begin{center}")
in_new = para(cur("sec_intro.tex"), "\\paragraph{Analysis strategy.}")
adds_frag = ["methodological band: the exact-split cross-check gives", "This is a bias test, not a coverage test",
             "The Nieves--Simo--Vacas MEC channel"]
b4_old = " ".join(sents_with(show(BASE, f), [fr]) for f, fr in zip(["sec_results.tex", "sec_fived16.tex", "sec_3d.tex"], adds_frag))
b4_new = " ".join([sents_with(cur("sec_results.tex"), [adds_frag[0], "Beyond this methodological band"]),
                   sents_with(cur("sec_fived16.tex"), [adds_frag[1], "The coverage of the result's intervals has not been validated."]),
                   sents_with(cur("sec_3d.tex"), [adds_frag[2]])])
PAIRS = [("the note's executive summary and its status table, before (accepted as correct)", es_old, es_new,
          ("reject all ten under six stated conditions", "reject all ten unconditionally")),
         ("the note's summary section, before (accepted as correct)", su_old, su_new,
          ("largely removes the purity-subtraction bias", "removes all background bias")),
         ("the note's introduction, analysis strategy and scope paragraphs, before (accepted as correct)", in_old, in_new,
          ("The principal limitations are listed in the executive summary", "There are no significant limitations; minor ones are listed in the executive summary")),
         ("three body sentences, before (accepted as correct)", b4_old, b4_new,
          ("has not been validated.", "has been validated."))]
NOTE = ("(The note's front matter was folded by design: the executive summary now gives one headline sentence per "
        "result, each with a pointer to the body section where the result is stated in full, and one list of "
        "limitations as pointers; the summary section keeps only conclusions the executive summary does not state; "
        "the introduction points to the list. A sentence removed because its body section states it is a removal by "
        "design and is not to be flagged as such. Judge whether what AFTER keeps or adds states anything more "
        "strongly or more broadly than BEFORE, or reads in a way that could mislead once the removed sentences are "
        "gone. For Q4, AFTER adds sentences to the body.)")
O.mkdir(parents=True, exist_ok=True)
for name, plant in (("pairs.txt", False), ("pairs-control.txt", True)):
    out = []
    for n, (what, before, after, pl) in enumerate(PAIRS, 1):
        if plant:
            assert after.count(pl[0]) >= 1, (n, pl[0])
            after = after.replace(pl[0], pl[1], 1)
        out.append(f"Q{n}.\nBEFORE ({what}): {before}\nAFTER: {after}\n")
    (O / name).write_text(NOTE + "\n\n" + "\n".join(out), encoding="utf-8")
print("pairs written:", len(PAIRS), "; control plants in each")

"""Build agy's pairs for the four paper protection edits from the sources (nothing retyped), with a control copy that
plants one strengthening per pair.

usage: python3 -I make_pairs.py <worktree> <base-rev> <outdir>

Q1 Sec. I's limitations paragraph; Q2 the Scope paragraph; Q3 the Limitations subsection; Q4 the two body
sentences that lost a duplicate (sec:departure, sec:gen16); Q5 Data Availability. Each CONTEXT is the printed home
text where the facts removed from that passage still print."""
import re
import subprocess
import sys
from pathlib import Path

W, BASE, O = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "note-n4"))
from check_ledger import printed, sentences  # noqa: E402

A = "docs/analysis-note/"


def show(f):
    return subprocess.run(["git", "-C", str(W), "show", f"{BASE}:{A}{f}"], capture_output=True, text=True, check=True).stdout


def cur(f):
    return (W / A / f).read_text()


def line_with(text, frag):
    hit = [l for l in text.splitlines() if frag in l and not l.lstrip().startswith("%")]
    assert len(hit) == 1, (frag, len(hit))
    return printed(hit[0])


def sent(text, frag):
    hit = [s for s in sentences(printed(text)) if frag in s]
    assert len(hit) == 1, (frag, len(hit))
    return hit[0]


pb0, pb1, mp0, mp1 = show("paper_body.tex"), cur("paper_body.tex"), show("main_paper.tex"), cur("main_paper.tex")
dec3 = re.search(r"^3\. \*\*No stability criterion.*?(?=\n\n|\n## )", (W / "docs/orchestration/DECISION-20261024-joseph-h2-16-cell-"
                 "definition.md").read_text(), re.S | re.M).group(0)
dec3 = re.sub(r"\s+", " ", dec3)
home = {
    "fd16": sent(pb1, "the reported uncertainty does not cover the fake-data bias at these GiBUU-like truths"),
    "f1": sent(pb1, "The tests assess bias, not coverage"),
    "f1b": sent(pb1, "Both tunes satisfy the bias criteria"),
    "flux": sent(pb1, "Weakening only the flux correlations by"),
    "cov16": sent(pb1, "is built from the change in the unfolded data when the prior is reweighted to GENIE + MEC"),
    "lim": line_with(pb1, "The limitations of these results are stated with the results they qualify"),
    "rel": "The note's release appendix: \"" + sent(cur("app_release.tex"), "reproduces the joint-test $p$ values") + "\" \""
           + sent(cur("app_release.tex"), "RC7 supports replay of the higher-dimensional inference") + "\"",
}
PAIRS = [
    ("Q1", "Sec. I's paragraph on the result's limitations", line_with(pb0, "The result has three limitations"),
     line_with(pb1, "Interval coverage has not been validated. The bias tests"),
     " ".join([home["f1b"], home["f1"], home["fd16"], home["flux"]]),
     ("are given with the result", "are shown to be negligible")),
    ("Q2", "the Scope paragraph", line_with(pb0, "\\emph{Scope.}"), line_with(pb1, "\\emph{Scope.}"),
     "The Limitations subsection: " + home["lim"],
     ("rather than of multidimensional OmniFold in general", "and of multidimensional OmniFold in general")),
    ("Q3", "the Limitations subsection", line_with(pb0, "The limitations of these results are stated with the results they qualify"),
     home["lim"], "The Scope paragraph before the edit: " + line_with(pb0, "\\emph{Scope.}") + " The decision that adds the "
     "low-stability sentence (DECISION-20261024-joseph-h2-16-cell-definition.md): \"" + dec3 + "\" The values file prints "
     "h2-lowstab-cells = R02, R06, R10 and R15, h2-lowstab-min = 0.16, h2-lowstab-max = 0.25; stability is a cell's fraction "
     "of simulated signal events generated in it and reconstructed that are reconstructed in it (the H2 definition code).",
     ("They are not physical exclusions of the generators", "They exclude the generators")),
    ("Q4", "two body sentences", " ".join([sent(pb0, "For the sixteen-cell result, the model term of its reported covariance"),
                                         sent(pb0, "The reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec.")]),
     sent(pb1, "For the sixteen-cell result, Sec.~\\ref{sec:fd16} reports the fake-data tests"),
     " ".join([home["cov16"], home["fd16"]]),
     ("reports the fake-data tests of the estimator's bias", "shows the estimator to be unbiased")),
    ("Q5", "the Data Availability statement", line_with(mp0, "The input data and simulation are the MINERvA open-data AnaTuples"),
     line_with(mp1, "The input data and simulation are the MINERvA open-data AnaTuples"),
     home["rel"] + " The paper's Sec. central quotes no numbers, and the paper quotes no multiplier scan.",
     ("not yet deposited", "deposited")),
]
NOTE = ("(These are edits to a physics paper that drop duplicate copies of limitations, keeping each at one home, and "
        "shorten a scope paragraph. A sentence removed because its CONTEXT home prints the same fact is a removal by "
        "design and is not to be flagged as such. Judge whether what AFTER keeps or adds states anything more strongly "
        "or more broadly than BEFORE, or reads in a way that could mislead, given that the CONTEXT still prints.)")
O.mkdir(parents=True, exist_ok=True)
for name, plant in (("pairs.txt", False), ("pairs-control.txt", True)):
    out = []
    for qid, what, before, after, ctx, pl in PAIRS:
        if plant:
            assert pl[0] in after, (qid, pl[0])
            after = after.replace(pl[0], pl[1], 1)
        out.append(f"{qid}.\nCONTEXT (where the removed facts print): {ctx}\nBEFORE ({what}, accepted as correct): {before}\nAFTER: {after}\n")
    (O / name).write_text(NOTE + "\n\n" + "\n".join(out), encoding="utf-8")
print("pairs written:", len(PAIRS), "; control plants in each")

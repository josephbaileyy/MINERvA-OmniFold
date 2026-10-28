r"""usage: python3 -I move_pass.py ANALYSIS_NOTE_DIR OUT.tsv -- r19 variant B: candidate note sites for every fact that
leaves the paper (DECISION-20261028-joseph-r19-variant-b-and-moves.md item 3).

The leaving text is:
- Sec. VI (the calibrated tests, from its \section line to the Discussion's);
- the sentences of O1-O6 and of the knock-on edits K1-K14 (r19/outline.md sections 4-5, and the rulings), each named
  below by its verbatim start in paper_body.tex.

The text is split into sentences. For each sentence the script ranks the note's printed sentences (all inputs of
main_note.tex, comments stripped) by the share of the paper sentence's content tokens they contain, and reports any
number or macro token missing from the best one.

This is a finder, not a verdict. The lane reads every row and writes the ledger's N: probes by hand, as verbatim
substrings of the note's printed source. A row with no adequate site goes to the paper-only list."""
import re, sys
from pathlib import Path

D = Path(sys.argv[1]); OUT = sys.argv[2]
strip = lambda t: re.sub(r"(?<!\\)%.*", "", t)
body = (D / "paper_body.tex").read_text(encoding="utf-8").split("\n")

# Sec. VI, whole
s = next(i for i, l in enumerate(body) if l.startswith(r"\section{Simulation-calibrated tests"))
e = next(i for i, l in enumerate(body) if l.startswith(r"\section{Discussion and conclusions"))
VI = " ".join(strip(l) for l in body[s:e] if not l.lstrip().startswith("%"))
# figure and table environments in VI print their captions only (the table body is checked as Table VI below)

ITEMS = [  # (id, verbatim start of the first leaving sentence, number of sentences from there)
    ("O1", "A diagnostic in simulation, summarized in Table~\\ref{tab:binned}", 5),
    ("O1", "The diagnostic is binned, signal-only and noise-free", 4),
    ("O1-T3", "\\caption{Median absolute residual (\\%) over the \\jtNcells{} joint cells", 6),
    ("O3", "These deviations occur with or without background", 2),
    ("O2", "A diagnosis that fits a Gaussian bias and spread", 5),
    ("O4", "The end-to-end test unfolds 400 pseudo-experiments per truth.", 3),
    ("O4-F4", "\\caption{Empirical coverage of statistical intervals for the 153 reported", 8),
    ("O5", "The block supersedes two earlier statistical bands", 1),
    ("O6", "Replacing it by the charged-pion mass", 1),
    ("K1", "Two properties must be distinguished.", 5),
    ("K2", "For GiBUU, whose sample lacks high-energy neutrinos, the domain is", 1),
    ("K3", "The NuWro and GiBUU comparisons contain a target difference of this kind", 1),
    ("K4", "The generator tests are conditional tests of simulated hybrid null hypotheses", 4),
    ("K5", "The three- and four-observable central values, the sixteen-cell five-observable result", 1),
    ("K6", "It motivates the different route to inference of", 1),
    ("K7", "The truths are the simulation's prior; the five hybrid truths", 1),
    ("K8", "The third is the upward displacement of the external nulls", 1),
    ("K9", "The calibrated tests illustrate inference with a biased estimator", 1),
    ("K9", "The generator tests reject hybrid nulls, conditionally on the simulation's hadronic response.", 3),
    ("K11", "As an application, Sec.~\\ref{sec:joint} tests generator predictions", 1),
    ("K12", "Every study uses the analysis simulation's detector response, except the calibration", 1),
    ("K13", "When intervals cannot be validated, tests can still be calibrated", 1),
    ("K14", "Table~\\ref{tab:joint}", 0),  # placeholder: Table VI's rows are checked separately
]
SENT = re.compile(r"(?<=[.?!])\s+(?=[A-Z\\(])")


def sentences(t):
    t = re.sub(r"\s+", " ", t).strip()
    return [x for x in SENT.split(t) if x.strip()]


flat = re.sub(r"\s+", " ", " ".join(strip(l) for l in body if not l.lstrip().startswith("%")))
rows = []
for k, start, n in ITEMS:
    if n == 0:
        continue
    i = flat.find(start)
    if i < 0 or flat.count(start) != 1:
        sys.exit("FAIL: %s start not found exactly once: %r" % (k, start[:60]))
    rows += [(k, x) for x in sentences(flat[i:])[:n]]
rows += [("VI", x) for x in sentences(VI)]
# Table VI rows: each row's numbers must print in the note's decision table
tv = re.search(r"\\label\{tab:joint\}(.*?)\\end\{tabular\}", VI, re.S)
for r in re.findall(r"(?m)([A-Z][^&\\]*?&[^\\]*?)\\\\", tv.group(1)):
    rows.append(("VI-T6", r.strip()))

main = (D / "main_note.tex").read_text(encoding="utf-8")
files = ["main_note.tex"] + [f if f.endswith(".tex") else f + ".tex" for f in re.findall(r"\\(?:input|include)\{([^}]+)\}", main)]
NOTE = []
for f in files:
    for ln, l in enumerate((D / f).read_text(encoding="utf-8").split("\n"), 1):
        t = strip(l)
        if t.strip():
            for x in sentences(t):
                NOTE.append((f, ln, x))

STOP = set("the a an of and or to in on at by for with is are be as that this which its it from than not no".split())
def toks(x):
    x = re.sub(r"\\(ref|nsec|napp|cite)\*?\{[^}]*\}", " ", x)
    return {w for w in re.findall(r"\\[A-Za-z]+|[A-Za-z][A-Za-z\-]+|\d+(?:\.\d+)?", x.lower()) if w not in STOP}
def nums(x):
    x = re.sub(r"\\(ref|nsec|napp|cite|label)\*?\{[^}]*\}", " ", x)
    return set(re.findall(r"\d+(?:\.\d+)?", x)) | set(re.findall(r"\\(?:jt|wone|cov|uq|fv)[A-Za-z]+", x))
NT = [(f, ln, x, toks(x)) for f, ln, x in NOTE]
with open(OUT, "w", encoding="utf-8") as o:
    o.write("item\tscore\tmissing_numbers\tnote_site\tpaper_sentence\tnote_sentence\n")
    for k, x in rows:
        tx, nx = toks(x), nums(x)
        best = max(NT, key=lambda r: (len(tx & r[3]) / max(1, len(tx)), len(nx & nums(r[2]))))
        sc = len(tx & best[3]) / max(1, len(tx))
        miss = sorted(nx - nums(best[2]))
        o.write(f"{k}\t{sc:.2f}\t{' '.join(miss)}\t{best[0]}:{best[1]}\t{x}\t{best[2]}\n")
print("leaving sentences: %d; note sentences searched: %d in %d files; wrote %s" % (len(rows), len(NT), len(files), OUT))

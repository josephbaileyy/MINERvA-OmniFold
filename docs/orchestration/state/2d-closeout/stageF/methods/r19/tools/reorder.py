r"""usage: python3 -I reorder.py PAPER_BODY.tex -- r19 step 0: reorder paper_body.tex into the approved order (variant A).

The outline is r19/outline.md, section 1, approved by the director on 2026-10-27. Blocks move verbatim, with no wording
change. A block is a run of non-blank lines, so a comment block moves with the paragraph it sits against. The script
changes only sectioning lines and marker lines:
- new or renamed \section / \subsection headings;
- the label sec:fd16 added, and sec:limits kept on its own line once its section heading goes;
- a FIVED16-END and a FIVED16-BEGIN added where a FIVED16 block splits, so each piece of a FIVED16 block that moves, because fived16/check_ledger.py rule 7
  forbids a hand-typed numeral between the markers.

It fails unless:
- each block's first line starts as expected, so the base is the one the outline names;
- every block is used exactly once;
- the multiset of all other lines is unchanged;
- the set of labels is the old set plus sec:fd16."""
import collections, re, sys

p = sys.argv[1]
L = open(p, encoding="utf-8").read().split("\n")
C, cur = [], []
for l in L:
    if l.strip():
        cur.append(l)
    elif cur:
        C.append(cur); cur = []
if cur:
    C.append(cur)
if len(C) != 98:
    sys.exit("FAIL: expected 98 blocks, found %d" % len(C))

EXPECT = {  # block -> start of its first non-comment line (the base at 855bf070, paper_body.tex sha256 b79837aa)
    2: r"\section{Introduction and scope}", 10: r"\section{Data, observables, and domains}",
    16: r"\section{Estimators and validation design}", 23: "A closure test measures", 24: r"\section{Two-dimensional benchmark}",
    25: r"\subsection{Comparison with the published measurement}", 29: r"\subsection{Two-dimensional covariance}",
    34: r"\section{Five observables: bias, coverage, and precision}", 35: r"\subsection{Normalization and closure}",
    39: r"\subsection{Generator-sized truth changes}", 41: r"\subsection{Coverage}", 44: r"\begin{figure*}",
    45: r"\begin{figure*}", 46: r"\begin{figure*}", 47: r"\subsection{Estimator stability}",
    51: r"\subsection{Reporting definitions and the precision target}", 54: r"\begin{table}", 55: r"\subsection{A sixteen-cell",
    56: "To compare the estimator's bias", 57: r"\begin{table*}", 58: "Under the reported covariance",
    59: r"\section{What limits the estimator}", 60: "Three results point", 61: "A diagnostic in simulation",
    64: "The studies of Secs.", 65: r"\section{Application: comparison with generator predictions}", 66: "Unfolded results can be compared",
    67: r"\subsection{Descriptive comparison of the central values}", 70: r"\subsection{Comparison on the sixteen reported cells}",
    73: "Weakening only the flux", 74: r"\subsection{Hypotheses and calibration}", 93: "The methodological contribution",
    94: r"\section{Discussion and conclusions}", 95: "The principal result is", 96: r"\subsection{Limitations}",
    97: "The limitations of these results",
}
for k, s in EXPECT.items():
    first = next((l for l in C[k] if not l.lstrip().startswith("%")), C[k][0])
    if not first.startswith(s):
        sys.exit("FAIL: block %d starts %r, expected %r" % (k, first[:60], s))
for k in (48, 49, 63):
    if not all(l.startswith("%") for l in C[k]):
        sys.exit("FAIL: block %d is not a comment block" % k)


def H(level, title, labels):
    return ["\\%s{%s}" % (level, title)] + ["\\label{%s}" % x for x in labels]


def drop(k, *prefixes):
    """Block k without its lines that start with any prefix (sectioning lines only)."""
    out = [l for l in C[k] if not l.startswith(prefixes)]
    assert len(C[k]) - len(out) == len(prefixes), (k, prefixes)
    return out


used = collections.Counter()
NEW = []


def B(*ks):
    for k in ks:
        used[k] += 1
        NEW.append(C[k])


def R(lines, *consumes):  # replacement material, consuming the blocks it replaces
    for k in consumes:
        used[k] += 1
    NEW.append(lines)


FB2 = "% FIVED16-BEGIN (r19 step 0: continued from Sec. III, the fake-data tests of the sixteen-cell result)"
FE = "% FIVED16-END"

B(0, 1)
# I. Introduction
R(H("section", "Introduction", ["sec:intro"]), 2); B(3, 4, 5, 6, 7, 8, 9)
# II. Data, simulation, and observables
R(H("section", "Data, simulation, and observables", ["sec:data"]), 10); B(11, 12, 13, 14, 15)
# III. Cross-section extraction: the estimators, the precision study, the reporting cells
R(H("section", "Cross-section extraction", ["sec:method"]), 16); B(17, 18, 19, 20, 21, 22)
B(51, 52, 53)
R(H("subsection", "Reporting cells", []))
used[55] += 1
NEW.append(drop(55, r"\subsection{A sixteen-cell", r"\label{sec:result16}") + [FE])  # its own BEGIN line stays
# IV. Uncertainties and validation
R(H("section", "Uncertainties and validation", ["sec:validation"]), 34); B(23)
R(H("subsection", "Two-dimensional benchmark", ["sec:repro2d", "sec:repro2d-pub"]), 24, 25); B(26, 27, 28)
B(29, 30, 31, 32, 33)
B(35, 36, 37, 38, 44)
B(39, 40, 45, 61, 62, 63, 54)
B(41, 42, 43, 46)
B(47, 48, 49, 50)
R(H("subsection", "Fake-data tests of the sixteen-cell result", ["sec:fd16"]))
used[56] += 1; NEW.append([FB2] + C[56])
B(57, 58)
# V. The sixteen-cell cross section
R(H("section", "The sixteen-cell cross section", ["sec:result16"]))
B(70, 71, 72, 73)
B(67, 68, 69)
# VI. Simulation-calibrated tests (variant A only)
R(H("section", "Simulation-calibrated tests of generator predictions", ["sec:joint"]), 65); B(66)
B(*range(74, 94))
# VII. Discussion and conclusions
B(94, 95)
used[59] += 1; NEW.append(drop(59, r"\section{What limits the estimator}"))  # the label sec:limits, now on the Discussion
B(60, 64, 96, 97)

bad = [k for k in range(len(C)) if used[k] != 1]
if bad:
    sys.exit("FAIL: blocks used other than once: %s" % {k: used[k] for k in bad})

STRUCT = re.compile(r"^(\\(sub)?section\{|\\label\{[^}]*\}$|% FIVED16-(BEGIN|END))")
def body(lines): return collections.Counter(l for l in lines if l.strip() and not STRUCT.match(l))
out = "\n\n".join("\n".join(b) for b in NEW) + "\n"
old_l, new_l = open(p, encoding="utf-8").read().split("\n"), out.split("\n")
if body(old_l) != body(new_l):
    d1, d2 = body(old_l) - body(new_l), body(new_l) - body(old_l)
    sys.exit("FAIL: non-structural lines changed: lost %s gained %s" % (list(d1)[:3], list(d2)[:3]))
lab = lambda t: collections.Counter(re.findall(r"\\label\{([^}]+)\}", t))
lo, ln = lab("\n".join(old_l)), lab(out)
if ln - lo != collections.Counter(["sec:fd16"]) or lo - ln:
    sys.exit("FAIL: labels changed beyond adding sec:fd16: %s / %s" % (dict(ln - lo), dict(lo - ln)))
missing = [l for l in old_l if l.startswith("% FIVED16-") and l not in new_l]
if missing:
    sys.exit("FAIL: an original FIVED16 marker line is gone: %r" % missing[0][:80])
nb = sum(1 for l in old_l if STRUCT.match(l)), sum(1 for l in new_l if STRUCT.match(l))
open(p, "w", encoding="utf-8").write(out)
print("r19 step 0: %d blocks reordered; non-structural lines unchanged (%d); labels +sec:fd16; structural lines %d -> %d"
      % (len(C), sum(body(new_l).values()), nb[0], nb[1]))

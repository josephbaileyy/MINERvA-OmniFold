"""Round 2 of the PRD read (DECISION-20261027 prd-review-route item 2): the abstracts, further paper wording and the
release scopings. Writes the rater inputs (plain text) and proposals.tsv. No configuration label in an abstract proposal."""
import re
X = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/xmodel/prd5d-r2"
pa = open(f"{X}/paper-abstract.txt").read().strip().replace("threemomentum", "three-momentum").replace("νµ", "ν_μ")
na = open(f"{X}/main_note-abstract-src.txt").read().strip()
for a, b in [(r"\emph{unbinned}", "unbinned"), (r"($\Eavail$)", "(E_avail)"), (r"($q_{3}$)", "(q_3)"), ("($W$)", "(W)"), (r"$\approx$1--2\,\%", "≈1–2 %"),
             (r"$\Eavail$", "E_avail"), ("$W$", "W"), (r"\%", "%"), ("--", "–")]:
    na = na.replace(a, b)
assert "\\" not in na and "$" not in na, re.findall(r"\\\w+|\$", na)[:5]
P = [  # id, where, old (exact, in the rater text), new
 ("A1", "paper abstract", "it yields central values only, whose normalizations agree with lower-dimensional results.",
        "it yields central values whose normalizations agree with lower-dimensional results, and a sixteen-cell cross section with total uncertainties whose coverage is not validated."),
 ("A2", "paper abstract", "no tested reporting definition meets our 10% precision criterion.",
        "none of the reporting definitions tested in a precision study meets our 10% precision criterion."),
 ("N1", "note abstract", "each of which passes marginal-normalization checks against the lower-dimensional result to ≈1–2 %.",
        "whose central values pass marginal-normalization checks against the lower-dimensional result to ≈1–2 %; a sixteen-cell five-observable result is also reported with total uncertainties, whose coverage is not validated."),
 ("N2", "note abstract", "the regularization bias is largest in this region", "the regularization bias measured in the five-dimensional validation is largest in this region"),
 ("N3", "note abstract", "The five-dimensional central value and its covariance use the purity subtraction, and the central value keeps its bias of up to 4% in the highest-W cells, which no quoted uncertainty includes.",
        "The five-dimensional central value and its five-axis covariance use the purity subtraction, and that central value keeps its bias of up to 4% in the highest-W cells, which no uncertainty quoted for it includes; the sixteen-cell result uses the refined negative-weight treatment."),
 ("N6", "note abstract", "The negative-weight treatment is used for the two-, three- and four-dimensional central values, in the generator tests,",
        "The negative-weight treatment is used for the two-, three- and four-dimensional central values and the sixteen-cell five-dimensional result, in the generator tests,"),
 ("N7", "note abstract", "interpreted as regularization bias, that no quoted uncertainty includes.",
        "interpreted as regularization bias, that no uncertainty quoted for the purity-subtracted five-dimensional central value includes."),
 ("N8", "note abstract", "Statistical intervals miscover at the tested truths,", "Statistical intervals of a deterministic purity-subtracted variant miscover at the tested truths,"),
 ("N9", "note abstract", "none of the tested reporting definitions satisfies the predeclared 10% criterion.",
        "none of the reporting definitions tested in the precision study satisfies the predeclared 10% criterion."),
 ("W1", "paper, Scope paragraph", "The paper does not deliver a validated five-observable cross-section measurement.",
        "The paper does not deliver a five-observable cross-section measurement whose intervals have validated coverage; the sixteen-cell result of Sec. V F is reported with total uncertainties and a fake-data study."),
 ("W2", "paper, Scope paragraph", "The sixteen-cell result of Sec. V F also has total uncertainties, whose coverage is not validated.",
        "The sixteen-cell result of Sec. V F is the exception: it also has total uncertainties, whose coverage is likewise not validated."),
 ("W3", "paper, Limitations paragraph", "Sec. V F reports the fake-data tests of the estimator's bias.",
        "Sec. V F reports the fake-data tests of the estimator's bias, in which the reported uncertainty does not cover the bias at the GiBUU-like truths or at the q_3 tilt."),
 ("R1", "note, release appendix", "or the quoted closure, bias and covariance-status measurements.",
        "or the quoted closure, bias and covariance-status measurements of the configuration-(a) central value."),
 ("R2", "note, release appendix", "Covariances: the five-axis covariance used in this note and its (E_avail,W) projection,",
        "Covariances: the five-axis covariance of the configuration-(a) central value and its (E_avail,W) projection,"),
 ("R3", "note, release appendix", "The four measurements that travel with the five-axis covariance used in this note",
        "The four measurements that travel with the five-axis covariance of the configuration-(a) central value"),
 ("R4", "note, release appendix", "The five-axis covariance used in this note is the file z-cv.npz,",
        "The five-axis covariance of the configuration-(a) central value is the file z-cv.npz,"),
]
scope = ("Scope. The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested, rather than of multidimensional OmniFold in general. "
         "Throughout, a three- to five-observable result is a central value without intervals of validated coverage: the output of the estimators of Sec. III, with the observable definitions, simulated detector response, background treatment, and regularization given there. "
         "The sixteen-cell result of Sec. V F also has total uncertainties, whose coverage is not validated. The paper does not deliver a validated five-observable cross-section measurement. "
         "The generator tests are conditional tests of simulated hybrid null hypotheses, ... [the paragraph continues unchanged]")
lim = ("The limitations of these results are stated with the results they qualify, in Secs. IV–VII. The principal ones are these. The two-dimensional covariance has not been independently validated, and its coverage has not been tested (Sec. IV D). "
       "The higher-dimensional central values lack intervals of validated coverage, and the uncertainties of the configuration-(a) five-observable central value omit its regularization bias (Sec. V B). "
       "The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec. V F reports the fake-data tests of the estimator's bias. The generator tests reject hybrid nulls, ... [the paragraph continues unchanged]")
rel = ("(1) RC7 supports replay of the higher-dimensional inference from sufficient inputs, but not extraction from the archived pseudo-experiment products, event-level unfolding, or the quoted closure, bias and covariance-status measurements.\n"
       "(2) Covariances: the five-axis covariance used in this note and its (E_avail,W) projection, with the algebra of Eqs. (...), the declared centering variant, and the band partition.\n"
       "(3) The four measurements that travel with the five-axis covariance used in this note, carried in the package that readers will quote and not only in this note.\n"
       "(4) The five-axis covariance used in this note is the file z-cv.npz, with sha256 ... , so a loaded C_Z can be checked against both.")
for pid, where, old, new in P:
    src = {"paper abstract": pa, "note abstract": na, "paper, Scope paragraph": scope, "paper, Limitations paragraph": lim}.get(where, rel)
    assert src.count(old) == 1, (pid, old[:50])
ctx = ("CONTEXT 1. The paper's current abstract (%d words):\n\n%s\n\nCONTEXT 2. The companion technical note's current abstract (%d words):\n\n%s\n\n"
       "CONTEXT 3. The paper's Scope paragraph (Sec. I), current:\n\n%s\n\nCONTEXT 4. The paper's Limitations paragraph (Sec. VIII), current:\n\n%s\n\n"
       "CONTEXT 5. Items of the note's release appendix, current (the note names its estimator configurations (a)-(f) throughout):\n\n%s\n\n"
       "Background: the paper reports two five-observable products. One is a central value from purity-based background subtraction (called configuration (a) in the body), with a covariance. "
       "The other is a sixteen-cell result from a refined negative-weight estimator (configuration (e)), with total uncertainties and a fake-data study of its bias; it is new in this draft.\n"
       % (len(pa.split()), pa, len(na.split()), na, scope, lim, rel))
def plist(order):
    return "".join(f'{p[0]}. [{p[1]}]\n   OLD: "{p[2]}"\n   NEW: "{p[3]}"\n\n' for p in order)
def newlen(abstract, ids):
    t = abstract
    for p in P:
        if p[0] in ids:
            t = t.replace(p[2], p[3])
    return len(t.split())
npa, nna = newlen(pa, {"A1", "A2"}), newlen(na, {"N1", "N2", "N3", "N6", "N7", "N8", "N9"})
lq = (f"LENGTH. With every proposal applied, the paper abstract goes from {len(pa.split())} to {npa} words, and the note abstract from {len(na.split())} to {nna} words.\n")
for tag, order in (("fwd", P), ("rev", P[::-1])):
    open(f"{X}/input-{tag}.txt", "w").write(ctx + "\nTHE PROPOSED CHANGES (answer in the order listed)\n\n" + plist(order) + lq)
open(f"{X}/proposals.tsv", "w").write("".join("\t".join(p) + "\n" for p in P))
print("paper abstract", len(pa.split()), "->", npa, "; note abstract", len(na.split()), "->", nna)

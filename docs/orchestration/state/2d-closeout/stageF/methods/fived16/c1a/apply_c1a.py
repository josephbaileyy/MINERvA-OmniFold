r"""usage: python3 -I apply_c1a.py ANALYSIS_NOTE_DIR -- step (c), the 1A half: the GENIE v3 held-out bias test.

Under DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md items 1 and 5 ("It is a bias test,
not a coverage test ... The paper says so"; the limitation sentences are revised from 1A's result and their wording
goes to Joseph with the final draft) and FD-F1-BINDING.md ruling 2. The readout is fd_f1_readout.json (cbe411a9,
FD-F1-REPORT.md, PR #446); every number is an \fvval key from make_values_fived16.py.

- E1, the Sec. I limitations paragraph (the 1A slot): the coverage sentence keeps "has not been validated" and adds
  the bias test, with "cannot test the intervals' width" (the readout's labels.f1). The fake-data pointer moves from
  sec:result16 to sec:fd16, where the study now prints (b3 review S2).
- E2, E3, the two abstracts: the coverage sentence adds the bias test's result in words. "Below the reported
  uncertainty in every cell": max |b|/sigma is under f1-bsig-ceil in all four records (asserted in make_values).
- E4, the paper's IV H: one paragraph after the F0b result, inside the FIVED16 block: the two tunes, how they enter,
  the grade, the overlaps (FD-F1-BINDING.md ruling 2), the descriptive leave-out grade, and "a bias test, not a
  coverage test".
- E5, the note's sec:fived16-fd: the same in full, as a paragraph (no new table, so no note table renumbers): all four
  records, the held-out group's tally as context, the overlaps, the descriptive variants, control 9.
The coverage sentences of C_model at held-out truths, the Scope paragraph, the Discussion, and the note's sec_intro and
sec_summary are unchanged: they say the coverage is not validated, which stays true.
PRD read round 5 (prd-read/r5; prd-read/REPORT.md "Round 5"): E1 is sol2 r2's L1 form and E4's paragraph sol2 r1's H1 form,
each applied whole after the truth column; the first drafts are r5/input.txt's NEW lines. E2, E3 and E5 are kept, except
that E2 and E3 add "but does not test interval widths" (L1's words) after agy's first pass (c1a/agy): without it, both
abstracts could be read as validating the intervals. agy's second pass read H1's "using the C_model procedure and the
simulation's detector response" as the response being used or probed; it now says "the detector response is the
simulation's and is not probed", as the readout's label does. The review of 589f0780 (N2, N3): "the same quasielastic
cross-section model" (both NievesQELCCPXSec; AR23 with a z-expansion form factor, FD-F1-DECLARATION.md:296-298,
probes/probe12.out), and the truth as the tune's shape ratio to GENIE CV, built as for the C_model components
(DECLARATION sec. 3 step 2), not "the tune's shape".
Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys

SRC = (r"% Step (c), 1A (fived16/c1a/apply_c1a.py): FD-F1-REPORT.md sec. 1.1 (the grade; control 9), sec. 1.3 (the "
       r"overlaps); fd_f1_readout.json (cbe411a9) labels.f1 and labels.not; FD-F1-DECLARATION.md sec. 3 (the truths as "
       r"pvl_ratios shape ratios, as the C_model vertices), sec. 4 (20 Poisson experiments on half the MC; the "
       r"noise-free closure), :297-298 (the CCQE and 2p2h models: NievesQELCCPXSec for both; NievesSimoVacasMECPXSec for G18, SuSAv2MECPXSec for AR23); FD-F1-BINDING.md ruling 2 (graded as non-vertex "
       r"truths against C_total + C_resp; the leave-out-GENIE+MEC grade descriptive; partial evidence; not two "
       r"independent tests). The tunes were generated for this test: LIMITATION-PLAN.md sec. 1.4, 1A (no GENIE v3 "
       r"events existed). Not a coverage claim.")

PAPER = [
 ("E1", r"The coverage of its intervals has not been validated. In a fake-data study at \fvval{f0b-all-truths} truths, the reported uncertainty does not cover the estimator's bias at the GiBUU-like truths or at a synthetic $q_{3}$ tilt (Sec.~\ref{sec:result16}).",
  r"Interval coverage has not been validated. At two held-out GENIE~v3 truths, a bias test finds the estimator's bias below the reported uncertainty in every cell, but does not test interval widths. In a fake-data study at \fvval{f0b-all-truths} truths, the reported uncertainty does not cover the estimator's bias at the GiBUU-like truths or at a synthetic $q_{3}$ tilt (Sec.~\ref{sec:fd16})."),
 ("E4", r"At the other \fvval{f0b-nunlisted} truths the bias passes both criteria: no cell beyond $\fvval{trig-z}\sigma$ and $p\geq\fvval{trig-p}$." + "\n% FIVED16-END",
  r"At the other \fvval{f0b-nunlisted} truths the bias passes both criteria: no cell beyond $\fvval{trig-z}\sigma$ and $p\geq\fvval{trig-p}$." + "\n\n" + SRC + "\n" +
  r"Two GENIE~v3 tunes, \fvval{f1-tune-g18} and \fvval{f1-tune-ar23}, were generated for this test and held out of the analysis. Each reweights the simulated truth by the tune's shape ratio to GENIE CV, built as for the $C_{\mathrm{model}}$ components; the detector response is the simulation's and is not probed. For each tune, \fvval{f1-n} Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance. Both tunes satisfy both bias criteria: the pseudo-experiment means give $\chi^2=\fvval{f1-g18-chi2}$ ($p=\fvval{f1-g18-p}$) and \fvval{f1-ar23-chi2} ($p=\fvval{f1-ar23-p}$), respectively, with $|z|\leq\fvval{f1-zmax-ceil}$ in every cell of the means and closures. Both are GENIE tunes and use the same quasielastic cross-section model; \fvval{f1-tune-g18} also uses a Valencia-family MEC model, as does the GENIE + MEC component of $C_{\mathrm{model}}$. They provide partial evidence and are not independent tests. Omitting that component gives $\chi^2=\fvval{f1-g18-sens-chi2}$ ($p=\fvval{f1-g18-sens-p}$) and \fvval{f1-ar23-sens-chi2} ($p=\fvval{f1-ar23-sens-p}$), respectively, as a descriptive comparison. These tests assess bias, not coverage: only event counts fluctuate, without variation of systematic parameters, so interval widths cannot be tested." + "\n% FIVED16-END"),
]
MAIN_PAPER = [
 ("E2", r"The coverage of the intervals has not been validated.",
  r"The coverage of the intervals has not been validated; a bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths."),
]
MAIN_NOTE = [
 ("E3", r"The coverage of the result's intervals has not been validated.",
  r"The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths."),
]
NOTE = [
 ("E5", "\n" + r"\subsection{Comparison with generator predictions}",
  "\n" + SRC + "\n" +
  r"Two truths are held out of the analysis: the GENIE~v3 tunes \fvval{f1-tune-g18} and \fvval{f1-tune-ar23}, generated for this test. Each enters as its gated, normalized shape ratio to GENIE CV on the fine grid, built as the reweighting ratios of the $C_{\mathrm{model}}$ vertices are, pooled over a coarser cell or set to one where the tune's sample fails the ratio's statistical gate, and applied to the simulated truth under the simulation's detector response. At each, \fvval{f1-n} Poisson pseudo-experiments on half the simulation and a noise-free closure are graded against the full reported covariance, as truths without a vertex, in a group of their own that is never pooled with the groups above. The bias passes both criteria in all four records. The mean of the pseudo-experiments gives $\chi^2=\fvval{f1-g18-chi2}$ ($p=\fvval{f1-g18-p}$; largest $|z|$ \fvval{f1-g18-zmax}, in \fvval{f1-g18-zcell}) at \fvval{f1-tune-g18} and \fvval{f1-ar23-chi2} ($p=\fvval{f1-ar23-p}$; \fvval{f1-ar23-zmax}, in \fvval{f1-ar23-zcell}) at \fvval{f1-tune-ar23}; the closures give \fvval{f1-closure-g18-chi2} ($p=\fvval{f1-closure-g18-p}$; \fvval{f1-closure-g18-zmax}, in \fvval{f1-closure-g18-zcell}) and \fvval{f1-closure-ar23-chi2} ($p=\fvval{f1-closure-ar23-p}$; \fvval{f1-closure-ar23-zmax}, in \fvval{f1-closure-ar23-zcell}). In every cell of the four records, the bias is below \fvval{f1-bsig-ceil} of the cell's reported $\sigma$. The group has \fvval{f1-grp-zcells} of \fvval{f1-grp-cells} cells with $|z|>\fvval{trig-z}$ (Gaussian reference \fvval{f1-grp-refcells}) and \fvval{f1-grp-ptruths} of \fvval{f1-grp-truths} records with $p<\fvval{trig-p}$ (reference \fvval{f1-grp-reftruths}). The references count the four records as independent, but they are two truths, each counted by its pseudo-experiments and by its closure, so they are context only." + "\n\n" +
  r"The two tunes use the same quasielastic cross-section model, GENIE's \texttt{NievesQELCCPXSec}, \fvval{f1-tune-ar23} with a z-expansion form factor, and the MEC model of \fvval{f1-tune-g18} is of the Valencia family used in the GENIE + MEC vertex. Both are GENIE tunes, so they are partial evidence and not independent tests. Descriptively, without the GENIE + MEC vertex the pseudo-experiments give $\chi^2=\fvval{f1-g18-sens-chi2}$ ($p=\fvval{f1-g18-sens-p}$) and \fvval{f1-ar23-sens-chi2} ($p=\fvval{f1-ar23-sens-p}$), and the closures \fvval{f1-closure-g18-sens-chi2} ($p=\fvval{f1-closure-g18-sens-p}$) and \fvval{f1-closure-ar23-sens-chi2} ($p=\fvval{f1-closure-ar23-sens-p}$). The model-only $\chi^2$, defined as in Table~\ref{tab:fived16-fdvar}, are \fvval{f1-mo-chi2-min}--\fvval{f1-mo-chi2-max} in the four records, with \fvval{f1-ar23-mo-cells} beyond $\fvval{trig-z}\sigma$ at \fvval{f1-tune-ar23} in both its records. The grading, rerun with the two truths, reproduces every record of the fake-data truths above exactly. This is a bias test, not a coverage test: Poisson pseudo-experiments with no draws of the systematic parameters cannot test the width of the intervals, and the detector response is not probed." + "\n\n" + r"\subsection{Comparison with generator predictions}"),
]


def pat(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))


def apply(path, edits):
    t = open(path, encoding="utf-8").read()
    for k, old, new in edits:
        m = list(pat(old).finditer(t))
        if len(m) != 1:
            sys.exit(f"{k}: {len(m)} matches in {path}")
        t = t[:m[0].start()] + new + t[m[0].end():]
    open(path, "w", encoding="utf-8").write(t)


if __name__ == "__main__":
    D = sys.argv[1]
    apply(f"{D}/paper_body.tex", PAPER)
    apply(f"{D}/main_paper.tex", MAIN_PAPER)
    apply(f"{D}/main_note.tex", MAIN_NOTE)
    apply(f"{D}/sec_fived16.tex", NOTE)
    print("c1a applied: %d edits" % (len(PAPER) + len(MAIN_PAPER) + len(MAIN_NOTE) + len(NOTE)))

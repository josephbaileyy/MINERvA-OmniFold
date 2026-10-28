r"""usage: python3 -I apply_c3d_r4.py ANALYSIS_NOTE_DIR -- step (c), flux half: the paper's band sentences after the
PRD read r4 and agy (prd-read/REPORT.md "Round 4"; c3d/agy/).

- D1, the paper: SHORTEN 3/3. gemini's form drops "they are not intervals for the chi2 under the true
  correlations", which the director required kept, so it is not applied. sol2's two forms are both true apart from
  agy's second point; r2's, the shorter, is applied with agy's two fixes:
  - "These bands measure how precisely the universes determine the correlations" is not what the study measured. It
    measured the estimation scatter of the reported chi2, which is now said;
  - "edges within 1.5-6.2%" can read as each edge lying between 1.5% and 6.2% of the reported value, which NuWro's
    lower edge (1.36%) contradicts. It now gives the bound only: "within 6.2%".
  Both parts of the director's clause stay: not the sensitivity to incorrect correlations, which the weakening
  probes; not intervals for the chi2 under the true correlations.
- D2, the note: sol2's two runs split (ACCEPT, SHORTEN), so the text is kept (the round-3 rule); agy found it SAME.
- P02: ACCEPT 3/3, unchanged.
The edit must match exactly once."""
import re, sys
D = sys.argv[1]
OLD = (r" The flux correlations are themselves estimated from the \fvval{fb-universes} hadron-production (PPFX) flux universes of Ref.~\cite{MINERvA:2016iqn}, weighted by the neutrino--electron and inverse-muon-decay constraint."
       r" Rebuilding them from bootstrap replicates of those universes gives \fvval{fb-plo}--\fvval{fb-phi}\,\% percentile bands of each 16-cell $\chi^2$ whose edges lie within \fvval{fb-edge-min}--\fvval{fb-edge-max}\,\% of the reported value, with the bootstrap median above it by at most \fvval{fb-offset-relmax}\,\%."
       r" These bands measure how precisely the universes determine the correlations, not how much the $\chi^2$ would change if the correlations were wrong, which the weakening probes; they are not intervals for the $\chi^2$ under the true correlations.")
NEW = (r" The flux correlations are estimated from \fvval{fb-universes} hadron-production (PPFX) flux universes~\cite{MINERvA:2016iqn}, weighted by the neutrino--electron and inverse-muon-decay constraint."
       r" Bootstrapping these universes gives \fvval{fb-plo}th--\fvval{fb-phi}th percentile bands for each 16-cell $\chi^2$, with edges within \fvval{fb-edge-max}\,\% of the reported value and a median at most \fvval{fb-offset-relmax}\,\% above it."
       r" These bands describe the scatter of the $\chi^2$ from estimating the correlations with these universes, not its sensitivity to incorrect correlations, which the weakening probes; they are not intervals for the $\chi^2$ under the true correlations.")
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
if t.count(OLD) != 1: sys.exit("D1: %d matches" % t.count(OLD))
open(p, "w", encoding="utf-8").write(t.replace(OLD, NEW, 1)); print("D1 r4 form applied")

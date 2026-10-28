r"""usage: python3 -I apply_c3d.py ANALYSIS_NOTE_DIR -- step (c), the flux half (3D): the band sentences, as a DRAFT for
the small PRD read, agy with a control and the truth column, then Joseph in the final draft (d).

Under:
- DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md item 3;
- FD-FLUX-BOOT-REPORT.md (PR #438; readout fd_flux_boot_readout.json, sha256 b7b5652c, pinned in
  make_values_fived16.py);
- FD-FLUX-BOOT-BINDING.md ruling 2: only the correlation variant's 16-84% percentile band, beside Stage G's chi2 and
  the offset, as estimation scatter given these universes under PPFX and the nu-e + IMD constraint; never as an
  interval for the true chi2, never the basic band;
- the director, 2026-10-28: the alpha = 0.1 sentence is kept and the band sentences follow it; whether to replace it
  is Joseph's, in (d). The last clause keeps both parts, "not how much the chi2 would change if the correlations were
  wrong" and "not intervals for the chi2 under the true correlations", so the text cannot read as "the chi2 is
  insensitive to the flux correlations" (the readout's NOT CITABLE FOR).

Every number is \fvval{...}. Each edit appends to the paragraph that holds the alpha sentence, and must match exactly
once."""
import sys
D = sys.argv[1]
PAPER_ANCHOR = r"every 16-cell prediction keeps $\chi^2\geq\fvval{sens-joint-chi2-min}$ for 16 degrees of freedom."
PAPER_ADD = (r" The flux correlations are themselves estimated from the \fvval{fb-universes} hadron-production (PPFX) flux universes of Ref.~\cite{MINERvA:2016iqn}, weighted by the neutrino--electron and inverse-muon-decay constraint."
             r" Rebuilding them from bootstrap replicates of those universes gives \fvval{fb-plo}--\fvval{fb-phi}\,\% percentile bands of each 16-cell $\chi^2$ whose edges lie within \fvval{fb-edge-min}--\fvval{fb-edge-max}\,\% of the reported value, with the bootstrap median above it by at most \fvval{fb-offset-relmax}\,\%."
             r" These bands measure how precisely the universes determine the correlations, not how much the $\chi^2$ would change if the correlations were wrong, which the weakening probes; they are not intervals for the $\chi^2$ under the true correlations.")
NOTE_ANCHOR = r"one group's correlations are shrunk toward the diagonal by a fraction $\alpha$ of the way, with its variances kept."
NOTE_ADD = (r" The flux correlations are themselves estimated from the \fvval{fb-universes} PPFX flux universes, weighted by the neutrino--electron and inverse-muon-decay constraint (\S\ref{sec:fived16-cov})."
            r" Rebuilding the flux block from \fvval{fb-replicates} bootstrap replicates of those universes, with its variances kept, gives \fvval{fb-plo}--\fvval{fb-phi}\,\% percentile bands of the total $\chi^2$:"
            r" \fvval{label-gcv} \fvval{fb-gcv-lo}--\fvval{fb-gcv-hi} around \fvval{g-gcv-total-chi2int}, \fvval{label-gmec} \fvval{fb-gmec-lo}--\fvval{fb-gmec-hi} around \fvval{g-gmec-total-chi2int}, \fvval{label-nuwro} \fvval{fb-nuwro-lo}--\fvval{fb-nuwro-hi} around \fvval{g-nuwro-total-chi2int}, \fvval{label-tune} \fvval{fb-tune-lo}--\fvval{fb-tune-hi} around \fvval{g-tune-total-chi2int}, and \fvval{label-gibuu}, on its \fvval{g-gibuu-total-ndf} cells, \fvval{fb-gibuu-lo}--\fvval{fb-gibuu-hi} around \fvval{g-gibuu-total-chi2int}."
            r" In each, the bootstrap median lies above the reported value, by \fvval{fb-gcv-offset}, \fvval{fb-gmec-offset}, \fvval{fb-nuwro-offset}, \fvval{fb-tune-offset} and \fvval{fb-gibuu-offset} in the same order."
            r" These bands measure the estimation scatter of the reported $\chi^2$ given these universes, not how much it would change if the flux correlations were wrong, which the weakening above probes; they are not intervals for the $\chi^2$ under the true correlations.")
for f, anchor, add in [("paper_body.tex", PAPER_ANCHOR, PAPER_ADD), ("sec_fived16.tex", NOTE_ANCHOR, NOTE_ADD)]:
    p = f"{D}/{f}"; t = open(p, encoding="utf-8").read()
    if t.count(anchor) != 1: sys.exit(f"{f}: anchor found {t.count(anchor)} times")
    if "fb-universes" in t: sys.exit(f"{f}: already applied")
    open(p, "w", encoding="utf-8").write(t.replace(anchor, anchor + add, 1))
print("3D band sentences applied (draft)")

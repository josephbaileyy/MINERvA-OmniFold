# The five-dimensional (5D) result to be added to the paper

This describes content that is measured and decided but not yet written into the paper. It is given so that the
scope advice accounts for it.

- **The result:** an unbinned OmniFold unfolding in five observables, muon p_T, muon p_parallel, available energy
  E_avail, three-momentum transfer q3 and hadronic invariant mass W. It is reported as cross sections in 16 reporting
  cells (R00-R15), which are boxes in those observables.
- **The reported uncertainty:** a full 16x16 covariance. It is the experimental and systematic covariance plus a
  generator-model-dependence term plus a detector hadronic-response term. The median per-cell relative uncertainty is
  about 7.3 percent.
- **A fake-data study:** the estimator's bias is graded against the reported covariance on 12 synthetic truths. The
  uncertainty covers the bias for GENIE-like and most NuWro-like truths. It does not cover it for GiBUU-like truths or
  for a synthetic q3 tilt. This limitation is stated.
- **Comparisons with five generator predictions** (GENIE 2.12.10 CV, GENIE with Valencia MEC, NuWro 21.09, GiBUU 2019
  on 8 of the cells, and the MINERvA-tuned simulation used as the unfolding prior):
  - chi2 with ndf under the reported covariance, with a shape-only chi2 beside it;
  - every generator is strongly disfavoured, with chi2 of 58 to 330 for 8 to 16 ndf;
  - the chi2 is dominated by a few combinations of neighbouring cells in which the flux uncertainty largely cancels.
    Weakening the flux correlations by 10 percent roughly halves it, and with the systematic correlations removed every
    generator still gives chi2/ndf of about 3 or more.
- **What the paper will print, as already decided:**
  - the chi2 table;
  - a data/generator ratio figure;
  - one quantified sentence on the correlation sensitivity;
  - the fake-data limitation, stated where the GiBUU comparison is given.
- **What the companion analysis note will print:** a figure of the cell combinations that carry the chi2, the
  sensitivity tables, a per-cell look at the most constraining cell, and the full fake-data results.

# Seven editorial corrections after the final referee read of 26af095d5 (2026-11-16)

The director routed these from the final referee read (minor revision), plus one item from director-helper-3 and one
from the director, as editorial only, with no claim changes. They are on director-helper-3's head 6e92be1fb.

| # | Where | Correction |
|---|---|---|
| 1 | Table S13 (tab:prr-levels) caption | The observable column mask applies to "the learners named in the `Applies to` column", not to "all three". The first observable row changes only the step-1 classifier. |
| 2 | S3 binning | The q3 edges are in GeV/c, and the hadronic axes' span gives q3 in GeV/c. |
| 3 | Table S14 (tab:cov-design) | New row "Excluded from C_T": for the 2D test, the run-period block; for the 5D test, C_resp and C_PL,5D, and in the primary variant also the GEANT4 neutron and proton bands (paper section 6.2). |
| 4 | Table S11, test 10 | The joint level is spelled out as test 8's: "null-alpha/16 per cell, null-alpha jointly". |
| 5 | Paper table tab:outcomes caption | "Two rows use `Descriptive` in a specific sense" replaces "has two uses here". The benchmark rows also print a descriptive distance. |
| 6 | S7, the sixteen-cell IBU | "its truth bins are the boxes from which the sixteen cells are formed (section S2)" replaces "the coarse grid". The paper's coarse grid is another grid. Matches the paper's section 4.5 and the REF-G1 declaration (H2 cells). |
| 7 | Paper section 7 | "cannot produce such contrasts" replaces "cannot produce the pattern", which had no antecedent. |

Read 1 (gpt-6.1-sol, high effort, read-only) FAILed item 3 alone: its first row omitted the primary variant's
GEANT4 bands, which the paper leaves out of the covariance as well. That is fixed. Read 2 PASSed all seven. Its one
optional suggestion, to name the empty boxes that are dropped in item 6, is not applied: the earlier wording omitted
them too. Each read's evidence is in its directory. new_paper.tex and new_supplement.tex are the committed sources at
this commit and are not copied.

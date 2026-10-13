# C07′ data-POT counting: is a band documented by MAT or the published analysis?

**Owner:** 2D closeout executor (2d closer), directed by the paper-tighten lane under
`AUTHORIZATION-20261012-2d-closeout-delegation.md`.
**Date:** 2026-10-12. **Rule applied:** Joseph's recipe decision C07′
(`docs/publication/DECISION-20261012-joseph-2d-closeout-recipe.md`, main `3921dec4`): add a POT-counting band
if MAT or the published analysis documents one; otherwise disclose it as omitted. The decision asked for this to
be settled during pilot design.

## Determination

**NOT DOCUMENTED as a band → disclose as omitted.** Neither MAT nor Ruterbories et al. 2021 (PRD 104, 092007;
arXiv:2106.16210v4) defines a POT-counting uncertainty band. The disclosure should also say that the NuMI flux
prediction includes a 2% POT-counting term (Aliaga et al. 2016). By MINERvA convention that term sits inside the
flux band, so adding a separate band would risk counting it twice.

## Evidence

All reads were made on 2026-10-12. A research subagent did the search, and I re-read the starred lines myself.

**Published analysis** (arXiv:2106.16210v4, text extracted from the downloaded PDF):
- ★ The exposure is stated as a value only ("10.61 × 10^20 protons on target"), with no uncertainty.
- ★ The flux is quoted "6.32 × 10⁻⁸ ± 3.9% per cm² per proton on target", so it is normalized per POT.
- ★ §V has a single normalization term: "normalization uncertainty of 1.4% corresponds to the un[certainty in the
  number of target nucleons]". This is the Fig. 6/7 "Normalization" curve.
- ★ A text search for "POT counting", "toroid" and "protons on target" finds only the exposure statement and a
  reference title. There is no uncertainty term.
- The ancillary README (`2d-unfolding/minerva_paper_anc/README:25-30`, main `b456fa4d`) lists total, stat, flux
  and energy-scale covariances only.

**MAT** (NERSC `MINERvA101/MAT` `35097b65ab1680db8058f9ede18fecffdc3a1ea3`, `MINERvA101/MAT-MINERvA`
`50d7631416d1c93edd4db6886a2ca29da64fee60`):
- ★ `MAT-MINERvA/utilities/MnvNormalization.h:100-103` sets `mass_scale_err = .014` ("Mass model scale +
  error"). This is the 1.4% target-mass term, not POT.
- ★ `MAT/PlotUtils/MnvPlotter.cxx:401-406` has a `"POT_Scale"` entry, but only as a name in a plotting
  summary group for a pion analysis's style. A repo-wide grep finds no code that creates a `POT_Scale` error
  band or sets its size. The only other hit is the installed copy of the same file
  (`opt/include/PlotUtils/MnvPlotter.cxx:404`).
- The subagent also read the following: `MacroUtil.h:36-38` "POT counting" holds only data and MC POT values;
  the inclusive style (`kCCQENuInclusiveStyle`) groups no POT entry under Normalization.

**Where a POT-counting uncertainty does appear:**
- ★ Aliaga et al., "Neutrino flux predictions for the NuMI beam", arXiv:1607.00704v3, §IV.
- ★ The quote reads: "the 2% measurement uncertainty of the number of protons incident on the NuMI target (POT
  counting)". It is listed as a flux-prediction uncertainty in their Fig. 7.
- That paper is the low-energy flux paper. This analysis uses the ME flux with the ν-e constraint.

## Inferred, not verified

- That the ME PPFX flux universes carry the POT-counting term. The universes are read from flux files, and their
  construction was not inspected.
- That the ν-e constraint (arXiv:1906.00111) absorbs a POT-normalization error common to both measurements. This
  is reasoning only; neither paper states it.

## Scope of the search

The search was in the ancillary README and the analysis note on main. On NERSC it covered MAT, MAT-MINERvA,
UnfoldUtils and GENIEXSecExtract, grepping for POT scale/err/uncert/count, Normalization, MassModel,
Target_Mass, 0.014 and exposure. It also read the full text of arXiv:2106.16210v4, arXiv:1607.00704v3 and
arXiv:1906.00111. The web search for other ME MINERvA papers listing a POT line was narrow. The downloaded PDFs
are not committed.

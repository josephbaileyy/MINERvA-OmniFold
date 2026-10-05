# Manuscript outline (2026-10-05): recommended specialist article, plus the conditional Letter variant

**CITABLE FOR:** the proposed structure, figure roles and claim placement for the two routes in the decision
packet (§2).
**NOT CITABLE FOR:** any result or wording approval. The numerical headline is deliberately left blank until the
handoffs in packet §3 land. No `docs/analysis-note/` source was edited by this lane.

Claim ids (I*, L*) refer to `CLAIMS-20261005-claim-to-evidence.md`. "[HOLD]" marks text that waits on a named
handoff.

## A. Recommended: specialist article (for example Phys. Rev. D), "Unbinned five-observable unfolding of MINERvA charged-current data and calibrated joint generator tests"

**Thesis.** An unbinned event-weight unfolding can be validated end-to-end against a published binned measurement,
extended to five simultaneous observables, and used for a calibrated joint test whose Monte Carlo calibration runs
the full analysis chain. Its limits are measured rather than assumed: a statistical-band coverage failure,
regularization bias at high W, an incomplete response model, and the estimator-seed sensitivity of the adopted
covariance.

1. **Introduction.** The generator-model problem in the few-GeV inclusive region. Why simultaneous observables
   matter. OmniFold and its prior neutrino applications, positioned without a first-use claim (literature file
   §1–§3). Derived observables (q3, W, E_avail share q0) are correlated, so five observables are not five
   independent measurements.
2. **Data, signal and simulation.** The ME-FHC OpenData AnaTuples (cite DOI 10.15484/3022562 and NIM A743), the
   older production used (OI-55), the signal definition and selection of Ref. 2106.16210, MnvTune v1, and the four
   external generators with their domains. GiBUU lacks E_ν > 20 GeV.
3. **Method.** The OmniFold steps, the GBDT estimators, and **the three estimator identities**: F1 for the
   production central values, LightGBM for the 2D ensembles, R for the joint tests (L4). The background
   treatment. The reporting grids: 10,694 reported cells and 109 J cells.
4. **Validation.**
   - The 2D reproduction (L1) and the uncertainty construction (L2), with the **fixed-truth coverage failure of the
     2D statistical band** (L3) in place of "untested".
   - The marginal anchors and injected closures (L5).
   - The background and regularization bias (L6), stated where the results are read and not in a supplement.
5. **Central-value results.** The low-E_avail deficit and 2p2h (L7). The (E_avail, q3) comparison with
   Ascencio et al. The joint (E_avail, W) central value relative to MnvTune and the external generators (L8, L9),
   explicitly descriptive.
6. **Calibrated joint tests** [HOLD for the numbers].
   - The null as amendment 7 defines it (the simple fine-grid hybrid null) and the two statistics.
   - The calibration process with its nuisance draws, V as a power-setting metric, the claim rule (process-shift
     and M1 variants), and Holm with determinacy.
   - The sequential stopping.
   - The result table (PLAN §4 columns): null, domain, statistic, k, B, p, CP interval, Holm step and threshold,
     decision, robustness label, missing-seed status and resolution, and the independent-recompute verdict.
   - **The conditions travel with the table** (amendment 7 `conditions_stated_with_every_claim`, all six). The
     recoil-response condition goes in the main text, together with the W2 result if W2 is approved.
   - Power appears only where amendment 7 allows it.
7. **Uncertainty status.** The adopted covariance under exception with its four measurements, and why no
   significance is derived from it (L10). The measurement branch was not admitted (I9). PET status (L12) in one
   sentence, or omitted.
8. **Conclusions.** What is constrained: the joint incompatibility of these five predictions under the declared
   model [HOLD]. What is not: localization, mechanism, a complete measurement, and modern generator versions. What
   a complete measurement release would add.
9. **Data availability and reproduction.** The release levels of the release inventory §3.

**Figures (roles). F2 and F4 do not exist yet; both are plotting-only from committed receipts and outputs:**
- F1: the 2D validation (the current Letter's Fig. 1).
- F2: the coverage failure of the 2D band (from VL168 receipts; plotting only).
- F3: the joint (E_avail, W) central value with the estimator named.
- F4: the observed statistic against each null's calibrated distribution, total and shape, with the claim variants
  [HOLD; plotting from frozen outputs and per-draw T, no new compute].
- F5: generator context (the current Letter's Fig. 3).

**Length:** a PRD article has no Letter limit. Keep the limitations in the body.

## B. Conditional Letter variant (PRL), only if packet §2's upgrade conditions are met

The core sequence follows PLAN §5:
1. **Question and result:** joint incompatibility under explicit conditions [HOLD].
2. **Data and method:** the R estimator and the 109-cell domain.
3. **Validation:** a compact version of L1, L3, L5 and L6; the missing-seed resolution; the response sensitivity
   (W2).
4. **Principal inference:** the table and F4.
5. **Consequence:** the matched coarse-projection comparison (W1), **required but not sufficient**. W1 can show
   discrimination only beyond coarse projections of the same cells, and the published 2D comparison already
   disfavours every family tested (packet §5.3).

**Exclusions:**
- The localization (L8) is not a Letter claim. It is descriptive and sits in the region of largest regularization
  bias.
- No adopted-covariance significance (L10).
- No PET.

**Length:** at most 3,750 word-equivalents in the core and at most two pages of End Matter (APS rules; see the
literature file §5 for the requirements as fetched). The current `paper_body.tex` is 2,151 words by raw `wc -w`
on the source, comments included, which is not an APS count. The inference must replace material rather than be
added to it.

**Text in the current Letter that must change on either route:**
- `paper_body.tex:61`: "its coverage is untested" (L3).
- The abstract's central-value localization headline (L8).
- The acknowledgment and bibliography for the open data (L13).
- The release-appendix access sentence (release inventory §3).

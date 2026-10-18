# Draft disclosures: the 2D endpoint and its approximations (DRAFT revision 3, 2026-10-17)

**Prepared by** the paper-tighten lane, as director, for Joseph's review and the review with Ben. Adoption of any
wording is Joseph's (Stage F, J4). Nothing here is in a deliverable.

**CITABLE FOR:** the content each disclosure must carry, and its source record.
**NOT CITABLE FOR:** an adoption of wording, any claim or any figure. The numbers below come from reviewed records.
Joseph adopted S5 + C_PL on 2026-10-17 (J2,
[`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`](../../../DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md)).
The wording is draft until he decides J4.

**How to read this.** Each item gives the required content, then a draft paper sentence. The note carries the full
version. Every number is quoted with its record on `main`.

**Revision 2 (2026-10-17)** fills every ⟨placeholder⟩. The sources are:
- [`../stageC/production/REPORT.md`](../stageC/production/REPORT.md) (PR #150), verified in
  [`F4-VERIFICATION.md`](F4-VERIFICATION.md);
- its `evidence/production/results/s5.json` `8c815149…`;
- [`../playlist-term/REPORT.md`](../playlist-term/REPORT.md);
- [`../playlist-term/COMBINATION-REPORT.md`](../playlist-term/COMBINATION-REPORT.md) (PR #149).

It also adds D0 (the budget), D11 (seed-related terms reported but not added) and D12 (the declared conventions), and
writes the D10 sentences.

**Revision 3 (2026-10-17)** follows J2. It corrects four statements that an independent briefing for Joseph found and
the director re-measured (The briefing is uncommitted: it is in the director's session scratchpad, `briefing-J1-J6.md`.): D9 quoted the reco-level bound as if it held after unfolding; D5 paired the double-ratio
step with the raw ratio's χ²; D10 said no reviewed record states VL175's flux band; and the open list still named the
revision-2 review. It also carries out the two J2 conditions (D1 names what lies outside every block; D5 says the block's
own check is passed by construction) and adds two clarifications from the briefing (D4's sentence names which seed
noise the G2 test used; D11 names the two universes where retraining noise is comparable to or larger than the
shift).

**Review.** A fresh read-only reviewer checked revision 2 before Joseph saw it: APPROVE WITH CHANGES. All numbers
match their records. There were 7 MATERIAL findings (five interpretive sentences corrected, two omissions added) and
8 MINOR ones. All are applied here. The
review packet `docs/preparation/PUBLICATION-REVIEW-PACKET-20261016.md` (PR #145) offered an endpoint sentence and a
playlist clause. They are used where noted.
The current paper text these would replace is `docs/analysis-note/paper_body.tex` §`sec:uq2d`
(l.253–306 at `main` `2aab43b5`) and the Fig. 1 caption.

## D0. The budget (the numbers every item below refers to)

Per-cell relative σ and the integral, in percent of `E_U`. Sources: COMBINATION-REPORT §2, and `s5.json`
`total_summary` and `functionals_total_sigma_rel_pct`.

| matrix | cell median | cell p84 | cell max | integral | p_∥ projections | p_T projections |
|---|---|---|---|---|---|---|
| VL175 (superseded 2026-10-17) | 6.09 | 9.02 | 23.1 | 4.23 | 4.24–14.9 | 4.28–7.25 |
| S5 total | 6.04 | 8.95 | 23.3 | 4.33 | 4.30–13.7 | 4.36–7.27 |
| S5 + C_PL (**adopted**, J2) | 6.45 | 9.18 | 23.6 | 4.75 | 4.77–13.8 | 4.73–7.77 |

S5 blocks: universe 5.97% median, statistical 0.68%, training seed (C08) 0.057%. The S5 total's rank is 197 of 205,
at S5's rcond 1e-10.

> *Draft (J2 adopted S5 + C_PL).* The total uncertainty has a median of 6.4% per bin and is 4.8% on the integrated
> cross section. In the median bin and in the integral it is dominated by the systematic-universe block. The
> run-period block described below raises the per-bin median from 6.0% to 6.4%.

## D1. The endpoint (narrower, construction complete)

**Must carry:**
- what is achieved: a reproducible central value and a matched uncertainty construction, under stated conventions;
- what is not achieved: independent validation of interval, bias or covariance claims;
- why: no independent production-size MC, no validated continuous nuisance generator, and only already-inspected
  independent-generator samples;
- that no coverage claim is made;
- what lies outside every block, by name (J2 condition): G2 (unmeasured, D4), the learner dependence (D3), and the
  unfolding-model and regularization dependence and response departures (C09, C10: Stage D, unpriced; Stage B
  REPORT §3, R8).

Source: DECISION-20261014 §2; DECISION-20261017 §2.

> *Draft.* The two-dimensional result is a reproducible central value with an uncertainty construction matched to its
> estimator under the conventions stated below. The construction has not been validated by independent
> pseudo-experiments: that would require simulation samples and a nuisance generator that are not available.
> We therefore make no claim about the coverage of its intervals, and goodness-of-fit values computed with it are
> indicative. The following are not included in any uncertainty block: an approximation in the
> systematic-universe unfolds (below), the dependence on the machine-learning estimator, and the dependence on the
> unfolding model and its regularization, which requires independent-generator samples; and we assume the detector
> response varies only within its parametrized family.

*Alternative, from the preparation packet (PR #145):* "We report a reproducible two-dimensional central value with
a matched uncertainty construction under declared conventions. Full scientific closeout is not achieved: the
construction has not been independently validated for population or simultaneous interval coverage, and it supplies
no calibrated covariance-based generator significance. The independent-validation stages are deferred for this
publication." Joseph chooses the register.

## D2. Coverage and KI-85

**Must carry:**
- the history: the earlier statistical band undercovered (VL169); it was rebuilt (VL170); post-hoc rescoring is
  descriptive and partly circular;
- the held-out re-test is deferred and was not pre-registered;
- the new production statistical block (S1, seed 42, three streams) has not been coverage-tested at all.

Source: KNOWN_ISSUES 85; paper §`sec:uq2d` (current text).

Also carry the following. Source: REPORT §3, §12; `s5.json` `stat`, `centring`.
- The block's median is 0.68% per cell.
- Its ensemble error is 4.1% on σ (1/√(2·299)). The nested 150-vs-300 replica ratio is 1.001.
- The replica mean sits a median 4.43 σ/√300, that is 0.26 σ, from `E_U`. That offset does not enter the ddof-1
  covariance.

> *Draft.* The statistical block is a 300-replica bootstrap of data, signal and background simulation at the central
> value's training seed, with a median of 0.7% per bin. Its coverage has not been tested. An earlier statistical band
> undercovered in closure tests and was rebuilt (note §`sec:coverage`). The mean of the replicas differs from the
> central value by a per-bin median of 0.26 of the statistical standard deviation. The block is the covariance about
> the replica mean, so this offset is not included in it.

## D3. Training-seed and learner dependence

**Must carry:**
- the seed main effect C08 is estimated from 5 seed triplets: rank at most 4, relative SE of variance about 71%;
- it includes the bootstrap × seed interaction's 1/20 share;
- X02 and X03 are reported, not added;
- the exact-split against LightGBM learner difference (median 0.98%) is in no block.

Source: production DESIGN §8 and §12; paper §`sec:repro2d`.

Production numbers. Source: REPORT §3 and `s5.json` `c08`:
- C08's median is 0.057% per cell, and its rank is 4.
- It is 0.30 times VL175's 10-seed block (median σ_c08/σ_ML 0.304). **The new seed block is about 0.3 of the size
  of the one it replaces.**
- The reason is ruling R7 (Stage B REPORT, R7). C08 is the seed main effect. The bootstrap × seed interaction, which
  dominated the earlier 10-seed scan, is already inside the fixed-seed statistical block. C08 carries it only at a
  1/20 share, which is a median 0.685 of C08's diagonal (`s5.json` `x02`).
- Training noise inside the universe shifts is covered in D11.

> *Draft.* A training-seed block, estimated from five seed settings, has a median of 0.06% per bin and is itself
> uncertain by about 70% in variance. The dependence on the learner (a per-bin median of 0.98% between the two estimators
> studied) is not included in any block.

## D4. G2: miss-row weighting in the universe unfolds

**Must carry** (DECISION-20261015-joseph-g2-carry §2, verbatim requirements):
- an approximation in the universe unfolds' miss-row weighting, not repaired;
- tested in `MaRES_0` and `Flux:23`, each at seeds 42 and 43;
- in neither was an effect resolved above the trainer's seed noise;
- an effect below trainer noise is not excluded, and 2 of 187 universes were tested.

> *Draft.* The systematic-universe unfolds approximate the weighting of events that fail reconstruction. Tests in two
> of the 187 universes, a resonance-production (MaRES) universe and the flux universe with the largest completeness change, each at
> two training seeds, resolved no effect above the noise of the earlier ten-seed training scan, which is about three
> times the seed block used here. A smaller effect is not excluded, and the approximation is not corrected.

Production context. Sources: the G2 decision §1; REPORT §3, X03.
- The G2 tests measured the off/on difference against σ_ML, VL175's seed block.
- K2 excludes only a median effect above 2 σ_ML.
- Separately, retraining moves these two universes' shifts by a median 1.28–1.29 σ_ML (X03).
- **The test is not tight, and the disclosure must not present it as tight.**

## D5. The playlist-consistency term

**Must carry** (DECISION-20261015-joseph-playlist-consistency-term §2):
- an observed run-period inconsistency of **unknown cause**, carried as an uncertainty, **not** a measured systematic
  of a known source;
- what it covers: the 1G–1M p_∥ shape, with 1N–1P treated in the same construction;
- that it is a separate block added after the other blocks;
- its size;
- which period, if any, is right is not established.

Numbers on main (period-unfold REPORT):
- after unfolding, the 1G–1M/1A–1F double-ratio p_∥ step is +6.94% ± 0.41;
- diluted into the combined result, the raw shift (`bias_PB`) has χ² p_∥ 33.8 against VL175, where noise would give
  1.8; the double-ratio shift gives 33.1, an ad hoc supplement with no noise reference (period-unfold REPORT, table
  and note below it). Revision 2 paired the step with 33.8;
- every marginal z is below 0.7.

> *Draft.* Subsets of the data taken in different run periods are not mutually consistent within the other
> uncertainties: one period group's unfolded p_∥ distribution differs from the earliest periods by a step of about
> 7% near 8 GeV/c. The cause is not known, and these data cannot establish which period is correct. We carry the
> effect of this inconsistency on the combined result as an additional uncertainty block. It is built from the
> differences among three period groups without choosing any as the reference. Its median is 2.1% per bin. It is
> 1.2–3.4% on the p_∥ projections and 2.0% on the integrated cross section. With few period groups, its own size is
> poorly determined.

Numbers. Sources: playlist REPORT §2; COMBINATION-REPORT §2–3.
- C_PL per cell: median 2.14%, p84 3.31%, max 5.69%; integral 1.97%.
- About 1.8 effective degrees of freedom.
- **Added to S5:**
  - per-cell σ rises by a median of 5.4%, at most 34.5%;
  - the integral rises by 9.9%;
  - the largest projection rise is 21%, in p_∥ 6–7 GeV/c;
  - C_PL carries 9.9% of the per-cell variance (median) and 17.1% of the integral's.
- **The raw 1G–1M p_∥ χ²** is 34.8 against S5 alone and 1.97 against S5 + C_PL. That is a sensitivity reading only.
  The reference-construction χ² values are bounded by construction and say nothing about coverage.
- **The 1A–1F-reference sensitivity** is smaller: median 1.45%, integral 1.09%.
- **Its own check cannot fail** (J2 condition). The double-ratio χ² against any total containing C_PL sits at or below
  the first-order bound (0.68 in 1G–1M p_∥) whatever the data (COMBINATION-REPORT §3). The disclosure must not
  present that value, or the containment, as a test.

**Required:** C_PL's carried limits are uncorrected shrinkage, unsubtracted noise and few groups. The packet's clause
(PR #145) carries them and must be appended, or equivalent wording used: "Its reference-free double-ratio construction uses the periods' own
simulated responses; it does not identify a correct period. The small number of groups, possible regularization
shrinkage and retained statistical and training noise limit its interpretation. Containment of the observed
differences by this construction is not evidence of coverage."


## D6. `NormDISCC` (G3)

**Must carry:**
- the band is null in the products, so it is carried as zero;
- whether that is intended is unconfirmed.

Source: recipe decision G3; DECISION-20261014 item 3.

> *Draft.* One systematic category provided in the input products is identically zero; we carry it as zero, which we
> have not been able to confirm is intended.

## D7. C07′ (data-POT counting) omitted

**Must carry:**
- no separate POT-counting band is applied;
- the reason: the NuMI flux prediction already carries a 2% POT-counting term by convention, so a separate band
  would risk double counting;
- two links in that argument are inferred, not verified.

Source: Stage B diagnostics §6.2.

> *Draft.* No separate uncertainty is assigned to the counting of protons on target, since the flux prediction
> includes one by convention; that this term propagates through the constrained flux is inferred.

## D8. Background stream independence (C03 not applied)

**Must carry:**
- the background bootstrap stream is independent of the signal stream;
- whether background and signal-miss rows share events was not measured.

Source: production DESIGN §8.

> *Draft.* Statistical fluctuations of the background simulation are drawn independently of those of the signal
> simulation; possible shared events between the two were not assessed.

## D9. Run-period POT mixing (J36)

**Must carry:**
- the 12 playlists are pooled with one global POT ratio;
- the measured bound: +0.18% total, at most +0.32% in a marginal bin, at reco level;
- the unfolded J36 term: −0.084% on the integral (sum of periods minus pooled; the same sign as at reco level, where
  the pooled result is high); marginal bins at most 0.57% in magnitude (the lowest p_∥ bin;
  p_T at most 0.17%); single cells −1.79% to +3.13%, each with cell z at most 0.28.

Source: KNOWN_ISSUES J36; period-unfold REPORT (J36 paragraph) and `outputs/analysis.json` `J36`. Revision 2's sentence quoted only the reco-level bound.

> *Draft (note only; the paper may cite it).* Run periods are combined with a single exposure ratio rather than
> per-period ratios. The resulting bias is not corrected. At reconstruction level it is below 0.4% in every marginal
> bin. After unfolding, the pooled result is 0.08% above the per-period combination on the integral (the same sign as
> at reconstruction level), and differs from it by at most 0.57% in a marginal bin.

## D10. Construction limits named in the endpoint decision (note sentences; the paper points to the note)

- **KI-88 (estimator pairing).** *Note:* "The statistical block is built at the central value's estimator and
  training seed (LightGBM, seed 42), so the central value and its covariance are matched in estimator and seed;
  the replica mean still differs from the central value by a median 0.26 σ (D2)." Its F4 condition is met
  ([`F4-VERIFICATION.md`](F4-VERIFICATION.md)). The KI row closes only at K3.
- **KI-90 (cell identity in the two publication consumers).** **Still not verified.** S5's own 205 cells equal the
  nonzero `E_U` cells (COMBINATION check 2; F4 part A). The two consumers are checked at rebuild R1–R4. No note
  sentence until then.
- **KI-91 (flux-universe index identity).** *Note:* "The flux-universe index identity behind the 1/Φ_u rescale is
  established by the code chain and by an exact test. 900 events × 100 universes match to 5.5e-14, and a
  shifted-by-one control fails at ≥ 0.245 (Stage B §2.1). The production flux weights equal the constraint file and
  VL175's in all 12 playlists (`s5.json` `weights_equal_*`; F4 part A)."
- **KI-92.** *Note:* "The Rvp1pi and Rvn1pi variations are one input, counted once."
- **KI-93.** *Note:* "The universe block uses the July sweep, whose products record no driver digest and came from
  an uncommitted driver revision. Five of its universes are reproduced to ≤ 1.4e-11 by the committed driver (pilot
  K1), and seven in production (S4(ii)). The rest are qualified by inference from the same producer."
- **KI-94.** *Note:* "Statistical fluctuations of the background simulation are propagated as their own bootstrap
  stream. A separable background-only term (median 0.26 of the statistical σ) is contained in the statistical block and
  reported separately."
- **Laterals.** *Note:* "Lateral systematics use a single unfold at the central training seed each, so they include
  that seed's training noise."
- **Ensemble size.** *Note:* "With 300 replicas the statistical σ per bin is known to about 4%. The seed block, from
  five settings, is known to about 70% in variance."
- **Flux block below the published one.** *Note:* "Our flux block is smaller than the published analysis's (median
  4.01%). The reason is not established from the released inputs." This sentence is conditional on R1 stating S5's
  value. Ben's review item 10 asks him about this. Our
  value is S5's `band_Flux` median. It is computed at rebuild R1 from the F4-verified npz. The paper's current
  `\fluxBand` is VL175's, 3.655% per-cell median
  ([`DECISION-20261012-joseph-adopt-2d-c04-repair.md`](../../../../publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md)
  l.31). Revision 2 said no reviewed record stated it; that was wrong.

## D11. Seed-related terms reported, not added (production DESIGN §8; REPORT §3)

**Must carry:**
- the bootstrap × seed interaction (X02): a median of 0.076 of the statistical variance, which C08 includes at its
  1/20 share;
- the universe × retraining term (X03): in the six non-null universes tested (of 187; DESIGN §12, S4(ii) samples 7),
  the seed SD of each universe's shift is a median 1.24–1.33 σ_ML (4 dof each);
- both are reported, not added (rulings R5/R7);
- so, in those universes, the universe block carries single-seed training noise. Its size is comparable to VL175's
  seed block, per universe;
- in two of them the noise is comparable to or larger than the shift: `2p2h:0` shift 0.114% against seed SD 0.235%,
  and `MaCCQE:0` 0.266% against 0.220% (REPORT §3, per-cell medians). In expectation, noise adds variance to such a
  band rather than removing it (inferred); these two bands are largely training noise (inferred from the medians);
- the X03 values and the band-centring numbers were not recomputed independently: they cannot be from the npz
  (REPORT §14, executor's verifier), and F4's script compares only their input digests.

> *Draft (note).* In the six non-null universes tested (of 187), retraining with different seeds moves each
> universe's shift by a median 1.24–1.33 times the earlier seed-scan uncertainty. This training noise is part of the universe block as built, and it is not separated
> from the physical variation; we report its size and do not add a further term.

## D12. The declared conventions (DECISION-20261014 §2; production DESIGN §8; REPORT §3)

D1 says "under the conventions stated below". These are those conventions.

**Must carry:**
- each universe band's covariance is taken about the mean of its universes, with the constraint-weighted mean for
  Flux and 1/N normalization, not about the central value (the MAT universe law, a declared convention);
- band centres lie a median 0.12–0.50% of `E_U` (0.08–2.26 σ_band) from it (R9);
- the statistical block is the ddof-1 covariance about the replica mean (D2);
- the normalization is 1.4%, rank 1 (R6).

> *Draft (note).* Each systematic band's covariance is computed about the mean of its universes (constraint-weighted
> for the flux), with 1/N normalization, not about the central value; the band centres lie a median 0.1–0.5% from
> it. The statistical block is the covariance about the replica mean. A 1.4% normalization uncertainty is included as
> a rank-one block.

## Open after revision 3

- The revision-2 review is done (above). Revision 3's changes are checked by a fresh read-only reviewer before merge.
- KI-90 waits on the rebuilds.
- J2 is decided (S5 + C_PL). Joseph's remaining choice here is J4: the wording and register (D1's two versions, and
  D5's packet clause).

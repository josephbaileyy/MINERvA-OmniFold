# Draft disclosures: the 2D endpoint and its approximations (DRAFT revision 1, 2026-10-16)

**Prepared by** the paper-tighten lane, as director, for Joseph's review and the review with Ben. Adoption of any
wording is Joseph's (Stage F, J4). Nothing here is in a deliverable.

**CITABLE FOR:** the content each disclosure must carry, and its source record.
**NOT CITABLE FOR:** any number marked ⟨…⟩, which waits on the reviewed Stage C rollup (F3/F4) or the playlist
block (F8); any claim; any figure.

**How to read this.** Each item gives the required content, then a draft paper sentence. The note carries the full
version. Numbers already on `main` are quoted with their record. A ⟨placeholder⟩ is filled in revision 2, after F10.
The current paper text these would replace is `docs/analysis-note/paper_body.tex` §`sec:uq2d`
(l.253–306 at `main` `2aab43b5`) and the Fig. 1 caption.

## D1. The endpoint (narrower, construction complete)

**Must carry:**
- what is achieved: a reproducible central value and a matched uncertainty construction, under stated conventions;
- what is not achieved: independent validation of interval, bias or covariance claims;
- why: no independent production-size MC, no validated continuous nuisance generator, and only already-inspected
  independent-generator samples;
- that no coverage claim is made.

Source: DECISION-20261014 §2.

> *Draft.* The two-dimensional result is a reproducible central value with an uncertainty construction matched to its
> estimator under the conventions stated below. The construction has not been validated by independent
> pseudo-experiments: that would require simulation samples and a nuisance generator that are not available.
> We therefore make no claim about the coverage of its intervals, and goodness-of-fit values computed with it are
> indicative.

## D2. Coverage and KI-85

**Must carry:**
- the history: the earlier statistical band undercovered (VL169); it was rebuilt (VL170); post-hoc rescoring is
  descriptive and partly circular;
- the held-out re-test is deferred and was not pre-registered;
- the new production statistical block (S1, seed 42, three streams) has not been coverage-tested at all.

Source: KNOWN_ISSUES 85; paper §`sec:uq2d` (current text).

> *Draft.* The statistical block is a 300-replica bootstrap of data, signal and background simulation at the central
> value's training seed. Its coverage has not been tested. An earlier statistical band undercovered in closure tests
> and was rebuilt; ⟨one-sentence pointer to the note⟩.

## D3. Training-seed and learner dependence

**Must carry:**
- the seed main effect C08 is estimated from 5 seed triplets: rank at most 4, relative SE of variance about 71%;
- it includes the bootstrap × seed interaction's 1/20 share;
- X02 and X03 are reported, not added;
- the exact-split against LightGBM learner difference (median 0.98%) is in no block.

Source: production DESIGN §8 and §12; paper §`sec:repro2d`.

> *Draft.* A training-seed block, estimated from five seed settings, has ⟨median %⟩ median and is itself uncertain
> by about 70% in variance. The dependence on the learner (a per-bin median of 0.98% between the two estimators
> studied) is not included in any block.

## D4. G2: miss-row weighting in the universe unfolds

**Must carry** (DECISION-20261015-joseph-g2-carry §2, verbatim requirements):
- an approximation in the universe unfolds' miss-row weighting, not repaired;
- tested in `MaRES_0` and `Flux:23`, each at seeds 42 and 43;
- in neither was an effect resolved above the trainer's seed noise;
- an effect below trainer noise is not excluded, and 2 of 187 universes were tested.

> *Draft.* The systematic-universe unfolds approximate the weighting of events that fail reconstruction. Tests in two
> of the 187 universes, a vertex-model universe and the flux universe with the largest completeness change, each at
> two training seeds, resolved no effect above the training-seed noise. A smaller effect is not excluded, and the
> approximation is not corrected.

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
- diluted into the combined result, χ² p_∥ is 33.8 against VL175, where noise would give 1.8;
- every marginal z is below 0.7.

> *Draft.* Subsets of the data taken in different run periods are not mutually consistent within the other
> uncertainties: one period group's unfolded p_∥ distribution differs from the earliest periods by a step of about
> 7% near 8 GeV/c. The cause is not known, and these data cannot establish which period is correct. We carry the
> effect of this inconsistency on the combined result as an additional uncertainty block,
> ⟨construction, one clause⟩, of ⟨median %⟩ median and up to ⟨max %⟩ in p_∥.

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
- the unfolded J36 term is −0.084%.

Source: KNOWN_ISSUES J36; period-unfold REPORT.

> *Draft (note only; the paper may cite it).* Run periods are combined with a single exposure ratio rather than
> per-period ratios; the resulting bias is below 0.4% in every marginal bin.

## D10. Construction limits named in the endpoint decision

These are not yet worded. Each needs a sentence in the note, with a paper pointer:
- **KI-88.** Resolved by the seed-42 statistical block, conditional on F4.
- **KI-90.** Cell identity in the two publication consumers. Not yet verified for Stage F (checklist K3).
- **KI-91.** Flux ordering. The identity is established by a code chain (Stage B §2.1).
- **KI-92.** Rvp1pi is counted once, as Rvn1pi.
- **KI-93.** The July sweep is qualified by K1 PASS, which is conditional on a producer revision that was not committed.
- **KI-94.** Background statistics are propagated (R5).
- **Laterals.** One active-file unfold each, at seed 42. Trainer noise is not removed.
- **Ensemble size.** 300 replicas gives about 4% per-cell error on σ.
- **Flux block below the published one.** The reason is not established.

## Open for revision 2

- Fill every ⟨…⟩ from F3, F4 and F8, citing the source line.
- Write the D10 sentences.
- Check every draft sentence against the narrower endpoint: no "validated", "calibrated" or "covers".
- A fresh read-only reviewer checks the numbers against their records before Joseph sees revision 2.

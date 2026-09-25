# OUTCOME 2026-09-25 — the purity background method biases the unfolded highest-W cells by about −4% at nominal truth

**CITABLE FOR:** a development-level measurement, in end-to-end pseudo-experiments that reproduce the
analysis's own background treatment (`--bkg-mode purity`, per-event weight `max(0, d−b)/d` per 5D reco
bin), of a systematic unfolding bias at nominal truth, its localization, and the controls that tie it
to the background treatment. **NOT CITABLE FOR:** a corrected central value, a bias on the real data
(the real-data size depends on how well the MC background shape describes nature), a coverage verdict,
or any change to the adopted trunk `3d7465f6…`, whose covariance does not contain this effect.
**Status: development evidence, single campaign lane; independent verification pending** (route below).

Campaign: [`CAMPAIGN-s5c-20260924-index.md`](CAMPAIGN-s5c-20260924-index.md). All experiments use
development seeds; no validation seed has been run.

## 1. What was measured

End-to-end pseudo-experiments (`nd-unfolding/s5c_pseudo.py`): event-level pseudo-data from MC signal
(Poisson) **plus background MC events (Poisson)**, purity weights rebuilt exactly as production does
(the vectorized purity reproduces the production `measured_weights` to 0.0 on the real data, P2), then
the unfold. At **nominal truth** — the truth model equals the unfolding prior — the unfolded result
should reproduce the truth up to statistical noise.

| development study | experiments | highest-W column of the `(E_avail,W)` projection (EW5, 11, 17, 23, 29, 35) | other | inside 1σ / 1.96σ |
|---|---|---|---|---|
| D1 split, candidate F2 | 9 | **−3.5% to −4.1%** (±0.1%), 8–12 Tier-S σ | J80 +2.7%, J233 −1.8%; 53/153 functionals biased at > 4 SE | 53% / 73% |
| D1 no-split (whole MC as source and unfolding MC), F2 | 4 | −3.6% to −4.1% | the same pattern | 60% / 76% |
| D1 split, production estimator | 2 | −3.4% to −3.9% | the same pattern | 45% / 76% |
| **D2 no-split, F2, signal-only (no background, no subtraction)** | 4 | **none: largest mean residual 0.22% (0.6σ) over all 153** | 4/153 at > 4 SE | **79% / 97%** |

σ is the Tier-S statistical σ (0.07%–0.49% of each functional). Summaries:
[`state/s5c/d1/d1_summary.json`](state/s5c/d1/d1_summary.json); D2 products under
`/pscratch/sd/j/josephrb/s5c-20260924/runs/d2/`.

## 2. What it is, and what it is not

- **Not a half-split artifact** (identical without the split), **not specific to F2** (identical with the
  production estimator), **not events reconstructed outside the grid** (428 of 20.4 M, zero weight).
- **Tied to the background treatment:** removing the background (D2) removes the bias.
- **The subtraction itself is unbiased where it is binned.** For the same seed, the purity-subtracted
  pseudo-data summed per reco-W bin equal the signal-only counts to ≤ 0.05%; background is 1.3%–4.0% of
  signal below W = 3 GeV and **13% in the widest bin, W ∈ [3, 100) GeV**.
- **Consistent mechanism (inferred, not separately proven):** the purity weight is uniform inside each
  coarse reco bin, while the unbinned classifier resolves where background sits *within* the bin. A bin
  total that is right with a within-bin shape that is wrong distorts the learned density ratio; the
  effect concentrates where the bin is widest and the background fraction largest.
- **Why it matters beyond the campaign:** the pseudo-experiments use the analysis's own background MC
  and purity method, so the real 5D result plausibly carries a bias of similar sign and size in the
  highest-W cells, **not represented in any covariance**, including the adopted trunk's. A fixed-bias
  size on real data is not established here.

## 3. Consequences recorded

- The campaign's Tier-S statistical intervals would undercover at the highest-W functionals by
  construction (a 4% bias against a 0.35% σ). F2 development revision 1
  ([`state/s5c/contract-amendment-3-f2-revision-1.json`](state/s5c/contract-amendment-3-f2-revision-1.json))
  adds a linear closure-bias allowance estimated at nominal truth, with a futility rule, before any
  validation experiment.
- A method-level remedy (finer purity binning where background is concentrated, or injecting background
  with negative weights as the driver's `negweight-refined` mode does) changes the measurement procedure
  and is a costed next increment, not part of the bounded candidate families.
- Routed for independent verification and for a `KNOWN_ISSUES.md` entry at the campaign's delivery phase.

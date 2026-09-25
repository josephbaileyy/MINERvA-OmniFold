# OUTCOME 2026-09-25 — the purity background method biases the unfolded highest-W cells by about −4% at nominal truth (and the highest-E_avail × highest-W corner by +1.7%)

**CITABLE FOR:** a development-level measurement, in end-to-end pseudo-experiments that reproduce the
analysis's own background treatment (`--bkg-mode purity`, per-event weight `max(0, d−b)/d` per 5D reco
bin), of a systematic unfolding bias at nominal truth, its localization, and the controls that tie it
to the background treatment. **NOT CITABLE FOR:** a corrected central value, a bias on the real data
(the real-data size depends on how well the MC background shape describes nature), a coverage verdict,
or any change to the adopted trunk `3d7465f6…`, whose covariance does not contain this effect.
**Status: development evidence; independently re-measured (review round 2, §4), with corrections applied in §4.**

Campaign: [`CAMPAIGN-s5c-20260924-index.md`](CAMPAIGN-s5c-20260924-index.md). All experiments use
development seeds; no validation seed has been run.

## 1. What was measured

End-to-end pseudo-experiments (`nd-unfolding/s5c_pseudo.py`): event-level pseudo-data from MC signal
(Poisson) **plus background MC events (Poisson)**, purity weights rebuilt as production does, then
the unfold. (Inside the pseudo-experiment the purity is self-consistent — the background histogram equals
its float32 construction with Σ|diff| = 0.0 — but the P2 dump's float32 path differs from the float64
production weights by up to 0.137 on 25,357 real events; corrected wording, §4.) At **nominal truth** — the truth model equals the unfolding prior — the unfolded result
should reproduce the truth up to statistical noise.

| development study | experiments | highest-W column of the `(E_avail,W)` projection, EW5, 11, 17, 23, 29, 35 | highest-E_avail × highest-W corner, EW41 | other | inside 1σ / 1.96σ |
|---|---|---|---|---|---|
| D1 split, candidate F2 | 9 | **−3.5% to −4.1%** (±0.1%), 8–12 Tier-S σ | **+1.66% ± 0.08% (+6.1σ)** | J80 +2.7%, J233 −1.8%, EW40 +0.6%, total +0.30% (+3.6σ); 53/153 functionals biased at > 4 SE | 53% / 73% |
| D1 no-split (whole MC as source and unfolding MC), F2 | 4 | −3.6% to −4.1% | +1.68% | the same pattern | 60% / 76% |
| D1 split, production estimator | 2 | −3.4% to −3.9% | +1.87% | the same pattern | 45% / 76% |
| **D2 no-split, F2, signal-only (no background, no subtraction)** | 4 | **none: largest mean residual 0.22% (0.6σ) over all 153** | +0.02% | 4/153 at > 4 SE | **79% / 97%** |

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
  and purity method, so the real 5D result plausibly carries a bias of the same **sign** in the
  highest-W cells, **not represented in any covariance**, including the adopted trunk's. Its **size** on
  real data is not established and does not follow from these facts: in the real top-W reco bin
  data/(S+B) = 1.20 and B/data = 9.7% (11.6% B/(S+B) in the pseudo-data), and the real within-bin W
  shape departs from S+B by up to 1.5× at W > 8 GeV (review round 2, finding 5).

## 3. Consequences recorded

- The campaign's Tier-S statistical intervals would undercover at the highest-W functionals by
  construction (a 4% bias against a 0.35% σ). F2 development revision 1
  ([`state/s5c/contract-amendment-3-f2-revision-1.json`](state/s5c/contract-amendment-3-f2-revision-1.json))
  added a linear closure-bias allowance with a futility rule; review round 2 found that it widened every
  interval (predicted nominal coverage 0.93 / 0.99 against the 68% / 95% labels) and it is **superseded**
  by revision 2 ([`state/s5c/contract-amendment-4-f2-revision-2.json`](state/s5c/contract-amendment-4-f2-revision-2.json)):
  a nominal-truth bias **correction** of every functional with its standard error in quadrature.
- A method-level remedy (finer purity binning where background is concentrated, or injecting background
  with negative weights as the driver's `negweight-refined` mode does) changes the measurement procedure
  and is a costed next increment, not part of the bounded candidate families.
- Routed for a `KNOWN_ISSUES.md` entry, and to the purity-footing obligation already on record
  ([`docs/analysis-note/app_negweight.tex`](../analysis-note/app_negweight.tex) :64-75 documents the
  within-bin shape term; :327-345 records the purity-footing decision and its obligation to revisit the
  footing before submission; :395-410 cites a two-universe, one-iteration 5D histogram spot check as a
  reason the choice is safe). This outcome is direct end-to-end evidence against that safety argument.
  The cheapest real-data size estimate is a 5D purity-versus-`negweight-refined` comparison on the data.

## 4. Independent review round 2 and corrections (2026-09-25)

An independent review (isolated worktree at `4bdfa75e`, own code) re-measured every number in §1 to the
printed precision, found no way the pseudo-experiment construction itself creates the bias (background
draw, background path, purity histogram, weights and split, truth definition, clipping, integer counts:
each checked), and confirmed the D2 control. Corrections made here:

1. **The highest-W column has seven cells, not six.** The seventh, EW41 (highest E_avail × highest W,
   the deep-DIS corner), is biased **positive**, +1.66% (+6.1σ); J80 (E_avail ≥ 1.5 GeV, W ≥ 2.2 GeV) is
   +2.7%. The table now shows it; the heading, the commit message of `4bdfa75e` and amendment 3's
   "highest-W column is low by 3.5%-4.1%" are wrong for this cell.
2. **The paper's headline region.** `paper_body.tex` locates the positive central-value difference
   from Tune v1 "where both E_avail and W are large" — where this bias is positive — and states that
   closure tests "validate the central values". The first claim's size is not threatened by a bias of
   this magnitude (the corner's data/generator ratios are 1.54–1.61, `sec_eavailw.tex`), but the
   nominal-truth closure of the purity method fails at 6–12σ statistical, so the second sentence is
   not true of this background treatment. Routed as a KNOWN_ISSUES entry and to the deliverables.
3. **Mechanism (still inferred).** An ideal one-step classifier on half-width sub-bins, pulled back to
   truth, reproduces the sign and location (highest-W column −0.4% to −1.0%, EW41 +0.4%, total 0;
   control with sub-bins equal to the purity bins: exactly 0), but only 10–25% of the size, and its
   growth with E_avail is not seen in the data. Amplification over five iterations is plausible and not
   shown.
4. **Real-data size** is not "similar"; see §2 (finding 5).
5. **`state/s5c/d2/d2_summary.json` mislabelled its groups** (its `split_F2` group held the four D2
   no-split, no-background experiments; the other two groups were copies of D1's). Corrected to one group,
   `d2_nosplit_F2_no_background`.
6. **Pooling.** The `split_F2` group pools `p3_nominal_s1` (code `2f4432d6`) with eight D1 products (code
   `52f2740f`); the diff makes no physics difference at nominal truth.
7. **Adequacy of the grid for a nominal-derived correction.** `q3_given_eavail_w` preserves the
   (E_avail, W) marginal by construction, so for the M1 (E_avail, W) functionals its truth equals nominal;
   the E_avail tilt is ±10%. Stated in amendment 4 and to be stated with any Tier-S result.

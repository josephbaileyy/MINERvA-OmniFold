# DECISION 2026-10-15 — Joseph: the 2D budget gets a declared playlist-consistency uncertainty

**Recorded by** the paper-tighten lane, as director. On 2026-10-15, in his session, the director reported the
per-period unfold test to Joseph
([`state/2d-closeout/period-unfold-20261014/REPORT.md`](state/2d-closeout/period-unfold-20261014/REPORT.md)), with
this recommendation: if the numbers held on re-check, add a declared playlist-consistency uncertainty for the 1G–1M
shape in p_∥. The director said it was Joseph's decision, and also a topic for the review with Ben. Joseph answered,
verbatim:

> "I agree with your recommendation"

The sha256 of the answer text plus a final newline begins `fe52db28f5bd3f77`. The numbers did hold: the director
re-ran the frozen analysis and got byte-identical outputs (REPORT §6).

**CITABLE FOR:**
- the decision that the 2D uncertainty budget will carry a declared playlist-consistency term;
- what that term must cover, and the route to its construction (§2).

**NOT CITABLE FOR:**
- the term's size, shape or construction. These are designed in a later record and reviewed before use;
- adopting any covariance, product or claim. Stage F adoption stays Joseph's;
- a cause for the spread, or a statement about which run period is right;
- a compute grant, or any message outside this repository. Raising the question with Ben, or with MINERvA, is
  Joseph's act.

## 1. Why

- **1G–1M (P_B) against 1A–1F (P_A).** After unfolding, the double-ratio p_∥ step at 8 GeV/c is
  **+6.94% ± 0.41** (z 16.8), against +6.10% at reco level. χ² p_∥ is 381.8 against a noise expectation of 19.4.
- **Diluted into the combined result**, the shift has χ² p_∥ 33.8 against VL175, where noise would give 1.8. Every
  marginal z is below 0.7, so no single bin moves much. But the shift has a p_∥ shape that VL175 constrains tightly,
  so VL175 does not cover it.
- **1N–1P (P_C)** is a roughly 5% normalization difference, and VL175 covers it.
- **J36** is −0.084% and negligible.

## 2. What follows

- **The term must cover** the 1G–1M p_∥ shape. It should treat 1N–1P in the same construction, for completeness.
  It is a separate, declared block. It does not edit VL175 or the bound Stage C S5 rollup: it is added after S5.
- **Construction.** The director writes a short design record, which a fresh read-only verifier checks before any
  number is quoted. The design must declare before computing:
  - the construction;
  - raw or double ratio;
  - the reference period;
  - how 1F and the per-period MC responses are handled.

  The director's starting candidate is the covariance Σ_X b_X b_Xᵀ of the dilution shifts b_X = e_X (x_X/x_A − 1).
  These come from the test's outputs, at 0 node-h.
- **Disclosure.** At Stage F the term is described as an observed run-period inconsistency of unknown cause,
  carried as an uncertainty. It is not described as a measured systematic of a known source.
- **Review with Ben.** The test, and this term, join the topics for that review
  ([`DECISION-20261014-joseph-2d-endpoint-and-open-items.md`](DECISION-20261014-joseph-2d-endpoint-and-open-items.md),
  item 4).

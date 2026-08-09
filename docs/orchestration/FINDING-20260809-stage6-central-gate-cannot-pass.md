# FINDING 2026-08-09 — Stage 6's central-reproduction gate cannot pass, and it encodes the convention we rejected

**This is the yield of building the CANDIDATE without a verifier PASS.** The question that
justified the exercise was whether stages 4-6 have defects of their own. Answer, on real products:

- **stage 4 (build components)** — clean. 45 bands, 40 retained, all measured identities at or
  below 4.6e-14 against a 1e-9 rtol.
- **stage 5 (validate)** — **PASS**, eleven named gates, including the new
  `candidate_self_declares_non_adoptable`. Also clean.
- **stage 6 (project 5D→4D)** — **FAIL-CLOSED**, and not marginally.

Stage 6 had **never executed before** (repair-4 established that stages 4-6 were unreachable). This
is first contact.

**Nothing was changed to make it pass. No tolerance was touched.** Joseph re-specified the stage on
2026-08-09 (§6): the projection's own validity is GATED, the marginal-vs-independent comparison is
REPORTED without a verdict. That is removing a gate on a proposition the analysis does not assert,
not widening a tolerance — the measurement below is unchanged and is now published in full.

---

## 1. What the gate demands

`p4_project_4d.py:86` → `p4_lib.check_projection_nonmutation(..., rtol_central=CENTRAL_REL)` with
`CENTRAL_REL = 3.0e-2`, hardcoded and deliberately not a CLI knob.

It builds `M`, the W-marginalisation matrix, and requires

    max over 4D reported bins of  |M @ x5 − x4| / |x4|   ≤  3 %

where `x5` is the 5D central (`products/5d/xsec_5d_MEFHC_5iter_lgbm.root`) and **`x4` is the
INDEPENDENT 4D unfold** (`products/4d/xsec_4d_MEFHC_5iter_lgbm.root`).

So the gate asserts: *the 5D→4D marginal must reproduce the independently-unfolded 4D result,
bin by bin, to 3 %.*

## 2. What is measured

Diagnostic on central vectors only (the 42 GB candidate covariance is not involved):

| quantity | value |
|---|---|
| 5D reported bins / 4D reported bins | 10 694 / 4 830 |
| **reported gate failure** | `projection mutates central (max rel 1.00e+00)` |
| 4D reported bins receiving **zero** from the 5D support | **5** of 4 830 (0.10 %) |
| content of those 5 in the frozen 4D | 3.00e-46 … 2.09e-44 — **0.0000 %** of the 4D total |
| **excluding those 5**, median relative difference | **4.43 %** |
| p90 / p99 / max | **20.8 % / 33.9 % / 72.8 %** |
| **bins exceeding the 3 % tolerance** | **3 009 of 4 825 (62 %)** |
| bins exceeding 10 % | 1 295 |
| **integral agreement** `sum(M@x5) / sum(x4)` | **1.005578** (0.56 %) |
| 5D contributors per 4D bin | min 0, median 2, max 6 |

**The `1.00e+00` in the error message is a red herring.** It comes from the 5 zero-support bins,
which are numerically irrelevant. The real result is the line under it: the marginal and the
independent 4D disagree at a **median of 4.4 % and a p90 of 21 %**, while their **integrals agree
to 0.56 %**. That is the signature of a genuine shape difference between two estimators, not a
units error or a plumbing bug — and it is nowhere near a 3 % per-bin gate.

## 2b. The lateral hypothesis: tested and REFUTED, at two independent levels

Joseph proposed that the gap is the adopted lateral replacement — the independent 4D still carrying
the support-limited lateral while the marginal carries the selection-complete one built at stage 4 —
which would make the disagreement expected and quantified rather than novel. It is not that, and it
cannot be.

**Level 1 — the failing comparison contains no systematic content at all.** Listing the keys of
both operands:

| file | keys |
|---|---|
| `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | 13: `dataPOT`, `globalCompleteness`, `ndim`, and 10 central histograms |
| `products/4d/xsec_4d_MEFHC_5iter_lgbm.root` | 12: the same, minus `hXSec_W` |

**Keys naming a lateral band: NONE. Keys naming a universe or a covariance: NONE.** Both are pure
CV cross sections, produced 2026-06-04 and 2026-06-06. Laterals are systematic universes that live
in the covariance; the stage-6 check that failed is `M @ x5` vs `x4`, centrals on both sides. The
lateral convention cannot move either operand, so it cannot be the cause. Note this also means the
two proposed tests — restricting to non-lateral blocks, and substituting the support-limited
lateral — are not defined on this quantity: there are no blocks in a central vector.

**Level 2 — the disagreement reproduces with none of my code.** The 5D product carries
`hXSecND_dropLast_flat`, a W-marginal computed by the 5D producer itself in June:

| comparison | result |
|---|---|
| `M @ x5` vs the producer's own `hXSecND_dropLast_flat` | median **0.0**, p90 **0.0**, max **3.1e-16** |
| producer's own `dropLast` vs independent 4D | median **0.0444**, p90 **0.2091** |

The first line says the projection matrix is exactly right — it reproduces an independently
computed marginal to machine epsilon. The second says the 4.4 % / 21 % gap is a property of the two
*products*, reproducible without stage 6, without `build_projection_M`, and without anything this
lane wrote. (It also confirms the 5 orphan bins: `dropLast` has 4825 nonzero entries against the
4D's 4830, and 4830 − 4825 = 5.)

## 2c. What it actually is

Neither hypothesis on the table survives:

- **not lateral** — no systematic content in either operand (§2b);
- **not statistical** — `corr(log10 bin content, log10 |rel|) = +0.058`, and the median `|rel|` by
  content quintile is flat: 0.037, 0.044, 0.044, 0.068, 0.041. The estimator-noise reading predicts
  a clearly negative correlation and does not get one.

What the data show instead is a **coherent shape redistribution localized in `(eavail, q3)`**, with
the muon-kinematic axes nearly flat:

| axis | signed mean relative difference across the axis |
|---|---|
| `pt` (14 bins) | −0.017 → −0.031 → −0.038 → −0.034 → −0.010 → +0.006 → −0.024 (shallow) |
| `pz` (16 bins) | −0.027 → −0.030 → −0.031 → −0.029 → −0.022 → −0.023 → −0.020 → −0.012 (flat) |
| **`eavail` (7 bins)** | **−0.091 → −0.069 → −0.002 → +0.043 → +0.013 → −0.004 → −0.010** |
| **`q3` (7 bins)** | **+0.098 → +0.064 → −0.012 → −0.079 → −0.092 → −0.029 → +0.011** |

Sign fraction 0.4676, signed mean −0.024, integral ratio 1.005578.

## 2d. The W-mixing mechanism: tested and REFUTED — the correlation is REVERSED, not absent

My §2c inference was that `(eavail, q3)` is the subspace most correlated with the W axis the 5D
adds. Joseph sharpened it into a causal mechanism worth testing: a 4D unfold marginalizes over W
*at the unfolding step*, so its response matrix mixes W-populations with different migration while
the 5D resolves them — on which reading the 4.4 % is the 4D's integration bias and the marginal is
the *better* object, not merely the adopted one.

**It is not that.** Two predictions, both measured on the 5D product, both failed.

**P1 — |rel| should rise with a cell's W-width. It falls.** W-width measured on the marginal's own
weighting (`p_k ∝ w_k · x5[j,k]`), as both the occupancy `n_W` and the entropy `H`:

| Spearman | value |
|---|---|
| `(H, |rel|)` | **−0.223** |
| `(n_W, |rel|)` | **−0.198** |
| Pearson `(H, |rel|)` | −0.270 |

and monotone the wrong way across the whole range:

| `n_W` (5D cells feeding the 4D bin) | cells | median \|rel\| |
|---|---|---|
| 1 | 1309 | **0.0572** |
| 2 | 2036 | 0.0519 |
| 3 | 1027 | 0.0363 |
| 4 | 205 | 0.0215 |
| 5 | 76 | **0.0190** |
| 6 | 172 | 0.0264 |

By H quintile: 0.0684 → 0.0487 → 0.0458 → 0.0505 → **0.0278**. **Cells with the MOST W-mixing agree
BEST.** The mechanism predicts the opposite, and by a factor of three across the range.

**P2 — W-width should vary on (eavail, q3) and stay flat on (pt, pz). It does the reverse.** Range
of median-H across each axis's bins:

| axis | range of median H |
|---|---|
| **`pt`** | **1.532** |
| `q3` | 0.806 |
| `eavail` | 0.236 |
| `pz` | 0.044 |

The axis with by far the largest W-width variation is **`pt`** — the axis on which `|rel|` is
*flattest*. `eavail`, where the signed mean swings −9.1 % → +4.3 %, has the second-*smallest*
W-width variation. P2 is not merely unsupported; it is anti-correlated with the observation it was
meant to explain.

**Why the mechanism had little room to operate: W is largely redundant with (eavail, q3).** Over
the whole pt–pz plane, the number of W bins reachable per `(eavail, q3)` cell is a kinematic
triangle — median **3 of 6**, with the upper-left of the plane identically zero:

```
             q3 ->
eavail 0 :  2 2 3 3 3 4 6
eavail 1 :  2 2 3 3 3 4 6
eavail 2 :  2 2 3 3 3 4 6
eavail 3 :  0 1 2 3 3 4 6
eavail 4 :  0 0 0 1 3 4 6
eavail 5 :  0 0 0 0 0 3 6
eavail 6 :  0 0 0 0 0 0 6
```

and **69.3 % of 4D cells (3345 / 4825) span ≤ 2 W bins**. That is the expected consequence of
`W² = M² + 2M·E_avail − Q²`: given `(eavail, q3)`, W is nearly determined. So there is not much
W-population mixing available for a 4D unfold to get wrong, which is consistent with P1 failing —
though it does not explain the *sign*.

**A fourth hypothesis, also refuted.** If narrow-W cells are phase-space-boundary cells, the
gradient might be an edge effect. It is not: 3624 / 4825 cells (75.1 %) have an unreported 4D
neighbour, and their median `|rel|` is **0.0411** against **0.0543** for interior cells — edge cells
agree *better*, and median `n_W` is 2.0 for both.

## 2e. Where that leaves the explanation: four mechanisms excluded, none established

| hypothesis | verdict | evidence |
|---|---|---|
| lateral replacement | **refuted** | no systematic content in either operand (§2b) |
| statistical, keyed to bin content | **refuted** | `corr(log content, log \|rel\|) = +0.058`; flat quintiles |
| 4D mixes W-populations | **refuted, reversed** | Spearman −0.22; monotone the wrong way; P2 anti-correlated |
| phase-space edge effect | **refuted** | edge 0.0411 vs interior 0.0543 |

What survives as *description*, not mechanism:

1. a **coherent** shape redistribution in `(eavail, q3)` (signed means −9.1 % → +4.3 % and
   +9.8 % → −9.2 %), with `pt`/`pz` flat at −2 to −3 %; and
2. a component that **dilutes with the number of 5D cells feeding a 4D bin** — the `n_W` gradient
   above, roughly consistent with averaging (a 4D bin fed by one 5D cell inherits that cell's full
   deviation; one fed by four averages them), though not a clean `1/√n`.

Averaging cannot produce (1) — a coherent axis-dependent swing is not what fluctuation-dilution
looks like — so this is most likely a superposition of two effects. **I am not asserting that.**
Four mechanisms have been excluded and none established; the honest state is that the disagreement
is real, reproducible from the products alone, structured, and unexplained.

## 2f. DRAFT — reported estimator dependence (for the note, pending Joseph's review)

Written against the outcome the test actually produced. **This is a draft, not a landed claim**, and
it deliberately does not assert a mechanism.

> **Estimator dependence of the 4D result.** The 4D cross section is reported as the exact
> marginal of the 5D unfold over W. An independent direct 4D unfold, retained as a cross-check,
> agrees with that marginal in normalisation to **0.56 %** (integral ratio 1.005578) but differs
> bin-by-bin at a **median of 4.4 %** (p90 20.8 %, p99 33.9 %, max 72.8 %; 3009 of 4825 reported
> bins above 3 %). The difference is **not** a statistical fluctuation of either unfold — it is
> uncorrelated with bin content (Spearman +0.06) — and is **structured**: the signed difference
> swings from −9.1 % to +4.3 % across `E_avail` and from +9.8 % to −9.2 % across `q3`, while
> remaining flat at −2 to −3 % across `p_T` and `p_z`.
>
> We tested and excluded the natural explanation that a 4D unfold mixes W-populations with
> differing migration: the difference *falls* with the number of W bins a 4D cell spans
> (Spearman −0.22), and W-width varies most strongly along `p_T`, the axis on which the difference
> is flattest. W is in any case largely determined by `(E_avail, q3)` — 69 % of reported 4D cells
> span two or fewer W bins — leaving little W-mixing for a 4D unfold to misestimate. A
> phase-space-boundary effect is also excluded (edge cells agree better than interior cells).
>
> We therefore report this as an **unexplained estimator dependence of the 4D shape**, not as a
> quantified bias of either estimator, and we note that it is concentrated in the `(E_avail, q3)`
> region where the data-minus-generator excess is reported. The marginal is quoted because the 4D
> result is *defined* as the 5D marginal; the size of this dependence is a systematic-adjacent
> uncertainty on any 4D shape statement and is reported in full rather than summarised by a
> single number.

**Open, and it should be flagged as open:** whether this dependence should enter the 4D shape
uncertainty budget, and whether the `(E_avail, W)` excess claim needs a corresponding statement.
`app_statmethods.tex` already argues that a coherent 1–2 % OmniFold-vs-IBU shape difference becomes
a large χ² in this region; a 4.4 % median estimator dependence is larger than that and sits in the
same place.

## 3. Why this is a specification question, not a bug to fix

**The gate encodes the opposite of the convention adopted 2026-08-07.** That decision — pre-settled
and explicitly not to be reopened — is that **4D is the exact 5D→4D marginal, and the independent
4D unfold is a cross-check.** Under that convention the marginal is *definitional*: it is the
answer, and there is nothing for it to reproduce. This gate instead treats the independent 4D as
ground truth and the marginal as a candidate that must match it, which is the convention we did
not adopt.

The gate predates the decision. Nothing was wrong with writing it then; it simply was never
revisited, and because stages 4-6 never ran, nothing forced the contradiction into the open.

**Two readings, and I am not choosing between them:**

1. *The gate is mis-specified.* Under the adopted convention it should not exist in this form —
   at most it should RECORD the marginal-vs-independent difference as a cross-check statistic,
   with a bar set from what two OmniFold estimators at different dimensionality are actually
   expected to agree to, which is plainly not 3 % per bin.
2. *The disagreement is itself worth attention.* Median 4.4 % / p90 21 % between the deliverable
   and its cross-check is a real number about the analysis, whichever way the convention falls,
   and it has not been quoted anywhere before because this comparison had never run.

Both may be true. **Raising the tolerance is not on the table** — a 3 % gate that fails at a median
of 4.4 % is not repaired by widening it to 100 %, and "never raise a tolerance to clear a
mismatch" is a standing rule on this campaign.

## 4. A separate, smaller defect in the same stage

`p4_lib.build_projection_M` checks coverage in **one direction only**: every reported 5D bin must
map to a reported 4D bin (`"high reported bin {g} maps to non-reported low bin {glow}"`). It never
checks the converse — that every reported 4D bin receives at least one 5D contributor. Hence the
5 orphan bins, which reach the central check as exact zeros and produce a `rel = 1.0` that
completely masks the 62 %-of-bins result behind it.

This is independent of the convention question and is a defect either way: a one-directional
coverage guard on a bijection-shaped requirement. The right form fails at `build_projection_M`
with the count and the identity of the orphan bins, rather than surfacing 4 830 bins later as a
single misleading `max rel`.

**Rule.** When a guard reports `max`, the maximum is chosen by the worst bin, and a handful of
degenerate bins will always win it. Report a distribution — median, p90, count-over-tolerance —
beside any max, or the max becomes a mask for the finding. Here the max said "one bin is 100 %
off" when the truth was "62 % of bins are over tolerance".

## 5. Status of the products

`active_universe_5d/standard/candidate/` on scratch holds:

| file | |
|---|---|
| `std_final5_candidate.root` | 42.3 GB, 45 bands, sqrt_tr_syst 4.3513e-38, sqrt_tr_full 4.3576e-38 |
| `std_component_manifest.json` | carries `publication_gate_rejects_this: true` |
| `p4_standard_validation.json` | `RESULT PASS`, gate `candidate_self_declares_non_adoptable` present |
| `std_proj4d_candidate.root` | **not produced — stage 6 aborted** |

The candidate is **not adoptable and not quotable**. It was built without a `standard-p4-verifier`
PASS, by explicit instruction, and `p4_adopt_standard.py` refuses it outright. Producing it did
not shorten the path to adoption; it answered a question about stages 4-6, and the answer is that
two of the three are clean and the third cannot pass as specified.

## 6. The re-specification, as landed 2026-08-09

`check_projection_nonmutation` is replaced by two functions with disjoint jobs:

- **`check_projection_validity(C_high, M)` — GATE.** Symmetry, PSD, and `M C M^T` against a direct
  block-sum recomputation at `1e-9`. All recomputation identities; nothing compares against a
  separately-produced product. The block-sum leg is not a restatement of the PSD leg: `project()`
  is one matrix expression and a bug in it yields a matrix that is still symmetric and still PSD,
  so an independent route is what makes it a check.
- **`crosscheck_marginal_vs_independent(M, x_high, x_indep)` — REPORT, no pass/fail.** Returns
  median, p90, p99, max, sign fraction, signed mean, integral ratio and counts over 3/10/20 %, and
  is written so it cannot raise. Tested on a comparison the retired 3 % gate would have rejected.

`CENTRAL_REL` is **deleted, not raised.** There is deliberately no tolerance constant left to
re-tune, because the correct value is *none*, not *larger*.

The cross-check is returned as a **distribution rather than a max**, which is BEN-064 applied to the
replacement rather than only recorded about the original: a test asserts that one degenerate bin
among 100 perfect ones yields `max > 1e5` and `median = 0`, so the max can never again be the only
number a reader sees.

`build_projection_M` now validates coverage in **both** directions and fails at construction, with
the orphan indices in the message, rather than letting all-zero rows surface 4830 bins later as a
`max rel` of 1.0.
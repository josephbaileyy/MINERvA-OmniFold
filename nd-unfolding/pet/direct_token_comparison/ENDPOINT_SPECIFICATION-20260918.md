# Endpoint specification, for A4 ratification

**CITABLE FOR:** the predeclared endpoint, contrast set, denominator, degenerate-case
rule, and the three qualifications that travel with them.
**NOT CITABLE FOR:** any result. Nothing has been measured against this.

Written because Joseph held A4 pending three things: name the three primary contrasts
explicitly with **C−B among them**, specify the relative-improvement denominator, and
say how a near-zero baseline error is handled. $\delta = 10$ percentage points,
provisionally, as directed.

## 1. The four arms have identical input shapes

This matters before anything else, because it is what makes the contrasts
interpretable. Every arm feeds the same tensor shapes: 1 event token, **12** generic
slots, and the typed tokens. They differ only in *content*.

| arm | typed families | generic cloud | generic slots used |
|---|---|---|---|
| **A** incumbent | disabled | energy-ranked, **truncated** at 12 | 12 |
| **B** typed pooled | enabled, summed per family | truncated at 12 | 12 |
| **C** typed individual | enabled, one token per object | truncated at 12 | 12 |
| **D** aggregate overflow | disabled | top **11** kept, slot 12 is the **aggregate**: summed four-momentum, tail-mean auxiliary, distinct type code, explicit merged count | 12 |

Two consequences. **A and D have identical token counts**, so P2 below is an
information-only contrast with no cost difference by construction — revision 2 gave D a
thirteenth slot and would have confounded the two. And the merged count, which upstream
discards, is carried on the event token beside the per-family counts that are already
there, so no arm's feature width changes.

## 2. The three primary contrasts

| id | contrast | question | single factor changed |
|---|---|---|---|
| **P1** | **C − B** | **does individual-object routing beat family pooling?** | routing, with typed objects present in both |
| **P2** | **D − A** | does aggregate overflow beat energy-ordered truncation at the cap? | the cap's treatment, with typed objects absent from both |
| **P3** | **B − A** | do typed objects help at all, pooled? | the presence of typed objects, routing held pooled |

**P1 is Joseph's original question and is primary.** Each contrast changes exactly one
factor, so none of them is a composite.

**The three are read together, not in sequence** (added 2026-09-18). A null P3 does
**not** retire P1: P3 asks whether *pooled* typed objects help, so if pooling is the
wrong routing then P3 can be null precisely because of the effect P1 measures. P3 null
with P1 positive is a coherent and informative outcome — typed objects help only when
routed individually — and it is evidence *for* that reading rather than against it.
Likewise a positive P3 with a null P1 says typed objects help and the routing does not
matter. No contrast gates the reporting of another.

**C − A is derived, not a fourth test.** Because all three share one denominator (§3),
$(C-B) + (B-A) = (C-A)$ holds **exactly**, not approximately. C−A is reported as the
composite candidate with an additivity check: it is also measured directly in the same
runs, and the difference between the measured composite and $P1+P3$ must be zero to
floating-point. A non-zero difference means a bookkeeping defect, not an interaction.

**Multiplicity of testing.** Two-sided $\alpha = 0.05$ split three ways by Bonferroni →
**0.0167 per primary contrast**, $z = 2.394$. The secondary and derived quantities are
reported with intervals and carry no adoption authority.

## 3. The denominator

For a seed $s$ and regime $r$, with candidate $X$ and reference $Y$:

$$g^{X,Y}_{s,r} = 100 \cdot \frac{\mathrm{RMSE}^{Y}_{s,r} - \mathrm{RMSE}^{X}_{s,r}}{\mathrm{RMSE}^{A}_{s,r}}$$

The denominator is **always arm A's** final-iteration log-ratio RMSE for the *same seed
and the same regime* — never the contrast's own reference arm. So P1 is
$g^{C,B}$, P2 is $g^{D,A}$, P3 is $g^{B,A}$, all divided by $\mathrm{RMSE}^{A}_{s,r}$.
Positive always means the candidate is better.

Three reasons, all of which the alternative fails:

1. **One physical scale.** $\delta = 10$ then means "10% of the incumbent's error" in
   every contrast. With per-contrast denominators, a 10-point P1 and a 10-point P2 would
   be different absolute quantities and could not be compared or traded off.
2. **Exact additivity**, as above. Per-contrast denominators make $P1+P3 \neq C-A$ and
   turn a bookkeeping check into an unfalsifiable "interaction".
3. **One noise source instead of two.** The finished matrix's statistic divided by the
   pooled arm's own RMSE; every contrast then carried its reference arm's denominator
   noise. A single shared denominator is measured once per seed and its precision is
   gated in §4.

The numerator uses the frozen quantity `summarize_runs.py` already computes
(`:84-88`), at the final OmniFold iteration on the held-out split. Nothing about the
existing safeguards changes.

## 4. Near-zero baseline error

A ratio with a small denominator is the standard way this endpoint goes wrong, so the
rule is fixed in advance and has three parts. All of them use the bootstrap of the
held-out split that the pilot already runs — no extra training.

| part | rule |
|---|---|
| **4a precision gate** | a seed enters the relative endpoint only if the denominator's relative standard error is small: $\mathrm{se}(\mathrm{RMSE}^{A}_{s,r}) / \mathrm{RMSE}^{A}_{s,r} \leq 0.02$. Failing seeds are recorded as `denominator_imprecise`, excluded from the relative endpoint, and still reported on the absolute scale. |
| **4b hard floor** | if $\mathrm{RMSE}^{A}_{s,r} \leq 10 \cdot \mathrm{se}(\mathrm{RMSE}^{A}_{s,r})$ the ratio is undefined, not merely imprecise: the seed is excluded and counted. The reducer's existing refusal on an exactly-zero denominator stays as the last fail-closed line. |
| **4c pre-registered switch** | if more than **10%** of seeds in the primary regime are excluded by 4a or 4b, the primary endpoint switches to the **absolute** difference $\mathrm{RMSE}^{Y}-\mathrm{RMSE}^{X}$, with $\delta_{\rm abs}$ fixed at **10% of the pilot's median $\mathrm{RMSE}^{A}$** — a number frozen by the pilot *before* Stage 2 runs, so it cannot be chosen after seeing results. The relative endpoint is then secondary. |

Every exclusion is reported with its count and its seed. A silently dropped seed would
be a selection effect on the endpoint itself.

## 5. Decision rule, unchanged in shape

Per primary contrast, at $\alpha = 0.0167$ two-sided:

* **superiority** — the CI lower bound exceeds $+\delta$;
* **equivalence** — the CI lies entirely within $[-\delta, +\delta]$;
* **inconclusive** — the CI is wider than that band; the question is closed at the
  achieved resolution and the incumbent stands. No seeds are added after seeing results.

Sample size solves $n = \lceil (t_{1-\alpha/2,\,n-1} + t_{0.8,\,n-1})^2 s^2/\delta^2 \rceil$
iteratively on the pilot's between-training-seed sd, after test-sample uncertainty has
been capped at $\delta/4$ with inference rather than with seeds.

**No sd measured so far applies to this endpoint.** The finished matrix's 25.8 points
came from a different fixture, two arms rather than four, and a ratio to the pooled arm
rather than to arm A. It is a planning assumption for costing only. The sd that sizes
Stage 2 is the one the pilot measures here, and it may be larger.

## 6. Three qualifications that travel with every number

These are conditions on interpretation, not caveats to be dropped when quoting.

**Q1. Measured tail energy does not establish predictive importance.** A1 measures the
energy share carried by clusters beyond rank 12. That bounds how much the cap *could*
matter and is used to calibrate the fixture's tail signal share, but energy share and
predictive importance are different quantities and only the first is measured. P2's
magnitude is therefore conditional on the proxy, and neither P2 nor A1 may be cited as
evidence about how much the real reco tail matters for unfolding.

**Q2. Training-loss patterns are diagnostic clues, not proof of a mechanism.** The pilot
records train-loss parity next to closure because superposition-versus-variance predicts
different signatures. A signature is *consistent with* a mechanism; it does not
establish it. No mechanism is named on the strength of a train-loss pattern alone: at
least two independent signatures must agree, and otherwise the report says
**undetermined**.

**Q3. Bucketing must preserve event inclusion, weights, and fair training, and be
checked at the actual multiplicities.** The A2 route groups events by identical typed
counts so every batch is uniform and unpadded. Five invariants are enforced in code and
tested in both directions:

| id | invariant |
|---|---|
| I1 | the buckets **partition** the events: every event appears exactly once, none is dropped for not fitting |
| I2 | per-event weights travel with their event, and the weight multiset is preserved exactly |
| I3 | every arm performs the **same number of gradient steps** on the **same events** in the same epoch |
| I4 | the batch partition is a function of the **fixture only, never of the arm** — so arms A and D are bucketed too, even though their typed geometry is constant, and P3 is not contaminated by a batch-structure difference |
| I5 | the covered-geometry check runs over the **realized** bucket set at the measured multiplicities, not over a sample of it |

I4 is the one that would have been easy to get wrong: bucketing only the arms with
variable typed geometry would have given B and C a different batch structure from A and
D, and P3 would then measure batching as much as representation.

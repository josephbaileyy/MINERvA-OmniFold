# Proposal: one bounded experiment to settle the PET representation choice

**Revision 2, 2026-09-17**, answering Joseph's four requests: trace the production
representation and the arms end to end; justify the predictions by mathematics and
finite-training behaviour instead of asserting them; make the endpoint, margin,
equivalence bounds and sample-size rule mutually consistent; and price the source read
and the geometry gate. Revision 1's arms were wrong — see §2.4 — and are replaced.

**CITABLE FOR:** a predeclared design, its decision rule, its diagnosis procedure and
its costs.
**NOT CITABLE FOR:** any learning result. Nothing has been run. The only measurement
taken to write this is a local CPU cost probe (§7), which trains nothing to convergence
and touches no cluster resource.

**Approvals needed are collected in `DECISION_PACKET-20260917.md`.** Nothing is
launched.

---

## 1. The decision, stated as production alternatives

The note already states the production position exactly (`docs/analysis-note/sec_pet.tex:404-410`
at `66d35706`):

> "Our reco leg instead uses generic detector-geometry calorimeter clusters, has no
> reconstructed-object type embedding, and discards tokens beyond the common
> top-12-by-energy cap. ... Typed reconstructed objects and aggregate overflow tokens
> are therefore **prospective representation improvements, not features of the present
> estimator**."

So there is one incumbent and three prospective changes, and the decision is which — if
any — to adopt. Joseph's question ("individual typed-object tokens, Gregor's
aggregate-overflow approach, or other separately tested changes") maps onto exactly
these alternatives.

## 2. End-to-end trace

### 2.1 The production estimator today

| element | what it is | where measured |
|---|---|---|
| reco/data cloud | non-muon calorimeter clusters $(E_{\rm dep},{\rm pos}_{\rm view},z,{\rm view},t)$, **energy-ranked, truncated at 12**, zero-padded below | `sec_pet.tex:33-40,56-57` |
| truth cloud | final-state hadrons, same cap | `sec_pet.tex:41-47,56-57` |
| cap cardinality in code | `P12_TOKEN_COUNT = 12`; receipts require `num_part == 12` | `typed_descriptor_source_smoke.py:34`, `validate_g2_npz_receipt.py:113` |
| event object | muon variables, FiLM-conditioned, not a cloud token | `sec_pet.tex:48-55` |
| typed objects | **none**; no type embedding | `sec_pet.tex:404-406` |
| where the cap binds | truth: mean cardinality **4.57**, **2.31%** at the cap, twelfth constituent **0.09%** of retained energy. Reco: mean **11.09** in data, **11.15** in MC, distributions "pile up at the cap" | `sec_pet.tex:104-116,156-165` |

The asymmetry is the whole point: on the truth leg the cap is nearly inert; on the reco
leg it is the operating point.

### 2.2 The typed-object candidate

The typed-descriptor pipeline reads three families from `MasterAnaDev` and is
**uncapped** in our code — variable per-family counts, batch-local padding, no
truncation (`typed_descriptors.py`, `FAMILY_CONTRACTS` at `:652`). Their source
cardinalities are structurally different from the generic cloud's:

| family | source cardinality | branch that measures it |
|---|---|---|
| photons | **at most 2 by construction** — only `gamma1_*`, `gamma2_*` exist, presence set by an energy threshold of `1e-5` | `typed_descriptor_source_smoke.py:107-129`, threshold at `:35`, applied at `:871` |
| prongs | one scalar count per event | `n_prongs` |
| blobs | variable-length vectors; length is the count | `MasterAnaDev_BlobTotalE_sz` |
| generic clusters | variable-length; length is the pre-truncation count | `cluster_energy_sz` |

**None of these distributions is known to us today except the generic cloud's two
published means.** That is why the source read in §8.1 is load-bearing rather than a
nicety: it sets the fixture's multiplicities, and it is the only thing that makes
"representative" a measured word.

### 2.3 What each arm receives and discards

All arms share one model (`typed_token_comparison.py`): 1 event token + 12 generic
slots + typed tokens, **one** `MultiHeadAttention(4, 8)` layer at width 32, one FFN
(64→32), and the classifier reads **only the event token's output**
(`typed_token_comparison.py:177-200`). Both routings already pass the per-family
**counts** into the event token (`event_projection(concat([event, counts]))`, built at
width 16 = 13 event features + 3 counts), so multiplicity itself is never the
discarded quantity.

| arm | typed objects | generic cloud tail beyond 12 | tokens $T$ | receives | discards |
|---|---|---|---|---|---|
| **A** incumbent | none (families disabled) | **truncated** | 13 + 3 masked | top-12 clusters by energy, event features | every cluster past rank 12, entirely: its energy, its count, everything |
| **B** typed pooled | one token per family = $\sum_i \phi_f(x_i)$, then Dense(32) | truncated | 16 | the **sum of per-object embeddings** per family, plus the exact per-family count | per-object identity *within* a family: attention assigns one weight to the whole family, so no content-based selection among its members |
| **C** typed individual | one token per object | truncated | $13+K$ | every object separately; attention weights each one | nothing on the typed side |
| **D** aggregate overflow | none (families disabled) | keep top **11**, and spend **slot 12** on one aggregate token: summed tail four-momentum, the tail **mean** of the remaining channels, a distinct type code, and -- unlike upstream -- an explicit **merged count** | 13 + 3 masked, **identical to A** | the tail's exact energy sum, its mean position/depth/view/time, how many were merged | the tail's per-object resolution: dispersion, extremum, and any non-additive function of it; positions and timing survive only as an average |

Each arm is a **single-factor change from A**, and because D spends the twelfth slot
rather than a thirteenth, **A and D have identical token counts** — so the cap contrast
is information-only, with no cost difference to confound it.

The contrast set, the denominator, the degenerate-case rule and the three qualifications
that travel with every number are specified in **`ENDPOINT_SPECIFICATION-20260918.md`**,
which is what A4 ratifies. In brief: the three primary contrasts are **P1 = C−B**
(routing — Joseph's original question, and primary), **P2 = D−A** (the cap's treatment)
and **P3 = B−A** (typed objects at all); all three divide by **arm A's** RMSE for the
same seed and regime, which makes δ one physical quantity and makes P1 + P3 = C−A exact
rather than approximate.

### 2.4 Why revision 1's arms were wrong

Revision 1 put the cap on the **blob family** and varied blob multiplicity to make it
bind. That mismatched production twice over: the cap that binds in production is on the
**generic cluster cloud**, not on a typed family; and typed families are uncapped in our
code, so a cap there would have been an invention rather than a candidate. It also
omitted the actual incumbent — generic-only, no typed objects — so every contrast would
have been measured against a representation we do not run. Corrected above.

### 2.5 Does this address the production choice? Yes, and nothing transfers for free

**Corrected 2026-09-18.** Revision 2 claimed that direction transfers to production
while magnitude does not, and that noise-only generic slots make any measured effect an
**upper bound**. Both claims were wrong and are withdrawn.

*Direction does not transfer either.* In the fixture the 12 generic slots are
`rng.normal` noise and every bit of signal is typed
(`run_typed_token_comparison.py:105-107`). In production the generic cluster cloud
carries most of the information and typed objects add increments. A representation that
wins when typed objects are the only signal can **lose** when they are a supplement: if
typed tokens are largely redundant with the cluster cloud, per-object routing spends
attention capacity discriminating among near-duplicates. Sign reversal is available, not
merely a change of scale.

*"Upper bound" was unjustified.* The argument was that free attention capacity maximises
the typed effect. The opposite argument is equally available: in production the arms must
compete for a fixed attention budget against 12 informative tokens, and per-object
resolution may matter **more** there, not less, because the model has to tell similar
objects apart under pressure. There is no monotone relation between the fixture's
signal placement and production's, so neither bound holds.

What remains true is narrower and worth stating on its own: this experiment answers the
question **on this fixture**, at multiplicities matched to the measured ones, with each
arm a single-factor change. Transfer to production is a separate claim that this design
does not license, and a positive result here is a reason to run the matched comparison
on real inputs, not a substitute for it.

## 3. Why the finished null was expected — the argument, not the label

Revision 1 called it a "structural null". Replacing that with what can be shown:

**(i) Exact representability, both arms.** The injected target is
$\exp(0.4\tanh(t_0 t_1))$ where $t_0,t_1$ are the two prong times
(`run_typed_token_comparison.py:332-337`). The two prongs carry distinct `raw_pid`
values (3 and 8) and distinct `charge` and `mass`
(`run_typed_token_comparison.py:83-90`). A per-object encoder $\phi$ can therefore map
$(\text{pid}=3,t)\mapsto(t,0,\dots)$ and $(\text{pid}=8,t)\mapsto(0,t,\dots)$, so the
pooled family token $\sum_i\phi(x_i)$ equals $(t_0,t_1,\dots)$ exactly in two of its 32
coordinates, and the FFN then forms the product. **Pooling at $K=2$ loses no
information about this target.** The general statement is the sum-decomposition bound
of Wagstaff et al. (ICML 2019): exact representation of arbitrary set functions by
sum-pooling requires latent dimension $\geq$ set size. At width 32 that bound is
satisfied for any $K\leq32$, so at **production multiplicities expressivity is still
not the obstruction** — a point that cuts against the arm I would otherwise have
favoured.

**(ii) So the treatment was small by construction.** What actually differs between the
arms is (a) sequence length, 16 versus 17 tokens, and (b) whether attention can weight
the two prongs separately. The classifier reads one token after one attention layer, so
the read-out is $\sum_j \alpha_j V_j$ either way; the direct arm's $\alpha$ can depend
on each prong, the pooled arm's cannot. That is a second-order channel, and a measured
$|{\rm mean}| = 0.817$ points against a seed sd of 25.774 is what a second-order channel
looks like.

**(iii) What should degrade with $K$, and its signature.** Since expressivity is not the
limit, the mechanism that can make individual tokens win is **finite-width superposition
plus finite-training optimisation**: the pooled family token must carry $K$ objects in
one 32-vector and the read-out must disentangle them from a sum, while each object's
gradient reaches the encoder only through that sum. This predicts a gap that grows with
$K$ and, crucially, a **distinguishable signature**:

| observation | conclusion |
|---|---|
| training loss parity, closure gap | not expressivity — an optimisation or variance effect |
| training loss gap favouring C | superposition is binding at this $K$ and width |
| both, but gap $\leq$ seed spread | undetermined at this resolution; report the resolution |

The Stage-1 pilot therefore measures **train-loss parity alongside closure**, at $K=2$
and at the measured production $K$. That converts the mechanism from a story into a
measurement, and it is cheap because it needs no extra jobs — only extra recorded
fields.

## 4. Regimes, predictions, and how a control failure is diagnosed

### 4.1 The three regimes govern the generic tail

The regimes are reused from `OVERFLOW_SPECIFICATION-20260915.md` §4 so they are not
re-implemented, but they now act on the **generic cloud** tail, which is where the
production cap discards:

| regime | the target's tail term | prediction, with its reason |
|---|---|---|
| **R1** extensive | a function of $\sum_{\rm tail} E$ | D recovers most of it, because aggregation conserves the summed four-momentum exactly (measured: `OVERFLOW_SPECIFICATION` §2.2, $\Sigma E$ in = out in all six cases). A loses it, because it never sees the tail. **Not an exact tie**: the aggregate token enters through a nonlinear encoder, so recovery is up to approximation and optimisation error. |
| **R2** resolved | a non-additive function of the tail (dispersion or extremum) | D recovers only partly, because a sum plus a mean cannot express dispersion. The gap D→(an uncapped reference) measures what aggregation still loses. |
| **R3** head-only | zero | D ties A, because the cap is then harmless by construction, and the recorded cap-binding fraction must be non-zero while the tail's contribution to the target is zero. |

The routing contrast C−B is measured in **all three** regimes with an identical typed
channel, so its replicates pool across regimes — three times the seeds for free.
The existing `shuffle` null-control mode (`run_typed_token_comparison.py:340-343`) is
retained unchanged as the routing null: with the conditional destroyed, C−B must vanish.

### 4.2 The tail's signal share is measured, not chosen

The size of any cap effect depends on how much of the target depends on the discarded
tail — a free parameter that would otherwise make R1 a tautology (A cannot recover
information it never receives). It is therefore **pinned to the measured energy share
carried by clusters beyond rank 12** (§8.1), so the R1/R2 magnitudes carry production
meaning rather than the fixture author's choice. If that measurement is not authorised,
the share becomes a stated assumption and the cap contrast reports direction only.

### 4.3 Diagnosis of a control failure — replacing "invalidates the fixture"

Revision 1 said a non-tie "invalidates the fixture". That is too strong: a non-tie can
be noise, an implementation defect, or a real effect. The diagnosis is ordered and each
step is a measurement already available in the receipts:

**If R3 does not tie (D ≠ A):**
1. Is the separation inside the seed-spread envelope measured in Stage 1? If yes →
   noise; report with the achieved resolution, no fixture claim.
2. Is the recorded cap-binding fraction non-zero and the tail's target contribution
   exactly zero? If the tail contributes → fixture leak, and the target generator is at
   fault, not the arms.
3. Replace the tail values with independent noise and re-evaluate the **trained** models
   (no retraining, seconds of inference). If predictions move, the model is reading the
   tail → leak confirmed.
4. Train-loss parity: if D and A reach equal training loss but differ on the held-out
   split, it is a generalisation/variance effect, not information.
5. Only if 1-4 all fail is the fixture wrong, and then R1/R2 are not reported.

**If R1 does not show D recovering:**
1. Unit-check that the target's tail term is exactly a function of $\sum_{\rm tail}E$
   (a pure-function test, no compute).
2. Unit-check aggregation against `verify_upstream_overflow_semantics.py`'s measured
   properties — energy conservation and the tail-mean auxiliary — on our implementation.
   Failure here is our aggregate token, not the science.
3. Compare D against an uncapped reference run: if the uncapped arm also fails to
   recover, the target is not learnable at this budget and the regime is underpowered,
   not invalid.
4. Check the approximation channel: does D's recovery improve with width 64? If yes, the
   limit is encoder capacity, which is reportable and not a defect.

**If the `shuffle` routing null does not tie (C ≠ B):** the arms differ where no signal
exists, which means the comparison's common footing has broken — check the shared
initialization digests the reducer already verifies (`summarize_runs.py:66-68`) before
anything else.

## 5. Endpoint, margin, equivalence, and the sample-size rule — one consistent block

Revision 1 was inconsistent here: it declared an absolute-RMSE primary endpoint and then
a 10% relative margin, and powered from a relative sd. One scale now, throughout.

| item | definition |
|---|---|
| **per-seed statistic** | $g_s = 100\cdot(\mathrm{RMSE}^{A}_s-\mathrm{RMSE}^{X}_s)/\mathrm{RMSE}^{A}_s$, final OmniFold iteration, held-out split — the quantity `summarize_runs.py:84-88` already computes, sign positive when the candidate $X$ beats incumbent $A$ |
| **primary endpoint** | the paired mean $\bar g$ over seeds, per contrast |
| **margin** | $\delta = 10$ points on that scale — Joseph's provisional threshold, adopted |
| **contrasts** | co-primary: B−A, C−A, D−A. Secondary: C−B (routing), pooled across regimes |
| **$\alpha$** | two-sided 0.05 Bonferroni-split three ways → **0.0167 per contrast**; the secondary contrast is reported with its interval and no adoption authority |
| **superiority** | the contrast's 98.33% CI lower bound $> +\delta$ |
| **equivalence** | the contrast's 98.33% CI lies entirely within $[-\delta,+\delta]$ |
| **inconclusive** | CI wider than that band — neither branch |
| **sample size** | $n$ solving $n=\lceil (t_{1-\alpha/2,\,n-1}+t_{0.8,\,n-1})^2\, s^2/\delta^2\rceil$ iteratively, with $s$ the **pilot's between-training-seed sd of $g$** |

Two details that change the number and so are stated rather than left implicit. First,
$\alpha=0.0167$ gives $z=2.394$ and a normal-approximation constant of **10.469**, not
the 7.849 of a single unadjusted test. Second, the test is a paired **t**-test on
$n-1$ degrees of freedom, and at these small $n$ the $t$ quantiles are materially wider
than $z$, so the normal approximation under-powers by about three seeds; the rule above
uses $t$ and the table reports both. The superiority rule is stricter than the
half-width rule equivalence needs, so a design powered by it always lands in one of the
two decisive branches. The equivalence branch is the CI-inclusion rule, which is TOST at
$\alpha/2$ per side — deliberately conservative.

**The 25.8 is a planning assumption, not this endpoint's power.** It was measured on
the four-object fixture, with two arms, against a different statistic — a ratio to the
pooled arm rather than to arm A — at a multiplicity the experiment no longer uses. None
of those carry over. It is used here only to show what a plausible sd implies for cost;
the sd that sizes Stage 2 is the one the pilot measures for **this** endpoint.

| $s$ (points) | $n$ from $z$ | $n$ from $t$ (**used**) | interpretation |
|---:|---:|---:|---|
| 25.8 (**planning assumption only** — see below) | 70 | **73** | unaffordable; variance reduction is mandatory, not optional |
| 18.0 | 34 | 37 | affordable only by dropping a regime |
| 12.9 | 18 | **21** | the design target |
| 9.0 | 9 | 12 | comfortable |

## 6. Separating training-seed variance from test-sample uncertainty

$\operatorname{Var}(g)=\sigma^2_{\rm train}+\sigma^2_{\rm fixture}+\sigma^2_{\rm test}$,
and only the first two are reduced by more seeds. The pilot measures each separately:

| component | how it is isolated | what it costs |
|---|---|---|
| $\sigma^2_{\rm test}$ | bootstrap the **held-out split** on one fixed trained pair, 200 resamples, no retraining | seconds of inference |
| $\sigma^2_{\rm train}$ | retrain on **identical data and identical test split** with a different training seed | 1 extra job per regime |
| $\sigma^2_{\rm fixture}$ | a different fixture draw with the **same** training seed | 1 extra job per regime |

Two rules follow, both predeclared:

1. **Fix the evaluation first.** Choose $N_{\rm test}$ so that
   $\sigma_{\rm test}\leq\delta/4 = 2.5$ points. Since $\sigma_{\rm test}$ falls as
   $1/\sqrt{N_{\rm test}}$, this is bought with inference, not with seeds; the finished
   matrix used 250,000 test rows and 1,000,000 is affordable at inference-only cost.
2. **Then power on the residual.** $s^2 = \sigma^2_{\rm train}+\sigma^2_{\rm fixture}$
   after the evaluation term is capped, and $n$ comes from §5 using that $s$. Reporting
   an $n$ derived from a variance the evaluation contributed would over-buy seeds to fix
   a problem that inference solves.

If $\sigma^2_{\rm test}$ turns out to dominate the measured 25.8, the honest reading is
that the finished matrix was **evaluation-limited**, not seed-limited, and that is the
single most useful thing the pilot can return.

## 7. Cost, remeasured at the proposed multiplicities

Measured today, locally, on CPU, with the real model class and the real
`predict_ratio` path: `measure_cost_scaling.py`, 2,048 rows, batch 1,024, 15 timed
steps, **5 replicates interleaved across multiplicities**, receipt at
`local_validation/20260917-cost-scaling/cost-scaling.json`. This is a **scaling**
measurement; absolutes need a GPU probe.

| typed objects $K$ | pooled ms/step | direct ms/step | direct/pooled **training** | direct/pooled inference |
|---:|---:|---:|---:|---:|
| 4 (the finished matrix's geometry) | 27.2 | 27.8 | **1.061** [0.962, 1.124] | 1.281 [1.203, 1.309] |
| 8 | 25.7 | 32.2 | 1.232 [1.164, 1.312] | 1.283 [1.213, 1.342] |
| 14 | 28.1 | 38.1 | 1.420 [1.327, 1.531] | 1.382 [1.358, 1.401] |
| 20 | 27.5 | 46.7 | 1.636 [1.593, 1.720] | 1.416 [1.362, 1.523] |
| 32 | 30.0 | 65.1 | 2.099 [2.007, 2.241] | 1.646 [1.471, 1.740] |

Brackets are the observed min and max over the five replicates, not a fitted error.

**The anchor holds.** At the finished matrix's geometry the GPU-measured training ratio
of **1.118** falls inside the local interval [0.962, 1.124], and the GPU-measured
inference ratio of **1.283** sits on the local median of 1.281. That is what licenses
reading the rest of the column.

**Replicate ordering had to be fixed before any of this was quotable.** The first
version of the probe ran all replicates of one multiplicity before moving to the next,
and the $K=14$ training ratio then read 1.217 in one run and 1.479 in another — machine
drift landing on whichever configuration coincided with it. Interleaving the replicates
across multiplicities removed the inversion and produced the monotone column above. The
same failure mode is what the inference benchmark's alternating-arm rule exists to
prevent.

Two consequences for the decision:

* **Pooling's cost is nearly independent of multiplicity.** Its token count is fixed at
  16 whatever $K$ is, so only the per-object encoder work grows: 27.2 → 30.0 ms per step
  across an eightfold increase in objects, about **+10%**. Individual routing goes 27.8
  → 65.1 ms, about **+134%**.
* At production-plausible typed multiplicity the training premium is **1.23-1.42x**, not
  the 1.118x measured at $K=4$, and the inference premium **1.28-1.38x**. Whatever
  $\delta$ we set, arm C gets more expensive with exactly the multiplicity that would
  justify it.

The premium is **not** FLOP-driven: at width 32 the feed-forward block dominates and is
linear in token count, which predicts about 1.06x at $K=4$ — close to the local median
but well below the 1.118x the GPU actually charges, and the gap widens with $K$. The
excess is the direct route's ragged-to-dense repacking. That is why this had to be
measured rather than extrapolated, and why Stage 2's per-job sizing still comes from the
GPU probe in §8.3 rather than from this table.

**Campaign budget.** Per paired job the finished matrix cost 1990.75 s of wall =
**0.553 GPU-hours** at $K=4$ with two arms. Four arms at $K\approx11$ scale that to an
estimated **1.5-1.8 GPU-hours** per seed-job, to be replaced by the §8.3 probe's
measurement before Stage 2 is sized.

| stage | jobs | estimate | **hard ceiling** |
|---|---:|---:|---:|
| §8.3 GPU cost-and-gate probe | 2 | 0.6 GPU-h | **1 GPU-h** |
| Stage 1 pilot (3 seeds x 3 regimes, plus the variance-isolation jobs) | 15 | ~24 GPU-h | **30 GPU-h** |
| Stage 2 ($n=21$, 3 regimes) | 63 | ~104 GPU-h | **130 GPU-h** |
| counts-and-energy source read | CPU | ~2 core-h | **8 core-h** |
| storage | models, receipts | ~60 GiB | **120 GiB** |

**Total GPU ceiling: 161 GPU-hours.** Headroom measured today: the project has 60,049
of 180,000 GPU node-hours and 3,490 of 20,000 CPU node-hours (`iris project m3246`);
pscratch is at **80.1%** (16.02/20.00 TiB), so the storage cap binds and Stage 2 inputs
are built in-job. All m3246_g GPU work since 2026-09-01 totals **14.8 device-hours over
35 jobs**, an upper bound on this campaign's consumption against its 290-hour ceiling;
the "~229 remaining" line in `INFERENCE_BENCHMARK_SPECIFICATION-20260917.md` does not
reconcile with that and should not be quoted.

If Stage 2 does not fit, the response is to **drop R1, then R2**, never to weaken a
criterion, drop R3, or cut $n$ below the powered value.

## 8. Prerequisites, each scoped and priced

### 8.1 The source read: counts, plus cluster energy

**Scope.** The same mechanism already used and digest-bound by
`typed_descriptor_source_smoke.py`: two manifest-routed tuples, pinned by manifest
sha256 — `2d-unfolding/playlist_manifests/1B_Data.txt` (playlist 1B, data) and
`1A_MC.txt` (playlist 1A, MC) — read through the same fail-closed reader that refuses
any branch outside its predeclared list. The only change is the entry range: entries
`0..min(200000, tree size)` per file instead of `0..15`.

**Branches read, and nothing else** (all already inside `REQUIRED_BRANCHES`):

| branch | why |
|---|---|
| `cluster_energy_sz` | pre-truncation generic-cloud multiplicity — the distribution the fixture needs |
| `cluster_isMuontrack` | production uses **non-muon** clusters; without it the count is wrong |
| `cluster_energy` | the energy share carried beyond rank 12, which pins the tail's signal share (§4.2) |
| `MasterAnaDev_BlobTotalE_sz` | blob multiplicity |
| `n_prongs` | prong multiplicity |
| `gamma1_energy`, `gamma2_energy` | photon presence against the `1e-5` threshold |
| event-key branches | provenance only |

**Note the deviation from "counts-only", stated deliberately:** `cluster_energy` is a
per-object value, not a count. It is requested because without it §4.2's calibration is
an assumption. **If you prefer strictly counts-only, say so** — the consequence is that
the cap contrast reports direction but not production-transferable magnitude.

**Emits** histograms and summary statistics only: per-family count distributions, the
fraction above 12, and the rank-ordered energy share. No per-event records, no
positions, no timing, no truth, no weights, no muon kinematics beyond selection.

**Cost:** CPU only, ~2 core-hours, output < 50 MiB. **Not publication-critical:** it
reads the same files the note's own figure already characterises and produces a fixture
input, not an analysis product.

### 8.2 The variable-geometry gate: resolve it by removing the geometry

Varying multiplicity means padding and masking — the geometry your 2026-09-16 decision
recorded as a failed stress check and explicitly excluded from
(`STRESS_SCOPE_AUTHORIZATION-20260916.md`: the approval "does not extend / to future
variable-length or real-source training"). Two routes:

**Route 1, approved and implemented: multiplicity bucketing.** Group events into
batches of identical typed counts, so every batch is **uniform and unpadded** — the
property whose absence produced the recorded stress failure.

**One correction to how revision 2 put this.** Bucketing removes the *padding*; it does
not thereby make a *width* validated. The frozen guard pins one geometry and says so in
its own refusal — "the GPU gate never validated a padded or variable-length batch"
(`run_typed_token_comparison.py:161-166`) — so a uniform batch at an unvalidated width
is still ungated. Two consequences, both now implemented in
`four_arm_representation.py`:

* `WidthSetGuard` carries the set of widths a gate run **actually passed** and refuses
  anything outside it, so the experiment cannot train at a width no gate has cleared.
  Arms A and D take the one deliberate exemption, a **declared** all-families-disabled
  configuration, which must be declared rather than inferred.
* Every width the fixture can realize must therefore be gated, which is why the fixture
  samples typed multiplicity from a **quantile-matched ladder** of the measured
  distribution rather than its full support: with full support the realized width set is
  larger than can be gated, and the alternative — training only inside gated buckets —
  would silently drop events and break the partition invariant.

The five invariants (partition, weights, equal steps, arm-independent partition, checks
at the realized widths) are `ENDPOINT_SPECIFICATION-20260918.md` §6 Q3, enforced in code
and tested in both directions. The one that would have been easy to get wrong is
arm-independence: bucketing only the arms with variable typed geometry would have given
B and C a different batch structure from A and D, and P3 would then measure batching as
much as representation. Risk still to state: homogeneous-multiplicity batches change
SGD's batch composition relative to production, so bucket order is shuffled, batch size
is held fixed, and the `shuffle` null control is the detector — if bucketing biases
training, the null control stops tying.

**Route 2, fallback: re-scope the gate.** Re-measure the cross-device discrepancy
against padding width with a tolerance tied to gradient magnitude rather than a
fixed `rtol`, since `CROSSDEVICE_D1_RESULT-20260915.md` showed the existing gate's
rtol-scaled `allclose` fails on zero gradients and that padding alone contributes only
1.19e-07. Cost: ~0.5 GPU-h plus a decision from you to change a gate — which is why it
is the fallback.

Either way this is a **blocker on Stage 1**, not on agreeing the design.

### 8.3 One bounded GPU probe, before either stage

Two short jobs, ≤1 GPU-hour total, that measure rather than assume:

1. **Cost at the proposed multiplicities on the real device** — per-step and
   per-inference time for all four arms at the measured production $K$, so §7's local
   curve becomes a GPU number and Stage 2's sizing is measured.
2. **The bucketed-geometry preflight** — the existing cross-device gate run at the
   bucketed geometries, confirming Route 1 holds.

No training to convergence, no learning statistic, no closure number. This is the one
compute item I would ask for before the pilot.

### 8.4 Implementation deliverables, no compute

The aggregate-overflow token does not exist in our code and must be written: cap at 12,
keep the top 11 by energy, append the summed four-momentum with the tail-mean auxiliary
block, a distinct type code, and the explicit merged count upstream omits. Tests must
include mutation controls against
`verify_upstream_overflow_semantics.py`'s six measured properties, and the
opposite-direction case (a cap that never binds must leave the input bit-identical).
Arm A is expressible through the model's existing per-family `enabled` inputs
(`typed_token_comparison.py:141`, `run_typed_token_comparison.py:156`), but the geometry
guard refuses it today — `"a disabled family is not covered"` at
`run_typed_token_comparison.py:168` — so the guard needs to accept a **declared**
all-families-disabled arm while still refusing an undeclared one, tested in both
directions.

## 9. What this experiment still cannot establish

It compares four representations on a synthetic fixture. It does **not** compare our
complete pipeline against Gregor's — that is rung R6 of
`MATCHED_COMPARISON_LADDER-20260916.md`, which needs his architecture inside our closure
harness. It says nothing about real-data closure. A superiority verdict transfers in
direction but not magnitude for the typed contrasts (§2.5). And adoption here means the
production *representation* inside method development, never a publication claim,
covariance, or Gate-6 action.

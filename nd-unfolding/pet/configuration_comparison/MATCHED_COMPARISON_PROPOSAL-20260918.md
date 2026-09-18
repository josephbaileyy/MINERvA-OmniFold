# Matched comparison of two complete PET configurations: execution proposal

**CITABLE FOR:** a frozen design for selecting between our production PET configuration
and Gregor's, on our unfolding task.
**NOT CITABLE FOR:** any result — none exists — or any publication adoption.

**Nothing is launched.** This document asks for approval of one bounded campaign.

Supersedes the "test two components first" plan in
`CONFIGURATION_COMPARISON-20260918.md` §14. That plan is **retired**, and §14 of this
document says exactly what it retires and why.

---

## 1. The decision this is built to support

Joseph's requirement: a defensible choice between our final PET configuration and
Gregor's, with his adopted if it performs better, and with "no detectable difference"
unable to masquerade as "at least as good."

That forces three things the earlier design did not have: a **single endpoint on our
unfolding task** (not a synthetic fixture), **one engine running both arms** (so the
contrast is configuration and not framework), and a **non-inferiority margin** fixed
before any number exists.

---

## 2. The two configurations, pinned

### OURS — `pet-fullevent-fps-v1`, already frozen

| element | value | pin |
|---|---|---|
| representation | non-muon calorimeter clusters, 5 columns (E, pos, z, view, time), energy-ranked, top 12 | `dump_pointcloud_inputs.py:90-112` |
| event block | 13 muon/vertex features, FiLM conditioning | `fullevent_fps_dataloader.DEFAULT_EVT_FEATURES` |
| model | PET, 2 blocks, 2 heads, width 32, KNN K=3 over `(pos,z)`, LayerScale 1e-3 | `train_fullevent_nominal.py:403-407` |
| capacity | 47,041 / 46,913 trainable parameters | `receipts/model-capacity.json` |
| training | weighted BCE; Adam 1e-4 → 1e-5 fit-time anneal; batch 512; niter 3; epochs 8; 2 M subsample; seed 42 | `NOMINAL_SEED_POLICY`, `LR_POLICY_ANNEALED` |
| background | negweight-refined, fail-closed | `FULL_EVENT_FEATURE_CONTRACT.md` |

### HIS — assembled from `fc9a099d3c9c060f03cef293c294f9de4eb019cd`

The exact upstream configuration, read from the job generator rather than from the CLI
help, is the **`Transformer1` regression preset**:

| element | value | pin |
|---|---|---|
| model | `PointGlobalMixedViT`, `d_model` **128**, `depth` **4**, `n_heads` **8**, `mlp_ratio` **4.0**, `dropout` **0.0**, `attn_dropout` **0.0**, CLS token fused with EVT token | `submit_train_jobs.py:149-153`; `vit.py:226-332` |
| positional encoding | absolute Fourier MLP, `num_bands` 16, `max_freq` 10.0, over `X[..., :coord_dim]`, `coord_dim` **2** | `vit.py:249-251, 281-286`; `train.py:1740` |
| optimizer | **AdamW**, lr **1e-4**, weight decay **0.01** | `train.py:660-663, 2345-2352` |
| schedule | linear warmup **1000** steps then cosine decay to zero over `max_steps` **250000** | `train.py:682, 927-937`; `submit_train_jobs.py:124` |
| gradient clipping | **1.0** | `train.py:685, 2608-2615` |
| batch | **2048**, `grad_accum_steps` **1** | `submit_train_jobs.py:123, 125` |
| token cap | `max_particles` **33**, first-N at batch time, no re-sort | `train.py:470-474`; `dataloader.py:126-132` |
| representation | 10-column typed-object tokens, 8-class PID embedding (`cat_emb_dim` 16), 16 global features | `preprocessing.py:546-583`; `constants/dataset.py:1-5` |
| overflow | aggregation **OFF by default**; joint energy sort only above 150 objects | `preprocess_dataset.py:355-377` |
| initialization | random; `--use-pretrained` optional and **unavailable** | `B_provenance.out.md` items 2-3 |

**Pin caveat that must travel with any result.** `fc9a099d` is his repository's default
configuration at that commit. It is **not established to be the configuration behind
arXiv:2604.12364** — the repo has no release tags. So a result compares against *his
repository's Transformer1 preset*, not against *his published model*, until he supplies
the paper commit. That is prerequisite **R1** below and it is a question for him, not
compute.

---

## 3. Source prerequisites — the decisive constraint

**Every distinctive element of his representation is absent from our production input,
for every inventory.** Measured at `44142e8c`: the G2 dump writes `part_reco`,
`part_gen`, `reco_scalars`, `truth_scalars`, `reco_muon`, `reco_vertex`, `reco_view`,
`reco_time`, `pass_reco`, `pass_truth`, weights and provenance
(`dump_pointcloud_inputs.py:190-235`). There is **no** blob, prong, photon, PID, dE/dx,
Michel, per-type-energy-sum or overflow-telemetry key anywhere in it.

This is not a new finding. The audited Gregor-PET2 campaign reached it in July and
recorded each row as `absent/absent/absent/absent` across data, signal, background and
measured inventories (`GREGOR_PET2_OMNIFOLD_ASSESSMENT.md:249-255`, at `b65f9ff2`). I
re-measured it against current code rather than relaying it.

Two further constraints from that record, both still live:

* his public dataset rows are **MC-only**, so they cannot supply a data leg;
* a typed vocabulary built from truth categories is **direct leakage** and is excluded
  permanently; only reconstruction-derived types are admissible, and they must be
  **symmetric across data, signal and background** or the type code becomes an
  inventory label the step-1 classifier can exploit.

### Consequence: the comparison splits in two, and only one half is runnable

| tier | what it compares | prerequisite | status |
|---|---|---|---|
| **A** | **architecture + training recipe**, both arms on the frozen G2 input | none | **runnable now** |
| **B** | **representation**: typed objects, PID embedding, 16 globals, 33-token cap, aggregate overflow | a symmetric data/signal/background typed-object dump at a raised cap with overflow telemetry | **blocked** |

Tier B's prerequisite is a C++ event-loop deliverable. It was requested in
`FULL_EVENT_INTERFACE_REQUEST.md` §D, it has not been delivered, and it is owned by the
active-universe C++ owner — **not schedulable by me, and not costed here.** Anyone who
tells you the full head-to-head is affordable has not priced that dump.

**So the honest answer to "what is the minimum remaining work for a matched comparison"
is: Tier A is the matched comparison we can have, and it is worth having.** It holds the
representation fixed at ours and asks whether his model and recipe unfold our task
better. A Tier-A result is immediately actionable precisely because it needs no new
dump. What it cannot do is settle the representation, and no conclusion from it may be
written as if it had.

---

## 4. One engine, both arms

Both arms run inside **our TensorFlow MultiFold**. The prior campaign declined the
cross-framework comparison for the right reason — *"comparing their separate synthetic
means would confound framework, representation, and training engine"*
(`GREGOR_PET2_OMNIFOLD_ASSESSMENT.md:414-417`). Running both arms in one engine removes
two of those three confounds by construction, and Tier A removes the third by holding
the representation fixed.

**Why not use the existing PyTorch backend.** `nd-unfolding/pet2_torch/` (≈10,900 lines,
≈2,900 of them tests, at `b65f9ff2`) is real and reusable, and it does support multiple
iterations (`engine.run_iterations`, so my first reading of "one-iteration" as a hard
limit was wrong). It is still the wrong instrument here for three reasons: its
`model.py` is by its own declaration *"a clean implementation of general
point-edge/attention ideas… does not copy Gregor Krzmanc's or OmniLearned source"*, so
it is **not his architecture**; its `g2_adapter.py` is a fail-closed seam that never saw
the real payload; and using PyTorch for one arm and TensorFlow for the other
reintroduces the framework confound. It contributes one thing to this design: its
cross-engine fixed-logit ratio-convention fixture (`ratio_conventions.py`), reused as
safeguard S4.

### The port-fidelity gate — validity condition V-PORT

His architecture must be ported to Keras-2 to run in our engine, and a comparison
against a *misported* architecture is worthless. The port is therefore gated, not
trusted:

1. build his `PointGlobalMixedViT` in PyTorch at the §2 settings and the Keras port with
   identical layer shapes;
2. **transfer his weights into the port**, layer by layer, by an explicit name map;
3. require outputs to agree to **≤1e-5 max absolute difference in float64** on 1,024
   fixed random inputs including fully-masked and single-token rows;
4. require the parameter counts to be **equal**, not merely close.

Any failure stops the campaign at stage 1. **A port that cannot be shown to compute his
function is not his configuration**, and no amount of downstream care repairs that.

Two mappings are forced and must be stated in every result, because they are the places
where "his configuration" is not literally his:

* **Positional-encoding coordinates.** His Fourier MLP consumes `(η, φ)`. Our tokens
  have no per-token `(η, φ)`; they have `(pos, z)`. The port feeds `(pos, z)` — the same
  *mechanism* over the geometric coordinates our representation actually carries. This is
  a mapped choice, not an identical one.
* **Loss.** OmniFold requires weighted binary cross-entropy. His `log1p` Huber is an
  `E_avail` regression loss and has no counterpart in a reweighting classifier, so it is
  **not ported**. His arm keeps his optimizer, schedule, clipping and batch; the
  objective is necessarily ours. A result therefore compares his *architecture and
  optimization recipe*, never his *task*.

---

## 5. Endpoint

### Primary: powered injected truth-reweight recovery

The ordinary self-consistency closure is **unusable** for this purpose: it is an
identity check that *a constant estimator optimizes* — structural zero power, recorded
at `AUDIT-FINDINGS-20260728.md` and restated at `closure_fullevent_fps.py:4-9`. Choosing
it because it is cheap would be letting measurability pick the specification.

The primary endpoint is the **powered closure**, whose protocol was predeclared on
2026-08-05 before any run and is reused **unchanged**:

* clipped exponential tilt in truth `pT`, amplitude **0.35**, clip `|z| ≤ 3`, applied to
  truth-passing rows only, rate-preserving;
* two **disjoint** deterministic halves, **2,000,000** each, split seed **7**;
* step-1 rows `pass_reco & pass_truth` on both sides;
* the statistic is **recovery** `= 1 − E_w[|1 − r_b|]` over the 285 extended-grid cells.

Source: `closure_powered_truth_reweight.py:10-33`. Reusing a protocol frozen six weeks
ago, by someone who could not have known this comparison would use it, is the strongest
available guarantee that the endpoint was not chosen to suit an answer.

**The production baseline on this endpoint is measured:** recovery **0.5126033** (job
`56552326`, independently finalized by `56562169`), against the adopted criterion
**0.494582** (`= 0.80 × ceiling 0.618228`, CLM-012), margin **+0.0180209**.

### Mandatory decomposition, reported alongside — not co-primary

BEN-038 measured that this statistic's gap to its ceiling is **97.8 % scatter and only
−0.0019 bias** on our baseline, because an absolute value turns symmetric per-cell noise
into a one-sided penalty. Its rule is to split before diagnosing. So each arm also
reports the **signed response** `E_w[r]` and the **scatter penalty**
`E_w[|1−r|] − |1−E_w[r]|`.

This matters for attribution, not for the decision: an arm can win the aggregate purely
by being less noisy per cell. That is a genuine advantage and will be **named as such**
rather than reported as better shape transport.

### Safeguards — all must pass for either arm to be recommended

| id | safeguard | criterion |
|---|---|---|
| S1 | normalization | `|dev|` within the adopted `FROZEN` bound for both arms |
| S2 | null-power control | the ordinary identity closure passes for both arms, confirming plumbing without being read as power |
| S3 | directional control | omitted-muon stress closure moves in the correct direction for both arms |
| S4 | ratio convention | both arms reproduce the fixed-logit odds fixture (`pet2_torch/ratio_conventions.py`) |
| S5 | realized LR | each arm's optimizer-verified realized rates match its declared policy, as production already enforces |
| S6 | port fidelity | V-PORT above |
| S7 | no leakage | `TRUTH_ELIGIBLE_FEATURES` holds; his arm gains no truth-derived input |

---

## 6. Non-inferiority margin

**δ = 0.018 recovery points**, absolute, on the primary endpoint.

**Justification, which is the point of the number.** 0.0180209 is exactly the margin by
which our production estimator currently clears its adopted acceptance criterion. A
deficit larger than δ would mean that adopting our configuration over his costs the
entire margin by which the estimator currently passes its own gate — i.e. it would move
production from clearing the criterion to sitting at or below it. That is a
decision-relevant quantity, not a round number.

Three cross-checks that δ is neither trivial nor unreachable:

* it is **14.7×** the closure's own measured run-to-run spread of **1.226e-3** (job
  `56611837`), so it is far above noise;
* it is **2.9 %** of the reference ceiling 0.618228 and **3.5 %** of the measured
  recovery, so it is a small relative effect — the margin is strict, not lenient;
* the LR-anneal adoption knowingly paid **−0.0342** of recovery for a 33-point
  normalization repair, so effects of order δ are ones this campaign has previously
  treated as material.

**The scatter figure 1.226e-3 is a same-configuration repeat spread, not seed-to-seed
scatter.** It bounds δ from below; it must not be used to size the campaign. Sizing uses
seed scatter, which the pilot measures (§8).

---

## 7. Freeze, before any final number exists

One file, `MATCHED_FREEZE-<date>.json`, written and committed **before** the final stage
launches, carrying: both arms' complete configurations and their file digests; the
injection protocol and split seed; the evaluation sample identity; δ; α; the decision
rule verbatim; every safeguard threshold; the tuning protocol and its trial list; and
the stop conditions. Its sha256 is verified by the launcher, exactly as
`VALIDATION_CRITERIA-20260918.json` (`abccd88b…`) was for the tail validation.

**Evaluation samples.** `G2_FPS_MEFHC_P12.npz`, sha256
**`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`**, 9,897,374,636
bytes, 49,152,885 signal / 4,116,128 data / 564,591 background rows, `num_part` 12,
produced 2026-07-19 by job 56120687, receipt status PASS. The two disjoint 2 M halves at
split seed 7 are the **final evaluation sample**; tuning uses a **third, disjoint** slice
and never touches either half. A tuning trial that reads an evaluation half voids the
stage.

The criteria are **not relaxed after seeing failures.** The tail validation established
that precedent by leaving three widths unreleased rather than loosening a criterion I
had frozen, and the same rule binds here.

---

## 8. Tuning budget, equal by construction, and sizing

**Tuning.** Each arm gets **exactly 4 trials**, on the disjoint tuning slice, scored by
the same endpoint. Each arm's own published/adopted setting is **trial 1**, so neither
can be made worse than its own default by a bad grid.

| arm | trial 1 | trials 2-4 vary |
|---|---|---|
| ours | the adopted `NOMINAL_SEED_POLICY` + `LR_POLICY_ANNEALED` | base LR, anneal point, batch |
| his | `Transformer1` preset at §2 | lr, weight decay, warmup fraction |

Equal trial counts, equal budget per trial, one grid axis count each. The winner of each
arm's 4 is that arm's frozen configuration and cannot be revisited.

**Sizing.** Paired on estimator seed; the statistic is the paired difference in recovery.
Planning prior for seed scatter: **σ ≈ 0.008**, taken from the 48-seed spread of a
closure-adjacent deviation statistic (CLM-010: mean 0.014256, sd **0.008023**). Paired
sd σ_d ≈ 0.011. At one-sided α = 0.025 and 80 % power for δ = 0.018,
`n = (1.96+0.84)² σ_d²/δ² ≈ 2.9`, so **8 paired seeds carries comfortable margin** and
tolerates σ_d up to ≈0.019 before the margin is lost.

**σ = 0.008 is a planning assumption from an adjacent statistic, not measured power for
this endpoint.** The pilot replaces it. The last campaign's error was to let a
planning scatter stand in for a measurement, and it cost 175 GPU-hours of illusory
affordability.

---

## 9. Stages, costs, gates

Per-evaluation cost is taken as **≈1.5 GPU-h** (one nominal train ≈1.1–1.3 GPU-h per
`FULL_EVENT_FEATURE_CONTRACT.md` §estimated cost, plus injection and scoring). **This is
an estimate and stage 2 exists to replace it with a measurement.**

| stage | work | cost | gate to proceed |
|---|---|---:|---|
| 1 | port his architecture to Keras-2; V-PORT fidelity gate; tests | **0.5 GPU-h** | V-PORT passes at ≤1e-5, equal parameter counts |
| 2 | cost calibration: one evaluation per arm | **3 GPU-h** | measured per-evaluation cost replaces the estimate; stage 4-5 re-sized |
| 3 | tuning: 4 trials × 2 arms on the tuning slice | **12 GPU-h** | both arms produce a frozen configuration; no evaluation half touched |
| 4 | variance pilot: 4 paired seeds × 2 arms | **12 GPU-h** | **measured σ_d admits δ = 0.018 within stage 5's ceiling** |
| 5 | final matched comparison: 8 paired seeds × 2 arms | **24 GPU-h** | — |
| | contingency (one stage repeated) | **18 GPU-h** | |
| | **ceiling requested** | **≤70 GPU-h** | |

Against the campaign's 290-hour ceiling with **16.0 consumed**, this leaves ≈204 hours
unspent. CPU cost is negligible. No new storage: the input already exists.

**These are stage ceilings inside the existing aggregate, not additions to it.**

---

## 10. Decision rule, frozen here

Paired differences `d_s = recovery(ours, s) − recovery(his, s)` over seeds `s`; `CI` is
the two-sided 95 % interval on `mean(d)`.

| condition | conclusion |
|---|---|
| `CI` lower bound **> −δ** and all safeguards pass for both arms | **Recommend OURS.** Non-inferior to his by a margin that matters, at equal tuning, on our task. |
| `CI` upper bound **< −δ** and his safeguards pass | **Recommend HIS.** His configuration is materially better by more than δ; adopt it for method development. |
| `CI` contains **−δ** | **Inconclusive. No selection is supported.** Report the interval, state that non-inferiority is *not* established, and name the incumbent as a **provisional engineering choice** on cost and continuity — explicitly not a demonstrated result. |
| any safeguard fails for an arm | that arm is **not recommendable** regardless of its endpoint value; if both fail, no selection. |

Two rules that close the loopholes Joseph named:

* **"No detectable difference" is not "at least as good."** A `CI` that merely contains
  zero decides nothing. Only a lower bound strictly above −δ licenses "ours".
* **Ours does not win by default.** If the interval is wide, the incumbent is retained as
  an engineering choice and the record says the comparison failed to decide. Retention
  and demonstration are different words and will not be interchanged.

Also frozen: the result is reported **whether or not it favours us**, and a Tier-A
conclusion is written as a conclusion about architecture and training recipe. It may not
be written as "our configuration is better than Gregor's" — the representation half is
untested.

---

## 11. Stop conditions

Execution stops, and I report, on any of:

1. **V-PORT fails** — his architecture is not faithfully ported; nothing downstream is
   interpretable.
2. **The pilot's measured σ_d cannot resolve δ = 0.018** inside stage 5's ceiling. Say so
   and stop; do not raise the ceiling and do not widen δ.
3. **Any safeguard S1–S7 fails** and is not attributable to a defect I can fix inside the
   contingency.
4. **Limits exhausted** — 70 GPU-h, or the per-stage ceiling.
5. **A change to the endpoint, δ, the decision rule or the samples becomes necessary.**
   That is a new approval, not an amendment I make mid-campaign.
6. **A repaired submission counts as a retry** and consumes the stage's budget.

No automatic retries. A technical failure is reported, not silently relaunched.

---

## 12. What is still not decidable, and will be said plainly

Even on a clean Tier-A pass, these remain open and the final deck will lead with them as
conditions:

* **the representation** — blocked on the typed-object dump (§3);
* **his published configuration** — `fc9a099d` is not established to be the paper commit
  (R1);
* **pretrained initialization** — checkpoints unreachable, so the arm of his work most
  likely to matter is untestable (R2);
* **the ceiling 0.618228 is a reference curve, not a proven bound** (CLM-012 caveat (i);
  BEN-038 measured a band at `E_w[r] = 1.0333`), so recovery fractions are relative to a
  reference;
* **one endpoint** — powered-closure recovery is the quantity we can measure with power,
  not the cross section.

---

## 13. Prerequisites I cannot resolve with compute

| id | prerequisite | who | blocks |
|---|---|---|---|
| R1 | the exact commit and configuration behind arXiv:2604.12364 | ask Gregor | whether a result speaks about his *published* model |
| R2 | pretrained checkpoint files and their hashes | ask Gregor | any pretrained arm |
| R3 | his `E_avail` definition in writing | ask Gregor | any numeric comparison against his reported values |
| R4 | symmetric data/signal/background typed-object dump, raised cap, overflow telemetry | C++ active-universe owner | **all of Tier B** |

R1–R3 are questions, not compute. **I have not contacted anyone**; sending them is
Joseph's call.

---

## 14. What this retires

The earlier plan proposed a coverage measurement as the gate on three borrowings, plus
single-factor arms. **Under a head-to-head on the real endpoint, most of that is
unnecessary**, and saying so is part of "don't start another sequence of isolated
component experiments":

| earlier item | status now |
|---|---|
| typed-object energy coverage as a **gate** | **retired as a gate.** It was a proxy for "will the typed representation help"; Tier B measures that directly. Coverage survives only as a diagnostic *if* R4 lands. |
| single-factor arms for energy sums, aggregation, routing, capacity | **retired.** They are inside the two configurations being compared, and the earlier note that they interact is the reason to compare complete configurations instead. |
| "test aggregation before routing" | **retired.** A priority ordering among components is moot once the comparison is between complete configurations. |
| the synthetic four-arm fixture and its 25.8-point scatter | **retired as a basis for sizing.** Replaced by the real endpoint and its own measured scatter. |
| the unreleased-V5-widths decision | **no longer on this path.** It gated the synthetic pilot, which this proposal does not run. It remains open for that other lane. |

One thing is **not** retired: the deck's corrected component inventory remains the record
of *what differs and why it might matter*, and stage 3's grids are drawn from it.

---

## 15. Approvals requested

| # | approval | ceiling |
|---|---|---|
| **A** | stages 1-2: port, fidelity gate, cost calibration | 3.5 GPU-h |
| **B** | stage 3: equal-budget tuning, both arms | 12 GPU-h |
| **C** | stage 4: variance pilot | 12 GPU-h |
| **D** | stage 5: final matched comparison, conditional on stage 4's gate | 24 GPU-h + 18 contingency |
| **E** | ratify δ = 0.018, the endpoint, the decision rule and the freeze before stage 5 | — |
| **F** | send R1-R3 to Gregor | — |

A, B and C can be approved together without committing to D: stage 4's gate is what
decides whether D is worth its cost. **If stage 4 says the question cannot be resolved
within the ceiling, the honest deliverable is that sentence**, plus the incumbent
retained as a provisional engineering choice.

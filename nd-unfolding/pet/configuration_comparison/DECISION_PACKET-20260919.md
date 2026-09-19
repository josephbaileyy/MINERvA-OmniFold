# Scientific decision packet: our PET configuration against Gregor's

**CITABLE FOR:** the proposed design of the matched comparison, and the separation
between what is chosen and what is measured.
**NOT CITABLE FOR:** any result, any ratified threshold, any adoption. Every
threshold below is **UNRATIFIED** and is written as a proposal.

PET remains method development. Nothing here touches publication adoption,
covariance, systematics, central values or Gate 6, and nothing here discharges
`OI-71`.

---

## 0. Implementation state, so the decisions land on something real

His backbone now runs in our engine. `PET2Port` reproduces `network.PET2` in
`mode="classifier"` at the V1-paper setting — `use_int=False, local_int=False`,
read off `plot_configs/V1Paper.json` and the `OLS`/`OLS_RW`/`OLM_FB` branches of
`submit_train_jobs.py`, **not** PET2's class defaults of `True`/`True`.

All six port checks hold (`receipts/PORT_CHECKS-20260919.json`). **The receipt
records 1,024 forward rows and 64 gradient rows** — P-2 and P-5 run on the 1,024,
P-3 and P-4 on the 64, and "at 1,024 rows" as I wrote it before was a single figure
covering two different populations:

| check | result |
|---|---|
| P-1 inventory | 176 tensors, 2,758,702 parameters, identical by name, shape and traversal order |
| P-2a float32, unmodified upstream, 1,024 rows | cross-engine 3.7e-7 against a limit of 5.3e-7 taken from the REFERENCE's own float32 deviation, so a defect in the port cannot widen its own band |
| P-2b float64, 1,024 rows | 6.7e-16 against a 1e-5 tolerance |
| P-3 gradients, 64 rows | 5.1e5 times closer than a mutant port with one structural change |
| P-4 one AdamW step, 64 rows | 4.0e8 times closer than the nearest off-the-shelf optimizer |
| P-5 masking, 1,024 rows | padded slots change the output by exactly 0; pad crowding begins only at coordinate magnitude ~1000, and our clouds are O(1) |
| P-6 | repeatable and reload-identical, bitwise |

The vendored `MultiFold` loop itself has been driven with it on both step schemas
(`receipts/OMNIFOLD_STEP_EXERCISE-20260919.json`): 5 features / 13 globals /
coord `(1,2)` at reco and 8 / 2 / coord `(5,6,7)` at truth, under **his** optimizer
rather than the engine's hardcoded Adam, with the `OI-125` fold-forward recorder
attached and the end-of-run ratio recorded rather than reconstructed.

**Nothing in that is a performance claim.** It means the comparison can be run once
the decisions below are made and R2 lands — not that either arm is better.

---

## 1. The dependency graph, corrected

The previous graph let tuning and the variance pilot sit on work that cannot supply
them. **The pretrained checkpoint is a prerequisite of the pretrained arm's tuning
and of its variance pilot, not only of its final runs.**

```
implementation ....... port + P-1..P-6 + recorder + adapter      DONE, no dependency
        |
        +--> scratch arm (OLS_RW)  ......... runnable today
        |        `-- supports: implementation checks, cost calibration, plumbing
        |        `-- CANNOT supply: the pretrained arm's selected settings
        |                           the pretrained arm's variance estimate
        |
        +--> pretrained arm (OLS, OLM_FB) .. BLOCKED on R2 checkpoints
                 |
                 +--> tuning, 4 trials      requires R2
                 |        |
                 |        +--> variance pilot, 4 paired seeds    requires R2 + its own tuning
                 |                 |
                 |                 +--> seed count n            from the pilot's sigma
                 |                          |
                 |                          +--> FINAL COMPARISON
```

**Why scratch cannot substitute, stated as the two specific claims it cannot
support.** A hyperparameter selected on a randomly initialised backbone is not the
selection for a pretrained one: fine-tuning a transferred representation is the
regime where the learning rate and schedule differ most from training from scratch,
which is the entire subject of his paper. And seed-to-seed spread is a property of
the initialisation: a scratch arm varies over random inits, a pretrained arm varies
over data order and fine-tuning noise from one fixed starting point, so a sigma
measured on the first is not an estimate of the second and would size the final
comparison wrongly in an unknown direction.

**What scratch work legitimately does:** exercises the plumbing, validates the port
end to end, and prices the arms. Those are the uses it is put to here.

---

## 2. Injection and scoring domain

| id | item | proposal | status |
|---|---|---|---|
| **U1** | injected variable | truth `E_avail`, `truth_scalars` column 2 | **unratified** |
| **U2** | tilt amplitude / clip | 0.35 / 3.0, clipped exponential tilt | **unratified** |
| **U3** | scoring domain | 1-D `E_avail`, edges `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100]` GeV | **unratified, and the open question** |

Committed before measurement in `CANDIDATE_ENDPOINT_CHOICES-20260918.json`. The
binning is the campaign's own canonical `E_avail` axis, chosen because it predates
this endpoint and so cannot have been tuned to it.

**Two measured facts bear on U3.**

1. **Scoring off-variable loses 42.4 % of the injected signal.** Total displacement
   is 0.2733 on `E_avail` and 0.1574 on the `(pT, p‖)` reporting grid. An injection
   in `E_avail` scored on the muon grid is a much weaker test of the same physics.
2. **The 1-D projection flatters itself.** No `E_avail` bin falls below 0.05
   acceptance, which looks reassuring, but that is an average over `(pT, p‖)` cells
   spanning **0.004 to 0.89**. The poorly accepted regions are still in the truth
   mass; the binning merely stops resolving them.

So the real U3 question is **1-D `E_avail` or 2-D `E_avail × (pT, p‖)`**. The
proposal is 1-D as the primary with the 2-D acceptance strata **co-reported, never
replaced by their average**. A 2-D primary is defensible and more sensitive to
regional failure; it costs more seeds for the same per-cell precision.

---

## 3. Protection against hidden regional failures

A single aggregate recovery number can be met while a region is badly wrong. Four
protections, all predeclared:

* **stratified reporting is mandatory, not optional.** Bins are reported in three
  acceptance strata — `< 0.05`, `[0.05, 0.5)`, `[0.5, 1]` — with the truth mass in
  each. Measured on the candidate: **0 bins below 0.05; 3 bins in `[0.05, 0.5)`
  holding 67.0 % of the truth mass; 4 bins in `[0.5, 1]` holding 33.0 %.** Most of
  the mass sits in the *less* well accepted stratum, which is the opposite of the
  reassuring reading.
* **low-acceptance bins are retained.** Binning is chosen from physics and frozen
  in advance. Choosing edges so that no bin is prior-dominated is choosing binning
  to hide poorly accepted regions, and is refused.
* **the worst bin is reported beside the aggregate**, always, with its acceptance
  and truth mass, so an aggregate pass with a failing region is visible rather than
  discoverable.
* **the `(pT, p‖)` co-report** carries the cell-level acceptance range, so the
  projection's averaging cannot be mistaken for the absence of a problem.

---

## 4. Adequacy, non-inferiority and superiority

Three different questions. Conflating them is how "no detectable difference"
becomes "at least as good".

| id | question | proposed criterion | status |
|---|---|---|---|
| **U4** | reference value | `ceiling(k=3)` on this endpoint, **measured 0.7131** (0.7552 truth-mass-weighted) | measured; **a reference model, not a proven bound** |
| **U5** | absolute adequacy | recovery ≥ `f × 0.7131`, `f` proposed 0.80 | **unratified**; the `f = 0.80` analogy is to a *different* endpoint |
| **U6** | non-inferiority margin δ | proposed as a **fraction of the calibrated reference**, not an absolute number | **unratified, and currently unjustified** |
| **U7** | switching threshold δ_switch | policy about adoption cost, not a property of either estimator | **unratified** |

**The pT reference does not transfer.** The inherited 0.618228 is wrong for this
endpoint by 0.095 — roughly five times the margin under discussion. Any criterion
expressed as a fraction must be a fraction of **0.7131**.

**δ has no justification at present and I am not supplying one.** Its previous
justification rested on `0.5126033`, and `OI-71` marks every artifact of closure
`56552326` `NONQUOTABLE-DIAGNOSTIC` with `recovery_evaluated: False` at the promoted
configuration. That justification was withdrawn and has not been replaced. δ is a
statement about how much recovery we are willing to lose to keep the incumbent, and
it needs an argument from the physics, not from a number that cannot be quoted.

**The selection rule is implemented and tested** (`selection_rule.py`, 30 tests),
including the case where both arms are adequate and the interval excludes zero but
does not bound the magnitude: `CI = [-0.10, -0.01]` with `δ_switch = 0.02`
establishes only that his advantage is *positive*, and returns
`THEIRS_BETTER_MAGNITUDE_UNRESOLVED → NO_SELECTION`. Measured performance and any
preference for retaining the incumbent are separate fields, and the preference is
flagged unratified.

---

## 5. Pilot and sizing procedure

* the statistic is the **paired** difference in recovery across estimator seeds;
* intervals use the **t distribution with n−1 df**; at n ≈ 8 the normal quantile
  understates the interval by about 15 %;
* `n` is solved **iteratively** with `t_{n−1}`, re-solved until stable, not from a
  closed-form normal expression;
* sizing uses the **upper one-sided 80 % confidence bound on σ** from the pilot, not
  the point estimate, so an optimistic pilot cannot undersize the comparison;
* the pilot is **4 paired seeds per arm**, and **for the pretrained arm it cannot
  run until R2 lands** (§1);
* the reported interval covers **estimator-seed variation at fixed data and fixed
  configuration**. It does not cover MC statistics, the choice of injection, or
  configuration uncertainty, and must not be quoted as if it did.

---

## 6. What needs your decision, and what will be measured

**Yours to decide — none of these is an implementation detail.**

| id | decision | consequence of getting it wrong |
|---|---|---|
| U1 | injected variable | the comparison is sensitive to the wrong physics |
| U2 | tilt amplitude and clip | too small and nothing is resolvable; too large and it is not a perturbation |
| **U3** | **1-D `E_avail` or 2-D** | 1-D averages over cells spanning 0.004–0.89 acceptance |
| U5 | adequacy fraction `f` | an arm passes that should not, or vice versa |
| U6 | δ, with a physics argument | "no difference detected" is read as "at least as good" |
| U7 | δ_switch | encodes what we will pay to switch; not measurable |
| **U9** | **his training schedule** | his cosine schedule needs `max_steps` **derived from the agreed fair budget**, never copied from his job script |
| **U10** | **token cap: 12 or 33** | 33 is his `max_particles` and needs a dump re-run; it costs ≈1.9x per evaluation, and `r` grows 2.7 -> 4.2 with tokens |
| **U11** | **run his arm without `pid` and `add_info`** | until R-1/R-2 lands his arm loses two input channels it was designed around; that is a handicap, not a matched comparison |

**To be measured — no decision needed.**

| id | quantity | state |
|---|---|---|
| M1 | reference `ceiling(k=3)` on `E_avail` | **measured 0.7131 / 0.7552** |
| M2 | injected displacement on the endpoint | **measured 0.2733** |
| M3 | loss from scoring off-variable | **measured 42.4 %** |
| M4 | acceptance and truth mass per bin and per stratum | **measured** |
| M5 | `r`, the per-example cost ratio, at 12 and 33 tokens | **measured 2.7 (12 tokens) and 4.2 (33) at matched batch; 3.55 at his native batch under the repair** |
| M6 | inference cost per arm | **measured**: 36 M presentations per evaluation, ratio 1.9 and 2.4 |
| M7 | whether his native batch 2048 runs at 33 tokens, and what fixes it | **measured: a backend repair (math SDPA) keeps his recipe; no batch change needed** |
| M8 | σ, seed scatter, per arm | **pilot; pretrained arm blocked on R2** |
| M9 | exact-coordinate ties among real tokens in the production clouds | **not yet run on real data**; zero in the synthetic fixture. Ties make k-NN ordering engine-defined, so this is a cheap CPU check to run before the comparison, not a risk to carry (`verify_knn_tie_freedom`) |

---

## 7. External blockers, precisely

| id | blocker | owner | blocks |
|---|---|---|---|
| **R2** | `best_model_pretrain_s.pt`, `best_model_pretrain_m.pt`, their sha256 and licence, from CFS project **m4567** (portal times out; not our project) | **Gregor** | the objective itself — tuning, pilot and final runs of the pretrained arm |
| **R-1** | three scalar branches `ev_run`, `ev_subrun`, `ev_gate` on `mc_signal_reco`, `data`, `mc_background` | **Agent A** | the typed-object join; the npz carries no event key |
| R-2 | ~21 typed-object vector branches, as an alternative to R-1 | Agent A | the representation half |
| **R4** | authorization to read the 21 typed branches at scale — outside A1, which covers blob and prong **counts**, not values | **Joseph** | the representation half |
| globals | authorization to read Gregor's 16 event-global branches; not in `REQUIRED_BRANCHES` at all | **Joseph** | his conditioning block |
| U1–U11 | the decisions above | **Joseph** | freezing the design |

Ours, needing nobody: the dump re-run at a raised token cap. The cap is a Python
choice in `dump_pointcloud_inputs._pad_tokens`; **no C++ change is required.**

Drafts to Agent A and Gregor are written and **not sent**:
`requests/DRAFT-agent-a-event-keys.md`, `requests/DRAFT-gregor-paper-configuration.md`.

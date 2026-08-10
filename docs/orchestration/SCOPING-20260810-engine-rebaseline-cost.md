# SCOPING — what a change to `omnifold.py` would cost

**Requested by Joseph 2026-08-10: "I would rather meet that decision with the effort quantified than
discover it." SCOPING ONLY. This is not a recommendation to proceed, and no engine edit has been made.**

The candidate change is one line's worth of behaviour: making the engine's intended per-iteration
learning-rate anneal effective (`RunModel` currently recompiles at full `self.LR` before every `fit()`,
overriding `CompileModels(fixed=True)`). The change is small. The blast radius is not, because **every
trained artifact in the campaign was produced by the current behaviour.**

## 1. What becomes invalid

Anything whose numbers came out of a training run. Not merely "should be re-checked" — **produced by a
different estimator**, in exactly the sense BEN/CLM already use for the 2026-08-01 full-event schema change.

| Class | Concretely | Status after an engine change |
|---|---|---|
| Nominal + floor artifacts | `pet_fullevent_nominal_weights.npz` (`58f664cdef266d09`), `pet_fullevent_floor_weights.npz` (`14cccc231dfd92c9`) | **Invalid.** Must be re-trained. |
| Checkpoints | 14 files per run incl. both BEN-043 `_final` weights | Invalid |
| Gate A/B provenance | `GATE_AB_PUSH_PROVENANCE.slurm-56445883{,.batch512}.json`, `.floor-56445883.json` | Invalid (they bind the artifact) |
| Step-1 decomposition + trajectory | `STEP1_DECOMPOSITION.slurm-56445883.json`, `STEP1_TRAJECTORY.slurm-56525829.json` | Invalid as measurements of the shipped estimator; still valid as measurements of the *old* one |
| D2 powered closure | `POWERED_CLOSURE_*` (`56381674`), and **CLM-012's entire numeric basis**: ceiling `0.618228`, measured recovery `0.546853`, margin `0.052271` | **Invalid.** The ceiling is a property of the estimator+injection; the measured value certainly changes. |
| Ordinary + stress closures | `closure_fullevent_fps.py`, `stress_closure_muon.py` products | Invalid |
| B1 rate-injection sweep | the **48-seed** measurement behind `fold_forward_ratio_dev_max = 0.05` and the `niter 2→3` policy | **Invalid, and load-bearing** — this is what justified the frozen tolerance AND the seed policy |
| Step-1 dynamics factorial | `56534116_[0-2]`, `56534117` | Invalid as baselines (they measured the old engine's dynamics) |
| Diagnostic extraction | push + xsec products, `56525297`/`56527676` | Invalid |
| Ledger | **48 rows** in `VALIDATION_LEDGER.md`; every technote-quoted number sourced from a trained run | Each row needs re-derivation or an explicit "old-estimator" tag |
| State receipts | **25 of 94** reference trained quantities (`estimator_fingerprint` / `weights_push` / `recovery` / `fold_forward`) | Re-issue or annotate |

**The sharpest single consequence:** CLM-012 was adopted yesterday and Gate-4 re-issued against it. Both
rest on `ceiling = 0.618228` and `recovery = 0.546853`, both measured on the current engine. An engine
change **re-opens the decision you just closed**, and the re-specification argument would have to be
re-made on new numbers (the *scope* argument survives — it is analytic — but the values do not).

## 2. Compute bill, from MEASURED elapsed times, not estimates

| Run | Measured elapsed | Notes |
|---|---|---|
| Nominal + matched floor repeat | **06:00:44** (`56445883`, both arms in one job) | the long pole |
| D2 powered closure | **01:58:19** (`56381674`) | needed for the CLM-012 basis |
| Step-1 dynamics factorial | **03:00:20** ×3 arms (`56534116`) | only if the dynamics baselines are wanted again |
| Annealed-LR arm | **03:01:22** (`56534117`) | becomes the *nominal*, not an arm |
| Step-1 trajectory | **00:07:55** (`56525829`) | cheap, gated on the artifact |
| Diagnostic extraction | 13 GPU-min push + 1:32 CPU xsec | cheap |
| Ordinary + stress closures | not re-measured this session | must be timed before committing to a number |
| **B1 48-seed sweep** | **not measured this session — the dominant unknown** | 48 trainings; if each is even ~20 min that is ~16 GPU-h, and it gates the frozen tolerance |

**Minimum credible path** (re-train nominal+floor, re-run D2, re-derive CLM-012, re-run the two closures):
**~10–12 GPU-hours**, plus the B1 sweep if the frozen tolerance is to remain evidence-backed.

**Full re-baseline including B1 and the dynamics arms: ~35–45 GPU-hours**, dominated by the B1 sweep,
whose cost I have *not* measured and would need to before quoting it as a number rather than a range.

Against the allocation: this is affordable in compute. **The cost is not GPU-hours — it is the
re-verification chain.**

## 3. Gates and receipts that would need re-issuing

1. `p3f-pet-gate4-launch-code-gate-*` — the live one is `...-20260809.json`, and it **DOES pin the
   engine**: `estimator_engine_multifold` → `omnifold_nn/omnifold/omnifold.py`, plus
   `estimator_engine_net` → `net.py`. So an engine edit **breaks the binding and the gate says so**, which
   is correct behaviour and means the re-issue would be required rather than optional.
   **RETRACTION (2026-08-10):** REVISION 1 of this document originally claimed `omnifold.py` was *not*
   pinned and called it a hole. **That was false and I asserted it without running the check** — my earlier
   grep had looked for the *closure* driver, not the engine, and I carried the conclusion across. Exactly
   the BEN-027 failure: a claim in a status document not backed by a command run in the same turn. Joseph
   asked for the hole to be closed; there was no hole, and a re-issue adding a second pin on an
   already-pinned file was created and then reverted.
2. `FROZEN["powered_closure"]` — `acceptance_limited_ceiling`, `ceiling_scope_scalar_value`,
   `ceiling_flip_value`, `unexplained_shortfall_vs_ceiling`, and `residual_over_gap_max` derived from them.
3. `FROZEN["tolerances"]["fold_forward_ratio_dev_max"]` and its `MEASURED_20260806_B1_48SEEDS_NITER3`
   status string — the status becomes a lie the moment the engine changes.
4. `NOMINAL_SEED_POLICY`'s `niter = 3`, which was chosen *because* of the B1 measurement. The 2026-08-09
   trajectory already put that choice in tension; an engine change re-opens it outright.
5. CLM-011, CLM-012 in `CLAIMS.md`; the D2 and Gate-A/B rows in `VALIDATION_LEDGER.md`.
6. `KNOWN_ISSUES` entries describing the *current* behaviour (the dead anneal entry becomes historical).

## 4. What is NOT invalidated

Worth stating, because it is most of the infrastructure and it is the reason the change is even thinkable:

- Every **gate, validator, auditor and test** — they check relationships, not values. `verify_hash_bindings`,
  the two repo-wide auditors, `pet_diagnostic_quarantine`, the quarantine power tests, the criterion
  derivation check.
- The **G2 dump** (`fa6b3463…`) and everything upstream of training: Gate-2 target, Gate-3 manifests,
  the P3F/P3S event loops, the 748 GB merged inputs.
- The **analytic** results: CLM-012's scope argument (Jensen, `φ` concave), the acceptance-dilution
  algebra, BEN-077's pattern, the FPS/J28 covariance work.
- All **BEN rows** — they describe how agents and code fail, not what the estimator measured.

## 5. The honest summary

The compute is affordable and the *code* change is trivial. What makes this a large decision is that it
invalidates **48 ledger rows, 25 state receipts, CLM-012 as adopted yesterday, the frozen fold-forward
tolerance, and the `niter=3` seed policy** — and the re-verification of those is human-reviewed work, not
GPU work. The correct sequencing question is therefore not "can we afford the re-train" (yes) but "do we
want to re-open CLM-012 and the seed policy", which is the same question one level up.

**Recorded as scoping. No engine edit made. Not a recommendation.**

---

# REVISION 1 — 2026-08-10. My §1 was TOO PESSIMISTIC, and the correction is large

Joseph challenged the claim that CLM-012's basis falls: *"the ceiling is `(1-a_b)^k` — a function of the
acceptance map and k, not of learning rate."* He is right. **Verified from the code, not argued.**

## The check he asked for: is the acceptance-limited ceiling estimator-dependent at fixed k?

**No.** Evidence, from `d2_acceptance_oracle.py` and the committed acceptance map:

- `a_b` is read from `products/pet/fullevent_fps/acceptance_map_fullevent_fps.json`, whose own
  `definition` field is `a_b = sum(w_truth | pass_truth & pass_reco) / sum(w_truth | pass_truth)`, with
  `inputs: G2_FPS_MEFHC_P12.npz` (sha `fa6b3463…`) and nothing else. A reco efficiency over dump
  quantities — **no estimator weights.**
- The oracle branch builds a **synthetic** push: `push_or = 1 + r_k[cellB] * (tilt_B - 1)` with
  `r_k = 1 - (1-a_b)^k`. It never reads `weights_push`.
- `h_prior`, `h_target` and therefore `gap` come from the dump plus the seeded injection. No unfold.
- `weights_push` enters only `h_unfold` — i.e. only the **measured** recovery.

So an LR anneal changes neither `a_b` nor `k`, and the ceiling at fixed `k=3` is **unchanged** by an engine
change.

## Consequence — CLM-012's CRITERION survives entirely

| Ingredient | Status | Why |
|---|---|---|
| ceiling `0.618228` | **SURVIVES** | dump-derived `a_b`, synthetic oracle push |
| `f = 0.80` | **SURVIVES** | predeclared and blind-confirmed *before* any measurement |
| threshold `0.494582` | **SURVIVES** | `= f × ceiling`, both ingredients survive |
| scope argument (Jensen, `φ` concave) | **SURVIVES** | analytic |
| `R = 1.1240802949941018` | **SURVIVES** | `(n_data − pot_scale·Σw_bkg)/(pot_scale·Σw_reco[pass_reco])` — data + POT + dump only |
| `gap`, `h_prior`, `h_target` | **SURVIVES** | dump + seeded injection |
| measured recovery `0.546853` | RE-MEASURED | uses `weights_push` |
| margin `0.052271` | RE-MEASURED | derived from the measured value |

**So the adopted criterion does not need re-deriving — only the comparison against it re-running.** My §1
claim that "CLM-012's entire numeric basis" is invalid was wrong: the *criterion* is untouched and only the
*measurement* moves. Gate-4's re-issue against that criterion likewise stands.

**The one real exposure, which is Joseph's own caveat:** the ceiling is fixed only *at fixed k*. If the
anneal changes which `niter` is right, `k` moves and so does the ceiling — `k=2 → 0.5642`,
`k=3 → 0.6182`, `k=4 → 0.6441`. Given the 2026-08-09 trajectory already put `niter=3` in tension, **that is
the live risk, and it is a policy question rather than a re-derivation one.**

## And a correction to my own arithmetic: "48 ledger rows" was a bad number

`VALIDATION_LEDGER.md` does not hold 48 one-per-claim rows. It holds several small tables, and my count
included **headers and `---:` separators**. Counting actual claim-blocks by reading them:

- **Trained-dependent (invalidated):** the step-1 prior-push trajectory table, and the iteration-2 sign
  control table from the dynamics factorial. **2 blocks.**
- **Survives unchanged:** the active-lateral/FPS budget block; the `R` block and its D1 leg comparison
  (dump quantities); the Gate-2 refined-target block (sha, rows, refiner); the 10/10 endpoint-agreement
  block; the normalisation/shape-shift block. **~5 blocks.**

So the honest split is roughly **2 invalidated to 5 surviving**, not "48 invalidated". Joseph's suspicion
was right and my flat count was the misleading kind of number this campaign keeps catching — I counted
rows because rows were countable, not because rows were the unit of meaning.

**The receipt count carries the same caveat.** My "25 of 94" (31 on a second pass) came from a keyword scan
for `weights_push|recovery|fold_forward|estimator_fingerprint`. That is an **upper bound on
touched-by-the-topic**, not a classification of invalidated — many of those receipts merely *cite* a trained
artifact's digest and would be re-verified unchanged rather than invalidated. I have not done the
row-by-row triage for 94 receipts and am not going to quote a split I have not done.

## Revised bottom line

Compute unchanged: **~10–12 GPU-h minimum, ~35–45 GPU-h full**, still dominated by the unmeasured 48-seed
B1 sweep. What changes is the *verification* burden, downward and substantially:

- CLM-012 and its adopted threshold: **no re-derivation needed** (was: "entire basis invalid")
- Gate-4's re-issue against that criterion: **stands**
- `R` and the fold-forward *target*: **stand**; only the achieved deviation is re-measured
- Ledger: **~2 claim-blocks** to redo, not 48 rows
- The genuinely open exposure: **the `niter` policy**, and `fold_forward_ratio_dev_max`'s
  `MEASURED_20260806_B1_48SEEDS_NITER3` status string, which does become stale

**So the engine question is materially more affordable than §1 implied.** It is still Joseph's decision and
this remains scoping, not a recommendation — but the honest framing is now "re-measure a handful of values
against surviving criteria, and re-open the niter policy", not "re-baseline the campaign".


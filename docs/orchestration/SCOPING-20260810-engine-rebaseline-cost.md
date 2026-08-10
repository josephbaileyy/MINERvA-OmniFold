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

1. `p3f-pet-gate4-launch-code-gate-*` — the live one is `...-20260809.json`. `omnifold.py` is **not** among
   its 17 pins, so the *binding* survives an engine edit. **That is a gap, not a reassurance:** the gate
   freezes the driver, validator, launchers and tests but not the engine they all call. Worth recording
   independently of this decision.
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

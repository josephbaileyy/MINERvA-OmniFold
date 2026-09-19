# Freeze proposal

**One ratification ask, not eleven.** Everything below is either already fixed by
evidence, or is the single policy choice that remains. Reference values and pilot
scatter are calculated or measured and are not on this list.

**CITABLE FOR:** what is proposed to be frozen and what pins each item.
**NOT CITABLE FOR:** any result. Nothing here is ratified until you say so.

---

## 1. What freezes, and what pins it

| # | item | frozen value | pinned by |
|---|---|---|---|
| F1 | **his complete arm** | PET2-small, `use_int=False`, `local_int=False`, PID (8 classes), 5 auxiliary columns, 16 globals, `--zero-cond-feature 2`, cap 33, batch 2048, AdamW(1e-4, wd 0.01), warmup+cosine, global-norm clip 1.0, init `best_model_pretrain_s.pt` | `configuration_identity.THEIRS_COMPLETE`, enforced by `require_his_complete_arm` |
| F2 | **our incumbent** | the promoted production PET: heads 2, transformers 2, `projection_dim` 32, `K` 3, cap 12, batch 512, engine Adam with the annealed policy | `configuration_identity.OURS_INCUMBENT`; exactly one arm may hold `PROMOTED_INCUMBENT` |
| F3 | **candidates** | any change to F2 is a declared candidate with a parent and a rationale; it never silently becomes "ours" | `configuration_identity.declare_candidate` |
| F4 | **injection** | truth `E_avail`, clipped exponential tilt, amplitude **0.35**, clip **3.0** | `CANDIDATE_ENDPOINT_CHOICES-20260918.json`, committed before measurement. **You have supported this.** |
| F5 | **primary score** | 1-D `E_avail`, edges `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100]` GeV | same file; the axis predates the endpoint |
| F6 | **regional safeguard** | regions on the **(pT, p‖) reporting cells** by cell acceptance; every scoreable region must clear its floor; failure ⇒ `NO_SELECTION` | `selection_rule.regional_safeguard`, `characterize_eavail_endpoint._region_census` |
| F7 | **fairness axis** | equal **example presentations** per fit; `max_steps` and warmup derived from it per arm | `training_recipe.derive_schedule` |
| F8 | **decision rule** | the eight verdicts plus the regional gate, measured performance separated from preference | `selection_rule.py`, 39 tests |
| F9 | **inference** | paired differences, t with n−1 df, `n` solved iteratively, sized on the **upper one-sided 80 % bound** on σ | proposal §7.4 |

## 2. The one thing to ratify: the threshold policy

Every number is translated into the quantity that can be judged — **truth mass left
in the wrong bin.** The injection moves **13.67 %** of the truth mass
(L1 displacement 0.2733); the calculated reference at k=3 is **0.7131**, which
itself leaves **3.92 %** misplaced.

| knob | proposed | what it permits |
|---|---|---|
| adequacy `f` | **0.80** of the reference ⇒ recovery ≥ **0.5705** | **5.87 %** of truth mass misplaced — 1.95 points worse than the reference |
| non-inferiority `δ` | **0.02** of recovery | **0.27 %** additional misplaced mass |
| switching `δ_switch` | **0.04** of recovery | **0.55 %** additional misplaced mass |
| regional floor | **0.60** of each region's own reference | looser than the global floor, deliberately |

**Why these, and what you are trading.**

* **`f = 0.80`.** Adequacy has to be acceptance-aware, or a low-acceptance endpoint
  fails for being hard rather than for being badly estimated — so it is a fraction
  of the reference, not an absolute recovery. 0.80 demands recovering 57 % of a
  13.67 % distortion. *Trade-off:* the reference is a model and not a bound, so
  `f` inherits its uncertainty; the residual column is the reading that does not.
  Lower `f` and an arm can pass while misplacing more mass; raise it and both arms
  may fail on an endpoint that is simply hard.
* **`δ = 0.02`.** This is the one genuinely scientific judgement here: it says we
  will accept **0.27 % more of the truth mass in the wrong bin** to keep the
  incumbent. I am not able to justify that against the measurement's systematic
  budget, which I must not assume — that is what I am asking you to weigh.
  *Trade-off:* δ enters the sample size roughly as `1/δ²`. Halving it to 0.01
  costs about **four times the seeds**, so the 8-seed comparison becomes ~32 seeds
  and ~64 GPU-h becomes ~256. δ = 0.02 is affordable inside the ceiling; δ = 0.01
  is not, at 33 tokens.
* **`δ_switch = 2δ`.** Adoption has a cost — a second framework's recipe, a
  checkpoint dependency, a 3.6× per-example price. Requiring twice the margin
  before switching prices that. It is a policy about what we will pay, not a
  property of either estimator. *Trade-off:* set it too high and a genuinely
  better method is kept out; too low and we adopt on noise.
* **regional `0.60`.** A region is a smaller sample and noisier, so holding it to
  the global floor would block on scatter rather than on failure. *Trade-off:* a
  looser regional floor is a weaker safeguard; the exempt-mass figure in the
  census is the audit that it has not been loosened into uselessness.

**Consequence of a regional failure, stated explicitly:** `NO_SELECTION`. Not
"recommend the other arm". One arm failing a region does not establish that the
other passed it, and the report names which regions failed for whom.

## 3. What does not freeze yet, and why

| open | blocked on |
|---|---|
| the pretrained arm's **selected settings** | R2. Scratch tuning cannot supply them. |
| the pretrained arm's **σ** and hence `n` | R2. Scratch variance is a different quantity. |
| the **absolute** GPU-hour total | `n_data`, which must be read off a production run's loader meta; the ratio is unaffected |
| `pid`, auxiliary, globals, cap 33 for his arm | R-1/R-2 and a dump re-run |

## 4. Stop conditions

1. Any port check fails ⇒ stop; the arm is not his configuration.
2. The regional safeguard fails for both arms ⇒ report `NO_SELECTION` and the
   failing regions; do not re-bin.
3. The pilot's σ demands more seeds than the ceiling allows ⇒ report that the
   comparison is underpowered at the frozen δ. **Do not shrink δ after seeing σ.**
4. `n_data` turns out to make the campaign exceed the ceiling ⇒ re-cost and return
   here before launching.

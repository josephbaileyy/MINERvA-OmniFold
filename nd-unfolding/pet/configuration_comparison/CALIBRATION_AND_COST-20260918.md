# GPU calibration plan and rebuilt cost accounting

**CITABLE FOR:** a bounded, executable calibration job and a cost model whose every
term is named.
**NOT CITABLE FOR:** a total. Two inputs are unmeasured and the totals below are
conditional on them. **Nothing is launched; submitting the job needs stage-2 approval.**

---

## 1. The calibration job

**What it answers:** `r`, the per-example training cost of Gregor's backbone relative to
ours. Everything downstream is priced in `r`, and no honest total exists without it.

**Executable now:** `calibrate_cost.py` + `sbatch_cost_calibration.sh`.

| element | choice |
|---|---|
| arms | ours = production PET (`num_feat` 5, `num_evt` 13, `num_part` 12, 2 blocks, 2 heads, width 32, K=3) at **batch 512**; his = OmniLearned **PET2-small** at the pinned constructor values, at **batch 2048** (his real setting) and at **512** (fixed-work comparison) |
| unit | **seconds per example presented**, not per step — per-step would flatter the larger batch, and example presentations are the frozen fairness axis |
| device | one A100, both arms, same job |
| protocol | 5 warm-up steps discarded, 20 timed; `tf.function` on our side, `cuda.synchronize()` on his so the clock measures work rather than queueing |
| pinning | the launcher verifies **our** HEAD and clean tree **and** that the Gregor checkout is at `fc9a099d` and clean — a ratio against an unpinned upstream is not a measurement of the named configuration |
| structure | **one arm per interpreter.** Ours needs TensorFlow, his needs PyTorch, and nothing establishes a Perlmutter interpreter has both. Each writes a half; `--arm reduce` combines them and **refuses a partial pair**, so a missing arm cannot become a one-sided cost report |
| bound | `--time=00:20:00`, two 600 s timeouts. No convergence, no closure statistic, no learning claim |

**Confound, named in the receipt rather than in a footnote:** the arms are
**device-matched and framework-unmatched**, because the Keras port does not exist yet. A
same-framework `r` needs the port. This job exists so the port is not built before anyone
knows whether the campaign it enables is affordable.

**Superseded by it:** `receipts/step-cost-scale.json`, which is a **CPU** measurement and
is labelled as one. Its two-batch control showed the ratio moving 1.6× → 5.8× across an
8× batch change, i.e. the small-batch figure was framework overhead. It is retained as
the reason to measure on GPU, not as an estimate of `r`.

---

## 1a. Campaign ceiling and spend reconciliation

**The cumulative campaign ceiling is 600 GPU device-hours**, raised from 290 by Joseph on
2026-09-18, **inclusive of existing spending and retries**.

| item | GPU device-hours | source |
|---|---:|---|
| representation matrix, 24 paired jobs | 13.27 | `matrix-summary.json` |
| A3 geometry probe + width gate, 5 submissions | 0.43 | `GO_NO_GO-20260918.md` §7 |
| tail validation, 4 submissions | 0.77 | `validation-final.json` |
| inference benchmark + matrix closeout | not itemized | — |
| *subtotal carried as the campaign figure* | **16.0** | `RECOMMENDATION-20260918.md` |
| this milestone: retries that measured nothing | 0.01 | jobs 58526592 (18 s), 58526558 (5 s), 58526214 (cancelled before start) |
| this milestone: calibration, ceiling | ≤0.42 | one 25-minute GPU job |
| **cumulative against the 600-hour ceiling** | **≤16.5** | |
| **headroom** | **≥583** | |

**This milestone's own limits: ≤2 GPU-hours and ≤8 CPU core-hours, inclusive of repairs
and retries.** Consumed so far: **0.01 GPU-h** across three failed or cancelled
submissions, and under 0.01 CPU core-hours. The optional full Tier-A campaign is **not
launched** at this milestone.

## 2. The cost model

Two parameters, both currently unmeasured:

* **`c`** — our per-evaluation GPU-hours. The feature contract gives ~1.1–1.3 GPU-h for a
  nominal train; an evaluation is one train plus injection and scoring. **Planning value
  `c = 1.5`, unmeasured.** The driver's own projection is fit-time only and understates
  absolute cost, because the fixture build, normalization, reweight-all inference and
  serialization do not scale with the backbone.
* **`r`** — his per-evaluation multiple. **Unmeasured.** CPU indication at production
  batch was 5.8× with a framework confound; planning value `r = 6`.

An arm-pair evaluation costs `c(1 + r)`. At the planning values that is **10.5 GPU-h**.

---

## 3. Complete accounting

Rows marked **N** are necessary for the stated objective — our complete configuration
against Gregor's intended **pretrained** method. Rows marked **O** are optional Tier-A
preparation, whose result is a real sub-conclusion but, being scratch-only and at our
representation, **cannot complete the objective**.

| | item | GPU-h | CPU | status |
|---|---|---|---|---|
| **N** | this preparation package | **0** | local | **done** |
| **N** | Keras port of PET2-small + checks P-1…P-6 (float64, CPU) | **0** | local | to implement |
| **N** | E-1/E-2: `E_avail` acceptance map + displacement, from the existing npz | 0 | ~1 core-h | **needs authorization** |
| **N** | fold-forward recorder (`OI-125`), ~8 lines, new file | 0 | local | to implement |
| **N** | **stage 2 calibration — measures `r`** | **0.33** | — | **executable, needs approval** |
| O | Tier-A tuning, 4 trials × 2 arms | `4c(1+r)` = 42 | — | after stage 2 |
| O | Tier-A variance pilot, 4 paired seeds | `4c(1+r)` = 42 | — | after tuning |
| O | Tier-A final, 8 paired seeds | `8c(1+r)` = 84 | — | after pilot |
| N | controls V2/V4/V5/V8/V9, one evaluation per arm | `c(1+r)` = 10.5 | — | V4/V5/V8 partly reuse existing artifacts |
| N | completion tuning, 4 trials × 2 arms, typed representation | `4c′(1+r′)` | — | blocked |
| N | completion pilot, 4 paired seeds | `4c′(1+r′)` | — | blocked |
| N | completion final, `n` paired seeds, `n` from the pilot | `n·c′(1+r′)` | — | blocked |
| N/O | retries, 25 % of the GPU subtotal | — | — | repairs count as retries |

**`c′` and `r′` are not `c` and `r`.** The completion configuration raises the cap from
12 tokens to Gregor's 33, so both arms carry ~2.75× the tokens; attention is quadratic in
token count and the MLP terms linear, so `c′ > c` and the two arms' ratio changes too.
Pricing completion at Tier-A's numbers would understate it. Stage 2 should therefore
time **both** token counts, and the plan says so rather than discovering it later.

### Conditional totals

| scope | GPU-h at `c=1.5, r=6` | note |
|---|---:|---|
| necessary preparation through stage 2 | **0.33** | plus ~1 CPU core-h |
| **+ Tier-A (optional) with 25 % retries** | **~211** | against 274 remaining of the 290 ceiling |
| + controls | **~224** | |
| completion at the typed representation | **not costed** | `c′`, `r′` unmeasured; blocked on R-1, R2 and a dump re-run |

**Tier A alone consumes roughly three-quarters of the remaining ceiling and cannot
complete the objective.** That is the central budget fact of this package, and it is why
Tier A is presented as optional rather than as the plan. If the objective is the
complete comparison, the sequence that respects the budget is: stage 2 first, then decide
whether Tier A is worth 211 GPU-h *given* what stage 2 says about completion's price.

**Sensitivity to `r`**, for an 8-seed arm-pair comparison at `c = 1.5`:

| `r` | `8c(1+r)` |
|---:|---:|
| 2 | 36 |
| **6** | **84** |
| 12 | 156 |
| 20 | 252 |
| 41 (PET2-medium) | 504 |

---

## 4. Stop conditions specific to calibration

1. Either half fails, or the reducer refuses the pair → report, do not quote a one-sided
   ratio.
2. The Gregor checkout is not at `fc9a099d`, or either tree is dirty → the launcher
   refuses before allocating.
3. Measured `r` puts completion outside the available allocation → **say so and stop.**
   Do not raise the ceiling, shrink the seed count below the pilot's requirement, or
   substitute a cheaper backbone and call it his configuration.
4. Repaired submissions count as retries against the stage budget. No automatic relaunch.

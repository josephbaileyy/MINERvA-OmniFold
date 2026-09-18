# Costed route to the complete pretrained comparison

**Objective, unchanged:** compare our complete configuration against Gregor's intended
**pretrained** method and recommend whichever the evidence supports. A scratch-only
Tier-A result cannot complete it.

**CITABLE FOR:** what remains between here and that comparison, and what each step costs.
**NOT CITABLE FOR:** any result, any ratified threshold, or any adoption.

---

## 1. Exactly what is missing

### 1.1 Checkpoints — blocks the objective itself

| item | file | source | state |
|---|---|---|---|
| OmniLearned-small pretrained | `best_model_pretrain_s.pt` | `https://portal.nersc.gov/cfs/m4567/checkpoints` | **unreachable** (verified: times out) |
| OmniLearned-medium pretrained | `best_model_pretrain_m.pt` | same | **unreachable** |
| sha256 for both | — | Gregor | **absent** |
| weights licence | — | Gregor | **absent** |

The loader **downloads silently when the file is absent** (`omnilearned/utils.py:58-79`),
so a reproduction attempt fails at runtime rather than at configuration time. CFS project
**m4567** is not ours, so this is not an access request we can make ourselves.

**Consequence, stated plainly: without these, arms P1 and P3 cannot run at all, and the
comparison can only be against his from-scratch arm P2 — which does not test the transfer
claim his paper is about.** Everything else on this page is affordable and tractable; this
one item decides whether the objective is reachable.

### 1.2 Exports — block the representation half

| id | export | owner | why |
|---|---|---|---|
| **R-1** | three scalar branches `ev_run`, `ev_subrun`, `ev_gate` on `mc_signal_reco`, `data`, `mc_background` | **Agent A** | the npz carries no event key, so typed objects cannot be joined to estimator rows. Draft at `requests/DRAFT-agent-a-event-keys.md` |
| R-2 | ~21 typed-object vector branches, as an alternative to R-1 | Agent A | larger ask, fixes the vocabulary in C++ |
| **own** | dump re-run at a raised cap with overflow telemetry | **ours** | the cap is a Python choice in `dump_pointcloud_inputs._pad_tokens`; **no C++ needed** |

### 1.3 Authorizations

| id | ask | owner |
|---|---|---|
| **R4** | read the **21** typed-object branches at scale — they are outside A1, which covers blob and prong **counts**, not values | Joseph |
| globals | read Gregor's 16 event-global branches; not in `REQUIRED_BRANCHES` at all, so they need enumerating separately | Joseph |

### 1.4 Scientific decisions — none of them ours to make

| id | decision | why it is not a detail |
|---|---|---|
| **U1** | injected variable (candidate: truth `E_avail`) | it determines what the comparison is sensitive to |
| **U2** | tilt amplitude and clip (candidate 0.35, 3.0) | the amplitude is dimensionless and transfers; the displacement field it produces does not |
| **U3** | scoring domain and binning (candidate: the campaign's own canonical `E_avail` axis) | **must not be chosen to hide poorly accepted regions** |
| **U4** | the reference value | **a reference model, not a proven bound**; the pT value 0.618228 does not transfer |
| **U5** | adequacy criterion `f` | the `f = 0.80` analogy is to a different endpoint |
| **U6** | non-inferiority margin δ | proposed as a **fraction** of the calibrated reference |
| **U7** | switching threshold δ_switch | encodes adoption cost — a policy about what we will pay, not a property of either estimator |
| **U8** | seed scatter σ | must be **measured** on this endpoint |
| **OI-71** | whether `VL100` may be quoted at all | `WAITING-USER`, G4 alone surviving |

---

## 2. The route

| # | step | cost | blocked on |
|---|---|---|---|
| 1 | preparation package: endpoint calibration, selection rule, identity contract, scope enforcement | **done, 0 GPU-h** | — |
| 2 | **E_avail endpoint characterization** (this milestone) | **CPU only** | — |
| 3 | **cost calibration at 12 and 33 tokens** (this milestone) | **≤0.42 GPU-h** | — |
| 4 | Keras port of PET2-small + checks P-1…P-6 (forward, gradient, weight-update, float64, CPU) | 0 GPU-h, implementation only | — |
| 5 | fold-forward recorder (`OI-125`), ~8 lines, new file | 0 GPU-h | — |
| 6 | ratify U1–U8 and freeze | 0 | **Joseph** |
| 7 | typed-object extraction and join, verified by the identity contract | CPU | **R-1 + R4** |
| 8 | dump re-run at the raised cap | CPU | ours |
| 9 | tuning, 4 trials per arm, at the completion configuration | see §3 | 6, 7, 8 |
| 10 | variance pilot, 4 paired seeds | see §3 | 9 |
| 11 | **final pretrained comparison**, `n` seeds from the pilot | see §3 | 10 **+ the checkpoints** |

Steps 4 and 5 are implementation with no external dependency and no unresolved scientific
choice. They are the obvious next work and are **not** authorized-and-waiting on anyone.

---

## 3. Costs, from the measured calibration

### 3.1 What was measured

Job **58527080**, one **NVIDIA A100-SXM4-80GB**, both arms on the **same physical GPU**
verified by UUID, our arm under `tensorflow 2.15.0 / keras 2.15.0`, his under
`pytorch/2.6.0` with the upstream source pinned by tree digest `bd832627…`.

**Measured throughput** — clock readings only:

| tokens | ours, batch 512 | ours per example | his, batch 512 | his per example | **r (matched batch)** | r (his native 2048) |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 18.71 ms/step | 36.55 µs | 52.75 ms/step | 103.02 µs | **2.82** | 2.47 |
| 33 | 28.37 ms/step | 55.41 µs | 122.07 ms/step | 238.42 µs | **4.30** | *unavailable* |

**`r` grows with token count: 2.82 → 4.30.** This is exactly why the cost plan promised
both, and why pricing the completion configuration at the current cap would have
understated it by about 50 %. His native batch 2048 ran at 12 tokens and raised
`CUDA error: invalid configuration argument` at 33, so the projections use the
matched-batch ratio throughout — same batch, same tokens, no batch artifact.

**Projected evaluation cost** — derived from the budget model (niter 3, epochs 8, 2 M
subsample, two fits per iteration = 96 M example presentations), **fit-time only**:

| tokens | ours / evaluation | his / evaluation | arm pair | 8 paired seeds |
|---:|---:|---:|---:|---:|
| 12 | 0.97 GPU-h | 2.75 | 3.72 | 29.8 |
| **33** | **1.48** | **6.36** | **7.84** | **62.7** |

Our 0.97 GPU-h at 12 tokens sits just under the feature contract's 1.1–1.3 GPU-h for a
nominal train, which is the expected direction: the contract's figure also covers the
fixture build, normalization, reweight-all inference and serialization, none of which
scale with the backbone. Taking that ratio as the overhead factor gives **≈1.24×** on
absolute totals.

### 3.2 The complete pretrained comparison, costed

At the completion configuration (**33 tokens**, matched-batch `r = 4.30`):

| step | evaluations | fit-time GPU-h |
|---|---:|---:|
| tuning, 4 trials per arm | 4 + 4 | 31.4 |
| variance pilot, 4 paired seeds | 4 + 4 | 31.4 |
| controls (V2 fold-forward, V4, V5, V8, V9), one pair | 1 + 1 | 7.8 |
| **final comparison, 8 paired seeds** | 8 + 8 | **62.7** |
| subtotal | | **133.3** |
| retries at 25 % | | 33.3 |
| **fit-time total** | | **166.6** |
| **with the ≈1.24× non-fit overhead** | | **≈207** |

**Against the 600 GPU device-hour ceiling with ≈16.5 consumed, the complete pretrained
comparison is affordable with roughly 375 hours of headroom to spare.** That is the
central result of this milestone: before it, the ratio was unknown within two orders of
magnitude and the objective could not be costed at all.

Seed count is the lever if the pilot's measured σ demands more than 8: each additional
paired seed costs **7.8 fit-time GPU-h**, so 16 seeds would add ≈63 and still fit.

**What this does not include:** the checkpoints (unavailable, §1.1), the typed-object
export and dump re-run (§1.2, CPU), and any cost of arms P1/P3 differing from P2 — the
calibration timed the **scratch** backbone, and a pretrained checkpoint changes the
initial weights, not the architecture, so the per-step cost should carry over. That last
point is an expectation from the architecture being identical, not a measurement.

---

## 4. What would make the objective unreachable

1. **The checkpoints stay unavailable.** Then only P2 runs, and the honest deliverable is
   a comparison against his scratch arm plus the statement that the paper's transfer
   claim was untestable here. That is a real result and it is not the objective.
2. **Agent A declines both R-1 and R-2.** Then the representation half is untestable and
   only architecture-and-recipe can be compared.
3. **The measured cost puts the final comparison outside the allocation.** Then say so;
   do not shrink the seed count below the pilot's requirement or substitute a cheaper
   backbone and call it his configuration.

None of these is a reason to report a narrower comparison as if it were the objective.

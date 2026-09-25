# FEASIBILITY 2026-09-25 — scalar-5D measurement and inference scopes (plan §5)

**CITABLE FOR:** the measured pilot costs, the exact sample-size and assurance calculations, the
validity route, and the separate feasibility dispositions of each proposed measurement scope and
inference method, locked before any validation experiment or new observed statistic.
**NOT CITABLE FOR:** any scientific PASS. *Feasibility is not a scientific pass* (plan §5).

Contract: [`state/s5c/contract.json`](state/s5c/contract.json). Pilot contract:
[`state/s5c/pilot-contract.json`](state/s5c/pilot-contract.json). Budget:
[`state/s5c/budget.json`](state/s5c/budget.json). Campaign index:
[`CAMPAIGN-s5c-20260924-index.md`](CAMPAIGN-s5c-20260924-index.md).

## 1. Measured costs (native billed units)

All pilots ran as steps on one interactive CPU node (Slurm `58856439`, `CfgTRES billing=256`), 32
CPUs per step, eight steps per node. Node-hours below are per unit of work when packed eight to a node.

| unit of work | measured | billed CPU node-h | source |
|---|---|---:|---|
| one complete 5D unfold, full MC, production estimator (npz path) | 469–475 s unfold, ~504 s step, 10 seeds | **0.0175** | P1 `f1_s42…s51` |
| one complete end-to-end pseudo-experiment (event-level pseudo-data from MC half B with Poisson signal and background, rebuilt purity subtraction, unfold on half A with candidate F2, known truth) | 18.5–18.7 s build + 279–283 s unfold; 427 s per step including env, 1.5 GB input hash and loads | **0.0148** single; **≈0.0104** batched (inputs loaded once per process) | P3/P4 `p3_nominal_s1`, `p3_tilt20_s2`, `p4_null_standin_s3` |
| one complete null experiment for an inference method | identical computation to a pseudo-experiment under a generator truth | ≈0.0104 batched | P4 (cost stand-in: no 5D generator prediction exists, §4) |
| one complete candidate construction of the existing design (seven arms, 598 unfolds, plus laterals) | sacct of the 2026-09-19 k=1200 member | **12.3 CPU + 13.2 GPU node-h** (all CPU work; the "GPU" arms run LightGBM on CPU) + ≈2.6 CPU node-h laterals | `58598277`–`58598283`; pipeline map |
| F2 statistical bootstrap for coverage (200 replicas, half MC) | 200 × 280 s | ≈2.1 | from P3 |
| storage | 94 kB per full-grid unfold; 182 kB per pseudo-experiment (estimate + truth) | 12,000 experiments ≈ 2.2 GB of the 371.7 GiB envelope | products |

The pilot costs were measured within the pilot stage (17.26 CPU node-h): **4.0 node-h reserved**
for the whole interactive allocation; actual charge reconciled from `sacct` at its release.

## 2. Exact sample sizes (Clopper–Pearson, Bonferroni lower bound on assurance)

⚠ **CORRECTED 2026-09-25 (independent review, finding 2): the coverage rows below were first quoted
from the m = 129 rows of `samplesize-assurance80.json` while stating m = 459.** At the contract's
m = 459 ([`state/s5c/samplesize-m459.json`](state/s5c/samplesize-m459.json), exact CP, forward scan):
68% gate — **21,152** per grid point if coverage is exactly nominal, **6,716** if 0.70, **2,935** if
0.72; 95% gate — **11,711** / **5,828** (0.96) / **3,530** (0.965). At n = 4,000: assurance lower
bounds **0.9985** (0.72) and **0.9589** (0.965), **0** at exactly nominal. The exactly-nominal
increment in §5 is therefore ≈ 63,500 experiments ≈ 660 CPU node-h, not 51,000 / 530. The superseded
figures are left visible below; the size and p-value rows were confirmed by the review.

From [`state/s5c/samplesize-assurance80.json`](state/s5c/samplesize-assurance80.json) and the
contract's scope (F = 153 functionals, G = 3 grid points, m = 459 comparisons per family):

| requirement (plan §7) | design value | n for 80% assurance |
|---|---|---:|
| 68% coverage, LCB > 0.66 (per grid point) | true coverage exactly 0.6827 | ≈17,000 |
| | true 0.70 | ≈6,800 |
| | true 0.72 | ≈3,550 |
| 95% coverage, LCB > 0.94 | true 0.9545 / 0.96 / 0.965 | ≈9,600 / ≈4,800 / ≈3,400 |
| size at α = 0.05, UCB ≤ 0.06 | true 0.05; 1 / 4 / 8 null scenarios | 3,370 / 7,924 / 10,404 |
| size at α = 0.01, UCB ≤ 0.012 | 1 scenario | 17,938 |
| size at α = 0.001, UCB ≤ 0.0012 | 1 scenario | 177,011 |
| p-value precision, one reported comparison | true p = 0.5 / 0.2 / 0.05 / 0.02 | 38,720 / 25,200 / 8,040 / 3,760 null draws |
| same, four simultaneous comparisons | true p = 0.5 | 62,720 per comparison |

**The coverage gate is passable in this envelope only if the frozen intervals are somewhat
conservative.** At the contract's n = 4,000 per grid point the pass probability is ≥ 0.95 if true
coverage is ≥ 0.72 (68%) and ≥ 0.965 (95%) everywhere, and **near zero if coverage is exactly
nominal**. Exactly-nominal intervals would need ≈17,000 experiments per grid point (≈530 CPU node-h
for three points). This is recorded as a design limitation, not relaxed.

## 3. Validity route

**Empirical.** No finite-sample theorem applies: the inference nulls would be composite (detector,
flux and model nuisances; finite MC), and the measurement intervals are not rank tests. Therefore no
empirical size or coverage check is replaced.

## 4. Dispositions

| scope | disposition | basis |
|---|---|---|
| **Measurement, Tier S** — F2 statistical intervals on the 153 functionals (43 `(E_avail,W)` M1 + 109 joint-5D cells of partition J = H3 + total), coverage at nominal nuisance over 3 truths | **FEASIBLE TO ATTEMPT** | 12,000 experiments ≈ 125 CPU node-h batched + ≈2 node-h bootstrap, inside the unallocated 224 CPU node-h with the 69 node-h verification reserve intact; pass probability as §2 |
| **Measurement, Tier T** — total (statistical + systematic) interval coverage at shifted nuisance settings | **UNRESOLVED DEPENDENCY** (resources would permit it): pseudo-data under systematic universes need per-event universe weights row-aligned with the unfolding inputs (the sweep bank's alignment with `of_inputs_5d.npz` is not established), and its intervals need the F2 systematic construction | two nuisance points × 4,000 ≈ 8,000 experiments; after Tier S and construction the envelope leaves ≈ 67 CPU node-h (≈ 6,400 batched experiments) plus ≈ 81 GPU node-h (≈ 3,800 on quarter-node slices) |
| **F2 systematic construction** (vertical universes, detector and selection-complete lateral bands under F2) | **FEASIBLE TO ATTEMPT** (≈15–30 node-h from the measured per-unfold cost and the historical arm structure) | needed for a reported total uncertainty; not coverage-validated by Tier S |
| **F1** (existing estimator) | **FAILED** its stability requirement (contract `family_history`) | two-member screen, 5.98%–9.47% on every coarse partition |
| **F3** (seed-averaged) | **INFEASIBLE** | ≥ 10 independent groups × M seeds × a complete construction: with M = 4, ≈ 10 × 4 × 28 node-h ≈ 1,100 node-h |
| **Joint-5D inference I-J** (four generators) | **INFEASIBLE WITHIN THE ENVELOPE** and **UNRESOLVED DEPENDENCY** | the precision rule alone needs ≥ 38,720 null experiments per comparison at p ≈ 0.5 (62,720 with four simultaneous comparisons), i.e. ≥ 400 CPU node-h per comparison, more than the envelope's total; the shallower tiers keep the same rule for p ≥ 0.05; no 5D generator truth prediction exists (only `(E_avail,W)` and 3D ones; the GENIE/NuWro/GiBUU event samples survive) |
| **Projection inference I-EW** and **fixed contrasts I-C** | **INFEASIBLE WITHIN THE ENVELOPE** | the same precision rule and null-ensemble size |

⚠ **CORRECTED 2026-09-25 (review finding 6):** "more than the envelope's total" is true of the CPU
pool alone (38,720 × 0.0104 = 403 > 345.27 CPU node-h); with the GPU pool the envelope could hold
≈ 39,000 experiments before Tier S and the reserve — still short of one comparison's null ensemble
plus its size validation. The plan's insufficient-precision exit would report a Monte Carlo interval
with a precision limitation, which does not qualify a comparison under §9 condition 4. The
dispositions stand.

**Assessed before abandoning joint inference (plan §5):** the permitted shallower tiers (smallest
reportable p of 0.01 or 0.05) do not change the p ≥ 0.05 precision requirement, which dominates the
cost. A surrogate calibration would still need independent end-to-end validation of its tail error
to the same precision (≈ 40,000 experiments). No tier is affordable.

## 5. Costed next increments

| increment | what it buys | forecast |
|---|---|---|
| joint-5D inference, one generator comparison, empirical route | calibrated p with the plan's precision, size at α = 0.05 | ≈ 42,000 null experiments ≈ 440 CPU node-h, plus 5D generator-prediction construction (event loops over the preserved gst samples, a few node-h) and composite-null nuisance sampling (unresolved design) |
| four generator comparisons | the paper's generator set | ≈ 4 × 62,720 ≈ 250,000 experiments ≈ 2,600 CPU node-h |
| Tier T | total-interval coverage at two nuisance settings | ≈ 8,000 experiments (≈ 67 CPU + ≈ 81 GPU node-h: fits the remaining envelope), after the universe-weight alignment work and the F2 systematic construction |
| exactly-nominal coverage precision for Tier S | 80% assurance even if coverage is exactly nominal | ≈ 51,000 experiments ≈ 530 node-h |
| an owner decision on the p-value precision rule | the rule (±0.005 for p ≥ 0.05) is the plan's default; relaxing it is a plan amendment outside this delegation | — |

## 6. Measurement-completion checkpoint and its protection

Tier S (≈127 node-h) and the F2 systematic construction (≤ 30 node-h) are allocated in budget
revision 2 as separate stages; the 20% verification/repair reserve (69.05 CPU / 25 GPU node-h) is
untouched; inference receives **no** allocation because no inference scope is feasible.

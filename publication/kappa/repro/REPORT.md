# Independent reproduction: report-only kappa-breakdown (SPEC-20261007-kappa-breakdown.md)

Reproducer: independent agent, 2026-10-08. The worktree `MINERvA-OmniFold-kappa-repro-20261008` was at HEAD `b75af4f4` and
was not modified. Inputs: the RC4 copy in `../rc4/`. Every file present there matches `rc4/SHA256SUMS`. The four
`code/*.py` files that SHA256SUMS lists, including `replay_inference.py`, are absent from the copy, and I did not read them.

## Code and outputs (sha256)

| file | sha256 |
|---|---|
| `kappa_repro.py` (main computation: claim rule, Holm with determinacy, CP, references, tasks 2–4) | `0ff74400d105991ef0294e9015fcb525deec56e47430699ff4a38b37759d7316` |
| `kappa_repro_results.json` (all outputs of tasks 1–4) | `1ebba5c6e8aabeee4a5c7c01818862a2fa189204225149eac3554a848bb8b622` |
| `grid_decisions.py` (extra: decisions on the 0.5 grid, from the stored k, using kappa_repro's Holm) | `ddd99b4fe287b64ce09526e106ef9613bd9d53fbd7db12c94eae212744c9e1fb` |
| `grid_decisions.json` | `5cdbb2277d4647a7d49cb9eb76036c368411af36335ad751b9883c4b0e111ea7` |
| `null_moments_check.py` (extra reference check, see below) | `c2bfb7182e083d01956453cec9f400d762ea5400267e88de0de815036d3ac146` |
| `null_moments_check.json` | `0883752c77b89850a6d8fe4a2271d37fe6de569c8a7a0088285372376befcf18` |
| `make_tables.py` (renders the tables below) | `6ac793f44134ccbcfee5a9a23b9f96e8bb8518b4698d513da620d42da8a825d7` |

Frozen code reused: `nd-unfolding/s5p_inference.py` (sha256 `55239135…`, which matches the manifests' `s5p_inference_sha256`).
Only `stat_total` and `stat_shape` were imported from it. I re-implemented the following from `s5p_joint.py`
(sha256 `2cd98235…`, which also matches the manifests), `s5p_inference.py` and amendment 7 `claims.rejection`:
- the metric W = V[dom,dom] + diag(var[dom]);
- the seed-keyed residual draw `rng([surrogate_seed0, pseudo_seed, 0x4A02]).normal(size=109) * sqrt(var)`, with the domain applied after the draw;
- the claim rule (max k over the variants, so max p because B is fixed within a null);
- Holm with determinacy (stable sort by p in insertion order; below if hi < th; above if lo > th; otherwise straddles);
- the Clopper–Pearson interval.

T_obs uses `f_data` with no draw. I ran it with numpy 1.26.4, scipy 1.15.2 and Python 3.12.2 on macOS.

## Task 1: reference verdicts (all AGREE)

| reading | check | result |
|---|---|---|
| frozen | family A, κ = 2, against `joint-evaluate.json` `tests.<G>.total/shape` and `decisions` (k, B, p rtol 1e-12, threshold, CP interval, decision) | AGREE, 10/10 tests, 0 problems |
| frozen | family B, κ = 3, against `tests.<G>.total_robust/shape_robust` and `decisions_robust_kappa` | AGREE, 10/10, 0 problems |
| union | family A, κ = 2, against `resolved-evaluate.json` | AGREE, 10/10, 0 problems |
| union | family B, κ = 3, against `resolved-evaluate.json` | AGREE, 10/10, 0 problems |
| both | extra check: T_total_obs and T_shape_obs (rtol 1e-12), and the k of every recorded variant (`variants.*` including m1±2, `robustness_variants` m1±3) | AGREE |
| both | extra check: the median and SD (ddof 0) of the null T for every recorded variant against `null_T_{total,shape}_{median,sd}` | 92 comparisons per reading; max relative difference 2.06e-14 (frozen), 2.01e-14 (union) |

The required references are dominated by k = 0 (only NuWro shape has k = 1 or 2). Agreement on k and the
decisions alone would therefore be a weak test of the per-experiment draw convention. The null-moment comparison
depends on every pseudo-experiment's residual draw and closes that gap.

Legend for the compact tables: R = rejected, U = undetermined, N = not rejected; (b/s/a) = the test's **own** CP
interval lies below, straddles or lies above its **own** Holm threshold. Abbreviations: Tune = MnvTune_v1,
GCV = GENIE_2_12_10_CV, GMEC = GENIE_2_12_10_MEC, NuWro = NuWro_21_09, GiBUU = GiBUU_2019; :T = total, :S = shape.

## Task 2: frozen reading, family A (compact)

| test | 0.0 | 2.0 | 3.0 | 5.2546875 | 5.25625 | 5.6640625 | 5.665625 | 6.478125 | 6.4796875 | 7.2109375 | 7.2125 | 8.459375 | 8.4609375 | 10.328125 | 10.3296875 | 12.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tune:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |
| Tune:S | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |
| GCV:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=4 (b) | U k=5 (s) | N k=1072 (a) | U k=1074 (a) | N k=1366 (a) |
| GCV:S | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=27 (b) | U k=27 (b) | U k=54 (s) | N k=54 (s) | N k=112 (a) | U k=112 (a) | U k=185 (a) | U k=186 (a) | N k=352 (a) | U k=352 (a) | N k=641 (a) | U k=641 (a) | N k=799 (a) |
| GMEC:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=3 (b) | U k=4 (s) | N k=1065 (a) |
| GMEC:S | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=22 (b) | U k=23 (s) | U k=45 (s) | N k=46 (a) | N k=119 (a) | U k=119 (a) | U k=267 (a) | U k=268 (a) | N k=544 (a) | U k=544 (a) | N k=876 (a) | U k=876 (a) | N k=1034 (a) |
| NuWro:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=4 (b) | R k=4 (b) | R k=17 (b) | U k=17 (b) | U k=114 (a) | U k=114 (a) | N k=785 (a) | U k=786 (a) | N k=1727 (a) | U k=1727 (a) | N k=1751 (a) |
| NuWro:S | R k=1 (b) | R k=1 (b) | R k=2 (b) | R k=4 (b) | R k=4 (b) | R k=7 (b) | R k=7 (b) | R k=12 (b) | U k=13 (s) | U k=18 (s) | U k=18 (s) | N k=36 (a) | U k=36 (a) | N k=89 (a) | U k=89 (a) | N k=137 (a) |
| GiBUU:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=6 (b) | U k=7 (s) | N k=400 (a) | U k=401 (a) | N k=1349 (a) | U k=1349 (a) | N k=1351 (a) |
| GiBUU:S | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=1 (b) |

## Task 3: union reading, family A (compact)

| test | 5.16875 | 5.1703125 | 6.540625 | 6.5421875 | 6.8453125 | 6.846875 |
|---|---|---|---|---|---|---|
| Tune:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |
| Tune:S | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |
| GCV:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |
| GCV:S | R k=26 (b) | U k=26 (b) | N k=119 (a) | U k=120 (a) | N k=145 (a) | U k=145 (a) |
| GMEC:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |
| GMEC:S | R k=23 (b) | U k=24 (s) | N k=134 (a) | U k=134 (a) | N k=204 (a) | U k=204 (a) |
| NuWro:T | R k=0 (b) | R k=0 (b) | R k=19 (b) | U k=20 (s) | N k=45 (a) | U k=46 (a) |
| NuWro:S | R k=4 (b) | R k=4 (b) | R k=13 (b) | R k=13 (b) | R k=13 (b) | U k=14 (s) |
| GiBUU:T | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=1 (b) | R k=1 (b) |
| GiBUU:S | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) | R k=0 (b) |

## Task 4: monotonicity spot-check, frozen reading, family A: claim k on κ = 0, 0.5, …, 12

| test | 0 | 0.5 | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 | 6.5 | 7 | 7.5 | 8 | 8.5 | 9 | 9.5 | 10 | 10.5 | 11 | 11.5 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tune:T | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Tune:S | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| GCV:T | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 85 | 366 | 769 | 1199 | 1355 | 1366 | 1366 |
| GCV:S | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 9 | 22 | 45 | 75 | 114 | 159 | 217 | 283 | 359 | 436 | 530 | 608 | 669 | 718 | 757 | 799 |
| GMEC:T | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 13 | 145 | 573 | 1065 |
| GMEC:S | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 6 | 18 | 29 | 75 | 121 | 226 | 318 | 434 | 554 | 655 | 743 | 830 | 900 | 952 | 996 | 1034 |
| NuWro:T | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 5 | 17 | 72 | 189 | 450 | 817 | 1214 | 1521 | 1665 | 1737 | 1748 | 1751 | 1751 |
| NuWro:S | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 3 | 3 | 3 | 4 | 5 | 9 | 13 | 17 | 20 | 30 | 37 | 52 | 68 | 81 | 91 | 102 | 115 | 137 |
| GiBUU:T | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 22 | 149 | 442 | 875 | 1224 | 1328 | 1351 | 1351 | 1351 | 1351 |
| GiBUU:S | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

Decreases: none

Extra (not requested): the family decisions on the same grid, computed from the k above with the same Holm code.
"Returns to rejected" means a decision that becomes "rejected" again after being lost.

```
MnvTune_v1:total           R R R R R R R R R R R R R R R R R R R R R R R R R
MnvTune_v1:shape           R R R R R R R R R R R R R R R R R R R R R R R R R
GENIE_2_12_10_CV:total     R R R R R R R R R R R R R R R R R U N N N U N N N
GENIE_2_12_10_CV:shape     R R R R R R R R R R R U N U U U N U N N N U N N N
GENIE_2_12_10_MEC:total    R R R R R R R R R R R R R R R R R R R R R U N N N
GENIE_2_12_10_MEC:shape    R R R R R R R R R R R U N U U U N U N N N U N N N
NuWro_21_09:total          R R R R R R R R R R R R R U U U N U N N N U N N N
NuWro_21_09:shape          R R R R R R R R R R R R R U U U N U N N N U N N N
GiBUU_2019:total           R R R R R R R R R R R R R R R U N U N N N U N N N
GiBUU_2019:shape           R R R R R R R R R R R R R R R R R R R R R R R R R
returns to rejected: none
```

## Surprises and observations

1. **Claim k is monotone, but the three-state decisions are not.** No claim k decreases on the 0.5 grid, and no
   decision returns to "rejected" once lost, either on the grid or at the requested points. However, "undetermined"
   and "not rejected" alternate as κ grows. Examples: GCV:S goes R,…,U,U,N,N,U,U,U,N,U,N,U,N across the task-2 points,
   and GCV:T is N at 10.328125 but U at 10.3296875. The cause is Holm's step-down. The state passed to later steps is
   set by the first failing step, so a test earlier in the order that starts to straddle turns an inherited
   "not rejected" into "undetermined". The spec's "first loss" threshold is well defined. A threshold for "not
   rejected" would not be, because it is not monotone.
2. **Inherited losses with own status "below".** At κ = 5.25625 (frozen), GCV:S has k = 27 and its own interval lies
   below its own threshold, yet it is "undetermined". It inherits this from GMEC:S, whose k = 23 straddles step 9's
   threshold of 0.025. The same pattern appears at κ = 6.4796875: NuWro:T has k = 17 (below) and inherits from
   NuWro:S, whose k = 13 straddles. The union reading shows the same at 5.1703125 (GCV:S inherits from GMEC:S).
3. **Every requested adjacent pair brackets exactly one decision change.** In each case, the change happens when
   the first failing test's own interval crosses its threshold:

   | reading | κ pair | test whose interval crosses |
   |---|---|---|
   | frozen | [5.2546875, 5.25625] | GMEC:S, k 22 → 23 (b → s): the first loss of any rejection (GMEC:S own, GCV:S inherited) |
   | frozen | [5.6640625, 5.665625] | GMEC:S, k 45 → 46 (s → a): U → N |
   | frozen | [6.478125, 6.4796875] | NuWro:S, k 12 → 13 (b → s): both NuWro tests lose R |
   | frozen | [7.2109375, 7.2125] | GiBUU:T, k 6 → 7 (b → s) |
   | frozen | [8.459375, 8.4609375] | GCV:T, k 4 → 5 (b → s): later tests go N → U |
   | frozen | [10.328125, 10.3296875] | GMEC:T, k 3 → 4 (b → s): later tests go N → U |
   | union | [5.16875, 5.1703125] | GMEC:S, k 23 → 24 (b → s): the first loss (GCV:S inherited) |
   | union | [6.540625, 6.5421875] | NuWro:T, k 19 → 20 (b → s) |
   | union | [6.8453125, 6.846875] | NuWro:S, k 13 → 14 (b → s) |
4. **Still rejected at κ = 12 (frozen):** Tune:T and Tune:S, which do not depend on κ, and GiBUU:S (k = 1 at
   κ = 12). These have thresholds "> 12". The first κ among the requested points at which each test is no longer
   rejected:

   | test | first κ not rejected |
   |---|---|
   | GMEC:S, GCV:S | 5.25625 |
   | NuWro:T, NuWro:S | 6.4796875 |
   | GiBUU:T | 7.2125 |
   | GCV:T | 8.4609375 |
   | GMEC:T | 10.3296875 |

   The 0.5 grid gives the same ordering.
5. NuWro's process shift is identically zero (manifest `magnitude` 0.0), so its three c·S variants coincide.
6. The RC4 copy lacks `code/{replay_inference,make_reading_b,verify_rc,w1_projected_tests}.py`, which
   SHA256SUMS lists. Presumably they were withheld for independence. Every file that is present verifies.

## Scope

This is a sensitivity of the frozen calculation along the single direction ±κ·δ_M1. It is not convergence,
not the true sub-fine residual, and not detector-model adequacy. I did not run the full 241-point grid or
the bisection refinement of spec §4. Those were not requested here; tasks 2–3 evaluate only the listed κ values.

## Appendix A: task 2 full tables (frozen, family A), in Holm order

**kappa = 0.0**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1751 | 0.000570776 | 1 | 0.005 | [0, 0.00210451] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 2 | 0.00555556 | [0, 0.00269685] | below | rejected |
| GENIE_2_12_10_CV:shape | 0 | 1366 | 0.000731529 | 3 | 0.00625 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 4 | 0.00714286 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 5 | 0.00833333 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 6 | 0.01 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 7 | 0.0125 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 8 | 0.0166667 | [0, 0.00274298] | below | rejected |
| GENIE_2_12_10_MEC:shape | 0 | 1343 | 0.000744048 | 9 | 0.025 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 1 | 1751 | 0.00114155 | 10 | 0.05 | [1.4459e-05, 0.00317783] | below | rejected |

**kappa = 2.0**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1751 | 0.000570776 | 1 | 0.005 | [0, 0.00210451] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 2 | 0.00555556 | [0, 0.00269685] | below | rejected |
| GENIE_2_12_10_CV:shape | 0 | 1366 | 0.000731529 | 3 | 0.00625 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 4 | 0.00714286 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 5 | 0.00833333 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 6 | 0.01 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 7 | 0.0125 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 8 | 0.0166667 | [0, 0.00274298] | below | rejected |
| GENIE_2_12_10_MEC:shape | 0 | 1343 | 0.000744048 | 9 | 0.025 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 1 | 1751 | 0.00114155 | 10 | 0.05 | [1.4459e-05, 0.00317783] | below | rejected |

**kappa = 3.0**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1751 | 0.000570776 | 1 | 0.005 | [0, 0.00210451] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 2 | 0.00555556 | [0, 0.00269685] | below | rejected |
| GENIE_2_12_10_CV:shape | 0 | 1366 | 0.000731529 | 3 | 0.00625 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 4 | 0.00714286 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 5 | 0.00833333 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 6 | 0.01 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 7 | 0.0125 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 8 | 0.0166667 | [0, 0.00274298] | below | rejected |
| GENIE_2_12_10_MEC:shape | 0 | 1343 | 0.000744048 | 9 | 0.025 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 2 | 1751 | 0.00171233 | 10 | 0.05 | [0.000138356, 0.00411988] | below | rejected |

**kappa = 5.2546875**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1751 | 0.000570776 | 1 | 0.005 | [0, 0.00210451] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 2 | 0.00555556 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 4 | 0.00714286 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 5 | 0.00833333 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 6 | 0.01 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 7 | 0.0125 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 4 | 1751 | 0.00285388 | 8 | 0.0166667 | [0.000622764, 0.00583858] | below | rejected |
| GENIE_2_12_10_MEC:shape | 22 | 1343 | 0.0171131 | 9 | 0.025 | [0.0102938, 0.0246969] | below | rejected |
| GENIE_2_12_10_CV:shape | 27 | 1366 | 0.0204828 | 10 | 0.05 | [0.0130652, 0.0286286] | below | rejected |

**kappa = 5.25625**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1751 | 0.000570776 | 1 | 0.005 | [0, 0.00210451] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 2 | 0.00555556 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 4 | 0.00714286 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 5 | 0.00833333 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 6 | 0.01 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 7 | 0.0125 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 4 | 1751 | 0.00285388 | 8 | 0.0166667 | [0.000622764, 0.00583858] | below | rejected |
| GENIE_2_12_10_MEC:shape | 23 | 1343 | 0.0178571 | 9 | 0.025 | [0.0108865, 0.0255869] | straddles | undetermined |
| GENIE_2_12_10_CV:shape | 27 | 1366 | 0.0204828 | 10 | 0.05 | [0.0130652, 0.0286286] | below | undetermined |

**kappa = 5.6640625**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 1 | 0.005 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 4 | 0.00714286 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 5 | 0.00833333 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 6 | 0.01 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:total | 4 | 1751 | 0.00285388 | 7 | 0.0125 | [0.000622764, 0.00583858] | below | rejected |
| NuWro_21_09:shape | 7 | 1751 | 0.00456621 | 8 | 0.0166667 | [0.00160875, 0.00821937] | below | rejected |
| GENIE_2_12_10_MEC:shape | 45 | 1343 | 0.0342262 | 9 | 0.025 | [0.0245432, 0.0445801] | straddles | undetermined |
| GENIE_2_12_10_CV:shape | 54 | 1366 | 0.0402341 | 10 | 0.05 | [0.0298342, 0.0512675] | straddles | undetermined |

**kappa = 5.665625**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 1 | 0.005 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 4 | 0.00714286 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 5 | 0.00833333 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 6 | 0.01 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:total | 4 | 1751 | 0.00285388 | 7 | 0.0125 | [0.000622764, 0.00583858] | below | rejected |
| NuWro_21_09:shape | 7 | 1751 | 0.00456621 | 8 | 0.0166667 | [0.00160875, 0.00821937] | below | rejected |
| GENIE_2_12_10_MEC:shape | 46 | 1343 | 0.0349702 | 9 | 0.025 | [0.0251835, 0.0454245] | above | not rejected |
| GENIE_2_12_10_CV:shape | 54 | 1366 | 0.0402341 | 10 | 0.05 | [0.0298342, 0.0512675] | straddles | not rejected |

**kappa = 6.478125**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 1 | 0.005 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 4 | 0.00714286 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 5 | 0.00833333 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 6 | 0.01 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 12 | 1751 | 0.00742009 | 7 | 0.0125 | [0.00354603, 0.0119406] | below | rejected |
| NuWro_21_09:total | 17 | 1751 | 0.010274 | 8 | 0.0166667 | [0.00566558, 0.0154993] | below | rejected |
| GENIE_2_12_10_CV:shape | 112 | 1366 | 0.0826628 | 9 | 0.025 | [0.0679878, 0.0978223] | above | not rejected |
| GENIE_2_12_10_MEC:shape | 119 | 1343 | 0.0892857 | 10 | 0.05 | [0.07395, 0.105093] | above | not rejected |

**kappa = 6.4796875**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 1 | 0.005 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000739645 | 4 | 0.00714286 | [0, 0.00272676] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 5 | 0.00833333 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 6 | 0.01 | [0, 0.00274298] | below | rejected |
| NuWro_21_09:shape | 13 | 1751 | 0.00799087 | 7 | 0.0125 | [0.00395889, 0.0126624] | straddles | undetermined |
| NuWro_21_09:total | 17 | 1751 | 0.010274 | 8 | 0.0166667 | [0.00566558, 0.0154993] | below | undetermined |
| GENIE_2_12_10_CV:shape | 112 | 1366 | 0.0826628 | 9 | 0.025 | [0.0679878, 0.0978223] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 119 | 1343 | 0.0892857 | 10 | 0.05 | [0.07395, 0.105093] | above | undetermined |

**kappa = 7.2109375**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 1 | 0.005 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 4 | 0.00714286 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 5 | 0.00833333 | [0, 0.00274298] | below | rejected |
| GiBUU_2019:total | 6 | 1351 | 0.00517751 | 6 | 0.01 | [0.00163152, 0.00964129] | below | rejected |
| NuWro_21_09:shape | 18 | 1751 | 0.0108447 | 7 | 0.0125 | [0.00610354, 0.0161981] | straddles | undetermined |
| NuWro_21_09:total | 114 | 1751 | 0.0656393 | 8 | 0.0166667 | [0.0540011, 0.0776932] | above | undetermined |
| GENIE_2_12_10_CV:shape | 185 | 1366 | 0.136064 | 9 | 0.025 | [0.117719, 0.154729] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 267 | 1343 | 0.199405 | 10 | 0.05 | [0.177769, 0.221175] | above | undetermined |

**kappa = 7.2125**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000731529 | 1 | 0.005 | [0, 0.00269685] | below | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 3 | 0.00625 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 4 | 0.00714286 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 5 | 0.00833333 | [0, 0.00274298] | below | rejected |
| GiBUU_2019:total | 7 | 1351 | 0.00591716 | 6 | 0.01 | [0.00208563, 0.0106462] | straddles | undetermined |
| NuWro_21_09:shape | 18 | 1751 | 0.0108447 | 7 | 0.0125 | [0.00610354, 0.0161981] | straddles | undetermined |
| NuWro_21_09:total | 114 | 1751 | 0.0656393 | 8 | 0.0166667 | [0.0540011, 0.0776932] | above | undetermined |
| GENIE_2_12_10_CV:shape | 186 | 1366 | 0.136796 | 9 | 0.025 | [0.118408, 0.155501] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 268 | 1343 | 0.200149 | 10 | 0.05 | [0.178482, 0.221948] | above | undetermined |

**kappa = 8.459375**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 1 | 0.005 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 3 | 0.00625 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 4 | 0.00714286 | [0, 0.00274298] | below | rejected |
| GENIE_2_12_10_CV:total | 4 | 1366 | 0.00365764 | 5 | 0.00833333 | [0.00079841, 0.00748039] | below | rejected |
| NuWro_21_09:shape | 36 | 1751 | 0.0211187 | 6 | 0.01 | [0.0144403, 0.0283505] | above | not rejected |
| GENIE_2_12_10_CV:shape | 352 | 1366 | 0.25823 | 7 | 0.0125 | [0.234669, 0.281752] | above | not rejected |
| GiBUU_2019:total | 400 | 1351 | 0.296598 | 8 | 0.0166667 | [0.271829, 0.321216] | above | not rejected |
| GENIE_2_12_10_MEC:shape | 544 | 1343 | 0.405506 | 9 | 0.025 | [0.378668, 0.431875] | above | not rejected |
| NuWro_21_09:total | 785 | 1751 | 0.44863 | 10 | 0.05 | [0.424839, 0.471965] | above | not rejected |

**kappa = 8.4609375**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 1 | 0.005 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 3 | 0.00625 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744048 | 4 | 0.00714286 | [0, 0.00274298] | below | rejected |
| GENIE_2_12_10_CV:total | 5 | 1366 | 0.00438917 | 5 | 0.00833333 | [0.00118953, 0.00852114] | straddles | undetermined |
| NuWro_21_09:shape | 36 | 1751 | 0.0211187 | 6 | 0.01 | [0.0144403, 0.0283505] | above | undetermined |
| GENIE_2_12_10_CV:shape | 352 | 1366 | 0.25823 | 7 | 0.0125 | [0.234669, 0.281752] | above | undetermined |
| GiBUU_2019:total | 401 | 1351 | 0.297337 | 8 | 0.0166667 | [0.27255, 0.321972] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 544 | 1343 | 0.405506 | 9 | 0.025 | [0.378668, 0.431875] | above | undetermined |
| NuWro_21_09:total | 786 | 1751 | 0.449201 | 10 | 0.05 | [0.425406, 0.472538] | above | undetermined |

**kappa = 10.328125**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 1 | 0.005 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 3 | 0.00625 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 3 | 1343 | 0.00297619 | 4 | 0.00714286 | [0.000460901, 0.00651412] | below | rejected |
| NuWro_21_09:shape | 89 | 1751 | 0.0513699 | 5 | 0.00833333 | [0.041015, 0.0621786] | above | not rejected |
| GENIE_2_12_10_CV:shape | 641 | 1366 | 0.469642 | 6 | 0.01 | [0.442513, 0.496126] | above | not rejected |
| GENIE_2_12_10_MEC:shape | 876 | 1343 | 0.65253 | 7 | 0.0125 | [0.626116, 0.677758] | above | not rejected |
| GENIE_2_12_10_CV:total | 1072 | 1366 | 0.784931 | 8 | 0.0166667 | [0.762012, 0.806302] | above | not rejected |
| NuWro_21_09:total | 1727 | 1751 | 0.986301 | 9 | 0.025 | [0.979674, 0.991199] | above | not rejected |
| GiBUU_2019:total | 1349 | 1351 | 0.998521 | 10 | 0.05 | [0.994663, 0.999821] | above | not rejected |

**kappa = 10.3296875**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 1 | 0.005 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000739645 | 3 | 0.00625 | [0, 0.00272676] | below | rejected |
| GENIE_2_12_10_MEC:total | 4 | 1343 | 0.00372024 | 4 | 0.00714286 | [0.000812093, 0.0076082] | straddles | undetermined |
| NuWro_21_09:shape | 89 | 1751 | 0.0513699 | 5 | 0.00833333 | [0.041015, 0.0621786] | above | undetermined |
| GENIE_2_12_10_CV:shape | 641 | 1366 | 0.469642 | 6 | 0.01 | [0.442513, 0.496126] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 876 | 1343 | 0.65253 | 7 | 0.0125 | [0.626116, 0.677758] | above | undetermined |
| GENIE_2_12_10_CV:total | 1074 | 1366 | 0.786394 | 8 | 0.0166667 | [0.763527, 0.807709] | above | undetermined |
| NuWro_21_09:total | 1727 | 1751 | 0.986301 | 9 | 0.025 | [0.979674, 0.991199] | above | undetermined |
| GiBUU_2019:total | 1349 | 1351 | 0.998521 | 10 | 0.05 | [0.994663, 0.999821] | above | undetermined |

**kappa = 12.0**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1365 | 0.000732064 | 1 | 0.005 | [0, 0.00269883] | below | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732064 | 2 | 0.00555556 | [0, 0.00269883] | below | rejected |
| GiBUU_2019:shape | 1 | 1351 | 0.00147929 | 3 | 0.00625 | [1.87399e-05, 0.00411712] | below | rejected |
| NuWro_21_09:shape | 137 | 1751 | 0.0787671 | 4 | 0.00714286 | [0.0660919, 0.0918247] | above | not rejected |
| GENIE_2_12_10_CV:shape | 799 | 1366 | 0.585223 | 5 | 0.00833333 | [0.558264, 0.611209] | above | not rejected |
| GENIE_2_12_10_MEC:shape | 1034 | 1343 | 0.770089 | 6 | 0.01 | [0.746459, 0.79219] | above | not rejected |
| GENIE_2_12_10_MEC:total | 1065 | 1343 | 0.793155 | 7 | 0.0125 | [0.77033, 0.814382] | above | not rejected |
| GENIE_2_12_10_CV:total | 1366 | 1366 | 1 | 8 | 0.0166667 | [0.997303, 1] | above | not rejected |
| NuWro_21_09:total | 1751 | 1751 | 1 | 9 | 0.025 | [0.997895, 1] | above | not rejected |
| GiBUU_2019:total | 1351 | 1351 | 1 | 10 | 0.05 | [0.997273, 1] | above | not rejected |

## Appendix B: task 3 full tables (union, family A), in Holm order

**kappa = 5.16875**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1800 | 0.000555247 | 1 | 0.005 | [0, 0.00204728] | below | rejected |
| MnvTune_v1:total | 0 | 1400 | 0.000713776 | 2 | 0.00555556 | [0, 0.00263145] | below | rejected |
| MnvTune_v1:shape | 0 | 1400 | 0.000713776 | 3 | 0.00625 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1400 | 0.000713776 | 4 | 0.00714286 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1400 | 0.000713776 | 5 | 0.00833333 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:total | 0 | 1400 | 0.000713776 | 6 | 0.01 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:shape | 0 | 1400 | 0.000713776 | 7 | 0.0125 | [0, 0.00263145] | below | rejected |
| NuWro_21_09:shape | 4 | 1800 | 0.00277624 | 8 | 0.0166667 | [0.000605802, 0.00567991] | below | rejected |
| GENIE_2_12_10_MEC:shape | 23 | 1400 | 0.0171306 | 9 | 0.025 | [0.0104421, 0.0245495] | below | rejected |
| GENIE_2_12_10_CV:shape | 26 | 1400 | 0.0192719 | 10 | 0.05 | [0.0121664, 0.0270937] | below | rejected |

**kappa = 5.1703125**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| NuWro_21_09:total | 0 | 1800 | 0.000555247 | 1 | 0.005 | [0, 0.00204728] | below | rejected |
| MnvTune_v1:total | 0 | 1400 | 0.000713776 | 2 | 0.00555556 | [0, 0.00263145] | below | rejected |
| MnvTune_v1:shape | 0 | 1400 | 0.000713776 | 3 | 0.00625 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1400 | 0.000713776 | 4 | 0.00714286 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1400 | 0.000713776 | 5 | 0.00833333 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:total | 0 | 1400 | 0.000713776 | 6 | 0.01 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:shape | 0 | 1400 | 0.000713776 | 7 | 0.0125 | [0, 0.00263145] | below | rejected |
| NuWro_21_09:shape | 4 | 1800 | 0.00277624 | 8 | 0.0166667 | [0.000605802, 0.00567991] | below | rejected |
| GENIE_2_12_10_MEC:shape | 24 | 1400 | 0.0178444 | 9 | 0.025 | [0.0110138, 0.0254004] | straddles | undetermined |
| GENIE_2_12_10_CV:shape | 26 | 1400 | 0.0192719 | 10 | 0.05 | [0.0121664, 0.0270937] | below | undetermined |

**kappa = 6.540625**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1400 | 0.000713776 | 1 | 0.005 | [0, 0.00263145] | below | rejected |
| MnvTune_v1:shape | 0 | 1400 | 0.000713776 | 2 | 0.00555556 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1400 | 0.000713776 | 3 | 0.00625 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1400 | 0.000713776 | 4 | 0.00714286 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:total | 0 | 1400 | 0.000713776 | 5 | 0.00833333 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:shape | 0 | 1400 | 0.000713776 | 6 | 0.01 | [0, 0.00263145] | below | rejected |
| NuWro_21_09:shape | 13 | 1800 | 0.00777346 | 7 | 0.0125 | [0.00385097, 0.0123186] | below | rejected |
| NuWro_21_09:total | 19 | 1800 | 0.0111049 | 8 | 0.0166667 | [0.00636676, 0.0164349] | below | rejected |
| GENIE_2_12_10_CV:shape | 119 | 1400 | 0.0856531 | 9 | 0.025 | [0.0709173, 0.100852] | above | not rejected |
| GENIE_2_12_10_MEC:shape | 134 | 1400 | 0.0963597 | 10 | 0.05 | [0.0808072, 0.112342] | above | not rejected |

**kappa = 6.5421875**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1400 | 0.000713776 | 1 | 0.005 | [0, 0.00263145] | below | rejected |
| MnvTune_v1:shape | 0 | 1400 | 0.000713776 | 2 | 0.00555556 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1400 | 0.000713776 | 3 | 0.00625 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1400 | 0.000713776 | 4 | 0.00714286 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:total | 0 | 1400 | 0.000713776 | 5 | 0.00833333 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:shape | 0 | 1400 | 0.000713776 | 6 | 0.01 | [0, 0.00263145] | below | rejected |
| NuWro_21_09:shape | 13 | 1800 | 0.00777346 | 7 | 0.0125 | [0.00385097, 0.0123186] | below | rejected |
| NuWro_21_09:total | 20 | 1800 | 0.0116602 | 8 | 0.0166667 | [0.0067998, 0.0171083] | straddles | undetermined |
| GENIE_2_12_10_CV:shape | 120 | 1400 | 0.0863669 | 9 | 0.025 | [0.0715746, 0.10162] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 134 | 1400 | 0.0963597 | 10 | 0.05 | [0.0808072, 0.112342] | above | undetermined |

**kappa = 6.8453125**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1400 | 0.000713776 | 1 | 0.005 | [0, 0.00263145] | below | rejected |
| MnvTune_v1:shape | 0 | 1400 | 0.000713776 | 2 | 0.00555556 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1400 | 0.000713776 | 3 | 0.00625 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1400 | 0.000713776 | 4 | 0.00714286 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:shape | 0 | 1400 | 0.000713776 | 5 | 0.00833333 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:total | 1 | 1400 | 0.00142755 | 6 | 0.01 | [1.8084e-05, 0.00397325] | below | rejected |
| NuWro_21_09:shape | 13 | 1800 | 0.00777346 | 7 | 0.0125 | [0.00385097, 0.0123186] | below | rejected |
| NuWro_21_09:total | 45 | 1800 | 0.0255414 | 8 | 0.0166667 | [0.0182923, 0.0333101] | above | not rejected |
| GENIE_2_12_10_CV:shape | 145 | 1400 | 0.104211 | 9 | 0.025 | [0.088098, 0.12073] | above | not rejected |
| GENIE_2_12_10_MEC:shape | 204 | 1400 | 0.146324 | 10 | 0.05 | [0.127634, 0.165295] | above | not rejected |

**kappa = 6.846875**

| test | k | B | p | step | threshold | CP 95% | own | decision |
|---|---|---|---|---|---|---|---|---|
| MnvTune_v1:total | 0 | 1400 | 0.000713776 | 1 | 0.005 | [0, 0.00263145] | below | rejected |
| MnvTune_v1:shape | 0 | 1400 | 0.000713776 | 2 | 0.00555556 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_CV:total | 0 | 1400 | 0.000713776 | 3 | 0.00625 | [0, 0.00263145] | below | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1400 | 0.000713776 | 4 | 0.00714286 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:shape | 0 | 1400 | 0.000713776 | 5 | 0.00833333 | [0, 0.00263145] | below | rejected |
| GiBUU_2019:total | 1 | 1400 | 0.00142755 | 6 | 0.01 | [1.8084e-05, 0.00397325] | below | rejected |
| NuWro_21_09:shape | 14 | 1800 | 0.00832871 | 7 | 0.0125 | [0.00425852, 0.0130154] | straddles | undetermined |
| NuWro_21_09:total | 46 | 1800 | 0.0260966 | 8 | 0.0166667 | [0.0187692, 0.0339416] | above | undetermined |
| GENIE_2_12_10_CV:shape | 145 | 1400 | 0.104211 | 9 | 0.025 | [0.088098, 0.12073] | above | undetermined |
| GENIE_2_12_10_MEC:shape | 204 | 1400 | 0.146324 | 10 | 0.05 | [0.127634, 0.165295] | above | undetermined |


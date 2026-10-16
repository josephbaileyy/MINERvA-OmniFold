# Per-period unfold test of the playlist spread: REPORT (2026-10-15)

**Answer: the 1G–1M p_∥ step at 8 GeV/c SURVIVES UNFOLDING, at about its reco-level size and far above the noise.
Diluted into the combined result, its p_∥ shape is NOT COVERED by VL175. The 1N–1P excess survives as a broad,
roughly 5% normalization, and is covered. J36 is negligible.**

**CITABLE FOR:**
- the control verdict;
- the per-period unfolded comparisons, their noise references and the step sizes;
- the J36 measurement after unfolding;
- the charge of the test.

**NOT CITABLE FOR:**
- which period is right, or the cause of either block;
- any change to VL175, or the size or construction of a playlist-consistency term. Joseph's ruling on adding one is
  recorded in [`../../../DECISION-20261015-joseph-playlist-consistency-term.md`](../../../DECISION-20261015-joseph-playlist-consistency-term.md);
  the term itself still has to be designed and reviewed;
- the 205-cell χ² as evidence (§4).

| field | content |
|---|---|
| `Authority` | [`../../../AUTHORIZATION-20261014-2d-closeout-period-unfold-test.md`](../../../AUTHORIZATION-20261014-2d-closeout-period-unfold-test.md) (≤ 6.0 node-h), after [`../playlist-spread-20261014/coverage/REPORT.md`](../playlist-spread-20261014/coverage/REPORT.md) found the spread PARTLY COVERED |
| `Who` | A Claude Opus 5.5 subagent of the paper-tighten lane (director) launched, monitored and analysed the test. The director wrote this REPORT, and re-measured what §6 lists |
| `Compute` | **1.9414 charged CPU node-h** over 40 `sacct` rows: 37 jobs plus 3 walltime retries. The ceiling is 6.0; the grant's median expectation was 1.04 (§5) |
| `Evidence` | [`outputs/`](outputs/): `control.json`, `roles.json`, `analysis.json`, `analysis.txt`, `sacct_charges.txt`, `retries.log.txt`, `launch_B0.log.txt`, `launch_B1.log.txt`, and the ad hoc `supplement_bias_dr.json` (§3). Unfold outputs: `/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/out/` |

## 1. Control: PASS

The all-12-playlist control `pu_CTRL_s42` (59795637), run by the same pipeline, reproduces both references inside
the 1e-8 tolerance on all 205 cells:

| reference | max rel. diff, cells | integral |
|---|---|---|
| XR-L0 `751380245dbb…` | 1.37e-11 | 6.9e-13 |
| `E_U` `4f5a1b6d…` | 3.0e-13 | 8.2e-15 |

The period inputs come from a pipeline that reproduces production. B1 ran only after this PASS.

## 2. Results

Periods:
- P_A = 1A–1F, the reference;
- P_B = 1G, 1L, 1M;
- P_C = 1N–1P.

The comparisons are:
- **raw:** the ratio of the unfolded results;
- **dr:** the double ratio, data over MC truth, which divides out each period's MC prior;
- **mc:** the MC truth ratio alone.

Brackets give the expected χ² from noise: data and MC bootstrap from 10 paired replicas, plus the seed draw. The step
is r[8,15) / r[1.5,8) − 1 in p_∥.

| comparison | integral | χ² p_∥ (16) | χ² p_T (14) | step | z |
|---|---:|---:|---:|---:|---:|
| raw P_B/P_A | −0.88% | **389.4** [20.5] | 22.5 [19.4] | +10.29% ± 0.43 | 24.1 |
| **dr P_B/P_A** | −2.32% | **381.8** [19.4] | 32.8 [17.8] | **+6.94% ± 0.41** | **16.8** |
| mc P_B/P_A | +1.48% | | | +3.13% | |
| raw P_C/P_A | +6.10% | 88.4 [20.0] | 21.0 [23.2] | +3.42% ± 0.43 | 8.0 |
| **dr P_C/P_A** | **+4.96%** | 96.5 [18.7] | 27.4 [22.2] | +2.00% ± 0.55 | 3.6 |
| mc P_C/P_A | +1.08% | | | +1.40% | |

**1G–1M.** At reco level, 1G–1M against 1A–1E had a step of **+6.10%**. After unfolding, the double ratio gives
**+6.94% ± 0.41**.
- **Shape:** the dr p_∥ marginal (16 bins, `analysis.json` `pz_marginal_shift_pct`) is low by 0.6–5.2% in its first
  10 bins. Its last six bins are +2.3%, +6.3%, +3.7%, +1.6%, +0.6% and +1.8%.
- **Against the noise:** across the 10 paired bootstrap draws, χ² p_∥ runs 6–40, against 382–389 observed.
- **p_T:** the raw p_T χ² is at noise level. The dr p_T χ² (32.8) is at the top of the draws (7–29), so it is
  borderline.

**1N–1P.** At reco level this block was +5.02% in total, with a +1.36% step. After unfolding it is +4.96% (dr) in
normalization, with a weak shape: step z = 3.6. With 10 replicas, that σ is uncertain by about ±22%.

## 3. Effect on the combined result, against VL175

This is the analogue of coverage (b): the shift of the combined result if a block's difference from P_A were a
bias, b_X = e_X (x_X / x_A − 1). It is set against the VL175 covariance.

| block | integral | χ² p_∥ | χ² p_T | largest marginal z | coverage (b), reco level |
|---|---:|---:|---:|---:|---|
| 1G–1M, raw (`bias_PB`) | −0.26% | **33.8** [1.8] | 2.0 [1.7] | p_∥ 0.68, p_T 0.19 | p_∥ **25.6** `sep` / **18.7** `interp`, p_T 2.3, integral −0.81% |
| 1G–1M, dr (supplement) | −0.68% | **33.1** | 2.85 | p_∥ 0.36, p_T 0.19 | |
| 1N–1P, raw (`bias_PC`) | +1.05% | 2.62 [0.59] | 0.62 [0.69] | | p_∥ 1.9, p_T 0.35, integral +0.77% |
| 1N–1P, dr (supplement) | +0.85% | 2.86 | 0.81 | p_∥ 0.26, p_T 0.22 | |

**How to read the 1G–1M row.** Bin by bin, the shift is small: every marginal z is below 0.7. The χ² is large because
the shift has a p_∥ shape that VL175 constrains tightly. So VL175 does not cover the shape, although no single bin
moves by much. The reco-level coverage verdict for 1G–1M is therefore confirmed after unfolding. 1N–1P is covered.

The dr rows are an ad hoc supplement, `supplement_bias_dr.json`. They were computed with the same metric, but outside
the frozen `analyze_periods.py`, and have no noise reference. The raw rows are the frozen script's output.

**J36** (the mix error of pooling playlists under one MC). The exposure-weighted sum of the period results is
**−0.084%** below the pooled result on the integral; the POT-weighted variant gives −0.075%.
- Its seed-only σ is 0.006%. The noise is a lower bound, because the common statistical part is not estimated.
- χ² p_∥ 0.77 [0.24], p_T 0.46 [0.24]; the lowest p_∥ bin is −0.57%.
- The sign matches the reco-level J36 estimate (+0.18%, pooled mix high), at about half the size.

J36 is negligible against VL175.

## 4. Limits

These were declared in the grant (§4) and are carried here:
- **One seed pair per period.** The seed draw contributes little: −0.15% on the B/A step, against 0.40% rms from the
  bootstrap. For the P_B step to fall below z = 3, the seed σ would have to be about 16 times the observed draw. The
  P_C shape rests on 10 bootstrap replicas and is marginal; another seed would not change that.
- **Regularization.** At 5 iterations, each period may be pulled toward its own MC prior, which would shrink the
  differences. Survival is conservative on that count. No closure test of step survival was run.
- **Response.** Each period is unfolded with its own MC response. The double ratio removes the MC truth, but not
  differences in response.
- **Approximate noise terms** for the comparisons against the pooled result, and for J36.
- **The 205-cell χ² is unusable.** Its noise expectation alone is 470–2,300, so the marginals lead.
- **The reference block.** P_A includes 1F, while the reco reference was 1A–1E.

## 5. Jobs and charge

All 37 jobs ran on QOS `shared`, with 64 CPUs and billing 64. The full table is in `outputs/sacct_charges.txt`.
- **B0** (59795637, 59795638, 59795835, 59795837): COMPLETED, 440–995 s.
- **B1** (59803426–59803478): 30 COMPLETED. Three P_C bootstrap replicas timed out at their 00:25:00 cap while still
  iterating:

  | job | jobid | elapsed | node | log reached |
  |---|---|---:|---|---|
  | `pu_PC_b01` | 59803463 | 1,526 s | `nid004074` | iteration 4 |
  | `pu_PC_b04` | 59803472 | 1,519 s | `nid004074` | iteration 4 |
  | `pu_PC_b05` | 59803473 | 1,525 s | `nid004078` | iteration 2 |

  The same work took 165–653 s on other nodes.
- **Retries** (59829084–59829086): COMPLETED in 228 s, 978 s and 139 s. Each ran at 00:50:00, the grant's maximum
  walltime, with those two nodes excluded. The three timeouts cost 0.317 node-h.

**Charge:** 1.9414 node-h, re-measured by the director from `sacct` (ElapsedRaw × billing ÷ 256, over 40 rows). The
median expectation was 1.04. Elapsed times did not scale linearly with sample size: P_C's central took 653 s, where
265 s was projected.

## 6. Deviations, and the director's checks

**Deviations:**
1. **The retries bypassed `launch.py`.** The bound `launch.py` refuses any name that already has a `sacct` row, so
   it has no retry path. The subagent therefore submitted the three retries by hand through the bound
   `sbatch_period_unfold.sh`, after computing the gate with the same formula (2.4730 ≤ 6.0) and logging it in
   `retries.log.txt`. This is within the grant's retry rule (§2: one per name, walltime failure, inside the
   ceiling), but not through the bound launcher.
2. **Supplement outside the frozen script:** `supplement_bias_dr.json` (§3).

**The director's checks:**
- **Digests.** On the cluster, the eight deployed scripts in `$NS/code/record/scripts/` have the grant's §3 digests.
- **The retries' own checks.** Each retry's log has five `: OK` digest checks, no `REFUSE` and no traceback, and
  reaches iteration 4. In `sacct`, each was granted `Timelimit 00:50:00`, QOS `shared` and billing 64.
- **The charge**, re-measured over all 40 `pu_*` rows: 1.9414.
- **The analysis, re-run independently.** The director re-ran `analyze_periods.py roles` and then `analyze` with the
  deployed script, `912af1dd…`, in a separate directory. `roles.json`, `analysis.json` and `analysis.txt` are
  byte-identical to the subagent's: `304e6833…`, `05edff61…` and `4024caa4…`.

## 7. What this means

- **1G–1M.** The p_∥ shape difference is real at the unfolded level. It is not removed by unfolding, and it is not
  covered by VL175 in the combined result. The director recommended a declared playlist-consistency uncertainty.
  Joseph agreed on 2026-10-15
  ([`../../../DECISION-20261015-joseph-playlist-consistency-term.md`](../../../DECISION-20261015-joseph-playlist-consistency-term.md)).
- **1N–1P** is a normalization difference that VL175 covers. It belongs in the same term's construction, for
  completeness.
- **J36** needs no action.

# Declaration: the KI 98 W-bias confirming test (2026-10-22)

**By** the measurement session, under [`ASSIGNMENT.md`](ASSIGNMENT.md) (director, PR #221). **Written** 2026-10-22,
before any job of this test was submitted and before any existing product was read for it. **Status:** awaiting the
director's binding. A run started before binding is held, not used.

**CITABLE FOR:** what will be run, what will be read, and the decision rule fixed before any result.

**NOT CITABLE FOR:** any result.

## The question

At the s5c E_avail-tilt grid point, a positive residual bias grows with truth W after the nominal-truth bias
correction (`state/2d-closeout/stageF/methods/M2-RATEFAIL-DIAGNOSIS.md`). It is not established whether it comes from:
- **the B/S change**: the signal rate drops by about 10% while the background does not, so B/S rises by 0.111·f_bkg;
- **the estimator alone**.

## Code, inputs and seeds

**Code.**
- **Experiments** run from the deploy that produced the 400 existing tilt products:
  `/pscratch/sd/j/josephrb/s5c-20260924/deploy/4bdfa75e`, pinned `4bdfa75e63581f1688d7c2cff118101f51ce9223`. It is
  clean at that pin, as checked 2026-10-22.
  - Its `s5c_pseudo.py` (`e423aaae…`) and `s5c_unfold.py` (`510d749a…`) are the bytes recorded in every existing
    product's meta.
  - Each task goes through that deploy's `s5c_array.sh` (`69305581…`). That gives the pinned-sha refusal, the guarded
    run, the inventory and the never-overwrite rule.
  - Between 4bdfa75e and 12d94181 (the interim evaluator's deploy) nothing that executes an experiment changed: the
    diff touches only coverage, queue and bias-correction tooling and tests.
- **No s5c code changes.**
- **Arm (c)'s input** is a derived background dump. `tools/mk_bkg_scaled.py` (`672ad881…`) multiplies both `bkg_w`
  (the Poisson means of the drawn background) and `bkg_nd` (the prediction that the purity subtraction removes) by
  0.9. It copies `bkg_reco` and the meta, keeps `meta.npz_sha256`, and records the scaling.
- **Reader:** `tools/ki98_read.py` (`a9373a9f…`), run with deploy 12d94181's `nd-unfolding` importable.
- **Launcher:** `measurement-paper/phase1/mp1/sbatch_mp1_s5c_packed.sh` (`2d74d4b8…`): one exclusive node, the
  table's lines as concurrent srun steps.

**Inputs, each checked by sha256:**
- `of_inputs_5d.npz` `07fccc1a…`, by `--expect-npz-sha256`;
- `runs/p2/bkg_dump.npz` `2addac8f…`, the dump every Tier-S experiment used, recorded in each product's meta;
- `contract.json` `d54fd7c9…`;
- `d1/bias_correction.json` `6c49c66c…` (β and se from 9 nominal development experiments);
- `tier_s/interim_400.json` `aa574c17…` (σ);
- the 200 Tier-S bootstrap replicas `runs/s_sigma/boot_b1..200.npz`. σ is recomputed from them and must match
  interim_400's σ to 1e-9 relative, or the reader refuses.

**Seeds:** 204000–204004, the first five declared Tier-S tilt validation seeds, chosen by position and not by value.
Each experiment runs in single-experiment mode with `--split-key` = `split_key_for(seed)`, the key batch mode derived
(541504895267644 for 204000).

**Tasks:** `tools/tasks.tsv` (`43826e75…`), 16 lines.

| arm | what | seeds | tasks |
|---|---|---|---:|
| (a) | as run: the **existing** Tier-S products `runs/s_valid/eavail_tilt_a0.2_s<seed>.npz` | 204000–204004 | 0 |
| control | arm (a) seed 204000 re-run in single-experiment mode. Its `xsec_flat`, `xtrue_flat` and `shape` must equal the existing product bitwise. | 204000 | 1 |
| (b) | tilt, `--no-background` | 204000–204004 | 5 |
| (b0) | nominal truth, `--no-background`: (b)'s own reference (below) | 204000–204004 | 5 |
| (c) | tilt, background ×0.9 | 204000–204004 | 5 |

**Why (c) restores B/S.** The tilt reweight is r = 1 + 0.2(E_avail/100 − 0.5) = 0.9 + 0.002·E_avail[GeV], because the
E_avail edges run from 0 to 100 GeV. So r lies between 0.900 and 0.906 for E_avail ≤ 3 GeV. Scaling the background by
0.9 returns B/S to its nominal value to within that range.

**Why (b) needs (b0).** Removing the background also removes the purity method's own nominal-truth closure bias,
which reaches about −4% at W ≥ 3 GeV (KI 75). So the d1 β, measured with background, does not apply to (b). Arm (b)
is referenced to β_nb, the per-cell mean over the five (b0) seeds of the raw relative bias f̂/f_true − 1.

## Separate read (no compute)

`ki98_read.py existing` reads the first 400 declared seeds at the tilt point (204000–204399) and at the nominal point
(200000–200399), all present as checked 2026-10-22. For every reported functional and band it gives:
- the raw relative bias e, as mean and SD;
- the corrected residual ρ, as mean, SE and SD.

This replaces the diagnosis's inferred table and is descriptive: no rule is attached.

## Metric

For a functional f with estimate f̂, own truth f_true and σ (Tier-S statistical σ):

ρ = (f̂ / (1 + β_ref) − f_true) / σ,

with β_ref = the d1 β for (a) and (c), and β_nb for (b) and (b0).

**Band aggregates** (declared, by the projection's own edges):
- EW cell k has E bin k // 6 and W bin k mod 6, with W edges 0, 1.1, 1.4, 1.8, 2.2, 3, 100 GeV.
- The bands are:
  - **W ≥ 3: EW5, 11, 17, 23, 29, 35, 41 (primary);**
  - W 2.2–3: EW4, 10, 16, 22, 28, 34, 40 (secondary);
  - W 1.4–2.2 and W < 1.4: 14 cells each;
  - J cells whose coarse W lower edge is ≥ 2.2: 25 cells.
- A band's estimate is the sum of its cells' corrected estimates, against the sum of their truths. Its σ comes from
  the same 200 replicas, with ddof = 1, exactly as `s5c_coverage.stat_covariance` computes it.

**Per-seed and five-seed quantities:**
- R_X = the mean of ρ over the five seeds of arm X.
- D_c = the mean of ρ_a − ρ_c, paired by seed. (a) and (c) share each seed's truth exactly, which the reader checks.
- D_b = the mean of ρ_a − ρ_b.

**Standard errors:**
- **SE_a and SE_c** = √(var_s/5 + S_β²). S_β is the correction's own SE in σ units, Σ se_k·|f̄_true,k|/(1 + β_k)
  over the band, taken as fully correlated within the band (conservative).
- **SE_b** = √(var(ρ_b)/5 + var(ρ_b0)/5).
- **SE_Dc** = sd(ρ_a − ρ_c)/√5.
- **SE_Db** = √(var(ρ_a − ρ_b)/5 + var(ρ_b0)/5).

**Reported for each arm:** R, D and SE, for EW9, EW10, EW16, EW17, J116, J224, total_integrated, EW_all_ones, every
band and all 153 functionals (`ki98.json`).

## Decision rule (fixed now; it may not change after any result)

k = 2.776, the two-sided 95% Student t with 4 degrees of freedom. It is applied to the **primary** band (EW, W ≥ 3).
The secondary band (EW, W 2.2–3) gets the same rule and is reported beside it as concordant or not; it does not
change the verdict.

1. **Preconditions.**
   - The control passes bitwise.
   - Every product passes its checks: truth, amplitude, no-background flag, seed, split key, config, estimator seed 42,
     iterations 5, threads 32, code sha256, background-dump sha256, and finiteness.
   - The residual is resolved in (a): R_a > k·SE_a.

   A failed control or product check gives INCOMPLETE. An unresolved residual in (a) gives UNDETERMINED.
2. **Patterns.**
   - (c) shows the **B/S pattern** if |R_c| ≤ k·SE_c and D_c > k·SE_Dc. It shows the **estimator pattern** if
     |D_c| ≤ k·SE_Dc and R_c > k·SE_c.
   - (b) is tested the same way, with R_b, SE_b, D_b and SE_Db.
3. **Verdict.**
   - **B/S CHANGE** if (c) shows the B/S pattern and (b) does not show the estimator pattern.
   - **ESTIMATOR** if (c) shows the estimator pattern and (b) does not show the B/S pattern.
   - **UNDETERMINED** otherwise. That covers a partial effect (both D_c and R_c beyond k·SE) and a conflict between
     (b) and (c).

These branches were exercised on constructed products before this declaration: a +1% shift in (a) only gives B/S
CHANGE; the same shift in all arms gives ESTIMATOR; no shift gives UNDETERMINED. A one-ulp change in the control
gives INCOMPLETE.

## Compute

- **Jobs:** 2, on **regular** QOS, account m3246, Joseph's own share.
- **Layout:** one exclusive node each, with 8 concurrent steps of 32 CPUs and 48G (the Tier-S launcher's step size).
  Lines 0–7 run on node 1 and 8–15 on node 2.
- **Time limit:** 15 min per job, so the worst case is **0.5 CPU node-h, the cap**.
- **Expected:** about 0.25 CPU node-h. Tier S measured 279 s per unfold at 8 per node, and single-experiment mode adds
  the input hash and load.
- **Outputs** go to `/pscratch/sd/j/josephrb/measurement-paper/ki98-wbias/` (inputs, tools, tables, unf, logs). None
  go to CFS.
- **Ledger:** every job goes in [`LEDGER.tsv`](LEDGER.tsv) here, with charge = ElapsedRaw × billing/256/3600 from
  sacct.
- **Failures.** A failed or killed task is a failure, never a result. Its lines may be re-run once, in one job, only
  if the charge so far plus that job's time limit stays within 0.5. Otherwise the verdict is INCOMPLETE.

## Order after binding

1. Build the scaled dump and record its receipt.
2. Submit the 2 jobs.
3. Run the existing read.
4. When both jobs are terminal: check sacct and the task logs, run `ki98_read.py analyze`, then commit the
   receipts, `LEDGER.tsv` and `REPORT.md` here and open a PR. The PR is not merged by this session.

## Not tested

- The mechanism inside either branch.
- Other tilt amplitudes, the q3 grid point, and nuisance settings away from nominal.
- Any coverage claim. Five seeds per arm measure a mean shift and nothing else.

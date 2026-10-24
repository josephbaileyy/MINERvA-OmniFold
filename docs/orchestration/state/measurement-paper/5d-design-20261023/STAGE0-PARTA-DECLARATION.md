# DECLARATION: 5D design Stage 0, Part A (0a, 0b) and Stage 0c (2026-10-23)

**By** the measurement session, at the director's request. The design is [`DESIGN.md`](DESIGN.md) §2.3 and §8. Part P
is done ([`STAGE0-PRESERVE-REPORT.md`](STAGE0-PRESERVE-REPORT.md)). Nothing here runs before the director's BINDING.
An independent read-only review of this declaration and its code found 3 MATERIAL and 12 MINOR issues; all are
addressed below (§9).

**CITABLE FOR:** the declared code, inputs, order, rules and compute cap of Stages 0a, 0b and 0c.
**NOT CITABLE FOR:** any result; any stage after 0c; any claim.

## 1. Fixed before any output

From `DECISION-20261023-joseph-5d-targets-and-paper-round-2.md`:
- **W.** W = 10%, so the model-term bar is **8.6%** (item 2).
- **Reporting definition.** **RD1** (109 J cells) if it passes Stage 0; otherwise **RD2** (H2, 27 cells); otherwise
  STOP (item 1).
- **Form.** **M2**: C_model = κ² Σ_k s_k s_kᵀ (item 8). M1 and κ_0.95 are computed and reported, not graded.
- **T2 and T4.** T2 is a validated-coverage requirement, with the recovery clause descriptive only (item 3). T4's
  "total" means statistical + model (item 4). Stage 0 grades neither directly.
- **GPU.** Stages 0 and 0c use no GPU (item 6).

## 2. Code (committed in this PR; sha256 of the files as committed)

| file | sha256 | role |
|---|---|---|
| `stage0/stage0_analysis.py` | `b25ff23560a80f1f665d3f728c7400602ea8075e8b6652ad581a80a8f766323d` | 0a and 0b, plus the 0c controls; read-only; login node; numpy only |
| `stage0/stage0c_ratio.py` | `9bd66d2b93018e36d6e03bd63a2f3bf11ca628fe0d8996df3527b780db7a4e57` | 0c ratio rebuild, with its control |
| `stage0/tasks-0c.tsv` | `09b08c13bd8edf332aa4e191db27eb56448066767011ddc094ba88f214438b46` | 0c unfolds, 8 lines |
| `state/gpu-timing-20261023/tools/sbatch_timing_packed.sh` (unchanged) | `b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3` | the 8 lines, concurrently, on one CPU node |

**What the analysis imports.**
- `stage0_analysis.py` imports `nd-unfolding/s5p_stage2_analyze.py`, sha256 `662d577a…`. That equals the hash recorded
  in `state/s5p/stage3/envelope-receipt.json`, which also records `s5p_envelope.py` at `12dd854f…`.
- `s5p_stage2_analyze.py` in turn imports `s5p_stage1_inspect.py`, sha256 `26569afc…`, equal to the hash recorded in
  `state/s5p/stage2/stage2_receipt.json`.
- Both match at main `ff1f8595`.

**The 0c unfolds run through a fresh clean clone at commit `978867700141440c9d85faadf1dd0ac3678dfc4d`.**
- Its `s5p_universe.py` blob, sha256 `30d9d910…`, is the one the study-P product `prior_R5fix_prior_d1.npz` records
  (job 58916065). It was live from `97886770` until `3e5f0c23` (2026-09-27).
- Choosing this commit is **(inference, tested by the line-0 bitwise control)**.
- The modules both old products record have the same sha256 at this commit, checked 2026-10-23:
  - `s5n_pseudo.py`, `s5c_pseudo.py`, `s5c_unfold.py`, `omnifold_nn_core.py`;
  - `xsec_nd.py`, `s5e_candidate.py`, `s5e_deform.py`;
  - `2d-unfolding/unfold_2d_omnifold_unbinned.py`.
- Imported modules the products do not record (`s5p_truths.py`, `s5p_numerics.py`, `s5e_trace.py`) are covered only by
  the bitwise controls.

## 3. Inputs

**The 425 files of `stage0/INVENTORY.sha256`**, with a copy on HPSS from Part P. `stage0_analysis.py` re-hashes every
inventoried file it reads and STOPS on any mismatch.

**Plus, for 0c only:** the vertical bank's
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz` (sha256 `072643e1e86ed0f3…`,
2,163,648,810 B).

**The 0c ratio. The primary choice follows DESIGN §8:** re-derive D1 from the repaired GENIE prediction, since GiBUU
itself "was not rebuilt" (`state/s5p/gen5d/README-gen5d-fluxfix.md:139`).

| role | file (under `/pscratch/sd/j/josephrb/s5p-20260926/`) | sha256 |
|---|---|---|
| numerator, primary and control (GiBUU, not rebuilt) | `gen5d/gibuu_cv_xsec5d.npz` | `b183fccaf620b798…` |
| denominator, control (unrepaired GENIE CV) | `gen5d/genie_cv_xsec5d.npz` | `8ff4e5e6824f3ba7…` |
| denominator, primary (repaired GENIE CV, with the 50–100 GeV supplement) | `gen5d_fluxfix/genie_cv_xsec5d_full.npz` | `cfa42210dfe9cadc…` |
| sensitivity A: numerator | `gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz` | `48917692ee129590…` |
| sensitivity B: denominator (repaired, < 50 GeV) | `gen5d_fluxfix/genie_cv_xsec5d.npz` | in the inventory |

- **Why the denominator includes the supplement.** The review's remedy was "PPFX flux and no 50 GeV cap" (`REVIEW-20260927-s5p-round1-stage2-exit-and-joint-design.md:119`).
  Sensitivities A and B are written and reported, not used.
- **The GiBUU deficit (`KNOWN_ISSUES` row 82).** GiBUU is empty above E_ν ≈ 20 GeV, which is about 5.2% of σ_CC
  (`state/s5p/gen5d/README-gen5d-fluxfix.md:146-148`). That deficit is in D1 and in the GiBUU truth, old and new alike, and the report states
  it.
- **Label and sample flag, recorded before any output.**
  - The committed s5n ratio's denominator is the Stage-A `genie_cv_xsec3d.root`, labelled "GENIE v2
    (DefaultPlusValenciaMEC, untuned)".
  - gen5d's `genie_cv` is a different GENIE sample (the `work_seed` sample, `state/s5p/gen5d/README-gen5d-build.md`),
    labelled "GENIE 2.12.10 CV (no MEC)".
  - So the ratio control tests that the two constructions agree in E_avail shape, not that they are identical.

## 4. Order of work and commands

**Definitions.**
- `B=/pscratch/sd/j/josephrb/5d-stage0-20261023`.
- `R=$B/repo`, a clean clone of this PR's merge commit.
- `S=$R/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0`.
- `PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"`.
- `G=/pscratch/sd/j/josephrb/s5p-20260926`.
- `IN="--repo $R --inventory $S/INVENTORY.sha256 --prior-dir $G/runs/s2/prior --assess-dir /pscratch/sd/j/josephrb/s5e-20260925/runs/cand/assess --data-dir $G/runs/s2/num/data --zcv /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz"`.

**Steps.**
1. **Provisional 0a and 0b** (login node; decides nothing). Two families, NuWro and GENIE MEC, with D1 excluded:
   `$PY $S/stage0_analysis.py $IN --mode provisional --out $B/stage0-provisional.json`.
2. **0c ratio** (login node). The primary run, then the two sensitivities:
   ```bash
   C="--s5n-ratio $R/docs/orchestration/state/s5n/eavail-ratio-gibuu-over-genie.json --old-num $G/gen5d/gibuu_cv_xsec5d.npz --old-den $G/gen5d/genie_cv_xsec5d.npz"
   $PY $S/stage0c_ratio.py $C --new-num $G/gen5d/gibuu_cv_xsec5d.npz --new-den $G/gen5d_fluxfix/genie_cv_xsec5d_full.npz --out $B/ratio/eavail-ratio-gibuu-over-genie-fluxfix.json
   $PY $S/stage0c_ratio.py $C --new-num $G/gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz --new-den $G/gen5d_fluxfix/genie_cv_xsec5d_full.npz --out $B/ratio/sensitivity-A.json
   $PY $S/stage0c_ratio.py $C --new-num $G/gen5d/gibuu_cv_xsec5d.npz --new-den $G/gen5d_fluxfix/genie_cv_xsec5d.npz --out $B/ratio/sensitivity-B.json
   ```
   **Control:** max |r / r_s5n − 1| ≤ 0.02 per bin, and every E_avail bin positive. Otherwise STOP; 0c and the binding
   run do not happen.
3. **0c unfolds** (one CPU node, regular QOS, never premium):
   ```bash
   sbatch -A m3246 -q regular -C cpu -t 01:00:00 -J s0c -o $B/logs/%x_%j.out \
     $R/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh \
     $B/deploy/97886770 978867700141440c9d85faadf1dd0ac3678dfc4d $S/tasks-0c.tsv $B/runs 32 56G 0 7 inherit
   ```
   It runs eight tasks concurrently, 8 × 32 CPUs and 8 × 56 GB, within the node's 487,802 MB:
   - line 0: the committed-ratio D1 data unfold (control). In `prior_a`, d1 ran after d0 in the same process; here it
     runs alone, so the bitwise control also tests order independence;
   - line 1: the new-ratio D1 data unfold;
   - line 2: the committed-ratio GiBUU pseudo-experiment 801000 (control);
   - lines 3–7: the new-ratio GiBUU ensemble, seeds 801000–801019 (inclusive ranges), 4 per line.
4. **Binding 0a and 0b** (login node). Three families, adding GiBUU = {d1new; GiBUU_new}. The 0c bitwise controls are
   checked inside the run (C0c):
   ```bash
   $PY $S/stage0_analysis.py $IN --mode binding --d1-new $B/runs/new_prior/prior_R5flux_prior_d1.npz \
     --gibuu-new-dir $B/runs/new_gibuu --ratio-new $B/ratio/eavail-ratio-gibuu-over-genie-fluxfix.json \
     --ctl-prior $B/runs/ctl_prior/prior_R5fix_prior_d1.npz --ctl-gibuu $B/runs/ctl_gibuu/eavail_shape_a1_s801000.npz \
     --out $B/stage0-binding.json
   ```
5. **Report.** `STAGE0-REPORT.md`, with:
   - both JSONs, the three ratios with their controls, and the ledger;
   - durable copies of the 0c products, put on HPSS beside Part P's tar, with hashverify.

## 5. What the analysis computes, and its controls

**Quantities.**
- **Shifts:** s_k = J_k / J_CV − 1 on the reporting cells, as in `s5p_envelope.shifts`.
- **Bias:** b = the mean over the R ensemble of (f̂ / f_true − 1), from `s5p_stage2_analyze.ensemble`.
- **Departure:** mean truth / mean nominal truth − 1, with s5e's 40 nominal assessment products as nominal.
- **Population:** the reported cells with |departure| > 1%.
- **Graded sets:** J and H2. EW is computed and reported, never graded, and never stops the run.

**Families.**
- NuWro: vertices {d2, d4, d5}; folds W1, W3 and q3.
- GENIE MEC: {d3}; fold W2.
- GiBUU, binding only: {d1new}; fold GiBUU_new.

**Controls.** Each one STOPS, and the JSON names the failure:
- **C1:** every inventoried input matches its sha256.
- **C2:** the CV path equals the N1 base `data_b-_j-.npz` bitwise. The nominal-prior control d0 equals the CV path to
  < 1e-5 relative on every reported cell. That is how the record states it: "equal on every reported functional to
  < 1e-5 relative, not bitwise" (`RECORD-20260927-s5p-stage2-exit.md:106-107`; `stage2_receipt.json` `study_P.controls`).
- **C3:** the committed envelope receipt's h medians are reproduced, with and without D1, on J, H2 and EW. The
  tolerance is relative 1e-9, because it is the same code path.
- **C4:** z-cv's `hRowIndex5D` equals the indices of its `hSupportMask`. Every reported J, H2 and EW cell receives at
  least one z-cv row. The covariance is 10,694². The J median of (a)'s central over (e)'s data base lies in
  [0.8, 1.25]. The projection identity is also recorded.
- **C5:** every graded covariance is positive definite.
- **C0c (binding):** line 0's `xsec_flat` equals `prior_R5fix_prior_d1.npz`'s bitwise. Line 2's `xsec_flat` and
  `xtrue_flat` equal s5e's `assess/eavail_gibuu/eavail_shape_a1_s801000.npz` bitwise.
- **C6 (binding):** all 20 seeds 801000–801019 exist, by exact name. Each product's `eavail_ratio_sha256` equals the new
  ratio's, and its `code_sha256` equals the old GiBUU product's. The new D1 product is prior d1, and carries the new
  ratio's sha if it records one.

## 6. Rules (DESIGN §8, with item 1's reporting rule)

| stage | PASS (anything else STOPS) |
|---|---|
| **0a**, J and H2 separately, on M2 | c_F ≥ 0.60 at every held-out family, **and** coverage pooled over the held-out families ≥ 0.68. κ^(−F) is the smallest κ covering ⌈68 n / 100⌉ of the other families' n pairs, computed in integer arithmetic |
| **0b**, J and H2 separately | κ* is the same quantile over all folds with all vertices. **The median over the reported cells of u*_f = κ*·(Σ_k s_k,f²)^½ must be ≤ 8.6%**, **and** the noise-corrected expected shape-only Δχ² must be ≥ 9 for ≥ 2 of the available stage-1 pairs |
| **Stage 0 verdict** (binding run only) | **RD1** if J passes 0a and 0b; otherwise **RD2** if H2 passes; otherwise **STOP**. The provisional verdict is labelled "decides nothing" |
| **0c** | the ratio control, C0c and C6 pass; otherwise STOP before the binding run's grades |

**0b's graded covariance is DESIGN §8 literally:** C_stat(e) + C_model + the (a) z-cv term.
- C_stat(e) comes from the 50 R data bootstrap replicas, `data_b{1..50}_j{101..150}.npz`.
- z-cv keeps only its total, `hCov_combined5d_total_uthrow`, which already contains (a)'s statistical block
  (`docs/analysis-note/sec_5d.tex:584-596`). So statistics count twice in the graded covariance. That is the
  conservative direction for a Δχ² gate.
- The z-cv-only variant is reported, not graded.

**The Δχ² ingredients:**
- **Pairs:** W2 (own vertex d3), W3 (d4), W1 (d2) and, in the binding run, GiBUU_new (d1new). For each pair, C_model
  drops only that pair's own vertex.
- **q3 is not a pair.** The stage-1 use-case pairs are the four fixed-generator differences (`amendment-1:10`), and q3
  is an a = 0.3 tilt **(inference)**.
- **d:** the R-unfolded ensemble mean over the nominal mean, minus 1.
- **Noise correction:** the finite-ensemble term tr(C⁻¹ C_noise) is subtracted. To first order, C_noise =
  Var(mean_g)/μ_n² + (μ_g/μ_n²)² Var(mean_n), with each sample covariance divided by its ensemble size.
- **Shape-only:** a free normalization mode of variance 100 (relative units) is added. The total (rate + shape) Δχ² is
  also reported.

## 7. Compute, ledger, storage

- **Steps 1, 2 and 4:** 0 node-h, on a login node. The largest object is z-cv, about 0.9 GB in memory.
- **Step 3:** one regular CPU job, capped at **1.0 CPU node-h** by its 1 h limit.
  - Expected: about 0.65. The longest line runs 4 pseudo-experiments of about 533 s each at today's C0 speed
    (`state/gpu-timing-20261023/REPORT.md`) **(arithmetic)**.
  - This is within the phase-1 grant, as the director stated.
  - The job is ledgered in `stage0/LEDGER.tsv` from `sacct`. It is stopped and reported if it runs beyond 1.25× its
    projected wall time.
- **Storage:** pscratch only during the run: products, ratios and JSONs, together under 20 MB. Durable copies go to
  HPSS afterwards. Nothing goes to CFS.

## 8. Unchanged

- No GPU is used.
- No stage after 0c is declared.
- MP-2 stays held, and no claim changes.
- R10 remains the validation lane's. Stages 2–4 wait for both Stage 0 and R10 (item 6).

## 9. Review dispositions (independent read-only review, 2026-10-23)

**MATERIAL:**
- (1) C2 now reflects the recorded d0 result.
- (2) The κ rank now uses integer arithmetic; it is unit-tested at n = 5, 75, 109, 150, 175 and 300.
- (3) The graded covariance is now DESIGN's literal, conservative sum.

**MINOR:**
- C4 was replaced by indexing checks that can fail.
- Binding inputs are validated (C6), and the 0c controls run in code (C0c).
- The numerator choice and the KI 82 deficit are stated (§3), and the ratio control's scope and tolerance are stated.
- EW and κ_0.95 are reported, and q3's exclusion from the pairs is explained.
- The noise term has the missing factor.
- The receipt citation is fixed, and inferences are labelled.
- The task table's header and the job script's path are fixed.
- Line 0 tests order dependence.
- The Part P report's unreceipted items and the hard-link caveat are stated in its addendum.

# DECLARATION 3D: the flux-correlation bootstrap over the 100 universes (2026-10-27)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's decision `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` (PR #423, main
  `289f4457`), item 3: "3D runs: a bootstrap of the flux correlations over the 100 universes … declared, then bound, on
  a login node at 0 node-h". Joseph's selected option was "Yes, run 3D (Recommended)".
- The director's request of 2026-10-27: define the statistic and its band here, with no p values, and say how n_eff 19
  enters the band.

**After:**
- [`LIMITATION-PLAN.md`](LIMITATION-PLAN.md) §3.2, option 3D (PR #421).
- G-SENS2 ([`FD-G-SENS2-REPORT.md`](FD-G-SENS2-REPORT.md)), which shrank the flux correlations by an arbitrary α. Its
  results stand.
- 3D measures something else: the **estimation uncertainty** of the χ² when those correlations are estimated from the
  100 weighted universes.

**Declares:**
- a new tool, `nd-unfolding/fd_flux_boot.py`, and its tests;
- the replicate scheme, the statistic and the two bands;
- the exact argv, the controls, the readout schema and the stop rule.

**MEASURES:** nothing. The tool has run only on synthetic fixtures.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit and has run only on synthetic fixtures -->

**CANNOT AUTHORIZE:**
- running it, which needs the director's binding first;
- any reading, claim or printed wording, including the new form of the paper's sensitivity sentence. That goes
  through the PRD read and the truth column, then to Joseph (decision item 3);
- any change to a covariance, cell or readout.

**CITABLE FOR:** what 3D will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:**
- any result;
- once it has run:
  - that the χ² is insensitive to the flux correlations;
  - that the PPFX or constraint correlations are correct;
  - an interval for the χ² under the true flux correlations.

## 0. Summary

### The question

Stage G's χ² depends on how strongly the flux block correlates the cells. In the block alone, R04–R08 correlate at
+0.983 (`FD-G-FOLLOWUP-REPORT.md:180-198`).
- G-SENS2 weakened those correlations by a chosen α.
- 3D asks how much the χ² moves when the correlations are re-estimated from the same 100 universes. The weighted
  ensemble holds only about 19 universes' worth of information (n_eff = 19.06, `S1-REPORT.md:288`).

### What the band is, and is not

**It is the estimation uncertainty** of the χ² from estimating the flux correlations with about 19 effective
universes. It is conditional on PPFX's model and on the chosen ν-e + IMD constraint.

**It is not a sensitivity.**
- A narrow band means the 100 universes pin the correlations well. It does **not** mean the χ² is insensitive to them.
  G-SENS2's α results stand.
- Systematic choices lie outside the band. One example is FHC-only against FHC+RHC+IMD, which is the leading inference
  for the 2D flux block (`2d-closeout/c04-repair/REPORT.md:284-287`).

### The replicate

S1 builds the flux block from the 100 PPFX Flux universes as MAT's weighted `CalcCovMx`, with the ν-e + IMD constraint
weights w (`s1_assemble.py`: `mat_cov`, `flux_weights`; `S1-DECLARATION.md` row 10).

Replicate b draws 100 universe indices uniformly with replacement. Each drawn universe carries its own weight. The
block is rebuilt with exactly S1's rule, C*_b = mat_cov(X[i_b], w[i_b]), where X is the universes' 16-cell integrals
(U · xsec_flat, S1's and Stage G's integration rule).

### The two variants

Each variant replaces the flux group, and only it, in Stage G's reported matrix C_total + C_resp + V_g.
- **`correlation` (primary):** S1's flux variances, bit for bit, with the replicate's correlations: D₀^½ ρ*_b D₀^½.
  These are the quantities G-SENS varied, since G-SENS keeps the variances.
- **`block` (second):** C*_b itself, variances included.
  - This adds the variance scatter c04-repair put at "a rough ±16% relative sampling scatter on σ"
    (`2d-closeout/c04-repair/REPORT.md:288-289`).
  - Under resampling, its variances are biased low by about (1 − 1/n_eff). The review measured 0.969 of S1's, and this
    pushes its χ² high.

### The statistic and its bands

For each prediction and variant, the statistic is the distribution, over B = 2000 replicates, of:
- the total χ² on the prediction's own cells (GiBUU on its eight);
- the shape-only χ², Stage G's free normalization 100·11ᵀ relative to f.

Everything is relative to f, as in G-SENS. Each distribution gets:
- **the percentile band q:** the 2.5, 16, 50, 84 and 97.5 percentiles (numpy `linear`), with the minimum and maximum.
  The same percentiles from replicates 1–1000 and 1001–2000 show the Monte Carlo scatter;
- **the centre χ̂:** Stage G's own χ², which is the identity replicate, printed beside each band;
- **the offset,** median − χ̂, labelled as the bootstrap's estimate of χ̂'s bias (§4.3);
- **the basic (reflected) band,** 2χ̂ − q at the mirrored percentile. For example, key 16 holds 2χ̂ − q₈₄. It is a
  declared companion.

**Neither band is an interval for the χ² under the true correlations** (§4.3). Which one a paper sentence would use is
the director's call (§7).

The R04–R08 correlation gets a percentile band in the flux block alone, and in C_total + C_resp with each variant. Its
values with S1's own block are given beside them.

**No p-value and no tail fraction.** The readout has no key `p`, and a test asserts this.

### How n_eff enters (§4.2)

n_eff enters exactly through the term the bootstrap carries. Under this resampling, a weighted mean's variance is
Σwᵢ²(xᵢ − μ)²/(Σw)².
- That term equals σ_w²/n_eff only when the residuals do not follow the weights. The ν-e + IMD weights are a
  likelihood of each universe's own flux, so they may follow them.
- The readout records the realized per-cell ratio `sd_over_sigma_w_root_n_eff`: the bootstrap sd of the weighted mean
  universe integral, over σ_w/√n_eff with σ_w² = Σw(x − μ)²/Σw. The review saw 0.70, 0.75 and 0.93 on synthetic
  columns with independent weights (`review/sim_neff.log`).
- **`delta_method_ratio`** is the same sd over √(Σw²(x − μ)²)/Σw. It is about 1 for any weights, because both sides
  are conditional on the same sample. So it only checks that the bootstrap carries that term, and is not evidence
  about n_eff.

### The named alternative

`uniform` is the block from the 100 universes with equal weights: the flux prior without the constraint, n_eff = 100.
- It gives one χ² per prediction, and its R04–R08 correlation.
- Its label says it is a named alternative, not an alternative result.
- A uniform matrix that is not positive definite refuses at B4.

**Cost:** 0 node-h, on a login node. No Slurm job, and nothing written to CFS.

**Stop rule:** any refusal, any non-zero exit, or a run past 1.25× its projected wall is reported unrepaired.

## 1. Inputs

**Stage G's inputs, with their pins unchanged,** as G-SENS2 used them (`FD-G-SENS2-DECLARATION.md` §1) and G-DIAG's
D0–D5 check them:

| input | where | pin |
|---|---|---|
| S1 assembly | `$P/s1-20261024/s1_assembly.npz` | `db000707…` (`D.PINS["s1_npz"]`) |
| S1 readout | `$T/s1/readout/s1_assembly.json` | `81e5ef3f…` |
| C_model,5D | `$D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json` | `3cfdc6a5…` |
| s5p archive sums | `$D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt` | `1a72cb43…` |
| the five predictions | `$P/s5p-20260926/gen5d_fluxfix/…`, `gen5d/mnvtune_v1_xsec5d.npz` | `fd_g_compare.PREDICTIONS` |
| Stage G readout | `$T/fd/readout/fd_g_readout.json` | `75a9ddee…` |
| C_resp, adopted | `$P/cresp-20261026/out/cresp.npz`, key `C_resp` | `4d8b5797…` (argv) |

**New inputs:**

| input | where | checked against |
|---|---|---|
| the 100 Flux universe products | `$T/s1/readout/s1_assembly/S1_Flux_0.npz` … `S1_Flux_99.npz`, committed (PR #348) | each file's sha256 against the S1 readout's `meta.inputs_sha256`, whose own digest is pinned (B0); S1 records exactly 100; each meta reads `s5p-universe/1`, `Flux:<u>` |
| the constraint file | `$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2`, which is both the tool's pin (`s1_assemble.CONSTRAINT_SHA256`) and the S1 readout's `meta.inputs_sha256.constraint`. Σw and n_eff must equal the readout's `meta.flux_weights` (B0) |

**Re-measured on login25 at 2026-10-27T19:24Z:**
- the constraint file `e38ad7d2…`, `cresp.npz` `4d8b5797…` and `s1_assembly.npz` `db000707…` match their pins;
- the cluster's root_6_28 numpy, 1.26.4, gives the declared index-matrix digest `23e2e374…`;
- `$P/fd-flux-boot-20261027` does not exist.
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-flux-boot-20261027` on login25 at 2026-10-27T19:24:02Z printed 'No such file or directory' -->

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`;
- `B=$P/fd-flux-boot-20261027`;
- `D=$B/deploy/<pin8>`, a clean clone of the binding commit;
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`;
- `PY=env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_flux_boot.py nd-unfolding/tests/test_fd_flux_boot.py nd-unfolding/fd_g_followup.py \
    nd-unfolding/fd_g_diag.py nd-unfolding/fd_g_compare.py nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py \
    nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-FLUX-BOOT-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_flux_boot test_fd_g_followup test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated \
  > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after;
- the §8 digests;
- `tests rc=0` with "Ran 203 tests … OK": 29 for 3D, plus 174 as G-SENS2 declared them, run locally on 2026-10-27.

The 3D tests' `CommittedPins` re-check the 100 committed universes' digests, and the index-matrix digest under the
cluster's numpy.

Anything else is a STOP.

### 2.2 The run (login node, after §2.1)

```bash
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_flux_boot.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --g-readout $T/fd/readout/fd_g_readout.json \
  --extra-block $P/cresp-20261026/out/cresp.npz \
  --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
  --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted \
  --flux-dir $T/s1/readout/s1_assembly \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --out-json $B/fd_flux_boot_readout.json > $B/logs/boot.out 2> $B/logs/boot.err; echo "rc=$?" >> $B/logs/boot.out
```

**Projected wall: 5 minutes.**
- G-SENS2's load took about 1 s.
- The 100 universe reads and 2000 × 2 × 5 pairs of 16 × 16 Cholesky solves take seconds, as they do on the synthetic
  tree in the end-to-end test.
- The timeout is 375 s, 1.25 × the projection.

**Exit codes:**
- 0: every control passed and the readout was written;
- 1: a control refused, an overwrite was refused, or an unexpected error occurred, and nothing was written;
- 2: argparse;
- 124: past the timeout.

Any exit other than 0 is a STOP.

**What is committed** (the report's PR):
- `$B/fd_flux_boot_readout.json`, as `fd/readout/fd_flux_boot_readout.json`;
- the logs and step scripts, under `fd/receipts-flux-boot/run/`;
- a ledger row.

**The results index:** if the readout enters the index population, it is regenerated in-branch under the director's
standing ruling (a).

## 3. Controls

All of these run before anything is written. Each one refuses: exit 1, with nothing written.

**D0–D5.** G-DIAG's controls, unchanged, through `fd_g_diag.load`. They pin and check Stage G's inputs, and reproduce
Stage G.
- Tested by G-DIAG's tests and by `test_the_real_script_reaches_d0_and_refuses_synthetic_records`.

**B0: the inputs.**
- The constraint file's digest is the tool's pin, and is the one S1's readout recorded.
- S1's parser (`flux_weights`) accepts it, and its Σw and n_eff equal S1's recorded values to 10⁻¹².
- The 100 universe files exist, in order 0–99, and each one's sha256 is the one S1 recorded.
- S1 records exactly 100 of them, and each meta is `s5p-universe/1`, `Flux:<u>`.
- **Tests:**
  - `test_b0_a_universe_whose_digest_is_not_s1s`
  - `test_b0_a_universe_named_for_another`
  - `test_b0_a_missing_universe`
  - `test_b0_s1_records_another_number_of_universes`
  - `test_b0_s1_records_a_101st_universe` (the count clause alone, with every digest right)
  - `test_b0_the_constraint_file_is_not_the_pin_or_s1s` (the pin, and S1's record)
  - `test_b0_the_weights_are_not_s1s` (n_eff × (1 + 10⁻⁹))
  - `test_b0_too_few_flux_weights`

**B1: S1's block, rebuilt.** The flux group is `band:Flux` alone. The block rebuilt from the 100 universes with their
weights (the identity replicate) equals S1's to 10⁻¹² relative.
- **Test:** `test_b1_the_block_rebuilt_without_the_weights`.

**B2: Stage G, reproduced.** Swapped in, the rebuilt block reproduces Stage G's total and shape-only χ² for every
prediction, to 10⁻¹⁰ relative.
- **Test:** `test_b2_a_shape_only_chi2_that_is_not_stage_gs`.

**B3: the replicates.** The 2000 × 100 index matrix from `default_rng(20261027)` hashes, as `<i4`, to the declared
`INDEX_SHA256`.
- **Tests:** `test_b3_another_index_matrix`; `test_the_seed_gives_the_declared_index_matrix`.

**B4: every replicate is usable.** Every replicate's flux variances are positive. Every swapped matrix is positive
definite (Cholesky), the uniform alternative's included.
- **Tests:**
  - `test_b4_a_replicate_with_a_non_positive_variance`
  - `test_b4_an_indefinite_swapped_matrix` (positive diagonal, correlations above 1)
  - `test_b4_an_indefinite_uniform_matrix_refuses`

**B5: the correlation variant keeps S1's flux variances,** bit for bit, in every replicate.
- **Test:** `test_b5_a_swap_that_moves_a_variance_by_one_ulp`.

**The pure functions,** tested beside the controls:
- the identity replicate is S1's rule, and agrees with an independent weighted covariance;
- a replicate carries each drawn universe's weight;
- the swap keeps the variances, takes the correlations, and is exactly symmetric;
- χ² and shape-only χ² by inverse, and None when the matrix is not positive definite;
- the band's percentiles, halves, basic band and offset;
- the spread of the weighted mean (§4.2).

**End to end, as invoked** (`-I -B`, with the cwd outside nd-unfolding), each value is recomputed by an independent
loop (`by_hand`: an `einsum` weighted covariance and inverse quadratic forms), to 10⁻⁹ relative:
- every band's percentiles, minimum, maximum, second-half median, basic band and offset;
- the R04–R08 band in the flux block, and in the reported matrix for each variant;
- `correlation_s1`;
- `sd_over_sigma_w_root_n_eff`;
- the uniform χ².

The same test also checks:
- the identity equals Stage G's committed χ²;
- GiBUU is graded on its eight cells;
- no key `p`, and the `not_citable_for` label.

## 4. Statistics, as built

### 4.1 The replicate scheme, and three not chosen

**Chosen: the nonparametric bootstrap over universes, each carrying its weight** (the review called it the pair
bootstrap).
- Its unit is the universe, which is PPFX's independent draw.
- The estimator is S1's, unchanged, applied to the resampled set.

**Not chosen:**
- **Resampling with probability ∝ w, then unweighted.** This draws 100 universes from the weighted ensemble and treats
  them as 100 independent draws from the target. Its spread corresponds to n = 100, not n_eff ≈ 19.
- **The Bayesian (Dirichlet) bootstrap,** with weights w·g and g ~ Dirichlet(1, …, 1). It agrees with the chosen scheme
  to first order and is smoother. It is less standard, and it adds nothing the band needs.
- **The jackknife,** the other option LIMITATION-PLAN named.
  - Leaving one universe out at a time gives a variance estimate, not a distribution, so there is no percentile band.
  - Its delete-1 form is unreliable for non-smooth functionals. The χ² of an inverted, near-degenerate matrix is one.
  - With n_eff ≈ 19, its leave-one-out replicates are dominated by the few heaviest universes.

### 4.2 How n_eff enters

For a weighted mean μ̂ = Σwᵢxᵢ/Σwᵢ, the scheme's variance is, to first order, Σwᵢ²(xᵢ − μ)²/(Σw)². The bootstrap
carries this term exactly. It equals σ_w²/n_eff only when the residuals do not follow the weights.

That condition is not given here. The ν-e + IMD weights are a likelihood of each universe's own flux, so universes with
a given flux shape are systematically up- or down-weighted. The realized ratio is therefore recorded per cell, not
assumed (`sd_over_sigma_w_root_n_eff`). The test `test_the_spread_follows_one_over_n_eff` shows, on synthetic
universes with weights independent of the values:
- `delta_method_ratio` within 12 % of 1, for both weight sets;
- the spread widening by √(100/19), within ±30 %, from equal weights to n_eff ≈ 19.

That widening holds only in expectation, and only when the residuals do not follow the weights.

**For correlations and χ², the scaling is first order only.** They are functions of weighted moments. The argument
above carries to them only to first order. It fails for inverse and eigenvalue functionals in a near-degenerate block
(§4.3).

### 4.3 What the bands are and are not

**Both bands measure estimation uncertainty.** They show the scatter of Stage G's χ² when the flux correlations are
re-estimated from these 100 universes, as PPFX and the constraint give them. They are not a sensitivity, and not a
confidence interval with guaranteed coverage.

**The centre can be biased, and the bootstrap shifts the same way.**
- The flux group is near-degenerate. Its correlations are 0.97–0.998, its λ_min is about 2 × 10⁻⁷ relative, and it has
  16 cells against n_eff ≈ 19.
- In the review's synthetic check, the χ² of the estimated matrix, χ̂, was biased high relative to the χ² under the
  matrix the ensemble estimates. The percentile bootstrap of χ²(C*) added a further shift in the same direction.
- On the real inputs, the direction and size are whatever the readout's offset shows. The offset is the bootstrap's
  estimate of χ̂'s bias.
- **The review's synthetic check,** which this declaration extends (`review/sim_coverage.py`,
  `review/sim_coverage_basic.py` and their logs), used a flux-like 16-cell block with spectrum 10⁻³–10⁻⁷, n_eff ≈ 19,
  S1's estimator, 3D's resampling and 150 ensembles. With weights independent of the universes:
  - χ²(C_true) is 100.65, and the median χ̂ is 103.58;
  - the median of (bootstrap median − χ̂) is +0.56 (correlation) and +1.24 (block);
  - the 16–84 % percentile band covers χ²(C_true) in **0.37** and **0.32** of ensembles, against a nominal 0.68;
  - the basic band covers it in **0.48** and **0.57**.
- **When the weights follow the universes' values,** as a constraint likelihood does, the weighted ensemble estimates
  the constrained covariance C_post = (C_true⁻¹ + s²q₀q₀ᵀ/λ₀)⁻¹, not the prior C_true. The right target is therefore
  χ²(C_post). The reviewer's rerun on the same seeds (`review/sim_followsx_target.py` and `.log`) found:
  - χ²(C_post) has median 115.47, and χ̂ has median 116.95 (+1.49);
  - **correlation:** median offset +0.43; the percentile band covers χ²(C_post) in **0.47** of ensembles, and the
    basic band in **0.57**;
  - **block:** median offset +1.11; the percentile band covers it in **0.45**, and the basic band in **0.61**.
- The follows-x arm of `review/sim_coverage.py` and `review/sim_coverage_basic.py` compared against χ²(C_true). Its
  0.00 is an artefact of that wrong target, and is superseded by the rerun.

**So the readout gives the offset beside each band.** Neither band is presented as an interval for the χ² under the
true correlations. In the toy, coverage of the nominal 0.68 is about 0.32–0.61, whether or not the weights follow the
values. The basic band removes the bootstrap's own extra shift to first order, but it cannot remove χ̂'s own bias.

### 4.4 Reused code

- S1's `mat_cov` and `flux_weights` (`s1_assemble.py`).
- G-DIAG's `load` (D0–D5) and `finite`.
- G-FOLLOWUP's `prediction_blocks`: the reported matrix's relative blocks, the residual and the cells.
- Stage G's `SHAPE_LAMBDA`.

## 5. The readout, `fd-flux-boot-readout/1`

```text
schema, labels{what, replicate, variants, uniform, n_eff, band, units, not, not_citable_for[3]},
controls_passed[D0..D5, B0..B5],
constants{replicates 2000, universes 100, seed 20261027, index_sha256, percentiles, percentile_method, variants,
          pair [R04, R08], reproduction, reported_matrix},
identity{prediction: {chi2_stage_g, shape_only_stage_g, chi2_rebuilt, shape_only_rebuilt, relative_difference}},
bands{correlation | block: {prediction: {cells, ndf, chi2_stage_g, shape_only_stage_g,
      total | shape_only: {percentiles{2.5, 16, 50, 84, 97.5}, min, max, halves[2], basic{2.5 .. 97.5},
                           offset_median_minus_centre}, label}}},
correlation_band{flux_block, reported_matrix_correlation, reported_matrix_block: {percentiles, min, max, halves}},
correlation_s1{flux_block, reported_matrix},
n_eff{s1, sum_w, sd_over_sigma_w_root_n_eff{R00..R15}, delta_method_ratio{R00..R15}},
uniform{n_eff 100, predictions{prediction: {chi2, shape_only}}, pair_correlation_flux_block, label},
inputs_sha256, code_sha256{fd_flux_boot.py, fd_g_followup.py, fd_g_diag.py, fd_g_compare.py, s1_assemble.py}, argv,
non_finite_written_as_null
```

**stdout prints:**
- the PASS lines;
- the label line;
- one `[3D]` line per variant and prediction: Stage G's χ², the 16–84 % and 2.5–97.5 % bands, the offset, the basic
  16–84 % band and the uniform χ²;
- one n_eff line, with the median and range of `sd_over_sigma_w_root_n_eff`;
- the `wrote` line.

## 6. Code and tests

### 6.1 `nd-unfolding/fd_flux_boot.py` (new)

**Pure functions:** `indices`, `index_digest`, `replicate_block`, `n_eff`, `correlation_swap`, `chi2s`,
`correlation`, `band` (with the basic band and offset when given a centre) and `mean_spread`.

**The rest:** the input checks `weights` and `universes` (B0), and `run`, which holds B1–B5, the bands and the readout.

**Constants:**
- `B_REPLICATES` 2000 and `SEED` 20261027;
- `INDEX_SHA256` `23e2e374…`;
- `PERCENTILES`, `VARIANTS` and `PAIR`.

They are constants, not arguments, so the argv cannot choose them.

### 6.2 `nd-unfolding/tests/test_fd_flux_boot.py` (new, 29 tests)

| class | tests |
|---|---|
| `Pure` | 7 |
| `EndToEnd` | 3 |
| `Controls` | 15 |
| `Invocation` | 2 |
| `CommittedPins` | 2 |

**The fixture, `BootTree`,** is G-DIAG's synthetic tree plus:
- 100 synthetic universes, built from a common scale, a tilt and noise, with lognormal weights solved to n_eff ≈ 19,
  written as `S1_Flux_<u>.npz`;
- a constraint file with distractor lines;
- S1's readout meta recording both.

### 6.3 Mutation receipt

`fd/receipts-flux-boot/declaration/mutants.py` runs 30 one-line mutants: the first round's 20, plus 10 from the review
and the code it added.
- Each mutant is applied to the tool in place, and the four non-pin test classes run against it.
- The tool is then restored, and its sha256 checked after every mutant and at the end.
- The log is `mutants.log`, and §11 gives the outcome.

## 7. For the director

1. **The primary variant is `correlation`,** so that the band concerns the correlations alone. `block` is the second
   record. Its variances are biased low by about (1 − 1/n_eff), which pushes its χ² high.
2. **Which band a paper sentence would use is the director's call.** The options are:
   - the percentile band;
   - the basic band;
   - or neither, with only the spread and the offset.

   Neither band is an interval for the χ² under the true correlations (§4.3), and the sentence must say what the band
   is: estimation uncertainty given these universes.
3. **B = 2000 and the seed 20261027.** For a normal distribution, the Monte Carlo error on a 16th or 84th percentile is
   about 2 % of the 16–84 % width: √(0.16 × 0.84/2000)/φ(1) ≈ 0.034σ, against a width of 2σ. The halves show it.
4. **No p-value or tail fraction,** against α = 0.1 or anything else.
5. **`uniform` is a single named alternative, not bootstrapped.** It changes the variances as well as the
   correlations.
6. **The pair is G-FOLLOWUP's R04–R08.** Other pairs can be added before binding.
7. **`sd_over_sigma_w_root_n_eff` and `delta_method_ratio` are descriptive, not controls.**

## 8. Pinned bytes

At this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_flux_boot.py` | `48c6eb04a212155bde8d6ce03db6d0f3a859b158fdf2f9c28822edd9e224a209` |
| `nd-unfolding/tests/test_fd_flux_boot.py` | `84d724ce64bd9e40f9105408e0d3ff0af7ed00bc2d1f44b4b53c68e4d5ffc219` |
| `nd-unfolding/fd_g_followup.py` | `ec8cbc6880f7a3f67eea5703ddeff958acb10462053696d2cfdb64de0ee5f60d` |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json` | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` |

Only the first two files are new. The other six are unchanged from `main`.

## 9. Ledger, storage and stops

**Ledger:** in `fd/LEDGER.tsv`, one row for the deploy and tests and one for the run. Both are 0 node-h, on a login
node, with no Slurm job.

**Storage:**
- `$B` on pscratch joins the retention list. Nothing goes to CFS.
- The readout is committed.
- The inputs are already preserved, so no HPSS copy is needed. S1's universes are committed, and S1, C_resp and the
  predictions are kept as for G-SENS2.

**Stops:** §0's stop rule applies. No step is rerun or repaired without the director.

## 10. Not changed

- Every covariance, cell, readout and κ.
- `docs/analysis-note/**`, including the paper's sensitivity sentence. Its new form belongs to the paper lane, through
  the PRD read and the truth column, then to Joseph.
- The fake-data limitation, which stays as stated (decision item 2).

## 11. Review dispositions

**First mutation receipt** (2026-10-27T19:23–19:30Z, the first round's 20 mutants, on `bed614c1…`): 19 of 20 killed.
The survivor was ddof 0 in the descriptive ratio. That log is replaced by the second receipt below; it is in this
branch's history at `d8945840`.

**Independent read-only review of `d8945840`.** It found no arithmetic defect:
- the rebuild is exactly S1's;
- the pair bootstrap is the right scheme;
- the correlation variant is positive semidefinite;
- there are no p values, and the pins match.

Its scripts and logs are committed under `fd/receipts-flux-boot/declaration/review/`.

**H1. The band measures estimation noise, not sensitivity.** Done.
- The tool's docstring and its `band` label now say "estimation uncertainty, not sensitivity". So do the `what`
  framing and §0's "What the band is, and is not".
- A narrow band means the correlations are well pinned, not that the χ² is insensitive to them. G-SENS2's α results
  stand.
- Systematic choices, such as FHC-only against FHC+RHC+IMD, are outside the band.
- The three NOT CITABLE FOR items are in the header and in the readout's `labels.not_citable_for`, which a test asserts.

**H2. The band's centre is biased.** Done.
- §4.3 states the bias and the review's synthetic numbers, and the tool records the offset, median − χ̂, with its
  label.
- The basic (reflected) band is a declared companion. Its coverage was measured by extending the reviewer's script:
  0.48 and 0.57, against the percentile band's 0.37 and 0.32, with independent weights. (That script's follows-x arm
  used the wrong target; see the focused re-review below.)
- Which band a sentence would use is §7 item 2.
- §4.2's claim that the scaling carries to the band is now stated as first order only, and as failing for inverse and
  eigenvalue functionals.

**M1. Neither n_eff diagnostic showed n_eff entering.** Done.
- `n_eff_replicate` is dropped: it counts duplicates as independent, so it is close to n_eff by construction.
- `delta_method_ratio` is kept, relabelled as a check that the bootstrap carries Σw²(x − μ)²/(Σw)², not as evidence
  about n_eff.
- The new `sd_over_sigma_w_root_n_eff` records the realized per-cell ratio.
- "The readout shows this directly" is gone. The widening is stated to hold only in expectation, and only when the
  residuals do not follow the weights, which the ν-e + IMD likelihood weights may not satisfy.

**M2. The block variant's variances are biased low** by about (1 − 1/n_eff), which pushes its χ² high. Done: this is
stated in §0, in the docstring, in the `variants` label and in §7 item 1.

**M3. Four surviving mutants.** All four are now covered:
- **the count clause:** `test_b0_s1_records_a_101st_universe` plants a 101st key with every digest right;
- **the reported-matrix correlation band using C0:** the end-to-end test now recomputes both variants' bands;
- **`correlation_s1.reported_matrix` without the flux block:** recomputed in the end-to-end test;
- **`n_eff_replicate` from the unresampled w:** the field is removed (M1), and its replacement is recomputed by hand.

**Low.**
- §8 now reads "the other six".
- A non-positive-definite uniform matrix refuses at B4, with a test, instead of raising a TypeError.
- §4.1 says why the jackknife was not chosen.

**Second mutation receipt** (2026-10-27T20:18–20:30Z, on `33b0a709…`; its log is in this branch's history at `49c20780`): **30 of 30 killed.** The tool was restored, and
its sha256 checked after every mutant. The first round's survivor, ddof 0, is now killed too, because the end-to-end
and pure tests recompute `sd_over_sigma_w_root_n_eff` by hand with ddof 1.

**Focused re-review of `49c20780`.** Everything else was resolved; the reviewer's three new mutants were killed, and
the 29 tests passed. It found one high and two lows, all done:
- **High: the follows-x arm compared against the wrong target.** With likelihood weights, the weighted ensemble
  estimates C_post, not the prior C_true, so the comparison with χ²(C_true) was bound to give 0.00. The reviewer said
  the fault began with them: they wrote that arm in their first round, then dropped it without saying so. §4.3 now uses
  their C_post rerun on the same seeds: 0.47 and 0.45 percentile coverage, and 0.57 and 0.61 basic, with median offsets
  +0.43 and +1.11. Their script and log are committed under `review/`. The conclusion is that neither band is an interval
  for the true-correlation χ². In the toy, coverage of the nominal 0.68 is about 0.32–0.61 across both arms, whether or
  not the weights follow the values. The re-review's "about 0.45–0.61" covers the C_post arm. With independent weights,
  the percentile band's 0.37 and 0.32 sit below it.
- **Low: "biased high" was stated as fact.** §4.3 and the tool's docstring now attribute it to the review's synthetic
  check. On real inputs, the direction is whatever the offset shows.
- **Low: the offset's label.** It now calls median − χ̂ the bootstrap's estimate of χ̂'s bias, in §0, the readout's
  `band` label and §4.3.

**Third mutation receipt** (`mutants.log`, 2026-10-27T23:16Z–2026-10-28T00:06Z, on `48c6eb04…`, whose changes from
`33b0a709…` are text only: the docstring and the `band` label): **30 of 30 killed**, with the tool restored.

# DECLARATION 3D: the flux-correlation bootstrap over the 100 universes (2026-10-27)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's decision `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` (PR #423, main
  `289f4457`), item 3: "3D runs: a bootstrap of the flux correlations over the 100 universes … declared, then bound, on
  a login node at 0 node-h". Joseph's selected option was "Yes, run 3D (Recommended)".
- The director's request of 2026-10-27:
  - define the statistic and its band here, with no p values;
  - say how n_eff 19 enters the band.

**After:** [`LIMITATION-PLAN.md`](LIMITATION-PLAN.md) §3.2, option 3D (PR #421), and G-SENS2
([`FD-G-SENS2-REPORT.md`](FD-G-SENS2-REPORT.md)). G-SENS2 shrank the flux correlations by an arbitrary α. 3D measures
how well the 100 weighted universes pin those correlations.

**Declares:**
- a new tool, `nd-unfolding/fd_flux_boot.py`, and its tests;
- the replicate scheme, the statistic and the band;
- the exact argv, the controls, the readout schema and the stop rule.

**MEASURES:** nothing. The tool has run only on synthetic fixtures.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit and has run only on synthetic fixtures -->

**CANNOT AUTHORIZE:**
- running it, which needs the director's binding first;
- any reading, claim or printed wording, including the new form of the paper's sensitivity sentence. That goes
  through the PRD read and the truth column, then to Joseph (decision item 3);
- any change to a covariance, cell or readout.

**CITABLE FOR:** what 3D will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:** any result.

## 0. Summary

**The question.** Stage G's χ² depends on how strongly the flux block correlates the cells. In the block alone, R04–R08
correlate at +0.983 (`FD-G-FOLLOWUP-REPORT.md:180-198`). G-SENS2 weakened those correlations by a chosen α. 3D asks
instead how much the χ² moves when the correlations are re-estimated from the same 100 universes, given that the
weighted ensemble holds only about 19 universes' worth of information (n_eff = 19.06, `S1-REPORT.md:288`).

**The replicate.** S1 builds the flux block from the 100 PPFX Flux universes as MAT's weighted `CalcCovMx`, using the
ν-e + IMD constraint weights w (`s1_assemble.py`, `mat_cov` and `flux_weights`; `S1-DECLARATION.md` row 10).
- Replicate b draws 100 universe indices uniformly with replacement. Each drawn universe carries its own weight.
- The block is then rebuilt with exactly S1's rule: C*_b = mat_cov(X[i_b], w[i_b]).
- X holds the universes' 16-cell integrals, U · xsec_flat, the integration rule of S1 and Stage G.

**Two variants of the swapped block.** Each replaces the flux group, and only it, in Stage G's reported matrix
C_total + C_resp + V_g:
- **`correlation` (primary):** S1's flux variances, bit for bit, with the replicate's correlations,
  D₀^½ ρ*_b D₀^½. This is the quantity G-SENS varied, since G-SENS keeps the variances when it shrinks.
- **`block` (second):** C*_b itself, with its variances included. It adds the variance scatter that c04-repair put at
  "a rough ±16% relative sampling scatter on σ" (`2d-closeout/c04-repair/REPORT.md:288-289`).

**The statistic.** For each prediction and variant, it is the distribution over the B = 2000 replicates of:
- the total χ² on the prediction's own cells (GiBUU on its eight), and
- the shape-only χ², Stage G's free normalization 100·11ᵀ relative to f.

Everything is relative to f, as in G-SENS.

**The band.** Each distribution's 2.5, 16, 50, 84 and 97.5 percentiles, numpy method `linear`, with the minimum and
maximum.
- The same percentiles are given from replicates 1–1000 and 1001–2000, to show the Monte Carlo scatter.
- Beside each band sits Stage G's χ² itself, which is the identity replicate.
- The R04–R08 correlation gets the same band twice: in the flux block alone, and in the reported matrix
  C_total + C_resp with each variant.
- **No p-value, and no tail fraction.** The readout has no key `p`, and a test asserts this.

**How n_eff enters the band (§4.2).** Under this resampling, a weighted estimator's spread is governed by
Σw²/(Σw)² = 1/n_eff. So the band is about as wide as an unweighted bootstrap over 19 universes would be, not over 100.
The readout shows this directly:
- each replicate's own n_eff* = (Σw*)²/Σw*², as a band;
- per cell, `delta_method_ratio`: the bootstrap sd of the weighted mean universe integral over its linearized value
  √(Σw²(x−μ)²)/Σw. It is expected near 1.

**One named alternative, `uniform`.** The block built from the 100 universes with equal weights: the flux prior
without the constraint (n_eff = 100). It gives one χ² per prediction, and its R04–R08 correlation. It is labelled a
named alternative, not an alternative result.

**Cost:** 0 node-h, on a login node. No Slurm job, and nothing written to CFS.

**Stop rule:** any refusal, any non-zero exit, or a run past 1.25× its projected wall is reported unrepaired.

## 1. Inputs

**Stage G's inputs and pins, unchanged,** as G-SENS2 used them (`FD-G-SENS2-DECLARATION.md` §1) and as G-DIAG's
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

**New:**

| input | where | checked against |
|---|---|---|
| the 100 Flux universe products | `$T/s1/readout/s1_assembly/S1_Flux_0.npz` … `S1_Flux_99.npz`, committed (PR #348) | each file's sha256 against the S1 readout's `meta.inputs_sha256`, whose own digest is pinned (B0). Each meta must read `s5p-universe/1` and `Flux:<u>` |
| the constraint file | `$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2`: the tool's pin (`s1_assemble.CONSTRAINT_SHA256`), and the S1 readout's `meta.inputs_sha256.constraint`. Σw and n_eff must equal the readout's `meta.flux_weights` (B0) |

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
- `tests rc=0` with "Ran 201 tests … OK". That is 27 for 3D and 174 as G-SENS2 declared them, run locally on
  2026-10-27. Its `CommittedPins` tests also re-check, on the deploy, the 100 committed universes' digests and the
  index-matrix digest under the cluster's numpy.

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

- **Projected wall: 5 minutes.**
  - G-SENS2's load took about 1 s.
  - The 100 universe reads and 2000 × 2 × 5 pairs of 16 × 16 Cholesky solves take seconds, as they do on the
    synthetic tree in the end-to-end test.
  - The timeout is 375 s, which is 1.25 × the projection.
- **Exit codes:**
  - 0: every control passed and the readout was written;
  - 1: a control refused, an overwrite was refused, or an unexpected error occurred, and nothing was written;
  - 2: an argparse error;
  - 124: past the timeout.

  Any exit other than 0 is a STOP.
- **What is committed** in the report's PR:
  - `$B/fd_flux_boot_readout.json`, as `fd/readout/fd_flux_boot_readout.json`;
  - the logs and step scripts, under `fd/receipts-flux-boot/run/`;
  - a ledger row.
- **The results index:** if the readout enters the index population, it is regenerated in-branch under the
  director's standing ruling (a).

## 3. Controls

All of them run before anything is written. Each one refuses: exit 1, with nothing written.

**D0–D5: G-DIAG's controls, unchanged,** through `fd_g_diag.load`. They pin and check Stage G's inputs and reproduce
Stage G.
- Tested by G-DIAG's tests, and by `test_the_real_script_reaches_d0_and_refuses_synthetic_records`.

**B0: the inputs.**
- **What it checks:**
  - the constraint file's digest is the tool's pin and the one S1's readout recorded;
  - S1's parser (`flux_weights`) accepts it;
  - its Σw and n_eff equal S1's recorded values to 10⁻¹²;
  - the 100 universe files exist, in order 0–99;
  - each file's sha256 is the one S1's readout recorded, S1 records exactly 100, and each meta is
    `s5p-universe/1`, `Flux:<u>`.
- **Tests:** `test_b0_a_universe_whose_digest_is_not_s1s`; `test_b0_a_universe_named_for_another`;
  `test_b0_a_missing_universe`; `test_b0_s1_records_another_number_of_universes`;
  `test_b0_the_constraint_file_is_not_the_pin_or_s1s` (the pin, and S1's record); `test_b0_the_weights_are_not_s1s`
  (n_eff × (1 + 10⁻⁹)); `test_b0_too_few_flux_weights`.

**B1: S1's block, rebuilt.**
- **What it checks:**
  - the flux group is `band:Flux` alone;
  - the block rebuilt from the 100 universes with their weights, the identity replicate, equals S1's to 10⁻¹² relative.
- **Test:** `test_b1_the_block_rebuilt_without_the_weights`.

**B2: Stage G, reproduced.** Swapped into the reported matrix, the rebuilt block reproduces Stage G's total and
shape-only χ² for every prediction, to 10⁻¹⁰ relative.
- **Test:** `test_b2_a_shape_only_chi2_that_is_not_stage_gs`.

**B3: the replicates.** The 2000 × 100 index matrix from `default_rng(20261027)` hashes, as `<i4`, to the declared
`INDEX_SHA256`. A numpy whose generator differed would refuse here.
- **Tests:** `test_b3_another_index_matrix`; `test_the_seed_gives_the_declared_index_matrix`.

**B4: every replicate is usable.** Every replicate's flux variances are positive, and every swapped matrix is positive
definite (Cholesky).
- **Tests:** `test_b4_a_replicate_with_a_non_positive_variance`; `test_b4_an_indefinite_swapped_matrix` (positive
  diagonal, correlations above 1).

**B5: the correlation variant keeps S1's flux variances,** bit for bit, in every replicate.
- **Test:** `test_b5_a_swap_that_moves_a_variance_by_one_ulp`.

**The pure functions** are tested beside the controls:
- the identity replicate is S1's rule, and agrees with an independent weighted covariance;
- a replicate carries each drawn universe's weight;
- the swap keeps the variances and takes the correlations, and is exactly symmetric;
- χ² and shape-only χ² by inverse, and None when the matrix is not positive definite;
- the band's percentiles and halves;
- the spread follows 1/n_eff (§4.2).

**End to end, as invoked** (`-I -B`, cwd outside nd-unfolding):
- every band's percentiles, minimum, maximum and second-half median;
- the R04–R08 flux-block median and the uniform χ²;
- each recomputed by an independent loop (`by_hand`: an `einsum` weighted covariance and inverse quadratic forms), to
  10⁻⁹ relative;
- the identity equals Stage G's committed χ²;
- GiBUU on its eight cells, and no key `p`.

## 4. Statistics, as built

### 4.1 The replicate scheme, and the two not chosen

**Chosen: the nonparametric bootstrap over universes, each carrying its weight.** Its unit is the universe, which is
the independent draw in PPFX. The estimator is S1's, unchanged, applied to the resampled set. Its spread is therefore
the sampling scatter of the very number S1 reports.

**Not chosen:**
- **Resampling with probability ∝ w, then unweighted.** That draws 100 universes from the weighted ensemble and treats
  them as 100 independent draws from the target. Its spread corresponds to n = 100, not n_eff ≈ 19. It would understate
  the scatter by about √(100/19) ≈ 2.3.
- **The Bayesian (Dirichlet) bootstrap,** with weights w·g and g ~ Dirichlet(1, …, 1). It agrees with the chosen
  scheme to first order, and is smoother. It is less standard, and adds nothing that the director's band needs.

### 4.2 How n_eff enters

**For a weighted mean** μ̂ = Σwᵢxᵢ/Σwᵢ, the scheme's variance is, to first order, Σwᵢ²(xᵢ − μ)²/(Σw)².
- When the residuals do not follow the weights, that is σ²·Σw²/(Σw)² = σ²/n_eff.
- A covariance or a correlation is a smooth function of weighted first and second moments, so its scatter scales the
  same way.
- The band is therefore that of about 19 effective universes. The readout carries the two diagnostics in §0
  (`n_eff_replicate` and `delta_method_ratio`). The test `test_the_spread_follows_one_over_n_eff` shows, on synthetic
  universes, both:
  - the ratio within 12 % of 1, for both weight sets;
  - the spread widening by √(100/19), within ±30 %, from equal weights to weights with n_eff ≈ 19.

### 4.3 What the band is and is not

**It is the scatter of Stage G's χ² under re-estimation of the flux correlations from these 100 universes.** It
replaces α = 0.1 with a measured spread.

**It is not:**
- a confidence interval with guaranteed coverage;
- a model of PPFX itself. The universes are taken as given.
- an alternative result.

**At small n_eff the bootstrap distribution of a correlation can be skewed, and centred away from S1's value.** For
that reason Stage G's χ², the identity replicate, is printed beside every band, and the full set of percentiles is
given rather than a symmetric width.

### 4.4 Reused code

- **S1's:** `mat_cov` and `flux_weights` (`s1_assemble.py`).
- **G-DIAG's:** `load`, which runs D0–D5, plus `finite`.
- **G-FOLLOWUP's:** `prediction_blocks`, the reported matrix's relative blocks, its residual, and each prediction's
  cells.
- **Stage G's:** `SHAPE_LAMBDA`.

## 5. The readout, `fd-flux-boot-readout/1`

```text
schema, labels{what, replicate, variants, uniform, n_eff, band, units, not}, controls_passed[D0..D5, B0..B5],
constants{replicates 2000, universes 100, seed 20261027, index_sha256, percentiles, percentile_method, variants,
          pair [R04, R08], reproduction, reported_matrix},
identity{prediction: {chi2_stage_g, shape_only_stage_g, chi2_rebuilt, shape_only_rebuilt, relative_difference}},
bands{correlation | block: {prediction: {cells, ndf, chi2_stage_g, shape_only_stage_g,
      total | shape_only: {percentiles{2.5, 16, 50, 84, 97.5}, min, max, halves[2]}, label}}},
correlation_band{flux_block, reported_matrix_correlation, reported_matrix_block: band},
correlation_s1{flux_block, reported_matrix},
n_eff{s1, sum_w, n_eff_replicate: band, delta_method_ratio{R00..R15}},
uniform{n_eff 100, predictions{prediction: {chi2, shape_only}}, pair_correlation_flux_block, label},
inputs_sha256, code_sha256{fd_flux_boot.py, fd_g_followup.py, fd_g_diag.py, fd_g_compare.py, s1_assemble.py}, argv,
non_finite_written_as_null
```

**stdout prints:**
- the PASS lines;
- the label line;
- one `[3D]` line per variant and prediction, with Stage G's χ², the 16–84 % and 2.5–97.5 % bands, and the uniform χ²;
- one n_eff line;
- the `wrote` line.

## 6. Code and tests

### 6.1 `nd-unfolding/fd_flux_boot.py` (new)

**What is in it:**
- the pure functions `indices`, `index_digest`, `replicate_block`, `n_eff`, `correlation_swap`, `chi2s`,
  `correlation`, `band` and `delta_method_ratio`;
- the input checks `weights` and `universes` (B0);
- `run`, which holds B1–B5, the bands and the readout.

**Constants:**
- `B_REPLICATES` 2000 and `SEED` 20261027;
- `INDEX_SHA256` `23e2e374…`;
- `PERCENTILES` (2.5, 16, 50, 84, 97.5);
- `VARIANTS` (correlation, block);
- `PAIR` (R04, R08).

The seed, B and the percentiles are constants, not arguments, so the argv cannot choose them.

### 6.2 `nd-unfolding/tests/test_fd_flux_boot.py` (new, 27 tests)

| class | tests |
|---|---|
| `Pure` | 7 |
| `EndToEnd` | 3 |
| `Controls` | 13 |
| `Invocation` | 2 |
| `CommittedPins` | 2 |

**The fixture is `BootTree`:**
- G-DIAG's synthetic tree;
- 100 synthetic universes, a common scale, a tilt and noise, with lognormal weights solved to n_eff ≈ 19, written as
  `S1_Flux_<u>.npz`;
- a constraint file with distractor lines (another band, and Flux 100 and 101);
- S1's readout meta recording both.

### 6.3 Mutation receipt

`fd/receipts-flux-boot/declaration/mutants.py` applies 20 one-line mutants to the tool, in place, and runs the four
non-pin test classes against each. It restores the tool, and checks the tool's sha256 after every mutant and at the end.
The log is `mutants.log`; the outcome is in §11.

## 7. For the director

1. **The primary variant is `correlation`.** It keeps S1's variances, as G-SENS did, so the band is about the
   correlations alone. `block` is the second record. Rule if the paper's sentence should use `block` instead.
2. **B = 2000 and the seed 20261027.** At 2000 replicates, the Monte Carlo error on a 16th or 84th percentile is about
   2 % of the 16–84 % width, for a normal distribution: √(0.16 × 0.84/2000)/φ(1) ≈ 0.034σ against a width of 2σ. The
   halves show it.
3. **The band's percentiles:** 16–84 % and 2.5–97.5 %, with the median. The readout has no p-value and no tail
   fraction against α = 0.1 or anything else.
4. **`uniform`** is a single named alternative, not bootstrapped. It changes the variances as well as the correlations,
   since the constraint narrows the flux, so it is not on the same footing as the band.
5. **The pair R04–R08** is G-FOLLOWUP's. Other pairs can be added before binding.
6. **`delta_method_ratio` and `n_eff_replicate` are descriptive.** Neither is a control, so a ratio away from 1 on the
   real universes does not stop the run. It is reported.

## 8. Pinned bytes

At this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_flux_boot.py` | `bed614c1c6dc75f0644996da580d60871053aa411c3204fdd516f9284d334315` |
| `nd-unfolding/tests/test_fd_flux_boot.py` | `89157b7ff5d9c62b36a8ecdef344128e35b62066c7461b15e5feb2d2186e245f` |
| `nd-unfolding/fd_g_followup.py` | `ec8cbc6880f7a3f67eea5703ddeff958acb10462053696d2cfdb64de0ee5f60d` |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json` | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` |

Only the first two are new. The other four are unchanged from `main`.

## 9. Ledger, storage and stops

- **Ledger:**
  - one row for the deploy and tests, and one for the run, in `fd/LEDGER.tsv`;
  - 0 node-h, on a login node, with no Slurm job.
- **Storage:**
  - `$B` on pscratch joins the retention list;
  - nothing is written to CFS;
  - the readout is committed;
  - the inputs are already preserved: S1's universes are committed, and S1, C_resp and the predictions are as for
    G-SENS2. So no HPSS copy is needed.
- **Stops:** §0's stop rule. No step is rerun or repaired without the director.

## 10. Not changed

- Every covariance, cell, readout and κ.
- `docs/analysis-note/**`, including the paper's sensitivity sentence. Its new form is for the paper lane, through the
  PRD read and the truth column, then Joseph.
- The fake-data limitation, which stays as stated (decision item 2).

## 11. Review dispositions

**Mutation receipt** (`fd/receipts-flux-boot/declaration/mutants.log`, 2026-10-27T19:23–19:30Z): **19 of 20 mutants
killed.** The tool was restored, and its sha256 checked after every mutant.
- **The survivor:** `delta method ddof 0`, which changes the descriptive `delta_method_ratio` by a factor
  √(1999/2000). It is harmless, and within the synthetic test's 12 % tolerance by design.

**Independent review:** pending. It is to be run read-only before the PR opens, with its findings folded in here.

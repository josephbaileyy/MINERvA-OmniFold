# DECLARATION: the cheap tier's three login-node readers, 3a, 4C and 5A (2026-10-28)

**By** the measurement session (`coverage`), for the director to bind.

**Under:**
- Joseph's decision [`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`](../../../DECISION-20261028-joseph-d2-approved-and-cheap-tier.md)
  item 2: the cheap tier "runs first … under the standing approval for jobs under 12 h, declared and bound as usual".
  Item 3 leaves 1B and 4B until it reports.
- The director's ruling (1) of 2026-10-28, given in a message after PR #460: "One declaration for the three 0-node-h
  readers, 3a, 4C and 5A. Separate declarations for 3b and 5B."

**After** [`LIMITATION-PLAN-ADDENDUM-20261028.md`](LIMITATION-PLAN-ADDENDUM-20261028.md): §3.2 (3a), §4.2 (4C) and
§5.2 (5A). The inputs' retention is in [`FD-CT-RETENTION.md`](FD-CT-RETENTION.md).

**Declares:**
- a new tool, `nd-unfolding/fd_ct_readers.py`, with subcommands `recoil` (3a), `chi2` (4C) and `period` (5A), and its
  tests;
- each reader's statistic, inputs, exact argv, controls, readout schema and stop rule.

**MEASURES:** nothing. The tool has run only on synthetic fixtures.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this branch and has run only on synthetic fixtures -->

**CANNOT AUTHORIZE:**
- running it, which needs the director's binding first;
- any covariance component, change to the reported matrix C_total + C_resp, or to κ. For items 3 and 5, a block
  printed beside the reported matrix, not in it, keeps the matrix fixed (addendum §5.4); adoption is Joseph's;
- a coverage, calibration or χ²-distribution statement;
- any reading, claim or printed wording.

**CITABLE FOR:** what each reader will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:** any result. Once run:
- 3a is not a bias under response mismatch and not a closure; it does not validate C_resp;
- 4C is not a calibration of any χ²;
- 5A is not a run-period effect in the hadronic variables, and not a 5D run-period block.

## 0. Summary

All three run on a login node at 0 node-h, with no Slurm job and nothing written to CFS. Every output is relative to f
or to a product's own integrals, and passes F0's leak guard (ruling 6) before it is written.

### 3a, `recoil`: W2b's ±4 % recoil data unfolds on the 16 cells

- **The inputs:** W2b's three data unfolds of the whole simulated reconstructed recoil at s = 0.96 (`rr0`), 1.04 (`rr1`)
  and 1 (`rrzero`), each made by (e) on its own lateral dump (`publication/w2/W2B-REPORT-20261006.md` §1, §8).
- **The statistic,** per cell, with X = U · xsec_flat (S1's integration rule):
  - s₋ = X_rr0 / X_rrzero − 1 and s₊ = X_rr1 / X_rrzero − 1;
  - the half-span d = (X_rr1 − X_rr0) / (2 X_rrzero), C_resp's own two-endpoint form (`build_cresp.py`, `species_block`);
  - beside each: σ/f of C_resp, of C_total and of C_total + C_resp, and |d|/σ for C_resp and for C_total + C_resp.
- **Three descriptive numbers:**
  - the half-span's quadratic form dᵀ M⁻¹ d, for M = (C_total + C_resp)/(f fᵀ) and C_total/(f fᵀ): a length in σ units;
  - the fraction of d in C_resp's range, ‖P d‖²/‖d‖² in relative units, with P the projector onto C_resp/(f fᵀ)'s
    eigenvectors above 10⁻¹² of its largest. 1 means a whole-recoil scale moves the cells only in the four species'
    directions. A direction drawn at random gives rank/16 = 0.25 in expectation, which the readout writes beside it.
    The value depends on the units: the review measured 0.24 in relative and 0.99 in absolute units for one d;
  - the curvature ratio in `build_cresp`'s G3 form on the cell integrals, ‖X₊ + X₋ − 2X₀‖/‖X₊ − X₋‖, so that it is
    comparable with C_resp's own.
- **The reference is `rrzero`, not f.** W2b's δ = 0 unfold is not bitwise the production product; its control passed by
  the fallback criterion (`W2B-REPORT-20261006.md` §4). Its lateral dump is byte-identical to MP-1 S1's zero dump
  (`6ca02c3d…`, `FD-CT-PRESERVE-REPORT.md` receipts `decl1.out`), and its background dump differs.
- **What it is:** a data-side sensitivity at a second construction (one coherent scale), as the addendum scopes it. It
  is not a mismatch closure: the pseudo-data and the unfolding share each variant's response.

### 4C, `chi2`: the χ² spread of A7's existing nuisance-drawn experiments

- **The inputs:** FD-PLAN row 5, the A7 calibration products at MnvTune v1 (1,365), GENIE 2.12.10 CV (1,366), GENIE
  MEC (1,343), NuWro 21.09 (1,751) and GiBUU 2019 (1,351): 7,176 in all (`FD-PLAN.md:146`; `fd_f0_regrade.COUNTS`).
- **Per experiment i at truth T,** r_i = X̂_i / X_true,i − 1 on the cells (F0's estimator, from each product's own
  `xsec_flat` and `xtrue_flat`), and
  - χ²_i about the truth, r_iᵀ M⁻¹ r_i;
  - χ²_i about the NuE-weighted mean, (r_i − b̃)ᵀ M⁻¹ (r_i − b̃), with b̃ = Σ w r / Σ w.
- **The weights** w are each experiment's drawn flux universe's ν-e + IMD constraint weight, F0's row-5 weighting.
  Weighting makes the ensemble's flux follow S1's constrained flux; the unweighted values are written beside them.
- **Two matrices:** M = (C_total + C_resp)/(f fᵀ), the reported matrix without V_g, since the truth is fixed; and
  C_e/(f fᵀ), the drawn-block analogue.
- **Cell sets:** all 16, and for GiBUU also its eight p_∥ < 4.5 cells, read from the definition and checked equal to
  `fd_f0_regrade.GIBUU_CELLS` (C1). Stage G compares GiBUU on them.
- **Written per truth, matrix and cell set:** the weighted and unweighted mean and 5, 16, 50, 84 and 95th percentiles of
  both χ², both by the inverted ECDF (the unweighted with unit weights), beside χ²_ndf's mean and percentiles; the χ² of b̃ itself; and the per-cell width ratio, the weighted sd of
  r over √diag M.
- **No p value and no tail fraction.** The readout has neither, and a test asserts it (the 3D binding's ruling 4).
- **Descriptive only.** LIMITATION-PLAN's disqualifiers hold (`LIMITATION-PLAN.md:148-160`):
  - F0's offset control 7 failed, χ²₁₆ = 245.74 (`FD-F0-REPORT.md:39-41`);
  - A7's draws are not S1's: one flux universe of 100 drawn uniformly, model bands that move only the response, and
    laterals not applied (`nd-unfolding/s5p_nullexp.py:13-30`);
  - the truths are hybrids on the J cells, and the products unfold with half of the MC.
  - C_model is not drawn, so the reported matrix is expected to over-cover the toys' scatter (`LIMITATION-PLAN.md:198-200`).

### 5A, `period`: the 2D run-period term projected onto the 16 cells

- **The input:** the adopted 2D term's `playlist_term.npz` (`c1723cb5…`): per period X ∈ {PA, PB, PC} and 2D cell b,
  the offset g_X,b = r_X,b / m_b − 1 of the double ratio from its exposure-weighted mean, with exposure shares e_X
  (`state/2d-closeout/playlist-term/DESIGN.md` §2).
- **The projection.** Each R-cell's (p_T, p_∥) footprint is a set of whole 2D cells: the 5D fine grid's p_T and p_∥
  edges are the 2D grid's (`s5p_stage1_inspect.FINE`; `playlist-spread-20261014/coverage/scripts/common.py:17-18`), and
  the H2 splits at p_T = 0.7 and p_∥ = 4.5 fall on those edges. Then
  - ω_R,b = W_R,b / Σ_{b supported} W_R,b, with W_R,b = Σ over R's fine cells in b of x_f vol_f;
  - g_X,R = Σ_b ω_R,b g_X,b;
  - C_PL,16 = k Σ_X e_X g_X,R g_X,Rᵀ relative to f, with 2D's own k = V2/(1 − V2), V2 = Σ e_X².
- **Why this form.** If the period offset does not depend on E_avail, q3 or W inside a 2D bin, a cell's period-X
  integral is Σ_b (1 + g_X,b) P_R,b, with P_R,b the pooled content of R in b. So g_X,R is the content-weighted mean of
  g_X,b, the identity Σ_X e_X g_X,R = 0 carries over exactly, and C_PL,16 is 2D's estimator on the cells.
- **The weights x:** primary, the (e) central value, the pooled data result that 2D's x = E_U corresponds to; as a
  declared sensitivity, MnvTune v1's prior. The addendum's scoping said "the cell's prior weight" (§5.2); the director
  chooses (§7 item 6).
- **The 2D term's support.** It covers 205 of the 224 2D cells (`playlist_term.py:90`). Measured from the binning alone
  (the committed fine map and the npz's `cells`, no values): R00–R07 lie wholly inside it; R08–R11 take 17 of their 36
  2D bins outside it, and R12–R15 take 2 of their 60.
  - The projection renormalizes over the supported bins, and writes each cell's weight share outside, u_R.
  - A cell with u_R > 0.10 is labelled extrapolated (§7 item 7).
- **Written:** per weighting, g_X,R per period and cell; σ/f of C_PL,16, of the S-ref sensitivity S_ref,16 =
  Σ_{X∈{B,C}} b_X,R b_X,Rᵀ, and of C_total + C_resp; their ratio; the trace share of C_PL,16 in
  C_total + C_resp + C_PL,16; C_PL,16 itself and its rank; the extrapolated cells; and the number of 2D cells in each
  footprint with negative weight.
  - S-ref's b_X = e_X (r_X / r_A − 1) is 2D's own (DESIGN §2), formed on the 2D cells and projected by the same
    linear rule as g. Averaging r first and then forming the ratio would reweight the footprint by the data/MC ratio,
    which the review measured as a factor of 0.80–1.50 on σ.
  - u_R is written for the prior weighting only. For the central value, u_R = 1 − X_sup/f, the X/f − 1 form of a
    partial data integral that also carries the result's shape inside the cell. Only the derived labels are written
    for it (§7 item 9).
<!-- absence-ok: a scoping statement about the design: the assumption is not tested here by construction, and only 5B can test it (LIMITATION-PLAN-ADDENDUM-20261028.md section 5.2) -->
- **What it is:** a size under an untested assumption. Built from the observed offsets, it contains them by
  construction and cannot fail (`2d-closeout/playlist-term/REPORT.md:19-20`). Only 5B can test the assumption.

**Stop rule:** any refusal, any non-zero exit, or a run past its timeout (1.25 × its projected wall) is reported
unrepaired.

## 1. Inputs

`$P` = `/pscratch/sd/j/josephrb`; `$T` = the deploy's `docs/orchestration/state/measurement-paper/5d-community-20261024`.
Every input is pinned in the tool (`PINS`, `W2B`) and re-measured on login08 at 2026-10-28T22:14Z
(`fd/receipts-ct/preserve/decl1.out`), unless marked.

| reader | input | where | sha256 |
|---|---|---|---|
| all | S1 assembly | `$P/s1-20261024/s1_assembly.npz` | `db000707…` |
| all | C_resp, adopted | `$P/cresp-20261026/out/cresp.npz` | `4d8b5797…` |
| all | H2 definition | `$D/nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b6790761…` (`s1_assemble.DEFINITION_SHA256`) |
| 3a | W2b rr0, rr1, rrzero | `$P/w2-recoil-20261006/w2b/unf/w2b_{rr0,rr1,rrzero}_b-_j-.npz` | `df11bfd8…`, `36313201…`, `ec5dc97d…` (`W2B-REPORT-20261006.md` §8); each one's input and background dump digests, from its own meta, are pinned too |
| 4C | the s5p archive sums | `$D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt` | `1a72cb43…` (committed) |
| 4C | the 7,176 calibration products | `$P/s5p-20260926/runs/prod/cal/<truth>/` | each against the sums (C0); HPSS `s5p-archive-20261006.tar` |
| 4C | F0b's readout | `$T/fd/readout/fd_f0b_readout.json` | `b9db935a…` (committed) |
| 4C | the flux constraint | `$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | `e38ad7d2…` (`s1_assemble.CONSTRAINT_SHA256`; not re-measured here, as 3D's run did on 2026-10-28) |
| 5A | the 2D term | `$P/tmp-playlist-term-20261016/out/playlist_term.npz` | `c1723cb5…`; also CFS `2d-closeout-playlist-term-20261016/` |
| 5A | its committed readout | `$D/docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json` | `5b023478…`, which names the npz |
| 5A | the (e) central value | `$P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz` | `fb5cc679…` (S1's G2) |
| 5A | MnvTune v1 | `$P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz` | `bf7bd278…` (`fd_g_compare.PREDICTIONS`) |

<!-- absence-ok: the constraint file's "not re-measured here" is a scoping statement about this declaration's probe -->

## 2. Exact commands

**Definitions:**
- `B=$P/fd-ct-readers-20261028`;
- `D=$B/deploy/<pin8>`, a clean clone of the binding commit;
- `PY=env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_ct_readers.py nd-unfolding/tests/test_fd_ct_readers.py nd-unfolding/fd_f0_regrade.py \
    nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-READERS-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_ct_readers test_fd_f0_regrade test_build_cresp test_s1_assemble test_s1_scripts_isolated \
  > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:** HEAD equal to the pin; 0 porcelain lines before and after; the §8 digests; `tests rc=0` with the
count §6.2 gives. Anything else is a STOP.

### 2.2 The three runs (login node, after §2.1, in this order)

```bash
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_ct_readers.py recoil \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --w2b-unf $P/w2-recoil-20261006/w2b/unf \
  --out-json $B/fd_ct_recoil.json > $B/logs/recoil.out 2> $B/logs/recoil.err; echo "rc=$?" >> $B/logs/recoil.out

cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_ct_readers.py chi2 \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --f0b-readout $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --out-json $B/fd_ct_chi2.json > $B/logs/chi2.out 2> $B/logs/chi2.err; echo "rc=$?" >> $B/logs/chi2.out

cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_ct_readers.py period \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --playlist-npz $P/tmp-playlist-term-20261016/out/playlist_term.npz \
  --playlist-json $D/docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json \
  --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz --prior $P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz \
  --out-json $B/fd_ct_period.json > $B/logs/period.out 2> $B/logs/period.err; echo "rc=$?" >> $B/logs/period.out
```

**Projected walls:** 60 s each for `recoil` and `period`, 300 s for `chi2`. F0's re-grade, which read these 7,176
calibration products among others with more work per product, exited in 44 s (`FD-F0-REPORT.md` §0); the timeouts are 1.25 × the projections.

**Exit codes:** 0, the readout was written; 1, a control refused or an overwrite was refused, with nothing written;
2, argparse; 3, the leak guard refused, with nothing written; 124, past the timeout. Any exit other than 0 is a STOP for
that reader. The three are independent: a STOP in one does not stop the others, and is reported as it stands.

**What is committed** (the report's PR): the three readouts as `fd/readout/fd_ct_{recoil,chi2,period}.json`; the logs
and step scripts under `fd/receipts-ct/run/`; ledger rows. If a readout enters the results index population, the index
is regenerated in-branch under the director's standing ruling (a).

## 3. Controls

Each refuses with exit 1 and nothing written, unless marked. Each test named makes it fire on a one-entry defect and is
in `test_fd_ct_readers.py`; the end-to-end tests show each stays silent on good input.

**S, shared** (every reader):
- the S1 assembly and C_resp match their pins (`test_refuses_another_s1_assembly`);
- U is S1's float32 functional matrix; f > 0 on every cell; C_total = C_e + C_model_abs;
- C_resp is the sum of its four primary species (`test_refuses_a_C_resp_that_is_not_its_species_sum`, which plants
  cross-talk);
- the file's C_total_resp equals S1's C_total + C_resp (`test_refuses_a_C_total_resp_that_is_not_C_total_plus_C_resp`).

**3a:**
- **R0:** each W2b product matches its recorded sha256 (`test_refuses_a_product_whose_digest_is_not_recorded`) and was
  made by (e) at seed 42, as data at the nominal truth, on its own input and background dumps
  (`test_refuses_a_product_made_on_another_dump`);
- **R1:** every W2b cell integral is positive (`test_refuses_a_non_positive_integral`).

**4C:**
- **C0:** the archive sums match their pin (`test_refuses_another_s5p_manifest`); each truth's directory holds exactly
  the products the sums list (`test_refuses_an_unlisted_product`); each product's sha256 is the one listed
  (`test_refuses_a_product_changed_after_its_manifest`);
- **C1:** each product is an A7 calibration experiment at its truth, by F0's `meta_problems` (`test_refuses_a_product_at_another_hypothesis`),
  in the declared count with no repeated seed (`test_refuses_a_count_other_than_declared`);
- **C2:** each truth's B_eff = (Σw)²/Σw² equals F0b's recorded `B_eff_calibration` to 10⁻¹² relative
  (`test_refuses_a_b_eff_that_is_not_f0bs`). This shows the products and weights are F0b's;
- **C3:** every truth integral is positive on all 16 cells (`test_refuses_a_non_positive_truth_integral`);
- **C1 also:** the definition's p_∥ < 4.5 cells are F0's eight GiBUU cells.
- **C4, an assertion,** written under `assertions_passed`, not `controls_passed`: for every truth, matrix and cell set,
  the weighted mean χ² about the truth equals the mean about b̃ plus b̃'s own χ², to 10⁻⁹ relative. It is an identity
  for a weighted mean, so it cannot fire on any input (the review: worst gap 1.4 × 10⁻¹⁴ over 2,000 random sets). It
  guards the code: round 1's "about-mean uses the unweighted mean" mutant was killed through it.

**5A:**
- **P0:** the fine grid's p_T and p_∥ edges are the 2D grid's, `common.py:17-18`, copied into the tool and checked
  against the committed file by a test (`test_refuses_a_2d_grid_that_is_not_the_fine_grids`); the npz and the
  committed JSON match their pins, and the JSON names the npz
  (`test_refuses_a_json_that_names_another_npz`); 205 distinct 2D cells on the 14 × 16 grid; one entry per cell in every
  period array; e_X constant over cells (`test_refuses_an_e_that_varies_by_cell`) and summing to 1; Σ_X e_X g_X = 0 on
  every cell (`test_refuses_offsets_that_do_not_cancel`); and C_PL rebuilt from k, e, x and g equals the stored C_PL to
  10⁻¹² (`test_refuses_a_stored_C_PL_that_is_not_rebuilt`);
- **P1:** the central value matches its pin, was made by (e) on S1's own input dumps, and integrates to S1's f
  (`test_refuses_a_central_value_that_is_not_s1s_f`);
- **P2:** the prior is MnvTune v1's `s5p-mc-truth-pred/1` on the fine grid's edges (`test_refuses_a_prior_of_another_schema`);
- **P3:** every cell has positive weight on the supported 2D cells (`test_p3_refuses_a_cell_with_no_weight_on_the_support`);
- **P4, an assertion:** Σ_X e_X g_X,R = 0 on the cells, and C_PL,16 is PSD of rank ≤ 2, for both weightings. P0
  implies it for a linear projection, so it cannot fire on inputs that pass P0. Its test calls the function directly
  (`test_p4_refuses_offsets_that_do_not_cancel_on_the_cells`).

**The leak guard** (exit 3, nothing written): F0's `LeakGuard`, with f and every integral the reader forms:
- 3a, the three W2b integrals; 4C, every product's X̂ and X_true; 5A, the prior's, and both weightings' integrals over
  the supported part of each footprint (X_sup), so that 1 − X_sup/X cannot be written by accident;
- the central value's integrals are f itself (P1) and are not passed again, nor is its X_sup where it equals f (a cell
  wholly inside the support): f/f = 1 would refuse every "1" in a string;
- **tests:** a planted f (`test_the_guard_refuses_a_planted_absolute_value`); a planted product integral in each
  reader (`test_the_guard_refuses_a_planted_product_integral`, `…_planted_truth_integral`,
  `…_planted_partial_data_integral_or_its_share`, which also plants the central u_R); and scans of the written text.

**Overwrite:** an existing `--out-json` refuses (`test_refuses_to_overwrite`).

## 4. Statistics, as built

- **Integration** is S1's: X = U · xsec_flat with U the fine-bin volumes per cell (`s1_assemble.functional_matrix`).
- **3a's divisor** is `rrzero`, so the shifts are W2b's own, free of the δ = 0 chain's difference from production. σ/f
  uses S1's f. The two differ by that chain difference, which W2b bounds by its jitter criterion; the ratio |d|/σ
  carries it at first order.
- **4C's percentiles:** unweighted by numpy's `linear`; weighted by the inverted weighted ECDF (the smallest value whose
  cumulative weight share reaches p). χ²_ndf's percentiles are by bisection on F0's exact even-ndf survival function.
- **4C's width ratio** uses the weighted sd with denominator Σw, as F0's `weighted` does.
- **5A's linear rule.** Everything 5A projects is a relative offset on the 2D cells, g_X or S-ref's b_X, averaged with
  the footprint weights ω. This is exact under the assumption, keeps Σ_X e_X g_X,R = 0, and treats C_PL,16 and
  S_ref,16 alike (review M1).
- **Reused code:** F0's `LeakGuard`, `meta_problems`, `listed_set`, `relative_manifest`, `require`, `report`,
  `chi2_sf_even`, `TRUTHS`, `HYP`, `COUNTS` and `GIBUU_CELLS`; S1's `fine_map`, `functional_matrix`, `check_meta`,
  `flux_weights` and `xs`.

## 5. The readouts

```text
fd-ct-recoil/1: labels{what, not_citable_for}, controls_passed, cells, scales, shift_minus, shift_plus, half_span,
  half_span_summary_abs, sigma_rel{C_resp, C_total, C_total_resp}, abs_half_span_over_sigma{C_resp, C_total_resp,
  *_summary}, half_span_quadratic_form{C_total_resp, C_total, label}, fraction_of_half_span_in_C_resp_span{value,
  C_resp_rank, random_direction_expectation, label}, curvature_ratio{value, label}, inputs_sha256, code_sha256, argv

fd-ct-chi2/1: labels{what, not_citable_for, no_p_values}, controls_passed, assertions_passed{C4},
  constants{percentiles, weights, matrices},
  truths{name: {cal, n_experiments, B_eff, matrices{C_total_resp | C_e: {all16 [, gibuu8]: {cells, ndf,
  about_truth | about_weighted_mean: {weighted{mean, percentiles}, unweighted{mean, percentiles},
  reference_chi2{ndf, mean, percentiles}}, chi2_of_weighted_mean_bias, width_ratio, width_ratio_summary}}}}},
  inputs_sha256, code_sha256, argv

fd-ct-period/1: labels{what, not_citable_for}, controls_passed, assertions_passed{P4}, cells, constants{periods, e,
  k, extrapolated_above, weights}, variants{central | prior: {g{PA, PB, PC}, sigma_rel{C_PL16, S_ref16,
  C_total_resp}, sigma_rel_summary, sigma_ratio_to_C_total_resp, sigma_ratio_summary, trace_share, C_PL16_rel, rank,
  extrapolated_cells, negative_weight_2d_cells [, weight_outside_2d_support: prior only]}}, inputs_sha256,
  code_sha256, argv
```

The 4C readout's keys are exactly these; a test fails on any other key (`CHI2_KEYS`), so a tail fraction cannot be
added under another name (review L3).

**stdout:** the PASS lines; one `[3a]`, five `[4C]` or two `[5A]` summary lines; the `wrote` line with the readout's
sha256.

## 6. Code and tests

### 6.1 `nd-unfolding/fd_ct_readers.py` (new)

`common` (control S); `run_recoil`, `run_chi2` and `run_period`, each holding its controls and readout; the pure
functions `chi2_quantile`, `weighted_percentiles`, `distribution`, `footprint`, `period_variant`, `quad`, `rel_sigma`
and `summary`. The constants `PINS`, `W2B`, `CAL`, `PERCENTILES`, `PERIODS` and `EXTRAPOLATED` are constants, not
arguments, so the argv cannot choose them.

### 6.2 `nd-unfolding/tests/test_fd_ct_readers.py` (new)

| class | tests |
|---|---:|
| `Pure` | 5 |
| `Recoil` | 16 |
| `Chi2` | 12 |
| `Period` | 20 |
| `Invocation` | 2 |
| `CommittedPins` | 4 |
| **total** | **59** |

**The fixture, `Tree`,** builds every input from known cell integrals on the committed H2 definition: fine arrays whose
cell integrals are exactly the chosen values, a synthetic S1 assembly and C_resp, three W2b products, 40 calibration
experiments per truth with flux draws and a constraint file, a synthetic 2D term with 205 supported cells (its 19
unsupported cells laid out as the measured binning's), and central and prior products.

**Recomputed independently:** 3a's shifts, half-span, σ ratios, quadratic form and in-span fraction (by least squares on
the four species' directions); 4C's χ² by explicit inverses and `einsum`, its percentiles, the weighted median by a
cumulative-weight scan, b̃'s χ² and the width ratio; 5A's footprint weights by explicit accumulation over fine cells,
and C_PL,16, S_ref,16, the σ ratios, u_R and the trace share from them.

**As invoked:** the module through a wrapper that sets only the pins, `-I -B`, cwd outside nd-unfolding; and the real
script, with its real pins, refusing the synthetic tree at R0 with nothing written.

**The declared deploy set** is `test_fd_ct_readers`, `test_fd_f0_regrade`, `test_build_cresp`, `test_s1_assemble` and
`test_s1_scripts_isolated`: **Ran 150 tests, OK**, locally with `-B` and a TMPDIR on 2026-10-29, at the §8 digests.

### 6.3 Mutation receipt

`fd/receipts-ct/declaration/mutants.py` applies one-line mutants to the tool in place, runs the whole test module
against each, and restores the tool, checking its sha256 after every mutant and at the end. A mutant whose text is not
found exactly once counts as a failure of the receipt. §11 gives the rounds.

## 7. For the director

1. **3a's reference is `rrzero`,** not f (§4). The alternative, f, would fold the δ = 0 chain's difference into every
   shift.
2. **4C's primary weighting is the constraint weight,** with the unweighted values beside it. The weighted form is
   F0's row-5 estimator.
3. **4C's matrices are C_total + C_resp without V_g, and C_e.** V_g describes the predictions, and these truths are
   fixed. Another pair can be added before binding.
4. **4C writes no p value and no tail fraction,** only means and percentiles beside χ²_ndf's, as the 3D binding ruled.
5. **4C's width ratio is an addition** beyond the addendum's "χ² spread". It is the per-cell analogue of the χ² spread,
   and can be dropped.
6. **5A's primary weighting is the central value, not the prior** that the addendum's scoping named (§5.2). The central
   value is the pooled result whose content the projection averages over; 2D's construction used x = E_U, the data.
   The prior is written beside it. If the director prefers the prior as primary, only the labels change.
   - **When the choice was made:** while writing the tool, before any 5A output existed. The tool has run only on
     synthetic fixtures. No real 5A quantity (g_X,R, C_PL,16 or u_R) has been computed or seen by this session.
   - **What of the real inputs was read before the choice:** the 2D term's `cells` list and the committed fine map,
     to measure which footprint bins fall outside the support (§0, 5A; binning only, no values); and the e_X means and
     their spread over cells (0.5334, 0.2945, 0.1721, spread 0), printed by the input re-measure
     (`fd/receipts-ct/preserve/decl1.out`). These are inputs of the 2D term already in its committed readout, not 5A
     results. No central-value or prior fine-cell content was read.
7. **5A's support rule:** renormalize over the 205 supported 2D cells and write u_R; label a cell extrapolated above
   u_R = 0.10. R08–R11 lose 17 of 36 2D bins to the support. Their u_R depends on how much of their content sits in
   those bins, which the run measures. The threshold is set here, before any value is read.
8. **Each readout is printed beside the reported matrix, not in it** (addendum §5.4). None is a component.
9. **5A writes u_R for the prior only** (review M2). For the central value it is 1 − X_sup/f, of the X/f − 1 form for a
   partial data integral, and it carries the result's within-cell shape. The extrapolated labels, derived from it with
   the threshold fixed here, are written; the number is not. If the director rules it may be written, one line changes.
10. **3a's in-span fraction is unit-dependent** (review M5). It is written in relative units, with rank/16 beside it.

## 8. Pinned bytes

At this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_ct_readers.py` | `cccc47aaff9b7c7f3b211d0d40d363cdceee3750f99dd451909ffa4c8db7e39c` |
| `nd-unfolding/tests/test_fd_ct_readers.py` | `c68d412a069e863f7744cad4abf58c5ad53b84cce2cc47046f730f3a79fa48f2` |
| `nd-unfolding/fd_f0_regrade.py` | `0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2` |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` |

Only the first two files are new. The other four are unchanged from `main`.

## 9. Ledger, storage and stops

**Ledger:** in `fd/LEDGER.tsv`, one row for the deploy and tests and one per reader. All are 0 node-h, on a login
node, with no Slurm job.

**Storage:** `$B` on pscratch joins the retention list. Nothing goes to CFS. The readouts are committed. The inputs are
already preserved (`FD-CT-RETENTION.md`, `FD-CT-PRESERVE-REPORT.md`): A7's on HPSS and CFS, the 2D term on CFS, W2b's on
CFS and HPSS, S1's assembly on HPSS. `cresp.npz` and the central value are on pscratch, on the retention list.

**Stops:** §0's stop rule applies. No step is rerun or repaired without the director.

## 10. Not changed

- Every covariance, cell, readout and κ, and the reported matrix C_total + C_resp.
- `docs/analysis-note/**`.
- 3b and 5B, which have their own declarations.

## 11. Review dispositions

**Mutation round 1** (`fd/receipts-ct/declaration/mutants-round1.log`, on the tool at `a71ec191…`): 43 of 44 killed.
The survivor, "C0 product digest unchecked", is covered by `test_refuses_a_product_changed_after_its_manifest`.

**Independent read-only review** of `0cdb2cb4`, by a Claude Opus 5.5 subagent on the claude-school account, in its own
detached worktree, which it left clean. Its report is kept verbatim as `fd/receipts-ct/declaration/review/REVIEW.txt`
(`0c89848c…`), with its probes, its 31 mutants and their logs. It found no defect in the pins, in 5A's g, k and e
construction, or in `chi2_quantile`. Its findings, and what was done:

<!-- absence-ok: quotes the review's finding at 0cdb2cb4, measured by its mutants (review/review_mutants.log: 28 of 31 survived); the dispositions below record what changed -->
- **H1. Most refusals, several written numbers and every guard table were untested;** 28 of its 31 mutants survived.
  **Done.**
  - Every refusal now has a test that makes it fire on a one-entry defect (§3).
  - The end-to-end tests now recompute every number it named: the curvature, both |d|/σ, the C_total quadratic form
    and σ, the absolute half-span summary, the weighted distribution about b̃, the written B_eff, and the width-ratio
    summary.
  - Each reader has a planted-integral leak test, run in O(1) units, so that only the guard's table, not its 10⁻³⁰
    floor, can refuse it.
  - Its 28 surviving mutants are in round 2, rewritten where the code changed.
- **M1. 5A's S_ref was projected by another rule than g.** **Done:** S-ref's b_X is formed on the 2D cells and projected
  linearly (§0, §4).
- **M2. The central u_R is the X/f − 1 form of a partial data integral.** **Done:** it is written for the prior only,
  with the central's extrapolated labels; the partial integrals enter the guard's table (§3, §7 item 9).
- **M3. The weighting departs from the addendum, and this declaration was not yet on a branch.** The reason and its
  timing are §7 item 6. This file is committed with the tool.
- **M4. C4 and P4 cannot fire on any input.** **Done:** both are written as assertions, not controls (§3).
- **M5. The in-span fraction had no reference.** **Done:** rank/16 is written beside it, and its units are stated (§0,
  §7 item 10).
- **L1.** The two percentile definitions now match: both use the inverted ECDF.
- **L2.** The curvature is now `build_cresp`'s G3 form.
- **L3.** A key-allowlist test fails on any key outside the 4C schema (§5).
- **L4.** The 2D grid edges are pinned and checked against the committed `common.py`; negative footprint weights are
  counted and written; C1's repeated seed has a test.
- **L5.** The shared NOT CITABLE FOR now reads "a coverage or calibration result, or that any chi2 follows or departs
  from chi2_ndf", which no longer disowns the readout's own percentiles.
- **L6.** GiBUU's eight cells are read from the definition and checked against F0's constant (C1).

**Mutation round 2** (`mutants-round2.log`, on `cccc47aa…`, 78 mutants including the review's): 75 of 78 killed. The
three survivors were the 3a and 4C "guard table empty" mutants and C1's GiBUU check. The planted-leak tests had run at
the fixture's 10⁻³⁹ scale, where the guard's floor refuses any absolute value. Both now run in O(1) units, and a test
changes F0's GiBUU constant.

**Mutation round 3** (`mutants.log`, on `cccc47aa…` with the test file `c68d412a…`): **78 of 78 killed**, none
unapplied, and the tool restored and checked equal to `cccc47aa…` after every mutant and at the end.

**A note on round 3's first start.** It was stopped after one mutant to add the grid test. The stop interrupted the
script before its restore, leaving the first mutant ("S1 pin unchecked") in the tool. That one change was reversed by
hand and the tool's sha256 checked equal to `cccc47aa…` before the tool and tests were committed and round 3 was
restarted.

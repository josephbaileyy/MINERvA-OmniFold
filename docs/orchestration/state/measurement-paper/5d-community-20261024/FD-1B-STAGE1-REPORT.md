# 1B with 4A, stage 1 report: the toy mode, the scorer, their tests and the derivation (2026-10-30)

**By** the measurement session `coverage-5b`, under [`FD-1B-BINDING.md`](FD-1B-BINDING.md) (PR #556), which binds
[`FD-1B-DECLARATION.md`](FD-1B-DECLARATION.md) (sha256 `07d0e0b6b722c7de…`), for the director.

**AUTHORIZED, and all that was done:** stage 1, the declaration's §8. Code, tests, a mutation receipt and the
derivation, written and run on this Mac at **0 node-h**. No Slurm job ran or was queued. The only cluster reads were
`du` and `ls` of the bank, the detector dump and the inputs npz, and `squeue` (login37, 2026-10-30T23:10:22Z:
`fd/receipts-1b/stage1/cluster-reads-2.out`). No toy output exists, and no data result was read.

**MEASURES:** that the code does what §2–§5 declare, on synthetic fixtures. **CANNOT AUTHORIZE:** any job, a change to
the protocol, or any coverage statement. §4 is **DERIVATION**, not a result: algebra and fixture tests about the
toys' draws, with nothing measured on the real inputs.
<!-- absence-ok: scopes this stage's own work, which ran no job and read no product; the cluster reads are listed above -->

**The matrix under test** is unchanged and is named in every readout the scorer writes: the reported C_total + C_resp
of `fd_data_product.json` (`b79556f0…`), as on `main` at `91a27ad1`, with no run-period block. The 5B audit has passed
(#555), and its block is to be added by a separate declared step. 1B stays on this matrix, as the director ruled.

## 1. What was built

| file | what | §8 item |
|---|---|---|
| `nd-unfolding/fd_1b_toys.py` | the toy mode: arms, modes (`toy`, `half`, `derivation`), the draws, the pins, the product | 1 |
| `nd-unfolding/fd_1b_score.py` | the scorer (§4, §5), 4A, gate D, the reproduction check and the half-MC pairs | 2, 3 |
| `nd-unfolding/fd_1b_tasks.py` | the step and lane tables and the submit lines of jobs 2a–3f, with their refusals | 4 (the submit line) |
| `nd-unfolding/tests/test_fd_1b.py` | 54 tests, in both directions (§2) | 4 |
| `fd/receipts-1b/stage1/mutation_fd_1b.py`, `mutation.out` | the mutation receipt (§3) | 4 |

**Imported, not copied:**
- **The draws** are composed from `s5p_nullexp`'s `checked_ratio`, `ModelCache`, `truth_preserving`, `model_bands`
  and `model_groups`. A test holds the composition equal, bitwise, to `s5p_nullexp.source_factors` for a full draw.
- **The pseudo-data** use `s5n_pseudo.build_data`'s experiment, `fid_mask`, `true_xsec` and `bootstrap_replica`'s
  streams.
- **The half-MC mode** is `s5n_pseudo.build_pseudo`.
- **The unfold** is `s5n_pseudo.unfold_negweight`, F1c's path, under `s5e_candidate.install("R")`.
- **S1's estimators** are `s1_assemble`'s: `mat_cov`, `flux_weights`, `fine_map`, `functional_matrix`, `x01_scale`,
  `check_meta` and `group_of`.
- **The pooled statistics, the toy bootstrap, the windows, the two-sided verdict and the positive control** are
  VL169's committed `2d-unfolding/uq/coverage_fixed_truth/score_coverage.py`, called with this study's seed 20261030.

`s5p_nullexp.py`, `s5e_candidate.py`, `s1_assemble.py` and every other existing module are unchanged; `git diff
--stat origin/main` lists only the new files and the records rows.

## 2. Tests (54 pass; `python3 -m pytest nd-unfolding/tests/test_fd_1b.py`)

Each rule is tested where it should pass and where it should fail.

- **Constants against the declaration's own text.** The declaration's sha256 prefix is checked. Each of these is
  checked against the declared string as well as the code's value:
  - the windows C1 [0.631880, 0.728668] and C2 [0.928139, 0.972193];
  - the 4A windows [13.223, 19.753] and [0.0106, 0.1673];
  - χ²₁₆'s 95th percentile, 26.296;
  - the flag counts 182/300 and 276/300;
  - the SEs 0.0269 and 0.0120;
  - 20,000 resamples at seed 20261030, and the 99.5 % and 95 % levels;
  - the seed ranges of all three arms and the pilot;
  - the data product's sha256.
- **Coverage, two-sided at the control:**
  - matched scatter gives PASS, with ×0.7 grading FAIL-undercoverage and ×1.3 FAIL-overcoverage;
  - scatter ×1.4 gives FAIL-undercoverage, and ×0.7 gives FAIL-overcoverage;
  - a failed positive control voids a PASS to INCONCLUSIVE;
  - the interim look returns CONTINUE unless it is a FAIL, at the control and at a test arm.
- **Coverage, one-sided at a test arm:**
  - matched scatter gives PASS, with the fixed meaning;
  - scatter ×1.4 gives FAIL;
  - an interval 2× too wide passes, but so does its ×0.7 control, so it reads INCONCLUSIVE;
  - the rule reads the interval's upper bound;
  - a cell with scatter ×1.8 is flagged on a pass;
  - the Wilson flags fall at exactly 182 and 276.
- **4A:**
  - a matched matrix gives PASS, scatter ×1.3 FAIL-undercoverage, and ×0.8 FAIL-overcoverage;
  - a singular matrix is refused (no ridge), and that refusal leaves the coverage verdict standing (4A gates nothing);
  - at a test arm, the mean-subtracted statistics carry no verdict (binding ruling 4), a 3σ bias leaves them inside
    the windows, and their value equals the hand formula with N/(N − 1).
- **The draws:**
  - w_u / Σw reproduces S1's weighted flux block exactly, and the uniform draw does not;
  - ½–½ and 2p2h's ⅓ reproduce the pair estimator exactly;
  - the draw records have the declared frequencies over 6,000 seeds;
  - independent band draws add to the sum of S1's blocks;
  - the draw is fixed by its seed;
  - `flux_probabilities` reads the constraint file's weights over their sum.
- **The world fixture** is a synthetic 5D world with every file a toy reads.
  - The interaction set is S1's 33 bands, equal to the scorer's own groups. Rvp1pi is dropped, and a missing universe
    refuses.
  - Flux ids must be 0–99.
  - The pins pass the recorded files, and refuse a wrong digest, a changed mtime or a missing file.
  - The truth ratio must carry the committed F1 digest.
  - A detector band comes from the dump only; the bank's GEANT copy is not a fallback.
  - g_f acts.
  - The expectation mode gives the mean, and the full-MC truth equals a hand extraction.
  - The truth does not move with the draw.
  - The streams equal set A's, and leave the pseudo-data counts unchanged.
  - Half mode applies the draw to half B and source C only.
- **F1c's line.**
  - Setup: F1c's own argv builder (`fd_f1_tasks.steps`) gives the line `f1_pe_genie_v3_g18_s806000`, which runs
    through `s5e_candidate.main`. Then 1B's `repro-g18` arm runs with `--no-draws`. The unfold in both is the same
    deterministic recorder.
  - Result: the two experiments are equal array for array, and the two products' `xsec_flat` and `xtrue_flat` are
    bitwise equal. `fd_1b_score.py repro` grades PASS on the pair and FAIL on a mismatched pair.
- **Toy runs:**
  - a control toy records the declared estimator, its draw and stream replica, and the full MC;
  - seeds outside the arm, `--no-draws` off the reproduction arms, the wrong mode, a wrong pins sha or a wrong input
    sha are refused with exit 4, and no product is written;
  - a derivation run is noise-free with one universe;
  - the toy mode's own products pass the scorer's read-back.
- **Read-back:**
  - a departing draw, a departing truth, a wrong arm, a wrong truth name or ratio digest, differing code, or a
    non-finite truth is INVALID;
  - a scorer under another numpy refuses (exit 4) rather than grading every toy INVALID;
  - a missing toy is INSUFFICIENT, and a partial product is INVALID;
  - the score readout names the matrix and the surrogate share, refuses to overwrite, and contains none of the f, x_T
    or toy values.
- **Gate D:**
  - toys that carry S1's blocks give ρ = 1 to 10⁻⁹ and PASS, with the noise-free unfold deliberately off the truth so
    that the carry by x_T is distinguished from a carry by x̂(CV);
  - S1 interaction blocks 4× the toys' give FAIL and the stop;
  - a missing product is INSUFFICIENT, and a mislabelled one or one with another truth is INVALID.
- **Tasks:**
  - unfolds, nodes, most per lane, limits and caps per job equal §7's table rows, and the caps total 49.5 (23.0 and
    26.5 by stage);
  - every declared toy and universe runs exactly once;
  - every step parses as a declared toy run;
  - every submit line is `-A m3246 -q regular -C cpu`, under 12 h, with no GPU option, through the committed packer.
    The packer itself carries `--exclusive`, `--no-requeue` and `--nodes=1`;
  - a 12 h limit, an off-declaration cap and a stage-ceiling breach are each refused on their own;
  - a deploy off `/pscratch/sd/j/josephrb` is refused.

**What the tests cannot reach:** LightGBM and ROOT do not run here, so every unfold is a recorder.
- The bitwise reproduction of F1c by the real estimator is stage 2a's reproduction runs, and a mismatch is a STOP
  (§6).
- That `unfold_negweight` is the production estimator rests on `s5p_numerics.py`'s documented bitwise equality with
  the s5n/s5e products when unjittered. The central value `data_b-_j-` was made by `s5p_numerics`.

## 3. The mutation receipt (`fd/receipts-1b/stage1/mutation.out`)

`mutation_fd_1b.py` follows the repository's pattern (`docs/orchestration/mutation_whose_row_clean_merge.py`).
- Each mutant lives in a throwaway tree outside the repository, made of real copies of every `nd-unfolding/*.py`. A
  symlinked module would put the unmutated directory first on `sys.path`.
- Each replacement must match exactly once, differ and compile.
- An unmutated control must pass first.

Run 1 had 40 mutants: 18 in the toy mode, 16 in the scorer and 6 in the submit line. The review's fixes (§6) added
7 more, for 47.

**Run 1** killed 36 and left 4 unkilled. All four were dispositioned:
- **M01** (flux drawn uniformly): a real gap. The frequency test passed `p` in directly and never read the constraint
  file. A test of `flux_probabilities` was added.
- **M10** (the full-MC truth at twice its weight): an equivalent mutant. `true_xsec` divides the reweighted truth by a
  completeness built from the same weights, so the factor cancels exactly. It was replaced by a mutant that is not
  equivalent: the truth taken over half the MC.
- **T02 and T06** (the 12 h limit check and the cap check removed): masked. Another refusal fired first in the
  existing tests. The tests were split so that each refusal is the only one that can fire.

**Run 2** (40 mutants, after those test changes): 40 of 40 killed.

**Run 3** (47 mutants, after the review's fixes) stopped at M14, as designed. The truth-ratio refactor had moved its
target line, so the replacement no longer matched. M14, S07 and S16 were re-targeted, and the harness now checks every
replacement before any mutant runs.

**Run 4** killed 46 of 47. **S22** (the finite-truth check removed) was masked: the fixture's NaN truth also tripped
the truth-agreement check, since NaN never equals itself. The fixture now gives every toy the same infinite truth,
which only the finite check can refuse.

**Run 5** (the committed `mutation.out`, 2026-10-30T23:42:24Z, Python 3.12.2, numpy 1.26.4): **47 of 47 killed**, with the unmutated control at 54 passed. The receipt's header records the sha256 of every file it
tested.

## 4. The derivation record (DERIVATION: algebra and fixture tests; nothing measured on the real inputs)
<!-- absence-ok: a label scoping this section to this stage's own derivation, which ran no job -->

For each block of the declaration's §3: whether the toys' draw reproduces S1's estimator, and how that is known.

| block | the toy's draw | the spread it produces, against S1's estimator | how known | what it leaves to gate D |
|---|---|---|---|---|
| flux | u with probability w_u / Σw | the covariance of X_u under that law is Σ_u p_u (X_u − μ_w)(X_u − μ_w)ᵀ, μ_w the weighted mean: `mat_cov(X, w)` exactly, since S1 normalises by Σw | algebra; `test_flux_probability_reproduces_s1s_weighted_block_exactly` | whether the toy's shift X_u equals S1's. S1 reweights the whole MC and divides by universe u's own flux; the toy reweights the source's reco weights and divides by the CV flux. To first order the shifts are equal in size and opposite in sign, so the covariance agrees **(inference)** |
| interaction, 32 pairs | each pair at either endpoint with probability ½ | ½ Σ (X_i − X̄)(X_i − X̄)ᵀ = ¼ ΔΔᵀ = `mat_cov` over the pair, exactly | algebra; `test_endpoint_and_2p2h_draws_reproduce_the_pair_estimator_exactly` | **the prior-part gap:** S1's band moves prior and response; the toy keeps the truth in every fine cell (g_f), so only the response moves (declaration §3) |
| interaction, 2p2h | one of 3 universes uniformly | `mat_cov` over 3 (1/N), exactly | the same test | the same gap |
| detector, 4 bands | either endpoint with probability ½, from the dump only | ¼ ΔΔᵀ per band, exactly | algebra; the same test; `test_a_detector_band_comes_from_the_dump_only` | S1's detector universes also carry their own `denom_nd`; the toy keeps the truth, so the efficiency's part enters only through the response |
| all bands together | independent per band | the sum of the blocks under linearity | `test_independent_band_draws_add_to_the_sum_of_s1s_blocks` (diagonals within 10 % over 6,000 draws) | the non-linear remainder, which the control itself tests |
| lateral | s_b = ±1 with probability ½, x̂ += Σ_b s_b Δ_b^T / 2 | Σ_b ¼ Δ_b^T Δ_b^Tᵀ, the transferred S1 block, exactly over the 32 sign patterns | algebra; `test_the_surrogates_are_carried_to_the_truth` | nothing: carried, not tested (29.0 % of C_e's trace together with normalization) |
| normalization | x̂ × (1 + 0.014 z), z ~ N(0, 1) | 0.014² x̂ x̂ᵀ, equal to the transferred (0.014 f)(0.014 f)ᵀ at x̂ = x_T, and second-order away from it | algebra | nothing: carried, not tested |
| stat | Poisson pseudo-data at the truth, plus set A's MC Poisson(1) and template Poisson(1) streams | set A's three streams, except that the data stream is the pseudo-data's own Poisson draw rather than a bootstrap of observed events, and the toys are float32 unjittered where set A is float64 jittered (its numerical component is absorbed there and not drawn here) | construction; `test_the_streams_are_set_as_and_leave_the_observed_counts` | gate D takes stat from M_d. The block is 0.1 % of C_total's trace |
| seed | not drawn (estimator seed 42) | S1 measured it as exactly 0 | S1-REPORT §7 | — |

**Gate D, as implemented.** The 176 noise-free runs give x̂(u) and x̂(CV) at the nominal truth, in the toy's space.
- Each band's E block is S1's own estimator on those runs, carried to f by diag(f / x_T), with x_T the runs' common
  stored truth. That is how the control's intervals are carried (σ_c^T = √M_cc / f_c · x_T,c), so ρ_c predicts the
  control's spread-to-interval ratio. The first version used x̂(CV), which is off by the noise-free unfold's bias
  (review finding 1).
- E_d = E_flux + E_interaction + E_detector + M_stat + M_lateral + M_norm, and ρ_c = √(E_d,cc / M_d,cc).
- Per-group σ ratios are printed beside it.
- The fixture tests show ρ = 1 to 10⁻⁹ when the toys' shifts carry S1's blocks, and ρ < 0.9 when S1's interaction
  blocks are 4× the toys'. The second fixture is the prior-part gap's signature.

### 4.1 The same code on the real inputs (DERIVATION)

`fd/receipts-1b/stage1/derivation_check.py` (sha256 `ec3a31a3…`) ran on login37 at 2026-10-31T10:52:40Z, at 0 node-h,
from a clean clone of this PR's head (`633e6ba6`, in `$P/fd-1b-20261030/stage1-derivation/`), under the compute
environment (`root_6_28`: Python 3.11.14, numpy 1.26.4, the numpy the tests ran under). It read only what §8 permits
in stage 1: S1's assembly npz, the 10 lateral unfolds, the committed records, and the bank's and constraint file's
listings and weights. It prints no cross-section value. Output: `derivation-check.out`, rc 0.

| check | result |
|---|---|
| S1's npz digest and block set | `db000707…`, 46 blocks; the seed block is exactly 0; M_d = C_e − seed to 9 × 10⁻¹⁹ relative |
| the surrogates' share of C_e's trace | **0.2899**, the 29.0 % every report states |
| Δ_b from the lateral unfolds, X01 applied | all 5 lateral blocks reproduced as ¼ ΔΔᵀ at rtol 10⁻¹⁰ |
| M_d and the reported matrix, relative form | both positive definite; condition numbers 2,897 and 2,737 |
| the real bank | exactly S1's 33 interaction bands (Rvp1pi dropped), groups equal to the scorer's; Flux universes 0–99 |
| the flux probabilities | sum 1; n_eff 19.06, S1's recorded value; largest 0.128 |
| the test truths | both bridged ratios carry the committed F1 prep digests |
| the expected over-coverage, context only | C1 mean 0.791, minimum 0.701; C2 mean 0.983; σ_reported / σ_drawn 1.04–1.85 per cell. This reproduces `LIMITATION-PLAN.md:198-200` independently |

## 5. Choices the code makes that the stage-2 declaration must state, for the director

1. **The laterals' transfer.** The binding writes the surrogate as x̂ += Σ_b s_b Δ_b / 2. The code adds Δ_b^T = Δ_b ⊙
   x_T / f, carried to the truth as §2 carries M_d, so the toys' lateral spread equals M_d^T's lateral block. Taken
   literally, untransferred Δ_b would differ from M_d^T's lateral block by x_T / f per cell, and that would bias the
   control by construction. **Confirmed by the director** (cross-session message, 2026-10-31): the binding's form "was
   shorthand, and the carried form is what makes the control unbiased". The stage-2 declaration records it as the
   binding's intended reading.
2. **The order of the two surrogates.** The normalization factor multiplies after the lateral shift is added. The
   difference from the other order is second-order.
3. **The pilot runs at the nominal truth,** as the control does. Its 8 half-MC toys use the same seeds and the same
   draws, with half B and source C as the pseudo-data source and no streams: A7's, F0's and F1's mechanics.
4. **The unfold path is `unfold_negweight`,** F1c's, so that the reproduction runs test the toys' own path. It is not
   `s5p_numerics.unfold_one`, A7's and set A's.
5. **The derivation runs' wall is unmeasured.** They run in expectation mode with all of the MC, so their observed
   sample is every reco-passing MC row, not a data-size draw. A7's half-MC expectation runs took about 400 s
   (`state/s5p/prod-draft/ADMISSION-DRAFT-amendment-7.json:38`). Job 2a priced them at the toy's 832 s. The stage-2
   declaration should order them so the pilot's walls and theirs are both measured, and apply §6's re-price rule to
   them. The only timing hit of this search is the A7 line cited:
   Search: git grep -i -E "expectation (construction|mode|pseudo)" docs/orchestration/state, for seconds or walls @ c5460a35
6. **The pins step** hashes every weight file a toy can read: the bank's CV and 668 universe files, most of its
   71.6 GB, and the dump's 32 files, 2.1 GB (`cluster-reads-2.out`). They are checked against the sf1 manifest and
   the dump's receipt, once, before job 2a. Each toy then re-checks size and mtime. That is login-node I/O of minutes, or a step of job 2a. The stage-2 declaration fixes
   which.
7. **4A at the test arms carries no verdict.** The declaration's §4.2 grades the mean-subtracted χ² at a test arm;
   the binding's ruling 4 says 4A "is graded at the control only". The code follows the binding and prints the test
   arms' statistics and intervals with no verdict. **The stage-2 declaration records that the binding governs.**
8. **The scorer's environment.** The scorer re-derives each draw from its seed with numpy's `Generator`, whose
   streams numpy does not promise across versions. Each toy records its numpy version, and the scorer refuses
   (exit 4) under another. The stage-2 declaration pins the scorer to the toys' environment.
9. **Validity.** A look needs its whole declared toy set. A missing toy reads INSUFFICIENT, which at the control is a
   STOP unless the same-seed rerun of §5.1 supplies it.

## 6. Review

§8 item 6 asks for an independent read-only review of the code and of the stage-2 declaration. The code's review ran
before this PR, so a defect is fixed before the code is pinned. Its findings and their dispositions are below. The
stage-2 declaration's review runs on that PR.

The reviewer was a separate read-only Claude agent in this session's account (claude-school). It had the code, the
declaration and the binding, and not this report's reasoning. It found no blocker. Its findings and their dispositions:

| # | finding | disposition |
|---|---|---|
| 1 | gate D carried the toys' blocks to f by x̂(CV), not by x_T, so ρ_c was off by the noise-free unfold's bias; the fixture could not see it, since it set the two equal | **fixed:** carried by the stored truth, which must agree across the 176 runs; the fixture now separates them; mutant S17 |
| 2 | a 4A refusal (a matrix that is not positive definite) overwrote the coverage verdict with INVALID, against "4A gates nothing" | **fixed:** 4A refuses its own block only; a test runs the control's final look with a singular matrix; mutant S18 |
| 3 | the declaration grades 4A at the test arms; the binding says "graded at the control only" | **fixed to the binding:** no verdict at the test arms (§5 item 7, for the stage-2 declaration to record); mutant S19 |
| 4 | the scorer checked only that the toys' truths agree with each other: not the truth's name or digest, the code digests, or that the truth is finite | **fixed:** all four checked; mutants S21, S22 |
| 5 | re-deriving draws under another numpy would read every toy INVALID | **fixed:** the numpy version is recorded and a mismatch refuses (exit 4); mutant S20; §5 item 8 |
| 6 | some failures (a bad weight ratio, a missing file, a corrupt product) escaped as tracebacks instead of exit 4 | **fixed:** caught as refusals in both entry points. Nothing had been accepted silently |
| 7 | test gaps: the toy's groups against the scorer's, a test arm's interim look, a real toy product through the read-back | **fixed:** three tests |
| 8 | the deploy path was not required to be on pscratch | **fixed:** `check_deploy`; mutant T07 |

**A pre-existing failure, outside this lane.** `tests/test_fd_f1.py::Tasks::test_the_seeds_appear_in_no_committed_task_table`
fails on this branch, and its only hit is a file `main` already holds, so it fails there too **(inference)**: F1c's own committed step table, `fd/receipts-f1/run/f1c/f1c-steps.tsv`
(commit `741ad029`). It is a pre-run guard that F1c's committed tables now trip. No 1B file is a hit; it is reported,
not repaired.

## 7. Not changed

- The reported covariance, κ, every claim and number, and the data product.
- `s5p_nullexp.py`, `s5e_candidate.py`, `s1_assemble.py`, VL169's scorer and every module s5p's records depend on.
- Nothing is submitted, deposited or tagged. The paper's statement that coverage was not validated stands.
  <!-- absence-ok: a reference to the decision record's own wording, quoted at DECISION-20261024-joseph-5d-community-standard-route.md:46-47; it claims no search -->

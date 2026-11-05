# COV2D amendment: answers to the rolling audit (parts 1–4), the final delta audit and the director's F3

**By** the `cov2d` session, 2026-11-04. The audit is by the `coverage-5b-audit` session; each part is copied verbatim
in `AUDIT-PART{1,2,3,4}-*.md` (this directory), and the final delta audit in `AUDIT-DELTA.md`. The director ruled: fix every finding as stated, J1 first. These answers
are not evidence: each fix's evidence is its commit, its tests and its mutant in `mutation_amendment.{py,txt}`.

**Commits:**
- `9731d0c8`: J1–J7 and P1–P4.
- `0d43c9a3`: S1–S4, R1–R8, the norm-check survivor, the real-path null test, and the new mutants.
- `fd8d68bb`: the final delta audit's F1 and F2 (merged in #773 at `e9cadf47`).
- `3d6cae57`: the director's F3, the submit script's binding check.

The mutation receipt has **63 mutants, 63 killed** at `3d6cae57` (`mutation_amendment.txt`). Earlier it had 60, all
killed at `fd8d68bb`, and before the final delta audit 51, all killed at `0d43c9a3` (both in that file's history); the first run of the 51 is `mutation_amendment.run1.txt`. The run of 2026-11-04,
before these fixes, had 29 mutants with 28 killed; the survivor was "norm check removed" (see Blocks below).

## Part 1: the null and the scorer

<!-- absence-ok: "untested" restates the auditor's finding, shown by mutants that survived in its own run (AUDIT-PART1/2); each row names the test that now kills them -->
| finding | fix | test | mutant |
|---|---|---|---|
| S1: any toy count graded | `score` refuses unless `E.shape[0] == len(TOY_SEEDS[truth])` (300) | `test_refuses_any_toy_count_but_the_declared_300` (299, 150) | "S1 any toy count graded" |
| S2: outlier skipped silently | `score` refuses if `OUTLIER_CELL` ∉ cells; the outlier is then always read | `test_refuses_cells_without_the_outlier` | "S2 outlier absence not refused" |
| S3: outlier values, weakened share untested | — | `test_the_outlier_cells_values_are_read_at_its_own_position` (outlier column ×3, so it flags and differs from cell 0); `test_weakened_share_counts_every_weakened_cell_when_they_flag` (all seven flag; share stays 7/205) | "S3 outlier read at position 0", "S3 weakened share over the unflagged" |
| S4: sigma from the caller | `errors` takes C_T, sets σ_c = √diag C_T and refuses a shape mismatch | `test_errors_apply_the_surrogates_per_toy` checks max and median of the cross term against √diag C_T by hand, and the refusal | "S4 cross term over diag C_T" |
| S5: equivalent survivors | no change: both noted as equivalent | — | — |
| Q1: worth a real-path test | added, in the PyROOT env | `test_cov2d_blocks.NullOnTheRealPath`: `assemble` → `re2c_rollup.universe_block` → `build_repair.wcov` → `null_at_T`, check_matched ≤ 1e-12 for C_T and C_T⁻ in four regimes (unit; physical 1e-39 spanning three decades; lognormal Flux weights σ 2; a 30% common offset) | — |

## Part 2: the readouts

<!-- absence-ok: "untested" restates the auditor's finding, shown by mutants that survived in its own run (AUDIT-PART1/2); each row names the test that now kills them -->
| finding | fix | test | mutant |
|---|---|---|---|
| R1: cross-terms test pins nothing | the CLI also saves F and P per draw (`<out>.npz`) | `test_runs_over_600_draws_and_matches_a_hand_first_order_histogram` now computes F (first order) and P (C2's product, r_T on signal rows only, the POT scale, both trees) by hand for G18's first draw and AR23's last, checks the draw's seed, recomputes median and max of \|z\| = \|P − F\|/√F from the npz, and asserts AR23's F ≠ G18's | "R1 z over F not sqrt F" |
| R2: not 1B's text | `leave_out_mec` uses 1B's three texts verbatim (fd_1b_mc.py:803–808), naming cells by flat index where 1B writes R⟨cc⟩. It lists every cell flagged under C_T⁻, as 1B does, so the earlier "newly flagged" set is gone with its mutant | `test_c_t_covers_and_c_t_minus_flags` (cells and "(and jointly)"), `test_c_t_minus_also_covers` ("covers without…"), `test_a_joint_flag_alone_is_a_shift_reading` (grade patched: no cell, joint flag), `test_no_reading_when_c_t_under_covers` ("printed; no reading…"). The tests spell 1B's text out literally rather than reading the module's constants | "R2 joint flag ignored", "R2 jointly suffix dropped", "R2 reading ignores C_T's verdict" |
| R2: the seed | C_T⁻'s null is built in `null_at_T` at `cov2d.NULL_SEED` (R3) | `test_cov2d_null.NullMinus`: both `null_contents` calls at 5,742,000, the second on C_T⁻ with C_model⁻ in its Gaussian | "C_T-'s null at 1B's seed", "C_T-'s null keeps C_model" |
| R3: C_T⁻'s null built beside E | `null_at_T` returns `null_minus` when the blocks carry C_T⁻, as 1B builds both nulls in its null step (fd_1b_mc.py:740); `leave_out_mec` takes it as input and builds no null | as above; the LeaveOutMEC tests take the null from `null_at_T` | as above |
| R4: four §6(ii) outputs untested | — (plus: the coherent offset is also reported over the toys with no missing cell, as the auditor suggested) | `test_clipping_residual_on_varying_inputs_against_a_hand_computation`: random S, N, m_seen, m_all, x_true and σ over 300 toys; 120 of the outlier's toys missing. Hand checks: per-cell medians over present toys only; the outlier's max and median (and max > median); a zero-filled median would differ by > 0.5 σ; the coherent offset vᵀC_T⁻¹v with v = R·x_true on a full-rank C_T (median, max); the complete-toy count and median | "R4 a missing R_c read as 0", "R4 outlier max is its median", "R4 complete toys ignored" |
| R5: row order trusted | `clipping_residual` refuses unless `cells_npz["seeds"][toy_index]` is `TOY_SEEDS[truth]` in order, and x_true is (toys × cells) | `test_refuses_rows_that_are_not_the_truths_toys_in_seed_order` (shifted, reversed, wrong truth) | "R5 seed order unchecked" |
| R6: outlier skipped | refuses if 216 ∉ rep; the outlier record also counts its missing toys | `test_refuses_cells_without_the_outlier` | "R6 outlier absence not refused" |
| R7: uncounted F ≤ 0 | records `excluded_pairs_F_le_0` and `cells_with_F_le_0_in_every_draw`; an all-empty cell's median is NaN without the all-NaN warning; the record states the unit | the R1 test checks the count from the npz | "R7 F <= 0 pairs not counted" |
| R8: --no-pins unrecorded | the cross-terms record, step A's `pseudo_a.json` and step B's record carry `pins_checked` | the R1 test asserts `pins_checked` is false under `--no-pins` | — |

## Part 3: the job scripts (fixed in `9731d0c8`)

| finding | fix |
|---|---|
| J1: no pilot or order in the route; gate blind to the pilot | `cov2d_jobs.order()` enforces COV2D-DECLARATION.md:40 and §10 steps 5–6 from PASS records committed on origin/main for the deploy's M: the G18 pseudo-data job first; the pilot after G18's pseudo-data PASS; AR23's pseudo-data job and every unfold job after the pilot readout's PASS; the universe jobs (the $UNI readers) after both pseudo-data PASSes; the rest after all eight universe jobs are submitted. `cov2d_submit.sh` fetches origin/main and calls it before the gate. The gate prices every cov2d job of the user (the pilot included) and refuses an unknown cov2d name instead of raising KeyError. Mutants: "J1 bulk without the pilot record", "J1 pilot without G18's pseudo PASS", "J1 the rest before the universe jobs". |
| J2: $UNI unchecked before step A | `cov2d_pseudo.sbatch` runs `cov2d_jobs.py uni-stat` before step A and stops on a mismatch |
| J3: sticky rc in the walls | each run's own rc goes in `walls.<lane>.tsv` |
| J4: E3 reset after step A | threads exported and `mkdir -p "$TMPDIR"` before step A |
| J5: stale tables | `cov2d_submit.sh` regenerates the tables at each submission and compares them with the deployed ones |
| J6: waves | stated in the amendment (§5), with the arithmetic below |
| J7: QOS/TimeLimit; unclosed files | the pseudo job checks its QOS and TimeLimit as the unfold jobs do; `check` closes its files |

**J6, the arithmetic.** From the committed tables (`cov2d_jobs.pack` and `pilot` at `9731d0c8`): the 24 unfold
limits sum to 172.27 node-h (8 × 08:54, 6 × 08:06, 6 × 07:38, 2 × 03:20); with the two pseudo-data jobs (03:00 each)
that is the auditor's 178.27, and with the pilot (01:41) **179.95**, above the 165.8 cap. The projected wall is
**144.95**. The order's steps 1–4 (both pseudo-data jobs, the pilot, the eight universe jobs) hold 78.88 node-h of
limits and the remaining 14 jobs 101.07, so some of the 14 wait while steps 1–4 are unfinished. A refusal there is a
wait, not a STOP. The gate requires (elapsed of ended attempts) + (limit of unfinished ones) + (the new limit) ≤ 165.8
at each submission. That sum only falls afterwards, as each limit is replaced by an elapsed time no larger, and every
attempt goes through the gate. So the final charge is at most 165.8, provided no job runs past its limit. The final
delta audit adds that Slurm enforces a limit only up to its kill grace; see "Final delta audit" below. The amendment
states this in §5.

## Part 4: the pilot (fixed in `9731d0c8`, except where noted)

| finding | fix |
|---|---|
| P1: §9.12's universe at 64 CPUs | P912_U_MaRES_0 moved to lane 1 at 128 CPUs, as part B's U_MaRES_0 (J2b.1). Lanes: 1 at 128 CPUs (P912_L, L_G18, P912_U), 2 at 64 (P2b, X, T), 3 at 64 (B, U_G18). Limit **01:41:00** (1.68 node-h), inside the 2.0 reserve and the 02:00:00 ruling. |
| P2: a failed run not INVALID | every one of the eight runs must have rc 0 and a digest, and every REPRICE class must have a wall, or the readout is INVALID (§9.13). `test_a_failed_run_of_any_class_is_invalid` runs one failed run per class. `test_a_class_without_a_measured_wall_is_invalid_even_when_every_run_passed` reaches the class check alone (added with the fixes below: the first 51-mutant run left "P2 a missing class is not INVALID" alive, because every failed-run case also trips the per-run check). Mutants: "P2 a failed run is not INVALID", "P2 a missing class is not INVALID". |
| P3: REPRICE unlike with like | part B's wall per run is now its run time: (elapsed − the declared 300 s preflight) × min(lanes, runs) / runs. The pilot's universe wall is P912_U at 128 CPUs against J2 at 128; U_G18_Flux_0 at 64 CPUs is a route test and is not priced (`NOT_MEASURED`). `PILOT_EST` was removed. The effective trigger is stated in the amendment (§5): the triggers, at 1.25 × part B's run-only wall per run, are 762.5 s for central and toy
(J1, 610.0 s), 1,081.1 s for universe (J2a–d at 128 CPUs, 864.9 s), 1,468.5 s for lateral (J3, 1,174.8 s) and 864.6 s
for replica (J4a–c, 691.7 s). Two differences remain, and both make the trigger slightly looser on pure run time:
J1's figure is the longest of its three one-per-lane runs, and part B's multi-run lanes include the gaps between srun
steps. Every trigger lies below the bulk's per-run estimate (866, 1,150, 1,678 and 920 s). |
| P4: staged rate probably cached | `dvs-rate` runs before `check`, so the staged 4 GiB is read before check's full re-hash; the record's `cache_note` says a page-cache hit left by another process on that node cannot be excluded, so the staged rate may be cached. The CFS figure is cold. |
| P5: cell sets of the references | run with the director's go (`connect-cells.sh` `89078399…`, M `045364a8`, login02, 0 node-h): **CELL-CHECK PASS**. ER, U_MaRES_0 and S3_BeamAngleX0, each read at its pin, all report E_R's 205 cells (`cell_check/CELL-CHECK.md`, commit `c184499a`). |
| P6 (= J1) | closed by `order()`: the bulk is refused without the committed pilot readout's PASS record. |
| P7: the pass rule retyped | the amendment states that `cov2d_pilot`'s rule (max relative difference ≤ `re2_k1.TOL` and the same cell set) is `re2_k1.check_row`'s `le` rule for hXSec2D. The pilot's own new products are read without O_NOATIME: they are lane outputs, not §7 inputs, and the amendment says so. |

## Blocks: the norm-check survivor

The 29-mutant run's one survivor, "norm check removed", is closed: `test_refuses_a_drifted_dict_layout` gains a case
whose `universe_block` returns the normalization entry off by one part in 10⁶, with the total re-summed to match, so
the key-set and sum checks pass and only the norm check can refuse.

## Final delta audit (`AUDIT-DELTA.md`; fixed in `fd8d68bb`)

The auditor's report, its follow-up and the director's ruling, which upheld F1 and F2, are copied verbatim in
`AUDIT-DELTA.md`.

<!-- absence-ok: "not measured" scopes this session's own work (Slurm's kill grace on Perlmutter was not read); it claims nothing about whether a value exists -->
| finding | fix | tests | mutants |
|---|---|---|---|
| F1: `order()` requires "M", which no writer emitted | `cov2d.deploy_head(root)`: the checkout's `git rev-parse HEAD`, refused (`Refusal`) if `git status --porcelain` is not empty. Step B records it as `"M"` before its output directory exists, and stops if the HEAD differs at write time. The pilot readout records it before it reads anything. Each writer reads its own checkout (`DEPLOY`, the repository holding the code), which in a job is the deploy at M. | `test_the_writers_record_is_what_order_admits` (step B) and `test_the_readouts_record_is_what_order_admits` (the pilot): each calls the real writer, on a clean one-commit checkout (`tests/deploy_fixture.py`) standing in for the deploy, and checks three things. `order()` admits the record; it refuses the same record with M deleted; and it refuses the record with M set to another sha. Also `test_a_dirty_deploy_is_refused_before_any_output`, `test_a_dirty_deploy_is_refused` (the readout), `test_a_deploy_that_moves_during_step_b_stops` and `test_deploy_head_is_the_clean_checkouts_head` (an untracked file and an edited file are each refused). `test_cov2d_jobs.Order`'s hand-written records now carry M = "sequence-test-not-a-commit", and its docstring limits them to the sequence. They cannot stand in for the writer tests, because the mutants that drop M from a writer run only that writer's suite. | "F1 the pseudo record without M", "F1 the pilot record without M", "F1 a dirty deploy admitted", "F1 a deploy moving during step B unchecked", "F1 order ignores M" |
| F2: a pilot needing REPRICE still opened the bulk | `order()` admits AR23's pseudo-data job and every unfold only on the pilot's PASS with `reprice_classes == []`. A list naming a class, or no list at all, is refused with the classes named. §8 makes REPRICE an amendment. | `test_a_pass_that_needs_repricing_does_not_open_the_bulk` (the readout's own PASS record with REPRICE `['lateral']` is refused); `test_the_readouts_record_is_what_order_admits` (with no REPRICE class it is admitted); `test_a_pilot_needing_repricing_opens_nothing_after_it` (`["universe"]` or no list, for AR23's pseudo-data job, a universe job and a later job) | "F2 bulk despite REPRICE", "F2 no REPRICE list read as none" |
| The KillWait caveat (question 4) | §5 now says the gate's bound holds only up to Slurm's kill grace. An overrun by a job that has already ended is in the elapsed sum the gate reads. Only jobs unfinished at the last submission can pass the cap, each by at most the grace: for example, 22 bulk jobs at 60 s come to 0.37 node-h. The grace was not measured. | — | — |
| The two coherent-offset mutants | the auditor's follow-up reports both killed by `test_clipping_residual_on_varying_inputs_against_a_hand_computation`. Both are now in this directory's harness too. | `test_clipping_residual_on_varying_inputs_against_a_hand_computation` | "R4 coherent offset on the identity", "R4 coherent offset without x_true" |

**Required mutants.** The harness now has a `REQUIRED` set: the two F2 mutants and four of the F1 mutants. It exits 1 if
any mutant survives or fails to match its text, and names any required mutant that was not killed. **Run:**
60 mutants, **60 killed**, harness exit 0, every required mutant killed (`mutation_amendment.txt`). **Suites:** at `fd8d68bb`, **147 tests, 0 skipped, all pass** (`suites_fd8d68bb.txt`; a local run in the one environment of the amendment's §8).

## The director's F3: the submit script's binding check (fixed in `3d6cae57`)

The director found F3 while drafting binding 2. It is copied verbatim at the end of `AUDIT-DELTA.md`.

**The defect.** The audited `cov2d_submit.sh` (blob `03ad296e`) required the deploy's HEAD to equal M, then grepped
the deploy's own `COV2D-BINDING-2.md` for M. A commit cannot hold a file naming its own hash, so that check refused
every submission. No test reached it.

**The fix.** After the clean-deploy check, the script runs `git -C "$C" fetch -q origin main` and refuses if it fails.
It reads the binding with `git -C "$C" show origin/main:<path>` and refuses if the file is absent there. It requires the
text to contain M (`grep -qF`, the full 40-hex HEAD). The deploy stays at M. `cov2d_env.sh`'s header comment now says
"the commit binding 2 names".

**`order()`, the same shape.** It reads the PASS records with `git show origin/main:<path>`, and an absent or
unreadable record counts as None, which is refused. The script's single fetch now comes before both the binding check
and every `order()` call, with an explicit refusal. Before, a separate fetch ran after the tables, and `set -e` stopped
on a failure without a message. A failed fetch stops the submission before any record is read.

| test (`test_cov2d_jobs.SubmitBinding`) | what it shows |
|---|---|
| `test_admits_when_origin_mains_binding_names_M` | the deploy at M has no binding file; origin/main's names M; the script passes every check (it reaches the stubbed `cov2d_env.sh`) |
| `test_refuses_a_binding_naming_another_commit` | refused: "does not name" |
| `test_refuses_when_origin_main_has_no_binding` | refused: "binding 2 is not on origin/main" |
| `test_refuses_a_failed_fetch_even_with_a_good_binding_already_fetched` | the clone's origin/main already holds a good binding, and origin's URL then points nowhere: refused on the fetch |
| `test_refuses_a_dirty_deploy_or_a_head_other_than_M` | both refused, as before |
| `test_the_audited_script_refuses_even_the_correct_setup` | blob `03ad296e`, read from the repository's history, refuses the setup the fixed script admits. This shows the test reaches the defect |

The fixture is real-shaped: an "origin" repository whose main is the code commit M followed by a commit adding the
binding, and a deploy made by `git clone` and checked out at M.

**Mutants, all REQUIRED:** "F3 the deploy's own binding read", "F3 the binding's name check skipped", and "F3 a failed
fetch admitted". All three were killed when run alone. **Run:** 63 mutants, **63 killed**, harness exit 0, all nine required mutants killed (`mutation_amendment.txt`). **Suites:** at `3d6cae57`, **153 tests, 0 skipped, all pass** (`suites_3d6cae57.txt`; a local run in the one environment of the amendment's §8).

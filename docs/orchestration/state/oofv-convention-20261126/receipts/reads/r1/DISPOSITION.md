# OOFVC r1: dispositions

The r1 reads were of commit 3a0489dc (inputs in `inputs.sha256`).
- **codex-school `gpt-6.2-sol`, high:** 10 BLOCKERs and 1 NONBLOCKER, NO-GO.
  - Attempt 1 read no file: the prompt's "Do not run anything" blocked its shell reads. It used 43,668 tokens.
  - Attempt 2, with "read-only shell commands" allowed, used 123,648 tokens.
- **agy `gemini-4-hydrogen-high`:** 1 BLOCKER and 5 NONBLOCKERs, NO-GO.

Every item below was fixed or answered in the commit that adds this file (declaration revision 4). Each fix's test or
mutant is named.

| # | reader | finding | disposition |
|---|---|---|---|
| c1, a1 | both | The dump skips the signal loop's truth-tree gate (C-SIGW could false-STOP), and dedupes after the selection | Fixed in part. The duplicate flag now follows the signal loop's order: first occurrence among all phase-space entries, before the selection. The gate is not re-evaluated. Stage B's P4 census measured nG1 = 0 and nSigLoopNoTruth = 0 on this omnifile's inputs, so it drops nothing, and if it did C-SIGW would STOP honestly. Stated in §2.2 C-SIGW |
| c2 | codex | The dump's write could miss its tree | Fixed. It writes through the output file (`out.cd()`, `WriteTObject` with return checks) and re-reads the tree's entry count (`oofvc_dump.cpp`) |
| c3 | codex | Closed rectangles against ROOT's half-open cells at upper edges | Fixed. Moved and appended sets use ROOT's cells (`oofvc_lib.in_bins`, the driver's append), and O's signal part keys on the binned reco cell. Tests: `Moved.test_moved_mask` (edges), `Driver.test_bad_rows_fail` (true p∥ = 60). Mutants: LIB_BINS_CLOSED, DRV_TRUTH_CLOSED |
| c4 | codex | The scorer trusted PASS strings, not digests or each unit's convention | Fixed. C-UNITS checks every unit's root and npz against its done-marker digests, its argv against its npz record, the convention and rows name, the unfolder, and N's controls. C-KS checks the K lists. Test: `Runner.test_scorer_controls_on_the_fixture_units`. Mutants: SCORE_DIGEST, SCORE_CONVENTION, SCORE_ROO_RAN |
| c5 | codex | C-NSUM added the driver's own moved part to both sides | Fixed. The direct side recomputes the moved part from the rows file. C-NMOVED compares the two cell by cell. Test: `Runner.test_r_units_carry_the_option`. Mutant: RUN_NMOVED |
| c6, a5 | both | C-PINS lacked libRooUnfold and expected digests | Fixed. Each unit process checks libRooUnfold.so against its pin and records it. The scorer requires every pin record equal to the expected driver, runner, lane, rows and library digests |
| c7, a5 | both | C-BASE ignored c2 zero cells, and C-FIX checked contents only and omitted the cm² flux integral | Fixed. Exact zeros are required; C-FIX compares contents, errors and edges, with `fluxIntegral_cm2_per_POT` added. Mutant: SCORE_FIX |
| c8, a3 | both | The append guard aborted on a truth weight the row does not use | Fixed. The loaders' own rules apply (1e4 for appended rows, 1e6 for rows reconstructed outside the grid), and a failing row is dropped and counted. C-MOVE uses the counts. Test: `Driver.test_weight_rules_drop_and_count`. Mutants: DRV_WEIGHT_ABORT, SCORE_MOVE_COUNT |
| c9 | codex | The tie bound refused zero ties, and a NaN in split.json could pass | Fixed. Zero tied weight passes; a non-finite C-LAB cell is a STOP. The join's STOP keeps the measured fields. Tests: `Join.test_tie_bound`, `JoinTool.test_nan_in_split_stops`. Mutants: LIB_TIE_ZERO, JOIN_LAB_FINITE |
| c10, a6 | both | Batch exit statuses, the playlist count, and squeue failures | Fixed. `units.sbatch` exits 6 if any unit failed. `dump_array.sbatch` exits 4 if finalizing fails. `dump-rest` requires 12 playlists in file-counts.txt. A failed squeue is a STOP in every script |
| a4 | agy | `--use-weights` not enforced under minerva | Fixed: refused without it. Test: `Driver.test_refusals`. Mutant: DRV_USE_WEIGHTS |
| c11 | codex | The formulas, the identity, the distance and the readings agree with the declaration | No change |

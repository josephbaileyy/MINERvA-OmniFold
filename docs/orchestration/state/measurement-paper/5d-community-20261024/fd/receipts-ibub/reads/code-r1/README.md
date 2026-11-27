# IBUB code, read 1: agy gemini-3.8-flash-high (2026-11-23)

**By** `director-helper-3`. This is the first agy read of `2d-unfolding/ibub/`. Its findings were taken as fixes in
the commit that adds this record.

**MEASURES:** one reader's findings on the code as copied. **CANNOT AUTHORIZE:** anything.

## A defect in this read's inputs, disclosed

The reader's copy of `ibub_unit.py` was not the code. I copied the inputs while `mutants.py` was running, and that
script edits files in place. The copy (sha256 `3dc94d53…`, in `inputs.sha256`) holds **mutant 1**, `bad = []` in
`g2r_check`.
- The real file at that time differed from the copy in that one line. The mutation runner's restore was verified by
  sha256 after every mutant.
- So the read's **finding 1, the BLOCKER (C-G2R a no-op), is a finding about the mutant, not about the code.** It is
  recorded here and not fixed, because there was nothing to fix.
- The read's other inputs (`ibub_readout.py`, `config.json`, both test files and `mutants.py`) equal the real files.
- Read 2 takes its inputs from a commit (`git archive`), so this cannot recur. The lesson is recorded for the lane.

## The findings and their dispositions

| # | label | finding | disposition |
|---|---|---|---|
| 1 | BLOCKER | C-G2R hardcoded to a no-op | **not applicable**: it was mutant 1 in the copy (above). The real line is `bad = sorted({a.split("=", 1)[0] for a in argv} & set(...))`, and mutants 1 and 2 are killed by the tests |
| 2 | MAJOR | `stage_data` leaves a partial copy if `copy_noatime` raises | fixed: any exception deletes the copy, then re-raises. Test `test_a_failed_data_copy_leaves_nothing_behind`; a mutant removing the deletion is killed |
| 3 | MAJOR | a unit with another K scan crashed the readout (KeyError) | fixed: it is missing (INCOMPLETE), with its problem named. Test updated; mutant added |
| 4 | MAJOR | products off their marker's digest raised an uncaught Refusal | fixed: they are missing (INCOMPLETE), with the problem named. Test `test_a_unit_whose_products_are_off_its_marker_is_incomplete_not_a_crash` |
| 5 | MAJOR | `config.json` lacked two of the code pins §9 declares | fixed: `s5c_unfold.py` and `compare_to_paper_fullcov.py` are pinned, and are equal to `ref_c2c1/config.json`'s pins |
| 6 | MINOR | the readout accepted an incomplete set of controls | fixed: each unit kind's declared set (`ibub_unit.CONTROLS`) is required, by the unit before it writes a marker and by the readout. Two tests; two mutants |
| 7 | MINOR | C-COMPLETE did not check the bound job or deploy | fixed: `--job` is required. Every unit's `slurm_job`, `runner_sha256` and `config_sha256` must equal the bound job and the readout's own checkout. Test; mutant |
| 8 | MINOR | no AR23 end-to-end test | fixed: `test_ar23_runs_end_to_end_at_its_own_paths_seed_and_cells` checks AR23-a2, bootstrap seed [5760000, 1] and two flagged cells |
| 9 | NOTE | some descriptive fields unasserted | fixed: assertions on `rms_rel_pct`, `median_abs_rel_pct`, `cells_ibu_smaller_abs_bias`, `unpaired_ratio` and the negative counts |

| file | sha256 |
|---|---|
| `prompt.txt` | `df883f7a1641569e5b5604821891964c64e2045b47df0855428149548d44ae3b` |
| `agy-gemini-3.8-flash-high.txt` | `084572ca9de26be200a5fb24a76c39b8cd24ff94009a6126d3ed3d748742dc51` |
| `rc.txt` | `bdb452ec7822ddca2df0eafa7b1fb13f73a6b73adc818f019e40070b984a57d0` |
| `inputs.sha256` | `0e4ab14c9966f130c4c6efd4f4851cfd792302d25c2aeef5b3e33f7a7a13e76c` |

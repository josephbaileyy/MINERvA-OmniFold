# PG tune support: agy read 1 and its dispositions

agy (Gemini 3.8 Flash (High), `--sandbox`) did a sandboxed, read-only read of copies of these files:
- `pg_generate.sh`, `pg_lib.py`, `README-pg.md`;
- `gen5d_v3.py`, `run_gevgen_v3.sh`, `setup_genie_v3.sh` and `fd_f1_prep.py`, with the diff of those four;
- `sbatch_fd_f1a.sh` and `sbatch_fd_f1b3.sh` for reference;
- `test_covfix_pg.py`, `mutants.py`, `LINE-TRACE.md`, and an excerpt of the declaration's §4.2.

Its input files' sha256 were unchanged after the read. The findings below are the PG session's restatements, not quotes. Each disposition is the PG session's.

| # | finding, restated | disposition |
|---|---|---|
| 1 | on a failed or timed-out task, the script exits before renaming gevgen's `genie-mcjob-<seed>.status`. A failed gntpc also leaves `gntp.<seed>.ghep.root`. Either way, seeds stay in file names under W | **Fixed.** Each task renames its own files when it ends, whatever its exit code. An EXIT trap renames them again on every exit, and TERM/INT route through it. A leftover GHEP is kept under the seed-free name `gntp.ghep.root`, not deleted |
| 2 | the failed-task test did not check file names | **Fixed.** `test_a_failed_task_stops_and_leaves_no_seed_in_a_name` and `test_a_missing_gst_stops_before_any_conversion` both check every name under W. `test_tasks_rename_their_own_files_if_the_script_is_killed` SIGKILLs the script mid-generation, so no trap runs and only the per-task layer can rename. That isolates the per-task layer |
| 3 | `PG-SHA256SUMS` left out the top-level products (flux file, spline checks, graphs) | **Fixed.** It now hashes everything under `W/out` except `logs/`, itself and any GHEP, as F1a's sums file does. The test checks one file from each place |
| 4 | the sums step's stderr reached the parent, which could leak W paths | **Fixed.** It goes to `W/out/logs/sums.log` |
| 5 | tune 0's conversion started before tune 1's gst count was checked | **Fixed.** Both counts are checked before any conversion starts, as in `sbatch_fd_f1b3.sh`. The missing-gst test checks that no hadd or convert ran |
| 6 | when one background step fails, its siblings keep running | **Fixed.** The EXIT trap stops this script's background jobs and their children. `test_a_stop_ends_the_other_background_steps` checks that the slow sibling never finishes |

agy found nothing in these categories: an output outside W, a seed-rule bug, or an F1 behaviour change.

After the changes, 22 tests pass (`tests-local.log`), 35 of 35 mutants are killed (`mutants.log`), and F1's `test_fd_f1.py` still passes 32 of 32.

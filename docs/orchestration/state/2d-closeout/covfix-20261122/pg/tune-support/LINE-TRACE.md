# PG tune support: line trace against the director's contract and COVFIX-DECLARATION.md §4.1–§4.2

By the PG session (tune-generator). The code is `3d-unfolding/genie/pg_generate.sh` (the one executable),
`pg_lib.py`, and the PG additions to `gen5d_v3.py`, `run_gevgen_v3.sh`, `setup_genie_v3.sh` and
`nd-unfolding/fd_f1_prep.py`. The tests are `nd-unfolding/tests/test_covfix_pg.py` (`tests-local.log`). The hand
mutants are in `mutants.py`, and `mutants.log` records 35 of 35 killed. References are to functions or literal lines.

| requirement (source) | code | test / mutant |
|---|---|---|
| F1's bound pipeline, unchanged except the tune names and the seeds (§4.2, "Who generates") | the same `run_gevgen_v3.sh reduce/graphs/genie`, `gen5d_v3.py make-flux/spline-check/flux-check/convert`, `hadd`, `fd_f1_prep.py` calls as `sbatch_fd_f1a.sh` and `sbatch_fd_f1b3.sh` | `Generate.test_end_to_end` (each call and its arguments, from the stubs' log) |
| F1b′'s layout: 7 tasks per tune, 160,000 events, 14 at once, one wave, `/usr/bin/time -v`, `timeout`, `\|\| exit 255` (director's contract; FD-F1-DECLARATION-AMENDMENT-2 §4) | `NT=7; NEV=160000; P=14; TO=5115`; the `xargs -P` line | `Consistency.test_layout_is_f1b_primes` (against `sbatch_fd_f1b3.sh`), `test_end_to_end` (14 tasks, 160000, `timeout 5115`); M11 |
| the tune support: `TUNES`, the spline pins, the reduce qualifier case, the setup qualifier case (director) | `gen5d_v3.TUNES`, `gen5d_v3.PG_SPLINE_PINS`, the `run_gevgen_v3.sh` and `setup_genie_v3.sh` cases | `Consistency.test_names`, `test_qualifier_cases` (against `pg-probe.py`'s `qualifier()`), `Gen5dV3Pins`; M24–M27 |
| `GENIE_XSEC_TUNE`: the product must set the tune asked for | `setup_genie_v3.sh`'s existing check, unchanged | the probe prints the product's UPS lines |
| the pins come from PG's probe | `PG_SPLINE_PINS` (empty until then; spline-check refuses an unpinned tune) | `Gen5dV3Pins.test_spline_check_refuses_an_unpinned_tune`, `Consistency.test_pg_pins_match_the_probe` (skipped until `pg-probe.out` exists); M26 |
| F1's records stay F1's | PG pins kept apart from `SPLINE_PINS`; `fd_f1_prep.py --truth-set f1` is the default and unchanged | `Consistency.test_f1_is_unchanged`; `test_fd_f1.py` 32 passed |
| the truths through the pv-ladder ratios and the bridge (§4.2; §3.4's r_u is the bridged ratio) | `fd_f1_prep.py --truth-set pg`, `PG_TRUTHS`, `PG_U0`, `PG_U1` | `PrepPG.*`; M19, M28–M30 |
| invocation `--workdir W --seeds W/seeds.json`, cwd W, `TMPDIR=W/tmp` (contract) | the argument and guard block at the top of `pg_generate.sh` | `Generate.test_refusals`; M12, M13 |
| seeds.json: 7 ints per tune, u0/u1 (contract); seed = base + 10,000 u + index, base in [1e9, 2e9), refuse ≥ 2³¹ − 1 (§4.2 "Range") | `pg_lib.load_seeds` | `Seeds.*`; M01–M07 |
| never prints a seed (contract) | refusals name the rule only; all sub-step output goes to files under W; work directories are `u<u>/t<k>`; gevgen's `genie-mcjob-<seed>.status` is renamed | `test_refusals_name_the_rule_not_the_seed`, `test_end_to_end` (no seed in stdout, stderr or any file name), `test_a_failed_task_stops`; M06, M09, M17, M22 |
| every output stays under W (contract) | outputs under `W/out` and `W/run`; `TMPDIR` re-exported after every activation (`setup_salloc_env.sh` resets it); `python3 -B` and `PYTHONDONTWRITEBYTECODE=1`; the deploy's `git status --ignored` compared after setup and at the end | `test_end_to_end` (the stubs see only `TMPDIR=W/tmp`; the deploy and its parent are unchanged), `test_a_write_into_the_deploy_stops`; M16, M18 |
| `W/PRODUCTS.json` lists the ratio files PV uses (contract) | `pg_lib.products` | `Seeds.test_products`, `test_end_to_end`, `test_fallback_tune`; M10 |
| exit 0 on success; any failure stops | `need` exits 1; `refuse` exits 2 | `test_a_failed_task_stops`, `test_flux_check_failure_stops`, `test_bad_seeds_stop_before_any_step`; M21, M23 |
| run only from the bound deploy | `PG_DEPLOY_PIN` = HEAD, no modified tracked file | `test_refusals`; M14 |
| no rerun into an earlier attempt's directory | refuses an existing `W/out`, `W/run` or `W/PRODUCTS.json` | `test_refusals`; M15 |
| the environment it needs is listed (contract) | `README-pg.md` | by inspection |

## Limits of these tests

- GENIE, ROOT, CVMFS and `setup_salloc_env.sh` are stubs. The real calls are F1's, and F1 ran them on Perlmutter. Nothing
  here shows that the new tunes' splines load or that the new qualifiers set up. The probe's catalog checks those
  products exist, and `setup_genie_v3.sh`'s own checks refuse at run time.
- macOS has no `timeout`, and its `/usr/bin/time` has no `-v`. The test substitutes both. On Perlmutter they are
  F1b′'s.
- The run is not priced or bound here. That is the director's.

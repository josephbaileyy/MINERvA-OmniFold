# PG tune support and slot-1 verification (A2): line trace

By the PG session (tune-generator). Its sources:
- `../PLAN-SLOT1-PROBE.md` (approved), with the director's rulings;
- COVFIX rev 12 §4.1, for the tunes, and §4.2, which lists the trace prefix since cov2d's 6cc2fad6;
- the director's contract for the one executable.

The code:
- `3d-unfolding/genie/pg_generate.sh`, the one executable;
- `pg_lib.py` and `pg_verify.py`;
- `pg_pins.json`;
- the PG additions to `gen5d_v3.py`, `run_gevgen_v3.sh`, `setup_genie_v3.sh` and `nd-unfolding/fd_f1_prep.py`.

The tests are `nd-unfolding/tests/test_covfix_pg.py` ("generate") and `test_pg_verify.py` ("verify"), with results
in `tests-local.log`. The mutants are in `mutants.py`, run with `../mutrun.py`'s kill rule, and their results are in
`mutants.log`.

| requirement (source) | code | tests |
|---|---|---|
| F1's bound pipeline, unchanged except the tune names, the seeds and slot 1's §4.2 changes (§4.2) | the same `run_gevgen_v3.sh` and `gen5d_v3.py` steps, `hadd` and `fd_f1_prep.py` calls as F1's | `Generate.test_end_to_end` |
| the tunes: u0 G21_11a_00_000, u1 G18_02a_00_000, with no fallback (rev 12) | `pg_lib.U0`, `U1`, `TRUTH`; `fd_f1_prep.PG_*`; `gen5d_v3.TUNES`; the setup and reduce cases | `Consistency.test_names`, `test_qualifier_cases`, `Seeds.test_valid`, `PrepPG.*` |
| the spline pins: the record's SciSoft digests, to be matched by the node's bytes | `gen5d_v3.PG_SPLINE_PINS` | `Consistency.test_pg_pins_are_the_records`, `Gen5dV3Pins` |
| slot 1 from the private product: `PRODUCTS` for setup, the private source for reduce and spline-check, and one path everywhere (SLOT1-PRIVATE-PRODUCT.md items 1–8) | `setup_genie_v3.sh`, `run_gevgen_v3.sh` (`PG_PRIVATE_PRODUCTS`), `pg_generate.sh` (`PRIV`, `xroot`), `pg_verify.PRIVATE_PRODUCTS` | `Consistency.test_one_private_products_path`, `Prefix.test_slot1_reads_its_private_source`, `Generate.test_end_to_end` |
| the trace prefix: never inherited, built only from a pinned strace descriptor and a trace directory, empty with neither, refusing anything else (director, Q-B) | `run_gevgen_v3.sh` `pg_trace` | `Prefix.*` (F1's argv byte-identical with no inputs; an exported scalar ignored; strace execs the command directly; refusals) |
| the traced calls are path-only: open, access, stat, readlink and chdir families; no execve, no argv, no seed (Q-C) | `TRACE_SET` (the same string in `run_gevgen_v3.sh` and the probe) | `Prefix.test_valid_inputs_trace_the_command_directly`, the probe's `Constants.test_trace_set_is_the_pipelines` |
| strace first, through its pinned descriptor with the self-test, before any other step (director, answer 2) | `pg_generate.sh` step 0, `pg_verify tool-check` | `Generate.test_end_to_end` (first call), `test_a_failed_strace_check_stops_before_any_step`, `ToolCheck.*` |
| R1's pins are filled only from the director's confirm; the binary refuses until then | `pg_pins.json`, `pg_generate.sh` `pin` | `Generate.test_unfilled_pins_refuse` |
| slot 1's product is every pinned member and nothing else, read-only; its dbconfig is the pinned one (condition 1; answers 3 and 4) | `pg_verify members-check`, `tool-check` on dbconfig | `Members.*`, `Generate.test_a_failed_members_or_dbconfig_check_stops` |
| the programs the traced steps run: no trace shows an exec (the kernel maps a program without an open), so `gevgen` and `gspl2root`, resolved by each tune's own setup, must be genie-product files matching the manifest, before any traced step | `pg_generate.sh` (`command -v` after sourcing the setup), `pg_verify exe-check` | `Exe.test_programs_against_the_manifest`, `Generate.test_end_to_end` (order), `test_a_failed_members_or_dbconfig_check_stops` |
| condition 2: the configuration GENIE loads, from the run, against the manifests; ROOT's files gated by location (Q-A); config-type files from outside the roots fail (tightening i); the search order (iii, Q-C) | `pg_verify trace-check` | `Trace.*` |
| condition 3: the generator's own spline open, with its bytes, from the run; the trace complete (tightening ii) | `trace-check`: initial process, spline sha; `trace_problems` | `Trace.test_the_initial_process_must_open_the_spline`, `Trace.test_completeness` |
| the checks before generation (reduce and graphs) and for every gevgen task; a failure STOPs | `pg_generate.sh` `tcheck` | `Generate.test_a_failed_trace_check_stops`, `test_end_to_end` (18 checks, the pre-generation ones before any gevgen) |
| PRODUCTS.json carries every check's pass, and refuses a failed, unreadable or missing one | `pg_lib.cmd_products` | `Seeds.test_products` |
| the required inventory in covfix_pg.py's gen-spec form, checked last (cov2d) | `pg_lib.inventory`, `inventory_problems`; `pg_generate.sh`'s last step | `Generate.test_inventory_rules`, `test_a_missing_inventory_file_stops`, `test_end_to_end` |
| piece 2's rules, unchanged: invocation, seeds, never printing a seed, everything under W, the deploy pin, no rerun | as before | `Seeds.*`, `Generate.test_refusals`, `test_end_to_end`, `test_a_failed_task_stops_and_leaves_no_seed_in_a_name`, `test_a_write_into_the_deploy_stops` |
| F1's records stay F1's | `SPLINE_PINS` apart from `PG_SPLINE_PINS`; `--truth-set f1` the default | `Consistency.test_f1_is_unchanged`; `test_fd_f1.py` passes unchanged |

## Limits of these tests

- **Stubs.** GENIE, ROOT, CVMFS, strace and `setup_salloc_env.sh` are stubs, so the end-to-end runs show the wiring,
  not GENIE's behaviour. `trace-check` is tested on synthetic traces in strace's format. B3's replay on a login node,
  and the binary's own checks, apply it to real traces.
- **Descriptor execution.** macOS can't execute a descriptor, so the tests point the descriptor directory at
  stand-in links. Descriptor execution is exercised on the node by the probe's self-test and by the binary's first
  step.
- **Tools the laptop lacks.** macOS has no `timeout`, and its `/usr/bin/time` has no `-v`; the tests substitute both.
- **Not priced or bound here.** That is the director's.

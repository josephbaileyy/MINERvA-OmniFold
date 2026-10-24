# Binding: the C_model,5D build on the 16 H2 cells (2026-10-24)

**By** the paper-tighten lane, as director, under `DECISION-20261024-joseph-5d-community-standard-route.md` item 3
and `DECISION-20261024-joseph-h2-16-cell-definition.md`. **Binds**
[`BUILD-DECLARATION.md`](BUILD-DECLARATION.md), merged in PR #337 (`8375876e`; the file's sha256 begins
`bfdd89131df38b6b`).

**MEASURES:** nothing. It authorizes one run of the builder.
**CANNOT AUTHORIZE:** a claim; folding C_model,5D into any other covariance; any printed wording; a coverage statement.

## The bound code

- **The code commit** is `dfcbb2c6c1dcb3211b7c6c8c364a6c1f9f171a47`, with `nd-unfolding/pv-ladder/build_cmodel5d.py`
  whose sha256 begins `aaa81575b211`. The director checked that digest at the commit and at the PR head.
- **The director's checks of the PR:**
  - `test_cmodel5d` and `test_pvl` pass, 53 of 53;
  - manifest `--check` is OK, and CI passed.
- **Module resolution:** the builder prepends its own directory, its parent and the deploy's `2d-unfolding/pv2d`
  paths, so `build_cmodel`, `pv2d_lib` and `pvl_analyze` resolve inside the deploy.

## Conditions

1. **Deploy as declared:** a clone at `dfcbb2c6` in `/pscratch/sd/j/josephrb/cmodel5d-20261024/repo`, with HEAD and
   a clean tree checked and logged.
2. **Log module resolution.** Before the build, print `__file__` for `build_cmodel`, `pv2d_lib` and `pvl_analyze`, as
   imported by the builder's own path setup. Each must lie under the deploy. If any does not, stop.
3. **Run the tests, then the exact argv once,** on a login node at 0 node-h:
   - no retries;
   - any refusal is reported to the director unrepaired;
   - nothing is written to CFS.
4. **The PC verdict does not gate the build,** as declared.
   - A verdict other than PASS carries its label ("not evidence"), and the director reports it to Joseph.
   - The 16-cell readout is always labelled "not powered".
5. **Report.** Commit `readouts/cmodel_5d.json` and a short `BUILD-REPORT.md`, containing:
   - the deploy log;
   - the module paths;
   - the test and run output;
   - every product sha256;
   - the NC result;
   - the PC verdict on 27 cells and the readout on 16;
   - the per-cell s_k;
   - C_model,5D's per-cell median, p84 and max, and its integral.

   It also carries the labels verbatim. It makes no claim and no comparison with any 5D covariance: the S1 (e)
   covariance is still at its declaration stage (`5d-community-20261024/S1-PLAN.md`). Open a PR to the director.

The run may start once this record is on `main`.

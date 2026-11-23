# MSR local step: STOP at C-DID; no reading computed (2026-11-23, tier3-design)

The run had the director's GO (Joseph via the director, 2026-11-22/23). It ran from a clean detached checkout of the
merge commit `b770570ab76e69bb3996d9a04da574494f587370` (PR #1254), with 0 porcelain lines, using exactly the declared
command (`run-env.json`):

    python3 nd-unfolding/msr/msr_project.py run --products docs/orchestration/state/measurability-20261122/run-b/cluster/build --out docs/orchestration/state/measurability-20261122/run-local

- **Code and environment:** msr_project.py `1c12b745…`; python 3.12.2, numpy 1.26.4, scipy 1.15.2 (`run-env.json`, which
  also holds `numpy.show_config()`). The two LAPACK builds are numpy's OpenBLAS 0.3.23.dev (libopenblas64_) for the
  `numpy` driver and scipy's OpenBLAS 0.3.21 for the `evr` driver.
- **Outcome:** rc 3, `{"stops": ["C-DID"]}`. Under the declaration (§6) and the director's conditions, no reading was
  computed. `readout.json` holds only the controls record, and `readout.txt` reads
  "STOP: C-DID failed; no reading computed."
- **The disposition is terminal for this run:** there is no repair round, and nothing is rerun without the director's
  word.

## The controls (`readout.json`)

Every control in the first block passed except C-DID:
- **C-OPS:** all six operands, all 11 code files and the three products at their sha256;
- **C-RID:** sigma_rel max rel 0.0, null_fraction max abs 0.0, infinities and NaNs matched, n_null_modes 1 = 1,
  n_cells_grid 29 = 29;
- **C-L:** linearity 3.5e-16; U equals M16; the 2D cells equal the bank's ids;
- **C-GRID:** h2 = h2_rid = non-empty coarse = 29, t1 134;
- **C-T3:** max abs 0.0, the T3 verdict COMPLETE;
- **C-F0B**, **C-D**, **C-A2** (max abs 0.0);
- **C-2D:** M equal to the bank's response; T equal to its prior; both background-term constructions equal;
- **C-MARG:** world shape [14, 16, 7, 7, 6], with the axes named.

C-RANK, C-RHO and every bias statistic come after this block and were not reached.
<!-- absence-ok: the record of a STOP; "not reached" and "no reading" describe this run's own order of work -->

## Why C-DID failed (diagnosis from the control's own inputs; no reading involved)

C-DID's record: 151 functionals compared, sigma_rel max relative difference 7.09e-13, null_fraction max absolute
difference 1.40e-16.

These were checked by recomputing only C-DID's sub-conditions from the same inputs:
- **The values pass the declared bars** (1e-6 on each). On the 151 functionals both lists name, sigma_rel and
  null_fraction agree to round-off, and the set of functionals with a finite width is identical on both sides (150 and
  150).
- **The failing sub-condition** is one I added in code, `len(common) == len(t1_names)`: every one of IBU-1's 153
  functional names must also be among D-ID's 183. Two are not: **`EW_all_ones`** and **`total_integrated`**. IBU-1's
  `s5c_coverage.reported_functionals` lists them, and D-ID's operand list does not carry them.
- **The declaration's C-DID** (§6) reads "reproduces … on the functionals both name". So the extra requirement is
  stricter than declared. The STOP comes from the implementation, not from any disagreement between IBU-1's world and
  D-ID's construction. agy's reads of msr_project.py, and its synthetic fixture (whose names are all shared), did not
  exercise the case.

**What this does not license:** any reading. No statistic of any bias vector was computed. The director decides whether
msr_project.py is amended to the declared "functionals both name" rule (which would mean a new sha, the tests, a review
and a new GO) and the run repeated.

## Files

- `readout.json`: the controls record, sha256 eded011a…
- `readout.txt`: sha256 d026c5e1…
- `run-env.json`: HEAD, the empty porcelain, the versions, `numpy.show_config()`, threadpoolctl's BLAS/LAPACK, the thread
  env and the command; sha256 ae63d895…
- `run.stdout.txt` and `run.stderr.txt` (stderr empty).

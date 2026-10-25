# S1 binding, amendment 1: re-pin the assembly after its import STOP (2026-10-25)

**By** the paper-tighten lane, as director.

**Amends** [`S1-BINDING.md`](S1-BINDING.md). With its erratum (PR #342, `a62a6040`), that record's file sha256 begins `b8c8b7ed16da1e38`.

**Under** the same approval: `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`, item 2.

**MEASURES:** nothing.

**CANNOT AUTHORIZE:**
- any new compute;
- a change to a declared choice, gate or cap;
- a claim.

## 1. What stopped

The jobs and gates before the assembly all passed. The measurement session reported them by correspondence, and
`S1-REPORT.md` will carry the receipts:
- the pilot, P1, P2 and the seed job all COMPLETED 0:0, using **6.04 CPU node-h of the 15.5 cap**;
- G1–G5 ALL PASS, rc 0, including G3 on all 175 universes and G5 on all four seeds;
- the products are 176 in `runs/uni` and 80 in `runs/seed`.

**The STOP.** The §3.1 argv, run exactly at 05:17:00 UTC on login12, exited 1 after 0.34 s with
`ModuleNotFoundError: No module named 's5p_stage1_inspect'`, at `s1_assemble.py:37`. No output was written.

**Cause.**
- Under `-I`, Python adds no script directory to `sys.path`; in 3.11 this is reported as `sys.flags.safe_path`.
- `s1_controls.py:31-33` puts its own directory there, and `s1_assemble.py` did not.
- No test ran the script the way the declaration invokes it.

## 2. The director's rulings

1. **Repair by a code fix and a re-pin** (the measurement session's option (b)), rather than changing the declared
   interpreter flags (option (a)).
   - This follows Joseph's standing rule: "fix now and re-pin with a record".
   - It also keeps the defect from reaching the next caller.
2. **The products and logs may go to HPSS** (S1-BINDING §2 item 7) despite the STOP.
   - Item 7 is conditioned only on G3 and G5.
   - The stop rule (item 5) bars continuing or repairing the analysis. A copy that only reads the products is
     neither.
   - The copy has run and passed. Its receipts go in `S1-REPORT.md`.

## 3. The fix (PR #346, merged at `3f545564`)

**The only code changes** between the old pin `d5617470` and `3f545564`:
- `s1_assemble.py` gains `import sys` and the `_ND` sys.path block copied from `s1_controls.py:31-33`. Its new sha256 is
  `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7`; it was `5ebe1a8a…`.
- A new test, `nd-unfolding/tests/test_s1_scripts_isolated.py`, sha256 `d65eabc9fc32462a…`.
  - It runs both scripts as `env -u PYTHONPATH <python> -I -B <script>`, from a temporary cwd.
  - `--help` must exit 0, and an argparse error must exit 2. No case may raise ModuleNotFoundError.

**Unchanged:**
- `s1_controls.py` (`bfc8986e…`), `test_s1_assemble.py` (`a4bb6982…`) and `s5p_assemble.py`;
- every other file under `nd-unfolding/`.

The other files that changed between the pins are `VALIDATION_LEDGER.md`, `tools/registry/check_registry.py` and
`docs/`. None is imported by any S1 script.

**The director's checks:**
- At `3f545564`, `test_s1_scripts_isolated`, `test_s1_assemble` and `test_s5p_assemble` ran **24 tests, all
  passing**.
- With `s1_assemble.py` set back to the old bytes, `test_s1_scripts_isolated` fails both of its `s1_assemble` cases,
  with the STOP's exact error.
- CI passed.

**The measurement session's sweep:**
- No other script named in a bound S1 argv has the defect. `s1_controls`, `s5p_universe` and `s5p_numerics` each
  insert their own directory.
- The task-table scripts run without `-I`, through `mnv_guarded_run`.

## 4. What is bound for the assembly

1. **A fresh deploy** of `3f5455648ff9b2c8ce85315f8f95458d87ea5673` in `$B/deploy/3f545564`.
   - Check HEAD, and log a clean tree with `--porcelain --ignored`.
   - Check `s1_assemble.py`'s sha256 against the value above.
   - Run the three test modules in it, with `TMPDIR` on pscratch and `-B`.
   - The old deploy `$B/deploy/d5617470` stays as it is.
2. **Before the run, log module resolution.**
   - Under the declared `$PY`, from a cwd outside `nd-unfolding`, import `s1_assemble` by path the way the script runs.
   - Print `__file__` for `s5p_stage1_inspect` and for every other non-standard-library module it loads.
   - Each must lie under the new deploy. Anything else is a STOP.
3. **The §3.1 argv, exactly,** with `$D=$B/deploy/3f545564` and `--cmodel-sha256 3008d8f6…e882` (S1-BINDING §1).
   - Every input stays where it is.
   - `--out $B/s1_assembly.npz` is unchanged. If a file is already at that path, the assembler's no-overwrite refusal
     fires, and that is a STOP.
   - It runs on a login node, at 0 node-h, with no retries. Any refusal or non-zero exit is a STOP, reported unrepaired.
4. **The products, gates G1–G5 and the jobs' ledger stand.** None of them depends on `s1_assemble.py`.

## 5. Where the old pin is cited

These citations stay as historical records of what was bound and declared:
- `S1-BINDING.md` §1, the deploy pin `d5617470`, the old `s1_assemble.py` digest and "20 tests";
- `S1-DECLARATION.md` §6, `5ebe1a8a…`, and §5's "18 tests".

Both records now carry a pointer to this amendment. For the assembly, this amendment's pin and digest supersede them.

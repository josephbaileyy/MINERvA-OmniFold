# FD-PRR ADDENDUM A1: the job script sources its environment before every python3 call (2026-11-08, for coverage-5b-audit and the director's binding; nothing runs)

**By:** the valid-region lane (session director-helper-2), at the director's direction of 2026-11-08.

**Amends:** `FD-PRR-DECLARATION.md` rev 2, bound by FD-PRR BINDING 1 at M = `a5235714a379457f09c539a2c94054354640648c`
(the #937 merge). Only §8.1's digests of three files and the test and mutant counts change. Every other section,
reading, price and licence is unchanged.

**CITABLE FOR:** the change to `sbatch_prr.sh`, its test, its required mutant, and the new digests.

**NOT CITABLE FOR:** anything the declaration does not license; any cluster result.

## 1. The defect

`sbatch_prr.sh:34` at M runs `python3 "$PY" limit "$MODE"` before the script sources `setup_salloc_env.sh`, which it
did only at :70.
- **The environment at that point.** The job inherits the plain login environment, and there `python3` is
  `/usr/bin/python3`, 3.6.15.
- **The failure.** In 3.6, `prr_probe.py`'s first statement, `from __future__ import annotations`, is a SyntaxError,
  so the call fails.
- **What it would have cost.** The dry job would have refused at once, with "no declared limit": rc 2, nothing
  staged, seconds of charge, and no dry run.
- **It is a known failure.** RS1 A1 hit the same defect on 2026-11-07 (#905).
- **How it was found.** The lane found the order while preparing the `prr_dry` connect. The director confirmed the
  cluster's version from RS1's record.
- **Why the tests missed it.** The local tests could not see it: on the lane's machine, `python3` is a conda 3.12.
  <!-- absence-ok: the reason the local suite could not reach the defect, stated by its mechanism -->

## 2. The change

One line in `sbatch_prr.sh`, after the mode check and before the first `python3` call, with a two-line comment:

    source "$D/setup_salloc_env.sh" > /dev/null 2>&1

- **No other line changes.** The later `source … > "$L/env.log"` at its old place stays, so the environment is
  sourced twice. Both activate the same root_6_28 prefix, and the second still writes the job's `env.log`.
- **The source comes before the log check,** so it runs before the script has written anything. It writes nothing
  itself. `setup_salloc_env.sh` activates the root_6_28 prefix and exports variables. Its two sub-setups are absent
  from a fresh deploy, and only print "No such file", as in FD-STAB's `env.log`.
- **No other file of the pipeline changes:**
  - `prr_probe.py`, `prr_ibu.py` and `prr_read.py` are byte-identical to M;
  - every production module is untouched.

## 3. The test and the required mutant

- **`test_every_python3_call_runs_after_the_environment_is_sourced`** (REQUIRED, in `JobScript`):
  - **Statically,** no non-comment line of the script calls `python3` before the first
    `source "$D/setup_salloc_env.sh"`.
  - **By behaviour,** in RS1 A1's style:
    - the job starts with a "system" `python3` that refuses `prr_probe.py`, as the cluster's 3.6 does;
    - the stand-in `setup_salloc_env.sh` puts a working `python3` first on PATH, as the real one puts root_6_28's;
    - the dry job must run to its DONE.
  - **The stand-in reads `PRR_ENVBIN`.** That variable is set only by this test, so every other test's environment is
    unchanged.
- **The required mutant, "limit above the source,"** deletes the new line. The test kills it both ways: the static
  order fails, and the job refuses at `prr_probe.py limit`.
- **The counts:** 104 tests (103 + 1) and 63 mutants (62 + 1).

## 4. The new digests (sha256; the other three files are M's)

| file | at M | after A1 |
|---|---|---|
| `sbatch_prr.sh` | `323f491a…` | `10290087cdd57d972a4df5289f1910161373e8def3f44c15ba0682f9d14a0b85` |
| `test_prr.py` | `33bfdf09…` | `44223143a6982fb876e742fd910c3de46e48fb419da351b9ad9693186f791746` |
| `prr_mutation.py` | `28f3f9e5…` | `4666aa0654dccbe999972642090cfc18ccac8d14d7fa4c5057be6e745520ef25` |
| `prr_probe.py`, `prr_ibu.py`, `prr_read.py` | unchanged | `f87ee90c…`, `17acad82…`, `f35bc328…` |

## 5. Receipts

- **Where they are made.** In a clean clone at this addendum's code commit, which the receipt README names. A
  following commit adds only the receipt files.
- **How.** Each run is one serial process under `nice -n 19`, with every thread cap at 1. The runs are:
  - every class but `JobScript`;
  - the `JobScript` class alone;
  - the 63-mutant run.
- **Where:** `fd/receipts-prr/a1/`.

## 6. The connect

- **The pre-check stays, run after sourcing.** The `prr_dry` connect's pre-submission check of `prr_probe.py limit
  dry` stays. It now runs after sourcing `setup_salloc_env.sh`, as the job does, so it tests what the job will run.
- **The connect is rebuilt at the bound commit.** It is built from a fresh clone at the commit that binds this
  addendum, and its sha256 goes to the director before launch (BINDING 1 ruling 7).

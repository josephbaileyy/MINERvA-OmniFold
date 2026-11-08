# RS1 full run, resumed under addendum A1: the receipt (job 60982139, 2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under RS1-BINDING-2 addendum A1,
revision 2:
- M_A1 = `1f747346`, the tools and the planner;
- tasks run from the bound deploy at M = `e306087e`;
- the fresh root `/pscratch/sd/j/josephrb/rs1-a1-20261107`.

**COMPLETED, 66 of 66 tasks, with no teardown crash.** The bound analysis ran on the fresh root and reports status
READ. The outcome is recorded separately, in the outcome record.

**CITABLE FOR:** the run's execution, the staging, the charge, the V_02 bitwise comparison, the analysis record and its
digest, and R0's record and its digest.

**NOT CITABLE FOR:** any reading's interpretation. That is the outcome record's job, with its CITABLE FOR and NOT CITABLE
FOR.

## The connect (`connect/`)

**The scripts:** `rs1_a1_submit.sh`, sha256 `00866763…`, and the launcher `rs1_a1_launch.sh`, `1a1db47a…`. Both are
byte-identical to the ones sent. The launcher's rc and ssh's rc were both 0.

**`connect-a1.log.txt`** (login34, 2026-11-08T00:13:27Z–00:15:12Z, rc 0). It shows:
- **the fence:** clear;
- **iris:** 1,766.1 node-h remaining;
- **attempt 1, from its own files:** both SHA256SUMS digests, FAILED rc=124, and sacct reading `COMPLETED|944|1` and
  `FAILED|3520|1`;
- **the stat** of both inputs;
- **both clones** clean at their pins, with 6/6 blobs;
- **the queue:** `252c9628…` and dry `92195b6d…`, equal to attempt 1's apart from the root;
- **the planner's `--help`** run under the sourced environment (Python 3.11.14);
- **the staging** (`stage/`), under the same environment:
  - 66 tasks, 20 done and 46 todo, 102 files copied and verified;
  - V_02's eight files in `runs-attempt1/rs1_V_02` only;
- **the submission:** `TimeLimit=04:30:00`.

## The job (`log-full/`, `sacct-60982139.txt`)

- **`sacct`:** COMPLETED 0:0, 1 node (nid004180), ElapsedRaw 10,090 s, so **2.8028 node-h**.
- **RS1's total:** 0.2622 (dry) + 0.9778 (attempt 1) + 0 (A1 connect 1) + 2.8028 = **4.0428 of the 8.0 cap**.
- **`DONE`:** `{"mode": "full", "addendum": "A1", "tasks": 66, "ended": 66, "staged": 20, "ran": 46, "rc": 0,
  "pin": "e306087e…", "a1_pin": "1f747346…", "teardown": ""}`.
- **The guard:** **no TEARDOWN-CRASH entries.** There is no `.teardown`, no `.failed` and no FAILED. The PyROOT
  teardown crash of attempt 1 did not recur in 46 tasks.
- **`log-full/SHA256SUMS`:** the products at the job's end.

## After the run (`read/`)

**The connect:** `rs1_postrun.sh`, sha256 `7351e8ab…`, and the launcher `f3ea0a16…`. It ran on login16,
2026-11-08T03:13:16Z–03:13:35Z, at 0 node-h, with rc 0.
- **The fence, under the director's rule** (only `rs1_*` and `ens1_*` jobs pass): a read-only squeue from the Mac at
  03:13:06Z showed no jobs, so it passed (`prelaunch-squeue-director-rule.txt`). The connect's own squeue matches.
- **The run checks:** the DONE is exact, sacct reads `COMPLETED|10090|1`, and the deploy is at M with no modified tracked
  files.

**The V_02 comparison** (the director's ruling 4). Its record stays on pscratch, at `/pscratch/sd/j/josephrb/rs1-a1-20261107/read/v02-compare.json`, sha256 `374969f26cad8d2d1fcc488c4c71ae4a469f008bf3be1e4e48c2cfe0a60d42f5`. It is not in git: it names the four products by bare file name, and `verify_receipt_artifacts.py` then requires them to be tracked. The checker is shared, so this lane does not change it. The four recomputed products, `rs1_V_b-_j6…j9.npz`,
are **bitwise identical** to attempt 1's copies in `xsec_flat` and `xtrue_flat` (`all_bitwise_identical: true`). The
crashed run's products were complete and reproducible, and the re-run's are the ones used.

  The compared files, by full path, with the re-run's digests from `runs-SHA256SUMS`:
  - `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/V/rs1_V_b-_j6.npz` (sha256 `087dc5f6480c35cc…`), against `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs-attempt1/rs1_V_02/rs1_V_b-_j6.npz`
  - `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/V/rs1_V_b-_j7.npz` (sha256 `397b9397c0964720…`), against `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs-attempt1/rs1_V_02/rs1_V_b-_j7.npz`
  - `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/V/rs1_V_b-_j8.npz` (sha256 `e1999de686bc47d7…`), against `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs-attempt1/rs1_V_02/rs1_V_b-_j8.npz`
  - `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/V/rs1_V_b-_j9.npz` (sha256 `9ccfd45657e4ae7a…`), against `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs-attempt1/rs1_V_02/rs1_V_b-_j9.npz`

**The analysis** (`rs1_read.json`, **sha256 `9938e168…`**). The bound `rounding_mechanism_analyze.py read` ran at M,
under the sourced environment. The FD-STAB references came from attempt 1's `refs/`, and the analysis verified them
against FD-STAB's pinned SHA256SUMS. The gates:
- **G1:** all 21 pass;
- **G2:** passes, with a zero-spread fraction of 0;
- **G4:** all 3 pass.

The status is READ. `runs-SHA256SUMS` pins all 458 files under `runs/`.

**R0** (`rs1_r0.json`, **sha256 `724f0c3a…`**) was run locally at M on the committed inputs:
- `i0.json` (`9a4142d3…`);
- `fd_data_product.json` (`b79556f0…`);
- `s1_assembly.json` (`81e5ef3f…`).

Its controls passed: I0's printed σ_J/f values were reproduced, and C_e is identical.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

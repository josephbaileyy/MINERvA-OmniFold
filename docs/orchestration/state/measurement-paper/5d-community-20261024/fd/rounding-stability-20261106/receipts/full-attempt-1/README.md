# RS1 full run, attempt 1: the failure receipt (job 60972000, 2026-11-07)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under `RS1-BINDING-2.md` at
M = `e306087e68fd497541d32b440848a40f7f29611e`, after the director's go on the connect's sha256.

**The director's classification:** INVALID (infrastructure), not a STOP on the study. Nothing is graded from this
attempt. A resume is RS1-BINDING-2 addendum A1, which is approved in principle and needs its own audit and binding.

**CITABLE FOR:**
- the attempt's execution: the connect's checks, the failure, its log, the charge, and which tasks ended.

**NOT CITABLE FOR:**
- any gate, reading, R0 or product value. Nothing was read or graded;
- a cause of the crash beyond the log's own frames.

## The connect (`connect/`)

- **The scripts:** `rs1_full_submit.sh`, sha256 `fe47b981…`, is byte-identical to the one sent. `rs1_full_launch.sh`
  is `7e5c4be5…`. ssh rc was 0 (`launch-full.out.txt`).
- **`connect-full.log.txt`:** login26, 2026-11-07T18:43:50Z–18:44:38Z, rc 0. In order:
  - **the fence:** clear (no josephrb job);
  - **iris:** 1,774.3 node-h remaining;
  - **the dry run:** DONE 9/9 at M; all 9 ends present; `log-dry/SHA256SUMS` at `e3cc597c…`, as committed; all 18 dry
    products at their lines; sacct for 60970044 reads `COMPLETED|944|1`; both queue digests unchanged;
  - **the projection:** 4.082 h against 6.964 h;
  - **the deploy:** a fresh clone at M into `deploy-full`, clean, 5/5 blobs;
  - **the submission:** job 60972000, with scontrol `TimeLimit=07:15:00`.

## The failure (`log-full/`, `sacct-60972000.txt`)

- **`sacct`:** FAILED 1:0, 1 node (nid005699), ElapsedRaw 3,520 s, so **0.9778 node-h**. The RS1 total is
  0.2622 + 0.9778 = **1.2400 of 8.0**.
- **The job log** (`connect/rs1_full_60972000.out.txt`): "xargs: bash: exited with status 255; aborting", then
  queue rc 124 and STOP. `log-full/FAILED` reads `rc=124`, and there is no DONE.
- **The task:** `rs1_V_02`, V jitters 6–9 (`log-full/tasks/rs1_V_02.log.txt`; exit status 129 and wall 30:23 in
  `rs1_V_02.time`):
  - **all four unfolds completed** and were written with rc 0: `rs1_V_b-_j6.npz` … `_j9.npz`;
  - **then** 18 lines of `Error in <TClass::LoadClassInfo>: no interpreter information for class TString`, and
    `*** Break *** segmentation violation`;
  - **the crashing thread** is in `CPyCppyy::op_str` (`libcppyy3_11.so`), called from `Py_FinalizeEx` →
    `atexit_callfuncs` after `handle_system_exit(sts=0)`. That is PyROOT, during interpreter teardown;
  - **no other task** of the 12 started in this job shows a TClass line or a crash.
- **What ended:**
  - 20 `.end` files: 9 copied from the dry run, and 11 full tasks (A0_03–07, F_pt_00–01, V_01, V_03–05), 42 unfolds;
  - `rs1_V_02` wrote its 4 products but has no end;
  - 45 tasks never started;
  - `log-full/SHA256SUMS` pins the 110 files under `runs/` at the job's end.
- **What remains:** 178 unfolds, since the director ruled that V_02 is re-run (ruling 4).

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

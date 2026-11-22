# cov2d_fence.sh rev 2: the COV2D fence, sacct only (2026-11-22)

**By** the `cov2d` session, at the director's request. Rev 1 (sha256 `16a2a5cd…`) called `squeue` at line 9, which the
standing rule forbids (sacct, never squeue). The four committed copies of rev 1 are left in place: each records a connect
that already ran with it. Nothing uses rev 2 until the director has its sha.

**Files**
<!-- absence-ok: describes this test's own stubs and cases, not a claim that a result does not exist -->
- `cov2d_fence.sh`: the fence. Run with bash on a Perlmutter login node. Exit 0 prints `FENCE CLEAR` last. Exit 3 prints `FENCE REFUSED: …`.
- `test_cov2d_fence.sh`: stub test. sacct, date, id, hostname and squeue are shims, and squeue must never run.
  It has 30 sacct/env cases. Each checks the exit code and the verdict line.
  It also checks the sacct argv (-S at least 172800 s back, -X -n -P -u -E now -o, no -s/--state), deletion of the
  `/dev/shm` self-copy on both exits, and that squeue never runs. `bash test_cov2d_fence.sh` exits 0 with ALL PASS
  (41 ok lines) on this Mac: bash 3.2.57, /usr/bin/awk.
- `mutants.txt`: 24 hand mutants of the fence, each run against the test: 24/24 killed.

**What the fence does**
- It reads `sacct -X -n -P -u <user> -S <60 days ago, local> -E now -o JobID,JobName,State 2>&1`.
- It refuses if `date` or `id` fails or gives a malformed value, or if sacct exits non-zero.
- It refuses on any line (stdout or stderr) that is not a 3-field row with a numeric JobID. An error sacct prints while exiting 0 therefore refuses.
- It refuses if a row named `cov2d*` or `t2a*` has a State whose first word is outside the closed terminal set
  BOOT_FAIL CANCELLED COMPLETED DEADLINE FAILED NODE_FAIL OUT_OF_MEMORY PREEMPTED TIMEOUT.
  State is classified in code, not with `sacct -s`, because Perlmutter's sacct rejects CF.

**Review**
<!-- absence-ok: describes this test's own stubs and cases, not a claim that a result does not exist -->
- Grok read a first draft and returned FIX.
- Fixed: sacct exiting 0 with an error on stderr printed CLEAR. stderr is now merged into the classified stream, and the JobID must be numeric.
- Tests added for the untested branches it named: stderr cases, id/date failures, a blank line mid-listing, bare
  `CANCELLED`, `CANCELLED+`, array/het JobIDs, the full argv, verdict text, and the self-copy exit code.
- The window went from 14 to 60 days. Grok noted that a pending job whose EligibleTime is before `-S` can fall outside a sacct window; 60 days reaches back before the cov2d campaign began (2026-11-02).
- agy (gemini-3.8-flash-high) read this version (fence `46092049…`, test `7a90157e…`) and returned PASS. It noted that a
  benign sacct stderr line would refuse; it judged that unlikely on a healthy node and acceptable under fail closed.

**Known gap (disclosed, not fixable sacct-only)**
- sacct's default listing omits a pending job with no EligibleTime: `sbatch --hold`, `scontrol hold`, and array tasks held by a `%` limit.
- Its view also lags slurmdbd briefly.
- squeue would see these jobs, but the rule forbids it. A connect that relies on this fence also takes a fresh ack from
  the `cov2d` session given just before it, which covers the gap.

**Not tested here:** gawk (the Perlmutter awk). The awk program uses only POSIX features (split, for-in, ERE, exit in END).

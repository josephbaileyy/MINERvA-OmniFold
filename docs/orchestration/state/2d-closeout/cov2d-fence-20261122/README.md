# cov2d_fence.sh rev 3: the COV2D fence, sacct only (2026-11-23)

**By** the `cov2d` session, at the director's request. Rev 1 (sha256 `16a2a5cd…`) called `squeue` at line 9, which the
standing rule forbids (sacct, never squeue). The four committed copies of rev 1 are left in place: each records a connect
that already ran with it.

**Rev 3 (2026-11-23).** Rev 2 (sha256 `3fbc9cbd…`, merged at 7d5a98361) failed closed in production. At tier3-design's MSR
connect P (login38, 2026-11-23T03:14:13Z), Perlmutter refused its query `-S <60 days ago>` with
`sacct: error: Too wide of a date range in query`, so the fence printed FENCE REFUSED and exited 3 (records:
tier3-design's branch at 2b06909b, `docs/orchestration/state/measurability-20261122/run-p1/`).
- **The only code change:** -S is now 14 days back, the window rev 1 and the T3 and flux2 sacct fences ran successfully
  with. It covers the 48 h MaxWall with margin.
- **The header comment is corrected.** Its "60 days is far past the required 48 h" premise is gone.
- **Two tests are added:** a stub case in which sacct prints "Too wide of a date range" with rc 1, which the fence must
  REFUSE; and checks that the logged -S is at most 14 days back and that the script's only `date -d` window is
  '14 days ago'.
- **Kept from rev 2:** everything else, including the self-delete guard and its `..` rule.
- Nothing uses rev 3 until the director has its sha.

**Files**
<!-- absence-ok: describes this test's own stubs and cases, not a claim that a result does not exist -->
- `cov2d_fence.sh`: the fence. Run with bash on a Perlmutter login node. Exit 0 prints `FENCE CLEAR` last. Exit 3 prints `FENCE REFUSED: …`.
- `test_cov2d_fence.sh`: stub test. sacct, date, id, hostname and squeue are shims, and squeue must never run.
  It has 30 sacct/env cases. Each checks the exit code and the verdict line.
  It also checks the sacct argv (-S at least 172800 s back, -X -n -P -u -E now -o, no -s/--state), and that squeue
  never runs. It has 5 self-copy cases, each run on both CLEAR and REFUSED; see "Self-copy cleanup" below.
  `bash test_cov2d_fence.sh` exits 0 with ALL PASS (52 ok lines) on this Mac: bash 3.2.57, /usr/bin/awk.
- `mutants.txt`: 32 hand mutants of the fence, each run against the test: 32/32 killed (rev 3 adds the 60-day and 15-day windows). They include dropping the `-ef`
  check, dropping the `/dev/shm/` prefix check, dropping the `..` rule, and rev 1's delete-any-`$1` cleanup.

**What the fence does**
- It reads `sacct -X -n -P -u <user> -S <14 days ago, local> -E now -o JobID,JobName,State 2>&1`.
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
- Rev 2 widened the window from 14 to 60 days, after Grok noted that a pending job whose EligibleTime is before `-S` can fall outside a sacct window. Perlmutter refused the 60-day range (rev 3 above), so rev 3 returns to 14 days. The held-pending gap is covered by the fresh cov2d ack.
- agy (gemini-3.8-flash-high) read the version before the cleanup fix (fence `46092049…`, test `7a90157e…`) and returned
  PASS. It noted that a benign sacct stderr line would refuse, and judged that unlikely on a healthy node and acceptable
  under fail closed.
- The director accepted everything except the self-copy cleanup, which is fixed above. agy (gemini-3.8-flash-high) read
  the fixed version (fence `3fbc9cbd…`, test `9d19808d…`) and returned PASS. It confirmed that fin() can delete only the
  running script's own /dev/shm copy (a symlink there is unlinked, never its target), and that the exit code is unchanged.

**Self-copy cleanup (director FIX on 2f2c9b875)**
- At exit the fence deletes `$1` only if `$1` is under `/dev/shm/`, has no `..` component, and `[ "$1" -ef "$0" ]`,
  so only when it is the running script itself.
- The `..` rule is cov2d's addition beyond the director's two conditions. Without it, `/dev/shm/../<repo>/cov2d_fence.sh`
  passes both the prefix check and `-ef` when the fence runs from the repo, and would delete the repo file.
- Any other `$1` is kept, the fence prints `self-copy not removed: <path>`, and the exit code is unchanged. A by-hand
  run or a wrong launcher argument therefore cannot delete a record or deploy file.
- macOS has no `/dev/shm`. The test runs a copy of the fence whose single `/dev/shm/*)` pattern is rewritten to a temp
  directory, and checks that the pattern occurs exactly once. The committed fence keeps the literal path.
- The five stub cases, each on both exits:
  - the real self-copy is deleted;
  - another file under shm is kept;
  - the running script outside shm is kept;
  - the running script reached through a `/dev/shm/..` path is kept;
  - the unmodified fence given an arbitrary file keeps it.

**Known gap (disclosed, not fixable sacct-only)**
- sacct's default listing omits a pending job with no EligibleTime: `sbatch --hold`, `scontrol hold`, and array tasks held by a `%` limit.
- Its view also lags slurmdbd briefly.
- squeue would see these jobs, but the rule forbids it. A connect that relies on this fence also takes a fresh ack from
  the `cov2d` session given just before it, which covers the gap.

**Not tested here:** gawk (the Perlmutter awk). The awk program uses only POSIX features (split, for-in, ERE, exit in END).

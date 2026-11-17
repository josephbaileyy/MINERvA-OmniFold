# RDX gs3a and s3a: the stage-3 gate and deploy, and the first arms job (receipt)

**By** session tier3-design, under the director's goes of 2026-11-17 (`../RDX-BINDING-1.md`, addendum J6, #1206 merged
at main `d4c8cb9b`). One run each. Both steps used the launcher and connect at P3
`95d1d529dc7c0d677c849e37bf3def06a5f76827`. They were taken by `git show P3:nd-unfolding/rdx/<f>` and checked by
`shasum -a 256` before the connects: `rdx_connect_launch.sh` `def31c02…` and `rdx_connect.sh` `1760327b…`, J6's digests.

`*.session.txt` is the launcher's stdout byte for byte, after the line `ssh rc=N` that the launcher prints first.
`*.session.err.txt` is the ssh session's stderr, NERSC's login banner. The two are byte-identical.

## gs3a: login27, 2026-11-17T11:12:02Z, rc 0

- **The checks:**
  - the `/dev/shm` copy was `1760327b…` (`gs3a.session.txt:2, 4`);
  - the 15 purge-exposed MP-1 inputs were PRESENT, by stat only (5-100);
  - `squeue --me` was empty (102-103).
- **The clone:** gs3a's clone branch (`rdx_connect.sh:57-61` at P3) runs when `$D3` is absent. It clones deploy3 and
  checks it out at P3. deploy3 at P3 after this run (below) is that clone. Then gs3a checked that deploy3's HEAD is P3 with 0 porcelain lines (63-64), as every stage-3 step does.
- **What it wrote:** `out/gates/S3a.ok`, with the lines `pin=95d1d529dc7c0d677c849e37bf3def06a5f76827` and
  `utc=2026-11-17T11:12:03Z` (104-105). gs3a STOPs if the gate file is already there (`rdx_connect.sh:103` at P3), and it
  exited rc 0, so this run created it.
- **Exit codes:** launcher, ssh and script all rc 0 (1, 106-107).
- **Charge:** none (no job).

### deploy3 after the clone, as J6 asks

`gs3a.deploy3-check.txt` is the stdout of one read-only ssh to login27 at 11:12:16Z, via saul. Its stderr was the same
login banner. It ran:
- `git -C $D3 rev-parse HEAD`;
- `git -C $D3 status --porcelain --untracked-files=all | wc -l`;
- `sha256sum` of deploy3's `sbatch_rdx_arms.sh`, `rdx-inputs-SHA256SUMS` and `rdx_connect.sh`;
- `cat out/gates/S3a.ok`;
- `ls out/gates/`.

| item | read | J6's table |
|---|---|---|
| deploy3 HEAD | `95d1d529…`, porcelain 0 | P3 |
| `sbatch_rdx_arms.sh` | `f77c89a5…` | `f77c89a5…` |
| `rdx-inputs-SHA256SUMS` | `e5baf9cc…` | `e5baf9cc…` (5 lines) |
| `rdx_connect.sh` | `1760327b…` | `1760327b…` |
| `S3a.ok` | `pin=95d1d529…` | names P3 |

The gates directory holds `ll5d_atime_post.txt`, `merge.ok`, `s2.ok` and `S3a.ok`.

## The holds, before s3a

- **cov2d acked before the s3a connect:** no cov2d cluster window was open or planned in the next hour. If the director's
  go for cov2d's login-node figure redraw came while `rdx_s3_a` was pending or running, they would hold for this lane's
  end message. The end message went to them after the watch's final read.
- **FYIs** on `rdx_s3_a` went to director-helper-2 and limitation-resolver.
- **Before the launch:** `sacct -X -u josephrb -S 2026-11-17T00:00:00 -s PD,R,RQ,S` over ssh to saul returned no rows.

## s3a: login27, 16:50:34–16:51:02Z, rc 0

- **The prologue:**
  - the `/dev/shm` copy was `1760327b…` (`s3a.session.txt:2, 4`);
  - the 15 inputs were PRESENT (5-100);
  - `squeue --me` was empty (102-103).
- **The connect's requirement:** deploy3 exists and its HEAD is P3 with 0 porcelain lines (`rdx_connect.sh:62-64` at
  P3). The connect STOPs otherwise, so it passed.
- **The policy check:** CLEAR, with `"hits": []` (104-134), over the six reads. These are the three dumps
  (`lat_RDX_ALL.npz`, `lat_RDX_ALL_bkg.npz`, `truthx_RDX_ALL.npz`), the staged `lat_zero.npz` and `lat_zero_bkg.npz`,
  and the ratio `pv-ladder-20261024/prep/ratios/L-5D-PV/tune_v1.json`.
- **The arms launcher's smoke:** "checks passed, 8 steps" (136-144). The steps are X0, X0_lat, X1, X1p, X1w, X1t, X0c
  and X1c, all under deploy3. The launcher refuses with exit 2 unless each of these holds, at P3
  (`sbatch_rdx_arms.sh:59-92`):
  - no fenced job is queued or running;
  - `gates/S3a.ok` holds the line `pin=<P3>`;
  - `checks/k1.json` and `checks/truthx_npz.json` record PASS;
  - deploy3's SUMS has a sha256 line for each of the five npz;
  - the `sha256sum` of each of the six reads equals its pin (SUMS for the five npz, `pv-ladder/prep-SHA256SUMS` for the
    ratio);
  - no product exists yet.

  Each step's `--expect-*-sha256` carries the same pins. `lat_RDX_ALL.npz` and `lat_zero.npz` both expect
  `6ca02c3d…`, as SUMS lines 1 and 4 record.
- **The fence and cap:** the connect's fence was clear, and the cap gate passed: spent 1.1492, held 0, s3a's ceiling
  0.3667 (exclusive, one node, 0:22:00), total 1.5159 of 2.5 (145). This is J6's projection.
- **The submit:** `SUBMIT id=61478320 name=rdx_s3_a limit=0:22:00 utc=2026-11-17T16:51:02Z`, PENDING in QOS regular_1
  (146-148).
- **Exit codes:** launcher, ssh and script all rc 0 (1, 149-150).

## The job's outcome: COMPLETED 0:0 in 15:38

**The watch.** `s3a-job/watch_s3a.sh` (sha256 `46eebd2a…`) ran on this laptop. Every 5 min it read
`sacct -X -n -P -j 61478320` over ssh to saul, never squeue. It stops at a terminal state, after a full read of every
step with MaxRSS, or after 6 unusable reads in a row. It differs from m's watch (`../run-m-20261117/m-job/watch_m.sh`)
in two ways:
- it takes the job id as `$1`;
- each ssh runs with `-v -E` into its own `ssh.<n>.log`, so an unusable read records ssh's reason.

All six reads here had ssh rc 0, so those debug logs are not committed. `s3a-job/watch.log.txt` holds every read:
- **Lines 1-2:** PENDING at 16:51:08Z.
- **Lines 3-8:** RUNNING at 16:56:16Z, 17:01:20Z and 17:06:24Z, started 08:52:03 PST.
- **Lines 9-10:** COMPLETED at 17:11:27Z.
- **Lines 11-22:** the final all-steps read.

**The final read,** `s3a-job/sacct.psv` (= `watch.log.txt:12-22`). Start and End are Perlmutter local time, PST
(UTC−8).

| step | state | elapsed | MaxRSS | start → end (PST) |
|---|---|---|---|---|
| `61478320` (`rdx_s3_a`) | COMPLETED 0:0 | 00:15:38 (938 s) | n/a | 08:52:03 → 09:07:41 |
| `.batch` | COMPLETED 0:0 | 00:15:38 | 1,493,776 KiB | 08:52:03 → 09:07:41 |
| `.extern` | COMPLETED 0:0 | 00:15:38 | n/a | 08:52:03 → 09:07:41 |
| `.0` | COMPLETED 0:0 | 00:15:01 (901 s) | 22,004,444 KiB | 08:52:39 → 09:07:40 |
| `.1` | COMPLETED 0:0 | 00:12:42 (762 s) | 16,310,320 KiB | 08:52:39 → 09:05:21 |
| `.2` | COMPLETED 0:0 | 00:12:42 (762 s) | 16,135,672 KiB | 08:52:39 → 09:05:21 |
| `.3` | COMPLETED 0:0 | 00:11:02 (662 s) | 21,985,728 KiB | 08:52:39 → 09:03:41 |
| `.4` | COMPLETED 0:0 | 00:13:12 (792 s) | 21,095,644 KiB | 08:52:39 → 09:05:51 |
| `.5` | COMPLETED 0:0 | 00:10:28 (628 s) | 16,972,072 KiB | 08:52:39 → 09:03:07 |
| `.6` | COMPLETED 0:0 | 00:13:01 (781 s) | 21,173,384 KiB | 08:52:39 → 09:05:40 |
| `.7` | COMPLETED 0:0 | 00:13:12 (792 s) | 21,157,776 KiB | 08:52:39 → 09:05:51 |

- **Against the limit:** 938 s of the 1,320 s limit, 71%.
- **Memory:** the largest step MaxRSS was 22,004,444 KiB (20.99 GiB). All eight ran at once on one node.
- **What the exit means:** the job's script sets rc 1 when any task's `wait` fails (`sbatch_rdx_arms.sh:129` at P3). It
  exits with that rc (132). So 0:0 means all eight tasks returned 0.
- **Which step is which task:** sacct shows only `python` for each step. Which task each srun step ran is in the job's
  log, which this receipt does not read.
- **The products:** after the end, one `ls -l` over ssh, stat only, showed all eight `out/products/<task>.npz`
  (96,063–188,868 bytes) and their `out/inventory/<task>.jsonl`, all written 09:02:45–09:07:09 PST. Their contents and
  sha256s were not read.

**The charge:** an exclusive job is billed wall time × nodes, so 938 s × 1 node = **0.2606 node-h**, under the 0.3667
ceiling. RDX's total spent is 1.4098 of the 2.5 cap: s1 0.0704, s2 0.7605, m 0.3183 and s3a 0.2606. With s3b still to
come at its 0.3667 ceiling, the projection is 1.7765.

**Not read here:**
- the job's log (`out/logs/rdx_s3_a_61478320.out` and the per-task logs);
- the eight products and their inventories;
- any arm's result.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - deploy3's clone at P3 and its digests against J6's table;
  - `S3a.ok`'s contents;
  - s3a's pre-submit checks: the policy reads, the 8-step smoke and the cap gate's total;
  - the job id and limit;
  - the launcher and connect shas that ran;
  - the job's sacct state, elapsed times, MaxRSS and charge;
  - the products' presence, by stat.
- **Not citable for:** the job's logs, the products' contents or sha256s, or any RDX arm reading or verdict.

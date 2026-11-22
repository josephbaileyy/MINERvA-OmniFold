# RDX gs3b and s3b: the second stage-3 gate, and the second arms job (receipt)

**By** session tier3-design, under the director's go of 2026-11-17 for gs3b and then s3b. The go came after s3a's
receipt merged (#1208, main `cd8be07a`), as J6 ruling 1 requires (`../RDX-BINDING-1.md`, addendum J6). One run each.
- **Pin and kit:** the same P3, `95d1d529dc7c0d677c849e37bf3def06a5f76827`, and the same kit as s3a
  (`../run-s3a-20261117/README.md`): `rdx_connect_launch.sh` `def31c02…` and `rdx_connect.sh` `1760327b…`. Their shas
  were re-checked by `shasum -a 256` before gs3b.
- **The files:** `*.session.txt` is the launcher's stdout byte for byte. Its line 1, `ssh rc=N`, is the launcher's own,
  and the rest is the ssh session's stdout. `*.session.err.txt` is the ssh session's stderr, NERSC's login banner. It is
  byte-identical to s3a's and gs3a's.

## gs3b: login27, 2026-11-17T17:43:17Z, rc 0

- **The checks:**
  - the `/dev/shm` copy was `1760327b…` (`gs3b.session.txt:2, 4`);
  - the 15 purge-exposed MP-1 inputs were PRESENT, by stat only (5-100);
  - `squeue --me` was empty (102-103).
- **deploy3:** it already existed, from gs3a, so gs3b's clone branch did not run (`rdx_connect.sh:57` at P3). gs3b then
  checked that deploy3's HEAD is P3 with 0 porcelain lines (63-64). It STOPs otherwise.
- **What it wrote:** `out/gates/S3b.ok`, with the lines `pin=95d1d529dc7c0d677c849e37bf3def06a5f76827` and
  `utc=2026-11-17T17:43:17Z` (104-105). gs3b STOPs if the gate file is already there (`rdx_connect.sh:103` at P3), and it
  exited rc 0, so this run created it.
- **Exit codes:** launcher, ssh and script all rc 0 (1, 106-107).
- **Charge:** none (no job).

## The holds, before s3b

- **cov2d gave a fresh ack before the s3b connect:** no cov2d cluster window was open or planned in the next hour. If
  the director gave cov2d new cluster work while `rdx_s3_b` was pending or running, they would hold for this lane's end
  message. The end message went to them after the watch's final read.
- **FYI** on `rdx_s3_b` went to limitation-resolver. The FYI to director-helper-2 could not be delivered: no session
  by that name was reachable. The director then confirmed that director-helper-2 is closed.
- **Before the launch:** `sacct -X -u josephrb -S 2026-11-17T00:00:00 -s PD,R,RQ,S` over ssh to saul returned no rows.

## s3b: login27, 17:43:41–17:44:22Z, rc 0

- **The prologue:**
  - the `/dev/shm` copy was `1760327b…` (`s3b.session.txt:2, 4`);
  - the 15 inputs were PRESENT (5-100);
  - `squeue --me` was empty (102-103).
- **The connect's requirement:** deploy3 exists and its HEAD is P3 with 0 porcelain lines (`rdx_connect.sh:62-64` at
  P3). The connect STOPs otherwise, so it passed.
- **The policy check:** CLEAR, with `"hits": []` (104-134), over s3a's six reads: the three dumps, the staged
  `lat_zero.npz` and `lat_zero_bkg.npz`, and pv-ladder's `tune_v1.json`.
- **The arms launcher's smoke:** "checks passed, 7 steps" (136-143). The steps are X1pc, X1wc, X0t, X0g, X1g, X0q and
  X1q, all under deploy3. The launcher's refusals are the ones s3a's receipt lists (`sbatch_rdx_arms.sh:59-92` at P3),
  here with `gates/S3b.ok`. They include the sha256 of each of the six reads against its pin, and a check that no product
  of these seven tasks exists yet.
- **The fence and cap:** the connect's fence was clear, and the cap gate passed: spent 1.4098, held 0, s3b's ceiling
  0.3667 (exclusive, one node, 0:22:00), total 1.7764 of 2.5 (144). That is within J6's at most 1.8825 after s3b.
- **The submit:** `SUBMIT id=61481240 name=rdx_s3_b limit=0:22:00 utc=2026-11-17T17:44:22Z`, PENDING in QOS regular_1
  (145-147).
- **Exit codes:** launcher, ssh and script all rc 0 (1, 148-149).

## The job's outcome: COMPLETED 0:0 in 15:35

**The watch.** `s3b-job/watch_s3b.sh` (sha256 `5a70c476…`) is s3a's watch with only its header comment changed. It ran
on this laptop. Every 5 min it read `sacct -X -n -P -j 61481240` over ssh to saul, never squeue. `s3b-job/watch.log.txt`
holds every read; all six had ssh rc 0, so the per-read ssh debug logs are not committed.
- **Lines 1-2:** PENDING at 17:44:26Z.
- **Lines 3-8:** RUNNING at 17:49:30Z, 17:54:34Z and 17:59:38Z, started 09:45:07 PST.
- **Lines 9-10:** COMPLETED at 18:04:42Z.
- **Lines 11-21:** the final all-steps read.

**The final read,** `s3b-job/sacct.psv` (= `watch.log.txt:12-21`). Start and End are Perlmutter local time, PST
(UTC−8).

| step | state | elapsed | MaxRSS | start → end (PST) |
|---|---|---|---|---|
| `61481240` (`rdx_s3_b`) | COMPLETED 0:0 | 00:15:35 (935 s) | n/a | 09:45:07 → 10:00:42 |
| `.batch` | COMPLETED 0:0 | 00:15:35 | 1,486,636 KiB | 09:45:07 → 10:00:42 |
| `.extern` | COMPLETED 0:0 | 00:15:36 | n/a | 09:45:07 → 10:00:43 |
| `.0` | COMPLETED 0:0 | 00:10:10 (610 s) | 21,793,988 KiB | 09:45:42 → 09:55:52 |
| `.1` | COMPLETED 0:0 | 00:12:41 (761 s) | 16,952,840 KiB | 09:45:42 → 09:58:23 |
| `.2` | COMPLETED 0:0 | 00:13:34 (814 s) | 21,663,068 KiB | 09:45:42 → 09:59:16 |
| `.3` | COMPLETED 0:0 | 00:11:54 (714 s) | 21,619,992 KiB | 09:45:42 → 09:57:36 |
| `.4` | COMPLETED 0:0 | 00:14:25 (865 s) | 16,847,448 KiB | 09:45:42 → 10:00:07 |
| `.5` | COMPLETED 0:0 | 00:15:00 (900 s) | 21,902,964 KiB | 09:45:42 → 10:00:42 |
| `.6` | COMPLETED 0:0 | 00:14:06 (846 s) | 17,311,612 KiB | 09:45:42 → 09:59:48 |

- **Against the limit:** 935 s of the 1,320 s limit, 71%.
- **Memory:** the largest step MaxRSS was 21,902,964 KiB (20.89 GiB). All seven ran at once on one node.
- **What the exit means:** the job's script sets rc 1 when any task's `wait` fails (`sbatch_rdx_arms.sh:129` at P3), and
  exits with it (132). So 0:0 means all seven tasks returned 0.
- **Which step ran which task:** sacct shows only `python`. That mapping is in the job's log, which this receipt does
  not read.
- **The products:** after the end, one `ls -l` over ssh, stat only, showed s3b's seven `out/products/<task>.npz`
  (98,630–189,035 bytes) and their `out/inventory/<task>.jsonl`, all written 09:55:43–10:00:37 PST. With s3a's eight,
  `out/products` holds 15 files. Their contents and sha256s were not read.

**The charge:** an exclusive job is billed wall time × nodes, so 935 s × 1 node = **0.2597 node-h**, under the 0.3667
ceiling. RDX's total spent is 1.6695 of the 2.5 cap: s1 0.0704, s2 0.7605, m 0.3183, s3a 0.2606 and s3b 0.2597. That
is under J6's 1.8825 projection.

**Not read here:**
- the job's log (`out/logs/rdx_s3_b_61481240.out` and the per-task logs);
- the products and their inventories;
- any arm's result.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - `S3b.ok`'s contents;
  - s3b's pre-submit checks: the policy reads, the 7-step smoke and the cap gate's total;
  - the job id and limit;
  - the launcher and connect shas that ran;
  - the job's sacct state, elapsed times, MaxRSS and charge;
  - RDX's total spent;
  - the products' presence, by stat.
- **Not citable for:** the job's logs, the products' contents or sha256s, or any RDX arm reading or verdict.

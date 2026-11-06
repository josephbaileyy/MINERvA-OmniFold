# COV2D A2, stage 3: the eight universe jobs are submitted (and the gate's held lags sacct)

**By** the `cov2d` session, 2026-11-06. This is the third stage of A2's fixed conditional sequence (COV2D-BINDING-2.md,
"Binding 2, addendum A2", revision 2: **M = `a60547692df5f963e428cdfe4661fc51ab785b7b`**). It proceeded on stage 2's
PASS record, `../../pseudo/AR23/pseudo_b.json` (#829, merged at `9f657e2e`).

**MEASURES:** the submission of `G18_Ua`–`G18_Ud` and `AR23_Ua`–`AR23_Ud` through the bound script, the gate's and the
order's JSON for each, and the charge sum at submission. **CANNOT AUTHORIZE:** stage 4. That proceeds under the
director's ruling below, after the auditor's read of its connect.

**Result:** all eight were submitted. Each was admitted by `order()` (`blocked_by` []) and passed the gate. The cap held:
the true sum at the last submission is 78.09 node-h of 165.8. The director accepted the stage. The gate undercounted
`held`, as described below. That is not a STOP: no guard fired and nothing was refused.

## The run

- **The connect:** `connect-universes-a2.sh`, sha256 `3e7219ea5362136b67b1f4dc8f68369d80193f2d4402d0059ad917bf35881598`.
  DIGEST_MATCH on login02, launched 09:07:57Z, DONE 09:08:28Z. Its log is `connect-uni.log.txt` (`799edc32…`, equal to
  the node's digest in `removal.log.txt`).
- **Pre-checks:**
  - the deploy `/pscratch/sd/j/josephrb/cov2d-deploy-a6054769` at M, porcelain 0 and `--ignored` 0, before and after;
  - no universe job already in `submissions.log` at M;
  - origin/main at `9f657e2e`, with AR23's `pseudo_b.json` there sha256 `d50ef13a…`, equal to the job's file;
  - G18's record `230f6918…` and the pilot readout `b59ffa2d…`.
- **Submitted** through `cov2d_submit.sh`, once for G18 (rc 0), then once for AR23 (rc 0):

| job | id | submitted (UTC) | gate: spent | held | total |
|---|---|---|---:|---:|---:|
| G18_Ua | 60895562 | 09:08:10 | 6.89 | 0.0 | 15.79 |
| G18_Ub | 60895566 | 09:08:12 | 6.89 | 0.0 | 15.79 |
| G18_Uc | 60895578 | 09:08:15 | 6.89 | 8.9 | 24.69 |
| G18_Ud | 60895585 | 09:08:18 | 6.89 | 17.8 | 33.59 |
| AR23_Ua | 60895594 | 09:08:22 | 6.89 | 35.6 | 51.39 |
| AR23_Ub | 60895595 | 09:08:23 | 6.89 | 35.6 | 51.39 |
| AR23_Uc | 60895596 | 09:08:24 | 6.89 | 35.6 | 51.39 |
| AR23_Ud | 60895597 | 09:08:25 | 6.89 | 53.4 | 69.19 |

Each job has TimeLimit 08:54:00, one node, and QOS regular_1. All eight were PENDING at 09:15:03Z (`state_after.txt`;
sacct prints node-local time, UTC−8).

## The gate's held lags sacct

`cov2d_jobs.gate` prices unfinished attempts only from the sacct snapshot that `cov2d_submit.sh` takes just before each
sbatch (`cov2d_jobs.py:242-243` at code `94544e0b`). sacct listed new jobs a few seconds after sbatch returned. So:
- each gate missed some of the jobs submitted just before it;
- `held` should have risen by 8.9 per job, from 0 to 62.3;
- it was undercounted by up to 17.8 node-h, at AR23_Uc: 35.6 against 53.4.

The last gate reported 69.19, while the true sum after all eight is 6.89 + 8 × 8.9 = **78.09**. The cap was not at
risk here. In stage 4, with 87.7 node-h of headroom left, back-to-back submissions could pass a job that takes the true
sum over 165.8.

**The director's ruling** (2026-11-06; A2's code stays frozen):
1. one job per `cov2d_submit.sh` call;
2. before each next call, sacct must list the previous id: polled every 10 s, and refused and reported after 10
   minutes;
3. before each submission, an independent recompute: spent from sacct, plus held from the unfinished attempts' limits
   and the limits of `submissions.log` ids at M that sacct does not list yet, plus this job's limit, refused over
   165.8. Both totals are printed for every job, and the stricter governs;
4. a test of the recompute on a stub where sacct omits the last submitted id: it refuses when the true total is over the
   cap and stays silent when it is not. It lives in the connect's companion test, not in A2's code.

The auditor reads the connect before stage 4 launches. Fixing the gate itself is on the follow-up list for after the
campaign.

## Files

- `connect-universes-a2.sh`, `connect-uni.log.txt`: the connect and its log.
- `removal.log.txt`: the node's digests of the log and script, then their removal from `/dev/shm`, rc 0 each, with
  `/dev/shm` left empty.
- `state_after.txt`: sacct for the eight jobs at 09:15:03Z.

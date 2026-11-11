# E96D dry run: GATE FAIL on the projection, a STOP; the full run was not submitted (2026-11-11)

**By** the valid-region lane (director-helper-2), for the director.

**Under** E96D-BINDING-1 (M_E96D `1d25f8e7`). Joseph's go of 2026-11-11, relayed by the director, lifted ruling 1's
"nothing before the LL5D readout" for this run, so that it could use the cluster before the 14:00Z maintenance.
The director's GOs were for:
- the fence (`hpss_launch.sh` `296ea772`, `cov2d_fence.sh` `16a2a5cd`);
- the dry submit (`e96d_dry_submit.sh` `c8e017dd`, `e96d_launch.sh` `8e94934b`);
- the post and full scripts (`e96d_post.sh` `824002ac`, `e96d_full_submit.sh` `9ba4321a`, `e96d_launch2.sh`
  `72ab0e04`). The full submit was not run.
  <!-- absence-ok: this record's own scope; the gate failed, so the full connect was never launched (connect/ holds no full session) -->

**The result:** the gate failed on its projection, so `GATE.json` has `"pass": false`
(`cluster/log-dry/GATE.json.txt:35-50`). Every other gate control passed. This is a STOP under ruling 3: the run is
reported as not made, nothing is repaired or resubmitted, and **no E₉₆ data reading exists.**
<!-- absence-ok: a statement of this record's own scope; the full run was never submitted (connect/ has no full session) -->

## What ran

- **The fence:** `connect/fence.session.txt`, login27 at 08:07:29Z, `FENCE CLEAR`. The only jobs queued were
  `ll5d_gate_G18` 61078463 and `ll5d_gate_AR23` 61078506, both PENDING.
- **The dry submit:** `connect/dry-submit.session.txt`, login18, 08:07:39 to 08:08:40Z, rc 0.
  - iris: the m3246 balance was 1525.6 node-h against the 4.0 cap (`:14`).
  - stat: the three files were present at AT-RISK's sizes (`:15-19`).
  - The deploy was a fresh clone at M_E96D, clean before and after, with the five bound files' sha256 matching
    E96D-BINDING-1's table.
  - The queues were `dry.tsv` `47f077d6` and `full.tsv` `3d49f92f`, as sent.
  - sbatch ran at 08:08:35Z: job 61137569, TimeLimit 00:30:00 (`:33-36`).
- **The dry job:** 61137569 COMPLETED, 08:09:02 to 08:24:40Z, 15:38 elapsed, on one exclusive node
  (`connect/post-dry-2.session.txt:9`).
  - The queue rc was 0, and both tasks ended (`:12`). DONE was written at the pin (`cluster/log-dry/DONE.txt`).
  - The gate rc was 8 (`:13`).
- **The receipts:** `post-dry.tar.gz` (sha256 `be2fe104…`) was fetched by scp and unpacked under `cluster/`, with
  `.txt` appended to each name. The products stay on pscratch under `/pscratch/sd/j/josephrb/e96data-20261111/runs/`,
  pinned by `cluster/log-dry/SHA256SUMS.txt`:
  - control `061862d0…`;
  - k = 1 `fcf1de9c…`.

## The gate (`cluster/log-dry/GATE.json.txt`)

| control | result |
|---|---|
| A-D0: (e)'s product is `fb5cc679` | pass (`:5-6`) |
| A-D0: U @ (e)'s xsec_flat equals the data product's f to 10⁻¹² | pass, max_rel 0.0 (`:8-9`) |
| A-D1: the control product exists | pass (`:14-15`) |
| A-D1: the control equals (e)'s xsec_flat bitwise, and is the declared call | pass (`:17-18`) |
| k = 1's product exists, and it is the declared call | pass |
| the control and k = 1 ran one code | pass (`:33`) |
| **the projection: lane_max × t + 300 s ≤ 0.9 × the limit** | **fail** (`:35-36`) |

**The projection:**
- lane_max is 14, and t = 907.572 s, which is k = 1's (`:39,43`). The control's t was 883.257 s (`:44`).
- So the projection is 13,006.008 s (`:40`), against 0.9 × 12,600 s = 11,340 s (`:41`). The declaration's bound is
  t ≤ 789 s.

**The measured walls** (GNU time, `cluster/log-dry/tasks/`):

| task | wall | CPU | seconds_unfold |
|---|---|---|---|
| control `e96data_E` | 14:46.08 | 1513 % | 864.186 |
| k = 1 `e96data_k001` | 15:09.71 | 1460 % | 888.48 |

- The `.time.txt` files give the walls at `:5` and the CPU at `:4`.
- seconds_unfold is at `e96data_E.log.txt:33` and `e96data_k001.log.txt:34`.
- For comparison, the declaration's unit was 657 s, and (e)'s own unfold took 692.864 s. No cause for the difference
  was measured here.

## The input atimes, for LL5D's gate receipts

The director ruled no STOP for this, with stat-only readings before and after, so that LL5D's receipts can
attribute the move. The bound job reads both inputs plainly.

| reading | of_inputs_5d.npz | bkg_dump.npz | data_b-_j-.npz |
|---|---|---|---|
| before: 08:08Z, before the sbatch (`connect/dry-submit.session.txt:16-18`) | 2026-11-08T23:17:18Z | 2026-11-08T23:17:18Z | 2026-11-05T15:18:15Z |
| during: 08:12:16Z (`connect/post-dry-1.session.txt:6-8`) | 2026-11-11T08:09:31Z | 2026-11-11T08:09:31Z | 2026-11-05T15:18:15Z |
| after: 08:26:31Z, after the only e96data job ended at 08:24:40Z (`connect/post-dry-2.session.txt:6-8`) | 2026-11-11T08:09:31Z | 2026-11-11T08:09:31Z | 2026-11-11T08:24:40Z |

- The epochs are 1794179838, 1794384571, 1793891895 and 1794385480. They were converted to UTC by script.
- The before-reading prints local time (-0800).
- Mtimes and sizes are unchanged across all three readings.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:**
- the dry run's controls: A-D0 and A-D1 passed, so the deploy, threads and runner reproduce (e)'s xsec_flat
  bitwise;
- the measured walls and per-unfold times above;
- the gate's projection failure, which is the reason the full run was not submitted;
- the atime readings.

**NOT CITABLE FOR:**
- any E₉₆ or F₆₄ statement about the data. None was computed or read: k = 1 alone is not E₉₆, and it was not
  analyzed.
- a cause of the slower unfolds;
- the full run's price at any other limit (that is the amendment's);
- any change to (e), C_e or any record.

Nothing is submitted, deposited or tagged.

# AUTHORIZATION 2026-10-16 — 2D closeout: one re-submission of the Stage C smoke pack

**Issued by** the paper-tighten lane, as director, under Joseph's compute delegation. It amends §4.6 of
[`AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md`](AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md).
That section allows one smoke pack. The first one was cancelled before it started and charged nothing.

**CITABLE FOR:**
- one re-submission of the same smoke pack from package commit `8ea086eb`;
- the QOS-name defect and how it was fixed.

**NOT CITABLE FOR:**
- the step-2 binding. Package `8ea086eb` is not bound. Every requirement of the build-step record §4 still applies;
- any other cancel or submit;
- a higher ceiling. It stays at 100.0 node-h, and committed grant ceilings under the delegation stay at 132.0 of 700.

## 1. What happened

These numbers were re-measured by the director with `TZ=UTC sacct` on `saul.nersc.gov` on 2026-10-16.

| job | name | state | QOS | ElapsedRaw | Start |
|---|---|---|---|---:|---|
| 59829287, 59829288, 59829289, 59829292 | `2dc_P_S1_001`–`004` (shared) | CANCELLED | shared | 0 | None |
| 59859828 | `2dc_P_K4_S1_001` (first smoke pack) | CANCELLED | regular_1 | 0 | None |

The closer reported the cause as follows. Slurm records a job submitted with `--qos=regular` as `regular_1`. The dispatcher and the member runner checked for the literal string `regular`, so the pack would have refused itself at start. That would have turned its 4 members into FAILED attempts. The closer cancelled the pack while it was still PENDING. By the package's rule this is not an attempt, and the 4 members are still owed.

The fix is package commit `8ea086eb` on `closeout/stagec-regular-packing-20261016`, with manifest `3578b334…`. Both scripts now accept `regular`, `regular_0` or `regular_1` and refuse anything else. 62 of 62 tests pass, including a test that accepts `regular_1` and refuses `shared` for each script.
`sacctmgr` shows `regular_0` and `regular_1` with UsageFactor 1.0, so the charge formula is unchanged.

After the cancel, 385 shared jobs are PENDING and 0 are RUNNING.

## 2. Ruling

The closer may submit **one** re-submission of the same smoke pack, with these conditions:
- the same 4 members (`2dc_P_S1_001`–`004`) and the same 00:51:00 cap, at most 0.85 node-h;
- submitted through the gate from `8ea086eb` as deployed to `$NS/repo_k`.

If this pack also fails to produce validated outputs for its members, for any reason, the closer stops and reports, and submits nothing more.

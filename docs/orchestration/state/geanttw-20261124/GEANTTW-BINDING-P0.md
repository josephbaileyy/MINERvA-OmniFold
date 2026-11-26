# GEANTTW-BINDING-P0: the geanttw campaign's P0

Director binding for P0 of `DECLARATION.md` in this folder (minerva-lib). Joseph asked on 2026-11-26 for geanttw to move now ("yes lets investigate this"), ahead of the v2 queue. P2–P3 get their own binding after P0's records are in.

## What is bound

The P0 package merged in #1337 (branch head `c75f0b0207b12080e9cb31a57202a5f3e16ab1b6`), unchanged on main at `d71d3f35c0475b9884b9dddf1d5f9755a5e51989`:
- `DECLARATION.md` sha256 `7733011174a71632c42a545ec5225fe268f321ec5104e77765b99a3aaa6e4a47`;
- `SHA256SUMS-P0` sha256 `f74f735c81cd80ed8a69ec2ff1d9f44c3da79a745f5a4523b80f9a966a0b8535`. Its 18 rows verify against main (shasum -c, 18 OK, checked by the director and by minerva-lib).

**M** for every connect is this binding's own merge commit. Every connect reads its scripts with `git show M:…`. Any changed byte in a bound file goes back to the director before it runs.

## The NuE exception: granted

The request is the declaration's "The NuE exception is REQUESTED" section, on the RDX precedent (`fd/redump-f12i-20261112/RDX-BINDING-1.md:146-152`). It is granted for P0 only, on these terms:
- cov2d's condition (a): the `p0` step takes cov2d's LL5D atime-post UTC, refuses unless it is given and already past, and records it in `run/gates/ll5d_atime_post.txt`. The value is **2026-11-15T02:21:21Z**, from `state/measurement-paper/5d-community-20261024/fd/receipts-ll5d/readout/post/atime-post.raw.txt` line 1 ("host=login25 utc=2026-11-15T02:21:21Z"). The director read that line on main at `d71d3f35c0475b9884b9dddf1d5f9755a5e51989`.
- Condition (b) is enforced on cov2d's side: its atime-snapshot connects refuse while a `geanttw_` job is queued or running.
- Condition (c): each event-loop job logs the NuE file's `atime_ns` and `mtime_ns`, with UTC, before and after its run (`geanttw_evloop.sbatch`). The logs go into the receipt.
- The job's `^(cov2d|t2a)` fence runs at job start and again immediately before the binary. `cov2d_fence.sh` rev 3 from M runs on every connect.
- P0 does not read cov2d's 2D universe dump. That read belongs to P3 and needs cov2d's word again.

cov2d's no-objection to P0 as merged came through minerva-lib on 2026-11-26, with the terms above. Its preflight ack was `cov2d-ACK-geanttw-preflight-2026-11-26T15:26:40Z`. cov2d asks for a fresh ack before each of the four connects.

**NUE_ACK** for all four connects: `GEANTTW-BINDING-P0:NuE-exception@2026-11-26`.

## What the GOs cover

Each step has its own GO from the director, given after the previous step's report: `deploy`, then `build`, then `p0`, then `check`, each through `geanttw_connect.sh STEP M COV2D_ACK NUE_ACK [ARG]` with a fresh COV2D_ACK.
- `build` is login-node work (0 node-h).
- `p0` submits the two declared jobs, `geanttw_p0_pin_1L` and `geanttw_p0_pat_1L`: account m3246, QOS shared, 1 task with 2 CPUs and 16G, `--time=01:00:00`, `--no-requeue`. A job that reaches its limit stops the campaign, which then goes back for a new price.
- `check` runs `p0_check.py` (C0a–C0f). Any control failure stops.

Not covered: any resubmission, any step beyond `check`, any write outside `/pscratch/sd/j/josephrb/geanttw-20261124/`, and any write to CFS.

## Budget and credential

P0 is estimated at [0.02, 0.08] node-h. At the limits it is bounded by 2 jobs × 1 h on a 2-CPU shared slice. The campaign cap is 8.0 node-h, enforced by `geanttw_sacct.py cap`. On 2026-11-26 at 15:27Z, m3246 had 488.3 node-h left (iris, via minerva-lib's preflight: Charged 19511.7 of Allocated 20000.0), so half the balance is 244 node-h. The charge is read from `sacct`. The NERSC certificate is valid until 2026-11-27T14:22:19Z (ssh-keygen -L, UTC), and no session is used past that time.

## Announcement

The director names the job prefix `geanttw_` to every fenced lane before the GO for `deploy`.

## Receipts

A receipts PR carries each connect's output, `run/acks.log`, `run/gates/ll5d_atime_post.txt`, the NuE atime and mtime logs, the `sacct` records of both jobs, and the C0a–C0f results.

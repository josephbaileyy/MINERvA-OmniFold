# OOFVC-BINDING-1: the out-of-fiducial counting-convention check

Director binding for OOFVC (ibu-chi). Joseph asked for it on 2026-11-26: central values of ten-iteration IBU (the note's c2c1-dibu quantity) and of the 2D OmniFold central value under MINERvA's counting convention, against the published result. It is descriptive. It changes no production default, and no cause is read from it.

## What is bound

PR #1400 (head `c08eda1f4837fa3bc74db5a9721acc2f53464b29`), on main at `10073a5c16de2946a87b9acb0817fb4a2f11c108`:
- `OOFVC-DECLARATION.md` (revision 7) sha256 `80c9bc39b036cbc3edb9840aabb64f8bd384832fc34e8e7f3ab38b0d1d753d2e`;
- tool commit `bbc3fc1be82572d9ad8bdd668fd51647ca1d86d9`;
- `2d-unfolding/oofvc/launch/bound/`: `oofvc_dump.sh` `bb7ca6f5784ccbbb3ed9a27c6672dc101115b0b4ceaa780335e4e5aabb9b91bb`, `oofvc_units.sh` `97c63b5ca1debc7137dd47f03fe225f399f929e674e60923099ca0c25cfe39a3`, `oofvc_post.sh` `23ef49772dc1af23d646ab7836cdc77bf44295964b905ab88023d9e525d92293`, `oofvc_launch.sh` `787445af04e50bd7086834a2e51e6fcc1102f7306e356979918e4750da5d362e`;
- the driver after `oofvc_driver.diff` `9d11bd4b…`, with ref_c2c1.py 285dd138 unchanged and inputs 43f8cc16 (CV) and d40aea69 (flux).

The code had three read rounds: codex-school, then the two last rounds with agy (gemini-4-hydrogen-high) GO. Every codex blocker was fixed with a test or mutant. It killed 55/55 mutants, and the 16 record checks pass. The director read the bound launch scripts. oofvc_dump.cpp has no local MAT, so it is checked on the cluster by C-ROUTE, C-JOIN, C-SIGW and C-LAB, each a STOP.

## Protected reads: the exception is granted

On §2.7's terms, with cov2d's no-objection of 2026-11-26T20:52:32Z, which names both reads:
1. **The NuE constraint file**, read plainly by MAT once per oofvc_dump task (12 tasks). The terms:
   - (a) dump-pilot takes the LL5D atime-post **2026-11-15T02:21:21Z** (receipts-ll5d/readout/post/atime-post.raw.txt line 1) and records it in gates/ll5d_atime_post.txt before any other write;
   - (b) on cov2d's side, its atime-snapshot connects refuse while an oofvc_ job is live;
   - (c) each task checks the declared path, then logs atime_ns and mtime_ns with UTC before and after, into dump/<pl>.nue.log;
   - the sacct fence (no live cov2d or t2a job; empty or unknown state counts as live) runs at each task's start, just before its binary, and before every submit.
2. **The CFS CV source 43f8cc16**, read once by `dd iflag=noatime` into the staging root, with the source's atime recorded before and after.

## What the GOs cover, one step per GO

Each step runs after a cert check by command and with fresh cov2d and limitation-resolver acks:
1. `oofvc_launch.sh dump-pilot <new dir> loginNN 2026-11-15T02:21:21Z`: the 1L pilot, -t 01:00:00.
2. `dump-rest`: the projection gate (each playlist ≤ 1.75 h), then the eleven tasks at -t 02:00:00.
3. `units`: staging by O_NOATIME, then one regular node at -t 00:45:00 for the join and the four units.
4. `post`, then `fetch`.

Not covered: route B (if C-JOIN STOPs, it comes back to the director priced), any resubmission, any write outside `/pscratch/sd/j/josephrb/oofvc-20261126/`, and any write to CFS.

## Budget and credential

The expected charge is about 0.3 node-h by route A, with a cap of 2.0 node-h. The balance was 488 node-h on 2026-11-26. The charge is read from sacct. The NERSC certificate is valid until 2026-11-27T14:22:19Z, and no session is used past that time. Job names: oofvc_dump and oofvc_units, announced to the fenced lanes in the fence round of 2026-11-26.

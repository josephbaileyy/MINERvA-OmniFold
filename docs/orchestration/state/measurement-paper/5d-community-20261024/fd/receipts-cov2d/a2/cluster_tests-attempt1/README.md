# COV2D A2, stage 1, attempt 1: the cluster test run FAILED (two defects; not a STOP)

**By** the `cov2d` session, 2026-11-06. This is the first stage of A2's fixed conditional sequence (COV2D-BINDING-2.md,
"Binding 2, addendum A2", M = `cf533377c7f9e1638940c677b9af5242f3ba66f4`). It is committed as is.

**Classification.** This is **not a STOP** under A2 §6: no production run's guard fired, and no input was off its pin.
It is a failure of the pre-run test stage. The sequence stops here, before stage 2, and goes to the director.

**MEASURES:**
- the suites at M in the cluster environments;
- whether A2's guard tests run on Linux;
- whether `showquota` can be read on a compute node.

**CANNOT AUTHORIZE:** stage 2.

## The run

- **The connect:** `connect-a2tests.sh`, sha256 `47402933…`. DIGEST_MATCH, then launched on login02, 02:12:05Z to
  02:20:37Z. Its log is `connect-a2tests.log.txt` (`bf5cb0cf…`, the node's digest in `node_and_removal.txt`).
- **The clone:** a fresh clone of GitHub at M, with HEAD asserted. Porcelain before was plain 0, `--ignored` 0; after,
  the same.
- **Suites:** **12 of 13 suite runs pass** in P (omnifold_py310), R (root_6_28) and RM (root_6_28 + the pinned MAT
  environment; `{"mat_setup_scripts": 6, "mismatches": 0}`).
  - The skips are only the expected ones: P's real-parser test, and the Receipt class in P and RM.
  - The audit hook caught 0 guarded reads.
- **The deploy:** `/pscratch/sd/j/josephrb/cov2d-deploy-cf533377` was made as a fresh clean clone at M, 0/0. It is
  still 0/0 and untouched.

## Failure 1: step A's fire test on Linux

`P test_cov2d_pseudo.test_a_plain_read_of_a_staged_copy_stops` failed with `(0, 'PASS', [])` against the expected
`(3, 'STOP', [<the constraint copy>])` (`logs/P_test_cov2d_pseudo.log.txt`). The other three guard tests ran OK on
Linux:

| test | env | result |
|---|---|---|
| step A silent on a clean run | P | RAN-OK |
| step A fire on a plain read | P | **NOT-OK** |
| step B silent on a clean run | RM | RAN-OK |
| step B fire on a plain read | RM | RAN-OK |

**The cause, inferred and not measured.**
- Linux stamps atime from the kernel's coarse clock, which has a granularity of one tick.
- The test sets `SETTLE_WAIT` to 0.
- Step A's plain read of the small constraint copy can land in the same tick as that copy's creation, so relatime
  rewrites atime to the value it already had.
- Step B's fire test passed because larger files are staged between that copy's creation and the read.

Production is not affected. The 5 s settle puts the guard's first reading at least 5 s after a copy's creation, so a
later read stamps a later atime. This is a defect in the test's timing.

## Failure 2: showquota on a compute node

`a2quota`, job 60883869 (debug QOS, nid006001, COMPLETED 0:0 in 4 s, about 0.001 node-h, outside the gate as the
director accepted). Its output is `logs/a2quota.log.txt`.
- `showquota` first queries the GPFS filesystems through `/usr/lpp/mmfs/bin/mmlsquota`. That binary does not exist on
  a compute node, so `showquota` raises FileNotFoundError before it prints pscratch's row.
<!-- absence-ok: measured, not inferred: the job's own FileNotFoundError for /usr/lpp/mmfs/bin/mmlsquota, verbatim in logs/a2quota.log.txt -->
- `cov2d.headroom_problem` therefore returns "pscratch quota unreadable from showquota". In the AR23 rerun's step A,
  that would refuse every run at its start, before staging.
- **A side note:** the job inherited the connect's TMPDIR, which was under `/dev/shm` and removed by then. Slurm logged
  that and fell back to `/tmp`. It is harmless.

## Files

- `connect-a2tests.sh`, `connect-a2tests.log.txt`: the connect and its log.
- `logs/`: one log per suite run, plus `a2quota.log.txt` and `blobs.txt` (the clone's `2d-unfolding/cov2d` tree).
  `SHA256SUMS` was written on the node, and every digest matches its file. The logs carry a `.txt` suffix because
  `*.log` is gitignored; their bytes are unchanged.
- `node_and_removal.txt`: the node listing and the connect's digests, then the removal of
  `/dev/shm/josephrb-cov2d-a2tests` and its script (rc 0 each, `/dev/shm` left empty), and the deploy's porcelain.

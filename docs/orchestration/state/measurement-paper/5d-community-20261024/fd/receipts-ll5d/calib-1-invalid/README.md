# LL5D ll5d_calib, run 1 (job 61014290): INVALID, a crash before any replicate (2026-11-09)

**By** the `cov2d` session, under LL5D BINDING 2. The director's go named `connect-calib.sh` `be7a9f37…` and
`launch-ll5d.sh` `45f5055c…`.

- **Verdict: INVALID.** `ll5d.py calib` exited 1 with a traceback 17 s after it started. No calibration record was
  written. This goes to the director unrepaired. Nothing has been relaunched, and a rerun needs the director's go.
- **sacct's state is not the step's:** sacct reads COMPLETED, ExitCode 0:0, Elapsed 00:00:26 (`watch.log.txt`). The job
  script records ll5d.py's rc (`calib rc=1` in `ll5d_calib_61014290.out.txt`; `Exit status: 1` in `calibration.time`) and
  then exits 0.
- **CANNOT AUTHORIZE:** a rerun, a repair, or the gate jobs.

## The traceback (`calibration.time`)

`ll5d.calib_main` → `truths_r` → `fd_1b_mc.truth_weight` → `s5n_pseudo.truth_weight("ratio_nd", …)` →
`s5c_pseudo.truth_weight`, which ends in `raise ValueError(name)`: **`ValueError: ratio_nd`**.

**The mechanism, read in the code at M_A1a:**
- The `ratio_nd` truth model is registered only by `s5e_candidate.install(toys.CONFIG)`, which calls
  `s5e_deform.install_ratio_truth(s5n_pseudo)`.
- `fd_1b_mc.run_unfold` calls it (`fd_1b_mc.py:507`), and so does A1b's `ll5d_b.run_unfold`. A1a's `ll5d.calib_main`
  and `gate_main` never do.
- The gate would fail at the same call.
- A1a's tests mocked `fd_1b_mc.truth_weight`, so none of them ran the real path.
- The fix and its routing are the director's to rule on. They are not part of this receipt.

## The run

- **The launch** (`fence.txt`, `staged_sha.txt`, `launch.txt`):
  - the fence was clear at 2026-11-09T00:04:03Z on login02 (squeue empty, no cov2d job unended);
  - the staged connect's node sha256 matched the local file and the go, `be7a9f3753a4c18b223e974d956c99f9fb87076941dbfeee6f87d5f45ab06aa0`;
  - it was launched detached at 00:04:21Z.
- **The connect** (`connect-calib.log.txt`):
  - iris: the m3246 balance was 1,659.6 node-h, half 829.8, against the cap 148.0;
  - the projection: charged 0.000, held 0.000, this job 5.0, total 5.000 against the cap 148.0;
  - the deploy: porcelain 0 at `e92e946759772d13e21055b21c69189c8b007183`, with all 12 bound blobs OK;
  - the job script's sha256 was `50e8db10c12dcb56cc08bffdea57dd6bb4514bb55d0f194ad20d9e6b78e8940d`, and this copy
    hashes to the same;
  - atime-pre: 749 files;
  - submitted as job 61014290, with scontrol's TimeLimit 05:00:00.
- **The job** (`ll5d_calib_61014290.out.txt`):
  - it ran on nid004154 from 00:06:17Z to 00:06:41Z;
  - the deploy was clean and the blobs OK;
  - Python 3.11 activated;
  - every thread variable was 1;
  - max RSS 4,946,388 KiB.
  - `env-job.log.txt` records two `setup.sh: No such file or directory` lines from `setup_salloc_env.sh`, which it sources
    and which do not stop it. Python 3.11 activated, as the job requires.
- **Cost:** about 0.007 node-h (26 s on one node).
- **Atimes:** atime-post was taken stat-only on the same declared inputs at 00:17:23Z (on login03). Of 749 files, 0
  moved (`atime-pre.tsv`, `atime-post.tsv`).
- **Removal:** the staged connect `/dev/shm/josephrb-ll5d-calib.sh` was removed (`rm -f` rc 0). The closing `ls` found
  nothing, which gives the step's rc of 2 (`removal.log.txt`).
- **The fetched files** match the node's sha256 (`node-sha256.txt`, 8 MATCH; the `.log`/`.out` files carry a
  `.txt` suffix here because the repository ignores those extensions, as earlier receipts did). They stay in
  `/pscratch/sd/j/josephrb/ll5d-calib-20261108/`.

## Files

`connect-calib.sh`, `launch-ll5d.sh`, `sbatch-ll5d-calib.sh`, `bound.sha256`, `connect-calib.log.txt`,
`ll5d_calib_61014290.out.txt`, `env-job.log.txt`, `calibration.time`, `calibration.out.txt` (empty), `atime-pre.tsv`,
`atime-post.tsv`, `node-sha256.txt`, `fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`, `watch.log.txt`.

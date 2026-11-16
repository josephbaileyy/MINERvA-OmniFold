# COV2D-G2R unfold jobs: the whole-set fetch and checks (2026-11-14)

**By** the `cov2d` session. This dir holds the checks that span all 12 unfold jobs. Each job has its own receipt dir
(`../D_Ua/` … `../AR23_Ud/`) with its README, connect, connect log, walls, sums and node-sha256.

**CANNOT AUTHORIZE:** the G2R readout or any other job.

- **sacct** (`sacct-utc.txt`, `TZ=UTC sacct -X -n -P` over the 12 ids): all 12 COMPLETED, ExitCode 0:0. Limits are
  08:54:00, except D_Ud at 09:18:00 (its THIS = 9.3).
- **Lane check** (`lane_check.py`, `lane_check.out.txt`): read-only on a login node, every read O_NOATIME, against
  `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/tables/runs_g2r.tsv`.
  - The table has 529 runs in 26 lanes. The two envtest lanes (one run each) have no walls file in `$O`; they ran in
    the envtest job, whose receipt is `../envtest/`.
  - For the 24 unfold lanes: each walls label set and each SHA256SUMS label set equals the table's labels for that
    lane, with no duplicates, and every `out/<label>/xsec.root` exists.
  - 527 walls lines, every rc 0: `LANE-CHECK PASS`.
- **Fetch** (`node_pass.py`): one O_NOATIME pass on login24 hashed 1716 files under `$O` (`node-sha256.raw.txt`). A
  second pass streamed the same files as a tar.
  - The files: the 12 jobs' walls, sums, job logs, preflight and MAT records, bound lists, gates and orders;
    `submissions.log`; the two tables; the 527 `xsec.root`; 527 label logs; 527 inventories.
  - `fetch-check.out.txt` is `shasum -a 256 -c` of the extracted tar against that list: 1716 `OK`, `shasum_rc=0`.
- **Sums** (`sums-check.out.txt`): `cat ../SHA256SUMS.* | shasum -a 256 -c`, run in the extracted `out/`. The 24
  SHA256SUMS files hold 527 lines, all `OK`, `shasum_rc=0`.
- **Not committed:** the `xsec.root` products, label logs and inventories. They stay on `$O` and are listed by sha256 in
  `node-sha256.raw.txt` (each job dir's `node-sha256.raw.txt` is its subset).

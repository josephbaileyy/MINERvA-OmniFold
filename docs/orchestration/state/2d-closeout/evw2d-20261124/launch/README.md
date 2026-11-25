# EVW2D launch set

These scripts run EVW2D (`2d-unfolding/evw2d/evw2d.py`, merged in #1347 at 4d9147f9) once on Perlmutter. They follow
EVW5D's merged set (`fd/evw5d-20261125/launch/`). Nothing here runs before the director's EVW2D BINDING 1 and GO.

## Files

| file | where it runs | what it does |
|---|---|---|
| `evw2d_launch.sh` | the Mac | Checks the sshproxy certificate by command before every step (`ssh-keygen -L` on the public certificate). It needs 45 minutes left for the connect and 15 for the post and cleanup. It sends each remote script through `saul` to a named login node. That node stages the script in `/dev/shm` and runs it only if its sha256 is the approved one. `fetch` copies `post.tar.gz` and `cleanup.tar.gz`. |
| `evw2d_connect.sh` | a login node | Claims the lane root by `mkdir`, with no `-p`. Clones `deploy_M` at M and `deploy_C` at C, and checks both are clean and carry the pinned bytes. Checks that `config.json` names this layout. Pre-checks the environment, with a real `O_NOATIME` open on `$SCRATCH`. Runs `evw2d.py stage` on the login node. Reads the staged omnifile through `/proc/self/fd/N` with ROOT and RDataFrame. Then it makes one `sbatch` and checks the allocation with `scontrol -o show job`. |
| `2d-unfolding/evw2d/sbatch_evw2d.sh` | the job | Checks the batch shell (name, array, `SLURM_JOB_NUM_NODES=1`). Checks `scontrol` for TimeLimit 00:30:00 and NumNodes `^1(-1)?$`, both checkouts, and the evw2d.py and config.json digests. Runs a print-only first srun step that records `SLURM_JOB_NUM_NODES`, `SLURM_STEP_NUM_NODES` and `SLURM_STEP_ID`, and stops with a recorded reason unless the step's value is `1`. Then runs one 64-CPU step of `evw2d.py run` in E_R's thread environment. |
| `evw2d_post.sh` | a login node | Uses squeue only to ask whether the job is still queued, and sacct for the outcome. Checks the product set and SHA256SUMS in place, runs `evw2d.accepted()`, and records stat lines (atime, mtime, size) for the purge exposure. Tars the receipts. |
| `evw2d_cleanup.sh` | a login node | Runs only after a passing post and its own GO. Runs `evw2d.py cleanup --out` (the declaration's §7) and keeps `deletions.tsv`. |
| `fill_pins.sh` | the Mac | Writes `bound/` and `PINS.txt` from the tool commit C, with every pin computed by command. It refuses unless `config.json` at C differs from the reviewed one (5fdb4c3f) only in the four binding fields, set to this layout. |

## Order

1. The binding commits `config.json` with `declaration_sha256`, `lane_root` (`/pscratch/sd/j/josephrb/evw2d-<yyyymmdd>`),
   `driver_tree.root` (`<lane>/deploy_M`) and `inputs.staging.root` (`<lane>/stage`). That commit is C.
2. `bash fill_pins.sh <C>` writes `bound/`, which is committed. The director binds `PINS.txt`.
3. GO, then the steps from the Mac:
   1. `bash bound/evw2d_launch.sh connect <new dir> loginNN`;
   2. after sacct shows the job ended, `bash bound/evw2d_launch.sh post <new dir> loginNN`;
   3. `bash bound/evw2d_launch.sh fetch <new dir>`;
   4. only on a passing post and a separate GO, `cleanup` and `fetch` again.

Everything is written under the lane root, on `$SCRATCH`. CFS is only read, by evw2d.py's O_NOATIME copies.

## Tests

`2d-unfolding/evw2d/test_evw2d_launch.py` (36 tests) covers the job script, the connect's allocation check, the
launcher and `fill_pins.sh`. It stubs scontrol, srun, ssh and ssh-keygen. The scontrol fixtures are two records on main,
read verbatim:
- a pending job with `NumNodes=1-1` (cov2d's connect log);
- a running job with `NumNodes=1` (xr-linux's `scontrol-job.txt`).

The post and cleanup scripts are checked only for syntax; they run after the job and submit nothing.

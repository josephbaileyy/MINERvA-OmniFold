# RSN J1 connect (2026-11-12), for the director's go

**By** session tier3-design, under RSN-BINDING-1 ruling 3 and the director's ruling of 2026-11-12 on `fence.txt`.
**It has not run.** It runs only on the director's go for these sha256s. The director gives that go after the LL5D
gates end, about 10:00–11:00Z, together with the `rsn_` announcement to every fenced lane, and names J1's slot
relative to E96D's runs.
<!-- absence-ok: an operational status of this connect's own run, not a claim that a result does not exist -->

| file | sha256 | role |
|---|---|---|
| `rsn_connect_j1.sh` | `b8f8c2af4b70384db4bb278d9d4ca11600b1fc1f2b1131e0c237b5a11fb0661e` | the connect script: fence.txt, the launcher's smoke, the J1 submit |
| `rsn_connect_j1_launch.sh` | `819be11134f1e61134a5429410541cf74470d8492525ef4411104d8426a6c04d` | the Mac-side launcher: connect 1's (`f7cc3c80`), with only the script name, its sha and two comment lines changed |
| `smoke_connect_j1.sh` | `8517c8b24141c81bbdedbac7f3933e74eb9f146f58d111939c1219a033120c8c` | the local smoke harness |
| `smoke.txt` | — | the smoke run at these bytes |

**What it does, on one login node.**
1. **It refuses before writing anything if:**
   - the host is not loginNN, or a Slurm job is set;
   - connect 1's deploy (`/pscratch/sd/j/josephrb/rsn-20261112/deploy`) is not clean at M_RSN `af711298`, or
     `sbatch_rsn.sh` is not the bound `f889a0cf…`;
   - `$OUT/nc_r.json` records no rsn-nc-r/1 PASS, or its recorded `rsn_regrade.py` sha256 is not the deployed and
     bound `661608d8…` (ruling 4, rechecked);
   - `$OUT/fence.txt` exists, or a J1 product exists;
   - a job named `cov2d*`, `t2a*`, `ll5d*`, `e96data*`, `rpd_*` or `rsn_*` is queued or running.
2. **It writes `$OUT/fence.txt`:** `cov2d`, `t2a`, `ll5d`, `e96data` and `rpd_`, one per line, the director's ruling.
   Its sha256 must equal `5934e327…`.
3. **It runs the bound launcher's own smoke mode for J1** (`RSN_SMOKE=1`, outside Slurm). That covers every refusal
   of `sbatch_rsn.sh`: the deploy, the name and limit, the fence, the NC-R PASS, the reweight's committed sha256 and
   the product. It reads no npz.
4. **It checks squeue again, then submits:**
   `sbatch --parsable --job-name=rsn_J1 --time=0:19:00 --output=$OUT/logs/%x_%j.out <deploy>/nd-unfolding/rsn/sbatch_rsn.sh <deploy> af711298… $OUT J1`.
   It then prints the job. It does not wait for the job.

The price is RSN's J1: projected 0.25 node-h, with 0:19:00 at most on one exclusive node.

**The smoke** (`smoke.txt`, 12 cases) needed one change to run off the cluster. The deploy is a local clone of M_RSN
plus one throwaway commit that pins a synthetic tune_v1 reweight, since the real one is on the cluster. The bound
launcher itself is unchanged, and its sha is checked. The cases:
- **the pass path:** the fence is at its pinned sha, the launcher's smoke passes with one step, and sbatch receives
  exactly the argv above;
- **refusals that write nothing and never call sbatch:**
  - an `ll5d`, an `e96data` or an `rsn_` job queued;
  - a dtn host, or a Slurm job set;
  - `fence.txt` exists, or a product exists;
  - no nc_r.json, or an r1 mismatch;
  - a dirty deploy;
- **a STOP before submit:** a reweight that differs from its pin, caught by the bound launcher's own smoke.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the J1 connect and its local smoke behaviour.
- **Not citable for:** J1 having run, or any reading.

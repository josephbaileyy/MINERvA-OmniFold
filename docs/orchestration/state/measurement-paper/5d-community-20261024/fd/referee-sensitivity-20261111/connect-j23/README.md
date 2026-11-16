# RSN J2/J3 connect (2026-11-12), for the director's go

**By** session tier3-design, under RSN-BINDING-1 ruling 3 ("J2 (or J2n) and J3: only after J1's NC PASS and the
committed gate files") and RSN-DECLARATION.md rev 3 §6 step 4. It deploys at **M_P1 = `5e43e509d08d9b29…`** (#1089), the
pin that adds the committed `nd-unfolding/rsn/rsn-prep-SHA256SUMS`. The diff from M_RSN to M_P1 under `nd-unfolding/` is
that one file (4 lines).
**It has not run.** Each step runs only on the director's go for these sha256s.
<!-- absence-ok: an operational status of this connect's own run, not a claim that a result does not exist -->

| file | sha256 | role |
|---|---|---|
| `rsn_connect_j23.sh` | `b576be1629163822ebe794617f464f50c5662836ae5ec844f87b1ec291eee39d` | the connect script, steps `nc` and `submit` |
| `rsn_connect_j23_launch.sh` | `5e113cf3b1af1a80bdf285c522b66b4e2eb85dedb933f146369773474b0358df` | the Mac-side launcher: J1's (`819be111`), with only the script name, its sha and a STEP argument changed |
| `smoke_connect_j23.sh` | `25c921f025145b886599b9d3bb05eb1a6a4c6a44a503afc7e1e300960097c365` | the local smoke harness |
| `smoke.txt` | — | the smoke run at these bytes (21 cases) |

Usage: `bash rsn_connect_j23_launch.sh <new empty dir> <loginNN> nc|submit`.

## Step `nc` (after J1 61168780 has ended)

1. **It refuses before writing anything if:**
   - the host is not loginNN, or a Slurm job is set;
   - a job named `cov2d*`, `t2a*`, `ll5d*`, `e96data*`, `rpd_*` or `rsn_*` is queued or running;
   - `sacct` does not show 61168780 as `rsn_J1 COMPLETED 0:0`;
   - J1's log (`$OUT/logs/rsn_J1_61168780.out`) lacks `[rsn] job=J1 rc=0`, or lacks the launcher's sha256 line for
     `rsn_nc.npz`, or the product on disk differs from that line;
   - `$OUT/nc.json`, `$OUT/gates` or the new deploy `$B/deploy-p1` exists, or connect 1's `$OUT/rsn-prep-SHA256SUMS`
     is missing.
2. **A fresh clone at M_P1 into `$B/deploy-p1`.** The checks: HEAD = M_P1 with no modified or untracked file; the
   nine §7 files at their bound sha256s; the committed `rsn-prep-SHA256SUMS` byte-equal to connect 1's; P5
   (tracked, `fd/receipts-f1/run/cluster/f1b3/prep/k1_p5_rerun.npz`) at `e36f3b25…`.
3. **`rsn_cmodel.py nc`** (§6 step 4) runs on J1's product, the frozen L-5D-PV products
   (`pv-ladder-20261024/products`, which the bound code checks against `build_cmodel5d.py` EXPECT) and P5, at
   threads 1 and nice 19, writing `$OUT/nc.json`. The file must record:
   - schema `rsn-nc/1` and `PASS`;
   - J1's product sha256;
   - the bound `rsn_cmodel.py` `ab632921…`.
4. **The gate files.** `$OUT/gates/J2.ok` and `J3.ok` each hold the one line `pin=<M_P1>`, which is what
   `sbatch_rsn.sh` requires.
5. **Everything is printed** for the receipt PR (`nc.json` and both gate files), which is committed before step
   `submit`.

None of these inputs is on prologue5's `cov2d_protected_paths`. Step `nc` reads the frozen products plainly, as the
bound code does.

## Step `submit` (after the receipt is committed, on the director's go)

1. **It refuses before submitting anything if:**
   - the host is not loginNN, or a Slurm job is set;
   - `nc.json` records no rsn-nc/1 PASS;
   - a gate file is not exactly `pin=<M_P1>`;
   - `deploy-p1` is not clean at M_P1, or `sbatch_rsn.sh` is not `f889a0cf…`;
   - `fence.txt` is not `5934e327…`;
   - a fenced or `rsn_` job is queued or running.
2. **The bound launcher's smoke mode** (`RSN_SMOKE=1`) runs for J2, which must print 8 steps, and for J3, which must
   print 4.
3. **J2 and J3 are submitted back to back,** so E96D does not wait long:
   - `sbatch --parsable --job-name=rsn_J2 --time=0:22:00 --output=$OUT/logs/%x_%j.out <deploy-p1>/nd-unfolding/rsn/sbatch_rsn.sh <deploy-p1> <M_P1> $OUT J2`;
   - the same with `rsn_J3`, `--time=0:19:00` and `J3`.

   J3 is not submitted if J2's sbatch fails. A J3 failure after J2's submit is a STOP that names J2's jobid.

The price is RSN's J2 and J3: at most 0:22:00 and 0:19:00 on one exclusive node each. That is within ruling 2's
maximum of 1.01 node-h at the three limits.

## The smoke (`smoke.txt`, 21 cases)

**The repository the connect clones** is a clone of M_P1 plus one throwaway commit. That commit changes only reweight
pins: pv-ladder's tune_v1 and nuwro lines, and RSN's four reweights, each pointed at a synthetic file. The nine bound
files are unchanged, and the bound launcher runs unmodified in its own smoke mode.

**The stubs:**
- `hostname`, `squeue`, `sacct`, `sbatch` and `timeout`;
- the root_6_28 python. Its `rsn_cmodel.py nc` writes the `nc.json` the real code writes. The real NC needs the
  frozen products, which are on the cluster.

**The cases:**
- **`nc` passes:** the clone, the bound shas, the sums equality, P5, the NC check and both gate files;
- **`nc` refuses, writing nothing:**
  - J1 still running, or an `e96data` job queued;
  - a dtn host, or a Slurm job set;
  - J1 FAILED in sacct;
  - the log's rc line missing;
  - a product that differs from its logged sha;
  - `nc.json` or the deploy already there;
  - a bad step name;
- **`nc` STOPs:**
  - the committed sums differ from connect 1's;
  - the NC fails;
  - `nc.json` names a different `rsn_cmodel.py`;
- **`submit` passes:** both launcher smokes, then exactly the two argv above;
- **`submit` refuses:**
  - a gate with the wrong pin;
  - no `nc.json`;
  - a dirty deploy;
  - an `e96data` job queued;
- **`submit` STOPs:**
  - J2's sbatch fails (J3 is not called);
  - J3's sbatch fails (J2's jobid is named).

The smoke found one defect before it was sent: the bound-files loop reused the variable that held J1's product
sha256, so the `nc.json` check compared against the wrong digest and STOPped a passing NC. It is fixed, with the
variable renamed to `psha`.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the J2/J3 connect and its local smoke behaviour.
- **Not citable for:** J2 or J3 having run, the NC's result, or any reading.

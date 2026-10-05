# Phase A2, Part 4 — resources

Scope §1, "use the resources efficiently": what is left, what the historical comparison actually
cost, and what the queue will charge a Phase C/D campaign in wall-clock.

Every number below is followed by the command that produced it. Raw captures are under
`receipts/resources_raw/`; each capture file begins with the literal command line, a UTC timestamp
and the login node that answered. **All MEASURED** unless tagged otherwise.

A caution that applies throughout: `ssh` here multiplexes onto one login node, so a node-local read
reflects that node. The allocation and quota figures below are cluster-global (Iris/Slurm/filesystem
services), so this does not affect them.

## 1. Allocation balances

```
$ iris                     # 2026-09-22T12:22:21Z, login16
Project      Charged(user)    Allocated(user)     Charged    Allocated
m3246               1701.6            10000.0     16534.2      20000.0
m3246_g              367.2            90000.0    120693.0     180000.0
```

| Account | Project charged | Project allocated | **Project remaining** | Joseph's own charge / his allocated |
|---|---:|---:|---:|---:|
| `m3246` (CPU) | 16,534.2 | 20,000.0 | **3,465.8 (17.3 %)** | 1,701.6 / 10,000.0 |
| `m3246_g` (GPU) | 120,693.0 | 180,000.0 | **59,307.0 (32.9 %)** | 367.2 / 90,000.0 |

`iris project m3246_g` errors with "project not found"; `m3246_g` is reported as a row of
`iris project m3246`, which is why the table above comes from the bare `iris` call.

**The binding constraint is CPU, not GPU.** `m3246` has 17.3 % left against `m3246_g`'s 32.9 %, and
a `gpu_shared` job charges CPU cores as well (§3). Joseph personally has used 4.1 % of his GPU
sub-allocation, so the project-level pool — shared with other users — is what to watch.

Units are as Iris reports them (Perlmutter node-hours). **INFERRED:** the exact charge formula
mapping a `gpu_shared` task to Iris units was not re-derived here, so §3's device-hours should not
be subtracted directly from the 59,307.0 above; the Iris user total (367.2) is the figure that
already includes the historical campaign.

Fairshare, for queue-priority context:

```
$ sshare -l -A m3246,m3246_g -u josephrb     # 2026-09-22T12:22:39Z
m3246     josephrb  FairShare 0.243257
m3246_g   josephrb  FairShare 0.119573
```

## 2. Storage

```
$ myquota                  # 2026-09-22T12:22:38Z
FILESYSTEM  SPACE_USED  SPACE_QUOTA  SPACE_PCT  INODE_USED  INODE_QUOTA  INODE_PCT
      home    20.30GiB     40.00GiB      50.8%     231.90K        1.00M      23.2%
  pscratch    16.34TiB     20.00TiB      81.7%     482.30K       10.00M       4.8%

$ cfsquota m3246           # 2026-09-22T12:22:39Z
Project    Usage(GB)   Quota(GB)  Percent      Inode Usage   Inode Quota  Percent
m3246          81061      102400       79         39302304      75000000       52
```

| Filesystem | Used | Quota | **Percent** | Inodes |
|---|---:|---:|---:|---:|
| `/pscratch/sd/j/josephrb` | 16.34 TiB | 20.00 TiB | **81.7 %** | 4.8 % |
| `/global/cfs/cdirs/m3246` | 81,061 GB | 102,400 GB | **79 %** | 52 % |
| `$HOME` | 20.30 GiB | 40.00 GiB | 50.8 % | 23.2 % |

(The rejected draft's "~80 %" was right about pscratch but carried no command; `myquota` is the
command.)

**Space is the tighter of the two limits, inodes are not.** ~3.7 TiB free on pscratch and ~21 TB on
CFS. A Phase C/D campaign that writes per-run checkpoints at the historical rate should budget
explicitly and purge superseded arms; pscratch is also subject to NERSC purge policy, so anything
that must survive belongs on CFS.

## 3. What the historical comparison actually cost

This is the number the rejected draft got wrong (it reported 12.7 GPU-h against handoffs citing
hundreds). Both figures were reachable because **two different units were in play.**

Job-id population, built so it cannot silently under-count:

1. every `JobId=` in all **56** `allocation.txt` files under `/pscratch/sd/j/josephrb/campaign-20260920/`
   (these are `scontrol show job` captures written *by the runs themselves*, so they record what ran,
   not what a plan intended), plus
2. every id in the campaign's own `campaign_jobs.txt`.

Union: **70 distinct ids.** Note that `scontrol` writes an array task's *unique numeric* id, while
`sacct` reports it as `<arrayjob>_<task>`; the 70 ids resolve onto 70 `sacct` rows — 56 array tasks
from 3 array jobs plus 14 single jobs. A first pass without `--starttime` silently returned a
different 70-row set (`sacct` defaults to a today-only window), which is why the query below pins
the window explicitly.

```
$ sacct -j <70 ids> -X --starttime 2026-09-10T00:00:00 --endtime 2026-09-23T23:59:59 \
        --format=JobID,JobName,State,ElapsedRaw,NNodes,Partition,QOS,AllocTRES -P
        # raw: receipts/resources_raw/sacct_campaign_20260920.psv
```

| Class | Jobs | GPU device-hours | CPU core-hours | Wall-hours |
|---|---:|---:|---:|---:|
| GPU (`gpu_shared`) | 56 | **32.8** | 1,051.0 | 32.8 |
| CPU (`shared`) | 14 | 0.0 | 21.3 | 0.8 |
| **Total** | **70** | **32.8** | **1,072.3** | 33.6 |

States: 57 COMPLETED, 10 CANCELLED, 3 FAILED. GPU task elapsed: min 907 s, median 1,922 s,
max 5,303 s. Every GPU task held exactly 1 A100 and 32 CPU cores.

**Reconciliation of the two figures.** 32.8 is GPU **device**-hours (`gres/gpu × elapsed`).
1,051.0 is CPU core-hours on those same GPU jobs, because `gpu_shared` allocated 32 cores per task —
that is the "hundreds" the handoffs referred to. Both describe the same 70 jobs. The comparison's
own pre-run projection, `COST_RECALIBRATION2-20260919.json` →
`final_comparison_gpu_hours_by_seeds`, put 8 seeds at **34.2 GPU-h**; the measured 32.8 for the
*entire* campaign (tuning + pilot + final) sits just under it. The projection was good.

**Planning consequence:** a PET arm costs ~0.5 h of one A100 but is billed 32 cores alongside it.
Phase C's four feature arms × 8 seeds ≈ 64 runs ≈ 35–40 GPU device-hours and ~1,200 CPU core-hours —
affordable against §1, but the CPU side is what draws down the scarcer account.

## 4. Queue depth and start latency

Live depth:

```
$ date -u; squeue -q gpu_shared -t PENDING --noheader | wc -l   # 2026-09-22T15:14:57Z
gpu_shared  PENDING 1428   RUNNING 197
shared      PENDING 1435
```

Realised start latency, from Joseph's own 809 jobs since 2026-09-08 (`Start − Submit`):

```
$ sacct -u josephrb -X --starttime 2026-09-08 --endtime now \
        --format=JobID,QOS,Submit,Start,State,ElapsedRaw,AllocTRES -P
        # raw: receipts/resources_raw/sacct_latency_josephrb.psv
```

| QOS | n | median | p90 | max |
|---|---:|---:|---:|---:|
| **`gpu_shared`** | 433 | **4 h 6 m** | **9 h 9 m** | 33 h 8 m |
| `shared` (CPU) | 313 | 48 m | 8 h 40 m | 33 h 30 m |
| `gpu_debug` | 6 | 4 m 27 s | 17 m 26 s | 17 m 26 s |
| `debug` | 19 | 1 m 34 s | 1 h 4 m | 1 h 36 m |

**This, not the allocation, is the real constraint on Phase C/D.** A `gpu_shared` PET run takes
~0.5 h and waits ~4 h at the median, ~9 h at p90 — the queue costs 8–18× the compute. Three
implications:

1. **Batch.** One job that runs several arms sequentially beats several jobs; each extra submission
   buys another ~4 h expected wait.
2. **Use `gpu_debug` for probes.** Median 4.5 min against 4.1 h, for anything that fits its limits.
3. **Size wall-clock generously and checkpoint.** A requeue is another full wait, so a job that
   dies at the limit is far more expensive than one that over-requested.

## 5. This task's own jobs

Recorded in `resources-A2.tsv`. Six jobs across the A2 delegates — 4 COMPLETED, 1 FAILED,
1 CANCELLED before it started — all CPU on `m3246`, all read-only. **No training was launched.**
Cumulative: **0 GPU-hours, 45.80 CPU core-hours.**

Confirmed that these are the only A2 jobs: over `sacct -u josephrb --starttime 2026-09-21`, the
`pet-a2` / `pet-a2-mask` names account for 6 jobs; `pa1-*` and `runtime-*` belong to delegate A1 and
`pet-b1-*` to delegate B1.

`58742132` FAILED (exit 3:0) at 1 m 46 s: NumPy's optional SVE probe runs `lscpu` at
`numpy.testing` import time, which TensorFlow reaches via scipy, and the OI-136 launch guard refuses
a child it cannot prove keeps its own Python launches guarded. Fixed in commit `31347723` by
answering the probe offline; the rerun `58742133` COMPLETED.

**§4's recommendation was then tested on this task's own last job.** `58752537` was submitted to
`shared` and sat PENDING on `Resources` for 10 minutes; it was cancelled (by its own submitter) and
resubmitted unchanged except for `--qos=debug` as `58752745`, which **started after 125 s and
finished in 90 s.** One flag turned a job of unknown remaining wait into one that was done inside
four minutes. Small read-only probes belong in `debug`.

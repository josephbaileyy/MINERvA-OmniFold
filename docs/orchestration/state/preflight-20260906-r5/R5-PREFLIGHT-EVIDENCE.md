# R5 accounting evidence packet — measured 2026-09-06 on Perlmutter

**Produced by** session `preflight [e11e6d]`, worktree `wt-z-spec`, base `f98cce8a` (Z spec rev. 6).
**Scope** read-only. No job submitted, no credential changed, no unattended execution configured, no
frozen checkout modified, no LIVE-STATE regenerated. Nothing committed.
**Cluster** Perlmutter, login31 pinned, user `josephrb`, accounts `m3246` / `m3246_g`.
**Raw evidence preserved** at `$SCRATCHPAD/r5-evidence/` (local) and `~/r5-evidence-20260906/` (cluster).


> **⚠ THE R5 RECEIPT DESCRIBED IN §1 IS INCOMPLETE AND IS NOT ADMISSION EVIDENCE.**
> It omits requeue expenditure: it reports `0.0016667` CPU task-hours where the requeue-inclusive
> reading is `12.5903`. Joseph ruled on 2026-09-06 that it be labelled incomplete and **not presented
> as valid admission evidence**, so it is deliberately not at
> `docs/orchestration/state/r5-meter-receipt.json`. Read §2 before quoting any figure from §1, and see
> this directory's `README.md`. The receipt bytes themselves are unaltered — the label is here and in
> the filename, never inside the measurement.

---

## 0. Headline

1. **The first genuine `r5_meter` receipt exists and is measured, not recalled.** §5.6's
   "`r5-meter-receipt.json` DOES NOT EXIST" is now discharged as an evidence question.
2. **But the receipt understates real consumption by ~7,500x**, for a reason that is a property of the
   landed implementation, not of the cluster. Measured, both ways, below.
3. **`PM-2` is DISCHARGED, and the spec's premise for it is false.** A contemporaneous digest of G's
   `combined_source` *is* recorded in the tree, in G's own build receipt, and it matches today's bytes.
4. **`PM-3` availability is discharged**; `PM-1`, `PM-4`, `PM-5` are blocked on a ROOT runtime that does
   not load on a login node.
5. **A 7-day full-system outage sits inside the R5 window**, and **`sacct` has a 30-day query ceiling**
   that puts a dated deadline on the final receipt.

---

## 1. The R5 receipt — measured

Run with the landed implementation, byte-identical to `HEAD:docs/orchestration/r5_meter.py`
(sha256 `3ea13eb99645a30853bffb0c1191298d188f566aaef3c7f7e52df4d2cb4a3e8d`, verified on both sides).
Executed from `~/r5-evidence-20260906/`, never from the deployed checkout.

| field | value |
|---|---|
| `measured_at_utc` | `2026-09-06T08:54:17.695700Z` |
| `measured_on_host` | `login31` |
| `source.kind` | `sacct` (live), argv exactly `_sacct_argv()` |
| `source.raw_sha256` | `e91b2f1122309464b8d09b01c112a0a0aa8104f8c2d452c3b1aa5c3dac0ba076` |
| `t0_utc` | `2026-09-02T13:44:27Z` — the original t0, `9ce59a59` |
| `stop_date_utc` | `2026-09-30T00:00:00Z` |
| **spend GPU** | **`0.0` task-hours** |
| **spend CPU** | **`0.0016666…` task-hours** (6 s) |
| `task_count` | `1` — `["57712764"]`, `by_state {"REQUEUED": 1}` |
| `fired` | `date:false  gpu:false  cpu:false  any:false` |
| **headroom GPU** | **`500.0`** |
| **headroom CPU** | **`499.99833…`** |

**Triangulation, because a single query is not evidence of itself.** I captured the raw dump, ran the
meter live against `sacct`, captured a second dump, and ran the meter again from the preserved first
dump. `dump1` and `dump2` are byte-identical (`cmp`), both hash to `e91b2f11…`, and that is also the
`raw_sha256` the live receipt independently recorded. The from-file receipt reports the same spend to
the last digit. The parse is therefore reproducible from preserved input, which is what makes the
receipt auditable rather than merely asserted.

**So §5.6's own question — "whether real Perlmutter `sacct` output parses cleanly through it is
unmeasured" — is answered: it parses cleanly.** That answer is narrower than it looks; see §2.

---

## 2. ⚠ The receipt is an undercount, and the size of the undercount is measured

The only task in the R5 window is `57712764`, a self-requeueing `cron`-partition waker
(`WAKER_STATE_DIR=/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/waker`).
`scontrol` reports **`Restarts=1990`**. It fires about every five minutes.

`sacct` without `--duplicates` returns only the most recent instance of a requeued job id. The meter's
`_sacct_argv()` (`r5_meter.py:380-392`) does not pass `--duplicates`. So the meter saw one 6-second row
and charged 6 seconds.

**The same window, same user, same fields, with `--duplicates`:**

| | instances | elapsed | R5 CPU task-hours |
|---|---:|---:|---:|
| what the meter metered | 1 | 6 s | **`0.00167`** |
| what actually ran post-t0 | **953** | 45,325 s | **`12.5903`** |

Distribution of the 953: min `0 s`, median `9 s`, max **`31,063 s` (8 h 37 m)**, mean `47.6 s`;
states `950 REQUEUED`, `2 NODE_FAIL`, `1 PENDING`. **The total is dominated by one hung instance** that
started `2026-09-03T16:15:20` and ran 8 h 37 m; the other 948 sum to ~2.96 task-hours (~11 s each).

**Two consequences, and the second is the one that needs a ruling.**

- **`--duplicates` is not a drop-in fix.** Fed the 8-field `--duplicates` dump, the meter *fails*:
  `R5 measurement failed: line 2: conflicting rows for task identity 57712764`. `_parse_sacct_dump`
  keys on job id alone and raises on rows that share an id but differ in start
  (`r5_meter.py`, `_parse_sacct_dump`). The identity model, not the query flag, is what needs changing.
- **This is a specification question, not only a bug.** The meter's own `UNIT` string says "over
  distinct task identities". Whether 953 requeues of one job id are one identity or 953 is exactly what
  R5 §3 speaks to when it says failed and retried tasks count in full — and the spec quotes that as
  including `FAILED`, `CANCELLED` and `TIMEOUT`. Under the implementation the answer is `0.00167`;
  under a plain reading of R5 §3 it is `12.59`. **I am not adjudicating that. It is the spec author's
  and Joseph's.** Both numbers are above, measured, so the ruling can be made against evidence.

**Note for the record, without overclaiming.** §5.6 states "No unattended execution is configured
(`ACCEPTANCE-20260905`)". A self-requeueing scheduled job with 1,990 restarts is running and is
charging R5. Whether that contradicts `ACCEPTANCE-20260905` depends on whether that record means
*campaign* execution specifically; I did not read it and am not interpreting it. I did not touch the
job.

---

## 3. Ceiling headroom vs. outstanding reservations — kept separate

Three different quantities, which §5.2a is right to insist are not interchangeable.

| quantity | GPU | CPU | what it is |
|---|---:|---:|---|
| **R5 ceiling** | 500.0 | 500.0 | a prohibition and an accounting boundary, per `RZ(iv)` — not a budget |
| **metered spend** (as the meter reports) | 0.0 | 0.00167 | actual `ElapsedRaw`, deduped by job id |
| **spend on a full-requeue reading** | 0.0 | 12.5903 | same window with `--duplicates` |
| **ceiling headroom** (meter's reading) | **500.0** | **499.998** | ceiling − metered spend |
| **ceiling headroom** (full-requeue reading) | **500.0** | **487.41** | ceiling − 12.59 |
| **outstanding reservation** | 0.0 | **up to 12.0** | the one PENDING task, below |

**The outstanding reservation is one queued task, not a campaign.** `57712764`, `JobState=PENDING`,
`Reason=BeginTime`, `Partition=cron`, `NumNodes=1`, `NumCPUs=1`, `TimeLimit=12:00:00`,
`StartTime=2026-09-06T09:00:00`. Its wall request reserves up to **12.0 CPU task-hours**; empirically it
will charge ~9 s. **A reservation is not a charge and not a floor on spend** — R5 meters actual elapsed.

**There are no outstanding Z-campaign reservations.** `squeue --user josephrb` returns exactly one job,
the waker. Nothing of a Z campaign is queued, running, or reserved.

**Three columns the census must not merge**, since the brief asks for the distinction:
- **operation runtime** — how long the science step takes (e.g. P4 stages 3-6 step `.1`: `00:47:58`);
- **Slurm allocation time** — how long the allocation was held (that step's parent: `03:00:03`);
- **R5 metered task-hours** — `ElapsedRaw` per task identity, which follows the *allocation*, not the
  operation. §5.2a is confirmed measured, below.

---

## 4. Historical task accounting — the cuts requested

All from `sacct`, allocation-level (`-X`) unless a step is named. `Timelimit` is the request;
`ElapsedRaw` is the charge.

### 4.1 §5.2a confirmed by direct measurement — this is the decisive row

| row | job | state | ElapsedRaw | Timelimit | partition | R5 task-h |
|---|---|---|---:|---|---|---:|
| parent | `57128458` `claude-hold` | **TIMEOUT** | **10,803 s** | `03:00:00` | `urgent_milan_ss11` (CPU) | **3.0008** |
| step | `57128458.1` `bash` | COMPLETED | 2,878 s = **`00:47:58`** | — | — | 0.7994 |
| step | `57128458.0` `bash` | FAILED | 6 s | — | — | — |

**`ElapsedRaw = 10,803 s` exceeds the `10,800 s` wall request by 3 seconds.** That is a direct
refutation of "the metered cost is the wall request": a wall request cannot be exceeded, an actual
elapsed can. The parent is literally named `claude-hold`, and the spec's reading — that the `3.00`
came from a hold that stayed allocated to timeout, not from the request — is confirmed on the
scheduler's own record. The step's `00:47:58` matches the spec exactly.

### 4.2 The two assemblies — `unmeasured` becomes a measured upper bound

| job | name | state | ElapsedRaw | Timelimit | partition | R5 task-h |
|---|---|---|---:|---|---|---:|
| `56429334` | `j28_adopt_5d` | COMPLETED | **1,883 s** | `04:00:00` | `shared_milan_ss11` (CPU) | **0.5231** |

The 4-hour figure §5.2 carries as `PROPOSED, UNVERIFIED` was a request. **The actual is 0.5231 CPU
task-hours for all four operations of that launcher** — 13% of the proposed reservation. Since Z's two
assemblies are a *subset* of those four operations and all four completed within the one job, **0.5231
CPU task-hours is a measured upper bound on the pair**. That is strictly better than the `4.0`
placeholder and better than `unmeasured`. It is an upper bound on the two *together with* the two
operations that are not Z's, so it does not license a point estimate.

### 4.3 The statistical+ML combine — still unmeasured, and now for a stronger reason

No job named `budget5d` or `combine_5d_budget` exists anywhere in retained accounting
(2026-07-01 → now, 3,994 allocation rows, complete coverage verified). The only adjacent name is the
4D analogue:

| job | name | state | ElapsedRaw | Timelimit |
|---|---|---|---:|---|
| `55969166` | `budget4dCc` | **CANCELLED** | **0 s** | `02:00:00` |

**The 4D analogue was cancelled before it started.** So there is not even a cross-dimensional prior for
the combine. Your `RUNS.tsv` grep returning 0 rows is corroborated by the scheduler: the combine has
never run in any dimension. **`unmeasured` is correct and should stay.** Its partition is therefore also
unmeasured — I cannot confirm your CPU assumption from accounting, only from the launcher.

### 4.4 `det5dBKG` — min/median/max/n and partition, and the distribution warning was justified

**Array `57753244`** (the tree's cited basis) — partition **`shared_gpu_ss11`, GPU, `gres/gpu:a100=1`**,
`Timelimit=04:00:00`:

| n | min | median | max | sum |
|---:|---:|---:|---:|---:|
| **19** | **2,511 s** (41.85 min) | **2,605 s** (43.42 min) | **2,730 s** (45.50 min) | 49,542 s = **13.7617 GPU task-h** |

Mean 43.46 min, matching the tree's 43.5. Min/max match the tree's 41.9 / 45.5. **It is GPU, not CPU.**

**Your warning about unlike distributions was exactly right, and the aggregate is a trap.** There are
**eight** `det5dBKG` array ids in retained history, 126 tasks, 57.87 GPU task-hours total — but they are
two populations:

| array | n | min | median | max | reading |
|---|---:|---:|---:|---:|---|
| `55894759` | 19 | 10 s | 2,658 s | 3,268 s | full-length |
| `57484989` | 19 | 2,555 s | 2,672 s | 2,904 s | full-length |
| `57527870` | 19 | 2,560 s | 2,615 s | 2,736 s | full-length |
| `57753244` | 19 | 2,511 s | 2,605 s | 2,730 s | full-length (the cited one) |
| `57481857` | 19 | 15 s | 20 s | 75 s | **aborted** |
| `57526064` | 19 | 4 s | 7 s | 9 s | **aborted** |
| `57742559` | 2 | 0 s | 0 s | 15 s | **aborted** |
| `55891346` | 10 | 0 s | 2,072 s | 2,734 s | partial |

The 126-task mean is **27.56 min** — a number that describes no run that ever happened. **Do not quote
it.** The four full-length arrays agree closely (medians 2,605–2,672 s), which is the real corroboration
for the per-replica basis. Separately: **three of eight array launches produced nothing**, and under
R5 §3 their elapsed still counts. That is a campaign risk multiplier the census may want, not a cost.

### 4.5 Other named jobs

| job | name | state | ElapsedRaw | Timelimit | partition | R5 task-h |
|---|---|---|---:|---|---|---:|
| `56720356` | `adopt5d_stamped` — **G's build** | COMPLETED | 320 s | `03:00:00` | `shared_milan_ss11` CPU | **0.0889** |
| `56693207` | `readopt5d_footing` | COMPLETED | 773 s | `06:00:00` | CPU | 0.2147 |
| `56695130` | `readopt5d_hash` | COMPLETED | 97 s | `02:00:00` | CPU | 0.0269 |
| `57266000_0` | `g5dotrain` — OI-136 | **FAILED** | 11,332 s | `08:00:00` | `shared_gpu_ss11` A100 | **3.1478** |
| `56847059_*` | `g6_ml_traj` | COMPLETED | ~833 s each | `04:00:00` | `shared_gpu_ss11` A100 | ~0.231 each |
| `55379222` | `adopt5d` | CANCELLED | 0 s | `01:00:00` | CPU | 0 |

**G's entire build lineage cost 1,190 s = 0.3306 CPU task-hours.** OI-136's `3 h 08 m` of A100 is
confirmed exactly (11,332 s = 3 h 08 m 52 s) and, being `FAILED`, counts in full under R5 §3.

---

## 5. Maintenance and other reservations

**A full-system outage sits inside the R5 window.**

| reservation | window (site-local PDT) | window (UTC) | nodes | flags | state |
|---|---|---|---:|---|---|
| **`maintenance_20260916`** | 2026-09-16 06:00 → 2026-09-23 06:00 | **2026-09-16T13:00Z → 2026-09-23T13:00Z** | **5,248** | `MAINT,IGNORE_JOBS,SPEC_NODES` | INACTIVE (scheduled) |

7 days, and the node list spans the CPU ranges, the `nid8xxx` GPU ranges and the pod — effectively the
whole machine. `IGNORE_JOBS` means overlapping work will not run.

**The R5 window arithmetic, measured rather than recalled** (at `2026-09-06T09:10Z`):

- R5 stop `2026-09-30T00:00:00Z` is **23 d 14 h 50 m** away.
- The outage removes **7 d 00 h** from inside that.
- **Usable scheduling window before the R5 date backstop: ≈ 16 d 15 h.**

Standing root reservations `debug` and `pod` are not outages for us. `zatom2_res_1`, `lcarch_gpu`,
`lcarch_gpu2`, `_CAP_aigs_hist`, `_CAP_spectral_function`, `imgap`, `Gd_DR`, `containers` are other
projects' reservations (accounts `m5008_g`, `m5381_g`, `e3sm_g`, `m4522`, `m342`, `m4547`, `ntrain5`) —
they reduce machine-wide availability but reserve nothing of ours.

**None of these is an R5 reservation.** R5's ceilings are an accounting boundary; Slurm reservations are
a scheduling object. They are different things and the census should not net them against each other.

---

## 6. ⚠ A dated deadline on the meter itself — new, and not in §5.6

**`sacct` on Perlmutter refuses a query wider than 30 days.** Measured by bisection: 30 d accepted,
31 d rejected with `sacct: error: Too wide of a date range in query`. The limit is on **span**, not
lookback — a 29-day window 67 days in the past succeeds. A `-j <jobid>` query bypasses it; `--name=`
does not.

`_sacct_argv()` queries `--starttime <t0> --endtime now`. That span grows every day.

- t0 `2026-09-02T13:44:27Z` + 30 d = **`2026-10-02T13:44:27Z`**.
- R5's stop is `2026-09-30T00:00:00Z`.
- **The meter can measure the complete R5 window only until 2026-10-02T13:44Z — 2 d 10 h after the
  stop.** After that the live query fails, and since admission is fail-closed, it fails closed.

The window is sufficient for the campaign, but the final full-window receipt has a deadline, and the
implementation should either chunk the range or archive dumps. Worth a line in §5.6.

---

## 7. `PM-1` – `PM-5`: what a bounded read settled and what it did not

All four named artifacts are **present** under `MNV_DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold`:

| artifact | size | mtime (UTC) | note |
|---|---:|---|---|
| **G** | 892,170,881 B | 2026-08-12T05:43:34Z | sha256 **`4f168e83…`** — **verified today, matches the spec** |
| **combined_source** | 41,436,632,945 B | 2026-07-14T20:59:17Z | sha256 **`9f7b2f55…`** — measured today |
| **S** | 42,326,607,877 B | 2026-08-16T23:10:24Z | byte count matches the spec exactly |
| `std_component_manifest.json` | 9,181 B | 2026-08-29T20:56:08Z | |

Exactly **one** file named `uq_universe_5d_covariance_combined_bkgaware.root` exists under the data
root, so the receipt's bare filename resolves unambiguously today.

| check | status | evidence / what it needs |
|---|---|---|
| **`PM-2`** G's `combined_source` sha256 | ✅ **DISCHARGED** | §8 — and better than a present-day read |
| **`PM-3`** availability of the ten endpoints | ✅ **DISCHARGED** | all ten present, §7.1 |
| **`PM-3`** grid/footing compatibility | ⛔ **BLOCKED** | needs ROOT |
| **`PM-1`** nine-vs-five weight-only band census on G's `combined_source` | ⛔ **BLOCKED** | needs ROOT |
| **`PM-4`** G's mask digest and row-order digest | ⛔ **BLOCKED** | needs ROOT |
| **`PM-5`** `V`/`R`/`A` partition against G's own band inventory | ⛔ **BLOCKED** | needs ROOT |

**Why the four are blocked, precisely.** They require opening a ROOT file and reading named objects.
On the login node, `uproot` is **not installed** in either `/usr/bin/python3.11` or the project env,
and PyROOT from `/global/u2/j/josephrb/.conda/envs/root_6_28` **segfaults on import**
(`cling::CIFactory::createCI(): cannot extract standard library include paths` → `Error in
modulemap.overlay!` → segmentation violation). It needs the campaign environment the launchers set up,
not a bare interpreter. **What would unblock them, cheaply and without compute:** a `uproot` install in
a user venv, or an interactive session with the campaign env. Reading a TKey list is a header read, not
a scan — it does not require reading the 41 GB. **I did not install anything**, because that changes the
environment rather than reading it, and that is a decision for you or Joseph.

### 7.1 `PM-3` availability — discharged

All ten selection-complete endpoints are present in `nd-unfolding/uq_5d/universe_sweep_bkgaware/`,
the `bkgaware` family matching G's lineage, each ~480 KB, **all dated 2026-07-14**:

`5d_xsec_MEFHC_5iter_lgbm_uni_full_{BeamAngleX,BeamAngleY,MuonResolution,Muon_Energy_MINERvA,Muon_Energy_MINOS}_{0,1}.root`

**A trap worth naming:** a *second*, non-bkgaware set of the same ten filenames exists in
`universe_sweep/`, dated 2026-06-12. Wrong family. Any read must pin the directory, not the filename.

**Corroboration for §8:** these ten endpoints and `combined_source` share the 2026-07-14 build date —
the stage-2 combine was made from the stage-1 sweep that same day, which is what the mtimes show.

**A filename-level census, offered as an observation and not as `PM-1` or `PM-5`:** the
`universe_sweep_bkgaware` directory holds **44 distinct band names × 2 endpoints = 88 files**. The list
includes `MinosEfficiency` — the disputed sixth lateral from
`nd-unfolding/pet_lateral_correction.py:42-43` — alongside the five `p4_lib.BANDS`. S's manifest records
**45** `all_syst_bands`; the stage-1 sweep carries 44. **That is a filename census of the stage-1
inputs, not G's own inventory**, so it does not discharge `PM-5`; it only says a discrepancy is worth
looking at when ROOT is available.

---

## 8. The historical binding — asked for as a gap, found as a record

**The brief's framing was right in principle and is superseded by evidence: a present-day hash alone
cannot prove the bytes G read on 2026-08-12. But a contemporaneous record exists, and I verified it.**

`nd-unfolding/uq_5d/readopt_20260811_footing/STAMPED_HASH_RECEIPT.slurm-56720356.json` — **committed**
(`d75833ab`), git-tracked, `"job_id": "56720356"` (G's build job),
`"created_at_utc": "2026-08-12T05:46:19+00:00"`. That instant is **exactly the end time of job
`56720356`** as `sacct` independently reports it (`05:40:59 → 05:46:19`). Its `combined_bkgaware` entry
records, contemporaneously:

| field | recorded 2026-08-12 | measured 2026-09-06 | agree? |
|---|---|---|---|
| `path` | `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` — **a full path, not a bare name** | same, unique on the data root | ✅ |
| `sha256` | `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` | `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` | ✅ |
| `size_bytes` | `41436632945` | `41436632945` | ✅ |
| `mtime_ns` | `1784062757000000000` = **2026-07-14T20:59:17Z** | 2026-07-14T20:59:17Z | ✅ |

**Two spec statements are therefore false and should be corrected:**

- §1.1 line 214: "**name only; no digest for it is recorded anywhere in the tree**". A digest *is*
  recorded, with a full path, in G's own build receipt, in the same directory as G.
- §4 row 5: that using `9f7b2f55…` as G's would be "**the substitution `PM-2` exists to prevent**".
  It is not a substitution. G's build receipt records that digest independently, four days before S
  read the file. S's 2026-08-16 manifest is a **second, agreeing measurement**, not the only one — and
  by the front door's own rule, two agreeing statements traced to one origin count once, so the
  independent value here is that they have *different* origins.

**What still is not proven, stated exactly, because this is the part the brief asked to be explicit
about.** The launcher hashes its inputs *after* building both arms: G was written at `05:43:34` and the
receipt was created at `05:46:19`, so the digest was taken ~3 minutes after consumption, inside the same
job. The digest therefore binds the bytes **at 05:46:19**, not by direct observation the bytes **read at
05:40:59–05:43:34**. Closing that last three-minute gap rests on one inference: the same receipt's
`mtime_ns` = 2026-07-14T20:59:17Z shows the file's last write **predates the job's own start**, so it
was not rewritten mid-read.

**That inference is now unusually well supported, and here is the strongest available corroboration.**
Today `ctime == mtime == 2026-07-14T20:59:17Z`. **`ctime` is the load-bearing field**: userspace cannot
set it. `touch -r`, `cp -p`, `rsync --times` and `tar -p` all forge `mtime` while moving `ctime` to the
copy instant. An unchanged `ctime` therefore rules out content writes, `chmod`, `chown`, rename and
relink since 2026-07-14 — 29 days *before* G was built and 54 days before today.

**The residual, which no read from here can close:**

1. `ctime` is filesystem metadata on `/pscratch`, a **purgeable scratch filesystem**. A full restore or
   filesystem migration that reconstructed inode metadata would defeat it. I have no record of such an
   event and no way to exclude one from inside the filesystem.
2. **No historical inode/device record exists**, so nothing proves the path resolved to *this* inode in
   August. Today's inode is `882725779362807937`, `links=1`; there is nothing from 2026-08-12 to
   compare it against.
3. The chain still runs partly **backwards** — from a later digest plus metadata — rather than from an
   observation taken at the moment of the read.

**My reading, offered as a recommendation and not a ruling:** `PM-2` should be marked **DISCHARGED**.
The remaining gap is a 3-minute intra-job window closed by a contemporaneous `mtime` that itself
predates the job, corroborated by an unforgeable `ctime` and by two independently-originated digests
that agree. That is a stronger provenance record than most artifacts in this tree have.

**The minimal record that would close it outright, for Z.** Require Z's producing revision to stamp,
for every input, `path + sha256 + size + mtime_ns + inode + device`, **captured at open time rather than
at job end**. G's receipt gets four of those six and takes them at the wrong instant; that is the whole
of the gap.

---

## 9. `x_cv_reported` — your §3.6a normalizer, confirmed and answered

**Your measurement is confirmed independently.** `nd-unfolding/unified_throw_cov.py:516-517`:

    tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)

On a vector of norm ~1e-37 this collapses to an absolute `1e-12`, exactly as you said. The writer at
`:541-579` persists `C_unified`, `C_blocksum`, `C_cross`, `sqrt_tr_unified`, `sqrt_tr_block`,
`joint_mean_shift_norm`, `fixed_seed_null_checked`, `fixed_seed_null_norm`, `n_throws`,
`estimator_seed`, `draw_seed`, `est_seed_offset_declared`, `est_seed_offset` and the `hJointMeanShift`
TH1D — **and does not write `x_cv_reported`**. It is returned in the dict at `:586` as
`"x_cv_reported": base` and dropped.

**Does anything carry G's reported CV vector or its norm?** From the committed receipt
`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json`, **G's complete key list is 13 keys**:
`centering_convention`, `combined_source`, `fixed_seed_null_norm_checked`, `hCov_combined5d_total_uthrow`,
`hInflation_g`, `joint_mean_shift_norm_checked`, `n_throws_checked`, `sqrt_tr_new`, `sqrt_tr_old`,
`upstream_fixed_seed_null_norm`, `upstream_joint_mean_shift_norm`, `upstream_n_throws`, `uthrow_source`.

**No CV vector and no norm among them. G does not carry it.** That is from a committed receipt's own
enumeration, so it does not depend on the blocked ROOT read.

**What I could not check**, and it is the one place the norm might still live: whether the separate 5D
**central-value** product carries a CV vector on the same 10,694-bin reported mask and row order. That is
a ROOT key read, blocked with `PM-1`/`PM-4`. **Your finding stands on the evidence available: nothing in
G, and nothing this writer emits, carries it** — which makes "persist `x_cv_reported`" a requirement on
Z's contract, not an optional field. If the ROOT runtime is unblocked, one key listing settles the
remaining case.

---

## 10. Boundaries held

No job submitted. No `scancel`, `scontrol update`, or queue modification — the waker was observed only.
No credential created, changed or stored. No unattended execution configured. The deployed checkout
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` was **read only**; the meter was copied to a fresh
`~/r5-evidence-20260906/` and run from there, never from the checkout. No LIVE-STATE regenerated.
Nothing committed to any branch; the `wt-z-spec` worktree is clean.

**One thing I did write on the cluster**, disclosed for completeness: the evidence directory
`~/r5-evidence-20260906/` (raw dumps, two receipts, two digests, the meter copy). It is new, outside
every checkout, and contains only measurements.

**Cost of this errand:** ~0 R5 task-hours. Everything was a login-node read; the only measurable load
was two `sha256sum` reads (41 GB and 892 MB), niced. No allocation was requested and nothing entered a
queue.

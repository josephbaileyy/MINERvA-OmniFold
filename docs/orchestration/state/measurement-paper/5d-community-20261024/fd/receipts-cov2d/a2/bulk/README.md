# COV2D A2, stage 4: the rest of the bulk and G18_C, with the per-label completeness table

**By** the `cov2d` session, 2026-11-07. This is the fourth stage of A2's fixed conditional sequence (COV2D-BINDING-2.md,
"Binding 2, addendum A2", revision 2: **M = `a60547692df5f963e428cdfe4661fc51ab785b7b`**). It follows stage 3
(`../universes/`), the director's rulings on the gate's sacct lag and on G18_L (2026-11-06), and addendum A3, the
pilot-label collision (#836).

**MEASURES:**
- the submission of the 14 jobs after the universe jobs, and of the completion job G18_C, through the bound
  `cov2d_submit.sh` at M;
- each job's end state and charge;
- A3 ruling 1's match evidence for the four FAILED jobs;
- A3 ruling 4's rename;
- A3 ruling 6's per-label completeness table over all 1,572 bulk labels.

**CANNOT AUTHORIZE:** stage 5. A3 ruling 6 lets stage 5 proceed once this record is committed on main; that call is
the director's.

**Result: PASS.**
- **Completeness:** all 1,572 labels pass. Each has exactly one rc-0 walls row and exactly one digest, from one job at
  M with one id, and the bytes in `$O/out/<label>/xsec.root` (read with O_NOATIME) equal that digest. The five
  pilot-collision labels come from G18_C (60912517).
- **The FAILED jobs:** G18_L, G18_Ua, G18_Ba and G18_Ta ended FAILED 1:0, each solely from its expected skips.
- **The cap:** it held at every submission. The total charge of all 27 cov2d attempts is **112.74 node-h of 165.8**.
- **STOPs:** none. The count stays at two.
- **A defect, disclosed below:** my flag watcher was blind for about 8 h. Read back afterwards, nothing would have fired.

## The submissions

Each submission went through one `cov2d_submit.sh` call.
- **Before each one:**
  - every label of the job was stat-listed against `$O/out` (wave connect v2 onward);
  - the gate's total and the independent recompute (`cov2d_cap.py`) were taken on one sacct snapshot;
  - both had to be at most 165.8.
- **After each one:** the next call waited until sacct listed the id.
- **Each connect run:**
  - checked its own digest and its helpers' digests against the reviewed ones;
  - ran the companion test (OK under the login node's Python 3.6.15);
  - found the deploy at M, porcelain 0 and `--ignored` 0, before and after;
  - had its `/dev/shm` files and log removed afterwards, rc 0 each (the `removal-*.log.txt` files).

| connect run | job | id | submitted (UTC) | limit | gate total | recompute total | final state | charge (node-h) |
|---|---|---|---|---|---:|---:|---|---:|
| wave 1 | G18_L | 60895948 | 09:19:07 | 03:20:00 | 81.42 | 81.42 | FAILED | 1.81 |
| wave 1 | G18_Ba | 60895949 | 09:19:12 | 08:06:00 | 89.52 | 89.52 | FAILED | 4.96 |
| wave 1 | G18_Bb | 60895951 | 09:19:27 | 08:06:00 | 97.62 | 97.62 | COMPLETED | 4.78 |
| wave 1 | G18_Bc | 60895953 | 09:19:45 | 08:06:00 | 105.72 | 105.72 | COMPLETED | 4.80 |
| wave 1 | G18_Ta | 60895956 | 09:20:02 | 07:38:00 | 113.36 | 113.36 | FAILED | 4.75 |
| wave 1 | G18_Tb | 60895973 | 09:20:18 | 07:38:00 | 120.99 | 120.99 | COMPLETED | 4.82 |
| wave 1 | G18_Tc | 60895982 | 09:20:33 | 07:38:00 | 128.62 | 128.62 | COMPLETED | 4.89 |
| wave 1 | AR23_L | 60895983 | 09:20:47 | 03:20:00 | 131.96 | 131.96 | COMPLETED | 1.81 |
| wave 1 | AR23_Ba | 60895985 | 09:21:04 | 08:06:00 | 140.06 | 140.06 | COMPLETED | 4.80 |
| wave 1 | AR23_Bb | 60895990 | 09:21:18 | 08:06:00 | 148.16 | 148.16 | COMPLETED | 4.95 |
| wave 1 | AR23_Bc | 60895992 | 09:21:23 | 08:06:00 | 156.26 | 156.26 | COMPLETED | 4.83 |
| wave 1 | AR23_Ta | 60896048 | 09:21:39 | 07:38:00 | 163.89 | 163.89 | COMPLETED | 4.83 |
| wave 2 | AR23_Tb | 60909280 | 15:19:52 | 07:38:00 | 161.73 | 161.73 | COMPLETED | 4.26 |
| wave 3 | AR23_Tc | 60911676 | 16:08:22 | 07:38:00 | 152.88 | 152.88 | COMPLETED | 4.24 |
| complete 1 | G18_C | 60912517 | 16:25:49 | 01:19:00 | 148.50 | 148.50 | COMPLETED | 0.66 |

**Waits.** These were waits, not STOPs (COV2D-AMENDMENT-1.md §5):
- wave 1 ended at AR23_Tb, at 171.52;
- wave 2 ended at AR23_Tc, at 169.37.

Each wave was relaunched without a further go, under the director's standing approval, once a watcher's recompute
said the job fit.

**The connects:**
- **Wave 1:** `connect-wave-29714c36.sh`, the auditor's GO.
- **Waves 2 and 3:** `connect-wave-f20da2d5.sh` (v2). It adds the per-job label listing against `$O/out`, from the
  director's G18_L ruling, item 4, with the auditor's GO.
- **Both wave versions** use `cov2d_cap.py` (`1ce76ea3…`) and `test_cov2d_cap.py` (`7a07c3ac…`).
- **G18_C:** `connect-complete.sh` (`9584dd4a…`), with the auditor's GO.
- **Sims:** `sim.sh` and `sim-complete.sh` are the local simulations the connects were reviewed with.

**Charges.** From `state_after.txt` (sacct at 2026-11-07T01:44:00Z; sacct prints node-local time, UTC−8):
- pre-bulk (pseudo_G18, the pilot, both pseudo_AR23 attempts): 6.89;
- the eight universe jobs of stage 3, all COMPLETED except G18_Ua: 44.67;
- the 15 jobs above: 61.19;
- total: 112.74 node-h.

## The FAILED jobs (A3 ruling 1)

Each of the four ended FAILED 1:0 because `cov2d_job.sbatch:41` skipped labels the pilot had written into `$O/out`.

**The evidence**, all in the `collision/` files:
- the watcher's check at each job's end (`collision/match-<id>.txt`, from `watch2.sh`). This is its final
  version; later runs added only exit modes, and its match logic was the same in every run;
- connect-complete's step 1 re-check (`complete/connect-complete-1.log.txt`, "CHECK" blocks).

Each check found:
- sacct ExitCode 1:0;
- every srun step COMPLETED 0:0;
- every walls row rc 0;
- no `[cov2d] <label> rc=` run-failure line;
- an end line with rc=1;
- the log's skip set equal to the job's expected labels;
- walls rows plus skips equal to the job's runs-table rows.

| job | id | skipped (expected = logged) | steps | walls + skips = rows |
|---|---|---|---:|---|
| G18_L | 60895948 | L_G18_BeamAngleX_0, X_G18 | 9 | 9 + 2 = 11 |
| G18_Ua | 60895562 | U_G18_Flux_0 | 43 | 43 + 1 = 44 |
| G18_Ba | 60895949 | B_G18_001 | 99 | 99 + 1 = 100 |
| G18_Ta | 60895956 | T_G18_5720000 | 99 | 99 + 1 = 100 |

**Diagnosis inputs:**
- `collision/g18l-diagnosis.txt`: G18_L's log `3f06fb72…`, check JSON `5516cd04…` and materialization JSON `447f0792…`.
- `collision/pilot-labels-stat.txt`: the pilot's five outputs.
- `collision/listing-130406Z.txt`: the stat-only listing of all 1,572 bulk labels at 13:04:06Z that A3 cites.
- The `g18l-q*.sh` files: the read-only scripts that produced them.

## The rename and G18_C (A3 rulings 3 and 4)

connect-complete ran in MODE fresh: G18_C was not in `submissions.log`, and none of its four state files existed.

1. **The rows.** It built `runs_G18C.tsv` from the five `runs_G18.tsv` rows verbatim.
   - Lane 1: L 1678 + X 866 + B 920 = 3464 s.
   - Lane 2: U 1150 + T 866 = 2016 s.
   - Limit: `limit_of(3464)` = 01:19:00.
2. **The rename.** Before renaming, each `$O/out/<label>/xsec.root`'s O_NOATIME sha256 matched its
   `SHA256SUMS.pilot.*` line. Then `mv -n` moved each label to `<label>.pilot-60857636`, rc 0, at 16:25:40–42Z.
3. **The ledger.** After each move it re-read the stat and the O_NOATIME sha256 at the new path and required both to
   be unchanged (stat_match=yes). The B9-form ledger is `complete/renames-pilot-60857636.tsv` (`71b18cae…`, fetched
   from `$O`): five rows, each mapping the pilot line to its new path.

| label | pilot sha256 (before = after the move) | G18_C's bulk sha256 now at the old path |
|---|---|---|
| L_G18_BeamAngleX_0 | f04eafde… | 4246aace… |
| X_G18 | 7575b7ce… | 2587ef99… |
| B_G18_001 | d6efdbda… | 47fc4f64… |
| U_G18_Flux_0 | db669e81… | f27d43fb… |
| T_G18_5720000 | 19804492… | 93a4e682… |

**The bytes differ**, as A3 ruling 2 expects: the pilot ran X_G18 and U_G18_Flux_0 at 64 CPUs, and the bulk runs
every label in its own configuration.

**Installed:** the G18C tables and `$O/pseudo/G18C -> G18`. The label listing found none of the five in `$O/out`.

**The submission.** The gate and the recompute agreed on 148.50. The job was submitted at 16:25:49Z and COMPLETED
0:0, charging 0.66 node-h. The pilot readout was not rerun.

## The completeness table (A3 ruling 6)

`completeness/completeness.py` (`3d2b4857…`) runs read-only on a login node under `$PY310` and writes only to stdout.
It produced `completeness/completeness.tsv` (`401e9d97…`) at 01:44Z on 2026-11-07, with its summary in
`completeness/completeness.err.txt`: labels=1572, pass=1572, fail=0, disk=checked.

**For every label of `runs_G18.tsv` and `runs_AR23.tsv`, it requires:**
- exactly one rc-0 walls row, and no other walls row;
- exactly one `SHA256SUMS` line;
- both from the same job;
- that job listed in `submissions.log` at M with exactly one id;
- with `--disk`: `cov2d_jobs.noatime_sha256` of `$O/out/<label>/xsec.root` equal to the digest.

**For the five `runs_G18C.tsv` labels**, that job must be G18_C, and the table cites A3 rulings 2–4 and the ledger.

**Per job** (job, id, sacct, labels): every label appears once, in its planned job, except the five, which are in
G18_C.
- **G18:**
  - G18_Ua 43, Ub 44, Uc 44, Ud 43;
  - G18_L 9;
  - G18_Ba 99, Bb 100, Bc 100;
  - G18_Ta 99, Tb 100, Tc 100;
  - G18_C 5.
- **AR23:**
  - Ua, Ub, Uc 44 each, Ud 43;
  - L 11;
  - Ba, Bb, Bc 100 each;
  - Ta, Tb, Tc 100 each.

A dry run at 16:28Z on 2026-11-06, while jobs were still running, passed 1,316 labels. It failed exactly the 256
labels not yet run, and no other kind of failure appeared.

## The cap projection and the flag triggers (and their blind window)

**The projection.** At the director's request (2026-11-06), `projection/proj.py` (`ed956646…`) projected the final
charge from the measured wall/estimate ratio of each truth and class:
- **Inputs:** the snapshots `out.txt` (15:22:02Z) and `out-1524.txt` (15:24:51Z).
- **Outputs:** `proj.txt` and `proj-1524.txt`.
- **Projection:** point 114.67 (low 109.94, p90 117.63, high 130.62); 114.82 on the second snapshot.
- **Actual:** 112.74.
- **Ruling:** the director ruled no cap change.

**The triggers** (the director, 2026-11-06), in `projection/flags.py`:
- **END-SLIP:** a job more than 1 h past its p90 end. It messages the director at once.
- **OVER-1.3MEAN:** a run, finishing after the 15:22:02Z snapshot, above 1.3× its class mean in that snapshot. It
  messages the director at once.
- **RUN-OVER-MAX:** a run over the re-baselined class max. Firings are batched.

**The batched firings.** The 15:24 firing of seven runs, a slowdown shared across jobs 15:05–15:24Z, was reported
when it happened. After re-baselining, 3 runs fired RUN-OVER-MAX against the 15:24 maxes:
- T_G18_5720080, 0.999;
- T_AR23_5730064, 0.934;
- G18_C's X_G18, 0.853, under 1.3× its class mean of 0.868.

### The defect

From G18_C's first walls row (the first cycle after 16:42:29Z) until the watch ended (00:56Z, about 8 h), the
version that ran crashed every cycle with `KeyError: ('G18', 'C')`:
- **The code:** `flags-b80b2232-as-run.py`, `b80b2232…`. It is rebuilt by reversing the fix, and its sha256 equals
  the version that ran.
- **The cause:** it took the class from the job name, and "C" is not a class.
- **Why nobody saw it:** Python's crash exit (1) equalled the flag exit (1), and the watcher treated both alike. It
  logged nothing and went on (`flagwatch-run.log.txt`, which shows each traceback).
- **The effect:** END-SLIP and OVER-1.3MEAN were not evaluated for any run in that window. The window holds every
  AR23_Tb, AR23_Tc and G18_C run, and the bulk's last runs.
  <!-- absence-ok: this describes my own monitoring script's blind window, evidenced by the attached crash log; it is not a claim that a result does not exist -->

**The fix**, `flags.py` `2a3092d6…`:
- the class comes from the label prefix, with X counted as L;
- flags exit 3, so a crash is neither 0 nor 3, and `flagwatch.sh` treats anything else as an error;
- END-SLIP also checks ended jobs against their sacct End.

**The test.** `test_flags.sh` (`b5f37060…`) passes 10/10 in this directory:
- each trigger is silent on the baselines and fires on a mutated baseline;
- three regressions: G18_C rows are silent at normal ratios and fire when slow; a late End fires END-SLIP; a crash
  exits neither 0 nor 3.

The `flagwatch.sh` here is the fixed one. The one that ran differed in one line: it accepted rc 0 or 1.

**Read back afterwards.** On the final snapshot `out-final.txt` (2026-11-07T01:44:00Z, after Joseph renewed the
NERSC certificate), flags.py `2a3092d6` over all 1,572 runs gave `retro.txt`:
- OVER-1.3MEAN: 0;
- END-SLIP: 0. Every baseline job ended at least 1.09 h before its trigger, and under its p90 itself.
- RUN-OVER-MAX: the 3 listed above.

**Nothing would have fired.** That is a reading after the fact, not monitoring during the window.

## Files

- **`wave/`:**
  - both wave connect versions;
  - `cov2d_cap.py` and `test_cov2d_cap.py`;
  - `relaunch.sh`, the local launcher: it stages the files, compares digests in a separate step, launches, fetches and
    removes;
  - `sim.sh`;
  - the three connect logs and their removal logs. Each log's local digest equals the node's digest in its removal
    log.
- **`complete/`:**
  - `connect-complete.sh`;
  - `launch-complete.sh`;
  - `sim-complete.sh`;
  - its log and removal log, LOG_DIGEST_MATCH (`1c8edacd…`);
  - the rename ledger.
- **`collision/`:**
  - `watch2.sh` and its four runs' output;
  - the four match files;
  - the G18_L diagnosis and the 13:04:06Z listing, with their read-only scripts.
- **`projection/`:**
  - `proj.py` and its inputs and outputs, all reproducible here;
  - `flags.py` (fixed), `flags-b80b2232-as-run.py`, `test_flags.sh`, `flagwatch.sh`, `q.sh` (the read-only fetch);
  - `flagwatch-run.log.txt`, `overmax.log.txt`, `out-final.txt`, `retro.txt`.
- **`completeness/`:** `completeness.py`, `completeness.tsv`, `completeness.err.txt`.
- **`state_after.txt`:** sacct for all 27 cov2d attempts at 2026-11-07T01:44:00Z (`2e408a27…`).

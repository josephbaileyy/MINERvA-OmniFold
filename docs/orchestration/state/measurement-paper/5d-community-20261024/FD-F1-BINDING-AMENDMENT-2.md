# Binding, amendment 2: F1b′ in one wave of 14 long tasks (2026-10-28)

**By** the paper-tighten lane, as director.

**Under:**
- `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` (PR #431), item 1: a ceiling of 2.5 node-h for
  F1 in total;
- [`FD-F1-BINDING.md`](FD-F1-BINDING.md) (PR #429) and [`FD-F1-BINDING-AMENDMENT-1.md`](FD-F1-BINDING-AMENDMENT-1.md)
  (PR #435), which this amends.

**Binds** [`FD-F1-DECLARATION-AMENDMENT-2.md`](FD-F1-DECLARATION-AMENDMENT-2.md), merged in PR #444 (after
`merge_main.sh` as `d21b07c3`). Its file sha256 begins `931808e5b601e4d6`.

**MEASURES:** nothing. It authorizes F1b′ as amendment 2 lays it out, on its gate's GO, and then F1c, the grade, the HPSS
copy and the report, as the earlier bindings bind them.

**CANNOT AUTHORIZE:**
- a new pilot;
- any read of `f1b/` or `f1b2/`;
- any charge above the ceiling;
- a rerun or repair after a STOP;
- anything the earlier bindings cannot authorize.

## 1. The bound code

**The deploy pin** is `5f5e392c4be9c6f8bb035a72d4a60f7dd8be8803`, main after PR #444. `OUT` is unchanged. The new
deploy is `D3=$OUT/deploy/5f5e392c`, which must not exist beforehand.

**At the PR head `3a0d2dc7`, the director checked:**
- the declared test modules, locally with `-I -B` and a TMPDIR: `test_fd_f1_amend2.py` 15 OK, `test_fd_f1_amend.py`
  13 OK, `test_fd_f1.py` 31 OK and `test_fd_f0_regrade.py` 47 OK, with 0 porcelain lines after;
- the earlier bound gates and scripts (`fd_f1_budget.py`, `fd_f1_budget2.py`, `sbatch_fd_f1a2.sh`, `sbatch_fd_f1b2.sh`),
  unchanged from `main`;
- the gate's projection, against the director's own arithmetic from the re-pilot records:
  - task wall 1,704.7 s;
  - F1b′ 2,604.7 s;
  - total 1.8819 node-h, against the priced 2.0;
  - worst case 2.2250 node-h, against the ceiling 2.5.

## 2. Rulings on §8

1. **The layout and the seeds are accepted:** 7 tasks of 160,000 events per tune, in one wave of 14, with seeds
   60001–60007 and 61001–61007. Seeds 60001 and 60006 have never-read gst files in `f1b/`, so a regenerated stream's
   first events may coincide with them. Nothing is used twice, and `f1b/` stays unread.
2. **No new pilot.** The gate projects from F1a′'s committed `.time` records at their largest per-event time and load,
   seed 60103 included. The 9.1× extrapolation in events, the unmeasured gntpc scaling and the RSS range are stated as
   the declaration states them. The job limit bounds them.
   <!-- absence-ok: scoping statements about the projection's inputs (amendment 2 states the event extrapolation, gntpc scaling and RSS range); no claim that a result is absent -->
3. **The per-task timeout is accepted as declared,** 3 × the projected task wall. It cannot fire within the 0:55 job
   limit, and with one wave `|| exit 255` has no further launch to stop. **The job limit is the effective stall bound.**
   - A task still running at 0:55 ends as a scheduler TIMEOUT, which is a STOP.
   - Its cost is already inside the worst case, 2.2250.
   - No code change is made for this.
4. **The 57-minute wall rule** is kept, and amendment 1's "55" is withdrawn. The wall rule binds at a task wall of
   1,836 s, about 8 % above the projection.
5. **`sbatch_fd_f1b2.sh`'s unchecked sums-file step** is left as is: it is bound and will not run. Any future use of that
   script needs the fix first.

## 3. Deviation recorded: reads of `f1b/`

`DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` item 1 says the partial F1b output "stays
untouched as the STOP's evidence and is never read". `FD-F1-BINDING-AMENDMENT-1.md` forbids any read of `f1b/`. Amendment
2 §7 and its committed transcript sweep (`disclosure_sweep.py`, `disclosure-sweep.out`, command bodies C1–C14) record
these reads:
- **Before amendment 1's binding:** the measurement session's probes 18 and 19 (C5, C6) read F1b's 128 task logs and
  the work-directory status files of four seeds, `grep -c Killed` included. The amendment's §1 cites them.
- **After amendment 1's binding:** the F1a′ review hashed the 128 task logs (C9) and read file metadata, against
  binding amendment 1's prohibition. Amendment 1's own review (C1–C4) read metadata only.
- **No gst or GHEP event content was read.** All 22 gst files were last accessed when F1b wrote them, provided Lustre
  updates access times on read. Nothing in `f1b/` was modified.

**The effect:** none on any F1 product or grade. The reads were of logs, status files and metadata from a stopped job,
used to diagnose its failure. No event from F1b enters F1b′, F1c or the grade.

**The director's share:** the director bound amendment 1 with §1 citing probes 18 and 19, and did not connect them to
the decision's "never read". The measurement session raised it first.

## 4. Conditions

1. **Deploy and tests** (login node):
   - clone the pin to `$D3`, detached, with HEAD equal to the pin and 0 porcelain lines, ignored files included;
   - re-verify F1a's five products and F1a′'s 20 `.time` records against their committed sums;
   - re-measure the original declaration's §8 digests;
   - run the four modules with root_6_28's Python, `-I -B` and `TMPDIR=$OUT/tmp3`. They must give 15, 13, 31 and 47
     passing, with 0 porcelain lines after;
   - `$OUT/f1b3` must not exist;
   - anything else is a STOP.
2. **F1b′:** `submit_fd_f1.sh f1b3 $D3 <pin> $OUT 2.0 2.5`. A gate STOP, a refused submit, a failed or timed-out task, a
   scheduler TIMEOUT or a non-zero exit comes to the director unrepaired.
3. **F1c, the grade, the HPSS copy and the report** follow `FD-F1-BINDING.md` §4, items 4–9, and
   `FD-F1-BINDING-AMENDMENT-1.md` §4, items 4–6. They read F1b′'s prep, and the receipt commits keep their path rule.
4. **The report adds:**
   - each F1b′ task's measured wall and RSS against the projection;
   - sacct's batch MaxRSS and elapsed time for every job;
   - the total charge against 2.0 and 2.5;
   - this binding's §3 deviation, restated.
5. **Retention:** `fd-f1-20261027` stays on the pscratch list, with `f1b3/` added.

The steps may start once this record is on `main`.

## Not changed

- F1 is a bias test, not a coverage test. Its grading, held-out group, F1c seeds and earlier rulings stand.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.

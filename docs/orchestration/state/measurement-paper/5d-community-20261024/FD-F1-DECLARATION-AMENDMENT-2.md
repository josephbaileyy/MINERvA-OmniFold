# DECLARATION F1, AMENDMENT 2: after the F1a′ re-pilot's STOP, F1b′ in one wave of 14 long tasks (2026-10-28)

**By** the measurement session, for the director to review and re-bind.

**Amends** [`FD-F1-DECLARATION.md`](FD-F1-DECLARATION.md) as amended by
[`FD-F1-DECLARATION-AMENDMENT-1.md`](FD-F1-DECLARATION-AMENDMENT-1.md), bound by
[`FD-F1-BINDING-AMENDMENT-1.md`](FD-F1-BINDING-AMENDMENT-1.md) at deploy pin `4b7a9892`.

**Under the director's ruling of 2026-10-28 on the F1a′ STOP** (by correspondence):
- F1b′ is re-laid out so that a task's fixed cost is paid 14 times instead of 128;
- no new pilot: the gate projects from F1a′'s committed measurements;
- Joseph's ceiling of **2.5 node-h for F1 in total** stands
  ([`DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md`](../../../DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md));
- nothing runs before the re-binding.

**MEASURES:** nothing new. The facts in §1 come from F1a′'s committed receipts (`fd/receipts-f1/run/s6-look.out` and
`cluster/f1a2/`, job 60425719). §7 comes from this session's transcripts and the probes and review notes they name.

**CANNOT AUTHORIZE:** a job, a price, or a reading.

## 0. What changes

| | as amended (amendment 1) | as amended here |
|---|---|---|
| F1b′ layout | 128 tasks of 17,500 events, at most 14 at once, 10 waves | **14 tasks of 160,000 events, 7 per tune, all at once, one wave**. Events per tune unchanged: 7 × 160,000 = 64 × 17,500 = 1,120,000 |
| seeds | 60001–60064, 61001–61064 | **60001–60007 and 61001–61007**: the first seven of each declared range, in order |
| pilot | F1a′ | **none**: F1a′ ran (job 60425719) and its records are committed |
| gate | `fd_f1_budget2.py`, inside the re-pilot job | **`fd_f1_budget3.py`**, run by `submit_fd_f1.sh f1b3` on a login node, on the committed records |
| submission | `submit_fd_f1.sh f1b2` | **`submit_fd_f1.sh f1b3 <deploy> <pin> <OUT> <priced> <ceiling>`** |
| output paths | `f1b2/` | **`gate3/` and `f1b3/`**, both new. `f1b/` and `f1b2/` are never read |
| wall rule | 1.25 × the wall ≤ 57 min (§6 said "55-minute" in error) | **1.25 × the wall ≤ 57 min**, unchanged; the "55" is withdrawn |
| F1c, the grade | reads `f1b2/prep` | reads **`f1b3/prep`**; otherwise unchanged |

`fd_f1_budget2.py`, `sbatch_fd_f1a2.sh` and `sbatch_fd_f1b2.sh` are unchanged, because their records are bound.

## 1. Why: what F1a′ measured

F1a′ ran 14 gevgen processes at once: per tune, 4 of 17,500 events and 3 that ran 1,000 events twice in a row. All 20
runs exited 0. Its gate said STOP on the wall and both cost rules (`FD-F1-BINDING-AMENDMENT-1.md` §4.2; receipts on
`fd/f1-report`, PR #442).

**A task is mostly fixed cost.** From the per-phase stamps in `s6-look.out` (seconds):

| run | events | gevgen | gntpc | wall (`/usr/bin/time -v`) |
|---|---:|---:|---:|---:|
| long, 8 runs | 17,500 | 163–165, and 272 (G18 seed 60103) | 46–52 | 215.81–223.72, and 327.72 |
| short, first run, 6 | 1,000 | 114–115 | 46–52 | 167.69–173.17 |
| short, second run, 6 | 1,000 | 50–54 | 44–48 | 95.60–102.98 |

- The long runs and the short first runs started in the same second (06:18:33Z), so they ran under the same load. Their
  gevgen phases differ by about 50 s for 16,500 events: about 3.0 ms per event.
- **gntpc took 44–52 s at both 1,000 and 17,500 events.** Its dependence on the event count is not resolved by these
  runs, so its cost at 160,000 events is unmeasured.
  <!-- absence-ok: a scoping statement about what F1a′'s 1,000- and 17,500-event runs measured -->
- So a 17,500-event task is about 165 s of fixed cost (start-up, about 114 s under 14-way start-up load, and gntpc) and
  about 50–58 s of events. The 128 × 17,500 layout paid that fixed cost 128 times.

**Peak RSS did not grow with events over the range measured.** It was 19,850,268–21,497,940 K in the long runs and
19,713,084–22,015,472 K in the short runs. That is a measurement from 1,000 to 17,500 events only.

**Seed 60103 is unexplained.** Its gevgen phase took 272 s against 163–165 s, with user CPU 259.30 s against
145.21–154.23 s (its `.time` record). Its DFRKinematics retries do not single it out (`s6-look.out`). The gate keeps it
(§3).

## 2. The layout and the seeds

- **14 tasks, 7 per tune, 160,000 events each,** run together under `xargs -P 14`: one wave.
- **Seeds: 60001–60007 (G18_10a_02_11b) and 61001–61007 (AR23_20i_00_000),** the first seven of each range the bound
  F1b declared (`sbatch_fd_f1b.sh`), in order. The rule is mechanical and uses no product.
  - They are disjoint from F1a′'s (60101–60110, 61101–61110) and the pseudo-experiments' (`fd_f1_tasks.SEEDS`). A test
    checks it.
  - Seeds 60010, 60011 and 60050, which stalled in F1b, are not among them.
  - F1b's never-read output holds a gst file for seeds 60001 and 60006 (the committed `tasks-outcome.txt`,
    recorded before the decision of §7). With the same seed and inputs, a new task's first events may repeat those. No
    F1b event is read or used, so nothing is counted twice.

## 3. The gate, `nd-unfolding/fd_f1_budget3.py`

**Its inputs are the committed records.**
- It reads the 20 `.time` records under `fd/receipts-f1/run/cluster/f1a2/runs/` in the deploy.
- Each re-verifies against the committed `f1a2-SHA256SUMS`, whose own sha256 (`43b62168…`) is pinned in the code. A
  changed, missing or extra record refuses.
- It parses them with `fd_f1_budget2`'s own `load_runs` and `summary`, so the fit is the one F1a′'s gate committed.

**The projection** (the director's rule, taken conservatively):
- t = the largest fitted per-event time over the two tunes, and L = the largest fitted load. Each is taken separately,
  so the task is at least each tune's own L + 160,000 t. Seed 60103 is included.
- task wall = L + 160,000 t; F1b′'s wall = task + 900 s (hadd, two conversions and the prep, as the earlier gates).
- memory = 14 × the largest per-process RSS over all 20 runs.
- spent = **0.408333** node-h, from sacct: F1a 0.104722 + F1b 0.202778 + F1a′ 0.100833 (`fd/LEDGER.tsv` S4.2, S4.3, S4.5;
  a test sums the rows). The re-pilot's own timer (0.097778) is not used.

**GO only if:**
- memory ≤ 75 % of the node's 487,802 MiB;
- 1.25 × the wall ≤ 57 min;
- spent + the wall + F1c's priced 0.75 ≤ the priced total the binding sets;
- the worst case (spent + F1b′'s limit + F1c's 0:54) ≤ the ceiling the binding sets.

**On GO** it writes `f1b3_time_limit` (1.25 × the wall, rounded up to a minute) and `f1b3_task_timeout_s` (3 × the task
wall). Anything else is a STOP for the director.

**The numbers, from the committed records** (`fd_f1_budget3.py --priced-node-h 2.0 --ceiling-node-h 2.5`):

| quantity | value | rule |
|---|---:|---|
| per-event time t (G18, seed 60103 included) | 9.590 ms | — |
| load L (AR23) | 170.37 s | — |
| task wall, 170.37 + 160,000 × 0.009590 | 1,704.7 s | — |
| F1b′ wall, + 900 s | 2,604.7 s | 1.25 × = 3,255.9 s ≤ 3,420 s |
| F1b′ time limit | 0:55 | — |
| memory, 14 × 22,015,472 K | 308,216,608 K, 61.7 % | ≤ 75 % |
| projected F1 total, 0.408333 + 0.723533 + 0.75 | 1.8819 node-h | ≤ 2.0 |
| worst case, 0.408333 + 0.916667 + 0.9 | 2.2250 node-h | ≤ 2.5 |
| per-task timeout, 3 × 1,704.7 | 5,115 s | — |
| **decision** | **GO** | |

- The director's arithmetic (task about 1,700 s, F1b′ about 0.72 node-h, total about 1.88, worst case about 2.2) agrees.
- With the 3.0 ms per event of §1 instead, the task would be about 650 s and F1b′ about 0.43 node-h. The gate does not
  use that figure.
- **Which rules bind.** The wall rule fires at a task wall of 1,836 s, about 8 % above the projection. The priced rule
  fires at 2,130 s. The ceiling rule cannot fire while the wall rule holds, because spent + 57 min + 0:54 is 2.2583.
  So the memory rule and the 57-minute wall rule are the ones that bind, as in amendment 1.
- **The extrapolation.** 160,000 events is 9.1× the largest run F1a′ measured. The 160,000 t term is therefore an
  extrapolation of the fit, and so is any growth of gntpc with events (§1). Peak RSS is measured only up to 17,500 events.
  The gate's verdict cannot see any of this; the job limit bounds it (below).
- **The per-task timeout cannot fire inside the job limit.** With one wave, 3 × the task wall (5,115 s) is longer than
  F1b′'s 0:55 limit (3,300 s). A stalled or slow task is therefore ended by the job's time limit, which is a STOP
  (TIMEOUT) costing at most the 0:55 already counted in the worst case. The timeout is kept as ruled. §8 item 3 puts the
  choice to the director.
- **The `|| exit 255` stop-on-failure** stops further launches only, and with one wave there are none to stop. A failed
  task still makes xargs exit non-zero, and the job STOPs after the wave.

**The sacct cross-check.** F1a′'s job ended FAILED 3:0, its gate's STOP exit, so amendment 1's "COMPLETED" check cannot
apply. `submit_fd_f1.sh f1b3` instead requires job 60425719 to read exactly `FAILED|3:0` in sacct (all 20 runs exited 0,
and the job was not killed). It also requires its batch MaxRSS (287,876,772 K, the node-level peak, a 30 s cgroup sample)
to be within 75 % of the node. It refuses otherwise.

## 4. F1b′ (new path `$OUT/f1b3`) and what follows

- **The launcher,** `nd-unfolding/sbatch_fd_f1b3.sh`, refuses unless:
  - the deploy is clean at the pin;
  - `$OUT/gate3/budget3.json` says GO, with concurrency 14 and a positive per-task timeout;
  - F1a's five products re-verify against `$OUT/f1a2/reused.sha256`;
  - `$OUT/f1b3` does not exist.
  <!-- absence-ok: a launcher precondition the script checks, not a claim about a result -->
- **It then:**
  - runs the 14 tasks, each under `/usr/bin/time -v` and `timeout` of the gate's `f1b3_task_timeout_s`, with
    `|| exit 255`;
  - runs the NOWIDTH flux-check on all 14, the gst counts (7 per tune), `hadd`, `gen5d_v3.py convert` and
    `fd_f1_prep.py`, as F1b′ did;
  - writes `f1b3-SHA256SUMS`, and STOPs if that step fails.
- **It never reads `$OUT/f1b` or `$OUT/f1b2`.** A test checks the script text.
- **F1c, the grade, the HPSS copy and the report** follow `FD-F1-BINDING.md` §4, items 4–9, and
  `FD-F1-BINDING-AMENDMENT-1.md` §4.4–4.6, reading `f1b3/prep`. The receipt commit's tables come from
  `fd_f1_tasks.py tables --prep $OUT/f1b3/prep`.
- **Any job that reaches its scheduler limit, a failed task or a timed-out task is a STOP.** A repeat stall names its
  seed.

## 5. Code and tests at this commit

**New:**
- `nd-unfolding/fd_f1_budget3.py`
- `nd-unfolding/sbatch_fd_f1b3.sh`
- `nd-unfolding/tests/test_fd_f1_amend2.py`, 15 tests:
  - the seed rule, read from the bound `sbatch_fd_f1b.sh` and checked against the gate and the launcher;
  - the single-wave plan (14 tasks, concurrency 14, one wave, 1,120,000 events per tune);
  - GO with every number recomputed;
  - **a STOP from each rule with every other rule holding**;
  - the memory boundary, counting the short runs;
  - the fit taking the largest per-event time and the largest load across the tunes;
  - the timeout as 3 × the projected task, and the launcher's timeout wiring;
  - the committed records: they re-verify, give GO with the §3 numbers, and refuse a changed, extra or missing record or
    a changed sums file;
  - spent as the sum of the ledger's F1 rows, and spent + 57 min + 0:54 ≤ 2.5;
  - **`submit_fd_f1.sh f1b3` run with stub `sbatch` and `sacct`:** it refuses a gate STOP (priced 1.0, or a ceiling of
    2.0), a re-pilot not at `FAILED|3:0`, a MaxRSS over 75 % in K or G units or empty, and an existing `gate3/` or
    `f1b3/`; otherwise it submits with the gate's 0:55;
  - **`sbatch_fd_f1b3.sh` run against a throwaway git deploy,** with a valid one-line checksum fixture so that the
    products check passes on GNU and BSD `sha256sum` alike: it exits 2, with each guard's own message, on a wrong pin, a
    missing gate file, a STOP, concurrency 16, a missing or zero timeout, changed F1a products, and an existing `f1b3/`,
    creating nothing; and it checks the sums-file step.

**Changed:** `nd-unfolding/submit_fd_f1.sh` gains the stage `f1b3`. Its other stages are unchanged.

**Unchanged:** every other F1 file, `fd_f1_budget2.py`, `sbatch_fd_f1a2.sh` and `sbatch_fd_f1b2.sh` included.

**Receipts** (`fd/receipts-f1/amendment-2/`):
- `tests-local.log`: this module, `test_fd_f1_amend.py`'s 13, `test_fd_f1.py`'s 31 and `test_fd_f0_regrade.py`'s 47;
- `mutants.py`, with 42 planted defects in the gate, the launcher and the f1b3 stage:
  - `mutants.log`: 42 of 42 killed with this machine's BSD `sha256sum`;
  - `mutants-gnu-shim.log`: 42 of 42 killed with `gnu-strict-sha256sum.sh` first on PATH. It refuses a checksum file
    with no well-formed line, as GNU `sha256sum` does on the cluster;
  - `control-old-fixture-gnu-strict.log`: the control. With the first draft's empty fixture under that shim, mutants 32–34
    (the GO, timeout and pin guards removed) survive. That is the review's finding (§9), now fixed;
- `disclosure_sweep.py` and `disclosure-sweep.out`: §7's evidence.

## 6. Re-priced budget

| stage | node-h | cap (scheduler limit) |
|---|---:|---:|
| spent: F1a 0.104722 + F1b 0.202778 + F1a′ 0.100833 | 0.408333 | 0.408333 |
| F1b′, one wave of 14 | 0.7235 (the gate's projection) | 0.9167 (0:55, from the gate) |
| F1c | 0.68–0.75 | 0.90 (0:54) |
| **F1 total** | **1.88** | **2.2250**, within Joseph's 2.5 |

For the re-binding I propose `<priced>` = **2.0** and `<ceiling>` = **2.5**, as amendment 1's binding set them.

## 7. Disclosure: reads of `f1b/` after Joseph's "never read"

**The rule.** Joseph's decision, committed as `2b1c9d63` at 2026-10-27 19:56:16 PDT (02:56:16Z on 10-28), says the
partial F1b output "stays untouched as the STOP's evidence and is never read". `FD-F1-BINDING-AMENDMENT-1.md` (line 18)
later made "any read of `f1b/`" something it cannot authorize. Nothing under `f1b/` has been modified since F1b ended
(the review of the F1a′ receipts: no mtime or ctime after 19:25:25 PDT).

**Every read after 19:56:16 PDT.** The evidence is `fd/receipts-f1/amendment-2/disclosure-sweep.out`, the output of
`disclosure_sweep.py` over this session's transcript and its subagents' (73 files).
- Its §1 lists every line of a command sent over ssh after 02:56:16Z on 10-28 that names an `f1b` path other than `f1b2` and
  `f1b3`: 18 lines. 16 are cluster commands. The last two are the sweep's own pattern text, run locally.
- Its §3 holds the F1a′ review's access-time listings of `f1b/`.
- The transcripts are files on the machine this session ran on, not in git, so that output is the committed record.
Search: f1b paths in ssh commands after 2026-10-28T02:56:16Z @ disclosure-sweep.out

| when (PDT) | who | what was read | content or metadata |
|---|---|---|---|
| 10-27 20:24–20:32 | amendment 1's independent review | `ls -l` of eight work directories (G18 60001, 60002, 60003, 60010, 60011, 60050; AR23 61001, 61012); `ls -l` of every work directory's `gevgen.log` and any `gntp.*.ghep.root`; `stat` of s60010's files and of `s60001/gevgen.log`; a `stat` loop over every work directory's `input-flux.root`, status file and `gevgen.log` (birth and modify times); `ls` counts of `input-flux.root` and `gntpc.log` | metadata only |
| 10-27 21:11–21:12 | this session, probe 18 (`fd/receipts-f1/amendment-1/probes/probe18.sh`) | `ls -la` of the work directories of G18 60010, 60011 and 60050; `wc -l`, the last 25 lines of, and a grep of each one's `gevgen.log`; the last 5 lines of `s60001/gevgen.log` | **log content** |
| 10-27 21:12 | this session, probe 19 (`probe19.sh`) | `stat` of the status files and `gevgen.log` of 60010, 60011, 60050 and 60001; a grep of those four status files; the last 4 lines of the task logs of 60010, 60011 and 60050; `grep -c Killed` over all 128 `f1b/logs/gen_*.log` | **status-file and log content** |
| 10-28 02:12–02:17 | the F1a′ receipts' independent review | `sha256sum` of the 128 `f1b/logs/gen_*.log`; `find` over `f1b/` printing modify, change and access times; `ls -la` and `ls -lR --time=atime` of `f1b/` | **log content** (hashed); otherwise metadata |

- **No gst or ghep file's event content was read** in any of these. Among the matched lines, gst and ghep files appear
  only as names in `ls` and `find` listings (the sweep's §2: one `ls -l` of `gntp.*.ghep.root`; the other two lines are
  its own pattern text).
  - The access times agree. In the F1a′ review's listing (sweep §3, taken before its own reads), every
    `genie_v3.gst.root` under `f1b/` (22 files) was last accessed at 19:25 PDT, when F1b wrote it, and the three
    `gntp.*.ghep.root` at 19:23.
  - A caveat: that holds only if Lustre updates access times on reads, as it did for the logs and status files below.
  Search: gst, ghep, ROOT, RDataFrame, TFile, uproot in the matched lines @ disclosure-sweep.out
- **The 21:12 access times** are probes 18 and 19's. In sweep §3's first listing, 136 files were last accessed at
  21:12 PDT: the 128 task logs (probe 19's `grep -c`), plus the status files and `gevgen.log` of 60001, 60010, 60011
  and 60050. The F1a′ review took that listing before its own reads, which then moved 135 directories' access times to
  02:12.
- **How it happened.** Probes 18 and 19 ran about 76 minutes after the decision was committed. I did not connect its sentence to
  the diagnosis I was writing. Amendment 1's §1 cites both probes. The F1a′ review's reads came from my own prompt, which
  asked it to compare times "with the prior receipts' f1b/ logs".
- **The director's account,** as they gave it by correspondence on 2026-10-28 (not in a committed file): "I accepted
  amendment 1 with §1 citing probes 18 and 19 and didn't connect them to Joseph's "never read" either."
- **What still holds:** the F1a′ re-pilot neither read nor modified `f1b/`. Sweep §3 shows no access time between
  23:18 and 23:24 PDT, the re-pilot's window, and no mtime or ctime after 19:25:25.
  Every F1b number used anywhere in F1 comes from receipts committed before the decision (`183b31e4`), from sacct, or
  from the reads above, which amendment 1 cites.

**This amendment's own review** was told, in its prompt, that any access to `$OUT/f1b/` or `$OUT/f1b2/` is forbidden,
and to read on the cluster only under `f1a/`, `f1a2/`, `deploy/` and `logs/` (§9).

## 8. For the director

1. The single-wave layout and the seed rule (§2), and that seeds 60001 and 60006 repeat F1b's never-read streams.
2. The gate's projection (§3): GO, with a task of 1,704.7 s, F1b′ 0.7235 node-h, total 1.8819 and worst case 2.2250. The
   per-event term is extrapolated 9.1×, and RSS is measured only up to 17,500 events.
3. **The per-task timeout (5,115 s) cannot fire within the 0:55 job limit (3,300 s).** The job limit is what ends a
   stall, at a cost already inside the worst case. You may keep it as ruled, or set it below the limit, for example the
   limit less the 900 s of post-processing. This declaration keeps it as ruled.
4. The sacct check adapted to F1a′'s `FAILED|3:0` (§3).
5. The 57-minute wall rule, kept; amendment 1's "55" withdrawn.
6. `<priced>` = 2.0 and `<ceiling>` = 2.5.
7. The disclosure (§7), for the binding's record.

## 9. Review

An independent read-only review (codex-school2, gpt-6.1-sol, high, sandbox read-only, no cluster access) ran on the
first draft at `e2dcad59`. Its prompt forbade any access to `$OUT/f1b/` and `$OUT/f1b2/`.

| finding | severity | done |
|---|---|---|
| The launcher refusal tests could pass for the wrong reason: the empty checksum fixture makes GNU `sha256sum -c` refuse, so mutants removing the GO, timeout or pin guard would survive on the cluster although they died locally on BSD `sha256sum` | medium | a valid one-line fixture, each refusal's own message asserted, a changed-products case added. Mutants rerun natively and under a GNU-strict shim: 42 of 42 killed. The old fixture under the shim lets 32–34 survive, which confirms the finding (§5) |
| The sums-file step's status was unchecked, so a failed hash could end the job as a success | medium | `need $? "the sums file"` added, with a test and mutant 41. The same pattern in the bound `sbatch_fd_f1b2.sh` is left unchanged, because that file is bound and will not run |
| The disclosure rested on an uncommitted transcript search, and on statements about other reviews without receipts | medium | `disclosure_sweep.py` and its output committed. §7 now cites them line by line, adds the access-time evidence, and marks the director's words as correspondence |

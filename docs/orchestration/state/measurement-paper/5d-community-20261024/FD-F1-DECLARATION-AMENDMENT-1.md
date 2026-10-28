# DECLARATION F1, AMENDMENT 1: after F1b's out-of-memory STOP, a re-pilot at production concurrency (2026-10-28)

**By** the measurement session, for the director to review and re-bind.

**Amends** [`FD-F1-DECLARATION.md`](FD-F1-DECLARATION.md), bound by [`FD-F1-BINDING.md`](FD-F1-BINDING.md) at deploy pin
`5015535e`.

**Under the director's ruling of 2026-10-28 on the F1b STOP** (by correspondence):
- option (A), the re-pilot at production concurrency with peak RSS measured per process;
- (C) declined;
- Joseph approved (A), with a ceiling of **2.5 node-h for F1 in total**, the 0.3075 already spent included
  ([`DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md`](../../../DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md),
  PR #431);
- no job runs before the re-binding, including the re-pilot.

**MEASURES:** nothing new. The facts in §1–2 come from F1a's and F1b's receipts, `sacct`, file metadata in F1b's work
directories, GENIE's own status files, and read-only reads of GENIE v3_04_00's source and configuration on CVMFS. The
probes are under `fd/receipts-f1/amendment-1/probes/`. The STOP's receipts are on the report branch, `fd/f1-report`
at `183b31e4`, so this amendment lands after that branch.

**CANNOT AUTHORIZE:** a job, a price, or a reading.

## 0. What changes

| | as bound | as amended |
|---|---|---|
| pilot | F1a: 2 processes, 10,000 events each; no memory rule | **F1a′**: 16 processes, F1b′'s own concurrency. Per tune, 4 run one full 17,500-event task and 4 run 1,000 events twice. Every run is under `/usr/bin/time -v` |
| gate | `fd_f1_budget.py`: a declared contention factor of 1.25 | **`fd_f1_budget2.py`**: F1b′'s wall is the measured full-task wall × 8 waves. **STOP if 16 × the largest per-process RSS exceeds 75 % of the node**, plus the wall, priced and ceiling rules |
| production | F1b: 128 tasks at once | **F1b′**: the same 128 tasks and seeds, at most 16 at once (`xargs -P 16`) in 8 waves; a failure stops new launches |
| submission | — | `submit_fd_f1.sh f1b2` also refuses unless `sacct`'s batch MaxRSS for F1a′, the node-level peak, is within 75 % of the node |
| output paths | `f1a/`, `f1b/` | `f1a2/` and `f1b2/`, both new. `f1b/` is left untouched as the STOP's evidence |
| F1c, the grade | — | unchanged, reading F1b′'s prep |

## 1. The cause, corrected

**F1b (job 60417614).** One node started 128 gevgen processes at once.
- The job ended OUT_OF_MEMORY after 12:10, with 103 `oom_kill` events. The batch MaxRSS was 499,490,432 K against the
  job's 487,802 M allocation.
- **The OOM struck during gevgen's start-up, before any event was generated.**
  - gevgen writes `input-flux.root` (`gEvGen.cxx:570`) when it builds its flux driver. That comes after `Initialize()`,
    which loads the splines (`:231`, `:270`).
  - Only 25 of the 128 work directories hold an `input-flux.root`. The other 103 hold a 0-byte `gevgen.log` and nothing
    else, and their task logs carry bash's "Killed" line. 103 is the number of `oom_kill` events.
- **The 25 that survived start-up:**

  | phase | timing, relative to gevgen start |
  |---|---|
  | flux driver built | 553–554 s |
  | event loop begins | 591–593 s |
  | 22 tasks finish 17,500 events | 647–656 s, at 3.3–3.6 ms per event |
  | F1a's pilot, for comparison | start-up 45–49 s, then about 3.1 ms per event |

  So **the event loop ran at the pilot's speed; start-up took over 10× as long**. The independent review measured these
  phases from file birth times.
- **The three tasks without a gst** (G18 seeds 60010, 60011, 60050) were still in their event loops when the job ended.
  - GENIE's status files read events 4,200, 11,900 and 15,850, at 3.82, 3.35 and 3.41 ms per event
    (`probes/probe19.out`).
  - Their logs end mid-line, and their task logs have no rc and no "Killed" line.
  - The batch script exited on the first failed task (02:25:25Z), and the job's teardown ended them. So they show no
    sign of a failure tied to their seeds.
  - The earlier statement that they "died in gntpc" was wrong.
- **The earlier "37.5 ms per event, about 3× the bound" was a misreading.** It divided the whole 656 s by the events.
  Per-event speed did not change.

**The lesson: memory was measured, and set aside.**
- F1a's batch step recorded MaxRSS 45,610,936 K, about 43.5 GiB (`sacct`, job 60415571, `probes/probe14.out`). The
  only GENIE stages that ran two at a time in F1a were two `gspl2root`, then the two gevgen pilots. So that peak bounds
  one gevgen process's start-up at about **22 GiB** (inference).
- Nobody read it before F1b ran 128 such processes. That needs about 2.8 TiB, against a 476 GiB node. The first gate
  had no memory rule.
- F1b's own evidence agrees: 128 processes exceeded the node (more than 3.7 GiB each on average), and the 25 that fit
  allow at most about 19 GiB each.
- So the amendment sizes concurrency from that bound (§3) and measures per process.

## 2. The "No Configuration available" message, explained (the director's item 2)

**The message.** Both pilots' logs carry, twice, "No Configuration available for
genie::EventGeneratorListAssembler/Default at the ConfigPool".

**Its source, in GENIE v3_04_00** (`probes/probe14.out`, `probe15.out`):
- **The warning:** `Algorithm::FindConfig` (`src/Framework/Algorithm/Algorithm.cxx:157`) logs it when the global pool
  holds no registry under that key, and keeps its configuration.
- **Why the key is missing:** the global `config/EventGeneratorListAssembler.xml` says: "The Default configuration
  depends on the tune and it is defined in TuneGeneratorList.xml, which is defined in each Tune subdirectory." That file
  defines only named special lists, never `Default`.
- **Where the list comes from:** `EventGeneratorListAssembler::AssembleGeneratorList`
  (`src/Framework/EventGen/EventGeneratorListAssembler.cxx:44-77`). When `RunOpt::EventGeneratorList()` is `"Default"`,
  it adds `AlgConfigPool::TuneGeneratorList()` as its top registry. That is the key `TuneGeneratorList/Default`, read by
  `AlgConfigPool::LoadTuneGeneratorList` from `TuneGeneratorList.xml`
  (`src/Framework/Algorithm/AlgConfigPool.cxx:237-251, :603-610`).
- **Why it is "Default":** `run_gevgen_v3.sh` passes no `--event-generator-list`, and `RunOpt` defaults to `"Default"`
  (`RunOpt.cxx:77`).

**Which list each pilot used.**
- `GetXMLFilePath` searches the tune directory, then the tune-family directory. Neither tune directory holds a
  `TuneGeneratorList.xml`, so each tune loads its family's: `config/G18_10a/TuneGeneratorList.xml` and
  `config/AR23_20i/TuneGeneratorList.xml`.
  - That path comes from the source, as the independent review read it (`XmlParserUtils.cxx:53-93`).
- The two files are byte-identical: the review measured sha256 `7a51f756…` for both. Each `Default` is the same 18
  generators: QEL-CC, QEL-NC, RES-CC, RES-NC, DIS-CC, DIS-NC, COH-CC-PION, COH-NC-PION, DIS-CC-CHARM, QEL-CC-CHARM,
  NUE-EL, IMD, IMD-ANH, DFR-CC, DFR-NC, QEL-CC-LAMBDA, MEC-CC and MEC-NC.
- So each tune ran its own list, and **this is not a STOP**.
- The laconic messenger suppresses GENIE's "** Loaded generator" lines, so the logs themselves don't name the
  generators.
  <!-- absence-ok: scoped to the two pilot gevgen.log files read in probe15 (a grep for "EventGenerator/" found none) -->

**The pilots' process mix,** from each pilot's gst (`probes/probe15.out`; 10,000 events per tune; the gst flags counted
over all events and over CC):

| flag | G18_10a_02_11b, all (CC) | AR23_20i_00_000, all (CC) | in the list |
|---|---:|---:|---|
| qel | 938 (663) | 902 (661) | QEL-CC, QEL-NC |
| mec | 238 (203) | 320 (283) | MEC-CC, MEC-NC |
| res | 2,254 (1,592) | 2,284 (1,637) | RES-CC, RES-NC |
| dis | 6,495 (4,785) | 6,432 (4,780) | DIS-CC, DIS-NC |
| coh | 60 (40) | 52 (30) | COH-CC-PION, COH-NC-PION |
| dfr | 15 (9) | 10 (9) | DFR-CC, DFR-NC |
| charm | 103 (103) | 88 (88) | DIS-CC-CHARM, QEL-CC-CHARM |
| imd, imdanh, nuel, em, singlek, amnugamma | 0 | 0 | IMD, IMD-ANH, NUE-EL; the rest are not in the list |
| CC / NC | 7,292 / 2,708 | 7,400 / 2,600 | |
| events with no flag; with two or more | 0; 103 | 0; 88 | the two-or-more count equals the charm count |

Every process seen is in the list, and nothing outside it appears.

**AR23's negative cross sections.**
- AR23's pilot logs **129** "Negative cross section for current kinematics!!" messages in 10,000 generated events.
  G18's logs none (a direct `grep -c`).
  - The 124 reported to the director earlier came from a count that collapsed lines.
- **What they are:** each message is followed by GENIE's interaction summary. As the review read it, all 129 are
  Weak[CC] QES on a C12 neutron, so they come from the QE kinematics.
- **What GENIE does with them:** `KineGeneratorWithCache::AssertXSecLimits`
  (`src/Physics/Common/KineGeneratorWithCache.cxx:266-270`) only logs and returns. In `QELEventGenerator`'s
  accept/reject test (`QELEventGenerator.cxx:195-203`), `accept = (t < xsec)` with `t = xsec_max × Rndm ≥ 0`, so a point
  with xsec < 0 is never accepted.
- The earlier citation of `MECGenerator`, and the dinucleon look-back, were wrong.

## 3. F1a′, the re-pilot (new path `$OUT/f1a2`)

**What it reuses.** F1a's five products are reused only after they re-verify against the committed
`fd/receipts-f1/amendment-1/f1a-SHA256SUMS`, which is F1a's own sums file:

| product | sha256 |
|---|---|
| `splines/G18_10a_02_11b_CH.xml.gz` | `dbd305df75dcd731a25dd0b20064ba52c20f095196ea21694997169831788c82` |
| `splines/AR23_20i_00_000_CH.xml.gz` | `f3a763e5e22e7f0246a838d6d2e8b94287f6f7137f71882dad5582cbab5439ba` |
| `flux_phi_t_0_100.root` | `06089d468525f9fe0a65f5d1f96094b3a918f288d8336dd29a40a2e8733fffbf` |
| `graphs_G18_10a_02_11b.root` | `f5840cb8970cff7554e3ea67873e6a6a70a49fdbc4dc49bd22f4978c5fd10d3d` |
| `graphs_AR23_20i_00_000.root` | `5afa412be71e5d9517336b5e5af860066d4034bd6b6b9f6423caa022f6226fd0` |

**The concurrency, P = 16.** 16 × about 22 GiB, the bound in §1, is about 352 GiB, or 72 % of the node. This is the
re-pilot's own risk: if a process needs more than about 29 GiB, the re-pilot itself runs out of memory, and that is a
STOP.

**The runs** (`nd-unfolding/sbatch_fd_f1a2.sh`, through `submit_fd_f1.sh f1a2 <deploy> <pin> <OUT> <priced> <ceiling>`,
with a 0:20 limit):
- Per tune, 4 processes run **one full F1b′ task** of 17,500 events, and 4 run 1,000 events twice in a row. So all 16
  run together for about one task's length.
- Every run is timed with `/usr/bin/time -v`. That gives the elapsed wall, the exit status, and the maximum RSS of the
  largest single process in the gevgen-and-gntpc tree.
- The NOWIDTH flux-check runs on all 24 work directories.
- Seeds: G18 60101–60112 and AR23 61101–61112. They are disjoint from F1a's (60000, 61000), F1b′'s and the
  pseudo-experiments', and a test checks it.

**The gate,** `nd-unfolding/fd_f1_budget2.py`:
- **The wall:** F1b′'s wall = 8 waves × the largest long-run wall + 900 s. The long runs *are* F1b′ tasks at 16-way
  load, so no fit and no contention factor is involved.
- **Memory:** F1b′'s memory = 16 × the largest RSS over every run. That covers both the start-up peak (seen in the short
  runs) and the full-task peak (seen in the long runs). It must be **at most 75 % of the node's 487,802 MiB**.
- **GO only if:**
  - every run exited 0;
  - the memory rule holds;
  - 1.25 × the wall ≤ 55 min;
  - spent + re-pilot + F1b′ + 0.75 ≤ the priced total;
  - the worst case (spent + re-pilot + F1b′'s limit + F1c's 0:54) ≤ the ceiling.
- **On GO** it writes `f1b2_time_limit` and the re-pilot's job id.
- **Descriptive only:** the per-event time and the load, fitted from the long and short runs.
- **The sacct cross-check:** `submit_fd_f1.sh f1b2` reads `sacct`'s batch MaxRSS for that job, the node-level peak,
  which `/usr/bin/time` cannot see. It refuses F1b′ unless that peak is within 75 % of the node.

## 4. F1b′ (new path `$OUT/f1b2`) and what follows

- **The tasks:** the same 128 as the bound F1b, with the same seeds, **60001–60064 and 61001–61064**, at 17,500 events
  each. They run at most 16 at once (`xargs -P 16`), in 8 waves. Each is timed with `/usr/bin/time -v`.
- **A failed task exits 255,** so xargs starts no further task.
- **Guards:**
  - the script refuses unless `budget2.json` says GO with concurrency 16, and unless F1a's five products still
    re-verify;
  - it refuses if `f1b2/` exists;
  - it never reads `f1b/`. **The 22 gst files from F1b are never read.**
- **Seeds 60010, 60011 and 60050 are reused.** §1 shows they were ended by teardown, not by a failure tied to their
  seeds. If any of them fails in F1b′, that is a STOP.
- **Everything after generation is F1b's, unchanged:** the NOWIDTH flux-check on all 128, the gst counts, `hadd`,
  `gen5d_v3.py convert` with its sampling test, and `fd_f1_prep.py`.
- **F1c and the grade are as bound.** The receipt commit's tables come from `f1b2/prep`.

## 5. Code and tests at this commit

**New:**
- `nd-unfolding/fd_f1_budget2.py`
- `nd-unfolding/sbatch_fd_f1a2.sh`
- `nd-unfolding/sbatch_fd_f1b2.sh`
- `nd-unfolding/tests/test_fd_f1_amend.py`, 13 tests:
  - `/usr/bin/time -v` parsing;
  - the seeds, checked against the script's arithmetic and against `fd_f1_tasks.SEEDS`;
  - GO with every number recomputed;
  - **a STOP from each rule with every other rule holding**;
  - the memory boundary, counting the short runs too;
  - the run-record refusals;
  - **`submit_fd_f1.sh f1b2` run with stub `sbatch` and `sacct`**: it refuses a STOP budget, a missing job id, and a
    re-pilot whose MaxRSS exceeds 75 % in K, M or G units, and submits with the gate's time limit otherwise;
  - the scripts' constants and their xargs stop-on-failure.

**Changed:** `nd-unfolding/submit_fd_f1.sh` gains the stages `f1a2` and `f1b2`. Its f1a, f1b and f1c lines are
unchanged.

**Unchanged:** every other F1 file, the bound gate `fd_f1_budget.py` included.

**Receipts:** `fd/receipts-f1/amendment-1/tests-local.log` (this module, plus `test_fd_f1.py`'s 31 and
`test_fd_f0_regrade.py`'s 47) and `mutants.log`. The deploy step runs every declared suite on a login node, as the
binding requires.

## 6. Re-priced budget

| stage | expected node-h | cap (scheduler limit) |
|---|---:|---:|
| spent: F1a 0.104722 + F1b 0.202778 | 0.3075 | 0.3075 |
| F1a′ re-pilot | 0.05–0.10 | 0.33 (0:20) |
| F1b′, 8 waves of 16 | 0.45–0.65 | ≤ 0.92 (from the gate, at most 0:55) |
| F1c | 0.68–0.75 | 0.90 (0:54) |
| **F1 total** | **1.49–1.80** | **ceiling 2.45**, within Joseph's 2.5 |

- **Assumptions.** These are estimates, not measurements: one task at 16-way load takes 60–120 s of start-up plus about
  60 s of events. The gate replaces them with the re-pilot's measured full-task wall before any production job.
- **The binding.** Joseph's ceiling is 2.5. For the re-binding I propose `<priced>` = `<ceiling>` = 2.5.
  - With those values neither cost rule can fire, because the caps sum to 2.45.
  - **The rules that actually bind are the memory rule and the 55-minute wall rule.**
  - A tighter `<priced>` is the director's to set.

## 7. For the director

1. The corrected cause (§1): the OOM came at start-up, F1a's MaxRSS was set aside, and the three tasks without a gst
   were ended by teardown.
2. P = 16, from F1a's MaxRSS. The re-pilot runs full-size tasks, so wall and memory are measured, not extrapolated.
3. The memory rule at 75 % of the node, with the sacct cross-check enforced in the submit line.
4. Reusing F1a's five products after re-verification, and F1b's seeds in `f1b2/`, never reading `f1b/`.
5. The generator-list finding in §2, as not a STOP.
6. The re-priced table, and the `<priced>` and `<ceiling>` values to bind.

## 8. Review

An independent read-only review ran on the first draft (`08a0b3ab`); §9 gives its findings and dispositions.

## 9. Review dispositions

| finding | severity | done |
|---|---|---|
| The OOM came at gevgen's start-up, not about 16,000 events in. The 64-process re-pilot was unsafe; "37.5 ms per event" was not contention | high | §1 rewritten. P = 16, from F1a's MaxRSS. The re-pilot runs full-size tasks, so nothing is extrapolated. §6 re-priced |
| The three tasks "died in gntpc" (false), and F1b′ reuses their seeds | high | read from GENIE's status files: they were in their event loops at normal speed when teardown ended them (§1). Reused, and a repeat failure is a STOP |
| The negative cross sections cited the wrong generator | medium | `QELEventGenerator.cxx:195-203` cited; the dinucleon look-back dropped |
| The time fit was fragile | medium | the gate uses the measured full-task wall; the fit is descriptive only |
| The sacct cross-check was prose only; `/usr/bin/time` reports the largest single process | medium | sacct's batch MaxRSS is enforced in `submit_fd_f1.sh f1b2` and tested with stubs; the RSS semantics are stated |
| The tests overstated "each rule on its own"; shell guards were only string-checked; the ledger test was vacuous; the seeds were retyped | medium | each-rule-alone test, stub-run submit tests, the xargs stop-on-failure check, the seeds read from `fd_f1_tasks.SEEDS`; the ledger test removed |
| priced = ceiling = 2.5 cannot fire; the F1b′ range topped above its own STOP; xargs ran on after a failure; the charm claim; the GetXMLFilePath resolution; 49 % | low | stated (§6); range corrected and the cap raised to 55 min within 2.5; `|| exit 255`; "equal count"; resolution stated (§2); the percentage recomputed for P = 16 |

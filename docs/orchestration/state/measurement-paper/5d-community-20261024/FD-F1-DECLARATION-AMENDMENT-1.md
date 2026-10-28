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

**MEASURES:** nothing new. The facts in §1–2 are read from F1a's and F1b's committed receipts, `sacct`, and read-only
reads of GENIE v3_04_00's source and configuration on CVMFS. The probes are under
`fd/receipts-f1/amendment-1/probes/`.

**CANNOT AUTHORIZE:** a job, a price, or a reading.

## 0. What changes

| | as bound | as amended |
|---|---|---|
| pilot | F1a: 2 processes, 10,000 events each, no per-process memory | **F1a′**: 64 processes, F1b′'s own concurrency, each run under `/usr/bin/time -v` |
| gate | `fd_f1_budget.py`: a declared contention factor of 1.25; no memory rule | **`fd_f1_budget2.py`**: the contended per-event time and the load fitted from two event counts; per-process RSS extrapolated to 17,500 events; **STOP if 64 × that exceeds 75 % of the node** |
| production | F1b: 128 tasks at once | **F1b′**: the same 128 tasks and seeds, at most 64 at once (`xargs -P 64`), in two waves |
| output paths | `f1a/`, `f1b/` | `f1a2/`, `f1b2/`, both new. `f1b/` is left untouched as the STOP's evidence |
| F1c, the grade | — | unchanged, reading F1b′'s prep |

## 1. The cause

**F1b (job 60417614).** One node ran 128 gevgen processes at once.
- After 12:10 the job ended OUT_OF_MEMORY, with 103 `oom_kill` events.
- The batch step's MaxRSS was 499,490,432 K, against the job's 487,802 M allocation.
- 22 of the 128 gevgen tasks returned rc 0, producing 15 G18 and 7 AR23 gst files. 3 more G18 tasks died in gntpc. The
  rest were killed inside gevgen. The per-task outcomes are in `fd/receipts-f1/run/cluster/f1b/tasks-outcome.txt` on the
  report branch.
- The tasks that finished took 656 s for 17,500 events, which is **37.5 ms per event**.

**The gate's two assumptions both failed.**
1. **Contention.** F1a's bound charged the whole pilot wall to its events, giving 12.6 ms per event for G18 and 12.9 ms
   for AR23. It multiplied that by a declared factor of 1.25. Under 128-way load the measured time was about 3.0× the
   bound.
2. **Memory was measured, and not read.** F1a's batch step recorded MaxRSS 45,610,936 K (`sacct`, job 60415571,
   `fd/receipts-f1/amendment-1/probes/probe14.out`).
   - Nobody read that number before F1b was submitted, and the first gate has no memory rule at all. **That is the real
     lesson of this STOP.**
   - The batch step's MaxRSS is its peak over everything F1a ran: the spline reduction, the spline and flux checks, two
     `gspl2root`, two gevgen pilots and two conversions. So it cannot be apportioned to one gevgen process.
   - It also does not fit F1b's evidence directly: about 3.7 GiB per process at the kill, 476 GiB over 128.
   - The amendment therefore measures RSS per process, with `/usr/bin/time -v`, and gates on that. `sacct`'s batch
     MaxRSS goes into the receipts beside it as a cross-check.

## 2. The "No Configuration available" message, explained (the director's item 2)

**The message.** Both pilots' logs carry, twice, "No Configuration available for
genie::EventGeneratorListAssembler/Default at the ConfigPool".

**Where it comes from in GENIE v3_04_00's source** (`probes/probe14.out`, `probe15.out`):
- **The warning:** `Algorithm::FindConfig` (`src/Framework/Algorithm/Algorithm.cxx`) logs it when the global ConfigPool
  holds no registry under the key `genie::EventGeneratorListAssembler/Default`, and then keeps its configuration.
- **Why the key is missing:** the global `config/EventGeneratorListAssembler.xml` says: "The Default configuration
  depends on the tune and it is defined in TuneGeneratorList.xml, which is defined in each Tune subdirectory." That file
  defines only the named special lists (CEvNS, DFR, Charm and so on), never `Default`.
- **Where the list actually comes from:** `EventGeneratorListAssembler::AssembleGeneratorList`
  (`src/Framework/EventGen/EventGeneratorListAssembler.cxx:44-77`). When `RunOpt::EventGeneratorList()` is `"Default"`,
  it adds `AlgConfigPool::TuneGeneratorList()` as its top registry. That is the key `TuneGeneratorList/Default`, which
  `AlgConfigPool::LoadTuneGeneratorList` reads from `TuneGeneratorList.xml`
  (`src/Framework/Algorithm/AlgConfigPool.cxx:237-251, :603-610`).
- **Why it is "Default":** `run_gevgen_v3.sh` passes no `--event-generator-list`, so the list is `"Default"`.

**Which list each pilot used.**
- Each tune's `TuneGeneratorList.xml` `Default` is the same list of 18 generators: `config/G18_10a/TuneGeneratorList.xml`
  and `config/AR23_20i/TuneGeneratorList.xml`.
- The 18 are QEL-CC, QEL-NC, RES-CC, RES-NC, DIS-CC, DIS-NC, COH-CC-PION, COH-NC-PION, DIS-CC-CHARM, QEL-CC-CHARM, NUE-EL,
  IMD, IMD-ANH, DFR-CC, DFR-NC, QEL-CC-LAMBDA, MEC-CC and MEC-NC.
- The laconic messenger suppresses GENIE's "** Loaded generator" lines, so the logs do not name the loaded generators.
  <!-- absence-ok: scoped to the two pilot gevgen.log files read in probe15 (a grep for "EventGenerator/" found none); it states the logs' content -->
- Which file `GetXMLFilePath` resolved for each run is not shown either.
- **The two lists are identical, though.** So the truth is the tune's own `Default` list either way, and **this is not
  a STOP**.

**The pilots' process mix,** from each pilot's gst (`probes/probe15.out`; 10,000 events per tune; the gst flags
counted over all events and over CC):

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
| events with no flag; with two or more | 0; 103 | 0; 88 | the two-flag events are the charm events |

Every process seen is in the list, and nothing outside it appears.

**AR23's negative cross sections** (`probes/probe16.out`, `probe17.out`).
- AR23's pilot logs **129** "Negative cross section for current kinematics!!" messages in 10,000 generated events.
  G18's logs none.
  - The 124 reported to the director earlier came from a count that collapsed some lines together. 129 is the direct
    `grep -c`.
- **What GENIE does with them:** `KineGeneratorWithCache::AssertXSecLimits`
  (`src/Physics/Common/KineGeneratorWithCache.cxx:266-270`) only logs the message and returns. An accept/reject test of
  the form `accept = (t < J*xsec)` with `t ≥ 0` (for example `MECGenerator.cxx:298-300`) never accepts a point with
  xsec < 0.
- **Who logs them:** the messages name only `KineGeneratorWithCache`, not the calling generator. In the 30 log lines
  before each one, the printed records hold dinucleon clusters: n+n 8, n+p 34, p+p 13. That is descriptive only.

## 3. F1a′, the re-pilot (new path `$OUT/f1a2`)

**What it reuses.** F1a's five products are reused only after they re-verify, from a clean deploy, against the
committed `fd/receipts-f1/amendment-1/f1a-SHA256SUMS`. That file is F1a's own sums file, fetched from the cluster.

| product | sha256 |
|---|---|
| `splines/G18_10a_02_11b_CH.xml.gz` | `dbd305df75dcd731a25dd0b20064ba52c20f095196ea21694997169831788c82` |
| `splines/AR23_20i_00_000_CH.xml.gz` | `f3a763e5e22e7f0246a838d6d2e8b94287f6f7137f71882dad5582cbab5439ba` |
| `flux_phi_t_0_100.root` | `06089d468525f9fe0a65f5d1f96094b3a918f288d8336dd29a40a2e8733fffbf` |
| `graphs_G18_10a_02_11b.root` | `f5840cb8970cff7554e3ea67873e6a6a70a49fdbc4dc49bd22f4978c5fd10d3d` |
| `graphs_AR23_20i_00_000.root` | `5afa412be71e5d9517336b5e5af860066d4034bd6b6b9f6423caa022f6226fd0` |

- The two spline digests are the ones F1a's spline-check recorded.
- If any of the five fails to re-verify, that is a STOP.

**The runs** (`nd-unfolding/sbatch_fd_f1a2.sh`, through `submit_fd_f1.sh f1a2 <deploy> <pin> <OUT> <priced> <ceiling>`,
with a 0:20 limit):
- Per tune, 16 processes generate 3,000 events each, and 16 generate 1,500 events twice in a row. So all 64 run
  together throughout, at F1b′'s concurrency.
- Every run is timed with `/usr/bin/time -v -o <tune>/<role>_s<seed>.time`. That records the elapsed wall, the maximum
  RSS of the gevgen and gntpc process tree, and the exit status.
- The NOWIDTH flux-check runs on all 96 work directories.
- Seeds: G18 60101–60148 and AR23 61101–61148 (`fd_f1_budget2.seeds`). They are disjoint from F1a's (60000, 61000),
  F1b′'s and the pseudo-experiments', and a test checks it.

**Is it safe to run?** F1b's 128 processes ran about 11 minutes and about 16,000 events before the kill, averaging at
most about 3.7 GiB each. 64 processes at 3,000 events stay below 64 × 3.7 GiB, which is 49 % of the node. If the
re-pilot itself runs out of memory, that is a STOP.

**The gate,** `nd-unfolding/fd_f1_budget2.py` (its docstring gives the formulas):
- **The fit:** the per-event time `t = (long wall − short wall) / 1,500` and the load `L = short wall − 1,500 t`. These
  are the maxima over each tune's runs, measured under 64-way contention. No contention factor is declared.
- **The projection:** F1b′'s wall is 2 waves × max(L + 17,500 t) + 900 s.
- **Memory:** RSS at 17,500 events = long RSS + max(0, slope) × 14,500, with slope = (long RSS − short RSS) / 1,500. F1b′
  needs 64 × that, which must be **at most 75 % of the node's 487,802 MiB**.
- **GO only if:**
  - the fit is physical (t > 0 and L ≥ 0);
  - the memory rule holds;
  - 1.25 × the wall ≤ 45 min;
  - spent + re-pilot + F1b′ + F1c's priced 0.75 ≤ the priced total the binding sets;
  - `worst_case_node_h` (spent + re-pilot + F1b′'s limit + F1c's 0:54) ≤ the ceiling the binding sets.
- **On GO** it writes `f1b2_time_limit` and `worst_case_node_h`. Anything else is a STOP.
- `sacct`'s batch MaxRSS for F1a′ goes into the receipts beside the per-process records, as a cross-check.

## 4. F1b′ (new path `$OUT/f1b2`) and what follows

- **The tasks:** the same 128 as the bound F1b, with the same seeds, **60001–60064 and 61001–61064**, at 17,500 events
  each. They run at most 64 at once (`xargs -P 64`), in two waves. Each task is timed with `/usr/bin/time -v`.
- **Guards:**
  - the script refuses unless `budget2.json` says GO with concurrency 64, and unless F1a's five products still
    re-verify;
  - it refuses if `f1b2/` exists;
  - it never reads `f1b/`. **The 22 partial gst files are never read.**
- **Everything after generation is F1b's, unchanged:** the NOWIDTH flux-check on all 128, the gst counts, `hadd`,
  `gen5d_v3.py convert` with its sampling test, and `fd_f1_prep.py`.
- **F1c** is the bound F1c. The receipt commit's tables come from `f1b2/prep`, and the rule that the receipt commit
  touches only `fd/receipts-f1/` stands.
- **The grade** is the bound grade.

## 5. Code and tests at this commit

**New:**
- `nd-unfolding/fd_f1_budget2.py`
- `nd-unfolding/sbatch_fd_f1a2.sh`
- `nd-unfolding/sbatch_fd_f1b2.sh`
- `nd-unfolding/tests/test_fd_f1_amend.py`, 12 tests:
  - `/usr/bin/time -v` parsing;
  - the seeds, checked against the script's arithmetic;
  - GO, and a STOP from each rule on its own, with every number recomputed;
  - the memory boundary;
  - the run-record refusals;
  - the scripts' constants against the gate's: event counts, concurrency, never touching `f1b/`, exactly five reused
    products, and the submission lines.

**Changed:** `nd-unfolding/submit_fd_f1.sh`, which gains the stages `f1a2` and `f1b2`. Its f1a, f1b and f1c lines are
unchanged.

**Unchanged:** every other F1 file, including `fd_f1_budget.py`, the bound gate.

**Tests and mutants:** `fd/receipts-f1/amendment-1/tests-local.log` (this module, plus `test_fd_f1.py`'s 31 and
`test_fd_f0_regrade.py`'s 47) and `mutants.log`. The deploy step runs every declared suite on a login node, as the
binding requires.

## 6. Re-priced budget

| stage | expected node-h | cap (scheduler limit) |
|---|---:|---:|
| spent: F1a 0.104722 + F1b 0.202778 | 0.3075 | 0.3075 |
| F1a′ re-pilot | 0.08–0.17 | 0.33 (0:20) |
| F1b′, 2 waves of 64 | 0.45–0.66 | ≤ 0.75 (from the gate, at most 0:45) |
| F1c | 0.68–0.75 | 0.90 (0:54) |
| **F1 total** | **1.52–1.89** | **ceiling 2.29** |

- **Assumptions.** These are estimates, not measurements: F1b′'s range assumes 20–35 ms per event at 64-way load. The
  gate replaces the estimate with the re-pilot's fit before any production job runs.
- **Joseph's ceiling is 2.5 node-h in total.** The caps sum to 2.29, within it.
- **For the re-binding, I propose `<priced>` = `<ceiling>` = 2.5.** The gate then STOPs if either the expected total or
  the worst case would pass Joseph's ceiling. A tighter `<priced>` is the director's to set.

## 7. For the director

1. The re-pilot's design: 64 processes, two event counts, a fitted load, and linear RSS extrapolation with no credit
   for a falling slope.
2. The memory rule at 75 % of the node.
3. Reusing F1a's five products after re-verification.
4. Reusing F1b's seeds in `f1b2/`, never reading `f1b/`.
5. The generator-list finding in §2, as not a STOP.
6. The re-priced table, under Joseph's 2.5, and the `<priced>` and `<ceiling>` values to bind.

## 8. Review

An independent read-only review is folded in before the PR (§9).

## 9. Review dispositions

(Filled at review.)

# COV2D amendment, rolling audit part 4: the pilot (5fe67700, 13927a0e)

**Auditor:** the `coverage-5b-audit` session, 2026-11-04, read-only. Its report, received by SendMessage, is copied
verbatim below. The answers and fixes are in `ANSWERS.md` (this directory).

---

COV2D audit part 4 (the pilot, 5fe67700 + 13927a0e): two medium findings, both able to produce a false STOP or a false PASS. Part 3's J1 is partly closed.

How I checked:
- Fresh detached worktree. test_cov2d_pilot and test_cov2d_jobs: 19 OK, 5 skipped (no PyROOT here).
- RealParser with ROOT stubbed for the import only: all 1,580 lines pass, including the pilot's 8.
- I ran REPRICE on part B's real ledger. 0 .pyc afterwards.

**Findings, most severe first**

**P1 (medium; part B's records): the §9.12 universe control runs at a different CPU count from its reference.**
- P912_U_MaRES_0 is in lane 3, at **64** CPUs. Part B's reference U_MaRES_0 ran at **128** (partb_runs.tsv, J2b.1).
- RE-2 only ever states equality "against a run on the same CPU count" (RE2-DECLARATION.md:234; RE2-J0-REPORT.md:128, noise ≤ 6.4e-13 "at the same CPU count"). I found no record showing 64 vs 128 agreeing to ≤ 1e-8.
- It may well agree: OMP_NUM_THREADS=64 in both lane sizes, and LightGBM's default threads follow OpenMP. But a failure here is (c)'s second STOP, which ends (c).
- The other two controls are matched: P2b (64) = ER (64), and P912_L (128) = S3_BeamAngleX0 (128).
- What would close it: run P912_U at 128 CPUs, or get the equivalence on record first.
  - The cheap layout: move it into lane 1, giving 1678 + 1678 + 1150 = 4,506 s. That is a limit of 01:41:00 (1.68 node-h), inside the 2.0 reserve and the 02:00:00 ruling.

**P2 (medium; RUN): a failed non-control run doesn't make the pilot INVALID.**
- main's verdict looks only at the three COMPARE products (cov2d_pilot.py:114–148).
- reprice() keeps only rc = 0 rows (:74), so a class whose runs failed just disappears.
- Run: with X_G18, T_G18_5720000, B_G18_001 and U_G18_Flux_0 at rc = 1, reprice returns lateral and central only, with replica, toy and universe absent. Nothing in main turns that into INVALID, so the verdict can be PASS.
- §9.13 makes any crash, OOM, kill or time-out INVALID.
- Part 3's J3 makes this worse: walls.tsv records the lane's sticky rc, so one failure also hides that lane's later successes.
- What would close it: all 8 runs with rc 0 and a digest, and every class present in REPRICE, or the verdict is INVALID.

**P3 (low-medium; computed): the REPRICE baselines don't measure what the pilot measures.**
- **Central and toy.** partb_wall_per_run gives J1 = 910 s per run: 3 runs in 4 lanes, so each run's wall is the whole job, preflight included. The pilot's walls are run-only (t1 − t0 per srun step). With the declared 300 s preflight, the effective trigger on run time is about 1.25 × 910 / 610 ≈ 1.86, not 1.25.
- **Universe.** The baseline is J2 at 128 CPUs (879 s). Both pilot universe runs are at 64, and the bulk universes run at 128. So the pilot doesn't measure the bulk's class wall, and the 64-CPU wall can fire REPRICE spuriously.
- **The J7 basis is not a 64-CPU universe measurement.**
  - Your "universe-type runs at 64 CPUs rest on part B's J7 (1,121 s per run)": partb_runs.tsv's J7 has 35 runs at 128 CPUs (S4U_*) and 4 at 64 (S4CV_s*, which are central-type).
  - So 43,714/39 is a mixed average, not a measurement of a 64-CPU universe run.
  - PILOT_EST is defined but never used.

**P4 (low-medium; reading): the staged side of dvs-rate is probably a page-cache read.**
- In cov2d_job.sbatch, check runs first. For the pilot it re-hashes the whole staged lat0 through O_NOATIME, about 54 GB (538.4 GB / 10).
- dvs-rate then reads that file's first 4 GiB, which on a 512 GB node is very likely still cached. The CFS side is cold.
- What would close it: time the staged copy cold (check's own re-hash timing is a cold full read), or run dvs-rate before check, or report the CFS rate alone.

**P5 (low; a 0 node-h pre-pilot check worth doing).**
- The control's same_cell_set (re2_k1.compare) requires each part B reference's own positive cells to equal E_R's 205.
- If U_MaRES_0's or S3_BeamAngleX0's reported set differs from E_R's, the control fails even when the pilot reproduces part B bitwise. Again a STOP.
- A login-node read of those two pinned products (O_NOATIME copies, flatnonzero of hXSec2D vs E_R's) settles it before the pilot.

**P6 (still open from part 3 J1): nothing refuses a bulk job before the pilot's readout.** Two parts of J1 are now closed:
- the gate sees the pilot, since it's a jobs_pilot.tsv row;
- the G18 pseudo-data PASS comes before the pilot in practice, because the pilot's check needs G18's pseudo_b.json and data files.

**P7 (low; reading):**
- **A retyped rule.** The pass rule (:131) retypes re2_k1.check_row's `le` rule. It is equivalent for hXSec2D, but it is a second implementation.
- **Reads without O_NOATIME.** The readout reads the pilot's own products by read_bytes and ROOT. These are new lane files, so it's harmless, but they aren't on §7's list.

**Your choices**
- **Eight runs in three lanes:** P1 for the universe control.
- **The limit, 01:17:00:** correct by the rule (longest lane 3,356 s), giving 1.28 node-h ≤ 2.0.
- **Part B's wall per run:** the formula is as you state. See P3 for preflight inclusion and CPU counts.
- **The cell set:** E_R's cells for all three comparisons, as §9.12 says. See P5.
- **Verified with no finding:**
  - $K2A pinned at 7eb39088 and hashed by check;
  - E_R pinned at a5c13fc3, through pw.PINS, which equals re2c_rollup.py:110;
  - the (2b), lateral and universe argv equal part B's J1, J3 and J2 rows plus --data-file;
  - DATA_TRUTH=G18 routes the pilot's data files;
  - the dvs-rate failure is descriptive, as ruling (b) says.

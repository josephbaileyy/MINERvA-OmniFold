# COV2D amendment, rolling audit part 3: the job scripts (9e1cb595)

**Auditor:** the `coverage-5b-audit` session, 2026-11-04, read-only; nothing was submitted. Its report, received by
SendMessage, is copied verbatim below. The answers and fixes are in `ANSWERS.md` (this directory).

---

COV2D audit part 3 (the job scripts at 9e1cb595): one medium finding, about the pilot and step order. Your pilot commit (part 4) may already address it, and I'll check it there. Nothing was submitted.

How I checked:
- test_cov2d_jobs: 13 passed and 1 skipped locally (no PyROOT).
- I ran the skipped RealParser test with ROOT stubbed for the import only: all 1,572 lines pass re2_driver's real argparse.
- Every class's argv is byte-identical to part B's partb_runs.tsv, apart from --data-file: central = J1 ER, universe = J2a, lateral = J3, replica = J4 (all 300 share one argv modulo the seed). A toy's argv is the central's with its own data file.
- UNI_STAT equals part B's preflight/inputs.stat row, whose sha is 220c479e.
- Afterwards there were 0 .pyc.

**Findings, most severe first**

**J1 (medium; reading): neither the pilot nor the order of steps 5–6 is in the route, and the charge gate cannot see the pilot.**
- COV2D-DECLARATION.md:40 forbids "the bulk before the amendment's binding and the pilot's readout". §10 step 6 orders the bulk: pseudo-data first, then the $UNI readers.
- cov2d_submit.sh:12 checks only binding 2, and any table job can go in any order.
- §8's cap includes "≤ 2.0 for the pilot", but the gate's sacct query keeps only the table names and cov2d-pseudo_* (submit:19). A pilot under any other name is invisible to "spent".
- The gate's limits[name] raises KeyError for an unknown cov2d-* name, so widening the filter would crash rather than count.
- What would close it: the bulk refused without a committed pilot-readout record, and the pilot's attempts counted by the gate.

**J2 (low-medium; reading): the pseudo-data job reads $UNI without checking which file it is.**
- cov2d_pseudo.sbatch:21 runs step A first and never calls check.
- cov2d_pseudo.py checks the constraint and ratio digests (:203–209) and $UNI's POT and branches (:227, :233), but not its stat or hash.
- Step A is the read that defines every toy's nature.
- What would close it: the unfold jobs' stat check (cov2d_jobs.py:162–167) run before step A, with a stop on mismatch.

**J3 (low-medium; RUN): walls.<lane>.tsv records the lane's sticky rc, not each run's own** (cov2d_job.sbatch:31, :45–46).
- I extracted the script's own lane() with sed and ran a 3-run lane with srun stubbed to fail only r1.
- The walls file reads "r1 1, r2 1, r3 1", but r2 and r3 succeeded.
- This is §8's REPRICE input, so a filter on rc = 0 drops every run after a lane's first failure.
- Part B's lane has no walls file; the bug is in this addition. A per-run rc fixes it.

**J4 (low; reading): the E3 reset doesn't reach step A.**
- Step A runs before cov2d_preflight (pseudo.sbatch:21–23). OMP, MKL and OPENBLAS threads are inherited through --export=ALL.
- Its TMPDIR, $O/tmp/$SLURM_JOB_ID, doesn't exist yet: only the preflight creates it, and that runs after step A. Step A uses no tempfile (grep), so this is harmless today.
- What would close it: the same exports and `mkdir -p "$TMPDIR"` before step A.

**J5 (low; reading): the tables are reused if present (submit:15), and check never ties $RUNS to M.**
- Failure scenario: tables from an earlier deploy drive the bulk with the old argv and limits.
- What would close it: record M in the tables, or regenerate and compare at submission.

**J6 (note; computed): the campaign must be submitted in waves.**
- The 24 limits (U 08:54, L 03:20, B 08:06, T 07:38, pseudo 03:00; all under 12 h) sum to 178.27 node-h, against the 165.8 cap. The projected wall is 143.6.
- The gate charges a queued job at its limit, so the last submissions will be refused while earlier jobs are queued.
- The 8 universe jobs plus 2 pseudo jobs come to 77.2 node-h of limits, which is fine for 2026-12-01. Worth stating in the amendment.

**J7 (note):**
- The pseudo job doesn't check its own QOS or TimeLimit, as cov2d_job.sbatch:22–25 does.
- check leaves two files unclosed (:137 runs_tsv, :142 stats; ResourceWarning in the tests).

**Your choices**
- **$UNI stat, not re-hash:** I agree. The constant is part B's record, and a mismatch stops the job, which is stricter than part B's re-hash fallback.
- **Toys at J1's argv:** verified, as above.
- **The central in the lateral job's 128-CPU lanes:** fine. The lanes are 9,256 s and 8,390 s, for a limit of 03:20:00.
- **The limit rule:** it reproduces part B's limits (the test passes).
- **The gate's accounting:** ended attempts are charged at ElapsedRaw × NNodes and unfinished ones at their limit, which is right for exclusive one-node jobs. See J1.
- **The pseudo job at 03:00:00:** this is §8's reserve.
- **Step B and MnvH1D:** a TH1D fixture can't show this. The cheap cover, with the director's go, is a login-node, 0 node-h, O_NOATIME call of load_flux_bins on the real 5,143-byte runEventLoopMC_MEFHC.root:
  - once in the pinned MAT environment, which must give the bins;
  - once in plain root_6_28, to see whether the class matters.

  Record both before the pilot.
- **(2a)'s kept file:** I found no bulk job that reads it, so I agree it needn't be in check, provided the pilot is gated before the bulk (J1).

Verified with no finding:
- cov2d_preflight checks, in order: the deploy, the MAT setup before sourcing, and the MAT environment after. It then resets TMPDIR and threads to part B's values.
- The staging record is pinned by sha (3614ebad) through O_NOATIME.
- The staged $CV and the laterals are re-hashed through O_NOATIME. A missing file stops the job with no re-stage.
- The data files are checked against pseudo_b.json, and $MC and $FLUXU against their pins.
- Everything is regular QOS, CPU only, under 12 h, with nothing written to CFS.
- --mem is part B's formula.

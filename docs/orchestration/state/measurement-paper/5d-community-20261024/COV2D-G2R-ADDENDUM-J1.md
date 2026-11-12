# COV2D-G2R addendum J1 (DRAFT): the jobs, the cap gate, the environment test and the P5 file check (2026-11-12)

**By** the `cov2d` session, as a draft for coverage-5b-audit and the director's binding. Binding 1 addendum C1 (ruling 2)
requires a second addendum, J1, before any connect. J1 must carry:
- the job scripts and the cluster-environment test (numpy 1.26 and the LightGBM end-to-end check);
- the cap gate at 110 node-h;
- the P5 per-playlist file check, a STOP if the files are gone;
- C1's six unexecuted lines;
- n8.

The director approved the design on 2026-11-12, items 1–5: namespace and names, the jobs, the gate, the environment
test, and the docstring. §9 lists where this draft departs from that design, and why.

**The code:** under `2d-unfolding/cov2d/g2r/jobs/` and `tests/`, at code commit `a0d43dcfff76dc8d8c36ab9c59307bc702e40a2a` (the envtest rule after the audit's B1; first draft `a14a08e5`):
- `g2r_jobs.py`: the tables, the job-side check, the order, the gate, the environment test's comparison and the
  products TSV;
- `g2r_env.sh`, `g2r_job.sbatch`, `g2r_envtest.sbatch`, `g2r_prepare.sbatch` and `g2r_submit.sh`;
- `test_g2r_jobs.py` and `g2r_jobs_mutation.py`.

Nothing in amendment 1's bound code changes: `re2_driver.py`, `g2r.py`, `g2r_prepare.py` and `g2r_readout.py` stay at
M_C1's bytes.

**MEASURES:** the job layout, its price and its gates, on the bound code. **CANNOT AUTHORIZE:**
- any connect or submission: each connect comes to the director with its sha256 and diff before it runs;
- adopting C_new or any coverage wording: reserved for Joseph, binding 1 ruling 5.

## 1. The jobs

The namespace is `$P/cov2d-g2r-20261112`, and every job is named `cov2dg2r-<job>`. The director checked at main
`347c11c4` that those names match every lane's "cov2d" fence: RSN, RDX, E96D, `cov2d_fence.sh`, and LL5D's pilot from
its fill on. They do not start with `cov2d-`, so COV2D's own gate (`cov2d_jobs.gate`, which refuses an unknown `cov2d-*`
name) never sees them.

| job | runs | lanes × CPUs | limit | held (node-h) | what |
|---|---:|---|---|---:|---|
| `envtest` | 2 | 2 × 128 | 01:04:00 | 1.067 | §4: MaRES:0 at the data, through the pre-patch driver and through the patched driver with the flag off |
| `prepare` | 0 | — | 02:00:00 | 2.0 | the declaration's §6 step 1: `g2r_prepare.py` on `$UNI` and P5's 12 per-playlist files |
| `D_Ua`–`D_Uc` | 44 each | 2 × 128 | 08:54:00 | 8.9 each | part (a): part B's own J2 rows (`partb_runs.tsv`, read at `526b70e0…`), with their jobs, lanes and CPUs, plus `--miss-map $MAP` |
| `D_Ud` | 43 + 2 | 2 × 128 | 09:18:00 | 9.3 | part (a)'s last 43, then the two override-off reruns at the end of the second lane |
| `G18_Ua`–`G18_Ud`, `AR23_Ua`–`AR23_Ud` | 44, 44, 44, 43 each | 2 × 128 | 08:54:00 | 8.9 each | part (+): COV2D's own universe rows and packing (`cov2d_jobs.pack`, imported), plus `--miss-map $MAP` |

- **The noise floor's two override-off reruns,** named here before any run as the declaration's §3 requires:
  - **Flux:23**, the Stage C pilot's `P2_Flux23` reference;
  - **MaRES:0**, P5's and COV2D 9.12's reference universe.

  Each is part B's own row, exactly, with no map. They run at part B's 128 CPUs, so they are compared like for like.
- **Limits** follow part B's rule (`cov2d_jobs.limit_of`: 1.25 × (longest lane + 300 s), rounded up to the minute) on
  part B's per-run estimate of 1,150 s. The prepare's limit is fixed.
- **The environment test's estimate** is the measured full-read universe unfold, max 2,738 s
  (`2d-closeout/stageB/REPORT.md:174`), because each of its lanes reads `$UNI` cold.
- **Each run** goes through the OI-136 guard (`mnv_guarded_run.py`) with its deploy as the only admitted tree. Each run
  records its sha256 and its wall, as COV2D's jobs did. A product that already exists is never overwritten.

## 2. The order

`g2r_jobs.order` enforces it at every submission, and `g2r_submit.sh` runs each job once:
1. `envtest`.
2. `prepare`: only once the environment test's record, committed at `fd/receipts-cov2d/g2r/envtest/envtest.json` on
   origin/main, reads PASS.
3. `D_Ua`: only once the prepare's record, at `fd/receipts-cov2d/g2r/prepare/g2r_prepare.json` on origin/main,
   reads PASS. The map's sha256 is taken from that record (`map_npz_sha256`), never typed. Each unfold job checks the
   map against it before any run.
4. **Every other unfold job:** only once D_Ua's first `--miss-map` run has finished with rc 0 and its product is on
   disk. That run is **the LightGBM end-to-end check on the real map.** No local test can train, because there is no
   LightGBM here, and this keeps 174 jobs' worth of runs from starting before one has trained through the override.

(a) and (+) are independent, as the declaration's §6 says. After step 4, the director orders the jobs, under the cap.

## 3. The cap gate at 110 node-h

`g2r_jobs.gate` runs in `g2r_submit.sh` before every sbatch.
- **What it prices:** only `cov2dg2r-*` attempts. An unknown `cov2dg2r-*` name is refused, because the gate cannot
  price it.
- **The charge:**
  - ended attempts at their elapsed node-h;
  - unfinished attempts at their limits;
  - submitted ids that sacct does not list yet, at their limits (the sacct-lag ruling, in code this time);
  - plus this job's limit.

  The total must be at most 110.
- **One job per call.** After its sbatch, `g2r_submit.sh` returns only once sacct lists the new id. It polls every
  10 s for 10 minutes, and otherwise returns rc 6 so the failure can be reported.
- **The director's rule:** "the gate must count the prepare's and the environment test's actual charge, not their
  projections. If the projection after the prepare exceeds 110, STOP to me."
  - For every unfold job, the gate also projects the whole campaign: what is spent, plus what is held, plus every job
    not yet submitted, at its limit.
  - A projection over 110 is **rc 9, a STOP to the director, not a trim**, even when the job alone would fit.
  - Held after the prepare: 3 × 8.9 + 9.3 + 8 × 8.9 = **107.2 node-h**. So the environment test's and the prepare's
    actual charges together must be at most 2.8 node-h. Expected: about 0.75 and at most 1.
- **The independent recompute** (the director's ruling 3 of 2026-11-06) is the connect's: spent from sacct, held from
  unfinished attempts and from submitted ids that sacct does not list. The stricter of the two totals governs.

## 4. The cluster-environment test

The test comes before the prepare, and its cost is inside the 110.
- **On a login node, in the connect,** under the jobs' own `root_6_28` environment (its numpy is 1.26):
  - the four G2R suites: `test_g2r`, `test_re2_miss_map`, `test_g2r_glue` and `test_g2r_jobs`;
  - the numpy and ROOT versions are printed.

  The local receipts are on numpy 2.4.4. This is the numpy 1.26 half of C1's requirement.
- **The `envtest` job:**
  - MaRES:0 at the data, part B's argv, through the pre-patch driver: `re2_driver.py` `938c53c5…` at COV2D's deploy
    commit `PRE_M = a6054769…`, in a clean checkout `$O/deploy-pre`;
  - the same run through the patched driver with the flag off (M_C1's `e226daf3…`);
  - both on one node, in the same environment, in two lanes of 128 CPUs.
- **The comparison,** `g2r_jobs.envtest`, under RE-2's bound rule (`ENVTEST_TOL` = 1e-8). The director ruled it on
  2026-11-12, after the audit's B1:
  - every histogram's contents and errors: max |a − b| / max |b| ≤ 1e-8, the metric of RE-2's `le` checks
    (`RE2-J0-REPORT.md:79`);
  - every TParameter: |a − b| ≤ 1e-8 × max(|a|, |b|);
  - every TNamed whose value is JSON (`runConfig`, `re2Refinement`, `branchSelection`, and `p1Streams` if present),
    leaf by leaf: floats to 1e-8 relative, while integers, booleans, strings and keys must be exactly equal;
  - every other TNamed must be exactly equal, except `driverFile`, `driverSha256`, `omnifoldHelperFile` and `runArgv`,
    which name the code and the paths and differ by design;
  - `runConfig` must agree once `out` is set aside;
  - the patched run's `miss_map` must be null, and its file must carry no `g2rMissMap`;
  - the helper's sha256 must be equal.

  Whether each object is also bitwise is recorded (`bitwise`, `all_bitwise`) and does not decide. This is G1 on the
  cluster, with real LightGBM.
- **Why not bitwise (the audit's B1).** Configuration (a) is LightGBM's non-deterministic mode
  (`RE2-DECLARATION.md:42`). RE-2 measured same-CPU reruns of this driver at 1.88e-14 and 6.36e-13 (`CHK-det1`,
  `CHK-det2`, `RE2-J0-REPORT.md:106-107`), and `re2Refinement` carries LightGBM outputs. A bitwise rule would have
  spent the environment test on a STOP with no verdict on G1.
- **The rule's power.**
  - The tolerance sits about 4 orders above the measured rerun noise.
  - It sits 5 to 6 orders below a real flag-off failure: P5 measured the override against the proxy at MaRES:0 as a
    per-cell change of median 1.6e-3 and max 2.8e-2 (`stageB/diagnostics/p5/result/report_s42.json`).
  - RE-2's power checks moved hXSec2D by 1e-2 to 2.2e-1 (`RE2-J0-REPORT.md:128`).
  - The tests hold the boundary (the director's condition): 0.5e-8 and 0.99e-8 PASS, and 2e-8 is INVALID, for a
    histogram, a TParameter and a JSON leaf. Mutants that loosen the tolerance to 3e-8 or tighten it to 0.4e-8 are
    killed, and so is one that puts it back to 0.
- The LightGBM end-to-end check **with** the override is D_Ua's first run, gating the rest (§2, step 4).

## 5. The P5 per-playlist file check

- **The stat-only reading** (login10, 2026-11-12T13:21:13Z): all 12 `runEventLoopOmniFold_{1A…1P}_universes_full.root`
  exist under `$P/MINERvA-OmniFold/2d-unfolding/`. The paths come from P5's `sbatch_p5.sh`. **No STOP.**
- **Their exposure:** their atimes are 2026-10-14T23:11–23:24Z, so the purge exposure is **2026-12-09T23:11Z**
  (atime + 8 weeks, `FD-CT-RETENTION.md` §2). That is ten days before `$UNI`'s 2026-12-19. The prepare reads them
  through O_NOATIME, which does not move the date. Only the prepare reads them, and the director will give it a slot
  well before then.
- **At run time:** a missing file is `g2r_prepare.py`'s rc 7, the director's STOP. `g2r_prepare.sbatch` passes that rc
  through unchanged, with 5 INVALID and 8 atime, and nothing after it is submitted (§2).

## 6. What each job reads (G9)

- **Every check in a job** goes through O_NOATIME (`cov2d_jobs.noatime_sha256`): `$MC` and `$FLUXU` against RE-2's
  pins, the map against the committed record, and each tune's realization against COV2D's committed step-B record
  (G8). `$UNI` is stat-checked only, against part B's DTN record of size, mtime and inode.
  - The two realization files are on pscratch: `cov2d-run-20261104/pseudo/G18/b/data_5721000.root` and
    `…/AR23-a2/b/data_5731000.root`, stat-read 2026-11-12. A missing one is a problem the job stops on; G8's
    regeneration by the bound writer is its own connect.
  - **Unlike** `cov2d_jobs.check`, it reads no staging record, so no plain read is left.
- **The driver's own reads,** as COV2D's §7 listed them:
  - `$UNI`, `$MC` and `$FLUXU`;
  - for a tune, the realization;
  - for a `--miss-map` run, the map;
  - the helper and the MAT setup, from the deploy.
- **The prepare** reads `$UNI` and the 12 files through O_NOATIME, and its own atime ledger is rc 8.
- **The readout** runs on a login node and reads each product at its digest (`read_pinned`). `g2r_jobs.py products`
  writes its TSV from the jobs' SHA256SUMS files.

## 7. C1's six unexecuted lines (amendment 1 §2a, unchanged)

| file | line | what | why |
|---|---|---|---|
| g2r_prepare.py | 137 | an atime move sets STOP, rc 8 | the stand-in reads restore atime; the receipt run on `$UNI` shows the ledger |
| g2r_readout.py | 246 | C_T' not PSD appends a control failure | needs a non-PSD C_T' from real products |
| g2r_prepare.py, g2r_readout.py | 144, 343 | `if __name__ == "__main__": sys.exit(main())` | each `main` is tested |
| re2_driver.py | 845 | "not every finite entry was applied" | unreachable: the override is applied before any `continue` (P5 recorded the same) |
| re2_driver.py | 1441 | the truth column's length differs from the tree's entries | unreachable through RDataFrame on the tree itself |

J1's own code leaves none. `g2r_jobs.py`: every executable line is run by `test_g2r_jobs.py`, counting the runs inside
its fixture deploy (receipts, §11). The four shell scripts cannot be line-traced. Each refusal and exit path of theirs
is run by a named test against stubs, listed in the receipts README.

## 8. n8, and one stale docstring

- **n8 (the audit's low):** at a tune, `g6_tune` (`g2r_readout.py:90-99`) holds `C_univ`, **and also `C_T` and
  `C_T_minus`**, to 10⁻¹² relative. The declaration's §8 words G6 for `C_univ` only, so the code is stricter than that
  wording. It is stated here, not changed.
- **The docstring:** `g2r_readout.py:13` still says G6 reproduces those blocks "bitwise". The code applies 10⁻¹² relative
  (`G6_TOL`, :87) and records whether each block is bitwise (amendment 1 §2a). The docstring is stale text in audited
  code. As the director ruled, it is stated here and **no byte is changed**: `g2r_readout.py` stays at `590ffba1…`.

## 9. Where this draft departs from the approved design

1. **The two override-off reruns end D_Ud's second lane, not a separate D_F job at 00:31:00.**
   - A single-run job reads `$UNI` cold, and a full-read universe unfold measured up to 2,738 s, so 00:31:00 (1,860 s)
     could time out, which is INVALID.
   - Part B's J2d.2 holds 21 runs, so the two reruns join it warm. D_Ud's limit becomes 09:18:00.
   - Cost: +0.4 node-h on D_Ud in place of D_F's 0.52.
2. **The environment test's limit is 01:04:00 (1.067 node-h), not 00:31:00,** for the same cold read.
3. **The LightGBM end-to-end check with the override** is D_Ua's first run, gating every other unfold job, not a run
   inside the environment test. The environment test runs before the prepare, so no real map exists yet.

## 10. Price

- **Held** if every job were pending at once: 110.27 node-h (`g2r_jobs.py tables`).
- **Held after the prepare:** 107.2 node-h. Expected charge: 74–94 node-h (the declaration's §7).
- **The gate's STOP fires** if the environment test's and the prepare's actual charges together pass 2.8 node-h.
- Every `$UNI` read must end before 2026-12-19, and the prepare's read of the 12 files before 2026-12-09.

## 11. Tests, mutants and coverage (`fd/receipts-cov2d/g2r/j1/`)

From a clean detached checkout of the code commit `a0d43dcfff76dc8d8c36ab9c59307bc702e40a2a`, on macOS with
`/opt/homebrew/bin/python3.13`, ROOT 6.36.000 and numpy 2.4.4:
- `test_g2r_jobs.py`: 55 tests, OK, rc 0, at PYTHONHASHSEED 0, 1 and 2;
- `g2r_jobs_mutation.py`: 37 mutations, all killed. They cover the tables, the check, the order, the gate, the comparison
  and the four shell scripts. The unmutated suite ran in full, and the sources were restored byte-identical;
- the coverage sweep: 0 of 394 executable lines of `g2r_jobs.py` never executed, counting 2 byte-identical copies in the
  tests' fixture deploys. The README maps each shell path to its test;
- amendment 1's suites at the same commit: `test_g2r` 27, `test_re2_miss_map` 11 and `test_g2r_glue` 18, OK, and
  `g2r_mutation.py` 23 of 23 killed.

## 12. For the director

1. Bind J1 and its code at a merge commit, written **`**M_J1 = \`<40-hex>\`**`** in COV2D-G2R-BINDING-1.md:
   `g2r_submit.sh` refuses unless origin/main's binding names its deploy's commit on exactly that line.
2. The connects (environment test, prepare, unfold submissions) come to you one at a time, each with its sha256, its
   diff and the independent recompute, after the audit reads them, as COV2D's did.
3. Reserved for Joseph, unchanged: adopting C_new and the wording of any changed coverage sentence.

Nothing is submitted, deposited or tagged.

# S2R connect package (tier3-design, 2026-11-24): for the director's GO

Under `../S2R-DECLARATION.md`, the director's acceptance of the candidate and threshold, and route (1)'s approval in
principle (2026-11-24). **Nothing has run on NERSC.** Each script below goes to the director with its sha256. Each
connect needs the director's GO with a window epoch, and a fence round with acks from cov2d, limitation-resolver and
director-helper-3.

## The deploy commit and the bound files

**M = `4017c0825444c4e88742801653bf088075c197ed`** (lane/s2r-step2-20261124, pushed). The submit connect clones M and
checks these files, with digests from `git show M:… | shasum -a 256`, never typed:

| file (under `nd-unfolding/`) | sha256 |
|---|---|
| `s2r/s2r_arm.py` | `33fdc2c0119ab02ca0f815fa4c3c5a4e906b473689219c43573824773ebc35be` |
| `s2r/s2r_probe.py` | `6894f2aeee87986b9705925eed34c40bc5b2127324789468cc3df0861bcb75e9` |
| `s2r/s2r_read.py` | `734b0e8b5a1cb634d44cf43f02bc69aef64cd07bb34005a1c5897c88058f97bf` |
| `s2r/s2r_rule.py` | `fbb649fcb7e16e119ab4fd14a58dadc6eeab2dc262030a71dce2e3cc2a314785` |
| `s2r/sbatch_s2r.sh` | `fb78e311763e9eba2d56a0a232d24dc938c6b63abe0d286b85156774aa43ff0a` |
| `s2r/test_s2r.py` | `e126533491753342a774fb3096b86e79f0839ba9eca6e36621ae7e2fd29859ce` |
| `tier3/t3p_arms.py` (T3-BINDING-1) | `4a685bde238dcc6dc25e9b1121029994f33becafab486cbec1a7bf846206bf84` |
| `tier3/t3p_probe.py` (T3-BINDING-1) | `e27bf07a3e2c60320a749355eaedceed5a36574d2d8fa83675bd4b4721985bd2` |

The declaration at M is `S2R-DECLARATION.md`, sha256 `16c7f5fb62e4b62aa9ee34dd62a16be15f49b598b8437f716bb99d51cf7970cd`.

## The connects

| script | sha256 | what it does |
|---|---|---|
| `s2r_submit.sh` (from `s2r_submit.template.sh`, filled from git and shasum) | `fa3fbaf75a60ee5ea277240579b785909b5d468e22be76e9da263f464079b4d7` | fence, iris, clone at M, bound digests, 58 tests, the pins check of every input (dd iflag=noatime, stat unmoved), env, fence.txt, the limit, one `sbatch` with Slurm option variables unset, then the TimeLimit and no-array checks |
| `s2r_fetch.sh` | `b5c9f5bc717ac5ad97959c17873b9b02528ba1d1e8d23ee5a76b54505444c4f3` | after the job: COMPLETED by sacct, DONE without STOP/FAILED, the readout present, the 6 product sums, then the records copied through dd iflag=noatime into one tar |
| `s2r_launch.sh` (from the template, with both connects' sha256) | `f8cd325dc9874cb2fbc823b105f408c66d5433b376808e94f154dc44516c552b` | saul then a loginNN; the /dev/shm copy is checked at its sha256 on the node; the remote side exits with the script's rc; for fetch, the tar, log and done are streamed back, the tar's sha256 must equal the log's, its sums must hold, and the done file must be 0 |

- **Usage:** `bash s2r_launch.sh submit <new empty dir> <loginNN> <window_end_epoch> cov2d,rpd_,d2s0,covfix`, then, after
  the job, the same with `fetch`.
- **The fence prefixes** are cov2d, rpd_, d2s0 and covfix, plus s2r_ in the code. They do not name ibub_, as the
  director ruled: the overlap check below is CLEAR against IBUB's set.
- **The job.** `s2r_run`, one exclusive CPU node, `--time=01:00:00` from `s2r_probe.py limit`.
  - Six tasks: B0 at k = 5 and S2R traced to k = 20, at nominal, A7_gibuu and q3, split 991000.
  - The steps, in order: stage, queue, gate, run, SHA256SUMS, C-PAIR/C-X/C-ONE, the in-job read, DONE.
- **The price.**
  - Lane budgets are 700 s (B0) and 2,100 s (S2R, k = 20). The lane wall is 0.58 h. The least limit (/0.9, +0.25 h)
    is 1.0 h.
  - **The cap is 1.0 CPU node-h.** About 0.6 is expected, from T3's measured 190 s + k × 78.5 s per lane.
- **Writes:** only `/pscratch/sd/j/josephrb/s2r-20261124`, including `tmp/` and `tmp-connect/`, plus the launcher's
  `/dev/shm/s2rc.<pid>.sh`. Nothing goes to CFS.
- **Job states:** sacct only. The connects call `scontrol show job` once, for the TimeLimit, as T3's did. Nothing calls
  squeue.

## The reproduction control

C-PAIR: B0's k = 5 unfold must equal FD-PRR's B0 product **bitwise**, at FD-PRR's thread count (32) and seed (42),
at each of the three truths. It is a job step. A failure STOPs the job before the read. The pass rule's ρ_B0 is this
job's B0.

## Checks before the GO (records in `read-checks/`, `standin/` and `overlap-s2r.txt`)

- **Tests at M:** `test_s2r.py` gives 58 OK in a clean detached worktree (`read-checks/tests-at-M.txt`).
  `test_s2r_overlap.py` gives 2 OK.
- **End-to-end smoke** (`read-checks/e2e-smoke-at-M.txt`, `s2r_e2e.py`).
  - The job's own task path ran with real LightGBM 4.7 on FD-STAB's synthetic fine-grid inputs, through
    `s2r_probe.run` → `s5p_nullexp.main` → refinement → traced unfold → product.
  - B0 and S2R ran at nominal and q3. All four gave rc 0 with a product, the s2r block and `refinement.ran`.
  - C-X held bitwise. C-ONE agreed to ≤ 4.4e-16. C-ARM's round trip was ≤ 1.3e-15 at all 20 S2R iterations.
  - ROOT was stubbed for the smoke only, because the refinement's import of the 2D driver needs it.
  - On these weak synthetic inputs the trees find no split, so S2R equals B0 at k = 5. The smoke shows the plumbing
    works, not the mechanism. `test_s2r.py` shows the arms differ on the stand-in estimators.
- **The codex-school read** of 37affb03a (`read-checks/codex-read-r1.md`) found 2 blockers, 4 majors and 2 minors.
  All were addressed in aa225eb07:
  - the saturation STOP;
  - Slurm option variables unset, and the array check;
  - the alternative's path and kind, and the output, pinned in the namespace check, and OUT pinned in the job;
  - the remote rc propagated, and the fetch requiring rc 0 and done 0;
  - TMPDIR under OUT;
  - T0 set before staging;
  - SHA256SUMS and DONE checked;
  - the k = 5 snapshot required;
  - the two tests strengthened.

  The recheck of aa225eb07 (`read-checks/codex-recheck-r2.md`) resolved both blockers, majors 2 and 4, and both minors.
  It left two items open and found two new majors. All four were fixed in 4017c0825 and the connects:
  - `--out` is pinned to `<OUT>/runs/<arm>/<truth>` exactly, by realpath, with OUT from the stage record;
  - the declaration's write list now names the launcher's /dev/shm copy;
  - the overlap prefix rule now matches '-' and '.' terminated prefixes, which catches /dev/shm/ibubc.*;
  - the fetch checks every sum append and the sums' line count, and the launcher verifies with `shasum --strict` and
    checks the record count.
- **Hand mutants** (`read-checks/mutants.txt`): 10 of 11 are killed. The survivor removes "ν_0 = 1 at k = 1". It is
  equivalent, because the reference check already requires ν_0 = w_push = 1 at k = 1.
- **The end-to-end smoke caught one bug** before the commit. The new output-root pin compared a resolved stage path
  with an unresolved `--out`, and macOS's /var → /private/var symlink made them differ. Both sides are now compared by
  realpath, which also covers a symlinked /pscratch.
- **Stand-ins** (`standin/`): Debian containers running the real connects, with stubs only for the scheduler, iris,
  git's clone URL, conda and planted pins. The per-variant results are in `standin/README.md`.
- **The overlap check** (`overlap-s2r.txt`, `nd-unfolding/s2r/s2r_overlap.py`) is CLEAR: 1,639 pairs, 0 hits.
  - "Theirs" is IBUB's own composition, including its 19 declared entries for ibub-20261124, both phases.
  - Allowed overlaps:
    - the shared interpreter;
    - three cov2d-protected reads of FD-PRR's inputs (of_inputs_5d.npz, bkg_dump.npz, bank cv.npz), read once
      through O_NOATIME and never written, as FD-PRR and T3 read them. **cov2d's ack at the fence round should name
      them.**

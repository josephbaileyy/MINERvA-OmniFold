# COV2D BINDING 2: the amendment's code, the job scripts and the pilot (director, 2026-11-05)

**Binds** [`COV2D-AMENDMENT-1.md`](COV2D-AMENDMENT-1.md), sha256
`777317bebaec0ad64feb1dba98eb9c9ceb3fbfeadd720e0f7d9b88e7c51a03cf`, and the code it lists, as on main at:

**M = `cb31611ca8b96ed2d1eeb809fda7236e56645863`** (the merge of #778; code commit `5c0e02a2`)

**Under** [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md) §10 item 4, [`COV2D-BINDING-1.md`](COV2D-BINDING-1.md) and
[`COV2D-BINDING-1-A1.md`](COV2D-BINDING-1-A1.md). The amendment merged in #773 (`e9cadf47`). F3 merged in #776
(`8a258b38`), and its M-line tightening in #778.

## What the director checked

- **The digest.** The amendment's sha256 at M is the one above.
- **Every blob.** All 25 rows of the amendment's §9 tables (15 code files and 10 test files) equal their blobs at M.
  So do all 12 imported modules of §1: `re2_driver.py` `97f26a1d`, `cov2d_writer.py` `bb3892e5`, `cov2d_receipt.py`
  `d5718bf4`, `fd_1b_null.py` `1810161d`, `fd_1b_mc.py` `74aa8dac`, `re2c_rollup.py` `e41940cb`, `build_cmodel.py`
  `7a987e25`, `re2_k1.py` `62a1dc33`, `fd_rpd_inputs.py` `7c2e018f`, `s5e_deform.py` `2c11f9f6`, `pvl_lib.py`
  `81d509ba`, and `clip_probe.py` `f5683876`.
- **The audit** (coverage-5b-audit): parts 1–4, the final audit, the F1/F2 delta, F3 and its tightening. All are
  closed and nothing blocks (`fd/receipts-cov2d/amendment/AUDIT-*.md`).
  - F3, the submit script's binding check, was a fixed point. It was found by the director while drafting this
    binding, and no test reached it. The check now reads this file from origin/main after a fetch that must succeed,
    and binds M only on the line above.
- **The receipts at `5c0e02a2`:** 155 tests, 0 skipped. Mutants: 64 of 64 killed, 10 of them REQUIRED, and the
  harness exits 1 on any survivor.
- **The time limits** are written `HH:MM:SS` (`cov2d_jobs.limit_of`, `cov2d_pseudo.sbatch`). Every job checks its own
  `scontrol` TimeLimit and stops on a mismatch.

## Rulings

1. **The amendment is bound at M,** with the rulings it carries (§2), REPRICE before the bulk, and §7's statements.
   The deploy is a fresh clean checkout at M.
2. **The order is as `cov2d_jobs.order` enforces it, with the director told before each connect:**
   1. **The G18 pseudo-data job.** Its connect's sha256 comes to the director first.
   2. **The pilot,** after G18's pseudo-data PASS record is on main. Its connect's sha256 comes to the director first.
   3. **The pilot readout,** which comes to the director before the bulk (binding 1 ruling 1). The bulk opens only on
      PASS with `reprice_classes == []`. A REPRICE class goes to an amendment.
   4. **The bulk,** in the amendment's waves, after the director has read the pilot readout. Each connect's sha256
      comes to the director.
   - An `order()` admission is necessary but is not the director's go.
3. **The price.**
   - The cap stays at **165.8 node-h** (binding 1 ruling 3), and the gate prices every cov2d job.
   - The KillWait overrun is accepted as a disclosure, not a block: each job unfinished at the last submission adds at
     most its grace, for example 22 × 60 s = 0.37 node-h. The amendment states the grace as an assumed example (§5). The readout reports the final
     charge from sacct.
   - The charge stays far below half the balance. This is an operational go-ahead within the standing grant, reported
     to Joseph with this binding.
4. **The cluster lane is `cov2d`** for every job, as for control (2a) and staging.
5. **Tests in the cluster environments, before the G18 job.** This is binding 1 ruling 4's pattern, at 0 node-h, from a
   fresh clone at M on a login node, with no pscratch or CFS reads:
   - run each suite in the environment §8's table names for it;
   - name every environment;
   - commit the logs, the node, and the porcelain before and after as a receipt.

   A failure is fixed and reported before any connect. It cannot be shown away by running the suite in another
   environment.
6. **The STOP count stands at one** (CONTROL-2A, 2026-11-03). A second STOP ends (c) unless Joseph rules otherwise.
   - (2b) or §9.12 failing in the pilot is that second STOP.
7. **The schedule** of §10 is bound, including its terminal branch:
   - no `$UNI`-reading job submitted by 2026-12-01 means no bulk, and a report;
   - `$UNI` is exposed from 2026-12-19.
8. **Unchanged:** binding 1's rulings 5–7 (schedule, retention and HPSS, the paper and the note).

Nothing is submitted, deposited or tagged.

# Binding, amendment 1: F1 after F1b's out-of-memory STOP (2026-10-28)

**By** the paper-tighten lane, as director.

**Under:**
- `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` (PR #431), item 1: option (A), with a ceiling of
  2.5 node-h for F1 in total, the 0.3075 already spent included;
- [`FD-F1-BINDING.md`](FD-F1-BINDING.md) (PR #429), which this amends.

**Binds** [`FD-F1-DECLARATION-AMENDMENT-1.md`](FD-F1-DECLARATION-AMENDMENT-1.md), merged in PR #434. Its file sha256
begins `2060a15e8c99925c`.

**MEASURES:** nothing. It authorizes F1a′ (the re-pilot), F1b′ only on its gate's GO, and then F1c, the grade and the
HPSS copy as bound in `FD-F1-BINDING.md`.

**CANNOT AUTHORIZE:**
- any charge above §3's ceiling;
- any read of `f1b/`, the STOP's evidence;
- a rerun or repair after a STOP;
- anything `FD-F1-BINDING.md` cannot authorize.

## 1. The bound code

**The deploy pin** is `4b7a9892ef4d739afc45f6bfb6cc5f8d7a36fe54`, main after PR #434. `OUT` is unchanged,
`/pscratch/sd/j/josephrb/fd-f1-20261027`. The new deploy is `D2=$OUT/deploy/4b7a9892`, a clean clone of the pin, and
`$D2` must not exist beforehand.

**At the PR head `4953ed59`, the director checked:**
- the declared test modules, locally with `-I -B` and a TMPDIR: `test_fd_f1_amend.py` **13 OK**, `test_fd_f1.py`
  **31 OK** and `test_fd_f0_regrade.py` **47 OK**, with 0 porcelain lines after;
- the bound F1 gate and scripts (`fd_f1_budget.py`, `sbatch_fd_f1a.sh`, `sbatch_fd_f1b.sh`) unchanged from `main`;
- `submit_fd_f1.sh f1b2`: it requires GO, the re-pilot job COMPLETED in `sacct`, and its batch MaxRSS at most 75 % of
  487,802 MiB. It takes the time limit from the gate.
- the scheduler record of the STOP: job 60417614 `OUT_OF_MEMORY` after 12:10, batch MaxRSS 499,490,432 K; job
  60415571 COMPLETED in 6:17, batch MaxRSS 45,610,936 K. The 0.3075 node-h spent is confirmed.

## 2. Rulings on §7

1. **The corrected cause is accepted.** The OOM came at gevgen's start-up. F1a's MaxRSS was measured and set aside. The
   three gst-less tasks stalled and were ended by teardown. It supersedes the measurement session's first account.
2. **P = 14 is accepted,** with one stated risk. F1a's 43.5 GiB peak is a 30 s sample for two processes, and the split
   between them is not measured. If one process carried most of it, the re-pilot itself can OOM. That would cost at
   most its 0:20 limit, 0.33 node-h, inside the ceiling, and it is a STOP like any other. The re-pilot is what measures
   it.
   <!-- absence-ok: a scoping statement about F1a's sampled peak (sacct job 60415571 records one batch-step MaxRSS, not a per-process split); no claim that a result is absent -->
3. **The memory rule at 75 % of the node,** with the sacct cross-check in the submit line, is accepted.
4. **Reuse is accepted:** F1a's five products, after their digests re-verify against the committed `f1a-SHA256SUMS`,
   and F1b's seeds in `f1b2/`. `f1b/` is never read. Seeds 60010, 60011 and 60050 are reused under the per-task
   timeout, and a repeat stall is a STOP that the report names by seed.
5. **The generator-list finding is accepted: not a STOP.** Each tune ran its family's own `TuneGeneratorList.xml`
   `Default`, the two files being byte-identical. The pilots' process mix lies within its 18 generators, and AR23's 129
   negative-cross-section points are never accepted. The report restates §2's table.
6. **The prices:** `<priced>` = **2.0** and `<ceiling>` = **2.5** node-h.
   - The ceiling is Joseph's.
   - The priced total is set at 2.0, not 2.5, so that the cost rule can still fire. The amendment's expected
     1.73–1.92 fits under it. A re-pilot that projects F1 above 2.0 is a STOP to the director, which comes before the
     ceiling is reached.
   - The expected cost is above the 1.45–1.65 the director quoted to Joseph. The director reports this to Joseph. It
     stays within his ceiling and needs no new decision.

## 3. Budget

- **Priced:** 2.0 node-h, enforced by `fd_f1_budget2.py` on the re-pilot's measurements.
- **Ceiling:** 2.5 node-h, Joseph's. It is enforced by the gate's worst-case rule: spent + the re-pilot + F1b′'s limit +
  F1c's 0:54.
- **Any job that reaches its scheduler limit or a per-task timeout is a STOP.**

## 4. Conditions

1. **Deploy and tests** (login node):
   - clone the pin to `$D2`, detached. HEAD must equal the pin, with 0 porcelain lines, ignored files included;
   - re-verify F1a's five products against `fd/receipts-f1/amendment-1/f1a-SHA256SUMS`, and re-measure the original
     declaration's §8 digests;
   - run `test_fd_f1_amend.py`, `test_fd_f1.py` and `test_fd_f0_regrade.py` at `$D2` with root_6_28's Python, `-I -B`
     and `TMPDIR=$OUT/tmp2`. They must give 13, 31 and 47 passing, with 0 porcelain lines after;
   - `$OUT/f1a2` and `$OUT/f1b2` must not exist;
   - anything else is a STOP.
2. **F1a′:** `submit_fd_f1.sh f1a2 $D2 <pin> $OUT 2.0 2.5`. A gate STOP, a failed run, a timeout or a non-zero exit
   comes to the director with `budget2.json`, unrepaired.
3. **F1b′,** only on GO: `submit_fd_f1.sh f1b2 $D2 <pin> $OUT`.
4. **F1c, the grade, the HPSS copy and the report** follow `FD-F1-BINDING.md` §4, items 4–9. They read `f1b2/prep`, and
   the receipt commits keep its path rule.
5. **The report adds, beside the bound items:**
   - the re-pilot's measured per-process RSS and full-task wall, against the gate's limits;
   - sacct's batch MaxRSS and elapsed time for every job;
   - the total charge against 2.0 and 2.5;
   - the STOP's receipts from `fd/f1-report` `183b31e4`, with their ledger rows;
   - §2's generator-list table.
6. **Ledger** rows go in `fd/LEDGER.tsv`. **Retention:** `fd-f1-20261027` stays on the pscratch list, now with
   `f1a2/`, `f1b2/` and the untouched `f1b/`.

The steps may start once this record is on `main`.

## Not changed

- F1 is a bias test, not a coverage test. Its grading, seeds for F1c, held-out group and rulings in
  `FD-F1-BINDING.md` §2 stand.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.

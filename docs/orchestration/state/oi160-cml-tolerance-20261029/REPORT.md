# REPORT — OI-160 for `C_ML`: the one split-replica producer reads CORRECTED (2026-10-30)

**By** the close-items session, for the director, who takes it to Joseph
(`DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md`, #515, item 2).

**Under:** [`DECLARATION.md`](DECLARATION.md) (sha256 `c665e7c126fa4b92…`, #517) and [`BINDING.md`](BINDING.md) (#519),
at the deploy pin `eb2282e1eedf89c51dda67102fd7f682bbc04976`.

**CITABLE FOR:**
- which committed `seedscan_split.py` reproduces each of the five graded stored split replicas within the declared
  tolerance, today;
- the producer's verdict under the declared table (§3.3), and the limits stated in §6.

**NOT CITABLE FOR:**
- the 19 split seeds not graded, beyond what the producer's verdict covers by inference;
- `C_stat`, which #515 closed;
- whether either contract is correct;
- any change to `C_ML`, `C_stat` or the trunk.

This report draws no conclusion about `C_ML` beyond the declaration's §3.3 reading. What follows from it is Joseph's
decision.

## 1. The outcome, from `run/out/readout.json`

> **`producers`:** `55849763`: `CORRECTED`
>
> **`overall`:** `CORRECTED`
>
> **`fresh_floor_ok`:** `true`

Every seed's `why`, verbatim: *"the corrected code (07c18aee) reproduces it within tolerance; the old code does not"*.

| seed | producer | separation | verdict | corrected vs stored: max rel, zero pattern | old vs stored: max rel, zero pattern | corrected vs old: max rel |
|---:|---|---|---|---|---|---:|
| 4 | `55849763` | SEPARATED | **CORRECTED** | 6.46e-12, equal | 0.115, equal | 0.115 |
| 9 | `55849763` | SEPARATED | **CORRECTED** | 5.79e-13, equal | 0.0764, equal | 0.0764 |
| 14 | `55849763` | SEPARATED | **CORRECTED** | 3.11e-12, equal | 0.0835, equal | 0.0835 |
| 19 | `55849763` | SEPARATED | **CORRECTED** | 2.71e-12, equal | 0.141, equal | 0.141 |
| 24 | `55849763` | SEPARATED | **CORRECTED** | 3.37e-12, equal | 0.116, equal | 0.116 |

- **The criterion:** max-relative over the union-nonzero bins ≤ τ = 1 × 10⁻⁸, plus an identical zero pattern
  (DECLARATION §3.2). The largest corrected-code distance, 6.46 × 10⁻¹², is 1,548× inside τ.
- **The old code** keeps the stored zero pattern on every seed. It misses on the distance clause alone, by 0.0764 to
  0.141.
- **Every seed's stored `train_frac` is 0.8,** the declared value.
- **V1, the fresh floor of `seedscan_split.py`** (split seed 1, the corrected code twice): max-relative
  1.57 × 10⁻¹², zero patterns equal. The limit is τ / 100 = 1 × 10⁻¹⁰. **Passed**, so τ holds (ruling 1).
- **V2, separation:** the two codes differ on every seed by at least 0.0764, against a minimum of 100 τ = 10⁻⁶. Every
  seed is SEPARATED; none is COINCIDENT or GREY.
- **Descriptive only, not part of the criterion,** from `readout.json`:
  - the medians of the same distances: corrected vs stored 2.7 × 10⁻¹⁴ to 2.9 × 10⁻¹³; old vs stored, and corrected vs
    old, 4.7 × 10⁻³ to 5.5 × 10⁻³;
  - the floor's median, 8.3 × 10⁻¹⁴;
  - the floor's maximum, 1.57 × 10⁻¹², is of the same order as the `C_stat` run's 1.43 × 10⁻¹² for `bootstrap_nd.py`
    (#506) and the first run's K1 maximum of 3.0 × 10⁻¹² (DECLARATION §3.2).

**The §3.3 hypothesis this matches:** *"If the corrected code wrote them and `random_state` matters: CORRECTED, with
V1 holding and every seed SEPARATED."* Its §3.3 meaning, unchanged: *"the 24 replicas behind `C_ML` rest on the
corrected contract, within §4's limits, as `C_stat`'s do."*

## 2. The job

- **Array:** `60530414`, tasks 0–5, QOS `shared`, 36 CPUs each, `--no-requeue`, no GPU. Submitted once from `login37`
  at 2026-10-30T03:39:50Z (`run/logs/submit-session.txt`).
- **Result:** every task COMPLETED `0:0`, and no task logged a STOP (`run/logs/task*.log`).

| task | role | elapsed | unfolds (A / B) |
|---:|---|---|---|
| 0 | fresh floor, seed 1 | 00:27:56 | 14:20 / 13:22 (A twice) |
| 1 | seed 4 | 00:19:12 | 10:06 / 8:58 |
| 2 | seed 9 | 00:22:44 | 11:30 / 11:06 |
| 3 | seed 14 | 00:23:56 | 12:19 / 11:31 |
| 4 | seed 19 | 00:16:47 | 8:31 / 8:10 |
| 5 | seed 24 | 00:23:59 | 11:46 / 12:04 |

- **Charge, per task** (`run/logs/sacct.txt`, `billing=36,cpu=36,mem=64G,node=1` on every task): elapsed × 36/256 =
  0.0655, 0.0450, 0.0533, 0.0561, 0.0393 and 0.0562 node-h for tasks 0–5.
- **Total:** Σ elapsed 2.243 h × 36/256 = **0.315 node-h**, against the declaration's 0.5 expected and 1.27 at most. The
  longest task took 28 min of its 1:30:00 limit.
- **Unfold walls:** 8:10 to 14:20. Five of the twelve fall inside the stored run's range of 472–680 s (7:52 to 11:20)
  per unfold; the other seven are above it, by up to 3 min.
- **Deploy** (`run/logs/deploy.log`, `run/logs/deploy-session.txt`, `login37`, 2026-10-30T03:38:54Z):
  - `$T` was absent beforehand;
  - HEAD equalled the pin;
  - 0 porcelain lines before and after the tests;
  - all seven §7 digests matched, and `DECLARATION.md`'s is `c665e7c1…`, as `BINDING.md` binds;
  - `tests rc=0`, *"Ran 13 tests in 0.429s"*, *"OK"*.
- **Controls P0–P3 passed in every task:**
  - P0: the four code digests and `repro_run.py`'s `649b1291…`;
  - P1: the input's 1,548,438,020 bytes and mtime epoch 1782610308;
  - P2: each task's stored-replica digest;
  - P3: 36 CPUs of affinity, with `OMP_NUM_THREADS` unset.
- **Provenance** (`run/out/*.provenance.json`, all twelve, identical in these fields): `preimported_under_lib: true`,
  `modules_under_forbidden_root: []` (P4), LightGBM 4.6.0, affinity 36, `OMP_NUM_THREADS` unset, `script_exit: 0`.
- **Grading** ran on `login37` at 2026-10-30T05:01:14Z, after every task had ended (`run/logs/grade.log`, `grade rc=0`;
  `run/logs/grade-session.txt`). It was the first time any graded replica was opened.

## 3. Ruling 2: INERT

No seed read INERT: the two codes separate on every graded seed. The ruling's condition did not arise. Had the codes
coincided and both matched the stored replica, that would have been a full answer.

## 4. Ruling 3: five seeds, one producer

**`55849763`'s verdict rests on five graded seeds, 4, 9, 14, 19 and 24.** The other 19 of its 24 split replicas are
covered by inference only, from that verdict. None of them was opened or compared.

- **Seed 1** was used only for the same-code floor, the corrected code against itself. Its stored replica was not
  graded.
- **No replacement seed was needed** (DECLARATION §1).

## 5. Ruling 4: the CPU count and the F2 configuration, beside the verdict

**The verdict is CORRECTED at 36 CPUs, under the production estimator configuration.**

- **The CPU count.** `sbatch_seedscan_split_5d.sh` at `07c18aee` reads `--cpus-per-task=16`, but every `55849763` task
  ran with `cpu=36` per `sacct` (DECLARATION §1). By `sacct`, then, the stored run was not submitted with the committed
  launcher's `--cpus-per-task`, or that value was overridden at submission. This run reproduced at 36, the shape `sacct`
  records. It did not try 16 CPUs, so it cannot say whether the count changes the output at τ, and it does not
  establish which launcher bytes submitted `55849763`.
- **The F2 configuration.** `KNOWN_ISSUES.md` 79 (s5e) found per-estimator seeds *"bitwise inert"* under the s5c F2
  configuration. F2 adds `bin_construct_sample_cnt` set to every row, `deterministic=True`, `force_row_wise=True` and a
  fixed `num_threads` (`nd-unfolding/s5c_unfold.py:54-60`). Both codes here ran the production configuration, with those
  parameters at the library defaults.
- **What was measured.** Under the production configuration, changing only LightGBM's `random_state`, from the split
  seed to 42, moved every graded replica by a max-relative of 0.0764 to 0.141. That is the A-vs-B column of §1.
- **What was not measured.** This run says nothing about F2 or about KI-79's finding, which was measured under F2. The
  mechanism the declaration gave, that the default `bin_construct_sample_cnt` of 200,000 makes the bin boundaries depend
  on `random_state`, was not isolated here.
  <!-- absence-ok: a scoping statement about this run's own measurements, not a claim that a result does not exist -->

## 6. Limits, restated beside the outcome

- **The 19 ungraded seeds** are covered only by inference from the producer's verdict (§4).
- **`C_stat`** is not in scope. #515 closed it.
- **A reproduction shows which code ran, not that it was correct.**
- **Today's environment** reproduced the stored replicas to 6.46 × 10⁻¹² at most. That bounds nothing about other
  environments.
- **Nothing here changes `C_ML`, `C_stat` or the trunk.**

## 7. Files and storage

**Committed under `run/`:**
- `out/readout.json`;
- the twelve `*.provenance.json` and the twelve reproduced npz files;
- `logs/`: `deploy.log`, `deploy-tests.log`, `task0`–`5.log`, the twelve unfold logs, `grade.log` and `sacct.txt`;
- the deploy, submit and grading session transcripts.

**Checks on the committed files:**
- **Not committed:** the scheduler's per-task `.out` and `.err` files. All twelve are empty (0 bytes).
- **Force-added:** the npz files and `.log` files match the repository's `*.npz` and `*.log` ignore rules, so they are
  added with `git add -f`.
- **Byte-identical to `$T`:** all 47 files copied from `$T` match by sha256.
- **Graded npz files:** each one's sha256 equals the digest `readout.json` records for it, ten of ten.
- **Control files:** the two carry no digest. Re-running `cml_compare.measure` on them reproduces the readout's
  `fresh_floor_control_split1_A_twice` entry exactly.

**Storage:** the run directory `$T = /pscratch/sd/j/josephrb/oi160-cml-20261029` is kept until this report merges. It
is removed afterwards, after a byte comparison of everything committed against main, unless the director says otherwise.
Nothing was written to CFS or to the canonical checkout, and nothing was resubmitted.

# DECLARATION — OI-160 for `C_ML`: a pre-declared tolerance run on the split replicas (2026-10-29)

**By** the close-items session, OI-160's owner, for the director to bind.

**Under:**
- Joseph's decision [`DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md`](../../DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md)
  (#515), item 2: *"`C_ML` is checked the same way."* His selected option was *"Close; check C_ML too (Recommended)"*.
  The director's implementation note there makes it one pre-declared tolerance run with a fresh same-code floor
  control, because a bitwise step can only return VOID (K1 of the first run).
- The director's request of 2026-10-29:
  - the 24 split replicas' producers, named from metadata only;
  - a few unseen seeds per producer;
  - τ and V1/V2 fixed from a floor for `seedscan_split.py` itself, with a statement of whether the `C_stat` run's
    τ = 1 × 10⁻⁸ carries over, and why;
  - both contracts' `seedscan_split.py`, at `07c18aee` and `07c18aee^`, with digests;
  - the reading tables fixed in advance;
  - shared QOS, 36 CPUs, `--no-requeue`, priced from measured walls.

**After:** the `C_stat` tolerance run, [`../oi160-tolerance-20261029/REPORT.md`](../oi160-tolerance-20261029/REPORT.md)
(#506, CORRECTED for all three producers). Its criterion, controls and wrapper are reused. Its comparer is not,
because the split replicas carry different keys and the two codes can coincide here (§3.3).

**Declares:** `cml_compare.py` (the criterion and the tables), `run_array.sh`, `test_cml.py`, `seeds.tsv`,
`stored.sha256` and `code.sha256`, all beside this file, plus the exact commands and the stops.
`metadata-session.txt` is the transcript of the §1 reads.

**MEASURES:** nothing. The tools have run only on synthetic fixtures (13 tests). Only metadata of the graded replicas
has been read: `sacct`, `stat`, and their sha256 (§1).
<!-- absence-ok: a scoping statement about this declaration's own work: nothing it declares has run on real inputs -->

**CANNOT AUTHORIZE:** running it before the binding; any change to `C_ML`, `C_stat` or the trunk.

**CITABLE FOR:** the tolerance and its reason, which split replicas are graded and how their producer was identified,
and how each result will be read.

**NOT CITABLE FOR:**
- any result;
- seeds not graded here, beyond what their producer's verdict covers;
- `C_stat`, which #515 closed;
- whether either contract is correct.

## 0. Summary

- **Five unseen split seeds** from the one array that wrote all 24, each reproduced under both codes and graded against
  its stored file: max-relative tolerance τ = 1 × 10⁻⁸, plus an identical zero pattern.
- **A fresh same-code control** (split seed 1, the corrected code twice) measures `seedscan_split.py`'s own floor on
  the day. The run is VOID if that floor exceeds τ / 100.
- **A fifth reading, INERT,** for the case this script allows and `bootstrap_nd.py` did not: the two codes agreeing
  with each other.
- **One array of 6 tasks, 12 unfolds,** on shared QOS with 36 CPUs; about 0.5 node-h expected, at most 1.27.

## 1. The graded replicas, and how their producer is identified

**All 24 split replicas have one producer, array `55849763`, named from metadata alone.** The director approved these
reads on 2026-10-29: `sacct` task rows, `stat` names, sizes and mtimes, log file names and mtimes (not their contents,
which print each replica's total cross section), and the five graded files' sha256. The transcript is
[`metadata-session.txt`](metadata-session.txt), read 2026-10-30T03:22Z on `login37`.

**The rule** (as in the `C_stat` run): a split seed belongs to an array task when that task COMPLETED and ended within
5 s of the file's mtime.

**The arrays that could have written `seedscan_split_5d/`:**
- **`55849763`** (2026-07-13): tasks 1–24 all COMPLETED 0:0, walls 7:52–11:20, `cpu=36`. **Every one of the 24 files
  has its mtime 0–3 s before its own task's end**, and equal to that task's `ssplit5d_<s>_55849763.out` mtime.
- **`55799925`** (2026-07-11): tasks 1–3 FAILED 1:0 within 9 s; tasks 4–24 CANCELLED before starting.
- **`55805464`** (2026-07-11): tasks 2–24 CANCELLED before starting. `sacct` shows no task 1.
- **`55151672`** (2026-06-28) left 24 `ssplit5d` logs in `nd-unfolding/`. That is the late-June set archived as
  `seedscan_split_5d_prehm_20260711/`.
- **`58598278`** (2026-09-19/20) also left 24 `ssplit5d` logs there. All 24 tasks COMPLETED in 520–1,552 s, at `cpu=36`
  (`nd-unfolding/pet/improvement_campaign/phase_a/receipts/resources_raw/sacct_latency_josephrb.psv:369-392`).
- **The August arrays** `57527869`, `57742558` and `57753243` ran on the member namespace.
- **None of the later arrays wrote a top-level file.** Every top-level mtime is 2026-07-13, between 03:26:16 and
  09:31:57 −0700.
- **Not read:** the 24 `res_split_<s>.npz.done` markers beside the files. Only their names were listed.

**The CPU count, and a discrepancy.** `sbatch_seedscan_split_5d.sh` at `07c18aee` reads `--cpus-per-task=16`, but every
`55849763` task ran with `cpu=36`. So the launcher that ran was not the committed one, or it was overridden at
submission. This run takes the allocation shape from `sacct`, 36 CPUs (P3). The same 36 appears for the July array,
the August member arrays and `58598278`.

**Graded seeds** (`seeds.tsv`): split seeds **4, 9, 14, 19 and 24**.
- **The rule** was fixed before any per-file metadata was read: every fifth task from 4. This spreads them across the
  array's six hours and excludes seed 1.
- **Replacements:** a seed failing the producer rule was to be replaced by the next higher seed not already graded.
  None was needed.
- **One producer means one per-producer verdict.** It covers the other 19 seeds by inference. Five seeds is
  "a few" for a producer that wrote all 24.

| task | split seed | producer | file mtime (−0700) | sha256 | identified by |
|---:|---:|---|---|---|---|
| 1 | 4 | `55849763` | 2026-07-13T03:55:58 | `77d72049…` | task `_4` COMPLETED (10:44), ended 2 s after the mtime |
| 2 | 9 | `55849763` | 2026-07-13T05:09:09 | `c059a5ac…` | task `_9` COMPLETED (7:52), ended 2 s after the mtime |
| 3 | 14 | `55849763` | 2026-07-13T06:46:59 | `1140673c…` | task `_14` COMPLETED (11:20), ended 2 s after the mtime |
| 4 | 19 | `55849763` | 2026-07-13T07:59:42 | `e58b6e99…` | task `_19` COMPLETED (9:05), ended at the mtime |
| 5 | 24 | `55849763` | 2026-07-13T09:31:57 | `5b8bc56a…` | task `_24` COMPLETED (8:25), ended 3 s after the mtime |

**What metadata cannot say:** which `seedscan_split.py` the array ran. The status log's 2026-07-12 line *"seedscan_split
fixes the estimator seed"* (`CORRECTED_UQ_PRODUCTION_STATUS.md:207` at `07c18aee`) is a narrative, not a record of the
bytes. This run answers it.

**Unseen, checked.** No earlier step compared or opened any graded file:
- In the record, the only top-level split replica opened is `res_split_1.npz`, whose keys OI-160's filing lane
  inspected (2026-08-28). This session read the five graded files' sha256 only. Seed 1 is therefore used only for the same-code floor, A against A.
- The `C_ML` build of 2026-07-13 read all 24, as production input. Nothing compared any of them with a reproduction.
- In the repository at `bab41e603`, `res_split_N.npz` appears in `OPEN_ITEMS.md` and the 2026-10-28 question (seed 1
  only), in three receipts and in `state/s5c/`. Every receipt hit is the member namespace `mii/member_k000000/` or a
  quarantine directory, and every s5c hit is that campaign's own run directory. None compares a top-level replica.
  Search: `res_split_[0-9]+\.npz` across the tree, excluding `MANIFEST.tsv` @ `bab41e603`

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`;
- `T=$P/oi160-cml-20261029`;
- `D=$T/deploy/<pin8>`, a clean clone of the binding commit;
- `H=$D/docs/orchestration/state/oi160-cml-tolerance-20261029`;
- `PY=env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node, 0 node-h)

```bash
test -e $T && { echo "STOP: \$T exists"; exit 1; }
mkdir -p $T/logs $T/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $H && sha256sum run_array.sh cml_compare.py test_cml.py seeds.tsv stored.sha256 code.sha256 DECLARATION.md \
    ../oi160-reproduction-20261029/repro_run.py
} > $T/logs/deploy.log 2>&1
cd / && TMPDIR=$T/tmp $PY -m unittest discover -s $H -p test_cml.py > $T/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $T/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $T/logs/deploy.log
```

**It must show:** `$T` absent beforehand; HEAD equal to the pin; 0 porcelain lines before and after; the §7 digests;
`tests rc=0` and "Ran 13 tests … OK". Anything else is a STOP. These tests were run locally in exactly this form, from
`/` with `-I -B`.

### 2.2 The array (submitted once)

```bash
cd $H && sbatch --output=$T/logs/%A_%a.out --error=$T/logs/%A_%a.err --export=NONE,T=$T,D=$D run_array.sh
```

`run_array.sh` carries `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G --time=01:30:00
--array=0-5 --no-requeue --account=m3246`. There is no GPU. It writes only under `$T`, with `TMPDIR` under `$T`.

- **Task 0:** split seed 1 under the corrected code, run twice (the fresh floor).
- **Tasks 1–5:** one graded seed each, the corrected code and then the old code.
- **Both codes get the stored launcher's own arguments:** `--npz of_inputs_5d.npz --split-seed <s> --train-frac 0.8
  --iters 5`. No `--estimator-seed` is passed, so the corrected code uses its default of 42, as the stored run would
  have. The old code has no such flag.
- **In total:** 12 unfolds.

**Priced from measured walls.**
- **The stored run:** `55849763`'s 24 unfolds took 472–680 s each on this shape. The August member runs of the same
  script on the same shape (`57527869`, `57753243`) took 507–1,730 s, and `58598278` in September 520–1,552 s.
- **Today:** the `C_stat` run on 2026-10-29 measured 8:31 to 28:57 per unfold of `bootstrap_nd.py`, whose two measured July
  walls (8:29 and 8:31) are of the same size as this script's. Its six two-unfold tasks took 17:45 to 53:01, a mean of 35.8 min.
- **The limit:** 1:30:00 per task is 1.55 × two unfolds at the worst wall measured for either script (about 29 min).
  The `C_stat` run's 1:05:00 limit was within 12 min of its longest task, so it is raised here.
- **Charge:** about 6 × 0.6 h × 36/256 ≈ **0.5 node-h** expected; at most 6 × 1.5 h × 36/256 ≈ 1.27 node-h if every
  task hits its limit. Both are under the standing approval.

### 2.3 Grading (login node, after every task has ended)

```bash
sacct -j <array id> -n -P --format=JobID,State,Elapsed,ExitCode,AllocTRES%60 > $T/logs/sacct.txt
cd / && $PY $H/cml_compare.py --out-dir $T/out --stored-dir $P/MINERvA-OmniFold/nd-unfolding/seedscan_split_5d \
  --seeds $H/seeds.tsv --readout $T/out/readout.json > $T/logs/grade.log 2>&1; echo "grade rc=$?" >> $T/logs/grade.log
```

The graded replicas are first opened here, after the binding.

## 3. The criterion, the controls and the readings

### 3.1 Controls (each a STOP, per task)

- **P0, the code** (`code.sha256`):

  | file | from | sha256 |
  |---|---|---|
  | `A/seedscan_split.py` | `07c18aee` | `8bb7e74cb2b85399a09b34a02253725228f83430c69a29665668f1d0fe4cdda7` |
  | `B/seedscan_split.py` | `07c18aee^` | `4fade69b69783d9d650c1d84f231f19647afc2e1ab802694dad29715f43b912d` |
  | `lib/omnifold_nn_core.py` | `07c18aee` | `24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582` |
  | `lib/xsec_nd.py` | `07c18aee` | `454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5` |

  The two helpers are byte-identical at `07c18aee^`, so one copy serves both codes. They are also the `C_stat` run's
  helpers. The wrapper is the first run's `repro_run.py`, `649b1291…`. Both contracts' scripts import only these two
  modules from the repository, and the wrapper pre-imports both from `lib/` (P4).
- **P1, the input:** `of_inputs_5d.npz`, 1,548,438,020 bytes and mtime epoch 1782610308 (2026-06-28T01:31:48Z), the
  `C_stat` run's input.
- **P2:** the task's stored replica matches `stored.sha256`. Its seed is not 1.
- **P3:** 36 CPUs of affinity, with `OMP_NUM_THREADS` unset. LightGBM's thread count is the affinity count, and the
  stored run had `cpu=36` (§1).
- **P4:** nothing is imported from the canonical checkout. The wrapper exits 3 otherwise.
- **Any unfold exiting non-zero** is also a STOP.

### 3.2 The tolerance, fixed before any graded replica is opened

**Two files agree iff** they have:
- equal `shape`, `split_seed` and `train_frac`;
- the **same zero pattern** in `xsec_flat`;
- **max over the bins nonzero in either of |x − y| / max(|x|, |y|) ≤ τ = 1 × 10⁻⁸.**

**Does the `C_stat` run's τ carry over? Yes, provisionally, and V1 decides whether it holds.**
- **No floor for this script exists.** No same-code repeat of `seedscan_split.py` at the production settings has been
  measured. The s5c stability runs (`nd-unfolding/s5c_stab.py`, `state/s5c/c-split-tasks.tsv`) ran it under the F2
  `deterministic` estimator configuration with 32 threads, which is not the stored runs' configuration.
- **Why the same τ is expected to fit.** The floor's source is the same: both scripts call the same `omnifold_loop`
  with the same LightGBM settings (100 trees, 8 leaves, learning rate 0.1), the same `xsec_nd` extraction, the same input
  and the same 36-CPU shape. The one step `seedscan_split.py` adds is the training subset, drawn by numpy's
  `default_rng(split_seed)`, which is deterministic. So the floor should be of the order the first run measured for
  `bootstrap_nd.py` (K1: median 2.8 × 10⁻¹³, maximum 3.0 × 10⁻¹²), and τ sits about 3,300× above that maximum.
- **Why that is not assumed.** Fitting on a subset changes which events reach each tree. If that makes the fits more
  sensitive to the thread-order rounding, the floor would be larger. So τ is used only if this script's own fresh
  floor passes V1.

**Validity, checked on the day:**
- **V1, the fresh floor of `seedscan_split.py`.** Task 0's two runs must have the same zero pattern and a max-relative
  of at most τ / 100 = 1 × 10⁻¹⁰. Otherwise **every reading is VOID**, and a new declaration fixes τ from the floor this
  run measured.
- **V2, separation per seed, read from A against B:**
  - **SEPARATED** if the two codes differ by a max-relative of at least 100 τ = 1 × 10⁻⁶;
  - **COINCIDENT** if they agree by the criterion above;
  - **GREY** if they fall between, which voids the seed.

**Why COINCIDENT is read, not voided.** In `bootstrap_nd.py`, `07c18aee` changed both the estimator seed and the
data-resampling streams, so the codes had to separate: #506 measured a max-relative of 1.00 on every seed, and the
first run a median of 7.4 × 10⁻³. In `seedscan_split.py` it
changes only LightGBM's `random_state`, from the split seed to 42; the training subset comes from the split seed under
both. Whether `random_state` moves the output at these settings is not settled in the record:
- **For:** with the 5D throws held fixed and only the estimator seed changed, `s_proj` moved about 6 %
  (`EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md`). That was the throw path, not this script.
- **Against, but under a different configuration:** `KNOWN_ISSUES.md` 79 (s5e, 2026-09-26) found per-estimator
  seeds *"bitwise inert"*. That was measured under the s5c F2 configuration, not the one that wrote these replicas.
  - **F2** (`s5c_unfold.config_params`, `nd-unfolding/s5c_unfold.py:54-60`) adds four LightGBM parameters:
    `bin_construct_sample_cnt` set to every row, `deterministic=True`, `force_row_wise=True` and a fixed `num_threads`.
  - **The stored replicas** used `make_estimators` as committed: 100 trees, 8 leaves, learning rate 0.1, `verbose=-1`
    and `random_state`, with every other parameter at the library default. That is the configuration `s5c_unfold`
    calls `production`, which adds nothing.
  - **Why the difference can matter.** By LightGBM's documented defaults, `bin_construct_sample_cnt` is 200,000. A fit
    with more rows draws the rows its bin boundaries come from using a seed derived from `random_state`. F2 uses every
    row, which removes that dependence. So F2's *"bitwise inert"* does not transfer to the production configuration.
    This is the library's documented behaviour, not measured here; this run measures it for these five seeds.

If the codes coincide on a seed, which code wrote it is unanswerable but immaterial: that replica is the same under
either contract.

### 3.3 The readings, fixed in advance (`cml_compare.py`)

**Per seed, when V1 holds:**

| A vs B | A agrees with stored | B agrees with stored | verdict |
|---|:-:|:-:|---|
| SEPARATED | yes | no | **CORRECTED** |
| SEPARATED | no | yes | **OLD** |
| SEPARATED | no | no | **NEITHER**: a third producer or environment |
| COINCIDENT | yes | yes | **INERT**: the contract does not change this replica |
| COINCIDENT | no | no | **NEITHER** |
| COINCIDENT | one of the two | | VOID: a boundary case |
| GREY | any | any | VOID |

A seed is also VOID if either reproduction is missing. A missing B output, from the old code's SKIPPED path, cannot
show separation.

**Per producer:**
- if every non-VOID seed has the same verdict, the producer takes that verdict;
- if all its seeds are VOID, it is VOID;
- if its seeds disagree, it is **MIXED**: that producer did not write with one code.

**Overall:**
- VOID if V1 fails or every producer is VOID;
- otherwise the producers' common verdict, or **MIXED**.

**What each outcome means for `C_ML`**, which this run reads but does not change:
- **CORRECTED:** the 24 replicas behind `C_ML` rest on the corrected contract, within §4's limits, as `C_stat`'s do.
- **INERT:** `C_ML` is the same under either contract for the graded seeds, so the contract question does not bear on it.
- **OLD, NEITHER or MIXED:** `C_ML` does not rest, or does not wholly rest, on the corrected contract. What follows is
  Joseph's decision.

**Expected under each hypothesis:**
- **If the corrected code wrote them and `random_state` matters:** CORRECTED, with V1 holding and every seed SEPARATED.
- **If `random_state` does not matter at these settings:** INERT.
- **If the old code wrote them and `random_state` matters:** OLD.
- **If neither committed code ran, or today's environment differs:** NEITHER.

## 4. What this run can and cannot show

**Can:** for each graded seed, which committed `seedscan_split.py` reproduces its stored replica within τ in today's
environment, or that both do. From that, a verdict for the one producer.

**Cannot:**
- **The 19 seeds not graded.** The producer's verdict covers them by inference.
- **`C_stat`:** closed by #515.
- **That either contract is right.**
- **Any change to `C_ML`, `C_stat` or the trunk.**
- **Seed 1:** it is used only for the same-code floor, A against A.

## 5. The readout, `oi160-cml-tolerance-readout/1`

`$T/out/readout.json` holds:
- the criterion's constants;
- the fresh floor, and whether it passed V1;
- per seed: its producer, its separation class, its verdict and reason, the A/stored, B/stored and A/B measures,
  whether the stored `train_frac` is 0.8, and the file digests;
- the producer verdict and the overall outcome;
- `not_citable_for`.

**Committed in the report's PR:** the readout, the provenance files, the reproduced npz files, the logs and
`sacct.txt`, under `run/` here. They are force-added past the `*.npz` and `*.log` ignore rules, and checked with
`git ls-tree` before the report says they are committed. The report restates §4's limits beside the outcome.

## 6. Code and tests

- **`cml_compare.py`:** the criterion (`measure`), the separation class (`separation`), the tables (`seed_verdict`,
  `producer_verdict`, `overall_verdict`), and the pinned-digest refusal.
- **`run_array.sh`:** P0–P3, the per-task unfolds through the first run's `repro_run.py` (P4), and the STOPs.
- **`test_cml.py`, 13 tests, synthetic, both directions.** Run from `/` as `-I -B -m unittest discover -s <dir>
  -p test_cml.py`, as §2.1 runs them:
  - the per-seed CORRECTED, OLD and NEITHER verdicts;
  - one reading across the producer;
  - coincident codes that both reproduce read INERT, and that both miss read NEITHER;
  - coincident codes with only one reproducing, and codes in the GREY band, void the seed;
  - τ from both sides (0.99 τ agrees, 2 τ does not);
  - a differing zero pattern disagrees even within τ;
  - a different `train_frac` disagrees;
  - a high fresh floor voids everything (V1);
  - MIXED within a producer;
  - a missing old-code output is not agreement;
  - a stored file that is not the pinned one is refused.
- **Mutation check:** deleting the COINCIDENT branch from `separation` fails 2 of the 13.

## 7. Pinned bytes

The pinned files are below. `DECLARATION.md`'s own digest is recorded in `deploy.log` at §2.1.

| file | sha256 |
|---|---|
| `run_array.sh` | `8c237939118eb1c79d28c297fb423fc0fdba8158d03571b01a0f31ac223f28b6` |
| `cml_compare.py` | `2a5a8343300ba647d12b95c1a1de35a3797769d7f59d8973d891ac1e628380e4` |
| `test_cml.py` | `d8656ecb9461b39e3d4011a1c7e3d5fe905ebf7fefe9bb59e72b042c2315f0ad` |
| `seeds.tsv` | `4bc994b1ceccd93df4df7fd4f2c80ede897c1d7d2cb459bd4b780b0852052227` |
| `stored.sha256` | `f8107e3612a302446f63c5adab6809b905a1a3c7503e446dbbe28ce27e420ac5` |
| `code.sha256` | `1b4c781e0d2420e91c3b8c1f2c41b9d2e0973e78580e4b0f8b6221c15df8968b` |
| `../oi160-reproduction-20261029/repro_run.py` | `649b12916b4fe43df1626f9809d89817ba3e57ee04238be793918eaa968396ae` |

## 8. Storage, cost and stops

- **Storage:** about 1.2 MB under `$T`. No CFS write; nothing in the canonical checkout.
- **Removal:** `$T` is removed after the report merges, unless the director says otherwise, after a byte comparison of
  everything committed against main.
- **Cost:** §2.2, about 0.5 node-h, at most 1.27.
- **Stops:** any STOP in §2.1 or §3.1; any task not COMPLETED 0:0; past the limit. A STOP is reported unrepaired, and
  nothing is resubmitted without a new binding.

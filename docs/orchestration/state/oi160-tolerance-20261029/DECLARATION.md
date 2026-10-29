# DECLARATION — OI-160: a pre-declared tolerance run on unseen replicas (2026-10-29)

**By** the close-items session, OI-160's owner, for the director to bind.

**Under:**
- Joseph's decision [`DECISION-20261029-joseph-oi160-tolerance-run.md`](../../DECISION-20261029-joseph-oi160-tolerance-run.md)
  (#498): *"A new declaration fixes the tolerance from the measured noise floor (≈1e-13) before any data, applied to
  unseen replicas: a few seeds from each of the three July producers. About 12 CPU unfolds, ~0.6 node-h, under the
  standing approval."* His selected option was *"Pre-declared tolerance run (Recommended)"*.
- The director's request of 2026-10-29:
  - a max-relative criterion over the union-nonzero bins, plus an equal zero pattern, with its margin stated both ways;
  - a fresh same-code control;
  - seeds per July producer, none of them seed 1, each producer identified, and no graded file opened before the
    binding except for its sha256;
  - a per-producer reading table that says what a mixed result means.

**After:** the first run, [`../oi160-reproduction-20261029/REPORT.md`](../oi160-reproduction-20261029/REPORT.md) (VOID).
Its K1 measured the noise floor this tolerance is fixed from. Its code, wrapper and controls are reused unchanged.

**Declares:** `tol_compare.py` (the criterion and the tables), `run_array.sh`, `test_tol.py`, `seeds.tsv`,
`stored.sha256` and `code.sha256`, all beside this file, plus the exact commands and the stops.

**MEASURES:** nothing. The tools have run only on synthetic fixtures (9 tests). Only metadata of the graded replicas has
been read: `sacct`, `stat`, and their sha256 (§1).
<!-- absence-ok: a scoping statement about this declaration's own work: nothing it declares has run on real inputs -->

**CANNOT AUTHORIZE:** running it before the binding; any change to `C_stat`, `C_ML` or the trunk, which is Joseph's
separate decision (#498, item 3).

**CITABLE FOR:** the tolerance and its reason, which replicas are graded and how their producers were identified, and
how each result will be read.

**NOT CITABLE FOR:**
- any result;
- seeds not graded here, beyond what their producer's verdict covers;
- `C_ML`;
- whether either contract is correct.

## 0. Summary

- **Five unseen seeds across the three July producers,** each reproduced under both codes and graded against its stored
  file by a max-relative tolerance τ = 1 × 10⁻⁸ plus an identical zero pattern.
- **A fresh same-code control** (seed 1, the corrected code twice) re-measures the floor on the day. The run is VOID if
  that floor exceeds τ / 100.
- **One array of 6 tasks, 12 unfolds,** on shared QOS with 36 CPUs; about 0.45 node-h expected.

## 1. The graded replicas, and how each producer is identified

**Every seed of the 100 top-level replicas has exactly one producer, named from metadata alone.** These reads were
approved by the director on 2026-10-29: `sacct` task rows, `stat` names, sizes and mtimes, and nothing else.

**The rule:**
- a seed belongs to an array task when that task COMPLETED and ended within 5 s of the file's mtime;
- it belongs to the 07-13 interactive packed loop when its `iboot_<s>.log` exists with an mtime within 5 s of the file's.

**The counts:**
- **`55805463`:** 2 seeds, 1 and 2.
- **`55871150`:** 7 seeds, 3–9.
- **The interactive loop:** 91 seeds, 10–100.
- None ambiguous or unnamed.
- **Excluded as raced:** seeds 10 and 11. Array `55871150` also ran them in full (8:31 each), and the loop's write
  landed last.

The logs' contents were **not** read, because each prints its replica's total cross section.

**Graded seeds** (`seeds.tsv`):

| task | seed | producer | file mtime (−0700) | sha256 | identified by |
|---:|---:|---|---|---|---|
| 1 | 2 | `55805463` | 2026-07-11T17:59:40 | `074344ff…` | task `_2` COMPLETED, ended 17:59:40, the file's mtime. `55871150_2` ran 0:16 (skip-if-exists). No log. |
| 2 | 3 | `55871150` | 2026-07-13T16:43:21 | `c8d81b15…` | task `_3` COMPLETED (8:31), ended within 5 s of the mtime. No log. |
| 3 | 6 | `55871150` | 2026-07-13T16:59:32 | `39929393…` | task `_6` COMPLETED (8:29), ended within 5 s of the mtime. No log. |
| 4 | 40 | interactive loop | 2026-07-13T17:32:10 | `0d0143b7…` | `iboot_40.log` mtime within 5 s. `55871150_40` ran 0:12 (skip-if-exists). |
| 5 | 85 | interactive loop | 2026-07-13T16:00:45 | `240bcd50…` | `iboot_85.log` mtime within 5 s. No `55871150` task for id 85. |

- **`55805463` has only one gradable seed.** It made seeds 1 and 2, and seed 1 is excluded (#498, item 1). Its verdict
  therefore rests on one replica.
- **Producer weights in the 100:** `55805463` 2, `55871150` 7, the interactive loop 91.

**Unseen, checked.** No earlier step compared or opened any graded file:
- The only replica ever opened, by this session, the director's checks or the first job, is `res_boot_1.npz`, in both
  sets.
- This session's remote reads loaded `res_boot_1` with numpy and no other replica. This step read the five files'
  sha256 only.
- In the repository at `835112d7e`, `res_boot_{2,3,6,40,85}.npz` appear in three quarantine receipts and in
  `state/s5c/c-boot-tasks.tsv`. Every hit is a file inventory of another namespace: `mii/member_k000000/`, a quarantine
  directory, the k=0 member namespace with its `.done` markers, or the s5c campaign. None compares a top-level replica.
  Search: res_boot_(2|3|6|40|85)\.npz across the tree, excluding MANIFEST.tsv @ 835112d7e

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`;
- `T=$P/oi160-tol-20261029`;
- `D=$T/deploy/<pin8>`, a clean clone of the binding commit;
- `H=$D/docs/orchestration/state/oi160-tolerance-20261029`;
- `PY=env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -B`.

**The first run's directory is kept:** `$P/oi160-repro-20261029` stays until this report merges, and its `out/A1.npz` is
the cross-day reference (§3.1).

### 2.1 Deploy and tests (login node, 0 node-h)

```bash
test -e $T && { echo "STOP: \$T exists"; exit 1; }
mkdir -p $T/logs $T/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $H && sha256sum run_array.sh tol_compare.py test_tol.py seeds.tsv stored.sha256 code.sha256 DECLARATION.md \
    ../oi160-reproduction-20261029/repro_run.py
} > $T/logs/deploy.log 2>&1
cd / && TMPDIR=$T/tmp $PY -m unittest discover -s $H -p test_tol.py > $T/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $T/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $T/logs/deploy.log
```

**It must show:** `$T` absent beforehand; HEAD equal to the pin; 0 porcelain lines before and after; the §7 digests;
`tests rc=0` and "Ran 9 tests … OK". Anything else is a STOP. These tests were run locally in exactly this form, from
`/` with `-I -B`.

### 2.2 The array (submitted once)

```bash
cd $H && sbatch --output=$T/logs/%A_%a.out --error=$T/logs/%A_%a.err --export=NONE,T=$T,D=$D run_array.sh
```

`run_array.sh` carries `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G --time=01:05:00
--array=0-5 --no-requeue --account=m3246`. There is no GPU. It writes only under `$T`, with `TMPDIR` under `$T`.

- **Task 0:** seed 1 under the corrected code, run twice (the fresh floor).
- **Tasks 1–5:** one graded seed each, the corrected code and then the old code.
- **In total:** 12 unfolds.

**Priced from this run's measured walls.** The first run measured, on the same allocation shape: corrected 14:23 and
13:33, old 17:21.
- A task holds two unfolds: about 28–32 min, and at worst 34:42 at the measured per-unfold maximum.
- The per-task limit, 1:05:00, is 1.87 × that worst case. It is also 1.5 × two June-maximum unfolds (21:40 each).
- The six tasks run concurrently.
- **Charge:** about 6 × 0.53 h × 36/256 ≈ **0.45 node-h** expected; at most 6 × 1.08 h × 36/256 ≈ 0.91 node-h if every
  task hits its limit. Both are under the standing approval.

### 2.3 Grading (login node, after every task has ended)

```bash
sacct -j <array id> -n -P --format=JobID,State,Elapsed,ExitCode,AllocTRES%60 > $T/logs/sacct.txt
cd / && $PY $H/tol_compare.py --out-dir $T/out --stored-dir $P/MINERvA-OmniFold/nd-unfolding/boot_nd_5d \
  --seeds $H/seeds.tsv --first-run-a1 $P/oi160-repro-20261029/out/A1.npz --readout $T/out/readout.json \
  > $T/logs/grade.log 2>&1; echo "grade rc=$?" >> $T/logs/grade.log
```

The graded replicas are first opened here, after the binding.

## 3. The criterion, the controls and the readings

### 3.1 Controls (each a STOP, per task)

- **P0, the code:** `code.sha256`, the same four files as the first run. A is `07c18aee`'s `bootstrap_nd.py`
  `da0f7724…`; B is `07c18aee^`'s `57c4f2bb…`; the helpers are unchanged. The wrapper is the first run's
  `repro_run.py`, `649b1291…`.
- **P1, the input:** 1,548,438,020 bytes and mtime epoch 1782610308.
- **P2:** the task's stored replica matches `stored.sha256`. Its seed is not 1.
- **P3:** 36 CPUs of affinity, with `OMP_NUM_THREADS` unset.
- **P4:** nothing is imported from the canonical checkout. The wrapper exits 3 otherwise.
- **Any unfold exiting non-zero** is also a STOP.

### 3.2 The tolerance, fixed from K1 before any graded replica is opened

**Two files agree iff** they have:
- equal `shape` and `seed`;
- the **same zero pattern** in `xsec_flat`;
- **max over the bins nonzero in either of |x − y| / max(|x|, |y|) ≤ τ = 1 × 10⁻⁸.**

**Why τ = 1 × 10⁻⁸.** The first run measured the same-code floor (K1, A1 vs A2): a median of 2.8 × 10⁻¹³ and a
**maximum of 3.0 × 10⁻¹²**. The separation between the two contracts, wherever they were compared, was a median of
**7.4 × 10⁻³**, with zero patterns that differ.
- **Margin above the floor:** τ / 3.0 × 10⁻¹² ≈ **3,300×**. An agreeing reproduction must keep every bin within τ, so
  the criterion uses the floor's maximum, not its median.
- **Margin below the separation:** 7.4 × 10⁻³ / τ ≈ **740,000×**. A different contract misses τ by more than five
  orders of magnitude, and usually also differs in its zero pattern.

**Validity, checked on the day:**
- **V1, the fresh floor.** Task 0's two runs must have the same zero pattern and a max-relative of at most τ / 100 =
  1 × 10⁻¹⁰, which is 33× the first run's floor maximum. Otherwise **every reading is VOID**: the floor has moved too
  close to τ.
- **V2, separation per seed.** The seed's two codes must differ by a max-relative of at least 100 τ = 1 × 10⁻⁶.
  Otherwise that seed is **VOID**: the tolerance cannot tell its codes apart.
- **Descriptive only.** The fresh control is also compared with the first run's `out/A1.npz`. This is a cross-day
  number, and it decides nothing.

### 3.3 The readings, fixed in advance (`tol_compare.py`)

**Per seed:**

| A agrees with stored | B agrees with stored | verdict |
|:-:|:-:|---|
| yes | no | **CORRECTED** |
| no | yes | **OLD** |
| no | no | **NEITHER**: a third producer or environment |
| yes | yes | VOID (the codes do not separate here) |

A seed is also VOID if V1 or V2 fails, or if either reproduction is missing. A missing B output, from the old code's
SKIPPED path, cannot show separation.

**Per producer:**
- if every non-VOID seed has the same verdict, the producer takes that verdict;
- if all its seeds are VOID, it is VOID;
- if its seeds disagree, it is **MIXED**: that producer did not write with one code.

**Overall:**
- VOID if V1 fails or every producer is VOID;
- CORRECTED, OLD or NEITHER if every non-VOID producer reads the same;
- otherwise **MIXED**.

**What a mixed result across producers means.** The 100 replicas behind the trunk's `C_stat` would then rest on more
than one seed contract. The readout reports each producer's verdict beside its weight in the 100 (2 / 7 / 91), because
the interactive loop wrote 91 of them. What that would mean for `C_stat` is Joseph's separate decision. This run reads
only which code wrote which producer's files.

**Expected under each hypothesis:**
- **If the corrected code ran throughout:** CORRECTED for all three producers, with V1 and V2 holding.
- **If the old code ran for some producer:** OLD for that producer, and MIXED overall.
- **If none of the committed code ran:** NEITHER.

## 4. What this run can and cannot show

**Can:** for each graded seed, which committed `bootstrap_nd.py` reproduces its stored replica within τ in today's
environment, and from that a verdict for each producer.

**Cannot:**
- **The seeds not graded.** A producer's verdict covers its other seeds by inference, and `55805463`'s rests on one seed.
- **`C_ML`:** not in scope (#498).
- **That either contract is right.**
- **Any change to `C_stat`, `C_ML` or the trunk.**
- **Seed 1 again:** neither seed 1 nor its three earlier outputs is regraded. Task 0 reuses seed 1 only for the
  same-code floor, A against A, and its comparison with the first run's A1 is descriptive.

## 5. The readout, `oi160-tolerance-readout/1`

`$T/out/readout.json` holds:
- the criterion's constants;
- the fresh floor, and whether it passed V1;
- the cross-day description;
- per seed: its producer, its verdict and reason, the A/stored, B/stored and A/B measures, and the file digests;
- the producer verdicts and the overall outcome;
- `not_citable_for`.

**Committed in the report's PR:** the readout, the provenance files, the reproduced npz files (about 92 kB each), the
logs and `sacct.txt`, under `run/` here. The report restates §4's limits beside the outcome.

## 6. Code and tests

- **`tol_compare.py`:** the criterion (`measure`), the tables (`seed_verdict`, `producer_verdict`), the overall outcome,
  and the pinned-digest refusal.
- **`run_array.sh`:** P0–P3, the per-task unfolds through the first run's `repro_run.py` (P4), and the STOPs.
- **`test_tol.py`, 9 tests, synthetic, both directions.** Run from `/` as `-I -B -m unittest discover -s <dir>
  -p test_tol.py`, as §2.1 runs them:
  - the per-seed CORRECTED, OLD and NEITHER verdicts;
  - one reading across producers;
  - τ from both sides (0.99 τ agrees, 2 τ does not);
  - a differing zero pattern disagrees even within τ;
  - a high fresh floor voids everything (V1);
  - codes that do not separate void a seed (V2);
  - MIXED within a producer;
  - a missing old-code output is not agreement;
  - a stored file that is not the pinned one is refused.

## 7. Pinned bytes

The pinned files are below. `DECLARATION.md`'s own digest is
recorded in `deploy.log` at §2.1.

| file | sha256 |
|---|---|
| `run_array.sh` | `c21d188ec9d6479283fcf73dd8f5eacd0ee0fb0dd9b4664c3a863df12a9388da` |
| `tol_compare.py` | `47ff57c950a7e539c7d580f360f8984ead4d6643645bd85388582bcec329cb3f` |
| `test_tol.py` | `82cbe3a12f7ffbc3d010f79c93149d2f8b39070e0ab4287844f032e6f0177868` |
| `seeds.tsv` | `d20298721bb99d5a319d036a90558c75de7ee691d9aba6987b8f5e32ab3587d5` |
| `stored.sha256` | `9197ee78994455ec5ac960cdc32bb011281159677934935e8ce1f7ecba0afc4b` |
| `code.sha256` | `5da5283b212e94e21ccfaa69f266a34136fc45d6c34eb84a25a1fbfe1cecadc0` |
| `../oi160-reproduction-20261029/repro_run.py` | `649b12916b4fe43df1626f9809d89817ba3e57ee04238be793918eaa968396ae` |

## 8. Storage, cost and stops

- **Storage:** about 1.2 MB under `$T`. No CFS write; nothing in the canonical checkout.
- **Removal:** `$T/deploy` is removed after the report merges. Both `$T` and the first run's directory are removed after
  this report merges, unless the director says otherwise.
- **Cost:** §2.2, about 0.45 node-h, at most 0.91.
- **Stops:** any STOP in §2.1 or §3.1; any task not COMPLETED 0:0; past the limit. A STOP is reported unrepaired, and
  nothing is resubmitted without a new binding.

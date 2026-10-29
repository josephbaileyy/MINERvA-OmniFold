# REPORT — OI-160 tolerance run: all three July producers read CORRECTED (2026-10-29)

**By** the close-items session, for the director, who takes it to Joseph
(`DECISION-20261029-joseph-oi160-tolerance-run.md`, item 3).

**Under:** [`DECLARATION.md`](DECLARATION.md) (sha256 `cb87a939d47c877c…`) and [`BINDING.md`](BINDING.md) (#500),
at the deploy pin `a310bb352ad64aaa3875bdb2f129450fa07594d6`.

**CITABLE FOR:**
- which committed `bootstrap_nd.py` reproduces each of the five graded stored replicas within the declared tolerance,
  today;
- each producer's verdict under the declared table, and the limits stated in §5.

**NOT CITABLE FOR:**
- `C_ML`;
- whether the corrected contract is correct;
- any change to `C_stat`, `C_ML` or the trunk.

This report draws no conclusion about `C_stat`. That is Joseph's separate decision (#498, item 3).

## 1. The outcome, from `run/out/readout.json`

> **`producers`:** `55805463`: `CORRECTED` · `55871150`: `CORRECTED` · `interactive-20260713`: `CORRECTED`
>
> **`overall`:** `CORRECTED`
>
> **`fresh_floor_ok`:** `true`

| seed | producer | verdict | corrected vs stored: max rel, zero pattern | old vs stored: max rel, zero pattern | corrected vs old: max rel |
|---:|---|---|---|---|---:|
| 2 | `55805463` | **CORRECTED** | 2.27e-13, equal | 1.00, **differs** | 1.00 |
| 3 | `55871150` | **CORRECTED** | 4.04e-12, equal | 1.00, **differs** | 1.00 |
| 6 | `55871150` | **CORRECTED** | 6.86e-12, equal | 1.00, **differs** | 1.00 |
| 40 | interactive loop | **CORRECTED** | 1.35e-12, equal | 1.00, **differs** | 1.00 |
| 85 | interactive loop | **CORRECTED** | 1.64e-12, equal | 1.00, **differs** | 1.00 |

- **Criterion:** max-relative over the union-nonzero bins ≤ τ = 1 × 10⁻⁸, plus an identical zero pattern (§3.2). The
  largest corrected-code distance, 6.86 × 10⁻¹², is 1,460× inside τ. The old code misses every seed in both clauses.
- **V1, the fresh floor** (seed 1, the corrected code twice): max-relative 1.43 × 10⁻¹², zero patterns equal; the limit
  is τ / 100 = 1 × 10⁻¹⁰. Passed.
- **V2, separation:** the two codes differ on every seed by a max-relative of 1.00, against a minimum of 100 τ = 10⁻⁶.
  Passed.
- **Descriptive only:** the fresh control against the first run's `A1.npz` (another day, another node) gives a
  max-relative of 2.98 × 10⁻¹², with zero patterns equal.

## 2. The job

- **Array:** `60489457`, tasks 0–5, QOS `shared`, 36 CPUs each, `--no-requeue`, no GPU. Submitted once from `login37` at
  2026-10-29T11:14:03Z.
- **Result:** every task COMPLETED `0:0`, and no task logged a STOP (`run/logs/task*.log`).

| task | role | elapsed | unfolds (A / B) |
|---:|---|---|---|
| 0 | fresh floor, seed 1 | 00:51:52 | 27:29 / 24:16 (A twice) |
| 1 | seed 2 | 00:35:05 | 19:29 / 15:30 |
| 2 | seed 3 | 00:18:54 | 9:32 / 9:16 |
| 3 | seed 6 | 00:53:01 | 28:57 / 23:59 |
| 4 | seed 40 | 00:17:45 | 8:31 / 9:08 |
| 5 | seed 85 | 00:38:17 | 18:00 / 20:10 |

- **Charge:** Σ elapsed 3.582 h × 36/256 = **0.504 node-h**. That compares with 0.45 expected and 0.91 at most; tasks 0
  and 3 ran longer than projected but inside the 1:05:00 limit (`run/logs/sacct.txt`).
- **Deploy** (`run/logs/deploy.log`, `run/logs/deploy-session.txt`, `login37`): `$T` was absent beforehand; HEAD equalled
  the pin; 0 porcelain lines before and after; all eight digests matched; `tests rc=0`, "Ran 9 tests … OK".
- **Controls P0–P3 passed in every task:** the code digests, the input's size and mtime, each task's stored-replica digest,
  and 36 CPUs of affinity with `OMP_NUM_THREADS` unset.
- **Provenance** (`run/out/*.provenance.json`, all twelve): `preimported_under_lib: true`,
  `modules_under_forbidden_root: []`, LightGBM 4.6.0, affinity 36, `OMP_NUM_THREADS` unset, `script_exit: 0`.
- **Grading** ran on `login37` after every task ended (`run/logs/grade.log`, `grade rc=0`). It was the first time any
  graded replica was opened.

## 3. The director's ruling 3: NEITHER

No seed read NEITHER, so the ruling's condition did not arise. Had one done so, it would not have counted as evidence
against either contract, because the interactive loop's thread allocation is not known from metadata.

## 4. The director's ruling 4: coverage and weights

**A producer's verdict covers its ungraded seeds by inference only.** The producers' shares of the 100 top-level replicas,
and how many of each were graded:

| producer | replicas in the 100 | graded |
|---|---:|---|
| `55805463` | 2 | 1 (seed 2) |
| `55871150` | 7 | 2 (seeds 3, 6) |
| the 07-13 interactive loop | 91 | 2 (seeds 40, 85) |

- **`55805463`'s verdict rests on one seed,** because it made only seeds 1 and 2 and seed 1 is not regraded (#498).
- **Seed 1**, from the same producer, was not regraded. It reads only as the earlier VOID run's descriptive pattern.
- **Seeds 10 and 11** had raced producers and were excluded from grading.

## 5. Limits, restated beside the outcome

- **The 95 ungraded seeds** are covered only by inference from their producer's verdict (§4).
- **`C_ML`** (`seedscan_split.py`, its 24 replicas) is untouched and not in scope.
- **A reproduction shows which code ran, not that it was correct.**
- **Nothing here changes `C_stat`, `C_ML` or the trunk.** What this means for the adopted trunk's stat block is Joseph's
  decision.

## 6. Files and storage

**Committed under `run/`:**
- `out/readout.json`;
- the twelve `*.provenance.json` and the twelve reproduced npz files;
- `logs/`: `deploy.log`, `deploy-tests.log`, `task0`–`5.log`, the twelve unfold logs, `grade.log` and `sacct.txt`;
- the deploy, submit and grading session transcripts.

The scheduler's per-task `.out` and `.err` files are all empty (0 bytes) and are not committed. The npz files and
`.log` files match the repository's `*.npz` and `*.log` ignore rules, so they are added with `git add -f`. Each graded
npz file's sha256 equals the digest `readout.json` records for it (ten of ten). The two control files carry no digest;
re-running `tol_compare.measure` on them reproduces both control entries in `readout.json` exactly.

**The first run's files, landing late.** The first run's REPORT (§7) lists `A1.npz`, `A2.npz`, `B1.npz` and six logs as
committed. The same ignore rules kept them out of #496, so until this PR they existed only in `$B` and a local
download. This PR adds them under `../oi160-reproduction-20261029/run/` from that download. The three npz files match the
digests in that run's `readout.json`, and the three transcripts that did land are byte-identical to the download's.

**Storage:** both run directories, this one (`$T = /pscratch/sd/j/josephrb/oi160-tol-20261029`) and the first run's
(`/pscratch/sd/j/josephrb/oi160-repro-20261029`), are kept until this report merges, as the binding requires. They are
removed afterwards only on the director's word. Nothing was written to CFS or to the canonical checkout, and nothing was
resubmitted.

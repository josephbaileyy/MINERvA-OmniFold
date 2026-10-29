# DECLARATION — OI-160: reproduce one bootstrap replica under each seed contract (2026-10-29)

**By** the close-items session, OI-160's owner, for the director to bind.

**Under:**
- Joseph's decision [`DECISION-20261029-joseph-oi160-reproduction-and-q8.md`](../../DECISION-20261029-joseph-oi160-reproduction-and-q8.md)
  (#487), item 1: *"The OI-160 reproduction runs under the standing approval for jobs under 12 h, declared and bound as
  usual."* His selected option was *"Yes, run it (Recommended)"*.
- The director's request of 2026-10-29: one replica, `res_boot_1` with `--seed 1`, under `07c18aee`'s and `07c18aee^`'s
  `bootstrap_nd.py`, each compared with the stored `xsec_flat` in `boot_nd_5d/` and in `boot_nd_5d_prehm_20260711/`.
  CPU only, no GPU, no CFS write, `--no-requeue`, a clean clone at a pin on pscratch, and a time limit priced from a
  measured unfold. The agreement criterion and the expected outcome under each contract are stated before the run.

**After:**
- [`QUESTION-20261028-trunk-stat-ml-replica-provenance.md`](../../QUESTION-20261028-trunk-stat-ml-replica-provenance.md),
  its check 4.
- [`RECORD-20261029-director-oi160-readonly-checks.md`](../../RECORD-20261029-director-oi160-readonly-checks.md), checks 1–3.

**Declares:**
- the two-by-two comparison and its same-code control;
- `repro_run.py`, `repro_compare.py`, `run_job.sh` and `test_repro.py`, all beside this file;
- the exact commands, the controls, the readout and the stops.

**MEASURES:** nothing. The tools have run only on synthetic fixtures (10 tests). The facts in §1 were read read-only
under this item's widened limits.
<!-- absence-ok: a scoping statement about this declaration's own work: nothing it declares has run on real inputs -->

**CANNOT AUTHORIZE:**
- running it, which needs the director's binding first;
- any change to `C_stat`, `C_ML` or the adopted trunk. That is a separate decision (decision item 1).

**CITABLE FOR:** what the run will compute, from which bytes, and how each result will be read.

**NOT CITABLE FOR:** any result; any other replica than seed 1; `C_ML` or `seedscan_split`; whether either contract is
correct.

## 0. Summary

**The question.** The adopted trunk's `C_stat` (`uq_cov_stat_5d.root`, `6580016f…`) was built from the 100
top-level replicas in `boot_nd_5d/`. Did the code that wrote them fix the estimator seed (the corrected contract,
`07c18aee`), or tie it to the bootstrap seed (the old contract, `07c18aee^`)?

**The two codes differ only in `bootstrap_nd.py`.** Both commits' `omnifold_nn_core.py` (`24f87f11…`) and `xsec_nd.py`
(`454001f3…`) are byte-identical, and neither file changed between 2026-06-15 and 2026-07-20. The two
`bootstrap_nd.py` differ in two ways. The old one draws the data and MC Poisson weights from one
`default_rng(seed)` and passes `seed` to the unfold. The corrected one draws them from `default_rng(seed)` and
`default_rng(seed + 10_000_000)`, and passes `--estimator-seed`, default 42. Fed the same seed, the two cannot write
the same file.

**The two-by-two.** A = `07c18aee`'s `bootstrap_nd.py`, B = `07c18aee^`'s. Both run with `--seed 1 --iters 5` on the
one input. A runs twice (A1, A2), B once (B1). Each is compared with S_top = `boot_nd_5d/res_boot_1.npz` and
S_pre = `boot_nd_5d_prehm_20260711/res_boot_1.npz`.

**Criterion:** bitwise equality of `xsec_flat` (§3.2).

## 1. Inputs, measured read-only on `login37`, 2026-10-29

| object | bytes | mtime (−0700) | sha256 | made by |
|---|---:|---|---|---|
| `nd-unfolding/of_inputs_5d.npz` (the input) | 1,548,438,020 | 2026-06-27T18:31:48 | recorded by the job | — |
| S_pre `boot_nd_5d_prehm_20260711/res_boot_1.npz` | 92,173 | 2026-06-27T21:32:24 | `2836ff561db04461…` | array `55151671_1`, `boot5d`, 36 CPUs, `shared_milan`, 21:20:53 + 11:34 |
| S_top `boot_nd_5d/res_boot_1.npz` | 92,051 | 2026-07-11T17:57:21 | `5e1c42d2607171e9…` | array `55805463_1`, `boot5d`, 36 CPUs, `shared_milan`, 17:45:56 → 17:57:21 |

- Both stored files have keys `seed shape total_xsec xsec_flat`, `seed` 1, shape `[14, 16, 7, 7, 6]` and 65,856
  float64 values, all finite. S_top has 10,510 nonzero values and S_pre 10,527.
- They differ: a median relative difference of 0.74% over the bins nonzero in either, and a maximum of 1.0, where a
  bin is zero in one of them. Total cross sections are 3.069177e-38 (S_top) and 3.069068e-38 (S_pre).
- The input predates both. The producers are identified from `sacct`, by task, at the files' exact mtimes. Array
  `55799900` (07-11 11:20) failed in 8 s, so it did not make S_top.
- **Environment now:** `$HOME/.conda/envs/root_6_28`, LightGBM 4.6.0, numpy 1.26.4.
  - The committed `sbatch_bootstrap_5d.sh` sources `setup_salloc_env.sh`, which activates that prefix. That script's
    conda base changed on 2026-07-02, between the two runs.
  - **The launcher that ran is not the committed one.** It took 36 CPUs, where the committed script says
    `--cpus-per-task=16`. So "both runs used this environment" is an inference.
  - The June and July LightGBM versions are not recorded. That is why K2 exists (§3.2).

**Why the two stored files differ at all.** Same input, same seed and same allocation shape. If the code and the
environment had been the same on 06-27 and 07-11, the old contract would have written the June file again in July.
So between those dates either the code changed (Reading 2, or a third code) or the environment did. The run is built
to tell these apart (§3.3).

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`;
- `B=$P/oi160-repro-20261029`;
- `D=$B/deploy/<pin8>`, a clean clone of the binding commit;
- `H=$D/docs/orchestration/state/oi160-reproduction-20261029`;
- `PY=env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node, 0 node-h)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $H && sha256sum run_job.sh repro_run.py repro_compare.py test_repro.py code.sha256 stored.sha256 DECLARATION.md
} > $B/logs/deploy.log 2>&1
cd / && TMPDIR=$B/tmp $PY -m unittest discover -s $H -p test_repro.py > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:** HEAD equal to the pin; 0 porcelain lines before and after; the §7 digests; and `tests rc=0` with
"Ran 10 tests … OK". Anything else is a STOP.

### 2.2 The job (one CPU job, after §2.1)

```bash
cd $H && sbatch --output=$B/logs/%j.out --error=$B/logs/%j.err --export=NONE,B=$B,D=$D run_job.sh
```

`run_job.sh` carries `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G --time=01:30:00
--no-requeue --account=m3246`. No GPU. It writes only under `$B`; `TMPDIR` is `$B/tmp`. It reads the input and the two
stored replicas from the canonical checkout read-only, and touches nothing else there.

**The time limit, priced from a measured unfold.** The June array `55151671` ran this tool on this input, with the
same allocation shape, in 100 tasks: median 10:49, maximum 21:40. Three unfolds run in sequence, so the projection is
32 min at the median and 65 min at the maximum. The limit, 1:30:00, is 1.38 × the maximum. The cost is at most 36 of
a Milan node's 256 hardware threads for 1.5 h, about 0.21 node-h, well inside the standing approval for jobs under 12 h.

**Exit codes:** 0 when the readout is written; 1 on any STOP (§3.1).

## 3. Controls, the criterion, and the readings

### 3.1 Controls, before any unfold (each a STOP: exit 1)

- **P0, the code.** The four files extracted from the clone's git objects match `code.sha256`:
  - A's `bootstrap_nd.py` `da0f7724…`;
  - B's `bootstrap_nd.py` `57c4f2bb…`, byte-identical to `c70397e04` (2026-06-04), the version that wrote S_pre;
  - `omnifold_nn_core.py` `24f87f11…`;
  - `xsec_nd.py` `454001f3…`.
- **P1, the input.** `of_inputs_5d.npz` has 1,548,438,020 bytes and mtime epoch 1782610308 (2026-06-27T18:31:48−0700).
  Its sha256 is recorded.
- **P2, the stored files.** They match `stored.sha256`.
- **P3, the allocation.** `OMP_NUM_THREADS` is unset and the CPU affinity is 36, as for both stored runs: LightGBM
  takes its thread count from the OpenMP default.
- **P4, imports** (per unfold, `repro_run.py`). Both versions put the canonical cluster checkout at `sys.path[0]`
  (OI-136). The wrapper imports `omnifold_nn_core` and `xsec_nd` from the extracted `lib/` first, runs the script
  unchanged, and exits 3 if any loaded module's file is under the canonical checkout. Exit 3 is a STOP.

### 3.2 The agreement criterion: exact equality

Two files **agree** iff their `xsec_flat` are bitwise identical as float64, and their `shape` and `seed` are equal.

**No tolerance.** The two contracts' known separation is a median of 0.74% per bin (§1). A tolerance would have to sit
somewhere between environment noise, which is unmeasured, and that separation, and choosing it would be choosing the
answer. Bit equality needs no threshold. A deterministic unfold, given the same code, input bytes, seeds and thread
count, writes the same bits. A bitwise match of 65,856 doubles cannot arise by chance.
<!-- absence-ok: a statement about this method's design: the environment-noise scale is what K1 and K2 measure, so no tolerance is chosen in advance -->

**The precondition, bit-reproducibility, is tested, not assumed:**
- **K1, the same-code control:** A1 = A2. Is today's unfold deterministic?
- **K2, the positive control:** B1 = S_pre. B is the code that wrote S_pre in June, on the same input, seed and
  allocation shape. Does today's environment reproduce a replica whose producer is known?

Distances (number of differing bins, max absolute, median and max relative) are reported for every pair, as
description only.

### 3.3 The readings, fixed before the run (`repro_compare.read`)

| A1 = S_top | B1 = S_top | K1 | K2 | outcome | reading |
|:-:|:-:|:-:|:-:|---|---|
| yes | no | any | any | **R2** | The corrected code wrote S_top. A bitwise match decides it on its own. |
| no | yes | any | any | **R1** | The old code wrote S_top. |
| yes | yes | — | — | VOID | The two codes wrote the same file. Not expected (§0). |
| no | no | no | — | VOID | The unfold is not deterministic today, so no "no" can be read. |
| no | no | yes | yes | **THIRD** | Today reproduces June, but neither committed code reproduces S_top: a third producer, or a July-only environment. |
| no | no | yes | no | **INCONCLUSIVE** | Today reproduces neither stored file (environment drift). |

**Expected under each contract:**
- **If the corrected code wrote S_top (Reading 2):** R2. K2 also holds if today's environment matches June's, and may
  fail if the 07-02 base change altered LightGBM. Either way, A1 = S_top.
- **If the old code wrote S_top (Reading 1):** the environment must then have changed between 06-27 and 07-11 (§1), so
  B1 = S_top if today matches July. That is R1, with K2 failing.
- **If neither did:** THIRD or INCONCLUSIVE. The next step would be a separate declaration, for example a scan of LightGBM
  versions. This run makes none.

## 4. What this two-by-two can and cannot show

**Can:** which committed `bootstrap_nd.py`, with the unchanged `omnifold_nn_core.py` and `xsec_nd.py`, reproduces each
stored seed-1 replica bit for bit in today's environment. It can also show whether today's environment reproduces a
replica whose producer is known (K2).

**Cannot:**
- **The other 99 replicas.** They had more than one producer. `res_boot_1` came from array `55805463` (07-11). Others
  came from the 07-13 interactive packed loop, whose `iboot_*.log` files sit beside them (for example `iboot_11.log`,
  07-13 18:01), and from array `55871150`, according to the July log. So a result for seed 1 says nothing certain about
  a replica written by another producer.
- **`C_ML`.** The 24 split replicas came from `seedscan_split.py` and a different array. This run does not touch them.
- **That the code is right.** A reproduction shows which code ran, not that it was correct.
- **That `C_stat` is right or wrong.** Any change to `C_stat`, `C_ML` or the trunk is Joseph's separate decision.
- **Anything with no bitwise match.** THIRD and INCONCLUSIVE leave the question open. The distances describe them and
  decide nothing.

## 5. The readout, `oi160-repro-readout/1`

`$B/out/readout.json` holds:
- the five file digests;
- `K1_A1_equals_A2`, `K2_B1_equals_S_pre`, `A1_equals_S_top`, `B1_equals_S_top` and `A1_equals_S_pre`;
- `outcome` and `reading`;
- `describe` (distances per pair);
- `not_citable_for`.

Each unfold also leaves `out/<label>.provenance.json`: the module files, LightGBM, numpy and Python versions, the
affinity, `OMP_NUM_THREADS`, and the script's exit. **Committed in the report's PR:** the readout, the three
provenance files, `A1.npz`, `A2.npz` and `B1.npz` (about 92 kB each), and the logs, under `run/` here. The report goes
to Joseph through the director (decision item 1). **Beside the outcome, the report restates §4's
limits:** seed 1 speaks only for its own producer, among the 99 others' several, and `C_ML` is untouched.

## 6. Code and tests

- **`repro_run.py`:** the import-isolating wrapper (P4).
- **`repro_compare.py`:** the criterion (`same`), the description, and the reading table (`read`).
- **`run_job.sh`:** P0–P3, the three unfolds and the comparison.
- **`test_repro.py`, 10 tests, synthetic.**
  - **How they are run.** §2.1 uses `$PY -m unittest discover -s $H -p test_repro.py` from `/`. Under `-I`, Python
    3.11+ does not put the current directory on `sys.path`, so `-m unittest test_repro` cannot import the module (the
    director's review of `88b2f9f8` measured that failure). `discover -s` adds the start directory itself.
  - Measured locally with Python 3.12.2 and `-I -B`: the old command gives `ModuleNotFoundError … Ran 1 test, FAILED`;
    the new one gives `Ran 10 tests … OK`. The first runs behind this declaration used `python3 -m unittest test_repro`
    from `$H`, without `-I`, which is why they passed.
  - **What they cover:**
    - the wrapper uses `lib/` and not a decoy `omnifold_nn_core` under the canonical root;
    - a module present only under the canonical root is refused with exit 3;
    - each outcome (R2, R1, THIRD, INCONCLUSIVE, VOID) is reached from the matching inputs;
    - one ulp of difference is a difference;
    - a missing B output matches nothing;
    - a stored file that is not the pinned one is refused.

## 7. Pinned bytes

| file | sha256 |
|---|---|
| `run_job.sh` | `46d0afacd50fb5e417238c5a9e3a2b49355f54af82aa0913d77c3a2f46eb2df4` |
| `repro_run.py` | `649b12916b4fe43df1626f9809d89817ba3e57ee04238be793918eaa968396ae` |
| `repro_compare.py` | `456d6bced4135ae8f40e7ee175a27555d7dc733ead6210ac2017226ba261c32d` |
| `test_repro.py` | `30589eec55c233bb8c18710b4804b3078f84cda532087768af0739eee4de9c96` |
| `code.sha256` | `5da5283b212e94e21ccfaa69f266a34136fc45d6c34eb84a25a1fbfe1cecadc0` |
| `stored.sha256` | `8e3cf24852d883eb41ac2b8e7c99878929d5e66802db6b71cbe255d3badb397f` |

`DECLARATION.md`'s own digest is recorded in `deploy.log` at §2.1.

## 8. Storage, cost and stops

- **Storage:** about 300 kB under `$B` on pscratch. No CFS write; nothing written in the canonical checkout. After the
  report, `$B/deploy` is removed. `$B/out` and `$B/logs` are committed, and `$B` is then removed.
- **Cost:** one job, at most about 0.21 node-h, under the standing approval.
- **Stops:** any STOP in §2.1 or §3.1; any exit other than 0; past the time limit. Nothing is resubmitted without a new
  binding.

## 9. For the director

- **QOS.** Your request said "regular QOS". This declares `shared`, with 36 CPUs on Milan, because that is the
  allocation both stored replicas were made with (§1). `regular` gives a whole node, so LightGBM's default thread count
  would be 256 and bit-reproduction would fail for a reason unrelated to the question. If you need `regular`, the job
  would have to pin 36 threads by hand, which neither stored run did, and K2 would test that as well.
- **No same-code control is skipped.** K1 tests the unfold's determinism today, and K2 tests the environment against a
  known producer.
- **Not changed:** any receipt, covariance, product or published value; the canonical checkout.
- **The director's review of `88b2f9f8` (2026-10-29):** `shared` with 36 CPUs, exact equality with K1 and K2, the §3.3
  table and §4's limits are accepted. The one blocker, §2.1's test command under `-I`, is fixed above (§6).

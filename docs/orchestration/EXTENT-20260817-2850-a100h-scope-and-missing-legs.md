# EXTENT of the `28.50 A100-h` figure — measured, and it omits the LARGER half

**Lane B, 2026-08-17. Read-only: `sacct` and code reads only. Nothing submitted, cancelled or requeued.**
Measured against `91fc4e9`. `docs/analysis-note/` untouched. No ROOT read or written. No covariance rebuilt.
Every job id, task count and elapsed below comes from `sacct` run in this turn (BEN-027), windowed by name;
the raw pulls are in the job tmp dir and the commands are quoted in §6.

---

## THE ONE NUMBER, WITH ITS SCOPE IN THE SAME SENTENCE

> **One additional estimator seed across all four blocks of the candidate costs `28.64` A100-hours
> PLUS `55.34` CPU task-hours (`2,764.7` CPU-core-hours) — and the `28.50 A100-h` figure is the
> `C_syst` path's 175 GPU unfolds only, which is `99.5 %` of the GPU bill and `0 %` of the CPU bill,
> the CPU bill being the larger half.**

The figure's extent gap is **not** a rounding term on the GPU side. It is **an entire second unit**, which a
GPU-denominated grant does not reach — and the single largest leg in it (`2,759.1` CPU-core-hours, the
160-throw `uthrow` production) is also **the one leg that cannot be re-seeded at all** without the code
change, so funding does not move it.

**A one-seed increment is not an `M(ii)` measurement.** At the predeclared `n >= 6` the same accounting gives
**`171.85` A100-hours plus `332.0` CPU task-hours**, of which `170.98` A100-h (`99.4 %` of GPU) is the
`C_syst` path alone. §5 derives both.

---

## 1. What `28.50` covers, re-derived this turn

`sacct -j 55892341,55892343,55891346,55891028,55912230,55919500 -X` — all `COMPLETED`, single node,
`gres/gpu:a100=1` per task:

| job | leg | tasks | elapsed/task | A100-h | in `28.50`? |
|---|---|---|---|---|---|
| `55892343` | `sweep5dBKGrun` — the 169 vertical universes | 169 | 8.1–9.9 min | **23.840** | YES |
| `55891346` | `det5dBKG` — the lateral arm | 5 | 41.6–45.6 min | **3.626** | YES |
| `55912230` | `fin5dBKG` — finalize | 1 | 61.8 min | **1.030** | YES |
| `55892341` | `sweep5dBKGdump` — bank prep | 16 | 33.6–37.2 min | 9.564 | no — reusable, §3 |
| `55891028` | `chkbkgbr` — branch check | 1 | 1.3 min | 0.021 | no |

**`23.840 + 3.626 + 1.030 = 28.496`** → the `28.50`. Full production over all five ids `= 38.081` A100-h.
Both figures reproduce the addendum to `COST-20260817-mii-seed-scan-derivation.md` digit for digit, from a
`sacct` call issued in this turn rather than from that document.

**So `28.50` is scoped to `combined_source` + finalize.** The candidate has **two** upstreams, named in its
own stamps (`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json`, both arms):

    combined_source = uq_universe_5d_covariance_combined_bkgaware.root     <- covered by 28.50
    uthrow_source   = unified_throw_cov_5d_fluxfix_20260806_full160.root   <- NOT covered at all

## 2. ⚠ THE OMITTED LEG IS THE LARGEST, AND IT IS CPU — MY EARLIER "CORRECTION" WAS ITSELF WRONG

`uthrow_source`'s production, found by scanning the window for `uthrow*` **by name** and reading the
launcher that carries those names (`sbatch_uthrow_run_5d_fast.sh`, the only file matching either):

| job | leg | tasks | elapsed/task | task-h | CPU-core-h | A100-h |
|---|---|---|---|---|---|---|
| `55821660` | `uthrow5d_runF` idx 0–29 (contiguous) | 30 | 32.2–69.3 min | 21.379 | 1068.9 | **0** |
| `56427580` | `uthrow5d_runF` idx 30–39 (contiguous) | 10 | 45.7–85.8 min | 11.782 | 589.1 | **0** |
| `55821661` | `uthrow5d_blkF` idx 0–30 (contiguous) | 31 | 15.7–77.1 min | 22.021 | 1101.1 | **0** |
| | **total** | **71** | | **55.182** | **2759.1** | **0** |

`--constraint=cpu`, `NCPUS=50` measured on every task, partition `shared_milan_ss11` on all 71.
`55821660`+`56427580` = **40 throw tasks**, and the launcher runs `--throws 4` each → **160 throws**, which
is the `upstream_n_throws=160` the candidate stamps. The `20260806` in the product name is
`56427580`'s top-up window (`2026-08-06T15:45:46 → 17:11:33`), not a full re-production.

**CORRECTION, against me.** `COST-20260817-mii-seed-scan-derivation.md` §1 withdrew my claim *"it is CPU,
not GPU"* and asserted *"every actual bkgaware production job ran on GPU,"* citing `55885596`/`55885597`.
**Those are the two jobs my own §2 established were the ABANDONED throw-combine path** — 12 `COMPLETED`
tasks each plus 2 `CANCELLED`. **The surviving `uthrow_source` ran on CPU**, exactly as the tracked launcher
says. So I withdrew a correct claim on the strength of a path nobody took, and the unit objection I gave up
**partially stands**: the `C_syst` path is GPU, the `uthrow` path is CPU.

**The generalisable error is the inverse of the one it replaced.** The first was *reading a tracked launcher
as a description of what ran.* The fix — *"`sacct` is what happened"* — was then applied to **the wrong
jobs**: I searched `sacct` for the operation's name and took the first jobs that matched, without checking
that they produced **the artifact the candidate cites**. `sacct` answers *what ran*; it does not answer
*what the product came from*. **Only the product's own `uthrow_source`/`combined_source` stamps answer
that**, and they were in a receipt I had already read. Filed `BEN-245`.

## 3. Are the stat and ML legs seed-dependent, and is the seed a knob or a production parameter?

**Both are seed-dependent. Both ALREADY have the two-role separation the `C_syst` path lacks.** The
`--estimator-seed` flag exists in both modules, defaults to `42`, and **no 5D launcher has ever set it** —
verified over every launcher that invokes either module:

    sbatch_bootstrap_5d.sh          --seed ${SLURM_ARRAY_TASK_ID}      (no --estimator-seed)
    sbatch_bootstrap_5d_gpu.sh      --seed ${SLURM_ARRAY_TASK_ID}      (no --estimator-seed)
    sbatch_boot5d_gpu_interactive.sh --seed ${s}                       (no --estimator-seed)
    boot5d_packed_loop.sh           --seed ${s}                        (no --estimator-seed)
    sbatch_seedscan_split_5d.sh     --split-seed ${SLURM_ARRAY_TASK_ID} (no --estimator-seed)

**stat (`boot5d`, `C_stat`, 100 replicas) — `bootstrap_nd.py`.** Two flags and a router:

    :17  --seed              (required)   the DRAW: data Poisson + MC Poisson
    :19  --estimator-seed    default 42   "fixed estimator seed; bootstrap seed varies only event weights"
    :21  --fixed-data-seed   default None  pins the draw and routes --seed to the ESTIMATOR
    :28  _data_base = a.fixed_data_seed if a.fixed_data_seed is not None else a.seed
    :29  _est_seed  = a.seed             if a.fixed_data_seed is not None else a.estimator_seed
    :37  omnifold_loop(..., seed=_est_seed)

As invoked in production, **`--seed` is a PRODUCTION parameter** — the replica index `1..100`, which selects
the draw — and **the estimator seed is `42`, fixed, and not exposed at launcher level.** `--fixed-data-seed`
swaps the roles, which is precisely run condition (b) (*"varies only the estimator seed with the draw held
fixed"*). **No code change is needed on this leg.**

**ML (`ssplit5d`, `C_ML`, 24 splits) — `seedscan_split.py`.**

    :34  --split-seed        (required)   the train/test split
    :36  --estimator-seed    default 42   "fixed estimator seed; split-seed varies only the training split"
    :54  omnifold_loop(..., seed=args.estimator_seed, train_frac=..., split_seed=args.split_seed)

**`--split-seed` is a PRODUCTION parameter and is not a nuisance seed at all — it IS the `C_ML` ensemble
axis**; the 24 splits *are* the band. The estimator knob is `--estimator-seed`, fixed at `42`, never set.
**No code change is needed on this leg either.**

**And that module's docstring records a prior on `M(ii)`'s own answer** (`:5-7`), which is worth surfacing
because it is a stated design premise rather than a measurement:

> *"LightGBM at the production settings is **nearly deterministic in the estimator seed alone**, so the
> genuine ML/optimization variance is exposed by re-fitting each OmniFold classifier on a random
> `train_frac` subset."*

That is the reason `C_ML` exists in split form at all. It is **unverified** — no committed artifact measures
it on this footing — and it predicts a small `M(ii)`. It should not be quoted as a result, and it should not
be allowed to substitute for one.

**Reusability across seeds, checked rather than assumed:** the `dump` leg (`9.564` A100-h) is reusable —
`sweep_bank_5d.py`'s `do_dump` (`:56`) never imports or calls `omnifold_loop`; only `do_run` does, at
`:208`/`:252`. So it is excluded from every re-seed figure here.

## 4. ⚠ SO THE SCOPE OF THE CODE CHANGE SHRINKS — three of five legs need nothing

Corrected seed map, every cell `file:line` at `91fc4e9`:

| leg | block | estimator seed | set where | re-seedable **today**? |
|---|---|---|---|---|
| vertical sweep, 169 universes | `C_syst` (dominant) | **42** | `sweep_bank_5d.py:252`, **hardcoded, no CLI flag** (`grep add_argument.*seed` → nothing) | **NO — needs the change** |
| lateral, 5 tasks (`det5dBKG`) | `C_syst` | **42** | `sbatch_unfold_5d_detector_bkgaware_gpu.sh:37,51` `--seed 42` | **YES** — `--seed` is estimator-only (`unfold_nd_omnifold_unbinned.py:930-931,956-959` → `random_state`); the draw is a separate `--bootstrap-seed` (`:904-905`) |
| 160 throws + block units | `uthrow` | **1000** | `sbatch_uthrow_run_5d_fast.sh:21` `--seed 1000`; parser at `unified_throw_cov.py:525` | **NO — needs the change**; one `--seed` drives the estimator (`:244,:281,:297,:314`) *and* the throw realization (`:223 default_rng(args.seed + gj)`) |
| 100 bootstrap replicas | `C_stat` | **42** | `bootstrap_nd.py:19` default, never overridden | **YES** — `--fixed-data-seed` |
| 24 train/test splits | `C_ML` | **42** | `seedscan_split.py:36` default, never overridden | **YES** — `--estimator-seed` |

**Four of the five legs run at estimator seed `42`. The outlier is the `uthrow` leg at `1000`.** That is a
sharper statement than *"the composite mixes two seeds"* and it amends `VL141`, which named only the sweep
on the `42` side; stat and ML belong there too.

**A second correction against me:** `COST-20260817`'s addendum says *"a `C_syst` built at estimator seed 42
with **throw/stat/ML** blocks built at seed 1000."* Measured, **stat and ML are at `42`, not `1000`** — only
throw/CV is `1000`. `VL141`'s row text is correct as written (*"throw/CV legs: 1000"*); the error is in that
addendum and in commit `382cd8e`'s body. Amended in the ledger in this commit.

**Consequence for the specification I handed back.** It was scoped to two modules and that still holds —
`sweep_bank_5d.py` and `unified_throw_cov.py` — but I implied breadth that is not there. **Three of the five
legs already have the separation, and `bootstrap_nd.py:21-29` is a WORKING REFERENCE IMPLEMENTATION of the
exact `--fixed-data-seed` routing the specification proposes for `unified_throw_cov.py`**, in the same repo,
already exercised in production (`sbatch_ai1_estimator_scan.sh:23-24`). The change is smaller and
better-precedented than my last message implied. **Still not written — specified-not-written stands until
Joseph rules.**

## 5. Cost per seed-dependent leg, from measured `sacct` elapsed

**The `M(ii)` instrument for the stat leg is already written and has already run.**
`sbatch_ai1_estimator_scan.sh:23-24` is `bootstrap_nd.py --npz of_inputs_5d.npz --seed ${TASK}
--fixed-data-seed 0 --iters 5` — fixed draw, varying estimator seed, i.e. exactly run condition (b):

    55919500_1  ai1est5d  COMPLETED  00:08:44  1x a100, 32 cpu, shared_gpu_ss11  start 2026-07-14T16:55:38
    55919500_2  ai1est5d  COMPLETED  00:08:46  1x a100, 32 cpu, shared_gpu_ss11  start 2026-07-14T18:18:43
    55919500_3, _4, _[5-12%4]        CANCELLED by 112498 at 2026-07-14T19:20:00
    55916613_[3-12%1]                CANCELLED by 112498 at 2026-07-14T16:34:07

**`0.2917` A100-h / 2 seeds = `0.1458` A100-h per estimator seed.** `n=2`, and I am quoting the per-seed
figure rather than a scaled total wherever a total is not needed. The array delivered 2 of 12; the 12-seed
`\gbdtAiEstTrace` result came from the packed `ai1_packed_loop.sh` run inside an interactive `salloc`, which
is **not separately attributable in `sacct`** — `FOOTING-20260817-gbdtaiesttrace-12-seeds.md:66-69` costs it
independently at `~1 GPU-node-hour` from `CONC=6`, 2 waves. **My `1.750` A100-h for 12 seeds (`= 12 x
0.1458`) and that `~1 GPU-node-hour` are in different units** — a Perlmutter GPU node is 4 A100s, so mine is
`0.44` node-h against their `~1`. **They do not agree, and the FOOTING figure is the more conservative**;
I have not tried to reconcile them and the discrepancy is the packing, not the arithmetic.

**Full 100-replica stat bank, for reference — this is NOT the `M(ii)` cost:**

    55151671  boot5d  array 1-100, 100/100 COMPLETED contiguous  8.5-21.7 min/task
              36 cpu, 0 gpu, shared_milan_ss11   2026-06-27T21:20:53 -> 2026-06-29T05:22:40
              19.092 task-h = 687.32 CPU-core-h
    55805463  boot5d  2 tasks (top-up)  0.336 task-h
    55871708  (the launcher asks --cpus-per-task=16; sacct measured NCPUS=36. Launcher is intent.)

**⚠ The GPU hedge is a wrong-extent trap and I nearly quoted it.** `boot5dG 55871150` shows 54 `COMPLETED`
tasks and `1.434` A100-h, which reads like *"the stat leg on GPU."* Measured, **45 of the 54 ran `<= 30 s`**
— the resume guard skipping an already-complete bank — and **only 9 did real work**, at 505–519 s
(`_3`.._11`). Per-replica GPU cost from those 9 is 8.4–8.7 min, so 100 replicas on GPU would be `~14.2`
A100-h; **that is a scaling from `n=9` of the same operation on different hardware, and it is labelled as a
scaling, not a measurement.** The complete, un-extrapolated stat-bank measurement is the CPU one.

**ML leg — no estimator-only scan has ever run, and the absence is established by a covering search:**
`git ls-files | grep seedscan_split` → for 5D only `sbatch_seedscan_split_5d.sh`, CPU, **no GPU variant
exists** (4D and FPS have `_corrected_gpu` siblings; 5D does not); no launcher passes `--estimator-seed`;
and over `2026-03-01 → 2026-08-17` **every one of the 48 `COMPLETED` `ssplit5d` tasks is
`shared_milan_ss11` with `gres/gpu` absent.** Windows before 2026-06-01 return **zero** `boot5d`/`ssplit`
rows at all, so the window covers the whole history rather than merely containing the answer.

    55849763  ssplit5d  24/24 COMPLETED contiguous  7.9-11.3 min  36 cpu, 0 gpu
              2026-07-13T03:15:51 -> 09:32:00   3.719 task-h = 133.87 CPU-core-h
              -> 0.1550 task-h = 5.58 CPU-core-h per member
    55151672  ssplit5d  24/24 COMPLETED contiguous  8.1-17.8 min  4.450 task-h = 160.20 CPU-core-h
              -> 0.1854 task-h per member    (quoted so the two passes can disagree; they differ by 20%)

I use the **later, post-fix** pass (`55849763`) for the forward figure and record the earlier one beside it.

### The accounting

**One additional estimator seed, per block** — and note the two sides are different shapes, which is the
thing most likely to be misread: for `C_syst` and `uthrow` one seed means **a whole alternative covariance
matrix** (175 and 71 unfolds); for `C_stat` and `C_ML` one seed means **one alternative point estimate**
(1 unfold), because those legs have the fixed-draw design.

| block | what one seed costs | tasks | A100-h | CPU task-h | CPU-core-h |
|---|---|---|---|---|---|
| `C_syst` (sweep + lateral + finalize) | full alternative matrix | 175 | **28.496** | 0 | 0 |
| `uthrow` (throws + blocks) | full alternative matrix | 71 | 0 | **55.182** | **2759.1** |
| `C_stat` | one fixed-draw member | 1 | **0.1458** | — | — |
| `C_ML` | one fixed-draw member | 1 | 0 | **0.1550** | **5.58** |
| **total** | | **248** | **28.642** | **55.337** | **2764.7** |

**`28.50` is `28.496 / 28.642 = 99.49 %` of the GPU column and `0 %` of the CPU column.**

**At the predeclared `n >= 6`** — the number `M(ii)` actually needs, since a one-seed increment yields no
spread:

| block | n | A100-h | CPU task-h |
|---|---|---|---|
| `C_syst` | 6 | `6 x 28.496 = ` **170.976** | 0 |
| `uthrow` | 6 | 0 | `6 x 55.182 = ` **331.092** |
| `C_stat` | 6 | `6 x 0.1458 = ` **0.875** | — |
| `C_ML` | 6 | 0 | `6 x 0.1550 = ` **0.930** |
| **total** | | **171.85** | **332.02** |

**`171.85` A100-h is `7.2x` the mediator's `24` A100-h grant and `6.0x` the `28.50` already queued for
Joseph. `332.02` CPU task-hours (`16,584` CPU-core-hours at 50 cores/task) is denominated in the unit the
grant does not mention at all.** Node-equivalents, stating the conversion so it can be disputed: at 128
cores per Milan node that CPU column is `~129.6` CPU node-hours, and at 4 A100 per GPU node the GPU column
is `~43.0` GPU node-hours. **The two are not fungible and I am not summing them.**

## 6. Commands, so every number above can be re-derived

    ssh saul.nersc.gov 'for w in "2026-06-01 2026-06-21" "2026-06-21 2026-07-11" \
        "2026-07-11 2026-07-31" "2026-07-31 2026-08-17"; do set -- $w; \
        sacct -u josephrb -S $1 -E $2 -X \
          -o JobID,JobName%20,State,Elapsed,NCPUS,Partition,AllocTRES%70,Submit,Start,End -P; done'
    # covering check for earlier runs (returns 0 rows for boot5d|ssplit):
    #   windows 2026-03-01..2026-06-01 in 20-day steps, same filter
    ssh saul.nersc.gov 'sacct -j 55892341,55892343,55891346,55891028,55912230,55919500 -X \
        -o JobID,JobName%16,State,Elapsed,NCPUS,AllocTRES%55 -P'

`sacct` rejects a range wider than ~50 days (*"Too wide of a date range in query"*), which is why every pull
above is windowed; a single wide call **fails loudly** rather than truncating, so the windowing is for
liveness, not for completeness.

## 7. What goes to Joseph

1. **The `28.50` figure is right about what it measures and wrong as a total** — it is `99.5 %` of the GPU
   bill and `0 %` of a CPU bill that is the larger half. **Do not authorize it as "the re-seed cost."**
2. **The decision is not a cost decision.** Two of the four blocks cannot be re-seeded at any price today
   (`sweep_bank_5d.py:252` hardcoded; `unified_throw_cov.py`'s dual-role `--seed`), and those two are
   `99.5 %` of GPU and `99.7 %` of CPU. Funding does not move them.
3. **The change is smaller and better-precedented than I said** — three of five legs already have the
   separation, and `bootstrap_nd.py:21-29` is a working in-repo implementation of the exact pattern.
4. **A cheap partial measurement exists that needs no code change and no ruling:** the `C_stat` and `C_ML`
   estimator axes at `n=12` cost **`1.75` A100-h + `1.86` CPU task-hours** together — inside any grant. It
   would not answer `M(ii)` for the dominant blocks, and **must not be reported as if it did**; it would
   test the `seedscan_split.py:5-7` near-determinism premise, which is currently asserted and unmeasured.

**Nothing run. `OI-130`'s preservation condition binds whatever any eventual run produces.**
**The two-module seed separation is NOT implemented.**

# EXTENT of the `28.50 A100-h` figure — measured, and it omits the LARGER half

**Lane B, 2026-08-17. Read-only: `sacct` and code reads only. Nothing submitted, cancelled or requeued.**
Measured against `91fc4e9`. `docs/analysis-note/` untouched. No ROOT read or written. No covariance rebuilt.
Every job id, task count and elapsed below comes from `sacct` run in this turn (BEN-027), windowed by name;
the raw pulls are in the job tmp dir and the commands are quoted in §6.

---

> ## ⚠ CORRIGENDUM 2026-08-17, and it corrects THIS DOCUMENT's own headline
>
> **`28.50` was understated by `+37.1 %`. The lateral leg is `19` universes, not `5`, and I costed a
> truncated attempt.** Raised by the mediator, verified independently here from `sacct` in the same turn.
> **The re-seed figure is `39.078` A100-h, and every number in this document that contains `28.496` is
> superseded by the arithmetic in §0 below.** The corrected headline:
>
> > **One additional estimator seed across all four blocks of the candidate costs `39.22` A100-hours
> > PLUS `55.34` CPU task-hours (`2,764.7` CPU-core-hours) — and the `28.50 A100-h` figure is the
> > `C_syst` path's GPU unfolds only, undercounted, which corrected is `99.6 %` of the GPU bill and
> > `0 %` of the CPU bill, the CPU bill being the larger half.**
>
> **The two conclusions this document draws do not move**, and that is stated so the corrigendum is not
> mistaken for a retraction: the figure is still ~all of the GPU bill and none of the CPU bill, and the
> decision is still not a cost decision. What moves is the number itself — from `63 %` over the `24`
> A100-h grant by one route to `63 %` over it by another, since `28.50/24 = 1.19` was wrong and
> `39.078/24 = 1.63` is right.

## THE ONE NUMBER, WITH ITS SCOPE IN THE SAME SENTENCE — **SUPERSEDED, see the corrigendum above and §0**

> ~~**One additional estimator seed across all four blocks of the candidate costs `28.64` A100-hours
> PLUS `55.34` CPU task-hours (`2,764.7` CPU-core-hours) — and the `28.50 A100-h` figure is the
> `C_syst` path's 175 GPU unfolds only, which is `99.5 %` of the GPU bill and `0 %` of the CPU bill,
> the CPU bill being the larger half.**~~ Retained rather than deleted: the `28.496` operand is wrong and
> the scope statement around it is right, and a reader who met the number elsewhere needs to find it here.

The figure's extent gap is **not** a rounding term on the GPU side. It is **an entire second unit**, which a
GPU-denominated grant does not reach — and the single largest leg in it (`2,759.1` CPU-core-hours, the
160-throw `uthrow` production) is also **the one leg that cannot be re-seeded at all** without the code
change, so funding does not move it.

**A one-seed increment is not an `M(ii)` measurement.** At the predeclared `n >= 6` the same accounting gives
**`235.34` A100-hours plus `332.02` CPU task-hours**, of which `234.47` A100-h (`99.6 %` of GPU) is the
`C_syst` path alone. §5 derives the shape; **§0 carries the corrected operands** (§5's tables still read
`28.496` and are marked superseded there).

---

## 0. THE CORRECTION — a missing job id, and the check that would have caught it

**Raised by the mediator; the defect is real; the ids below are from `sacct -j 55891346,55894759 -X` run
in this turn, not from the message.** `55891346` is a **truncated attempt**:

    55891346_0..4    COMPLETED  41.6-45.6 min   5 real universes        3.6264 A100-h
    55891346_5,6     FAILED     34:32, 34:32 }
    55891346_7,8     CANCELLED  19:56, 12:53  }  4 tasks of waste       1.6981 A100-h
    55891346_[10-18%8] CANCELLED  00:00:00        never started         0
    (index 9 appears in neither listing for this job)

    55894759_0..4    COMPLETED  10-36 s         5 resume-guard SKIPS    0.0269 A100-h
    55894759_5..18   COMPLETED  43.6-54.5 min  14 real universes       10.5811 A100-h

**The array is `0-18` = 19 tasks, and the composition is `188 = 169 vertical + 18 lateral + 1 CV` — so the
19 tasks are the 18 lateral universes plus the CV.** I costed 5 of them.

**MY CORRECTION IS ITSELF A CORRECTION TO THE MEDIATOR'S, and it is the same principle that saved the
`99` A100-h: do not extrapolate when you can measure.** The mediator proposed
*"FORECAST re-seed `14.36` = 19 x 45.35 min"*, where `45.35` min is the mean of `55894759`'s **14** real
tasks scaled to 19. **No scaling is needed: all 19 universes have a measured real production** — 5 in
`55891346`, 14 in `55894759`, and the resume skips are exactly why the two sets are disjoint and complete.

| | tasks | A100-h | basis |
|---|---|---|---|
| lateral+CV, `55891346_0..4` | 5 | 3.6264 | measured |
| lateral+CV, `55894759_5..18` | 14 | 10.5811 | measured |
| **lateral+CV, all 19** | **19** | **14.2075** | **measured, no extrapolation** (mean 44.87 min) |
| *(mediator's forecast, for the record)* | *19* | *14.3601* | *14-task mean scaled to 19* |
| excluded — resume-skip overhead `55894759_0..4` | 5 | 0.0269 | not work |
| excluded — `55891346`'s 2 FAILED + 2 CANCELLED | 4 | 1.6981 | history and provenance, not a clean-run forecast |

**The two figures agree to `1.1 %`; I use the measured one.** The `1.6981` A100-h of failed/cancelled work is
kept out of **both** the as-run and the forecast totals, per the mediator's framing, which is right: a
re-seed does not reproduce another run's failures.

### Corrected arithmetic

    RE-SEED  = 23.840 sweep(169) + 14.2075 lateral+CV(19) + 1.030 finalize(1) = 39.078 A100-h  [189 tasks]
    FULL     = re-seed + 9.564 dump(16) + 0.021 chk(1)                        = 48.663 A100-h  [206 tasks]

    published 28.496  ->  39.078   understated by +37.1 %
    against the 24 A100-h grant    39.078 / 24 = 1.63x   (63 % over)

    ONE COMPOSITE ARM (both seeds moved: C_syst path + uthrow leg)
                                                     GPU 39.078 A100-h  +  CPU 55.182 task-h
    ONE additional estimator seed, all four blocks:  GPU 39.223 A100-h  +  CPU 55.337 task-h
      C_syst share of the GPU column                 99.63 %
      C_syst per seed / C_stat per seed              268x   (was quoted as 195x)
    At the predeclared n >= 6:                       GPU 235.34 A100-h  +  CPU 332.02 task-h

**⚠ `39.078` AND `39.223` ARE DIFFERENT QUANTITIES THAT NEARLY COINCIDE, and the coincidence is not
rounding.** `C_syst` is `99.63 %` of the GPU column, so the `C_syst` re-seed (`39.078`) and the all-four-block
one-seed total (`39.223`) differ by `0.37 %` — small enough that a reader meeting them in adjacent documents
will assume one is the other printed to different precision. **They are not.** Lane A named this as the
retracted-values index's own *"two quantities that have historically agreed at the printed precision"* trap:
it is the condition under which one sentence can describe two things. **State which one you mean, every
time**, and note that `39.078` is the GPU column of a quantity whose CPU column is `55.182` task-hours —
**never quote either bare.**

**A composite arm necessarily carries the CPU term, and the code REFUSES the alternative rather than merely
implying it.** A composite arm's second seed is `unified_throw_cov.py`'s `--seed`, which threads into every
throw unfold (`:244`), every knob block endpoint (`:281`) and every flux block unit (`:297`); is stamped into
each slab (`:254`, `:285`, `:302`); and is enforced by the **F2 guard at `:417-419`**, which raises
`SystemExit` — *"refusing mixed-seed combine"*, the comment giving the reason as *"else `C_uni`/`C_block`
would mix estimator jitter across slabs."* **So not one slab is reusable across a seed change: all 71 CPU
tasks re-run** (`55821660`, `56427580`, `55821661`). Since that leg is `0` A100-h and `2,759.1` CPU-core-h,
**the composite arm's defining move is the leg carrying essentially the entire CPU bill** — the reason a
GPU-only figure is worst, not best, at a site whose subject is composite scope. *Raised as an unasserted
chain by lane A, which offered to withdraw it; traced here and confirmed.*

**`39.078` is MEASURED throughout** — every one of the 189 tasks in it has a realized elapsed. It is not a
forecast, with one named assumption: **a re-seed resumes nothing**, because a new estimator seed invalidates
every stored product, so the `55894759_0..4` skip path cannot recur. That assumption is load-bearing and it
is an assumption, not a measurement. **The `dump` leg is still excluded and that exclusion IS verified**
(`sweep_bank_5d.py`'s `do_dump` never calls `omnifold_loop`) — it is the one thing a re-seed genuinely reuses.

### ⚠ THE LESSON, and it is about my own method, not the mediator's

**Re-deriving a figure from its stated operands catches wrong arithmetic on stated inputs and is BLIND TO A
MISSING INPUT.** My `3.626` reproduces to the digit — for 5 of 19 universes. **Every figure reconciles
perfectly inside a scope that is too small**, so an ingredients receipt (`BEN-077`) is necessary and is
**not sufficient**: it can only be falsified by its own operands.

**The complementary check is one comparison: cross the id set against the DESIGN'S OWN MEMBER COUNT before
trusting a per-leg total.** `sacct` reporting `5` where the composition says `18 lateral + 1 CV` is visible
immediately, and the composition was **in this document**, two sections from the error.

**The aggravating fact, and it is the whole finding: I HAD ALREADY USED THIS TECHNIQUE IN THIS DOCUMENT AND
DID NOT APPLY IT TWICE.** The surviving vertical sweep was found precisely by scanning the window **by name**
because every id the status log recorded was `CANCELLED` — and I then confirmed completeness by counting
(`169 sweep5dBKGrun|COMPLETED` against 169 expected universes). **The lateral leg got neither the name scan
nor the count**, because it had a plausible id that returned `COMPLETED` rows. **A `CANCELLED` id forces the
search; a partially-`COMPLETED` id silently satisfies it.** That is the enabling condition, it is general,
and it is the opposite of where I was looking. Filed `BEN-247`.

**On the mediator's flagged unknown — *"whether the lateral leg is re-seedable at all… it could be a third
hardcoded site"* — ANSWERED, and it is NOT:** §4 of this document already measured it.
`sbatch_unfold_5d_detector_bkgaware_gpu.sh:37,51` passes `--seed 42` into
`unfold_nd_omnifold_unbinned.py`, where `--seed` sets `random_state` on the classifiers
(`:930-931`, `:956-959`) and the data/MC draw is a **separate** `--bootstrap-seed` (`:904-905`). **So the
lateral arm has the two-role separation, is re-seedable today with no code change, and is the only `C_syst`
arm that is.** The vertical sweep (`23.840` of the `39.078`) is still blocked by
`sweep_bank_5d.py:252`, so **`39.078` does NOT imply the run is possible** — which is exactly the inference
the mediator asked not to license.

### ⚠ AND THE SENTENCE ABOVE CREATES A HAZARD, SO THE REFUSAL BELONGS BESIDE IT

*"The lateral arm is the only `C_syst` arm that is re-seedable today"* makes a **laterals-only estimator-seed
scan the cheapest run-condition-(b)-clean job on the board** — 19 tasks, `14.2075` A100-h, no code change, no
ruling. Assistant flagged that it **must be refused as `M(ii)`** and that is right. **REFUSED here, in the
document that would otherwise license it.**

**But not for the reason offered, and the difference matters because the offered reason is false.** The
stated ground was *"18 of 188 is the minor leg."* **That is a MEMBER COUNT doing duty as a VARIANCE SHARE,
and the only per-group figures the committed summary carries point the other way.** The 18 lateral universes
are exactly `detector_universes.txt` — `BeamAngleX/Y`, `MinosEfficiency`, `MuonResolution`,
`Muon_Energy_MINERvA`, `Muon_Energy_MINOS` (12) and `GEANT_Neutron/Pion/Proton` (6) — which map **1:1** onto
two of `uq_universe_5d_summary.txt`'s five groups, leaving the other three to the sweep:

    lateral  (Muon reconstruction 2.789e-38  +  Hadronic response 4.017e-38)          = 6.806e-38
    vertical (Models 8.964e-38 + Normalization 4.507e-39 + Flux 3.993e-39)            = 9.814e-38
    -> lateral is 41 % of the summed figure, on 9.6 % of the members

**That `41 %` is NOT a variance share and must not be quoted as one:** those are **sums of per-band
sqrt-traces**, not a quadrature decomposition, and the proof is in the same file — `total syst
sqrt-trace = 4.3515e-38` is **smaller than either arm's sum**, so the two do not add to the total and no
share is derivable from them. **The lateral arm's actual variance share is UNMEASURED.** What the figures do
establish is the negative: **the lateral arm is not a small perturbation by any available reading, so
"minor leg" is unsupported** — 18 detector universes can carry large shifts precisely because a detector
band moves the reconstructed quantities and cannot be reweighted away, which is why it needs a re-unfold at
all.

**The refusal that does not need a variance share, and is therefore the one to use:** a laterals-only scan
**holds the vertical arm's estimator seed fixed at `42` by construction**, so it measures the seed
sensitivity of one sub-block while `169` of the `188` universes contribute a **constant**. That is a partial
derivative reported as a total, and it is not *"the magnitude of what varying seeds would have contributed"*
under **any** weighting of the two arms — including a weighting that turned out to favour the laterals.
**It would be a defensible `M(ii)` LOWER BOUND on the lateral arm alone, labelled as such, and nothing
more.** A number filed as `M(ii)` that measures one arm at fixed other-arm seed is the same scope defect
this document exists to correct, arriving with a receipt.

---

## 1. What `28.50` covers, re-derived this turn — **§0 SUPERSEDES THIS SECTION'S LATERAL ROW AND TOTALS**

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

**⚠ ATTRIBUTION, DISAMBIGUATED BEFORE THE CREDIT — the lane named below is `Assistant [28640e]`, which is
NOT lane `A [84e2e8]`.** Both were live and distinct in `ListAgents` at the time of writing, and **lane A
explicitly DECLINED this credit**: it has no record of working on `bootstrap_nd.py`, `seedscan_split.py` or
gate 1's leg structure, and it notes the name *"Assistant"* has been used for at least two different sessions
in its hearing today. **A reader who maps *"Assistant"* onto the lane holding `BEN-390-399` would therefore
manufacture a misattribution in the flattering direction** (`BEN-214`'s shape), **and the only mechanism that
could catch it is the party declining the credit, which is what happened.** Recorded here rather than
silently corrected, because the ambiguity is in the name and will recur.

**CORROBORATED INDEPENDENTLY, 2026-08-17, and the independence is evidenced rather than assumed.** The
`Assistant [28640e]` lane reached the same gate-1 conclusion — that `--fixed-data-seed` already pins the draw and
routes `--seed` to the estimator, that `seedscan_split.py:36` exposes `--estimator-seed`, and that gate 1 is
therefore **two modules rather than four legs** — **citing the code and its quoted help text directly, not
this document.** The independence claim rests on `Assistant`'s own unprompted statement, made *before*
producing the finding: *"`EXTENT-20260817-…md` exists on main and names this launcher; **I HAVE NOT READ
IT**, and it may already carry some of §1."* **So this is a second derivation, and §3/§4 are corroborated
rather than merely restated.**

**THIRD DERIVATION, and it comes with an UPGRADE TO MY OWN CITATION.** Lane `A [84e2e8]` — the lane that
declined the credit above — then ran the check itself, reading the tree before reading this document and
without reference to it, and confirmed both flags exist and route as described. **A's contribution is not the
agreement but a correction to which citation is load-bearing: HELP TEXT IS DOCUMENTATION.** A help string
describing seed routing is a claim about what the author *intended*; the **behaviour** is
`bootstrap_nd.py:28-29`, two lines below it:

    :28  _data_base = a.fixed_data_seed if a.fixed_data_seed is not None else a.seed
    :29  _est_seed  = a.seed             if a.fixed_data_seed is not None else a.estimator_seed

**Cite those, not the help string.** This section already cites both (`:28`, `:29`, `:37`, and `:54` for the
ML leg), so nothing here rested on documentation alone — **but the agreement between the two is worth
stating explicitly rather than leaving implicit**, because it is `BEN-391`'s instance 2 in miniature, where
*"no committed DOCUMENT records X"* was true and got read as settling a question about **code**. **The help
text and the implementation agree here; that is a finding, not an assumption.**

**AND A DECLINED TO OVERSTATE ITS OWN PASS, which is the part I must not inherit as completeness:** A
verified that the two flags exist and route as described. A did **NOT** verify *"gate 1 is therefore two
modules rather than four legs"*, which depends on what the four legs were — a document A has not read.
**Premises thrice-derived; the conclusion is not corroborated by A.** And the conclusion is in any case now
qualified by the inversion above, so what stands thrice-derived is the **capability**, which is precisely the
half that turned out not to help.

### ⚠ INVERSION: THE CAPABILITY FINDING STANDS AS FACT AND ITS CONSEQUENCE REVERSES UNDER SPEC (B)

**Added 2026-08-17, after lane C conceded (B) as the `M(ii)` specification.** Everything above about the
capability is **true and re-verified** (`bootstrap_nd.py:28-29`,
`_est_seed = a.seed if a.fixed_data_seed is not None else a.estimator_seed`). **What is false is that it
helps.**

Under **(B)** `M(ii)` is a **joint** measurement on the composite, so a coherent variation across the four
legs sharing estimator seed `42` needs **all four seed-variable at once**. A joint measurement **cannot
yield a partial result**, so **partial capability buys nothing** — and therefore
**`sweep_bank_5d.py:252`'s hardcoded `42` stops being one of two parallel edits and becomes the BLOCKING
DEPENDENCY.** Lane C's summary is the one to carry, and **both halves must travel together because the first
reads as good news and the second is why it isn't:**

> **Gate 1 is SMALLER than anyone said in module count, and MORE SERIAL than anyone said in sequencing.**

**So my §7 item 4 is withdrawn** (marked there) and the *"smaller and better-precedented"* sentence above
should be read as a statement about **module count only** — never about schedule or about how much of `M(ii)`
is reachable today, which is **none of it**. **This is not a defect in the measurement; the specification
changed after it was filed.** The mediator, who handed me the favourable framing, self-reported the transport
error as the same class again: **a true capability claim carried without the specification it depends on, and
the specification is what determines whether the capability is useful.**

**MY OWN SEED MAP IS WHAT MADE (A) FAIL, and the correlation is documented rather than inferred.** The
decisive argument against (A) was that four legs at seed `42` make their estimator noise move **coherently**,
so (A)'s independent-additive assumption fails exactly where it is applied. The named correlation is the
**retired jitter term** — verified from history at this commit,
`git show a0cdc01:nd-unfolding/unified_throw_cov.py` `:225-227`:

> *"OmniFold run-to-run jitter does NOT cancel against `x_cv`; the block units + `x_cv` all share one seed,
> so their jitter cancels in `(x_b - x_cv)`."*

— which **is** a statement that the covariance is set by seed-sharing. Corroborating, on the band axis:
`docs/HIGHER_DIM_OMNIFOLD_DESIGN.md:153-155` (verified at `docs/`, not `nd-unfolding/`) records the block-sum
inference **measured, rejected and rebuilt against** — *"block-sum underestimates the vertical systematic
~2x (jitter-corrected unified/block sqrt-trace `2.01`)"*.

**THE DECORRELATION ESCAPE HATCH, pre-answered because I own the seed map and will be the one asked.** The
argument is: the four legs at `42` run on **different inputs**, so a shared seed initialises the same RNG
state but consumes draws against different data, and perhaps the perturbations decorrelate after all. **Lane
C considered and declined to offer it**, on the ground that it is an empirical claim nobody has measured,
which puts it in `M(ii)`'s own position — *letting an unmeasured convenience choose the criterion.* **That is
right, and it is stronger than stated: the hatch is foreclosed by the IDENTICAL blocker.** Testing whether
two legs' estimator perturbations decorrelate requires varying **one** leg's seed independently of the other;
for the sweep leg that is `sweep_bank_5d.py:252`, hardcoded with no flag. **So the argument that would excuse
the code change cannot be evaluated without the code change.** It is not merely unmeasured — on the current
footing it is unmeasurable, for the same reason `M(ii)` is.

**The distinction is recorded because I nearly lost it in the opposite direction.** The finding first reached
me *relayed as new information*, and I flagged it back as my own conclusion returning to me — correctly on
the facts available, and **wrongly on the merits**, because the derivation really was independent; what was
missing was its **route**. `BEN-312` is one number derived by three parties from one source, where agreement
read as corroboration; **this is that mechanism in reverse — genuine corroboration reading as an echo — and
in both directions the defect is that the route is not carried with the fact.** Corroboration and echo have
**opposite** evidential value, so a relay that omits the route destroys the difference. **The check is one
clause: when relaying a claim, say where it came from.** That is the receipt-ingredients rule
(`CONVENTION-receipt-ingredients.md`, `BEN-077`) applied to the **provenance of a claim** rather than to the
operands of a number. *Transport error the mediator's, self-reported; independence established from
`Assistant`'s own prior disclaimer; framing this lane's, routed to lane A, which owns the transport class.*

## 5. Cost per seed-dependent leg, from measured `sacct` elapsed

**The `M(ii)` instrument for the stat leg is already written and has already run.**
`sbatch_ai1_estimator_scan.sh:23-24` is `bootstrap_nd.py --npz of_inputs_5d.npz --seed ${TASK}
--fixed-data-seed 0 --iters 5` — fixed draw, varying estimator seed, i.e. exactly run condition (b):

    55919500_1  ai1est5d  COMPLETED  00:08:44  1x a100, 32 cpu, shared_gpu_ss11  start 2026-07-14T16:55:38
    55919500_2  ai1est5d  COMPLETED  00:08:46  1x a100, 32 cpu, shared_gpu_ss11  start 2026-07-14T18:18:43
    55919500_3, _4, _[5-12%4]        CANCELLED by 112498 at 2026-07-14T19:20:00
    55916613_[3-12%1]                CANCELLED by 112498 at 2026-07-14T16:34:07

**`0.2917` A100-h / 2 seeds = `0.1458` A100-h per estimator seed.** `n=2`, and I am quoting the per-seed
figure rather than a scaled total wherever a total is not needed.

**`n` RAISED FROM 2 TO 11, on lane C's challenge that `268x` inherited an `n=2` with no spread estimate.**
`bootstrap_nd.py`'s per-task cost does not depend on **which** seed role varies — same `.npz`, same
`--iters 5`, same `lgbm` estimator, same 1-A100 hardware; `--fixed-data-seed` changes only which RNG seeds
the weight draw. So the 9 real replicas inside `boot5dG 55871150` (`_3`..`_11`) measure the same operation,
and pooling is **checked against the data rather than assumed** — the two sets' ranges nearly touch:

    ai1est5d   n= 2   524-526 s   mean 525.0 s = 0.1458 A100-h   (fixed draw, varying estimator seed)
    boot5dG    n= 9   505-519 s   mean 509.7 s = 0.1416 A100-h   sd 4.2 s
    POOLED     n=11   505-526 s   mean 512.5 s = 0.1423 A100-h   sd 7.3 s = 1.4 %

    ratio to C_syst's 39.078 A100-h/seed:  268x (ai1-only) | 275x (pooled) | 267-279x (per-task range)

**So `268x` is good to about `±4 %` and now carries a measured spread instead of none. The conclusion is
untouched at every value**, which is what C said it would be.

**One observation against pooling, recorded so nobody over-reads the pooled figure:** the two `ai1est5d`
tasks are the **two slowest of the eleven** — `526` and `524` s against a `boot5dG` maximum of `519`. Under
random assignment that has probability `1/C(11,2) = 1.8 %`, which is **suggestive of a small real systematic
in the `--fixed-data-seed` path (or in the node/day, 07-14 vs 07-13) and is a post-hoc test on a pattern I
noticed, at `n=2`** — so it is not a finding. Its practical effect: **pooling would slightly UNDERSTATE the
fixed-draw cost, so `0.1458` stays the headline as the conservative choice and the exact operation**, with
the pooled set serving as the spread evidence rather than as the estimate. The array delivered 2 of 12; the 12-seed
`\gbdtAiEstTrace` result came from the packed `ai1_packed_loop.sh` run inside an interactive `salloc`, which
is **not separately attributable in `sacct`** — `FOOTING-20260817-gbdtaiesttrace-12-seeds.md:66-69` costs it
independently at `~1 GPU-node-hour` from `CONC=6`, 2 waves. **My `1.750` A100-h for 12 seeds (`= 12 x
0.1458`) and that `~1 GPU-node-hour` are in different units** — a Perlmutter GPU node is 4 A100s, so mine is
`0.44` node-h against their `~1`. **They do not agree, and the FOOTING figure is the more conservative**;
I have not tried to reconcile them and the discrepancy is the packing, not the arithmetic. (Node width is
in-repo, not from memory: `sbatch_boot5d_gpu_interactive.sh:4` requests `--nodes=1 --gpus=4`, and
`gpus-per-node=4` appears elsewhere in the launcher set.)

### ⚠ RECONCILED 2026-08-17, AND "THEY DO NOT AGREE" WAS MY OWN ASYMMETRIC COMPARISON

**The packed run is NOT unattributable — I looked for the wrong name.** A covering name-scan for
`ai1|est5d` over the four windows returns three job names, not one: `ai1est5d` (6 rows, the array),
**`ai1int` (3 rows, the packed interactive run)** and **`ai1comb` (1 row, the combine)**. Measured, all on a
full 4-A100 node (`gres/gpu:a100=4`, `NCPUS=128`):

| job | state | elapsed | node-h | A100-h |
|---|---|---|---|---|
| `55922588` `ai1int` | CANCELLED | 00:01:02 | 0.0172 | 0.069 |
| `55922613` `ai1int` | **TIMEOUT** | 01:00:20 | **1.0056** | 4.022 |
| `55923713` `ai1int` | COMPLETED | 00:27:31 | 0.4586 | 1.834 |
| `55924460` `ai1comb` | COMPLETED | 00:01:51 | 0.0308 | 0.123 |
| | **as-run total** | | **1.5122** | **6.049** |

**So `FOOTING`'s `~1 GPU-node-hour` is measurable after all, and as-run it is `1.51` node-hours — of which
`1.01` is a job that TIMED OUT.** The `~1` figure lands almost exactly on the timeout.

**And the reconciliation is not "packing" — it is that the two numbers are DIFFERENT QUANTITIES, which makes
my own earlier sentence an instance of the failure this document keeps filing.** `FOOTING`'s figure is
**allocation** (a whole 4-GPU node held for a wall-clock interval); mine is **work** (12 tasks x measured
per-task GPU time). Those are never comparable, and I wrote *"they do not agree"* — a delta asserted across
two conditions I had not named. **The correct statement:** the completing run plus combine is `0.4894`
node-h and my work-based figure is `0.4374` node-h, **consistent to 11 %**, and `55923713` is a *lower*
bound because `rg_skip_if_complete` means it only finished what `55922613` had not. **There was no
disagreement to reconcile; there was a unit-of-account difference plus a wasted hour.**

**Consequence for the ratios in the next subsection:** the honest AI1 denominator depends on which question
is asked — `1.51` node-h **as-run including the timeout**, `~0.49` node-h **for a clean completing pass**, or
`0.4374` node-h **of actual work.** Quoting any of them as *"the cost of an AI1 scan"* without saying which
is the same defect one level down, so all three are stated here and the ratios below name theirs.

### ⚠ AND THAT CROSS-UNIT PAIR HAS ALREADY PRODUCED A RATIO — `~28.5x` IS WRONG TWICE OVER

`SCOREBOARD-20260817-quarantine-seven-causes.md:133-134` (lane C's file, **not edited from here**) reads:
*"The measured unit on the candidate footing is `28.50 A100-h per re-seed`, `~28.5x`."* That `~28.5x` is the
understatement factor of C's own withdrawn `~1 GPU-node-hour`. **Two independent defects, and the dead
numerator is the smaller of them:**

1. **CROSS-UNIT.** It divides A100-hours by GPU-node-hours as though `1 A100-h = 1 GPU-node-h`. At 4 A100
   per node, the same-unit ratio of C's **own** operands is **`7.12x`** (`28.50 / 4`), not `28.5x` — so the
   ratio was off by a factor of 4 **before** its numerator was found to be stale. It is the exact unit
   confusion the paragraph above this one warns about, committed one paragraph later by a different lane.
2. **NON-COMMENSURABLE, which no unit conversion repairs.** The numerator is **one** estimator seed of
   `C_syst`; the denominator is **twelve** seeds of `C_stat`. Different block, different member count. A
   ratio of *"1 seed of one thing"* to *"12 seeds of another"* measures nothing at all.

**The quantity that cell wants — how much dearer the candidate footing is than AI1's — is the per-seed
like-for-like ratio, and it is `268x` (`267-279x` over the pooled `n=11` per-task range):** `39.078` A100-h
per `C_syst` seed against `0.1458` A100-h per `C_stat` seed. Same unit, same operation shape, both measured.

**If the 12-seed comparison is wanted instead, it has three denominators and they are not interchangeable**
— the subsection above measures all three rather than leaving the discrepancy open:

    vs AI1 as-run allocation incl. the TIMEOUT   1.5122 node-h = 6.049 A100-h  ->   6.5x
    vs AI1 clean completing pass + combine       0.4894 node-h = 1.958 A100-h  ->  20.0x
    vs AI1 work (12 x 0.1458)                    0.4374 node-h = 1.750 A100-h  ->  22.3x

**The `~1 GPU-node-hour` that `FOOTING` quotes is none of these three exactly** — it sits almost on the
timed-out job alone (`1.0056` node-h). **So a ratio against "the AI1 figure" is undefined until the
denominator is named**, and the per-seed `268x` is preferable precisely because it needs no denominator
choice at all.

**C owns that cell and has been notified. Nothing in that file was edited from here.** This is lane A's
"descendant ratio" hazard concretely: `~28.5x` does not string-match `28.50`, so a retraction of the parent
propagates straight past it — which is why A indexed the ratio as a **separate** dead value. **C's
conclusions at `:158-164` are unaffected and my measurements strengthen them:** `M(ii)` is blocked on two
code changes before it is a cost question, and measured, the two blocked legs are `99.6 %` of the GPU and
`99.7 %` of the CPU bill while three of five legs need no change at all.

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

### The accounting — **⚠ THE `C_syst` OPERAND IN BOTH TABLES BELOW IS SUPERSEDED BY §0**

**The two tables keep `28.496` as written**, per this repo's convention of leaving written history written,
and the corrected figures are stated here so no reader has to carry them from §0: `C_syst` per seed is
**`39.078`** A100-h over **189** tasks (not `28.496` over 175); the one-seed GPU total is **`39.223`** and
`C_syst` is **`99.63 %`** of it (not `99.49 %`); the `n>=6` GPU total is **`235.34`** (not `171.85`), which is
**`9.8x`** the `24` A100-h grant (not `7.2x`). **The CPU columns are unaffected** — the defect was entirely
in the lateral arm of the GPU leg.

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

1. **The `28.50` figure is wrong twice over, and both ways understate.** It **undercounts its own leg** —
   the lateral arm is 19 universes, not 5, so the `C_syst` re-seed is **`39.078`** A100-h, `+37.1 %` (§0);
   and it is **`99.6 %` of the GPU bill and `0 %` of a CPU bill that is the larger half.** **Do not
   authorize `28.50` as "the re-seed cost."** Against the `24` A100-h grant the corrected figure is
   `1.63x`, so it still goes to Joseph — the *decision* the `28.50` implied is unchanged, the *number*
   was not defensible.
2. **The decision is not a cost decision.** Two of the four blocks cannot be re-seeded at any price today
   (`sweep_bank_5d.py:252` hardcoded; `unified_throw_cov.py`'s dual-role `--seed`), and those two are
   `99.5 %` of GPU and `99.7 %` of CPU. Funding does not move them.
3. **The change is smaller in MODULE COUNT and MORE SERIAL in SEQUENCING than I said, and the second half is
   why the first is not good news.** Three of five legs already have the separation, and
   `bootstrap_nd.py:28-29` is a working in-repo implementation of the exact pattern. **But under spec (B) —
   conceded by lane C — `M(ii)` is a JOINT measurement, so partial capability buys nothing and
   `sweep_bank_5d.py:252` is the BLOCKING dependency rather than one of two parallel edits.** Never quote the
   module count without the sequencing (§4's inversion note).
4. ~~**A cheap partial measurement exists that needs no code change and no ruling:** the `C_stat` and `C_ML`
   estimator axes at `n=12` cost **`1.75` A100-h + `1.86` CPU task-hours** together — inside any grant. It
   would not answer `M(ii)` for the dominant blocks, and **must not be reported as if it did**; it would
   test the `seedscan_split.py:5-7` near-determinism premise, which is currently asserted and unmeasured.~~
   **⚠ WITHDRAWN AS AN `M(ii)` RECOMMENDATION, 2026-08-17 — the specification changed under it.** Lane C has
   conceded **(B)**: `M(ii)` is a **JOINT** measurement on the composite, with `M(ii)` recorded UNMEASURED.
   **Under (B) a coherent variation across the four legs at seed `42` requires all four seed-variable AT
   ONCE, so a partial capability buys NOTHING toward `M(ii)`** — a joint measurement cannot produce a partial
   result the way (A) would have. My caveat above (*"would not answer `M(ii)` for the dominant blocks"*) was
   **too weak**: it does not answer `M(ii)` at all, even partially. The costs stay correct and the
   near-determinism test remains a legitimate *auxiliary* run, **but it must not be offered as a step toward
   `M(ii)`, and I am withdrawing it as one rather than leaving it to be quoted that way.** See §4's inversion
   note.

**Nothing run. `OI-130`'s preservation condition binds whatever any eventual run produces.**
**The two-module seed separation is NOT implemented.**

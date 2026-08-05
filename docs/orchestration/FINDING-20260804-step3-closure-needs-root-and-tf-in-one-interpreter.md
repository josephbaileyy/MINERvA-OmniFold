# FINDING 2026-08-04 — RESTORE Step 3 cannot run: the closure needs ROOT *and* TF 2.15 in one interpreter, and no such interpreter exists on Perlmutter

*Measured on Perlmutter, 2026-08-04, by running the step. This establishes the environment blocker;
subsequent review also found the target construction is discarded by the closure and its identity
test has only smoke-test power. **No code was changed and no substitute refiner was injected** by
the measured run.*

> **DECIDED 2026-08-04; implementation pending.** The nominal will consume the hash-bound
> precomputed Gate-2 target; the ordinary MC closure will use an MC-only loader path and will not
> claim to exercise that target. No combined ROOT/TF publication environment and no two-process
> closure handoff will be introduced. The canonical decision, including the required powered
> closure, is
> [`DECISION-20260804-B4-STEP3-RECEIPTS.md`](DECISION-20260804-B4-STEP3-RECEIPTS.md#d2--restore-step-3-separate-target-ownership-from-mc-closure-construction).
>
> **Correction to this finding's original premise:** the nominal does *not* currently consume
> `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy`; it also rebuilds refinement through
> `build_fullevent_loaders` (audit J04). The environment measurements below remain valid.

## The blocker

`closure_fullevent_fps.py` calls `fe.build_fullevent_loaders(...)` at `:116`. With the default
`bkg_mode="negweight-refined"` — the locked publication nominal — that call reaches
`fullevent_fps_dataloader.py:1328`:

```python
refiner = refine_fn if refine_fn is not None else learned_stay_positive_refiner()
```

and `learned_stay_positive_refiner()` at `:671` does `from unfold_2d_omnifold_unbinned import
refine_stay_positive`, which imports ROOT. Meanwhile the closure needs TensorFlow for the PET
network. Measured traceback under the canonical env layering
(`source setup_salloc_env.sh; module load tensorflow/2.15.0`):

```
File ".../closure_fullevent_fps.py", line 116, in main
    data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
File ".../fullevent_fps_dataloader.py", line 1328, in build_fullevent_loaders
    refiner = refine_fn if refine_fn is not None else learned_stay_positive_refiner()
File ".../fullevent_fps_dataloader.py", line 671, in learned_stay_positive_refiner
    from unfold_2d_omnifold_unbinned import refine_stay_positive
ModuleNotFoundError: No module named 'unfold_2d_omnifold_unbinned'
```

## Why no interpreter satisfies both — surveyed, not assumed

| environment | python | ROOT | TF / Keras |
|---|---|---|---|
| `root_6_28` (what `setup_salloc_env.sh` activates) | 3.11.14 | **yes** | no |
| `cernroot` | — | **yes** | no |
| `omnifold_py310` | — | no | no |
| `module load tensorflow/2.15.0` | 3.9.18 | no | **2.15.0 / 2.15.0** |

* There is **no `root` module** on Perlmutter (`module avail root` → "No module(s) or extension(s)
  found!").
* `module load tensorflow/2.15.0` **shadows** the conda python entirely — `which python3` becomes
  `/global/common/software/nersc9/tensorflow/2.15.0/bin/python3`.
* The two cannot be bridged by `PYTHONPATH`: root_6_28's ROOT bindings are built for
  **python3.11** (`.../envs/root_6_28/lib/python3.11/site-packages/ROOT`) and the TF module is
  **python3.9.18**. CPython extension modules are not compatible across minor versions.

`sbatch_pet_nominal_bkgsub.sh:71` already records the same wall from the other side:
*"Extraction needs PyROOT (TF-module python has none): source the analysis env."* It solves it by
running the two stages as separate jobs. The closure is a single process and cannot.

## Correction: the nominal is affected too

`sbatch_pet_fullevent_nominal.sh:20` says it *"Consumes the negweight-refined **literal Gate-2
target**"*, but the launcher passes the raw G2 NPZ and `train_fullevent_nominal.py` calls
`build_fullevent_loaders` without a precomputed-target argument. The loader has no such argument;
its signature (`:1041-1046`) offers only `refine_fn`, a callable. Thus Step 4 would reach the same
ROOT/TF conflict. This is the already-confirmed J04 defect: the certified Gate-2 target is silently
rebuilt rather than consumed.

The closure additionally discards the measured loader returned by that call and constructs its
pseudo-data from MC reco rows. Its refinement call is therefore both environment-blocking and dead
with respect to the statistic the closure reports.

## Why the obvious workarounds are not available

1. **Inject a substitute `refine_fn`.** Refused. `:1329-1330` sets
   `refine_backend = getattr(refine_fn, "__name__", ...)` whenever `refine_fn is not None`, and
   the canonical string `"u2d.refine_stay_positive"` is emitted *only* in the `None` branch. This
   is exactly the path that self-reports `refinement_is_learned_production=False`, which Step 4
   names as the reason Delta cannot produce a nominal. A closure certified through it would not
   certify the nominal estimator.
2. **`--bkg-mode purity`.** Refused by Step 3 in terms: *"Do not accept `--bkg-mode purity` as the
   closure. It is a labeled control."*
3. **Run it on Delta instead.** Same wall, worse: the NGC container has no ROOT at all.

## Consequence for the restore chain

Step 2b's Gate-4 re-issue *composes* Step 3's `--json` report
(`validate_pet_nominal_gate4.py --closure-report`). So:

```
Step 3 blocked  ->  Step 2b blocked  ->  Step 4's precondition unreachable
```

Step 4's launch authorisation was explicitly conditional on Step 2b flipping
`nominal_pet_training_allowed` to true. That condition cannot currently be met, so **not
launching is the correct execution of that authorisation, not a departure from it.**

## Options, all of which are the user's call

1. **Build one combined env.** **Measured feasible 2026-08-04** — `conda create --dry-run -c
   conda-forge python=3.11 root tensorflow=2.15` solves cleanly and proposes exactly the right set:

   | | python | ROOT | TF | Keras | numpy |
   |---|---|---|---|---|---|
   | `tensorflow=2.15` **(pin it)** | 3.11.15 | 6.32.2 | **2.15.0** | **2.15.0** | 1.26.4 |
   | `tensorflow` unpinned | 3.11.15 | 6.40.02 | 2.19.1 | **3.15.1** | 2.4.6 |

   **The pin is not optional.** Unpinned resolves to Keras **3**, which is the exact reason local
   Mac TF cannot run the vendored Keras-2 PET net. Pinned gives Keras 2.15.0 and a numpy matching
   the TF module's 1.26.3. Add `scikit-learn` explicitly — the refiner needs it.

   Two honest caveats: ROOT would move **6.28 → 6.32.2**, and a conda TF is not the NERSC
   `tensorflow/2.15.0` module the receipts reference. So the closure's provenance would record an
   environment no receipt has seen. For a publication gate that is a real consideration, not a
   detail. It is, however, low-risk to *try*: a new env touches nothing existing.
2. **Give the closure a precomputed-target path**, so it consumes
   `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` the way the nominal does. This is the change most
   consistent with the existing architecture, and it makes Step 3 depend on Step 2's re-issued
   weights — which is arguably correct anyway, since a closure certifying the nominal ought to
   read the same target the nominal reads. Requires editing `closure_fullevent_fps.py` and
   `build_fullevent_loaders`, both of which feed a receipt.
3. **Split the closure into two processes** — refine under `root_6_28`, hand the weights to a
   TF-only stage. Mirrors what `sbatch_pet_nominal_bkgsub.sh` already does for extraction.

The decision record supersedes this option list. Its nominal half takes the precomputed-target
architecture of option 2; its closure half removes the unused measured-target construction
entirely, because making the closure read an artifact it discards would not certify that artifact.

## Provenance

Found by running Step 3's own command for the first time since its repair at `b5ec859`. The
runbook notes that the PASS at `36ab84d` was obtained against the pre-gate dataloader and that
"a repair is not a receipt" — consistent with this conflict never having been exercised, though
that inference is mine and not established by the record.

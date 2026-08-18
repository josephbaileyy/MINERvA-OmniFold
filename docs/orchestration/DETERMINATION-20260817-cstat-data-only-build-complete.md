# DETERMINATION — `C_stat^data` BUILT: two sites, one shared predicate module, 30 controls green

**Lane E, 2026-08-17.** The data-only ensemble's construction, built to lane C's specification
(`BEN-407`, `BEN-408`, `BEN-409`) after seven sites were found by attempting rather than inspecting.

**NOTHING SUBMITTED. No GPU, no training, no unfolding, no `sbatch`. No pinned file edited — the
differential pin test's mismatch set did not grow. The 151 A100-h remains authorized and unspent.**

---

## What was built

| file | status | why |
|---|---|---|
| `nd-unfolding/pet/cstat_data_only.py` | **new** | P1–P8 in ONE home. Both drivers import it; the extract driver could not import the train driver without dragging TensorFlow into a stage that does not need it, and two copies of one predicate is lane A's `OI-65` shape (`BEN-411`). Verified: imports with **no TF in `sys.modules`**. |
| `nd-unfolding/pet/train_fullevent_replica.py` | modified | `--cstat-product`, one dispatch on the tag into a separate named path, P1–P8 asserted **live inside `replica_atomic_data_only` before the write**. |
| `nd-unfolding/pet/extract_fullevent_replica.py` | modified | data-only branch dispatched **before** the three-stream coherence gate; P1–P4, P6, and P5′ on persisted evidence. |
| `nd-unfolding/tests/test_cstat_data_only_predicates.py` | **new** | 30 tests, **0 skipped**. |

**The dispatch is once, on the tag, into a separate path — so the ~13 sites that read
`meta["bootstrap"]` are NOT REACHED rather than each branched.** Thirteen `if data_only:` tests
would have been their own defect, and my own reconnaissance had counted the thirteen reads without
questioning the structure — the specification replaced work that would have been a defect rather
than speeding up work I was going to do.

---

## The predicates, and the two that are not what the spec first said

**P1** product tag, absence raises, and **its converse**: the three-stream validator rejects a
data-only tag when present while *tolerating absence*, because the archived 50 predate the tag and
requiring it there would fail a family this build must not touch.
**P2/P3** MC factors persisted, full-length, **explicitly ones** — never inferred from absence.
**P4** the coherence check **surviving**, re-pointed at the stream that actually varies, and derived
from the production `coherent_bootstrap_factors` rather than a local reimplementation.
**P5a/P5b** — see below.
**P6** seed under `data_bootstrap_seed`, so `BEN-405`'s `-1` sentinel collision is unreachable.
**P7** all three of `step1_class_ratio_loader_stamped`, `step1_class_ratio_applied`,
`weights_embody`; absence of any one raises (`BEN-077`: ship both operands so they *can* contradict).
**P8** the loader's own `step1_class_ratio` stamp is left **exactly as written**; the correction is
additive, because overwriting it would make a loader-stamped field assert what the loader did not do.

### P5 could not pass as specified, and the loader's own comment said so

`hash_array(w_truth) == hash_array(w_truth_full[imc])` is false even with the MC completely
unthinned: the MC DataLoader normalizes, so the truth leg lands at `1e6·sum(w_truth)/sum(w_reco)`
**by construction** — stated in `fullevent_fps_dataloader.py:1344-1347`, three lines above the call
it describes. Split along C's rule:

- **P5a — bit-exact.** The claim is that *nothing happened*, and an absence has no rounding. The
  **zero pattern** is the exact signature: Poisson(1) zeroes ~1/e of rows, a positive scalar zeroes
  none.
- **P5b — toleranced closure, ≤ 4 float32 eps.** The claim is that *a specific computation happened*.
  The scalar is **derived independently** as `1e6/sum(w_reco_full[imc][pass_reco])`, so P5b also
  catches a *wrong* normalization, which a hash comparison could not. It **asserts its own
  `size == 1` precondition** rather than inheriting the launcher's guard (`BEN-386`).

### The measured leg: `R` must vary, and it is the only route by which it can

`normalize` forces `sum(weight[pass_reco]) == 1e6·R` whatever the pre-normalization sum was, so the
data draw carried by the refined target is **divided back out exactly**. Freeze `R` and all fifty
replicas share one measured normalization — the rate term removed by *exact cancellation*, not
attenuated, producing a **shape-only** statistical uncertainty under a name the field reads as
total-rate. The driver therefore recomputes `R` with the data factor and rescales, with a closure
assertion; and **the independently derived nominal `R` must reproduce the loader's own stamp**, which
is one assertion covering every operand choice.

---

## The controls: 30 tests, 0 skipped, each shown to fire

Every control **mutates a synthetic store** — never disables a check — and each is paired with the
unmutated positive control in the same suite. Predicates are **imported from the shipped module**, so
the code under test is the code that ships, and each one's source is asserted **non-empty and
carrying its `raise`** before anything is asserted on it, because on the P5A launcher guards that
discipline caught an empty extracted file exiting 0.

Named controls the spec required by name, all green:
- a constant derived from the **truth** leg is rejected — the *plausible* mistake, since
  `dataloader.py:148` selects `weight_reco`, and the plausible mistake is the one that ships;
- a **flush-to-zero** subnormal fails P5a, **and that is correct**. Constructed deterministically
  rather than hoped for: the first version *skipped* because its premise did not arise, and a
  control that skips is a control that did not fire;
- `-1` under `data_bootstrap_seed` is rejected;
- P5b refuses `size != 1`.

**One control caught my own prose-versus-code confusion.** The P5′-locality test searched the raw
file and failed on the block's **own comment**, which names `w_truth_full[imc]` while explaining that
the code must not use it. It now strips comments before asserting — `OI-96`'s defect reproduced
inside its own control, one file along, and caught by the control.

---

## Verification

```
30 passed, 0 skipped   test_cstat_data_only_predicates.py
70 passed              + test_gate5_replica_driver.py + test_fullevent_fps.py
442 passed             broad sweep (gate5 / replica / fullevent / cstat / hash_bindings)
ALL BINDINGS INTACT    differential pin test: local mismatch set did not grow
pre-commit: 9 checks passed
```

**A three-stream regression was caught and fixed properly.** The driver's own test builds `args` by
hand, so `args.cstat_product` did not exist. Resolved by `getattr(..., CSTAT_THREE_STREAM)` — and the
direction matters: **absence means three-stream, so a family is never data-only by omission.**

**Two failures in the broad sweep, neither mine, both attributed rather than waved past:**
`test_pet_fullevent_nominal_launcher.py` **passes in isolation** (39/39) and fails only under a broad
`-k` selection where an earlier test has already imported TF into the shared process — an
order-dependent assertion, latent and not introduced here. And
`FINDING-20260817-the-floor-shape-noise-is-heterogeneous.md` is **unindexed** in `FINDINGS.md`; it is
another lane's, so it is surfaced to its author rather than indexed with my summary of someone
else's finding.

---

## What is NOT done

- **The reconciler's verdict path.** Scheduled during the run per the mediator's ruling, with one
  amendment: the distinctness check is the **only family-level** one, so it must exist **before
  anyone reads a number off the family** — fifty per-artifact gates cannot see "all fifty are
  identical" by construction. Profile is 2-of-4 distinctness plus 2-of-3 replay; its own path, never
  a relaxation.
- **No run.** Submission still gates on the predeclaration and a second key's review, neither mine.
- **The lazy-TF finding**, filed alongside: the loader has no module-level TF import but imports it
  lazily, so on a login node without the module loaded it dies after **~2 minutes of I/O** rather
  than immediately. Anyone writing a quick diagnostic against it will pay that.

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

---

## AMENDMENT 1 — the target family, the launchers, and a NINTH stop before submission

**Built to lane C's `BEN-420`:** `build_fullevent_replica_target.py` gains `--cstat-product`, T1–T5,
**and both branched checks** — the `:215-222` three-stream replay *and* the `:205-213`
normalized-target-sum closure, which C found and the dispatch had missed. Three new launchers, ADD
never rename: `sbatch_gate5_data_only_{target,train}_array.sh` and
`submit_gate5_data_only_n50.sh`, each carrying the **never-unify** prohibition in its header.

**The target stage's mechanism is a driver-side substitution, and it is not the training stage's.**
`bootstrap_seed=None` is right for training and *wrong* here: the target genuinely needs the data
factor applied, so `None` would remove the variation this stage exists to produce. "Data Poisson,
background unity" is unreachable through the loader's single switch, so the driver substitutes the
module-global the loader calls — the same idiom this file already uses for the DataLoader itself —
and **restores it before the verification block**, so the replay sees the canonical function rather
than comparing a patched draw against itself. That makes T2/T5 true **by construction**, and they are
still asserted, because a mechanism correct-by-construction and unchecked is one refactor from being
neither.

**The predicate module is pinned at submit alongside the drivers.** T1–T5 and L2 live in one module,
so a change there changes what *"data-only"* means; a family built against a different predicate set
is a different product wearing the same name.

### NINTH STOP: the submit controller cannot run against the main scratch tree

`submit_gate5_data_only_n50.sh` requires `[[ -z "$(git status --porcelain)" ]]` — inherited from the
three-stream controller and correct. Measured on the cluster this turn: **725 dirty paths**, so it
would die `code worktree is dirty`. That is not a defect in the controller; **`GATE5_CODE_ROOT` was
never the main tree.** The established convention is a *frozen deployment checkout named for its sha*
— measured, ten of them exist: `gate5-extraction-frozen-7dc8c34`,
`gate5-target-validator-frozen-70be58a`, `gate5-training-recon-56857233`, and others.

**So submission needs a fresh frozen checkout at this HEAD, and creating one is a deployment decision
rather than an implementation one:** it becomes the provenance anchor recorded in all 100 receipts of
the run, and `OI-64C` exists precisely because *"committed is not deployed"* was unchecked — with its
parity checker unwired, because both its call sites are pinned (`BEN-385`).

**Not created, not submitted.** Two things are needed and neither is mine to decide: who creates the
deployment checkout and under what name, and whether the parity check runs against it before the
arrays go in.

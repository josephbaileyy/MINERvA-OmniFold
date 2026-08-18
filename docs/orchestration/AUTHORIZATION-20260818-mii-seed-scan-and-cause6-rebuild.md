# AUTHORIZATION — `M(ii)` seed scan, and the cause-6 rebuild

**Given by Joseph directly to the mediator session, 2026-08-18. Committed BEFORE any submission,
per this campaign's convention that a relayed grant lands in the repo before it is acted on.**

## What was asked and what was answered

**Asked:** confirmation of the `M(ii)` seed scan at **~39.223 A100-hours + ~55.337 CPU task-hours**,
with the standing caveat that CPU is the tighter allocation — `iris` measured this session:

| project | charged | allocated | used |
|---|---|---|---|
| `m3246` (CPU) | 15986.4 | 20000.0 | **79.9%**, ~4014 node-h left |
| `m3246_g` (GPU) | 115805.8 | 180000.0 | 64.3%, ~64194 left |

**Answered, verbatim:** *"Yes I confirm any hours (both CPU and GPU) needed. Do the steps then launch it"*,
following *"once its implemented, will you launch it?"*

## Scope, stated because the phrase was broad

**COVERED, unambiguously:** the `M(ii)` seed scan — the run this exchange was about.

**TREATED AS COVERED, and flagged here rather than assumed silently: the cause-6 rebuild.** The
mediator had said it would return for that separately; *"any hours needed"* is broader than the
question asked. **It is recorded as covered so that the reading is visible and correctable, not so
that it is settled.** Cause 6 has a non-funding prerequisite regardless — a corrected upstream input —
so the authorization is not its only blocker.

**NOT COVERED:** anything else. This is not a standing grant.

## Preconditions that funding does not discharge

**The specification is settled and the code is not.** `BEN-461` ruled `(ii)` OFFSET, lane A seconded,
and `(B)` was amended — *a variation that preserves each leg's seed-sharing relationships, a common
OFFSET from each leg's own baseline, not a common value.*

1. **NO DRIVER EXISTS.** No launcher drives all four legs. The nearest reaches three of four
   (`uq_fps/corrected/run_fps_uq_packed.sh`), and `sweep_bank_5d.py` is in none of them.
2. **THE FORBIDDEN-OFFSET ASSERTION MUST SHIP WITH IT, IN ITS PAIRWISE FORM.** `k ∉ {±958}` is
   **under-inclusive** — collisions are pairwise on the grid (`k − k' == b_i − b_j`), so a grid holding
   `100` and `1058` passes that check and aliases. The assertion is over PAIRS, and its failure message
   must describe **aliasing between two scan members**, not destruction of the co-variation structure.
3. **THE CONSTRAINT'S PREMISE IS UNMEASURED AND MUST BE CITED AS SUCH.** It is necessary only if a
   shared seed across different legs produces correlated noise, which `BEN-461` itself records as
   `CONSIDERED-AND-DECLINED` and unmeasured. Impose it on conservatism; do not assert it as a
   structural fact.
4. **A FLAG IS CAPABILITY, NOT INTEGRATION — AND A LAUNCHER DIFF IS NOT A LAUNCHER.** Four modules
   accepting an estimator seed is not one run driving them coherently, and under `(B)` an incoherent
   four-leg run measures nothing.

## What the spend buys, and what it does not

**It buys the magnitude recorded UNRESOLVED. It does not discharge the leg.** Whether the number leaves
the published values standing is a physics-presentation judgement of the same class as the endpoint
census — ***measured is not acceptable***. This authorization funds an operand, not a conclusion.

## Baselines, for the record

Measured by lane B at `3be8c052`. Two coherence groups, mutually independent:

| leg | baseline |
|---|---|
| `sweep_bank_5d.py` (vertical bank, 169 universes) | `42` |
| `bootstrap_nd.py` (`C_stat`, 100 replicas) | `42` |
| `seedscan_split.py` (`C_ML`, 24 splits) | `42` |
| `unified_throw_cov.py` (throws + block units + CV) | `1000` |

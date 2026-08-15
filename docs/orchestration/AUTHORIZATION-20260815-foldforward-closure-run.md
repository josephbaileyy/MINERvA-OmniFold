# AUTHORIZATION — fold-forward instrumented / corrected powered closure

Recorded by the executor lane 2026-08-15, **before submission**, because `BEN-082(v)` requires a
relayed authorization to be committed before it is acted on.

## What Joseph said, verbatim

> Yes the closure run sounds good.

Relayed by the mediator (`personal-orchestrator`) this turn. **That is the whole of the user's text.**

## What it was said in answer to, and who resolved the ambiguity

The mediator put a three-option menu to Joseph, drawn from
`PROPOSAL-20260815-instrumented-and-corrected-foldforward-closure.md`:

| option | arms × draws | GPU-hours |
|---|---|---:|
| recommended | 2 × 3 | 11.7 |
| minimum | 2 × 1 | 3.9 |
| instrument only | 1 × 1 | 2.0 |

**The mediator's interpretation, marked as the mediator's and not as Joseph's:** *"the closure run"*
reads as the recommended option, since instrument-only is a partial rather than "the closure run."
Resolved to **2 arms × 3 draws**.

**Joseph was NOT asked to disambiguate a third time.** The mediator's own words: *"If he meant
instrument-only, that correction lands on me and not on you."*

**So this record does NOT say "Joseph authorized 11.7 GPU-hours."** It says: Joseph authorized *"the
closure run"*, and the mediator resolved which run that is. Anyone reading this later who needs the
distinction has it here rather than having to reconstruct it.

## What is authorized by this

Six Slurm array tasks of `sbatch_foldforward_instrumented_closure.sh`: tasks 0–2 arm 0 (instrumented,
uncorrected), tasks 3–5 arm 1 (scale-only corrected). One A100 each, `--time=04:00:00`,
`qos=shared`, account `m3246`.

## What is NOT authorized by this

- **No promotion, no engine edit, no threshold change.** `omnifold.py` stays at `3a2022b0…`.
- **No repinning of any receipt-bound launcher.** The closure driver stays byte-identical at
  `a45fae7c…`; both files this run adds are NEW.
- **Nothing about quotability.** `VL100`'s quotability is a determination for the PET lane and Joseph,
  and no run produces it.
- **Not the corrected NOMINAL run.** See the limitation in the predeclaration: this closure's own
  fold-forward is ≈ 1, so it does not exercise the nominal extraction's ~34% deficit, and this run
  cannot settle that deficit's magnitude.

## Chain of custody

| step | where |
|---|---|
| the ask, costed | `PROPOSAL-20260815-instrumented-and-corrected-foldforward-closure.md` |
| the reading, fixed in advance | `PREDECLARATION-20260815-foldforward-instrumented-closure.md` |
| why a run is the only instrument | `FINDING-20260815-the-quarantine-measured-a-different-run.md` §4 |
| the item it closes | `OI-71` (G4) and `OI-125` |
| the clause that made a fresh authorization necessary | `p3f-pet-gate4-nominal-promotion-56563761.json` → `scope_PROMOTED_IS_NOT_PROCEED.NOT_authorized` lists *"any recovery run"* |

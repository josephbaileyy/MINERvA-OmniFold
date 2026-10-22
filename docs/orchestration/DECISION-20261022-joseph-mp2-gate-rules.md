# DECISION 2026-10-22 — Joseph: size-controlled MP-2 closure gates; keep the 3000-tree cap

**Recorded by** the paper-tighten lane, as director. It was recorded at 09:03 PDT, before any V2 or V3
statistic had been read: the files are sealed under addendum 13.

**What led to it.** Binding addendum 13 (`state/measurement-paper/BINDING-PHASE1-ADDENDUM-13.md`) found two
problems with the frozen MP-2 S2 gates and put both to Joseph.

1. **The gate thresholds.** Under exact closure they fail often by chance alone:
   - V3, χ²/ndf ≤ 1.5 on four distributions: about 45% per replica;
   - V2, "no J cell beyond 3σ" over 109 cells: about 26% per replica.
2. **The tree cap.** The probe models reached the frozen n_estimators = 3000 without early stopping.

The director asked both as multiple-choice questions. Joseph's answers are below; the option text is the director's.

> Gate rules: "Size-controlled (Recommended)" — Replace them now, before any gate output: a p-value per distribution
> with a Holm correction across the family for V3, and a maximum-pull bar corrected for 109 cells for V2.
>
> Tree cap: "Keep 3000 (Recommended)"

sha256 of the two answer lines plus a final newline begins `3432fa9cc8b3532b`.

## What is decided

1. **The MP-2 S2 gates change to size-controlled rules** before any V2 or V3 output is read:
   - for V3, a p-value per distribution, with Holm across the family;
   - for V2, a maximum-pull bar corrected for the 109 cells.

   The exact rules are written in binding addendum 14, which must be committed before any V2 or V3 statistic is
   released. This is a contract change, made before the outcome is known.
2. **The production models keep the frozen n_estimators = 3000**, with the addendum-13 checkpoints and the
   descriptive 10,000-tree V1 when the cap binds.

## Not changed

- The models and their training. Anything else in the frozen contract. No claim. No outward act.

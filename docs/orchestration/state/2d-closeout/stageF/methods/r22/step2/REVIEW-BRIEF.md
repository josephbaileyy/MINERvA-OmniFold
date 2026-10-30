# r22 Step 2: the two-direction review brief

You are an independent, read-only reviewer of a register rewrite of a physics analysis note. Writers reworded the
note's LaTeX sources to read more like a long PRD or JINST paper. Their rules are in `step2/WRITER-BRIEF.md`; read it
first. Your job is to find any place where the rewrite changed what the note says.

Paths:
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`:
  the worktree with the edits. The base is commit `9d3054f9`.
- `R=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/4834bf2d-a370-41b8-ae11-7b9d48874031/scratchpad/r22`.
- See each change with `git -C $WT diff 9d3054f9 -- docs/analysis-note/<file>`. Each writer's fact ledger is
  `$R/step2/ledger-<piece>.md`.

## The two directions

1. **Old to new.** Every fact, number, qualifier, limitation and disclosure of the base text still prints in the note.
   That means in the same file, or at the home the ledger names: another note file (`N:`), the records document (`R:`),
   or a repository ledger file (`L:`, implementation detail only).
   - A qualifier must still be attached to the claim it qualifies. Examples: "has not been tested", "not validated",
     "descriptive", "for reporting only", "does not cover", "conditionally on".
  <!-- absence-ok: quotes printed qualifiers and limitations of the note as examples or as gaps; not a claim that a result is absent -->
   - Flag any fact that is lost, weakened, moved away from what it qualifies, or now ambiguous.
2. **New to old.** The new text adds no fact, number, definition, cause, claim or citation that the base text, or a
   source the ledger names, does not support. Flag every addition. For a definition or gloss, say whether the base note
   or a named repository source states it. A gloss written from general knowledge counts as an addition.

## Checked by machine; do not re-check

- The fact-ledger probes: `step2/check_ledger.py` reports 0 failures.
- The gate-bound phrases, labels, macros, the values files and `main_note.tex`.
- The out-of-scope sentences, which are checked separately.

The machine checks only that probe strings print. Your judgement is about meaning.

## Specific points to rule on

The writers or the integrator raised these, so check each one:
- B02: the PPFX expansion "Package to Predict the FluX" was written from memory, with no source in the repository.
  Recommend reverting it to the acronym with its citation.
- B02: "a combined flux and central-value (CV) weight" (MAT's FluxAndCVReweighter).
- B03: the glosses for EtaNCEL ("the neutral-current elastic axial parameter") and Rvp1pi/Rvn1pi ("nonresonant CC
  single-pion production on protons/neutrons") came from general GENIE usage. Also check "205 reported cells" for
  C_model.
- B04: the new band names, "completeness-divided band" and "undivided band". Are they accurate (KI-84, VL162, VL170)?
  Are they consistent with the other files, which still say "first-built"?
- B05: 0.66 and 1.42 are now labelled as χ²/ndf.
- B06: "IBU has no practical analog for unfolding many observables simultaneously". It must not imply that binned
  multi-dimensional measurements are impractical.
- B07:
  - the reading of "spline-normalized" (does it fit GENIE+MEC?);
  - "null spread" became "null standard deviation";
  - "The article distinguishes" became "The analysis distinguishes". Did "the article" mean the companion PRD paper?
  - one sentence on the localization relative to MINERvA Tune v1 was cut.
- B08:
  - the definition of "identified" ("constrained well by the binned response"), when the record defines only the
    opposite;
  - the "edge-safe jitter" definition, taken from code.
- B09: the bands are glossed as "which reweight simulated events", and the "noise gate" is equated with the
  "statistical gate".
- B10:
  - "about 0.07" was replaced by the measured 0.068;
  - a superseded "~0.05" now prints;
  - the `\jtRecompRows` count was moved to the records;
  - "0.72" is now named "the shape power at 0.005 against the first alternative".
- B11: "absolute" was added to "median deviation", citing VALIDATION_LEDGER.md:1623–1638.
- B13: the gloss for "battery" ("the set of unfolds run on that date").
- B15:
  - the second subtraction method is now named "negative-weight injection";
  - release item 10 now names "the four measurements";
  - worked-example step 6 now names "the estimator-seed sensitivity".
  - In app_release.tex every claim about the package must stay true of the package.

## Output

Write `$R/step2/review-<your range>.md`. List each finding as:
- **ID:** the file and the sentence, quoted;
- **direction:** LOST, WEAKENED, MOVED-AWAY, AMBIGUOUS or ADDED;
- **base text and new text**, quoted;
- **why;**
- **fix:** restore, reword or remove.

Add a final section that rules on each specific point above that falls in your range: OK, or a fix. Read-only:
write only that file, run no command that writes, and make no model, CLI or network call. Report back the count of
findings by direction, and the three most serious, in under 200 words.

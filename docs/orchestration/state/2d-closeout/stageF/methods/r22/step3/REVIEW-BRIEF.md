# r22 Step 3: the two-direction review brief

You are an independent, read-only reviewer of a register rewrite of a physics analysis note. In this round, writers
changed sentences that a protection had held: qualifiers (B1), run history (B2) and honesty-required disclosures (C1,
C2, C9). An independent reviewer allowed each change, usually in a narrowed form. Find any place where the rewrite
changed what the note says, or went beyond the allowed form.

**Read first:**
- `step3/WRITER-BRIEF.md`;
- `step2/WRITER-BRIEF.md`, whose rules it extends;
- for each gap, `step3/briefs/<piece>.md`. Each lists the CHANGE TO MAKE, the refused original request and the two
  classifications that had held it.

**Paths:**
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`
  is the worktree with the edits. The base is commit `14a0415f`.
- `D=$WT/docs/orchestration/state/2d-closeout/stageF/methods/r22`.
- See each change with `git -C $WT diff 14a0415f -- docs/analysis-note/<file>`. Each writer's ledger is
  `$D/step3/ledger-<piece>.md`. B01's abstract proposal is `$D/step3/abstract-pairs.md`.

## The two directions

1. **Old to new.** Every fact, number, qualifier, limitation and disclosure of the base text still prints in the note,
   at the same strength. It may be in the same file, or at the home the ledger names: `N:` another note file, `R:` the
   records, or `L:` a repository file.
   - A qualifier must stay attached to the claim it qualifies.
   - Flag any fact that is lost, weakened, moved away from what it qualifies, or now ambiguous.
   - **Flag any change that goes beyond the narrowed form,** even partly toward the refused original request.
2. **New to old.** The new text adds no fact, number, definition, cause, claim, citation or attribution that the base
   text, or a source the ledger names, does not support. Flag every addition.

## Checked by machine; do not re-check

- The ledger probes: `step3/check_ledger.py` reports 0 failures over 65 rows and 187 probes.
- The gate-bound phrases, labels, macros, the values files and `main_note.tex`.
- The 29 held sentences, which print exactly.

The machine checks only that the probe strings print. Your judgement is about meaning.

## Specific points to rule on

- **B02-g-01:** "no seed option; no seed passed" left the note for a ledger row (`uncertainty-preparation-20261008/a/pairings.tsv`, P01). An earlier director ruling (round n2) had kept that reason in the note. Does the narrowed form allow the move, and is the ledger home adequate?
- **B05-g-08** cut the caption remark "the panels have no printed titles", with the plotting code as its home. **B07-g-03** cut a storage fact, with the event-loop source and a P5B record as its homes. Is code an acceptable home for a presentation or storage fact?
- **B03-g-10** adds a table for six values. Check that every value and its label match the base prose exactly.
- **B09-g-09** moves five χ² values from prose into a new column of `tab:fived16-gen`. Check the column's values, ndf and covariance label against the base sentence.
- **B12-g-04** cuts rows of the label table, with `R:`/`L:` homes. Check each home holds what the cut row said.
- **B14-g-02** moved a person's credit ("private communication") from the body into a new footnote, "We thank Kevin McFarland for suggesting this distinction and stress". Is this the narrowed form, and does it add an acknowledgment that the note's Acknowledgments (Joseph's protected text) does not hold?
- **B15-g-08** "should not be checked" for "Do not check"; **B15-g-06** "(fixed)" for the check marks. In `app_release.tex`, every claim about the package must stay true of the package.
- **B01-g-03** keeps "has not been established" as a clause. **B01-g-07** is the abstract pair: check it as a proposal (every fact and qualifier kept, as the narrowed form asks).
- **B04-g-01**'s new "Two bands were scored: …" sentence. Is the rebuild fact still printed as strongly?
- **B13-g-06:** "which has not been shown" is now also said in the appendix. Is it a restatement or a new claim?

## Output

Write `$D/step3/review-<your range>.md`. List each finding as:
- **ID:** the file and the sentence, quoted;
- **direction:** LOST, WEAKENED, MOVED-AWAY, AMBIGUOUS, ADDED or BEYOND-NARROWED;
- **base text and new text,** quoted;
- **why;**
- **fix:** restore, reword or remove.

Add a final section that rules on each specific point above that falls in your range: OK, or a fix.

**Rules:**
- Read-only: write only that file.
- Run no command that writes, and make no model, CLI or network call.
- Report back in under 200 words: the count of findings by direction, and the three most serious.

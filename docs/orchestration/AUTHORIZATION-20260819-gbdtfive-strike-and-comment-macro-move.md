# AUTHORIZATION 2026-08-19 — strike the `\gbdtFive*` block and move the comment macros to the preamble

**Joseph, verbatim and complete, given directly in his own session (not relayed):**

> strike gbdtFive and move the three macros to the preamble

Given after he asked why each was proposed and received the grounds below. This receipt is
committed and pushed before the publication text is changed, as this repository requires for
`docs/analysis-note/` work, even though neither edit is outward-facing.

## Authorized scope

1. **Strike the four `\gbdtFive*` consumption sites** in `sec_systematics.tex` (`:163`, `:165`,
   `:166`, `:168` — `\gbdtFiveBlockMedian` 13.36%, `\gbdtFiveAdoptTrace` 5.81e-38,
   `\gbdtFiveCVTrace` 6.24e-38, `\gbdtFiveMeanShift` 1.65e-38) using the existing `\dead{}` macro,
   plus whatever surrounding prose must change for the struck sentences to read coherently.
2. **Move the three reviewer-comment macro definitions** `\bpn`, `\jrb`, `\gk` from
   `main_note.tex:17-19` into the shared `preamble.tex`, unchanged in behaviour.

## The grounds, recorded so the edit is not re-litigated

**The strike.** `PROCEDURE-gbdtFive-macro-update.md` records the four values as quarantined on TWO
grounds — the 2026-07-12 class and J28 — and states "Nothing here supplies a replacement magnitude."
Three things make striking the right remedy rather than replacing or leaving them:
- They print as current, and the page argues for that reading: J28 is named eight lines below at
  `:175` as a correction the passage has accounted for, so a reader has positive reason to believe
  the values above are post-J28. They are pre-J28, and J28 is one of the two grounds.
- A naive replacement produces a FALSE SENTENCE, measured in the procedure: the J28 pair
  `5.2600e-38`/`5.6609e-38` is footed on the **non**-background-aware sweep while the values it would
  replace are **background-aware**, because `sbatch_j28_adopt_5d.sh` never passes `--combined`.
  "Writing the J28 pair under the sentence at `:162` would make that sentence false."
- Striking needs no adopted magnitude, which is exactly the authorization nobody has.
`sec_systematics.tex` is inputted by `main_note` ONLY (measured: 1 in `main_note.tex`, 0 in
`main_paper.tex`, 0 in `main_primer.tex`), so `\dead{}` there CANNOT reach an outward-facing driver.
That matters because `check_dead_containment.py:331-335` FAILS any non-note driver reaching a
`\dead{}` use — "struck retracted values would render in an outward-facing PDF" — and `:6-7` records
that strike-not-erase is right for an internal audit trail and wrong for anything outward-facing.
So the note build is the one place striking is both permitted and correct.

**The macro move.** `\bpn`, `\jrb` and `\gk` are defined only in `main_note.tex` and used 16 times
across the note sections, 0 times in `paper_body.tex` or `primer_body.tex`. Neither external wrapper
defines them. The first time a commented paragraph is distilled into the paper — the routine way the
paper is written — the paper build fails with `Undefined control sequence`. This is a latent
build-breaker, not a defect in current output, and the fix is three lines.

## Boundaries

This authorization does **not**: adopt or supply any replacement magnitude for the struck values;
change any other value, caption, figure or cross-reference; touch `paper_body.tex` or
`primer_body.tex`; alter `check_dead_containment.py`, `build_all.sh` or `values.tex`; or authorize
compute, deletion, repinning, pinned-file changes, embargo lifting, the 41.44 GB intermediate, a
`C_stat`/P5A pairing, or an `OI-126` resolution.

The thirteen visible reviewer comments themselves are NOT in scope — moving the definitions does not
remove a single `\gk{}` call, and two sites where a comment and its own "[JRB: Fixed!]" answer were
both left in remain as they are. Removing them is a separate editorial decision.

Pre-push gate as before: `build_all.sh`, which now forces the rebuild and proves the PDFs postdate a
marker stamped before the builds, then the containment stage with both halves.

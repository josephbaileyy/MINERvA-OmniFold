# DECISION 2026-11-08 (latest) — Joseph: the note's abstract and title are unfrozen and the note is reframed to the methods study, with the current version archived first; REF-G1's estimator dependence is a stated limitation

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **Joseph asked for referee rounds on the paper, its Supplemental Material and the companion note**, so that all
  three are ready together. The note lane's round-1 currency audit (`draft/note-round1-20261108`, head `722517d5`)
  found, as N1, that the note's abstract, executive summary, `sec_fived16` and four appendix sites still frame it as a
  measurement, against `DECISION-20261106-joseph-methods-study-and-archive.md` item 1. The note's abstract and title
  were frozen. As N2, it found that REF-G1's estimator dependence appears nowhere in the note, and
  `OUTCOME-20261106-ref-g1-r1-differ.md` says no text is drafted before Joseph decides how it enters.
- The director put both through AskUserQuestion:
  1. How the note is framed before its referee reads. The options were "Reframe to match paper (Recommended)",
     "Keep measurement framing" and "Minimal: framing paragraph".
  2. Whether REF-G1's IBU–OmniFold difference (R1 `differ`, T = 194.4 against a calibrated bar of 28.12) enters as a
     stated limitation (recommended), an uncertainty block, or both.

## Joseph's answers, verbatim

1. > Yes I think we shouuld relax the frozen ness of the abstract and title, remember to archive this version though in case we are ever able to move back to a methods paper

   sha256 begins `6057c97758c96816`.
2. > Stated limitation (Recommended)

   sha256 begins `d9151adf08cb30cc`.

## What is decided

1. **The note's abstract and title are no longer frozen.** The note is reframed as the technical record of the
   methods-and-benchmark study, consistent with the paper. The 16-cell result is presented as the paper presents it.
2. **The current note is archived first,** before any reframing edit lands, as an in-repository package like
   `archive-measurement-framed-20261106/` (#865 series): the note PDF built from main at the archive commit, a manifest of
   every source blob, the build log and the rebuild commands.
   - **The director's reading of "move back to a methods paper":** the version being archived is the
     measurement-framed note, so the archive is what a return to the **measurement** framing would start from. Joseph
     corrects this if he meant otherwise.
3. **REF-G1's estimator dependence is a stated limitation.** It is reported as a finding of the benchmark (the binned
   IBU and OmniFold 16-cell results differ beyond the calibrated bar), in R1's licensed terms. No covariance block is
   added, and the reported 16-cell numbers do not change. Its sentences go through the paper and note lanes, the
   referee reads and Joseph.
4. **Unchanged:** every wording choice goes through a PRD-referee read before Joseph; no paper or note text merges
   without his wording approval; nothing is posted, submitted, deposited or tagged.

Nothing is submitted, deposited or tagged.

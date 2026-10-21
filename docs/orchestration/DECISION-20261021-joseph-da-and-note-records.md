# DECISION 2026-10-21 (third) — Joseph: adopt the shorter Data availability; the published note is not a records ledger

**Recorded by** the paper-tighten lane, as director (Stage F).

**What led to it.** The director put two decisions to Joseph.

1. **The Data availability paragraph** (`main_paper.tex`).
   - It is Joseph's protected text.
   - Its release bookkeeping was quoted by GPT-6.1-sol in 3 of 3 rubric runs on round r13.
   - The r13 writer drafted a shorter version, about 140 words against about 262
     (`state/2d-closeout/stageF/methods/r13/DA-proposal.md`). The independent review found every one of the 23 facts a
     destination.
   - The director flagged two points:
     - adopting the draft reverses plain-language pass 2 ruling P6, which kept the package's Fig. 1 limitation in the
       paper;
     - one proposed note sentence rests only on the package's own README.
2. **Apps. G–J of the analysis note** (provenance, release, codebase, history).
   - The note's register baseline scores them worst (`rater-calibration/NOTE-BASELINE.md`).
   - They are records by design.
   - The options: keep them as they are, shorten them, or move them to the repository with a pointer. This was already
     pending as "App. J placement".

Joseph's answer, verbatim:

> Decision 1. I think its a good idea to adopt. Decision 2. I agree. I think there should be an internal ledger for these
> records (or maybe the archival system we have now is already good enough), but the analysis note that we publish as
> supplementary material should not be that.

sha256 of the text plus a final newline begins `270eed1dca825f2a`.

## What is decided

1. **The shorter Data availability paragraph is adopted.**
   - **The text.** It is the r13 draft with review fix D-1, the unambiguous "The other quoted numbers, except the
     multiplier scan, and the event-level processing require …".
   - **What it reverses.** It reverses P6: the package's Fig. 1 limitation now prints in the note (`app_release.tex`,
     "RC7 was assembled before …").
   - **The note addition, under review fix D-2.** One sentence is added to the note's release status paragraph, so that
     no fact leaves both documents: "RC7's own verifier, run on the packaged files in an empty directory, reproduces
     every value recorded in the package and every figure number that it checks."
     - It is worded as the package's own verifier, cited to its README.
     - It is not worded as, or placed beside, the independent replay, which was of RC1.
   - **Unchanged:** the `\pubhold` text is byte-identical. "Candidate" and "not yet deposited" stay.
2. **The analysis note posted as supplementary material is not a records ledger.**
   - **The records leave the note's published build:** provenance tags, struck and superseded values, withdrawn results,
     commit and record chronology. They go to an internal ledger in the repository, which stays maintained and checked.
   - **The director's reading,** stated for Joseph to confirm or override:
     - App. G (provenance) and App. J (superseded values and withdrawn results) are records, and leave the note.
     - App. H (the release package) and App. I (the codebase) hold reader-facing material: what the package reproduces,
       and how the code is organized. That material stays in the note, rewritten in its register. The record-keeping
       parts move with G and J. Those are the fixed-identity tables, the audits, and implementation refusals and
       markers.
     - Body pointers into App. G tags are replaced by a citation of the repository record. App. G is not cited.
   - **Joseph's open question**, whether the existing archival system is already good enough: it is to be answered from
     an inventory before anything moves. The inventory will establish:
     - what Apps. G–J hold that the repository records do not;
     - which build gates read them, including the struck-value containment check and the body-pointer lint;
     - what the paper and the primer cite in them.

     The internal ledger is then either the existing records, or a separately built internal document. Either way the
     gates keep running.

## Not changed

- Claims and numbers. The ledger move changes where records live, not what they say.
- The `\pubhold` text, the funding text and the release decision, which are Joseph's.
- No outward act. Nothing is submitted, deposited or tagged.

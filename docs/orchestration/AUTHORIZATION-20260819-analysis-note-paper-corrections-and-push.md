# AUTHORIZATION 2026-08-19 — correct and push the external paper build

**Joseph, verbatim and complete:**

> `[JOSEPH-VERBATIM]` Approve the paper edits and have it push to the analysis note github

Joseph gave this instruction in the Codex relay conversation after receiving the analysis-note
audit status that the external paper build misattributes the central-value estimator, prints a
PET--GBDT comparison with a disposition opposite to the internal note, and contains a PET-closure
claim whose legacy scope requires owner adjudication. This receipt is committed and pushed before
the publication text is changed, as required for outward-facing `docs/analysis-note/` work.

## Authorized scope

The analysis-note owner may edit the external paper build and any shared analysis-note source needed
to make the verified paper-facing claims internally and scientifically consistent. In particular,
the authorization covers:

1. correcting the central-value estimator attribution and explicitly preserving the verified
   central-value/covariance estimator mismatch where the measurement actually has one;
2. striking, removing, or accurately qualifying the paper's PET--GBDT `9\%` comparison so its
   disposition agrees with the governing record and the note's supported interpretation;
3. resolving the paper's `petClosure` print sites only after the PET/spec owner determines whether
   the value is current or legacy, rather than guessing from an ambiguous block header;
4. correcting verified external-build traceability or caveat defects found by the active
   note-versus-record audit when the authoritative ledger, ruling, determination, or claim state
   fixes the answer; and
5. updating captions, cross-references, or shared prose required for those corrections to render
   coherently.

Before pushing, the owner must run the repository's complete analysis-note build workflow for all
three products (`main_note`, `main_primer`, and `main_paper`) and inspect the resulting logs/PDFs in
proportion to the change. The edit commit(s) may then be pushed to the GitHub remote that owns
`docs/analysis-note/`. In this checkout that subtree is not a nested Git repository; it is tracked by
the root `MINERvA-OmniFold` repository and its configured `origin` remote.

## Boundaries

This authorization does **not**:

- adopt a new central value, covariance, PET result, or uncertainty magnitude;
- pair `C_stat` with P5A or resolve OI-126 by prose;
- license an answer where the audit says `CANNOT-TELL`; the relevant scientific/spec owner must
  adjudicate first;
- authorize compute submission, deletion, repinning, pinned-file changes, embargo lifting, or the
  41.44 GB intermediate's removal; or
- authorize unrelated rewrites elsewhere in the note.

The audit findings and their cited source lines remain the evidence for each edit. This receipt is
authority to correct and push the verified publication-facing defects, not authority to change the
measurement to fit the prose.

# DECISION 2026-10-29 — Joseph: relax "no fact leaves both documents" where the internal ledger keeps the fact

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The r22 gap diagnosis named cuts of implementation detail from the note. That detail is no limitation, disclosure,
  qualifier, number or finding, and it is printed in neither the paper nor the note elsewhere.
- Under guardrail B2, "no fact leaves both documents", each such cut needed Joseph's lift for a named fact
  (`DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md:43`).
- The director had told Joseph that this would come to him as one question: whether B2 applies to pure implementation
  detail.
- B2 was set from Joseph's words of 2026-10-21 (`DECISION-20261021-joseph-register-loop-2.md:22-23`): "I think the
  limitations and after-the-fact disclosures don't need to be in the paper as long as they are mentioned somewhere,
  like in the note or another supplementary material."
- His records ruling of the same day (`DECISION-20261021-joseph-da-and-note-records.md` item 2) moved the note's
  records to an internal ledger in the repository, "which stays maintained and checked".

Joseph's words, verbatim, in his own message:

> yes I think we need to relax the no fact leaves both documents rule since we have the internal ledger

sha256 of the text plus a final newline begins `2f50e4e8d7bf6890`.

## What is decided

1. **B2 is relaxed.** A fact may leave both the paper and the note when the internal ledger keeps it. The ledger is the
   repository's records, with the checks that keep them maintained.
2. **The director's reading of its scope,** stated for Joseph to confirm or override:
   - **Relaxed:** implementation detail and provenance. That covers code paths, file names, receipt and commit
     identifiers, record chronology, tooling and process steps. It applies when the detail bears on no limitation,
     disclosure, qualifier, reported number or finding. Each such cut names the ledger record that keeps the fact, and a
     probe checks that the record holds it.
   - **Not relaxed:** limitations, after-the-fact disclosures, qualifiers, and reported numbers and findings. These still
     appear in at least one published document, the paper or the note. That is Joseph's 2026-10-21 condition ("as long
     as they are mentioned somewhere, like in the note or another supplementary material"), and the question put to him
     was about pure implementation detail.
   - **Unchanged:** the KEEP list (B3), the honesty-required facts (inventory §4) and the truth guardrail ("a qualifier
     stays where omission makes the sentence false"). None of them is B2.
3. **r22's sub-class PROTECTED-B2-DETAIL is reclassified STRUCTURE (cut)** for every gap that names a ledger home. A gap
   with no ledger home stays PROTECTED. The report gives both tallies, before and after this decision.

## Not changed

- Every claim, number and limitation, and the protections other than B2.
- Nothing is submitted, deposited or tagged.

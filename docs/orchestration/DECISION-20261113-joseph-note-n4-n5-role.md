# DECISION 2026-11-13 — Joseph: the note keeps the AUD-N4 and AUD-N5 drafts and the role change; a referee is asked about its development history

**Recorded by** the paper-tighten lane, as director.

## What led to it

On 2026-11-13 Joseph stopped the codex-school2/grok note loop and moved note editing to director-helper-2. helper-2's
read of #952 (`draft/note-round2-20261108`, head `4836da131`) found three commits after the canonical `e339bdf36`, each
"Pending Grok review", which ISSUES.md still lists as held:

1. `4708988a6`, the AUD-N4 draft: `app_release.tex` describes a planned, provisional Zenodo reproduction package (DOI
   pending, deposit before submission, provisional until #981 is re-pinned). ISSUES.md:117-121 says HELD.
2. `1fbade809`, the AUD-N5 draft: "Event-loop outputs are preserved on the analysis's NERSC storage", and a planned
   Zenodo route for public access. ISSUES.md:123-127 says HELD.
3. `4836da131`, the note role: the abstract's "technical record" becomes "companion technical document to the methods
   paper", with an executive-summary paragraph on its release. The n4 outline froze the abstracts and title until
   Joseph's inventory decision.

The director put the three to Joseph as his decisions.

## Joseph's words, verbatim

> we can keep the zenodo package text, we can keep the data preservation for now, and we can accept the abstract change. I think we need to also keep in mind to keep with the historical reporting style of other technical documents. Ours has a lot of history of things we've tried and I'm not sure if its typical. maybe we need a referee suggestion. again, we always have the internal ledger for keeping track of these things

(`a1ca71a4fbe2f195`, the sha256 of the text plus a final newline).

## What is decided

1. **AUD-N4.** The planned-package text of `4708988a6` stays. AUD-N4's hold is lifted for that text. The deposit
   itself still needs Joseph's final go (DECISION-20261112-joseph-consult-d1-d7.md, D6).
2. **AUD-N5.** The preservation text of `1fbade809` stays "for now". Its preservation sentence is a claim, so it needs
   a record citable for it before the note is released.
3. **The note role.** The abstract and executive-summary change of `4836da131` is accepted.
4. **The note's development history.** A referee is asked whether the note's account of what was tried matches the
   reporting style of comparable technical documents. Any history cut from the note stays in the internal ledger. Its
   recommendation comes back to Joseph before any cut.

ISSUES.md's AUD-N4 and AUD-N5 rows, and the rows that repeat their holds, are updated to match.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** these choices, as Joseph's.
- **Not citable for:** event-loop outputs being preserved; any deposit having been made; any note or paper sentence
  beyond the three commits named.

Nothing is submitted, deposited or tagged.

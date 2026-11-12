# DECISION 2026-11-12 — Joseph: the consult's recommendations D1–D7 are adopted, including unlocking B0 and RS1

**Recorded by** the paper-tighten lane, as director.

## What led to it

At Joseph's request, the director asked codex-school (gpt-6.1-sol, high, session `01a1d10d…`) for a recommendation on
each pending decision. The record is
`state/2d-closeout/stageF/methods/secondary-results/consult-decisions-20261112/`. The director gave Joseph the
recommendations with his own view beside each one.

## Joseph's words, verbatim

> i agree with unlocking the protected sentences, as well with everything else, can you give me a prompt to send codex-school2?

(`9a33227b47ddca2a`, the sha256 of the text plus a final newline).

## What is decided

1. **D1, the 2D covariance.** If COV2D-G2R's part (a) is VALID and its held-out constructions validate, the rebuilt
   covariance becomes the reported 2D covariance. The current covariance stays as a documented comparison. The paper
   reports the new coverage counts and intervals under the unchanged rule, whatever they are, and every dependent result
   is updated. If the rebuild fails validation, the failure is investigated, and the current covariance is not
   validated by default. This settles COV2D-G2R-BINDING-1 ruling 5's reserved adoption, conditionally on those
   validations.
   <!-- absence-ok: a conditional ruling about a pending validation, not a claim that a result does not exist -->
2. **D2, GEANT4 neutron and proton.** The paper prints a bounded quantification and presents it as an unresolved
   implementation property, not as a resolution. First, the effect is checked with the full covariance in the coverage
   test's own space. The diagonal approximation and its 0.76 % reproduction are stated if they are used. The primary
   reading's exclusion of the two bands is stated. The mechanism study stays a post-paper follow-up.
3. **D3, the protected passages.** B0 (`DECISION-20261106-joseph-b0-reconciliation-sentence.md`) and RS1's
   mechanism paragraph are **unlocked** for a controlled rewrite. A claim-by-claim comparison against the approved
   text comes first, and Joseph reviews the new wording before it is final. These must be kept:
   - the variance against standard-deviation distinctions and the cell sets;
   - the 20-perturbation summary against the two-perturbation maximum;
   - the limitation to one pseudo-experiment;
   - the statement that the ties' action within refinement was not tested.
   <!-- absence-ok: quotes a scope the RS1 record already states (OUTCOME-20261108-rs1-rounding-mechanism.md) -->
4. **D4, the note.**
   - (a) The background sentence is corrected before submission.
   - (b) The 38 desynced Supplement paragraphs are **not** synchronized back into the note. The note keeps its own
     prose, the divergence is recorded, and any substantive difference is reconciled.
   - (c) S8.6's per-band diagnostics stay in the Supplement. They move only to a destination referees can access.
5. **D5, the style target.** No absolute score is chased. One bounded editorial pass clears the style referee's
   concrete items. Then a human technical read is the stopping criterion: can a reader explain back the covariances,
   the rounding result, the coverage conclusions and the output's illustrative status?
6. **D6, the deposit.** The Zenodo package is deposited **before submission**, after the final adopted results are in,
   and the paper cites that version. It is first tested from a clean environment, with each headline claim mapped to
   what reproduces it. **The deposit itself still needs Joseph's final go on its contents.**
7. **D7, RDX.** The paper does not wait, unless RSN shows a material failure. (RSN's readings of 2026-11-12 show none
   that blocks: G6 survives, WR is immaterial, and SM adds one χ²-only flag.) If RDX lands first and contradicts a
   claim, the claim is revised.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** these choices, as Joseph's.
- **Not citable for:** any result; any paper sentence; the deposit having been made.

Nothing is submitted, deposited or tagged.

## Addendum (2026-11-12): Joseph approves the B0, RS1 and RSN wording

**What was put to him:** the controlled-rewrite drafts.
- **Paper B0 and RS1,** in director-helper-3's `b0rs1/DRAFT-v3.md`.
- **The RSN readings' paper and Supplement text,** in `rsn_draft/DRAFT-v3.md`.
- **Supplement S4.4 RS1,** revision 4, by journal-editor.

**How they were checked:** each draft had a claim table against its records. A codex-school referee read the drafts
(`secondary-results/consult-b0rs1rsn/`, session `01a1d14c`), its edits were applied, and a meaning read checked each
change against its record.

The director flagged one change in particular: the correction to RS1's "float64 inputs and a permutation … do not
reduce the spread". The record reads K3 as bitwise equality of the unperturbed bases, and K4 as a permutation shift of
about 10⁻¹⁰ of the spread.

**Joseph's words, verbatim:**

> i approve the draft

(`54269e43a17cb41d`, the sha256 of the text plus a final newline; corrected 2026-11-12 from a value the director wrote before computing it).

**Decided:**
1. The drafts are applied as approved, through the usual gate.
2. check_restyle's B0 and RS1 spans and check_round's three B0 LITERAL_KEYS rows are removed in the same commit,
   citing D3 and this addendum.
3. **The paper's smoothing sentence:** "region cells" is defined only in the Supplement. It may be worded "the
   neighbouring cells within two fine bins on every axis", with S5 keeping the definition, if a meaning read confirms
   the meaning is identical. Otherwise it stays as drafted.

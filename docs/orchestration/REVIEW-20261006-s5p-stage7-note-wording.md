# s5p (`OI-193`): independent review of the Stage-7 note and primer wording (2026-10-06)

**CITABLE FOR:** the independent wording review of the s5p Stage-7 text in the analysis note and primer (branch
`docs/s5p-stage7-20261006`), its findings, their dispositions and the final verdict. **NOT CITABLE FOR:** any physics
result; the governing records are `RECORD-20261005-s5p-joint-5d-inference-result.md`,
`RECORD-20261006-s5p-lost-seed-recovery-resolution.md` and `DECISION-20261005-…` §5.

**Reviewer:** a fresh read-only agent in an isolated worktree, commissioned by the campaign session. It had no
authorship of the text and checked every statement against the records and the evaluation outputs.

## Round 1: commit `34d69c05`, verdict APPROVE WITH CHANGES

- **Builds:** all three PDFs built with rc 0 and no undefined references.
- **Numbers:** every number matched `joint-evaluate.json` (`b9604502…`) and `robust-labels.json` (`206655f9…`).
- **Forbidden phrasings:** none of CHECKLIST-20261001 §4's.

| # | severity | finding | disposition at `6927c3ab` |
|---|---|---|---|
| 1 | blocking | disclosure 5 (the scope of the independent checks) missing; the recompute and recovery cross-check conflated | scope list added; 1379 rows named; provenance scoped |
| 2 | blocking | the margin not disclosed (only in a comment) | 4.6 T units (T_obs 868.6) and 49.8 stated |
| 3 | should-fix | disclosures 2 and 4 incomplete ("reproduced" for never-started draws; nulls and B = 1200 unnamed) | fixed |
| 4 | should-fix | "normalization" misdescribes the total test (rate and shape) | fixed in note, exec summary, primer |
| 5 | should-fix | condition paraphrases weakened (2, 4, 5, 6; minor 1, 3) | faithful paraphrases |
| 6 | should-fix | "holds the familywise rate" asserts unverified validity | "the decisions use Holm's procedure … at familywise level 0.05" |
| 7 | should-fix | caption hid completed vs submitted B | caption states 1400/1800 submitted |
| 8 | should-fix | power for one null only | both nulls; frozen vs complete sets |
| 9 | should-fix | exec-summary overgeneralization and missing report-only/conditions | revised |
| 10 | should-fix | primer overclaims | the reviewer's replacement text |
| 11 | should-fix | summary wording; a citation to a not-yet-existing file | wording fixed; citation fixed in round 2 |
| 12 | should-fix | provenance pinned to a moving branch | pinned to `466b427b` and `00009056`; date 2026-10-06 |
| 13 | note | minor wording (J cells, unfolding description, frozen-set power) | fixed |
| 14 | note | LaTeX conventions (`\pPar`, units); paper body unchanged | fixed; paper body unchanged by design (the publication lane owns it) |

## Round 2: delta `34d69c05..6927c3ab`, verdict APPROVE WITH CHANGES

- **Status:** findings 1–10, 12 and 13 resolved, and the two deliberate departures accepted. The reviewer
  re-measured the MEC margin as 4.62 (T_obs 868.585, largest recovered T 863.965) and checked the power figures and
  the 0.72.
- **Finding 11:** a comment-only citation to an unlanded file.
- **New notes:**
  - A: the comments cited this review before it was a committed record.
  - B: the primer's "with at most a 5% chance overall of wrongly rejecting a true one" reads as a validity guarantee
    (the reviewer's own round-1 text).
- **Disposition at the following commit:**
  - 11: the clause is removed; the comment cites RECORD-20261005 §7 and CHECKLIST §4.
  - A: the comments cite this record.
  - B: the reviewer's suggested wording, "rejected at a combined 5% error level, as the test was designed".

**Final:** all findings are resolved. The text is approved for merge.

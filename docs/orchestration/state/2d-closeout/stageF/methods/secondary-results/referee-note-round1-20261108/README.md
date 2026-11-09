# The companion note's first referee round, 2026-11-08

**Asked for by** Joseph: referee rounds on the paper, its Supplemental Material and the companion note, so that all three
are ready together. The note is reframed as the technical record of the methods-and-benchmark study under
`DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` (#947).

**What was read.** `draft/note-round1-20261108` at `b1da7ba8372348d9600d043eb381f676db25e1df` (draft PR #946, CI green).
It is unmerged, and no wording is approved. The rater copy `note-r1.blind.txt` (sha256 `55128d32f97a2937…`, 69,536
words, 139 pp) was built by the note lane's `make_note_rater_copy.sh` and checked complete: 37/37 figure captions, 35/35
table captions, appendices A–H, the last body section and the last line before the references. The title block,
acknowledgments and reference list are removed, and the repository URL is masked.

**Procedure.** As in round 4, with the note's own prompt:
- the prompt is `referee-prompt-note.txt` (sha256 `fe97c97613a40dd6…`), approved by the director before any read;
- Sonnet as two read-only subagents, each allowed to Read only the prompt and the rater copy;
- Gemini via agy (`gemini-3.8-flash-high`, `--sandbox`), run from an empty directory that was still empty afterwards,
  each input prefixed with `gemini-preamble.txt`. Both runs exited 0 with empty stderr.

## Scores ("readiness to post as is", 1–10)

| read | score | recommendation |
|---|---|---|
| Sonnet 1 | 4 | major revision |
| Sonnet 2 | 4 | major revision |
| Gemini 1 | 3 | not ready to post |
| Gemini 2 | 2 | not ready to post, **but its input was cut short** (below) |

**Gemini 2 read only part of the note.** It reports the text "ends abruptly mid-sentence in §9.4 (`Median absolute
residual (`)". In the rater copy that string is the header of a table at line 5,948 of 12,536, after 31,717 of the
69,536 words; the copy continues to the end. The cut is on the reader's side. Its completeness findings that rest on
the missing half (§§9.5–13, the appendices) are void; its other findings stand as written. Gemini 1 and both Sonnet
reads cite sections past §9.4.

## What the reads agree on

These are the referees' findings, not verified facts; each is to be checked against the records before any edit.
- **Contradictions inside the note** (both Sonnet reads): Tune v1 in the quasielastic–Δ dip (the executive summary
  against §7.8's data/Tune v1 ≈ 1.01); the Tune v1 normalization deficit quoted four ways; "at least fifteen-fold"
  against 3.5/0.24 = 14.6; "five" bands where four are named; ndf 204 against 205; "fresh" pseudo-experiments that
  §9.4 says were used in development.
- **Which coverage test "did not run to a result"**: the abstract conflates the 1,200-experiment 5D test (ran, failed
  futility) with the staged sixteen-cell test (stopped). §10.5's two stopped efforts are hard to tell apart.
- **A covariance marked "not to be used" is used** (configuration (a)'s 5D covariance) as a yardstick in several
  places, and is listed as a fixed release identity.
- **Self-containment:** decisions and definitions given only by reference to the records document [37], the joint-test
  specification [52], [56], [57] and the companion article; numbers quoted from superseded material; private
  communications; the release placeholders ("[snapshot identifier pending deposit]").
- **Unquantified items:** the nonlinear cross-source terms named as a methodological finding; learner and configuration
  dependence; the joint tests' sub-grid residual (condition (i)); the failed offset control.
- **A per-result status table** (what each product may be cited for): proposed by all four reads in some form.
- **Claim strength:** the abstract's 1 % without the "not an independent test" caveat; "calibrated" joint tests;
  generator localization from central values without covariance.

**CITABLE FOR:** these referees' reports on the round-1 rater copy, and the scores they gave.

**NOT CITABLE FOR:** any physics claim, any venue or posting decision, the truth of any finding before it is checked
against the records, or approval of any wording.

Nothing is posted, submitted, deposited or tagged.

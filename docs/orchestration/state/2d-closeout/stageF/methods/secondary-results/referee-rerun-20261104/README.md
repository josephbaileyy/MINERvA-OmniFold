# The second two-referee read, 2026-11-04

**Asked for by** Joseph (2026-11-04): "lets do another PRD rating and see what they say about revision".

**The same procedure as 2026-11-01** (`../referee-and-qualifications-20261101/`):
- the same prompt (`referee-prompt.txt`, byte-identical to 11-01's);
- two blind referees: Sonnet as a read-only subagent (`sonnet-referee-task.txt`), and Gemini via agy with
  gemini-3.8-flash-high and `--sandbox`;
- the blinded rater copy (`manuscript.blind.txt`) from `rater-calibration/make_rater_copy.sh`, run on a clean
  worktree at main `3ee597df`. That is the paper after the cut-list round (#711), the targeted round (#731) and the
  run-period sentence (#753). 7,676 words, against about 8,100 on 11-01.

**Verdicts:**

| referee | 2026-11-01 | 2026-11-04 |
|---|---|---|
| Sonnet | major revision; not publishable as a measurement as it stands | major revision; not publishable in PRD as a measurement with the current set of limitations; reframe as a methods study if they cannot be resolved |
| Gemini | reject, or major revision recast as a methods study | major revision, with mandatory re-scoping to a methodology paper or rejection as a cross-section measurement |

**Unchanged:** both referees name the same disqualifying combination:
- unvalidated coverage and the stopped test;
- the fake-data bias at the GiBUU hybrid and the q3 tilt;
- the rounding instability;
- the post hoc run-period block.

Gemini also lists the unexplained 2D shape difference. None of these has yet been resolved by a campaign.

**New or sharper requests, from Sonnet:**
- a data-driven-prior re-unfold;
- mock data with a varied detector response;
- the joint-test estimator run in 2D against the published result;
- a binned cross-check;
- per-playlist reconstruction-level comparisons;
- cell merging or flagging for R02, R06, R10 and R15;
- self-containment: a per-block uncertainty table, the correlation matrix, the systematic list, a background table
  and the flux integral;
- the internal inconsistency between "No hyperparameter search was performed on data" and the learner chosen after
  the comparison;
- the register still reads as an audit log.

**CITABLE FOR:** the two referees' reports on the paper at `3ee597df`. **NOT CITABLE FOR:** any physics claim, or a
decision.

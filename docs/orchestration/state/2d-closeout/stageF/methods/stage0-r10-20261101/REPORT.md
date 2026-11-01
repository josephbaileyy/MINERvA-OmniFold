# The Stage 0 / R10 round: report (2026-11-01)

**Under:** the director's instruction of 2026-11-01, from the qualifications inventory §6.1 and §6.2
(`secondary-results/referee-and-qualifications-20261101/REPORT.md`, #640), under
`DECISION-20261024-joseph-5d-community-standard-route.md` item 3 ("The paper states plainly that coverage was not
validated, and why: Stage 0 and R10 are reported"). No new decision was needed. No other disclosure moves, since both
referees asked that limitations be resolved, not moved.
<!-- absence-ok: quotes the decision's requirement on the paper's text, not a claim that a result is absent -->

**Result.** Both gaps are closed, and every check passes. The abstracts, `main_paper.tex` and `main_note.tex` are
byte-identical to the base `2f62fe4ee`. Joseph sees the new text in his next read. Nothing is submitted, deposited or
tagged.

## What changed

**(1) Stage 0 and R10** (`sec_fived16.tex` §10.2, a paragraph after the C_model paragraph). It says:
- coverage is not validated because an earlier route to a calibrated model term with validated coverage did not pass
  its first two tests and was not pursued further, after which C_model was adopted unscaled;
- Stage 0 tested that earlier term on the J and H2 cells, not this C_model on the sixteen cells;
- what 0a asked (family hold-out of a scale calibrated on estimator R's bias), and its bars (0.60 per family, 0.68
  pooled);
- 0a failed on both: H2 GiBUU 0.259, with the pooled 0.697 meeting its bar; J NuWro 0.570 and GiBUU 0.541, with the
  pooled 0.645 missing it;
- 0b passed on both, and Stage 0 stopped;
- what the reconstruction-information test asked; none of its 11 configurations met its residual requirement; it
  ended incomplete, neither passing nor stopping.
<!-- absence-ok: restates the note's new text, which restates DECISION-20261024 item 3 and the two recorded verdicts (STAGE0-REPORT.md, measurement-scoping/r10/REPORT.md); no search claim -->

"R10" is named only in the source comment, because R10 is also one of the sixteen cells, listed in §10.1. The failed
global null behind INCOMPLETE is not printed ("no more").

**The paper's pointer** (`paper_body.tex`, the C_model sentence): "…has not been validated, and the first two tests of an
earlier route to a calibrated model term with validated coverage did not pass (\nsec{sec:fived16-cov})."
<!-- absence-ok: restates the note's new text, which restates DECISION-20261024 item 3 and the two recorded verdicts (STAGE0-REPORT.md, measurement-scoping/r10/REPORT.md); no search claim -->

**(2) The low-stability cells** (`sec_fived16.tex` §10.1, after "meets the support rule"): R02, R06, R10 and R15 at
0.16–0.25, the other twelve at 0.26–0.81, the definition of stability as the paper gives it, and "No stability
criterion is applied in forming the cells" (H2 decision item 3). The paper's limitation item is unchanged.

**Numbers:** each prints through `\fvval` from two new pinned readouts in `make_values_fived16.py`:
`stage0-binding.json` `df70af43` and `r10_results.json` `dafcc55e`, plus `h2_definition.json` (already pinned) for the
twelve. The stated verdicts are asserted in code: STOP; 0a FAIL and 0b PASS on both; exactly the families named below
the bar; both pooled clauses; 109 and 27 cells; INCOMPLETE, nothing passing, leg B at zero departures everywhere.

## Checks, on the final text

| check | result |
|---|---|
| the ledger (`check_ledger.py`, base `2f62fe4ee`, with `paper_body.tex` in the batch) | 5 rows, 25 probes, 1 changed base sentence, 0 failures; self-test PASS |
| `make_values_fived16.py --check` and `--self-test` | PASS: 2306 values |
| `build_all.sh` | PASS: all five PDFs (paper 12 pp, note 130 pp); no "??" in either |
| the reflow check and the registry (`check_registry.py`) | PASS |
| the two-direction review (`review.md`) | 3 Medium and 9 Low findings fixed, one omission kept with a reason; nothing false |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | 4 flags, the 620 and 5B rounds' four, none of them this round's |
| the rater copy | holddiff VERDICT PASS |

**Not run this round:** agy's targeted read and P1. The director named the four checks above. The only replaced
passage is the one paper sentence, and its old words print unchanged inside the new one.

## For the director and Joseph

- **The 1B reopening** (DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md, #640's merge) leaves the
  printed 1B disclosures true as they stand: gate D's verdict and the diagnosis stand as recorded. If the
  investigation reports, those two sentences are the ones to revisit.
- **Section numbers:** the paper's pointer resolves to the note's Sec. 10.2.

# The Stage 0 / R10 round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent with no stake in the text, read-only. It was given the diff, the
requirement (DECISION-20261024-joseph-5d-community-standard-route.md item 3; the director's "say what Stage 0 tested
and that it stopped, and no more") and the sources, not the writer's conclusions.

**What it reviewed:** `2f62fe4ee..c4a592113` (`sec_fived16.tex`, `paper_body.tex`, `make_values_fived16.py`,
`values_fived16.tex`), against `STAGE0-REPORT.md`, `stage0-binding.json`, `DESIGN.md` §2.3, §3(b) and §8,
`measurement-scoping/r10/REPORT.md`, `r10_results.json`, `DECISION-20261024-joseph-h2-16-cell-definition.md` and the
built PDFs. It then re-reviewed the fixes (`c4a592113..4ec9118f5`).

**The result:**
- Nothing false. Every number matches its readout. The asserts refuse every mutation the reviewer tried (verdict,
  form, 0a and 0b flipped, a family added below or moved above the bar, either pooled clause, R10 STOP, a passing
  configuration, leg B at 1 or 3, an extra configuration).
- Three Medium findings and nine Low findings (eight first-pass, one from the re-review). All are fixed except one
  Low, kept with a reason.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | the paper's "the two tests made toward that validation" reads as tests of this C_model; Stage 0 graded a calibrated M2 on five vertices and other cells, R10 is not a coverage test, and the 1B coverage test a few paragraphs later competes for "two tests" | FIXED: "the first two tests of an earlier route to a calibrated model term with validated coverage did not pass" |
| 2 | Medium | the note's scope caveat (Stage 0's numbers are not this result's) was only in a comment | FIXED: "The first, Stage~0, tested that earlier term on the J and H2 cells, not $C_{\mathrm{model}}$ on the sixteen cells." |
| 3 | Medium | 0a's failure never stated; J's pooled value not said to miss its bar; "Its second part" with no first | FIXED: "This first part failed on both sets of cells …, and the pooled 0.645 did not meet its bar … With the first part failed, Stage~0 stopped." |
| 4 | Low | "and of 0.68 pooled" reads as exactly 0.68 | FIXED: "of at least" |
| 5 | Low | "the truths of the other generator families": the folds are truth deformations assigned to families (the q3 tilt by inference) | FIXED: "the truth deformations assigned to the other generator families" |
| 6 | Low | "the generators stay distinguishable": 0b's pairs are departures against the nominal | FIXED: "truth departures stay distinguishable from the nominal" |
| 7 | Low | R10 tested width and residual, and added variables in the plural | FIXED: "from finer reconstructed binning or added reconstructed variables, narrows a width floor and reduces the residual" |
| 8 | Low | R10 INCOMPLETE did not fail the route by its own rules; the route ended by DECISION item 6 | FIXED: "and was not pursued further" (item 6) |
| 9 | Low | "the model term" ambiguous after "route" | FIXED: "after which $C_{\mathrm{model}}$ was adopted unscaled" |
| 10 | Low | "only 0.16–0.25" implies a gap; R11 is 0.26 | FIXED: "only" dropped; "(the other twelve, 0.26–0.81)" through new keys `h2-stab-rest-*` |
| 11 | Low | the J (109) and H2 (27) cell counts not asserted | FIXED: asserted from GiBUU's `n_pairs` in both sets |
| 12 | Low (re-review) | "with these inputs" (item 6's wording) has nothing in the note to refer to | FIXED: dropped |
| — | — | the INCOMPLETE reason (R10's failed global null) is left out | KEPT, as the guardrail asks ("no more"); the reviewer counted it as not misstated |

**Checks the reviewer ran that passed:** the values against both JSONs and the reports; the stability definition
against `h2_definition.py` `Stats.of` and the four lowest cells; "No stability criterion" against the H2 decision item 3
and the purity-only merge rule; `make_values_fived16.py --check`; the rendered text of both PDFs, the paper pointer
resolving to the note's Sec. 10.2; "R10" never printed as the test's name; the worktree unchanged after each read.

# Referee read of fig:deformation (2026-11-12) and check A

**Consult (`consult/`).** At Joseph's request, the director ran a JINST/PRD figure-referee read of
fig:deformation: codex-school, gpt-6.1-sol, reasoning effort high, read-only sandbox, session
01a1ce03-e0d7-7243-8f7f-b41d3251360a.
- `input.txt` is the prompt: the caption and the two citing paragraphs, values as [value].
- The figure as reviewed is not copied here. Its bytes, sha256
  31ca6df9af94f40c97f4b12b9f8b85f1d925806b34962eef0208071e8a2ff906, are the tracked
  docs/analysis-note/figures/methods_short/m3_fig2_deformation.png at #977 b86c387f (*.png is gitignored; this
  avoids a force-added duplicate).
- `out.txt` is the report, verbatim. `run.log.txt` is the session log.

The verdict was minor changes: seven readability items, plus two points beyond readability. First, the caption's "Each point
… its own pseudo-experiment" is misleading for ensemble means. Second, "recovers only part" is not uniform: in the
red cell, 0.8–1.5 GeV with W ≥ 3 GeV, an injection of about −30 % against a +74 % residual puts the unfolded value
above nominal.

**Check A (`check-a/`, the director's item A).** The referee's reading, verified from the records rather than the plot.
`a_recovery.py` defines everything, `a_recovery.json` is its output, and `a_recovery.out.txt` its stdout. In EW29
(E_avail 0.8–1.5 GeV, W ≥ 3 GeV):

| truth | injected | residual | unfolded vs nominal | recovered fraction f |
|---|---|---|---|---|
| GiBUU-to-GENIE E_avail | −30.3 % | +73.9 % | +21.2 % | −0.70 |
| W1 NuWro E_avail | −16.5 % | +31.3 % | +9.7 % | −0.59 |
| W3 NuWro (pT, p∥, E_avail) | −13.1 % | +23.7 % | +7.5 % | −0.57 |
| W2 GENIE + MEC | −0.7 % | −3.4 % | −4.0 % | (\|i\| ≤ 2 %, not classed) |

Over the supported cells with |injected| > 2 %, net of the nominal closure (at most 0.1 % per cell):

| truth | cells | opposite (f < 0) | partial (0 ≤ f ≤ 1) | overshoot (f > 1) | median f |
|---|---|---|---|---|---|
| GiBUU | 39 | 12 | 17 | 10 | 0.63 |
| W1 | 33 | 10 | 22 | 1 | 0.56 |
| W2 | 26 | 0 | 17 | 9 | 0.88 |
| W3 | 35 | 8 | 23 | 4 | 0.61 |

The referee is right. The unfolded cells move toward the changed truth by a median 56–88 % of the injected change,
but per cell the response ranges from movement opposite to the change (EW29 for three of the four truths) to
overshoot. "Recovers only part" holds for the median but not cell by cell. Paragraph 1 (paper_body.tex:263) is not
edited until the director rules on wording, after a PRD read.

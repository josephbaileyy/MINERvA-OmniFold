# Independent referee reports and a qualifications inventory (2026-11-01)

**Asked for by Joseph** (2026-11-01): "is it possible to get a full validated measurement and report clean results? maybe do the physics referee review too ... the next goal should be trying to resolve all of the qualifications so we dont need to include them".

**Recorded by** the paper-tighten lane, as director. Three consults, none on sol (the P1 rater):

| consult | model | saw | files |
|---|---|---|---|
| blind referee 1 | Claude Sonnet (Agent tool, read-only, told to read only the two files) | `referee-prompt.txt` + the paper text | `sonnet-referee-task.txt`, `sonnet-referee-answer.txt` |
| blind referee 2 | gemini-3.8-flash-high via agy, `--sandbox` | the same prompt + paper text | `gemini-referee-answer.txt` |
| qualifications inventory | Claude Sonnet (Agent tool), read-only on a detached worktree of main `bc07ed0e` | the repository | `inventory-prompt.txt`, `inventory-answer.txt` |

The paper text is the 620 round's rater copy (`INPUTS.txt`); `main_paper` is unchanged from `291ac142` to `bc07ed0e`. Answers are verbatim from each run's output. The inventory agent's own write was refused by the harness, so its report is the text of its final message.

**CITABLE FOR:** what these three reviewers said about this text on 2026-11-01. **NOT CITABLE FOR:** any physics claim; a rater's factual reading of the paper unless checked below; any decision.

## In brief

- **Both referees:** not publishable as a measurement as it stands. Sonnet: major revision; Gemini: reject, or major revision recast as a methods study. Both prefer that the limitations be **resolved, not moved to the note**, and both offer a methods-study reframing as the alternative.
- **Common major issues:** unvalidated coverage and the stopped coverage test; the fake-data bias at the GiBUU hybrid and the q3 tilt; the run-period block (cause unknown, added after the fact); the rounding-level instability (up to 2.6 statistical σ); the uncorrected carbon-versus-CH target difference for NuWro and GiBUU.
- **Inventory:** 44 distinct qualifications; 26 inherent (K), 10 movable (M), 11 resolvable (R) in some form. "No qualifications" is infeasible; a 16-cell coverage validation by the only recorded independent design costs about 1,800 node-h per arm.

## The director's checks of the reviewers' factual claims

- **Sonnet minor 7 (Table III "transposed"):** not a defect. The text extraction scrambles the table. `values_fived16.tex`: GENIE CV total 105.42, shape-only 100.57 (with the block); 109.35 and 108.51 without; shape-only is below total in both.
- **Inventory §6.1 (Stage 0 not disclosed): confirmed.** `DECISION-20261024-joseph-5d-community-standard-route.md:46-47` says the paper states why coverage was not validated: "Stage 0 and R10 are reported". A grep of `docs/analysis-note/*.tex` at `bc07ed0e` finds the Stage 0 STOP (`5d-design-20261023/STAGE0-REPORT.md`, result table at :25-30) printed in neither document; the only "stage0" hits are fake-data truth labels.
  <!-- absence-ok: scoped to the grep of docs/analysis-note/*.tex at bc07ed0e named in the sentence -->
- **Inventory §6.2 (low-stability cells in the paper only):** confirmed for the sentence at `paper_body.tex:288`; the values are defined in `values_fived16.tex:1614-1616`, and a grep of the note's sources finds no print.
  <!-- absence-ok: scoped to the grep of the note's .tex sources at bc07ed0e -->
- **Gemini 4(12) (C_resp "a single overall 1σ parameter"):** imprecise. The inventory (Q16) and `DECISION-20261026-joseph-adopt-cresp.md:42-43` give a ±1σ scale per species; the paper's qualification is that effects beyond a scale are not covered.
- Other figures quoted by the referees (p = 5.3×10⁻²⁸, 2.6σ, 0.73–2.56, 8.3 %, 0.06, χ²/ndf 2.27) are the paper's own.

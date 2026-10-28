# Reviewer brief: the five-observable integration PR (one document per reviewer)

`S` = `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad`. The tree is `S/wt-con`, uncommitted, on branch `stageF/fived16-integration-20261027` from main `8b0f83fd`. **It is read-only for you.** The base sources are in `S/5d/base/`.

## What the PR does

Joseph, in `docs/orchestration/DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2, integrates a new five-dimensional result into the note and the paper:
- **The result:** configuration (e)'s data result on 16 cells R00–R15, with the reported covariance C_total + C_resp.
- **Its fake-data tests:** F0 graded against C_total, and F0b against C_total + C_resp.
- **The generator comparison:** χ² against C_total + C_resp + V_g.

The new content is:
- the note's new chapter `docs/analysis-note/sec_fived16.tex`;
- the paper's two blocks in `docs/analysis-note/paper_body.tex`, marked `% FIVED16-BEGIN … % FIVED16-END`.

Every number prints through `\fvval{key}` from the generated `values_fived16.tex`, which `make_values_fived16.py` writes from readouts it pins by sha256. A writer also edited existing statements (the "scoping edits") so that each statement says which five-dimensional product it is about: the configuration-(a) central value and its five-axis covariance, or the sixteen-cell result.

**Inputs:**
- the outline and rulings: `S/5d/outline.md`, with the director's rulings (below);
- the site list: `S/5d/scope-sites.tsv`;
- the ledger: `docs/orchestration/state/2d-closeout/stageF/methods/fived16/ledger.md`;
- the built PDFs as text: `S/5d/main_note.txt`, `S/5d/main_paper.txt`. They print two `[PENDING: …]` placeholders by design: the covariance export and two figures have not landed.

**Sources** (read them directly):
- `docs/orchestration/state/measurement-paper/5d-community-20261024/`: S1-REPORT, S1-DIRECTOR-RULINGS, FD-PLAN, FD-F0-REPORT, FD-F0b-REPORT, FD-G-REPORT, FD-G-DIAG-REPORT, FD-G-FOLLOWUP-REPORT, FD-G-SENS2-REPORT, and the readouts in `fd/readout/` and `s1/readout/`;
- `docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/` (CRESP-REPORT, cresp.json);
- `nd-unfolding/pv-ladder/readouts/` (h2_definition.json, cmodel_5d.json);
- `docs/orchestration/state/s5p/stage1/stage1_inspect.json`;
- the decisions DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md, DECISION-20261026-joseph-adopt-cresp.md, DECISION-20261026-joseph-5d-generator-comparison-presentation.md and DECISION-20261027-joseph-chi2-table-format.md.

## The rulings the text must obey

1. **The reported covariance of f is C_total + C_resp.** The χ² adds each prediction's V_g. The fake-data tests grade against C_total + C_resp, or without the truth's own generator vertex, with C_total beside it. Both columns are printed, and nothing reads their difference.
2. **C_model is stated as what it is:** the change in the unfolded data when the prior is reweighted to each generator. It is unscaled, not a calibrated bound, and its coverage at held-out truths has not been validated. **Never** write that it "includes", "covers" or "does not include" the regularization bias.
3. **No coverage claim** is made for the sixteen-cell result. The only limitation sentence allowed is that the reported uncertainty does not cover the fake-data bias at the GiBUU-like truths or at the q3 tilt. The listed truths must be exactly those listed under C_total + C_resp: Stage 0c GiBUU (R06 only, z = 2.01, which must print with two decimals), A7 GiBUU, and the q3 tilt.
4. **χ² prints with its ndf (109/16), never as a ratio.** Shape-only is the only companion, and no diagonal-only χ² is formed.
5. **Qualifiers that must print where the statement is made:**
   - GiBUU is compared on 8 cells, and why;
   - NuWro and GiBUU are on carbon, with no correction to CH;
   - Tune v1 is the prior;
   - the covariance is built in part from the compared generator, GENIE CV included through the reference.
6. **The sensitivity sentence** is the director's accepted draft, word for word.
7. **Out of scope for edits:** the abstracts, release text (app_release.tex), claims, KI-85, `\pubhold` and data-availability text. The writer listed proposals for these separately.
<!-- absence-ok: quotes or summarizes the note's and paper's printed text, or a ruling about it, as this PR's record; not a new absence claim -->

## Your job (two directions)

1. **Every printed number** in your document's new content: check it against its readout at the printed precision, beside the right matrix. Use the `\fvval` key and `make_values_fived16.py` to find the source key.
2. **Every statement** in the new content: confirm the sources support it, adds no interpretation, and carries its qualifiers (rulings 1–6).
3. **Every scoping edit** in your document (`diff` against `S/5d/base/`): confirm it is true as read for BOTH products, adds no fact, obeys rulings 2 and 3, and leaves no unscoped "the/any/one" five-dimensional statement that is false once the sixteen-cell result prints. Also check for sites the writer left (see `S/5d/W/REPORT-W.md`) that you judge must change.
4. **Placement and register:** a reader of a PRD paper, or of its long note, must be able to follow it.

## Output (in text; write no files)

- A table with the columns `# | severity (BLOCKING / SHOULD-FIX / NIT) | where (file:line, quoted words) | finding | exact fix`.
- A verdict: ADOPT, ADOPT-AFTER-FIXES or DO-NOT-ADOPT.

**Constraints:**
- Read-only: no edits and no git state changes.
- No web, and no other models or CLI agents.
- Never propose a fix that adds a fact the sources do not support.

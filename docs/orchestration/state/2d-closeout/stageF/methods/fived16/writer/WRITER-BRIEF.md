# Writer brief: make every 5D statement product-specific (the five-observable integration PR, item 4)

`S` = `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad`

Your copy: `S/5d/W/repo/docs/analysis-note/`. The base (main `8b0f83fd`): `S/5d/base/`. Edit only your copy.

## Why

A new five-dimensional product is being integrated into the note and the paper. It is:
- **the sixteen-cell result** on cells R00–R15;
- from **configuration (e)**, which uses refined negative-weight background subtraction;
- with a **reported covariance C_total + C_resp**, at a median per-cell relative σ of 7.29 %.

The integrator writes its own chapter (`sec_fived16.tex`: labels `sec:fived16`, `sec:fived16-result`, `sec:fived16-cov`, `sec:fived16-fd`, `sec:fived16-gen`). The integrator also writes the paper's two new subsections, `sec:result16` (end of Sec. V) and `sec:gen16` (Sec. VII, after `sec:central`). Your copy has stubs carrying those labels. Do not write inside the stubs or the `% FIVED16-BEGIN … END` blocks.

The note and paper today describe one 5D product:
- the **configuration-(a)** five-dimensional central value, with purity-based background subtraction;
- with the **five-axis covariance** used with it, which does not meet its specification (`sec:eavailw-adopted`).

Once the 16-cell result prints, the unscoped or universal statements about "the" or "any" 5D product become false or ambiguous. Your job is to make each one say which product it is about. Change nothing else.

**Read first:**
- `S/5d/outline.md` §2 (the groups and their proposed forms);
- `S/5d/scope-sites.tsv` (every site: file, line at 8b0f83fd, quote, about, why, severity).

## The rulings (director, 2026-10-27), which override the outline where they differ

- **Group C** ("no quoted uncertainty includes the regularization bias"):
  - scope the existing statement to the configuration-(a) product and its five-axis covariance;
  - for the 16-cell result, state what C_model **is**, not what it covers. C_model is "the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU)". Point to `\S\ref{sec:fived16-cov}` for it, and to `\S\ref{sec:fived16-fd}` for the fake-data study's measured comparison of the bias with the reported covariance.
  - **Never** write that C_model, or the reported covariance, "includes", "covers", "accounts for" or "does not include" the regularization bias. That reading is Joseph's.
- **Group E** ("no five-dimensional measurement with total uncertainties was constructed"):
  - the precision study's reporting definitions (RD1–RD3, including H2 at 27 cells) met no precision target;
  - the 16-cell result is the same H2 grid after a purity merge of its supported boxes (`sec:fived16-result`), with total uncertainties.
  - Do not print counts or σ yourself. Point to `sec:fived16-result` for them.
- **No coverage claim.** The fake-data study is NOT CITABLE FOR coverage. Never write that the 16-cell result's intervals are "validated" or have "coverage".
- **Stage G sentences** ("no covariance-based generator significance", 4 sites): scope them to the configuration-(a) covariance and add a pointer to `sec:fived16-gen` (or `sec:gen16` in the paper). Write the scoped form only. The p-value question is the integrator's packet.

## Hands off (list each site you skip, with its reason, in your REPORT)

- **The abstracts:** `main_note.tex` and `main_paper.tex`. They are Joseph's text and are protected. List their sites, with your proposed form, in `S/5d/W/abstract-proposals.md`.
- **Release text:** `app_release.tex`. It is Joseph's. List its sites in the same file, under a heading.
- **Protected files:** `values.tex`, `values_inference.tex`, `app_history.tex` and the records files.
- **Unchanged statements:** claims, KI-85, `\pubhold`, data-availability text, §5.2's check-bound history, the SEC4 phrases and `\covTwoDCTwo`.
- **paper_body.tex's Scope paragraph (line 46) and Limitations (line 405)** carry claims. Edit only the product scoping in them. Put any wording beyond that in `abstract-proposals.md` as "for Joseph".

## The move

- **Add a qualifier that names the product,** e.g. "the configuration-(a) five-dimensional central value", "the five-axis covariance of the configuration-(a) central value". Where a sentence lists uses or products, add the 16-cell result with a pointer.
- **Remove "the one"/"one" uniqueness** where a second product now exists.
- **Add no fact and no number.** A pointer replaces any number you would need.
- **Keep every true qualifier.** A sentence must stay true as read for BOTH products. If you cannot make one true without new facts, leave it unchanged and list it.
- **AMBIGUOUS sites:** fix them where the 16-cell result is in view: the same section, the summaries, Table 1, the method and estimator tables, the abstract-adjacent text. Leave purely local ones (inside `sec:eavailw-adopted`, which is about that covariance) unchanged, and record each with a reason.
- **Format:** one source line per paragraph and per comment block. Never end a prose line with a `%` comment. Keep every `% Search:` line in its paragraph. If you change an absence claim's paragraph, its Search line stays.

## Ledger

Put one row per changed base sentence in `S/5d/W/ledger-W.md`, with the columns `| id | fact | before | disposition | after | probe |`.
- **The id:** the group letter plus a number, e.g. `A3`, `C2`, `AMB17`.
- **`before`:** the base sentence id from:
  ```
  python3 S/wt-con/docs/orchestration/state/2d-closeout/stageF/methods/fived16/check_ledger.py S/5d/W/repo --old-dir S/5d/base --list
  ```
- **The probes:**
  - `X:<file>::<the old unscoped words>`;
  - `N:<file>::<the scoped words>`.
- **Check:**
  ```
  python3 …/fived16/check_ledger.py S/5d/W/repo --old-dir S/5d/base --ledger S/5d/W/ledger-W.md
  ```
  It must report 0 failures. STRUCTURAL is already satisfied in your copy.

## Checks in your copy

- `python3 S/wt-con/docs/analysis-note/reflow_tex.py --check <your files>` must PASS.
- `python3 S/wt-con/docs/orchestration/state/2d-closeout/stageF/methods/note-consolidate/printed_diff.py --dirs S/5d/base S/5d/W/repo/docs/analysis-note <files>` must show only the intended sentences.
- **Build:**
  ```
  cd S/5d/W/repo/docs/analysis-note && PAR_GLOBAL_TMPDIR=S/partmp-5dW bash build_all.sh > ../../build.log 2>&1; echo rc=$?
  ```
  - Undefined references are expected only for labels the stubs lack. There should be none, since the stubs carry all seven.
  - A make_values or RECORDS-PIN SKIP in a copy is expected, and so is the pending-placeholder check.

  Report what fails and why.

## Deliverables (in `S/5d/W/`)

- the ledger;
- `changes-W.md`: per site, before, after and its group;
- `abstract-proposals.md`;
- `REPORT-W.md`:
  - every FALSE-ONCE-PRINTED site (all 33) and every AMBIGUOUS site, with its disposition: changed (ledger id), left (reason), or hands-off (where listed);
  - the check outputs.

**Constraints:**
- No git commands.
- No outside models or CLI agents.
- No outward acts.
- If the harness refuses a file write, put its content in your reply.

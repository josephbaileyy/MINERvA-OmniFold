# The five-observable integration PR: report (2026-10-27)

**Authority:** Joseph, `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2.
**Presentation rules:** `DECISION-20261026-joseph-5d-generator-comparison-presentation.md`, `DECISION-20261027-joseph-chi2-table-format.md`, `DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` and `DECISION-20261026-joseph-adopt-cresp.md`.
**Outline:** `outline.md`, with the director's rulings at its end.
**Base:** main `8b0f83fd`. **Branch:** `stageF/fived16-integration-20261027`.

**Status: not mergeable.** Two things have to happen first:
- **The printed wording goes to Joseph** (`WORDING-PACKET.md`, `printed-wording.md`) and merges only with his answers.
- **Two inputs must land:**
  - the covariance export;
  - the two figures from the 5D measurement session.

  Until both land, the build refuses the `\fvpending` placeholders. The paper's supplemental file is Joseph's to specify.

## What it adds

- **The note's new chapter** `sec_fived16.tex` (§10), with eight tables:
  - the sixteen cells, R00–R15: their boxes, the cell-integrated cross section $f$, and the per-cell σ under $C_{\mathrm{total}}$, $C_{\mathrm{resp}}$ and the reported $C_{\mathrm{total}}+C_{\mathrm{resp}}$;
  - the covariance and what it is built from: the groups of $C_{\mathrm{e}}$; what $C_{\mathrm{model}}$ is, with its labels and vertex shares; and $C_{\mathrm{resp}}$ with its scope and cross-talk;
  - the fake-data tests:
    - F0b against $C_{\mathrm{total}}+C_{\mathrm{resp}}$, with F0 against $C_{\mathrm{total}}$ beside it;
    - the triggers, read by group, and the controls;
    - the descriptive variants and the six ungraded power alternatives;
  - the generator comparison:
    - χ² with ndf and shape-only, with the variant without $C_{\mathrm{resp}}$ as a labelled sentence;
    - per-cell pulls and $(g-f)/f$;
    - the sensitivity tables, the eigenmode breakdown and the R04 look.
- **The paper's two new subsections** (paper_body.tex, `FIVED16` blocks):
  - Sec. V F, the measurement: its cells, covariance and fake-data table, and the limitation once;
  - Sec. VII B, the comparison: the χ² table, the limitation at GiBUU, and the sensitivity sentence.
- **Scoping edits** (the writer's, groups A–F and AMB, `writer/`): 73 changed base sentences in 15 files. Each one now names the five-dimensional product it is about, so that nothing printed is false once the sixteen-cell result prints.
- **The structural exception** (director, 2026-10-27):
  - `\input{values_fived16}` and `\input{sec_fived16}` in main_note.tex;
  - `\input{values_fived16}` in main_paper.tex;
  - nothing else in either file. `check_ledger.py` STRUCTURAL enforces this.

## How the numbers are kept honest (code, not notes)

- **`make_values_fived16.py`** writes every printed number of the new prose, 1207 keys, into `values_fived16.tex`.
  - It reads 11 readouts, each pinned by sha256: S1, CRESP, F0, F0b, G, G-DIAG, G-FOLLOWUP, G-SENS2, the H2 definition, the stage-1 receipt and cmodel_5d.
  - Numbers that live only in readout label strings are parsed with regexes that fail if the label changes: GiBUU's domain, the step-adjacent fraction and the trigger rule.
  - `--check` runs in build_all.sh and in CI.
  - `--self-test` shows that a wrong pin is refused and that a file printing R06's $z$ as "2.0" fails `--check`.
  - Outside the canonical repository it reports SKIP.
- **NUMERAL** (`check_ledger.py`) fails on any number typed by hand in the new prose. Only 16, 8 and 5 are allowed, and layout arguments are exempt.
- **R06's pull, 2.0096, prints as 2.01.** build_all.sh fails on any printing of it with one decimal.
- **`\fvpending{…}`** marks the covariance export and the two figures. build_all.sh refuses a note or paper that prints one. The pdftotext output goes through a file, so an extraction failure cannot read as a pass.
- **Ledger** (`ledger.md`): 80 rows, 189 probes, 73 changed base sentences, 0 failures. Besides the scoping rows:
  - I1–I3, the integrator's: the structural exception and the two insertion points;
  - **G1/G2,** the guard for agy's measured blind spot (below). The sensitivity sentence's scope must name "interaction, flux, detector and lateral", and "all systematic" and "all correlations" must not print, in the note and in the paper. A copy planted with "all systematic correlations removed" fails both probes;
  - **G3,** director ruling 3: "whose coverage is not validated" prints in its three scope homes, and no "with validated coverage" or "coverage is validated" prints;
  - **G4,** director ruling 1: the variant without $C_{\mathrm{resp}}$ is a labelled sentence from FD-G's `variant` keys, not a table column.
<!-- absence-ok: quotes or summarizes the note's and paper's printed text, or a ruling about it, as this PR's record; not a new absence claim -->

## Gate inputs changed

- **`records-move-ledger.md`:** five probes pin sentences that the scoping edits changed: L11, L-thin-C55 (the §1 roadmap row), L-thin-C01 (App. A), L-thin-C07 (App. C) and L-thin-C41 (§11 lead). Each now pins the scoped text, with a "probe updated for the five-observable integration" note, as earlier passes did. RECORDS-MOVE passes, and its self-test catches 41 of 41.
- **Registry** (`docs/orchestration/registry/`):
  - paper_body.tex:90, cited by ALIASES rows 35, 38 and 67 and ATTRIBUTION row 17, changed under the group-A scoping. Every cited quote ("configuration~(e), the joint-test estimator", "joint-test estimator", "configuration~(f)") still prints on it, so only the line digest was re-cited (`--cite`).
  - The Search line added to the paper's Scope paragraph moved later lines by one, so `--repoint` refreshed the line hints. It never accepts an edited line. It also refreshed three UNRESOLVED-NAMES hints that had drifted on main.
  - `results_index.py --write` regenerated RESULTS-INDEX and `records_results_index.tex` / `records_estimators.tex`, whose diffs are those line hints only.
  - REGISTRY and its self-test pass.

## Rulings and facts established during the work

- **The F0b listed set** (the director's queue message said otherwise; corrected from `fd_f0b_readout.json`):
  - W3 is no longer listed (p = 0.0141);
  - **Stage 0c GiBUU is still listed** by R06 ($z$ = 2.0096), though its p trigger cleared;
  - A7 GiBUU and the q3 tilt are listed.
- **The covariance:** a committed 16×16 export is being made, and the note will print it. The paper's supplemental file is Joseph's.
- **The flux sentence quotes the per-group numbers only,** with no interpretive verb. "All systematic correlations" was false: the joint family is interaction, flux, detector and lateral only. "χ²/ndf ≳ 3" failed for both GENIE predictions (2.84, 2.83).
- **H2:** one grid at two stages.
  - stage1_inspect gives 27 of 32 boxes supported;
  - h2_definition records 12 merge steps at τ = 0.1 and 4 boxes unreported, giving 16 cells. Box 17 is absorbed into R09.
- **W1–W3:** the note's deformations and FD-PLAN's Stage 0 truths are the same, by description, source (the s5e assessment) and seeds (803000–803019, …). Neither side carries a digest, so identity was not checked by sha256.
- **sec_systematics.tex:278 and :282 stay true; each now has a Search line.**
  - S1's lateral block is re-selected event loops: `MNV101_ACTIVE_UNIVERSE`, MODE=standard, and the C++ rebuilds selection, kinematics, weights and backgrounds.
  - All 11 C_resp products are full-sample and deterministic: their sha256 equal cresp.json's pins, every estimator has subsample 1.0 and deterministic true, and the split is null.
- **sec_method.tex:28** lists "the sixteen-cell 5D result **and its covariance**" among the refined uses (S1-DECLARATION's title; C-RESP-SPEC's 400/31).
- **A stale `% Search:` line** in sec_5d.tex ("no note source prints a five-dimensional measurement with total uncertainties") was re-searched and re-dated @ 8b0f83fd.

## Reviews

**Writer** (`writer/REPORT-W.md`):
- **Changes:** 29 of the 33 false-once-printed sites and 49 of the 101 ambiguous ones changed.
- **Left:** 39 ambiguous sites, each with a reason.
- **Hands-off:** 17 sites in the abstracts and release text, proposed in `writer/abstract-proposals.md`.

**Fresh reviewers:** one for the note and one for the paper. Both found every printed number matched its readout. Both gave ADOPT-AFTER-FIXES. The fixes:
- **Paper, blocking:**
  - "Under the reported covariance, the bias is listed at the GiBUU shape…" was false as read: against the full matrix Stage 0c has p = 0.113. It now says "without the GiBUU component", and the note's listing sentence is fixed the same way;
  - "…the 8 cells … where the fake-data tests list the GiBUU-like truths" was false, because R06 and R07 lie outside them. It is replaced by the allowed limitation sentence.
- **Note, blocking:** Table 14's "without $C_{\mathrm{resp}}$" column broke the χ² format decision. It became a labelled sentence (ruling 1).
- **Should-fix, applied:**
  - C_resp's full scope from C-RESP-SPEC §7, including that it does not enter the joint tests;
  - "unscaled and not a calibrated bound" at every $C_{\mathrm{model}}$ clause;
  - the H2 sentence, with edges, the 27 supported boxes and box 17;
  - "no such truth … its own generator's component";
  - configuration (e)'s subtraction named as the paper defines it;
  - "These are not held-out truths, and the detector response is not probed" (F0b's `labels.not`);
  - the trigger groups defined; cross-talk; V_g as the finite-sample diagonal covariance; units in the cells table;
  - the descriptive-variant, power-alternative and per-cell-pull tables;
  - the limitations-list pointers (ruling 2);
  - the placement sentence, drafted for Joseph (packet Q9);
  - the generator self-test, which the reviewer showed was vacuous (`elif stale != text`). It now runs `--check`'s comparison on a stale file.
- **Not done (NITs), with reasons:**
  - a records citation for the chapter: that needs a records entry;
  - explaining the 4.5 GeV/$c$ boundary with the DIRECTOR-RULINGS §5 fractions: they exist only in prose, so they cannot be generated values. The director offered to route them into the covariance product's labels;
  - "noise gate" undefined: it is the label's own wording.

## agy (gemini-3.8-flash-high, `register-method/tools/run_x.sh gemini`), blind, with planted-defect controls

| run | passages | result |
|---|---|---|
| scoping edits (4 groups) | 62 | all AGREE |
| scoping control | 8 (3 plants) | **3 of 3 caught**: "C_model includes the regularization bias", "the one five-dimensional covariance", "validated coverage" |
| new content, printed text against source excerpts | 7 | 5 REVISE |
| new-content control, first | 2 of 4 plants applied | **2 of 2 caught**: W3 listed, R06 at 2.0 |
| new-content control, re-planted on normalized text | 2 plants | **1 of 2 caught**: caught "C_model includes …"; **missed "all systematic correlations removed"** |

- **agy caught 6 of 7 planted defects.** Its measured blind spot is a group-scope overstatement inside a sentence whose numbers are right. Ledger rows G1/G2 guard that sentence instead of agy.
- **Of the real run's REVISEs, two were valid and are fixed:**
  - the paper's $C_{\mathrm{model}}$ sentence lacked "not a calibrated bound";
  - the circularity sentence omitted GENIE CV.
- **The rest were not defects:** PDF-extraction and float artifacts (checked on the layout text); numbers in the readouts and CRESP §2–§3 that the excerpts omitted; and the placeholders.
- **One true conflict** went to Joseph (packet Q3): the decision allows one sensitivity sentence, and the accepted draft has three.
- All inputs, outputs and controls are in `agy/`.

## Checks (on the delivered tree)

| check | result |
|---|---|
| `check_ledger.py` (base 8b0f83fd), with STRUCTURAL and NUMERAL; `--self-test` | 80 rows, 189 probes, 73 changed base sentences, 0 failures; 9 of 9 plants caught |
| `make_values_fived16.py --check`; `--self-test` | PASS (1207 values, 11 readouts pinned); PASS |
| `reflow_tex.py --note --check` | PASS, 45 sources (values_fived16.tex is GENERATED) |
| build (`build_all.sh`) | 0 undefined references in the note and the paper; SEC4 15/15; **refused at the pending-placeholder check, as designed**, until the export and the figures land |
| the note's records gates, registry, absence claims, pytest | run at commit by the pre-commit hook and in CI |

## Errors in this work

- **A wrong default of mine, found while checking the packet's numbers:** the values generator's p floor (10⁻³⁰) applied to every small p, so Stage G's exact p-values (e.g. 1.5×10⁻⁴⁸) would have printed as "<10⁻³⁰". Only F0's underflow (p = 0) is below that floor. It is fixed.
- **I adopted review NIT wording without checking it once before** (the consolidation PR's W1#10); here every reviewer's fix was checked against its source first (C-RESP-SPEC §7, F0b `labels.not`, FD-G-DECLARATION's V_g, the readout's groups).
- **Process slips, each caught before it shipped:**
  - an f-consistency check compared cells by position;
  - `\fvval` digits were split as strings for box edges;
  - a `declare -A` in bash 3.2;
  - an apostrophe broke a quoted heredoc;
  - build_all.sh was edited while a build was running; that build was discarded and rerun.
- **I left a `git checkout origin/main --` in a worktree,** which detached it. The sweep reviewer noticed. It was harmless: #409 was already pushed.

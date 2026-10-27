# Note consolidation content PR: report (2026-10-27)

**Authority:** Joseph, `DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md` item 1: the note's repeated caveats are merged now; drops wait for Joseph and Ben.
**Base:** main `602ab31f`. **Branch:** `stageF/note-consolidate-20261027`.
**What it is:** a content PR, not a scored register round. It has no P2N or P1N.
**Outline:** `outline.md`, approved by the director with five rulings, which are recorded at its end.

## What changed

Each removed restatement (a `[C]` site of `../note-n3/content-reduction.md` §3) became a pointer to the fact's single home (its `[keep]` site), or was removed where the sentence already points there. No fact leaves the note. A site where removing the qualifier would make the remaining sentence false or misleading was kept verbatim, with its reason in the ledger.

- **Files changed (15):** selection_features, sec_method, sec_systematics, sec_validation, sec_3d, sec_eavailw, sec_5d, sec_joint, app_statmethods, app_negweight, app_guide, app_codebase, sec_execsummary, sec_intro and sec_summary.
  - In sec_systematics.tex one of its five sites is applied (R18a, the omissions list). The other four are kept (R04b, R04c and R14a reverted at integration; R21a kept by the writer).
- **Gate inputs changed (2):** `records-move-ledger.md` (three rows, below) and the self-test fixture of `check_note_records.py` (below).
- **Byte-identical to base:**
  - `values.tex`, `values_inference.tex`, `app_history.tex`, `app_release.tex`, `main_note.tex` (the abstract), `main_paper.tex`, `paper_body.tex`, the records files and `result_status_rows.tex` (Table 1);
  - §5.2's check-bound history, the SEC4 phrases and the `\covTwoDCTwo` sentences.
- **No `[D]` site was applied.**

## The 60 sites

`SITES.tsv` gives every `[C]` site of the cost list with its disposition and ledger row. `check_sites.py` parses the cost list independently of the extraction that once dropped six sites. It fails unless the table holds exactly the list's `[C]` sites. Given `ledger.md`, it also fails on a named ledger row the ledger does not hold, and on a ledger row that no site names.

```
python3 check_sites.py ../note-n3/content-reduction.md SITES.tsv ledger.md
CHECK-SITES :: PASS (cost list [C] sites 60; table 60: applied 43, excluded 4, kept 13, merged 0)
python3 check_sites.py --self-test
CHECK-SITES SELF-TEST :: PASS (10 cases)
```

**Applied (43).** Each has a ledger row with an `X:` probe for the removed words, an `N:` probe for every kept fact at its home, and an `N:` probe for the pointer sentence.

**Kept by the director's ruling 1 (4):** Table 1's cells.
- R07 `result_status_rows.tex:32` "calibration adequacy remains conditional";
- R14 `result_status_rows.tex:14` "Earlier statistical band failed fixed-truth coverage";
- R17 `result_status_rows.tex:25` "injected-bump closures have no recorded threshold";
- R18 `result_status_rows.tex:14` "learner chosen after the comparisons were known".

**Kept by the guardrail (13).** The full reasons are in the ledger rows.

Eight were kept by the writers:
- **R03d** (sec_eavailw, sec:eavailw-band): "no compatibility metric is quoted" prints only beside these ratios.
- **R07a** (sec_joint, sec:joint5d-design): the sentence is the third of "Three requirements are distinct".
- **R13a** (sec_validation): the home lacks the "or a validated generative law" option and the "conditional precision" and "not a general impossibility" points.
- **R14c** (sec_method, sec:method-config): "which was built at seed~1" identifies the band whose per-bin standard deviation is the denominator of the printed 0.30. The writer's first reason ("prints only here in the body") was false: sec_validation.tex also prints the seed. The W1 review caught it, and the ledger gives the true reason.
- **R14f** (app_statmethods, audit row): without "Earlier statistical band", the 0.912 reads as the quoted block's coverage. The row is also a `\covTwoDCTwo` use.
- **R14g** (app_statmethods, standing assumption 3): a `\covTwoDCTwo` use, and its "has not been tested either" qualifies the assumption.
- **R16b** (sec_joint, tab:joint5d caption): the report-only disclosure of the recovered draws, beside the caption's B.
- **R21a** (sec_systematics): 1.13–1.23 for two named universes, against 1.08–1.36 for six at the home.
<!-- absence-ok: quotes or summarizes the note's own text, or a reviewer's or agy's reading of it, as this PR's record; not a new absence claim -->

Five were applied by the writers and reverted to base at integration, after the blind agy run (below) named them. Each was checked on the tree first.
- **R04a** (sec_method, configuration paragraph): the paragraph states each configuration's covariance status. A 3D/4D sentence that is silent about it reads as a statement too.
- **R04b** (sec_systematics lead) and **R04c** (sec_systematics, background-subtraction paragraph):
  - The pointer forms read as if a 3D or 4D budget, or 4D and extended-fiducial covariances, existed. W1's "For the 3D and 4D results, see §7" invites that reading in an uncertainty-budget paragraph.
  - Review NIT W1#10's "uncertainties" and "covariances", which I adopted, state it outright.
- **R14a** (sec_systematics, sec:uq-boot): the paragraph's third sentence, "Because the fixed-truth test's truth equals the prior, it also cannot decide …", needs this clause as its antecedent. The sentence is also a home of KI-85's statement, which the outline leaves untouched.
- **R10e** (selection_features caption): no home prints that PET design-study recovery does not validate real-data background subtraction. App. F says nothing from PET is used or claimed, and §1 that no result depends on it. The recount flagged the same sentence (below). The caption's other site, R12a, stays applied.

**KI-85.** R13b and R14e removed restatements of KI-85's statement in app_statmethods; the statement itself keeps its homes:
- sec_validation.tex §5.2;
- sec_systematics.tex sec:uq-boot, unchanged (R14a);
- the kept standing assumption 3 (R14g), "has not been tested either".
<!-- absence-ok: quotes or summarizes the note's own text, or a reviewer's or agy's reading of it, as this PR's record; not a new absence claim -->

## Process and accounts

- **Writers:** two Claude Opus 5.5 subagents of the claude-school session.
  - W1 wrote §2–§10.
  - W2 wrote Apps. A–H, then the executive summary, §1 and §12, against W1's body.
- **Reviewers:** one fresh two-direction reviewer per batch (Claude Opus 5.5 subagents): W1, W2's appendices, and W2's summaries. Each was read-only and had no other model.
- **agy:** gemini-3.8-flash-high through `register-method/tools/run_x.sh gemini`, on every changed passage (below).
- **Integration:** the main session.
  - It copied the writers' files and applied the review fixes. Each fix's words were checked against the base text and its home before it was applied.
  - It merged the ledgers and built `SITES.tsv`.
  - It patched the records-move ledger, ran agy, the gates and the recount, and wrote this report.

## Review fixes applied at integration

W1 review (body):
- **#1** sec_validation coverage row: "Predeclared coverage windows; earlier band fails (§5.2)". The base's "earlier band fails" is kept as the row's conclusion; only "Rebuilt band awaits independent test" is removed.
- **#2** sec_eavailw GiBUU ratios: "($E_\nu\approx\SI{20}{GeV}$ limit: §8.5)". This uses the base's own word, "limit", not the reviewer's "sample limit".
- **#3** sec_eavailw caption: the pointer to §7 for the $W$ deficit is dropped. §7 does not discuss the deficit, and its lead covers the no-mechanism statement for §8.
- **#4** sec_5d: "(status in the quoted uncertainties: §9.4)", the base's words.
- **#5** sec_5d: "(stability failure and the study's scope: …)".
- **#6** sec_joint roadmap: "(…; lost pseudo-experiments: §10.x)". The recovery is not read as part of the decisions.
- **#7** R14c: the KEEP reason is corrected (above).
- **#8** sec_3d: the pointer to the enclosing section is dropped.
- **#9** sec_3d `% Search:` line: re-run on the delivered tree. The line now names every printed source of the 3D/4D no-covariance statement:
  - sec_3d;
  - sec_method's configuration paragraph;
  - sec_systematics' lead and its background-subtraction paragraph;
  - the ES and §12 limitations paragraphs.

  The old line missed both summaries, which printed it at base too.
- **#10** "uncertainties" and "covariances" in sec_systematics: applied, then superseded. Both sites were reverted to base (R04b, R04c above).
- **#11** sec_5d Table 6 cell: the pointer to closure-map is added, so the four-observable closure's "no predeclared threshold" is reached too.
- **#12** R03b: the home probe re-pointed to the no-pulls sentence and the caption.

W2 review (appendices):
- **#1 (blocking)** app_negweight scope paragraph: "is stated in §3.1, and by configuration in §3.2 (Table 3)". §3.2 alone never names the extended-fiducial value. The R15c probe for §3.1's sentence is added.
- **#5** app_statmethods: the pointer to sec:uq-boot is added, where the test's truth-equals-prior limit is applied to these explanations. The R14e probe for that sentence is added.
- **#2:** the old source comment is left as history.
- **#3, #4:** recorded, with no text change (the KI-85 homes, above).

W2 review (summaries):
- **#1 (blocking)** ES "Principal limitations": "the absence of a 3D or 4D covariance (§7)". The writer's "the uncertainties of the 3D and 4D results" read as if such uncertainties existed.
- **#4** the base lead-in "; the principal ones are these" is restored, and the list opens "The others".
- **#3** two source comments that still said these facts are "restated" under Principal limitations now say they are named there with a pointer.
- **#2 (blocking for integration)** the records-move ledger (below).

## Gate inputs

**`records-move-ledger.md`** pins some posted sentences, and the consolidation changed three of them. The rows carry the same kind of "probe updated for …" note as earlier register passes.
- **L11 and L-thin-C55** (the §1 roadmap's five-axis row lost "and its four measured limitations", R05b): W2's drafted probe update.
- **L-con-R10** (new, REWRITE): the App. H PET reader paragraph (hash `dbf0faa3ea9a`) no longer prints verbatim (R10b).
- L13 and L-thin-C57 were patched for R04b and then returned to base when R04b was kept.

**`check_note_records.py` self-test.**
- The "edited reader paragraph" plant must edit a reader paragraph that still prints verbatim from the base. Its anchor was the App. H PET paragraph, which R10b rewrote.
- Of the 20 base reader paragraphs, the one still verbatim is app_release.tex's scope heading. The file is protected, so the plant moved there, with a comment. The bhi register pass made the same kind of move earlier.
- The self-test fires 41 of 41 plants.

## Checks (on the delivered tree)

| check | result |
|---|---|
| `check_ledger.py` (base 602ab31f) | ledger rows 56, probes 249, changed base sentences 64, failures 0 |
| `check_sites.py` with the ledger; `--self-test` | PASS (60 = 43 + 4 + 13); PASS (10 cases) |
| `printed_diff.py` on each scripted integration edit | review fixes: 12 printed sentences; ES stage-2 fixes: 2; guardrail reverts: 6; each OK, only the intended sentences |
| `reflow_tex.py --note --check` | PASS, 44 sources |
| `check_note_records.py probe` | RECORDS-MOVE PASS, 0 failures |
| `check_note_records.py --self-test`; `--self-test-pin`; `pin` | PASS (41 of 41); PASS (11 of 11); RECORDS-PIN PASS (pinned to 3c3a6f74) |
| `entry-numbers --check`; `--self-test-entry-numbers` | PASS (18 entries); PASS |
| `check_registry.py`; `--self-test` | PASS; PASS. Its two line-hint NOTEs predate this PR: sec_method.tex has the same lines 85–95 as base |
| `absence_claims.py` | run by the pre-commit hook on the staged lines |
| build (`build_all.sh`) | rc 0; 0 undefined references, no "??" in the PDF; SEC4 15/15; main_note 120 pp, paper 13 pp |
| pytest `test_check_sec4_receipts.py`; `test_build_all.py` | 16 passed; 81 passed |

## The recount

`recount.py` ports the cost list's measure, with paths as arguments. It reproduced the list's own figures at `e8c76937` exactly. Before is main `602ab31f` and its built note (`recount-before.*`); after is this tree and its built note (`recount-after.*`).

```
python3 recount.py docs/analysis-note docs/analysis-note/main_note.pdf \
  ../caveat-study/inv/ours-note-body.tsv ../caveat-study/inv/ours-note-app.tsv --json recount-after.json
```

| measure | before (602ab31f) | after | change |
|---|---:|---:|---:|
| TeX words (26 sources) | 48,904 | 48,384 | −520 |
| blinded PDF words | 52,558 | 52,045 | −513 |
| inventory quotes found / partial / gone | 662 / 227 / 78 | 637 / 235 / 95 | −25 / +8 / +17 |
| statements per 1,000 words (found; found + partial) | 12.60; 16.91 | 12.24; 16.75 | −0.36; −0.16 |
| distinct caveats (found; found + partial) | 373; 430 | 372; 430 | −1; 0 |
| distinct per 1,000 words (found; found + partial) | 7.10; 8.18 | 7.15; 8.26 | +0.05; +0.08 |
| restatements per caveat (found; found + partial) | 1.775; 2.067 | 1.712; 2.028 | −0.063; −0.039 |

**Words fell by 520, not the outline's about 1,285.** That figure was the sum of the `[C]` rows' sizes in the list. Three things account for the gap:
- 17 of the 60 sites were kept (13 by the guardrail, 4 by ruling 1);
- pointers replace text and carry words of their own;
- the review fixes restored words where a bare pointer was false or unclear.

**One distinct caveat lost its only matching quote** (found basis): 'fixed-truth test blind to prior bias'.
- Its one inventory quote was the removed app_statmethods clause.
- The fact prints at its home in §5.2, "Because $T$ equals the prior, it cannot detect regularization bias toward the prior", and in sec:uq-boot.
- The ledger probes for R14e pin both.
- It is counted as "partial", so the found + partial count is unchanged.

Before the reverts, a second pair, 'pet future work not used', had also lost its only quote. Its fact printed nowhere else, which led to the R10e KEEP above.

## agy

The prompt (`agy/prompt.md`) gives each changed paragraph BEFORE and AFTER, with the consolidation rules, and asks for AGREE or REVISE with an exact fix. The first run was void, and the blind runs that replaced it were checked against a control.

**The first run was void.** Its context carried the merged ledger: the disposition column, with the review fixes named, and probes holding the fixed sentences. It returned AGREE on all 45 passages with no reasons.
- A control rebuilt from the pre-fix tree, which still carried three defects the human reviewers had caught, was REVISEd on all three.
- But the fixes it gave repeated the ledger's words, so the context had handed over the answers.
- Neither result is evidence.

**The blind runs** use `agy/build_blind.py`. The context carries:
- each row's fact, with any review note removed;
- its home probes, each in its full paragraph of the tree under review;
- no disposition, no probe that the tree does not print, and no probe that is the passage's own text.

**The control (blind):** `agy/control.*`, on the pre-fix tree. It caught 1 of the 3 known defects, the sec_joint roadmap pointer that hung the lost draws on "the decisions". It missed:
- the ES's "the uncertainties of the 3D and 4D results";
- app_negweight's pointer to a home that does not name the extended-fiducial value.

agy has some power here, but less than the human reviews, and its silence is not a pass.

**Its flags on the delivered tree, and what was done:**

| run | passage | flag | disposition |
|---|---|---|---|
| g1 run 1 | sec_systematics:4, :302 (R04b, R04c) | the pointer topic asserts uncertainties/covariances that do not exist | **correct**: both KEEP (guardrail), reverted to base |
| g1 run 2 | selection_features:20 (R10e) | the specific PET fact prints at no home | **correct**: KEEP, reverted to base |
| g1 run 2 | sec_method:100 (R04a) | the covariance status is dropped from a per-configuration paragraph | **accepted**: KEEP, reverted to base |
| g1 run 2 | sec_systematics:53 (R14a) | "the fixed-truth test … also" loses its antecedent | **correct**: KEEP, reverted to base; agy's fix was the base sentence verbatim |
| g1 run 3 | sec_method:44 (R10a) | "(point-cloud representations: App. F)" drops "future work" | **not adopted**: "We use GBDTs for all unfolds in this note" excludes PET unfolds, and App. F's printed title begins "Future work" |
| g1 run 3 | sec_validation:18 (R14b) | the row drops "Rebuilt band awaits independent test" | **not adopted**: "earlier band fails" asserts nothing about the rebuilt band; §5.2 prints "the quoted block has not been tested"; the W1 review accepted this form |
| g2 | sec_3d:91 | `\S\ref{sec:closure-map}` should be a table reference | **wrong**: `sec:closure-map` is a subsection label (sec_validation.tex:55) |
| g3 | sec_5d:192 | the stability failure is in sec:val-negweight | **wrong**: the sentence is at sec_5d.tex:90, inside sec:val-departure (lines 71–100) |
| g4 | app_statmethods:468 | sec:uq-boot does not discuss the test | **wrong**: sec_systematics.tex:53, inside sec:uq-boot (lines 49–98), applies it; the ledger now pins that home |
| g5 | 10 passages (ES, §1, §12) | none | AGREE on all (second attempt; the first returned no output, an agy tool-permission error) |
<!-- absence-ok: quotes or summarizes the note's own text, or a reviewer's or agy's reading of it, as this PR's record; not a new absence claim -->

- Each g1 run, made after the previous run's flags were resolved, flagged different passages. The runs are not a stable list, and the loop was stopped after run 3 on the merits above.
- g2–g5 ran once, on their files' final text; the reverts touched only g1's files.
- All inputs and outputs are in `agy/`.

## Errors in this PR's process

- **The first site extraction missed 6 of the 60 `[C]` sites.** Its file-name pattern had no digits, and two bullet formats were dropped. I re-extracted the sites, told the writers and the director, and the director required `check_sites.py`. Its first version had two bugs, which its self-test now covers:
  - the split dropped the first row;
  - it counted every reference in a bullet as a site.
- **My first word estimate to the director, 1,500–2,000, was not a sum.** The sum of the `[C]` sizes is about 1,285, which I corrected in a message. The delivered fall is 520 (above).
- **I adopted review NIT W1#10 ("uncertainties", "covariances") without checking what the words assert.** They asserted objects that do not exist, the defect the stage-2 reviewer had just caught in the ES. The blind agy run found it, and both sites are now KEEP.
- **My first agy context leaked the fixes** (above), so that run was void.
- **Two other errors were corrected before any check ran on them:**
  - the ledger merge's first renumbering cascaded, moving W2 ids that did not collide; now W2's own ids are reserved, and only true collisions move;
  - my first agy context builder stripped TeX quote marks from the probes, so one home was "not found".
- **One blind batch used `declare -A`, which bash 3.2 here lacks,** so its five inputs were identical. They were rebuilt and run again.
<!-- absence-ok: quotes or summarizes the note's own text, or a reviewer's or agy's reading of it, as this PR's record; not a new absence claim -->

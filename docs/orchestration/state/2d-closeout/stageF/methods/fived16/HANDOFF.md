# Handoff: the 5D integration, the move of the non-final configurations and the measurement framing (paper rewrite lane, 2026-10-27)

**For:** a fresh session continuing the paper rewrite lane with no memory of this one.
**From:** the paper rewrite lane (Claude). The session was restarted by Joseph and the director because it was long.
**This is a working record.** It authorizes nothing. The decisions listed in §3 govern.

## 1. Role and standing rules

**Role.** You are the paper rewrite lane. You take direction from the director, the paper-tighten lane, a Claude session that messages you across sessions. Reply to it with SendMessage, never with terminal text. Joseph decides. The director relays and records his decisions as `docs/orchestration/DECISION-*.md`.

**Standing rules:**
- **Presentation only,** unless a decision rules otherwise.
- **No fact leaves both documents** (the paper and the companion note).
- **The guardrail.** A qualifier stays wherever leaving it out would make a printed sentence false as read. For every cut or shortening a rater proposes, state from the records whether the sentence stays true.
- **Never adopt a rater's rewrite without checking every fact in it.**
- **The wording is Joseph's.** So are the claims, KI-85, `\pubhold`, data availability, release text (`app_release.tex`), the abstracts' final text and the title.
  - You draft. Joseph approves.
  - Nothing is submitted, deposited or tagged. Write nothing to CFS. Contact no one, Ben included.
  - Do not push to the standalone note repository or to Overleaf.
- **Pushing to GitHub is not publication.** Branches, PRs and records on `github.com/josephbaileyy/MINERvA-OmniFold` are work in progress (DECISION-20261027-joseph-prd-review-route-push-and-public-github.md item 4).
- **Never write to the shared checkout** `/Users/josephbailey/local-research/MINERvA-OmniFold`. Work in a worktree under your scratchpad: `git worktree add <scratch>/wt-con stageF/fived16-integration-20261027`.
- **Git:**
  - `git add` with explicit paths only, and never `git stash`.
  - Commit identity: `git -c user.name='paper rewrite lane (Claude)' -c user.email='paper-rewrite@minerva-omnifold.invalid' commit`, with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  - PR bodies end with "🤖 Generated with [Claude Code](https://claude.com/claude-code)".
  - The director merges with merge commits, never squash, because the pinned commits 1a015eef and 3c3a6f74 must stay ancestors.
  - To update the branch, merge origin/main into it. Do not rebase. **Do not merge main yourself:** ask the director, who runs `merge_main.sh` and merges main before the final draft goes to Joseph (director, 2026-10-27).
- **The tree hook.** `bash .githooks/pre-commit` (19 checks) must pass before every commit. Run it on the staged index.
- **Every new `.md` under `docs/orchestration`** needs a CATALOG.md row and a MANIFEST-overrides.tsv row. Then, after `git add`, run `generate_manifest.py --committed-only` and `--check`.
- **Protected files.**
  - `values.tex`, `values_inference.tex`, `app_history.tex` and `app_release.tex` are byte-identical to the protected base.
  - `main_note.tex` and `main_paper.tex` may differ only by the approved `\input` lines (STRUCTURAL) and inside their abstract blocks (ABSTRACT_OPEN, the director's exception, 2026-10-27).
  - `check_ledger.py` enforces both, with plants. **The title is outside the abstract block, so it is not edited.**
- **Raters** run only through `register-method/tools/run_x.sh`:
  - `sol2` is gpt-6.1-sol via codex-school2;
  - `gemini` is agy gemini-3.8-flash-high.
  - The allowed delegation accounts are codex-school2, codex-school, claude-school and agy. **Never use the bare `codex`,** which is a personal account. Subagents of your own session are fine.
- **agy blind check.** Every new passage gets a blind agy check, with a planted-defect control that agy must catch. agy's measured blind spots are listed in §6.
- **Ask the director when anything is ambiguous,** rather than guessing.

## 2. State

**Branch:** `stageF/fived16-integration-20261027`, draft PR #413, pushed. The head is the commit that adds this file; see `git log -1`. The branch merges main through #417; main later received #419–#424 (decision records only).

**Done:**
1. **The 16-cell integration** (DECISION-20261027-joseph-5d-integration-then-second-scope-review.md item 2):
   - note §10 (`sec_fived16.tex`), with Table 13 (the correlation matrix) and Fig. 30 (the modes);
   - the paper's two subsections, `sec:result16` (V F) and `sec:gen16` (VII B), with Fig. 5 (the ratio);
   - product scoping across 15 files, and every number through `\fvval` (`values_fived16.tex`).
2. **The Q5 truth fix:** "the bias passes both criteria: no cell beyond 2σ and p ≥ 0.01".
3. **Round 1 of the PRD read and its application** (`prd-read/REPORT.md`):
   - Q3: (i) 24/24;
   - Q4: split, so the integers are kept;
   - the change table for 26 clauses, with sol2's true forms applied;
   - the accuracy fixes C06 and C08.
4. **The move of the non-final configurations to the note** (DECISION-20261027-joseph-move-nonfinal-configurations-to-note.md; records in `move/`):
   - the paper now shows only the two-observable estimator and the joint-test estimator;
   - the letters (a)–(f) print only in the note;
   - the independent review (`move/REVIEW.md`) found 0 MISSING, and its 3 blocking findings are fixed.
5. **The measurement framing drafts** (DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md item 1):
   - both abstracts (paper 204 words, note 349);
   - Sec. I, led by the result, with the three limitations as separate `\fvval` sentences in the paper's Sec. I;
   - in the abstracts, the three limitations were one semicolon sentence until round 3 (item 7);
   - the χ² range covers the external predictions only (109–272/16; GiBUU 58/8). Ledger row AB-EXT guards it.
6. **Gates** (at 7a6833b1): ledger 168 rows / 332 probes / 0 failures; `make_values_fived16 --check` and `--self-test` PASS; registry, results index and their self-tests PASS; build clean (paper 14 pp, note 129 pp).
7. **Round 3 applied, with the abstract limitation split** (§4 items 1 and 2; `prd-read/REPORT.md`, "Round 3"; `tools/apply_r3.py`; ledger rows `F-R3-*`):
   - sol2's true forms of P02, P11, P14, P15, P19 and P25. P14 and P15 keep the phrases that `check_sec4_receipts.py` binds. P02 keeps NEW's "the simulation mismodels the truth", because agy read sol2's wording as ambiguous;
   - kept as NEW: A and B (every sol2 form fails the truth column) and P05, P20 and P24 (sol2's two runs disagree);
   - in both abstracts, the limitation sentence is now three sentences, one per limitation, so that 1A and 3D can each replace one. Paper abstract 203 words, note abstract 348;
   - gates: ledger 175 rows / 352 probes / 0 failures; SEC4 15/15; reflow, swallowed-text, values, registry and results index PASS; build clean (14 pp, 129 pp); the new phrases checked in `main_paper.pdf`;
   - a blind agy check of the eight changed passages, with a planted control (caught): `prd-read/r3/agy/`. It found no false statement, and its one ambiguity finding (P02) is applied.

**PRD read status.**
- **Round 2** (abstract proposals, wording W1–W3, release R1–R4): 4/4 runs complete, in `prd-read/r2/`. The move superseded most of it. R1–R4 were accepted 4/4; W2 was denied 3 of 4. The note abstract at 635 words was too long 4/4.
- **Round 3** (the post-move and post-framing text: both abstracts, title options T0–T3, and 26 body pairs P01–P26): **4/4 runs complete** (sol2 r1 and r2, gemini r1 and r2), in `prd-read/r3/runs/`, tabulated in `prd-read/r3/runs/PR3-analysis.txt`.
  - No DENY anywhere.
  - P01, P03, P04, P06–P10, P12, P13, P16–P18, P21–P23 and P26: ACCEPT 4/4.
  - Splits: A, B, P02, P05, P11, P14, P15, P19, P20, P24 and P25. In each, sol2 says SHORTEN and gemini says ACCEPT.
  - Title: **T1 in 4/4.**
  - Paper abstract length: ACCEPTABLE 4/4. Note abstract: TOO-LONG 2/4 (sol2).
  - **The truth column and the application are done** (Done, item 7).

## 3. Governing decision records (`docs/orchestration/`)

**This lane's decisions:**
- #408: `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`. The integration, then the second scope review.
- #415: `DECISION-20261027-joseph-5d-wording-q2-q5-and-independent-prd-read.md`. Q2 no p-values; Q5 state the criteria; the independent PRD read.
- #417: `DECISION-20261027-joseph-prd-review-route-push-and-public-github.md`. The PRD sessions accept, deny or shorten before the final draft; public GitHub is not publication.
- #419: `DECISION-20261027-joseph-move-nonfinal-configurations-to-note.md`.
- #420: `DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md`.
- #423: `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md`. 1A, a GENIE v3 held-out bias test; 3D, a flux-correlation bootstrap that replaces α = 0.1; the fake-data bias stays a stated limitation.
- #424: `DECISION-20261027-joseph-f1-genie-v3-both-tunes.md`.
- #431: `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md`. F1 re-priced (option A, ceiling 2.5 node-h); the second scope review runs now, on #413; the structural round r19 runs before the final draft.
- `DECISION-20261025-joseph-register-rounds-paper-rewrite.md`, the rule r19 runs under: an outline the director approves before any writing; adopted at 3/4 pairwise, no sol2 order flip, P1 not falling; at most 4 rounds per document (r19 is the paper's third); no fact leaves both documents.

**Presentation decisions:**
- `DECISION-20261026-joseph-5d-generator-comparison-presentation.md` (option 1; no diagonal-only χ² printed);
- `DECISION-20261027-joseph-chi2-table-format.md` (χ² with ndf and shape-only);
- `DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` (the f0-limitation wording, "the reported uncertainty does not cover the fake-data bias at the GiBUU-like truths or at the q3 tilt");
- `DECISION-20261024-joseph-5d-community-standard-route.md` (coverage not required for publishing; κ = 1);
- `DECISION-20261024-joseph-h2-16-cell-definition.md`.

**Method record:** `../register-method/HANDOFF.md`, which covers the calibrated raters, the P1 and P2 prompts and the stop rule.

## 4. Open items, each with its next step

1. **The round-3 truth column, then apply.** **Done** (§2, Done item 7). The rule, as applied, with the two tie-breaks the lane added, is in `prd-read/REPORT.md`, "Round 3".
2. **Split the abstracts' limitation sentence** into three sentences in both abstracts (director, after #423). **Done** with item 1. The wording is otherwise unchanged; only the third sentence carries `\fvval` keys, because the other two hold no number.
3. **1A and 3D.** When the 5D measurement session reports:
   - **3D: drafted, 2026-10-28.** The readout is pinned (b7b5652c). The band sentences follow the kept α sentence in V A and in note §10.4 (c3d/apply_c3d.py, then apply_c3d_r4.py after PRD read r4 and agy; prd-read/REPORT.md "Round 4"). Replace-or-keep, the abstracts and Sec. I go to Joseph in (d).
   - **3D (flux bootstrap), as first planned:** replace the "weakening only the flux correlations by 10 %" sentences with the measured band. They print in the paper's sec:gen16, Sec. I's limitations paragraph and both abstracts; the note's are in sec_fived16 §10.4.
   - **1A: drafted, 2026-10-28.** The F1 readout is pinned (cbe411a9). The bias-test sentences are in Sec. I, both abstracts (drafts for (d)), IV H and note sec:fived16-fd, with Sec. I's fake-data pointer fixed to IV H (`c1a/apply_c1a.py`, `c1a/REPORT.md`; PRD read r5 and agy). The ledger rows are C1A-ALLOW, C1A-1 to C1A-6 and GC1–GC24 in `r19/ledger.md`.
   - **1A (GENIE v3 held-out bias test), as first planned:** revise the coverage limitation ("The coverage of its intervals has not been validated"; ledger guard G3, plus the abstracts and Sec. I) to what the readout supports. Name it as a bias test at the held-out truths, and never as validated coverage unless the readout says so.
   - **For both:** pin the new readout in `make_values_fived16.py` (READOUTS, by sha256), add keys, give the changed sentences a small PRD read of their own, add an agy check with a control, and update the ledger.
   - **P02 (director, ruling 3, after 0a87881c): done.** PRD reads r4 and r5 both gave ACCEPT ×3. agy read the printed pair in `c1a/agy/p02/`; its control was caught. It reads DIFFERS on two register changes that the raters accepted: "show how far the result can be trusted" becomes "assess the result", and "the background subtraction" becomes "background-subtraction tests". Neither strengthens anything, so they go to Joseph in (d) as reading notes, not edits.
4. **The final draft to Joseph,** after items 1–3 and 5 (r19): one draft with the change tables. **Assembled 2026-10-28** as `FINAL-DRAFT.md` (generated by `final-draft/make_final_draft.py`; the PDFs and the paper redline are in `final-draft/`), for the director to check and put to Joseph. #413 stays a draft PR until he approves.
   - **The title:** options T0–T3 are in `WORDING-PACKET.md` (last section). The raters chose T1 4/4. Not edited.
   - **Q8:** whether the release and the supplemental file carry the sixteen-cell vector and covariance. This is open and Joseph's. The data product is `measurement-paper/5d-community-20261024/fd/data-product/`.
   - **Data availability:** the proposal is in `WORDING-PACKET.md`, and the text is unedited.
   - **Both abstracts,** named in words, with their word counts (`tools/recount.py`). **The note abstract's length goes to Joseph as one item** (director, ruling 1, after 0a87881c): 348 words, sol2's "too long", and the fact that no rater form passed the truth column. Draft a shorter version only if he asks, because it would be new wording. (c) will change the length anyway.
   - **Sentence-level pieces of rater forms are declined** (director, ruling 2): a form is applied whole or not at all. A composite is an untested reading. Keep them out of the packet.
   - **Q6:** answered by the framing (the abstracts are drafts).
   - **Added by r19 and (c), 2026-10-28.** Each is unedited protected text or Joseph's call, so each goes to him as an item:
     - **stale protected text after variant B:** the abstract's "simulation-calibrated tests … all reject" sentence; Data Availability's "of the joint tests"; the title's "Performance and limitations"; and `app_release.tex:9`'s list of note figures "the article cites", which includes the joint tests' null distributions, which the article now reaches only through K8's pointer. `app_release.tex:29`'s "the article's Figs. 1–3" is still correct.
     - **O3** (director, after b2): put the paper's "We interpret the residual as regularization bias, because it persists over the tested iteration numbers and classifier capacities" beside the note's "No single cause is established". The base wording stands; any softening is his.
     - **Q4** (director): whether the final uncertainty accounts for the rounding instability. This is an open item, and r19 prints nothing new.
     - **The flux band (3D):** replace the α = 0.1 sentence, or keep both, as now. Also the abstracts' and Sec. I's flux sentence, which (c) left unchanged (prd-read/REPORT.md "Round 4").
     - **The deposit** (DECISION-20261028 result-table decision item 3): the paper's citation of the prepared package and the data-availability wording, as proposals. Nothing is deposited and no DOI or URL is cited.
     - **The register result, as measured:** P1 sol2 3, 3, 3 for the kept text (r19's), against the published anchors' 3.67. r19 won the pairwise 4 of 4; r20 was not adopted (2 of 4) and is reverted (`r20/REPORT.md`). The paper's register rounds are closed.
     - **Reading notes from gemini (r20's pairwise), for Joseph to judge by reading, not edits:** mixing spelled-out words and numerals ("Ten, 15 or 20"); the serial comma; "so it keeps five" as colloquial; "far upward" as an intensifier; a parenthetical nested in a semicolon (the Limitations lead). These are about r20's wording, which is not kept; the kept text's P1 quotes are in `r19/REPORT.md`.
     - **Data Availability's release-package sentence** (quoted by 2 of 3 P1 runs after r19), with both raters' readings: "not yet deposited" placed last, and the sentence split. It is protected text.
     - **Protected pointers:** fixed with the 1A sentence. Sec. I's fake-data pointer is now IV H (sec:fd16), as the director approved (b3 review S2; `c1a/REPORT.md`).
     - **The 1A sentences (c):** both abstracts' additions are drafts. The paper abstract goes from 203 to 228 words and the note abstract from 348 to 373. Sec. I says "Interval coverage has not been validated" (r5's form) where the abstracts say "The coverage of the intervals …"; whether to align them is Joseph's call (`c1a/REPORT.md`, "For Joseph"). A1, A2 and H1 print as composites, and PRD read r6 and its agy pass read them as printed (`prd-read/REPORT.md` "Round 6"). All stand. **H1 has an alternative for Joseph:** sol2 r2's r6 form (154 words against 164), which passed the truth column and agy. It goes beside the printed paragraph and does not replace it. A1/A2 have no alternative: sol2 r1's form failed agy, because its plural "bias tests" reads as independent tests.
     - **Beside the Sec. I sentence it qualifies** ("…finds the estimator's bias below the reported uncertainty in every cell…"), the reviewer's R11 observation (director, after 1bcccc38). At G18's R11, the −8.5 % bias stays below σ mainly through C_model's GiBUU vertex: |b|/σ is 0.62 in full, 0.93 without GiBUU and 1.07 with C_e + C_resp alone (`c1a/REPORT.md`). Say plainly that "the reported uncertainty" includes C_model, which the paper calls "not a calibrated bound".
   - **Q1, Q7, Q9:** settled by round 1 and the move.
5. **The second scope review, then register round r19** (#431; director, 2026-10-27). The order is: the director runs the scope review (gpt-6-astra high, read-only) on #413 now; when it reports, this lane writes the r19 outline and **holds it for the director's approval before any writing**; then r19; item 3 runs in parallel; then item 4.
   - **r19's aims:** a measurement paper's order (the seven PRD measurement papers of `register-prd-study` run intro, experiment and data, simulation, selection, extraction, systematics, results, comparisons, conclusions, in 5–8 sections), with the sixteen-cell result, now subsection V F, placed where they place a result and the validation studies as its support; Table I (no corpus paper has a table before Sec. 3, or a findings table): fold its content into the text or justify keeping it; and the passages the P1 re-score at a55e2686 quotes (VII C's design, budget and lost-pseudo-experiment sentences; V F's "not held-out truths" sentences; the joint-test estimator's rounding-instability sentence).
   - **If the scope review moves the joint tests to the note,** VII B–E stop being r19's problem. The move is Joseph's.
   - **The baseline** is built with `rater-calibration/make_rater_copy.sh`, after its case-4 fix (§6).
   - **Status:** the outline (`../r19/outline.md`, 12a65d89) is **approved** with the director's rulings Q1–Q6, recorded at its end. Table I is folded; A is built first; B and O1–O6 are with Joseph. The P1 baseline is sol2 3, 3, 3 on the corrected copy. Done: step 0 (9df8f748), the B ledger pass (569a13cd), b1 and N1-N4 (ac1508ec), then K1 and the scope guards G1-G20. Next: b2 (IV), b3 (V and the VI deletion), b4 (Discussion). **r19 is done and measured** (`r19/REPORT.md`): P2 4 of 4 with no order flip, P1 3, 3, 3; ADOPT under DECISION-20261025. The paper is standalone again (11 pp, 6 sections). r20, the fourth and last round, was **not adopted** (pairwise 2 of 4; `r20/REPORT.md`), and the paper's text is r19's. The paper's register rounds are closed. Final P1: 3, 3, 3, against the anchors' 3.67.
6. **Rulings given but not applied:**
   - the release scopings R1–R4, accepted 4/4 in round 2, go to Joseph as proposals only, because `app_release.tex` is protected.
   - Everything else the director ruled on is applied: Q5, the round-1 rules, the move, the coverage-test option (i), the abstract exception, the external-only χ² range, round 3 and the abstract limitation split.
<!-- absence-ok: states an open item and quotes the printed limitation to be revised; not a new absence claim -->

## 5. Files and tools

Paths are relative to the worktree root. `F = docs/orchestration/state/2d-closeout/stageF/methods/fived16`.

| what | path | run |
|---|---|---|
| the fact ledger and its checker | `F/ledger.md`, `F/check_ledger.py` | `python3 F/check_ledger.py . [--self-test]` (0 failures required; `--list` prints base sentence ids) |
| values generator: readouts pinned by sha256, the figure pins | `docs/analysis-note/make_values_fived16.py` | `python3 docs/analysis-note/make_values_fived16.py [--check\|--self-test]` (no flag: write `values_fived16.tex`) |
| word counts | `F/tools/recount.py` | `python3 F/tools/recount.py . --base 8b0f83fd` |
| printed wording (resolved) | `F/tools/packet_text.py` → `F/printed-wording.md` | `python3 F/tools/packet_text.py docs/analysis-note <base-copy> F/printed-wording.md`, where `<base-copy>` is `git archive 8b0f83fd docs/analysis-note` extracted to a scratch directory |
| edit scripts (exact old→new, asserting one match) | `F/tools/apply_final.py`, `apply_move.py`, `apply_framing.py`, `apply_r3.py` | records of the applied edits; copy the pattern, do not re-run them (each asserts its old text, so a re-run on the edited tree exits with "0 matches") |
| chapter and paper-block assembly | `F/tools/build_chapter.py`, `paper_blocks.py` | historical; the `.tex` is the source now |
| build | `docs/analysis-note/build_all.sh` | `cd docs/analysis-note && PAR_GLOBAL_TMPDIR=<scratch>/partmp bash build_all.sh` (≈5 min; it must end with "no pending placeholder"; build in the worktree, not with build_copy.sh, whose layout lacks the nd-unfolding readouts) |
| reflow | `docs/analysis-note/reflow_tex.py` | `python3 reflow_tex.py --note --check`; `python3 reflow_tex.py --check paper_body.tex main_paper.tex` |
| body pointers, records, Sec. IV receipts | `check_body_pointers.py`, `check_note_records.py`, `check_sec4_receipts.py` | `python3 check_body_pointers.py`; `python3 check_note_records.py probe records-inventory-base.json .`; `python3 check_sec4_receipts.py [--self-test]` |
| registry | `tools/registry/check_registry.py`, `results_index.py` | **they read the git INDEX:** `git add` the TSVs first. `check_registry.py [--repoint\|--cite FILE:LINE\|--self-test]`; `results_index.py --write`, then `git add` its 4 outputs; `results_index.py [--check\|--self-test]` |
| manifest | `docs/orchestration/generate_manifest.py` | after `git add`: `--committed-only`, then `git add MANIFEST.tsv`, then `--check` |
| raters | `F/../register-method/tools/run_x.sh` | `XMODEL_DIR=<scratch> bash run_x.sh sol2\|gemini <prompt> <out.md> <inputs…>`; at most 3 concurrent per model; smoke-test first ("Reply with exactly: OK"; check that the log says `model: gpt-6.1-sol`) |
| PRD-read rounds | `F/prd-read/` (round 1: REPORT, prompts, inputs, runs, tools; `r2/`, `r3/`) | the input builders `r3/tools/make_r3.py` and `r2/tools/make_r2.py` and the analyses `tools/analyze_*.py`, `r3/tools/analyze_r3.py` hold scratch paths: set `S=` at their top |
| agy Q5 check with its control | `F/prd-read/q5/` | — |
| move records | `F/move/` (`config-inventory.md`, `MOVE-OUTLINE.md`, `REVIEW.md`) | — |
| scope sites | `F/scope-sites.tsv` (178 rows: 33 FALSE-once-printed, 101 AMBIGUOUS, 44 FINE) | — |
| the packet for Joseph | `F/WORDING-PACKET.md`, `F/printed-wording.md`, `F/writer/abstract-proposals.md` | keep them current; Joseph reads them in the worktree |

**Left uncommitted on purpose** (all in the old scratchpad, reproducible):
- the base copy of `docs/analysis-note` at 8b0f83fd (`git archive`);
- the pre-move and pre-framing `.tex` copies, which equal commit `1f7f93da` (verified by `cmp`);
- rater `.log` and `.prompt` files (the full prompt plus input, duplicating the committed prompts and inputs);
- per-job input copies;
- the voided duplicate-pool sol2 outputs of round 1, never read;
- build logs.

## 6. Pitfalls met, one line each

- **Comment-swallowing edits:** an edit can push printed text into, or out of, a `%` comment. A cut that keeps "comment lines only" can orphan source notes. Check with `register-method/tools/swallowed_text.py`, and diff the printed text.
- **Estimated line numbers drift:** line numbers from an inventory or from memory go stale after any edit above them. Re-measure before citing, and cite by digest where the tools allow (`check_registry.py --cite`).
- **pdftotext anchors:** pdftotext breaks lines and hyphenates ("threemomentum"), so plants and probes on PDF text miss. Normalize whitespace and hyphens, or probe the comment-stripped source.
- **agy's scope blind spot:** agy misses group-scope overstatements ("all systematic correlations"; ledger guards G1 and G2). It drops limitations as "defensive disclaimers". It misread the fake-data study as held-out validation (round-1 C06). Never apply an agy form that drops a qualifier.
- **sol2's noise:** sol2's two replicates split on single items (round-1 C07; round-3 P05, P20, P24). Always use two runs per model (both orders for pairwise), and read agreement, not a single verdict.
- **agy hangs:** `run_x.sh` runs agy with `--print-timeout 0`, and agy can stay alive long after writing a complete answer (ending in END). Check the output, then kill only that agy PID. A retry loop treats the kill as a failure and relaunches, so stop the loop first.
- **Duplicate launches:** a second pool on the same output files races. Check `ps` before launching. Kill the whole process tree with `kill -9`, using bash for word splitting.
- **Rater copy, reference [1] inside the body (case 4):** on #413 at a55e2686, pdftotext emitted ref [1]'s first two lines inside Sec. VIII's last paragraph, so blinding (which cuts at '[1] ') dropped the end of VIII, the acknowledgments and Data Availability, and `fix_da_order.py`'s old fallback then put the DATA AVAILABILITY heading after its first sentence. Case 4 moves the fragment back to the rest of [1]; the fallback now fails on a layout no case describes; and `make_rater_copy.sh` checks that the section's first sentence survives blinding after its heading. The director's P1 re-score copy at a55e2686 lacks that sentence (16 words).
- **macOS has no `timeout`:** run a rater in the background and wait with an `until` loop on its output's END line.
- **Quoting:** unquoted heredocs substitute backticks and mangle backslashes. Use `<<'EOF'` for any text with LaTeX or backticks. zsh does not word-split `$var`.
- **Check-bound phrases:** `check_sec4_receipts.py` binds exact paper phrases ("reduces it to below", "within the quoted total uncertainty in about half of those cells") to receipts. Reword around them, not through them.
- **The registry reads the git index:** stage the TSVs before checking. Alias rows that cite moved paper lines must be re-cited, with `--cite` for the digest. The results-index fixtures follow their alias row's `source`.
- **The abstract range:** MINERvA Tune v1 is the unfolding's prior, not an independent prediction, so keep it out of any "predictions" count or range (AB-EXT).
- **The absence-claims lint covers rater outputs too:** verbatim rater outputs that quote limitation text fail the hook. The lane added `<!-- absence-ok: verbatim rater output … -->` lines after those paragraphs, in `prd-read/r2/runs/PR2__fwd__gemini.md` and `prd-read/r3/runs/PR3__r{1,2}__sol2.md`. Those lines are the only change to the raw outputs.

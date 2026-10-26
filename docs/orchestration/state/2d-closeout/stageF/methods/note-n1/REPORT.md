# Note register round n1: report (2026-10-26)

**Lane:** paper rewrite, for the director.

**Base:** the round was written on origin/main `ddf16f10` and moved to `5bb5e179` before its first commit. The 15
files it changes are byte-identical at both commits, so the ledger's sentence ids hold. The checker runs with
`--base 5bb5e179`, because PR #373 changed `main_paper.tex`, a protected file, in between.

**Brief:**
- the caveat study's note rules R-N1 to R-N7 (`caveat-study/REPORT.md` §5.2);
- register-prd-study R1 to R10;
- the note's sentence-level standard: a qualifier stays wherever leaving it out would make a printed sentence false;
- the director's rulings of 2026-10-25 and 2026-10-26, listed below.

**What this round is:** presentation and language only. No number, claim, scope, citation key, value macro, table
value, figure or caption meaning changes. The one exception is the second commit, "accuracy fixes (unscored)": factual
corrections of stale text, ruled by the director. See the last section.

**Outcome:**
- Adopted per piece: 11 of the 12 changed pieces. App. A (piece N11) is not adopted and keeps its base text.
- The note goes from 121 to 120 pages.

## Files

| file | records |
|---|---|
| `outline.md` | the approved outline (R-N1, R-N2, R-N5, R-N6 moves by chapter; the "not touched" list) |
| `ledger.md` | the fact ledger: 199 rows (190 register, ACC1–ACC9 accuracy), 510 probes, 157 changed base sentences named, 0 failures; App. A's rows under "Not adopted" |
| `changes.md` | every change paragraph by paragraph, the review fixes, n1-F, and what was not adopted |
| `check_ledger.py` | the ledger checker (probes; coverage of every changed base sentence; labels; protected files; SEC4 sites) |
| `REPORT.md` | this file |

Re-run the checks:

```
python3 -I docs/orchestration/state/2d-closeout/stageF/methods/note-n1/check_ledger.py . --base 5bb5e179
python3 -I docs/orchestration/state/2d-closeout/stageF/methods/note-n1/check_ledger.py . --base 5bb5e179 --self-test
```

## Batches

**Writers:**
- Five writer agents wrote batches n1-B, n1-C, n1-D and n1-E against the base. n1-A, the executive summary, §1 and §12,
  was written against the new body.
- n1-F is the director's addendum on process words. I wrote it.

| batch | files | moves |
|---|---|---|
| n1-B | sec_method, sec_systematics, sec_validation | the seven earlier-budget defects gathered into one §4.6 paragraph, "Changes from the earlier 2D budget" (director's ruling); the history of the two earlier statistical bands at one home, §5.2; process words |
| n1-C | sec_3d, sec_eavailw, sec_5d | a §7 lead stating once that the comparisons are central values without uncertainties and identify no mechanism; residual-bias home §9.3; miscoverage home §9.5; §9.6 status in plain words |
| n1-D | sec_joint, sec_fps | §10.3 the home of the pre-specification; "do not re-grade" becomes "These target-corrected evaluations are descriptive; the decisions of Table~\ref{tab:joint5d} are unchanged." (DECISION-20261020 line 37); §11 unchanged |
| n1-E | app_statmethods, app_statmethods_nd, app_negweight, app_response_mismatch | App. C's revisit stated once, as status, split by result, at sec:negweight-footing (director's ruling) |
| n1-F | sec_joint, app_negweight, app_statmethods_nd | "(corrected for audit finding J28)" dropped; "decision gate" becomes "decision rule"; two "predeclared" criteria stated; the §10.3 and §10.9 titles without "predeclared"/"recorded" (labels kept) |
| n1-A | sec_execsummary, sec_intro, sec_summary | one "Principal limitations" paragraph in the executive summary and in §12, one clause per home with a pointer; a §1 "Scope" paragraph as the single home of the note's scope; PET items gathered |

**Source words** (comment-stripped, words containing a letter or digit), for the round's files:

| file | before | after |
|---|---:|---:|
| sec_execsummary | 1532 | 1034 |
| sec_intro | 947 | 1033 |
| sec_summary | 1074 | 937 |
| sec_method | 2958 | 2956 |
| sec_systematics | 3972 | 3978 |
| sec_validation | 2770 | 2711 |
| sec_3d | 3785 | 3755 |
| sec_eavailw | 1874 | 1850 |
| sec_5d | 5075 | 5066 |
| sec_joint | 5533 | 5502 |
| sec_fps | 888 | 888 |
| app_statmethods_nd | 1909 | 1915 |
| app_negweight | 3284 | 3317 |
| app_response_mismatch | 396 | 407 |

## Review

Four two-direction reviews were run, each by a fresh reviewer working from the base and the brief:
- §3–§9;
- §10–§11 with App. A–D;
- the executive summary, §1 and §12;
- n1-F.

They found five BLOCKING problems: one in each of the first three reviews and two in n1-F. All are
fixed; `changes.md` lists each fix and its ledger row.
- **§4.2.** "No design … has been specified" was false: an unregistered draft design exists.
- **App. D.** A timing condition had been replaced by an independence condition.
- **Executive summary and §12** (one finding, printed at both sites). "The generator comparisons are
  descriptive" was not scoped. As printed, it covered §6.5's χ² and the calibrated joint tests.
- **n1-F, NF2.** The stated criterion called all 153 quantities "integrals".
- **n1-F, NF4.** "95% … bound" read as one-sided.

**Other checks:**
- **The plain-language invariance checker** (`plain-language/check_invariance.py`, not in build_all or CI) showed that
  n1-A had dropped the executive summary's `\covTwoDCTwo`. The outline protects that use, and check_dead_containment's
  comment counts four prints. It is restored, and the note again prints it four times.
- **agy agreement** on every changed passage, per file, with that file's ledger rows as context: AGREE on 64 of 64.
  - The only REVISE was an artifact of the passage builder, which read a comment-only line as a paragraph break. The
    builder was fixed and the file re-run.
- The executive summary was re-run after the `\covTwoDCTwo` restore: 4 of 4.

## Scoring

**P2N** is the blind pairwise comparison, note framing: both orders, sol2 (codex-school2) and gemini (agy). OLD is the
base pieces. A piece is adopted if NEW wins at least 3 of 4.

| piece | content | sol2 AB | sol2 BA | gemini AB | gemini BA | NEW wins | adopted |
|---|---|---|---|---|---|---:|---|
| N01 | abstract, executive summary, §1 (final text) | NEW 2 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N02 | §2, §3 | OLD 1 | NEW 1 | NEW 1 | NEW 1 | 3 | yes |
| N03 | §4 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N04 | §5 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N06 | §7 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N07 | §8 | NEW 1 | NEW 1 | OLD 2 | NEW 2 | 3 | yes |
| N08 | §9 | NEW 1 | NEW 1 | OLD 2 | NEW 2 | 3 | yes |
| N09 | §10 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N10b | §12 | NEW 2 | NEW 2 | NEW 2 | NEW 2 | 4 | yes |
| N11 | guide, App. A | OLD 1 | OLD 1 | NEW 1 | OLD 1 | 1 | **no** |
| N12 | App. B, App. C | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N13 | App. D–F | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |

**Pieces not scored:** N05 (§6) is byte-identical to the base. N10a (§11) and N14 (App. G, H) differ only in line
breaks and page numbers.

**N11.** Both sol2 runs preferred the base App. A sentences, which are shorter and sequential, and so did one gemini run.
`app_statmethods.tex` therefore keeps its base text. Its pointers into the changed chapters were re-checked against the
new body, and each lands on text that supports it:
- §4.1, PPFX effectively rank 1;
- §3 `sec:method-config`, the exact-split history;
- §4.5 `sec:uq-combine`, whose printed text is identical to the base;
- §5.2 and §5.3.

**P1N** is the per-piece rubric, scored on the final register text (before the accuracy commit, which is unscored).
- The rubric is `rater-calibration/prompts/P1N.prompt.txt`.
- Each piece gets 2 sol2 runs (codex-school2) and 1 gemini run (agy). The baseline is n1v2base, the same pieces at
  the base.
- sol2 hit its usage limit after 33 of the 45 runs. The remaining 12 sol2 runs (N10a–N14) were re-run after the reset
  on the same account and script. No account was switched.

**The adoption test** (director, 2026-10-26).
- It is sol2's: for each adopted piece, sol2's mean of 2 runs on the final text must not fall below its n1v2base
  mean. Any piece that falls reverts to base.
- Gemini is reported beside it and is not used to adopt.

| piece | sol2 base | sol2 final | Δ sol2 (mean) | gemini base | gemini final | adoption test |
|---|---|---|---:|---:|---:|---|
| N01 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2.5 | holds |
| N02 | 3, 3 | 3, 3 | +0.00 | 3 | 2.5 | holds |
| N03 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2 | holds |
| N04 | 3, 3 | 3, 3.5 | +0.25 | 2.5 | 2.5 | holds |
| N05 | 3.5, 3 | 3.5, 3.5 | +0.25 | 3 | 3 | not applicable (byte-identical to base) |
| N06 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2 | holds |
| N07 | 3.5, 3.5 | 3.5, 3.5 | +0.00 | 3 | 3 | holds |
| N08 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N09 | 3, 3 | 3, 3 | +0.00 | 2 | 2.5 | holds |
| N10a | 3, 3.5 | 3.5, 3.5 | +0.25 | 3 | 2.5 | not applicable (layout only) |
| N10b | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N11 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | not applicable (not adopted (= base)) |
| N12 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2 | holds |
| N13 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2 | holds |
| N14 | 3, 3.5 | 3, 3 | -0.25 | 2 | 2 | not applicable (layout only) |

**Result:** no adopted piece falls below base on sol2, so no piece reverts. The table is the output of `p1n_adopt.py <base p1n dir> <final p1n dir>`, run on the
rater outputs.

**Means over the 15 pieces:**
- sol2: base 3.083, final 3.117;
- gemini: base 2.467, final 2.300.

The only negative sol2 change is N14 (−0.25), which is layout-only and not a scored change.

**Gemini's six drops.** Gemini fell on N02, N03, N06, N10a, N12 and N13. Its stated reasons on the final text:
- **N02**: "Although the physics and technical methods are described with competence and rigor throughout most of the text, multiple sections—most acutely Sec. 3.2—lapse into an internal laboratory-notebook register characterized by software-debugging narratives, lost-log postmortems, calendar dates, and raw code expressions."
- **N03**: "The text frequently abandons publication register for that of an internal laboratory note or software audit, with multiple paragraphs dominated by record-keeping details—such as uncommitted code versions, checksum validations, runtime script assertions, and historical defect tracking—alongside pervasive defensive caveats."
- **N06**: "Although the underlying physics and mathematical foundations are competent, the text departs frequently into an internal-note and logbook register across nearly every subsection, characterized by raw codebase identifiers, workflow record-keeping, defensive hedging, and retrospective development narratives that require substantial rewriting for PRD."
- **N10a**: "While the underlying technical exposition is mathematically coherent and detailed, the text frequently slips into the register of an internal collaboration memo, characterized by development-history bookkeeping, defensive hedging, and unrefined jargon."
- **N12**: "While the core mathematical and statistical derivations are sound, substantial portions of the text frequently lapse into the register of an internal technical report or software audit log, dominated by defensive record-keeping, command-line flags, code-provenance tracking, and batch-run chronologies."
- **N13**: "While the literature survey and basic mathematical definitions are clear, the text frequently lapses into an internal analysis-notebook register characterized by software-implementation guardrails, project-management bookkeeping, informal jargon, and raw repository file paths."

Each reason names register: notebook or audit register, provenance bookkeeping, hedging, code identifiers. None
names a fact or an accuracy problem, so none goes to the director before adoption (director's rule).

**Calibration.** N10a's text equals the base apart from line breaks, and gemini still moved it from 3 to 2.5. Its
other drops are of the same size, so a 0.5 step from gemini is within its run-to-run noise on this rubric.

**Stop rule:** P2N no longer prefers NEW, or P1N ≥ 3.5, or 4 rounds. **Not met; the loop continues to n2.**
- P2N still prefers NEW on 11 of the 12 changed pieces.
- The sol2 P1N mean is 3.117. No adopted piece reaches 3.5 on both runs except N07, which was already at 3.5 in the base.
- This is round 1 of 4.

## Checks on the delivered tree

- **Ledger:** `check_ledger.py` gives 199 rows, 510 probes, 157 changed base sentences, 0 failures (the register round alone: 190, 487, 149). Its self-test passes:
  a missing probe, a dropped sentence and a removed label are each caught.
- **Protected files** are byte-identical to the base: values.tex, values_inference.tex, app_history.tex,
  app_release.tex, main_note.tex, main_paper.tex, paper_body.tex and main_records.tex. Every `\label` is kept.
- **Build:** `build_all.sh` exits 0.
  - Pages: note 120, paper 13, primer 15, PET note 26, records 55.
  - 0 undefined references or citations, and no `??`.
  - BODY-POINTERS PASS, RECORDS-PIN PASS, SEC4-RECEIPTS PASS (15/15), RESULT PASS.
- **`check_note_records.py`, every mode:**
  - probe: RECORDS-MOVE PASS, 0 failures. 14 probes were repointed across 15 rows of `records-move-ledger.md`
    (L-thin-C07, C12, C13, C31, C35–C38, C41, C48, C58, C60, C63, C70) to follow the new body wording.
  - --self-test: PASS, with 21 of 21 planted defects fired and 2 of 2 listed drops silent.
  - pin: PASS.
  - --self-test-pin: 9 of 9.
- **Tests outside build_all:**
  - `nd-unfolding/tests/test_hash_bindings.py`, `docs/analysis-note/test_build_all.py` and
    `docs/analysis-note/test_check_sec4_receipts.py` give 129 passed and 1 failed.
  - The failure (`test_a_wrong_printed_value_fails[\SI{97.7}{\percent}…]`) is on main and predates this round: r18
    moved the bound value, and the fixture still looks for it in paper_body.tex.
  - The director has assigned the fixture fix and a CI step to a separate PR.

## Not done in this round

- **The `rvp1pi` tracker row in the records** (`app_provenance.tex`) still points to §4.4. The Rvn1pi/Rvp1pi account now
  prints at §4.1 and §4.6.
  - The pointer edit fails `check_note_records.py probe` P5, which requires every base record paragraph to stay
    verbatim and has no escape.
  - Director's ruling 2026-10-26: the next PR adds R-EDIT ledger rows, limited to pointer tokens and with planted-defect
    self-tests, and applies this edit with its row. n1 leaves the records untouched.
- **Printed records tags.** The note prints 11 internal records tags after "Ref. [41]", among them `oi6-oi8-oi126`.
  Director's ruling: this is an n2 outline item, to propose citing records entries by number with a RECORDS-PIN check.
- **Executive-summary caveat count.** The outline's target was about 30 caveat statements in the executive summary and
  about 15 in §12. The writer counted about 54 and 37 after the round. Most of what remains qualifies a number printed
  in the same sentence, which the guardrail keeps, and 15 sit in Table 1's rows (`result_status_rows.tex`, not a round
  file). Reaching the targets would mean removing printed results, which is a content decision.
- **Table 1** (`result_status_rows.tex`) still prints "Tests specified in advance". That file was not in the round.

## Accuracy fixes (unscored; second commit)

**What these are.** Factual corrections of stale text, not register changes, ruled by the director on 2026-10-26.
They are flagged for Joseph. They are not scored. Ledger rows ACC1–ACC9 are at the end of `ledger.md`.

**The facts they restore.** The note's own scope statements (`sec_method.tex` sec:method-algo; `app_negweight.tex`
"Scope of the numbers") and the drivers agree:
- The 2D result and its covariance, and the 3D and 4D central values, use refined negative-weight subtraction. These
  are configurations (f) and (e).
- The 5D central value and its covariance, and the extended-fiducial value, use the binned purity weight.

**Mechanism, from the driver code at `ddf16f10`** (unchanged at `5bb5e179`):
- Both drivers take `--bkg-mode {purity, negweight, negweight-refined}`, default `purity`
  (`2d-unfolding/unfold_2d_omnifold_unbinned.py:1362-1377`; `nd-unfolding/unfold_nd_omnifold_unbinned.py:619-630`).
- `purity` down-weights the data per reconstructed bin.
- The negative-weight modes set the data to +1 and inject the background and the signal fakes at negative weight. In
  `negweight-refined` these are then refined to non-negative weights by Stay-Positive (`unfold_2d_omnifold_unbinned.py:1825-1870`,
  fakes at `:1846-1858`; `unfold_nd_omnifold_unbinned.py:900-1030`).
- The 2D driver's own help string still calls purity "default, headline". That is code, not printed text, so it is not
  changed here.

### The sweep

**Method.** `acc/sweep.py` reads every printed sentence in the `\input` closures of `main_note`, `main_paper` and
`main_primer`, with comments stripped. It keeps each sentence that matches any of these patterns:
- `purit`;
- `(D-B)/D`;
- "fixed before training";
- `default`;
- "binned correction/subtraction/weight";
- "reproduction measurement";
- "negative-weight";
- "refined";
- "background subtraction/treatment/removal";
- "do(es) not use it/the/this";
- "improved removal" (the primer).

Each hit was then classified by claim, not by wording. The question for each: does the sentence, as read, assign the
purity weight to the 2D result, its covariance or the 3D/4D central values, or misstate what treatment they use?

**Hits before the corrections** (`acc/sweep-before.tsv`): 220 sentences.
- **Note, 188:**
  - app_negweight 84, sec_method 31, sec_5d 10, sec_3d 9;
  - sec_validation 6, sec_joint 6, app_release 6, main_note 5;
  - sec_fps 4, sec_summary 4, app_statmethods 4;
  - sec_execsummary 3, sec_intro 3, sec_systematics 3, sec_results 3;
  - result_status_rows 2, app_guide 2;
  - values 1, selection_features 1, app_codebase 1.
- **Paper, 23:** paper_body 22, main_paper 1.
- **Primer, 9:** primer_body 9.

After the corrections there are 221 hits, because the §1 sentence became two (`acc/sweep-after.tsv`).

**Stale:** 9 note sites.
- 8 were found by the sweep: ACC1–ACC8.
- 1 (ACC9) was found by agy's review of ACC7, below.
- **Paper and primer: 0 stale.**
- A second screen ran after ACC9, for sentences that present the 2D treatment as a cross-check or alternative, or purity as
  the default or the headline. It found no further site.
- The nearest, `app_negweight.tex:31`, is kept. It reads "Here negative-weight injection is an equivalence study … this
  appendix establishes no supported production path and changes no default". It is scoped to the appendix, and the
  driver default is purity.

| id | where (after) | before → after |
|---|---|---|
| ACC1 | `sec_intro.tex:86` | "Background subtraction is the exception: a per-reco-bin $(D-B)/D$ purity weight is fixed before training" → two sentences: unbinned for the 2D result and its covariance and the 3D/4D central values (refined); purity for the 5D central value and covariance and the extended-fiducial value |
| ACC2 | `sec_method.tex:47-50` | heading "(the one binned step)" dropped; "In the binned purity subtraction, all selected data events enter step 1" |
| ACC3 | `sec_method.tex:355-357` | "Step 1 targets the purity-weighted background-subtracted data" → "the background-subtracted data …, purity-weighted or with background simulation injected at negative weight (refined to non-negative weights in the refined configurations)" |
| ACC4 | `sec_validation.tex:83` | "binning maps and purity correction held fixed" → "binning maps and background subtraction held fixed" |
| ACC5 | `app_negweight.tex:4` | "Background subtraction in §3.1 is the only step that uses analysis binning" → "Binned purity subtraction (§3.1) is the only step …" |
| ACC6 | `app_negweight.tex:192` | "reproduces the binned correction used for the results" → "reproduces the binned correction" |
| ACC7 | `app_negweight.tex:258-260` | "Binned purity remains the default for this note's reproduction measurement" → the scope sentence |
| ACC8 | `app_codebase.tex:21-23` | "applies purity-weight background subtraction" → "applies the background subtraction its background-mode option selects (by default the purity weight; §3.1)" |
| ACC9 | `app_negweight.tex:268-270` | "Negative-weight injection is the validated unbinned cross-check and designated extended-fiducial baseline …" → "Negative-weight injection is the designated extended-fiducial baseline …" |

**ACC9.**
- **The defect.** Beside ACC7's new sentence, "the validated unbinned cross-check" read as if the 2D result's treatment
  were only a cross-check. At base the sentence followed the stale "default" sentence, so the two formed one stale pair.
- **Why not option (b).** Option (b) would have kept the label as "unrefined injection is the validated cross-check".
  Table tab:estimators-matrix (`sec_method.tex:281-305`) rules it out:
  - (a), (b) and (c) are purity-based, and (b), the exact-split estimator, is the table's only cross-check;
  - (d), (e) and (f) use negative weights with refinement;
  - no negative-weight configuration has a cross-check role;
  - neither driver's `--bkg-mode` designates one;
  - the note never prints "unrefined".
- **The fix.** So the label is dropped rather than replaced by an invented role. The extended-fiducial clause and its
  binning-independence reason stay. The paragraph's first sentence carries the 2D support, unchanged: "support
  negative-weight injection as an unbinned alternative at the 2D scale" (`app_negweight.tex:255-257`).

### Two defects in my edit script, caught by agy

- In the first application, two replacements ended in a `%` comment line while the original sentence continued on the
  same source line. Its remainder became comment:
  - "Genuine backgrounds \emph{and}" in §3;
  - "Each data event in reconstructed" in App. C.
- `acc/apply_acc.py` now ends each such line. It also asserts that the printed text after the edits equals the printed
  text before them with exactly the edits' printed text swapped.
- `acc/guard-mutation.txt` shows the old behaviour, run in `--check` mode against the pre-correction sources, failing on
  both sites. The fixed script passes.

### agy agreement

All runs used gemini via `run_x.sh`, with the scope-correction prompt `acc/agy/ACC.prompt.txt`. The prompt asks, for
each passage, whether the BEFORE text was stale and whether the AFTER text satisfies:
- (a) agreement with the scope;
- (b) nothing else lost or added;
- (c) register.

Each run's full input and output is in `acc/agy/`.

| run | passages | context | verdicts |
|---|---|---|---|
| 1 | ACC1–8, first application | the two scope homes, quoted from the note; the driver mechanism | STALE: YES ×8. AGREE ×6. REVISE on ACC3 and ACC5: the two swallowed fragments (real; fixed) |
| 2 | ACC1–8, fixed application | as run 1 | STALE: YES ×8. AGREE ×6. REVISE on ACC1 and ACC7, on two false premises (below) |
| 3 | as run 2 | run 2 + two printed facts, quoted with file:line | STALE: YES ×8. AGREE ×7. REVISE on ACC7: the cross-check sentence, which became ACC9 |
| ACC9-1 | the ACC7/ACC9 paragraph | run 3 + the equivalence study's sentence (`app_negweight.tex:255-257`) and App. C's "equivalence study" sentence, verbatim; the table's configuration roles | REVISE: "designated extended-fiducial baseline" read as contradicting the purity-produced extended-fiducial value |
| ACC9-2 | as ACC9-1 | ACC9-1 + `sec_fps.tex:120-122` verbatim; one line address in the context corrected (`app_negweight.tex:31-34`, not 28-30) | STALE: YES. AGREE |

**Run 2's false premises, and the note's text that refutes them:**
- *"a nonexistent covariance for the 5D measurement"*. The note prints "The one five-dimensional covariance used in this
  note, with its $(\Eavail,W)$ projection, does not meet its specification" (`sec_execsummary.tex:157`). The covariance
  is built in the paper's sec:cov5d.
- *"the 3D and 4D uncertainties"*. The note prints "In three and four observables they use central values without
  uncertainties: no 3D or 4D covariance is quoted" (`sec_3d.tex:31-32`) and "No 4D uncertainty is reported."
  (`sec_3d.tex:521`).
<!-- absence-ok: quotes a rater's false premise in order to refute it with the note's printed text; the REPORT claims the opposite -->

**ACC9-1's premise.** It read "designated" as contradicting the extended-fiducial value's purity production. The note
prints both facts in one sentence: "The extended-fiducial value was produced with the binned purity correction, not with
the negative-weight treatment designated for the extended-fiducial analysis" (`sec_fps.tex:120-121`).

**How the context grew.** Each fact added was quoted verbatim from the note, with its file and line. No verdict or
instruction was added. The text changed only for run 1's two real defects and for ACC9.

### Erratum to the 2026-10-25 fix

`note-fixes/FIX-20261025-negweight-scope.md` said its sweep found the defect sentence as the only stale statement. That
sweep required a 2D or quoted-result term together with a negation, so it missed statements that made purity the
general method. An erratum line there points here.

### Checks

- **Ledger:** `check_ledger.py . --base 5bb5e179` gives 199 rows, 510 probes, 157 changed base sentences, 0 failures.
  VA-3's probe now reads "background subtraction held fixed".
- `apply_acc.py --check` gives OK on the pre-correction sources. The printed-text guard holds.

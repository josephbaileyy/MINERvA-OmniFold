# Round r17: restructuring the methods paper paragraph by paragraph (2026-10-25)

**Governed by** `DECISION-20261025-joseph-register-rounds-paper-rewrite.md` (model-scored register rounds that
restructure, reorder and rewrite paragraphs; the paper first). Written by the paper rewrite lane and sent to the
director, who merges. The round's records are here:
- `outline.md`: the reverse outline and the moves S1–S14 (S9 declined by the director);
- `ledger.md` and `check_ledger.py`: the fact ledger and its checker;
- `changes.md`: paragraph by paragraph, with the review fixes and the KEEP ids.

Base: origin/main `f0b26234`. Only `docs/analysis-note/paper_body.tex` changed in the paper. `main_paper.tex` (with
the abstract), the note, the primer and the PET note are unchanged. The rater-copy tool `fix_da_order.py` gains one
case (below).

## What changed

The paper was rewritten in four section batches, each from a reverse outline and a fact ledger: b1 Secs. I–III, b2
Secs. IV–V with the Fig. 3 caption, b3 Secs. VI–VII, and b4 Sec. VIII. The batches were spliced into one file. The
moves:

| move | where | change |
|---|---|---|
| S1 | I | The state of the art closes I ¶1. The roadmap is its own paragraph after the scope. |
| S2 | I ¶4 | Scope positive-first: what the findings cover; "a central value without intervals of validated coverage"; one negative sentence ("does not deliver a validated five-observable cross-section measurement"). The hybrid-null, recoil-response, FWER and "not physical exclusions … no measurement uncertainty" sentences are kept. |
| S3 | III ¶4 | Split into three: the shared settings; which configuration serves which result, with the 2D reproducibility sentence moved here from IV B; the fixed iteration criterion of (e). |
| S4 | IV A | Split: agreement; estimator dependence, with the post-selection disclosure next to the choice. |
| S5 | IV B | Reordered: the blocks; the statistical block as a test report; the run periods; C_model. |
| S6 | V A | Split into three: normalization; closure with backgrounds and the purity bias; the 2D closure. |
| S7 | V D | One pointer ("Sec. 9.6", not "Secs. 9.6 and 9.6"). |
| S8 | VI ¶2 | Split: the diagnostic's result; its population and scope. |
| S10 | VII C ¶3 | Reordered by R9: design fixed (with the reviewers' look); the budget extension at the choice; the error-control consequence; the lost draws and the rerun; recomputation. |
| S11 | VII D (ii) | Split: the omitted band and why it matters; the ±4% exploratory study. |
| S12 | VII E | One pointer pair ("Secs. 10.9 and 10.5", not "Secs. 10.9, 10.5, and 10.5"). |
| S13 | VIII A | The nine items as plain declaratives with one idea per sentence; the conditions verbatim. |
| S14 | Fig. 3 | The seed sentence in two sentences, same meaning. |

Elsewhere the batches made R10 splits and R7 pointer moves. Sentence counts and lengths, by batch:
- b2: printed prose sentences 73 → 91; mean length 25.8 → 20.9 words.
- b3: mean length 27.1 → 20.5 words; sentences of 35 words or more 26 → 10; semicolons 20 → 6.
- b4: VIII A sentences 17 → 24; mean length 22.1 → 16.4 words.

The printed rater copy grows from 9,192 to 9,297 words (+1.1%).

No number, claim, scope, citation key, value macro, table value, figure, caption meaning, `\label` or protected text
changed. Table I, the abstract, every `\pubhold` and the ten phrases bound by `check_sec4_receipts.py` print
byte-identical.

## Checks (on the committed text, `paper_body.tex` sha256 `711b3e91…`)

| check | result |
|---|---|
| `check_ledger.py --old-dir <f0b26234> --ledger ledger.md` | 317 rows, 368 probes, 95 changed sentences, **0 failures** |
| `check_ledger.py --self-test` | PASS (planted defects caught, including a MOVE→note row whose note text is absent) |
| `check_sec4_receipts.py` / `--self-test` | PASS (15/15) / PASS (18 perturbations rejected) |
| `tools/registry/absence_claims.py` (staged) | 0 bare absence claims in 318 added or changed lines |
| `tools/registry/check_registry.py` | PASS: 112 printed labels, each naming exactly one estimator |
| `swallowed_text.py <wt> f0b26234 paper_body.tex` | 0 flagged |
| full build (`build_all.sh`, scratch copy) | exit 0; note 121, primer 15, paper 13, PET note 26, records 55 pages; 0 undefined references in the paper; no `??` |

`check_ledger.py` is r16's checker with three changes: the base is `f0b26234`; `--old-dir` reads the base from a
directory; and self-test (b) plants a MOVE→note row (X2).

## Review: ADOPT-AFTER-FIXES in every batch, no BLOCKING finding

Each batch had an independent two-direction review: does the new text lose or add a fact or a condition, and does it
read in register? All findings and their dispositions are in `changes.md` ("Every review finding and its
disposition"):
- 11 fixed;
- 12 kept as written or not adopted, each with its reason;
- 3 raised to the director (b2-R1, b3-R1, b3-R2), which became the accuracy fixes below.

The findings that bear on accuracy:

- **b1-R1:** the scope sentence had lost "rather than of multidimensional OmniFold in general". It was restored,
  positive-first.
- **b1-R2 / b2-R6:** "is reproducible …, so its covariance …" let "so" cover reproducibility. It is now two sentences.
- **b3-R1:** the writer's "drawn from the source half" is wrong for the background, which is a Poisson draw from an
  independent half of the background sample. The text was reverted to the base's "drawn from it". The base's own
  antecedent invites the same misreading, so the fix goes in the separate accuracy commit (below).
- **b4-R1:** "We claim no coverage on …" could parse as a claim that coverage fails. It now reads "We make no coverage
  claim on …".
- **Raised to the director:**
  - **b2-R1:** IV B prints "failed the test" without the test's criterion;
  - **b3-R2:** the A2 clause, carried from r16.

  Both would add a fact, so they are outside this round. With b3-R1, the director approved them as unscored accuracy
  fixes, committed separately (below).

## agy agreement on every changed printed passage

- **Scope:** 19 changed units (sections or subsections), BEFORE and AFTER, with the prompt asking for an AGREE or a
  REVISE on meaning and register.
- **First pass:** 15 AGREE and 4 REVISE.
- **The four REVISEs**, each a false positive:
  - **U03 / U05:** the reproducibility sentence moved between the two units, so each looked like a lost or added
    fact.
  - **U05:**
    - a backslash that the passage extraction had dropped from `\cmodelIntegral`; the source has it;
    - "failed the test" read as stronger than the base's "undercovered", although Table I prints "an earlier band
      failed coverage".
  - **U09:** the V D pointer "dropped" a section that prints the same number (S7).
  - **U17:** the VII E pointer "dropped" the κ-scan label, whose paragraph is inside note Sec. 10.5 (S12).
- **Resolution:** each was resubmitted with the context (no text change), and each returned AGREE.
- **Final: 19 of 19 AGREE.**

## Blind pairwise comparison (P2, both orders, both models)

**NEW wins 4 of 4, with no order flip.**

| | revision | blinded copy sha256 | words |
|---|---|---|---|
| OLD | `f0b26234` | `00aaeeb4c846fe0d…` | 9,192 |
| NEW | this round | `a9ba20eb7f419680…` | 9,297 |

| model | order | winner | strength |
|---|---|---|---|
| sol2 | A = OLD, B = NEW | B (NEW) | 2 |
| sol2 | A = NEW, B = OLD | A (NEW) | 2 |
| gemini | A = OLD, B = NEW | B (NEW) | 2 |
| gemini | A = NEW, B = OLD | A (NEW) | 3 |

What the raters cite against OLD:
- overloaded sentences joined by semicolons;
- the paragraph organization of the covariance and estimator discussions;
- the duplicate pointers "Secs. 9.6 and 9.6" and "Secs. 10.9, 10.5, and 10.5";
- the trailing "that of the covariance of Sec. V D".

## P1 (absolute rubric score)

| rater | baseline (`f0b26234`) | r17 |
|---|---|---|
| sol2 (gates) | 3, 3, 3 | **3, 3, 3** |
| gemini (reported, does not gate; rater-calibration §4) | 2.5, 3, 2.5 | 2.5, 2.5, 2.5 |

The first sol2 attempt (13:32) hit codex-school2's usage limit on all three runs and produced no rating. The failed
logs are kept. On the director's ruling, the rerun after the reset used the same account and the same blinded copy,
with one attempt per run and no switch of account.

The rerun (14:16, codex-school2, blinded copy `a9ba20eb…`) gave 3, 3, 3. All three justifications name "repeated
qualifications, internal bookkeeping, and accounts of analysis development". The passages they quote are:
- **VII C, the design and the budget extension:** quoted by 3 of 3 runs.
- **IV B, the post hoc rescoring of the earlier band:** quoted by 3 of 3 runs.
- **VII E, "These target-corrected evaluations are descriptive. The decisions of Table IV … stand"**, with the
  multiplier scan: quoted by 2 of 3 runs.
- **III, the configuration paragraph** ("Each result below states which configuration …"; "The two-dimensional
  central value is reproducible. It is that of its systematic-universe ensemble …"): quoted by 1 of 3 runs. The
  paragraph is r17's S3 move.

The first two are r18's targets (`DECISION-20261025-joseph-r18-history-to-note.md`). Several of the raters' rewrites
change facts, so none is adopted. Two examples:
- "this extension preserves error control because the stopping rule is unrestricted" drops the A1 and A2
  condition's role;
- "a reconstructed version of another previously calculated uncertainty band" misstates which band was rebuilt.

## Adoption

Rule: the round is adopted only if (1) the pairwise prefers NEW in at least 3 of 4 runs, (2) sol2 shows no order
flip, and (3) P1 sol2 does not fall.

**Adopted.**
- (1) NEW wins 4 of 4.
- (2) sol2 picks NEW in both orders.
- (3) P1 sol2 is 3, 3, 3, against 3, 3, 3 at the baseline, so it did not fall.

**Stop rule:** not met. The pairwise still prefers the new version in both models, P1 sol2 is below 3.5, and this is
the first of at most four rounds. r18 follows, from r17 as merged.

## The rater-copy tool

`rater-calibration/tools/fix_da_order.py` gains a second case. The new layout made pdftotext emit the
acknowledgments' last block and the DATA AVAILABILITY heading ahead of the ACKNOWLEDGMENTS column. In that case the
tool moves the tail and the heading back, and it asserts that the order is acknowledgments, then the heading, then
the text. On the baseline text its output is byte-identical to before.

## The accuracy fixes (separate commit, not scored)

The director approved three fixes to pre-existing accuracy issues that the review found. They are committed after
this round's scored text, in their own commit, and r17's scores do not cover them. They are listed in the PR for
Joseph, and r18's baseline includes them.

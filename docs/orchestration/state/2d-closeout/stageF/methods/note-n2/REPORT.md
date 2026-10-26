# Note register round n2: report (2026-10-26)

**Lane:** paper rewrite, for the director.

**Base:** origin/main `be045af4`. The checker's default `--base` is `be045af4`. Main moved to `c6f96f97` (PR #387, Joseph's FPS decision record) during the round. That PR changes no note source; it adds its decision file and touches `CATALOG.md`, `MANIFEST-overrides.tsv` and `MANIFEST.tsv`, which this branch also changes, so main is merged in before the PR and the manifest is regenerated after the merge.

**Brief:** the approved n2 outline, with the director's rulings at its end (moves R-N2a to R-N2e, N2-1, Table 1, the caveat count, App. A's retry); the writer and reviewer briefs; the guardrail that a qualifier stays wherever leaving it out would make a printed sentence false.

**What this round is:** presentation and language only. No number, claim, scope, citation key, value macro, table value, figure or caption meaning changes. There are two exceptions, both outside the scoring rules: the accuracy fixes of `03e98d3d` (Joseph's FPS ruling and the director's), and N2-1, which changes how records citations print, not what they cite.

**Outcome:**
- **Adopted:** 11 of the 13 changed pieces. They are N01–N04, N06–N09, N10b, N11 and N13.
- **Not adopted, 2 pieces:**
  - **§11 (N10a)** lost P2N, 0 of 4.
  - **App. B and App. C (N12)** won P2N 4 of 4 but failed the P1N adoption test (sol2 −0.25).
  - Both are at base text, apart from the accuracy fixes and the N2-1 citation numbers.
- **The note** stays at 120 pages. Its records citations print entry numbers (R1.n) instead of internal tags.
- **Stop rule: not met; the loop continues to n3.** P2N still prefers NEW on 12 of 13 changed pieces. The sol2 P1N mean is 3.133, below 3.5. This was round 2 of 4.

## Accounts and models

| role | account | model |
|---|---|---|
| writers n2-A to n2-E, every reviewer, the caveat coder | Claude subagents of this claude-school session | Claude Opus 5.5 |
| integration, ledgers, checks, this report | the paper rewrite lane (claude-school) | Claude Opus 5.5 |
| sol2 (P2N, P1N) | codex-school2, through `register-method/tools/run_x.sh` | gpt-6.1-sol |
| gemini (P2N, P1N, agy agreement) | agy, through `run_x.sh` | gemini-3.8-flash-high |

No account was switched during the round. No bare `codex` was used.

## Files

| file | what it records |
|---|---|
| `RECORDS.md` | the records additions (first commit): six Section R1 entries, R1.n numbering, P9 |
| `N2-1.md` | N2-1: records entries cited by generated number; the machinery and the conversion |
| `ledger.md` | the fact ledger, one section per batch, plus ACC and N2-1. The "Not adopted" sections hold §11's and App. B/C's rows |
| `check_ledger.py` | the ledger checker: probes, coverage of every changed base sentence, labels, protected files, SEC4 sites |
| `printed_diff.py` | the standing guard for scripted edits: only the intended printed sentences change |
| `p1n_adopt.py` | the P1N adoption test for n2 (baseline: n1's final scores) |
| `acc-agy/`, `records-agy/`, `agy-runs/` | agy agreement inputs and outputs. In `agy-runs/n10a/`, the passage file holds run 2's text; run 1's output is `*.agy.run1.txt` |
| `caveat-count/` | the blinded ES and §12 excerpts, the coder's TSVs and the blinding key |
| `REPORT.md` | this file |

Re-run the checks:

```
python3 -I docs/orchestration/state/2d-closeout/stageF/methods/note-n2/check_ledger.py .
python3 -I docs/orchestration/state/2d-closeout/stageF/methods/note-n2/check_ledger.py --self-test .
python3 docs/analysis-note/check_note_records.py probe docs/analysis-note/records-inventory-base.json docs/analysis-note
python3 docs/analysis-note/check_note_records.py --self-test docs/analysis-note/records-inventory-base.json docs/analysis-note
python3 docs/orchestration/state/2d-closeout/stageF/methods/note-n2/printed_diff.py --dirs <base-dir> docs/analysis-note <files>
```

## Commits

| commit | what |
|---|---|
| `1a015eef` | records additions: six App. G entries, numbered R1.1–R1.17, and P9. **Pinned: never rewritten** |
| `d3e99de5` | NoteRecords2026 pinned to `1a015eef` |
| `624acea1` | N2-1 machinery |
| `7ad668f4` | prose batches n2-B to n2-E, with each batch's review fixes |
| `03e98d3d` | accuracy fixes ACC1–ACC6 (unscored) |
| `daa6899e` | N2-1 conversion: `\texttt{tag}` → `\recentry{tag}` |
| `0d9c64fd` | n2-A: executive summary, §1, §12, Table 1's \rsC cell |
| `d4a51c88` | §11 not adopted: base text with ACC1 and ACC2 |
| this commit | App. B and App. C not adopted: base text with Joseph's App. C sentence and the citation numbers; this report |

## Batches

Each batch had a writer and a fresh two-direction reviewer. Each reviewer worked from the base, the brief and the batch's ledger.

| batch | files | moves | review | agy |
|---|---|---|---|---|
| n2-B | sec_method, sec_systematics, sec_validation | R-N2a splits; R-N2b provenance cases (A) 2d-central-value and (C) july-sweep. (B), the exact-split seed, stays by ruling | 0 BLOCKING, 2 SHOULD-FIX, 3 NIT; ADOPT-AFTER-FIXES ×2, ADOPT ×1 | integrated run (below) |
| n2-C | sec_3d, sec_eavailw, sec_5d | R-N2a; R-N2c | 0 / 5 / 8; ADOPT-AFTER-FIXES ×2, ADOPT ×1 | integrated run |
| n2-D | sec_joint, sec_fps | R-N2a (the writer's count: sec_joint 166 → 258 sentences, sec_fps 35 → 49) | 0 / 5 / 7; sec_joint ADOPT-AFTER-FIXES, sec_fps ADOPT | integrated run |
| n2-E | App. A–D | R-N2e (App. A at sol2's six passages only); R-N2b in App. C | 0 / 1 / 1 (plus 2 for the director); App. C ADOPT-AFTER-FIXES, others ADOPT | integrated run |
| n2-A | sec_execsummary, sec_intro, sec_summary, result_status_rows (Table 1's \rsC only) | R-N2a, written last against the new body | 0 / 4 / 5, plus two flags on base text; ES and §12 ADOPT-AFTER-FIXES, §1 and Table 1 ADOPT | 6 of 6 AGREE (Table 1 cell included), then 5 of 5 after the fixes |
| records commit | app_provenance, main_records, check_note_records | six entries, R1.n, P9 | 1 BLOCKING (the committed MANIFEST listed an untracked file), fixed before the pin | `records-agy/` |

**The integrated agy run.** It covered every changed passage of n2-B to n2-E, each judged with its file's ledger rows as context: 57 of 57 AGREE, plus the §5.2 paragraph. The earlier per-batch agy runs are superseded by it.

**n2-A review fixes** (each checked against its home):
- Two splits had dropped the five-dimensional scope. The ES now says "The one five-dimensional coverage test", and §12 says "a deterministic five-dimensional estimator variant". The home is `sec_5d.tex:502-504`.
- §1: "differs from that study" and "we budget that component". §12: "a comparison across configurations".
- Corrections to Search lines and comments. A Search line on the tension misdescribed its homes. "No record of a threshold" was a source comment, not printed text.
- The §12 release paragraph is byte-identical to base, because release text is Joseph's. n2-A had already reverted its split but left a stale comment and Search line, which are now removed.
- printed_diff: the fixes changed exactly the 5 intended sentences.

**Table 1** (ruling 3). The \rsC cell "Tests specified in advance" became "Design fixed before any production pseudo-experiment or observed statistic, with two data-informed elements", which is its home's wording (`sec_joint.tex:256-258`). The status is unchanged and the \rsA..\rsD wrappers are intact. agy agrees. The RevTeX article builds; it no longer inputs this table (header of `result_status_rows.tex`: dropped on 2026-10-11).

**Source words** (comment-stripped, words containing a letter or digit), base → delivered:

| file | before | after |
|---|---:|---:|
| sec_execsummary | 1034 | 1074 |
| sec_intro | 1067 | 1078 |
| sec_summary | 937 | 950 |
| result_status_rows | 216 | 225 |
| sec_method | 2973 | 2966 |
| sec_systematics | 3978 | 3955 |
| sec_validation | 2711 | 2710 |
| sec_3d | 3755 | 3775 |
| sec_eavailw | 1850 | 1875 |
| sec_5d | 5066 | 5076 |
| sec_joint | 5502 | 5599 |
| sec_fps (not adopted) | 888 | 885 |
| app_statmethods (App. A) | 6502 | 6510 |
| app_statmethods_nd (App. B, not adopted) | 1915 | 1915 |
| app_negweight (App. C, not adopted) | 3335 | 3342 |
| app_response_mismatch (App. D) | 407 | 419 |
| app_provenance (records) | 1305 | 1570 |

Splitting adds subjects and connectives, so word counts rise slightly where R-N2a applies.

## Scoring

**P2N** is the blind pairwise comparison, note framing, in both orders, with sol2 and gemini.
- OLD is the note built at `be045af4`, which is n1's merged final text. NEW is the n2 build.
- A piece is adopted if NEW wins at least 3 of 4.
- The scored text includes the accuracy fixes ACC1–ACC6 (§11, App. C, App. D, sec_joint) and the N2-1 conversion, because they cannot be separated from the prose in the built PDF.

| piece | content | sol2 AB | sol2 BA | gemini AB | gemini BA | NEW wins | adopted | unscored changes inside |
|---|---|---|---|---|---|---:|---|---|
| N01 | abstract, ES, §1 | NEW 2 | NEW 2 | NEW 2 | OLD 2 | 3 | yes | — |
| N02 | §2, §3 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | N2-1 (2d-central-value) |
| N03 | §4 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | N2-1 (july-sweep, flux-index) |
| N04 | §5 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | N2-1 (2) |
| N06 | §7 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | N2-1 (flux-repair) |
| N07 | §8 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | — |
| N08 | §9 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | N2-1 (2) |
| N09 | §10 | NEW 1 | NEW 2 | OLD 2 | NEW 2 | 3 | yes | ACC4 (§10.9) |
| N10a | §11 | OLD 2 | OLD 1 | OLD 2 | OLD 2 | 0 | **no** | ACC1, ACC2 |
| N10b | §12 | NEW 2 | NEW 2 | NEW 2 | NEW 2 | 4 | yes | — |
| N11 | guide, App. A (R-N2e) | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | app_guide citation wording (N2-1) |
| N12 | App. B, App. C | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes, then failed P1N | ACC3, ACC6, N2-1 (5) |
| N13 | App. D–F | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes | ACC5 |

**Not scored:** N05 (§6) is byte-identical to the base. N14 (App. G, H) differs only in layout.

**R-N2e (App. A).** N11 now wins 4 of 4, against 1 of 4 in n1, so App. A stays in the loop.

**N10a (§11), not adopted.** All four reasons fault the R-N2a splits as choppy and repetitive. Three also name "the battery of 2026-06-10" as notebook register; that date is in the option Joseph selected. §11 returns to base text, except for ACC1 and ACC2 (below). The n2-D rows for §11 are under "Not adopted: §11" in `ledger.md`.

**P1N** is the per-piece rubric (`rater-calibration/prompts/P1N.prompt.txt`). Each piece gets 2 sol2 runs and 1 gemini run. The baseline is n1's final scores (outline, "Checks and scoring"). Every piece except N10a was scored on the text after n2-A and before the N12 revert; N10a was scored on its delivered text (base plus ACC1 and ACC2). No run failed and none hit a usage limit.

**The adoption test** is sol2's. For each adopted piece, sol2's mean of 2 runs must not fall below its baseline mean; a piece that falls reverts to base. Gemini is reported beside it and is not used. The table is the output of `p1n_adopt.py`.

| piece | sol2 base | sol2 final | Δ sol2 (mean) | gemini base | gemini final | adoption test |
|---|---|---|---:|---:|---:|---|
| N01 | 3, 3 | 3, 3 | +0.00 | 2.5 | 3 | holds |
| N02 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2.5 | holds |
| N03 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N04 | 3, 3.5 | 3.5, 3.5 | +0.25 | 2.5 | 3 | holds |
| N05 | 3.5, 3.5 | 3, 3.5 | −0.25 | 3 | 3 | not applicable (byte-identical to base) |
| N06 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N07 | 3.5, 3.5 | 3.5, 3.5 | +0.00 | 3 | 3 | holds |
| N08 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N09 | 3, 3 | 3, 3 | +0.00 | 2.5 | 2 | holds |
| N10a | 3.5, 3.5 | 3.5, 3 | −0.25 | 2.5 | 2.5 | not applicable (not adopted: base + ACC1, ACC2) |
| N10b | 3, 3 | 3.5, 3.5 | +0.50 | 2 | 2.5 | holds |
| N11 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N12 | 3, 3 | 2.5, 3 | −0.25 | 2 | 2.5 | **fails: reverts to base** |
| N13 | 3, 3 | 3, 3 | +0.00 | 2 | 2 | holds |
| N14 | 3, 3 | 3.5, 3 | +0.25 | 2 | 2 | not applicable (layout only) |

**Means over the 15 pieces:** sol2 3.117 → 3.133; gemini 2.300 → 2.400.

**N12, not adopted.**
- sol2's reasons name register only, not a fact. Run 1 (2.5) gives "recurrent production bookkeeping, development history, repeated scope disclaimers, and conversational judgments".
- It was not re-rated. Re-rating until a piece passes would make the test meaningless, and the rule as written decides it (director, ruling (a)).
- App. B and App. C return to base text. Kept:
  - Joseph's App. C sentence (ACC3);
  - the N2-1 numbers of the four base citations (rank-inversion, negweight-hpss, oi6-oi8-oi126, fps-battery).
- Reverted with the prose:
  - the fps-battery move (ACC6). It is an R-N2b register move, even though it was committed with the accuracy fixes; its records copy stays, bound by its records-move-ledger row;
  - App. C's bkg-mode-elimination citation, which came with n2-E's move C3;
  - the n2-E review fix at App. C :290-294. Its one-test classification: it repaired referents that n2-E's own move C3 had removed, so it was not a correction of false base text.
- After the revert:
  - printed_diff against base shows only Joseph's sentence and the four R1.n citations;
  - agy on the App. C accuracy site in its base context: AGREE;
  - the n2-E rows for App. B and App. C are under "Not adopted: App. B … and App. C" in `ledger.md`;
  - three records-move-ledger rows (L15, L-thin-C04, L-thin-C06) return to their base probes, with the negweight-hpss citation in its numbered form.
- P1N on the reverted N12, recorded as information (it does not reopen adoption): sol2 3, 2.5 (mean 2.75, the same as the n2 text's); gemini 2. The base-text N12 scores no higher on sol2 than the text that failed.

**Calibration.** sol2 moved ±0.25 on text that did not change: N05 (byte-identical) and N14 (layout only), and in n1 also N05, N10a and N14. That is the size of the step that failed N12. See "For n3".

**The caveat count** (ruling 4: the numeric target is dropped as a gate, and the guardrail decides). The count is still reported.
- **Method:** one coder (a Claude Opus 5.5 subagent) applied the caveat study's `CODEBOOK.md` to the extracted ES and §12 text, base and n2. The files were blinded as X and Y in shuffled order; the key is `caveat-count/blind_key.json`. Every one of the 209 quotes is a mechanically verified substring of its file.

| excerpt | words | caveat statements | per 1,000 words | distinct issues | per 1,000 words |
|---|---:|---:|---:|---:|---:|
| ES, base | 1,260 | 58 | 46.0 | 35 | 27.8 |
| ES, n2 | 1,309 | 71 | 54.2 | 42 | 32.1 |
| §12, base | 950 | 36 | 37.9 | 32 | 33.7 |
| §12, n2 | 963 | 44 | 45.7 | 35 | 36.3 |

- **The rise is mostly a counting effect of R-N2a, not more caveats.** The codebook counts one row per sentence. The coder noted that a semicolon-joined sentence holding two caveats of one kind yields one row, while the same caveats split yield two. n1's writer estimate for the base was about 54 and 37.
- **Comparator range** (caveat study `REPORT.md` §3.1, all kinds per 1,000 words): long documents 2.1–4.8, PRD papers 2.4–7.8.
  - Those are whole-document rates. These excerpts are the two summaries, where a note concentrates its limitations, so the comparison is not like for like.
  - The study's measured gap for the whole note (all caveats 18.2 per 1,000 words against 2.1–4.8; distinct caveats 8.4 against 1.6–2.5, R-N7) is a content matter for Joseph, not something a register round can close.

## Accuracy fixes (unscored) and rulings during the round

**ACC1–ACC6** (`03e98d3d`), and their state after the not-adopted pieces:
- **ACC1 (§11).** "No covariance is quoted for it, so the result consists of central values and these validation tests." This is Joseph's choice as the director applied it to a third site.
- **ACC2 (§11)**, final form (the director's ruling (c)): "The extended-fiducial central value was produced with the binned purity correction (the battery of 2026-06-10), not with refined negative-weight subtraction, the treatment designated for the extended-fiducial analysis (App.~\ref{app:negweight})."
  - The base sentence's designation fact is kept. App. C designates negative-weight injection with Stay-Positive refinement (`app_negweight.tex:370-371`), the refined form (`:257-258`, `:476`).
  - agy history: a semicolon join, REVISE; the `03e98d3d` two-sentence text in base context, REVISE; the single sentence, AGREE. Both REVISEs were register only. Their fix, Joseph's option verbatim, would have dropped the designation fact.
- **ACC3 (App. C).** Joseph's sentence, now in App. C's base paragraph. agy AGREE.
- **ACC4 (§10.9)** and **ACC5 (App. D)**: unchanged; N09 and N13 are adopted.
- **ACC6 (the fps-battery move)**: reverted with N12, as above.
- **A miss of mine.** Item 1.3 of Joseph's FPS decision keeps §11's "no extended-domain covariance has been constructed with re-selected lateral bands under the procedure of §4.5", which is true as scoped, with a Search line. `03e98d3d` did not add that Search line. It was added with the §11 revert (`d4a51c88`) as a comment, citing:
  - the activelat FPS covariance of job 56431823 (`AUDIT-FINDINGS-20260820-fps.md:217-221`);
  - C_PL's adoption (`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`);
  - `AGENTS.md:36`.

**n2-A's two flags on base text** (director's rulings):
- **(B) "The rejections are not physical exclusions": stays.** It is an interpretive limit on the joint tests' rejections. Its body support is `sec_joint.tex:821-824`, and the abstract (`main_note.tex:123`) and §12 (`sec_summary.tex:37`) print it.
- **(A) "Its source has not been identified" (ES, `paper_body.tex:408`, `primer_body.tex:253`): stays at all three sites, and is not sent to Joseph.** By the note's own numbers its referent, the quoted 2.27 distance, has no attributed source:
  - the about-one-unit attribution (`sec_results.tex:245-250`; `app_statmethods.tex:1022-1029`) is the 0.96 gap between the exact-split cross-check's 3.66 and the histogram backends' 2.65–2.70;
  - the 2.65 → 2.27 step is attributed to the refined subtraction;
  - nothing attributes the remaining 2.27. The diagonal-only value is 0.29 (`sec_results.tex:224-225`), and the 73 best-measured directions give 0.66 (`:235`).
  - The appendix conclusion (`app_statmethods.tex:1033-1041`) locates the difference but names no source.
- **Considered and rejected:** "Part of it is attributed to …; the source of the rest has not been identified". That would be false for the quoted value.

## My errors in this round

- **A wrong absence claim to the director.** I said "No corrected covariance exists for it" printed nowhere. It prints at `sec_fps.tex:8-9`, and my search had missed it because it did not catch the pronoun. Corrected in correspondence.
- **Two factual errors in proposals, both corrected:**
  - I said the fps-battery record lacked "purity default"; it has it in other words.
  - I proposed filing (B), the exact-split seed, under 2d-central-value. (B) stays in the note, by ruling.
- **`7ad668f4` broke the C62 self-test plant.** I committed it after running the probe but not `--self-test`. Fixed in `daa6899e` (`N2-1.md`).
- **The comment-swallow hazard hit me three times.** Twice in TeX (sec_joint's "The hydrogen fraction is", App. C's "The") and once in a Python inline comment in `check_note_records.py`. The ledger's coverage check caught each one. `printed_diff.py` is now the standing guard.
- **Estimated line numbers.** My first message on flag (A) quoted several line ranges I had estimated from memory of the file, and a later one gave one more wrong address (the battery is named at `app_negweight.tex:354`). Both were corrected after `grep -n`.
- **A near miss with running scorers.** I launched a rebuild chain whose last step would have deleted the P2N input directory while scorers were still reading it. I stopped it before that step and re-routed the output to a new directory; no score was affected.
- **The missing Search line** of decision item 1.3, above.
- **Reported by writers, corrected at integration:**
  - n2-B claimed §5.2's single-toy sentence had a semicolon. It has none, so only the attribution-rule split was made (row VA-X1).
  - n2-D's writer added two Search lines on the FPS sentences that were false. I dropped both before integration.
  - Reviewers found source comments (J36's and four in App. A) that still cite pre-RE-2 values while the text prints RE-2's refined values. The four App. A comments were corrected in `03e98d3d`. The J36 comments are left for n3.

## Checks on the delivered tree

- **Ledger:** `check_ledger.py` reports 202 rows, 461 probes, 198 changed base sentences, 0 failures. Its self-test passes.
- **Records:**
  - `check_note_records.py probe`: RECORDS-MOVE PASS.
  - `--self-test`: 35 of 35 planted defects fired; 3 of 3 listed drops stayed silent.
  - `pin` and `--self-test-pin`: PASS.
  - entry-numbers `--check` and `--check-aux`: PASS.
- **Build:** `build_all.sh` exits 0.
  - Pages: note 120, paper 13, primer 15, PET note 26, records 56.
  - 0 undefined references or citations, and no `??`.
  - BODY-POINTERS, RECORDS-PIN (12 tags, all by number), ENTRY-NUMBERS(-AUX), SEC4-RECEIPTS (15/15) and RESULT all PASS.
- **Protected files** are byte-identical to the base: values.tex, values_inference.tex, app_history.tex, app_release.tex, main_note.tex, main_paper.tex and paper_body.tex. Every `\label` is kept.

## For n3

- **Outline items (director's rulings):**
  - App. C `app_negweight.tex:361-363` → "…, not with refined negative-weight subtraction, the intended extended-fiducial baseline". The surviving homes of the injection designation are `:268-269` and `:370-371`.
  - `app_statmethods.tex:1029`: scope "∼1 χ²-unit of the tension" to its referent, the exact-split cross-check's tension. Check it against `:1022-1028` first.
- **A proposal for the director: a noise floor in the P1 adoption test.**
  - sol2 rates on a 0.5 grid, so a 2-run mean moves in 0.25 steps.
  - Within a piece, run 1 and run 2 differ by 0.5 in 8 of 45 pairs (n1 base, n1 final, n2 final), and agree in the other 37. That gives a single-run SD of about 0.15, and about 0.15 for the difference of two 2-run means.
  - On text that did not change, the 2-run mean moved +0.25, +0.25, −0.25 and 0.00 in n1 (N05, N10a, N14, N11), and −0.25 and +0.25 in n2 (N05, N14). The SD is 0.22, and the largest move is 0.25.
  - Proposal: a piece reverts only if its sol2 mean falls by more than 0.25, that is by 0.5 or more. Alternatively, the test could use 4 runs per piece, which would halve the variance of the mean. The director decides before n3 scores anything.
- **Order:** do not branch n3 until the director's reflow PR lands on main after this PR merges.

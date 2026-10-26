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
| `ledger.md` | the fact ledger: 190 rows, 487 probes, 149 changed base sentences named, 0 failures; App. A's rows under "Not adopted" |
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

**P1N** is the per-piece rubric. On the final pieces, with 2 sol2 runs and 1 gemini run each:
(pending: added in the round's last commit, once every run is complete)

**Stop rule:** P2N no longer prefers NEW, or P1N ≥ 3.5, or 4 rounds. (pending, with P1N)

## Checks on the delivered tree

- **Ledger:** `check_ledger.py` gives 190 rows, 487 probes, 149 changed base sentences, 0 failures. Its self-test passes:
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

(pending: the second commit)

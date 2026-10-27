# Note register round n3: report (2026-10-27)

**Lane:** paper rewrite, for the director.

**Base:** origin/main `0d919b1a`, which is n2 merged and reflowed (#396). During the round, main gained:
- the comparator check (#398);
- the absence audit (#400), which changed the ES sentence "the one … coverage test" (ACC-A2), `paper_body.tex`, the primer and comments;
- absence-audit items 3 and 4 (#402), which changed §8's pT-convention sentence and App. history's PSD sentence (R-FIX-1);
- Joseph's decisions (#401, #403).

main is merged into this branch at `4da481d7` and `5a767822`. n3's printed text is unchanged by those merges: printed_diff gives 0 lines on the overlapping files. Ledger rows AUD-1 and AUD-2 cover the two main-side sentences in n3's files.

**Brief:** the approved n3 outline with the director's rulings (`outline.md`); the writer and reviewer briefs; the guardrail that a qualifier stays wherever leaving it out would make a printed sentence false.

**What this round is:** presentation and language only. No number, claim, scope, citation key, value macro, table value, figure or caption meaning changes. The exceptions are unscored accuracy fixes, each ruled by the director:
- ACC-n3-1 to 3, the production iteration count scoped to the exact-split cross-check;
- App. A's "∼1 χ²-unit of the exact-split cross-check's tension";
- comment corrections (rulings (c), (d)).

**Outcome:**
- **Adopted: 7 of the 12 changed pieces.** They are N02, N03, N06, N08, N09, N11 and N12. N12 is App. B and App. C, n2-E's text re-proposed, which this time passes both tests.
- **Not adopted on P2N:** N07 (§8), and N01 and N10b (the ES, §1 and §12).
- **Not adopted on P1N** under the director's noise rule: N04 (§5) and N13 (App. D).
- The note is 121 pages. The extra page comes from the audit's longer ES sentence, which is on main.
- **The stop rule is not met.** P2N still prefers NEW on 9 of 12 changed pieces. The sol2 P1N mean is 3.133 before and after the round, below 3.5. This is round 3 of 4.
- **The costed content-reduction list for Joseph is in `content-reduction.md`.** Its headline: register work and consolidation cannot reach the comparator range. Only removing secondary results together with their qualifiers can.

## Accounts and models

| role | account | model |
|---|---|---|
| writers n3-A to n3-E, every reviewer, the content-reduction list | Claude subagents of this claude-school session | Claude Opus 5.5 |
| integration, ledgers, checks, this report | the paper rewrite lane (claude-school) | Claude Opus 5.5 |
| sol2 (P2N, P1N) | codex-school2, through `register-method/tools/run_x.sh` | gpt-6.1-sol |
| gemini (P2N, P1N, agy) | agy, through `run_x.sh` | gemini-3.8-flash-high |

No account was switched. sol2 hit codex-school2's usage limit during the body P2N; those runs were repeated on the same account after the reset.

## Files

| file | records |
|---|---|
| `outline.md` | the approved outline and the director's rulings |
| `ledger.md` | the fact ledger: one section per batch, then integration fixes and history removals, then the "Not adopted" sections and AUD-1/2 |
| `check_ledger.py` | n2's checker with base `0d919b1a`. Protected files are compared with the merge base of HEAD and origin/main (`--protected-base`), because #400 changed two of them on main |
| `printed_diff.py` | the standing scripted-edit guard |
| `sol2-quotes-located.tsv` | sol2's quoted passages on n2's delivered text, located at `0d919b1a` |
| `agy-runs/` | agy's inputs and outputs: integrated (41 passages), acc and acc2 (the item (a) fixes) |
| `content-reduction.md` | the costed content-reduction list for Joseph (director's ruling 4) |
| `REPORT.md` | this file |

```
python3 -I docs/orchestration/state/2d-closeout/stageF/methods/note-n3/check_ledger.py .
python3 -I docs/orchestration/state/2d-closeout/stageF/methods/note-n3/check_ledger.py --self-test .
```

## Batches and reviews

| batch | files | review (BLOCKING / SHOULD-FIX / NIT) | verdicts |
|---|---|---|---|
| n3-B | sec_method, sec_systematics, sec_validation | 1 / 1 / 4, plus 1 for the director | sec_method ADOPT-AFTER-FIXES; the other two ADOPT |
| n3-C | sec_3d, sec_eavailw, sec_5d | 0 / 3 / 4 | sec_eavailw ADOPT-AFTER-FIXES; sec_3d, sec_5d ADOPT |
| n3-D | sec_joint | 0 / 1 / 4 | ADOPT-AFTER-FIXES |
| n3-E | App. A–D (App. B, C: n2-E re-proposed) | 0 / 4 / 4 | App. A, C ADOPT-AFTER-FIXES; App. B, D ADOPT |
| n3-A | ES, §1, §12 (written last) | 0 / 0 / 1 | all ADOPT |

Each batch had a writer and a fresh two-direction reviewer. All BLOCKING and SHOULD-FIX findings are applied, and most NITs.

**The BLOCKING finding.** B3-4 moved the seed-42 sentence so that "the statistical band" read as the quoted block. The costed band was a different one. The sentence went back to its place.

**Notable fixes:**
- **D-9:** "supersede the finding of the sensitivity analysis", not the whole analysis.
- **E-2:** a causal colon that wrongly made the pre-flux-fix sweep a reason the MAT check missed the omission.
- **E-4:** "the collaboration uses the same pseudo-inverse", where the draft said "its own".
- **C9:** the event-loop location restored.
- **C10:** "It has not been run."
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

**agy:** 41 of 41 AGREE on the integrated passages, and 3 of 3 on the item (a) fixes, against both forms of the §5.4 home. n3-A gave 2 of 2.

## The director's items and rulings

- **App. C, the intended baseline** (n3-E): "…, not with refined negative-weight subtraction, the intended extended-fiducial baseline". The designation's homes still print.
- **App. A** (accuracy): "∼1 χ²-unit of the exact-split cross-check's tension", checked against item (ii).
- **N12 re-proposal:** n2-E's App. B/C text from `d4a51c88`, reflowed, with the fps-battery move and the :290-294 fix. It is adopted: P2N 4 of 4; P1N 3, 2.5 → 3, 3.
  - Ruling (c) then applies: `sec_fps.tex`'s source comment now cites App. C's adopted lines (:148, :105, :180). Comment only.
- **Ruling (a), accuracy, unscored:** the production iteration count's justification. "Doubling it to n=10 moves the total cross section by 0.026%" said the comparison was of the quoted estimator. §5.4 says it was measured for the exact-split cross-check, and that it is a bound. The fix is applied at sec_method's two sites and the validation table's row (ACC-n3-1 to 3), with agy.
- **Ruling (b):** §8's lead was confirmed by a fact-token diff (the same numbers, configurations and references). §8 was later not adopted anyway.
- **Ruling (d):** the comment values in sec_method and sec_systematics now cite RE-2's values_table rows.
- **Ruling (e):** records-move-ledger rows L-thin-C62 and L-thin-C30 are repointed. The ten-seed comparison sentence and the figure-code sentence leave the body, with `R:app_history.tex` probes showing App. history prints both facts. The records-move-ledger diff keeps the rows' before and after.
- **Records consequences:**
  - L14 and L-thin-C21 follow the new text.
  - L15, L-thin-C04 and L-thin-C06 carry n2's App. C probes again.
  - Two `check_note_records.py` self-test plants were re-anchored on citations that still print, because the ten-seed citation left. Both still fire.
- **Registry:** one alias digest was re-cited (`sec_5d.tex:107`, quote unchanged), and the results index regenerated.

## Scoring

**P2N** is OLD = the note at `0d919b1a`, NEW = n3, both orders, sol2 and gemini, adopted at 3 of 4. The scored text includes the unscored accuracy fixes in its piece (ACC-n3 in N02 and N04; App. A's in N11) and, for N01, the audit's ACC-A2.

| piece | content | sol2 AB | sol2 BA | gemini AB | gemini BA | NEW wins | P2N |
|---|---|---|---|---|---|---:|---|
| N01 | abstract, ES, §1 | OLD 1 | OLD 1 | NEW 1 | OLD 1 | 1 | **no** |
| N02 | §2, §3 | NEW 1 | NEW 1 | NEW 2 | OLD 2 | 3 | yes |
| N03 | §4 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N04 | §5 | NEW 1 | NEW 1 | NEW 2 | NEW 1 | 4 | yes |
| N06 | §7 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N07 | §8 | NEW 1 | OLD 1 | OLD 2 | NEW 2 | 2 | **no** |
| N08 | §9 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N09 | §10 | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N10b | §12 | NEW 1 | OLD 1 | OLD 1 | OLD 1 | 1 | **no** |
| N11 | guide, App. A | NEW 1 | NEW 1 | NEW 1 | NEW 2 | 4 | yes |
| N12 | App. B, C (n2-E re-proposed) | NEW 1 | NEW 1 | NEW 2 | NEW 2 | 4 | yes |
| N13 | App. D–F | NEW 1 | OLD 1 | NEW 2 | NEW 2 | 3 | yes |

**Not scored:** N05 (§6) is unchanged. N10a (§11) and N14 (App. G, H) differ only in the extraction order of figure labels and page numbers. Ruling (c) touches only a comment.

**P1N:** 2 sol2 runs and 1 gemini run per piece. The baseline is n2's delivered scores (N12's from its base-text re-score). The reflow is print-identical, so the baselines compare like with like.

**The adoption test is the director's noise rule** (2026-10-26):
- a piece reverts only if its sol2 2-run mean falls by more than 0.25;
- a fall of exactly 0.25 gets 2 more sol2 runs, and the piece reverts only if the 4-run mean falls.

| piece | sol2 base | sol2 n3 | Δ (2-run) | gemini base → n3 | test |
|---|---|---|---:|---|---|
| N02 | 3, 3 | 3, 3 | +0.00 | 2.5 → 3 | holds |
| N03 | 3, 3 | 3, 3 | +0.00 | 2 → 2.5 | holds |
| N04 | 3.5, 3.5 | 3.5, 3, then 3.5, 3 | −0.25 | 3 → 2.5 | 4-run mean 3.250 < 3.50: **reverts** |
| N06 | 3, 3 | 3, 3 | +0.00 | 2 → 2.5 | holds |
| N08 | 3, 3 | 3, 3 | +0.00 | 2 → 2 | holds |
| N09 | 3, 3 | 3, 3 | +0.00 | 2 → 2.5 | holds |
| N11 | 3, 3 | 3, 3 | +0.00 | 2 → 2 | holds |
| N12 | 3, 2.5 | 3, 3 | +0.25 | 2 → 2 | holds |
| N13 | 3, 3 | 3, 2.5, then 3, 3 | −0.25 | 2 → 2.5 | 4-run mean 2.875 < 3.00: **reverts** |
| not adopted on P2N, or unchanged | N01 3,3 → 3,3; N05 3,3.5 → 3.5,3.5; N07 3.5,3.5 → 3.5,3.5; N10a 3.5,3 → 3,3.5; N10b 3.5,3.5 → 3.5,3.5; N14 3.5,3 → 3.5,3 | | | | not applicable |

**Means over 15 pieces:** sol2 3.133 → 3.133; gemini 2.367 → 2.433. The table is the output of `p1n_adopt.py`, the n3 adoption test, which implements the noise rule.

**After the N04 and N13 reverts:**
- `sec_validation.tex` keeps ACC-n3-3, the iteration-stability row.
- ACC-n3-1's home probe quotes §5.4's base wording, which states the same scope; agy agrees against it.
- `app_response_mismatch.tex` is at base.

**Stop rule:** P2N no longer prefers NEW, or P1N ≥ 3.5, or 4 rounds. **Not met.**
- P2N prefers NEW on 9 of 12 changed pieces.
- The sol2 P1N mean has not moved: 3.083 at n1's base, 3.117 after n1, 3.133 after n2, 3.133 after n3.
- Round 4 is the last.

## The costed content-reduction list (`content-reduction.md`; director's ruling 4)

**What it holds:** 29 rows. For each distinct caveat that could be consolidated or dropped, it gives:
- its homes, with quotes;
- what the reader would lose;
- whether it bears on a printed number or claim;
- the sol2 quotes it answers;
- its size;
- any binding record.

It was measured on `e8c76937`, n3's integration before the §8, ES, §5 and App. D reverts. Those reverts restore base text, so the base-text homes it quotes still print.

**Its findings, for Joseph:**
- **The gap cannot be closed this way.** The note carries about 7.1–8.2 distinct caveats per 1,000 words, against the long comparators' 1.6–2.5. Applying every row would reach about 7.0–8.0.
- **Consolidation does not lower the distinct count.** Only drops do. 253 of the 431 surviving distinct caveats are stated exactly once, and the density is about the same in every section.
- **Reaching 2.5 needs about 270–315 more distinct caveats removed,** roughly two thirds of them. That happens only if secondary results leave together with their qualifiers. This is the content decision the caveat study (R-N7) leaves to Joseph, and it is the open secondary-results question from #370.
- **What the list does buy:**
  - about 3,300 words (6%);
  - caveat statements per 1,000 words down from 17.0 to 15.1;
  - restatements per caveat down from 2.06 to 1.89, the top of the comparators' range.
- **Every DROP row needs Joseph to lift "no fact leaves both documents"** for that fact, or to name the records document as its destination.
- **Bound items are marked with their records.** Among them are the 5D covariance's four measurements, the lost pseudo-experiment disclosures, the earlier 2D band's history, the 2D construction disclosures and the extended-fiducial scope fix. The most-restated caveat (the unassigned regularization bias, 21 statements) has no reduction available.
- **An alternative is for Joseph to decide** that 1.6–2.5 is not the right target for a collaboration-internal note.

## My errors in this round

- **I relayed a wrong fact to the director:** "the worst case over 43 functionals" (from G3). The note never prints 43 for s_proj. I caught it before any printed text used the number.
- **Miscounts I corrected in correspondence:** I gave 15 true audit claims (16) and 20 bare claims (21); the grandfathered list missed one table cell.
- **Two errors of my own:**
  - "The one five-dimensional coverage test" was my n2-A review fix. It was false as read, because the development assessment of candidate R is a second check. The audit found it, and ACC-A2 corrected it.
  - I listed the stale J36 and App. A comments as open n3 work. They had been corrected in n2.
- **Line numbers I estimated before measuring them,** in messages on items 3 and 4. Each was corrected after `grep -n`.
- **A zsh glob error.** An unmatched glob aborted the command that should have re-run P2N's sol2 half after the quota reset. It was re-run under bash.
- **A stale App. C probe.** The re-proposed App. C text first met the records ledger's base-text App. C probes, which the n2 revert had restored. The records probe caught it, and n2's versions were restored.

## Checks on the delivered tree

- **Ledger:** `check_ledger.py` gives 64 rows, 173 probes and 0 failures; its self-test passes. Pointed at `0d919b1a`, the protected check still flags the two files #400 changed, so the check is not weakened.
- **Records:**
  - probe PASS;
  - `--self-test` 41 of 41 fired and 4 of 4 silent;
  - `--self-test-pin` PASS;
  - pin PASS at `3c3a6f74`;
  - entry-numbers `--check` and `--check-aux` PASS.
- **Registry:** PASS. **`reflow_tex.py --note --check`:** PASS.
- **Build:** `build_all.sh` exits 0.
  - Pages: note 121, paper 13, primer 15, PET note 26, records 56.
  - 0 undefined references, no `??`.
  - SEC4 15/15; BODY-POINTERS, RECORDS-PIN, ENTRY-NUMBERS(-AUX) and RESULT all PASS.
- **Tests:** pytest on `test_hash_bindings.py`, `test_build_all.py`, `test_check_sec4_receipts.py` and `tools/registry/test_registry.py`: 158 passed.
- **Protected files are unchanged by n3:** values, values_inference, app_history, app_release, main_note, main_paper, paper_body. Every `\label` is kept.

## For round 4

- Re-propose nothing that lost P2N twice. §8 lost in n3; §11 lost in n2.
- N04 and N13 fell on P1N by the noise rule's 4-run test, with no reason naming a fact. Round 4 may re-propose them as candidates under the same rule.
- The content decision on secondary results is Joseph's. It decides whether any later round can move P1N.

# Round r19: a measurement paper's order, variant B (2026-10-28)

**Governed by:**
- `DECISION-20261025-joseph-register-rounds-paper-rewrite.md` (the method; round 3 of at most 4 for the paper);
- `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` (#431, the structural round);
- `DECISION-20261028-joseph-r19-variant-b-and-moves.md` (#433: variant B, O1–O6);
- `DECISION-20261028-joseph-result-table-and-deposit-package.md` (#441: the result table);
- the director's rulings on `outline.md` (recorded there).

**Written by** the paper rewrite lane, for the director, who merges.

**Records** (this directory):
- `outline.md`, with the rulings;
- `move-pass.md` and `move-pass/` (every leaving fact's note probe);
- `ledger.md` and `check_ledger.py`;
- `tools/` (one script per batch; each docstring lists its edits);
- `agy-b1/`, `agy-b1n/`, `agy-b2/`, `agy-b3/`, `agy-b4/`;
- `measure/` (the blinded copies' digests and the rater runs).

## What changed

**Base:** #413 at `00428d10`. Step 0 (`9df8f748`) reordered the base verbatim. The batches then ran:

| commit | step |
|---|---|
| `9df8f748` | step 0: the measurement order, verbatim |
| `569a13cd` | the variant-B ledger pass (357 facts; paper-only list P1–P7) |
| `ac1508ec`, `a7158e16` | b1 (I–III, Table I folded) and the note additions N1–N4; K1; the scope guards |
| `e893ead7`, `7b4e92c0` | b2 (IV: O1–O5, T2, T3, K12) and its fixes |
| `51cf46e3` | F2 ("Coverage asks") and F3 (Fig. 36 in its own appendix) in the note |
| `367231da`, `a1702535` | b3 (Sec. VI removed; the result table; K8, K9, K13, K14), its fixes, and b4 (the Discussion) |

Step (c)'s flux half (`b88b2858`) landed in between; it is recorded in `fived16/prd-read/REPORT.md` "Round 4".

**The paper now:**
- 11 pages and 6 sections: Introduction; Data, simulation, and observables; Cross-section extraction; Uncertainties
  and validation; The sixteen-cell cross section; Discussion and conclusions. It was 14 pages and 8 sections.
- The sixteen-cell result is its own section, with the new Table III (`tab:result16`) and its comparisons.
- Table I is folded into the text.
- The calibrated hybrid-null tests (former VII B–F and Table VI), the exact binned diagnostic's detail and Table III,
  Fig. 4, and O2, O3, O5 and O6 are in the note.

**Blinded words:** 10,381 → 7,404.

**Every fact that left the paper prints in the note,** at a ledger row with an `N:` probe. Paper-only facts were added
to the note first (N1–N4), before the paper text left.

**Unchanged:**
- no number, claim, citation key or figure meaning;
- the abstract, the title, every `\pubhold`, the acknowledgments and Data Availability;
- the Sec. I limitations paragraph (step (c)'s).

Figs. 1–3 are the same three figures, so `app_release.tex:29` stays correct. In the note, nothing renumbers: 201
labels, the two new ones last.

## Checks

| check | result |
|---|---|
| `r19/check_ledger.py` | 204 rows, 350 probes, 0 failures; `--self-test` PASS, 31 scope guards, each planted strengthening caught |
| `fived16/check_ledger.py`, frozen at step 0 against 8b0f83fd | 176 rows, 0 failures |
| `build_all.sh` | rc 0; paper 11 pp, note 129 pp; no undefined reference; no `??`; no pending placeholder |
| SEC4 receipts | 15/15, self-test PASS |
| reflow, swallowed-text, body pointers, records-move | PASS, 0 flagged |
| registry, results index, absence-claims, manifest | PASS |
| numerals in the FIVED16 blocks (fived16 rule 7) | none typed by hand |

## Reviews and agy

- **Independent reviews:** four, each ADOPT-AFTER-FIXES, with every BLOCKING and SHOULD-FIX finding fixed or recorded:
  - b1, 2 BLOCKING;
  - b1's fixes and N1–N4, 0 BLOCKING;
  - b2, 1 BLOCKING: O1 had deleted a sentence that DECISION-20261023 item 3b keeps; it is restored, with guard G22;
  - b3 and (c), 0 BLOCKING.
- **agy, each pass with a control:**
  - In b1, the subtle control was MISSED twice; it planted a strengthening of a structural sentence. A blunt one was
    caught.
  - The director's remedy is the scope guards G1–G31: each pins a structural sentence's scope words, and the self-test
    plants a strengthening that must fail.
  - In b2, a prompt defect, not agy's: the context block excused a sentence that had not moved.
  - Every other control was caught.

## Blind pairwise comparison (P2, both orders, both models)

**r19 wins 4 of 4, with no order flip.**

| | revision | blinded copy sha256 | words |
|---|---|---|---|
| OLD | `00428d10` (= `a55e2686`'s text, the corrected copy) | `16dcbccfbc0c7006…` | 10,381 |
| NEW | `a1702535` | `76c6bfa374bffdba…` | 7,404 |

| model | order | winner | strength |
|---|---|---|---|
| sol2 | A = OLD, B = NEW | B (NEW) | 2 |
| sol2 | A = NEW, B = OLD | A (NEW) | 1 |
| gemini | A = OLD, B = NEW | B (NEW) | 2 |
| gemini | A = NEW, B = OLD | A (NEW) | 2 |

**The raters' reasons** (gemini):
- NEW "adheres to standard PRD section nomenclature";
- NEW "removes … the QA-style audit table of 'Findings as tested' and the legalistic enumerated 'Conditions'";
- OLD "repeatedly lapses into internal technical-note bookkeeping, such as recounting cluster computing timeouts,
  superseded preliminary bands …".

## P1 (absolute rubric score, sol2)

| | OLD (`00428d10`, the director's corrected re-score) | NEW (`a1702535`) |
|---|---|---|
| sol2 | 3, 3, 3 | **3, 3, 3** |

**After the measurement copy was built,** one wording fix followed (agy-b4 Q2). The body's "no evidence of gain over
matched coarse projections" became "no evidence of additional discrimination beyond …", as the note says. The protected
abstract keeps "gain".

## Adoption (DECISION-20261025 item 2)

**ADOPT.** All three conditions hold:
- 4 of 4 pairwise wins (the rule asks for at least 3 of 4);
- no sol2 order flip;
- P1 does not fall (3, 3, 3 → 3, 3, 3).

**The stop rule** (item 3):
- the pairwise still prefers the new version in both models;
- P1 sol2 is below 3.5;
- r19 is the paper's third of at most four rounds.

So one round remains, if the director wants it.

**What the three P1 runs quote,** the targets for a fourth round:
- the five-iteration sentence of Sec. III ("The joint-test estimator keeps five iterations because 10, 15, or 20 …"),
  in 3 of 3 runs;
- the Limitations paragraph's lead ("The limitations of these results are stated with the results they qualify …"),
  in 2 of 3;
- the release-package sentence of Data Availability (protected), in 2 of 3;
- once each:
  - the scope paragraph;
  - the binned-diagnostic sentence;
  - the fake-data listing rule ("A truth is listed when …");
  - the note's-tests sentence of the Discussion.

The model logs record `model: gpt-6.1-sol` for every sol2 run. The digests are in `measure/SHA256SUMS`.

## For Joseph, in the final draft (d)

These are in `fived16/HANDOFF.md` §4 item 4:
- the protected text that B leaves stale: the abstract's "all reject … no evidence of gain", Data Availability's "of
  the joint tests", the title, `app_release.tex:9`'s figure list, and the Sec. I limitations paragraph's pointer to
  Sec. V for the fake-data study;
- the O3 pair: the paper's "We interpret the residual as regularization bias, because …" beside the note's "No single
  cause is established";
- Q4, the rounding instability, against the final uncertainty;
- the flux band: replace or keep;
- the deposit proposals.

The n4 note items (the main-result inconsistency; six interval-sense "calibration" sites) are in `outline.md`.
<!-- absence-ok: quotes printed limitation wording and records what was not changed; not a new absence claim -->

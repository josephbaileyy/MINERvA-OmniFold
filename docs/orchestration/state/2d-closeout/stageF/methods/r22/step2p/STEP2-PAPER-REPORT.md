# r22 Step 2, the paper round: report (2026-10-30)

The round followed [STEP2-PAPER.md](../STEP2-PAPER.md), the paper part of [STEP2-PLAN.md](../STEP2-PLAN.md).

**Result.** `paper_body.tex` was rewritten for register on the in-scope gaps, and the rewrite is **adopted** under the
paper rule committed before any score.

- **P1.** sol2 P1 stays at 3, 3, 3, the same as the base, against a target of 3.667. Under §5 this is no movement:
  the paper's first round without it, of the three the stopping rule counts.
- **Joseph pairs.** The two pairs (A4, A1) wait for Joseph. They are not applied, and the runs judged the paper
  without them.
- **Not changed.** main_paper.tex (title, abstract, acknowledgments, Data availability) and every note source are
  unchanged.

Nothing is submitted, deposited or tagged.

## The base

STEP2-PAPER.md §2: the note round renumbered two note tables that the paper cites through xr-hyper, so the paper's
rater copy at `f47b1b4a` differs from Step 1's in one line. It was rebuilt and re-scored before any text was written
(sol2 P1: 3, 3, 3). Its rater copy is `base/manuscript.txt`, 7,465 words.

## The gaps (34 in scope)

| disposition | gaps |
|---|---|
| **fixed** (19) | G1:paper-g-07, -g-09, -s-02, -s-04, -s-05, -s-07; G1b:paper-g-05 (a #522 move; the note prints it), -g-10, -g-16, -s-01, -s-03, -s-06, -s-09, -s-11, -s-12, -s-14, -s-16, -s-18 |
| **partly fixed** (3) | G1:paper-s-01 (the pointer and caption only); G1:paper-s-03 ("fallback" and "ungraded" removed; "residual proxy" is only in a held sentence); G1b:paper-g-17 (merged, not cut: C1) |
| **pairs for Joseph** (2) | G1:paper-s-06 (A4), G1:paper-s-09 (A1): [pairs.md](pairs.md) |
| **skipped: quote held, no other passage** (9) | G1:paper-g-01, -g-04; G1b:paper-g-11, -g-12, -s-04, -s-08, -s-10, -s-17, -s-19 |
| **skipped after review R-1** (2) | G1:paper-s-10, G1b:paper-s-15. The cut "is stated only here" was restored: the four low-stability cells print only in the paper's limitations (C18), not in the note, so the #522 move's condition fails. |

That is 19 + 3 + 2 + 9 + 2 = 34.

## The checks

- **Fact ledger** ([ledger.md](ledger.md), `check_paper.py`): 27 rows, 47 probes, 30 changed base sentences, 0
  failures.
  - Also checked: the 8 GATE phrases once each, the FROZEN sentence once, the labels, no new numeral, and the
    registered alias.
  - main_paper.tex and every other source are unchanged, apart from the two registry-generated records files.
  - Self-test: 16 planted defects caught, 2 silent controls.
- **Held sentences** (`tools/check_held.py`, exact): 23 of 23 print in the new rater copy.
- **Two-direction review** ([review.md](review.md)): 7 findings.
  - Six are fixed: R-1 (restored), R-2 (the "populated" gloss removed), R-3 (the fake-data tests no longer tied to
    the uncertainties), R-4 ("unstable" restored), R-5 (C_resp the subject of "does not cover") and R-7 (the note's
    training-detail wording instead of a general-knowledge gloss).
  - R-6: the 39-cell definition's "fallback" role left the paper. The note prints it (`sec_5d.tex`, "takes RD3 as the
    fallback"). It is recorded as a cut to the note (ledger P-10), **for the director to accept**; if it is not
    accepted, the clause is restored.
- **agy.**
  - First run ([agy1/](agy1/)): the control caught 3 of 3 planted negations. The 16 flags of 20 agree with the review.
  - Re-run on the fixed text ([agy2/](agy2/)): the control caught 3 of 3. Every flag is one the review ruled supported
    or moved, with the note source quoted, apart from one new flag. "the sixteen-cell result supports the comparison
    that follows" could be read as "corroborates", so it now says "can be used for".
- **Build** (`build_all.sh`): PASS. SEC4 15/15, paper 11 pages, no undefined reference. VALUES-FIVED16 PASS. REFLOW
  PASS. Registry PASS. Results index fresh.

## The B4 re-pin (STEP2-PLAN.md §7, ruling 4)

`paper_body.tex` line 52 (the estimator paragraph) carried in-scope gaps G1:paper-s-01 and G1b:paper-s-11 and was
reworded. After the cut Scope paragraph, it is now line 50.

| row | old | new |
|---|---|---|
| ALIASES 38 (`e-R-joint-test`, "joint-test estimator") | `paper_body.tex:52`, `402b2cee1998669e` | `paper_body.tex:50`, `52bd6f35a5367d1e` |
| ATTRIBUTION 17 (`e-R-joint-test`) | `paper_body.tex:52`, `402b2cee1998669e` | `paper_body.tex:50`, `52bd6f35a5367d1e` |
| ALIASES 47 (table row, text unchanged) | `paper_body.tex:64`, `308c2724c0758c07` | `paper_body.tex:62`, `308c2724c0758c07` |

- The alias text "the joint-test estimator, a deterministic LightGBM" still prints on the cited line, and stays
  registered.
- `records_estimators.tex` is regenerated.
- One registry self-test fixture had cited `paper_body.tex` line 290 by index, and the shorter paper broke it. It now
  computes the same position, the file's last element. At the base that is still line 290, with digest `e3b0c442…`.

## Adoption (the paper rule of STEP2-PLAN.md §4)

The base is `base/manuscript.txt`. NEW is `new/manuscript.txt`: the blinded rater copy at `8c76b128`, 7,459 words,
built by `make_rater_copy.sh`, hold diff PASS. `tools/step2p_runs.sh` ran the adoption runs, and
`tools/adopt_step2p.py` applied the rule ([runs/adoption.tsv](runs/adoption.tsv)):

| model | order | winner | strength |
|---|---|---|---|
| sol2 | A = base, B = NEW | NEW | 1 |
| sol2 | A = NEW, B = base | NEW | 1 |
| gemini | A = base, B = NEW | NEW | 2 |
| gemini | A = NEW, B = base | NEW | 2 |

- NEW won 4 of 4 runs.
- sol2 did not flip.
- P1 sol2 was 3, 3, 3, against the base's 3, 3, 3.
- **ADOPTED.**

All seven runs answered on the first attempt. The rater outputs are committed verbatim as `runs/*.txt`, and
recomputing from copies renamed to `.md` gives the same `adoption.tsv`.

**The raters' reasons.**
- **sol2:** NEW "separat[es] the response covariance's definition, scope, and limitations". It replaces "ungraded"
  and "the same pull" with explicit statements, and integrates the scope statement into the introduction.
- **gemini:** NEW removes the run-in "Scope." heading and "ungraded", splits the C_resp run-on sentence, and resolves
  vague pronouns ("exceeds the target").

**What P1 still quotes (all three runs).**
- The held five-iterations sentence (B3, F109 KEEP).
- The held limitations-pointer passage with the restored "is stated only here" (#522 item 2, C18).
- The Data availability package sentence (A1, the pending pair).

P1's remaining quotes are the passages the protections hold, which is why it stays at 3.

## For the director and Joseph

- The two pairs ([pairs.md](pairs.md)), with pins `bbb99991e62f584b` (A4) and `083bfb80f9fac8fd` (A1). If Joseph
  approves them, they are applied with `PAIRS` / `PAIR_PINS` and judged in their own check. A1 also exempts the held
  G1b:paper-s-05 quote.
- The R-6 cut of "fallback definition".
- P1 at 3 is held up by protected passages. Moving it would need Joseph's choices on the held sentences P1 quotes,
  and those are already in the PROTECTED lists.

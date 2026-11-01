# The 620 round: report (2026-11-01)

**Under:**
- `DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md` item 2: Joseph's four editorial fixes ("Apply all
  four"), through the fact ledger and truth checks; nothing factual leaves the paper;
- `DECISION-20261101-joseph-eavail-keep-135.md` item 2: the departure sentence after Eq. (1) ("Keep 135");
- the director's 2026-11-01 instructions:
  - after #634, a disclosure of the stopped 1B coverage test, one sentence in the paper and a fuller one in the note;
  - after #637, re-point `sec_3d.tex`'s source comment, and check that the note's 135 MeV paragraph agrees with the
    measured size.

**Result.** All four fixes, the departure sentence and both 1B disclosures are in, and every check passes. The
abstracts, `main_paper.tex` and `main_note.tex` are byte-identical to the base `c93a73bce`. Joseph sees the new
sentences in his next read. Nothing is submitted, deposited or tagged.

## What changed

**The four fixes** (`paper_body.tex`):
1. Eq. (1) is split across two lines under one number, breaking before the π⁰ term (amsmath `split`).
2. The reconstructed-W paragraph goes from seven sentences to four, with every fact kept (ledger E2, one probe per
   fact).
3. "Fixed seed" is kept. "42" and "seed plus three" leave the paper. Both already print in the note section the paper
   cites (`sec_method.tex` configuration (f): "seeded at the estimator seed plus three: the 2D central value (seed~42)").
   This round's earlier note that "seed plus three" had no home there was wrong, so no note sentence was needed.
4. Table I is replaced by a paragraph that gives:
   - what the two estimators share;
   - what each one gives;
   - the joint-test estimator's fixed seeds;
   - "not combined", and the pointer to the note.

   Further details:
   - `tab:estimators` is removed, and nothing references it.
   - The held sentence G1b:paper-g-07 / paper-s-02 (r22 `step2p/held.tsv`, WORDING, PROTECTED) prints verbatim inside
     the new paragraph.
   - The next paragraph's repeated "five iterations" opening is dropped, and its citation of the classifiers moves
     into the new paragraph.

**The departure sentence** follows Eq. (1)'s species sentences ("contribute nothing"). It states:
- no single published definition exists;
- Eq. (1) keeps the closed list's species (Ref. [18], Rodrigues 2016) except e±;
- the charged-pion term exceeds the kinetic energy of that list and of Eq. 4 of Ref. [19] (arXiv:2312.16631) by 4.57 MeV
  per charged pion;
- it omits further species of the open list (Ref. [20], Ascencio 2022);
- to first order in the unfolding, without retraining, replacing the constant alone moves the sixteen-cell result by
  at most 0.19σ in any cell and by 0.42σ as one coherent shift. That is the norm under the reported covariance. Without
  the run-period block the figures are 0.21σ and 0.42σ.

The source is #622 §7.2–7.3 (`step0_metric.txt`). "The constant alone" keeps it one departure of several.

**The note's 135 MeV paragraph** (`sec_3d.tex`):
- OI-30(c)'s 0.67 % and 1.05 % (a 65,911-event sample whose binning that record does not identify;
  `EAVAIL_DEFINITION.md` §3 after #637) give way to #622's measurement on the analysis's fine grid: 0.65 % of the
  signal weight changes bin, and no bin moves by more than 0.97 % (`step0.json`, control C1 bitwise).
- "So its materiality is not established" gives way to the same sixteen-cell size as the paper's, for configuration (e).
- The configuration-(a) clause stays, since that projection is still unassessed.
  <!-- absence-ok: restates the note's unchanged sentence; #622 measured the sixteen-cell result only (ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md sec. 7.3) -->
- The source comment no longer cites `EAVAIL_DEFINITION.md:118` ("It has not been done"), which #637 removed. It cites
  #622 §7.3 and the keep-135 decision. It also drops the false "the same numbers print in paper_body.tex"; the paper
  prints neither.

**The 1B disclosure:**
- **Paper:** after the held-out tunes' bias tests. A coverage test at these two tunes was declared in advance for the
  covariance without the run-period block. Its pseudo-experiments also drew the flux, interaction and detector
  uncertainties. It was stopped at one of its gates before any coverage pseudo-experiment ran: the uncertainties
  reproduced through its pseudo-experiments disagreed with the covariance blocks they draw, for reasons not established.
- **Note:** the fuller version adds:
  - the surrogates and what is not drawn;
  - the ratio outside 0.9–1.1 in 11 of 16 cells, from 0.70 to 2.30;
  - the L1 replacement test over the 38 drawn bands;
  - the open cause.
- **Sources:** FD-1B-DECLARATION.md §1–3, FD-1B-STAGE2-REPORT.md §4.1 and its "Not measured", and FD-1B-DIAG-REPORT.md.
- **Wording:** "at one of its gates", not "its first gate": gate 1 passed and gate D was stage 2's second.

**Numbers:** each new one prints through `\fvval` from four new pinned readouts in `make_values_fived16.py`:
- `step0_metric.txt` `3e8bd546`;
- `step0.json` `c284a6b3`;
- `gate-d.json` `e1838c0a`;
- `diag.json` `6fd6669e`.

The 1B claims are asserted in code (gate D FAIL, NOT LOCALIZED, zero sets, ρ reproduced bit for bit).

**Tooling:**
- `r22/step2/check_ledger.py`:
  - declared label removals, with two self-test plants;
  - the self-test's abstract anchor taken from the base, since main's abstract no longer begins "We report";
  - a failure on any ledger row that does not split into six columns. One of this round's rows quoted a markdown table
    and was skipped silently. No earlier ledger had such a row.
- **The registry:** three citations of the old Table I lines (`ALIASES.tsv` rows 38 and 47, `ATTRIBUTION.tsv` row 17)
  are re-cited to the new paragraph, and `records_estimators.tex` is regenerated.

## Checks, on the final text (`3863016d4`, and this report's commit)

| check | result |
|---|---|
| the ledger (`check_ledger.py`, base `c93a73bce`, with `paper_body.tex` in the batch) | 9 rows, 50 probes, 17 changed base sentences, 0 failures; self-test PASS |
| `make_values_fived16.py --check` and `--self-test` | PASS: 2296 values; 9 listed-truth sentences agree |
| `build_all.sh` | PASS: all five PDFs (paper 12 pp, note 129 pp); no "??" in either |
| the registry (`check_registry.py`, and `--self-test`) | PASS |
| the two-direction review (`review.md`) | 3 Medium and 8 Low findings fixed. Two Lows kept, with reasons. One outside the diff is reported. No number was wrong, and no fact was lost |
| agy's targeted read (`agy-triage.md`) | no undeclared difference; the control caught 6 of 6 |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | 4 flags, the 5B round's four, none of them this round's; the two flags this round first raised are fixed |
| the rater copy (`rater-copy/`) | holddiff VERDICT PASS |
| P1 ×3 (sol, on the rater copy of `3863016d4`) | 3, 3, 3, so the non-regression holds |

## For the director and Joseph

- **0.19σ, not 0.21σ, leads.** The question Joseph approved quoted 0.21σ, the without-block value. The paper prints the
  reported (with-block) 0.19σ first, and 0.21σ with "without the run-period block", as J2 asks.
- **Not added:** a switch would also move every generator prediction, so a χ² changes by the difference of the two
  shifts (#622 §7.3's caution). The sentence speaks of the result, not of a χ².
- **arXiv:2312.16631 Eq. 4:** `EAVAIL_DEFINITION.md` reads it at :41 as three terms, but :80 mentions an Eq. 4 "strange,
  or heavier quark" clause. The paper claims only that Eq. 4's charged-pion term is kinetic, which holds under either
  reading. Only the paper itself settles whether its list is also open.
- **`EAVAIL_DEFINITION.md`:118–119** calls C_total + C_resp "the reported" covariance. The paper's reported covariance
  includes C_PL,5D. That file has its own owner's review.
- **P1 rater r3** suggests splitting the paper's 1B sentence in two. Its rewrite reads "did not reproduce", the causal
  wording the review removed, so it is not applied. The sentence stays one, as the director asked.
- **Older wrappers:** the step3, step4 and step4-install self-tests are not meaningful on today's tree. Their base
  abstracts are not main's, so their baselines already fail check 4, as the 5B report recorded. Each is valid at its
  own round's head.

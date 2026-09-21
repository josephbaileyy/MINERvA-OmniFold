# ASSESSMENT — the scoped Letter's manuscript and external-review readiness

**Owner:** independent-assessment lane. **Base of measurement:** `origin/main = 6f24fb00`;
note repository `d0c3768e`. **Scoped under Ruling 1** — no Z-dependent or non-2D generator
significances, p-values or calibrated exclusion claims; the validated 2D scope preserved.
**No compute launched.** Builds were local, in an isolated worktree, and no scheduler was touched.

## VERDICT

> **READY as a manuscript. NOT READY for external review, on one EVIDENCE fault.**
>
> The build passes, the scope claim holds, no quarantined value reaches the Letter, and the standalone
> repository is in sync. **The single blocker is that the authority for the Letter's scope is not in
> any repository a referee would be given.**

| # | finding | fault type |
|---|---|---|
| 1 | `build_all.sh` **passes**, three PDFs, containment clean | — |
| 2 | *"Every non-two-dimensional result … is a central value"* **holds** | — |
| 3 | audit descriptors labelled, and **absent from the Letter entirely** | — |
| 4 | standalone note repository **in sync** | — |
| 5 | **Ruling 1's record is unreachable from `main`** | ⚠ **EVIDENCE** |
| 6 | *"the corrected contract"* is a definite description a referee cannot resolve | **EVIDENCE**, minor |
| 7 | 18 `\dead{}` struck values visible in the companion note | **MANUSCRIPT**, expect-the-question |

---

## 1 — DOES IT BUILD? **YES**, at `6f24fb00`, exit `0`

Toolchain checked **before** blaming the manuscript: `latexmk`, `pdflatex`, `biber`, `bibtex`,
`python3` all present. **No `biber`/PAR-cache fault occurred**; had one, it would be an environment
fault and reported as such.

    main_note.pdf    90 pp
    main_primer.pdf   5 pp
    main_paper.pdf    3 pp

**All three confirmed written by this run** — the script's own freshness check fired three times with
timestamps from the run, which is the guard against the 2026-08-19 "green over last week's PDFs"
defect. `SELF-TEST :: PASS`, `RESULT :: PASS`, `FAIL` count **0**.

**Containment holds:** `note.pdf` carries **10/10** struck literals (positive control), `paper.pdf`
and `primer.pdf` carry **0 of 10**.

## 2 — DOES THE SCOPE CLAIM HOLD? **YES, and it is stronger than quoted**

`paper_body.tex:145-148` reads *"Every non-two-dimensional result in this Letter is a central value. A
publication-level significance requires the adopted, selection-complete scalar five-dimensional
covariance, which is not yet in hand; **no superseded or historical covariance is used here.**"* The
final clause is not in the excerpt I was given and it strengthens the claim.

**Verified exhaustively rather than by reading.** Counts in `paper_body.tex`: `p-value` **0**,
`chi^{2}` **0**, `chiCombined` **0**, `exclusion` **0**, `Nsigma` **0**, `gbdtFive` **0**. All seven
`sigma`/`significance` hits are benign — the cross-section symbol `d²σ/(dp_T dp_∥)`, published-σ
standardized residuals whose own caption places them *"on the reported two-dimensional grid"*, and
**`No significance is assigned.` twice, in figure captions at `:120` and `:137`.**

## 3 — IS ANY QUOTED NUMBER FROM A QUARANTINED PRODUCT? **NO — and the descriptors never reach the Letter**

The three 3D descriptors occur in **one** passage, `sec_3d.tex:247-250`, and the label is in the same
paragraph immediately after them, `:251-252`: *"These are audit descriptors, not publication
uncertainties."* The only other hits are `1431` at `app_statmethods.tex:945` (a **bin count**) and
`247` in `values.tex` `%`-comments about tape recovery — neither an uncertainty descriptor.

**And structurally the question is moot for the Letter.** `main_paper.tex` inputs exactly
`\input{values}` and `\input{paper_body}` — **`sec_3d.tex` is not in the paper's closure.** The
descriptors are note-only.

**Two independent instruments agree.** The Letter uses exactly **8** value macros — `\binsTen`,
`\pullMean`, `\pullRMS`, `\ratioTot`, `\sigTwoD`, `\sigTwoDpaper`, `\uqMedian`, `\uqPaper` — **none**
carrying a quarantine, struck, dead or audit-descriptor marker in `values.tex`; and the build's own
containment stage independently reports `paper.pdf: 0 of 10 struck literals`.

## 4 — IS THE STANDALONE REPOSITORY IN SYNC? **YES. The gate is met.**

    monorepo   origin/main  = 6f24fb0097a7603b7d6acb695de06dbb3f3ea157
    note repo  HEAD         = d0c3768ea1e53ec80b84b92eccc9244a45fa3a8c

- **25 of 25** `.tex`/`.bib` files **byte-identical** between `note-repo:HEAD` and
  `origin/main:docs/analysis-note/`.
- **0 of 89** monorepo note files absent from the note repository.
- Last monorepo commit touching `docs/analysis-note/` is `3ae65695`, **2026-08-26 21:00:11**; the note
  repo's head is **21:00:04** — **seven seconds apart, the same synchronisation operation**, and its
  message is *"Synchronize clarified note and improve PET table spacing."*

**⚠ I nearly reported this as stale.** The note repo's last commit is 2026-08-26, two weeks old, and
a date-only read says out of sync. **The content says otherwise, because nothing has touched the note
sources since.** A staleness claim from a timestamp would have sent someone to re-sync an already
synchronised repository.

## 5 — WHAT WOULD AN EXTERNAL REVIEWER ASK THAT WE CANNOT ANSWER?

### 5a — ⚠ THE BLOCKER, AND IT IS AN **EVIDENCE** FAULT: RULING 1'S RECORD IS NOT IN ANY REPOSITORY A REFEREE GETS

The Letter's defensibility rests on a deliberate exclusion: no non-2D significance, because the
covariance is *"not yet in hand."* A referee's first question is **"on what basis, and who decided
that?"**

The answer is Joseph's Ruling 1, recorded in
`DECISION-20260910-joseph-b-deferred-and-finite-ensemble-disclosure.md` — which is **committed on
`lane/decision-20260910-z-endpoint-a-ruling` and is NOT reachable from `main`**, and therefore is in
neither the monorepo's main line nor the standalone note repository.

**So the manuscript is internally consistent and its governing authority is unreachable from the
artifact.** This is not a manuscript defect — the text is correct — and it is not an environment
defect. **It is an evidence fault, and it is the one thing standing between "READY as a manuscript"
and "READY for external review."** Closing it is a merge, which this lane cannot authorize.

### 5b — **EVIDENCE**, minor: an unresolvable definite description

`sec_3d.tex:252-255` reads *"Under **the corrected contract**, the quotable 3D covariance is the exact
projection…"*. A referee reading the companion note cannot resolve *"the corrected contract"* — it
points at orchestration records outside both repositories. The claim is true; its referent is not
reachable from where it is made.

### 5c — **MANUSCRIPT**, expect-the-question rather than a fault

The note carries **18** `\dead{}` struck values in `app_statmethods.tex`. That is deliberate,
correctly contained (they reach the note only), and honest. **A referee will still ask why a
companion document displays eighteen retracted numbers**, and the answer should be ready rather than
improvised.

### 5d — WHAT IS **NOT** A GAP, MEASURED

- **No quarantined value reaches the Letter** — §3, two independent instruments.
- **The Letter does point a referee onward**: `paper_body.tex:157`, *"documented in the companion
  analysis note"*, and that note is available and in sync.
- **Clause (v) does not bind the Letter.** `app_statmethods.tex:645`'s declarations are conditioned on
  *"Any N-D χ²"*, and the Letter quotes none.

## SCOPE OF THIS ASSESSMENT

**Not assessed:** any Z adoption question, the pilot, A-7, `κ`, the maps — excluded by the brief.
**Not verified:** whether the note's *content* is scientifically correct; this is a readiness and
conformance assessment, not a physics review. **No compute launched**; the only executions were local
LaTeX builds in a disposable worktree, since removed.

**A method note.** My first grep of the 5172-line build log returned nothing for `PASS`, `FAIL` and
`written by this run` alike — the log is *Non-ISO extended-ASCII*, so `grep` treated it as binary and
suppressed output. **The positive control is what caught it**: a log that visibly contained `PASS`
reporting zero occurrences is an instrument failure, not a result. Re-run with `grep -a`.

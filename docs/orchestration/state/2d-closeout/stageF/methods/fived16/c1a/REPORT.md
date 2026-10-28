# Step (c), the 1A half: the GENIE v3 held-out bias test in the paper and the note (2026-10-28)

**Under:**
- `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md`, items 1 and 5. "It is a bias test,
  not a coverage test … The paper says so". The limitation sentences are revised from 1A's result, and their final
  wording goes to Joseph with the final draft.
- `FD-F1-BINDING.md`, ruling 2: graded as non-vertex truths against C_total + C_resp; the leave-out-GENIE+MEC grade is
  descriptive; the overlaps are stated; the two truths are not counted as independent tests.
- The director's approval of the plan, 2026-10-28, after #413 moved to `22314565`, with five conditions (below).

**The director's conditions,** verbatim, from the message of 2026-10-28 that released the hold at `22314565`:

> Your (c) 1A plan is approved, with these conditions.
> 1. **"below the reported uncertainty in every cell":** your assert computes max |b|/σ < 1 from bias and relative_sigma_plus_C_resp, without the noise term. Keep that assert. Also probe, by key, that it holds for all four records (ensembles and closures). The z the report prints uses C + N; say in the ledger which one the sentence rests on.
> 2. **The abstract additions are drafts for (d).** The abstracts' final wording is Joseph's. Your guards' plants on "below the reported uncertainty" and "cannot test the intervals' width" are right. Add one plant that drops "GENIE v3", since the family qualifier carries the partial-evidence scope in the abstract.
> 3. **IV H's "partial evidence, not two independent tests" and "a bias test, not a coverage test"** both need guards, and the report's overlap facts need ledger probes into FD-F1-REPORT.md.
> 4. **The protected-span allowance:** yes, an explicit (c)-1A allowance for Sec. I's limitations paragraph in r19/check_ledger.py, recorded as a ledger row citing this message. After the edit, re-pin the byte check to the new paragraph so it stays protected.
> 5. **The pointer fix** sec:result16 → sec:fd16 is approved.

**Condition 4 names only Sec. I's paragraph.** The allowance also covers the protected title-to-abstract span, by E2
only. That follows from condition 2's approval of the abstract additions as drafts, and it is put to the director to
confirm.

**Written by** the paper rewrite lane, for the director, who merges.

**The readout:** `measurement-paper/5d-community-20261024/fd/readout/fd_f1_readout.json`, sha256 `cbe411a9…`
(`FD-F1-REPORT.md`, PR #446). The two tunes' names come from their generation records
(`fd/receipts-f1/run/cluster/f1b3/gen5d/*.meta.json`, `4fe333b8…` and `d7d136e5…`). Those digests equal the F1c
pin's `f1b3-SHA256SUMS`.

## What changed

`apply_c1a.py` makes every text edit, as exact old → new pairs. It reproduces the tree byte for byte from `22314565`.

| edit | where | what |
|---|---|---|
| E1 | Sec. I, limitations paragraph (the 1A slot) | "Interval coverage has not been validated. At two held-out GENIE v3 truths, a bias test finds the estimator's bias below the reported uncertainty in every cell, but does not test interval widths." The fake-data sentence is unchanged, except that its pointer moves from Sec. V to IV H (sec:fd16; b3 review S2; director condition 5). This is PRD read r5's sol2 r2 form. |
| E2, E3 | both abstracts | The coverage sentence keeps "has not been validated". It adds "; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths". The width clause follows agy's first pass. These are **drafts for (d)**: the abstracts' wording is Joseph's (director condition 2). |
| E4 | IV H, one paragraph after the F0b result, inside the FIVED16 block | The two tunes, generated for this test, and how they enter. 20 Poisson pseudo-experiments plus a closure against the full covariance. Both criteria pass, with the ensemble means' χ² and p and \|z\| ≤ 0.65 in the means and the closures. The overlaps: partial evidence, not independent tests. The leave-out-GENIE+MEC χ², descriptive. Bias, not coverage; the width is not tested; the detector response is the simulation's and is not probed. This is PRD read r5's sol2 r1 form, with agy's second-pass fix to the detector-response clause. |
| E5 | note sec:fived16-fd, before sec:fived16-gen | The same, in full. It gives all four records with χ², p and the largest \|z\| with its cell; \|b\| < 0.65σ in every cell; the held-out group's tally with its Gaussian references, as context; the overlaps; the leave-out and model-only variants; control 9; and "the detector response is not probed". There is no new table, so no note table renumbers. |
<!-- absence-ok: quotes the printed and draft limitation wording that this step edits or keeps; not a new absence claim -->

**Numbers:** `make_values_fived16.py` adds `"f1"` and the two meta records to READOUTS, which gives 1,411 values in
all. It asserts these properties:
- **Control 9:** every F0b truth in the F1 readout equals the F0b readout's record, field for field.
- The trigger rule is F0b's.
- `all_graded` is F0b's, so the held-out group stays out of it.
- No held-out record is listed.
- Each record is graded against C_total + C_resp, with no own vertex.
- **For each of the four records,** max over the cells of |b|/σ is below 1. Here σ = √diag(C_total + C_resp), with no
  noise term. The keys `f1-g18-bsig` 0.63, `f1-closure-g18-bsig` 0.61, `f1-ar23-bsig` 0.65 and `f1-closure-ar23-bsig`
  0.61 are ceiled, and the ledger probes each one (director condition 1).

The z the report prints uses C + N, so |b|/σ ≥ |z|. The abstracts' and Sec. I's "below the reported uncertainty in
every cell" rests on |b|/σ, and the note prints that basis: "In every cell of the four records, the bias is below 0.65
of the cell's reported σ."

The self-test plants a wrong control 9, a listed held-out record and a cell with |b| = 2σ. Each one is refused.

**Unchanged,** because each still says only that coverage is not validated, which stays true:
- the C_model "coverage at truths held out of its construction has not been validated" sentences (paper IV A,
  sec:cov16; note §10.2);
- the Scope paragraph;
- the Discussion's limitations;
- the note's sec_intro and sec_summary.
<!-- absence-ok: quotes the printed and draft limitation wording that this step edits or keeps; not a new absence claim -->

## The ledger and the protected text

**`r19/ledger.md`** adds:
- **C1A-ALLOW:** the director's condition 4;
- **C1A-1 to C1A-6:** the changed sentences P20, P21, M2, A3 and F47, and the two additions. Their probes reach into
  `FD-F1-REPORT.md`, `FD-F1-DECLARATION.md`, `FD-F1-BINDING.md`, `LIMITATION-PLAN.md`, the readout and the four
  `bsig` keys (director conditions 1 and 3);
- **GC1–GC24, scope guards** (GC17–GC24 after the review):
  - "has not been validated", in Sec. I and both abstracts;
  - the dropped "GENIE v3", in Sec. I and the paper abstract (director condition 2);
  - "below the reported uncertainty in every cell";
  - "does not test interval widths", in Sec. I and both abstracts;
  - IV H's "partial evidence and are not independent tests" and "These tests assess bias, not coverage" (director
    condition 3);
  - the width and detector-response clauses;
  - the note's two qualifiers.
<!-- absence-ok: quotes the printed and draft limitation wording that this step edits or keeps; not a new absence claim -->

**`r19/check_ledger.py`:**
- **The allowance, condition 4.** The protected title-to-abstract span and the Sec. I limitations paragraph are
  byte-checked against the base with `apply_c1a.py`'s E1 and E2 applied. The pairs are imported, not retyped. Any other
  edit there still fails, and the self-test plants one in each.
- **`R:<path>::` probes** into repository records, with a planted bad probe in the self-test.
- **Coverage** of the note's sec_fived16.tex and main_note.tex (F and A ids).
- **Note guards,** planted in the note file. A GUARD row with only note probes is allowed.

## PRD read and agy

**The PRD read** (`../prd-read/REPORT.md`, "Round 5"):
- L1: sol2 r2's form applied, after the truth column;
- H1: sol2 r1's form applied;
- H2: kept, because both sol2 forms drop the |b|/σ sentence;
- A1, A2 and P02: unanimous ACCEPT, kept.

**agy** (`agy/README.txt`): five passes, each with a control that plants four strengthenings. Every control caught 4
of 4.
- **Pass 1, the first drafts:** both abstracts read DIFFERS. Without "cannot test the width" they could read as
  validating the intervals, so both now add L1's "but does not test interval widths".
- **Pass 2, after the round-5 forms:** H1 read DIFFERS. "using the C_model procedure and the simulation's detector
  response" could read as the response being used or probed, so it now says "the detector response is the
  simulation's and is not probed".
- **Twice declined:** the reading that the note abstract's "the result's intervals" misleads. That clause is the base
  wording and is right.
- **Pass 3:** all five SAME, before the review's N2 and N3 wording.
- **Pass 4, after N2 and N3:** Q5 read DIFFERS only because BEFORE lacked the declaration's model facts. BEFORE was
  fixed, not the text.
- **Pass 5, the final text with the fuller BEFORE:** all five SAME.
- **P02** (`agy/p02/`): the control was caught. It reads DIFFERS on the two register changes the raters accepted ("show
  how far the result can be trusted" → "assess the result"; "the background subtraction" → "background-subtraction
  tests"). Neither strengthens anything, so they go to Joseph as reading notes.

## The independent review (of `589f0780`)

**Verdict: ADOPT-AFTER-FIXES, with no BLOCKING finding.** The reviewer re-derived every printed claim and the four
|b|/σ values from the readout. It found the truth-column decisions right. `apply_c1a.py` reproduces the commit byte
for byte, and the protected files are unchanged. Fixed in the next commit:
- **SF1:** guards GC17–GC24 on every sentence that ruling 2 needs: the shared quasielastic model, G18's MEC family, the
  descriptive leave-out, the note's "so they are context only", "the detector response is not probed" and
  "Descriptively,". There is also a probe for "Both tunes satisfy both bias criteria".
- **SF2:** `make_values` asserts that AR23's two records share their model-only cell, and that neither G18 record has
  one, with two self-test plants.
- **N2:** "share their quasielastic model" becomes "use the same quasielastic cross-section model". The note adds
  `NievesQELCCPXSec`, with AR23's z-expansion form factor (FD-F1-DECLARATION.md:296-298).
- **N3:** the truth is "the tune's shape ratio to GENIE CV, built as for the C_model components". The note's wording
  is "built as the reweighting ratios of the C_model vertices are".
- **N5:**
  - E1's and E2's pairs are pinned by sha256 in `check_ledger.py`, so editing a pair together with the paper fails
    PROTECTED. A self-test plants that, and a run with the pin moved shows the pin is what catches it.
  - Labels in sec_fived16.tex and main_note.tex are now checked.
- **N1:** Round 5 records the composites (A1, A2, H1) and round 3's full rule.
- **N6:** the conditions are quoted above.
- **N7:** P02's agy pass (`agy/p02/`).

**Not changed:** N4, a pointer of its own for the Sec. I bias-test sentence. It is optional, and the truth column
accepted one pointer for both sentences.

**The reviewer's observation, for Joseph:** at G18's R11, the −8.5 % bias stays below σ mainly through C_model's
GiBUU vertex. |b|/σ is 0.62 in full, 0.93 without GiBUU and 1.07 with C_e + C_resp alone. The sentence is right as
written, because C_model is part of the reported uncertainty, which the paper calls "not a calibrated bound".

## PRD read r6: the composites as printed (director, accepting `1bcccc38`)

The director's message: "the composites A1, A2 and H1 get a read as printed now, not at (d) … If a rater form beats a
composite and passes the truth column, it goes to Joseph as an alternative. It doesn't replace the composite
silently." In `../prd-read/REPORT.md`, "Round 6":
- **P02, the control:** ACCEPT ×3.
- **A1 and A2:** the composites stand. Two rater forms drop the width limitation. sol2 r1's form is true, but agy reads
  its plural "bias tests" as independent tests.
- **H1:** the composite stands, and sol2 r2's form goes to Joseph as an alternative. It is true, and agy reads it
  SAME.
- **agy** (`agy/r6/`): the control caught 4 of 4, and the three composites as printed read SAME.

The director also confirmed the allowance's abstract coverage, by E2 only, under condition 2. It is recorded in
C1A-ALLOW.

## Checks

| check | result |
|---|---|
| `r19/check_ledger.py . --base 9df8f748` | 235 rows, 406 probes, 192 changed sentences, 0 failures; `--self-test` PASS (55 scope guards, each planted strengthening caught; the allowance pin's plant caught) |
| `make_values_fived16.py --check`, `--self-test` | PASS |
| fived16 rule 7 (no numeral typed by hand in the new prose) | 0. "2p2h" became "MEC" because of it |
| `build_all.sh` | rc 0; paper 12 pp (11 before: the reference list's last column), note 130 pp (129); no undefined reference; no `??`; no pending placeholder; SEC4 15/15 |
| reflow, swallowed-text, registry, results index | PASS |

## For Joseph, in (d)

- **H1's alternative,** sol2 r2's r6 form, beside the printed IV H paragraph.
- **Beside Sec. I's "below the reported uncertainty in every cell":** at G18's R11 that holds mainly through C_model's
  GiBUU vertex. |b|/σ is 0.62 in full, 0.93 without GiBUU and 1.07 with C_e + C_resp alone. "The reported uncertainty"
  includes C_model, which the paper calls "not a calibrated bound".

- **The abstracts' 1A sentences,** as drafts. The paper abstract goes from 203 to 228 words and the note's from 348 to
  373 (`tools/recount.py`). The note abstract's length is already a (d) item.
- **Sec. I now says "Interval coverage has not been validated"** (r5's form), and the abstracts say "The coverage of
  the intervals has not been validated". Whether to align them is a wording choice.
- **The Sec. I pointer for the fake-data study** is fixed (condition 5). It leaves the (d) list.
<!-- absence-ok: quotes the printed and draft limitation wording that this step edits or keeps; not a new absence claim -->

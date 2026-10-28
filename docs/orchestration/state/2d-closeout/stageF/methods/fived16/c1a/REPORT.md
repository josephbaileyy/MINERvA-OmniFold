# Step (c), the 1A half: the GENIE v3 held-out bias test in the paper and the note (2026-10-28)

**Under:**
- `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md`, items 1 and 5. "It is a bias test,
  not a coverage test … The paper says so". The limitation sentences are revised from 1A's result, and their final
  wording goes to Joseph with the final draft.
- `FD-F1-BINDING.md`, ruling 2: graded as non-vertex truths against C_total + C_resp; the leave-out-GENIE+MEC grade is
  descriptive; the overlaps are stated; the two truths are not counted as independent tests.
- The director's approval of the plan, 2026-10-28, after #413 moved to `22314565`, with five conditions (below).

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
- **GC1–GC16, scope guards:**
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

**agy** (`agy/README.txt`): three passes, each with a control that plants four strengthenings. Every control caught 4
of 4.
- **Pass 1, the first drafts:** both abstracts read DIFFERS. Without "cannot test the width" they could read as
  validating the intervals, so both now add L1's "but does not test interval widths".
- **Pass 2, after the round-5 forms:** H1 read DIFFERS. "using the C_model procedure and the simulation's detector
  response" could read as the response being used or probed, so it now says "the detector response is the
  simulation's and is not probed".
- **Twice declined:** the reading that the note abstract's "the result's intervals" misleads. That clause is the base
  wording and is right.
- **Pass 3, the final text:** all five SAME.

## Checks

| check | result |
|---|---|
| `r19/check_ledger.py . --base 9df8f748` | 227 rows, 396 probes, 192 changed sentences, 0 failures; `--self-test` PASS (47 scope guards, each planted strengthening caught) |
| `make_values_fived16.py --check`, `--self-test` | PASS |
| fived16 rule 7 (no numeral typed by hand in the new prose) | 0. "2p2h" became "MEC" because of it |
| `build_all.sh` | rc 0; paper 12 pp (11 before: the reference list's last column), note 130 pp (129); no undefined reference; no `??`; no pending placeholder; SEC4 15/15 |
| reflow, swallowed-text, registry, results index | PASS |

## For Joseph, in (d)

- **The abstracts' 1A sentences,** as drafts. The paper abstract goes from 203 to 228 words and the note's from 348 to
  373 (`tools/recount.py`). The note abstract's length is already a (d) item.
- **Sec. I now says "Interval coverage has not been validated"** (r5's form), and the abstracts say "The coverage of
  the intervals has not been validated". Whether to align them is a wording choice.
- **The Sec. I pointer for the fake-data study** is fixed (condition 5). It leaves the (d) list.
<!-- absence-ok: quotes the printed and draft limitation wording that this step edits or keeps; not a new absence claim -->

# d2: Joseph's decisions on (d) applied, and the independent raters' choices (2026-10-28)

**Under:**
- `DECISION-20261028-joseph-final-draft-d.md` (main `f9f5a37a`, PR #452), merged into #413 at `13af4709`;
- the director's work order of 2026-10-28.

**Written by** the paper rewrite lane, for the director. The packet for Joseph is `../FINAL-DRAFT-2.md`.

**Records** (this directory):
- `MEASURE.md` and `DA-SURVEY.md`: what is typical, measured;
- `make_candidates.py` and `candidates.json`: the abstract candidates;
- `options.py`: every option, once;
- `make_battery.py`, `tabulate.py`, `raters/` and `raters-v2/`: the blind reads;
- `apply_d2.py`: every edit;
- `agy/`.

## What is applied

| edit | decided by | what |
|---|---|---|
| T1 | Joseph, item 1 | the title. The note's title is its own and unchanged |
| H1 | Joseph, item 5 | IV H takes PRD read r6's sol2 r2 form; `apply_d2.check_h1` asserts that it prints exactly as read |
| ABS-P | raters, item 2 | the paper abstract is candidate PB, 120 words |
| ABS-N | raters, item 2 | the note abstract is candidate NA (v2), 138 words |
| O3 | raters, item 7 | the qualified sentence |
| R11 | raters, item 7 | IV H's R11 sentence |

**Not applied:**
- Data Availability, R1–R4 and `app_release.tex:9` are protected text, so the raters' choices go to Joseph as
  proposals.
- The deposit citation fails the truth column, because nothing is deposited.
- B1 (form i) and B2 (keep both) change nothing.

## The reads

There are two blind batteries, each run by sol2 (both logs `gpt-6.1-sol`) and by gemini, in both orders. The
KEY files that map labels to options were given to no rater. `raters/TABLE.md` and `raters-v2/TABLE.md` are
`tabulate.py`'s output.
- **Controls:** P02 ACCEPT in 8 of 8 runs (and in PRD reads r4–r6). The register control B0 chose the neutral form in
  4 of 4.
- **The first read's network failures:** three gemini runs failed to reach the server ("no such host",
  retryable). They were re-run unchanged, and the outputs are the re-runs.
- **The note candidates were re-read (v2).** The truth column of the first read found that both v1 note candidates
  opened with "The principal result of the analysis is a cross section …". Once the metatext sentence left, that no
  longer named the measurement (MINERvA, ν_μ CC inclusive, OmniFold): ambiguous as read. v2 opens each note
  candidate with the paper abstract's first sentence, which is printed wording. The v1 note result (ND 2, NA 2, split
  by model) is superseded. v2: NA 3 of 4 (gemini 2 of 2; sol2 split by order).

| item | result | runner-up | applied? |
|---|---|---|---|
| A1, paper abstract | PB, 8 of 8 over both reads | PA and PC, tied on mean rank | yes |
| A2, note abstract (v2) | NA, 3 of 4 | ND | yes |
| B1, the coverage wording | (i) "Interval coverage has not been validated.", 4 of 4 | (ii) | nothing to change: Sec. I already prints (i), and PB drops the abstract's sentence. The note abstract keeps its own (iii); the read asked about the paper |
| B2, the flux band | keep both, 4 of 4 | replace | unchanged |
| B3, O3 | the qualified form: sol2 2 of 2, gemini keep 2 of 2 | keep | yes (models split: sol2's true form, round 3's rule) |
| B4, `app_release.tex:9` | keep, 4 of 4 | "directly or through its pointers" | unchanged |
| B5, R1–R4 | scoped, 4 of 4 | keep | a proposal (protected) |
| B6, the caption's deposit citation | add, 4 of 4 | none | **no:** false now, since nothing is deposited. It stays "beyond typical, for later" (item 6) |
| B7, Data Availability | the typical draft, 4 of 4 (strength 3) | current | a proposal (protected), conditional on Q8 |
| B8, the deposit sentence in Data Availability | none, 4 of 4 | add | not added |
| B9, the R11 sentence | add, 4 of 4 | none | yes |
<!-- absence-ok: the table quotes the printed coverage wording the raters chose among; not a new absence claim -->

## The truth column and the guardrail

- **Every applied abstract is whole printed sentences,** so no sentence that stays is weakened.
- **Each dropped sentence's facts still print** (ledger rows D2-M4, D2-M6, D2-M7, D2-A0, D2-A1 and D2-A5–D2-A8; 61
  probes, built and verified by a read-only subagent, then checked by `check_ledger.py`). Three facts are not covered
  by that rule:
  - The paper's joint-test rejections ("five generator predictions all reject at the 5% familywise level") print only
    in the note, which the decision's rule allows. Their limitation ("no evidence of additional discrimination
    beyond matched coarse projections") prints in the paper's Scope paragraph.
  - **"principal result" (A1) prints in no note body file.** The note's executive summary and summary call the
    validation findings the main results. That is the n4 inconsistency, now visible because the note abstract opens
    with "We report a simultaneous measurement".
  - **"on a finer grid" (A6) is never stated;** it can only be inferred from the cell counts. To Joseph.
- **O3's qualified form is true** (sec_5d.tex: "No single cause is established").
- **R11 is true:** |b|/σ is 1.07 with C_e + C_resp alone and 0.62 in full.
- **B6 and B8 fail the truth column for now:** no deposit exists.
- **B7's "provided … in the Supplemental Material"** is true only if Q8 is answered yes and the files are made.

## agy (`agy/README.txt`)

The control caught 5 of 5.
- **Q1, the paper abstract:** SAME.
- **Q2, the note abstract:** DIFFERS on the measurement framing. That bears on n4, so it goes to Joseph, and the
  candidate stands.
- **Q3 and Q4:** DIFFERS, both declined as artifacts of how BEFORE was built (reasons in the README).
- **Q5, the title:** DIFFERS on "on hydrocarbon", which no paper body sentence names. The note's sec_experiment.tex
  does ("polystyrene scintillator"). A DRAFT phrase goes to Joseph.

## Checks

| check | result |
|---|---|
| `r19/check_ledger.py . --base 9df8f748` | 255 rows, 475 probes, 202 changed sentences, 0 failures |
| `--self-test` | PASS: 57 scope guards, each planted strengthening caught; the title, the abstract and the allowance pins each caught |
| `make_values_fived16.py --check` | PASS |
| fived16 rule 7 | 0 numerals typed by hand |
| `build_all.sh` | rc 0; paper 11 pp, note 130 pp; no undefined reference; no `??`; SEC4 15/15 |
| reflow, swallowed-text, registry | PASS |
| `values.tex`, `values_inference.tex`, `app_history.tex`, `app_release.tex` | byte-identical |
<!-- absence-ok: records the measured outcome, what was not applied and why, and two facts found in no note body file; not a new absence claim about results -->

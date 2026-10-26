# Round r18: the history passages to the note, the limitations list into the text (2026-10-25)

**Governed by:**
- `DECISION-20261025-joseph-r18-history-to-note.md` (PR #355);
- `DECISION-20261025-joseph-prd-caveat-convention.md`, with the caveat-study rules R-P1 and R-P3 to R-P7;
- the director's rulings on `outline.md` (2026-10-25).

**Written by** the paper rewrite lane, for the director, who merges.

**Records** (this directory):
- `outline.md`;
- `ledger.md` and `check_ledger.py`;
- `changes.md`, move by move, with what was not adopted.

## What changed

**Base:** origin/main `e270db89`, which is r17 as merged with its accuracy fixes. `paper_body.tex` changes from
`1a0cc74a…` to `fd1af760…`.

**The moves** (details in `changes.md`):
- **S1.** The history of the two superseded 2D statistical bands leaves IV B. IV B now states the quoted block's
  status and points to the note.
- **S2.** VII C has one short statement each of the budget extension and the lost pseudo-experiments, with PR #355's
  four facts.
- **S3.** Fig. 3's seed sentences become "Neither seed set was held out from the estimator's development."
- **S4.** Scope is stated once.
- **S5.** VII E, plainer wording.
- **S6.** III, plainer wording.
- **S7.** The nine-item Sec. VIII A list is folded into the text at the results it qualifies. A prose paragraph
  restates the four principal limitations.
- **S8 and S9.** Process vocabulary is removed. Data-informed choices are stated with their basis.

**Unchanged:**
- no number, claim, citation key, value macro or `\label`;
- the abstract, every `\pubhold` and the release text;
- Table I's rows and its gate-bound values.

**Words in the rater copy:** 9,348 → 9,221.

**Facts that left the paper.** Every one prints in the note, at a ledger row with an `N:` probe:
- the earlier band's test, criterion, failure and rescoring (sec:coverage);
- that the design's reviewers had seen the residuals (sec:joint5d-frozen);
- the interrupted versus never-started split of the lost draws (sec:joint5d-lost);
- the pre-fixed iteration rule (sec:gbdt-model-dependence);
- panel (b)'s separate assessment seeds. This prints in the note through the sentence r18 added to `sec_5d.tex`.

**Approved Table I caption change.** The caption clause "numbers are in the section given, and the limitations in
Sec. VIII A" became "numbers and limitations are in the section given, and Sec.~\ref{sec:limitations} summarizes the
principal limitations".
- The director approved it (2026-10-25): "A caption pointer that S7 makes false has to be corrected … This is a
  presentation change and makes no claim."
- A grep shows that no check binds the caption text: not check_sec4_receipts, not the registry TSVs, not the re2
  inventory. The only match is a historical drafts record.
- agy agrees (unit U15). Ledger row T3.

The Table I 2D-covariance test cell changed to "coverage not tested", as PR #355 item 1 allows. Ledger rows T1 and T2.

## `check_sec4_receipts.py`: three entries now bind note values

The paper no longer prints the superseded bands' values, so the entries that bound them now find them where they print,
in the note. Every entry uses the same computation as before; only the units change, to fractions.

| entry | was | now |
|---|---|---|
| two-sigma nominal | `paper_body.tex` "against \SI{95.4}{\percent} nominal" | `sec_validation.tex` "lies entirely below its window (Gaussian 0.954)"; erf(2/√2), as a fraction |
| rescoring against the rebuilt band, 2 and 1 σ | `paper_body.tex` "\SI{97.7}… and \SI{78.1}…" | `sec_validation.tex` "$C_2=0.977$ $[…]$ and $C_1=0.781$"; `rescore_vl169_toys_vl170.json`, as fractions |
| first-built band, within 2 σ | `values.tex` `\covTwoDCTwoPctOne` (91.2; the paper's form, now unprinted) | `values.tex` `\covTwoDCTwo` (0.912, which the note prints); `interim_score.json` C2 |

- The module docstring now says that it ties three note values.
- The third entry was the I–V reviewer's finding 2. Without the change it would have guarded a macro that nothing
  prints.
- **Results:**
  - `check_sec4_receipts.py`: PASS (15/15);
  - `--self-test`: PASS (18 perturbations rejected), including a one-unit move at each new site: 0.954 → 0.955,
    0.977 → 0.978, 0.781 → 0.782 and 0.912 → 0.913;
  - `python3 -W error`: clean.

## Checks

| check | result |
|---|---|
| `check_ledger.py` (base e270db89) | 61 rows, 76 probes, 50 changed base sentences, **0 failures**; `--self-test` PASS |
| `check_sec4_receipts.py` / `--self-test` | PASS (15/15) / PASS (18) |
| `absence_claims.py` (staged) | 0 bare absence claims; every moved absence claim keeps a `% Search:` line in its paragraph |
| `swallowed_text.py` | 0 flagged |
| `check_registry.py`, after `--repoint`, and `--self-test` | PASS, 0 found-at notes; self-test PASS (the hints are refreshed this round, so CI's self-test does not fail as it did on r17) |
| full build (`build_all.sh`, scratch copy) | exit 0; note 121, primer 15, paper 13, PET note 26, records 55 pages; 0 undefined references; no `??`; the note's new sentence prints |

## Review: two directions, ADOPT-AFTER-FIXES in both batches, no BLOCKING finding

**Secs. VI–VIII.**
- **The S7 mapping holds.** Every clause of the nine old items prints with its condition attached, and the reviewer's
  map agrees with the ledger. VII C carries PR #355's four facts, and the moved mechanics print in the note.
- **Fixed:**
  1. The summary attached the below-grid condition to the hybrid nulls. It now limits the carry-over to the
     predictions.
  2. Table I's caption (approved, above).
  3. "budget" becomes "computing budget of the calibration".
  4. "examined" becomes "seen".
  5. VII D (ii) sentence order.
  6. "central values without intervals of validated coverage".
  7. "The test design".
  8. Stale comments.

**Secs. I–V.**
- **The facts that left IV B all print in the note.** The reviewer checked them line by line.
- **Fixed:**
  - the third SEC4 entry;
  - "therefore" in V D, which had lost its base basis. The moved seed sentences now follow it.
  - the dangling "criterion", now "The comparison";
  - "Its source", now "The source of this residual bias";
  - the roadmap restatement;
  - Table II's sentence, now "lists the configurations and the results each is used for";
  - "Their pseudo-experiment seeds";
  - the docstring wrap and wording;
  - stale comments.
- **Not adopted:**
  - **Finding 6:** the base qualifier on the coverage claim stays.
  - **Finding 7:** the status-first order is the director's example.
  - **The comment in `check_dead_containment.py`:** that file's digest is recorded in
    `nd-unfolding/gbdt_model_dependence/build_evidence.json`.

## agy agreement

- **Paper:** 16 changed units, with a context block naming every fact that moved and where it now prints.
  - First pass: 15 AGREE.
  - U12 (VII E): REVISE. "The decisions … test each prediction" is a category error. Fixed with agy's "concern",
    then AGREE.
  - **Final: 16 of 16.**
- **Note sentence:** REVISE first. The draft "separate from those of the development studies" was more specific than
  the source. Replaced by agy's wording, which is the pre-r16 caption's, then AGREE.

## Blind pairwise comparison (P2, both orders, both models)

**NEW wins 4 of 4, with no order flip.**

| | revision | blinded copy sha256 | words |
|---|---|---|---|
| OLD | `e270db89` (r17 as merged) | `74d21334f55cc086…` | 9,348 |
| NEW | this round | `caf8f6aab105f534…` | 9,221 |

| model | order | winner | strength |
|---|---|---|---|
| sol2 | A = OLD, B = NEW | B (NEW) | 1 |
| sol2 | A = NEW, B = OLD | A (NEW) | 1 |
| gemini | A = OLD, B = NEW | B (NEW) | 2 |
| gemini | A = NEW, B = OLD | A (NEW) | 2 |

**Reasons the raters give:**
- NEW embeds the limitations in the analysis sections, rather than keeping "an enumerated nine-point list … that
  resembles an internal review memo";
- NEW drops "the granular account of abandoned statistical bands";
- OLD has pre-registration and review vocabulary ("its reviewers had already seen …", "predeclared design",
  "and they stand", "In a post hoc observation").

## P1 (absolute rubric score)

| rater | r17 (scored text) | r18 |
|---|---|---|
| sol2 (gates) | 3, 3, 3 | **3, 3, 3** |
| gemini (reported only) | 2.5, 2.5, 2.5 | 2.5, 2.5, 2.5 |

The P1 baseline is r17's scored text, `63f1d61b`, which r17's accuracy fixes changed only slightly.

**What the sol2 justifications quote now.** All three say "repeated qualifications, configuration bookkeeping, and
development-history passages":
- **III, the configuration (f) sentences** ("uses configuration (f): the learner and seed of configuration (a) …";
  "This reproducible central value …"): 3 of 3 runs. These are the lines the registry cites. Q3 kept them
  byte-identical this round.
- **VII C, the design and budget sentences:** 2 of 3 runs.
- **Data availability** ("A candidate release package …"): 2 of 3 runs. This is Joseph's text.
- **V D, "The covariance of the five-observable central value …":** 1 of 3 runs.

## Adoption

**Adopted.**
- (1) NEW wins 4 of 4.
- (2) sol2 picks NEW in both orders, at strength 1.
- (3) P1 sol2 does not fall.

**Stop rule: not met.**
- The pairwise still prefers the new version in both models.
- P1 sol2 is below 3.5.
- This is round 2 of at most 4 for the paper.
- **What holds the score at 3:** the passages above.
  - Two are outside a register round's reach as currently ruled: the registry-cited (f) lines and Joseph's
    data-availability text.
  - One is the joint-test disclosure that Joseph's decisions require (D1).
- A round r19 would target III with a registry refresh, VII C's two sentences and V D.

## The rater-copy tool

`rater-calibration/tools/fix_da_order.py` gains case 3. In this layout the data-availability text's continuation
printed between the acknowledgments and the DATA AVAILABILITY heading. Case 3 moves it back after the first sentence,
and an order assertion checks the result. On the r17-base, r17 and r17-merged copies the output is byte-identical to
before.

## For Joseph: proposals only, not in the scored text

**1. The abstract (R-P8; DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md item 1).**

R-P8 says the abstract carries scope only, but the abstract's caveat-coded sentences are this methods paper's main
validation findings (Table I's rows 4–6 and 8). The one comparator whose headline is a negative result, P3, keeps it in
its abstract ("remains an open problem"). P1's abstract does not state its negative comparison; the body does.

So the proposal removes no clause and changes one sentence, from negative-first to measured-result form:

> Pseudo-experiments ~~reveal background-subtraction bias, incomplete recovery~~ **measure a background-subtraction
> bias, a partial recovery** of generator-sized truth changes, and statistical undercoverage at the tested truths.

| removed clause | lands in the body |
|---|---|
| none: every clause stays in the abstract | (no move) |

- agy read a draft that also reworded the precision sentence, and asked to keep "no tested reporting definition meets
  our 10% precision criterion", because the reword added a metric. The proposal keeps it.
- The proposal lands only if Joseph approves the wording, as an add-on commit or in r19.

**2. Data availability (PR #355 item 5).** This is Joseph's text, and r18 did not change it. Proposed wording, with
agy AGREE:

> The input data and simulation are the MINERvA open-data AnaTuples, released under CC0 [12]. This analysis used an
> earlier production of that release, whose 2,374 input files are identified by SHA256 checksum in the records cited
> in Ref. [14], App. G. A candidate release package of about 16 MB, which requires only numpy, scipy, and matplotlib,
> recomputes every $p$ value, decision, robustness result, and power figure of the joint tests and the numbers quoted
> in Sec. VII A, and regenerates the analysis note's figures of the joint-test null distributions and the
> $(E_{\rm avail},W)$ map. It has not yet been deposited. Reproducing the other quoted numbers, except the multiplier
> scan, and the event-level processing requires the archived analysis products, the open-data AnaTuples, and the
> generator samples produced for this analysis. Ref. [14], App. G states what each part of the release reproduces and
> what it does not.

Every fact stays: candidate, about 16 MB, the three packages, what it recomputes, not deposited, what else is
required, and App. G's scope. The `\pubhold` follows unchanged.

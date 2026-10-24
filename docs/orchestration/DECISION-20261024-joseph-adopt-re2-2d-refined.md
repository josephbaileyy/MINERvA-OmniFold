# DECISION 2026-10-24 — Joseph: adopt the refined 2D result E_R and Q_R; Fig. 1 approved with a legend fix; scope (ii) for now

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **RE-2 part C** ran as bound by `RE2-BINDING-C.md` and its amendments 1 and 2. Its report,
  `state/2d-closeout/stageF/methods/re2/RE2-PARTC-REPORT.md` (PR #326, merged at `923441e2`; the file's sha256 begins
  `70d620bac2994a42`), gives:
  - the refined 2D covariance `Q_R`, per-cell median 6.41 % (Q: 6.45 %);
  - `E_R − E_U` per cell, median 0.06 σ and max 0.48 σ of `Q_R`;
  - the published comparison on `E_R` and `Q_R`. For example, χ²/ndf against the published covariance is 2.27
    (2.65 before), and 86.8 % of bins are within 5 % (82.9 % before);
  - C_model beside `Q_R`, with the users' total `Q_R` + C_model at a median of 7.90 %;
  - 241 regenerated printed values, each after its positive control reproduced the printed one.
- **The director's recommendation:** adopt. It is the estimator DECISION-20261023 (`-2d-refined-integrate-ci`)
  item 1 chose, and every bound control passed.
- **The director's questions to Joseph:**
  1. review Fig. 1 visually (ruling Q3);
  2. adopt `E_R` and `Q_R`;
  3. approve the wording, drafted by the director, before anything prints.

Joseph's answer, verbatim:

> what are your recommendations? this is what I am thinking so far for the first decisions you sent: decision 1: (b) but are you saying its impossible to validate 5d? decision 2: what did re-2 part C report? and how did it inform this decision? new decisions 1: new fig 1 is good but can we standardize the capitalization in the legend? 2: yes 3: okay

sha256 of the text plus a final newline begins `5820a4ba71c41f07`.

## What is decided

1. **The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty.** This replaces `E_U` and Q.
   - C_model stays separate, beside `Q_R` (DECISION-20261024, `-2d-model-dependence-component`, item 1).
   - The users' total is `Q_R` + C_model.
2. **Fig. 1 is approved,** on the refined products (`fig1_validation.pdf` `cabbbbc3…`), with one change: the
   legend's capitalization is standardized to sentence case. "published ±1σ" becomes "Published ±1σ", and "this work
   ±1σ" becomes "This work ±1σ". That is a change to a bound file (`publication/release/figs/make_figs.py`, pinned by
   `re2c_fig1.py`), so it goes through an amendment to RE2-BINDING-C with a check that only the legend text changes.
3. **Wording:** the director drafts every changed sentence, and Joseph approves each one before it prints. That
   covers:
   - the C_model sentences;
   - the comparison with MINERvA's published result;
   - RO-FPS (3.069e-38 against 3.073e-38, which no longer reproduces);
   - `sec_systematics.tex:101`'s S2 diagnostic;
   - `\fpsAbove`;
   - the 22 sites handled by hand.

   **How the drafts are checked** (Joseph, a later message the same day, verbatim:
   "for your wording, can you make sure it sounds PRD style and give it (with the paragraphs around it in the note/paper as context) to agy and make sure it agrees?";
   sha256 of the text plus a final newline begins `ecb4f57d2ae8a509`):
   - every draft is written in PRD register, under the PRD-study rules (`register-prd-study/REPORT.md`);
   - each draft goes to agy with the paragraphs around it in the note or the paper as context;
   - a draft goes to Joseph only once agy agrees with it. A disagreement is revised and resubmitted, or brought to
     Joseph with both versions.

4. **Measurement scope: (ii), "for now".** The measurement is the 2D (p_T, p_∥) result, `E_R` with `Q_R` and
   C_model beside it, together with the higher-dimensional central values and their model dependence stated. That
   is the community-standard fallback of DECISION-20261023 (`-5d-targets-and-paper-round-2`). No coverage
   validation is claimed for them. Joseph's follow-up message, verbatim:

   > decision 1: I really just want to try and get a published 5d measurement, what would it take for this? maybe its worth trying asking a fresh context session with a minimal prompt like codex with gpt 6.1 sol high what they think for an outside perspective? decision 2: (ii) for now

   sha256 of the text plus a final newline begins `cb37249f965549a6`.

## Not decided here

- **The R10 / 5D question.** Joseph wants to try for a published 5D measurement. He asked what it would take, and
  for an outside opinion from a fresh-context session. Option (b), redesigning R10's null control, is not yet
  decided.
- **No claim change.** Claims and KI-85 are Joseph's.
- **No release candidate.** The release appendix's digests describe the release candidate as built.

## What follows

1. RE2-BINDING-C amendment 3, for the legend, and the bound redraw.
2. **One integration batch** into the note, paper and primer, which lands only with the wording approved:
   - `E_R` and `Q_R`;
   - the values table's 241 regenerated values;
   - C_model beside `Q_R`;
   - the new Fig. 1;
   - `check_sec4_receipts.py` repointed at `Q_R`'s `budget_Q.json`.
3. Then a new reading copy, and the sync of the standalone note repository.

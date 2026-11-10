# DECISION 2026-11-09 — Joseph: configuration (e) is frozen as the methods paper's baseline, with the ensemble reported as a tested mitigation; the consult's ranked plan is adopted; the bias–variance study of the ensemble starts after the methods paper's compute, which the paper does not wait on

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The question.** The round-5 referee reads all flag the rounding instability (`secondary-results/referee-methods-round5-20261109/README.md`).
  Joseph asked whether the major-revision step is to rerun with a fix. The director set out three options:
  - (A) keep configuration (e) and state the instability;
  - (B) adopt the 96-fit ensemble E₉₆ despite ENS1's BIAS_WORSE (`OUTCOME-20261109-ens1-stab-pass-bias-worse.md`);
  - (C) a new held-out bias test of E₉₆ before adopting it.
- **The consult.** At Joseph's request, a fresh codex-school2 session (gpt-6-astra, high, read-only at main `82ee901c`)
  gave an independent read: `secondary-results/consult-astra-publishable-path-20261109/` (#975), with `answer.txt`
  verbatim. It recommends:
  - a short methods-and-validation paper, with the measurement a separate conditional goal;
  - (e) frozen as the studied baseline, its instability presented as a result, and E₉₆ shown as a tested mitigation
    with mixed outcomes;
  - completing FD-PRR and LL5D on (e) within their caps;
  - deferring any replacement estimator to a declared bias–variance (mean-squared-error) trade-off study at reserved
    truths, priced before launch;
  - a ranked plan, and work to stop.
- **The consult's cost arithmetic** (an extrapolation, not a price):
  - one E₉₆ covariance rebuild is about 497 node-h;
  - an E₉₆ coverage test at LL5D's scale is about 3,642 node-h, above the group's remaining balance;
  - so only (e) can carry a coverage test.
- **The director's recommendation** agreed with the consult, and put two questions to Joseph:
  1. freeze (e) as the methods baseline;
  2. declare the stronger study, or skip it.

## Joseph's answers, verbatim

> Lets do what you and astra recommend, and I can tell Ben that we can start the stronger study as soon as we finalize everything for this initial methods paper we publish

sha256 of the text plus a final newline begins `0b8b9f78cfb98323`.

His follow-up, verbatim:

> although if we do finish all of the methods paper compute it doesn't hurt to start on the new compute too right? to use up the hours we have as we still have them

sha256 of the text plus a final newline begins `1e196774065b3092`.

## What is decided

1. **Configuration (e) is frozen as the methods paper's baseline estimator.**
   - Its rounding instability is reported as a result of the study.
   - E₉₆ is reported as a tested mitigation: it meets the stability bars, and it is BIAS_WORSE at one of 17 truths,
     with ENS1's licences unchanged.
   - No estimator is replaced.
2. **The target is a short methods-and-validation paper** (the consult's "JINST-type" venue). This reaffirms
   `DECISION-20261106-joseph-methods-study-and-archive.md` item 1. The measurement remains a separate, conditional
   objective. The venue itself is Joseph's, at submission.
3. **The ranked plan, in order:**
   1. freeze the methods claim, and audit V-HALF (`DECISION-20261109-joseph-bias-half-rule.md`) and any localization
      claim, at 0 node-h;
   2. finish FD-PRR within its 27.0 node-h cap;
   3. finish LL5D on (e) within its 148.0 node-h cap, whichever verdict it reads;
   4. write a short, self-contained paper and a reproducible result package, read by Joseph and a human experimental or
      statistical reviewer before submission.
4. **The bias–variance study of E₉₆ (the strengthened option C) comes after the methods paper's compute.**
   - It is declared, audited, priced and bound once FD-PRR and LL5D have ended, and it may then run while the paper is
     written, so the remaining hours are used. This is Joseph's follow-up below.
   - **The initial methods paper neither waits on it nor changes because of it.** Its result, either way, belongs to
     the next paper. If it lands before submission, nothing about it enters this paper without a new decision by Joseph.
   - Its launch follows the usual gates: it is priced from measured rates, and a campaign above half the balance goes
     to Joseph.
   <!-- absence-ok: a scheduling rule for a future study, not a claim that a result does not exist -->
5. **Stopped:**
   - broad hyperparameter or numerical searches;
   - wording-only referee rounds;
   - further GEANT_Neutron / GEANT_Proton band studies;
   - selecting run periods by their agreement with the publication.
   Referee rounds resume only on a changed paper, after FD-PRR and LL5D land (paper round 6).
6. **The advisor's story is held to the records.** The paper does not claim:
   - that 5D validates the full distribution, beyond the 2D benchmark with its stated limits;
   - that V-HALF identifies detector inadequacy (it grades bias under simulated truths);
   - that the 2D mismodeling is localized in the extra dimensions. That needs its own declared test, and until then it
     is a stated next step.
   Any sentence on these goes through the PRD-referee read and Joseph.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the baseline choice, the plan and the deferral, as Joseph's decision.
- **Not citable for:** any statement that E₉₆ is better or worse beyond ENS1's licences; any coverage statement; the
  consult's views as findings; any paper or note sentence without the PRD-referee read and Joseph.

Nothing is submitted, deposited or tagged.

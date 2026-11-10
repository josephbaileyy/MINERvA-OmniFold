# DECISION 2026-11-10 — Joseph: V-HALF-R's open choices: C6 and C7 must be included; the six design recommendations are adopted, with three clarifications fixed before binding

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **V-HALF-R** (#1016, DRAFT) is the follow-up paper's pre-declared rebinning and candidate-observable study. It
  answers the advisor's suggestion to pick observables on which the per-cell rule V-HALF passes. Its §7 left choices
  open for Joseph.
- **The decision packet** (`state/2d-closeout/valid-region-20261107/v-half-r/CHOICES-FOR-JOSEPH-20261110.md`, PR #1043
  at `af9289a81`, by the limitation-resolver lane) set out each choice with options and a recommendation. It folds in
  V-HALF's 16-cell result, the confirming round's referee remark on low-stability cells
  (`referee-methods-confirm-20261110/claude.txt:174-176`), the director's Tier 2 reading (`READING-T2-20261110.md`)
  and Tier 3's corrected question.
- **An independent consult** at Joseph's request (codex-school `gpt-6.1-sol`, high, read-only;
  [`v-half-r/consult-sol-20261110/`](state/2d-closeout/valid-region-20261107/v-half-r/consult-sol-20261110/)) agreed
  with the six design recommendations, with qualifications, and asked for three clarifications before binding.

## Joseph's answers, verbatim

On the must-include candidates:

> C6 and C7 (Recommended)

(sha256 of the text plus a final newline begins `c7acdfc74f33ad8d`). On the six design choices, first:

> can you ask a codex-school gpt 6.1 sol for what it thinks?

(sha256 begins `f99a5a8d6c45175d`), and then, after the consult:

> Accept six + 3 fixes (Recommended)

(sha256 begins `c0131a734259e713`).

## What is decided

1. **Must-include (§7 item 3):** C6 (p_T, p_∥) and C7 (E_avail, q3) are both required. Joseph chose the option that
   confirms C7's physics reason, the hadronic-energy against momentum-transfer contrast. If either ends with no
   reportable binning, that is the reported outcome; a passing optional candidate does not replace it.
2. **The six design choices**, as the packet recommends:
   - (1) the binning criterion is min(purity, diagonal fraction) ≥ 0.5, one threshold, also used to order the joins
     (§1.2 is amended);
   - (2) the candidates are C0–C8 as drafted, frozen at the binding;
   - (4) the phase space is the 16-cell reported domain;
   - (5) the disclosure's first sentence is extended to say that the rule was set after the 16-cell V-HALF result and
     the referee's remark were known, and to name the graded estimator if Tier 3 leads to a change;
   - (6) the criterion is a final requirement for every reported bin; the outcome table states both fractions and
     the support rule consistently;
   - (7) the cancellation listing is per fine cell for C1–C8 and per R-cell for C0, machine-readable, and reconciled
     to the scored bin quantities.
3. **Three clarifications go into the amendment before audit and binding:**
   - (a) **the two-dimensional resolution** C6 and C7 must keep, so that strips integrating over one whole axis cannot
     satisfy the bin floor. It is set from physics, without consulting any candidate's bias, and confirmed by Joseph
     or Ben;
   - (b) **the domain boundary:** projected bins are rectangles intersected with the fixed 5D mask, with an explicit
     account of migration across the mask in both directions;
   - (c) **freezing:** whether C2 and C6 may join across p∥ = 4.5; the graded estimator, frozen by name and digest; and
     the reserved-truth confirmatory step, specified before those truths are examined.
4. **Run order:** the valid-region lane amends #1016. Then come the code, coverage-5b-audit and the director's
   binding. The study runs only after Tier 3 reports and Joseph has decided whether the estimator changes.
5. **Unchanged:** V-HALF-R is follow-up work. The methods paper reports V-HALF as a diagnostic on R00–R15, with no
   rebinning.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the choices; the run order.
- **Not citable for:** any V-HALF-R result, or a claim that any candidate will pass.

Nothing is submitted, deposited or tagged.

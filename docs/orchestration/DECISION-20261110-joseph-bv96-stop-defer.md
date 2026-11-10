# DECISION 2026-11-10 — Joseph: the ensemble bias–variance study (BV96) stops as an MSE study and runs nothing; a held-out bias comparison is deferred to the follow-up paper's planning

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **BV96** (#1017, DRAFT) declared a paired MSE comparison of configuration (e) with the 96-fit ensemble E96 at two
  reserved truths, on the 153 functionals, with M = 30. It was planned under
  `DECISION-20261109-joseph-methods-baseline-and-plan.md` item 4.
- **Its power check** (O1, #1017 at `b738074e`) found P(E96 detectably better at both truths) of about 0.001 at
  M = 30. The reason is that at generator-shape truths (e)'s bias is large, so MSE is bias-dominated, and E96's
  variance-only gain is unresolvable at affordable M.
- **An independent consult** (codex-school2 gpt-6-astra, high, read-only at `b738074e`; committed with #1017)
  recommended stopping BV96 in its present form. It recommended a redesigned bias study only once a result that would
  justify advancing E96 is specified first. It also corrected the extrapolation: the worst-truth M₈₀ is about 52,200.
- **The director recommended** recording the finding, and deferring a held-out bias comparison to the follow-up
  paper's planning.

## Joseph's answer

> okay sounds good. also I like the new paper draft. […]

The full message also raised figure and table presentation points, which are handled on #977. Its sha256 plus a final
newline begins `7684e95e62297ec8`.

## What is decided

1. **BV96 stops as an MSE study and launches nothing.** #1017 becomes a findings record. It holds the scale finding,
   the power planning and the consult's corrections; the design is archived as never run.
   <!-- absence-ok: this decision's own instruction (nothing launches), not a claim that a result does not exist -->
2. **A held-out bias comparison of E96 with (e)** (the consult's redesigned option b) is deferred to the follow-up
   paper's planning. There it is declared only after the physics contrasts, the acceptable absolute bias, a
   non-inferiority margin and a variance-reduction target are specified. That is the same physics basis V-HALF-R's
   minimum-cell question needs. It needs its own decision.
3. **Unchanged:** E96 is reported in the methods paper as a tested mitigation (the plan decision, item 1). No preference
   between E96 and (e) is claimed.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** stopping BV96; the deferral.
- **Not citable for:** any preference between E96 and (e); any measurement claim.

Nothing is submitted, deposited or tagged.

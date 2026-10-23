# DECISION 2026-10-23 (fifth) — Joseph: the 5D design's target changes; another paper register round

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The measurement session's 5D measurement design (`state/measurement-paper/5d-design-20261023/
DESIGN.md`, PR #284) ends with eight decisions for Joseph (§11). The director gave a recommendation on each. The r15
register round won the blind pairwise comparison 4 of 4, and its absolute score stayed at 3.0.

Joseph's answer, verbatim:

> yes I think we should do another round for the paper. for the eight decisions:1. what is rd2 again?  2. keep it. 3. agree 4. agree 5. agree 6. yes I will send the message when you agree its ready to be sent 7. agree 8. what is M1 vs M2 again?

sha256 of the text plus a final newline begins `d964099b217223fd`.

## What is decided

- **Another paper register round** follows r15 once r15's review fixes land. Its targets are the passages the P1
  raters still flagged.
- **2. T1 is kept:** a 10 % median total 68 % half-width. With the 1.4 % normalization floor, the bar on the model
  term is 8.6 % (DESIGN §6).
- **3. T2 changes.** The 5 % cap on the model component is replaced by a validated-coverage requirement: the model
  term must cover the bias at held-out truths, at the rule the stage declarations fix. The recovery clause is
  reported descriptively and is no longer a target.
- **4. T4 changes.** "Total" means statistical plus model. Systematics are carried as covariance blocks.
- **5.** The route "prior dependence carried as an uncertainty component" (`PLAN.md:385`) is reopened, through items
  2–4.
- **6. GPU use.**
  - Joseph sends his note to Ben when the director says it is ready.
  - Stages 2–4 (about 360 GPU node-h) count as tests and run only after Stage 0 and R10 pass.
  - The large stages need Joseph's campaign criterion (DECISION-20261023 first, item 3) and Ben's agreement.
- **7.** The community-standard alternative (publishing without coverage tests) is kept as the fallback if Stage 0 or
  R10 fails.

## Decided after the director explained RD2 and M1/M2

The director explained both. Joseph's answer, verbatim:

> okay sure I agree with your recommendation for 1. and 8.

sha256 of the text plus a final newline begins `9a0d9ad9aab53588`.

- **1. The reporting definition is predeclared:** RD1 (109 J cells) if it passes Stage 0. Otherwise RD2 (H2: 27 cells of
  a 2⁵ partition, still joint in five observables). The rule is fixed now, before any Stage 0 output. Joseph accepts
  RD2's coarseness as the fallback; that is a stated exception to DECISION-20261019 §1a, limited to this fallback.
- **8. M2 is declared:** the model term is correlated, C_model = κ² Σ_k s_k s_kᵀ, one fully correlated component per
  vertex (DESIGN §2.2).
- **W is fixed by item 2:** W = 10 %, so Stage 0b's bar on the model term is 8.6 %. Stage 0's analysis (Part A) may
  now be declared and bound.

## Not changed

- No campaign is authorized. Stage 0, a 0 node-h read of existing products, may be declared and bound now, because it
  depends on none of the open items. Claims, and MP-2's hold, are unchanged.

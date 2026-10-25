# FD: the director's rulings on the fake-data plan (2026-10-25)

**By** the paper-tighten lane, as director.

**Rules on** [`FD-PLAN.md`](FD-PLAN.md) §7. That plan is PR #352, merged at `a54a10be`, and its file sha256 begins
`aca777c46bca27d2`.

**Under** `DECISION-20261025-joseph-scope-5d-fake-data-test.md`.

**MEASURES:** nothing.

**CANNOT AUTHORIZE:**
- compute, including F0's login-node work, which needs Joseph's approval of the plan, then a declaration and a binding
  (decision item 3);
- Stage G's read of the data, which needs Joseph's own approval after F0 reports (decision item 2);
- a claim, printed wording or a publishability conclusion, which are Joseph's.

**The plan is accepted as the costed plan for Joseph.** Each of the six questions in §7 is ruled on below. A
declaration for F0 follows these rulings without reopening them.

## 1. Merging: the rule does not admit one

- **The substitute rule.** The H2 decision ("What led to it") replaced route item 2's clause with two conditions:
  - a merge uses only simulation and generator-truth quantities;
  - the rule is committed "before any H2-level quantity is computed from an (e) data product in this pipeline".
- **Why neither condition can hold for a merge prompted by F0:**
  - The C_model,5D build (2026-10-24T21:44Z) and S1's assembly (2026-10-25T05:45Z) have computed exactly those
    quantities.
  - F0's grades divide by C_e, s_k and f, all of which come from data.
- **Ruling:** the "cell merge" outcome leaves §3.6.
  - A FAIL leads to a proposed limitation and the fake-data table, both for Joseph.
  - Joseph may still change R00–R15, since the definition is his. Any such change is labelled post hoc wherever it is
    reported.

## 2. Thresholds: reporting triggers, not gates

**Bound as proposed.** These are the triggers for listing a truth or a cell in the proposed limitation:
- |z| > 2 per cell;
- or a χ² with P(χ²_16 > χ²_T) < 0.01 per truth;
- both against the leave-own-vertex-out C_total for a vertex-family truth, and the full C_total otherwise.

**The report must also print:**
- the denominators: the number of cells with |z| > 2 out of 18 × 16 = 288, and the number of truths with p < 0.01 out of 18;
- beside each, the count a Gaussian reference would give: about 13 of 288 and 0.18 of 18. That is context only, since b is a deterministic bias (§3.3);
- each count by truth family. The vertex-family, non-vertex and prior truths are not pooled.

**The model-only variants** stay descriptive and carry no threshold. They drop all five systematic blocks, so they
are a lower bound on C_model's reach (§3.2), not a reported uncertainty.

## 3. S-3, the spread test: kept out

- It stays out of F0.
- Its expected value needs a derivation that does not yet exist (§3.4).
- Adding it after F0 has been read would be post hoc. If it is ever wanted, it comes as its own declaration, with
  the derivation first.

## 4. New truths outside the vertex set: deferred until after F0

- **F1 (GENIE v3).** The configuration is Joseph's choice. The rule at `stageD-inputs/REPORT.md:297` bars any lane that
  tunes the recipe from choosing it. The director has ruled on this result's recipe, so it does not choose.
  - Joseph is asked after F0 reports, with F0's results in hand, and only if F0 leaves a question F1 would answer.
  - The F1a pilot does not run before that.
- **F1-W (data-driven truth).**
  - Building a truth from the reco-level data distribution **is a read of the data**, at reconstruction level. It is
    not a read of the unfolded result.
  - It is admissible only if its recipe is frozen and committed before the data/MC ratio is computed: the variables,
    the smoothing, the amplitude and the seeds.
  - The choice to include it is Joseph's, after F0, under the same rule as F1.

## 5. GiBUU in Stage G: eight cells, as declared

- R04–R07 and R12–R15 span p_∥ 4.5–60 GeV/c. There, GiBUU's missing E_ν > 20 GeV share is 4.9–5.3 % of the cross
  section at 6–10, 43–44 % at 10–20 and all of it at 20–60 (addendum §1). A χ² there would test the sample's coverage,
  not the model.
- **Ruling:**
  - GiBUU is compared on the eight p_∥ < 4.5 cells only, with ndf 8 (7 for shape only);
  - no 16-cell GiBUU χ² is computed;
  - any figure that shows GiBUU at high p_∥ marks it as incomplete there, in wording Joseph approves.

## 6. Using f as a divisor is not a read for Stage G

- F0 uses f only to make C_e fractional, and the same values are printed in `cmodel_5d.json` key `x`.
- The blinding that Stage G protects is of the comparison f − g.
- **Ruling:**
  - F0's use of f is not a read for the purposes of decision item 2;
  - F0's tool prints no f, no absolute cell value and no f − g;
  - its synthetic tests check that the tool prints none of them.

## 7. For F0's declaration

- **It carries:**
  - these rulings;
  - the plan's controls 0–8;
  - the triggers and denominators of §2 above;
  - the row 4 HPSS copy.
- **It runs under** the usual stop rule: any refusal or non-zero exit is reported unrepaired.
- **It writes** nothing to CFS, and the HPSS copy takes the 14.7 MB of the `f4` products.

## Not changed

- The S1 covariance, C_model,5D, R00–R15, κ = 1 and the route decision.
- No GPU and no premium QOS.
- Claims, KI-85 and publication are Joseph's.

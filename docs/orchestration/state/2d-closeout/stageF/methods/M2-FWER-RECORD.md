# M2: the familywise error of the sequential decisions (record)

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19, methods-paper item M2
([`../METHODS-FRAMING.md`](../METHODS-FRAMING.md)).

**CITABLE FOR:**
- the bound on the familywise error of the ten s5p decisions under any stopping;
- the assumptions the bound rests on;
- the replacement for the paper's "p values remain valid" sentence.

**NOT CITABLE FOR:**
- calibration exactness (assumption A1 below, which is what SF-1 and the text address);
- any change to amendment 7's decisions;
- final wording (J3–J5 provisional).

## 1. Sources

- **[`M2-AUDIT.md`](M2-AUDIT.md):** an independent Claude audit of the calibration's probability model, Q1–Q4, at
  `19b46af9`. Its derivation of the bound is in Q2.
- **[`m2-calc/director_seqsize.py`](m2-calc/director_seqsize.py):** the director's earlier scratch calculation. The
  audit reproduced it to three decimals, after deriving the bound independently (`m2-calc/fwer_*.py`,
  `cont_rest.py`).
- **[`m2-calc/gpt-6.1-sol-check.md`](m2-calc/gpt-6.1-sol-check.md):** an outside check of the derivation by
  codex-school GPT-6.1-sol, with its prompt alongside. Verdict: **correct with caveats**.
  - The event inclusion and the first-true-null Holm reduction are sound with arbitrary dependence. Ordering by p̂,
    the undetermined branch, shared stopping and budget decisions made with results visible do not defeat them.
  - Uniform p is the worst case for the crossing event.
  - The caveats: the constant was not certified numerically; the production-specific 0.81α was not established;
    and the observed-count likelihood (P(K=0 | p=0.005) ≈ 0.0012) is not an error bound.
- **[`m2-calc/certify_crossing.py`](m2-calc/certify_crossing.py) → [`certify_out.json`](m2-calc/certify_out.json):**
  the director's certified computation, which answers the first caveat.
  - It computes, at each Holm threshold c = 0.05/j for j = 1..10, an exact dynamic program in p for the event that
    the 95% Clopper–Pearson upper end falls below c at some B ≤ 1999.
  - That probability is nonincreasing in p, so a left Riemann sum over 6,000 points plus the tail term
    (1−h)·g(h) is a rigorous upper bound.

## 2. Result

| j | c = 0.05/j | R(c)/c, certified interval |
|---|---|---|
| 1 | 0.0500 | [0.8892, **0.8902**] |
| 2 | 0.0250 | [0.8247, 0.8257] |
| 3 | 0.0167 | [0.7743, 0.7753] |
| 5 | 0.0100 | [0.6907, 0.6917] |
| 10 | 0.0050 | [0.5138, 0.5148] |

The other thresholds lie in between; all ten are in `certify_out.json`.

- Holm gives FWER ≤ max over m₀ of m₀·R(α/m₀) = max over j of R(c_j)/c_j · α. That is **at most 0.8902α**, or
  **at most 0.0446 for α = 0.05**, under any stopping at or before 1999 pseudo-experiments.
- "≤ 0.89α" as previously written is **not** certified, since the bound is 0.8902. The paper states **"at most
  0.9α"**, or "below 0.045".
- The tighter figures (0.81α for the rule as coded, 0.844α on the batch grid) are not used. The production looks
  were irregular and the frozen-rule calculation does not model shared stopping.

## 3. Assumptions (stated with the bound)

- **A1:** for each true null, the calibrated tail probability is super-uniform. This is the calibration-exactness
  assumption: what the nuisance-averaged calibration, the half-versus-full simulation step (SF-1) and the scope
  statement address.
- **A2:** conditional on the data, the retained exceedance indicators form an iid Bernoulli stream. This requires
  product losses to be independent of outcomes. The losses were slow-node timeouts; they are not shown to be
  outcome-independent.
- **The rule:** each decision uses at most 1999 draws; each rejection passes the 95% CP upper-end gate; Holm stops
  at the first failed gate; and the variant maximum includes the unshifted variant at a common B.

## 4. Replacement text (for `paper_body.tex:843-844` and `sec_joint.tex:111-112`; provisional, J4)

> A hypothesis is rejected only when the upper end of the 95% Clopper–Pearson interval of its exceedance fraction lies
> below its Holm threshold. If each true null's calibrated tail probability is uniformly distributed or conservative,
> and the pseudo-experiments' exceedances are independent given the data, the probability of passing this gate at any
> number of pseudo-experiments up to 1999 is at most 0.9 times the threshold, whatever rule determines when sampling
> stops, including the budget extensions. The familywise error rate of the ten decisions is therefore at most 0.9α.
> The point estimates (k+1)/(B+1) carry no separate validity claim.

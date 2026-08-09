# FINDING 2026-08-09 — Stage 6's central-reproduction gate cannot pass, and it encodes the convention we rejected

**This is the yield of building the CANDIDATE without a verifier PASS.** The question that
justified the exercise was whether stages 4-6 have defects of their own. Answer, on real products:

- **stage 4 (build components)** — clean. 45 bands, 40 retained, all measured identities at or
  below 4.6e-14 against a 1e-9 rtol.
- **stage 5 (validate)** — **PASS**, eleven named gates, including the new
  `candidate_self_declares_non_adoptable`. Also clean.
- **stage 6 (project 5D→4D)** — **FAIL-CLOSED**, and not marginally.

Stage 6 had **never executed before** (repair-4 established that stages 4-6 were unreachable). This
is first contact.

**Nothing was changed to make it pass. No tolerance was touched.** The decision this raises is
Joseph's, not mine.

---

## 1. What the gate demands

`p4_project_4d.py:86` → `p4_lib.check_projection_nonmutation(..., rtol_central=CENTRAL_REL)` with
`CENTRAL_REL = 3.0e-2`, hardcoded and deliberately not a CLI knob.

It builds `M`, the W-marginalisation matrix, and requires

    max over 4D reported bins of  |M @ x5 − x4| / |x4|   ≤  3 %

where `x5` is the 5D central (`products/5d/xsec_5d_MEFHC_5iter_lgbm.root`) and **`x4` is the
INDEPENDENT 4D unfold** (`products/4d/xsec_4d_MEFHC_5iter_lgbm.root`).

So the gate asserts: *the 5D→4D marginal must reproduce the independently-unfolded 4D result,
bin by bin, to 3 %.*

## 2. What is measured

Diagnostic on central vectors only (the 42 GB candidate covariance is not involved):

| quantity | value |
|---|---|
| 5D reported bins / 4D reported bins | 10 694 / 4 830 |
| **reported gate failure** | `projection mutates central (max rel 1.00e+00)` |
| 4D reported bins receiving **zero** from the 5D support | **5** of 4 830 (0.10 %) |
| content of those 5 in the frozen 4D | 3.00e-46 … 2.09e-44 — **0.0000 %** of the 4D total |
| **excluding those 5**, median relative difference | **4.43 %** |
| p90 / p99 / max | **20.8 % / 33.9 % / 72.8 %** |
| **bins exceeding the 3 % tolerance** | **3 009 of 4 825 (62 %)** |
| bins exceeding 10 % | 1 295 |
| **integral agreement** `sum(M@x5) / sum(x4)` | **1.005578** (0.56 %) |
| 5D contributors per 4D bin | min 0, median 2, max 6 |

**The `1.00e+00` in the error message is a red herring.** It comes from the 5 zero-support bins,
which are numerically irrelevant. The real result is the line under it: the marginal and the
independent 4D disagree at a **median of 4.4 % and a p90 of 21 %**, while their **integrals agree
to 0.56 %**. That is the signature of a genuine shape difference between two estimators, not a
units error or a plumbing bug — and it is nowhere near a 3 % per-bin gate.

## 3. Why this is a specification question, not a bug to fix

**The gate encodes the opposite of the convention adopted 2026-08-07.** That decision — pre-settled
and explicitly not to be reopened — is that **4D is the exact 5D→4D marginal, and the independent
4D unfold is a cross-check.** Under that convention the marginal is *definitional*: it is the
answer, and there is nothing for it to reproduce. This gate instead treats the independent 4D as
ground truth and the marginal as a candidate that must match it, which is the convention we did
not adopt.

The gate predates the decision. Nothing was wrong with writing it then; it simply was never
revisited, and because stages 4-6 never ran, nothing forced the contradiction into the open.

**Two readings, and I am not choosing between them:**

1. *The gate is mis-specified.* Under the adopted convention it should not exist in this form —
   at most it should RECORD the marginal-vs-independent difference as a cross-check statistic,
   with a bar set from what two OmniFold estimators at different dimensionality are actually
   expected to agree to, which is plainly not 3 % per bin.
2. *The disagreement is itself worth attention.* Median 4.4 % / p90 21 % between the deliverable
   and its cross-check is a real number about the analysis, whichever way the convention falls,
   and it has not been quoted anywhere before because this comparison had never run.

Both may be true. **Raising the tolerance is not on the table** — a 3 % gate that fails at a median
of 4.4 % is not repaired by widening it to 100 %, and "never raise a tolerance to clear a
mismatch" is a standing rule on this campaign.

## 4. A separate, smaller defect in the same stage

`p4_lib.build_projection_M` checks coverage in **one direction only**: every reported 5D bin must
map to a reported 4D bin (`"high reported bin {g} maps to non-reported low bin {glow}"`). It never
checks the converse — that every reported 4D bin receives at least one 5D contributor. Hence the
5 orphan bins, which reach the central check as exact zeros and produce a `rel = 1.0` that
completely masks the 62 %-of-bins result behind it.

This is independent of the convention question and is a defect either way: a one-directional
coverage guard on a bijection-shaped requirement. The right form fails at `build_projection_M`
with the count and the identity of the orphan bins, rather than surfacing 4 830 bins later as a
single misleading `max rel`.

**Rule.** When a guard reports `max`, the maximum is chosen by the worst bin, and a handful of
degenerate bins will always win it. Report a distribution — median, p90, count-over-tolerance —
beside any max, or the max becomes a mask for the finding. Here the max said "one bin is 100 %
off" when the truth was "62 % of bins are over tolerance".

## 5. Status of the products

`active_universe_5d/standard/candidate/` on scratch holds:

| file | |
|---|---|
| `std_final5_candidate.root` | 42.3 GB, 45 bands, sqrt_tr_syst 4.3513e-38, sqrt_tr_full 4.3576e-38 |
| `std_component_manifest.json` | carries `publication_gate_rejects_this: true` |
| `p4_standard_validation.json` | `RESULT PASS`, gate `candidate_self_declares_non_adoptable` present |
| `std_proj4d_candidate.root` | **not produced — stage 6 aborted** |

The candidate is **not adoptable and not quotable**. It was built without a `standard-p4-verifier`
PASS, by explicit instruction, and `p4_adopt_standard.py` refuses it outright. Producing it did
not shorten the path to adoption; it answered a question about stages 4-6, and the answer is that
two of the three are clean and the third cannot pass as specified.

# s5p (`OI-193`): the joint-5D inference result (amendment 7), recorded 2026-10-05

**CITABLE FOR:**
- the ten primary decisions of the frozen joint-5D inference (amendment 7, frozen at `4f5a613f`), each with its final
  B, stop reason, claim p, Holm threshold and 95% interval;
- each decision's ruled robustness label (κ = 3 replace);
- each decision's missing-seed status as it stands now;
- the amendment-7 conditions stated with every claim;
- the independent recompute verdict that permits recording.

**NOT CITABLE FOR:**
- **A measurement.** This is a set of statements about the simple hypotheses H0(G) that amendment 7 defines. It is not
  a measured cross section, and it does not validate, qualify or re-qualify any measurement or uncertainty.
- **Certification against the lost draws.** Every decision is currently "can change" under the labelled
  missing-seed sensitivity. Its report-only resolution is in progress (§5), and how it enters the claims is Joseph's
  decision.
- **The adequacy of the calibration model**, beyond the stated conditions.
- **Publication readiness.** It is NOT READY (CHECKLIST-20261001 §4).

**Authority for recording:** amendment 7 `validation_and_assurance` (v) and
`DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §1. The joint result is recorded only after the
extended, independently reviewed comparer returned AGREE (§4).

## 1. What was tested (amendment 7 `claims.family`, verbatim)

> for each of the five predictions G: H0(G) is the SIMPLE fine-grid hybrid null that the calibration actually
> simulates: the true cross section equals G on the fine 5D grid (fine-ratio null truth: the J integrals exactly G's)
> with MnvTune v1's shape and G's finite-MC fine-cell fluctuations below it; for MnvTune (the analysis MC, rho = 1)
> this is H0 exactly. Test domains: the 109 supported J cells; GiBUU the 72 of them with p_parallel < 6 GeV/c (pz index
> <= 1). Two tests each (total, shape-only): 10 tests

**Rejection rule** (verbatim, abridged only at the ellipsis): "H0(G) is rejected at familywise 0.05 only by
s5p_inference.holm_determined on the CLAIM p-values: the largest p over the process-shift variants (bias-aligned
upper-bound D, c in 0, 1/2, 1) AND the sub-fine-residual variants F +- 2 delta_M1 (kappa = 2; …). … A step rejects only
when the 95% Clopper-Pearson interval of k/B lies entirely below its Holm threshold".

## 2. The ten primary decisions

Source: `joint-evaluate.json`, sha256 `b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11`; copy in
`state/s5p/stage7/joint/`. Evaluated from the clean deploy `e9372b75`; frozen modules identical to `4f5a613f`.

| test | final B | stop reason | k | claim p | Holm threshold | 95% CP interval | decision | robustness (κ = 3 replace) |
|---|---:|---|---:|---:|---:|---|---|---|
| NuWro total | 1751 | rule met for both tests | 0 | 1/1752 | 0.005 | [0, 0.00210] | **rejected** | robust to the sub-fine residual |
| GENIE CV total | 1366 | rule met for both tests | 0 | 1/1367 | 0.00556 | [0, 0.00270] | **rejected** | robust |
| GENIE CV shape | 1366 | rule met for both tests | 0 | 1/1367 | 0.00625 | [0, 0.00270] | **rejected** | robust |
| MnvTune total | 1365 | rule met for both tests | 0 | 1/1366 | 0.00714 | [0, 0.00270] | **rejected** | robust |
| MnvTune shape | 1365 | rule met for both tests | 0 | 1/1366 | 0.00833 | [0, 0.00270] | **rejected** | robust |
| GiBUU total | 1351 | rule met for both tests | 0 | 1/1352 | 0.01 | [0, 0.00273] | **rejected** | robust |
| GiBUU shape | 1351 | rule met for both tests | 0 | 1/1352 | 0.0125 | [0, 0.00273] | **rejected** | robust |
| GENIE MEC total | 1343 | rule met for both tests | 0 | 1/1344 | 0.0167 | [0, 0.00274] | **rejected** | robust |
| GENIE MEC shape | 1343 | rule met for both tests | 0 | 1/1344 | 0.025 | [0, 0.00274] | **rejected** | robust |
| NuWro shape | 1751 | rule met for both tests | 1 | 2/1752 | 0.05 | [0.0000145, 0.00318] | **rejected** | robust (κ = 3: k = 2, p = 3/1752) |

- **p-values:** Monte Carlo, (k + 1)/(B + 1). None is zero; each is bounded below by 1/(B + 1).
- **Labels:** `robust-labels.json`, sha256 `206655f906bdffac636676f39ed86267f31eb9600ed9d45a335905fdaf7fde2a`, schema 2,
  per `RULING-20260929-s5p-A7-robustness-flag.md`.
- **Observed-p stability** over the 20 real-data rounding jitters (`validation_and_assurance` (iv)): every p is
  identical across them, except NuWro shape, which ranges over 2/1752–3/1752.

## 3. Conditions stated with every claim (amendment 7 `claims.conditions_stated_with_every_claim`, verbatim)

Each decision above holds under all six:

1. "below the fine grid the null truth carries MnvTune's shapes and G's finite-MC fine-cell fluctuations: the M1
   check is not converged (fine vs merged-x2 is 0.50-0.86 of coarse vs fine in L2); its effect enters the claim rule
   as the kappa = 2 variants and its size in null-T units (with the frozen V) is committed before the first look"
2. "the MC detector simulation per event beyond the drawn detector bands (MinosEfficiency, GEANT neutron/pion/proton,
   each +-1 sigma) and the linear lateral surrogate (five bands); there is no recoil-energy-scale band in the
   analysis's systematic set (app_statmethods.tex), so hadronic-response completeness is not established"
3. "the interaction-model prior is the analysis's vertical band set (34 bands, every band drawn per experiment);
   negative weights of LowQ2_1/HighQ2_1 are clipped per universe (EXCEPTION-20260927-s5p-pilot-negative-rate-
   resubmission.md: <= 0.35% of a band's shift in whitened norm)"
4. "the pseudo-experiment process unfolds with half the MC, the data with all of it; the MC-size shift D (16 pairs)
   is at noise level per cell (median |D|/f 0.02-0.075%); along the null's bias direction it is not always consistent
   with zero (proxy a/se +4.7 MnvTune, -3.4 NuWro) but at most ~0.05 null SD; it enters as the bias-aligned
   upper-bound variant"
5. "GiBUU: E_nu > 20 GeV absent (KNOWN_ISSUES 82) and its out-of-domain truth (p_parallel >= 6 GeV/c, E_nu-truncated)
   enters the migrations into the domain cells; all generators: E_nu > 100 GeV absent (only the data's flux integral
   stops there; negligible)"
6. "the predictions' own finite MC enters as diag Var(mu_G) in the metric and as a drawn residual term"

## 4. Independent recomputation (amendment 7 `validation_and_assurance` (v))

- **Reviewed final verdict: AGREE.** 1379 of 1379 rows agree, with 0 discrepancies, 0 required items not located and 0
  unresolved leaves.
  - **Run:** from the reviewed comparer extension (commit `02df81e6`; recompute `81b879ae…`, comparer `bc924f31…`,
    design `404446eb…`), on the unchanged production outputs (`b9604502…`, `206655f9…`).
  - **Outputs:** `recompute.json` `550a95fc…` and `compare.json` `97e1666a…`. They are on branch
    `s5p-parallel-recompute-20260928` (tip `466b427b`), in `state/s5p/recompute/final-ext/`. The campaign re-read
    `compare.json` there: verdict `AGREE`, sha256 prefix `97e1666a7e5722b0`.
  - **Record:** `REPORT-20261005-s5p-recompute-final-verification.md` §8.
- **Review of the extension:** `REVIEW-20261005-s5p-recompute-comparer-extension.md`, APPROVE at `02df81e6`, with
  nothing at MEDIUM or above (4 LOW, 3 NOTE).
  - Caveat, as disclosed by that review: its full test suite did not finish under machine load, so it has no runner
    summary line. The extension's author ran the same code's full suite before the commit: 84 tests (73 + 11) passed
    (REPORT-20261005 §8).
  - Two LOWs are owed, each with its own review; neither affects the verdict.
- **Owner rulings applied:** A16, a report-only clarification of two descriptive fields, and allowed new output fields
  (DECISION-20261005 §4).
- **Before the extension:** the first reviewed comparer, at `0142a228`, had already found 712 of 712 rows agreeing
  with 0 discrepancies. Its verdict was INCOMPLETE on layout mapping.
- **Scope:** the verification establishes the calculation from the products. It does not establish the calibration's
  adequacy, and it does not certify the missing-seed sensitivity.

## 5. Missing-seed status (labelled sensitivity; report only)

- **The lost draws:** 224 calibration (111 interrupted, 113 never started) and 53 power. All were lost to scheduler
  time-limit kills.
- **Sensitivity** (`missing-sensitivity.json` `f48e16ef…`; COMPLETE): every decision reads "can change (counterexample:
  worst_interrupted, worst_all_missing)".
  - If every interrupted draw exceeded the observed statistic, no test would be rejected (p 0.013–0.019).
  - The sufficient all-assignment certificate certifies no rejection.
  - The recompute lane's independent bounds agree on every mapped quantity.
- **Supporting, not certifying, evidence:** among completed draws, runtime is not associated with the statistic
  (|ρ| ≤ 0.06).
- **Resolution in progress:** under Joseph's decision (DECISION-20261005 §2), a report-only recovery of exactly the
  lost seeds is under way. It follows the independently reviewed `PROCEDURE-20261005-s5p-lost-seed-recovery.md`:
  - Phase 0 passed;
  - the Phase A determinism array `59397841` was submitted 2026-10-05T23:37Z.
- **What the resolution will and will not do:** its outcome will be added to this record as a report-only resolution,
  with the recompute lane's cross-check. It will not change any primary decision above.
- **Update 2026-10-06:** the resolution is complete and independently cross-checked
  (`RECORD-20261006-s5p-lost-seed-recovery-resolution.md`). No recovered draw reaches the observed statistic, and every
  decision is unchanged under all three readings. How this enters the claims awaits Joseph's disposition.

## 6. Power per null

- **Not a claim condition here.** Amendment 7 attaches power to NON-rejections, and only at the MnvTune and GENIE CV
  nulls; every decision here is a rejection.
- **Context only** (claim rule with determinacy; `joint-evaluate.json` `power`):
  - at the MnvTune null, P1 and P2 have power 1.000 for both tests at 0.05 and at 0.005, and P3 has shape power 0.231
    at 0.005;
  - at the GENIE CV null, P1g has shape power 0.739 at 0.005, P2g's is low, and P3g's is ≈ 0.
- **Incomplete sets:** every power set is incomplete (time-limit losses). Amendment 7 records that and never aborts.
- **The T6 target** (shape power ≥ 0.80 at 0.005 at the MnvTune null, a = 1) is met by P1 and P2, not by P3.
- **Details:** `RECORD-20261005-s5p-terminal-evaluation-pending-verification.md` §3.

## 7. Unchanged by this record

- The measurement branch is NOT ADMITTED (amendment 4).
- There is no new reportable uncertainty.
- Publication readiness is NOT READY.
- The A6 (R6) and A8 (R8) rulings remain the owner's.

# CAMPAIGN s5e-20260925 — `OI-192` diagnosis and bounded estimator development

**CITABLE FOR:** where this campaign's authority, contract, budget, receipts and state live.
**NOT CITABLE FOR:** any number, cause, grade, adoption or readiness; those live in the receipts,
`VALIDATION_LEDGER.md` and the records named there. Machine state:
[`state/s5e/campaign-state.json`](state/s5e/campaign-state.json), authoritative for phase, job IDs and the
next deterministic action. This page is its reading guide. Tracker: `OI-192`.

| | |
|---|---|
| authority | [`AUTHORIZATION-20260925-oi192-estimator-diagnosis.md`](AUTHORIZATION-20260925-oi192-estimator-diagnosis.md) |
| attachment | [`GOAL-20260925-oi192-estimator-diagnosis.txt`](GOAL-20260925-oi192-estimator-diagnosis.txt) (blob `23ed4e12…`) |
| prior approved plan | [`PLAN-scalar5d-reportable-uncertainties-and-inference.md`](PLAN-scalar5d-reportable-uncertainties-and-inference.md), blob `8b0617b6…`, **never edited** |
| predecessor | [`CAMPAIGN-s5n-20260925-index.md`](CAMPAIGN-s5n-20260925-index.md) (`OI-191`, CLOSED `STAGE1_FAIL`; not reopened, not re-graded) |
| contract | [`state/s5e/contract.json`](state/s5e/contract.json) (frozen at the commit that adds it); amendments are new files beside it |
| lane / committer | `scalar5d campaign` (OI block `190-199`) |
| owning worktree | `MINERvA-OmniFold-oi192`, branch `campaign/oi192-diagnosis-20260925` |
| cluster namespace | `/pscratch/sd/j/josephrb/s5e-20260925/` — fresh outputs only; s5c, s5n and historical products are read, never written |
| admission and accounting | [`nd-unfolding/s5c_meter.py`](../../nd-unfolding/s5c_meter.py) bound to [`state/s5e/budget.json`](state/s5e/budget.json) and the ledger `…/s5e-20260925/ledger/admissions.jsonl`; job names carry the `s5e-` prefix |

## Envelope (budget revision 1, measured 2026-09-25T22:30Z)

| pool | campaign cap | binding | diagnosis | verification/repair (≥ 20%) | unallocated |
|---|---:|---|---:|---:|---:|
| CPU (`m3246`) | **60.0** billed CPU node-h | the explicit cap (unspent prior envelope 320.583; 10% of uncommitted 342.816) | 10.0 | 12.0 | 38.0 |
| GPU | **0** | no GPU allocation | — | — | — |

Prior charges carried forward: s5c 20.086 + s5n 4.601 = 24.687 CPU node-h of the 345.27 envelope.

## Stages (contract)

1. **D — diagnosis** (≤ 10 CPU node-h): D0 reproduction of the s5n evidence by instrumented runs; D1
   matched driver and npz paths on noise-free departures; D2 pipeline reconciliation (seeds, precision,
   masks, weights, normalization, refinement); D3 per-iteration trace (forward fold, step-1/step-2
   response, missed-event regression); D4 noise-free iteration scan; D5 one-factor capacity and
   missed-event probes; D6 observability after detector response; D7 the nominal background-related bias.
   A cause is named only under the contract's attribution rule.
2. **Candidate decision** — zero, one or two candidates, each supported by a predeclared rule, frozen
   and costed by amendment; or a recorded stop.
3. **C — development** (one revision per candidate) and **A — assessment** on fresh seeds and the
   withheld physical deformations W1–W3, with acceptance and useful-width criteria frozen first.
4. **Independent review, deliverables, closeout** with the four status fields.

## Closeout (2026-09-26) — final disposition

Evidence:

- [`DIAGNOSIS-20260926-s5e-oi192-estimator.md`](DIAGNOSIS-20260926-s5e-oi192-estimator.md) (`VL153`;
  review round 1 in [`state/s5e/diag/review-round-1.md`](state/s5e/diag/review-round-1.md));
- [`OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md`](OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md)
  (`VL154`; review round 2 in [`state/s5e/cand/review-round-2.md`](state/s5e/cand/review-round-2.md));
- receipts under [`state/s5e/diag/`](state/s5e/diag/) and [`state/s5e/cand/`](state/s5e/cand/), and the
  costed design `state/s5e/cand/next_design.json`.

| field | value |
|---|---|
| `campaign_disposition` | **CLOSED — bounded objective met.** Diagnosis complete and independently reviewed. One candidate (`R`, refinement 400 trees / 31 leaves) passed development and was assessed on fresh seeds and withheld physical deformations: **`A_FAIL`** on A3 (real-data numerical reproducibility floor, `KNOWN_ISSUES.md` 80). A1, A2 (pooled; 6 functionals miscalibrated, EW41 among them) and A5 pass; the A4 scope is 20 of 42 EW cells. The A3 failure belongs to the estimator family (B0 the same) and was foreseeable. 1 of 2 candidates used; no revision (A_FAIL is terminal). |
| `reportable_uncertainty_scope` | **Unchanged.** The 2D standalone covariance (validated) and the `(E_avail,W)` `C_EW` `835828bf…` published under exception with M1–M4 travelling. Neither the background bias (75) nor the departure (regularization) bias (77) is in any covariance; whether any interval absorbs the numerical floor (80) is not established. No 5D coverage claim; nothing adopted. |
| `joint_5d_inference_status` | **NOT PERFORMED** (excluded by the authorization; no qualified covariance). |
| `publication_readiness` | **NOT READY.** The larger publication objective is not met. |

**Spend:** 10.399 of 60 CPU node-h, all admissions closed: diagnosis 3.932, development 2.224, assessment
4.243; verification ran read-only on login nodes. GPU 0. The carried-forward envelope stands at 35.086 of
345.27 CPU node-h.

**Next:** `OI-193`, the costed increments (outcome §6) reserved to Joseph.

**Deliverables and heads (verified by `git ls-remote`, 2026-09-26).** Note, primer and paper state the findings (`5683e329`); `build_all.sh` passes in both repositories. Standalone `MINERvA-OmniFold-Analysis-Note` `main` = **`b1410fc3`**. Canonical `origin/main` is the commit that adds this line (see the state file's `remote_heads`). Release package unchanged: nothing qualified. Review worktrees `MINERvA-OmniFold-s5e-review1` and `-review2` were left clean.

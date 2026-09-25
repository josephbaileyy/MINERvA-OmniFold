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

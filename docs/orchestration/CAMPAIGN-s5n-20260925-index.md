# CAMPAIGN s5n-20260925 — scalar-5D `negweight-refined` successor (`OI-191`)

**CITABLE FOR:** where this successor's authority, contract, budget, receipts and state live.
**NOT CITABLE FOR:** any number, grade, adoption or readiness; those live in the receipts,
`VALIDATION_LEDGER.md` and the decision records named there. Machine state:
[`state/s5n/campaign-state.json`](state/s5n/campaign-state.json), authoritative for phase, job IDs
and the next deterministic action. This page is its reading guide. Tracker: `OI-191`.

| | |
|---|---|
| authority | [`AUTHORIZATION-20260925-negweight-refined-successor.md`](AUTHORIZATION-20260925-negweight-refined-successor.md) (commit `75bd22c0`) |
| attachments | [`HANDOFF-20260925-negweight-refined-successor.md`](HANDOFF-20260925-negweight-refined-successor.md) (blob `6eb22414…`), [`GOAL-20260925-negweight-refined-successor.txt`](GOAL-20260925-negweight-refined-successor.txt) (blob `2748dc36…`) |
| prior approved plan | [`PLAN-scalar5d-reportable-uncertainties-and-inference.md`](PLAN-scalar5d-reportable-uncertainties-and-inference.md), blob `8b0617b6…`. It is **never edited**; its gates are retained (authorization §3) |
| predecessor | [`CAMPAIGN-s5c-20260924-index.md`](CAMPAIGN-s5c-20260924-index.md) (`OI-190`, CLOSED; not reopened, not re-graded) |
| contract | [`state/s5n/contract.json`](state/s5n/contract.json) (frozen `75bd22c0`); amendments are new files beside it |
| lane / committer | `scalar5d campaign` (OI block `190-199`) |
| owning worktree | `MINERvA-OmniFold-s5n`, branch `campaign/s5n-negweight-refined-20260925` |
| cluster namespace | `/pscratch/sd/j/josephrb/s5n-20260925/` — fresh outputs only; s5c and historical products are read, never written |
| admission and accounting | [`nd-unfolding/s5c_meter.py`](../../nd-unfolding/s5c_meter.py) bound to [`state/s5n/budget.json`](state/s5n/budget.json) and the ledger `…/s5n-20260925/ledger/admissions.jsonl`; job names carry the `s5n-` prefix |

## Envelope (budget revision 1, measured 2026-09-25T19:01Z)

Carried forward from s5c, not reset: the caps are the **unspent portions** of the s5c envelopes
after its reconciled charge (20.086 CPU node-h; 9.786 GPU node-h = 39.14 A100-h), each also held to
≤ 10% of the uncommitted allocation measured after reservations. These are remaining balances, not
new grants (authorization §4).

| pool | successor cap | binding | Stage-1 development (≤ 10%) | verification/repair (≥ 20%) |
|---|---:|---|---:|---:|
| CPU (`m3246`) | **325.184** billed CPU node-h | unspent (10% of uncommitted = 343.26) | 32.518 | 65.037 |
| GPU (`m3246_g`) | **115.214** GPU node-h = **460.86 A100-h** | unspent | 11.521 (46.09 A100-h) | 23.043 |
| pscratch | **370.6 GiB** | 10% of 3.62 TiB free | — | — |

Everything else is unallocated until the pre-expansion feasibility receipt (a budget revision
plus a ledger `rebind`).

## Stages (contract §§ `stage_1_development`, `stage_2_preconditions`)

1. **Stage 1 — development.** Controls C0–C8: baseline reproduction; evidence that the refinement
   runs in every path; refinement equivalence and reproducibility; background-inclusive known-truth
   closure at nominal, under a meaningful E_avail shape departure and under the repaired q3
   departure; σ calibration of the repaired bootstrap; a real-data method-sensitivity comparison;
   a signal-only reference. At most 10% of each pool.
2. **Independent review and feasibility.** The construction is reviewed from its operands. The
   COMPLETE remaining work is costed, and sample size and assurance are recomputed at the
   development coverage estimates. The Stage-2 construction is frozen by amendment before any
   validation seed runs.
3. **Stage 2 — only if the controls pass and the work is affordable.** Tier S, the matched
   systematic construction, seed stability, and Tier T, each only as its claimed scope requires.
   Delegated adoption only under plan §9.

## Inherited dependencies

Retained from the s5c index unchanged: D4 (protected baseline namespace), D6 (shared cluster checkout
not moved), D7 (outward acts), D8 (no `git pull` in the shared main checkout), D9–D11 as recorded
there. D3 is closed (HPSS backup); nothing in this successor rebuilds from the nine sole-copy objects.

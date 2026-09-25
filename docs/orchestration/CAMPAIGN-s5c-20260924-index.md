# CAMPAIGN s5c-20260924 — scalar-5D reportable uncertainties and calibrated generator inference

**CITABLE FOR:** where this campaign's authority, contract, budget, receipts and state live; which
inherited dependency blocks which exact action. **NOT CITABLE FOR:** any number, grade, adoption or
readiness — those live in the receipts, `VALIDATION_LEDGER.md` and the decision records it names.
Machine state: [`state/s5c/campaign-state.json`](state/s5c/campaign-state.json) (authoritative for
phase, job ids and the next deterministic action; this page is its reading guide). Tracker: `OI-190`.

| | |
|---|---|
| authority | [`AUTHORIZATION-20260924-scalar5d-campaign-activation.md`](AUTHORIZATION-20260924-scalar5d-campaign-activation.md) (commit `81c62d15`) |
| approved plan | [`PLAN-scalar5d-reportable-uncertainties-and-inference.md`](PLAN-scalar5d-reportable-uncertainties-and-inference.md), blob `8b0617b6…`, commit `bf34a12c…` — **never edited by this campaign** |
| lane / committer | `scalar5d campaign` (OI block `190-199`) |
| owning worktree | `MINERvA-OmniFold-campaign-scalar5d`, branch `campaign/scalar5d-20260924` |
| cluster namespace | `/pscratch/sd/j/josephrb/s5c-20260924/` — fresh outputs only; historical adopted bytes are read, never written |
| admission and accounting | [`nd-unfolding/s5c_meter.py`](../../nd-unfolding/s5c_meter.py) (every campaign job is submitted through it; job names carry the `s5c-` prefix); budget [`state/s5c/budget.json`](state/s5c/budget.json), evidence [`state/s5c/allocation-measurement-20260925.txt`](state/s5c/allocation-measurement-20260925.txt) |

## Envelope (budget revision 1, measured 2026-09-25T06:07Z)

| pool | campaign cap | binding rule | 20% verification/repair | pilots (≤5%) | cleanup (≤10%) |
|---|---:|---|---:|---:|---:|
| CPU (`m3246`) | **345.27** billed CPU node-h | 10% of 3,452.7 uncommitted | 69.05 | 17.26 | 34.53 |
| GPU (`m3246_g`) | **500** A100-h (125 GPU node-h) | absolute ceiling | 100 A100-h | 25 A100-h | 50 A100-h |
| pscratch | **371.7 GiB** | 10% of 3.63 TiB free | — | — | — |
| HPSS (D3 only) | 64 GiB | D3 | — | — | — |

Measurement and inference stage allocations are set by the feasibility receipt (a budget revision
plus a ledger `rebind`), never by spending first.

## Inherited dependencies, tracked by the exact action each blocks

From [`HANDOFF-20260924-preparation-for-scalar5d-campaign.md`](HANDOFF-20260924-preparation-for-scalar5d-campaign.md) §6.

| # | state | blocks exactly | closure |
|---|---|---|---|
| D1 | **CLOSED** by the activation record | — | `81c62d15` |
| D2 | **CLOSED for this campaign** by mapping rows S1–S2 and the campaign meter | any campaign submission before the meter and budget are committed | this index's commit |
| D3 | **CLOSED** 2026-09-25 — [`RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md`](RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md) (tape residency 9/9; restore SHA-256 9/9; tape-read not proven) | a rebuild from, or recomputation over, any of the nine sole-copy objects (`active`, `throw`, `stat`, `ml`, `z-mean.npz`, the graded pair and their `z-mean.npz`); in particular any new assembly that reads `active` | the committed HPSS recovery receipt with all nine restored and SHA-256-equal |
| D4 | **RETAINED** (not displaced) | baseline `run_p4_unfold_std.sh` re-production in the protected namespace | none sought; lateral propagation uses fresh endpoints in the campaign namespace |
| D5 | **DISPLACED** by S7 | — | a fresh paired rebuild at one revision, if the contract needs one |
| D6 | **OPEN, avoided** | moving or redeploying the shared cluster checkout `32e403b8` | not needed: the campaign deploys its own tree |
| D7 | **RETAINED** | shipping Appendix F, sending the hadronic-response question, adopting the 3D projection | outward/adoption acts outside this delegation |
| D8 | **OPEN, not ours** | `git pull` in the shared main checkout | not needed: the campaign works in its own worktree |
| D9 | **OPEN** | trusting a bare red from `probe-20260922-seven-gates.sh` | use `probe-20260922-render-checks.py --since 8cffde7b` |
| D10 | **OPEN** | archiving the two 0921/0922 handoffs | unchanged by this campaign |
| D11 | **OPEN** | describing any cause-3 criterion as never computed in production | the successor contract defines its own gates and does not quote the census |

## Phases (plan §§4–10) — current state lives in the state file

A (preparation) → B (contract, feasibility receipt) → C (reportable scope) → D (calibration and
coverage; measurement checkpoint) → E (frozen comparisons) → F (verification, delivery, release
preparation). Each committed receipt is listed in the state file's `receipts` array with its digest.

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

## Paper-wide completion table

[`CAMPAIGN-s5c-20260924-paper-wide-table.md`](CAMPAIGN-s5c-20260924-paper-wide-table.md) — initialized in Phase A, reconciled before closeout.

## Phases (plan §§4–10) — current state lives in the state file

A (preparation) → B (contract, feasibility receipt) → C (reportable scope) → D (calibration and
coverage; measurement checkpoint) → E (frozen comparisons) → F (verification, delivery, release
preparation). Each committed receipt is listed in the state file's `receipts` array with its digest.

## Closeout (2026-09-25) — final disposition

Evidence: [`OUTCOME-20260925-s5c-tier-s-futility-fail.md`](OUTCOME-20260925-s5c-tier-s-futility-fail.md) (`VL150`,
independently reproduced), [`OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md`](OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md)
(`VL149`, `KNOWN_ISSUES.md` 75), [`state/s5c/review-3-disposition.json`](state/s5c/review-3-disposition.json),
[`FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md`](FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md).

| field | value |
|---|---|
| `campaign_disposition` | **CONCLUDED — objective NOT MET.** Measurement: the existing estimator F1 fails the 5% seed gate on every coarse partition (`VL146`). Candidate F2 FAILED Tier-S coverage (futility) after both permitted development revisions (`VL150`). F3 is infeasible, and it cannot remove the estimator-independent causes (see below). Inference: not performed. |
| `reportable_uncertainty_scope` | **Unchanged in kind; one new caveat travels.** The 2D standalone covariance (validated). The `(E_avail,W)` 42-cell `C_EW` `835828bf…`, published under exception with M1–M4 travelling, **and now with the purity-background closure bias** (0.36–1.07 of its quoted σ in the highest-W column, not in the covariance; `KNOWN_ISSUES.md` 75). **No frequentist coverage is claimed for any 5D interval.** No new measurement checkpoint qualified. No reportable 3D, 4D or 1D-projection uncertainty. |
| `joint_5d_inference_status` | **NOT PERFORMED.** Infeasible within the envelope: the precision rule needs ≥ 38,720 null experiments per comparison (≈ 440 CPU node-h for one generator, ≈ 2,600 for four). The 5D generator predictions do not exist. There is no qualified measurement covariance to calibrate against. |
| `publication_readiness` | **NOT READY.** |

**Failed or missing requirements.**
1. Tier-S statistical coverage (plan §7). FAILED for F2's bias-corrected intervals at the nominal and E_avail-tilt truths. The uncorrected reported intervals were not validated.
2. A measurement uncertainty checkpoint (plan §§7, 9): none qualifies.
3. Background-inclusive closure: the purity method is biased up to 4% at nominal truth in the highest-W cells.
4. A statistical σ that includes background-sampling variance (the Tier-S bootstrap does not redraw background).
5. Transfer of a nominal-truth correction under truth departures: fails at the tilt point.
6. The F2 systematic construction: held and not assembled; boot 100/100, sweep lines 0-39 and detector lines 0-4 exist, unadopted.
7. G-stab-F2: not run (its probes were held with construction).
8. Tier T: unresolved dependency (feasibility §4).
9. Joint-5D and projection inference: not performed (above).
10. Release package, per-object provenance, and generator-prediction digests: still OPEN (paper-wide table R20).
11. The outward-facing acts held by D7 remain Joseph's.

**Three causes, each sufficient to fail Tier S, none of them estimator-seed behaviour:**
1. the purity background method's closure bias (estimator-independent, D1);
2. σ omitting background sampling;
3. non-transfer of a nominal correction.

This is why no third family was started (plan §6: advance only for a requirement a later family can meet).

**Costed next increments** (native billed units, from committed measurements; remaining envelope: 325.2 CPU node-h, 115.2 GPU node-h):

| # | increment | what it buys | forecast |
|---|---|---|---|
| 1 | 5D purity-versus-`negweight-refined` comparison on data (`OI-191`, part 1) | the real-data size of the background-method bias | ≈ one construction: ≈ 12 CPU + 13 GPU node-h |
| 2 | a background-method family: `negweight-refined` background in the unfold, a Tier-S σ that redraws background, fresh validation seeds, the same frozen gate (`OI-191`, part 2) | a chance at a qualified measurement checkpoint | development ≈ 20 + construction ≈ 25 + Tier S ≈ 127 → **≈ 170–200 CPU node-h**, inside the remaining envelope |
| 3 | a q3-deformation study with the repaired truth (`KNOWN_ISSUES.md` 76), at a = 0.1 and 0.3 | whether the estimator can follow within-cell q3 changes (the lead in the Tier-S outcome §3) | ≈ 40 pseudo-experiments ≈ 5 CPU node-h |
| 4 | Tier T after 2 | total-interval coverage at two nuisance settings | ≈ 67 CPU + 81 GPU node-h (feasibility §5) |
| 5 | joint-5D inference, one generator | a calibrated p at the plan's precision | ≈ 440 CPU node-h plus the 5D prediction construction: exceeds the remaining envelope with 2 |
| 6 | four generator comparisons | the paper's generator set | ≈ 2,600 CPU node-h: a separately authorized campaign |

**Spend:** 20.09 CPU + 9.79 GPU node-h (39.2 A100-h), measured at 17:49Z (`state/s5c/tier_s/meter-measure-20260925T1749Z.json`). No campaign job remains. **Deliverables:** note, primer and paper corrected and built; standalone `MINERvA-OmniFold-Analysis-Note` at **`7739089b`**, pushed and verified.

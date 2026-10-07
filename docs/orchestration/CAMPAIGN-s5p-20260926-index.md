# CAMPAIGN s5p-20260926 — scalar precision measurement completion (`OI-193`)

**CITABLE FOR:** where this campaign's authority, contract, budget, receipts and state live.
**NOT CITABLE FOR:** any number, criterion, grade, adoption or readiness; those live in the receipts,
`VALIDATION_LEDGER.md` and the records named there. Machine state:
[`state/s5p/campaign-state.json`](state/s5p/campaign-state.json), authoritative for phase, job IDs and the
next deterministic action. This page is its reading guide. Tracker: `OI-193`.

| | |
|---|---|
| authority | [`AUTHORIZATION-20260926-precision-measurement-completion.md`](AUTHORIZATION-20260926-precision-measurement-completion.md) |
| attachments | [`HANDOFF-20260926-precision-measurement-completion.md`](HANDOFF-20260926-precision-measurement-completion.md) (blob `49c8e767…`, **never edited**); [`GOAL-20260926-precision-measurement-completion.txt`](GOAL-20260926-precision-measurement-completion.txt) (blob `f3a2da95…`) |
| prior approved plan | [`PLAN-scalar5d-reportable-uncertainties-and-inference.md`](PLAN-scalar5d-reportable-uncertainties-and-inference.md), blob `8b0617b6…`, **never edited** |
| predecessor | [`CAMPAIGN-s5e-20260925-index.md`](CAMPAIGN-s5e-20260925-index.md) (`OI-192`, CLOSED; candidate `R` A_FAIL on A3; not reopened, not re-graded) |
| contract | [`state/s5p/contract.json`](state/s5p/contract.json) (the framework, frozen at the commit that adds it); each stage's choices are frozen by numbered amendments beside it |
| lane / committer | `scalar5d campaign` (OI block `190-199`) |
| owning worktree | `MINERvA-OmniFold-s5p`, branch `campaign/s5p-precision-20260926` |
| cluster namespace | `/pscratch/sd/j/josephrb/s5p-20260926/` — fresh outputs only; s5c, s5n, s5e and historical products are read, never written |
| admission and accounting | [`nd-unfolding/s5c_meter.py`](../../nd-unfolding/s5c_meter.py) bound to [`state/s5p/budget.json`](state/s5p/budget.json) and the ledger `…/s5p-20260926/ledger/admissions.jsonl`; job names carry the `s5p-` prefix |

## Envelope (budget revision 1, measured 2026-09-26T16:04Z)

| pool | campaign cap | binding | stages 1–2 (≤ 15%) | verification/repair (≥ 20%) | unallocated |
|---|---:|---|---:|---:|---:|
| CPU (`m3246`) | **310.184** billed CPU node-h | the unspent cumulative envelope (345.27 − 35.086); 10% of uncommitted is 341.630 | 46.527 | 62.037 | 201.620 |
| GPU (`m3246_g`) | **114.904** GPU node-h (459.62 A100-h) | the unspent cumulative envelope (500 − 40.38 A100-h); 10% of uncommitted is 5,824 GPU node-h | 17.235 | 22.981 | 74.688 |

Prior charges carried forward: CPU s5c 20.086 + s5n 4.601 + s5e 10.399 = 35.086; GPU s5c 9.786 + s5n 0.309
+ s5e 0 = 10.095 GPU node-h (40.38 A100-h).

## Stages (handoff; contract `stages`)

1. **Use case** — physics use, precision targets, ≤ 3 reporting definitions, joint nulls, nuisances and
   power alternatives; amendment 1.
2. **Construction questions** — `R` first; numerical/bootstrap overlap; the six calibration failures;
   convergence and observability to 200 iterations; ≤ 3 configurations, ≤ 2 development revisions each;
   a provisionally affordable validation method and a complete forecast (≤ 15% of each pool for 1–2).
3. **Model dependence and production admission** — domain, withheld truths, frozen uncertainty and
   joint-test designs; an independently reviewed admission record.
4. **Construction** of matched central and uncertainty products.
5. **Validation** on fresh background-inclusive experiments and withheld truths.
6. **Delegated conditional adoption** of qualified scope only.
7. **Joint inference**, release materials, reproduction, deliverables and verified remote heads.

## Progress

See the state file.

- Stage 1 frozen: amendment 1 (use case, targets T1–T7, RD1/RD2/RD3), receipt `state/s5p/stage1/stage1_inspect.json`.
- Stage 2: amendments 2–3 (studies N, C, K, P, I); exit [`RECORD-20260927-s5p-stage2-exit.md`](RECORD-20260927-s5p-stage2-exit.md) and amendment 4: `R` selected; measurement branch not admitted (T1/T2 unattainable); joint-test branch to Stage 3.
- Stages 3–6: amendments 5–8 (joint-test design, repairs, production admission) and production under budget
  revisions 1–7. Production became terminal on 2026-10-05T20:32Z: five finals, all "rule met for both tests".
- Stage 6 verification: the independent recompute returned AGREE, 1379/1379, after a reviewed comparer extension
  (DECISION-20261005 §1, §4).
- Joint result recorded: [`RECORD-20261005-s5p-joint-5d-inference-result.md`](RECORD-20261005-s5p-joint-5d-inference-result.md),
  all ten H0(G) rejected.
- Lost-seed recovery, report-only, cross-checked 856/856:
  [`RECORD-20261006-s5p-lost-seed-recovery-resolution.md`](RECORD-20261006-s5p-lost-seed-recovery-resolution.md).
  Joseph's disposition is in DECISION-20261005 §5.
- **Closeout 2026-10-06: TERMINAL.** The four final fields, paper-wide readiness, spend, heads and costed remaining
  requirements are in [`DELIVERY-20261006-s5p-campaign-terminal.md`](DELIVERY-20261006-s5p-campaign-terminal.md).
  - campaign: TERMINAL;
  - measurement branch: NOT ADMITTED;
  - reportable uncertainty: none new;
  - joint-5D inference: executed, with all ten rejected;
  - publication: NOT READY.

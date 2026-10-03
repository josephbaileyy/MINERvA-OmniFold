# s5p (`OI-193`): terminal checks, evaluation sequence and claim rules (prepared 2026-10-01)

**CITABLE FOR:** the concrete checks that establish production is terminal (after transition r2); the evaluation
sequence and its verifications; the labelled missing-seed sensitivity and how it is reported; the wording rules for
the four final fields, which keep the measurement branch's non-admission distinct from the joint-test result.
**NOT CITABLE FOR:** any result or decision. It changes no frozen claim, statistic, stopping rule or terminal status.
The sensitivity is **report-only**: the primary decisions stand.

**Requested** by Joseph, relayed on 2026-10-01 by the peer session Codex: "resolve these issues by directly
communicating with these sessions until you are satisfied that there are no problems". The request is bounded to
three concerns and at most two review/repair cycles.

## 1. Production is terminal only when ALL hold (re-measured, never taken from a record)

1. Five `$NS/runs/prod/status/<null>-final.json` files exist. Read each one's `reason` (`rule met for both tests`,
   `maximum reached`, `batches exhausted`, `budget`).
2. Power is finished:
   - `runs/queue-prod-r2-pow.log` (**the r2 log**, not r1) contains `queue done`;
   - or the runner's own lines show a budget or incomplete outcome.
3. `squeue -h -u josephrb -o "%j"` exits **rc 0**, read into a file and with its own rc checked, and lists no
   `s5p-s5p_(cal|pow)_` job.
4. `s5c_meter.py measure`, run **from `$NS/deploy/c754f3cd`** (or a later deploy carrying budget revision 6), exits
   rc 0 with open concurrency **0** for both cpu and gpu. The old deploys' budget is refused (rc 5).
5. All six r2 runners have ended (`queue done`, or a recorded stop). No queue-runner process is left on login33.

## 2. Evaluation sequence (login node; no allocation)

`state/s5p/stage7/s5p_terminal_run.sh` implements §1 and §2, steps 1–4 and 6, with assertions and exit codes:
- `check` exits 0 only when §1 holds;
- `deploy <sha>` makes the new clean clone and verifies it;
- `verify <sha>` re-checks an existing deploy;
- `evaluate <sha>` re-runs `check` and `verify`, refuses to overwrite any output, then runs the four steps and
  prints the recompute packet.

Its exit codes are 0 done, 1 a check failed, 2 a probe failed, 4 sensitivity INCOMPLETE. It was tested read-only
on 2026-10-03: `check` correctly gave TERMINAL: NO; `verify c754f3cd` passed the frozen, design and V checks and
correctly failed on the missing sensitivity script.

1. **Deploy.** Make a NEW clean clone of current `origin/main` into `$NS/deploy/<sha>`. Verify:
   - HEAD and a clean tree;
   - `s5p_joint.py`, `s5p_inference.py` and `s5p_seqstop.py` byte-identical to `4f5a613f`;
   - `prod/design.json` sha256 `404446eb…`;
   - V sha256 `35979ef7…`.
2. **Evaluate.** Run `s5p_joint.py evaluate` per handoff §8. It refuses unless each null's product count equals its
   final B.
3. **Labels.** Run `s5p_robust_labels.py` (schema 2, A7-VS replace).
4. **Seed states, at terminal.** Run the task-log classification:
   `PYTHONPATH=nd-unfolding python3 docs/orchestration/state/s5p/diag/s5p_lost_seed_runtime_diagnostic.py --logs
   $NS/runs/prod/logs --v $NS/stage3/V/V-s3v.npz --out $NS/stage7/joint/seed-states.json`.
   Then **missing-seed sensitivity** (§3):
   `PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_missing_sensitivity.py --evaluate <joint-evaluate.json> --design
   docs/orchestration/state/s5p/prod/design.json --tables docs/orchestration/state/s5p/prod/tables --ledger
   $NS/ledger/admissions.jsonl --seed-states <seed-states.json> --out $NS/stage7/joint/missing-sensitivity.json`.
   It refuses unless every null's completed count equals the evaluator's B, and every power set's count its n.
5. **Commit copies.** Commit copies of the four outputs under `state/s5p/stage7/joint/`, with their sha256.
6. **Notify the recompute lane** (session `gbdt independent`). Send:
   - the terminal evidence for §1, items 1–5;
   - the deploy sha;
   - the paths and sha256 of `joint-evaluate.json`, `robust-labels.json`, `seed-states.json` and
     `missing-sensitivity.json`.

   It re-measures terminal state itself (its §5.1, already switched to the r2 log and deploy c754f3cd). Then it
   runs its reviewed deploy `0142a228` and its own report-side seed disposition. **The joint result is not recorded
   before its report** (amendment 7 `validation_and_assurance` (v)). A disagreement is resolved by the routes in its
   handoff, never by changing a reading to match.

## 3. Missing-seed sensitivity (report only): `nd-unfolding/s5p_missing_sensitivity.py`

The step and its 10 controls are in `tests/test_s5p_missing_sensitivity.py`. It was smoke-run on the real tables,
ledger, status files and a fresh classification on 2026-10-01: completed plus missing equals submitted at every look
(400 after batch 1, 200 after batch 0).

- **Classification**, per submitted batch from the ledger and the frozen tables:
  - **completed**;
  - **interrupted** (the seed running at the kill);
  - **never started**;
  - **unestablished** (anything not accounted for).

  Unsubmitted batches are not missing.
- **Bounds per test.** The claim count moves with the missing draws of its null. Corners:
  - `worst_interrupted`: k + I + U, B + I + U, so unestablished draws count pessimistically;
  - `worst_all_missing`: k + M, B + M;
  - `best_all_missing`: k, B + M.

  Holm with determinacy is re-run under each corner, and so are the κ = 3 replace labels.
- **Looks.** Each look is mapped to its batch count by the products, never by file order. The frozen stopping rule
  is re-applied at every mapped look with the draws missing by then. A look whose batch count is ambiguous (a wholly
  lost batch, or a status overwritten at the same B) is marked unresolved, and stopping is then not certifiable.
- **Power.** Power fractions are bounded with none or all of the missing alternatives detected. The bounds
  **condition on the retained null calibration**; the effect of the null's own lost draws on power is not bounded.
- **Completeness.** The output is COMPLETE, with exit 0, only when four things hold: every null has a final status,
  no task log is unfinished, no seed is unestablished, and every lane's completed seeds are exactly the evaluator's
  own product selection (`s5p_joint.product_files`; partials excluded). Otherwise the file says INCOMPLETE, gives its
  reasons, exits 4, and certifies nothing.
- **Holm with determinacy is not monotone, so the corners are descriptive, not proven extremes.** A rejection is
  reported as **certified** only by the sufficient all-assignment certificate (raised by the peer, Codex). Let R be
  the rejected set. For every member of R, the 95% Clopper-Pearson upper end at (k + M, B + M) must be below α/m.
  The largest worst p in R, (k + M + 1)/(B + M + 1), must also be below the smallest best p outside R,
  (k + 1)/(B + M + 1). Then every member of R is rejected under every assignment.
  - The certificate is computed for M = interrupted only and for M = all missing.
  - A κ = 3 "robust" label is certified only when certified in both families.
  - Decisions outside R are never certified by this check.
- **How it is reported, beside each primary decision** (the `per_test_status` field):
  - "**certified** under all missing-outcome assignments", or certified for the interrupted and unestablished draws
    only;
  - "**can change** (counterexample: <corner>)", only when a corner, which is an explicit and realizable assignment,
    changes the decision;
  - otherwise "**not certified**: survival under all missing-outcome assignments is unestablished". A failed
    sufficient certificate is **not** evidence that any assignment changes a decision.

  The primary decision is reported as the frozen evaluator gives it and is **never** revised from this step. Every
  sensitivity number is labelled as a sensitivity. These are numerical labels. Their scientific interpretation in
  the deliverables, as a stated condition or otherwise, is **Joseph's decision**.
- **Comparison with the independent lane.** That lane computes its own report-side bounds, the simple α/m
  certificate and a stronger step-aware group certificate. The common per-test bounds and the simple certificate
  must agree **exactly**; any difference there is a finding. Different sufficient certificates may legitimately
  differ in strength: a stronger certificate certifying more is not a numerical disagreement.

## 4. The four final fields: wording rules (the measurement and joint-test branches stay distinct)

Each field is filled from the records, never from memory.

| field | rule |
|---|---|
| `campaign_disposition` | Bounded campaign TERMINAL. State both branches separately:<br>(i) **measurement branch: NOT ADMITTED** at the Stage-2 exit (amendment 4, "no reporting definition can meet the frozen useful-precision targets … within the budget"). No measurement construction was run, and the targets were not relaxed;<br>(ii) **joint-5D inference: executed** under amendment 7, with its result as recorded after the independent verification. |
| `reportable_uncertainty_scope` | **No new reportable uncertainty.** s5p constructed and adopted no measurement or covariance product. The adopted scalar-5D trunk `3d7465f6…` and its four travelling measurements are unchanged and are not re-qualified by s5p. |
| `joint_5d_inference_status` | The per-test primary decisions (10 tests, Holm with determinacy, α = 0.05), each stated with:<br>• the amendment-7 conditions (`claims.conditions_stated_with_every_claim`);<br>• the robustness label (A7/A7-VS);<br>• the missing-seed certificate status (§3);<br>• the final B and stop reason;<br>• power per null where amendment 7 allows (MnvTune and GENIE CV only, a = 1; "low power is not evidence for generator agreement");<br>• the independent recompute verdict.<br>It is a statement about H0(G) as amendment 7 defines it (the simple fine-grid hybrid null), not about a measured cross section. |
| `publication_readiness` | **NOT READY**, whatever the joint result. The authorization requires "the joint result and all retained claims to qualify", and the precision-measurement objective (a useful scalar measurement with defensible TOTAL uncertainties) is unmet, because the measurement branch was not admitted. Name the costed remaining requirements. |

**Forbidden phrasings:**
- calling the joint test a "measurement", or implying it validates or qualifies the measurement;
- "the campaign succeeded", without the branch split;
- "READY" or "publication-complete";
- any p = 0; and any certified claim the §3 certificate does not support.

## 5. Status of the three relayed concerns (2026-10-01)

1. **Missing seeds:** the report-side bound is implemented, tested (13 controls) and smoke-run (§3). It runs at
   terminal (§2, step 4). Its certificate answers the non-monotonicity point. Cycle-1 review (Codex) found four
   defects, all fixed:
   - unknown seeds now count pessimistically, and an incomplete output cannot certify;
   - looks are mapped by products, not file order;
   - products are checked against the evaluator's own selection;
   - the power bounds carry their conditioning caveat.

   The wording follows the counterexample rule.
2. **Branch distinctness:** the rules are in §4, and the terminal delivery must use them.
3. **ETA and packing:**
   - Budget revision 6 is live (ledger `b9260acd…`). The applicable forecast is the 209.647 column of
     `REPORT-20260930-s5p-batch1-throughput-eta-cost.md` §2: no refusal up to about 4.83 node-h per batch (the
     measured mean is 4.69; batch 1 alone was 4.59). Terminal is about **2026-10-06T13–17Z**, partition-bound.
   - A re-forecast comes at the batch-3 looks (about 10-02).
   - **No packing switch exists or is planned for live production.** `PLAN-20260930-s5p-packing-benchmark.md` runs
     only after terminal and after the recompute verification, under a separate grant.

# PET improvement campaign (2026-09-22 →)

Diagnostic and method-development campaign following the completed comparison with Gregor's pretrained
PET2-small (`nd-unfolding/pet/configuration_comparison/`, verdict `NEITHER_ELIGIBLE / NO_SELECTION`,
preserved unmodified). **PET is diagnostic method development.** Nothing here is a publication adoption,
an uncertainty product, a central-value change, or a Gate-6 action.

- Authorization: `docs/orchestration/AUTHORIZATION-20260922-pet-improvement-campaign.md` (verbatim grant).
- Scope: `SCOPE-HANDOFF-20260922.md` (byte copy of the handoff the grant names).
- Branch: `pet-improvement-20260922`, from `pet-direct-token-comparison` @ `7090fcc1`.

## State

| phase | question | state | evidence |
|---|---|---|---|
| A | Do the suspected optimizer / shared-step-2 recipe discrepancies exist in the executed path? | A1 done: both CONFIRMED at runtime; repaired per-step driver built and checked | `phase_a/INTENDED_VS_EXECUTED-20260922.md`, `phase_a/receipts/` |
| B | Where is recovery lost? | not started | `phase_b/` |
| C | Which feature/model changes improve recovery? | not started | `phase_c/` |
| D | Do more events help? | not started | `phase_d/` |
| E | Physics robustness, reference calibration, coverage | not started | `phase_e/` |
| F | Conditional alternative methods | not started | `phase_f/` |

Cumulative resource use: `RESOURCE_LEDGER.tsv`.

## Code (task A1)

| file | role |
|---|---|
| `recipe.py` | frozen, hashed per-step `StepRecipe` and per-run `RunConfig` (no TensorFlow) |
| `run_unfold.py` | the driver: engine subclass replacing only `Unfold`/`RunModel`; builds each step's optimizer from its recipe and refuses to train if `model.optimizer` differs |
| `recorder.py` | per-epoch recorder (loss, lr, updates, examples, batch, gradient norms, probe weight tails/ESS); enforces the recipe and the restore policy |
| `closure_data.py` | the historical powered-closure inputs, recomposed from the historical functions, OI-136-safe |
| `feature_arms.py` | named, hashed input transforms (Phase C plugs in here) |
| `authorization_scope.py` | the scope guard the authorization record promises |
| `test_*.py` | recipe/scope/feature-arm tests (no TF) and regression tests on executed objects for every confirmed defect (TF) |
| `phase_a/` | runtime audit harness, level-2 miner, declared-differences check, configs, job scripts, receipts |

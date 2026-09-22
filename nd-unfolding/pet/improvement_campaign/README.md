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
| A | Do the suspected optimizer / shared-step-2 recipe discrepancies exist in the executed path? | done: both CONFIRMED at runtime (A1); repaired per-step driver built and checked (A1); historical headline, data path, feature inventory and resources recovered (A2) | `phase_a/INTENDED_VS_EXECUTED-20260922.md`, `phase_a/receipts/` |
| B | Where is recovery lost? | B1 done (scalar IBU/GBDT/MLP references, reference decomposition, truth learnability); B2 (PET stepwise diagnostics) running | `phase_b/scalar/SCALAR_REFERENCES-20260922.md`, `phase_b/pet/` |
| C | Which feature/model changes improve recovery? | first four feature arms queued inside B2 | `phase_c/` |
| D | Do more events help? | not started | `phase_d/` |
| E | Physics robustness, reference calibration, coverage | distortions predeclared (protocol amendment 1); E1 building the library, identifiability and reference assessment | `PROTOCOL-20260922.md`, `phase_e/` |
| F | Conditional alternative methods | AUSSIE benchmarked at scalar level: gain is miss handling, not the non-iterative form; PET evaluation not justified on this evidence | `phase_f/AUSSIE_SCALAR_BENCHMARK-20260922.md` |

Cumulative resource use: `RESOURCE_LEDGER.tsv`, rebuilt from every `resources-*.tsv` by `aggregate_resources.py`
(`--check` verifies it is current).

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

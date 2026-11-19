# IBUKT declaration amendment A2 (draft for review)

This amendment proposes a fresh paired known-truth screen after run `ibukt-20261119-c` stopped at C-NOM. It changes the IBU target treatment and proposes cap arithmetic for the new run. The reviewed declaration, cap decision, launch binding and stage approvals are separate prerequisites. [Original declaration](IBUKT-DECLARATION.md)

## Objective and interpretation

Ask how two 2D workflows recover the same known truths from the same pseudo-data draws. OmniFold uses the existing Stay-Positive refined event weights. Binned IBU uses the signed data-minus-background histogram. Both pipelines share the pseudo-data truth, reconstructed positive draw, fixed negative template, bank, nominal response inputs and reporting grid.

The paired result compares **two end-to-end workflows that differ in background treatment as well as in unfolding**. The comparison cannot isolate response inversion. It is separate from REF-C2C1's real-data C2 result, including the K=10 distance of 1.03, which uses the refined target. The outcome licenses in the original declaration apply to these two complete workflows and these test truths. A differential within-cell reading is evidence on this paired design and does not identify a cause of the measured data difference. [REF-C2C1 outcome](../../OUTCOME-20261106-ref-c2c1-read.md)

## §3 estimators and controls

The IBU response, truth prior, efficiency/fake convention, extraction, 224-cell grid and 205-cell reporting mask follow the original declaration. Keep K=5 primary for both methods and K=10 descriptive for IBU. Only the supplied IBU target changes.

**Historical C-ID.** Keep prepare's recorded E_R and refined-target C2 K=5 and K=10 reproductions and RooUnfold/NumPy check. They verify the historical inputs, response convention and normalization on real data. Retain C-FULL and the truth nonvacuity checks.

**Signed-target identity.** Before the fitted nominal pair, form the nominal signed histogram on the full reco grid with the bound C2 indexing. The identical positive and negative background templates cancel binwise in this control. Require the resulting vector to equal the nominal response row sums to relative `1e-9` in supported reco rows, with exact zeros in unsupported rows. With both implementations fed that signed target, require RooUnfold and NumPy D'Agostini to agree and each to recover the nominal prior at K=5 and 10 to relative `1e-9` on supported truth columns. Record the maximum discrepancies and supported indices. A reported truth cell must have positive truth and positive response efficiency. The signed-target identity is a separate control from the refined C-ID.

**Admissible signed targets.** After summing the signed weights in reco bins, a nonfinite bin, a strictly negative bin, or a nonzero bin with no response support causes a named STOP before either estimator is fitted. Inspect all 224 bins. Zero in a supported bin is allowed. Preserve the offending indices, signed counts and support in the STOP record. The run keeps the prescribed draws and weights, with no clipping, offset, merging, masking or resampling. Tests must include a negative Poisson net bin, a positive unsupported bin, and exact cancellation in a nominal supported toy.

**C-NOM.** Use the same two target treatments as in the Poisson pairs. The nominal IBU consumes the checked signed histogram. OmniFold consumes the refined nominal sample. The 2% per-cell threshold at K=5 applies to both methods on all 205 reporting cells. Save both maximum residuals and identify both targets. C-NOM remains a prerequisite for a timed pair and the rest of the ensemble. Run c's stopped control remains historical evidence.

## §5 step 4 and receipts

Use the original seven truths, five fixed Poisson draws per truth, and the frozen expansion and template rules. Before the first fit in screen, run a fit-free admissibility pass over the noise-free nominal target and all 35 Poisson targets. Build each signed reco histogram from the frozen draw and template, including the existing expansion-size check, and apply the full-grid admissibility rules above. If any target fails, record its truth, trial, affected bins, contents and support and stop before C-NOM. Preserve a receipt keyed by bank, configuration and target-histogram digests. Tests must show that an inadmissible final draw blocks the first fit and that the admissibility histogram matches the one used by the pair.

After all targets pass, use the checked signed histogram for IBU. Refine the same measured rows once at the original settings and pass the refined weights to OmniFold. Verify each regenerated histogram against its admissibility digest before fitting. A STOP in any pair ends the run under the existing outcome rules. A partial ensemble remains unscoreable.

Use a new configuration identity and include the two target treatments in the signed identity, nominal control, pair and score receipts. Preserve the bank/config/product pins, control chain, per-method K, and existing per-cell readout. Scoring must reject a prior-design control or pair, inconsistent target treatment, and a missing signed-target identity. File names alone do not establish treatment identity.

## Proposed §7 and A1 cost arithmetic

The proposed cap is **6.50 CPU node-hours across all IBUKT attempts**. The amended admission and forecast may use it after the governing decision is merged and cited by exact commit and digest. Carry forward all three observed allocations.

| Slurm job | Terminal state | Actual seconds on one CPU node |
|---|---|---:|
| `61556304` | FAILED | 638 |
| `61559122` | COMPLETED | 832 |
| `61567091` | FAILED | 466 |

The ledger carries `1,936 / 3,600 = 0.5377778` node-hours. A fresh zero-node-hour envstage, 0.50 node-hour prepare, 5.25 node-hour screen and 0.10 node-hour score project **6.3877778 node-hours**, leaving **0.1122222 node-hours (404 seconds)** before the proposed cap. Recheck exact terminal rows and all new actual or reserved charges in fresh `sacct`. Screen admission reserves 5.35 node-hours and limits prior spend to 1.15. Keep the 05:15:00 screen limit and the one-pair forecast, substituting the authorized campaign cap into the existing formula.

Rehearse with synthetic inputs and zero allocated node-hours under the bound guard before fresh staging. Use a new run name and new receipts. The execution binding will pin all changed bytes, record the rehearsal, and require separate exact-SHA stage approvals and fresh fence acknowledgments.

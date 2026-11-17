# IBUKT: paired 2D known-truth recovery screen

**2026-11-17; declaration and code for independent audit. NOT BOUND FOR EXECUTION.**

## 1. Authority, decision, owner and terminal conditions

Joseph approved "go ahead with the IBU test," relayed in the director's instruction of 2026-11-17. The scope here is the declaration and code for seven truths and 35 paired recoveries, followed by a PR and independent audit. A cluster run is explicitly excluded from this approval. Every future connect needs the director's go on its exact script SHA, plus the notices and acknowledgments in section 9. Manuscript wording is untouched.

This asks whether the recorded 2D estimators recover known truth, cell by cell, when fed the same fake data. A difference on data does not establish that either method is correct. Neither agreement with the publication nor nominal closure is the primary statistic. The result can be: both recover within the stated tolerance; one fails at a specified truth/cell; both fail; or unresolved at the screen's noise. These are useful terminal outcomes, not instructions to tune a method until it passes.

The IBUKT lane owns the code and eventual receipt. The director assigns an independent read-only audit before binding, with at most one focused repair round before reassessing material unresolved issues. The setup follows `CAMPAIGN-REVIEW-20260929.md`'s bounded owner/reviewer and terminal-budget advice. No reviewer verdict is claimed here. Baseline for this draft: `5ddf896457cfd75ad69e5855d9c1266884eab47a`, fetched origin/main. This declaration supplements the routed work; it changes no existing scientific adoption.

## 2. Existing work and coordination

The executed comparison is governed by `../measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md`, its BINDING-2, and `../../OUTCOME-20261106-ref-c2c1-read.md`: C2-R1 detects a difference, C2-R2 leaves attribution unresolved. C2's target is the same refined background-subtracted event sample as E_R, not a separate purity subtraction. Its K=5 result already exists and is the IBU identity operand for this screen. K=10 remains an identity/diagnostic operand; this screen's primary K is **5 for both methods**, as instructed.

Reuse the component audit `stageF/methods/secondary-results/component-accounting-20261104/REPORT.md`. It does not certify unpublished MINERvA intermediate arrays. Do not redo its accounting or the completed C2 data scan. COV2D's G18/AR23 coverage and bias readouts are distinct from a paired known-truth comparison. The November 14 G2R covariance adoption changes no central estimator in this screen.

**Coordination before fixing arms:** tier3-design replied by PeerMessage on 2026-11-17 and agreed to separate the missed-event intervention from this screen. The defining records were opened: `../measurement-paper/5d-community-20261024/fd/referee-sensitivity-20261111/RSN-DECLARATION.md` section 2.3 and neighboring `fd/tier3-20261110/T3-PIPELINE-TESTS-DECLARATION.md` section 3.3. Their shared weighted-regression definition is `sample_weight = w_push * w_truth` on the passing rows in loop order, not w_truth alone. Their miss oracle returns `r / w_push` on missed rows, so their pulled weight is exactly r. An all-row oracle-pull control does this for every row. These definitions are retained for the follow-up in section 8; no 5D numerical result is transplanted to 2D.

## 3. Frozen estimators, grid, inputs and identity controls

Code is new under `2d-unfolding/ibukt/`; production modules are imported, not edited. `config.json` pins the driver, helper, C2 implementation, comparison module and generator-ratio bytes. The eventual deployment commit pins this package itself. That SHA and environment/library pins belong in the execution binding before a connect. `run_ibukt.py prepare` executes the recorded E_R driver argv, captures its exact arrays and extraction, and applies C2's RooUnfold implementation to that same refined target. The driver is the current G2R-capable copy with its optional override **off**; the recorded central identity must still pass.

- E_R: `--iters 5 --use-weights --estimator lgbm --seed 42 --branch-select all --bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31`.
- OmniFold classifiers/miss regressor: helper defaults, 100 trees, 8 leaves, learning rate 0.1; seeds 42, 43, 44. Refinement: 400 trees, 31 leaves, seed 45. CPU only; allocated affinity 64 CPUs, OMP/MKL/OPENBLAS = 64/1/1.
- IBU: C2 `binned_problem` and `roounfold_bayes`, same weighted truth/reco arrays, same refined target, K=5 primary and K=10 descriptive. K=10 is cheap matrix arithmetic, not another refinement or OmniFold fit.
- Truth prior and response remain nominal in every recovery. Only the positive fake-data signal is deformed. Reconstructed background and negative subtraction template retain their recorded nominal weights.
- Full 14x16 grid from `re2_driver.py:44-48`; exact positive-StatOnlyCovariance 205-cell publication mask; pT-major order. The driver and config grids must match exactly. Both inference methods use all admitted events/cells, not a pretrim to the 205 output cells.
- Existing truth rectangle, theta_mu<20 degrees, reco selection and finite/weight filters are inherited. Unexpected signal fakes are a STOP. Exact-upper-edge overflow remains the ROOT convention in C2 and histogram output.

Inputs, full digests in config.json:

| staged name | source identity / canonical receipt |
|---|---|
| cv.root | E_R CV omnifile `43f8cc16...`; C2 config inputs.CV_sha256 |
| flux.root | E_R baseline flux `d40aea69...`; C2 config inputs.MC_sha256 |
| er.root | recorded E_R `a5c13fc3...`; C2 config e_r.central_sha256 |
| c2.npz | recorded C2 central `929d0e78...`; `fd/receipts-ref-c2c1/step2/units-centrals/c2_central.done`, key sha256 |
| paper.root | precision comparison `6c6dce72...`; C2 config publication.sha256; used for cell mask only |
| libRooUnfold.so | `0b34e1e3...`; C2 config inputs.roounfold_lib_sha256 |

All source locations must be resolved and frozen by the approved connect's source manifest. Availability has not been observed in this phase. Missing or wrong bytes stop; they are not substituted with a newly produced "reference."

**C-ID, before any fake-data fit:** reproduce E_R and C2 K=5 and K=10 on the recorded real-data inputs to relative 1e-8 in each reported cell. This is identity at nominal configuration, not a claim that real data are nominal truth. Compare RooUnfold and NumPy IBU to 1e-9. Reuse the exact common flux, target, POT, areas and completeness from the driver's extraction. Derive a count-to-cross-section vector by sending unit counts through that extraction. Save its use for each IBU and OmniFold result. Full mask/order and finite checks must pass.

**C-FULL:** the bank retains the full denominator loaded by E_R. On the 205 cells require completeness equal to one within 1e-8, and independently require each of the seven deformed input-truth histograms to match the corresponding full-denominator truth histogram within 1e-8. STOP on failure; do not use an acceptance-extrapolated target as if it were known full truth. The known truth is full-denominator counts times the normalization without the completeness correction. This control is especially necessary for within-cell changes.

The relative identity denominator is max(abs(reference cell), 1e-12 times the largest absolute reference cell); all nonfinite operands refuse. Zero-valued unreported cells are not made into recovery denominators.

## 4. Seven fixed truths

All deformations are applied on truth coordinates before detector projection. The nominal weighted response is kept fixed. This is an event-level simulation test, not pseudo-data generated by multiplying a coarse response matrix by its own prior.

| truth | fixed definition |
|---|---|
| nominal | r=1 |
| genie_mec | exact `2d-unfolding/pv2d/ratios/genie_mec.json`, r on its stated 14x16 truth grid |
| nuwro | exact `2d-unfolding/pv2d/ratios/nuwro.json`, same grid |
| bump | r=1+0.20 exp(-((pT-0.40)/0.10)^2), GeV/c |
| tilt | r=(p_parallel/5.0)^0.10, GeV/c |
| within_plus | r=1+0.50(u-mu_c), u=(pT-lower_pT)/(upper_pT-lower_pT); mu_c is the full nominal truth-weighted mean of u in cell c |
| within_minus | r=1-0.50(u-mu_c), using the identical mu_c |

Outside the histogram grid the within-cell and generator factors are one. All factors must be finite and positive. The within-cell pair changes the response-weighted composition while preserving the full weighted truth integral **in every coarse cell**, up to numerical precision; it is not a null event-level deformation. Their factors lie in [0.5,1.5]. The generator stresses are fixed existing coarse maps, with their existing pooling/support conventions, not new detector-simulated generator samples. They leave within-bin composition nominal, so the complementary within-bin pair is essential.

This concretizes the Phase-1 "two generator-shape alternatives": use the two existing pinned 2D maps rather than build new G18/AR23 5D-to-2D mappings. This choice is made before outputs. No new generator physics, free-proton correction or held-out-generator claim is licensed by reusing these maps. No amplitude or cell is chosen after seeing recovery. Prior use of these maps in PV2D is disclosed: these are development stresses, not unseen validating truths.

## 5. Five paired fake-data trials per truth

Fixed pseudo-data seeds: 771001-771005, generator `default_rng([20261117, seed])`. Simulation rows, response and learner seeds remain fixed. These are **five independent Poisson pseudo-data realizations conditional on one finite simulated bank**, not five independent MC partitions or five training seeds. This replaces Phase 1's provisional partition/seed design to preserve the recorded estimator settings and avoid claiming row independence without event identities.

For each truth and trial:

1. Positive expectation sample: truth-passing/reco-passing signal rows with mean w_reco*r, followed by nominal background rows with mean w_bkg. These weights already carry the recorded POT scaling.
2. Draw independent Poisson counts in that order; expand each row into that many unit-weight data rows. This preserves the production data-row representation (do not replace repeated rows with weighted unique rows, which can alter tree binning/minimum-row behavior).
3. Append the original negative nominal background template once. Counts do not fluctuate that template. A draw above 20 million expanded rows stops for memory; do not clip or truncate it.
4. Run the unchanged 400/31 refinement once. Give the exact same resulting arrays and weights to both methods. Fit nominal-response OmniFold at K=5 and nominal-response IBU at K=5, plus descriptive IBU K=10.
5. Save each full 224-vector, known truth, prior, exact selected indices, configuration/bank/product digests and refinement diagnostics. Neither arm changes response weights or efficiency after the truth deformation.

This samples data counting noise, not simulation, template or systematic uncertainty. It tests response inversion on shared simulation rows; it cannot establish generalization to independent detector samples, true detector-response modeling, or coverage. The full-truth and source-identity controls do not cure that limitation.

## 6. Primary statistic and pre-output readings

For each method, truth t, reported cell c and trial s:

`e_m,t,c,s = estimate_m,t,c,s / known_truth_t,c - 1`.

Report all five signed residuals, their mean b, and `h = 2.7764451051977987 * sample_sd(e)/sqrt(5)`. This is the usual two-sided 95% Student-t multiplier for four degrees of freedom used as a **descriptive noise guard**, not a simultaneous confidence or coverage guarantee. Five trials are a small screen. No covariance inversion or publication chi-square enters this primary reading.

The fixed engineering recovery tolerance is **2% of truth per cell**. It is a screen convention, not an adopted uncertainty or a physics-derived acceptance bound:

- **within tolerance:** abs(b)+h <= 0.02;
- **outside tolerance:** max(abs(b)-h,0) > 0.02;
- **unresolved:** otherwise.

For each truth/cell report the ordered pair of method readings. "OmniFold within / IBU outside," its reverse, "both outside," and "both within" mean exactly these combinations. Any unresolved member keeps that comparison unresolved. No truth-wide winner, multiple-testing significance, automatic estimator choice or covariance block is derived. For within-bin truths the coarse departure is zero; do not divide by the injected coarse change. Report all cells even if power is poor. K=10 is labeled secondary and cannot replace the K=5 reading.

Incomplete ensembles, missing trial IDs, repeated/mismatched truth or cell identities, nonfinite values, changed config/bank/product hashes, or nonpositive reported truth refuse scoring. No partial-ensemble grade. A finding outside tolerance may motivate a separately declared mechanism study; it does not prove that the data's estimator difference has that cause. The all-within outcome supports only these deformations/tolerances and conditional sample.

## 7. Cost, hard cap, gates and time limits

Hard cap **5.90 CPU node-hours**, including all attempts, controls, staging, preparation, reading and failures. No GPU or premium queue. The estimates use `../measurement-paper/5d-community-20261024/COV2D-SCOPING.md` section 3: 0.0489-0.0843 CPU node-h per statistical/central unfold. Thirty-five primary OmniFold fits give 1.71-2.95 node-h; pairing shares the expensive refinement. IBU matrix arithmetic and bank I/O remain overhead. The Phase-1 conservative envelope 3.42-5.90 is retained; no reduction is asserted as a measured runtime. The identity run and bank preparation consume the same cap.

Four single-node envelopes (whole-node charge is conservative even for single 64-CPU steps):

| envelope | maximum --time | reserved node-h | prerequisite |
|---|---|---:|---|
| ibukt-envstage | 00:18:00 | 0.30 | audit, binding, exact connect go and fence acknowledgments |
| ibukt-prepare | 00:30:00 | 0.50 | committed environment/staging PASS |
| ibukt-screen | 05:00:00 | 5.00 | committed C-ID/C-FULL PASS and bank digest |
| ibukt-score | 00:06:00 | 0.10 | all 35 pairs complete and hashed |

These sum to 5.90, not an extra allowance above it. Screen packs at most two 64-CPU processes on one CPU node; the submitted time limit is 05:00:00, with each task enforcing affinity 64. The prepared `screen.sbatch` submits nothing itself. Its tasks run through `nd-unfolding/mnv_guarded_run.py` with the deployment root and a separate import inventory for each pair. The binding must use that same guard for preparation, staging and scoring, with no alternate-checkout allow-list. Slurm stdout/stderr destinations must be bound under the fresh scratch run directory. Environment setup/interpreter and fresh quota/headroom checks are fixed in the later audited connect. Any forecast above the remaining cap, timeout, unexpected numerical failure, lost product, absent pin, fence conflict or inability to validate the environment stops and returns to the director. No automatic resubmission, silent smaller ensemble or changed tolerance.

`jobs.py gate` takes a freshly captured `sacct -n -P --format=JobIDRaw,JobName,State,ElapsedRaw,NNodes` record and the persistent submission-reservation ledger. It charges terminal attempts including failures by elapsed whole-node time; active jobs reserve their full time limit (or greater observed spend); submitted jobs absent from sacct still reserve their limit. Unknown/duplicate campaign allocation IDs or invalid rows refuse. Before each submit the prospective envelope plus spend/reservations must be <=5.90. Record the returned job ID and reservation immediately, before another admission. The connect must also verify submitted TimeLimit/CPU settings and keep the reservation ledger across attempts. Never use squeue.

## 8. Separately gated missed-event diagnosis

Do not add extra fits to the 35-pair screen. Weighted and oracle fits would cost additional unfolds and change the tested estimator; they are not established as negligible under the cap. After the screen, a separate amendment may price these same fixed truths with:

- U: recorded unweighted misses regression;
- W: weight each passing-row regression fit by that iteration's w_push*w_truth, with the same target and regressor settings;
- O: oracle prediction r/w_push on misses, giving true pulled weights r, passing rows untouched;
- OP: all-row oracle pull as a control of step-2 recovery.

Oracle outputs are diagnostics, never estimators. This preserves T3/RSN semantics and complements the 5D study. No script in this PR runs those arms; the amendment must fix readings, seeds, cost and authorization before implementation/execution. A small or orthogonal W shift does not clear the miss component if O reveals remaining extrapolation/step-2 error.

## 9. Cluster and artifact boundary

No cluster command has been run for this declaration. New job family: `ibukt-`. Before any connect: director's approval on the SHA-pinned script; fence notices and acknowledgments from cov2d and tier3-design, with the director coordinating additional overlapping lanes. Peer coordination identified protected E_R/CV/ancillary paths and families cov2d, t2a, ll5d, e96data, rpd_, rsn_, rdx_ and pfb_; re-observe this volatile list before action.

All protected source reads are O_NOATIME. Stage the six explicit source files once, compare full digests, record source atime before/after, and use only the staged copies for ROOT. Plain Python reads outside the stage are refused by the existing C2 guard; bank/receipt reads use O_NOATIME. Lack of O_NOATIME is a refusal, not a fallback. Check project quota as well as filesystem capacity before copying. Jobs write only a fresh pscratch run directory; nothing writes to CFS. No input is purged or deleted by this package. Source manifests, staging receipts, logs, submission ledger, identities and results are preserved for audit under a separately named dated receipt directory.

A local macOS environment cannot execute the ROOT/O_NOATIME production path; synthetic tests validate numerical/control contracts, not a cluster fit. A cluster environment/identity test remains an explicit execution gate, and is not authorized by this PR. Any outcome is first committed with its required ledger/run/status records and reviewed before being quoted. Findings go to the director and Joseph; contact with Ben remains outside this lane's authority.

## 10. Local audit package

- `ibukt.py`: truth definitions, ROOT bin mapping, Poisson row construction, per-cell readings, reservation arithmetic.
- `run_ibukt.py`: unchanged-driver identity capture, full-truth checks, paired recovery and complete-ensemble readout.
- `jobs.py`: exact-pin staging and offline admission arithmetic; no submission or connect function.
- `screen.sbatch`: proposed bounded two-worker CPU execution, inactive until bound and explicitly submitted.
- `config.json`: estimator argv, truths, seeds, grid, external input digests and imported source pins.
- `test_ibukt.py`: synthetic tests including deliberately wrong truth weighting, scale/axis errors, within-bin efficiency sensitivity, incomplete ensembles, Poisson/template separation and failed/active/missing scheduler attempts.

Local validation is recorded in the PR; no fit, run outcome, independent audit or scientific adoption is claimed by this declaration.

# RPD-RECO implementation and local code receipt

This package implements the reconstruction-level d1/d2 diagnostic in
`nd-unfolding/fd_rpd_reco.py`. It supplies code and local checks for the subsequent
code audit and binding 2. It contains no production measurement, run permission,
publication adoption, or change to the estimator, covariance or unknown-cause clause.

The governing design is [revision 2](../../../FD-RPD-RECO-DECLARATION.md), SHA256
`b0eee33c95ccb037c681df8d33dccdf1b3d3af60098bba6545c725f706ebe5d8`, under
[BINDING 1](../../../FD-RPD-RECO-BINDING-1.md). The implementation was frozen at
`6b690fbc89520de53cc3df742270ac07640853ea`, including the later explicit
known-sibling ruling; the routed design bytes are unchanged. `VERIFICATION.json` binds
those files by digest.

The implementation owner is the code lane; agy supplied a read-only independent
second read in an isolated detached worktree. The review answers whether the code
implements the declaration, not whether any scientific outcome is established.
The review budget was two full reads, including correction of the first finding,
plus one focused addendum for the subsequent explicit dump-layout ruling. The terminal deliverable is an open PR with this package; the separate
code audit and director's binding 2 follow. No cluster was contacted and no
scientific computation was performed. Local synthetic fixtures are the only data
used by these tests.

## Interpretation awaiting the binding-2 record

The design's summary order puts C-0 before d2-predict, while its scientific rule
requires the committed MC prediction before any measured key. The director's
reply `6711f520-0201-4b0c-920e-486db0334a3f` resolves this as:

`pins -> p0 -> d2-predict -> step0 -> c0 -> d1 -> d2`.

P0 and step0 read only MC/flux/exposure metadata. Every measured-key read and
consumption of a data-bearing product requires an exact committed prediction
record and matching product. The external prediction is restaged for each
check, preventing a cached copy from hiding a later source change.

The director's reply `0d25e722-5f46-4375-baf0-8126770eee5f` fixes C-0's allocation:
real data counts are exact, using a shuffled fixed-size assignment; signal and
background are independent categorical assignments at their own selected-weight
shares, interpreted as expected fractions. Realized fractions and exact data
counts are disclosed, never read by scoring. C-E controls use reconstructed
p_parallel strata, with energy/q3 from MCgen. These clarifications are explicit
here; this package does not represent them as already written into binding 1.

## Step and test map

All function names below are in the producer. Test names are in
`nd-unfolding/tests/test_fd_rpd_reco.py`.

| Step | Implementation and retained evidence | Discriminating checks |
|---|---|---|
| pins | `Inputs.load_pins`, `stage_copy`, `read_guards`: exact 24-pair membership with a closed twelve-name stat-only sibling list, source/copy SHA, O_NOATIME, source fingerprint, explicit key allowlist | `test_known_siblings_are_stat_only`, `test_pins_bad_and_good`, `test_pin_manifest_guards`, `test_staging_guards`, `test_input_changed_guard`, `test_plain_open_refused_and_staging_allowed`, `test_key_allowlist_and_object_array` |
| p0 | `p0`, `read_flux_histogram`: explicit inventory selections 1D/1M/1N, actual opened staged ROOT path, digest, byte size, histogram, edges, retention, source commit and line-span digests for P-F, parsed mass constants; `runtime_estimate` | `test_p0_real_root_inputs_and_no_data`, `test_p0_refusals`, `test_mass_and_flux_size_guards`, `test_runtime_estimate_and_resource_guards` |
| d2-predict | `aggregate(data=False)`, `prediction_controls`, `predicted_steps`: MC-only paired prediction and product before measured reads; pooled C-E1/C-E3 by reconstructed strata, C-E2 disclosure, common-range cap | `test_real_format_prediction_bins_readback_and_two_bootstrap_seeds`, `test_energy_algebra_only_and_controls`, `test_energy_controls_each_stratum_and_bars`, `test_flux_range_step_function_and_gate` |
| step0 | `step0`, `weighted_quantiles`, `axis_assignments`, `reporting_cells`: fixed muon bins, weighted deciles with merged duplicates and infinite outer edges, four muon strata, 16 reported cells, separate unreported and overflow bins | `test_bins_deciles_and_reporting_cells`, `test_real_format_prediction_bins_readback_and_two_bootstrap_seeds` |
| c0 | `_c0`, `aggregate`, `score_axes`, `calibration_gate`: 20 independent partitions, 200 paired Poisson replicas, same axes/scorer and shared draws; all 1,920 p-values retained on PASS and calibration STOP | `test_real_format_c0_pass_and_stop`, `test_data_partition_exact_and_independent`, `test_c0_calibration_both_sigma_directions_and_offset`, `test_c0_tail_count_and_family_guards` |
| d1 | `_d1`, `group_step`, `_rate_summary`, `hadronic_reading`: two-sided step, muon family tests, rates/POT, unconditional/conditional hadronic tests, descriptive carriers | `test_downstream_scoring_two_seeds`, `test_d2_negative_zero_and_bracket`, `test_rate_per_pot_guard_and_arithmetic`, `test_hadronic_firing_bars` |
| d2 | `_d2`, `classify_flux_swap`, `bracket_outcome`: ordered exhaustive outcomes, paired sigma_f and sigma(s_obs,X-s_pred,X), 12-dof size test, integral background bracket, descriptive mirror/PC | `test_downstream_scoring_two_seeds`, `test_d2_outcomes_and_revision_one_gap`, `test_d2_boundaries_and_signed_prediction_bar`, `test_d2_negative_zero_and_bracket` |

`require_predecessors` checks every predecessor's PASS, code/config identity,
dry-run class and digest chain. `Inputs.require_prediction` checks both the
external committed JSON and this run's JSON/product. `test_every_step_refuses_missing_predecessor`,
`test_predecessor_pass_identity_and_chain`, `test_prediction_required_committed_and_exact`,
`test_committed_prediction_is_staged_before_read`, `test_prediction_content_guard`,
`test_prediction_reproduction_guard` and `test_product_digest_guard` exercise these
conditions. Production prediction JSON must be inside an intact Git worktree at
the committed HEAD; a detached export is insufficient.

`aggregate` reuses each row's Poisson draw across axes, references, strata and all
swap variants. Signal selection assertions and measured finiteness are checked
before binning. No row is removed by the P>=25 statistic rule. Overflow and
unreported rows and weights remain counted. The hand calculation in
`test_leave_one_out_and_bootstrap_sigma_hand_calculation` checks paired noise,
leave-one-out arithmetic, weighted-mean subtraction, ndf and simulation-only
sparsity. The size-test denominator is the paired residual's bootstrap sigma,
including shared-MC covariance, rather than sigma(s_obs) alone.

The CLI limits numerical threads to one and nice to 19, emits a price-review STOP
when the planning estimate exceeds two hours, and refuses an elapsed stage over
two hours. The estimate times a bounded Poisson probe; its factor-ten planning
allowance is explicitly an estimate, not a measured total runtime. Every STOP
has `readings: null`. `require_output_root` rejects CFS before mkdir, including
before a STOP receipt could be written there. Resource, wall-clock, dry-run,
output-existence and CFS refusal have positive/negative tests and REQUIRED mutants.

## Readings and licences

The code retains the diagnostic readings and the following boundaries; this
mapping paraphrases declaration section 8. Note use precedes any paper use,
which remains the publication owner's separate decision.

| Reading | Function / test | Permitted statement; excluded inference |
|---|---|---|
| R-d1.0 SEEN | `step_reading`, `_d1` / negative/zero/boundary and downstream tests | Reco-level p_parallel step, sign and size; no cause |
| R-d1.0 NOT-SEEN-AT-3sigma | same | Not detected at 3 sigma; no claim of absence |
| R-d1.1 and R-d1.2 | `_d1`, `_rate_summary` / downstream, rate arithmetic tests | Firing axes/playlists and rates/POT with uncertainties; no detector localisation |
| HADRONIC-CONDITIONAL | `hadronic_reading` / `test_hadronic_firing_bars` | Difference within common muon bins; no cause |
| HADRONIC-VIA-MUON | same | Difference not detected after conditioning; no equal-response claim |
| HADRONIC-NOT-DETECTED | same | None detected at this sensitivity; no claim none exists |
| R-d1.4 carriers | `_d1` / downstream tests | Descriptive intersection with 1L/1M and the rest |
| d2 NOT-SEEN | `_d2`, `classify_flux_swap` / negative/zero and downstream tests | Stop the d2 reading at the undetected step |
| TRACKS | `_d2`, `classify_flux_swap` / outcome and boundary tests | Removed fraction and agreement with predicted steps; coincidence with assigned flux-file difference. No correct-period/flux judgement, correction, explanation or removal of unknown cause |
| PARTIAL | same | Fraction descriptively; no mechanism wording |
| DOES-NOT-TRACK | same | File difference does not reproduce the step; no broader exclusion |
| INCONCLUSIVE | same, `bracket_outcome` / outcome and bracket tests | Test did not decide; no other outcome's licence |
| Mirror and PC swaps | `_d2` / downstream readback tests | Descriptive only; no classifier input |

## Local evidence and limits

`HEAD-VERIFICATION.json` binds the completed suite and full mutation rerun at
PR head `98a1fea4e4fe550420f0fa3c01fe2f1346484d59`, including exact executable
blob identities and output digests. Its record-checks CI passed. The subsequent
receipt-only commit records these outputs and changes no executable bytes.

- `SUITE.txt`: 71 passed. `MUTATIONS.txt` and `MUTATIONS.json`: all 87 REQUIRED
  mutants killed, complete. Mutants run in isolated module copies. Import and
  collection failures do not count as kills; actual failing test assertions do.
- `local_receipt.py` rebuilds the dry runs and import-closure receipts from this
  checkout, using disposable local fixtures and the test-only descriptor shim.
- `LOCAL-DRY-RUN.json`: pins and p0 dry runs on seeds 17 and 43, twelve real NPZ
  signal/background pairs with object-array axes, and three real TH1 ROOT spectra
  per fixture, with all twelve stat-only nn siblings. A runtime audit records zero
  sibling opens. No real MAT file was opened and no runtime flux selection is made
  for production. Private temporary paths are normalized; fixture digests still
  refer to their original local bytes.
- `NATIVE-NOATIME-STOP.json`: the native platform refuses NOATIME, with no readings.
  The positive local fixtures substitute O_NONBLOCK as a distinguishable test-only
  descriptor flag. This tests the flag guard and copy path; it does not establish
  Linux atime behaviour. There is no production fallback.
- `IMPORT-CLOSURE.json` and `OPEN-CLOSURE.tsv`: 910 loaded files, 419 source grep
  hits, each with its disposition. The exercised producer closure includes NumPy,
  uproot and scipy.stats; the fixture generator and pytest are in a separate
  parent process. No ROOT/TFile is imported. Source grep cannot inspect native
  extension internals; numpy/uproot receive staged paths only, and the active
  Python audit rejects plain original-root reads.
- The integrated null fixture actually passes C-0 at seed 17 and actually STOPs
  at seed 43. The separate planted-step d1/d2 scoring tests at both seeds use an
  explicit synthetic passing predecessor; they do not claim that planted fixture
  passed the null calibration. These are code checks, not a scientific calibration
  or coverage result.
- `AGY-PROMPT.txt` / `AGY-ANSWER.txt` preserve the first review verbatim. Its one
  MAJOR finding was a surviving prediction-SHA mutant after staging changed.
  Missing-file and mismatched-local-record cases were added, and explicit
  Refused raises are now mutated too. The second prompt/answer preserve the final
  bounded read. The final read confirms 67 passing tests and 84 killed mutants,
  discharges the first finding, and reports readiness for the binding-2 audit
  subject to production inventory preflight. Reviewer worktree status was inspected
  before/after each read.

P-F is a source-pinned premise: the configuration binds selected line spans,
commit and explicit assertions. Hash agreement does not prove arbitrary C++
semantics; binding 2 must review that premise against the actual MAT source.
Likewise real MAT histogram compatibility must pass P0 in the intended environment.

The production layout question was resolved by director message
`8099ee8b-200a-406e-8bd3-eef00fd28e0c`, preserved verbatim in
`DIRECTOR-SIBLINGS-RULING.txt`. The committed `fd/receipts-rpd/rpd-a-steps.tsv:30`
and `run/jobA/line4-60786801.log:217` show the auxiliary nn files. The input set
remains exactly the 24 bound lat files. Only the twelve names constructed from
the bound playlist list are permitted siblings, and only their name, size and
mtime are recorded. They are never opened or hashed; no glob exclusion is used.
Any other file, including a thirteenth nn name, refuses. Positive 24-only and
24-plus-12 cases and both unknown-file cases are tested; three dedicated mutants
check allowed siblings, rejection of an extra playlist and the no-open rule.
`AGY-PROMPT-SIBLINGS.txt` and `AGY-ANSWER-SIBLINGS.txt` preserve the focused review
of this later ruling. Actual runtime stat remains the run lane's preflight; no
production run is licensed here.

Disposable fixture artifact paths are explicitly identified as normalized local
temporary paths, not missing binary deliverables. Fixture inputs are reproduced
by tests, rather than committed. Review answers retain their exact Markdown hard
break whitespace because their text is required verbatim.

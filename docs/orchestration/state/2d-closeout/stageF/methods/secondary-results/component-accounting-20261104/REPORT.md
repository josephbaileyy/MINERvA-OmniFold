# B-C: 2D component accounting from committed products

**Disposition: inventory complete; publication-intermediate comparison remains partial.**
The inspected records demonstrate no new numerical upstream defect requiring a correction to E_R.
They establish the adopted input identity and several internal consistency checks, but do not
establish equality with the publication's intermediate pipeline beyond the ingredients in the inspected copy. c2/c1 must therefore
compare estimators on this analysis's inputs, without claiming a reproduction of every published
extraction stage. The director decides the next campaign step; this report neither releases the
hold on those runs nor supplies a binding.

**Authority and scope.** Joseph relayed the director's next assignment after #760: B-C first,
existing committed products only, then C-N; c2/c1 wait for B-C. This is a read-only inventory,
not a campaign declaration. Baseline: `97f1ff8deddddecfad07352ebb5df16377dd8e3c`.
No cluster contact, unfolding, covariance recomputation, numerical substitution or new analysis
run was made. Source reads, source hashing and literal metadata transcription only; cluster
charge is zero. No code, estimator, covariance or manuscript source changes.

**Owner/review/stop.** The component-accounting lane owns the record. One independent read-only
source review, with at most one focused repair, checks the identity chain and inference limits.
The useful terminal answers are a documented upstream defect, or an explicit limit from missing
comparison operands. Success does not require explaining the shape difference. This follows the
bounded-review advice in `CAMPAIGN-REVIEW-20260929.md:17–29` at the baseline. Review evidence is
preserved with this package; the director merges the records PR.

Every source label below resolves to a path, reading lines, full sha256 and the baseline commit
in [SOURCE-INVENTORY.tsv](SOURCE-INVENTORY.tsv). These are source identities, not fresh observations
of external storage. The source list and searches bound every availability statement below.

## 1. Freeze the actual comparison operands

- **Adopted central value:** E_R, `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef`,
  object `hXSec2D`. It is RE-2's refined LightGBM result, not the earlier purity E_U [ADOPT], [ER-SUM], [AGREEMENT].
- **Published precision reference:** `cov_ptpl_minerva_inclusive_6GeV.root`, digest
  `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3`, object
  `pt_pl_cross_section`, with `StatOnlyCovariance` defining the mask [AGREEMENT].
  This is a **committed receipt identity**; the ROOT binary itself is outside this worktree's
  tracked ancillary copy. It was not reopened here.
- **Input to E_R:** CV omnifile `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df`
  and baseline flux `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316`
  [ER-ENV], [ER-RUNS], [ER-PREFLIGHT]. This connects the adopted refinement to the older Stage-A
  accounting on the same CV inputs; it does not relabel E_U measurements as direct E_R measurements.
- **Recorded final comparison:** the E_R receipt gives the area-weighted integrals
  `3.0687381668997114e-38` and `3.03901139455691e-38 cm²/nucleon` [AGREEMENT].
  Its bare bin-content sums are different quantities. The recorded full-covariance comparison is
  descriptive `2.270` per reported bin [TENSION]. Neither final agreement nor an unchanged ratio
  verifies the intermediate operands.

## 2. Stage-by-stage accounting

The publication column refers specifically to the **committed ancillary release copy** in
`2d-unfolding/minerva_paper_anc/`, plus identities in committed comparison receipts. It is not
an assertion that MINERvA possesses no further material. [RELEASE-LIST] enumerates the tracked
release files and [SEARCHES] records the scoped searches. No external website was queried.
<!-- absence-ok: availability is scoped to the enumerated committed ancillary copy and cited comparison records, not all material held by MINERvA -->

| stage | this analysis: evidence and available products | publication-side operand in this copy | accounting and consequence for c2/c1 |
|---|---|---|---|
| Reporting domain and truth selection | E_R's declared driver uses the paper pT/p_parallel grid and the angular truth gate; current event-loop source explicitly separates fiducial, CC/nu_mu and muon phase-space cuts [DRIVER], [LOOP], [KINEMATICS]. | `bin_mapping.txt` supplies the momentum-domain edges. It contains no event-level truth/reco selection or calibration record [MAP]. | Momentum reporting grid is matched by existing Stage-A checks and the E_R receipt. Equality of every selection and beam-frame implementation is **not established by a shared grid**. Use this analysis's canonical gate for the new paired tests; seek publication definitions/intermediates through [QUESTION]. |
| Cell order and reported mask | `hXSec2D` is [pT,p_parallel]; GlobalID is `(Ptbin-1)*16+(P||bin-1)`. Stage A records exact edge/order agreement on its input lineage. E_R's receipt uses 205 of 224 cells [A-ANALYSIS], [CELLS], [AGREEMENT]. | Text result has p_parallel,pT column order and zero-valued unreported bins; mapping supplies GlobalID. The precision ROOT has the opposite histogram-axis order from ours; the comparison maps it explicitly [RELEASE], [MAP], [COMPARE]. | Equal cell counts are insufficient. Bind the exact reported indices and covariance ordering. Do not flatten the publication histogram as though it had our axes, or infer zero-valued cells to be physical zero cross sections. |
| Bin areas and units | Extraction divides by `Delta pT * Delta p_parallel`, then converts square metres to square centimetres. Projections integrate with the perpendicular widths [DRIVER]. Stage A reproduces the older product's formula from saved ingredients [A-ANALYSIS]. | README states differential cross sections divided by bin area, and how to form projections [RELEASE]. | This convention is demonstrably aligned. Keep the explicit area Jacobian and angular event selection separate; do not add an extra geometric angular-area factor. The receipt's bare sums cannot replace area-weighted integrals [AGREEMENT]. |
| Data POT and MC scale | Stage A records data POT `1.057394261158926e21`, MC POT `4.978198462880827e21`, and the global MC scale `0.21240500334472884`; it checks playlist sums. E_R binds the same CV input [A-ANALYSIS], [ER-ENV], [ER-PREFLIGHT]. | The paper exposure quoted in the existing audit is `1.061e21`; the ancillary copy supplies no per-playlist exposure ledger [A-REPORT], [RELEASE-LIST]. | The exposure difference is documented, not silently equated. A scalar final-normalisation change cannot alone explain a shape residual. POT inside background subtraction/MC mixing is a different operation; C-N traces it separately. |
| Flux convention and target | E_R uses the pinned baseline file and the geometry target constant. Stage A's saved flux-bin values and target check, and the unchanged formula, provide the upstream accounting [ER-ENV], [A-REPORT], [DRIVER]. | Final result and covariance exist, including a flux covariance. The copy contains no CV energy spectrum, integration recipe or target-count ingredient [RELEASE], [RELEASE-LIST]. | Flux covariance is not the central flux spectrum. Preserve `Phi_i` and target convention; no new flux replacement is justified from an uncertainty-width difference. The publication's exact nominal flux/constraint/integration recipe remains a question. |
| Selected reco signal and background | The saved older input histograms and data count are in Stage A. The direct E_R health record has `n_data=4091707`, signed target sum `3972574.631186321`, refined sum `3972573.2249477347`, and the recorded refinement settings [A-ANALYSIS], [ER-CHECKS]. Selected reco signal is the reco-passing truth-eligible MC array weighted by `w_reco`; `hEffNum` bins these events in truth coordinates and is not a selected-reco spectrum. The ordinary refined path includes any signal fakes in the background histogram and injected signed sample; only the `p1_on` background-bootstrap stream refuses nonzero fakes. E_R's health record has `background_stream=false`; its working central run does not exercise that guard [DRIVER-BKG], [ER-CHECKS]. | No selected data, selected MC signal, background decomposition or subtracted reco vector is in the enumerated release [RELEASE-LIST]. | These E_R scalars check the refinement's integral, not its per-cell shape or equality to the publication. `hMeasTrain2D` is a purity diagnostic in the full-container driver; the signed/refined event sample is the actual refined training target [DRIVER-BKG]. Bind the correct target in c2/c1. |
| Efficiency and input completeness | `hEff2D = hEffNum/hEffDen` is diagnostic. `hOFCompleteness2D = input-truth/full-truth` is the extraction divisor. Stage A measured unity completeness on the reported input cells; E_R's `PB-ER-eff` check reproduces the J0 purity arm's selection-efficiency histogram bitwise [A-REPORT], [ER-CHECKS], [J0], [DRIVER-COMP]. | No numerical selected/full-truth efficiency pair, acceptance denominator or response migration matrix appears in the release copy [RELEASE-LIST]. | Do not divide the OmniFold result by selection efficiency again. Do not use the legacy incomplete-input correction as the present central correction. The E_R check is on `hEff2D`; it is not an independently measured equality of every E_R ingredient to the publication. |
| Unfolded yield and response | Driver writes `hUnfold2D` from step-2 ratios times input truth weights. RE-2 preserves full ROOT containers externally; the committed `reduce.json` preserves final central vectors, not a publication response [DRIVER-U], [REDUCE], [ER-PARTC]. | No pre-efficiency unfolded event-yield vector, response/migration, prior or regularisation study products are in this copy [RELEASE-LIST]. | The requested numerical comparison stops here. The final published cross section cannot uniquely reconstruct yield without flux, target and efficiency conventions. A binned run on our response is a third estimator on our inputs, not a reconstruction of the unavailable published response. |
| Final cross section and uncertainty | E_R/Q_R are adopted; model dependence is separate. Existing comparison receipts and tension anatomy use the refined E_R [ADOPT], [AGREEMENT], [TENSION]. | Final cross section, model prediction and total/statistical/flux/muon-energy covariance text files are committed; the precision ROOT identity survives in the receipt [RELEASE], [AGREEMENT]. | Final comparison exists. It supplies no unique upstream decomposition. Bind the precision reference and use the frozen covariance/mask convention; neither combined shared-systematic covariance nor a favourable pseudoinverse cutoff identifies the cause. |

## 3. Two convention traps that do not establish a new upstream defect

**Flux metadata sum.** Stage A reports `Phi_i = 6.2433433768512e-4 m^-2/POT`, broadcast
across the pT bins. The stored `fluxIntegral_m2_per_POT = 0.008740680727591705` is the sum
of those repeated bins, not a second physical integrated flux. The driver reads the individual
bin, not this metadata parameter [A-REPORT]:151–174, [DRIVER]:1271–1325,1818–1841. Substituting
the metadata sum into the extraction would introduce an error; the adopted path does not do that.
The old reference's warning about substituting a paper scalar must not be read as a measured
factor-sized disagreement between physical fluxes. This inventory does not compare the publication's
flux spectrum, which is outside the inspected copy.

**Flux-axis mismatch.** The baseline flux histogram has some different pT edges from the analysis
grid. Stage A explicitly records this and observes values equal to one floating-point ulp across
the bins, so index-based use has no numerical effect for this central histogram [A-REPORT]:167–172.
This is not permission to ignore axes in an energy-dependent or nonconstant histogram.

**Text versus precision ROOT.** The ancillary README supplies the ROOT covariance for precision.
Stage A records a small final-integral difference between the rounded text and ROOT versions
[A-REPORT]:116–120. The primary E_R comparison is pinned to the precision ROOT above. The present
inventory neither re-inverts rounded covariance text nor measures the effect of its rounding.

## 4. Missing publication intermediates and the factual question

[QUESTION] is **PREPARED, NOT SENT**. It asks whether matched intermediate arrays and their
processing/normalisation metadata can be supplied, and identifies the specific objects needed
at each unresolved row. It does not ask for a scientific endorsement or claim a defect in the
publication. No collaborator, coauthor or support service was contacted.

Internal missing-operand boundaries are recorded too: the adopted E_R ROOT file is digest-bound
and archived by RE-2, but its full ingredient histograms are not all serialized into the committed
readouts. The current inventory does not convert a remote path or digest into a local numerical
measurement. A recovery/read beyond the records remains a separately governed action.
<!-- absence-ok: missing operands are scoped to RELEASE-LIST and the cited RE-2 committed readouts; no global absence claim -->

## 5. Handoff to limitations-catalog: what c2/c1 should test

1. Bind E_R, its CV omnifile and baseline flux by digest; do not substitute E_U, the exact-split
   cross-check, a 1D-projection input or a later universe-only CV.
2. Use the same signal phase space, cell identities, bin areas, target/POT convention and complete
   truth denominator in both arms. Record the binned algorithm's response, missed-event handling,
   background subtraction and any departure from the refined event target explicitly.
3. Preserve the actual refinement target identity. A binned background method that differs from
   signed/refined subtraction is a confound, not a pure unfolding-only intervention. If the
   campaign uses the background-bootstrap stream, verify its no-signal-fakes precondition;
   success of the central run alone does not test that conditional guard [DRIVER-BKG].
4. Keep iteration/regularisation choices fixed by the declaration and simulation evidence; do not
   select by closeness to the published data. Bind the precision publication reference and its mask.
5. Report paired differences and their covariance as declared, with finite-ensemble/rank treatment.
   Agreement between methods does not prove that upstream ingredients match MINERvA; a difference
   does not establish that either method is correct. Retain the missing-intermediate boundary.
6. Existing refined-input eigenmode anatomy [TENSION] can guide description. Selecting modes or
   cutoffs after reading a favourable result is not an explanation of the residual.

**Terminal routing:** B-C has supplied the requested existing-product accounting and its gaps.
There is no demonstrated new upstream numerical defect in these records that this lane proposes
correcting before c2/c1. The director should read this disposition before deciding whether the
existing declarations test the intended question. It is not a PASS on the publication's inputs,
a covariance/coverage claim, an admission or a compute go. C-N follows in the companion inventory;
C-R/d1 and d2 remain limitation-resolver's work.

[RELEASE-LIST]: RELEASE-INVENTORY.tsv
[SEARCHES]: SEARCHES.txt
[RELEASE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/minerva_paper_anc/README#L1
[MAP]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/minerva_paper_anc/bin_mapping.txt#L1
[ADOPT]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md#L30
[ER-SUM]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_readout/sums/SHA256SUMS.J1.1#L1
[AGREEMENT]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/receipts/RECEIPT-agreement-windows.json#L1
[ER-ENV]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_env.sh#L7
[ER-RUNS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv#L1
[ER-PREFLIGHT]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_readout/preflight/inputs.stat#L1
[ER-CHECKS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_readout/k1_core.json#L1
[ER-PARTC]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/RE2-PARTC-REPORT.md#L122
[J0]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/RE2-J0-REPORT.md#L75
[REDUCE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/reduce.json#L1
[TENSION]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/receipts/figs/tension_report.txt#L1
[A-REPORT]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageA/REPORT.md#L88
[A-ANALYSIS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageA/operands/analysis.json#L1
[A-INPUTS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageA/operands/inputs.json#L1
[DRIVER]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/re2/re2_driver.py#L44
[DRIVER-BKG]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/re2/re2_driver.py#L1932
[DRIVER-COMP]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/re2/re2_driver.py#L1155
[DRIVER-U]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/re2/re2_driver.py#L2408
[LOOP]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp#L1694
[KINEMATICS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h#L61
[COMPARE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/compare_to_paper_fullcov.py#L47
[CELLS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/uq/reported_cells.py#L1
[COMBINER]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/2d-unfolding/combine_flux_MEFHC.py#L1
[FLUXCHECK]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/playlist-spread-20261014/outputs/fluxcheck.json#L1
[PLAYLIST]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/playlist-spread-20261014/REPORT.md#L48
[RPD-RULE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION.md#L267
[RPD-CONTROLS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/run/controls/controls.json#L1
[RPD-READOUT]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/run/readout/fd_rpd.json#L1228
[RPD-D]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/run/stageD.json#L145
[RPD-INPUTS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/nd-unfolding/fd_rpd_inputs.py#L72
[RPD-GATE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/nd-unfolding/fd_rpd.py#L474
[BASE-PINS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/nd-unfolding/fd_rpd_inputs.py#L72
[ARCHIVE-MANIFEST]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv#L1820
[ARCHIVE-VERIFY]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/publication/release/preservation/anatuple-data/DATA-SHA256SUMS#L1813
[COPY-VERIFY]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/publication/release/preservation/anatuple-data/copy-verify.txt#L1
[COPY-RECORD]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/publication/corrections-20261008/RECORD-20261009-anatuple-data-cfs-copy.md#L51
[C04-VERIFY]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/2d-closeout/stageB/verify-c04-x01/VERIFICATION.md#L4
[RECO-DECL]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-DECLARATION.md#L35
[RECO-BIND]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/97f1ff8deddddecfad07352ebb5df16377dd8e3c/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-BINDING-1.md#L29
[QUESTION]: ../../../../../../QUESTION-20261104-published-2d-extraction-intermediates.md

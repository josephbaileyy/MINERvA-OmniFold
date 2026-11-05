# C-N: per-playlist flux and POT provenance from existing records

**Disposition: integrated-flux and POT chain identified; energy-spectrum candidates recovered;
P0 runtime identification remains required.** The archived records supply the individual
baseline-file byte identities, the per-playlist POT and repeated integrated-flux values, the
production combiner and the RPD C1 results. They also supply candidate unintegrated flux files
with full digests, including both `g4numiv6` and `gen2thin` families. The preserved file names
and integral values alone do not select the runtime MAT CV histogram or establish d2's premise.

**Authority/order.** This follows the director's C-N assignment after B-C. Baseline:
`97f1ff8deddddecfad07352ebb5df16377dd8e3c`. Read-only committed-record inventory, zero cluster
node-hours; no cluster connection, ROOT open, new flux build, flux swap, bootstrap or unfolding.
Metadata values are literal transcriptions, not new measurements. C-R/d1 and d2 are owned by
limitation-resolver; this inventory supplies provenance to their separate binding process.
No scientific product, code or manuscript text is changed.

**Owner/review/terminal rule.** This records lane owns the inventory. One read-only source review,
with at most one focused repair, checks provenance and the boundaries of F1/C1. Completion means
available identities and remaining runtime/input gaps are explicit, not that a flux or period
cause is identified. The completed [shared source review](../component-accounting-20261104/REVIEW-DISPOSITION.md)
found no material issue remaining. The shared source identity list is
[the B-C SOURCE-INVENTORY.tsv](../component-accounting-20261104/SOURCE-INVENTORY.tsv).

## 1. Three different quantities called flux

| object | actual content and provenance | what it cannot establish |
|---|---|---|
| Per-playlist baseline `pTmu_reweightedflux_integrated` | An integrated per-POT flux, broadcast over the pT bins. Literal per-bin values are in Stage-A `inputs.json`; the global data-POT-weighted combination is the production file `d40aea69…` [A-INPUTS], [A-REPORT], [COMBINER]. | It has no E_nu axis and cannot supply an energy-dependent swap ratio. |
| `fluxIntegral_m2_per_POT` / historical `flux_sum_m2_per_pot` | The sum of the broadcast pT-bin contents in the audited 2D products/playlist records, not a new physical integration over energy [A-REPORT]:151–174, [FLUXCHECK]. | It cannot be used as the extraction's Phi_i, or compared directly with an energy-integrated physical scalar without undoing the duplicate-bin convention. |
| MAT flux ROOT spectra | Candidate energy spectra exist in the preservation manifest, with positive-PDG-14 files for the period labels in two flux families [ARCHIVE-MANIFEST], [ARCHIVE-VERIFY]. | A preserved filename/hash is not evidence that a particular runtime MAT instance opened it, chose a particular histogram, applied a particular constraint, or used a particular generation-flux denominator. |

`playlist-integrals.tsv` copies each recorded baseline data/MC POT, the first pT-bin integrated
flux value, its baseline-file digests, and RPD C1's `s_X/s_ALL`. No averaging, new ratio or new
flux calculation is performed by that transcription. The original complete flux-bin arrays
remain the source. `energy-spectrum-candidates.tsv` copies the archived file identities, size
and relative path without assigning a runtime role.

## 2. POT and normalisation chain

1. **Baseline accounting.** Each playlist's data and MC `POTUsed` is recorded independently of
   its event yields. The combined omnifile carries `dataPOTUsed` and `mcPOTUsed`; Stage A records
   their agreement with the playlist sums and the flux file's data-POT weighting metadata
   [A-ANALYSIS]:134–185, [A-REPORT]:122–149. This is historical internal consistency, not a new
   measurement of the beam exposure or agreement with the publication's exposure ledger.
2. **Merged 2D extraction.** `get_pot_scales` uses the combined `dataPOTUsed/mcPOTUsed` for MC
   weights; extraction uses the combined data POT [DRIVER]:126–139,1782–1783,1271–1325.
   This is the documented global-mixture convention, not per-playlist rescaling of every event.
   The existing playlist study measures a limited mixing effect; it is not a universal bound
   on all multidimensional or nonlinear estimator changes [PLAYLIST]:48–104.
3. **Flux combination.** The producer explicitly uses
   `Phi_eff[i] = sum_X POT_data,X * Phi_X[i] / sum_X POT_data,X`.
   It checks per-playlist flux axes against each other and writes the weighting exposure
   [COMBINER]:39–96,109–124. It is data-POT-weighted, not MC-POT-weighted or RPD-exposure-share-weighted.
4. **RPD individual playlists.** The C1 declaration uses `s_X = D_X/M_X`, `s_ALL = sum D/sum M`,
   and requires per-playlist MC arrays to differ from the pooled arrays by `s_X/s_ALL`. The
   committed C1 receipt records PASS, including weights, histogram sums, flux and data POT
   [RPD-RULE]:267–295, [RPD-CONTROLS]:1–61. This tests the declared conversion, not whether global
   and separately unfolded estimates must be identical.
5. **RPD exposure shares.** `e_X` is proportional to `D_X * Phi_X`, normalised across playlists;
   the code uses the pT-constant integrated value [RPD-INPUTS]:407–437. These shares are not
   raw POT fractions and do not replace the production combiner's weighting rule.

A uniform factor applied only to a final spectrum cancels in a high/low shape ratio. A change
to exposure inside MC scaling, background subtraction, classifier fitting or playlist mixture
can change shape. An energy-dependent flux ratio changes MC weights as a function of true energy,
and can change reconstructed shape through the response. These are algebraically different
operations; this inventory applies none of them to data or simulation.

## 3. What the existing RPD F1 and C1 evidence proves

**F1 contract.** The period-wise data-POT-weighted combinations must reproduce 5B's period
flux files, and the full combination must reproduce the pinned production flux. Contents,
POT and edges have explicit predicates; flux-error differences are a printed diagnostic
[RPD-RULE]:267–273, [RPD-INPUTS]:391–405. The source refuses to consume a flux record unless it
has schema `fd-rpd-flux/1` and verdict PASS [RPD-INPUTS]:530–535.

**Committed receipt boundary.** The RPD readout, controls and stage-D receipts identify the
consumed `flux/F1.json` by sha256
`649f9d55422016367a69350a742799bb4187c475696bfdb9a800e82723af794f`
[RPD-READOUT]:1228–1233, [RPD-CONTROLS]:250–256, [RPD-D].
The inspected committed RPD run directory does not contain that full F1 JSON. The surviving
records and refusing consumer trace successful use; they do not expose every per-playlist
F1 numerical residual for an independent reread here. Those raw residuals are **not remeasured**.
The exact scoped file search is in the shared `SEARCHES.txt` [SEARCHES]. Recovering the existing
receipt is an internal records follow-up for the owning lane under its authorised read workflow,
not an external question or permission for this lane to connect.
<!-- absence-ok: full F1 availability is scoped to the enumerated committed receipts-rpd files and pinned digest, not to cluster storage or all history -->

**C1 direct result.** The committed controls JSON has `C1.pass=true` and every graded key true,
including flux, per-playlist weight conversion, denominator/background histogram sums and data POT.
The `measured_weights_share_equal` diagnostic has entries below its adjacent nominal share field;
that is not a failed flux/POT predicate. The declaration explicitly treats differences from
ALL's measured weights as descriptive; the (e) estimator does not read those weights
[RPD-RULE]:285–295, [RPD-CONTROLS]. Do not reinterpret that diagnostic as an unrecorded C1 failure.

Neither F1 nor C1 proves the absolute physical flux, the publication's flux choice, the equality
of original generated energy spectra across a group, or a cause of the period difference.
The code grouping is **reweighted to the same flux file**, with labels
`1A–1F -> 1D`, `{1G,1L,1M} -> 1M`, and `1N–1P -> 1N` [PLAYLIST]:152–163, [RPD-RULE]:267–273.
The historical integrated baseline values happen to coincide within those groups [A-INPUTS];
that is not an energy-spectrum equality measurement.

## 4. Concrete input identities for d2, and the remaining P0 obligations

The preservation manifest and destination checksum record agree on the candidate byte identities
in `energy-spectrum-candidates.tsv` [ARCHIVE-MANIFEST], [ARCHIVE-VERIFY]. The recorded preservation
root is given in [COPY-RECORD]:63–65, with the relative paths from the manifest. Its current
existence, retention, runtime symlink target and access permissions have not been rechecked here.
The tabulation is an acquisition/identity route, not a current-storage receipt.

Both `flux-g4numiv6-pdg14-...` and `flux-gen2thin-pdg14-...` must be distinguished. The manifest
also distinguishes the plain 1D files from the `rearrangedUniverses` versions. This inventory
**does not choose one family or substitute a candidate for the runtime input**.

Binding 1 explicitly assigns C-N the flux-file identity inventory [RECO-BIND]:43–46. It does not
waive the P0 requirements in the owning declaration [RECO-DECL]:61–75,186–194:

- Bind the actual MAT checkout/library and source lines selecting the flux version, playlist
  mapping, generated denominator, constraint treatment and histogram name. The historical
  C04 verification pins MAT `35097b65ab1680db8058f9ede18fecffdc3a1ea3` and its constraint route,
  but that is not a fresh measurement of the d2 runtime [C04-VERIFY]:4,24–35.
- Compare the **actual file read** to the candidate/preserved bytes; record its resolved path,
  current SHA, histogram name, E_nu edges and successful open in the execution environment.
- Establish P-F from that source: the generation denominator is independent of the target flux
  file, so the intended swap reduces to the target/own energy-spectrum ratio. If not, the
  declared d2 stops before a swap. The names and integrated fluxes cannot settle that premise.
- Keep source/target energy ranges and any constraint-induced CV correction explicit. A central
  energy spectrum and a constrained flux-uncertainty band are different objects.

These are the owning lane's existing P0/binding obligations, **not a new run request from C-N**.
C-N provides the recovered byte identities now; the source/histogram/runtime selection remains
**NEEDS P0**, without an assertion that the inventory supplied everything needed to execute d2.

## 5. Coordination handoff

- **To limitations-catalog:** B-C's canonical denominator, flux-broadcast, mask and background
  distinctions apply to c2/c1. No claim of exact publication-input equality follows.
- **To limitation-resolver:** use the candidate identity table to avoid treating the baseline
  integrated-flux file as an E_nu spectrum. Retain P0 and P-F. The F1 raw JSON is an identified
  internal receipt gap; attach it when its owning authorised workflow provides it.
- **To Joseph:** the publication-intermediate QUESTION is prepared in B-C. This inventory does
  not require a new muon-calibration request; calibration-specific diagnostics remain with C-R.
- **Unchanged:** no A campaign, no prior change, no covariance replacement and no publication
  claim. Declarations and execution remain with their campaign owners and the director.

[SEARCHES]: ../component-accounting-20261104/SEARCHES.txt
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

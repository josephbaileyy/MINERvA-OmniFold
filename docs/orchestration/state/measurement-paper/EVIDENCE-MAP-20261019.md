# Evidence map for the physics-measurement handoff

Tree: detached worktree of `origin/main` `a148f22f`, read on 2026-10-19. All paths are repo-relative and all line
numbers refer to that commit. P = `docs/analysis-note/paper_body.tex`, N = the note files, O = `docs/orchestration`,
A7 = `O/state/s5p/contract-amendment-7-production-admission.json`, T = `O/state/2d-closeout/stageF/PLAIN-LANGUAGE-PASS2-IMPLEMENTATION.md`
(where the outside referees' physics points were triaged; §5 there is the source of items 1, 3, 5 and 6).

**Not recorded in the tree.** Two things this handoff depends on have no record at `a148f22f`:
- **The new compute approval for a measurement paper.** The newest AUTHORIZATION file is dated 20261016. `AGENTS.md:92`
  says "There is no standing authorization here for a new scientific analysis."
- **Joseph's 2026-10-10 GBDT/5D pause.** It is not in the tree; see item 4(e).

The approval and the pause need committed records before any launch.

---

## 1. Calorimetric (hadronic-recoil) response uncertainty

**(a) Paper and note**
- The abstract says "the nuisance model has no calorimetric recoil-response uncertainty" (`main_paper.tex:79-80`).
- The paper names it as an interpretive limit at P:92-93 and in condition (ii), P:884-886. The dedicated section is
  P:1016-1056. P:1046-1050 says: "The null distributions were not regenerated with the variation. Particle-species,
  energy-dependent, and resolution effects … were not tested." The conclusion's remedy, at P:1100-1103, is "a response
  band drawn through the calibration".
- The note has the same content at `sec_joint.tex:164-168` (condition ii) and `:326-376` (§joint5d-response).
  `:355-356` says "The ±4% size is a labelled exploratory sensitivity, not a validated uncertainty prescription."

**(b) Governing records**
- `O/DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md:69`: weight-only implementation "does not prove that
  all relevant…" response variations are represented. `:83`: "Lack of a collaborator response does not reopen PM-1".
  `:85`: "It does not authorize inventing a hadronic-energy shift or adding an arbitrary uncertainty."
- `O/QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md:8`: "STATUS: PREPARED, NOT SENT." Paper-wide row R15
  is "BLOCKED-EXTERNAL" (`O/CAMPAIGN-s5c-20260924-paper-wide-table.md:46`).
- A7:14 is the claim condition: "there is no recoil-energy-scale band in the analysis's systematic set …
  hadronic-response completeness is not established".
- `docs/publication/PACKET-20261005-publication-decision.md` §5.4 (:180-221) and the W2 specification (:263-319). The
  terminal rule is "One δ and one run of W2b" (:312) and "No second δ after the result" (:316).
- `docs/publication/DECISION-20261006-joseph-publication-approvals.md:36-41`: "Accept ±4% solely as the labelled
  exploratory sensitivity, not as a validated uncertainty prescription."
- Results: `publication/w2/W2B-REPORT-20261006.md:3-4`: "the variation moves the data, not the null." The independent
  check is `O/REPORT-20261006-s5p-recompute-w2-recoil-check.md` (AGREE 1379/1379, cited at W2B:18-23).
- No KNOWN_ISSUES row and no VALIDATION_LEDGER row covers the response gap or W2. Search:
  `grep -i 'recoil|calorimetr|hadronic.response|response band'` over both files found only historical recoil-PET rows.

**(c) Inputs and code**
- Existing code:
  - `publication/w2/src/event/RecoilResponseUniverse.h` (one coherent scale applied to `NewEavail()` and to
    `q0=<tree>_recoil_E`);
  - `publication/w2/src/runEventLoopOmniFold-recoil-response.patch`, `build_w2.sh`, `sbatch_w2b_evloop.sh`, `w2b.py`
    and `compare_omnifiles.py`.
  - The tracked event loop is unchanged; it is byte-pinned (`W2A-REPORT-20261006.md:34-36`).
- Per-particle machinery, as recorded in `O/state/inelastic-high-region-20261011/REPORT.md` §11.1 (:836-847):
  - The MC AnaTuples carry per-species visible energy, `blob_recoil_E_{tracker,ecal,…}_{p,meson,em,other,lown,midn,highn,xtalk,mu}`,
    and MAT shift branches `part_response_recoil_allNonMuonClusters_*_err`. This comes from an agent-read branch listing
    with no receipt; the `blob_recoil_E` family is in `nd-unfolding/pet/improvement_campaign/phase_a/receipts/feature_inventory.json`.
  - Our stored products do not carry species ("absent").
  - "There is no calorimetric response universe, and MAT's response band is commented out at … `systematics/Systematics.h:87-89`"
    (a pscratch copy, untracked; the systematics directory is not in git).
  - Data have no truth species, so species variations are "possible only on the simulated-response side" with a new
    event-loop pass of about 50 lines (:849-852).
  - The MAT default sizes (`ParticleResponseDefaults.h`, agent-read) are meson 5%, EM 3%, proton 3.5%, neutron 25/10/20%
    and other 20% (:872-880, :448-450).
  - W2B:31-32 also records that "MAT's per-particle response map is not used; it is commented out".
- Still missing:
  - any response-varied null ("No response-varied null exists", :844);
  - any neutron-response calibration (:845);
  - the unsent collaborator question.

**(d) Costs**
- W2a measured 0.0985 node-h. The W2b projection was 2.38–3.03 node-h, or ≤ 6.06 with a retry margin
  (`W2A-REPORT:107-146`). W2b measured 1.898, or 1.997 with W2a (high-region REPORT:1000).
- Species screening is ≈ 19–42 billed CPU node-h [assumption] (high-region REPORT:1001-1011).
- A calibrated response validation (response-varied nulls) is "order 10² node-h (packet estimate ~200, unmeasured)"
  (high-region REPORT:1005; PACKET:321). It is repeated in `docs/research/MINERVA-MODEL-STUDIES-SYNTHESIS-20261012.md:295`.

**(e) Dispositions to respect**
- PM-1 forbids inventing a shift. A new size needs a documented source and Joseph's ruling.
- W2 is terminal: one δ, no second δ.
- High-region REPORT:103 asks for an independent MINERvA hadronic-response reviewer before any validation is designed.
- The response-mismatch closure (`N/app_response_mismatch.tex`, "protocol implemented; not yet run") is deferred:
  `O/DECISION-20261014-joseph-2d-endpoint-and-open-items.md:29` reads "defer it".

---

## 2. Hybrid nulls, the fine grid and refinement

**(a) Paper and note**
- The hybrid null is defined at P:743-761. The fine grid is "14×16 … times 7 Eavail, 7 q3, and 6 W" (P:753-754), and
  "for the Tune v1 … it is H0 exactly" (P:756-757).
- Condition (i) is at P:856-883. The rate per halving is "a value taken from the review of the test design whose
  calculation is not recorded" (P:870). κ=2 is used for claims and κ=3 for robustness (P:872-877).
- The κ scan is at P:913-922: up to 5.25 δ_fine, and "up to 5.17 … with the recovered pseudo-experiments", which
  "bounds neither the actual residual nor the convergence".
- The note covers the same ground at `sec_joint.tex:19-33`, `:123-149` and `:233-248`. `:241-245` gives the endpoints
  5.2547/5.2563 (5.1688/5.1703 with the union) and names the test that loses determinacy first (GENIE+MEC shape).

**(b) Governing records**
- A7:9 (`claims.family`): "the SIMPLE fine-grid hybrid null … with MnvTune v1's shape … below it; for MnvTune … H0
  exactly".
- A7:10 (`claims.rejection`): "the W-norm step … shrinks by 0.45-0.76 per halving … kappa = 2 is its central value".
  A7:13: "the M1 check is not converged (fine vs merged-x2 is 0.50-0.86 of coarse vs fine in L2)".
- The origin of 0.45–0.76 is `O/REVIEW-20260927-s5p-admission-confirmation.md:49`.
- Its provenance is unresolved: `docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md:81`
  says "No recorded operand reproduces it". `:241` (G6b) says only "its author, or a new pre-registered measurement (a
  new study, not authorized here), could resolve it". `:346` puts it to Joseph: accept it as disclosed, or authorize a
  new measurement.
- M1 data: `O/state/s5p/campaign-state.json:133-134` (L2 ratios 0.76/0.86/0.54/0.50) and
  `O/state/s5p/stage3/m1/fine-minus-mid-*.json`. The producer is `docs/publication/corrections-20261008/m1_f2_norm_ratio.py`.
- κ scan: `publication/kappa/RECORD-20261008-kappa-breakdown.md` (cited at P:925). The κ=3 robustness family is set by
  the owner ruling `O/RULING-20260929-s5p-A7-robustness-flag.md` (`campaign-state.json:339`).
- Triage point T:138: "The null inherits Tune v1's hadron composition within cells … valid, text (medium)".

**(c) Inputs and code**
- Grids: `nd-unfolding/s5p_stage1_inspect.py:37-45` (FINE and J_EDGES).
- Fine-ratio truths: `nd-unfolding/s5p_truths.py:165` (`fine_ratio`, which "reweights rows by rho of their fine
  cell") and `:233` (merged grid).
- Pair differences: `nd-unfolding/s5p_pairdiff.py`. The null experiment is `nd-unfolding/s5p_nullexp.py`.
- Generator 5D products: `O/state/s5p/gen5d/` and CFS `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/gen5d{,_fluxfix}`,
  per `O/state/2d-closeout/stageD-inputs/REPORT.md:252-256`.
- The independent generator-event detector-level check is **UNAVAILABLE**. Stage D REPORT:286 says "MINERvA simulation
  not available in this environment", citing `O/state/valencia-feasibility-20261011/REPORT.md:268`, which leaves
  detector-level prediction cost "unknown" at an assumed 10 CPU-s/event.
- Every independent-generator sample is truth-only and has already been inspected: Stage D REPORT:264-276 says "None of
  these is fresh."
- The only priced substitute is truth reweighting under the nominal response (Stage D:287).

**(d) Costs**
- s5p production: forecast ~180 CPU node-h expected and ~280 worst case (A7:34-40). Measured: 207.899 production and
  253.192 for the campaign pool (`O/DELIVERY-20261006-s5p-campaign-terminal.md:97-105`).
- Reproduction tier C (full regeneration) is "about 208 billed CPU node-h" (DELIVERY:159-160).
- No cost is recorded for a further refinement level or a new rate measurement.

**(e) Dispositions to respect**
- A7 and its conditions are frozen. DECISION-20261004 says "Keep all scientific criteria unchanged"
  (`O/DECISION-20261004-s5p-production-budget-extension.md:23`).
- The κ scan and lost-seed recovery are report-only (`sec_joint.tex:302-304`).
- Any rate measurement is a "new pre-registered measurement" (G6b).
- Stage D Q4: "lets just accept the limited version for now" (`O/DECISION-20261014-joseph-stage-d-input-answers.md:24`).

---

## 3. Target: NuWro and GiBUU on C12, data on CH

**(a) Paper and note**
- P:161-166: "GENIE 2.12.10 on CH … NuWro 21.09 … and GiBUU 2019 …, both on carbon". GiBUU stops at E_ν≈20 GeV
  (P:171).
- The note discusses the targets at `N/sec_3d.tex:213-233` per T-reports. The triage reports that neither the paper
  nor the note quantifies the effect.

**(b) Governing records**
- `O/DESIGN-20260911-endpoint-B-generator-comparison-test.md:243-250`: "NuWro and GiBUU are on a C target; GENIE and
  Tune v1 are on CH … the residual target mismatch lands precisely in the dip region … only … where fresh production
  would buy something: a CH NuWro or GiBUU sample."
- T:137 records the point as "valid; disclosed in records, unquantified (medium)", with the remedy "a GENIE CH-vs-C
  proxy".
- `O/state/2d-closeout/stageF/plain-language/PLAIN-LANGUAGE-PASS2-REPORTS.md:1860-1867` gives a counting estimate
  ("a few percent overall, with channel-dependent sign") and proposes the remedy: "a cheap GENIE proxy (CH vs C12-only
  splines and samples in the 109 cells …). Better: NuWro run on H and combined 12:1."
- One measured data point exists: the "C-only vs CH per-nucleon target effect on ρ_C" is −0.25% (high-region
  REPORT:436, `r5_genie_events.json`). It is a single functional, not the 109 cells.
- KI 82 and KI 83 (`KNOWN_ISSUES.md:72-73`, both OPEN) cover GiBUU's 20 GeV cap and the flux-sampling defect, which was
  repaired by reweighting rather than regeneration.

**(c) Inputs and provenance**
- `3d-unfolding/genie/README.md:32`: GENIE target "CH (C12 0.9225 / H1 0.0775 by mass); per-nucleon = /13".
- NuWro: `:125`, "Target C12 (~92 % of CH by nucleons; documented approximation)".
- GiBUU: `:179`, "CC νμ on C12", with jobcard `work_gibuu/gibuu_mefhc_numu.job`.
- Splines for both species: `:233` (`-t 1000060120`, `-t 1000010010`).
- Sample table: Stage D REPORT:264-269. The files are pscratch-only, under
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie/`.
- The H handling hook exists: `3d-unfolding/genie/gen5d_flux_reweight.py:173-191` (`SigmaCC`, target 'CH' →
  (C12+H1)/13, 'C12' → /12).
- NuWro `v21_09_1` is on CVMFS. GiBUU is not on CVMFS (Stage D:288).
- No CH NuWro or GiBUU sample exists (Stage D:288, "UNPRICED").

**(d) Costs**
- Projection basis: NuWro took about 2 min per 100k events on C12 on a login node (Stage D:288, citing
  `README-gen5d-fluxfix.md:189-190`, "documented, not a receipt").
- GENIE v2 took 4 min per 100k (Stage D:287).
- No cost is recorded for a CH run.

**(e) Dispositions**
- Stage D:288 says it is "not established" whether a CH run of an already-inspected generator counts as fresh.
- The custodian/independence constraints are in Stage D §7 (:292-297).

---

## 4. Validated 5D uncertainties

**(a) Paper and note**
- Model dependence is "about 10–13%" against the 10% target (`main_paper.tex:68-71`; P:84-86, P:624-641, P:1088-1090).
- The coverage failure is at P:553-569. The minimum, 0.06, is under the **E_avail tilt**. At nominal truth, two
  quantities fail at 95% (lowest 0.85).
- Seed dependence: P:596-615.
- In the note:
  - RD1–RD3: `sec_5d.tex:206-230`;
  - "the affordable five-iteration setting fails the frozen improvement requirement": `:201-204`;
  - coverage: `:349-366`;
  - D-ID: `:368-384`;
  - seed: `:489-546`.

**(b) Governing records (history)**
- s5c: Tier-S FAIL (futility). `O/OUTCOME-20260925-s5c-tier-s-futility-fail.md:30-33` gives `eavail_tilt` 51/42 futile
  and min 0.060 (J224); the row is VL150 (`VALIDATION_LEDGER.md:213`).
- s5n: "STAGE1_FAIL; no Stage 2; campaign CLOSED" (`O/OUTCOME-20260925-s5n-stage1-development-fail.md:1`; VL151 at :198).
- s5e: diagnosis and candidate R (VL153/154, :186-187).
- s5p Stage 2: `O/RECORD-20260927-s5p-stage2-exit.md:122-147`, with the RD1/RD2/RD3 medians 12.0/9.6/13.4% (:127-131).
  `:143-145` says: "The limitation is scientific, not financial."
- KI 77 (`KNOWN_ISSUES.md:67`, OPEN): "Noise-free traces to 200 iterations show no reduction … capacity 400/31 changes
  it by 3–8%".
- KI 80 (:70) covers the numerical (rounding) instability.
- `O/DELIVERY-20261006-s5p-campaign-terminal.md:148-151`: "No compute increment alone can meet them" (the measurement
  branch needs "a new estimator or regularization method").
- Seed: VL146 (`VALIDATION_LEDGER.md:209`). Adopted under exception: `O/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`.
- D-ID: `O/state/next-preparation-20261009/d-id/REPORT.md:27`: "Branch C in J, EW and H2 … scoped to binned
  estimators". `:28` sets the next action as the endpoint-scope question for Joseph. It landed via merge `7184e436` in
  PR #72, not PR #71 directly. `O/CATALOG.md:91` reads "validates no interval".
- Successor: `O/PROPOSAL-20261005-scalar-measurement-successor.md:12`: "NO-GO for immediate new compute".

**Compute-bound or intrinsic?** The records say intrinsic (prior dependence), not compute-bound:
- stage2-exit:144 and DELIVERY:148-151, quoted above;
- the KI 77 iteration and capacity traces;
- D-ID branch C, which finds weakly constrained response directions, scoped to its binned, signal-only, development
  setting.

**(c) Inputs and code**
- Infrastructure that was built but never run for a measurement: `s5p_universe.py`, `s5p_input_dumps.py` and
  `s5p_assemble.py` (stage2-exit:171).
- The adopted trunk `z-cv.npz` `3d7465f6…` (VL142).

**(d) Costs**
- From stage2-exit:111-114:
  - "≈ 20 iterations at B0 capacity: … 222.6 CPU-equivalent node-h at k = 20 … 328.7 at k = 30";
  - "capacity 400/31 … 190.8 at k = 5, 371.1 at k = 10".
- The deferred 70-node-hour R5/R20/capacity panel is "not requested" (PROPOSAL-20261005:225-231).
- PROPOSAL:44 records Stage C illustrations of 1,902 node-h and ~1.48M naive, both superseded.
- D-ID used ≈1.5 local core-h (d-id REPORT:24).

**(e) Dispositions**
- The frozen targets "are not relaxed" (stage2-exit:146).
- **The 2026-10-10 pause is not in the tree.** `git grep -i paus` and searches for "no I1", "strict-bounds" and
  "long-term objective" found no disposition. The only source is the session memory file `d-id-diagnostic-done-branch-c.md`
  ("Further GBDT production and tuning is paused: no I1, no I2, no strict-bounds study, no more iterations, no s5p
  extension … endpoint not changed"), and it needs a committed record.
- Committed text still lists the endpoint-scope decision as open (d-id REPORT:569;
  `integration-followup/REPORT.md:414`).

---

## 5. W redundancy

**(a)** Paper and note:
- P:131 defines truth W. P:146-149 says the reco inputs "do not, by themselves, provide five independent constraints".
- P:681 is framed as "The fifth observable, W, separates …". P:1066 says "five simultaneous observables".
- The note gives the reco equations at `N/scalar_kinematics.tex:1-19`, input at `sec_3d.tex:92`: "five recorded
  coordinates do not establish five independently constrained physical directions". Truth W is defined at
  `sec_eavailw.tex:21-25`.

**(b)** T:135 says "at reconstruction level it is an exact function of (pT, p∥, q3); at truth level … fixed to within
tens of MeV … valid (medium)". The remedy there is to reword the framing and run "one residual check on a simulation
dump". The detailed row is PLAIN-LANGUAGE-PASS2-REPORTS.md:1780 ("VALID, OPEN"). There is no RECORD, DECISION or KI row.

**(c)** Code:
- `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:396-410` (`GetTrueExperimentersW`, which uses M_n or M_p
  from the struck nucleon);
- `:196-235` (RecoQ3 and RecoW from the same q0).
- The residual check is not run.

---

## 6. Sequential stopping rule and the "p values remain valid" sentence

**(a)**
- P:812-816 now describes the 99.5% look interval. This is the director's C7 ruling, recorded at T:120-123 and F-p2-1.
- P:841-844 still says "the Monte Carlo p values remain valid at the number of pseudo-experiments reached", and so does
  `sec_joint.tex:111-112`.

**(b)**
- Code: `nd-unfolding/s5p_inference.py:89-114` (`sequential_decision`, look_level 0.995, "Bonferroni over at most ten
  looks") and `:127-155` (`holm_determined`, 95% CP). The frozen text is A7:23 (`calibration.sequential_rule`): "the
  p-value stays valid at the B reached".
- T:136 says "unsupported as written. The decisions are conservative … Holm familywise rate is at most 0.89α (a new
  calculation in the director's scratchpad, not a record)".
- Replacement wording is proposed as F-p2-2 (PLAIN-LANGUAGE-PASS2-REPORTS.md:4662; derivation :1853-1857). It is
  listed as open for Joseph at T:165, and it is not applied.

---

## 7. Compute ledger and budget records

- `O/RUNS.tsv` is stale. It has 346 lines and was last touched in `e1821a9c` (2026-08-21).
- 2D closeout delegation: "≤ 700 charged CPU node-hours on m3246", jobs < 12 h, never premium
  (`O/AUTHORIZATION-20261012-2d-closeout-delegation.md:53-58`).
  - Committed grant ceilings are 132.0 of 700 (`O/AUTHORIZATION-20261015-2d-closeout-stageC-production.md:80`;
    re-stated in the 20261016 bindings).
  - Stage C production charged 29.0297 of 100.0 (`O/state/2d-closeout/stageC/production/REPORT.md:24`).
  - Period-unfold test: 1.9414 (`…/period-unfold-20261014/outputs/sacct_charges.txt:42`).
  - Ledgers live per stage, in each stage REPORT and in sacct files.
- Most recent allocation balance (iris, 2026-10-14T07:28:47Z, `O/state/2d-closeout/stageD-inputs/evidence/remote_reads_20261014.txt:3-6`):

  | project | charged | allocated | remaining (all users) | josephrb |
  |---|---:|---:|---:|---|
  | m3246 CPU | 17,193.7 | 20,000 | 2,806.3 | 2,043.0 of 10,000 |
  | m3246_g GPU | 129,162.8 | 180,000 | — | 1,295.8 of 90,000 |

  This reading is restated in Stage D REPORT:79 as "context only, not a ceiling".
- Earlier readings: 16,980.6 on 10-11 (`sb1-run/evidence/scheduler/iris-post-run.txt`) and 16,817.7 on 10-04.
- s5p spend: DELIVERY-20261006:97-107 (253.192 of 341.434 pool; GPU 12.182 of 125 node-h).
- No record later than 2026-10-14 was found (`git grep iris` filtered to dates 10-15..10-19). Re-measure before use.

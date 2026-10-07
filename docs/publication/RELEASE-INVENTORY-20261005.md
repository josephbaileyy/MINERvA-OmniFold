# Release inventory for the publication decision (2026-10-05)

**CITABLE FOR:** what exists today toward an external release of each candidate route, where it lives, its
identity, its access class, and the gaps.
**NOT CITABLE FOR:** a release, a deposit, a tag or a reproducibility claim. Nothing here was uploaded, tagged
or sent. Those acts are not authorized (the user instruction of 2026-10-05; `AUTHORIZATION-20260926-…` row 164).

**Baseline:** `origin/main` `61cad10d`. The PLAN §6 components are the rows. The existing release appendix
(`docs/analysis-note/app_release.tex`) and the assembled-but-unshipped package
(`docs/analysis-note/release-package-20260922/`) are the starting inventory, not evidence of a current release.

## 1. Two different result families need two different releases

| family | estimator | grid | what it supports | existing package |
|---|---|---|---|---|
| **Measurement / central-value** (current Letter) | production F1, with scikit-learn and LightGBM ensembles not estimator-matched (claims table, L4) | 10,694 reported 5D cells; 42-cell (E_avail,W) projection | the 2D reproduction; the 3D–5D central values; the adopted covariance under exception | `release-package-20260922/` (in repo, **NOT SHIPPED**) |
| **Joint inference** (proposed headline) | candidate **R**, 5 iterations | 109 supported J cells (3^5 coarse grid; GiBUU 72) | the 10 tests | **none**: no inference release exists |

A p-value from the R procedure cannot be attached to the F1 map (PLAN §4). Each family's release carries its own
estimator identity.

## 2. Inventory against the PLAN §6 components

| component | exists now | identity | location | access class | gap |
|---|---|---|---|---|---|
| **Numerical results**, measurement family | 5D central values, masks, M, the (E_avail,W) covariance | sha256 `6773530647f66103…`, `2c02f47f13448a61…`, `3b81f42bdc75613f…`, `94679d6dcdf1ff25…` (package README §3); trunk `3d7465f6…`, projection `835828bf…` | repository (package); trunk on `/pscratch` | releasable (derived) | `acceptance_question: UNDECLARED` is carried verbatim (package §2). Masks ship as float64 and need `.astype(bool)` (package §3). |
| **Numerical results**, inference family | data product on J cells; the five predictions and Var(μ_G); domain masks; cell order (`names`, 109) | data `runs/s2/num/data/data_b-_j-.npz` sha256 `fb5cc679…`, a **lane-pinned** digest (`reproduction/s5p/pins/unrecorded-inputs-20260928.json`; the design records a path only); predictions by path in `state/s5p/prod/design.json` | `/pscratch/sd/j/josephrb/s5p-20260926/` | releasable (derived) | **The design pins no sha256 for `data_central`.** A release must bind it and re-verify it against the lane pin. |
| **Inference definition** | contract and amendments 1–8; frozen design; V; shift and M1 files; evaluator code | design `404446eb…`; V `35979ef7…`; D16 and M1 digests in the design; `s5p_joint.py`, `s5p_inference.py` and `s5p_seqstop.py` byte-identical to `4f5a613f` | repo plus `/pscratch` (V, D16, M1) | releasable | V is a power-setting metric, not a measurement covariance. The release must say so (PLAN §6). |
| **Calibration and resolution** | 5 × (1343–1751) calibration products; 6 power sets; observed statistics; frozen outputs; seed states | outputs `b9604502…`, `206655f9…`, `6823e701…`, `f48e16ef…` (terminal record §2) | outputs: repo copies (`state/s5p/stage7/joint/`) plus cluster; products ~185 kB each, ~1.3–2.1 GB in total (amendment 7 `storage`) | releasable (derived) | Replaying p-values needs **either** the per-draw T arrays per variant **or** the products. No per-draw T table is committed today. The recovery products, when they exist, must be released **separately labelled** as report-only (`DECISION-20261005` §2). |
| **Provenance** | the s5p reproduction harness, tiers A/B: 0 failures, 7 declared differences, tier D `PENDING` | `reproduction/s5p/reports/fresh-6f080601/report.md` (exit 0) | repo; runs on Perlmutter | internal tooling | Tier D (the joint result) is a declared slot to fill after the record. The harness assumes Perlmutter roots and a ROOT 6.28 environment. |
| **Reproduction**, external reader | none for the inference; for the measurement family, one worked projection example (package §5) | — | — | — | A standalone replay from released sufficient products to every main table and figure, with no `/pscratch` paths and no internal covariance file (PLAN §6), **does not exist**. Estimated 2–4 working days (PLAN §11), local packaging, no cluster compute. |
| **Raw inputs** | MINERvA ME-FHC OpenData AnaTuples, 12 playlists | download route `2d-unfolding/download_playlist.sh` (`root://fndca1.fnal.gov:1095/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC`); integrity receipts `docs/orchestration/state/opendata-input-integrity-*.json` | public source; analysed copies on `/pscratch` and tape | **public (CC0)**, see §3 | **The analysed copies are a valid OLDER production, smaller than the current OpenData files of the same name; the current files are 1.243–1.244× their size, so the copies are about 20% smaller** (`docs/OPEN_ITEMS.md` OI-55, whose wording reads "~24% smaller"). A fresh download therefore does not reproduce the inputs. The release must state which production was used and preserve its identities. |
| **Generator truth samples** | GENIE 2.12.10 CV and MEC, NuWro 21.09, GiBUU 2019 (flux-repaired), MnvTune v1 | `gen5d*/…xsec5d*.npz` by path in the design; the harness pins digests | `/pscratch` | produced by this analysis; releasable at the 5D-histogram level | Event-level samples are large. State whether only the 5D histograms are released. GiBUU lacks E_ν > 20 GeV (`KNOWN_ISSUES` 82). |

## 3. Access boundaries, measured 2026-10-05

- **The data are public.** The MINERvA open-data page (https://minerva.fnal.gov/opendata/, fetched 2026-10-05)
  says the release is "released under the CC0 license". It says "We do not require MINERvA review of non-MINERvA
  manuscripts". It asks users to cite DOI **10.15484/3022562** and the MINERvA NIM paper, Nucl. Instrum. Meth. A743
  (2014) 130, and suggests the acknowledgment "The authors thank the MINERvA Collaboration for making their data,
  simulated data, and analysis tools available to the community." These are WebFetch summaries of that page.
  Re-read the page before quoting it in the manuscript.
- **The release appendix contradicts this.** `app_release.tex:32–35` says each E_avail, q3 and W result "requires
  collaboration-internal MINERvA production AnaTuples". The analysis reads the **OpenData** path. What is
  non-public is (a) the exact older production analysed (OI-55), (b) the event-loop outputs and generator samples
  produced by this analysis, and (c) the products on `/pscratch`. All three are releasable by the authors, subject
  to the size choices above. **Correction owed:** the appendix sentence and the bibliography (the DOI is absent from
  `technote.bib`).
- **Reproduction levels must be named separately.** There are three: public sufficient-product replay (to be
  built), internal Perlmutter replay (the harness, tiers A/B), and end-to-end event processing (harness tier C,
  `NOT_RUN`). The release must not call the public package end-to-end reproducible (PLAN §6).

## 4. Release acts that remain reserved

The release tag, the public deposit (for example Zenodo or HEPData), any upload of the package, and the
Data-Availability wording that names a deposit. Each needs Joseph's separate authorization after the package
passes an independent empty-checkout replay (PLAN §6 exit gate, §9).

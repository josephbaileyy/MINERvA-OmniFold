# CAMPAIGN s5c-20260924 — paper-wide completion table (plan §10), Phase-A initialization

**CITABLE FOR:** the campaign's initial inventory of retained claims and reporting products in the
note, primer and paper, each with its evidence route, open dependency and a proposed closure
criterion. **NOT CITABLE FOR:** any readiness verdict, grade or adoption; it is a working table that
the campaign reconciles against all three deliverables before closeout (plan §10).

**Provenance.** Produced 2026-09-25 by one read-only research agent commissioned by the campaign,
from worktree `MINERvA-OmniFold-campaign-scalar5d` at `HEAD = 6abfb5f4` (before the activation
commit `81c62d15`); committed unedited below this header except for the four-field summary, which
the campaign restated. **Single reader: the rows are not independently verified.** Its statements
that the plan is "PROPOSED" predate the activation and are superseded by
[`AUTHORIZATION-20260924-scalar5d-campaign-activation.md`](AUTHORIZATION-20260924-scalar5d-campaign-activation.md).
Reader findings that would change a deliverable (e.g. R10's comparator label, R14's attribution of
M1, R21's nine consistency defects) are leads for the campaign's delivery phase, not settled facts.

Citations use `file:line` at the sha above. Abbreviations: **N** = analysis note (`main_note.tex` plus its
`sec_*`/`app_*` inputs), **Pr** = primer (`primer_body.tex`), **Pa** = paper (`main_paper.tex` plus
`paper_body.tex`). All tex paths are under `docs/analysis-note/`.

Readiness values: `READY` / `OPEN` / `BLOCKED-EXTERNAL` / `EXCLUDED-BY-RECORDED-SCOPE`. I applied
READY conservatively: it needs committed evidence, an independent check, **and** no open dependency.
A tested reproduction or package gap alone keeps a row OPEN, because plan §10 (line 616) requires
every retained figure/table to link to operands, checksums and a tested reproduction.

---

## 0. Summary of rows

| # | Row (claim / product) | Readiness | One-line reason |
|---|---|---|---|
| R1 | 2D central-value reproduction | OPEN | Validated scientifically. Its operands sit untracked on purgeable scratch (`values.tex:31-33`), `OI-130` is open, and the release package holds no 2D object. |
| R2 | 2D standalone uncertainty (6.87 % median) | OPEN | Validated construction. There is no receipt comment in `values.tex:97`, no package entry, and no tested reproduction. |
| R3 | 2D comparison to MINERvA Tune v1 and the shared-data residual (Pa Fig. 1) | OPEN | The chi² is VERIFIED-NUMERIC, but the committed figure PDFs have no digest and no recorded producing run. |
| R4 | 3D central value, 2D anchor, injected-E_avail closure | OPEN | Validated. Two E_avail-definition dependencies remain open (the 135 MeV constant at `OI-30`, the 1.17 scale at `OI-31`), and there is no package or reproduction. |
| R5 | 3D generator comparison and low-recoil/2p2h/FSI interpretation (CV level) | OPEN | Prediction files are not in the repo or package and have no digests. The GENIE configuration is described two ways (N `sec_3d.tex:195-197` against `:336-341`). |
| R6 | 3D `(p_T,p_∥,E_avail)` covariance projected from the trunk (`20c16e16…`) | OPEN | Constructed, not adopted. The `declared-dst-cv` variant was never made, and there is no ledger row. |
| R7 | 4D central value, 3D anchor, closure | OPEN | Validated. There is no corrected 4D covariance (`sec_3d.tex:512-518`) and no package. |
| R8 | 4D `(E_avail,q3)` comparison to Ascencio (CV level, "within 10 %") | OPEN | CV only. The note figure prints a superseded-covariance chi², no trunk projection to `(E_avail,q3)` exists, and the Ascencio file digest is not in the ledger. |
| R9 | 5D central value, 4D anchor, injected-W closure | OPEN | Validated, and in the package. Per-object provenance is not carried, and the seed moves single 5D bins by up to 49.8 % of σ (M4). |
| R10 | Joint `(E_avail,W)` localization map (Pa Fig. 2, Pr Fig., N Fig. `excess_eavail_W`) | OPEN | Its "GENIE" comparator is built from `w_truth`, documented as the Tune v1 weight. The response-mismatch closure has not run, and the hadronic question is unsent. |
| R11 | Four-generator `(E_avail,W)` band and 1D E_avail/W projections (Pa Fig. 3) | OPEN | The corner ratios are verified (`VL35`–`VL38`). The predictions are absent from the package with no digests, and the GENIE-CV total differs between 3D and 5D. |
| R12 | Adopted scalar-5D covariance `C_Z` `3d7465f6…` | OPEN | Adopted under exception. Cause 3 is not discharged and M1 fails the bound. Endpoint receipts are superseded by code drift, and `C_Z` is not in the package. |
| R13 | `(E_avail,W)` projected covariance `C_EW` `835828bf…` | OPEN | VERIFIED (`VL143`, `VL145`). `acceptance_question: UNDECLARED`, and N `app_release` contradicts N `sec_eavailw` on the λ_min sign. |
| R14 | Estimator-seed statement (M1–M4) as written in Pa/Pr/N | OPEN | Measured on two other products (`361090f9…`/`7e4636a3…`); only the note says so. The note also writes "42 destinations" where the record says 43 functionals. |
| R15 | Hadronic-response scope statement (PM-1) | BLOCKED-EXTERNAL | The required collaborator question is PREPARED, NOT SENT. Sending it is outward-facing and the answer is external. |
| R16 | Joint-5D generator inference | OPEN | Not attempted. No frozen map or statistic exists. `OI-187`: an upgrade, not a submission blocker, but the dependency is kept by choice, and no exclusion is recorded. |
| R17 | Projection/contrast inference (`(E_avail,W)`, corner, 3D/4D, Ascencio) | OPEN | None computed. Blocked by M1 and by the lack of any declared regularization. The inference contract (`README.md` §1) is unwritten. |
| R18a | PET as a measurement or uncertainty product | EXCLUDED-BY-RECORDED-SCOPE | Joseph's ruling of 2026-08-20 (`OI-126`), and `KNOWN_ISSUES` row 19 closed by ruling 2026-09-23. |
| R18b | PET mention in Pa/Pr (method development, limitation only) | READY | The wording matches the ruling in all three deliverables and has no dependency. (Checked by this reader only.) |
| R18c | PET section content in N (`sec_pet.tex`) | OPEN | `OI-125` and `OI-93` are live publication items in `CURRENT_WORK`. |
| R19 | Preliminary extended-fiducial (FPS) central value | OPEN | No corrected covariance (`sec_fps.tex:6-8`). The `OI-2` scalar-FPS component is still required and UNOWNED, yet the primer quotes the number. |
| R20 | Reproduction and release package | OPEN | Not shipped; no tag or manifest. It lacks generator predictions, per-object provenance and `C_Z`, the builder cannot run from its committed path, and the figures carry no digests. |
| R21 | Note/primer/paper consistency, builds, sync | OPEN | Nine consistency defects are listed in R21. Sources equal the standalone HEAD, but the remote heads and the Overleaf `output` build are not verified. |

**Four fields (plan §10), as initialized 2026-09-25** (campaign restatement; the live values are in
`state/s5c/campaign-state.json` and the final report):
- `campaign_disposition`: **IN PROGRESS** — activated 2026-09-24; Phase A complete but for this table's reconciliation; Phase B pilots running.
- `reportable_uncertainty_scope`: unchanged from before the campaign — the **2D** standalone covariance (validated); the **`(E_avail,W)` 42-cell** `C_EW` (`835828bf…`) published under exception with M1–M4 travelling and nothing inferential; no reportable 3D, 4D or 1D-projection uncertainty.
- `joint_5d_inference_status`: **NOT PERFORMED.**
- `publication_readiness`: **OPEN** (rows R1–R21 other than R18a/R18b).

**Closeout reconciliation 2026-09-25 (campaign).** Rows whose state changed; all others are unchanged:
- **R9:** the injected-W closure stands. It is signal-only, and the background-inclusive closure is biased (≤ 4%, highest-W; `VL149`). The paper and note now say so. It stays OPEN.
- **R12/R13:** the purity-background bias (0.36–1.07 of `C_EW`'s quoted σ) is recorded against them (`KNOWN_ISSUES.md` 75), and no coverage is claimed. Both stay OPEN.
- **R16/R17:** joint-5D and projection inference NOT PERFORMED, infeasible within the envelope (feasibility §4). They stay OPEN, and the costed increments are in the index closeout.
- **R21:** tracked sources equal the standalone repository at `7739089b`, and all three documents build. The Overleaf `output` is not verified. It stays OPEN.

**Final four fields:** see [`CAMPAIGN-s5c-20260924-index.md`](CAMPAIGN-s5c-20260924-index.md) §Closeout: CONCLUDED, objective NOT MET / scope unchanged in kind plus the bias caveat / joint-5D NOT PERFORMED / **NOT READY**.

---

## 1. Rows

Fields per row: **Claim** · **Where** · **Required uncertainty/inference scope** · **Digests (tex/ledger)** ·
**Adoption/ruling** · **Independent verification** · **Reproduction/package** · **Owner** ·
**Unresolved dependency (governing record)** · **Closure criterion (executable)** · **Readiness**.

### R1 — 2D central-value reproduction
- **Claim:** The five-iteration OmniFold 2D total is 3.073e-38 cm²/nucleon against the published 3.039e-38 (ratio 1.011). 94.1 % of the 205 bins agree within 10 %, and the pull RMS is 0.598 with published σ. The paper presents this as validation of the estimator, not as an independent comparison.
- **Where:** Pa `paper_body.tex:51-62`, `main_paper.tex:41-43`; Pr `primer_body.tex:109-119`; N `sec_execsummary.tex:31`, `sec_results.tex:14-136`.
- **Scope:** Shared-data validation. No combined-covariance statistic may be quoted (Pa `:61-62`, AGENTS 2D row).
- **Digests:** ours `2d_crossSection_omnifold_MEFHC_5iter.root` sha256 `142a45b0…7fd5`; paper ancillary `cov_ptpl_minerva_inclusive_6GeV.root` `6c6dce72…73e3` (`values.tex:22-25`). Receipt: `docs/orchestration/receipts/RECEIPT-2d-agreement-windows-20260821.json`. Neither digest appears in `VALIDATION_LEDGER.md`. The ledger's "Active 2D Result" is at `:1585-1600`.
- **Adoption/ruling:** AGENTS "2D central value … VALIDATED". There is no DECISION record specific to it.
- **Independent verification:** Ledger `:1587-1588` (paper chi² 3.661 recomputed, PASS). The agreement-window producer "reproduce[s] the previously unattested values exactly", but it is "not shown to be the method that ORIGINALLY produced" them (`values.tex:58-63`).
- **Reproduction/package:** N `app_release.tex:26-30` claims the comparison is recomputable from public inputs. But the OmniFold output itself is on purgeable scratch and untracked (`values.tex:31-33`). The package (`release-package-20260922/README.md:71-77`) holds no 2D object.
- **Owner:** not stated. `OI-130` is routed to lane D (`docs/CURRENT_WORK.md:17`).
- **Dependency:** `OI-130` (quoted values to artifacts; OPEN, `docs/OPEN_ITEMS.md:207`).
- **Closure criterion:** (1) a tracked or preserved copy of `2d_crossSection_omnifold_MEFHC_5iter.root` whose `sha256sum` equals `142a45b0…`; (2) that file added to the package manifest with its digest; (3) `agreement_windows_receipt.py`, run from a fresh checkout on the packaged operands, reproduces 1.0113 / 193/205.
- **Readiness:** **OPEN.** Packaging and durability only; the science is validated.

### R2 — 2D standalone uncertainty
- **Claim:** A matched-CV systematic plus statistical plus training-seed covariance gives a 6.87 % median relative uncertainty, against 6.86 % published. The central value (exact sklearn GBDT) and the covariance ensembles (LightGBM) are "not estimator-matched".
- **Where:** Pa `paper_body.tex:42-46,56-59,74-77`; Pr `:116-119`; N `sec_systematics.tex` (whole), `sec_results.tex:138-166`.
- **Scope:** Reported budget only. The 2D coverage test is open (N `sec_validation.tex:57-67`) and is **not** claimed.
- **Digests:** none cited in tex. Value source: `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:56`; covariance files `uq_universe_covariance_full_matcorr_fluxfix.root:hCov_combined` + `uq_covariance_ml.root` (ledger `:1589-1592`), with no sha.
- **Adoption/ruling:** AGENTS "2D standalone uncertainty construction VALIDATED". `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md` relies on that grade.
- **Independent verification:** combined-covariance checks PASS (ledger `:1589-1595`). I found no receipt of an independent recomputation of the 6.87 % median.
- **Reproduction/package:** not packaged; covariance ROOT files not digested.
- **Owner:** not stated.
- **Dependency:** `OI-130` (class: quoted macro with no bound artifact).
- **Closure criterion:** a receipt JSON recording the sha256 of each covariance input, plus a script that recomputes `median(sqrt(diag C)/x) = 6.87 %` from them; the numbers are then added to the package.
- **Readiness:** **OPEN.**

### R3 — 2D comparison to MINERvA Tune v1; shared-data residual (Pa Fig. 1)
- **Claim:** The overlay of published, OmniFold and Tune v1 in 1D projections, plus the (OmniFold − published)/σ_pub map, is a descriptive residual, not an independent pull.
- **Where:** Pa `paper_body.tex:64-91`; N `sec_results.tex:209-251` (with chi² values).
- **Scope:** The paper quotes no model chi². The note quotes data-vs-tune 33.039 and ours-vs-tune 26.491 (ledger `:1596-1599`).
- **Digests:** Tune v1 ancillary sha256 `22231752…8240` in `2d-unfolding/receipt_model_chi2_2d.json` (not in the ledger). Figure PDFs: **no digest anywhere** (figure agent; `check_dead_containment.py`/`test_build_all.py` hash only the built PDFs).
- **Adoption/ruling:** none needed (descriptive).
- **Independent verification:** ledger `:661` "2D vs GENIE MINERvA Tune v1 chi2/ndf — VERIFIED-NUMERIC".
- **Reproduction/package:** the producers are committed (§3). The committed PDFs have no recorded producing run, commit or job, and the producers hardcode `/pscratch`.
- **Dependency:** plan §10 package requirement; `OI-130`.
- **Closure criterion:** a figure manifest giving, per PDF, its sha256, producer path@sha, input digests and job id; then one regeneration on a fresh checkout that byte-compares or tolerance-compares the plotted arrays.
- **Readiness:** **OPEN.**

### R4 — 3D central value, anchor and closure
- **Claim:** The E_avail-marginal of the 3D result matches the 2D total to +0.95 % (median ratio 1.0016). A +30 % Gaussian injected at E_avail = 0.3 GeV is recovered: mean weight 1.048 against 1.0485, marginal residual σ 0.06 %. The shape χ²/ndf of 4.98 is not calibrated.
- **Where:** Pa `paper_body.tex:93-97`; N `sec_3d.tex:124-181`, `sec_validation.tex:24-27`.
- **Scope:** Central-value validation only. One injected shape; no suite; no response mismatch (N `sec_3d.tex:166-181`).
- **Digests:** none in tex. Status `3d-unfolding/3D_OMNIFOLD_STATUS.md:63`; ledger `:1621-1623` (bottom-line 3D PASS).
- **Adoption/ruling:** AGENTS 3D central row VALIDATED.
- **Independent verification:** ledger bottom-line test PASS. I found no separate third-lane record.
- **Reproduction/package:** `xsec_3d_MEFHC_5iter_lgbm.root` is not packaged. N `app_release.tex:32-37` declares every E_avail/q3/W result not recomputable from public inputs, which is a declared access restriction.
- **Dependency:** (a) the charged-pion 135 MeV constant, where "materiality against the adopted projection is still not established" (N `sec_3d.tex:88-94`; `OI-30`, owner Joseph + Gregor, `OPEN_ITEMS.md:150`). (b) The 1.17 reconstructed-E_avail scale: `KNOWN_ISSUES` row 26 is RESOLVED-quantified, but a per-bin band is "PROPOSED, not adopted … Joseph's decision, carried at OI-31" (`OI-31` WAITING-USER).
- **Closure criterion:** Joseph's recorded disposition of `OI-30` and `OI-31` (adopt or decline the band), with the note text updated to match; the 3D central file digest recorded in the package manifest.
- **Readiness:** **OPEN.**

### R5 — 3D generator comparison and low-recoil / 2p2h / FSI interpretation
- **Claim:** At low E_avail, all four predictions fall below the data: GENIE CV, Tune v1, NuWro 21.09 and GiBUU 2019. Pion-FSI dials move dσ/dE_avail by less than 1 %. Valencia 2p2h fills 46 % of the dip gap and 27 % of the integrated deficit. All of this is at central-value level.
- **Where:** Pa `paper_body.tex:99-107`; Pr `:139-151`; N `sec_execsummary.tex:37-40`, `sec_3d.tex:183-269,305-420`.
- **Scope:** CV only; no 3D chi² (N `sec_3d.tex:246-254`). N Figs. `3dmodels`, `modedecomp`, `mec` and `3dfullcov` draw the **superseded** historical 3D covariance, and their captions say so (`:236-242,402-405,414-417,259-267`).
- **Digests:** none for any prediction file (generator agent; ledger has none).
- **Adoption/ruling:** none. The historical covariance is QUARANTINED (AGENTS).
- **Independent verification:** ledger `:1604-1608` reproduces the historical scan as DIAGNOSTIC ONLY. I found no independent check of the 46 %/27 % figures.
- **Reproduction/package:** prediction ROOT files are on `/pscratch` only. They are **not** in release schema item 7, which covers the `(E_avail,W)` predictions only (N `app_release.tex:68-72`).
- **Dependency:** (a) **Configuration description conflict:** N `sec_3d.tex:195-197` ("GENIE 2.12.10 central value … DefaultPlusValenciaMEC configuration") against `:336-341` (base CV "default event-generator list … mec=0"). This is probably spline-set against event-list wording, but it is unconfirmed. (b) Pa `:100-101` names Tune v1 in the low-E_avail claim, yet no paper figure plots Tune v1 in E_avail. (c) R4's `OI-30`/`OI-31`.
- **Closure criterion:** the generator/version/config/target/flux table in the package with sha256 of every prediction array; a one-line wording fix in N `sec_3d.tex:197`, confirmed by the owner; the Pa `:100` claim either cited to the note figure or narrowed to the plotted set.
- **Readiness:** **OPEN.**

### R6 — 3D `(p_T,p_∥,E_avail)` covariance projected from the adopted trunk
- **Claim (N only):** The projection exists (`20c16e16…`, 1431 cells) but is "constructed, not adopted", and it exists only in the receiving-cells mask. So no 3D covariance-dependent comparison is made.
- **Where:** N `sec_3d.tex:240-242,263-267,284-292`. Not in Pa or Pr.
- **Scope:** Would supply the 3D reportable uncertainty (plan §10, line 612).
- **Digests:** `20c16e16a35a837b…1f69e`, 15,937,290 B; row index `856469c4…`; M `6147e154…` (`OUTCOME-20260922-3d-covariance-projected-from-the-adopted-trunk.md:11,39-40`). **None of them is in `VALIDATION_LEDGER.md`.**
- **Adoption/ruling:** **not adopted.** Adoption is reserved to Joseph (OUTCOME §5, `:78-80`).
- **Independent verification:** reviews #11a and others re-solved the spectrum (OUTCOME §2, `:36`). No ledger row exists.
- **Reproduction/package:** the receipt is `state/PROJ3D-20260922-ptpzeavail-from-adopted-trunk-receipt.json`. The product is not in the package, and `acceptance_question: UNDECLARED` (OUTCOME `:42`).
- **Owner:** Joseph (adoption).
- **Dependency:** the `declared-dst-cv` variant bound to `xsec_3d_MEFHC_5iter_lgbm.root` was "not made" (OUTCOME §4, `:70-74`). The adoption decision is also absent.
- **Closure criterion:** a Joseph DECISION record adopting (or declining) a named 3D product digest; if adopted, a `declared-dst-cv` projection run with a receipt, a ledger row, and the four historical-band figures regenerated or withdrawn.
- **Readiness:** **OPEN.**

### R7 — 4D central value, anchor and closure
- **Claim:** The 4D/3D marginal integral ratio is 0.9960 (4D total 3.0665e-38), and the E_avail-marginal reproduces the 3D low-recoil shape.
- **Where:** Pa `paper_body.tex:93-97`; N `sec_3d.tex:422-449`.
- **Scope:** CV only. "No 4D uncertainty magnitude … is reported" (N `sec_3d.tex:512-518`).
- **Digests:** none. `nd-unfolding/ND_OMNIFOLD_STATUS.md:107` gives `products/4d/xsec_4d_MEFHC_5iter_lgbm.root`.
- **Adoption/ruling:** AGENTS 4D/5D central row VALIDATED.
- **Independent verification:** ledger `:1609-1611` (`check_4d_anchors.py` PASS).
- **Reproduction/package:** not packaged.
- **Dependency:** there is no reportable 4D uncertainty. None was projected from the trunk, and none is declared excluded. R4's `OI-30`/`OI-31` also apply.
- **Closure criterion:** either a recorded scope decision that 4D is CV-only (with Pa/Pr/N wording matching), or a trunk projection receipt plus a ledger row.
- **Readiness:** **OPEN.**

### R8 — 4D `(E_avail,q3)` comparison to Ascencio et al.
- **Claim:** On the maximal common grid, two super-cells come out 9.2 % and 6.3 % above Ascencio. Pa phrases this as "agrees to within 10 %".
- **Where:** Pa `paper_body.tex:108-111`; Pr `:150-151`; N `sec_3d.tex:465-497`, `sec_eavailw.tex:450-453`.
- **Scope:** CV only. The N figure `ascencio_fullcov_compare` prints a chi² from the **superseded** 4D covariance, disclosed at `sec_3d.tex:490-495`. Shared MINERvA systematics are "treated here as independent" (`:477-478`).
- **Digests:** the Ascencio supplemental `3d-unfolding/genie/ascencio_2110.13372_supplemental.txt` is in the repo. No ledger digest exists; the generator agent's local sha256 starts `748afa92…`.
- **Adoption/ruling:** none.
- **Independent verification:** ledger `:1612-1614` records that `compare_ascencio_q3.py` passes for our-side spectra only. I found no independent record of the 9.2 %/6.3 % values.
- **Reproduction/package:** not packaged.
- **Dependency:** no `(E_avail,q3)` projection of `C_Z` exists; the historical 4D product is quarantined.
- **Closure criterion:** a ledger row carrying the two super-cell ratios and the Ascencio file sha256; the note figure regenerated without the superseded chi², or the chi² removed from the asset.
- **Readiness:** **OPEN.**

### R9 — 5D central value, anchor and closure
- **Claim:** The 5D/4D total is 1.0011, with per-axis medians of 0.3–1.5 %. The injected-W closure passes, and dσ/dW is finite and non-negative.
- **Where:** Pa `paper_body.tex:93-97`; N `sec_eavailw.tex:18-36`.
- **Scope:** CV.
- **Digests:** `central_values_5d.npz` `6773530647f66103…`. The pairing digest of `hXSecND_flat` is `0f04abce…9baa` (`VALIDATION_LEDGER.md:52` VL143; `state/PROJ-20260920-binding-check.json:4`).
- **Adoption/ruling:** AGENTS VALIDATED.
- **Independent verification:** ledger `:1552`; `ND_OMNIFOLD_STATUS.md:108`. VL143 establishes by digest identity that the adopted trunk was built on the same bytes.
- **Reproduction/package:** in the package, but "per-object provenance … NOT CARRIED" (README `:98-102`). The pairing digest is reproducible but not shipped (`:103-107`).
- **Dependency:** (a) M4: per single 5D bin the seed moves the CV by up to 49.8 % of σ, median 3.77 % (DECISION-20260920 §4 M4). (b) The "5D control differs from the frozen 5D central by a median 0.58 %", which is unexplained (`KNOWN_ISSUES` row 26). (c) R4's `OI-30`/`OI-31`.
- **Closure criterion:** `_build_report.json` gains `producing_revision`, `producing_job` and the read-back digest per object; a disposition is recorded for the 0.58 % control residual.
- **Readiness:** **OPEN.**

### R10 — Joint `(E_avail,W)` localization (the headline central-value claim)
- **Claim:** The positive unfolded-minus-generator difference concentrates at high E_avail and high W. In the note, 67 % of positive excess sits at E_avail ≥ 0.8 GeV, and 83 % of that at W ≥ 1.8 GeV. No significance is assigned.
- **Where:** Pa `main_paper.tex:48-50`, `paper_body.tex:113-137`; Pr `:169-207`; N `sec_execsummary.tex:42-43`, `sec_eavailw.tex:38-90`.
- **Scope:** Central value under nominal response; descriptive localization. The region is data-selected (N `sec_eavailw.tex:208-210`). The shares are not seed-measured (`:57-58`).
- **Digests:** CV pairing `0f04abce…` (VL143). The figure PDF has no digest.
- **Adoption/ruling:** none needed for CV. `OI-187` (a): a significance on this is the claim upgrade.
- **Independent verification:** the CV pairing is verified. I found no independent recomputation of the shares (57/67/83/22 %).
- **Reproduction/package:** the `(E_avail,W)` marginal is in the package (`covariance_eavailW.npz:cv_marginal`). The **comparator array is not** (README `:112-114`).
- **Dependency:**
  - **(a) Comparator identity.** Pa Fig. 2 and Pr call the comparator "GENIE". But `nd-unfolding/excess_eavail_W.py:13-14,62-72` builds it from `mc_truth_denom` weighted by `w_truth`, and `3d-unfolding/genie/model_tune_xsec3d.py:5-9` documents `w_truth` as "the full MINERvA Tune v1 weight". The 4D analog is consistent with this: data/"GENIE-CV" = 1.13 at N `sec_3d.tex:448`, against 3.08/2.71 ≈ 1.137 for Tune v1. **This comparator is the OmniFold prior, and it is a different object from Fig. 3's gevgen GENIE-CV.** Owner confirmation is needed.
  - (b) Response-mismatch closure: "No response-mismatch artifact has been produced" (N `app_response_mismatch.tex:51-58`).
  - (c) R15.
  - (d) R4's `OI-30`/`OI-31`.
- **Closure criterion:** a code-cited statement of the comparator's weights, with every "GENIE" label for the Fig. 2 comparator in Pa/Pr/N corrected if (a) holds; the comparator array added to the package with its digest; the response-mismatch diagnostic run with a predeclared amplitude and threshold and a ledger row, **or** a recorded scope decision that the claim stands without it.
- **Readiness:** **OPEN.**

### R11 — Four-generator `(E_avail,W)` band and 1D E_avail/W projections (Pa Fig. 3)
- **Claim:** GENIE-CV, GENIE+MEC, NuWro and GiBUU all underpredict high W. In the corner, data/generator = 1.54 / 1.58 / 1.56 / 1.61, and 2p2h does not close it.
- **Where:** Pa `paper_body.tex:139-161`; Pr `:153-167`; N `sec_eavailw.tex:92-210`.
- **Scope:** CV ratios only. No chi² (N `:179-184`).
- **Digests:** ledger VL35–VL38 (`VALIDATION_LEDGER.md:485-536`) record the corner integrals, with the log `3d-unfolding/genie/eavailW_band_20260811_allfour.log`. **There is no sha256 for any prediction file.**
- **Adoption/ruling:** none. The normalization convention was ruled by Joseph on 2026-08-12 (N comment `sec_eavailw.tex:156-159`).
- **Independent verification:** VL35–VL38 VERIFIED-NUMERIC (predeclared at `PREDECLARE-20260811-gibuu-corner-ratio.md`).
- **Reproduction/package:** the predictions are "Not assembled here; that is packaging still owed" (README `:112-114`).
- **Dependency:** (a) GENIE-CV integrated σ is 2.52e-38 at N `sec_3d.tex:217` but 2.4446e-38 in VL35 (ledger `:499`). The 3D and 5D gevgen shards may differ, and their identity is UNKNOWN. (b) Pa and Pr state no generator versions.
- **Closure criterion:** the four arrays plus the Tune v1 ancillary shipped on the release binning, each with version, config, target, flux and sha256 (release schema item 7); a recorded reconciliation of 2.52e-38 against 2.4446e-38.
- **Readiness:** **OPEN.**

### R12 — Adopted scalar-5D covariance `C_Z`
- **Claim:** `z-cv.npz` (`3d7465f6…`, 890,500,272 B, variant `cv`) is adopted as publication-under-exception.
- **Where:** Pa `main_paper.tex:50-52`, `paper_body.tex:167-170`; Pr `:66-69`; N `sec_eavailw.tex:244-386`, `app_release.tex:94-99`.
- **Scope:** Reporting only. The product's own fields read `NON-PASSING` / `adoptable: false`. M1–M4 travel with it.
- **Digests:** `3d7465f66fbe66b0…918c5`, ledger VL142 (`VALIDATION_LEDGER.md:51`); `values.tex:328`.
- **Adoption/ruling:** `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:17-27`; `AMENDMENT-20260918-spec-6.4-…`; `CORRECTION-20260920-lower-bound-inference-withdrawn.md`; `CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md`.
- **Independent verification:** VL142, "independently re-hashed and re-diagonalized by a third lane" (`VERDICT-20260920-third-lane-c5-c7-verification.md`).
- **Reproduction/package:** not in the package (README `:109-111`; on `/pscratch` only). The ten endpoint receipts are **SUPERSEDED-BY-CODE-DRIFT** (`OUTCOME-20260922-ten-adopted-receipts-superseded-by-code-drift.md:11`), so there is no tested rebuild from the current tree.
- **Owner:** Joseph (adoption); scalar-5D lane (transcription).
- **Dependency:** cause 3 is not discharged: `M(i)` UNRESOLVED `4c`, `C3` "predeclared, not computed" for this digest (DECISION §2). M1 fails the 5 % bound. KNOWN_ISSUES row 16 is closed for this digest only.
- **Closure criterion:** either a Joseph record that publication proceeds with M1 unmet (a scope decision), or a new predeclared campaign whose `s_proj ≤ 5 %` on a product he adopts. In both cases a durable off-scratch copy is needed, with its `sha256sum` equal to `3d7465f6…`.
- **Readiness:** **OPEN.**

### R13 — `(E_avail,W)` projected covariance `C_EW`
- **Claim:** The 42-cell `M C_Z Mᵀ` is built and paired to the figure's CV by digest identity. No rank is quoted, and the matrix is not to be inverted without declared regularization.
- **Where:** Pa `paper_body.tex:168-170`; Pr `:67-68`; N `sec_eavailw.tex:308-367`, `app_release.tex:106-129,154-204`.
- **Digests:** `835828bf…a54e` (VL143, VL145; `values.tex:329`); M `64fec490…`; row index `9eb9d216…`; package copy `covariance_eavailW.npz` `94679d6d…`.
- **Adoption/ruling:** built under DECISION-20260920 §6's authorization.
- **Independent verification:** VL143 VERIFIED. VL145 is the first independent spectral scan (bitwise-identical to the diagnostic).
- **Reproduction/package:** shipped, with the worked example executed (README §5-6). A cross-host check agrees at float64 rounding.
- **Dependency:** (a) `acceptance_question: UNDECLARED` (`state/PROJ-20260920-m1-publication-receipt.json`; README §2). (b) **N internal contradiction:** `app_release.tex:109-110,183-185` says to check "λ_min is positive", while `sec_eavailw.tex:338-342` and README `:138,157-159` say the sign "carries no information". (c) `OI-129` is still listed NOW for the standard-P4 lane (`CURRENT_WORK.md:21`), although VL143 records a closed-file row-index read-back for this product. (d) No paper figure draws a band from it.
- **Closure criterion:** a recorded declaration of `acceptance_question` for this product; `app_release.tex` rewritten to drop the positivity check (`grep -n "is positive" app_release.tex` returns 0); `OI-129` dispositioned for this product.
- **Readiness:** **OPEN.**

### R14 — Estimator-seed statement (M1–M4) as written
- **Claim:** s_proj = 6.145 % against a 5 % bound. It does not fall across N = 40/80/160 (nested subsets, one seed pair). Five pinned bands carry 26.0 % of √Tr and are unprobed in either direction. The CV moves by at most 6.02 % of σ.
- **Where:** Pa `paper_body.tex:171-195`; Pr `:73-94,179-181`; N `sec_eavailw.tex:380-448`; README `:21-59`.
- **Digests/evidence:** `state/GRADE-20260920-cause3-two-member.json` (tracked); `values.tex:333-382`.
- **Adoption/ruling:** DECISION-20260920 §4 ("measurements, not caveats"); the two CORRECTION records.
- **Independent verification:** the third-lane verdict (P1 finding). The L2 control reproduces 6.145388 % exactly (`OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md:17-28`).
- **Dependency / defects:**
  - (a) M1 was graded on `361090f9…`/`7e4636a3…`, **not on the adopted bytes** (DECISION §2 and §4 M1). N says so (`sec_eavailw.tex:443-447`). Pa `:172-174` and Pr `:73-77` attribute it to the adopted covariance without that qualifier.
  - (b) N `sec_eavailw.tex:52-53,433` says "on these 42 destinations", but M4 is measured "on the 43 M1 projection functionals" (DECISION `:98`; `values.tex:379`).
  - (c) The L2 released-lateral value (6.189 %) comes from a pair that "FAILS the grader's own comparability precondition"; it is not citable as a discharge.
- **Closure criterion:** the Pa/Pr wording carries the "measured on the two-member campaign products" qualifier; N states 43 functionals; the withdrawal checker (`state/check-withdrawal-completeness-20260910.py`) returns 0 discrepancies.
- **Readiness:** **OPEN.**

### R15 — Hadronic-response scope statement
- **Claim:** Five kinematic bands are rebuilt selection-complete. MINOS efficiency and the three GEANT bands remain weight-based. This "does not independently validate the completeness of the hadronic-response model".
- **Where:** Pa `paper_body.tex:197-202`; Pr `:96-104`; N `sec_eavailw.tex:237-242`.
- **Adoption/ruling:** `DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md` (PM-1 accepted with a provenance limitation).
- **Dependency:** `QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md:8-9`, "PREPARED, NOT SENT". The ruling §5 requires the question. Silence "does not reopen PM-1" (`:61-62`).
- **Closure criterion:** a committed record that the question was sent (date, recipient); when an answer arrives, an OUTCOME record per `QUESTION §4`.
- **Readiness:** **BLOCKED-EXTERNAL.** Sending is outward-facing (Joseph), and the answer is external. The deliverable wording already matches the ruling.

### R16 — Joint-5D generator inference
- **Claim in deliverables:** none. Pa `:167-171` says every non-2D result is a CV and quotes no significance.
- **Required scope:** plan §10 line 614 requires a frozen joint map or statistic, hypotheses, selection treatment, calibration, power and multiplicity.
- **Evidence:** none exists. The plan is PROPOSED (plan:5-7).
- **Adoption/ruling:** `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md` holds that (a) the covariance gates a claim upgrade, not submission, and (b) "the dependency is retained by choice". **That is not an exclusion.**
- **Owner:** Joseph (plan approval / scope).
- **Closure criterion:** either an executed approval of the plan plus a frozen-statistic record and a calibration receipt, or a Joseph scope record that excludes joint-5D inference from this publication, with Pa/Pr/N already free of dependent claims (they appear to be).
- **Readiness:** **OPEN.**

### R17 — Projection and contrast inference
- **Claim in deliverables:** none. Every comparison is marked "No significance is assigned" (Pa `:135,159`; N `sec_eavailw.tex:179-184`, `sec_3d.tex:252-254`).
- **Blocking evidence:** M1 (R14). No declared regularization exists for `C_EW` (N `sec_eavailw.tex:350-354`; `app_release.tex:192-196`). The data-selected corner is at `sec_eavailw.tex:208-210`. The inference-contract items in `docs/analysis-note/README.md:31-45` are not recorded as done.
- **Closure criterion:** a predeclared inference contract (statistic, mask, regularization, generator set, multiplicity) committed **before** any significance is computed; then a calibrated result with power, or a recorded scope exclusion.
- **Readiness:** **OPEN.**

### R18 — PET / point-cloud material
- **R18a, PET as a measurement or uncertainty product:** **EXCLUDED-BY-RECORDED-SCOPE.** The authority is Joseph's ruling of 2026-08-20 (`OI-126`, `docs/OPEN_ITEMS.md`; AGENTS "PET is diagnostic"), with `KNOWN_ISSUES` row 19 "CLOSED 2026-09-23 by ruling". Gate 6 is BLOCKED by receipt keys (N `sec_pet.tex:452-456`).
- **R18b, Pa/Pr mention:** Pa `paper_body.tex:206-210` and Pr `:213-219` say method development only, with pairing declined, coverage not demonstrated, and no uncertainty product adopted. This matches N `sec_pet.tex:4-13,444-458`. **READY:** limitation text only, no dependency. Verified by this read-only pass, not by a recorded reviewer.
- **R18c, N `sec_pet.tex` numeric content:** **OPEN.** `OI-125` (PET lane, publication/P1) and `OI-93` (lane B, publication/P2) are NOW in `docs/CURRENT_WORK.md:15-16`. The 2026-09-23 re-run changed every `projection_*` value (ledger `:3-23`).

### R19 — Preliminary extended-fiducial (FPS) study
- **Claim:** σ_ext = 4.502e-38 cm²/nucleon. About 6 % of the rate is tier-1 acceptance-supported and about 28 % is tier-2 prior-dominated. No corrected covariance exists.
- **Where:** Pa `paper_body.tex:204-206` (no number); Pr `:221-242` (number); N `sec_fps.tex:1-148`, `sec_execsummary.tex:62-63`.
- **Digests:** ledger `:1403,:1530` (Delta passes); the omnifile size is in `AUDIT-FINDINGS-20260820-fps.md:180-186`. No sha.
- **Dependency:** `OI-2` "scalar-FPS STILL OPEN … compatible scalar-FPS joint-throw component is still required", UNOWNED (`OPEN_ITEMS.md:122`).
- **Closure criterion:** either a recorded scope decision that FPS is a CV-only preliminary study in all three deliverables, or the `OI-2` component delivered with a ledger row.
- **Readiness:** **OPEN.**

### R20 — Reproduction and release package
- **State:** "NOT SHIPPED"; "no release tag and no release manifest" (README `:1-11`; N `app_release.tex:12-21`). Upload is reserved to Joseph.
- **Present:** `central_values_5d.npz` `67735306…`, `masks_5d.npz` `2c02f47f…`, `projection_matrix_M_eavailW.npz` `3b81f42b…`, `covariance_eavailW.npz` `94679d6d…` (README `:71-77`). None of these four is in the ledger.
- **Missing** (README §4, `:96-116`): per-object provenance (schema item 8); generator predictions (item 7); CVs for every quoted projection (item 3); `C_Z` itself; the pairing digest; all 2D/3D/4D/FPS objects; figure digests.
- **Defects:**
  - The builder `probes/probe-20260922-build-appendix-f-package.py` "is not runnable from its committed location" (README `:17`).
  - N `app_release.tex:73-75` ticks item 7/8 provenance as ✓ "already fixed", while README `:98-102` says it is not carried.
  - N `app_release.tex:183-185` contains the λ_min sign check (R13).
  - `masks_5d.npz` ships as float64 (README `:74`).
- **Closure criterion:** a manifest listing every retained figure and table with operand digests; a build script runnable from a fresh clone with no private paths (`grep -rn /pscratch` on the package returns 0); an executed reproduction on a fresh checkout reproducing each retained number within a stated tolerance; `acceptance_question` resolved or promotion withheld.
- **Readiness:** **OPEN.**

### R21 — Note, primer and paper consistency; builds; sync
**Consistency defects found in this pass (each needs an owner fix or a recorded disposition):**
1. The comparator for the Fig. 2 / `excess_eavail_W` map is labelled "GENIE (CV)", but the code weights it with `w_truth`, the Tune v1 weight (R10a). This affects Pa `:115,123-135`, Pr `:189`, and N `sec_eavailw.tex:41,67`.
2. The GENIE description varies: Pa `:35` says "GENIE 2.12.6 and the MINERvA Tune v1" (the analysis MC), while N `sec_3d.tex:195` says gevgen "2.12.10 … DefaultPlusValenciaMEC", against `:336-341` "mec=0". Pa and Pr give no version for the predictions in Figs. 2 and 3.
3. N `app_release.tex:109-110,183-185` (λ_min positive) contradicts N `sec_eavailw.tex:338-342` and README §5.
4. N `app_release.tex:73-75` (provenance ✓) contradicts README §4 `:98-102`.
5. N `sec_eavailw.tex:52-53,433` ("42 destinations") differs from the record's 43 M1 functionals.
6. Pa/Pr attribute M1 to the adopted covariance without the qualifier that it was graded on other products (R14a).
7. Pa `:100-101` puts Tune v1 in the low-E_avail generator set, but Pa Fig. 3's set is GENIE-CV/+MEC/NuWro/GiBUU.
8. GENIE-CV total: 2.52e-38 (N `sec_3d.tex:217`) against 2.4446e-38 (VL35) (R11a).
9. N `app_release.tex:12-13` carries a dated census ("35 git tags … 2026-09-21") that must be re-measured at release.

**Builds and sync, measured read-only:**
- Worktree `docs/analysis-note/` sources, figures and release package were compared with the standalone `MINERvA-OmniFold-Analysis-Note` checkout at `HEAD a11b705` (2026-09-23 17:48), using `diff -rq` and excluding build products. They are identical, apart from standalone-only `AGENTS.md`, `.gitignore` and `main_paperNotes.bib`.
- The standalone checkout's local PDFs (2026-09-23 17:47) show no unresolved references or citations; the logs contain only `T1/cmtt` font-shape warnings.
- **Not verified:** a fresh `build_all.sh` run (this pass is read-only and TeX lives on the NERSC login node); the Overleaf `output` jobname build; the actual remote heads of either repository (not fetched).

**Closure criterion:** each of items 1–9 fixed or dispositioned in a commit; `bash build_all.sh` exits 0 in both repos with fresh timestamps; `latexmk -jobname=output main_paper.tex` succeeds on a clean tree; `git ls-remote` heads recorded for both repositories.

**Readiness:** **OPEN.**

---

## 2. Generator and model predictions compared against

Sources: the generator agent's inventory plus my own reads. "In repo" means tracked here; every generated
prediction lives on `/pscratch` only. **No prediction file has a sha256 in `VALIDATION_LEDGER.md`.**

| Prediction | Version / config (as stated) | Dims | Prediction file / producer | Fixed or tuned (as stated) | Digest |
|---|---|---|---|---|---|
| Published MINERvA 2D (Ruterbories et al., arXiv:2106.16210) | Data plus covariance (N `sec_results.tex:54-96`) | 2D | `2d-unfolding/minerva_paper_anc/*.txt` in repo; ROOT `cov_ptpl_minerva_inclusive_6GeV.root` | Measurement | `6c6dce72…` (`values.tex:24-25`; `receipt_model_chi2_2d.json`) |
| MINERvA Tune v1, shipped ancillary | "GENIE 2.12.6 MINERvA Tune v1" (N `sec_results.tex:211-212`) | 2D (Pa Fig. 1) | `minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt` in repo; `2d-unfolding/compare_to_models.py` | Contains a low-recoil 2p2h enhancement fit (N `sec_experiment.tex:24-27`), built to absorb the low-q3 excess (N `sec_3d.tex:309-314`). Whether it was fit on these data: UNKNOWN. It is also the OmniFold prior. | `22231752…8240` (`receipt_model_chi2_2d.json`) |
| Tune v1, analysis MC truth (`w_truth`) | GENIE 2.12.6 + Tune v1 (N `sec_3d.tex:198-202`) | 2D slices, 3D; **also the "GENIE-CV" in the 4D q3 map and the 5D `(E_avail,W)` map** (R10a) | `3d-unfolding/genie/model_tune_xsec3d.py`; `nd-unfolding/q3_excess_projection.py`; `nd-unfolding/excess_eavail_W.py` (computed on the fly) | As above | none |
| GENIE CV (gevgen) | "GENIE 2.12.10 … DefaultPlusValenciaMEC"; CH target; ME FHC flux (N `sec_3d.tex:195-197`). Events contain no MEC (`:336-341`) | 3D; 5D band (Pa Fig. 3) | `3d-unfolding/genie/genie_to_xsec3d.py`, `gen_to_xsec_eavailW.py`, `run_gevgen.sh`; outputs `genie_cv_xsec3d.root`, `genie_cv_xsec_eavailW.root` | Stock GENIE, untuned (`3d-unfolding/genie/README.md:29-31`) | none (VL35 integrals only) |
| GENIE + Valencia 2p2h | `--event-generator-list Default+CCMEC`, 2M events, f_MEC = 2.87 % (N `sec_3d.tex:353-359`) | 3D; 5D band | `genie_mec_to_xsec3d.py`, `sbatch_gevgen_mec.sh`; `genie_mec_xsec_eavailW.root` | Stock; not independent of GENIE CV (Pa `:144-146`) | none (VL36) |
| Pion-FSI variations | `grwght1p` FrInel_pi / FrAbs_pi ±1σ (N `sec_3d.tex:317-322`) | 3D E_avail | `fsi_variation_xsec3d.py`; summaries in repo | Standard dials | none |
| NuWro | "NuWro 21.09", C target (N `sec_3d.tex:203-204`) | 3D; 5D band; FPS prior | `nuwro_to_xsec3d.py`, `nuwro_to_xsec_eavailW.py`, `run_nuwro.sh` | Independent generator | none (VL37) |
| GiBUU | "GiBUU 2019", C target, native build (N `sec_3d.tex:205-207`) | 3D; 5D band | `gibuu_to_xsec3d.py`, `gibuu_to_xsec_eavailW.py`; jobcard `work_gibuu/gibuu_mefhc_numu.job` | Independent | none (VL38) |
| Ascencio et al. (arXiv:2110.13372) | 44-cell d²σ/(dE_avail dq3) plus covariance (N `sec_3d.tex:466-468`) | 4D `(E_avail,q3)` | `3d-unfolding/genie/ascencio_2110.13372_supplemental.txt` in repo; `nd-unfolding/compare_ascencio_fullcov.py` | Measurement | not in ledger (local `748afa92…`) |
| NEUT, Tune v4.x | not compared (N `sec_3d.tex:209`) | — | — | — | — |

Release schema item 7 (N `app_release.tex:68-72`) covers only the four `(E_avail,W)` predictions plus the
Tune v1 ancillary, and they are **not assembled** (README `:112-114`). The 3D predictions, GENIE+MEC 3D,
FSI variations and Ascencio are outside the schema.

---

## 3. Every figure and table in the main paper, with its producer

The paper has **three figure environments and no `table` environment**; the only tabular is inline
in Fig. 1. `make_figures.sh` runs each producer on Perlmutter (`REPO=/pscratch/…`). It then copies any
newer same-name PDF into `figures/` (`make_figures.sh:115-123`) and makes the paper crops with
`pdfcrop` (`:156-167`). **No figure has a recorded sha256, producing commit or job.**

| Paper item | Asset | make_figures.sh | Producer (committed) | Key inputs (digest if known) |
|---|---|---|---|---|
| Fig. 1 top (`paper_body.tex:66`) | `model_comp_projections.pdf` | `:36` | `2d-unfolding/compare_to_models.py:160` (prefix `:44`) | `2d_crossSection_omnifold_MEFHC_5iter.root` (`142a45b0…`); paper `cov_ptpl…root` (`6c6dce72…`); Tune v1 txt (`22231752…`) |
| Fig. 1 bottom-left (`:69`) | `paper_validation_residual.pdf` | crop `:159-161` of `MEFHC_5iter_pull_full.pdf` (made at `:34`) | `2d-unfolding/compare_to_paper_fullcov.py:298-299` | same 2D ROOT plus paper covariance |
| Fig. 1 inline tabular (`:72-80`) | macros `\uqMedian`, `\uqPaper`, `\pullMean`, `\pullRMS` | — | `values.tex:77-78,97-98`; source `2D_OMNIFOLD_STUDY_STATUS.md:56-58`; `receipt_model_chi2_2d.json:197` (`pull_rms` 0.5981) | UNKNOWN for `uqMedian` (no receipt) |
| Fig. 2 (`:122`), also Pr `:188` | `paper_joint_localization.pdf` | crop `:165-167` of `excess_eavail_W.pdf` (made at `:54`) | `nd-unfolding/excess_eavail_W.py:201` | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root:hXSecND_flat` (pairing `0f04abce…`, `state/PROJ-20260920-binding-check.json:4`); comparator `mc_truth_denom`×`w_truth` from `runEventLoopOmniFold_5D_MEFHC.root`; flux `2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` |
| Fig. 3 (`:155`) | `paper_eavailW_generators.pdf` | crop `:162-164` of `eavailW_band.pdf` (made at `:55`) | `3d-unfolding/genie/overlay_eavailW_band.py:184,188` | `nd-unfolding/products/5d/excess_eavail_W.root:hData2D`; `{genie_cv,genie_mec,nuwro_cv,gibuu_cv}_xsec_eavailW.root:hXSec_eavailW`; no digests |

Primer-only figures, for completeness: `migration_resolution` (`nd-unfolding/make_control_plots.py:220-221`,
side output of `make_figures.sh:98`); `MEFHC_5iter_fig13` (`2d-unfolding/plot_2d_threeway_fig13.py:322,351`,
`:30`); `eavailW_band` (above); `fps_pilot_compare_MEFHC` (`nd-unfolding/fps_pilot_compare.py:159`, `:88`).

---

## 4. Governing records consulted

`AGENTS.md`; `docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`;
`DECISION-20260901-joseph-oi187-upgrade-not-blocker.md`; `DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`
(by reference); `QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md`;
`OUTCOME-20260922-3d-covariance-projected-from-the-adopted-trunk.md`;
`OUTCOME-20260922-ten-adopted-receipts-superseded-by-code-drift.md`;
`OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md`;
`CORRECTION-20260920-*`, `CORRECTION-20260921-*` (by reference); `VALIDATION_LEDGER.md` (VL35–39, VL142–145,
Active 2D/3D/4D sections); `KNOWN_ISSUES.md` rows 16, 19, 26, 36; `docs/OPEN_ITEMS.md` OI-2, OI-30, OI-31, OI-71,
OI-126, OI-129, OI-130, OI-187; `docs/CURRENT_WORK.md`; `docs/analysis-note/README.md`;
`release-package-20260922/README.md`. A predecessor readiness view exists at
`docs/orchestration/PUBLICATION-READINESS-20260822.md`; this draft has not been reconciled against it.

## Reconciliation after the s5n successor (`OI-191`, 2026-09-25)

The successor ([`OUTCOME-20260925-s5n-stage1-development-fail.md`](OUTCOME-20260925-s5n-stage1-development-fail.md))
changes no readiness value. Every row above keeps its state and **no row becomes READY**. It adds
dependencies to these rows:

| row | new dependency | governing record |
|---|---|---|
| R9, R12, R13 | the estimator's regularization bias under a GiBUU/GENIE-anchored E_avail shape change (several percent in the largest (E_avail,W) cells, up to 74% at high W) is in no covariance. The residual background-method nominal bias is ≈ 4% under purity, and ≤ ≈ 1% under `negweight-refined` (not adopted) | `KNOWN_ISSUES.md` 75, 77; `VL151`–`VL152`; `OI-192` |
| R12, R13 | no successor measurement uncertainty checkpoint qualified; the adopted-under-exception state stands with M1–M4 | s5n outcome §7 |
| R16, R17 | not attempted (excluded by the successor's authorization) | s5n authorization §3 (S3 not carried) |
| R20 | no new product qualified, so the release package is unchanged | — |
| R21 | the three deliverables state the s5n findings (canonical `84f284ef`, standalone `a1027e64`); built fresh, containment PASS, 0 unresolved references; clean-tree paper build (`-jobname=output`) OK | s5n index closeout |

# R21 fix plan: nine note/primer/paper consistency items

**Scope.** This is a read-only audit of `MINERvA-OmniFold-campaign-scalar5d` at `HEAD = 1957326e`
(branch `campaign/scalar5d-20260924`; `git ls-remote origin refs/heads/main` also returns `1957326e`).
`git diff 6abfb5f4 HEAD -- docs/analysis-note` is empty, so every line number in R21 (cited at
`6abfb5f4`) is still valid at this HEAD. Unless stated otherwise, all tex paths below are under
`docs/analysis-note/`. **Pa** means `paper_body.tex`, **Pr** means `primer_body.tex`, and **N** means
the note's `sec_*`/`app_*` files.

**Status of this plan.** One reader produced it and nobody has verified it independently. Nothing was
edited, staged or committed. Every proposed text keeps the macros and numbers that are already there.
The only new rendered numbers are generator version labels already printed in N `sec_3d.tex`, plus one
optional ledger value (2.44e-38, VL35) in item 8.

| # | Verdict | One line |
|---|---|---|
| 1 | **REAL** | The comparator for Fig. 2 and the note's `excess_eavail_W` figure is MINERvA Tune v1 (`w_truth`, the OmniFold prior), not stock GENIE. |
| 2 | **REAL (wording and omission)** | "DefaultPlusValenciaMEC" names the spline set. The event list was the default one, so there is no MEC and no contradiction, but it reads as one. Pa and Pr state no versions. |
| 3 | **REAL** | `app_release.tex` tells readers to check that λ_min "is positive". Both the note and README say the sign carries no information. |
| 4 | **REAL** | The ✓ on schema item 8 (provenance) is not earned. Most objects have no revision or job recorded, and the package carries none. |
| 5 | **REAL (minor; operand wording)** | M4 is measured over 43 functionals: the 42 destinations plus the all-ones total rate. The two maxima hold for the 42. The median does not strictly hold. |
| 6 | **REAL** | Pa and Pr attribute M1 (and, implicitly, M2/M4) to the adopted covariance. The measurements were made on the two campaign products. |
| 7 | **NOT A DEFECT** (optional qualifier) | Pa `:100-101` states the 3D four-generator result (N `sec_3d.tex:213-223`, `sec_execsummary.tex:37`), not Fig. 3. |
| 8 | **DISPOSITION: different objects, not an error** | 2.52e-38 comes from the 3D gevgen production and 2.4446e-38 from a separate (E_avail,W) gevgen production. They differ by 2.95% and nothing reconciles them. A TeX comment misattributes the second value to sec_3d. |
| 9 | **DISPOSITION** (dated census; add scope qualifier; re-measure at release) | The census is true as dated, but it is stale now (37 local tags, 31 on origin). "No release tag" still holds. |

---

## Item 1: Fig. 2 / `excess_eavail_W` comparator. **REAL**

**Evidence (code at 1957326e):**
- `nd-unfolding/excess_eavail_W.py:52-72` builds the comparator from tree `mc_truth_denom` weighted by
  `w_truth` (`br = [...] + ["w_truth"]`, `w = cols["w_truth"]`, `histnd(..., w[keep]*pot_scale)`).
  Its docstring at `:11-14` says so directly: "mc_truth_denom IS the GENIE CV model OmniFold starts
  from -- the prior".
- `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:595` sets
  `w_truth = model.GetWeight(*truthCV, evt)`. The model is defined at `:1745-1759`:
  `MnvTunev1 = {FluxAndCVReweighter, GENIEReweighter(true,false), LowRecoil2p2hReweighter,
  MINOSEfficiencyReweighter, RPAReweighter}`, and `mc_truth_denom` is created at `:1916`.
- `3d-unfolding/genie/model_tune_xsec3d.py:5-9` says "w_truth = the full MINERvA Tune v1 weight".
  The same object is labelled "MINERvA Tune v1" in N `sec_3d.tex:198-202`, and it reproduces the
  shipped Tune v1 ancillary to 0.01% (`3d-unfolding/genie/README.md`, Stage B).
- **Corroboration (independent operand):** the 4D analog `nd-unfolding/q3_excess_projection.py:5-8,51-54`
  uses the same `w_truth` prior and prints integrated data/"GENIE-CV" = 1.13 (N `sec_3d.tex:448`).
  For Tune v1 the 3D ratio is 3.08/2.71 = 1.137, while for the gevgen CV it is 3.08/2.52 = 1.22. Only
  the Tune v1 reading fits.
- The paper figure `paper_joint_localization.pdf` is a crop of panels (b) and (c) of
  `excess_eavail_W.pdf` (`make_figures.sh:165-167`). Those panels are titled "data/CV ratio" and
  "excess sigma (data - CV)" (`excess_eavail_W.py:193,198`), so no "GENIE" label appears inside the
  paper figure. The note's full figure has a left-panel legend and title reading "GENIE CV"
  (`:187-189`).
- The stock gevgen "GENIE-CV" (untuned GENIE 2.12.10, no MEC events) is a **different object**. It is
  the one in Fig. 3 / `eavailW_band` (`3d-unfolding/genie/run_eavailW_band.sh:12-19`). Pa and the note
  currently give both objects the same name.

**Proposed changes (captions and prose only; no number changes; the shares 57/67/83/22% were computed
against this same comparator and stay unchanged):**

1. Pa `paper_body.tex:115`
   - old: `$(\Eavail,W)$ projection relative to GENIE.  The positive central-value`
   - new: `$(\Eavail,W)$ projection relative to the MINERvA Tune~v1, the tuned GENIE~2.12.6 simulation from which the unfolding starts.  The positive central-value`
2. Pa `paper_body.tex:128`
   - old: `the unfolded-to-GENIE ratio per cell, dimensionless, on a $0.5$--$1.5$`
   - new: `the unfolded-to-Tune~v1 ratio per cell, dimensionless, on a $0.5$--$1.5$`
3. Pa `paper_body.tex:129`
   - old: `scale.  Right: the unfolded-minus-GENIE difference as a`
   - new: `scale.  Right: the unfolded-minus-Tune~v1 difference as a`
4. Pa `paper_body.tex:135`
   - old: `high-$\Eavail$, high-$W$ corner.  No significance is assigned.}`
   - new: `high-$\Eavail$, high-$W$ corner.  No significance is assigned.  The comparator is the MINERvA Tune~v1 (GENIE~2.12.6 with the analysis tune weights), not the untuned GENIE central value of Fig.~\ref{fig:generator-context}.}`
5. Pr `primer_body.tex:189`
   - old: `\caption{The unfolded data compared to the GENIE central simulation across`
   - new: `\caption{The unfolded data compared to the MINERvA-tuned GENIE simulation (MINERvA Tune~v1, the simulation the unfolding starts from, not the untuned ``central configuration'' of Fig.~\ref{fig:primergen}) across`
6. N `sec_eavailw.tex:40-41`
   - old: `Projecting the unfolded five-axis result onto $(\Eavail,W)$ and subtracting` / `the GENIE central value localizes the excess`
   - new: `Projecting the unfolded five-axis result onto $(\Eavail,W)$ and subtracting` / `the MINERvA Tune~v1 prediction (the analysis simulation's truth weighted by its full tune weight \texttt{w\_truth}, i.e.\ the OmniFold prior; \emph{not} the untuned GENIE~CV of \S\ref{sec:eavailw-band}) localizes the excess`
7. N `sec_eavailw.tex:67`
   - old: `\caption{Unfolded data versus the GENIE-CV prediction across the`
   - new: `\caption{Unfolded data versus the MINERvA Tune~v1 prediction (GENIE~2.12.6 with the analysis tune weights \texttt{w\_truth}, the OmniFold prior; labelled ``GENIE CV'' and ``CV'' inside the figure) across the`

**Adjacent, outside R21's list (same defect; R10a names it):** the 4D map in N `sec_3d.tex:444,448,455`
labels the same `w_truth` prior "GENIE-CV". Two places also assert something false for that comparator,
because Tune v1 carries the low-recoil 2p2h enhancement:
- `:461-462` says "(the base GENIE event-generator list contains no 2p2h, as in \S\ref{sec:3d-2p2h})".
- The caption at `:506-507` says "GENIE central value, no 2p2h in the base event-generator list."

Proposed wording:
- `:461-462` → `We show it here at central-value level (the comparator is the MINERvA Tune~v1 prior, \texttt{w\_truth}, \texttt{nd-unfolding/q3\_excess\_projection.py}, not the untuned GENIE sample of \S\ref{sec:3d-2p2h});`
- `:506-507` → `Comparator: the MINERvA Tune~v1 prior (\texttt{w\_truth}).}`

Relabelling "GENIE-CV" → "Tune~v1" at `:444,448,455,501` would complete the fix. Regenerating the figure
pixel labels ("GENIE CV" legend) needs ROOT plus `/pscratch` inputs on Perlmutter, and that step is
optional once the captions carry the qualifier.

---

## Item 2: GENIE description (versions and config). **REAL (wording and omission; no contradiction)**

**Evidence:**
- Pa `:35` ("GENIE~2.12.6 and the MINERvA Tune~v1") describes the analysis MC. This is correct and
  agrees with N `sec_experiment.tex:24`, `sec_results.tex:112,212`.
- The gevgen samples use `3d-unfolding/genie/setup_genie.sh:26-29`: `GENIE_VER=v2_12_10c`,
  `GENIE_XSEC_VER=v2_12_10`, and `GENIE_TUNE=DefaultPlusValenciaMEC`. `GENIE_TUNE` selects the
  **spline set** (`.../NULL/DefaultPlusValenciaMEC/data/gxspl-FNALbig.xml.gz`).
- `run_gevgen.sh:37-46` passes `--event-generator-list` only if `GEVGEN_LIST` is set. Its comment
  says "the bare 'Default' list excludes it [MEC]". The CV runs (`run_parallel_cv.sh`,
  `sbatch_gevgen_mefhc.sh`) do not set it. The MEC run sets `Default+CCMEC` (`sbatch_gevgen_mec.sh:15`).
- So N `sec_3d.tex:195-197` (splines/config) and `:336-341` (`mec=0` for all 1.48M CC events) are both
  true. They describe different settings, but the text makes them look contradictory.
- Pa Fig. 3 (`:156-159`) and Pr Fig. `primergen` (`:156-165`) give no generator versions or targets.
  N gives NuWro 21.09 on C and GiBUU 2019 on C at `sec_3d.tex:203-207`, and GENIE on CH at `:195-196`.

**Proposed changes:**
1. N `sec_3d.tex:195-197`
   - old:
     ```
       \item \textbf{GENIE 2.12.10 central value} --- generated with \texttt{gevgen}
             on a CH target with the MINERvA ME~FHC flux and the
             DefaultPlusValenciaMEC configuration~\cite{Andreopoulos:2009rq}.
     ```
   - new:
     ```
       \item \textbf{GENIE 2.12.10 central value} --- generated with \texttt{gevgen}
             on a CH target with the MINERvA ME~FHC flux, using the
             DefaultPlusValenciaMEC cross-section splines~\cite{Andreopoulos:2009rq}
             but gevgen's default event-generator list, which excludes MEC, so the
             sample contains no 2p2h events (\S\ref{sec:3d-2p2h}); no MINERvA
             reweights are applied.
     ```
2. Pa `paper_body.tex:157-159`
   - old: `central-value projections.  GENIE-CV, GENIE with the Valencia two-particle--` / `two-hole contribution, NuWro, and GiBUU all remain below the unfolded result` / `at high $W$.  No significance is assigned.}`
   - new: `central-value projections.  GENIE-CV (untuned GENIE~2.12.10 on CH, with no two-particle--two-hole events), the same GENIE with the Valencia two-particle--` / `two-hole contribution, NuWro~21.09, and GiBUU~2019 (both on carbon) all remain below the unfolded result` / `at high $W$.  No significance is assigned.}`
3. Pr `primer_body.tex:157-158`
   - old: `simulation predictions --- GENIE's own central configuration, the same GENIE` / `with the two-nucleon process added, NuWro and GiBUU.`
   - new: `simulation predictions --- GENIE's own untuned central configuration (version 2.12.10), the same GENIE` / `with the two-nucleon process added, NuWro (21.09) and GiBUU (2019).`

The Fig. 2 version is covered by item 1 (Tune v1 = GENIE 2.12.6).

---

## Item 3: λ_min positivity. **REAL**

**Evidence:**
- N `app_release.tex:109-110` has "λ_min = +4.359104e-92 (positive; n_negative = 0)". Step 4 at
  `:182-185` says "Check instead that λ_min/λ_max ≈ 2.9e-15 and that λ_min is positive".
- N `sec_eavailw.tex:337-342` says the smallest eigenvalues sit at the noise floor, "so **their sign
  carries no information**".
- `release-package-20260922/README.md` §5, λ row (`:138`), withdraws "λ_min is positive". A cross-host
  re-measurement agrees to only 5 significant digits. `:154-159` replaces the signed ratio with
  "|λ_min|/λ_max of order 1e-15" and adds "Do not check λ_min > 0".
- The governing measurement is `docs/orchestration/PLAN-20260918-scalar5d-publication-completion.md`
  §16.1a (`:1174`). R13's closure test is `grep -n "is positive" app_release.tex` returning 0.

**Proposed changes:**
1. N `app_release.tex:109-110`
   - old: `$\max|C-C^{\top}|=0$; $\lambda_{\min}=+4.359104\times10^{-92}$ (positive;` / `$n_{\mathrm{negative}}=0$) against $\lambda_{\max}=1.488215\times10^{-77}$,`
   - new: `$\max|C-C^{\top}|=0$; $\lambda_{\min}=+4.359104\times10^{-92}$ on the build host (its sign sits at the floating-point noise floor and carries no information, \S\ref{sec:eavailw-construction};` / `$n_{\mathrm{negative}}=0$ describes this computation only) against $\lambda_{\max}=1.488215\times10^{-77}$,`
2. N `app_release.tex:182-185`
   - old:
     ```
             package is corrupt. Check instead that
             $\lambda_{\min}/\lambda_{\max}\approx2.9\times10^{-15}$ and that
             $\lambda_{\min}$ is positive, and treat the object as ill-conditioned
             rather than as having a definite rank.
     ```
   - new:
     ```
             package is corrupt. Check instead that
             $|\lambda_{\min}|/\lambda_{\max}$ is of order $10^{-15}$, the edge of
             double precision, and treat the object as ill-conditioned rather than
             as having a definite rank. Do not check the sign of $\lambda_{\min}$:
             it sits at the noise floor, carries no information, and a second host
             reproduces $\lambda_{\min}$ to only five significant digits.
     ```

After both edits, `grep -n "is positive" app_release.tex` returns nothing.

---

## Item 4: Provenance ✓. **REAL**

**Evidence:**
- N `app_release.tex:42-44` defines ✓ as "identity or value already fixed and listed in
  \S\ref{app:release-identities}". Item 8 at `:73-75` requires "for each object, the producing revision,
  the producing job, and the digest ... read back".
- The identities table (`:94-129`) lists a revision and job only for C_Z (`fb9ec356`, `58454524`). It
  lists a job but no revision for C_EW (`58655509`). It lists neither for M, the row index, or the
  paired central values. The row index does have a read-back digest.
- `docs/orchestration/state/PROJ-20260920-m1-publication-receipt.json` records only the **source's**
  `code_identity.revision` (`fb9ec356...`), not a producing revision for the projection.
- `release-package-20260922/README.md:98-102` says "Per-object provenance ... NOT CARRIED ... no
  producing revision and no producing job for any object".

**Proposed change:** N `app_release.tex:73-75`
- old:
  ```
    \item \textbf{Provenance} $\checkmark$: for each object, the producing
          revision, the producing job, and the digest of the bytes as read back
          out of the closed file.
  ```
- new:
  ```
    \item \textbf{Provenance}: for each object, the producing
          revision, the producing job, and the digest of the bytes as read back
          out of the closed file. This is fixed only in part: the assembling
          revision and job of $C_{Z}$, the job of $C_{EW}$ and the read-back
          digest of the row index (\S\ref{app:release-identities}). No producing
          revision or job is recorded for the other objects, and the assembled
          package carries none.
  ```

---

## Item 5: "42 destinations" versus "43 functionals". **REAL (minor; operand wording)**

**The two sentences describe different objects:**
- **43** is the functional set `U = vstack([M, ones])` from `nd-unfolding/z_grade.py:260-305`
  (`m1_functionals`): the 42 rows of M1 (the (E_avail,W) destinations) plus the all-ones total-rate
  vector at index 42.
- M4 (`docs/orchestration/state/CENTRAL-VALUE-VS-SIGMA-20260920.json`, `n_functionals: 43`; DECISION
  §4 M4 `:98`; `values.tex:379` "max over the 43 functionals") is computed over all 43.
- The two maxima quoted in the note fall on destination rows: movement argmax 2
  (`\cvMoveProjMax` = 0.761) and movement/σ argmax 4 (`\cvMoveOverSigmaMax` = 6.02). So "at most"
  over the 42 destinations is **true**.
- The median `\cvMoveOverSigmaMed` = 1.06% is the median over 43 values. It includes the total rate,
  whose ratio is 1.13%. The median over the 42 destinations alone was never computed. Because the
  dropped value lies above 1.06%, that median is ≤ 1.06%.
- So "on these 42 destinations ... median 1.06%" names the wrong operand for the median. The M4 values
  also come from the two campaign members' own CV executions (see item 6), not from the adopted
  product's bytes.

**Proposed changes:**
1. N `sec_eavailw.tex:52-53`
   - old: `five-axis result, and that result is not seed-independent: on these` / `\zprojCells\ destinations the estimator seed moves the central value by at most`
   - new: `five-axis result, and that result is not seed-independent: on the 43 projection functionals of the estimator-seed campaign (these` / `\zprojCells\ destinations plus the total rate), the estimator seed moves the central value by at most`
2. N `sec_eavailw.tex:433`
   - old: `their own uncertainty.} On these \zprojCells\ destinations the central value`
   - new: `their own uncertainty.} On the 43 projection functionals of the grade (these \zprojCells\ destinations plus the all-ones total rate), the central value`

These edits change no number. Pa `:193-195` and Pr `:91-93` say "projected central values" without a
count and need no change for item 5.

---

## Item 6: M1 attribution in Pa and Pr. **REAL**

**Evidence:**
- `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:36-38` (§2) says the campaign
  "computed M(ii) for `361090f9…` and `7e4636a3…`, which are *different products*. For **this** digest,
  cause 3 remains predeclared and not computed". §4 M1 `:62` names "Digests graded / compared:
  `361090f9…` / `7e4636a3…`".
- `OUTCOME-20260920-cause3-two-member-assessable-FAIL.md:103-106` says those products are "graded,
  recorded, and **not** put forward".
- M2 is measured on the same campaign: `state/SEED-EFFECT-20260920.json` `control_reproduces_the_grade`
  gives 0.06145388. M4 uses the members' own CV executions
  (`probes/probe-20260920-central-value-seed-movement.py:1-20`, commit `9f85830f`). Only M3 (26.0% of
  √Tr C_Z) is a property of the adopted bytes.
- The note states this for M(ii) (`sec_eavailw.tex:443-447`). Pa `:171-174` ("Varying the estimator
  seed moves the projected uncertainty by 6.145%" straight after "A scalar five-dimensional covariance
  is adopted") and Pr `:73-76` do not.

**Proposed changes:**
1. Pa `paper_body.tex:171-173`
   - old: `quote no publication-level significance, and the reason is measured rather` / `than precautionary.  Varying the estimator seed moves the projected` / `uncertainty by \SI{\sprojMeasured}{\percent}, against a`
   - new: `quote no publication-level significance, and the reason is measured rather` / `than precautionary.  In a dedicated campaign of two companion covariances built at two estimator-seed settings for this test (products distinct from the adopted bytes), varying the seed moves the projected` / `uncertainty by \SI{\sprojMeasured}{\percent}, against a`
2. Pr `primer_body.tex:74-76`
   - old: `Change that seed, leaving everything else alone, and the \emph{uncertainty} we` / `report on the projected result shifts by about \SI{\sprojMeasured}{\percent}`
   - new: `Change that seed, leaving everything else alone, and the \emph{uncertainty} we` / `report on the projected result shifts by about \SI{\sprojMeasured}{\percent} (measured on two test versions of it built for exactly this comparison, not on the adopted version itself)`
3. (Optional, N, so the note says the same for M2 and M4.) `sec_eavailw.tex:447-448`
   - old: `built for that purpose, and grading them does not regrade these bytes. The` / `exact record identifiers are in App.~\ref{app:provenance}.`
   - new: `built for that purpose, and grading them does not regrade these bytes. The first, second and fourth measurements above were all made on those two products; only the third is a property of these bytes. The` / `exact record identifiers are in App.~\ref{app:provenance}.`

---

## Item 7: Tune v1 in the Pa low-E_avail generator set. **NOT A DEFECT** (optional qualifier)

**Evidence:**
- Pa `:99-101` does not cite Fig. 3. It restates the note's **3D** comparison, whose four predictions
  are GENIE CV, Tune v1, NuWro and GiBUU (N `sec_3d.tex:190-208`). "The data sit above all four in the
  lowest-E_avail bins" (`:219-223`), and `sec_execsummary.tex:37` says the same.
- Pa Fig. 3's set (GENIE-CV/+MEC/NuWro/GiBUU) is the (E_avail,W) band and is introduced separately at
  Pa `:139-142`.
- GENIE+MEC also remains below the data in the low-E_avail dip, since it fills only 46% of the gap
  (N `sec_3d.tex:360-363`). So the claim is true whichever set a reader picks.
- After item 1, Tune v1 does appear in the paper (Fig. 2).

**Optional qualifier to stop readers matching the sentence to Fig. 3:** Pa `paper_body.tex:100`
- old: `low-recoil discrepancy.  GENIE, the MINERvA Tune~v1, NuWro, and GiBUU all`
- new: `low-recoil discrepancy.  In the three-observable comparison of the companion note, GENIE, the MINERvA Tune~v1, NuWro, and GiBUU all`

---

## Item 8: GENIE-CV total, 2.52e-38 versus 2.4446e-38. **DISPOSITION: different objects, not an error**

**Evidence:**
- **2.52e-38** (N `sec_3d.tex:217`) is the 3D Stage-A gevgen sample.
  - Source: `3d-unfolding/genie/run_parallel_cv.sh` (8 × 250k, seeds 11–18, `work_p*`) converted by
    `genie_to_xsec3d.py`. `3d-unfolding/genie/README.md` Stage A reads "total-in-PS 2.52e-38 vs
    unfolded 3.08e-38".
  - The tracked summaries `genie_fsi_FrAbs_pi_xsec3d_summary.txt:6` and
    `genie_fsi_FrInel_pi_xsec3d_summary.txt:6` give dial 0 = CV = 2.516697e-38.
- **2.4446e-38** (`VALIDATION_LEDGER.md:512`, VL35) is the (E_avail,W) band's GENIE-CV.
  - Source: `run_eavailW_band.sh:12-19`, which hadds `work_seed*` (`sbatch_gevgen_mefhc.sh`,
    20 seeds × 200k) and runs `gen_to_xsec_eavailW.py`.
  - The log (copy at `docs/sep-09-presentation/ai-research-talk/inputs/eavailW_band_20260811_allfour.log`)
    reads "GENIE-CV: total=2.4446e-38".
- The gevgen productions are distinct, and so are the converters. Both converters use the same
  `flux_avg_sigma_cc_per_nucleon` normalization. The W edges start at 0 and `w_true` maps W² ≤ 0 to 0,
  so the (E_avail,W) converter drops nothing the 3D one keeps.
- NuWro (2.34 / 2.3444) and GiBUU (2.22 / 2.2227) agree across the 3D and 5D sets. The GENIE-CV pair
  differs by **2.95%**, and **no record reconciles it**. No record shows either number wrong under its
  own producer.
- The rendered text quotes only 2.52e-38. The band section `sec_eavailw.tex:185-186` quotes GiBUU and
  data totals, not GENIE's, so no rendered sentence contradicts another. Pa and Pr quote neither value.
- **A real mis-citation, but in a non-rendering comment:** `sec_eavailw.tex:140-142`, repeated in the
  append-only ledger at `VALIDATION_LEDGER.md:536-538`, reads "sec_3d:151's ordering GiBUU 2.2227e-38
  < NuWro 2.3444e-38 < GENIE CV 2.4446e-38". sec_3d prints 2.52e-38 there, and `:151` is a stale
  address; the ordering is at `:215-217`.

**Proposed changes:**
1. (Recommended, comment only.) N `sec_eavailw.tex:140-142`
   - old:
     ```
     % Controls that reproduce EXACTLY and are why the set is trustworthy: GiBUU integrated
     % 2.2227e-38 and data 3.0699e-38 (this paragraph's own 2.22 / 3.07), and sec_3d:151's
     % ordering GiBUU 2.2227e-38 < NuWro 2.3444e-38 < GENIE CV 2.4446e-38.
     ```
   - new:
     ```
     % Controls that reproduce EXACTLY and are why the set is trustworthy: GiBUU integrated
     % 2.2227e-38 and data 3.0699e-38 (this paragraph's own 2.22 / 3.07). The ORDERING
     % GiBUU < NuWro < GENIE CV matches sec_3d.tex:215-217, but the GENIE value does not:
     % this band's GENIE-CV 2.4446e-38 (work_seed* gevgen, gen_to_xsec_eavailW.py) is a
     % different object from sec_3d's 2.52e-38 (Stage-A work_p* gevgen, genie_to_xsec3d.py);
     % the 2.95% difference is not reconciled. (The ledger's VL35 prose repeats the old claim.)
     ```
2. (Optional, rendered qualifier.) N `sec_eavailw.tex:94-96`
   - old: `predictions from GENIE~CV, GENIE$+$Valencia~2p2h/MEC, NuWro, and GiBUU` / `(Fig.~\ref{fig:eavailWband}).`
   - new: `predictions from GENIE~CV, GENIE$+$Valencia~2p2h/MEC, NuWro, and GiBUU` / `(Fig.~\ref{fig:eavailWband}). These are separate productions from the 3D samples of \S\ref{sec:3d-models}; this GENIE~CV's in-phase-space total, \SI{2.44e-38}{cm^2/nucleon}, is \SI{3}{\percent} below the \SI{2.52e-38}{} quoted there, and that difference has not been reconciled.`

**Closing R11's reconciliation needs one cluster read.** Compare `nCCtotal` and the in-PS fraction
printed by the two converters, or rerun `genie_to_xsec3d.py` on `genie_mefhc_cv_ALL.gst.root`. This
plan does not do that.

---

## Item 9: Dated census in `app_release.tex:12-13`. **DISPOSITION**

**Measured 2026-09-25 (read-only):**
- `git tag` in this checkout: **37** (32 `evidence/*`, 1 `freeze/*`, 4 `z-deploy-*`).
- `git ls-remote --tags origin`: **31**, all `evidence/*`. There are no freeze or deploy tags on the
  remote.
- The standalone remote carries 1 tag (`evidence/preparation-2026-09-24-a11b7055`).
- No `release`/publication tag exists anywhere, so the paragraph's headline ("No release tag and no
  release manifest exist") **still holds**.

The count is true only as dated. "In this checkout" is also ambiguous, because the same source is built
in the standalone repository, which has 1 tag.

**Proposed change (no number changed; the release-time re-measure stays open under R21):** N
`app_release.tex:12-13`
- old: `exist.} Measured in this checkout on 2026-09-21: 35 git tags, of which 30 are`
- new: `exist.} Measured on 2026-09-21 in a local checkout of the canonical analysis repository (a dated census, to be re-measured against the remote when a release is cut): 35 git tags, of which 30 are`

---

## Adjacent leads found while checking (not in R21; unverified; route to R11/R10)

- **VL36 GENIE+MEC normalization convention.** 3D `genie_mec_to_xsec3d.py:7-21,64-93` divides by the
  **non-MEC** CC count, lifting the total by 1/(1−f_MEC), because `tot_cc` excludes MEC. N
  `sec_3d.tex:355-359` describes that convention. The (E_avail,W) GENIE+MEC is made by
  `gen_to_xsec_eavailW.py` (`run_eavailW_band.sh:23-29`), which divides by **all** CC (`:107-108`), so
  that band may be low by about f_MEC ≈ 2.9%. If so, VL36's corner ratio 1.579 becomes about 1.534 under
  the 3D convention, roughly equal to GENIE-CV's 1.535. That would weaken N `sec_eavailw.tex:176-177`
  ("slightly worsens it (1.54→1.58)"), but not the claim that 2p2h does not close the corner. This
  needs the MEC fraction of `genie_mefhc_mec_ALL.gst.root` (a cluster read).
- **A numeric coincidence worth one look:** 2.516697/2.4446 = 1.02949, and 1/(1−0.0287) = 1.02955.
- **Note Fig. `excess_eavail_W` pixels** still say "GENIE CV" (item 1). Regenerating them needs Perlmutter.

---

## How the three documents are built

- `docs/analysis-note/build_all.sh` builds `main_note`, `main_primer` and `main_paper`.
  - **Build step:** it runs `module load texlive/2024 || true`, which is a no-op locally, then
    `latexmk -g -pdf -interaction=nonstopmode -halt-on-error <t>.tex` for each target.
  - **Checks on each PDF:** it re-invokes once if the log shows unresolved references (KNOWN_ISSUES
    row 50). It then fails if the PDF does not postdate a pre-build marker, if a shared source
    (`preamble.tex values.tex technote.bib`) is newer than the PDF, or if the log is missing or still
    unresolved.
  - **Containment:** it runs `python3 check_dead_containment.py --self-test` and then the strict
    check. This needs `pdftotext` or Ghostscript.
  - **Last:** it prints page counts.
- `README.md` (`:11-19`) says `bash build_all.sh` must produce all three PDFs and prove containment.
- The paper is `revtex4-2` with `apsrev4-2`, so it uses bibtex. The note and primer use biblatex/biber.
- R21's closure criterion also asks for the Overleaf form `latexmk -jobname=output main_paper.tex`.
- Figures come from `make_figures.sh`. It crops panels from cluster-made PDFs and asserts their page
  sizes; regenerating those PDFs needs ROOT plus `/pscratch`.
- **The TeX toolchain exists locally:**
  - `/Library/TeX/texbin/{latexmk,pdflatex,biber,bibtex,pdfcrop}`.
  - Versions: TeX Live 2024, latexmk 4.83, pdfTeX 1.40.26, biber 2.19.
  - `pdftotext`, `gs` and `pdfinfo` are in `/opt/homebrew/bin`.
  - The build header says "NERSC login node", but that is not the only option.
  - The last standalone sync commit `a11b705` reports `build_all.sh` exit 0 (note 106 pp, primer 7 pp,
    paper 4 pp). `build_all.sh:37-40` records a local cold-tree run with latexmk 4.83.
  - Known local hazard: the macOS biber PAR cache can age out, giving biber exit 2 with an empty `.blg`.

## Standalone repository sync

- **Contract:** `/Users/josephbailey/local-research/MINERvA-OmniFold-Analysis-Note/AGENTS.md` and the
  canonical `AGENTS.md:144-150`. The standalone is a source-only mirror of `docs/analysis-note/`:
  1. Copy the changed source files in both directions without overwriting unrelated history.
  2. Run `bash build_all.sh` in the standalone checkout.
  3. Commit and push **both** repositories.
  4. Record both remote heads.
- **Practice:** the pattern is a `[sync] ...` commit in the standalone listing "Synced from
  MINERvA-OmniFold docs/analysis-note/ at <sha>" and the build result (e.g. `a11b705`). Because the two
  histories differ, the method is file copy, not subtree push. The PDFs are gitignored at the root
  (`/main_*.pdf`).
- **Remotes:**
  - The standalone's `origin` is `https://github.com/josephbaileyy/MINERvA-OmniFold-Analysis-Note.git`.
  - The canonical repo has the same URL as remote `analysis-note`, plus `origin` at
    `https://github.com/josephbaileyy/MINERvA-OmniFold`.
- **Push authority:** DECISION-20260920 §6 reserved "the analysis-note push" to Joseph.
  `AUTHORIZATION-20260924-scalar5d-campaign-activation.md` §4 now activates "commits, merges and pushes
  to `origin` and `analysis-note`" (force-push and history rewrite excluded).
- **Standalone state (read-only, 2026-09-25):**
  - `git status --porcelain` is empty.
  - `HEAD = a11b705` = `origin/main`. `git ls-remote` confirms `refs/heads/main a11b7055`, and an open
    `refs/pull/1/head b61cd896` also exists.
  - `diff -rq` against this worktree's `docs/analysis-note/` (build products excluded) shows only the
    standalone-only `.gitignore`, `AGENTS.md` and `main_paperNotes.bib`. Sources, figures and the
    release package are identical.

## `git status --porcelain` after this audit
- `MINERvA-OmniFold-campaign-scalar5d`: empty (no changes).
- `MINERvA-OmniFold-Analysis-Note`: empty (no changes).

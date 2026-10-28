# Data-availability and data-release survey: seven neutrino cross-section papers (2026-10-28)

## 0. What was read

- **Sources.** The brief's path (`ee772d13-.../scratchpad/register-study/src/<id>/`) holds only empty directories. The
  tmp sweep at 2026-10-28 00:00 emptied them: `find` reports zero files under `src/`. On the coordinator's correction,
  I read the surviving copy instead, read-only:
  `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/be6e903d-7ae7-440f-b5aa-de78760f31e0/scratchpad/corpus-dl/<id>vN/x/`.
  The versions are 2106.16210v4, 2110.13372v2, 2002.12496v2, 2004.05434v2, 2102.03346v1, 2301.03700v4 and
  2310.06082v4, the same versions listed in the corpus record REPORT.md §1.
- **Files read.**
  - Every top-level `.tex` file.
  - The `.bbl` and `.bib` entries for each data-release citation.
  - Every README.
  - The arXiv ancillary trees `x/anc/` of 2106.16210 and 2002.12496, including file headers and, through
    `pdftotext` to stdout, the 14-page `anc/SupplementaryMaterial.pdf` of 2002.12496.
  - The section headers of the data file shipped in the source of 2110.13372.
  - The `supp.tex` of both MicroBooNE papers, with their `\input` tables.
- **Ancillary files.** Saved arXiv abstract pages from session `796e7ecc` list ancillary files only for 2106.16210
  (25) and 2002.12496 (16). These pages were read locally; no web access was used.
- **Method.** I searched with grep for: supplement, data avail, data release, availab, HEPData, doi, url, http, href,
  ancillary, .root, .txt, "provided", "can be found", "appendix". I then read the context of every hit.
- **No web use and no downloads.** Nothing was written except this file.

## 1. Per-paper extraction

Notation: `x/` is relative to the corpus-dl copy above.

### 1.1 MINERvA 2106.16210v4 (PRD 104, 092007)

| element | finding |
|---|---|
| Data-availability or release statement in the paper | **None.** `x/main.tex` has no sentence on data release, supplement, URL or DOI. The only hit is `main.tex:291`: "In addition to the two-dimensional cross sections,  one-dimensional projections, limited to the phase space of the double-differential cross section, are also provided." This refers to the figures in the paper. |
| Supplemental-material references | None in `main.tex`. |
| What is released, and in what form | The arXiv **ancillary files** `x/anc/` hold 25 files and are never mentioned in the text. `anc/README:1`: "Conventions and units used within this data release for : Phys.Rev.D 104 (2021) 9, 092007". `anc/README:15`: "Data Cross Section, Figure 13, is saved in data_result_ptpl_2D_minerva_inclusive_6GeV.txt" (CSV of the cross section with statistical and total uncertainty). `anc/README:25-30`: "Covariance matrices are provided for: total uncertainty … total uncertainty in ROOT TMatrix format for precision … statistical uncertainty … flux uncertainty … muon energy scale uncertainty". `anc/README:40`: "Cross sections for model predictions described in Figures 15,16,17,18 are provided in the model_ptpl*.txt files." (17 model files). `anc/README:8`: binning in `bin_mapping.txt`. `anc/README:3-5` names two contact persons. |
| Repository, DOI, URL or HEPData | None cited. The release lives only as arXiv ancillary files. |

### 1.2 MINERvA 2110.13372v2 (PRD 106, 032001)

| element | finding |
|---|---|
| Data-availability or release statement | **None.** The nearest sentence is `Analysis.tex:341`: "The unfolded cross section allows for a wider range of comparisons and can be used by researchers without requiring the full \minerva experiment simulation." |
| Supplemental-material references | None in `Analysis.tex`. There is an in-paper appendix (`Analysis.tex:646-647`) that the text points to: `:520` "the efficiencies as a function of available energy are reported at the Appendix"; `:574` "The $\chi^2$ values and commentary are provided in the appendix." The appendix shows efficiency **figures** and a χ² table, not tabulated data. |
| What is released, and in what form | The source tree holds a text file, `x/supplementalMELowRecoilData.txt_.txt` (224 non-empty lines), that **the TeX never references**. Its contents: `:1` "Table I: neutrino flux"; `:134` "Table II: Measured cross section per nucleon …"; `:135` "Format: Idx, Eavail (low-edge of bin -- up-edge of bin), q3 (low-edge of bin -- up-edge of bin), cross section"; `:184` "Table III: Covariance matrix on cross section." (44×44). It is not an arXiv ancillary file. Its name suggests it was the journal supplement. |
| Repository, DOI, URL or HEPData | None. |
| Side observation | The Table II header (`:134`) gives the units as "10$^{-39}$ cm$^2$ / GeV$^2$ / nucleon", but the values are written absolutely (for example `:138` "9.49304e-39"). The header and the values are inconsistent. |

### 1.3 MINERvA 2002.12496v2 (PRD 101, 112007)

| element | finding |
|---|---|
| Data-availability or release statement | **None in the text.** |
| Supplemental-material references | No reference in the text. A dormant switch sits in the preamble: `2DLEInclusive.tex:4-6` "The document must be slightly different for PRD than the arXiV because the appendix (and references to it) must be "supplemental material" for PRD." and `:51-56` `\newcommand{\PRDsupp}{1}` … `\newcommand{\SuppLocation}{at URL}`. `\SuppLocation` is defined but never used (2 occurrences, both definitions). |
| What is released, and in what form | There are 16 arXiv ancillary files, unmentioned in the text. (a) `anc/SupplementaryMaterial.pdf` (14 pp.), section "I. SUPPLEMENTAL MATERIALS": "This supplement includes the double and single differential cross sections used in this analysis. The bin limits used for all cross sections are presented in Table I." It contains the measured double- and single-differential cross sections, the total uncertainties and the binning, plus predictions for 10 models ("Tables IV-XIII show the Monte Carlo cross sections for each model and variant used"). It has no covariance. (b) `anc/data_release/`: `data_result_{ptpl_2D,ptmu,pzmu}_CCInclusive.txt` and `cov_{fullUncertainty,statonly}_*_CCInclusive.{txt,root}` (CSV and ROOT). There is no README. |
| Repository, DOI, URL or HEPData | None. |
| Side observation | `cov_statonly_ptpl_2D_CCInclusive.txt` and `cov_fullUncertainty_ptpl_2D_CCInclusive.txt` are **byte-identical** (`cmp` exits 0). The ROOT pair differs, and so do the 1D text pairs. |

### 1.4 T2K 2004.05434v2 (PRD 101, 112004)

| element | finding |
|---|---|
| Data-availability or release statement | **Yes, as the last paragraph of the Conclusions.** `JointNumuOCCC0piXsec.tex:1277`: "The data release for the results presented in this analysis is posted at the link in Ref. \cite{bib:datarel}.  It contains the analysis binning, the oxygen and carbon $\nu_\mu$ double-differential  cross  sections  central  values, their ratio and associated covariance and correlation matrices." |
| Supplemental-material references | `:825` "Similar plots for the other signal and control samples can be found in the supplementary material." `:1042` "…for completeness the unregularised results are available as supplementary material…". `:1044` "Similar plots for the control samples are available in the supplementary material…". The arXiv source contains no supplement. Appendices A–B (`:1293`, `:1326`) show uncertainty, covariance and correlation **figures**. |
| What is released, and in what form | Binning, O and C cross sections, their ratio, covariance and correlation matrices, on a collaboration web page. The page's file formats were not checked (no web access). |
| Repository, DOI, URL or HEPData | **URL**: `JointNumuOCCC0piXsec.bbl:901-904` (`bibliography.bib:2447-2449`) `title = {Data release}`, `\url{https://t2k-experiment.org/results/cc0pi_c_o_data/}`. No DOI and no HEPData. |

### 1.5 T2K 2102.03346v1 (PRD 103, 112009)

| element | finding |
|---|---|
| Data-availability or release statement | **Yes, as the last paragraph of the Conclusion.** `ms.tex:1070-1071`: "The data release for the results presented in this analysis is posted in Ref.~\cite{data}. It contains the analysis binning, the differential cross section best-fit values, and associated covariance matrices." |
| Supplemental-material references | None. The appendix "More model comparisons" (`ms.tex:1084`) holds figures only. |
| What is released, and in what form | Binning, best-fit cross sections and covariance matrices on a collaboration web page. Formats were not checked. |
| Repository, DOI, URL or HEPData | **URL**: `ms.bbl:1200-1203` (`ms.bib:34-36`) `title = {Data release}`, `\url{https://t2k-experiment.org/results/2021_tki_numucc1pinp/}`. No DOI and no HEPData. |

### 1.6 MicroBooNE 2301.03700v4 (PRD 108, 053002)

| element | finding |
|---|---|
| Data-availability or release statement | **Yes, one sentence in the main-text methods section.** `main.tex:381`: "The data release, the unfolded covariance matrices, and the additional matrices $A_{C}$ can be found in the Supplemental Material." |
| Supplemental-material references | `main.tex:164` "The particle composition of the panels included in Fig.~\ref{picpid} is shown in the Supplemental Material." `:381` (above). `:414` "The Supplemental Material includes tables detailing all the cross section uncertainties used in this work." In `supp.tex:66` §"Data Release", `:72-73`: "The data release with the data results, the covariance matrices, and the additional smearing matrices is included in the DataRelease.root file. Instructions on how to use the data release and the description of the binning scheme are included in the README file." `supp.tex:69` gives usage: "The additional smearing matrix $A_{C}$ should first be applied to the event distribution of an independent theoretical prediction … and then divided by the bin width." |
| What is released, and in what form | (a) Supplement tables of cross sections with uncertainty (11 `\input` tables, `supp.tex:78-92`) and uncertainty-component tables (`:121`, `:198`). (b) A ROOT file with cross sections, total uncertainties, covariances and A_C (`README.txt:3-4`), plus a global-bin scheme text file (`README.txt:17`). |
| Repository, DOI, URL or HEPData | None. The release rides with the APS supplement. |
| Side observation | The README names `DataRelease.root` and `BinScheme.txt`, but the files in the source are `main_supp_DataRelease.root` and `main_supp_BinScheme.txt`. |

### 1.7 MicroBooNE 2310.06082v4 (PRD 109, 092007)

| element | finding |
|---|---|
| Data-availability or release statement | **Partial, in the main-text methods section.** `main.tex:687`: "The $A_{C}$ matrix is included in the Supplemental Material and needs to be applied to all theory predictions in order to compare to the data measurements, even though its effect is small." The full release sentence is in the supplement only: `supp.tex:74-76` "The data release with the data results, the covariance matrices, and the additional smearing matrices is included in the DataRelease.root file. These are also included in the Supplemental Material in Sec.~\ref{datarel}, Sec.~\ref{cov}, and Sec.~\ref{smear}, respectively. Instructions on how to use the data release and the description of the binning scheme are included in the README file." |
| Supplemental-material references | `main.tex:355` "…is shown in the Supplemental Material." `:495` "The results without FSI are presented in the Supplemental Material." `:687` (above). `:689` "…fake data studies with alternative generator predictions, which are presented in the Supplemental Material." `:1018` "A simultaneous extraction of the double-differential results … is presented in the Supplemental Material." |
| What is released, and in what form | Supplement sections: Data Release (cross-section tables, `supp.tex:68-80`); acceptance-rejection curves; no-FSI results; 2D extraction; fake data; muon and proton efficiencies (figures, `:411`); covariance matrices (figures, `:439-443`, "They are also included in the DataRelease.root file."); additional smearing matrices (figures, `:497-500`). There is also a ROOT file, `BinScheme.txt` and `README.txt`. `README.txt:8-11` gives the units and bin-width conventions. |
| Repository, DOI, URL or HEPData | None. |

## 2. Counts (n = 7)

| element | count | which |
|---|---|---|
| Section titled "Data Availability" | **0/7** | none |
| A main-text sentence saying where the released numbers are | **4/7** | 2004.05434, 2102.03346 (Conclusions, last paragraph); 2301.03700, 2310.06082 (methods, A_C or "data release … in the Supplemental Material"). All three MINERvA papers have none. |
| Main-text references to "Supplemental/supplementary Material" | **3/7** | 2004.05434 (3), 2301.03700 (3), 2310.06082 (5) |
| A machine-readable release exists (in the source or cited) | **7/7** | MINERvA: arXiv ancillary or source files, unreferenced in the text (3); T2K: collaboration web page (2); MicroBooNE: ROOT file in the supplement (2) |
| Release has cross-section central values | 7/7 | all |
| Release has a covariance matrix | 7/7 | all. Component covariances (stat, flux, energy scale) in 2106 and 2002 only. |
| Release has a correlation matrix (stated) | 1/7 | 2004.05434 |
| Release has binning | 7/7 | bin-mapping or bin-scheme file, or "analysis binning" |
| Release has model predictions | 2/7 | 2106.16210 (17 files), 2002.12496 (SM tables) |
| Release has the flux | 1/7 | 2110.13372 (Table I of its data file) |
| Release has A_C / additional smearing | 2/7 | 2301.03700, 2310.06082 (Wiener-SVD papers only) |
| Release has tabulated efficiencies | 0/7 | efficiency figures only, in 2110 (appendix) and 2310 (SM) |
| A README or usage instructions | 3/7 | 2106 (`anc/README`), 2301 and 2310 (`README.txt`) |
| Form: text or CSV | 3/7 | 2106, 2002, 2110 |
| Form: ROOT | 4/7 | 2106, 2002, 2301, 2310 |
| Form: tables in a supplement document | 3/7 | 2002 (PDF), 2301, 2310 |
| URL cited for the data | 2/7 | both T2K, collaboration web page, cited as a `@misc` "Data release" reference |
| DOI or HEPData cited for the data | **0/7** | none |

## 3. Typical pattern

- **Placement.** No paper in this genre has a Data Availability section in its arXiv text. A statement, where there
  is one, comes in one of two forms:
  - a closing paragraph of the Conclusions that cites a "Data release" reference (T2K);
  - a methods sentence pointing to the Supplemental Material, usually tied to how theorists must use the release
    (MicroBooNE: apply A_C first).

  MINERvA ships the release as arXiv ancillary files with a README and says nothing in the text.
- **What a typical paper releases.** Binned cross-section central values, the full covariance matrix and the binning,
  in machine-readable form (ROOT and/or text). Uncertainties are usually included, and usage conventions often come
  in a README (units, bin-width normalization, unreported bins, global bin numbering). Model predictions, flux,
  correlation matrices and efficiencies are each the exception (at most 2/7). No paper uses HEPData or a DOI.
- **The most typical sentences, verbatim:**
  1. T2K 2102.03346, `ms.tex:1070-1071`: "The data release for the results presented in this analysis is posted in
     Ref.~\cite{data}. It contains the analysis binning, the differential cross section best-fit values, and
     associated covariance matrices."
  2. MicroBooNE 2301.03700, `main.tex:381`: "The data release, the unfolded covariance matrices, and the additional
     matrices $A_{C}$ can be found in the Supplemental Material."
  3. MicroBooNE 2301.03700, `supp.tex:72-73`: "The data release with the data results, the covariance matrices, and
     the additional smearing matrices is included in the DataRelease.root file. Instructions on how to use the data
     release and the description of the binning scheme are included in the README file."

## 4. Caveats

- **arXiv versions only.** No journal version was read, and a journal version may differ. In particular, the APS
  supplement URL replaces "the Supplemental Material" in print. The source of 2002.12496 (`:4-6`) records that its
  PRD version differs from the arXiv version in exactly this respect.
- **All seven predate the PRD Data Availability requirement of 2024-09-04.** The publication dates are:
  - PRD 101 (2020), twice;
  - PRD 103 (2021);
  - PRD 104 (2021-11-19);
  - PRD 106 (2022-08-01);
  - PRD 108 (2023-09-06);
  - PRD 109, 092007 (2024): volume 109 covers January to June 2024, and arXiv v4 is dated 16 May 2024. This placement
    rests on the volume number, and I did not check the APS page.

  None of the seven was therefore bound by the requirement. Their silence is no evidence about current practice, and
  a post-2024-09-04 PRD would need an explicit statement that this corpus cannot model.
- **T2K web-page contents were not verified.** They are reported as the papers describe them, since no web access
  was used.
- **No paper is fully empty.** Every source holds at least one element. The three MINERvA papers have no element in
  their TeX. Their releases are found only in ancillary or source files:
  - 2106: `x/anc/*`;
  - 2002: `x/anc/*`;
  - 2110: `x/supplementalMELowRecoilData.txt_.txt`.

# Records citations of the posted note: classification (thinning batch)

Base: origin/main 563715b8, 71 `\cite{NoteRecords2026}` in the posted note's closure (ids C01-C71 in file order, as in `ctx-before.txt`). Authority: DECISION-20261022-joseph-note-records-refs-and-stop.md, "Thin to essentials".

**Result: 19 KEEP (one of them the guide's single statement), 52 DROP.** Of the KEEPs, 5 were shortened. Tags dropped from kept citations: C04 \texttt{negweight-toy}, C07 \texttt{gbdt-closeout}, C09 \texttt{negweight-audit}.

KEEP: a reader needs the record to verify a number or claim printed at that place. DROP: the pointer only said where history, code or bookkeeping lives; the citation and any clause that only carried it are removed, and no fact or limitation goes with it. `dropped key` is the target the ledger lists for the drop (`records-move-ledger.md` L-thin rows, checked by `check_note_records.py` P6-P8).

| id | file | where | class | dropped key(s) | reason |
|---|---|---|---|---|---|
| C01 | app_guide.tex | guide, records paragraph | KEEP-SHORT | - | the one statement of where records live (Joseph's ruling); rewritten as one plain sentence |
| C02 | app_guide.tex | glossary, J28 row | DROP | superseded values | glossary row; the pointer only says where the superseded J28 products are recorded; App. negweight stays |
| C03 | app_codebase.tex | seedscan paragraph | DROP | \texttt{variance-sources} | code pointers only; the claim (aggregation step, not seedscan) stays |
| C04 | app_negweight.tex | intro, the two provenance limits | KEEP-SHORT | \texttt{negweight-toy} | provenance a result depends on: the twelve production values' limits are checkable only in the durability receipt (negweight-hpss); the toy tag is dropped (the toy record is the deterministic script, not these limits) |
| C05 | app_negweight.tex | estimator section, continuous estimand | DROP | superseded values | the sentence is a mathematical statement; the record is the withdrawn earlier argument |
| C06 | app_negweight.tex | footing, current production | DROP | \texttt{bkg-mode-pins} | code identifier only (STANDARD_BKG_MODE); the claim stays |
| C07 | app_negweight.tex | footing, purity as a recorded choice | KEEP-SHORT | \texttt{gbdt-closeout} | the claims that the choice is recorded, what decided it, and the open obligation are checkable only in the oi6-oi8-oi126 decision record (review S2); gbdt-closeout is dropped, since that entry cites it |
| C08 | app_negweight.tex | what the quoted extended-fiducial number used | DROP | superseded values | the disclosure stays and is explained by the next sentences; the pointer is to the record of the earlier wording |
| C09 | app_negweight.tex | the quoted extended-fiducial number | KEEP-SHORT | \texttt{negweight-audit} | provenance of a quoted number: sigma_ext comes from this battery (job, launchers, default mode), checkable only in fps-battery; the audit-finding tag (how the defect was found) is dropped |
| C10 | app_negweight.tex | extended-fiducial designated treatment | DROP | \texttt{bkg-mode-pins} | code identifier only (PUBLICATION_BKG_MODE); the claim and the run-stopping check stay |
| C11 | app_negweight.tex | scope of the 2D agreement | DROP | superseded values | the limitation stays; the pointer is to the withdrawn earlier argument |
| C12 | app_negweight.tex | background treatment and choice of covariance | DROP | \texttt{p4-verifier} | process record (the P4 verifier directory); the claim stays |
| C13 | app_statmethods_nd.tex | N-D declarations | KEEP | - | the rank 263 of 10,694 bins and the 40x/18x understatement are measurements whose derivation and the predeclared rank cut are printed only in the record |
| C14 | app_release.tex | intro | DROP | (whole) | says only where the records live (now said once, in the guide); the checksums keep their pointer in the schema lead (C15) |
| C15 | app_release.tex | schema lead | KEEP | - | the checkmarks claim identities are fixed; the checksums that fix them are printed only in the records' identity table |
| C16 | app_release.tex | schema item 7, generator predictions | DROP | \texttt{flux-repair} | the flux repair is described, with its one kept citation, in sec:3d-models (C29), which stays cited here |
| C17 | app_release.tex | schema item 8, provenance | DROP | identities already fixed | the same identity table is cited by the schema lead (C15) a few lines above |
| C18 | app_statmethods.tex | Table tab:variance-sources caption | DROP | \texttt{variance-sources} | code pointers only |
| C19 | app_statmethods.tex | universes, the band sum | DROP | \texttt{rvp1pi} | tracker row only; the reason (same shift as Rvn1pi) is printed in sec:uq-universes and sec:uq-2d-construction |
| C20 | app_statmethods.tex | grouped medians | DROP | superseded values: struck values | points to the struck legacy-grouping row, a pure record (the posted note is a first public version, L17) |
| C21 | app_statmethods.tex | MAT cross-check of the earlier sweep | DROP | superseded values: struck values | the limitation (older sweep, not a quoted product, could not detect the omission) stays in full |
| C22 | app_statmethods.tex | chi2 limit (ii) | KEEP | - | prints 1.47, a value computed with an earlier covariance; its provenance is only in the records |
| C23 | app_statmethods.tex | rank, remaining candidates | KEEP | - | the claim (the split bootstrap separated two explanations from an MC-statistics omission) rests on the split-bootstrap numbers printed only in the records |
| C24 | app_statmethods.tex | Data/MC split bootstrap paragraph | DROP | superseded values: retired material | the clause says only where the split bootstrap's closure, data stream and structure comparison are; C23 cites the same record four lines above; the records print all three |
| C25 | app_statmethods.tex | ours-only chi2 convention | DROP | superseded values: superseded uncertainty constructions | the convention is stated; the pointer is to the history of the earlier scan |
| C26 | app_statmethods.tex | tension footnote, POT ratio | DROP | \texttt{pot-ratio} | tracker row only; the fact and the per-playlist range are printed |
| C27 | app_statmethods.tex | closure thresholds | KEEP | - | relies on a superseded value, the 0.166% floor of the earlier ten-seed scan, printed in the records |
| C28 | app_statmethods.tex | closure procedures | DROP | \texttt{closure-scripts} | script paths only |
| C29 | sec_3d.tex | flux repair of the GENIE and NuWro predictions | KEEP | - | every generator comparison of Secs. 3d and eavailw rests on this repair; its tracker rows, ledger rows and receipt are only in the records |
| C30 | sec_3d.tex | flux repair, figure code | DROP | superseded values | points to the pre-repair values, which the sentence does not use |
| C31 | sec_3d.tex | Fig. 3dmodels caption | DROP | superseded values | the caption's statement stands; the pointer is to the caption's earlier fuller wording |
| C32 | sec_3d.tex | no 3D covariance quoted | DROP | superseded values | the statement stands; the pointer is to the superseded 3D material |
| C33 | sec_3d.tex | 2p2h closes the gap | DROP | superseded values | the printed values are current (VL160); the pointer is to the pre-repair 27%/64% fractions, which the sentence does not use |
| C34 | sec_3d.tex | high-Eavail bin | DROP | superseded values | data/CV 1.09 is the current value; the pointer is to the pre-repair 1.15, which the sentence does not use |
| C35 | sec_3d.tex | Fig. modedecomp caption | DROP | superseded values | as C31 |
| C36 | sec_3d.tex | Fig. mec caption | DROP | superseded values | as C31 |
| C37 | sec_3d.tex | q3 excess map | DROP | \texttt{q3-excess} | script path only |
| C38 | sec_3d.tex | Fig. ascencio caption | DROP | superseded values | as C31 |
| C39 | sec_method.tex | central value at seed 42 | KEEP-SHORT | - | identity of the quoted 2D central value: its file name and sha256 are printed only in the record |
| C40 | sec_method.tex | binning, bin-mapping file | DROP | \texttt{bin-mapping} | the published release is cited directly; the record adds only the repository path |
| C41 | sec_joint.tex | section lead | DROP | \texttt{joint-5d} | the specification and decisions are cited to Ref. JointTestRecord2026 in the same paragraph; the clause it was attached to (no reportable uncertainty) needs no record |
| C42 | sec_eavailw.tex | Fig. eavailWexcess caption | DROP | \texttt{eavailw-excess} | script path only; the units are stated |
| C43 | sec_eavailw.tex | generator band, flux repair | DROP | \texttt{flux-repair} | the repair is described and cited once in sec:3d-models (C29), referenced here |
| C44 | sec_eavailw.tex | generator band, normalization | DROP | superseded values | the current convention is stated; the pointer is to the removed 3% and 2.87% pre-repair differences |
| C45 | sec_results.tex | flux band | DROP | superseded values: struck values | points to the struck 6.871% row, a pure record (L9: the posted note is a first public version) |
| C46 | sec_5d.tex | binned response diagnostic | KEEP | - | the diagnostic's exclusions, definitions and numerical verification are only in its record |
| C47 | sec_5d.tex | status of the five-axis covariance | KEEP | - | the identity of the object every quoted 5D uncertainty is computed from; the checksums (and the metadata fields) are printed in the records' identity table |
| C48 | sec_5d.tex | status, the metadata | DROP | construction and audit record | the identity table cited one sentence earlier (C47) prints the same metadata fields (NON-PASSING, adoptable: false); the claim stays |
| C49 | sec_5d.tex | status, the earlier direct block sum | DROP | superseded values: the earlier direct $(\Eavail,W)$ block sum | the whole sentence is a pure record (a superseded construction, quoted nowhere); the records print it at this heading, including that it is quoted nowhere in this note. The comment that kept it verbatim gave the ledger probe L12 as its reason; L12 is updated in this batch |
| C50 | sec_5d.tex | construction, band groups | DROP | construction and audit record | implementation pointer only; the requirement stays |
| C51 | sec_5d.tex | centering, variant identity | DROP | construction and audit record | the claim stays; the record adds the projector's flag names (software detail) |
| C52 | sec_5d.tex | projection, symmetry | DROP | construction and audit record | checkable from the released file; the claim stays |
| C53 | sec_5d.tex | conditioning, no implicit regularization | DROP | construction and audit record | the statement stands; nothing in it needs the record |
| C54 | sec_5d.tex | estimator-seed magnitude criterion | KEEP | - | the limitation (computed only for the two companion covariances) is checkable only in the adoption record and its campaign |
| C55 | sec_intro.tex | roadmap, five-axis covariance row | DROP | (whole) | roadmap pointer outside the note; the section, which cites what it needs, stays |
| C56 | sec_intro.tex | roadmap, records row | DROP | (whole) | the roadmap lists the note's sections; where the records live is now said once, in the guide |
| C57 | sec_systematics.tex | lead, 3D budget | DROP | superseded values: the historical 3D uncertainty budget | the statement (not quoted) stands; the pointer is to the historical budget |
| C58 | sec_systematics.tex | universes, Rvp1pi | DROP | \texttt{rvp1pi} | tracker row only; the reason is printed and sec:uq-2d-construction is cited |
| C59 | sec_systematics.tex | flux 1/Phi normalization | DROP | superseded values: retired material | the whole sentence only says where the earlier budget's superseded values are; the records print them (4.99% without the constraint weights, about 1% with the CV Phi) |
| C60 | sec_systematics.tex | bootstrap, coverage | DROP | superseded values: retired material, \texttt{coverage-fixed-truth} | the sentence only says where the earlier bootstrap's split streams and the band identities are; the records print both |
| C61 | sec_systematics.tex | bootstrap, no held-out re-test | DROP | \texttt{statband-retest} | the limitation stays; the record is the tracker row of the deferral |
| C62 | sec_systematics.tex | learner dependence | KEEP | - | the 0.99% is measured against the earlier ten-seed scan, a retired product printed only in the records |
| C63 | sec_systematics.tex | construction limits, Rvp1pi | DROP | \texttt{rvp1pi} | tracker row only; the defect, its size and the fix are printed |
| C64 | sec_systematics.tex | flux-universe index identity | KEEP | - | prints the numbers of an exact test (900 x 100, 5.5e-14, >= 0.245) whose record is the only source |
| C65 | sec_systematics.tex | earlier 5D candidate constructions | DROP | superseded values: the superseded 5D candidate unified-throw constructions | the statement (neither used, no magnitude quoted) stands; the pointer is to the superseded constructions |
| C66 | sec_systematics.tex | background-CV choice | KEEP | - | the 0.28% and 0.18% are ratios whose reference products are identified only in the records (taken against superseded products, so they are a bound); the pointer carries that scope |
| C67 | sec_validation.tex | fixed-truth coverage, which band | DROP | superseded values, \texttt{coverage-fixed-truth} | the claim stays; the band's identity is in coverage-fixed-truth, cited in the next sentence (C68) |
| C68 | sec_validation.tex | fixed-truth coverage, pre-registration | KEEP | - | a pre-registration claim: the design, criteria and positive control fixed before any toy are checkable only in the pre-registration and its amendments |
| C69 | sec_validation.tex | fixed-truth coverage, the rebuild | DROP | \texttt{coverage-fixed-truth} | history pointer (the record names both bands); C68 cites the same tag |
| C70 | sec_validation.tex | post hoc rescoring, held-out re-test | DROP | \texttt{statband-retest} | the limitation stays; the record is the tracker row of the deferral |
| C71 | sec_validation.tex | same-ensemble pull diagnostic | KEEP | - | the record (coverage_summary.txt) is the only source of the pull numbers printed two sentences later (68.50%, +0.006 +- 0.082 sigma, 97.6%, 5 of 205), as for C64 (review S5) |

## The KEEP list

- **C01** `app_guide.tex`, guide, records paragraph: the one statement of where records live (Joseph's ruling); rewritten as one plain sentence.
- **C04** `app_negweight.tex`, intro, the two provenance limits: provenance a result depends on: the twelve production values' limits are checkable only in the durability receipt (negweight-hpss); the toy tag is dropped (the toy record is the deterministic script, not these limits).
- **C07** `app_negweight.tex`, footing, purity as a recorded choice: the claims that the choice is recorded, what decided it, and the open obligation are checkable only in the oi6-oi8-oi126 decision record (review S2); gbdt-closeout is dropped, since that entry cites it.
- **C09** `app_negweight.tex`, the quoted extended-fiducial number: provenance of a quoted number: sigma_ext comes from this battery (job, launchers, default mode), checkable only in fps-battery; the audit-finding tag (how the defect was found) is dropped.
- **C13** `app_statmethods_nd.tex`, N-D declarations: the rank 263 of 10,694 bins and the 40x/18x understatement are measurements whose derivation and the predeclared rank cut are printed only in the record.
- **C15** `app_release.tex`, schema lead: the checkmarks claim identities are fixed; the checksums that fix them are printed only in the records' identity table.
- **C22** `app_statmethods.tex`, chi2 limit (ii): prints 1.47, a value computed with an earlier covariance; its provenance is only in the records.
- **C23** `app_statmethods.tex`, rank, remaining candidates: the claim (the split bootstrap separated two explanations from an MC-statistics omission) rests on the split-bootstrap numbers printed only in the records.
- **C27** `app_statmethods.tex`, closure thresholds: relies on a superseded value, the 0.166% floor of the earlier ten-seed scan, printed in the records.
- **C29** `sec_3d.tex`, flux repair of the GENIE and NuWro predictions: every generator comparison of Secs. 3d and eavailw rests on this repair; its tracker rows, ledger rows and receipt are only in the records.
- **C39** `sec_method.tex`, central value at seed 42: identity of the quoted 2D central value: its file name and sha256 are printed only in the record.
- **C46** `sec_5d.tex`, binned response diagnostic: the diagnostic's exclusions, definitions and numerical verification are only in its record.
- **C47** `sec_5d.tex`, status of the five-axis covariance: the identity of the object every quoted 5D uncertainty is computed from; the checksums (and the metadata fields) are printed in the records' identity table.
- **C54** `sec_5d.tex`, estimator-seed magnitude criterion: the limitation (computed only for the two companion covariances) is checkable only in the adoption record and its campaign.
- **C62** `sec_systematics.tex`, learner dependence: the 0.99% is measured against the earlier ten-seed scan, a retired product printed only in the records.
- **C64** `sec_systematics.tex`, flux-universe index identity: prints the numbers of an exact test (900 x 100, 5.5e-14, >= 0.245) whose record is the only source.
- **C66** `sec_systematics.tex`, background-CV choice: the 0.28% and 0.18% are ratios whose reference products are identified only in the records (taken against superseded products, so they are a bound); the pointer carries that scope.
- **C68** `sec_validation.tex`, fixed-truth coverage, pre-registration: a pre-registration claim: the design, criteria and positive control fixed before any toy are checkable only in the pre-registration and its amendments.
- **C71** `sec_validation.tex`, same-ensemble pull diagnostic: the record (coverage_summary.txt) is the only source of the pull numbers printed two sentences later (68.50%, +0.006 +- 0.082 sigma, 97.6%, 5 of 205), as for C64 (review S5).

# Changes (thinning batch): before, after and reason, per citation

Printed text (comments stripped, whitespace collapsed). KEEP entries left unchanged are listed only in `citations.md`.

## C01 app_guide.tex, guide, records paragraph (KEEP-SHORT)

- before: The note's records --- the provenance of the repository records it cites, the fixed-identity table and audit record of the five-axis covariance, the test-suite discipline, and the superseded values and withdrawn arguments --- are kept in a separate internal records document, Ref.~\cite{NoteRecords2026}, which is not part of this note; the note cites its entries by tag or by heading.
- after: The provenance of the records the note cites, the fixed identities and audit record of the five-axis covariance, the test-suite discipline, and superseded values and withdrawn results are kept in the analysis repository's records document, Ref.~\cite{NoteRecords2026}; each citation names the entry's tag or heading.
- reason: the one statement of where records live (Joseph's ruling); rewritten as one plain sentence

## C02 app_guide.tex, glossary, J28 row (DROP)

- before: (App.~\ref{app:negweight}; Ref.~\cite{NoteRecords2026}, superseded values) \\
- after: (App.~\ref{app:negweight}) \\
- reason: glossary row; the pointer only says where the superseded J28 products are recorded; App. negweight stays

## C03 app_codebase.tex, seedscan paragraph (DROP)

- before: production (Ref.~\cite{NoteRecords2026}, \texttt{variance-sources}), not by the \texttt{seedscan} scripts.
- after: production, not by the \texttt{seedscan} scripts.
- reason: code pointers only; the claim (aggregation step, not seedscan) stays

## C04 app_negweight.tex, intro, the two provenance limits (KEEP-SHORT)

- before: and no output records the job that produced it. Their records are in Ref.~\cite{NoteRecords2026} (\texttt{negweight-hpss}, \texttt{negweight-toy}).
- after: and no output records the job that produced it (Ref.~\cite{NoteRecords2026}, \texttt{negweight-hpss}).
- reason: provenance a result depends on: the twelve production values' limits are checkable only in the durability receipt (negweight-hpss); the toy tag is dropped (the toy record is the deterministic script, not these limits)

## C05 app_negweight.tex, estimator section, continuous estimand (DROP)

- before: $r^{\star}(x)=(D(x)-B(x))/S(x)$ (Ref.~\cite{NoteRecords2026}, superseded values).
- after: $r^{\star}(x)=(D(x)-B(x))/S(x)$.
- reason: the sentence is a mathematical statement; the record is the withdrawn earlier argument

## C06 app_negweight.tex, footing, current production (DROP)

- before: configuration object that rejects every other mode (Ref.~\cite{NoteRecords2026}, \texttt{bkg-mode-pins}). The standard
- after: configuration object that rejects every other mode. The standard
- reason: code identifier only (STANDARD_BKG_MODE); the claim stays

## C07 app_negweight.tex, footing, purity as a recorded choice (KEEP-SHORT)

- before: Purity is \textbf{a recorded choice, not a silent default} (Ref.~\cite{NoteRecords2026}, \texttt{gbdt-closeout} and \texttt{oi6-oi8-oi126}), made on two grounds.
- after: Purity is \textbf{a recorded choice, not a silent default} (Ref.~\cite{NoteRecords2026}, \texttt{oi6-oi8-oi126}), made on two grounds.
- reason: the claims that the choice is recorded, what decided it, and the open obligation are checkable only in the oi6-oi8-oi126 decision record (review S2); gbdt-closeout is dropped, since that entry cites it

## C08 app_negweight.tex, what the quoted extended-fiducial number used (DROP)

- before: was not produced with negative-weight injection (Ref.~\cite{NoteRecords2026}, superseded values).
- after: was not produced with negative-weight injection.
- reason: the disclosure stays and is explained by the next sentences; the pointer is to the record of the earlier wording

## C09 app_negweight.tex, the quoted extended-fiducial number (KEEP-SHORT)

- before: (Ref.~\cite{NoteRecords2026}, \texttt{fps-battery}, \texttt{negweight-audit}). The
- after: (Ref.~\cite{NoteRecords2026}, \texttt{fps-battery}). The
- reason: provenance of a quoted number: sigma_ext comes from this battery (job, launchers, default mode), checkable only in fps-battery; the audit-finding tag (how the defect was found) is dropped

## C10 app_negweight.tex, extended-fiducial designated treatment (DROP)

- before: The code fixes it (Ref.~\cite{NoteRecords2026}, \texttt{bkg-mode-pins}), and a check
- after: The code fixes it, and a check
- reason: code identifier only (PUBLICATION_BKG_MODE); the claim and the run-stopping check stay

## C11 app_negweight.tex, scope of the 2D agreement (DROP)

- before: identical (Ref.~\cite{NoteRecords2026}, superseded values), and covariance
- after: identical, and covariance
- reason: the limitation stays; the pointer is to the withdrawn earlier argument

## C12 app_negweight.tex, background treatment and choice of covariance (DROP)

- before: using a component in place (Ref.~\cite{NoteRecords2026}, \texttt{p4-verifier}).
- after: using a component in place.
- reason: process record (the P4 verifier directory); the claim stays

## C14 app_release.tex, intro (DROP)

- before: Rebuilding this note's PDFs assembles documents; it does not reproduce scientific results. The supporting internal records, including the checksums of the fixed identities, are kept in Ref.~\cite{NoteRecords2026}.
- after: Rebuilding this note's PDFs assembles documents; it does not reproduce scientific results.
- reason: says only where the records live (now said once, in the guide); the checksums keep their pointer in the schema lead (C15)

## C16 app_release.tex, schema item 7, generator predictions (DROP)

- before: (Ref.~\cite{NoteRecords2026}, \texttt{flux-repair}; \S\ref{sec:3d-models}).
- after: (\S\ref{sec:3d-models}).
- reason: the flux repair is described, with its one kept citation, in sec:3d-models (C29), which stays cited here

## C17 app_release.tex, schema item 8, provenance (DROP)

- before: checksum are fixed (Ref.~\cite{NoteRecords2026}, identities already fixed). No producing
- after: checksum are fixed. No producing
- reason: the same identity table is cited by the schema lead (C15) a few lines above

## C18 app_statmethods.tex, Table tab:variance-sources caption (DROP)

- before: \caption{Variance-source procedures for the 2D measurement ($205$ reported bins). Code pointers: Ref.~\cite{NoteRecords2026} (\texttt{variance-sources}).}
- after: \caption{Variance-source procedures for the 2D measurement ($205$ reported bins).}
- reason: code pointers only

## C19 app_statmethods.tex, universes, the band sum (DROP)

- before: drops Rvp1pi (Ref.~\cite{NoteRecords2026}, \texttt{rvp1pi}) and holds
- after: drops Rvp1pi and holds
- reason: tracker row only; the reason (same shift as Rvn1pi) is printed in sec:uq-universes and sec:uq-2d-construction

## C20 app_statmethods.tex, grouped medians (DROP)

- before: Run period $2.137\%$ (Ref.~\cite{NoteRecords2026}, superseded values: struck values).
- after: Run period $2.137\%$.
- reason: points to the struck legacy-grouping row, a pure record (the posted note is a first public version, L17)

## C21 app_statmethods.tex, MAT cross-check of the earlier sweep (DROP)

- before: sweep from before the flux fix (Ref.~\cite{NoteRecords2026}, superseded values: struck values), not on a quoted product
- after: sweep from before the flux fix, not on a quoted product
- reason: the limitation (older sweep, not a quoted product, could not detect the omission) stays in full

## C24 app_statmethods.tex, Data/MC split bootstrap paragraph (DROP)

- before: The data/MC split bootstrap was run on the earlier rebuilt bootstrap; its closure, its data-only stream and its structure comparison are given in Ref.~\cite{NoteRecords2026}, superseded values: retired material. For the quoted
- after: The data/MC split bootstrap was run on the earlier rebuilt bootstrap. For the quoted
- reason: the clause says only where the split bootstrap's closure, data stream and structure comparison are; C23 cites the same record four lines above; the records print all three

## C25 app_statmethods.tex, ours-only chi2 convention (DROP)

- before: over all $1431$ reported bins (Ref.~\cite{NoteRecords2026}, superseded values: superseded uncertainty constructions).
- after: over all $1431$ reported bins.
- reason: the convention is stated; the pointer is to the history of the earlier scan

## C26 app_statmethods.tex, tension footnote, POT ratio (DROP)

- before: ratio (Ref.~\cite{NoteRecords2026}, \texttt{pot-ratio}); per-playlist
- after: ratio; per-playlist
- reason: tracker row only; the fact and the per-playlist range are printed

## C28 app_statmethods.tex, closure procedures (DROP)

- before: procedures and otherwise unreported values follow (scripts: Ref.~\cite{NoteRecords2026}, \texttt{closure-scripts}).
- after: procedures and otherwise unreported values follow.
- reason: script paths only

## C30 sec_3d.tex, flux repair, figure code (DROP)

- before: figure code from the repaired inputs (Ref.~\cite{NoteRecords2026}, superseded values).
- after: figure code from the repaired inputs.
- reason: points to the pre-repair values, which the sentence does not use

## C31 sec_3d.tex, Fig. 3dmodels caption (DROP)

- before: Data have no error bars because the 3D covariance that would be quoted is not used for any result in this note (Ref.~\cite{NoteRecords2026}, superseded values).}
- after: Data have no error bars because the 3D covariance that would be quoted is not used for any result in this note.}
- reason: the caption's statement stands; the pointer is to the caption's earlier fuller wording

## C32 sec_3d.tex, no 3D covariance quoted (DROP)

- before: computed but is not used for any result in this note (Ref.~\cite{NoteRecords2026}, superseded values).
- after: computed but is not used for any result in this note.
- reason: the statement stands; the pointer is to the superseded 3D material

## C33 sec_3d.tex, 2p2h closes the gap (DROP)

- before: (CV $-\SI{7.2}{\percent}\to-\SI{2.6}{\percent}$; Ref.~\cite{NoteRecords2026}, superseded values). The prediction
- after: (CV $-\SI{7.2}{\percent}\to-\SI{2.6}{\percent}$). The prediction
- reason: the printed values are current (VL160); the pointer is to the pre-repair 27%/64% fractions, which the sentence does not use

## C34 sec_3d.tex, high-Eavail bin (DROP)

- before: (data/CV $1.09$; Ref.~\cite{NoteRecords2026}, superseded values) and exceed
- after: (data/CV $1.09$) and exceed
- reason: data/CV 1.09 is the current value; the pointer is to the pre-repair 1.15, which the sentence does not use

## C35 sec_3d.tex, Fig. modedecomp caption (DROP)

- before: populate. Data carry no error bars because the 3D covariance that would be quoted is not used for any result in this note (Ref.~\cite{NoteRecords2026}, superseded values).}
- after: populate. Data carry no error bars because the 3D covariance that would be quoted is not used for any result in this note.}
- reason: as C31

## C36 sec_3d.tex, Fig. mec caption (DROP)

- before: error bars because the 3D covariance that would be quoted is not used for any result in this note (Ref.~\cite{NoteRecords2026}, superseded values).}
- after: error bars because the 3D covariance that would be quoted is not used for any result in this note.}
- reason: as C31

## C37 sec_3d.tex, q3 excess map (DROP)

- before: prior, distinct from the untuned GENIE sample of \S\ref{sec:3d-2p2h} (Ref.~\cite{NoteRecords2026}, \texttt{q3-excess}). No per-cell
- after: prior, distinct from the untuned GENIE sample of \S\ref{sec:3d-2p2h}. No per-cell
- reason: script path only

## C38 sec_3d.tex, Fig. ascencio caption (DROP)

- before: not used for any result in this note (Ref.~\cite{NoteRecords2026}, superseded values); the
- after: not used for any result in this note; the
- reason: as C31

## C39 sec_method.tex, central value at seed 42 (KEEP-SHORT)

- before: (its file name and checksum are listed in Ref.~\cite{NoteRecords2026}, \texttt{2d-central-value})
- after: (Ref.~\cite{NoteRecords2026}, \texttt{2d-central-value})
- reason: identity of the quoted 2D central value: its file name and sha256 are printed only in the record

## C40 sec_method.tex, binning, bin-mapping file (DROP)

- before: release~\cite{MINERvA:2021owq} (Ref.~\cite{NoteRecords2026}, \texttt{bin-mapping}).
- after: release~\cite{MINERvA:2021owq}.
- reason: the published release is cited directly; the record adds only the repository path

## C41 sec_joint.tex, section lead (DROP)

- before: add no reportable uncertainty (Ref.~\cite{NoteRecords2026}, \texttt{joint-5d}), and do not validate
- after: add no reportable uncertainty, and do not validate
- reason: the specification and decisions are cited to Ref. JointTestRecord2026 in the same paragraph; the clause it was attached to (no reportable uncertainty) needs no record

## C42 sec_eavailw.tex, Fig. eavailWexcess caption (DROP)

- before: in \si{cm^2/nucleon} (Ref.~\cite{NoteRecords2026}, \texttt{eavailw-excess}), so the catch-bin
- after: in \si{cm^2/nucleon}, so the catch-bin
- reason: script path only; the units are stated

## C43 sec_eavailw.tex, generator band, flux repair (DROP)

- before: flux-repaired as in \S\ref{sec:3d-models} (Ref.~\cite{NoteRecords2026}, \texttt{flux-repair}).
- after: flux-repaired as in \S\ref{sec:3d-models}.
- reason: the repair is described and cited once in sec:3d-models (C29), referenced here

## C44 sec_eavailw.tex, generator band, normalization (DROP)

- before: convention of the 3D comparison (Ref.~\cite{NoteRecords2026}, superseded values).
- after: convention of the 3D comparison.
- reason: the current convention is stated; the pointer is to the removed 3% and 2.87% pre-repair differences

## C45 sec_results.tex, flux band (DROP)

- before: constraint weights (Ref.~\cite{NoteRecords2026}, superseded values: struck values). The
- after: constraint weights. The
- reason: points to the struck 6.871% row, a pure record (L9: the posted note is a first public version)

## C48 sec_5d.tex, status, the metadata (DROP)

- before: as not passing and as not to be used (Ref.~\cite{NoteRecords2026}, construction and audit record). It is used
- after: as not passing and as not to be used. It is used
- reason: the identity table cited one sentence earlier (C47) prints the same metadata fields (NON-PASSING, adoptable: false); the claim stays

## C49 sec_5d.tex, status, the earlier direct block sum (DROP)

- before: The earlier direct 42-bin $(\Eavail,W)$ block sum is superseded and quoted nowhere in this note (Ref.~\cite{NoteRecords2026}, superseded values: the earlier direct $(\Eavail,W)$ block sum).
- after: (removed)
- reason: the whole sentence is a pure record (a superseded construction, quoted nowhere); the records print it at this heading, including that it is quoted nowhere in this note. The comment that kept it verbatim gave the ledger probe L12 as its reason; L12 is updated in this batch

## C50 sec_5d.tex, construction, band groups (DROP)

- before: exhaust the 45 bands (implementation in Ref.~\cite{NoteRecords2026}, construction and audit record). The same
- after: exhaust the 45 bands. The same
- reason: implementation pointer only; the requirement stays

## C51 sec_5d.tex, centering, variant identity (DROP)

- before: not by its path (Ref.~\cite{NoteRecords2026}, construction and audit record).
- after: not by its path.
- reason: the claim stays; the record adds the projector's flag names (software detail)

## C52 sec_5d.tex, projection, symmetry (DROP)

- before: exactly symmetric (Ref.~\cite{NoteRecords2026}, construction and audit record). Support
- after: exactly symmetric. Support
- reason: checkable from the released file; the claim stays

## C53 sec_5d.tex, conditioning, no implicit regularization (DROP)

- before: applied implicitly (Ref.~\cite{NoteRecords2026}, construction and audit record).
- after: applied implicitly.
- reason: the statement stands; nothing in it needs the record

## C55 sec_intro.tex, roadmap, five-axis covariance row (DROP)

- before: \S\ref{sec:eavailw-construction}; audit record Ref.~\cite{NoteRecords2026} \\
- after: \S\ref{sec:eavailw-construction} \\
- reason: roadmap pointer outside the note; the section, which cites what it needs, stays

## C56 sec_intro.tex, roadmap, records row (DROP)

- before: Provenance of records, fixed identities, superseded values and withdrawn arguments & internal records, Ref.~\cite{NoteRecords2026} \\
- after: (removed)
- reason: the roadmap lists the note's sections; where the records live is now said once, in the guide

## C57 sec_systematics.tex, lead, 3D budget (DROP)

- before: is not quoted (Ref.~\cite{NoteRecords2026}, superseded values: the historical 3D uncertainty budget), and no 4D
- after: is not quoted, and no 4D
- reason: the statement (not quoted) stands; the pointer is to the historical budget

## C58 sec_systematics.tex, universes, Rvp1pi (DROP)

- before: (\S\ref{sec:uq-2d-construction}; Ref.~\cite{NoteRecords2026}, \texttt{rvp1pi}), and holds
- after: (\S\ref{sec:uq-2d-construction}), and holds
- reason: tracker row only; the reason is printed and sec:uq-2d-construction is cited

## C59 sec_systematics.tex, flux 1/Phi normalization (DROP)

- before: of \SI{\uqMedian}{\percent}. The earlier budget's values without the constraint weights and with the CV $\Phi$ are in Ref.~\cite{NoteRecords2026}, superseded values: retired material.
- after: of \SI{\uqMedian}{\percent}.
- reason: the whole sentence only says where the earlier budget's superseded values are; the records print them (4.99% without the constraint weights, about 1% with the CV Phi)

## C60 sec_systematics.tex, bootstrap, coverage (DROP)

- before: The split data/MC streams of that earlier, rebuilt bootstrap are in Ref.~\cite{NoteRecords2026}, superseded values: retired material, and \texttt{coverage-fixed-truth}. The rebuilt band was
- after: The rebuilt band was
- reason: the sentence only says where the earlier bootstrap's split streams and the band identities are; the records print both

## C61 sec_systematics.tex, bootstrap, no held-out re-test (DROP)

- before: registered in advance (Ref.~\cite{NoteRecords2026}, \texttt{statband-retest}). Because
- after: registered in advance. Because
- reason: the limitation stays; the record is the tracker row of the deferral

## C63 sec_systematics.tex, construction limits, Rvp1pi (DROP)

- before: counts the shift once (Ref.~\cite{NoteRecords2026}, \texttt{rvp1pi}).
- after: counts the shift once.
- reason: tracker row only; the defect, its size and the fix are printed

## C65 sec_systematics.tex, earlier 5D candidate constructions (DROP)

- before: no magnitude from either is quoted (Ref.~\cite{NoteRecords2026}, superseded values: the superseded 5D candidate unified-throw constructions).
- after: no magnitude from either is quoted.
- reason: the statement (neither used, no magnitude quoted) stands; the pointer is to the superseded constructions

## C67 sec_validation.tex, fixed-truth coverage, which band (DROP)

- before: That band is an earlier one (Ref.~\cite{NoteRecords2026}, superseded values and \texttt{coverage-fixed-truth}), not the quoted
- after: That band is an earlier one, not the quoted
- reason: the claim stays; the band's identity is in coverage-fixed-truth, cited in the next sentence (C68)

## C69 sec_validation.tex, fixed-truth coverage, the rebuild (DROP)

- before: The band was then rebuilt without this term (Ref.~\cite{NoteRecords2026}, \texttt{coverage-fixed-truth}, names both bands). The quoted
- after: The band was then rebuilt without this term. The quoted
- reason: history pointer (the record names both bands); C68 cites the same tag

## C70 sec_validation.tex, post hoc rescoring, held-out re-test (DROP)

- before: it has not been run (Ref.~\cite{NoteRecords2026}, \texttt{statband-retest}). Split-sample
- after: it has not been run. Split-sample
- reason: the limitation stays; the record is the tracker row of the deferral

## Comment-only edit

- sec_intro.tex: the roadmap's source comment now says the records row and the audit-record pointer were dropped by this batch.

## Check files

- `check_note_records.py`: D: probes, P6 drop allowance, P7 target check (tree and HEAD), P8 exact count against THIN_BASE 563715b8, verdict SKIP (exit 0) when P8 cannot run, eleven new self-test plants (nine fire, two silent, including a kept citation moved within its file), the lost-tag-pointer plant moved from sec_joint.tex (no citation left) to app_statmethods_nd.tex.
- `records-move-ledger.md`: 16 earlier rows repointed (L1, L3, L4, L5, L9-L13, L15, L17, L18, L-sec_results, L-sec_eavailw, L-sec_joint, L-app_codebase); 71 L-thin rows appended, one per base citation (a kept citation's row pins it to its sentence).
- `README.md:137`: the checker row names the thinning and that probe and self-test run in the canonical checkout (reviewer's wording, S4).

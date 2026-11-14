# Note statements whose only support is an unreleased record (history restructure, 2026-11-13)

The director's list (2026-11-13), for Joseph's decision at the end of the restructure: put the records in the Zenodo deposit, or change the statements. This file lists them and changes nothing.

**How it was built:**
- Every printed sentence of the note's inputs (`main_note.tex` and each `\input` file, LaTeX comments stripped) is split at sentence ends.
- A sentence is listed when it cites one of the records below and cites nothing else. "Only support" is read here as "no other citation in the sentence"; a sentence may also lean on a `\ref` to the note's own text, which this does not test.
- Line numbers are at branch head a4cec8757, and are re-measured at each later section.
- Sites: 33 in all, and every one cites only these records.

**The records:**
- [34] NoteRecords2026: "Internal record of the MINERvA-OmniFold repository, not posted" (technote.bib:1014-1019). It is built from `main_records.tex` and is never posted. This is the referee's Ref. [34].
- [31] UnfoldedWeightsESS2026, [39] TwoDFollowup2026, [53] JointTestRecord2026, [57] JointTestKappa2026, [58] JointTestRecovery2026, [59] JointTestProjections2026, [61] JointTestRecoil2026, [98] ReleaseCandidate2026 and [99] AnaTuplePreservation2026: "MINERvA-OmniFold repository record". Each is a commit-pinned GitHub URL to a file in the repository. It is readable where the repository is, but not deposited.

## Not posted: NoteRecords2026 [34] (22 sites)

| file:line | ref | sentence (as printed source, comments stripped) |
|---|---|---|
| `sec_method.tex:48` | [34] NoteRecords2026 | An independent rerun reproduces it to $1.4\times10^{-11}$, and so does a regeneration whose run configuration is recorded (Ref.~\cite{NoteRecords2026}, \recentry{2d-central-value}). |
| `sec_systematics.tex:121` | [34] NoteRecords2026 | Seven universes of the sweep used by the quoted universe block (\S\ref{sec:uq-universes}) are reproduced to $\le1.4\times10^{-11}$ by the committed driver; the others are accepted by inference, becaus |
| `sec_systematics.tex:143` | [34] NoteRecords2026 | The flux-universe index identity behind the $1/\Phi_{u}$ rescale is established by the code chain and by an exact test: 900 events $\times$ 100 universes match to $5.5\times10^{-14}$, and a control sh |
| `sec_systematics.tex:332` | [34] NoteRecords2026 | Subtracting the background separately in each of the 187 universe unfolds and in the CV changes the square-root trace of the combined block sum by \SI{0.28}{\percent} and $C_Z$ by \SI{0.18}{\percent}, |
| `sec_validation.tex:137` | [34] NoteRecords2026 | The design, criteria and positive control of the test were specified before any toy was generated (Ref.~\cite{NoteRecords2026}, \recentry{coverage-fixed-truth}). |
| `sec_validation.tex:228` | [34] NoteRecords2026 | \paragraph{Same-ensemble pull diagnostic (not a coverage test).} An earlier ensemble of $N_{\text{toy}}=200$ 2D closure unfolds (Ref.~\cite{NoteRecords2026}, \recentry{coverage-toys}) uses weighted MC |
| `sec_3d.tex:133` | [34] NoteRecords2026 | \paragraph{Flux repair and normalization.} The GENIE (CV and $+$Valencia~2p2h) and NuWro samples were generated from a flux that had no PPFX weights, was capped at \SI{50}{GeV}, and stored flux \emph{ |
| `sec_eavailw.tex:70` | [34] NoteRecords2026 | For GENIE with MEC, NuWro and GiBUU its effect is not reliably determined (Ref.~\cite{NoteRecords2026}, \recentry{mp5-truth-axis}). |
| `sec_5d.tex:90` | [34] NoteRecords2026 | The numerical verification of these counts is in the binned response diagnostic record (Ref.~\cite{NoteRecords2026}, \recentry{response-diagnostic}). |
| `sec_5d.tex:294` | [34] NoteRecords2026 | The file and the projection are identified by their SHA-256 checksums (Ref.~\cite{NoteRecords2026}, identities already fixed). |
| `sec_5d.tex:360` | [34] NoteRecords2026 | It was computed only for the two companion covariances built for that purpose, and their outcomes do not transfer to this covariance (Ref.~\cite{NoteRecords2026}, \recentry{z-cv-record}). |
| `app_guide.tex:8` | [34] NoteRecords2026 | The provenance of the records the note cites, the fixed identities and audit record of the five-axis covariance of the configuration-(a) central value, the test-suite discipline, and superseded values |
| `app_statmethods.tex:362` | [34] NoteRecords2026 | Nor is the exact-split cross-check's $1.47$, computed with an earlier covariance built before the flux-band repair, evidence against them on its own (Ref.~\cite{NoteRecords2026}, superseded values). |
| `app_statmethods.tex:458` | [34] NoteRecords2026 | A split bootstrap of the earlier rebuilt bootstrap (Ref.~\cite{NoteRecords2026}, superseded values: retired material) separated the first two from an MC-statistics omission but not from the third, and |
| `app_statmethods.tex:565` | [34] NoteRecords2026 | The thresholds lie comfortably above the $0.166\%$ ML floor of the earlier ten-seed scan, which was in force when the tests were graded (Ref.~\cite{NoteRecords2026}, superseded values: retired materia |
| `app_statmethods_nd.tex:12` | [34] NoteRecords2026 | The measurements, the derivation and the requirement that N-D difference statistics use a rank cut fixed in advance are in Ref.~\cite{NoteRecords2026} (\recentry{rank-inversion}). |
| `app_negweight.tex:8` | [34] NoteRecords2026 | Two provenance limits apply to the production numbers: the driver revision that produced them is corroborated but not pinned, and no output records the job that produced them (Ref.~\cite{NoteRecords20 |
| `app_negweight.tex:122` | [34] NoteRecords2026 | The existing endpoint unfolds, produced in July 2026, used purity, as established by elimination from their job scripts and logs (Ref.~\cite{NoteRecords2026}, \recentry{bkg-mode-elimination}). |
| `app_negweight.tex:126` | [34] NoteRecords2026 | The standard chain uses purity by choice, on two grounds (Ref.~\cite{NoteRecords2026}, \recentry{oi6-oi8-oi126}). |
| `app_negweight.tex:145` | [34] NoteRecords2026 | Its ten endpoint unfolds used the purity correction and are recorded as purity controls, not publication inputs (Ref.~\cite{NoteRecords2026}, \recentry{fps-battery}). |
| `app_release.tex:62` | [34] NoteRecords2026 | A $\checkmark$ marks identities or values already fixed (bin edges: \S\ref{app:release-edges}; checksums: Ref.~\cite{NoteRecords2026}, identities already fixed); the rest are packaging. |
| `app_devhistory.tex:8` | [34] NoteRecords2026 | The chronology behind the rows is kept in the analysis repository's records~\cite{NoteRecords2026} and its commit history. |

## Repository records, not deposited (11 sites)

| file:line | ref | sentence (as printed source, comments stripped) |
|---|---|---|
| `sec_method.tex:15` | [31] UnfoldedWeightsESS2026 | For configuration~(e), the per-event Kish effective sample size and weight tails have been computed on the sixteen reported cells~\cite{UnfoldedWeightsESS2026}; they describe the unfolded simulated-ev |
| `sec_systematics.tex:282` | [39] TwoDFollowup2026 | \paragraph{Comparison with the earlier 2D budget.} The saved products and code of the earlier 2D budget~\cite{TwoDFollowup2026} show the following defects in its construction; the quoted budget correc |
| `sec_validation.tex:46` | [39] TwoDFollowup2026 | \paragraph{Requirements for validated total uncertainties.} The follow-up assessment~\cite{TwoDFollowup2026} distinguishes a proposed split-sample width check from repeated-sampling coverage. |
| `sec_joint.tex:5` | [53] JointTestRecord2026 | Reference~\cite{JointTestRecord2026} gives the specification and the decisions, and each later study's own reference is cited where the study is described. |
| `sec_joint.tex:224` | [57] JointTestKappa2026 | A scan of $\kappa$ along the direction $\delta_{\mathrm{fine}}$ of the claim variants~\cite{JointTestKappa2026} (for reporting only) found, in the calibration ensembles used for the decisions, all ten |
| `sec_joint.tex:239` | [58] JointTestRecovery2026 | The lost seeds were rerun under a procedure that was fixed, and reviewed independently, before the rerun~\cite{JointTestRecovery2026}. |
| `sec_joint.tex:254` | [59] JointTestProjections2026 | Its $p$ values were reproduced independently~\cite{JointTestProjections2026}. |
| `sec_joint.tex:289` | [61] JointTestRecoil2026 | In an exploratory sensitivity study of the response~\cite{JointTestRecoil2026}, the data are re-unfolded with the simulation's reconstructed recoil energy scaled by $\pm\SI{4}{\percent}$, and the ten  |
| `app_release.tex:9` | [98] ReleaseCandidate2026 | \paragraph{Release status.} RC7, a local release candidate with a README, checksums and a replay verifier~\cite{ReleaseCandidate2026}, has not been deposited or released under a publication tag. |
| `app_release.tex:52` | [57] JointTestKappa2026 | The multiplier scan of the joint tests is recomputable from RC7's sufficient inputs with the scan code of Ref.~\cite{JointTestKappa2026}, but it is not part of RC7's own verification. |
| `app_release.tex:55` | [99] AnaTuplePreservation2026 | All 2,374 inventoried input files (2,307 AnaTuples and 67 flux, reweight and parameter files) are identified by SHA256 checksum in Ref.~\cite{AnaTuplePreservation2026}; |

## Timing statements whose object no record names

- **`sec_method.tex:150`:** "The settings of the two OmniFold classifiers and the missed-event regressor were fixed \emph{a priori}." It names no object for "before".
  - Search: `git log -S'fixed \emph{a priori}' -- docs/analysis-note/*.tex` finds only 242e996c6 (2026-07-04, "note: advisor-comment round 1"). That commit wrote "The learner settings were fixed \emph{a priori} rather than tuned on data: 100 trees, learning rate $0.1$, and depth-3 capacity are the sklearn GradientBoosting defaults".
  - `grep -i 'a priori' docs/orchestration/CATALOG.md` finds only the F1 bias test's "seeds fixed a priori" row, which is a different object.
  - No record names what the settings were fixed before. The surviving sentence "No hyperparameter search was performed on data" states what it rules out. The wording is left as it is, for Joseph.

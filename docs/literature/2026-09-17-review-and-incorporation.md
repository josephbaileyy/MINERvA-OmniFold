# Literature update and incorporation proposal — 2026-09-17

This records the September literature review and proposes concrete manuscript and
methodology follow-ups. External findings are distinguished from implications
inferred for this project. Proposed studies have not been performed. This is a
literature record and editorial proposal, not evidence of scientific adoption,
a run authorization, or a change to the publication scope.

**Manuscript integration, 2026-09-17:** the selected editorial changes below have
now been applied to the paper, note, and primer sources: channel-qualified
MINERvA context, narrower FSI/2p2h interpretation, downstream-correlation and
coverage distinctions, method-development outlook, and release conventions.
The register remains a record of the review; its proposed scientific studies
remain unperformed. The integration also adds sixteen bibliography entries and
preserves the existing measured values and covariance-adoption boundaries.

## Scope, source checks, and project context

The search covered 2025–2026 unbinned unfolding, uncertainty quantification for
inverse problems, neutrino interaction measurements/modeling, and release tools,
through 2026-09-17. It is a targeted survey, not an exhaustive literature census.
Primary sources are linked below. Full-text passages were examined for the main
methodology and interpretation claims; supplementary leads are labeled where
only abstracts or release descriptions were screened.

The baseline was `LITERATURE_NOTES.md`, both analysis-note bibliographies, the
paper and relevant note sections, and identifier/title searches over searchable
Markdown, LaTeX, and BibTeX in the working tree. Before this record was written,
the new identifiers below were absent from the bibliographies/literature notes;
the broader searches also found no matching mentions for the principal entries.
This establishes a documentation gap, not that nobody has read the papers.
Ignored files, binary documents, remote-only branches, and archived evidence tags
were not exhaustively searched. Existing coverage includes 2504.06857 (T2K),
2507.09582 (Practical Guide), 2604.12364 (neutrino transfer), and 2608.28449 (Greif).

The repository snapshot read was main `9dba11949df648aa31bc179ac9f2c0cfaa293742`.
Scientific decisions continue to route through `docs/CURRENT_WORK.md` and the
governing records in `docs/OPEN_ITEMS.md`. In particular:

- OI-126 declines the PET nominal/statistical pairing; no literature analogy
  establishes its mechanism or supplies estimator-equivalence and coverage.
- OI-187 calls the covariance a claim upgrade while retaining the intention to
  complete uncertainties before publication. This proposal changes neither half.
- OI-183 and OI-184 already route the background-survey and measurement-census
  updates. Coordinate edits there rather than declaring those issues newly found.
- Joseph reports Perlmutter down with some jobs queued. No scheduler was queried
  in this review, so their identities, state, and absence of execution are not
  independently established. A queued job may start after service resumes.

## Source register and implications

### LIT-01 — uncertainty on selected physics quantities

Stanley et al., [Confidence intervals for functionals in constrained inverse
problems via data-adaptive sampling-based calibration](https://arxiv.org/abs/2502.02674),
February 2025; the current abstract page records a July 2026 revision.
The method constructs calibrated intervals for functionals under a known noise
law, evaluable forward model, and parameter constraints, including a
rank-deficient unfolding example. Batlle et al., [Simultaneous Frequentist
Calibration of Confidence Regions for Multiple Functionals in Constrained Inverse
Problems](https://arxiv.org/abs/2510.11708), October 2025, develops joint regions
and distinguishes simultaneous from marginal coverage (Introduction and §§4–7).

**Project inference:** selected integrals or linear contrasts can be useful
targets for an independent uncertainty benchmark. Specify a projection/contrast
matrix, units, support, and simultaneous coverage target before evaluating it.
A high-E_avail/high-W region already noticed in data is not a prospectively
chosen discovery region; any significance must account for that selection or
remain explicitly exploratory.

**Limit:** a rank-deficient forward operator and a finite-ensemble rank-deficient
covariance are different objects. These papers do not make a truncated covariance
inverse valid. Their guarantees do not automatically cover a learned response,
finite MC, detector nuisances, or our nonlinear estimator. A reduced benchmark
would complement, not replace, the adopted scalar-5D construction. Put the
conceptual distinction in `app_statmethods.tex`; first prepare an assumptions
table on paper, before proposing any computation.

### LIT-02 — correlations between unfolded events

Desai, Long, and Nachman, [Unbinned Inference with Correlated Events](https://arxiv.org/abs/2504.14072),
April 2025; published version v2, EPJC 85 (2025) 1089. Their examples demonstrate
that unfolding induces event correlations and that neglecting them can
underestimate downstream parameter uncertainties.

**Project inference:** nominal event weights are insufficient for arbitrary
downstream inference. Carry coherent replicas through the downstream fit or
statistic, or justify an alternative correlated construction. Distinguish
resampling original data and repeating the estimator from independently
resampling already-unfolded rows. A classifier two-sample or permutation test
needs a null construction appropriate to its learned weights and reused data.
No flaw in an existing project test was established by this literature review.

**Incorporation:** add a short consumer contract to `app_statmethods.tex` and
event-weight release documentation. A later read-only code review should trace
which randomness, fitting, and data reuse the current GoF null actually includes.

### LIT-03 — a closely related MINERvA three-dimensional measurement

Ruterbories et al., [Comparisons of triple-differential cross sections for
quasielastic-like neutrino–hydrocarbon interactions using approximately 3 GeV
versus 6 GeV beams](https://arxiv.org/abs/2606.00745), submitted May 30, 2026.
The [Introduction](https://arxiv.org/html/2606.00745v1) describes p_T, p_parallel,
and E_avail, with E_avail equal to summed proton kinetic energy for its
quasielastic-like signal. Comparisons point toward overestimated proton and
charged-pion final-state interactions within the tested models.

**Project inference:** use this as context for visible/invisible energy and FSI,
and as an updated multidimensional precedent. The signal, observable convention,
flux, support, and selection must match before a numerical comparison. It is not
an inclusive 3D validation reference, and its FSI conclusion does not determine
the cause of our inclusive discrepancy.

**Incorporation:** cite in the Letter's opening context and the note's `sec_3d.tex`
and `app_landscape.tex`. Replace unqualified “no published 3D reference” with a
statement about no directly matched CC-inclusive reference used for validation.
Check the landscape figure's source inventory before claiming its census is complete.

### LIT-04 — shallow-inelastic context for W

Lozano et al., [Measurement of charged-current neutrino and antineutrino cross
sections on hydrocarbon in a shallow inelastic scattering region](https://arxiv.org/abs/2503.20043),
March 2025; the [APS acceptance record](https://journals.aps.org/prd/accepted/10.1103/vq38-kmxq)
reports acceptance on August 13, 2026. The measurement probes the resonance–DIS
transition and reports shape and normalization disagreements with generators.

**Project inference:** cite as motivation for resolving hadronic-mass dependence.
It is not independent confirmation of the same excess: regions, observables,
selection, and shared experimental uncertainties require comparison first.
Place compact context in `paper_body.tex` and detail in `sec_eavailw.tex`.

### LIT-05 — nuclear currents and axial form factors

Franco-Munoz et al., [Two-body current and axial form factor effects in
charged-current quasielastic neutrino-nucleus scattering within the NEUT event
generator](https://arxiv.org/abs/2605.00756), May 2026. The study examines changes
to quasielastic predictions, including one-/two-body current interference;
no tested configuration is uniformly preferred by the different datasets.

**Project inference:** interaction labels in a generator are not unique physical
mechanism measurements. Two-body currents must not automatically be equated with
the generator's 2p2h event category. Their interplay with axial form factors and
FSI motivates qualified interpretation of visible-energy spectra. This does not
erase any existing measured dial response or MEC-addition comparison.

**Incorporation:** a short interpretation paragraph in `sec_3d.tex`; avoid making
the Letter a review of nuclear models. A new model comparison would require its
own configuration, selection matching, provenance, and authorization.

### LIT-06 — ensemble placement and pretraining

Torales Acosta et al., [Stabilizing Neural Likelihood Ratio Estimation](https://arxiv.org/abs/2503.20753),
March 2025. The authors report improved bias and variance when aggregating models
at Step 1 before pushing weights to Step 2. In their studies, pretraining can
further reduce variance while increasing bias. These statements were checked
against the primary abstract; an implementation proposal requires full-method review.

**Project inference:** final-weight averaging and averaging inside iterations are
different estimator definitions. Specify the object averaged (classifier scores,
ratios, or weights), weighting, and position in the iteration. Reduced seed spread
alone is not evidence of reduced total error. Rank candidate designs by closure
bias together with dispersion, not only classifier AUC or training loss.

**Incorporation:** `sec_pet.tex` method-development outlook and an estimator-design
table. No PET C_ML construction, new training, or reconsideration of OI-126 follows
from this paper; any future experiment needs the exact governing authorization.

### LIT-07 — background, acceptance, and efficiency derivation

Falcão and Takacs, [High-Dimensional Unfolding in Large Backgrounds](https://arxiv.org/abs/2507.06291),
July 2025, [JHEP 07 (2026) 012](https://doi.org/10.1007/JHEP07(2026)012).
The OmniFold-HI derivation explicitly incorporates fakes and missed events and
relates the construction to expectation-maximization/IBU; auxiliary observables
improve their heavy-ion examples.

**Project inference:** compare the event categories and normalization factors in
its §2 with the selection-complete scalar construction. Record differences in
background treatment, generation support, and efficiency corrections. Dense
heavy-ion contamination and neutrino non-signal backgrounds are not identical.
Equation agreement would not independently verify our implementation or UQ.

**Incorporation:** revise the historical background survey in `sec_method.tex`
through OI-183, add context in `app_negweight.tex`, and prepare a symbolic mapping
before considering new studies. Do not identify this method as negative-weight
subtraction merely because both address backgrounds.

### LIT-08 — nuisance profiling

Zhu et al., [Machine Learning-based Unfolding for Cross Section Measurements in
the Presence of Nuisance Parameters](https://arxiv.org/abs/2512.07074), December
2025. Profile OmniFold extends the EM-based method to nuisance parameters and is
demonstrated on Gaussian and simulated CMS examples. The CMS discussion also
reports sensitivity to initialization/local optima.

**Project inference:** distinguish uncertainty propagated under an external
nuisance distribution from nuisances constrained by the same observed data.
Profiling changes the inference procedure and may encounter detector/physics
degeneracies. It is not a correction that can be applied to an existing covariance.

**Incorporation:** distinguish this algorithm from the already cited 2023
unbinned profiled unfolding paper in the methodology outlook. An initial design
exercise should name one nuisance, its external constraint, and which observed
information distinguishes it from a truth-shape change. No implementation now.

### LIT-09 — alternative estimators

[AUSSIE: Unfolding without Iterations, Adversaries, or Surrogates](https://arxiv.org/abs/2602.24282),
February 2026, replaces the second OmniFold step with a different loss and reports
improved closure in its benchmarks. [SPINUP: Simulation-Prior Independent Neural
Unfolding Procedure](https://arxiv.org/abs/2507.15084), July 2025, learns the forward
mapping. [Analysis-ready Generative Unfolding](https://arxiv.org/abs/2509.02708),
September 2025, introduces GenFoldG/GenFoldC with impurities, acceptance, and
efficiency. The latter two were screened at abstract level.

**Project inference:** these are candidates for future algorithmically different
cross-checks, not grounds to replace production. Simulation-prior independence
does not imply detector-model independence, adequate simulation support, or valid
coverage. Compare identical input/support and evaluate bias and uncertainty,
not a single attractive projection.

**Incorporation:** related-work/outlook citations in the note; no benchmark claim
in the Letter without a project measurement.

### LIT-10 — releasing reusable unbinned results

The [ATLAS full charged-particle phase-space release](https://opendata.cern.ch/record/atlas-160005)
provides a concrete public data/code route beyond the already recorded Greif
thesis. The [September 7–9 PyHEP.dev presentation](https://indico.nikhef.nl/event/7873/timetable/?print=1&view=standard_numbered)
describes `omnifold_publication`, including uncertainty-family metadata,
normalization, binning, row alignment, and checksums. The latter is an emerging
proposal/tool, not an established mandatory publication standard.

**Project inference:** prepare a release schema retaining stable event identity,
nominal-estimator identity, units, support, normalization, family/member identity,
centering/divisor convention, and the supported downstream use. Include a small
reproduction example and limitations of arbitrary new projections. Do not import
an experimental event-count threshold as a universal MINERvA requirement.

**Incorporation:** release-design documentation first. Verify public ATLAS source
and release versions before upgrading any thesis-only claim about approved
numbers. Do not infer that every background detail was verified from the portal
description. Coordinate with OI-183/OI-184.

### LIT-11 — additional physics and data-release leads

These were screened at abstract or collaboration-page level and are lower
priority than LIT-03/LIT-04 for this inclusive FHC paper:

- [MINERvA single-pion production with zero pion kinetic-energy threshold,
  2605.24224](https://arxiv.org/abs/2605.24224), May 2026: useful context for pion
  modeling and threshold effects; an exclusive channel, not our validation sample.
- [MINERvA inclusive antineutrino scattering on C, CH, Fe, and Pb,
  2604.07091](https://arxiv.org/abs/2604.07091), April 2026: nuclear-target and
  beam-mode context; not a same-sample FHC comparison.
- The [MINERvA open-data page](https://minerva.fnal.gov/getdata/) describes planned
  flux/reconstruction improvements and an RHC playlist 6F MC vertex-prediction
  issue. No impact on this project's frozen FHC inputs has been established.
  Track release identity when planning future input updates; do not silently
  replace frozen inputs or transfer an RHC warning to FHC.

## Concrete editorial proposals

The following prose records the editorial proposal; the integrated wording is in
the manuscript sources and is adapted to each document's audience. Source
links in this document identify the citations to add to `technote.bib` during
integration. Existing numerical claims require their original receipts; this
review neither recalculates nor re-ratifies them.

### Letter: dimensional precedent and scope

Target: `docs/analysis-note/paper_body.tex`, opening context after the existing
MINERvA three-dimensional citation. Add LIT-03 alongside that precedent:

> Recent MINERvA measurements also compare triple-differential quasielastic-like
> cross sections in muon kinematics and available recoil energy between two beam
> configurations. Their signal differs from the inclusive signal studied here;
> the advance of this work is the simultaneous unbinned inclusive construction
> and its extension to additional observables.

For a compact Letter, combine this with the existing sentence rather than
appending a second general survey paragraph.

### Letter and note: qualify the FSI interpretation

Target: the Letter's low-E_avail paragraph; retain established observations and
add the following qualification with LIT-03:

> The pion-FSI variations tested here do not exhaust possible changes in nuclear
> transport. Recent quasielastic-like measurements highlight sensitivity to
> proton and pion final-state interactions, although their different signal
> definition prevents a direct identification of the effect with the inclusive
> discrepancy reported here.

The sharper concern is in `sec_3d.tex`: the emphasized sentence “Final-state
interactions do not explain it” and the subsequent attribution to the
initial-state/nuclear model rather than rescattering overgeneralize the stated
two-pion-dial exercise. Proposed replacement framing:

> The tested pion-FSI variations do not account for the discrepancy. This result
> constrains those variations within the chosen generator; it does not exclude
> other transport models or proton-FSI effects. Adding the tested MEC component
> improves the low-recoil description, supporting its relevance without uniquely
> identifying the underlying nuclear mechanism.

Also review “identify its origin directly” and “confirms it” in the same section.
Preserve the measured comparisons and cite their existing evidence; change the
scope of interpretation, not the measurements. LIT-05 belongs in the longer
note discussion, with the distinction between two-body currents and 2p2h labels.

### Letter: W and the generator discrepancy

Target: after the high-W generator-context paragraph; cite LIT-04:

> Dedicated MINERvA measurements in the shallow-inelastic region also report
> difficulties describing cross sections with current generators. These results
> motivate differential tests across the resonance–DIS transition; the different
> selections preclude interpreting them as an independent confirmation of the
> localized difference shown here.

Keep the existing central-value-only qualification. Do not promote “generator
deficit” to a discovery, unique mechanism, or quantified significance.

### Note: inference and coverage

Target: `app_statmethods.tex`, with LIT-01 and LIT-02:

> Unfolding induces correlations among weighted events, so a likelihood treating
> the unfolded sample as independent observations need not yield valid parameter
> uncertainties. Downstream inference must propagate the correlated unfolding
> construction or otherwise justify its calibration. Coverage for each reported
> projection separately is distinct from simultaneous coverage across a chosen
> set of projections. Methods for constrained inverse problems offer possible
> benchmarks, but their guarantees require assumptions not established by closure
> of the present estimator alone.

Keep this in the note unless the Letter actually introduces downstream unbinned
inference. A bibliography addition alone does not demonstrate compliance.

### Note: related work and publication language

Update `sec_method.tex` with LIT-07/LIT-08; `sec_pet.tex` with LIT-06;
`app_landscape.tex` with the channel-qualified MINERvA additions; and the release
discussion with LIT-10. Cross-check `sec_summary.tex`, `sec_execsummary.tex`, the
primer, and figure captions for the same scope statements. The T2K source's own
abstract describes a mock-data study on public simulation; use that primary
classification rather than inheriting a contrary table label (OI-184).

Do not add every methods paper to the Letter. Prioritize the two close physics
references and the FSI qualification there; retain alternatives, coverage theory,
PET design, and release tooling in the note or future-work record.

## Work during the outage and after it

| Order | Work | Concrete completion criterion | Dependency |
|---|---|---|---|
| 1 | Literature record and editorial proposal | Sources, limitations, manuscript locations, and proposed prose recorded here and linked from the literature front door | Local documentation; delivered by this change |
| 2 | Focused manuscript integration | Add verified bibliography entries, incorporate selected prose, reconcile note/primer/paper, render and inspect all deliverables | Local LaTeX tools and standalone note checkout; no cluster analysis |
| 3 | Inference assumptions review | Trace the actual GoF null, fitting/data reuse, ensemble provenance and projection semantics; label unknowns | Read-only source/artifact access; do not claim validation from searches |
| 4 | Production-interface decision packet | Inventory supported operations, missing real-input adapters and parity checks, queued-job bindings, and an explicit adoption scope | Branch identification and local review; production evidence later |
| 5 | Study specifications | Freeze quantities, assumptions, estimator, truth scenarios, bias/coverage metrics, precision/power goals, and resource limits | Design work only; no production launch |
| 6 | Authorized scientific studies | Measured results under the named run authorization with original inputs, environment, receipts and required records | Perlmutter recovery/data access and authorization |

For item 5, a useful order is (a) functional-coverage assumptions, (b) downstream
null calibration, (c) symbolic background/selection comparison, (d) ensemble
placement design. Alternative algorithms and nuisance profiling are longer-term.
Do not silently enlarge any queued run to implement these ideas.

When access returns, first observe the scheduler and governing job records.
Before changing deployment, determine whether queued jobs bind an immutable
revision or read mutable paths at execution. Do not cancel, resubmit, or redirect
another lane's jobs as part of a literature or branch-migration task.

Manuscript integration has a defined completion contract: run
`docs/analysis-note/build_all.sh` for note, primer, and paper; inspect the rendered
results and citations; synchronize corresponding sources to the standalone
`MINERvA-OmniFold-Analysis-Note` repository; build there; commit and push the
corresponding changes and record both remote heads. Draft prose in this document
is not a completed manuscript edit or a synchronized publication deliverable.

## Relationship to the possible trimmed project branch

The candidate inspected locally is `feat/production-interface` at
`972face833ce21a7e3ca64dcbde452ceda9e9ac4`; confirmation that this is the branch
Joseph means was requested. These observations are conditional on that identity
and are a source comparison, not a production-equivalence audit:

- `git diff --stat main...feat/production-interface` shows 28 added files under
  `production/`. It is an added interface, not removal of the existing project.
- Direct comparison of `LITERATURE_NOTES.md`, `paper_body.tex`, and `technote.bib`
  between these two tips showed no differences. Literature/editorial work can
  therefore be carried independently of the migration decision.
- The branch's `production/README.md` describes shared scalar nominal/member
  calculation and explicit projection contracts. Its `production/tests/README.md`
  records local checks and says full-data equivalence, ROOT/MAT production, PET
  execution, coverage, and total-systematic construction were not established.
  Those reported test results were read, not rerun in this literature task.
- Selection-complete systematic execution, total-covariance assembly, and PET
  uncertainty products are explicitly outside the new interface's supported scope.

**Recommendation:** complete the scientific writing on the current sources,
keeping its changes separate from any workflow migration. Evaluate adoption of
the new interface task by task after the required parity evidence exists. A
cleaner interface does not establish scientific equivalence or supersede the
governing uncertainty construction. Do not switch queued jobs or frozen
reproduction paths merely because the local interface is easier to use.

This literature work does not switch production branches, alter analysis code,
launch compute, or change scientific adoption. The selected prose has been
integrated into the manuscript sources. The branch decision and proposed studies
remain separate from those editorial changes.

## Manuscript verification — 2026-09-17

`build_all.sh` passed in both the canonical project and standalone analysis-note
checkout: note 94 pages, primer 5 pages, and paper 3 pages. Source and PDF
containment checks passed; their existing source-only exceptions remain explicitly
reported by the gate. All 89 tracked manuscript files match between checkouts,
and extracted text matches for all three PDFs. Rendered paper and primer pages,
changed note sections, and bibliography pages were inspected. A pre-existing
overflowing systematic-total table row was wrapped without changing its values.
The final logs have no undefined citations/references or overfull boxes.

This verifies document construction and synchronization, not the proposed
scientific studies or uncertainty coverage. Commit and remote identifiers are
reported with delivery so that this record need not refer to its own future hash.

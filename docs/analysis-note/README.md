# Publication deliverables and completion plan

This directory builds three audience-specific documents from shared sources:

| Deliverable | Driver | Purpose |
|---|---|---|
| Analysis note | `main_note.tex` | Complete technical and validation record |
| Primer | `main_primer.tex` | Short internal orientation |
| External paper | `main_paper.tex` | PRL-style scientific argument |

Build and containment checks run together:

```bash
bash build_all.sh
```

`build_all.sh` must produce all three PDFs and prove that retracted note-only material does not
reach the primer or paper. The PDFs are generated outputs; the tracked sources and figures in this
directory are the publication inputs.

## Scope of this plan

This page is navigation, not evidence or authorization. It records publication
work that can proceed without inspecting a covariance-derived significance;
scientific states and decisions live in the routed `OI-*` records and receipts.

## Priority while the scalar-5D work is active

Put most effort into protecting and completing the scalar-5D covariance and response-robustness
critical path. Use parallel publication capacity on the five packages below. A useful allocation is
approximately 70% critical-path support and 30% covariance-independent publication preparation.

### 1. Fix the inference contract before reading significances

- Name the primary generator-comparison statistic and the covariance projection it consumes.
- Fix the tested projections, bin masks, rank/inversion treatment, and generator set before reading
  covariance-derived significances.
- Prefer a global test on the full `(E_avail, W)` plane. Treat the high-`E_avail`, high-`W`
  region as localization after the global comparison unless its boundaries have an independently
  documented, pre-data origin.
- State how data-selected localization and any multiple comparisons will be handled.
- Define what each possible result can support: a global discrepancy, descriptive localization,
  method validation only, or no covariance-dependent claim.

This is a prospective analysis contract, not permission to calculate or quote a new significance.

### 2. Make the paper figures ready to receive the adopted covariance

- Rework the 2D reproduction figure so the uncertainty comparison and a ratio or residual panel are
  visible rather than described only in prose.
- Put physical bin ranges and fully specified color-bar quantities on the joint
  `(E_avail, W)` figure instead of exposing only bin indices.
- Reserve a single, traceable interface through which the adopted scalar-5D covariance supplies
  projected bands, correlations, and test statistics.
- Keep central values visually distinct from uncertainty-dependent annotations so a provisional
  plot cannot be mistaken for the final result.
- Reflow the PRL draft so the headline figure is part of the argument rather than isolated after the
  references.

### 3. Assemble the compact validation supplement

The paper should point to a small, quantitative validation package containing:

- lower-dimensional marginal anchors;
- injected-shape closures for every added observable;
- iteration and classifier-family stability;
- detector migration, phase-space support, and acceptance diagnostics;
- detector-response-mismatch robustness, once its governed result lands; and
- the exact distinction between estimator validation, uncertainty coverage, and physics adoption.

Do not convert an open coverage or response question into a passing statement by summary. The
supplement must inherit the controlled state of each source result.

### 4. Prepare the public result package

Define the release schema before the final numbers are available:

- reporting bin edges and canonical flattened-bin ordering;
- central-value and covariance object names, units, and normalization;
- projection matrices and row-index maps;
- provenance metadata and digests;
- generator predictions used by the paper; and
- one minimal example that reproduces a published projection from the released trunk.

The released covariance and every lower-dimensional product should be mechanically traceable to the
same adopted scalar-5D object.

### 5. Support provenance at the projection boundary

Close the routed projection-receipt gap before producing publication projections. In particular,
`OI-129` requires the projected covariance itself to be digested after the output file is closed and
the stored row-index object to be read back and checked independently of the in-memory array that
wrote it. Do not retrofit immutable historical receipts; make the next projection self-verifying.

## Paper work to defer until the scientific result lands

Do not finalize:

- the headline significance or generator interpretation;
- a title or abstract that presupposes the covariance outcome;
- the final high-`E_avail`, high-`W` claim strength;
- covariance-dependent conclusions in the note, primer, or paper; or
- a publication-results tag.

If the covariance is adopted and the response study supports the result, the paper can lead with the
localized generator discrepancy. If the uncertainty is adopted but weakens that discrepancy, lead
with the completed five-observable measurement and treat the localization descriptively. If no
candidate becomes adoptable, the external paper is not a completed cross-section result and should
not imply otherwise.

## Source map

| Need | Read or edit |
|---|---|
| Paper title, authors, abstract, bibliography wiring | `main_paper.tex` |
| Paper scientific narrative and figure placement | `paper_body.tex` |
| Full note driver and section ordering | `main_note.tex` |
| Primer driver and narrative | `main_primer.tex`, `primer_body.tex` |
| Shared measured-value macros | `values.tex` |
| Validation details | `sec_validation.tex`, `app_response_mismatch.tex` |
| Scalar higher-dimensional result | `sec_3d.tex`, `sec_eavailw.tex` |
| Uncertainty construction and inference rules | `sec_systematics.tex`, `app_statmethods.tex` |
| Generated figure inputs | `figures/`, `make_figures.sh` |
| Build and containment behavior | `build_all.sh`, `test_build_all.py`, `check_dead_containment.py` |

Before changing a claim or measured value, follow the evidence route in the repository `AGENTS.md`.

## Relationship to repository organization

Broad layout moves are deferred until after the publication-results freeze; see
`docs/POST_PUBLICATION_REORG_PLAN.md`. Until then, prefer small front doors such
as this one, accurate source maps, and removal of duplicated paper prose.

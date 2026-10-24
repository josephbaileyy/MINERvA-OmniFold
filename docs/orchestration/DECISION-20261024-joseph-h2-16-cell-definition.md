# DECISION 2026-10-24 — Joseph: approve the 16-cell H2 reporting definition for the 5D measurement

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The route.** DECISION-20261024 (`-5d-community-standard-route`) put the 5D measurement on the community-standard
  route, reporting from H2's joint cells. Its item 2 allows merges chosen before data are read.
- **The director's ruling on that clause.** Refined-estimator data results had already been read: s5p Stage 2's H2 h,
  Stage 0's H2 readouts, the ladder's readouts, P5 and Stage 1's H2 bootstrap widths. "Declared before any read"
  therefore cannot hold literally. In its place:
  - any merge, restriction or split uses only simulation and generator-truth quantities;
  - the rule is committed before any H2-level quantity is computed from an (e) data product in this pipeline;
  - the earlier reads are disclosed.
- **The declaration.** `state/measurement-scoping/pv-ladder/H2-DEFINITION-DECLARATION.md` (PR #333, merged at
  `9947cda0`; the file's sha256 begins `3bdf74a8e9e7a83b`), from the 2d test lane.
  - **The rule:** a reported box with MC purity below 0.1 joins the neighbour whose union has the highest purity,
    lowest-purity box first, and repeats until none remains below 0.1.
  - **How it ran:** the code was committed in `7cb80cc2` before it ran once. It read MC keys only.
  - **The result:** 12 merges take H2's 27 reported cells to 16 reporting cells, R00–R15 (`readouts/h2_definition.json`,
    sha256 begins `b67907615fe2e903`).
- **The director's three questions:**
  1. Approve the 16-cell definition? The director recommended yes.
  2. How to grade the positive control? The director recommended grading it on the 27 base H2 cells, with the rule
     unchanged (21 of 27 qualify), plus a descriptive readout on the 16 cells labelled "not powered".
  3. Add a stability rule? The director leaned no: disclose the four low-stability cells instead.

Joseph's answer, verbatim:

> 1. I approve the 16 cell definition. 2. sure do your recommendation 3. no for now

sha256 of the text plus a final newline begins `9f54434646ba1ac9`.

## What is decided

1. **The 5D reporting definition is the 16 cells R00–R15** of `h2_definition.json`, as declared.
   - Both the S1 covariance and C_model,5D use these cells and this order, with the fine map whose sha256 begins
     `930326a3`.
   - GiBUU's shift above p_∥ = 10 GeV/c is carried as measured, with a label (the declaration's §2).
2. **The positive control is graded on the 27 base H2 cells,** with the declared rule unchanged. The 16-cell readout
   is reported descriptively and labelled "not powered". The thin margin is a disclosed risk: 5 qualifying cells lie at
   1.04–1.21 %.
3. **No stability criterion, for now.** The four low-stability cells (R02, R06, R10 and R15, stability 0.16–0.25) are
   disclosed in the paper's limitations.

## Open, before C_model,5D is bound

- **GiBUU's domain.** The pv-ladder reweights GiBUU below p_∥ = 10 GeV/c. The paper's joint tests restrict GiBUU to
  p_∥ < 6 GeV/c, "whose sample lacks high-energy neutrinos" (`paper_body.tex:245-246`). The S1 plan flagged the
  difference (its §5 item 7).
  - The 2d test lane reconciles the two, using generator and simulation quantities only.
  - The director brings the choice to Joseph if it changes the vertex.
  - It does not change the cell definition.

## Not changed

- **No compute is granted.** The S1 plan's 11 CPU node-h cap needs Joseph's separate approval.
- **Claims and KI-85** are Joseph's.

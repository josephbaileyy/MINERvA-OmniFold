# DECISION 2026-10-27 — Joseph: frame the paper as a measurement, and scope whether its limitations can be reduced

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The paper is titled and framed as a methods study: "Performance and limitations of multidimensional OmniFold
  unfolding with MINERvA open data".
- The sixteen-cell 5D result, the measurement Joseph chose to pursue by the community-standard route
  (`DECISION-20261024-joseph-5d-community-standard-route.md`), is being integrated. The non-final configurations are
  leaving the paper (`DECISION-20261027-joseph-move-nonfinal-configurations-to-note.md`).
- The director laid out the methods and the measurement framings and recommended a measurement-led paper, with the
  methods findings as its support.

Joseph's answer, verbatim:

> I think we should do the measurement framing and are we sure theres no way to resoslve the limitations?

sha256 of the text plus a final newline begins `6d9ab460be9ccf27`.

## What is decided

1. **The paper is framed as a measurement.** Its title, abstract and Sec. I lead with the sixteen-cell five-observable
   cross section, its covariance and its generator comparison.
   - **The methods findings support the result.** These are the 2D reproduction, the background-subtraction result,
     the recovery failures, the coverage test and the fake-data study. They show how far the result can be trusted.
   - **The result's limitations are stated up front, as its limitations:**
     - interval coverage is not validated;
     - the fake-data bias at the GiBUU-like truths and the q3 tilt is not covered;
     - the generator χ² depends on the flux correlations.
   - **The paper rewrite lane drafts the title, abstract and Sec. I.** The text goes through the independent PRD read
     (`DECISION-20261027-joseph-prd-review-route-push-and-public-github.md`) before the final draft reaches Joseph.
   - The joint-test move is still only "seriously considered". The second scope review weighs it under this framing.
2. **Whether the limitations can be reduced is scoped at about 0 node-h,** as a costed plan for Joseph. Nothing runs
   before he decides. The plan covers:
   - **a held-out truth** (F1, GENIE v3, deferred on 2026-10-25), and a frequentist coverage test of the sixteen-cell
     intervals against it. This needs compute and a declaration;
   - **the GiBUU-like and q3 fake-data bias:**
     - an assigned non-closure term, or a generator-shape component built from that truth, to be priced. Adopting
       either would change the reported covariance, so it is Joseph's;
     - the alternative is to keep the limitation as stated;
   - **the flux-correlation sensitivity:** whether anything beyond stating it applies. It is a property of the
     comparison, not a defect of the measurement;
   - **for each option:** what comparable published measurements do, the cost, the risk, and what it would change in
     the printed result.
   - The 5D measurement session prepares the plan. Cell merges or new cuts after the data read stay inadmissible
     (`FD-DIRECTOR-RULINGS.md`).
3. **A measurement framing raises two of Joseph's own acts in importance:** MINERvA collaboration review, and the
   release of the data file (Q8). Both remain his.
     <!-- absence-ok: states the record's own scope (the reduction is scoped, not run) and its limitations as the paper will state them; no new claim that a result is absent from the repository -->

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.

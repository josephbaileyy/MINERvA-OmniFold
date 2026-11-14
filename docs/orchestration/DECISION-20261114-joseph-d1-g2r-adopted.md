# DECISION 2026-11-14 — Joseph: D1's "validate" means the runs are valid; the rebuilt 2D covariance is adopted

**Recorded by** the paper-tighten lane, as director.

## What led to it

DECISION-20261112-joseph-consult-d1-d7.md, D1: "If COV2D-G2R's part (a) is VALID and its held-out constructions
validate, the rebuilt covariance becomes the reported 2D covariance." COV2D-G2R's readout ran on 2026-11-14 (data
03:53Z, G18 04:00Z, AR23 04:09Z; launcher 1f719ba3, connects 56c34ad6, 029ff7fb and 6bec8fad, all PASS).

cov2d's reading, from the readout records:
- **Part (a):** VALID (COV2D-G2R-DECLARATION.md:229-232). Controls failed none, G6 and G10 pass, and all 177
  products are present.
- **The held-out tunes:** each run is valid. Controls failed none, G6 and G7 pass, and there are 175 products each.
  Each tune's verdict is UNDER-COVERS under the unchanged rule (COV2D-DECLARATION.md:269-273).
- **Coverage, identical under the rebuilt C_T' and the current C_T:**
  - G18: joint 0 of 300, flagged cell 29.
  - AR23: joint 0 of 300, flagged cells 29 and 56.
  - Every flagged cell is driven by bias.
- **The data covariance:**
  - median per-bin relative σ 6.41367 % → 6.46302 %;
  - integrated σ 4.75917 % → 4.75912 %;
  - max |Δρ| 0.130;
  - rank 205 → 205.

The G2R records do not define "validate" for the held-out constructions. The director put two readings to Joseph:
"the runs are valid", under which the rebuild is adopted, and "coverage passes", under which it is not.

## Joseph's words, verbatim

> D1: yes lets read validate as the runs are valid

(`4876d9f65fb2b1d4`, the sha256 of the text plus a final newline).

## What is decided

1. In D1, "the held-out constructions validate" means that the held-out tunes' runs are valid under their declared
   controls. It does not mean that they cover.
2. The condition is met, so the rebuilt covariance (COV2D-G2R's C_T') becomes the reported 2D covariance. The current
   covariance stays as a documented comparison.
3. As D1 says, the paper reports the coverage counts under the unchanged rule. They are unchanged: under-covers at both
   tunes, with the same flagged cells and joint counts. Every result that depends on the 2D covariance is updated from
   the G2R readout records. The construction's correction (per-universe weights on the missed-event rows) is described.
4. T2A's descriptive decomposition and its truncated joint counts, which the G2R code did not produce, are computed for
   C_T' as a descriptive step before the dependent text is updated.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** this reading of D1 and the adoption, as Joseph's.
- **Not citable for:** any number, which the readout records carry; the covariance covering at any tune; any paper
  sentence.

Nothing is submitted, deposited or tagged.

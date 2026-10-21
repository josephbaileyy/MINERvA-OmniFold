# JIT-1: estimator discreteness under rounding-scale input changes (specification, frozen before any run)

**Owner:** the paper-tighten lane, as director, 2026-10-21. Joseph said "sure spec them now". The compute comes under
the methods-paper approval.

**CITABLE FOR:** JIT-1's question, design and grant.
**NOT CITABLE FOR:** any result before its report.

## 1. Question, and what is known

**Known:**
- The MP-1 input-jitter study (measurement-paper phase 1, addendum 12): edge-safe ±½ float32-ulp jitter of every
  coordinate moves the unfolded result as much as the curvature of a ±1σ response shift.
- KNOWN_ISSUES 80 and the note (`sec_5d`) record a real-data rounding spread with a median of 0.23% per J cell.
- The configurations are deterministic and seed-invariant: no bagging, and bins constructed from all rows.

**The question:** what in the estimator makes its output depend on rounding-scale input changes, and how large is that
dependence relative to the statistical uncertainty, for the configurations the paper uses?

## 2. Design (declared in a file before any output)

- **Configurations:** (a), the central values, and (e), the tests and the refined central values (RE-1). Each is run
  on the data and on one nominal-truth pseudo-experiment.
- **Jitter:** `s5p_numerics --pairs=-:J`, edge-safe, J = 1–10.
- **Mechanism arms**, each changing one setting:
  - (m1) LightGBM `max_bin` 255 → 1023;
  - (m2) `bin_construct_sample_cnt` reduced to 200,000;
  - (m3) the exact-split (non-histogram) learner, where the code supports it;
  - (m4) binned IBU (IBU-1's estimator), expected to be smooth, as a control.
- **Readout:**
  - the per-cell jitter scatter of f over the statistical σ (median and 90th percentile), for each configuration and
    arm;
  - the scatter's dependence on the arm;
  - whether the scatter accounts for the G3 curvature and the rounding spread of KI 80.

## 3. Use

The result supports a short paper statement on estimator stability under rounding-scale changes, and the design of any
future linearity test (addendum 12). It is descriptive, with no gate.

## 4. Grant

- At most 5 CPU node-h on m3246, or on Delta after a reproduction control.
- Each job under 12 h; every job ledgered; nothing on CFS.
- It runs when the inputs are reachable.

# The Supplement side of the codex referee read at 3d75ed5d4 (2026-11-16)

The director passed on these Supplement items from `referee-paper-3d75ed5d4….md`.

- **Major 1: table S13, `tab:prr-levels`, in S8.2.** It lists every tested level of the prior-retention study, with
  configuration (e) as the baseline: iterations 2/10/20/50; capacity (25,4), (400,31), (1000,63); a quarter of the
  simulation; and the observable sets O4r (no W in step 1 only), O4, O3 and O2. Per level it gives what the level
  applies to, ρ at both flagged truths, Δρ from (e), the setting's class, and the number of newly flagged graded truths.
  - Every number is a key from the FD-PRR readout, made by make_values_fived16.py's `prr_levels_values()`. It asserts
    that every level still flags both flagged truths, that the new flags recomputed from the grades equal PR-3's
    lists, and that every threshold is the floor (9.03 s stays below 0.022).
  - The levels and learners are taken from FD-PRR-DECLARATION.md:165-172 and from prr_probe.py's MASKS and LEVELS
    (:116-137).
  - Pointers: S8.2's design and results paragraphs, and index row 4's Details.
- **Minor 2 (S5.1).** For both alternative constructions of C_model, the trace ratio and GiBUU's share are now stated
  as those of the fractional covariance, against $C_{\mathrm{model}}^{\mathrm{frac}}$.
- **Minor 7.** Index row 7 now reads: "Neither cross-fitting nor the two tree regularizations passes. The ensemble
  average passes stability, …, but fails its separate bias criterion, closure no worse at every truth: …".
- **Minor 8 (S10).** S10 now states the bias-half rule's noise band, as written in v-half/DECLARATION.md sec. 4
  :126-147: m, σ_m² = ((1+d)ν)² + (0.5 sgn(d) − |r|)² σ_d², K, and the pass, fail and unresolved conditions.
  K (`vhalf-k`) is read from the readout's own rule record. No class changes.
- **Minor 4** (the five-observable results table) is separate. It is built on prep/ll5d-fill-20261115 with
  director-helper-3's per-cell keys.

## Meaning reads (codex-school, gpt-6.1-sol, high effort, read-only)

- **Read 1: FAIL.** It found two problems, both fixed:
  - S10 dropped σ_d's coefficient;
  - "at most 0.021" was a rounded-down maximum. It is now "below 0.022", rounded up and asserted.
- **Read 2: FAIL**, on a stale page image only.
- **Read 3: PASS**, on the current render.

Each read's inputs are its `-prompt.txt` file, `meaning-read-records.txt`, `diff-as-read.txt` and
`new-values-as-read.txt`.

## Terms aligned with the paper (2026-11-16)

Table S13's caption uses the paper's §3.1 names for the three learners: "the reconstruction-level (step-1) classifier,
the truth-level (step-2) classifier and the regressor". Its mask is now "a column mask on the inputs of all three",
which matches director-helper-3's §5.3 alternative. `meaning-read-4.txt` checks this change against
`meaning-read-4-records.txt`: PASS.

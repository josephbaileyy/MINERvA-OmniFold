# The GENCMP amendment E paper round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent, read-only. It was given:
- the diff `a4cd6ffcf..3572ebb56`;
- the work order, ruling A and the authorities: FD-GENCMP-AMENDMENT-E-REPORT.md, its declaration (§4, §8, §12), the
  rerun1 readouts and `values_diff.tsv`, and #656's diff (`dfa137370..750466a70`).

It was not given the writer's conclusions. It re-derived the values, the gs- keys and the figure digests with its own
scripts, and mutation-tested the new assertions.

**The two directions:**
- truth: each touched sentence, caption, value and figure against its source;
- loss: no true fact dropped beyond the order, and no sentence elsewhere left false by the new numbers.

**The result:** no High finding, and nothing false in the diff.
- 252 changed keys, equal to `values_diff.tsv` without its 64 gs- rows.
- The 110 gs- keys equal #656's printed values. The reviewer also recomputed their 30 χ² from `b55366b3`/`75a9ddee`
  directly.
- The installed figures equal the E-1 sources and their sidecar digests.
- The new ratio figure plots the same numbers as #656's GENCMP redraw (max relative difference 0). Only the legend
  text differs.
- The sensitivity, bootstrap, sensitivity-caption and diag-caption text is byte-identical to before #656
  (`dfa137370`). The modes caption differs only by the added sentence.
- Every prose summary still holds against the table values it summarizes:
  - flux falls 23.2–38.3 %;
  - detector and lateral at most 17.8 %;
  - joint minimum 41.91;
  - edges at most 3.79 %;
  - median offset at most 0.38 %.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | the paper's ratio legend now prints E-A1's qualifiers, "NuWro 21.09: CH; hydrogen: supplement FLAGGED" and "GiBUU 2019: CH; hydrogen: closure B3 failed; …". The paper never explains the NuWro supplement flag (only the note does, `sec_joint.tex:327`), and "B3" is not defined in the paper. The GiBUU table note gives the closure failure in words | TO THE DIRECTOR AND JOSEPH: the declaration's §8 makes the legends carry these qualifiers, and the order allows no ratio-caption sentence beyond what #656 has. No word is changed here |
| 2 | Low | the removed scoping sentence was the paper's only pointer to the note's `sec:fived16-gen-target`. The generator-definition GiBUU numbers at `paper_body.tex:233` now have no note pointer | REPORTED: the removal is the order's. A pointer would be a new clause, so it is for the director |
| 3 | Low | `check_dead_containment.py`'s 6.86 exemption cited the superseded `fd/with-cpl/figures/fd_g_fig_modes.json` and "distance +4.85σ". The printed figure now reads "σ = 6.86%, distance +4.99σ" | FIXED in `e6e1b65ed`: the exemption and `test_build_all.py`'s fixture cite E-1's with-arm sidecar (σ 0.0685528). The containment tests (15) and `check_dead_containment.py` pass |
| 4 | Low | nothing checked that diag, fup and sens2 were computed from the pinned g readout. Swapping any of them for the old Stage G file was silent (predates the round) | FIXED in `e6e1b65ed`: `values()` requires each downstream readout's `inputs_sha256` to name the readouts its arm pins (g, diag, fup), with a self-test plant. All three swaps are now refused, each by this guard |
| — | note | a local variable `g0` in `values()` was unrelated to the new `"g0"` pin | renamed `p0` |

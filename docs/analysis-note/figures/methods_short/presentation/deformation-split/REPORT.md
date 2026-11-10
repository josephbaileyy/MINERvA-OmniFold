# Split deformation figures

Parent: 8320315bd. One producer generates separate paper and Supplement assets from
the same committed inputs. No manuscript, caption, pointer or shared style file changes. The estimator registry
citation digest is refreshed for the producer docstring's “Paper figure” wording;
its alias, estimator identity and citation location remain unchanged.
The figures lane owns the assets; director-helper-3 writes the two captions and
section 5.1 pointers, integrates them, and runs the final manuscript checks.

## Outputs and printed sizes

| Asset | Estimator/study | Printed width | Height |
|---|---|---:|---:|
| methods_short/m3_fig2_deformation.pdf and .png | Reported estimator; prior panel (b) | 508pt | 2.8in |
| methods_short/m3_fig2_deformation_lowcap.pdf and .png | Lower-capacity variant; prior panel (a) | 468pt | 2.8in |

Each is a single panel with no panel letter or cross-panel title reference. Both
retain the same residual sign, percent unit, 42-cell EW grid, limits, ticks and marker
styles. Both have a y label and one single-line x label. Legends stay inside the
empty upper-left region; all text fits inside the canvas and no data marker lies
under a legend. The plots and their print proofs were visually inspected.

The paper asset contains only the three reported-estimator curves: NuWro E_avail,
GENIE MEC (E_avail,W), and NuWro (pT,p_parallel,E_avail), 20 pseudo-experiments each.
The Supplement asset contains only the GiBUU/GENIE E_avail study, 60 experiments,
with its gray injected-change step. These are the existing 42 EW diagnostics,
not a rendering of the sixteen reported cells.

## Estimator identity and input provenance

The assessment receipt is pinned as before and identifies candidate R; the producer
now asserts that identity before plotting. nd-unfolding/s5e_candidate.py:CANDIDATES
sets R's refinement to 400 trees and 31 leaves. The committed candidate definition
in state/s5e/contract-amendment-3-candidate-R-and-assessment.json confirms its five
iterations and unchanged other settings; estimator_stability_probe.py:12 explicitly
identifies R as configuration (e). The receipt's W1/W2/W3 entries each have n=20.

The lower-capacity study is intentionally confined to the Supplement asset. Its
s5n development receipt controls.C2.refinement_params has 100 trees and 8 leaves,
and grid.C4_eavail_shape has 60 experiments. Its injection is unchanged from the
truth-check record. The numerical input records and frozen array reference retain
their complete SHA256 pins, repeated in checks.json; all are committed at the parent.
No paper source or generated values file is pinned as an input.

## Exact numerical comparison

Both emitted arrays.json and numbers.json files are byte-identical to the parent;
they remain the complete producer record for both studies. The existing frozen-array
assertion is retained. In addition, the parent and changed producers were run with
save-time inspection of their actual Matplotlib artists. The new paper axis equals
the parent's lower axis exactly, and the new Supplement axis equals its upper axis:
means, every error-bar segment, x positions/offsets, injected step values/edges,
limits, ticks, colors, markers and marker sizes. The resulting plot-content hashes
and axis/overlap checks are in artist-checks.json. This also checks that neither
study was accidentally saved to the other's filename.

## Printed fonts and validation

The unchanged figtext.py (SHA256 970246b691e27a70d3df73e4a9dac1d66de04b73525a97d665b75bfb9397d214)
was run on a TeX proof containing the parent figure at 508pt and both new assets at
their specified widths, and on the built paper. Raw output is in font-sizes.txt and
paper-font-sizes.txt.

| Figure at print width | Raw min | Median | Max |
|---|---:|---:|---:|
| Parent combined, 508pt | 3.0pt | 8.3pt | 9.3pt |
| Paper single panel, 508pt | 3.0pt | 8.3pt | 9.3pt |
| Supplement single panel, 468pt | 3.0pt | 8.3pt | 9.3pt |

The raw minimum is transformed geometry of a rotated glyph, as before; authored
ticks, legends and titles remain 8.3pt, and axis labels 9.3pt. The paper's actual
inclusion also measures median 8.3pt against a 9.0pt caption. No font was reduced.

The producer's existing numerical assertions and the additional artist comparison
pass. Estimator-registry citation checks and the results-index freshness check pass
after refreshing the docstring citation digest. make_values_fived16.py --check passes 3843 values, both source-figure checks
and ten listed-truth sentences. Python compilation and the TeX print proof pass.
The paper builds with latexmk and has no overfull box, oversized float or undefined
reference. Its external-note aux is an untracked build aid copied from the already
built note in the retained Supplement worktree. No new scientific computation is
performed. Captions and text remain for the integrator to update at the split;
this build verifies the asset inclusion and typography, not the pre-split caption.
Final integration checks and standalone-note synchronization remain with the integrator.

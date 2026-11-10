# Caption-first integration repair

Parent: d53af941a. This branch is the caption-only delivery for integration before
the paper's paragraph restructuring. It supersedes 3045fcbb5/7815eaa73 for caption
integration. It contains no figure producer, PDF, PNG, table or Supplement change.
The previous two-panel producer delivery is not a dependency of this branch.

## Scope

Items 1–4 and 6–10 of the caption repair are applied. Item 5 retains only its
changed-truth lead. M010, M011 and the panel (a)-specific estimator/configuration
wording are deferred to the paper integrator, who will move Figure 3(a) into the
Supplement. Apart from adding “at the changed truth”, Figure 3's caption is identical
to d53af941a. Its panel-specific caption is not rewritten in this commit.

The remaining repairs define Figure 1's band and ratios, Figure 2's difference,
Figure 4's z, twelve truths/order, leave-own-generator-out covariance, p-only q3 flag
and per-cell-only outlines, and Figure 5's requirements fixed before the test.
The total-only covariance reading is explicitly absent from Figure 4 and points
to the table. The complete Figure 5 population is defined with “are”. Figure 6
names the NuWro-shape comparator truth and keeps cells/not-repeated-experiments
in its caption. Its measured-bias and no-bias-bound qualifications stay in section 7.
The four moved-clause blocks are folded into their citing paragraphs.

pairs.json contains old/new/location fields for every applied item and each of the
ten remaining meaning clauses. It separately lists the three deferred panel (a)
requests. The original clauses trace to the committed captions at d1d60e74f.
Overlapping requests reuse one final clause rather than insert it again.

## Verification

checks.json records identical fvval/fvcase occurrence multisets, retained reference
targets, byte-identical table blocks and protected stability paragraph, and no new
numeric literal. The Figure 3 caption exception is checked against d53af941a directly.
Every applied meaning clause occurs once at its recorded location. Data, producers
and figure assets are unchanged from the parent.

| Figure | Before | After |
|---|---:|---:|
| 1 | 52 | 57 |
| 2 | 35 | 37 |
| 3 | 64 | 68 |
| 4 | 51 | 105 |
| 5 | 65 | 68 |
| 6 | 65 | 76 |

Counts use texcount -sum -brief on caption fragments. Figure 4 exceeds the earlier
approximate length target because the requested self-contained qualifications return.

make_values_fived16.py --check passes 3811 values, both source-figure checks and ten
listed-truth sentences. The ordinary paper builds successfully; its log has no
overfull box, undefined reference or oversized float. The existing note auxiliary
file and bibliography are untracked build aids copied from the earlier built tree.
The changed caption pages were rendered and checked for overlap and clipping.
Final integration checks, the blind rater copy and standalone-note synchronization
remain with the paper integrator.

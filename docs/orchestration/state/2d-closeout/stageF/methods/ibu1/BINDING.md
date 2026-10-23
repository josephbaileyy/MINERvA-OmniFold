# Binding: IBU-1 (2026-10-22)

**By** the paper-tighten lane, as director, under [`../IBU1-SPEC.md`](../IBU1-SPEC.md) and the lane brief
[`../../lanes/VALIDATION-LANE-BRIEF.md`](../../lanes/VALIDATION-LANE-BRIEF.md).

**Bound:** [`DECLARATION.md`](DECLARATION.md) as merged through PR #255 (the validation lane's `25095af1`, with a
director merge of main), file sha256 `39959a4dd3e2842ec00702627d98177fecff945a6f342bae0d7e406550732366`, with the code under `nd-unfolding/ibu1/` at that commit. It is bound
as written: the amendments IA-1 to IA-14, the readouts, the reading rule and the compute plan. A change after this
binding needs a new declaration and binding, and no change may follow a result.

## Rulings

- **The six resolutions and the director's three additions** (IA-9 response provenance, IA-10 small-n, IA-11 the K
  scan and the data comparison) are bound as declared.
- **IA-10 is explicitly bound, as amended.**
  - **Why the count cannot decide below 400.** With Clopper–Pearson at 0.05/459, a functional covered in every
    experiment still has a lower bound of 0.859 at n = 60 and 0.634 at n = 20, below the gates. So below n = 400 the
    below-gate count cannot resolve the factor-of-2 boundary.
  - **Below 400:** it is reported with its interval, as description. The residual decides, through the paired
    seed-bootstrap interval on the median ratio.
  - **At the rate change (n = 400):** both metrics decide.
  - **In every case,** no reading rests on a quantity whose interval spans the boundary.
- **IA-14,** the oracle floor, is reported with no rule.
- **Compute:**
  - job A on debug QOS (30 min), then B1 and B2 on regular QOS, each limited to 1.25× job A's projection and at most
    1:30;
  - worst case 3.5 CPU node-h, within IBU1-SPEC's 10;
  - outputs on `$PSCRATCH`;
  - every job ledgered.
- **Before the REPORT's PR:** an independent two-direction review.
